"""
WRHITW Event API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
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
    force: bool = Query(False, description="Force regeneration of cached summary"),
    db: Session = Depends(get_db),
):
    """
    Get AI multi-perspective summary for an event.

    Auto-generates if no cached summary exists or if it has expired.
    Use ?force=true to regenerate even if a valid cache exists.

    - **event_id**: Event ID
    - **force**: Force regeneration
    """
    from app.services.ai_service import get_cached_summary, generate_and_cache_summary

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Try cache first (unless force)
    if not force:
        cached = get_cached_summary(db, event_id)
        if cached:
            return cached

    # Auto-generate
    try:
        result = await generate_and_cache_summary(db, event_id, force=force)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{event_id}/analysis")
async def get_event_analysis(
    event_id: str,
    force: bool = Query(False, description="Force regeneration"),
    db: Session = Depends(get_db),
):
    """
    Get stakeholder-based deep analysis for an event.
    Auto-generates if no cached analysis exists.
    """
    from app.services.event_analysis_service import get_cached_analysis, generate_event_analysis

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if not force:
        cached = get_cached_analysis(db, event_id)
        if cached:
            return cached

    try:
        result = await generate_event_analysis(db, event_id, force=force)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{event_id}/stakeholders")
async def get_event_stakeholders(
    event_id: str,
    db: Session = Depends(get_db),
):
    """Get stakeholders and their perspectives for an event."""
    from app.models.stakeholders import EventStakeholder, Stakeholder

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    results = (
        db.query(EventStakeholder, Stakeholder)
        .join(Stakeholder, EventStakeholder.stakeholder_id == Stakeholder.id)
        .filter(EventStakeholder.event_id == event_id)
        .all()
    )

    return [
        {
            "id": str(es.id),
            "stakeholder_id": str(es.stakeholder_id),
            "stakeholder_name": s.name,
            "perspective_summary": es.perspective_summary,
            "key_concerns": es.key_concerns or [],
            "relevance_score": float(es.relevance_score) if es.relevance_score else None,
            "is_ai_generated": es.is_ai_generated,
            "status": es.status,
        }
        for es, s in results
    ]


@router.post("/{event_id}/summary/feedback")
async def submit_summary_feedback(
    event_id: str,
    helpful: bool = Body(..., embed=True, description="Was the summary helpful?"),
    perspective: Optional[str] = Body(None, embed=True, description="Which perspective (left/center/right)?"),
    db: Session = Depends(get_db),
):
    """
    Submit feedback on an AI summary.

    - **helpful**: Was the summary helpful? (true/false)
    - **perspective**: Optional — which perspective the feedback is about
    """
    summary = db.query(AiSummary).filter(AiSummary.event_id == event_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="No summary found for this event")

    # Adjust quality score based on feedback (simple moving average)
    current_score = float(summary.quality_score) if summary.quality_score else 0.5
    feedback_value = 1.0 if helpful else 0.0
    # Weighted: 90% existing score, 10% new feedback
    summary.quality_score = round(current_score * 0.9 + feedback_value * 0.1, 4)
    db.commit()

    return {
        "message": "Feedback recorded",
        "updated_quality_score": float(summary.quality_score),
    }
