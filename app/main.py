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
from app.core.log_config import setup_logging
from app.presentation_layer.routers import tasks_router

# Настраиваем конфигурацию логгирования
setup_logging()

# Загружаем настрйоки и кешируем их
settings = get_settings()

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Подключаем Prometheus для сбора метрик
Instrumentator().instrument(app).expose(app)

# Подключаем роутеры
app.include_router(tasks_router.router)


# Тестовый/корневой эндпоинт
@app.get("/")
async def root() -> dict[str, str]:
    """
    Корневой эндпоинт для проверки доступности сервиса.

    Returns:
        dict: Простое сообщение {"status": "ok"}.
    """
    return {"status": "ok"}
