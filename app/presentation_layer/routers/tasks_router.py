from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from typing import List
from uuid import UUID
import logging

from app.presentation_layer.schemas.task_schema import TaskCreate, TaskRead, TaskUpdate
from app.business_logic_layer.services.task_service import TaskService
from app.core.dependencies import get_task_service, get_task_repository
from app.core.exceptions import NotFoundException, BusinessRuleException

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


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


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Task deleted"},
        404: {"description": "Task not found"},
        500: {"description": "Deletion failed"},
    },
)
async def delete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> JSONResponse:
    try:
        # Обращаемся к сервису
        await service.delete_task(task_id)
    except NotFoundException as e:
        # Если таска не найдена
        logger.info("task not found", extra={"task_id": str(task_id)})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Если иная ошибка
        logger.exception("unexpected error during delete_task", extra={"task_id": str(task_id)})
        raise HTTPException(status_code=500, detail="Internal Server Error")
    # Успех
    return JSONResponse(
        status_code=204,
        content={
            "message": "Task deleted successfully"
        }
    )
