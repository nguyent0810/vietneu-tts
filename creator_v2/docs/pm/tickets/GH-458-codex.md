# GH-458 — Khai containsSyntheticMedia khi video có ảnh AI phỏng tác

Bạn đang chạy TRONG worktree riêng `D:\Tools\Youtube Creator v2\wt-synth` (nhánh `lead/synthetic-media-flag`). Đường dẫn dưới đây tính từ `creator_v2/`. Không đụng checkout `vietneu-main`.

## Bối cảnh
storytelling-guide §15 (chủ kênh 17/11/2026): video có ảnh AI phỏng tác nhân vật rõ mặt phải bật khai báo nội dung chỉnh sửa/tổng hợp của YouTube (`status.containsSyntheticMedia`, trường của videos.insert/videos.update) và có dòng ghi chú trong mô tả.

## Việc
1. Tìm nơi dựng body `status` khi upload (Long: `motion/long/publish_long.py` → `factory/channel.py`; Short: luồng enqueue/publish dùng bundle `bundles/<CH>/<slug>.json`). Khi spec/bundle có `"ai_faces": true` thì body status có `"containsSyntheticMedia": true`. Không có khóa thì giữ nguyên hành vi cũ (không gửi trường).
2. Mô tả: Long (`motion/long/describe.py`) và Short (nơi dựng description của bundle) thêm một dòng `Một số hình là phỏng dựng bằng AI dựa trên tư liệu.` khi `ai_faces` true, đặt trước phần nguồn/ghi công; không trùng nếu đã có.
3. Long: `ai_faces` đọc từ `data/long/<topic>/spec.json`. Short: từ `data/stier/specs/<slug>.json`, chép sang bundle khi enqueue nếu luồng đó chép các khóa khác.

## Test
Thêm test dùng `factory/youtube_fake.py`: upload với `ai_faces` có `containsSyntheticMedia: true` trong status gửi đi; không có thì không có trường. Test mô tả có/không có dòng. Chạy test liên quan và `python -m pytest -q tests`; báo dòng cuối.

## File được ghi
Code + test trong worktree này; báo cáo `docs/pm/tickets/GH-458-codex.report.md` (UTF-8, ghi bằng Python). Không commit, không gọi mạng, không đọc thư mục credentials.
