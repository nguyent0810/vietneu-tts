# Kế hoạch hệ thống hình ảnh 14 chương: Hòa Thân ngoài đời thật (slug: hoa-than)

> **Tài liệu sản xuất:** Thuộc Ticket GH-179, kênh CL (Hình Sự).
> **Đầu vào:** `data/long/hoa-than/plan.md`, `docs/pm/tickets/GH-179-hoathan-research-report.md`, `output/long/hoa-than/research.json`, `ext.json`, `img/`.
> **Tiêu chuẩn áp dụng:** `CLAUDE.md`, `docs/codex/long-rules.md`, `motion/long/floor.py`, `motion/long/SOURCES.md`.

## 1. Mục tiêu và Chiến lược phân bổ tài nguyên

- **Thời lượng toàn video:** 28 phút 50 giây (1.730 giây), cấu trúc chuẩn 14 chương (CH00 đến CH13).
- **Nhịp chuyển động hình ảnh (pacing):** Tổng cộng **429 nhịp hình**, thời lượng trung bình **4,03 giây/nhịp** (tuân thủ nghiêm ngặt dải mục tiêu 3–5 giây/nhịp). Mỗi nhịp là một thay đổi thị giác rõ nét: đổi khung hình, zoom chi tiết, pan Ken Burns, chuyển lớp đồ họa hoặc motion graphic.
- **Bốn nhóm tài nguyên:**
  - **Nhóm A (Tư liệu lịch sử):** Chiếm **931 giây (53,8% thời lượng)**, là xương sống của video. Bao gồm 142 ảnh tự do đã kiểm duyệt (chân dung đời Thanh, ngự chế Càn Long, tấu sớ, hiện vật CC0/CC BY, ảnh tư liệu vương phủ 1912). Mọi chương đều đạt tỷ lệ A ≥ 50%.
  - **Nhóm B (AI tái dựng bối cảnh):** Chiếm **163 giây (9,4% thời lượng)**. Tái dựng phố cổ Bắc Kinh, cung đình, thư phòng, hồi lang phủ đệ. **Tuyệt đối không có mặt người thật**, không vẽ chữ Hán hay ấn triện giả, không dựng cảnh hành hình. Lần đầu xuất hiện trong mỗi chương mang nhãn nhỏ "TÁI DỰNG MINH HỌA".
  - **Nhóm C (AI minh họa khái niệm):** Chiếm **148 giây (8,6% thời lượng)**. Ẩn dụ điện ảnh: dải lụa trắng, hòm đá, cán cân công lý, chìa khóa, rương bạc nén cổ, đồng hồ cát. Không chữ, không mặt người.
  - **Nhóm B + C tổng cộng:** **311 giây (18,0% thời lượng)**, nằm an toàn dưới trần tối đa 25%.
  - **Nhóm D (Motion Graphics engine):** Chiếm **488 giây (28,2% thời lượng)**. Đóng vai trò phân tích số liệu tài chính, timeline các mốc ngày, sơ đồ phả hệ, bảng so sánh đối chiếu và mô-típ bản kê cuộn chạy xuyên suốt 12 dòng.

### Bảng kiểm định Floor kênh (`motion/long/floor.py`)

| Tiêu chí sàn | Mức quy định sàn | Mức thiết kế dự án `hoa-than` | Trạng thái |
|---|---|---|---|
| **Âm tiết kịch bản** | ≥ 5.000 âm tiết (≈ 23 phút) | ≈ 6.100 âm tiết (28m50s ở 212 âm/phút) | **ĐẠT** |
| **Số chương** | ≥ 10 chương | 14 chương (CH00 đến CH13) | **ĐẠT** |
| **Số loại cảnh engine** | ≥ 14 loại | 18 loại (`photo`, `print`, `map`, `ledger`, `counter`, `slam`, `broll`, `file`, `date`, `timeline`, `quote`, `split`, `bars`, `org`, `question`, `waterfall`, `chapter`, `heat`) | **ĐẠT** |
| **Ảnh tư liệu A khác nhau** | ≥ 40 ảnh | **68 ảnh tư liệu khác nhau** (trích từ kho 142 ảnh tự do) | **ĐẠT** |
| **Cảnh có video / b-roll** | ≥ 30 cảnh | **34 cảnh video** (8 video Flow `vid_NN.mp4` + broll kiến trúc phủ đệ) | **ĐẠT** |
| **Tỷ lệ kinetic** | ≤ 38% | **12,8%** (55/429 nhịp) | **ĐẠT** |
| **Chữ trên nền trống (naked)** | ≤ 12% | **3,5%** (hầu hết chữ đều có background tranh/tư liệu mờ) | **ĐẠT** |

---

## 2. Chi tiết hệ thống nhịp hình 14 chương (CH00 – CH13)

### CH00: Nhà riêng, 22/2/1799 (Cold Open) (75 giây, 18 nhịp, trung bình 4.17s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **01 (0s–4s)** | Đêm 22/2/1799, phố kinh thành Bắc Kinh phủ kín tuyết lạnh | **B** | `ai_01.png (Phố đêm Bắc Kinh mùa đông 1799)` | Slow pan qua mái ngói và tường xám phủ tuyết |
| **02 (4s–8s)** | Một chỉ dụ khẩn cấp từ hoàng cung Cố Cung ban xuống tư dinh Hòa Thân | **A** | `output/long/hoa-than/img/qianlong_temple_name.jpg (Tấu sớ triều đình)` | Pan dọc nét mực son và dấu triện hoàng gia |
| **03 (8s–12s)** | Cổng dinh thự Zhizhai đóng chặt dưới sự giám sát nghiêm ngặt của thị vệ | **A** | `File:Prince Gong's Mansion - Main Gate.jpg (Cổng Đinh Phủ - Zhizhai)` | Ken Burns slow zoom-in vào chi tiết then cài cổng gỗ |
| **04 (12s–16s)** | Hòa Thân, nhân vật quyền lực nhất triều Thanh, đối diện với hồi kết | **A** | `File:Heshen.jpg (Chân dung Hòa Thân đời Thanh)` | Pan từ từ từ y phục quan nhất phẩm lên ánh mắt |
| **05 (16s–20s)** | Chỉ đúng 15 ngày sau khi Thái thượng hoàng Càn Long băng hà | **D** | `timeline (Mốc 15 ngày: 7/2 Càn Long mất -> 22/2 án tự kết liễu)` | Vẽ đường mốc thời gian chuyển động liên tục |
| **06 (20s–25s)** | Càn Long, người che chở tuyệt đối suốt 24 năm, vừa nằm xuống Dụ Lăng | **A** | `output/long/hoa-than/img/qianlong_essay_old_age.jpg (Ngự chế Càn Long tuổi già)` | Slow pan ngang qua từng dòng ngự bút tuổi già |
| **07 (25s–29s)** | Tân hoàng đế Gia Khánh lập tức ra tay tước đoạt toàn bộ binh quyền | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh triều phục)` | Focus mặt hoàng đế, đẩy sáng viền áo hoàng long |
| **08 (29s–33s)** | Bản án ban đầu được tuyên xử là cực hình lăng trì xử trảm | **D** | `slam ("BẢN ÁN BAN ĐẦU: LĂNG TRÌ")` | Chữ đập mạnh trên nền tối, rung nhẹ màn hình |
| **09 (33s–37s)** | Nhưng triều đình đã bất ngờ đổi án, ban ân cho tự tận tại tư gia | **A** | `File:Princess Hexiao.jpg (Công chúa Hòa Hiếu)` | Zoom cận cảnh chân dung công chúa Hòa Hiếu bảo mệnh |
| **10 (37s–41s)** | Một căn phòng tĩnh mịch, ánh nến leo lét trong dinh thự Zhizhai | **B** | `ai_02.png (Thư phòng cổ vắng lặng trong đêm)` | Pan chậm từ góc cửa sổ trăng rọi sang bàn làm việc |
| **11 (41s–45s)** | Không có pháp trường náo nhiệt, chỉ có một dải lụa trắng và sự sụp đổ | **C** | `ai_03.png (Biểu tượng dải lụa và sự sụp đổ quyền lực)` | Subtle camera drift, ánh sáng bên hông chiếu lên dải lụa |
| **12 (45s–49s)** | Đế chế quyền lực và tiền bạc lớn nhất triều Mãn sụp đổ trong chớp mắt | **C** | `vid_02.mp4 (Bạc nén cổ trong ánh nến)` | Camera lướt chậm qua rương bạc mờ dần trong bóng tối |
| **13 (49s–53s)** | Người đời sau thêu dệt nên một kho vàng khổng lồ bằng cả chục năm ngân sách | **D** | `counter (1.100.000.000 LẠNG BẠC - Số đồn đoán)` | Bộ đếm số nhảy nhanh từ 0 lên 1,1 tỷ lạng |
| **14 (53s–57s)** | Cùng hình tượng một gã quan tham béo tròn, hài hước trên màn ảnh truyền hình | **D** | `split ("PHIM TRUYỀN HÌNH" vs "HỒ SƠ LỊCH SỬ")` | Chia đôi màn hình, đối chiếu chữ tương phản |
| **15 (57s–61s)** | Nhưng hồ sơ lưu trữ năm 1799 thực sự ghi lại những gì? | **A** | `File:Prince Gong's Mansion - Grand Theater.jpg (Đại hý đài)` | Góc ngước nhìn kiến trúc vương phủ trong bóng đêm |
| **16 (61s–65s)** | Chân dung thực sự của Hòa Thân ngoài đời thật | **A** | `File:Hesen (cropped).jpg (Chân dung cận cảnh đời Thanh)` | Zoom cận cảnh vào gương mặt thanh tú, sắc sảo |
| **17 (65s–70s)** | Và câu chuyện về khối tài sản bí ẩn nhất lịch sử Á Đông | **A** | `output/long/hoa-than/img/qianlong_dragon_dish.jpg (Đĩa rồng men lam vàng)` | Xoay nhẹ chi tiết men gốm và hoa văn rồng hoàng gia |
| **18 (70s–75s)** | Bắt đầu từ bản kê được mở ra trong đêm định mệnh | **D** | `chapter (CHƯƠNG 00: NHÀ RIÊNG, 22/2/1799)` | Thẻ chương đồ họa mở màn sắc nét |

**Tổng kết số liệu chương:**
- Số nhịp: **18 nhịp** | Thời lượng: **75s** | Nhịp trung bình: **4.17s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 38s (50.7%)** | Nhóm B: 8s (10.7%) | Nhóm C: 8s (10.7%) | **Nhóm B+C: 16s (21.3%)** | **Nhóm D: 21s (28.0%)**.
- Số ảnh A sử dụng: **9 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 0 đạt 38s nhóm A (50.7%), sử dụng 8 tư liệu thật (chân dung Hòa Thân, Gia Khánh, Công chúa Hòa Hiếu, tấu sớ Càn Long, ngự chế tuổi già, đĩa rồng, cổng phủ, đại hý đài). Bù đắp nhịp căng thẳng bằng D (timeline 15 ngày, slam án lăng trì) và B/C tái dựng không gian thư phòng đêm 22/2/1799.

### CH01: Nghịch lý (105 giây, 27 nhịp, trung bình 3.89s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **19 (0s–4s)** | Mở đầu với nghịch lý lớn nhất: Quan tham nổi tiếng nhất nhưng tài sản mâu thuẫn nhất | **D** | `slam ("NGHỊCH LÝ KHO VÀNG")` | Chữ đập mạnh, hiệu ứng rung nhẹ |
| **20 (4s–8s)** | Phim ảnh và giai thoại kể về những hầm ngầm chứa đầy vàng bạc châu báu | **C** | `ai_04.png (Rương kho báu trong hầm đá thâm nghiêm)` | Slow pan từ góc tối vào rương khóa đồng |
| **21 (8s–12s)** | Bách khoa tiếng Việt ghi nhận con số 1,1 tỷ lạng bạc, tương đương 270 tỷ USD | **D** | `counter (1.100.000.000 LẠNG BẠC · 270 TỶ USD)` | Đếm số nhảy vọt kèm quy đổi USD |
| **22 (12s–16s)** | Con số này tương đương ngân sách toàn bộ quốc gia Đại Thanh suốt 12 đến 15 năm | **D** | `bars (So sánh: Ngân sách 1 năm vs 1,1 tỷ lạng)` | Cột đồ họa vọt cao vượt khung hình |
| **23 (16s–20s)** | Nhưng khi mở bách khoa tiếng Anh và tài liệu quốc tế, con số lại hoàn toàn khác | **D** | `split ("WIKIPEDIA VI: 1.100 TRIỆU" vs "WIKIPEDIA EN: 60–80 TRIỆU")` | Hai cột tương phản rõ rệt |
| **24 (20s–24s)** | Bài tiếng Anh chỉ ghi nhận động sản điều tra thực tế vào khoảng 60 đến 80 triệu lạng | **A** | `output/long/hoa-than/img/qianlong_lacquer_teabowl.jpg (Chén trà điêu tất ngự chế CC0)` | Zoom cận cảnh hiện vật bảo bối hoàng triều |
| **25 (24s–28s)** | Còn các con số từ 100 đến 800 triệu lạng vẫn đang bị các sử gia tranh cãi gay gắt | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Pan chi tiết áo thụng quan nhất phẩm |
| **26 (28s–32s)** | Vì sao có khoảng lệch lên đến hàng chục lần giữa các nguồn tài liệu? | **D** | `question ("VÌ SAO CÓ KHOẢNG LỆCH HÀNG CHỤC LẦN?")` | Chữ câu hỏi nổi bật trên nền xám |
| **27 (32s–36s)** | Ba vòng mở ra để giải mã toàn bộ câu chuyện lịch sử này | **D** | `timeline (3 vòng: Bản kê 1799 · Mốc 3 năm · Hình tượng phim)` | 3 nhánh đồ họa mở rộng dần |
| **28 (36s–40s)** | Vòng 1: Bản kê năm 1799 thực sự là kho vàng hay hồ sơ bị phóng đại? | **C** | `ai_05.png (Cán cân công lý và thỏi bạc cổ)` | Ken Burns nghiêng nhẹ theo góc đòn cân |
| **29 (40s–44s)** | Vòng 2: Vì sao Gia Khánh lên ngôi năm 1796 nhưng phải đợi đến năm 1799 mới dám hành động? | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh ngai vàng)` | Focus vào ngọc ấn và thần thái hoàng đế trẻ |
| **30 (44s–48s)** | Vòng 3: Vì sao văn hóa đại chúng cần biến một đại thần tài năng thành gã hề? | **A** | `File:Hesen (cropped).jpg (Chân dung Hòa Thân)` | Zoom cận cảnh gương mặt sắc sảo đăm chiêu |
| **31 (48s–52s)** | Đối chiếu Lưu Dung và Hòa Thân: Phim ảnh biến họ thành tử thù một mất một còn | **A** | `File:Liu Yong.png (Chân dung Lưu Dung)` | Zoom cận cảnh nét mặt điềm đạm của Lưu Dung |
| **32 (52s–56s)** | Nhưng ngoài đời thực, họ từng cùng làm Thượng thư Bộ Lại suốt hai năm liền | **A** | `output/long/hoa-than/img/wenguan_portrait_1.jpg (Quan văn triều Thanh CC0)` | Pan dọc bổ phục hạc trắng quan nhất phẩm |
| **33 (56s–60s)** | Hai vị thượng thư cùng nhau phê duyệt quan chế và ký các văn bản bổ nhiệm triều đình | **A** | `output/long/hoa-than/img/wenguan_portrait_2.jpg (Quan văn triều Thanh CC0)` | Pan dọc bức chân dung quan văn thứ hai |
| **34 (60s–64s)** | Sự thật nằm dưới các lớp bụi thời gian và văn bản gốc chưa từng công bố | **B** | `vid_03.mp4 (Hành lang sơn son phủ đệ cổ)` | Camera drift chậm qua hành lang son bóng đổ |
| **35 (64s–67s)** | Không thể vội vã kết luận bằng những giai thoại truyền miệng dân gian | **D** | `slam ("KHÔNG KẾT LUẬN BẰNG TIN ĐỒN")` | Chữ đập dứt khoát trên nền đen |
| **36 (67s–71s)** | Video này lần theo từng trang tấu sớ, bản kê và chỉ dụ thực tế | **A** | `output/long/hoa-than/img/qianlong_temple_name.jpg (Tấu sớ miếu hiệu Càn Long)` | Pan lướt qua nét mực son và dấu triện ngự phê |
| **37 (71s–75s)** | Khởi đầu từ văn phòng tối mật và quyền lực bậc nhất: Quân cơ xứ | **A** | `File:Hall of Supreme Harmony.jpg (Thái Hòa Điện)` | Góc máy rộng hùng vĩ của Cố Cung |
| **38 (75s–79s)** | Nơi một thị vệ bình thường đã bước chân vào triều đình và làm thay đổi cục diện | **A** | `File:Meridian Gate of the Forbidden City.jpg (Ngọ Môn)` | Ken Burns zoom-out từ cổng vòm cao vút |
| **39 (79s–83s)** | Con đường thăng tiến thần tốc chưa từng có tiền lệ trong lịch sử | **B** | `ai_06.png (Cổng cung điện uy nghiêm trong sương sớm)` | Pan chậm từ thềm đá lên bóng lính canh |
| **40 (83s–87s)** | Để lại một phủ đệ bề thế và lộng lẫy nhất kinh thành | **A** | `File:Prince Gong's Mansion - Grand Theater.jpg (Đại hý đài)` | Góc máy hất lên trần gỗ chạm trổ tinh xảo |
| **41 (87s–91s)** | Ngôi nhà ngày nay vẫn đứng sừng sững bên bờ hồ Thập Sát Hải | **A** | `File:Prince Gong Mansion Garden.jpg (Hoa viên Cung Vương Phủ)` | Pan ngang hồ nước và núi đá hoa viên |
| **42 (91s–95s)** | Nhưng trước khi có bạc vạn và lâu đài tráng lệ | **C** | `ai_07.png (Chùm chìa khóa đồng và ổ khóa phong ấn)` | Ánh sáng quét qua kim loại đồng cổ |
| **43 (95s–99s)** | Chàng thanh niên Hòa Thân năm 22 tuổi đã bắt đầu như thế nào? | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom vào ánh nhìn tự tin |
| **44 (99s–102s)** | Bước vào hành trình 24 năm vươn lên tột đỉnh quyền lực | **A** | `output/long/hoa-than/img/court_jifu_robe.jpg (Cát phục quan triều Thanh)` | Pan dọc hoa văn rồng cuộn chỉ vàng |
| **45 (102s–105s)** | Bắt đầu từ cánh cửa Ngọ Môn mùa đông năm 1772 | **D** | `chapter (CHƯƠNG 01: NGHỊCH LÝ)` | Thẻ chương chuyển cảnh dứt khoát |

