# GH-132: thẻ duyệt phương án cho Long (chép từ nhánh nghiên cứu)

Code thẻ duyệt đã viết và review xong ở nhánh `origin/research/hitl-card`: `research/hitl/card.py`, `test_card.py`, `REPORT_card.md`. Lệnh render/decide/verify, hash SHA-256 của candidate, lịch sử quyết định append-only. Xem bằng `git show origin/research/hitl-card:research/hitl/card.py`. **Chép sang và chỉnh cho Long của creator_v2. Không viết lại từ đầu.**

**File được tạo hoặc sửa (worktree riêng):**
- `scripts/review_card.py`: bản chép từ `card.py`, đã chỉnh;
- `tests/test_review_card.py`: chép từ `test_card.py` và thêm test mới;
- báo cáo `docs/pm/tickets/GH-132-report.md`.

Không sửa `publish_long.py`, `factory/*` hay engine.

**Bắt buộc về mã hoá:** mọi file có tiếng Việt ghi bằng Python, `encoding="utf-8"`. KHÔNG dùng PowerShell `Set-Content`, `Out-File` hay `echo` để ghi file. Trước khi kết thúc, chạy:
`python -c "import subprocess,sys;d=subprocess.run(['git','diff'],capture_output=True,text=True,encoding='utf-8').stdout;sys.exit('MẤT DẤU' if '???' in d or 'Kh?ng' in d else 0)"`
rồi kiểm cả file báo cáo. Có lỗi thì sửa lại cho đúng dấu.

**Chỉnh cho Long:**
1. `python scripts/review_card.py init <topic>`:
   - tạo `data/long/<topic>/candidates.json` từ spec;
   - mỗi phần tử `youtube.titles` là một phương án tiêu đề;
   - thumbnail lấy từ `output/long/<topic>/t*.jpg` nếu có, ngược lại từ `motion/long/thumbs/<topic>_t*.html`;
   - có chỗ cho `claims` (dữ kiện kèm câu dẫn trong `script.md`) và `flags` của reviewer, để Grok điền vào.
2. `render <topic>`:
   - thẻ HTML và Markdown tại `output/long/<topic>/review_card.html` và `.md`;
   - các phương án đặt cạnh nhau, hiện số ký tự của tiêu đề so với `title_max` của kênh (đọc `library/channels/<kenh>.yaml` như `scripts/long_gate.py`);
   - kèm ảnh thumbnail và bản thu nhỏ 168 px, như bản gốc.
3. `decide <topic> --approve <candidate_id> [--edits ...] --by <tên>`: giữ luật và lịch sử của bản gốc. Khi APPROVE, in ra lệnh hoặc đoạn JSON để Lead đặt `youtube.titles[0]` cho đúng phương án đã chọn. **Không tự ghi spec**; Lead tự áp dụng.
4. `verify <topic>`: giữ nguyên ý nghĩa `stale` / `not_approved` / `invalid`.
5. Test: giữ các test gốc, thêm:
   - `init` từ một spec giả;
   - `render` có đủ các phương án và hiện cảnh báo khi vượt `title_max`.

   Chạy `python -m pytest tests/test_review_card.py tests/test_console.py -q`. Script CLI phải gọi `factory.console.utf8_console()`.

**Không:** commit, upload.
