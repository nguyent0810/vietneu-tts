# GH-420: báo cáo bước 2–3, Long CL `cl-sarin-tokyo-1995` (15/11/2026)

Người làm: Claude Sonnet (subagent). Worktree `wt-plan-cl2/creator_v2`. Không commit, không push, không TTS, không render, không upload.

## 1. Bước 2: tư liệu ảnh (điểm dừng đã kiểm)

Lệnh: `research_long.py` với 4 bài Wikipedia (Tokyo subway sarin attack, Matsumoto incident, Aum Shinrikyo, Shoko Asahara) và 13 truy vấn Commons; `media_search.py search` (openverse, europeana) với 7 truy vấn. Ra `output/long/cl-sarin-tokyo-1995/research.json` (137 ảnh qua bộ lọc giấy phép và kích thước) cùng `sheet_0..3.jpg`, `ext_sheet_*.jpg`. Đã mở và soi cả bốn sheet.

Đếm sau lọc bằng mắt (không tính logo, cờ, ảnh lạc đề, ảnh thương vong):

| Nhóm | Số ảnh dùng được | Ghi chú |
|---|---|---|
| A. Tư liệu sự kiện và tổ chức: Lực lượng Phòng vệ khử độc (khoảng 10), PSIA kiểm tra cơ sở Aum (khoảng 6), Satyan và trụ sở cũ, biểu ngữ và biểu tình phản đối Aum, bia tưởng niệm gia đình Sakamoto, phòng hành chính Kamikuishiki, vài ảnh khác | khoảng 32 | Cốt lõi của kể chuyện |
| B. Sơ đồ tuyến (hai chuyến Marunouchi, hai chuyến Hibiya, Chiyoda, bản đồ tiếng Nhật), khác nhau thật | khoảng 5 | CC BY-SA, dùng làm đồ họa |
| C. Ảnh địa điểm: ga Kasumigaseki (Tokyo Metro), Tsukiji, Hibiya, Ueno, đoàn tàu Marunouchi và Hibiya, đường phố Matsumoto, vài ảnh lâu đài Matsumoto | khoảng 30 ảnh khác nhau (bản trùng nhau loại ra) | Chụp những năm 2010 đến 2020, chỉ làm b-roll địa điểm |
| Cộng A + B | khoảng 37 | Dưới 45 nếu chỉ tính ảnh sự kiện và sơ đồ |
| Cộng A + B + C | khoảng 67 | Đủ ngưỡng nếu tính cả b-roll địa điểm |

Loại bỏ: ảnh người bị thương hoặc nạn nhân (3 ảnh trong sheet 0), logo và cờ Aum, ga Tobu Kasumigaseki tỉnh Saitama (nhầm ga, khoảng 8 ảnh), tượng ếch Matsumoto, bóng đá, tàu thủy, ga Tsukiji của Nagoya, lâu đài Matsumoto trùng lặp. Không có ảnh tự do của ông Kono, của hiện trường Matsumoto 1994, chân dung Asahara. Ứng viên ngoài Commons tìm thêm: `Tokyo Subway Sarin Atack 1995-03-20` (ảnh mạnh nhất của plan, có trong openverse là X13), vài ảnh PSIA (X9, X11, X12) chưa tải.

Quyết định: tôi coi ảnh địa điểm chính xác của các ga và đoạn tuyến trong vụ là dùng được (chúng không lạc đề), nên A + B + C vượt 45 và tôi đi tiếp sang bước 3. **Lead cần biết đây là lằn ranh sát:** nếu chỉ tính ảnh sự kiện và sơ đồ thì dưới 45, và chương 1 đến 5 (Matsumoto, ông Kono, cảnh sát) gần như không có ảnh người hay hiện trường, chỉ có đường phố, sơ đồ, lâu đài và đồ họa. Cần đồ họa chung `minh_hoa_chung`, bản đồ, thẻ chữ và dòng thời gian. Nếu Lead muốn dừng theo luật chặt, bản kịch bản này vẫn dùng được cho đề tài khác cùng nguồn.

## 2. Nguồn: đã mở và chưa mở

Đã mở thật (WebFetch; công cụ trả về bản tóm tắt theo câu hỏi, không phải toàn văn): Wikipedia en Tokyo subway sarin attack (hai đoạn), Matsumoto incident, Aum Shinrikyo, Shoko Asahara, Yoshiyuki Kono (victim); Wikipedia ja 地下鉄サリン事件; Nippon.com (Takino Yusaku, 12/6/2025, điểm sách của ông Kakimi); Nippon.com (Medhurst, 27/6/2014); Al Jazeera 27/2/2004; EBSCO Research Starters. Chỉ qua đoạn trích tìm kiếm: AP 20/3/2025 (lời ông Kakimi, luật sư Nakamura, Aleph xin lỗi), Japan Times 21/6/2014 và 28/2/2004.