**Tổng kết số liệu chương:**
- Số nhịp: **27 nhịp** | Thời lượng: **105s** | Nhịp trung bình: **3.89s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 55s (52.4%)** | Nhóm B: 8s (7.6%) | Nhóm C: 12s (11.4%) | **Nhóm B+C: 20s (19.0%)** | **Nhóm D: 30s (28.6%)**.
- Số ảnh A sử dụng: **14 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 1 đạt 55s nhóm A (52.4%), sử dụng 14 ảnh tư liệu A (Hòa Thân, Lưu Dung, Gia Khánh, 2 quan văn, chén điêu tất, tấu sớ, áo cát phục, Ngọ Môn, Thái Hòa Điện, Cung Vương Phủ). Bù đắp câu hỏi nghịch lý bằng hệ thống đồ họa D (split EN vs VI, counter 1,1 tỷ, bars ngân sách, timeline 3 vòng) và biểu tượng C (rương hầm đá, cán cân, chìa khóa).

### CH02: Thị vệ cửa cung (130 giây, 33 nhịp, trung bình 3.94s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **46 (0s–4s)** | Hòa Thân sinh ngày 1 tháng 7 năm 1750, tên khai sinh là Thiện Bảo | **D** | `date ("01.07.1750 · THIỆN BẢO CHÀO ĐỜI")` | Mốc ngày số lớn hiện trên nền tối |
| **47 (4s–8s)** | Xuất thân từ dòng dõi quý tộc Mãn Châu Nữu Hỗ Lộc, thuộc Chính Hồng kỳ | **A** | `File:Plain Red Banner.png (Huy hiệu Chính Hồng kỳ)` | Ken Burns zoom-in vào chi tiết cờ đỏ thêu viền |
| **48 (8s–12s)** | Dù xuất thân danh môn, gia cảnh sớm sa sút khi cha mẹ qua đời khi ông mới lên chín | **A** | `File:Forbidden City Map 18th century.jpg (Bản đồ Cố Cung thế kỷ 18)` | Pan qua khu vực phủ nội vụ và cư xá Bát Kỳ |
| **49 (12s–16s)** | Hai anh em Thiện Bảo và Hòa Lâm nương tựa vào người hầu già trung thành | **B** | `ai_09.png (Giảng đường Quốc Tử Giám thời Thanh)` | Pan ngang qua các dãy bàn gỗ và nghiên mực |
| **50 (16s–20s)** | Ông theo học tại Hàm An Cung quan học, ngôi trường danh giá dành cho con em Bát Kỳ | **A** | `File:Gate of Supreme Harmony.jpg (Thái Hòa Môn)` | Góc rộng thềm đá Cố Cung nơi đặt trường quan học |
| **51 (20s–24s)** | Tại đây, chàng trai trẻ bộc lộ tài năng phi thường, thông thạo 4 thứ tiếng | **D** | `slam ("THÔNG THẠO 4 THỨ TIẾNG: MÃN · HÁN · MÔNG · TẠNG")` | 4 cụm từ hiện lần lượt theo nhịp đọc |
| **52 (24s–28s)** | Năng lực ngôn ngữ và trí nhớ siêu phàm trở thành bệ phóng cho tương lai | **A** | `File:Heshen.jpg (Chân dung Hòa Thân thời trẻ)` | Zoom cận cảnh nét thư sinh đĩnh đạc |
| **53 (28s–32s)** | Năm 1769, ông thi Hương khoa cử nhưng không đỗ đạt | **A** | `File:Forbidden City Map 18th century.jpg (Bản đồ Cố Cung)` | Pan góc trường thi Cố Cung |
| **54 (32s–36s)** | Nhưng con đường quan lộ của quý tộc Mãn Châu không chỉ có khoa cử | **A** | `File:Eight Banners review.jpg (Bát Kỳ duyệt binh)` | Pan dọc hàng quân trang phục chỉnh tề |
| **55 (36s–40s)** | Năm 1772, ông thừa kế chức quan nhỏ và trở thành Tam đẳng thị vệ cửa Ngọ Môn | **D** | `date ("1772 · TAM ĐẲNG THỊ VỆ NGỌ MÔN")` | Mốc ngày hiện sắc nét |
| **56 (40s–44s)** | Nhiệm vụ hàng ngày là bưng lọng, cầm cờ và đứng gác cổng hoàng thành | **A** | `File:Meridian Gate of the Forbidden City.jpg (Ngọ Môn Tử Cấm Thành)` | Ken Burns góc rộng ngước nhìn cổng thành |
| **57 (44s–48s)** | Hàng ngàn thị vệ đứng gác mỗi ngày, nhưng Thiện Bảo luôn tìm cách nổi bật | **B** | `ai_08.png (Sân duyệt binh thị vệ Ngọ Môn)` | Pan từ thềm đá sang hàng lính canh thẳng tắp |
| **58 (48s–52s)** | Năm 1775, cơ hội định mệnh đã xuất hiện giữa Tử Cấm Thành | **D** | `date ("1775 · CUỘC GẶP ĐỊNH MỆNH")` | Mốc năm nổi bật trên nền đỏ cung đình |
| **59 (52s–56s)** | Hoàng đế Càn Long đang ở đỉnh cao quyền lực của triều đại thịnh trị | **A** | `File:The Qianlong Emperor in Ceremonial Armour on Horseback.jpg` | Slow pan chi tiết giáp vàng và cung tên |
| **60 (56s–60s)** | Trong một chuyến xuất hành, Càn Long trích dẫn một câu sách cổ nhưng cận thần lúng túng | **A** | `File:Palace of Heavenly Purity.jpg (Càn Thanh Cung)` | Pan góc ngai vàng Càn Thanh Cung |
| **61 (60s–64s)** | Từ hàng thị vệ, Thiện Bảo đã cất tiếng đối đáp trôi chảy, đúng từng điển tích | **A** | `File:Qianlong by Castiglione.jpg (Càn Long Castiglione)` | Focus ánh mắt kinh ngạc của vị hoàng đế |
| **62 (64s–67s)** | Càn Long kinh ngạc trước diện mạo tuấn tú và trí tuệ mẫn tiệp của chàng thị vệ trẻ | **A** | `File:Hesen (cropped).jpg (Chân dung Hòa Thân)` | Zoom vào ánh mắt thông minh, đĩnh đạc |
| **63 (67s–71s)** | Chỉ trong vòng vài tháng, ông được đổi tên thành Hòa Thân và điều về hầu cận | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom cận cảnh chân dung tân quan sủng thần |
| **64 (71s–75s)** | Nắm giữ Phủ Nội Vụ, cơ quan quản lý toàn bộ tài chính riêng của hoàng đế | **C** | `ai_05.png (Cán cân công lý và thỏi bạc cổ)` | Ken Burns đòn cân bạc nghiêng nhẹ |
| **65 (75s–79s)** | Ông biến quỹ riêng của hoàng đế từ thâm hụt thành dư thừa dồi dào | **A** | `output/long/hoa-than/img/court_jifu_robe.jpg (Cát phục quan triều Thanh)` | Pan dọc hoa văn rồng cuộn chỉ vàng |
| **66 (79s–83s)** | Ngày 22 tháng 4 năm 1776, Hòa Thân chính thức được bổ nhiệm vào Quân cơ xứ | **D** | `date ("22.04.1776 · BỔ NHIỆM VÀO QUÂN CƠ XỨ")` | Mốc ngày quan trọng hiện trang trọng |
| **67 (83s–87s)** | Khi đó, ông mới tròn 26 tuổi — độ tuổi trẻ hiếm thấy trong lịch sử triều Mãn | **D** | `counter (26 TUỔI · QUÂN CƠ ĐẠI THẦN)` | Số tuổi đếm từ 22 lên 26 |
| **68 (87s–91s)** | Bài viết tiếng Việt nén quá trình này thành 'một năm sau', nhưng sử liệu ghi rõ 4 năm | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Ken Burns pan dọc y phục triều đình |
| **69 (91s–95s)** | Bước vào Quân cơ xứ nghĩa là bước vào trái tim điều hành toàn bộ đế chế | **A** | `File:Hall of Supreme Harmony.jpg (Thái Hòa Điện)` | Góc rộng cung điện lộng lẫy |
| **70 (95s–99s)** | Càn Long nhìn thấy ở Hòa Thân không chỉ một cận thần, mà là một cánh tay đắc lực | **A** | `File:Qianlong in old age.jpg (Càn Long)` | Zoom vào ánh mắt sủng ái của hoàng đế |
| **71 (99s–103s)** | Quyền lực gia tăng đi kèm với những đặc ân vượt bậc | **C** | `ai_16.png (Bóng ngai vàng và quyền lực tối cao)` | Bóng ngai vàng phủ dài trên sàn đá |
| **72 (103s–107s)** | Đỉnh điểm là đặc quyền chưa từng có dành cho một đại thần mới ngoài hai mươi | **B** | `vid_01.mp4 (Mái ngói Cố Cung)` | Camera trôi nhẹ qua mái hoàng lưu ly |
| **73 (107s–111s)** | Năm 1777 đánh dấu cột mốc làm rúng động toàn bộ triều đình Bắc Kinh | **D** | `date ("1777 · NĂM BẢN LỀ")` | Năm 1777 phát sáng |
| **74 (111s–115s)** | Một viên quan trẻ được phép cưỡi ngựa đi thẳng vào Tử Cấm Thành | **D** | `slam ("CƯỠI NGỰA TRONG TỬ CẤM THÀNH")` | Dòng chữ lớn đập mạnh |
| **75 (115s–119s)** | Và cũng trong năm ấy, những viên gạch đầu tiên của dinh thự Zhizhai được đặt xuống | **A** | `File:Prince Gong's Mansion - Main Gate.jpg (Cổng phủ)` | Pan chi tiết trụ đá chạm khắc |
| **76 (119s–123s)** | Khởi đầu của một cơ ngơi nguy nga bên hồ Thập Sát Hải | **A** | `File:Shichahai Lake Beijing.jpg (Hồ Thập Sát Hải)` | Góc máy phong cảnh hồ nước yên ả |
| **77 (123s–126s)** | Mô-típ bản kê bắt đầu ghi nhận những dòng tài sản đầu tiên | **D** | `ledger (DÒNG 01: KHỞI ĐẦU TỪ TƯ GIA BẮC KINH NĂM 1777)` | Dòng bản kê chạy vào cố định |
| **78 (126s–130s)** | Bước vào chương ba: Năm 27 tuổi đầy huy hoàng | **D** | `chapter (CHƯƠNG 02: THỊ VỆ CỬA CUNG)` | Đóng chương 2 chuyển tiếp mượt mà |

**Tổng kết số liệu chương:**
- Số nhịp: **33 nhịp** | Thời lượng: **130s** | Nhịp trung bình: **3.94s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 71s (54.6%)** | Nhóm B: 12s (9.2%) | Nhóm C: 8s (6.2%) | **Nhóm B+C: 20s (15.4%)** | **Nhóm D: 39s (30.0%)**.
- Số ảnh A sử dụng: **16 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 2 đạt 71s nhóm A (54.6%), sử dụng 18 ảnh tư liệu A (cờ Chính Hồng kỳ, bản đồ Cố Cung 2 lần, Thái Hòa Môn, Bát Kỳ duyệt binh, Ngọ Môn, Càn Long giáp vàng, Càn Thanh Cung, Castiglione, áo cát phục, Thái Hòa Điện, cổng phủ, Thập Sát Hải, chân dung Hòa Thân). D hỗ trợ các mốc ngày thăng tiến (1750, 1772, 1775, 1776, 1777) và slam danh hiệu.

### CH03: Hai mươi bảy tuổi (120 giây, 30 nhịp, trung bình 4.00s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **79 (0s–4s)** | Năm 1777, Hòa Thân tròn 27 tuổi, nhận đặc ân cưỡi ngựa trong Tử Cấm Thành | **D** | `counter (27 TUỔI · ĐẶC ÂN TỬ CẤM THÀNH)` | Bộ đếm dừng ở 27 tuổi, vầng hào quang nhẹ |
| **80 (4s–8s)** | Theo điển lệ triều Thanh, đặc ân này vốn chỉ ban cho các nguyên lão trên 65 tuổi | **A** | `File:The Qianlong Emperor in Ceremonial Armour on Horseback.jpg` | Slow pan chi tiết giáp vàng và yên ngựa Càn Long |
| **81 (8s–12s)** | Hình ảnh vị đại thần trẻ tuổi cưỡi ngựa qua các cổng thành làm cả kinh thành kinh ngạc | **B** | `ai_10.png (Con đường cưỡi ngựa trong Tử Cấm Thành)` | Ken Burns pan theo bóng ngựa chạy dọc tường đỏ |
| **82 (12s–16s)** | Càn Long yêu quý ông không chỉ vì tài năng mà còn coi như tri kỷ | **A** | `File:Qianlong by Castiglione.jpg (Càn Long)` | Pan từ từ vào ánh mắt cưng chiều của Càn Long |
| **83 (16s–20s)** | Hoàng đế thường xuyên ban tặng những bảo mã ngự dụng quý giá nhất | **A** | `File:Castiglione - Chaoerji.jpg (Ngự mã Siêu Nhị)` | Chiêm ngưỡng bức tranh ngự mã trứ danh |
| **84 (20s–24s)** | Bức tranh ngự mã Lai Viễn Lưu do họa sĩ cung đình Lang Thế Ninh vẽ | **A** | `File:Castiglione - Laiyuanliu.jpg (Ngự mã Lai Viễn Lưu)` | Pan chi tiết bờm ngựa và yên cương lộng lẫy |
| **85 (24s–28s)** | Cùng những chiến mã huyền thoại Nguyệt Quật Lai và Lăng Côn Bạch | **A** | `File:Castiglione - Yuekuelai.jpg (Ngự mã Nguyệt Quật Lai)` | Zoom vào dáng chạy dũng mãnh |
| **86 (28s–32s)** | Ngựa quý và bổng lộc triều đình liên tiếp đổ về phủ đệ | **A** | `File:Castiglione - Lingkunbai.jpg (Ngự mã Lăng Côn Bạch)` | Pan toàn cảnh bức họa ngự mã |
| **87 (32s–36s)** | Cũng trong năm 1777 định mệnh, ông khởi công xây dựng đại dinh thự Zhizhai | **D** | `date ("1777 · KHỞI CÔNG PHỦ ĐỆ ZHIZHAI")` | Mốc năm 1777 nổi bật kèm sơ đồ vị trí |
| **88 (36s–40s)** | Khu đất vàng tọa lạc ngay phía bắc Thập Sát Hải, vị trí phong thủy đắc địa nhất | **A** | `File:Shichahai Lake Beijing.jpg (Hồ Thập Sát Hải)` | Góc rộng hồ nước Thập Sát Hải phía bắc vương phủ |
| **89 (40s–44s)** | Dinh thự được xây dựng với quy mô và kiến trúc vượt xa quy chế đại thần | **B** | `ai_11.png (Công trường xây dựng phủ đệ năm 1777)` | Góc máy rộng công trường mái ngói gỗ đồ sộ |
| **90 (44s–48s)** | Hàng ngàn thợ thủ công giỏi nhất được điều động từ khắp các tỉnh phương Nam | **C** | `ai_04.png (Rương kho báu trong hầm đá)` | Ánh sáng quét qua các rương ngân lượng chi trả |
| **91 (48s–52s)** | Khuôn viên dinh thự mô phỏng kiến trúc thu nhỏ của chính Ninh Thọ Cung | **A** | `File:Nine Dragon Screen Forbidden City.jpg (Cửu Long Bích)` | Pan dọc chi tiết phù điêu rồng ngọc lưu ly |
| **92 (52s–56s)** | Gỗ lim vàng Nam mộc quý hiếm, vốn chỉ dành riêng cho hoàng đế, được đưa vào tư dinh | **A** | `File:Prince Gong's Mansion - Anshan Hall.jpg (An Thiện Đường)` | Zoom vào cột gỗ lim nguyên khối thế kỷ 18 |
| **93 (56s–60s)** | Đại sảnh Gia Lạc Đường với trần nhà chạm trổ hàng trăm chữ Phúc hoa mỹ | **A** | `File:Prince Gong's Mansion - Jiale Hall.jpg (Gia Lạc Đường)` | Góc hất lên trần nhà chạm khắc hoa văn |
| **94 (60s–64s)** | Hệ thống hồi lang dài hàng trăm mét nối liền các viện trang nhã | **B** | `vid_03.mp4 (Hành lang sơn son phủ đệ cổ)` | Dolly shot lướt mượt mà dọc dãy cột đỏ |
| **95 (64s–68s)** | Càn Long đích thân ban tặng thơ ngự chế và thư pháp để treo tại phòng khách | **A** | `output/long/hoa-than/img/qianlong_poem_flowers.jpg (Thơ ngự chế Càn Long)` | Pan từng dòng chữ ngự bút thư pháp thanh thoát |
| **96 (68s–72s)** | Sự sủng ái vô bờ bến của hoàng đế khiến không ai dám lên tiếng can gián | **D** | `slam ("SỰ SỦNG ÁI KHÔNG GIỚI HẠN")` | Chữ đập mạnh dứt khoát |
| **97 (72s–76s)** | Hòa Thân trở thành người nắm giữ chìa khóa tài chính và quyền uy triều đình | **C** | `ai_07.png (Chùm chìa khóa đồng và ổ khóa phong ấn)` | Ánh sáng làm nổi bật vòng khóa đồng |
| **98 (76s–80s)** | Nhưng quyền lực lớn luôn đi kèm với những ánh mắt dòm ngó của đình thần | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Focus vào gương mặt điềm tĩnh, tự tin |
| **99 (80s–84s)** | Đặc biệt là những trọng thần kỳ cựu theo phái thanh liêm chính thống | **A** | `File:Liu Yong.png (Chân dung Lưu Dung)` | Chân dung Lưu Dung xuất hiện đối chiếu |
| **100 (84s–88s)** | Một trong những nhân vật nổi tiếng nhất đương thời chính là Lưu Dung | **A** | `output/long/hoa-than/img/wenguan_portrait_1.jpg (Quan văn triều Thanh)` | Pan theo vạt áo thêu bổ phục |
| **101 (88s–92s)** | Mối quan hệ giữa hai người sẽ bước vào giai đoạn thử thách lớn nhất | **D** | `timeline (Mốc 1777 -> 1784: Chuẩn bị cùng nhậm chức)` | Đồ họa mũi tên kết nối hai nhân vật |
| **102 (92s–96s)** | Khi cả hai cùng bước vào sảnh đường Bộ Lại vào năm 1784 | **A** | `output/long/hoa-than/img/wenguan_portrait_2.jpg (Quan văn triều Thanh)` | Zoom chi tiết mũ quan đính ngọc |
| **103 (96s–100s)** | Phủ đệ hoàn thành, cơ ngơi ngày một đồ sộ | **A** | `File:Prince Gong Mansion Garden.jpg (Hoa viên Cung Vương Phủ)` | Toàn cảnh góc hồ và giả sơn thanh bình |
| **104 (100s–104s)** | Dòng thứ hai của bản kê được khắc ghi vào biên niên sử | **D** | `ledger (DÒNG 02: DINH THỰ ZHIZHAI HOÀN THÀNH TẠI THẬP SÁT HẢI)` | Cập nhật dòng 2 của bản kê |
| **105 (104s–108s)** | Một năm 27 tuổi với quyền uy tột đỉnh và ngôi nhà huyền thoại | **D** | `slam ("TUỔI 27: ĐỈNH CAO DANH VỌNG")` | Chữ slam hiện ấn tượng |
| **106 (108s–112s)** | Chuẩn bị bước sang cuộc chạm trán lịch sử giữa hai vị thượng thư | **D** | `question ("LƯU DUNG VÀ HÒA THÂN: AI ĐỐI ĐẦU AI?")` | Chữ câu hỏi mở ra chương mới |
| **107 (112s–116s)** | Chân dung hai con người cùng chèo lái bộ máy nhân sự Đại Thanh | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Ken Burns chuyển từ Hòa Thân sang Lưu Dung |
| **108 (116s–120s)** | Khép lại chương 3, mở ra câu chuyện đồng liêu năm 1784 | **D** | `chapter (CHƯƠNG 03: HAI MƯƠI BẢY TUỔI)` | Thẻ chương chuyển cảnh hoàn tất |

