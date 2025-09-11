"""
Модуль: app.main
================

Главный модуль приложения FastAPI.

Задачи модуля:
---------------
- Инициализация логирования.
- Загрузка настроек приложения.
- Создание экземпляра FastAPI.
- Подключение метрик.
- Подключение роутеров.
- Определение корневого эндпоинта проверки работы сервиса.
"""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.app_config import get_settings
from app.core.exception_handlers import (
    business_rule_exception_handler,
    generic_exception_handler,
    not_found_exception_handler,
)
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.core.log_config import setup_logging
from app.presentation_layer.routers import task_router

# Настраиваем конфигурацию логгирования
setup_logging()

# Загружаем настрйоки и кешируем их
settings = get_settings()

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Подключаем Prometheus для сбора метрик
Instrumentator().instrument(app).expose(app)

# Регистрируем обработчики
app.add_exception_handler(NotFoundError, not_found_exception_handler)
app.add_exception_handler(BusinessRuleError, business_rule_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Подключаем роутеры
app.include_router(task_router.router)


# Тестовый/корневой эндпоинт
@app.get("/")
async def root() -> dict[str, str]:
    """
    Корневой эндпоинт для проверки доступности сервиса.

    Returns:
        dict: Простое сообщение {"status": "ok"}.
    """
    return {"status": "ok"}
