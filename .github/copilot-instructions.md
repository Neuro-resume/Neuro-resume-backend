# Нейро-резюме через чат — AI Resume Builder (Python)

## Описание проекта

Веб-приложение для создания резюме с помощью ИИ. Пользователь создает профиль, начинает сессию, и нейронка задает целевые вопросы для составления профессионального резюме.

Подробные задания по пунктам для тебя расписаны в файле `copilot-tasks.md`. Работай строго по одной задаче за раз, не переходя к следующей, пока текущая не завершена и не протестирована. Строго следуй этому плану.

## Технологический стек

### Backend

-   Python 3.11+
-   FastAPI (или Flask для MVP, но предпочтительно FastAPI)
-   PostgreSQL для хранения данных
-   SQLAlchemy (или asyncpg для асинхронного доступа)
-   MCP (Model Context Protocol) для интеграции с нейронкой

### Frontend

-   Разделение на frontend и backend
-   API-first подход

### API

-   OpenAPI спецификация для всех endpoints (FastAPI генерирует автоматически)
-   RESTful API design principles

### Инструменты разработки

-   black для форматирования
-   flake8 и mypy для линтинга и типизации
-   pytest для тестирования
-   pre-commit для автопроверок
-   alembic для миграций БД

## Структура проекта

```
/
├── .github/
│   └── copilot-instructions.md     # Этот файл
├── api/
│   └── openapi.yaml                # OpenAPI спецификация
├── app/
│   ├── main.py                     # Точка входа приложения (FastAPI)
│   ├── models/                     # Pydantic/SQLAlchemy модели
│   ├── db/                         # Работа с БД
│   ├── repository/                 # Слой доступа к данным
│   ├── services/                   # Бизнес-логика
│   ├── handlers/                   # HTTP endpoints
│   └── mcp/                        # MCP интеграция
├── migrations/                     # Alembic миграции
├── scripts/                        # Скрипты для разработки
│   ├── setup.sh
│   └── test.sh
├── requirements.txt                # Зависимости
├── pyproject.toml                  # Настройки форматирования и линтинга
├── README.md
└── .env.example                    # Пример env-файла
```

## Стандарты кодирования

### Python конвенции

-   Всегда запускать `black` перед коммитом
-   Использовать `flake8` и `mypy` для проверки кода
-   Следовать стандартному Python project layout (см. выше)
-   snake_case для функций и переменных
-   Короткие, описательные имена переменных
-   Обязательная обработка исключений — не игнорировать ошибки
-   Использовать логирование через стандартный модуль `logging`
-   Для асинхронных операций — использовать `async def` и `await`

### Обработка ошибок

```python
# ПРАВИЛЬНО
try:
    ...
except Exception as e:
    logger.error(f"Failed to create profile: {e}")
    raise

# НЕПРАВИЛЬНО — не игнорировать ошибки
try:
    some_function()
except:
    pass  # нельзя
```

### Работа с контекстом

-   Для асинхронных запросов использовать `async`/`await` и dependency injection FastAPI (`Depends`)

## База данных

### Основные таблицы

-   `profiles` — профили пользователей (имя, email, дата создания)
-   `chat_sessions` — сессии общения с ИИ (связь с профилем, статус, дата)
-   `questions` — заданные вопросы (категория, текст вопроса)
-   `answers` — ответы пользователя (связь с вопросом и сессией)
-   `resumes` — сгенерированные резюме (связь с сессией, формат, содержимое)

### Работа с БД

-   Использовать SQLAlchemy ORM или asyncpg с параметризацией
-   Всегда использовать транзакции для связанных операций
-   Конфигурация подключения через переменные окружения

## API Endpoints (OpenAPI)