**Tổng kết số liệu chương:**
- Số nhịp: **30 nhịp** | Thời lượng: **120s** | Nhịp trung bình: **4.00s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 68s (56.7%)** | Nhóm B: 12s (10.0%) | Nhóm C: 8s (6.7%) | **Nhóm B+C: 20s (16.7%)** | **Nhóm D: 32s (26.7%)**.
- Số ảnh A sử dụng: **17 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 3 đạt 68s nhóm A (56.7%), sử dụng 17 ảnh tư liệu A (4 bức ngự mã Castiglione, Cửu Long bích, An Thiện Đường, Gia Lạc Đường, hoa viên, Thập Sát Hải, Lưu Dung, quan văn, thơ ngự chế, chân dung Càn Long & Hòa Thân). D bổ trợ counter 27 tuổi, timeline 1777-1784 và slam danh vọng.

### CH04: Đồng liêu (125 giây, 31 nhịp, trung bình 4.03s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **109 (0s–4s)** | Ngày 4 tháng 9 năm 1784, một quyết định nhân sự đặc biệt được ban hành | **D** | `date ("04.09.1784 · BỔ NHIỆM THƯỢNG THƯ BỘ LẠI")` | Mốc ngày hiện rõ nét trên nền sẫm |
| **110 (4s–8s)** | Hòa Thân và Lưu Dung được bổ nhiệm cùng giữ chức Thượng thư Bộ Lại | **A** | `output/long/hoa-than/img/wenguan_portrait_1.jpg (Quan văn triều Thanh CC0)` | Pan dọc bức chân dung quan văn uy nghiêm |
| **111 (8s–12s)** | Bộ Lại là cơ quan đứng đầu Lục bộ, nắm quyền khảo khóa, thăng giáng toàn bộ quan lại | **A** | `output/long/hoa-than/img/wenguan_portrait_2.jpg (Quan văn triều Thanh CC0)` | Đối chiếu bức chân dung quan văn thứ hai |
| **112 (12s–16s)** | Cơ chế một người Mãn, một người Hán cùng đứng đầu một bộ là truyền thống nhà Thanh | **A** | `File:Liu Yong.png (Chân dung Lưu Dung)` | Zoom vào chân dung Lưu Dung nét mặt điềm đạm |
| **113 (16s–20s)** | Phim truyền hình 'Tể tướng Lưu gù' biến hai người thành kẻ thù sống chết | **D** | `quote ("PHIM ẢNH: KẺ THÙ SỐNG CHẾT · ĐỜI THẬT: ĐỒNG LIÊU CÙNG BỘ")` | Thẻ trích dẫn tương phản phim - đời |
| **114 (20s–24s)** | Nhưng trong suốt hai năm nhiệm kỳ, hồ sơ triều đình không hề ghi nhận cuộc xung đột nảy lửa nào | **A** | `File:Ji Yun.jpg (Chân dung Kỷ Hiểu Lam)` | Chân dung Kỷ Hiểu Lam, đồng sự thân thiết |
| **115 (24s–28s)** | Lưu Dung là bậc đại danh sĩ thông tuệ, thư pháp trứ danh, tính tình cẩn trọng kín kẽ | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Pan chi tiết áo thụng quan triều |
| **116 (28s–32s)** | Ông hiểu rõ sự sủng ái tuyệt đối của Càn Long dành cho Hòa Thân nên chọn cách ôn hòa | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom vào ánh mắt kiên định, tự tin |
| **117 (32s–36s)** | Đại sảnh Bộ Lại hàng ngày chứng kiến hai vị thượng thư cùng nhau ký tấu sớ | **B** | `ai_12.png (Đại sảnh Bộ Lại trang nghiêm)` | Góc máy hất lên trần gỗ và hai chiếc ghế quan |
| **118 (36s–40s)** | Những vụ án thanh tra lớn bắt đầu bộc lộ tài năng phá án xuất chúng của Hòa Thân | **C** | `ai_05.png (Cán cân công lý và thỏi bạc cổ)` | Ken Burns đòn cân lắc nhẹ |
| **119 (40s–44s)** | Năm 1781, vụ đại án tham nhũng Cam Túc làm chấn động triều đình phương Bắc | **A** | `File:Qing Dynasty Administrative Map.jpg (Bản đồ hành chính Đại Thanh)` | Vẽ đường khoanh đỏ tỉnh Cam Túc trên bản đồ cổ |
| **120 (44s–48s)** | Tuần phủ Vương Đàm Vọng thông đồng quan lại khai man hạn hán để bỏ túi hàng triệu lạng bạc cứu đói | **A** | `output/long/hoa-than/img/court_jifu_robe.jpg (Cát phục quan triều Thanh)` | Pan dọc hoa văn rồng cuộn chỉ vàng |
| **121 (48s–52s)** | Càn Long phái Hòa Thân cùng A Quế tới tận nơi điều tra làm rõ chân tướng | **A** | `File:Agui.jpg (Chân dung A Quế)` | Chân dung tướng quân A Quế cương nghị |
| **122 (52s–56s)** | Hòa Thân dùng mưu lược bóc trần toàn bộ mạng lưới giả mạo sổ sách cứu trợ | **B** | `vid_05.mp4 (Cuộn tấu sớ đóng kín dưới ánh nến)` | Camera lướt qua các cuộn tấu sớ niêm phong |
| **123 (56s–60s)** | Vụ án kết thúc với hàng chục quan lại bị xử trảm, thu hồi hàng triệu lạng cho quốc khố | **D** | `slam ("PHÁ VỤ ĐẠI ÁN CAM TÚC")` | Chữ slam khẳng định chiến tích |
| **124 (60s–64s)** | Tuy nhiên năm 1784, ông từng bị triệu hồi khỏi chiến dịch Cam Túc do bất đồng phương án tác chiến | **A** | `File:The Qianlong Emperor in Ceremonial Armour on Horseback.jpg` | Zoom vào chi tiết ấn kiếm chỉ huy |
| **125 (64s–68s)** | Điều đó không làm suy giảm quyền lực mà ngược lại, Càn Long muốn giữ ông cạnh mình | **A** | `File:Qianlong Southern Inspection Tour.jpg (Tuần du phương Nam)` | Tranh cuộn hoàng đế ngự thuyền du hành |
| **126 (68s–72s)** | Trong các chuyến Nam tuần tốn kém, Hòa Thân luôn là người xoay xở đủ ngân sách dồi dào | **A** | `output/long/hoa-than/img/court_jifu_robe.jpg (Cát phục quan triều Thanh)` | Pan dọc hoa văn rồng cuộn chỉ vàng |
| **127 (72s–76s)** | Ngày 16 tháng 9 năm 1786, Lưu Dung được điều chuyển sang ngạch quan khác | **D** | `date ("16.09.1786 · KẾT THÚC HAI NĂM ĐỒNG SỰ")` | Mốc kết thúc nhiệm kỳ hiển thị rõ |
| **128 (76s–80s)** | Hai năm làm việc cùng nhau kết thúc trong hòa bình, không hề có chuyện 'đấu trí cung đình' | **A** | `File:Liu Yong.png (Lưu Dung)` | Chân dung Lưu Dung bên cạnh Hòa Thân |
| **129 (80s–84s)** | Phim ảnh cần xung đột kịch tính nên đã tô vẽ nên những màn đối đầu hư cấu | **A** | `File:Heshen 2.jpg (Hòa Thân)` | Ken Burns giữ hình ảnh trang nghiêm |
| **130 (84s–88s)** | Thực tế, Hòa Thân tiếp tục thâu tóm thêm Bộ Hộ, Bộ Binh và Viện Hàn Lâm | **C** | `ai_16.png (Bóng ngai vàng và quyền lực tối cao)` | Bóng quyền lực trùm lên các cơ quan triều đình |
| **131 (88s–92s)** | Một mình kiêm nhiệm hàng chục chức vụ then chốt nhất của bộ máy đế chế | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom-in vào ánh mắt quyền uy tuyệt đối |
| **132 (92s–96s)** | Đêm đêm tại thư phòng riêng, mạng lưới nhân sự khắp các tỉnh được ông sắp đặt | **B** | `ai_02.png (Thư phòng cổ vắng lặng trong đêm)` | Ánh nến soi rọi chồng tấu sớ trên bàn |
| **133 (96s–100s)** | Đến cuối thập niên 1780, thế lực của ông đã bám rễ sâu vào mọi ngóc ngách | **D** | `counter (KIÊM NHIỆM HƠN 20 CHỨC VỤ TRỌNG YẾU)` | Bộ đếm chức danh kiêm nhiệm |
| **134 (100s–104s)** | Nhưng mối liên kết vững chắc nhất với hoàng tộc vẫn chưa chính thức xuất hiện | **D** | `question ("LÀM THẾ NÀO ĐỂ BẢO VỆ ĐẾ CHẾ QUYỀN LỰC?")` | Chữ câu hỏi dẫn dắt người xem |
| **135 (104s–108s)** | Câu trả lời nằm ở một cuộc hôn nhân thế kỷ giữa hai gia tộc | **A** | `File:Palace of Heavenly Purity.jpg (Càn Thanh Cung)` | Pan góc cung điện hoàng gia |
| **136 (108s–112s)** | Khi con trai ông lọt vào mắt xanh của Càn Long để chọn làm phò mã | **D** | `slam ("LIÊN MINH HÔN NHÂN HOÀNG TỘC")` | Chữ đập mạnh báo hiệu chương mới |
| **137 (112s–116s)** | Dòng thứ ba của bản kê tiếp tục ghi nhận sự bành trướng quyền lực | **D** | `ledger (DÒNG 03: ĐỨNG ĐẦU BỘ LẠI VÀ BỘ HỘ · NẮM TRỌN NHÂN SỰ VÀ TÀI CHÍNH)` | Cập nhật dòng 3 mô-típ bản kê |
| **138 (116s–121s)** | Chân dung vị đại thần năm 1786 vững như bàn thạch | **A** | `File:Heshen 2.jpg (Hòa Thân)` | Ken Burns giữ hình ảnh trang nghiêm |
| **139 (121s–125s)** | Chuyển sang chương 5: Cuộc hôn nhân với công chúa Hòa Hiếu năm 1790 | **D** | `chapter (CHƯƠNG 04: ĐỒNG LIÊU)` | Thẻ chương chuyển tiếp dứt khoát |

**Tổng kết số liệu chương:**
- Số nhịp: **31 nhịp** | Thời lượng: **125s** | Nhịp trung bình: **4.03s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 69s (55.2%)** | Nhóm B: 12s (9.6%) | Nhóm C: 8s (6.4%) | **Nhóm B+C: 20s (16.0%)** | **Nhóm D: 36s (28.8%)**.
- Số ảnh A sử dụng: **12 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 4 đạt 69s nhóm A (55.2%), sử dụng 16 ảnh tư liệu A (2 quan văn CC0, Lưu Dung, Kỷ Hiểu Lam, A Quế, Càn Long giáp vàng, Nam tuần, bản đồ hành chính, áo cát phục, Càn Thanh Cung, chân dung Hòa Thân). D hỗ trợ ngày 1784, 1786, slam giải ảo tử thù và counter chức danh kiêm nhiệm.

### CH05: Công chúa Hòa Hiếu (115 giây, 29 nhịp, trung bình 3.97s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **140 (0s–4s)** | Năm 1790, một sự kiện trọng đại diễn ra: Hôn lễ của Thập công chúa triều Càn Long | **A** | `File:Princess Hexiao.jpg (Chân dung Cố Luân Hòa Hiếu công chúa)` | Mốc đại hôn hiện lên trên nền chân dung công chúa |
| **141 (4s–8s)** | Cố Luân Hòa Hiếu công chúa là con gái thứ mười, người được Càn Long yêu thương nhất | **A** | `File:Princess Hexiao.jpg (Công chúa Hòa Hiếu)` | Ken Burns zoom cận cảnh dung nhan công chúa |
| **142 (8s–12s)** | Công chúa có tính cách cương nghị, thích cưỡi ngựa bắn cung, diện mạo giống hệt Càn Long | **A** | `File:Qianlong with Imperial Consorts.jpg (Càn Long và hậu phi)` | Pan qua khung cảnh cung đình quý phái |
| **143 (12s–16s)** | Hoàng đế từng nói: 'Nếu con là hoàng tử, trẫm nhất định sẽ lập con làm thái tử' | **A** | `File:The Qianlong Emperor in Ceremonial Armour on Horseback.jpg` | Focus ánh mắt kiêu hãnh của Càn Long |
| **144 (16s–20s)** | Phò mã được chọn không ai khác chính là Phong Thân Ân Đức, con trai cả của Hòa Thân | **A** | `output/long/hoa-than/img/bridal_dragon_robe.jpg (Long bào hôn lễ)` | Pan chi tiết chỉ vàng long bào phò mã |
| **145 (20s–24s)** | Tên gọi 'Phong Thân Ân Đức' do chính Càn Long đặt tặng, có nghĩa là phúc lộc dồi dào | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom cận cảnh nét cười thỏa mãn của Hòa Thân |
| **146 (24s–28s)** | Hôn lễ diễn ra với quy mô xa hoa chưa từng thấy trong hoàng tộc Đại Thanh | **B** | `ai_13.png (Nghi lễ hôn lễ hoàng tộc và đèn lồng)` | Toàn cảnh sân viện đèn lồng đỏ rực rỡ |
| **147 (28s–32s)** | Bộ lễ phục hôn lễ tráng lệ thêu chỉ vàng nguyên chất lộng lẫy | **A** | `output/long/hoa-than/img/bridal_dragon_robe.jpg (Long bào hôn lễ công chúa CC0)` | Zoom cận cảnh hoa văn rồng vàng và sóng biển thêu tay |
| **148 (32s–36s)** | Ánh đèn lồng đỏ lung linh thắp sáng toàn bộ dinh thự Zhizhai suốt nhiều đêm | **B** | `vid_04.mp4 (Đèn lồng đỏ lung linh trong đêm hỷ sự)` | Focus pull chậm rãi qua dãy đèn lồng lụa đỏ |
| **149 (36s–40s)** | Khôn Ninh Cung, nơi tổ chức các nghi thức đại hôn hoàng thất | **A** | `File:Palace of Earthly Tranquility.jpg (Khôn Ninh Cung)` | Góc rộng cung điện linh thiêng |
| **150 (40s–44s)** | Của hồi môn Càn Long ban cho công chúa trị giá hàng triệu lạng bạc và bảo vật ngọc ngà | **C** | `ai_04.png (Sính lễ và của hồi môn hoàng gia)` | Ánh sáng quét qua các tráp ngọc quý |
| **151 (44s–48s)** | Hòa Thân chính thức trở thành thông gia của hoàng đế thiên triều | **A** | `File:Heshen 2.jpg (Chân dung Hòa Thân triều phục)` | Zoom vào phong thái đĩnh đạc |
| **152 (48s–52s)** | Mối liên minh hôn nhân này là đỉnh cao danh vọng nhưng cũng gieo mầm hiểm họa | **C** | `ai_07.png (Chiếc khóa vàng gắn kết thông gia hoàng tộc)` | Chiếc khóa vàng đóng chặt mang tính ẩn dụ |
| **153 (52s–56s)** | Các hoàng tử khác, đặc biệt là Thập ngũ hoàng tử Vĩnh Diễm (Gia Khánh sau này), bằng mặt không bằng lòng | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh)` | Focus ánh mắt trầm ngâm kiềm chế của Gia Khánh |
| **154 (56s–60s)** | Công chúa Hòa Hiếu là người phụ nữ thông tuệ, từng nhìn thấy trước nguy cơ diệt vong | **A** | `File:Princess Hexiao.jpg (Công chúa Hòa Hiếu)` | Pan chậm chi tiết hoa cài đầu ngọc trai |
| **155 (60s–64s)** | Bà từng nhiều lần khuyên chồng: 'Cha chàng quyền thế quá lớn, ngày sau ắt gặp họa' | **A** | `File:Prince Gong's Mansion - Anshan Hall.jpg (An Thiện Đường)` | Góc tĩnh lặng nơi ở của công chúa |
| **156 (64s–68s)** | Nhưng giữa cơn say quyền lực và sự bảo bọc tuyệt đối của Càn Long, không ai dừng lại | **B** | `vid_03.mp4 (Hành lang phủ đệ rực rỡ)` | Dolly lướt qua hồi lang sơn son tráng lệ |
| **157 (68s–72s)** | Kế hoạch bài này chỉ tập trung vào sự kiện có ngày tháng, không kể lan man danh sách thiếp | **D** | `split ("SỰ KIỆN CÓ NGUỒN: HÔN LỄ 1790" vs "BỎ QUA: DANH SÁCH THIẾP GIAI THOẠI")` | Đối chiếu tuân thủ nguyên tắc nội dung |
| **158 (72s–76s)** | Hòa Hiếu công chúa không chỉ là con dâu, mà chính là sợi dây bảo mệnh chín năm sau | **D** | `slam ("LÁ BÙA HỘ MỆNH DUY NHẤT")` | Chữ slam nhấn mạnh vai trò của công chúa |
| **159 (76s–80s)** | Khi cơn bão thanh trừng 1799 ập đến, sự nể trọng của Gia Khánh dành cho em gái đã cứu cả gia tộc | **A** | `File:Prince Gong Mansion Garden.jpg (Hoa viên Cung Vương Phủ)` | Pan bờ hồ và đình tạ bình yên |
| **160 (80s–84s)** | Một nửa phủ đệ Zhizhai vẫn được để lại cho công chúa và Phong Thân Ân Đức sinh sống | **A** | `File:Dingfu Gate Prince Gong.jpg (Cổng Đinh Phủ)` | Zoom vào cổng vòm đá xanh |
| **161 (84s–88s)** | Thập niên 1790 mở ra với vị thế độc tôn của Hòa Thân trên chính trường | **C** | `ai_16.png (Bóng ngai vàng và quyền lực tối cao)` | Bóng quyền uy vươn dài |
| **162 (88s–92s)** | Không chỉ thống trị triều chính nội trị, ông còn đại diện cho hoàng đế tiếp đón phương Tây | **D** | `question ("PHƯƠNG TÂY NHÌN NHẬN HÒA THÂN NHƯ THẾ NÀO?")` | Chữ câu hỏi mở ra tầm nhìn ngoại giao |
| **163 (92s–96s)** | Năm 1793, đoàn sứ thần Anh quốc của Huân tước Macartney đặt chân đến Trung Hoa | **D** | `counter (NĂM 1793 · ĐOÀN SỨ THẦN MACARTNEY)` | Mốc số năm 1793 nổi bật |
| **164 (96s–100s)** | Hòa Thân bước ra vũ trường ngoại giao quốc tế với vai trò toàn quyền tiếp đón | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Pan phong thái quý tộc ngoại giao |
| **165 (100s–104s)** | Bản kê tiếp tục ghi nhận mối liên kết hoàng tộc vô giá | **D** | `ledger (DÒNG 04: LIÊN MINH HÔN NHÂN CÔNG CHÚA HÒA HIẾU · SÍNH LỄ HOÀNG GIA)` | Cập nhật dòng 4 bản kê |
| **166 (104s–108s)** | Đỉnh cao quyền lực gia đình và chính trị đan kết chặt chẽ | **D** | `slam ("GIA ĐÌNH VÀ HOÀNG GIA ĐAN KẾT")` | Chữ đập mạnh dứt khoát |
| **167 (108s–111s)** | Sẵn sàng cho cuộc đối đầu ngoại giao lớn nhất thế kỷ 18 | **A** | `File:Palace of Heavenly Purity.jpg (Cung điện)` | Zoom chậm Cố Cung trang nghiêm |
| **168 (111s–115s)** | Khép lại chương 5, mở ra chương 6: Sứ đoàn năm 1793 | **D** | `chapter (CHƯƠNG 05: CÔNG CHÚA HÒA HIẾU)` | Thẻ chương chuyển cảnh hoàn hảo |

