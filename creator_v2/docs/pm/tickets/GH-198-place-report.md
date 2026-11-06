# GH-198: place và tự ghi lần dùng (báo cáo)

Codex làm, Lead viết lại báo cáo (bản gốc và hai chuỗi in trong `publish_long.py` bị mất dấu vì Codex ghi file qua PowerShell; Lead đã sửa).

- `assets.py place <topic> <key> <asset_id> [--creator-root] [--force]`:
  - tìm ảnh khớp SHA trên máy hoặc trong cache, thiếu thì `pull`;
  - cắt cover thành JPEG RGB 1920×1080 tại `output/long/<topic>/img/<key>.jpg`;
  - ghi sidecar `.json` có `asset_id`, `ai_generated`;
  - không ghi đè nếu thiếu `--force`.
- `publish_long.py`: sau khi có `video_id`, gọi `mark_library_used` duyệt sidecar trong `img/` và gọi `mark_used(..., ngay_public=publish_at[:10])`. Lỗi chỉ in cảnh báo, không chặn lần đăng.
- `mark_used`: cùng video và kênh thì không ghi trùng khi chạy lại vào ngày khác; vẫn cập nhật ngày public.
- Test: `tests/test_assets.py` và test mark-used đều đạt.
