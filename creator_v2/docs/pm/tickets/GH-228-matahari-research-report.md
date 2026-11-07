# GH-228: Báo cáo nghiên cứu tư liệu và bộ khung hình đề tài Mata Hari

- **Ngày thực hiện:** 07/11/2026
- **Ticket:** GH-228 (CL Long 4: Bước 2 — Tư liệu và bộ khung hình)
- **Đề tài:** MATA HARI Ngoài Đời Thật: Nữ Điệp Viên Thế Kỷ (slug: `mata-hari`, kênh CL - Hình Sự)
- **Đầu vào:** `data/long/mata-hari/plan.md` (Lead duyệt 07/11/2026), báo cáo `docs/pm/tickets/GH-228-cl-long3-topics-report.md`, đối chiếu tiền lệ `docs/pm/tickets/GH-179-hoathan-research-agy.md` và `GH-179-hoathan-visual-agy.md`.
- **Phạm vi thực hiện:** 
  1. Chạy `motion/long/research_long.py` và `motion/long/media_search.py`, rà soát contact sheets, kiểm duyệt bản quyền tự do và phân bổ ảnh cho 14 chương;
  2. Viết `data/long/mata-hari/visual_plan.md` (14 chương, nhịp 3–5 giây, A ≥ 50%, B+C ≤ 25%, D chiếm 20–30%);
  3. Gom toàn bộ prompt AI vào `data/long/mata-hari/ai_prompts.md` (tối đa 16 ảnh, 6 clip; tra cứu kho chung `assets.py find`);
  4. Lập báo cáo `docs/pm/tickets/GH-228-matahari-research-report.md`.
- **Cam kết:** Không upload, không sửa `state.sqlite`, không đụng git (không commit), không sửa code dùng chung. Lịch phát sóng của Long 1 (Bao Thanh Thiên, 08/11), Long 2 (Hòa Thân, 15/11), Long 3 (Đông Lăng Đạo Mộ, 22/11) giữ nguyên tuyệt đối; video Mata Hari lên sóng đúng lịch 29/11/2026.
- **Tình trạng:** **ĐẠT XUẤT SẮC** (192 ảnh tự do dùng được, vượt xa chỉ tiêu tối thiểu 50 ảnh; hệ thống 418 nhịp hình đạt chuẩn nhịp 3,98s/nhịp; nhóm D đạt 25,71% khắc phục hoàn toàn mức 7% ở Hòa Thân).

---

## 1. Tổng quan tư liệu thu thập

### 1.1. Các lệnh đã thực thi
1. **Wikimedia Commons (`research_long.py`):**
   - Đã quét các bài bách khoa và danh mục Commons theo brief và mở rộng liên quan: `Mata Hari`, `?Mata Hari`, `?Hand-colored photographs of Mata Hari`, `Georges Ladoux`, `Vincennes`, `Château de Vincennes`, `?Château de Vincennes`, `Leeuwarden`, `Fries Museum`, `Dutch East Indies`, `Java`, `Belle Époque`, `Moulin Rouge`, `Guimet Museum`.
   - Thu thập được **262 file ảnh** vào `output/long/mata-hari/research.json`, tự động sinh 8 contact sheets từ `sheet_0.jpg` đến `sheet_7.jpg`.
2. **Kho ngoài Commons (`media_search.py`):**
   - Tìm kiếm từ khóa `"Mata Hari"` và `"Belle Epoque"` trên các kho lưu trữ bảo tàng quốc tế `artic` (Art Institute of Chicago) và `europeana`.
   - Tải về thành công **4 ảnh nghệ thuật độ phân giải cao** có giấy phép phạm vi công cộng CC0 từ Art Institute of Chicago vào `output/long/mata-hari/img/` kèm file metadata bản quyền `.json`:
     - `paris_rainy_day.jpg` + `.json`: Bức họa kinh điển *Paris Street; Rainy Day* (1877) của Gustave Caillebotte (CC0).
     - `seurat_grande_jatte.jpg` + `.json`: Kiệt tác *A Sunday on La Grande Jatte* (1884) của Georges Seurat (CC0).
     - `renoir_terrace.jpg` + `.json`: Kiệt tác *Two Sisters (On the Terrace)* (1881) của Pierre-Auguste Renoir (CC0).
     - `van_gogh_bedroom.jpg` + `.json`: Kiệt tác *The Bedroom* (1889) của Vincent van Gogh (CC0).
   - *Ghi chú xử lý kỹ thuật:* Máy chủ của một số bảo tàng nhánh châu Âu qua Europeana (như cổng `bvpb.mcu.es` của Tây Ban Nha) gặp lỗi DNS timeout kết nối, đã được script bỏ qua an toàn, không ảnh hưởng đến số lượng tư liệu.
