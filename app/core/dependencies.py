"""
Модуль: app.core.dependencies.py
=====================

Этот модуль содержит функции и объекты, которые используются в качестве зависимостей
в разных эндпоинтах приложения. Здесь реализованы:

- Получение асинхронной сессии базы данных.

Используется совместно с FastAPI, SQLAlchemy и системой JWT-аутентификации.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.business_logic_layer.services.task_service import TaskService
from app.core.app_config import Settings, get_settings
from app.core.db_config import get_db
from app.data_access_layer.repositories.task_repository import TaskRepository


async def get_db_session(session: AsyncSession = Depends(get_db)) -> AsyncSession:
    """
    Получение асинхронной сессии базы данных.
    Args:
        session (AsyncSession): Сессия SQLAlchemy, создаётся автоматически через Depends(get_db).
    Returns:
        AsyncSession: Асинхронная сессия SQLAlchemy для работы с БД.
    """
    return session


async def get_task_repository(
    session: AsyncSession = Depends(get_db_session),
) -> TaskRepository:
    return TaskRepository(session=session)


async def get_task_service(
    repository: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(repository=repository)
