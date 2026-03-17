"""
WRHITW Comment System Models
评论系统数据库模型
"""

from sqlalchemy import Column, String, Text as _Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.types import UUID
import uuid


class Comment(Base):
    """评论表"""
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 外键关联
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user_persona_id = Column(UUID(as_uuid=True), ForeignKey('user_personas.id', ondelete='SET NULL'), nullable=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    thread_id = Column(UUID(as_uuid=True), ForeignKey('threads.id', ondelete='CASCADE'), nullable=True, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('comments.id', ondelete='CASCADE'), nullable=True)  # 回复评论
    
    # 评论内容
    content = Column(_Text, nullable=False)
    
    # 状态
    is_deleted = Column(Boolean, default=False)  # Soft delete
    is_edited = Column(Boolean, default=False)  # 是否编辑过
    
    # 互动统计
    like_count = Column(Integer, default=0)
    dislike_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    user = relationship("User", backref="comments")
    persona = relationship("UserPersona", backref="comments")
    event = relationship("Event", backref="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

    def to_dict(self, include_verified_badge=False):
        """转换为字典"""
        data = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "user_persona_id": str(self.user_persona_id) if self.user_persona_id else None,
            "persona_name": self.persona.persona_name if self.persona and not self.persona.is_deleted else "Deleted",
            "avatar_color": self.persona.avatar_color if self.persona else "gray",
            "event_id": str(self.event_id),
            "thread_id": str(self.thread_id) if self.thread_id else None,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "content": self.content,
            "is_deleted": self.is_deleted,
            "is_edited": self.is_edited,
            "like_count": self.like_count,
            "dislike_count": self.dislike_count,
            "reply_count": self.reply_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_verified_badge:
            data["is_verified"] = self.persona.is_verified if self.persona else False
        
        return data
