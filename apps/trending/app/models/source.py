"""
数据源模型 - sources 表
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Source(Base):
    """新闻数据源模型"""
    
    __tablename__ = "sources"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="媒体名称")
    url = Column(String(500), nullable=False, unique=True, comment="RSS URL")
    stance = Column(String(20), nullable=False, comment="政治立场：left, center-left, center, center-right, right")
    region = Column(String(50), nullable=False, comment="地区：us, uk, europe, asia, international")
    
    # 抓取配置
    priority = Column(String(10), default="P2", comment="优先级：P0, P1, P2")
    update_interval_minutes = Column(Integer, default=60, comment="更新间隔（分钟）")
    enabled = Column(Boolean, default=True, comment="是否启用")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="source")
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', priority='{self.priority}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "stance": self.stance,
            "region": self.region,
            "priority": self.priority,
            "update_interval_minutes": self.update_interval_minutes,
            "enabled": self.enabled,
        }
