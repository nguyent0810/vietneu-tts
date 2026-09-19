# Báo cáo Data Analyst — Cycle 2 (2026-07-27)

Nguồn: `00a_pt_utc_finding.md` + `00_raw_data_bundle_v2.json`. Chỉ số liệu có trong 2 file; không khuyến nghị.

---

## 1. Tóm tắt phát hiện PT/UTC

YouTube Analytics API bucket chiều `day` theo **Pacific Time (PT)**, không phải UTC — đã xác nhận bằng test A/B API thật (không phải suy đoán từ docs). Video `uHwa6nFBtkc` publish `2026-07-25T05:00:31Z` (= `2026-07-24T22:00:31` PDT) nên toàn bộ hoạt động đang thấy nằm trong bucket PT `"2026-07-24"`; query nhãn UTC `2026-07-25`–`2026-07-26` trả về toàn 0 dù video đã có traffic. Trong 17 video đợt này, chỉ **2** có cỡ mẫu Analytics ngày đủ lớn để tin được (`uHwa6nFBtkc`: 853 views / 91.9% AVP; `YStIdWWuXcU`: 586 views / 35.13% AVP); các video còn lại hoặc chưa có dòng PT ngày đã xử lý, hoặc có nhưng chỉ 1–3 views.

---

## 2. Bảng đầy đủ 17 video

**Khung query Analytics (nhãn UTC trên request):** `2026-07-20` → `2026-07-27`.  
**Traffic source:** cấp kênh, không tách theo video (API/bundle này không có traffic theo video).  
**Cột `real_pt_day_rows`:** `[day, views, estimatedMinutesWatched, averageViewDuration, averageViewPercentage, likes, comments, shares]`.

### 2.1. Kênh Phong Thủy — traffic source (khung wide window)

| insightTrafficSourceType | views | estimatedMinutesWatched |
|---|---:|---:|
| SHORTS | 3377 | 470 |
| YT_SEARCH | 701 | 363 |
| YT_CHANNEL | 65 | 6 |
| SUBSCRIBER | 29 | 90 |
| NO_LINK_OTHER | 26 | 11 |
| EXT_URL | 24 | 10 |
| HASHTAGS | 24 | 28 |
| RELATED_VIDEO | 23 | 90 |
| YT_OTHER_PAGE | 10 | 46 |
| NOTIFICATION | 6 | 0 |
| SOUND_PAGE | 1 | 0 |
| **Tổng views traffic (cộng các dòng)** | **4286** | **1114** |

### 2.2. Kênh Phật giáo — traffic source (khung wide window)

| insightTrafficSourceType | views | estimatedMinutesWatched |
|---|---:|---:|
| SHORTS | 9527 | 1053 |
| YT_SEARCH | 181 | 107 |
| YT_CHANNEL | 31 | 3 |
| RELATED_VIDEO | 25 | 60 |
| EXT_URL | 24 | 15 |
| YT_OTHER_PAGE | 22 | 24 |
| SUBSCRIBER | 14 | 106 |
| NO_LINK_OTHER | 12 | 29 |
| PLAYLIST | 5 | 9 |
| NOTIFICATION | 4 | 1 |
| HASHTAGS | 1 | 0 |
| SOUND_PAGE | 1 | 0 |
| **Tổng views traffic (cộng các dòng)** | **9847** | **1407** |

### 2.3. Chi tiết từng video

