"""
Модуль: src.data_access_layer.models.base
====================

Модуль содержит SQLAlchemy-модель `Task` и перечисление `TaskStatus`,
которые используются для управления задачами в системе.

Сущности:
---------
- `TaskStatus` — перечисление возможных статусов задачи.
- `Task` — ORM-модель задачи, которая хранит основную информацию
  и текущий статус в базе данных.

Основное назначение:
--------------------
Модуль используется в слое DAL (Data Access Layer) и описывает,
как сущность задачи хранится в базе данных. Модель совместима
с SQLAlchemy ORM и используется репозиториями и сервисами.
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.data_access_layer.models.base_model import Base


class TaskStatus(str, enum.Enum):
    """Перечисление возможных статусов задачи.

    Атрибуты:
        CREATED (str): Задача создана, но ещё не взята в работу.
        IN_PROGRESS (str): Задача находится в процессе выполнения.
        DONE (str): Задача завершена.
    """

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    """Модель задачи для хранения в базе данных.

    Представляет задачу с уникальным идентификатором, названием,
    описанием, текущим статусом и временными метками создания/обновления.

    Атрибуты:
        id (UUID): Уникальный идентификатор задачи (генерируется автоматически).
        title (str): Название задачи (обязательно).
        description (str): Дополнительное описание задачи (опционально).
        status (TaskStatus): Текущий статус задачи.
        created_at (datetime): Дата и время создания задачи.
        updated_at (datetime): Дата и время последнего обновления задачи.
    """

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        doc="Уникальный идентификатор задачи",
    )

    title: Mapped[str] = mapped_column(
        String(150), nullable=False, doc="Название задачи"
    )

    description: Mapped[str] = mapped_column(Text, nullable=True, doc="Описание задачи")

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.CREATED,
        doc="Статус задачи",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        doc="Дата создания задачи (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        doc="Дата последнего обновления задачи (UTC)",
    )
