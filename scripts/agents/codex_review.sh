#!/bin/bash
# Read-only Codex review with a 30 minute watchdog and non-fatal ledger writes.
if [ "$#" -ne 3 ]; then
  echo "Usage: codex_review.sh <ticket> <report_out> <prompt_file>" >&2
  exit 2
fi

ticket="$1"
report_out="$2"
prompt_file="$3"
script_dir="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$script_dir/../.." && pwd)"
python="$root/.venv/bin/python"
[ -x "$python" ] || python="$(command -v python3)"
ledger="$script_dir/agent_ledger.py"

if [ ! -f "$prompt_file" ]; then
  echo "codex_review: prompt file not found" >&2
  exit 2
fi
mkdir -p "$(dirname "$report_out")"
started="$("$python" "$ledger" start "$ticket" codex --role reviewer 2>/dev/null)"
if [ -z "$started" ]; then
  started="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
fi

timeout_seconds="${CODEX_REVIEW_TIMEOUT:-1800}"
codex exec --skip-git-repo-check -s read-only -o "$report_out" "$(cat "$prompt_file")" < /dev/null &
codex_pid=$!
( sleep "$timeout_seconds"; kill -TERM "$codex_pid" 2>/dev/null ) &
alarm_pid=$!
wait "$codex_pid"
status=$?
kill "$alarm_pid" 2>/dev/null
wait "$alarm_pid" 2>/dev/null

"$python" "$ledger" end "$ticket" codex --role reviewer --started-at "$started" \
  --report "$report_out" --exit-code "$status"
exit "$status"
