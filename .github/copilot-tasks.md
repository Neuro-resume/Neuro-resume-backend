# 🚀 MVP Development Roadmap - AI Resume Builder (Python)

> **Инструкция для Copilot**: После завершения каждой задачи, измени `[ ]` на `[x]` в соответствующей строке. Работай строго последовательно - не переходи к следующей задаче, пока текущая не отмечена как выполненная.

## Прогресс проекта

**Общий прогресс**: 0/26 задач выполнено

---

## 🔌 ФАЗА 0: MCP Протокол (0/1)

### Задача 0.1: Реализация MCP-протокола для работы с ИИ

-   [ ] **Задача 0.1** - Реализация MCP-протокола для работы с ИИ
    -   **Цель**: Создать базовый MCP server для интеграции с нейросетью
    -   **Файлы**: `app/mcp/server.py`, `app/mcp/tools.py`, `app/mcp/prompts.py`
    -   **Критерии завершения**:
        -   ✅ Создан MCP server с базовыми tools
        -   ✅ Реализованы tools для генерации вопросов
        -   ✅ Настроены prompts для категорий вопросов
        -   ✅ Интеграция с Claude/OpenAI API
        -   ✅ Тестирование через MCP Inspector

---

## 📦 ФАЗА 1: Инфраструктура и базовая настройка (0/3)

### Задача 1.1: Инициализация проекта и структуры

-   [ ] **Задача 1.1** - Инициализация проекта и структуры
    -   **Цель**: Создать базовую структуру проекта и настроить зависимости
    -   **Файлы**: `requirements.txt`, `pyproject.toml`, структура папок
    -   **Критерии завершения**:
        -   ✅ Создан requirements.txt с базовыми зависимостями (FastAPI, SQLAlchemy, Alembic)
        -   ✅ Создана структура папок: `app/`, `api/`, `migrations/`, `scripts/`
        -   ✅ Настроен pyproject.toml для black, flake8, mypy
        -   ✅ Создан .gitignore для Python проектов

### Задача 1.2: Настройка подключения к PostgreSQL

-   [ ] **Задача 1.2** - Настройка подключения к PostgreSQL
    -   **Цель**: Реализовать подключение к БД через SQLAlchemy/asyncpg
    -   **Файлы**: `app/db/connection.py`, `app/main.py`
    -   **Критерии завершения**:
        -   ✅ Создан модуль для работы с БД (engine, session)
        -   ✅ Конфигурация через environment variables (pydantic Settings)
        -   ✅ Реализована функция health check для БД
        -   ✅ Обработка исключений и graceful shutdown

### Задача 1.3: Настройка системы миграций

-   [ ] **Задача 1.3** - Настройка системы миграций
    -   **Цель**: Подключить Alembic для управления схемой БД
    -   **Файлы**: `scripts/migrate.sh`, `migrations/`, `alembic.ini`
    -   **Критерии завершения**:
        -   ✅ Alembic установлен и инициализирован
        -   ✅ Создан скрипт для запуска миграций
        -   ✅ Миграции можно откатывать (upgrade/downgrade)

---

## 👤 ФАЗА 2: Модуль профилей пользователей (0/5)

### Задача 2.1: Создание модели и таблицы Profile

-   [ ] **Задача 2.1** - Создание модели и таблицы Profile
    -   **Цель**: Определить структуру данных профиля и создать таблицу в БД
    -   **Файлы**: `app/models/profile.py`, `migrations/versions/001_create_profiles.py`
    -   **Критерии завершения**:
        -   ✅ Создана SQLAlchemy модель Profile (id, name, email, created_at, updated_at)
        -   ✅ Создана Pydantic схема для валидации
        -   ✅ Создана миграция Alembic для таблицы profiles
        -   ✅ Email должен быть уникальным

### Задача 2.2: Реализация Profile Repository

-   [ ] **Задача 2.2** - Реализация Profile Repository
    -   **Цель**: Создать слой доступа к данным для профилей
    -   **Файлы**: `app/repository/profile_repo.py`, `tests/test_profile_repo.py`
    -   **Критерии завершения**:
        -   ✅ Класс ProfileRepository с методами (create, get_by_id, update)
        -   ✅ Использование async/await для асинхронных операций
        -   ✅ Обработка исключений SQLAlchemy
        -   ✅ Unit тесты с pytest и mock БД

