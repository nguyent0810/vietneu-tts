# Báo cáo: đối chiếu phân tích 28 ngày (17/9–14/10/2026) với source code

Người viết: Claude (Code), 16/10/2026. Người nhận: agent Lead. **PR chỉ gồm báo cáo này, không đổi code.**

Nguồn phân tích được đối chiếu: bản tổng hợp analytics kênh **Astro Việt Insights** (119K lượt xem, 346,6 giờ xem, +95 người đăng ký, 136 Shorts, khoảng 675 Shorts và vài video dài), do người dùng dán vào phiên làm việc. Tôi **không có dữ liệu gốc** (file xuất Studio, CSV, `reports.query`), nên mọi con số bên dưới là con số trong bản tóm tắt, chưa kiểm lại.

## 1. Tóm tắt cho Lead

1. Kết luận chính của bản phân tích **khớp với những gì code đã ghi nhận từ đợt đánh giá 03/10**: mỗi Short dừng ở ~1.000 view (vòng thử của feed), bài yếu rơi người xem khi câu 2 là định nghĩa/thuật ngữ ("Thái cực sinh lưỡng nghi" xuất hiện ở cả hai nơi), Short dưới 20 giây rất yếu. Hai nguồn độc lập cho cùng kết luận nên độ tin cậy tăng.
2. **Cửa sổ 28 ngày này gần như chưa chịu luật "short v2/v3".** Hai cổng chặn render theo công thức đó chỉ bật cho Short lên lịch từ **14/11/2026** (`SHORT_V2_FROM`) và **18/11/2026** (`SHORT_V3_FROM`). Vì vậy số liệu hiện tại là *đường cơ sở trước v2*, và hàng đợi đã lên lịch trước 14/11 **không** bị cổng chặn.
3. **Phần "đề xuất" của bản phân tích đã được code làm một phần** (câu hook ≤ 12–22 từ, câu 2 không định nghĩa, độ dài 21–27 giây, tự chỉnh giờ đăng, mùa khoá 2027). Thứ **thiếu thật** là vòng đo: không có chỗ nào lưu chiến lược hook / định dạng cho từng video để nối với chỉ số "ở lại xem" từ Studio.
4. **Rủi ro lớn nhất không nằm trong đề xuất 1–7** mà ở cảnh báo cuối bản phân tích: nội dung lặp/sản xuất hàng loạt ảnh hưởng YPP. Có một xung đột cần Lead quyết (mục 4.3): câu "theo lịch pháp truyền thống…" là hedge **bắt buộc** theo `creator_specs`, nên không thể bỏ, chỉ có thể đa dạng hoá cách diễn đạt.
5. Hai chỗ bản phân tích có thể đang **nhầm nút thắt**: người đăng ký (+95/28 ngày ≈ 10 tháng để đạt 1.000) và "giờ xem đủ điều kiện" (346,6 giờ có thể đã gồm Shorts).

## 2. Giới hạn của báo cáo
- Không có dữ liệu gốc; không biết "bình thường" (mức +159%) tính trên kỳ nào; không có n cho từng nhóm nội dung.
- "Astro Việt Insights" **không xuất hiện trong repo**. Repo gọi hai kênh là `bud` (`phat_giao`) và `fs` (`phong_thuy`). Giả định ở đây: Astro Việt Insights = kênh `fs`. Lead nên xác nhận.
- Repo tracked **không có** generator cho "series theo năm sinh" (ví dụ "1978, 1979: mệnh Thiên Thượng Hỏa"); chuỗi "Thiên Thượng Hỏa" chỉ gặp trong `hf_showreel.py`/`hf_batch_render.py`. Những video này nhiều khả năng sinh từ các `build_X.py` nằm trong `output/` (đã `.gitignore`). Vì vậy phát hiện 3 **không đối chiếu được với code**.
- Không chạy được gì có mạng hoặc YouTube API ở môi trường dựng báo cáo.

## 3. Bảng đối chiếu từng phát hiện

Trạng thái: **Khớp** (code/ghi chú trong repo ủng hộ), **Một phần**, **Không xác minh được**, **Cần xác nhận**.

