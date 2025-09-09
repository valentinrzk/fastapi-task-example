#!/bin/bash

# Ждём 30 секунд
echo "Waiting for 30 seconds..."
sleep 15

# Создаём ревизию Alembic с автогенерацией
echo "Creating initial Alembic revision..."
alembic revision --autogenerate -m "Initial revision"

# Применяем все миграции
echo "Upgrading database to latest revision..."
alembic upgrade head

echo "Migrations completed."
