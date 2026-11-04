# GH-10 · Preview lần 2 cho `mim-jobs-1985` (agy)

Codex đã sửa xong các lỗi "chặn" trong `docs/pm/tickets/GH-10-preview-report.md`; chi tiết ở `GH-10-fix2-report.md`. Claude kiểm lại ba điểm:
- ảnh `nextcube` không còn được dùng;
- mọi cảnh `print` đều có `side.h`;
- `long_gate` ĐẠT và `floor` trả về `[]`.

**Phạm vi và cấm:** giữ đúng như `docs/pm/tickets/GH-10-preview-agy.md`. **Không chạy `final`.**

## Việc

1. Chạy `python motion/long/build_long.py mim-jobs-1985 render --draft`. Chương nào không đổi thì để lệnh tự bỏ qua.
2. Làm lại các sheet `qa/preview_chNN.jpg` và `qa/preview_all.jpg`.
3. Xác nhận từng lỗi trong mục §4 và §5 của `GH-10-preview-report.md` đã hết:
   - 4 tiêu đề `print`: `ch03#6`, `ch04#4`, `ch05#11` (hoặc cảnh thay thế), `ch07#6`;
   - không còn chữ "minitel" ở bất kỳ khung nào;
   - thẻ tên của Sculley;
   - nhãn TRÍCH DỊCH ở `ch01#6`.
4. Lướt toàn bài để tìm lỗi mới do lần sửa này gây ra.

## Báo cáo

Ghi `docs/pm/tickets/GH-10-preview2-report.md`, gồm:
- bảng xác nhận các lỗi trên;
- danh sách lỗi mới, kèm severity và bằng chứng;
- kết luận, chọn một trong hai: **"sẵn sàng final"** hoặc **"cần sửa tiếp"**.
