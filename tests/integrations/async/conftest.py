# tests/conftest.py
import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from src.core.dependencies import get_db_session
from src.data_access_layer.models.base_model import Base
from src.main import app


# --- Явный event loop для всей сессии ---
@pytest.fixture(scope="session")
def event_loop():
    """
    Создаёт явный event loop для всей сессии pytest.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.stop()
    loop.close()


# --- Контейнер Postgres ---
@pytest_asyncio.fixture(scope="session")
def postgres_url():
    with PostgresContainer(
        image="postgres:16",
        username="test_user",  # pragma: allowlist secret
        password="test_pass",  # pragma: allowlist secret
        dbname="test_db",  # pragma: allowlist secret
    ) as postgres:
        postgres.start()
        url = postgres.get_connection_url().replace(
            "postgresql+psycopg2://", "postgresql+asyncpg://"
        )
        url = url.replace("localhost", "127.0.0.1")
        yield url


# --- Async Engine ---
@pytest_asyncio.fixture(scope="session")
async def async_engine(postgres_url):
    engine = create_async_engine(
        postgres_url, echo=False, future=True, poolclass=NullPool
    )

    # создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # дропаем таблицы после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    async_session_factory = async_sessionmaker(
        bind=async_engine, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session
        # rollback изменений после теста, чтобы база была чистой
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(async_session):
    """
    Клиент, который создаёт новую сессию на каждый запрос (через override).
    """

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def created_task(client):
    response = await client.post(
        "/tasks/", json={"title": "Test task", "description": "desc"}
    )
    assert response.status_code == 201
    return response.json()
