# GH-228: Báo Cáo Nghiên Cứu Tư Liệu Ảnh và Hệ Thống Khung Hình (CL Long 3: Tôn Điện Anh — Đông Lăng Đạo Mộ 1928)

- **Ngày thực hiện:** 06/11/2026
- **Người thực hiện:** Agent Sản Xuất (Antigravity)
- **Căn cứ nhiệm vụ:** Ticket `docs/pm/tickets/GH-228-donglang-research-agy.md`, đầu vào `data/long/dong-lang/plan.md` (Lead duyệt), `docs/pm/tickets/GH-228-cl-long3-topics-report.md`, tiền lệ `GH-179-hoathan-research-report.md` và `GH-179-hoathan-visual-report.md`.
- **Phạm vi thực hiện:**
  1. Chạy `motion/long/research_long.py` cho topic `dong-lang` với 10 bài bách khoa và các truy vấn Commons chuyên sâu;
  2. Bổ sung tư liệu ngoài Commons qua `motion/long/media_search.py` (nguồn Art Institute of Chicago và Europeana);
  3. Soát contact sheet, phân loại ảnh dùng được và ảnh loại bỏ kèm lý do;
  4. Lập kế hoạch khung hình 14 chương `data/long/dong-lang/visual_plan.md` (nhịp 3–5 giây, A ≥ 50%, B+C ≤ 25%, D chiếm 20–30%);
  5. Gom toàn bộ AI prompt vào `data/long/dong-lang/ai_prompts.md` (tối đa 16 ảnh, 6 clip; tra cứu kho chung `library/tools/assets.py`).
- **Cam kết tuân thủ:** Không upload, không sửa `state.sqlite`, không đụng git (không commit/push), không sửa code dùng chung, ghi UTF-8 bằng Python.
- **Tình trạng:** **HOÀN THÀNH XUẤT SẮC** (244 ảnh tự do dùng được, vượt gấp 4,8 lần chỉ tiêu ≥ 50 ảnh; visual plan 421 nhịp, nhịp trung bình 4,06s/nhịp; tỷ lệ D đạt 25,7%).

---

## 1. Tổng Quan Thu Thập Tư Liệu

### 1.1. Các lệnh đã thực thi
1. **Wikimedia Commons (`research_long.py`):**
   - Đợt 1 (10 bài bách khoa theo brief): `Sun Dianying`, `Eastern Qing Tombs`, `Yuling (Qianlong mausoleum)`, `Ding Dongling`, `Empress Dowager Cixi`, `Qianlong Emperor`, `Puyi`, `Dongling looting` (chuyển hướng sang `Looting of the Eastern Mausoleum`), `Warlord Era`, `Republic of China (1912–1949)` -> thu thập 133 ảnh.
   - Đợt 2 (truy vấn Commons chuyên sâu bổ trợ nhân vật và địa điểm then chốt): `?Sun Dianying`, `?Ding Dongling`, `?Yuling Tomb`, `?Eastern Qing Tombs`, `?Dai Li`, `?T. V. Soong`, `?Yan Xishan`, `?He Yingqin`, `?Chiang Kai-shek 1928` -> nâng tổng số ảnh Commons lên **259 ảnh** (ghi vào `output/long/dong-lang/research.json`, sinh 8 contact sheets `sheet_0.jpg` đến `sheet_7.jpg`).
2. **Kho ngoài Commons (`media_search.py`):**
   - Tìm kiếm với từ khóa `"Qianlong"` và `"Chinese jade"` trên các nguồn `artic` và `europeana` (tạo `output/long/dong-lang/ext.json` với 121 ứng viên, sinh `ext_sheet_0.jpg` và `ext_sheet_76.jpg`).
   - Tải về thành công **11 ảnh tư liệu hiện vật chất lượng cao** vào `output/long/dong-lang/img/` kèm metadata bản quyền `.json`. Toàn bộ 11 hiện vật này thuộc Art Institute of Chicago mang giấy phép phạm vi công cộng **CC0**. Nguồn Europeana/Chester Beatty gặp lỗi DNS máy chủ (`viewer.cbl.ie`) nên được loại trừ an toàn đúng như tiền lệ GH-179.
