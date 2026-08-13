"""Database setup for SQLAlchemy and SQL Server access."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


@lru_cache(maxsize=1)
def get_engine():
    """Create and cache the SQLAlchemy engine."""

    settings = get_settings()
    engine_kwargs = {"pool_pre_ping": True, "future": True}
    engine_kwargs["pool_recycle"] = 3600
    return create_engine(settings.database_url, **engine_kwargs)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Return a cached session factory."""

    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def get_session() -> Session:
    """Create a new database session."""

    return get_session_factory()()
