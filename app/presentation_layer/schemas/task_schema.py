from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.data_access_layer.models.task_model import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(
        ...,
        description="Название задачи",
        max_length=100,
        examples=["Сходить за продуктами", "Погулять с дочкой", "Выбросить мусор"],
    )

    description: Optional[str] = Field(
        None,
        description="Описание задачи",
        max_length=1000
    )


class TaskCreate(TaskBase):
    pass  # Для создания достаточно title и description


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        description="Новое название",
        max_length=100
    )
    description: Optional[str] = Field(
        None,
        description="Новое описание",
        max_length=1000
    )
    status: Optional[TaskStatus] = None


class TaskRead(TaskBase):
    id: UUID
    status: TaskStatus

    class Config:
        orm_mode = True  # Позволяет Pydantic читать данные из SQLAlchemy моделей
