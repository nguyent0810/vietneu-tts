# YCV-ju9q · M1 W2: dựng cảnh, spec, SAY và prompt ảnh AI cho `mim-jobs-1985`

Chủ kênh đã duyệt `script.md` ngày 29/10 (1.932 âm tiết, lint 0 lỗi).

- **Không sửa lời đọc.**
- Không render, không upload, không chạy `thumb.py`, không gọi bot sinh ảnh.
- Báo cáo ghi vào `docs/pm/tickets/YCV-ju9q-M1-W2-ket-qua.md`.

Đây là **Long thử nghiệm** cho cổng phủ hình (YCV-adbc) và luật cảnh (YCV-ahg7). Mục 6 và 7 bên dưới là phần mới so với mẫu W2 cũ.

## Chỉ đọc

| File | Ghi chú |
|---|---|
| Ticket này | |
| `docs/codex/long-cheatsheet.md` | Toàn bộ, nhất là "Bài học Moneyball" |
| `docs/codex/long-rules.md` | Mục "Lỗi đã gặp", "Ảnh AI", "Cấm lách cổng bằng cảnh đệm" |
| `data/long/mim-moneyball/gen_scenes.py` | **Khung để chép.** Có `fix_anchors`. Bỏ `SPLIT`/`shift_anchors` |
| `data/long/mim-jobs-1985/script.md`, `factcheck.md` (mục HÌNH), `research.md` (§4 ảnh, §9), các `chNN.json` | |
| `docs/pm/ai-image/mim.yaml` | Khung phong cách và cụm cấm cho prompt ảnh AI |

Không đọc engine, không grep repo.

## Làm

1. **Chép khung** sang `data/long/mim-jobs-1985/gen_scenes.py`, rồi thay nội dung.
   - `publish_at`: `2026-12-01T13:00:00Z` (01/12, 20:00 giờ VN; lịch còn chờ chủ kênh chốt).
   - `SAY`: phiên âm mọi tên tiếng Anh và viết tắt: Steve Jobs, Apple, Sculley, Pepsi, Macintosh, NeXT, NeXTSTEP, OPENSTEP, WebObjects, Pixar, Lucasfilm, Alvy Ray Smith, Toy Story, CERN, Tim Berners-Lee, Be, BeOS, Mac OS X, Gil Amelio, Stanford, Computer History Museum, Cult of Mac, Technologizer, San Jose Mercury News, The Register, Times of India, CEO, 10-K, …
   - **Mô-típ "đường vòng 1985 → 1997":** dùng `LEDGER`/`ROWS`, mỗi chương thêm một dòng, mỗi dòng tối đa 26 ký tự.
   - Đồ họa nên có:
     - `timeline` 1983 → 2001;
     - bảng hai con số 400 / 427 triệu (ghi nguồn: thông cáo / 10-K SEC);
     - `bars` doanh thu FY1996 / FY1997;
     - `counter` cho 50 nghìn máy và 230/530 người.
2. **Ảnh tư liệu.** Lấy ảnh trong research §4 và các ảnh NeXT Computer/CERN đã ghi trong `factcheck.md` mục HÌNH. Chỉ dùng ảnh PD, CC0 hoặc CC BY; ghi công trong `credits`.
   - Cảnh ảnh Sculley năm 2006 phải ghi rõ năm trên màn hình.
   - Không dùng clip keynote, ảnh báo chí hay hình từ phim. Logo Apple/NeXT/Pixar không được chiếm cả khung.
3. **Viết `ai_prompts.md`**, tối đa 6 ảnh.
   - Mỗi mục bắt đầu bằng `## ai_NN.png — …`, đúng 2 dấu `#`.
   - Prompt gồm:
     - khối phong cách lấy từ `docs/pm/ai-image/mim.yaml`;
     - chủ thể viết **theo đúng nghĩa câu** mà ảnh minh họa;
     - phần cấm của hồ sơ.
   - Người thật chỉ vẽ theo dáng gốc, góc nghiêng quay đi hoặc từ phía sau, có ghi ảnh tham chiếu.
   - Cảnh dùng ảnh AI phải có `"credit": false`. Nhãn `illus` "ẢNH MINH HỌA" giữ nguyên.
4. **Tải clip:** `python motion/long/pexels.py get mim-jobs-1985 <id> …`. Nếu clip báo "không có bản ngang" thì dùng `search`.
5. **Neo:**
   - neo tăng dần;
   - không neo vào chữ số;
   - phần tử đầu tiên của `org`/`timeline` neo cùng mốc với cảnh.
6. **Cổng phủ hình (mới).**
   - Chạy `python motion/long/coverage_lint.py mim-jobs-1985` sau khi có `timing.json`.
   - Mục tiêu:
     - **chỉ chữ ≤ 22%**;
     - **chuỗi chỉ chữ ≤ 17 giây**.
   - Nếu trượt, đổi cảnh chữ thành ảnh, clip hoặc đồ họa có nghĩa. Không thêm cảnh đệm vô nghĩa (luật "cấm lách cổng").
   - Ghi số liệu trước và sau vào báo cáo.
7. **Luật cảnh (mới).**
   - Chạy `python motion/long/scene_rules.py mim-jobs-1985`.
   - Áp các đề xuất hợp lý: đổi `move` khi hai ảnh liền nhau cùng hiệu ứng; thêm `zoom` hoặc `circles` cho ảnh dài hơn 8 giây; chia shot cho ảnh dài hơn 12 giây.
   - Ghi trong báo cáo đề xuất nào đã áp, đề xuất nào bỏ, kèm lý do.
8. **Chạy html.**
   - Thứ tự: `gen_scenes.py --standin` → `script_lines.py` → `build_long.py mim-jobs-1985 tts` (đủ 9 chương) → `build_long.py mim-jobs-1985 html`.
   - Phải in đủ 9 dòng `chNN: … -> …html`, không có dòng `Error`.
   - Sau đó chạy lại bản thật: `gen_scenes.py` rồi `script_lines.py`.
   - Nếu `tts` hoặc `html` hỏng vì sandbox (`EPERM`, `spawn`), ghi rõ lệnh và lỗi vào báo cáo rồi dừng bước đó, không lách. Claude hoặc agy sẽ chạy tiếp.
9. **Soát clip.** Chạy `clip_sheet.py`, rồi mở `qa_clips.jpg` xem từng clip. Thay clip có logo hoặc chữ đọc được.
10. **Cổng cuối.** Chạy `python scripts/long_gate.py mim-jobs-1985 --min-syl 1900`. Phải ra **ĐẠT**; nếu chỉ thiếu ảnh AI thì chấp nhận.

## Báo cáo

- kết quả `html` (x/9), `long_gate`, `clip_sheet`, kèm danh sách clip đã thay;
- số liệu `coverage_lint` trước và sau;
- các đề xuất `scene_rules` đã áp và đã bỏ;
- số ảnh AI cần tạo.
