# GH-228: Đông Lăng, gắn ảnh/clip AI đã về (bước 4, vòng cuối)

**Phạm vi:** chỉ ghi `data/long/dong-lang/gen_scenes*.py`, `data/long/dong-lang/ch*.json`, `data/long/dong-lang/spec.json` và báo cáo `docs/pm/tickets/GH-228-donglang-ai-report.md`. Lời đọc (`lines`) giữ nguyên tuyệt đối.

**Tiếng Việt:** ghi file bằng Python `encoding="utf-8"`; trước khi xong chạy lệnh kiểm mất dấu trong brief cảnh `docs/pm/tickets/GH-228-donglang-scenes-codex.md` (phải in `[]`).

**Đã có (Lead soát bằng mắt, đạt):**
- 16 ảnh AI `output/long/dong-lang/img/ai01.jpg … ai16.jpg` (1920×1080), mô tả từng ảnh ở `data/long/dong-lang/ai_prompts.md` (mục `## ai_NN`).
- 6 clip AI `output/long/dong-lang/broll/900001.mp4 … 900006.mp4` (đã cắt sparkle), mô tả ở mục `## vid_NN` cùng file.

**Việc:**
1. Thay các clip tạm của Hòa Thân `198101, 198103, 198105, 198107, 198108` trong cảnh Đông Lăng bằng clip `900001–900006` theo đúng nội dung (xem `ai_prompts.md` và `visual_plan.md`). Clip kho chung `198011–198015` được giữ nếu hợp cảnh. Sau khi thay, không cảnh nào còn dùng `1981xx`.
2. Gắn ảnh `ai01–ai16` vào các nhịp nhóm B/C trong `visual_plan.md` mà hiện đang dùng ảnh thay thế. Mỗi ảnh AI: `"credit": false`; lần đầu nhóm B xuất hiện trong mỗi chương có chú thích `illus` "TÁI DỰNG MINH HỌA" (như các Long cũ). Mỗi ảnh AI dùng tối đa 3 cảnh.
3. Khai báo `ai01–ai16` trong `spec.imgs` (nếu chưa), không để key nào không có cảnh dùng.
4. Giữ các luật cảnh (Lead 07/11, rút từ Hòa Thân): mỗi cảnh 2,5–9 giây (ước 4,2 âm tiết/giây vì chưa TTS); phần tử con thứ hai của ledger/timeline/file hiện ≤ 1,0 s từ đầu cảnh; cảnh có clip không dài hơn clip − 0,5 s (clip AI dài ~7,8 s → cảnh ≤ 7,3 s); không neo vào chữ số; không 6 cảnh cùng loại liên tiếp.
5. Đạt khi: `floor.problems(...)` trả `[]`; `PYTHONIOENCODING=utf-8 python motion/variety.py audit dong-lang` đạt; `PYTHONIOENCODING=utf-8 python scripts/long_gate.py dong-lang --min-syl 5000` chỉ còn lỗi "chưa TTS"; `python motion/long/scene_params.py dong-lang` không lỗi.

**Không:** chạy TTS, render; commit; đổi nhánh git; sửa engine.

**Báo cáo** `docs/pm/tickets/GH-228-donglang-ai-report.md`: bảng ảnh/clip AI → chương#cảnh, số cảnh mỗi loại, kết quả các cổng.
