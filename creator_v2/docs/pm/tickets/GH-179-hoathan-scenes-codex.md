# GH-179: Hòa Thân, bước 4 (cảnh viết tay)

**Đọc:**
- `CLAUDE.md`, bước 4;
- `AGENTS.md`;
- skill `../.claude/skills/long-video/SKILL.md`;
- `data/long/golden/` (mẫu `gen_scenes.py` và `chNN.json`);
- `data/long/bao-thanh-thien/gen_scenes.py` (Long CL gần nhất).

**Đầu vào đã duyệt:**
- `data/long/hoa-than/script.md`: lời đọc 14 chương, 5.688 âm tiết;
- `data/long/hoa-than/visual_plan.md`: 429 nhịp hình, mỗi nhịp ghi nhóm A/B/C/D và tài nguyên;
- `output/long/hoa-than/research.json`, `output/long/hoa-than/img/*` (142 ảnh tư liệu và 20 ảnh AI `ai01–ai20`);
- 8 clip AI ở `output/long/hoa-than/broll/900001–900008.mp4`, sidecar `ai_generated`.

**Việc:**
1. Viết `data/long/hoa-than/gen_scenes.py` (thêm `gen_scenes2.py` nếu dài), theo mẫu golden. Mỗi câu gắn với ảnh, bản đồ, hồ sơ, biểu đồ, sketch hay b-roll, **đúng theo `visual_plan.md`**. Sinh ra `chNN.json` và `spec.json`.
   - `spec.json` đặt `channel: "CL"`, theme và look theo các Long CL gần nhất (xem `motion/variety.py`, phải khác 3 video gần nhất).
2. **Ảnh AI (nhóm B/C):**
   - cảnh dùng `ai0N` đặt `"credit": false`;
   - lần đầu nhóm B xuất hiện trong mỗi chương, thêm chú thích nhỏ "TÁI DỰNG MINH HỌA" bằng trường chú thích ảnh mà engine Long đã có (xem cách dùng `illus` trong các Long cũ; CL vẫn hỗ trợ). Không gắn nhãn "TƯ LIỆU" cho ảnh AI;
   - clip AI dùng `vid` = `"900001"`…`"900008"`.
3. Nhóm D (motion graphics) dùng các loại cảnh engine có sẵn: timeline, map, ledger, counter, board, chart, file, date, quote… Mọi số, ngày và trích dẫn trên màn hình phải có trong `factcheck.md`. Danh sách tài sản trên ledger không được cộng thành tổng.
4. Không còn cảnh `"auto": true`.
5. Chạy theo thứ tự và sửa cho đến khi đạt:
   - `python motion/long/scene_params.py hoa-than` (hoặc lệnh validate trong `build_long.py`);
   - `python motion/long/floor.py hoa-than`;
   - `PYTHONIOENCODING=utf-8 python motion/variety.py audit hoa-than`;
   - `python motion/long/cadence.py hoa-than`: trung bình 3–5 giây, không khoảng nào quá 8 giây trừ endcard.
6. **Không** chạy TTS, render hay final. Không sửa engine, `build_long.py` hay `factory`.

**Báo cáo** `docs/pm/tickets/GH-179-hoathan-scenes-report.md` (ghi bằng Python UTF-8): kết quả floor, variety, cadence và scene_params, số cảnh theo loại, % nhóm A/B/C/D, các chỗ lệch `visual_plan` và lý do.