| # | video_id | Kênh | Title | published_at (UTC) | Lifetime views / likes / comments | real_pt_day_rows (nếu có) | Cỡ mẫu |
|---|---|---|---|---|---|---|---|
| 1 | `uHwa6nFBtkc` | Phong Thủy | Mệnh Thủy Thuận Lợi, Mệnh Mộc Thận Trọng Ngày Canh Tý 25/07/2026 | 2026-07-25T05:00:31Z | 881 / 6 / 1 | PT `2026-07-24`: views=853, minWatched=151, avgDur=24s, AVP=91.9%, likes=5, comments=1, shares=0 | **Đủ lớn (853 ≥ 500)** |
| 2 | `VoTM7ILVbP0` | Phong Thủy | Song Tử: Bên Ngoài Náo Nhiệt, Bên Trong Sâu Sắc | 2026-07-25T08:00:06Z | 8 / 0 / 0 | PT `2026-07-24`: views=1, minWatched=0, avgDur=38s, AVP=102.75%, likes=0, comments=0, shares=0 | **cỡ mẫu quá nhỏ để diễn giải (1 view)** |
| 3 | `xrP_GshgjeM` | Phong Thủy | Ý nghĩa quẻ Tốn Vi Phong: Mềm mỏng nhưng bền bỉ | 2026-07-25T11:00:04Z | 307 / 1 / 0 | PT `2026-07-24`: views=2, minWatched=0, avgDur=27s, AVP=109.16%, likes=0, comments=0, shares=0 | **cỡ mẫu quá nhỏ để diễn giải (2 views)** |
| 4 | `7hV0dkjaHyM` | Phong Thủy | Bạch Dương bốc đồng hay chỉ sợ bỏ lỡ cơ hội? | 2026-07-25T14:00:09Z | 799 / 7 / 0 | PT `2026-07-24`: views=2, minWatched=0, avgDur=50s, AVP=181.89%, likes=0, comments=0, shares=0 | **cỡ mẫu quá nhỏ để diễn giải (2 views)** |
| 5 | `_m0aX_gJbaw` | Phong Thủy | Duy Trì Tinh Thần Kiên Định Qua Quẻ Càn Vi Thiên | 2026-07-26T05:00:25Z | 967 / 13 / 0 | PT `2026-07-24`: views=2, minWatched=0, avgDur=29s, AVP=116.23%, likes=0, comments=0, shares=0 | **cỡ mẫu quá nhỏ để diễn giải (2 views)** |
| 6 | `AuUpRQZOcwc` | Phong Thủy | Cách kê giường có khiến bạn thấy bất an? | 2026-07-26T08:00:09Z | 1120 / 11 / 0 | PT `2026-07-24`: views=3, minWatched=1, avgDur=80s, AVP=216.69%, likes=0, comments=0, shares=0 | **cỡ mẫu quá nhỏ để diễn giải (3 views)** |
| 7 | `C59YfZdozJ0` | Phong Thủy | Hôm Nay Con Giáp Nào May Mắn Nhất? | 2026-07-26T11:00:08Z | 1007 / 9 / 0 | *(rỗng — không có dòng views>0 trong cửa sổ đã kéo)* | Không có dữ liệu ngày PT thật trong bundle |
| 8 | `8xTWAaMDFYk` | Phong Thủy | Khuyết mệnh Kim: Đừng vội dùng ví màu đỏ, hồng, tím! | 2026-07-26T14:00:40Z | 79 / 0 / 0 | *(rỗng)* | Không có dữ liệu ngày PT thật trong bundle |
| 9 | `iagKR5aAwH8` | Phật giáo | Bóng tối trong bạn chưa từng là một hình phạt | 2026-07-26T23:00:28Z | 812 / 4 / 0 | *(rỗng)* | Không có dữ liệu ngày PT thật trong bundle |
| 10 | `zv2UAKajdYk` | Phật giáo | Người ấy đã đi rồi, sao bạn còn giữ oán hận? | 2026-07-25T12:30:17Z | 166 / 0 / 0 | *(rỗng)* | Không có dữ liệu ngày PT thật trong bundle |
| 11 | `qF6RgxysgWk` | Phật giáo | Địa ngục có thật hay chỉ là tấm gương tâm lý? | 2026-07-25T08:00:14Z | 782 / 9 / 0 | *(rỗng)* | Không có dữ liệu ngày PT thật trong bundle |
| 12 | `YStIdWWuXcU` | Phật giáo | Địa ngục thực sự trông như thế nào? | 2026-07-25T03:30:37Z | 594 / 10 / 0 | PT `2026-07-24`: views=586, minWatched=92, avgDur=14s, AVP=35.13%, likes=10, comments=0, shares=0 | **Đủ lớn (586 ≥ 500)** |
| 13 | `vdqTzm-qXOo` | Phật giáo | Kinh Phật kể cõi khổ: Hù dọa hay lòng từ bi? | 2026-07-25T16:20:10Z | 850 / 54 / 1 | *(rỗng)* | Không có dữ liệu ngày PT thật trong bundle |
| 14 | `LERavRjVH7Q` | Phật giáo | Cõi Tối Tăm Liệu Có Đang Chờ Người Sống Ác? | 2026-07-25T23:00:16Z | 926 / 19 / 0 | *(rỗng)* | Không có dữ liệu ngày PT thật trong bundle |
| 15 | `B_i31QRy670` | Phật giáo | Từ Bi Không Phải Là Chịu Đựng Vô Điều Kiện | 2026-07-26T16:20:34Z | 938 / 8 / 0 | PT `2026-07-22`: views=2, minWatched=0, avgDur=32s, AVP=119.9%, likes=0, comments=0, shares=0 | **cỡ mẫu quá nhỏ để diễn giải (2 views)** |
| 16 | `bURO6B6dgvs` | Phật giáo | Bạn Có Quyền Đau, Có Quyền Chưa Hiểu Hết Vì Sao | 2026-07-25T16:20:34Z | 492 / 4 / 0 | *(rỗng)* | Không có dữ liệu ngày PT thật trong bundle |
| 17 | `ptC7AlcsA6o` | Phật giáo | Phật Giáo Ngày 27/7: Bài Học Sâu Sắc | 2026-07-26T23:00:04Z | 1 / 0 / 0 | *(rỗng)* | Không có dữ liệu ngày PT thật trong bundle |