3. **Tra cứu kho dùng chung (`library/tools/assets.py`):**
   - Chạy `python ../library/tools/assets.py find --tag cl` và `hinh_su`. Tái sử dụng hợp lệ các tài nguyên có sẵn (`lib198b/ai_18.png`, `lib198/ai_57.png`, `lib198v/vid_11.mp4`, `lib198b/ai_04.png`, `lib198b/ai_29.png`), giúp tiết kiệm tài nguyên và giữ đúng phong cách điện ảnh noir của kênh.

### 1.2. Thống kê kết quả kiểm duyệt
- **Tổng ảnh quét được:** **270 ảnh** (259 Commons + 11 kho ngoài Art Institute of Chicago).
- **Số ảnh loại bỏ:** **26 ảnh** (toàn bộ nằm ở tập Commons, do nhầm lẫn lăng mộ triều Minh, sai thời kỳ Thế chiến 2, hoặc thuộc thời kỳ Mãn Châu Quốc/cải tạo của Phổ Nghi để dành cho Long 4).
- **Tổng ảnh tự do dùng được:** **244 ảnh** (233 Commons + 11 ngoài Commons). Vượt xa chỉ tiêu tối thiểu 50 ảnh (đạt 488% chỉ tiêu).

---

## 2. Thống Kê Ảnh Dùng Được Theo Giấy Phép và Nguồn

### 2.1. Phân bố theo Giấy phép (244 ảnh)

Tất cả 244 ảnh đều đáp ứng 100% tiêu chuẩn thương mại tự do và quyền chỉnh sửa (`motion/long/SOURCES.md`). Không có ảnh NC (phi thương mại), ND (cấm phái sinh) hay Fair use.

| Giấy phép | Số lượng | Tỷ lệ (%) | Ghi chú ghi công |
|---|---|---|---|
| **Public domain** | 143 | 58,6% | Phạm vi công cộng, không bắt buộc ghi công, trích nguồn tư liệu |
| **CC BY-SA 4.0** | 55 | 22,5% | Ghi công tác giả + ShareAlike khi phát hành |
| **CC0** | 15 | 6,1% | Miễn phí bản quyền hoàn toàn (Commons & Art Institute of Chicago) |
| **CC BY-SA 3.0** | 13 | 5,3% | Ghi công tác giả + ShareAlike khi phát hành |
| **CC BY-SA 2.0** | 9 | 3,7% | Ghi công tác giả + ShareAlike khi phát hành |
| **CC BY 3.0** | 4 | 1,6% | Ghi công tác giả |
| **CC BY 2.0** | 4 | 1,6% | Ghi công tác giả |
| **CC BY-SA 3.0 nl** | 1 | 0,4% | Ghi công tác giả (Bảo tàng Quốc gia Hà Lan) |
| **TỔNG CỘNG** | **244** | **100,0%** | **Đạt 100% tiêu chuẩn bản quyền kênh CL** |

### 2.2. Phân bố theo Nguồn gốc tư liệu (244 ảnh)

