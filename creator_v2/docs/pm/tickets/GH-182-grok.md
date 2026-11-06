# GH-182 (phân tích và viết): MIM, brief lô Long tháng 12 và bao bì cho Long chưa đăng

Làm trong `creator_v2/`. Đọc `CLAUDE.md`, `AGENTS.md`, issue #182 và kế hoạch #177 trước.

## Phạm vi
- Chỉ được ghi `docs/pm/2026-11-mim-thang12-brief.md` và file báo cáo.
- Không được: sửa spec, sửa video, upload, đổi lịch, commit, đọc thư mục credentials.

## Dữ liệu
- `docs/pm/2026-11-05-analytics-api-3-kenh.md` (số liệu API).
- Kế hoạch trong issue #177: MIM có 91% impressions Long từ Đề xuất, CTR khoảng 1%. Chủ đề thắng là lừa đảo, AI và việc làm: AI Giả Giọng 14,2 giờ, AI Cướp Việc 11 giờ, Luật sư nộp vụ ChatGPT bịa 10,4 giờ.
- `state.sqlite`, bảng `item`, channel MIM, kind `long`: các Long đã hẹn lịch tới 01/12. Chỉ đọc. Long CHƯA lên sóng là có `publish_at` sau hôm nay.
- `data/long/mim-*/spec.json` (`youtube.titles`, `thumb`).

## Việc
1. **Brief lô tháng 12:** 8 Long, 10–15 phút, khoảng 60% về AI, lừa đảo và an toàn số. Mỗi đề tài ghi:
   - sự kiện thật làm móc mở đầu, kèm nguồn có URL;
   - vì sao người xem Việt quan tâm;
   - 2–3 Short đi kèm, ghi rõ loại S hay L.
   Không bịa số liệu.
2. **Bao bì Long chưa đăng:** mỗi video đề xuất 2 tiêu đề mới và 1 ý thumbnail (chữ ≤ 4 từ, hình gì), nhắm CTR từ Đề xuất. Lý do ngắn gọn.
   - Không giật tít sai sự thật. Không dùng các cụm "Bí ẩn", "Sự thật kinh hoàng".
   - Chữ trên hình theo phong cách điện ảnh của kênh. Không chữ máy móc.

## Báo cáo
Ghi `docs/pm/tickets/GH-182-report.md`: tóm tắt, các giả định, những chỗ thiếu dữ liệu.
