#!/bin/sh
set -e

# Переменные (можно задать через .env)
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${POSTGRES_USER:-app}

echo "⏳ Ждём Postgres на $DB_HOST:$DB_PORT ..."

# Проверяем готовность БД в цикле
TIMEOUT=30
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
  sleep 1
  TIMEOUT=$((TIMEOUT-1))
  if [ $TIMEOUT -le 0 ]; then
    echo "❌ Таймаут ожидания базы"
    exit 1
  fi
done

echo "✅ Postgres готов! Применяем миграции Alembic..."

# Запускаем Alembic
alembic upgrade head

echo "🚀 Запускаем FastAPI"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