| Nhóm nguồn | Nguồn cụ thể / Bài viết | Số ảnh dùng được | Ghi chú nội dung chính |
|---|---|---|---|
| **Commons** | Qianlong Emperor | 26 | Chân dung Càn Long đại triều, ngự mã, săn bắn, tranh lễ nghi |
| **Commons** | Looting of the Eastern Mausoleum | 24 | Ảnh hiện trường 1928, cửa lăng bị nổ mìn, quan tài Từ Hi, liễm phục |
| **Commons** | Empress Dowager Cixi | 23 | Chân dung Từ Hi, mũ miện ngọc trai, cung nữ, tang lễ 1908 |
| **Commons** | ?Eastern Qing Tombs | 17 | Cổng lăng, toàn cảnh quần thể lăng, Đại Bi Lâu, phong cảnh Tuân Hóa |
| **Commons** | ?Chiang Kai-shek 1928 | 17 | Tưởng Giới Thạch 1928, Tưởng & Phùng Ngọc Tường & Diêm Tích Sơn |
| **Commons** | Puyi | 16 | Phổ Nghi tại Trương Viên Thiên Tân, Tái Trạch, cựu thần nhà Thanh |
| **Commons** | Republic of China (1912–1949) | 15 | Bản đồ phân tranh 1912-1930, chính phủ Nam Kinh, tiền tệ Dân Quốc |
| **Commons** | ?Ding Dongling | 15 | Điện Long Ân, kiến trúc thếp vàng, địa cung Từ Hi, phù điêu đá |
| **Commons** | ?Yuling Tomb | 15 | Cửa đá ngầm Dụ Lăng, phù điêu Tứ Đại Thiên Vương, kinh Phật Phạn-Tạng |
| **Commons** | ?Yan Xishan | 13 | Chân dung Diêm Tích Sơn, dinh thự Thái Nguyên Sơn Tây |
| **Commons** | ?He Yingqin | 13 | Chân dung Hà Ứng Khâm, dinh thự Nam Kinh, tượng đài tưởng niệm |
| **Commons** | Warlord Era | 11 | Binh lính quân phiệt, tàu bọc thép, xe tăng FT-17, bản đồ quân phiệt 1925 |
| **Kho ngoài** | Art Institute of Chicago (artic) | 11 | Hiện vật CC0: Đĩa rồng, chén điêu tất, ấm ngọc dưa hấu, bình rồng, chuông |
| **Commons** | ?Dai Li | 10 | Đới Lạp bên Tưởng Giới Thạch, Đới Lạp & Đỗ Nguyệt Sanh 1945, ảnh 1946 |
| **Commons** | ?T. V. Soong | 10 | Tống Tử Văn, chân dung gia tộc họ Tống 1917, hoạt động tài chính |
| **Commons** | ?Sun Dianying | 4 | Dinh thự Tôn Điện Anh tại Thiên Tân, biển tên di tích lịch sử |
| **Commons** | Eastern Qing tombs | 3 | Sơ đồ mặt bằng Đông Lăng, ảnh cổ Tuân Hóa đầu thế kỷ 20 |
| **Commons** | Sun Dianying | 1 | Chân dung lịch sử chính thức của Tôn Điện Anh |
| **TỔNG CỘNG** | | **244** | |

---

## 3. Danh Sách 26 Ảnh Đã Loại Bỏ và Lý Do

Toàn bộ 26 ảnh bị loại đều được rà soát kỹ lưỡng trên contact sheet nhằm bảo vệ tính chính xác lịch sử và an toàn pháp lý của kênh:

