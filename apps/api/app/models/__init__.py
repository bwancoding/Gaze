"""
WRHITW Database Models
数据库模型定义
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Source(Base):
    """信息源表"""
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
    """事件表"""
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512), nullable=False)
    summary = Column(Text)
    description = Column(Text)
    category = Column(String(50))
    tags = Column(ARRAY(String))
    occurred_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    hot_score = Column(DECIMAL(5, 2), default=0)
    view_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    status = Column(String(20), default='active')
    source_count = Column(Integer, default=0)


class EventSource(Base):
    """事件 - 来源关联表"""
    __tablename__ = "event_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey('sources.id', ondelete='CASCADE'), nullable=False)
    article_url = Column(String(1024), nullable=False)
    article_title = Column(String(512), nullable=False)
    article_content = Column(Text)
    article_summary = Column(Text)
    published_at = Column(TIMESTAMP(timezone=True))
    fetched_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    sentiment_score = Column(DECIMAL(3, 2))
    word_count = Column(Integer)

    __table_args__ = (
        UniqueConstraint('event_id', 'source_id', name='uq_event_source'),
    )


class AiSummary(Base):
    """AI 摘要表"""
    __tablename__ = "ai_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), unique=True, nullable=False)
    left_perspective = Column(Text, nullable=False)
    center_perspective = Column(Text, nullable=False)
    right_perspective = Column(Text, nullable=False)
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
    """用户表"""
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


class ReadingHistory(Base):
    """阅读历史表"""
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
    """收藏表"""
    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    notes = Column(Text)

    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', name='uq_user_bookmark'),
    )
