# GH-307: Lưu Gù, bước 4 phần C: gắn ảnh minh họa AI và b-roll (Codex)

Đọc issue: `gh issue view 307 --repo nguyent0810/vietneu-tts`. Cảnh CH00–CH13 đã xong (phần A và B). Phần này gắn tư liệu minh họa AI để **floor đạt**. Hiện floor thiếu cảnh b-roll: sàn là ≥30 cảnh b-roll.

Chủ kênh đã duyệt ngày 12/11/2026: ảnh và clip minh họa chung do AI tạo, **không người, không mặt, không chữ**, gắn tag `minh_hoa_chung` và chú thích "TÁI DỰNG MINH HỌA".

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-luugu`, nhánh `long/cl-luu-gu`. Đường dẫn tính từ `creator_v2/`. Lead commit.
- Python: `python`, hoặc `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.

## Sửa brief (lượt 2, sau báo cáo `GH-307-media-report.r1.md`)
Lượt 1 đúng khi dừng lại. Lead nới phạm vi như sau:
- **Cách chính để giảm chữ nền trống là thêm nền, không thay cảnh.** `floor` không tính một cảnh chữ (`kinetic`, `slam`, `date`, `counter`, `question`, `quote`) là "nền trống" khi cảnh có `bg`, `img` hoặc `vid`. Long Hòa Thân dùng `bg=` 266 lần (xem `data/long/hoa-than/gen_scenes*.py`). Gắn `bg="<khóa ảnh>"` cho cảnh chữ, hoặc `vid=V[...]` (cảnh có `vid` còn được tính là cảnh b-roll).
- **Nguồn nền:** ngoài ảnh AI, dùng thêm ảnh thật trong `research.json` (167 ảnh tự do, hiện mới dùng khoảng 44). Thêm khóa vào `IMGS` bằng `im(i, must)`, giữ đúng các ảnh lạc đề đã cấm trong brief phần A (`GH-307-scenesA-codex.md`). Ảnh nền phải hợp nghĩa câu ở mức bối cảnh, ví dụ cung điện, nha môn, thư pháp, quan lại chung.
- Luật 5 đổi thành: mỗi clip ≤8 lần (cách nhau ≥1 chương); mỗi ảnh AI ≤6 lần; mỗi ảnh research ≤4 lần làm nền.
- **Được** chạy `gen_scenes.py`. Lệnh này ghi lại `spec.json` qua `write(...)` là cách làm bình thường (khai báo ảnh đã dùng). Được sửa đoạn cập nhật spec trong `gen_scenes.py` nếu cần, nhưng không đổi title, channel, theme, look, nhạc.
- `long_gate` trượt vì thiếu TTS và thiếu `spec.youtube` là **bình thường** ở bước này; Lead làm sau. Không cần sửa.
- Mục tiêu đạt: `floor.measure`/`problems` không còn lỗi b-roll (≥30) và chữ nền trống (≤12%); ảnh ≥40; kinetic ≤38%; variety đạt. `floor.py` không in gì khi chạy CLI thì gọi `measure`/`problems` từ Python như lượt 1.

## Tư liệu có sẵn (Lead đã import, không tạo thêm, không gọi mạng)

**Ảnh** nằm ở `output/long/cl-luu-gu/img/aiNN.jpg` (1920×1080). Khai báo `"aiNN": "EXT:ai:ai_NN"`. Đã có đủ ai01–ai18 (Lead import ai14).

| Mã | Nội dung | Mã | Nội dung |
|---|---|---|---|
| ai01 | bàn thư phòng, cuộn giấy, nến | ai10 | sông Hồ Nam sương sớm, thuyền neo |
| ai02 | cổng phủ quan đêm tuyết, đèn lồng | ai11 | kho cổ, rương nén bạc, đèn dầu |
| ai03 | phòng giam song gỗ, đuốc | ai12 | quan đạo Sơn Đông, đồng bằng thu |
| ai04 | dãy buồng thi trường cống viện | ai13 | thư phòng hoàng tử bỏ trống |
| ai05 | kiệu quan trước cổng thành | ai14 | đại điện trống, ngai trong bóng tối |
| ai06 | tường thành đất, gió bụi | ai15 | sân cung tuyết, vải tang trắng |
| ai07 | sổ sách đóng chỉ, bàn tính, nến | ai16 | dải lụa trắng vắt xà nhà |
| ai08 | tập thơ mở, giấy ngả vàng | ai17 | sân khấu kinh kịch trống |
| ai09 | mộ đá phủ rêu, nghĩa địa hoang | ai18 | đầu bút lông chấm mực |

