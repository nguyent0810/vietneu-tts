# Báo cáo YCV-ju9q · M1: render, final, khung soát và thumbnail cho `mim-jobs-1985`

## 1. Tóm tắt công việc & Lệnh đã chạy

1. **Kiểm tra cổng chất lượng (`long_gate.py`):**
   - Lệnh: `python -X utf8 scripts/long_gate.py mim-jobs-1985 --min-syl 1900`
   - Kết quả: **ĐẠT** (`âm tiết 1932, phút 8.9, cảnh 111, giây/cảnh 4.8, clip khác 2, ảnh khác 5, URL nguồn 32`), kèm 8 cảnh báo ảnh dọc `jobs84`, `mac84`, `sculley06` thiếu `focus`.

2. **Chạy render (`build_long.py mim-jobs-1985 render`):**
   - Lệnh: `python -X utf8 motion/long/build_long.py mim-jobs-1985 render`
   - Kết quả: **Bị chặn (exit code 1)** bởi hàm kiểm sàn (`floor`) trong `motion/long/build_long.py`:
     ```text
     ! WARNING engine đã đổi từ lần soát dấu cuối: python motion/long/diacritics_gallery.py render lab
     floor (mim-jobs-1985): video này kém các Long đã đăng, không dựng bản thật:
       kịch bản 1932 âm tiết (≈9 phút), sàn 5000 (≈23 phút)
       9 chương, sàn 10
       chỉ 10 loại cảnh, sàn 14 (photo, map, file, split, ledger, bars, sketch, broll…)
       dùng 6 ảnh tư liệu, sàn 40 — chạy research_long.py / media_search.py trước khi viết cảnh
       3 cảnh có b-roll, sàn 30
       28% cảnh là chữ trên nền trống (không ảnh, không b-roll), trần 12%
     ```
   - Do ticket và `AGENTS.md` quy định **không sửa `motion/long/build_long.py`, engine hay `data/long/**`**, bước `render`, `final` và trích `output/long/mim-jobs-1985/qa_final_sheet.jpg` từ `final.mp4` đang bị chặn bởi cổng `floor` trong `build_long.py`.

3. **Dựng và kiểm tra 2 Thumbnail (`t1`, `t2`):**
   - Tạo `motion/long/thumbs/mim-jobs-1985_t1.html` (chữ lớn `"1985 → 1997"` nối bằng mũi tên vòng, dòng nhỏ `"BỊ GẠT KHỎI APPLE"`, nền `ai01.jpg` người quay lưng, không mặt Jobs, không logo Apple).
   - Tạo `motion/long/thumbs/mim-jobs-1985_t2.html` (chữ lớn `"BỊ GẠT RA"`, dòng nhỏ `"RỒI QUAY LẠI"`, nền `ai01.jpg` người quay lưng).
   - Lệnh: `python -X utf8 motion/long/thumb.py mim-jobs-1985 t1 t2`
   - Kết quả: **Thành công (exit code 0)**. Đã soi trực tiếp `t1.jpg`, `t1_small.jpg`, `t2.jpg`, `t2_small.jpg`: ở cỡ 320 px (`t1_small.jpg`, `t2_small.jpg`), chữ rõ nét, đầy đủ dấu tiếng Việt, không tràn khung.

---

## 2. Thời lượng dự kiến của `final.mp4` (tổng 9 chương từ `timing.json` / `data.js`)

Khi mở khoá `floor` để xuất `final.mp4`, tổng thời lượng 9 chương là **534,38 giây** (**08:54,38**):

| Chương | Thời lượng (s) | Mốc tích luỹ trên `final.mp4` |
|---|---:|---|
| `ch00` | 45,10 s | `00:00,00 – 00:45,10` |
| `ch01` | 47,14 s | `00:45,10 – 01:32,24` |
| `ch02` | 46,50 s | `01:32,24 – 02:18,74` |
| `ch03` | 52,26 s | `02:18,74 – 03:11,00` |
| `ch04` | 88,82 s | `03:11,00 – 04:39,82` |
| `ch05` | 72,18 s | `04:39,82 – 05:52,00` |
| `ch06` | 86,34 s | `05:52,00 – 07:18,34` |
| `ch07` | 58,02 s | `07:18,34 – 08:16,36` |
| `ch08` | 38,02 s | `08:16,36 – 08:54,38` |
| **Tổng** | **534,38 s** | **08:54,38** |

