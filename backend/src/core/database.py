"""Database connection and session management for the financial assistant."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from contextlib import contextmanager
from src.models import Base


def get_database_url():
    """Get database URL from settings."""
    return settings.get("DATABASE_URL", "sqlite:///./financial_assistant.db")


def get_engine():
    """Get database engine with proper configuration."""
    database_url = get_database_url()
    # For PostgreSQL, we don't need the sqlite-specific connect_args
    if "postgresql" in database_url or "postgres" in database_url:
        return create_engine(database_url)
    else:
        # For SQLite, we need the check_same_thread option
        return create_engine(database_url, connect_args={"check_same_thread": False})


# Create database engine
engine = get_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)