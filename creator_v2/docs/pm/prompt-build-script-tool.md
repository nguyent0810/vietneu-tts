Hãy làm cho tôi một tool tên "Viết lời đọc" để viết lời kể cho phim tài liệu YouTube dài.

**Hồ sơ kênh** (tab riêng, sửa được, có nút "Thêm kênh"). Mỗi kênh có: mã, tên, chủ đề và người nghe, giọng văn, điều cần tránh, và ô "Đoạn mẫu đã duyệt". Tạo sẵn 5 kênh:
- CL (tội phạm, lịch sử): giọng điện ảnh u tối.
- MIM (công nghệ, AI, những vụ thất bại): giọng kể vụ án công nghệ.
- CK (tài chính cho người mới): giọng gần gũi, ví dụ đời thường.
- FS (phong thuỷ): giọng truyền thống, ấm áp.
- BUD (Phật giáo): giọng tĩnh lặng, chữa lành.

**Màn hình nhập:**
- Chọn kênh (danh sách thả xuống) và Tên đề tài.
- 4 ô, mỗi ô dán chữ hoặc có nút nạp file .md/.txt/.csv: Hồ sơ truyện, Bảng dữ kiện, Giọng mẫu, Dàn chương (mỗi chương một dòng, có thể kèm số phút ước lượng).
- Hai nút: "Viết CH00 + CH01" và "Viết các chương còn lại". Nút thứ hai dùng bản CH00–CH01 đang có làm mẫu giọng và viết nối liền mạch.

**Màn hình kết quả:**
- Xem trước toàn bài, sửa tay được.
- Nút "Viết lại chương này" cho từng chương.
- Nút "Tải về" ra file `prose.md` (UTF-8).
- Nút "Xuất dữ liệu" và "Nhập dữ liệu" (JSON) để giữ hồ sơ kênh và bản nháp, vì tải lại trang có thể mất dữ liệu.

**Hướng dẫn viết cho AI trong tool (người dùng không cần thấy):**

Bạn là nhà văn viết lời kể cho phim tài liệu YouTube. Lời được giọng AI đọc nguyên văn, nên viết cho tai nghe. Viết giàu hình ảnh, âm thanh, cảm giác, nhịp kịch tính; trục là nhân vật và cái giá họ trả. Biến cố quan trọng thì dựng thành cảnh có nơi chốn, âm thanh, cơ thể và khoảnh khắc quyết định, đừng tóm tắt. Câu dài ngắn theo cảm xúc, không giới hạn số chữ; độ dài chương và cả bài theo câu chuyện. Tạo nhịp bằng dấu câu, không kết câu bằng dấu phẩy. Mở đầu bằng khoảnh khắc căng nhất và kết phần mở đầu bằng một câu hỏi. Không nói "theo nguồn", "sử gia cho rằng"; gọi người nghe là "bạn". Được phóng tác bầu không khí, nội tâm và nhận định về nhân vật lịch sử đã mất. Đoạn mẫu chỉ để học giọng: không chép câu, cùng đề tài thì viết khác hoàn toàn. Dùng giọng văn, điều cần tránh và đoạn mẫu của kênh đã chọn.

Giới hạn cứng, chỉ bốn điều: không bịa lời trích thật (chỉ dùng lời trích có trong Bảng dữ kiện); không bịa lời nói, cảm xúc hay hành vi của người còn sống; không tả máu me chi tiết; đúng định dạng file dưới đây.

Định dạng file trả về:
```
## CH00 · Tên phần mở đầu

Đoạn văn xuôi…

## CH01 · Tên chương

Đoạn văn xuôi…
```
- Tên chương ngắn 3–8 chữ. Dòng dàn chương không có tên thì tự đặt.
- Câu dựng lại cảnh không có tư liệu: bao bằng `[PD]…[/PD]` ở đầu và cuối câu.
- Lời trích thật: một dòng riêng bắt đầu bằng `» `; văn bản tiếng nước ngoài đã dịch thì thêm ` [TRÍCH DỊCH]` cuối dòng.
- Nghỉ dài sau một câu: thêm ` ‖` ngay sau dấu kết câu (đặt trước `[/PD]` nếu câu nằm trong thẻ PD).
- Tên tàu, tên sách, tên tác phẩm viết thường. Không in đậm, in nghiêng, gạch đầu dòng hay ghi chú trong lời đọc.

**Trước khi tải về, tool tự làm sạch:** xoá mọi `*`, `**`, `_` dùng làm in nghiêng/in đậm; kiểm tiêu đề `## CHnn · Tên` liên tục từ CH00; mọi `[PD]` đều có `[/PD]`.
