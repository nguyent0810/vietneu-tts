# Lỗi: publish_long.py đăng tiêu đề cũ, không dùng tiêu đề đã chọn

**Sự cố ngày 06/11:** Bao Thanh Thiên được upload với `spec["title"]` ("BAO THANH THIÊN Ngoài Đời Thật: Bao Chửng"). Tiêu đề Lead đã chọn nằm ở `spec["youtube"]["titles"][0]` và bị bỏ qua. Lead đã sửa tay trên YouTube.

**Áp dụng ngoại lệ AGENTS.md cho ticket code.** Được sửa:
- `motion/long/publish_long.py`;
- test mới `tests/test_publish_long_title.py`;
- báo cáo `docs/pm/tickets/GH-179-title-report.md`.

Ghi file bằng Python, `encoding="utf-8"`.

**Việc:**
1. Thêm một hàm `chosen_title(spec)`:
   - `youtube.titles[0]` nếu có và không rỗng, ngược lại `spec["title"]`;
   - nếu hai giá trị khác nhau, in một dòng cảnh báo cho biết đang dùng cái nào.
   Mọi chỗ hiện dùng `spec["title"]` để làm tiêu đề upload hoặc khớp tiêu đề kênh đều phải đi qua hàm này (dòng 68, 190 và các chỗ khác nếu có). Riêng `thumbnail_text` giữ nguyên hành vi hiện tại.
2. Kiểm tra các script đăng hoặc dựng Long khác (`motion/long/describe.py`, `scripts/*long*`) xem có cùng lỗi không. Chỉ ghi vào báo cáo, không sửa ngoài `publish_long.py`.
3. Test (không gọi API):
   - có `youtube.titles` thì dùng `titles[0]`;
   - không có thì dùng `title`;
   - `titles` rỗng hoặc chuỗi rỗng thì dùng `title`.
4. Chạy `python -m pytest tests -q -k "publish or title"`.

**Không:** commit, upload, gọi API thật.
