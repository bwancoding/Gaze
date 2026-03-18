"""
Notifications API - User notification management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.auth import get_current_user
from app.models import User
from app.models.notifications import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List notifications for the current user (unread first, then by date)."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()

    notifications = query.order_by(
        asc(Notification.is_read),  # unread first
        desc(Notification.created_at),
    ).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": n.id,
                "type": n.type,
                "message": n.message,
                "link_url": n.link_url,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifications
        ],
        "total": total,
        "unread_count": unread_count,
        "page": page,
        "page_size": page_size,
    }


@router.get("/unread-count")
@limiter.limit("120/minute")
async def get_unread_count(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get count of unread notifications."""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()

    return {"count": count}


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a single notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()

    return {"message": "Marked as read"}


@router.post("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()

    return {"message": "All notifications marked as read"}
