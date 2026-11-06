# GH-182 — báo cáo Grok

**Ticket:** `docs/pm/tickets/GH-182-grok.md`  
**Ngày:** 06/11/2026  
**File được ghi:** `docs/pm/2026-11-mim-thang12-brief.md`, file này.

## Đã làm

1. Đọc `CLAUDE.md`, `AGENTS.md`, issue #182, kế hoạch #177, số liệu API `docs/pm/2026-11-05-analytics-api-3-kenh.md`, chiến lược 45 ngày, brief MIM 01–07/12 bản 1, bước R 28/10, luật Short S/L, #173 (chữ điện ảnh).
2. Mở `state.sqlite` **chỉ đọc** (`file:state.sqlite?mode=ro`). MIM `kind=long`: 29 dòng, tất cả `stage=published`. 16 bài có `publish_at` từ 06/11 20:00 VN tới 01/12. Brief bảo Long chưa lên sóng = `publish_at` **sau hôm nay** → loại `mim-ai-chat-privacy` (06/11), còn **15** bài 08/11–01/12.
3. Đọc `youtube.titles`, `thumb`, `summary` trong `data/long/mim-*/spec.json` và chữ trên HTML thumbnail (15 bài; Jobs 1985 **không** có file thumb).
4. Viết brief lô **8 Long** 10–15 phút, 5/8 nhóm AI–lừa đảo–an toàn số, mỗi bài một sự kiện có ngày + URL, 2–3 Short S/L.
5. Đề xuất **2 tiêu đề + 1 ý thumbnail** cho 15 Long chưa lên sóng, nhắm CTR Đề xuất. Không giật tít sai, không dùng "Bí ẩn" / "Sự thật kinh hoàng", chữ thumb ≤ 4 từ.

**Không làm (đúng phạm vi):** không sửa spec/video, không upload, không đổi lịch, không commit, không đọc credentials, không ghi `state.sqlite`.

## Lệnh đã chạy

- `gh issue view 182 --repo nguyent0810/vietneu-tts`
- `gh issue view 177 --repo nguyent0810/vietneu-tts`
- `gh issue view 173 --repo nguyent0810/vietneu-tts`
- Python đọc `state.sqlite` URI mode=ro (schema `item`, liệt kê MIM long, MIM short tương lai).
- Python đọc `spec.json` và HTML thumbnail.
- Mở URL (06/11): VnExpress Binance; VnExpress Musk; VnExpress Altman RAM; CoinDesk Cornell/Yale; CERN licensing-web; Wikipedia Moffatt v. Air Canada; CRT item 525448 (thân rỗng); CanLII k2spq (lỗi); HK LegCo 26/6/2024; info.gov.hk deepfake.

## Giả định

- Hôm nay = **06/11/2026**. `publish_at` sau ngày này = chưa lên sóng. Chat-privacy lên tối nay nên không đề xuất đổi bao bì.
- `stage=published` nghĩa là đã upload private + hẹn giờ, video vẫn chưa công khai nếu `publish_at` còn ở tương lai.
- CTR ~1% và 91% impressions Đề xuất lấy từ gói Studio trong #177. API 05/11 **không** có impressions/CTR (400 "query is not supported").
- Nhịp 2 Long/tuần từ 02/12 khớp chiến lược 45 ngày và câu "hẹn lịch từ 02/12" của #182. Thứ tự D1–D8 là đề xuất; chưa ghi lịch.
- Jobs 1985 (`publish_at` 01/12) thuộc lịch cũ, không nằm trong 8 bài mới. Brief 28/10 (M2 Web, M3 LeCun, M4 deepfake, M5 luật AI) được giữ và bổ sung Binance, agent, Air Canada, RAM.
- Góc Binance của MIM là cơ chế + bẫy ăn theo. Góc giá/token để CK (`ck_19` trong GH-31).
- Chữ thumbnail "điện ảnh" = thẻ tiêu đề phim của kênh (#173): một cụm ngắn, font/màu theme, không ô cảnh báo, không chữ công cụ.

## Chỗ thiếu dữ liệu

| Thiếu | Hệ quả |
|---|---|
| API không có impressions, CTR, Shown in feed | Bao bì nhắm CTR Đề xuất dựa trên Studio #177, không đo được từng video chưa đăng. |
| Mẫu Long công khai n=13 | Công thức tiêu đề là giả thuyết để thử, không phải quy luật. |
| CanLII / thân CRT của *Moffatt v. Air Canada* không lấy được 06/11 | D5 dựa Wikipedia + CBC/BBC. R phải mở 2024 BCCRT 149 trước khi viết. |
| vneconomy Luật AI trả về rỗng 06/11 | Ngày thông qua/hiệu lực lấy từ R 28/10. R mở lại vanban.chinhphu.vn / Công báo. |
| Thông cáo FBI gốc vụ Binance | D2 dẫn VnExpress (FBI 31/10, TraderTraitor) + GH-31 (CoinDesk, The Register). R mở fbi.gov. |
| arXiv 2610.35835 chưa mở toàn văn | D3 lấy số 9/10, 5/10, Countersign từ CoinDesk 01/11. R mở paper. |
| `mim-jobs-1985` không có HTML thumb | Ý thumb "BỊ GẠT" là đề xuất; chưa dựng. |
| Thumb "45.000 NĂM" của `mim-may-choi-game` không khớp summary | Không dùng số này trong tiêu đề mới. |
| Pilot hook MIM 13–18/11 chưa có kết quả 7 ngày | Short L của lô 12 chỉ ghi trên giấy; dựng sau pilot. |
| Số 8.000 tỷ / 4.200 vụ là **tổng** lừa đảo trực tuyến 2025, không tách deepfake | Brief đã ghi. Không đọc thành "thiệt hại deepfake 8.000 tỷ". |
| 5% thời gian RAM là lời Altman trên Cheeky Pint, không phải số đo kênh | Brief đã ghi. |
| CL không có credential API | Không dùng số CL để suy MIM, trừ công thức "Ngoài Đời Thật" đã có trong #177. |

## Kết

Brief nằm ở `docs/pm/2026-11-mim-thang12-brief.md`. Chờ chủ kênh duyệt từng cụm (lô 8 bài, từng tiêu đề/thumb video chưa đăng) rồi mới sang R/W và đổi bao bì qua API. Ticket này dừng ở giấy.