| # | Phát hiện trong analytics | Trạng thái | Bằng chứng trong repo |
|---|---|---|---|
| 1 | Phần lớn Shorts đứng ở ~1.000 view (top 50 nằm 950–1.300) | **Khớp** | `hf_batch_render.py:291-294`: "short nào cũng dừng ở ~900-1.000 view (vòng thử của feed Shorts); bài bứt lên là bài xem hết > 90%" (đánh giá 28 ngày tới 03/10) |
| 1b | Bài yếu mất người xem sớm; ví dụ "Thái cực sinh lưỡng nghi" 119 view | **Khớp** | cùng đoạn trên: rơi người xem ở 20–50% thời lượng, đúng câu 2 khi là định nghĩa, ví dụ "Thái cực sinh lưỡng nghi"; luật chặn `DEFINE_OPENER`/`DEFINE_IN2` (`hf_batch_render.py:298-299`, dùng ở `short_v2_issues`) |
| 2 | Nội dung 2027 là động lực tăng trưởng (3 video ≈ 40K view) | **Một phần** | Chủ đề đã có trong cấu hình: `hf_brief.py:46-48` (SEEDS/SEARCH có "năm 2027", "tử vi 2027"), `hf_trends.py`, kicker `"12 CON GIÁP · 2027"` cho lane `long` của `fs` (`hyperframes_bridge.py:108`). Không có generator Short riêng cho Tam Tai/Kim Lâu/Hoang Ốc/sao hạn trong repo tracked |
| 3 | Series năm sinh: tỉ lệ ở lại 50–73%, xem ~100% | **Không xác minh được** | không có generator tracked (xem mục 2). Mô tả "xem hết hoặc xem lại" phù hợp với nhận định của code rằng bài tốt là bài xem hết > 90% |
| 4a | Lịch ngày: 160–700 view; ~30 video/tháng; ~75 video đã lên lịch đến tháng 12 | **Khớp (xác minh 20/10)** | **Đính chính 20/10:** đếm lại bằng `hf_coverage` (search.list + index) thấy **71 short hoàng đạo dạng cũ** đã hẹn từ 20/10 đến 29/12; số "46 video hẹn, không có chuỗi lịch ngày" đo ngày 19/10 là thiếu vì playlist uploads bỏ sót video riêng tư có `publishAt` (ước lượng ~75 ban đầu gần đúng). Dạng cũ ghi sai trực có hệ thống (vd 21/10 ghi Bế, đúng là Phá; 22/10 ghi Kiến, đúng là Nguy). Ngày 20/10 đã gỡ lịch cả 71 (chuyển riêng tư, KHÔNG xoá; sổ khôi phục `output/cl_staging/fs/hoangdao_old_unscheduled_2026-10-20.json`), thay bằng khuôn lưới 12 con giáp (~711 view/giờ so với 8–19 view/giờ của dạng cũ). 180 short gỡ ngày 06/10 (80 FS + 100 BUD) vẫn ở chế độ riêng tư, không xoá. |
| 4b | Kinh Dịch, Can, Tài tinh, cung hoàng đạo phương Tây: 13–400 view | **Khớp (có generator)** | `iching_short_generator.py`, `western_zodiac_short_generator.py`, `element_*_short_generator.py`; lane `kinhdich`, `nguhanh` |
| 5 | Video dài mới bắt đầu (14–26 view), ~20 video đã lên lịch | **Một phần** | Hạ tầng dài có đủ (`long_batch_runner.py`, skill `long-script`, `next_available_weekly_slot` ở `long_batch_runner.py:703`). Skill `long-script` có format (b) "Tử vi trọn đời tuổi X + 2027" (35–45 phút), đúng loại bản phân tích đề xuất |
| 6 | Kênh đăng ~5 Shorts/ngày | **Khớp** | `twice_weekly_batch.py:85` `SHORTS_PER_DAY = 5`; mỗi lần chạy tự lấp phần thiếu của từng ngày (`:233`, `:274`), nên cắt nội dung phải đổi cả quota lẫn danh sách generator |
| 7 | Đề xuất "sửa 2 giây đầu, hiện chữ to ngay khung đầu" | **Một phần đã làm** | Câu hook ≤ 12 từ trong prompt judge panel và ngưỡng 20 từ ép trần điểm (`short_judge_panel_engine.py:65`, `_validate_verdict`); `short_v2_issues` chặn câu 1 > 22 tiếng, câu 2 là định nghĩa, độ dài lệch 68–88 tiếng (FS) (`hf_batch_render.py:326-348`, `SHORT_V2_SYLLABLES` ở `:297`) — **nhưng chỉ cho Short lên lịch từ 14/11** |
| 8 | Đề xuất giờ đăng 12h và 18–21h | **Đã có cơ chế** | `hf_slots.py`: tự đổi tối đa một giờ/tuần dựa trên hạng trung vị trong tuần (`WEEKS=4`, `MIN_N=6`, `COOLDOWN_W=3`); mặc định FS `["04:30","08:00","12:00","15:00"]` UTC (`hf_slots.py:DEFAULT`), tức 11:30, 15:00, 19:00, 22:00 giờ VN |
| 9 | Đề xuất nối Shorts → video dài, ghim bình luận, CTA | **Chưa có** | Có scope OAuth `youtube.force-ssl` (commit `3d6ffc7`) nhưng không có code ghim/trả lời bình luận hay gắn "video liên quan" (`grep` không thấy `commentThreads`/`relatedVideo`) |
| 10 | Cảnh báo nội dung lặp / "Ghi chép theo lịch pháp truyền thống…" | **Khớp, có xung đột** | Chuỗi chính xác không có trong code. Nhưng `creator_specs/PRODUCTION_CREATOR_PROMPT_v1.md:70` và `PROMPT_DELTA_v1.md` bắt buộc hedge "theo lịch pháp truyền thống / được xem là" cho mọi khẳng định cát/hung, vi phạm bị FAIL cùng mức với sai dữ liệu. Xem 4.3 |
| 11 | Chưa đo được tác dụng của hook | **Khớp** | `short_batch_runner.py:805` và `:819` ghi `entry["hook_score"] = None` cho mọi topic khác `DEFAULT_TOPIC` (trong đó có FS), dù judge panel đã tính điểm. Điểm chỉ lưu ở nhánh review chung `:828` |

