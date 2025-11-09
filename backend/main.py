"""
Spelling & Drawing App - FastAPI Backend
Phase 1: MVP - Core Canvas & Basic Spelling
Phase 12: Multi-user and multi-child support
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
from typing import Optional
from database import (
    init_db, get_word_for_practice, save_practice, get_all_words, get_word_by_id,
    update_word_on_success, get_words_for_today, add_word, update_word, delete_word,
    get_all_words_admin, get_practice_stats, get_word_accuracy, get_practice_trend,
    get_recent_drawings, reset_db_to_initial, create_user, get_user_by_email,
    verify_password, create_child, get_user_children, get_child_by_id, update_child,
    delete_child, get_words_for_child, update_word_on_success_for_child,
    get_user_by_id
)
from data_management import (
    cleanup_old_drawings, get_storage_stats, optimize_database, create_backup
)
from session import WordSession
from auth import create_access_token, verify_token, get_user_id_from_token
from models import (
    UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse,
    ChildCreateRequest, ChildUpdateRequest, ChildResponse, AddWordRequest, PracticeRequest
)
from migrate import migrate_to_latest

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8002",
        "https://spelling-drawing-app.fly.dev",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()
# Run migrations
migrate_to_latest()

# Global session state (per client session)
current_session = None

# Determine if running in Docker/production
import sys
IS_DOCKER = os.path.exists('/.dockerenv') or os.getenv('FLY_APP_NAME')
BASE_DIR = '/app' if IS_DOCKER else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Serve frontend files
frontend_dir = os.path.join(BASE_DIR, 'frontend')

# Serve drawings
drawings_dir = os.path.join(BASE_DIR, 'data', 'drawings')
os.makedirs(drawings_dir, exist_ok=True)
app.mount("/drawings", StaticFiles(directory=drawings_dir), name="drawings")

# Serve root and frontend pages
from fastapi.responses import FileResponse

# Serve static files (CSS, JS, images, etc.) - must be mounted BEFORE specific routes
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Define specific routes for HTML pages  
@app.get("/")
async def root():
    """Serve main app page"""
    return FileResponse(os.path.join(frontend_dir, "index.html"), media_type="text/html")

@app.get("/admin")
async def admin():
    """Serve admin page"""
    return FileResponse(os.path.join(frontend_dir, "admin.html"), media_type="text/html")

@app.get("/dashboard")
async def dashboard():
    """Serve dashboard page"""
    return FileResponse(os.path.join(frontend_dir, "dashboard.html"), media_type="text/html")

@app.get("/login")
async def login_page():
    """Serve login page"""
    return FileResponse(os.path.join(frontend_dir, "login.html"), media_type="text/html")

@app.get("/register")
async def register_page():
    """Serve register page"""
    return FileResponse(os.path.join(frontend_dir, "register.html"), media_type="text/html")

@app.get("/select-child")
async def select_child_page():
    """Serve child selector page"""
    return FileResponse(os.path.join(frontend_dir, "select-child.html"), media_type="text/html")

@app.get("/user-profile")
async def user_profile_page():
    """Serve user profile page"""
    return FileResponse(os.path.join(frontend_dir, "user-profile.html"), media_type="text/html")

# Request/Response models
class WordResponse(BaseModel):
    id: int
    word: str
    category: str
    successful_days: int

class PracticeResponse(BaseModel):
    success: bool
    message: str
    drawing_filename: str

# ===== PHASE 12: Auth Dependencies =====

async def get_current_user(authorization: Optional[str] = Header(None)) -> int:
    """
    Dependency to get current user from JWT token
    Raises HTTPException 401 if token invalid or missing
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Extract token from "Bearer {token}"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_id

