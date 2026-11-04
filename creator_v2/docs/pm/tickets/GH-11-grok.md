# GH-11 · Điều tra cách tạo `final.mp4` của `mim-macintosh-1984` (Grok, chỉ đọc)

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/11

## Phạm vi quyền

- **Chỉ đọc.** Chỉ được ghi một file: `docs/pm/tickets/GH-11-report.md`.
- Không sửa code, không chạy render, không chạy git ở dạng ghi. Được dùng `git log`, `git show`, `git reflog`.
- Không đọc `.youtube_channels`, `vietneu-tts/.youtube_channels` hay bất kỳ thư mục khóa hoặc credentials nào.

## Câu hỏi

File `output/long/mim-macintosh-1984/final.mp4` (27/10/2026 05:33) có tồn tại. Nhưng từ commit e405989 (12/10), `build_long.py render` (không có `--draft`) và `final` đều gọi `_refuse_floor`, và topic này không qua `floor`. Vậy file được tạo bằng đường nào?

## Gợi ý chỗ tìm

Chỉ ghi điều có bằng chứng.

- Mốc thời gian (mtime) của các file trong `output/long/mim-macintosh-1984/`: từng chương `chNN/*.mp4`, `concat*.txt`, `final.mp4`, log nếu có.
- `git log --since=2026-10-25 --until=2026-10-28` của `motion/long/build_long.py`, `motion/long/floor.py`, `scripts/`. Có bản nào tạm bỏ hoặc nới `floor` không?
- Các script khác có ghép chương hoặc render:
  - `scripts/*long*`, `scripts/codex_ticket.py`, `motion/long/*.py`;
  - grep `concat`, `ffmpeg`, `final.mp4`.
- Worktree hoặc repo cạnh bên (`<thư mục làm việc>/wt-studio`, `<thư mục vietneu-tts>`): có `build_long.py` nào không có `floor`? Có output nào trỏ tới topic này?
- Ticket và báo cáo quanh 26–27/10:
  - `docs/pm/tickets/2026-10-26-codex-pilot/*`
  - `.tickets/*`
  - `docs/pm/*2026-10-2[67]*`

## Báo cáo

Ghi vào `GH-11-report.md`:

1. **Kết luận** theo một trong ba mức:
   - đã xác định được, kèm bằng chứng;
   - có khả năng, kèm lý do;
   - chưa xác định được.
2. **Dòng thời gian bằng chứng:** đường dẫn file, giờ, commit.
3. **Đề xuất chốt chặn** nếu thấy có đường lách cổng.

**Không suy đoán là đã lách cổng khi chưa có bằng chứng.**
