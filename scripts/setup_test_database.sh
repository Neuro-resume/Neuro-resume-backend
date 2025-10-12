#!/bin/bash

# Скрипт для создания тестовой базы данных

set -e

echo "🔧 Настройка тестовой базы данных..."

# Параметры подключения (можно переопределить через env)
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
TEST_DB_NAME="neuro_resume_test"

echo "📊 Проверка существования базы данных ${TEST_DB_NAME}..."

# Проверяем, существует ли база данных
DB_EXISTS=$(PGPASSWORD=${POSTGRES_PASSWORD} psql -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -tAc "SELECT 1 FROM pg_database WHERE datname='${TEST_DB_NAME}'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" = "1" ]; then
    echo "⚠️  База данных ${TEST_DB_NAME} уже существует"
    read -p "Пересоздать базу данных? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Удаление существующей базы данных..."
        PGPASSWORD=${POSTGRES_PASSWORD} psql -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -c "DROP DATABASE ${TEST_DB_NAME};" 2>/dev/null || true
        
        echo "✨ Создание новой базы данных ${TEST_DB_NAME}..."
        PGPASSWORD=${POSTGRES_PASSWORD} psql -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -c "CREATE DATABASE ${TEST_DB_NAME};"
    else
        echo "⏭️  Пропускаем создание базы данных"
    fi
else
    echo "✨ Создание базы данных ${TEST_DB_NAME}..."
    PGPASSWORD=${POSTGRES_PASSWORD} psql -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -c "CREATE DATABASE ${TEST_DB_NAME};"
fi

echo "✅ Тестовая база данных готова!"
echo ""
echo "Теперь вы можете запустить тесты:"
echo "  python3 -m pytest tests/ -v"
