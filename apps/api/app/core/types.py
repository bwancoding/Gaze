"""
Shared SQLAlchemy type decorators for SQLite/PostgreSQL compatibility.
"""

from sqlalchemy import String as _String, Text as _Text, DateTime, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY as PG_ARRAY, TIMESTAMP as PG_TIMESTAMP, JSONB
import json
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wrhitw.db")
IS_SQLITE = DATABASE_URL.startswith("sqlite")


class SQLiteUUID(TypeDecorator):
    """SQLite UUID type, stored as string."""
    impl = _String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value) if hasattr(value, '__str__') else value

    def process_result_value(self, value, dialect):
        return value


class SQLiteArray(TypeDecorator):
    """SQLite ARRAY type, stored as JSON string."""
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
        except Exception:
            return []


class SQLiteJSON(TypeDecorator):
    """SQLite JSON type, stored as JSON string."""
    impl = _Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return json.loads(value)
        except Exception:
            return None


if IS_SQLITE:
    def UUID(as_uuid=False):
        return SQLiteUUID(36)

    def ARRAY(item_type):
        return SQLiteArray()

    def TIMESTAMP(timezone=False):
        return DateTime()

    JSONColumn = SQLiteJSON
else:
    UUID = PG_UUID
    ARRAY = PG_ARRAY
    TIMESTAMP = PG_TIMESTAMP
    JSONColumn = JSONB
