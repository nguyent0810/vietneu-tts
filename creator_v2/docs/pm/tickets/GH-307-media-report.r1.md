# GH-307 — Báo cáo tư liệu Lưu Gù

## Kết quả: chưa thể hoàn tất

Chưa sửa cảnh, chưa sinh lại chương. Sàn hiện tại có **0 cảnh b-roll trước và 0 sau**, cùng 237/480 cảnh chữ nền trống (49,375%; trần 12%). Không thể đạt đồng thời các yêu cầu trong phạm vi ticket:

1. Chỉ thay cảnh bằng ảnh hoặc clip được cung cấp, không chèn cảnh. Muốn giảm 237 cảnh chữ nền trống xuống tối đa 57/480 phải thay ít nhất 180 cảnh chữ nền trống. Có tám clip, mỗi clip tối đa sáu lần: nhiều nhất 48 cảnh. Có 17 ảnh AI hiện có (ai14 vắng), mỗi ảnh tối đa ba lần: nhiều nhất 51 cảnh. Tổng tối đa 99 cảnh thay, chưa xét giới hạn khoảng cách chương hay mức độ phù hợp nội dung; vẫn thiếu ít nhất 81 cảnh. Đây là giới hạn trên, không phải kế hoạch sử dụng được.
2. `spec.json` chưa khai báo ảnh AI, trong khi ticket cấm sửa spec. Vì vậy không thể khai báo `EXT:ai:ai_NN` cho các ảnh để dùng đúng khuôn mẫu mà vẫn giữ spec nguyên vẹn.
3. Lệnh sinh cảnh hiện tại ghi `spec.json` qua `write(...)` và còn trực tiếp ghi lại spec sau đó. Vì ticket cấm sửa spec nên không chạy lệnh này khi chưa sửa được thiết kế sinh cảnh và giải quyết việc khai báo ảnh.
4. `long_gate` đang trượt do thiếu TTS ở cả 14 chương và thiếu các trường `publish_at`, `playlist`, `video_credits` trong `spec.youtube`. Ticket cấm TTS và sửa spec nên không thể làm cổng in ĐẠT trong phạm vi được giao.

Đề nghị Lead quyết định điều chỉnh ràng buộc sàn/tư liệu và xử lý khai báo ảnh, TTS, các trường spec ở bước được phép trước khi tiếp tục. Không thể coi bước này hoàn tất.

## Bảng cảnh và tần suất

| Chương | Cảnh đổi sang ảnh/clip; neo câu |
|---|---|
| CH00–CH13 | Không đổi cảnh; chưa có neo mới. |

| Tư liệu | Số lần dùng mới |
|---|---:|
| v1, v2, v3, v4, v5, v6, v7, v8 | 0 mỗi clip |
| ai01–ai13, ai15–ai18 | 0 mỗi ảnh |
| ai14 | 0; file không có |

## Kiểm tra

1. `python data/long/cl-luu-gu/gen_scenes.py`: **không chạy**, vì lệnh hiện ghi spec bị cấm như nêu trên.
2. `python motion/long/floor.py cl-luu-gu`: mã thoát 0 nhưng **không in kết quả**. Gọi trực tiếp `measure` và `problems` của file này trên 14 JSON chương: 5.814 âm tiết, 480 cảnh, 14 loại, 45 ảnh, 0 cảnh b-roll, kinetic 35,625%, chữ nền trống 49,375%; hai lỗi là thiếu b-roll và vượt trần chữ nền trống.
3. `PYTHONIOENCODING=utf-8 python motion/variety.py audit cl-luu-gu`: **OK**, đủ khác các video gần đây.
4. `python motion/long/cadence.py cl-luu-gu`: **CẢNH BÁO** ngay ở hiện trạng; CH00 và tổng có khoảng tối đa 14,31 giây, dùng ước lượng 150 giây/chương vì chưa có timing, không phải số đo TTS thật.
5. `python motion/long/scene_params.py cl-luu-gu`: 0 lỗi, 0 cảnh báo, nhưng `planned_chapters: 0`; chưa xác minh được cảnh đã lập kế hoạch.
6. `python scripts/long_gate.py cl-luu-gu --min-syl 1900`: **TRƯỢT (2 lỗi)**: thiếu TTS ch00–ch13; thiếu ba trường spec.youtube nêu trên. Lệnh báo 5.814 âm tiết, 479 cảnh, 0 clip khác nhau, 44 ảnh khác nhau, 10 URL. Cách đếm cảnh/ảnh của lệnh khác với `floor.measure`.

Không mở issue qua mạng vì ticket cấm gọi mạng. Không kiểm lại các khẳng định hay URL nguồn trong lượt công việc này; không thêm khẳng định vào lời đọc. Không render hoặc TTS. Clip sheet và thumbnail: không tạo, không kiểm; ticket không cho render và không giao sửa thumbnail. Không đăng, không commit.