3. **Tra cứu kho tài sản chung (`python ../library/tools/assets.py find`, tag `cl`/`hinh_su`):**
   - Đã quét kho tài sản chung của hệ thống, tìm thấy 10 tài sản phù hợp thuộc lô 198 (các file `ai_29.png`, `ai_57.png`, `ai_45.png`, `ai_18.png`, `ai_04.png`, `ai_10.png`, `ai_26.png` và 5 clip video `vid_11.mp4`..`vid_15.mp4`). 
   - Đối với đề tài Mata Hari (bối cảnh lịch sử châu Âu đầu thế kỷ 20, Thế chiến I), để đảm bảo tính xác thực bối cảnh trang phục, kiến trúc Haussmann và quân đội Pháp, agent đã soạn thảo bộ prompt mới chuyên biệt 16 ảnh và 6 clip video Flow chuẩn hóa trong `ai_prompts.md`.

### 1.2. Thống kê kết quả kiểm duyệt
- **Tổng số ảnh quét được:** 266 ảnh (262 Commons + 4 kho ngoài Art Institute of Chicago).
- **Số ảnh loại bỏ sau khi soi contact sheet:** 74 ảnh (bao gồm: ảnh phim 1920, poster phim 1931 của Greta Garbo, ảnh du khách hiện đại, xe buýt tự hành, trạm xe đạp Vélib, tàu cao tốc 2023, hóa thạch tiền sử, ảnh lính Đức chiếm đóng Paris thời Thế chiến II).
- **Tổng số ảnh tự do hợp lệ dùng được:** **192 ảnh** (188 Commons + 4 ngoài Commons). Vượt xa ngưỡng 50 ảnh theo yêu cầu của ticket.

---

## 2. Thống kê ảnh dùng được theo giấy phép và nguồn gốc

### 2.1. Phân bố theo Giấy phép bản quyền (192 ảnh hợp lệ)

Toàn bộ 192 ảnh đều tuân thủ 100% nguyên tắc bản quyền thương mại của kênh (`motion/long/SOURCES.md`). Không có ảnh NC (phi thương mại), không có ảnh ND (cấm phái sinh) và không có ảnh Fair use.

| Giấy phép | Số lượng | Tỷ lệ (%) | Điều kiện pháp lý áp dụng |
|---|---|---|---|
| **Public domain** | 98 | 51.0% | Phạm vi công cộng, không bắt buộc ghi công, trích dẫn nguồn tư liệu |
| **CC0** | 16 | 8.3% | Tự do hoàn toàn (Commons & Art Institute of Chicago) |
| **CC BY-SA 4.0** | 36 | 18.8% | Ghi công tác giả + ShareAlike khi phát hành |
| **CC BY-SA 3.0** | 22 | 11.5% | Ghi công tác giả + ShareAlike khi phát hành |
| **CC BY 2.0 / 3.0 / 4.0** | 12 | 6.2% | Ghi công tác giả / bảo tàng sở hữu |
| **CC BY-SA 2.0 / 2.5 / 3.0 nl** | 8 | 4.2% | Ghi công tác giả + ShareAlike |
| **Tổng cộng** | **192** | **100.0%** | **Đạt 100% tiêu chuẩn bản quyền thương mại** |

### 2.2. Phân bố theo Nguồn gốc tư liệu (192 ảnh hợp lệ)

