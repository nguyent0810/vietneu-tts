# GH-179: Hòa Thân, bước 5–6 (giọng, html, render, final)

**Điều kiện (đã thỏa 06/11):** Lead đã duyệt bước 4 (PR #225, floor/cadence/factcheck đạt). Trước đây ghi: chỉ chạy khi bước 4 đã đạt (`docs/pm/tickets/GH-179-hoathan-scenes-report.md` ghi floor, variety, cadence đạt và Lead đã duyệt).

**Đọc:** `CLAUDE.md` (bước 5–6), `AGENTS.md`, chú thích đầu `motion/long/build_long.py` (dòng ~320: takes → stt_takes → pick → tts).

**Việc (chạy từ `vietneu-main/creator_v2/`, topic `hoa-than`):**
1. Giọng:
   - `python motion/long/build_long.py hoa-than takes 3` (venv có `vieneu`);
   - `python motion/long/stt_takes.py hoa-than` (venv `.venv-video`, CUDA);
   - `python motion/long/build_long.py hoa-than pick`, rồi `python motion/long/build_long.py hoa-than tts`.
   - Ghi lại số câu, số câu bản 0 kém hơn bản được chọn, và mọi câu `pick` vẫn báo lỗi đọc (sai số, nuốt chữ).
2. `python motion/long/build_long.py hoa-than html`, rồi `render ch01 --draft` và `render ch07 --draft` để soi. Lỗi lint/craft/floor thì dừng, ghi vào báo cáo, không tự sửa cảnh.
3. Đạt thì `render` toàn bộ, rồi `final`.
4. Chạy contact sheet từng chương (`motion/long/clip_sheet.py` hoặc lệnh contact sheet mà `build_long.py` in ra) và ghi đường dẫn.

**Không được:** sửa `gen_scenes*.py`, `chNN.json`, `spec.json`, engine, `factory/`; hạ ngưỡng cổng; upload, đặt lịch, commit.

**Được ghi:** `output/long/hoa-than/**` và báo cáo.

**Báo cáo** `docs/pm/tickets/GH-179-hoathan-voice-report.md`, ghi bằng Python `open(..., "w", encoding="utf-8")`, không dùng PowerShell redirect:
- thời lượng từng chương và tổng; đường dẫn file final;
- kết quả takes/pick (số câu, câu lỗi còn lại);
- kết quả lint, craft, floor khi render;
- đường dẫn contact sheet từng chương;
- mọi lệnh lỗi kèm 20 dòng log cuối.
