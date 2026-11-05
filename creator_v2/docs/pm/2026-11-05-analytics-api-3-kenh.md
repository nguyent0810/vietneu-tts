# Số liệu YouTube Analytics API cho MIM, CK, CL (issue #183)

Ngày lấy: 05/11/2026. Kỳ chính 28 ngày 07/10–03/11, kỳ 7 ngày 29/10–04/11, kỳ 365 ngày 05/11/2025–04/11/2026. Chỉ đọc API. Dữ liệu thô: `data/analytics/<KÊNH>/183/` (gitignore). Script: `scripts/analytics_pull_183.py` (kéo), `scripts/analytics_analyze_183.py` (bảng).

**CL: chưa có số liệu.** Máy này không có file credential của CL (`factory/channels.py` trỏ `hinh_su.json`, không tồn tại; các báo cáo 22/10 đã ghi điều này). Tôi không tìm credential ở chỗ khác. Mọi mục về CL dưới đây chỉ dựa vào số Studio trong #177, đánh dấu rõ. Khi có credential: `python scripts/analytics_pull_183.py --channel CL` rồi `python scripts/analytics_analyze_183.py --channel CL` (CL không có `upload_log`, nên giờ đăng lấy từ `publishedAt`, script đã dùng nguồn này sẵn).

## 1. Metric lấy được và không lấy được

| Metric | Kết quả |
|---|---|
| views, estimatedMinutesWatched, averageViewDuration, averageViewPercentage, subscribersGained, subscribersLost | Có, theo video (không giới hạn 50 dòng: MIM 119, CK ~ toàn bộ video có view) và theo kênh |
| engagedViews | Có (video và kênh). Đây là cột "ở lại xem"; tỷ lệ ở lại = engagedViews / views |
| creatorContentType (shorts / videoOnDemand) | Có. Dùng tách Long và Short chính xác ở mức kênh |
| video x insightTrafficSourceType | **API từ chối khi gộp hai chiều (400).** Làm bằng cách hỏi từng video với `filters=video==ID`: đủ cho mọi video công khai. |
| impressions, CTR (`videoThumbnailImpressions`, `...ClickRate`) | **Không lấy được**: 400 "query is not supported". Không suy ngược. CTR và impressions chỉ có ở Studio. |
| Shown in feed / lướt qua (`shownInFeed`, `shortsFeedImpressions`) | **Không lấy được**: "Unknown identifier". Chỉ có Studio. Thay thế duy nhất: engagedViews/views (xem dưới). |
| hour (giờ trong ngày) | **Không có.** Chỉ có `day`. |
| Video x day | Có (từng video). Ngày tính theo giờ Thái Bình Dương. |

Hệ quả cho #183: bốn mục của issue chỉ làm được hai (Short đủ dòng, bảng video x nguồn). CSV gốc, Shown in feed và CTR vẫn phải xuất tay từ Studio nếu cần. Báo cáo này không điền thay chúng.

## 2. Bảng tổng và đối chiếu Studio

| | MIM | CK | CL |
|---|--:|--:|--:|
| Sub hiện tại (API channels.list) | 62 | 42 | n/a |
| Sub Earn trong Studio | 62 | 42 | 573 |
| Giờ xem 365 ngày, chỉ Long (videoOnDemand), tới 30/10 | 57,1 | 17,7 | n/a |
| Giờ xem Earn (Studio) | 53 | 17 | 965 |
| Giờ xem 365 ngày, chỉ Long, tới 03/11 (ngày cuối API có) | 67,3 | 21,5 | n/a |
| 28 ngày Long: views / giờ / AVD / sub | 1.545 / 63,3 / 4:34 / 8 | 487 / 20,9 / 4:31 / 2 | Studio: 8.287 / 503 / 10:09 / 11 |
| 28 ngày Short: views / giờ / sub | 82.686 / 137,3 / 44 | 41.703 / 97,2 / 28 | Studio: 84.342 / – / 90 (50 Short đầu) |
| 7 ngày (29/10–04/11): Long views / Short views | 456 / 14.292 | 185 / 2.810 | n/a |
| Tỷ lệ sub trên 1.000 view: Long / Short | 5,2 / 0,53 | 4,1 / 0,67 | n/a |
| Tỷ lệ ở lại (engagedViews/views), cả kênh 28 ngày | 30,1% | 35,1% | n/a |

