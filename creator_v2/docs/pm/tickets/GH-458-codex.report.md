# GH-458 — Báo cáo

**Trạng thái: chưa hoàn tất.** Phần Short và kiểm thử upload giả lập chưa được xác minh.

## Đã làm

- `factory/channel.py`: thêm cờ `Upload.ai_faces`, chỉ gửi `status.containsSyntheticMedia: true` khi cờ bật; mặc định không gửi trường.
- `motion/long/publish_long.py`: đọc `ai_faces` từ spec Long để truyền vào Upload.
- `motion/long/describe.py`: thêm dòng thông báo theo cờ vào trước phần nguồn, bao gồm trong tính toán giới hạn độ dài và tránh chèn trùng.
- Thêm test tương ứng vào `tests/test_channel.py` và `tests/test_describe_fit.py`.

## Chưa làm / cần Lead quyết định

Luồng Short đi qua `motion/stier/enqueue.py`, `motion/stier/enqueue_mim.py`, `motion/stier/enqueue_ck.py`, `motion/stier/upload_one.py`, cùng các file bundle/publish. Quy định AGENTS.md cấm sửa `motion/stier/*.py` và `factory/*` trừ khi ticket code ghi rõ từng file được sửa. Brief chưa nêu đích danh các file này (ngoại trừ `factory/channel.py`), nên chưa sửa chúng. Cần brief bổ sung danh sách file chính xác để nối cờ từ spec qua bundle và upload, thêm thông báo Short, và kiểm thử đầu cuối. Long bundle cũng chưa lưu cờ vì cần sửa cấu trúc bundle chưa được nêu đích danh.

Nếu thông báo đã được ghi sẵn trong phần nguồn hoặc sau đó, hàm hiện giữ nguyên vị trí cũ để không trùng; trường hợp này chưa đảm bảo thông báo nằm trước nguồn, cần xử lý tiếp.

## Kiểm thử

- `python -m pytest -q -p no:cacheprovider tests/test_describe_fit.py`: **7 passed in 0.18s**.
- `python -m pytest -q tests/test_channel.py tests/test_describe_fit.py`: lần đầu có 1 test mô tả thất bại (đã sửa test), 6 passed, 45 errors do PermissionError truy cập thư mục tạm Windows.
- `python -m pytest -q -p no:cacheprovider --basetemp=.tmp_gh458_related tests/test_channel.py tests/test_describe_fit.py`: 7 test mô tả đạt; 45 test fixture lỗi, pytest tiếp tục lỗi PermissionError khi dọn thư mục tạm, không có dòng tổng kết. Không xóa thư mục này do quy định repo.
- `python -m pytest -q tests`: dòng cuối **877 passed, 15 skipped, 67 warnings, 457 errors in 118.26s (0:01:58)**. Nhiều lỗi setup do PermissionError tại `C:/Users/Tung-QA/AppData/Local/Temp/pytest-of-Tung-QA`; chưa thể kết luận toàn bộ lỗi đều cùng nguyên nhân.
- Chưa chạy lint. Đây là ticket code, không dựng video; không có clip sheet hoặc thumbnail.
- Không có khẳng định nội dung cần factcheck. Không gọi mạng, không upload, không sửa lịch, không thao tác Git.
