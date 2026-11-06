# Báo Cáo GH-228 — Chọn Đề CL Long 3 và Long 4 (Lên Sóng 22/11 và 29/11/2026)

**Ngày lập:** 06/11/2026  
**Người thực hiện:** Agent Sản Xuất (Antigravity)  
**Căn cứ nhiệm vụ:** Ticket `docs/pm/tickets/GH-228-cl-long3-topics-agy.md`, quy chuẩn `docs/pm/title-patterns-cl.md` và tiền lệ `docs/pm/tickets/GH-179-long2-report.md`.  
**Phạm vi:** Đề xuất 8 đề tài có neo văn hóa Việt; kiểm kê số lượng ảnh tự do thực tế trên Wikimedia Commons (ngưỡng tối thiểu 50 ảnh); chọn 2 đề cho Long 3 và Long 4; viết nháp `data/long/dong-lang/plan.md` cho đề thứ nhất.  
**Cam kết:** Không upload, không sửa `state.sqlite`, không đụng git (không commit), không sửa code chung. Lịch phát sóng hiện tại của Long 1 (Bao Thanh Thiên, 08/11) và Long 2 (Hòa Thân, 15/11) giữ nguyên tuyệt đối.

---

## 1. Phương Pháp và Tiêu Chí Chấm Điểm

Mỗi đề tài được chấm trên thang điểm tối đa **25 điểm**, tổng hợp từ 5 tiêu chí (0–5 điểm mỗi mục):

| Tiêu chí | Thang điểm | Mô tả |
|---|---|---|
| **Nhận diện tại VN** | 0–5 | Phim ảnh kinh điển (TVB, phim rạp) hoặc địa danh, nhân vật lịch sử đại chúng Việt Nam quen thuộc |
| **Khớp công thức** | 0–5 | Khớp khuôn thắng `[IP/Địa Danh] Ngoài Đời Thật: [Nhân Vật] — [Nghịch Lý Có Số]`, cold open có ngày và nơi cụ thể |
| **Khớp ngách Hình Sự** | 0–5 | Thuộc ngách điều tra tội phạm, vụ án chấn động, trộm cắp báu vật, tham nhũng quyền lực hơn là võ thuật hay danh nhân thuần túy |
| **Ảnh tự do Wikimedia** | 0–5 | Số lượng ảnh giấy phép tự do (PD, CC0, CC BY, CC BY-SA) trên Wikimedia Commons. **Nếu dưới 50 ảnh -> 0 điểm và LOẠI NGAY** |
| **An toàn pháp lý** | 0–5 | Rủi ro đời tư người còn sống, khiếu nại bản quyền hình ảnh, độ nhạy cảm chính trị và tôn giáo |

---

## 2. Bảng Tổng Hợp Đánh Giá 8 Đề Tài Ứng Viên

*(Danh sách loại trừ theo brief: bao-thanh-thien, hoa-than, khun sa, đỗ nguyệt sanh, yakuza, mafia, kowloon, bulger, capone, escobar, ripper, trịnh nhất tẩu, bảy viễn, lưu vĩnh phúc, đại cathay; các đề đã loại ở GH-179: Ngô Tích Hào, Lôi Lạc, Diệp Vấn, Hoàng Phi Hồng).*

