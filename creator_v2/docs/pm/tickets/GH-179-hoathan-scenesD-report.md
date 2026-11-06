# GH-179 — Báo cáo phần D

**Trạng thái: CHƯA HOÀN THÀNH.** Đã tạo cảnh biên tập và JSON cho CH10–CH13, nhưng còn thiếu nhiều nhịp, chưa có endcard và không qua cổng bắt buộc. Không dùng để render hoặc xuất bản.

## Việc đã làm

- Tạo `data/long/hoa-than/gen_scenes4.py`, tạo CH10–CH13 từ các câu trong kịch bản và chạy bộ sinh.
- Số cảnh: CH10 9 (date 1, photo 3, file 3, ledger 1, question 1); CH11 12 (question 1, file 5, photo 4, date 1, slam 1); CH12 11 (date 4, timeline 1, photo 5, ledger 1); CH13 14 (date 6, file 3, photo 3, ledger 1, question 1).
- Không sửa cảnh chương khác bằng tay. Bộ sinh đã cập nhật các JSON chương và spec theo chức năng sẵn có. Không chạy TTS hoặc render.
- Lần đầu ảnh AI trong từng chương có `credit: false` và nhãn tái dựng; chưa kiểm bằng khung hình.
- Kế hoạch hình lệch kịch bản: CH11 chỉ dùng tên diễn viên, không dùng hình phim; CH12 theo thứ tự 1799, 1850, 1852 trong kịch bản; CH13 bỏ tư liệu Yamanaka 1912 vì không có trong kịch bản và chưa được kiểm chứng.

## Kiểm tra

- `python data/long/hoa-than/gen_scenes.py`: chạy xong, sinh 14 chương.
- `python motion/long/cadence.py hoa-than`: cảnh báo CH10–CH13; lần lượt 12,50 / 12,50 / 10,00 / 9,37 giây mỗi thay đổi; khoảng dài nhất 37,27 / 38,76 / 28,45 / 35,23 giây. Ước tính do chưa có timing; đều chưa đạt yêu cầu 3–5 giây và tối đa 8 giây.
- Tỷ lệ A/B/C/D theo cadence lần lượt: CH10 2,1/0/0/11,1%; CH11 3,6/0/0/0%; CH12 3,8/0/0/3,2%; CH13 3,5/0/0/4,5%. UNKNOWN lần lượt 86,9%, 96,4%, 93,0%, 91,9%; đây không phải tỷ lệ hoàn chỉnh đáng tin cậy.
- `python motion/long/scene_params.py hoa-than`: không lỗi, không cảnh báo.
- `python motion/long/floor.py hoa-than`: không in kết quả trong lượt chạy; không có căn cứ kết luận ĐẠT.
- `python motion/variety.py audit hoa-than`: OK, đủ khác video gần đây.
- `python scripts/long_gate.py hoa-than --min-syl 5000`: **TRƯỢT, 13 lỗi**. CH12 thiếu loại cảnh; chưa TTS toàn bộ 14 chương; ảnh canlong, hoa, luudung, giakhanh, hieu dùng quá 3 lần; lời đọc bị phát hiện cụm “trong kho”; năm 1760 không có trong factcheck theo cổng; thiếu metadata xuất bản, nguồn công khai và bảng SAY. Âm tiết 5.718, nguồn 21 URL.
- Lỗi thiếu TTS không thể xử lý trong ticket vì ticket cấm TTS; các lỗi kịch bản và metadata cần Lead xử lý theo đúng phạm vi cho phép.
- Các khẳng định đưa vào cảnh lấy từ kịch bản và bảng factcheck; chưa kiểm lại từng URL trong lượt này. Không khẳng định đã kiểm chứng độc lập.

Clip sheet và thumbnail: không tạo trong ticket này. Cần tiếp tục bổ sung nhịp gắn câu, endcard, sửa variety và kiểm lại mọi cổng trước khi nhận hoàn thành.
