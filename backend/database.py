"""
Database setup and operations
SQLite database for words and practices
Phase 4: Spaced repetition tracking
Phase 12: Multi-user and multi-child support
Phase 13: Modal deployment with Turso support
"""

import sqlite3
from datetime import datetime, timedelta, date
import os
import hashlib
import secrets

try:
    import libsql_experimental as libsql
    LIBSQL_AVAILABLE = True
except ImportError:
    LIBSQL_AVAILABLE = False

IS_DOCKER = os.path.exists('/.dockerenv') or os.getenv('FLY_APP_NAME')
IS_MODAL = os.getenv('MODAL_APP_ID') is not None
BASE_DIR = '/app' if IS_DOCKER else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Modal uses /modal-data for persistent volume, Fly.io/Docker use /app/data
DATA_DIR = '/modal-data' if IS_MODAL else os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'spelling.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

TURSO_DATABASE_URL = os.getenv('TURSO_DATABASE_URL')
TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN')
USE_TURSO = TURSO_DATABASE_URL and TURSO_AUTH_TOKEN and LIBSQL_AVAILABLE

def _convert_row_to_dict(row, column_names=None):
    """
    Convert database row to dictionary.
    Handles both SQLite Row objects and libSQL tuple results.
    
    Args:
        row: Database row object (Row, tuple, or dict)
        column_names: List of column names for tuple results. Required for libSQL tuples.
    
    Returns:
        Dictionary representation of the row, or None if row is None
    """
    if row is None:
        return None
    
    # Already a dict
    if isinstance(row, dict):
        return row
    
    # SQLite Row object with keys() method
    if hasattr(row, 'keys'):
        return dict(row)
    
    # Tuple-like result from libSQL - requires column_names
    if column_names:
        return {name: row[i] for i, name in enumerate(column_names)}
    
    # Fallback: if no column names provided for tuple, raise error
    # This helps catch missing column_names arguments
    if isinstance(row, (tuple, list)):
        raise ValueError(f"Cannot convert tuple/list to dict without column_names. Row type: {type(row)}, Row: {row}")
    
    # Unknown type - return as-is (shouldn't happen)
    return row

def get_db():
    """
    Get database connection
    Supports both local SQLite and remote Turso (libSQL)
    """
    if USE_TURSO:
        conn = libsql.connect(TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Initialize database with tables"""
    # Ensure database directory exists
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    os.makedirs(db_dir, exist_ok=True)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table - Phase 12: Parent/teacher accounts
    # Issue #16: Added session_mastery_threshold for configurable word mastery
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            session_mastery_threshold INTEGER DEFAULT 2,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Children table - Phase 12: Child profiles linked to users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Words table - Phase 4: Added successful_days, last_practiced, next_review
    # Phase 5: Added reference_image
    # Phase 12: Added user_id for family custom words (NULL = core/global)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            category TEXT NOT NULL,
            successful_days INTEGER DEFAULT 0,
            last_practiced DATE,
            next_review DATE,
            reference_image TEXT,
            user_id INTEGER,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(word, user_id)
        )
    """)
    
    # Practices table - Phase 12: Added child_id to tie practices to specific child
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS practices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            child_id INTEGER NOT NULL,
            spelled_word TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            drawing_filename TEXT,
            practiced_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (word_id) REFERENCES words(id),
            FOREIGN KEY (child_id) REFERENCES children(id)
        )
    """)
    
    # Child Progress table - Phase 13: Per-child word progress tracking
    # Tracks successful_days per child to fix multi-child isolation bug
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS child_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER NOT NULL,
            word_id INTEGER NOT NULL,
            successful_days INTEGER DEFAULT 0,
            last_practiced DATE,
            next_review DATE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (child_id) REFERENCES children(id),
            FOREIGN KEY (word_id) REFERENCES words(id),
            UNIQUE(child_id, word_id)
        )
    """)
    
    # No default/core words - each family adds their own words
    
    conn.commit()
    conn.close()

def get_all_words():
    """Get all words from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, word, category FROM words")
    words = cursor.fetchall()
    conn.close()
    return [_convert_row_to_dict(word, ['id', 'word', 'category']) for word in words]

def get_word_for_practice(practiced_today=None):
    """
    Get next word to practice - Phase 4
    
    Returns words where next_review <= today, excluding already practiced today
    Shuffles to provide variety
    
    Args:
        practiced_today: set of word IDs already practiced in this session
    """
    if practiced_today is None:
        practiced_today = set()
    
    conn = get_db()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    # Get words ready for review (where next_review <= today)
    # Exclude already practiced words in this session
    cursor.execute("""
        SELECT id, word, category, successful_days
        FROM words
        WHERE next_review <= ?
        ORDER BY RANDOM()
        LIMIT 1
    """, (today,))
    
    word = cursor.fetchone()
    conn.close()
    return _convert_row_to_dict(word, ['id', 'word', 'category', 'successful_days'])

def get_word_by_id(word_id: int):
    """Get word by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT word, category FROM words WHERE id = ?", (word_id,))
    word = cursor.fetchone()
    conn.close()
    return _convert_row_to_dict(word, ['word', 'category'])

def save_practice(word_id: int, child_id: int, spelled_word: str, is_correct: bool, drawing_filename: str):
    """Save practice record"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO practices (word_id, child_id, spelled_word, is_correct, drawing_filename)
        VALUES (?, ?, ?, ?, ?)
    """, (word_id, child_id, spelled_word, is_correct, drawing_filename))
    conn.commit()
    conn.close()

def get_practices_for_word(word_id: int):
    """Get all practices for a word"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, spelled_word, is_correct, drawing_filename, practiced_date
        FROM practices
        WHERE word_id = ?
        ORDER BY practiced_date DESC
    """, (word_id,))
    practices = cursor.fetchall()
    conn.close()
    return [_convert_row_to_dict(p, ['id', 'spelled_word', 'is_correct', 'drawing_filename', 'practiced_date']) for p in practices]

