# GH-516 — Công cụ ảnh AI và b-roll (Codex)

Issue #516 (`gh issue view 516 --repo nguyent0810/vietneu-tts`). Làm trong worktree hiện tại. Không commit, không push, không render, không đăng, không đọc credentials, không in biến môi trường hay URL/khoá webhook.

## 1. `scripts/ai_img_request.py --redo ai_01,ai_03`
- Đọc code hiện tại (biến `out`, `share_out`, hàm `missing`). Thêm cờ `--redo` (danh sách tên không đuôi hoặc có đuôi .png).
- Trước khi tính `missing`: với mỗi tên, nếu file có ở `out` hoặc `share_out` thì chuyển sang `<thư mục đó>/_old/<YYYYmmdd-HHMMSS>/` (không xoá). Sau đó luồng gửi/chờ/import chạy như cũ, nên chỉ các tên đó bị yêu cầu lại.
- `--redo` với `--no-send` thì báo lỗi rõ.

## 2. `scripts/fetch_broll.py <topic>`
- Bản nháp chạy được: `docs/pm/tickets/GH-516-fetch_broll_draft.py` (Lead viết). Đưa vào `scripts/fetch_broll.py`, làm gọn: argparse, ROOT tính từ file, chọn file ngang ≤ 1920, bỏ qua file đã có (> 10 KB), ghi `output/long/<topic>/broll/index.json`, in `clip N ok M thiếu [...]`, mã thoát 1 nếu thiếu.
- Docstring tiếng Việt ngắn như các script khác.

## 3. Test
`tests/test_ai_img_request_redo.py`, `tests/test_fetch_broll.py`: thư mục tạm, monkeypatch mạng (httpx/urllib) và webhook; kiểm chuyển file sang `_old`, chỉ tên redo bị gửi, chọn đúng file ngang ≤1920, index.json.

## Kiểm
`python -m pytest -q -p no:cacheprovider tests/test_ai_img_request_redo.py tests/test_fetch_broll.py` xanh. Ghi file bằng Python utf-8.

## Báo cáo
`docs/pm/tickets/GH-516-codex-report.md`: tóm tắt diff, lệnh test + dòng cuối nguyên văn.
