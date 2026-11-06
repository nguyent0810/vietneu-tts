# GH-228: Đông Lăng (CL Long 3), bước 3 (kịch bản `script.md`)

**Đọc trước:**
- `CLAUDE.md`: quy trình một Long, bước 3.
- Skill `../.claude/skills/long-script/SKILL.md` và các file trong `references/` (story, line-rules, evidence, sources, formats).
- `motion/long/RETENTION.md`.
- `data/long/dong-lang/plan.md` (đã duyệt).
- `data/long/dong-lang/visual_plan.md`: nhịp hình từng chương. Lời phải khớp hình đã thiết kế.
- **Mẫu định dạng:** `data/long/bao-thanh-thien/script.md` và `factcheck.md`. Long CL vừa làm, đã qua `factcheck_lint` 0 lỗi.

**Việc:**
1. Viết `data/long/dong-lang/script.md`:
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
3. Viết `data/long/dong-lang/factcheck.md` theo mẫu Bao Thanh Thiên. Mỗi số, ngày và trích dẫn trong script phải có một dòng. Chạy `python motion/long/factcheck_lint.py hoa-than` (hoặc lệnh lint trong `publish_long.py`; đọc code để biết cách gọi) cho tới khi **0 lỗi**.
4. Chạy `python motion/long/script_lines.py dong-lang` hoặc công cụ đếm âm tiết mà Bao đã dùng (xem `CLAUDE.md`, `long-script` skill) để báo số âm tiết.
5. Đề xuất 2–3 tiêu đề vào báo cáo, theo khuôn thắng của CL: `[PHIM] Ngoài Đời Thật: [người] — [nghịch lý có số]`, tối đa 100 ký tự, phần gây tò mò nằm trong 60 ký tự đầu. Đề xuất 2–3 phương án cho Đông Lăng. Mọi dữ kiện trong tiêu đề phải có câu dẫn trong lời đọc.

**Được ghi:**
- `data/long/dong-lang/script.md`;
- `data/long/dong-lang/factcheck.md`;
- báo cáo `docs/pm/tickets/GH-228-donglang-script-report.md`.

Ghi UTF-8. Không sửa code, không TTS, không render, không commit.

**Báo cáo:**
- số âm tiết, số chương, số dòng;
- kết quả `factcheck_lint`;
- danh sách dữ kiện còn chưa chắc;
- tiêu đề đề xuất, mỗi dữ kiện kèm câu dẫn.

## Bổ sung cho Đông Lăng (Lead, 07/11)

**Mẫu giọng:** `data/long/hoa-than/script.md`. Bản v2 này đã qua review, đọc kỹ cách mở chương và cách kể các nguồn lệch nhau.

**Phải tránh (lỗi của Hòa Thân bản 1):**
- không đọc tên "Wikipedia", "bài tiếng Việt/Anh", "bách khoa";
- không để ghi chú sản xuất lọt vào lời ("plan", "lời đọc", "trên hình", "mô-típ");
- không báo trước cấu trúc chương.

Gate `script_lines` có cổng `META_LEAK` chặn các lỗi này. Chạy gate trước khi nộp.

**Tiêu đề:** theo khuôn CL (`docs/pm/title-patterns-cl.md`), phần gây tò mò nằm trong khoảng 45 ký tự đầu.

**Không mô tả chi tiết cảnh phá quan tài hay làm nhục thi thể.** Kể sự kiện ở mức hồ sơ, đủ cho YouTube và người xem.
