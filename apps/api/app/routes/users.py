"""
User Profile API - My threads, my comments, password change.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import User, Event
from app.models.threads import Thread
from app.models.comments import Comment
from app.models.personas import UserPersona

router = APIRouter(prefix="/users", tags=["Users"])


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class DisplayNameUpdate(BaseModel):
    display_name: str


@router.get("/me/threads")
async def get_my_threads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all threads created by the current user."""
    query = db.query(Thread).options(
        joinedload(Thread.event),
        joinedload(Thread.user_persona),
    ).filter(
        Thread.user_id == current_user.id,
        Thread.is_deleted == False,
    )

    total = query.count()
    threads = query.order_by(desc(Thread.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for t in threads:
        items.append({
            "id": str(t.id),
            "title": t.title,
            "event_id": str(t.event_id),
            "event_title": t.event.title if t.event else "Unknown Event",
            "persona_name": t.user_persona.persona_name if t.user_persona else "Anonymous",
            "avatar_color": t.user_persona.avatar_color if t.user_persona else "gray",
            "reply_count": t.reply_count or 0,
            "like_count": t.like_count or 0,
            "dislike_count": t.dislike_count or 0,
            "view_count": t.view_count or 0,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/me/comments")
async def get_my_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all comments by the current user."""
    query = db.query(Comment).options(
        joinedload(Comment.persona),
        joinedload(Comment.event),
        joinedload(Comment.thread),
    ).filter(
        Comment.user_id == current_user.id,
        Comment.is_deleted == False,
    )

    total = query.count()
    comments = query.order_by(desc(Comment.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for c in comments:
        thread_title = c.thread.title if c.thread else None
        content_preview = c.content[:150] + "..." if len(c.content) > 150 else c.content

        items.append({
            "id": str(c.id),
            "content_preview": content_preview,
            "event_id": str(c.event_id),
            "event_title": c.event.title if c.event else "Unknown Event",
            "thread_id": str(c.thread_id) if c.thread_id else None,
            "thread_title": thread_title,
            "persona_name": c.persona.persona_name if c.persona else "Anonymous",
            "avatar_color": c.persona.avatar_color if c.persona else "gray",
            "like_count": c.like_count or 0,
            "dislike_count": c.dislike_count or 0,
            "reply_count": c.reply_count or 0,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/me/change-password")
async def change_password(
    data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change the current user's password."""
    from app.utils.security import verify_password, hash_password

    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")

    current_user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.put("/me/display-name")
async def update_display_name(
    data: DisplayNameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the current user's display name."""
    if not data.display_name or len(data.display_name.strip()) == 0:
        raise HTTPException(status_code=400, detail="Display name cannot be empty")

    if len(data.display_name) > 100:
        raise HTTPException(status_code=400, detail="Display name too long (max 100 characters)")

    current_user.display_name = data.display_name.strip()
    db.commit()

    return {
        "message": "Display name updated",
        "display_name": current_user.display_name,
    }
