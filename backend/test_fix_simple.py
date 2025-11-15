"""
Simple test: Verify the 'Session complete' bug fix
No TestClient needed - just test the core logic
"""

import time
from database import (
    create_user, create_child, add_word, 
    reset_db_to_initial, get_words_for_child,
    get_user_mastery_threshold
)
from session import WordSession


def test_session_exhausted_then_word_added():
    """
    Bug scenario: Start session with no words → Add word → Should get word
    Before fix: Would throw "Session complete" error
    After fix: Should return the newly added word
    """
    print("\n" + "="*60)
    print("TEST: Session Exhausted, Then Word Added")
    print("="*60)
    
    reset_db_to_initial()
    
    # Setup
    unique_email = f"test_{int(time.time() * 1000)}@test.com"
    user_id = create_user(unique_email, "password123")
    child_id = create_child(user_id, "Test Child")
    
    print("\n1️⃣ Starting session with 0 words...")
    mastery_threshold = get_user_mastery_threshold(user_id)
    session = WordSession(child_id=child_id, mastery_threshold=mastery_threshold)
    
    word_id = session.get_next_word_id()
    assert word_id is None, "Should have no words"
    print("   ✓ Session has no words (expected)")
    
    print("\n2️⃣ Adding word...")
    new_word_id = add_word("elephant", "animals", user_id=user_id)
    print(f"   ✓ Word added: {new_word_id}")
    
    print("\n3️⃣ Checking if word is available from DB (simulating /next-word fallback)...")
    # This is what the endpoint does when session returns None
    words = get_words_for_child(child_id)
    
    # Before fix: words would be empty
    # After fix: words should contain the newly added word
    assert len(words) > 0, "❌ FAILED: Word not found! The fix didn't work."
    assert words[0]['id'] == new_word_id
    print(f"   ✓ Found fresh word: {words[0]['word']} (id: {words[0]['id']})")
    
    print("\n✅ TEST PASSED: Fix works correctly!")
    reset_db_to_initial()


def test_practice_all_words_then_add_new():
    """
    Test: Master all words in session → Add new word → Should get new word
    """
    print("\n" + "="*60)
    print("TEST: Master All, Then Add New Word")
    print("="*60)
    
    reset_db_to_initial()
    
    # Setup
    unique_email = f"test_{int(time.time() * 1000)}@test.com"
    user_id = create_user(unique_email, "password123")
    child_id = create_child(user_id, "Test Child")
    
    print("\n1️⃣ Adding word and starting session...")
    word_id_1 = add_word("apple", "fruits", user_id=user_id)
    
    mastery_threshold = get_user_mastery_threshold(user_id)
    session = WordSession(child_id=child_id, mastery_threshold=mastery_threshold)
    print(f"   ✓ Started session with mastery threshold: {mastery_threshold}")
    
    print("\n2️⃣ Mastering the word...")
    first_word = session.get_next_word_id()
    assert first_word == word_id_1
    
    for i in range(mastery_threshold):
        session.mark_word_mastered(first_word)
        print(f"   ✓ Practice {i+1} marked as mastered")
    
    print("\n3️⃣ Checking if session is exhausted...")
    next_word = session.get_next_word_id()
    assert next_word is None, "Session should be exhausted"
    print("   ✓ Session exhausted (all words mastered)")
    
    print("\n4️⃣ Adding new word...")
    word_id_2 = add_word("banana", "fruits", user_id=user_id)
    print(f"   ✓ New word added: {word_id_2}")
    
    print("\n5️⃣ Checking if new word is available from DB...")
    words = get_words_for_child(child_id)
    
    assert len(words) > 0, "❌ FAILED: New word not found!"
    # Should find the new word
    found = any(w['id'] == word_id_2 for w in words)
    assert found, f"❌ FAILED: Word {word_id_2} not in result: {words}"
    print(f"   ✓ Found new word: {words[0]['word']}")
    
    print("\n✅ TEST PASSED: Fix works correctly!")
    reset_db_to_initial()


def test_multiple_children_independent_sessions():
    """
    Test: Verify fix works for multiple children with different sessions
    """
    print("\n" + "="*60)
    print("TEST: Multiple Children Independent Sessions")
    print("="*60)
    
    reset_db_to_initial()
    
    # Setup: 2 users, each with a child
    unique_email_1 = f"test_{int(time.time() * 1000)}_1@test.com"
    unique_email_2 = f"test_{int(time.time() * 1000)}_2@test.com"
    
    user_id_1 = create_user(unique_email_1, "password123")
    user_id_2 = create_user(unique_email_2, "password123")
    
    child_id_1 = create_child(user_id_1, "Child 1")
    child_id_2 = create_child(user_id_2, "Child 2")
    
    print("\n1️⃣ Starting sessions for both children...")
    session_1 = WordSession(child_id=child_id_1)
    session_2 = WordSession(child_id=child_id_2)
    print("   ✓ Both sessions started (with no words)")
    
    print("\n2️⃣ Adding word for user 1...")
    word_id_1 = add_word("apple", "fruits", user_id=user_id_1)
    print(f"   ✓ Word added for user 1: {word_id_1}")
    
    print("\n3️⃣ Checking words for both children...")
    words_1 = get_words_for_child(child_id_1)
    words_2 = get_words_for_child(child_id_2)
    
    assert len(words_1) > 0, "Child 1 should see the word"
    assert len(words_2) == 0, "Child 2 should not see user 1's word"
    print(f"   ✓ Child 1 has {len(words_1)} word(s)")
    print(f"   ✓ Child 2 has {len(words_2)} word(s)")
    
    print("\n✅ TEST PASSED: Multiple children isolated correctly!")
    reset_db_to_initial()


if __name__ == "__main__":
    try:
        test_session_exhausted_then_word_added()
        test_practice_all_words_then_add_new()
        test_multiple_children_independent_sessions()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()
        exit(1)
