"""
Tests for Issue #16: Session mastery threshold configuration
Tests that words require N correct answers before being mastered in a session
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from session import WordSession
from database import (
    init_db, create_user, create_child, add_word, get_db,
    get_user_mastery_threshold, update_user_mastery_threshold
)

DB_PATH = "../data/test_mastery.db"

def setup():
    """Setup test environment with fresh database"""
    import database
    database.DB_PATH = DB_PATH
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    init_db()

def cleanup():
    """Clean up test database"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_default_mastery_threshold():
    """Verify default mastery threshold is 2"""
    setup()
    
    user_id = create_user("test@example.com", "password")
    threshold = get_user_mastery_threshold(user_id)
    
    assert threshold == 2, f"Expected default threshold 2, got {threshold}"
    print("✓ Default mastery threshold is 2")
    
    cleanup()

def test_update_mastery_threshold():
    """Verify can update mastery threshold"""
    setup()
    
    user_id = create_user("test@example.com", "password")
    
    # Update to 3
    success = update_user_mastery_threshold(user_id, 3)
    assert success, "Failed to update threshold"
    
    threshold = get_user_mastery_threshold(user_id)
    assert threshold == 3, f"Expected threshold 3, got {threshold}"
    print("✓ Can update mastery threshold to 3")
    
    # Update to 1
    success = update_user_mastery_threshold(user_id, 1)
    assert success, "Failed to update threshold"
    
    threshold = get_user_mastery_threshold(user_id)
    assert threshold == 1, f"Expected threshold 1, got {threshold}"
    print("✓ Can update mastery threshold to 1")
    
    cleanup()

def test_session_mastery_threshold_2():
    """Verify word needs 2 correct answers with threshold=2"""
    setup()
    
    # Create user and child
    user_id = create_user("test@example.com", "password")
    child_id = create_child(user_id, "TestChild", 8)
    
    # Add word
    word_id = add_word("apple", "fruits", user_id=user_id)
    
    # Create session with default threshold (2)
    session = WordSession(child_id=child_id, mastery_threshold=2)
    
    # Initial state
    assert word_id in session.available_words, "Word not in initial session queue"
    print("✓ Word starts in session queue")
    
    # First correct answer - should still be in queue
    session.mark_word_mastered(word_id)
    assert word_id in session.available_words, "Word removed from queue after 1 correct"
    assert word_id in session.word_correct_count, "Word not tracked in correct count"
    assert session.word_correct_count[word_id] == 1, "Correct count not incremented"
    print("✓ After 1 correct: word still in queue")
    
    # Second correct answer - should be removed from queue
    session.mark_word_mastered(word_id)
    assert word_id not in session.available_words, "Word still in queue after 2 correct"
    assert word_id in session.mastered_words, "Word not marked as mastered"
    assert session.word_correct_count[word_id] == 2, "Correct count not correct"
    print("✓ After 2 correct: word removed from queue and mastered")
    
    cleanup()

def test_session_mastery_threshold_1():
    """Verify word needs only 1 correct answer with threshold=1"""
    setup()
    
    # Create user and child
    user_id = create_user("test@example.com", "password")
    child_id = create_child(user_id, "TestChild", 8)
    
    # Add word
    word_id = add_word("banana", "fruits", user_id=user_id)
    
    # Create session with threshold=1
    session = WordSession(child_id=child_id, mastery_threshold=1)
    
    # Initial state
    assert word_id in session.available_words, "Word not in initial session queue"
    print("✓ Word starts in session queue")
    
    # First correct answer - should be removed with threshold=1
    session.mark_word_mastered(word_id)
    assert word_id not in session.available_words, "Word still in queue after 1 correct"
    assert word_id in session.mastered_words, "Word not marked as mastered"
    print("✓ With threshold=1: word mastered after 1 correct answer")
    
    cleanup()

def test_session_mastery_threshold_3():
    """Verify word needs 3 correct answers with threshold=3"""
    setup()
    
    # Create user and child
    user_id = create_user("test@example.com", "password")
    child_id = create_child(user_id, "TestChild", 8)
    
    # Add word
    word_id = add_word("cherry", "fruits", user_id=user_id)
    
    # Create session with threshold=3
    session = WordSession(child_id=child_id, mastery_threshold=3)
    
    # First correct - in queue
    session.mark_word_mastered(word_id)
    assert word_id in session.available_words, "Word removed after 1 correct"
    assert session.word_correct_count[word_id] == 1
    
    # Second correct - in queue
    session.mark_word_mastered(word_id)
    assert word_id in session.available_words, "Word removed after 2 correct"
    assert session.word_correct_count[word_id] == 2
    
    # Third correct - removed from queue
    session.mark_word_mastered(word_id)
    assert word_id not in session.available_words, "Word still in queue after 3 correct"
    assert word_id in session.mastered_words, "Word not marked as mastered"
    assert session.word_correct_count[word_id] == 3
    print("✓ With threshold=3: word mastered after 3 correct answers")
    
    cleanup()

if __name__ == "__main__":
    try:
        test_default_mastery_threshold()
        test_update_mastery_threshold()
        test_session_mastery_threshold_2()
        test_session_mastery_threshold_1()
        test_session_mastery_threshold_3()
        print("\n✓ All mastery threshold tests passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