### Задача 2.3: Реализация Profile Service

-   [ ] **Задача 2.3** - Реализация Profile Service
    -   **Цель**: Создать бизнес-логику для работы с профилями
    -   **Файлы**: `app/services/profile_service.py`, `tests/test_profile_service.py`
    -   **Критерии завершения**:
        -   ✅ Валидация данных профиля через Pydantic (email format, required fields)
        -   ✅ Методы create_profile, get_profile, update_profile
        -   ✅ Unit тесты для бизнес-логики

### Задача 2.4: Реализация Profile Handlers

-   [ ] **Задача 2.4** - Реализация Profile Handlers
    -   **Цель**: Создать HTTP endpoints для работы с профилями
    -   **Файлы**: `app/handlers/profile.py`, `app/main.py`
    -   **Критерии завершения**:
        -   ✅ POST /api/v1/profiles - создание профиля
        -   ✅ GET /api/v1/profiles/{id} - получение профиля
        -   ✅ PUT /api/v1/profiles/{id} - обновление профиля
        -   ✅ Правильные HTTP status codes (201, 200, 400, 404, 500)
        -   ✅ Использование FastAPI Depends для DI
        -   ✅ Request/Response через Pydantic модели

### Задача 2.5: OpenAPI спецификация для Profile endpoints

-   [ ] **Задача 2.5** - OpenAPI спецификация для Profile endpoints
    -   **Цель**: Документировать API для профилей (FastAPI генерирует автоматически)
    -   **Файлы**: `app/handlers/profile.py` (docstrings)
    -   **Критерии завершения**:
        -   ✅ Добавлены docstrings для всех endpoints
        -   ✅ Настроены response_model в декораторах
        -   ✅ Примеры в OpenAPI доступны через /docs

---

## 💬 ФАЗА 3: Модуль чат-сессий (0/7)

### Задача 3.1: Создание моделей Session, Question, Answer

-   [ ] **Задача 3.1** - Создание моделей Session, Question, Answer
    -   **Цель**: Определить структуры данных для сессий и вопросов
    -   **Файлы**: `app/models/session.py`, `app/models/question.py`, `app/models/answer.py`
    -   **Критерии завершения**:
        -   ✅ SQLAlchemy модели Session (id, profile_id, status, created_at)
        -   ✅ SQLAlchemy модели Question (id, session_id, category, text, order)
        -   ✅ SQLAlchemy модели Answer (id, question_id, answer_text, created_at)
        -   ✅ Enum для статусов сессии (active, completed, abandoned)
        -   ✅ Enum для категорий вопросов

### Задача 3.2: Создание миграций для Session, Question, Answer

-   [ ] **Задача 3.2** - Создание миграций для Session, Question, Answer
    -   **Цель**: Создать таблицы в БД для сессий
    -   **Файлы**: `migrations/versions/002_create_sessions.py`
    -   **Критерии завершения**:
        -   ✅ Миграция Alembic для таблицы chat_sessions
        -   ✅ Миграция для таблицы questions
        -   ✅ Миграция для таблицы answers
        -   ✅ Foreign keys настроены правильно
        -   ✅ Индексы для оптимизации запросов

### Задача 3.3: Реализация Session Repository

-   [ ] **Задача 3.3** - Реализация Session Repository
    -   **Цель**: Слой доступа к данным для сессий
    -   **Файлы**: `app/repository/session_repo.py`, `tests/test_session_repo.py`
    -   **Критерии завершения**:
        -   ✅ Методы: create_session, get_session, update_session_status
        -   ✅ Методы: save_question, save_answer, get_session_questions
        -   ✅ Unit тесты с pytest

### Задача 3.4: Интеграция с MCP для генерации вопросов

-   [ ] **Задача 3.4** - Интеграция с MCP для генерации вопросов
    -   **Цель**: Использовать MCP server (из задачи 0.1) для динамической генерации вопросов
    -   **Файлы**: `app/services/mcp_client.py`, `tests/test_mcp_client.py`
    -   **Критерии завершения**:
        -   ✅ Класс MCPClient с методом get_next_question
        -   ✅ Интеграция с MCP server для вызова tools
        -   ✅ Обработка ответов от ИИ
        -   ✅ Fallback на mock вопросы при недоступности MCP
        -   ✅ Unit тесты

