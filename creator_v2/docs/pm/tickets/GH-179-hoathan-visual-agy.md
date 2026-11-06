# GH-179: Hòa Thân, hệ thống hình ảnh cho 14 chương

Đầu vào:
- `data/long/hoa-than/plan.md` (đã duyệt);
- báo cáo tư liệu của bạn `docs/pm/tickets/GH-179-hoathan-research-report.md` (142 ảnh tự do);
- `output/long/hoa-than/research.json`, `ext.json`, `img/`;
- luật kênh trong `CLAUDE.md` (mục floor, ngoại lệ ảnh AI) và `motion/long/SOURCES.md`;
- mẫu cảnh `data/long/golden/ch*.json` và các loại cảnh mà engine Long đang có. Đếm `"type"` trong các file `data/long/*/ch*.json`, ví dụ photo, map, ledger, counter, kinetic, slam, broll, file, date, chart, board, timeline.

## Mục tiêu (chủ kênh, 06/11)
Video tài liệu dài, nhịp hình liên tục: **trung bình cứ 3–5 giây có một thay đổi hình đáng kể**. Đổi hình không bắt buộc là ảnh mới: đổi khung (pan/zoom sang chi tiết), đổi lớp (overlay, chú thích, đường vẽ), hay chuyển sang motion graphic đều tính. Không chương nào được thiếu hình chỉ vì thiếu tư liệu lịch sử.

## Bốn nhóm tài nguyên

| Nhóm | Gồm | Luật bắt buộc |
|---|---|---|
| A. Tư liệu lịch sử | tranh, ảnh, bản đồ, văn bản, hiện vật có nguồn | ghi nguồn và giấy phép (CC BY/BY-SA phải ghi công) |
| B. AI tái dựng bối cảnh | kiến trúc, nội thất, phố xá, sinh hoạt thời Thanh | **không có người thật nhận diện được** (Hòa Thân, Càn Long, Gia Khánh, Lưu Dung, Hòa Hiếu… không bao giờ vẽ bằng AI); người chỉ là bóng, quay lưng hoặc ở xa; không vẽ chữ Hán, chỉ dụ, ấn hay dấu triện giả; không dựng cảnh hành hình. Lần đầu nhóm B xuất hiện trong mỗi chương có nhãn nhỏ kiểu điện ảnh "TÁI DỰNG MINH HỌA" (phong cách #173); không bao giờ gắn nhãn "TƯ LIỆU" |
| C. AI minh họa khái niệm | tiền bạc, quyền lực, tham nhũng, giàu có, xung đột | ẩn dụ (thỏi bạc, cán cân, chuỗi khóa, bóng ghế quyền lực), không giả làm tư liệu, không chữ, không mặt người. Trước khi xin ảnh mới, tra kho chung (`python ../library/tools/assets.py find`, tag `cl`/`hinh_su`/`minh_hoa_chung`) |
| D. Motion graphics (engine) | timeline, bản đồ động, số liệu, sơ đồ quan hệ, trích văn bản | mọi con số và trích dẫn phải có trong plan hoặc nguồn đã mở. Văn bản chỉ dụ chỉ hiện bằng bản dịch tiếng Việt kèm nguồn, không dựng chữ Hán giả |

**Tỉ lệ:** nhóm A là xương sống, ít nhất 50% thời lượng hình. B + C tối đa 25%. D lấp phần còn lại.

**Floor của kênh** (`motion/long/floor.py`) vẫn phải qua:
- ≥ 40 ảnh;
- ≥ 30 cảnh b-roll;
- ≥ 14 loại cảnh;
- kinetic ≤ 38%;
- chữ trên nền trống ≤ 12%.

## Việc
1. Ước thời lượng từng chương: video 25–32 phút, dàn 14 chương theo plan.
2. Với mỗi chương, viết **danh sách nhịp hình**: mỗi nhịp 3–5 giây, ghi các cột
   - nhịp số và khoảng giây;
   - ý lời đọc dự kiến (một dòng, theo plan);
   - nhóm A/B/C/D;
   - tài nguyên cụ thể: tên ảnh hoặc key trong research/img; với B/C là prompt tiếng Anh ngắn; với D là loại cảnh engine kèm dữ liệu;
   - kiểu chuyển động: Ken Burns, pan tới chi tiết, overlay, vẽ đường.
3. Bảng tổng mỗi chương: số nhịp, % thời lượng mỗi nhóm, số ảnh A dùng. Đánh dấu chương thiếu A và ghi cách bù.
4. Gom toàn bộ prompt nhóm B và C vào `data/long/hoa-than/ai_prompts.md`, dạng `## ai_NN.png — <chương>` cùng dòng `- Prompt (tiếng Anh): ...`. Đây là định dạng `scripts/ai_img_request.py` đọc. Prompt nào là video Flow thì đặt tên `## vid_NN.mp4 — <chương>`. Không lặp ý giữa các prompt.
5. Tự kiểm: trung bình nhịp cả video nằm trong 3–5 giây; đạt các ngưỡng floor ước tính; không vi phạm luật nhóm B, C.

**Được ghi:**
- `data/long/hoa-than/visual_plan.md`;
- `data/long/hoa-than/ai_prompts.md`;
- báo cáo `docs/pm/tickets/GH-179-hoathan-visual-report.md`.

Ghi UTF-8. Không sửa code, không viết `script.md`, không gọi Grok Bot, không render, không commit.

**Báo cáo:**
- tổng số nhịp và nhịp trung bình;
- % theo nhóm A/B/C/D;
- số prompt AI (ảnh và video);
- các chương phải bù nhiều nhất;
- ước tính floor.
