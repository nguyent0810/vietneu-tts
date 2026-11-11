# GH-284: chặn render khi trang dựng lỗi, kiểm video đứng hình, font Long, endcardBg (Codex)

Đọc issue: `gh issue view 284 --repo nguyent0810/vietneu-tts`. Brief này ghi phạm vi và môi trường.

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-284`, nhánh `feat/284`, tách từ main ef2bb39. Mọi đường dẫn bên dưới tính từ `creator_v2/` của worktree này.
- Python: `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.
- Pytest: `--basetemp=tmp_pytest -p no:cacheprovider`. Bộ gốc có 7 test đỏ do thiếu module `vnlunar`, bỏ qua. Gặp lỗi quyền khi dọn thư mục tạm thì ghi lại và **làm tiếp, không dừng**. Lead chạy lại toàn bộ test ngoài sandbox.
- Sandbox của bạn không chạy được Node/Chrome. Code gọi puppeteer phải test bằng mock: tách hàm thuần (dựng lệnh, đọc kết quả JSON, so khung hình) để test được bằng Python.

## File được sửa (Lead cho phép đích danh)
- `motion/long/build_long.py`: chỉ phần `cmd_render` (gọi kiểm trước và sau render) và phần kiểm `spec.imgs` (tính cả `endcardBg`).
- File mới `motion/long/pagecheck.py`: mở composition bằng Chrome headless, bắt `pageerror` và console error. Kèm script node `motion/long/pagecheck.cjs`, gọi từ Python bằng subprocess.
  - Tìm `puppeteer-core` trong cache npx (`%LOCALAPPDATA%\npm-cache\_npx\*\node_modules\puppeteer-core`) và `chrome.exe` trong `~/.cache/puppeteer`.
  - HTML phải được mở từ gốc `motion/hf/` để đường dẫn tương đối tới asset đúng. Chép composition ra `motion/hf/_pagecheck_<tên>.html`, kiểm, rồi xóa file tạm trong `finally`.
  - Đọc `window.__timelines` để trả về thời lượng timeline.
  - Không tìm thấy puppeteer hoặc Chrome: in cảnh báo và **không chặn**. Chỉ chặn khi có pageerror thật.
  - Mẫu chạy đúng có sẵn ở `C:\Users\Tung-QA\AppData\Local\Temp\claude\57b85a600e693a86\2143065b-91f2-4413-8e5d-3c2247ea565d\scratchpad\pagecheck.cjs` (đọc để tham khảo).
- File mới `motion/long/frozen_check.py`: sau render, trích 3 khung ở 10%, 50%, 90% bằng ffmpeg, so độ khác nhau (ví dụ trung bình sai khác điểm ảnh trên ảnh thu nhỏ). Ba khung gần như giống nhau thì báo lỗi "video đứng hình" và trả mã khác 0.
- `motion/long/README.md`: mục font và giấy phép OFL, mục hai bước kiểm mới.
- `.gitignore` (nếu cần) để thư mục `motion/long/fonts/` vào git. Kiểm `git check-ignore`. Không tự commit, Lead commit.
- File font: thêm `motion/long/fonts/LICENSE-OFL.txt` (văn bản OFL 1.1, ghi tên các họ font: Be Vietnam Pro, Inter, Montserrat, Playfair Display).
- Test mới `tests/test_render_guard.py`.

## Tiêu chí đạt
- Test cho cả 3 mục:
  1. Kết quả pagecheck có pageerror thì `cmd_render` dừng trước khi gọi `hyperframes render` (mock subprocess).
  2. Hàm so khung báo đứng hình với 3 ảnh giống nhau và không báo với 3 ảnh khác nhau (tạo ảnh bằng PIL hoặc numpy).
  3. Kiểm `spec.imgs` không còn báo "không có cảnh nào dùng" với ảnh chỉ nằm ở `endcardBg`.
- `pytest tests/test_render_guard.py tests/test_long_floor.py tests/test_long_defaults.py` xanh.
- Không đổi hành vi render khi không có lỗi, ngoài thời gian kiểm thêm.

## Báo cáo
Ghi `docs/pm/tickets/GH-284-report.md` bằng Python utf-8, tiếng Việt có dấu. Gồm: file đã sửa, cách gọi, kết quả test, và lệnh để Lead thử thật một spec cố tình thiếu ảnh.

Không render, không commit, không đăng. **Phải làm đủ cả 3 mục. Dừng giữa chừng tính là hỏng.**
