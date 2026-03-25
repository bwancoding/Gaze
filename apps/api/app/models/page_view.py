"""
Page View Model
Stores frontend page view events for analytics
"""

from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime, timezone
from app.core.database import Base


class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    path = Column(String(500), nullable=False, index=True)
    referrer = Column(String(1000), nullable=True)
    user_agent = Column(String(500), nullable=True)
    client_ip = Column(String(45), nullable=True)
    screen_width = Column(Integer, nullable=True)
    user_id = Column(String(36), nullable=True)
