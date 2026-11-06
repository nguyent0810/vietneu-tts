# GH-179 — Báo cáo phần B

## Kết quả

Đã viết gen_scenes2.py và ch04.json–ch06.json, bổ sung khóa ảnh vào gen_scenes.py, không sửa nội dung cảnh CH00–CH03. Lệnh sinh của ticket chạy thành công và bản thân scenekit ghi lại các chương đã có cũng như spec. Không chạy TTS hoặc render theo ticket.

- CH04: 31 cảnh; date: 11, file: 1, kinetic: 3, ledger: 2, photo: 6, question: 2, slam: 3, split: 2, timeline: 1. Phân loại theo số cảnh: A 5/31 (16.1%), B 4/31 (12.9%), C 0/31 (0.0%), D 22/31 (71.0%).
- CH05: 30 cảnh; date: 3, file: 2, kinetic: 7, ledger: 2, photo: 9, question: 1, slam: 2, split: 2, timeline: 2. Phân loại theo số cảnh: A 8/30 (26.7%), B 2/30 (6.7%), C 0/30 (0.0%), D 20/30 (66.7%).
- CH06: 35 cảnh; date: 7, file: 1, kinetic: 6, ledger: 3, photo: 13, question: 1, slam: 4. Phân loại theo số cảnh: A 11/35 (31.4%), B 5/35 (14.3%), C 0/35 (0.0%), D 19/35 (54.3%).

Cách tính A/B/C/D ở trên là tỷ lệ theo số cảnh, không phải thời lượng: A là photo tư liệu, B là photo AI hoặc cảnh có clip AI, C là minh họa ẩn dụ tách riêng (không dùng), D là các cảnh đồ họa còn lại. cadence không phân loại được phần lớn thời lượng (UNKNOWN 80–88%) vì thiếu timing và thông tin nhận diện, nên không thể báo tỷ lệ thời lượng thực đáng tin cậy.

## Kiểm tra

- python data/long/hoa-than/gen_scenes.py: thành công, CH04 31, CH05 30, CH06 35 cảnh.
- python motion/long/cadence.py hoa-than: CH04 39 thay đổi, 3,85 giây/thay đổi, dài nhất 7,94 giây; CH05 44 thay đổi, 3,41 giây, dài nhất 6,99 giây; CH06 45 thay đổi, 3,33 giây, dài nhất 6,96 giây. Đây là ước tính 150 giây/chương do chưa có timing TTS, không phải đo video thực. CH00–CH03 còn cảnh báo.
- python motion/long/scene_params.py hoa-than: 0 lỗi, 0 cảnh báo.
- python scripts/long_gate.py hoa-than --min-syl 5000: TRƯỢT. Hiện mới có bảy chương, 2.704 âm tiết; thiếu TTS; báo cụm “trong kho”, năm 1760 chưa có trong factcheck, thiếu publish_at, playlist, chapter_titles, video_credits, sources công khai và bảng say. Các hạng mục này nằm ngoài phạm vi chỉnh sửa ticket.
- Kiểm tra ký tự hỏng theo lệnh ticket: in [] (đạt).

## Lệch visual plan

- CH04: theo kịch bản, giữ hai mốc Cam Túc khác nhau và bổ sung vụ Vân Nam cùng vụ Quốc Thái; bỏ lời khẳng định phá án Cam Túc, thâu tóm hàng chục chức và các cảnh suy đoán không có trong kịch bản.
- CH05: dùng hồi môn khoảng 300.000 lạng có ghi nguồn Wikipedia, không dùng “hàng triệu”, lời trích và các suy đoán về tâm lý trong plan. Giữ số phận con trai, công chúa và mối quan hệ gia đình theo kịch bản.
- CH06: theo thứ tự hành trình, yêu sách, từ chối và lời ghi sau năm 1796; bỏ biếm họa Gillray, nhật ký trích dẫn chưa mở, nhận định về bán nước, tuổi 83 và các kết luận không có trong kịch bản.

Các nguồn chưa mở và điểm chưa kiểm được giữ nguyên theo factcheck.md; không đưa lời trích nhật ký Macartney hoặc toàn văn McMahon lên màn hình. Clip sheet, thumbnail: chưa có mới trong phạm vi ticket; ticket cấm render và không giao thumbnail. Chưa xem được chuyển động, chất lượng khung hình hay thời lượng TTS thực. Cần Lead tiếp tục các chương còn lại và xử lý các cổng toàn bài; chưa thể báo hoàn tất video.
