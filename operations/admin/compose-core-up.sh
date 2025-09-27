#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR/docker"

# Ensure docker/.env exists to satisfy env_file references
if [ ! -f .env ]; then
  if [ -f ../.env ]; then
    ln -sf ../.env .env
  else
    echo "Warning: no .env found at repo root; continuing with defaults" >&2
  fi
fi

if command -v podman-compose >/dev/null 2>&1; then
  PC=podman-compose
elif command -v docker-compose >/dev/null 2>&1; then
  PC=docker-compose
else
  echo "Neither podman-compose nor docker-compose found" >&2
  exit 1
fi

echo "Using $PC"

$PC -f docker-compose.yml up -d postgres redis nats

sleep 2
$PC ps || true

if command -v podman >/dev/null 2>&1; then
  echo "\n-- podman ps --"
  podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi

echo "\nProbing NATS health..."
if curl -fsS http://localhost:8222/healthz >/dev/null 2>&1; then
  echo "NATS healthy"
else
  echo "NATS health probe failed; showing last logs"
  if command -v podman >/dev/null 2>&1; then podman logs --tail=200 syn_os_nats || true; fi
fi

echo "\nProbing Postgres..."
if command -v podman >/dev/null 2>&1; then
  podman exec syn_os_postgres pg_isready -U "${POSTGRES_USER:-syn_os_user}" -d "${POSTGRES_DB:-syn_os}" || true
fi

echo "\nProbing Redis..."
if command -v podman >/dev/null 2>&1; then
  podman exec syn_os_redis redis-cli ping || true
fi

echo "Done."
