# GH-179: Hòa Thân, bước 2 (tư liệu trước, chữ sau)

Đọc `CLAUDE.md` (mục "Quy trình một Long", bước 2), `data/long/hoa-than/plan.md` (đã duyệt) và `motion/long/SOURCES.md`.

**Việc:**
1. Chạy `python motion/long/research_long.py hoa-than` với các bài Wikipedia liên quan. Ít nhất có:
   - Heshen
   - Prince Gong Mansion
   - Qianlong Emperor
   - Jiaqing Emperor
   - Liu Yong (Qing dynasty)
   - Ji Xiaolan
   - Princess Hexiao
   - Qing dynasty
   - Eight Banners
   - Forbidden City

   Thêm bài nếu thiếu ảnh cho một chương trong plan.
2. Bổ sung ảnh ngoài Commons bằng `python motion/long/media_search.py search hoa-than "<từ khóa>"`, nguồn artic, europeana, wellcome. Gợi ý từ khóa: "Qing dynasty court painting", "Qianlong", "Beijing 18th century", "Qing official portrait", "silver tael", "Qing palace". Chỉ tải ứng viên có giấy phép tự do, bằng lệnh `get`.
3. Mở các contact sheet `output/long/hoa-than/sheet_*.jpg` và soát bằng mắt:
   - loại ảnh diễn viên, still phim, poster, ảnh không đúng người hoặc không đúng thời kỳ;
   - ghi số ảnh dùng được cho từng chương trong dàn 14 chương của plan.
4. Mục tiêu khoảng 50 ảnh tự do dùng được trở lên. Thiếu thì ghi chương nào thiếu và đề xuất cách bù: bản đồ, hồ sơ, chart. Không dùng ảnh AI cho người hay sự kiện thật.

**Được ghi:** `output/long/hoa-than/*` (do script tạo) và báo cáo `docs/pm/tickets/GH-179-hoathan-research-report.md`, ghi UTF-8. Không sửa code, không viết kịch bản, không render, không commit.

**Báo cáo:**
- tổng ảnh tự do dùng được, chia theo nguồn và giấy phép;
- bảng chương × số ảnh;
- danh sách ảnh đã loại kèm lý do;
- các chương thiếu ảnh.