def update_word_on_success(word_id: int):
    """
    Phase 4: Update word progress after successful practice
    
    - Increment successful_days (once per day)
    - Update last_practiced to today
    - Calculate next_review based on successful_days
    
    Returns: True if successful_days was incremented, False if already practiced today
    """
    conn = get_db()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    # Get current word data
    cursor.execute("SELECT successful_days, last_practiced FROM words WHERE id = ?", (word_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False
    
    current_successful_days, last_practiced = row
    
    # Only increment if not already practiced today
    if last_practiced == today:
        conn.close()
        return False  # Already practiced today
    
    # Increment successful_days
    new_successful_days = current_successful_days + 1
    
    # Calculate next_review based on successful_days
    if new_successful_days == 1:
        # After first success → review in 2 days
        next_review = (date.today() + timedelta(days=2)).isoformat()
    elif new_successful_days >= 2:
        # After 2+ successes → review in 3 days
        next_review = (date.today() + timedelta(days=3)).isoformat()
    else:
        next_review = (date.today() + timedelta(days=1)).isoformat()
    
    # Update word record
    cursor.execute("""
        UPDATE words
        SET successful_days = ?, last_practiced = ?, next_review = ?
        WHERE id = ?
    """, (new_successful_days, today, next_review, word_id))
    
    conn.commit()
    conn.close()
    return True

def get_words_for_today():
    """
    Phase 4: Get all words ready for practice today
    Returns words where next_review <= today, sorted by successful_days
    """
    conn = get_db()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    cursor.execute("""
        SELECT id, word, category, successful_days
        FROM words
        WHERE next_review <= ?
        ORDER BY successful_days ASC, word ASC
    """, (today,))
    
    words = cursor.fetchall()
    conn.close()
    return [_convert_row_to_dict(w, ['id', 'word', 'category', 'successful_days']) for w in words]

def add_word(word: str, category: str, reference_image: str = None, user_id: int = None):
    """
    Phase 5: Add a new word to the database
    Phase 12: user_id required - all words belong to a family
    """
    conn = get_db()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    try:
        cursor.execute("""
            INSERT INTO words (word, category, successful_days, next_review, user_id)
            VALUES (?, ?, 0, ?, ?)
        """, (word.lower(), category, today, user_id))
        
        word_id = cursor.lastrowid
        
        if reference_image:
            cursor.execute("""
                UPDATE words SET reference_image = ? WHERE id = ?
            """, (reference_image, word_id))
        
        conn.commit()
        conn.close()
        return word_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Word '{word}' already exists for your family")

def update_word(word_id: int, word: str = None, category: str = None, reference_image: str = None):
    """
    Phase 5: Update a word's details
    """
    conn = get_db()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if word:
        updates.append("word = ?")
        params.append(word.lower())
    if category:
        updates.append("category = ?")
        params.append(category)
    if reference_image is not None:
        updates.append("reference_image = ?")
        params.append(reference_image)
    
    if not updates:
        conn.close()
        return False
    
    params.append(word_id)
    query = f"UPDATE words SET {', '.join(updates)} WHERE id = ?"
    
    cursor.execute(query, params)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def delete_word(word_id: int):
    """
    Phase 5: Delete a word and all its practices
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM practices WHERE word_id = ?", (word_id,))
    cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
    
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def get_all_words_admin(user_id: int):
    """
    Phase 12: Get all words with full details for user's admin panel
    Returns only this user's words (user_id must match)
    Includes reference_image for flashcard support (Issue #15)
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, word, category, successful_days, last_practiced, next_review, reference_image, created_date
        FROM words
        WHERE user_id = ?
        ORDER BY created_date DESC
    """, (user_id,))
    words = cursor.fetchall()
    conn.close()
    return [_convert_row_to_dict(word, ['id', 'word', 'category', 'successful_days', 'last_practiced', 'next_review', 'reference_image', 'created_date']) for word in words]

def get_practice_stats():
    """
    Phase 6: Get overall practice statistics for dashboard
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT CASE WHEN DATE(practiced_date) = DATE('now') THEN word_id END) as words_today,
            COUNT(DISTINCT CASE WHEN DATE(practiced_date) >= DATE('now', '-7 days') THEN word_id END) as words_this_week,
            ROUND(AVG(CASE WHEN is_correct = 1 THEN 100.0 ELSE 0.0 END), 1) as overall_accuracy,
            COUNT(*) as total_practices
        FROM practices
    """)
    
    stats = cursor.fetchone()
    conn.close()
    
    if stats:
        return {
            'words_today': stats[0] or 0,
            'words_this_week': stats[1] or 0,
            'overall_accuracy': stats[2] or 0.0,
            'total_practices': stats[3] or 0
        }
    return {'words_today': 0, 'words_this_week': 0, 'overall_accuracy': 0.0, 'total_practices': 0}

def get_word_accuracy():
    """
    Phase 6: Get accuracy per word, sorted by worst performing
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            w.word,
            w.category,
            COUNT(*) as total_attempts,
            SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_attempts,
            ROUND(100.0 * SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy
        FROM words w
        JOIN practices p ON w.id = p.word_id
        GROUP BY w.id, w.word, w.category
        ORDER BY accuracy ASC, total_attempts DESC
    """)
    
    words = cursor.fetchall()
    conn.close()
    
    return [{
        'word': w[0],
        'category': w[1],
        'total_attempts': w[2],
        'correct_attempts': w[3],
        'accuracy': w[4]
    } for w in words]

def get_practice_trend(days=7):
    """
    Phase 6: Get practice trend over last N days
    Returns daily practice counts for line chart
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(f"""
        SELECT 
            DATE(practiced_date) as practice_date,
            COUNT(*) as practice_count,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_count
        FROM practices
        WHERE DATE(practiced_date) >= DATE('now', '-{days} days')
        GROUP BY DATE(practiced_date)
        ORDER BY practice_date ASC
    """)
    
    trend = cursor.fetchall()
    conn.close()
    
    return [{
        'date': t[0],
        'total': t[1],
        'correct': t[2]
    } for t in trend]

def get_recent_drawings(limit=10):
    """
    Phase 6: Get recent drawings with metadata for gallery
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.drawing_filename,
            w.word,
            p.is_correct,
            p.practiced_date
        FROM practices p
        JOIN words w ON p.word_id = w.id
        WHERE p.drawing_filename IS NOT NULL
        ORDER BY p.practiced_date DESC
        LIMIT ?
    """, (limit,))
    
    drawings = cursor.fetchall()
    conn.close()
    
    return [{
        'filename': d[0],
        'word': d[1],
        'is_correct': bool(d[2]),
        'practiced_date': d[3]
    } for d in drawings]

def reset_db_to_initial():
    """
    Reset database to original state with only 3 initial words
    Deletes all practices and user words, keeps only bee, spider, butterfly
    """
    conn = get_db()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    # Delete all practices
    cursor.execute("DELETE FROM practices")
    
    # Delete all words
    cursor.execute("DELETE FROM words")
    
    # Re-insert initial words
    test_words = [
        ("bee", "insects", 0, None, today, None),
        ("spider", "insects", 0, None, today, None),
        ("butterfly", "insects", 0, None, today, None)
    ]
    cursor.executemany(
        "INSERT INTO words (word, category, successful_days, last_practiced, next_review, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        test_words
    )
    
    conn.commit()
    conn.close()
    return True

# ===== PHASE 12: User & Child Management =====

def hash_password(password: str) -> str:
    """Hash password using PBKDF2"""
    salt = secrets.token_hex(32)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hash_obj.hex()}"

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hash_hex = password_hash.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == hash_hex
    except:
        return False

def create_user(email: str, password: str) -> int:
    """Create new user account. Returns user_id."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email.lower(), password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Email '{email}' already registered")

def get_user_by_email(email: str):
    """Get user by email"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (email.lower(),))
    user = cursor.fetchone()
    conn.close()
    return _convert_row_to_dict(user, ['id', 'email', 'password_hash'])

def get_user_by_id(user_id: int):
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, created_date FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return _convert_row_to_dict(user, ['id', 'email', 'created_date'])

def create_child(user_id: int, name: str, age: int = None) -> int:
    """Create child profile. Returns child_id."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO children (user_id, name, age) VALUES (?, ?, ?)",
        (user_id, name, age)
    )
    conn.commit()
    child_id = cursor.lastrowid
    conn.close()
    return child_id

def get_user_children(user_id: int):
    """Get all children for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, name, age, created_date FROM children WHERE user_id = ? ORDER BY created_date DESC",
        (user_id,)
    )
    children = cursor.fetchall()
    conn.close()
    return [_convert_row_to_dict(c, ['id', 'user_id', 'name', 'age', 'created_date']) for c in children]

