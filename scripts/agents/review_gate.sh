#!/bin/zsh
# Cổng review CHỈ ĐỌC cho ticket/PR của thợ. Gom ticket + diff + file đính kèm thành MỘT prompt bằng shell
# (Lead không đọc nội dung vào ngữ cảnh của mình), gửi agy máy C trước; máy C hỏng thì agy Mac;
# cả hai hỏng thì exit 5 (Lead quyết: Codex / sub-agent). Không đổi index của worktree.
# Dùng: review_gate.sh <ticket.md> <worktree> <report_out.md> [file đính kèm thêm...]
# Prompt giữ lại ở <report_out>.prompt.txt để tra lại. Xem docs/agents/agy-machine-c.md.
set -u
[ $# -ge 3 ] || { echo "Dùng: review_gate.sh <ticket.md> <worktree> <report_out.md> [file thêm...]" >&2; exit 2; }
ticket="$1"; wt="$2"; out="$3"; shift 3
[ -f "$ticket" ] || { echo "review_gate: không thấy ticket $ticket" >&2; exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"; root="$(cd "$here/../.." && pwd)"
py="$root/.venv/bin/python"; [ -x "$py" ] || py="$(command -v python3)"
model="${REVIEW_MODEL:-gemini-3.8-flash-high}"
name="$(basename "$ticket" .md)"
mkdir -p "$(dirname "$out")"
prompt="$out.prompt.txt"
{
  echo "KHÔNG gọi bất kỳ công cụ/lệnh/đọc file nào. Chỉ đọc nội dung dán dưới đây và trả lời bằng văn bản."
  echo "Bạn là reviewer. Review thay đổi cho ticket dưới đây. Tìm lỗi THẬT (sai yêu cầu ticket, hồi quy, tất định,"
  echo "off-by-one, test thiếu). Mỗi lỗi ghi file:dòng + cách sửa. Kết luận một dòng: APPROVE hoặc REQUEST_CHANGES."
  echo; echo "## TICKET"; cat "$ticket"
  echo; echo "## DIFF (đã theo dõi, so với HEAD)"; echo '```diff'; git -C "$wt" diff HEAD; echo '```'
  git -C "$wt" ls-files --others --exclude-standard | while IFS= read -r f; do
    echo; echo "## FILE MỚI $f"; echo '```'; cat "$wt/$f"; echo '```'
  done
  for f in "$@"; do echo; echo "## FILE $f"; echo '```'; cat "$f"; echo '```'; done
} > "$prompt"

ledger() { "$py" "$here/agent_ledger.py" "$@" >/dev/null 2>&1 || true; }
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

host=c; started="$(now)"; ledger start "$name" agy_c --role reviewer
"$here/agy_c.sh" "$prompt" "$model" > "$out" 2> "$out.err"; rc=$?
ledger end "$name" agy_c --role reviewer --started-at "$started" --report "$out" --exit-code $rc
if [ $rc -ne 0 ]; then
  echo "review_gate: máy C hỏng ($(tail -1 "$out.err")) -> agy Mac" >&2
  host=local; started="$(now)"; ledger start "$name" agy_local --role reviewer
  agy -p "$(cat "$prompt")" --model "$model" > "$out" 2>> "$out.err" < /dev/null; rc=$?
  ledger end "$name" agy_local --role reviewer --started-at "$started" --report "$out" --exit-code $rc
  [ $rc -eq 0 ] || { echo "review_gate: agy Mac cũng hỏng (exit $rc) -> Lead quyết (Codex / sub-agent)" >&2; exit 5; }
fi
echo "review_gate: xong trên máy $host -> $out"
grep -oE "APPROVE|REQUEST_CHANGES" "$out" | tail -1
