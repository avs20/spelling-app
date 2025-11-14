"""
Test session queue logic
"""

import sys
from session import WordSession
from database import init_db, get_words_for_today

def test_word_session():
    """Test basic session functionality"""
    init_db()
    
    # Create session with 3 words
    session = WordSession(num_words=3)
    
    print(f"Session created with {session.num_words} words")
    print(f"Available words: {session.available_words}")
    
    # Get first word
    word1 = session.get_next_word_id()
    print(f"\nFirst word: {word1}")
    assert word1 is not None
    
    # Try to get same word again (should prevent)
    word2 = session.get_next_word_id()
    print(f"Second word (should be different): {word2}")
    
    if len(session.available_words) > 1:
        # If multiple words, second shouldn't be same as first
        assert word1 != word2, f"Got consecutive duplicates: {word1}, {word2}"
        print(f"✓ No consecutive duplicates")
    
    # Mark first word as correct (Issue #16: needs mastery_threshold correct answers)
    session.mark_word_mastered(word1)
    print(f"\nMarked word {word1} as correct (1/{session.mastery_threshold})")
    print(f"Available words now: {session.available_words}")
    print(f"Session stats: {session.get_session_stats()}")
    
    # Mark as correct again to fully master it
    session.mark_word_mastered(word1)
    print(f"\nMarked word {word1} as correct (2/{session.mastery_threshold}) - MASTERED")
    print(f"Available words now: {session.available_words}")
    assert word1 not in session.available_words, f"Word {word1} should be removed after mastering"
    
    # Get next word
    word3 = session.get_next_word_id()
    print(f"\nThird word: {word3}")
    
    print("\n✓ Session test passed!")

if __name__ == "__main__":
    test_word_session()
