# GH-507 — Báo cáo

## Thay đổi
- `motion/long/build_long.py`: sau khi tạo HTML, in từng cảnh báo factcheck; chặn render và final trước khi lấy khóa nếu có lỗi, trừ khi dùng `--draft` hoặc `--allow-factcheck`. Chuyển các cờ từ nhánh CLI final vào `do_final`; thông báo chặn liệt kê lỗi và hướng dẫn bổ sung nguồn.
- `tests/test_build_long_factcheck_gate.py`: kiểm tra chặn render/final, hai cờ bỏ qua, và mock các bước render.

## Kiểm tra
- `python -m pytest -q tests/test_build_long_factcheck_gate.py tests/test_factcheck_lint.py tests/test_factcheck_lint_label.py`
  - Lần đầu: `1 failed, 15 passed, 2 warnings in 6.10s`. Lỗi do chuỗi tiếng Việt trong test bị biến thành dấu hỏi khi truyền qua PowerShell; đã sửa chuỗi test và thông báo, ghi UTF-8 bằng Python.
  - Lần cuối, dòng cuối nguyên văn: `16 passed, 1 warning in 1.04s`
  - Cảnh báo còn lại: pytest không tạo được đường dẫn cache do Windows từ chối quyền; không ảnh hưởng bài test.
- `python -c "import sys; sys.path[:0]=['motion/long','motion','.']; import factcheck_lint; print(factcheck_lint.lint('cl-vidocq-javert'))"`
  - Dòng cuối nguyên văn: `[]`

Không render video, không đăng, không commit và không đổi lịch.