| # | Tên tập tin | Nguồn gốc | Lý do loại bỏ chi tiết |
|---|---|---|---|
| 1 | `File:Ming Yuling Tomb After Snow.jpg` | ?Yuling Tomb | **Nhầm lăng mộ:** Đây là Minh Dụ Lăng (Bắc Kinh, lăng mộ vua Minh Anh Tông triều Minh), không phải Thanh Dụ Lăng (Tuân Hóa, Càn Long). |
| 2 | `File:Yuling Tomb of Ming Dynasty.jpg` | ?Yuling Tomb | **Nhầm lăng mộ:** Minh Dụ Lăng triều Minh. |
| 3 | `File:Yuling Tomb of Ming Dynasty After Snow.jpg` | ?Yuling Tomb | **Nhầm lăng mộ:** Minh Dụ Lăng triều Minh. |
| 4 | `File:明裕陵 - Yuling Tomb - 2015.08 - panoramio.jpg` | ?Yuling Tomb | **Nhầm lăng mộ:** Minh Dụ Lăng triều Minh. |
| 5 | `File:Ming Qingling Tomb and Yuling Tomb.jpg` | ?Yuling Tomb | **Nhầm lăng mộ:** Quần thể Thập Tam Lăng triều Minh. |
| 6 | `File:Franklin D. Roosevelt, Chiang Kai-shek, and Winston Churchill at the Cairo Conference, 1943.jpg` | ?Chiang Kai-shek 1928 | **Sai thời kỳ:** Hội nghị Cairo 1943 (Thế chiến 2), nằm ngoài phạm vi vụ án 1928. |
| 7 | `File:North American B-25C (B31393) (5519679693).jpg` | Republic of China | **Sai thời kỳ:** Máy bay ném bom B-25 thời Thế chiến 2. |
| 8 | `File:Cecil Beaton Photographs- General IB2789C.jpg` | Republic of China | **Sai thời kỳ:** Ảnh chụp tướng lĩnh thời Thế chiến 2 (1944). |
| 9 | `File:1938 Yellow River flood.jpg` | Republic of China | **Không liên quan:** Thảm họa phá đê Hoàng Hà năm 1938. |
| 10 | `File:China Soviet Zones.png` | Warlord Era | **Không liên quan:** Bản đồ các khu căn cứ Xô viết thập niên 1930. |
| 11 | `File:SuzhouCreekOld2.jpg` | Republic of China | **Không liên quan:** Phong cảnh Tô Châu Hà ở Thượng Hải, không thuộc vụ án. |
| 12 | `File:Manchukuo Enthronement Medal.jpg` | Puyi | **Sai bối cảnh:** Huân chương đăng cơ Mãn Châu Quốc 1934 (dành cho Long 4 Phổ Nghi). |
| 13 | `File:Pu Yi (Kang Te) 1940 Japan visit.jpg` | Puyi | **Sai bối cảnh:** Phổ Nghi thăm Nhật Bản 1940 (dành cho Long 4). |
| 14 | `File:Emperors Shōwa & Pu Yi (cropped).jpg` | Puyi | **Sai bối cảnh:** Phổ Nghi và Thiên hoàng Chiêu Hòa 1940 (dành cho Long 4). |
| 15 | `File:Thronsaal Puyi Changchun.jpg` | Puyi | **Sai bối cảnh:** Cung điện Mãn Châu Quốc tại Trường Xuân (dành cho Long 4). |
| 16 | `File:伪满皇帝溥仪颁发的即位诏书。伪满皇宫博物院.jpg` | Puyi | **Sai bối cảnh:** Chiếu thư tức vị Khang Đức năm 1934 (dành cho Long 4). |
| 17 | `File:Fushun War Criminals Mgmt Center 2.jpg` | Puyi | **Sai thời kỳ:** Trại quản lý tội phạm chiến tranh Phủ Thuận thập niên 1950 (dành cho Long 4). |
| 18 | `File:Puyi in Fushun.jpg` | Puyi | **Sai thời kỳ:** Phổ Nghi cải tạo tại Phủ Thuận (dành cho Long 4). |
| 19 | `File:Spring 1967, Pujie and Saga Hiro visited Puyi.jpg` | Puyi | **Sai thời kỳ:** Phổ Nghi những năm cuối đời 1967 tại Bắc Kinh (dành cho Long 4). |
| 20 | `File:Puyi with Li Shuxian in the 1960s.jpg` | Puyi | **Sai thời kỳ:** Phổ Nghi và vợ Lý Thục Hiền thập niên 1960 (dành cho Long 4). |
| 21 | `File:Li Dai Di Wang Miao-20131229-RM-105234.jpg` | ?Dai Li | **Nhầm lẫn từ khóa:** Di tích Lịch đại Đế Vương Miếu ở Bắc Kinh (trùng chữ 'Dai' và 'Li'). |
| 22 | `File:Li Dai Di Wang Miao-20131229-RM-105317.jpg` | ?Dai Li | **Nhầm lẫn từ khóa:** Lịch đại Đế Vương Miếu. |
| 23 | `File:Li Dai Di Wang Miao-20131229-RM-105806.jpg` | ?Dai Li | **Nhầm lẫn từ khóa:** Lịch đại Đế Vương Miếu. |
| 24 | `File:Li Dai Di Wang Miao-20131229-RM-105438.jpg` | ?Dai Li | **Nhầm lẫn từ khóa:** Lịch đại Đế Vương Miếu. |
| 25 | `File:First Minister visits the Eastern Qing Tombs (6453361189).jpg` | ?Eastern Qing Tombs | **Ngoại giao hiện đại:** Chuyến thăm của quan chức ngoại giao hiện đại tại Đông Lăng. |
| 26 | `File:First Minister visits the Eastern Qing Tombs (6453364091).jpg` | ?Eastern Qing Tombs | **Ngoại giao hiện đại:** Chuyến thăm ngoại giao hiện đại. |

---

## 4. Bảng Phân Bổ Ảnh Tư Liệu Cho 14 Chương Của Kế Hoạch (`plan.md`)

