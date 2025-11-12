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
    
    # Step 2: Simulate practicing words until all mastered
    words_practiced = []
    attempt = 0
    while session.available_words:
        word_id = session.get_next_word_id()
        if word_id is None:
            break
        words_practiced.append(word_id)
        
        # Simulate user practicing word - mark all as correct to complete session
        session.mark_word_mastered(word_id)
        print(f"\n{attempt+1}. Word {word_id} correct ✓ (mastered)")
        
        attempt += 1
        if attempt > 10:
            break
    
    # Step 3: Check session stats
    stats = session.get_session_stats()
    print(f"\nFinal Session Stats:")
    print(f"  - Total words: {stats['total_words']}")
    print(f"  - Mastered: {stats['mastered']}")
    print(f"  - Remaining: {stats['remaining']}")
    print(f"  - Queue size: {stats['queue_size']}")
    
    assert stats['mastered'] == 3, f"Expected 3 mastered words, got {stats['mastered']}"
    assert stats['queue_size'] == 0, f"Expected empty queue, got {stats['queue_size']}"
    
    print(f"\nWords practiced sequence: {words_practiced}")
    print("\n✓ Session workflow test passed!")

def test_session_prevents_consecutive_duplicates():
    """Verify no consecutive duplicates when words remain in queue"""
    init_db()
    reset_db_to_initial()
    
    print("\n\nTesting Consecutive Duplicate Prevention")
    print("=" * 50)
    
    session = WordSession(num_words=5)
    last_word = None
    attempts = 0
    
    while session.available_words and attempts < 50:
        word_id = session.get_next_word_id()
        if word_id is None:
            break
        
        if last_word is not None and len(session.available_words) > 1:
            assert word_id != last_word, \
                f"Consecutive duplicate at attempt {attempts}: {last_word}, {word_id}"
        
        last_word = word_id
        
        import random
        if random.random() > 0.5:
            session.mark_word_mastered(word_id)
        else:
            session.mark_word_incorrect(word_id)
        
        attempts += 1
    
    print(f"✓ Tested {attempts} attempts with proper duplicate prevention")

if __name__ == "__main__":
    test_session_workflow()
    test_session_prevents_consecutive_duplicates()
    print("\n" + "=" * 50)
    print("All integration tests passed!")
