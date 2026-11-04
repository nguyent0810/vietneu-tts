# GH-26 — Báo cáo vòng sửa Codex

## Đã làm

- Xác nhận `tests/test_branch_gate.py` có hai ca riêng biệt:
  - Ca working tree bẩn tạo `output/x.txt` chưa được Git theo dõi và kỳ vọng `working_tree: dirty`.
  - Ca working tree sạch kỳ vọng `working_tree: clean`.
- Xác nhận hai CLI có khởi tạo console UTF-8 trước khi in tiếng Việt:
  - `scripts/precommit_size.py`: import và gọi `factory.console.utf8_console()` trong khối `__main__`.
  - `motion/long/branch_gate.py`: import và gọi `factory.console.utf8_console()` trong khối `__main__`.

Tóm tắt diff theo ticket: test branch gate nay phân biệt đúng thư mục rỗng với file chưa track; hai CLI nêu trên dùng console UTF-8. Không sửa các CLI cũ ngoài phạm vi ticket.

## Lệnh kiểm tra

1. `python -m py_compile tests/test_branch_gate.py scripts/precommit_size.py motion/long/branch_gate.py`
   - Đạt, không có lỗi cú pháp.
2. `python -m pytest tests/test_branch_gate.py tests/test_console.py -q`
   - Không thể hoàn tất: fixture `tmp_path` bị `PermissionError: [WinError 5] Access is denied` khi pytest quét `%USERPROFILE%\AppData\Local\Temp\pytest-of-<user>`.
   - Quét console chỉ còn bảy CLI cũ ngoài phạm vi: `scripts/qa_mark.py`, `motion/long/commons_find.py`, `motion/long/dryplan.py`, `motion/long/unschedule.py`, `motion/stier/bang_tra_look.py`, `motion/stier/bud_variety.py`, `motion/stier/script_lint.py`. Hai tên GH-26 không còn trong danh sách.
3. `python -m pytest tests/test_branch_gate.py -q --basetemp '.pytest-tmp-gh26' -p no:cacheprovider`
   - Vẫn không thể hoàn tất do `PermissionError` khi pytest dọn thư mục `.pytest-tmp-gh26`; đây là giới hạn quyền của sandbox.

## Lỗi lint còn lại

- Không chạy lint riêng cho ticket này.
- Không có lỗi `py_compile` ở ba file kiểm tra.

## Khẳng định không kiểm được

- Không áp dụng: đây là ticket test/CLI, không có khẳng định nội dung cần fact-check.

## Clip sheet và thumbnail

- Không áp dụng: ticket cấm render và không có asset video.
