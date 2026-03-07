"""
WRHITW Event API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models import Event, EventSource, Source, AiSummary
from app.schemas import EventResponse, EventListResponse, EventCreate, EventUpdate

router = APIRouter()


@router.get("", response_model=EventListResponse)
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = Query("active", regex="^(active|archived|closed|all)$"),
    sort_by: str = Query("hot_score", regex="^(hot_score|created_at|view_count)$"),
    db: Session = Depends(get_db),
):
    """
    Get event list
    
    - **page**: Page number
    - **page_size**: Items per page
    - **category**: Filter by category
    - **status**: Filter by status (active, archived, closed, all)
    - **sort_by**: Sort field (hot_score, created_at, view_count)
    """
    # Base query
    if status == "all":
        query = db.query(Event)
    else:
        query = db.query(Event).filter(Event.status == status)
    
    # Category filter
    if category:
        query = query.filter(Event.category == category)
    
    # Total count
    total = query.count()
    
    # Sorting
    if sort_by == "hot_score":
        query = query.order_by(Event.hot_score.desc())
    elif sort_by == "created_at":
        query = query.order_by(Event.created_at.desc())
    elif sort_by == "view_count":
        query = query.order_by(Event.view_count.desc())
    
    # Pagination
    offset = (page - 1) * page_size
    events = query.offset(offset).limit(page_size).all()
    
    return EventListResponse(
        items=events,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    Get event details
    
    - **event_id**: Event ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Increment view count
    event.view_count += 1
    db.commit()
    
    return event


@router.post("", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
):
    """
    Create new event
    
    - **title**: Event title
    - **summary**: Event summary
    - **category**: Category
    - **tags**: Tags
    """
    import json
    data = event_data.model_dump()
    
    # Serialize tags to JSON for SQLite
    if 'tags' in data and isinstance(data['tags'], list):
        data['tags'] = json.dumps(data['tags'])
    
    event = Event(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
):
    """
    Update event
    
    - **event_id**: Event ID
    """
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


@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete event (soft delete - archive)
    
    - **event_id**: Event ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Soft delete - set to archived
    event.status = 'archived'
    event.archived_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Event archived"}


@router.post("/{event_id}/archive")
async def archive_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    Archive event
    
    - **event_id**: Event ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = 'archived'
    event.archived_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Event archived"}


@router.post("/{event_id}/close")
async def close_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    Close event (no new comments allowed)
    
    - **event_id**: Event ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = 'closed'
    event.closed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Event closed"}


@router.get("/{event_id}/sources")
async def get_event_sources(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    Get all sources for an event
    
    - **event_id**: Event ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    sources = db.query(EventSource, Source).join(
        Source, EventSource.source_id == Source.id
    ).filter(EventSource.event_id == event_id).all()
    
    return [
        {
            "id": es.id,
            "source": {
                "id": s.id,
                "name": s.name,
                "bias_label": s.bias_label,
                "bias_score": float(s.bias_score) if s.bias_score else None,
            },
            "article_title": es.article_title,
            "article_url": es.article_url,
            "published_at": es.published_at,
        }
        for es, s in sources
    ]


@router.get("/{event_id}/summary")
async def get_event_summary(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    Get AI multi-perspective summary for an event
    
    - **event_id**: Event ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    summary = db.query(AiSummary).filter(AiSummary.event_id == event_id).first()
    
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not generated yet")
    
    return {
        "event_id": str(summary.event_id),
        "left_perspective": {
            "summary": summary.left_perspective,
            "sources": summary.left_sources or []
        },
        "center_perspective": {
            "summary": summary.center_perspective,
            "sources": summary.center_sources or []
        },
        "right_perspective": {
            "summary": summary.right_perspective,
            "sources": summary.right_sources or []
        },
        "generated_at": summary.generated_at,
    }
