"""Database connection and session management for PostgreSQL."""
from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from domain.config import DATABASE_URL


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""
    pass


_engine: async_sessionmaker | None = None


def get_engine() -> async_sessionmaker:
    """Возвращает async sessionmaker. Одиночка — переиспользует движок."""
    global _engine
    if _engine is None:
        _engine = async_sessionmaker(
            create_async_engine(
                DATABASE_URL,
                echo=os.getenv("DB_ECHO", "0") == "1",
                pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
                max_overflow=10,
            ),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения AsyncSession."""
    engine = get_engine()
    async with engine() as session:
        yield session


async def init_db() -> None:
    """Создать все таблицы (вызывать в начале приложения)."""
    from infrastructure.postgres.db import Base  # noqa: F811
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Закрыть подключения."""
    global _engine
    if _engine is not None:
        _engine.sync_engine.dispose()
        _engine = None
