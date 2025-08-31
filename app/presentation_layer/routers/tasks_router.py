from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from app.presentation_layer.schemas.task_schema import TaskCreate, TaskRead, TaskUpdate
from app.business_logic_layer.services.task_service import TaskService
from app.core.dependencies import get_task_service, get_task_repository

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead)
async def create_task(
    task_in: TaskCreate,
    service: TaskService = Depends(get_task_service)
):
    return await service.create_task(title=task_in.title, description=task_in.description)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service)
):
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/", response_model=List[TaskRead])
async def list_tasks(
    status: str | None = None,
    service: TaskService = Depends(get_task_service)
):
    return await service.list_tasks(status=status)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    task_in: TaskUpdate,
    service: TaskService = Depends(get_task_service)
):
    task = await service.update_task(task_id, **task_in.dict(exclude_unset=True))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service)
):
    success = await service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
