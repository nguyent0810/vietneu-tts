#!/bin/bash
# Cron wrapper cho short_batch_runner.py -- chạy độc lập với phiên Claude,
# sống qua nhiều ngày kể cả khi đóng CLI. Log JSON 1 dòng/lần chạy vào
# daily_run_log.jsonl để job báo cáo cuối (hoặc người dùng) đọc lại lịch sử.
set -euo pipefail
cd "/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS"

# launchd runs với PATH tối giản (/usr/bin:/bin:/usr/sbin:/sbin) -- "python3"
# trần sẽ resolve nhầm sang stub Python của Command Line Tools (không có
# certifi/google-auth/...), không phải venv của dự án. Dùng path tuyệt đối
# tới venv cho MỌI lời gọi python3 trong file này.
PY="/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/.venv/bin/python3"

LOG_DIR="output/shorts"
mkdir -p "$LOG_DIR"
RUN_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# The two command substitutions below are deliberately run with errexit OFF
# (set +e ... set -e): under `set -e`, `VAR=$(failing_cmd)` aborts the script
# AT that assignment line, before EXIT_CODE=$? or the logging block ever run
# -- a real failure would then vanish silently instead of reaching
# daily_run_log.jsonl, which is exactly what the health-check depends on.

set +e
SSL_CERT_FILE="$("$PY" -c 'import certifi; print(certifi.where())')"
CERT_EXIT_CODE=$?
set -e
export SSL_CERT_FILE

if [ "$CERT_EXIT_CODE" -ne 0 ]; then
    OUTPUT="[daily_short_batch.sh] failed to resolve SSL_CERT_FILE via certifi (exit $CERT_EXIT_CODE); short_batch_runner.py was not invoked."
    EXIT_CODE="$CERT_EXIT_CODE"
else
    set +e
    OUTPUT="$("$PY" short_batch_runner.py --episodes 06 --count 5 --playlist "GIẢI MÃ KINH ĐỊA TẠNG" 2>&1)"
    EXIT_CODE=$?
    set -e
fi

N_DONE="$(echo "$OUTPUT" | grep -oE '[0-9]+ đoạn xong' | grep -oE '^[0-9]+' || echo 0)"
N_FAILED="$(echo "$OUTPUT" | grep -oE '[0-9]+ lỗi\.' | grep -oE '^[0-9]+' || echo 0)"

"$PY" -c "
import json
entry = {
    'run_at': '$RUN_TS', 'exit_code': $EXIT_CODE,
    'n_done': $N_DONE, 'n_failed': $N_FAILED,
}
with open('$LOG_DIR/daily_run_log.jsonl', 'a', encoding='utf-8') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
"

echo "$OUTPUT" >> "$LOG_DIR/daily_run_full_output.log"
echo "--- $RUN_TS (exit=$EXIT_CODE) ---" >> "$LOG_DIR/daily_run_full_output.log"

# Preserve the real outcome as this script's own exit code -- logging above
# always runs regardless of success/failure, but launchd/callers still need
# to see a non-zero exit to register the run as failed.
exit "$EXIT_CODE"
