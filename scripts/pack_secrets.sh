#!/bin/bash
# Gói toàn bộ credential của dự án thành 1 file mã hoá để chuyển tay sang máy khác.
#
#   bash scripts/pack_secrets.sh [file_dich]
#
# Mặc định ghi ra ./secrets-full.tar.gz.age. Hỏi passphrase 2 lần (age + scrypt);
# passphrase KHÔNG nằm ở đâu trong repo, tự chuyển qua kênh riêng.
#
# Giải mã ở máy mới, chạy tại thư mục gốc repo:
#   age -d secrets-full.tar.gz.age | tar xzvf -
#
# Danh sách dưới đây khớp với FORBIDDEN_PATHS trong scripts/secret_scan.py —
# thêm credential mới thì nhớ cập nhật cả hai chỗ.

set -euo pipefail

cd "$(dirname "$0")/.."

OUT="${1:-secrets-full.tar.gz.age}"

PATHS=(
  .youtube_channels
  .tiktok_channels
  .youtube_oauth_clients.env
  .tiktok_oauth_clients.env
  .github_integration.env
  .vercel_token.env
  .youtube_hub.env
  apps/hub/.env.local
  video_tool_clone/.env
)

PRESENT=()
for p in "${PATHS[@]}"; do
  if [ -e "$p" ]; then
    PRESENT+=("$p")
    echo "  gói   $p"
  else
    echo "  bỏ    $p (không có trên máy này)"
  fi
done

if [ ${#PRESENT[@]} -eq 0 ]; then
  echo "Không tìm thấy credential nào để gói." >&2
  exit 1
fi

echo
echo "Nhập passphrase (gõ 2 lần, age không hiện ký tự nào khi gõ):"
tar czf - "${PRESENT[@]}" | age -p > "$OUT"

chmod 600 "$OUT"
echo
echo "Xong: $OUT ($(du -h "$OUT" | cut -f1)), ${#PRESENT[@]} mục."
echo "Kiểm tra lại bằng:  age -d $OUT | tar tzvf -"
