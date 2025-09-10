"""
Модуль task_service.py
======================

Модуль содержит сервис для работы с задачами (Task).
Сервис реализует бизнес-логику для CRUD-операций:
создание, получение, обновление, удаление и смену статуса задачи.

Сервис использует TaskRepository для доступа к базе данных
и управляет бизнес-правилами и проверками.
"""

from typing import Optional
from uuid import UUID

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.data_access_layer.models.task_model import Task, TaskStatus
from app.data_access_layer.repositories.task_repository import TaskRepository


class TaskService:
    """Сервисный слой для работы с задачами."""

    def __init__(self, repository: TaskRepository):
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
        if not title:
            raise BusinessRuleError("Title не может быть пустым")

        # Проверка уникальности через репозиторий
        existing = await self.repo.get_by_title(title)
        if existing:
            raise BusinessRuleError("Задача с таким названием уже существует")

        task = Task(title=title, description=description)
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
            raise NotFoundError(f"Task {task_id} не найден")
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
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            # пример бизнес-правила: нельзя вернуть из DONE в IN_PROGRESS
            if task.status == TaskStatus.DONE and status != TaskStatus.DONE:
                raise BusinessRuleError("Нельзя изменить статус завершенной задачи")
            task.status = status

        await self.repo.update(task)  # flush, commit делается выше в сессии
        return task

    # -------------------- DELETE --------------------
    async def delete_task(self, task_id: UUID) -> None:
        """Удаление задачи по id с проверкой бизнес-правил."""
        task = await self.get_task(task_id)  # бросит NotFoundException, если нет

        # пример бизнес-правила: нельзя удалять задачи в процессе выполнения
        if task.status == TaskStatus.IN_PROGRESS:
            raise BusinessRuleError("Нельзя удалить задачу в работе")

        await self.repo.delete(task)
