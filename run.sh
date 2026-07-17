#!/usr/bin/env bash
# Chạy pipeline TTS tự động: quét mọi thư mục CHỦ ĐỀ trong gdrive:TTS-Input/
# (mỗi chủ đề có Long/ và Short/), tự chọn giọng theo chủ đề (xem TOPIC_VOICES
# trong process_topics.py), render (cắt tự nhiên + QA + retry), upload lên
# TTS-Output/{Chủ đề}/..., đánh dấu input đã xử lý.
#
# Usage:
#   ./run.sh                          # mọi chủ đề, cả Long + Short, giọng tự chọn
#   ./run.sh --long                   # chỉ Long/ (mọi chủ đề)
#   ./run.sh --short                  # chỉ Short/ (mọi chủ đề)
#   ./run.sh --topic "Phật giáo"      # chỉ 1 chủ đề
#   ./run.sh --voice Tuyen            # ép 1 giọng cho MỌI chủ đề (bỏ qua auto-chọn)
#   ./run.sh --long --topic "Phong Thủy" --voice Sơn   # kết hợp
set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

PY_ARGS=()

while [ $# -gt 0 ]; do
    case "$1" in
        --long)  PY_ARGS+=(--long) ;;
        --short) PY_ARGS+=(--short) ;;
        --topic) PY_ARGS+=(--topic "${2:-}"); shift ;;
        --voice) PY_ARGS+=(--voice "${2:-}"); shift ;;
        -h|--help)
            echo "Usage: ./run.sh [--long | --short] [--topic TEN_CHU_DE] [--voice TEN_GIONG]"
            exit 0
            ;;
        *)
            echo "Tham số không nhận diện: $1 (dùng --help để xem cách dùng)" >&2
            exit 1
            ;;
    esac
    shift
done

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/run_$(date +%Y%m%d_%H%M%S).log"

echo "=== VieNeu-TTS auto pipeline (theo chủ đề) ==="
echo "Log: $LOG_FILE"
echo ""

fail() {
    echo "LỖI: $1" | tee -a "$LOG_FILE"
    exit 1
}

command -v rclone >/dev/null 2>&1 || fail "rclone chưa được cài (brew install rclone)."
command -v uv     >/dev/null 2>&1 || fail "uv chưa được cài."
rclone listremotes 2>/dev/null | grep -q '^gdrive:$' \
    || fail "Remote 'gdrive' chưa được cấu hình (chạy: rclone config)."

# Nạp .env nếu có (vd HF_TOKEN=...) — không bắt buộc, chỉ để tiện set 1 lần.
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

if [ -z "${HF_TOKEN:-}" ]; then
    echo "CẢNH BÁO: chưa set HF_TOKEN — request tới Hugging Face Hub sẽ ở chế độ ẩn danh," \
         "dễ dính rate limit khi chạy nhiều/tần suất cao. Tạo token tại https://huggingface.co/settings/tokens" \
         "rồi thêm vào file .env: HF_TOKEN=hf_xxx (hoặc export HF_TOKEN=hf_xxx trước khi chạy)." | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
fi

echo "Kiểm tra điều kiện: OK" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

uv run python process_topics.py ${PY_ARGS[@]+"${PY_ARGS[@]}"} 2>&1 | tee -a "$LOG_FILE"
status="${PIPESTATUS[0]}"

echo "" | tee -a "$LOG_FILE"
if [ "$status" -eq 0 ]; then
    echo "=== XONG — không có lỗi ===" | tee -a "$LOG_FILE"
else
    echo "=== XONG — CÓ FILE LỖI, xem log: $LOG_FILE ===" | tee -a "$LOG_FILE"
fi
exit "$status"
