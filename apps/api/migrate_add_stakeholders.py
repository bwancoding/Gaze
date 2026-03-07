#!/usr/bin/env python3
"""
Migration Script: Add stakeholder recognition system
Creates tables for stakeholder types, stakeholders, verifications, and user roles
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "wrhitw.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating stakeholder tables...")
    
    # 1. Stakeholder Types
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stakeholder_types (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            category TEXT,
            verification_required INTEGER DEFAULT 1,
            verification_method TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ stakeholder_types")
    
    # 2. Stakeholders
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stakeholders (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type_id TEXT REFERENCES stakeholder_types(id),
            description TEXT,
            category TEXT,
            verification_required INTEGER DEFAULT 1,
            verification_method TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ stakeholders")
    
    # 3. Event-Stakeholder Links
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_stakeholders (
            id TEXT PRIMARY KEY,
            event_id TEXT REFERENCES events(id) ON DELETE CASCADE,
            stakeholder_id TEXT REFERENCES stakeholders(id),
            relevance_score REAL DEFAULT 0.5,
            status TEXT DEFAULT 'pending',
            approved_at TIMESTAMP,
            approved_by TEXT REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(event_id, stakeholder_id)
        )
    """)
    print("  ✓ event_stakeholders")
    
    # 4. Stakeholder Verifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stakeholder_verifications (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
            stakeholder_id TEXT REFERENCES stakeholders(id),
            event_id TEXT REFERENCES events(id) ON DELETE CASCADE,
            application_text TEXT,
            proof_type TEXT,
            proof_data TEXT,
            status TEXT DEFAULT 'pending',
            reviewed_by TEXT REFERENCES users(id),
            reviewed_at TIMESTAMP,
            review_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ stakeholder_verifications")
    
    # 5. User-Stakeholder Roles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stakeholder_roles (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
            stakeholder_id TEXT REFERENCES stakeholders(id),
            is_verified INTEGER DEFAULT 0,
            verified_at TIMESTAMP,
            display_name TEXT,
            badge_color TEXT DEFAULT 'blue',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, stakeholder_id)
        )
    """)
    print("  ✓ user_stakeholder_roles")
    
    # Insert default stakeholder types
    print("\nInserting default stakeholder types...")
    
    default_types = [
        ('Country', 'Countries/Nations', 'geopolitics', 1, 'IP address, Government email'),
        ('Military', 'Military personnel', 'geopolitics', 1, 'Military email (.mil), ID document'),
        ('Organization', 'International organizations', 'geopolitics', 1, 'Official email, Document'),
        ('Group', 'Civilian groups', 'geopolitics', 0, 'IP address, Self-declaration'),
        ('Company', 'Companies/Corporations', 'technology', 1, 'Company email'),
        ('Expert', 'Domain experts', 'all', 1, 'Academic/Work credentials'),
    ]
    
    import uuid
    from datetime import datetime
    
    for name, desc, category, verify_required, verify_method in default_types:
        type_id = str(uuid.uuid4())
        try:
            cursor.execute("""
                INSERT INTO stakeholder_types (id, name, description, category, verification_required, verification_method)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (type_id, name, desc, category, verify_required, verify_method))
            print(f"  ✓ Created type: {name}")
        except sqlite3.IntegrityError:
            print(f"  ⚠ Type already exists: {name}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("\nNext steps:")
    print("1. Restart the backend server")
    print("2. Create stakeholders via admin API")
    print("3. Test verification flow")

if __name__ == "__main__":
    migrate()
