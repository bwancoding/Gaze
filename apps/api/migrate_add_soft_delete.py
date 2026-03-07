#!/usr/bin/env python3
"""
Migration Script: Add soft delete support for UserPersona
Adds is_deleted and deleted_at fields
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "wrhitw.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Adding soft delete columns to user_personas table...")
    
    # Add is_deleted column
    try:
        cursor.execute("""
            ALTER TABLE user_personas ADD COLUMN is_deleted INTEGER DEFAULT 0
        """)
        print("  ✓ Added is_deleted column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("  ⚠ is_deleted column already exists")
        else:
            raise
    
    # Add deleted_at column
    try:
        cursor.execute("""
            ALTER TABLE user_personas ADD COLUMN deleted_at TIMESTAMP
        """)
        print("  ✓ Added deleted_at column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("  ⚠ deleted_at column already exists")
        else:
            raise
    
    # Add index for performance
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_personas_deleted 
            ON user_personas(is_deleted, deleted_at)
        """)
        print("  ✓ Created index on is_deleted")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print("  ⚠ Index already exists")
        else:
            raise
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("\nNext steps:")
    print("1. Restart the backend server")
    print("2. Test persona deletion (should now be soft delete)")
    print("3. Verify comments still show for deleted personas")

if __name__ == "__main__":
    migrate()
