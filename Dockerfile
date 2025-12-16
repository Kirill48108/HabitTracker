# Используем актуальный образ Python 3.13 (slim версия для экономии места)
FROM python:3.13-slim

# Устанавливаем переменные окружения для стабильной работы Python и Poetry
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Устанавливаем системные зависимости
# Добавлен curl (нужен для установки poetry) и библиотеки для работы с Postgres
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry и создаем символьную ссылку для удобного вызова
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем только файлы зависимостей для эффективного кэширования слоев Docker
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости проекта (флаг --no-root исправляет ошибку отсутствия README)
RUN poetry install --no-interaction --no-ansi --no-root

# Копируем весь остальной код проекта в контейнер
COPY . .

# Открываем порт 8000 (тот, на котором работает Django/Gunicorn)
EXPOSE 8000