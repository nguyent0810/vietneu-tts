#!/usr/bin/env bash
# Dọn dẹp local artifact tích luỹ theo thời gian (chunks_cache/, drive_input/)
# -- 2 thư mục này thuần staging/cache, sinh lại được, xoá định kỳ không mất
# dữ liệu thật.
#
# CỐ Ý KHÔNG đụng tới output/ ở đây nữa (đã sửa sau khi phát hiện thật: quét
# tuổi mù quáng trên output/ từng có nguy cơ xoá EP005/EP007 -- 2 tập Long đã
# render xong nhưng CHƯA TỪNG upload YouTube, hoá ra "output/ chỉ là
# staging" là giả định sai vì upload có thể lỗi/bị bỏ dở mà không ai biết).
# output/ giờ được dọn qua cơ chế RIÊNG, gắn với xác nhận upload thành công
# thật (xem long_batch_runner.py process_one_episode() + finalize_episode.py
# cleanup_generation_cache()) -- KHÔNG dựa vào tuổi file.
#
# Usage:
#   ./cleanup_local.sh              # xoá file cũ hơn 14 ngày
#   ./cleanup_local.sh --days 7     # tuỳ chỉnh số ngày
#   ./cleanup_local.sh --dry-run    # chỉ liệt kê, không xoá
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

DAYS=14
DRY_RUN=0

while [ $# -gt 0 ]; do
    case "$1" in
        --days) DAYS="${2:-14}"; shift ;;
        --dry-run) DRY_RUN=1 ;;
        -h|--help)
            echo "Usage: ./cleanup_local.sh [--days N] [--dry-run]"
            exit 0
            ;;
        *)
            echo "Tham số không nhận diện: $1" >&2
            exit 1
            ;;
    esac
    shift
done

TARGETS=("chunks_cache" "drive_input")

echo "=== Dọn local artifact cũ hơn $DAYS ngày ==="
[ "$DRY_RUN" -eq 1 ] && echo "(dry-run — chỉ liệt kê, không xoá thật)"
echo ""

total=0
for dir in "${TARGETS[@]}"; do
    [ -d "$dir" ] || continue
    count=$(find "$dir" -type f -mtime "+${DAYS}" 2>/dev/null | wc -l | tr -d ' ')
    total=$((total + count))
    echo "$dir/: $count file cũ hơn $DAYS ngày"
    if [ "$DRY_RUN" -eq 1 ]; then
        find "$dir" -type f -mtime "+${DAYS}" 2>/dev/null | head -10 | sed 's/^/    /'
        [ "$count" -gt 10 ] && echo "    ... và $((count - 10)) file khác"
    else
        find "$dir" -type f -mtime "+${DAYS}" -delete 2>/dev/null
        # dọn thư mục rỗng còn sót lại sau khi xoá file
        find "$dir" -type d -empty -delete 2>/dev/null
    fi
done

echo ""
if [ "$DRY_RUN" -eq 1 ]; then
    echo "Tổng cộng $total file sẽ bị xoá nếu chạy không có --dry-run."
else
    echo "Đã xoá $total file."
fi
