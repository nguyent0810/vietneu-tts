# GH-179 — Báo cáo bước cảnh Hòa Thân

**Trạng thái: CHƯA HOÀN TẤT.** Chưa viết bộ cảnh mới, chưa sửa JSON hiện có; không chạy TTS, render hoặc final. Kết quả dưới đây đo trạng thái sẵn có.

## Vướng mắc cần Lead quyết định

1. Kế hoạch hình chưa khớp lời đọc: CH00 nhịp 02 mô tả chỉ dụ khẩn, nhịp 03 mô tả cổng và thị vệ, trong khi các câu mở đầu kịch bản xác định ngày, địa điểm, tên Trí Trai và Hòa Thân. CH01 nhịp 27–30 đưa ba vòng mở vào đoạn lời đọc đang so sánh các ước tính và nói về Lưu Dung. Cần đối chiếu lại từng nhịp trước khi neo cảnh.
2. Đối chiếu tên File trong kế hoạch với research.json: 43/52 tên trích xuất không khớp nguyên văn danh mục, ví dụ File:Heshen.jpg và File:Hall of Supreme Harmony.jpg. Cần bảng ánh xạ tài nguyên đã xác minh hoặc kế hoạch đã sửa. Đây chỉ là phép so tên; ảnh tương ứng có thể tồn tại dưới tên khác.
3. long_gate yêu cầu TTS 14 chương, nhưng ticket cấm TTS. Tệp script.md và factcheck.md cũng nằm ngoài phạm vi ghi, trong khi cổng báo lỗi về lời đọc và năm 1760. Lead cần xử lý những điều kiện này hoặc làm rõ cách nghiệm thu bước 4.

## Kiểm tra trạng thái hiện có

- `python motion/long/scene_params.py hoa-than`: mã 0, 14 chương, không có lỗi hoặc cảnh báo.
- `python motion/long/floor.py hoa-than`: mã 0, không in kết quả.
- `PYTHONIOENCODING=utf-8 python motion/variety.py audit hoa-than`: mã 0; CL, theme noir, look amber; báo đủ khác các video gần đây; danh sách nhạc nhận diện hiện rỗng.
- `python motion/long/cadence.py hoa-than`: mã 0 nhưng cảnh báo; 416 lượt thay đổi, trung bình 5,05 giây, tối đa 39,49 giây tại ch01#4. CH00–03 và CH10–13 bị cảnh báo; CH08 và CH09 trung bình 2,50 và 2,31 giây. Số liệu ước lượng 150 giây mỗi chương do chưa có timing.
- Cadence ước lượng A 4,1%, B 0%, C 0%, D 10,7%, b-roll 1,8%, UNKNOWN 83,3%. Không thể coi đây là tỷ lệ thực tế đã xác nhận vì UNKNOWN quá lớn.
- `python scripts/long_gate.py hoa-than --min-syl 1900`: mã 1, **TRƯỢT (13 lỗi)**. Ghi nhận 5.718 âm tiết, 304 cảnh, 21 URL; CH12 chỉ có 4 loại cảnh; thiếu TTS 14 chương; 5 ảnh dùng quá 3 lần; hai lần báo cụm “trong kho”; năm 1760 thiếu trong factcheck; spec thiếu 4 trường YouTube, thiếu URL nguồn công khai và bảng phiên âm cho 51 tên hoặc thuật ngữ.
- Lệnh thống kê bị NameError ở phần đếm nhịp plan vì thiếu import re, sau khi đã in số cảnh; không ghi file.

## Cảnh hiện có

Tổng 304: photo 89, date 54, kinetic 49, file 31, slam 22, ledger 22, question 19, timeline 9, split 7, quote 2. Không có cảnh auto: true trong JSON hiện có. Chưa đối chiếu hoàn tất 429 nhịp của kế hoạch.

Chưa tạo gen_scenes.py hoặc gen_scenes2.py, chưa ghi lại chNN.json hay spec.json; chưa xác nhận tỷ lệ thực tế hoặc lập đủ danh sách sai lệch. Không có clip sheet hay thumbnail mới; ticket cấm render và không yêu cầu dựng thumbnail. Không thể báo hoàn tất khi long_gate chưa in ĐẠT.
