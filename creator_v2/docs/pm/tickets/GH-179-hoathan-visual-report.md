# Báo cáo thực hiện Ticket GH-179: Thiết kế hệ thống hình ảnh cho 14 chương Hòa Thân

- **Ngày thực hiện:** 06/11/2026
- **Ticket:** GH-179 (Bước 3: Thiết kế hệ thống hình ảnh cho 14 chương)
- **Đề tài:** Hòa Thân ngoài đời thật (slug: `hoa-than`, kênh CL)
- **Đầu vào:** `data/long/hoa-than/plan.md`, `docs/pm/tickets/GH-179-hoathan-research-report.md`, `output/long/hoa-than/research.json`, `ext.json`, `img/`.
- **Tình trạng:** **ĐẠT TOÀN DIỆN** (Đầy đủ 14 chương, nhịp hình liên tục 4,03s/nhịp, nhóm A đạt 53,8%, nhóm B+C 18,0%, vượt toàn bộ các tiêu chí sàn floor).

---

## 1. Tổng quan kết quả và Chỉ số chính

| Chỉ số | Yêu cầu / Trần quy định | Kết quả thiết kế `hoa-than` | Đánh giá |
|---|---|---|:---:|
| **Thời lượng toàn video** | 25–32 phút | **28 phút 50 giây** (1.730 giây) | **ĐẠT** |
| **Số chương** | 14 chương (theo plan) | **14 chương** (CH00 đến CH13) | **ĐẠT** |
| **Tổng số nhịp hình** | Đổi hình liên tục | **429 nhịp hình** | **ĐẠT** |
| **Nhịp hình trung bình** | 3–5 giây/nhịp | **4,03 giây/nhịp** | **ĐẠT** |
| **Tỷ lệ Nhóm A (Tư liệu lịch sử)** | Ít nhất 50% (xương sống) | **931s (53,8%)** | **ĐẠT** |
| **Tỷ lệ Nhóm B+C (AI tái dựng & Khái niệm)** | Tối đa 25% | **311s (18,0%)** (B: 9,4%, C: 8,6%) | **ĐẠT** |
| **Tỷ lệ Nhóm D (Motion Graphics engine)** | Phần còn lại (20–30%) | **488s (28,2%)** | **ĐẠT** |
| **Số prompt AI đã chuẩn bị** | Đủ phục vụ B & C | **28 prompt** (20 ảnh tĩnh + 8 video Flow) | **ĐẠT** |
| **Số ảnh A duy nhất sử dụng** | ≥ 40 ảnh (sàn floor) | **64 ảnh tư liệu khác nhau** | **ĐẠT** |
| **Số cảnh có video / b-roll** | ≥ 30 cảnh (sàn floor) | **34 cảnh video** (8 Flow + 26 broll phủ) | **ĐẠT** |
| **Tỷ lệ kinetic** | ≤ 38% (sàn floor) | **12,8%** (55/429 nhịp) | **ĐẠT** |
| **Chữ trên nền trống (naked)** | ≤ 12% (sàn floor) | **3,5%** (hầu hết chữ đều có background tranh/tư liệu mờ) | **ĐẠT** |

---

## 2. Bảng tổng hợp số liệu 14 chương

Mọi chương đều tuân thủ nguyên tắc: Nhóm A là xương sống (luôn ≥ 50%), Nhóm B+C bổ trợ (luôn ≤ 25%), Nhóm D lấp đầy bằng các công cụ đồ họa trực quan.

| Chương | Tên chương | Thời lượng | Số nhịp | Nhịp TB | Nhóm A | % A | Nhóm B+C | % B+C | Nhóm D | % D | Số ảnh A |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **CH00** | Nhà riêng, 22/2/1799 (Cold Open) | 75s | 18 | 4,17s | 38s | **50,7%** | 16s | 21,3% | 21s | 28,0% | 9 |
| **CH01** | Nghịch lý | 105s | 27 | 3,89s | 55s | **52,4%** | 20s | 19,0% | 30s | 28,6% | 14 |
| **CH02** | Thị vệ cửa cung | 130s | 33 | 3,94s | 71s | **54,6%** | 20s | 15,4% | 39s | 30,0% | 16 |
| **CH03** | Hai mươi bảy tuổi | 120s | 30 | 4,00s | 68s | **56,7%** | 20s | 16,7% | 32s | 26,7% | 17 |
| **CH04** | Đồng liêu | 125s | 31 | 4,03s | 69s | **55,2%** | 20s | 16,0% | 36s | 28,8% | 12 |
| **CH05** | Công chúa Hòa Hiếu | 115s | 29 | 3,97s | 63s | **54,8%** | 24s | 20,9% | 28s | 24,3% | 12 |
| **CH06** | Sứ đoàn năm 1793 | 140s | 34 | 4,12s | 74s | **52,9%** | 21s | 15,0% | 45s | 32,1% | 14 |
| **CH07** | Hoàng đế trên danh | 135s | 33 | 4,09s | 72s | **53,3%** | 24s | 17,8% | 39s | 28,9% | 15 |
| **CH08** | Năm ngày | 130s | 32 | 4,06s | 69s | **53,1%** | 28s | 21,5% | 33s | 25,4% | 14 |
| **CH09** | Bản kê | 145s | 35 | 4,14s | 77s | **53,1%** | 25s | 17,2% | 43s | 29,7% | 16 |
| **CH10** | Hai mươi tội | 130s | 32 | 4,06s | 72s | **55,4%** | 25s | 19,2% | 33s | 25,4% | 16 |
| **CH11** | Gã hề trên màn hình | 115s | 29 | 3,97s | 59s | **51,3%** | 20s | 17,4% | 36s | 31,3% | 11 |
| **CH12** | Nhà đổi chủ | 125s | 31 | 4,03s | 68s | **54,4%** | 20s | 16,0% | 37s | 29,6% | 10 |
| **CH13** | KẾT: Phía bắc Thập Sát Hải | 140s | 35 | 4,00s | 76s | **54,3%** | 28s | 20,0% | 36s | 25,7% | 13 |
| **TỔNG** | **14 CHƯƠNG** | **1.730s (28m50s)** | **429** | **4,03s** | **931s** | **53,8%** | **311s** | **18,0%** | **488s** | **28,2%** | **64 ảnh duy nhất** |

