# Báo cáo YouTube Analytics — 2026-07-25 đến 2026-07-26

**Đối tượng chính:** kênh **Phong Thủy** (pipeline `generator_new`)  
**Đối chiếu bối cảnh:** kênh **Phật giáo** (pipeline `preexisting_other` — không phải đối tượng cải tiến)  
**Nguồn:** `00_raw_data_bundle.json`  
**Thời điểm dữ liệu proxy:** lũy kế Data API tới lúc chạy báo cáo (khoảng **2026-07-27**)

---

## Giới hạn dữ liệu (bắt buộc đọc trước)

Theo field `data_limitations` trong file:

1. **YouTube Analytics API v2 có độ trễ xử lý thật ~3 ngày.** Đã kiểm chứng: dữ liệu Analytics có đầy đủ tới hết **2026-07-24**, nhưng **07-25 / 07-26 / 07-27 trả về 0 rows** dù query đúng.
2. **Hệ quả:** trong khung 07-25→07-26 **KHÔNG CÓ** dữ liệu theo ngày về retention, `averageViewPercentage`, `averageViewDuration`, traffic source, `subscribersGained`/`subscribersLost`, likes/comments/shares theo ngày, hay watch-time. Tất cả `analytics_window.rows`, `channel_analytics_by_day.rows`, `traffic_sources.rows` đều **rỗng**.
3. **Proxy tạm thời:** dùng `lifetime_statistics` (viewCount / likeCount / commentCount) từ Data API — đây là **số lũy kế tới thời điểm chạy báo cáo**, **không** phải số tách riêng theo từng ngày 25/26. Với video mới 1–2 ngày, gần đúng khung nhưng **có thể lẫn một phần view sau 07-26**.
4. **Nên chạy lại Analytics đầy đủ** khi dữ liệu 07-25/07-26 đã xử lý xong — **dự kiến khoảng 2026-07-28** (theo độ trễ quan sát ~3 ngày).

Báo cáo dưới đây **không suy diễn** retention / swipe-away / traffic source.

---

## 1. View distribution và growth

> **Ghi chú:** mọi view dưới đây là **lũy kế `lifetime_statistics.viewCount`**, không phải views theo ngày từ Analytics API.

### 1.1. Phong Thủy (8 video) — đối tượng chính

| # | video_id | Title (hook) | Ngày đăng (UTC) | Duration | Views lũy kế |
|---|----------|--------------|-----------------|----------|--------------|
| 1 | `AuUpRQZOcwc` | Cách kê giường có khiến bạn thấy bất an? | 2026-07-26T08:00:09Z | PT37S | **1120** |
| 2 | `C59YfZdozJ0` | Hôm Nay Con Giáp Nào May Mắn Nhất? | 2026-07-26T11:00:08Z | PT29S | **1007** |
| 3 | `_m0aX_gJbaw` | Duy Trì Tinh Thần Kiên Định Qua Quẻ Càn Vi Thiên | 2026-07-26T05:00:25Z | PT25S | **967** |
| 4 | `uHwa6nFBtkc` | Mệnh Thủy Thuận Lợi, Mệnh Mộc Thận Trọng Ngày Canh Tý 25/07/2026 | 2026-07-25T05:00:31Z | PT27S | **881** |
| 5 | `7hV0dkjaHyM` | Bạch Dương bốc đồng hay chỉ sợ bỏ lỡ cơ hội? | 2026-07-25T14:00:09Z | PT28S | **799** |
| 6 | `xrP_GshgjeM` | Ý nghĩa quẻ Tốn Vi Phong: Mềm mỏng nhưng bền bỉ | 2026-07-25T11:00:04Z | PT25S | **307** |
| 7 | `8xTWAaMDFYk` | Khuyết mệnh Kim: Đừng vội dùng ví màu đỏ, hồng, tím! | 2026-07-26T14:00:40Z | PT30S | **79** |
| 8 | `VoTM7ILVbP0` | Song Tử: Bên Ngoài Náo Nhiệt, Bên Trong Sâu Sắc | 2026-07-25T08:00:06Z | PT37S | **8** |

- **Tổng views lũy kế (8 video):** 881 + 8 + 307 + 799 + 967 + 1120 + 1007 + 79 = **5168**
- **Phân bố theo ngày đăng (proxy theo `published_at_created`, không phải views theo ngày):**
  - Đăng **2026-07-25** (4 video): 881 + 8 + 307 + 799 = **1995** views lũy kế
  - Đăng **2026-07-26** (4 video): 967 + 1120 + 1007 + 79 = **3173** views lũy kế
