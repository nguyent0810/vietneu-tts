# GH-179: Hòa Thân, bước 4 phần C (CH07–CH09)

**Phạm vi:** AGENTS.md (PR #222) cho phép agent làm CL khi có ticket kèm brief; chủ kênh đã duyệt plan và kịch bản Hòa Thân. Bước 4 được chia làm 4 phần (A–D) vì 429 nhịp quá lớn cho một lượt. Phần này chỉ làm **CH07–CH09**. Lượt trước bỏ cuộc mà không viết dòng nào: **lần này phải viết code cảnh thật, không được chỉ báo cáo.**

**Khuôn mẫu: chép cấu trúc `data/long/bao-thanh-thien/`.**
- `gen_scenes.py`: `IMGS` (ảnh theo số thứ tự trong `research.json`, hàm `im(i, must)`), `V` (clip), `GEO`, `CH["chNN"] = dict(hud=..., bgm=..., scenes=[sc(...), ...])`, và khối `__main__` nạp `gen_scenes2/3/4.py`. Ghi ra bằng `scenekit.write`.
- `gen_scenes2.py`: `from gen_scenes import ...`, chỉ khai `CH`.
- Đọc thêm `data/long/golden/gen_scenes.py` và `CLAUDE.md` bước 4.

**Nguồn sự thật khi lệch nhau:**
- Thứ tự và chữ lấy theo `script.md`. Mỗi `sc(kind, câu_số, ...)` neo vào câu thật trong kịch bản; `hitAt`/`at` dùng từ có thật trong câu đó.
- `visual_plan.md` là gợi ý tài nguyên và nhóm A/B/C/D. Kế hoạch lệch kịch bản (thứ tự, chi tiết) thì **theo kịch bản**, lấy tài nguyên hợp nhất từ kế hoạch của chương đó, ghi một dòng vào báo cáo. Đây không phải lý do để dừng.
- Mọi số, ngày, trích dẫn trên màn hình phải có trong `factcheck.md`. Mục ghi LỆCH hay CHƯA MỞ thì không đưa lên màn hình dạng khẳng định. Danh sách tài sản trên ledger không cộng thành tổng.

**Ảnh/clip AI:**
- `ai01–ai20` là ảnh AI: đặt `"credit": false`. Lần đầu nhóm B xuất hiện trong mỗi chương, gắn chú thích nhỏ "TÁI DỰNG MINH HỌA" bằng trường chú thích ảnh (`illus`) như các Long CL cũ. Không gắn "TƯ LIỆU" cho ảnh AI.
- Clip AI: `vid` = `"900001"`…`"900008"`.
- Không ảnh AI mô tả rõ mặt người thật.

**Nhịp:** trung bình 3–5 giây/cảnh, không khoảng nào quá 8 giây trừ endcard. Không còn cảnh `"auto": true`.

**File được ghi:** `data/long/hoa-than/gen_scenes3.py`, các `chNN.json` của phần mình, và báo cáo. Thêm key vào `IMGS`/`V` trong `gen_scenes.py` khi cần: chỉ được **thêm dòng**, không sửa cảnh chương khác. Không sửa engine, `scenekit`, `build_long.py`, `factory/`, `script.md`, `visual_plan.md`. Không chạy TTS hay render.

**Kiểm sau khi viết** (từ `vietneu-main/creator_v2/`):
1. `python data/long/hoa-than/gen_scenes.py`: phải sinh `chNN.json` cho các chương đã có.
2. `python motion/long/cadence.py hoa-than`: ghi số của các chương mình làm.
3. `python motion/long/scene_params.py hoa-than`.
4. `long_gate`/`floor` trượt vì thiếu chương sau là bình thường; ghi lại lỗi.

**Tiếng Việt (bắt buộc):** ghi mọi file bằng Python `open(..., "w", encoding="utf-8")`, không dùng PowerShell `Set-Content`/`Out-File`/redirect. Trước khi báo xong, chạy lệnh sau; nó phải in `[]`:
`python -c "import pathlib,sys;fs=list(pathlib.Path('data/long/hoa-than').glob('*.*'))+[pathlib.Path('docs/pm/tickets/GH-179-hoathan-scenesC-report.md')];b=[str(p) for p in fs if p.is_file() and p.suffix in ('.py','.json','.md') and any(x in p.read_text(encoding='utf-8',errors='replace') for x in ('???','�'))];print(b);sys.exit(1 if b else 0)"`

**Báo cáo** `docs/pm/tickets/GH-179-hoathan-scenesC-report.md` (UTF-8): số cảnh theo loại và theo chương; tỉ lệ A/B/C/D của phần mình; kết quả cadence và scene_params; các chỗ lệch `visual_plan` kèm lý do.
