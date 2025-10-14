# 🎯 Инструкция по запуску Neuro Resume Backend

## ✅ Что уже сделано

### 1. База данных PostgreSQL

База данных **`neuro_resume`** создана и готова к работе:

-   **Host**: localhost
-   **Port**: 5432
-   **Database**: neuro_resume
-   **User**: postgres
-   **Password**: postgres

### 2. Миграции

Все миграции успешно накатаны:

-   ✅ `001_create_users` - Таблица пользователей
-   ✅ `002_create_sessions` - Таблица интервью-сессий и сообщений
-   ✅ `003_create_resumes` - Таблица резюме

Текущая версия: `003_create_resumes (head)`

### 3. Зависимости

Все необходимые пакеты установлены:

-   ✅ FastAPI 0.115.0
-   ✅ uvicorn 0.32.0
-   ✅ SQLAlchemy 2.0.23
-   ✅ asyncpg 0.29.0
-   ✅ alembic 1.12.1
-   ✅ bcrypt 4.1.1
-   ✅ pyjwt 2.8.0
-   ✅ email-validator 2.1.0
-   ✅ anthropic 0.40.0
-   ✅ openai 1.54.0

### 4. API Handlers

Реализованы все endpoints согласно OpenAPI спецификации:

-   ✅ Authentication (`/v1/auth`)
-   ✅ User Profile (`/v1/user`)
-   ✅ Interview Sessions (`/v1/interview`)

## 🚀 Команды для запуска

### Запустить сервер

```bash
# Из корня проекта с активированным venv
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Сервер будет доступен по адресу: **http://localhost:8000**

### API Документация

-   **Swagger UI**: http://localhost:8000/docs
-   **ReDoc**: http://localhost:8000/redoc

### Проверка работы

```bash
# Health check
curl http://localhost:8000/health

# Или откройте в браузере
http://localhost:8000/
```

## 📝 Управление миграциями

### Применить все миграции

```bash
./scripts/migrate.sh upgrade
```

### Откатить последнюю миграцию

```bash
./scripts/migrate.sh downgrade -1
```

### Посмотреть текущую версию

```bash
./scripts/migrate.sh current
```

### Создать новую миграцию

```bash
./scripts/migrate.sh revision "your migration message"
```

### История миграций

```bash
./scripts/migrate.sh history
```

## 🔧 Управление базой данных

### Пересоздать базу данных

```bash
./scripts/setup_database.sh
```

### Подключиться к базе через psql

```bash
sudo -u postgres psql neuro_resume
```

### Полезные SQL команды

```sql
-- Посмотреть все таблицы
\dt

-- Посмотреть структуру таблицы
\d users

-- Посмотреть всех пользователей
SELECT * FROM users;

-- Посмотреть сессии
SELECT * FROM interview_sessions;

-- Посмотреть резюме
SELECT * FROM resumes;
```

## 🧪 Тестирование API

### Регистрация пользователя

```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "firstName": "Test",
    "lastName": "User"
  }'
```

### Вход в систему

```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

Сохраните полученный `token` для дальнейших запросов.

### Создание интервью-сессии

```bash
curl -X POST http://localhost:8000/v1/interview/sessions \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"language": "ru"}'
```

### Получить профиль

```bash
curl -X GET http://localhost:8000/v1/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📁 Структура проекта

```
neuro-resume-backend/
├── app/
│   ├── handlers/          # API endpoints
│   │   ├── auth.py        # Аутентификация
│   │   ├── user.py        # Профиль пользователя
│   │   ├── interview.py   # Интервью-сессии
│   │   └── resume.py      # Резюме
│   ├── models/            # Pydantic и SQLAlchemy модели
│   ├── repository/        # Слой работы с БД
│   ├── services/          # Бизнес-логика (TODO)
│   ├── utils/             # Утилиты (JWT, bcrypt)
│   ├── db/                # Настройка БД
│   └── main.py            # Точка входа
├── migrations/            # Alembic миграции
├── scripts/               # Скрипты управления
│   ├── migrate.sh         # Управление миграциями
│   └── setup_database.sh  # Настройка БД
├── requirements.txt       # Зависимости Python
├── .env                   # Переменные окружения
└── alembic.ini            # Конфигурация Alembic
```

## ⚙️ Настройки (.env)

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/neuro_resume
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400
LOG_LEVEL=INFO
```

## 🐛 Troubleshooting

### Ошибка подключения к БД

```bash
# Проверьте, что PostgreSQL запущен
sudo systemctl status postgresql

# Запустите, если не запущен
sudo systemctl start postgresql
```

### Ошибка с миграциями

```bash
# Проверьте текущую версию
./scripts/migrate.sh current

# Посмотрите историю
./scripts/migrate.sh history

# Откатите к предыдущей версии
./scripts/migrate.sh downgrade -1
```

### Проблемы с зависимостями

```bash
# Переустановите все зависимости
pip install -r requirements.txt --force-reinstall
```

## 🎯 Следующие шаги

1. **AI Integration** - Интеграция с MCP для генерации вопросов интервью
2. **Resume Generation** - Реализация генерации PDF/DOCX резюме
3. **Tests** - Написание unit и integration тестов
4. **Authentication** - Добавить refresh tokens и token blacklist
5. **Validation** - Дополнительная валидация бизнес-логики
6. **Logging** - Настроить структурированное логирование

## 📚 Документация

-   **API Handlers**: см. `API_HANDLERS.md`
-   **OpenAPI Spec**: см. `openapi.yaml`
-   **Database Schema**: см. миграции в `migrations/versions/`

## ✅ Готово к работе!

Сервер запущен и готов принимать запросы на **http://localhost:8000** 🚀
