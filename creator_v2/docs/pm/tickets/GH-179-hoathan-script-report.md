# GH-179: Hòa Thân, bước 3 — báo cáo kịch bản

- **Ngày:** 06/11/2026
- **Ticket:** GH-179 (bước 3: `script.md` + `factcheck.md`)
- **Slug:** `hoa-than`
- **Phạm vi:** viết lời đọc và bảng đối chiếu. Không TTS, không render, không sửa code, không commit, không đăng, không đổi lịch.

**Tình trạng:** kịch bản 14 chương, 5.541 âm tiết (sàn brief 5.500–7.000), `factcheck_lint` 0 lỗi. Chờ Lead/chủ kênh duyệt trước TTS.

---

## 1. Số đo

Đo bằng `script_lines.parse` trên `data/long/hoa-than/script.md` (không ghi `chNN.json`, vì brief chỉ cho phép ba file).

| Chương | Câu | Âm tiết | ~phút (÷200) |
|---|---:|---:|---:|
| CH00 Nhà riêng, 22/2/1799 | 29 | 259 | 1,3 |
| CH01 Nghịch lý | 37 | 370 | 1,9 |
| CH02 Thị vệ cửa cung | 38 | 412 | 2,1 |
| CH03 Hai mươi bảy tuổi | 38 | 343 | 1,7 |
| CH04 Đồng liêu | 50 | 525 | 2,6 |
| CH05 Công chúa Hòa Hiếu | 35 | 376 | 1,9 |
| CH06 Sứ đoàn năm 1793 | 37 | 395 | 2,0 |
| CH07 Hoàng đế trên danh | 42 | 406 | 2,0 |
| CH08 Năm ngày | 46 | 423 | 2,1 |
| CH09 Bản kê | 39 | 459 | 2,3 |
| CH10 Hai mươi tội | 42 | 432 | 2,2 |
| CH11 Gã hề trên màn hình | 37 | 351 | 1,8 |
| CH12 Nhà đổi chủ | 38 | 368 | 1,8 |
| CH13 KẾT: Phía bắc Thập Sát Hải | 44 | 422 | 2,1 |
| **Tổng** | **552** | **5.541** | **≈27,7** |

- Chương: 14 (CH00–CH13).
- Câu ngắn ≤6 âm tiết: 118/552 = 21%.
- Câu >35 âm tiết: 0.
- `script_lines.gate`: OK (không `ROADMAP_CLICHE`, không câu lặp chặn).
- Lộ trình: dạng **Nghịch lý**. Không dùng "Hai hồ sơ". Không dùng "trả lời ba câu hỏi".
- Cold open: 22/2/1799, nhà riêng, dừng ở đỉnh (bản kê chưa cộng được).
- Ba vòng đóng đúng chỗ plan: bản kê (CH09), đợi 1796–1799 (CH08), gã hề (CH11).

Ở 212 âm tiết/phút (nhịp Khôi): ≈26,1 phút. Cộng nghỉ `‖` và thẻ chương: khoảng 27–29 phút. Nằm trong 25–32.

## 2. `factcheck_lint`

```
python motion/long/factcheck_lint.py hoa-than
hoa-than: 0 lỗi (factcheck)
```

Mã thoát 0.

## 3. File đã ghi

- `data/long/hoa-than/script.md`
- `data/long/hoa-than/factcheck.md`
- `docs/pm/tickets/GH-179-hoathan-script-report.md`

Không ghi `chNN.json`. Không chạy TTS/render.

## 4. Nguồn đã mở khi viết

- Wikipedia EN Heshen, Princess Hexiao, Jiaqing, Qianlong, Liu Yong, Ji Yun, Agui, Macartney Embassy, Prince Gong's Mansion, Prince Gong.
- Wikipedia VI Hòa Thân (đối chiếu chỗ lệch; không chép danh sách thiếp).
- 清史稿/卷319, zh.wikisource (toàn phần truyện Hòa Thân đã tải, gồm 20 tội rút và 賜自盡).
- Britannica Heshen.
- Harris 2018, *The Peking Gazette* (đoạn chỉ dụ 15/2 và "silk cord").
- Wook Yoon 2012, *T'oung Pao* 98.4–5 (đoạn ước tính tài sản, nhóm 20 tội, 2,8 triệu, tấu cuối 5/1799).
- McMahon 2008: **tóm tắt** trên trang Tsing Hua Journal; toàn văn PDF chưa mở.

Bốn câu TRÍCH DỊCH trong lời: 賜自盡; tội 1 (hai nhịp); tội 2. Mỗi câu có nguyên văn + bản Anh + URL trong `factcheck.md`.

## 5. Dữ kiện còn chưa chắc

Cần Lead biết trước khi duyệt TTS. Lời đọc đã nói mềm hoặc đặt cạnh; không khẳng định một phía.