**Clip** nằm ở `output/long/cl-luu-gu/broll/9000NN.mp4` (đã có json `ai_generated`, `credit: false`). Khai báo `V = {"v1":"900001", ..., "v8":"900008"}`.

| Mã | Nội dung | Lưu ý |
|---|---|---|
| v1 | hành lang có đèn lồng | |
| v2 | nến cháy trên bàn thư phòng, khói | |
| v3 | tuyết rơi trên mái cung điện đêm | |
| v4 | mực loang trong chén nước sứ | |
| v5 | rương **thỏi vàng** dưới đèn | chỉ dùng cho câu nói chung về "của cải", "tài sản tịch biên". **Không** dùng cho câu nói rõ "bạc" hay "kho bạc" |
| v6 | sương trên sông, thuyền trôi | |
| v7 | cuộn giấy trắng trên bàn gỗ, nến | |
| v8 | cửa ngục gỗ, đuốc trên tường đá | |

## Khuôn mẫu
Dùng đúng cách của `data/long/hoa-than/gen_scenes.py` (dòng 13–50):
- `TD = "TÁI DỰNG MINH HỌA"`;
- hàm `ai(at, img, cap=False, ...)`: cảnh photo, `credit=False`, có `illus=TD` khi `cap=True`;
- hàm `clip(at, v, *items, tone="noir", veil=0.4)`: cảnh broll, có `illus` và `kin`;
- cảnh `slam` và `kinetic` có `vid=V[...]` làm nền.

Đọc `motion/long/floor.py` để biết cảnh nào được đếm là "cảnh có b-roll".

## Luật
1. **Thay, không chèn.** Đổi cảnh chữ trên nền trống (naked) hoặc cảnh motion lặp sang ảnh hay clip AI. Giữ nhịp 3–5 giây/cảnh và neo `at`/`hitAt` vào câu và từ thật. Không đổi tổng thời lượng.
2. **Đúng nghĩa câu đọc.** Ảnh và clip phải khớp nội dung câu: phòng giam cho câu về ngục, buồng thi cho câu về khoa cử, quan đạo Sơn Đông cho chuyến tra án 1782, và tương tự. Không đặt minh họa cạnh câu nói về một người cụ thể theo kiểu khiến người xem tưởng đó là ảnh thật của người đó hay nơi đó.
3. **Chú thích.** Ảnh AI đầu tiên trong mỗi chương phải có `cap=True` ("TÁI DỰNG MINH HỌA"). Clip dùng `illus` minh họa, giống hằng `FILMV` của Hòa Thân hoặc chính `TD`.
4. **Giữ xương sống.** Không thay ảnh chân dung hay thư pháp thật của Lưu Dung, không thay bản đồ, timeline, ledger mang số liệu.
5. **Mỗi clip dùng ≤6 lần cả video.** Hai lần dùng cùng một clip cách nhau ≥2 chương. Mỗi ảnh AI dùng ≤3 lần.
6. Mục tiêu sau khi sửa:
   - `floor` đạt (≥30 cảnh b-roll);
   - `variety audit` và `cadence` vẫn đạt.

## File được ghi
- `data/long/cl-luu-gu/gen_scenes.py`, `gen_scenes2.py`, `ch00.json` đến `ch13.json` (sinh lại).
- Báo cáo.
- Không sửa engine, `scenekit`, `build_long.py`, `script.md`, `factcheck.md`. `spec.json` chỉ được ghi qua `gen_scenes.py`. Không sửa ảnh hay clip. Không render, không TTS.

## Kiểm (từ creator_v2 của worktree)
1. `python data/long/cl-luu-gu/gen_scenes.py`
2. `python motion/long/floor.py cl-luu-gu`: phải đạt mọi mục, trừ mục cần TTS hoặc spec.youtube (nếu có).
3. `PYTHONIOENCODING=utf-8 python motion/variety.py audit cl-luu-gu`
4. `python motion/long/cadence.py cl-luu-gu`
5. `python motion/long/scene_params.py cl-luu-gu`

## Tiếng Việt
Ghi mọi file bằng Python `encoding="utf-8"`, rồi grep để chắc không có `???` hay `�`.

## Báo cáo
`docs/pm/tickets/GH-307-media-report.md`, gồm:
- số cảnh b-roll trước và sau;
- bảng "chương → cảnh nào đổi sang ảnh hay clip nào, neo câu số mấy";
- số lần dùng mỗi clip và mỗi ảnh;
- kết quả 5 lệnh kiểm.

Không render, không commit, không đăng.
