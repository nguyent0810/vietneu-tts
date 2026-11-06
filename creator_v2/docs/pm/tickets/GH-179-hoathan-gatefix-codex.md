# GH-179: Hòa Thân, sửa cho qua `long_gate` (trừ TTS)

Cảnh 14 chương đã có (scenesA–D): `gen_scenes*.py`, `chNN.json`, `spec.json`. `python scripts/long_gate.py hoa-than --min-syl 5000` đang trượt 12 lỗi. Lỗi "chưa TTS" là bình thường, để agy làm sau. Sửa hết các lỗi còn lại.

**Được sửa:** `data/long/hoa-than/gen_scenes*.py`, `chNN.json`, `spec.json`, `factcheck.md`. **Không sửa `script.md`**: Lead vừa sửa 2 câu, bạn chỉ đồng bộ sang cảnh. Ghi file bằng Python, `encoding="utf-8"`.

1. **Đồng bộ 2 câu Lead đã sửa trong `script.md`** sang `ch05.json` và `ch09.json`, đồng thời sửa trong `gen_scenes*.py` để chạy lại không mất:
   - "…khoản mà người ta đang tranh cãi khi nói về kho vàng."
   - "…2,8 triệu lạng bạc cất giữ."

   Cổng coi cụm "trong kho" là ghi chú nội bộ.
2. **Năm ảnh dùng quá 3 lần:** canlong 6, hoa 7, luudung 4, giakhanh 9, hieu 6. Thay các lần dư bằng ảnh khác cùng chủ đề trong `output/long/hoa-than/img/` (142 ảnh tư liệu, xem `research.json`). Có thể dùng chi tiết hoặc crop khác của tranh khác, bản đồ, tranh cung đình. Không dùng ảnh AI cho người thật.
3. **ch12 chỉ có 4 loại cảnh** (date, ledger, photo, timeline). Thêm ít nhất 1 loại hợp nội dung, ví dụ map, file hoặc quote.
4. **`spec.youtube`** thêm `publish_at`, `playlist`, `chapter_titles`, `video_credits`, theo mẫu Long CL `data/long/bao-thanh-thien/spec.json`.
   - `publish_at`: để `"2026-11-15T14:00:00Z"`, chỉ là giờ dự kiến; Lead sẽ chốt lịch.
   - `playlist`: dùng playlist "Ngoài Đời Thật" như Bao Thanh Thiên.
   - `chapter_titles`: lấy theo 14 chương.
   - `video_credits`: ghi công đúng các ảnh CC BY / CC BY-SA đã dùng (artist + license từ `img/*.json`).
   - `sources`: ít nhất 8 URL công khai, lấy từ bảng nguồn trong `script.md` và `factcheck.md`.
   - `titles`: để `["TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Hòa Thân Bị Ép Chết 15 Ngày Sau Khi Càn Long Mất"]`, chỉ là bản tạm; Lead sẽ chốt.
5. **Bảng `say`** (phát âm) cho 51 tên hoặc thuật ngữ nước ngoài mà cổng liệt kê. Định dạng xem `bao-thanh-thien/spec.json` và cách `long_gate.py` kiểm. Tên Hán-Việt đọc như chữ Việt thì không cần `say`. Tên Latin/Anh (Macartney, Harris, Pittsburgh…) ghi cách đọc tiếng Việt.
6. **`factcheck_lint`:** cảnh hiện có 6 câu TRÍCH DỊCH, `factcheck.md` mới có nguyên văn cho 5. Tìm câu thứ 6 trong `chNN.json`, rồi thêm dòng "TRÍCH DỊCH — … — nguyên văn: … — URL" có nguồn thật (đã mở). Không có nguồn thì bỏ câu trích đó khỏi cảnh.
7. Chạy lại `scene_params`, `floor.py`, `variety.py audit hoa-than`, `cadence.py hoa-than`, `factcheck_lint.py hoa-than`, và `long_gate.py hoa-than --min-syl 5000`. Kết quả phải chỉ còn lỗi "chưa TTS".

**Báo cáo** `docs/pm/tickets/GH-179-hoathan-gatefix-report.md` (UTF-8): kết quả từng cổng, các ảnh đã thay, câu trích thứ 6.
