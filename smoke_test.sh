#!/usr/bin/env bash
# Kiểm tra nhanh toàn bộ pipeline còn hoạt động đúng sau khi sửa code:
# tạo 1 chủ đề tạm + 1 file Long + 1 file Short, chạy process_topics.py,
# xác nhận output (wav+srt+json) sinh đúng và pass QA, dọn dẹp sạch sau đó.
#
# Usage: ./smoke_test.sh
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    echo "Usage: ./smoke_test.sh"
    echo "Tạo 1 chủ đề tạm, render Long+Short, verify output, dọn dẹp. Không nhận tham số."
    exit 0
fi

TOPIC="_SmokeTest"
FAIL=0

pass() { echo "  ✓ $1"; }
failmsg() { echo "  ✗ $1"; FAIL=1; }

cleanup() {
    echo "--- Dọn dẹp ---"
    rclone purge "gdrive:TTS-Input/${TOPIC}/" >/dev/null 2>&1
    rclone purge "gdrive:TTS-Output/${TOPIC}/" >/dev/null 2>&1
    rm -rf "drive_input/topics/${TOPIC}" "output/topics/${TOPIC}" "chunks_cache/Binh/${TOPIC}"* 2>/dev/null
    rm -f /tmp/smoke_long.txt /tmp/smoke_short.txt
}
trap cleanup EXIT

echo "=== Smoke test: dựng dữ liệu tạm ==="
printf "Đây là câu kiểm tra nhanh cho smoke test, xác nhận pipeline vẫn hoạt động đúng sau khi sửa code.\n" > /tmp/smoke_long.txt
printf "*** 1\nĐoạn kiểm tra thứ nhất.\n\n*** 2\nĐoạn kiểm tra thứ hai, ngắn gọn để test nhanh.\n" > /tmp/smoke_short.txt

rclone copyto /tmp/smoke_long.txt "gdrive:TTS-Input/${TOPIC}/Long/smoke.txt" 2>&1 | grep -v NOTICE
rclone copyto /tmp/smoke_short.txt "gdrive:TTS-Input/${TOPIC}/Short/smoke_short.txt" 2>&1 | grep -v NOTICE

echo ""
echo "=== Smoke test: chạy pipeline (chủ đề: $TOPIC) ==="
uv run python process_topics.py --topic "$TOPIC" 2>&1 | grep -v "ggml_metal_init\|skipping kernel\|UserWarning\|warnings.warn\|llama_context\|ONNX decoder"
pipeline_status=$?

echo ""
echo "=== Smoke test: kiểm tra kết quả ==="

[ "$pipeline_status" -eq 0 ] && pass "pipeline exit code 0" || failmsg "pipeline exit code $pipeline_status"

long_files=$(rclone lsf "gdrive:TTS-Output/${TOPIC}/Long/" --files-only 2>/dev/null)
echo "$long_files" | grep -q "smoke.wav" && pass "Long: smoke.wav tồn tại" || failmsg "Long: thiếu smoke.wav"
echo "$long_files" | grep -q "smoke.srt" && pass "Long: smoke.srt tồn tại" || failmsg "Long: thiếu smoke.srt"
echo "$long_files" | grep -q "smoke.json" && pass "Long: smoke.json tồn tại" || failmsg "Long: thiếu smoke.json"

short_files=$(rclone lsf "gdrive:TTS-Output/${TOPIC}/Short/processed/smoke_short/" --files-only 2>/dev/null)
echo "$short_files" | grep -q "1_smoke_short.wav" && pass "Short: đoạn 1 tồn tại" || failmsg "Short: thiếu đoạn 1"
echo "$short_files" | grep -q "2_smoke_short.wav" && pass "Short: đoạn 2 tồn tại" || failmsg "Short: thiếu đoạn 2"

input_remaining=$(rclone lsf "gdrive:TTS-Input/${TOPIC}/" -R --files-only 2>/dev/null | grep -v "processed/")
[ -z "$input_remaining" ] && pass "Input đã được chuyển vào processed/ hết" || failmsg "Input còn sót: $input_remaining"

echo ""
if [ "$FAIL" -eq 0 ]; then
    echo "=== SMOKE TEST PASS ==="
else
    echo "=== SMOKE TEST FAIL — xem chi tiết ở trên ==="
fi
exit "$FAIL"
