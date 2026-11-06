# GH-179: Báo cáo gom tư liệu ảnh và nghiên cứu đề tài Hòa Thân

- **Ngày thực hiện:** 06/11/2026
- **Ticket:** GH-179 (Bước 2: Tư liệu trước, chữ sau)
- **Đề tài:** Hòa Thân ngoài đời thật (slug: `hoa-than`, kênh CL)
- **Phạm vi:** Chạy `research_long.py` và `media_search.py`, kiểm soát contact sheet, phân bổ ảnh theo 14 chương trong `data/long/hoa-than/plan.md`. Không viết kịch bản, không sửa code dùng chung, không render, không commit, không đổi lịch phát sóng.
- **Tình trạng:** **ĐẠT** (Tổng cộng 142 ảnh tự do dùng được, vượt xa chỉ tiêu tối thiểu 50 ảnh).

---

## 1. Tổng quan tư liệu thu thập

### 1.1. Các lệnh đã thực thi
1. **Wikimedia Commons (`research_long.py`):**
   - Đợt 1 (10 bài bách khoa theo brief): `Heshen`, `Prince Gong Mansion`, `Qianlong Emperor`, `Jiaqing Emperor`, `Liu Yong (Qing dynasty)`, `Ji Xiaolan`, `Princess Hexiao`, `Qing dynasty`, `Eight Banners`, `Forbidden City` -> thu thập 121 ảnh.
   - Đợt 2 (bổ sung bài và truy vấn liên quan): `?Heshen`, `Macartney Embassy`, `George Macartney, 1st Earl Macartney`, `Prince Gong`, `Agui`, `Shichahai`, `?Prince Gong Mansion` -> nâng tổng số ảnh Commons lên **174 ảnh** (ghi vào `output/long/hoa-than/research.json`, contact sheets `sheet_0.jpg` đến `sheet_4.jpg`).
2. **Kho ngoài Commons (`media_search.py`):**
   - Tìm kiếm với các từ khóa theo brief: `"Qing dynasty court painting"`, `"Qianlong"`, `"Beijing 18th century"`, `"Qing official portrait"`, `"silver tael"`, `"Qing palace"` trên các nguồn `artic`, `europeana`, `wellcome` (tạo `output/long/hoa-than/ext.json` với 418 ứng viên).
   - Tải về thành công **12 ảnh tư liệu chất lượng cao** vào `output/long/hoa-than/img/` kèm metadata bản quyền `.json`. Nguồn Art Institute of Chicago (CC0) và Chester Beatty qua Europeana (CC BY 4.0). Nguồn Wellcome và một số bảo tàng nhỏ châu Âu gặp lỗi DNS/timeout phía máy chủ nên được loại trừ an toàn.

### 1.2. Thống kê kết quả kiểm duyệt
- **Tổng ảnh quét được:** 186 ảnh (174 Commons + 12 kho ngoài).
- **Số ảnh loại bỏ:** 44 ảnh (toàn bộ nằm ở tập Commons, do sai thời kỳ, sai đối tượng, du khách hiện đại hoặc nhầm khái niệm).
- **Tổng ảnh tự do dùng được:** **142 ảnh** (130 Commons + 12 ngoài Commons).

---

## 2. Thống kê ảnh dùng được theo giấy phép và nguồn

### 2.1. Phân bố theo Giấy phép (142 ảnh)

Tất cả 142 ảnh đều tuân thủ nguyên tắc thương mại và quyền chỉnh sửa (`motion/long/SOURCES.md`). Không có ảnh NC (phi thương mại), ND (cấm sửa đổi) hay Fair use.