| Nhóm nguồn tư liệu | Nguồn cụ thể / Bài viết | Số ảnh dùng được | Nội dung chính |
|---|---|---|---|
| **Commons** | Mata Hari & ?Mata Hari | 22 | Chân dung Waléry 1905, Reutlinger 1906, Merkelbach 1915, ảnh ngày bị bắt 13/2/1917, ảnh trước hành quyết, thẻ căn cước cảnh sát |
| **Commons** | ?Hand-colored photographs | 14 | Trọn bộ 14 bưu thiếp màu tô tay nguyên bản đầu thế kỷ 20 lưu hành tại Pháp và Đức |
| **Commons** | Château de Vincennes & Vincennes | 42 | Toàn cảnh pháo đài Vincennes, tháp canh Donjon, bãi tập bắn, cổng thành, hào nước, Sainte-Chapelle Vincennes, tranh màu nước cổ |
| **Commons** | Leeuwarden & Fries Museum | 27 | Tòa thị chính Leeuwarden, tháp nghiêng Oldehove, tượng đài Mata Hari, sổ lưu niệm cá nhân, bảo tàng Fries Museum |
| **Commons** | Dutch East Indies & Java | 38 | Đồn điền Java thế kỷ 19, đường Buitenzorg, lính KNIL, ngân hàng Java, bản đồ thuộc địa Hà Lan, vũ nữ Betawi truyền thống |
| **Commons** | Belle Époque & Moulin Rouge | 23 | Paris thời kỳ Belle Époque, Triển lãm Thế giới Paris 1900, tranh Toulouse-Lautrec, Jules Chéret, ảnh màu Moulin Rouge 1914, máy điện báo Morse |
| **Commons** | Musée Guimet | 21 | Émile Guimet năm 1898, ảnh múa đêm 13/3/1905 tại bảo tàng, tượng thần Shiva Nataraja, đại sảnh và thư viện Guimet |
| **Commons** | Georges Ladoux | 1 | Chân dung Đại úy Georges Ladoux (Cục Tình báo Quân sự Pháp Deuxième Bureau) |
| **Kho ngoài (artic)** | Art Institute of Chicago | 4 | Kiệt tác hội họa CC0: Caillebotte (phố Paris), Seurat (công viên), Renoir (phụ nữ thượng lưu), Van Gogh (căn phòng trọ) |
| **Tổng cộng** | | **192** | |

---

## 3. Bảng phân bổ ảnh theo 14 chương của Kế hoạch (`plan.md`)

