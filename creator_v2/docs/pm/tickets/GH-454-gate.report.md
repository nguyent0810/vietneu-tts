# GH-454 — Báo cáo

## Thay đổi

- Mở rộng `short_retention` cho MIM/CK/CL: kiểm tra hook_kind, câu đầu tối đa 9 từ, câu hỏi trong 10 từ đầu, hình cảnh mở và tiêu đề tối đa 60 ký tự. Các luật mới là lỗi từ 01/12/2026, cảnh báo với ngày cũ hoặc thiếu ngày; giữ luật cũ.
- Dùng chung danh sách loại cảnh và trường hình với cổng build; chặn loại cảnh logo/kicker. Thêm ca đạt/hỏng và ca cảnh báo cho spec cũ.
- Kiểm tra các dòng có dấu hỏi trong phần sửa để phát hiện lỗi mã hóa; chữ tiếng Việt được ghi UTF-8.

## Kiểm thử

- `python -m pytest tests/test_script_lint_short.py tests/test_stier_hook_gate.py tests/test_stier_preflight_schema.py -q`: lần chạy nguyên lệnh gặp lỗi quyền thư mục tạm Windows; dòng cuối: `2 failed, 16 passed, 2 warnings, 7 errors in 2.21s`. Hai ca failed do chữ tiếng Việt bị hỏng khi truyền mã lần đầu, đã sửa và chạy lại.
- Chạy lại cùng ba tập test qua `pytest.main`, tắt cache, đặt basetemp riêng và thay mode mkdir 0700 bằng 0777 trong tiến trình pytest để tránh lỗi quyền Windows: `25 passed in 0.44s`.
- `python -m pytest -q -x tests`: dừng vì pytest không truy cập được thư mục tạm mặc định: `2 warnings, 1 error in 5.39s`.
- Chạy lại toàn bộ bằng cùng cách đổi mode mkdir trong tiến trình pytest: `1 failed, 362 passed, 1 skipped in 14.48s`. Test `test_qa_blank_cli_prints_vietnamese_on_cp1252_console[cp1252]` chạy Python con; tiến trình con tạo thư mục tạm mode 0700 và ffmpeg bị Permission denied. Chưa chứng minh được toàn bộ tests không đỏ thêm; cần Lead chạy lại trong môi trường có quyền thư mục tạm bình thường.

Không render, không gọi mạng, không đăng, không đổi lịch, không dùng git.
