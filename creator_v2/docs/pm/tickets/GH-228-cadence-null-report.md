# GH-228 — báo cáo

**Trạng thái: chưa hoàn tất các cổng của ticket.** Đã sửa `motion/long/cadence.py` dùng `Anchors` của engine cho các dạng mốc, gồm `null`, lần xuất hiện và độ lệch. Khi thiếu mốc từng từ, nội suy từ thời gian câu; khi có `words`, dùng thời điểm có sẵn. Float nay được hiểu là giây tuyệt đối theo `Anchors`. Việc so khớp từ cũng theo engine, thay vì khớp chuỗi con như trước.

## Kiểm tra

- Kiểm tra trực tiếp bằng Python các dạng `int`, `float`, `[i]`, `[i, null, 0, off]`, `[i, w]`, `[i, w, n]`, `[i, w, n, off]`: đạt, kể cả từ lặp và độ lệch; đây không thay thế test hồi quy được lưu trong repo.
- `python -m pytest tests -q -k "cadence or anchor"` (tắt bytecode và pytest cache): 20 đạt, 2 lỗi setup do `PermissionError` khi đọc thư mục tạm `C:\Users\Tung-QA\AppData\Local\Temp\pytest-of-Tung-QA`, 1057 bị loại.
- `python -m pytest tests -q -k '(cadence or anchor) and not scheduled_video and not say_changes_tts_input'` (tắt bytecode và pytest cache): 20 đạt, 1059 bị loại. Bài scheduled_video dùng `state.sqlite` tạm; bài say_changes bị loại ở lần chạy này vì lỗi thư mục tạm nói trên.
- Không chạy toàn bộ `python -m pytest tests -q`: trong suite có test thực thi mã publish/enqueue và ghi `state.sqlite` tạm, xung đột với lệnh cấm trong AGENTS.md. Vì vậy chưa thể xác nhận toàn bộ suite xanh.
- `PYTHONIOENCODING=utf-8 python motion/long/cadence.py mata-hari`: thoát 0, có cảnh báo cadence ở nhiều chương; dữ liệu dùng ước tính 150 giây/chương, tổng khoảng dài nhất 12,90 giây, nhóm UNKNOWN 67,8%.
- `PYTHONIOENCODING=utf-8 python motion/long/cadence.py hoa-than`: thoát 0, dùng `data.js` đã lập kế hoạch; cảnh báo ch13, khoảng dài nhất 9,00 giây. Cách chạy này không chứng minh nhánh mốc gốc của ch00 đã được sử dụng vì dữ liệu đã lập kế hoạch được ưu tiên.

## Việc còn lại

- Chưa thêm test vào `tests/`: AGENTS.md cấm sửa `tests/*` trừ khi brief nêu rõ từng tên file code dùng chung được sửa và yêu cầu làm trong worktree hoặc nhánh riêng; brief chỉ nói thêm test mới trong `tests/`, không ghi tên file test cụ thể hoặc yêu cầu worktree/nhánh riêng. Cần Lead làm rõ và cập nhật brief phù hợp trước khi thêm test.
- Cần Lead xác định cách chạy toàn bộ suite phù hợp với lệnh cấm publish/enqueue và `state.sqlite`, và xử lý quyền thư mục tạm. Chưa chạy lint riêng; ticket không chỉ định lệnh lint.
- Không có khẳng định nội dung cần factcheck; không dựng video, nên không có clip sheet hoặc thumbnail.
