"""
Модуль: app.main
================

Главный модуль приложения FastAPI.

Задачи модуля:
---------------
- Инициализация логирования.
- Загрузка настроек приложения.
- Создание экземпляра FastAPI.
- Подключение роутеров (эндпоинтов).
- Определение корневого эндпоинта проверки работы сервиса.
"""

from fastapi import FastAPI
from app.presentation_layer.routers import tasks_router
from app.core.log_config import setup_logging
from app.core.app_config import get_settings
from prometheus_fastapi_instrumentator import Instrumentator


# -----------------------
# Настройка логирования
# -----------------------
# Вызывается перед созданием экземпляра FastAPI, чтобы все логи приложения корректно обрабатывались.
setup_logging()

# -----------------------
# Загрузка настроек
# -----------------------
# Настройки кэшируются через lru_cache внутри get_settings()
settings = get_settings()

app = FastAPI()

# -----------------------
# Подключение роутеров
# -----------------------
# Роутеры отвечают за аутентификацию и работу с пользователями
app.include_router(tasks_router.router)

# Подключаем метрики
@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)

# -----------------------
# Тестовый/корневой эндпоинт
# -----------------------
@app.get("/")
async def root():
    """
    Корневой эндпоинт для проверки доступности сервиса.

    Returns:
        dict: Простое сообщение {"status": "ok"}.
    """
    return {"status": "ok"}