"""
Модуль юнит-тестов для TaskService.

Содержит асинхронные тесты для класса TaskService, покрывающие методы:

- ensure_unique_title
- ensure_title_is_not_empty
- create_task
- get_task
- list_tasks
- update_task
- delete_task

Тесты проверяют:
- Корректное соблюдение бизнес-правил (уникальность названия, непустое название,
  ограничения на удаление, невозможность изменения статуса завершенной задачи)
- Правильную работу CRUD-операций через репозиторий
- Граничные сценарии: несуществующие задачи, пустые поля, дубликаты названий

Используемые фикстуры:
- service: экземпляр TaskService с замоканным репозиторием
- repo_mock: AsyncMock для методов репозитория
- sample_task: пример объекта Task для тестирования
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.business_logic_layer.services.task_service import TaskService
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.data_access_layer.models.task_model import Task, TaskStatus


@pytest.mark.asyncio
class TestEnsureUniqueTitle:
    """Тесты метода ensure_unique_title сервиса TaskService."""

    async def test_unique_title_passes(
        self, service: TaskService, repo_mock: AsyncMock
    ):
        """Если название уникальное, метод проходит без ошибок."""
        repo_mock.get_by_title.return_value = None

        # Метод не должен выбросить исключение
        await service.ensure_unique_title("New Unique Title")

    async def test_duplicate_title_raises(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Если название уже существует, выбрасывается BusinessRuleError."""
        repo_mock.get_by_title.return_value = sample_task

        with pytest.raises(BusinessRuleError) as exc:
            await service.ensure_unique_title(sample_task.title)

        assert str(exc.value) == "Task with this title already exists"


@pytest.mark.asyncio
class TestEnsureTitleIsNotEmpty:
    """Тесты метода ensure_title_is_not_empty сервиса TaskService."""

    async def test_non_empty_title(self, service):
        """Если передано непустое название, метод проходит без ошибок."""
        title = "Valid Title"
        # Метод не должен выбросить исключение
        await service.ensure_title_is_not_empty(title)

    async def test_empty_title_raises(self, service):
        """Если передано пустое название, выбрасывается BusinessRuleError."""
        title = ""
        with pytest.raises(BusinessRuleError) as exc:
            await service.ensure_title_is_not_empty(title)
        assert str(exc.value) == "Title cannot be empty"

    async def test_whitespace_title_raises(self, service):
        """Если название состоит только из пробелов, выбрасывается BusinessRuleError."""
        title = "   "
        with pytest.raises(BusinessRuleError) as exc:
            await service.ensure_title_is_not_empty(title)
        assert str(exc.value) == "Title cannot be empty"

    async def test_title_with_leading_trailing_spaces(self, service):
        """Если название валидное, но содержит пробелы вокруг, метод проходит без ошибок."""
        title = "  Task  "
        await service.ensure_title_is_not_empty(title)


@pytest.mark.asyncio
class TestCreateTask:
    """Тесты метода create_task сервиса TaskService."""

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


