"""
Admin API Routes
Management backend for event administration
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import secrets
import logging

logger = logging.getLogger(__name__)

from sqlalchemy import text as sql_text

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
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """
    List all events (admin view)

    - **status_filter**: Filter by status (all, active, archived, closed)
    - **category**: Filter by category
    - **search**: Search by title
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

    # Search filter
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))
    
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


@router.delete("/events/{event_id}/analysis")
async def admin_clear_event_analysis(
    event_id: str,
    regenerate: bool = Query(True, description="Auto-regenerate analysis in background after clearing"),
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Clear all AI-generated analysis and stakeholders for an event, then regenerate."""
    from app.models.stakeholders import EventStakeholder
    from app.models.event_analysis import EventAnalysis

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Delete EventStakeholder records
    es_deleted = db.query(EventStakeholder).filter(
        EventStakeholder.event_id == event_id
    ).delete(synchronize_session='fetch')

    # Delete EventAnalysis cache
    ea_deleted = db.query(EventAnalysis).filter(
        EventAnalysis.event_id == event_id
    ).delete(synchronize_session='fetch')

    # Clear inline fields on Event
    event.background = None
    event.cause_chain = None
    event.impact_analysis = None
    event.timeline_data = None
    event.stakeholder_perspectives = None

    db.commit()

    # Auto-regenerate in background
    if regenerate:
        _schedule_analysis(_generate_analysis_background(event_id))

    return {
        "event_id": event_id,
        "stakeholders_deleted": es_deleted,
        "analysis_deleted": ea_deleted,
        "regenerating": regenerate,
        "message": "Analysis cleared and regeneration started in background." if regenerate else "Analysis cleared.",
    }


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
    event.published_at = datetime.utcnow()
    event.last_activity_at = datetime.utcnow()
    db.commit()

    # Auto-generate stakeholder analysis in the background
    background_tasks.add_task(_generate_analysis_background, str(event_id))

    # Auto-seed threads/comments so the event isn't empty
    background_tasks.add_task(_seed_interactions_background, str(event_id))

    return {"message": "Event published, analysis + seed interactions queued", "event_id": str(event_id)}


async def _generate_analysis_background(event_id: str):
    """Background task: generate AI stakeholder analysis for an event."""
    from app.core.database import SessionLocal
    from app.services.event_analysis_service import generate_event_analysis

    db = SessionLocal()
    try:
        result = await generate_event_analysis(db, event_id, force=True)
        logger.info(f"[Auto-Analysis] Generated for event {event_id}")
    except Exception as e:
        import traceback
        logger.error(f"[Auto-Analysis] Failed for event {event_id}: {e}\n{traceback.format_exc()}")
    finally:
        db.close()


async def _seed_interactions_background(event_id: str):
    """Background task: auto-seed threads/comments for a newly published event."""
    from app.core.database import SessionLocal
    from app.services.seed_interactions import seed_event_interactions

    db = SessionLocal()
    try:
        result = await seed_event_interactions(db, event_id)
        logger.info(f"[Auto-Seed] {result.get('status')} for event {event_id}: "
                     f"{result.get('threads_created', 0)} threads, {result.get('comments_created', 0)} comments")
    except Exception as e:
        import traceback
        logger.error(f"[Auto-Seed] Failed for event {event_id}: {e}\n{traceback.format_exc()}")
    finally:
        db.close()


# Keep references to background tasks so they don't get garbage collected
_background_tasks: set = set()


def _schedule_analysis(coro):
    """Schedule an async task and keep a reference to prevent GC."""
    import asyncio
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


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
    """Trigger AI analysis generation for an event (admin). Runs in background."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    _schedule_analysis(_generate_analysis_background(event_id))
    return {"message": "Analysis generation started in background", "event_id": event_id}


@router.post("/events/backfill-analysis")
async def admin_backfill_analysis(
    limit: int = Query(10, ge=1, le=50, description="Max events to retry per call"),
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Find active events without a completed analysis and retry them synchronously.

    Picks events where EventAnalysis is missing, status='failed', or stuck in
    'pending' for more than 10 minutes. Skips rows that have exceeded the max
    attempt count so permanently-broken events don't hammer the LLM forever.
    """
    from datetime import timedelta
    from sqlalchemy import or_, and_
    from app.models.event_analysis import EventAnalysis
    from app.services.event_analysis_service import generate_event_analysis

    cutoff_pending = datetime.utcnow() - timedelta(minutes=10)
    max_attempts = 5

    events = (
        db.query(Event)
        .outerjoin(EventAnalysis, EventAnalysis.event_id == Event.id)
        .filter(Event.status == 'active')
        .filter(or_(
            EventAnalysis.id == None,  # noqa: E711
            EventAnalysis.status == 'failed',
            and_(
                EventAnalysis.status == 'pending',
                or_(
                    EventAnalysis.last_attempt_at == None,  # noqa: E711
                    EventAnalysis.last_attempt_at < cutoff_pending,
                ),
            ),
        ))
        .filter(or_(
            EventAnalysis.attempt_count == None,  # noqa: E711
            EventAnalysis.attempt_count < max_attempts,
        ))
        .order_by(Event.last_activity_at.desc().nullslast())
        .limit(limit)
        .all()
    )

    succeeded = 0
    failed = 0
    errors: List[dict] = []
    for event in events:
        try:
            await generate_event_analysis(db, str(event.id), force=True)
            succeeded += 1
            logger.info(f"[Backfill] Generated analysis for event {event.id}")
        except Exception as e:
            failed += 1
            errors.append({"event_id": str(event.id), "error": str(e)[:200]})
            logger.error(f"[Backfill] Failed for event {event.id}: {e}")

    return {
        "status": "success",
        "candidates": len(events),
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors,
    }


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
        hot_score=trending.heat_score or 0,
        trending_origin_id=trending.id,
        tags=trending.keywords if isinstance(trending.keywords, list) else None,
    )
    db.add(event)

    trending.status = 'promoted'
    db.commit()
    db.refresh(event)

    # Trigger AI analysis in background (non-blocking)
    _schedule_analysis(_generate_analysis_background(str(event.id)))

    return {
        "message": "Trending event promoted to candidate (AI analysis generating in background)",
        "event_id": str(event.id),
        "trending_id": trending_id,
    }


@router.post("/trending/{trending_id}/reject")
async def admin_reject_trending(
    trending_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Reject a trending event (dismiss from admin review)."""
    trending = db.query(TrendingEvent).filter(TrendingEvent.id == trending_id).first()
    if not trending:
        raise HTTPException(status_code=404, detail="Trending event not found")

    if trending.status != 'raw':
        raise HTTPException(status_code=400, detail=f"Cannot reject trending with status '{trending.status}'")

    trending.status = 'rejected'
    db.commit()

    return {"message": "Trending event rejected", "trending_id": trending_id}


@router.post("/trending/batch-promote")
async def admin_batch_promote(
    trending_ids: List[int],
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Batch promote multiple trending events to candidates."""
    import json

    promoted = []
    errors = []

    for tid in trending_ids:
        trending = db.query(TrendingEvent).filter(TrendingEvent.id == tid).first()
        if not trending:
            errors.append({"id": tid, "error": "Not found"})
            continue
        if trending.status != 'raw':
            errors.append({"id": tid, "error": f"Status is '{trending.status}'"})
            continue

        event = Event(
            title=trending.title,
            summary=trending.summary,
            category=trending.category,
            status='candidate',
            source_count=trending.article_count,
            hot_score=trending.heat_score or 0,
            trending_origin_id=trending.id,
            tags=trending.keywords if isinstance(trending.keywords, list) else None,
        )
        db.add(event)
        db.flush()  # Get event.id
        trending.status = 'promoted'
        promoted.append({"trending_id": tid, "event_id": str(event.id), "title": trending.title})

    db.commit()

    # Trigger AI analysis + seed interactions for all promoted events in background
    for item in promoted:
        _schedule_analysis(_generate_analysis_background(item["event_id"]))
        _schedule_analysis(_seed_interactions_background(item["event_id"]))

    return {
        "promoted": len(promoted),
        "errors": len(errors),
        "promoted_items": promoted,
        "error_items": errors,
    }


@router.post("/events/batch-publish")
async def admin_batch_publish(
    event_ids: List[str],
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Batch publish multiple candidate events."""
    published = []
    errors = []

    for eid in event_ids:
        event = db.query(Event).filter(Event.id == eid).first()
        if not event:
            errors.append({"id": eid, "error": "Not found"})
            continue
        if event.status not in ('candidate', 'archived'):
            errors.append({"id": eid, "error": f"Status is '{event.status}'"})
            continue

        event.status = 'active'
        event.published_at = datetime.utcnow()
        event.last_activity_at = datetime.utcnow()
        published.append({"event_id": eid, "title": event.title})

    db.commit()

    # Trigger AI analysis + seed interactions for all published events
    for item in published:
        _schedule_analysis(_generate_analysis_background(item["event_id"]))
        _schedule_analysis(_seed_interactions_background(item["event_id"]))

    return {
        "published": len(published),
        "errors": len(errors),
        "published_items": published,
        "error_items": errors,
    }


@router.post("/pipeline/refresh")
async def admin_trigger_pipeline(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Manually trigger the full news pipeline (fetch → dedup → cluster → heat → trim). Runs in background."""
    from app.services.news_aggregator import run_full_pipeline
    from app.core.database import SessionLocal
    import asyncio

    async def _run_pipeline():
        pipeline_db = SessionLocal()
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_full_pipeline, pipeline_db)
            logger.info(f"Pipeline complete: {result}")
        except Exception as e:
            logger.exception("Pipeline failed")
        finally:
            pipeline_db.close()

    asyncio.create_task(_run_pipeline())
    return {"status": "started", "message": "Pipeline running in background. This may take several minutes."}


@router.post("/pipeline/heat-recalculate")
async def admin_recalculate_heat(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Recalculate heat scores and re-trim to top 20."""
    from app.services.news_aggregator import run_heat_update
    try:
        result = run_heat_update(db)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heat recalculation failed: {str(e)}")


@router.post("/backfill-categories")
async def admin_backfill_categories(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Backfill categories for uncategorized trending events, then recalculate heat scores."""
    from app.services.event_clusterer import backfill_categories
    from app.services.news_aggregator import run_heat_update
    cat_result = backfill_categories(db)
    heat_result = run_heat_update(db)
    return {"categories": cat_result, "heat_recalc": heat_result}


@router.post("/recategorize-events")
async def admin_recategorize_events(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Re-classify category for ALL active published Events using the corrected
    normalize-by-keyword-count algorithm. Also recategorizes trending events."""
    from app.services.news_aggregator import classify_category as classify_na

    # Published Events
    active_events = db.query(Event).filter(Event.status == 'active').all()
    event_updated = 0
    for event in active_events:
        text = f"{event.title or ''} {event.summary or ''} {' '.join(event.tags or [])}"
        new_cat = classify_na(text)
        if new_cat and new_cat != event.category:
            event.category = new_cat
            event_updated += 1

    # Trending Events (all, not just uncategorized)
    trending_all = db.query(TrendingEvent).all()
    trending_updated = 0
    for te in trending_all:
        text = f"{te.title or ''} {te.summary or ''} {' '.join(te.keywords or [])}"
        new_cat = classify_na(text)
        if new_cat and new_cat != te.category:
            te.category = new_cat
            trending_updated += 1

    db.commit()
    return {
        "events": {"total": len(active_events), "updated": event_updated},
        "trending": {"total": len(trending_all), "updated": trending_updated},
    }


@router.post("/trending/consolidate")
async def admin_consolidate_events(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """
    Pairwise-merge already-existing raw/promoted events that should be the
    same story (same rules as live pipeline continuation detection).
    Losers are archived; winners absorb articles and concatenate timelines.
    """
    from app.services.news_aggregator import consolidate_existing_events, run_heat_update
    try:
        result = consolidate_existing_events(db)
        heat = run_heat_update(db)
        return {"status": "success", "consolidate": result, "heat_recalc": heat}
    except Exception as e:
        logger.exception("Consolidate failed")
        raise HTTPException(status_code=500, detail=f"Consolidate failed: {str(e)}")


@router.post("/events/consolidate")
async def admin_consolidate_published_events(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """
    Pairwise-merge duplicate published events on the Stories page (the
    `Event` model, not trending). EventSource rows move from loser to
    winner (deduped on uq_event_source); loser is archived.
    """
    from app.services.news_aggregator import consolidate_published_events
    try:
        result = consolidate_published_events(db)
        return {"status": "success", "consolidate": result}
    except Exception as e:
        logger.exception("Published consolidate failed")
        raise HTTPException(status_code=500, detail=f"Consolidate failed: {str(e)}")


@router.post("/trending/cleanup-bad-merges")
async def admin_cleanup_bad_merges(
    payload: dict,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """
    Archive a list of events wrongly absorbed via the (now-removed)
    text-only matching tier. Body: {"event_ids": [32, 1605, ...]}
    """
    from app.services.news_aggregator import cleanup_bad_merges
    event_ids = payload.get("event_ids") or []
    if not isinstance(event_ids, list) or not all(isinstance(i, int) for i in event_ids):
        raise HTTPException(status_code=400, detail="event_ids must be a list of ints")
    try:
        result = cleanup_bad_merges(db, event_ids)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception("cleanup-bad-merges failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/auto-archive")
async def admin_trigger_auto_archive(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Manually trigger auto-archive of stale/expired active events."""
    from app.services.event_lifecycle import auto_archive_events
    try:
        result = auto_archive_events(db)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-archive failed: {str(e)}")


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


# ==================== Seed Interactions ====================

@router.post("/seed-interactions")
async def admin_seed_all_interactions(
    force: bool = False,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Seed fake interactions (threads, comments, votes) for all active events. Runs in background."""
    import asyncio
    from app.services.seed_interactions import seed_all_active_events
    from app.core.database import SessionLocal

    async def _run_seed():
        seed_db = SessionLocal()
        try:
            result = await seed_all_active_events(seed_db, force=force)
            logger.info(f"Seed interactions complete: {result}")
        except Exception as e:
            logger.exception("Seed interactions failed")
        finally:
            seed_db.close()

    asyncio.create_task(_run_seed())
    return {"status": "started", "message": "Seeding interactions in background. This may take a few minutes."}


@router.post("/events/{event_id}/seed-interactions")
async def admin_seed_event_interactions(
    event_id: str,
    force: bool = False,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Seed fake interactions for a specific event. Runs in background."""
    import asyncio
    from app.services.seed_interactions import seed_event_interactions
    from app.core.database import SessionLocal

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    async def _run_seed():
        seed_db = SessionLocal()
        try:
            result = await seed_event_interactions(seed_db, event_id, force=force)
            logger.info(f"Seed interactions for event {event_id} complete: {result}")
        except Exception as e:
            logger.exception(f"Seed failed for event {event_id}")
        finally:
            seed_db.close()

    asyncio.create_task(_run_seed())
    return {"status": "started", "message": f"Seeding interactions for event {event_id} in background."}


@router.delete("/seed-interactions")
async def admin_cleanup_seed_interactions(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Remove all seed/fake data (users, threads, comments, votes)."""
    from app.services.seed_interactions import cleanup_seed_data
    try:
        result = await cleanup_seed_data(db)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception("Seed cleanup failed")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


# ─── Analytics Dashboard Endpoint ────────────────────────────────────

@router.get("/analytics")
async def admin_analytics(
    days: int = 7,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Get aggregated analytics data for admin dashboard."""
    from datetime import timedelta

    if days > 90:
        days = 90

    now = datetime.utcnow()
    start = now - timedelta(days=days)
    start_str = start.isoformat()

    def query_one(sql, **params):
        result = db.execute(sql_text(sql), {"start": start_str, **params})
        row = result.fetchone()
        return row[0] if row else 0

    def query_all(sql, **params):
        result = db.execute(sql_text(sql), {"start": start_str, **params})
        return [dict(row._mapping) for row in result.fetchall()]

    # Subquery to exclude seed users
    seed_filter = "email NOT LIKE '%@seed.wrhitw.local'"
    seed_user_exclude = "user_id NOT IN (SELECT id FROM users WHERE email LIKE '%@seed.wrhitw.local')"

    # ── Users ──
    today_str = now.strftime("%Y-%m-%d")
    total_users = query_one(f"SELECT COUNT(*) FROM users WHERE {seed_filter}")
    new_registrations = query_one(f"SELECT COUNT(*) FROM users WHERE {seed_filter} AND created_at >= :start")
    active_users = query_one(f"SELECT COUNT(*) FROM users WHERE {seed_filter} AND last_login_at >= :start")
    today_registrations = query_one(f"SELECT COUNT(*) FROM users WHERE {seed_filter} AND DATE(created_at) = :today", today=today_str)
    today_active_users = query_one(f"SELECT COUNT(*) FROM users WHERE {seed_filter} AND DATE(last_login_at) = :today", today=today_str)
    registrations_by_day = query_all(
        f"SELECT DATE(created_at) as date, COUNT(*) as count FROM users "
        f"WHERE {seed_filter} AND created_at >= :start GROUP BY DATE(created_at) ORDER BY date"
    )

    # ── Engagement ──
    total_threads = new_threads = total_comments = new_comments = new_likes = 0
    threads_by_day = []
    comments_by_day = []
    try:
        total_threads = query_one(f"SELECT COUNT(*) FROM threads WHERE is_deleted = false AND {seed_user_exclude}")
        new_threads = query_one(f"SELECT COUNT(*) FROM threads WHERE created_at >= :start AND is_deleted = false AND {seed_user_exclude}")
        total_comments = query_one(f"SELECT COUNT(*) FROM comments WHERE is_deleted = false AND {seed_user_exclude}")
        new_comments = query_one(f"SELECT COUNT(*) FROM comments WHERE created_at >= :start AND is_deleted = false AND {seed_user_exclude}")
        new_likes = query_one(f"SELECT COUNT(*) FROM user_likes WHERE created_at >= :start AND {seed_user_exclude}")
        threads_by_day = query_all(
            f"SELECT DATE(created_at) as date, COUNT(*) as count FROM threads "
            f"WHERE created_at >= :start AND is_deleted = false AND {seed_user_exclude} GROUP BY DATE(created_at) ORDER BY date"
        )
        comments_by_day = query_all(
            f"SELECT DATE(created_at) as date, COUNT(*) as count FROM comments "
            f"WHERE created_at >= :start AND is_deleted = false AND {seed_user_exclude} GROUP BY DATE(created_at) ORDER BY date"
        )
    except Exception as e:
        logger.debug(f"Engagement analytics query error: {e}")

    # ── Content ──
    total_active_events = query_one("SELECT COUNT(*) FROM events WHERE status = 'active'")
    events_by_category = query_all(
        "SELECT category, COUNT(*) as count FROM events WHERE status = 'active' "
        "GROUP BY category ORDER BY count DESC"
    )
    try:
        most_viewed_events = query_all(
            f"SELECT e.id, e.title, e.view_count, "
            f"  (SELECT COUNT(*) FROM comments c WHERE c.event_id = e.id AND c.is_deleted = false AND c.{seed_user_exclude}) as comment_count "
            f"FROM events e WHERE e.status = 'active' ORDER BY e.view_count DESC LIMIT 10"
        )
        most_discussed_events = query_all(
            f"SELECT e.id, e.title, e.view_count, "
            f"  (SELECT COUNT(*) FROM comments c WHERE c.event_id = e.id AND c.is_deleted = false AND c.{seed_user_exclude}) as comment_count "
            f"FROM events e WHERE e.status = 'active' ORDER BY comment_count DESC LIMIT 10"
        )
    except Exception:
        most_viewed_events = query_all(
            "SELECT id, title, view_count, 0 as comment_count "
            "FROM events WHERE status = 'active' ORDER BY view_count DESC LIMIT 10"
        )
        most_discussed_events = most_viewed_events

    # ── Traffic (from request_logs) ──
    traffic = {"total_requests": 0, "unique_ips": 0, "requests_by_day": [],
               "slow_requests": 0, "error_count": 0, "top_paths": [], "status_breakdown": {}}
    try:
        traffic["total_requests"] = query_one(
            "SELECT COUNT(*) FROM request_logs WHERE timestamp >= :start"
        )
        traffic["unique_ips"] = query_one(
            "SELECT COUNT(DISTINCT client_ip) FROM request_logs WHERE timestamp >= :start"
        )
        traffic["requests_by_day"] = query_all(
            "SELECT DATE(timestamp) as date, COUNT(*) as count FROM request_logs "
            "WHERE timestamp >= :start GROUP BY DATE(timestamp) ORDER BY date"
        )
        traffic["slow_requests"] = query_one(
            "SELECT COUNT(*) FROM request_logs WHERE timestamp >= :start AND is_slow = true"
        )
        traffic["error_count"] = query_one(
            "SELECT COUNT(*) FROM request_logs WHERE timestamp >= :start AND status_code >= 500"
        )
        traffic["top_paths"] = query_all(
            "SELECT path, COUNT(*) as count FROM request_logs "
            "WHERE timestamp >= :start GROUP BY path ORDER BY count DESC LIMIT 15"
        )

        status_rows = query_all(
            "SELECT CASE "
            "  WHEN status_code >= 500 THEN '5xx' "
            "  WHEN status_code >= 400 THEN '4xx' "
            "  WHEN status_code >= 300 THEN '3xx' "
            "  ELSE '2xx' END as status_group, COUNT(*) as count "
            "FROM request_logs WHERE timestamp >= :start GROUP BY status_group"
        )
        traffic["status_breakdown"] = {r["status_group"]: r["count"] for r in status_rows}
    except Exception as e:
        logger.debug(f"Traffic analytics query error: {e}")

    # ── Page Views ──
    page_views = {"total": 0, "unique_visitors": 0, "today_pv": 0, "today_uv": 0,
                  "views_by_day": [], "uv_by_day": [], "top_pages": [], "top_referrers": []}
    try:
        page_views["total"] = query_one(
            "SELECT COUNT(*) FROM page_views WHERE timestamp >= :start"
        )
        page_views["unique_visitors"] = query_one(
            "SELECT COUNT(DISTINCT client_ip) FROM page_views WHERE timestamp >= :start"
        )
        page_views["today_pv"] = query_one(
            "SELECT COUNT(*) FROM page_views WHERE DATE(timestamp) = :today", today=today_str
        )
        page_views["today_uv"] = query_one(
            "SELECT COUNT(DISTINCT client_ip) FROM page_views WHERE DATE(timestamp) = :today", today=today_str
        )
        page_views["views_by_day"] = query_all(
            "SELECT DATE(timestamp) as date, COUNT(*) as count FROM page_views "
            "WHERE timestamp >= :start GROUP BY DATE(timestamp) ORDER BY date"
        )
        page_views["uv_by_day"] = query_all(
            "SELECT DATE(timestamp) as date, COUNT(DISTINCT client_ip) as count FROM page_views "
            "WHERE timestamp >= :start GROUP BY DATE(timestamp) ORDER BY date"
        )
        page_views["top_pages"] = query_all(
            "SELECT path, COUNT(*) as count FROM page_views "
            "WHERE timestamp >= :start GROUP BY path ORDER BY count DESC LIMIT 15"
        )
        page_views["top_referrers"] = query_all(
            "SELECT referrer, COUNT(*) as count FROM page_views "
            "WHERE timestamp >= :start AND referrer IS NOT NULL AND referrer != '' "
            "GROUP BY referrer ORDER BY count DESC LIMIT 10"
        )
    except Exception as e:
        logger.debug(f"Page views analytics query error: {e}")

    # ── Errors ──
    recent_errors = []
    try:
        recent_errors = query_all(
            "SELECT id, timestamp, method, path, error_type, error_message "
            "FROM error_logs WHERE timestamp >= :start ORDER BY timestamp DESC LIMIT 20"
        )
    except Exception as e:
        logger.debug(f"Error logs query error: {e}")

    return {
        "period": {"days": days, "start": start.isoformat(), "end": now.isoformat()},
        "users": {
            "total": total_users,
            "new_registrations": new_registrations,
            "active_users": active_users,
            "today_registrations": today_registrations,
            "today_active_users": today_active_users,
            "registrations_by_day": registrations_by_day,
        },
        "engagement": {
            "total_threads": total_threads,
            "new_threads": new_threads,
            "total_comments": total_comments,
            "new_comments": new_comments,
            "new_likes": new_likes,
            "threads_by_day": threads_by_day,
            "comments_by_day": comments_by_day,
        },
        "content": {
            "total_active_events": total_active_events,
            "events_by_category": events_by_category,
            "most_viewed_events": most_viewed_events,
            "most_discussed_events": most_discussed_events,
        },
        "traffic": traffic,
        "page_views": page_views,
        "recent_errors": recent_errors,
    }


@router.post("/data-cleanup")
async def admin_data_cleanup(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """One-time data cleanup: fix tags, remove duplicates, fix categories, remove non-news."""
    import json
    results = {"tags_fixed": 0, "duplicates_removed": 0, "non_news_removed": 0, "categories_fixed": 0}

    # 1. Fix broken tags (single-character arrays from json.dumps double-encoding)
    events = db.query(Event).all()
    for event in events:
        if event.tags and len(event.tags) > 5:
            # Check if tags look like exploded characters from a JSON string
            sample = ''.join(event.tags[:20])
            if sample.startswith('["') or sample.startswith("[\""):
                try:
                    # Reconstruct the original JSON string and parse it
                    original = ''.join(event.tags)
                    parsed = json.loads(original)
                    if isinstance(parsed, list) and all(isinstance(t, str) for t in parsed):
                        event.tags = parsed
                        results["tags_fixed"] += 1
                except (json.JSONDecodeError, TypeError):
                    pass

    # 2. Remove duplicate events (same title, keep the one with more views/comments)
    from collections import defaultdict
    title_groups = defaultdict(list)
    active_events = db.query(Event).filter(Event.status.in_(['active', 'candidate'])).all()
    for event in active_events:
        title_groups[event.title.strip().lower()].append(event)

    for title, group in title_groups.items():
        if len(group) > 1:
            # Keep the one with most views, then most recent
            group.sort(key=lambda e: (e.view_count or 0, e.created_at or datetime.min), reverse=True)
            for dup in group[1:]:
                dup.status = 'dismissed'
                results["duplicates_removed"] += 1
                logger.info(f"Dismissed duplicate: '{dup.title[:50]}'")

    # 3. Remove non-news content
    non_news_patterns = [
        'deploytarot', 'meow.camera', 'show hn:', 'ask hn:',
        'launch hn:', 'tell hn:',
        'go hard on agents', 'not on your filesystem',
    ]
    for event in active_events:
        title_lower = event.title.strip().lower()
        if any(pattern in title_lower for pattern in non_news_patterns):
            event.status = 'dismissed'
            results["non_news_removed"] += 1
            logger.info(f"Dismissed non-news: '{event.title[:50]}'")

    # 4. Re-classify all active/candidate events using improved classifier
    from app.services.event_clusterer import EventClusterer
    clusterer = EventClusterer(db)
    for event in active_events:
        if event.status == 'dismissed':
            continue
        text = f"{event.title or ''} {event.summary or ''}"
        new_cat = clusterer.classify_category(text, title=event.title or "")
        if new_cat and new_cat != event.category:
            old_cat = event.category
            event.category = new_cat
            results["categories_fixed"] += 1
            logger.info(f"Re-classified: '{event.title[:50]}' {old_cat} -> {new_cat}")

    # 5. Clean up trending pool: dismiss duplicates and non-news
    from app.models.trending import TrendingEvent as TE
    trending_events = db.query(TE).filter(TE.status == 'raw').all()
    trending_title_groups = defaultdict(list)
    for te in trending_events:
        trending_title_groups[te.title.strip().lower()].append(te)
    for title, group in trending_title_groups.items():
        if len(group) > 1:
            group.sort(key=lambda e: (e.heat_score or 0), reverse=True)
            for dup in group[1:]:
                dup.status = 'dismissed'
                results["duplicates_removed"] += 1
    for te in trending_events:
        title_lower = te.title.strip().lower()
        if any(pattern in title_lower for pattern in non_news_patterns):
            te.status = 'dismissed'
            results["non_news_removed"] += 1

    db.commit()
    return {"status": "success", "results": results}
