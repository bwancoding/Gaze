"""
Thread Model - Reddit-style discussion threads within events
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import UUID, JSONColumn
import uuid


class Thread(Base):
    """Discussion thread within an event"""
    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    user_persona_id = Column(UUID(as_uuid=True), ForeignKey('user_personas.id', ondelete='SET NULL'), nullable=True)

    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSONColumn)  # ["tag1", "tag2"]

    # Moderation
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    # Stats
    view_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    dislike_count = Column(Integer, default=0)

    # Optional stakeholder filter
    stakeholder_filter_tag = Column(UUID(as_uuid=True), ForeignKey('stakeholders.id', ondelete='SET NULL'), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "event_id": str(self.event_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "user_persona_id": str(self.user_persona_id) if self.user_persona_id else None,
            "title": self.title,
            "content": self.content,
            "tags": self.tags or [],
            "is_pinned": self.is_pinned,
            "is_locked": self.is_locked,
            "is_deleted": self.is_deleted,
            "view_count": self.view_count,
            "reply_count": self.reply_count,
            "like_count": self.like_count,
            "dislike_count": self.dislike_count or 0,
            "stakeholder_filter_tag": str(self.stakeholder_filter_tag) if self.stakeholder_filter_tag else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