| Hạng | Đề tài & Slug | Neo văn hóa / Phim quen thuộc | Ảnh tự do kiểm thực tế | Rủi ro chính | Điểm | Kết luận |
|:---:|---|---|---|---|:---:|:---:|
| **1** | **Tôn Điện Anh**<br>`dong-lang` | Phim *Đông Lăng Đạo Mộ* (1986); vụ nổ mìn cướp lăng Từ Hi & Càn Long 1928 | **189 ảnh** (100% tự do): Sun Dianying (2), Eastern Qing Tombs (78), Yuling (93), Ding Dongling (16 có ảnh hiện trường 1928) | Mất 1947 trong tù. Cần lọc ảnh hiện trường nhạy cảm, tránh mê tín | **24/25** | **CHỌN (Long 3)** |
| **2** | **Phổ Nghi**<br>`pho-nghi` | Phim *Hoàng Đế Cuối Cùng* (1987, 9 Oscar); vành móng ngựa Tòa án Tokyo 1946 | **202 ảnh** trong `Category:Pu Yi` (mẫu 100/100 tự do, PD-China, PD-Russia, PD-US NARA) | Mất 1967. Tránh tranh cãi ý thức hệ, bám sát biên bản Tòa án Tokyo | **23/25** | **CHỌN (Long 4)** |
| **3** | **Từ Hi Thái Hậu**<br>`tu-hi` | Phim *Từ Hi Thái Hậu*, *Mặt Trời Lặn Sau Tử Cấm Thành*; vụ án đầu độc Quang Tự | **>80 ảnh**: Empress Dowager Cixi (30), Ding Dongling (16), Summer Palace (30+) | Mất 1908. Tránh quy chụp chính trị, bám sát báo cáo pháp y 2008 | **22/25** | Dự bị hàng 1 (Long 5) |
| **4** | **Tần Thủy Hoàng**<br>`tan-thuy-hoang` | Phim *Cỗ Máy Thời Gian* (TVB 2001); Kinh Kha ám sát; bí mật thủy ngân lăng mộ | **>500 ảnh**: Terracotta Army (373), Qin Mausoleum (128), Qin Shi Huang (11) | Thời cổ đại. Cần đối chiếu Sử ký với đo đạc địa vật lý lăng mộ | **20/25** | Dự bị hàng 2 |
| **5** | **Võ Tắc Thiên**<br>`vo-tac-thien` | Phim *Võ Tắc Thiên* (1995 Lưu Hiểu Khánh, 2014 Phạm Băng Băng); Vô Tự Bia Càn Lăng | **66 ảnh**: Qianling Mausoleum (64), Empress Wu Ze Tian (2) | Thời Đường. Cần kiểm soát chi tiết giật gân hậu cung, bám sát Cựu Đường Thư | **19/25** | Dự bị hàng 3 |
| **6** | **Hoàng Hoa Thám**<br>`hoang-hoa-tham` | Phim *Thủ lĩnh áo nâu*; Vụ án Hà Thành Đầu Độc đêm 27/6/1908 và bí ẩn hài cốt | **29 ảnh** (Category:Hoàng Hoa Thám 18 + Category:Yên Thế Insurrection 11) | Dưới ngưỡng 50 ảnh tự do | **15/25** | **LOẠI VÌ ẢNH** |
| **7** | **Hà Hồng Sân**<br>`stanley-ho` | Phim *Đổ Thành Đại Hanh* (1992, Lưu Đức Hoa); Vua sòng bạc Ma Cao | **13 ảnh** trong `Category:Stanley Ho` | Dưới ngưỡng 50 ảnh; mới mất 2020, con cái nắm tập đoàn lớn | **13/25** | **LOẠI VÌ ẢNH** |
| **8** | **Trương Tử Cường**<br>`truong-tu-cuong` | Phim *Truy Long 2* (2019, Lương Gia Huy); vụ bắt cóc thế kỷ con trai Lý Gia Thành | **0 ảnh** (Không có category, ảnh báo chí đều có bản quyền) | Dưới ngưỡng 50 ảnh; gia tộc Lý Gia Thành còn sống | **12/25** | **LOẠI VÌ ẢNH** |

*Điểm chi tiết từng đề (Nhận diện + Khớp khuôn + Khớp ngách + Ảnh tự do + An toàn):*  
- Tôn Điện Anh: 5 + 5 + 5 + 5 + 4 = 24  
- Phổ Nghi: 5 + 5 + 4 + 5 + 4 = 23  
- Từ Hi Thái Hậu: 5 + 4 + 4 + 5 + 4 = 22  
- Tần Thủy Hoàng: 5 + 4 + 3 + 5 + 3 = 20  
- Võ Tắc Thiên: 5 + 4 + 2 + 5 + 3 = 19  
- Hoàng Hoa Thám: 5 + 4 + 4 + 0 + 2 = 15  
- Hà Hồng Sân: 4 + 4 + 4 + 0 + 1 = 13  
- Trương Tử Cường: 4 + 5 + 5 + 0 - 2 = 12  

---

## 3. Phân Tích Chi Tiết 8 Đề Tài

