#!/bin/sh
set -eu

printf 'Waiting for database migrations to complete...\n'

attempt=0
until alembic upgrade head; do
  attempt=$((attempt + 1))
  printf 'Alembic failed (attempt %d). Retrying in 5 seconds...\n' "$attempt"
  sleep 5
done

printf 'Starting API server...\n'
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
