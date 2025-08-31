"""
Модуль: app.core.db_config
====================

Этот модуль отвечает за настройку подключения к базе данных для FastAPI-приложения,
используя SQLAlchemy с поддержкой асинхронных операций.

Функционал:
-----------
1. Создаёт асинхронный движок SQLAlchemy (`engine`) на основе настроек.
2. Настраивает фабрику сессий `AsyncSessionLocal` для работы с БД.
3. Предоставляет зависимость `get_db()` для корректной работы сессий в эндпоинтах.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from app.core.app_config import get_settings

# Кеш движка и фабрики сессий (один на приложение)
_engine: AsyncEngine | None = None
_async_session_local: async_sessionmaker[AsyncSession] | None = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency FastAPI для получения асинхронной сессии SQLAlchemy.

    Args:
        settings (Settings): Настройки приложения, получаем через Depends.

    Yields:
        AsyncSession: Экземпляр асинхронной сессии SQLAlchemy.
    """
    global _engine, _async_session_local

    settings = get_settings()

    # Инициализация движка и фабрики сессий при первом вызове
    if _engine is None:
        _engine = create_async_engine(
            settings.get_database_async_url,
            echo=settings.DEBUG
        )
    if _async_session_local is None:
        _async_session_local = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async with _async_session_local() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise