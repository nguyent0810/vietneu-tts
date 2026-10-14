# Phân tích 4 video thật đã public ngày 2026-07-27 — Phong Thủy + Phật giáo

**Trạng thái: Codex APPROVED (vòng 4). Lịch sử: vòng 1 NEEDS_REVISION (8 phát hiện) → vòng 2 NEEDS_REVISION (2 chưa đạt + 4 sửa tối thiểu) → vòng 3 NEEDS_REVISION (1 lỗi số liệu nhỏ) → vòng 4 APPROVED.**

**Nguồn dữ liệu + raw evidence:** YouTube Data API v3 (`videos.list`) qua `youtube_catalog.py`, YouTube Analytics API v2 qua `youtube_analytics.py`, credentials thật trong `.youtube_channels/`. **Round 2 correction (Codex finding #1 — bản round-1 chỉ lưu bản đã rút gọn/normalize, không phải response thô thật):** response JSON gốc, chưa qua biến đổi, của từng lệnh gọi API đã được lưu thành file riêng trong `analytics_reviews/2026-07-27_daily_factory_raw/` — xem danh sách file + cách đối chiếu ở mục "Raw evidence" cuối tài liệu này.

---

## Dữ liệu thô (Data API thật, lấy lúc `retrieved_at_utc = 2026-07-28T11:04Z` — xem raw evidence)

| Kênh | Video ID | Publish (UTC) | Tuổi tại lúc lấy số liệu | Tiêu đề | Định dạng | Views | Likes | Comments |
|---|---|---|---|---|---|---|---|---|
| FS | `y60qB8xSrZU` | 23:00:20 | ~12.1 giờ | BÍ MẬT NGÀY RẰM THÁNG 6: ĐÓN CÁT KHÍ THIÊN ĐỨC | Short (PT39S) | 12 | 1 | 1 |
| BUD | `IktxS6H8UmU` | 13:00:28 | ~22.1 giờ | Địa Tạng Bồ Tát Là Ai? Giải Mã Danh Hiệu, Biểu Tượng Và Đại Nguyện | **Long-form (PT18M8S)** | 8 | 0 | 0 |
| BUD | `8Q0D7DCIU0o` | 16:20:31 | ~18.7 giờ | Có Người Chỉ Đi Cùng Bạn Một Đoạn Đường Tối | Short (PT33S) | **836** | 6 | 0 |
| BUD | `kX4gmF0bCjA` | 23:00:37 | ~12.1 giờ | Lời Phật Dạy Ngày 28/7: Bài Học Sâu Sắc | Short (PT8S) | 17 | 0 | 0 |

**Round 1 correction (Codex finding #3 — so sánh chưa kiểm soát tuổi video):** đã thêm cột tuổi video tại thời điểm lấy số liệu. Lưu ý: video 836-view (16:20:31) đã có ~18.7 giờ tiếp xúc, nhiều hơn ~6.6 giờ so với 2 video 23:00 (12.1 giờ) — một phần chênh lệch view có thể đến từ tuổi, không chỉ từ giờ đăng/nội dung. Không đủ dữ liệu để tách 2 yếu tố này.

**Round 1 correction (Codex finding #7 — 0 like/comment có thể là "thiếu trường" chứ không chắc là số 0 thật):** `youtube_catalog.get_videos_details()` dùng `stats.get("likeCount", 0)`/`stats.get("commentCount", 0)` — nếu YouTube không trả field này (vd bị ẩn/tắt), hàm hiện tại sẽ báo `0` giống hệt trường hợp thật sự bằng 0, không phân biệt được. Các số `0` trong bảng trên (đặc biệt likes/comments của video Long-form và "Lời Phật Dạy") cần được đọc với lưu ý này — không khẳng định chắc chắn đó là số 0 thật.

## Đối chiếu với lịch phát real đã biết trước đó trong kênh

- FS thường có 4 khung giờ lặp lại thật: 05:00 / 08:00 / 11:00 / 14:00 UTC. Video FS thật duy nhất của 27/7 đăng lúc **23:00 UTC** — không khớp 4 khung đã biết. Fact, chưa rõ nguyên nhân.
- BUD thường có nhịp 5 khung giờ thật: 03:30 / 08:00 / 12:30 / 16:20 / 23:00 UTC. 3 video BUD hôm 27/7 đăng lúc 13:00, 16:20, 23:00 UTC — 16:20 và 23:00 khớp chính xác; 13:00 lệch ~30 phút so với khung 12:30 đã biết (video này là Long-form, có thể thuộc nhóm lịch khác Short).

## Quan sát nổi bật (facts, chưa phải kết luận)

1. **Chênh lệch view lớn giữa 2 Short cùng kênh, cùng ngày (đã kiểm soát tuổi ở mức có thể):** "Có Người Chỉ Đi Cùng Bạn..." (836 views, ~18.7h tuổi) cao hơn ~49 lần so với "Lời Phật Dạy Ngày 28/7" (17 views, ~12.1h tuổi) — chênh lệch views/giờ vẫn rất lớn (~44.7 views/giờ so với ~1.4 views/giờ) ngay cả sau khi quy đổi thô theo tuổi, nên tuổi không giải thích hết chênh lệch. Không có traffic-source/retention để giải thích nguyên nhân; đây là tín hiệu, không phải kết luận.
2. **Video Long-form (18 phút) là loại nội dung khác hoàn toàn Short — không dùng để so tỷ lệ.** *(Round 1 correction, Codex finding #4: bản v1 vừa cảnh báo "không nên so 1-1" vừa tự dùng tỷ lệ "~100 lần" so Short với Long-form ngay sau đó — mâu thuẫn nội bộ. Đã bỏ hẳn con số tỷ lệ Short-vs-Long khỏi phần quan sát; chỉ giữ lại dữ kiện thô 8 views/~22.1h cho video Long-form, không so sánh định lượng với Short.)*
3. **FS chỉ có 1 video thật public trong cửa sổ 2026-07-27T00:00:00Z–2026-07-28T00:00:00Z**, theo playlist uploads thật của kênh (`UU` + channel ID `UCabOUyNfseJfu-Xy_KXz2rw`), duyệt 20 video gần nhất, không phân trang thêm. *(Round 1 correction, Codex finding #8: nêu rõ tiêu chí lọc + phạm vi duyệt. Mệnh đề này chỉ nói về số video ĐÃ public, không suy ra được có video nào khác đã lên lịch nhưng chưa tới giờ hay không — đã bỏ câu suy đoán đó khỏi bản v1.)*
4. **Không tìm thấy video ID/tiêu đề nào trong 4 video này trùng với package đã soạn trong phiên làm việc này** (đối chiếu thủ công với `WEEKLY_CONTENT_PACKAGE_v1_draft.md`). *(Round 1 correction, Codex finding #6: bản v1 suy luận từ đây sang "đây là nội dung thuộc pipeline có sẵn, đang chạy độc lập" — kết luận provenance quá xa so với bằng chứng thực tế đã có. Không có ledger/upload-log nào của pipeline khác được đối chiếu, nên KHÔNG khẳng định được provenance, chỉ khẳng định được sự không trùng khớp với manifest phiên này.)*

## Giả thuyết (hypothesis, gắn nhãn rõ — CHƯA xác minh)

- *Giả thuyết, có trích dẫn cụ thể (round 1 correction — Codex finding #5, bản v1 không dẫn bảng/N):* dữ liệu thật trong `analytics_reviews/cycle2_2026-07-27/00_raw_data_bundle_v2.json` (kênh Phật giáo, N=9 video) cho thấy 3 video đăng lúc 16:20 UTC có views = 850, 938, 492 (trung bình ~760), và 3 video đăng lúc 23:00 UTC có views = 926, 812, 1 (trung bình ~580, nhưng phương sai rất lớn do 1 video chỉ có 1 view — có thể do tuổi quá thấp tại thời điểm đo, không phải hiệu suất giờ đăng). Với N=3/khung và phương sai cao, đây là tín hiệu yếu, KHÔNG phải kết luận đã được chứng minh về khung giờ tối ưu. **Round 2 correction (Codex finding #5 — vẫn còn 1 câu dùng video 836-view làm "nhất quán với" giả thuyết ngay sau khi đã nói không dùng nó làm bằng chứng, tự mâu thuẫn):** đã bỏ hẳn câu đó — video "Có Người Chỉ Đi Cùng Bạn..." KHÔNG được dùng ở bất kỳ hình thức nào (kể cả "nhất quán với") để củng cố giả thuyết khung giờ này, vì giờ đăng/tuổi video/nội dung của chính nó đều là biến nhiễu chưa tách được (xem giả thuyết thứ 2 ngay dưới).
- *Giả thuyết:* tiêu đề "Có Người Chỉ Đi Cùng Bạn Một Đoạn Đường Tối" (ẩn dụ, câu hỏi mở) có thể hấp dẫn hơn 2 tiêu đề còn lại. Không có dữ liệu CTR/impression để kiểm chứng — giờ đăng, tuổi video, và nội dung đều là biến nhiễu (confound) chưa tách được, nên KHÔNG dùng video này làm bằng chứng bổ sung cho giả thuyết về giờ đăng ở trên (round 1 correction, Codex finding #5).

## Giới hạn rõ ràng của báo cáo này

- Không có watch-time/retention/traffic-source cho 4 video này.
- **Về nguyên nhân Analytics rỗng (round 1 correction, Codex finding #2 — bản v1 khẳng định nguyên nhân "độ trễ xử lý" mà không tách khỏi vấn đề PT-vs-UTC day-bucketing đã xác lập ở Cycle 2):** đã tự query lại channel-day-level Analytics cho cửa sổ rộng 2026-07-20 đến 2026-07-28 (`dimensions=day`, xem raw evidence) — kết quả thật: có hàng dữ liệu cho các ngày PT đến hết `"2026-07-25"`, KHÔNG có hàng nào cho `"2026-07-26"` trở đi, ở cả 2 kênh. **Round 2 correction (Codex finding #2 — cần tách rõ 2 hiện tượng khác nhau):** đây là 2 câu hỏi khác nhau, chưa trả lời được câu nào: (a) *hiện tượng quan sát được* — channel-day-level hoàn toàn không có hàng nào cho ngày PT ≥ 26/7, ở CẢ 2 kênh, không riêng video nào; (b) *PT-day-bucketing* (đã xác lập ở Cycle 2) chỉ giải thích việc 1 video UTC cụ thể bị gán vào ngày PT nào, KHÔNG tự giải thích việc toàn bộ channel-day-level thiếu hẳn 1 ngày. Báo cáo này chỉ xác nhận được (a) bằng dữ liệu thật; KHÔNG kết luận (a) là do (b), do độ trễ xử lý thuần tuý, hay do cả hai.
- Mẫu quá nhỏ và quá mới (N=4, 12-22 giờ tuổi) để kết luận nhân quả.
- **Round 2 correction (Codex finding #6 — overclaim provenance tái xuất hiện: "không thuộc phạm vi nội dung tôi tạo" là kết luận rộng hơn bằng chứng cho phép):** Không tìm thấy bốn video này trong manifest được đối chiếu (`WEEKLY_CONTENT_PACKAGE_v1_draft.md`); vì vậy báo cáo không xác định được Creator Rules/CR-1 có được áp dụng cho 4 video này hay không.
- Số liệu like/comment bằng 0 có thể là giá trị thật hoặc trường bị thiếu trong response API (xem ghi chú ở bảng dữ liệu thô).

---

## Raw evidence (round 2 correction — Codex finding #1: round-1 chỉ có bản rút gọn, không phải response gốc; đã lưu file JSON thô thật)

**`retrieved_at_utc`:** 2026-07-28T11:04:00Z (round 1, các số trong bảng "Dữ liệu thô" ở đầu tài liệu) và 2026-07-28T11:31:00Z (round 2, lúc lưu lại các file raw JSON dưới đây — cùng phiên làm việc, cách nhau vài phút, không có video mới public giữa 2 lần gọi nên số liệu round 1 vẫn khớp).

Toàn bộ response JSON gốc (không qua `get_videos_details()`/hàm normalize nào) được lưu tại `analytics_reviews/2026-07-27_daily_factory_raw/`:

| File | Nội dung |
|---|---|
| `phong_thuy_videos_list_raw.json` | Response gốc `videos.list` (part=snippet,statistics,contentDetails) cho 20 video gần nhất trong uploads playlist thật của kênh Phong Thủy |
| `phong_thuy_last20_uploads.json` | Rút gọn còn `id`/`publishedAt`/`title` của cùng 20 video trên — dùng để kiểm tra độc lập mệnh đề "FS chỉ có 1 video public ngày 27/7" (đối chiếu `publishedAt` bắt đầu bằng `"2026-07-27"`) |
| `phong_thuy_channel_analytics_raw.json` | Response gốc `youtubeAnalytics#resultTable` đầy đủ `columnHeaders` + `rows`, `get_channel_analytics(cred, "2026-07-20", "2026-07-28")` |
| `phat_giao_videos_list_raw.json` | Như trên, kênh Phật giáo |
| `phat_giao_last20_uploads.json` | Như trên, kênh Phật giáo |
| `phat_giao_channel_analytics_raw.json` | Như trên, kênh Phật giáo |
| `video_analytics_y60qB8xSrZU_raw.json` | Response gốc `get_video_analytics()` riêng cho từng video (4 file, 1 file/video ID) |
| `video_analytics_IktxS6H8UmU_raw.json` | " |
| `video_analytics_8Q0D7DCIU0o_raw.json` | " |
| `video_analytics_kX4gmF0bCjA_raw.json` | " |

**Tóm tắt nhanh (không thay thế file raw, chỉ để đọc lướt; round 3 correction — Codex phát hiện phạm vi views ghi sai, chỉ lấy từ 1 kênh):** channel-day-level Analytics có hàng thật cho ngày PT đến hết `"2026-07-25"` — Phong Thủy: views 355-2369/ngày; Phật giáo: views 1071-5294/ngày — không có hàng nào cho `"2026-07-26"` trở đi ở cả 2 kênh. Xem `columnHeaders`+`rows` đầy đủ trong 2 file `*_channel_analytics_raw.json`. Cả 4 file `video_analytics_*_raw.json` đều có `rows: []`.

**Round 2 correction (Codex finding #1 — mô tả sai số lượng trích dẫn):** phần "Giả thuyết" ở trên trích **6 giá trị views thuộc 2 khung giờ (16:20 và 23:00 UTC)** từ `analytics_reviews/cycle2_2026-07-27/00_raw_data_bundle_v2.json` (file đó có N=9 video Phật giáo tổng cộng, không phải cả 9 đều được trích) — bản round-1 mô tả nhầm thành "trích nguyên văn danh sách 9 video", đã sửa lại cho đúng số thực tế được dùng.