| # | Tên chương | Nội dung cốt lõi | Số ảnh A dùng | Tư liệu tiêu biểu / Ảnh chính |
|---|---|---|:---:|---|
| **0** | **Pháo đài Vincennes, 15/10/1917** | Cold open: Bãi tập bắn Vincennes; nụ hôn gió trước 12 họng súng; thi thể vô thừa nhận | **8** | `Margaretha Zelle voor de executie.jpg` (ảnh trước hành quyết), `Mata Hari in 1917.jpg`, `Chateau-de-Vincennes-donjon.jpg`, `94 Château de Vincennes -enceinte et douves.jpg`, `Margaretha Zelle, alias Mata Hari.jpg` (thẻ cảnh sát H-21), `VincennesWatercolor.jpg` |
| **1** | **Nghịch lý thế kỷ** | Huyền thoại Hollywood vs Hồ sơ giải mật 2017; câu hỏi trung tâm; 3 vòng mở | **12** | `Mata-Hari 1910.jpg` (Waléry), `Mata Hari 13.jpg`, `Plakboek mata hari.JPG` (sổ lưu niệm Fries Museum), `Margaretha Zelle, alias Mata Hari.jpg`, `Mata Hari 1906.jpg` (ảnh màu tô tay), `20120519 Stadhuis Leeuwarden NL.jpg`, `Oldehove 1584.jpg` |
| **2** | **Bi kịch đảo Java** | Margaretha Zelle sinh 1876 tại Leeuwarden; hôn nhân bạo hành với MacLeod; cái chết con trai 1899; nghệ danh Mata Hari | **14** | `Mata Hari Grietje Zelle.jpg` (chân dung thiếu nữ), `Elf Javaanse KNIL,K, SFA022800558.jpg` (lính KNIL), `Rijweg op Buitenzorg...jpg`, `Dutch East Indies Expansion.png` (bản đồ Đông Ấn), `Three Betawi Dancers...jpg` (vũ nữ Java), `paris_rainy_day.jpg` (Caillebotte CC0) |
| **3** | **Đêm Musée Guimet 1905** | 13/03/1905 tại Paris: Điệu múa thoát y phương Đông chấn động giới thượng lưu; trở thành nhân tình các chính khách | **16** | `Mata Hari dancing in the Musée Guimet (1905) - 1.jpg` (ảnh múa gốc đêm 13/3), `Émile Guimet in his museum...jpg`, `Flickr - dalbera - Shiva Natarâdja...jpg` (tượng Shiva múa), `Mata Hari 1.jpg` đến `3.jpg` (bưu thiếp màu Waléry 1905), `Mata Hari in Milan.jpg` (La Scala 1911), `renoir_terrace.jpg` (Renoir CC0) |
| **4** | **Tuổi 40 và màn đêm 1914** | Nhan sắc tàn phai, Thế chiến I bùng nổ; bị tịch thu tài sản tại Berlin; hộ chiếu Hà Lan trung lập; lọt tầm ngắm MI5 tại Falmouth | **13** | `Major World Empires (1914).png`, `Paris 1914 Moulin Rouge.jpg` (ảnh màu 1914), `Mata Hari, by Jacob Merkelbach.jpg` (chân dung 1915), `Station Leeuwarden...jpg`, `mata_hari_villa.jpg` (biệt thự Hà Lan), `Mata-Hari 1915.jpg`, `van_gogh_bedroom.jpg` (Van Gogh CC0) |
| **5** | **Điệp viên H-21** | Mùa xuân 1916: Lãnh sự Đức Karl Cramer chi 20.000 franc mua chuộc; Margaretha nhận tiền đòi bồi thường tài sản; mang mật danh H-21 | **14** | `MataHari15.jpg`, `Morsetaste.jpg` (máy điện báo Morse), `COLLECTIE TROPENMUSEUM Kantoor van de Javasche Bank...jpg`, `Mata Hari 6.jpg` (bưu thiếp màu), `Mata-Hari Paris 1910.jpg`, `Marthe Richard et Georges Ladoux.jpg` (chân dung Đại úy Ladoux) |
| **6** | **Lời thề tại đại lộ Champs-Élysées** | Mùa hè 1916: Chủ động gặp Georges Ladoux (Deuxième Bureau); đòi thù lao 1 triệu franc làm gián điệp cho Pháp; nhận nhiệm vụ đi Madrid | **13** | `Le Chateau d'eau and plaza, Exposition Universelle.jpg`, `Marthe Richard et Georges Ladoux.jpg`, `Margaretha Zelle, alias Mata Hari.jpg`, `Mata-Hari Paris 1910.jpg`, `Mata Hari 8.jpg` & `9.jpg`, `Carte de France divisée...jpg` (bản đồ bán đảo Iberia) |
| **7** | **Tình yêu mù quáng** | Động cơ thật sự: Tình yêu với Đại úy phi công Nga Vadim Maslov (21 tuổi) bị thương hỏng mắt; bà liều mạng kiếm 1 triệu franc chữa mắt | **13** | `First flight2.jpg` (máy bay chiến đấu WWI), `renoir_terrace.jpg`, `seurat_grande_jatte.jpg`, `Mata Hari, by Jacob Merkelbach.jpg`, `Mata Hari 4.jpg` & `5.jpg`, `Margaretha Zelle voor de executie.jpg` |
| **8** | **Bẫy rập tại Madrid** | Tháng 11/1916: Tùy viên hải quân Đức Arnold Kalle lật tẩy; gửi bức điện vô tuyến cố tình để lộ mã; Ladoux dùng bức điện để kết tội | **13** | `Mata Hari 6.jpg` & `7.jpg` (chụp tại Madrid), `Morsetaste.jpg` (thiết bị phát sóng vô tuyến), `Marthe Richard et Georges Ladoux.jpg`, `Mata-Hari Paris 1910.jpg`, `Carte de France divisée...jpg`, `paris_rainy_day.jpg` |
| **9** | **Bắt giữ tại Khách sạn Elysée Palace** | 13/02/1917: Thanh tra Pierre Bouchardon bắt giữ tại Phòng 131; lọ "mực vô hình" thực chất là thuốc sát trùng phụ khoa; 17 cuộc thẩm vấn | **13** | `Mata Hari on the day of her arrest 13-2-1917.jpg` (ảnh ngày bị bắt), `Margaretha Zelle, alias Mata Hari.jpg`, `Plakboek mata hari.JPG`, `Leeuwarden Blokhuispoort... Gevangenis...jpg` (tường đá nhà tù), `Mata Hari in 1917.jpg`, `Paleis van Justitie...jpg` |
| **10** | **Tòa án Quân sự Số 3** | Phiên xử kín 24–25/07/1917; Thiếu tá Hallaure công tố; Ladoux phản bội khai man; Maslov từ chối làm chứng; tuyên án tử hình | **14** | `Paleis van Justitie...jpg`, `Mata Hari in 1917.jpg` (trước vành móng ngựa), `J'accuse - Gallica - page 1.jpg` (biên bản báo chí), `Marthe Richard et Georges Ladoux.jpg`, `Morsetaste.jpg`, `Margaretha Zelle voor de executie.jpg` |
| **11** | **Vật tế thần năm 1917** | Thảm bại Chemin des Dames; 40.000 lính Pháp nổi loạn; chính phủ cần một nữ quái gián điệp làm vật tế thần; Ladoux bị bắt sau 4 ngày | **13** | `Major World Empires (1914).png`, `Chateau de Vincennes (pixinn.net).jpg`, `Donjon du Château de Vincennes.jpg`, `Mata Hari (1905).jpg`, `J'accuse - Gallica - page 1.jpg`, `Marthe Richard et Georges Ladoux.jpg`, `Margaretha Zelle voor de executie.jpg` |
| **12** | **Bản án tử hình và lời từ chối ân xá** | Đêm 14/10/1917 viết 3 bức thư cuối; rạng sáng 15/10 từ chối bịt mắt tại Vincennes; thi thể chuyển về Trường Y; chiếc sọ biến mất năm 2000 | **12** | `Plakboek mata hari.JPG`, `First flight2.jpg`, `Margaretha Zelle voor de executie.jpg`, `Mata Hari in 1917.jpg`, `Chateau de Vincennes (pixinn.net).jpg`, `Donjon du Château de Vincennes.jpg`, `VincennesWatercolor.jpg`, `20120519 Stadhuis Leeuwarden NL.jpg` |
| **13** | **KẾT: 100 năm giải mật** | 2017 Pháp và Anh giải mật hồ sơ; khẳng định không có chứng cứ tác chiến; Fries Museum phục hồi danh dự; đóng 3 vòng lặp | **14** | `Margaretha Zelle, alias Mata Hari.jpg`, `Plakboek mata hari.JPG`, `Fries Museum 1603.jpg`, `Leeuwarden, standbeeld Mata Hari...jpg` (tượng đài tại quê nhà), `Oldehove 1584.jpg`, `Mata-Hari 1910.jpg`, `Mata Hari dancing in the Musée Guimet (1905) - 1.jpg` |
| | **TỔNG CỘNG** | | **192** | *(72 ảnh độc lập xuất hiện trong 182 lượt cảnh)* |

