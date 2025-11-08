"""
Phase 5: Tests for admin word management
"""

import pytest
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from database import (
    init_db, add_word, update_word, delete_word, 
    get_all_words_admin, get_word_by_id
)

DB_PATH = "../data/test_spelling.db"

@pytest.fixture(autouse=True)
def setup_test_db():
    """Setup test database before each test"""
    import database
    database.DB_PATH = DB_PATH
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    init_db()
    
    yield
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_add_word():
    """Test adding a new word"""
    word_id = add_word("ant", "insects")
    assert word_id is not None
    
    word = get_word_by_id(word_id)
    assert word is not None
    assert word[0] == "ant"
    assert word[1] == "insects"

def test_add_word_with_reference_image():
    """Test adding a word with reference image"""
    word_id = add_word("wasp", "insects", "wasp_ref.jpg")
    assert word_id is not None

def test_add_duplicate_word():
    """Test that adding duplicate word raises error"""
    add_word("dragonfly", "insects")
    
    with pytest.raises(ValueError, match="already exists"):
        add_word("dragonfly", "insects")

def test_update_word():
    """Test updating word details"""
    word_id = add_word("butter", "insects")
    
    success = update_word(word_id, word="ladybug", category="insects")
    assert success is True
    
    word = get_word_by_id(word_id)
    assert word[0] == "ladybug"

def test_update_word_category():
    """Test updating only category"""
    word_id = add_word("cat", "animals")
    
    success = update_word(word_id, category="baby animals")
    assert success is True
    
    word = get_word_by_id(word_id)
    assert word[1] == "baby animals"

def test_update_nonexistent_word():
    """Test updating word that doesn't exist"""
    success = update_word(9999, word="test")
    assert success is False

def test_delete_word():
    """Test deleting a word"""
    word_id = add_word("mosquito", "insects")
    
    success = delete_word(word_id)
    assert success is True
    
    word = get_word_by_id(word_id)
    assert word is None

def test_delete_nonexistent_word():
    """Test deleting word that doesn't exist"""
    success = delete_word(9999)
    assert success is False

def test_get_all_words_admin():
    """Test getting all words with admin details"""
    add_word("firefly", "insects")
    add_word("cricket", "insects")
    add_word("grasshopper", "insects")
    
    words = get_all_words_admin()
    assert len(words) >= 3
    
    assert 'id' in words[0]
    assert 'word' in words[0]
    assert 'category' in words[0]
    assert 'successful_days' in words[0]
    assert 'next_review' in words[0]

def test_new_word_initialized_with_today():
    """Test that new words have next_review set to today"""
    word_id = add_word("ant", "insects")
    
    words = get_all_words_admin()
    word = next(w for w in words if w['id'] == word_id)
    
    today = date.today().isoformat()
    assert word['next_review'] == today
    assert word['successful_days'] == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
