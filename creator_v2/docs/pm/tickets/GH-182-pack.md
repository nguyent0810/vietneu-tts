# GH-182 (phần B): soát tiêu đề MIM với lời đọc

**Mục tiêu:** với 5 Long MIM chưa đăng, chọn MỘT tiêu đề mới cho mỗi video. Mỗi chữ số, năm, tên trong tiêu đề phải có trong lời đọc của video đó.

**Video (theo thứ tự ưu tiên):** mim-may-thang-poker (lên 08/11), mim-siri-susan-bennett, mim-ai-khuon-mat, mim-may-choi-game, mim-jobs-1985.

**Đầu vào (chỉ đọc):**
- `docs/pm/2026-11-mim-thang12-brief.md`, bảng mục B (tiêu đề đang hẹn và 2 phương án cho mỗi video).
- `data/long/<topic>/script.md` (lời đọc) và `data/long/<topic>/spec.json`.

**Việc:**
1. Với mỗi phương án tiêu đề: liệt kê từng dữ kiện (số, năm, tên, hành động) và dẫn câu trong script.md chứng minh nó. Dữ kiện không có trong script thì ghi KHÔNG CÓ.
2. Chọn một tiêu đề cho mỗi video: dữ kiện đủ hết, tối đa 60 ký tự, tiếng Việt có dấu. Được sửa nhẹ phương án cho đúng lời đọc. Nếu không phương án nào đạt, giữ tiêu đề cũ và ghi lý do.
3. Thumbnail: ghi chữ đề xuất (2–3 từ) và xác nhận chữ đó khớp lời đọc. Riêng mim-may-choi-game: kiểm số "45.000 NĂM" trên thumb hiện tại có trong script không.
4. mim-jobs-1985: kiểm tra file thumb có trong `output/long/mim-jobs-1985/` không và ghi lại.

**Được ghi:** chỉ `docs/pm/tickets/GH-182-pack-report.md`. Không sửa spec, không đăng, không commit, không đổi lịch.

**Báo cáo:** một bảng cho mỗi video (tiêu đề chọn, số ký tự, dữ kiện kèm câu dẫn, chữ thumb), cuối báo cáo liệt kê phần chưa chắc.
