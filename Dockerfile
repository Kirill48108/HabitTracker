FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Установка системных зависимостей (Postgres client, build deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Копируем только файлы зависимостей, чтобы кэшировать установку
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости (и prod, и dev при необходимости можно разделить)
RUN poetry install --no-interaction --no-ansi

# Копируем остальной код проекта
COPY . .

# Открываем порт (для Django / gunicorn)
EXPOSE 8000