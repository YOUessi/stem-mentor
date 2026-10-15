#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  echo "Create .venv first; see README.md." >&2
  exit 2
fi
cd "$ROOT/backend"
echo "STEM Mentor local simulator: http://127.0.0.1:8000"
exec "$ROOT/.venv/bin/python" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
