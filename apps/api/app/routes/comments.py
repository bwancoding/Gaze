"""
WRHITW Comment System API
Comment system API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.core.limiter import limiter

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_user_optional
from app.models import User
from app.models.comments import Comment
from app.models.personas import UserPersona, EventStakeholderVerification

router = APIRouter(prefix="/api/comments", tags=["Comments"])


def check_persona_ownership(db: Session, persona_id: str, user_id: str):
    """Check if the user owns this persona"""
    persona = db.query(UserPersona).filter(
        UserPersona.id == persona_id,
        UserPersona.user_id == user_id,
        UserPersona.is_deleted == False
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found or not owned by user")
    
    return persona


def check_verified_status(db: Session, persona_id: str, event_id: str) -> bool:
    """Check if the persona has an approved verification for this event"""
    verification = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.user_persona_id == persona_id,
        EventStakeholderVerification.event_id == event_id,
        EventStakeholderVerification.status == 'approved'
    ).first()
    
    return verification is not None


@router.get("/event/{event_id}")
def get_event_comments(
    event_id: str,
    parent_id: Optional[str] = Query(None, description="Parent comment ID for replies"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Get all comments for an event (supports replies)

    - Not logged in: up to 20 comments
    - Logged in: all comments with pagination
    """
    # Limit unauthenticated users to 20 comments
    if current_user is None and limit > 20:
        limit = 20
    
    query = db.query(Comment).options(
        joinedload(Comment.persona),
        joinedload(Comment.user)
    ).filter(
        Comment.event_id == event_id,
        Comment.is_deleted == False
    )
    
    if parent_id:
        # Get replies for specific parent
        query = query.filter(Comment.parent_id == parent_id)
    # When no parent_id filter, return ALL comments (top-level + replies)
    # Frontend handles nesting/grouping
    
    total = query.count()
    comments = query.order_by(desc(Comment.created_at)).offset(offset).limit(limit).all()
    
    return {
        "items": [
            {
                **comment.to_dict(include_verified_badge=True),
                "is_verified": check_verified_status(db, str(comment.user_persona_id), event_id) if comment.user_persona_id else False
            }
            for comment in comments
        ],
        "total": total,
        "has_more": total > offset + limit,
        "login_required_for_more": current_user is None and total > 20
    }


