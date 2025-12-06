# NeuroResume

Сервис генерации профессиональных резюме через интерактивный диалог с AI. Главное отличие от аналогов — система сама задаёт вопросы пользователю, помогая структурировать информацию о профессиональном опыте.

## Как это работает

1. Пользователь регистрируется и создаёт сессию интервью
2. AI задаёт структурированные вопросы о карьере, навыках и опыте
3. На основе ответов формируется профессиональное резюме в формате Markdown
4. Резюме можно редактировать и сохранять несколько версий

## Технологии

| Компонент | Стек |
|-----------|------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, Alembic |
| Frontend | React 18, TypeScript, Vite, TailwindCSS |
| Инфраструктура | Docker, Docker Compose |

## Требования

- Docker и Docker Compose
- Node.js >= 18.0.0
- npm >= 9.0.0

## Быстрый старт

### Запуск всего проекта одной командой

```bash
chmod +x start.sh
./start.sh
```

Скрипт запустит backend (Docker) и frontend (Vite dev-server).

### Ручной запуск

**Backend:**

```bash
cd Neuro-resume-backend
docker compose up --build
```

Backend доступен на `http://localhost:8000`

**Frontend:**

```bash
cd Neuro-resume-frontend
npm install
cp .env.example .env  # настройте переменные окружения
npm run dev
```

Frontend доступен на `http://localhost:3000`

## Структура проекта

```
NeuroResume/
├── Neuro-resume-backend/    # FastAPI приложение
│   ├── app/                 # Исходный код
│   │   ├── handlers/        # API эндпоинты
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── repository/      # Слой работы с БД
│   │   └── services/        # Бизнес-логика
│   ├── migrations/          # Alembic миграции
│   └── docker-compose.yml
│
├── Neuro-resume-frontend/   # React приложение
│   ├── src/
│   │   ├── components/      # UI компоненты
│   │   ├── pages/           # Страницы
│   │   ├── services/        # API клиент
│   │   └── contexts/        # React контексты (auth)
│   └── package.json
│
├── README.md                # Этот файл
└── start.sh                 # Скрипт запуска проекта
```

## API

- OpenAPI спецификация: `Neuro-resume-backend/openapi.yaml`
- Postman коллекция: `Neuro-resume-backend/api/neuro-resume.postman_collection.json`
- Swagger UI: `http://localhost:8000/docs` (после запуска backend)

### Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/v1/auth/register` | Регистрация |
| POST | `/v1/auth/login` | Авторизация |
| GET | `/v1/user/me` | Профиль пользователя |
| POST | `/v1/interview/sessions` | Создать сессию интервью |
| POST | `/v1/interview/sessions/{id}/messages` | Отправить ответ |
| GET | `/v1/interview/sessions/{id}/resume` | Получить резюме |

## Разработка

### Backend тесты

```bash
cd Neuro-resume-backend
make tests       # unit/integration
make api-tests   # e2e
```

### Frontend линтинг

```bash
cd Neuro-resume-frontend
npm run lint
npm run type-check
```

