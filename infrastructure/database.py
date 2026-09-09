"""Database connection and session management."""
from __future__ import annotations

import os
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from domain.config import DATABASE_URL, DATABASE_URL_SYNC


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass


_engine: Optional[async_sessionmaker] = None
_engine_sync: Optional[object] = None


def get_engine() -> async_sessionmaker:
    """Возвращает sessionmaker для async сессий."""
    global _engine
    if _engine is None:
        engine = create_async_engine(
            DATABASE_URL,
            echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            pool_pre_ping=True,
        )
        _engine = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return _engine


def get_sync_engine():
    """Возвращает sync engine для миграций и операций вне async."""
    global _engine_sync
    if _engine_sync is None:
        from sqlalchemy import create_engine
        _engine_sync = create_engine(DATABASE_URL_SYNC)
    return _engine_sync


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения AsyncSession."""
    engine = get_engine()
    async with engine() as session:
        yield session


async def init_db() -> None:
    """Инициализирует базу: создаёт все таблицы."""
    from infrastructure.database import Base
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Закрывает подключения."""
    global _engine, _engine_sync
    if _engine:
        _engine.sync_engine.dispose()
        _engine = None
    if _engine_sync:
        _engine_sync.dispose()
        _engine_sync = None
