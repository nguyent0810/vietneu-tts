# GH-190 — báo cáo Codex

**Trạng thái: chưa hoàn tất.** Ticket yêu cầu sửa `motion/long/build_long.py` và thêm `tests/test_long_tools_190.py`, nhưng AGENTS.md do chủ phiên cung cấp cấm tuyệt đối sửa `motion/long/build_long.py` và `tests/*`. Vì vậy chưa triển khai kiểm ảnh thiếu ở bước html và chưa tạo bộ test yêu cầu; cần Lead xử lý xung đột phạm vi. Không chạy html của Bao Thanh Thiên, render, đăng, commit hoặc đổi lịch.

## Đã làm

- `motion/long/scene_params.py`: A7 giữ tối thiểu 2,5 giây, tối đa 25 giây riêng cho `endcard`, các loại khác giữ tối đa 9 giây.
- `motion/long/stt_takes.py`: bỏ đường dẫn venv cố định; dùng CUDA/float16 khi CTranslate2 nhận diện CUDA, CPU/int8 khi không có GPU hoặc truy vấn CUDA gặp RuntimeError. Giữ logic ghi `transcripts.json` cũ. Chưa chạy nhận dạng thực tế, chưa kiểm tra khả năng nạp CUDA/cuDNN khi GPU có nhưng thư viện runtime thiếu.
- `motion/long/lint_html.py`: khi các font đã biết cần cho kiểm tra nhưng thiếu, trả một thông báo hướng dẫn thay vì traceback hoặc bỏ qua kiểm tra kinetic. Không thêm script tải font. Khi thiếu font của thẻ, lint trả lỗi thiếu font và vẫn kiểm các cảnh map, song chưa đo được các thẻ cho đến khi cài font.

## Kiểm tra

- Fixture nội tuyến không ghi vào `tests/*`: A7 qua 6 ca (endcard 20, 25, 25,1 và 2 giây; photo 20 và 9 giây); chọn STT qua 3 ca giả lập CUDA, CPU và lỗi driver; font qua các ca thiếu font, cảnh không dùng font và kinetic chỉ có serif. Các ca này không thay thế bộ test tự động trong ticket; chưa kiểm tra đầu ra transcript thực tế và chưa có fixture kiểm ảnh html.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests` được bắt đầu trước khi sửa nhưng tiếp tục chạy trong lúc sửa: **557 passed, 29 skipped, 345 errors**. Do chạy chồng lúc sửa, đây không phải baseline trước sửa đáng tin cậy.
- Sau sửa, `python -m pytest -q -p no:cacheprovider --tb=no tests` với `PYTHONDONTWRITEBYTECODE=1`: **1 failed, 556 passed, 29 skipped, 345 errors**. Test thất bại `tests/test_scene_params.py::test_duration_bounds_and_image_usage_are_blocking_without_exceptions` vẫn đòi chặn endcard 9,1 giây, trái yêu cầu mới; không sửa test vì bị cấm. Một lỗi thiết lập được kiểm riêng là `PermissionError [WinError 5]` khi pytest đọc thư mục tạm `pytest-of-Tung-QA`; chưa xác minh từng lỗi còn lại. Không thể kết luận không có lỗi mới so với baseline sạch.
- Lint: chưa chạy lint tổng thể riêng; kiểm tra font qua fixture như trên. Không có clip sheet hoặc thumbnail vì ticket không cho render.

## Còn cần Lead xử lý

1. Cho phép người có thẩm quyền sửa `build_long.py` để chặn các tham chiếu `img`, `bg`, `a.img`, `b.img`, `pins[].img` không có trong `spec.imgs`, kèm chương, cảnh và khóa ảnh.
2. Cập nhật test cũ cho hợp đồng A7 mới, thêm các test của GH-190 và chạy lại toàn bộ pytest trong môi trường có thư mục tạm truy cập được; lấy baseline sạch nếu cần so sánh.
3. Kiểm thử STT thực tế trên CPU và CUDA, định dạng transcript, và xác nhận font tải đúng tên và có thể đọc. Không có khẳng định nội dung video nào cần fact-check trong ticket công cụ này.
