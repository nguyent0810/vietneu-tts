# GH-10 · Codex vòng sửa 2: các lỗi "chặn" còn lại trong bản preview `mim-jobs-1985`

Nguồn lỗi: `docs/pm/tickets/GH-10-preview-report.md`, mục §4 và §5. Ảnh bằng chứng ở `output/long/mim-jobs-1985/qa/`.

Phạm vi file được ghi và các điều cấm giữ nguyên như `docs/pm/tickets/GH-10-fix-codex.md`:
- không sửa `script.md`;
- không chạy TTS;
- không render;
- không commit.

## Sửa

1. **`print` mất tiêu đề** ở 4 cảnh: `ch03#6`, `ch04#4`, `ch05#11`, `ch07#6`.
   - Sửa hàm `print_scene` trong `gen_scenes.py` để tiêu đề chính luôn nằm ở `side.h`. Renderer không vẽ `head`.
   - Kiểm mọi cảnh `print` trong bài, không chỉ 4 cảnh trên.
2. **Ảnh `nextcube` có máy Minitel và chữ "3615 FRED".**
   - **Bỏ hẳn `nextcube`** khỏi bài. Không crop file ảnh: ảnh CC BY, sửa file thì phải ghi chú là đã chỉnh sửa.
   - Cảnh `ch04#6`, `ch05#11`, `ch07#0` thay bằng `nextcube2`, `nextstation` (mỗi ảnh vẫn tối đa 3 lần), ảnh AI (mỗi ảnh tối đa 2 lần), clip đã có trong `broll/`, hoặc đồ họa có nghĩa.
   - `ch04#6`: nhãn phải khớp với hình. Không ghi "MÀN HÌNH ĐỘ PHÂN GIẢI CAO" nếu màn hình trong ảnh đang tắt.
   - Gỡ `nextcube` khỏi `IMGS` và khỏi phần ghi công.
3. **`sculley06` lộ thẻ tên "John Sculley"** trong khung `print`.
   - Dùng tham số engine sẵn có (`pos`, `maxH`, `maxW`) để chỉ lấy phần đầu và vai, không lộ thẻ tên.
   - Không được thì đổi cảnh, không dùng ảnh này ở chỗ đó.
4. **`ch01#6`:** câu trích dẫn thiếu nhãn "TRÍCH DỊCH". Thêm vào.
5. **`ch03#0`, `ch08#0`:** dấu của chữ "Ấ" chạm vào dòng "CHƯƠNG …". Sửa nếu engine có tham số khoảng cách; không có thì ghi lại và bỏ qua.

## Gate

Chạy đủ 8 cổng như vòng trước:
`gen_scenes` → `script_lines` → `html` (9/9) → `coverage_lint` → `scene_rules` → `clip_sheet` → `long_gate` (phải ĐẠT) → `floor` theo kênh (phải ra `[]`).

## Báo cáo

Ghi `docs/pm/tickets/GH-10-fix2-report.md`, gồm:
- bảng các lỗi đã sửa, theo scene ID;
- kết quả gate;
- số lần dùng của từng ảnh.
