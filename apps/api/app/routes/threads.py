"""
Thread API Routes - Discussion threads within events
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.auth import get_current_user, get_current_user_optional
from app.models import Event, User
from app.models.threads import Thread
from app.models.comments import Comment
from app.models.personas import UserPersona

router = APIRouter()


class ThreadCreate(BaseModel):
    title: str
    content: str
    user_persona_id: Optional[str] = None
    tags: Optional[list] = None
    stakeholder_filter_tag: Optional[str] = None


class ThreadUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list] = None


@router.get("/events/{event_id}/threads")
async def list_threads(
    event_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|like_count|reply_count)$"),
    stakeholder_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List threads for an event with pagination and sorting."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    query = db.query(Thread).options(
        joinedload(Thread.user_persona),
    ).filter(
        Thread.event_id == event_id,
        Thread.is_deleted == False,
    )

    if stakeholder_id:
        query = query.filter(Thread.stakeholder_filter_tag == stakeholder_id)

    total = query.count()

    if sort_by == "like_count":
        query = query.order_by(Thread.is_pinned.desc(), Thread.like_count.desc())
    elif sort_by == "reply_count":
        query = query.order_by(Thread.is_pinned.desc(), Thread.reply_count.desc())
    else:
        query = query.order_by(Thread.is_pinned.desc(), Thread.created_at.desc())

    offset = (page - 1) * page_size
    threads = query.offset(offset).limit(page_size).all()

    # Enrich with author info
    items = []
    for t in threads:
        data = t.to_dict()
        data["persona_name"] = t.user_persona.persona_name if t.user_persona else "Anonymous"
        data["avatar_color"] = t.user_persona.avatar_color if t.user_persona else "gray"
        items.append(data)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/threads/{thread_id}")
async def get_thread(
    thread_id: str,
    db: Session = Depends(get_db),
):
    """Get thread details."""
    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.is_deleted == False).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Increment view count
    thread.view_count += 1
    db.commit()

    data = thread.to_dict()
    persona = db.query(UserPersona).filter(UserPersona.id == thread.user_persona_id).first() if thread.user_persona_id else None
    data["persona_name"] = persona.persona_name if persona else "Anonymous"
    data["avatar_color"] = persona.avatar_color if persona else "gray"

    return data


@router.post("/events/{event_id}/threads")
@limiter.limit("5/minute")
async def create_thread(
    request: Request,
    event_id: str,
    thread_data: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new thread in an event (requires auth + persona)."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Validate persona ownership
    if thread_data.user_persona_id:
        persona = db.query(UserPersona).filter(
            UserPersona.id == thread_data.user_persona_id,
            UserPersona.user_id == current_user.id,
            UserPersona.is_deleted == False,
        ).first()
        if not persona:
            raise HTTPException(status_code=403, detail="Invalid persona")

    thread = Thread(
        event_id=event_id,
        user_id=current_user.id,
        user_persona_id=thread_data.user_persona_id,
        title=thread_data.title,
        content=thread_data.content,
        tags=thread_data.tags,
        stakeholder_filter_tag=thread_data.stakeholder_filter_tag,
    )
    db.add(thread)

    # Update event activity timestamp
    from app.services.event_lifecycle import touch_event_activity
    touch_event_activity(db, event_id)

    db.commit()
    db.refresh(thread)

    return thread.to_dict()


@router.put("/threads/{thread_id}")
async def update_thread(
    thread_id: str,
    thread_data: ThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a thread (author only)."""
    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.is_deleted == False).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    if str(thread.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not the thread author")

    if thread_data.title is not None:
        thread.title = thread_data.title
    if thread_data.content is not None:
        thread.content = thread_data.content
    if thread_data.tags is not None:
        thread.tags = thread_data.tags

    db.commit()
    db.refresh(thread)

    return thread.to_dict()


@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a thread (author only)."""
    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.is_deleted == False).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    if str(thread.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not the thread author")

    thread.is_deleted = True
    db.commit()

    return {"message": "Thread deleted"}


@router.post("/threads/{thread_id}/vote")
@limiter.limit("30/minute")
async def vote_thread(
    request: Request,
    thread_id: str,
    action: str = Query(..., regex="^(like|dislike)$", description="like or dislike"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Vote on a thread (like/dislike). Toggle behavior:
    - Same vote again → cancel (remove vote)
    - Different vote → switch (e.g. like→dislike)
    """
    from app.models.user_likes import UserLike

    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.is_deleted == False).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    existing = db.query(UserLike).filter(
        UserLike.user_id == current_user.id,
        UserLike.thread_id == thread_id,
    ).first()

    if existing:
        if existing.vote_type == action:
            # Same vote → cancel
            if action == 'like':
                thread.like_count = max(0, thread.like_count - 1)
            else:
                thread.dislike_count = max(0, getattr(thread, 'dislike_count', 0) - 1)
            db.delete(existing)
            db.commit()
            return {"like_count": thread.like_count, "dislike_count": getattr(thread, 'dislike_count', 0), "user_vote": None}
        else:
            # Switch vote
            old_type = existing.vote_type
            if old_type == 'like':
                thread.like_count = max(0, thread.like_count - 1)
            else:
                thread.dislike_count = max(0, getattr(thread, 'dislike_count', 0) - 1)
            if action == 'like':
                thread.like_count += 1
            else:
                if not hasattr(thread, 'dislike_count') or thread.dislike_count is None:
                    thread.dislike_count = 0
                thread.dislike_count += 1
            existing.vote_type = action
            db.commit()
            return {"like_count": thread.like_count, "dislike_count": getattr(thread, 'dislike_count', 0), "user_vote": action}
    else:
        # New vote
        if action == 'like':
            thread.like_count += 1
        else:
            if not hasattr(thread, 'dislike_count') or thread.dislike_count is None:
                thread.dislike_count = 0
            thread.dislike_count += 1
        vote = UserLike(user_id=current_user.id, thread_id=thread_id, vote_type=action)
        db.add(vote)

        # Update event activity timestamp
        from app.services.event_lifecycle import touch_event_activity
        touch_event_activity(db, str(thread.event_id))

        # Notify thread owner
        from app.models.notifications import create_notification
        persona = db.query(UserPersona).filter(UserPersona.user_id == current_user.id, UserPersona.is_deleted == False).first()
        actor_name = persona.persona_name if persona else "Someone"
        create_notification(
            db, thread.user_id, action,
            f'{actor_name} {action}d your thread "{thread.title[:50]}"',
            f'/events/{thread.event_id}/threads/{thread_id}',
            source_user_id=current_user.id, thread_id=thread_id,
        )

        db.commit()
        return {"like_count": thread.like_count, "dislike_count": getattr(thread, 'dislike_count', 0), "user_vote": action}
