"""
文章模型 - articles 表
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Article(Base):
    """新闻文章模型"""
    
    __tablename__ = "articles"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, index=True, comment="所属事件 ID")
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, comment="数据源 ID")
    
    # 文章信息
    title = Column(String(500), nullable=False, comment="文章标题")
    summary = Column(Text, comment="文章摘要")
    content = Column(Text, comment="文章内容（可选）")
    url = Column(String(1000), nullable=False, unique=True, comment="文章 URL")
    
    # 时间信息
    published_at = Column(DateTime, nullable=False, index=True, comment="发布时间")
    fetched_at = Column(DateTime, default=datetime.utcnow, comment="抓取时间")
    
    # 热度相关
    heat_score = Column(Float, default=0.0, comment="文章热度分数")
    comment_count = Column(Integer, default=0, comment="评论数")
    share_count = Column(Integer, default=0, comment="分享数")
    
    # 处理状态
    is_processed = Column(Boolean, default=False, comment="是否已聚类处理")
    source_priority = Column(String(10), default="P2", comment="源优先级缓存")
    
    # 关系
    event = relationship("Event", back_populates="articles")
    source = relationship("Source", back_populates="articles")
    
    # 索引
    __table_args__ = (
        Index('idx_article_published_source', 'published_at', 'source_id'),
        Index('idx_article_heat', 'heat_score', 'published_at'),
        Index('idx_article_url', 'url'),
    )
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source_id={self.source_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "source_id": self.source_id,
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "heat_score": self.heat_score,
            "is_processed": self.is_processed,
        }
