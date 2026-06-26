"""
Database Connection — Async SQLAlchemy Engine and Session Factory

Supports both SQLite (development) and MySQL (production) via DATABASE_URL.
The URL is read from .env so you can switch databases without code changes.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# Build engine from DATABASE_URL in .env
# SQLite needs connect_args for thread safety; MySQL uses connection pooling
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs: dict = {
    "echo": (settings.APP_ENV == "development"),
}

if _is_sqlite:
    # SQLite doesn't support pool_size/max_overflow with NullPool
    # check_same_thread=False is required for async SQLite
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
# --- UPDATED FOR SERVERLESS NEON POSTGRESQL ---
    engine_kwargs["pool_pre_ping"] = True   # Silently tests and replaces dead connections
    engine_kwargs["pool_recycle"] = 300     # Refresh connections every 5 minutes instead of 1 hour
    engine_kwargs["pool_size"] = 5          # Lower pool size prevents overwhelming serverless limits
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# Session factory creates new async sessions for each request
# expire_on_commit=False keeps objects usable after commit without re-querying
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    Every model inherits from this to get table creation and migration support.
    """
    pass


async def create_tables() -> None:
    """Create all tables if they don't exist (used for dev with SQLite)."""
    # Import models so they register with Base.metadata
    import app.db.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
