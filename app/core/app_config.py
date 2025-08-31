"""
Модуль: app.core.app_config.py
=====================

Содержит класс настроек приложения, который загружает переменные окружения из файла `.env`
с помощью Pydantic. Поддерживает кэширование настроек, чтобы избежать многократной инициализации.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
       Класс конфигурации приложения.

       Загружает переменные окружения из файла `.env` и предоставляет их в виде атрибутов.
       Используется для хранения всех настроек, связанных с:
       - Базой данных
       - JWT-аутентификацией
       - Интеграцией с Grafana
       - Режимом отладки

       Атрибуты:
           APP_NAME (str): Название приложения.
           DEBUG (bool): Флаг отладки. Если True — выводит больше логов.
           POSTGRES_USER (str): Имя пользователя базы данных.
           POSTGRES_PASSWORD (str): Пароль пользователя базы данных.
           POSTGRES_DB (str): Имя базы данных.
           POSTGRES_HOST (str): Хост базы данных.
           POSTGRES_PORT (int): Порт базы данных.
           DATABASE_ASYNC_URL (str): URL для подключения через asyncpg.
           DATABASE_SYNC_URL (str): URL для подключения через psycopg2.
           JWT_SECRET (str): Секрет для подписи JWT.
           JWT_ALG (str): Алгоритм шифрования JWT.
           ACCESS_TOKEN_EXPIRE_MINUTES (int): Срок жизни access-токена в минутах.
           REFRESH_TOKEN_EXPIRE_DAYS (int): Срок жизни refresh-токена в днях.
           GRAFANA_USER (str): Логин Grafana.
           GRAFANA_PASSWORD (str): Пароль Grafana.
       """
    # Общие настройки
    APP_NAME: str = "FastAPI Task Example"
    DEBUG: bool = False

    # Настройки базы данных
    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "app"
    POSTGRES_DB: str = "app_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # Автоматическая генерация URL для подключения к БД
    @property
    def get_database_async_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Генерация URL для подключения к базе данных (синхронный)
    @property
    def get_database_sync_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Настройки Grafana
    GRAFANA_USER: str = "admin"
    GRAFANA_PASSWORD: str = "admin"

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