# GH-179: Hòa Thân, bước 3 (kịch bản `script.md`)

**Đọc trước:**
- `CLAUDE.md`: quy trình một Long, bước 3.
- Skill `../.claude/skills/long-script/SKILL.md` và các file trong `references/` (story, line-rules, evidence, sources, formats).
- `motion/long/RETENTION.md`.
- `data/long/hoa-than/plan.md` (đã duyệt).
- `data/long/hoa-than/visual_plan.md`: nhịp hình từng chương. Lời phải khớp hình đã thiết kế.
- **Mẫu định dạng:** `data/long/bao-thanh-thien/script.md` và `factcheck.md`. Long CL vừa làm, đã qua `factcheck_lint` 0 lỗi.

**Việc:**
1. Viết `data/long/hoa-than/script.md`:
   - 14 chương theo plan, 5.500–7.000 âm tiết (25–32 phút);
   - định dạng giống `bao-thanh-thien/script.md` (tiêu đề chương, dòng đọc, dấu `‖`, bảng nguồn từng chương);
   - lộ trình mở bài **Nghịch lý**, không dùng "Hai hồ sơ" hay "trả lời ba câu hỏi";
   - cold open 22/2/1799, dừng ở đỉnh.
2. **Luật dữ kiện, bắt buộc:**
   - Mọi số, ngày, tên và trích dẫn phải có trong một nguồn bạn đã mở thật. Ghi URL vào bảng nguồn.
   - Các con số tài sản đang lệch nhau giữa các nguồn: lời đọc phải nói rõ là "theo …", và đặt các con số cạnh nhau. **Không** khẳng định một tổng tài sản.
   - "Lụa vàng" chỉ đưa vào lời khi có nguồn thứ hai ngoài Wikipedia.
   - Mỗi dòng "TRÍCH DỊCH" phải có nguyên văn và URL.
   - Không dựng cảnh hành hình, không mô tả chi tiết lăng trì hay thắt cổ.
   - Không kéo sang chính trị hôm nay.
   - Danh sách thiếp trên Wikipedia VI không được đưa vào (plan đã cấm).
3. Viết `data/long/hoa-than/factcheck.md` theo mẫu Bao Thanh Thiên. Mỗi số, ngày và trích dẫn trong script phải có một dòng. Chạy `python motion/long/factcheck_lint.py hoa-than` (hoặc lệnh lint trong `publish_long.py`; đọc code để biết cách gọi) cho tới khi **0 lỗi**.
4. Chạy `python motion/long/script_lines.py hoa-than` hoặc công cụ đếm âm tiết mà Bao đã dùng (xem `CLAUDE.md`, `long-script` skill) để báo số âm tiết.
5. Đề xuất 2–3 tiêu đề vào báo cáo, theo khuôn thắng của CL: `[PHIM] Ngoài Đời Thật: [người] — [nghịch lý có số]`, tối đa 100 ký tự, phần gây tò mò nằm trong 60 ký tự đầu. Lead đang nghiêng về "TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Hòa Thân Bị Ép Chết 15 Ngày Sau Khi Càn Long Mất". Mọi dữ kiện trong tiêu đề phải có câu dẫn trong lời đọc.

**Được ghi:**
- `data/long/hoa-than/script.md`;
- `data/long/hoa-than/factcheck.md`;
- báo cáo `docs/pm/tickets/GH-179-hoathan-script-report.md`.

Ghi UTF-8. Không sửa code, không TTS, không render, không commit.

**Báo cáo:**
- số âm tiết, số chương, số dòng;
- kết quả `factcheck_lint`;
- danh sách dữ kiện còn chưa chắc;
- tiêu đề đề xuất, mỗi dữ kiện kèm câu dẫn.