### 1. TÔN ĐIỆN ANH (1889–1947) — Vụ Án Đông Lăng Đạo Mộ 1928 [CHỌN LONG 3]
- **Neo văn hóa / Phim:** Phim *Đông Lăng Đạo Mộ* (1986, 5 tập, đạo diễn Lý Văn Hoa, Cố Lam đóng Tôn Điện Anh). Phim chiếu rạp và truyền hình Việt Nam nhiều lần thập niên 1990–2000, tạo ấn tượng sâu đậm về vụ trộm mộ Càn Long và Từ Hi.
- **Điểm lệch phim và đời thật (có nguồn):**
  1. *Chiến dịch quân sự quy mô thay vì thảo khấu vô tổ chức:* Phim khắc họa nhóm cướp mộ như đám thổ phỉ nhốn nháo. Thực tế hồ sơ Tòa án Nam Kinh 1928 ghi nhận: Đây là chiến dịch có tổ chức của Sư đoàn 12 thuộc Quân đoàn 6 Quốc Dân Cách Mạng Quân. Tôn Điện Anh phong tỏa Tuân Hóa dưới vỏ bọc "diễn tập quân sự", dùng công binh nổ mìn phá cửa đá ngầm, điều 30 xe tải quân sự chở cổ vật ròng rã 3 ngày đêm (4–7/7/1928).
  2. *Lưới hối lộ vô tiền khoáng hậu để thoát tội:* Phim thường kết thúc bằng sự trừng phạt. Thực tế Tôn Điện Anh dùng chính bảo vật vừa cướp để mua chuộc toàn bộ chóp bu chính quyền: tặng Cửu Long Bảo Kiếm cho Tưởng Giới Thạch (qua Đới Lạp), Dạ Minh Châu trong miệng Từ Hi cho Tống Mỹ Linh, dưa hấu ngọc phỉ thúy cho Tống Tử Văn, bảo vật cho Hà Ứng Khâm và Diêm Tích Sơn. Phiên tòa quân sự Nam Kinh bị đình chỉ, Tôn Điện Anh không những không bị xử bắn mà còn được thăng chức.
  3. *Huyền thoại viên Dạ Minh Châu:* Truyền thuyết kể viên ngọc to bằng quả trứng gà tách đôi phát sáng xanh ngắt. Hồ sơ ghi nhận đây là khối khoáng vật quý (kim cương hoặc fluorite) đường kính khoảng 4,5 cm, phát lân quang mờ trong tối, sau khi tặng Tống Mỹ Linh thì tung tích hoàn toàn biến mất trong lịch sử.
- **Cold open:** Đêm 4/7/1928, Tuân Hóa, Hà Bắc: Tiếng mìn công binh nổ tung cửa đá Dụ Lăng và Định Đông Lăng, mở màn vụ đào trộm lăng tẩm hoàng gia chấn động thế giới.
- **Tư liệu ảnh tự do:** **189 file tự do** trên Wikimedia Commons:
  - `Category:Eastern Qing Tombs` (78 file tự do): https://commons.wikimedia.org/wiki/Category:Eastern_Qing_Tombs
  - `Category:Yuling Tomb of the Qing Dynasty` (93 file tự do): https://commons.wikimedia.org/wiki/Category:Yuling_Tomb_of_the_Qing_Dynasty
  - `Category:Ding Dongling` (16 file tự do, có ảnh tư liệu 1928 chụp hiện trường phá mộ và quan tài): https://commons.wikimedia.org/wiki/Category:Ding_Dongling
  - `Category:Sun Dianying` (2 file chân dung PD): https://commons.wikimedia.org/wiki/Category:Sun_Dianying
- **Rủi ro:** Mất 1947 trong tù. Không rủi ro kiện cáo. Cần làm mờ ảnh hiện trường nhạy cảm, không đưa tin đồn mê tín dị đoan vào lời đọc.

---