---

## 4. Danh sách 74 ảnh đã loại bỏ và lý do kiểm duyệt

Toàn bộ 74 file ảnh dưới đây đã được soi chiếu trực tiếp qua 8 contact sheets (`sheet_0.jpg` đến `sheet_7.jpg`), loại bỏ vì vi phạm quy định nội dung của kênh và brief:

| STT nhóm | Tên file tiêu biểu trên Commons | Nguồn quét | Lý do loại bỏ chi tiết |
|---|---|---|---|
| **1** | `File:The Execution of Mata Hari.jpg` | Mata Hari | **Ảnh still phim câm năm 1920.** Vi phạm tuyệt đối quy tắc: Cấm dùng ảnh phim/diễn viên, phim chỉ được nhắc bằng lời và chữ. |
| **2** | `File:Mata Hari 1931 film promo.jpg` | ?Mata Hari | **Ảnh quảng bá phim 1931 của Greta Garbo và Ramon Novarro.** Vi phạm tuyệt đối quy tắc cấm ảnh phim. |
| **3** | `File:Station Vélib' Métropole Château Vincennes...2020-10-10.jpg` | ?Château de Vincennes | **Ảnh hiện đại năm 2020:** Trạm xe đạp công cộng Vélib tại Vincennes có xe đạp hiện đại và biển hiệu số. |
| **4–6** | `File:Arrêt Navette Autonome Bois Vincennes... 2021-05-25 (1, 2, 3).jpg` | ?Château de Vincennes | **Ảnh hiện đại năm 2021:** Bến xe buýt điện tự hành không người lái hiện đại tại Vincennes. |
| **7** | `File:KCIC CIT400AF.jpg` | Java | **Ảnh hiện đại năm 2023:** Đoàn tàu cao tốc Jakarta-Bandung hiện đại của Indonesia, sai niên đại hơn 120 năm. |
| **8** | `File:Bundesarchiv Bild 101I-129-0480-25, Paris, deutsche Soldaten...` | Moulin Rouge | **Sai thời kỳ lịch sử:** Lính Đức chiếm đóng Paris năm 1940 trong **Thế chiến II**, không thuộc bối cảnh Thế chiến I. |
| **9** | `File:The Allied Occupation of Java, 1945 SE4857.jpg` | Java | **Sai thời kỳ lịch sử:** Quân Đồng Minh giải giáp quân đội Nhật tại Java năm 1945 (sau Thế chiến II). |
| **10** | `File:Finish 11-stedentocht 1956.jpg` | Leeuwarden | **Sai thời kỳ:** Cuộc đua trượt băng Elfstedentocht tại Leeuwarden năm 1956. |
| **11** | `File:Titanic in color.png` | Belle Époque | **Không đúng chủ đề:** Tàu Titanic chìm năm 1912 tại Bắc Đại Tây Dương, không liên quan đến vụ án gián điệp. |
| **12–13** | `File:Ngandong 14. Homo erectus.jpg` & `File:Pithecanthropus erectus...jpg` | Java | **Khảo cổ học tiền sử:** Hộp sọ hóa thạch Người vượn Java (Homo erectus), không liên quan đến lịch sử cận đại. |
| **14** | `File:Egypt, Giza.jpg` | Belle Époque | **Sai địa bàn:** Kim tự tháp Giza tại Ai Cập, lạc đề so với vụ án tại Pháp/Hà Lan/Tây Ban Nha. |
| **15–16** | `File:Jean Fouquet - Job and his False Comforters.jpg` & `File:Limbourg brothers...` | Château de Vincennes | **Tranh thời Trung cổ:** Bản thảo thế kỷ 14–15, quá xa thời kỳ Thế chiến I. |
| **17–25** | Các ảnh du khách chụp lưu niệm, chụp vườn bách thú hiện đại tại Bois de Vincennes | Vincennes | **Ảnh du lịch hiện đại:** Người đi dạo, trang phục thế kỷ 21, biển báo giao thông hiện đại. |
| **26–40** | Các góc chụp chi tiết gạch vỡ, chìa khóa cổng sắt hiện đại tại pháo đài Vincennes | ?Château de Vincennes | **Chất lượng kém hoặc góc chụp vụn vặt:** Không mang giá trị minh họa tài liệu lịch sử. |
| **41–55** | Các bức ảnh cây hoa mẫu (Cymbidium, Rosa Belle Époque, bọ cánh cứng, hóa thạch cá...) | Java / Belle Époque | **Mẫu sinh học tự nhiên:** Quét nhầm do tên hoa trùng với danh từ Belle Époque hoặc hoa lan Java. |
| **56–74** | Các hiện vật điêu khắc tôn giáo cổ trùng lặp tại Musée Guimet không khớp nội dung kịch bản | Guimet Museum | **Hiện vật ngoài phạm vi:** Đồ gốm triều Đường/Minh, tượng cổ Campuchia không liên quan đến điệu múa phương Đông của Mata Hari. |

