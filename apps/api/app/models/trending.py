"""
Trending Models - Trending-related data models

Uses trending_ prefix to avoid conflicts with main events/sources tables.
Trending pipeline operates independently: fetch -> store articles -> cluster -> calculate heat score -> serve API.
"""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
    Text, Boolean, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.types import JSONColumn
from datetime import datetime


class TrendingSource(Base):
    """News Data Sources"""
    __tablename__ = "trending_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    stance = Column(String(20), nullable=False, default="center")
    region = Column(String(50), nullable=False, default="international")
    priority = Column(String(10), default="P2")
    update_interval_minutes = Column(Integer, default=60)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    articles = relationship("TrendingArticle", back_populates="source", cascade="all, delete-orphan")
    events = relationship("TrendingEvent", back_populates="source")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "stance": self.stance,
            "region": self.region,
            "priority": self.priority,
            "enabled": self.enabled,
        }


class TrendingEvent(Base):
    """Event Clustering - Aggregates related articles into events"""
    __tablename__ = "trending_events"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("trending_sources.id"), nullable=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    keywords = Column(JSONColumn, default=list)
    category = Column(String(50))
    heat_score = Column(Float, default=0.0, index=True)
    status = Column(String(20), default='raw')  # raw, promoted, rejected, archived
    article_count = Column(Integer, default=0)
    media_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source = relationship("TrendingSource", back_populates="events")
    articles = relationship("TrendingArticle", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_trending_event_heat_created', 'heat_score', 'created_at'),
    )

    @property
    def unique_media_count(self) -> int:
        if not self.articles:
            return 0
        return len(set(a.source_id for a in self.articles))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "keywords": self.keywords or [],
            "category": self.category,
            "heat_score": self.heat_score,
            "status": self.status,
            "article_count": self.article_count,
            "media_count": self.media_count,
            "sources": list(set(
                a.source.name for a in self.articles if a.source
            )) if self.articles else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class TrendingArticle(Base):
    """News Articles"""
    __tablename__ = "trending_articles"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("trending_events.id"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("trending_sources.id"), nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    url = Column(String(1000), nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    heat_score = Column(Float, default=0.0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    is_processed = Column(Boolean, default=False)
    source_priority = Column(String(10), default="P2")

    event = relationship("TrendingEvent", back_populates="articles")
    source = relationship("TrendingSource", back_populates="articles")

    __table_args__ = (
        Index('idx_trending_article_published_source', 'published_at', 'source_id'),
        Index('idx_trending_article_heat', 'heat_score', 'published_at'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "source_id": self.source_id,
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "heat_score": self.heat_score,
            "source_name": self.source.name if self.source else None,
        }
