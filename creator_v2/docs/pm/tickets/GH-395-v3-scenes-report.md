# GH-395: báo cáo dựng lại cảnh Long CL `cl-dich-nhan-kiet` theo kịch bản v3 (16/11/2026)

Người làm: subagent (Sonnet), worktree `wt-dnk3/creator_v2`. Không commit, không push, không upload, không TTS, không render, không đọc thư mục credentials.

File ghi: `data/long/cl-dich-nhan-kiet/{gen_scenes.py, gen_scenes2.py, spec_dnk.py, spec.json, ch00..ch13.json}` (chỉ `scenes`, `hud`, `bgm`; `lines` và `title` của chNN.json không đổi, đã so với HEAD) và file này.

## 1. Số liệu

- **314 cảnh**, 14 chương, 16 loại cảnh: kinetic 93, slam 61, quote 37, photo 19, broll 19, org 10, ledger 13, file 13, question 13, chapter 13, date 9, counter 5, myth 4, map 3, timeline 1, print 1.
- `floor.measure`: 5.728 âm tiết, **74 ảnh**, **31 cảnh b-roll** (sàn 30; mỗi clip c1–c8 tối đa 4 lần: c1 4, c2 4, c3 4, c4 4, c6 4, c7 4, c8 4, c5 3), kinetic **29,6%** (trần 38%), chữ trên nền trống 0%.
- Cảnh `file`: 13/314 = 4,1% (trần 12%), cách nhau ≥ 5 cảnh (gate floor báo lỗi ở bản nháp đầu khi hai thẻ file cách 3 cảnh, đã đổi thẻ Vương Đức Thọ ở CH08 thành kinetic).
- Mỗi ảnh `img` ≤ 2 lần (trần 3). Ảnh làm nền (`bg`) tối đa 8 lần/ảnh sau bước cân nền; không có chữ hiển thị lặp.
- Độ dài cảnh theo timing giả: 3,7 từ/giây tối đa 8,6 s; 4,4 từ/giây tối thiểu 2,6 s (trung bình 5,6 s và 4,8 s).
- Số cảnh theo chương: 11, 26, 19, 19, 20, 25, 19, 20, 22, 22, 25, 18, 29, 39.

## 2. Luật cảnh đã áp

- **10 giây đầu (CH00):** cảnh 0 là clip c1 (`broll`, động từ khung 0), cảnh 1 và 2 là ảnh có `move` (chân dung Địch Nhân Kiệt tông noir, tranh Võ Tắc Thiên tông noir). Thẻ chữ đầu tiên là slam "PHẢN LÀ THẬT!" neo vào từ "cam" của câu trích, bắt đầu ở giây 10,8 / 11,5 / 12,6 (4,4 / 4,1 / 3,7 từ/giây). Ba nhịp hình mạnh đầu (clip, ảnh noir, ảnh động) rồi slam, câu hỏi, clip c8 ở giây ~28–38; cắt 2,7–5 giây.
- **Phỏng dựng:** cả 31 câu `{pd}` có cảnh riêng gắn nhãn `PHỎNG DỰNG` (ảnh: "PHỎNG DỰNG", hiện vật: "PHỎNG DỰNG · HIỆN VẬT", clip: "PHỎNG DỰNG · MINH HỌA CHUNG"). `gen_scenes.py` có hàm `kiem_tra_pd` đối chiếu bảng `PD_LINES` (số dòng theo chNN.json) và dừng nếu cảnh bao câu đó thiếu nhãn.
- **Nguồn trên hình:** 29 cảnh có `srcnote` "NGUỒN: …" (con số 17.000, 850, 1.700 miếu, mốc 675/676/679/691/697/698/700/705, nhật ký Bành Trạch, phim/tiểu thuyết, v.v.); 37 thẻ trích dẫn lấy nguyên văn từ dòng lời đọc (hàm `QX`), nguồn ghi trên thẻ.
- Câu quá dài (30 chữ, ví dụ "Bọn Giai Cố…" ở CH10) tách hai thẻ quote để cảnh ≤ 9 s ở 3,7 từ/giây.
- Chữ lớn: `ngat_dong` ngắt slam và kinetic không `sm` về ≤ 16 ký tự/dòng; nhãn org ≤ 14 ký tự; tiêu đề thẻ chương ≤ 12 ký tự/dòng. Ảnh dọc có `focus` (dnk_a [0,5; 0,78]; còn lại [0,5; 0,3–0,45]); ảnh `wu1..3, off*, yao…` làm nền được gán focus theo kích thước thật trong research.json.
- Không có AI mô phỏng người thật, không ảnh bạo lực. Cảnh đập đầu/nhận tội dùng chữ và cửa ngục tối (clip c8), không hình người.
- Ảnh chưa có ghi công trong `CREDITS` (henan, changmap, horse1, qianmap, wh1, coin, cmodel2, wustat, zodiac) không dùng.

