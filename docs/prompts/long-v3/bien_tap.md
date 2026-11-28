# Biên tập sau Gemini — NHẸ TAY (PO 27/11)

Chỉ sửa những gì liên quan tới THÔNG TIN CẦN CHÍNH XÁC: con số, can chi, tên sao/hạn, ngày Tết, tên kinh và lời trích, tên người thật, luật an toàn kênh (không hứa tiền, không doạ, không bịa lời người còn sống). Không biên tập chi tiết câu chữ, không cắt đoạn, không san phẳng nhịp, không ép độ dài: bài ngắn hay dài hơn do chất liệu là chấp nhận được. Câu dài quá sức đọc TTS (> 35 tiếng) thì chỉ tách tại chỗ.

---
(Phần dưới là ghi chú tham khảo cũ, ưu tiên thấp hơn đoạn trên.)

# Biên tập sau Gemini (ngắn)

Nguyên tắc (chủ kênh 25/11: "biên tập giữ giọng hay cho tai, không cắt cụt, không chặt câu khô"): sửa tối thiểu. Bản Gemini v2 được khen vì hành văn; đừng viết lại cho "đúng khuôn".

1. Đọc thành tiếng hoặc nghe thử TTS đoạn đầu (15–40 giây đầu và đoạn kết). Chỗ vấp, chỗ phải nghe lại mới hiểu thì sửa đúng câu đó.
2. Giữ giọng: chỉ cắt (a) câu cảnh vô nghĩa chen vào mà không đổi gì cho ý, (b) câu nhắc lại tiêu đề, (c) sáo ngữ ("trớ trêu thay"). Không chặt câu dài hay hay.
3. Kiểm dữ kiện từng con số, năm, tên, con giáp so với bảng dữ kiện; FS chạy lại code sinh số. Chỗ nào Gemini tự thêm kiến thức ngoài bảng thì xoá hoặc đưa về dữ kiện.
4. Chuyển luật an toàn sang khâu này (không nhồi vào prompt): BUD lời Phật gán đúng kinh (`hf_sutta.py`); CL/MIM không có lời trích hay cảm xúc người còn sống bịa; CK không có lời hứa lãi; FS tên chi, "theo cách tính dân gian", không phán xấu chắc chắn; không máu me chi tiết.
5. Kiểm lời hứa: lời hứa ở đầu bài (và ở các chỗ kéo lại giữa Long dài) có được trả đúng thứ đã hứa không; vòng mở có đóng không; kết có gọi lại đầu bài không. Thiếu thì thêm một hai câu, không viết lại đoạn.
6. Định dạng cho TTS: bỏ ký hiệu, gạch đầu dòng, ngoặc đơn còn sót; số và năm đọc tự nhiên. Chạy `tools/prose_to_script.py` rồi lint theo SKILL.
7. Gắn mốc chương SAU (bài viết liền, không có tiêu đề): chọn các chỗ đổi lớp (đoạn nối "ta vừa đi qua... sắp tới...", câu hỏi mới, mốc re-hook) làm điểm chương, đặt tiêu đề bằng câu người xem gõ tìm, 3–8 chữ; Long vừa 3–5 mốc, Long dài một mốc mỗi 3–5 phút. Ghi vào plan/mô tả theo giờ thật của TTS (`00:00` đầu, mốc đầu >= 10 giây, mỗi mốc >= 10 giây) cho mục lục YouTube. Thẻ chương là điểm đến khi tua (evidence.md: F6, F1 tăng ở thẻ chương), nên đặt đúng chỗ đổi nghĩa.
8. Đường lùi: nếu bản nháp có chỗ chương rơi (định nghĩa dài, đọc bảng, dồn số) thì chia nhỏ ra xen cảnh, theo evidence.md, không bỏ dữ kiện.


## Bỏ sáo, giữ kịch (PO 27/11)
- Xoá câu nói về chính video ("nghe hết bài này", "trong video này", "cuối bài bạn sẽ…").
- Lời rào "chỉ là kiến thức tham khảo / theo cách tính dân gian" chỉ giữ MỘT lần, ở CUỐI bài (kiểu "Nhân định thắng Thiên, con người mới là gốc"); đầu và giữa bài xoá hết; lời nhắc tham khảo đầy đủ đặt ở mô tả video.
- Kết bằng lời khuyên chung chung ("hãy tỉnh táo") thì thay bằng hình ảnh hoặc câu gợi nghĩ có sẵn trong bài.
- Không san phẳng chỗ cao trào: câu ngắn ở đỉnh và khoảng lặng sau đỉnh phải giữ.
