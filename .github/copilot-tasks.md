# 🚀 MVP Development Roadmap - AI Resume Builder

> **Инструкция для Copilot**: После завершения каждой задачи, измени `[ ]` на `[x]` в соответствующей строке. Работай строго последовательно - не переходи к следующей задаче, пока текущая не отмечена как выполненная.

## Прогресс проекта

**Общий прогресс**: 0/25 задач выполнено

---

## 📦 ФАЗА 1: Инфраструктура и базовая настройка (0/3)

### Задача 1.1: Инициализация проекта и структуры

-   [ ] **Задача 1.1** - Инициализация проекта и структуры
    -   **Цель**: Создать базовую структуру проекта и настроить зависимости
    -   **Файлы**: `go.mod`, `go.sum`, структура папок
    -   **Критерии завершения**:
        -   ✅ Создан go.mod с правильным module name
        -   ✅ Создана структура папок: `cmd/`, `internal/`, `api/`, `migrations/`, `scripts/`
        -   ✅ Установлены базовые зависимости (http router, pgx/sqlx)
        -   ✅ Создан .gitignore для Go проектов

### Задача 1.2: Настройка подключения к PostgreSQL

-   [ ] **Задача 1.2** - Настройка подключения к PostgreSQL
    -   **Цель**: Реализовать подключение к БД с connection pool
    -   **Файлы**: `internal/db/connection.go`, `cmd/server/main.go`
    -   **Критерии завершения**:
        -   ✅ Создан пакет для работы с БД с connection pool
        -   ✅ Конфигурация через environment variables
        -   ✅ Реализована функция health check для БД
        -   ✅ Proper error handling и graceful shutdown

### Задача 1.3: Настройка системы миграций

-   [ ] **Задача 1.3** - Настройка системы миграций
    -   **Цель**: Подключить golang-migrate для управления схемой БД
    -   **Файлы**: `scripts/migrate.sh`, `migrations/`
    -   **Критерии завершения**:
        -   ✅ Установлен golang-migrate
        -   ✅ Создан скрипт для запуска миграций
        -   ✅ Миграции можно откатывать (up/down)

---

## 👤 ФАЗА 2: Модуль профилей пользователей (0/5)

### Задача 2.1: Создание модели и таблицы Profile

-   [ ] **Задача 2.1** - Создание модели и таблицы Profile
    -   **Цель**: Определить структуру данных профиля и создать таблицу в БД
    -   **Файлы**: `internal/models/profile.go`, `migrations/001_create_profiles.up.sql`, `migrations/001_create_profiles.down.sql`
    -   **Критерии завершения**:
        -   ✅ Создана Go структура Profile (id, name, email, created_at, updated_at)
        -   ✅ Создана миграция для таблицы profiles
        -   ✅ Email должен быть уникальным

### Задача 2.2: Реализация Profile Repository

-   [ ] **Задача 2.2** - Реализация Profile Repository
    -   **Цель**: Создать слой доступа к данным для профилей
    -   **Файлы**: `internal/repository/profile_repo.go`, `internal/repository/profile_repo_test.go`
    -   **Критерии завершения**:
        -   ✅ Интерфейс ProfileRepository (Create, GetByID, Update)
        -   ✅ Реализация с использованием pgx/sqlx
        -   ✅ Все методы принимают context.Context
        -   ✅ Unit тесты с mock DB

### Задача 2.3: Реализация Profile Service

-   [ ] **Задача 2.3** - Реализация Profile Service
    -   **Цель**: Создать бизнес-логику для работы с профилями
    -   **Файлы**: `internal/services/profile_service.go`, `internal/services/profile_service_test.go`
    -   **Критерии завершения**:
        -   ✅ Валидация данных профиля (email format, required fields)
        -   ✅ Методы CreateProfile, GetProfile, UpdateProfile
        -   ✅ Unit тесты для бизнес-логики

### Задача 2.4: Реализация Profile Handlers

-   [ ] **Задача 2.4** - Реализация Profile Handlers
    -   **Цель**: Создать HTTP endpoints для работы с профилями
    -   **Файлы**: `internal/handlers/profile.go`, `cmd/server/main.go`
    -   **Критерии завершения**:
        -   ✅ POST /api/v1/profiles - создание профиля
        -   ✅ GET /api/v1/profiles/{id} - получение профиля
        -   ✅ PUT /api/v1/profiles/{id} - обновление профиля
        -   ✅ Правильные HTTP status codes (201, 200, 400, 404, 500)
        -   ✅ JSON response format и request validation

### Задача 2.5: OpenAPI спецификация для Profile endpoints

-   [ ] **Задача 2.5** - OpenAPI спецификация для Profile endpoints
    -   **Цель**: Документировать API для профилей
    -   **Файлы**: `api/openapi.yaml`
    -   **Критерии завершения**:
        -   ✅ Описаны все Profile endpoints в OpenAPI формате
        -   ✅ Указаны request/response schemas
        -   ✅ Примеры запросов и ответов

---

