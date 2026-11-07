# GH-228 — Báo cáo hiện trạng

**Chưa hoàn thành.** Chưa tạo gen_scenes.py, spec.json hoặc cảnh; 14 tệp chương hiện có vẫn giữ nguyên lời đọc và đều có scenes rỗng. Không đủ cơ sở báo đạt.

## Kiểm tra đã chạy

- python motion/long/scene_params.py mata-hari: lỗi do chưa có spec.json.
- python motion/long/floor.py mata-hari: không in kết quả; gọi trực tiếp floor.problems cho 14 chương trả 5 lỗi: 0 loại cảnh (cần 14), 0 ảnh (cần 40), 0 b-roll (cần 30), chữ nền trống và kinetic đều 100% theo phép tính khi không có cảnh.
- python motion/variety.py audit mata-hari với PYTHONIOENCODING=utf-8: lỗi do chưa có spec.json.
- python motion/long/cadence.py mata-hari: 0 thay đổi hình mỗi chương, không tính được giây mỗi lần đổi; không đạt yêu cầu.
- python scripts/long_gate.py mata-hari --min-syl 1900: TRƯỢT, 33 lỗi; 5.773 âm tiết, 0 cảnh, 11 URL. Thiếu HUD, cảnh, spec.youtube, bảng say và TTS. Ticket cấm chạy TTS ở bước này; không thể đạt cổng đầy đủ trước khi Lead thực hiện bước giọng. Các lỗi còn lại cũng chưa được sửa.

## Nội dung và tài nguyên

Số cảnh theo loại: 0. Không thể tính tỷ lệ A/B/C/D có ý nghĩa khi chưa có cảnh. Chưa đối chiếu từng nhịp với lời đọc hay xác minh các khẳng định và URL; chưa xác định được danh sách khẳng định không kiểm được. Visual plan CH00 có các nhịp về phát súng, thi thể và áo dạ hội mà chỉ dẫn lần hai yêu cầu bỏ; chưa dựng cảnh thay thế. Chưa kiểm quyền và nội dung clip. Không chạy TTS, render hoặc final. Không có clip sheet hay thumbnail được tạo trong ticket này.

Việc còn lại: viết cảnh thủ công bám lời đã duyệt, tạo spec và HUD, kiểm nguồn và tư liệu, chạy lại các cổng của ticket; sau đó Lead chạy TTS và kiểm lại long_gate.