**Tổng kết số liệu chương:**
- Số nhịp: **29 nhịp** | Thời lượng: **115s** | Nhịp trung bình: **3.97s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 63s (54.8%)** | Nhóm B: 12s (10.4%) | Nhóm C: 12s (10.4%) | **Nhóm B+C: 24s (20.9%)** | **Nhóm D: 28s (24.3%)**.
- Số ảnh A sử dụng: **12 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 5 đạt 63s nhóm A (54.8%), sử dụng 15 ảnh tư liệu A (Công chúa Hòa Hiếu 3 lần, Càn Long hậu phi, long bào hôn lễ CC0 2 lần, Khôn Ninh Cung, Gia Khánh, An Thiện Đường, Cung Vương Phủ, Càn Thanh Cung, chân dung Hòa Thân). D hỗ trợ sơ đồ liên minh gia tộc, date 1790, counter sứ đoàn 1793.

### CH06: Sứ đoàn năm 1793 (140 giây, 34 nhịp, trung bình 4.12s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **169 (0s–4s)** | Mùa hè năm 1793, chiến hạm HMS Lion của Hoàng gia Anh đưa sứ đoàn Macartney tới Trung Hoa | **D** | `date ("HÈ 1793 · SỨ ĐOÀN HOÀNG GIA ANH QUỐC")` | Mốc thời gian hiện lên kèm huy hiệu |
| **170 (4s–8s)** | Huân tước George Macartney mang theo quốc thư của Vua George III và hàng trăm hòm tặng phẩm | **A** | `File:Lord Macartney Portrait.jpg (Chân dung Huân tước Macartney)` | Zoom cận cảnh chân dung Macartney đĩnh đạc |
| **171 (8s–12s)** | Mục tiêu là mở rộng thương mại, đặt đại sứ quán tại Bắc Kinh và nhượng lại một hòn đảo nhỏ | **A** | `File:Great Wall at Gubeikou Alexander.jpg (Ải Cổ Bắc Khẩu)` | Pan dọc bức tường thành hùng vĩ trong sương |
| **172 (12s–16s)** | Họa sĩ cung đình William Alexander đi theo đoàn đã phác họa lại toàn bộ chuyến đi lịch sử | **A** | `File:Alexander - Reception of Macartney.jpg (Tranh tiếp kiến Nhiệt Hà)` | Slow pan toàn cảnh lều tiệc hoàng gia tại Nhiệt Hà |
| **173 (16s–20s)** | Đoàn sứ thần di chuyển qua Vạn Lý Trường Thành tại ải Cổ Bắc Khẩu để đến Sơn Trang Nghỉ Mát | **A** | `File:Alexander - Imperial Barges.jpg (Thuyền ngự trên sông)` | Pan lướt theo đoàn thuyền cờ dong trống mở |
| **174 (20s–24s)** | Hòa Thân, với tư cách Lãnh ban Quân cơ và Tổng quản Nội vụ, là người trực tiếp đón tiếp sứ đoàn | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom vào phong thái tự tin, điềm tĩnh |
| **175 (24s–28s)** | Ông bố trí các thuyền ngự lộng lẫy đưa đoàn sứ thần đi dọc kênh đào | **A** | `File:Alexander - Chinese Military.jpg (Quân lính triều Thanh)` | Zoom vào chi tiết cung thủ và kỵ binh |
| **176 (28s–32s)** | Quân đội triều Thanh duyệt binh biểu dương lực lượng trước mắt người phương Tây | **A** | `File:Eight Banners review.jpg (Bát Kỳ duyệt binh)` | Pan dọc hàng quân chỉnh tề |
| **177 (32s–36s)** | Tại Sơn Trang Nghỉ Mát Nhiệt Hà, lễ mừng thọ 83 tuổi của Càn Long được tổ chức đại quy mô | **D** | `counter (83 TUỔI · ĐẠI THỌ CÀN LONG TẠI NHIỆT HÀ)` | Bộ đếm dừng ở 83 tuổi rực rỡ |
| **178 (36s–40s)** | Đại sảnh lều gấm tiếp đón sứ đoàn diễn ra trang nghiêm, lộng lẫy | **B** | `ai_14.png (Tiệc tiếp đón ngoại giao tại Nhiệt Hà 1793)` | Góc máy hất lên trần lều lụa và bàn tiệc |
| **179 (40s–44s)** | Một tranh cãi ngoại giao nảy lửa nổ ra xoay quanh nghi thức 'Tam quỳ cửu khấu' | **D** | `split ("NGHI THỨC ĐẠI THANH: TAM QUỲ CỬU KHẤU" vs "NGHI THỨC NƯỚC ANH: QUỲ MỘT GỐI")` | Hai cột đối chiếu nghi lễ ngoại giao |
| **180 (44s–48s)** | Hòa Thân đã khéo léo đàm phán, tìm ra giải pháp thỏa hiệp giữ thể diện cho cả hai bên | **A** | `File:Heshen 2.jpg (Hòa Thân)` | Pan từ từ phong thái nhà ngoại giao sắc sảo |
| **181 (48s–52s)** | Trong nhật ký của mình, Macartney đã dành những dòng đánh giá sâu sắc về Hòa Thân | **A** | `File:Lord Macartney Portrait.jpg (Macartney)` | Focus ánh nhìn tôn trọng của sứ thần |
| **182 (52s–56s)** | Macartney nhận xét: 'Ông ta là người lịch lãm nhất triều đình, nắm bắt ý đồ đối phương cực nhanh' | **D** | `quote ("MỘT VỊ ĐẠI THẦN TAO NHÃ, LỊCH THIỆP, CỰC KỲ SẮC SẢO VÀ KIÊN QUYẾT · MACARTNEY")` | Trích nhật ký Macartney bằng chữ trang trọng |
| **183 (56s–60s)** | Những tặng phẩm khoa học hiện đại: kính thiên văn, đồng hồ thiên văn, súng trường tối tân | **C** | `ai_04.png (Rương quà tặng ngoại giao và thiên triều)` | Ánh sáng quét qua các cỗ máy bánh răng đồng |
| **184 (60s–64s)** | Càn Long và Hòa Thân xem chúng như những món đồ chơi kỳ xảo chứ không nhận ra giá trị quân sự | **A** | `File:Qianlong in old age.jpg (Càn Long tuổi già)` | Pan nét mặt lạnh lùng thờ ơ của hoàng đế |
| **185 (64s–68s)** | Triều đình từ chối toàn bộ các yêu sách mở cửa thương mại và đặt sứ quán của Anh | **A** | `output/long/hoa-than/img/emperor_jifu_robe.jpg (Long bào hoàng đế)` | Pan vạt áo long bào uy nghiêm |
| **186 (68s–72s)** | Biếm họa James Gillray năm 1793 tại Luân Đôn mỉa mai chuyến đi thất bại của Macartney | **A** | `File:James Gillray - The Reception of the Diplomatic and his Suite.jpg` | Zoom chi tiết tranh biếm họa châm biếm nổi tiếng |
| **187 (72s–76s)** | Một khẳng định lịch sử quan trọng: Hòa Thân bảo vệ quyền lợi triều đình, không hề 'bán nước' | **D** | `slam ("BẢO VỆ CHỦ QUYỀN · TUYỆT ĐỐI KHÔNG BÁN NƯỚC")` | Chữ slam đập dứt khoát bác bỏ tin đồn |
| **188 (76s–80s)** | Ông thực thi đúng đường lối bế quan tỏa cảng của hoàng đế với sự kiên định ngoại giao cao nhất | **A** | `File:Alexander - Reception of Macartney.jpg (Tiếp kiến)` | Zoom vào bàn đàm phán trung tâm |
| **189 (80s–84s)** | Tuy nhiên, chuyến đi đã cho phương Tây thấy rõ sự già cỗi và tự mãn của đế chế nhà Thanh | **C** | `ai_16.png (Bóng quyền lực trước sứ thần Tây phương)` | Bóng ngai vàng cao ngất phủ bóng lạnh |
| **190 (84s–88s)** | Sau chuyến ngoại giao thắng lợi vẻ vang trên bề mặt, quyền lực của Hòa Thân càng thêm củng cố | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Focus vào phong thái tự tin tột cùng |
| **191 (88s–92s)** | Càn Long ngày một suy yếu về thể chất, giao phó gần như toàn quyền điều hành đất nước cho ông | **A** | `File:Palace of Heavenly Purity.jpg (Cung điện Càn Thanh)` | Pan dọc các cột rồng mờ trong khói trầm |
| **192 (92s–96s)** | Một giai đoạn bước ngoặt sắp sửa diễn ra khi hoàng đế bước vào tuổi 85 | **D** | `counter (85 TUỔI · CÀN LONG CHUẨN BỊ THOÁI VỊ)` | Bộ đếm tăng lên 85 tuổi |
| **193 (96s–100s)** | Lời hứa thoái vị sau 60 năm trị vì để không vượt quá thời gian của ông nội Khang Hy | **D** | `date ("02.1796 · THỜI ĐIỂM THOÁI VỊ ĐÃ ĐẾN")` | Mốc tháng 2/1796 xuất hiện |
| **194 (100s–104s)** | Một tình thế chưa từng có: Một hoàng đế thoái vị nhưng vẫn nắm quyền, và một đại thần làm 'Nhị hoàng đế' | **D** | `split ("CÀN LONG: THÁI THƯỢNG HOÀNG" vs "HÒA THÂN: 'NHỊ HOÀNG ĐẾ'")` | Thẻ chữ hai bên đối lập |
| **195 (104s–108s)** | Gia Khánh đăng cơ nhưng hoàn toàn bất lực trong việc điều hành | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh)` | Zoom vào khuôn mặt nghiêm nghị, nén nhịn |
| **196 (108s–112s)** | Bản kê tiếp tục ghi nhận vai trò ngoại giao toàn quyền của Hòa Thân | **D** | `ledger (DÒNG 05: TOÀN QUYỀN TIẾP ĐÓN SỨ ĐOÀN ANH QUỐC NĂM 1793)` | Cập nhật dòng 5 bản kê |
| **197 (112s–116s)** | Đỉnh cao uy tín quốc tế và sự tín nhiệm tuyệt đối từ thiên tử | **D** | `slam ("ĐỈNH CAO UY TÍN NGOẠI GIAO")` | Chữ slam hiện ấn tượng |
| **198 (116s–120s)** | Một chương ngoại giao rực rỡ nhưng là khúc dạo đầu cho giai đoạn chuyên quyền tột bậc | **B** | `ai_06.png (Cổng cung điện uy nghiêm)` | Góc rộng hoàng cung trong ráng chiều vàng |
| **199 (120s–125s)** | Bước vào chương 7: Giai đoạn 1796–1799, thời kỳ 'Hoàng đế trên danh' | **A** | `File:Hall of Supreme Harmony.jpg (Thái Hòa Điện)` | Góc máy rộng hùng tráng của hoàng cung |
| **200 (125s–130s)** | Mối quan hệ tay ba giữa Càn Long già yếu, Gia Khánh nhẫn nhục và Hòa Thân quyền thế | **A** | `File:Heshen 2.jpg (Hòa Thân)` | Chuyển động nhẹ giữa chân dung 3 nhân vật |
| **201 (130s–135s)** | Sự tĩnh lặng đáng sợ trước cơn giông bão tháng Hai năm 1799 | **B** | `vid_01.mp4 (Mái ngói Cố Cung)` | Camera trôi nhẹ qua hàng ngói âm dương |
| **202 (135s–140s)** | Khép lại chương 6, bước sang giai đoạn quyền lực tối thượng | **D** | `chapter (CHƯƠNG 06: SỨ ĐOÀN NĂM 1793)` | Thẻ chương kết thúc chương 6 |

**Tổng kết số liệu chương:**
- Số nhịp: **34 nhịp** | Thời lượng: **140s** | Nhịp trung bình: **4.12s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 74s (52.9%)** | Nhóm B: 13s (9.3%) | Nhóm C: 8s (5.7%) | **Nhóm B+C: 21s (15.0%)** | **Nhóm D: 45s (32.1%)**.
- Số ảnh A sử dụng: **14 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 6 đạt 74s nhóm A (52.9%), sử dụng 18 ảnh tư liệu A (Lord Macartney, ải Cổ Bắc Khẩu, 3 tranh William Alexander, Bát Kỳ, biếm họa Gillray 1793, áo long bào, Càn Long già, Gia Khánh, Càn Thanh Cung, Thái Hòa Điện, chân dung Hòa Thân). D hỗ trợ ngày tháng hè 1793, 1796, split nghi thức quỳ và slam bảo vệ chủ quyền.

### CH07: Hoàng đế trên danh (135 giây, 33 nhịp, trung bình 4.09s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **203 (0s–4s)** | Tháng 2 năm 1796, Càn Long chính thức thoái vị sau đúng 60 năm ngự trị ngai vàng | **D** | `date ("02.1796 · CÀN LONG THOÁI VỊ")` | Mốc tháng 2/1796 hiện uy nghiêm |
| **204 (4s–8s)** | Thập ngũ hoàng tử Vĩnh Diễm đăng cơ, lấy niên hiệu là Gia Khánh | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh triều phục)` | Pan chi tiết vương miện và áo long bào mới |
| **205 (8s–12s)** | Tuy nhiên, Càn Long không trao trả thực quyền mà giữ tước hiệu Thái thượng hoàng | **A** | `File:The Qianlong Emperor in Ceremonial Armour on Horseback.jpg` | Focus ấn kiếm và quyền lực của Thái thượng hoàng |
| **206 (12s–16s)** | Thái thượng hoàng chuyển sang ở tại Dưỡng Tâm Điện, tiếp tục ngự phê mọi tấu sớ quan trọng | **A** | `File:Qianlong in old age.jpg (Càn Long tuổi già)` | Focus ánh mắt già nua nhưng uy quyền |
| **207 (16s–20s)** | Chiếc áo long bào đại triều của hoàng đế vẫn được may đo tỉ mỉ từng đường kim | **A** | `output/long/hoa-than/img/emperor_jifu_robe.jpg (Long bào Càn Long CC0)` | Zoom cận cảnh chín con rồng thêu chỉ vàng |
| **208 (20s–24s)** | Do tuổi tác đã ngoài 85, giọng nói Càn Long thều thào khó nghe, tai nghễnh ngãng | **D** | `counter (86 TUỔI · SỨC KHỎE CÀN LONG SUY KIỆT)` | Bộ đếm dừng ở tuổi 86 |
| **209 (24s–28s)** | Người duy nhất có thể nghe và truyền đạt lại mệnh lệnh của Càn Long chính là Hòa Thân | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom vào dáng vẻ kề cận bên ngai |
| **210 (28s–32s)** | Trong các buổi thiết triều, Hòa Thân đứng ngay cạnh ngai rồng của Thái thượng hoàng | **B** | `ai_15.png (Thư phòng Quân cơ xứ đêm khuya)` | Ánh nến soi rọi chồng tấu sớ mật |
| **211 (32s–36s)** | Gia Khánh chỉ được ngồi ở một chiếc ghế thấp hơn bên cạnh, im lặng quan sát | **A** | `File:Hall of Supreme Harmony.jpg (Thái Hòa Điện)` | Góc rộng ngai vàng điện Thái Hòa |
| **212 (36s–40s)** | Dân gian và quan lại kinh thành bắt đầu gọi Hòa Thân bằng danh xưng: 'Nhị hoàng đế' | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Pan chi tiết mũ quan đính ngọc trai |
| **213 (40s–44s)** | Tháng 10 năm 1797, Lãnh ban Quân cơ đại thần A Quế qua đời vì tuổi già | **D** | `date ("10.1797 · TƯỚNG QUÂN A QUẾ QUA ĐỜI")` | Mốc ngày màu trắng viền đen |
| **214 (44s–48s)** | A Quế là vị nguyên lão duy nhất còn giữ được sự kiềm chế đối với Hòa Thân | **A** | `File:Agui.jpg (Chân dung A Quế)` | Chân dung A Quế với ánh nhìn nghiêm nghị |
| **215 (48s–52s)** | Sau cái chết của A Quế, Hòa Thân chính thức đảm nhiệm vị trí Lãnh ban Quân cơ xứ | **D** | `slam ("LÃNH BAN QUÂN CƠ XỨ: ĐỈNH CAO QUYỀN LỰC")` | Chữ đập mạnh dứt khoát |
| **216 (52s–56s)** | Từ ngày 12 tháng 10 năm 1797, không còn bất kỳ thế lực nào trong triều đình đủ sức ngăn cản ông | **C** | `ai_16.png (Bóng ngai vàng và quyền lực tối cao)` | Bóng đen ngai rồng bao trùm toàn bộ không gian |
| **217 (56s–60s)** | Các chiến dịch quân sự tốn kém: Dẹp giặc Bạch Liên Giáo, bình định biên ải | **A** | `output/long/hoa-than/img/qianlong_poem_siege.jpg (Bản ngự chế giải vây Hắc Thủy CC BY 4.0)` | Pan dọc dòng thơ ngự chế chiến công |
| **218 (60s–64s)** | Bản ngự chế đại thắng Qurman được lưu giữ trong kho lưu trữ hoàng gia | **A** | `output/long/hoa-than/img/qianlong_poem_victory.jpg (Bản ngự chế đại thắng Qurman CC BY 4.0)` | Zoom vào chữ ngự bút Càn Long |
| **219 (64s–68s)** | Hòa Thân lợi dụng ngân sách quân phí khổng lồ để điều phối và bớt xén hàng triệu lạng bạc | **C** | `vid_02.mp4 (Bạc nén cổ trong ánh nến)` | Camera lướt qua các khay bạc thỏi trong bóng tối |
| **220 (68s–72s)** | Mọi chức vụ bổ nhiệm quan lại từ trung ương đến địa phương đều phải qua tay ông | **C** | `ai_07.png (Chiếc khóa vạn năng nắm giữ đế chế)` | Chiếc chìa khóa đồng và then cài |
| **221 (72s–76s)** | Gia Khánh nhận thức sâu sắc mối nguy hiểm, chọn chiến lược nhẫn nhịn tuyệt đối | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh)` | Focus nét mặt đăm chiêu nhẫn nhịn |
| **222 (76s–80s)** | Hoàng đế trẻ luôn tỏ ra tôn kính, nhún nhường, thậm chí gọi Hòa Thân là 'đại thần trụ cột' | **A** | `output/long/hoa-than/img/wenguan_portrait_1.jpg (Quan văn triều Thanh)` | Pan dọc nét mặt trang nghiêm của các đại thần |
| **223 (80s–84s)** | Sự nhẫn nhục của Gia Khánh khiến Hòa Thân hoàn toàn mất cảnh giác | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom vào ánh mắt kiêu hãnh của Hòa Thân |
| **224 (84s–88s)** | Những cuộn tấu sớ mật được soạn thảo trong đêm khuya tại thư phòng | **B** | `vid_05.mp4 (Cuộn tấu sớ đóng kín dưới ánh nến)` | Camera tilt từ ngọn nến xuống cuộn tấu sớ |
| **225 (88s–92s)** | Mạng lưới phe cánh bao phủ khắp Lục bộ, Bát Kỳ và Phủ Nội Vụ | **A** | `output/long/hoa-than/img/court_jifu_robe.jpg (Cát phục quan triều Thanh)` | Pan chi tiết vạt áo quan đại thần |
| **226 (92s–96s)** | Nhưng toàn bộ quyền uy tối thượng đó chỉ dựa trên một điểm tựa duy nhất | **A** | `output/long/hoa-than/img/qianlong_essay_old_age.jpg (Ngự bút Càn Long tuổi già)` | Pan dòng ngự bút yếu ớt của Càn Long |
| **227 (96s–100s)** | Một điểm tựa đang ngày một tàn lụi theo từng cơn ho của vị Thái thượng hoàng 88 tuổi | **A** | `File:Qianlong in old age.jpg (Càn Long già)` | Pan từ từ dung mạo hao mòn của Càn Long |
| **228 (100s–104s)** | Mùa đông năm 1798 ập đến Bắc Kinh với những đợt rét cắt da cắt thịt | **B** | `ai_02.png (Thư phòng đèn dầu leo lét)` | Ánh đèn dầu lay lắt trước gió đông |
| **229 (104s–108s)** | Gia Khánh âm thầm chuẩn bị lực lượng, liên lạc với các tướng lĩnh trung thành | **A** | `File:Palace of Heavenly Purity.jpg (Càn Thanh Cung)` | Góc rộng cung điện chìm trong bóng tối |
| **230 (108s–112s)** | Ngày 7 tháng 2 năm 1799, thời khắc định mệnh cuối cùng đã điểm | **D** | `date ("07.02.1799 · HƠI THỞ CUỐI CÙNG")` | Mốc ngày 7/2/1799 hiện lên rực lửa |
| **231 (112s–116s)** | Càn Long băng hà, chấm dứt chiếc ô che chở vĩ đại nhất | **A** | `output/long/hoa-than/img/qianlong_temple_name.jpg (Tấu sớ dâng miếu hiệu)` | Pan dòng tấu sớ thương tiếc Càn Long |
| **232 (116s–120s)** | Bản kê ghi nhận giai đoạn nắm quyền sinh sát tối cao | **D** | `ledger (DÒNG 06: LÃNH BAN QUÂN CƠ XỨ · 'NHỊ HOÀNG ĐẾ' NẮM TOÀN BỘ TRIỀU CHÍNH)` | Cập nhật dòng 6 bản kê |
| **233 (120s–125s)** | Một quyền lực vô song nhưng biến mất chỉ trong đúng 15 ngày | **D** | `slam ("SỰ SỤP ĐỔ CHÓNG VÁNH TRONG 15 NGÀY")` | Chữ slam đập mạnh rúng động |
| **234 (125s–130s)** | Mở ra vòng 2: Vì sao Gia Khánh phải đợi đúng 3 năm? | **D** | `question ("VÌ SAO PHẢI ĐỢI ĐÚNG 3 NĂM?")` | Chữ câu hỏi mở ra câu trả lời |
| **235 (130s–135s)** | Bước vào chương 8: Năm ngày nghẹt thở thay đổi lịch sử | **D** | `chapter (CHƯƠNG 07: HOÀNG ĐẾ TRÊN DANH)` | Thẻ chương kết thúc chương 7 |

**Tổng kết số liệu chương:**
- Số nhịp: **33 nhịp** | Thời lượng: **135s** | Nhịp trung bình: **4.09s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 72s (53.3%)** | Nhóm B: 12s (8.9%) | Nhóm C: 12s (8.9%) | **Nhóm B+C: 24s (17.8%)** | **Nhóm D: 39s (28.9%)**.
- Số ảnh A sử dụng: **15 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 7 đạt 72s nhóm A (53.3%), sử dụng 18 ảnh tư liệu A (Gia Khánh, Càn Long giáp vàng, Càn Long già 2 lần, long bào CC0, Thái Hòa Điện, A Quế, 2 bản ngự chế Qurman & Hắc Thủy, quan văn, áo cát phục, ngự chế tuổi già, Càn Thanh Cung, tấu sớ, chân dung Hòa Thân). D hỗ trợ các mốc ngày 1796, 1797, 1799, counter tuổi 86 và slam sụp đổ.

### CH08: Năm ngày (130 giây, 32 nhịp, trung bình 4.06s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **236 (0s–4s)** | Ngày 7 tháng 2 năm 1799, Thái thượng hoàng Càn Long trút hơi thở cuối cùng tại Càn Thanh Cung | **D** | `date ("07.02.1799 · CÀN LONG BĂNG HÀ")` | Mốc ngày trắng nền đen trang nghiêm |
| **237 (4s–8s)** | Hưởng thọ 88 tuổi, vị hoàng đế sống thọ nhất lịch sử Trung Hoa chính thức nằm xuống | **A** | `output/long/hoa-than/img/qianlong_temple_name.jpg (Tấu sớ miếu hiệu Càn Long CC BY 4.0)` | Pan chậm dòng tấu sớ phong thụy hiệu |
| **238 (8s–12s)** | Toàn bộ Tử Cấm Thành khoác lên mình màu trắng tang tóc của quốc tang | **B** | `ai_17.png (Hành lang cung đình tang lễ Càn Long 1799)` | Dải lụa trắng tang rủ dài theo hàng cột đỏ |
| **239 (12s–16s)** | Hòa Thân được cử làm Tổng lý tang lễ, ngày đêm quỳ trước linh cữu hoàng đế | **A** | `File:Heshen.jpg (Chân dung Hòa Thân trong tang lễ)` | Focus nét mặt u sầu và bất an |
| **240 (16s–20s)** | Ông không hề hay biết rằng, vị trí chủ tang chính là cái bẫy hoàn hảo giam lỏng ông | **C** | `ai_18.png (Đồng hồ cát thời gian và sự sụp đổ)` | Cát vàng trong đồng hồ chảy siết xuống đáy |
| **241 (20s–24s)** | Tuyết rơi trắng xóa trên các mái ngói Cố Cung trong những ngày tang lễ lạnh lẽo | **B** | `vid_01.mp4 (Tuyết rơi trên mái ngói Cố Cung tháng 2/1799)` | Camera bay chậm qua rặng tuyết phủ |
| **242 (24s–28s)** | Đúng 5 ngày sau khi Càn Long mất, ngày 12 tháng 2 năm 1799, sấm sét giáng xuống | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh quyết đoán)` | Mốc ngày 12/2 giáng xuống trên nền chân dung Gia Khánh |
| **243 (28s–32s)** | Gia Khánh phát lệnh cách chức toàn bộ chức vụ của Hòa Thân và Phúc Trường An | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh)` | Zoom cận cảnh ánh mắt lạnh lùng của Gia Khánh |
| **244 (32s–36s)** | Lập tức hạ lệnh bắt giam vào ngục tối của Bộ Hình để thẩm vấn | **B** | `ai_01.png (Thị vệ áp giải trong đêm tuyết)` | Bóng thị vệ giải người qua cổng thành tuyết |
| **245 (36s–40s)** | Triều đình choáng váng trước tốc độ hành động thần tốc và quyết liệt của hoàng đế mới | **A** | `output/long/hoa-than/img/qianlong_temple_name.jpg (Tấu sớ đình thần)` | Pan lướt nét mực tấu sớ bàng hoàng |
| **246 (40s–44s)** | Ngày 15 tháng 2, chỉ 3 ngày sau khi bắt, bản định tội được công bố trước bá quan | **D** | `date ("15.02.1799 · CHỈ DỤ ĐỊNH TỘI")` | Mốc ngày 15/2 hiện ra |
| **247 (44s–48s)** | Gia Khánh ban bố chỉ dụ kết án Hòa Thân phạm đại tội, xử phạt bằng cực hình lăng trì | **A** | `File:Hall of Supreme Harmony.jpg (Thái Hòa Điện)` | Góc máy rộng bao trùm thềm đá điện Thái Hòa |
| **248 (48s–52s)** | Điện Thái Hòa xôn xao, các quan đại thần quỳ rạp trước uy quyền tân đế | **A** | `output/long/hoa-than/img/wenguan_portrait_1.jpg (Quan văn triều Thanh)` | Pan dọc nét mặt bàng hoàng của các quan |
| **249 (52s–56s)** | Tin tức truyền đến dinh thự Zhizhai, công chúa Hòa Hiếu lập tức vào cung quỳ lạy van xin | **A** | `File:Princess Hexiao.jpg (Công chúa Hòa Hiếu)` | Zoom vào giọt nước mắt của công chúa |
| **250 (56s–60s)** | Công chúa khóc xin hoàng huynh niệm tình phụ hoàng vừa mất và thể diện hoàng gia | **A** | `File:Prince Gong's Mansion - Anshan Hall.jpg (An Thiện Đường)` | Góc tĩnh lặng nơi ở của công chúa |
| **251 (60s–64s)** | Nhiều đại thần thanh liêm cũng dâng tấu khuyên can: Không nên dùng cực hình với đại thần trong tang kỳ | **A** | `output/long/hoa-than/img/wenguan_portrait_2.jpg (Quan văn triều Thanh)` | Pan dọc bức chân dung quan văn can gián |
| **252 (64s–68s)** | Gia Khánh, một mặt muốn trừ khử mối họa, mặt khác rất thương yêu cô em gái duy nhất | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh suy xét)` | Ánh mắt hoàng đế trầm ngâm suy tính |
| **253 (68s–72s)** | Ngày 22 tháng 2 năm 1799, chỉ dụ cuối cùng được ban bố tại tư dinh Hòa Thân | **D** | `date ("22.02.1799 · CHỈ DỤ ĐỔI ÁN TỰ TẬN")` | Mốc ngày 22/2/1799 hiện lên sắc nét |
| **254 (72s–76s)** | Đổi án từ lăng trì thị chúng thành ân ban cho tự vẫn bằng cách thắt cổ tại nhà riêng | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Pan từ tà áo quan lên nét mặt buông xuôi |
| **255 (76s–80s)** | Một dải lụa trắng được đưa đến tư dinh Zhizhai, khép lại sinh mạng của vị đại thần | **C** | `ai_03.png (Biểu tượng dải lụa đổi án)` | Ánh sáng bên hông chiếu lên dải lụa trắng |
| **256 (80s–84s)** | Không có máu chảy, không có hành hình công khai, chỉ có sự im lặng bao trùm | **C** | `vid_06.mp4 (Bóng tối khép lại trên kho báu)` | Bóng tối nuốt chửng rương báu |
| **257 (84s–88s)** | Đúng 15 ngày kể từ khi Càn Long nhắm mắt, đế chế Hòa Thân tan thành mây khói | **D** | `timeline (15 NGÀY NGHẸT THỞ: 7/2 -> 12/2 -> 15/2 -> 22/2)` | 4 điểm mốc thời gian nối liền phát sáng |
| **258 (88s–92s)** | Đóng lại vòng 2: Vì sao Gia Khánh phải đợi đúng 3 năm? | **D** | `slam ("ĐÓNG VÒNG 2: 3 NĂM NHẪN NHỊN VÌ CÀN LONG")` | Chữ slam đóng vòng 2 câu hỏi |
| **259 (92s–96s)** | Không phải vì Gia Khánh yếu hèn, mà vì đạo hiếu và sự kiên nhẫn sắt đá | **A** | `File:Yuling Mausoleum.jpg (Lăng mộ Dụ Lăng)` | Toàn cảnh lăng tẩm Càn Long uy nghiêm giữa núi rừng |
| **260 (96s–100s)** | Linh cữu Càn Long được đưa về Dụ Lăng, an nghỉ nghìn thu | **A** | `File:Qianlong in old age.jpg (Càn Long)` | Zoom vào chân dung Càn Long đã khuất |
| **261 (100s–104s)** | Còn Hòa Thân ra đi ở tuổi 49, để lại một hồ sơ tịch thu tài sản đồ sộ | **A** | `File:Hesen (cropped).jpg (Chân dung Hòa Thân)` | Zoom chậm vào gương mặt trước khi chết |
| **262 (104s–108s)** | Bước tiếp theo của triều đình là niêm phong toàn bộ tư dinh và kiểm kê tài sản | **C** | `ai_07.png (Chùm chìa khóa và ổ khóa phong ấn)` | Chiếc khóa phong ấn đóng lại kịch tính |
| **263 (108s–112s)** | Bản kê năm 1799 chính thức được mở ra dưới sự giám sát của các hoàng thân | **A** | `output/long/hoa-than/img/qianlong_dragon_dish.jpg (Bảo vật đĩa rồng)` | Xoay nhẹ đĩa rồng chuẩn bị kiểm kê |
| **264 (112s–116s)** | Bản kê tiếp tục ghi nhận dòng sự kiện bi kịch này | **D** | `ledger (DÒNG 07: BỊ BẮT NGÀY 12/2 · ÉP TỰ VẪN NGÀY 22/2/1799 TẠI TƯ GIA)` | Cập nhật dòng 7 bản kê |
| **265 (116s–120s)** | Mười lăm ngày nghẹt thở khép lại cuộc đời một nhân vật lịch sử | **D** | `slam ("15 NGÀY NGHẸT THỞ THAY ĐỔI LỊCH SỬ")` | Chữ slam đập mạnh |
| **266 (120s–125s)** | Chuyển sang chương 9: Giải mã bản kê tài sản thực sự năm 1799 | **A** | `File:Prince Gong's Mansion - Main Gate.jpg (Cổng Đinh Phủ)` | Pan qua cổng phủ đệ bị niêm phong |
| **267 (125s–130s)** | Khép lại chương 8 đầy kịch tính | **D** | `chapter (CHƯƠNG 08: NĂM NGÀY)` | Thẻ chương chuyển tiếp hoàn hảo |

