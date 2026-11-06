# GH-179: Hòa Thân, dày cảnh 8 chương thưa (theo visual_plan)

`python motion/long/cadence.py hoa-than` (timing ước lượng, chưa TTS):
- **Đạt:** ch04–ch09, 2,3–3,9 giây mỗi lần đổi hình, khoảng dài nhất ≤ 8 giây.
- **Thưa:**

| Chương | Số lần đổi hình | s/lần | Khoảng dài nhất |
|---|---:|---:|---|
| ch00 | 12 | 12,5 | 25 s (ledger #6) |
| ch01 | 13 | 11,5 | 39 s (date #4) |
| ch02 | 16 | 9,4 | 25 s (photo #9) |
| ch03 | 19 | 7,9 | 32 s (kinetic #11) |
| ch10 | 12 | 12,5 | 37 s (file #2) |
| ch11 | 12 | 12,5 | 39 s (slam #10) |
| ch12 | 16 | 9,4 | 27 s (date #7) |
| ch13 | 16 | 9,4 | 35 s (photo #8) |

`visual_plan.md` thiết kế mỗi chương 27–35 nhịp, khoảng 4 giây một nhịp. Hai phần đầu và cuối đang đi lệch thiết kế.

**Được sửa:** `data/long/hoa-than/gen_scenes*.py` và các `chNN.json` của 8 chương trên. Không sửa `script.md`, `factcheck.md` (trừ khi thêm chữ hay số mới trên màn hình, khi đó thêm dòng có nguồn), ch04–ch09, engine hay `build_long.py`. Ghi file bằng Python, `encoding="utf-8"`.

**Việc:**
1. Với mỗi chương thưa, đối chiếu từng câu `script.md` với các nhịp của chương đó trong `visual_plan.md`. Chia lại cảnh để **trung bình ≤ 4,5 giây mỗi lần đổi hình** và **không khoảng nào quá 8 giây** (endcard được miễn). Dùng các cách sau:
   - thêm cảnh mới gắn vào đúng câu, theo nhịp `visual_plan` (ảnh A, ảnh AI B/C, clip `9000NN`, motion graphic D);
   - với cảnh dài đang có, thêm bước con mà engine hỗ trợ (nhiều hàng ledger hiện dần, nhiều mốc timeline, nhiều ảnh trong một photo/split…).
2. Luật vẫn giữ:
   - ảnh dùng tối đa 3 lần;
   - ảnh AI có `credit: false`;
   - nhóm B lần đầu mỗi chương có chú thích "TÁI DỰNG MINH HỌA";
   - không cộng tài sản thành tổng;
   - mọi số trên màn hình phải có trong `factcheck.md`.
3. Chạy lại và đạt hết:
   - `cadence.py hoa-than`: mọi chương ≤ 5 s/lần, max ≤ 8 s trừ endcard, có dán bảng vào báo cáo;
   - `scene_params.py`;
   - `floor.py`;
   - `variety.py audit hoa-than`;
   - `factcheck_lint.py hoa-than`;
   - `long_gate.py hoa-than --min-syl 5000`, chỉ còn lỗi chưa TTS.

**Báo cáo** `docs/pm/tickets/GH-179-hoathan-densify-report.md` (UTF-8): bảng cadence trước và sau theo chương, số cảnh thêm theo loại.