| Giấy phép | Số lượng | Tỷ lệ (%) | Ghi chú ghi công |
|---|---|---|---|
| **Public domain** | 67 | 47.2% | Không bắt buộc ghi công, trích nguồn tư liệu |
| **CC0** | 16 | 11.3% | Miễn phí bản quyền hoàn toàn (Commons & Art Institute of Chicago) |
| **CC BY-SA 2.0** | 15 | 10.6% | Ghi công + ShareAlike khi phát hành |
| **CC BY-SA 4.0** | 11 | 7.7% | Ghi công + ShareAlike khi phát hành |
| **CC BY 2.0** | 10 | 7.0% | Ghi công tác giả |
| **CC BY-SA 3.0** | 10 | 7.0% | Ghi công + ShareAlike khi phát hành |
| **CC BY 4.0** | 7 | 4.9% | Ghi công tác giả (Bảo tàng Chester Beatty) |
| **CC BY 3.0** | 5 | 3.5% | Ghi công tác giả |
| **CC BY-SA 2.0 fr** | 1 | 0.7% | Ghi công tác giả |
| **Tổng cộng** | **142** | **100.0%** | **Đạt tiêu chuẩn bản quyền kênh CL** |

### 2.2. Phân bố theo Nguồn gốc tư liệu (142 ảnh)

| Nhóm nguồn | Nguồn cụ thể / Bài viết | Số ảnh dùng được | Ghi chú nội dung chính |
|---|---|---|---|
| **Commons** | Qianlong Emperor | 26 | Chân dung Càn Long, ngự mã, săn bắn, tranh lễ nghi triều đình |
| **Commons** | Forbidden City | 25 | Cổng Ngọ Môn, Thái Hòa Điện, Khôn Ninh Cung, kiến trúc Cung đình |
| **Commons** | Prince Gong's Mansion & ?Prince Gong Mansion | 28 | Cổng chính, đại hý đài, hoa viên, hồi lang, ảnh cổ 1912 Yamanaka |
| **Commons** | Qing dynasty | 17 | Bản đồ Đại Thanh 1760, tranh cuộn thương nghiệp, đồ gốm sứ ngự dụng |
| **Commons** | Macartney Embassy | 10 | Tranh tiếp đón Macartney 1793 của William Alexander, chân dung sứ giả |
| **Commons** | ?Heshen & Heshen | 7 | Tranh chân dung Hòa Thân đời Thanh, thư pháp thật của Hòa Thân, Trí Trai tập |
| **Commons** | Chester Beatty Library (Europeana) | 5 | Bản ngự chế Càn Long về tuổi già, tấu sớ dâng miếu hiệu, thơ ngự chế |
| **Commons** | Art Institute of Chicago (artic) | 7 | Long bào đại triều Càn Long, cát phục quan văn, đĩa rồng, chén trà điêu tất |
| **Commons** | Eight Banners | 4 | Đội hình Bát Kỳ, duyệt binh thị vệ cửa cung, nghi trượng |
| **Commons** | Prince Gong | 4 | Chân dung Cung Thân vương Dịch Hân, Tĩnh Quý phi |
| **Commons** | Shichahai | 3 | Cảnh quan Thập Sát Hải bao quanh phủ đệ |
| **Commons** | Jiaqing Emperor | 2 | Chân dung Gia Khánh hoàng đế triều phục |
| **Commons** | Liu Yong (Qing dynasty) | 1 | Chân dung Lưu Dung (Thượng thư Bộ Lại đồng liêu) |
| **Commons** | Ji Yun | 1 | Chân dung Kỷ Hiểu Lam |
| **Commons** | Princess Hexiao | 1 | Chân dung Cố Luân Hòa Hiếu công chúa |
| **Commons** | Agui | 1 | Chân dung Quân cơ đại thần lãnh ban A Quế |
| **Tổng cộng** | | **142** | |

---

## 3. Bảng phân bổ ảnh theo 14 chương của Kế hoạch (`plan.md`)

