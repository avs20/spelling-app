"""
Phase 7: Data management and performance utilities
"""

import os
import sqlite3
from datetime import datetime, timedelta
from PIL import Image
import io

IS_DOCKER = os.path.exists('/.dockerenv') or os.getenv('FLY_APP_NAME')
BASE_DIR = '/app' if IS_DOCKER else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'spelling.db')
DRAWINGS_DIR = os.path.join(BASE_DIR, 'data', 'drawings')


def compress_drawing(filename):
    """
    Compress a drawing image from PNG to JPEG to reduce file size
    Returns new filename if successful, None otherwise
    """
    try:
        png_path = os.path.join(DRAWINGS_DIR, filename)
        
        if not os.path.exists(png_path):
            return None
        
        with Image.open(png_path) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            
            jpeg_filename = filename.replace('.png', '.jpg')
            jpeg_path = os.path.join(DRAWINGS_DIR, jpeg_filename)
            
            img.save(jpeg_path, 'JPEG', quality=85, optimize=True)
            
            if os.path.exists(jpeg_path):
                os.remove(png_path)
                return jpeg_filename
            
        return None
    except Exception as e:
        print(f"Error compressing {filename}: {e}")
        return None


def cleanup_old_drawings(keep_per_word=10):
    """
    Delete old drawings, keeping only the most recent N per word
    Returns count of deleted files
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT word_id, drawing_filename, practiced_date
        FROM practices
        WHERE drawing_filename IS NOT NULL
        ORDER BY word_id, practiced_date DESC
    """)
    
    practices = cursor.fetchall()
    conn.close()
    
    word_drawings = {}
    for word_id, filename, date in practices:
        if word_id not in word_drawings:
            word_drawings[word_id] = []
        word_drawings[word_id].append((filename, date))
    
    deleted_count = 0
    
    for word_id, drawings in word_drawings.items():
        if len(drawings) > keep_per_word:
            to_delete = drawings[keep_per_word:]
            
            for filename, _ in to_delete:
                filepath = os.path.join(DRAWINGS_DIR, filename)
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting {filename}: {e}")
    
    return deleted_count


def get_database_size():
    """
    Get the size of the database file in bytes
    """
    if os.path.exists(DB_PATH):
        return os.path.getsize(DB_PATH)
    return 0


def get_drawings_directory_size():
    """
    Get total size of all drawings in bytes
    """
    total_size = 0
    if os.path.exists(DRAWINGS_DIR):
        for filename in os.listdir(DRAWINGS_DIR):
            filepath = os.path.join(DRAWINGS_DIR, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def optimize_database():
    """
    Run VACUUM on database to reclaim space and optimize
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("VACUUM")
        conn.close()
        return True
    except Exception as e:
        print(f"Error optimizing database: {e}")
        return False


def create_backup(backup_dir="../data/backups"):
    """
    Create a backup of the database
    Returns backup filename if successful
    """
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"spelling_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        
        return backup_filename
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None


def get_storage_stats():
    """
    Get storage statistics
    """
    db_size = get_database_size()
    drawings_size = get_drawings_directory_size()
    
    drawings_count = 0
    if os.path.exists(DRAWINGS_DIR):
        drawings_count = len([f for f in os.listdir(DRAWINGS_DIR) if os.path.isfile(os.path.join(DRAWINGS_DIR, f))])
    
    return {
        'database_size_bytes': db_size,
        'database_size_mb': round(db_size / (1024 * 1024), 2),
        'drawings_size_bytes': drawings_size,
        'drawings_size_mb': round(drawings_size / (1024 * 1024), 2),
        'total_size_mb': round((db_size + drawings_size) / (1024 * 1024), 2),
        'drawings_count': drawings_count
    }
