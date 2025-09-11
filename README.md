# Task Manager Service

## 📌 Описание

Сервис для управления задачами (**CRUD**: Create, Read, Update, Delete).
Реализованы бизнес-правила:

* Нельзя создать задачу с пустым названием
* Название задачи должно быть уникальным
* Нельзя изменить статус завершённой задачи
* Удалять можно только задачи в статусе `CREATED`

Проект построен на **слоистой архитектуре**:

* **API (FastAPI)** — точки входа для клиентов
* **Service layer** — бизнес-логика
* **Repository layer** — доступ к данным
* **Data models (SQLAlchemy)** — модели таблиц базы данных

## Структура проекта

```
root/                               # Корень проекта
├── app/                            # Основной код
    ├── core/                       # Инфраструктурный слой
        ├── app_config.py           # Подгрузка переменных из env
        ├── db_config.py            # Настройка бд
        ├── dependencies.py         # Настройка зависимостей для внедрения
        ├── exception_handlers      # Глобальная обработка исключений
        ├── exceptions.py           # Кастомные исключения
        ├── log_config.py           # Настройка логгера под промтейл
    ├── data_access_layer/          # Слой доступа к данным
        ├── models/                 # SQLAlchemy модели
            ├── base_model.py       # Базовая модель
            ├── task_model.py       # Модель задачи
        ├── repositories/           # Репозитории - абстракция для управления данными в бд
            ├── task_repository.py  # Репозиторий задачи
    ├── business_logic_layer/       # Слой бизнес-логики
        ├── services/               # Сервисы - абстракция для обработки бизнес правил до БД
            ├── task_service/       # Сервис для задач
    ├── presentation_layer/         # Абстракция для внешнего слоя
        ├── shemas/                 # Pydantic схемы для валидации и сваггера
            ├── task_shema.py       # Схема для задачи
        ├── routes/                 # Ручки
            ├── task_router         # Роутер для задач, содержит круд ручек
    ├── main.py                     # Точка входа
├── tests/                          # Тесты
    ├── units/
        ├── repositories/
            ├── test_task_repository# Юнит тесты репозитория
        ├── services/
            ├── test_task_service   # Юнит тесты сервиса
        ├── shemas/
            ├── test_task_shema     # Юнит тесты Pydantic схем
        ├── routers/
            ├── test_task_router    # Юнит тесты ручек
├── migration/                      # Мигарции alembic
├── grafana/                        # конфиг графаны
├── loki/                           # конфиг локи
├── promtail/                       # конфиг промтейла
├── prometheus/                     # конфиг прометеуса

... и многое другое типа пре коммитов, скриптов, конфигов
```
## Чистый код

В проект встроены pre-commit hooks для гарантии чистого кода:

- ruff
- black
- detect-secrets
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- check-added-large-files
- check-merge-conflict
- check-ast

## Наблюдаемость

В проект встроены инструменты мониторинга и логирования:

* **Prometheus** — сбор метрик
* **Grafana** — визуализация метрик и дашборды
* **Loki** — централизованное хранение логов
* **Promtail** — агент для сбора логов и отправки в Loki

## Миграции

Миграции базы данных управляются через **Alembic**.

Примеры:

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

Миграции применяются автоматически при запуске Docker-compose

## Запуск через Docker Compose

Убедитесь, что у вас установлен Docker и Docker Compose.

1. Клонировать репозиторий:

   ```bash
   git clone https://github.com/your-org/task-manager.git
   cd task-manager
   ```

2. Создать файл окружения `.env` (пример):

   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=tasks_db
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/tasks_db
   ```
В проекте есть env.example. Вы можете скопировать его содержимое в .env

3. Запустить проект:

   ```bash
   docker compose up --build
   ```

4. После запуска будут доступны:

   * API: [http://localhost:8000/docs](http://localhost:8000/docs)
   * Grafana: [http://localhost:3000](http://localhost:3000) (логин: `admin`, пароль: `admin`)
   * Prometheus: [http://localhost:9090](http://localhost:9090)
   * Loki: [http://localhost:3100](http://localhost:3100)

## 🧪 Тестирование

В проекте реализовано покрытие из 69 unit-тестов:

- Репозиторий
- Бизнес-логика
- Endpoints
- Pydantic схемы

Для запуска тестов (с pytest):
```
- python -m venv .venv          # В корне проекта ставим venv
- source .venv/bin/activate     # Linux/macOS
- .venv\Scripts\activate        # Windows
- pip install -r requirements-dev.txt     # Устанавливаем дев зависимости
- pytest -v                       # Запускаем тесты
```

```bash
pytest -v
```
