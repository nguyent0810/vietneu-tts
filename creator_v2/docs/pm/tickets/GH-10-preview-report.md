# GH-10 — Báo cáo soát bản preview: `mim-jobs-1985`

- **Ticket:** `docs/pm/tickets/GH-10-preview-agy.md` (GitHub Issue #10)
- **Báo cáo đối chiếu:** `docs/pm/tickets/GH-10-qa-report.md` & `docs/pm/tickets/GH-10-fix-report.md`
- **Topic:** `mim-jobs-1985` — *Steve Jobs 1985: Bị Gạt Khỏi Apple, Thành Đường Quay Lại* (kênh MIM)
- **Ngày thực hiện:** 29/10/2026
- **Kết luận tổng thể:** **cần sửa tiếp**

---

## 1. Các lệnh đã chạy & File kết quả đã tạo

1. **Render bản preview (`--draft`) cho đủ 9 chương:**
   - Lệnh: `python motion/long/build_long.py mim-jobs-1985 render --draft` (Exit code 0)
   - Kết quả 9 video draft (`output/long/mim-jobs-1985/ch00/draft.mp4` .. `ch08/draft.mp4`, tổng thời lượng `534.50s` ≈ `8 phút 54.5 giây`):
     - `output/long/mim-jobs-1985/ch00/draft.mp4` (`45.10s`)
     - `output/long/mim-jobs-1985/ch01/draft.mp4` (`47.17s`)
     - `output/long/mim-jobs-1985/ch02/draft.mp4` (`46.50s`)
     - `output/long/mim-jobs-1985/ch03/draft.mp4` (`52.27s`)
     - `output/long/mim-jobs-1985/ch04/draft.mp4` (`88.83s`)
     - `output/long/mim-jobs-1985/ch05/draft.mp4` (`72.20s`)
     - `output/long/mim-jobs-1985/ch06/draft.mp4` (`86.37s`)
     - `output/long/mim-jobs-1985/ch07/draft.mp4` (`58.03s`)
     - `output/long/mim-jobs-1985/ch08/draft.mp4` (`38.03s`)
2. **Trích khung & ghép contact sheet theo yêu cầu:**
   - Sheet theo chương (mỗi 3 giây 1 khung, lưới 6 cột, nhãn mốc giây dưới mỗi khung):
     - `output/long/mim-jobs-1985/qa/preview_ch00.jpg` (16 khung, `00s`–`45s`)
     - `output/long/mim-jobs-1985/qa/preview_ch01.jpg` (16 khung, `00s`–`45s`)
     - `output/long/mim-jobs-1985/qa/preview_ch02.jpg` (16 khung, `00s`–`45s`)
     - `output/long/mim-jobs-1985/qa/preview_ch03.jpg` (18 khung, `00s`–`51s`)
     - `output/long/mim-jobs-1985/qa/preview_ch04.jpg` (30 khung, `00s`–`87s`)
     - `output/long/mim-jobs-1985/qa/preview_ch05.jpg` (25 khung, `00s`–`72s`)
     - `output/long/mim-jobs-1985/qa/preview_ch06.jpg` (29 khung, `00s`–`84s`)
     - `output/long/mim-jobs-1985/qa/preview_ch07.jpg` (20 khung, `00s`–`57s`)
     - `output/long/mim-jobs-1985/qa/preview_ch08.jpg` (13 khung, `00s`–`36s`)
   - Sheet toàn bài (mỗi 6 giây 1 khung trên toàn bộ 9 chương, lưới 6 cột):
     - `output/long/mim-jobs-1985/qa/preview_all.jpg` (93 khung)
   - Sheet bổ trợ kiểm từng cảnh (127 khung tại thời điểm chữ/hiệu ứng đã vào đủ):
     - `output/long/mim-jobs-1985/qa/preview_scenes_ch00.jpg` .. `preview_scenes_ch08.jpg` và `output/long/mim-jobs-1985/qa/tmp_scene_frames/chNN_sMM.jpg`

---

## 2. Kết quả kiểm 9 hạng mục trọng tâm trong ticket

| # | Hạng mục kiểm tra | Trạng thái | Chi tiết & Bằng chứng |
|---|---|---|---|
| 1 | **Chữ tràn hoặc bị cắt** | **Còn lỗi mới (`chặn`)** | - Các lỗi tràn cũ đã hết: `ch04#18` nút `"PIXAR / ĐẦU TƯ · PHIM ĐỒ HỌA"` vừa gọn trong hộp (`ch04_s18.jpg`); `ch00#10` (`"BƯỚC MỘT"`) và `ch07#4` (`"TẠM QUYỀN"`) tự co ~95% vừa khung, không mất nét.<br>- **Lỗi mới phát sinh (`chặn`):** 4 cảnh đổi từ `photo` sang `print` (`ch03#6`, `ch04#4`, `ch05#11`, `ch07#6`) truyền tiêu đề chính vào tham số `head` (trường bị renderer `print` bỏ qua) và để trống `side.h = ""`, làm **mất hoàn toàn tiêu đề lớn bên phải** ở cả 4 cảnh.<br>- **Lỗi nhỏ (`nhỏ`):** Ở `ch03#0` và `ch08#0` (`chapter`), dấu mũ + sắc của chữ `"Ấ"` (`"MẤT QUYỀN,"`, `"THẤT BẠI NÀO"`) chạm nhẹ vào dòng chữ xanh `"CHƯƠNG BA"` / `"CHƯƠNG TÁM"` phía trên. |
| 2 | **Ledger đè lên phụ đề** | **Đã hết** | Hàm `ledger(n, at)` (`gen_scenes.py` dòng 82) đã giới hạn tối đa 5 dòng (`ROWS[max(0,n-5):n]`). Cả `ch07#14` (`preview_ch07.jpg` mốc `57s`, `ch07_s14.jpg`) và `ch08#9` (`preview_ch08.jpg` mốc `36s`, `ch08_s09.jpg`) chỉ hiện 5 dòng, đáy bảng dừng ở `y ≈ 820px`, cách xa hộp phụ đề phía dưới. |
| 3 | **Mặt Sculley bị phụ đề đè** | **Đã hết đè mặt / Còn lộ thẻ tên (`nên sửa`)** | - `ch03#6` và `ch07#6` đã chuyển từ `photo` toàn màn hình sang `print` (`ch03_s06.jpg`, `ch07_s06.jpg`); ảnh `sculley06` nằm trong khung Polaroid bên trái nên phụ đề ở đáy giữa màn hình không còn đè lên cằm/miệng John Sculley.<br>- Tuy nhiên, do khung Polaroid của `print` có tỷ lệ dọc `~3:4` trùng với tỷ lệ gốc của `sculley06.jpg` (`960×1280`), `focus: [0.5, 0.25]` không cắt bỏ được phần dưới ảnh; **thẻ tên hội nghị màu trắng (`"John Sculley / Partner / Sculley Brothers, LLC"`) ở ngực áo vẫn lộ nguyên** trong khung Polaroid ở cả `ch03#6` và `ch07#6`. |
| 4 | **Ảnh `nextcube` không còn lộ chữ `"minitel"`** | **Chưa hết (`chặn`)** | Ảnh `nextcube.jpg` (`1920×1280`, tỷ lệ ngang `3:2 = 1.50`) đặt trong khung `16:9` (`1.78`) với `object-fit: cover` đã phủ 100% chiều ngang `1920px`, nên `focus: [0.72, 0.45]` (`object-position-x: 72%`) có **độ dịch ngang bằng 0px**. Do đó ở cả 3 cảnh dùng `nextcube` (`ch04#6` `photo`, `ch05#11` `print`, `ch07#0` `chapter`), **chữ `"minitel / 3615 / FRED"` và bảng tiếng Anh `"MINITEL AND TELETEXT: LONG RUNNING SUCCESSES"` vẫn lộ rõ hoàn toàn** (`ch04_s06.jpg`, `ch05_s11.jpg`, `ch07_s00.jpg`). Ở `ch07#0`, chữ `"minitel 3615 FRED"` còn đè ngay dưới HUD `"CHƯƠNG 07"`. |
| 5 | **`"AMELIO"` hiện đủ** | **Đã hết** | `ch07#2` (`5.63–8.95s`, `ch07_s02.jpg`, `preview_ch07.jpg` mốc `06s`–`09s`) đã đổi thành `kinetic(a(1,"nói"), "CỐ VẤN CHO GIL AMELIO", "VAI TRÒ ĐẦU TIÊN · THEO THÔNG CÁO")`, hiển thị trọn vẹn `"CỐ VẤN CHO GIL AMELIO"` có gạch chân `"AMELIO"` màu cam. |
| 6 | **Nhãn `TRÍCH DỊCH`** | **Đã hết ở `ch03#8`, `ch07#7` / Còn thiếu ở `ch01#6` (`nên sửa`)** | - `ch03#8` (`ch03_s08.jpg`, `preview_ch03.jpg` mốc `33s`, `36s`) và `ch07#7` (`ch07_s07.jpg`, `preview_ch07.jpg` mốc `24s`) đã hiển thị đúng nhãn **`TRÍCH DỊCH`** ở góc trên phải khung trích dẫn và gõ xong toàn bộ câu từ sớm.<br>- Riêng `ch01#6` (`19.52–24.28s`, `ch01_s06.jpg`, `preview_ch01.jpg` mốc `21s`) hiển thị câu trích dịch ngôi thứ nhất trong ngoặc kép `"HỘI ĐỒNG ĐÃ CHỌN CHÍNH NGƯỜI TÔI MỜI VỀ." — STEVE JOBS · STANFORD 2005` nhưng vẫn mang nhãn **`DIỄN Ý`**. |
| 7 | **Không còn cảnh có chữ nào hiện dưới 2,5 giây** | **Đã hết** | Kiểm tra toàn bộ 127 cảnh (`ch00#0`..`ch08#9`): thời lượng cảnh ngắn nhất là **`2.50s`** (`ch02#4`: `13.93–16.43s`), dài nhất là **`8.16s`** (`ch06#10`: `39.36–47.52s`), **0 cảnh `< 2.5s`**. (Chỉ còn 2 nút phụ cuối sơ đồ `org` ở `ch06#3` và `ch03#7` xuất hiện ở nửa cuối cảnh còn `1.16s` và `1.28s` — mức `nhỏ`). |
| 8 | **Màn trống hoặc đen quá 1 giây** | **Đã hết** | Chạy `ffmpeg blackdetect=d=0.5:pix_th=0.10` trên toàn bộ 9 file `draft.mp4` trả về **0 đoạn đen**. Các cảnh từng bị trống nửa đầu (`ch04#12`, `ch06#8`, `ch06#15`, `ch06#16`) đều đã neo phần tử đầu tại `+0.0s` khi mở cảnh. |
| 9 | **Tiếng và hình khớp nhau** | **Đạt** | Thời lượng 9 file `draft.mp4` khớp tuyệt đối với `dur` trong `data.js` (sai số `≤ 0.03s`). Mốc `t0..t1` và `at` của 127 cảnh bám đúng word timestamps của Whisper; clip lỗi `854167.mp4` (lộ `"MacBook Pro"` và kệ đĩa DVD) đã được gỡ bỏ hoàn toàn (0 lần dùng). |

---

## 3. Bảng xác nhận từng lỗi cũ trong `GH-10-fix-report.md` & `GH-10-qa-report.md`

| Scene ID | Vấn đề gốc trong QA | Trạng thái | Bằng chứng trên bản preview (`draft.mp4` & `qa/preview_*.jpg`) |
|---|---|---|---|
| `ch00#0` | Cảnh dài 2.19s (< 2.5s); mặt Jobs hơi lệch | **Đã hết** | Cảnh dài `2.68s` (`0.00–2.68s`); `focus: [0.5, 0.18]` lấy rõ mặt Steve Jobs (`preview_ch00.jpg` @`00s`, `ch00_s00.jpg`). |
| `ch00#7` | Chênh mốc 1 và mốc 3 của `timeline` là 3.65s; từng gắn `bg="nextcube"` | **Đã hết** | Cảnh `27.10–32.73s` (`5.64s`); 3 mốc xuất hiện tại `27.10s`, `28.41s`, `29.92s` (chênh `1.32s` và `1.51s`), nền tối sạch không còn ảnh `nextcube` (`preview_ch00.jpg` @`30s`, `ch00_s07.jpg`). |
| `ch00#9` | Cảnh `slam` dài 2.37s (< 2.5s) | **Đã hết** | Cảnh dài `3.27s` (`36.21–39.48s`), chữ `"Ở LẠI ĐỂ TRANH ĐẤU"` hiện đủ và rõ (`preview_ch00.jpg` @`39s`, `ch00_s09.jpg`). |
| `ch00#10` | Cảnh `kinetic` dài 2.34s (< 2.5s); cảnh báo co chữ `"BƯỚC MỘT"` | **Đã hết** | Cảnh dài `2.96s` (`39.48–42.43s`); `"BƯỚC MỘT / TRONG BA BƯỚC LỚN"` tự co 95% vừa khung, không mất chữ (`preview_ch00.jpg` @`42s`, `ch00_s10.jpg`). |
| `ch01#2` | Ảnh `jobs84` cắt ngang cằm và mất máy Macintosh; chữ phụ trễ 1.57s | **Đã hết** | Đổi sang `print` (`5.12–8.96s`), khung Polaroid bên trái hiển thị trọn Steve Jobs và máy Macintosh 128K; cột phải hiện đủ `"MACINTOSH / RA MẮT / GIAI ĐOẠN ĐẦY KỲ VỌNG"` ngay từ `5.12s` (`preview_ch01.jpg` @`06s`, `ch01_s02.jpg`). |
| `ch01#3` | Ảnh dọc `mac84` bị cắt đáy máy; cảnh lân cận ngắn | **Đã hết** | `focus: [0.45, 0.35]` lấy rõ màn hình và ổ đĩa Macintosh 128K; `ch01#3` dài `2.94s` (`8.96–11.90s`), `ch01#4` dài `2.74s` (`preview_ch01.jpg` @`09s`, `ch01_s03.jpg`). |
| `ch01#5` | Chữ `slam` `"NHÀ SÁNG LẬP"` viền mảnh hơi tối | **Đã hết** | Chữ `"NHÀ SÁNG LẬP"` hiện dạng chữ đặc trắng sáng rõ (`fx: "punch"`) trên nền tối (`preview_ch01.jpg` @`15s`, `18s`, `ch01_s05.jpg`). |
| `ch02#0` | Ảnh `sculley06` lặp trong cùng chương; cảnh chỉ dài 2.12s | **Đã hết** | Cảnh dài `2.67s` (`0.00–2.67s`); `ch02#4` đã đổi sang `org` nên `sculley06` không còn lặp trong `ch02` (`preview_ch02.jpg` @`00s`, `ch02_s00.jpg`). |
| `ch02#1` | Cảnh `date` dài 2.43s (< 2.5s); chữ phụ trễ | **Đã hết** | Cảnh dài `3.33s` (`2.67–5.99s`), thẻ `"04.1985 / KỲ HỌP HỘI ĐỒNG QUẢN TRỊ"` hiển thị đầy đủ (`preview_ch02.jpg` @`03s`, `ch02_s01.jpg`). |
| `ch02#2` | Dời neo chữ về `"cuộc"` (5.99s) để trả thời lượng cho `ch02#1` | **Đã hết** | Cảnh `5.99–9.26s` (`3.27s`), chữ `"BẤT ĐỒNG VỀ MACINTOSH"` khớp lời đọc (`preview_ch02.jpg` @`06s`, `09s`, `ch02_s02.jpg`). |
| `ch02#4` | Lặp `sculley06` trong cùng chương và lộ thẻ tên | **Đã hết** | Đổi sang sơ đồ `org` 3 nút (`HỘI ĐỒNG` → `SCULLEY` / `JOBS`) từ `16.43–21.07s`, sạch và rõ (`preview_ch02.jpg` @`18s`, `ch02_s05.jpg` — nay là cảnh `#5` do chèn cảnh). |
| `ch02#5` (nay là `ch02#6`) | Ảnh `mac84` cắt đáy máy; chữ xuất hiện trễ | **Đã hết** | Cảnh `21.07–24.16s` (`3.10s`), nhãn `"BỘ PHẬN MACINTOSH / CẦN MỘT NGƯỜI QUẢN LÝ MỚI"` hiện ngay từ `21.07s` (`preview_ch02.jpg` @`24s`, `ch02_s06.jpg`). |
| `ch02#10` (nay là `ch02#11`) | Mốc 2 của `timeline` hiện ở 37.34s (còn 1.85s) | **Đã hết** | Mốc 1 tại `34.80s`, mốc 2 tại `37.34s` (khớp từ `"đơn"` trong `"đơn từ chức"`, hiện đủ `1.85s` đến `39.19s`, `preview_ch02.jpg` @`36s`, `39s`, `ch02_s11.jpg`). |
| `ch03#0` | Ảnh `sculley06` dùng quá số lần; cảnh dài 2.17s (< 2.5s) | **Đã hết lỗi cũ / Có lỗi nhỏ dấu chữ** | Đã đổi nền sang `ai05` (có nhãn `ẢNH MINH HỌA`) và kéo dài lên `2.69s` (`0.00–2.69s`). *(Lưu ý nhỏ: dấu chữ `"Ấ"` của `"MẤT QUYỀN,"` chạm nhẹ chữ `"CHƯƠNG BA"` ở `ch03_s00.jpg`)*. |
| `ch03#1` | Mốc 2 của `timeline` trễ 2.76s sau mốc 1 | **Đã hết** | Mốc 1 tại `2.69s`, mốc 2 tại `3.11s` (chênh `0.42s`, hiện suốt `3.22s` đến `6.33s`, `preview_ch03.jpg` @`03s`, `06s`, `ch03_s01.jpg`). |
| `ch03#4` | Highlight `source` ở 15.08s sát cuối cảnh | **Đã hết** | Cảnh mở sớm từ `13.24–16.48s` (`3.24s`), highlight tại `15.08s` hiện đủ `1.40s` (`preview_ch03.jpg` @`15s`, `ch03_s04.jpg`). |
| `ch03#6` | Ảnh `sculley06` phóng toàn màn hình bị phụ đề đè mặt và lộ thẻ tên | **Còn lỗi (`chặn` + `nên sửa`)** | - Đổi sang `print` (`20.53–27.88s`) nên phụ đề không còn đè mặt Sculley.<br>- **Lỗi mới (`chặn`):** Tiêu đề `"JOHN SCULLEY · 25.07.1985"` truyền vào `head` thay vì `side.h` nên **bị mất hoàn toàn trên màn hình**.<br>- **Lỗi còn (`nên sửa`):** Khung Polaroid dọc ~3:4 vẫn lộ nguyên thẻ tên `"John Sculley"` ở ngực áo (`preview_ch03.jpg` @`21s`, `24s`, `27s`, `ch03_s06.jpg`). |
| `ch03#7` | Nút 2 của `org` hiện ở 30.17s (còn 1.28s) | **Còn hơi ngắn (`nhỏ`)** | Cảnh `27.88–31.45s` (`3.57s`), nút 2 `"BƯỚC 2 · TỰ NỘP ĐƠN"` hiện lúc `30.17s` khớp lời đọc `"tự nộp đơn"`, giữ trên hình `1.28s` (`preview_ch03.jpg` @`30s`, `ch03_s07.jpg`). |
| `ch03#8` | Nhãn trích dẫn để `DIỄN Ý` thay vì `TRÍCH DỊCH` | **Đã hết** | Đã hiện đúng nhãn **`TRÍCH DỊCH`** ở góc trên phải khung quote; chữ gõ xong lúc `33.40s`, giữ trọn câu `4.40s` đến `37.80s` (`preview_ch03.jpg` @`33s`, `36s`, `ch03_s08.jpg`). |
| `ch03#9` | Bố cục `kinetic` hơi trống | **Đã hết** | Hiển thị trong khung viền `frame` cân đối từ `37.80–42.01s` (`preview_ch03.jpg` @`39s`, `42s`, `ch03_s09.jpg`). |
| `ch03#10` | Clip `5924021` dùng 3 lần toàn bài | **Đã hết** | Sau khi đổi `ch06#6` sang `8426053`, clip `5924021` chỉ còn dùng đúng 2 lần (`ch00#1`, `ch03#10`). |
| `ch03#12` | Ảnh `nextcube2` bị cắt sát cạnh phải thân máy | **Đã hết** | Đổi sang `print` (`48.48–52.27s`), thân máy NeXTcube nằm gọn trong khung Polaroid bên trái; cột phải hiện đủ `"1985 / RỜI APPLE ĐỂ LẬP NEXT / MANG THEO CỘNG SỰ"` (`preview_ch03.jpg` @`51s`, `ch03_s12.jpg`). |
| `ch04#0` | Cảnh dài 2.20s (< 2.5s); ảnh nền `nextcube2` lặp và cắt cạnh | **Đã hết** | Đổi nền sang `ai04` (kèm nhãn `ẢNH MINH HỌA`) và kéo dài lên `2.66s` (`0.00–2.66s`, `preview_ch04.jpg` @`00s`, `ch04_s00.jpg`). |
| `ch04#2` | Clip `854167` lộ chữ kệ đĩa DVD và chữ `"MacBook Pro"` | **Đã hết** | Đã thay bằng clip `6285657` (`6.19–9.37s`, bàn họp đối chiếu tài liệu sạch sẽ, không lộ chữ thương hiệu, `preview_ch04.jpg` @`09s`, `ch04_s02.jpg`). |
| `ch04#3` | Cảnh `slam` dài 2.08s (< 2.5s) | **Đã hết** | Cảnh kéo dài lên `2.64s` (`9.37–12.00s`, `preview_ch04.jpg` @`12s`, `ch04_s03.jpg`). |
| `ch04#4` | Lặp `nextcube2` và cắt cạnh phải thân máy | **Còn lỗi mới (`chặn`)** | - Đổi sang `print` (`12.00–15.45s`) nên không còn cắt máy và không lặp với `ch04#0`.<br>- **Lỗi mới (`chặn`):** Tiêu đề `"NEXT COMPUTER"` truyền vào `head` thay vì `side.h` nên **bị mất hoàn toàn trên màn hình**, chỉ còn dòng phụ `"RA MẮT NĂM 1988"` và `"HƯỚNG TỚI ĐẠI HỌC"` (`preview_ch04.jpg` @`15s`, `ch04_s04.jpg`). |
| `ch04#6` | Ảnh `nextcube` lộ máy và chữ `"minitel 3615 FRED"` bên trái; nhãn đè bàn phím | **Còn (`chặn`)** | `focus: [0.72, 0.45]` không dịch ngang được ảnh `3:2` trong khung `16:9`. Máy Minitel bên trái, chữ **`"minitel / 3615 / FRED"`** và bảng tiếng Anh **`"MINITEL AND TELETEXT: LONG RUNNING SUCCESSES"`** vẫn lộ nguyên trên màn hình từ `19.80–24.80s` (`preview_ch04.jpg` @`21s`, `24s`, `ch04_s06.jpg`). |
| `ch04#12` | Biểu đồ `bars` trống suốt 2.43s đầu cảnh | **Đã hết** | Thanh 1 `"TRẢ LUCASFILM"` (`5 TRIỆU USD`) xuất hiện ngay khi mở cảnh ở `44.65s` (trễ `0.0s`), thanh 2 ở `47.19s` (`preview_ch04.jpg` @`45s`, `48s`, `ch04_s12.jpg`). |
| `ch04#14` | Nền `timeline` trống trong lúc chờ mốc 2 | **Đã hết** | Đã gắn video nền `7988642` (khán phòng rạp chiếu phim, có nhãn `VIDEO MINH HỌA`) từ `55.08–61.99s` (`preview_ch04.jpg` @`57s`, `60s`, `ch04_s14.jpg`). |
| `ch04#15` | Cảnh `slam` dài 2.09s (< 2.5s) | **Đã hết** | Cảnh kéo dài lên `2.75s` (`61.99–64.74s`, `preview_ch04.jpg` @`63s`, `ch04_s15.jpg`). |
| `ch04#18` | Nút 3 `"PIXAR"` trong `org` bị tràn chữ dòng phụ `"KHOẢN ĐẦU TƯ RIÊNG · PHIM ĐỒ HỌA"` | **Đã hết** | Dòng phụ đã rút gọn thành `"ĐẦU TƯ · PHIM ĐỒ HỌA"`, nằm gọn hoàn toàn trong hộp nút 3 từ `74.87–79.51s` (`preview_ch04.jpg` @`75s`, `78s`, `ch04_s18.jpg`). |
| `ch04#20` | Bảng `ledger` 4 dòng dài 2.80s | **Đã hết** | Hiển thị 4 dòng sạch sẽ từ `82.16–84.96s` (`2.80s`), không đè phụ đề (`preview_ch04.jpg` @`84s`, `ch04_s20.jpg`). |
| `ch05#0` | Cảnh `chapter` dài 2.29s (< 2.5s) | **Đã hết** | Cảnh dài `2.66s` (`0.00–2.66s`, `preview_ch05.jpg` @`00s`, `ch05_s00.jpg`). |
| `ch05#1` | Ảnh nền `nextcube` dưới `counter` làm giảm tương phản chữ và lộ Minitel | **Đã hết** | Đã bỏ ảnh nền `nextcube`; số `50 NGHÌN MÁY` nổi bật rõ trên nền tối từ `2.66–6.60s` (`preview_ch05.jpg` @`03s`, `06s`, `ch05_s01.jpg`). |
| `ch05#2` | Lặp ảnh `nextstation` trong cùng chương `ch05` | **Đã hết** | Đã bỏ ảnh nền `nextstation` khỏi `ch05#2` (`6.60–9.27s`, `preview_ch05.jpg` @`09s`, `ch05_s02.jpg`). |
| `ch05#3` | Thanh 2 của `bars` hiện ở 10.50s (còn 2.22s) | **Đã hết** | Thanh 1 hiện ngay tại `9.27s`, thanh 2 tại `10.50s` (hiện đủ `2.22s` đến `12.72s`, `preview_ch05.jpg` @`12s`, `ch05_s03.jpg`). |
| `ch05#4, ch05#14` | Lặp ảnh AI `ai04` trong cùng chương `ch05` | **Đã hết** | `ch05#4` giữ `ai04` (`12.72–16.69s`), còn `ch05#14` đổi sang sơ đồ `org` 2 nút (`54.03–58.05s`, `preview_ch05.jpg` @`57s`, `ch05_s14.jpg`). |
| `ch05#6` | Chữ `"GIÁ TRỊ Ở BÊN TRONG"` hơi chìm; cảnh trước `ch05#5` ngắn | **Đã hết** | `ch05#5` đạt `2.58s` (`16.69–19.27s`); `ch05#6` (`19.27–24.13s`) phủ lớp tối `veil: 0.6` giúp chữ trắng tách nền rõ (`preview_ch05.jpg` @`21s`, `24s`, `ch05_s06.jpg`). |
| `ch05#11` | Ảnh `nextcube` lộ `"minitel 3615 FRED"` và nhãn đè bàn phím | **Còn (`chặn`)** | Đổi sang `print` (`40.23–46.20s`) giúp chữ sang cột phải không đè bàn phím, **NHƯNG phát sinh 2 lỗi mức `chặn`**:<br>1. Khung ảnh bên trái vẫn lộ rõ máy Minitel và chữ **`"minitel / 3615 / FRED"`**.<br>2. Tiêu đề `"CERN · WEBSITE ĐẦU TIÊN"` đặt ở `head` thay vì `side.h` nên **bị mất hoàn toàn trên màn hình** (`preview_ch05.jpg` @`42s`, `45s`, `ch05_s11.jpg`). |
| `ch05#16` | Clip `854027` quá tối khi đứng một mình làm `broll` | **Đã hết** | Đổi sang `kinetic` có nền `vid: 854027` (`62.03–67.59s`), chữ lớn `"NHÌN VÀO THỨ ĐƯỢC XÂY / TRÊN HỆ ĐIỀU HÀNH ẤY"` chiếm chủ đạo (`preview_ch05.jpg` @`63s`, `66s`, `ch05_s16.jpg`). |
| `ch06#0` | Ảnh nền `nextcube2` lặp quá số lần và cắt cạnh | **Đã hết** | Đổi nền sang `ai03` (có nhãn `ẢNH MINH HỌA`), dài `2.88s` (`0.00–2.88s`, `preview_ch06.jpg` @`00s`, `ch06_s00.jpg`). |
| `ch06#1` | Cảnh `broll` dài 2.45s (< 2.5s) | **Đã hết** | Kéo dài lên `3.53s` (`2.88–6.41s`, `preview_ch06.jpg` @`03s`, `06s`, `ch06_s01.jpg`). |
| `ch06#3` | Cảnh `org` dài 2.34s (< 2.5s) | **Đã hết lỗi độ dài cảnh / Nút 3 hơi ngắn (`nhỏ`)** | Cảnh dài `2.90s` (`10.14–13.04s`). Tuy nhiên nút 3 `"NEXT / NEXTSTEP"` xuất hiện lúc `11.89s`, chỉ còn hiện `1.16s` trước khi sang `ch06#4` (`ch06_s03.jpg`). |
| `ch06#6` | Clip nền `5924021` dùng lần 3 toàn bài | **Đã hết** | Đã đổi sang clip `8426053` (`18.42–22.62s`, `preview_ch06.jpg` @`21s`, `ch06_s06.jpg`). |
| `ch06#7` | Highlight `source` ở 27.18s (cảnh 22.62–29.92s) | **Đã hết** | Highlight hiện rõ suốt `2.75s` cuối cảnh (`preview_ch06.jpg` @`27s`, `ch06_s07.jpg`). |
| `ch06#8` | Thanh 1 của `bars` xuất hiện trễ | **Đã hết** | Thanh 1 hiện ngay lúc mở cảnh `29.92s` (trễ `0.0s`), thanh 2 hiện lúc `31.75s` (`preview_ch06.jpg` @`30s`, `33s`, `ch06_s08.jpg`). |
| `ch06#10` | Thanh 2 của `bars` hiện ở 43.89s theo lời đọc | **Đã hết** | Thanh 1 tại `39.36s`, thanh 2 tại `43.89s` (khớp giọng đọc và còn hiện `3.63s` đến `47.52s`, `preview_ch06.jpg` @`42s`, `45s`, `ch06_s10.jpg`). |
| `ch06#12` | Clip nền `854167` lộ chữ `"MacBook Pro"` và kệ đĩa DVD | **Đã hết** | Đã thay bằng clip `6285657` (`52.14–56.71s`, `preview_ch06.jpg` @`54s`, `ch06_s12.jpg`). |
| `ch06#14` | Ảnh `nextstation` dùng quá 3 lần toàn bài | **Đã hết** | Sau khi gỡ ở `ch05#2`, `ch07#9`, `ch08#6`, `nextstation` chỉ còn dùng đúng 3 lần (`ch04#9`, `ch05#0`, `ch06#14`). |
| `ch06#15` | Nút 5 `"STEVE JOBS"` của `org` xuất hiện sát cuối cảnh | **Đã hết** | Cả 5 nút (`MUA NEXT` → `OPENSTEP`, `MACH KERNEL`, `WEBOBJECTS`, `STEVE JOBS`) đều đã hiện đầy đủ từ `68.17s` đến `71.12s` (`2.96s`, `preview_ch06.jpg` @`69s`, `ch06_s15.jpg`). |
| `ch06#16` | Cảnh `split` trống nửa phải 2.27s và lặp ảnh `nextcube`/`nextstation` | **Đã hết** | Đổi sang `kinetic` (`71.12–75.82s`), chữ `"MỘT QUYẾT ĐỊNH · HAI HỆ QUẢ / KỸ THUẬT · NHÂN SỰ"` hiện ngay từ đầu cảnh (`preview_ch06.jpg` @`72s`, `75s`, `ch06_s16.jpg`). |
| `ch07#0` | Ảnh nền `nextcube` lộ chữ `"minitel 3615 FRED"` góc trên trái | **Còn (`chặn`)** | Ở `ch07#0` (`0.00–2.97s`), chữ **`"minitel / 3615 / FRED"`** và máy Minitel vẫn lộ rõ ngay dưới HUD `"CHƯƠNG 07 THƯƠNG VỤ KHÉP VÒNG"`, kèm bảng tiếng Anh ở đáy trái (`preview_ch07.jpg` @`00s`, `ch07_s00.jpg`). |
| `ch07#1` | Cảnh `date` dài 2.13s (< 2.5s) và bị chồng mờ ở 4.90s | **Đã hết** | Cảnh kéo dài lên `2.67s` (`2.97–5.63s`); khung hình ở giữa cảnh (`3.5s–5.5s`) hoàn toàn sạch, không còn chồng chữ chương (`preview_ch07.jpg` @`03s`, `ch07_s01.jpg`). |
| `ch07#2` | Lặp ảnh `nextcube` trong `ch07`; chữ `"GIL AMELIO"` bị cắt mất `"AMELIO"` | **Đã hết** | Đã bỏ ảnh nền `nextcube` và đổi sang `kinetic` `"CỐ VẤN CHO GIL AMELIO / VAI TRÒ ĐẦU TIÊN · THEO THÔNG CÁO"` (`5.63–8.95s`), chữ `"AMELIO"` hiện đầy đủ (`preview_ch07.jpg` @`06s`, `09s`, `ch07_s02.jpg`). |
| `ch07#3` | Ảnh nền `nextcube2` dùng lần 4; mốc 2 `timeline` hiện sát cuối | **Đã hết** | Đã bỏ nền `nextcube2`; mốc 2 hiện từ `10.32s` đến `12.33s` (`2.01s`, `preview_ch07.jpg` @`12s`, `ch07_s03.jpg`). |
| `ch07#4` | Cảnh báo co chữ `"TẠM QUYỀN"` | **Đã hết** | Chữ `"TẠM QUYỀN / THÁNG 9 · 1997"` tự co ~95% vừa khung, rõ nét từ `12.33–15.65s` (`preview_ch07.jpg` @`15s`, `ch07_s04.jpg`). |
| `ch07#6` | Ảnh `sculley06` phóng lớn bị phụ đề đè mặt và lộ thẻ tên | **Còn lỗi (`chặn` + `nên sửa`)** | - Đổi sang `print` (`19.36–22.13s`) nên phụ đề không còn đè mặt Sculley.<br>- **Lỗi mới (`chặn`):** Tiêu đề `"JOHN SCULLEY"` truyền vào `head` thay vì `side.h` nên **bị mất hoàn toàn trên màn hình**.<br>- **Lỗi còn (`nên sửa`):** Khung Polaroid vẫn lộ rõ thẻ tên `"John Sculley"` trên áo (`preview_ch07.jpg` @`21s`, `ch07_s06.jpg`). |
| `ch07#7` | Chữ `quote` gõ chưa xong (`"MỘT SAI LẦ"`) và gắn nhãn `DIỄN Ý` | **Đã hết** | Cảnh mở sớm từ `22.13–26.93s` (`4.80s`), câu trích dẫn gõ xong hoàn toàn lúc `24.93s` (giữ nguyên trọn câu `2.00s` trước khi hết cảnh) và đã gắn đúng nhãn **`TRÍCH DỊCH`** (`preview_ch07.jpg` @`24s`, `ch07_s07.jpg`). |
| `ch07#9` | Ảnh nền `nextstation` dùng lần 6 | **Đã hết** | Đã bỏ ảnh nền `nextstation` khỏi `ch07#9` (`33.32–36.91s`, `preview_ch07.jpg` @`36s`, `ch07_s09.jpg`). |
| `ch07#14` | Bảng `ledger` 8 dòng tràn xuống đè lên phụ đề | **Đã hết** | Bảng `ledger` chỉ còn hiển thị 5 dòng (`54.07–58.03s`), nằm hoàn toàn phía trên phụ đề (`preview_ch07.jpg` @`57s`, `ch07_s14.jpg`). |
| `ch08#0` | Ảnh nền `nextcube2` dùng quá 3 lần và bị cắt | **Đã hết lỗi cũ / Có lỗi nhỏ dấu chữ** | Tổng số lần dùng `nextcube2` giảm về 3 và có `focus: [0.5, 0.38]`. *(Lưu ý nhỏ: dấu chữ `"Ấ"` của `"THẤT BẠI NÀO"` chạm nhẹ chữ `"CHƯƠNG TÁM"` ở `ch08_s00.jpg`)*. |
| `ch08#1` | Ảnh dọc `jobs84` bị cắt ngang cổ/vai, mất máy Macintosh | **Đỡ hơn nhưng vẫn mất máy (`nhỏ`)** | `focus: [0.5, 0.18]` lấy trọn đầu và vai Steve Jobs (`3.65–7.36s`), nhưng vì là cảnh `photo` `16:9` cắt ngang từ ảnh dọc `2:3` nên phần máy Macintosh phía dưới tay vẫn nằm ngoài khung (`preview_ch08.jpg` @`06s`, `ch08_s01.jpg`). |
| `ch08#6` | Ảnh nền `nextstation` dùng lần 7 | **Đã hết** | Đã bỏ ảnh nền `nextstation` khỏi `ch08#6` (`21.92–26.64s`, `preview_ch08.jpg` @`24s`, `ch08_s06.jpg`). |
| `ch08#9` | Bảng `ledger` 9 dòng tràn xuống đè lên phụ đề | **Đã hết** | Bảng `ledger` chỉ còn 5 dòng cuối (`34.93–38.03s`), không đè phụ đề (`preview_ch08.jpg` @`36s`, `ch08_s09.jpg`). |

---

## 4. Bảng lỗi mới phát sinh & lỗi cũ chưa dứt điểm cần sửa

| # | Scene ID | Mốc giây | Severity | Bằng chứng cụ thể | Đề xuất sửa |
|---|---|---|---|---|---|
| 1 | `ch03#6`<br>`ch04#4`<br>`ch05#11`<br>`ch07#6` | `ch03`: `20.53–27.88s`<br>`ch04`: `12.00–15.45s`<br>`ch05`: `40.23–46.20s`<br>`ch07`: `19.36–22.13s` | **chặn** | **Lỗi mới phát sinh khi đổi từ `photo` sang `print`:** Trong `data/long/mim-jobs-1985/gen_scenes.py`, hàm `print_scene(img, at, head, k, h, lines)` gán `o["head"] = head` và `o["side"] = {"k": k, "h": h, "lines": ...}`. Tuy nhiên renderer `print` của theme `lab` chỉ vẽ `side.k` (nhãn xanh nhỏ), `side.h` (tiêu đề serif lớn) và `side.lines` (ghi chú gạch đầu dòng), hoàn toàn **không vẽ `o["head"]`**. Ở `ch01#2` và `ch03#12`, Codex truyền tiêu đề vào tham số thứ 5 (`h`) nên hiện đủ; nhưng ở 4 cảnh `ch03#6`, `ch04#4`, `ch05#11`, `ch07#6`, Codex lại truyền tiêu đề chính vào tham số thứ 3 (`head`) và để `h = ""`, khiến **4 tiêu đề chính biến mất hoàn toàn khỏi màn hình**:<br>- `ch03#6`: mất `"JOHN SCULLEY · 25.07.1985"` (`ch03_s06.jpg`, `preview_ch03.jpg` @`21s–27s`)<br>- `ch04#4`: mất `"NEXT COMPUTER"` (`ch04_s04.jpg`, `preview_ch04.jpg` @`15s`)<br>- `ch05#11`: mất `"CERN · WEBSITE ĐẦU TIÊN"` (`ch05_s11.jpg`, `preview_ch05.jpg` @`42s–45s`)<br>- `ch07#6`: mất `"JOHN SCULLEY"` (`ch07_s06.jpg`, `preview_ch07.jpg` @`21s`) | Trong `data/long/mim-jobs-1985/gen_scenes.py` (dòng 135, 148, 179, 216), chuyển chuỗi ở tham số thứ 3 (`head`) sang tham số thứ 5 (`h`) hoặc sửa hàm `print_scene` để tự gán `"h": h or head` (và đảo `k`/`h` cho đồng nhất: dòng nhãn ngắn ở `k`, tiêu đề chính ở `h`, giống `ch01#2` và `ch03#12`). |
| 2 | `ch04#6`<br>`ch05#11`<br>`ch07#0` | `ch04`: `19.80–24.80s`<br>`ch05`: `40.23–46.20s`<br>`ch07`: `0.00–2.97s` | **chặn** | **Ảnh `nextcube` vẫn lộ nguyên chữ `"minitel 3615 FRED"` và bảng bảo tàng tiếng Anh:** File `output/long/mim-jobs-1985/img/nextcube.jpg` có kích thước `1920×1280` (tỷ lệ `3:2 = 1.50`). Khi đặt vào khung `16:9` (`1.78` ở `ch04#6` `photo` và `ch07#0` `chapter`) với `object-fit: cover`, ảnh được khớp theo chiều ngang `1920px` và chỉ cắt trên/dưới, nên `focus: [0.72, 0.45]` (`object-position: 72% 45%`) có **độ dịch ngang bằng 0px**; còn ở khung Polaroid `4:3` của `ch05#11` (`print`) cũng chỉ cắt ~11% mép trái. Hậu quả là ở cả 3 cảnh (`ch04_s06.jpg`, `ch05_s11.jpg`, `ch07_s00.jpg`), chiếc máy Minitel của Pháp ở góc trên trái cùng dòng chữ **`"minitel / 3615 / FRED"`** và tấm bảng **`"MINITEL AND TELETEXT: LONG RUNNING SUCCESSES"`** ở góc dưới trái vẫn hiện rõ mồn một. Ở `ch07#0`, chữ `"minitel 3615 FRED"` đè ngay dưới HUD `"CHƯƠNG 07"`. Ngoài ra ở `ch04#6`, nhãn vẫn ghi `"MÀN HÌNH ĐỘ PHÂN GIẢI CAO"` trong khi màn hình CRT trong ảnh đang tắt đen. | **Cách triệt để nhất:** Crop trực tiếp file ảnh `output/long/mim-jobs-1985/img/nextcube.jpg` (cùng bản gốc trong `data/long/mim-jobs-1985/` nếu có) lấy vùng bên phải `x = 540..1920, y = 0..1080` để loại bỏ vĩnh viễn máy Minitel và bảng thuyết minh `"MINITEL AND TELETEXT"` ở bên trái, chỉ giữ lại cụm màn hình NeXT, bàn phím và khối NeXTcube. Đồng thời ở `ch04#6` đổi nhãn `"MÀN HÌNH ĐỘ PHÂN GIẢI CAO"` thành `"CỤM MÁY TRẠM NEXTCUBE"` cho khớp hình màn hình đang tắt. |
| 3 | `ch03#6`<br>`ch07#6` | `ch03`: `20.53–27.88s`<br>`ch07`: `19.36–22.13s` | **nên sửa** | **Ảnh `sculley06` vẫn lộ thẻ tên hội nghị ở ngực áo:** Do `sculley06.jpg` có kích thước `960×1280` (tỷ lệ dọc `3:4`) và khung Polaroid dọc của cảnh `print` cũng có tỷ lệ `~3:4`, thuộc tính `object-fit: cover` với `focus: [0.5, 0.25]` hầu như không cắt bớt chiều dọc. Vì vậy thẻ tên màu trắng ghi **`"John Sculley / Partner / Sculley Brothers, LLC / New York NY"`** ở phần dưới (`y > 0.75`) vẫn lộ nguyên trong khung Polaroid ở cả `ch03#6` (`ch03_s06.jpg`) và `ch07#6` (`ch07_s06.jpg`). | Crop bỏ 25% cạnh dưới của `output/long/mim-jobs-1985/img/sculley06.jpg` (giữ `y = 0..940`) để loại bỏ hoàn toàn thẻ tên hội nghị ở cả `ch02#0`, `ch03#6` và `ch07#6`. |
| 4 | `ch01#6` | `ch01`: `19.52–24.28s` | **nên sửa** | **Nhãn `DIỄN Ý` trên câu trích dịch ngôi thứ nhất:** Cảnh `quote` ở `ch01#6` (`ch01_s06.jpg`, `preview_ch01.jpg` @`21s`) hiển thị câu `"HỘI ĐỒNG ĐÃ CHỌN CHÍNH NGƯỜI TÔI MỜI VỀ." — STEVE JOBS · STANFORD 2005` trong dấu ngoặc kép với đại từ ngôi thứ nhất `"TÔI"` (dịch từ bài phát biểu Stanford 2005 của Jobs), nhưng `gen_scenes.py` dòng 105 không truyền tham số `lbl="TRÍCH DỊCH"` nên màn hình hiện nhãn **`DIỄN Ý`**. | Trong `data/long/mim-jobs-1985/gen_scenes.py` dòng 105, thêm tham số thứ 5 `"TRÍCH DỊCH"` vào `quote(...)` (giống `ch03#8` và `ch07#7`), hoặc viết lại nội dung thẻ ở ngôi thứ ba không dùng `"TÔI"`. |
| 5 | `ch03#0`<br>`ch08#0` | `ch03`: `0.00–2.69s`<br>`ch08`: `0.00–3.65s` | **nhỏ** | **Dấu chữ tiêu đề chương chạm nhẹ dòng kicker phía trên:** Ở `ch03#0` (`ch03_s00.jpg`) và `ch08#0` (`ch08_s00.jpg`), dấu mũ + sắc của chữ `"Ấ"` ở dòng đầu tiêu đề lớn (`"MẤT QUYỀN,"` và `"THẤT BẠI NÀO"`) nhô cao chạm nhẹ vào chân chữ xanh `"CHƯƠNG BA"` / `"CHƯƠNG TÁM"`. | Nếu tiện trong lần sửa `gen_scenes.py`, có thể ngắt dòng hoặc đổi từ đầu để chữ có dấu kép (`Ấ`, `Ể`, `Ỗ`) không nằm ngay dưới cụm chữ `"CHƯƠNG ..."`, hoặc giữ nguyên nếu chấp nhận vì chỉ hiện thoáng qua ở thẻ mở chương. |
| 6 | `ch06#3`<br>`ch03#7` | `ch06`: `10.14–13.04s`<br>`ch03`: `27.88–31.45s` | **nhỏ** | **Nút cuối của sơ đồ `org` hiện hơi ngắn trước khi hết cảnh:** Ở `ch06#3` (`ch06_s03.jpg`), nút 3 `"NEXT / NEXTSTEP"` xuất hiện lúc `11.89s` (còn `1.16s` trước khi chuyển cảnh lúc `13.04s`). Ở `ch03#7` (`ch03_s07.jpg`), nút 2 `"BƯỚC 2 · TỰ NỘP ĐƠN"` xuất hiện lúc `30.17s` (còn `1.28s` trước khi chuyển cảnh lúc `31.45s`). | Neo sớm nút 3 của `ch06#3` lên `a(1, "với")` (`10.60s`) và nút 2 của `ch03#7` lên `a(5, "rồi")` (`29.35s`) để người xem có trên `2.0s` đọc trọn sơ đồ trước khi chuyển cảnh. |
| 7 | `ch08#1` | `ch08`: `3.65–7.36s` | **nhỏ** | **Cảnh `photo` `jobs84` cắt mất chiếc máy Macintosh:** Ở `ch08#1` (`ch08_s01.jpg`), `jobs84` dùng layout `photo` `16:9` nên dù `focus: [0.5, 0.18]` lấy rõ khuôn mặt Steve Jobs, chiếc máy Macintosh ở nửa dưới bức ảnh dọc vẫn bị cắt mất (trong khi `ch01#2` dùng `print` lấy được cả người lẫn máy). | Đổi `ch08#1` từ `photo` sang `print_scene` (nhớ truyền tiêu đề vào tham số thứ 5 `h`) để hiển thị trọn cả Steve Jobs lẫn chiếc Macintosh 1984. |

---

## 5. Kết luận

- **Kết luận:** **`cần sửa tiếp`**
- **Lý do:** Dù 52/58 mục lỗi từ đợt QA trước đã được xử lý tốt (độ dài cảnh `≥ 2.5s`, hết đè `ledger`, gỡ sạch clip `854167`, hiện đủ `"AMELIO"`, gắn `TRÍCH DỊCH` cho `ch03#8` & `ch07#7`, đạt toàn bộ cổng tự động), bản render thực tế còn **2 nhóm lỗi mức `chặn`**:
  1. **Mất tiêu đề chính ở 4 cảnh `print` mới đổi (`ch03#6`, `ch04#4`, `ch05#11`, `ch07#6`)** do truyền nhầm tiêu đề vào tham số `head` thay vì `side.h` (`h`).
  2. **Ảnh `nextcube.jpg` vẫn lộ nguyên chữ `"minitel 3615 FRED"` và bảng tiếng Anh `"MINITEL AND TELETEXT"` ở cả 3 cảnh (`ch04#6`, `ch05#11`, `ch07#0`)** vì `focus` ngang không có tác dụng trên ảnh tỷ lệ `3:2` đặt trong khung `16:9`.
- Sau khi sửa nhanh 2 điểm `chặn` này (kèm crop 25% đáy `sculley06.jpg` và thêm `"TRÍCH DỊCH"` cho `ch01#6`), bài `mim-jobs-1985` sẽ sẵn sàng chạy `final`.
