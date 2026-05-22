"""
Alembic Environment Configuration — Async MySQL Support

This file configures Alembic to work with our async SQLAlchemy engine.
We use the run_async_migrations pattern to bridge Alembic's sync API
with our async database connection.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Import Base and ALL models so Alembic can detect them for autogenerate
# Every model must be imported here or Alembic won't see it
from app.db.mysql import Base
from app.db.models import User, Resume, JobApplication  # noqa: F401
from app.core.config import settings

# Alembic Config object — provides access to alembic.ini values
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate — Alembic compares this with the database
# to detect what tables/columns need to be created or modified
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — generates SQL without connecting to DB.
    Useful for reviewing migration SQL before applying.
    """
    url = settings.mysql_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "format"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    Execute migrations using the provided database connection.
    Called from within the async context.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Create an async engine and run migrations within its connection.
    This bridges Alembic's sync migration API with our async engine.
    """
    connectable = create_async_engine(settings.mysql_url)

    async with connectable.connect() as connection:
        # run_sync runs our sync migration function inside the async connection
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode — connects to DB and applies changes.
    Uses asyncio to support our async MySQL driver (aiomysql).
    """
    asyncio.run(run_async_migrations())


# Determine which mode to run in based on Alembic context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
