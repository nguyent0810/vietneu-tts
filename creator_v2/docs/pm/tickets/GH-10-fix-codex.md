# GH-10 · Codex sửa đúng các cảnh lỗi của `mim-jobs-1985`

- Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/10
- Danh sách lỗi (agy QA): `docs/pm/tickets/GH-10-qa-report.md`, bảng §3 và tổng kết §4. Ảnh bằng chứng nằm ở `output/long/mim-jobs-1985/qa/`.

## Phạm vi

- **Chỉ sửa các cảnh có trong báo cáo.** Không viết lại các cảnh đạt chuẩn.
- Được ghi:
  - `data/long/mim-jobs-1985/gen_scenes.py`;
  - các file do `gen_scenes.py` sinh ra;
  - `output/long/mim-jobs-1985/**`: html, data.js, broll, img đã có;
  - báo cáo.
- Không sửa `script.md` (lời đọc đã duyệt). Không chạy lại TTS.
- Không sửa engine hay tool. Không render. Không gọi bot sinh ảnh. Không commit, không upload.

## Thứ tự

1. **Sửa hết 7 lỗi "chặn":**
   - `ch04#18` chữ tràn khỏi node: rút ngắn dòng phụ.
   - `ch05#9` và `ch07#13` dùng clip `854167` lộ chữ "MacBook Pro": thay bằng `8888977` hoặc một clip không có chữ. Hai cảnh b-roll liền nhau thì đổi một cảnh sang loại khác.
   - `ch06#11`: counter đứng hình 9,46 giây. Chia cảnh hoặc dời neo để không cảnh nào vượt 9 giây; `ch06#12` phải hiện ≥ 2,5 giây.
   - `ch07#2`: mất chữ "AMELIO" do truyền sai tham số `accent`/`v`. Sửa cho đủ chữ.
   - `ch07#14` và `ch08#9`: ledger 7–8 dòng tràn xuống vùng phụ đề. Thu gọn: giữ tối đa 5 dòng gần nhất, hoặc giảm cỡ chữ hay khoảng cách dòng bằng tham số engine sẵn có, sao cho đáy bảng không vượt `y ≈ 860`.
2. **Sửa 33 lỗi "nên sửa"**, gồm cả các nhóm sau:
   - **Nhãn trích dẫn:** `ch07#7` phải là "TRÍCH DỊCH", không phải "DIỄN Ý". Gõ chữ xong phải còn ≥ 1,5 giây trên màn hình.
   - **Ảnh lặp:** mỗi ảnh Wikimedia dùng tối đa 3 lần (`nextcube`, `nextstation`, `jobs84`, `nextcube2`, `mac84`). Thay bằng clip, ảnh AI (`ai01`–`ai06`, mỗi ảnh tối đa 2 lần) hoặc đồ họa có nghĩa. Không thêm nền vô nghĩa.
   - **`nextcube`:** ảnh có chữ "minitel 3615 FRED" và bảng thuyết minh. Không dùng làm nền toàn khung. Nếu dùng thì dùng `photo` kèm `focus` chỉ vào máy NeXT bên phải, hoặc bỏ hẳn.
   - **Cảnh ngắn hơn 2,5 giây:** dời neo hoặc gộp cảnh cho các cảnh có chữ (danh sách ở §2 mục 4).
   - **Phần tử con xuất hiện trễ:** neo phần tử đầu cùng mốc với cảnh (`ch04#12`, `ch06#15`, `ch06#16`, `ch02#5`, `ch01#2`).
   - **`sculley06`:** phụ đề đè lên miệng. Dùng `print` hoặc `focus` để mặt nằm phía trên dải phụ đề, và không lộ thẻ tên.
   - **`nextcube2`:** ảnh vuông bị lower-third đè. Thêm `focus` hoặc đổi bố cục.
   - **`ch04#6`:** callout NEXTSTEP trỏ vào màn hình đang tắt. Đổi ảnh hoặc đổi callout.
   - **`scene_rules`:** còn 4 cặp cảnh cùng loại đứng liền nhau. Xử lý cả 4.
3. **Lỗi "nhỏ":** sửa nếu không tốn công. Ghi lại cái nào bỏ qua và lý do.

## Gate (bắt buộc)

Chạy lần lượt:

1. `gen_scenes.py`
2. `script_lines.py`
3. `build_long.py mim-jobs-1985 html`: đủ 9 chương, không có `Error`.
4. `coverage_lint.py`: chỉ chữ ≤ 22%, chuỗi chữ ≤ 17 giây.
5. `scene_rules.py`: 0 cảnh báo.
6. `clip_sheet.py`, rồi mở `qa_clips.jpg` xem.
7. `python scripts/long_gate.py mim-jobs-1985 --min-syl 1900`: phải **ĐẠT**.
8. Kiểm floor theo kênh: `python -c "import sys,json;sys.path[:0]=['motion/long','motion','.'];import build_long as B,floor;s,c,o=B.load('mim-jobs-1985');print(floor.problems(c,s.get('channel'),'mim-jobs-1985'))"` phải ra `[]`.

## Báo cáo

Ghi `docs/pm/tickets/GH-10-fix-report.md`, gồm:

- bảng cho từng scene ID trong báo cáo QA: đã sửa thế nào, hoặc bỏ qua và lý do;
- số lần dùng của từng ảnh sau khi sửa;
- kết quả của mọi gate.
