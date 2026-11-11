# GH-291: chặn nguồn bịa trong plan, sửa máy C trả rỗng (Codex)

Đọc issue: `gh issue view 291 --repo nguyent0810/vietneu-tts`.

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-291`, nhánh `feat/291`. Đường dẫn tính từ `creator_v2/`, trừ `../scripts/agents/agy_c.sh` ở gốc repo.
- Python: `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.
- Pytest: `--basetemp=tmp_pytest -p no:cacheprovider`. Bộ gốc có 7 test đỏ do thiếu `vnlunar`, bỏ qua. Gặp lỗi quyền khi dọn thư mục tạm thì ghi lại và **làm tiếp, không dừng**.
- Sandbox của bạn không có mạng. Mọi chỗ gọi mạng phải tách hàm để test bằng mock.

## File được sửa
1. `scripts/long_story_review.py`, hàm `run_agent`:
   - Với agent `c` và `local`, chèn hằng `NO_SHELL` vào đầu prompt: "KHÔNG chạy lệnh shell (run_command bị cấm và sẽ làm hỏng phiên). Chỉ dùng công cụ tìm kiếm và đọc web có sẵn. URL nào không mở được thì ghi 'không mở được'."
   - Nếu `result.response` rỗng và có `denied_actions`, ném lỗi ghi rõ tên action bị từ chối.
   - Tách hàm `ask(agent, prompt) -> str` dùng chung cho việc khác, không chỉ review câu chuyện.
2. `../scripts/agents/agy_c.sh` (zsh, cho máy Mac): chèn cùng câu `NO_SHELL` vào đầu prompt; báo `denied_actions`. Kiểm bằng `zsh -n` nếu có, không có thì đọc kỹ.
3. File mới `scripts/plan_sources.py <topic> [--write]`:
   - Đọc `data/long/<topic>/plan.md`, lấy mọi URL.
   - Mỗi URL: tải (urllib, timeout 20 s, user-agent rõ ràng `creator-plan-check/1.0`, **không giả trình duyệt**), ghi trạng thái: `OK` / `HTTP <mã>` / `TRANG_LOI` (tiêu đề hoặc nội dung giống trang lỗi, ví dụ "Trang báo lỗi", "404", "không tìm thấy") / `CHAN` (403, 429) / `KHONG_CHUA_SO` (trong cùng dòng của plan có con số, ví dụ "14.384.902", mà trang không chứa con số đó).
   - Đếm ảnh Commons: plan có `Category:<tên>` trên commons.wikimedia.org thì gọi API `list=categorymembers&cmtype=file` (kèm 1 cấp category con) và in số file thật.
   - `--write`: chèn khối "Kiểm nguồn tự động (<ngày>)" vào đầu plan.md, gồm bảng URL, trạng thái và số ảnh. Không xóa nội dung cũ.
   - Mã thoát khác 0 nếu có URL `TRANG_LOI`, `HTTP 4xx/5xx` (trừ 403/429) hoặc `KHONG_CHUA_SO`.
4. Test mới `tests/test_plan_sources.py`: mock mạng. Dùng `docs/pm/tickets/GH-291-sample-plan.md` (bản sao plan CK bài 10) làm dữ liệu: trang trả "Trang báo lỗi" thì phải ra `TRANG_LOI`; trang không chứa "14.384.902" thì `KHONG_CHUA_SO`. Thêm test cho `NO_SHELL` và lỗi `denied_actions` trong `test_long_story_review.py`.
5. `CLAUDE.md` của creator_v2, bước 1 quy trình Long: thêm một câu: "Trước khi gửi plan cho chủ kênh, chạy `python scripts/plan_sources.py <topic> --write`; plan chỉ do model mạnh viết (không giao Gemini Flash), số ảnh đếm bằng API Commons (#291)."

## Kiểm
- `pytest tests/test_plan_sources.py tests/test_long_story_review.py tests/test_console.py` xanh (script mới phải gọi `factory.console.utf8_console()` ở khối `__main__`).

## Báo cáo
`docs/pm/tickets/GH-291-report.md`, ghi **bằng Python utf-8**, tiếng Việt có dấu.

Không commit, không đăng. **Phải làm đủ 5 mục.**
