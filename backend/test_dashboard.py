"""
Phase 6: Tests for parent dashboard
"""

import pytest
import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from database import (
    init_db, add_word, save_practice, 
    get_practice_stats, get_word_accuracy, get_practice_trend, get_recent_drawings
)

DB_PATH = "../data/test_dashboard.db"

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

def test_get_practice_stats_empty():
    """Test stats with no practice data"""
    stats = get_practice_stats()
    
    assert stats['words_today'] == 0
    assert stats['words_this_week'] == 0
    assert stats['overall_accuracy'] == 0.0
    assert stats['total_practices'] == 0

def test_get_practice_stats_with_data():
    """Test stats with practice data"""
    from database import create_user, create_child
    word_id = add_word("wasp", "insects")
    user_id = create_user("test@test.com", "password")
    child_id = create_child(user_id, "Test Child", 8)
    
    save_practice(word_id, child_id, "bee", True, "drawing1.png")
    save_practice(word_id, child_id, "bea", False, "drawing2.png")
    save_practice(word_id, child_id, "bee", True, "drawing3.png")
    
    stats = get_practice_stats()
    
    assert stats['total_practices'] == 3
    assert stats['overall_accuracy'] == pytest.approx(66.7, abs=0.1)
    assert stats['words_today'] >= 1
    assert stats['words_this_week'] >= 1

def test_get_word_accuracy():
    """Test word accuracy calculation"""
    from database import create_user, create_child
    word1_id = add_word("wasp", "insects")
    word2_id = add_word("moth", "insects")
    user_id = create_user("test@test.com", "password")
    child_id = create_child(user_id, "Test Child", 8)
    
    save_practice(word1_id, child_id, "bee", True, "d1.png")
    save_practice(word1_id, child_id, "bee", True, "d2.png")
    save_practice(word1_id, child_id, "bea", False, "d3.png")
    
    save_practice(word2_id, child_id, "ant", True, "d4.png")
    
    words = get_word_accuracy()
    
    assert len(words) == 2
    
    wasp_word = next(w for w in words if w['word'] == 'wasp')
    assert wasp_word['total_attempts'] == 3
    assert wasp_word['correct_attempts'] == 2
    assert wasp_word['accuracy'] == pytest.approx(66.7, abs=0.1)
    
    moth_word = next(w for w in words if w['word'] == 'moth')
    assert moth_word['total_attempts'] == 1
    assert moth_word['correct_attempts'] == 1
    assert moth_word['accuracy'] == 100.0

def test_get_word_accuracy_sorted():
    """Test that word accuracy is sorted by worst performing"""
    from database import create_user, create_child
    word1_id = add_word("flea", "insects")
    word2_id = add_word("tick", "insects")
    user_id = create_user("test@test.com", "password")
    child_id = create_child(user_id, "Test Child", 8)
    
    save_practice(word1_id, child_id, "flea", True, "d1.png")
    save_practice(word1_id, child_id, "flea", True, "d2.png")
    
    save_practice(word2_id, child_id, "tick", True, "d3.png")
    save_practice(word2_id, child_id, "teck", False, "d4.png")
    save_practice(word2_id, child_id, "tock", False, "d5.png")
    
    words = get_word_accuracy()
    
    assert words[0]['word'] == 'tick'
    assert words[0]['accuracy'] < words[1]['accuracy']

def test_get_practice_trend():
    """Test practice trend data"""
    from database import create_user, create_child
    word_id = add_word("gnat", "insects")
    user_id = create_user("test@test.com", "password")
    child_id = create_child(user_id, "Test Child", 8)
    
    save_practice(word_id, child_id, "bee", True, "d1.png")
    save_practice(word_id, child_id, "bea", False, "d2.png")
    save_practice(word_id, child_id, "bee", True, "d3.png")
    
    trend = get_practice_trend(7)
    
    assert len(trend) >= 1
    today_data = next((t for t in trend if t['date'] == date.today().isoformat()), None)
    
    if today_data:
        assert today_data['total'] == 3
        assert today_data['correct'] == 2

def test_get_recent_drawings():
    """Test getting recent drawings"""
    from database import create_user, create_child
    word1_id = add_word("midge", "insects")
    word2_id = add_word("louse", "insects")
    user_id = create_user("test@test.com", "password")
    child_id = create_child(user_id, "Test Child", 8)
    
    save_practice(word1_id, child_id, "midge", True, "drawing1.png")
    save_practice(word2_id, child_id, "louse", False, "drawing2.png")
    save_practice(word1_id, child_id, "midge", True, "drawing3.png")
    
    drawings = get_recent_drawings(10)
    
    assert len(drawings) == 3
    
    assert 'drawing3.png' in [d['filename'] for d in drawings]
    assert 'drawing2.png' in [d['filename'] for d in drawings]
    assert 'drawing1.png' in [d['filename'] for d in drawings]
    
    assert any(d['word'] == 'midge' and d['is_correct'] is True for d in drawings)
    assert any(d['word'] == 'louse' and d['is_correct'] is False for d in drawings)

def test_get_recent_drawings_limit():
    """Test drawings limit"""
    from database import create_user, create_child
    word_id = add_word("roach", "insects")
    user_id = create_user("test@test.com", "password")
    child_id = create_child(user_id, "Test Child", 8)
    
    for i in range(15):
        save_practice(word_id, child_id, "bee", True, f"drawing{i}.png")
    
    drawings = get_recent_drawings(10)
    
    assert len(drawings) == 10

def test_get_recent_drawings_no_data():
    """Test getting drawings with no data"""
    drawings = get_recent_drawings(10)
    
    assert len(drawings) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
