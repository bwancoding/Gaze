#!/usr/bin/env python3
"""
Migration: Add timeline_data column to trending_events table.

Supports both SQLite (local) and PostgreSQL (Railway). Safe to run multiple times.
"""
from sqlalchemy import text
from app.core.database import engine, DATABASE_URL


def migrate():
    is_sqlite = DATABASE_URL.startswith("sqlite")
    with engine.begin() as conn:
        if is_sqlite:
            # SQLite: check column existence via PRAGMA
            cols = conn.execute(text("PRAGMA table_info(trending_events)")).fetchall()
            col_names = {row[1] for row in cols}
            if "timeline_data" in col_names:
                print("⚠ timeline_data already exists (sqlite)")
                return
            conn.execute(text("ALTER TABLE trending_events ADD COLUMN timeline_data TEXT DEFAULT '[]'"))
            print("✓ Added timeline_data column (sqlite)")
        else:
            # PostgreSQL: use IF NOT EXISTS
            conn.execute(text(
                "ALTER TABLE trending_events ADD COLUMN IF NOT EXISTS timeline_data JSONB DEFAULT '[]'::jsonb"
            ))
            print("✓ Added timeline_data column (postgres)")


if __name__ == "__main__":
    migrate()
    print("✅ Migration completed!")
