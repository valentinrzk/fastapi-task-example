from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from src.data_access_layer.models.base_model import Base

# Тип для моделей
T = TypeVar("T", bound=Base)


class BaseRepository[T]:
    """Универсальный базовый репозиторий для CRUD-операций."""

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        """
        Args:
            session (AsyncSession): асинхронная сессия SQLAlchemy.
            model (Type[T]): модель, с которой работает репозиторий.
        """
        self.session = session
        self.model = model

    # -------------------- CREATE --------------------
    async def create(self, obj: T) -> T:
        """Создание новой сущности."""
        self.session.add(obj)
        await self.session.flush()
        return obj

    # -------------------- READ --------------------
    async def get_by_id(self, obj_id: UUID) -> T | None:
        """Получение сущности по UUID."""
        return await self.session.get(self.model, obj_id)

    async def get_by_field(self, field_name: str, value: Any) -> T | None:
        """Получение сущности по значению конкретного поля."""
        field: InstrumentedAttribute[Any] = getattr(self.model, field_name)
        stmt = select(self.model).where(field == value)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list(self, **filters: Any) -> list[T]:
        stmt = select(self.model)
        for key, value in filters.items():
            if value is not None:  # фильтруем только те, что реально заданы
                field: InstrumentedAttribute[Any] = getattr(self.model, key)
                stmt = stmt.where(field == value)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # -------------------- UPDATE --------------------
    async def update(self, obj: T, **kwargs: Any) -> T:
        """Обновление полей сущности."""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.add(obj)
        await self.session.flush()
        return obj

    # -------------------- DELETE --------------------
    async def delete(self, obj: T) -> None:
        """Удаление сущности из базы."""
        await self.session.delete(obj)
        await self.session.flush()
