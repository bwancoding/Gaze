"""
WRHITW Comment System API
评论系统 API 接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_user_optional
from app.models import User
from app.models.comments import Comment
from app.models.personas import UserPersona, EventStakeholderVerification

router = APIRouter(prefix="/api/comments", tags=["Comments"])


def check_persona_ownership(db: Session, persona_id: str, user_id: str):
    """检查用户是否拥有该 Persona"""
    persona = db.query(UserPersona).filter(
        UserPersona.id == persona_id,
        UserPersona.user_id == user_id,
        UserPersona.is_deleted == False
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found or not owned by user")
    
    return persona


def check_verified_status(db: Session, persona_id: str, event_id: str) -> bool:
    """检查 Persona 在该事件中是否有已认证的验证"""
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
    获取事件的所有评论（支持回复）
    
    - 未登录：最多 20 条
    - 已登录：全部评论，支持分页
    """
    # 未登录用户限制 20 条
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
        # 获取回复
        query = query.filter(Comment.parent_id == parent_id)
    else:
        # 获取顶级评论
        query = query.filter(Comment.parent_id == None)
    
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
    current_user: User = Depends(get_current_user),  # 必须登录
):
    """创建新评论或回复"""
    # 验证内容
    if not content or len(content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")
    
    if len(content) > 5000:
        raise HTTPException(status_code=400, detail="Comment content too long (max 5000 characters)")
    
    # 检查 Persona 所有权
    persona = check_persona_ownership(db, user_persona_id, str(current_user.id))
    
    # 如果是回复，检查父评论是否存在
    if parent_id:
        parent_comment = db.query(Comment).filter(
            Comment.id == parent_id,
            Comment.event_id == event_id,
            Comment.is_deleted == False
        ).first()
        
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        # 增加父评论的回复计数
        parent_comment.reply_count += 1
    
    # 创建评论
    comment = Comment(
        user_id=current_user.id,
        user_persona_id=user_persona_id,
        event_id=event_id,
        content=content.strip(),
        parent_id=parent_id
    )

    db.add(comment)

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
    current_user: User = Depends(get_current_user),  # 必须登录
):
    """编辑自己的评论"""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.user_id == current_user.id,
        Comment.is_deleted == False
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # 验证内容
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
    current_user: User = Depends(get_current_user),  # 必须登录
):
    """删除自己的评论（软删除）"""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.user_id == current_user.id,
        Comment.is_deleted == False
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # 软删除
    comment.is_deleted = True
    comment.deleted_at = datetime.utcnow()
    comment.content = "[Deleted]"
    
    # 如果是回复，减少父评论的回复计数
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
    else:
        query = query.filter(Comment.parent_id == None)

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