Đối chiếu:
- Sub khớp tuyệt đối (62, 42).
- Giờ Earn khớp trong khoảng 4 giờ: CK 17,7 so với 17; MIM 57,1 so với 53 (lệch 4,1 giờ, chưa giải thích được. Khả năng: Earn bỏ phần xem của video không công khai tại thời điểm tính hoặc tính theo cửa sổ khác; không kiểm được).
- Con số "giờ xem 365 ngày" thô của kênh (MIM 12.660 phút = 211 giờ, CK 119 giờ) không dùng để so với Earn: gồm cả Short (MIM 142 giờ, CK 97 giờ). Earn chỉ tính Long công khai.
- Long 28 ngày API so với Studio: MIM 63,3 so với 66,7 giờ; CK 20,9 so với 22,2 giờ; views 1.545 so với 1.626 (MIM), 487 so với 507 (CK). API thấp hơn 4–6%; chênh do ngày đầu/cuối cửa sổ tính theo giờ Thái Bình Dương và độ trễ dữ liệu (API mới có tới 02/11 cho vài chỉ số).
- Short 28 ngày: API MIM 82.686 so với "84.566 (50 Short đầu)" trong #177. Bản Studio còn cao hơn API dù chỉ 50 dòng, nên cột Short trong gói Studio gồm cả lượt xem ngoài định nghĩa videoOnDemand/shorts của API (khả năng là live hoặc cách quy ngày). Không giải thích hết.
- CL: không đối chiếu được (không có credential).

## 3. MIM

### Long (13 video công khai, tất cả đăng 20:00 VN), xếp theo giờ xem 28 ngày

| # | Video | Views | Giờ | AVD | AVP | Nguồn kéo giờ xem |
|--|--|--:|--:|--|--:|--|
| 1 | AI Giả Giọng Người Thân Để Lừa Tiền | 429 | 12,9 | 4:24 | 34% | Đề xuất 4,5 h; Link ngoài 4,3 h; Subscriber 3,6 h |
| 2 | Luật Sư Nộp 6 Vụ Án Do ChatGPT Bịa | 129 | 10,3 | 5:51 | 44% | Link ngoài 5,6 h; Đề xuất 4,1 h |
| 3 | AI Có Cướp Việc Của Bạn? 200 Năm Trước... | 160 | 10,3 | 5:21 | 38% | Đề xuất 6,2 h; Link ngoài 2,7 h |
| 4 | Thuật Toán Đề Xuất: TikTok Và YouTube | 266 | 6,1 | 2:48 | 21% | Đề xuất 5,1 h |
| 5 | Năm Ván Cờ Thay Đổi AI (AlphaGo) | 70 | 5,7 | 8:23 | 42% | Đề xuất 3,5 h; Link ngoài 1,0 h |
| 6 | AI Đã "Chết" Hai Lần | 178 | 4,5 | 3:40 | 28% | Subscriber 2,5 h |
| 7 | "Tôi Không Phải Người Máy" | 165 | 4,3 | 3:35 | 40% | Đề xuất 2,9 h |
| 8 | Sholes 1873: Bàn Phím QWERTY | 46 | 4,0 | 6:07 | 69% | Link ngoài 3,5 h |
| 9 | Mã QR | 50 | 2,8 | 3:57 | 48% | Đề xuất 2,1 h |
| 10 | Deep Blue Đấu Kasparov 1997 | 21 | 1,1 | 5:46 | 31% | Đề xuất 1,0 h |
| 11 | AlexNet 2012 | 18 | 0,9 | 3:49 | 30% | Đề xuất 0,5 h |
| 12 | Flappy Bird | 13 | 0,2 | 1:21 | 20% | Đề xuất |
| 13 | Watson Jeopardy! (04/11) | 0 | 0 | | | chưa đủ tuổi |

Bảng đầy đủ kèm cột 365 ngày và % view theo nguồn: chạy `analytics_analyze_183.py --channel MIM --section long`.

