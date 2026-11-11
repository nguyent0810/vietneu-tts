<!-- plan-sources:start -->
## Kiểm nguồn tự động (2026-11-11)

> Kết quả hỗ trợ rà soát, không chứng minh nội dung đúng; CHAN và KHONG_MO_DUOC chưa được xác minh.

| URL | Trạng thái | Số file Commons (gồm một cấp con) | Chi tiết |
|---|---|---:|---|
| https://commons.wikimedia.org/wiki/File:Di_Renjie.jpg | OK | — |  |
| https://commons.wikimedia.org/wiki/File:%E7%8B%84%E4%BB%81%E6%9D%B0.jpg | OK | — |  |
| https://commons.wikimedia.org/wiki/File:Portraits_of_Famous_Men_-_Di_Renjie.jpg | KHONG_CHUA_SO | — | 19 |
| https://commons.wikimedia.org/wiki/File:%E6%A2%81%E5%85%AC%E4%B9%9D%E8%AB%AB.jpg | HTTP 404 | — |  |
| https://commons.wikimedia.org/wiki/File:%E6%B4%9B%E9%98%B3%E7%99%BD%E9%A9%AC%E5%AF%BA%E5%86%85%E7%8B%84%E4%BB%81%E6%9D%B0%E5%A2%93.jpg | OK | — |  |
| https://commons.wikimedia.org/wiki/File:Tomb_of_Di_Renjie,_White_Horse_Temple.jpg | HTTP 404 | — |  |
<!-- plan-sources:end -->

> **Ghi chú của Lead (11/11/2026), đọc trước:** plan do Gemini Flash viết; ngày tháng, giai thoại và URL **chưa kiểm**. Số ảnh trong plan là ước lượng của model. Lead đếm thật trên Wikimedia Commons: category riêng của nhân vật có **2 file**. Phần còn lại phải là ảnh bối cảnh (triều đại, kiến trúc, tranh thời đó), nên bước tư liệu phải đếm đủ khoảng 50 ảnh tự do trước khi viết.

# Kế hoạch Long CL: ĐỊCH NHÂN KIỆT Ngoài Đời Thật (Đề tài ứng viên 1)

Kế hoạch ngắn gửi chủ kênh duyệt theo ticket `GH-CL3-agy`. Chưa viết kịch bản, chưa TTS, chưa render.
Dữ liệu lịch sử: *Cựu Đường thư* (quyển 89), *Tân Đường thư* (quyển 115), *Tư trị thông giám* (quyển 202–206).

## 1. Vì sao hợp CL bây giờ & góc kể khác các Long đã có

- **Sức hút IP điện ảnh/truyền hình:** Địch Nhân Kiệt là thương hiệu trinh thám phá án cổ trang quen thuộc nhất với khán giả Việt Nam qua loạt phim truyền hình nhiều phần *Thần thám Địch Nhân Kiệt* (Lương Quan Hoa) và các bom tấn điện ảnh của đạo diễn Từ Khắc (*Thông thiên đế quốc*, *Rồng biển trỗi dậy*). Khán giả mặc định nhớ tới ông như một "Sherlock Holmes phương Đông" chuyên phá án ma quái, trừ tà và đấu võ hiệp.
- **Trùng hướng với Long Bao Thanh Thiên đã làm (08/11/2026):** Cả hai đều là biểu tượng quan tòa xử án thanh liêm của lịch sử phong kiến Trung Hoa.
- **Góc kể khác biệt hoàn toàn:**
  1. *Bao Chửng* là vị quan đứng đầu phủ Khai Phong thời Tống, chuyên xử án dân gian, chống hoàng thân quốc thích giữa công đường bằng uy quyền pháp luật và đao chém đầu.
  2. *Địch Nhân Kiệt* không phải hiệp khách múa kiếm phá kỳ án quái dị, mà là một **Đại thẩm phán (Đại lý thừa)** xử lý khối lượng án tồn đọng kỷ lục (17.000 phạm nhân trong 1 năm không ai kêu oan), kiêm **Tể tướng chính trị thượng thừa** thời kỳ bạo quyền đen tối nhất: chế độ khủng bố mật vụ của Võ Tắc Thiên (triều Võ Chu).
  3. Khác với sự cương trực thẳng thừng của Bao Chửng, vũ khí lớn nhất của Địch Nhân Kiệt là **sự kiên nhẫn và mưu lược sinh tồn**: ông từng phải giả vờ nhận tội mưu phản trước Khốc lại Lai Tuấn Thần để thoát chết trong gang tấc, rồi xé áo bông nhét thư máu giải oan; ông dùng trí tuệ can gián Võ Tắc Thiên trao trả lại giang sơn cho nhà Đường thay vì dòng họ Võ, sắp đặt mạng lưới nhân tài (Trương Giản Chi, Diêu Sùng) chuẩn bị cho ngày phục hưng triều đại.

## 2. Đếm sơ bộ ảnh tự do (Wikimedia Commons & SOURCES.md)

