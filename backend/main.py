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
    update_word_on_success, get_words_for_today
)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Serve frontend files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
