"""
Test Phase 14: Database-backed daily mastery tracking

Tests that:
1. correct_count_today increments on each correct answer
2. When correct_count_today >= mastery_threshold, word is mastered (next_review set to future)
3. When correct_count_today < mastery_threshold, word stays in queue (next_review = today)
4. Counter resets when next day starts (if same word practiced on different days)
5. Works across multiple workers (no global session state)
"""

import pytest
import sqlite3
import os
from datetime import date, timedelta
from database import (
    init_db, add_word, create_user, create_child, save_practice,
    update_word_on_correct_answer, get_db
)

# Use test database
os.environ['TEST_MODE'] = '1'
TEST_DB = '/tmp/test_db_daily_mastery.db'

@pytest.fixture
def test_db():
    """Create and teardown test database"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Monkey patch database path
    import database
    database.DB_PATH = TEST_DB
    
    init_db()
    yield
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_correct_count_today_increments(test_db):
    """Test that correct_count_today increments on each correct answer"""
    # Setup
    user_id = create_user("test@example.com", "password123")
    child_id = create_child(user_id, "TestChild")
    word_id = add_word("apple", "fruits", user_id=user_id)
    
    mastery_threshold = 2
    
    # First correct answer
    mastered = update_word_on_correct_answer(word_id, child_id, mastery_threshold)
    assert mastered is False, "Word should not be mastered yet (need 2, have 1)"
    
    # Check database state
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT correct_count_today, next_review FROM child_progress 
        WHERE child_id = ? AND word_id = ?
    """, (child_id, word_id))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    correct_count = row[0] if isinstance(row, (tuple, list)) else row['correct_count_today']
    next_review = row[1] if isinstance(row, (tuple, list)) else row['next_review']
    
    assert correct_count == 1, "correct_count_today should be 1"
    assert next_review == date.today().isoformat(), "Word should stay in queue for today"
    
    # Second correct answer
    mastered = update_word_on_correct_answer(word_id, child_id, mastery_threshold)
    assert mastered is True, "Word should be mastered after 2 correct answers"
    
    # Check database state
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT correct_count_today, next_review FROM child_progress 
        WHERE child_id = ? AND word_id = ?
    """, (child_id, word_id))
    row = cursor.fetchone()
    conn.close()
    
    correct_count = row[0] if isinstance(row, (tuple, list)) else row['correct_count_today']
    next_review = row[1] if isinstance(row, (tuple, list)) else row['next_review']
    
    assert correct_count == 2, "correct_count_today should be 2"
    expected_review = (date.today() + timedelta(days=3)).isoformat()
    assert next_review == expected_review, "Word should be scheduled for review in 3 days"

def test_counter_resets_on_new_day(test_db):
    """Test that correct_count_today resets when a new day starts"""
    # Setup
    user_id = create_user("test@example.com", "password123")
    child_id = create_child(user_id, "TestChild")
    word_id = add_word("apple", "fruits", user_id=user_id)
    
    mastery_threshold = 2
    
    # First correct answer on day 1
    mastered = update_word_on_correct_answer(word_id, child_id, mastery_threshold)
    assert mastered is False
    
    # Simulate a new day by manually setting last_practiced to yesterday
    conn = get_db()
    cursor = conn.cursor()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    cursor.execute("""
        UPDATE child_progress 
        SET last_practiced = ?
        WHERE child_id = ? AND word_id = ?
    """, (yesterday, child_id, word_id))
    conn.commit()
    conn.close()
    
    # First correct answer on day 2 (counter should reset to 1)
    mastered = update_word_on_correct_answer(word_id, child_id, mastery_threshold)
    assert mastered is False, "After reset, should need another correct answer"
    
    # Check database state
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT correct_count_today, last_practiced FROM child_progress 
        WHERE child_id = ? AND word_id = ?
    """, (child_id, word_id))
    row = cursor.fetchone()
    conn.close()
    
    correct_count = row[0] if isinstance(row, (tuple, list)) else row['correct_count_today']
    last_practiced = row[1] if isinstance(row, (tuple, list)) else row['last_practiced']
    
    assert correct_count == 1, "Counter should reset to 1 on new day"
    assert last_practiced == date.today().isoformat(), "last_practiced should be today"

def test_multiple_children_isolated(test_db):
    """Test that progress is isolated between children"""
    # Setup
    user_id = create_user("test@example.com", "password123")
    child1_id = create_child(user_id, "Child1")
    child2_id = create_child(user_id, "Child2")
    word_id = add_word("apple", "fruits", user_id=user_id)
    
    mastery_threshold = 2
    
    # Child 1 gets 1 correct answer
    mastered = update_word_on_correct_answer(word_id, child1_id, mastery_threshold)
    assert mastered is False
    
    # Child 2 should start fresh (0 correct answers)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT correct_count_today FROM child_progress 
        WHERE child_id = ? AND word_id = ?
    """, (child2_id, word_id))
    row = cursor.fetchone()
    conn.close()
    
    # Child 2 shouldn't have a record yet
    assert row is None, "Child 2 should have no progress record yet"
    
    # Child 2 gets first correct answer (separate from Child 1)
    mastered = update_word_on_correct_answer(word_id, child2_id, mastery_threshold)
    assert mastered is False
    
    # Verify both children have count=1
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT correct_count_today FROM child_progress 
        WHERE word_id = ? ORDER BY child_id
    """, (word_id,))
    rows = cursor.fetchall()
    conn.close()
    
    assert len(rows) == 2, "Both children should have progress records"
    count1 = rows[0][0] if isinstance(rows[0], (tuple, list)) else rows[0]['correct_count_today']
    count2 = rows[1][0] if isinstance(rows[1], (tuple, list)) else rows[1]['correct_count_today']
    
    assert count1 == 1 and count2 == 1, "Both children should have independent counts"

def test_works_without_session_state(test_db):
    """Test that mastery works without global session state"""
    # This test verifies the main improvement: no global state needed
    # We can call update_word_on_correct_answer independently multiple times
    
    user_id = create_user("test@example.com", "password123")
    child_id = create_child(user_id, "TestChild")
    word_id = add_word("apple", "fruits", user_id=user_id)
    
    mastery_threshold = 3
    
    # Simulate multiple independent calls (as would happen with different workers)
    for i in range(3):
        mastered = update_word_on_correct_answer(word_id, child_id, mastery_threshold)
        if i < 2:
            assert mastered is False, f"Should not be mastered on attempt {i+1}"
        else:
            assert mastered is True, f"Should be mastered on attempt {i+1}"
    
    # Word should now be in future review
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT next_review FROM child_progress 
        WHERE child_id = ? AND word_id = ?
    """, (child_id, word_id))
    row = cursor.fetchone()
    conn.close()
    
    next_review = row[0] if isinstance(row, (tuple, list)) else row['next_review']
    expected_review = (date.today() + timedelta(days=3)).isoformat()
    assert next_review == expected_review, "Word should be scheduled for 3 days from now"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
