# GH-395: báo cáo bước 2 và 3, Long CL "Địch Nhân Kiệt ngoài đời thật" (topic `cl-dich-nhan-kiet`)

Ngày 14/11/2026. Làm trong worktree `wt-dnk/creator_v2`. Không commit, không upload, không TTS, không render.

## Bước 2: tư liệu ảnh

- `research_long.py` gom 343 ảnh Commons tự do (PD, CC0, CC BY, CC BY-SA) từ 22 bài Wikipedia và 15 truy vấn Commons. Kết quả ở `output/long/cl-dich-nhan-kiet/research.json` và `sheet_0..9.jpg`.
- Lọc rác: 201 ảnh dùng được. Gộp các loạt gần trùng (Qianling 16 tấm, Longmen 14, bia vô tự 8, phù điêu Chiêu Lăng 6, tượng gốm 5) giữ tối đa 4 tấm mỗi loạt: 172 ảnh khác nhau. Danh sách ở `output/long/cl-dich-nhan-kiet/selected.json` (khóa `keep` và `keep_conservative`).
- Giấy phép trong 201 ảnh: 62 PD, 68 CC0, 62 CC BY-SA, 9 CC BY. Không ảnh nào NC/ND/fair use.
- Đã loại: ảnh hiện đại (ga tàu, cầu, thư viện Wenhui, đại sứ Burns), lăng Chiêu Lăng của nhà Thanh (Abahai, trùng tên Zhaoling), bản đồ Hán, Nam Đường, tranh Tống/Nguyên/Thanh, ảnh Seljuk, Mông Cổ, thùng hương và tượng Phật chùa Bạch Mã gần như lặp.
- Ảnh trực tiếp về nhân vật: 4 chân dung (PD): `Di Renjie.jpg`, `狄仁杰.jpg`, `Portraits of Famous Men - Di Renjie` (2610x3792) và bản thứ hai của bộ tranh này; 3 ảnh mộ (CC BY-SA): bia ở chùa Bạch Mã (2000x1334), `2017-02-25 Tomb of Di Renjie.jpg`, `20251018 Tomb of Di Renjie.jpg`. Có thêm chân dung Diêu Sùng (`Portraits of Famous Men - Yao Chong`, PD). Không tìm được ảnh Trương Giản Chi, Lai Tuấn Thần, Võ Tắc Thiên bản tranh thời ấy tốt; Võ Tắc Thiên có tranh Thanh (`武曌像`, `Wuhou`), tượng và bia vô tự ở Càn Lăng.
- Phần còn lại là bối cảnh: Võ Tắc Thiên, Càn Lăng (lăng Cao Tông và bà), Chiêu Lăng (cây bách!), Lạc Dương, Trường An, Long Môn, Bạch Mã Tự, bản đồ Đường 700 và 669, tượng gốm quan Đường, tranh cung đình, Đột Quyết (bản đồ, tranh tường), mô hình Trường An.
- Đủ trên 50: 201 sau lọc, 172 sau gộp. Nhưng đa số là cảnh bối cảnh, ảnh có mặt nhân vật rất ít (7). Lead cần biết khi soạn cảnh: nhiều cảnh phải dùng tượng gốm quan, bản đồ, bia, thư pháp.
- Giới hạn của việc lọc: tôi mở trực quan sheet 0 và sheet 8; các sheet còn lại lọc theo tên file và giấy phép. Nên soi nhanh các sheet 1 đến 7, 9 khi soạn cảnh (hồ sơ chọn nằm trong `selected.json`).

## Bước 3: góc kể và phát hiện chính

Góc kể (khác Bao Thanh Thiên và khác "bốn mốc" của Hoàng Kim Vinh): khoảng cách giữa thám tử trong phim và người trong hồ sơ. Mỗi chặng đời hỏi trước "nếu là phim, ông làm gì?", rồi đọc xem sử ghi gì. Lộ trình dạng "hai cuốn sổ đặt cạnh nhau".

Phát hiện chính (đã đọc toàn văn Cựu Đường thư q.89, Tân Đường thư q.115, Tư trị thông giám q.202 đến 207 trên Wikisource tiếng Trung, và Wikipedia en/zh):
- Hai bộ Đường thư không có một vụ án ma quái nào ở phần truyện Địch Nhân Kiệt. Thứ gần nhất là đền Đố Nữ (ông gạt chuyện sấm gió) và 1.700 miếu bị phá. Hình tượng thám tử đến từ tiểu thuyết đời Thanh và van Gulik.
- Nhiều cảnh nổi nhất của ông là ngăn một hình phạt: cây bách Chiêu Lăng (676), Dự Châu (688), xá Hà Bắc (698), hai tướng Khitan, pho tượng Phật (700), và lời nhận tội để khỏi chết dưới roi. Nhưng ông cũng đòi trị Vương Bản Lập và phá 1.700 miếu; lời đọc nói rõ không gọi ông là người "chỉ xin tha".
- Cảnh áo bông: sử chép ông xé lụa ở đầu chăn, viết oan trạng, nhét vào áo bông, nói "trời đang nóng, xin cho người nhà tháo bông". Con trai Quang Viễn mang thư vào cung. Cậu bé con của một người đã bị xử tử (Lạc Tư Hối) cũng dâng thư. Võ Tắc Thiên bắt được tờ "tạ tội chết" giả. Không nguồn nào nói viết bằng máu.
- Ba cách đếm khác nhau ở Dự Châu (600 đến 700 gia đình, 5.000 người bị tịch thu, 2.000 người bị án tử). Giấc mơ của Võ Tắc Thiên: Tư trị thông giám chép con vẹt gãy cánh, Tân Đường thư chép ván song lục. Năm mất: 700 theo sử, 704 theo một giả thuyết (zh.wikipedia). Mộ ở chùa Bạch Mã: en nói ở đó, zh nói vị trí thật còn tranh cãi.

