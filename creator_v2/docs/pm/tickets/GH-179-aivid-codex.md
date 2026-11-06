# ai_img_request.py: xử lý cả clip Flow (vid_NN.mp4)

**Bối cảnh:** `data/long/hoa-than/ai_prompts.md` có 20 mục `## ai_NN.png` và 8 mục `## vid_NN.mp4`. Grok Bot lưu cả hai loại vào `Downloads\grokbot\<topic>\out\`. `scripts/ai_img_request.py` hiện chỉ đọc `ai_NN.png`. Clip Flow có dấu ✦ ở góc dưới phải; `webauto/videofix.py strip_video(path, "crop")` cắt dấu đó và ghi đè file.

**Áp dụng ngoại lệ AGENTS.md.** Được sửa:
- `scripts/ai_img_request.py`;
- `tests/test_ai_img_request_stage.py`;
- báo cáo `docs/pm/tickets/GH-179-aivid-report.md`.

Đọc thêm (không sửa) `motion/long/build_long.py` và `motion/long/clip_sheet.py` để biết Long đọc b-roll clip ở đâu, dưới tên và định dạng nào (id clip, thư mục `motion/hf/assets/clips` hay `output/long/<topic>/…`).

Ghi file bằng Python, `encoding="utf-8"`. Trước khi kết thúc, chạy:
`python -c "import subprocess,sys;d=subprocess.run(['git','diff'],capture_output=True,text=True,encoding='utf-8').stdout;sys.exit('MẤT DẤU' if '???' in d or 'Kh?ng' in d else 0)"`

**Việc:**
1. Đọc cả `## vid_NN.mp4` trong prompt.
   - Khi gửi bot: thêm `task: generate_videos` riêng cho các clip còn thiếu, hoặc gộp vào cùng yêu cầu. Ghi rõ cách đã chọn.
   - Cờ `--no-send` giữ nguyên hành vi.
2. Chờ ảnh và clip. Clip về thì:
   - chép sang một thư mục tạm trong repo;
   - gọi `strip_video(path, "crop")`;
   - đặt vào đúng chỗ engine Long đọc b-roll, kèm sidecar hoặc metadata mà engine cần, có `ai_generated: true` và `credit: false` (giống ảnh AI).

   Nếu engine chưa có cách đọc clip AI theo topic thì **không sửa engine**: đặt vào `output/long/<topic>/clips_ai/vid_NN.mp4` và ghi rõ trong báo cáo cách nối vào cảnh, để Lead quyết.
3. Thêm cờ `--images-only` và `--videos-only`.
4. Test (giả lập webhook, `strip_video` và import):
   - đọc đúng cả hai loại mục;
   - clip được cắt rồi đặt đúng chỗ;
   - `--videos-only` không chờ ảnh.

   Chạy `python -m pytest tests -q`.

**Không:** gọi webhook thật, commit, upload.
