# GH-527 — html chặn sớm chương thiếu nhạc + gom lỗi thời lượng cảnh (Codex)

Issue #527. Làm trong thư mục hiện tại. Không commit, không push, không render, không đăng. Ghi file bằng Python utf-8 (không PowerShell) để giữ tiếng Việt.

## Sửa (chỉ các file này)
- `motion/long/build_long.py`, `do_html`:
  1. Sau `variety.resolve_bgm(...)`: với mỗi chương mà `ch.get("bgm")` khác rỗng nhưng không đoạn nào có `file` (dùng `bgm_items` hoặc kiểm từng dict) → gom tên chương, rồi `raise SystemExit("nhạc nền: <ch..> không có bài cho mood ...; chọn tay output/long/<topic>/bgm_picks.json")`.
  2. Vòng lặp chương: lỗi `planned_check["errors"]` và `pano_bad` (~dòng 1218–1225) không raise ngay; gom vào danh sách, cuối `do_html` (trước khi in tổng kết) raise một lần `"tham số cảnh:\n  " + ...`. Các chương sau chương lỗi vẫn được kiểm (có thể bỏ qua phần ghi html/mix của chương lỗi).
  3. Cảnh `date`: nếu `groupAt` do spec ghi có ít mốc hơn số nhóm số trong `date` → thêm vào lỗi gom ở mục 2 (`chNN#i date: groupAt có X mốc, date có Y nhóm số`) thay vì để `sfx_long` IndexError.
- Test mới `tests/test_build_long_html_gather.py` (monkeypatch, không render, không ffmpeg nếu tránh được): (a) mood không có bài → SystemExit chứa "nhạc nền"; (b) hai chương cùng có cảnh quá ngắn → một SystemExit liệt kê cả hai.

## Kiểm
`python -m pytest -q tests/test_build_long_html_gather.py` và các test build_long hiện có (`python -m pytest -q tests -k build_long`) xanh.

## Báo cáo
`docs/pm/tickets/GH-527-codex-report.md`: diff tóm tắt, lệnh test + dòng kết quả cuối nguyên văn.