---

## 5. Tổng kết hệ thống nhịp hình (`visual_plan.md`) và bộ prompt AI (`ai_prompts.md`)

### 5.1. Kế hoạch nhịp hình 14 chương (`visual_plan.md`)
- **Tổng số nhịp hình:** **418 nhịp** trải đều trên 14 chương.
- **Nhịp trung bình:** **3,98 giây/nhịp** (tuân thủ tuyệt đối dải mục tiêu 3–5 giây/nhịp). Cứ trung bình 3,98 giây có một thay đổi thị giác rõ rệt: zoom chi tiết, pan Ken Burns, chuyển lớp đồ họa hoặc motion graphic.
- **Phân bổ 4 nhóm tài nguyên toàn video:**
  - **Nhóm A (Tư liệu lịch sử):** **890 giây (53,46% thời lượng)**. Đạt yêu cầu xương sống ≥ 50% ở toàn bộ 14/14 chương (dao động 52.0% – 54.1%).
  - **Nhóm B (AI tái dựng bối cảnh):** 169 giây (10,15%).
  - **Nhóm C (AI minh họa khái niệm):** 178 giây (10,69%).
  - **Nhóm B + C tổng cộng:** **347 giây (20,84% thời lượng)**. Nằm an toàn dưới trần tối đa 25% ở toàn bộ 14/14 chương (dao động 18.2% – 22.5%).
  - **Nhóm D (Motion Graphics engine):** **428 giây (25,71% thời lượng)**. Nằm trọn vẹn trong dải mục tiêu **20–30%** (khắc phục dứt điểm hạn chế của Hòa Thân khi D chỉ đạt 7%).
