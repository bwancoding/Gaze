#!/usr/bin/env python3
"""
Migration: Add topic_engagement_score column to trending_events table.

This column stores the accumulated demand-side signal (Reddit upvotes +
HN points + Bluesky likes/reposts + comment counts) from topic seeds.
It is read by HeatCalculator.calculate_event_heat as a first-class term
alongside media_count, so highly-upvoted entertainment/gaming/sports
stories are no longer crushed by multi-outlet hard-news stories.

Supports both SQLite (local) and PostgreSQL (Railway). Safe to run
multiple times.
"""
from sqlalchemy import text
from app.core.database import engine, DATABASE_URL


def migrate():
    is_sqlite = DATABASE_URL.startswith("sqlite")
    with engine.begin() as conn:
        if is_sqlite:
            cols = conn.execute(text("PRAGMA table_info(trending_events)")).fetchall()
            col_names = {row[1] for row in cols}
            if "topic_engagement_score" in col_names:
                print("⚠ topic_engagement_score already exists (sqlite)")
                return
            conn.execute(text(
                "ALTER TABLE trending_events ADD COLUMN topic_engagement_score FLOAT DEFAULT 0.0"
            ))
            print("✓ Added topic_engagement_score column (sqlite)")
        else:
            conn.execute(text(
                "ALTER TABLE trending_events ADD COLUMN IF NOT EXISTS topic_engagement_score DOUBLE PRECISION DEFAULT 0.0"
            ))
            print("✓ Added topic_engagement_score column (postgres)")


if __name__ == "__main__":
    migrate()
    print("✅ Migration completed!")
