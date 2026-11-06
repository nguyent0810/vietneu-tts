# GH-132 — Báo cáo

## Đã thực hiện

- Chép mã và kiểm thử từ nhánh nghiên cứu, giữ hàm quyết định, SHA-256, lịch sử append-only và ý nghĩa verify.
- Thêm CLI init/render/decide/verify cho Long. Init tạo candidate theo tiêu đề, gắn thumbnail theo thứ tự (lặp lại nếu số ảnh ít hơn số tiêu đề), cùng claims và flags rỗng; từ chối ghi đè candidates đã tồn tại. Render tạo HTML và Markdown, hiển thị tiêu đề, giới hạn ký tự và cảnh báo, thumbnail và bản 168 px. Quyết định APPROVE in giá trị để Lead tự cập nhật spec; không sửa spec.
- Đọc giới hạn bằng channel_profile như long_gate, có cảnh báo và dự phòng 60 khi không đọc được. Trong worktree này không có library.tools.channel_profile, vì vậy thực tế đang dùng dự phòng 60; Lead cần kiểm tra lại với thư viện/hồ sơ kênh đầy đủ.
- Đã thêm kiểm thử init và cảnh báo tiêu đề; CLI gọi utf8_console.

## Kiểm tra

- `python -m pytest tests/test_review_card.py tests/test_console.py -q`: 4 passed, 16 errors do pytest không có quyền đọc thư mục tạm mặc định trên máy.
- Chạy lại qua pytest.main với thư mục tạm trong worktree và điều chỉnh mode tạo thư mục trong tiến trình thử nghiệm: 17 passed, 3 failed trước khi sửa kiểm thử init. Hai lỗi console còn lại do tiến trình qa_blank/FFmpeg không ghi được thư mục TemporaryDirectory của hệ thống (WinError 5); không sửa code dùng chung.
- Sau khi sửa kiểm thử init: chạy lại cùng thiết lập, loại hai trường hợp qa_blank bị chặn quyền: 18 passed, 2 deselected. Chưa có kết quả xanh cho toàn bộ lệnh bắt buộc.
- `python scripts/review_card.py --help`: thành công.
- Đã chạy đúng lệnh kiểm mất dấu trong brief: exit 0. Đồng thời kiểm trực tiếp hai file mới theo UTF-8, không còn ký tự dấu hỏi; kiểm file báo cáo sau khi ghi.
- Lint: ticket không chỉ định lệnh lint; chưa chạy lint.

## Giới hạn

Không có khẳng định nội dung video cần factcheck. Không có clip sheet hoặc thumbnail sản xuất: ticket chỉ yêu cầu code và test. HTML thumbnail dự phòng được nhúng qua iframe; Markdown phụ thuộc trình xem có hỗ trợ iframe. Chưa commit, upload hay thay đổi lịch.
