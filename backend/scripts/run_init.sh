#!/bin/bash
# Script to initialize database with roles and users
# Uses backend/venv when present.

cd "$(dirname "$0")/.."
ROOT="$(pwd)"
VENV_PY="$ROOT/venv/bin/python"
if [ -x "$VENV_PY" ]; then
  exec "$VENV_PY" -m scripts.init_db
fi
echo "ERROR: backend/venv not found. Create: cd backend && python -m venv venv && ./venv/bin/pip install -r requirements.txt" >&2
exit 1
