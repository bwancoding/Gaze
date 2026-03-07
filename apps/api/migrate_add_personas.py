#!/usr/bin/env python3
"""
Migration Script: Add user persona system
Creates tables for user personas and event-level stakeholder verifications
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "wrhitw.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating persona tables...")
    
    # 1. User Personas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_personas (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
            persona_name TEXT NOT NULL,
            avatar_color TEXT DEFAULT 'blue',
            is_verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ user_personas")
    
    # 2. Event-Stakeholder Verifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_stakeholder_verifications (
            id TEXT PRIMARY KEY,
            user_persona_id TEXT REFERENCES user_personas(id) ON DELETE CASCADE,
            event_id TEXT REFERENCES events(id) ON DELETE CASCADE,
            stakeholder_id TEXT REFERENCES stakeholders(id),
            application_text TEXT,
            proof_type TEXT,
            proof_data TEXT,
            status TEXT DEFAULT 'pending',
            reviewed_by TEXT REFERENCES users(id),
            reviewed_at TIMESTAMP,
            review_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_persona_id, event_id)
        )
    """)
    print("  ✓ event_stakeholder_verifications")
    
    # 3. Add user_persona_id to comments table (optional - comments table may not exist yet)
    try:
        cursor.execute("""
            ALTER TABLE comments ADD COLUMN user_persona_id TEXT REFERENCES user_personas(id) ON DELETE SET NULL
        """)
        print("  ✓ comments.user_persona_id")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("  ⚠ comments.user_persona_id already exists")
        elif "no such table" in str(e).lower():
            print("  ⚠ comments table doesn't exist yet (will be added later)")
        else:
            raise
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("\nNext steps:")
    print("1. Restart the backend server")
    print("2. Create user personas via API")
    print("3. Test event-level verification flow")

if __name__ == "__main__":
    migrate()
