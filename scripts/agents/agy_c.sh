#!/bin/zsh
# Gọi agy trên máy C (may-c, Tailscale, user "du bi") cho việc CHỈ ĐỌC: review gate, viết lời.
# Dùng: agy_c.sh <prompt.txt> [model] > ketqua.md   (exit 0 = SUCCESS)
# Prompt đi qua stdin dạng stream-json (tránh giới hạn ~32k ký tự dòng lệnh Windows).
# Máy C là hạ tầng test của QA: không mở port, không render, không đụng D:\qa-*.
set -u
[ $# -ge 1 ] || { echo "Dùng: agy_c.sh <prompt.txt> [model]" >&2; exit 2; }
p="$1"; model="${2:-gemini-3.8-flash-high}"
[ -f "$p" ] || { echo "thiếu file prompt: $p" >&2; exit 2; }
out=$(python3 -c '
import json,sys
print(json.dumps({"event":"user","message":{"role":"user","content":open(sys.argv[1],encoding="utf-8").read()}},ensure_ascii=False))' "$p" \
 | ssh -o BatchMode=yes -o ConnectTimeout=15 C-ts "agy --model $model --input-format stream-json --output-format stream-json --print-timeout 1800s \"-p=\"" 2>&1)
res=$(print -r -- "$out" | grep '"event":"result"' | tail -1)
[ -n "$res" ] || { echo "AGY_C_ERROR: không có kết quả (máy C tắt / mất Tailscale / chưa đăng nhập?)" >&2; print -r -- "$out" | tail -5 >&2; exit 3; }
print -r -- "$res" | python3 -c '
import json,sys
r=json.loads(sys.stdin.read())["result"]
if r.get("status")!="SUCCESS":
    sys.stderr.write("AGY_C_ERROR: %s\n" % r.get("error")); sys.exit(4)
sys.stdout.write(r.get("response",""))'