| # | Tên chương | Nội dung cốt lõi | Số ảnh dùng được | Ảnh tiêu biểu / Tư liệu chính |
|---|---|---|---|---|
| **0** | **Nhà riêng, 22/2/1799** | Cold open: Càn Long mất 15 ngày, Hòa Thân thắt cổ tại tư gia | **4** | `File:Heshen.jpg` (chân dung đời Thanh), `qianlong_essay_old_age` (ngự chế Càn Long về tuổi già), Ngai rồng Càn Thanh Cung, Lăng mộ Dụ Lăng |
| **1** | **Nghịch lý** | Kho vàng vs 2 bài Wikipedia; câu hỏi trung tâm; 3 vòng lặp | **1** | `File:Hesen (cropped).jpg` (chân dung cắt cận nét). *Bù bằng đồ họa bảng số liệu* |
| **2** | **Thị vệ cửa cung** | 1750-1776: Nữu Hỗ Lộc, Bát Kỳ, thị vệ Ngọ Môn gặp Càn Long | **17** | `court_jifu_robe` (cát phục quan đại thần), Càn Long duyệt binh, Bát Kỳ Lam Kỳ, Ngọ Môn, Thái Hòa Môn, bản đồ Tử Cấm Thành |
| **3** | **Hai mươi bảy tuổi** | 1777: Đặc ân cưỡi ngựa trong Tử Cấm Thành, khởi công xây tư dinh | **17** | Tranh Càn Long mặc giáp cưỡi ngựa, 4 bức ngự mã (Siêu Nhị, Lai Viễn Lưu, Nguyệt Quật Lai, Lăng Côn Bạch), Cửu Long bích, phù điêu cung thành |
| **4** | **Đồng liêu** | 1784-1786: Cùng Lưu Dung làm Thượng thư Lại bộ; vụ án Cam Túc | **5** | Chân dung Lưu Dung (`Liu Yong.png`), chân dung Kỷ Hiểu Lam (`Ji Yun.jpg`), 2 bức tranh quan văn triều phục (`wenguan_portrait_1 & 2`), tranh tuần du Nam |
| **5** | **Công chúa Hòa Hiếu** | 1790: Con trai cưới công chúa thứ 10 của Càn Long | **5** | Chân dung Cố Luân Hòa Hiếu công chúa, `bridal_dragon_robe` (long bào hôn lễ), Khôn Ninh Cung, tranh Càn Long hậu phi |
| **6** | **Sứ đoàn năm 1793** | Hòa Thân tiếp đón Huân tước Macartney; ngoại giao triều đình | **15** | Tranh William Alexander vẽ tiếp kiến tại Nhiệt Hà, chân dung Lord Macartney, biếm họa James Gillray 1793, bản vẽ Vạn Lý Trường Thành, ải Cổ Bắc Khẩu |
| **7** | **Hoàng đế trên danh** | 1796-1799: Càn Long Thái thượng hoàng, A Quế mất, Hòa Thân nắm Quân cơ | **16** | Chân dung A Quế (`Agui.jpg`), chân dung Càn Long tuổi già, `emperor_jifu_robe`, các bản ngự chế chiến công Qurman & Hắc Thủy, tranh tiệc biên ải |
| **8** | **Năm ngày** | 7/2 - 12/2 - 15/2 - 22/2/1799: Bắt giữ, chỉ dụ kết án, đổi án thắt cổ | **5** | Chân dung Gia Khánh triều phục (`清仁宗嘉庆皇帝朝服像`), tấu sớ miếu hiệu Càn Long (`qianlong_temple_name`), Thái Hòa Điện, bản đồ Đại Thanh 1820 |
| **9** | **Bản kê** | Phân tích danh sách tài sản: bạc lạng, đồ ngự dụng, kho báu | **9** | Đĩa rồng men lam vàng (`qianlong_dragon_dish`), chén trà điêu tất (`qianlong_lacquer_teabowl`), sách ngọc hoàng gia, bình Peking glass, đồ sứ ngự dụng |
| **10** | **Hai mươi tội** | Bản án 20 tội danh của Gia Khánh; văn bia và thơ phú | **5** | Thư pháp thật của Hòa Thân: Khải thư *Bình Định Đài Loan Vịnh*, bản chép thơ Càn Long *Tụng Hạ Cảnh Sơn Thủy*, tập thơ *Trí Trai văn tập* |
| **11** | **Gã hề trên màn hình** | Phim ảnh (Vương Cương, Lưu Dung...) vs Sự thật lịch sử | **1** | Tranh chân dung Hòa Thân đời Thanh (`File:Hesen.jpg`) làm gốc đối chiếu. *Không dùng ảnh phim/diễn viên* |
| **12** | **Nhà đổi chủ** | 1799 giao Khánh Thân vương; 1850 giao Cung Thân vương Dịch Hân | **21** | Chân dung Cung Thân vương Dịch Hân, Tĩnh Quý phi, điện Gia Lạc Đường, các góc kiến trúc phủ, sân trong, hành lang |
| **13** | **KẾT: Bắc Thập Sát Hải** | Lịch sử tòa nhà: Phụ Nhân, nhà máy, di tích quốc gia, mở cửa hôm nay | **21** | Ảnh Thập Sát Hải hiện nay, cổng phủ Đinh Phủ, đại hý đài, giả sơn, ảnh tư liệu năm 1912 của hãng Yamanaka & Co. |
| | **TỔNG CỘNG** | | **142** | |

