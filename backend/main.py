"""
Spelling & Drawing App - FastAPI Backend
Phase 1: MVP - Core Canvas & Basic Spelling
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
from database import (
    init_db, get_word_for_practice, save_practice, get_all_words, get_word_by_id,
    update_word_on_success, get_words_for_today, add_word, update_word, delete_word,
    get_all_words_admin, get_practice_stats, get_word_accuracy, get_practice_trend,
    get_recent_drawings, reset_db_to_initial
)
from data_management import (
    cleanup_old_drawings, get_storage_stats, optimize_database, create_backup
)

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

# Request/Response models
class WordResponse(BaseModel):
    id: int
    word: str
    category: str
    successful_days: int

class PracticeRequest(BaseModel):
    word_id: int
    spelled_word: str
    is_correct: bool

class PracticeResponse(BaseModel):
    success: bool
    message: str
    drawing_filename: str

# Routes
@app.get("/api/health")
async def health_check():
    """Check if API is running"""
    return {"status": "ok"}

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

@app.get("/api/next-word")
async def next_word():
    """
    Phase 4: Get next word to practice
    Returns only words where next_review <= today
    Includes successful_days to determine mode (Learning vs Recall)
    """
    word = get_word_for_practice()
    if word:
        return {
            "id": word[0],
            "word": word[1],
            "category": word[2],
            "successful_days": word[3]
        }
    return {"error": "No words available"}, 404

@app.post("/api/practice")
async def submit_practice(
    word_id: int = Form(...),
    spelled_word: str = Form(...),
    drawing: UploadFile = File(...),
    is_correct: str = Form(...)
):
    """Submit practice: save drawing + spelling"""
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
            
            # Phase 4: Update word progress if correct
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
