"""
Модуль: app.presentation_layer.routers.tasks
===========================================

Реализация маршрутов (эндпоинтов) для работы с задачами.

Все ошибки, возникающие в сервисах (`NotFoundError`, `BusinessRuleError`),
обрабатываются глобальными exception handlers, поэтому ручки максимально
тонкие и содержат только вызов сервиса и возврат результата.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from app.business_logic_layer.services.task_service import TaskService
from app.core.dependencies import get_task_service
from app.presentation_layer.schemas.task_schema import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead)
async def create_task(
    task_in: TaskCreate,
    service: TaskService = Depends(get_task_service),  # type: ignore
) -> TaskRead:
    """
    Создание новой задачи.

    Аргументы:
        task_in: TaskCreate - данные новой задачи
        service: TaskService - сервис для работы с задачами

    Возвращает:
        TaskRead - созданная задача
    """
    new_task = await service.create_task(
        title=task_in.title, description=task_in.description
    )
    return TaskRead.model_validate(new_task)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID, service: TaskService = Depends(get_task_service)  # type: ignore
) -> TaskRead:
    """
    Получение задачи по её уникальному идентификатору.

    Исключения `NotFoundError` обрабатываются глобальными хендлерами.

    Аргументы:
        task_id: UUID - ID задачи
        service: TaskService - сервис для работы с задачами

    Возвращает:
        TaskRead - найденная задача
    """
    task = await service.get_task(task_id)
    return TaskRead.model_validate(task)


@router.get("/", response_model=list[TaskRead])
async def list_tasks(
    task_status: str | None = None,
    service: TaskService = Depends(get_task_service),  # type: ignore
) -> list[TaskRead]:
    """
    Получение списка задач, опционально фильтруемых по статусу.

    Аргументы:
        status: str | None - фильтр по статусу задачи
        service: TaskService - сервис для работы с задачами

    Возвращает:
        list[TaskRead] - список задач
    """
    tasks = await service.list_tasks(status=task_status)
    return [TaskRead.model_validate(task) for task in tasks]


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    task_in: TaskUpdate,
    service: TaskService = Depends(get_task_service),  # type: ignore
) -> TaskRead:
    """
    Частичное обновление задачи.

    Исключения `NotFoundError` и `BusinessRuleError` обрабатываются глобальными хендлерами.

    Аргументы:
        task_id: UUID - ID задачи
        task_in: TaskUpdate - данные для обновления
        service: TaskService - сервис для работы с задачами

    Возвращает:
        TaskRead - обновлённая задача
    """
    task = await service.update_task(task_id, **task_in.model_dump(exclude_unset=True))
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID, service: TaskService = Depends(get_task_service)  # type: ignore
) -> Response:
    """
    Удаление задачи по ID.

    Исключения `NotFoundError` и `BusinessRuleError` обрабатываются
    глобальными exception handlers.

    Аргументы:
        task_id: UUID - ID задачи
        service: TaskService - сервис для работы с задачами

    Возвращает:
        Response со статусом 204 при успешном удалении
    """
    await service.delete_task(task_id)
    return Response(status_code=204)