### 2. PHỔ NGHI (1906–1967) — Hoàng Đế Cuối Cùng Ra Tòa Án Tokyo [CHỌN LONG 4]
- **Neo văn hóa / Phim:** Phim *Hoàng Đế Cuối Cùng* (The Last Emperor 1987, Bernardo Bertolucci, John Lone đóng, đoạt 9 giải Oscar).
- **Điểm lệch phim và đời thật (có nguồn):**
  1. *Chủ động hợp tác vì mộng phục quốc:* Phim khắc họa Phổ Nghi như nạn nhân ngây thơ bị người Nhật ép buộc. Hồi ký *Nửa đời đã qua* và tài liệu giải mật thừa nhận: Sau vụ trục xuất khỏi Tử Cấm Thành 1924 và vụ Đông Lăng 1928, Phổ Nghi chủ động móc nối với trùm tình báo Nhật Doihara Kenji, trốn khỏi Thiên Tân trong thùng xe hơi tháng 11/1931 để sang Mãn Châu khôi phục ngai vàng.
  2. *Vụ bắt sống tại sân bay Thẩm Dương:* Ngày 19/8/1945, khi Mãn Châu Quốc sụp đổ, Phổ Nghi mang theo 468 bảo vật tinh xảo nhất Tử Cấm Thành (trong 2 vali da lớn, gồm Điền hoàng tam liên ấn) định trốn sang Nhật thì bị lính dù Liên Xô bắt sống tại sân bay Thẩm Dương.
  3. *Màn đối chất dối trá tại Tòa án Tokyo 1946:* Phim cắt gọn phiên tòa. Thực tế biên bản IMTFE ghi nhận Phổ Nghi ra làm chứng 8 ngày liên tục từ 16/8/1946: Để tránh án tử hình tội phạm chiến tranh, ông liên tục khai man, phủ nhận toàn bộ trách nhiệm và chữ ký trên các hiệp ước hợp tác với Nhật.
- **Cold open:** Ngày 16/8/1946, Tòa án Quân sự Quốc tế Viễn Đông (Tokyo): Vị hoàng đế cuối cùng của Trung Hoa mặc âu phục xám bước lên bục nhân chứng đối chất với thẩm phán quốc tế.
- **Tư liệu ảnh tự do:** **202 file tự do** trong `Category:Pu Yi`:
  - Link: https://commons.wikimedia.org/wiki/Category:Pu_Yi
  - Kiểm tra mẫu 100/100 file đều là Public Domain (PD-China, PD-Russia, PD-US NARA) và CC BY-SA, ghi lại đầy đủ các thời kỳ: ấu thơ, lưu vong Thiên Tân, Mãn Châu Quốc, Tòa án Tokyo 1946 và Trại giam Phủ Thuận.
- **Rủi ro:** Mất 1967 tại Bắc Kinh. Tránh sa đà vào tranh cãi ý thức hệ, bám sát biên bản chính thức Tòa án Tokyo và hồi ký của chính ông.

---

### 3. TỪ HI THÁI HẬU (1835–1908) — Vụ Án Đầu Độc Quang Tự Bằng Thạch Tín [DỰ BỊ HÀNG 1]
- **Neo văn hóa / Phim:** Phim *Từ Hi Thái Hậu*, *Mặt Trời Lặn Sau Tử Cấm Thành*, *Thanh Cung Bí Sử*.
- **Điểm lệch phim và đời thật (có nguồn):**
  1. *Cái chết của Quang Tự:* Phim thường để Quang Tự chết do trầm cảm hoặc thái giám đầu độc. Năm 2008, báo cáo giám định pháp y 5 năm của Viện Năng lượng nguyên tử và Viện Kiểm sát Bắc Kinh khẳng định: Quang Tự chết vì ngộ độc asen (thạch tín) cấp tính với 201 mg asen trong dạ dày và tóc (gấp 2.400 lần bình thường), xảy ra trước khi Từ Hi chết đúng 20 tiếng (14/11/1908 và 15/11/1908).
  2. *Rút ruột ngân sách xây Di Hòa Viên:* Dân gian đồn bà lấy hết tiền mua thiết giáp hạm. Hồ sơ kinh tế lịch sử chỉ ra ngân sách hải quân bị trích khoảng 5–6 triệu lạng ("Hải quân cự khoản"), tuy không phải 100% nhưng trực tiếp làm tê liệt Bắc Dương Thủy Sư suốt 6 năm trước Chiến tranh Giáp Ngọ 1894.
  3. *Vụ ném Trân Phi xuống giếng:* Phim xây dựng như ghen tuông quyền lực. Sử liệu ghi nhận Trân Phi can dự bán chức tri phủ Định Viễn giá 40.000 lạng, vi phạm nghiêm trọng cung quy triều đình trước khi bị xử phạt.
