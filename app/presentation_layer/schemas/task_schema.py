from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, constr, field_validator

from app.data_access_layer.models.task_model import TaskStatus


class BaseSchema(BaseModel):
    """Базовая схема с настройкой from_attributes."""

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseSchema):
    """Базовая схема задачи."""

    title: Annotated[
        constr(min_length=1, max_length=150),
        Field(
            description="Название задачи",
            examples=["Сходить за продуктами", "Погулять с дочкой", "Выбросить мусор"],
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            description="Описание задачи",
            max_length=5000,
        ),
    ]

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title не может быть пустым или содержать только пробелы")
        return v


class TaskCreate(TaskBase):
    """Схема для создания задачи. title обязателен, description опционален."""


class TaskUpdate(BaseSchema):
    """Схема для частичного обновления задачи (PATCH)."""

    title: Annotated[
        constr(min_length=1, max_length=150) | None,
        Field(
            description="Новое название задачи",
            examples=["Сходить за продуктами", "Погулять с дочкой", "Выбросить мусор"],
            default=None,
        ),
    ]
    description: Annotated[
        str | None,
        Field(description="Новое описание задачи", max_length=5000, default=None),
    ]
    status: Annotated[
        TaskStatus | None, Field(description="Новый статус задачи", default=None)
    ]

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("title не может быть пустым или содержать только пробелы")
        return v


class TaskRead(TaskBase):
    """Схема для возврата задачи через API."""

    id: UUID
    status: TaskStatus


class TaskListResponse(BaseSchema):
    """Модель для возврата списка задач."""

    tasks: list[TaskRead]


class TaskDeleteResponse(BaseModel):
    """Модель ответа при успешном удалении задачи."""

    message: str = "Task deleted successfully"