Không mở được hoặc chưa mở: Japan Times (HTTP 403), The Guardian, NHK, BBC, NYT, bản án Tòa án quận Tokyo 2004, báo cáo của cảnh sát Nhật, Underground, báo Yomiuri 1/1/1995 và Asahi 28/6 và 4/7/1994, Mainichi 27/7/2018, Kyodo 22/7/2002, bài Yomiuri và Asahi 6/8/2008. **Lời đọc nói ở CH07 "chưa đọc được bản gốc" cho Yomiuri và ở CH01 liệt kê nguồn đúng với những gì đã mở.** Chưa có bản án hay báo lớn đã mở toàn văn: đây là điểm yếu nguồn, Nippon.com 2025 (dựa trên sách của chính cựu cục trưởng cảnh sát) và hai bản tin 2004 và 2014 là nguồn mạnh nhất có.

## 3. Mâu thuẫn nguồn và cách kịch bản xử lý

- **Số người chết:** 14 (W1, lead), 12 (tòa án; W1 và EBSCO: được công nhận đến 2008), 13 (chính quyền theo W6). Kịch bản nói cả ba (CH00 "từ 12 đến 14", CH10 giải thích từng cách đếm, kể cả người mất 10/3/2020).
- **Số bị thương Tokyo:** khoảng 1.000 (W1), khoảng 5.500 (Al Jazeera), khoảng 6.300 (W6). Kịch bản nêu 1.000 và 6.300, không chọn.
- **Số bị thương Matsumoto:** 144 (W1), 274 được điều trị, hơn 500 (infobox và W3), 58 nhập viện + 253 ngoại trú. Kịch bản nêu từ 144 đến hơn 500, cùng hai cách chia.
- **Khám xét 22/3:** trang en nói đã định từ trước nhưng không dẫn nguồn; trang ja ghi 17/3 là ngày chốt và có yêu cầu hỗ trợ Cục Phòng vệ; Takino/Kakimi ghi 22/3 được chọn sau vụ Kariya (tháng 2). Kịch bản nêu các bản và chỉ khẳng định điều chắc chắn: ngày khám xét là 22/3. Thêm hai cách hiểu "đánh lạc hướng" (Kakimi) và "không thể lường trước" (cảnh sát không nêu tên, qua Takino).
- **Lời xin lỗi ông Kono:** W2 (cảnh sát trưởng Matsumoto xin lỗi, không ngày, không lời), W5 (ông Nonaka, người đứng đầu Ủy ban An ninh Công cộng Quốc gia, và truyền thông; Nagano không xin lỗi trực tiếp đến 2002, dẫn Kyodo), N2 (nhiều báo xin lỗi, cảnh sát Nagano "unrepentant"). CH13 nêu cả ba, nói "tôi không chọn".
- **Năm thành lập nhóm yoga:** 1984 (W3) và 1987 (W4); nêu cả hai ở CH06.
- **Ngày vụ mất tích Sakamoto:** 10/1989 (N1) và 11/1989 (W3, W4); kịch bản chỉ nói "cuối năm 1989" ở cả CH05 và CH06.
- **Số người chết Matsumoto:** N2 ghi bảy người chết, W2 ghi tám (bảy người ngay sau đó, bà Sumiko mất 2008). Kịch bản nói bảy và thêm người thứ tám.
- **Thời gian xử Asahara:** tám năm (Al Jazeera), hơn bảy năm (W4). Nêu cả hai ở CH12.
- **Giờ các chuyến tàu:** trang en ghi khởi hành 07:39 đến 07:59, trang ja ghi khoảng 8 giờ sáng. Kịch bản nói "khoảng 8 giờ".
- **Một số chi tiết chỉ có trên Wikipedia hoặc không dẫn nguồn:** hóa chất 20 loại trong nhà ông Kono (W5), thư nặc danh "definitely an experiment" (W2), 140.000 chữ ký (W2 có dẫn nhưng chưa mở), Nonaka xin lỗi (W5), St. Luke's (tóm tắt). Người duyệt kiểm lại bằng bước story review.

## 4. Khác plan (cần Lead biết)