async def verify_child_ownership(child_id: int, user_id: int) -> dict:
    """
    Verify that child belongs to user
    Returns child data if valid
    """
    child = get_child_by_id(child_id)
    if not child or child['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied: child not found or doesn't belong to you")
    return child

# Routes
@app.get("/api/health")
async def health_check():
    """Check if API is running"""
    return {"status": "ok"}

# ===== PHASE 12: Authentication Endpoints =====

@app.post("/api/auth/register", response_model=UserResponse)
async def register(req: UserRegisterRequest):
    """Register new parent account"""
    try:
        if len(req.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        user_id = create_user(req.email, req.password)
        user = get_user_by_id(user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: UserLoginRequest):
    """Login and get JWT token"""
    user = get_user_by_email(req.email)
    
    if not user or not verify_password(req.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token({"sub": str(user['id'])})
    return TokenResponse(access_token=access_token)

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(user_id: int = Depends(get_current_user)):
    """Get current logged-in user info"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ===== PHASE 12: Child Management Endpoints =====

@app.post("/api/children", response_model=ChildResponse, status_code=201)
async def create_child_profile(
    req: ChildCreateRequest,
    user_id: int = Depends(get_current_user)
):
    """Create new child profile for user"""
    try:
        child_id = create_child(user_id, req.name, req.age)
        child = get_child_by_id(child_id)
        return child
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/children")
async def list_children(user_id: int = Depends(get_current_user)):
    """Get all children for logged-in user"""
    children = get_user_children(user_id)
    return children

@app.put("/api/children/{child_id}", response_model=ChildResponse)
async def update_child_profile(
    child_id: int,
    req: ChildUpdateRequest,
    user_id: int = Depends(get_current_user)
):
    """Update child profile"""
    # Verify ownership
    await verify_child_ownership(child_id, user_id)
    
    try:
        update_child(child_id, req.name, req.age)
        child = get_child_by_id(child_id)
        return child
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/children/{child_id}")
async def delete_child_profile(
    child_id: int,
    user_id: int = Depends(get_current_user)
):
    """Delete child and all their practices"""
    # Verify ownership
    await verify_child_ownership(child_id, user_id)
    
    try:
        success = delete_child(child_id)
        if success:
            return {"success": True, "message": "Child deleted successfully"}
        raise HTTPException(status_code=404, detail="Child not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/words")
async def get_words():
    """Get all words"""
    words = get_all_words()
    return {"words": words}

@app.get("/api/words-for-today")
async def get_todays_words():
    """
    Phase 4: Get all words ready for practice today
    Returns words where next_review <= today
    Useful for dashboard/tracking what needs to be practiced
    """
    words = get_words_for_today()
    return {"words": words}

@app.post("/api/session/start")
async def start_session(num_words: int = None, user_id: int = Depends(get_current_user)):
    """
    Phase 12: Start a new practice session with optional word limit
    Requires authentication and child_id in localStorage on frontend
    
    Args:
        num_words: Limit session to N words (None = all available)
    
    Returns:
        Session info and first word
    """
    global current_session
    
    # Create new session
    current_session = WordSession(num_words=num_words)
    
    # Get first word
    word_id = current_session.get_next_word_id()
    
    if not word_id:
        raise HTTPException(status_code=404, detail="No words available for today")
    
    word = get_word_by_id(word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Get word record for successful_days
    from database import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT successful_days FROM words WHERE id = ?", (word_id,))
    word_data = cursor.fetchone()
    conn.close()
    
    successful_days = word_data[0] if word_data else 0
    
    stats = current_session.get_session_stats()
    
    return {
        "id": word_id,
        "word": word[0],
        "category": word[1],
        "successful_days": successful_days,
        "session": stats
    }

@app.get("/api/next-word")
async def next_word(user_id: int = Depends(get_current_user)):
    """
    Phase 12: Get next word to practice (requires authentication)
    Uses session queue if active, otherwise falls back to default behavior
    Returns only words where next_review <= today
    Includes successful_days to determine mode (Learning vs Recall)
    """
    global current_session
    
    # If no session active, get next available word
    if not current_session or not current_session.session_started:
        word = get_word_for_practice()
        if word:
            return {
                "id": word[0],
                "word": word[1],
                "category": word[2],
                "successful_days": word[3],
                "session": None
            }
        raise HTTPException(status_code=404, detail="No words available")
    
    # Get next word from session queue
    word_id = current_session.get_next_word_id()
    
    if not word_id:
        raise HTTPException(status_code=404, detail="Session complete - all words mastered")
    
    word = get_word_by_id(word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Get word record for successful_days
    from database import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT successful_days FROM words WHERE id = ?", (word_id,))
    word_data = cursor.fetchone()
    conn.close()
    
    successful_days = word_data[0] if word_data else 0
    
    stats = current_session.get_session_stats()
    
    return {
        "id": word_id,
        "word": word[0],
        "category": word[1],
        "successful_days": successful_days,
        "session": stats
    }

@app.post("/api/practice")
async def submit_practice(
    word_id: int = Form(...),
    spelled_word: str = Form(...),
    drawing: UploadFile = File(...),
    is_correct: str = Form(...),
    user_id: int = Depends(get_current_user)
):
    """
    Phase 12: Submit practice - save drawing + spelling (requires authentication)
    """
    global current_session
    
    try:
        # Save drawing file (use absolute path)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        drawings_dir = os.path.join(base_dir, "data", "drawings")
        os.makedirs(drawings_dir, exist_ok=True)
        
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(drawings_dir, filename)
        
        contents = await drawing.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        
        # Save practice record
        word_data = get_word_by_id(word_id)
        if word_data:
            # Convert string 'true'/'false' to boolean
            is_correct_bool = is_correct.lower() == 'true'
            save_practice(word_id, spelled_word, is_correct_bool, filename)
            
            # Update session queue if active
            if current_session and current_session.session_started:
                if is_correct_bool:
                    current_session.mark_word_mastered(word_id)
                else:
                    current_session.mark_word_incorrect(word_id)
            
            # Update word progress if correct
            if is_correct_bool:
                update_word_on_success(word_id)
        else:
            raise Exception("Word not found")
        
        return PracticeResponse(
            success=True,
            message="Practice saved",
            drawing_filename=filename
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/words")
async def admin_add_word(
    word: str = Form(...),
    category: str = Form(...),
    reference_image: UploadFile = File(None)
):
    """Phase 5: Admin endpoint to add new word"""
    try:
        reference_filename = None
        
        if reference_image and reference_image.filename:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            references_dir = os.path.join(base_dir, "data", "references")
            os.makedirs(references_dir, exist_ok=True)
            
            reference_filename = f"{uuid.uuid4()}_{reference_image.filename}"
            filepath = os.path.join(references_dir, reference_filename)
            
            contents = await reference_image.read()
            with open(filepath, "wb") as f:
                f.write(contents)
        
        word_id = add_word(word, category, reference_filename)
        
        return {"success": True, "word_id": word_id, "message": f"Word '{word}' added successfully"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/words/{word_id}")
async def admin_update_word(
    word_id: int,
    word: str = Form(None),
    category: str = Form(None),
    reference_image: UploadFile = File(None)
):
    """Phase 5: Admin endpoint to update word"""
    try:
        reference_filename = None
        
        if reference_image and reference_image.filename:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            references_dir = os.path.join(base_dir, "data", "references")
            os.makedirs(references_dir, exist_ok=True)
            
            reference_filename = f"{uuid.uuid4()}_{reference_image.filename}"
            filepath = os.path.join(references_dir, reference_filename)
            
            contents = await reference_image.read()
            with open(filepath, "wb") as f:
                f.write(contents)
        
        success = update_word(word_id, word, category, reference_filename)
        
        if success:
            return {"success": True, "message": "Word updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Word not found")
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/words/{word_id}")
async def admin_delete_word(word_id: int):
    """Phase 5: Admin endpoint to delete word"""
    try:
        success = delete_word(word_id)
        
        if success:
            return {"success": True, "message": "Word deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Word not found")
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/words")
async def admin_get_words():
    """Phase 5: Admin endpoint to get all words with details"""
    try:
        words = get_all_words_admin()
        return {"words": words}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats")
async def dashboard_stats():
    """Phase 6: Get overall practice statistics"""
    try:
        stats = get_practice_stats()
        return stats
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/word-accuracy")
async def dashboard_word_accuracy():
    """Phase 6: Get accuracy per word"""
    try:
        words = get_word_accuracy()
        return {"words": words}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/trend")
async def dashboard_trend(days: int = 7):
    """Phase 6: Get practice trend"""
    try:
        trend = get_practice_trend(days)
        return {"trend": trend}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/drawings")
async def dashboard_drawings(limit: int = 20):
    """Phase 6: Get recent drawings"""
    try:
        drawings = get_recent_drawings(limit)
        return {"drawings": drawings}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/storage-stats")
async def get_storage():
    """Phase 7: Get storage statistics"""
    try:
        stats = get_storage_stats()
        return stats
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/cleanup")
async def cleanup_data(keep_per_word: int = 10):
    """Phase 7: Cleanup old drawings"""
    try:
        deleted = cleanup_old_drawings(keep_per_word)
        return {"success": True, "deleted_count": deleted, "message": f"Deleted {deleted} old drawings"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/optimize")
async def optimize_db():
    """Phase 7: Optimize database"""
    try:
        success = optimize_database()
        if success:
            return {"success": True, "message": "Database optimized successfully"}
        else:
            raise HTTPException(status_code=500, detail="Optimization failed")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/backup")
async def backup_data():
    """Phase 7: Create database backup"""
    try:
        filename = create_backup()
        if filename:
            return {"success": True, "filename": filename, "message": f"Backup created: {filename}"}
        else:
            raise HTTPException(status_code=500, detail="Backup failed")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/reset-db")
async def reset_database():
    """Reset database to original state with only 3 initial words"""
    try:
        success = reset_db_to_initial()
        if success:
            return {"success": True, "message": "Database reset to initial state with 3 words"}
        else:
            raise HTTPException(status_code=500, detail="Reset failed")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