- **Growth theo ngày từ Analytics:** **KHÔNG CÓ DỮ LIỆU** (`channel_analytics_by_day.rows` = `[]`)
- **Traffic sources:** **KHÔNG CÓ DỮ LIỆU** (`traffic_sources.rows` = `[]`)

**Phân bố views theo category (pipeline_metadata):**

| Category | Số video | Views lũy kế | % trên tổng 5168 |
|----------|----------|--------------|------------------|
| Category 5 – Storytelling | 1 | 1120 | 21.7% |
| Category 3 – Interpretation (Kinh Dịch) | 2 | 307 + 967 = **1274** | 24.7% |
| Category 1 – Grounded Data (con giáp hợp/kỵ theo ngày) | 1 | 1007 | 19.5% |
| Category 1 – Grounded Data (mệnh tài lộc theo ngày) | 1 | 881 | 17.0% |
| Category 4 – Creative Astrology (12 cung hoàng đạo) | 2 | 8 + 799 = **807** | 15.6% |
| Category 1 – Grounded Data, evergreen (màu hợp mệnh) | 1 | 79 | 1.5% |

**Phân bố views theo generator:**

| Generator | Views lũy kế |
|-----------|--------------|
| `storytelling_short_generator.py` | 1120 |
| `iching_short_generator.py` | 1274 |
| `zodiac_short_generator.py` | 1007 |
| `element_luck_short_generator.py` | 881 |
| `western_zodiac_short_generator.py` | 807 |
| `element_color_short_generator.py` | 79 |

**Phân bố theo khung giờ đăng (UTC, slot cố định 05/08/11/14):**

| Slot UTC | Video | Views lũy kế tổng slot |
|----------|-------|------------------------|
| 05:00 | 2 (mệnh ngày + quẻ Càn) | 881 + 967 = **1848** |
| 08:00 | 2 (Song Tử + kê giường) | 8 + 1120 = **1128** |
| 11:00 | 2 (quẻ Tốn + con giáp) | 307 + 1007 = **1314** |
| 14:00 | 2 (Bạch Dương + màu mệnh Kim) | 799 + 79 = **878** |

### 1.2. Phật giáo (9 video) — chỉ đối chiếu

- **Tổng views lũy kế:** 812 + 166 + 782 + 594 + 850 + 926 + 938 + 492 + 1 = **5561**
- Growth / traffic theo ngày: **KHÔNG CÓ DỮ LIỆU** (cùng lý do API lag)
- Dải views: **1** (`ptC7AlcsA6o`) → **938** (`B_i31QRy670`); video nổi bật engagement: `vdqTzm-qXOo` (850 views, **54** likes)

---

## 2. Viewed vs swiped away

**KHÔNG CÓ DỮ LIỆU.**

Metric “viewed vs swiped away” **không có sẵn** qua YouTube Analytics API v2 public — đây là **giới hạn thật của API**, không phải lỗi thu thập trong bundle này.

**Nguồn thay thế khi cần:**
- YouTube Studio UI (thủ công) — Shorts / “Viewed vs swiped away” nếu Studio hiển thị
- Sau khi Analytics lag hết: dùng `averageViewPercentage` / retention curve từ `reports.query` (dự kiến có từ ~**2026-07-28** cho khung 07-25/07-26)

---

## 3. Retention và average percentage viewed

**KHÔNG CÓ DỮ LIỆU** cho khung 2026-07-25 → 2026-07-26.

- Mọi `analytics_window.rows` = `[]` (không có `averageViewPercentage`, `averageViewDuration`, `estimatedMinutesWatched`)
- Lý do: độ trễ Analytics API ~3 ngày (`data_limitations`)
- **Đề xuất chạy lại:** khoảng **2026-07-28** (hoặc sau khi xác nhận query range 07-25→07-26 trả về rows khác rỗng)

Không suy diễn retention từ viewCount/likeCount.

---

## 4. Engagement (likes, comments, subscribers)

> Proxy: `lifetime_statistics` lũy kế. Subscribers theo ngày: **KHÔNG CÓ DỮ LIỆU**.

### 4.1. Phong Thủy