---

## 4. Danh sách 44 ảnh đã loại và lý do

Toàn bộ 44 file dưới đây đã được rà soát qua contact sheet và đối chiếu metadata, loại bỏ vì không đúng tiêu chuẩn nội dung của kênh Hình Sự và brief #179:

| STT | Tên file trên Commons | Nguồn bài gốc | Lý do loại bỏ chi tiết |
|---|---|---|---|
| 1 | `File:Western gate of the Temple of Heshen (the River God) in Hequ...jpg` | ?Heshen | Nhầm lẫn danh từ: Miếu thờ **Hà Thần** (thần sông He Shen) ở Hà Khúc, Sơn Tây; không phải nhân vật Hòa Thân |
| 2 | `File:Heshen temple in Hequ, Xinzhou, Shanxi, China.jpg` | ?Heshen | Nhầm lẫn danh từ: Miếu thờ **Hà Thần** (River God) ở Sơn Tây; không phải Hòa Thân |
| 3 | `File:孝洁肃皇后陈氏.jpg` | Forbidden City | Sai triều đại: Hiếu Khiết Túc Hoàng hậu họ Trần là hoàng hậu thời **Minh Thế Tông** (Gia Tĩnh), không thuộc nhà Thanh |
| 4 | `File:Dorgon, the Prince Rui (17th century).jpg` | Qing dynasty | Sai thời kỳ: Nhiếp chính vương Đa Nhĩ Cổn (thế kỷ 17), trước thời Hòa Thân hơn 100 năm |
| 5 | `File:Portrait of the Kangxi Emperor in Court Dress.jpg` | Qing dynasty | Sai thời kỳ: Khang Hy hoàng đế (mất năm 1722), thế hệ ông nội Càn Long |
| 6 | `File:Empress-Dowager-Cixi1.jpg` | Qing dynasty | Sai thời kỳ: Từ Hi Thái hậu (cuối thế kỷ 19) |
| 7 | `File:China imperialism cartoon.jpg` | Qing dynasty | Sai thời kỳ: Tranh biếm họa phân chia Trung Hoa thời Bát quốc liên quân (cuối TK 19) |
| 8 | `File:2ndPrinceChun1.jpg` | Qing dynasty | Sai thời kỳ: Thuần Thân vương Tái Phong (thế kỷ 20, cha vua Phổ Nghi) |
| 9 | `File:Destroying Chinese war junks, by E. Duncan (1843).jpg` | Qing dynasty | Sai thời kỳ: Chiến tranh Nha phiến năm 1843 (sau khi Hòa Thân mất hơn 40 năm) |
| 10 | `File:Great Rear Attack by Our Second Army at Weihaiwei.jpg` | Qing dynasty | Sai thời kỳ: Chiến tranh Giáp Ngọ 1894–1895 |
| 11 | `File:Pitched battle between the imperial and revolutionary army...jpg` | Qing dynasty | Sai thời kỳ: Cách mạng Tân Hợi năm 1911 |
| 12 | `File:Minggunbattle.jpg` | Qing dynasty | Sai thời kỳ: Chiến dịch thời Minh-Thanh thế kỷ 17 |
| 13 | `File:YuanShikaiPresidente1915.jpg` | Qing dynasty | Sai thời kỳ: Tổng thống Viên Thế Khải năm 1915 |
| 14 | `File:Qing new army 1905.jpg` | Qing dynasty | Sai thời kỳ: Tân quân nhà Thanh năm 1905 |
| 15 | `File:Chinese soldiers 1899 1901.jpg` | Eight Banners | Sai thời kỳ: Lính nhà Thanh thời phong trào Nghĩa Hòa Đoàn (1899–1901) |
| 16 | `File:Within historic grounds of the Forbidden City... - NARA - 532582.jpg` | Qing dynasty | Sai thời kỳ: Quân Đồng minh duyệt binh trong Tử Cấm Thành năm 1900 |
| 17 | `File:Puyi, Runqi and Wanrong in the Forbidden City.jpg` | Forbidden City | Sai thời kỳ: Phổ Nghi, Uyển Dung thập niên 1920 |
| 18 | `File:1 dragon dollar Qing dynasty - 1911.png` | Qing dynasty | Sai thời kỳ: Đồng đô la rồng đúc năm 1911 (thời Càn Long dùng bạc thỏi và tiền đồng) |
| 19 | `File:Xián Fēng Tōng Bǎo (咸豐通寶) 1850–1861 Qing Dynasty cash coin.png` | Qing dynasty | Sai thời kỳ: Tiền đồng triều Hàm Phong (1850–1861) |
| 20 | `File:Empire Chinois, Japon (1832).jpg` | Qing dynasty | Sai thời kỳ: Bản đồ xuất bản năm 1832 thời Đạo Quang |
| 21 | `File:Die Gartenlaube (1853) b 445.jpg` | Forbidden City | Không đúng chủ đề: Tranh khắc gỗ tạp chí Đức năm 1853 về Bắc Kinh |
| 22 | `File:Budala5.jpg` | Qing dynasty | Không đúng địa bàn: Cung điện Potala ở Lhasa (Tây Tạng) |
| 23 | `File:Foreign factory site.jpg` | Qing dynasty | Không đúng bối cảnh: Khu xưởng thương gia ngoại quốc Thập Tam Hàng (Quảng Châu) |
| 24 | `File:Chan Clan Ancestral Hall 1930s.jpg` | Qing dynasty | Sai đối tượng và thời kỳ: Nhà thờ họ Trần ở Quảng Châu xây thập niên 1930 |
| 25 | `File:Puankhequa oil painting on a mirror.jpg` | Qing dynasty | Không đúng đối tượng: Tranh vẽ trên gương thương gia Phan Chấn Thừa ở Quảng Châu |
| 26 | `File:Dongyang, Jinhua, Zhejiang, China - panoramio.jpg` | Forbidden City | Sai địa điểm: Cảnh phim trường Hoành Điếm (Chiết Giang), không phải Cố Cung thật |
| 27 | `File:潍坊市美术馆.jpg` | ?Heshen | Không liên quan: Bảo tàng Mỹ thuật thành phố Duy Phường (Sơn Đông) |
| 28 | `File:City Wall of Weixian 01.jpg` | ?Heshen | Không liên quan: Di tích tường thành Duy Huyện (Sơn Đông) |
| 29 | `File:City Wall of Weixian 02.jpg` | ?Heshen | Không liên quan: Tường thành Duy Huyện (Sơn Đông) |
| 30 | `File:City Wall of Weixian 03.jpg` | ?Heshen | Không liên quan: Tường thành Duy Huyện (Sơn Đông) |
| 31 | `File:潍县城墙东段 2020-12-13.jpg` | ?Heshen | Không liên quan: Tường thành Duy Huyện chụp năm 2020 |
| 32 | `File:潍县城墙东段 2020-12-13 2.jpg` | ?Heshen | Không liên quan: Tường thành Duy Huyện chụp năm 2020 |
| 33 | `File:October Bei Hai Beijing China... panoramio (4).jpg` | Prince Gong's Mansion | Chất lượng kém: Ảnh công viên Bắc Hải chụp từ xa, mờ và không rõ kiến trúc phủ |
| 34 | `File:China Proper Map William Mackenzie c1866.png` | Qing dynasty | Sai thời kỳ: Bản đồ Trung Hoa vẽ năm 1866 |
| 35 | `File:Map Asia physical (continental).png` | Qing dynasty | Không đúng bối cảnh: Bản đồ địa hình vật lý châu Á hiện đại |
| 36 | `File:China edcp relief location map.jpg` | Forbidden City | Không đúng bối cảnh: Bản đồ cứu trợ định vị Trung Quốc hiện đại |
| 37 | `File:Flickr - archer10 (Dennis) - China-6164.jpg` | Forbidden City | Ảnh du lịch hiện đại: Du khách chụp lưu niệm trong sân Cố Cung |
| 38 | `File:Flickr - archer10 (Dennis) - China-6237.jpg` | Forbidden City | Ảnh du lịch hiện đại: Du khách chụp lưu niệm trong sân Cố Cung |
| 39 | `File:Un hombre mira la Ciudad Prohibida... bruma y contaminación...` | Forbidden City | Ảnh du lịch hiện đại: Người đàn ông nhìn sương mù ô nhiễm ở Bắc Kinh từ Cảnh Sơn |
| 40 | `File:Beijing 2006 2-48.jpg` | Forbidden City | Ảnh du lịch hiện đại: Du khách năm 2006 |
| 41 | `File:·˙·ChinaUli2010·.· Beijing - Forbidden Town - panoramio (82).jpg` | Forbidden City | Ảnh du lịch hiện đại: Ảnh lưu niệm năm 2010 |
| 42 | `File:2020北京天安门.jpg` | Forbidden City | Ảnh du lịch hiện đại: Quảng trường Thiên An Môn năm 2020 với xe cộ hiện đại |
| 43 | `File:Transmongolie-676 (27131815114).jpg` | Forbidden City | Ảnh du lịch hiện đại: Hành khách trên tàu hỏa Xuyên Mông Cổ |
| 44 | `File:1stViscountMelville2.jpg` | Macartney Embassy | Trùng lặp: Trùng hoàn toàn với bức chân dung Viscount Melville ở index 143 |

