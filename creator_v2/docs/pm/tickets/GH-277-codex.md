# GH-277: Nhóm B, chữ động theo nhịp giọng, kiểu chữ xoay, hiệu ứng chữ (Codex)

Đọc issue (đủ 5 việc và luật chung): `gh issue view 277 --repo nguyent0810/vietneu-tts`. Brief này ghi phạm vi và môi trường.

## Môi trường
- Worktree riêng `D:\Tools\Youtube Creator v2\wt-277`, nhánh `feat/277`, tách từ main 6de8cb9. Không phải checkout sản xuất. Lead cho phép đích danh sửa code dùng chung trong worktree này. Lead commit.
- Mọi đường dẫn tính từ `creator_v2/` của worktree.
- Python: `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.
- Pytest: `--basetemp=tmp_pytest -p no:cacheprovider`. Lỗi quyền thư mục tạm thì ghi lại và làm tiếp.
- Main vừa nhận PR #294 (trộn kiểu hình Long + kinetic theo ngưỡng, tránh 40 giây đầu) và #293 (bộ style mới cho Long mới). Đọc hai thay đổi đó trước (`git log -3 --stat` không chạy được thì đọc `motion/long/README.md` và code), để bộ chọn hiệu ứng chữ không đá nhau với bộ trộn có sẵn.
- Sandbox không chạy Node/Chrome: logic chọn kiểu/hiệu ứng viết thành hàm Python thuần (hoặc JS thuần được gọi tất định) để test bằng pytest. Hiệu ứng trong `beat.js` thì Lead render kiểm.

## File được sửa
- `motion/hf/assets/engine/beat.js`, `beat.css`: hiệu ứng mới, kiểu chữ, `sync`, `strike`.
- `motion/long/build_long.py`: chỉ phần gán hiệu ứng/kiểu chữ khi `html`, và in bảng phân bố.
- File mới nếu cần, ví dụ `motion/long/kinetic_style.py` (bộ chọn tất định).
- `motion/long/lint_html.py`: chỉ `KIN_FONTS`.
- Font mới (nếu cần) vào `motion/long/fonts/` kèm dòng trong `LICENSE-OFL.txt`; chỉ font OFL có tiếng Việt. Không tải được font thì ghi tên font + URL Google Fonts trong báo cáo, Lead tải.
- `motion/long/README.md`: bảng khoá, ví dụ JSON, luật xoay.
- Test mới `tests/test_kinetic_style.py`.

## Ràng buộc
- Spec cũ không có khoá mới thì HTML ra **y như trước** (test: dựng HTML một chương của `golden` trước và sau, so chuỗi phần chữ động; hoặc so đầu ra hàm chọn với cờ tắt).
- Cảnh đã ghi tay `fx`/`style` thì giữ nguyên.
- Tất định: hạt từ topic + số thứ tự cảnh.

## Tiêu chí đạt
- Test bộ chọn: mỗi chương ≥ 4 hiệu ứng khác nhau, không hiệu ứng nào > 20% số dòng chữ, không lặp liền kề; `strike` tự bật với "KHÔNG PHẢI X · Y", "ĐỪNG", "SAI", "CHẲNG PHẢI".
- `build_long.py <topic> html` in bảng phân bố hiệu ứng và kiểu chữ.
- `pytest tests -q` không thêm test đỏ so với trước khi sửa.
- Lệnh render thử 1 chương để Lead chạy (ghi trong báo cáo).

## Báo cáo
Ghi `docs/pm/tickets/GH-277-report.md` bằng **Python utf-8** (không dùng PowerShell `>`), tiếng Việt có dấu: file đã sửa, bảng hiệu ứng, kết quả test, lệnh render thử.

Không render, không commit, không đăng. Làm đủ cả 5 việc trong issue; dừng giữa chừng tính là hỏng.