- **Ảnh trực tiếp về nhân vật (Category:Di Renjie & Subcategories):** Khoảng 18–22 ảnh.
  - Chân dung tranh khắc cổ Wanxiaotang (1921), tranh tàng bản Cung đình nhà Thanh (PD-old).
  - Tranh mộc bản *Lương Công cửu gián* và tranh minh họa sách cổ (PD).
  - Ảnh chụp thực địa khu lăng mộ Địch Nhân Kiệt tại Chùa Bạch Mã, Lạc Dương (CC BY-SA / CC0).
- **Ảnh bối cảnh thời Đường & Võ Chu:** Khoảng 40–50 ảnh bổ trợ (chân dung Võ Tắc Thiên trong `Category:Wu Zetian`, Vô Tự Bia Càn Lăng, kiến trúc Chùa Bạch Mã Lạc Dương, bản đồ Trường An - Lạc Dương thời Đường, tượng gốm quan lại Đường tam thái).
- **Đánh giá kiểm kê:** **Rủi ro thiếu ảnh.** Số lượng ảnh trực tiếp về Địch Nhân Kiệt và di tích của ông khá mỏng (dưới 40 ảnh). Khi dựng video 25–30 phút, bắt buộc phải dùng nhiều ảnh bối cảnh thời Đường, bản đồ đồ họa cổ, hiện vật pháp đình Đại Lý Tự và hồ sơ tư liệu chữ.

**5–8 link ảnh mẫu đã kiểm duyệt giấy phép:**
1. https://commons.wikimedia.org/wiki/File:Di_Renjie.jpg (Chân dung mộc bản Wanxiaotang 1921, Public Domain)
2. https://commons.wikimedia.org/wiki/File:%E7%8B%84%E4%BB%81%E6%9D%B0.jpg (Tranh chân dung Địch Nhân Kiệt từ Thanh Cung điện tàng họa bản, Public Domain)
3. https://commons.wikimedia.org/wiki/File:Portraits_of_Famous_Men_-_Di_Renjie.jpg (Tranh trục lụa Địch Nhân Kiệt thế kỷ 19, Philadelphia Museum of Art, Public Domain)
4. https://commons.wikimedia.org/wiki/File:%E6%A2%81%E5%85%AC%E4%B9%9D%E8%AB%AB.jpg (Tranh khắc cổ Lương Công cửu gián, Public Domain)
5. https://commons.wikimedia.org/wiki/File:%E6%B4%9B%E9%98%B3%E7%99%BD%E9%A9%AC%E5%AF%BA%E5%86%85%E7%8B%84%E4%BB%81%E6%9D%B0%E5%A2%93.jpg (Khu lăng mộ Địch Nhân Kiệt tại Chùa Bạch Mã Lạc Dương, CC BY-SA 3.0)
6. https://commons.wikimedia.org/wiki/File:Tomb_of_Di_Renjie,_White_Horse_Temple.jpg (Bia mộ và kiến trúc khu tưởng niệm Địch Nhân Kiệt, CC BY-SA 4.0)

## 3. Cold open (~40 giây)

Một đêm mùa xuân năm 692 trong ngục thất tăm tối tại Lạc Dương, cỗ máy tra tấn khét tiếng của Khốc lại Lai Tuấn Thần vừa tạm dừng khi viên thẩm phán 62 tuổi Địch Nhân Kiệt đặt bút ký vào bản tự thú: "Triều Chu cách mạng, ta mưu phản là thật." Cả đời từng phân xử oan sai cho hàng vạn người, ông hiểu rất rõ nếu không nhận tội, chiếc lồng đinh tra tấn "Định bách mạch" sẽ lấy mạng ông trước khi trời sáng. Nhưng khi ngục tốt vừa quay lưng, Địch Nhân Kiệt lén xé lớp lót chiếc áo bông mùa đông, dùng máu viết vội một bức thư kêu oan nhét sâu vào ruột áo, rồi nhờ chuyển về nhà với lời dặn: "Trời sang xuân, gửi áo về rút bớt bông." Một chiếc áo rách gửi ra khỏi ngục tối không chỉ cứu mạng vị thẩm phán lỗi lạc, mà còn xoay chuyển cả vận mệnh ngai vàng triều Đường.

## 4. Ba vòng mở và chỗ đóng