---

## 5. Đánh giá các chương ít ảnh và đề xuất giải pháp bù tư liệu

Qua bảng phân bổ, các chương 2, 3, 6, 7, 12, 13 có lượng ảnh rất dồi dào (15–21 ảnh/chương). Một số chương có lượng ảnh dưới 5 ảnh, đã được kiểm tra tính chất và đề xuất phương án bù đắp chi tiết như sau:

### 5.1. Chương 1: Nghịch lý (1 ảnh)
- **Đặc điểm nội dung:** Là chương mở đầu đặt ra bài toán mâu thuẫn giữa truyền thuyết văn hóa (kho vàng vô tận) với các tài liệu bách khoa hiện có (1,1 tỷ lạng bạc vs 60–80 triệu lạng vs 100–800 triệu lạng).
- **Ảnh hiện có:** `Hesen (cropped).jpg` (chân dung Hòa Thân cận cảnh).
- **Phương án bù tư liệu (không dùng AI):**
  1. **Đồ họa bảng so sánh (Comparison Table / Infographic):** Đặt song song 3 cột số liệu (Wikipedia VI, Wikipedia EN, và các ước tính tranh cãi của giới nghiên cứu).
  2. **Trích dẫn văn bản (Quote Card):** Hiển thị câu trích nguyên văn từ các bách khoa kèm ghi chú nguồn kiểm chứng.
  3. **Tái sử dụng luân chuyển:** Lồng ghép xen kẽ hình ảnh phủ đệ (`PrinceGongM2`) và ngự bút Càn Long.

