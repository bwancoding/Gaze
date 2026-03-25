"""
Error Log Model
Stores unhandled exceptions for debugging and monitoring
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.core.database import Base


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    method = Column(String(10), nullable=True)
    path = Column(String(500), nullable=True)
    client_ip = Column(String(45), nullable=True)
    error_type = Column(String(200), nullable=True)
    error_message = Column(Text, nullable=True)
    traceback = Column(Text, nullable=True)
    user_id = Column(String(36), nullable=True)
