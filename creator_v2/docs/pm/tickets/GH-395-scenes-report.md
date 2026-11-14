# GH-395: báo cáo bước 4 (cảnh) Long CL "Địch Nhân Kiệt Ngoài Đời Thật" (15/11/2026)

Người làm: Claude (Sonnet), trong worktree `wt-dnk/creator_v2`. Chưa TTS, chưa render, chưa commit, chưa chạm YouTube. Đã áp bổ sung của Lead 15/11 (tiêu đề "survival", cold open, thẻ chương).

File ghi: `data/long/cl-dich-nhan-kiet/{gen_scenes.py, gen_scenes2.py, spec_dnk.py, ch00..ch13.json (scenes/hud/bgm), spec.json}`, `output/long/cl-dich-nhan-kiet/broll/` (7 clip chung chép từ Lưu Gù, cùng sidecar `ai_generated`, `minh_hoa_chung`) và file này.

## 1. Số liệu

- **283 cảnh**, 14 chương, 16 loại cảnh (kinetic 96, slam 37, quote 36, org 26, chapter 13, file 13, photo 12, ledger 11, date 10, counter 8, question 8, map 4, timeline 3, myth 3, split 2, print 1). `floor.report`: 5.613 âm tiết, 75 ảnh, 35 cảnh b-roll, kinetic 34% (trần 38%), chữ trên nền trống 0%.
- Cảnh `file`: 13/283 = **4,6%** (trần 12%), khoảng cách nhỏ nhất giữa hai thẻ file 9 cảnh (yêu cầu ≥ 5).
- Ảnh khai trong spec: **75** (sàn 40); 12 ảnh khác nhau làm `img` (mỗi ảnh ≤ 3, `dnk_a` 2 lần); còn lại làm nền `bg`/split.
- Clip: 7 clip, mỗi clip đúng 5 cảnh (trần 5) = 35 cảnh b-roll (sàn 30).

| Chương | Cảnh | Chương | Cảnh |
|---|---:|---|---:|
| CH00 Một chữ "thật" | 11 | CH07 Lạc Dương dưới triều Võ Chu | 24 |
| CH01 Hai cuốn sổ đặt cạnh nhau | 16 | CH08 Chữ "thật" được nói ra | 15 |
| CH02 Cậu bé ngồi đọc sách | 18 | CH09 Mảnh lụa trong áo bông | 20 |
| CH03 Đại lý thừa, và con số 17.000 | 15 | CH10 Từ Bành Trạch về Ngụy Châu | 20 |
| CH04 Cây bách ở Chiêu Lăng | 17 | CH11 Cô cháu hay mẹ con | 27 |
| CH05 Thứ gần với ma quái nhất | 26 | CH12 Biên cương, Hà Bắc, một pho tượng | 22 |
| CH06 Dự Châu | 21 | CH13 Người trong hồ sơ, người trong phim | 31 |

## 2. Trục "hai cuốn sổ đặt cạnh nhau"

- Mỗi chặng đời có một thẻ `org` cùng khuôn: gốc "CHẶNG n · <tên>" + "HAI CUỐN SỔ", hai cột **NẾU LÀ PHIM / SỬ CHÉP** (9 chặng: thuở nhỏ, đại lý thừa, cây bách, Kỳ Châu, đền miếu, Dự Châu, Lạc Dương, ngôi thái tử, truy đuổi). CH01 (lộ trình) và CH13 (kết) dùng cùng khuôn "SỔ CỦA PHIM / SỔ CỦA SỬ". Thêm `myth` "TRONG PHIM: ÁN MA QUÁI / TRONG HAI BỘ ĐƯỜNG THƯ: KHÔNG CÓ VỤ NÀO" (CH05, CH13), `split` hai cách hiểu (CH03) và hai lần can (CH12).
- Thẻ `quote` cho **cả 36 câu [TRÍCH DỊCH]**, nguồn ghi trên thẻ (Cựu Đường thư Q.89; Tư trị thông giám Q.202, 204, 205, 206, 207; chọn theo bảng factcheck). Câu "Phản là thật!" tách riêng thành cảnh slam lớn sau thẻ quote (CH00).
- Nhãn BÁCH KHOA, DỊ BẢN, TÂN ĐƯỜNG THƯ đặt trên khung (`illus`); ảnh chụp ngày nay có nhãn "ẢNH NGÀY NAY", mô hình/diorama có nhãn "MÔ HÌNH · BẢO TÀNG"; tượng gốm quan đường dùng thay người không có ảnh ghi rõ "TƯỢNG GỐM QUAN ĐƯỜNG · MINH HỌA" hoặc chỉ làm nền. Lai Tuấn Thần, Trương Giản Chi, Trương Quang Phụ, Vương Đức Thọ... chỉ có thẻ chữ (file), không ảnh.
- Ba cách đếm Dự Châu (CH06): `org` ba cột khác loại, không cộng: BỊ BUỘC TỘI 600–700 gia đình (Thông giám), BỊ TỊCH THU 5.000 người (Thông giám), BỊ ÁN TỬ 2.000 người (Tân Đường thư).
- Dòng thời gian Võ Chu: `timeline` 690/691 (CH07) và 700/704/705 (CH13, năm mất 700 theo sử, 704 là giả thuyết, 705 chính biến). Bản đồ `map` Lạc Dương–Trường An–Dự Châu–Ngụy Châu (CH06, CH07) và Hà Bắc (CH10, CH12).
- Không có cảnh máu, không viết thư bằng máu (CH09 có `myth`: "thư viết bằng máu" gạch bỏ, "lụa từ đầu chăn, máu từ cú đập đầu").

## 3. Phần bổ sung của Lead (15/11)

1. Tiêu đề: `spec.title` và `youtube.titles[0]` = "Địch Nhân Kiệt Thật: Nhận Tội Mưu Phản Để Sống Sót" (50 ký tự); hai phương án sau giữ lại: "ĐỊCH NHÂN KIỆT Ngoài Đời Thật: Phản Là Thật", "Địch Nhân Kiệt: Hai Cuốn Sổ, Một Người". Thumbnail không làm.
2. Cold open CH00 (11 cảnh, 3–6 giây/cảnh): giây 0–5 là chân dung Địch Nhân Kiệt tông `noir` có phủ tối (không có clip nào chiếm đầu, vẫn là media); quote hai câu đầu; "PHẢN LÀ THẬT!" là slam đơn độc (nối vào ý "Sử cũng chép rằng, có lần", dài 2,5–2,8 giây ở cả ba tốc độ vì câu không có chỗ ngừng); "17.000 NGƯỜI, KHÔNG AI KÊU OAN" là counter ngay sau; "Vậy vì sao chính ông lại tự nhận mình là kẻ phản?" là cảnh `question` riêng. Không ảnh bạo lực.
3. Thẻ chương `chapter` ở CH01–CH13 (CH06, CH07 chèn thêm vào đầu, bản đồ dời xuống câu 1), `sub` lấy từ ý có trong kịch bản: ví dụ CH05 "KHÔNG CÓ MỘT VỤ ÁN MA QUÁI NÀO", CH08 "MỘT TRONG BA TỂ TƯỚNG BỊ TỐ", CH04 "HAI TƯỚNG LỠ TAY CHẶT CÂY BÁCH". Nghịch lý rõ nhất chỉ có ở CH05 và CH08; các chương khác dùng mốc mở chương, không thêm chữ ngoài lời đọc.

## 4. Cổng đã chạy

- `python data/long/cl-dich-nhan-kiet/gen_scenes.py`: sạch (mọi mốc `[dòng, từ]` có thật, mốc cảnh tăng dần, ảnh `img` ≤ 3, ghi công đủ).
- `python scripts/check_scene_durations.py cl-dich-nhan-kiet --out <timing giả>` ở **3,7 / 4,1 / 4,4 từ/giây: TỔNG LỖI 0 cả ba**. Gồm cổng nhịp cảnh, lint html (tiêu đề thẻ), craft, floor (idcards). Timing giả tính theo số từ + ngắt `p` + 0,32 giây giữa câu, wav im lặng, đặt ngoài repo (thư mục scratchpad của phiên). Chưa có TTS nên sau `tts` phải chạy lại không `--out`.
- `motion/variety.py audit`: **1 vấn đề giả**: sổ trong worktree cũ, chỉ biết `bao-thanh-thien` (cùng look `rose`) là video trước. Trên lịch thật, ba video trước là Hoàng Kim Vinh (classic), Lưu Gù (jade), Đông Lang (sulfur) nên `rose` khác cả ba (rose lần cuối ở Bao Thanh Thiên, cách 4 video). Lead chạy lại audit ở checkout sản xuất; nếu muốn tránh hẳn rose thì mọi look khác đều đã có video lân cận (steel Mata Hari 29/11, amber Hòa Thân).
- Mức nhạc: `mix_levels.CL` gain 0,27, threshold 0,08, ratio 3,0.

## 5. Spec

Playlist "Ngoài Đời Thật"; `publish_at` 2026-11-24T14:00:00Z; `approved` = "13/11/2026 — duyet, ban tu dieu phoi theo cach tot nhat nhe, toi di ngu"; thumb `t1.jpg` (chưa có); `youtube.sources` 13 URL công khai (Cựu Đường thư q.89, Tân Đường thư q.115, Tư trị thông giám q.202, 204–207 trên Wikisource; Wikipedia Di Renjie en/zh, Lai Junchen, Judge Dee, Zhang Jianzhi, Yao Chong); `video_credits` 76 dòng (75 ảnh có tác giả, giấy phép, URL Commons lấy từ API 15/11 + dòng clip minh họa chung); `chapter_titles` 14; `say` 7 mục (Wikipedia, CCTV, Robert, Van, Gulik, Judge, Dee: nghe thử sau TTS).