| video_id | Views | Likes | Comments | Like/View (tính từ số có sẵn) |
|----------|-------|-------|----------|-------------------------------|
| `AuUpRQZOcwc` | 1120 | 11 | 0 | 11/1120 |
| `C59YfZdozJ0` | 1007 | 9 | 0 | 9/1007 |
| `_m0aX_gJbaw` | 967 | **13** | 0 | 13/967 |
| `uHwa6nFBtkc` | 881 | 6 | **1** | 6/881 |
| `7hV0dkjaHyM` | 799 | 7 | 0 | 7/799 |
| `xrP_GshgjeM` | 307 | 1 | 0 | 1/307 |
| `8xTWAaMDFYk` | 79 | 0 | 0 | 0/79 |
| `VoTM7ILVbP0` | 8 | 0 | 0 | 0/8 |

- **Tổng likes lũy kế:** 6+0+1+7+13+11+9+0 = **47**
- **Tổng comments lũy kế:** **1** (chỉ video `uHwa6nFBtkc`)
- **dislikeCount / favoriteCount:** toàn bộ = **0** theo file
- **subscribersGained / subscribersLost:** **KHÔNG CÓ DỮ LIỆU**
- **shares theo Analytics:** **KHÔNG CÓ DỮ LIỆU**

**Engagement theo category (likes lũy kế):**

| Category | Likes | Comments |
|----------|-------|----------|
| Cat 3 Kinh Dịch | 1+13 = **14** | 0 |
| Cat 5 Storytelling | **11** | 0 |
| Cat 1 Con giáp | **9** | 0 |
| Cat 4 Astrology | 0+7 = **7** | 0 |
| Cat 1 Mệnh tài lộc ngày | **6** | **1** |
| Cat 1 Evergreen màu mệnh | **0** | 0 |

### 4.2. Phật giáo (đối chiếu)

| Tổng likes lũy kế | Tổng comments | Video likes cao nhất |
|-------------------|---------------|----------------------|
| 4+0+9+10+54+19+8+4+0 = **108** | **1** (`vdqTzm-qXOo`) | `vdqTzm-qXOo`: **54** likes / 850 views |

So sánh thô (cùng proxy lũy kế, kênh khác nhau — chỉ bối cảnh): Phong Thủy 47 likes / 5168 views; Phật giáo 108 likes / 5561 views. **Không suy ra “chất lượng retention”** từ tỷ lệ này vì thiếu retention data.

---

## 5. Publishing time, topic, hook, duration

### 5.1. Phong Thủy (có `pipeline_metadata`)

Lịch đăng cố định slot UTC **05:00 / 08:00 / 11:00 / 14:00**; `publish_at_scheduled` = `null` trên mọi video; `privacy_status` = `public`.  
`hook_score_at_generation` = **NOT PERSISTED** (gap thật trong registry — không có điểm hook số để phân tích).

| Ngày | Slot UTC | Title (= hook) | Category | Generator | Duration |
|------|----------|----------------|----------|-----------|----------|
| 07-25 | 05:00:31Z | Mệnh Thủy Thuận Lợi, Mệnh Mộc Thận Trọng Ngày Canh Tý 25/07/2026 | Cat 1 mệnh tài lộc ngày | `element_luck_short_generator.py` | PT27S |
| 07-25 | 08:00:06Z | Song Tử: Bên Ngoài Náo Nhiệt, Bên Trong Sâu Sắc | Cat 4 Astrology | `western_zodiac_short_generator.py` | PT37S |
| 07-25 | 11:00:04Z | Ý nghĩa quẻ Tốn Vi Phong: Mềm mỏng nhưng bền bỉ | Cat 3 Kinh Dịch | `iching_short_generator.py` | PT25S |
| 07-25 | 14:00:09Z | Bạch Dương bốc đồng hay chỉ sợ bỏ lỡ cơ hội? | Cat 4 Astrology | `western_zodiac_short_generator.py` | PT28S |
| 07-26 | 05:00:25Z | Duy Trì Tinh Thần Kiên Định Qua Quẻ Càn Vi Thiên | Cat 3 Kinh Dịch | `iching_short_generator.py` | PT25S |
| 07-26 | 08:00:09Z | Cách kê giường có khiến bạn thấy bất an? | Cat 5 Storytelling | `storytelling_short_generator.py` | PT37S |
| 07-26 | 11:00:08Z | Hôm Nay Con Giáp Nào May Mắn Nhất? | Cat 1 con giáp ngày | `zodiac_short_generator.py` | PT29S |
| 07-26 | 14:00:40Z | Khuyết mệnh Kim: Đừng vội dùng ví màu đỏ, hồng, tím! | Cat 1 evergreen màu mệnh | `element_color_short_generator.py` | PT30S |

