from typing import Literal
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from src.core import settings


Category = Literal[
    "food", "transport", "shopping", "entertainment",
    "health", "bills", "education", "other"
]
_engine: Engine | None = None

def get_engine() -> Engine:
    """Get or create a cached SQLAlchemy engine for PostgreSQL."""
    global _engine
    if _engine is None:
        url = settings.get("DATABASE_URL")
        if not url:
            raise ValueError("DATABASE_URL environment variable is not set.")
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine