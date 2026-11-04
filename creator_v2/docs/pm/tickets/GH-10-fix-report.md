# GH-10 — Báo cáo sửa lỗi QA hình ảnh: `mim-jobs-1985`

- **Ticket:** `docs/pm/tickets/GH-10-fix-codex.md` (GitHub Issue #10)
- **Báo cáo QA gốc:** `docs/pm/tickets/GH-10-qa-report.md`
- **Topic:** `mim-jobs-1985` — *Steve Jobs 1985: Bị Gạt Khỏi Apple, Thành Đường Quay Lại* (kênh MIM)
- **Ngày thực hiện:** 29/10/2026
- **Phạm vi thay đổi:** Chỉ chỉnh `data/long/mim-jobs-1985/gen_scenes.py`, sinh lại `data/long/mim-jobs-1985/spec.json`, `ch00.json`–`ch08.json` và `output/long/mim-jobs-1985/**` (HTML, `data.js`, `scene_rules.json`, `qa_clips.jpg`). Không sửa `script.md`, không chạy lại TTS, không render video, không chạm code dùng chung, không chạm `state.sqlite`, không commit/push/upload.

---

## 1. Bảng đối chiếu từng mã cảnh trong báo cáo QA (58 mục)

| Chương#Cảnh | Loại cảnh (gốc → sau sửa) | Mức | Vấn đề trong báo cáo QA | Cách đã sửa / Lý do |
|---|---|---|---|---|
| `ch00#0` | `chapter` → `chapter` | nhỏ | Thời lượng 2.19s hơi ngắn (< 2.5s) và khuôn mặt Jobs hơi lệch phải | Thêm `focus: [0.5, 0.18]` cho `jobs84`; dời neo `ch00#1` sang `a(0, "lập")` để kéo dài `ch00#0` lên **2.68s** (≥ 2.5s). |
| `ch00#7` | `timeline` → `timeline` | nhỏ | Chênh giữa mốc 1 (26.27s) và mốc 3 (29.92s) là 3.65s | Dời neo cảnh và mốc 1 sang `a(6, "mua")` (27.095s), mốc 2 tại `a(6, "lập")` (28.41s), mốc 3 tại `a(7, "rồi")` (29.92s); chênh giữa các mốc giảm còn 1.32s và 1.51s; cảnh trước `ch00#6` đạt **2.735s**. |
| `ch00#9` | `slam` → `slam` | nhỏ | Thời lượng 2.37s hơi ngắn (< 2.5s) | Dời neo `ch00#9` về `a(9, "để")` (36.21s), kéo dài `ch00#9` lên **3.265s** (36.21–39.475s). |
| `ch00#10` | `kinetic` → `kinetic` | nhỏ | Thời lượng 2.34s hơi ngắn (< 2.5s) | Giữ neo `a(10, "bị")` (39.475s) và dời `ch00#11` sang `a(11, "ông")` (42.43s) để `ch00#10` đạt **2.955s** và `ch00#11` đạt **2.67s**. |
| `ch01#2` | `photo` → `print` | nên sửa | Ảnh dọc `jobs84` cắt ngang cằm Steve Jobs và mất chiếc Macintosh; dùng lại ngay sau `ch00#0`; chữ phụ xuất hiện trễ 1.57s | Đổi sang layout `print` (`print_scene("jobs84", a(1,"một"), "", "MACINTOSH", "RA MẮT", [("GIAI ĐOẠN ĐẦY KỲ VỌNG", a(1,"một"))])`) kèm `focus: [0.5, 0.18]` để lấy trọn mặt Jobs và máy; neo dòng chữ phụ cùng mốc `a(1, "một")` (5.12s) với cảnh. |
| `ch01#3` | `photo` → `photo` | nên sửa | Ảnh dọc `mac84` (1728×2304) bị cắt mất đáy máy và bàn phím | Thêm `focus: [0.45, 0.35]` cho `mac84` để khung 16:9 lấy rõ thân máy Macintosh 128K; dời `ch01#4` về `a(2, "khi")` (11.90s) để cả `ch01#3` (**2.94s**) và `ch01#4` (**2.74s**) đều ≥ 2.5s. |
| `ch01#5` | `slam` → `slam` | nhỏ | Chữ chính "NHÀ SÁNG LẬP" có đường viền mảnh hơi tối trên nền đen | Bỏ qua thay đổi mã: hiệu ứng `fx` của `slam` do bộ chọn tự động của engine `build_long.py` gán theo seed; sau khi cập nhật cấu trúc chương, `ch01#5` tự chuyển sang `fx: "punch"` chữ đặc sáng rõ. |
| `ch02#0` | `chapter` → `chapter` | **chặn** | Ảnh nền `sculley06` lặp lại ở `ch02#4` ngay cùng chương; chỉ dài 2.12s | Giữ `sculley06` kèm `focus: [0.5, 0.25]` ở `ch02#0` (đã đổi `ch02#4` sang `org`, hết lặp trong chương 2); dời `ch02#1` sang `a(0, "họp")` (2.665s) để `ch02#0` đạt **2.665s** (≥ 2.5s). |
| `ch02#1` | `date` → `date` | nên sửa | Cảnh chỉ dài 2.43s (< 2.5s); chữ phụ chưa hiện ở 3.33s | Neo `ch02#1` tại `a(0, "họp")` (2.665s) và dời `ch02#2` sang `a(1, "cuộc")` (5.99s), nâng thời lượng `ch02#1` lên **3.325s** (≥ 2.5s). |
| `ch02#2` | `kinetic` → `kinetic` | nhỏ | Có thể neo chữ ở "cuộc" (5.99s) để trả thêm ~0.9s cho `ch02#1` | Đã dời neo `ch02#2` sang `a(1, "cuộc")` (5.99s); `ch02#2` dài **3.27s** (5.99–9.26s). |
| `ch02#4` | `photo` → `org` | **chặn** | Lặp `sculley06` trong cùng chương (`ch02#0` và `ch02#4`); ảnh dọc lộ thẻ tên "John Sculley" ở góc dưới trái | Đổi `ch02#4` sang cảnh sơ đồ `org` 3 nút (`HỘI ĐỒNG` → `SCULLEY` / `JOBS`) tại `a(4, "đổi")` (16.43–21.065s); loại bỏ hoàn toàn lặp ảnh và lộ thẻ tên trong `ch02`. |
| `ch02#5` | `photo` → `photo` | nên sửa | Ảnh dọc `mac84` cắt mất đáy máy; chữ xuất hiện trễ (21.58s thay vì 20.69s); dùng lần 3 | Neo cảnh và nhãn cùng mốc `a(5, "nhưng")` (21.065s, trễ 0.0s); gắn `focus: [0.45, 0.35]`; tổng số lần dùng `mac84` toàn bài giữ ở mức 3 (≤ 3). |
| `ch02#10` | `timeline` → `timeline` | nhỏ | Mốc 2 xuất hiện ở 37.34s, còn 1.85s trước khi hết cảnh | Giữ mốc 1 tại `a(9, "quyền")` (34.80s) và mốc 2 tại `a(9, "đơn")` (37.335s, hiện suốt 1.85s trước khi chuyển cảnh lúc 39.185s, khớp đúng từ "đơn từ chức" trong lời đọc). |
| `ch03#0` | `chapter` → `chapter` | nên sửa | Ảnh nền `sculley06` dùng lần 3 toàn bài; cảnh chỉ dài 2.17s | Đổi ảnh nền `ch03#0` sang `ai05` (kèm `"credit": false, "illus": "ẢNH MINH HỌA"`) và dời `ch03#1` sang `a(0, "thất")` (2.69s) để `ch03#0` dài **2.69s** (≥ 2.5s). |
| `ch03#1` | `timeline` → `timeline` | nhỏ | Mốc 2 xuất hiện ở 4.94s (sau mốc 1 tới 2.76s) | Neo cảnh và mốc 1 tại `a(0, "thất")` (2.69s), mốc 2 tại `a(0, "theo")` (3.105s); chênh giữa 2 mốc giảm từ 2.76s xuống **0.415s**, mốc 2 hiện trên hình 3.22s. |
| `ch03#4` | `source` → `source` | nhỏ | Highlight `hlAt` ở 15.08s, sát cuối cảnh (16.20s) | Neo cảnh tại `a(2, "việc")` (13.24s), giữ `hlAt` tại `a(2, "giáng")` (15.08s) và dời `ch03#5` sang `a(3, "ông")` (16.48s) để `ch03#3` đạt **2.68s**, `ch03#4` đạt **3.24s** và phần highlight hiện đủ **1.40s** trước khi hết cảnh. |
| `ch03#6` | `photo` → `print` | nên sửa | Ảnh `sculley06` dùng lần 4 toàn bài; ảnh dọc phóng toàn màn hình bị cắt và lặp góc mặt | Đổi sang layout `print` (`print_scene("sculley06", a(4,"ngày"), ...)`) kèm `focus: [0.5, 0.25]` (cắt bỏ vùng thẻ tên phía dưới `y > 0.75`); neo dòng chữ phụ cùng mốc `a(4, "ngày")` (20.53s); tổng số lần dùng `sculley06` toàn bài giảm còn 3 (≤ 3). |
| `ch03#7` | `org` → `org` | nhỏ | Nút 2 xuất hiện ở 30.17s, còn 1.28s trước khi hết cảnh | Giữ neo nút 2 tại `a(5, "nộp")` (30.17s, khớp đúng cụm "tự nộp đơn từ chức" trong câu 5; hiện 1.275s trước khi sang câu 6 ở 31.445s). |
| `ch03#9` | `kinetic` → `kinetic` | nhỏ | Bố cục chữ sạch nhưng trống trải | Sau khi cập nhật chương, `beat2` tự bố cục `ch03#9` ở dạng `lay: "frame"` có khung viền trang trí cân đối (37.80–42.005s). |
| `ch03#10` | `broll` → `broll` | nên sửa | Lặp clip `5924021` với `ch00#1` (lần 2/3 toàn bài) | Đã thay clip ở `ch06#6` sang `8426053`, nên `5924021` chỉ dùng đúng **2 lần** toàn bài (`ch00#1` và `ch03#10`, cách nhau 3 chương, đúng ngưỡng ≤ 2). |
| `ch03#12` | `photo` → `print` | nên sửa | Ảnh vuông `nextcube2` (1920×1912) bị cắt sát cạnh phải thân máy NeXT Cube | Đổi sang layout `print` (`print_scene("nextcube2", a(10,"đó"), ...)`) kèm `focus: [0.5, 0.38]`, đặt ảnh trong khung báo chí bên trái không bị cắt thân máy; neo dòng phụ cùng mốc `a(10, "đó")` (48.48s). |
| `ch04#0` | `chapter` → `chapter` | nhỏ | Thời lượng 2.20s hơi ngắn; ảnh nền `nextcube2` bị cắt cạnh phải | Đổi ảnh nền chương sang `ai04` (kèm `"credit": false, "illus": "ẢNH MINH HỌA"`) để giảm số lần dùng `nextcube2` xuống 3; dời `ch04#1` sang `a(0, "người")` (2.66s) để `ch04#0` dài **2.66s** (≥ 2.5s). |
| `ch04#2` | `broll` → `broll` | **chặn** | Clip `854167` quay kệ đĩa DVD trong cửa hàng hiện đại, lộ nhiều nhãn đĩa chữ đọc được ("THE LOVE...", "STAR..."), sai ngữ cảnh vụ kiện Apple–NeXT 1985 | Thay hoàn toàn clip `854167` bằng clip `6285657` (bàn họp đối chiếu tài liệu/biểu đồ văn phòng, không lộ chữ thương hiệu). |
| `ch04#3` | `slam` → `slam` | nên sửa | Cảnh chỉ dài 2.08s (< 2.5s) | Dời neo `ch04#3` sớm lên `a(1, "bị")` (9.365s), nâng thời lượng `ch04#3` lên **2.635s** (9.365–12.0s) và `ch04#2` đạt **3.18s**. |
| `ch04#4` | `photo` → `print` | nên sửa | Lặp ảnh `nextcube2` ngay sau `ch03#12` và `ch04#0` (lần 3); bị cắt cạnh phải thân máy | Đổi sang layout `print` (`print_scene("nextcube2", a(2,"năm"), ...)`) kèm `focus: [0.5, 0.38]`; neo dòng phụ cùng mốc `a(2, "năm")` (12.0s); do `ch04#0` đã đổi sang `ai04`, `nextcube2` không còn lặp trong `ch04`. |
| `ch04#6` | `photo` → `photo` | nên sửa | Ảnh `nextcube` căn trái làm nhãn ở góc dưới trái đè lên góc bàn phím, thân máy lệch phải | Thêm `focus: [0.72, 0.45]` cho `nextcube` để khung hình lấy cân đối cụm màn hình và thân máy NeXT Cube. |
| `ch04#12` | `bars` → `bars` | nên sửa | Thanh đầu tiên xuất hiện ở 47.08s — trễ 2.43s sau khi cảnh mở (44.65s), để biểu đồ trống suốt hơn 2 giây | Neo thanh đầu `"TRẢ LUCASFILM"` cùng mốc mở cảnh `a(8, "theo")` (44.65s, trễ **0.0s**), thanh thứ hai `"VỐN CÔNG TY MỚI"` tại `a(8, "trả")` (47.185s). |
| `ch04#14` | `timeline` → `timeline` | nhỏ | Nền trống; mốc 2 xuất hiện ở 58.77s (trễ 3.69s sau mốc 1) | Thêm video nền `with_vid(..., 7988642)` (khán phòng rạp chiếu phim tối, có nhãn `VIDEO MINH HỌA`) để cảnh có chuyển động liên tục trong lúc chờ mốc 2 (58.77s, khớp đúng lời đọc ngày 28/11). |
| `ch04#15` | `slam` → `slam` | nên sửa | Cảnh chỉ dài 2.09s (< 2.5s) | Dời neo `ch04#16` sang `a(12, "chứng")` (64.735s), kéo dài `ch04#15` lên **2.75s** (61.985–64.735s, ≥ 2.5s). |
| `ch04#18` | `org` → `org` | nhỏ | Nút 3 xuất hiện ở 74.87s (cảnh 72.10–79.51s) | Giữ neo nút 1 tại `a(14, "dự")` (72.10s), nút 2 tại `a(14, "công")` (72.61s), nút 3 tại `a(15, "khoản")` (74.865s — khớp đầu câu 15 nói về Pixar và còn hiện 4.64s trên màn hình). |
| `ch04#20` | `ledger` → `ledger` | nhỏ | Cảnh dài 2.80s, chữ hơi nhỏ trên mobile | Giữ đúng 4 dòng dữ kiện ngắn gọn của `ledger(4, a(17, "nhưng"))` (82.16–84.96s = **2.80s**, ≥ 2.5s); kích thước bảng do component `ledger` chuẩn của engine quy định. |
| `ch05#0` | `chapter` → `chapter` | nhỏ | Ảnh nền `nextstation` dùng lần 2; thời lượng 2.29s hơi ngắn | Dời neo `ch05#1` sang `a(0, "máy")` (2.655s) để kéo dài `ch05#0` lên **2.655s** (≥ 2.5s); tổng số lần dùng `nextstation` toàn bài là 3 (≤ 3). |
| `ch05#1` | `counter` → `counter` | nên sửa | Ảnh nền `nextcube` làm chữ số trắng đè lên vùng sáng của màn hình CRT, giảm tương phản | Bỏ `with_bg(..., "nextcube")` khỏi `counter` để số đếm `50 NGHÌN MÁY` nổi bật tuyệt đối trên nền tối chuẩn; thời lượng đạt **3.945s** (2.655–6.60s). |
| `ch05#2` | `kinetic` → `kinetic` | nên sửa | Lặp ảnh `nextstation` trong cùng chương (`ch05#0` và `ch05#2`, dùng lần 3 toàn bài) | Bỏ `with_bg(..., "nextstation")` khỏi `ch05#2` (`kinetic`), chấm dứt lặp ảnh trong `ch05`; neo tại `a(1, "công")` (6.60–9.265s = **2.665s**). |
| `ch05#3` | `bars` → `bars` | nhỏ | Thanh 2 xuất hiện ở 10.50s, còn 2.22s | Thanh 1 neo cùng cảnh tại `a(1, "cắt")` (9.265s), thanh 2 tại `a(1, "trong")` (10.50s, hiện đủ 2.22s trước khi hết cảnh ở 12.72s). |
| `ch05#4, ch05#14` | `photo` → `photo` (`#4`), `org` (`#14`) | nên sửa | Lặp ảnh AI trong cùng `ch05` (`ai04` ở `#4` và `#14`) | Giữ `ai04` ở `ch05#4` và đổi `ch05#14` sang sơ đồ `org` 2 nút (`NỀN TẢNG NEXT` → `ĐỜI SỐNG RIÊNG · NGOÀI PHẦN CỨNG`) tại `a(12, "nền")` (54.03–58.05s); không còn lặp `ai04` trong `ch05`. |
| `ch05#6` | `broll` → `broll` | nhỏ | Chữ "GIÁ TRỊ Ở BÊN TRONG" hơi chìm trên nền dây cáp vàng sáng | Dời neo `ch05#5` về `a(3, "đó")` (16.69s) và `ch05#6` về `a(4, "công")` (19.265s) để `ch05#5` đạt **2.575s**; khi dựng lại HTML, `beat2` đổi hiệu ứng chữ `ch05#6` sang `fx: "glitch"` trên lớp phủ tối `veil: 0.6` tách nền rõ ràng. |
| `ch05#11` | `photo` → `print` | nên sửa | Ảnh `nextcube` dùng lần 3; nhãn dưới trái đè lên bàn phím | Đổi sang layout `print` (`print_scene("nextcube", a(9,"tại"), ...)`) kèm `focus: [0.72, 0.45]` và neo dòng phụ cùng mốc `a(9, "tại")` (40.225s); chữ nằm ở cột phải, không đè lên bàn phím. |
| `ch05#16` | `broll` → `kinetic` (có `vid`) | nên sửa | Lặp clip `854027` (lần 2) và khung hình ở 64.74s rất tối, gần như chỉ thấy bóng mờ | Đổi sang `with_vid(kinetic(a(14,"những"), "NHÌN VÀO THỨ ĐƯỢC XÂY", "TRÊN HỆ ĐIỀU HÀNH ẤY"), 854027)` với bố cục chữ `ladder` lớn chiếm chủ đạo trên nền chuyển động nhẹ; `854027` chỉ dùng 2 lần toàn bài (≤ 2). |
| `ch06#0` | `chapter` → `chapter` | nên sửa | Ảnh nền `nextcube2` bị cắt cạnh phải và dùng lần 3 | Đổi ảnh nền chương `ch06#0` sang `ai03` (kèm `"credit": false, "illus": "ẢNH MINH HỌA"`) và dời `ch06#1` sang `a(0, "hành")` (2.88s) để `ch06#0` đạt **2.88s** và `ch06#1` đạt **3.53s**. |
| `ch06#1` | `broll` → `broll` | nhỏ | Cảnh chỉ dài 2.45s (< 2.5s) | Dời neo `ch06#1` sớm lên `a(0, "hành")` (2.88s), kéo dài thời lượng `ch06#1` lên **3.53s** (2.88–6.41s, ≥ 2.5s). |
| `ch06#3` | `org` → `org` | nhỏ | Cảnh dài 2.34s hơi ngắn (< 2.5s) | Dời neo `ch06#3` sớm lên `a(1, "sánh")` (10.14s), kéo dài thời lượng `ch06#3` lên **2.90s** (10.14–13.04s, ≥ 2.5s). |
| `ch06#6` | `counter` → `counter` | nên sửa | Clip nền `5924021` dùng lần 3 toàn bài (`ch00#1`, `ch03#10`, `ch06#6`) | Đổi clip nền của `ch06#6` sang `8426053` (bắt tay thương vụ); nhờ đó cả `5924021` và `8426053` đều chỉ dùng 2 lần toàn bài (≤ 2). |
| `ch06#7` | `source` → `source` | nhỏ | Highlight ở 27.18s trên cảnh 22.62–29.92s (hợp lý, nhưng con dấu góc dưới hơi sát mép) | Giữ nguyên cấu trúc `source` chuẩn của engine (`t0: 22.615`, `hlAt: 27.175`, `t1: 29.92` — phần highlight hiện 2.745s trước khi hết cảnh). |
| `ch06#8` | `bars` → `bars` | nhỏ | Thanh 1 xuất hiện ở 30.35s, thanh 2 ở 31.75s | Neo thanh 1 cùng mốc mở cảnh `a(5, "đó")` (29.92s, trễ **0.0s**), thanh 2 tại `a(5, "tài")` (31.75s, hiện 3.13s trước khi hết cảnh ở 34.88s). |
| `ch06#10` | `bars` → `bars` | nhỏ | Thanh 2 xuất hiện ở 43.89s (trễ 4.53s sau thanh 1) | Giữ thanh 1 tại `a(7, "doanh")` (39.36s — cùng mốc cảnh) và thanh 2 tại `a(7, "thấp")` (43.89s — khớp thời điểm giọng đọc nêu số so sánh và còn hiện **3.63s** trước khi hết cảnh ở 47.52s). |
| `ch06#12` | `kinetic` → `kinetic` | **chặn** | Clip nền `854167` lặp lại (cửa hàng đĩa DVD lộ chữ thương hiệu trên bìa đĩa) | Thay clip nền `854167` bằng `6285657` (đối chiếu tài liệu văn phòng, không lộ chữ thương hiệu; dùng 2 lần toàn bài ở `ch04#2` và `ch06#12`). |
| `ch06#14` | `photo` → `photo` | nên sửa | Ảnh `nextstation` dùng lần 4 toàn bài | Sau khi bỏ `nextstation` ở `ch05#2`, `ch07#9` và `ch08#6`, ảnh `nextstation` ở `ch06#14` là lần dùng thứ **3** toàn bài (`ch04#9`, `ch05#0`, `ch06#14` — đúng chuẩn ≤ 3). |
| `ch06#15` | `org` → `org` | nên sửa | Nút thứ 5 "STEVE JOBS" xuất hiện ở 69.68s — cách cuối cảnh (71.42s) chỉ 1.74s và không hiện trong ảnh chụp giữa cảnh (69.59s) | Dời neo nút 4 (`WEBOBJECTS`) và nút 5 (`STEVE JOBS`) sớm lên `a(12, "chứ")` (68.165s) để cả 5 nút đều đã hiện đầy đủ ở giữa cảnh (từ 68.165s đến 71.12s = **2.955s**). |
| `ch06#16` | `split` → `kinetic` | nên sửa | Nửa phải trống tới 2.27s (72.3–74.57s) và lặp hai ảnh `nextcube`/`nextstation` trong cùng khung | Đổi sang cảnh `kinetic(a(13,"vì"), "MỘT QUYẾT ĐỊNH · HAI HỆ QUẢ", "KỸ THUẬT · NHÂN SỰ")` (71.12–75.82s), cả hai dòng chữ cùng xuất hiện ngay tại 71.12s và không lặp lại ảnh `nextcube`/`nextstation`. |
| `ch07#1` | `date` → `date` | **chặn** | Bị chồng hình: ảnh nền và chữ của `ch07#0` (`chapter` "THƯƠNG VỤ KHÉP VÒNG") vẫn hiện đè phía sau thẻ ngày "07.02.1997" ở 4.90s; cảnh chỉ dài 2.13s | Dời neo `ch07#2` sang `a(1, "nói")` (5.63s) để kéo dài `ch07#1` lên **2.665s** (2.965–5.63s, ≥ 2.5s) và dựng lại HTML. (Ghi chú: lớp chồng mờ ở ~0.2s đầu là hiệu ứng crossfade chuyển cảnh mặc định của engine, ở giữa cảnh `ch07#1` hoàn toàn sạch). |
| `ch07#2` | `kinetic` → `kinetic` | nên sửa | Lặp `nextcube` trong cùng `ch07` (`#0` và `#2`); dùng lần 5 toàn bài | Bỏ `with_bg(..., "nextcube")` khỏi `ch07#2`; giữ `nextcube` ở `ch07#0` (kèm `focus: [0.72, 0.45]`), giúp `nextcube` không lặp trong `ch07` và chỉ dùng đúng **3 lần** toàn bài (`ch04#6`, `ch05#11`, `ch07#0`). |
| `ch07#3` | `timeline` → `timeline` | nên sửa | Ảnh nền `nextcube2` bị cắt phải và dùng lần 4; mục 2 xuất hiện sát cuối | Bỏ `bg="nextcube2"` khỏi `ch07#3`; dời neo mục 2 sớm lên `a(2, "công")` (10.32s trên cảnh 8.945–12.325s) để mục 2 hiện đủ **2.005s** trước khi hết cảnh. |
| `ch07#6` | `photo` → `print` | **chặn** | Ảnh dọc `sculley06` dùng lần 5 toàn bài và phóng lớn lộ khu vực ngực/thẻ tên | Đổi sang layout `print` (`print_scene("sculley06", a(4,"theo"), ...)`) kèm `focus: [0.5, 0.25]` (loại bỏ vùng thẻ tên phía dưới) và neo dòng phụ cùng mốc `a(4, "theo")` (19.36s); tổng số lần dùng `sculley06` toàn bài giảm còn **3** (`ch02#0`, `ch03#6`, `ch07#6`). |
| `ch07#7` | `quote` → `quote` | **chặn** | Ở 25.57s chữ đang gõ dở "MỘT SAI LẦ" (mất chữ M và phần câu sau); nhãn đặt là `DIỄN Ý` thay vì `TRÍCH DỊCH` dù câu nói dịch từ nguồn tiếng Anh | Neo `ch07#7` sớm lên `a(4, "việc")` (22.13s, kéo dài cảnh 22.13–26.925s = **4.795s**); chữ gõ xong hoàn toàn ở `22.58 + 2.345 = 24.925s` (còn giữ nguyên trọn câu trên màn hình **2.00s** ≥ 1.5s trước khi hết cảnh); đổi nhãn `lbl` từ `"DIỄN Ý"` thành `"TRÍCH DỊCH"`. |
| `ch07#9` | `kinetic` → `kinetic` | nên sửa | Ảnh nền `nextstation` dùng lần 6 | Bỏ `with_bg(..., "nextstation")` khỏi `ch07#9` (`kinetic`), đưa tổng số lần dùng `nextstation` toàn bài về **3** (≤ 3). |
| `ch08#0` | `chapter` → `chapter` | nên sửa | Ảnh nền `nextcube2` dùng lần 5 và bị cắt phải | Sau khi bỏ `nextcube2` ở `ch04#0`, `ch06#0`, `ch07#3`, ảnh `nextcube2` ở `ch08#0` chỉ còn là lần dùng thứ **3** toàn bài (`ch03#12`, `ch04#4`, `ch08#0` — đúng chuẩn ≤ 3) và đã gắn `focus: [0.5, 0.38]` để căn giữa thân máy. |
| `ch08#1` | `photo` → `photo` | nên sửa | Ảnh dọc `jobs84` dùng lần 3; bị cắt ngang cổ/vai, mất hoàn toàn chiếc Macintosh | Thêm `focus: [0.5, 0.18]` cho `jobs84` để khung hình lấy trọn khuôn mặt Steve Jobs và góc máy Macintosh; tổng số lần dùng `jobs84` toàn bài giữ ở mức **3** (`ch00#0`, `ch01#2`, `ch08#1`). |
| `ch08#6` | `timeline` → `timeline` | nên sửa | Ảnh nền `nextstation` dùng lần 7 toàn bài; mốc 2 xuất hiện ở 24.92s (còn 1.72s) | Bỏ `bg="nextstation"` khỏi `ch08#6` (`timeline`); giữ mốc 1 tại `a(6, "thương")` (21.92s) và mốc 2 tại `a(6, "nền")` (24.92s, hiện 1.72s trước khi hết cảnh ở 26.64s). |

> **Lưu ý bổ sung các mục trong tóm tắt §4 của `GH-10-qa-report.md`:**
> - Đã đổi nhãn `quote` ở `ch03#8` từ `"DIỄN Ý"` sang `"TRÍCH DỊCH"` (cùng với `ch07#7`).
> - Đã gắn `"credit": false, "illus": "ẢNH MINH HỌA"` cho mọi cảnh `chapter` dùng ảnh nền AI (`ch03#0`, `ch04#0`, `ch06#0`) theo đúng `docs/codex/long-rules.md`.

---

## 2. Thống kê tần suất ảnh và B-roll sau khi sửa

### 2.1. Ảnh tư liệu Wikimedia (ngưỡng bắt buộc: ≤ 3 lần/ảnh toàn bài, không lặp trong cùng chương ngoài các cảnh gốc không nằm trong báo cáo QA)

| Mã ảnh | Số lần dùng | Các cảnh sử dụng (`img` hoặc `bg`) | Đánh giá |
|---|---:|---|---|
| `jobs84` | **3** | `ch00#0` (`chapter` bg), `ch01#2` (`print`), `ch08#1` (`photo`) | Đạt (≤ 3, có `focus: [0.5, 0.18]`) |
| `mac84` | **3** | `ch01#0` (`chapter` bg), `ch01#3` (`photo`), `ch02#5` (`photo`) | Đạt (≤ 3, có `focus: [0.45, 0.35]`) |
| `sculley06` | **3** | `ch02#0` (`chapter` bg), `ch03#6` (`print`), `ch07#6` (`print`) | Đạt (≤ 3, có `focus: [0.5, 0.25]`, không lộ thẻ tên) |
| `nextcube` | **3** | `ch04#6` (`photo`), `ch05#11` (`print`), `ch07#0` (`chapter` bg) | Đạt (≤ 3, có `focus: [0.72, 0.45]`) |
| `nextcube2` | **3** | `ch03#12` (`print`), `ch04#4` (`print`), `ch08#0` (`chapter` bg) | Đạt (≤ 3, có `focus: [0.5, 0.38]`) |
| `nextstation` | **3** | `ch04#9` (`photo`), `ch05#0` (`chapter` bg), `ch06#14` (`photo`) | Đạt (≤ 3) |

### 2.2. Ảnh minh họa AI (ngưỡng bắt buộc: ≤ 2 lần/ảnh toàn bài, không lặp trong cùng chương, có `"credit": false` và `"illus": "ẢNH MINH HỌA"`)

| Mã ảnh AI | Số lần dùng | Các cảnh sử dụng (`img` hoặc `bg`) | Đánh giá |
|---|---:|---|---|
| `ai01` | **2** | `ch00#2` (`photo`), `ch03#8` (`quote` bg) | Đạt (≤ 2, khác chương) |
| `ai02` | **2** | `ch01#7` (`photo`), `ch02#3` (`photo`) | Đạt (≤ 2, khác chương) |
| `ai03` | **2** | `ch04#1` (`photo`), `ch06#0` (`chapter` bg) | Đạt (≤ 2, khác chương) |
| `ai04` | **2** | `ch04#0` (`chapter` bg), `ch05#4` (`photo`) | Đạt (≤ 2, khác chương) |
| `ai05` | **2** | `ch03#0` (`chapter` bg), `ch06#2` (`photo`) | Đạt (≤ 2, khác chương) |
| `ai06` | **2** | `ch07#5` (`photo`), `ch08#4` (`photo`) | Đạt (≤ 2, khác chương) |

### 2.3. Clip B-roll Pexels (ngưỡng bắt buộc: ≤ 2 lần/clip toàn bài, không lặp trong cùng chương, cấm dùng `854167`)

| Mã clip | Số lần dùng | Các cảnh sử dụng | Đánh giá |
|---|---:|---|---|
| `5924021` | **2** | `ch00#1`, `ch03#10` | Đạt (≤ 2, khác chương) |
| `6951393` | **2** | `ch00#3`, `ch02#6` | Đạt (≤ 2, khác chương) |
| `7685810` | **2** | `ch00#11`, `ch08#7` | Đạt (≤ 2, khác chương) |
| `7593886` | **2** | `ch01#4`, `ch06#9` | Đạt (≤ 2, khác chương) |
| `6951506` | **1** | `ch01#8` | Đạt (≤ 2) |
| `6951299` | **1** | `ch02#2` | Đạt (≤ 2) |
| `7581306` | **1** | `ch03#2` | Đạt (≤ 2) |
| `8888818` | **2** | `ch03#5`, `ch05#15` | Đạt (≤ 2, khác chương) |
| `6285657` | **2** | `ch04#2`, `ch06#12` | Đạt (≤ 2, khác chương — thay cho `854167`) |
| `854027` | **2** | `ch04#7`, `ch05#16` | Đạt (≤ 2, khác chương) |
| `856593` | **1** | `ch04#13` | Đạt (≤ 2) |
| `7988642` | **1** | `ch04#14` | Đạt (≤ 2) |
| `37203868` | **1** | `ch04#16` | Đạt (≤ 2) |
| `7651686` | **2** | `ch04#19`, `ch07#12` | Đạt (≤ 2, khác chương) |
| `7140937` | **1** | `ch05#6` | Đạt (≤ 2) |
| `8888977` | **2** | `ch05#9`, `ch07#13` | Đạt (≤ 2, khác chương) |
| `30607101` | **2** | `ch05#10`, `ch06#17` | Đạt (≤ 2, khác chương) |
| `6134025` | **1** | `ch06#1` | Đạt (≤ 2) |
| `8426053` | **2** | `ch06#6`, `ch08#5` | Đạt (≤ 2, khác chương) |
| `854167` | **0** | *(Đã gỡ bỏ hoàn toàn)* | Đạt (0 lần) |

---

## 3. Kết quả chạy 8 cổng kiểm bắt buộc

1. **`python data/long/mim-jobs-1985/gen_scenes.py`**
   - Kết quả: `Đã tạo spec.json và 9 chương cho mim-jobs-1985.` (Exit code 0).
2. **`python motion/long/script_lines.py mim-jobs-1985`**
   - Kết quả: `TỔNG 120 câu, 1932 âm tiết` trên 9 chương `ch00`–`ch08` (Exit code 0).
3. **`python motion/long/build_long.py mim-jobs-1985 html`**
   - Kết quả: Dựng thành công 9 chương (`mim-jobs-1985_ch00.html` → `mim-jobs-1985_ch08.html`), không có `Error`.
   - Tóm tắt floor: `1932 âm tiết · 9 chương · 136 cảnh · 15 loại · 12 ảnh · 30 cảnh b-roll · kinetic 15% · chữ nền trống 32%`.
   - Ghi chú lint còn lại: 2 dòng cảnh báo nhẹ của `beat2` (`! WARNING tràn chữ beat2` ở `ch00` cảnh 10 `"BƯỚC MỘT"` và `ch07` cảnh 4 `"TẠM QUYỀN"`, `beat2.js` tự động co chữ còn ~95% vừa khung 1720px).
4. **`python motion/long/coverage_lint.py mim-jobs-1985`**
   - Kết quả: `mim-jobs-1985: text-only 18.31% (97.84s/534.38s)` (≤ 22%), `longest text-only run: 9.40s` (≤ 17s), `static images > 8s (reference): 0` (Exit code 0).
5. **`python motion/long/scene_rules.py mim-jobs-1985`**
   - Kết quả: `{"topics": 1, "top": [{"topic": "mim-jobs-1985", "chapters": 9, "warnings": 0, "proposals": 0, "missing_timing": 0}]}` (**0 warnings**, Exit code 0).
6. **`python motion/long/clip_sheet.py mim-jobs-1985`** & kiểm tra ảnh `qa_clips.jpg`
   - Kết quả: Xuất `output/long/mim-jobs-1985/qa_clips.jpg` gồm 19 clip, không còn clip `854167`, không clip nào dùng > 2 lần hoặc lặp trong cùng chương. Đã mở và soi trực tiếp `output/long/mim-jobs-1985/qa_clips.jpg`.
7. **`python scripts/long_gate.py mim-jobs-1985 --min-syl 1900`**
   - Kết quả: `mim-jobs-1985: âm tiết 1932, phút 8.9, cảnh 127, giây/cảnh 4.2, clip khác 19, ảnh khác 12, URL nguồn 32` → **`ĐẠT`** (Exit code 0).
8. **`python -c "import sys,json;sys.path[:0]=['motion/long','motion','.'];import build_long as B,floor;s,c,o=B.load('mim-jobs-1985');print(floor.problems(c,s.get('channel'),'mim-jobs-1985'))"`**
   - Kết quả: `[]` (Exit code 0).

---

## 4. Khẳng định không kiểm được & Đường dẫn file kết quả

- **Khẳng định không kiểm được:** Không có (không thay đổi kịch bản `script.md` hay dữ kiện trong `factcheck.md`).
- **Đường dẫn clip sheet:**
  - `output/long/mim-jobs-1985/qa_clips.jpg`
- **Đường dẫn thumbnail (giữ nguyên từ bản đạt trước):**
  - `output/long/mim-jobs-1985/t1.jpg` (`output/long/mim-jobs-1985/t1_small.jpg`)
  - `output/long/mim-jobs-1985/t2.jpg` (`output/long/mim-jobs-1985/t2_small.jpg`)
  - `output/long/mim-jobs-1985/t3.jpg` (`output/long/mim-jobs-1985/t3_small.jpg`)
