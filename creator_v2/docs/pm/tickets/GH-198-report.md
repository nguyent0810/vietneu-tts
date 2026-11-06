# GH-198 — báo cáo

## Thay đổi

- `library/tools/assets.py`: pHash ảnh và năm khung video, phát hiện gần trùng, `near-dups`, push/pull/prune qua subprocess rclone, giới hạn sử dụng theo kênh, luật tag ảnh AI. Đường dẫn manifest xuất theo dấu `/` trên Windows.
- `tests/test_assets.py`: test ảnh Pillow, rclone giả lập, kiểm tra SHA, prune, giới hạn sử dụng và luật CL.
- `library/channels/cl.yaml`: đổi riêng `kho_loc` thành yêu cầu tag `minh_hoa_chung` cho ảnh AI.
- `creator_v2/docs/pm/tickets/GH-198-report.md`: báo cáo này.

## Lệnh và kiểm tra

- Lệnh mới: `near-dups [--near-threshold N]`, `push (--id ID | --all-local)`, `pull (--ids ID... | --plan PATH)`, `prune [--dry-run | --yes]`. Các lệnh hỗ trợ `--manifest`, `--root`; `scan`/`add` có `--near-threshold`, `--allow-near`; `find` có `--max-uses`, `--min-gap-days`.
- `python -m pytest tests/test_assets.py -q`: **2 passed, 20 errors**, do Windows từ chối truy cập thư mục tạm mặc định của pytest, trước khi chạy phần lớn test.
- Chạy lại cùng bộ test với wrapper sửa quyền tạo thư mục tạm và tắt pytest cache: **25 passed in 1.25s**. Wrapper gọi `pytest.main(['tests/test_assets.py', '-q', '--basetemp=./gh198_test6', '-p', 'no:cacheprovider', '--tb=short'])` sau khi buộc `os.mkdir` dùng mode `0o777`.
- `git diff --check`: không có lỗi khoảng trắng.
- `gh issue view 198 --repo nguyent0810/vietneu-tts`: thất bại do proxy không kết nối; chỉ đối chiếu được brief local.
- Không chạy rclone thật, không commit, không đăng.

## Giả định và giới hạn

- So sánh video dùng khoảng cách nhỏ nhất giữa các cặp khung; ngưỡng mặc định 8 bit. `scan` báo lỗi băm trong `hash_errors` và vẫn giữ record để tương thích dữ liệu cũ; các record này chưa được kiểm tra gần trùng. `add` yêu cầu băm thành công.
- `pull --plan` nhận đường dẫn JSON; đối chiếu các giá trị chuỗi với ID hoặc đường dẫn manifest. `prune` coi mọi file `*plan*.json` dưới `output` là plan còn hoạt động, ưu tiên giữ file khi không chắc chắn.
- `prune` yêu cầu mỗi mục lịch sử có `ngay_public` hợp lệ và đã qua hơn 7 ngày. `mark-used` hiện chỉ ghi ngày dùng, không tự chứng minh đã public; do đó các record thông thường sẽ được giữ lại cho tới khi có bằng chứng public. SHA từ remote phải được rclone cung cấp dưới dạng SHA-256; nếu remote không hỗ trợ, push/prune dừng an toàn. Chưa xác minh khả năng SHA-256 của Drive thật.
- Lệnh dọn các thư mục tạm do test tạo bị chính sách tự động từ chối; các thư mục `gh198_*`, `.tmp_gh198` và `pytest-cache-files-*` có thể còn trong workspace.