**Tổng kết số liệu chương:**
- Số nhịp: **32 nhịp** | Thời lượng: **130s** | Nhịp trung bình: **4.06s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 69s (53.1%)** | Nhóm B: 12s (9.2%) | Nhóm C: 16s (12.3%) | **Nhóm B+C: 28s (21.5%)** | **Nhóm D: 33s (25.4%)**.
- Số ảnh A sử dụng: **14 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 8 đạt 69s nhóm A (53.1%), sử dụng 17 ảnh tư liệu A (tấu sớ Càn Long 2 lần, Gia Khánh 3 lần, Thái Hòa Điện, 2 quan văn, Công chúa Hòa Hiếu, An Thiện Đường, Dụ Lăng, đĩa rồng, cổng phủ, chân dung Hòa Thân & Càn Long). D hỗ trợ dòng thời gian 15 ngày, date 7/2, 12/2, 15/2, 22/2 và slam đóng vòng 2.

### CH09: Bản kê (145 giây, 35 nhịp, trung bình 4.14s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **268 (0s–4s)** | Ngay sau cái chết của Hòa Thân, các đoàn kiểm kê của triều đình ùa vào dinh thự Zhizhai | **B** | `vid_03.mp4 (Hành lang kho chứa phủ đệ)` | Camera lướt nhanh dọc hành lang kho |
| **269 (4s–8s)** | Khánh Thân vương Vĩnh Lân và các đại thần được giao nhiệm vụ lập biên bản tịch biên tài sản | **A** | `File:Prince Gong's Mansion - Anshan Hall.jpg (An Thiện Đường)` | Zoom vào cửa kho lưu trữ cổ |
| **270 (8s–12s)** | Một bản kê chi tiết được ghi chép từng ngày, mở ra kho báu khổng lồ của vị đại thần | **A** | `output/long/hoa-than/img/qianlong_lacquer_teabowl.jpg (Chén trà điêu tất ngự chế CC0)` | Zoom cận cảnh hoa văn chạm khắc tinh vi |
| **271 (12s–16s)** | Đầu tiên là tiền mặt và động sản: Hàng trăm hòm bạc nén nguyên chất xếp tầng trong hầm ngầm | **C** | `ai_04.png (Rương kho báu trong hầm đá thâm nghiêm)` | Ánh sáng quét qua các rương bạc nén |
| **272 (16s–20s)** | Bạc thỏi được đúc hình móng ngựa (nguyên bảo), xếp ngay ngắn trong các rương gỗ tuyết tùng | **C** | `vid_06.mp4 (Rương vàng bạc phản chiếu ánh nến)` | Camera trôi chậm qua bề mặt bạc sáng loáng |
| **273 (20s–24s)** | Con số động sản thực tế được triều đình kiểm kê vào khoảng 60 đến 80 triệu lạng bạc | **A** | `output/long/hoa-than/img/qianlong_dragon_dish.jpg (Đĩa rồng men lam vàng)` | Zoom cận cảnh hoa văn hoàng gia kiểm kê |
| **274 (24s–28s)** | Để hiểu độ lớn: Thu ngân sách hàng năm của toàn bộ đế chế Đại Thanh khi đó là khoảng 40 triệu lạng | **D** | `bars (SO SÁNH: NGÂN SÁCH ĐẠI THANH 1 NĂM (40 TRIỆU) vs ĐỘNG SẢN HÒA THÂN (80 TRIỆU))` | Cột đồ họa so sánh gấp đôi ngân sách |
| **275 (28s–32s)** | Nghĩa là riêng lượng bạc mặt của Hòa Thân đã tương đương gần hai năm tổng thu cả nước | **A** | `output/long/hoa-than/img/court_jifu_robe.jpg (Cát phục quan văn)` | Pan chi tiết hoa văn chỉ vàng quý phái |
| **276 (32s–36s)** | Vậy con số 1,1 tỷ lạng bạc mà các bài viết tiếng Việt lưu truyền xuất phát từ đâu? | **D** | `question ("CON SỐ 1,1 TỶ LẠNG XUẤT PHÁT TỪ ĐÂU?")` | Chữ câu hỏi nổi bật trên nền xám |
| **277 (36s–40s)** | Các nhà nghiên cứu lịch sử phát hiện đó là sản phẩm của giai thoại dân gian thời Đạo Quang | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Pan từ tà áo quan lên phong thái quý tộc |
| **278 (40s–44s)** | Người ta đã cộng gộp cả giá trị ước tính của đất đai, nhà cửa, đồ cổ bị thổi giá lên hàng trăm lần | **D** | `waterfall (PHÂN BỔ TÀI SẢN: BẠC MẶT · TIỆM CẦM ĐỒ · ĐẤT ĐAI · BẢO VẬT)` | Biểu đồ thác nước phân tích các mảng |
| **279 (44s–48s)** | Kho bảo vật ngự dụng chứa hàng ngàn món đồ gốm sứ tinh xảo vượt quy chế | **A** | `output/long/hoa-than/img/qianlong_dragon_dish.jpg (Đĩa rồng men lam vàng CC0)` | Zoom cận cảnh hoa văn rồng vờn ngọc |
| **280 (48s–52s)** | Chiếc chén trà điêu tất Càn Long ngự chế chạm khắc hoa văn tinh vi tuyệt hảo | **A** | `output/long/hoa-than/img/qianlong_lacquer_teabowl.jpg (Chén trà điêu tất)` | Xoay nhẹ chi tiết men sơn mài đỏ thắm |
| **281 (52s–56s)** | Những bộ sách ngọc hoàng gia khắc chữ vàng vốn chỉ dành riêng cho hoàng đế | **A** | `File:Qing Dynasty Imperial Jade Book.jpg (Sách ngọc triều đình)` | Pan dọc phiến ngọc bích dát vàng |
| **282 (56s–60s)** | Bình thủy tinh Peking glass với màu sắc rực rỡ và độ trong suốt hoàn hảo | **A** | `File:Peking Glass Vase Qianlong.jpg (Bình thủy tinh Bắc Kinh)` | Ánh sáng chiếu xuyên qua bình ngọc lưu ly |
| **283 (60s–64s)** | Các kho bảo vật ngự dụng tịch thu chất đầy các gian phòng phụ của dinh thự | **C** | `ai_19.png (Kho báu vật ngự dụng tịch thu)` | Toàn cảnh các tráp ngọc và đồ sứ trên kệ |
| **284 (64s–68s)** | Ngoài bạc và bảo vật, ông còn sở hữu một đế chế kinh doanh khổng lồ | **A** | `File:Prince Gong's Mansion - Jiale Hall.jpg (Gia Lạc Đường)` | Góc hất lên trần nhà chạm khắc hoa văn |
| **285 (68s–72s)** | Hơn 75 tiệm cầm đồ và ngân hiệu rải khắp Bắc Kinh và các tỉnh phụ cận | **D** | `counter (75 TIỆM CẦM ĐỒ · NGÂN HIỆU TOÀN QUỐC)` | Bộ đếm dừng ở 75 tiệm |
| **286 (72s–76s)** | Hơn 80.000 mẫu ruộng đất màu mỡ trải dài từ Trực Lệ đến Sơn Đông, Giang Nam | **D** | `counter (80.000 MẪU RUỘNG ĐẤT TƯ NHÂN)` | Bộ đếm đất đai tăng vọt |
| **287 (76s–80s)** | Đội thuyền buôn hơn 80 chiếc hoạt động dọc sông Đại Vận Hà và bờ biển duyên hải | **A** | `File:Alexander - Imperial Barges.jpg (Thuyền vận tải)` | Pan dọc đoàn thuyền buôn trên sông |
| **288 (80s–84s)** | Ông chính là nhà tư bản tài chính phong kiến lớn nhất trong lịch sử triều Thanh | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom vào phong thái nhà quản trị tài chính |
| **289 (84s–88s)** | Nghiên cứu của giáo sư Wook Yoon năm 2012 khẳng định: Tài sản thực tế khoảng 60–80 triệu lạng | **A** | `File:和珅楷书《平定台湾咏》.jpg (Thư pháp Khải thư Hòa Thân)` | Pan nét chữ Khải thư chân phương tuyệt mỹ |
| **290 (88s–92s)** | Con số này đã là một kỷ lục vô tiền khoáng hậu, không cần phải phóng đại lên 1,1 tỷ lạng | **D** | `slam ("KỶ LỤC LỊCH SỬ · KHÔNG CẦN PHÓNG ĐẠI")` | Chữ slam khẳng định sự thật |
| **291 (92s–96s)** | Biên bản kiểm kê chính thức tháng 5 năm 1799 của triều đình Gia Khánh khép lại con số | **A** | `File:和珅书弘历颂夏景山水十二咏诗册.png (Thư pháp Hòa Thân chép thơ Càn Long)` | Pan nét chữ thanh thoát uyển chuyển |
| **292 (96s–100s)** | Gia Khánh sung toàn bộ số bạc vào quốc khố để chi trả chiến phí dẹp loạn Bạch Liên Giáo | **C** | `ai_07.png (Chùm chìa khóa niêm phong kho bạc)` | Khóa niêm phong kho quốc khố |
| **293 (100s–104s)** | Dân gian để lại câu ca dao châm biếm sâu cay: 'Hòa Thân ngã ngựa, Gia Khánh no nê' | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh)` | Focus ánh mắt đắc thắng của Gia Khánh |
| **294 (104s–108s)** | Đóng lại vòng 1: Bản kê năm 1799 thực sự lớn cỡ nào? | **D** | `slam ("ĐÓNG VÒNG 1: 60–80 TRIỆU LẠNG LÀ SỰ THẬT TÀI CHÍNH")` | Chữ slam đóng vòng 1 dứt khoát |
| **295 (108s–112s)** | Từ chối chọn một con số cảm tính truyền miệng để bảo vệ tính chân thực của lịch sử | **A** | `File:Hesen (cropped).jpg (Chân dung Hòa Thân)` | Zoom vào nét mặt trầm mặc |
| **296 (112s–116s)** | Bút tích thư pháp của chính Hòa Thân vẫn còn lưu giữ trong kho sách | **A** | `File:和珅楷书《平定台湾咏》.jpg (Thư pháp Khải thư)` | Pan chi tiết nét mực đen óng |
| **297 (116s–120s)** | Một người có tài thư họa xuất chúng nhưng bị nhấn chìm bởi lòng tham quyền lực | **A** | `File:Nine Dragon Screen Forbidden City.jpg (Cửu Long bích)` | Pan chi tiết phù điêu rồng ngọc |
| **298 (120s–125s)** | Toàn bộ tài sản bị sung công, chỉ để lại bản án 20 điều đại tội | **A** | `File:Prince Gong's Mansion - Grand Theater.jpg (Đại hý đài)` | Góc rộng nhà hát tư gia trong phủ |
| **299 (125s–130s)** | Bản kê mô-típ hoàn tất dòng thứ tám đầy chấn động | **D** | `ledger (DÒNG 08: ĐỘNG SẢN 60–80 TRIỆU LẠNG · 75 TIỆM CẦM ĐỒ · 80.000 MẪU RUỘNG ĐẤT)` | Cập nhật dòng 8 bản kê chi tiết |
| **300 (130s–135s)** | Chân dung bản kê năm 1799 đã được làm sáng tỏ | **D** | `slam ("BẢN KÊ 1799: SỰ THẬT ĐÃ ĐƯỢC GIẢI MÃ")` | Chữ slam hiện mạnh mẽ |
| **301 (135s–140s)** | Bước vào chương 10: Hai mươi tội danh chính thức của triều đình | **B** | `ai_02.png (Thư phòng kiểm kê)` | Góc tĩnh lặng của thư phòng sau cuộc tịch biên |
| **302 (140s–145s)** | Khép lại chương 9, bước sang bản luận tội | **D** | `chapter (CHƯƠNG 09: BẢN KÊ)` | Thẻ chương chuyển tiếp hoàn hảo |

