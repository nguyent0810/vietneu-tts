# GH-179 — Báo cáo chưa hoàn thành

Chưa dựng dày tám chương và chưa đạt cổng hoàn thành. Đã đối chiếu sơ bộ script, visual_plan và factcheck. Một số nhịp trong visual_plan dựa trên lời dự kiến khác kịch bản hiện tại; CH13 dùng tư liệu Yamanaka 1912 trong khi factcheck ghi đã bỏ. Cần đối chiếu từng nhịp với lời đọc và dữ kiện đã kiểm.

Đã thử thêm chín cảnh CH00 nhưng chữ bị lỗi mã hóa qua shell. Đã loại cả chín cảnh thử và chạy lại cadence. Nội dung cảnh CH00 trở về như trước; tệp JSON đã được ghi lại định dạng. Số cảnh thêm theo loại: 0.

## Cadence trước và sau

Mỗi ô: số lần đổi hình / giây trung bình mỗi lần / khoảng dài nhất (giây). Sau giống trước vì không giữ cảnh thử. Đây là ước lượng 150 giây/chương khi chưa TTS.

| Chương | Trước | Sau |
|---|---|---|
| CH00 | 12 / 12,50 / 25,32 | 12 / 12,50 / 25,32 |
| CH01 | 13 / 11,54 / 39,49 | 13 / 11,54 / 39,49 |
| CH02 | 16 / 9,38 / 24,71 | 16 / 9,38 / 24,71 |
| CH03 | 19 / 7,89 / 32,09 | 19 / 7,89 / 32,09 |
| CH04 | 39 / 3,85 / 7,94 | 39 / 3,85 / 7,94 |
| CH05 | 44 / 3,41 / 6,92 | 44 / 3,41 / 6,92 |
| CH06 | 45 / 3,33 / 6,96 | 45 / 3,33 / 6,96 |
| CH07 | 48 / 3,12 / 6,90 | 48 / 3,12 / 6,90 |
| CH08 | 60 / 2,50 / 6,20 | 60 / 2,50 / 6,20 |
| CH09 | 65 / 2,31 / 6,37 | 65 / 2,31 / 6,37 |
| CH10 | 12 / 12,50 / 37,27 | 12 / 12,50 / 37,27 |
| CH11 | 12 / 12,50 / 38,76 | 12 / 12,50 / 38,76 |
| CH12 | 16 / 9,38 / 27,00 | 16 / 9,38 / 27,00 |
| CH13 | 16 / 9,37 / 35,23 | 16 / 9,37 / 35,23 |

## Kiểm tra

- `python motion/long/cadence.py hoa-than`: chạy thành công; tám chương được giao vẫn cảnh báo.
- `python motion/long/scene_params.py hoa-than`: mã thoát 0, không lỗi hoặc cảnh báo. Chạy khi còn cảnh thử, sau đó đã bỏ các cảnh thử.
- `python motion/long/floor.py hoa-than`: mã thoát 0 nhưng không in kết quả; chưa xác nhận cổng floor.
- `python motion/long/variety.py audit hoa-than` và `python scripts/variety.py audit hoa-than`: không tìm thấy file tại hai đường dẫn thử; chưa chạy được audit. Ticket không ghi đường dẫn; cần Lead chỉ đúng đường dẫn theo giới hạn không khám phá repo.
- `python motion/long/factcheck_lint.py hoa-than`: 0 lỗi.
- `python scripts/long_gate.py hoa-than --min-syl 5000`: **TRƯỢT**; 5.722 âm tiết, 305 cảnh; một lỗi là thiếu TTS cho CH00–CH13. Không chạy TTS vì ticket chỉ cho phép sửa các tệp cảnh và yêu cầu gate chỉ còn lỗi chưa TTS. Yêu cầu người giao là in ĐẠT chưa được đáp ứng.

Cần dựng lại tám chương theo từng câu, kiểm giới hạn ảnh và chạy lại các cổng, xác định đường dẫn audit và cách chạy floor có kết quả, tạo timing TTS cho đủ 14 chương. Chưa render, chưa kiểm trực quan, chưa có clip sheet hoặc thumbnail mới. Chưa kiểm thêm nguồn ngoài; các giới hạn nguồn giữ như factcheck hiện tại.
