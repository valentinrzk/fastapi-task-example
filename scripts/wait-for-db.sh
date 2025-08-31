#!/bin/sh
set -e

DB_HOST="db"
DB_PORT="5432"
DB_USER="app_user"
DB_PASSWORD="app_password"
DB_NAME="app_db"

echo "DB_HOST=$DB_HOST | DB_PORT=$DB_PORT | DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER | DB_PASSWORD=$DB_PASSWORD"
echo "⏳ Ждём Postgres на $DB_HOST:$DB_PORT..."

TIMEOUT=60
while ! PGPASSWORD=$DB_PASSWORD pg_isready \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" > /dev/null 2>&1; do
  sleep 1
  TIMEOUT=$((TIMEOUT-1))
  if [ $TIMEOUT -le 0 ]; then
    echo "❌ Таймаут ожидания базы на $DB_HOST:$DB_PORT"
    exit 1
  fi
done

echo "✅ Postgres готов!"

echo "🚀 Применяем миграции Alembic..."
PGPASSWORD=$DB_PASSWORD alembic upgrade head

echo "🚀 Запускаем FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
