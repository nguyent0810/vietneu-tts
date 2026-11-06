# GH-179 — báo cáo

- Đã thêm `chosen_title(spec)`: ưu tiên phần tử đầu `youtube.titles` khi không rỗng, còn lại dùng `spec.title`; cảnh báo khi phần tử đầu khác tiêu đề hồ sơ. Bundle và Upload dùng hàm này, `thumbnail_text` vẫn dùng `spec.title`.
- Đã thêm test lựa chọn, fallback và Bundle/thumbnail, không gọi API.
- Kiểm tra `motion/long/describe.py`: tạo mô tả và tiêu đề chương, không dùng tiêu đề hồ sơ để upload hoặc khớp tiêu đề kênh. `scripts/*long*` chỉ có `scripts/long_gate.py`: kiểm tra độ dài bằng phần tử đầu `youtube.titles` nếu danh sách có phần tử, nhưng nếu phần tử đầu là chuỗi rỗng thì không fallback sang `spec.title`; có thể bỏ sót lỗi độ dài. Không sửa file này.
- `python -m pytest tests -q -k "publish or title"`: 33 passed, 2 skipped, 919 deselected, 38 errors; các lỗi setup do PermissionError khi pytest truy cập thư mục tạm mặc định. Thử đặt TEMP/TMP trong workspace và tắt cache vẫn gặp 38 lỗi tương tự. Chưa thể xác nhận bộ kiểm thử đầy đủ xanh; Lead cần chạy lại trong môi trường có thư mục tạm truy cập được.
- `python -m pytest tests/test_publish_long_title.py -q -k "not bundle" -p no:cacheprovider`: 5 passed, 1 deselected. Test Bundle cần tmp_path nên chưa chạy được.
- Không chạy lint riêng; ticket không yêu cầu lint. Không có khẳng định nội dung cần factcheck, clip sheet hoặc thumbnail thuộc ticket code này.
- Không upload, không gọi API thật, không commit. Thư mục làm việc được cung cấp không có mục `.git`, nên không thể độc lập xác minh metadata worktree; thực hiện theo chỉ dẫn người giao rằng đây là worktree riêng.
