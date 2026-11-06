# GH-198 — báo cáo ingest-dir

- Đã sửa `library/tools/assets.py`: thêm `ingest-dir`, tái sử dụng `add_asset`, bỏ qua file trùng và ghi ID trùng, đọc prompt/tag theo nhóm, hỗ trợ dry-run và push các asset mới qua `push_assets`. Quét các file media trực tiếp trong thư mục theo thứ tự tên. Kết quả JSON gồm `added`, `near_duplicates`, `errors`, `pushed`; lỗi từng file không dừng lô.
- Đã sửa `tests/test_assets.py`: kiểm tra ảnh gần trùng trong lô và kho, prompt/tag, dry-run, push giả lập và xử lý lỗi.
- Cách dùng: `python library/tools/assets.py ingest-dir <thu-muc-trong-repo> --pham-vi chung --ai --tags a,b --tags-from-prompts <ai_prompts.md> --near-threshold 8 --dry-run`. Bỏ `--dry-run` để ghi manifest; thêm `--push` để đẩy asset mới. Có thể đặt `--root` và `--manifest` nếu cần.
- Kiểm thử: `python -m pytest tests/test_assets.py -q` chạy trực tiếp gặp `PermissionError` với thư mục tạm Windows của môi trường. Chạy cùng bộ test qua `pytest.main` với TEMP/TMP trong workspace và thay mode mkdir 0700 thành 0777 trong tiến trình kiểm thử, tắt cache: **28 passed in 1.25s**. Thay đổi mode này chỉ áp dụng trong tiến trình kiểm thử.
- Không gọi rclone thật, không upload, không đọc credentials, không commit hoặc push git. Các thư mục tạm do pytest tạo có thể còn lại trong workspace; một số bị môi trường từ chối quyền truy cập.
