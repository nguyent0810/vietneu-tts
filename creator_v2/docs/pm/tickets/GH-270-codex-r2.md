# GH-270 (lần 2): preflight Short kiểm schema cảnh (Codex)

Đọc issue: `gh issue view 270 --repo nguyent0810/vietneu-tts`. Lần 1 bạn dừng vì brief không ghi worktree. Lần này có worktree riêng.

## Môi trường
- Worktree riêng `D:\Tools\Youtube Creator v2\wt-270`, nhánh `feat/270`, tách từ main 6de8cb9. Đây **không phải** checkout sản xuất. Lead cho phép đích danh sửa code dùng chung trong worktree này theo AGENTS.md. Bạn không cần đụng git: Lead commit.
- Mọi đường dẫn tính từ `creator_v2/` của worktree.
- Python: `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.
- Pytest: `--basetemp=tmp_pytest -p no:cacheprovider`. Lỗi quyền thư mục tạm thì ghi lại và **làm tiếp**. Lead chạy lại toàn bộ test ngoài sandbox.

## File được sửa
- `motion/stier/build.py`: chỉ phần preflight.
- `motion/stier/README.md`: ghi bảng trường bắt buộc theo loại cảnh (nếu chưa có, hoặc chỉnh cho khớp code).
- Test mới `tests/test_stier_preflight_schema.py`.

## Việc
1. Preflight kiểm schema từng cảnh theo loại (`type`), dựa trên trường mà engine thật sự đọc (`motion/stier/sfx.py`, `casefile.js`, builder). Đọc code để lập bảng, đừng đoán. Ví dụ: `timeline` cần `items[{year,text,at}]`; spec có `rows` thì báo lỗi cứng "timeline cần `items`, không phải `rows`".
2. Trường bị bỏ qua mà không báo: `evidence` chỉ đọc `tag` và `callouts`. Spec có `code`, `title`, `desc` trong cảnh `evidence` thì **cảnh báo** (không chặn), ghi rằng engine bỏ qua các trường này.
3. Thông báo lỗi tiếng Việt có dấu, ghi tên cảnh/số thứ tự, trường thiếu và trường đúng.

## Tiêu chí đạt
- Test: spec có `timeline.rows` bị preflight chặn; spec `evidence` có `title` nhận cảnh báo nhưng không bị chặn; spec đúng thì qua.
- Chạy preflight trên mọi `data/stier/specs/cl-*.json`, `ck-*.json`, `mim-*.json` có trong git (`git ls-files` không được thì dùng danh sách file): liệt kê spec **bị chặn thêm** do cổng mới, so với cổng cũ. Không tự sửa spec.
- `pytest tests/test_stier_preflight_schema.py tests/test_ck_stier.py` (3 test đỏ có sẵn ở test_ck_stier do spec chưa vào git, bỏ qua).

## Báo cáo
Ghi `docs/pm/tickets/GH-270-report.md` bằng **Python utf-8** (không dùng PowerShell `>`/Set-Content: lần trước báo cáo mất dấu thành `?`). Gồm: diff tóm tắt, bảng trường bắt buộc, kết quả test, danh sách spec bị chặn thêm.

Không render, không commit, không đăng. Làm đủ cả 3 việc; dừng giữa chừng tính là hỏng.