def get_child_by_id(child_id: int):
    """Get child by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, name, age, created_date FROM children WHERE id = ?",
        (child_id,)
    )
    child = cursor.fetchone()
    conn.close()
    return _convert_row_to_dict(child, ['id', 'user_id', 'name', 'age', 'created_date']) if child else None

def update_child(child_id: int, name: str = None, age: int = None) -> bool:
    """Update child profile"""
    conn = get_db()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if name:
        updates.append("name = ?")
        params.append(name)
    if age is not None:
        updates.append("age = ?")
        params.append(age)
    
    if not updates:
        conn.close()
        return False
    
    params.append(child_id)
    query = f"UPDATE children SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def delete_child(child_id: int) -> bool:
    """Delete child and all their practices and progress"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM practices WHERE child_id = ?", (child_id,))
    cursor.execute("DELETE FROM child_progress WHERE child_id = ?", (child_id,))
    cursor.execute("DELETE FROM children WHERE id = ?", (child_id,))
    
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def get_words_for_child(child_id: int):
    """
    Phase 13: Get words available for child with per-child progress
    Returns only family's own words (no shared core words)
    Uses child_progress table for per-child successful_days tracking
    Only returns words that need practice (next_review <= today)
    Includes reference_image for flashcard support (Issue #15)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Get child's user_id first
    cursor.execute("SELECT user_id FROM children WHERE id = ?", (child_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return []
    
    # Handle both SQLite Row objects and Turso tuples
    user_id = result[0] if isinstance(result, (tuple, list)) else result.get('user_id')
    today = date.today().isoformat()
    
    # Get only family's custom words (user_id must match)
    # Use child_progress table for per-child successful_days tracking
    # Only include words where next_review <= today (ready for practice today)
    # For new children (no cp record), cp.next_review IS NULL so they see all words
    cursor.execute("""
    SELECT 
    w.id, 
    w.word, 
    w.category, 
    COALESCE(cp.successful_days, 0) as successful_days,
    w.user_id,
    COALESCE(cp.next_review, w.next_review) as next_review,
    w.reference_image
    FROM words w
    LEFT JOIN child_progress cp ON w.id = cp.word_id AND cp.child_id = ?
    WHERE w.user_id = ?
    AND (cp.next_review IS NULL OR cp.next_review <= ?)
    ORDER BY COALESCE(cp.successful_days, 0) ASC, w.word ASC
    """, (child_id, user_id, today))
    
    words = cursor.fetchall()
    conn.close()
    return [_convert_row_to_dict(w, ['id', 'word', 'category', 'successful_days', 'user_id', 'next_review', 'reference_image']) for w in words]

def get_user_mastery_threshold(user_id: int) -> int:
    """
    Issue #16: Get session mastery threshold for a user
    Returns the number of correct answers needed to master a word in a session
    Default is 2
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT session_mastery_threshold FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # Handle both SQLite Row objects and tuples
        threshold = result[0] if hasattr(result, '__getitem__') else result
        return threshold if threshold else 2
    return 2