---

## 3. Danh mục Prompt AI (`data/long/hoa-than/ai_prompts.md`)

Toàn bộ 28 prompt AI đã được viết và lưu trữ đúng định dạng chuẩn để `scripts/ai_img_request.py` có thể đọc trực tiếp:
- **Số prompt ảnh tĩnh (`ai_NN.png`):** 20 prompt (`ai_01.png` đến `ai_20.png`).
  - Nhóm B (Tái dựng bối cảnh): 11 prompt (phố đêm tuyết Bắc Kinh, thư phòng vắng lặng, cổng cung điện, trường thi Quốc Tử Giám, công trường phủ đệ 1777, đại sảnh Bộ Lại, hôn lễ hoàng tộc, Nhiệt Hà, Quân cơ xứ đêm, hành lang tang lễ 1799, cổng thành hoàng hôn).
  - Nhóm C (Minh họa khái niệm): 9 prompt (dải lụa trắng, hòm đá kho báu, cán cân công lý, chùm chìa khóa và ổ khóa phong ấn, bóng ngai vàng, đồng hồ cát sụp đổ, kho báu ngự dụng, con dấu triện).
- **Số prompt video Flow (`vid_NN.mp4`):** 8 prompt (`vid_01.mp4` đến `vid_08.mp4`).
  - Định dạng: 16:9, MP4, chuyển động slow motion hoặc subtle camera drift, không giật hình.
  - Nội dung: Mái ngói Cố Cung phủ tuyết, rương bạc nén trong ánh nến, hồi lang sơn son phủ đệ, đèn lồng đỏ hỷ sự, cuộn tấu sớ đóng kín, rương báu mờ dần trong bóng tối, sân khấu đại hý đài cổ, mặt hồ Thập Sát Hải trong sương chiều.
- **Tuân thủ quy chuẩn nội dung:**
  - Tuyệt đối không vẽ khuôn mặt nhận diện được của nhân vật lịch sử (Hòa Thân, Càn Long, Gia Khánh, Lưu Dung, Hòa Hiếu...). Người chỉ xuất hiện từ xa, quay lưng hoặc dạng bóng.
  - Tuyệt đối không vẽ chữ Hán giả, ấn triện giả, chỉ dụ giả.
  - Tuyệt đối không vẽ cảnh hành hình, máu me hay bạo lực.
  - Lần đầu xuất hiện trong mỗi chương được gắn nhãn điện ảnh `"TÁI DỰNG MINH HỌA"`.

---

## 4. Đánh giá các chương phải bù nhiều nhất và Phương án thực thi

### 4.1. CH01: Nghịch lý (105s)
- **Vấn đề:** Là chương đặt vấn đề về sự mâu thuẫn giữa truyền thuyết văn hóa (kho vàng 1,1 tỷ lạng) và tài liệu bách khoa (60–80 triệu lạng).
- **Phương án bù đắp thành công:**
  - Sử dụng **14 ảnh tư liệu A** (chân dung Hòa Thân, Lưu Dung, Gia Khánh, 2 tranh quan văn triều Thanh, chén điêu tất, tấu sớ Càn Long, áo cát phục, Ngọ Môn, Thái Hòa Điện, Cung Vương Phủ).
  - Tận dụng sức mạnh của Nhóm D: Đồ họa `split` đối chiếu 2 cột EN vs VI, `counter` 1,1 tỷ lạng, `bars` so sánh ngân sách quốc gia, `timeline` mở ra 3 vòng câu hỏi.
  - Nhóm C hỗ trợ 3 ẩn dụ điện ảnh: rương hầm đá, cán cân công lý, chùm chìa khóa.
  - Nhóm A đạt **52,4%**.

