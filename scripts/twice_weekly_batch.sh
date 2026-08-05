#!/bin/bash
# launchd wrapper cho twice_weekly_batch.py -- chạy Thứ 3 + Thứ 6, 8h30
# sáng giờ local. Wrapper CHỈ lo path/env, toàn bộ logic thật nằm trong
# twice_weekly_batch.py (dễ test hơn bash thuần, và tránh lặp lại bug
# PATH/python3 đã gặp ở daily_short_batch.sh).
set -euo pipefail
cd "/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS"

# launchd chạy PATH tối giản (/usr/bin:/bin:/usr/sbin:/sbin) -- "python3"
# trần resolve nhầm sang stub Python của Command Line Tools (thiếu mọi
# dependency thật), không phải venv dự án. Dùng path tuyệt đối.
PY="/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/.venv/bin/python3"

exec "$PY" twice_weekly_batch.py "$@"
