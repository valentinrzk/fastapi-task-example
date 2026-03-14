"""
Модуль: src.core.app_config.py
=====================

Содержит класс настроек приложения, который загружает переменные окружения из файла `.env`
с помощью Pydantic. Поддерживает кэширование настроек, чтобы избежать многократной инициализации.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):  # type: ignore[misc]
    """
    Класс конфигурации приложения.

    Загружает переменные окружения из файла `.env` и предоставляет их в виде атрибутов.
    """

    # Общие настройки
    APP_NAME: str = "FastAPI Task Example"
    DEBUG: bool = False

    # Настройки базы данных
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    # Автоматическая генерация URL для подключения к БД
    @property
    def get_database_async_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Генерация URL для подключения к базе данных (синхронный)
    @property
    def get_database_sync_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Настройки Grafana

    GRAFANA_USER: str
    GRAFANA_PASSWORD: str
    PROMETHEUS_PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """
    Получает закэшированный экземпляр настроек.
    Возвращает:
        Settings: Объект настроек приложения.
    """
    return Settings()