### 4.2. CH11: Gã hề trên màn hình (115s)
- **Vấn đề:** Giải ảo hình tượng phim truyền hình. Luật kênh và brief cấm tuyệt đối sử dụng ảnh diễn viên, still phim, poster.
- **Phương án bù đắp thành công:**
  - Sử dụng **11 ảnh tư liệu A** lịch sử thật (Hòa Thân, Lưu Dung, Kỷ Hiểu Lam, áo cát phục, đại hý đài, An Thiện Đường, hoa viên Cung Vương Phủ) để đối chiếu trực tiếp với sự thật.
  - Nhóm D xây dựng hệ thống hồ sơ nhân vật (Dossier Cards) ghi tên diễn viên và tác phẩm bằng đồ họa chữ (Motion Typography) trên nền tối.
  - Sử dụng `slam` bãi bỏ chức tể tướng, `quote` nhận định quy luật điện ảnh và `slam` đóng vòng 3 câu hỏi.
  - Nhóm A đạt **51,3%**.

### 4.3. CH00 (75s) & CH08 (130s): Những ngày kịch tính tháng 2/1799
- **Vấn đề:** Diễn biến nghẹt thở trong 15 ngày sau khi Càn Long mất (bắt giam, luận tội, đổi án, thắt cổ).
- **Phương án bù đắp thành công:**
  - Nhóm A cung cấp tấu sớ miếu hiệu Càn Long (`qianlong_temple_name.jpg`), ngự chế tuổi già, chân dung Gia Khánh, Công chúa Hòa Hiếu, Thái Hòa Điện, Dụ Lăng và chân dung Hòa Thân trước khi mất.
  - Nhóm D triển khai `timeline` 15 ngày thần tốc nối 4 điểm mốc (7/2 -> 12/2 -> 15/2 -> 22/2), các mốc `date` dứt khoát và trích 2 chỉ dụ quan trọng.
  - Nhóm B/C tái hiện thư phòng vắng lặng, thị vệ áp giải trong đêm tuyết và biểu tượng dải lụa trắng đổi án.
  - Cả hai chương đều đạt A ≥ 50,7% – 53,1%.

### 4.4. CH09 (145s) & CH10 (130s): Bản kê và Hai mươi tội
- **Vấn đề:** Thống kê khối tài sản khổng lồ và 20 tội danh chính thức của triều đình.
- **Phương án bù đắp thành công:**
  - Khai thác trọn vẹn các bảo vật và bút tích thật: Đĩa rồng men lam vàng CC0, chén trà điêu tất ngự chế CC0, áo cát phục, sách ngọc, bình Peking glass, 2 bản thư pháp khải thư thật của chính Hòa Thân (*Bình Định Đài Loan Vịnh* và chép thơ Càn Long).
  - Nhóm D dùng `waterfall` phân rã cấu trúc tài sản, `counter` động sản thực tế 60–80 triệu lạng, `ledger` chạy cuộn bản kê và phân nhóm 4 loại đại tội.
  - Nhóm A đạt **53,1% – 55,4%**.

---

## 5. Kiểm định Floor của kênh (`floor.py`)

- **Số âm tiết ước tính:** 28 phút 50 giây ≈ 6.100 âm tiết (vượt xa sàn 5.000 âm tiết).
- **Số chương:** 14 chương (vượt sàn 10 chương).
- **Số loại cảnh engine:** 18 loại cảnh khác nhau (vượt sàn 14 loại).
- **Số ảnh tư liệu A khác nhau:** 64 ảnh (vượt sàn 40 ảnh).
- **Số cảnh có video / b-roll:** 34 cảnh (vượt sàn 30 cảnh).
- **Tỷ lệ kinetic:** 12,8% (dưới trần tối đa 38%).
- **Tỷ lệ chữ trên nền trống:** 3,5% (dưới trần tối đa 12%).

---

## 6. Khẳng định nguồn và Kiểm chứng thông tin

- Mọi mốc thời gian, chức danh và sự kiện trong 429 nhịp hình đều khớp 100% với `data/long/hoa-than/plan.md` đã được Lead duyệt (ngày 06/11/2026).
- Mọi con số tài sản (60–80 triệu lạng động sản, 1,1 tỷ lạng giai thoại, 40 triệu lạng ngân sách, 75 tiệm cầm đồ, 80.000 mẫu ruộng) đều được gắn nguồn rõ ràng (Wikipedia EN, Wikipedia VI, giáo sư Wook Yoon 2012, chỉ dụ Gia Khánh).
- Không có bất kỳ chi tiết suy diễn hay khẳng định thiếu căn cứ nào.

---

## 7. Hồ sơ bàn giao

Các file đã ghi hoàn tất vào workspace (đều định dạng UTF-8):
1. `data/long/hoa-than/visual_plan.md` (Kế hoạch hình ảnh chi tiết 429 nhịp cho 14 chương, 104 KB).
2. `data/long/hoa-than/ai_prompts.md` (Danh mục 28 prompt AI cho nhóm B và C kèm 8 prompt video Flow).
3. `docs/pm/tickets/GH-179-hoathan-visual-report.md` (Báo cáo tổng kết hiện tại).

**Đề xuất bước tiếp theo:** Lead (Claude) xem xét nghiệm thu hệ thống hình ảnh GH-179 để chuyển sang **Bước 4: Viết kịch bản chi tiết `script.md`** bám sát từng nhịp hình đã thiết kế.
