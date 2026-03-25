"""
WRHITW User Persona Models
User persona system database models
"""

from sqlalchemy import Column, String, Text as _Text, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.types import UUID
import uuid


class UserPersona(Base):
    """User Personas Table"""
    __tablename__ = "user_personas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    persona_name = Column(String(100), nullable=False)  # e.g., "Iranian Civilian"
    avatar_color = Column(String(20), default='blue')  # Random color identifier
    is_verified = Column(Boolean, default=False)  # Whether there is a verified association
    
    # Soft delete fields
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="personas")
    verifications = relationship("EventStakeholderVerification", backref="persona")
    # comments = relationship("Comment", backref="persona")


class EventStakeholderVerification(Base):
    """Event-Persona-Stakeholder Verification Association Table"""
    __tablename__ = "event_stakeholder_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_persona_id = Column(UUID(as_uuid=True), ForeignKey('user_personas.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    stakeholder_id = Column(UUID(as_uuid=True), ForeignKey('stakeholders.id'), nullable=False)
    
    # Application information
    application_text = Column(_Text)
    proof_type = Column(String(50))
    proof_data = Column(_Text)

    # Review status
    status = Column(String(20), default='pending')  # pending, approved, rejected
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(_Text)

    # Uploaded proof files (JSON list of file paths)
    proof_files = Column(_Text)  # JSON array of uploaded file paths

    # AI review fields
    ai_review_score = Column(Integer)  # 0-100, AI confidence that application is legitimate
    ai_review_notes = Column(_Text)    # AI analysis text
    ai_flags = Column(_Text)           # JSON list of flags (e.g. ["too_short", "copy_paste"])

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    event = relationship("Event", backref="verifications")
    stakeholder = relationship("Stakeholder", backref="verifications")

    # Unique constraint: a persona can only have one verification per event
    __table_args__ = (
        UniqueConstraint('user_persona_id', 'event_id', name='uq_persona_event'),
    )


# Comment model is in a separate file, only adding foreign key reference notes here
# class Comment(Base):
#     """Comments Table (needs the following fields added)"""
#     __tablename__ = "comments"
#
#     # Existing fields...
#     user_persona_id = Column(UUID(as_uuid=True), ForeignKey('user_personas.id', ondelete='SET NULL'))
#     # Whether to show verified badge on comment, determined by querying EventStakeholderVerification
