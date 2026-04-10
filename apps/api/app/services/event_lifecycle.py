"""
Event Lifecycle Manager

Handles auto-archiving of active events based on:
1. Inactivity timeout: 3 days with no new articles, comments, threads, or votes
2. Hard expiration: 7 days after published_at regardless of activity
3. Overflow cap: max 50 active events, oldest-activity-first archived when exceeded

Also provides helper to update last_activity_at on relevant actions.
"""
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.models import Event

logger = logging.getLogger(__name__)

# Configuration constants
MAX_ACTIVE_EVENTS = 41  # Stories page shows top 41 by heat (page 1: 21 = lead+20, page 2: 20)
INACTIVITY_DAYS = 3
HARD_EXPIRY_DAYS = 7


def trim_active_events_to_cap(db: Session, cap: int = MAX_ACTIVE_EVENTS) -> dict:
    """Archive any active events beyond the top `cap` by hot_score.

    Called after heat updates and publish operations to enforce the hard cap
    on the Stories page. Lowest-heat events lose first.
    """
    now = datetime.now(timezone.utc)
    active = (
        db.query(Event)
        .filter(Event.status == 'active')
        .order_by(Event.hot_score.desc().nullslast(), Event.last_activity_at.desc().nullslast())
        .all()
    )
    if len(active) <= cap:
        return {"active_before": len(active), "archived": 0, "active_after": len(active)}

    archived = 0
    for event in active[cap:]:
        event.status = 'archived'
        event.archived_at = now
        archived += 1
        logger.info(f"Trim: archived '{(event.title or '')[:50]}' (heat={event.hot_score or 0:.0f}, rank>{cap})")

    db.commit()
    return {"active_before": len(active), "archived": archived, "active_after": cap}


def auto_archive_events(db: Session) -> dict:
    """
    Run auto-archive logic on all active events.
    Returns summary of actions taken.
    """
    now = datetime.now(timezone.utc)
    archived_inactivity = 0
    archived_expired = 0
    archived_overflow = 0

    active_events = (
        db.query(Event)
        .filter(Event.status == 'active')
        .order_by(Event.last_activity_at.desc().nullslast())
        .all()
    )

    if not active_events:
        return {"archived_inactivity": 0, "archived_expired": 0, "archived_overflow": 0, "active_remaining": 0}

    still_active = []

    for event in active_events:
        should_archive = False
        reason = ""

        # Rule 1: Hard expiration — 7 days after publishing
        published = event.published_at or event.created_at
        if published and (now - published) > timedelta(days=HARD_EXPIRY_DAYS):
            should_archive = True
            reason = "hard_expiry"
            archived_expired += 1

        # Rule 2: Inactivity — 3 days with no activity
        if not should_archive:
            last_active = event.last_activity_at or event.published_at or event.created_at
            if last_active and (now - last_active) > timedelta(days=INACTIVITY_DAYS):
                should_archive = True
                reason = "inactivity"
                archived_inactivity += 1

        if should_archive:
            event.status = 'archived'
            event.archived_at = now
            logger.info(f"Auto-archived event '{event.title[:50]}' (reason: {reason})")
        else:
            still_active.append(event)

    # Rule 3: Overflow cap — if more than MAX_ACTIVE_EVENTS still active,
    # keep the top `cap` by hot_score and archive the cold tail.
    if len(still_active) > MAX_ACTIVE_EVENTS:
        still_active.sort(key=lambda e: (e.hot_score or 0), reverse=True)
        overflow = still_active[MAX_ACTIVE_EVENTS:]
        for event in overflow:
            event.status = 'archived'
            event.archived_at = now
            archived_overflow += 1
            logger.info(f"Auto-archived event '{event.title[:50]}' (reason: overflow, heat={event.hot_score or 0:.0f})")

    db.commit()

    active_remaining = (
        db.query(Event)
        .filter(Event.status == 'active')
        .count()
    )

    result = {
        "archived_inactivity": archived_inactivity,
        "archived_expired": archived_expired,
        "archived_overflow": archived_overflow,
        "active_remaining": active_remaining,
    }
    logger.info(f"Auto-archive complete: {result}")
    return result


def touch_event_activity(db: Session, event_id: str):
    """
    Update last_activity_at for an event.
    Call this whenever a thread, comment, or vote is created for the event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if event and event.status == 'active':
        event.last_activity_at = datetime.now(timezone.utc)
        # Don't commit here — caller is responsible for committing