**Ghi chú quan sát (không diễn giải nguyên nhân):** Trong bundle, mỗi video chỉ có các dòng `analytics_by_pt_day.rows` cho các ngày PT `2026-07-20` … `2026-07-24` (5 ngày), dù `query_window_utc_labels` ghi `2026-07-20`–`2026-07-27`.

---

## 3. So sánh trực tiếp 2 video cỡ mẫu đủ lớn

Cả hai chỉ có **một** dòng `real_pt_day_rows`, cùng ngày PT `2026-07-24`.

| Metric | `uHwa6nFBtkc` (Phong Thủy) | `YStIdWWuXcU` (Phật giáo) | Chênh (A − B) |
|---|---:|---:|---:|
| duration_iso8601 | PT27S | PT41S | — |
| published_at_utc | 2026-07-25T05:00:31Z | 2026-07-25T03:30:37Z | — |
| PT day | 2026-07-24 | 2026-07-24 | cùng ngày |
| views | 853 | 586 | +267 |
| estimatedMinutesWatched | 151 | 92 | +59 |
| averageViewDuration (giây) | 24 | 14 | +10 |
| averageViewPercentage (%) | 91.9 | 35.13 | +56.77 |
| likes (PT day) | 5 | 10 | −5 |
| comments (PT day) | 1 | 0 | +1 |
| shares (PT day) | 0 | 0 | 0 |
| likes / views (PT day) | 5/853 ≈ 0.586% | 10/586 ≈ 1.706% | — |
| lifetime viewCount | 881 | 594 | +287 |
| lifetime likeCount | 6 | 10 | −4 |
| lifetime commentCount | 1 | 0 | +1 |
| lifetime views − PT-day views | 881−853 = 28 | 594−586 = 8 | — |

**Observation (mô tả pattern, không khuyến nghị):** Trên cùng một ngày PT đã xử lý, `uHwa6nFBtkc` có views / phút xem / avg duration / AVP cao hơn; `YStIdWWuXcU` có likes (PT day và lifetime) cao hơn dù views thấp hơn.

---

## 4. FACTS

1. Dimension `day` của YouTube Analytics bucket theo PT; đã kiểm chứng bằng query thật trên `uHwa6nFBtkc` (range `2026-07-23`–`24` có data; `2026-07-25`–`26` toàn 0 trong test đó).
2. Chỉ **2/17** video có `real_pt_day_rows` với views ≥ 500: `uHwa6nFBtkc` (853), `YStIdWWuXcU` (586).
3. **8/17** video có `real_pt_day_rows` không rỗng; trong đó **6/8** có views ∈ {1, 2, 3} — cỡ mẫu quá nhỏ để diễn giải.
4. **9/17** video có `real_pt_day_rows = []` (toàn 0 trong các ngày PT hiện có trong bundle), dù nhiều video vẫn có lifetime views từ Data API (ví dụ `C59YfZdozJ0` lifetime 1007; `vdqTzm-qXOo` lifetime 850 / 54 likes / 1 comment; `AuUpRQZOcwc` lifetime 1120 nhưng PT-day thật chỉ 3 views).
5. Trên 6 video cỡ mẫu nhỏ có AVP: 102.75%, 109.16%, 181.89%, 116.23%, 216.69%, 119.9% — tất cả > 100%; file `00a` ghi đây là hiện tượng Shorts loop/autoplay thật, không phải lỗi số liệu.
6. Kênh Phong Thủy (traffic wide window): nguồn views lớn nhất là SHORTS (3377), tiếp theo YT_SEARCH (701); các nguồn còn lại ≤ 65 views mỗi nguồn.
7. Kênh Phật giáo (traffic wide window): nguồn views lớn nhất là SHORTS (9527); YT_SEARCH chỉ 181; các nguồn còn lại ≤ 31 views mỗi nguồn.
8. Tổng views từ traffic source wide window: Phong Thủy 4286; Phật giáo 9847 (cộng các dòng trong bundle).
9. Video Phong Thủy publish slot `05:00 UTC` (`uHwa6nFBtkc`) là video Phong Thủy duy nhất trong đợt có PT-day views lớn; các slot `08:00`/`11:00`/`14:00` cùng ngày UTC hoặc có 1–3 views hoặc rỗng.
10. Video Phật giáo có PT-day views lớn duy nhất là `YStIdWWuXcU` (`published_at` 03:30:37Z); các video Phật giáo khác trong bundle hoặc rỗng PT-day hoặc 2 views (`B_i31QRy670`).
11. Ba video có `published_at_utc` sau ngày PT trong `real_pt_day_rows`: `_m0aX_gJbaw` (publish 2026-07-26, row PT 2026-07-24, n=2), `AuUpRQZOcwc` (publish 2026-07-26, row PT 2026-07-24, n=3), `B_i31QRy670` (publish 2026-07-26, row PT 2026-07-22, n=2) — đây là số liệu trong bundle; cỡ mẫu quá nhỏ để diễn giải.
12. Lifetime like cao nhất trong 17 video: `vdqTzm-qXOo` = 54 likes / 850 views; video này **không** có `real_pt_day_rows` trong bundle.
13. Lifetime views cao nhất: `AuUpRQZOcwc` = 1120; PT-day thật chỉ 3 views (cỡ mẫu quá nhỏ).
14. Lifetime views thấp nhất: `ptC7AlcsA6o` = 1; `VoTM7ILVbP0` = 8.
15. Trong 2 video cỡ mẫu đủ lớn, shares = 0 cả hai trên ngày PT `2026-07-24`.
16. Bundle ghi `_bugfix_note`: `has_real_retention_data` từng tính sai bằng `row[0]!=0` (so sánh chuỗi ngày); đã sửa thành `row[1]!=0` (views) trước khi dùng bundle này.

