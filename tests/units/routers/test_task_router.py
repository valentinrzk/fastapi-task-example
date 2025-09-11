from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.responses import Response

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.data_access_layer.models.task_model import TaskStatus
from app.presentation_layer.routers import task_router as tasks_router
from app.presentation_layer.schemas.task_schema import TaskCreate, TaskRead, TaskUpdate


@pytest.fixture
def sample_task():
    """Возвращает пример TaskRead для тестов."""
    return TaskRead(
        id=uuid4(),
        title="Sample Task",
        description="Sample Description",
        status=TaskStatus.CREATED,
    )


@pytest.fixture
def service_mock():
    """Возвращает мок TaskService."""
    return AsyncMock()


class TestCreateTask:
    async def test_create_task_success(self, service_mock, sample_task):
        """Проверяет успешное создание задачи через ручку create_task."""
        service_mock.create_task.return_value = sample_task

        result = await tasks_router.create_task(
            TaskCreate(title="Test", description="Desc"), service=service_mock
        )

        service_mock.create_task.assert_awaited_once_with(
            title="Test", description="Desc"
        )
        assert result == sample_task


class TestGetTask:
    async def test_get_task_success(self, service_mock, sample_task):
        """Проверяет успешное получение задачи по ID через ручку get_task."""
        service_mock.get_task.return_value = sample_task

        result = await tasks_router.get_task(sample_task.id, service=service_mock)

        service_mock.get_task.assert_awaited_once_with(sample_task.id)
        assert result == sample_task

    async def test_get_task_not_found(self, service_mock):
        """Проверяет, что при отсутствии задачи вызывается NotFoundError."""
        service_mock.get_task.side_effect = NotFoundError("Not found")

        with pytest.raises(NotFoundError):
            await tasks_router.get_task(uuid4(), service=service_mock)


class TestListTasks:
    async def test_list_tasks_all(self, service_mock, sample_task):
        """Проверяет возврат всех задач без фильтрации."""
        service_mock.list_tasks.return_value = [sample_task]

        result = await tasks_router.list_tasks(None, service=service_mock)

        service_mock.list_tasks.assert_awaited_once_with(status=None)
        assert result == [sample_task]

    async def test_list_tasks_filtered(self, service_mock, sample_task):
        """Проверяет возврат задач с фильтром по статусу."""
        service_mock.list_tasks.return_value = [sample_task]

        result = await tasks_router.list_tasks(TaskStatus.CREATED, service=service_mock)

        service_mock.list_tasks.assert_awaited_once_with(status=TaskStatus.CREATED)
        assert result == [sample_task]


class TestUpdateTask:
    async def test_update_task_success(self, service_mock, sample_task):
        """Проверяет успешное обновление задачи через ручку update_task."""
        service_mock.update_task.return_value = sample_task
        update_data = TaskUpdate(title="New Title", description=None, status=None)

        result = await tasks_router.update_task(
            sample_task.id, update_data, service=service_mock
        )

        service_mock.update_task.assert_awaited_once_with(
            sample_task.id, title="New Title", description=None, status=None
        )
        assert result == sample_task

    async def test_update_task_not_found(self, service_mock):
        """Проверяет, что при отсутствии задачи вызывается NotFoundError при update."""
        service_mock.update_task.side_effect = NotFoundError("Not found")
        update_data = TaskUpdate(title="New Title")

        with pytest.raises(NotFoundError):
            await tasks_router.update_task(uuid4(), update_data, service=service_mock)

    async def test_update_task_business_rule(self, service_mock):
        """Проверяет, что нарушение бизнес-правил вызывает BusinessRuleError при update."""
        service_mock.update_task.side_effect = BusinessRuleError("Rule violated")
        update_data = TaskUpdate(title="New Title")

        with pytest.raises(BusinessRuleError):
            await tasks_router.update_task(uuid4(), update_data, service=service_mock)


class TestDeleteTask:
    async def test_delete_task_success(self, service_mock):
        """Проверяет успешное удаление задачи через ручку delete_task."""
        task_id = uuid4()

        result = await tasks_router.delete_task(task_id, service=service_mock)

        service_mock.delete_task.assert_awaited_once_with(task_id)
        assert isinstance(result, Response)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_task_not_found(self, service_mock):
        """Проверяет, что при отсутствии задачи вызывается NotFoundError при delete."""
        service_mock.delete_task.side_effect = NotFoundError("Not found")
        task_id = uuid4()

        with pytest.raises(NotFoundError):
            await tasks_router.delete_task(task_id, service=service_mock)

    async def test_delete_task_business_rule(self, service_mock):
        """Проверяет, что нарушение бизнес-правил вызывает BusinessRuleError при delete."""
        service_mock.delete_task.side_effect = BusinessRuleError("Rule violated")
        task_id = uuid4()

        with pytest.raises(BusinessRuleError):
            await tasks_router.delete_task(task_id, service=service_mock)
