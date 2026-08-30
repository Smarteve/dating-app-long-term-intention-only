#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
MOBILE_DIR="${PROJECT_DIR}/mobile"
LOG_DIR="${PROJECT_DIR}/logs"
BACKEND_LOG_FILE="${LOG_DIR}/backend-$(date +%Y%m%d-%H%M%S).log"
BACKEND_PID=""
BACKEND_URL="http://127.0.0.1:8000"

mkdir -p "${LOG_DIR}"

cleanup() {
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
    echo
    echo "Stopping backend..."
    kill "${BACKEND_PID}"
    wait "${BACKEND_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

for command_name in docker uv node npm curl; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}" >&2
    exit 1
  fi
done

node_major="$(node -p 'process.versions.node.split(".")[0]')"
if (( node_major < 22 )); then
  echo "Node.js 22 or newer is required; found $(node --version)." >&2
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  compose_command=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_command=(docker-compose)
else
  echo "Docker Compose is required." >&2
  exit 1
fi

echo "Starting PostgreSQL..."
(
  cd "${BACKEND_DIR}"
  "${compose_command[@]}" up -d --wait db
)

echo "Applying database migrations..."
(
  cd "${BACKEND_DIR}"
  uv run alembic upgrade head
)

if curl --fail --silent "${BACKEND_URL}/health/ready" >/dev/null 2>&1; then
  echo "Backend is already healthy at ${BACKEND_URL}."
else
  echo "Starting backend..."
  echo "Backend log: ${BACKEND_LOG_FILE}"
  (
    cd "${BACKEND_DIR}"
    exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
      >>"${BACKEND_LOG_FILE}" 2>&1
  ) &
  BACKEND_PID=$!

  echo "Waiting for backend health check..."
  backend_ready=false
  for _ in {1..60}; do
    if curl --fail --silent "${BACKEND_URL}/health/ready" >/dev/null 2>&1; then
      backend_ready=true
      break
    fi

    if ! kill -0 "${BACKEND_PID}" 2>/dev/null; then
      echo "Backend exited before becoming healthy." >&2
      exit 1
    fi

    sleep 0.5
  done

  if [[ "${backend_ready}" != true ]]; then
    echo "Backend did not become healthy within 30 seconds." >&2
    exit 1
  fi

  echo "Backend is healthy."
fi

echo "Starting Expo web at http://localhost:8081..."
cd "${MOBILE_DIR}"
npm run web
