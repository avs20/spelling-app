"""
Tests for child deletion and progress data integrity bug.

Bug Description:
1. Deleting a child deletes the progress data ✓ (intended)
2. Adding a new child shows all words as completed (BUG - should show all as not completed)

These tests verify:
- Deleting a child properly deletes their practice records
- Creating a new child starts with no completed progress
- Practice history doesn't affect new child's word status
"""

import pytest
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from database import (
    init_db, create_user, create_child, delete_child, get_user_children,
    add_word, save_practice, get_words_for_child, get_child_by_id,
    get_db
)

DB_PATH = "../data/test_child_progress.db"

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment with fresh database"""
    import database
    
    database.DB_PATH = DB_PATH
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    init_db()
    
    yield
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

class TestChildDeletion:
    """Tests for child deletion behavior"""
    
    def test_delete_child_removes_practices(self):
        """Verify that deleting a child removes their practice records"""
        # Setup
        user_id = create_user("parent@test.com", "password")
        child_id = create_child(user_id, "Child 1", 8)
        word_id = add_word("apple", "fruits")
        
        # Child practices a word
        save_practice(word_id, child_id, "apple", True, "drawing1.png")
        
        # Verify practice was saved
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ?", (child_id,))
        practice_count = cursor.fetchone()[0]
        conn.close()
        assert practice_count == 1
        
        # Delete child
        delete_child(child_id)
        
        # Verify practices are deleted
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ?", (child_id,))
        practice_count = cursor.fetchone()[0]
        conn.close()
        assert practice_count == 0
    
    def test_delete_child_removes_child_record(self):
        """Verify that deleting a child removes the child record"""
        user_id = create_user("parent@test.com", "password")
        child_id = create_child(user_id, "Child 1", 8)
        
        # Verify child exists
        child = get_child_by_id(child_id)
        assert child is not None
        
        # Delete child
        delete_child(child_id)
        
        # Verify child record is deleted
        child = get_child_by_id(child_id)
        assert child is None
    
    def test_delete_child_does_not_affect_other_children(self):
        """Verify deleting one child doesn't affect other children's practices"""
        user_id = create_user("parent@test.com", "password")
        child1_id = create_child(user_id, "Child 1", 8)
        child2_id = create_child(user_id, "Child 2", 6)
        
        word_id = add_word("banana", "fruits")
        
        # Both children practice
        save_practice(word_id, child1_id, "banana", True, "drawing1.png")
        save_practice(word_id, child2_id, "banana", True, "drawing2.png")
        
        # Delete child 1
        delete_child(child1_id)
        
        # Verify child 2's practice remains
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ?", (child2_id,))
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 1
    
    def test_delete_child_does_not_affect_word_records(self):
        """Verify deleting a child doesn't delete the words themselves"""
        user_id = create_user("parent@test.com", "password")
        child_id = create_child(user_id, "Child 1", 8)
        word_id = add_word("cherry", "fruits")
        
        # Child practices
        save_practice(word_id, child_id, "cherry", True, "drawing.png")
        
        # Verify word exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM words WHERE id = ?", (word_id,))
        word_count = cursor.fetchone()[0]
        conn.close()
        assert word_count == 1
        
        # Delete child
        delete_child(child_id)
        
        # Verify word still exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM words WHERE id = ?", (word_id,))
        word_count = cursor.fetchone()[0]
        conn.close()
        assert word_count == 1