```
POST   /api/v1/profiles                    # Создание профиля
GET    /api/v1/profiles/{id}               # Получение профиля
PUT    /api/v1/profiles/{id}               # Обновление профиля

POST   /api/v1/sessions                    # Начало новой сессии
GET    /api/v1/sessions/{id}               # Получение сессии
POST   /api/v1/sessions/{id}/answers       # Отправка ответа на вопрос
GET    /api/v1/sessions/{id}/next-question # Получение следующего вопроса

POST   /api/v1/resumes/generate            # Генерация резюме
GET    /api/v1/resumes/{id}                # Получение резюме
GET    /api/v1/resumes/{id}/download       # Скачать резюме (PDF/DOC)
```

## Категории вопросов для нейронки

1. **Опыт работы**: должности, компании, обязанности, достижения
2. **Образование**: учебные заведения, степени, сертификации
3. **Hard skills**: технические навыки, инструменты, языки программирования
4. **Soft skills**: коммуникация, лидерство, работа в команде
5. **Проекты и достижения**: значимые проекты, награды, публикации

## Команды для разработки

-   `pip install -r requirements.txt` — установка зависимостей
-   `alembic upgrade head` — запуск миграций
-   `pytest` — запуск всех тестов
-   `black .` — автоформатирование
-   `flake8 .` — линтинг
-   `uvicorn app.main:app --reload` — запуск сервера для разработки

## Правила для AI помощника

### Общие правила

1. **НИКОГДА не генерировать весь код сразу** — работать только над текущей задачей из roadmap
2. Всегда включать обработку ошибок и исключений
3. Использовать dependency injection FastAPI для работы с БД и сервисами
4. Следовать принципам чистой архитектуры (разделение слоев)
5. Документировать все публичные функции и классы (docstrings)
6. Писать unit-тесты для бизнес-логики (pytest)
7. Валидировать входящие данные через Pydantic-схемы

### Приоритеты при написании кода

1. Корректность и безопасность
2. Читаемость и поддерживаемость
3. Производительность (но не в ущерб пунктам 1-2)

### Паттерны тестирования

-   Использовать parametrize в pytest для table-driven tests
-   Мокировать зависимости (БД, внешние сервисы через unittest.mock или pytest-mock)
-   Тесты должны быть независимыми друг от друга

---

# MVP ROADMAP - ПОШАГОВЫЙ ПЛАН РАЗРАБОТКИ

## ⚠️ ВАЖНО: Работать строго по одной задаче за раз!

Не генерировать код для следующих задач, пока текущая не завершена и не протестирована.

---

## ФАЗА 1: Инфраструктура и базовая настройка

### Задача 1.1: Инициализация проекта и структуры

**Цель**: Создать базовую структуру проекта и настроить зависимости

**Acceptance Criteria**:

-   ✅ Создан requirements.txt с базовыми зависимостями
-   ✅ Создана структура папок согласно project layout выше
-   ✅ Установлен FastAPI, SQLAlchemy, Alembic
-   ✅ Создан .gitignore для Python проектов

**Затрагиваемые файлы**:

-   `requirements.txt`, `pyproject.toml`
-   Структура папок: `app/`, `api/`, `migrations/`, `scripts/`

### Задача 1.2: Настройка подключения к PostgreSQL

**Цель**: Реализовать подключение к БД через SQLAlchemy (или asyncpg)

**Acceptance Criteria**:

-   ✅ Модуль для работы с БД (engine, session)
-   ✅ Конфигурация подключения через переменные окружения
-   ✅ Реализована функция health check
-   ✅ Обработка ошибок и graceful shutdown

**Затрагиваемые файлы**:

-   `app/db/connection.py`
-   `app/main.py`

### Задача 1.3: Настройка системы миграций

**Цель**: Подключить Alembic для управления схемой БД

**Acceptance Criteria**:

-   ✅ Alembic установлен и инициализирован
-   ✅ Скрипт для запуска миграций
-   ✅ Миграции можно откатывать (upgrade/downgrade)

**Затрагиваемые файлы**:

-   `scripts/migrate.sh`
-   `migrations/` (будут создаваться по мере необходимости)

---

## ФАЗА 2: Модуль профилей пользователей