- **Duration quan sát:** PT25S → PT37S (toàn bộ Shorts ngắn)
- **Hook dạng câu hỏi** trong title: có ở `7hV0dkjaHyM`, `AuUpRQZOcwc`, `C59YfZdozJ0` (và một phần `8xTWAaMDFYk` dạng cảnh báo)

### 5.2. Phật giáo (chỉ title + publish time — không có pipeline_metadata nội bộ)

| published_at_created (UTC) | Title | Duration | Views | Likes |
|----------------------------|-------|----------|-------|-------|
| 2026-07-25T03:30:37Z | Địa ngục thực sự trông như thế nào? | PT41S | 594 | 10 |
| 2026-07-25T08:00:14Z | Địa ngục có thật hay chỉ là tấm gương tâm lý? | PT39S | 782 | 9 |
| 2026-07-25T12:30:17Z | Người ấy đã đi rồi, sao bạn còn giữ oán hận? | PT30S | 166 | 0 |
| 2026-07-25T16:20:10Z | Kinh Phật kể cõi khổ: Hù dọa hay lòng từ bi? | PT41S | 850 | **54** |
| 2026-07-25T16:20:34Z | Bạn Có Quyền Đau, Có Quyền Chưa Hiểu Hết Vì Sao | PT22S | 492 | 4 |
| 2026-07-25T23:00:16Z | Cõi Tối Tăm Liệu Có Đang Chờ Người Sống Ác? | PT30S | 926 | 19 |
| 2026-07-26T16:20:34Z | Từ Bi Không Phải Là Chịu Đựng Vô Điều Kiện | PT27S | 938 | 8 |
| 2026-07-26T23:00:04Z | Phật Giáo Ngày 27/7: Bài Học Sâu Sắc | PT10S | 1 | 0 |
| 2026-07-26T23:00:28Z | Bóng tối trong bạn chưa từng là một hình phạt | PT22S | 812 | 4 |

---

## 6. Successful patterns và potential bottlenecks

> Chỉ dựa trên view / like / comment lũy kế + metadata pipeline. **Không** kết luận về retention.

### 6.1. Patterns quan sát được trên số liệu thật (Phong Thủy)

1. **Top views lũy kế (≥1000):** Storytelling kê giường (1120), Con giáp ngày (1007) — cả hai đăng **07-26**.
2. **Top likes lũy kế:** Quẻ Càn Vi Thiên (**13** likes / 967 views); Storytelling (**11**); Con giáp (**9**).
3. **Category 3 (Kinh Dịch)** có biến thiên lớn trong cùng generator: Quẻ Càn 967 views / 13 likes vs Quẻ Tốn 307 views / 1 like.
4. **Category 4 (Astrology)** cũng biến thiên lớn: Bạch Dương 799 / 7 vs Song Tử **8 / 0**.
5. **Hai video “đuôi” rõ:** Song Tử (8 views) và Khuyết mệnh Kim evergreen (79 views, 0 like) — cùng generator khác nhau, cùng nằm ở đuôi phân bố.
6. **Comment gần như không có:** 1 comment / 8 video.
7. **Gap metadata:** `hook_score_at_generation` không được persist → không thể đối chiếu hook score với performance trong báo cáo này.
8. **Slot 05:00 UTC** có tổng views lũy kế cao nhất trong 4 slot (1848), nhưng mẫu chỉ 2 video/slot — chưa đủ để khẳng định slot “tốt”.

### 6.2. Bottlenecks quan sát được trên số liệu thật

1. **Phân bố views rất lệch:** max 1120 vs min 8 trên cùng 2 ngày / cùng kênh.
2. **Một nhánh Astrology và một nhánh evergreen màu mệnh** đang ở đuôi views (8 và 79) — cần dữ liệu retention/traffic sau này để biết do discovery hay do giữ chân.
3. **Engagement comment gần zero** trên toàn bộ sample Phong Thủy tuần này.
4. **Thiếu Analytics theo ngày** khiến không đo được growth thật, watch-time, subscriber net, traffic — đây là bottleneck **phân tích**, không phải bottleneck nội dung đã chứng minh.

### 6.3. Đối chiếu Phật giáo (bối cảnh, không phải đối tượng cải tiến)

- Tổng views lũy kế cùng khung gần tương đương (5561 vs 5168) nhưng **likes cao hơn rõ** (108 vs 47), chủ yếu do 1 outlier `vdqTzm-qXOo` (54 likes).
- Không có category/generator nội bộ để map pattern pipeline.

---

# FACTS

*(Chỉ con số / sự kiện có trong file — không diễn giải)*

