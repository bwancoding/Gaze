#!/usr/bin/env python3
"""
Create sample events for testing
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models import Event

# Sample international events
SAMPLE_EVENTS = [
    {
        "title": "US Federal Reserve Maintains Interest Rates Amid Inflation Concerns",
        "summary": "The Federal Reserve announced today it will maintain interest rates at current levels as inflation shows signs of cooling.",
        "category": "Economy",
        "hot_score": 95.5,
    },
    {
        "title": "EU Parliament Passes Landmark AI Regulation Act",
        "summary": "European Union lawmakers approved comprehensive AI regulation with strict requirements for high-risk systems.",
        "category": "Technology",
        "hot_score": 88.3,
    },
    {
        "title": "Middle East Peace Talks Resume in Geneva",
        "summary": "International mediators bring together regional leaders for renewed peace negotiations.",
        "category": "Politics",
        "hot_score": 92.1,
    },
    {
        "title": "SpaceX Successfully Launches New Satellite Constellation",
        "summary": "Private space company achieves another milestone with successful deployment of communication satellites.",
        "category": "Technology",
        "hot_score": 85.7,
    },
    {
        "title": "Global Climate Summit Reaches Agreement on Carbon Reduction",
        "summary": "Nearly 200 countries commit to accelerated carbon reduction targets at international climate conference.",
        "category": "Environment",
        "hot_score": 91.2,
    },
]

def create_sample_events():
    db = SessionLocal()
    
    try:
        for event_data in SAMPLE_EVENTS:
            # Check if already exists
            existing = db.query(Event).filter(Event.title == event_data["title"]).first()
            if existing:
                print(f"⚠ Event already exists: {event_data['title'][:50]}...")
                continue
            
            event = Event(
                title=event_data["title"],
                summary=event_data["summary"],
                category=event_data["category"],
                hot_score=event_data["hot_score"],
                status="active",
                source_count=3,
                view_count=0,
                occurred_at=datetime.utcnow() - timedelta(days=1),
            )
            
            db.add(event)
            db.commit()
            print(f"✓ Created: {event_data['title'][:50]}...")
        
        print("\n✅ Sample events created successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_events()