---

## 3. Danh sách lỗi phát hiện theo mốc thời gian (soát trên `ch00..ch08/data.js`, `img/*` và `qa_clips.jpg`)

### A. Lỗi ảnh dọc bị cắt mặt người / chủ thể do thiếu `focus`
- **`00:00,00 – 00:05,52` (`ch00`, `chapter`, nền `jobs84` 1630×2400):** Ảnh dọc Steve Jobs đứng sau Macintosh không có `focus` (mặt ở vùng `y ≈ 0.08–0.28`), khung 16:9 lấy giữa ảnh sẽ cắt mất mặt Jobs.
- **`00:05,52 – 00:10,89`, `00:20,08 – 00:24,36`, `00:36,21 – 00:39,08` (`ch00`, `timeline`, nền `jobs84`):** Tương tự, nền `jobs84` bị cắt vùng mặt.
- **`00:45,10 – 00:50,22` (`ch01`, `chapter`, nền `mac84` 1800×2400) & `00:54,06 – 00:59,74` (`ch01`, `photo` `mac84`):** Ảnh dọc máy Macintosh 128K không có `focus`; ngoài ra trên góc trái dưới mặt trước vỏ máy có logo quả táo cầu vồng nhỏ của máy nguyên bản trong bảo tàng.
- **`01:08,83 – 01:13,02` (`ch01`, `photo` `sculley06` 960×1280):** Ảnh dọc chân dung John Sculley không có `focus` (`[0.5, 0.2]`), lấy giữa ảnh khiến phần trán/đỉnh đầu dễ bị cắt và phần ngực dưới lộ thẻ đeo tên có chữ tiếng Anh (`"John Sculley / Partner / Sculley Brothers, LLC / New York NY"`).
- **`01:32,24 – 01:37,33` (`ch02`, `chapter`, nền `sculley06`) & `01:37,33 – 01:41,50` (`ch02`, `photo` `sculley06`):** Ảnh dọc `sculley06` không có `focus`, cắt mặt/lộ thẻ tên.
- **`01:48,56 – 01:51,84` & `02:07,04 – 02:11,43` (`ch02`, `timeline`, nền `sculley06`):** Nền `sculley06` thiếu `focus`.
- **`02:18,74 – 02:25,07` (`ch03`, `chapter`, nền `jobs84`) & `02:39,27 – 02:46,24`, `02:50,19 – 02:56,54`, `03:04,18 – 03:07,22` (`ch03`, `timeline`, nền `jobs84`):** Ảnh dọc `jobs84` thiếu `focus`, cắt mất mặt.
- **`08:16,36 – 08:20,01` (`ch08`, `chapter`, nền `mac84`) & `08:31,91 – 08:35,21` (`ch08`, `timeline`, nền `mac84`):** Ảnh dọc `mac84` thiếu `focus`.

### B. Lỗi ảnh AI không xuất hiện trong cảnh (bị ghi đè trong `gen_scenes.py`)
- **`02:50,19 – 02:56,54` (`ch03`, câu 6):** Trong `data/long/mim-jobs-1985/gen_scenes.py`, khoá `(3, 6)` được gán `photo("ai01", x, z)` ở dòng 45 nhưng bị ghi đè bởi `(3, 6): tl(...)` ở dòng 55. Mảng `AI = ["ai01", ..., "ai06"]` ở dòng 13 không được gọi trong `scenes()`, dẫn tới **cả 6 ảnh AI (`ai01`–`ai06`) không xuất hiện ở bất kỳ cảnh nào** trong `ch00`–`ch08`.

