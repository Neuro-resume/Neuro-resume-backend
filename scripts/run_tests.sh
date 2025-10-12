#!/bin/bash

# Скрипт для запуска тестов

set -e

echo "🧪 Запуск тестов..."

# Переход в корневую директорию проекта
cd "$(dirname "$0")/.."

# Проверка существования тестовой базы данных
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
TEST_DB_NAME="neuro_resume_test"

echo "📊 Проверка тестовой базы данных..."
DB_EXISTS=$(PGPASSWORD=${POSTGRES_PASSWORD} psql -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -tAc "SELECT 1 FROM pg_database WHERE datname='${TEST_DB_NAME}'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" != "1" ]; then
    echo "❌ Тестовая база данных не найдена!"
    echo "Создайте её с помощью:"
    echo "  ./scripts/setup_test_database.sh"
    exit 1
fi

echo "✅ Тестовая база данных найдена"
echo ""

# Запуск pytest с параметрами
if [ -z "$1" ]; then
    # Если аргументы не переданы, запускаем все тесты
    echo "🚀 Запуск всех тестов..."
    python3 -m pytest tests/ -v --tb=short
else
    # Если переданы аргументы, используем их
    echo "🚀 Запуск тестов с параметрами: $@"
    python3 -m pytest "$@"
fi
