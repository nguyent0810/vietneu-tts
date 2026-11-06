# GH-173 vòng 2: nhãn đè tiêu đề cảnh cards3d

**QA thật của Grok** (`docs/pm/tickets/GH-173-qa-report.md`, ảnh trong `output/stier/_qa173/*/frames/`): 5/7 cảnh đạt.
- **Lỗi:** cảnh `cards3d` (CK cảnh 3, MIM cảnh 2). Nhãn ở `top: 220px`, hộp cao khoảng 140px (y 220–366), đè tiêu đề cảnh (`hộp y = 304–380`). Thẻ bắt đầu ở y ≈ 427–432.
- **Đạt:** chart, counter, ledger.

**Áp dụng ngoại lệ AGENTS.md.** Chỉ sửa:
- `motion/hf/assets/engine/casefile.css` và `casefile.js`;
- dòng link Google Fonts trong `motion/stier/build.py`;
- `tests/test_hypo_label_173.py`;
- báo cáo `docs/pm/tickets/GH-173-codex-v2-report.md`.

Ghi file bằng Python, `encoding="utf-8"`. Trước khi kết thúc, chạy:
`python -c "import subprocess,sys;d=subprocess.run(['git','diff'],capture_output=True,text=True,encoding='utf-8').stdout;sys.exit('MẤT DẤU' if '???' in d or 'Kh?ng' in d else 0)"`

**Việc:**
1. Khi một cảnh có `hypo`, gắn class (ví dụ `has-hypo`) vào phần tử gốc của cảnh. Với các loại cảnh có tiêu đề ở phía trên vùng nhãn (cards3d chắc chắn; kiểm thêm board, table, ledger, kinetic nếu tiêu đề hay nội dung nằm trong y 220–380), đẩy tiêu đề và nội dung xuống đủ cho hộp nhãn cộng khoảng 24px.
   - Dùng biến CSS, ví dụ `--hypo-offset` bằng chiều cao nhãn.
   - Nhãn có `hypo_sub` cao hơn, offset phải tính cả trường hợp đó.
   - Nội dung đẩy xuống không được tràn vào vùng subtitle (top 1478px). Nếu tràn, thu nhỏ khối nội dung (scale) thay vì đẩy.
   - Các cảnh chart, counter, ledger đã đạt thì giữ nguyên.
2. Link Google Fonts trong `build.py` thêm hai độ đậm mà nhãn dùng: Playfair Display nghiêng 900 (`1,900`) và JetBrains Mono 800.
3. Test:
   - cảnh cards3d có `hypo` thì có class/offset;
   - cảnh không có `hypo` thì không đổi;
   - link font chứa đủ hai độ đậm.

   Chạy `python -m pytest tests -q`.
4. Báo cáo: offset đã dùng cho từng loại cảnh, và lý do chọn đẩy hay thu nhỏ.

**Không:** commit, render (Grok sẽ chụp lại), upload.
