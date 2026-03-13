"""
事件聚类模型 - events 表
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB


class Event(Base):
    """事件聚类模型 - 将相关文章聚合为事件"""
    
    __tablename__ = "events"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True, comment="首发媒体 ID")
    
    # 事件信息
    title = Column(String(500), nullable=False, comment="事件标题")
    summary = Column(Text, comment="事件摘要")
    keywords = Column(JSONB, default=list, comment="关键词列表")
    
    # 热度相关
    heat_score = Column(Float, default=0.0, index=True, comment="热度分数")
    article_count = Column(Integer, default=0, comment="文章数量")
    media_count = Column(Integer, default=0, comment="报道媒体数量")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="创建时间")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="最后更新时间")
    
    # 关系
    source = relationship("Source", back_populates="events")
    articles = relationship("Article", back_populates="event", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_event_heat_created', 'heat_score', 'created_at'),
        Index('idx_event_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title[:50]}...', heat={self.heat_score})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "keywords": self.keywords or [],
            "heat_score": self.heat_score,
            "article_count": self.article_count,
            "media_count": self.media_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }
    
    @property
    def unique_media_count(self) -> int:
        """获取独特媒体数量"""
        if not self.articles:
            return 0
        return len(set(a.source_id for a in self.articles))
