"""
Admin API Routes
Management backend for event administration
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import secrets

from app.core.database import get_db
from app.models import Event
from app.models.trending import TrendingEvent
from app.schemas import EventResponse, EventCreate, EventUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])

# Simple HTTP Basic Auth
security = HTTPBasic()

# Admin credentials (required from environment)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise RuntimeError(
        "ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required."
    )


def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin username and password"""
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username


@router.get("/events")
async def admin_list_events(
    status_filter: Optional[str] = "all",
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """
    List all events (admin view)
    
    - **status_filter**: Filter by status (all, active, archived, closed)
    - **category**: Filter by category
    - **page**: Page number
    - **page_size**: Items per page
    """
    # Base query
    if status_filter and status_filter != "all":
        query = db.query(Event).filter(Event.status == status_filter)
    else:
        query = db.query(Event)
    
    # Category filter
    if category:
        query = query.filter(Event.category == category)
    
    # Total count
    total = query.count()
    
    # Sorting (newest first)
    query = query.order_by(Event.created_at.desc())
    
    # Pagination
    offset = (page - 1) * page_size
    events = query.offset(offset).limit(page_size).all()
    
    return {
        "items": events,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/events/{event_id}")
async def admin_get_event(
    event_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Get event details (admin view)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event


@router.post("/events")
async def admin_create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """
    Create new event (admin)
    
    - **title**: Event title
    - **summary**: Event summary
    - **category**: Category (Environment, Economy, Technology, Politics)
    - **tags**: Tags
    """
    import json
    
    data = event_data.model_dump()
    
    # Serialize tags for SQLite
    if 'tags' in data and isinstance(data['tags'], list):
        data['tags'] = json.dumps(data['tags'])
    
    # Set default values
    data['status'] = 'active'
    data['hot_score'] = 50.0
    data['source_count'] = 1  # Manually created
    
    event = Event(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event


@router.put("/events/{event_id}")
async def admin_update_event(
    event_id: str,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Update event (admin)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update fields
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return event


@router.post("/events/{event_id}/archive")
async def admin_archive_event(
    event_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Archive event (admin)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = 'archived'
    event.archived_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Event archived", "event_id": str(event_id)}


@router.post("/events/{event_id}/close")
async def admin_close_event(
    event_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Close event (admin) - no new comments allowed"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = 'closed'
    event.closed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Event closed", "event_id": str(event_id)}


@router.delete("/events/{event_id}")
async def admin_delete_event(
    event_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Permanently delete event (admin) - use with caution!"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event permanently deleted", "event_id": str(event_id)}


@router.get("/candidates")
async def admin_list_candidates(
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """List candidate events awaiting review."""
    query = db.query(Event).filter(Event.status == 'candidate')
    total = query.count()
    query = query.order_by(Event.created_at.desc())
    offset = (page - 1) * page_size
    events = query.offset(offset).limit(page_size).all()

    return {
        "items": events,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/events/{event_id}/publish")
async def admin_publish_event(
    event_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Publish a candidate event (candidate → active). Auto-triggers AI stakeholder analysis."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status not in ('candidate', 'archived'):
        raise HTTPException(status_code=400, detail=f"Cannot publish event with status '{event.status}'")

    event.status = 'active'
    db.commit()

    # Auto-generate stakeholder analysis in the background
    background_tasks.add_task(_generate_analysis_background, str(event_id))

    return {"message": "Event published, stakeholder analysis queued", "event_id": str(event_id)}


def _generate_analysis_background(event_id: str):
    """Background task: generate AI stakeholder analysis for an event."""
    import asyncio
    from app.core.database import SessionLocal
    from app.services.event_analysis_service import generate_event_analysis

    db = SessionLocal()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generate_event_analysis(db, event_id, force=True))
        print(f"[Auto-Analysis] Generated for event {event_id}: {result.get('stakeholder_count', 0)} stakeholders")
    except Exception as e:
        print(f"[Auto-Analysis] Failed for event {event_id}: {e}")
    finally:
        db.close()
        loop.close()


@router.post("/events/{event_id}/reject")
async def admin_reject_event(
    event_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Reject a candidate event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.status = 'closed'
    event.closed_at = datetime.utcnow()
    db.commit()

    return {"message": "Event rejected", "event_id": str(event_id)}


@router.post("/events/{event_id}/generate-analysis")
async def admin_generate_analysis(
    event_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Trigger AI analysis generation for an event (admin)."""
    from app.services.event_analysis_service import generate_event_analysis

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        result = await generate_event_analysis(db, event_id, force=True)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/trending/{trending_id}/promote")
async def admin_promote_trending(
    trending_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Promote a trending event to a candidate event."""
    import json

    trending = db.query(TrendingEvent).filter(TrendingEvent.id == trending_id).first()
    if not trending:
        raise HTTPException(status_code=404, detail="Trending event not found")

    if trending.status == 'promoted':
        raise HTTPException(status_code=400, detail="Already promoted")

    # Create candidate event from trending
    event = Event(
        title=trending.title,
        summary=trending.summary,
        category=trending.category,
        status='candidate',
        source_count=trending.article_count,
        trending_origin_id=trending.id,
        tags=json.dumps(trending.keywords) if trending.keywords else None,
    )
    db.add(event)

    trending.status = 'promoted'
    db.commit()
    db.refresh(event)

    return {
        "message": "Trending event promoted to candidate",
        "event_id": str(event.id),
        "trending_id": trending_id,
    }


@router.get("/stats")
async def admin_get_stats(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Get admin statistics"""
    total_events = db.query(Event).count()
    active_events = db.query(Event).filter(Event.status == 'active').count()
    candidate_events = db.query(Event).filter(Event.status == 'candidate').count()
    archived_events = db.query(Event).filter(Event.status == 'archived').count()
    closed_events = db.query(Event).filter(Event.status == 'closed').count()
    pending_trending = db.query(TrendingEvent).filter(TrendingEvent.status == 'raw').count()

    return {
        "total_events": total_events,
        "active_events": active_events,
        "candidate_events": candidate_events,
        "archived_events": archived_events,
        "closed_events": closed_events,
        "pending_trending": pending_trending,
    }
