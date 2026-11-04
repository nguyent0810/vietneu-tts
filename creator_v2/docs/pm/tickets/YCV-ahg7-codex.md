# YCV-ahg7 · Mượn luật scene_picker và motion_picker cho Long MIM/CK (Codex)

## Bối cảnh

Repo vietneu-tts vừa đưa hai công cụ vào nhánh main ngày 29/10. Bản chép chỉ để đọc nằm ở `.ref/vietneu-main/`, **không sửa gì trong thư mục này**:

- `library/tools/scene_picker.py` và `library/scenes/catalog.json` (#70): chọn cảnh Long theo nghĩa câu đọc, chống lặp cảnh, ghi log lý do chọn.
- `library/tools/motion_picker.py` (#71): gán preset chuyển động cho ảnh tĩnh và chia cảnh dài thành nhiều shot.
- Hai công cụ này gắn với engine của bên đó: `.ref/vietneu-main/hyperframes_short/compositions/longform.js`.

Engine bên này: `motion/long/build_long.py` và `motion/hf/compositions/longform.js` (bản tách ra từ trước), HyperFrames 0.8.75.
- Cảnh Long nằm trong `data/long/<topic>/chNN.json`.
- Giờ đọc của từng câu nằm trong `output/long/<topic>/chNN/timing.json`.

Số liệu nền: `docs/pm/2026-10-29-anh-tinh-long-mim-ck.md`. MIM có 86 ảnh tĩnh dài quá 8 giây, trong đó 15 ảnh quá 12 giây.

## Việc

1. **So engine.**
   - So `catalog.json` và `longform.js` của bên kia với `motion/hf/compositions/longform.js` và `engine.js` của bên này: loại cảnh, trường dữ liệu, preset chuyển động (`move`/`zoom` của cảnh `photo`/`print`).
   - Ghi bảng khác biệt vào báo cáo.
   - Kết luận: dùng thẳng được qua adapter, hay chỉ port luật.
2. **Viết `motion/long/scene_rules.py`.** Công cụ chỉ đọc spec và timing, **không sửa** `data/long/**`. Đầu ra là `output/long/<topic>/scene_rules.json`, kèm một bản tóm tắt in ra màn hình:
   - Cảnh liền kề lặp cùng loại, hoặc lặp cùng media: cảnh báo, ghi lý do theo kiểu log của scene_picker.
   - Ảnh tĩnh (`photo`/`print`) dài quá 8 giây: đề xuất chia shot (số shot, mốc theo câu) và preset `move` lấy từ bộ luật motion_picker. Dùng tên preset mà `longform.js` bên này hiểu.
   - Ảnh tĩnh không có `move`/`zoom`: đề xuất một preset, tránh trùng với preset của ảnh liền trước.
   - Gọi: `python motion/long/scene_rules.py <topic>` và `--all` (chỉ chạy các topic `mim-*` và `ck-*`).
3. **Test:** `tests/test_long_scene_rules.py`, dùng dữ liệu giả nhỏ, không phụ thuộc file thật.
4. **Chạy thử** `--all` và ghi top 10 video có nhiều đề xuất nhất vào báo cáo.

## Giới hạn

- Chỉ được ghi các file sau:
  - `motion/long/scene_rules.py`
  - `tests/test_long_scene_rules.py`
  - `output/long/*/scene_rules.json`
  - báo cáo
- Không render, không chạy `npx`, không đăng, không commit, không sửa spec Long.
- Không áp cho CL (topic không có tiền tố `mim-` hoặc `ck-`).

## Báo cáo

Ghi `docs/pm/tickets/YCV-ahg7-report.md`, gồm:
- bảng so engine và kết luận dùng thẳng hay port;
- tóm tắt luật đã port, kèm dòng nguồn bên vietneu;
- kết quả `pytest tests/test_long_scene_rules.py`;
- top 10 video có nhiều đề xuất nhất.