- **Vòng 1 (Huyền thoại phá án vs Thực tế):** Địch Nhân Kiệt có thực sự phá các kỳ án ma quái như phim Từ Khắc và tiểu thuyết của Robert van Gulik, hay sự nghiệp tư pháp của ông được xây dựng trên những hồ sơ nào? Đóng ở Chương 3 và 4 (Hồ sơ 17.000 tù nhân Đại Lý Tự năm 676 và kỳ án Chiêu Lăng).
- **Vòng 2 (Sinh tồn trước bạo quyền):** Làm thế nào một vị quan trung thành với hoàng tộc họ Lý lại có thể sống sót, được chính Võ Tắc Thiên tin cẩn giao ghế Tể tướng giữa thời kỳ mật thám Khốc lại tàn bạo nhất? Đóng ở Chương 7 (Vụ án áo bông năm 692 và sự sụp đổ của Lai Tuấn Thần).
- **Vòng 3 (Ván cờ phục hưng triều đại):** Địch Nhân Kiệt đã dùng mưu lược chính trị nào để thuyết phục nữ hoàng duy nhất trong lịch sử Trung Hoa trao trả lại ngai vàng cho nhà Đường thay vì truyền cho họ Võ? Đóng ở Chương 9 và 10 (Lời can gián Thái miếu và mạng lưới ngầm Thần Long 705).

## 5. Dàn ý 13 chương (mỗi chương một dòng)

- Ch0: Lạc Dương, năm 692: Bản nhận tội mưu phản và bức thư máu giấu trong chiếc áo bông.
- Ch1: Huyền thoại và Sử liệu: Từ "Công án Địch" của Robert van Gulik đến hai bộ Đường thư.
- Ch2: Chốn quan trường thuở đầu: Đỗ Minh kinh, làm Tiêu phủ phán quan và danh tiếng liêm chính.
- Ch3: Kỷ lục Đại Lý Tự (676): Một năm xử lý 17.000 phạm nhân tồn đọng, không một người kêu oan.
- Ch4: Vụ án cây bách Chiêu Lăng: Đứng trước Đường Cao Tông bảo vệ tính tôn nghiêm của pháp luật.
- Ch5: Đêm tối Võ Chu và sự trỗi dậy của Khốc lại: Lai Tuấn Thần, Chu Hưng và các ngục hình man rợ.
- Ch6: Thứ sử cứu dân: Trấn nhậm Dự Châu, giải cứu 2.000 người vô tội khỏi án tru diệt phản nghịch.
- Ch7: Ván cờ trong ngục tối: Chiếc áo bông giải oan và cú lừa ngoạn mục đánh bại Lai Tuấn Thần.
- Ch8: Trở lại đỉnh cao quyền lực: Làm Tể tướng thời Võ Tắc Thiên, đối mặt nạn tranh giành quyền bính.
- Ch9: Trận can gián Thái miếu: "Chưa từng thấy cháu thờ cúng cô", cứu ngai vàng cho họ Lý.
- Ch10: Mạng lưới ngầm cứu quốc: Tiến cử Trương Giản Chi, Diêu Sùng, dọn đường cho biến cố Thần Long.
- Ch11: Uy danh biên cương: Đẩy lùi quân Đột Quyết xâm lấn phương Bắc mà không tốn một mũi tên.
- Ch12: KẾT: Nắm đất Chùa Bạch Mã: Năm 700 "Triều đình vắng bóng người", bài học công lý giữa thời bạo quyền.

## 6. Ba tiêu đề đề xuất & Ý tưởng Thumbnail

- **Tiêu đề 1 (46 ký tự):** `ĐỊCH NHÂN KIỆT Ngoài Đời Thật: Án Trong Áo Bông`
- **Tiêu đề 2 (49 ký tự):** `ĐỊCH NHÂN KIỆT Ngoài Đời Thật: Hồ Sơ 17.000 Tù Nhân`
- **Tiêu đề 3 (52 ký tự):** `ĐỊCH NHÂN KIỆT Ngoài Đời Thật: Cứu Ngai Vàng Nhà Đường`
- **Thumbnail:** Chân dung cận cảnh Địch Nhân Kiệt (tranh cổ phục dựng độ phân giải cao, ánh mắt sắc sảo, phong thái đại thần), tương phản cao trên nền đen và sắc đỏ của pháp đình thời Đường.
- **Chữ lớn trên thumbnail (≤ 4 chữ):** `ÁN ÁO BÔNG` hoặc `17.000 TÙ NHÂN`.

## 7. Rủi ro

- **Dễ lẫn phim với sử:** Phim ảnh Từ Khắc và tiểu thuyết của Robert van Gulik đã in sâu vào đầu khán giả rằng Địch Nhân Kiệt đi trừ ma, đấu võ và giải mã ảo thuật. Kịch bản phải liên tục nhắc người nghe đây là hồ sơ tư pháp hành chính và chính trị cung đình có thật trong Đường thư.
- **Sử liệu mỏng về chi tiết kỹ thuật phá án:** Sử sách thời Đường ghi chép thiên về các phán quyết, số liệu tổng thể và các cuộc can gián lớn, không có biên bản khám nghiệm hiện trường chi tiết như thời Tống Từ sau này.
- **Rủi ro thiếu ảnh tự do:** Tổng số ảnh trực tiếp về Địch Nhân Kiệt dưới ngưỡng 40 ảnh. Cần chuẩn bị nhiều đồ họa timeline, bản đồ địa danh cổ và ảnh tư liệu bối cảnh thời Đường để lấp đầy sàn sản xuất.