### Задача 3.5: Реализация Session Service

-   [ ] **Задача 3.5** - Реализация Session Service
    -   **Цель**: Бизнес-логика управления сессиями
    -   **Файлы**: `app/services/session_service.py`, `tests/test_session_service.py`
    -   **Критерии завершения**:
        -   ✅ start_session - создание новой сессии
        -   ✅ get_next_question - получение следующего вопроса через MCP
        -   ✅ submit_answer - сохранение ответа пользователя
        -   ✅ Логика определения завершения сессии
        -   ✅ Unit тесты

### Задача 3.6: Реализация Session Handlers

-   [ ] **Задача 3.6** - Реализация Session Handlers
    -   **Цель**: HTTP endpoints для работы с сессиями
    -   **Файлы**: `app/handlers/session.py`, `app/main.py`
    -   **Критерии завершения**:
        -   ✅ POST /api/v1/sessions - начало новой сессии
        -   ✅ GET /api/v1/sessions/{id} - получение информации о сессии
        -   ✅ GET /api/v1/sessions/{id}/next-question - следующий вопрос
        -   ✅ POST /api/v1/sessions/{id}/answers - отправка ответа
        -   ✅ Использование FastAPI Depends и async handlers
        -   ✅ Proper error handling и validation

### Задача 3.7: OpenAPI спецификация для Session endpoints

-   [ ] **Задача 3.7** - OpenAPI спецификация для Session endpoints
    -   **Цель**: Документировать API для сессий
    -   **Файлы**: `app/handlers/session.py` (docstrings)
    -   **Критерии завершения**:
        -   ✅ Добавлены docstrings для всех endpoints
        -   ✅ Настроены response_model
        -   ✅ Примеры взаимодействия в /docs

---

## 📄 ФАЗА 4: Модуль генерации резюме (0/6)

### Задача 4.1: Создание модели Resume

-   [ ] **Задача 4.1** - Создание модели Resume
    -   **Цель**: Определить структуру данных резюме
    -   **Файлы**: `app/models/resume.py`
    -   **Критерии завершения**:
        -   ✅ SQLAlchemy модель Resume (id, session_id, content, format, created_at)
        -   ✅ Pydantic схемы для валидации
        -   ✅ Поддержка форматов: text, json (для MVP)
        -   ✅ Content в виде JSON с секциями

### Задача 4.2: Создание миграции для Resume

-   [ ] **Задача 4.2** - Создание миграции для Resume
    -   **Цель**: Таблица для хранения резюме
    -   **Файлы**: `migrations/versions/003_create_resumes.py`
    -   **Критерии завершения**:
        -   ✅ Миграция Alembic для таблицы resumes
        -   ✅ Foreign key на sessions
        -   ✅ JSONB поле для content (PostgreSQL)

### Задача 4.3: Реализация Resume Repository

-   [ ] **Задача 4.3** - Реализация Resume Repository
    -   **Цель**: Слой доступа к данным для резюме
    -   **Файлы**: `app/repository/resume_repo.py`, `tests/test_resume_repo.py`
    -   **Критерии завершения**:
        -   ✅ Методы: create_resume, get_resume_by_id, get_resume_by_session_id
        -   ✅ Unit тесты с pytest

### Задача 4.4: Реализация Resume Service - генерация

-   [ ] **Задача 4.4** - Реализация Resume Service - генерация
    -   **Цель**: Логика генерации резюме из ответов пользователя
    -   **Файлы**: `app/services/resume_service.py`, `tests/test_resume_service.py`
    -   **Критерии завершения**:
        -   ✅ generate_resume - собирает все ответы из сессии
        -   ✅ Структурирует данные по секциям (опыт, образование, навыки)
        -   ✅ Использование MCP для улучшения форматирования (опционально)
        -   ✅ Базовое форматирование текста
        -   ✅ Сохранение в БД
        -   ✅ Unit тесты

### Задача 4.5: Реализация Resume Handlers

