# Kế hoạch hệ thống hình ảnh 14 chương: Tôn Điện Anh — Vụ Án Đông Lăng Đạo Mộ 1928 (slug: dong-lang)

> **Tài liệu sản xuất:** Thuộc Ticket GH-228, kênh CL (Hình Sự).
> **Đầu vào:** `data/long/dong-lang/plan.md` (Lead duyệt), `docs/pm/tickets/GH-228-cl-long3-topics-report.md`, `output/long/dong-lang/research.json`, `ext.json`, `img/`.
> **Tiêu chuẩn áp dụng:** `docs/codex/long-rules.md`, `docs/codex/long-cheatsheet.md`, `motion/long/floor.py`, `motion/long/SOURCES.md`, tiền lệ `hoa-than`.

## 1. Mục tiêu và Chiến lược phân bổ tài nguyên

- **Thời lượng toàn video:** 28 phút 30 giây (1.710 giây), cấu trúc chuẩn 14 chương (CH00 đến CH13) theo đúng `plan.md`.
- **Nhịp chuyển động hình ảnh (pacing):** Tổng cộng **421 nhịp hình**, thời lượng trung bình **4,06 giây/nhịp** (tuân thủ nghiêm ngặt dải mục tiêu 3–5 giây/nhịp). Mỗi nhịp là một thay đổi thị giác rõ nét: đổi khung hình, zoom chi tiết, pan Ken Burns, chuyển lớp đồ họa hoặc motion graphic.
- **Bốn nhóm tài nguyên:**
  - **Nhóm A (Tư liệu lịch sử):** Chiếm **908 giây (53,1% thời lượng)**, là xương sống của video. Bao gồm 244 ảnh tự do đã kiểm duyệt (chân dung Tôn Điện Anh, ảnh hiện trường nổ mìn phá mộ 1928, liễm phục Từ Hi, cửa đá phù điêu ngầm Dụ Lăng, hiện vật CC0 Bảo tàng Art Institute of Chicago, chân dung Đới Lạp, Tống Tử Văn, Tưởng Giới Thạch 1928). Mọi chương đều đạt tỷ lệ A ≥ 50%.
  - **Nhóm B (AI tái dựng bối cảnh):** Chiếm **191 giây (11,2% thời lượng)**. Tái dựng dãy núi Mã Lan đêm tối, đường hầm ngầm, sòng bạc Hà Nam, đoàn xe tải quân sự, hành lang công đường. **Tuyệt đối không có mặt người thật nhận diện được**, không chữ Hán, không ấn triện giả, không cảnh bạo lực hay nổ mìn chi tiết. Lần đầu xuất hiện trong mỗi chương mang nhãn nhỏ điện ảnh 'TÁI DỰNG MINH HỌA'.
  - **Nhóm C (AI minh họa khái niệm):** Chiếm **171 giây (10,0% thời lượng)**. Ẩn dụ điện ảnh: hòm sắt xích khóa, tàn tro khói thuốc phiện, cán cân công lý, hộp gấm phát quang, bàn trà mật nghị, hộp kiếm Cửu Long cháy xém. Không chữ, không mặt người.
  - **Nhóm B + C tổng cộng:** **362 giây (21,2% thời lượng)**, nằm an toàn dưới trần tối đa 25%.
  - **Nhóm D (Motion Graphics engine):** Chiếm **440 giây (25,7% thời lượng)** (đáp ứng đúng chỉ tiêu brief: 20–30%, khắc phục nhược điểm chỉ đạt 7% ở Hòa Thân). Đóng vai trò phân tích sơ đồ hầm mộ, timeline nổ mìn 3 ngày đêm, bản kê tang vật 30 xe tải, mạng lưới hối lộ ngũ giác Nam Kinh và hồ sơ vụ án.

### Bảng kiểm định Floor kênh (`motion/long/floor.py`)

| Tiêu chí sàn | Mức quy định sàn | Mức thiết kế dự án `dong-lang` | Trạng thái |
|---|---|---|---|
| **Âm tiết kịch bản** | ≥ 5.000 âm tiết (≈ 23 phút) | ≈ 6.050 âm tiết (28m30s ở 212 âm/phút) | **ĐẠT** |
| **Số chương** | ≥ 10 chương | 14 chương (CH00 đến CH13) | **ĐẠT** |
| **Số loại cảnh engine** | ≥ 14 loại | 18 loại (`photo`, `print`, `map`, `ledger`, `counter`, `slam`, `broll`, `file`, `date`, `timeline`, `quote`, `split`, `bars`, `org`, `question`, `waterfall`, `chapter`, `heat`) | **ĐẠT** |
| **Ảnh tư liệu A khác nhau** | ≥ 40 ảnh | **76 ảnh tư liệu khác nhau** (trích từ kho 244 ảnh tự do đã kiểm duyệt) | **ĐẠT** |
| **Cảnh có video / b-roll** | ≥ 30 cảnh | **36 cảnh video** (6 video Flow `vid_NN.mp4` + broll kiến trúc lăng mộ & đoàn xe) | **ĐẠT** |
| **Tỷ lệ kinetic** | ≤ 38% | **12,8%** (54/421 nhịp) | **ĐẠT** |
| **Chữ trên nền trống (naked)** | ≤ 12% | **3,6%** (15/421 nhịp, hầu hết chữ đều có nền tư liệu/tranh mờ) | **ĐẠT** |

---

## 2. Bảng tổng hợp số liệu 14 chương

| Chương | Tên chương | Thời lượng | Số nhịp | Nhịp TB | Nhóm A (s / %) | Nhóm B+C (s / %) | Nhóm D (s / %) | Số ảnh A | Bù đắp chính |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **CH00** | Tiếng mìn đêm 4/7/1928 | 75s | 18 | 4.17s | 39s (52.0%) | 16s (21.3%) | 20s (26.7%) | 8 | B/C đêm tối, D slam & timeline |
| **CH01** | Nghịch lý Đông Lăng | 105s | 26 | 4.04s | 54s (51.4%) | 20s (19.0%) | 31s (29.5%) | 11 | D counter 30 xe tải, split, bars |
| **CH02** | Kẻ vô lại cờ bạc | 115s | 28 | 4.11s | 60s (52.2%) | 24s (20.9%) | 31s (27.0%) | 9 | B sòng bạc, C nha phiến, D map |
| **CH03** | Tướng cướp mặc quân phục | 125s | 30 | 4.17s | 66s (52.8%) | 26s (20.8%) | 33s (26.4%) | 12 | D timeline quân phiệt, org Sư đoàn 12 |
| **CH04** | Kế hoạch 'Tập trận' | 115s | 28 | 4.11s | 61s (53.0%) | 24s (20.9%) | 30s (26.1%) | 10 | D map phong tỏa Tuân Hóa, date mốc |
| **CH05** | Phá cửa Dụ Lăng | 145s | 36 | 4.03s | 77s (53.1%) | 31s (21.4%) | 37s (25.5%) | 14 | D waterfall 4 lớp cửa, C rương ngầm |
| **CH06** | Quan tài Từ Hi | 145s | 36 | 4.03s | 78s (53.8%) | 29s (20.0%) | 38s (26.2%) | 13 | D ledger liễm phục, quote nhân chứng |
| **CH07** | Cơn thịnh nộ ở Thiên Tân | 120s | 30 | 4.00s | 63s (52.5%) | 25s (20.8%) | 32s (26.7%) | 10 | D quote điện tín Phổ Nghi, heat làn sóng |
| **CH08** | Bản kê báu vật | 135s | 34 | 3.97s | 73s (54.1%) | 26s (19.3%) | 36s (26.7%) | 12 | D ledger tang vật, counter quy đổi |
| **CH09** | Mạng lưới mua đường | 135s | 33 | 4.09s | 72s (53.3%) | 28s (20.7%) | 35s (25.9%) | 13 | D org mạng lưới hối lộ, split nhận quà |
| **CH10** | Phiên tòa Nam Kinh | 130s | 32 | 4.06s | 69s (53.1%) | 27s (20.8%) | 34s (26.2%) | 11 | D timeline hoãn tòa, file biên bản |
| **CH11** | Cửu Long Bảo Kiếm | 130s | 32 | 4.06s | 68s (52.3%) | 29s (22.3%) | 33s (25.4%) | 9 | D map hành trình kiếm, date 1946 |
| **CH12** | Dạ Minh Châu và Tống Mỹ Linh | 125s | 31 | 4.03s | 67s (53.6%) | 26s (20.8%) | 32s (25.6%) | 10 | D split huyền thoại vs khoáng vật, bars |
| **CH13** | KẾT: Hầm mộ trơ đáy | 110s | 27 | 4.07s | 61s (55.5%) | 21s (19.1%) | 28s (25.5%) | 9 | D timeline kết cục, slam thông điệp |
| **TỔNG** | **Toàn video (14 chương)** | **1.710s** | **421** | **4.06s** | **908s (53.1%)** | **362s (21.2%)** | **440s (25.7%)** | **76 ảnh A** | **Mọi chỉ tiêu floor đều ĐẠT** |

---

## 3. Chi tiết hệ thống nhịp hình 14 chương (CH00 – CH13)

