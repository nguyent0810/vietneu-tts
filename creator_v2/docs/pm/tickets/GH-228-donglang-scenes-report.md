# Báo cáo GH-228 — chưa hoàn thành

## Tình trạng

Chưa tạo bộ cảnh, gen_scenes.py hay spec.json; 14 chNN.json vẫn là bản cũ, không phải lời đọc đã duyệt. Chưa chạy script_lines.py vì chưa hoàn thành việc gắn cảnh. Không chạy TTS, render, final; không sửa engine hoặc code dùng chung.

## Vướng mắc cần Lead quyết định

- Cổng bắt buộc python scripts/long_gate.py dong-lang --min-syl 5000 hiện yêu cầu TTS đủ 14 chương, trong khi ticket cấm chạy TTS. Cần quyết định quy trình kiểm cổng sau khi có TTS do Lead thực hiện, hoặc sửa yêu cầu cổng; không thể tự bỏ điều cấm.
- Kế hoạch hình mô tả kịch bản khác bản đã duyệt: ví dụ CH00 nhịp 5–6 mô tả mở quan tài và viên ngọc, còn lời đọc mở đầu chuyển sang phong tỏa và lệnh diễn tập; CH13 nhịp 406 ghi ngày mất 30/9/1947 nhưng bảng factcheck chỉ xác nhận năm 1947. Không được đưa các chi tiết chưa kiểm chứng lên hình. Cần đối chiếu lại kế hoạch với script.md và factcheck.md; chưa xác định đầy đủ mọi nhịp lệch.
- Ticket lần 2 nói ảnh AI và clip Đông Lăng chưa về, cho dùng ảnh tư liệu và clip kho chung. Thư mục ảnh hiện có 23 tệp; thư mục broll của bài chưa tồn tại. Chưa kiểm được tính phù hợp, quyền và khả năng hiển thị của từng tài nguyên trong visual_plan.

## Các lệnh kiểm đã chạy trên trạng thái cũ

- python motion/long/scene_params.py dong-lang: lỗi vì thiếu spec.json.
- python motion/long/floor.py dong-lang: thoát 0 nhưng không in kết quả. Gọi loor.problems đúng chỉ dẫn: 0 loại cảnh (sàn 14), 0 ảnh tư liệu (sàn 40), 0 b-roll (sàn 30), 100% chữ nền trống và 100% kinetic theo cách hàm xử lý dữ liệu trống. Không đạt.
- PYTHONIOENCODING=utf-8 python motion/variety.py audit dong-lang: lỗi vì thiếu spec.json.
- python motion/long/cadence.py dong-lang: 0 lần đổi hình ở cả 14 chương; trung bình không xác định. Các tỷ lệ A/B/C/D đều 0% vì chưa có cảnh, không phải tỷ lệ của sản phẩm hoàn chỉnh.
- python scripts/long_gate.py dong-lang --min-syl 5000: TRƯỢT 33 lỗi. Công cụ đọc 6.884 âm tiết từ các chương cũ; thiếu HUD, cảnh, spec.youtube, say và TTS. Con số này không đại diện script.md đã duyệt.

## Thống kê và bàn giao

Số cảnh đã dựng theo loại: 0. Tỷ lệ A/B/C/D thực tế: chưa xác định. Chưa có clip sheet hay thumbnail; ticket cấm render và không yêu cầu dựng thumbnail. Các khẳng định và tài nguyên trong visual_plan chưa được kiểm toàn bộ. Cần dựng lại lines từ script.md, biên tập từng nhịp bám lời đọc và factcheck, hoàn thiện spec rồi chạy lại toàn bộ cổng. Không báo hoàn tất.
