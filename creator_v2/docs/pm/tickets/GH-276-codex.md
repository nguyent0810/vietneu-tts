# GH-276: Họ thẻ thông tin 20 kiểu, xoay vòng thay thẻ hồ sơ kẹp ghim (Codex)

Đọc kỹ issue #276: `gh issue view 276 --repo nguyent0810/vietneu-tts`. Thiết kế, bảng 20 kiểu, luật xoay và ràng buộc nội dung đều nằm trong issue. Brief này chỉ thêm phần môi trường.

## Môi trường
- **Worktree:** `D:\Tools\Youtube Creator v2\wt-idcards`, nhánh `feat/276-idcards`. Nhánh này dựng trên nhánh #274 (đã có `cine_auto.py` và khoá mặc định `idcards: true` cho Long mới).
- **Python:** `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.
- **Pytest:** `--basetemp=tmp_pytest -p no:cacheprovider`. Bộ gốc có 7 test đỏ do thiếu module `vnlunar`, bỏ qua. Lỗi quyền lúc dọn thư mục tạm thì ghi lại, **không được dừng vì lỗi đó**. Lead chạy lại toàn bộ test ngoài sandbox.
- **Dữ liệu thật (chỉ đọc):** `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\data\long\mata-hari\` (31 cảnh `file`).

## File ĐƯỢC SỬA (Lead cho phép đích danh)
- `creator_v2/motion/hf/assets/engine/casewide.js`
- `creator_v2/motion/hf/assets/engine/casewide.css`
- `creator_v2/motion/hf/assets/engine/casefile.js` và `casefile.css` (6 kiểu cho Short; làm sau, nếu còn thời gian)
- `creator_v2/motion/long/build_long.py`: chỉ phần gọi bộ chọn và in phân bố
- `creator_v2/motion/long/scene_params.py`: khoá `style` và `hint` của cảnh `file`
- `creator_v2/motion/long/floor.py`: chặn mật độ
- `creator_v2/motion/long/README.md`
- File mới:
  - `creator_v2/motion/long/idcards.py` (bộ chọn tất định)
  - `creator_v2/motion/long/idcards_demo.py`
  - `creator_v2/tests/test_idcards.py`

## Thứ tự làm
1. `idcards.py`: bộ chọn + luật mật độ + test, chạy thử trên bản sao Mata Hari.
2. Engine: dựng **đủ 20 kiểu** bằng CSS/SVG, kèm nhãn "ĐỒ HỌA" cho các kiểu dạng tài liệu. Mỗi kiểu có chuyển động vào/ra; chữ hiện dần theo mốc `at`, như `file` hiện tại.
3. `idcards_demo.py`: sinh 1 composition chứa đủ 20 kiểu (dữ liệu giả lập, nhưng dữ kiện hợp lý) để Lead render thành ảnh tĩnh.
4. `floor.py` + README.

## Kiểm
- Test bộ chọn: chạy lại Mata Hari ra ≥ 8 kiểu, không kiểu nào > 4%, không lặp trong 6 cảnh, hai thẻ cách nhau ≥ 4 cảnh. Topic legacy không đổi.
- `node --check casewide.js` phải qua.
- Không được ném lỗi khi thiếu trường tuỳ chọn (`img`, `date`…). Lỗi ném ra làm video đứng hình (#284).

## Báo cáo (tiếng Việt có dấu, ghi bằng Python utf-8)
`docs/pm/tickets/GH-276-report.md`, gồm:
- danh sách 20 kiểu đã dựng;
- phân bố trên Mata Hari;
- kết quả test;
- lệnh render trang demo để Lead chạy.

## Ràng buộc
Không render, không commit, không đăng. **Phải làm đủ.** Dừng giữa chừng mà không có code thì tính là hỏng.
