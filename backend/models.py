"""
Pydantic models for Phase 12 API requests/responses
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ===== Authentication Models =====

class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str

class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response (no password)"""
    id: int
    email: str
    created_date: str

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"

# ===== Child Models =====

class ChildCreateRequest(BaseModel):
    """Create child request"""
    name: str
    age: Optional[int] = None

class ChildUpdateRequest(BaseModel):
    """Update child request"""
    name: Optional[str] = None
    age: Optional[int] = None

class ChildResponse(BaseModel):
    """Child response"""
    id: int
    user_id: int
    name: str
    age: Optional[int]
    created_date: str

# ===== Word Models =====

class WordResponse(BaseModel):
    """Word response"""
    id: int
    word: str
    category: str
    successful_days: int
    next_review: Optional[str] = None
    user_id: Optional[int] = None
    reference_image: Optional[str] = None

class AddWordRequest(BaseModel):
    """Add word request"""
    word: str
    category: str

# ===== Practice Models =====

class PracticeRequest(BaseModel):
    """Practice request"""
    word_id: int
    spelled_word: str
    is_correct: bool
    drawing_filename: Optional[str] = None

class PracticeResponse(BaseModel):
    """Practice response"""
    id: int
    word_id: int
    child_id: int
    spelled_word: str
    is_correct: bool
    drawing_filename: Optional[str]
    practiced_date: str