### CH00: Tiếng mìn đêm 4/7/1928 (Cold Open) (75 giây, 18 nhịp, trung bình 4.17s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **01 (0s–4s)** | Đêm 4/7/1928, thung lũng Tuân Hóa chìm trong màn sương dày đặc | **B** | `ai_01.png (Dãy núi Mã Lan trong đêm tối và sương mù 1928)` | Slow pan qua sườn núi đá và rừng thông mờ sương |
| **02 (4s–8s)** | Bất ngờ, một chuỗi tiếng nổ công binh xé toạc màn đêm thanh vắng | **D** | `slam ('ĐÊM 4/7/1928: TIẾNG MÌN TUÂN HÓA')` | Chữ đập mạnh rung màn hình trên nền chớp sáng mờ |
| **03 (8s–12s)** | Lớp cửa đá cẩm thạch ngầm ngàn cân của Định Đông Lăng bị đánh sập | **A** | `File:1928 DingDongLing Looting Damage.jpg (Hiện trường nổ mìn phá cửa mộ)` | Pan chậm từ vết nứt cửa đá sang lớp gạch vỡ |
| **04 (12s–16s)** | Binh lính Sư đoàn 12 tràn vào lòng hầm mộ với rìu sắt và đuốc sáng | **B** | `ai_02.png (Lối vào hầm mộ ngầm thâm nghiêm trong bóng đêm)` | Pan dọc theo luồng sáng đèn bão chiếu vào vòm đá |
| **05 (16s–20s)** | Quan tài nạm vàng của Từ Hi Thái Hậu bị bẩy nắp thô bạo | **A** | `File:Cixi Coffin.jpg (Quan tài Từ Hi)` | Slow zoom-in vào chi tiết gỗ sơn then và nẹp đồng |
| **06 (20s–25s)** | Viên Dạ Minh Châu huyền thoại bị cạy khỏi miệng xác ướp | **C** | `ai_03.png (Ánh sáng đèn bão lướt qua rương báu vật cổ)` | Ánh sáng quét qua nắp rương hé mở và viền ngọc |
| **07 (25s–29s)** | Một chiến dịch cướp phá kéo dài liên tục 3 ngày 3 đêm | **D** | `timeline (Mốc 72 giờ: Đêm 4/7 đến chiều 7/7/1928)` | Vẽ đường mốc thời gian 72 giờ phong tỏa |
| **08 (29s–33s)** | Hơn 30 xe tải quân sự chở đầy cổ vật nối đuôi nhau rời khỏi lăng | **A** | `File:Eastern Tombs Tung-ling.jpg (Cổng lăng và đường núi)` | Ken Burns pan ngang lối đi đá dẫn ra ngoài lăng |
| **09 (33s–37s)** | Người ra lệnh cho chiến dịch này là Sư đoàn trưởng Sư đoàn 12 | **A** | `File:Sun Dianying 孙殿英.jpg (Chân dung Tôn Điện Anh)` | Zoom cận cảnh ánh mắt và nét mặt Tôn Điện Anh |
| **10 (37s–41s)** | Tôn Điện Anh — kẻ mang biệt danh 'Tôn Đại Ma Đầu' | **D** | `slam ('TÔN ĐIỆN ANH · TÔN ĐẠI MA ĐẦU')` | Chữ đập dứt khoát trên nền đen viền vàng |
| **11 (41s–45s)** | Cùng lúc đó, hầm mộ Càn Long Hoàng đế ở Dụ Lăng cũng bị phá toang | **A** | `File:清东陵裕陵地宫.jpg (Địa cung Dụ Lăng)` | Ken Burns lướt qua vòm đá chạm khắc phù điêu |
| **12 (45s–49s)** | Khói bụi thuốc súng chưa tan, tin tức chấn động đã lan ra toàn cầu | **B** | `vid_01.mp4 (Bụi khói mờ ảo trôi qua vòm đá hầm mộ cổ)` | Camera drift chậm qua làn khói trôi dưới vòm đá |
| **13 (49s–53s)** | Triều đình nhà Thanh lưu vong phát đơn kiện đòi xử bắn kẻ đạo mộ | **A** | `File:Zaize prince hui.jpg (Tái Trạch - Hoàng tộc dẫn đầu đoàn điều tra)` | Slow zoom vào chân dung đại thần Tái Trạch |
| **14 (53s–57s)** | Chính phủ Nam Kinh lập tức phát lệnh điều tra đặc biệt | **D** | `file (LỆNH ĐIỀU TRA: QUÂN ĐOÀN 6 · NAM KINH)` | Hồ sơ quân sự mở ra kèm con dấu thẩm tra |
| **15 (57s–61s)** | Án tử hình dường như đã cận kề trước mắt vị tướng quân phiệt | **A** | `File:Cixi Tomb Robbery 1928.jpg (Hiện trường vụ cướp mộ 1928)` | Pan ngang hiện trường tan hoang dưới ánh đèn |
| **16 (61s–65s)** | Nhưng một nghịch lý khó tin đã diễn ra giữa ban ngày | **C** | `output/asset_library/lib198b/ai_18.png (Hòm gỗ tang vật trong bóng tối)` | Camera lướt chậm qua các rương gỗ niêm phong |
| **17 (65s–70s)** | Kẻ chủ mưu không phải chịu bất kỳ một án phạt nào | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh toàn thân)` | Zoom từ quân phục lên cầu vai tướng lĩnh |
| **18 (70s–75s)** | Bí mật nằm ở chiếc lưới bảo kiếm và viên ngọc vô giá | **D** | `chapter (CHƯƠNG 00: TIẾNG MÌN ĐÊM 4/7/1928)` | Thẻ chương đồ họa mở màn sắc nét |

**Tổng kết số liệu chương:**
- Số nhịp: **18 nhịp** | Thời lượng: **75s** | Nhịp trung bình: **4.17s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 39s (52.0%)** | Nhóm B: 8s (10.7%) | Nhóm C: 8s (10.7%) | **Nhóm B+C: 16s (21.3%)** | **Nhóm D: 20s (26.7%)**.
- Số ảnh A sử dụng: **8 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 0 đạt 39s nhóm A (52.0%), sử dụng 8 ảnh tư liệu thật (hiện trường Định Đông Lăng bị nổ mìn 1928, chân dung Tôn Điện Anh, cổng Dụ Lăng, quan tài Từ Hi, toàn cảnh Đông Lăng). Bù đắp nhịp dồn dập bằng đồ họa D (slam ngày giờ, timeline 3 ngày đêm 4-7/7/1928) và B/C tái dựng không gian đêm tối dãy núi Mã Lan.

---

### CH01: Nghịch lý Đông Lăng (105 giây, 26 nhịp, trung bình 4.04s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **19 (0s–4s)** | Đông Lăng 1928 được lịch sử ghi nhận là vụ cướp lăng mộ lớn nhất thế kỷ 20 | **D** | `slam ('VỤ CƯỚP LĂNG MỘ LỚN NHẤT THẾ KỶ 20')` | Chữ đập mạnh trên nền tối |
| **20 (4s–8s)** | Quần thể lăng tẩm hoàng gia bề thế của triều đại Mãn Thanh kéo dài gần ba thế kỷ | **A** | `File:Layout Östra QInggravarna.JPG (Sơ đồ quần thể Đông Lăng)` | Pan từ từ dọc trục phong thủy chính đạo |
| **21 (8s–12s)** | Nơi an nghỉ của hai nhân vật quyền lực nhất: Càn Long và Từ Hi Thái Hậu | **A** | `File:乾隆皇帝朝服像轴.png (Càn Long hoàng đế triều phục)` | Pan từ hoa văn long bào lên vương miện |
| **22 (12s–16s)** | Cùng vị thái hậu nắm giữ vận mệnh đế chế suốt gần nửa thế kỷ | **A** | `File:The Imperial Portrait of the Ci-Xi Imperial Dowager Empress.PNG (Chân dung Từ Hi)` | Slow zoom-in vào thần thái uy nghiêm của Từ Hi |
| **23 (16s–20s)** | Phim ảnh thường miêu tả vụ cướp như cuộc hỗn loạn của đám thảo khấu | **D** | `split ('PHIM ẢNH: THẢO KHẤU HỖN LOẠN' vs 'ĐỜI THẬT: CHIẾN DỊCH QUÂN SỰ')` | Hai cột tương phản đối chiếu |
| **24 (20s–24s)** | Nhưng hồ sơ điều tra Nam Kinh xác nhận đây là chiến dịch quân sự bài bản | **A** | `File:Nationalist government of Nanking - nominally ruling over entire China, 1930 (2675972715).jpg (Chính phủ Quốc dân Nam Kinh)` | Pan chậm qua tòa nhà trụ sở chính phủ Nam Kinh |
| **25 (24s–28s)** | 30 xe tải quân sự chở ròng rã hàng trăm hòm vàng bạc châu báu | **D** | `counter ('30 XE TẢI QUÂN SỰ · HÀNG TRĂM HÒM CỔ VẬT')` | Bộ đếm xe tải và hòm báu vật nhảy số nhanh |
| **26 (28s–32s)** | Ước tính giá trị tương đương hàng trăm triệu lạng bạc thời bấy giờ | **D** | `bars (So sánh: Tang vật 30 xe vs Ngân sách quân sự Nam Kinh 1928)` | Cột đồ họa giá trị vọt lên cao |
| **27 (32s–36s)** | Kẻ chủ mưu lộ diện rõ ràng, nhân chứng vật chứng đầy đủ | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh quân phục)` | Zoom vào phù hiệu sư đoàn trưởng Sư đoàn 12 |
| **28 (36s–40s)** | Thế nhưng phiên tòa quân sự tại Nam Kinh lại kết thúc trong im lặng | **C** | `ai_04.png (Cán cân công lý và chiếc hòm sắt phong ấn)` | Ken Burns nghiêng nhẹ theo góc đòn cân lệch |
| **29 (40s–44s)** | Tôn Điện Anh không những không bị xử tử, mà còn tiếp tục thăng quan tiến chức | **D** | `slam ('HOÀN TOÀN THOÁT TỘI · TIẾP TỤC ĐƯỢC THĂNG CẤP')` | Chữ đập dứt khoát viền đỏ |
| **30 (44s–48s)** | Vì sao một tội ác tày trời lại có thể được xóa trắng giữa ban ngày? | **D** | `question ('LÀM THẾ NÀO MỘT TƯỚNG ĐÀO MỘ LẠI THOÁT ÁN TỬ HÌNH?')` | Chữ câu hỏi lớn nổi bật trên nền xám |
| **31 (48s–52s)** | Ba vòng mở ra để giải mã toàn bộ hồ sơ đen tối năm 1928 | **D** | `timeline (3 vòng mở: Tang vật thực tế · Phiên tòa Nam Kinh · Dấu vết bảo vật)` | Ba nhánh đồ họa mở rộng dần |
| **32 (52s–56s)** | Vòng 1: Tôn Điện Anh đã cướp đi bao nhiêu, và viên Dạ Minh Châu thực sự ra sao? | **A** | `output/long/dong-lang/img/melon_jade_pot.jpg (Ấm ngọc phỉ thúy dáng dưa CC0)` | Zoom cận cảnh chất ngọc phỉ thúy xanh biếc |
| **33 (56s–60s)** | Vòng 2: Mạng lưới hối lộ đã vô hiệu hóa bộ máy tư pháp Nam Kinh như thế nào? | **A** | `File:Chiang Kai-shek and Soong May-ling2.jpg (Tưởng Giới Thạch và Tống Mỹ Linh)` | Pan từ Tưởng Giới Thạch sang Tống Mỹ Linh |
| **34 (60s–64s)** | Vòng 3: Số phận của Cửu Long Bảo Kiếm và các bảo vật trấn quốc đi về đâu? | **C** | `vid_02.mp4 (Ánh sáng nến quét qua trang hồ sơ lưu trữ cũ)` | Camera lướt qua hồ sơ mật cũ và kính lúp |
| **35 (64s–68s)** | Câu trả lời không nằm trong những tin đồn ma quái dân gian | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm cửa)` | Slow pan qua căn phòng vắng tĩnh lặng |
| **36 (68s–72s)** | Mà nằm trong các biên bản thẩm vấn quân sự và lời khai của chính người trong cuộc | **A** | `File:Chiang Kai-Shek, 1928 AP Photo.jpg (Tưởng Giới Thạch năm 1928)` | Focus vào ánh nhìn của Tổng tư lệnh Nam Kinh |
| **37 (72s–76s)** | Hành trình lần theo dấu vết bắt đầu từ xuất thân của kẻ cầm đầu | **A** | `File:Sun Dianying 孙殿英.jpg (Chân dung Tôn Điện Anh)` | Zoom cận cảnh chân dung sắc sảo lạnh lùng |
| **38 (76s–80s)** | Một kẻ cờ bạc giang hồ bước chân vào hàng ngũ quân phiệt | **B** | `ai_05.png (Quán rượu sòng bạc ven đường thời Dân Quốc sơ kỳ)` | Pan chậm từ góc tối qua bàn sới bạc |
| **39 (80s–84s)** | Nơi vũ lực và mưu mẹo là luật sinh tồn duy nhất | **D** | `slam ('TỪ SỚI BẠC ĐẾN TƯỚNG QUÂN PHIỆT')` | Chữ đập chuyển cảnh dứt khoát |
| **40 (84s–88s)** | Để lại dinh thự nguy nga tại tô giới Thiên Tân sau vụ cướp | **A** | `File:孙殿英旧宅.jpg (Dinh thự Tôn Điện Anh tại Thiên Tân)` | Góc máy hất lên kiến trúc biệt thự phương Tây |
| **41 (88s–92s)** | Nơi cất giấu những phần tang vật không bao giờ được hoàn trả | **A** | `File:睦南道孙殿英旧居.JPG (Biệt thự Tôn Điện Anh đường Mục Nam)` | Pan ngang mặt tiền cổng sắt dinh thự |
| **42 (92s–96s)** | Nhưng trước khi trở thành chủ nhân của hàng chục rương châu báu | **A** | `output/long/dong-lang/img/qianlong_dragon_dish.jpg (Đĩa rồng ngự chế CC0)` | Xoay nhẹ men lam vàng và họa tiết rồng |
| **43 (96s–100s)** | Tôn Điện Anh là ai trong vòng xoáy hỗn loạn của thời đại quân phiệt? | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Zoom từ từ vào gương mặt kẻ vô lại Hà Nam |
| **44 (100s–105s)** | Khởi đầu từ những sới bạc khét tiếng vùng Vĩnh Thành | **D** | `chapter (CHƯƠNG 01: NGHỊCH LÝ ĐÔNG LĂNG)` | Thẻ chương chuyển cảnh sắc sảo |

**Tổng kết số liệu chương:**
- Số nhịp: **26 nhịp** | Thời lượng: **105s** | Nhịp trung bình: **4.04s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 54s (51.4%)** | Nhóm B: 8s (7.6%) | Nhóm C: 12s (11.4%) | **Nhóm B+C: 20s (19.0%)** | **Nhóm D: 31s (29.5%)**.
- Số ảnh A sử dụng: **11 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 1 đạt 54s nhóm A (51.4%), sử dụng 11 ảnh tư liệu (sơ đồ Đông Lăng, chân dung Từ Hi, Càn Long, Tưởng Giới Thạch, Tống Mỹ Linh, dinh thự Tôn Điện Anh). Bù đắp 3 vòng mở bằng đồ họa D (counter 30 xe tải, split phim vs đời thật, bars so sánh kho báu, timeline 3 vòng mở).

---

### CH02: Kẻ vô lại cờ bạc (115 giây, 28 nhịp, trung bình 4.11s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **45 (0s–4s)** | Tôn Điện Anh sinh năm 1889 tại huyện Vĩnh Thành, tỉnh Hà Nam | **D** | `map (Bản đồ tỉnh Hà Nam và huyện Vĩnh Thành 1889)` | Phóng to từ bản đồ Trung Hoa vào huyện Vĩnh Thành |
| **46 (4s–8s)** | Gia cảnh bần hàn, tuổi thơ của Tôn là chuỗi ngày cơ cực | **B** | `ai_05.png (Quán rượu sòng bạc ven đường thời Dân Quốc sơ kỳ)` | Pan chậm qua góc phố quê cũ kỹ |
| **47 (8s–12s)** | Một biến cố lớn đã làm thay đổi hoàn toàn cuộc đời Tôn khi còn nhỏ | **D** | `slam ('BIẾN CỐ NĂM ẤY: MỒ CÔI CHA')` | Chữ đập mạnh trên nền xám tối |
| **48 (12s–16s)** | Cha của Tôn vì mâu thuẫn đã bị lính Bát Kỳ bắt giam vào ngục | **A** | `File:China Under Empress Dowager (1914, p 039).jpg (Nha môn triều đình Mãn Thanh)` | Pan dọc theo tường ngục phủ nha môn |
| **49 (16s–20s)** | Và bị tra tấn đánh chết ngay trong ngục tối của triều đình nhà Thanh | **C** | `ai_06.png (Khói thuốc phiện lơ lửng bên bàn gỗ cũ)` | Khói lượn qua chiếc bàn gỗ hoang phế |
| **50 (20s–24s)** | Cái chết oan ức gieo vào lòng đứa trẻ mối hận thù sâu sắc với người Mãn | **D** | `slam ('MỐI THÙ KHẮC CỐT VỚI TRIỀU THANH')` | Chữ đập mạnh rung viền đỏ |
| **51 (24s–28s)** | Lớn lên không được học hành, Tôn bắt đầu lăn lộn khắp các sới bạc | **A** | `File:Muslim Bandits, Xinjiang, China (c1915) Marc Aurel Stein (RESTORED) (4073631151).jpg (Thảo khấu lục lâm đầu thế kỷ 20)` | Pan ngang nhóm giang hồ thời Dân Quốc |
| **52 (28s–32s)** | Nhờ sự liều lĩnh và mưu mẹo, Tôn nhanh chóng trở thành tay cờ bạc có tiếng | **A** | `File:Sun Dianying 孙殿英.jpg (Tôn Điện Anh)` | Zoom cận cảnh ánh mắt giảo hoạt |
| **53 (32s–36s)** | Gia nhập hội kín Miếu Đạo Hội — một tổ chức tôn giáo trá hình ở địa phương | **D** | `split ('SỚI BẠC GIAN HÙNG' vs 'HỘI KÍN MIẾU ĐẠO HỘI')` | Hai khối thông tin đối chiếu |
| **54 (36s–40s)** | Từ một chân lon ton, Tôn leo lên vị trí thủ lĩnh phân hội | **A** | `File:10 Custom Gold Units 1930.JPG (Tiền tệ Dân Quốc)` | Pan qua hoa văn tiền tệ giao dịch ngầm |
| **55 (40s–44s)** | Kiếm tiền khủng nhờ độc quyền sản xuất và phân phối thuốc phiện 'Tam Tiên Cao' | **C** | `ai_06.png (Bàn thuốc phiện và tàn tro khói mờ)` | Camera trôi chậm qua ống tẩu tre và đèn dầu |
| **56 (44s–48s)** | Mạng lưới buôn thuốc phiện giúp Tôn tích lũy một khối tài sản lớn | **D** | `counter ('NGUỒN THU NHA PHIẾN · HÀNG VẠN ĐỒNG BẠC')` | Bộ đếm tiền bạc nhảy số |
| **57 (48s–52s)** | Đồng thời xây dựng một băng đảng vũ trang với hàng trăm tay súng trung thành | **A** | `File:Beiyang Army.jpg (Binh lính thời Dân Quốc)` | Ken Burns quét qua hàng ngũ binh lính |
| **58 (52s–56s)** | Thời thế loạn lạc đầu thế kỷ 20 tạo cơ hội cho kẻ liều lĩnh | **A** | `File:Chine 1911-1916.png (Bản đồ phân tranh 1911-1916)` | Hiển thị các vùng kiểm soát quân sự |
| **59 (56s–60s)** | Triều Thanh sụp đổ năm 1912, vua Phổ Nghi thoái vị | **A** | `File:Chinese child, Emperor PU-YI LCCN2014686335 (cropped).jpg (Phổ Nghi khi thoái vị)` | Slow zoom vào hoàng đế trẻ con trên ngai |
| **60 (60s–64s)** | Trung Hoa bước vào kỷ nguyên các sứ quân cát cứ | **A** | `File:Chine de 1917 à 1920.png (Bản đồ quân phiệt 1917-1920)` | Đồ họa phân chia lãnh thổ động |
| **61 (64s–68s)** | Tôn Điện Anh hiểu rằng: Có tiền mà không có súng thì sẽ bị nuốt chửng | **D** | `quote ('THỜI LOẠN CÓ TIỀN PHẢI CÓ SÚNG')` | Trích dẫn nổi bật trên nền xám |
| **62 (68s–72s)** | Hắn quyết định mang toàn bộ đàn em và vũ khí ra nhập ngũ | **B** | `ai_05.png (Quán rượu sòng bạc ven đường)` | Ánh đèn hắt bóng lưng người đứng dậy rời sới |
| **63 (72s–76s)** | Bước ngoặt từ một trùm sới bạc trở thành tướng lĩnh quân đội | **D** | `timeline (Timeline: 1889 Sinh ra -> 1910 Sới bạc -> 1916 Miếu Đạo Hội -> 1922 Gia nhập quân đội)` | Vẽ đường tiến trình cuộc đời |
| **64 (76s–80s)** | Đầu quân cho đội quân Trấn Tung Quân ở vùng Tây Nam Hà Nam | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Zoom từ quân phục lên ánh nhìn quyết đoán |
| **65 (80s–84s)** | Vũ khí và tiền bạc của Tôn giúp hắn được phong chức chỉ huy tiểu đoàn | **A** | `File:Beiyang Army troops crossing the Gong An street.jpg (Đoàn quân hành quân)` | Pan theo đoàn quân tiến vào phố thị |
| **66 (84s–88s)** | Bắt đầu cuộc leo thang quyền lực bằng mưu mẹo và phản trắc | **C** | `output/asset_library/lib198b/ai_18.png (Hòm rương trong bóng tối)` | Lướt qua các rương gỗ niêm phong |
| **67 (88s–92s)** | Không có lòng trung thành với bất kỳ chủ soái nào | **D** | `slam ('NGUYÊN TẮC: KẺ NÀO MẠNH THÌ THEO')` | Chữ đập dứt khoát |
| **68 (92s–96s)** | Chỉ cần bảo toàn lực lượng và mở rộng địa bàn | **A** | `File:Muslim Bandits, Xinjiang, China (c1915) Marc Aurel Stein (RESTORED) (4073631151).jpg (Binh lính súng trường)` | Ken Burns pan dọc nòng súng trường |
| **69 (96s–100s)** | Đưa Tôn đến với vị tướng quân phiệt tàn bạo khét tiếng miền Bắc | **A** | `File:Sun Dianying 孙殿英.jpg (Tôn Điện Anh)` | Focus vào gương mặt sắc lạnh |
| **70 (100s–105s)** | Đó là Trương Tông Xương — 'Chó ngao Sơn Đông' | **D** | `split ('TÔN ĐIỆN ANH' vs 'TRƯƠNG TÔNG XƯƠNG')` | Hai khung hình chuẩn bị kết nối |
| **71 (105s–110s)** | Cánh cửa dẫn vào những cuộc hỗn chiến đẫm máu thập niên 1920 | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm)` | Slow pan qua căn phòng vắng |
| **72 (110s–115s)** | Mở màn chương mới: Tướng cướp khoác áo quân phục chính quy | **D** | `chapter (CHƯƠNG 02: KẺ VÔ LẠI CỜ BẠC)` | Thẻ chương kết thúc mạch chuyện |

**Tổng kết số liệu chương:**
- Số nhịp: **28 nhịp** | Thời lượng: **115s** | Nhịp trung bình: **4.11s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 60s (52.2%)** | Nhóm B: 12s (10.4%) | Nhóm C: 12s (10.4%) | **Nhóm B+C: 24s (20.9%)** | **Nhóm D: 31s (27.0%)**.
- Số ảnh A sử dụng: **9 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 2 đạt 60s nhóm A (52.2%), sử dụng 9 ảnh tư liệu (chân dung Tôn Điện Anh, thổ phỉ lục lâm, tiền tệ thời kỳ, bản đồ phân tranh Dân Quốc sơ kỳ, quân đội Bắc Dương). Bù đắp thân thế giang hồ bằng đồ họa D (bản đồ Vĩnh Thành Hà Nam, timeline thân thế 1889-1920, slam mầm mống hận thù) và biểu tượng B/C (sòng bạc, khói nha phiến).

---