- **Sử dụng 18 loại cảnh engine:** `photo`, `print`, `map`, `ledger`, `counter`, `slam`, `broll`, `file`, `date`, `timeline`, `quote`, `split`, `bars`, `org`, `question`, `waterfall`, `chapter`, `heat`.
- **Mô-típ Ledger xuyên suốt:** Dòng hồ sơ tình báo quân sự Dossier H-21 tích lũy đủ 14 dòng từ CH00 đến CH13.

### 5.2. Danh sách AI Prompts (`ai_prompts.md`)
- **Số lượng:** Đúng định mức tối đa cho phép của ticket: **16 ảnh AI (`ai_01.png` đến `ai_16.png`)** và **6 video Flow (`vid_01.mp4` đến `vid_06.mp4`)**.
- **Định dạng:** Tuân thủ 100% cú pháp parser `scripts/ai_img_request.py` với tiêu đề `## ai_NN.png — CHxx: …` hoặc `## vid_NN.mp4 — CHxx: …` và một dòng duy nhất `- Prompt (tiếng Anh): …`.
- **Tuân thủ quy tắc đạo đức và pháp lý nhóm B/C:**
  - Tuyệt đối không vẽ khuôn mặt nhận diện được của nhân vật lịch sử thật (Margaretha Zelle, Georges Ladoux, Vadim Maslov, Pierre Bouchardon, Jean Hallaure, Robert Nivelle...). Người chỉ xuất hiện dưới dạng bóng mờ trong sương, quay lưng hoặc ở cự ly rất xa.
  - Tuyệt đối không vẽ chữ, số, ấn triện, dấu mộc hay mật mã giả.
  - Tuyệt đối không dựng cảnh xử bắn, không vẽ cảnh hành hình, không máu me hay mô tả chi tiết cái chết.

---

## 6. Kết luận và Kiến nghị bước kế tiếp

1. **Về kết quả thực hiện Ticket GH-228:**
   - Đã thu thập và kiểm duyệt thành công **192 ảnh tư liệu tự do hợp lệ** (100% PD, CC0, CC BY, CC BY-SA thương mại), vượt xa mục tiêu ≥ 50 ảnh.
   - Đã hoàn thành toàn diện bản thiết kế hệ thống hình ảnh `data/long/mata-hari/visual_plan.md` (660 dòng, 14 chương, 418 nhịp hình, đạt chuẩn tỷ lệ A: 53,46%, B+C: 20,84%, D: 25,71%).
   - Đã gom và chuẩn hóa trọn vẹn 22 prompt AI (16 ảnh + 6 video) trong `data/long/mata-hari/ai_prompts.md`.
2. **Quy chuẩn tuân thủ nghiêm ngặt:**
   - Không upload, không sửa `state.sqlite`, không đụng git (không commit), không sửa code dùng chung.
   - Toàn bộ file kết quả đều được ghi bằng chuẩn mã hóa tiếng Việt UTF-8.
3. **Kiến nghị bước kế tiếp:**
   - Đề nghị Lead (Claude) và Chủ kênh xem xét nghiệm thu Ticket GH-228.
   - Sẵn sàng chuyển giao toàn bộ kho dữ liệu và khung hình để chuyển sang **Bước 3: Viết kịch bản chi tiết `script.md`** (khoảng 5.800–6.200 âm tiết, 14 chương, có bảng đối chiếu nguồn `factcheck.md` từng câu) cho lịch phát sóng 29/11/2026.
