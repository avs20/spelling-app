"""
Database setup and operations
SQLite database for words and practices
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = "../data/spelling.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Words table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Practices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS practices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            spelled_word TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            drawing_filename TEXT,
            practiced_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (word_id) REFERENCES words(id)
        )
    """)
    
    # Insert test words if empty
    cursor.execute("SELECT COUNT(*) FROM words")
    if cursor.fetchone()[0] == 0:
        test_words = [
            ("bee", "insects"),
            ("spider", "insects"),
            ("butterfly", "insects")
        ]
        cursor.executemany("INSERT INTO words (word, category) VALUES (?, ?)", test_words)
    
    conn.commit()
    conn.close()

def get_all_words():
    """Get all words from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, word, category FROM words")
    words = cursor.fetchall()
    conn.close()
    return [dict(word) for word in words]

def get_word_for_practice():
    """Get next word to practice (random)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, word, category FROM words ORDER BY RANDOM() LIMIT 1")
    word = cursor.fetchone()
    conn.close()
    return word

def get_word_by_id(word_id: int):
    """Get word by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT word, category FROM words WHERE id = ?", (word_id,))
    word = cursor.fetchone()
    conn.close()
    return word

def save_practice(word_id: int, spelled_word: str, is_correct: bool, drawing_filename: str):
    """Save practice record"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO practices (word_id, spelled_word, is_correct, drawing_filename)
        VALUES (?, ?, ?, ?)
    """, (word_id, spelled_word, is_correct, drawing_filename))
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
    return [dict(p) for p in practices]