@pytest.mark.asyncio
class TestUpdateTask:
    """Тесты метода update_task сервиса TaskService."""

    async def test_update_task_success_with_description(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Валидный апдейт: существующая задача, непустое название и описание."""
        repo_mock.get_by_id.return_value = sample_task
        repo_mock.get_by_title.return_value = None

        updated_task = await service.update_task(
            sample_task.id, title="New Title", description="New Description"
        )

        assert updated_task.title == "New Title"
        assert updated_task.description == "New Description"
        repo_mock.update.assert_awaited_once_with(sample_task)

    async def test_update_task_success_status_change(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Валидный апдейт: смена статуса с CREATED на IN_PROGRESS."""
        repo_mock.get_by_id.return_value = sample_task
        updated_task = await service.update_task(
            sample_task.id, status=TaskStatus.IN_PROGRESS
        )

        assert updated_task.status == TaskStatus.IN_PROGRESS
        repo_mock.update.assert_awaited_once_with(sample_task)

    async def test_update_task_success_clear_description(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Валидный апдейт: очистка описания."""
        repo_mock.get_by_id.return_value = sample_task
        updated_task = await service.update_task(sample_task.id, description=None)

        assert updated_task.description is None
        repo_mock.update.assert_awaited_once_with(sample_task)

    async def test_update_task_not_found(
        self, service: TaskService, repo_mock: AsyncMock
    ):
        """Попытка обновить несуществующую задачу вызывает NotFoundError."""
        repo_mock.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await service.update_task(uuid.uuid4(), title="New Title")

    async def test_update_task_empty_title(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Попытка обновить название на пустое вызывает BusinessRuleError."""
        repo_mock.get_by_id.return_value = sample_task
        with pytest.raises(BusinessRuleError):
            await service.update_task(sample_task.id, title="")

    async def test_update_task_duplicate_title(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Попытка обновить название на уже существующее вызывает BusinessRuleError."""
        repo_mock.get_by_id.return_value = sample_task
        repo_mock.get_by_title.return_value = (
            sample_task  # имитация существующего названия
        )

        with pytest.raises(BusinessRuleError):
            await service.update_task(sample_task.id, title=sample_task.title)

    async def test_update_task_only_title_changes(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Обновление только title изменяет только title."""
        repo_mock.get_by_id.return_value = sample_task
        repo_mock.get_by_title.return_value = None

        updated_task = await service.update_task(sample_task.id, title="Updated Title")

        assert updated_task.title == "Updated Title"
        repo_mock.update.assert_awaited_once_with(sample_task)

    async def test_update_task_only_description_changes(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Обновление только description изменяет только description."""
        repo_mock.get_by_id.return_value = sample_task

        updated_task = await service.update_task(
            sample_task.id, description="Updated Description"
        )

        assert updated_task.description == "Updated Description"
        repo_mock.update.assert_awaited_once_with(sample_task)

    async def test_update_task_status_done_cannot_change(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Попытка изменить статус у задачи DONE вызывает BusinessRuleError."""
        sample_task.status = TaskStatus.DONE
        repo_mock.get_by_id.return_value = sample_task

        with pytest.raises(BusinessRuleError):
            await service.update_task(sample_task.id, status=TaskStatus.IN_PROGRESS)

    async def test_update_task_no_fields_provided(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Если не передано ни одного поля, задача остается без изменений."""
        repo_mock.get_by_id.return_value = sample_task

        updated_task = await service.update_task(sample_task.id)

        assert updated_task.title == sample_task.title
        assert updated_task.description == sample_task.description
        assert updated_task.status == sample_task.status
        repo_mock.update.assert_awaited_once_with(sample_task)


@pytest.mark.asyncio
class TestDeleteTask:
    """Тесты метода delete_task сервиса TaskService."""

    async def test_delete_task_success(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Удаление существующей задачи со статусом CREATED проходит успешно."""
        sample_task.status = TaskStatus.CREATED
        repo_mock.get_by_id.return_value = sample_task

        await service.delete_task(sample_task.id)

        repo_mock.delete.assert_awaited_once_with(sample_task)

    async def test_delete_task_not_created_raises(
        self, service: TaskService, repo_mock: AsyncMock, sample_task: Task
    ):
        """Попытка удалить задачу со статусом не CREATED вызывает BusinessRuleError."""
        sample_task.status = TaskStatus.IN_PROGRESS
        repo_mock.get_by_id.return_value = sample_task

        with pytest.raises(BusinessRuleError) as exc:
            await service.delete_task(sample_task.id)
        assert (
            str(exc.value) == "A task can only be deleted when its status is 'created'."
        )

    async def test_delete_task_not_found(
        self, service: TaskService, repo_mock: AsyncMock
    ):
        """Попытка удалить несуществующую задачу вызывает NotFoundError."""
        repo_mock.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.delete_task(uuid.uuid4())