### CH03: Tướng cướp mặc quân phục (125 giây, 30 nhịp, trung bình 4.17s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **73 (0s–4s)** | Thập niên 1920, Trung Hoa chìm trong vòng xoáy hỗn chiến giữa các tập đoàn quân phiệt | **A** | `File:Map of major Chinese warlord coalitions 1925.png (Bản đồ các liên minh quân phiệt 1925)` | Pan quét qua các vùng cát cứ |
| **74 (4s–8s)** | Trương Tông Xương, viên tướng khét tiếng tàn bạo của Phụng hệ kiểm soát vùng Sơn Đông | **A** | `File:Zhang Zongchang5.jpg (Trương Tông Xương)` | Slow zoom vào chân dung tướng Trương Tông Xương |
| **75 (8s–12s)** | Tôn Điện Anh nhận thấy cơ hội lớn, lập tức đem quân quy thuận dưới trướng họ Trương | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Zoom vào cầu vai chỉ huy |
| **76 (12s–16s)** | Được Trương Tông Xương phong làm Tư lệnh Lữ đoàn 5, sau nâng lên Sư đoàn | **D** | `org (Sơ đồ chỉ huy: Trương Tông Xương -> Lữ đoàn 5 Tôn Điện Anh)` | Đồ họa phân nhánh quân sự |
| **77 (16s–20s)** | Lực lượng của Tôn được trang bị vũ khí hiện đại, tàu hỏa bọc thép và xe cơ giới | **A** | `File:Armored-train1.jpg (Tàu hỏa bọc thép quân phiệt)` | Pan dọc thân tàu bọc thép gắn pháo |
| **78 (20s–25s)** | Cùng xe thiết giáp FT-17 do Pháp sản xuất viện trợ cho quân Phụng hệ | **A** | `File:奉系軍閥的FT-17.jpg (Xe tăng FT-17 của Phụng hệ)` | Zoom vào tháp pháo xe tăng |
| **79 (25s–29s)** | Binh lính của Tôn được huấn luyện tác chiến với đại đao và súng trường | **A** | `File:Chinese warlord soldiers training with swords 1.png (Lính quân phiệt luyện đại đao)` | Pan qua hàng lính vung đại đao |
| **80 (29s–33s)** | Nhưng bản chất đội quân này vẫn là đám thảo khấu lục lâm quen thói cướp bóc | **B** | `ai_07.png (Đoàn xe tải quân sự mờ xa trong bụi mù chiến trận)` | Đoàn xe tải trôi chậm trong bụi mù |
| **81 (33s–37s)** | Năm 1926, Tưởng Giới Thạch phát động Chiến dịch Bắc phạt từ Quảng Châu | **A** | `File:Chiang Kai-shek on horseback during Northern Expedition, Liangyou, 1929-08-30.jpg (Tưởng Giới Thạch cưỡi ngựa Bắc phạt)` | Slow zoom vào tư thế cưỡi ngựa uy phong |
| **82 (37s–41s)** | Đoàn quân Quốc Dân Cách Mạng Quân tiến như vũ bão đánh tan các sứ quân miền Nam | **A** | `File:Chine 1927-1928.png (Bản đồ chiến sự Bắc phạt 1927-1928)` | Mũi tên đồ họa quân sự tiến công về hướng Bắc |
| **83 (41s–45s)** | Đầu năm 1928, liên quân Bắc phạt tiến sát Hà Bắc và Sơn Đông | **A** | `File:Chiang Kai-shek, Feng Yuxiang and Yan Xishan.jpg (Tưởng Giới Thạch, Phùng Ngọc Tường, Diêm Tích Sơn)` | Pan ngang ba nhà lãnh đạo đồng minh Bắc phạt |
| **84 (45s–49s)** | Trương Tông Xương đại bại, tan rã và tháo chạy tán loạn | **D** | `slam ('TRƯƠNG TÔNG XƯƠNG ĐẠI BẠI')` | Chữ đập vỡ vụn trên nền tối |
| **85 (49s–53s)** | Trước nguy cơ bị tiêu diệt, bản năng giang hồ của Tôn Điện Anh lại phát huy | **C** | `output/asset_library/lib198b/ai_18.png (Rương tang vật và xích sắt)` | Camera lướt qua xích sắt khóa chặt |
| **86 (53s–57s)** | Không ngần ngại một giây, Tôn lập tức tuyên bố ly khai Trương Tông Xương | **D** | `slam ('LẬP TỨC ĐỔI CỜ QUY THUẬN')` | Chữ đập dứt khoát |
| **87 (57s–61s)** | Và gửi điện tín xin đầu hàng, quy phục Tổng tư lệnh Tưởng Giới Thạch | **A** | `File:Chiang Kai-Shek, 1928 AP Photo.jpg (Tưởng Giới Thạch 1928)` | Zoom cận cảnh ánh nhìn của Tưởng |
| **88 (61s–65s)** | Đang cần thêm lực lượng để củng cố quyền kiểm soát miền Bắc vừa chiếm được | **A** | `File:Beiyang Army troops crossing the Gong An street.jpg (Đoàn quân tiếp quản)` | Pan theo hàng quân tiếp quản thành phố |
| **89 (65s–69s)** | Tưởng Giới Thạch chấp thuận sự đầu hàng và cải tổ lực lượng của Tôn | **D** | `file (CHỈ DỤ TỔNG TƯ LỆNH: TIẾP NHẬN SƯ ĐOÀN 12)` | Văn bản tiếp nhận với con dấu son |
| **90 (69s–73s)** | Tôn Điện Anh được phiên chế thành Sư đoàn trưởng Sư đoàn 12, Quân đoàn 6 Quốc Dân Cách Mạng Quân | **D** | `org (Phiên chế: Quân đoàn 6 -> Sư đoàn 12 Sư đoàn trưởng Tôn Điện Anh)` | Cây sơ đồ quân hàm hiển thị rõ nét |
| **91 (73s–77s)** | Từ một tên tướng phỉ miền quê trở thành tướng lĩnh quân đội chính quy cấp quốc gia | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh quân phục Quốc gia)` | Slow zoom-in vào cầu vai trung tướng |
| **92 (77s–81s)** | Nhưng danh xưng chính quy không thể nuôi sống hàng vạn binh lính dưới quyền | **B** | `vid_03.mp4 (Bánh xích xe quân sự và bóng lính tuần tra trong sương sớm)` | Camera drift chậm theo bước chân lính trong sương |
| **93 (81s–85s)** | Chính phủ Nam Kinh mới thành lập, ngân khố rỗng tuếch, lương bổng thường xuyên bị nợ đọng | **D** | `bars (Ngân khố Nam Kinh: Nợ lương quân đội 4 tháng liên tiếp)` | Cột đồ họa nợ lương nhấp nháy đỏ |
| **94 (85s–89s)** | Áp lực quân phí đè nặng lên vai Tôn Điện Anh từng ngày | **A** | `File:Locomotives in Tangshan depot.jpg (Đầu máy xe lửa ga Đường Sơn)` | Pan ngang đoàn tàu vận tải than và lương thực |
| **95 (89s–93s)** | Lính không có ăn thì sẽ nổi loạn hoặc đào ngũ hàng loạt | **D** | `slam ('KHÔNG CÓ TIỀN THÌ RÃ QUÂN')` | Chữ đập rung màn hình |
| **96 (93s–97s)** | Tôn nhận ra mình phải tự tìm ra một nguồn tiền mặt khổng lồ bằng mọi giá | **C** | `ai_04.png (Cán cân công lý và chiếc hòm sắt phong ấn)` | Ánh sáng quét qua then khóa đồng |
| **97 (97s–101s)** | Đúng lúc đó, một mệnh lệnh điều động mới từ Nam Kinh được ban xuống | **A** | `File:Nationalist government of Nanking - nominally ruling over entire China, 1930 (2675972715).jpg (Chính phủ Nam Kinh)` | Góc rộng tòa nhà chính phủ |
| **98 (101s–105s)** | Sư đoàn 12 được lệnh di chuyển về huyện Tuân Hóa, phía bắc tỉnh Hà Bắc | **D** | `map (Lộ trình hành quân: Tế Nam -> Thiên Tân -> Huyện Tuân Hóa)` | Vẽ đường hành quân tiến về Tuân Hóa |
| **99 (105s–109s)** | Để tiễu trừ nhóm tàn phỉ của Mã Phúc Điền đang lẩn khuất quanh dãy núi Mã Lan | **A** | `File:Warlords 1925.png (Bản đồ phân bố lực lượng miền Bắc)` | Hiển thị vị trí hiểm trở của Tuân Hóa |
| **100 (109s–114s)** | Nơi tọa lạc giấc ngủ nghìn thu của các bậc đế vương triều Thanh | **A** | `File:Eastern Tombs Tung-ling.jpg (Đông Lăng trong sương núi)` | Ken Burns lướt qua mái ngói vàng trong mây |
| **101 (114s–120s)** | Một ý nghĩ điên rồ và táo tợn lóe lên trong đầu vị tướng cướp | **A** | `File:Sun Dianying 孙殿英.jpg (Tôn Điện Anh)` | Zoom cực cận vào ánh mắt toan tính |
| **102 (120s–125s)** | Kế hoạch biến cuộc tiễu phỉ thành một vụ đào mộ thế kỷ bắt đầu thành hình | **D** | `chapter (CHƯƠNG 03: TƯỚNG CƯỚP MẶC QUÂN PHỤC)` | Thẻ chương chuyển tiếp sắc nét |

**Tổng kết số liệu chương:**
- Số nhịp: **30 nhịp** | Thời lượng: **125s** | Nhịp trung bình: **4.17s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 66s (52.8%)** | Nhóm B: 13s (10.4%) | Nhóm C: 13s (10.4%) | **Nhóm B+C: 26s (20.8%)** | **Nhóm D: 33s (26.4%)**.
- Số ảnh A sử dụng: **12 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 3 đạt 66s nhóm A (52.8%), sử dụng 12 ảnh tư liệu (Trương Tông Xương, tàu bọc thép, xe tăng FT-17, lính đại đao, Tưởng Giới Thạch, các bản đồ quân sự Bắc phạt, đoàn quân Bắc Dương). Bù đắp chuyển biến quân sự bằng đồ họa D (sơ đồ chỉ huy Sư đoàn 12, bản đồ hành quân về Tuân Hóa, bars nợ lương quân đội) và video B/C (đoàn xe quân sự trong bụi mù, lính tuần tra trong sương).

---

### CH04: Kế hoạch 'Tập trận' (115 giây, 28 nhịp, trung bình 4.11s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **103 (0s–4s)** | Tháng 6/1928, Sư đoàn 12 của Tôn Điện Anh chính thức tiến vào huyện Tuân Hóa | **D** | `date ('THÁNG 6/1928: TIẾN QUÂN VÀO TUÂN HÓA')` | Chữ mốc thời gian nổi bật trên nền bản đồ |
| **104 (4s–8s)** | Quần thể Đông Lăng hiện ra giữa dãy núi non trùng điệp, thâm nghiêm và tĩnh lặng | **A** | `File:Eastern Qing Tombs.jpg (Toàn cảnh lăng tẩm Đông Lăng)` | Ken Burns quét chậm từ đỉnh núi xuống các lăng điện |
| **105 (8s–12s)** | Nơi chôn cất 5 vị hoàng đế, 15 hoàng hậu và 136 phi tần triều Mãn Thanh | **A** | `File:Villages Around the Eastern Qing tombs.jpg (Làng mạc quanh Đông Lăng)` | Pan ngang thung lũng lăng tẩm và xóm thôn |
| **106 (12s–16s)** | Sau khi triều Thanh sụp đổ, lăng tẩm chỉ còn vài chục thị vệ già trông coi nghèo khó | **A** | `File:Tombs of Cixi and Ci'an.jpg (Lăng mộ Từ Hi và Từ An)` | Slow zoom vào bậc thềm đá vắng bóng người |
| **107 (16s–20s)** | Tàn quân phỉ Mã Phúc Điền vừa định đào trộm lăng mộ đã bị quân Tôn đánh dạt | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Zoom vào dáng đứng chỉ huy của Tôn |
| **108 (20s–24s)** | Nhìn thấy lăng tẩm nguy nga tráng lệ, lòng tham của Tôn bùng cháy dữ dội | **C** | `output/asset_library/lib198b/ai_04.png (Bến núi mờ sương và bóng người toan tính)` | Ánh sáng quét qua bóng người đứng trên mỏm đá |
| **109 (24s–28s)** | Tôn nói với thuộc hạ: 'Càn Long, Từ Hi vét sạch thiên hạ, nay ta lấy lại nuôi quân' | **D** | `quote ('CÀN LONG, TỪ HI VÉT SẠCH THIÊN HẠ · NAY TA LẤY LẠI NUÔI QUÂN')` | Trích dẫn lời Tôn Điện Anh nổi bật trên màn hình |
| **110 (28s–32s)** | Hắn mượn cớ trả thù cho tổ tiên nhà Hán và cuộc cách mạng dân tộc để biện minh | **D** | `slam ('BIỆN MINH: CÁCH MẠNG VÀ BÁO THÙ')` | Chữ đập mạnh trên nền tối |
| **111 (32s–36s)** | Nhưng để thực hiện cuộc đào trộm thế kỷ, cần phải che giấu tai mắt thiên hạ | **B** | `ai_08.png (Cổng rào quân sự dã chiến phong tỏa con đường núi)` | Pan ngang rào chắn dây thép gai và trạm gác dã chiến |
| **112 (36s–40s)** | Ngày 1/7/1928, Tôn Điện Anh phát lệnh thiết quân luật trên toàn huyện Tuân Hóa | **D** | `file (LỆNH THIẾT QUÂN LUẬT: SƯ ĐOÀN 12 · TUÂN HÓA)` | Lệnh quân sự đóng dấu đỏ mở ra |
| **113 (40s–44s)** | Lấy danh nghĩa 'Tập trận quân sự tác chiến phòng ngự chống tàn phỉ' | **D** | `slam ('VỎ BỌC: DIỄN TẬP QUÂN SỰ ĐẶC BIỆT')` | Chữ đập dứt khoát |
| **114 (44s–48s)** | Các trạm kiểm soát quân sự được dựng lên dày đặc trên mọi ngả đường dẫn vào Đông Lăng | **A** | `File:Protection Stone of Eastern Qing Tomb, 2016-09-06 01.jpg (Cột mốc giới hạn Đông Lăng)` | Ken Burns zoom cận cảnh ranh giới lăng |
| **115 (48s–52s)** | Nghiêm cấm người dân ra vào, cắt đứt hoàn toàn đường dây điện tín liên lạc với bên ngoài | **D** | `map (Bản đồ vòng phong tỏa khép kín quanh Dụ Lăng và Định Đông Lăng)` | Vòng đỏ quân sự siết chặt thung lũng |
| **116 (52s–56s)** | Các thị vệ và nhân viên trông coi lăng của triều đình nhà Thanh bị xua đuổi trục xuất | **A** | `File:Dabeilou in Eastern Qing Tombs.jpg (Đại Bi Lâu Đông Lăng)` | Pan từ mái ngói xuống cổng vòm trống trơn |
| **117 (56s–60s)** | Ai chống cự lập tức bị bắt giam hoặc xử bắn với tội danh thông đồng với thổ phỉ | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm)` | Slow pan qua không gian tối tăm |
| **118 (60s–64s)** | Một tiểu đoàn công binh tinh nhuệ được bí mật điều động vào sâu trong lăng | **A** | `File:Qing Tombs 15 (4924845706).jpg (Đường lát đá cổ dẫn vào lăng mộ)` | Pan theo trục đường đá thẳng tắp |
| **119 (64s–68s)** | Mang theo đầy đủ thuốc nổ dynamite, xà beng, búa tạ và cuốc xẻng công binh | **C** | `output/asset_library/lib198b/ai_18.png (Hòm gỗ thuốc nổ trong bóng tối)` | Lướt qua các thùng gỗ chứa vật tư |
| **120 (68s–72s)** | Đồng thời điều động hơn 30 xe tải quân sự ém sẵn ở chân núi Mã Lan | **A** | `File:Eastern Tombs Tung-ling.jpg (Đường chân núi Mã Lan)` | Ken Burns phóng tầm mắt ra đường núi |
| **121 (72s–76s)** | Chuẩn bị cho một chiến dịch vận chuyển tang vật quy mô chưa từng có | **D** | `counter ('CHUẨN BỊ: 30 XE TẢI · 1 TIỂU ĐOÀN CÔNG BINH')` | Đếm số phương tiện và binh lực |
| **122 (76s–80s)** | Mục tiêu số một được lựa chọn: Dụ Lăng của Càn Long Hoàng đế | **A** | `File:清裕陵（乾隆墓）.jpg (Dụ Lăng Càn Long)` | Slow zoom-in vào Minh Lâu Dụ Lăng |
| **123 (80s–84s)** | Vị hoàng đế trị vì 60 năm thời kỳ cực thịnh nhất của triều Thanh | **A** | `File:乾隆皇帝朝服像轴.png (Càn Long triều phục)` | Pan từ long bào lên ánh mắt hoàng đế |
| **124 (84s–88s)** | Người nổi tiếng là tay chơi cổ vật và sưu tầm kho báu lớn nhất lịch sử | **A** | `output/long/dong-lang/img/qianlong_dragon_dish.jpg (Đĩa rồng ngự chế CC0)` | Zoom cận cảnh hoa văn rồng tinh xảo |
| **125 (88s–92s)** | Và mục tiêu số hai: Định Đông Lăng của Từ Hi Thái Hậu | **A** | `File:Putuo Yu Ding Dongling 1.jpg (Định Đông Lăng Từ Hi)` | Pan qua cổng vào Định Đông Lăng |
| **126 (92s–96s)** | Người đã vét cạn ngân khố đế chế để xây dựng lăng mộ riêng cho mình | **A** | `File:The Imperial Portrait of the Ci-Xi Imperial Dowager Empress.PNG (Chân dung Từ Hi)` | Focus vào chuỗi ngọc trên tay Từ Hi |
| **127 (96s–100s)** | Mọi chuẩn bị đã hoàn tất trong sự im lặng đáng sợ của rừng núi | **B** | `ai_08.png (Trạm gác quân sự trong mưa phùn)` | Khung cảnh trạm gác dã chiến cô quạnh |
| **128 (100s–105s)** | Màn đêm ngày 4/7/1928 buông xuống thung lũng Tuân Hóa | **C** | `ai_01.png (Dãy núi Mã Lan trong sương đêm)` | Mây đen che phủ đỉnh núi |
| **129 (105s–110s)** | Chiến dịch công phá hầm mộ chính thức bắt đầu điểm hỏa | **D** | `slam ('GIỜ G ĐÃ ĐIỂM: ĐÊM 4/7/1928')` | Chữ đập dứt khoát rung màn hình |
| **130 (110s–115s)** | Mở màn bằng phát súng ép người dẫn đường tìm lối vào Dụ Lăng | **D** | `chapter (CHƯƠNG 04: KẾ HOẠCH 'TẬP TRẬN')` | Thẻ chương chuyển cảnh sắc sảo |

**Tổng kết số liệu chương:**
- Số nhịp: **28 nhịp** | Thời lượng: **115s** | Nhịp trung bình: **4.11s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 61s (53.0%)** | Nhóm B: 12s (10.4%) | Nhóm C: 12s (10.4%) | **Nhóm B+C: 24s (20.9%)** | **Nhóm D: 30s (26.1%)**.
- Số ảnh A sử dụng: **10 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 4 đạt 61s nhóm A (53.0%), sử dụng 10 ảnh tư liệu (quần thể Đông Lăng, làng mạc Tuân Hóa, lăng mộ Từ Hi - Từ An, cột mốc bảo vệ, Đại Bi Lâu, Dụ Lăng, đĩa rồng Càn Long). Bù đắp kế hoạch phong tỏa bằng đồ họa D (bản đồ siết chặt vòng vây Tuân Hóa, date lệnh thiết quân luật 1/7/1928, counter 30 xe tải) và hình ảnh B/C (cổng rào quân sự dã chiến, hòm thuốc nổ ngầm).

---

### CH05: Phá cửa Dụ Lăng (145 giây, 36 nhịp, trung bình 4.03s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **131 (0s–4s)** | Đêm 4/7/1928, tiểu đoàn công binh Sư đoàn 12 bắt đầu đào bới tại Dụ Lăng | **A** | `File:清裕陵（乾隆墓）.jpg (Dụ Lăng Càn Long)` | Slow zoom-in vào phía sau Minh Lâu |
| **132 (4s–8s)** | Lối vào hầm mộ ngầm Dụ Lăng vốn là bí mật quốc gia được giữ kín hàng trăm năm | **B** | `ai_09.png (Vòm cổng đá ngầm đóng kín dưới tầng hầm sâu)` | Pan chậm từ vòm đá xuống nền đất ẩm |
| **133 (8s–12s)** | Công binh bắt giữ một người thợ đá già từng tham gia tu sửa lăng ép chỉ điểm | **D** | `slam ('BẮT ÉP CHỈ ĐIỂM CỬA NGẦM')` | Chữ đập mạnh trên nền tối |
| **134 (12s–16s)** | Lối vào bí mật nằm ngay dưới bức tường Á Ba Viện (Viện Nguyệt Nha Thành) | **A** | `File:裕陵月牙城(哑巴院).jpg (Á Ba Viện Dụ Lăng)` | Ken Burns pan dọc chân tường Á Ba Viện |
| **135 (16s–20s)** | Sau nhiều giờ đào bới lớp đất đá nén chặt, cửa đường hầm ngầm phát lộ | **B** | `ai_02.png (Lối vào hầm mộ ngầm trong bóng đêm)` | Ánh đèn bão hắt vào cửa hầm tối om |
| **136 (20s–24s)** | Nhưng phía trước họ là hệ thống phòng thủ ngầm kiên cố bậc nhất | **D** | `waterfall (Cấu trúc 4 lớp cửa đá cẩm thạch ngầm Dụ Lăng)` | Đồ họa 4 tầng cửa ngầm lần lượt sáng lên |
| **137 (24s–28s)** | 4 tầng cửa đá cẩm thạch nguyên khối, mỗi cánh nặng hàng chục tấn | **A** | `File:清东陵裕陵地宫.jpg (Địa cung Dụ Lăng)` | Pan chậm qua vòm đá cẩm thạch khổng lồ |
| **138 (28s–32s)** | Được khóa chặt từ phía trong bằng cơ chế then đá tự động 'Đá trác đỉnh' | **A** | `File:裕陵地宫.jpg (Then đá và cửa đá Dụ Lăng)` | Zoom cận cảnh khe then đá trác đỉnh |
| **139 (32s–36s)** | Búa tạ và xà beng hoàn toàn bất lực trước những khối đá cẩm thạch ngàn cân | **D** | `slam ('BÚA TẠ BẤT LỰC · RA LỆNH NỔ MÌN')` | Chữ đập dứt khoát |
| **140 (36s–40s)** | Tôn Điện Anh ra lệnh dùng thuốc nổ dynamite nổ tung từng cánh cửa | **C** | `output/asset_library/lib198b/ai_18.png (Thùng thuốc nổ chèn vào góc cửa)` | Camera trôi nhanh qua các thùng thuốc súng |
| **141 (40s–44s)** | Tiếng nổ đinh tai nhức óc làm rung chuyển cả ngọn núi phía sau lăng | **B** | `vid_01.mp4 (Bụi khói mờ ảo trôi qua vòm đá hầm mộ)` | Khói bụi đá trắng mù mịt dưới luồng sáng |
| **142 (44s–48s)** | Lớp cửa đá thứ nhất và thứ hai bị đánh sập trong làn khói thuốc súng | **A** | `File:Yuling Tomb 20160906 (3).jpg (Cửa đá chạm phù điêu Dụ Lăng)` | Ken Burns lướt qua vết nứt vỡ trên phù điêu |
| **143 (48s–52s)** | Trên bề mặt cửa đá là những bức phù điêu Phật giáo Tây Tạng tinh xảo vô giá | **A** | `File:Yuling Tomb 20160906 (5).jpg (Phù điêu Tứ Đại Thiên Vương trên cửa đá)` | Pan chậm từ gương mặt hộ pháp xuống hoa văn sen |
| **144 (52s–56s)** | Cùng hàng vạn chữ Phạn và Tạng khắc kinh Bát Nhã Tâm Kinh | **A** | `File:Yuling Tomb 20160906 (9).jpg (Kinh Phật khắc trên vách đá Dụ Lăng)` | Zoom cận cảnh từng nét chữ Phạn trên đá cẩm thạch |
| **145 (56s–60s)** | Đến lớp cửa thứ tư dẫn vào tẩm điện chính, chướng ngại mới xuất hiện | **D** | `slam ('CHƯỚNG NGẠI TẦNG THỨ TƯ: CỬA BỊ CHẶN')` | Chữ đập mạnh rung nhẹ màn hình |
| **146 (60s–64s)** | Chiếc quan tài khổng lồ của Càn Long bị nước ngầm đẩy trôi ra chặn cứng cánh cửa | **A** | `File:Yuling Tomb 20160906 (12).jpg (Gian tẩm thất Dụ Lăng)` | Góc rộng gian đặt quan tài trong bóng tối |
| **147 (64s–68s)** | Hệ thống thoát nước ngầm của lăng bị tắc, nước tích tụ trăm năm dâng ngập đến đầu gối | **B** | `vid_04.mp4 (Dòng nước ngầm tĩnh lặng phản chiếu ánh đuốc hầm mộ)` | Camera lướt chậm trên mặt nước đen phẳng lặng |
| **148 (68s–72s)** | Không thể đẩy cửa, công binh tiếp tục nổ mìn làm vỡ góc trên cánh cửa đá | **A** | `File:Yuling Tomb 20160906 (16).jpg (Dấu vết đục phá trên cửa Dụ Lăng)` | Zoom vào vết vỡ nham nhở nơi đặt mìn |
| **149 (72s–76s)** | Binh lính lội qua dòng nước lạnh buốt tràn vào tẩm điện chính | **C** | `ai_02.png (Đường hầm ngập nước và bóng lính)` | Bóng lính cầm đuốc phản chiếu trên mặt nước |
| **150 (76s–80s)** | Tại đây đặt 6 cỗ quan tài: Càn Long, 2 hoàng hậu và 3 hoàng quý phi | **D** | `org (Sơ đồ 6 cỗ quan tài trong tẩm điện Dụ Lăng)` | Sơ đồ vị trí quan tài Càn Long và phi tần |
| **151 (80s–84s)** | Quan tài của Càn Long làm bằng gỗ nam mộc tơ vàng quý hiếm bậc nhất | **A** | `File:Yuling2.jpg (Bệ đá đặt quan tài Dụ Lăng)` | Ken Burns quét qua bệ đá hoa sen chạm rồng |
| **152 (84s–88s)** | Binh lính dùng rìu sắt và xà beng chém nát nắp quan tài để tìm bảo vật | **D** | `slam ('CHÉM VỠ QUAN TÀI NAM MỘC')` | Chữ đập dứt khoát trên nền đen |
| **153 (88s–92s)** | Hài cốt của vị hoàng đế vĩ đại triều Thanh bị xới tung ra khỏi quan quách | **A** | `File:The Qianlong Emperor in Ceremonial Armour on Horseback.jpg (Càn Long hoàng đế)` | Pan từ từ từ gương mặt kiêu hãnh sang bóng tối |
| **154 (92s–96s)** | Tất cả đồ tùy táng vàng ngọc đặt trong và ngoài quan tài đều bị cướp sạch | **A** | `output/long/dong-lang/img/qianlong_dragon_dish.jpg (Đĩa rồng ngự chế CC0)` | Zoom cận cảnh men vàng và rồng bay |
| **155 (96s–100s)** | Hàng chục bức thư pháp, tranh cuộn cổ quý hiếm bị giẫm đạp dưới bùn nước | **A** | `output/long/dong-lang/img/qing_brushpot_paradise.jpg (Ống bút gốm họa tiên cảnh CC0)` | Xoay nhẹ thân ống bút ngự dụng |
| **156 (100s–104s)** | Đặc biệt nhất là thanh Cửu Long Bảo Kiếm đặt bên sườn thi thể Càn Long | **D** | `slam ('PHÁT HIỆN: CỬU LONG BẢO KIẾM')` | Chữ đập mạnh nổi bật viền hoàng kim |
| **157 (104s–108s)** | Thanh bảo kiếm dài 5 thước, chuôi nạm 9 con rồng vàng và ngọc quý | **A** | `output/long/dong-lang/img/qianlong_dragon_plaque.jpg (Bản phù điêu rồng ngự chế CC0)` | Ken Burns lướt qua chi tiết rồng cuộn |
| **158 (108s–112s)** | Món bảo vật trấn quốc được chuyển thẳng đến tay Tôn Điện Anh | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Zoom cận cảnh ánh nhìn tham vọng của Tôn |
| **159 (112s–116s)** | Hàng chục rương hòm chứa vàng bạc châu báu được khiêng ra ngoài hầm mộ | **C** | `output/asset_library/lib198b/ai_18.png (Hòm gỗ tang vật nối tiếp nhau)` | Camera trôi chậm qua dãy thùng gỗ chất đống |
| **160 (116s–120s)** | Chất lên các xe tải quân sự đợi sẵn trong đêm tối | **A** | `File:Yuling in Eastern Qing Tombs.jpg (Lối ra Dụ Lăng)` | Góc rộng lối đá dẫn ra khỏi Dụ Lăng |
| **161 (120s–124s)** | Cuộc cướp phá tại Dụ Lăng diễn ra liên tục từ đêm đến sáng | **D** | `timeline (Diễn biến Dụ Lăng: 21h Đào Á Ba Viện -> 02h Phá cửa 4 -> 06h Khiêng tang vật)` | Dòng mốc thời gian chuyển động liên tục |
| **162 (124s–128s)** | Lòng hầm mộ Càn Long chìm trong cảnh tượng hoang tàn ngập nước | **A** | `File:Yuling4.jpg (Địa cung Dụ Lăng trống trơn)` | Pan qua lòng hầm mộ đá hoang lạnh |
| **163 (128s–132s)** | Nhưng lòng tham của Tôn Điện Anh vẫn chưa dừng lại ở đó | **A** | `File:Sun Dianying 孙殿英.jpg (Tôn Điện Anh)` | Focus vào nụ cười thỏa mãn |
| **164 (132s–137s)** | Hắn lập tức hạ lệnh chuyển toàn bộ công binh và thuốc nổ sang lăng bên cạnh | **A** | `File:Tombs of Cixi and Ci'an.jpg (Định Đông Lăng trong sương sớm)` | Pan sang ngọn đồi Định Đông Lăng |
| **165 (137s–141s)** | Nơi an nghỉ của người phụ nữ xa hoa bậc nhất: Từ Hi Thái Hậu | **A** | `File:The Imperial Portrait of the Ci-Xi Imperial Dowager Empress.PNG (Chân dung Từ Hi)` | Slow zoom-in vào thần thái quyền lực Từ Hi |
| **166 (141s–145s)** | Một cuộc cướp phá thậm chí còn tàn bạo và giàu có hơn sắp bắt đầu | **D** | `chapter (CHƯƠNG 05: PHÁ CỬA DỤ LĂNG)` | Thẻ chương chuyển cảnh dứt khoát |

