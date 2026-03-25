"""
Event Lifecycle Manager

Handles auto-archiving of active events based on:
1. Inactivity timeout: 3 days with no new articles, comments, threads, or votes
2. Hard expiration: 7 days after published_at regardless of activity
3. Overflow cap: max 50 active events, oldest-activity-first archived when exceeded

Also provides helper to update last_activity_at on relevant actions.
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.models import Event

logger = logging.getLogger(__name__)

# Configuration constants
MAX_ACTIVE_EVENTS = 50
INACTIVITY_DAYS = 3
HARD_EXPIRY_DAYS = 7


def auto_archive_events(db: Session) -> dict:
    """
    Run auto-archive logic on all active events.
    Returns summary of actions taken.
    """
    now = datetime.utcnow()
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

    # Rule 3: Overflow cap — if more than 50 still active, archive least active
    if len(still_active) > MAX_ACTIVE_EVENTS:
        # Sort by last_activity_at ascending (least active first)
        still_active.sort(key=lambda e: (e.last_activity_at or e.created_at or now))
        overflow = still_active[:len(still_active) - MAX_ACTIVE_EVENTS]
        for event in overflow:
            event.status = 'archived'
            event.archived_at = now
            archived_overflow += 1
            logger.info(f"Auto-archived event '{event.title[:50]}' (reason: overflow)")

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
        event.last_activity_at = datetime.utcnow()
        # Don't commit here — caller is responsible for committing
