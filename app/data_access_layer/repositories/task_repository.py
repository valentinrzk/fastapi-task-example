"""
Модуль: app.data_access_layer.repositories.task_repository.py
=========================

Модуль содержит репозиторий для работы с задачами в базе данных.
Он реализует стандартные CRUD-операции и предоставляет интерфейс
для работы с объектами модели Task.

Сущности:
---------
- TaskRepository — класс, отвечающий за доступ к данным о задачах.

Назначение:
-----------
Репозиторий используется в слое BLL (сервисах) для работы с базой данных.
Он инкапсулирует SQL-запросы и обеспечивает единый интерфейс для
создания, чтения, обновления и удаления задач.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.data_access_layer.models.task_model import Task, TaskStatus
from uuid import UUID


class TaskRepository:
    """Репозиторий для работы с задачами в базе данных.

    Методы класса позволяют создавать, получать, обновлять и удалять задачи.
    Репозиторий не содержит бизнес-логику и отвечает только за доступ к данным.
    Репозиторий использует flush() для отправки SQL-запросов в базу без фиксации транзакции.
    Коммит осуществляется в BLL
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
        """
        self.session = session

    # -------------------- CREATE --------------------
    async def create(self, task: Task) -> Task:
        """Создание новой задачи в базе.

        Args:
            task (Task): Объект задачи для создания.

        Returns:
            Task: Созданный объект задачи с заполненным id.
        """
        self.session.add(task)
        await self.session.flush()  # генерирует id для Python-side default
        return task

    # -------------------- READ --------------------
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Получение задачи по UUID.

        Args:
            task_id (UUID): Уникальный идентификатор задачи.

        Returns:
            Optional[Task]: Задача, если найдена, иначе None.
        """
        result = await self.session.get(Task, task_id)
        return result

    async def get_by_title(self, title: str) -> Optional[Task]:
        """Получение задачи по названию.

        Args:
            title (str): Название задачи.

        Returns:
            Optional[Task]: Задача, если найдена, иначе None.
        """
        stmt = select(Task).where(Task.title == title)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """Получение списка задач. Можно фильтровать по статусу.

        Args:
            status (Optional[TaskStatus]): Статус задачи для фильтрации.

        Returns:
            List[Task]: Список задач.
        """
        stmt = select(Task)
        if status:
            stmt = stmt.where(Task.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # -------------------- UPDATE --------------------
    async def update(self, task: Task, **kwargs) -> Task:
        """Обновление полей задачи.

        Args:
            task (Task): Объект задачи для обновления.
            **kwargs: Поля и значения для обновления.

        Returns:
            Task: Обновлённый объект задачи.
        """
        for key, value in kwargs.items():
            setattr(task, key, value)
        self.session.add(task)
        await self.session.flush()
        return task

    # -------------------- DELETE --------------------
    async def delete(self, task: Task) -> None:
        """Удаление задачи из базы.

        Args:
            task (Task): Объект задачи для удаления.
        """
        await self.session.delete(task)
        await self.session.flush()