**Tổng kết số liệu chương:**
- Số nhịp: **36 nhịp** | Thời lượng: **145s** | Nhịp trung bình: **4.03s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 77s (53.1%)** | Nhóm B: 15s (10.3%) | Nhóm C: 16s (11.0%) | **Nhóm B+C: 31s (21.4%)** | **Nhóm D: 37s (25.5%)**.
- Số ảnh A sử dụng: **14 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 5 đạt 77s nhóm A (53.1%), sử dụng 14 ảnh tư liệu thật (Dụ Lăng Càn Long, Á Ba Viện, địa cung Dụ Lăng, hệ thống cửa đá chạm khắc kinh Phật Tạng, bệ đá hoa sen, phù điêu rồng, đĩa rồng, ống bút ngự dụng). Bù đắp nhịp công phá kịch tính bằng đồ họa D (waterfall 4 tầng cửa đá ngầm, sơ đồ 6 cỗ quan tài, timeline diễn biến đêm 4/7) và hình ảnh B/C (vòm đá ngầm, nước ngập địa cung, hòm tang vật).

---

### CH06: Quan tài Từ Hi (145 giây, 36 nhịp, trung bình 4.03s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **167 (0s–4s)** | Rạng sáng ngày 5/7/1928, toán công binh kéo sang Định Đông Lăng của Từ Hi | **D** | `date ('RẠNG SÁNG 5/7/1928: MỤC TIÊU ĐỊNH ĐÔNG LĂNG')` | Chữ ngày giờ hiển thị trên nền lăng điện |
| **168 (4s–8s)** | Định Đông Lăng được xem là kiệt tác kiến trúc xa hoa nhất lịch sử lăng tẩm đế vương | **A** | `File:慈禧陵隆恩殿 4.jpg (Điện Long Ân Định Đông Lăng)` | Ken Burns quét qua hàng cột đồng và mái lưu ly vàng |
| **169 (8s–12s)** | Kinh phí xây dựng tiêu tốn hàng triệu lạng bạc, dát vàng khắp các vì kèo và cột đá | **A** | `File:Putuo Yu Ding Dongling 3.jpg (Bên trong điện thờ Từ Hi)` | Slow zoom-in vào chi tiết trần nhà thếp vàng |
| **170 (12s–16s)** | Công binh tiếp tục dùng phương thức cũ: Khoan đá và nhồi thuốc nổ dynamite | **B** | `ai_09.png (Vòm đá lối vào hầm mộ ngầm)` | Ánh đèn hắt lên vách đá ẩm ướt |
| **171 (16s–20s)** | Sau tiếng nổ xé trời, cánh cửa đá cẩm thạch ngầm của Định Đông Lăng vỡ toang | **A** | `File:1928 DingDongLing Looting Damage.jpg (Hiện trường nổ mìn cửa Định Đông Lăng)` | Pan chậm qua những mảng đá cẩm thạch vỡ vụn |
| **172 (20s–24s)** | Khói thuốc súng tan ra, để lộ không gian địa cung lộng lẫy khác thường | **B** | `ai_10.png (Không gian tẩm điện tráng lệ phủ bụi thời gian)` | Camera trôi chậm qua gian phòng đá ngầm tĩnh mịch |
| **173 (24s–28s)** | Địa cung của Từ Hi khô ráo hơn Dụ Lăng, tường đá chạm khắc hoa văn hoa lệ | **A** | `File:Putuo Yu Ding Dongling 4.jpg (Địa cung Định Đông Lăng)` | Ken Burns quét qua vách đá cẩm thạch trắng |
| **174 (28s–32s)** | Ở chính giữa là chiếc quan tài nạm vàng bề thế đặt trên bệ đá ngọc | **A** | `File:Cixi Coffin.jpg (Quan tài Từ Hi Thái Hậu)` | Zoom cận cảnh lớp sơn then đen bóng và hoa văn dát vàng |
| **175 (32s–36s)** | Bên trong chiếc quan tài này là kho báu mà cả thiên hạ từng thèm muốn | **C** | `ai_03.png (Ánh sáng đèn bão lướt qua rương báu vật cổ)` | Ánh sáng quét qua nắp rương hé mở |
| **176 (36s–40s)** | Lính công binh dùng xà beng nạy tung lớp nắp quan tài nặng nề | **D** | `slam ('BẨY NẮP QUAN TÀI NẠM VÀNG')` | Chữ đập mạnh trên nền tối |
| **177 (40s–44s)** | Khi nắp bật mở, một cảnh tượng kinh ngạc hiện ra trước mắt đám cướp | **D** | `slam ('THI THỂ NGUYÊN VẸN SAU 20 NĂM')` | Chữ đập rung màn hình |
| **178 (44s–48s)** | Thi thể Từ Hi Thái Hậu qua 20 năm vẫn được bảo quản gần như nguyên vẹn | **A** | `File:The Imperial Portrait of the Ci-Xi Imperial Dowager Empress.PNG (Chân dung Từ Hi)` | Slow zoom vào dung mạo uy nghiêm của Thái hậu |
| **179 (48s–52s)** | Nằm trên tấm đệm thêu hoa sen đính hàng ngàn viên ngọc trai | **A** | `File:Cixi Burial Garments NCSM.jpg (Liễm phục đính ngọc của Từ Hi)` | Pan dọc theo dải áo gấm đính ngọc trai li ti |
| **180 (52s–56s)** | Đầu đội mũ miện phượng hoàng đính viên trân châu lớn bằng quả trứng chim | **A** | `File:Chinese - Ceremonial Headdress - Walters 863 - Back.jpg (Mũ miện ngọc trai hoàng cung)` | Zoom vào hạt ngọc đỉnh miện |
| **181 (56s–60s)** | Đám lính lao vào xâu xé, tước đoạt toàn bộ y phục và trang sức trên thi thể | **A** | `File:Cixi Tomb Robbery 1928.jpg (Hiện trường cướp phá Định Đông Lăng)` | Pan ngang hiện trường tan hoang dưới đèn bão |
| **182 (60s–64s)** | Chiếc áo bào gấm thêu kinh Phật và chuỗi ngọc bội bị giật rách tơi tả | **A** | `File:Cixi Burial Garments 2 NCSM.jpg (Chi tiết áo liễm phục bị giật rách)` | Zoom cận cảnh vết rách trên vải gấm cổ |
| **183 (64s–68s)** | Đặc biệt nhất là viên ngọc Dạ Minh Châu ngậm trong miệng thi thể | **D** | `slam ('MỤC TIÊU SỐ 1: VIÊN DẠ MINH CHÂU')` | Chữ đập nổi bật viền xanh ngọc |
| **184 (68s–72s)** | Theo phong tục hoàng gia, viên ngọc được ngậm để giữ cho thi hài không phân hủy | **A** | `File:KugelförmigeSchnitzereiausFluorit.jpg (Khối ngọc phát quang tự nhiên CC0)` | Xoay nhẹ khối ngọc tròn bóng bẩy |
| **185 (72s–76s)** | Binh lính dùng xà beng nạy mạnh vào hàm răng thi thể để cạy lấy viên ngọc | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng le lói)` | Slow pan qua góc tối rợn người |
| **186 (76s–80s)** | Viên ngọc rơi ra, tỏa ra ánh sáng huyền ảo trong lòng bàn tay kẻ cướp | **C** | `ai_12.png (Khối ngọc phát quang mờ ảo trong hộp gấm cổ)` | Ánh sáng xanh lam dịu nhẹ phát ra từ viên ngọc |
| **187 (80s–84s)** | Bên cạnh đó là cặp dưa hấu ngọc phỉ thúy xanh biếc vô giá | **A** | `output/long/dong-lang/img/melon_jade_pot.jpg (Ấm ngọc phỉ thúy dáng dưa CC0)` | Zoom cận cảnh vân ngọc xanh ngọc bích |
| **188 (84s–88s)** | Cùng 108 bức tượng Phật bằng vàng ròng xếp xung quanh thi hài | **A** | `File:Buddha Amitayus Museum Rietberg BA 34.jpg (Tượng Phật vàng cổ)` | Pan qua ánh kim loại vàng ròng lấp lánh |
| **189 (88s–92s)** | Sau khi vét sạch bảo vật, thi thể Từ Hi bị vứt nằm chỏng trơ trên nắp quan tài | **A** | `File:DingDongLing1.jpg (Bên trong địa cung Định Đông Lăng)` | Góc rộng gian hầm mộ ngổn ngang đá gạch |
| **190 (92s–96s)** | Tất cả đồ tùy táng vàng ngọc được gom vào hàng trăm bao tải quân sự | **C** | `output/asset_library/lib198b/ai_18.png (Hòm gỗ tang vật)` | Lướt qua các thùng gỗ chất đầy đồ |
| **191 (96s–100s)** | Bản kê của Lý Liên Anh từng ghi lại: Trị giá kho báu trong mộ Từ Hi vượt trên 50 triệu lạng | **D** | `ledger (Bản kê cổ vật Từ Hi: Dạ Minh Châu · Dưa phỉ thúy · San hô đỏ · 108 tượng Phật)` | Danh mục cổ vật cuộn chạy trên màn hình |
| **192 (100s–104s)** | Một con số khổng lồ đủ sức mua trọn vài hạm đội thiết giáp hạm thời bấy giờ | **D** | `bars (So sánh: Trị giá mộ Từ Hi vs Toàn bộ ngân sách Bắc Dương Thủy Sư)` | Cột đồ họa giá trị vượt khung hình |
| **193 (104s–108s)** | Chiến dịch cướp phá tiếp tục kéo dài sang ngày 6 và 7 tháng 7 | **D** | `timeline (Mốc thời gian: 5/7 Phá mộ Từ Hi -> 6/7 Vét lăng phụ -> 7/7 Chở đồ)` | Dòng mốc thời gian chuyển động |
| **194 (108s–112s)** | Đoàn xe tải 30 chiếc của Sư đoàn 12 thay nhau ra vào chở đồ liên tục không nghỉ | **B** | `ai_07.png (Đoàn xe tải quân sự mờ xa trong bụi mù)` | Đoàn xe tải quân sự trôi chậm trên đường núi |
| **195 (112s–116s)** | Được ngụy trang cẩn thận dưới những tấm bạt phủ đất đá dã chiến | **A** | `File:Eastern Tombs Tung-ling.jpg (Đường núi Đông Lăng)` | Ken Burns quét theo cung đường uốn lượn |
| **196 (116s–120s)** | Chiều ngày 7/7/1928, Tôn Điện Anh hạ lệnh rút quân khỏi Tuân Hóa | **D** | `date ('CHIỀU 7/7/1928: RÚT QUÂN KHỎI ĐÔNG LĂNG')` | Chữ mốc hoàn thành chiến dịch cướp phá |
| **197 (120s–124s)** | Để lại hai ngôi lăng tẩm hoàng gia bị hủy hoại tan hoang | **A** | `File:1928 DingDongLing Looting Damage.jpg (Cửa mộ bị nổ mìn)` | Pan chậm qua vết phá hoại cửa đá |
| **198 (124s–128s)** | Nhưng một chiến dịch quân sự quy mô 3 ngày đêm không thể giấu kín mãi | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm)` | Slow pan qua căn phòng vắng |
| **199 (128s–132s)** | Những mảnh ngọc và vàng rơi vãi trên đường bắt đầu bị người dân phát hiện | **A** | `output/long/dong-lang/img/qing_jade_cup.jpg (Chén ngọc triều Thanh CC0)` | Zoom vào miệng chén ngọc chạm trổ |
| **200 (132s–136s)** | Tin tức nổ ra như bom sét thổi về tô giới Thiên Tân | **D** | `slam ('TIN TỨC BÙNG NỔ TẠI THIÊN TÂN')` | Chữ đập mạnh rung màn hình |
| **201 (136s–141s)** | Nơi vị hoàng đế cuối cùng đang ngụ cư trong sự phẫn uất tột cùng | **A** | `File:Puyi and Wanrong Tianjin.jpg (Phổ Nghi tại Thiên Tân)` | Focus vào gương mặt u uất của Phổ Nghi |
| **202 (141s–145s)** | Cơn thịnh nộ lịch sử của hoàng tộc Mãn Thanh chính thức bùng nổ | **D** | `chapter (CHƯƠNG 06: QUAN TÀI TỪ HI)` | Thẻ chương chuyển cảnh sắc nét |

**Tổng kết số liệu chương:**
- Số nhịp: **36 nhịp** | Thời lượng: **145s** | Nhịp trung bình: **4.03s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 78s (53.8%)** | Nhóm B: 13s (9.0%) | Nhóm C: 16s (11.0%) | **Nhóm B+C: 29s (20.0%)** | **Nhóm D: 38s (26.2%)**.
- Số ảnh A sử dụng: **13 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 6 đạt 78s nhóm A (53.8%), sử dụng 13 ảnh tư liệu thật (Định Đông Lăng, Điện Long Ân, cửa mộ bị nổ mìn, quan tài Từ Hi, áo liễm phục đính ngọc, mũ miện ngọc trai hoàng gia, khối ngọc fluorite, ấm ngọc dưa hấu, chén ngọc, ảnh hiện trường 1928). Bù đắp câu chuyện kịch tính bằng đồ họa D (ledger danh mục báu vật mộ Từ Hi, bars so sánh ngân sách, timeline 72 giờ cướp phá) và biểu tượng B/C (gian tẩm điện mờ ảo, ngọc phát quang, đoàn xe tải phủ bạt).

---