1. Khung ngày: **2026-07-25 → 2026-07-26**.
2. Phong Thủy: **8** video public, pipeline `generator_new`.
3. Phật giáo: **9** video public, pipeline `preexisting_other`.
4. Analytics theo ngày / retention / traffic / subscribers window: **0 rows** cho cả 2 kênh trong khung này.
5. `data_limitations`: API lag ~**3 ngày**; proxy = lifetime Data API; khuyến nghị chạy lại ~**2026-07-28**.
6. Phong Thủy tổng views lũy kế: **5168**; likes: **47**; comments: **1**.
7. Phong Thủy views theo video: 1120, 1007, 967, 881, 799, 307, 79, 8.
8. Phong Thủy likes theo video: 11, 9, 13, 6, 7, 1, 0, 0 (cùng thứ tự video ở mục 1.1).
9. Phong Thủy đăng 07-25: 4 video, tổng views lũy kế **1995**; đăng 07-26: 4 video, **3173**.
10. Generators Phong Thủy trong khung: `element_luck`, `western_zodiac`, `iching`, `storytelling`, `zodiac`, `element_color`.
11. Durations Phong Thủy: PT25S, PT37S, PT25S, PT28S, PT25S, PT37S, PT29S, PT30S.
12. Slot đăng Phong Thủy (UTC): 05:00, 08:00, 11:00, 14:00 mỗi ngày; `publish_at_scheduled` = null.
13. `hook_score_at_generation` = NOT PERSISTED trên mọi video Phong Thủy trong file.
14. Phật giáo tổng views lũy kế: **5561**; likes: **108**; comments: **1**.
15. Phật giáo video likes cao nhất: `vdqTzm-qXOo` — **850** views, **54** likes, **1** comment.
16. Phật giáo video views thấp nhất trong sample: `ptC7AlcsA6o` — **1** view, PT10S, đăng 2026-07-26T23:00:04Z.

---

# HYPOTHESES

*(Có thể đúng nhưng chưa đủ dữ liệu xác nhận. Cỡ mẫu 8 video / 2 ngày là **rất nhỏ** — hầu hết tin cậy thấp.)*

1. **[Tin cậy: thấp]** Storytelling (hook câu hỏi thực dụng về nhà ở) và “con giáp ngày” có xu hướng đạt views lũy kế cao hơn các format khác trong sample này — có thể do topic/search intent, nhưng chưa tách được ảnh hưởng traffic source / retention.
2. **[Tin cậy: thấp]** Cùng Category 4 Astrology có thể cho outcome rất khác nhau (Bạch Dương 799 vs Song Tử 8) — giả thuyết: hook dạng câu hỏi / cung cụ thể / timing khác nhau; **chưa chứng minh** vì thiếu impression/swipe/retention.
3. **[Tin cậy: thấp]** Evergreen “màu hợp mệnh” (`element_color`) đang underperform so với grounded-data theo ngày trong sample — có thể do thiếu neo thời gian trong title, hoặc do slot 14:00 UTC ngày 26 chưa đủ thời gian tích lũy (video mới hơn) — **không thể tách** hai yếu tố với dữ liệu hiện có.
4. **[Tin cậy: thấp]** Slot 05:00 UTC “có vẻ” mạnh hơn trên tổng views lũy kế slot — nhưng chỉ 2 video/slot và video 05:00 ngày 26 (967) vs 05:00 ngày 25 (881) gần nhau; song Tử 08:00 kéo thấp trung bình slot 08:00 → dễ gây nhiễu.
5. **[Tin cậy: thấp]** Tỷ lệ like/view Phật giáo cao hơn Phong Thủy trong sample chủ yếu do outlier 54 likes; khi bỏ outlier, khoảng cách hẹp lại — chưa đủ để kết luận khác biệt “engagement culture” giữa 2 kênh.
6. **[Tin cậy: trung bình]** Việc thiếu `averageViewPercentage`/retention cho khung này làm **không thể** xếp hạng “chất lượng giữ chân” — mọi xếp hạng hiện tại chỉ phản ánh **tích lũy view/like**, không phản ánh completion. (Mức tin cậy trung bình vì đây là hệ quả trực tiếp từ `data_limitations`, không phải suy đoán nội dung.)
7. **[Tin cậy: thấp]** Comment ≈ 0 trên Phong Thủy có thể liên quan CTA/hook không kích thích trả lời; hoặc đơn giản do tuổi video còn ngắn / audience size — **không xác nhận được** từ file.

---

*Báo cáo này **không** đưa khuyến nghị cải tiến cụ thể — dành cho bước phân tích tiếp theo.*