### Задача 2.1: Создание модели и таблицы Profile

**Цель**: Определить структуру данных профиля и создать таблицу в БД

**Acceptance Criteria**:

-   ✅ Создана Go структура Profile с необходимыми полями
-   ✅ Создана миграция для таблицы `profiles`
-   ✅ Поля: id (UUID), name, email, created_at, updated_at
-   ✅ Email должен быть уникальным

**Затрагиваемые файлы**:

-   `internal/models/profile.go`
-   `migrations/001_create_profiles.up.sql`
-   `migrations/001_create_profiles.down.sql`

### Задача 2.2: Реализация Profile Repository

**Цель**: Создать слой доступа к данным для профилей

**Acceptance Criteria**:

-   ✅ Интерфейс ProfileRepository с методами Create, GetByID, Update
-   ✅ Реализация с использованием pgx/sqlx
-   ✅ Все методы принимают context.Context
-   ✅ Proper error handling
-   ✅ Unit тесты с mock DB

**Затрагиваемые файлы**:

-   `internal/repository/profile_repo.go`
-   `internal/repository/profile_repo_test.go`

### Задача 2.3: Реализация Profile Service

**Цель**: Создать бизнес-логику для работы с профилями

**Acceptance Criteria**:

-   ✅ Валидация данных профиля (email format, required fields)
-   ✅ Методы CreateProfile, GetProfile, UpdateProfile
-   ✅ Unit тесты для бизнес-логики

**Затрагиваемые файлы**:

-   `internal/services/profile_service.go`
-   `internal/services/profile_service_test.go`

### Задача 2.4: Реализация Profile Handlers

**Цель**: Создать HTTP endpoints для работы с профилями

**Acceptance Criteria**:

-   ✅ POST /api/v1/profiles - создание профиля
-   ✅ GET /api/v1/profiles/{id} - получение профиля
-   ✅ PUT /api/v1/profiles/{id} - обновление профиля
-   ✅ Proper HTTP status codes (201, 200, 400, 404, 500)
-   ✅ JSON response format
-   ✅ Request validation

**Затрагиваемые файлы**:

-   `internal/handlers/profile.go`
-   `cmd/server/main.go` (регистрация routes)

### Задача 2.5: OpenAPI спецификация для Profile endpoints

**Цель**: Документировать API для профилей

**Acceptance Criteria**:

-   ✅ Описаны все Profile endpoints в OpenAPI формате
-   ✅ Указаны request/response schemas
-   ✅ Примеры запросов и ответов

**Затрагиваемые файлы**:

-   `api/openapi.yaml`

---

## ФАЗА 3: Модуль чат-сессий

### Задача 3.1: Создание моделей Session, Question, Answer

**Цель**: Определить структуры данных для сессий и вопросов

**Acceptance Criteria**:

-   ✅ Структура Session (id, profile_id, status, created_at)
-   ✅ Структура Question (id, session_id, category, text, order)
-   ✅ Структура Answer (id, question_id, answer_text, created_at)
-   ✅ Enum для статусов сессии (active, completed, abandoned)
-   ✅ Enum для категорий вопросов

**Затрагиваемые файлы**:

-   `internal/models/session.go`
-   `internal/models/question.go`
-   `internal/models/answer.go`

### Задача 3.2: Создание миграций для Session, Question, Answer

**Цель**: Создать таблицы в БД для сессий

**Acceptance Criteria**:

-   ✅ Миграция для таблицы `chat_sessions`
-   ✅ Миграция для таблицы `questions`
-   ✅ Миграция для таблицы `answers`
-   ✅ Foreign keys настроены правильно
-   ✅ Индексы для оптимизации запросов

**Затрагиваемые файлы**:

-   `migrations/002_create_sessions.up.sql`
-   `migrations/002_create_sessions.down.sql`

### Задача 3.3: Реализация Session Repository

**Цель**: Слой доступа к данным для сессий

**Acceptance Criteria**:

