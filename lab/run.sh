#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-pma-webauthn-lab}"
export PYTHONUNBUFFERED=1

BASE="${1:-http://127.0.0.1:18080}"

chmod +x poc.py

down() {
  echo "== docker compose down =="
  docker compose down --remove-orphans || true
}

wait_ready() {
  local i
  echo "== wait for http =="
  for i in $(seq 1 60); do
    if curl -fsS -o /dev/null "${BASE}/index.php?route=/"; then
      echo "IOC pma-up"
      return 0
    fi
    sleep 2
  done
  echo "FAIL phpMyAdmin did not become ready"
  docker compose logs --tail=80
  return 1
}

echo "== docker compose up =="
docker compose up -d --build

if ! wait_ready; then
  exit 1
fi

echo "== poc.py =="
python3 poc.py "${BASE}"
