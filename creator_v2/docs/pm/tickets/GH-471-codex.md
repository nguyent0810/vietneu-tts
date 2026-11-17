# GH-471 — creator_v2: cau_tron + markup_leak theo chuẩn 075b

Bạn đang chạy TRONG worktree riêng `D:\Tools\Youtube Creator v2\wt-471` (nhánh `lead/471-v2-script-gates`). Đường dẫn tính từ `creator_v2/`. Không đụng checkout `vietneu-main`.

Đọc trước: `../docs/script/audio-script.md` §9 và `../docs/script/lint-matrix.md` (chuẩn chung 075b), `../audio_script_rules.py` (bản gốc của hai luật cho đường HBR — dùng lại logic nếu import được sạch, không thì viết tương đương).

## Việc
1. **Long V2** — `motion/long/script_lines.py` (nơi tách lời Long; xem hàm kiểm integrity hiện có):
   - `cau_tron`: dòng lời (sau khi gỡ nhãn `{pd}`, `{beat:…}`, `[TRÍCH DỊCH]`…) kết bằng dấu phẩy → LỖI nếu spec Long có `youtube.publish_at` ≥ `2026-11-18`; Long cũ hơn/không có ngày → CẢNH BÁO (không làm hỏng Long đã dựng khi chạy lại).
   - `markup_leak`: URL, khoá JSON kiểu `"key":`, `{pd}`/`{beat…}` còn sót, `[PAUSE]`, ký hiệu markdown trong LỜI ĐỌC cuối (chuỗi đưa vào TTS) → LỖI (mọi Long; nếu Long cũ đang có thì báo trong báo cáo, không sửa dữ liệu).
   - Nối vào chỗ build_long đang gọi kiểm lời (bước `takes`/`tts`/`html` — ghi rõ trong báo cáo).
2. **Short V2** — `motion/stier/build.py` (ear check/preflight hiện có, xem `tests/test_stier_ear.py`): nếu chưa có, dòng `lines[i]` kết bằng dấu phẩy → LỖI khi `publish_at` ≥ `2026-11-29`, cũ hơn → cảnh báo.

## Test
Test mới cho từng luật (đạt / hỏng / Long cũ chỉ cảnh báo). `python -m pytest -q tests` báo dòng cuối. Chạy thử `python -c` gọi kiểm trên `data/long/cl-sarin-tokyo-1995` và `data/long/cl-dich-nhan-kiet` (Long cũ: chỉ cảnh báo) và ghi số cảnh báo vào báo cáo.

## File được ghi
`motion/long/script_lines.py`, `motion/long/build_long.py` (chỉ chỗ nối), `motion/stier/build.py` (chỉ chỗ ear check), test mới trong `tests/`, báo cáo `docs/pm/tickets/GH-471-codex.report.md` (UTF-8, ghi bằng Python — KHÔNG ghi tiếng Việt qua PowerShell). Không commit, không render, không TTS.
