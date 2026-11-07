# GH-228: lô Short CL 2 (14 Short, 16–22/11, 2 mỗi ngày)

Đọc trước: brief lô 1 `docs/pm/tickets/GH-228-cl-shorts1-agy.md` (công thức, nguồn đọc, luật mỗi Short). Lô 2 theo đúng các luật đó, CỘNG các bài học Lead rút ra khi soát lô 1:
- `docs/pm/tickets/GH-228-cl-respec-codex.md`: ≥ 4 ảnh khác nhau mỗi bài, một ảnh tối đa 2 cảnh;
- `docs/pm/tickets/GH-228-cl-variety-codex.md`: không chữ slam chung kiểu "DẤU VẾT", cụm slam lấy từ lời của chính bài; không 2 bài nào cùng chuỗi loại cảnh; không khung mốc năm nhỏ trên nền trống;
- không dùng lại ảnh mà 12 Short lô 1 đã dùng (danh sách ở `docs/pm/tickets/GH-228-cl-shorts1-report.md`, kiểm `src`/`local` trong 12 spec đó), và không ảnh nào dùng ở 2 bài trong lô 2;
- ảnh FBI/hồ sơ chung không được dùng làm ảnh mở ở quá 1 bài.

**14 Short:**
- **L, 6 bài** (chi tiết thật có trong `script.md` + `factcheck.md` của Long, không phải trailer):
  - 4 nối Hòa Thân (`data/long/hoa-than/`, Long đăng 15/11 21:00 VN). Không trùng 3 bài Hòa Thân lô 1 (cl-hoa-than-hai-muoi-toi, cl-hoa-than-doi-ten-phu, cl-hoa-than-thi-ve);
  - 2 nối Bao Thanh Thiên (`data/long/bao-thanh-thien/`), không trùng 3 bài lô 1 (cl-bao-*).
- **S, 8 bài:** vụ án hoặc nhân vật mới, chưa có Short trên kênh (grep tiêu đề, tên người trong `data/stier/specs/`). Ưu tiên đề có ảnh Commons tự do ≥ 4 ảnh. Trải nhiều nước và thời kỳ. Mỗi bài có nguồn URL mở được.

**Lịch** (`publish_at` UTC): 16/11 đến 22/11, mỗi ngày 12:00 và 19:00 giờ VN (05:00Z và 12:00Z). Bài L Hòa Thân không trước 16/11. Xen kẽ L và S.

**Lời:** hook ≤ 9 từ, 25–40 giây, không câu khái quát không nguồn ("nhiều người", "hầu hết"); truyền thuyết thì nói "theo giai thoại". Không mô tả bạo lực hay xác chết. Tiêu đề ≤ 60 ký tự.

**Việc:** viết 14 spec `data/stier/specs/<slug>.json` (slug bắt đầu `cl-`) bằng Python `json.dump(ensure_ascii=False)`, `encoding="utf-8"`; chạy `PYTHONIOENCODING=utf-8 python motion/stier/build.py --preflight <slug>` tới khi OK; chạy kiểm mất dấu (grep "?" giữa chữ trong lời). Ghi `docs/pm/tickets/GH-228-cl-shorts2-lines.md`: lời, nguồn, loại S/L, chuỗi loại cảnh, cụm slam của từng bài.

**Không:** render, enqueue, upload, commit, đổi nhánh git, sửa spec lô 1.

**Báo cáo** `docs/pm/tickets/GH-228-cl-shorts2-report.md` (UTF-8): bảng slug, loại, ngày giờ, số ảnh khác nhau, chuỗi loại cảnh, kết quả preflight.