## 6. Ảnh: loại bỏ và giấy phép

Đã mở cả mười sheet (0 đến 9). Loại: ảnh hiện đại không nhãn (ga tàu, cầu, tàu điện, tòa nhà, ảnh người đời nay, bản đồ hành chính Hà Nam), ảnh rác (hoa mẫu đơn, cảnh sông núi không đề tài), bản đồ Hán, tranh Minh/Thanh/Tống không liên quan, lăng Chiêu Lăng của nhà Thanh (Thẩm Dương) và lăng nhà Minh (trùng tên "Zhaoling"), tranh phong cảnh, bình, gương và bát đĩa lặp, tượng Phật lặp ở Bạch Mã Tự. Không ảnh AI mô phỏng người thật. Ảnh nhân vật: 4 chân dung PD Địch Nhân Kiệt (`dnk_a`, `dnk_b`, `dnk_c` bản vẽ, `dnk_t` trang tán), 3 ảnh mộ (CC BY-SA, nhãn "ẢNH NGÀY NAY"), 1 chân dung Diêu Sùng; Võ Tắc Thiên có 2 tranh, 1 tranh hành lễ, bia vô tự không dùng.

Giấy phép của 75 ảnh dùng: **Public domain 31, CC0 22, CC BY-SA 4.0 13, CC BY-SA 3.0 5, CC BY-SA 2.5 3, CC BY-SA 2.0 1**; không NC/ND. Cần ghi công (CC BY-SA, 22 ảnh; đã nằm trong `spec.youtube.video_credits`, engine cũng in dòng "ẢNH: …" trên khung): ba ảnh mộ (Gisling, Windmemories x2), mô hình Lạc Dương, thẻ vàng Võ Tắc Thiên, bản đồ Tang China 669 và Tang Dynasty circa 700, bản đồ First Turkic Khaganate, History of Xi'an, Càn Lăng (4 ảnh), Chiêu Lăng, Luoyang 2006, mô hình minh đường, ba tượng gốm quan/chiến binh (Gary Todd, CMOC), tượng thần giữ cửa Cernuschi. Danh sách đầy đủ với tên file, tác giả, giấy phép và URL: `spec.json` mục `youtube.video_credits` (hoặc bảng `CREDITS` trong `spec_dnk.py`). Ảnh PD/CC0 chính: bốn chân dung Địch Nhân Kiệt, Diêu Sùng, hai tranh Võ Tắc Thiên, Thái Tông (Diêm Lập Bản), phù điêu Chiêu Lăng (CC0), tranh vách mộ Trường Lạc công chúa, tranh Lụa mới dệt (Trương Huyên), bản đồ Đột Quyết.

## 7. Lỗi còn lại và việc cần Lead quyết

1. **Chưa TTS**: thời lượng thật phải đo lại bằng `check_scene_durations.py` ngay sau `build_long.py tts` (không `--out`). Cảnh "PHẢN LÀ THẬT!" ngắn nhất (2,5–2,8 giây); nếu TTS đọc nhanh hơn 4,4 từ/giây thì nới điểm neo của cảnh đếm 17.000. Ngắt `‖` trước "Phản là thật" không có sẵn trong lời đọc: nếu Lead muốn nhịp ngừng thật thì thêm `‖` ở cuối câu trích (sửa script, ngoài phạm vi ticket này).
2. **Clip chung là 7 clip chép từ Lưu Gù/HKV** (lồng đèn, thư phòng, mực, sông sương, cuộn giấy, cửa tối...), không phải ngục Đường; mỗi cảnh có nhãn "MINH HỌA CHUNG". Nếu muốn sát hơn, nhờ bot tạo 7 clip mới (ngục tối, hành lang cung, đuốc, cuộn lụa...) rồi đổi `CLIPS`.
3. **Ngục/tra khảo**: kho ảnh tự do không có ảnh ngục hay tra khảo thời Đường; cảnh đầu phải dùng chân dung tông noir. Cần ảnh thật hơn thì chỉ còn đường clip AI chung.
4. **Look `rose`**: xem mục 4, cần audit lại ở sổ thật.
5. Thẻ `file` và thẻ chương chưa soi khung hình; cần mở contact sheet sau `html` (đặc biệt tiêu đề thẻ chương 3 dòng ở CH01, CH03, CH06, CH10, CH12, CH13 và kinetic dài trong font Spectral/Archivo của look rose).
6. Chương CH05 mở bằng sub "KHÔNG CÓ MỘT VỤ ÁN MA QUÁI NÀO" trước khi lời đọc nói câu đó (câu 19): là chủ ý "nghịch lý mở chương" theo yêu cầu 15/11.
7. Lời trích dịch do subagent kịch bản tự dịch từ chữ Hán (36 câu) vẫn chờ rà bản dịch, như báo cáo bước 3.
