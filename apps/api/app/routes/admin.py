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
        hot_score=trending.heat_score or 0,
        trending_origin_id=trending.id,
        tags=json.dumps(trending.keywords) if trending.keywords else None,
    )
    db.add(event)

    trending.status = 'promoted'
    db.commit()
    db.refresh(event)

    # Trigger AI analysis in background (non-blocking)
    import asyncio
    try:
        from app.services.event_analysis_service import generate_event_analysis
        from app.core.database import SessionLocal
        async def _run_analysis():
            analysis_db = SessionLocal()
            try:
                await generate_event_analysis(analysis_db, str(event.id), force=True)
                logger.info(f"AI analysis completed for event {event.id}")
            except Exception as e:
                logger.warning(f"AI analysis failed for event {event.id}: {e}")
            finally:
                analysis_db.close()
        asyncio.create_task(_run_analysis())
    except Exception as e:
        logger.warning(f"Failed to schedule AI analysis: {e}")

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
            tags=json.dumps(trending.keywords) if trending.keywords else None,
        )
        db.add(event)
        db.flush()  # Get event.id
        trending.status = 'promoted'
        promoted.append({"trending_id": tid, "event_id": str(event.id), "title": trending.title})

    db.commit()

    # Trigger AI analysis for all promoted events in background
    import asyncio
    try:
        from app.services.event_analysis_service import generate_event_analysis
        from app.core.database import SessionLocal
        async def _run_batch_analysis():
            for item in promoted:
                analysis_db = SessionLocal()
                try:
                    await generate_event_analysis(analysis_db, item["event_id"], force=True)
                    logger.info(f"AI analysis completed for event {item['event_id']}")
                except Exception as e:
                    logger.warning(f"AI analysis failed for event {item['event_id']}: {e}")
                finally:
                    analysis_db.close()
        asyncio.create_task(_run_batch_analysis())
    except Exception as e:
        logger.warning(f"Failed to schedule batch AI analysis: {e}")

    return {
        "promoted": len(promoted),
        "errors": len(errors),
        "promoted_items": promoted,
        "error_items": errors,
    }


@router.post("/events/batch-publish")
async def admin_batch_publish(
    event_ids: List[str],
    background_tasks: BackgroundTasks,
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
        background_tasks.add_task(_generate_analysis_background, eid)

    db.commit()

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
    """Manually trigger the full news pipeline (fetch → dedup → cluster → heat → trim)."""
    from app.services.news_aggregator import run_full_pipeline
    import asyncio
    try:
        # run_full_pipeline uses asyncio.run() internally, which conflicts with
        # the already-running event loop in FastAPI. Run it in a thread instead.
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_full_pipeline, db)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


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
    """Seed fake interactions (threads, comments, votes) for all active events."""
    from app.services.seed_interactions import seed_all_active_events
    try:
        result = await seed_all_active_events(db, force=force)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception("Seed interactions failed")
        raise HTTPException(status_code=500, detail=f"Seed failed: {str(e)}")


@router.post("/events/{event_id}/seed-interactions")
async def admin_seed_event_interactions(
    event_id: str,
    force: bool = False,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Seed fake interactions for a specific event."""
    from app.services.seed_interactions import seed_event_interactions
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    try:
        result = await seed_event_interactions(db, event_id, force=force)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception(f"Seed failed for event {event_id}")
        raise HTTPException(status_code=500, detail=f"Seed failed: {str(e)}")


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

    # ── Users ──
    total_users = query_one("SELECT COUNT(*) FROM users")
    new_registrations = query_one("SELECT COUNT(*) FROM users WHERE created_at >= :start")
    active_users = query_one("SELECT COUNT(*) FROM users WHERE last_login_at >= :start")
    registrations_by_day = query_all(
        "SELECT DATE(created_at) as date, COUNT(*) as count FROM users "
        "WHERE created_at >= :start GROUP BY DATE(created_at) ORDER BY date"
    )

    # ── Engagement ──
    total_threads = query_one("SELECT COUNT(*) FROM threads WHERE is_deleted = 0")
    new_threads = query_one("SELECT COUNT(*) FROM threads WHERE created_at >= :start AND is_deleted = 0")
    total_comments = query_one("SELECT COUNT(*) FROM comments WHERE is_deleted = 0")
    new_comments = query_one("SELECT COUNT(*) FROM comments WHERE created_at >= :start AND is_deleted = 0")
    new_likes = query_one("SELECT COUNT(*) FROM user_likes WHERE created_at >= :start")
    threads_by_day = query_all(
        "SELECT DATE(created_at) as date, COUNT(*) as count FROM threads "
        "WHERE created_at >= :start AND is_deleted = 0 GROUP BY DATE(created_at) ORDER BY date"
    )
    comments_by_day = query_all(
        "SELECT DATE(created_at) as date, COUNT(*) as count FROM comments "
        "WHERE created_at >= :start AND is_deleted = 0 GROUP BY DATE(created_at) ORDER BY date"
    )

    # ── Content ──
    total_active_events = query_one("SELECT COUNT(*) FROM events WHERE status = 'active'")
    events_by_category = query_all(
        "SELECT category, COUNT(*) as count FROM events WHERE status = 'active' "
        "GROUP BY category ORDER BY count DESC"
    )
    most_viewed_events = query_all(
        "SELECT e.id, e.title, e.view_count, "
        "  (SELECT COUNT(*) FROM comments c WHERE c.event_id = e.id AND c.is_deleted = 0) as comment_count "
        "FROM events e WHERE e.status = 'active' ORDER BY e.view_count DESC LIMIT 10"
    )
    most_discussed_events = query_all(
        "SELECT e.id, e.title, e.view_count, "
        "  (SELECT COUNT(*) FROM comments c WHERE c.event_id = e.id AND c.is_deleted = 0) as comment_count "
        "FROM events e WHERE e.status = 'active' ORDER BY comment_count DESC LIMIT 10"
    )

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
            "SELECT COUNT(*) FROM request_logs WHERE timestamp >= :start AND is_slow = 1"
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
    page_views = {"total": 0, "unique_visitors": 0, "views_by_day": [],
                  "top_pages": [], "top_referrers": []}
    try:
        page_views["total"] = query_one(
            "SELECT COUNT(*) FROM page_views WHERE timestamp >= :start"
        )
        page_views["unique_visitors"] = query_one(
            "SELECT COUNT(DISTINCT client_ip) FROM page_views WHERE timestamp >= :start"
        )
        page_views["views_by_day"] = query_all(
            "SELECT DATE(timestamp) as date, COUNT(*) as count FROM page_views "
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
