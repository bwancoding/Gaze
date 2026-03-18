"""
WRHITW Database Configuration
Database connection configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./wrhitw.db"
)

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()


def get_db():
    """Get database session (dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
