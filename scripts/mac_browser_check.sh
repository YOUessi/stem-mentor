#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ ! -x .venv/bin/python ]]; then
  echo "Create the Mac Python environment first." >&2
  exit 2
fi
if ! .venv/bin/python -c "import playwright" >/dev/null 2>&1; then
  echo "Playwright required: .venv/bin/python -m pip install playwright" >&2
  exit 2
fi
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [[ ! -x "$CHROME" ]]; then
  echo "Google Chrome is required for browser interaction tests." >&2
  exit 2
fi
PORT="$(printenv STEM_MENTOR_BROWSER_TEST_PORT || true)"
if [[ -z "$PORT" ]]; then
  PORT="$("$ROOT/.venv/bin/python" -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()')"
fi
if curl --noproxy '*' -fsS --max-time 2 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
  echo "Port $PORT is already occupied; choose another test port." >&2
  exit 3
fi
TMP_DB="$(mktemp -d /tmp/stem-mentor-ui.XXXXXXXX)"
mkdir -p artifacts/ui
cleanup(){
  if [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -rf -- "$TMP_DB"
}
SERVER_PID=""
trap cleanup EXIT
(
  cd backend
  export STEM_MENTOR_DB="$TMP_DB/demo.sqlite3"
  exec ../.venv/bin/python -m uvicorn app.main:app \
    --host 127.0.0.1 --port "$PORT" >"$ROOT/artifacts/ui/browser-test-server.log" 2>&1
) &
SERVER_PID=$!
ready=0
for i in {1..40}; do
  if curl --noproxy '*' -fsS --max-time 2 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    ready=1;break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then break; fi
  sleep .25
done
if [[ "$ready" -ne 1 ]]; then
  echo "Browser test server failed; inspect artifacts/ui/browser-test-server.log" >&2
  exit 4
fi
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python tests/browser/test_green_restore.py
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python tests/browser/test_learning_tools_v07.py
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python tests/browser/test_math_lab_v08.py
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python tests/browser/test_math_lab_numerics_v08.py
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python tests/browser/test_math_lab_v09.py
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python tests/browser/test_math_lab_keyboard_v09.py
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python tests/browser/test_math_lab_v09_extremes.py
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python tests/browser/test_math_lab_v010.py
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python tests/browser/test_math_lab_extremes_v010.py
STEM_MENTOR_URL="http://127.0.0.1:$PORT" .venv/bin/python -m pytest -q tests/browser/test_math_lab_review_v010.py
echo "Chrome browser suite passed; temporary synthetic database will be removed."
