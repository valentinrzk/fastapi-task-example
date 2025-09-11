import uuid
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.business_logic_layer.services.task_service import TaskService
from app.data_access_layer.models.task_model import Task, TaskStatus
from app.data_access_layer.repositories.task_repository import TaskRepository


@pytest.fixture
def repo_mock():
    return AsyncMock(spec=TaskRepository)


@pytest.fixture
def session_mock():
    """Фикстура для мокированной асинхронной сессии SQLAlchemy."""
    session = AsyncMock(spec=AsyncSession)
    # flush и delete тоже асинхронные
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repo(session_mock):
    """Репозиторий с замоканной сессией."""
    return TaskRepository(session=session_mock)


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


@pytest.fixture
def mock_scalars_first(sample_task):
    """Мок для execute().scalars().first()."""
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = sample_task
    return mock_scalars


@pytest.fixture
def mock_scalars_all(sample_task):
    """Мок для execute().scalars().all()."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_task]
    return mock_scalars
