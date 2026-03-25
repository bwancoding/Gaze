"""
Request Log Model
Stores API request logs for monitoring and analytics
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index
from datetime import datetime, timezone
from app.core.database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    is_slow = Column(Boolean, default=False, index=True)
    user_id = Column(String(36), nullable=True)
    error_detail = Column(Text, nullable=True)

    __table_args__ = (
        Index('ix_request_logs_timestamp_path', 'timestamp', 'path'),
    )