@router.post("")
@limiter.limit("10/minute")
def create_comment(
    request: Request,
    event_id: str = Body(..., embed=True),
    user_persona_id: str = Body(..., embed=True),
    content: str = Body(..., embed=True),
    parent_id: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Login required
):
    """Create a new comment or reply"""
    # Validate content
    if not content or len(content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")
    
    if len(content) > 5000:
        raise HTTPException(status_code=400, detail="Comment content too long (max 5000 characters)")
    
    # Check persona ownership
    persona = check_persona_ownership(db, user_persona_id, str(current_user.id))
    
    # If this is a reply, check that the parent comment exists
    if parent_id:
        parent_comment = db.query(Comment).filter(
            Comment.id == parent_id,
            Comment.event_id == event_id,
            Comment.is_deleted == False
        ).first()
        
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        # Increment the parent comment's reply count
        parent_comment.reply_count += 1
    
    # Create comment
    comment = Comment(
        user_id=current_user.id,
        user_persona_id=user_persona_id,
        event_id=event_id,
        content=content.strip(),
        parent_id=parent_id
    )

    db.add(comment)

    # Update event activity timestamp
    from app.services.event_lifecycle import touch_event_activity
    touch_event_activity(db, event_id)

    # Notify parent comment author on reply
    if parent_id and parent_comment:
        from app.models.notifications import create_notification
        create_notification(
            db, parent_comment.user_id, "reply",
            f'{persona.persona_name} replied to your comment',
            f'/events/{event_id}',
            source_user_id=current_user.id, comment_id=parent_id,
        )

    db.commit()
    db.refresh(comment)

    return {
        "message": "Comment created successfully",
        "comment": {
            **comment.to_dict(include_verified_badge=True),
            "is_verified": check_verified_status(db, user_persona_id, event_id)
        }
    }


@router.put("/{comment_id}")
def update_comment(
    comment_id: str,
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Login required
):
    """Edit own comment"""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.user_id == current_user.id,
        Comment.is_deleted == False
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Validate content
    if not content or len(content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")

    if len(content) > 5000:
        raise HTTPException(status_code=400, detail="Comment content too long (max 5000 characters)")
    
    comment.content = content.strip()
    comment.is_edited = True
    comment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(comment)
    
    return {
        "message": "Comment updated successfully",
        "comment": comment.to_dict(include_verified_badge=True)
    }


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Login required
):
    """Delete own comment (soft delete)"""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.user_id == current_user.id,
        Comment.is_deleted == False
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Soft delete
    comment.is_deleted = True
    comment.deleted_at = datetime.utcnow()
    comment.content = "[Deleted]"
    
    # If this is a reply, decrement the parent comment's reply count
    if comment.parent_id:
        parent_comment = db.query(Comment).filter(
            Comment.id == comment.parent_id
        ).first()
        if parent_comment:
            parent_comment.reply_count = max(0, parent_comment.reply_count - 1)
    
    db.commit()
    
    return {"message": "Comment deleted successfully"}


@router.get("/thread/{thread_id}")
def get_thread_comments(
    thread_id: str,
    parent_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get comments for a thread."""
    from app.models.threads import Thread

    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.is_deleted == False).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    query = db.query(Comment).options(
        joinedload(Comment.persona),
    ).filter(
        Comment.thread_id == thread_id,
        Comment.is_deleted == False,
    )

    if parent_id:
        query = query.filter(Comment.parent_id == parent_id)
    # When no parent_id filter, return ALL comments (top-level + replies)
    # Frontend handles nesting/grouping

    total = query.count()
    comments = query.order_by(desc(Comment.created_at)).offset(offset).limit(limit).all()

    return {
        "items": [comment.to_dict(include_verified_badge=True) for comment in comments],
        "total": total,
        "has_more": total > offset + limit,
    }


@router.post("/thread/{thread_id}")
@limiter.limit("10/minute")
def create_thread_comment(
    request: Request,
    thread_id: str,
    user_persona_id: str = Body(..., embed=True),
    content: str = Body(..., embed=True),
    parent_id: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a comment in a thread."""
    from app.models.threads import Thread

    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.is_deleted == False).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    if thread.is_locked:
        raise HTTPException(status_code=403, detail="Thread is locked")

    if not content or len(content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")
    if len(content) > 5000:
        raise HTTPException(status_code=400, detail="Comment content too long (max 5000 characters)")

    persona = check_persona_ownership(db, user_persona_id, str(current_user.id))

    if parent_id:
        parent_comment = db.query(Comment).filter(
            Comment.id == parent_id,
            Comment.thread_id == thread_id,
            Comment.is_deleted == False,
        ).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        parent_comment.reply_count += 1

    comment = Comment(
        user_id=current_user.id,
        user_persona_id=user_persona_id,
        event_id=thread.event_id,
        thread_id=thread_id,
        content=content.strip(),
        parent_id=parent_id,
    )

    db.add(comment)
    thread.reply_count += 1

    # Update event activity timestamp
    from app.services.event_lifecycle import touch_event_activity
    touch_event_activity(db, str(thread.event_id))

    # Notifications
    from app.models.notifications import create_notification
    link = f'/events/{thread.event_id}/threads/{thread_id}'

    # Notify parent comment author on reply
    if parent_id and parent_comment:
        create_notification(
            db, parent_comment.user_id, "reply",
            f'{persona.persona_name} replied to your comment',
            link, source_user_id=current_user.id, comment_id=parent_id,
        )

    # Notify thread owner of new comment (if not replying to thread owner's own comment)
    if thread.user_id:
        create_notification(
            db, thread.user_id, "thread_reply",
            f'{persona.persona_name} commented on your thread "{thread.title[:50]}"',
            link, source_user_id=current_user.id, thread_id=thread_id,
        )

    db.commit()
    db.refresh(comment)

    return {
        "message": "Comment created successfully",
        "comment": comment.to_dict(include_verified_badge=True),
    }


@router.post("/{comment_id}/vote")
def vote_comment(
    comment_id: str,
    action: str = Query(..., regex="^(like|dislike)$", description="like or dislike"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Vote on a comment (like/dislike). Toggle behavior:
    - Same vote again → cancel (remove vote)
    - Different vote → switch (e.g. like→dislike)
    """
    from app.models.user_likes import UserLike

    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    existing = db.query(UserLike).filter(
        UserLike.user_id == current_user.id,
        UserLike.comment_id == comment_id,
    ).first()

    if existing:
        if existing.vote_type == action:
            # Same vote → cancel
            if action == 'like':
                comment.like_count = max(0, comment.like_count - 1)
            else:
                comment.dislike_count = max(0, comment.dislike_count - 1)
            db.delete(existing)
            db.commit()
            return {"like_count": comment.like_count, "dislike_count": comment.dislike_count, "user_vote": None}
        else:
            # Switch vote
            if existing.vote_type == 'like':
                comment.like_count = max(0, comment.like_count - 1)
            else:
                comment.dislike_count = max(0, comment.dislike_count - 1)
            if action == 'like':
                comment.like_count += 1
            else:
                comment.dislike_count += 1
            existing.vote_type = action
            db.commit()
            return {"like_count": comment.like_count, "dislike_count": comment.dislike_count, "user_vote": action}
    else:
        # New vote
        if action == 'like':
            comment.like_count += 1
        else:
            comment.dislike_count += 1
        vote = UserLike(user_id=current_user.id, comment_id=comment_id, vote_type=action)
        db.add(vote)

        # Update event activity timestamp
        from app.services.event_lifecycle import touch_event_activity
        touch_event_activity(db, str(comment.event_id))

        # Notify comment owner
        from app.models.notifications import create_notification
        from app.models.personas import UserPersona
        persona = db.query(UserPersona).filter(UserPersona.user_id == current_user.id, UserPersona.is_deleted == False).first()
        actor_name = persona.persona_name if persona else "Someone"
        link = f'/events/{comment.event_id}'
        if comment.thread_id:
            link = f'/events/{comment.event_id}/threads/{comment.thread_id}'
        create_notification(
            db, comment.user_id, action,
            f'{actor_name} {action}d your comment',
            link, source_user_id=current_user.id, comment_id=comment_id,
        )

        db.commit()
        return {"like_count": comment.like_count, "dislike_count": comment.dislike_count, "user_vote": action}
