# GH-179 — Báo cáo cảnh CH07–CH09

**Trạng thái: chưa đạt cổng tổng, chưa thể bàn giao hoàn tất.** Đã viết `data/long/hoa-than/gen_scenes3.py`, thêm các khóa ảnh cần dùng vào `gen_scenes.py`, tạo và sinh `ch07.json`–`ch09.json`. Lệnh sinh theo ticket cũng cập nhật các chương đã có và spec qua `scenekit.write`. Không chạy TTS, render, upload hay sửa kịch bản.

## Số cảnh

- CH07: 36 — date 7, kinetic 8, photo 11, split 1, slam 3, timeline 1, ledger 1, file 2, question 2.
- CH08: 45 — date 7, kinetic 10, photo 13, file 5, question 3, slam 4, quote 1, timeline 2.
- CH09: 40 — photo 9, ledger 6, kinetic 11, file 6, slam 3, split 2, question 2, date 1.

## Tỷ lệ nhóm

`cadence.py` chưa phân loại được đa số thời lượng, do đó không có tỷ lệ A/B/C/D thời lượng đáng tin cậy. Số liệu của công cụ theo thứ tự A/B/C/D/UNKNOWN: CH07 9,4/0/0/0/87,9%; CH08 7,8/0/0/1,1/91,1%; CH09 8,3/0/0/23,1/66,5%. Phần còn lại là b-roll (CH07 2,7%; CH08 0%; CH09 2,1%). Đây là ước lượng 150 giây/chương do chưa có timing, không phải phép đo video.

Để Lead rà thêm, phân loại sơ bộ **theo số cảnh**, không phải thời lượng: ảnh photo tư liệu A 21/121 (17,4%); photo AI bối cảnh B 5/121 (4,1%); photo AI biểu tượng C 7/121 (5,8%); cảnh đồ họa D 86/121 (71,1%); 2/121 (1,7%) cảnh có video chưa xác định nhóm. Đồ họa có thể dùng ảnh nền nên không thể suy ra tỷ lệ A theo thời lượng từ các số này. Tỷ lệ thực tế và nhãn cần được xác minh bằng khung hình và timing.

## Kiểm tra

- `python data/long/hoa-than/gen_scenes.py`: chạy thành công; CH07 36, CH08 45, CH09 40 cảnh. Lần đầu thiếu ba tệp chương nên đã tạo `lines` từ script trước khi chạy lại.
- `python motion/long/cadence.py hoa-than`: CH07 48 thay đổi, 3,12 giây/thay đổi, tối đa 6,90 giây; CH08 60, 2,50 giây, tối đa 6,20 giây; CH09 65, 2,31 giây, tối đa 6,37 giây. Đây là ước lượng không có TTS; CH08–09 nhanh hơn mục tiêu 3–5 giây theo phép đo thay đổi, cần rà thực tế. CH00–CH03 còn cảnh báo khoảng dài.
- `python motion/long/scene_params.py hoa-than`: 0 lỗi, 0 cảnh báo.
- `python scripts/long_gate.py hoa-than --min-syl 5000`: **TRƯỢT, 12 lỗi**. Mới có 10 chương được sinh; 4.048 âm tiết, chưa có TTS; ảnh canlong dùng 6, hoa 6, giakhanh 9, hieu 6 lần; hai báo lỗi cụm “trong kho”; năm 1760 chưa có trong factcheck; spec thiếu publish_at, playlist, chapter_titles, video_credits, thiếu URL sources và bảng say cho 41 tên/thuật ngữ. Phần còn lại và các tệp chung không thuộc quyền sửa của ticket. Không thể tuyên bố ĐẠT.
- Kiểm chữ hỏng theo lệnh ticket: in `[]`. Chưa có clip sheet hay thumbnail vì ticket cấm TTS và render; đường dẫn hai sản phẩm này chưa có.

## Lệch kế hoạch hình và giới hạn

- CH07 theo đúng thứ tự kịch bản: thoái vị, A Quế mất, quyền qua tấu và vụ Chu Khuê. Các cảnh dùng tài nguyên hợp ý; không khẳng định chi tiết không có trong factcheck.
- CH08 theo kịch bản và factcheck: mất ở Dưỡng Tâm Điện, thọ 87; hai bản khác nhau về người bị bắt cùng; bản chép dải lụa được gắn nguồn, chỉ dụ không mô tả dải. Không dùng các chi tiết kế hoạch về cạm bẫy tang lễ, cảnh công chúa van xin hoặc tuổi 88/49.
- CH09 theo kịch bản: so các ước tính, các dòng bản án, chênh số Lưu Toàn và nghiên cứu Yoon. Không chọn 60–80 triệu làm tổng xác thực, không dùng các khẳng định 80.000 mẫu, đoàn thuyền và các diễn biến chưa được kịch bản/factcheck xác nhận; không cộng các dòng ledger thành tổng.
- Các nguồn và độ tin cậy được kế thừa `factcheck.md`; chưa kiểm tra lại từng URL trong lượt dựng cảnh. Những khác biệt giữa các nguồn được giữ ở dạng có quy thuộc hoặc nêu rõ bất đồng. Không có tờ soát và chưa thể xác nhận hình ảnh AI/clip, vị trí nhãn, chất lượng hình, bản quyền hiển thị hoặc nhịp sau TTS.