Nguồn (tổng 1.545 view Long): Subscriber 786 view nhưng chỉ 9,9 giờ (AVD ngắn: người đã đăng ký bấm xem rồi bỏ); Đề xuất (RELATED_VIDEO) 543 view, 31,4 giờ; Link ngoài (EXT_URL) chỉ 99 view nhưng 18,1 giờ (AVD dài nhất, đúng ghi nhận 11:03 trong #177); Tìm kiếm 54 view, 0,9 giờ. Không video Long nào nhận lượt xem từ nguồn SHORTS.

Nhận xét:
- Top 3 là: lừa đảo bằng AI (có hành động bảo vệ cụ thể), vụ việc có thật kèm số cụ thể (6 vụ án), nỗi sợ mất việc kèm đối chiếu lịch sử. Khớp công thức lừa đảo/AI/việc làm trong #177.
- Cuối bảng là đề tài "lịch sử công nghệ" tên riêng + năm (AlexNet 2012, Deep Blue 1997, Flappy Bird): 13–21 view, 0,2–1,1 giờ. Ngoại lệ: AlphaGo (5,7 giờ, AVD 8:23) và Sholes (AVP 69%), nghĩa là chủ đề lịch sử vẫn giữ người xem khi đã vào được, vấn đề là vào không được (view thấp).
- Video 12/10 sống bằng Subscriber (80% view): không có sức kéo ngoài.
- "Thuật Toán Đề Xuất" được đẩy nhiều (266 view) nhưng AVP 21%: tiêu đề kéo được nhưng nội dung/độ mở không giữ.

### Short (110 công khai, 100 có view trong 28 ngày)

- Views 28 ngày: **median 832, p25 502, p75 1.034, max 1.420**. Phân phối bị chặn rất sát ở 1.0–1.4k: không có Short nào vượt 1.420, không có "hit". Đây là trần theo khối, không phải sự khác biệt giữa các Short.
- Tỷ lệ ở lại (video >= 100 view, n=97): median 25,5% (p25 19,1%, p75 34,4%). Ở lại cao nhất: Nước đi thứ 78 AlphaGo 58%, trò đoán chữ 1951 55%, chatbot 1966 45%, nơ-ron 1958 44%.
- Sub: 42 trên 78k view (0,54 mỗi 1.000 view). Cao nhất: "Sau khi Flappy Bird bị gỡ: hơn 60 trò nhái" 4 sub, các Short Turing, ELIZA 1966, AlphaGo nước 37 mỗi cái 2 sub. Sub đến từ Short có câu chuyện cụ thể có hậu quả, không phải Short có view cao nhất (top view 1.420 chỉ 1 sub).
- Theo tuần đăng (views 7 ngày đầu, median): 12/10 tuần 1.204 (n=30), 19/10 tuần 748 (n=29), 26/10 tuần 762 (n=33, mới 15 đủ 7 ngày). Rớt 38% từ tuần 12/10 sang 19/10 khi số Short/ngày tăng; không phục hồi.
- Tỷ lệ Short dẫn sang Long: **không đo được trực tiếp**. API không có chiều "video nguồn". Gián tiếp: không Long nào nhận traffic nguồn SHORTS, và cả kênh chỉ có 0,5 sub/1.000 view Short so với 5,2 cho Long. Số 786 view Subscriber của Long cho thấy người đã đăng ký là nguồn chính, mà người đăng ký chỉ 62.

## 4. CK

### Long (12 công khai, tất cả 20:00 VN)

| # | Video | Views | Giờ | AVD | AVP | Nguồn |
|--|--|--:|--:|--|--:|--|
| 1 | Trả Góp 19 Triệu Hay Thuê 6 Triệu | 132 | 5,7 | 5:18 | 39% | Đề xuất 5,0 h |
| 2 | Ngày VN-Index Mất 115 Điểm | 80 | 5,1 | 6:23 | 53% | Link ngoài 4,4 h |
| 3 | Xếp Hàng Mua Vàng Có Phải Là Đỉnh? | 77 | 2,8 | 4:00 | 32% | Đề xuất 1,4 h |
| 4 | Nợ Thẻ Tín Dụng: Chỉ Trả Tối Thiểu | 23 | 1,6 | 4:55 | 61% | Link ngoài 0,8 h; Đề xuất 0,6 h |
| 5 | VN-Index Đứng Yên — Sao Tài Khoản Vẫn Có Lãi | 13 | 1,1 | 5:49 | 47% | Link ngoài 0,8 h |
| 6 | Trả Góp 0% | 18 | 0,9 | 3:39 | 45% | Đề xuất |
| 7 | Hoá Đơn Viện 15 Triệu | 21 | 0,7 | 3:09 | 39% | |
| 8 | Lãi Kép | 12 | 0,7 | 4:12 | 56% | |
| 9 | Mua Xe 700 Triệu | 8 | 0,4 | 3:44 | 42% | |
| 10 | Năm 2026: Chứng Khoán, Vàng, Coin, Nhà Đất Đều Đỏ | 9 | 0,1 | 1:02 | 10% | |
| 11 | Một Cây Nến Đỏ Kể Gì? | 11 | 0,1 | 0:42 | 5% | |
| 12 | Cổ Tức 10% (04/11) | 0 | | | | chưa đủ tuổi |

Nguồn (404 view Long có số nguồn): Đề xuất 170 view, 9,1 giờ; Subscriber 159 view, 1,8 giờ; Link ngoài 45 view, 7,4 giờ. Không có view từ SHORTS.
Nhận xét: hai bài đầu mang quyết định tiền cụ thể (trả góp, một ngày giảm 115 điểm) đúng như #177. Hai bài cuối (bài tổng quan năm, nến cho người mới) AVD 0:42–1:02, AVP 5–10%: người xem rời trong một phút.

### Short (62 công khai, 56 có view trong 28 ngày)

- Views 28 ngày: **median 316, p25 141, p75 1.040, max 3.210**. Phân phối hai cụm: một cụm 100–400 và một cụm 950–1.270; không giống MIM.
- Ở lại (video >= 100 view, n=47): median 27,9% (p25 22,7%, p75 34,4%).
- Top view: lạm phát 3 tỷ sau 30 năm 3.210 (ở lại 49%); bảo hiểm tiền gửi 350 triệu 2.271 (AVP 110%, tức xem lặp); gửi tiết kiệm sức mua đứng yên 1.448 (3 sub); DCA 8 năm VN-Index 1.273; bảng xếp hạng 2025/2026 1.268.
- Sub: 28 trên 41,7k view (0,67 mỗi 1.000). Cao nhất: "Khối ngoại bán ròng 9 tháng" 3 sub; "gửi tiết kiệm sức mua đứng yên" 3 sub.

### Số liệu cho luật dừng đợt 5 Short/ngày (29/10–11/11)

Mốc so sánh: median view mỗi Short, tính theo views trọn đời tới 05/11 của các Short công khai, nhóm theo ngày đăng (giờ VN). Số của tôi cho 20–26/10 là **271 (n=13, p25 168, p75 575)**, không phải 322: có thể bạn dùng định nghĩa/mẫu khác (sổ lịch có thể tính cả video đã gỡ); hai bảng dưới dùng cùng một định nghĩa nên so sánh với nhau được.

| Tuần đăng | n công khai | median | p25 | p75 |
|--|--:|--:|--:|--:|
| 13–19/10 | 28 | 997 | 150 | 1.202 |
| 20–26/10 (mốc) | 13 | 271 | 168 | 575 |
| 27/10–02/11 | 11 | 308 | 90 | 774 |
| 29/10–04/11 (tuần thử 1, 14 Short đã công khai) | 14 | 248 | 79 | 819 |
| trong đó 29–31/10 | 3 | 942 | 485 | 972 |
| trong đó 01–04/11 | 11 | 206 | 90 | 492 |

Đọc đúng:
- Tuần thử 1 mới có 14 Short công khai; 17 Short CK còn non-public (đã hẹn lịch) nên chưa thể có "5/ngày" thực. Trên 7 ngày chỉ khoảng 2/ngày lên sóng.
- 11 Short đăng 01–04/11 còn chưa đủ 7 ngày tuổi (view còn tăng); median 206 là cận dưới. Chưa nên kết luận dưới mốc.
- Theo tuần 7 ngày đầu (xem bảng `--section tuan`): 19/10 tuần 254, 26/10 tuần 309, 02/11 tuần 102 (n=4, chưa đủ tuổi).
- Gợi ý mốc dừng: so sánh lại ngày 12/11 với median trọn đời của Short đăng 29/10–11/11, chỉ tính Short đủ 7 ngày tuổi. Nếu nhỏ hơn 271 (hoặc 322 nếu bạn giữ định nghĩa cũ) mà số Short/ngày thực lên sóng đã đạt gần 5, thì luật dừng kích hoạt. Hiện tại luật chưa đánh giá được vì mẫu thiếu.

## 5. CL

Không có dữ liệu API (không có credential). Số trong #177 (Studio): Browse 81% lượt xem Long, CTR 4,5%, 503 giờ/28 ngày, 70% giờ xem đến từ hai bài "Ngoài Đời Thật" (Khun Sa 215 giờ, Đỗ Nguyệt Sanh 134 giờ), "Bí Ẩn..." gần bằng 0. Chưa kiểm được bằng API; không có giờ đăng Long CL, không có bảng nguồn, không tách Long/Short.

## 6. Giờ đăng tốt nhất

Phương pháp: views 3 ngày đầu của từng video, đăng 01–31/10, lấy từ chiều `day` (ngày Thái Bình Dương của ngày đăng và hai ngày sau, nên khoảng 48–72 giờ). Giờ đăng theo VN từ `publishedAt` (trùng `publish_at` trong `upload_log`).

**Long (MIM, CK): không có dữ liệu so sánh.** Mọi Long đều đăng đúng 20:00 VN (MIM n=10, CK n=9 trong tháng 10). Không có biến thiên nên không kết luận được giờ nào tốt hơn. Khuyến nghị: giữ 20:00 làm mặc định và thử một đợt 3 Long ở 12:00 hoặc 12:00–13:00 để có so sánh; chọn theo số views 72 giờ. Với CL không làm được (không có số).

**Short: giờ đăng gần như không ảnh hưởng.** Tôi chuẩn hóa views 3 ngày đầu so với median của cùng ngày đăng (để loại hiệu ứng "tuần yếu"):

| Kênh | Khung giờ VN | n | tỷ số so với median cùng ngày |
|---|---|--:|--:|
| MIM | 06h | 16 | 1,05 |
| MIM | 11h | 16 | 0,93 |
| MIM | 17h | 15 | 1,00 |
| MIM | 19h | 17 | **1,13** |
| MIM | 21h | 16 | 0,97 |
| CK | 07h | 6 | 1,00 |
| CK | 12h | 13 | 0,94 |
| CK | 17h | 7 | 1,06 |
| CK | 19h | 11 | 1,00 |
| CK | 22h | 5 | 1,06 |

Mọi tỷ số nằm trong 0,93–1,13, tức không có slot nào hơn rõ. Khuyến nghị thực dụng:
- MIM Short: ưu tiên 19:00 VN (tỷ số 1,13, median 3 ngày 999, n=21), tránh 11:00 (0,93, median 610, n=16). Chênh nhỏ, đừng dồn.
- CK Short: 17:00–22:00 VN (tỷ số 1,06, median 3 ngày 954–962), tránh 07:00 và 12:00 (median thô 166 và 471 nhưng sau chuẩn hóa chỉ còn 1,00 và 0,94: thấp thô là do hai slot này rơi vào tuần yếu).
- Chọn slot trước hết không phải biến số quyết định: yếu tố lớn hơn là tuần đăng (MIM tuần 12/10 median 1.204 so với 748 tuần sau).

Giới hạn: API không có giờ trong ngày, nên không đo được "ở slot nào khán giả hoạt động". `dimensions=day` cho video x ngày; dữ liệu thô ở `video_x_day.json` để xem khán giả hoạt động ngày nào.

## 7. Công thức tiêu đề và thumbnail

Chỉ Long, vì mẫu Long đủ để đọc (n=12–13 mỗi kênh). Không có dữ liệu thumbnail/CTR (API không có), nên mục thumbnail chưa có bằng chứng.

**Nên dùng**
1. **Vụ lừa đảo/rủi ro đời thường kèm hành động bảo vệ** (MIM): "AI Giả Giọng Người Thân Để Lừa Tiền: Một Từ Bí Mật Có Thể Cứu Bạn": 12,9 giờ, cao nhất kênh, 429 view.
2. **Vụ việc có thật, có con số** (MIM): "Luật Sư Nộp 6 Vụ Án Do ChatGPT Bịa": 10,3 giờ, AVP 44%, Link ngoài kéo 5,6 giờ.
3. **Câu hỏi đánh vào nỗi lo của người xem, kèm đối chiếu lịch sử** (MIM): "AI Có Cướp Việc Của Bạn? 200 Năm Trước...": 10,3 giờ, 3 sub (cao nhất Long MIM).
4. **Một quyết định tiền cụ thể có hai phương án** (CK): "Trả Góp 19 Triệu Hay Thuê 6 Triệu: 10 Năm Sau Ai Khá Hơn?": 5,7 giờ, đứng đầu Long CK.
5. **Một sự kiện có ngày và nỗi đau cụ thể** (CK): "Ngày VN-Index Mất 115 Điểm...": 5,1 giờ, AVP 53%.
6. (CL, từ Studio, chưa kiểm bằng API) "Ngoài Đời Thật" về ông trùm châu Á người xem Việt đã biết qua phim.

**Nên tránh**
1. **Tiêu đề kiểu "tên riêng + năm" cho đề tài lịch sử công nghệ** (MIM): AlexNet 2012 (18 view, 0,9 giờ), Deep Blue 1997 (21 view, 1,1 giờ), Flappy Bird (13 view, 0,2 giờ). Người xem không biết các tên này; AlphaGo và Sholes thoát được nhờ câu chuyện quen thuộc/hấp dẫn, không phải nhờ công thức.
2. **Bài tổng quan chung hoặc dạy người mới không có tình huống** (CK): "Một Cây Nến Đỏ Kể Gì? Biểu Đồ Nến Cho Người Mới" (AVD 0:42, AVP 5%) và "Năm 2026: Chứng Khoán, Vàng, Coin, Nhà Đất Đều Đỏ" (AVD 1:02, AVP 10%). Người xem thoát trong khoảng một phút.
3. **Tiêu đề kéo mạnh nhưng nội dung không giữ** (MIM): "Thuật Toán Đề Xuất" 266 view nhưng AVP 21%, AVD 2:48. Được đẩy rồi bị bỏ.
4. (CL, từ Studio) "Bí Ẩn..." gần như bằng 0.

Mẫu nhỏ: mỗi nhóm chỉ 2–4 video; coi là giả thuyết để kiểm ở lần rà 4 tuần, không phải quy luật.

## 8. Mười kết luận chính

1. Sub khớp Studio tuyệt đối (MIM 62, CK 42); giờ Earn Long khớp trong khoảng 4 giờ (CK 17,7/17; MIM 57,1/53).
2. API **không** có impressions, CTR, Shown in feed hay giờ trong ngày. Chỉ Studio có; #183 không thể làm hết bằng API.
3. Giờ xem công khai Long 365 ngày: MIM 67 giờ, CK 21,5 giờ (CL chưa đo). Cách mốc 3.000 giờ rất xa.
4. Short tạo gần như toàn bộ view (MIM 98%, CK 99%) nhưng gần như không tạo sub (0,5–0,7/1.000 view) và không dẫn sang Long (không Long nào có nguồn SHORTS).
5. Long chuyển sub tốt hơn Short khoảng 6–10 lần trên mỗi 1.000 view (MIM 5,2 so với 0,53; CK 4,1 so với 0,67).
6. MIM Short bị chặn trần khoảng 1.0–1.4k view (median 832, p75 1.034, max 1.420); tuần đăng nhiều thì median giảm 38%.
7. Giờ đăng Short gần như không ảnh hưởng (tỷ số 0,93–1,13). Long chỉ có một slot 20:00 nên không so được.
8. Long thắng khi có đề tài lừa đảo/AI/việc làm (MIM) và quyết định tiền cụ thể (CK); thua khi tiêu đề là tên riêng + năm, hoặc bài tổng quan chung.
9. Link ngoài (EXT_URL) cho AVD dài nhất (MIM 11 phút theo #177) nhưng chỉ vài view; Đề xuất mang phần lớn giờ xem Long; Subscriber cho nhiều view nhưng ít giờ.
10. CK tuần thử đầu 29/10–04/11: median 248 (n=14, chưa đủ tuổi) so với mốc 271 của 20–26/10; mới có 14 Short công khai nên chưa kích hoạt được luật dừng.

## 9. Giới hạn dữ liệu

- Không có credential CL: toàn bộ mục CL thiếu.
- API không có impressions, CTR, Shown in feed, lướt qua, giờ trong ngày. Không suy ngược.
- Thông tin "ở lại" chỉ qua engagedViews/views, không phải định nghĩa "stayed to watch" của Studio; nên dùng như xếp hạng tương đối.
- Ngày tính theo giờ Thái Bình Dương; cửa sổ 3 ngày đầu là xấp xỉ 48–72 giờ.
- Dữ liệu API trễ khoảng 2 ngày (ngày cuối có số là 02–03/11), nên kỳ 7 ngày và video 01–04/11 thiếu.
- Chỉ video còn trên kênh; video đã gỡ không có trong bảng theo video.
- Short = thời lượng <= 180 giây; ranh giới giữa Long/Short theo video khác `creatorContentType` ở kênh. Số theo kênh dùng `creatorContentType`.
- Mẫu nhỏ: Long mỗi kênh 12–13 video; slot Short mỗi ô 5–21 video.
- Chênh 322 (mốc CK của bạn) so với 271 (của tôi) chưa xác định nguyên nhân.
- Quy mô vẫn thấp; không phân tách được nguyên nhân (nội dung hay lịch) bằng số này.