## Chương và âm tiết

14 chương CH00 đến CH13, 413 câu, 5.662 âm tiết (khoảng 25 phút theo script_lines). Đạt mức 5.500 đến 7.000 nhưng ở sát cận dưới; nếu Lead muốn dày hơn, có thể mở rộng CH03 và CH08 bằng chi tiết đã có trong factcheck. Mọi câu đều ≤ 32 âm tiết. Cold open 180 âm tiết (khoảng 45 giây), có câu hỏi ở câu thứ 8.

## Ba cổng

1. `python motion/long/script_lines.py cl-dich-nhan-kiet`: chạy xong, sinh `ch00.json` đến `ch13.json`, không lỗi, không cảnh báo nhịp 30 giây, không cảnh báo mật độ nguồn hay lời kể meta.
2. `craft.audio_problems(script_lines.parse(text))`: `[]`.
3. `factcheck_lint.lint('cl-dich-nhan-kiet')`: `[]` (36 câu TRÍCH DỊCH đều có dòng nguyên văn kèm URL; 38 dòng trong factcheck).

## Đã bỏ hoặc hạ cấp so với plan

- Bỏ "62 tuổi", "mùa xuân 692", "lồng đinh Định bách mạch", "Tiêu phủ phán quan", "Đại thẩm phán kiêm tể tướng chính trị thượng thừa": không có nguồn.
- Sửa: "xé áo bông, thư máu, trời sang xuân" thành lụa ở chăn, chữ "nóng", máu là do đập đầu vào cột. "Đẩy lùi Đột Quyết không tốn một mũi tên" thành "đuổi 10 vạn quân không kịp, rồi xin xá Hà Bắc". "Dự Châu cứu 2.000 người" thành ba cách đếm.
- Hạ cấp: "mạng lưới ngầm Thần Long 705": sử chỉ chép ông tiến cử Trương Giản Chi, Diêu Nguyên Sùng, Hoàn Ngạn Phạm, Kính Huy; chính biến 705 xảy ra khoảng năm năm sau khi ông mất, không nguồn nào nói ông dự mưu.
- Bỏ hai URL 404 trong plan. Đưa dị bản mộ vào lời đọc.
- Không dùng: "Địch công án" năm 1890 hay thế kỷ 18 (W1 và W4 lệch nhau, lời đọc chỉ nói "đời Thanh"); bài của Benedetti (chỉ biết qua chú thích).

## Rủi ro cần Lead quyết

1. Lời trích dịch từ nguyên văn Hán: tôi tự dịch, 36 câu. Cần Lead (hoặc agy Gemini) rà bản dịch tiếng Việt.
2. Nhiều chi tiết chỉ có ở hai bộ Đường thư hoặc chỉ ở Tân Đường thư (đám mây, cảnh màn trướng, Kỳ Châu, lý lẽ năm vạn người): lời đọc đã nói "hai bộ Đường thư chép" hoặc "Tân Đường thư chép". Nếu muốn an toàn tuyệt đối thì bỏ.
3. Lời đọc dùng "Wikipedia" cho vài chi tiết chỉ có ở bản en/zh (Lai Tuấn Thần, hạn hán Bành Trạch, năm mất 704): không đối chiếu được với sử, đã gắn nhãn BÁCH KHOA.
4. Phim và tiểu thuyết chỉ nhắc ở CH01 và CH13; không gán nhân vật phim nào cho người thật khác.
5. Số âm tiết sát cận dưới (5.662). Sau TTS khoảng 25 phút.
6. Chưa chạy `long_story_review.py` (ngoài phạm vi ticket).
7. Ba cảnh dễ dựng sai: bảng số Dự Châu (ba cách đếm, không được rút gọn thành một con số), tờ lụa (không vẽ máu), và nhãn năm mất 700/704.

## File đã ghi

- `data/long/cl-dich-nhan-kiet/factcheck.md`
- `data/long/cl-dich-nhan-kiet/script.md`
- `data/long/cl-dich-nhan-kiet/ch00.json` đến `ch13.json` (do script_lines.py sinh)
- `output/long/cl-dich-nhan-kiet/research.json`, `sheet_0.jpg` đến `sheet_9.jpg`, `selected.json`
- `docs/pm/tickets/GH-395-script-report.md` (file này)
