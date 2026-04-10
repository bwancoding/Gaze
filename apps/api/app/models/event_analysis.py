"""
Event Analysis Model - AI-generated deep analysis for events
Replaces the old left/center/right AiSummary with stakeholder-based perspectives
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import UUID, JSONColumn
import uuid


class EventAnalysis(Base):
    """AI-generated deep analysis for an event"""
    __tablename__ = "event_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Deep analysis content
    background = Column(Text)  # Event background/context
    cause_chain = Column(JSONColumn)  # [{cause, description, sources}]
    impact_analysis = Column(JSONColumn)  # [{dimension, impact, affected_groups}]
    timeline = Column(JSONColumn)  # [{timestamp, title, description, sources}]

    # Stakeholder perspectives (dynamic, not fixed left/center/right)
    stakeholder_perspectives = Column(JSONColumn)  # [{stakeholder_id, stakeholder_name, perspective_text, key_arguments, sources_cited}]
    disputed_claims = Column(JSONColumn)  # [{claim, disputed_by, evidence}]

    # Metadata
    model_name = Column(String(100))
    quality_score = Column(DECIMAL(3, 2))
    generated_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)

    # Generation lifecycle tracking (pending / done / failed)
    status = Column(String(20), default='pending')
    last_attempt_at = Column(DateTime)
    attempt_count = Column(Integer, default=0)
    error_message = Column(Text)

    def to_dict(self):
        return {
            "id": str(self.id),
            "event_id": str(self.event_id),
            "background": self.background,
            "cause_chain": self.cause_chain or [],
            "impact_analysis": self.impact_analysis or [],
            "timeline": self.timeline or [],
            "stakeholder_perspectives": self.stakeholder_perspectives or [],
            "disputed_claims": self.disputed_claims or [],
            "model_name": self.model_name,
            "quality_score": float(self.quality_score) if self.quality_score else None,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "status": self.status,
            "attempt_count": self.attempt_count or 0,
        }
