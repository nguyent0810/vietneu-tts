# GH-180: lắp 9 Short CK (17–19/11) từ lời của Grok

**Đầu vào:** `docs/pm/tickets/GH-180-shorts-lines.md` (9 Short đã viết: hook, lời, câu chốt, tiêu đề, nguồn, cảnh giả định) và báo cáo `docs/pm/tickets/GH-180-shorts-report.md`.

**Đọc:**
- `motion/stier/README.md`;
- skill `../.claude/skills/shorts-studio/SKILL.md`;
- 3 spec CK gần nhất trong `data/stier/specs/`: `ck-e5-luong-25-trieu-thue-giam-13-lan.json`, `ck-e6-rut-mot-lan-200-trieu.json`, `ck-a2-luong-toi-thieu-52-so-voi-10.json`. Chép đúng cấu trúc, theme, look và các trường.

**Việc:**
1. Tạo 9 spec `data/stier/specs/<slug>.json`, slug lấy theo file lời. Lịch:
   - 17/11: Short 1, 4, 7;
   - 18/11: Short 2, 5, 8;
   - 19/11: Short 3, 6, 9;
   - giờ trong ngày (VN) 17:30, 19:00, 22:00 theo thứ tự trên. Ghi `publish_at` UTC giống các spec mẫu.
2. Lời đọc chép **nguyên văn** từ file lời, không cắt câu, không rút gọn. Cảnh gắn câu theo cách các spec mẫu làm.
3. Cảnh nào là ví dụ giả định thì thêm `"hypo": true` (nhãn mới #173). Bỏ chữ "giả định" khỏi `sub` hoặc `note` cỡ nhỏ ở cảnh đó.
4. Mô tả kèm nguồn URL lấy từ file lời. Short CK bắt buộc có câu miễn trừ "Nội dung giáo dục, không phải tư vấn đầu tư." (xem `motion/stier/enqueue_ck.py`). Short loại L ghi Long nối tới.
5. Chạy `python motion/stier/build.py --preflight <slug>` cho từng spec đến khi OK. Preflight không còn cảnh báo hypo.

**Bắt buộc về mã hoá:** viết một script Python sinh spec bằng `json.dump(..., ensure_ascii=False)` và `open(..., "w", encoding="utf-8")`. Không dùng PowerShell `Set-Content`/`echo`, không dán tiếng Việt qua shell. Trước khi kết thúc, chạy:
`python -c "import glob,sys;bad=[f for f in glob.glob('data/stier/specs/*.json') if '???' in open(f,encoding='utf-8').read() or 'Kh?ng' in open(f,encoding='utf-8').read()];print(bad);sys.exit(1 if bad else 0)"`

**Được ghi:** 9 spec mới, script sinh spec tạm (xoá sau khi xong hoặc đặt ở `docs/pm/tickets/GH-180-gen_specs.py`), báo cáo `docs/pm/tickets/GH-180-specs-report.md` (UTF-8). Không render, không enqueue, không upload, không sửa spec cũ, không commit.
