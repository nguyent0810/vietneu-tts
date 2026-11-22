# GH-516 — Báo cáo

- `scripts/ai_img_request.py`: thêm `--redo`, kiểm tra tên ảnh và không cho dùng cùng `--no-send`; chuyển bản cũ ở cả hai nơi vào `_old` trước khi tính ảnh thiếu. Tránh ghi đè bản lưu nếu chạy cùng giây.
- `scripts/fetch_broll.py`: lấy danh mục theo bản nháp, chọn clip ngang rộng tối đa 1920, bỏ tải lại file trên 10 KiB, ghi index và báo thiếu/mã thoát 1.
- Hai file test dùng thư mục riêng trong workspace và giả lập webhook, HTTP; kiểm tra lưu bản cũ, yêu cầu lại, từ chối `--no-send`, chọn clip, file đã có và index.

Lần chạy đầu bị `PermissionError` tại thư mục tạm mặc định của pytest trên Windows; các test sau đó dùng thư mục riêng trong workspace. Các thư mục kiểm thử `gh516-test-*`, `gh516-pytest-work` và `gh516-*` được giữ lại theo luật không xóa ngoài topic.

Lệnh kiểm:

```text
python -m pytest -q -p no:cacheprovider tests/test_ai_img_request_redo.py tests/test_fetch_broll.py
3 passed in 0.34s
```

Không chạy lint riêng (brief không yêu cầu). Không có khẳng định nội dung cần fact-check, clip sheet hay thumbnail trong ticket công cụ này.
