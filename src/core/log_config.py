"""
Модуль: src.core.log_config
====================

Этот модуль содержит конфигурацию логирования для приложения FastAPI.

Основные задачи:
- Определение формата логов для консоли и Uvicorn.
- Настройка корневого логгера приложения.
- Подавление избыточных SQL-логов от SQLAlchemy.

Функции:
    setup_logging():
        Инициализирует систему логирования на основе LOGGING_CONFIG.
        Включает консольный вывод логов и снижает уровень подробности логов SQLAlchemy.

Использование:
    from src.core.log_config import setup_logging

    setup_logging()
"""

import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    "version": 1,  # Версия схемы конфигурации логгера (1 — актуальная)
    "disable_existing_loggers": False,  # Не отключаем уже существующие логгеры
    "formatters": {  # Форматирование сообщений логов
        "default": {"format": "%(asctime)s %(levelname)s %(name)s - %(message)s"},
        "uvicorn": {"format": "%(asctime)s %(levelname)s %(name)s - %(message)s"},
    },
    "handlers": {  # "Обработчики" логов — куда отправлять сообщение
        "console": {  # Здесь логи выводятся в stdout (терминал, docker logs)
            "class": "logging.StreamHandler",  # Потоковый обработчик (stdout)
            "formatter": "default",  # Используем формат default
        },
    },
    "root": {  # Настройки корневого логгера
        "level": "INFO",  # Минимальный уровень логов (DEBUG < INFO < WARNING < ERROR)
        "handlers": ["console"],  # Отправляем логи в консоль
    },
}


def setup_logging() -> None:
    """
    Подключает созданную конфигурацию логгирования.
    Принудительно повышает уровень логов SQLAlchemy до WARNING
    """
    dictConfig(LOGGING_CONFIG)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