**Tổng kết số liệu chương:**
- Số nhịp: **35 nhịp** | Thời lượng: **145s** | Nhịp trung bình: **4.14s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 77s (53.1%)** | Nhóm B: 9s (6.2%) | Nhóm C: 16s (11.0%) | **Nhóm B+C: 25s (17.2%)** | **Nhóm D: 43s (29.7%)**.
- Số ảnh A sử dụng: **16 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 9 đạt 77s nhóm A (53.1%), sử dụng 19 ảnh tư liệu A (chén điêu tất 2 lần, đĩa rồng 2 lần, áo cát phục, sách ngọc, bình Peking glass, Gia Lạc Đường, thuyền buôn Alexander, 2 bản thư pháp thật của Hòa Thân, Gia Khánh, Cửu Long bích, đại hý đài, chân dung Hòa Thân). D hỗ trợ counter 60-80 triệu, bars so sánh ngân sách, waterfall phân rã tài sản, slam đóng vòng 1.

### CH10: Hai mươi tội (130 giây, 32 nhịp, trung bình 4.06s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **303 (0s–4s)** | Bản án chính thức do hoàng đế Gia Khánh đích thân ban bố gồm đúng 20 tội danh | **D** | `slam ("HAI MƯƠI TỘI DANH CỦA GIA KHÁNH")` | Chữ slam hiện dứt khoát |
| **304 (4s–8s)** | Điều bất ngờ là tội tham nhũng và vơ vét tiền bạc không hề đứng ở vị trí đầu tiên | **A** | `File:和珅楷书《平定台湾咏》.jpg (Thư pháp Khải thư Hòa Thân)` | Pan nét chữ đối chiếu với bản án thanh trừng |
| **305 (8s–12s)** | Nhóm tội danh hàng đầu tập trung vào tội lạm quyền quân cơ và bất kính với hoàng thất | **A** | `File:Hall of Supreme Harmony.jpg (Thái Hòa Điện)` | Góc máy hất lên thềm rồng uy nghiêm |
| **306 (12s–16s)** | Tội thứ nhất: Khi Càn Long lập thái tử năm 1795, Hòa Thân tự ý tiết lộ bí mật trước | **A** | `File:清仁宗嘉庆皇帝朝服像.jpg (Gia Khánh)` | Focus ánh nhìn nghiêm khắc của Gia Khánh |
| **307 (16s–20s)** | Tội thứ hai: Cưỡi ngựa đi thẳng qua Viên Minh Viên và Tử Cấm Thành, coi thường hoàng thượng | **A** | `File:Forbidden City Map 18th century.jpg (Bản đồ hoàng thành)` | Vẽ đường ngựa đi qua các cổng cấm |
| **308 (20s–24s)** | Tội thứ ba: Dùng võng khiêng thẳng vào cửa cung như bậc phụ hoàng | **A** | `File:Meridian Gate of the Forbidden City.jpg (Ngọ Môn)` | Ken Burns góc rộng ngước nhìn cổng thành |
| **309 (24s–28s)** | Tội thứ tư: Cưới cung nữ trong nội đình làm tì thiếp riêng | **A** | `File:Qianlong with Imperial Consorts.jpg (Hậu phi cung đình)` | Pan chi tiết trang phục cung nữ |
| **310 (28s–32s)** | Tội thứ năm: Bưng bít chiến báo quân sự vụ khởi nghĩa Bạch Liên Giáo | **A** | `output/long/hoa-than/img/qianlong_poem_siege.jpg (Bản ngự chế chiến công CC BY 4.0)` | Zoom vào dòng chữ ngự bút chỉ huy chiến dịch |
| **311 (32s–36s)** | Nhóm tội danh tiếp theo tố cáo việc lạm quyền Quân cơ xứ và Phủ Nội Vụ | **B** | `ai_15.png (Thư phòng Quân cơ xứ đêm khuya)` | Ánh nến soi rọi chồng tấu sớ mật |
| **312 (36s–40s)** | Tự ý sửa đổi tấu sớ của các đại thần, che giấu các báo cáo bất lợi | **B** | `vid_05.mp4 (Cuộn tấu sớ đóng kín dưới ánh nến)` | Camera lướt qua cuộn tấu sớ thắt dây lụa |
| **313 (40s–44s)** | Tố cáo dinh thự Zhizhai mô phỏng kiến trúc Ninh Thọ Cung, xây nhà bằng gỗ Nam mộc quý hiếm | **A** | `File:Prince Gong's Mansion - Anshan Hall.jpg (An Thiện Đường)` | Zoom vào cột gỗ lim nguyên khối |
| **314 (44s–48s)** | Các tội danh về tiền bạc, kho báu và ruộng đất chỉ bắt đầu xuất hiện từ điều thứ 15 trở đi | **A** | `output/long/hoa-than/img/court_jifu_robe.jpg (Cát phục quan văn triều Thanh)` | Pan chi tiết hoa văn chỉ vàng |
| **315 (48s–52s)** | Nghiên cứu của học giả Daniel McMahon năm 2008 chỉ ra bản chất cuộc thanh trừng | **D** | `quote ("CUỘC THANH TRỪNG NHẰM THÂU TÓM QUYỀN LỰC VÀ TÁI THIẾT TÀI CHÍNH TRIỀU ĐÌNH · DANIEL MCMAHON 2008")` | Trích nghiên cứu của McMahon |
| **316 (52s–56s)** | Trước năm 1799, hồ sơ chính thức của triều đình luôn ngợi khen năng lực hành chính của ông | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Pan phong thái đại thần tận tụy trước 1799 |
| **317 (56s–60s)** | Bản án 20 tội danh phản ánh nhu cầu chính trị cấp bách của Gia Khánh để xác lập uy quyền tuyệt đối | **A** | `output/long/hoa-than/img/qianlong_temple_name.jpg (Tấu sớ dâng miếu hiệu)` | Pan dòng chữ chiếu chỉ thanh trừng |
| **318 (60s–64s)** | Dấu ấn tài hoa của Hòa Thân vẫn còn hiện hữu qua các tác phẩm văn chương và thư pháp | **A** | `File:和珅楷书《平定台湾咏》.jpg (Thư pháp Khải thư Bình Định Đài Loan Vịnh)` | Pan chi tiết nét bút Khải thư mực đen nhánh |
| **319 (64s–68s)** | Tập thơ 'Trí Trai văn tập' do chính ông sáng tác bộc lộ tư chất thi sĩ uyên bác | **A** | `File:和珅书弘历颂夏景山水十二咏诗册.png (Thơ Trí Trai)` | Zoom vào con dấu riêng Trí Trai |
| **320 (68s–72s)** | Trước khi thắt cổ trong đêm 22 tháng 2, ông đã để lại bài thơ tuyệt mệnh đầy trăn trở | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom vào ánh mắt bi kịch của nhân vật |
| **321 (72s–76s)** | 'Năm mươi năm qua tựa giấc mộng, nay bỏ trần gian theo bóng mây' | **D** | `quote ("NĂM MƯƠI NĂM QUA NHƯ GIẤC MỘNG · THẢ CẦN NƯỚC LẠNH MẶC THUYỀN TROI · BÀI THƠ TUYỆT MỆNH")` | Bản dịch bài thơ tuyệt mệnh hiện trang trọng |
| **322 (76s–80s)** | Con dấu triện quyền uy bị thu hồi, khép lại sự nghiệp của vị đại thần | **C** | `ai_20.png (Con dấu triện và bản án khép lại)` | Chiếc triện đồng đặt trên trang giấy trắng |
| **323 (80s–84s)** | Đồng hồ thời gian đã cạn kiệt những hạt cát cuối cùng | **C** | `ai_18.png (Đồng hồ cát cạn kiệt)` | Hạt cát cuối cùng rơi xuống đáy |
| **324 (84s–88s)** | Bản án 20 điều khép lại một chương đời đầy thăng trầm và tranh cãi | **C** | `ai_16.png (Bóng quyền lực sụp đổ)` | Bóng ngai vàng tan biến trong bóng tối |
| **325 (88s–92s)** | Gia Khánh xóa bỏ toàn bộ tước hiệu, nhưng không tru diệt cả gia tộc như án thông thường | **A** | `output/long/hoa-than/img/wenguan_portrait_1.jpg (Quan văn triều đình)` | Pan dọc nét mặt trầm mặc của các đại thần |
| **326 (92s–96s)** | Con trai ông, Phong Thân Ân Đức, vẫn được giữ lại tước vị nhỏ nhờ công chúa Hòa Hiếu | **A** | `File:Princess Hexiao.jpg (Công chúa Hòa Hiếu)` | Zoom vào chân dung công chúa |
| **327 (96s–100s)** | Hai mươi tội danh trở thành bản cáo trạng nổi tiếng nhất trong lịch sử tư pháp Đại Thanh | **D** | `slam ("BẢN CÁO TRẠNG NỔI TIẾNG NHẤT LỊCH SỬ")` | Chữ slam hiện dứt khoát |
| **328 (100s–104s)** | Nhưng trong văn hóa đại chúng, hình tượng của ông lại bị biến đổi hoàn toàn | **D** | `question ("VÌ SAO HÌNH TƯỢNG BỊ BIẾN ĐỔI TRÊN MÀN ẢNH?")` | Chữ câu hỏi mở sang chương 11 |
| **329 (104s–108s)** | Từ một đại thần tài năng, tuấn tú thành một gã hề xu nịnh trên phim ảnh | **A** | `File:Hesen (cropped).jpg (Chân dung Hòa Thân)` | Cận cảnh nét mặt thanh tú, sắc sảo |
| **330 (108s–112s)** | Bản kê tiếp tục ghi nhận sự kết thúc của 20 điều đại tội | **D** | `ledger (DÒNG 09: BẢN ÁN 20 TỘI DANH CỦA GIA KHÁNH · TỊCH THU TOÀN BỘ TƯ DINH)` | Cập nhật dòng 9 bản kê |
| **331 (112s–116s)** | Chân dung lịch sử và bản án đã được đặt cạnh nhau | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Pan chuyển động nhẹ qua chân dung |
| **332 (116s–121s)** | Bước vào chương 11: Giải ảo hình tượng gã hề trên màn ảnh truyền hình | **B** | `ai_06.png (Cổng cung thành thâm nghiêm)` | Góc rộng cung đình trong hoàng hôn |
| **333 (121s–125s)** | Một chương đặc biệt giải mã khoảng lệch giữa phim ảnh và đời thực | **D** | `slam ("GIẢI MÃ KHOẢNG LỆCH PHIM VÀ ĐỜI")` | Chữ slam hiện ấn tượng |
| **334 (125s–130s)** | Khép lại chương 10, mở ra chương giải ảo | **D** | `chapter (CHƯƠNG 10: HAI MƯƠI TỘI)` | Thẻ chương kết thúc chương 10 |

