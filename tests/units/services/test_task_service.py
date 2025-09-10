import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.business_logic_layer.services.task_service import TaskService
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.data_access_layer.models.task_model import Task, TaskStatus


# Простой мок-объект вместо SQLAlchemy Task
class TaskMock:
    def __init__(self, title, description=None, status=TaskStatus.CREATED):
        self.title = title
        self.description = description
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


# -------------------- CREATE --------------------
@pytest.mark.asyncio
class TestCreateTask:
    """Тесты метода create_task сервиса TaskService."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, service, repo_mock):
        """Создание задачи с валидным title и description должно пройти успешно."""
        repo_mock.get_by_title.return_value = None
        repo_mock.create.return_value = None

        task = await service.create_task("New Task", "Description")

        assert task.title == "New Task"
        assert task.description == "Description"
        assert task.status == TaskStatus.CREATED
        repo_mock.create.assert_awaited_once_with(task)

    async def test_create_task_empty_title(self, service):
        """Попытка создать задачу с пустым title должна вызвать BusinessRuleError."""
        with pytest.raises(BusinessRuleError):
            await service.create_task("")

    async def test_create_task_duplicate_title(self, service, repo_mock, sample_task):
        """Попытка создать задачу с уже существующим title должна вызвать BusinessRuleError."""
        repo_mock.get_by_title.return_value = sample_task
        with pytest.raises(BusinessRuleError):
            await service.create_task(sample_task.title)


# -------------------- GET --------------------
@pytest.mark.asyncio
class TestGetTask:
    """Тесты метода get_task сервиса TaskService."""

    async def test_get_task_success(self, service, repo_mock, sample_task):
        """Получение существующей задачи по ID должно вернуть объект Task."""
        repo_mock.get_by_id.return_value = sample_task
        task = await service.get_task(sample_task.id)
        assert task == sample_task

    async def test_get_task_not_found(self, service, repo_mock):
        """Получение несуществующей задачи должно вызвать NotFoundError."""
        repo_mock.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await service.get_task(uuid.uuid4())


# -------------------- LIST --------------------
@pytest.mark.asyncio
class TestListTasks:
    """Тесты метода list_tasks сервиса TaskService."""

    async def test_list_tasks_no_filter(self, service, repo_mock, sample_task):
        """Получение списка задач без фильтрации должно вернуть все задачи."""
        repo_mock.list.return_value = [sample_task]
        tasks = await service.list_tasks()
        assert tasks == [sample_task]
        repo_mock.list.assert_awaited_once_with(status=None)

    async def test_list_tasks_with_status(self, service, repo_mock, sample_task):
        """Получение списка задач с фильтром по статусу должно вернуть только подходящие задачи."""
        repo_mock.list.return_value = [sample_task]
        tasks = await service.list_tasks(status=TaskStatus.CREATED)
        assert tasks == [sample_task]
        repo_mock.list.assert_awaited_once_with(status=TaskStatus.CREATED)


# -------------------- UPDATE --------------------
@pytest.mark.asyncio
class TestUpdateTask:
    """Тесты метода update_task сервиса TaskService."""

    async def test_update_task_title(self, service, repo_mock, sample_task):
        """Обновление title существующей задачи должно изменить title."""
        repo_mock.get_by_id.return_value = sample_task
        updated_task = await service.update_task(sample_task.id, title="Updated Title")
        assert updated_task.title == "Updated Title"
        repo_mock.update.assert_awaited_once_with(sample_task)

    async def test_update_task_description(self, service, repo_mock, sample_task):
        """Обновление description существующей задачи должно изменить description."""
        repo_mock.get_by_id.return_value = sample_task
        updated_task = await service.update_task(sample_task.id, description="New Desc")
        assert updated_task.description == "New Desc"

    async def test_update_task_status_allowed(self, service, repo_mock, sample_task):
        """Обновление статуса задачи в разрешенный статус должно пройти успешно."""
        repo_mock.get_by_id.return_value = sample_task
        updated_task = await service.update_task(
            sample_task.id, status=TaskStatus.IN_PROGRESS
        )
        assert updated_task.status == TaskStatus.IN_PROGRESS

    async def test_update_task_status_from_done_raises(
        self, service, repo_mock, sample_task
    ):
        """Попытка изменить статус из DONE в другой должна вызвать BusinessRuleError."""
        sample_task.status = TaskStatus.DONE
        repo_mock.get_by_id.return_value = sample_task
        with pytest.raises(BusinessRuleError):
            await service.update_task(sample_task.id, status=TaskStatus.IN_PROGRESS)

    async def test_update_task_not_found(self, service, repo_mock):
        """Попытка обновить несуществующую задачу должна вызвать NotFoundError."""
        repo_mock.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await service.update_task(uuid.uuid4(), title="x")


# -------------------- DELETE --------------------
@pytest.mark.asyncio
class TestDeleteTask:
    """Тесты метода delete_task сервиса TaskService."""

    async def test_delete_task_success(self, service, repo_mock, sample_task):
        """Удаление существующей задачи со статусом CREATED или DONE должно пройти успешно."""
        sample_task.status = TaskStatus.CREATED
        repo_mock.get_by_id.return_value = sample_task
        await service.delete_task(sample_task.id)
        repo_mock.delete.assert_awaited_once_with(sample_task)

    async def test_delete_task_in_progress_raises(
        self, service, repo_mock, sample_task
    ):
        """Попытка удалить задачу со статусом IN_PROGRESS должна вызвать BusinessRuleError."""
        sample_task.status = TaskStatus.IN_PROGRESS
        repo_mock.get_by_id.return_value = sample_task
        with pytest.raises(BusinessRuleError):
            await service.delete_task(sample_task.id)

    async def test_delete_task_not_found(self, service, repo_mock):
        """Попытка удалить несуществующую задачу должна вызвать NotFoundError."""
        repo_mock.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await service.delete_task(uuid.uuid4())
