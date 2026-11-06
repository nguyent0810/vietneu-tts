# Giới hạn độ dài tiêu đề theo kênh (thay cho 60 cố định)

**Bối cảnh (Lead, 06/11):** `scripts/long_gate.py` dòng 205–207 chặn mọi tiêu đề Long dài trên 60 ký tự. Với CL, dữ liệu thật trái hẳn: hai Long thắng lớn nhất dài 85 và 88 ký tự ("TAM GIÁC VÀNG Ngoài Đời Thật: Khun Sa — Ông Vua Thuốc Phiện Mỹ Treo Thưởng 2 Triệu Đô", "BẾN THƯỢNG HẢI Ngoài Đời Thật: Đỗ Nguyệt Sanh – Từ Cậu Bé Bán Lê Đến Ông Trùm Thanh Bang"). Hồ sơ kênh `library/channels/<kenh>.yaml` đã có `luat_noi_dung.title_max`, nhưng code không đọc.

**Áp dụng ngoại lệ AGENTS.md.** Được sửa:
- `creator_v2/scripts/long_gate.py`;
- `library/channels/cl.yaml` (chỉ `luat_noi_dung.title_max`);
- test mới `creator_v2/tests/test_title_max_per_channel.py`;
- báo cáo `creator_v2/docs/pm/tickets/GH-title-max-report.md`.

Ghi file bằng Python, `encoding="utf-8"`.

**Việc:**
1. `long_gate.py` đọc `title_max` của kênh qua `library/tools/channel_profile.py` (xem `load_profile` / `resolve`; hồ sơ kênh lấy từ spec hoặc tham số kênh mà gate đang dùng). Không đọc được thì mặc định 60 và in cảnh báo.
2. Sửa lỗi Codex đã báo: `youtube.titles[0]` là chuỗi rỗng thì quay về `spec.title`, cùng logic với `chosen_title` trong `motion/long/publish_long.py`. Nếu import gọn được thì dùng lại hàm đó.
3. `cl.yaml`: `title_max` đổi từ 60 thành 100 (giới hạn của YouTube). MIM và CK giữ 60.
4. Thông báo lỗi ghi rõ kênh và giới hạn, ví dụ "tiêu đề 84 ký tự > 60 (MIM)".
5. Test:
   - CL 84 ký tự qua;
   - MIM 61 ký tự bị chặn;
   - `titles[0]` rỗng thì dùng `title`;
   - hồ sơ không đọc được thì giới hạn 60.
6. `python -m pytest creator_v2/tests -q -k "gate or title"` và `tests/test_channel_profile*.py` (gốc repo, nếu có) phải xanh.

**Không:** commit, upload.