## 4. Nhận định

### 4.1 Đồng ý
- Hướng "tập trung 2027 + giảm lịch ngày + cắt Kinh Dịch/Can chi" phù hợp cả với dữ liệu bản phân tích lẫn kết luận 03/10 trong code.
- Cảnh báo monetization là điểm giá trị nhất của bản phân tích.
- So sánh nội bộ (50–73% so với 35% ở lại) đáng tin hơn mọi benchmark ngoài.

### 4.2 Cần sửa hoặc thận trọng
1. **Nút thắt YPP.** Với +95 người đăng ký mỗi 28 ngày, mốc 1.000 người đăng ký cần khoảng 10 tháng; mốc giờ xem có thể chưa phải thứ chặn. Hơn nữa 346,6 giờ có thể đã gồm Shorts, trong khi giờ xem đủ điều kiện chỉ tính video dài công khai. Cần xem mục "giờ xem đủ điều kiện" ở tab Kiếm tiền của Studio. Điều kiện YPP có thể đã đổi, cần đối chiếu bản hiện hành.
2. **Quy kết nhân quả.** "+159% là do đăng nhiều hơn" và "YouTube thử với nhóm nhỏ rồi không đẩy tiếp" là giả thuyết. Thiếu mức nền và n từng nhóm.
3. **Mâu thuẫn trong đề xuất.** Bộ "12 con giáp, mỗi tuổi một video" và series năm sinh chính là kiểu mẫu lặp mà cảnh báo cuối nói đến. Mỗi video phải khác nhau về *nội dung tính ra được* (ví dụ sao hạn, tháng cần để ý của đúng tuổi đó), không chỉ đổi tên tuổi.
4. **Nối Shorts → video dài.** Khán giả Shorts feed hiếm khi sang video 30 phút (14–26 view là hợp lý). Người dùng vẫn **ƯU TIÊN Long ≥ 30 phút** để nội dung sinh động, phong phú, có chiều sâu (bỏ lý do "để có quảng cáo giữa" vì quảng cáo giữa chỉ cần ≥ 8 phút và kênh chưa bật kiếm tiền). Không dừng lên lịch video 30+ phút mà tập trung sửa 2 phút đầu và các mốc re-hook 25/50/75%. Video dài cần đi bằng tìm kiếm/gợi ý (format (b) của `long-script`).
5. **Giờ đăng** có tác dụng yếu với Shorts feed và đã có `hf_slots.py`, nên ưu tiên thấp.

### 4.3 Xung đột giữa "đa dạng hoá" và "hedge bắt buộc"
Bản phân tích khuyên làm các video bớt giống nhau. `creator_specs` lại yêu cầu mỗi khẳng định cát/hung phải có framing dè dặt, và vi phạm là FAIL. Cách giải: **giữ hedge, đa dạng hoá cách nói** (một danh sách nhiều mẫu câu hedge, chọn xoay vòng và kiểm không lặp trong N video gần nhất, giống `hf_novelty.py` đã làm cho chủ đề). Không nên bỏ hedge để chống lặp, vì hedge cũng bảo vệ khỏi rủi ro nội dung.

### 4.4 Việc code đã làm và chưa làm
- Đã có: công thức short v2/v3, chống trùng chủ đề (`hf_novelty`), tự chỉnh giờ (`hf_slots`), bản tóm tắt tuần (`hf_brief`), báo cáo Short (`hf_shorts_report`).
- **Chưa có / khoảng trống thật:**
  1. Lưu `hook_score`, chiến lược hook (A/B/C) và lane/định dạng cho mỗi video FS vào registry (hiện `None`).
  2. Nhập số "ở lại xem / lướt qua" từ Studio (API không có chỉ số này; xem `analytics_reviews/2026-07-25_to_2026-07-26/01_cursor_analytics_report.md:90`) để nối với metadata trên.
  3. Cơ chế giảm quota theo lane thay vì lấp cố định 5 video/ngày.
  4. Generator Short cho 2027 theo tuổi (Tam Tai, Kim Lâu, Hoang Ốc, sao hạn) với dữ kiện tính bằng code.
  5. Ghim bình luận / trả lời / CTA tự động.
  6. Đa dạng hoá câu hedge có kiểm lặp.