- **Cold open không còn câu "5 gói báo bị chọc thủng bằng đầu ô"** của plan mục 2: theo luật không mô tả cách tấn công, bản này nói "khí sarin bắt đầu lan ra trên năm chuyến tàu". Hình slam "5 CHUYẾN TÀU. 5 GÓI BÁO." của plan nên đổi thành "5 CHUYẾN TÀU." thôi.
- **Không có thời điểm 07:39 đến 08:35** từng chuyến như plan mục 4 Ch10: hai trang không thống nhất, kịch bản chỉ giữ các mốc có nguồn (8:10, 8:35, 8:30, 9:27, 10:30, 12:50).
- **Không nêu tên** người bị thương, người thi hành, nhân viên nhà ga, hay nạn nhân Matsumoto ngoài ông bà Kono. Có nêu tên người công khai trong vai trò công vụ hoặc phát ngôn: Kakimi, Takino, Nakamura, Nagaoka (lời trích đã đăng báo), Yanagisawa, Nonaka, thẩm phán Ogawa, học giả Shimada, nhà sử học Tsuneishi. Ông Nagaoka là người bị Aum nhắm đến và còn sống: Lead cân nhắc có giữ lời trích không.
- **Tên người còn sống ghi trong lời đọc:** ông Kono (nhân vật chính, đã có nhiều bài viết công khai), ông Kakimi, luật sư Nakamura. Không ước đoán cảm xúc: CH11 và CH13 có câu "tôi không dám đoán" để chặn.
- **Ba tiêu đề:** dùng phương án 1 của plan (56 ký tự). Bằng chứng "vợ hôn mê, chồng bị nghi" có (W5, N2); "hạ độc" trong tiêu đề là điều ông bị nghi, không phải điều ông làm: Lead xem lại chữ này.

## 5. Kịch bản

`data/long/cl-sarin-tokyo-1995/script.md`: 14 chương CH00 đến CH13, 389 câu, **5.894 âm tiết** (khoảng 27 phút theo 215 âm tiết/phút), câu dài nhất 32 âm tiết. Cold open CH00 khoảng 160 âm tiết (khoảng 40 giây): giờ thứ Hai, năm chuyến tàu, câu hỏi hậu quả ở câu thứ 5, người đàn ông ở Matsumoto trước giây 15, lời hứa của Long ở câu cuối. Lộ trình CH01 theo dạng "tấm bảng ghi nợ ba khoản", đi sau cold open. Có "bạn", có ‖, ghi chú kiểm chứng và bảng phiên âm cuối file (24 tên). Có hai lời trích dịch (thẩm phán Ogawa, ông Nagaoka), nguyên văn và URL ở factcheck §12.

Cấu trúc: CH00 cold open; CH01 lộ trình; CH02 đêm Matsumoto; CH03 ông Kono; CH04 hóa chất trong nhà và bài báo Asahi; CH05 ba tỉnh và bản tin Aum; CH06 Aum; CH07 mẫu đất, Yomiuri; CH08 vụ Kariya, ngày khám xét, hai cách hiểu, tóm tắt mốc; CH09 sáng 20/3, 8:10 "vụ nổ"; CH10 cấp cứu, bài học Matsumoto, ba cách đếm; CH11 khám xét 22/3 và bắt 16/5, lời ông Kono; CH12 phán quyết; CH13 kết.

## 6. Cổng đã chạy

- `python motion/long/script_lines.py cl-sarin-tokyo-1995`: qua (ghi `ch00..ch13.json`). Cảnh báo còn lại: `NHAY_MOC` ở CH04, CH06, CH10, CH12 (mốc lùi về tiểu sử Asahara 1955, 1981 và các mốc sau 2008 là cố ý), `SOURCE_DENSITY` ở CH02, CH10, CH11, CH12 (nhắc "trang bách khoa" hơn một lần mỗi chương: nên bớt khi review), `NHIP_30S` ở hai cửa sổ 660 đến 690 giây và 1110 đến 1140 giây dù đã đặt dấu beat gần đó (ước lượng thời gian của script_lines có thể lệch; kiểm lại sau TTS).
- `craft.audio_problems(...)`: `[]`.
- `factcheck_lint.lint("cl-sarin-tokyo-1995")`: `[]`.

## 7. Việc còn lại cho Lead

1. Duyệt lằn ranh ảnh ở mục 1.
2. Chạy `scripts/long_story_review.py cl-sarin-tokyo-1995` (model thứ hai) và áp bản viết lại; đặc biệt kiểm CH05, CH08, CH13 (các nhận định "người viết điểm sách" và "lời xin lỗi").
3. Bớt cụm "trang bách khoa" ở CH02, CH10, CH11, CH12 (đổi thành "theo một số nguồn" hoặc "theo hồ sơ").
4. Tải thêm ảnh X13, X9, X11, X12 bằng `media_search.py get` khi sang bước cảnh.
5. Chưa có bước cảnh (`gen_scenes.py`), chưa có `spec.json`: chưa dựng gì.