def update_user_mastery_threshold(user_id: int, threshold: int) -> bool:
    """
    Issue #16: Update session mastery threshold for a user
    
    Args:
        user_id: User ID
        threshold: Number of correct answers needed (minimum 1)
    
    Returns:
        True if successful, False otherwise
    """
    if threshold < 1:
        return False
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET session_mastery_threshold = ? WHERE id = ?",
        (threshold, user_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def update_word_on_success_for_child(word_id: int, child_id: int):
    """
    Phase 13: Update word progress after successful practice for a child
    Updates child_progress table for per-child tracking
    """
    conn = get_db()
    cursor = conn.cursor()
    today = date.today().isoformat()
    
    # Verify child_id owns this word (indirectly via user_id)
    cursor.execute("""
        SELECT c.user_id FROM children c WHERE c.id = ?
    """, (child_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False
    
    # Check if child_progress record exists for this child/word
    cursor.execute("""
        SELECT successful_days, last_practiced FROM child_progress 
        WHERE child_id = ? AND word_id = ?
    """, (child_id, word_id))
    row = cursor.fetchone()
    
    if row:
        # Record exists
        current_successful_days, last_practiced = row
        
        # Only increment if not already practiced today
        if last_practiced == today:
            conn.close()
            return False
    else:
        # No record yet, create one
        current_successful_days = 0
        last_practiced = None
    
    # Increment successful_days
    new_successful_days = current_successful_days + 1
    
    # Calculate next_review
    if new_successful_days == 1:
        next_review = (date.today() + timedelta(days=2)).isoformat()
    elif new_successful_days >= 2:
        next_review = (date.today() + timedelta(days=3)).isoformat()
    else:
        next_review = (date.today() + timedelta(days=1)).isoformat()
    
    # Insert or update child_progress record
    if row:
        # Update existing record
        cursor.execute("""
            UPDATE child_progress
            SET successful_days = ?, last_practiced = ?, next_review = ?
            WHERE child_id = ? AND word_id = ?
        """, (new_successful_days, today, next_review, child_id, word_id))
    else:
        # Insert new record
        cursor.execute("""
            INSERT INTO child_progress (child_id, word_id, successful_days, last_practiced, next_review)
            VALUES (?, ?, ?, ?, ?)
        """, (child_id, word_id, new_successful_days, today, next_review))
    
    conn.commit()
    conn.close()
    return True
