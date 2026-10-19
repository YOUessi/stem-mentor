#!/usr/bin/env bash
# Concurrent independent verification processes, not autonomous AI agents.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 2
if [[ ! -x .venv/bin/python ]]; then echo 'Missing Mac project virtual environment' >&2;exit 2;fi
if [[ "$#" -gt 1 ]] || [[ "$#" -eq 1 && "$1" != '--with-browser' ]]; then echo 'Usage: bash scripts/check_v010.sh [--with-browser]' >&2;exit 2;fi
RUN="$ROOT/artifacts/v010/runs/$(date '+%Y%m%dT%H%M%S')-$$"
mkdir -p "$RUN" || exit 2
export CHECK_RUN_DIR="$RUN"
export CHECK_STARTED_AT="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
export CHECK_COMMIT="$(git rev-parse HEAD)"
pids=()
interrupt(){ for pid in "${pids[@]}"; do kill -TERM "$pid" 2>/dev/null || true; done; exit 130; }
trap interrupt INT TERM
(node --test tests/node/*.test.cjs > "$RUN/node.log" 2>&1) & npid=$!;pids+=("$npid")
(cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q > "$RUN/pytest.log" 2>&1) & ppid=$!;pids+=("$ppid")
bpid='';brc=''
if [[ "${1:-}" == '--with-browser' ]]; then
  (bash scripts/mac_browser_check.sh > "$RUN/browser.log" 2>&1) & bpid=$!;pids+=("$bpid")
fi
printf 'Concurrent jobs: node=%s pytest=%s browser=%s\nLogs: %s\n' "$npid" "$ppid" "${bpid:-not-requested}" "$RUN"
wait "$npid"; nrc=$?
wait "$ppid"; prc=$?
if [[ -n "$bpid" ]]; then wait "$bpid";brc=$?;fi
pids=()
export CHECK_NODE_RC="$nrc" CHECK_PYTEST_RC="$prc" CHECK_BROWSER_RC="$brc"
export CHECK_NODE_PID="$npid" CHECK_PYTEST_PID="$ppid" CHECK_BROWSER_PID="$bpid"
.venv/bin/python - <<'PY'
import json,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(os.environ['CHECK_RUN_DIR'])
jobs=[]
for name in ('node','pytest','browser'):
    status=os.environ['CHECK_'+name.upper()+'_RC']
    if status=='': continue
    logfile=root/(name+'.log')
    jobs.append({'name':name,'pid':int(os.environ['CHECK_'+name.upper()+'_PID']),
                 'exit_code':int(status),'log':logfile.name,
                 'log_sha256':hashlib.sha256(logfile.read_bytes()).hexdigest()})
report={'mechanism':'CONCURRENT_PROCESSES_NOT_SUBAGENTS','commit':os.environ['CHECK_COMMIT'],
        'started_at':os.environ['CHECK_STARTED_AT'],'finished_at':datetime.now(timezone.utc).isoformat(),
        'passed':all(j['exit_code']==0 for j in jobs),'jobs':jobs}
(root/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
PY
report_rc=$?
printf '\nNode tail:\n';tail -10 "$RUN/node.log"
printf '\nBackend tail:\n';tail -14 "$RUN/pytest.log"
if [[ -n "$bpid" ]]; then printf '\nBrowser tail:\n';tail -18 "$RUN/browser.log";fi
if [[ "$nrc" -ne 0 || "$prc" -ne 0 || "${brc:-0}" -ne 0 || "$report_rc" -ne 0 ]]; then exit 1;fi