## 3. Spec

`title` và `youtube.titles[0]` = "Tể Tướng Tự Nhận Mình Phản: Ba Chữ Cứu Mạng Địch Nhân Kiệt" (58 ký tự); hai phương án sau lấy từ `script.md`: "Mảnh Lụa Giấu Trong Áo Bông: Tể Tướng Thoát Chết Ra Sao?" và "Xử Xong Cho 17.000 Người Không Ai Oan, Rồi Nhận Mình Phản?". Giữ nguyên: playlist "Ngoài Đời Thật", `publish_at` 2026-11-24T14:00:00Z, `approved`, `mix_levels.CL` 0,27 / 0,08 / 3,0, thumb `t1.jpg`, look `rose`. Đã cập nhật: `youtube.summary`, `chapter_titles` (14 tiêu đề theo script v3), `video_credits` (74 ảnh), thẻ chương (`CARDS`).

## 4. Cổng đã chạy (timing giả ngoài repo, wav im lặng, đã xóa)

- `python data/long/cl-dich-nhan-kiet/gen_scenes.py`: sạch (mốc `[dòng, từ]` có thật và tăng dần, ảnh `img` ≤ 3, ghi công đủ, `kiem_tra_pd` đạt).
- `python scripts/check_scene_durations.py cl-dich-nhan-kiet --out <timing giả>` ở **3,7 / 4,1 / 4,4 từ/giây: TỔNG LỖI 0 cả ba** (gồm nhịp cảnh, lint html tiêu đề thẻ, craft, floor).
- `python motion/long/opening_gate.py cl-dich-nhan-kiet --out-root <timing giả cha>`: **OK** ở cả ba tốc độ. Worktree này chưa có O9/O10 trong `opening_gate.py`, nên các kiểm tra "không thẻ chữ trước giây 10" và "cảnh đầu là hình động" được đối chiếu bằng tay trên cảnh đã `plan()` (xem mục 2).

## 5. Việc còn lại cho Lead

1. Cảnh báo (không chặn) của `opening_gate`: "Từ khóa tiêu đề chưa nói trước 20s" (tiêu đề mới có cụm "Tể Tướng Tự Nhận Mình Phản", lời mở đầu nói "tể tướng… tự nhận mình mưu phản", chưa khớp nguyên cụm). Nếu muốn hết cảnh báo thì chỉnh câu 0 của CH00 trong script (ngoài phạm vi ticket này).
2. Chưa TTS: sau `build_long.py ... tts` chạy lại `check_scene_durations.py` không `--out` và `opening_gate.py`, nhất là cảnh slam "PHẢN LÀ THẬT!" (phải sau giây 10) và các cảnh 2,6–2,9 s ở tốc độ nhanh.
3. Clip chung vẫn là 8 clip (lồng đèn, thư phòng, mái tuyết, mực, rương vàng, thuyền sương, cuộn giấy, cửa ngục) gắn nhãn "MINH HỌA CHUNG"/"PHỎNG DỰNG · MINH HỌA CHUNG". Dùng hết 31/32 lượt cho phép; muốn thêm cảnh clip phải có clip mới.
4. Nhiều nền thẻ chữ dùng tượng gốm quan đường (off1–off10) và tranh vách mộ làm hình chung; ảnh tư liệu tự do không có cảnh ngục hay tra khảo thời Đường.
5. `motion/variety.py audit` không chạy ở worktree này (sổ lịch ở checkout sản xuất).