**Tổng kết số liệu chương:**
- Số nhịp: **32 nhịp** | Thời lượng: **130s** | Nhịp trung bình: **4.06s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 72s (55.4%)** | Nhóm B: 13s (10.0%) | Nhóm C: 12s (9.2%) | **Nhóm B+C: 25s (19.2%)** | **Nhóm D: 33s (25.4%)**.
- Số ảnh A sử dụng: **16 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 10 đạt 71s nhóm A (54.6%), sử dụng 18 ảnh tư liệu A (Thái Hòa Điện, Gia Khánh, bản đồ Cố Cung, Ngọ Môn, Càn Long hậu phi, ngự chế giải vây Hắc Thủy, An Thiện Đường, áo cát phục, tấu sớ, 2 bản thư pháp thật của Hòa Thân, Công chúa Hòa Hiếu, quan văn, chân dung Hòa Thân). D hỗ trợ phân tích 20 tội danh, quote McMahon 2008 & bài thơ tuyệt mệnh.

### CH11: Gã hề trên màn hình (115 giây, 29 nhịp, trung bình 3.97s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **335 (0s–4s)** | Bước vào chương 11: Giải ảo hình tượng người xem Việt Nam đã quen thuộc trên màn ảnh | **D** | `slam ("GIẢI ẢO HÌNH TƯỢNG TRÊN MÀN ẢNH")` | Chữ slam hiện dứt khoát |
| **336 (4s–8s)** | Hàng triệu khán giả nhớ đến Hòa Thân qua vai diễn kinh điển của nghệ sĩ Vương Cương | **A** | `File:Hesen (cropped).jpg (Chân dung Hòa Thân đời Thanh)` | Đối chiếu dung mạo thật với vai diễn truyền hình |
| **337 (8s–12s)** | Một nhân vật béo tròn, hoạt kê, luôn luồn cúi và bị Lưu Dung trêu chọc | **A** | `File:Heshen.jpg (Chân dung Hòa Thân toàn thân)` | Zoom cận cảnh khuôn mặt thanh tú, sống mũi cao |
| **338 (12s–16s)** | Quy định bản quyền và tôn trọng lịch sử: Video tuyệt đối không dùng ảnh diễn viên hay still phim | **D** | `quote ("QUY ĐỊNH KÊNH: KHÔNG DÙNG STILL PHIM, ẢNH DIỄN VIÊN, POSTER · CHỈ ĐỐI CHIẾU SỬ LIỆU")` | Khẳng định nguyên tắc kênh |
| **339 (16s–20s)** | Chân dung đời Thanh thực sự cho thấy một diện mạo hoàn toàn trái ngược | **A** | `File:Heshen 2.jpg (Chân dung Hòa Thân)` | Pan dọc tà áo quan và vóc dáng nho nhã |
| **340 (20s–24s)** | Hòa Thân ngoài đời thật là một trang tuấn kiệt, dáng người cao ráo, diện mạo khôi ngô | **A** | `output/long/hoa-than/img/court_jifu_robe.jpg (Cát phục quan văn triều Thanh CC0)` | Pan chi tiết hoa văn trên áo cát phục |
| **341 (24s–28s)** | Các bức họa cổ thời Càn Long miêu tả ông với phong thái thư sinh đĩnh đạc | **A** | `File:Hesen (cropped).jpg (Hòa Thân tư thái nho nhã)` | Zoom vào phong thái thư sinh |
| **342 (28s–32s)** | Trần Nhuệ đóng ông trong 'Vương triều Càn Long' năm 2003 với góc nhìn chính luận | **D** | `file (Hồ sơ diễn viên: TRẦN NHUỆ · 'VƯƠNG TRIỀU CÀN LONG' 2003)` | Thẻ diễn viên Trần Nhuệ |
| **343 (32s–36s)** | Trần Triển Bằng khắc họa 28 ngày cuối cùng của ông trong phim 'Thiên mệnh' năm 2018 | **D** | `file (Hồ sơ diễn viên: TRẦN TRIỂN BẰNG · 'THIÊN MỆNH' TVB 2018)` | Thẻ diễn viên Trần Triển Bằng |
| **344 (36s–40s)** | Lưu Giang từng thủ vai ông trong các tác phẩm truyền hình Hồng Kông thập niên 1980 | **D** | `counter (4 DIỄN VIÊN TIÊU BIỂU TRÊN MÀN ẢNH NHỎ)` | Bộ đếm 4 diễn viên |
| **345 (40s–44s)** | Sân khấu kịch truyền thống vắng lặng, bức màn hư cấu dần khép lại | **B** | `vid_07.mp4 (Sân khấu kịch truyền thống vắng lặng)` | Camera trôi chậm qua sân khấu đại hý đài cổ |
| **346 (44s–48s)** | Vì sao kịch bản truyền hình lại cần biến một chính khách quyền uy thành một gã hề? | **D** | `question ("VÌ SAO PHIM CẦN MỘT GÃ HỀ?")` | Chữ câu hỏi hiện to trên nền tối |
| **347 (48s–52s)** | Câu trả lời: Phim ảnh đại chúng cần một cặp nhân vật tương phản để tạo tiếng cười | **A** | `File:Liu Yong.png (Chân dung Lưu Dung)` | Zoom cận cảnh chân dung Lưu Dung |
| **348 (52s–56s)** | Khán giả muốn thấy kẻ tham lam bị trừng phạt và chế giễu một cách sảng khoái | **C** | `ai_05.png (Cán cân giữa nghệ thuật và lịch sử)` | Cán cân dao động giữa hai thái cực |
| **349 (56s–60s)** | Lưu Dung trong phim được phóng đại thành vị tể tướng lưng gù đầy mưu mẹo | **A** | `output/long/hoa-than/img/wenguan_portrait_1.jpg (Quan văn triều Thanh)` | Pan dọc bức chân dung quan văn thanh liêm |
| **350 (60s–64s)** | Nhưng trong thực tế, triều Thanh không hề có chức danh 'Tể tướng' | **A** | `output/long/hoa-than/img/wenguan_portrait_2.jpg (Quan văn triều Thanh)` | Pan dọc áo quan đại thần làm rõ quan chế |
| **351 (64s–68s)** | Kỷ Hiểu Lam cũng là một học giả biên soạn Tứ Khổ Toàn Thư, không phải quan thanh tra đi bắt gian thần | **A** | `File:Ji Yun.jpg (Chân dung Kỷ Hiểu Lam)` | Chân dung Kỷ Hiểu Lam đang cầm sách |
| **352 (68s–72s)** | Họ đều là những đại thần phục vụ dưới quyền của vị hoàng đế độc tài Càn Long | **B** | `ai_09.png (Giảng đường Nho gia kinh điển)` | Pan qua các dãy bàn học và sách cổ |
| **353 (72s–76s)** | Đóng lại vòng 3: Hòa Thân trên phim và đời thực là hai chân dung hoàn toàn khác biệt | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom vào ánh mắt uy nghiêm bác bỏ phim ảnh |
| **354 (76s–80s)** | Đời thực không có những cuộc đấu khẩu hài hước, chỉ có cuộc chơi quyền lực tàn khốc | **C** | `ai_16.png (Bóng chiếc ghế quyền lực sân khấu)` | Bóng chiếc ghế quyền uy in trên màn che |
| **355 (80s–84s)** | Một người đàn ông xuất chúng, tinh thông 4 thứ tiếng, quản trị tài chính xuất sắc | **A** | `File:Heshen 2.jpg (Hòa Thân tư thái nho nhã)` | Pan dọc chân dung uy nghiêm |
| **356 (84s–88s)** | Nhưng chính sự tha hóa trước quyền lực tuyệt đối đã đưa ông vào con đường diệt vong | **A** | `File:Prince Gong's Mansion - Grand Theater.jpg (Đại hý đài)` | Toàn cảnh sân khấu đại hý đài ngoài đời |
| **357 (88s–92s)** | Tiếng cười trên màn ảnh đã che mờ bi kịch sâu sắc của một thể chế phong kiến già cỗi | **B** | `vid_03.mp4 (Hành lang cổ phủ đệ)` | Dolly lướt chậm qua hàng cột son |
| **358 (92s–96s)** | Ngôi nhà nơi ông từng sống và trút hơi thở cuối cùng vẫn còn đứng đó | **A** | `File:Prince Gong's Mansion - Anshan Hall.jpg (An Thiện Đường)` | Góc tĩnh lặng nơi ở của vương phủ |
| **359 (96s–100s)** | Sau cái chết của ông, dinh thự tráng lệ này đã đổi chủ như thế nào? | **D** | `question ("NGÔI NHÀ ĐÃ ĐỔI CHỦ NHƯ THẾ NÀO?")` | Chữ câu hỏi mở sang chương 12 |
| **360 (100s–104s)** | Bản kê tiếp tục ghi nhận dòng thứ mười: Giải ảo hình tượng | **D** | `ledger (DÒNG 10: GIẢI ẢO HÌNH TƯỢNG TRUYỀN HÌNH · PHÂN BIỆT PHIM VÀ SỰ THẬT)` | Cập nhật dòng 10 bản kê |
| **361 (104s–108s)** | Chân dung đích thực đã được trả lại cho lịch sử | **A** | `File:Hesen (cropped).jpg (Chân dung Hòa Thân)` | Zoom-in vào ánh mắt trầm ngâm |
| **362 (108s–111s)** | Chuyển sang câu chuyện về số phận của ngôi nhà sau năm 1799 | **A** | `File:Prince Gong Mansion Garden.jpg (Hoa viên Cung Vương Phủ)` | Pan bờ hồ và cầu đá hoa viên |
| **363 (111s–115s)** | Khép lại chương 11, bước vào chương 12: Nhà đổi chủ | **D** | `chapter (CHƯƠNG 11: GÃ HỀ TRÊN MÀN HÌNH)` | Thẻ chương chuyển tiếp hoàn hảo |

**Tổng kết số liệu chương:**
- Số nhịp: **29 nhịp** | Thời lượng: **115s** | Nhịp trung bình: **3.97s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 59s (51.3%)** | Nhóm B: 12s (10.4%) | Nhóm C: 8s (7.0%) | **Nhóm B+C: 20s (17.4%)** | **Nhóm D: 36s (31.3%)**.
- Số ảnh A sử dụng: **11 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 11 đạt 60s nhóm A (52.2%), sử dụng 16 ảnh tư liệu A (Hòa Thân 5 lần, áo cát phục, Lưu Dung, 2 quan văn, Kỷ Hiểu Lam, đại hý đài, An Thiện Đường, hoa viên Cung Vương Phủ). Tuân thủ nghiêm cấm ảnh phim/diễn viên, đối chiếu lịch sử bằng hồ sơ 4 diễn viên đồ họa D, slam bãi bỏ tể tướng và slam đóng vòng 3.

### CH12: Nhà đổi chủ (125 giây, 31 nhịp, trung bình 4.03s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **364 (0s–4s)** | Năm 1799, ngay sau khi Hòa Thân qua đời, Gia Khánh ban dinh thự Zhizhai cho Khánh Thân vương Vĩnh Lân | **A** | `File:Dingfu Gate Prince Gong.jpg (Cổng Đinh Phủ)` | Zoom vào cổng vòm đá xanh phủ đệ năm 1799 |
| **365 (4s–8s)** | Vĩnh Lân là em trai ruột của Gia Khánh, con trai thứ 17 và là con út của Càn Long | **D** | `org (Sơ đồ hoàng tộc: CÀN LONG -> HOÀNG TỬ THỨ 17 VĨNH LÂN)` | Nhánh sơ đồ hoàng thất mở ra |
| **366 (8s–12s)** | Tương truyền khi các hoàng tử tranh giành ngai vàng, Vĩnh Lân chỉ xin: 'Sau này cho đệ dinh thự của Hòa Thân là đủ' | **A** | `File:Prince Gong's Mansion - Anshan Hall.jpg (An Thiện Đường)` | Pan qua dãy nhà An Thiện Đường |
| **367 (12s–16s)** | Tuy nhiên, ông chỉ được sở hữu một nửa phủ đệ, nửa còn lại vẫn để công chúa Hòa Hiếu ở | **A** | `File:Princess Hexiao.jpg (Công chúa Hòa Hiếu)` | Zoom vào chân dung công chúa Hòa Hiếu |
| **368 (16s–20s)** | Năm 1820, Vĩnh Lân qua đời, con cháu ông tiếp tục sinh sống tại đây qua nhiều thập kỷ | **A** | `File:Dingfu Gate Prince Gong.jpg (Cổng Đinh Phủ)` | Pan qua cánh cổng đá rêu phong |
| **369 (20s–24s)** | Đến năm 1850, một bước ngoặt lớn làm thay đổi vĩnh viễn tên gọi của dinh thự | **D** | `date ("1850 · HOÀNG ĐẾ HÀM PHONG BAN PHỦ")` | Mốc năm 1850 nổi bật |
| **370 (24s–28s)** | Hoàng đế Hàm Phong quyết định thu hồi và ban tặng phủ đệ cho người em trai thứ sáu | **A** | `File:Prince Gong Yixin.jpg (Chân dung Cung Thân vương Dịch Hân)` | Ken Burns zoom cận cảnh Cung Thân vương Dịch Hân |
| **371 (28s–32s)** | Người đó chính là Cung Thân vương Dịch Hân, một trong những hoàng thân quyền lực nhất cuối triều Thanh | **A** | `File:Prince Gong.jpg (Dịch Hân thời trẻ)` | Pan bức ảnh chụp Dịch Hân thời vương gia |
| **372 (32s–36s)** | Sau hai năm đại trùng tu, năm 1852, Cung Thân vương chính thức dọn vào sinh sống | **D** | `date ("1852 · CHÍNH THỨC DỌN VÀO CUNG VƯƠNG PHỦ")` | Mốc năm 1852 hiện rõ |
| **373 (36s–40s)** | Từ thời điểm này, dinh thự Zhizhai chính thức mang tên gọi lịch sử: Cung Vương Phủ | **D** | `slam ("CHÍNH THỨC MANG TÊN: CUNG VƯƠNG PHỦ")` | Chữ slam đập mạnh rực rỡ |
| **374 (40s–44s)** | Bài viết tiếng Việt thường nhảy thẳng từ Hòa Thân sang Cung Vương Phủ, bỏ quên 50 năm của Khánh Thân vương | **A** | `File:Prince Gong Yixin.jpg (Dịch Hân)` | Đối chiếu sửa sai sử liệu qua chân dung |
| **375 (44s–48s)** | Dịch Hân cho xây dựng lại khu hoa viên phía sau với quy mô tráng lệ bậc nhất kinh thành | **A** | `File:Prince Gong Mansion Garden.jpg (Hoa viên Cung Vương Phủ)` | Pan toàn cảnh hoa viên và hồ nước |
| **376 (48s–52s)** | Điện Gia Lạc Đường được tân trang làm nơi tiếp đón các đại thần và sứ tiết quốc tế | **A** | `File:Prince Gong's Mansion - Jiale Hall.jpg (Gia Lạc Đường)` | Zoom vào các hàng cột son và cửa ngọc |
| **377 (52s–56s)** | Khu đại hý đài bằng gỗ nguyên khối được hoàn thiện, trở thành nhà hát tư gia lớn nhất Bắc Kinh | **A** | `File:Prince Gong's Mansion - Grand Theater.jpg (Đại hý đài)` | Góc máy hất lên trần gỗ chạm tranh hoa |
| **378 (56s–60s)** | Cung Thân vương Dịch Hân là người khởi xướng phong trào Dương Vụ, mở đầu hiện đại hóa Trung Hoa | **A** | `File:Prince Gong.jpg (Dịch Hân)` | Zoom vào ánh mắt cải cách của Dịch Hân |
| **379 (60s–64s)** | Nơi đây trở thành trung tâm chính trị thứ hai của triều đình nửa cuối thế kỷ 19 | **C** | `ai_16.png (Bóng ngai vàng thế kỷ 19)` | Bóng quyền uy của Dịch Hân |
| **380 (64s–68s)** | Hồ Thập Sát Hải trong chiều sương chứng kiến sự thịnh suy của các thế hệ chủ nhân | **B** | `vid_08.mp4 (Hồ Thập Sát Hải trong chiều sương)` | Camera tracking chậm dọc bờ hồ rợp bóng liễu |
| **381 (68s–72s)** | Những ổ khóa đồng được thay đổi qua từng triều đại, nhưng cốt cách vương phủ vẫn vẹn nguyên | **C** | `ai_07.png (Ổ khóa đổi chủ qua các triều đại)` | Ánh sáng quét qua ổ khóa rỉ sét |
| **382 (72s–76s)** | Hành lang sơn son phủ đệ cổ kính vẫn lưu giữ dấu ấn bàn tay của người thợ năm 1777 | **B** | `vid_03.mp4 (Hành lang sơn son phủ đệ cổ)` | Dolly lướt chậm qua dãy cột son |
| **383 (76s–80s)** | Kiến trúc gỗ tráng lệ chống chọi với mưa nắng của thời gian | **B** | `ai_11.png (Kiến trúc gỗ tráng lệ)` | Góc ngước nhìn kết cấu mái ngói dougong |
| **384 (80s–84s)** | Năm 1898, Cung Thân vương Dịch Hân qua đời, triều Thanh bước vào những năm tháng suy tàn cuối cùng | **D** | `date ("1898 · DỊCH HÂN QUA ĐỜI · ĐẾ CHẾ SUY TÀN")` | Mốc năm 1898 màu xám |
| **385 (84s–88s)** | Cháu nội của ông là Bối lặc Phổ Vĩ kế thừa vương phủ giữa cơn bão táp cách mạng | **A** | `File:Dingfu Gate Prince Gong.jpg (Cổng phủ)` | Pan qua cánh cổng đá cổ kính |
| **386 (88s–92s)** | Năm 1912, triều Thanh sụp đổ, thời đại của các vương tôn quý tộc chính thức chấm dứt | **A** | `File:Prince Gong's Mansion - Grand Theater.jpg (Đại hý đài vắng lặng)` | Góc chụp nhà hát lớn phủ đệ sau cách mạng |
| **387 (92s–96s)** | Ngôi nhà của Hòa Thân sẽ bước vào thế kỷ 20 với những biến thiên lịch sử không ai ngờ tới | **A** | `File:Prince Gong's Mansion - Main Gate.jpg (Cổng chính)` | Góc chụp từ xa cổng chính vương phủ |
| **388 (96s–100s)** | Từ phủ đệ quý tộc thành trường đại học, nhà máy và di tích lịch sử | **D** | `timeline (Biến thiên: Vương phủ -> Đại học -> Nhà máy -> Bảo tàng)` | Trục thời gian mở ra thế kỷ 20 |
| **389 (100s–104s)** | Bản kê tiếp tục ghi nhận dòng thứ mười một | **D** | `ledger (DÒNG 11: 1799 GIAO KHÁNH THÂN VƯƠNG · 1850 TRỞ THÀNH CUNG VƯƠNG PHỦ)` | Cập nhật dòng 11 bản kê |
| **390 (104s–108s)** | Từ phủ Hòa Thân đến Cung Vương Phủ lừng danh | **D** | `slam ("TỪ PHỦ HÒA THÂN ĐẾN CUNG VƯƠNG PHỦ")` | Chữ slam hiện trang trọng |
| **391 (108s–112s)** | Cơ ngơi 60.000 mét vuông bước qua thời đại phong kiến | **A** | `File:Prince Gong Mansion Garden.jpg (Toàn cảnh hoa viên)` | Zoom-out toàn cảnh hoa viên rộng lớn |
| **392 (112s–116s)** | Chuyển sang chương cuối: Số phận ngôi nhà bên hồ Thập Sát Hải hôm nay | **A** | `File:Prince Gong Yixin.jpg (Dịch Hân)` | Ken Burns chuyển từ Dịch Hân sang phong cảnh hiện đại |
| **393 (116s–120s)** | Một thế kỷ biến động dữ dội chuẩn bị mở ra | **A** | `File:Shichahai Lake Beijing.jpg (Hồ Thập Sát Hải)` | Lướt trên mặt nước hồ Thập Sát Hải |
| **394 (120s–125s)** | Khép lại chương 12, bước vào chương kết | **D** | `chapter (CHƯƠNG 12: NHÀ ĐỔI CHỦ)` | Thẻ chương chuyển cảnh hoàn tất |

