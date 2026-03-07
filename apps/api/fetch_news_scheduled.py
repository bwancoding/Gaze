#!/usr/bin/env python3
"""
WRHITW News Fetcher - Scheduled Task
Runs every 4 hours to fetch news from RSS feeds

Usage:
    python fetch_news_scheduled.py

Cron Setup:
    crontab -e
    0 */4 * * * cd /path/to/wrhitw/apps/api && ./venv/bin/python fetch_news_scheduled.py >> /tmp/wrhitw_fetcher.log 2>&1
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal, engine
from app.models import Event, Source, EventSource
import feedparser
import hashlib

# International news sources (English)
NEWS_SOURCES = [
    {
        "name": "Reuters World",
        "url": "https://feeds.reuters.com/reuters/worldNews",
        "category": "Politics",
        "bias_label": "center"
    },
    {
        "name": "AP News",
        "url": "https://apnews.com/apf-internationalnews",
        "category": "Politics",
        "bias_label": "center"
    },
    {
        "name": "BBC World",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "Politics",
        "bias_label": "center-left"
    },
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "category": "Technology",
        "bias_label": "center"
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "category": "Technology",
        "bias_label": "center-left"
    },
    {
        "name": "Bloomberg",
        "url": "https://www.bloomberg.com/feed/podcast/etf.xml",
        "category": "Economy",
        "bias_label": "center"
    },
]

LOG_FILE = Path('/tmp/wrhitw_fetcher.log')

def log(message: str):
    """Log message to file and stdout"""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_line + '\n')
    except:
        pass

def generate_event_id(title: str) -> str:
    """Generate unique event ID from title"""
    return hashlib.md5(title.encode()).hexdigest()

def fetch_rss_feed(source_url: str, source_name: str):
    """Fetch and parse RSS feed"""
    log(f"Fetching {source_name}...")
    
    try:
        feed = feedparser.parse(source_url)
        entries = feed.entries if hasattr(feed, 'entries') else []
        log(f"  Retrieved {len(entries)} entries from {source_name}")
        return entries
    except Exception as e:
        log(f"  ✗ Error fetching {source_name}: {e}")
        return []

def save_to_database(entries, source_name: str, category: str, bias_label: str, db: SessionLocal):
    """Save entries to database"""
    saved_count = 0
    updated_count = 0
    
    for entry in entries[:15]:  # Limit to 15 per source
        try:
            title = entry.title if hasattr(entry, 'title') else ''
            summary = entry.get('summary', '')[:500] if hasattr(entry, 'get') else ''
            link = entry.link if hasattr(entry, 'link') else ''
            published = entry.get('published_parsed') if hasattr(entry, 'get') else None
            
            if not title:
                continue
            
            if published:
                published_at = datetime(*published[:6], tzinfo=timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)
            
            # Check if event already exists
            event = db.query(Event).filter(Event.title == title).first()
            
            if not event:
                # Create new event
                event = Event(
                    title=title,
                    summary=summary[:200],  # Short summary for list
                    description=summary,
                    category=category,
                    status='active',
                    hot_score=50.0,  # Default score
                    source_count=1,
                    occurred_at=published_at,
                )
                db.add(event)
                db.commit()
                db.refresh(event)
                log(f"  ✓ Created: {title[:60]}...")
                saved_count += 1
            else:
                # Update existing event
                event.source_count += 1
                event.updated_at = datetime.now(timezone.utc)
                db.commit()
                log(f"  ~ Updated: {title[:60]}...")
                updated_count += 1
            
        except Exception as e:
            log(f"  ✗ Error saving entry: {e}")
            db.rollback()
            continue
    
    return saved_count, updated_count

def main():
    """Main function"""
    log("=" * 60)
    log("WRHITW News Fetcher - Scheduled Task Started")
    log("=" * 60)
    
    db = SessionLocal()
    total_saved = 0
    total_updated = 0
    
    try:
        for source in NEWS_SOURCES:
            entries = fetch_rss_feed(source["url"], source["name"])
            
            if entries:
                saved, updated = save_to_database(
                    entries,
                    source["name"],
                    source["category"],
                    source["bias_label"],
                    db
                )
                total_saved += saved
                total_updated += updated
                log(f"  → {source['name']}: {saved} saved, {updated} updated")
        
        log("=" * 60)
        log(f"Summary: {total_saved} new events, {total_updated} updated events")
        log(f"Completed at: {datetime.now(timezone.utc).isoformat()}")
        log("=" * 60)
        
    except Exception as e:
        log(f"✗ Fatal error: {e}")
        db.rollback()
    finally:
        db.close()
    
    return total_saved, total_updated

if __name__ == "__main__":
    main()