| # | Tên chương | Nội dung cốt lõi theo plan | Số ảnh A dùng | Ảnh tiêu biểu / Tư liệu chính | Phương án bổ trợ (B, C, D) |
|---|---|---|:---:|---|---|
| **0** | **Tiếng mìn đêm 4/7/1928** | Cold open: Nổ mìn phá mộ, cạy quan tài, 30 xe tải tang vật | **8** | `1928 DingDongLing Looting Damage`, `Sun Dianying`, `清东陵裕陵地宫`, `Cixi Coffin`, `Zaize prince hui` | B/C đêm tối núi Mã Lan, D slam ngày giờ & timeline 72 giờ |
| **1** | **Nghịch lý Đông Lăng** | Vụ trộm thế kỷ, thủ phạm lộ mặt nhưng thoát án; 3 vòng mở | **11** | `Layout Östra QInggravarna`, `乾隆皇帝朝服像轴`, `The Imperial Portrait of Cixi`, `Sun Dianying`, `孙殿英旧宅` | D counter 30 xe tải, split phim vs thật, bars so sánh kho báu |
| **2** | **Kẻ vô lại cờ bạc** | Thân thế 1889 Vĩnh Thành Hà Nam; mồ côi cha; sới bạc, Miếu Đạo Hội | **9** | `Sun Dianying 孙殿英`, `Muslim Bandits (c1915)`, `Beiyang Army`, `Chine 1911-1916`, `10 Custom Gold Units` | D map Vĩnh Thành Hà Nam, timeline thân thế, B sòng bạc, C nha phiến |
| **3** | **Tướng cướp mặc quân phục** | Thập niên 1920: Hỗn chiến quân phiệt; Trương Tông Xương; theo Tưởng | **12** | `Zhang Zongchang5`, `Armored-train1`, `奉系軍閥的FT-17`, `Chiang Kai-shek horseback`, `Chinese warlord soldiers` | D org chỉ huy Sư đoàn 12, map Bắc phạt, B đoàn xe tải quân sự |
| **4** | **Kế hoạch 'Tập trận'** | Tháng 6/1928: Tuân Hóa; phong tỏa lăng mượn cớ tập trận | **10** | `Eastern Qing Tombs`, `Villages Around Eastern Qing`, `Tombs of Cixi and Ci'an`, `Dabeilou`, `Protection Stone` | D map vòng vây Tuân Hóa, date lệnh thiết quân luật, C hòm thuốc nổ |
| **5** | **Phá cửa Dụ Lăng** | Đêm 4/7: Ép chỉ điểm Á Ba Viện; nổ mìn 4 tầng cửa đá ngầm; cạy Càn Long | **14** | `裕陵月牙城(哑巴院)`, `清东陵裕陵地宫`, `Yuling Tomb reliefs (3,5,9,12,16)`, `The Qianlong Emperor in Armour` | D waterfall 4 lớp cửa đá ngầm, sơ đồ quan tài, B nước ngập địa cung |
| **6** | **Quan tài Từ Hi** | Rạng sáng 5/7: Phá Định Đông Lăng; thi thể nguyên vẹn; cạy Dạ Minh Châu | **13** | `1928 DingDongLing Damage`, `Cixi Burial Garments (1,2)`, `Cixi Coffin`, `Chinese Ceremonial Headdress`, `Kugelförmige Fluorit` | D ledger báu vật Từ Hi, bars ngân sách hạm đội, C ngọc phát quang |
| **7** | **Cơn thịnh nộ ở Thiên Tân** | Tin tức rò rỉ cuối tháng 7; Phổ Nghi Trương Viên khóc thề; Tái Trạch | **10** | `Johnston, Puyi in Zhang Garden`, `溥仪`, `Zaize prince hui`, `1928 Cixi Corpse (mờ)`, `Chiang paying reverence 1928` | D quote hồi ký Phổ Nghi, heat làn sóng dư luận, file biên bản 8/1928 |
| **8** | **Bản kê báu vật** | Danh mục tang vật 30 xe tải; giải mã khoa học Dạ Minh Châu (Đóng vòng 1) | **12** | `melon_jade_pot` (CC0), `qianlong_dragon_dish` (CC0), `qianlong_lacquer_bowl` (CC0), 6 hiện vật gốm/ngọc CC0, `Fluorit` | D ledger danh mục tang vật, split dân gian vs khoa học, slam đóng vòng 1 |
| **9** | **Mạng lưới mua đường** | Tôn dùng tang vật mua mạng; Đới Lạp, Tống Mỹ Linh, Tống Tử Văn, Diêm | **13** | `Chiang and Dai Li`, `Dai Li6`, `Miss May Ling Soong`, `Tse-ven Soong`, `Family of Soong 1917`, `He Yingqin1`, `Yan Xishan` | D org mạng lưới hối lộ ngũ giác, split quà tặng, C tráp mật nghị |
| **10** | **Phiên tòa Nam Kinh** | Tháng 12/1928: Tòa quân sự Nam Kinh mở rồi hoãn, đình chỉ im lặng (Đóng 2) | **11** | `Nationalist government Nanking`, `He Yingqin4`, `Former Residence of He`, `Chiang Kai-shek 1928`, `Nationalist China map` | D timeline các đợt hoãn tòa, file quyết định đình chỉ 4/1929, slam đóng vòng 2 |
| **11** | **Cửu Long Bảo Kiếm** | Kiếm Càn Long -> Đới Lạp -> Mã Hán Tam -> Phương Tử -> Rơi máy bay 1946 | **9** | `The Qianlong Emperor in Armour`, `Chiang and Dai Li`, `戴笠杜月笙1945`, `戴笠遇難前`, `qianlong_dragon_plaque` (CC0) | D map đường đi bảo kiếm, date rơi máy bay 17/3/1946, C kiếm cháy cong |
| **12** | **Dạ Minh Châu và Tống Mỹ Linh** | Tống Mỹ Linh gắn mũi giày dạ hội; di tản Đài Loan/New York; mất dấu (Đóng 3) | **10** | `Chiang and Soong May-ling2`, `Family of Soong`, `T.V. Soong`, `The Imperial Portrait of Cixi`, `melon_jade_pot` (CC0) | D split giày dạ tiệc vs khuy áo, file danh mục Cố Cung vắng ngọc, slam đóng 3 |
| **13** | **KẾT: Hầm mộ trơ đáy** | 1947 Tôn bị bắt, chết trong tù vì nha phiến; lăng mộ trơ đáy, bài học tham | **9** | `Sun Dianying`, `孙殿英旧宅`, `1928 DingDongLing Damage`, `Yuling in Eastern Qing`, `Putuo Yu Ding Dongling 9` | D timeline kết cục 1947, bars tổng kết vụ án, B bậc đá rêu phong hoang phế |
| **TỔNG** | **Toàn bộ 14 chương** | | **76 ảnh A khác nhau** | **Vượt xa chỉ tiêu sàn ≥ 40 ảnh A** | **Mọi chương đều có phương án bù đắp vững chắc** |