## 💬 ФАЗА 3: Модуль чат-сессий (0/7)

### Задача 3.1: Создание моделей Session, Question, Answer

-   [ ] **Задача 3.1** - Создание моделей Session, Question, Answer
    -   **Цель**: Определить структуры данных для сессий и вопросов
    -   **Файлы**: `internal/models/session.go`, `internal/models/question.go`, `internal/models/answer.go`
    -   **Критерии завершения**:
        -   ✅ Структура Session (id, profile_id, status, created_at)
        -   ✅ Структура Question (id, session_id, category, text, order)
        -   ✅ Структура Answer (id, question_id, answer_text, created_at)
        -   ✅ Enum для статусов сессии (active, completed, abandoned)
        -   ✅ Enum для категорий вопросов

### Задача 3.2: Создание миграций для Session, Question, Answer

-   [ ] **Задача 3.2** - Создание миграций для Session, Question, Answer
    -   **Цель**: Создать таблицы в БД для сессий
    -   **Файлы**: `migrations/002_create_sessions.up.sql`, `migrations/002_create_sessions.down.sql`
    -   **Критерии завершения**:
        -   ✅ Миграция для таблицы chat_sessions
        -   ✅ Миграция для таблицы questions
        -   ✅ Миграция для таблицы answers
        -   ✅ Foreign keys настроены правильно
        -   ✅ Индексы для оптимизации запросов

### Задача 3.3: Реализация Session Repository

-   [ ] **Задача 3.3** - Реализация Session Repository
    -   **Цель**: Слой доступа к данным для сессий
    -   **Файлы**: `internal/repository/session_repo.go`, `internal/repository/session_repo_test.go`
    -   **Критерии завершения**:
        -   ✅ Методы: CreateSession, GetSession, UpdateSessionStatus
        -   ✅ Методы: SaveQuestion, SaveAnswer, GetSessionQuestions
        -   ✅ Unit тесты

### Задача 3.4: Базовая интеграция с MCP (заглушка)

-   [ ] **Задача 3.4** - Базовая интеграция с MCP (заглушка)
    -   **Цель**: Создать интерфейс для работы с MCP с mock реализацией
    -   **Файлы**: `internal/services/mcp_client.go`, `internal/services/mcp_mock.go`
    -   **Критерии завершения**:
        -   ✅ Интерфейс MCPClient с методом GetNextQuestion
        -   ✅ Mock реализация с фиксированными вопросами
        -   ✅ 2-3 вопроса для каждой категории (опыт, образование, навыки)

### Задача 3.5: Реализация Session Service

-   [ ] **Задача 3.5** - Реализация Session Service
    -   **Цель**: Бизнес-логика управления сессиями
    -   **Файлы**: `internal/services/session_service.go`, `internal/services/session_service_test.go`
    -   **Критерии завершения**:
        -   ✅ StartSession - создание новой сессии
        -   ✅ GetNextQuestion - получение следующего вопроса
        -   ✅ SubmitAnswer - сохранение ответа пользователя
        -   ✅ Логика определения завершения сессии
        -   ✅ Unit тесты

### Задача 3.6: Реализация Session Handlers

-   [ ] **Задача 3.6** - Реализация Session Handlers
    -   **Цель**: HTTP endpoints для работы с сессиями
    -   **Файлы**: `internal/handlers/session.go`, `cmd/server/main.go`
    -   **Критерии завершения**:
        -   ✅ POST /api/v1/sessions - начало новой сессии
        -   ✅ GET /api/v1/sessions/{id} - получение информации о сессии
        -   ✅ GET /api/v1/sessions/{id}/next-question - следующий вопрос
        -   ✅ POST /api/v1/sessions/{id}/answers - отправка ответа
        -   ✅ Proper error handling и validation

### Задача 3.7: OpenAPI спецификация для Session endpoints

-   [ ] **Задача 3.7** - OpenAPI спецификация для Session endpoints
    -   **Цель**: Документировать API для сессий
    -   **Файлы**: `api/openapi.yaml`
    -   **Критерии завершения**:
        -   ✅ Описаны все Session endpoints
        -   ✅ Request/response schemas
        -   ✅ Примеры взаимодействия

---

## 📄 ФАЗА 4: Модуль генерации резюме (0/6)

### Задача 4.1: Создание модели Resume

-   [ ] **Задача 4.1** - Создание модели Resume
    -   **Цель**: Определить структуру данных резюме
    -   **Файлы**: `internal/models/resume.go`
    -   **Критерии завершения**:
        -   ✅ Структура Resume (id, session_id, content, format, created_at)
        -   ✅ Поддержка форматов: text, json (для MVP)
        -   ✅ Content в виде JSON с секциями

### Задача 4.2: Создание миграции для Resume

-   [ ] **Задача 4.2** - Создание миграции для Resume
    -   **Цель**: Таблица для хранения резюме
    -   **Файлы**: `migrations/003_create_resumes.up.sql`, `migrations/003_create_resumes.down.sql`
    -   **Критерии завершения**:
        -   ✅ Миграция для таблицы resumes
        -   ✅ Foreign key на sessions
        -   ✅ JSONB поле для content

