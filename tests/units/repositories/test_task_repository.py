from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.data_access_layer.models.task_model import Task, TaskStatus
from src.data_access_layer.repositories.task_repository import TaskRepository


@pytest.mark.asyncio
class TestCreate:
    """Тесты метода create."""

    async def test_create_calls_add_and_flush(
        self, repo: TaskRepository, session_mock, sample_task
    ):
        """Проверка, что create добавляет объект и вызывает flush."""
        await repo.create(sample_task)
        session_mock.add.assert_called_once_with(sample_task)
        session_mock.flush.assert_awaited_once()


@pytest.mark.asyncio
class TestGetById:
    """Тесты метода get_by_id."""

    async def test_get_by_id_calls_session_get(
        self, repo: TaskRepository, session_mock, sample_task
    ):
        """Проверка, что get_by_id вызывает session.get и возвращает объект."""
        session_mock.get.return_value = sample_task
        task = await repo.get_by_id(sample_task.id)
        session_mock.get.assert_called_once_with(Task, sample_task.id)
        assert task == sample_task


@pytest.mark.asyncio
class TestGetByTitle:
    async def test_get_by_title_executes_select(self, repo, session_mock, sample_task):
        scalars_mock = MagicMock()
        scalars_mock.first.return_value = sample_task

        execute_mock = MagicMock()
        execute_mock.scalars.return_value = scalars_mock
        session_mock.execute = AsyncMock(return_value=execute_mock)

        task = await repo.get_by_title(sample_task.title)
        session_mock.execute.assert_awaited()
        assert task == sample_task


@pytest.mark.asyncio
class TestList:
    """Тесты метода list."""

    async def test_list_no_status(self, repo, session_mock, sample_task):
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_task]

        execute_mock = MagicMock()
        execute_mock.scalars.return_value = scalars_mock
        session_mock.execute = AsyncMock(return_value=execute_mock)

        tasks = await repo.list()
        session_mock.execute.assert_awaited()
        assert tasks == [sample_task]

    async def test_list_with_status(self, repo, session_mock, sample_task):
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_task]

        execute_mock = MagicMock()
        execute_mock.scalars.return_value = scalars_mock
        session_mock.execute = AsyncMock(return_value=execute_mock)

        tasks = await repo.list(status=TaskStatus.CREATED)
        session_mock.execute.assert_awaited()
        assert tasks == [sample_task]


@pytest.mark.asyncio
class TestUpdate:
    """Тесты метода update."""

    async def test_update_sets_attributes_and_flush(
        self, repo: TaskRepository, session_mock, sample_task
    ):
        """Обновление полей задачи должно установить атрибуты и вызвать flush."""
        updates = {"title": "Updated Title", "description": "Updated Description"}
        await repo.update(sample_task, **updates)
        assert sample_task.title == "Updated Title"
        assert sample_task.description == "Updated Description"
        session_mock.add.assert_called_once_with(sample_task)
        session_mock.flush.assert_awaited_once()


@pytest.mark.asyncio
class TestDelete:
    """Тесты метода delete."""

    async def test_delete_calls_session_delete_and_flush(
        self, repo: TaskRepository, session_mock, sample_task
    ):
        """Проверка, что delete вызывает session.delete и flush."""
        await repo.delete(sample_task)
        session_mock.delete.assert_awaited_once_with(sample_task)
        session_mock.flush.assert_awaited_once()
