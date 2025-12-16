# HabitTracker — Django + DRF + Celery + Telegram

Полноценный сервис трекинга привычек с автоматизированным циклом разработки и деплоя.

## Функционал
- **Кастомный пользователь**: Аутентификация через Email и JWT (SimpleJWT).
- **Привычки**: Полный CRUD для личных привычек и публичный список для вдохновения.
- **Валидаторы**: Строгие бизнес-правила (отсутствие конфликтов по времени, вознаграждение только для приятных привычек и др.).
- **Уведомления**: Интеграция с Telegram Bot API через Celery + Redis.
- **Права доступа**: Настроены через кастомные Permissions (только автор может редактировать/удалять).
- **Документация**: Автоматическая генерация OpenAPI 3.0 (Swagger) на главной странице.

---

## Технологии
- **Backend**: Python 3.13, Django 5.2.8, DRF 3.16
- **Database**: PostgreSQL 15
- **Task Queue**: Celery 5.5 + Redis 5
- **DevOps**: Docker Compose V2, Poetry
- **CI/CD**: GitHub Actions (Linting, Testing, Auto-deploy to Yandex Cloud)
- **Code Style**: Black, isort, Flake8

---

## CI/CD и Качество кода
В проекте настроен автоматический пайплайн (GitHub Actions):
1. **Linter & Security**: Проверка стиля кода (`Black`, `isort`, `Flake8`) и безопасности (`Bandit`).
2. **Pytest**: Автоматический запуск тестов в изолированном контейнере Postgres.
3. **Continuous Deployment**: При пуше в ветку `main` проект автоматически обновляется на сервере в Yandex Cloud через SSH-экшен.

---

## Быстрый старт (Docker)

1. **Клонируйте репозиторий**:
   ```bash
   git clone github.com
   cd HabitTracker
# Используйте код с осторожностью.

# Создайте файл .env в корне проекта (см. раздел "Переменные окружения").
# Запустите проект:

bash
docker compose up --build -d


# Примените миграции и создайте админа:
bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser


# Соберите статику:
bash
docker compose exec web python manage.py collectstatic --noinput


# Переменные окружения (.env)
Обязательные переменные для работы:
env

# Django
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=158.160.91.136,localhost,127.0.0.1

# Database (для Docker HOST должен быть 'db')
NAME=habittracker_db
USER=kirill
PASSWORD=your_password
HOST=db
PORT=5432

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Redis / Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
Используйте код с осторожностью.

# Эндпоинты
Главная (Swagger UI): http://<server_ip>/ (автоматический редирект на документацию)
Админ-панель: http://<server_ip>/admin/
Документация API: http://<server_ip>/api/docs/
JWT Auth: http://<server_ip>/api/auth/jwt/create/
Тестирование и Линтинг
Запуск тестов с покрытием:
bash
docker compose exec web coverage run -m pytest
docker compose exec web coverage report
Используйте код с осторожностью.

# Ручной запуск линтеров:
bash
poetry run black .
poetry run isort .
poetry run flake8 .
Используйте код с осторожностью.