**Tổng kết số liệu chương:**
- Số nhịp: **31 nhịp** | Thời lượng: **125s** | Nhịp trung bình: **4.03s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 68s (54.4%)** | Nhóm B: 12s (9.6%) | Nhóm C: 8s (6.4%) | **Nhóm B+C: 20s (16.0%)** | **Nhóm D: 37s (29.6%)**.
- Số ảnh A sử dụng: **10 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 12 đạt 68s nhóm A (54.4%), sử dụng 17 ảnh tư liệu A (cổng Đinh Phủ 3 lần, An Thiện Đường, Công chúa Hòa Hiếu, Cung Thân vương Dịch Hân 4 bức, hoa viên 2 lần, Gia Lạc Đường, đại hý đài 2 lần, cổng chính, Thập Sát Hải). D làm rõ mốc chuyển giao 1799 sang Vĩnh Lân, 1850 sang Dịch Hân, đính chính khoảng lệch 50 năm trong bách khoa tiếng Việt.

### CH13: KẾT: Phía bắc Thập Sát Hải (140 giây, 35 nhịp, trung bình 4.00s/nhịp)

| Nhịp & Khoảng giây | Ý lời đọc dự kiến (theo plan) | Nhóm | Tài nguyên cụ thể (Key / Ảnh / Prompt / Engine) | Kiểu chuyển động / Visual treatment |
|---|---|:---:|---|---|
| **395 (0s–4s)** | Bước vào chương kết: Hành trình thế kỷ 20 của ngôi nhà phía bắc hồ Thập Sát Hải | **A** | `File:Prince Gong Mansion 1912 Yamanaka.jpg (Ảnh tư liệu 1912)` | Góc chụp tư liệu toàn cảnh Cung Vương Phủ năm 1912 |
| **396 (4s–8s)** | Năm 1912, hãng đồ cổ Yamanaka & Co. của Nhật Bản mua lại và chụp ảnh lưu trữ toàn bộ nội thất | **A** | `File:Prince Gong Mansion 1912 Yamanaka.jpg (Ảnh tư liệu 1912 Yamanaka)` | Pan bức ảnh đen trắng quý giá chụp năm 1912 |
| **397 (8s–12s)** | Những bức ảnh tư liệu năm 1912 lưu giữ nguyên vẹn nội thất gỗ quý của vương phủ trước khi bị phân tán | **A** | `File:Yamanaka 1912 Interior Prince Gong.jpg (Nội thất 1912)` | Zoom chi tiết bàn ghế gỗ trắc và hoành phi cổ |
| **398 (12s–16s)** | Năm 1921, cháu nội Dịch Hân là Phổ Vĩ lâm vào cảnh túng quẫn, thế chấp phủ cho Dòng Biển Đức | **D** | `date ("1921 · THẾ CHẤP CHO DÒNG BIỂN ĐỨC")` | Mốc năm 1921 hiện rõ |
| **399 (16s–20s)** | Các giáo sĩ Công giáo tiếp quản và thành lập nên Đại học Công giáo Phụ Nhân Bắc Kinh | **A** | `File:Fu Jen Catholic University Beijing.jpg (Đại học Phụ Nhân)` | Góc chụp giảng đường Đại học Phụ Nhân thập niên 1930 |
| **400 (20s–24s)** | Những gian phòng vương phủ xưa biến thành giảng đường đại học và thư viện hiện đại | **B** | `ai_09.png (Giảng đường Nho gia kinh điển)` | Pan qua các dãy bàn học gỗ |
| **401 (24s–28s)** | Đại học Phụ Nhân hoạt động tại đây suốt 30 năm cho đến khi các giáo sĩ rời đi vào năm 1951 | **D** | `date ("1951 · KẾT THÚC THỜI KỲ ĐẠI HỌC PHỤ NHÂN")` | Mốc năm 1951 hiện lên |
| **402 (28s–32s)** | Thời kỳ Cách mạng Văn hóa, dinh thự được trưng dụng làm Nhà máy sản xuất điều hòa nhiệt độ Bắc Kinh | **A** | `File:Dingfu Gate Prince Gong.jpg (Cổng Đinh Phủ)` | Pan qua cổng vòm và biển hiệu thời kỳ nhà máy |
| **403 (32s–36s)** | Kế hoạch bài này tuân thủ nguyên tắc: Chỉ nêu công năng tòa nhà, không bình luận chính trị đương đại | **A** | `File:Prince Gong Mansion 1912 Yamanaka.jpg (Tư liệu Yamanaka)` | Pan bức ảnh kiến trúc cổ được bảo tồn |
| **404 (36s–40s)** | Máy móc và xưởng cơ khí đặt ngay trong các gian đại sảnh, may mắn là kết cấu gỗ cổ vẫn trụ vững | **A** | `File:Dingfu Gate Prince Gong.jpg (Cổng Đinh Phủ)` | Pan qua tường gạch cổ kính |
| **405 (40s–44s)** | Năm 1982, chính phủ công nhận Cung Vương Phủ là Di tích bảo hộ trọng điểm cấp quốc gia | **D** | `date ("1982 · DI TÍCH BẢO HỘ TRỌNG ĐIỂM QUỐC GIA")` | Mốc năm 1982 dát vàng nổi bật |
| **406 (44s–48s)** | Các nhà máy và cơ quan dân sự lần lượt được di dời để chuẩn bị cho công cuộc trùng tu lịch sử | **B** | `vid_03.mp4 (Hồi lang phủ đệ cổ kính)` | Camera lướt chậm qua hồi lang được giải tỏa |
| **407 (48s–52s)** | Tháng 11 năm 1996, khu hoa viên lần đầu tiên chính thức mở cửa đón khách tham quan | **D** | `date ("11.1996 · MỞ CỬA HOA VIÊN ĐÓN KHÁCH")` | Mốc tháng 11/1996 hiện lên |
| **408 (52s–56s)** | Ngày 24 tháng 8 năm 2008, đúng dịp Thế vận hội Bắc Kinh, toàn bộ phủ đệ mở cửa trọn vẹn | **D** | `date ("24.08.2008 · MỞ CỬA TOÀN DIỆN SAU TRÙNG TU")` | Mốc ngày 24/8/2008 rực rỡ |
| **409 (56s–60s)** | Khu đại hý đài ngày nay được phục dựng hoàn hảo, đón hàng triệu du khách mỗi năm | **A** | `File:Prince Gong's Mansion Grand Theater Modern.jpg (Đại hý đài ngày nay)` | Góc máy hất lên trần nhà hát rực rỡ ánh đèn |
| **410 (60s–64s)** | Hoa viên Cung Vương Phủ hôm nay là ốc đảo xanh bình yên giữa lòng thủ đô Bắc Kinh hiện đại | **A** | `File:Prince Gong Mansion Garden Today.jpg (Hoa viên hôm nay)` | Pan toàn cảnh hồ nước xanh ngắt và giả sơn |
| **411 (64s–68s)** | Hồ Thập Sát Hải phía nam vẫn êm đềm soi bóng những rặng liễu rủ trăm năm | **A** | `File:Shichahai Lake Beijing.jpg (Cảnh quan Thập Sát Hải hiện nay)` | Góc quay phong cảnh mặt hồ Thập Sát Hải |
| **412 (68s–72s)** | Toàn bộ quần thể rộng hơn 60.000 mét vuông là vương phủ triều Thanh nguyên vẹn nhất còn sót lại | **A** | `File:Prince Gong Mansion Garden Today.jpg (Toàn cảnh hoa viên)` | Zoom-out toàn cảnh 60.000 m2 phủ đệ |
| **413 (72s–76s)** | Hơn hai thế kỷ đã trôi qua kể từ đêm đông định mệnh 22 tháng 2 năm 1799 | **C** | `ai_18.png (Đồng hồ cát trăm năm lịch sử)` | Ánh sáng chiếu xuyên qua đồng hồ cát |
| **414 (76s–80s)** | Hòa Thân, người từng nắm trong tay sinh mạng của hàng vạn người và huyết mạch kinh tế cả đế chế | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Zoom chậm từ từ vào đôi mắt sâu thẳm |
| **415 (80s–84s)** | Đã ra đi dưới một dải lụa trắng, không mang theo được dù chỉ một thỏi bạc hay mảnh ngọc quý | **C** | `ai_03.png (Dải lụa và sự sụp đổ)` | Dải lụa buông hờ trên khay gỗ tối |
| **416 (84s–88s)** | Cán cân lịch sử đã phán xét công và tội của ông qua hơn hai trăm năm tranh cãi | **C** | `ai_05.png (Cán cân lịch sử phán xét công tội)` | Đòn cân tĩnh lặng thăng bằng giữa hư không |
| **417 (88s–92s)** | Một viên thị vệ tài năng, một nhà ngoại giao mẫn tiệp, nhưng cũng là hiện thân của quyền lực tha hóa | **A** | `File:Hesen (cropped).jpg (Chân dung cận nét)` | Focus nét mặt sắc sảo đăm chiêu |
| **418 (92s–96s)** | Sự sụp đổ của ông cũng chính là điềm báo sớm cho sự suy tàn không thể đảo ngược của triều đại Mãn Thanh | **A** | `File:Hall of Supreme Harmony.jpg (Cố Cung hoàng hôn)` | Góc rộng Cố Cung chìm trong ráng chiều tím |
| **419 (96s–100s)** | Những con số của bản kê năm 1799 vẫn tiếp tục là đề tài tranh luận của các thế hệ sử gia | **A** | `File:Heshen 2.jpg (Hòa Thân triều phục)` | Pan từ tà áo lên mũ quan đính ngọc |
| **420 (100s–104s)** | Kho vàng 1,1 tỷ lạng có thể là huyền thoại phóng đại của người đời sau | **D** | `split ("HUYỀN THOẠI KHO VÀNG: 1,1 TỶ LẠNG" vs "SỰ THẬT TƯ LIỆU: BẢN KÊ ĐẦY TRANH CÃI")` | Hai cột đúc kết kết thúc video |
| **421 (104s–108s)** | Nhưng câu chuyện về cuộc đời và sự sụp đổ của ông là bài học lịch sử có thật và nguyên vẹn | **A** | `File:Hesen (cropped).jpg (Chân dung Hòa Thân)` | Zoom vào ánh mắt kiên định của bức tranh lịch sử |
| **422 (108s–112s)** | Câu đóng đắt giá: Ngôi nhà 60.000 mét vuông vẫn còn đó | **A** | `File:Prince Gong's Mansion - Grand Theater.jpg (Đại hý đài)` | Góc máy ngước lên kiến trúc sừng sững |
| **423 (112s–116s)** | Nhưng các con số của kho vàng thì chưa bao giờ đứng yên | **A** | `File:Prince Gong Mansion Garden.jpg (Hoa viên Cung Vương Phủ)` | Pan ngang hồ nước và núi đá hoa viên |
| **424 (116s–120s)** | Hồ Thập Sát Hải chiều nay vẫn lặng lẽ trôi giữa dòng chảy của thời gian | **B** | `vid_08.mp4 (Hồ Thập Sát Hải chiều sương mờ)` | Camera trôi chậm trên mặt hồ mờ sương |
| **425 (120s–124s)** | Mô-típ bản kê hoàn thành dòng thứ mười hai trọn vẹn | **D** | `ledger (DÒNG 12: HOÀN TẤT BẢN KÊ · DI TÍCH QUỐC GIA 60.000 M² TỒN TẠI HÔM NAY)` | Dòng 12 chốt lại toàn bộ mô-típ bản kê |
| **426 (124s–128s)** | Toàn bộ 14 chương của cuộc điều tra lịch sử đã khép lại | **A** | `File:Heshen.jpg (Chân dung Hòa Thân)` | Ken Burns zoom-out từ từ ra xa |
| **427 (128s–132s)** | Hình ảnh Hòa Thân mờ dần vào không gian ký ức | **B** | `ai_06.png (Cổng cung thành mờ xa)` | Ánh ráng chiều buông xuống cổng thành cổ |
| **428 (132s–136s)** | Một thước phim tài liệu lịch sử chân thực và công tâm | **D** | `slam ("HÒA THÂN NGOÀI ĐỜI THẬT: HỒ SƠ KHÉP LẠI")` | Chữ slam kết thúc bộ phim |
| **429 (136s–140s)** | Khép lại chương 13 và toàn bộ video | **D** | `chapter (CHƯƠNG 13: KẾT: PHÍA BẮC THẬP SÁT HẢI)` | Thẻ chương kết thúc trang trọng |

**Tổng kết số liệu chương:**
- Số nhịp: **35 nhịp** | Thời lượng: **140s** | Nhịp trung bình: **4.00s/nhịp**.
- Tỉ lệ nhóm: **Nhóm A: 76s (54.3%)** | Nhóm B: 16s (11.4%) | Nhóm C: 12s (8.6%) | **Nhóm B+C: 28s (20.0%)** | **Nhóm D: 36s (25.7%)**.
- Số ảnh A sử dụng: **13 ảnh**.
- **Đánh giá & Phương án bù đắp:** Chương 13 đạt 76s nhóm A (54.3%), sử dụng 20 ảnh tư liệu A (3 ảnh 1912 Yamanaka, Đại học Phụ Nhân, cổng Đinh Phủ 2 lần, đại hý đài hiện đại & cổ, hoa viên hiện đại & cổ 3 lần, Thập Sát Hải hiện nay, Cố Cung hoàng hôn, 4 bức chân dung Hòa Thân). D chốt trục thời gian 1921-2008, counter 60.000 m², hoàn tất dòng 12 bản kê và slam kết thúc.

---

## 3. Bảng tổng hợp số liệu 14 chương toàn video

| Chương | Tên chương | Thời lượng (s) | Số nhịp | Nhịp TB (s) | Nhóm A (s) | % A | Nhóm B+C (s) | % B+C | Nhóm D (s) | % D | Số ảnh A |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **CH00** | Nhà riêng, 22/2/1799 (Cold Open) | 75s | 18 | 4.17s | 38s | **50.7%** | 16s | 21.3% | 21s | 28.0% | 9 |
| **CH01** | Nghịch lý | 105s | 27 | 3.89s | 55s | **52.4%** | 20s | 19.0% | 30s | 28.6% | 14 |
| **CH02** | Thị vệ cửa cung | 130s | 33 | 3.94s | 71s | **54.6%** | 20s | 15.4% | 39s | 30.0% | 16 |
| **CH03** | Hai mươi bảy tuổi | 120s | 30 | 4.00s | 68s | **56.7%** | 20s | 16.7% | 32s | 26.7% | 17 |
| **CH04** | Đồng liêu | 125s | 31 | 4.03s | 69s | **55.2%** | 20s | 16.0% | 36s | 28.8% | 12 |
| **CH05** | Công chúa Hòa Hiếu | 115s | 29 | 3.97s | 63s | **54.8%** | 24s | 20.9% | 28s | 24.3% | 12 |
| **CH06** | Sứ đoàn năm 1793 | 140s | 34 | 4.12s | 74s | **52.9%** | 21s | 15.0% | 45s | 32.1% | 14 |
| **CH07** | Hoàng đế trên danh | 135s | 33 | 4.09s | 72s | **53.3%** | 24s | 17.8% | 39s | 28.9% | 15 |
| **CH08** | Năm ngày | 130s | 32 | 4.06s | 69s | **53.1%** | 28s | 21.5% | 33s | 25.4% | 14 |
| **CH09** | Bản kê | 145s | 35 | 4.14s | 77s | **53.1%** | 25s | 17.2% | 43s | 29.7% | 16 |
| **CH10** | Hai mươi tội | 130s | 32 | 4.06s | 72s | **55.4%** | 25s | 19.2% | 33s | 25.4% | 16 |
| **CH11** | Gã hề trên màn hình | 115s | 29 | 3.97s | 59s | **51.3%** | 20s | 17.4% | 36s | 31.3% | 11 |
| **CH12** | Nhà đổi chủ | 125s | 31 | 4.03s | 68s | **54.4%** | 20s | 16.0% | 37s | 29.6% | 10 |
| **CH13** | KẾT: Phía bắc Thập Sát Hải | 140s | 35 | 4.00s | 76s | **54.3%** | 28s | 20.0% | 36s | 25.7% | 13 |
| **TỔNG CỘNG** | **14 CHƯƠNG** | **1730s (28m50s)** | **429** | **4.03s** | **931s** | **53.8%** | **311s** | **18.0%** | **488s** | **28.2%** | **68 ảnh duy nhất** |

## 4. Kết luận và Hướng dẫn thực thi kỹ thuật

1. **Tuân thủ quy chuẩn sàn:** Mọi chỉ số ước tính đều vượt hoặc đạt sàn chất lượng của kênh Hình Sự (`floor.py`), nhóm A đạt 53,8% (vượt sàn ≥ 50%), nhóm B+C chiếm 18,0% (dưới trần 25%).
2. **Quy tắc bản quyền và nhãn hiển thị:**
   - Nhóm A sử dụng đúng tên file Commons và các file hiện vật đã tải trong `output/long/hoa-than/img/`. Ghi công đầy đủ cho CC BY / CC BY-SA.
   - Lần đầu tiên nhóm B xuất hiện trong mỗi chương phải có nhãn nhỏ điện ảnh `"TÁI DỰNG MINH HỌA"` (#173). Tuyệt đối không gắn nhãn `"TƯ LIỆU"`.
   - Tuyệt đối không dùng still phim, ảnh diễn viên hay poster phim trong bất kỳ cảnh nào.
3. **Bước tiếp theo:** Sau khi Lead duyệt `visual_plan.md` và `ai_prompts.md`, chuyển sang bước viết kịch bản chi tiết `script.md` bám sát 429 nhịp hình này.
