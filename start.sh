#!/bin/bash

# Скрипт для запуска всего проекта NeuroResume из директории backend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$SCRIPT_DIR"
FRONTEND_DIR="$PROJECT_ROOT/Neuro-resume-frontend"

echo "🚀 Запуск NeuroResume..."
echo ""

# Проверка наличия docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    exit 1
fi

# Проверка наличия docker compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose не установлен"
    exit 1
fi

# Проверка наличия node и npm
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm не установлен"
    exit 1
fi

# Запуск backend
echo "📦 Запуск Backend (Docker)..."
cd "$BACKEND_DIR"
docker compose up -d --build

echo "⏳ Ожидание запуска backend..."
sleep 5

# Проверка здоровья backend
MAX_RETRIES=30
RETRY_COUNT=0
while ! curl -s http://localhost:8000/docs > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Backend не запустился. Проверьте логи: docker compose logs"
        exit 1
    fi
    echo "   Попытка $RETRY_COUNT/$MAX_RETRIES..."
    sleep 2
done

echo "✅ Backend запущен на http://localhost:8000"
echo ""

# Запуск frontend
echo "🎨 Запуск Frontend..."
cd "$FRONTEND_DIR"

# Установка зависимостей если нужно
if [ ! -d "node_modules" ]; then
    echo "   Установка зависимостей..."
    npm install
fi

echo "✅ Frontend запускается на http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 NeuroResume готов к работе!"
echo ""
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "   Для остановки: Ctrl+C и 'docker compose down' в backend/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Запуск frontend в foreground
npm run dev
