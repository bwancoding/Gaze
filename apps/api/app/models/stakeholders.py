"""
WRHITW Stakeholder Models
Stakeholder verification system database models
"""

from sqlalchemy import Column, String, Text as _Text, Integer, Boolean, DateTime, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import UUID, JSONColumn
import uuid


class StakeholderType(Base):
    """Stakeholder Types Table (predefined)"""
    __tablename__ = "stakeholder_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Country", "Company", "Organization", "Group"
    description = Column(_Text)
    category = Column(String(50))  # geopolitics, technology, economy
    verification_required = Column(Boolean, default=True)
    verification_method = Column(String(200))  # e.g., "IP address", "Email domain", "Document upload"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Stakeholder(Base):
    """Stakeholders Table"""
    __tablename__ = "stakeholders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)  # e.g., "Iranian Civilians", "US Soldiers", "NVIDIA Employees"
    type_id = Column(UUID(as_uuid=True), ForeignKey('stakeholder_types.id'), nullable=False)
    description = Column(_Text)  # e.g., "Ordinary citizens living in Iran"
    category = Column(String(50))  # geopolitics, technology, economy
    verification_required = Column(Boolean, default=True)
    verification_method = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    # type = relationship("StakeholderType", backref="stakeholders")


class EventStakeholder(Base):
    """Event-Stakeholder Association Table"""
    __tablename__ = "event_stakeholders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    stakeholder_id = Column(UUID(as_uuid=True), ForeignKey('stakeholders.id'), nullable=False)
    relevance_score = Column(DECIMAL(3, 2), default=0.5)  # AI-determined relevance score 0-1
    perspective_summary = Column(_Text)  # AI-generated stakeholder perspective for this event
    key_concerns = Column(JSONColumn)  # ["concern1", "concern2"]
    is_ai_generated = Column(Boolean, default=False)  # Whether this was auto-created by AI
    status = Column(String(20), default='pending')  # pending, approved, rejected
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('event_id', 'stakeholder_id', name='uq_event_stakeholder'),
    )


class StakeholderVerification(Base):
    """Stakeholder Identity Verification Applications Table"""
    __tablename__ = "stakeholder_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    stakeholder_id = Column(UUID(as_uuid=True), ForeignKey('stakeholders.id'), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'))
    
    # Application information
    application_text = Column(_Text)  # User explanation of why they are a stakeholder
    proof_type = Column(String(50))  # ip_address, email, document, other
    proof_data = Column(_Text)  # Stored proof data (encrypted)

    # Review status
    status = Column(String(20), default='pending')  # pending, approved, rejected
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(_Text)  # Review notes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserStakeholderRole(Base):
    """User-Stakeholder Role Association Table (verified roles)"""
    __tablename__ = "user_stakeholder_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    stakeholder_id = Column(UUID(as_uuid=True), ForeignKey('stakeholders.id'), nullable=False)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True))
    
    # Metadata
    display_name = Column(String(255))  # Display name (can differ from stakeholder.name)
    badge_color = Column(String(20), default='blue')  # Badge color
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'stakeholder_id', name='uq_user_stakeholder'),
    )