---

## 5. HYPOTHESES

*(Khả năng chưa đủ chứng cứ — không phải kết luận. Mức tin gắn với cỡ mẫu thật.)*

1. **[Tin cậy trung bình — dựa trên 2 video n≥500]** Chênh lệch AVP 91.9% vs 35.13% và avg duration 24s vs 14s giữa `uHwa6nFBtkc` và `YStIdWWuXcU` phản ánh khác biệt retention thật giữa hai video trên cùng một ngày PT đã xử lý. *Chưa đủ để suy ra nguyên nhân (độ dài, chủ đề, kênh, traffic mix, v.v.) vì không có traffic/retention breakdown theo video và chỉ n=2 video.*

2. **[Tin cậy thấp]** Like rate PT-day cao hơn ở `YStIdWWuXcU` (≈1.7%) so với `uHwa6nFBtkc` (≈0.6%) có thể phản ánh khác biệt engagement; *chỉ 2 điểm dữ liệu, không có phân rã theo nguồn traffic per video.*

3. **[Tin cậy thấp–trung bình theo mô tả file 00a]** Khoảng trống `real_pt_day_rows` ở nhiều video (lifetime cao nhưng Analytics ngày = 0) chủ yếu do PT calendar day chưa được Analytics xử lý xong, hơn là do video thực sự không có traffic ngày đó. *Lifetime API lifetime luôn có; Analytics day có lag theo PT — đã xác nhận cơ chế, nhưng chưa có pull lại sau khi các ngày PT sau 2026-07-24 được xử lý để đối chiếu từng video.*

4. **[Tin cậy thấp — n=1–3]** AVP > 100% trên các video nhỏ phản ánh loop/autoplay Shorts (theo 00a); *không thể dùng để xếp hạng retention giữa các video đó.*

5. **[Tin cậy thấp]** SHORTS chiếm đa số views traffic cả hai kênh trong wide window có thể đồng nghĩa phần lớn traffic đợt này đến từ feed Shorts; *window là cấp kênh (có thể gồm video ngoài 17 video này), không gắn được sang từng video trong bảng.*

6. **[Tin cậy rất thấp — n=2–3 và mâu thuẫn thời gian]** Các dòng PT-day có views trước `published_at_utc` (`_m0aX_gJbaw`, `AuUpRQZOcwc`, `B_i31QRy670`) có thể là nhiễu/edge case/processing artifact; *cỡ mẫu quá nhỏ, không đủ để khẳng định pattern.*

7. **[Tin cậy thấp]** `vdqTzm-qXOo` (850 views lifetime, 54 likes) có thể có retention/engagement đáng chú ý khi Analytics PT day của nó được xử lý; *hiện không có bất kỳ dòng `real_pt_day_rows` nào để kiểm chứng.*

---

*Vai trò Data Analyst kết thúc tại đây — không có khuyến nghị / quyết định tối ưu.*