| # | Dữ kiện | Vì sao chưa chắc | Cách lời đọc đang giữ |
|---|---|---|---|
| 1 | Tổng tài sản | VI 1,1 tỷ; EN ≥60 triệu / 60–80 triệu động sản / 100–800 triệu tranh cãi; Britannica ~60 triệu + 75 tiệm; Yoon 10–20 triệu thận trọng, một biên bản 2,8 triệu, trần 800 triệu | Đặt cạnh nhau. Không chọn một tổng |
| 2 | Lụa vàng | Wikipedia EN/VI: golden silk. Harris: silk cord. 清史稿: 賜自盡, không tả | Harris = nguồn thứ hai cho **dải lụa**. "Lụa vàng" gắn Wikipedia |
| 3 | Người bị bắt cùng | EN: Phúc Trường An, quản thúc. VI: Tô Lăng A | Không nêu tên |
| 4 | Năm Cam Túc | 清史稿 1781 (Càn Long 46). EN 1784 | Đặt hai năm cạnh nhau |
| 5 | Lưu Toàn | QS >20 vạn. EN 240.000 lạng | Nói hai số lệch |
| 6 | McMahon 2008 | Mới mở abstract + Wikipedia | "Theo Wikipedia, dẫn McMahon" |
| 7 | Số nhà 17 Tây Tiền Hải | VI có. Bài Prince Gong đã đọc không có. Bài Heshen EN có "17 Qianhai Road West" | Giữ "phía bắc Thập Sát Hải" theo plan |
| 8 | Hồi môn 300.000 lạng | Chỉ Wikipedia Princess Hexiao | "Theo Wikipedia" |
| 9 | Bốn thứ tiếng | Chỉ Wikipedia EN Heshen | "Theo Wikipedia" |
| 10 | 40 triệu / 120 triệu (ngân sách năm / mười đại chiến dịch) | Chỉ Wikipedia EN Heshen | Tỷ lệ, không cộng vào tài sản ông |
| 11 | Nơi chết | EN Zhizhai. VI Cung Vương Phủ | Nhà riêng; 1799 chưa mang tên Cung |

Đã bỏ (không có trong lời): danh sách thiếp VI; tin đồn Càn Long–Hòa Thân; câu "nếu con là hoàng tử"; nhật ký Macartney chưa mở; bài thơ tuyệt mệnh; 80.000 mẫu / 80 thuyền; Yamanaka 1912; ánh xạ chính trị hôm nay; cảnh hành hình.

## 6. Tiêu đề đề xuất

Khuôn: `[PHIM] Ngoài Đời Thật: [người] — [nghịch lý có số]`. Tối đa 100 ký tự. Phần gây tò mò trong 60 ký tự đầu. Mọi dữ kiện có câu dẫn trong lời.

### A — Lead đang nghiêng (80 ký tự)

**TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Hòa Thân Bị Ép Chết 15 Ngày Sau Khi Càn Long Mất**

60 ký tự đầu: `TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Hòa Thân Bị Ép Chết 15 Ngày`

| Dữ kiện | Câu dẫn |
|---|---|
| Tể tướng Lưu gù | CH00: "Có người nhớ Tể tướng Lưu gù, nơi ông là phản diện." CH04: "Phim Tể tướng Lưu gù cần hai người đánh nhau." |
| Hòa Thân | Cả kịch bản; CH00: "Thanh sử cảo gọi ông là Hòa Thân, tự Trí Trai." |
| Bị ép chết | CH00: "» Ban cho tự vẫn." CH08: "Ông ban cho tự vẫn." |
| 15 ngày | CH00: "Mười lăm ngày trước, Thái thượng hoàng Càn Long vừa mất." CH08: "Từ ngày Càn Long mất đến ngày ấy là mười lăm ngày." |
| Càn Long mất | CH00/CH08: mất ngày 7/2/1799; CH08: "Ngày 7 tháng 2 năm 1799, Càn Long mất tại Dưỡng Tâm Điện." |

### B (70 ký tự)

**KỶ HIỂU LAM Ngoài Đời Thật: Hòa Thân — Bản Kê Năm 1799 Không Cộng Được**

60 ký tự đầu: `KỶ HIỂU LAM Ngoài Đời Thật: Hòa Thân — Bản Kê Năm 1799 Không`

| Dữ kiện | Câu dẫn |
|---|---|
| Kỷ Hiểu Lam | CH00: "Nhiều người Việt có thể đã xem Kỷ Hiểu Lam." CH11: "Kỷ Hiểu Lam không phải phim tiểu sử Hòa Thân." |
| Hòa Thân | như trên |
| Bản kê 1799 | CH09 cả chương; CH00: "một bản kê chưa ai cộng ra cùng một số." |
| Không cộng được | CH09: "Đây là chỗ vòng thứ nhất đóng, bằng cách không chọn một số." CH13: "Không dòng nào được phép cộng thành một tổng." |

### C (78 ký tự)

**HÒA THÂN Ngoài Đời Thật: 15 Ngày Sau Càn Long Mất, Bản Kê Không Cộng Ra Một Số**

60 ký tự đầu: `HÒA THÂN Ngoài Đời Thật: 15 Ngày Sau Càn Long Mất, Bản Kê Kh`

Cùng các câu dẫn 15 ngày / Càn Long mất / bản kê như A và B. Thiếu mỏ neo tên phim so với A và B.

**Gợi ý:** A khớp khuôn thắng CL và đúng hướng Lead. Rủi ro: người xem tưởng video về Lưu Dung. B lấy mỏ neo Kỷ Hiểu Lam (plan mục 2). C đặt tên người trước, mất mỏ neo phim.

## 7. Việc không làm

Không đăng, không enqueue, không commit, không đổi lịch Bao Thanh Thiên (08/11/2026, 21:00, IVOqSZWHIYY), không TTS, không render, không sửa code.
