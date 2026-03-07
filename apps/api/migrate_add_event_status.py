#!/usr/bin/env python3
"""
Migration Script: Add event status fields
Adds archived_at and closed_at columns to events table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "wrhitw.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Add archived_at column
    try:
        cursor.execute("ALTER TABLE events ADD COLUMN archived_at TIMESTAMP")
        print("✓ Added archived_at column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("⚠ archived_at column already exists")
        else:
            raise
    
    # Add closed_at column
    try:
        cursor.execute("ALTER TABLE events ADD COLUMN closed_at TIMESTAMP")
        print("✓ Added closed_at column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("⚠ closed_at column already exists")
        else:
            raise
    
    # Update existing events to have status='active'
    cursor.execute("UPDATE events SET status='active' WHERE status IS NULL")
    print("✓ Updated existing events status")
    
    conn.commit()
    conn.close()
    print("✅ Migration completed!")

if __name__ == "__main__":
    migrate()
