# GH-10 · Báo cáo sửa vòng 3 — `mim-jobs-1985`

## Đã làm

| Cảnh | Xử lý |
|---|---|
| `ch03#6` | Bỏ `maxH`, `maxW` và `pos` dạng mảng khỏi cảnh `print` của `sculley06`, để renderer dùng kích thước/bố cục mặc định hợp lệ. |
| `ch07#6` | Bỏ cùng ba tham số sai khỏi cảnh `print` của `sculley06`. |
| `ch03` · `org` “BƯỚC 1 · BỊ TƯỚC QUYỀN” | Neo nút “BƯỚC 2 · TỰ NỘP ĐƠN” từ từ `nộp` về `việc`, ngay sau khi cảnh mở. |
| `ch04` · `org` “TRUNG TÂM CỦA NEXT” | Neo hai nút con vào `nhưng` và `nó`, ngay lúc cảnh mở. |
| `ch04#4` | Không thay ảnh: `nextstation` đang được dùng đúng 3 lần, đã chạm giới hạn tối đa nên không còn lượt dùng. |

Đã kiểm lại JSON sinh ra: `scene_max_constraints=0`, `scene_pos_arrays=0`, `nextstation_refs=3`.

## Cổng đã chạy

1. `python data/long/mim-jobs-1985/gen_scenes.py` — tạo đủ `spec.json` và 9 chương.
2. `python motion/long/script_lines.py mim-jobs-1985` — 120 câu, 1.932 âm tiết.
3. `python motion/long/build_long.py mim-jobs-1985 html` — đủ 9 chương, không có `Error`.
4. `python motion/long/coverage_lint.py mim-jobs-1985` — chữ nền trống 18,31%; chuỗi dài nhất 9,40 giây.
5. `python motion/long/scene_rules.py mim-jobs-1985` — 0 cảnh báo, 0 đề xuất, không thiếu timing.
6. `python motion/long/clip_sheet.py mim-jobs-1985` — tạo sheet 19 clip; đã soi, không thấy logo hoặc chữ thương hiệu đọc được.
7. `python scripts/long_gate.py mim-jobs-1985 --min-syl 1900` — **ĐẠT** (1.932 âm tiết; 127 cảnh; 19 clip khác; 11 ảnh khác; 32 URL nguồn).
8. `python -c "import sys,json;sys.path[:0]=['motion/long','motion','.'];import build_long as B,floor;s,c,o=B.load('mim-jobs-1985');print(floor.problems(c,s.get('channel'),'mim-jobs-1985'))"` — `[]`.

## Lint còn lại

Lệnh HTML chỉ còn hai cảnh báo co chữ tự động, không có lỗi và ngoài phạm vi sửa vòng này:

- `ch00` cảnh 10, hero `BƯỚC MỘT`: engine dự kiến co còn khoảng 95%.
- `ch07` cảnh 4, hero `TẠM QUYỀN`: engine dự kiến co còn khoảng 95%.

Không có khẳng định nội dung mới nào được thêm hoặc cần kiểm nguồn.

## Artifact

- Clip sheet: `output/long/mim-jobs-1985/qa_clips.jpg`
- Thumbnail hiện có: `output/long/mim-jobs-1985/t1.jpg`
- Nguồn thumbnail: `motion/long/thumbs/mim-jobs-1985_t1.html`

Không chạy TTS, render, đăng, commit hoặc thao tác lịch.
