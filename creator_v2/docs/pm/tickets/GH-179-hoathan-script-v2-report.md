# GH-179 — Báo cáo kịch bản vòng 2 (Hòa Thân)

Ngày: 06/11/2026. Viết lại lời đọc `data/long/hoa-than/script.md`. Cập nhật ghi chú khớp giọng mới trong `data/long/hoa-than/factcheck.md`. Không commit, không TTS, không render, không đăng, không đổi lịch.

Dàn giữ nguyên 14 chương (CH00–CH13), cùng tiêu đề với `visual_plan.md` và các mốc của `plan.md`: mở 22/2/1799, lộ trình Nghịch lý, ba câu hỏi (bản kê, ba năm chờ, gã hề), bản án tháng 2/1799, ngôi nhà đổi chủ. Số, ngày và bốn câu trích giữ nguyên. Lời không còn ghi chú sản xuất, không đọc thẻ chương, không nêu tên trang bách khoa.

## Số âm tiết

Đếm bằng `script_lines.parse` rồi `split()` trên lời sẽ đọc (cùng bộ đếm của `motion/long/script_lines.py`). Không chạy lệnh ghi `chNN.json`.

**Tổng: 5.688 âm tiết, 578 câu, 14 chương.** Nằm trong sàn 5.500–7.000. Ước khoảng 28 phút ở 200 âm tiết/phút.

| Chương | Câu | Âm tiết |
|---|---:|---:|
| CH00 Nhà riêng, 22/2/1799 | 25 | 231 |
| CH01 Nghịch lý | 41 | 376 |
| CH02 Thị vệ cửa cung | 42 | 425 |
| CH03 Hai mươi bảy tuổi | 43 | 388 |
| CH04 Đồng liêu | 50 | 510 |
| CH05 Công chúa Hòa Hiếu | 36 | 386 |
| CH06 Sứ đoàn năm 1793 | 40 | 388 |
| CH07 Hoàng đế trên danh | 44 | 413 |
| CH08 Năm ngày | 51 | 460 |
| CH09 Bản kê | 44 | 471 |
| CH10 Hai mươi tội | 46 | 472 |
| CH11 Gã hề trên màn hình | 38 | 383 |
| CH12 Nhà đổi chủ | 41 | 394 |
| CH13 Phía bắc Thập Sát Hải | 37 | 391 |

## factcheck_lint

```
python motion/long/factcheck_lint.py hoa-than
hoa-than: 0 lỗi (factcheck)
```

## script_lines.gate

Gọi `gate(parse(script.md))`. Kết quả: **0 lỗi**. Không chạy `python motion/long/script_lines.py hoa-than` vì lệnh ấy ghi `chNN.json`, ngoài phạm vi.

## Tự kiểm giọng

Lệnh trong brief:

```
python -c "import re,io;t=io.open('data/long/hoa-than/script.md',encoding='utf-8').read();L=[l for l in t.splitlines() if l.strip() and not l.startswith(('|','#','-','>','*'))];bad=[l for l in L if re.search(r'(?i)wikipedia|bách khoa|bài tiếng (việt|anh)|kịch bản|plan|lời đọc|trên hình|mô-típ|infobox|cùng trang|video này|chương (một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)',l)];print(len(bad));print('\n'.join(bad[:40]))"
```

Kết quả:

```
0
```

Tên nguồn còn trong lời, mỗi chương khoảng một lần, khi tên ấy là một phần của chuyện: Thanh sử cảo (CH00, CH02, CH04, CH07, CH10, CH11), sứ đoàn Macartney (CH06), Harris 2018 (CH08), Britannica và Wook Yoon (CH09), Daniel McMahon 2008 (CH10). CH09 và CH10 có hai tên vì chương ấy đặt các bản chép cạnh nhau: sách tra cứu với sử gia, rồi chỉ dụ với sử gia hỏi lại chân dung. Cách chia 20 tội ở CH10 nói "khảo cứu năm 2012", không nhắc lại họ Yoon.

## Mười câu trước và sau

