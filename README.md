# Neuro Resume Backend

AI-помощник для подготовки профессиональных резюме через интерактивное интервью.

## Возможности

-   Регистрация и аутентификация пользователей (JWT)
-   Управление профилем и смена пароля
-   Создание и ведение интервью-сессий с вопросами от нейросети
-   Хранение переписки (сообщений) в рамках сессии
-   Формирование резюме из ответов, хранение нескольких версий
-   REST API c OpenAPI спецификацией

## Стек

-   Python 3.11+
-   FastAPI
-   SQLAlchemy (async) + PostgreSQL
-   Alembic для миграций
-   Pytest для тестов

## Быстрый старт

```bash
git clone https://github.com/Neuro-resume/neuro-resume-backend.git
cd neuro-resume-backend
make venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Makefile задачи

```bash
make venv        # создаёт виртуальное окружение .venv
make activate    # открывает shell с активированным окружением
make run         # запускает API (python app/main.py)
make tests       # pytest
make api-tests   # e2e smoke-тесты (scripts/test_api.sh)
```

## Скрипты

-   `scripts/test_api.sh` — e2e smoke-тесты API
-   `scripts/migrate.sh` — управление миграциями
-   `scripts/setup_database.sh` — подготовка базы

## API документация

-   OpenAPI: `openapi.yaml`
-   Ручки подробно: `API_HANDLERS.md`
-   Postman-коллекция: `api/neuro-resume.postman_collection.json`

### Основные эндпоинты

-   `/v1/auth/*` — аутентификация
-   `/v1/user/*` — профиль
-   `/v1/interview/*` — интервью-сессии и сообщения
-   `/v1/resumes/*` — управление резюме

## Тестирование

```bash
make tests       # unit/integration tests
make api-tests   # энд-ту-энд сценарий
```

## Переменные окружения

Создайте `.env` на основе `.env.example`:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/neuro_resume
JWT_SECRET=change_me
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400
LOG_LEVEL=INFO
```

## Контрибьюторам

1. Перед коммитом запускайте `make tests`
2. Соблюдайте стиль (black, flake8, mypy)
3. Миграции: `alembic revision --autogenerate -m "message"`
4. Pull Request с описанием изменений и покрытием тестами

## Лицензия

MIT License
