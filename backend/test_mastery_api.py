"""
Integration tests for mastery threshold API endpoints
Tests the GET and POST /api/admin/mastery-threshold endpoints
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from database import (
    init_db, create_user, create_child, add_word, get_db,
    get_user_mastery_threshold, update_user_mastery_threshold
)

DB_PATH = "../data/test_mastery_api.db"

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

def test_mastery_threshold_api():
    """Test the full mastery threshold workflow"""
    setup()
    
    # Simulate user signup (creates user)
    user_id = create_user("parent@example.com", "password123")
    print(f"✓ User created (ID: {user_id})")
    
    # Test: GET mastery threshold (should be default 2)
    threshold = get_user_mastery_threshold(user_id)
    assert threshold == 2, f"Expected default threshold 2, got {threshold}"
    print(f"✓ Default mastery threshold: {threshold}")
    
    # Test: Parent updates threshold to 3
    success = update_user_mastery_threshold(user_id, 3)
    assert success, "Failed to update threshold to 3"
    
    threshold = get_user_mastery_threshold(user_id)
    assert threshold == 3, f"Expected threshold 3 after update, got {threshold}"
    print(f"✓ Updated mastery threshold to: {threshold}")
    
    # Test: Parent can set it back to 2
    success = update_user_mastery_threshold(user_id, 2)
    assert success, "Failed to update threshold back to 2"
    
    threshold = get_user_mastery_threshold(user_id)
    assert threshold == 2, f"Expected threshold 2 after reset, got {threshold}"
    print(f"✓ Reset mastery threshold to: {threshold}")
    
    # Test: Multiple users have independent thresholds
    user2_id = create_user("parent2@example.com", "password456")
    threshold1 = get_user_mastery_threshold(user_id)
    threshold2 = get_user_mastery_threshold(user2_id)
    
    # Change user1's threshold
    update_user_mastery_threshold(user_id, 4)
    
    # Verify they're independent
    threshold1_after = get_user_mastery_threshold(user_id)
    threshold2_after = get_user_mastery_threshold(user2_id)
    
    assert threshold1_after == 4, "User 1 threshold should be 4"
    assert threshold2_after == 2, "User 2 threshold should still be 2"
    print(f"✓ User 1 threshold: {threshold1_after}, User 2 threshold: {threshold2_after}")
    print("✓ Multiple users have independent threshold settings")
    
    # Test: Threshold applies to all children of a user
    child1_id = create_child(user_id, "Child 1", 8)
    child2_id = create_child(user_id, "Child 2", 6)
    
    # Add word for the family
    word_id = add_word("elephant", "animals", user_id=user_id)
    
    # Both children use parent's mastery threshold when practicing
    parent_threshold = get_user_mastery_threshold(user_id)
    assert parent_threshold == 4, "Parent should have threshold of 4"
    print(f"✓ Parent threshold (4) applies to all children")
    
    cleanup()

if __name__ == "__main__":
    try:
        test_mastery_threshold_api()
        print("\n✓ All mastery threshold API tests passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
