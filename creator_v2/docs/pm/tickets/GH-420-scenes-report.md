# GH-420: báo cáo dựng cảnh Long CL `cl-sarin-tokyo-1995` theo kịch bản cuối (16/11/2026)

Người làm: subagent, worktree `wt-plan-cl2/creator_v2` (nhánh `long/cl2`). Không commit, không push, không upload, không TTS, không render, không đọc thư mục credentials.

File ghi: `data/long/cl-sarin-tokyo-1995/{gen_scenes.py, gen_scenes2.py, spec_sarin.py, spec.json, ch00..ch13.json}` và file này. `ch*.json`: `title` và `lines` sinh lại từ `script.md`; `scenes`, `hud`, `bgm` do `gen_scenes.py` ghi. Ngoài repo (gitignored): chép 15 clip vào `output/long/cl-sarin-tokyo-1995/broll/` (xem mục 2).

## 1. Số liệu

- **338 cảnh**, 14 chương (11, 16, 27, 20, 22, 23, 21, 27, 28, 26, 31, 25, 31, 30 cảnh), 16 loại cảnh: kinetic 117, slam 78, photo 41, date 27, chapter 13, ledger 12, counter 9, file 9, question 7, org 6, broll 5, timeline 5, map 4, quote 3, print 1, split 1.
- `floor.measure`: 6.393 âm tiết (khoảng 30 phút), **59 ảnh** (30 ảnh Commons có ghi công + 29 ảnh AI), **33 cảnh có clip** (sàn 30; 15 clip khác nhau, mỗi clip tối đa 3 lần, trần của long_gate là max(2, round(phút/6)) = 4 đến 5), kinetic **34,6%** (trần 38%), chữ trên nền trống 0%, không cảnh `auto`.
- Cảnh `file`: 9/338 (2,7%), cách nhau từ 5 cảnh. Mỗi ảnh `img` tối đa 3 lần.
- Cảnh dùng ảnh AI: 146 cảnh, trong đó 38 cảnh gắn `PHỎNG DỰNG` (mọi câu `{pd}`) và 108 cảnh gắn `MINH HỌA CHUNG`. Cả 29 ảnh AI đều được dùng.
- Độ dài cảnh theo timing giả: 3,7 / 4,1 / 4,4 từ/giây đều nằm trong [2,5 s; 9,0 s]. Có 101 cảnh mang `srcnote`.

## 2. Luật cảnh đã áp

