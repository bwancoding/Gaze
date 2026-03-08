"""
WRHITW Database Models
Database models for multi-perspective news aggregation
"""

from sqlalchemy import Column, String, Text as _Text, Integer, Boolean, DateTime, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY as PG_ARRAY, TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import os

# 根据数据库类型选择兼容的类型
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wrhitw.db")
IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    from sqlalchemy import String as _String
    from sqlalchemy import TypeDecorator
    import json
    
    class SQLiteUUID(TypeDecorator):
        """SQLite UUID 类型，存储为字符串"""
        impl = _String
        cache_ok = True
        
        def process_bind_param(self, value, dialect):
            if value is None:
                return value
            return str(value) if hasattr(value, '__str__') else value
        
        def process_result_value(self, value, dialect):
            return value
    
    class SQLiteArray(TypeDecorator):
        """SQLite ARRAY 类型，存储为 JSON 字符串"""
        impl = _Text
        cache_ok = True
        
        def process_bind_param(self, value, dialect):
            if value is None:
                return value
            return json.dumps(value) if isinstance(value, list) else value
        
        def process_result_value(self, value, dialect):
            if value is None:
                return []
            try:
                return json.loads(value)
            except:
                return []
    
    def UUID(as_uuid=False):
        return SQLiteUUID(36)
    def ARRAY(item_type):
        return SQLiteArray()
    def TIMESTAMP(timezone=False):
        return DateTime()
else:
    UUID = PG_UUID
    ARRAY = PG_ARRAY
    TIMESTAMP = PG_TIMESTAMP


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
    hot_score = Column(DECIMAL(5, 2), default=0)
    view_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    status = Column(String(20), default='active')  # active, archived, closed
    source_count = Column(Integer, default=0)


class EventSource(Base):
    """事件 - 来源关联表"""
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
    """AI 摘要表"""
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

    def check_password(self, password: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            
        Returns:
            True 如果密码匹配，否则 False
        """
        from app.utils.security import verify_password
        return verify_password(password, self.password_hash)


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
    notes = Column(_Text)

    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', name='uq_user_bookmark'),
    )