### Задача 4.3: Реализация Resume Repository

-   [ ] **Задача 4.3** - Реализация Resume Repository
    -   **Цель**: Слой доступа к данным для резюме
    -   **Файлы**: `internal/repository/resume_repo.go`, `internal/repository/resume_repo_test.go`
    -   **Критерии завершения**:
        -   ✅ Методы: CreateResume, GetResumeByID, GetResumeBySessionID
        -   ✅ Unit тесты

### Задача 4.4: Реализация Resume Service - генерация

-   [ ] **Задача 4.4** - Реализация Resume Service - генерация
    -   **Цель**: Логика генерации резюме из ответов пользователя
    -   **Файлы**: `internal/services/resume_service.go`, `internal/services/resume_service_test.go`
    -   **Критерии завершения**:
        -   ✅ GenerateResume - собирает все ответы из сессии
        -   ✅ Структурирует данные по секциям (опыт, образование, навыки)
        -   ✅ Базовое форматирование текста
        -   ✅ Сохранение в БД
        -   ✅ Unit тесты

### Задача 4.5: Реализация Resume Handlers

-   [ ] **Задача 4.5** - Реализация Resume Handlers
    -   **Цель**: HTTP endpoints для работы с резюме
    -   **Файлы**: `internal/handlers/resume.go`, `cmd/server/main.go`
    -   **Критерии завершения**:
        -   ✅ POST /api/v1/resumes/generate - генерация резюме
        -   ✅ GET /api/v1/resumes/{id} - получение резюме (JSON)
        -   ✅ GET /api/v1/resumes/{id}/download - скачивание (текстовый файл для MVP)
        -   ✅ Proper error handling

### Задача 4.6: OpenAPI спецификация для Resume endpoints

-   [ ] **Задача 4.6** - OpenAPI спецификация для Resume endpoints
    -   **Цель**: Документировать API для резюме
    -   **Файлы**: `api/openapi.yaml`
    -   **Критерии завершения**:
        -   ✅ Описаны все Resume endpoints
        -   ✅ Request/response schemas

---

## ✨ ФАЗА 5: Финализация MVP (0/4)

### Задача 5.1: Настройка CORS и middleware

-   [ ] **Задача 5.1** - Настройка CORS и middleware
    -   **Цель**: Подготовить backend для работы с frontend
    -   **Файлы**: `internal/middleware/cors.go`, `internal/middleware/logging.go`, `cmd/server/main.go`
    -   **Критерии завершения**:
        -   ✅ CORS middleware
        -   ✅ Logging middleware (запросы/ответы)
        -   ✅ Recovery middleware (panic handling)
        -   ✅ Request ID middleware

### Задача 5.2: Health check endpoint

-   [ ] **Задача 5.2** - Health check endpoint
    -   **Цель**: Endpoint для мониторинга состояния сервиса
    -   **Файлы**: `internal/handlers/health.go`, `cmd/server/main.go`
    -   **Критерии завершения**:
        -   ✅ GET /health - проверка работоспособности
        -   ✅ Проверка подключения к БД
        -   ✅ Возврат версии приложения

### Задача 5.3: Документация и README

-   [ ] **Задача 5.3** - Документация и README
    -   **Цель**: Описать проект и способы запуска
    -   **Файлы**: `README.md`, `.env.example`
    -   **Критерии завершения**:
        -   ✅ README.md с описанием проекта
        -   ✅ Инструкции по установке и запуску
        -   ✅ Примеры использования API
        -   ✅ Environment variables документированы

### Задача 5.4: Docker и docker-compose (опционально)

-   [ ] **Задача 5.4** - Docker и docker-compose (опционально)
    -   **Цель**: Упростить развертывание
    -   **Файлы**: `Dockerfile`, `docker-compose.yaml`
    -   **Критерии завершения**:
        -   ✅ Dockerfile для backend
        -   ✅ docker-compose.yaml с PostgreSQL и backend
        -   ✅ Инструкции по запуску через Docker

---

## 🔮 Пост-MVP задачи (после завершения основного функционала)

-   [ ] Интеграция реального MCP (замена mock на реальный клиент)
-   [ ] Экспорт резюме в PDF
-   [ ] Интеграция с Figma API
-   [ ] Система аутентификации (JWT tokens)

---

## 📝 Validation Checklist (применять к каждой задаче)

Перед тем как отметить задачу как выполненную (`[x]`), убедись что:

1. ✅ Код проходит `gofmt`
2. ✅ Код проходит `golangci-lint run`
3. ✅ Все ошибки обрабатываются явно
4. ✅ Есть unit тесты для нового функционала
5. ✅ Тесты проходят: `go test ./...`
6. ✅ Нет хардкода - конфигурация через env variables
7. ✅ Логирование важных операций
8. ✅ Документация обновлена (если требуется)

---

**Последнее обновление**: 03.10.2025
