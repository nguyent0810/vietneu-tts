# GH-228: lô Short CL 1 (14 Short, 09–15/11, 2 mỗi ngày)

**Bối cảnh:** plan tháng 11 (`docs/pm/2026-11-plan-thang-11.md`) và số liệu CL (`docs/pm/2026-11-06-cl-analytics.md`). Các Short CL đứng đầu 28 ngày qua, mỗi bài trên 1.000 lượt xem:
- "Mắt xích còn thiếu lừa cả giới khoa học suốt 41 năm"
- "Công chúa đảo Javasu hóa ra là con gái thợ sửa giày"
- "Ned Kelly: tên cướp mặc áo giáp làm từ lưỡi cày"
- "Vụ Brink's Boston 1950 và sáu năm im lặng"

Công thức chung: một chi tiết lạ có thật, một nhân vật hoặc vụ án, kết bằng một cú đảo.

**Đọc:**
- spec CL mẫu trong `data/stier/specs/`: `unabomber.json` và 3–4 spec mới nhất có bản dựng trong `output/stier/<slug>/final_sheet.jpg`. Mở contact sheet để thấy kiểu hình đạt;
- `motion/stier/README.md`;
- skill `../.claude/skills/shorts-studio/SKILL.md`;
- `docs/pm/2026-10-12-shorts-analysis.md` §7 (8 luật Short).

**14 Short:**
- **L, 8 bài:**
  - 3 nối về `data/long/bao-thanh-thien/script.md` (đăng 08/11);
  - 3 nối về `data/long/hoa-than/script.md` (đăng 15/11);
  - 1 nối về Khun Sa, 1 nối về Đỗ Nguyệt Sanh. Tìm `script.md` trong `data/long/` theo tên.

  Mỗi bài lấy một chi tiết thật đã có trong kịch bản và `factcheck.md` của Long đó. Không phải trailer.
- **S, 6 bài:** vụ án hoặc nhân vật mới, chưa có Short trên kênh. Kiểm trùng tiêu đề bằng `grep` trong `data/stier/specs/`. Mỗi bài có nguồn mở được.

**Mỗi Short:**
- hook ≤ 9 từ;
- 25–40 giây;
- tiêu đề ≤ 60 ký tự;
- ≥ 5 loại cảnh theo theme CL `case`;
- số hay ngày chính hiện cỡ lớn;
- ảnh tư liệu tự do (`motion/long/SOURCES.md`). Ảnh AI chỉ loại minh họa chung tag `minh_hoa_chung` từ kho (`python ../library/tools/assets.py find`), không vẽ người thật;
- mô tả có nguồn URL. Bài L ghi Long nối tới.

**Lịch:** `publish_at` UTC cho 09–15/11, mỗi ngày 2 bài lúc 12:00 và 19:00 giờ VN. Xen kẽ L và S.

**Việc:** viết thẳng 14 spec `data/stier/specs/<slug>.json` bằng Python `json.dump(ensure_ascii=False)`, `encoding="utf-8"`, rồi chạy `python motion/stier/build.py --preflight <slug>` cho tới khi OK. Ghi kèm `docs/pm/tickets/GH-228-cl-shorts1-lines.md`, liệt kê lời, nguồn và loại S/L từng bài.

**Không:** render, enqueue, upload, commit.

**Báo cáo** `docs/pm/tickets/GH-228-cl-shorts1-report.md` (UTF-8): bảng slug, loại, ngày giờ, số từ, kết quả preflight.
