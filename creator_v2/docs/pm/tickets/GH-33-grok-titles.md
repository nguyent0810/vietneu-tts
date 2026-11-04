# GH-33 · Grok: tinh chỉnh title, mô tả, tag theo từ khóa đang hot cho 12 Short pilot

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/33. Chủ kênh yêu cầu 02/11: title chuẩn hot xu hướng, bám từ khóa, hook SS-tier.

Đầu vào:
- 12 spec `data/stier/specs/{ck-thue-xang-0-giam-1804,ck-dien-giam-44-dong-20-nam,ck-vang-sjc-140-trieu-chenh-14-trieu,ck-ho-kinh-doanh-giam-30-thue,ck-lai-giam-05-tien-gui-80-ngan-han,ck-binance-63-ty-rut-36-ty,mim-binance-20-phut-6-3-ty,mim-cam-nhap-dien-thoai-cu-2027,mim-sam-altman-ram-5-phan-tram,mim-android-20-tin-nhan-tu-than,mim-9-tren-10-ai-tu-lay-otp,mim-ve-tinh-google-4-chip-tpu}.json`
- facts: `docs/pm/tickets/GH-33-{MIM,CK}-facts.json`

## Được ghi
- `docs/pm/tickets/GH-33-titles.json`: đề xuất; Lead sẽ áp vào spec
- báo cáo `docs/pm/tickets/GH-33-titles-report.md`

**Không:** sửa spec, `lines` hay hook (đã render), upload, đổi lịch, commit. Không dùng Google autocomplete.

## Việc
1. **Từ khóa.** Với mỗi Short, tìm cụm người Việt đang tìm thật cho sự kiện:
   - Google Trends VN (trending RSS `trends.google.com/trending/rss?geo=VN` và trang Explore);
   - tiêu đề các bài báo VN đang dẫn đầu về sự kiện;
   - tìm kiếm YouTube VN (gõ tay xem kết quả, không dùng autocomplete API).

   Ghi cụm từ khóa chính (vd. "Binance bị hack", "giá xăng hôm nay", "giá điện giảm", "giá vàng SJC") kèm bằng chứng: URL, trang, số liệu Trends nếu có.
2. **Title mới.**
   - **Từ khóa chính đặt ở 3–4 từ đầu**, rồi tới con số sốc hoặc mâu thuẫn thật.
   - ≤ 60 ký tự, tiếng Việt có dấu.
   - Giật gân nhưng **đúng sự thật**: mọi số phải có trong facts, không bịa, không phóng đại, không hứa điều video không trả lời.
   - Mỗi Short 2 phương án, đánh dấu phương án khuyên dùng.
3. **Mô tả.** 2 câu đầu chứa từ khóa chính và phụ, giữ nguyên phần nguồn, ghi công và câu miễn trừ CK đang có trong spec. Kèm 3–5 hashtag: hashtag kênh có sẵn + từ khóa sự kiện.
4. **Tag:** 8–12 tag (từ khóa chính, phụ, tên riêng).
5. Kiểm trùng title với các video đã có của kênh (`data/channel_titles/*.json`, `state.sqlite`).

## Định dạng `GH-33-titles.json`
`[{slug, keyword_primary, keyword_evidence, title_recommended, title_alt, description_head, hashtags, tags}]`
