"""
WRHITW API Schemas
Pydantic model definitions
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import os

# Import category translation
from app.models import translate_category

# SQLite 用 string，PostgreSQL 用 UUID
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wrhitw.db")
IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    from typing import Union
    UUID = Union[str, object]  # type alias for pydantic
else:
    from uuid import UUID


# ==================== Event Schemas ====================

class EventBase(BaseModel):
    title: str
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []


class EventCreate(EventBase):
    """创建事件"""
    pass


class EventUpdate(BaseModel):
    """更新事件"""
    title: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    hot_score: Optional[float] = None


class EventResponse(EventBase):
    """Event Response"""
    id: UUID
    source_count: int
    view_count: int
    hot_score: float
    status: str
    created_at: datetime
    occurred_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Override to translate category"""
        data = {
            'id': str(obj.id) if hasattr(obj.id, '__str__') else obj.id,
            'title': obj.title,
            'summary': obj.summary,
            'category': translate_category(obj.category) if obj.category else None,
            'tags': obj.tags if hasattr(obj, 'tags') else [],
            'source_count': obj.source_count,
            'view_count': obj.view_count,
            'hot_score': float(obj.hot_score) if obj.hot_score else 0,
            'status': obj.status,
            'created_at': obj.created_at,
            'occurred_at': obj.occurred_at,
        }
        return cls(**data)


class EventListResponse(BaseModel):
    """事件列表响应"""
    items: List[EventResponse]
    total: int
    page: int
    page_size: int


# ==================== Source Schemas ====================

class SourceBase(BaseModel):
    name: str
    url: str
    bias_label: str = "center"
    bias_score: Optional[float] = None
    country: Optional[str] = None
    language: str = "en"


class SourceCreate(SourceBase):
    """创建信息源"""
    pass


class SourceResponse(SourceBase):
    """信息源响应"""
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Event Source Schemas ====================

class EventSourceBase(BaseModel):
    article_url: str
    article_title: str
    source_id: UUID


class EventSourceCreate(EventSourceBase):
    """创建事件 - 来源关联"""
    event_id: UUID


class EventSourceResponse(EventSourceBase):
    """事件 - 来源响应"""
    id: UUID
    published_at: Optional[datetime] = None
    fetched_at: datetime

    class Config:
        from_attributes = True


# ==================== AI Summary Schemas ====================

class PerspectiveSummary(BaseModel):
    """单视角摘要"""
    summary: str
    sources: List[str]
    key_focus: Optional[List[str]] = []


class AiSummaryCreate(BaseModel):
    """创建 AI 摘要"""
    event_id: UUID
    left_perspective: str
    center_perspective: str
    right_perspective: str


class AiSummaryResponse(BaseModel):
    """AI 摘要响应"""
    id: UUID
    event_id: UUID
    left_perspective: PerspectiveSummary
    center_perspective: PerspectiveSummary
    right_perspective: PerspectiveSummary
    generated_at: datetime

    class Config:
        from_attributes = True


# ==================== User Schemas ====================

class UserBase(BaseModel):
    email: Optional[str] = None
    display_name: Optional[str] = None


class UserCreate(UserBase):
    """创建用户"""
    password: str


class UserLogin(BaseModel):
    """用户登录"""
    email: str
    password: str


class UserResponse(UserBase):
    """用户响应"""
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Common Schemas ====================

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str
    code: Optional[str] = None
