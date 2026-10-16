# Khuyến nghị tổng hợp cho hai kênh FS (Astro Việt Insights) và BUD (Phật giáo), 10/2026

Người viết: Claude (Code), 16/10/2026. Dành cho agent Lead. **Tài liệu quyết định, không đổi code.**
Gom từ: [`ANALYTICS_REVIEW_2026-10.md`](ANALYTICS_REVIEW_2026-10.md) (đối chiếu số liệu FS với code), [`SERIES_PROPOSAL_2027.md`](SERIES_PROPOSAL_2027.md) (chuỗi FS tới Tết 2027), phần chẩn đoán Kinh Dịch/Tài tinh/cung hoàng đạo (FS), phần đánh giá phân tích BUD, và dữ liệu thô tháng 7 trong `analytics_reviews/`.

## 0. Mức tin cậy của từng nguồn
| Nguồn | Mức | Ghi chú |
|---|---|---|
| Code và hằng số trong repo | Cao | Đã đọc, có `file:dòng` |
| Dữ liệu thô tháng 7 (`analytics_reviews/2026-07-27_daily_factory_raw`) | Cao nhưng cũ | Chỉ số view lũy kế, **không** có retention/"Shown in feed"; tuổi video khác nhau; mỗi kênh 18–20 video |
| Số liệu 28 ngày FS (17/9–14/10) | Trung bình | Người dùng dán bản tóm tắt; **chưa thấy dữ liệu gốc** |
| Số liệu BUD (30,1% ở lại, 97,2% feed, 2% tìm kiếm, 490 view video dài…) | Thấp–trung bình | Chỉ có bản *đánh giá* do agent khác viết, **chưa thấy phân tích gốc** |
| Chính sách YPP "inauthentic content" | Cao | [Trang trợ giúp chính thức](https://support.google.com/youtube/answer/1311392) |
| Cơ chế phân phối Shorts | Trung bình–thấp | Chỉ có blog tổng hợp; YouTube không công bố ngưỡng |
| Nhu cầu tìm kiếm (quẻ, cung hoàng đạo, Tam Tai…) | **Không đo được** | Google Trends/gợi ý tìm kiếm bị proxy chặn; web search mỏng |

## 1. Điều hai kênh có chung (kết luận chính)
1. **Short dừng ở ~1.000 view** là vòng thử của feed, không phải trần của chủ đề. Code đã ghi nhận từ đợt 03/10 cho cả hai kênh (`hf_batch_render.py:291-294`); phân tích FS 28 ngày và đánh giá BUD cùng thấy.
2. **Chênh lệch trong cùng chủ đề, cùng generator, cùng ngày lớn hơn chênh lệch giữa các chủ đề.** FS tháng 7: Bạch Dương 800 view và Song Tử 10 view (cùng generator). BUD tháng 7: trung vị 604 view, từ 0 đến 1.195 view. → **cách đóng gói và hook quyết định nhiều hơn chủ đề.**
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
| R6 | **FS: đóng gói lại Kinh Dịch/Tài tinh/cung hoàng đạo, chưa bỏ hẳn** | FS | 6–8 video mỗi nhóm trong 2 tuần, mỗi nhóm ≤ 1 video/ngày. Kinh Dịch: mở bằng tình huống thay vì tên quẻ, giữ quy tắc không dự đoán; có thể làm "xin quẻ đầu năm" mùa Tết. Tài tinh: theo năm sinh (ghi rõ đơn giản hoá, Bát tự chuẩn dùng Can ngày sinh). Cung hoàng đạo: chỉ tiếp tục nếu tab Khán giả của chính các video đó khớp |
| R7 | **BUD: định dạng "hiểu lầm → điều kinh thực sự nói"** và lời dạy gắn chuyện đời thường | BUD | Phù hợp tông "hiền, chữa lành, có kinh". Tránh mở bằng "…— sai" gay gắt với tục dân gian (đốt vàng mã, phóng sinh): 42% khán giả (FS) từ 45 tuổi; đối chiếu kinh bằng `hf_sutta.py`, link SuttaCentral trong mô tả (`hf_batch_render.py:379`) |
| R8 | **Đa dạng hoá câu hedge nhưng giữ hedge** ("theo lịch pháp truyền thống…") | FS | Hedge là **bắt buộc** (`creator_specs/PRODUCTION_CREATOR_PROMPT_v1.md:70`); xoay nhiều mẫu câu, kiểm lặp trong N video gần nhất như `hf_novelty.py` |

### P2 — video dài và liên kết
| # | Việc | Chi tiết |
|---|---|---|
| R9 | **Long FS: thử A/B** bản ngắn 12–15 phút "Tuổi X năm 2027" (3 tuổi) với bản 35–45 phút "trọn đời" (2 tuổi, cùng tuổi). Mở rộng khi 2–3 video đầu đạt ≥ 300 view/14 ngày và ≥ 40% ở lại (ngưỡng khởi đầu, chỉnh sau) | Khán giả Short hiếm chuyển sang Long; Long phải đến từ tìm kiếm/gợi ý. Dừng lên lịch Long mới chung chung (~20 video FS đang chờ) |
| R10 | **Long BUD:** giữ hướng tuyển tập Tiền Thân và "Đêm nghe"; theo dõi tín hiệu sớm (490 view/3 ngày, 13,7% giờ xem từ TV — số từ bản đánh giá, chưa kiểm) | Khán giả lớn tuổi xem TV: ưu tiên chất lượng chương và mô tả có mục lục |
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
| Giữ hay bỏ Kinh Dịch/Tài tinh/cung hoàng đạo? | Chưa bỏ: thử đóng gói lại 2 tuần rồi quyết theo số liệu |
| Kênh `fs` có đúng là Astro Việt Insights? | Cần xác nhận |
| Merge phần TTS (QA, lexicon, ASR) | **Quyết riêng**, xem mô tả PR; ba tài liệu này không phụ thuộc phần TTS |

## 4. Lộ trình 4 tuần và tiêu chí dừng
| Tuần | Việc |
|---|---|
| 1 (17–23/10) | R1, R2 (đổi quota), R3 (lưu metadata); xuất bảng Studio 28 ngày cho **cả hai kênh** |
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
1. Bảng Studio 28 ngày cho **mỗi kênh**, theo từng video: tiêu đề, ngày đăng, thời lượng, view, **Shown in feed**, **viewed vs swiped away**, giờ xem, người đăng ký.
2. Nguồn của ~75 video lịch ngày FS và ~20 video dài đã lên lịch.
3. "Giờ xem đủ điều kiện" và tổng người đăng ký hiện tại (tab Kiếm tiền).
4. Phân tích gốc của BUD (chưa thấy).
5. Tab Khán giả riêng cho nhóm cung hoàng đạo (FS).
