"""
Phase 7: Tests for data management
"""

import pytest
import sys
import os
import shutil
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, add_word, save_practice
from data_management import (
    cleanup_old_drawings, get_storage_stats, optimize_database, 
    create_backup, get_database_size, get_drawings_directory_size
)

DB_PATH = "../data/test_data_mgmt.db"
DRAWINGS_DIR = "../data/test_drawings"
BACKUPS_DIR = "../data/test_backups"

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment"""
    import database
    import data_management
    
    database.DB_PATH = DB_PATH
    data_management.DB_PATH = DB_PATH
    data_management.DRAWINGS_DIR = DRAWINGS_DIR
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(DRAWINGS_DIR):
        shutil.rmtree(DRAWINGS_DIR)
    if os.path.exists(BACKUPS_DIR):
        shutil.rmtree(BACKUPS_DIR)
    
    os.makedirs(DRAWINGS_DIR, exist_ok=True)
    
    init_db()
    
    yield
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(DRAWINGS_DIR):
        shutil.rmtree(DRAWINGS_DIR)
    if os.path.exists(BACKUPS_DIR):
        shutil.rmtree(BACKUPS_DIR)

def create_test_drawing(filename):
    """Create a test PNG drawing"""
    img = Image.new('RGB', (100, 100), color='white')
    filepath = os.path.join(DRAWINGS_DIR, filename)
    img.save(filepath, 'PNG')
    return filepath

def test_cleanup_old_drawings():
    """Test cleaning up old drawings"""
    word_id = add_word("wasp", "insects")
    
    for i in range(15):
        filename = f"drawing_{i}.png"
        create_test_drawing(filename)
        save_practice(word_id, "bee", True, filename)
    
    deleted = cleanup_old_drawings(keep_per_word=10)
    
    assert deleted == 5
    assert len(os.listdir(DRAWINGS_DIR)) == 10

def test_cleanup_multiple_words():
    """Test cleanup with multiple words"""
    word1_id = add_word("moth", "insects")
    word2_id = add_word("flea", "insects")
    
    for i in range(12):
        filename = f"bee_drawing_{i}.png"
        create_test_drawing(filename)
        save_practice(word1_id, "bee", True, filename)
    
    for i in range(8):
        filename = f"ant_drawing_{i}.png"
        create_test_drawing(filename)
        save_practice(word2_id, "ant", True, filename)
    
    deleted = cleanup_old_drawings(keep_per_word=5)
    
    assert deleted == 10
    assert len(os.listdir(DRAWINGS_DIR)) == 10

def test_get_storage_stats():
    """Test getting storage statistics"""
    word_id = add_word("tick", "insects")
    
    for i in range(3):
        filename = f"drawing_{i}.png"
        create_test_drawing(filename)
        save_practice(word_id, "bee", True, filename)
    
    stats = get_storage_stats()
    
    assert stats['database_size_bytes'] > 0
    assert stats['database_size_mb'] >= 0
    assert stats['drawings_size_bytes'] > 0
    assert stats['drawings_size_mb'] >= 0
    assert stats['total_size_mb'] >= 0
    assert stats['drawings_count'] == 3

def test_optimize_database():
    """Test database optimization"""
    word_id = add_word("gnat", "insects")
    
    for i in range(10):
        save_practice(word_id, "bee", True, f"drawing_{i}.png")
    
    success = optimize_database()
    assert success is True

def test_create_backup():
    """Test database backup creation"""
    word_id = add_word("mite", "insects")
    save_practice(word_id, "bee", True, "drawing.png")
    
    filename = create_backup(BACKUPS_DIR)
    
    assert filename is not None
    assert filename.startswith("spelling_backup_")
    assert filename.endswith(".db")
    assert os.path.exists(os.path.join(BACKUPS_DIR, filename))

def test_get_database_size():
    """Test getting database size"""
    size = get_database_size()
    assert size > 0

def test_get_drawings_directory_size():
    """Test getting drawings directory size"""
    create_test_drawing("test1.png")
    create_test_drawing("test2.png")
    
    size = get_drawings_directory_size()
    assert size > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
