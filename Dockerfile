# ---- 1. Builder stage ----
FROM python:3.12-alpine AS builder

# Отключаем генерацию pyc и делаем вывод в stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# Системные зависимости для сборки пакетов Python
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    gcc

# Копируем только requirements, чтобы кэшировать pip install
COPY requirements.txt .

# Устанавливаем зависимости в отдельную директорию
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- 2. Final stage ----
FROM python:3.12-alpine AS final

# Создаём небезопасного пользователя без root
RUN adduser -D appuser

WORKDIR /app

# Копируем зависимости из builder stage
COPY --from=builder /install /usr/local

# Копируем код приложения
COPY . .

# Копируем скрипт ожидания базы (если он в scripts/)
COPY scripts/wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Даём права пользователю
RUN chown -R appuser:appuser /app
USER appuser

# Открываем порт FastAPI
EXPOSE 8000

# ENTRYPOINT запускает скрипт wait-for-db.sh
ENTRYPOINT ["/wait-for-db.sh"]