- **Cold open:** 14/11/1908, Doanh Đài (Tử Cấm Thành): Quang Tự 37 tuổi quằn quại chết vì đau thắt dạ dày dữ dội. Đúng 20 tiếng sau, Từ Hi trút hơi thở cuối cùng.
- **Tư liệu ảnh tự do:** **>80 file tự do**:
  - `Category:Empress Dowager Cixi` (30 file ảnh gốc do Dụ Huân Linh chụp 1903–1904): https://commons.wikimedia.org/wiki/Category:Empress_Dowager_Cixi
  - `Category:Ding Dongling` (16 file): https://commons.wikimedia.org/wiki/Category:Ding_Dongling
  - `Category:Summer Palace, Beijing` (30 file): https://commons.wikimedia.org/wiki/Category:Summer_Palace,_Beijing
- **Rủi ro:** Đã mất 1908. Tránh quy chụp chính trị đương đại, bám sát báo cáo pháp y 2008.

---

### 4. TẦN THỦY HOÀNG (259–210 TCN) — Bí Mật Biển Thủy Ngân & Vụ Ám Sát Của Kinh Kha [DỰ BỊ HÀNG 2]
- **Neo văn hóa / Phim:** Phim *Cỗ Máy Thời Gian* (TVB 2001, Cổ Thiên Lạc, Lâm Phong), *Kinh Kha Ám Tần Vương*, *Anh Hùng*.
- **Điểm lệch phim và đời thật (có nguồn):**
  1. *Màn ám sát lúng túng tại Điện Hàm Dương:* Khác với phim kiếm hiệp hoành tráng, Sử ký Tư Mã Thiên ghi lại: Kiếm Tần vương quá dài không rút được khỏi bao, phải chạy quanh cột đồng, nhờ ngự y Hạ Vô Thả ném túi thuốc trúng Kinh Kha và cận thần hô "Vác kiếm sau lưng!" mới rút kiếm chém đứt chân Kinh Kha.
  2. *Biển thủy ngân trong lăng mộ có cơ sở khoa học:* Ghi chép "thủy ngân làm trăm sông biển lớn" được chứng minh qua các đợt đo đạc địa vật lý 2003–2006: nồng độ thủy ngân trên 40.000 m² gò lăng cao gấp 280 lần tự nhiên theo đúng mô hình sông ngòi cổ.
  3. *Biến cố Sa Khâu 210 TCN:* Tần Thủy Hoàng đột tử vì ngộ độc thủy ngân đan dược. Triệu Cao giấu xác trong xe cá ươn bốc mùi tanh nồng để ép thái tử Phù Tô tự sát.
- **Cold open:** Năm 227 TCN, Điện Hàm Dương: Tấm bản đồ dâng nộp mở ra, thanh đoản kiếm tẩm độc lộ diện.
- **Tư liệu ảnh tự do:** **>500 file tự do**:
  - `Category:Terracotta Army` (373 file): https://commons.wikimedia.org/wiki/Category:Terracotta_Army
  - `Category:Mausoleum of the First Qin Emperor` (128 file): https://commons.wikimedia.org/wiki/Category:Mausoleum_of_the_First_Qin_Emperor
  - `Category:Qin Shi Huang` (11 file): https://commons.wikimedia.org/wiki/Category:Qin_Shi_Huang
- **Rủi ro:** Thời cổ đại, cần phân biệt giữa huyền sử truyền miệng và khảo cổ học hiện đại.

---

### 5. VÕ TẮC THIÊN (624–705) — Thần Long Chính Biến & Bí Mật Vô Tự Bia [DỰ BỊ HÀNG 3]
- **Neo văn hóa / Phim:** Phim *Võ Tắc Thiên* (Lưu Hiểu Khánh 1995, Phan Nghênh Tử 1985, Phạm Băng Băng 2014).
- **Điểm lệch phim và đời thật (có nguồn):**
  1. *Nghi án bóp cổ con gái sơ sinh:* Phim khẳng định bà giết con vu oan Vương hoàng hậu. *Cựu Đường Thư* chỉ chép đứa trẻ chết yểu; chi tiết mưu sát chỉ xuất hiện trong *Tân Đường Thư* và *Tư Trị Thông Giám* viết sau đó hơn 300 năm dưới góc nhìn Nho giáo Tống triều.
  2. *Ngục tù mật thám và "La Chức Kinh":* Quyền lực Võ Chu dựa vào Lai Tuấn Thần và cuốn "La Chức Kinh" (sách bẫy án oan), tạo hàng ngàn ngục hình oan khốc.
  3. *Bia Không Chữ Càn Lăng:* Khảo sát thực tế phiến đá 98 tấn tại Càn Lăng cho thấy đã kẻ sẵn 3.300 ô vuông để khắc chữ, nhưng cuộc đảo chính Thần Long 705 khiến vua Trung Tông không muốn khắc lời ca tụng.
