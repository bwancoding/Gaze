"""
WRHITW Comment System API
评论系统 API 接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.security import HTTPBasic
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import secrets

from app.core.database import get_db
from app.models import User  # User 在 __init__.py 中
from app.models.comments import Comment
from app.models.personas import UserPersona, EventStakeholderVerification

router = APIRouter(prefix="/api/comments", tags=["Comments"])

# 认证
security = HTTPBasic()


def get_current_user(
    credentials=Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    from app.models import User
    from app.utils.security import verify_password
    
    user = db.query(User).filter(User.email == credentials.username).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # 使用 bcrypt 验证密码
    if verify_password(credentials.password, user.password_hash):
        return user
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


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
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取事件的所有评论（支持回复）"""
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
    
    comments = query.order_by(desc(Comment.created_at)).offset(offset).limit(limit).all()
    
    return {
        "items": [
            {
                **comment.to_dict(include_verified_badge=True),
                "is_verified": check_verified_status(db, str(comment.user_persona_id), event_id) if comment.user_persona_id else False
            }
            for comment in comments
        ],
        "total": query.count()
    }


@router.post("")
def create_comment(
    event_id: str = Body(..., embed=True),
    user_persona_id: str = Body(..., embed=True),
    content: str = Body(..., embed=True),
    parent_id: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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


@router.post("/{comment_id}/like")
def like_comment(
    comment_id: str,
    action: str = Query("like", description="like or dislike"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """点赞/点踩评论（简化版：只增加计数，不记录用户）"""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if action == "like":
        comment.like_count += 1
    elif action == "dislike":
        comment.dislike_count += 1
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'like' or 'dislike'")
    
    db.commit()
    
    return {
        "message": f"Comment {action}d successfully",
        "like_count": comment.like_count,
        "dislike_count": comment.dislike_count
    }
