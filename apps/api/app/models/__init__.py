"""
WRHITW Database Models
Database models for multi-perspective news aggregation
"""

from sqlalchemy import Column, String, Text as _Text, Integer, Boolean, DateTime, DECIMAL, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import UUID, ARRAY, TIMESTAMP, JSONColumn
import uuid


# Category translation mapping (Chinese to English)
CATEGORY_TRANSLATIONS = {
    '环境': 'Environment',
    '财经': 'Economy',
    '科技': 'Technology',
    '政治': 'Politics',
}

def translate_category(category: str) -> str:
    """Translate Chinese category to English"""
    return CATEGORY_TRANSLATIONS.get(category, category)


class Source(Base):
    """Sources Table"""
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)
    logo_url = Column(String(512))
    bias_label = Column(String(20), default='center')
    bias_score = Column(DECIMAL(3, 2))
    country = Column(String(2))
    language = Column(String(10), default='en')
    credibility_score = Column(DECIMAL(3, 2))
    rss_feed_url = Column(String(512))
    api_endpoint = Column(String(512))
    scrape_interval = Column(Integer, default=900)
    is_active = Column(Boolean, default=True)
    last_scraped_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class Event(Base):
    """Event Table"""
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512), nullable=False)
    summary = Column(_Text)
    description = Column(_Text)
    category = Column(String(50))
    tags = Column(ARRAY(String))
    occurred_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    archived_at = Column(TIMESTAMP(timezone=True))
    closed_at = Column(TIMESTAMP(timezone=True))
    hot_score = Column(DECIMAL(10, 2), default=0)
    view_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    status = Column(String(20), default='active', index=True)  # candidate, active(published), archived, closed
    source_count = Column(Integer, default=0)

    # Lifecycle timestamps for auto-archiving
    published_at = Column(TIMESTAMP(timezone=True))  # When event was published to Stories
    last_activity_at = Column(TIMESTAMP(timezone=True))  # Last article/comment/thread/vote activity

    # Deep analysis fields (populated by AI)
    background = Column(_Text)  # Event background/context
    cause_chain = Column(JSONColumn)  # [{cause, description, sources}]
    impact_analysis = Column(JSONColumn)  # [{dimension, impact, affected_groups}]
    timeline_data = Column(JSONColumn)  # [{timestamp, title, description, sources}]
    stakeholder_perspectives = Column(JSONColumn)  # [{stakeholder_id, name, perspective, key_arguments}]
    source_article_count = Column(Integer, default=0)
    trending_origin_id = Column(Integer, nullable=True)  # Reference to trending source (no FK - table may not exist)

    __table_args__ = (
        Index('ix_events_hot_score', 'hot_score'),
        Index('ix_events_created_at', 'created_at'),
        Index('ix_events_category', 'category'),
    )


class EventSource(Base):
    """Event-Source Association Table"""
    __tablename__ = "event_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey('sources.id', ondelete='CASCADE'), nullable=False)
    article_url = Column(String(1024), nullable=False)
    article_title = Column(String(512), nullable=False)
    article_content = Column(_Text)
    article_summary = Column(_Text)
    published_at = Column(TIMESTAMP(timezone=True))
    fetched_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    sentiment_score = Column(DECIMAL(3, 2))
    word_count = Column(Integer)

    __table_args__ = (
        UniqueConstraint('event_id', 'source_id', name='uq_event_source'),
    )


class AiSummary(Base):
    """AI Summaries Table"""
    __tablename__ = "ai_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), unique=True, nullable=False)
    left_perspective = Column(_Text, nullable=False)
    center_perspective = Column(_Text, nullable=False)
    right_perspective = Column(_Text, nullable=False)
    left_sources = Column(ARRAY(UUID(as_uuid=True)))
    center_sources = Column(ARRAY(UUID(as_uuid=True)))
    right_sources = Column(ARRAY(UUID(as_uuid=True)))
    model_name = Column(String(100))
    prompt_version = Column(String(20))
    token_count = Column(Integer)
    quality_score = Column(DECIMAL(3, 2))
    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True))


class User(Base):
    """Users Table"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True)
    phone = Column(String(20), unique=True)
    password_hash = Column(String(255))
    provider = Column(String(50))
    provider_id = Column(String(255))
    display_name = Column(String(100))
    avatar_url = Column(String(512))
    preferred_language = Column(String(10), default='zh-CN')
    preferred_categories = Column(ARRAY(String))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def check_password(self, password: str) -> bool:
        """
        Verify password

        Args:
            password: Plain text password

        Returns:
            True if the password matches, otherwise False
        """
        from app.utils.security import verify_password
        return verify_password(password, self.password_hash)


class ReadingHistory(Base):
    """Reading History Table"""
    __tablename__ = "reading_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    read_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    read_duration = Column(Integer)
    device_type = Column(String(20))

    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', name='uq_user_event'),
    )


class Bookmark(Base):
    """Bookmarks Table"""
    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    notes = Column(_Text)

    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', name='uq_user_bookmark'),
    )