- **Cold open:** Ngày 20/2/705, Cung Trường Sinh (Lạc Dương): 500 cấm quân phát động Thần Long chính biến, chém đầu hai sủng thần họ Trương, ép nữ hoàng 81 tuổi thoái vị.
- **Tư liệu ảnh tự do:** **66 file tự do**:
  - `Category:Qianling Mausoleum` (64 file tự do): https://commons.wikimedia.org/wiki/Category:Qianling_Mausoleum
  - `Category:Empress Wu Ze Tian` (2 file tự do): https://commons.wikimedia.org/wiki/Category:Empress_Wu_Ze_Tian
- **Rủi ro:** Đã mất năm 705. Cần kiểm soát chi tiết giật gân phòng the, tập trung vào ngục hình và khảo cổ học.

---

### 6. HOÀNG HOA THÁM (1858–1913) — Vụ Hà Thành Đầu Độc 1908 [LOẠI VÌ THIẾU ẢNH]
- **Neo văn hóa / Phim:** Phim *Thủ lĩnh áo nâu*, lịch sử khởi nghĩa Yên Thế.
- **Điểm lệch phim và đời thật:** Chiến thuật du kích ngầm và thỏa hiệp lập đồn điền tự trị Phồn Xương (1894, 1897); Vụ Hà Thành đầu độc đêm 27/6/1908 bị lộ do một phụ bếp đi xưng tội với linh mục Pháp; Cái chết bị sát hại ngày 10/2/1913 và bí ẩn hài cốt chưa tìm thấy.
- **Cold open:** Đêm 27/6/1908, Hà Nội: Binh lính Trung đoàn bộ binh Pháp ngã gục sau bữa ăn nấu bằng cà độc dược.
- **Tư liệu ảnh tự do:** **29 file** (`Category:Hoàng Hoa Thám` 18 file + `Category:Yên Thế Insurrection` 11 file).
  - Link: https://commons.wikimedia.org/wiki/Category:Ho%C3%A0ng_Hoa_Th%C3%A1m và https://commons.wikimedia.org/wiki/Category:Y%C3%AAn_Th%E1%BA%BF_Insurrection
- **Kết luận:** **LOẠI** vì chỉ có 29 ảnh tự do (dưới ngưỡng 50 ảnh theo yêu cầu của ticket GH-228).

---

### 7. HÀ HỒNG SÂN (1921–2020) — "Vua Sòng Bạc Ma Cao" [LOẠI VÌ THIẾU ẢNH]
- **Neo văn hóa / Phim:** Phim *Đổ Thành Đại Hanh* (Casino Tycoon 1992, Lưu Đức Hoa, Vương Tinh).
- **Điểm lệch phim và đời thật:** Stanley Ho không bao giờ đánh bạc và xuất thân danh gia vọng tộc Ho Tung; Thắng thầu 1961 là liên minh 4 người (Stanley Ho, Diệp Hán, Ho Yim, Hoắc Anh Đông); Bức thư đe dọa 13 điều của hắc bang năm 1962 dọa đánh bom sòng bạc và phản đòn treo thưởng 1 triệu HKD.
- **Cold open:** 30/3/1962, sòng bạc Tân Hoa Viên (Hotel Estoril, Ma Cao) khai trương dưới sự bảo vệ của cảnh sát vũ trang.
- **Tư liệu ảnh tự do:** **13 file tự do** trong `Category:Stanley Ho`.
  - Link: https://commons.wikimedia.org/wiki/Category:Stanley_Ho
- **Kết luận:** **LOẠI** vì chỉ có 13 ảnh tự do (dưới ngưỡng 50 ảnh). Rủi ro gia tộc đông con cái còn sống đang nắm giữ các tập đoàn niêm yết lớn.

---