## 5. Đề xuất cho Lead (xếp theo ưu tiên, **không có thay đổi code trong PR này**)
1. **Hàng đợi FS:** **Đính chính 20/10:** đếm lại bằng `hf_coverage` (search.list + index) thấy **71 short hoàng đạo dạng cũ** đã hẹn từ 20/10 đến 29/12; số "46 video hẹn, không có chuỗi lịch ngày" đo ngày 19/10 là thiếu vì playlist uploads bỏ sót video riêng tư có `publishAt` (ước lượng ~75 ban đầu gần đúng). Dạng cũ ghi sai trực có hệ thống (vd 21/10 ghi Bế, đúng là Phá; 22/10 ghi Kiến, đúng là Nguy). Ngày 20/10 đã gỡ lịch cả 71 (chuyển riêng tư, KHÔNG xoá; sổ khôi phục `output/cl_staging/fs/hoangdao_old_unscheduled_2026-10-20.json`), thay bằng khuôn lưới 12 con giáp (~711 view/giờ so với 8–19 view/giờ của dạng cũ). 180 short gỡ ngày 06/10 (80 FS + 100 BUD) vẫn ở chế độ riêng tư, không xoá.
2. **Cân nhắc kéo `SHORT_V2_FROM`/`SHORT_V3_FROM` sớm hơn** nếu hàng đợi hiện tại do hf pipeline sinh. Hai ngày mốc trong `hf_batch_render.py:295` và `:353` là hằng số, đổi rất rẻ, nhưng cần Lead quyết vì có thể chặn hàng đợi hiện có.
3. **Lưu metadata hook/lane vào registry** và thêm bước nhập CSV Studio vào `hf_shorts_report.py` hoặc `hf_brief.py`. Đây là việc nhỏ và mở khoá khả năng thử nghiệm A/B hook trong series năm sinh.
4. **Đổi cơ cấu quota** (ví dụ 3 năm sinh/2027, 1 cặp tuổi hợp–xung, 1 lịch gộp theo tuần) và đo hai tuần trước khi cắt tiếp. Cắt tổng số quá mạnh làm mất lượng thử mà feed Shorts cần.
5. **Bộ Short 2027 theo tuổi** với dữ kiện từ code dự án (`canchi.py`, `tuvi_year.py`, `amlich.py`, `ngaytot.py`), kèm hedge đa dạng (mục 4.3).
6. **Nối Short 2027 → video dài "Tử vi trọn đời tuổi X + 2027"** (format (b)) thay vì lên lịch thêm video dài chủ đề chung.
7. Bình luận ghim + CTA "bình luận năm sinh": ưu tiên thấp vì 42% khán giả từ 45 tuổi hiếm bình luận.

## 6. Dữ liệu và xác nhận cần từ người dùng/Lead
- Kênh Astro Việt Insights có phải kênh `fs` không?
- Xuất từ Studio, theo từng video trong 28 ngày: tiêu đề, ngày đăng, thời lượng, lượt xem, **% ở lại xem**, giờ xem, người đăng ký. Với dữ liệu đó có thể tính phân bố (trung vị, p90) theo từng lane thay vì chỉ nhìn top 50.
- Nguồn của hàng đợi FS: `hf_coverage` (search.list + index) ngày 20/10: 71 short hoàng đạo dạng cũ (đã gỡ lịch, không xoá); playlist uploads không thấy video riêng tư có `publishAt`.
- Giờ xem *đủ điều kiện* và tổng số người đăng ký hiện tại.

## Phụ lục: tham chiếu code đã dùng
`twice_weekly_batch.py:85,233,274` · `hf_batch_render.py:291-299,326-348,353-371` · `hyperframes_bridge.py:94-110` · `hf_slots.py` (docstring, `DEFAULT`) · `hf_brief.py:1-30,44-49` · `hf_trends.py` · `short_batch_runner.py:805,819,828` · `short_judge_panel_engine.py:65` · `zodiac_short_generator.py:65` · `twelve_gods_short_generator.py:49` · `creator_specs/PRODUCTION_CREATOR_PROMPT_v1.md:70` · `analytics_reviews/2026-07-25_to_2026-07-26/01_cursor_analytics_report.md`