-   ✅ Методы: CreateSession, GetSession, UpdateSessionStatus
-   ✅ Методы: SaveQuestion, SaveAnswer, GetSessionQuestions
-   ✅ Unit тесты

**Затрагиваемые файлы**:

-   `internal/repository/session_repo.go`
-   `internal/repository/session_repo_test.go`

### Задача 3.4: Базовая интеграция с MCP (заглушка)

**Цель**: Создать интерфейс для работы с MCP, пока с фиксированными вопросами

**Acceptance Criteria**:

-   ✅ Интерфейс MCPClient с методом GetNextQuestion
-   ✅ Mock реализация с жестко закодированными вопросами для каждой категории
-   ✅ 2-3 вопроса для каждой категории (опыт, образование, навыки)

**Затрагиваемые файлы**:

-   `internal/services/mcp_client.go`
-   `internal/services/mcp_mock.go` (для MVP)

### Задача 3.5: Реализация Session Service

**Цель**: Бизнес-логика управления сессиями

**Acceptance Criteria**:

-   ✅ StartSession - создание новой сессии
-   ✅ GetNextQuestion - получение следующего вопроса из очереди
-   ✅ SubmitAnswer - сохранение ответа пользователя
-   ✅ Логика определения, когда сессия завершена
-   ✅ Unit тесты

**Затрагиваемые файлы**:

-   `internal/services/session_service.go`
-   `internal/services/session_service_test.go`

### Задача 3.6: Реализация Session Handlers

**Цель**: HTTP endpoints для работы с сессиями

**Acceptance Criteria**:

-   ✅ POST /api/v1/sessions - начало новой сессии
-   ✅ GET /api/v1/sessions/{id} - получение информации о сессии
-   ✅ GET /api/v1/sessions/{id}/next-question - следующий вопрос
-   ✅ POST /api/v1/sessions/{id}/answers - отправка ответа
-   ✅ Proper error handling и validation

**Затрагиваемые файлы**:

-   `internal/handlers/session.go`
-   `cmd/server/main.go` (регистрация routes)

### Задача 3.7: OpenAPI спецификация для Session endpoints

**Цель**: Документировать API для сессий

**Acceptance Criteria**:

-   ✅ Описаны все Session endpoints
-   ✅ Request/response schemas
-   ✅ Примеры взаимодействия

**Затрагиваемые файлы**:

-   `api/openapi.yaml` (обновление)

---

## ФАЗА 4: Модуль генерации резюме

### Задача 4.1: Создание модели Resume

**Цель**: Определить структуру данных резюме

**Acceptance Criteria**:

-   ✅ Структура Resume (id, session_id, content, format, created_at)
-   ✅ Поддержка форматов: text, json (для MVP)
-   ✅ Content в виде JSON с секциями

**Затрагиваемые файлы**:

-   `internal/models/resume.go`

### Задача 4.2: Создание миграции для Resume

**Цель**: Таблица для хранения резюме

**Acceptance Criteria**:

-   ✅ Миграция для таблицы `resumes`
-   ✅ Foreign key на sessions
-   ✅ JSONB поле для content

**Затрагиваемые файлы**:

-   `migrations/003_create_resumes.up.sql`
-   `migrations/003_create_resumes.down.sql`

### Задача 4.3: Реализация Resume Repository

**Цель**: Слой доступа к данным для резюме

**Acceptance Criteria**:

-   ✅ Методы: CreateResume, GetResumeByID, GetResumeBySessionID
-   ✅ Unit тесты

**Затрагиваемые файлы**:

-   `internal/repository/resume_repo.go`
-   `internal/repository/resume_repo_test.go`

### Задача 4.4: Реализация Resume Service - генерация

**Цель**: Логика генерации резюме из ответов пользователя

**Acceptance Criteria**:

-   ✅ GenerateResume - собирает все ответы из сессии
-   ✅ Структурирует данные по секциям (опыт, образование, навыки)
-   ✅ Базовое форматирование текста
-   ✅ Сохранение в БД
-   ✅ Unit тесты

