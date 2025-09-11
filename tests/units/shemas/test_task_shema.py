"""
Модуль: tests.units.schemas.test_task_schema
============================================

Модуль содержит юнит-тесты для Pydantic-схем задачи:
TaskCreate, TaskUpdate, TaskRead, TaskListResponse, TaskDeleteResponse.

Тесты проверяют:
- корректное создание схем с валидными данными,
- валидацию полей (title, description, status),
- граничные значения (максимальная длина, пустые строки, None),
- частичное обновление через TaskUpdate,
- формирование ответов для списков и удаления задач.

Тесты сгруппированы по классам, соответствующим тестируемым схемам.
"""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.data_access_layer.models.task_model import TaskStatus
from app.presentation_layer.schemas.task_schema import (
    TaskCreate,
    TaskDeleteResponse,
    TaskListResponse,
    TaskRead,
    TaskUpdate,
)


class TestTaskCreate:
    """Тесты Pydantic-схемы TaskCreate."""

    @pytest.mark.parametrize("title", ["A", "Valid Title", "A" * 150])
    @pytest.mark.parametrize("description", [None, "", "A" * 5000])
    def test_valid_creation(self, title, description):
        """Проверка корректного создания объекта с допустимыми значениями."""
        task = TaskCreate(title=title, description=description)
        assert task.title == title
        assert task.description == description

    @pytest.mark.parametrize("title", ["", "   ", "A" * 151])
    def test_invalid_title(self, title):
        """Проверка валидации: title не может быть пустым, пробелом или превышать 150 символов."""
        with pytest.raises(ValidationError):
            TaskCreate(title=title, description="Some description")

    @pytest.mark.parametrize("description", ["A" * 5001])
    def test_invalid_description(self, description):
        """Проверка валидации: description не может превышать 5000 символов."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Valid Title", description=description)


class TestTaskUpdate:
    """Тесты Pydantic-схемы TaskUpdate (частичное обновление)."""

    def test_valid_update_all_fields(self):
        """Проверка обновления всех полей схемы."""
        update = TaskUpdate(
            title="Updated Title",
            description="Updated Description",
            status=TaskStatus.IN_PROGRESS,
        )
        assert update.title == "Updated Title"
        assert update.description == "Updated Description"
        assert update.status == TaskStatus.IN_PROGRESS

    def test_partial_update_none_fields(self):
        """Проверка, что все поля могут быть None (необязательные)."""
        update = TaskUpdate(title=None, description=None, status=None)
        assert update.title is None
        assert update.description is None
        assert update.status is None

    @pytest.mark.parametrize("title", ["", "   ", "A" * 151])
    def test_invalid_title(self, title):
        """Проверка валидации: title не может быть пустым, пробелом или превышать 150 символов."""
        with pytest.raises(ValidationError):
            TaskUpdate(title=title)

    @pytest.mark.parametrize("description", ["A" * 5001])
    def test_invalid_description(self, description):
        """Проверка валидации: description не может превышать 5000 символов."""
        with pytest.raises(ValidationError):
            TaskUpdate(title="Valid Title", description=description)


class TestTaskRead:
    """Тесты Pydantic-схемы TaskRead (чтение задачи)."""

    def test_creation(self):
        """Проверка создания объекта TaskRead с валидными данными."""
        task_read = TaskRead(
            id=uuid4(),
            title="Read Title",
            description="Read Description",
            status=TaskStatus.CREATED,
        )
        assert task_read.title == "Read Title"
        assert task_read.description == "Read Description"
        assert task_read.status == TaskStatus.CREATED
        assert isinstance(task_read.id, type(uuid4()))

    def test_title_max_length(self):
        """Проверка, что title может быть максимальной длины (150 символов)."""
        title = "A" * 150
        task_read = TaskRead(
            id=uuid4(), title=title, description="Desc", status=TaskStatus.CREATED
        )
        assert task_read.title == title


class TestTaskListResponse:
    """Тесты Pydantic-схемы TaskListResponse (список задач)."""

    def test_single_task(self):
        """Проверка формирования ответа со списком из одной задачи."""
        task = TaskRead(
            id=uuid4(),
            title="Task 1",
            description="Description 1",
            status=TaskStatus.CREATED,
        )
        response = TaskListResponse(tasks=[task])
        assert len(response.tasks) == 1
        assert response.tasks[0].title == "Task 1"

    def test_multiple_tasks(self):
        """Проверка формирования ответа со списком из нескольких задач."""
        tasks = [
            TaskRead(
                id=uuid4(),
                title=f"Task {i}",
                description=f"Desc {i}",
                status=TaskStatus.CREATED,
            )
            for i in range(5)
        ]
        response = TaskListResponse(tasks=tasks)
        assert len(response.tasks) == 5
        assert response.tasks[2].title == "Task 2"


class TestTaskDeleteResponse:
    """Тесты Pydantic-схемы TaskDeleteResponse (удаление задачи)."""

    def test_default_message(self):
        """Проверка значения поля message по умолчанию."""
        resp = TaskDeleteResponse()
        assert resp.message == "Task deleted successfully"

    def test_custom_message(self):
        """Проверка возможности переопределения значения поля message."""
        resp = TaskDeleteResponse(message="Deleted")
        assert resp.message == "Deleted"
