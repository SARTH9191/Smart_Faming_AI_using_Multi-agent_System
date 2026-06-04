"""
Database Session Factory — Async SQLAlchemy + PostgreSQL
Connection pooling configured per postgres-best-practices skill.
"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
import os


# ── Base class for all ORM models ──────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Engine & Session Factory (lazy-init) ───────────────────────────
_engine = None
_async_session_factory = None


def _get_database_url() -> str:
    """
    Read DATABASE_URL from env.
    Converts 'postgresql://' to 'postgresql+asyncpg://' for async driver.
    """
    url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:farming123@localhost:5432/smart_farming",
    )
    # Ensure async driver prefix
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _get_database_url(),
            # ── Connection pool (postgres-best-practices: conn-pool-sizing) ──
            pool_size=5,
            max_overflow=15,       # up to 20 total connections
            pool_timeout=30,       # wait max 30s for a connection
            pool_recycle=1800,     # recycle connections every 30 min
            pool_pre_ping=True,    # verify connection is alive before use
            echo=False,            # set True for SQL debug logging
        )
    return _engine


def get_session_factory():
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_factory


# ── Dependency for FastAPI ─────────────────────────────────────────
async def get_db() -> AsyncSession:
    """
    FastAPI dependency — yields an async session, auto-closes after request.
    Usage:
        @app.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_context():
    """
    Context-manager variant for use outside FastAPI request cycle
    (e.g., inside agents, startup tasks).
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Lifecycle helpers ──────────────────────────────────────────────
async def init_db():
    """
    Create all tables (use only for dev/testing — Alembic handles prod).
    """
    from core.db_models import Base as _  # noqa — ensure models are loaded
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Dispose engine on shutdown."""
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
