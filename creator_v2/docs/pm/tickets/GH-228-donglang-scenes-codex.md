# GH-228: Đông Lăng (CL Long 3), bước 4 (cảnh)

**Phạm vi:** AGENTS.md (từ PR #222) cho phép agent làm CL khi có ticket kèm brief. Đây là ticket đó; chủ kênh đã duyệt plan và kịch bản. File được ghi: `gen_scenes.py`, `gen_scenes2.py`, `chNN.json`, `spec.json` trong `data/long/dong-lang/`, và file báo cáo. Không ghi file nào khác.

**Tiếng Việt (bắt buộc):** mọi file viết bằng Python `open(..., "w", encoding="utf-8")`, không dùng PowerShell `Set-Content`/`Out-File`/redirect. Trước khi báo xong, chạy lệnh dưới, phải in `[]`:
`python -c "import pathlib,sys;b=[str(p) for p in list(pathlib.Path('data/long/dong-lang').glob('*'))+[pathlib.Path('docs/pm/tickets/GH-228-donglang-scenes-report.md')] if p.is_file() and ('???' in p.read_text(encoding='utf-8',errors='replace') or '�' in p.read_text(encoding='utf-8',errors='replace'))];print(b);sys.exit(1 if b else 0)"`

**Đọc:**
- `CLAUDE.md`, bước 4;
- `AGENTS.md`;
- skill `../.claude/skills/long-video/SKILL.md`;
- `data/long/golden/` (mẫu `gen_scenes.py` và `chNN.json`);
- `data/long/bao-thanh-thien/gen_scenes.py` (Long CL gần nhất).

**Đầu vào đã duyệt:**
- `data/long/dong-lang/script.md`: lời đọc 14 chương, 5.688 âm tiết;
- `data/long/dong-lang/visual_plan.md`: 429 nhịp hình, mỗi nhịp ghi nhóm A/B/C/D và tài nguyên;
- `output/long/dong-lang/research.json`, `output/long/dong-lang/img/*` (142 ảnh tư liệu và 20 ảnh AI `ai01–ai20`);
- 8 clip AI ở `output/long/dong-lang/broll/900001–900008.mp4`, sidecar `ai_generated`.

**Việc:**
1. Viết `data/long/dong-lang/gen_scenes.py` (thêm `gen_scenes2.py` nếu dài), theo mẫu golden. Mỗi câu gắn với ảnh, bản đồ, hồ sơ, biểu đồ, sketch hay b-roll, **đúng theo `visual_plan.md`**. Sinh ra `chNN.json` và `spec.json`.
   - `spec.json` đặt `channel: "CL"`, theme và look theo các Long CL gần nhất (xem `motion/variety.py`, phải khác 3 video gần nhất).
2. **Ảnh AI (nhóm B/C):**
   - cảnh dùng `ai0N` đặt `"credit": false`;
   - lần đầu nhóm B xuất hiện trong mỗi chương, thêm chú thích nhỏ "TÁI DỰNG MINH HỌA" bằng trường chú thích ảnh mà engine Long đã có (xem cách dùng `illus` trong các Long cũ; CL vẫn hỗ trợ). Không gắn nhãn "TƯ LIỆU" cho ảnh AI;
   - clip AI dùng `vid` = `"900001"`…`"900008"`.
3. Nhóm D (motion graphics) dùng các loại cảnh engine có sẵn: timeline, map, ledger, counter, board, chart, file, date, quote… Mọi số, ngày và trích dẫn trên màn hình phải có trong `factcheck.md`. Danh sách tài sản trên ledger không được cộng thành tổng.
4. Không còn cảnh `"auto": true`.
5. Chạy theo thứ tự và sửa cho đến khi đạt:
   - `python motion/long/scene_params.py dong-lang` (hoặc lệnh validate trong `build_long.py`);
   - `python motion/long/floor.py dong-lang`;
   - `PYTHONIOENCODING=utf-8 python motion/variety.py audit dong-lang`;
   - `python motion/long/cadence.py dong-lang`: trung bình 3–5 giây, không khoảng nào quá 8 giây trừ endcard.
6. **Không** chạy TTS, render hay final. Không sửa engine, `build_long.py` hay `factory`.

**Báo cáo** `docs/pm/tickets/GH-228-donglang-scenes-report.md` (ghi bằng Python UTF-8): kết quả floor, variety, cadence và scene_params, số cảnh theo loại, % nhóm A/B/C/D, các chỗ lệch `visual_plan` và lý do.

## Bài học từ Hòa Thân (bắt buộc ngay từ đầu, Lead 07/11)
- **Mỗi chương** đạt `cadence.py`: trung bình ≤ 5 giây mỗi lần đổi hình, không khoảng nào > 8 giây (trừ endcard). Hòa Thân có 8 chương 9–12 giây/đổi hình, phải dày lại. Đừng lặp lại.
- **Floor:** gọi `floor.problems([(ten, chNN_json), ...], "CL", "dong-lang")` trong Python (CLI không in gì). Kết quả phải là `[]`: ≥ 14 loại cảnh, ≥ 30 cảnh b-roll.
- **Nhóm D (motion graphics) 20–30%:** timeline 1928–1929, map Đông Lăng, ledger đồ tùy táng (không cộng thành tổng), sơ đồ quan hệ người nhận quà (ghi "theo lời kể").
- **Lời trích:** dòng trích ở dạng `{"t": …, "q": 1, "tr": 1}`, không để `»` trong `lines` (test_speakable).
- `gen_scenes*.py` phải giữ nguyên `lines` đã duyệt khi chạy lại (xem `data/long/hoa-than/gen_scenes.py` main).
- **Ảnh AI:** `output/long/dong-lang/img/ai*.jpg` (Grok Bot đang tạo; dùng file nào đã có). Clip `broll/9000NN.mp4` (nếu đã có). Clip từ kho chung `lib198v` được phép.
- Ghi file bằng Python UTF-8. Trước khi xong, chạy lệnh kiểm mất dấu trên `git diff`.

## Lần 2 (Lead, 07/11 05:15)
Lần trước các file `script.md`, `plan.md`, `visual_plan.md`, `factcheck.md` vắng mặt là lỗi của Lead (đổi nhánh git giữa chừng). Giờ đã có đủ.

**`chNN.json` hiện có là bản cũ**, sinh từ kịch bản bị thay (6.884 âm tiết). Sinh lại `lines` từ `script.md` đã duyệt (5.665 âm tiết) bằng `script_lines.py` (xem cách `gen_scenes.py` của Hòa Thân gọi), rồi mới gắn cảnh.

Ảnh AI và clip Đông Lăng **chưa về**: Grok Bot đang làm. Dựng cảnh bằng ảnh tư liệu (`output/long/dong-lang/img/` và ảnh Commons trong `research.json`, engine tự tải), clip kho chung `lib198v`, và motion graphics. Để sẵn chỗ cho ảnh AI theo `visual_plan`, khai báo key `ai01…` trong `IMGS`; Lead sẽ kiểm khi ảnh về.

`spec.json`: `channel: "CL"`; mục `youtube` làm theo mẫu `data/long/hoa-than/spec.json`, có `say`, `sources` (≥ 8 URL lấy từ `factcheck.md`), `chapter_titles`, `video_credits`, `playlist`; `publish_at` để `2026-11-22T14:00:00Z`.