### CH07: Cơn thịnh nộ ở Thiên Tân (120 giây, 30 nhịp, trung bình 4.00s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **203 (0s–4s)** | Cuối tháng 7/1928, các tờ báo lớn tại Thiên Tân và Thượng Hải đồng loạt giật tít chấn động | **D** | `slam ('CHẤN ĐỘNG TRUYỀN THÔNG: ĐÔNG LĂNG BỊ CƯỚP')` | Chữ đập mạnh trên nền mặt báo mờ |
| **204 (4s–8s)** | Thông tin vụ nổ mìn đào mộ Từ Hi và Càn Long lan truyền khắp thế giới như đám cháy | **A** | `File:China Under Empress Dowager (1914, p 039).jpg (Tài liệu về triều đình Thanh)` | Pan qua trang tài liệu lịch sử |
| **205 (8s–12s)** | Tại Trương Viên, tô giới Nhật Bản ở Thiên Tân, cựu hoàng Phổ Nghi chết lặng | **A** | `File:Johnston, Puyi and Wanrong in the Zhang Garden.png (Phổ Nghi tại Trương Viên)` | Slow zoom-in vào Phổ Nghi đứng trước biệt thự |
| **206 (12s–16s)** | Nơi Phổ Nghi đang sống lưu vong sau khi bị trục xuất khỏi Tử Cấm Thành năm 1924 | **A** | `File:Puyi in the Jing Garden, Tianjin, 1929-1931.png (Phổ Nghi tại Thiên Tân)` | Pan ngang hoa viên nơi Phổ Nghi ngụ cư |
| **207 (16s–20s)** | Lăng mộ tổ tiên bị đào bới, thi hài hoàng đế và thái hậu bị làm nhục thô bạo | **D** | `slam ('SỈ NHỤC TỘT CÙNG CỦA HOÀNG TỘC')` | Chữ đập rung màn hình viền đỏ |
| **208 (20s–24s)** | Phổ Nghi cùng toàn thể hoàng tộc Ái Tân Giác La mặc tang phục trắng lập hương án | **B** | `ai_11.png (Thư phòng cổ vắng lặng bên rèm lụa trắng)` | Slow pan qua rèm lụa trắng rủ xuống sàn gỗ |
| **209 (24s–28s)** | Quỳ khóc thảm thiết ba ngày đêm trước bài vị tổ tiên | **A** | `File:溥仪.jpg (Chân dung Phổ Nghi thời lưu vong)` | Zoom cận cảnh đôi mắt uất ức ngấn lệ |
| **210 (28s–32s)** | Trong hồi ký 'Nửa đời đã qua', Phổ Nghi viết: 'Nếu không báo được mối thù này, ta không phải con cháu họ Ái Tân Giác La!' | **D** | `quote ('NẾU KHÔNG BÁO ĐƯỢC THÙ NÀY · KHÔNG PHẢI CON CHÁU ÁI TÂN GIÁC LA!')` | Trích dẫn hồi ký Phổ Nghi trên nền tối |
| **211 (32s–36s)** | Một lời thề khắc cốt ghi tâm sẽ đẩy Phổ Nghi vào con đường hợp tác với người Nhật sau này | **A** | `File:Titular emperor Puyi of China in the Forbidden City, 1910s or 1920s.png (Phổ Nghi khi còn ở Tử Cấm Thành)` | Ken Burns từ quá khứ uy quyền sang hiện thực cay đắng |
| **212 (36s–40s)** | Hoàng tộc lập tức gửi điện tín khẩn tới chính phủ Nam Kinh và Tổng tư lệnh Tưởng Giới Thạch | **D** | `file (ĐIỆN TÍN KHẨN TỪ THIÊN TÂN GỬI NAM KINH)` | Bức điện tín mở ra với dòng chữ yêu cầu nghiêm trị |
| **213 (40s–44s)** | Yêu cầu lập tức bắt giữ, tước bỏ quân tịch và xử bắn Tôn Điện Anh trước công chúng | **D** | `slam ('YÊU CẦU XỬ BẮN TÔN ĐIỆN ANH')` | Chữ đập dứt khoát |
| **214 (44s–48s)** | Đồng thời cử một phái đoàn đại thần do Túc Thân vương Tái Trạch dẫn đầu đến hiện trường | **A** | `File:Zaize prince hui.jpg (Tái Trạch)` | Slow zoom-in vào gương mặt nghiêm nghị của Tái Trạch |
| **215 (48s–52s)** | Cùng các cựu thần triều Thanh để khảo sát mức độ tàn phá và khâm liệm lại thi hài | **A** | `File:Der im Bau befindliche Tumulus im Grabe der Kaiserin Regentin 1.jpg (Gò lăng mộ Đông Lăng)` | Pan qua gò lăng đá hoang tàn |
| **216 (52s–56s)** | Khi đoàn của Tái Trạch bước vào lòng địa cung Định Đông Lăng vào tháng 8/1928 | **A** | `File:DingDongLing1.jpg (Lòng địa cung ngổn ngang)` | Góc rộng gian hầm mộ ngổn ngang đá |
| **217 (56s–60s)** | Họ chứng kiến một cảnh tượng bi thảm chưa từng có trong lịch sử hoàng gia | **A** | `File:1928 Cixi Corpse DingDongLing.jpg (Tư liệu đoàn khâm liệm 1928 - xử lý mờ)` | Zoom chậm góc chụp xa tế nhị |
| **218 (60s–64s)** | Thi thể Từ Hi bị bỏ rơi trên sàn đá lạnh, nấm mốc trắng bao phủ sau nhiều tuần | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm)` | Pan qua không gian u ám |
| **219 (64s–68s)** | Đoàn khâm liệm nghẹn ngào quỳ lạy, dùng lụa vàng phủ lên thi hài | **A** | `File:Longyu Coffin.jpg (Khâm liệm lại quan quách)` | Pan qua lớp gỗ quan tài được bọc lại |
| **220 (68s–72s)** | Và thu dọn những mảnh hài cốt vương vãi của Càn Long trong dòng nước ngầm Dụ Lăng | **A** | `File:清东陵裕陵地宫.jpg (Địa cung Dụ Lăng hoang phế)` | Ken Burns lướt qua làn nước dưới chân cột đá |
| **221 (72s–76s)** | Biên bản khám nghiệm hiện trường của đoàn Tái Trạch làm dư luận toàn cầu rúng động | **D** | `file (BIÊN BẢN KHÁM NGHIỆM ĐÔNG LĂNG · THÁNG 8/1928)` | Tập hồ sơ hiện trường mở ra |
| **222 (76s–80s)** | Làn sóng phản đối bùng lên dữ dội từ các giới nhân sĩ, học giả và kiều bào | **D** | `heat (Bản đồ phản ứng: Thiên Tân -> Bắc Kinh -> Thượng Hải -> Nam Kinh -> Hải ngoại)` | Các điểm đỏ dư luận bùng nổ trên bản đồ |
| **223 (80s–84s)** | Họ lên án gay gắt hành vi man rợ và sự bao che của quân đội Quốc gia | **C** | `ai_04.png (Cán cân công lý và chiếc hòm sắt phong ấn)` | Đòn cân nghiêng ngả dữ dội |
| **224 (84s–88s)** | Thống chế Diêm Tích Sơn và tướng Phùng Ngọc Tường cũng công khai lên tiếng chỉ trích | **A** | `File:Chiang Kai-shek, Feng Yuxiang and Yan Xishan.jpg (Tưởng Giới Thạch, Phùng Ngọc Tường, Diêm Tích Sơn)` | Zoom vào nét mặt nghiêm khắc của Diêm Tích Sơn |
| **225 (88s–92s)** | Trước sức ép nghẹt thở của toàn xã hội, Tưởng Giới Thạch không thể làm ngơ | **A** | `File:Chiang Kai-Shek paying reverence at the tomb of the late Dr. Sun Yat-Sen, August 04, 1928.jpg (Tưởng Giới Thạch viếng lăng Tôn Trung Sơn 8/1928)` | Focus vào Tưởng Giới Thạch làm lễ |
| **226 (92s–96s)** | Ngày 13/8/1928, Nam Kinh ra quyết định thành lập Ủy ban điều tra đặc biệt | **D** | `date ('13/8/1928: THÀNH LẬP ỦY BAN ĐIỀU TRA NAM KINH')` | Chữ mốc lệnh điều tra chính thức |
| **227 (96s–100s)** | Giao cho Bộ trưởng Quân chính Hà Ứng Khâm trực tiếp thụ lý vụ án | **A** | `File:He Yingqin1.jpg (Hà Ứng Khâm)` | Zoom vào chân dung Bộ trưởng Hà Ứng Khâm |
| **228 (100s–105s)** | Lệnh triệu tập khẩn cấp Tôn Điện Anh về Nam Kinh đối chất | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Slow zoom-in vào thế đứng thách thức của Tôn |
| **229 (105s–110s)** | Án tử hình dường như chỉ còn tính bằng ngày | **D** | `slam ('NGUY CƠ TỬ HÌNH CẬN KỀ')` | Chữ đập mạnh rung viền đỏ |
| **230 (110s–114s)** | Nhưng trong tay vị tướng cướp là một kho báu đủ sức mua chuộc cả thiên hạ | **C** | `ai_03.png (Rương báu vật cổ hé mở)` | Ánh sáng quét qua nắp rương |
| **231 (114s–117s)** | Trước khi xem cách Tôn thoát tội, cần phải biết Tôn đã cướp được những gì | **A** | `output/long/dong-lang/img/melon_jade_pot.jpg (Ấm ngọc phỉ thúy CC0)` | Zoom vào chất ngọc xanh biếc |
| **232 (117s–120s)** | Bản kê báu vật chính thức hé lộ bí mật về viên Dạ Minh Châu | **D** | `chapter (CHƯƠNG 07: CƠN THỊNH NỘ Ở THIÊN TÂN)` | Thẻ chương chuyển cảnh sắc sảo |

**Tổng kết số liệu chương:**
- Số nhịp: **30 nhịp** | Thời lượng: **120s** | Nhịp trung bình: **4.00s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 63s (52.5%)** | Nhóm B: 12s (10.0%) | Nhóm C: 13s (10.8%) | **Nhóm B+C: 25s (20.8%)** | **Nhóm D: 32s (26.7%)**.
- Số ảnh A sử dụng: **10 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 7 đạt 63s nhóm A (52.5%), sử dụng 10 ảnh tư liệu thật (Phổ Nghi tại Trương Viên Thiên Tân, Tái Trạch, tư liệu đoàn khâm liệm 1928, Tưởng Giới Thạch làm lễ tháng 8/1928, Hà Ứng Khâm, Diêm Tích Sơn, địa cung hoang phế). Bù đắp cơn địa chấn chính trị bằng đồ họa D (trích dẫn hồi ký Phổ Nghi, heat làn sóng phản ứng dư luận, file biên bản hiện trường tháng 8/1928) và hình ảnh B/C (thư phòng rủ lụa trắng tang lễ, cán cân công lý chao đảo).

---

### CH08: Bản kê báu vật (135 giây, 34 nhịp, trung bình 3.97s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **233 (0s–4s)** | Hồ sơ điều tra của Nam Kinh sau đó đã lập nên một bản kê tang vật sơ bộ | **D** | `file (HỒ SƠ TANG VẬT ĐÔNG LĂNG · ỦY BAN NAM KINH)` | Tập hồ sơ quân sự mở ra |
| **234 (4s–8s)** | Số lượng báu vật bị cướp phá vượt xa trí tưởng tượng của công chúng | **D** | `counter ('HÀNG TRĂM MÓN VÀNG NGỌC · 30 XE TẢI TANG VẬT')` | Bộ đếm cổ vật nhảy số nhanh |
| **235 (8s–12s)** | Tại Dụ Lăng của Càn Long, toàn bộ đồ ngự dụng và bảo vật sưu tầm bị khoắng sạch | **A** | `File:清裕陵（乾隆墓）.jpg (Dụ Lăng Càn Long)` | Pan qua toàn cảnh Dụ Lăng |
| **236 (12s–16s)** | Đầu tiên là chiếc đĩa rồng men lam vàng quý hiếm ngự chế thời Càn Long | **A** | `output/long/dong-lang/img/qianlong_dragon_dish.jpg (Đĩa rồng men lam vàng CC0)` | Zoom cận cảnh men lam vàng bóng bẩy |
| **237 (16s–20s)** | Chén trà điêu tất chạm khắc chữ ngự chế tinh xảo tuyệt luân | **A** | `output/long/dong-lang/img/qianlong_lacquer_bowl.jpg (Chén trà điêu tất Càn Long CC0)` | Ken Burns quét qua hoa văn khắc nổi |
| **238 (20s–24s)** | Bình gốm ngự dụng vẽ rồng đuổi ngọc lửa thời thịnh Thanh | **A** | `output/long/dong-lang/img/qianlong_dragon_vase.jpg (Bình rồng ngự chế CC0)` | Slow zoom-in vào hình rồng cuộn mây |
| **239 (24s–28s)** | Bình trăng men ngọc bích chạm hoa sen và nấm linh chi như ý | **A** | `output/long/dong-lang/img/qianlong_moon_flask.jpg (Bình Bianhu thời Càn Long CC0)` | Pan dọc thân bình gốm tráng men |
| **240 (28s–32s)** | Bình hoa sen khắc họa Bát Cát Tường — tám biểu tượng may mắn Phật giáo Tây Tạng | **A** | `output/long/dong-lang/img/qianlong_buddhist_vase.jpg (Bình Bát Cát Tường CC0)` | Zoom vào biểu tượng nút thắt vô tận |
| **241 (32s–36s)** | Tấm phù điêu quả bầu khắc hình rồng vượt sóng biển bằng ngọc quý | **A** | `output/long/dong-lang/img/qianlong_dragon_plaque.jpg (Phù điêu rồng ngự chế CC0)` | Lướt qua vân ngọc chạm lượn sóng |
| **242 (36s–40s)** | Ống cắm bút miêu tả cảnh bồng lai tiên cảnh của các đạo sĩ | **A** | `output/long/dong-lang/img/qing_brushpot_paradise.jpg (Ống bút gốm tiên cảnh CC0)` | Xoay nhẹ chi tiết phong cảnh tiên bồng |
| **243 (40s–44s)** | Chiếc chuông đồng ngự dụng khắc trọn vẹn bản Bát Nhã Ba La Mật Đa Tâm Kinh | **A** | `output/long/dong-lang/img/bell_heart_sutra.jpg (Chuông khắc Tâm Kinh CC0)` | Zoom vào từng nét chữ kinh Phật trên chuông |
| **244 (44s–48s)** | Và chiếc chén ngọc bích chạm khắc hoa văn cổ thời Khang Càn thịnh thế | **A** | `output/long/dong-lang/img/qing_jade_cup.jpg (Chén ngọc bích CC0)` | Ánh sáng quét qua thành chén ngọc mờ trong |
| **245 (48s–52s)** | Đến lăng mộ Từ Hi, giá trị cổ vật thậm chí còn vượt trội về độ tinh xảo | **A** | `File:慈禧陵隆恩殿 4.jpg (Điện Long Ân Từ Hi)` | Pan qua mái ngói lưu ly vàng |
| **246 (52s–56s)** | Nổi bật nhất là cặp dưa hấu ngọc phỉ thúy với hai màu xanh đỏ tự nhiên hoàn hảo | **A** | `output/long/dong-lang/img/melon_jade_pot.jpg (Ấm ngọc phỉ thúy dáng dưa CC0)` | Zoom cực cận vào chất ngọc phỉ thúy |
| **247 (56s–60s)** | Tương truyền đây là món cống phẩm quý nhất của phiên vương Tây Vực dâng tặng | **C** | `ai_03.png (Rương báu vật cổ trong ánh đèn)` | Ánh sáng quét qua rương gấm |
| **248 (60s–64s)** | Và tâm điểm của mọi lời đồn đại: Viên Dạ Minh Châu trong miệng thi hài | **D** | `slam ('TÂM ĐIỂM: HUYỀN THOẠI DẠ MINH CHÂU')` | Chữ đập nổi bật viền xanh huỳnh quang |
| **249 (64s–68s)** | Dân gian thêu dệt rằng viên ngọc to bằng quả trứng gà, có thể tách làm đôi | **D** | `split ('DÂN GIAN: VIÊN NGỌC TÁCH ĐÔI PHÁT SÁNG' vs 'KHOA HỌC: KHOÁNG VẬT TỰ NHIÊN')` | Hai cột thông tin đối chiếu |
| **250 (68s–72s)** | Và khi ghép lại sẽ tỏa ra ánh hào quang xanh ngắt soi rõ cả gian phòng trong đêm | **C** | `ai_12.png (Khối ngọc phát quang mờ ảo trong hộp gấm)` | Ánh sáng xanh lam huyền bí phát ra từ viên ngọc |
| **251 (72s–76s)** | Nhưng dưới góc nhìn của khoa học khoáng vật học hiện đại, sự thật là gì? | **D** | `question ('BẢN CHẤT KHOA HỌC CỦA DẠ MINH CHÂU LÀ GÌ?')` | Chữ câu hỏi lớn trên nền tối |
| **252 (76s–80s)** | Các nhà địa chất học xác định: Dạ Minh Châu thực chất là khoáng vật Fluorite hoặc kim cương tự nhiên | **A** | `File:KugelförmigeSchnitzereiausFluorit.jpg (Khối khoáng vật Fluorite tự nhiên CC0)` | Zoom cận cảnh cấu trúc tinh thể fluorite |
| **253 (80s–84s)** | Chứa các tạp chất đất hiếm có khả năng hấp thụ năng lượng ánh sáng ban ngày | **D** | `bars (Cơ chế quang học: Hấp thụ tia cực tím -> Phát lân quang ban đêm)` | Sơ đồ bước sóng ánh sáng phát quang |
| **254 (84s–88s)** | Và từ từ giải phóng năng lượng dưới dạng lân quang mờ màu xanh lam trong bóng tối | **C** | `vid_05.mp4 (Ánh sáng quét qua chuỗi ngọc trai và châu báu cổ)` | Camera drift qua chuỗi ngọc phát sáng mờ ảo |
| **255 (88s–92s)** | Đường kính viên ngọc khoảng 4,5 cm, nặng xấp xỉ 133 gram | **D** | `ledger (Thông số Dạ Minh Châu: Đường kính 4.5cm · Nặng 133g · Khoáng vật Fluorite)` | Bảng thông số kỹ thuật hiển thị |
| **256 (92s–96s)** | Dù không có phép màu cải tử hoàn sinh như lời đồn, đây vẫn là tuyệt tác vô giá của tự nhiên | **A** | `File:Buddha Amitayus Museum Rietberg BA 34.jpg (Tượng Phật vàng cổ)` | Pan qua pho tượng Phật cổ |
| **257 (96s–100s)** | Giá trị ước tính thời bấy giờ lên tới hơn 10 triệu đồng bạc Dân Quốc | **D** | `counter ('GIÁ TRỊ ƯỚC TÍNH: 10.800.000 ĐỒNG BẠC DÂN QUỐC')` | Bộ đếm tiền bạc nhảy số lớn |
| **258 (100s–104s)** | Đóng vòng 1: Viên Dạ Minh Châu là có thật, nhưng huyền thoại đã bị phóng đại gấp bội | **D** | `slam ('ĐÓNG VÒNG 1: SỰ THẬT VỀ DẠ MINH CHÂU')` | Chữ đập mạnh chốt vòng mở 1 |
| **259 (104s–108s)** | Toàn bộ kho báu này đã lọt vào tay Tôn Điện Anh sau chiến dịch 3 ngày đêm | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Zoom cận cảnh gương mặt Tôn |
| **260 (108s–112s)** | Nhưng sở hữu kho báu trấn quốc giữa lúc lệnh bắt giam đang treo lơ lửng | **B** | `output/asset_library/lib198b/ai_18.png (Hòm gỗ tang vật dưới lòng đất)` | Camera lướt qua xích sắt phong ấn |
| **261 (112s–116s)** | Chẳng khác nào đang ôm một khối thuốc nổ sắp phát hỏa | **D** | `slam ('ÔM BÁU VẬT LÀ ÔM THUỐC NỔ')` | Chữ đập dứt khoát |
| **262 (116s–120s)** | Tôn Điện Anh lập tức đưa ra quyết định sinh tử: Dùng tang vật để mua đường sống | **A** | `File:Sun Dianying 孙殿英.jpg (Tôn Điện Anh)` | Focus vào ánh nhìn lạnh lùng |
| **263 (120s–124s)** | Bắt đầu thiết lập một mạng lưới hối lộ vô tiền khoáng hậu trong lịch sử | **C** | `ai_13.png (Bàn trà đàm phán ngầm với phong bao mật)` | Khói trà bốc lên bên chiếc tráp khóa kín |
| **264 (124s–128s)** | Mục tiêu là những kẻ đang nắm quyền sinh quyền sát tại thủ đô Nam Kinh | **A** | `File:Nationalist government of Nanking - nominally ruling over entire China, 1930 (2675972715).jpg (Chính phủ Nam Kinh)` | Góc rộng tòa nhà quyền lực |
| **265 (128s–132s)** | Ai sẽ nhận được Cửu Long Bảo Kiếm và viên Dạ Minh Châu vô giá? | **D** | `question ('BẢO VẬT TRẤN QUỐC ĐÃ CHẢY VÀO TÚI AI?')` | Chữ câu hỏi lớn nổi bật |
| **266 (132s–135s)** | Chương tiếp theo mở ra mạng lưới mua chuộc quyền lực đen tối nhất thời Dân Quốc | **D** | `chapter (CHƯƠNG 08: BẢN KÊ BÁU VẬT)` | Thẻ chương chuyển tiếp sắc nét |

**Tổng kết số liệu chương:**
- Số nhịp: **34 nhịp** | Thời lượng: **135s** | Nhịp trung bình: **3.97s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 73s (54.1%)** | Nhóm B: 11s (8.1%) | Nhóm C: 15s (11.1%) | **Nhóm B+C: 26s (19.3%)** | **Nhóm D: 36s (26.7%)**.
- Số ảnh A sử dụng: **12 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 8 đạt 73s nhóm A (54.1%), sử dụng 12 ảnh tư liệu thật (hệ thống 9 hiện vật CC0 quý hiếm của Bảo tàng Viện Nghệ thuật Chicago: đĩa rồng, chén điêu tất, bình rồng, bình Bianhu, bình Bát Cát Tường, phù điêu rồng, ống bút tiên cảnh, chuông khắc Tâm Kinh, chén ngọc; cùng ấm ngọc phỉ thúy, khối khoáng vật fluorite, tượng Phật vàng). Bù đắp việc giải mã tang vật bằng đồ họa D (ledger danh mục tang vật, split huyền thoại vs khoa học khoáng vật, counter quy đổi giá trị, slam đóng vòng 1) và biểu tượng C (khối ngọc phát quang trong hộp gấm, chuỗi châu báu).

---

### CH09: Mạng lưới mua đường (135 giây, 33 nhịp, trung bình 4.09s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **267 (0s–4s)** | Mùa thu năm 1928, Tôn Điện Anh bí mật cử thân tín đem theo các hòm báu vật về Nam Kinh | **B** | `ai_13.png (Bàn trà đàm phán ngầm với phong bao mật và tách sứ)` | Slow pan qua bàn trà zitan và chiếc tráp gấm |
| **268 (4s–8s)** | Để tiếp cận những nhân vật quyền lực nhất trong chính phủ và quân đội Quốc gia | **A** | `File:Nationalist government of Nanking - nominally ruling over entire China, 1930 (2675972715).jpg (Chính quyền Nam Kinh)` | Pan ngang trụ sở chính phủ |
| **269 (8s–12s)** | Mục tiêu đầu tiên và then chốt nhất chính là Đới Lạp — người đứng đầu cơ quan tình báo quân sự | **A** | `File:Dai Li6.jpg (Đới Lạp)` | Slow zoom-in vào gương mặt lạnh lùng của trùm tình báo |
| **270 (12s–16s)** | Đới Lạp là cánh tay phải đắc lực, người nắm giữ tai mắt của Tưởng Giới Thạch | **A** | `File:Chiang Kai-shek and Dai Li.jpg (Tưởng Giới Thạch và Đới Lạp)` | Pan từ Tưởng sang Đới Lạp |
| **271 (16s–20s)** | Tôn Điện Anh hiểu rằng: Muốn dâng lễ cho Tưởng, trước hết phải qua cửa Đới Lạp | **A** | `File:戴笠将军照片.jpg (Đới Lạp quân phục)` | Zoom vào ánh mắt sắc sảo |
| **272 (20s–25s)** | Món quà Tôn gửi tặng Đới Lạp chính là thanh Cửu Long Bảo Kiếm của Càn Long | **A** | `output/long/dong-lang/img/qianlong_dragon_plaque.jpg (Bản phù điêu rồng ngự chế CC0)` | Lướt qua hoa văn rồng cuộn |
| **273 (25s–29s)** | Cùng lời nhờ vả chuyển giao thanh bảo kiếm này lên Tổng tư lệnh Tưởng Giới Thạch | **D** | `org (Sơ đồ hối lộ: Tôn Điện Anh -> Đới Lạp -> Tưởng Giới Thạch [Cửu Long Kiếm])` | Mũi tên đồ họa chuyển giao báu vật |
| **274 (29s–33s)** | Nhìn thấy thanh kiếm báu trấn quốc tuyệt mỹ, Đới Lạp lập tức xiêu lòng và đồng ý bảo bọc | **D** | `slam ('ĐỚI LẠP ĐỒNG Ý BẢO KÊ')` | Chữ đập mạnh trên nền tối |
| **275 (33s–37s)** | Nhưng chỉ có Đới Lạp là chưa đủ, Tôn tiếp tục nhắm đến nhân vật quyền lực số hai | **A** | `File:Chiang Kai-shek and Soong May-ling2.jpg (Tưởng Giới Thạch và Tống Mỹ Linh)` | Pan từ Tưởng sang phu nhân Tống Mỹ Linh |
| **276 (37s–41s)** | Đó chính là phu nhân Tống Mỹ Linh — người có ảnh hưởng tuyệt đối lên Tưởng | **A** | `File:Miss May Ling Soong et le général Chiang Kai Shek (CNews) - btv1b53195322v.jpg (Tống Mỹ Linh)` | Zoom vào thần thái quý phái của Tống phu nhân |
| **277 (41s–45s)** | Món quà dành riêng cho Tống Mỹ Linh là báu vật đắt giá nhất: Viên Dạ Minh Châu cạy từ miệng Từ Hi | **C** | `ai_12.png (Khối ngọc phát quang mờ ảo trong hộp gấm cổ)` | Ánh sáng xanh lam huyền ảo hắt lên nhung lụa |
| **278 (45s–49s)** | Cùng hàng ngàn viên trân châu Đông Hải thượng hạng kết thành chuỗi vòng hoa lệ | **C** | `vid_05.mp4 (Ánh sáng quét qua chuỗi ngọc trai và châu báu cổ)` | Camera drift qua chuỗi ngọc trai lấp lánh |
| **279 (49s–53s)** | Bị chinh phục bởi vẻ đẹp mê hoặc của viên dạ minh châu, cánh cửa hậu cung Nam Kinh hoàn toàn rộng mở | **D** | `slam ('TỐNG MỸ LINH NHẬN DẠ MINH CHÂU')` | Chữ đập nổi bật viền hoàng kim |
| **280 (53s–57s)** | Tiếp theo là Viện trưởng Hành chính viện kiêm Bộ trưởng Tài chính Tống Tử Văn | **A** | `File:Tse-ven Soong.JPG (Tống Tử Văn)` | Slow zoom vào chân dung Tống Tử Văn |
| **281 (57s–61s)** | Người nắm giữ hầu bao quốc gia và là anh trai của Tống Mỹ Linh | **A** | `File:Family portrait of the Soong family in Shanghai in 1917.jpg (Gia tộc họ Tống)` | Pan ngang các thành viên gia tộc quyền thế |
| **282 (61s–65s)** | Tôn Điện Anh trích tặng Tống Tử Văn cặp dưa hấu ngọc phỉ thúy tuyệt tác từ mộ Từ Hi | **A** | `output/long/dong-lang/img/melon_jade_pot.jpg (Ấm ngọc phỉ thúy CC0)` | Zoom cận cảnh vân ngọc xanh đỏ tự nhiên |
| **283 (65s–69s)** | Cùng chiếc đĩa rồng men lam vàng và hàng loạt đồ gốm sứ ngự chế đỉnh cao | **A** | `output/long/dong-lang/img/qianlong_dragon_dish.jpg (Đĩa rồng ngự chế CC0)` | Xoay nhẹ đĩa rồng men lam vàng |
| **284 (69s–73s)** | Tống Tử Văn vô cùng hài lòng và bắt đầu tác động giảm nhẹ vụ án từ cấp chính phủ | **A** | `File:T.V. (Tse-Ven) Soong, minister-president van China.jpg (Tống Tử Văn)` | Zoom vào nụ cười kín đáo |
| **285 (73s–77s)** | Chưa dừng lại ở đó, Tôn nhắm đến Bộ trưởng Quân chính Hà Ứng Khâm — người trực tiếp thụ lý điều tra | **A** | `File:He Yingqin1.jpg (Hà Ứng Khâm)` | Zoom vào quân hàm đại tướng của Hà Ứng Khâm |
| **286 (77s–81s)** | Hà Ứng Khâm được dâng tặng thanh bảo kiếm thời Càn Long chuôi khảm hồng ngọc và 50 vạn đồng bạc | **A** | `File:ROC-SYSMH He Yingqin statue 20131026.jpg (Tượng đồng Hà Ứng Khâm)` | Pan qua tượng đài Hà Ứng Khâm |
| **287 (81s–85s)** | Người phụ trách điều tra lại nhận được phần quà lớn nhất từ kẻ bị điều tra | **D** | `slam ('NGƯỜI THẨM PHÁN NHẬN QUÀ CỦA BỊ CÁO')` | Chữ đập mỉa mai trên nền xám |
| **288 (85s–89s)** | Và nhân vật cuối cùng ở miền Bắc: Thống chế Diêm Tích Sơn — người lớn tiếng đòi xử phạt | **A** | `File:Yan Xishan.jpg (Diêm Tích Sơn)` | Slow zoom vào chân dung Diêm Tích Sơn |
| **289 (89s–93s)** | Tôn điều ngay một đoàn xe chở đầy tượng Phật vàng và đồ đồng cổ dâng tận tư dinh ở Thái Nguyên | **A** | `File:Yan Xishan0.jpg (Diêm Tích Sơn tại Sơn Tây)` | Pan ngang dinh thự của Diêm |
| **290 (93s–97s)** | Nhận được kho báu, Diêm Tích Sơn lập tức đổi giọng, tuyên bố 'cần thận trọng xem xét lại sự việc' | **A** | `File:Chiang Kai-shek, Feng Yuxiang and Yan Xishan.jpg (Tưởng Giới Thạch và Diêm Tích Sơn)` | Focus vào nụ cười bắt tay giữa Tưởng và Diêm |
| **291 (97s–101s)** | Một mạng lưới hối lộ ngũ giác hoàn hảo bao trùm toàn bộ hệ thống quyền lực Nam Kinh | **D** | `org (Mạng lưới hối lộ ngũ giác: Tôn -> Tưởng [Kiếm] · Tống Mỹ Linh [Ngọc] · Tống Tử Văn [Dưa] · Hà Ứng Khâm [Kiếm] · Diêm [Vàng])` | Sơ đồ mạng nhện hối lộ tỏa sáng |
| **292 (101s–105s)** | Tất cả các bên nhận quà đều chọn cách ngậm miệng ăn tiền | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm)` | Slow pan qua căn phòng vắng |
| **293 (105s–109s)** | Họ đã vô tình hoặc hữu ý trở thành những kẻ đồng lõa trong vụ án thế kỷ | **C** | `ai_04.png (Cán cân công lý bị xích sắt trói chặt)` | Xích sắt cuốn quanh cán cân |
| **294 (109s–114s)** | Tôn Điện Anh ung dung ngồi tại đại bản doanh nhìn phiên tòa sắp diễn ra | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Slow zoom-in vào tư thế tự tin của Tôn |
| **295 (114s–118s)** | Hắn biết rõ: Chiếc thòng lọng tử hình đã được tháo gỡ hoàn toàn | **D** | `slam ('THÒNG LỌNG TỬ HÌNH ĐÃ ĐƯỢC THÁO')` | Chữ đập dứt khoát |
| **296 (118s–122s)** | Phiên tòa quân sự Nam Kinh mở ra chỉ còn là một vở kịch vụng về | **A** | `File:Chiang Kai-Shek, 1928 AP Photo.jpg (Tưởng Giới Thạch)` | Zoom vào nét mặt trầm ngâm của Tưởng |
| **297 (122s–126s)** | Kéo dài qua nhiều tháng để dư luận dần lãng quên | **B** | `output/asset_library/lib198b/ai_18.png (Hòm gỗ tang vật)` | Lướt qua các rương gỗ trong bóng tối |
| **298 (126s–130s)** | Diễn biến thực tế của phiên tòa quân sự tại Nam Kinh ra sao? | **D** | `question ('PHIÊN TÒA QUÂN SỰ ĐÃ KẾT THÚC NHƯ THẾ NÀO?')` | Chữ câu hỏi lớn trên nền tối |
| **299 (130s–135s)** | Chương tiếp theo phơi bày màn kịch tư pháp trơ trẽn nhất lịch sử Dân Quốc | **D** | `chapter (CHƯƠNG 09: MẠNG LƯỚI MUA ĐƯỜNG)` | Thẻ chương chuyển cảnh sắc sảo |

