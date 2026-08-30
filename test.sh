#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
TEST_DATABASE_URL="postgresql+psycopg://dating_app_test:dating_app_test@localhost:5433/dating_app_test"

for command_name in docker uv; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}" >&2
    exit 1
  fi
done

if docker compose version >/dev/null 2>&1; then
  compose_command=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_command=(docker-compose)
else
  echo "Docker Compose is required." >&2
  exit 1
fi

echo "Starting test PostgreSQL..."
(
  cd "${BACKEND_DIR}"
  "${compose_command[@]}" up -d --wait test-db
)

echo "Applying migrations to the test database..."
(
  cd "${BACKEND_DIR}"
  APP_ENV=test \
    DATABASE_URL="${TEST_DATABASE_URL}" \
    IDENTITY_PROVIDER_ISSUER="https://identity-provider.test/auth/v1" \
    IDENTITY_PROVIDER_AUDIENCE=authenticated \
    uv run alembic upgrade head
)

echo "Running backend tests..."
(
  cd "${BACKEND_DIR}"
  APP_ENV=test \
    DATABASE_URL="${TEST_DATABASE_URL}" \
    IDENTITY_PROVIDER_ISSUER="https://identity-provider.test/auth/v1" \
    IDENTITY_PROVIDER_AUDIENCE=authenticated \
    uv run pytest
)
