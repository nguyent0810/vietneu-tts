# GH-228: Mata Hari (CL Long 4), bước 4 (cảnh)

**Phạm vi:** AGENTS.md (từ PR #222) cho phép agent làm CL khi có ticket kèm brief. Đây là ticket đó; chủ kênh đã duyệt plan và kịch bản. File được ghi: `gen_scenes.py`, `gen_scenes2.py`, `chNN.json`, `spec.json` trong `data/long/mata-hari/`, và file báo cáo. Không ghi file nào khác.

**Tiếng Việt (bắt buộc):** mọi file viết bằng Python `open(..., "w", encoding="utf-8")`, không dùng PowerShell `Set-Content`/`Out-File`/redirect. Trước khi báo xong, chạy lệnh dưới, phải in `[]`:
`python -c "import pathlib,sys;b=[str(p) for p in list(pathlib.Path('data/long/mata-hari').glob('*'))+[pathlib.Path('docs/pm/tickets/GH-228-matahari-scenes-report.md')] if p.is_file() and ('???' in p.read_text(encoding='utf-8',errors='replace') or '�' in p.read_text(encoding='utf-8',errors='replace'))];print(b);sys.exit(1 if b else 0)"`

**Đọc:**
- `CLAUDE.md`, bước 4;
- `AGENTS.md`;
- skill `../.claude/skills/long-video/SKILL.md`;
- `data/long/golden/` (mẫu `gen_scenes.py` và `chNN.json`);
- `data/long/bao-thanh-thien/gen_scenes.py` (Long CL gần nhất).

**Đầu vào đã duyệt:**
- `data/long/mata-hari/script.md`: lời đọc 14 chương, 5.773 âm tiết (Lead đã review 07/11);
- `data/long/mata-hari/visual_plan.md`: 418 nhịp hình, mỗi nhịp ghi nhóm A/B/C/D và tài nguyên;
- `output/long/mata-hari/research.json`, `output/long/mata-hari/img/*` (192 ảnh tư liệu; ảnh AI `ai*` chưa có);
- clip AI CHƯA có: dùng clip kho chung `output/asset_library/lib198v` (tag minh_hoa_chung) và clip tư liệu tự do nếu research có.

**Việc:**
1. Viết `data/long/mata-hari/gen_scenes.py` (thêm `gen_scenes2.py` nếu dài), theo mẫu golden. Mỗi câu gắn với ảnh, bản đồ, hồ sơ, biểu đồ, sketch hay b-roll, **đúng theo `visual_plan.md`**. Sinh ra `chNN.json` và `spec.json`.
   - `spec.json` đặt `channel: "CL"`, theme và look theo các Long CL gần nhất (xem `motion/variety.py`, phải khác 3 video gần nhất).
2. **Ảnh AI (nhóm B/C):**
   - cảnh dùng `ai0N` đặt `"credit": false`;
   - lần đầu nhóm B xuất hiện trong mỗi chương, thêm chú thích nhỏ "TÁI DỰNG MINH HỌA" bằng trường chú thích ảnh mà engine Long đã có (xem cách dùng `illus` trong các Long cũ; CL vẫn hỗ trợ). Không gắn nhãn "TƯ LIỆU" cho ảnh AI;
   - clip AI dùng `vid` = `"900001"`…`"900008"`.
3. Nhóm D (motion graphics) dùng các loại cảnh engine có sẵn: timeline, map, ledger, counter, board, chart, file, date, quote… Mọi số, ngày và trích dẫn trên màn hình phải có trong `factcheck.md`. Danh sách tài sản trên ledger không được cộng thành tổng.
4. Không còn cảnh `"auto": true`.
5. Chạy theo thứ tự và sửa cho đến khi đạt:
   - `python motion/long/scene_params.py mata-hari` (hoặc lệnh validate trong `build_long.py`);
   - `python motion/long/floor.py mata-hari`;
   - `PYTHONIOENCODING=utf-8 python motion/variety.py audit mata-hari`;
   - `python motion/long/cadence.py mata-hari`: trung bình 3–5 giây, không khoảng nào quá 8 giây trừ endcard.
6. **Không** chạy TTS, render hay final. Không sửa engine, `build_long.py` hay `factory`.

**Báo cáo** `docs/pm/tickets/GH-228-matahari-scenes-report.md` (ghi bằng Python UTF-8): kết quả floor, variety, cadence và scene_params, số cảnh theo loại, % nhóm A/B/C/D, các chỗ lệch `visual_plan` và lý do.

## Bài học từ Hòa Thân (bắt buộc ngay từ đầu, Lead 07/11)
- **Mỗi chương** đạt `cadence.py`: trung bình ≤ 5 giây mỗi lần đổi hình, không khoảng nào > 8 giây (trừ endcard). Hòa Thân có 8 chương 9–12 giây/đổi hình, phải dày lại. Đừng lặp lại.
- **Floor:** gọi `floor.problems([(ten, chNN_json), ...], "CL", "mata-hari")` trong Python (CLI không in gì). Kết quả phải là `[]`: ≥ 14 loại cảnh, ≥ 30 cảnh b-roll.
- **Nhóm D (motion graphics) 20–30%:** timeline 1876–1917 và 2017, map Leeuwarden–Java–Paris–Madrid–Falmouth, ledger "bốn con số" (1 triệu franc, 20.000 franc, 50.000, 12; không cộng thành tổng), sơ đồ Ladoux–Kalle–bức điện H-21.
- **Lời trích:** dòng trích ở dạng `{"t": …, "q": 1, "tr": 1}`, không để `»` trong `lines` (test_speakable).
- `gen_scenes*.py` phải giữ nguyên `lines` đã duyệt khi chạy lại (xem `data/long/hoa-than/gen_scenes.py` main).
- **Ảnh AI:** `output/long/mata-hari/img/ai*.jpg` (Grok Bot đang tạo; dùng file nào đã có). Clip `broll/9000NN.mp4` (nếu đã có). Clip từ kho chung `lib198v` được phép.
- Ghi file bằng Python UTF-8. Trước khi xong, chạy lệnh kiểm mất dấu trên `git diff`.


## Thêm từ Hòa Thân (Lead 07/11, các cổng `html` đã chặn)
- **Mỗi cảnh dài 2,5–9 giây** (`scene_params`). Đừng dày quá: Hòa Thân ch00 có 31 cảnh trong 72 giây, 23 cảnh < 2,5 giây, phải cắt còn 18. Nhắm 3–5 giây.
- **Phần tử con thứ hai** của ledger/timeline/file/board/map/org phải hiện trong ≤ 1,0 giây kể từ đầu cảnh. Nếu các dòng gắn `at` vào chữ cách xa nhau, bỏ `at` của dòng hoặc bắt đầu cảnh muộn hơn.
- **Tên trên thẻ file** (`name`) phải vừa 872px: tên dài hơn ~14 ký tự chữ hoa thì chia dòng bằng `
`.
- **Mốc `at` theo chữ** phải là một từ có thật trong lời đọc sau TTS: số như "300.000" bị đọc thành chữ, nên đừng neo vào chữ số; neo vào từ thường bên cạnh.
- Không có cảnh nào mô tả xử bắn: CH12 dùng ảnh pháo đài Vincennes, hồ sơ, date; không ảnh thi thể.
- Ảnh AI chưa về: khai báo key `ai01…` theo `ai_prompts.md` trong `IMGS` nhưng KHÔNG dùng trong cảnh; Lead sẽ gắn khi ảnh về.

`spec.json`: `channel: "CL"`; `youtube` theo mẫu `data/long/hoa-than/spec.json` (say cho tên nước ngoài: Margaretha Zelle, Leeuwarden, Vincennes, Ladoux, Bouchardon, Maslov, MacLeod, Kalle, Guimet, Falmouth, Poincaré, Mornet, Clunet, Nivelle, Pétain…; sources ≥ 8 URL từ factcheck; chapter_titles; video_credits; playlist); `publish_at` `2026-11-29T14:00:00Z`. Tiêu đề theo `docs/pm/title-patterns-cl.md` (≤ 100 ký tự), 3 phương án trong `youtube.titles`.

## Lần 2 (Lead 07/11, trả lời báo cáo lần 1)
1. **TTS không cần cho bước này.** Lỗi `long_gate` "chưa TTS" và "spec.youtube" là BÌNH THƯỜNG trước bước giọng: bỏ qua lỗi "chưa TTS". Cảnh neo theo chỉ số câu và chữ trong `lines` (`[câu, "chữ"]`), không cần timing. Lead chạy TTS sau khi cảnh xong.
2. **`visual_plan.md` là gợi ý tư liệu, không phải bản khớp 1:1.** Kịch bản đã sửa sau khi viết visual plan. Quy tắc: lời đọc trong `chNN.json` là chuẩn. Nhịp visual plan nào không có trong lời thì BỎ (đặc biệt mọi nhịp về phát súng, thi thể, áo dạ hội ở CH00: bỏ hết, không đưa lên hình). Câu nào không có nhịp tương ứng thì chọn ảnh/tư liệu phù hợp từ `research.json` và `output/long/mata-hari/img/`, hoặc motion graphics nhóm D. Ghi các chỗ lệch vào báo cáo, không dừng lại vì chúng.
3. Giữ nguyên `lines` hiện có trong `chNN.json` (sinh từ `script.md` đã duyệt). Chỉ thêm `scenes`, `hud {k, t}` và tạo `spec.json`.
4. Đạt khi: `floor.problems(...)` trả `[]`, `cadence.py` đạt (ước theo số câu nếu chưa có timing: khoảng 1 cảnh mỗi 1–2 câu), `variety.py audit` đạt, và `long_gate.py mata-hari --min-syl 5000` chỉ còn lỗi "chưa TTS".
