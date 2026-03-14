"""
Модуль task_service.py
======================

Модуль содержит сервис для работы с задачами (Task).
Сервис реализует бизнес-логику для CRUD-операций:
создание, получение, обновление, удаление и смену статуса задачи.

Сервис использует TaskRepository для доступа к базе данных
и управляет бизнес-правилами и проверками.
"""

# from typing import Optional
from uuid import UUID

from src.core.exceptions import BusinessRuleError, NotFoundError
from src.data_access_layer.models.task_model import Task, TaskStatus
from src.data_access_layer.repositories.task_repository import TaskRepository


class TaskService:
    """Сервисный слой для работы с задачами."""

    def __init__(self, repository: TaskRepository) -> None:
        """
        Args:
            repository (TaskRepository): Репозиторий для работы с БД.
        """
        self.repo = repository

    # -------------------- CREATE --------------------
    async def create_task(self, title: str, description: str | None = None) -> Task:
        """Создание новой задачи.

        Args:
            title (str): Название задачи
            description (Optional[str]): Описание задачи

        Returns:
            Task: Созданная задача
        """
        # Бизнес-правило: Название задачи не может быть пустым.
        await self.ensure_title_is_not_empty(title)

        # Бизнес-правило: Название задачи должно быть уникальным
        await self.ensure_unique_title(title)

        # Явно ставим дефолтный статус
        task = Task(title=title, description=description, status=TaskStatus.CREATED)

        await self.repo.create(task)
        return task

    # -------------------- READ --------------------
    async def get_task(self, task_id: UUID) -> Task:
        """Получение задачи по id.

        Args:
            task_id (UUID): Идентификатор задачи

        Returns:
            Task: Задача

        Raises:
            NotFoundException: Если задача не найдена
        """
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found")
        return task

    async def list_tasks(self, status: TaskStatus | None = None) -> list[Task]:
        """Получение списка задач, с опциональной фильтрацией по статусу."""
        return await self.repo.list(status=status)

    # -------------------- UPDATE --------------------
    async def update_task(
        self,
        task_id: UUID,
        title: str | None = None,
        description: str | None = None,
        status: TaskStatus | None = None,
    ) -> Task:
        """Обновление задачи по id с проверкой бизнес-правил."""
        task = await self.get_task(task_id)  # бросит NotFoundException, если нет

        if title is not None:
            await self.ensure_title_is_not_empty(title)

            existing = await self.repo.get_by_title(title)
            if existing and existing.id != task.id:
                raise BusinessRuleError("Task with this title already exists")

            task.title = title

        task.description = description

        if status is not None:
            if task.status == TaskStatus.DONE and status != TaskStatus.DONE:
                raise BusinessRuleError(
                    "The status of a completed task cannot be changed."
                )
            task.status = status

        await self.repo.update(task)
        return task

    # -------------------- DELETE --------------------
    async def delete_task(self, task_id: UUID) -> None:
        """Удаление задачи по id с проверкой бизнес-правил."""
        task = await self.get_task(task_id)  # бросит NotFoundException, если нет

        # Бизнес-правило: задачу можно удалить только в статусе CREATED
        if task.status != TaskStatus.CREATED:
            raise BusinessRuleError(
                "A task can only be deleted when its status is 'created'."
            )

        await self.repo.delete(task)

    # -------------------- COMMON --------------------
    async def ensure_unique_title(self, title: str) -> None:
        """Проверяет, что название задачи является уникальным.

        Args:
            title (str): Название задачи

        Raises:
            BusinessRuleError: Если название уже существует.
        """
        existing = await self.repo.get_by_title(title)
        if existing:
            raise BusinessRuleError("Task with this title already exists")

    async def ensure_title_is_not_empty(self, title: str) -> None:
        """Проверяет, что название задачи не пустое.

        Args:
            title (str): Название задачи

        Raises:
            BusinessRuleError: Если название пустое или состоит только из пробелов.
        """
        if not title or not title.strip():
            raise BusinessRuleError("Title cannot be empty")
