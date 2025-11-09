"""
Integration tests for session-based word cycling
Tests the full workflow: session start -> word cycling -> word mastery
"""

import sys
from session import WordSession
from database import init_db, get_words_for_today, reset_db_to_initial

def test_session_workflow():
    """Test complete session workflow"""
    init_db()
    reset_db_to_initial()
    
    print("Testing Session Workflow")
    print("=" * 50)
    
    # Step 1: Create session with 3 words
    session = WordSession(num_words=3)
    print(f"\n1. Session created")
    print(f"   - Total words: 3")
    print(f"   - Available words: {len(session.available_words)}")
    assert len(session.available_words) == 3
    
    # Step 2: Simulate practicing words
    words_practiced = []
    for attempt in range(10):
        word_id = session.get_next_word_id()
        words_practiced.append(word_id)
        
        # Simulate user practicing word
        is_correct = attempt % 2 == 0  # Every other attempt is correct
        
        if is_correct:
            session.mark_word_mastered(word_id)
            print(f"\n{attempt+1}. Word {word_id} correct ✓ (mastered)")
        else:
            session.mark_word_incorrect(word_id)
            print(f"\n{attempt+1}. Word {word_id} incorrect ✗")
        
        # Check no consecutive duplicates
        if len(words_practiced) >= 2:
            assert words_practiced[-1] != words_practiced[-2], \
                f"Consecutive duplicates at position {attempt}: {words_practiced[-2]}, {words_practiced[-1]}"
    
    # Step 3: Check session stats
    stats = session.get_session_stats()
    print(f"\nFinal Session Stats:")
    print(f"  - Total words: {stats['total_words']}")
    print(f"  - Mastered: {stats['mastered']}")
    print(f"  - Remaining: {stats['remaining']}")
    print(f"  - Queue size: {stats['queue_size']}")
    
    print(f"\nWords practiced sequence: {words_practiced}")
    print("\n✓ Session workflow test passed!")

def test_session_prevents_consecutive_duplicates():
    """Verify no consecutive duplicates across many attempts"""
    init_db()
    reset_db_to_initial()
    
    print("\n\nTesting Consecutive Duplicate Prevention")
    print("=" * 50)
    
    session = WordSession(num_words=5)
    last_word = None
    attempts = 50
    
    for i in range(attempts):
        word_id = session.get_next_word_id()
        
        if last_word is not None:
            assert word_id != last_word, \
                f"Consecutive duplicate at attempt {i}: {last_word}, {word_id}"
        
        last_word = word_id
        
        # Randomly mark as mastered or incorrect
        import random
        if random.random() > 0.3:
            session.mark_word_mastered(word_id)
    
    print(f"✓ Tested {attempts} attempts with no consecutive duplicates")

if __name__ == "__main__":
    test_session_workflow()
    test_session_prevents_consecutive_duplicates()
    print("\n" + "=" * 50)
    print("All integration tests passed!")