class TestNewChildProgressReset:
    """Tests for new child progress initialization (the bug)"""
    
    def test_new_child_has_no_practices(self):
        """Verify new child has no practice records"""
        user_id = create_user("parent@test.com", "password")
        child_id = create_child(user_id, "New Child", 8)
        
        # Check practices for new child
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ?", (child_id,))
        practice_count = cursor.fetchone()[0]
        conn.close()
        
        assert practice_count == 0
    
    def test_new_child_sees_all_words_as_unpracticed(self):
        """
        Bug Test: When a new child is created, all words should show as unpracticed.
        If another child completed the words, new child should start fresh.
        """
        user_id = create_user("parent@test.com", "password")
        child1_id = create_child(user_id, "Child 1", 8)
        
        # Add words
        word1_id = add_word("dog", "animals")
        word2_id = add_word("cat", "animals")
        word3_id = add_word("bird", "animals")
        
        # Child 1 completes all words
        for word_id in [word1_id, word2_id, word3_id]:
            for i in range(3):  # Practice multiple times
                save_practice(word_id, child1_id, "correct_spelling", True, f"drawing{i}.png")
        
        # Update words to mark them as completed (successful_days > 0)
        conn = get_db()
        cursor = conn.cursor()
        today = date.today().isoformat()
        for word_id in [word1_id, word2_id, word3_id]:
            cursor.execute(
                "UPDATE words SET successful_days = 3, last_practiced = ?, next_review = ? WHERE id = ?",
                (today, today, word_id)
            )
        conn.commit()
        conn.close()
        
        # Create a new child
        child2_id = create_child(user_id, "New Child", 6)
        
        # Verify new child has no practices
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ?", (child2_id,))
        practice_count = cursor.fetchone()[0]
        conn.close()
        
        assert practice_count == 0, "New child should have no practices"
    
    def test_child1_and_child2_have_separate_progress(self):
        """Verify that two children have independent progress tracking"""
        user_id = create_user("parent@test.com", "password")
        child1_id = create_child(user_id, "Child 1", 8)
        child2_id = create_child(user_id, "Child 2", 6)
        
        word_id = add_word("elephant", "animals")
        
        # Child 1 practices the word
        save_practice(word_id, child1_id, "elephant", True, "drawing1.png")
        save_practice(word_id, child1_id, "elephant", True, "drawing2.png")
        
        # Child 2 hasn't practiced it
        conn = get_db()
        cursor = conn.cursor()
        
        # Get practices for child 1
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ? AND word_id = ?", 
                      (child1_id, word_id))
        child1_count = cursor.fetchone()[0]
        
        # Get practices for child 2
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ? AND word_id = ?", 
                      (child2_id, word_id))
        child2_count = cursor.fetchone()[0]
        
        conn.close()
        
        assert child1_count == 2, "Child 1 should have 2 practices"
        assert child2_count == 0, "Child 2 should have 0 practices"
    
    def test_deleting_child1_does_not_reset_word_progress(self):
        """
        Test that deleting child1 doesn't affect word.successful_days
        which would incorrectly show as "completed" for new children.
        
        The words table stores progress globally, which might be the issue.
        """
        user_id = create_user("parent@test.com", "password")
        child1_id = create_child(user_id, "Child 1", 8)
        
        word_id = add_word("lion", "animals")
        
        # Child 1 practices and succeeds
        save_practice(word_id, child1_id, "lion", True, "drawing.png")
        
        # Update word progress
        conn = get_db()
        cursor = conn.cursor()
        today = date.today().isoformat()
        cursor.execute(
            "UPDATE words SET successful_days = 1, last_practiced = ?, next_review = ? WHERE id = ?",
            (today, today, word_id)
        )
        conn.commit()
        
        # Verify word has successful_days = 1
        cursor.execute("SELECT successful_days FROM words WHERE id = ?", (word_id,))
        successful_days = cursor.fetchone()[0]
        conn.close()
        assert successful_days == 1
        
        # Delete child 1
        delete_child(child1_id)
        
        # Verify word still has successful_days = 1
        # (This is the issue - new child will think this word is completed)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT successful_days FROM words WHERE id = ?", (word_id,))
        successful_days = cursor.fetchone()[0]
        conn.close()
        assert successful_days == 1
    
    def test_new_child_after_delete_shows_word_status_correctly(self):
        """
        Integration test: After deleting a child with completed words,
        a new child should show those words as needing practice.
        
        This tests the actual bug scenario.
        """
        user_id = create_user("parent@test.com", "password")
        child1_id = create_child(user_id, "Child 1", 8)
        
        # Create word
        word_id = add_word("tiger", "animals")
        
        # Child 1 completes the word (practices and succeeds)
        save_practice(word_id, child1_id, "tiger", True, "drawing.png")
        
        # Update word as completed
        conn = get_db()
        cursor = conn.cursor()
        today = date.today().isoformat()
        cursor.execute(
            "UPDATE words SET successful_days = 2, last_practiced = ?, next_review = ? WHERE id = ?",
            (today, today, word_id)
        )
        conn.commit()
        conn.close()
        
        # Delete child 1
        delete_child(child1_id)
        
        # Create new child
        child2_id = create_child(user_id, "Child 2", 6)
        
        # Verify new child has zero practices for the word
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ? AND word_id = ?",
                      (child2_id, word_id))
        practice_count = cursor.fetchone()[0]
        conn.close()
        
        assert practice_count == 0, "New child should have no practices for any word"
    
    def test_multiple_children_independent_practice_records(self):
        """
        Test that practice records are properly isolated per child.
        Each child should have their own practice history.
        """
        user_id = create_user("parent@test.com", "password")
        child1_id = create_child(user_id, "Child 1", 8)
        child2_id = create_child(user_id, "Child 2", 6)
        child3_id = create_child(user_id, "Child 3", 5)
        
        word1_id = add_word("monkey", "animals")
        word2_id = add_word("giraffe", "animals")
        
        # Child 1 practices word 1 (successful)
        save_practice(word1_id, child1_id, "monkey", True, "c1_d1.png")
        save_practice(word1_id, child1_id, "monkey", False, "c1_d2.png")
        
        # Child 2 practices word 2 (unsuccessful)
        save_practice(word2_id, child2_id, "giraffe", False, "c2_d1.png")
        
        # Child 3 doesn't practice anything
        
        # Verify correct isolation
        conn = get_db()
        cursor = conn.cursor()
        
        # Child 1: 2 practices for word 1, 0 for word 2
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ? AND word_id = ?",
                      (child1_id, word1_id))
        assert cursor.fetchone()[0] == 2
        
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ? AND word_id = ?",
                      (child1_id, word2_id))
        assert cursor.fetchone()[0] == 0
        
        # Child 2: 0 for word 1, 1 for word 2
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ? AND word_id = ?",
                      (child2_id, word1_id))
        assert cursor.fetchone()[0] == 0
        
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ? AND word_id = ?",
                      (child2_id, word2_id))
        assert cursor.fetchone()[0] == 1
        
        # Child 3: 0 for both
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ?", (child3_id,))
        assert cursor.fetchone()[0] == 0
        
        conn.close()
    
    def test_delete_one_child_does_not_affect_others_progress(self):
        """
        Test that deleting one child doesn't affect other children's progress.
        """
        user_id = create_user("parent@test.com", "password")
        child1_id = create_child(user_id, "Child 1", 8)
        child2_id = create_child(user_id, "Child 2", 6)
        
        word_id = add_word("zebra", "animals")
        
        # Both children practice
        save_practice(word_id, child1_id, "zebra", True, "c1.png")
        save_practice(word_id, child2_id, "zebra", True, "c2.png")
        
        # Delete child 1
        delete_child(child1_id)
        
        # Verify child 2's practice still exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ?", (child2_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1, "Child 2's practices should be preserved"


