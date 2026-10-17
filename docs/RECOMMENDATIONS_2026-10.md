# Khuyến nghị tổng hợp cho hai kênh FS (Astro Việt Insights) và BUD (Phật giáo), 10/2026

Người viết: Claude (Code), 16/10/2026. Dành cho agent Lead. **Tài liệu quyết định, không đổi code.**
Cập nhật 16/10 theo file xuất Studio 28 ngày của cả hai kênh: [`DATA_ANALYSIS_2026-10.md`](DATA_ANALYSIS_2026-10.md) (R6, R6b, R7, R9, R10 đã đổi theo số liệu).
Gom từ: [`ANALYTICS_REVIEW_2026-10.md`](ANALYTICS_REVIEW_2026-10.md) (đối chiếu số liệu FS với code), [`SERIES_PROPOSAL_2027.md`](SERIES_PROPOSAL_2027.md) (chuỗi FS tới Tết 2027), phần chẩn đoán Kinh Dịch/Tài tinh/cung hoàng đạo (FS), phần đánh giá phân tích BUD, và dữ liệu thô tháng 7 trong `analytics_reviews/`.

## 0. Mức tin cậy của từng nguồn
| Nguồn | Mức | Ghi chú |
|---|---|---|
| Code và hằng số trong repo | Cao | Đã đọc, có `file:dòng` |
| Dữ liệu thô tháng 7 (`analytics_reviews/2026-07-27_daily_factory_raw`) | Cao nhưng cũ | Chỉ số view lũy kế, **không** có retention/"Shown in feed"; tuổi video khác nhau; mỗi kênh 18–20 video |
| **File xuất Studio 28 ngày của FS và BUD** (theo video: view, giờ xem, đăng ký, hiển thị hình thu nhỏ) | **Cao** | Phân tích ở [`DATA_ANALYSIS_2026-10.md`](DATA_ANALYSIS_2026-10.md). **Ưu tiên số liệu ở đó** khi khác với các dòng dưới |
| Số liệu tóm tắt FS 28 ngày (17/9–14/10) do người dùng dán | Trung bình | Đã được file Studio thay thế |
| Số liệu BUD trong bản đánh giá của agent khác (30,1% ở lại, 97,2% feed, 2% tìm kiếm…) | Thấp–trung bình | "Ở lại xem" và nguồn lưu lượng vẫn chưa kiểm (file Studio không có) |
| Chính sách YPP "inauthentic content" | Cao | [Trang trợ giúp chính thức](https://support.google.com/youtube/answer/1311392) |
| Cơ chế phân phối Shorts | Trung bình–thấp | Chỉ có blog tổng hợp; YouTube không công bố ngưỡng |
| Nhu cầu tìm kiếm (quẻ, cung hoàng đạo, Tam Tai…) | **Không đo được** | Google Trends/gợi ý tìm kiếm bị proxy chặn; web search mỏng |

## 1. Điều hai kênh có chung (kết luận chính)
1. **Short dừng ở ~1.000 view** là vòng thử của feed, không phải trần của chủ đề. Code đã ghi nhận từ đợt 03/10 cho cả hai kênh (`hf_batch_render.py:291-294`); phân tích FS 28 ngày và đánh giá BUD cùng thấy.
2. **Chủ đề hay đóng gói? Khác nhau giữa hai kênh** (cập nhật theo file Studio, xem `DATA_ANALYSIS_2026-10.md`). Dữ liệu tháng 7 (n=20, chỉ view) từng gợi ý đóng gói quan trọng hơn chủ đề. Số liệu 28 ngày cho thấy: **FS — chủ đề quyết định rất mạnh** (trung vị view theo chủ đề từ 412 đến 14.587; APV 0,13 đến 0,50). **BUD — chủ đề ít ảnh hưởng lượt xem** (trung vị 911–1.149) **nhưng ảnh hưởng mạnh tới người đăng ký** (1,0 đến 4,9 người/1.000 view). Ở cả hai kênh, Short chỉ vượt trần ~1.000 view khi APV khoảng ≥ 0,4–0,5.
3. **Hook nhắm người xem thắng hook gọi tên khái niệm.** FS: tiêu đề có năm sinh giữ chân 50–73%. BUD: "Hù dọa hay lòng từ bi?" 863 view/58 like; "Cả 3 tên gọi Kinh Địa Tạng đều không nhắc tới địa ngục?" 832 view. Thất bại điển hình: câu 2 là thuật ngữ ("Thái cực sinh lưỡng nghi" 119 view).
4. **Cả hai kênh sản xuất 5 Short/ngày theo khuôn.** Quota cố định ở `twice_weekly_batch.py:85` (`SHORTS_PER_DAY = 5`), batch tự lấp phần thiếu; mỗi kênh có 4–5 khung giờ mặc định (`hf_slots.py`). Nhiều video trong số này là video "lấp chỗ" theo khuôn ngày (FS "BÍ MẬT NGÀY…", BUD "…Ngày 28/7: Bài Học Sâu Sắc" 8–10 giây, 17–114 view).
5. **Rủi ro YPP áp dụng cho cả kênh.** Văn bản chính thức: nội dung "làm theo khuôn, ít hoặc không biến thể" hoặc "dễ nhân bản hàng loạt" không đủ điều kiện kiếm tiền, và có thể gỡ kiếm tiền trên *toàn kênh*. (Văn bản không nhắc giọng đọc hay AI; đó là diễn giải của bên thứ ba.)
6. **Không có vòng đo.** `short_batch_runner.py:805,819` ghi `hook_score = None` cho mọi topic khác mặc định; API không có "viewed vs swiped away" hay "Shown in feed". Hiện không đối chiếu được hook với hiệu suất.
7. **Cổng chất lượng short v2/v3 chưa áp cho hàng đợi hiện tại**: chỉ bật cho Short lên lịch từ **14/11** (`SHORT_V2_FROM`) và **18/11** (`SHORT_V3_FROM`) (`hf_batch_render.py:295,353`). Số liệu 28 ngày là đường cơ sở *trước* v2.

## 2. Khuyến nghị (xếp theo ưu tiên)

### P0 — làm ngay, rủi ro thấp
| # | Việc | Vì sao | Cần đổi gì |
|---|---|---|---|
| R1 | **Dừng/giảm video lấp chỗ theo khuôn ngày** (FS lịch ngày hằng ngày, BUD "…Ngày dd/mm: Bài Học Sâu Sắc"). Thay bằng 1 video gộp theo tuần (FS) và bỏ khuôn ngày (BUD). | Hiệu suất thấp nhất cả hai kênh; rủi ro YPP lớn nhất (khuôn lặp, số lượng lớn) | Tắt generator/lane trong rotation; kiểm hàng đợi đã lên lịch FS (~75 video đến tháng 12) và nguồn của chúng (nằm ngoài repo tracked) |
| R2 | **Đổi quota từ "lấp đủ 5/ngày" sang quota theo chuỗi/lane** | Cắt tổng số quá mạnh làm mất lượng thử; để nguyên thì tiếp tục sinh nội dung yếu | `twice_weekly_batch.py:85,233,274` + cơ cấu ở `SERIES_PROPOSAL_2027.md` mục 5 |
| R3 | **Lưu metadata hook/lane/chiến lược cho mọi Short FS+BUD** và nhập CSV Studio (Shown in feed, viewed vs swiped away, % ở lại) | Không có thì mọi thử nghiệm bên dưới không kết luận được | `short_batch_runner.py:805,819`; mở rộng `hf_shorts_report.py`/`hf_brief.py` |

### P1 — nội dung, bắt đầu trong tuần này
| # | Việc | Kênh | Chi tiết |
|---|---|---|---|
| R4 | **Sửa hook: nhắm người xem, không gọi tên khái niệm** | FS+BUD | Khung đầu là năm sinh/con giáp/tình huống; câu 2 không định nghĩa. Dùng luôn cổng v2/v3 cho hàng đợi mới ngay từ bây giờ (Lead cân nhắc kéo `SHORT_V2_FROM`/`SHORT_V3_FROM` sớm hơn) |
| R5 | **FS: chuỗi 2027** (Tuổi X năm 2027, Tam Tai, năm sinh+mệnh, Kim Lâu, xông đất, lịch Tết gộp, cặp tuổi) | FS | Chi tiết, dữ kiện đã tính và cơ cấu ở `SERIES_PROPOSAL_2027.md`. Mỗi video khác nhau bằng dữ kiện tính ra, không chỉ đổi tên con giáp |
| R6 | **FS: dừng Kinh Dịch, Tử vi sao/cung, chiêm tinh phương Tây trong lịch thường** (*thay* khuyến nghị cũ "thử đóng gói lại 2 tuần") | FS | Đã đủ mẫu: Kinh Dịch 15 video, trung vị 677, APV 0,13 (thấp nhất), hook dạng câu hỏi **không** giúp (398 so với 853); Tử vi sao/cung 8 video trung vị 412; chiêm tinh phương Tây 6 video trung vị 450. Kinh Dịch chỉ thử lại dạng "xin quẻ đầu năm" mùa Tết, ≤ 1 video/tuần. Can/Tài tinh chỉ giữ dạng theo năm sinh (ghi rõ đơn giản hoá). Không xếp nhiều video cùng đề tài liền nhau (6 video quẻ Kiền trong 6 ngày) |
| R6b | **FS: dồn sản lượng vào 2027 + năm sinh + quan hệ con giáp** | FS | 33% sản lượng mang về 65% lượt xem. 2027 nổ khi là câu hỏi chung cả năm với đáp án là danh sách tuổi; hoàn tất 30 cặp năm sinh (đang 17) |
| R7 | **BUD: nâng "giải mã biểu tượng" và "thực hành", giảm "đời thường/tâm lý"** (64% sản lượng xuống ~30%) | BUD | Biểu tượng: 4,9 người đăng ký/1.000 view so với 1,2; "đời thường" chiếm 11/16 video dưới 300 view. Giữ định dạng "hiểu lầm → điều kinh thực sự nói", tông "hiền, chữa lành, có kinh"; tránh mở bằng "…— sai" gay gắt với tục dân gian; đối chiếu kinh bằng `hf_sutta.py`, link SuttaCentral trong mô tả (`hf_batch_render.py:379`). Đa dạng công thức tiêu đề (không chỉ "Vì sao…?") |
| R8 | **Đa dạng hoá câu hedge nhưng giữ hedge** ("theo lịch pháp truyền thống…") | FS | Hedge là **bắt buộc** (`creator_specs/PRODUCTION_CREATOR_PROMPT_v1.md:70`); xoay nhiều mẫu câu, kiểm lặp trong N video gần nhất như `hf_novelty.py` |

### P2 — video dài và liên kết
| # | Việc | Chi tiết |
|---|---|---|
| R9 | **Long cả hai kênh: sửa 2 phút đầu trước khi làm thêm** | CTR đã ổn (FS 4,2–13%, BUD 2,7–3,4%) nhưng người xem chỉ ở lại ~1–3 phút: FS bản 35 phút giữ ~4,6% thời lượng, bản 7,6 phút ~15%; BUD bản 30 phút 11–17%. Ưu tiên bản 6–15 phút theo tuổi/chủ đề có tìm kiếm; dừng lên lịch thêm video 30+ phút (~20 video FS đang chờ) tới khi giữ chân cải thiện |
| R10 | **YPP: giờ xem video dài mới là nút thắt** | 28 ngày: FS 43 giờ, BUD 68 giờ (ước ~560 và ~900 giờ/năm nếu giữ tốc độ). Shorts chiếm 80–91% giờ xem nhưng không tính vào mốc 4.000 |
| R11 | **Nối Short → Long** qua "Video liên quan", mô tả có mục lục chương | Repo chưa có code làm việc này; làm thủ công hoặc API |
| R12 | **Tiêu đề/mô tả theo từ khoá người dùng gõ** (FS: Tam Tai, Kim Lâu, xông đất 2027; BUD: chủ đề có cầu như nhân quả, sám hối — *cầu chưa đo được*) | Tìm kiếm chỉ ~2–5% lượt xem; cải thiện từ từ, không thay hook |

### P3 — chậm hơn
- Series/playlist cho cụm chủ đề nhất quán (giúp feed học tệp khán giả; **không** đủ để kéo người xem quay lại khi 94–97% đến từ feed).
- Thương hiệu kênh BUD: `channelTitle` hiện là "Trần Kim Liên" (xác nhận trong dữ liệu thô). Hạ ưu tiên hơn hook và nội dung; quyết định của chủ kênh.
- Giờ đăng: ưu tiên thấp, đã có `hf_slots.py` tự chỉnh.

## 3. Quyết định cần Lead
| Quyết định | Đề xuất mặc định |
|---|---|
| Tạm dừng hàng đợi FS lịch ngày (~75 video) và video lấp chỗ BUD? | Có, tới khi xác nhận nguồn và cổng v2 áp được |
| Kéo `SHORT_V2_FROM`/`SHORT_V3_FROM` sớm hơn 14/11 và 18/11? | Có thể, nếu hàng đợi do pipeline hf sinh; kiểm tác động lên video đã lên lịch trước |
| Quota mới theo lane (hiện cố định 5/ngày)? | Có, thử 2 tuần theo cơ cấu ở `SERIES_PROPOSAL_2027.md` mục 5 |
| Giữ hay bỏ Kinh Dịch/Tài tinh/cung hoàng đạo? | **Dừng trong lịch thường** (số liệu đủ mẫu, xem R6); Kinh Dịch thử lại dạng "xin quẻ đầu năm" mùa Tết |
| Kênh `fs` có đúng là Astro Việt Insights? | Cần xác nhận |
| Merge phần TTS (QA, lexicon, ASR) | **Quyết riêng**, xem mô tả PR; ba tài liệu này không phụ thuộc phần TTS |

## 4. Lộ trình 4 tuần và tiêu chí dừng
| Tuần | Việc |
|---|---|
| 1 (17–23/10) | R1, R2 (đổi quota), R3 (lưu metadata), R6 (dừng nhóm yếu FS); xuất "Shown in feed"/"viewed vs swiped away" cho **cả hai kênh** |
| 2 (24–30/10) | R4, R5 (S1, S2), R7; bắt đầu R6 (≤ 1 video/ngày/nhóm) |
| 3–4 (31/10–13/11) | Thêm S3, S4; tổng kết R6 theo số liệu; chuẩn bị cổng v2/v3 |
| Từ 14/11 | Cổng v2/v3 bật; S5 (xông đất) từ 15/12; mùa Tết đến 5/2/2027 |

**Tiêu chí theo chuỗi (sau 6 video):** giữ nếu trung vị view ≥ 2× baseline (~1.000) *và* % ở lại ≥ 50%; thu hẹp nếu thấp hơn baseline ở cả hai. Chỉ số quyết định: "Shown in feed" thấp (< ~300) → vấn đề phân phối; "Shown in feed" cao nhưng viewed-vs-swiped thấp → vấn đề hook/nội dung.

## 5. Những khẳng định **không** nên dùng làm căn cứ
Có trong các bản đánh giá của agent khác nhưng không có nguồn kiểm chứng được:
- "62% Gen Z tin cung hoàng đạo" là số lặp lại từ khảo sát Mỹ (chưa kiểm chứng; nguồn Brands Vietnam không nêu mẫu; số EduBirdie tôi tìm thấy là khoảng 80% và khác).
- "Video 20K–100K+ view phổ biến ở kênh tử vi cỡ trung", "app gieo quẻ 100K+ lượt tải", "Chú Đại Bi/sám hối hàng triệu view ở kênh khác".
- "Tử vi theo con giáp mạnh hơn cung hoàng đạo ở nhóm tuổi lớn" (hợp lý với dữ liệu kênh nhưng chưa có khảo sát).
- Ngưỡng retention "70%+" và khoảng 500–5.000 view của giai đoạn thử (một blog, YouTube không công bố).

## 6. Dữ liệu cần để chốt
Đã có: bảng Studio 28 ngày theo video cho cả hai kênh (view, giờ xem, đăng ký, hiển thị hình thu nhỏ). Còn thiếu:
1. **BUD: "Stayed to watch" (viewed vs swiped away) và "Engaged views" theo video.** FS đã có: ngưỡng vượt trần ~45% ở lại; năm sinh 52%, 2027 50%, con giáp 43%, Kinh Dịch 15% (xem `DATA_ANALYSIS_2026-10.md` mục 2b).
2. Nguồn lưu lượng theo video (ba Short 2027 của FS đến từ feed hay tìm kiếm) và đường giữ chân của video dài.
3. Nguồn của ~75 video lịch ngày FS và ~20 video dài đã lên lịch.
4. "Giờ xem đủ điều kiện" và tổng người đăng ký hiện tại (tab Kiếm tiền).
5. Xuất lại FS sau ~3 ngày để chốt số ngày 15/10 (hai Short 2027 đăng hôm đó).
