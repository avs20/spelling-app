"""
Database migration system for schema updates
Handles version tracking and incremental schema changes
"""

import sqlite3
from datetime import date
import os
from database import get_db, DB_PATH

# Define migrations in order
MIGRATIONS = {
    1: {
        "name": "initial_schema",
        "description": "Create initial tables: users, children, words, practices",
        "up": """
            -- Users table - Parent/teacher accounts
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Children table - Child profiles linked to users
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                age INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            
            -- Words table - Words to practice
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
            );
            
            -- Practices table - Practice records
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
            );
        """
    }
}

def create_migrations_table():
    """Create migrations tracking table"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_applied_migrations():
    """Get list of applied migrations"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM schema_migrations ORDER BY id")
    migrations = cursor.fetchall()
    conn.close()
    return {m[0]: m[1] for m in migrations}

def apply_migration(migration_id: int, migration: dict) -> bool:
    """Apply a single migration"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Execute migration SQL
        cursor.executescript(migration["up"])
        
        # Track migration
        cursor.execute(
            "INSERT INTO schema_migrations (id, name, description) VALUES (?, ?, ?)",
            (migration_id, migration["name"], migration["description"])
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Migration {migration_id} failed: {e}")
        return False

def migrate_to_latest():
    """Apply all pending migrations"""
    create_migrations_table()
    
    applied = get_applied_migrations()
    pending = [mid for mid in sorted(MIGRATIONS.keys()) if mid not in applied]
    
    if not pending:
        print("✓ Database is up to date")
        return True
    
    print(f"Found {len(pending)} pending migration(s)")
    
    for migration_id in pending:
        migration = MIGRATIONS[migration_id]
        print(f"Applying migration {migration_id}: {migration['name']}")
        
        if not apply_migration(migration_id, migration):
            return False
        
        print(f"✓ Migration {migration_id} applied")
    
    print(f"✓ All {len(pending)} migration(s) applied successfully")
    return True

def get_migration_status():
    """Get current migration status"""
    create_migrations_table()
    applied = get_applied_migrations()
    
    print("\n=== Database Migration Status ===\n")
    
    for mid in sorted(MIGRATIONS.keys()):
        status = "✓ Applied" if mid in applied else "✗ Pending"
        migration = MIGRATIONS[mid]
        print(f"{status} | Migration {mid}: {migration['name']}")
        print(f"       {migration['description']}\n")
    
    applied_count = len(applied)
    total_count = len(MIGRATIONS)
    print(f"Progress: {applied_count}/{total_count} migrations applied")
    
    return applied_count == total_count

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            get_migration_status()
        elif sys.argv[1] == "migrate":
            migrate_to_latest()
    else:
        migrate_to_latest()