### 8. TRƯƠNG TỬ CƯỜNG (1955–1998) — "Big Spender" [LOẠI VÌ THIẾU ẢNH]
- **Neo văn hóa / Phim:** Phim *Truy Long 2* (2019, Lương Gia Huy), *Operation Billionaire* (1998, Nhậm Đạt Hoa).
- **Điểm lệch phim và đời thật:** Tâm lý đàm phán lạnh lùng: một mình quấn thuốc nổ vào biệt thự Lý Gia Thành tối 23/5/1996 lấy trọn 1,038 tỷ HKD tiền mặt; Từng thắng kiện Cảnh sát HK năm 1995 đòi bồi thường 8 triệu HKD; Bị xử bắn tại Quảng Châu ngày 6/12/1998 gây tranh cãi quyền tài phán sau trao trả 1997.
- **Cold open:** Tối 23/5/1996, đường Deep Water Bay, Hồng Kông: Xe chở Lý Trạch Cự bị nhóm cướp AK-47 chặn đường.
- **Tư liệu ảnh tự do:** **0 file tự do** trên Commons (không có category, ảnh báo chí đều có bản quyền).
- **Kết luận:** **LOẠI** vì 0 ảnh tự do.

---

## 4. Quyết Định Chọn Đề và Kế Hoạch Sản Xuất

Căn cứ vào bảng điểm và yêu cầu của brief, 2 đề tài được chọn là:

1. **LONG 3 (Dự kiến phát sóng 22/11/2026): TÔN ĐIỆN ANH — Vụ Án Đông Lăng Đạo Mộ 1928**
   - **Slug:** `dong-lang`
   - **Tiêu đề đề xuất (≤60 ký tự):** `ĐÔNG LĂNG ĐẠO MỘ Ngoài Đời Thật: Tôn Điện Anh` (42 ký tự)  
     *(Bản A/B: `ĐÔNG LĂNG ĐẠO MỘ Ngoài Đời Thật: Tôn Điện Anh — Vụ Án Năm 1928` - 58 ký tự)*
   - **Lý do chọn:** Đứng đầu bảng điểm (24/25). Khớp hoàn hảo ngách hình sự (vụ án đào trộm mộ lớn nhất thế kỷ 20, có điều tra, phiên tòa quân sự, hối lộ thoát án). 189 ảnh tự do đã kiểm trên Commons, có cả ảnh hiện trường 1928.
   - **Tình trạng:** Đã hoàn thành bản thảo kế hoạch chi tiết `data/long/dong-lang/plan.md` (14 chương, cấu trúc chuẩn theo mẫu `hoa-than`).

2. **LONG 4 (Dự kiến phát sóng 29/11/2026): PHỔ NGHI — Hoàng Đế Cuối Cùng Ra Tòa Án Tokyo**
   - **Slug:** `pho-nghi`
   - **Tiêu đề đề xuất (≤60 ký tự):** `HOÀNG ĐẾ CUỐI CÙNG Ngoài Đời Thật: Phổ Nghi` (40 ký tự)  
     *(Bản A/B: `HOÀNG ĐẾ CUỐI CÙNG Ngoài Đời Thật: Phổ Nghi — Tòa Án Tokyo 1946` - 58 ký tự)*
   - **Lý do chọn:** Hạng nhì bảng điểm (23/25). IP phim kinh điển đoạt 9 Oscar. Yếu tố hình sự / pháp đình đắt giá: 8 ngày ra làm chứng tại Tòa án Quân sự Quốc tế Viễn Đông (Tokyo 1946) và 10 năm cải tạo tại Trại giam Phủ Thuận. 202 ảnh tự do trong `Category:Pu Yi`.
   - **Tình trạng:** Đã khóa số liệu, sẵn sàng viết `data/long/pho-nghi/plan.md` ngay khi Lead duyệt.

3. **DỰ BỊ HÀNG 1 (Long 5): TỪ HI THÁI HẬU — Báo Cáo Pháp Y 2008** (`tu-hi`, 80+ ảnh tự do).

---

## 5. Kết Quả Bàn Giao và Trạng Thái

- Đã tạo file kế hoạch chi tiết cho Long 3: `data/long/dong-lang/plan.md` (UTF-8, 14 chương).
- Đã lập báo cáo hoàn chỉnh: `docs/pm/tickets/GH-228-cl-long3-topics-report.md` (UTF-8).
- Không thực hiện bất kỳ lệnh git commit nào.
- Không sửa đổi bất kỳ file code dùng chung hay cơ sở dữ liệu `state.sqlite`.
- Kính chuyển Lead và Chủ kênh xem xét phê duyệt đề xuất.
