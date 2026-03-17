"""
User Likes/Dislikes tracking model.
Prevents duplicate votes and supports toggle (like/dislike/cancel).
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import UUID
import uuid


class UserLike(Base):
    """
    Tracks user votes (like/dislike) on threads and comments.
    Each user can only have one vote per target (thread or comment).
    """
    __tablename__ = "user_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Polymorphic target: either thread_id OR comment_id is set
    thread_id = Column(UUID(as_uuid=True), ForeignKey('threads.id', ondelete='CASCADE'), nullable=True, index=True)
    comment_id = Column(UUID(as_uuid=True), ForeignKey('comments.id', ondelete='CASCADE'), nullable=True, index=True)

    # Vote type: 'like' or 'dislike'
    vote_type = Column(String(10), nullable=False)  # 'like' or 'dislike'

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # Each user can only vote once per thread
        UniqueConstraint('user_id', 'thread_id', name='uq_user_thread_vote'),
        # Each user can only vote once per comment
        UniqueConstraint('user_id', 'comment_id', name='uq_user_comment_vote'),
    )
