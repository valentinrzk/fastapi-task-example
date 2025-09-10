"""
Модуль: app.presentation_layer.schemas.task_schema
=================================================

Модуль содержит Pydantic-схемы для валидации, сериализации и документации
объектов "Task" в REST API. Поддерживается полное, частичное обновление,
а также генерация примеров данных для Swagger.
"""

from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.data_access_layer.models.task_model import TaskStatus


class BaseSchema(BaseModel):
    """Базовая схема, включающая общие настройки для всех моделей."""

    model_config = {"from_attributes": True}


class TaskBase(BaseSchema):
    """Базовая модель задачи, содержит общие поля для всех операций."""

    title: Annotated[
        str,
        Field(
            description="Название задачи",
            max_length=100,
            examples=["Сходить за продуктами", "Погулять с дочкой", "Выбросить мусор"],
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description="Описание задачи",
            max_length=1000,
        ),
    ]


class TaskCreate(TaskBase):
    """
    Модель для создания новой задачи.

    Наследует `title` и `description` от `TaskBase`.
    """


class TaskUpdate(BaseModel):
    """
    Модель для частичного обновления задачи (PATCH).

    Все поля являются необязательными.
    """

    title: Annotated[
        str,
        Field(
            description="Новое название задачи",
            max_length=100,
            examples=["Сходить за продуктами", "Погулять с дочкой", "Выбросить мусор"],
            default=None,
        ),
    ]

    description: Annotated[
        str | None,
        Field(description="Новое описание задачи", max_length=1000, default=None),
    ]
    status: Annotated[
        TaskStatus | None, Field(description="Новый статус задачи", default=None)
    ]


class TaskRead(TaskBase):
    """
    Модель для возврата задачи в API-ответах.

    Наследует `title` и `description` от `TaskBase`.
    """

    id: UUID
    status: TaskStatus


class TaskDeleteResponse(BaseModel):
    message: str = "Task deleted successfully"
