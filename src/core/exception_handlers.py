"""
Модуль: src.presentation_layer.exception_handlers

Модуль содержит кастомные обработчики исключений для FastAPI-приложения.

Назначение:

Обработчики позволяют централизованно перехватывать ошибки в приложении
и возвращать корректные HTTP-ответы с соответствующими кодами статуса,
не перегружая логику отдельных ручек.

Сущности:

not_found_exception_handler — обработка ошибок NotFoundError, возвращает 404.

business_rule_exception_handler — обработка ошибок бизнес-логики, возвращает 400.

generic_exception_handler — обработка всех остальных неожиданных ошибок, возвращает 500.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


async def not_found_exception_handler(request: Request, exc: Exception):
    """Обработчик для NotFoundError"""
    logger.info(
        "Resource not found", extra={"path": request.url.path, "detail": str(exc)}
    )
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def business_rule_exception_handler(request: Request, exc: Exception) -> Response:
    """Обработчик для бизнес-исключений"""
    logger.info(
        "Business rule violated", extra={"path": request.url.path, "detail": str(exc)}
    )
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Обработчик всех остальных ошибок"""
    logger.exception(
        "Unexpected error", extra={"path": str(request.url), "detail": str(exc)}
    )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
