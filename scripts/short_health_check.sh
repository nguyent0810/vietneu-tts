#!/bin/bash
# launchd wrapper cho short_health_check.py -- cùng pattern với
# scripts/twice_weekly_batch.sh (xem ghi chú ở đó).
#
# BUG THẬT đã sửa (audit launchd 04/08, phát hiện qua Codex CLI adversarial
# review): plist trước đây gọi thẳng "python3 -c 'import certifi...'" và
# "python3 short_health_check.py" TRỰC TIẾP trong ProgramArguments, không
# qua wrapper -- launchd's PATH tối giản khiến "python3" resolve vào stub
# của Command Line Tools (thiếu certifi + mọi dependency dự án), job đã
# CRASH ÂM THẦM (không ai biết) từ 30/07 tới lúc audit này (xem
# output/shorts/health_check_stderr.log: "ModuleNotFoundError: No module
# named 'certifi'"). Đây chính là loại lỗi mà health-check job LẼ RA phải
# giám sát cho các job khác -- bản thân nó lại dính đúng lỗi đó.
set -euo pipefail
cd "/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS"

PY="/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/.venv/bin/python3"

exec "$PY" short_health_check.py "$@"
