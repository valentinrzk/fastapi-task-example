# tests/integrations/test_create_task.py
import pytest


class TestCreateTask:
    @pytest.mark.asyncio
    async def test_create_single_unique_task(self, client):
        payload = {"title": "Test task", "description": "desc"}
        resp = await client.post("/tasks/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == payload["title"]

    @pytest.mark.asyncio
    async def test_create_duplicate_task_name_fails(self, client):
        payload = {"title": "Test task", "description": "desc"}

        first_resp = await client.post("/tasks/", json=payload)
        assert first_resp.status_code == 201

        second_resp = await client.post("/tasks/", json=payload)
        assert second_resp.status_code == 400


@pytest.mark.asyncio
async def test_list_tasks_empty(client):
    """
    Проверяем, что список задач пустой до создания первой задачи.
    """
    response = await client.get("/tasks/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0  # коллекция должна быть пустой


@pytest.mark.asyncio
async def test_get_task(client, created_task):
    task_id = created_task["id"]

    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test task"
