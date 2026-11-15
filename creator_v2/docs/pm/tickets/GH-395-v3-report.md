# GH-395 v3: báo cáo bản viết lại lời Long CL `cl-dich-nhan-kiet`

Người kể: Sonnet. File: `data/long/cl-dich-nhan-kiet/script.v3.md` (không ghi đè `script.md`).

- Âm tiết (đếm từ, như script_lines.py): **5.728** (yêu cầu 5.600 đến 6.800). 14 chương CH00 đến CH13, 383 câu, câu dài nhất 32 âm tiết. Ước lượng khoảng 26 phút.
- Rào nguồn: **19/383 câu = 4,96%** (regex theo|ghi|chép|nguồn|bách khoa|wikipedia|trang tiếng|sử cảo|tài liệu|bản ghi, khớp cả chuỗi con như "nghiên", "ghi danh"; ngưỡng 8%). Không câu nào mở bằng "theo" liên tục.
- Số cảnh phỏng dựng `{pd}`: **31**.
- Số câu đối chiếu phim: hai chỗ (CH04 một lần nhắc "vụ án ma quái trong phim", CH13 kết).
- Ba tiêu đề (không nêu nguồn):
  1. Tể Tướng Tự Nhận Mình Phản: Ba Chữ Cứu Mạng Địch Nhân Kiệt (58 ký tự)
  2. Mảnh Lụa Giấu Trong Áo Bông: Tể Tướng Thoát Chết Ra Sao? (56)
  3. Xử 17.000 Án Không Ai Kêu Oan, Rồi Tự Nhận Mình Phản? (53)
- Kết quả kiểm (Python, trên script.v3.md): `script_lines.parse` + `gate` = [] ; `craft.audio_problems` = [] ; `beat_warnings` chỉ còn một cảnh báo đuôi 1560 đến 1564 s (4 giây cuối).
- Cold open (CH00, 183 âm tiết, khoảng 40 s): câu sốc ở câu 1, câu hỏi ở câu 4, bằng chứng đối lập (17.000 người) ở câu 4, không chào, không lộ trình.

## Điểm cần Lead soát
- Câu `{pd}` chỉ tả không gian, đồ vật, người vô danh; không thêm lời, số, phán quyết.
- Các chi tiết chỉ có ở một nguồn được kể tiết chế: Kỳ Châu (S2), màn trướng và lý lẽ số lính (S1/S2), hạn hán Bành Trạch (W2, lời đọc nói "bản tiếng Trung").
- CH13: câu "Cảnh Huy làm quan ở Ngụy Châu... phá sinh từ của cha" ghép từ FC §12 và §16 (Z207 nói về tượng/hình); không gắn với sinh từ ở Bành Trạch.
- Không dùng Hán tự của Nghiêm Thiện Tư vì FC chưa có.