### 5.2. Chương 11: Gã hề trên màn hình (1 ảnh)
- **Đặc điểm nội dung:** Chương này giải ảo hình tượng màn ảnh: phim ảnh cần một vai hài (Vương Cương) và một kẻ thù đối đầu (Lưu Dung), khác hẳn lịch sử thật. Brief và `SOURCES.md` **cấm tuyệt đối dùng ảnh diễn viên, still phim, poster hay ảnh chụp bản tin truyền hình**.
- **Ảnh hiện có:** `File:Hesen.jpg` (tranh chân dung Hòa Thân đời Thanh vẽ sau thời ông).
- **Phương án bù tư liệu (không dùng AI):**
  1. **Hồ sơ nhân vật (Dossier Card / Typography):** Thiết kế thẻ đồ họa ghi tên diễn viên, tác phẩm (*Kỷ Hiểu Lam*, *Tể tướng Lưu gù*, *Thiên mệnh*) và năm phát sóng bằng đồ họa chữ (Motion Typography) trên nền tối.
  2. **Split-Screen đối chiếu:** Một bên là chân dung lịch sử thật của Hòa Thân (`Hesen.jpg`), Lưu Dung (`Liu Yong.png`), bên kia là thẻ phân tích tính cách nhân vật do phim xây dựng.