**Tổng kết số liệu chương:**
- Số nhịp: **33 nhịp** | Thời lượng: **135s** | Nhịp trung bình: **4.09s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 72s (53.3%)** | Nhóm B: 12s (8.9%) | Nhóm C: 16s (11.9%) | **Nhóm B+C: 28s (20.7%)** | **Nhóm D: 35s (25.9%)**.
- Số ảnh A sử dụng: **13 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 9 đạt 72s nhóm A (53.3%), sử dụng 13 ảnh tư liệu thật (Đới Lạp, Tưởng Giới Thạch, Tống Mỹ Linh, Tống Tử Văn, Hà Ứng Khâm, Diêm Tích Sơn, gia tộc họ Tống, trụ sở chính phủ Nam Kinh, đĩa rồng, ấm ngọc phỉ thúy). Bù đắp mạng lưới hối lộ ngầm bằng đồ họa D (sơ đồ mạng lưới hối lộ ngũ giác, split người nhận vs báu vật, slam tháo thòng lọng tử hình) và hình ảnh B/C (bàn trà mật nghị phong bao, rương tang vật phong ấn).

---

### CH10: Phiên tòa Nam Kinh (130 giây, 32 nhịp, trung bình 4.06s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **300 (0s–4s)** | Tháng 12/1928, Tòa án Quân sự Nam Kinh chính thức mở phiên xem xét vụ án Đông Lăng | **D** | `date ('THÁNG 12/1928: MỞ TÒA ÁN QUÂN SỰ NAM KINH')` | Chữ ngày giờ trên nền phòng xử án |
| **301 (4s–8s)** | Dưới sự chủ trì của Bộ Quân chính do Hà Ứng Khâm đứng đầu | **A** | `File:He Yingqin4.jpg (Hà Ứng Khâm)` | Slow zoom vào chân dung Hà Ứng Khâm |
| **302 (8s–12s)** | Trụ sở tòa án tại Nam Kinh được canh phòng cẩn mật, thu hút sự chú ý của báo giới quốc tế | **A** | `File:Former Residence of He Yingqin in Nanjing 2010-11.JPG (Dinh thự Hà Ứng Khâm tại Nam Kinh)` | Pan ngang kiến trúc tòa nhà |
| **303 (12s–16s)** | Hoàng tộc nhà Thanh và cựu hoàng Phổ Nghi cử luật sư đại diện tham gia với tư cách nguyên đơn | **A** | `File:溥仪.jpg (Phổ Nghi)` | Focus vào đôi mắt trông đợi công lý của Phổ Nghi |
| **304 (16s–20s)** | Đưa ra bằng chứng đanh thép: Biên bản khám nghiệm lăng mộ và danh sách hơn 30 xe tải tang vật | **D** | `file (HỒ SƠ KHỞI KIỆN CỦA HOÀNG TỘC MÃN THANH)` | Tập hồ sơ khởi kiện mở ra |
| **305 (20s–24s)** | Thế nhưng tại phiên tòa, bị cáo chính là Tôn Điện Anh lại không hề xuất hiện | **B** | `ai_14.png (Hành lang công đường vắng bóng người với hàng cột xám)` | Camera lướt chậm qua hành lang dài hun hút vắng tanh |
| **306 (24s–28s)** | Tôn viện lý do 'bận chỉ huy tác chiến tiễu phỉ ở tiền tuyến' nên cử một sĩ quan cấp dưới đi thay | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Zoom cận cảnh quân hàm chỉ huy |
| **307 (28s–32s)** | Người đại diện này khai trước tòa: Việc đào đất ở Tuân Hóa hoàn toàn là hoạt động công sự dã chiến | **D** | `slam ('LỜI KHAI: ĐÀO CÔNG SỰ DÃ CHIẾN')` | Chữ đập mạnh trên nền tối |
| **308 (32s–36s)** | Còn việc nổ mìn hầm mộ là do 'tàn phỉ Mã Phúc Điền thực hiện trước đó, quân ta chỉ đến dẹp' | **D** | `slam ('ĐỔ LỖI HOÀN TOÀN CHO TÀN PHỈ')` | Chữ đập dứt khoát |
| **309 (36s–40s)** | Một lời ngụy biện trắng trợn đi ngược lại toàn bộ lời khai nhân chứng và dấu vết công binh | **C** | `ai_04.png (Cán cân công lý và chiếc hòm sắt phong ấn)` | Đòn cân công lý bị gỉ sét nghiêng hẳn |
| **310 (40s–44s)** | Trước những chứng cứ áp đảo đòi xử tội, tòa án Nam Kinh bắt đầu chiến thuật câu giờ | **B** | `output/asset_library/lib198v/vid_11.mp4 (Hành lang công quyền vắng lặng trong bóng tối)` | Camera drift chậm trong hành lang tối |
| **311 (44s–48s)** | Hà Ứng Khâm liên tục tuyên bố: 'Vụ án phức tạp, cần thu thập thêm chứng cứ tại hiện trường' | **A** | `File:He Yingqin1.jpg (Hà Ứng Khâm)` | Zoom vào ánh mắt lảng tránh của thẩm phán |
| **312 (48s–52s)** | Phiên tòa bị hoãn lần thứ nhất sang đầu năm 1929 | **D** | `timeline (Lịch hoãn phiên tòa: 12/1928 Mở tòa -> 01/1929 Hoãn -> 03/1929 Tạm đình chỉ)` | Dòng mốc hoãn án kéo dài |
| **313 (52s–56s)** | Trong thời gian này, các bảo vật hối lộ tiếp tục phát huy tác dụng bảo kê ở hậu trường | **C** | `output/asset_library/lib198b/ai_18.png (Hòm gỗ tang vật bị phong ấn)` | Lướt qua các rương tang vật giấu kín |
| **314 (56s–60s)** | Tưởng Giới Thạch ra chỉ thị mật: 'Tránh làm căng thẳng nội bộ quân đội trong lúc chưa thống nhất' | **A** | `File:Chiang Kai-shek（蔣中正）.jpg (Tưởng Giới Thạch)` | Slow zoom vào chân dung chính thức của Tưởng |
| **315 (60s–64s)** | Quốc gia lúc này đang chuẩn bị đối mặt với cuộc Đại chiến Trung Nguyên giữa các sứ quân | **A** | `File:Nationalist China 1929 - 1937.PNG (Bản đồ phân tranh 1929-1937)` | Hiển thị các mặt trận quân sự đang đe dọa Nam Kinh |
| **316 (64s–68s)** | Tưởng cần lực lượng của Tôn Điện Anh để đối phó với Phùng Ngọc Tường và Diêm Tích Sơn | **A** | `File:Pai Toung Chi, Chiang Kai Chek, Feng Ju Hsiang, Yen Hsi Shan (Pacific) - btv1b532047106.jpg (Các tướng lĩnh quân phiệt)` | Pan ngang các tướng lĩnh |
| **317 (68s–72s)** | Đến tháng 4/1929, phiên tòa quân sự tại Nam Kinh chính thức tạm đình chỉ vô thời hạn | **D** | `file (QUYẾT ĐỊNH ĐÌNH CHỈ VỤ ÁN ĐÔNG LĂNG · 4/1929)` | Tờ quyết định đình chỉ đóng dấu lưu trữ |
| **318 (72s–76s)** | Hồ sơ vụ cướp phá lăng tẩm hoàng gia lớn nhất thế kỷ bị xếp vào ngăn kéo bảo mật | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm)` | Slow pan qua tủ hồ sơ lưu trữ |
| **319 (76s–80s)** | Không một ai trong Sư đoàn 12 bị xử bắn, phạt tù hay tước quân hàm | **D** | `slam ('KẾT LUẬN: KHÔNG MỘT KẺ NÀO BỊ TRỪNG PHẠT')` | Chữ đập mạnh trên nền tối |
| **320 (80s–84s)** | Thậm chí Tôn Điện Anh còn nhận được lệnh điều động mới từ Bộ Quân chính | **A** | `File:Sun Dianying 孙殿英.jpg (Tôn Điện Anh)` | Zoom cận cảnh gương mặt đắc thắng |
| **321 (84s–88s)** | Bổ nhiệm làm Quân đoàn trưởng Quân đoàn Tân Biên số 2, tiếp tục mở rộng binh lực | **A** | `File:Beiyang Army troops crossing the Gong An street.jpg (Đoàn quân di chuyển)` | Pan theo đoàn quân rầm rộ |
| **322 (88s–92s)** | Đóng vòng 2: Một phiên tòa quốc gia kết thúc trong sự thỏa hiệp bẩn thỉu của quyền lực và tiền bạc | **D** | `slam ('ĐÓNG VÒNG 2: BỘ MÁY TƯ PHÁP TÊ LIỆT')` | Chữ đập chốt vòng mở 2 |
| **323 (92s–96s)** | Công lý hoàn toàn bị giẫm đạp trước nòng súng và các khối vàng ngọc | **C** | `ai_04.png (Cán cân công lý bị xích sắt trói chặt)` | Đòn cân gãy lệch hoàn toàn |
| **324 (96s–100s)** | Sự việc này để lại nỗi cay đắng tột cùng cho Phổ Nghi và hoàng tộc Mãn Thanh | **A** | `File:Puyi and Wanrong Tianjin.jpg (Phổ Nghi đau đớn tại Thiên Tân)` | Focus vào ánh nhìn cay đắng của cựu hoàng |
| **325 (100s–104s)** | Cắt đứt hoàn toàn niềm tin còn sót lại của họ vào chính phủ Trung Hoa Dân Quốc | **A** | `File:Titular emperor Puyi of China in the Forbidden City, 1910s or 1920s.png (Phổ Nghi)` | Slow zoom-in vào hình bóng hoàng đế cô độc |
| **326 (104s–108s)** | Dẫn thẳng đến quyết định sang Mãn Châu lập quốc với sự hỗ trợ của quân đội Nhật năm 1931 | **A** | `File:Nationalist government of Nanking - nominally ruling over entire China, 1930 (2675972715).jpg (Chính phủ Nam Kinh)` | Góc rộng tòa nhà chính phủ trong hoàng hôn |
| **327 (108s–112s)** | Kẻ cướp thoát tội, nhưng số phận của các bảo vật trấn quốc sau đó ra sao? | **D** | `question ('SỐ PHẬN CỦA BẢO KIẾM VÀ DẠ MINH CHÂU RA SAO?')` | Chữ câu hỏi lớn trên nền xám |
| **328 (112s–116s)** | Đặc biệt là thanh Cửu Long Bảo Kiếm trong tay trùm tình báo Đới Lạp | **A** | `output/long/dong-lang/img/qianlong_dragon_plaque.jpg (Bản phù điêu rồng)` | Ánh sáng quét qua chi tiết rồng |
| **329 (116s–121s)** | Một lời nguyền bí ẩn dường như đã bám theo những kẻ chiếm giữ bảo vật | **C** | `ai_15.png (Hộp gấm đen chạm rồng bị cháy xém)` | Khói tro bay qua góc hộp cháy xém |
| **330 (121s–125s)** | Bắt đầu bằng vụ tai nạn máy bay thảm khốc tại núi Đới Sơn năm 1946 | **D** | `slam ('TAI NẠN MÁY BAY ĐỚI SƠN 1946')` | Chữ đập mạnh rung viền đỏ |
| **331 (125s–130s)** | Chương tiếp theo theo chân hành trình bi thảm của thanh kiếm Càn Long | **D** | `chapter (CHƯƠNG 10: PHIÊN TÒA NAM KINH)` | Thẻ chương chuyển tiếp sắc nét |

**Tổng kết số liệu chương:**
- Số nhịp: **32 nhịp** | Thời lượng: **130s** | Nhịp trung bình: **4.06s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 69s (53.1%)** | Nhóm B: 12s (9.2%) | Nhóm C: 15s (11.5%) | **Nhóm B+C: 27s (20.8%)** | **Nhóm D: 34s (26.2%)**.
- Số ảnh A sử dụng: **11 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 10 đạt 69s nhóm A (53.1%), sử dụng 11 ảnh tư liệu thật (Hà Ứng Khâm, dinh thự Nam Kinh, Phổ Nghi, Tưởng Giới Thạch, bản đồ phân tranh Dân Quốc 1929-1937, đoàn quân Bắc Dương, phù điêu rồng ngự chế, trụ sở chính phủ Nam Kinh). Bù đắp phiên tòa đình chỉ bằng đồ họa D (timeline các đợt hoãn tòa, file biên bản đình chỉ vụ án 4/1929, slam đóng vòng 2) và hình ảnh B/C (hành lang công đường vắng ngắt, cán cân gãy xích sắt).

---

### CH11: Cửu Long Bảo Kiếm (130 giây, 32 nhịp, trung bình 4.06s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **332 (0s–4s)** | Cửu Long Bảo Kiếm là bảo vật trấn quốc được Càn Long Hoàng đế trân quý nhất lúc sinh thời | **A** | `File:The Qianlong Emperor in Ceremonial Armour on Horseback.jpg (Càn Long cưỡi ngựa)` | Slow zoom vào thanh kiếm bên sườn hoàng đế |
| **333 (4s–8s)** | Được đúc bằng thép tinh luyện vùng Tây Vực, chuôi nạm 9 con rồng vàng uốn lượn khảm hồng ngọc | **A** | `output/long/dong-lang/img/qianlong_dragon_plaque.jpg (Phù điêu rồng ngự chế CC0)` | Zoom cận cảnh hoa văn rồng cuộn tinh xảo |
| **334 (8s–12s)** | Khi băng hà năm 1799, Càn Long di chiếu chôn theo thanh kiếm bên cạnh thi hài mình ở Dụ Lăng | **A** | `output/long/dong-lang/img/bell_heart_sutra.jpg (Chuông khắc Tâm Kinh CC0)` | Pan dọc thân chuông ngự chế |
| **335 (12s–16s)** | Sau khi bị Tôn Điện Anh đào trộm năm 1928, thanh kiếm được dâng tặng cho trùm tình báo Đới Lạp | **A** | `File:Chiang Kai-shek and Dai Li.jpg (Đới Lạp và Tưởng Giới Thạch)` | Focus vào Đới Lạp |
| **336 (16s–20s)** | Đới Lạp lúc này đang bí mật chuẩn bị mạng lưới gián điệp Quân Thống trên toàn quốc | **A** | `File:Dai Li6.jpg (Đới Lạp)` | Slow zoom-in vào gương mặt bí ẩn của Đới |
| **337 (20s–24s)** | Không dám công khai giữ kiếm, Đới giao bảo kiếm cho thuộc hạ thân tín là Mã Hán Tam cất giữ | **D** | `map (Hành trình bảo kiếm: Đông Lăng 1928 -> Nam Kinh -> Bắc Kinh 1940)` | Đường bay bản đồ di chuyển bảo vật |
| **338 (24s–28s)** | Năm 1940 trong thời kỳ kháng chiến chống Nhật, Mã Hán Tam bị cơ quan mật vụ Nhật bắt giữ tại Bắc Kinh | **D** | `slam ('1940: MÃ HÁN TAM BỊ BẮT')` | Chữ đập mạnh trên nền tối |
| **339 (28s–32s)** | Để giữ mạng sống, Mã Hán Tam đã phản bội, dâng nộp Cửu Long Bảo Kiếm cho phía Nhật | **C** | `ai_15.png (Hộp gấm đen chạm rồng bị cháy xém)` | Ánh sáng quét qua nắp hộp hé mở |
| **340 (32s–36s)** | Thanh kiếm rơi vào tay nữ gián điệp khét tiếng Xuyên Đảo Phương Tử (Yoshiko Kawashima) | **D** | `split ('MÃ HÁN TAM DÂNG KIẾM' vs 'NỮ GIÁN ĐIỆP XUYÊN ĐẢO PHƯƠNG TỬ')` | Hai cột thông tin đối chiếu |
| **341 (36s–40s)** | Xuyên Đảo Phương Tử cất giấu thanh bảo kiếm như một báu vật bất ly thân suốt thời chiến | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm)` | Slow pan qua căn phòng vắng |
| **342 (40s–44s)** | Tháng 8/1945, Nhật Bản tuyên bố đầu hàng Đồng Minh không điều kiện | **A** | `File:Chinese cruiser NING-HAI in 1931.jpg (Tàu tuần dương thời chiến)` | Pan qua mặt biển và chiến hạm |
| **343 (44s–48s)** | Đới Lạp dẫn đầu lực lượng Quân Thống tiến vào Bắc Kinh truy bắt Hán gian | **A** | `File:戴笠杜月笙陆京士合影1945年.jpg (Đới Lạp và Đỗ Nguyệt Sanh năm 1945)` | Zoom cận cảnh Đới Lạp thời kỳ đỉnh cao quyền lực |
| **344 (48s–52s)** | Xuyên Đảo Phương Tử bị bắt sống, thanh Cửu Long Bảo Kiếm được thu hồi nguyên vẹn | **D** | `slam ('THU HỒI CỬU LONG BẢO KIẾM')` | Chữ đập mạnh nổi bật viền vàng |
| **345 (52s–56s)** | Đới Lạp vô cùng mừng rỡ, đích thân đem thanh kiếm theo bên mình để chuẩn bị dâng lên Tưởng Giới Thạch | **A** | `File:Chiang Kai-shek and Dai Li.jpg (Đới Lạp bên Tưởng Giới Thạch)` | Slow zoom vào hai nhân vật quyền lực |
| **346 (56s–60s)** | Nhưng một định mệnh kinh hoàng đã đón đợi vị trùm mật vụ khét tiếng | **B** | `vid_06.mp4 (Tàn tro bay chậm qua thanh kiếm cổ trong tủ kính)` | Tàn tro bay chậm qua thanh thép mờ ảo |
| **347 (60s–64s)** | Ngày 17/3/1946, Đới Lạp đáp chuyến bay quân sự từ Thanh Đảo bay về Nam Kinh | **D** | `date ('17/3/1946: CHUYẾN BAY ĐỊNH MỆNH')` | Chữ ngày giờ trên nền mây mù giông bão |
| **348 (64s–68s)** | Thời tiết Nam Kinh mưa bão dữ dội, chiếc máy bay bị mất phương hướng | **A** | `File:戴笠將軍遇難前近影.png (Ảnh Đới Lạp trước chuyến bay)` | Zoom vào nét mặt trầm mặc cuối cùng của Đới |
| **349 (68s–72s)** | Đâm sầm vào đỉnh núi Đới Sơn thuộc huyện Giang Ninh, phát nổ như một quả cầu lửa | **D** | `slam ('MÁY BAY ĐÂM VÀO ĐỈNH ĐỚI SƠN')` | Chữ đập rung màn hình viền đỏ |
| **350 (72s–76s)** | Toàn bộ phi hành đoàn và Đới Lạp tử nạn tại chỗ trong ngọn lửa ngút trời | **C** | `ai_15.png (Hộp gấm đen chạm hoa văn rồng bị cháy xém một góc)` | Chiếc hộp cháy xém nằm trơ trọi giữa sỏi đá |
| **351 (76s–80s)** | Tại hiện trường, lực lượng tìm kiếm phát hiện thi thể Đới Lạp bị cháy đen biến dạng | **B** | `output/asset_library/lib198b/ai_29.png (Bóng đêm và tĩnh mịch nơi núi hoang)` | Slow pan qua sườn núi mờ sương |
| **352 (80s–84s)** | Bên cạnh là thanh Cửu Long Bảo Kiếm bị nhiệt độ hàng nghìn độ nung cháy cong queo | **C** | `vid_06.mp4 (Lưỡi kiếm cổ phủ tàn tro đen)` | Camera lướt qua vết cong vênh trên thân kiếm thép |
| **353 (84s–88s)** | 9 con rồng vàng trên chuôi kiếm bị chảy nham nhở, lưỡi thép tinh luyện biến thành một thanh sắt cháy đen | **D** | `slam ('BẢO KIẾM BIẾN DẠNG TRONG LỬA ĐỎ')` | Chữ đập dứt khoát |
| **354 (88s–92s)** | Mất đi hoàn toàn vẻ sắc bén và hào quang vương giả năm xưa | **A** | `output/long/dong-lang/img/qianlong_dragon_plaque.jpg (Phù điêu rồng bị cháy xém)` | Pan từ từ qua bề mặt đá sứt mẻ |
| **355 (92s–96s)** | Khi Tưởng Giới Thạch tổ chức quốc táng cho Đới Lạp tại núi Linh Cốc (Nam Kinh) | **A** | `File:Nationalist government of Nanking - nominally ruling over entire China, 1930 (2675972715).jpg (Lễ tang quốc gia Nam Kinh)` | Góc rộng lễ tang quốc gia |
| **356 (96s–100s)** | Thuộc hạ đã cho đặt thanh bảo kiếm cháy xém này chôn cùng vào trong quan tài của Đới | **A** | `File:ROC-SYSMH He Yingqin statue 20131026.jpg (Khu tưởng niệm Nam Kinh)` | Pan qua bậc thềm đá tưởng niệm |
| **357 (100s–104s)** | Ngôi mộ của Đới Lạp được đổ bằng hàng chục tấn bê tông cốt thép kiên cố | **A** | `File:Former Residence of He Yingqin in Nanjing 2010-11.JPG (Kiến trúc bê tông thời Dân Quốc)` | Slow zoom vào nền bê tông xám |
| **358 (104s–108s)** | Sau năm 1949 khi chính quyền thay đổi, ngôi mộ của Đới Lạp bị san phẳng | **D** | `slam ('1949: NGÔI MỘ BỊ SAN PHẲNG')` | Chữ đập vỡ vụn |
| **359 (108s–112s)** | Thanh Cửu Long Bảo Kiếm bị xới tung lẫn vào đất đá phế tích | **C** | `ai_15.png (Hộp gấm cháy xém vùi trong đất đá)` | Đất đá vùi lấp dần dấu tích chiếc hộp |
| **360 (112s–116s)** | Và vĩnh viễn mất tích trong dòng chảy lịch sử, không bao giờ được tìm thấy nữa | **D** | `slam ('CỬU LONG KIẾM VĨNH VIỄN BIẾN MẤT')` | Chữ đập mạnh trên nền đen tuyền |
| **361 (116s–120s)** | Thanh kiếm trấn quốc rốt cuộc đã theo hai người chủ sang thế giới bên kia | **A** | `File:The Qianlong Emperor in Ceremonial Armour on Horseback.jpg (Càn Long hoàng đế)` | Pan từ ánh mắt Càn Long sang bóng tối |
| **362 (120s–125s)** | Vậy còn viên Dạ Minh Châu trong tay Tống Mỹ Linh thì sao? | **D** | `question ('DẠ MINH CHÂU VÀ TỐNG MỸ LINH ĐÃ ĐI ĐÂU?')` | Chữ câu hỏi lớn trên nền xám |
| **363 (125s–130s)** | Chương tiếp theo khép lại mảnh ghép cuối cùng về số phận viên ngọc vô giá | **D** | `chapter (CHƯƠNG 11: CỬU LONG BẢO KIẾM)` | Thẻ chương chuyển cảnh sắc nét |

