# GH-176 (Codex): integrity INT_REPEATED_SENTENCE chặn nhầm câu lặp có chủ đích

Làm trong `creator_v2/`. Đọc `CLAUDE.md`, `AGENTS.md` và issue #176 trước.

## Phạm vi
- Được ghi: `factory/integrity.py`, `tests/test_integrity*.py` hoặc `tests/test_lines.py` (thêm ca), và file báo cáo.
- Không được: sửa kịch bản hay bundle của video đã đăng, upload, commit, đọc thư mục credentials.

## Việc
- Chọn hướng (a) trong issue: cho phép lặp có chủ đích khi câu ngắn (≤ 8 từ), hoặc khi hai lần xuất hiện cách nhau ≥ N câu (đề xuất N và đo), hoặc khi spec đánh dấu `refrain`.
- Câu dài bị ghép lặp liền nhau, tức lỗi thật, vẫn phải bị chặn.
- Ba ví dụ trong issue (`long-ck-c6-gia-tran-san-t2`, `long-mim-ai-voice`) phải qua.
- Đo trước và sau trên toàn bộ `bundles/`, nếu có local, và `data/long/*/script.md`: liệt kê mọi chỗ đổi kết quả, từ chặn thành qua và ngược lại.

## Tiêu chí đạt
- Test cho ca lặp có chủ đích (qua) và ca ghép lặp thật (chặn).
- `python -m pytest -q tests` của creator_v2 không thêm lỗi mới. Ghi số trước và sau.

## Báo cáo
Ghi `docs/pm/tickets/GH-176-report.md`: luật mới, bảng đo trước và sau, file đã đổi.

## Quyền cho ticket code (Lead cấp, 06/11)
Đây là ticket **code**, không phải ticket sản xuất video. Theo `CLAUDE.md` mục "Chọn agent" (code, spec và test giao Codex), Lead cho phép **riêng ticket này** ghi đúng các file nêu trong "Phạm vi", kể cả `factory/*`, `tests/*` và `motion/long/build_long.py`. Mọi điều cấm khác của `AGENTS.md` vẫn giữ: không upload, không commit hay đụng git, không ghi `state.sqlite`, không đọc credentials, không render.
Được chạy `python -m pytest -q tests`: các test liên quan đăng bài đều dùng mock, không gọi YouTube.
