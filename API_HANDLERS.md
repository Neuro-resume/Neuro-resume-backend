# API Handlers Documentation

## Обзор

Все API handlers реализованы согласно OpenAPI спецификации (`openapi.yaml`). Handlers разбиты по функциональным группам.

## Структура handlers

```
app/handlers/
├── __init__.py          # Экспорт всех роутеров
├── auth.py              # Аутентификация
├── user.py              # Профиль пользователя
└── interview.py         # Интервью-сессии и markdown-резюме
```

## Endpoints

### Authentication (`/v1/auth`)

-   `POST /auth/register` - Регистрация нового пользователя
-   `POST /auth/login` - Вход в систему
-   `POST /auth/logout` - Выход из системы
-   `POST /auth/refresh` - Обновление токена

### User Profile (`/v1/user`)

-   `GET /user/profile` - Получить профиль текущего пользователя
-   `PATCH /user/profile` - Обновить профиль
-   `POST /user/change-password` - Изменить пароль

### Interview Sessions (`/v1/interview`)

-   `GET /interview/sessions` - Список сессий пользователя (с пагинацией)
-   `POST /interview/sessions` - Создать новую сессию
-   `GET /interview/sessions/{sessionId}` - Детали сессии
-   `DELETE /interview/sessions/{sessionId}` - Удалить сессию
-   `GET /interview/sessions/{sessionId}/messages` - История сообщений
-   `POST /interview/sessions/{sessionId}/messages` - Отправить сообщение
-   `POST /interview/sessions/{sessionId}/complete` - Завершить интервью

## Авторизация

Большинство endpoints требуют JWT токен в заголовке:

```
Authorization: Bearer <token>
```

Токен получается при регистрации или входе в систему.

## Утилиты

### Security (`app/utils/security.py`)

-   `hash_password()` - Хеширование паролей с bcrypt
-   `verify_password()` - Проверка паролей
-   `create_access_token()` - Создание JWT токена
-   `decode_access_token()` - Декодирование JWT токена
-   `get_current_user_id()` - FastAPI dependency для получения ID текущего пользователя

### Common Schemas (`app/models/common.py`)

-   `Pagination` - Схема пагинации
-   `ErrorResponse` - Стандартный формат ошибок
-   `create_paginated_response()` - Хелпер для создания пагинированных ответов
-   Helper функции для создания стандартных ошибок

## Repository Layer

### UserRepository (`app/repository/user.py`)

-   `create_user()` - Создание пользователя
-   `get_user_by_id()` - Получение по ID
-   `get_user_by_username()` - Получение по username
-   `get_user_by_email()` - Получение по email
-   `update_user()` - Обновление профиля
-   `update_password()` - Изменение пароля

### SessionRepository (`app/repository/session.py`)

-   `create_session()` - Создание интервью-сессии
-   `get_session_by_id()` - Получение сессии
-   `get_user_sessions()` - Список сессий пользователя (с пагинацией)
-   `update_session_progress()` - Обновление прогресса
-   `complete_session()` - Завершение сессии
-   `delete_session()` - Удаление сессии
-   `create_message()` - Создание сообщения в сессии
-   `get_session_messages()` - Получение всех сообщений сессии

## Примеры использования

### Регистрация и вход

```bash
# Регистрация
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "firstName": "John",
    "lastName": "Doe"
  }'

# Ответ
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "john_doe",
    "email": "john@example.com",
    ...
  },
  "expiresIn": 86400
}
```

### Создание сессии интервью

```bash
curl -X POST http://localhost:8000/v1/interview/sessions \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"language": "ru"}'
```

### Отправка сообщения

```bash
curl -X POST http://localhost:8000/v1/interview/sessions/{sessionId}/messages \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Я работал разработчиком в компании X более 3 лет"}'
```

## TODO: Требуется доработка

1. **AI Integration**: Интеграция с MCP для генерации вопросов и обработки ответов

    - В `interview.py`: метод `send_message()` использует placeholder ответ
    - Необходимо реализовать сервисный слой для работы с AI

2. **Resume Generation**: Автоматическая генерация содержимого резюме в формате Markdown и экспорт в файлы

-   В `interview.py`: метод `complete_interview()` сохраняет placeholder markdown
-   Необходимо интегрировать генерацию контента через AI и реализовать экспорт (PDF/DOCX/TXT)

3. **Tests**: Написать unit-тесты для всех handlers и repositories

4. **Validation**: Добавить дополнительную валидацию входных данных

## Запуск сервера

```bash
# Установить зависимости (включая новые: bcrypt, pyjwt)
pip install -r requirements.txt

# Запустить миграции
./scripts/migrate.sh

# Запустить сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Документация API будет доступна по адресу: http://localhost:8000/docs
