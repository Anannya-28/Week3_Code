"""
Single source of truth for DB sessions.

Sync  → used by most endpoints (simple CRUD)
Async → used by checkout + payment flows (await external APIs + DB together)

WHY TWO SESSIONS:
Mixing sync SQLAlchemy with async routes causes event-loop blocking.
We keep sync for simple fast queries and async only where external
I/O is also involved (checkout, payments).
"""


from typing import AsyncIterator, Iterator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from core.config import settings

Base = declarative_base()




_sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

_SyncSession = sessionmaker(
    bind=_sync_engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Iterator[Session]:        
    """
    Sync session dependency — used by most routes via Depends(get_db).

    WHY Iterator[Session] not Session:
    This function uses `yield`, making it a generator.
    Generators return Iterator[YieldType], not the yielded type directly.
    Writing -> Session tells the IDE the function returns a Session object,
    which is wrong — it returns a generator that yields Session objects.
    FastAPI's Depends() unwraps the iterator automatically at runtime.
    """
    db = _SyncSession()
    try:
        yield db
    finally:
        db.close()


# Async engine 

_async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    echo=(settings.APP_ENV == "development"),
)

_AsyncSession = async_sessionmaker(
    bind=_async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # prevents lazy-load errors post-commit in async
)


async def get_async_db() -> AsyncIterator[AsyncSession]:   #  FIX — was -> AsyncSession
    """
    Async session dependency — used only by checkout + payment routes.

    WHY AsyncIterator[AsyncSession] not AsyncSession:
    This is an async generator (uses `yield` inside `async def`).
    Async generators return AsyncIterator[YieldType], not the yielded
    type itself. The IDE correctly warns when you annotate it as
    -> AsyncSession because that implies the coroutine resolves to
    an AsyncSession directly, which is false.
    FastAPI's Depends() unwraps the async iterator automatically.
    """
    async with _AsyncSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def create_all_tables() -> None:
    """Called once at startup to create tables that don't exist."""
    Base.metadata.create_all(bind=_sync_engine)