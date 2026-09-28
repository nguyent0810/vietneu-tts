# 09: Lấy retention curve + traffic source vào baseline raw

**Spec:** `../spec.md` — Retention curve + traffic source. Quyết định: D20, D36, D50.

**What to build:** Một lệnh (người vận hành chạy, dùng xác thực YouTube hiện có) lấy retention curve (tỷ lệ người xem theo vị trí trong video) và phân bố traffic source cho từng Short đã đăng, ghi vào thư mục baseline raw local (gitignore). Dùng chung cách gọi API và xử lý lỗi tạm thời của luồng sync hiện có. Video không có dữ liệu được ghi là thiếu, không làm hỏng lần chạy. Không đổi payload ingest của Hub.

**Blocked by:** None (can start immediately)

**Status:** done (grok review OK)

- [x] Hàm lấy retention curve và hàm lấy traffic source đặt cạnh hàm lấy báo cáo ngày của luồng sync
- [x] Parse đúng kết quả API cho từng video; video thiếu dữ liệu ghi lý do
- [x] Lỗi tạm thời được retry như luồng sync hiện tại; lỗi vĩnh viễn được ghi lại và chạy tiếp video khác
- [x] Kết quả ghi vào baseline raw, có version và thời điểm lấy
- [x] Test với hàm gọi API giả lập, theo mẫu test sync hiện có