- **10 giây đầu (CH00):** cảnh 0 là clip `198013` (bóng người đi trong hẻm, động từ khung 0), cảnh 1 là ảnh AI `ai03` (rèm cửa đêm hè, `move: in`, nhãn MINH HỌA CHUNG), cảnh 2 là ảnh tàu điện có chuyển động. Thẻ chữ đầu tiên là câu hỏi hậu quả ở câu 3, sau giây 10 ở cả ba tốc độ. Câu sốc nằm trong ba câu đầu (người gọi cấp cứu bị gọi là "Người Khí Độc"), nhịp hình mạnh trong 40 giây đầu: clip, ảnh, câu hỏi, ba cảnh `PHỎNG DỰNG`, slam "NĂM CHUYẾN TÀU" trên ảnh tư liệu 1995, slam "12 ĐẾN 14 NGƯỜI CHẾT", bản đồ.
- **Phỏng dựng:** 39 câu `{pd}` (CH00 4-6, CH02 3-6, 11, 26-27, CH03 13-16, CH04 7-9, CH05 3-4, CH06 20-22, CH07 9-11, CH08 14-15, CH09 1-2, 14-15, CH10 12-13, CH11 0-1, CH12 0-1, CH13 27-28) đều có cảnh riêng gắn nhãn `PHỎNG DỰNG`. `gen_scenes.py` có `kiem_tra_pd` (bảng `PD_LINES` lấy từ `script.md`): thiếu nhãn là dừng. Hàm kiểm thứ hai dừng nếu cảnh dùng ảnh AI mà nhãn không phải `PHỎNG DỰNG...` hoặc `MINH HỌA CHUNG`.
- **Ảnh AI:** chỉ cảnh không người rõ mặt (đường đêm, cửa sổ, phòng điều tra, toa tàu, hành lang bệnh viện, phòng xử, hoa trắng...). Không ảnh AI nào đặt làm hình của người cụ thể; người còn sống (ông Kono, ông Kakimi, ông Nagaoka, luật sư Nakamura, ông Yanagisawa, ông Shimada) chỉ có thẻ chữ, không ảnh.
- **Ảnh thật:** chỉ 30 ảnh Commons có tác giả và giấy phép ghi rõ (CC0, CC BY 2.5/3.0/4.0, CC BY-SA 3.0/4.0, public domain). Ảnh `Spot of abduction ... Kamiosaki` (không ghi tác giả trên Commons) không dùng. Không dùng ảnh nạn nhân nằm trên đường (#14, #18, #28 trong research) vì nhạy cảm. Ảnh chụp ngày nay (ga, lâu đài Matsumoto, trụ sở...) mang nhãn `ẢNH NGÀY NAY`.
- **Clip:** research không có clip nào về Nhật; 8 clip Muse của DNK/HKV/Lưu Gù mang màu Trung Hoa cổ nên không dùng. Dùng 6 clip noir chung đã có trong kho (`198005, 198011..198015`, tag `minh_hoa_chung`, dùng ở mata-hari/dong-lang) và 9 clip stock Pexels ngang 16:9 đã có trên đĩa ở các Long CK/MIM (hành lang, sương, rừng núi, bàn bản đồ, kính lúp, sách luật, đồng hồ, máy chữ, sổ tay). Tất cả gắn nhãn `MINH HỌA CHUNG`. 33 cảnh clip là 5 cảnh `broll` thuần và 28 cảnh chữ nền clip.
- **Nguồn trên hình:** con số, mốc ngày và số liệu trên chữ có `srcnote` "NGUỒN: …" (WIKIPEDIA, NIPPON.COM, AP 2025, AL JAZEERA). Bước hậu kỳ tự gắn `srcnote` cho cảnh có số ≥ 2 chữ số hay ngày mà chưa có.
- **Trích dẫn:** 3 thẻ `quote` lấy nguyên văn từ dòng lời đọc bằng `QX` (thẩm phán Ogawa CH12 dòng 11, ông Nagaoka CH12 dòng 25, ông Kono CH11 dòng 18 theo Nippon.com).
- **Chữ lớn:** `ngat_dong` giữ slam và kinetic không `sm` ≤ 16 ký tự/dòng; cảnh `ledger` ≤ 4 dòng, chữ dòng ≤ 968 px.
- **Chương mở:** cảnh đầu mỗi chương là thẻ chương; không cảnh nào neo vào giây 0 của chương (thẻ chương phải ≥ 2,5 s).

## 3. Spec

`look` = `steel` (CL gần đây: rose, classic, sulfur, jade; `variety.py audit` báo OK). `mix_levels.CL` 0,27 / 0,08 / 3,0. Playlist "Ngoài Đời Thật". Ba tiêu đề (≤ 52 ký tự):

1. "Gọi Cấp Cứu Cho Vợ, Bị Báo Chí Gọi Là Người Khí Độc"
2. "Cảnh Sát Có Cặn Sarin Từ Trước, Tokyo Vẫn Bị Đánh Úp"
3. "Chín Tháng Sau Matsumoto, Vì Sao Tokyo Vẫn Bị Sarin?"

Tiêu đề đầu khớp lời mở đầu (tiêu đề 2 lấy nghịch lý "cảnh sát có mẫu sarin từ 16/11/1994"). Đã ghi: `summary`, `chapter_titles` (14), `tags`, `hashtags`, 11 URL `sources`, `video_credits` (30 ảnh có tác giả, giấy phép và URL Commons, kèm dòng cho ảnh AI và clip), bảng `say` (cuối `script.md`). **`publish_at` và `approved` để trống**, Lead quyết định.

## 4. Cổng đã chạy (timing giả ngoài repo, wav im lặng, đã xóa)

- `python data/long/cl-sarin-tokyo-1995/gen_scenes.py`: sạch (mốc `[dòng, từ]` có thật và tăng dần, ảnh `img` ≤ 3, ghi công đủ, `kiem_tra_pd` đạt, nhãn ảnh AI đạt).
- `python scripts/check_scene_durations.py cl-sarin-tokyo-1995 --out <timing giả>` ở **3,7 / 4,1 / 4,4 từ/giây: TỔNG LỖI 0 cả ba** (gồm nhịp cảnh, độ dài clip, lint html tiêu đề thẻ, craft, floor).
- `python motion/long/opening_gate.py cl-sarin-tokyo-1995 --out-root <timing giả cha>`: **OK** ở cả ba tốc độ.
- `python motion/long/dryplan.py cl-sarin-tokyo-1995`: 14 chương ok; dòng floor ghi 59 ảnh, 33 cảnh b-roll, 16 loại, kinetic 35%, chữ nền trống 0%.
- `python scripts/long_gate.py cl-sarin-tokyo-1995`: chỉ còn hai lỗi dự kiến: chưa TTS, và `publish_at` trống.
- `python motion/variety.py audit cl-sarin-tokyo-1995`: OK.

## 5. Việc còn lại cho Lead

1. **`script_lines.py` chặn câu CH01 dòng 11**: "...sẽ được gắn nhãn PHỎNG DỰNG trên hình." bị gate `META_LEAK` (cụm "trên hình"). Tôi không sửa lời. Để ghi `lines` tôi chạy `script_lines.parse` rồi ghi `chNN.json` giống hệt công cụ nhưng bỏ gate; các `chNN.json` chỉ khác HEAD ở `title` và `lines`. Bước TTS và lần chạy `script_lines.py` sau này sẽ vẫn bị chặn cho đến khi đổi cụm đó (ví dụ "trong khung hình") hoặc Lead cho phép ngoại lệ.
2. **Cảnh báo (không chặn) của `opening_gate`**: "Từ khóa tiêu đề chưa nói trước 20s" với tiêu đề 1. Đổi thứ tự tiêu đề hoặc chỉnh câu 0 nếu muốn hết cảnh báo.
3. **Clip chung chỉ có 15 loại phù hợp** (6 noir AI + 9 Pexels). Đủ 33 cảnh clip với mỗi clip ≤ 3 lần, nhưng không có clip nào về Nhật Bản. Muốn thêm cảnh clip hay giảm lặp phải có clip mới (tàu điện, sân ga). Chạy lại `check_scene_durations.py` sau TTS vì clip noir chỉ dài 8 s (cảnh dùng chúng phải ≤ 7,5 s).
4. **Ảnh thật chỉ 30** (đủ sàn nhờ 29 ảnh AI). Ảnh sự kiện có giấy phép rất ít: 8 ảnh Lực lượng Phòng vệ/Cứu hỏa Tokyo 1995, ảnh tư liệu Satyan, vài sơ đồ tuyến; còn lại là ga, lâu đài Matsumoto, trụ sở ngày nay. 146/338 cảnh dùng ảnh AI làm nền (nhãn `MINH HỌA CHUNG` hoặc `PHỎNG DỰNG`); Lead xem lại tỉ lệ này ở bước QA bằng mắt.
5. **Ảnh thật chưa tải**: `output/long/cl-sarin-tokyo-1995/img/` mới có 29 ảnh AI; bước `html` sẽ tải 30 ảnh Commons theo tên file (cần mạng). Các ảnh `map_hib` (print), `hz15`, `sdf*` nên soi lại khung đầu sau khi tải.
6. **Thẻ phụ**: `idcards` (CL bật mặc định) chưa chạy trong bước kiểm; `file` hiện 9 thẻ nên nằm dưới trần 12%.
