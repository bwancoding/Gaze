"""
Notification Model - User notifications for likes, replies, and verification status changes.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import UUID


class Notification(Base):
    """User notification record"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Type: like, dislike, reply, thread_reply, verification_approved, verification_rejected, verification_revoked
    type = Column(String(50), nullable=False)
    message = Column(String(500), nullable=False)
    link_url = Column(String(500))  # Frontend route, e.g. "/events/{id}/threads/{id}"

    is_read = Column(Boolean, default=False, index=True)

    # Optional context
    source_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    thread_id = Column(UUID(as_uuid=True), nullable=True)
    comment_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


def create_notification(db, user_id, type: str, message: str, link_url: str = None,
                        source_user_id=None, thread_id=None, comment_id=None):
    """Create a notification. Skips self-notifications."""
    if source_user_id and str(source_user_id) == str(user_id):
        return None

    notif = Notification(
        user_id=user_id,
        type=type,
        message=message,
        link_url=link_url,
        source_user_id=source_user_id,
        thread_id=thread_id,
        comment_id=comment_id,
    )
    db.add(notif)
    return notif