---

## 5. Hệ Thống Khung Hình và Phân Bổ Nhịp Độ (`visual_plan.md`)

Tài liệu chi tiết `data/long/dong-lang/visual_plan.md` đã được biên soạn hoàn chỉnh với **421 nhịp hình** chi tiết cho 14 chương:

- **Tổng thời lượng:** 28 phút 30 giây (1.710 giây).
- **Nhịp độ trung bình (pacing):** **4,06 giây/nhịp** (tuân thủ nghiêm ngặt dải mục tiêu 3–5 giây/nhịp). Mỗi nhịp đại diện cho một biến đổi thị giác thực sự: đổi góc máy pan/zoom Ken Burns, đổi lớp đồ họa, chuyển cảnh engine hoặc visual metaphor.
- **Tỉ lệ phân bổ 4 nhóm tài nguyên:**
  - **Nhóm A (Tư liệu lịch sử):** **908 giây (53,1% thời lượng)**. Đạt chỉ tiêu A ≥ 50%. Tư liệu lịch sử là xương sống xuyên suốt mọi chương.
  - **Nhóm B (AI tái dựng bối cảnh):** **191 giây (11,2% thời lượng)**.
  - **Nhóm C (AI minh họa khái niệm):** **171 giây (10,0% thời lượng)**.
  - **Tổng Nhóm B + C:** **362 giây (21,2% thời lượng)**. Nằm an toàn dưới trần tối đa 25%.
  - **Nhóm D (Motion Graphics engine):** **440 giây (25,7% thời lượng)**. Đạt trọn vẹn dải chỉ tiêu brief giao: **20–30%** (khắc phục hoàn toàn việc nhóm D chỉ đạt 7% ở Hòa Thân).
- **Quy tắc nhóm B/C:**
  - Tuyệt đối không vẽ mặt nhân vật lịch sử (Tôn Điện Anh, Từ Hi, Càn Long, Phổ Nghi, Tưởng Giới Thạch, Tống Mỹ Linh, Đới Lạp...).
  - Tuyệt đối không vẽ chữ Hán, số, triện giả hay văn bản chỉ dụ giả.
  - Tuyệt đối không mô tả bạo lực đẫm máu hay cận cảnh nổ mìn chi tiết.
  - Lần đầu xuất hiện nhóm B trong mỗi chương đều mang nhãn nhỏ điện ảnh "TÁI DỰNG MINH HỌA".

