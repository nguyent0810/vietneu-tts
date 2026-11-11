# GH-285 phần 2: đưa 87 bài nhạc mới vào danh mục, luật lặp dài hạn, ghi công theo tác giả (Codex)

Đọc issue: `gh issue view 285 --repo nguyent0810/vietneu-tts`. Phần 1 đã xong: Grok tải 87 bài và kiểm giấy phép (`docs/pm/tickets/GH-285-agy-report.md`). Lead đã chép cả 87 file vào kho thật `output/music/` (kho dùng chung, không nằm trong worktree này).

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-285`, nhánh `feat/285` (đã cập nhật theo main). Đường dẫn tính từ `creator_v2/`.
- Python: `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.
- Pytest: `--basetemp=tmp_pytest -p no:cacheprovider`. Bộ gốc có 7 test đỏ do thiếu `vnlunar`, bỏ qua. Gặp lỗi quyền khi dọn thư mục tạm thì ghi lại và **làm tiếp, không dừng**.
- Đầu vào (chỉ đọc): `tmp_music/proposed_catalog.json` (87 mục) và báo cáo phần 1.
- Kho file thật (chỉ đọc): `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\output\music\`. Trong worktree này `output/` không tồn tại, nên test không được phụ thuộc file nhạc thật.

## File được sửa
- `motion/long/music_catalog.json`:
  - Gộp 87 mục. 23 mục MacLeod đã có thì chỉ bổ sung `source_url`, `license_url`, `duration_s` và sửa `license` theo đúng chữ trên trang bài (báo cáo phần 1: incompetech ghi CC BY 3.0).
  - 64 mục mới thêm đầy đủ trường.
  - Cập nhật `_doc`: không còn "chỉ Kevin MacLeod".
  - Giữ nguyên thứ tự và khóa cũ.
- `motion/variety.py`, luật lặp dài hạn:
  - Một bài có mặt **tối đa 1 trong 5 Long gần nhất** của kênh.
  - Một bài có mặt **tối đa ở 15%** tổng số Long của kênh (làm tròn lên, tối thiểu 1).
  - Áp ở `resolve_bgm` khi tự chọn (loại bài vi phạm khỏi ứng viên; hết ứng viên thì cảnh báo rõ, không crash) và ở `audit` (báo vi phạm).
  - Giữ luật Jaccard 3 video gần nhất hiện có.
  - Lệnh `library` in thêm: số bài theo kênh và tác giả, bài thiếu file.
- `motion/long/describe.py`: ghi công **theo từng tác giả**.
  - Bỏ bảng `MUSIC` cứng chỉ cho MacLeod. Lấy `title`, `author`, `license` từ danh mục.
  - Mỗi tác giả một dòng: `"Bài A", "Bài B" by <Tác giả> (<nguồn ngắn>), licensed under <license> (<license_url>)`.
  - MacLeod giữ chữ `incompetech.com`. Scott Buckley ghi `scottbuckley.com.au`. Chris Zabriskie ghi `chriszabriskie.com`. Kai Engel ghi trang nguồn của bài.
  - Video cũ (chỉ MacLeod) phải ra **đúng chuỗi như trước** nếu license không đổi. Nếu đổi 4.0 thành 3.0 thì chỉ khác phần license: viết test chứng minh.
- `tests/test_variety_longterm.py`, `tests/test_describe_music_credit.py` (mới).
- `motion/long/README.md`: mục nhạc nền (tác giả, giấy phép, luật lặp).

## Tiêu chí đạt
- Test luật lặp:
  - bài đã dùng trong 1 của 5 Long gần nhất bị loại;
  - bài đã ở 15% số Long bị loại;
  - hết ứng viên thì cảnh báo, không crash.
- Test ghi công: video dùng 2 bài của 2 tác giả ra 2 dòng đúng.
- `python motion/variety.py library` (chạy từ thư mục `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2` để có file thật, **chỉ đọc**) cho kết quả: không bài thiếu file; mỗi kênh ≥ 40 bài, ≥ 3 tác giả. Chép kết quả vào báo cáo. Nếu sandbox không chạy được ở đó thì ghi lại; Lead sẽ chạy.
- `pytest tests/test_variety_longterm.py tests/test_describe_music_credit.py` và các test hiện có của variety/describe xanh.

## Báo cáo
Ghi `docs/pm/tickets/GH-285-codex-report.md` **bằng Python, mã hóa utf-8** (không dùng PowerShell `Out-File`/`Set-Content`: lần trước báo cáo #284 mất hết dấu thành "?"). Tiếng Việt có dấu.

Không commit, không đăng, không xóa file nhạc. **Phải làm đủ. Dừng giữa chừng tính là hỏng.**