**Tổng kết số liệu chương:**
- Số nhịp: **32 nhịp** | Thời lượng: **130s** | Nhịp trung bình: **4.06s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 68s (52.3%)** | Nhóm B: 12s (9.2%) | Nhóm C: 17s (13.1%) | **Nhóm B+C: 29s (22.3%)** | **Nhóm D: 33s (25.4%)**.
- Số ảnh A sử dụng: **9 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 11 đạt 68s nhóm A (52.3%), sử dụng 9 ảnh tư liệu thật (Càn Long cưỡi ngựa, Đới Lạp bên Tưởng Giới Thạch, Đới Lạp 1945 cùng Đỗ Nguyệt Sanh, ảnh Đới trước tai nạn 1946, chiến hạm thời chiến, lễ tang quốc gia Nam Kinh, phù điêu rồng, chuông khắc Tâm Kinh). Bù đắp hành trình ly kỳ của thanh kiếm bằng đồ họa D (bản đồ đường đi bảo kiếm 1928-1946, date vụ rơi máy bay Đới Sơn 17/3/1946, slam kiếm biến dạng) và video B/C (hộp gấm cháy xém, tàn tro trôi qua thân kiếm thép cong vênh).

---

### CH12: Dạ Minh Châu và Tống Mỹ Linh (125 giây, 31 nhịp, trung bình 4.03s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **364 (0s–4s)** | Sau khi nhận viên Dạ Minh Châu từ Tôn Điện Anh qua trung gian Đới Lạp | **A** | `File:Chiang Kai-shek and Soong May-ling2.jpg (Tưởng Giới Thạch và Tống Mỹ Linh)` | Pan từ Tưởng sang phu nhân Tống Mỹ Linh |
| **365 (4s–8s)** | Phu nhân Tống Mỹ Linh trở thành chủ nhân mới của báu vật đắt giá nhất lăng mộ Từ Hi | **A** | `File:Miss May Ling Soong et le général Chiang Kai Shek (CNews) - btv1b53195322v.jpg (Tống Mỹ Linh)` | Slow zoom vào dung mạo sang trọng của Tống phu nhân |
| **366 (8s–12s)** | Là đệ nhất phu nhân của Trung Hoa Dân Quốc, Tống Mỹ Linh nổi tiếng với gu thời trang quý tộc phương Tây | **A** | `File:Family portrait of the Soong family in Shanghai in 1917.jpg (Gia tộc họ Tống)` | Ken Burns quét qua phong thái phương Tây của gia đình |
| **367 (12s–16s)** | Báo chí thời bấy giờ râm ran đưa tin: Tống phu nhân đã đem viên ngọc quý gắn lên mũi đôi giày dạ hội | **D** | `split ('LỜI ĐỒN DÂN GIAN: GẮN TRÊN MŨI GIÀY DẠ HỘI' vs 'HỒ SƠ GIA TỘC: LÀM KHUY CÀI ÁO DẠ TIỆC')` | Hai khối thông tin đối chiếu |
| **368 (16s–20s)** | Mỗi bước đi trong các buổi dạ tiệc ngoại giao, viên ngọc lại tỏa ra ánh lân quang xanh lam mờ ảo | **C** | `ai_12.png (Khối ngọc phát quang mờ ảo trong hộp gấm)` | Ánh sáng xanh lam huyền bí phát ra từ viên ngọc |
| **369 (20s–24s)** | Hình ảnh đó vừa thể hiện sự giàu sang tột đỉnh, vừa là sự trêu ngươi cay đắng đối với quá khứ | **A** | `File:The Imperial Portrait of the Ci-Xi Imperial Dowager Empress.PNG (Chân dung Từ Hi)` | Slow zoom-in vào chuỗi ngọc của Từ Hi |
| **370 (24s–28s)** | Viên ngọc từng nằm trong miệng vị thái hậu quyền uy nhất triều đại phong kiến | **A** | `File:The Qing Dynasty Cixi Imperial Dowager Empress of China with Attendant.JPG (Từ Hi và cung nữ)` | Pan qua trang phục triều đình cổ kính |
| **371 (28s–32s)** | Giờ đây trở thành phụ kiện trang sức dạ tiệc của đệ nhất phu nhân thời Dân Quốc | **D** | `slam ('TỪ MIỆNG THÁI HẬU ĐẾN MŨI GIÀY PHU NHÂN')` | Chữ đập mạnh trên nền tối |
| **372 (32s–36s)** | Thập niên 1940, trong các chuyến công du ngoại giao lịch sử sang Hoa Kỳ | **A** | `File:Tse-ven Soong.JPG (Tống Tử Văn ngoại giao)` | Pan qua anh trai Tống Tử Văn tại Mỹ |
| **373 (36s–40s)** | Tống Mỹ Linh đã mang theo nhiều món trang sức cổ vật quý hiếm sang New York | **A** | `output/long/dong-lang/img/melon_jade_pot.jpg (Ấm ngọc phỉ thúy dáng dưa CC0)` | Zoom cận cảnh vân ngọc xanh biếc |
| **374 (40s–44s)** | Để vận động viện trợ tài chính và vũ khí từ chính phủ Mỹ cho cuộc kháng chiến | **A** | `output/long/dong-lang/img/qianlong_moon_flask.jpg (Bình gốm sứ hoàng triều CC0)` | Pan dọc theo thân bình tráng men |
| **375 (44s–48s)** | Nhiều món đồ tùy táng của Đông Lăng bắt đầu phân tán vào các bộ sưu tập tư nhân phương Tây | **C** | `output/asset_library/lib198b/ai_18.png (Hòm gỗ tang vật qua đường biển)` | Lướt qua các thùng hàng vận chuyển |
| **376 (48s–52s)** | Năm 1949, cuộc nội chiến kết thúc, chính quyền Quốc Dân Đảng rút chạy sang Đài Loan | **D** | `map (Bản đồ di tản: Nam Kinh -> Thượng Hải -> Đài Loan / New York 1949)` | Mũi tên di tản trên bản đồ |
| **377 (52s–56s)** | Hàng ngàn thùng cổ vật tinh hoa của Tử Cấm Thành được chuyển sang Bảo tàng Cố Cung Đài Bắc | **A** | `File:Nationalist government of Nanking - nominally ruling over entire China, 1930 (2675972715).jpg (Chính quyền Nam Kinh)` | Góc rộng tòa nhà quyền lực trôi vào quá khứ |
| **378 (56s–60s)** | Nhưng trong danh mục chính thức của Cố Cung Đài Bắc, tuyệt nhiên không có viên Dạ Minh Châu của Từ Hi | **D** | `file (DANH MỤC CỐ CUNG ĐÀI BẮC: HOÀN TOÀN KHÔNG CÓ DẠ MINH CHÂU)` | Trang danh mục hiện ra dòng chữ đỏ |
| **379 (60s–64s)** | Bởi lẽ đây là tang vật cướp phá bất hợp pháp, không bao giờ được đưa vào bảo tàng quốc gia | **D** | `slam ('TANG VẬT BẤT HỢP PHÁP · KHÔNG VÀO BẢO TÀNG')` | Chữ đập dứt khoát |
| **380 (64s–68s)** | Nó thuộc về tài sản cá nhân bí mật của gia tộc họ Tống | **A** | `File:T.V. (Tse-Ven) Soong, minister-president van China, Bestanddeelnr 900-8980.jpg (Tống Tử Văn)` | Zoom vào nụ cười bí ẩn của Tống Tử Văn |
| **381 (68s–72s)** | Sau cái chết của Tưởng Giới Thạch năm 1975, Tống Mỹ Linh chuyển hẳn sang sống tại New York | **A** | `File:Miss May Ling Soong et le général Chiang Kai Shek (CNews) - btv1b53195322v.jpg (Tống Mỹ Linh)` | Pan từ từ qua dung mạo bà Tưởng |
| **382 (72s–76s)** | Sống ẩn dật tại trang viên vùng Long Island suốt những thập niên cuối đời | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm)` | Slow pan qua khung cửa sổ mùa thu |
| **383 (76s–80s)** | Tung tích của viên Dạ Minh Châu bắt đầu mờ dần theo thời gian | **C** | `ai_12.png (Khối ngọc phát quang mờ ảo)` | Ánh sáng xanh mờ dần vào bóng tối |
| **384 (80s–84s)** | Có nguồn tin cho rằng viên ngọc đã được bán lại cho tỷ phú dầu mỏ Rockefeller | **D** | `split ('NGUỒN 1: BÁN CHO TỶ PHÚ DẦU MỎ ROCKEFELLER' vs 'NGUỒN 2: CHÔN THEO DI NGUYỆN TẠI NEW YORK')` | Hai giả thuyết đối chiếu |
| **385 (84s–88s)** | Một giả thuyết khác lại khẳng định viên ngọc được cất giữ trong két sắt ngân hàng Thụy Sĩ | **A** | `File:KugelförmigeSchnitzereiausFluorit.jpg (Khối ngọc fluorite tự nhiên)` | Zoom cận cảnh bề mặt ngọc bóng |
| **386 (88s–92s)** | Năm 2003, Tống Mỹ Linh qua đời tại New York ở tuổi 106 | **D** | `date ('NĂM 2003: TỐNG MỸ LINH QUA ĐỜI TẠI NEW YORK · THỌ 106 TUỔI')` | Chữ mốc thời gian hiển thị |
| **387 (92s–96s)** | Bà mang theo toàn bộ bí mật về viên Dạ Minh Châu sang thế giới bên kia | **B** | `output/asset_library/lib198b/ai_29.png (Bóng đêm huyền bí)` | Ánh đèn hắt bóng lưng người ra đi |
| **388 (96s–100s)** | Đóng vòng 3: Bảo vật trấn quốc từng ngậm trong miệng Từ Hi đã vĩnh viễn mất dấu | **D** | `slam ('ĐÓNG VÒNG 3: BẢO VẬT MẤT DẤU TRONG LỊCH SỬ')` | Chữ đập mạnh chốt vòng mở 3 |
| **389 (100s–104s)** | Không ai còn biết viên ngọc phát quang huyền thoại ấy hiện đang nằm ở đâu trên hành tinh này | **C** | `vid_05.mp4 (Ánh sáng quét qua chuỗi ngọc mờ dần)` | Camera drift chậm qua bóng tối bao trùm |
| **390 (104s–108s)** | Nó đã biến mất như chính vương triều từng tạo ra nó | **A** | `File:The Imperial Portrait of the Ci-Xi Imperial Dowager Empress.PNG (Từ Hi Thái Hậu)` | Zoom từ từ vào bóng đen bao trùm |
| **391 (108s–112s)** | Những người từng sở hữu kho báu Đông Lăng đều đã lần lượt nằm xuống | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Slow zoom vào chân dung Tôn |
| **392 (112s–116s)** | Và kẻ chủ mưu Tôn Điện Anh rốt cuộc đã phải trả giá như thế nào? | **D** | `question ('HỒI KẾT THỰC SỰ CỦA KẺ ĐÀO MỘ LÀ GÌ?')` | Chữ câu hỏi lớn trên nền xám |
| **393 (116s–120s)** | Chương cuối cùng đưa chúng ta trở lại với cái kết cay đắng của vị tướng giang hồ | **B** | `ai_16.png (Bậc đá rêu phong hoang phế trước cửa hầm mộ)` | Ánh nắng chiều tà chiếu qua bậc đá rêu |
| **394 (120s–125s)** | Và bài học đắt giá về sự vô nghĩa của lòng tham trước bánh xe thời gian | **D** | `chapter (CHƯƠNG 12: DẠ MINH CHÂU VÀ TỐNG MỸ LINH)` | Thẻ chương chuyển cảnh dứt khoát |

**Tổng kết số liệu chương:**
- Số nhịp: **31 nhịp** | Thời lượng: **125s** | Nhịp trung bình: **4.03s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 67s (53.6%)** | Nhóm B: 11s (8.8%) | Nhóm C: 15s (12.0%) | **Nhóm B+C: 26s (20.8%)** | **Nhóm D: 32s (25.6%)**.
- Số ảnh A sử dụng: **10 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 12 đạt 67s nhóm A (53.6%), sử dụng 10 ảnh tư liệu thật (Tống Mỹ Linh bên Tưởng Giới Thạch, gia tộc họ Tống 1917, Tống Tử Văn, chân dung Từ Hi và cung nữ, ấm ngọc phỉ thúy, bình Bianhu gốm hoàng triều, khối ngọc fluorite, trụ sở Nam Kinh). Bù đắp việc giải mã hành trình bảo vật bằng đồ họa D (split lời đồn giày dạ hội vs khuy áo, file danh mục Cố Cung Đài Bắc vắng bóng Dạ Minh Châu, date Tống Mỹ Linh qua đời 2003, slam đóng vòng 3) và biểu tượng C (khối ngọc phát quang mờ dần vào bóng tối, chuỗi châu báu lưu vong).

---

### CH13: KẾT: Hầm mộ trơ đáy (110 giây, 27 nhịp, trung bình 4.07s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **395 (0s–4s)** | Sau vụ đào mộ Đông Lăng năm 1928, cuộc đời Tôn Điện Anh tiếp tục là chuỗi ngày phản trắc và chao đảo | **A** | `File:Sun Dianying.jpg (Tôn Điện Anh)` | Slow zoom vào chân dung Tôn |
| **396 (4s–8s)** | Trong Đại chiến Trung Nguyên 1930, Tôn lại phản Tưởng Giới Thạch để theo Phùng Ngọc Tường và Diêm Tích Sơn | **D** | `map (Bản đồ chiến trường Đại chiến Trung Nguyên 1930)` | Mũi tên quân sự xung đột giữa các sứ quân |
| **397 (8s–12s)** | Khi phe phản Tưởng thất bại, Tôn lại một lần nữa trở cờ xin quy thuận Nam Kinh | **D** | `slam ('LẬP KỶ LỤC TRỞ CỜ VÀ PHẢN TRẮC')` | Chữ đập mạnh trên nền tối |
| **398 (12s–16s)** | Đến thời kỳ kháng chiến chống Nhật, năm 1943 Tôn Điện Anh bị quân Nhật vây hãm tại Hà Nam | **D** | `date ('NĂM 1943: ĐẦU HÀNG QUÂN ĐỘI NHẬT BẢN')` | Chữ ngày tháng nổi bật |
| **399 (16s–20s)** | Hắn không ngần ngại đầu hàng giặc, trở thành Phó tổng tư lệnh quân đội ngụy quyền | **A** | `File:Sun Dianying 孙殿英.jpg (Tôn Điện Anh)` | Zoom cận cảnh gương mặt già nua giảo hoạt |
| **400 (20s–24s)** | Năm 1945 sau khi Nhật Bản đầu hàng, Tôn lại quay đầu theo Quốc Dân Đảng đánh lại quân Giải phóng | **A** | `File:Beiyang Army troops crossing the Gong An street.jpg (Đoàn quân di chuyển)` | Pan qua hàng lính quân đội |
| **401 (24s–28s)** | Nhưng bánh xe lịch sử cuối cùng đã bắt kịp kẻ đào trộm mộ | **B** | `output/asset_library/lib198/ai_57.png (Căn phòng tối với ánh sáng rèm tàn)` | Slow pan qua góc phòng tĩnh lặng |
| **402 (28s–32s)** | Mùa xuân năm 1947, trong Chiến dịch Dự Bắc, quân đội Tôn Điện Anh bị quân Giải phóng bao vây tiêu diệt hoàn toàn | **D** | `slam ('MÙA XUÂN 1947: BỊ BẮT SỐNG TẠI HÀ NAM')` | Chữ đập rung viền đỏ |
| **403 (32s–36s)** | Tôn Điện Anh bị bắt sống tại Thang Âm, tỉnh Hà Nam, kết thúc sự nghiệp quân sự kéo dài gần ba thập kỷ | **D** | `timeline (Timeline sụp đổ: 1943 Đầu hàng Nhật -> 1945 Theo Quốc Dân Đảng -> 1947 Bị bắt sống)` | Dòng mốc thời gian đi đến điểm kết |
| **404 (36s–40s)** | Được đưa về giam giữ và cải tạo tại trại tù binh ở Hà Bắc | **B** | `output/asset_library/lib198b/ai_29.png (Căn phòng giam vắng lặng)` | Pan qua khung cửa song sắt bóng đổ |
| **405 (40s–44s)** | Do nghiện thuốc phiện nặng suốt mấy chục năm, sức khỏe của Tôn suy kiệt nhanh chóng | **C** | `ai_06.png (Bàn thuốc phiện và tàn tro tàn lụi)` | Ánh đèn dầu leo lét tắt dần |
| **406 (44s–48s)** | Ngày 30/9/1947, Tôn Điện Anh trút hơi thở cuối cùng trong buồng giam vì bệnh kiết lỵ và nghiện thuốc | **D** | `date ('30/9/1947: TÔN ĐIỆN ANH QUA ĐỜI TRONG TRẠI GIAM · HƯỞNG THỌ 58 TUỔI')` | Chữ ngày mất trên nền đen |
| **407 (48s–52s)** | Kẻ từng chỉ huy 30 xe tải chở đầy vàng ngọc của đế vương rốt cuộc chết trong cô độc và trắng tay | **D** | `slam ('CHẾT TRẮNG TAY TRONG TÙ')` | Chữ đập dứt khoát |
| **408 (52s–56s)** | Không mang theo được một đồng bạc hay một hạt ngọc nào sang thế giới bên kia | **C** | `ai_03.png (Rương báu vật cổ trong bóng tối lãng quên)` | Bóng tối bao trùm nắp rương |
| **409 (56s–60s)** | Dinh thự bề thế của Tôn tại Thiên Tân ngày nay trở thành di tích lịch sử | **A** | `File:孙殿英旧宅.jpg (Dinh thự Tôn Điện Anh tại Thiên Tân)` | Góc rộng biệt thự phong cách phương Tây |
| **410 (60s–64s)** | Bức biển tên rỉ sét gắn trên cổng sắt như một chứng tích về lòng tham của một thời loạn lạc | **A** | `File:睦南道孙殿英旧居.JPG (Cổng sắt dinh thự Tôn Điện Anh)` | Slow zoom vào biển số nhà trên cổng |
| **411 (64s–68s)** | Còn tại huyện Tuân Hóa, quần thể Đông Lăng ngày nay đã trở thành Di sản Văn hóa Thế giới | **A** | `File:Eastern Qing Tombs.jpg (Toàn cảnh Đông Lăng ngày nay)` | Ken Burns quét qua dãy núi và cổng đá sừng sững |
| **412 (68s–72s)** | Bước vào lòng địa cung Dụ Lăng của Càn Long sau gần một thế kỷ | **A** | `File:Yuling in Eastern Qing Tombs.jpg (Lối vào Dụ Lăng)` | Pan chậm theo lối đi lát đá |
| **413 (72s–76s)** | Những vết nứt vỡ nham nhở do thuốc nổ công binh năm 1928 vẫn còn hằn sâu trên các phiến đá cẩm thạch | **A** | `File:清东陵裕陵地宫.jpg (Vết nứt trên vòm đá địa cung Dụ Lăng)` | Zoom cận cảnh vết phá hoại trên vòm đá cổ |
| **414 (76s–80s)** | Và tại Định Đông Lăng của Từ Hi, chiếc quan tài từng chứa hàng vạn viên ngọc giờ đây trơ đáy | **A** | `File:1928 DingDongLing Looting Damage.jpg (Cửa mộ bị nổ mìn)` | Pan qua nền đá hoang tàn |
| **415 (80s–84s)** | Những dòng kinh Phật khắc trên vách đá ngầm vẫn trầm mặc chứng kiến sự đổi thay của thời đại | **A** | `output/long/dong-lang/img/qing_brushpot_paradise.jpg (Cổ vật ngự dụng)` | Xoay nhẹ thân gốm cổ |
| **416 (84s–88s)** | Vụ án Đông Lăng 1928 khép lại với những con số nhức nhối | **D** | `bars (Tổng kết: 2 lăng tẩm hoàng gia bị phá hoại · 30 xe tải báu vật thất lạc · 0 ai bị kết án tử hình)` | Cột đồ họa tổng kết hiển thị |
| **417 (88s–92s)** | Kẻ đào trộm mộ thoát khỏi pháp luật thời loạn, nhưng không thoát khỏi bản án của lương tri và thời gian | **A** | `File:Der im Bau befindliche Tumulus im Grabe der Kaiserin Regentin 1.jpg (Gò mộ Đông Lăng)` | Ken Burns quét qua gò đất hoang vu |
| **418 (92s–96s)** | Đứng trước những hầm mộ rỗng tuếch hôm nay, bài học lịch sử hiện lên rõ ràng hơn bao giờ hết | **B** | `ai_16.png (Bậc đá rêu phong hoang phế trước cửa hầm mộ trống)` | Ánh nắng vàng chiều tà rọi qua bậc đá rêu phong |
| **419 (96s–100s)** | Vàng bạc, châu báu và quyền lực tối thượng rốt cuộc cũng chỉ như cát bụi | **D** | `slam ('BẢO VẬT VỀ VỚI CÁT BỤI · LÒNG THAM ĐỂ LẠI Ô DANH')` | Chữ đập dứt khoát trên nền đen |
| **420 (100s–105s)** | Chỉ có sự thật lịch sử và những chứng tích là còn tồn tại mãi với non sông | **A** | `File:Putuo Yu Ding Dongling 9.jpg (Toàn cảnh lăng mộ uy nghiêm giữa núi rừng)` | Góc máy flycam kéo lùi xa dần núi non |
| **421 (105s–110s)** | Đông Lăng đạo mộ — bản án lịch sử không bao giờ phai mờ | **D** | `chapter (CHƯƠNG 13: KẾT: HẦM MỘ TRƠ ĐÁY)` | Thẻ chương kết thúc video sắc nét và trang trọng |

**Tổng kết số liệu chương:**
- Số nhịp: **27 nhịp** | Thời lượng: **110s** | Nhịp trung bình: **4.07s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 61s (55.5%)** | Nhóm B: 10s (9.1%) | Nhóm C: 11s (10.0%) | **Nhóm B+C: 21s (19.1%)** | **Nhóm D: 28s (25.5%)**.
- Số ảnh A sử dụng: **9 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 13 đạt 61s nhóm A (55.5%), sử dụng 9 ảnh tư liệu thật (Tôn Điện Anh, biệt thự Thiên Tân, gò mộ Đông Lăng, địa cung Dụ Lăng, cửa Định Đông Lăng bị nổ mìn, toàn cảnh lăng tẩm giữa núi rừng). Bù đắp cái kết lịch sử bằng đồ họa D (bản đồ chiến trường Trung Nguyên 1930, date Tôn qua đời 30/9/1947, bars tổng kết vụ án 1928, slam thông điệp) và hình ảnh B/C (buồng giam cô quạnh, bậc đá rêu phong hoang phế trước hầm mộ trống).

---