1. Trước: "Kịch bản này không kể danh sách thiếp. Bài tiếng Việt có một danh sách dài. Plan đã cấm đưa vào lời."
   Sau: câu ấy bỏ. Chương công chúa chỉ giữ người có ngày: "Năm 1790, con trai ông cưới con gái thứ 10 của Càn Long."

2. Trước: "Cảnh ấy ta không dựng. Không pháp trường. Không dây. Không máu trên lời đọc."
   Sau: "Gia Khánh không cho đem ông ra giữa chợ." rồi "» Ban cho tự vẫn."

3. Trước: "Không có pháp trường trong lời đọc này. Không có dải lụa trên hình."
   Sau: "Một án lăng trì đã được đổi thành bốn chữ, ban cho tự vẫn."

4. Trước: "Mô-típ một dòng bản kê chạy suốt mười hai lần."
   Sau: "Bản kê không thành một tổng." Dòng bản kê vẫn là việc của hình, theo `visual_plan.md`.

5. Trước: "Ngay các bách khoa đang kể cũng không thống nhất kho ấy lớn cỡ nào. Video này đi tìm bản kê."
   Sau: "Các con số được chép lại chênh nhau đến kinh ngạc. Có nơi ghi 1,1 tỷ lạng bạc. Có nơi chỉ ghi chừng 60 triệu."

6. Trước: "Chương một. Nghịch lý."
   Sau: "Bạn hãy đặt hai con số lên cùng một mặt bàn." Thẻ chương để hình đọc.

7. Trước: "Vòng thứ nhất đóng ở chương chín, khi các số nằm cạnh nhau."
   Sau: "Hồ sơ đang mở không đưa ra một tổng."

8. Trước: "Sợi chỉ này sẽ quay lại ở chương tám."
   Sau: "Người sẽ đổi án, về sau, không phải một quan tòa đứng ngoài. Đó là anh trai của công chúa."

9. Trước: "Bài tiếng Việt nén cả đoạn thăng chức vào một năm sau 1772. Lời đọc theo mốc tiếng Anh."
   Sau: "Có bản gom cả quãng thăng chức vào một năm sau 1772. Bản có ngày thì dài hơn."

10. Trước: "Cold open đã không nêu tên. Chương này cũng không chốt."
    Sau: "Có bản ghi Phúc Trường An, bị quản thúc tại gia, không bị xử tử. Có bản ghi Thượng thư Tô Lăng A. Hai tên chưa chịu vào cùng một chỗ."

## Tiêu đề đề xuất

Mỗi dữ kiện trong tiêu đề có một câu trong lời đọc. Chưa đưa lụa vàng hay một tổng tài sản lên tiêu đề: hai chỗ ấy vẫn đang lệch giữa các bản.

1. `KỶ HIỂU LAM Ngoài Đời Thật: Hòa Thân` (36 ký tự)
   - Kỷ Hiểu Lam: "Nhiều người Việt có thể đã xem Kỷ Hiểu Lam."
   - Hòa Thân: "Người trong nhà là Hòa Thân."
   - Rủi ro đã ghi trong plan: người xem có thể tưởng phim kể về Kỷ Vân. Lời có câu chặn: "Kỷ Hiểu Lam không phải phim kể đời Hòa Thân."

2. `HÒA THÂN Ngoài Đời Thật: Bản Kê Năm 1799` (40 ký tự)
   - Hòa Thân: "Người trong nhà là Hòa Thân."
   - Bản kê: "Hãy trải các con số ra, và đừng vội cộng."
   - Năm 1799: "Ngày 22 tháng 2 năm 1799, tại một nhà riêng ở Bắc Kinh."

3. `HÒA THÂN Ngoài Đời Thật: Kho Vàng Không Khớp` (44 ký tự)
   - Kho vàng: "Người ta kể một kho vàng bằng nhiều năm ngân sách."
   - Không khớp: "Các con số được chép lại chênh nhau đến kinh ngạc."
   - Câu dẫn thêm, không chọn tổng: "Có nơi ghi 1,1 tỷ lạng bạc. Có nơi chỉ ghi chừng 60 triệu."
