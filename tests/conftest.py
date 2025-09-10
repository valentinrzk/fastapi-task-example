import uuid
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.business_logic_layer.services.task_service import TaskService
from app.data_access_layer.models.task_model import Task, TaskStatus
from app.data_access_layer.repositories.task_repository import TaskRepository


@pytest.fixture
def repo_mock():
    return AsyncMock(spec=TaskRepository)


@pytest.fixture
def service(repo_mock):
    return TaskService(repository=repo_mock)


@pytest.fixture
def sample_task():
    return Task(
        id=uuid.uuid4(),
        title="Sample Task",
        description="Sample Description",
        status=TaskStatus.CREATED,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