### 5.3. Chương 0: Nhà riêng, 22/2/1799 & Chương 8: Năm ngày (4–5 ảnh)
- **Đặc điểm nội dung:** Diễn biến nghẹt thở trong 15 ngày sau khi Càn Long mất (7/2 mất Càn Long -> 12/2 bắt giữ -> 15/2 chỉ dụ kết án lăng trì -> 22/2 đổi án ép thắt cổ).
- **Ảnh hiện có:** Chân dung Hòa Thân, Gia Khánh triều phục, tấu sớ miếu hiệu, ngự chế tuổi già, Thái Hòa Điện.
- **Phương án bù tư liệu:**
  1. **Timeline đồ họa chuyển động (Chronological Tracker):** Đồ họa trục thời gian hiển thị từng ngày (7/2, 12/2, 15/2, 22/2) giúp giữ nhịp câu chuyện và duy trì độ tập trung (retention).
  2. **Văn bản chỉ dụ (Document Replica / Slate):** Thể hiện trích đoạn chỉ dụ của Gia Khánh (về việc nể tình Cố Luân Hòa Hiếu công chúa nên ban ân cho tự tận) bằng kiểu chữ Hán-Việt cổ điển trên khung hình.

### 5.4. Chương 9: Bản kê (9 ảnh) & Chương 10: Hai mươi tội (5 ảnh)
- **Đặc điểm nội dung:** Thống kê khối tài sản khổng lồ bị tịch thu và 20 tội danh chính thức.
- **Ảnh hiện có:** Rất đắt giá với thư pháp thật của chính Hòa Thân (*Bình Định Đài Loan Vịnh*, *Trí Trai văn tập*), bát điêu tất ngự chế, đĩa sứ rồng Càn Long, ngọc sách.
- **Phương án bù tư liệu:**
  1. **Bản kê tài sản dạng cuộn (Scrollable Ledger):** Hiển thị từng dòng bản kê (nhà cửa, điền trang, bạc nén, ngọc như ý, đồ ngự dụng) chạy trên màn hình theo đúng mô-típ đã đề ra ở `plan.md`.
  2. **Bảng danh sách 20 tội danh:** Trình bày đồ họa thẻ trích dẫn từng nhóm tội (lạm quyền quân cơ, bất kính hoàng tộc, chiếm đoạt đất đai, tích trữ châu báu).

---

## 6. Kết luận và Kiến nghị bước kế tiếp

1. **Về số lượng và chất lượng tư liệu:**
   - Đợt nghiên cứu đã cung cấp **142 ảnh tự do hợp lệ**, vượt xa yêu cầu (50 ảnh).
   - Có đầy đủ các nhân vật lịch sử then chốt: Hòa Thân, Càn Long, Gia Khánh, Lưu Dung, Kỷ Hiểu Lam, Công chúa Hòa Hiếu, Huân tước Macartney, A Quế, Cung Thân vương Dịch Hân.
   - Có các bảo vật và bút tích lịch sử trực tiếp của chính Hòa Thân (thư pháp khải thư, tập thơ Trí Trai).
2. **Quy tắc tuân thủ:**
   - Tuyệt đối không dùng ảnh AI cho người thật hoặc sự kiện lịch sử thật.
   - Tuyệt đối không dùng ảnh diễn viên hoặc poster phim.
   - Tất cả ảnh ngoài tải về đều đã lưu kèm file chứng minh bản quyền `.json` trong `output/long/hoa-than/img/`.
3. **Kiến nghị:**
   - Tư liệu bước 2 đã hoàn tất và đáp ứng đầy đủ điều kiện để Lead (Claude) xem xét chuyển sang **Bước 3: Viết kịch bản `script.md`** (khoảng 5.500–7.000 âm tiết, 14 chương theo `plan.md`).
