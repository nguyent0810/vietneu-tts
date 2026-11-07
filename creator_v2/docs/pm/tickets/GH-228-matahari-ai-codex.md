# GH-228: Mata Hari, gắn ảnh/clip AI đã về (bước 4, vòng cuối)

**Phạm vi:** chỉ ghi `data/long/mata-hari/gen_scenes*.py`, `data/long/mata-hari/ch*.json`, `data/long/mata-hari/spec.json` và báo cáo `docs/pm/tickets/GH-228-matahari-ai-report.md`. Lời đọc (`lines`) giữ nguyên tuyệt đối.

**Tiếng Việt:** ghi file bằng Python `encoding="utf-8"`; trước khi xong chạy lệnh kiểm mất dấu trong brief cảnh `docs/pm/tickets/GH-228-matahari-scenes-codex.md` (phải in `[]`).

**Đã có (Lead soát bằng mắt, đạt):**
- 15 ảnh AI `output/long/mata-hari/img/ai02.jpg … ai16.jpg` (1920×1080), mô tả từng ảnh ở `data/long/mata-hari/ai_prompts.md` (mục `## ai_NN`).
- 6 clip AI `output/long/mata-hari/broll/900001.mp4 … 900006.mp4` (đã cắt sparkle), mô tả ở mục `## vid_NN` cùng file.

**Việc:**
1. Dùng clip `900001–900006` cho các cảnh b-roll hợp nội dung (xem `ai_prompts.md`), thay bớt các lần dùng lặp clip kho chung `198005–198015` (hiện mỗi clip dùng tới 5 lần; sau khi thay, mỗi clip ≤ 3 lần).
2. Gắn ảnh `ai02–ai16` vào các nhịp nhóm B/C trong `visual_plan.md` mà hiện đang dùng ảnh thay thế. Mỗi ảnh AI: `"credit": false`; lần đầu nhóm B xuất hiện trong mỗi chương có chú thích `illus` "TÁI DỰNG MINH HỌA" (như các Long cũ). Mỗi ảnh AI dùng tối đa 3 cảnh.
3. **XÓA `ai01` khỏi `spec.imgs` và không dùng ở đâu** (ảnh hàng lính ở hào Vincennes = mô tả cảnh xử bắn, Lead loại). Các key `ai02–ai16` phải có cảnh dùng.
4. Giữ các luật cảnh (Lead 07/11, rút từ Hòa Thân): mỗi cảnh 2,5–9 giây (ước 4,2 âm tiết/giây vì chưa TTS); phần tử con thứ hai của ledger/timeline/file hiện ≤ 1,0 s từ đầu cảnh; cảnh có clip không dài hơn clip − 0,5 s (clip AI dài ~7,8 s → cảnh ≤ 7,3 s); không neo vào chữ số; không 6 cảnh cùng loại liên tiếp.
5. Đạt khi: `floor.problems(...)` trả `[]`; `PYTHONIOENCODING=utf-8 python motion/variety.py audit mata-hari` đạt; `PYTHONIOENCODING=utf-8 python scripts/long_gate.py mata-hari --min-syl 5000` chỉ còn lỗi "chưa TTS"; `python motion/long/scene_params.py mata-hari` không lỗi.

**Không:** chạy TTS, render; commit; đổi nhánh git; sửa engine.

**Báo cáo** `docs/pm/tickets/GH-228-matahari-ai-report.md`: bảng ảnh/clip AI → chương#cảnh, số cảnh mỗi loại, kết quả các cổng.

**Mata Hari thêm:** không ảnh AI nào thay cho ảnh tư liệu thật của chính Mata Hari; ảnh AI chỉ dựng bối cảnh (phòng, ga tàu, hồ sơ, chiến hào). `ai03` (người phụ nữ quay lưng) chỉ dùng kèm chú thích "TÁI DỰNG MINH HỌA". CH12 không dùng `ai13` (mũ lính) cạnh lời về hành quyết.