**Затрагиваемые файлы**:

-   `internal/services/resume_service.go`
-   `internal/services/resume_service_test.go`

### Задача 4.5: Реализация Resume Handlers

**Цель**: HTTP endpoints для работы с резюме

**Acceptance Criteria**:

-   ✅ POST /api/v1/resumes/generate - генерация резюме
-   ✅ GET /api/v1/resumes/{id} - получение резюме (JSON)
-   ✅ GET /api/v1/resumes/{id}/download - скачивание (текстовый файл для MVP)
-   ✅ Proper error handling

**Затрагиваемые файлы**:

-   `internal/handlers/resume.go`
-   `cmd/server/main.go` (регистрация routes)

### Задача 4.6: OpenAPI спецификация для Resume endpoints

**Цель**: Документировать API для резюме

**Acceptance Criteria**:

-   ✅ Описаны все Resume endpoints
-   ✅ Request/response schemas

**Затрагиваемые файлы**:

-   `api/openapi.yaml` (обновление)

---

## ФАЗА 5: Финализация MVP

### Задача 5.1: Настройка CORS и middleware

**Цель**: Подготовить backend для работы с frontend

**Acceptance Criteria**:

-   ✅ CORS middleware
-   ✅ Logging middleware (запросы/ответы)
-   ✅ Recovery middleware (panic handling)
-   ✅ Request ID middleware

**Затрагиваемые файлы**:

-   `internal/middleware/cors.go`
-   `internal/middleware/logging.go`
-   `cmd/server/main.go`

### Задача 5.2: Health check endpoint

**Цель**: Endpoint для мониторинга состояния сервиса

**Acceptance Criteria**:

-   ✅ GET /health - проверка работоспособности
-   ✅ Проверка подключения к БД
-   ✅ Возврат версии приложения

**Затрагиваемые файлы**:

-   `internal/handlers/health.go`
-   `cmd/server/main.go`

### Задача 5.3: Документация и README

**Цель**: Описать проект и способы запуска

**Acceptance Criteria**:

-   ✅ README.md с описанием проекта
-   ✅ Инструкции по установке и запуску
-   ✅ Примеры использования API
-   ✅ Environment variables документированы

**Затрагиваемые файлы**:

-   `README.md`
-   `.env.example`

### Задача 5.4: Docker и docker-compose (опционально для MVP)

**Цель**: Упростить развертывание

**Acceptance Criteria**:

-   ✅ Dockerfile для backend
-   ✅ docker-compose.yaml с PostgreSQL и backend
-   ✅ Инструкции по запуску через Docker

**Затрагиваемые файлы**:

-   `Dockerfile`
-   `docker-compose.yaml`

---

## Пост-MVP задачи (после завершения основного функционала)

### Будущая задача: Интеграция реального MCP

-   Заменить mock MCP на реальный MCP клиент
-   Динамическая генерация вопросов на основе предыдущих ответов

### Будущая задача: Экспорт в PDF

-   Использовать библиотеку для генерации PDF
-   Шаблоны оформления резюме

### Будущая задача: Интеграция с Figma API

-   Генерация ссылки на резюме в Figma
-   Кастомизация шаблонов

### Будущая задача: Аутентификация

-   JWT tokens
-   User authentication system

---

## Validation checklist для каждой задачи

Перед тем как считать задачу завершенной, проверить:

1. ✅ Код проходит `black .`
2. ✅ Код проходит `flake8 .` и `mypy .`
3. ✅ Все ошибки и исключения обрабатываются явно
4. ✅ Есть unit-тесты для нового функционала (pytest)
5. ✅ Тесты проходят: `pytest`
6. ✅ Нет хардкода — конфигурация через env variables
7. ✅ Логирование важных операций
8. ✅ Документация обновлена (если требуется)
9. ✅ Пометь выполненные задания в файле copilot-tasks.md
