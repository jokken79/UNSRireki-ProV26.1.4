"""Database configuration and session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from app.core.config import settings

# Naming convention for constraints (helps with migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    metadata = MetaData(naming_convention=convention)


# Create async engine
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine_args = {
    "url": settings.DATABASE_URL,
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}

# Add pool settings only for non-SQLite
if "sqlite" not in settings.DATABASE_URL:
    engine_args["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_args["max_overflow"] = settings.DATABASE_MAX_OVERFLOW

engine = create_async_engine(**engine_args)

if "sqlite" in settings.DATABASE_URL:
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency to get database session.

    Note: Endpoints should call await db.commit() explicitly after write operations.
    This dependency handles rollback on exceptions and session cleanup.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Import all models to register them
        from app.models import models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