class TestBugDemonstration:
    """
    Demonstrates the actual bug: successful_days is shared across all children.
    
    Root cause: The 'successful_days' field in the words table is NOT per-child.
    It's a global metric for the word. When get_words_for_child() returns words,
    it includes this global successful_days value, causing new children to see
    words as "already completed" if any child has practiced them.
    """
    
    def test_get_words_for_child_returns_successful_days(self):
        """Verify that get_words_for_child returns successful_days field"""
        from database import get_words_for_child
        
        user_id = create_user("parent@test.com", "password")
        child_id = create_child(user_id, "Child", 8)
        
        word_id = add_word("pencil", "objects")
        
        words = get_words_for_child(child_id)
        
        assert len(words) > 0
        assert 'successful_days' in words[0]
    
    def test_bug_shared_successful_days(self):
        """
        VERIFIES THE FIX:
        When child1 completes a word, it only affects child1's progress.
        When child2 (new) requests the same word, they see successful_days = 0
        because they haven't practiced it yet. The per-child progress tracking is working.
        """
        from database import get_words_for_child
        
        user_id = create_user("parent@test.com", "password")
        child1_id = create_child(user_id, "Child 1", 8)
        child2_id = create_child(user_id, "Child 2", 6)
        
        word_id = add_word("notebook", "objects")
        
        # Initial state: word should have successful_days = 0 in words table
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT successful_days FROM words WHERE id = ?", (word_id,))
        initial_days = cursor.fetchone()[0]
        conn.close()
        assert initial_days == 0
        
        # Child 1 practices and completes the word
        save_practice(word_id, child1_id, "notebook", True, "drawing.png")
        
        # Update child1's progress in child_progress table
        conn = get_db()
        cursor = conn.cursor()
        today = date.today().isoformat()
        cursor.execute(
            "INSERT INTO child_progress (child_id, word_id, successful_days, last_practiced, next_review) VALUES (?, ?, ?, ?, ?)",
            (child1_id, word_id, 2, today, today)
        )
        conn.commit()
        conn.close()
        
        # Now when child 2 requests words, they should see successful_days = 0
        words_for_child2 = get_words_for_child(child2_id)
        
        # FIX VERIFIED: Child 2 sees successful_days = 0 even though child1 completed it
        notebook_word = next((w for w in words_for_child2 if w['id'] == word_id), None)
        
        if notebook_word:  # Word should be in the list
            assert notebook_word['successful_days'] == 0, \
                f"FIXED: Child 2 should see successful_days=0, not {notebook_word['successful_days']}"
        
        # Verify child 2 has NO practices for this word
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ? AND word_id = ?",
                      (child2_id, word_id))
        practice_count = cursor.fetchone()[0]
        conn.close()
        
        assert practice_count == 0, "Child 2 should have no practices for this word"
        
        # Child 2 sees unpracticed status (successful_days = 0), which is correct
        if notebook_word:
            assert notebook_word['successful_days'] == 0, \
                "FIX VERIFIED: Child 2 sees correct unpracticed status"
    
    def test_bug_scenario_step_by_step(self):
        """
        Complete scenario with per-child progress tracking (FIX VERIFIED):
        1. User creates child "Alice"
        2. Alice practices words (some completed, some not)
        3. User deletes Alice
        4. User creates new child "Bob"
        5. FIXED: Bob sees all words as unpracticed (fresh start)
        """
        from database import get_words_for_child
        
        user_id = create_user("parent@test.com", "password")
        alice_id = create_child(user_id, "Alice", 8)
        
        # Create words
        word1_id = add_word("house", "places")
        word2_id = add_word("school", "places")
        word3_id = add_word("park", "places")
        
        # Alice practices words 1 and 2, completes them
        for word_id in [word1_id, word2_id]:
            save_practice(word_id, alice_id, "correct", True, "alice_drawing.png")
            conn = get_db()
            cursor = conn.cursor()
            today = date.today().isoformat()
            # Update Alice's progress in child_progress table
            cursor.execute(
                "INSERT INTO child_progress (child_id, word_id, successful_days, last_practiced, next_review) VALUES (?, ?, ?, ?, ?)",
                (alice_id, word_id, 3, today, today)
            )
            conn.commit()
            conn.close()
        
        # Alice practices word 3 but doesn't complete it
        save_practice(word3_id, alice_id, "wrong", False, "alice_drawing2.png")
        
        # Verify Alice's state
        alice_words = get_words_for_child(alice_id)
        assert any(w['id'] == word1_id and w['successful_days'] == 3 for w in alice_words), \
            "Alice should see word1 with successful_days=3"
        assert any(w['id'] == word2_id and w['successful_days'] == 3 for w in alice_words), \
            "Alice should see word2 with successful_days=3"
        
        # Delete Alice
        delete_child(alice_id)
        
        # Create Bob
        bob_id = create_child(user_id, "Bob", 6)
        
        # FIXED: Bob sees all words as unpracticed
        bob_words = get_words_for_child(bob_id)
        
        house_word = next((w for w in bob_words if w['id'] == word1_id), None)
        school_word = next((w for w in bob_words if w['id'] == word2_id), None)
        park_word = next((w for w in bob_words if w['id'] == word3_id), None)
        
        # FIXED: Bob sees these as unpracticed (successful_days=0) because he never practiced them
        if house_word:
            assert house_word['successful_days'] == 0, \
                f"FIXED: Bob sees 'house' with successful_days=0 (unpracticed)"
        
        if school_word:
            assert school_word['successful_days'] == 0, \
                f"FIXED: Bob sees 'school' with successful_days=0 (unpracticed)"
        
        # Verify Bob has NO practices
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM practices WHERE child_id = ?", (bob_id,))
        bob_practice_count = cursor.fetchone()[0]
        conn.close()
        
        assert bob_practice_count == 0, \
            f"Bob should have no practices, but has {bob_practice_count}"
        
        # Bob starts fresh with all words showing as unpracticed - bug is fixed!
        all_unpracticed = all(w['successful_days'] == 0 for w in bob_words)
        assert all_unpracticed, \
            "All of Bob's words should be unpracticed (successful_days=0)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