### C. Lỗi chữ không dấu, sai đơn vị biểu đồ và cắt cụt 5 chữ đầu câu trên màn hình
- **`02:50,19 – 02:56,54` (`ch03`, `timeline`):** Chữ không dấu `"JOBS NHO LAI VIEC ROI APPLE"`.
- **`03:17,06 – 03:23,00` (`ch04`, `timeline`):** Chữ không dấu `"APPLE KHOI KIEN NEXT"`, `"TRUOC XET XU"`, `"VU KIEN DUOC RUT"`.
- **`03:23,00 – 03:30,80` (`ch04`, `counter`):** Nhãn không dấu `"GIA NEXT COMPUTER · USD"`.
- **`03:50,65 – 03:55,65` (`ch04`, `counter`) & `03:55,65 – 04:01,40` (`ch04`, `bars`):** Chữ không dấu `"DAU TU PIXAR · TRIEU USD"`, `"VON PIXAR"`, `"VON MOI"`.
- **`04:06,08 – 04:12,99` (`ch04`, `timeline`):** Chữ không dấu `"PHIM RA RAP"`, `"CHAO BAN CO PHIEU"`.
- **`04:44,46 – 04:52,54` (`ch05`, `bars`):** Tiêu đề và nhãn không dấu `"NHAN SU NAM 1993"`, `"CAT GIAM"` (230), `"CON LAI"` (300), đồng thời **sai đơn vị trục** `"unit": "TRIỆU USD"` (đang biểu diễn số nhân viên nhưng gắn đơn vị triệu USD).
- **`05:58,41 – 06:05,04` (`ch06`, `timeline`):** Chữ không dấu `"SO SANH BEOS / NEXTSTEP"`.
- **`06:08,30 – 06:14,62` (`ch06`, `counter`):** Chữ không dấu `"THUONG VU NEXT · TRIEU USD"`.
- **`06:31,36 – 06:39,52` (`ch06`, `bars`):** Chữ không dấu `"DOANH THU NAM TAI CHINH"`.
- **`07:27,29 – 07:34,06` (`ch07`, `timeline`):** Chữ không dấu `"CEO TAM QUYEN"`.
- **`07:44,82 – 07:51,17` (`ch07`, `timeline`):** Chữ không dấu `"APPLE MUA NEXT"`, `"JOBS TRO LAI"`.
- **Xuyên suốt `00:00 – 08:54` (các cảnh sinh tự động từ `z = " ".join(L[i].split()[:5]).upper()`):** Chữ trên `slam`, `kinetic`, `timeline`, `org` bị cắt đúng 5 từ đầu câu tạo thành cụm từ lửng nghĩa (ví dụ `00:10,89` `"HỘI ĐỒNG QUẢN TRỊ LÀ"`, `00:24,36` `"NGHỊCH LÝ BẮT ĐẦU TỪ"`, `01:16,14` `"ĐÓ LÀ HỘI ĐỒNG, CƠ"`, `02:29,30` `"NGÀY 1 THÁNG 6, SAN"`, `05:11,79` `"NÓ NẰM Ở VIỆC PHẦN"`, `08:43,00` `"CHUYỆN NGƯỜI SÁNG LẬP BỊ"`), và mọi cảnh `org` có 2 nút `a`, `b` lặp y hệt một chuỗi chữ.

### D. Clip B-roll (`qa_clips.jpg`)
- Đã kiểm `output/long/mim-jobs-1985/qa_clips.jpg` (2 clip `854027` và `8888818`): cảnh bàn máy tính CRT cũ và cảnh gõ bàn phím cận cảnh không lộ logo hay chữ thương hiệu đọc được.

---

## 4. Khẳng định không kiểm được

- Ticket chỉ giao bước render, khung soát và thumbnail (không viết mới `factcheck.md`); không phát sinh khẳng định mới ngoài kịch bản đã duyệt.

---

## 5. Đường dẫn file kết quả

- **Clip sheet hiện có:** `output/long/mim-jobs-1985/qa_clips.jpg`
- **Final QA sheet (`qa_final_sheet.jpg`):** Chưa thể tạo vì `output/long/mim-jobs-1985/final.mp4` đang chờ mở cổng `floor` trong `motion/long/build_long.py`.
- **Thumbnail HTML:**
  - `motion/long/thumbs/mim-jobs-1985_t1.html`
  - `motion/long/thumbs/mim-jobs-1985_t2.html`
- **Thumbnail đã render (1920×1080 và bản 320 px):**
  - `output/long/mim-jobs-1985/t1.jpg` (`output/long/mim-jobs-1985/t1_small.jpg`)
  - `output/long/mim-jobs-1985/t2.jpg` (`output/long/mim-jobs-1985/t2_small.jpg`)
