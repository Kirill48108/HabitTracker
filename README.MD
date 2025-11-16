# HabitTracker — Django + DRF + Celery + Telegram

Полноценный сервис трекинга привычек:
- Кастомный пользователь (приложение `users`)
- JWT-аутентификация (SimpleJWT)
- CORS (для фронтенда)
- Документация OpenAPI (drf-spectacular)
- Фильтрация (django-filter)
- Пагинация (5 элементов на страницу)
- Валидаторы бизнес-правил как классы с методами `__call__` и `__fields__`
- Уведомления в Telegram (Celery + Redis)
- Права доступа (CRUD только для своих привычек, публичный список для всех)
- Тесты с высоким покрытием и линтинг (flake8/black/isort)

Содержимое:
- Технологии
- Быстрый старт (локально, через Poetry)
- Переменные окружения (.env пример)
- Миграции/суперпользователь
- Запуск Celery/Redis
- Эндпоинты API и фильтры
- Документация
- Тесты/покрытие/линтинг
- Docker: Dockerfile и docker-compose.yml (PostgreSQL, Redis, web, Celery worker/beat)
- Траблшутинг

---

## Технологии

- Python 3.13, Django 5, Django REST Framework
- SimpleJWT (djangorestframework-simplejwt)
- django-filter
- drf-spectacular (OpenAPI/Swagger UI)
- Celery 5 + Redis
- requests (Telegram Bot API)
- django-cors-headers (CORS)
- Poetry (зависимости)
- flake8, black, isort, mypy (линтинг)
- coverage (покрытие)

---

## Быстрый старт (локально)

1) Установите зависимости: bash poetry install
2) Скопируйте `.env.sample` в `.env` и заполните (см. раздел ниже):
bash cp .env.sample .env
3) Примените миграции и запустите сервер: bash poetry run python manage.py migrate poetry run python manage.py runserver
4) (Опционально) создайте суперпользователя: bash poetry run python manage.py createsuperuser
5) Запустите Redis/Celery для напоминаний (см. раздел Celery/Redis).


## Переменные окружения

Пример `.env` (работает локально с PostgreSQL и Redis):