-   [ ] **Задача 4.5** - Реализация Resume Handlers
    -   **Цель**: HTTP endpoints для работы с резюме
    -   **Файлы**: `app/handlers/resume.py`, `app/main.py`
    -   **Критерии завершения**:
        -   ✅ POST /api/v1/resumes/generate - генерация резюме
        -   ✅ GET /api/v1/resumes/{id} - получение резюме (JSON)
        -   ✅ GET /api/v1/resumes/{id}/download - скачивание (текстовый файл для MVP)
        -   ✅ Использование StreamingResponse для download
        -   ✅ Proper error handling

### Задача 4.6: OpenAPI спецификация для Resume endpoints

-   [ ] **Задача 4.6** - OpenAPI спецификация для Resume endpoints
    -   **Цель**: Документировать API для резюме
    -   **Файлы**: `app/handlers/resume.py` (docstrings)
    -   **Критерии завершения**:
        -   ✅ Добавлены docstrings для всех endpoints
        -   ✅ Настроены response_model
        -   ✅ Примеры в /docs

---

## ✨ ФАЗА 5: Финализация MVP (0/4)

### Задача 5.1: Настройка CORS и middleware

-   [ ] **Задача 5.1** - Настройка CORS и middleware
    -   **Цель**: Подготовить backend для работы с frontend
    -   **Файлы**: `app/middleware/cors.py`, `app/middleware/logging.py`, `app/main.py`
    -   **Критерии завершения**:
        -   ✅ CORS middleware через FastAPI CORSMiddleware
        -   ✅ Logging middleware для запросов/ответов
        -   ✅ Exception handlers для обработки ошибок
        -   ✅ Request ID middleware (UUID для каждого запроса)

### Задача 5.2: Health check endpoint

-   [ ] **Задача 5.2** - Health check endpoint
    -   **Цель**: Endpoint для мониторинга состояния сервиса
    -   **Файлы**: `app/handlers/health.py`, `app/main.py`
    -   **Критерии завершения**:
        -   ✅ GET /health - проверка работоспособности
        -   ✅ Проверка подключения к БД
        -   ✅ Возврат версии приложения и статуса
        -   ✅ Использование Pydantic модели для ответа

### Задача 5.3: Документация и README

-   [ ] **Задача 5.3** - Документация и README
    -   **Цель**: Описать проект и способы запуска
    -   **Файлы**: `README.md`, `.env.example`
    -   **Критерии завершения**:
        -   ✅ README.md с описанием проекта
        -   ✅ Инструкции по установке и запуску (pip install, alembic, uvicorn)
        -   ✅ Примеры использования API
        -   ✅ Environment variables документированы в .env.example

### Задача 5.4: Docker и docker-compose (опционально)

-   [ ] **Задача 5.4** - Docker и docker-compose (опционально)
    -   **Цель**: Упростить развертывание
    -   **Файлы**: `Dockerfile`, `docker-compose.yaml`
    -   **Критерии завершения**:
        -   ✅ Dockerfile для Python backend (multi-stage build)
        -   ✅ docker-compose.yaml с PostgreSQL и backend
        -   ✅ Инструкции по запуску через Docker
        -   ✅ Volumes для persistence данных

---

## 🔮 Пост-MVP задачи (после завершения основного функционала)

-   [ ] Улучшение MCP интеграции (контекстно-зависимые вопросы)
-   [ ] Экспорт резюме в PDF (использовать reportlab или weasyprint)
-   [ ] Интеграция с Figma API для визуализации резюме
-   [ ] Система аутентификации (JWT tokens, OAuth2)
-   [ ] Rate limiting для API endpoints
-   [ ] Кэширование через Redis

---

## 📝 Validation Checklist (применять к каждой задаче)

Перед тем как отметить задачу как выполненную (`[x]`), убедись что:

1. ✅ Код проходит `black .`
2. ✅ Код проходит `flake8 .` и `mypy .`
3. ✅ Все исключения обрабатываются явно (try/except)
4. ✅ Есть unit тесты для нового функционала (pytest)
5. ✅ Тесты проходят: `pytest`
6. ✅ Нет хардкода - конфигурация через env variables
7. ✅ Логирование важных операций через logging
8. ✅ Документация обновлена (если требуется)
9. ✅ Docstrings добавлены для всех публичных функций/классов

---

**Последнее обновление**: 12.10.2025