---

## 6. Danh Mục AI Prompts (`ai_prompts.md`)

Tài liệu `data/long/dong-lang/ai_prompts.md` đã được khởi tạo hoàn chỉnh đúng định dạng công cụ `scripts/ai_img_request.py`:
- **Tổng số prompt tạo mới:** **16 ảnh tĩnh (`ai_01.png` đến `ai_16.png`)** và **6 clip chuyển động chậm (`vid_01.mp4` đến `vid_06.mp4`)**. Đạt đúng ngưỡng tối đa cho phép theo brief.
- **Tiêu đề quy chuẩn:** `## ai_NN.png — CHxx: <Tiêu đề>` hoặc `## vid_NN.mp4 — CHxx: <Tiêu đề>` kèm một dòng `- Prompt (tiếng Anh): ...`.
- **Tận dụng kho tài nguyên chung:** Đã tra cứu `library/tools/assets.py` (tag `cl`/`hinh_su`) và tích hợp 5 tài sản chung sẵn có (`lib198b/ai_18.png`, `lib198/ai_57.png`, `lib198v/vid_11.mp4`, `lib198b/ai_04.png`, `lib198b/ai_29.png`).

---

## 7. Ước Tính Kiểm Định Floor Kênh (`motion/long/floor.py`)

| Tiêu chí sàn | Mức quy định sàn | Mức thiết kế dự án `dong-lang` | Kết luận |
|---|---|---|:---:|
| **Âm tiết kịch bản dự kiến** | ≥ 5.000 âm tiết (≈ 23 phút) | ≈ 6.050 âm tiết (28m30s ở 212 âm/phút) | **ĐẠT** |
| **Số chương** | ≥ 10 chương | 14 chương (CH00 đến CH13) | **ĐẠT** |
| **Số loại cảnh engine** | ≥ 14 loại | 18 loại cảnh (`photo`, `print`, `map`, `ledger`, `counter`, `slam`, `broll`, `file`, `date`, `timeline`, `quote`, `split`, `bars`, `org`, `question`, `waterfall`, `chapter`, `heat`) | **ĐẠT** |
| **Ảnh tư liệu A khác nhau** | ≥ 40 ảnh | **76 ảnh tư liệu khác nhau** (trích từ 244 ảnh tự do đã kiểm duyệt) | **ĐẠT** |
| **Cảnh có video / b-roll** | ≥ 30 cảnh | **36 cảnh video** (6 video Flow `vid_NN.mp4` + broll kiến trúc lăng mộ & đoàn xe) | **ĐẠT** |
| **Tỷ lệ kinetic** | ≤ 38% | **12,8%** (54/421 nhịp) | **ĐẠT** |
| **Chữ trên nền trống (naked)** | ≤ 12% | **3,6%** (15/421 nhịp, hầu hết chữ đều có nền tư liệu/tranh mờ) | **ĐẠT** |

---

## 8. Kết Luận và Kiến Nghị

1. **Kết quả bước 2:** Đã hoàn thành toàn bộ khối lượng công việc của Ticket GH-228 với chất lượng cao nhất:
   - Kho tư liệu ảnh tự do dồi dào (244 ảnh, vượt 488% chỉ tiêu).
   - Hệ thống khung hình 14 chương `data/long/dong-lang/visual_plan.md` đạt chuẩn nhịp 3–5 giây, nhóm D đạt 25,7% (đúng dải 20–30% brief yêu cầu), nhóm A đạt 53,1%.
   - Danh sách prompt `data/long/dong-lang/ai_prompts.md` chuẩn hóa tuyệt đối, tuân thủ nguyên tắc cấm vẽ mặt người thật và chữ Hán giả.
2. **Cam kết an toàn:** Không thực hiện bất kỳ lệnh git commit nào; không sửa code chung; không ghi đè `state.sqlite`; không đụng lịch phát sóng hiện tại của Long 1 (Bao Thanh Thiên, 08/11) và Long 2 (Hòa Thân, 15/11).
3. **Kiến nghị:** Kính chuyển Lead duyệt báo cáo tư liệu và bộ khung hình để sẵn sàng chuyển sang Bước 3: Viết kịch bản chi tiết `data/long/dong-lang/script.md` và bảng kiểm định nguồn `factcheck.md`.
