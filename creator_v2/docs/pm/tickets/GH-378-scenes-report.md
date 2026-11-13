# GH-378: báo cáo bước 4 (cảnh) Long CL "Hoàng Kim Vinh Ngoài Đời Thật" (13/11/2026)

Người làm: Claude (Sonnet). Chưa TTS, chưa render, chưa commit, chưa chạm YouTube. File ghi: `data/long/cl-hoang-kim-vinh/{gen_scenes.py, gen_scenes2.py, spec_hkv.py, ch00..ch13.json, spec.json}`, `output/long/cl-hoang-kim-vinh/broll/` (7 clip chung chép từ Lưu Gù) và file này.

## 1. Số liệu

- **313 cảnh**, 14 chương, 15 loại cảnh, 5.751 âm tiết (27,4 phút ước), ước 5,2 giây/cảnh (long_gate).
- Cảnh `file`/thẻ: **14/313 = 4.5%** (trần 12%), mọi cặp cách nhau ≥ 5 cảnh (floor/idcards kiểm qua).
- Cảnh có b-roll: **35** (sàn 30), 7 clip khác nhau, mỗi clip 5–5 lần (trần long_gate 5).
- Ảnh khai trong spec: **42** (sàn 40); 22 ảnh dùng làm `img` (mỗi ảnh ≤ 3 lần), 33 ảnh làm nền `bg` cho thẻ chữ.
- Kinetic 31% (trần 38%); chữ trên nền trống 0% (mọi thẻ chữ đều có ảnh/clip nền); cảnh `auto` 0.

| Chương | Cảnh | Loại | Clip | Thẻ file |
|---|---:|---:|---:|---:|
| CH00 Hai Tờ Báo, 20/5/1951 | 10 | 6 | 3 | 0 |
| CH01 Bốn Mốc, Bốn Cách Kể | 14 | 8 | 1 | 1 |
| CH02 Đứa Trẻ Tô Châu | 25 | 13 | 3 | 1 |
| CH03 Chiếc Ghế Của Người Thám Tử | 22 | 10 | 3 | 1 |
| CH04 Một Trang Sách Năm 1930 | 25 | 11 | 3 | 1 |
| CH05 Thứ Hàng Nằm Trong Kho | 14 | 8 | 3 | 1 |
| CH06 Tam Hâm Và Cậu Học Trò | 21 | 10 | 3 | 1 |
| CH07 Người Đào Hát Và Đêm Bị Bắt | 27 | 9 | 3 | 2 |
| CH08 Khu Vườn Ở Tào Hà Kính | 24 | 8 | 3 | 1 |
| CH09 Mùa Xuân 1927 | 32 | 11 | 2 | 1 |
| CH10 Đại Thế Giới | 31 | 11 | 2 | 2 |
| CH11 Người Ở Lại | 26 | 11 | 2 | 0 |
| CH12 Bản Tự Thú | 25 | 7 | 2 | 1 |
| CH13 Ba Tờ Giấy, Một Người | 17 | 8 | 2 | 1 |

Loại cảnh: kinetic 99, date 52, slam 28, ledger 24, photo 22, quote 16, file 14, question 13, org 12, counter 10, timeline 8, myth 6, print 5, map 3, split 1.

## 2. Trục "bốn mốc, bốn cách kể"

- Thẻ mốc `date` cùng khuôn "MỐC n/4 · <cách kể>": MỐC 1/4 · ĐÊM BỊ BẮT (1924, CH01 và CH07), MỐC 2/4 · TRANG SÁCH (1930, CH01 và CH04), MỐC 3/4 · ĐẠI THẾ GIỚI (1931, CH01 và CH10), MỐC 4/4 · BẢN TỰ THÚ (1951, CH01, CH12, CH13).
- "Ba cách kể" dạng cột (`org`): cha (CH02), hai bản kể song song (CH03), ba cách rời ghế (CH08: Wikipedia en 1924, bách khoa zh 1925, sách 1930), ba mục sách 1930 về cùng một mùa xuân (CH09), hai bản bách khoa về Tam Hâm (CH06).
- Dòng thời gian (CH02, CH04, CH05, CH09, CH11, CH13), bản đồ giang nam và tô giới (map `jn`, `dn` ở CH01, CH02, CH11; bản đồ 1896 và 1932 làm `print`/`photo`), thẻ trích dẫn `quote` cho **cả 15 câu [TRÍCH DỊCH]** (16 thẻ vì một câu ở CH09 tách làm hai), nguồn ghi trên thẻ; GIAI THOẠI ở CH03 có nhãn `illus` "GIAI THOẠI · BÀI BÁO KHÔNG DẪN NGUỒN" và thẻ `myth` gạch bỏ.

## 3. Cổng đã chạy

- `python data/long/cl-hoang-kim-vinh/gen_scenes.py`: sạch (kiểm mốc neo: mọi `[dòng, từ]` có thật trong câu, mốc cảnh tăng dần; ảnh `img` ≤ 3; ghi công đủ).
- `python scripts/check_scene_durations.py cl-hoang-kim-vinh --out <thư mục timing giả>`: **TỔNG LỖI: 0** ở tốc độ đọc 3,7 / 4,1 / 4,4 từ/giây (Lưu Gù đo thật 3,95–4,3). Chưa có TTS nên dùng `timing.json` giả tính theo số từ + ngắt `p` (không đủ thay cho thời lượng thật: sau TTS phải chạy lại). Ở 3,4 từ/giây có 15 cảnh quá 9 giây và ở 5,0 từ/giây có 6 cảnh dưới 2,5 giây: nằm ngoài khoảng đo được của giọng này.
- `motion/long/opening_gate.py` (ước lượng): OK (5 giây đầu có clip; chữ trống 0 giây trong 40 giây đầu; không chào hỏi/lộ trình; từ khóa tiêu đề nói trước 15 giây).
- `motion/variety.py audit`: OK với `look: classic`. Lead lưu ý: sổ chỉ biết video đã ghi sổ; lịch tới là Lưu Gù (jade) 17/11, Đông Lang (sulfur) 22/11, Mata Hari (steel) 29/11, Hòa Thân (amber): chọn `classic` để khác cả bốn.
- `scripts/long_gate.py`: chỉ còn lỗi "chưa TTS" (không phụ thuộc cảnh).
- `floor.report`: 15 loại, 42 ảnh, 35 cảnh b-roll, kinetic 31%, chữ trống 0%.

## 4. Ảnh: loại bỏ và lý do

Đã mở cả bốn sheet và lọc tay: bỏ toàn bộ 31 ảnh Tưởng Giới Thạch trừ 6 ảnh dùng cho CH09 (1916, 1926, Quảng Châu 1926, Hoàng Phố, Bắc phạt 1928, bản đồ Nam Kinh 1930), ảnh rác (chim, khủng long, sợi alginate, cây quất, bản vẽ hóa thạch), ảnh hiện đại của Bund/Phố Đông/Phúc Châu...; ảnh chặt đầu 1927 không dùng. Ảnh hiện đại chỉ còn 4 tấm, đều có nhãn "ẢNH NGÀY NAY" và chỉ dùng ở câu nói về hiện tại: kho hàng Hoàng Kim Vinh (CH05), Đại Thế Giới (CH10, CH13), mộ Đỗ Nguyệt Sanh (CH13). Không có ảnh thật cho cảnh nào thì dùng thẻ chữ/ledger/dòng thời gian; không tạo ảnh AI, không minh họa người thật.

## 5. Ảnh dùng, giấy phép, URL (ghi công đã nằm trong `spec.youtube.video_credits`)

| Khóa | Dùng `img` | Dùng `bg` | Tệp · tác giả · giấy phép · URL |
|---|---:|---:|---|
| `bund30` | 0 | 20 | 1930 Shanghai.jpg — US Signal Corps — Public domain — https://commons.wikimedia.org/wiki/File%3A1930_Shanghai.jpg |
| `bund90` | 1 | 5 | The Bund, Shanghai, c1890s.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3AThe_Bund%2C_Shanghai%2C_c1890s.jpg |
| `bundfc` | 2 | 11 | Shanghai Bund seen from the French Concession.jpg — Tác giả không rõ, c. 1934 — Public domain — https://commons.wikimedia.org/wiki/File%3AShanghai_Bund_seen_from_the_French_Concession.jpg |
| `cangku` | 1 | 0 | Huangjinrong Cangku.JPG — Fayhoo — CC BY-SA 3.0 — https://commons.wikimedia.org/wiki/File%3AHuangjinrong_Cangku.JPG |
| `canton26` | 0 | 4 | Chiang Kai-shek, Wang Jingwei, Borodin and others, Canton, January 1926 (Fu-n086).jpg — Fu Bingchang — Public domain — https://commons.wikimedia.org/wiki/File%3AChiang_Kai-shek%2C_Wang_Jingwei%2C_Borodin_and_others%2C_Canton%2C_January_1926_%28Fu-n086%29.jpg |
| `chiang16` | 1 | 0 | 民國五年三十歲的蔣介石.png — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3A%E6%B0%91%E5%9C%8B%E4%BA%94%E5%B9%B4%E4%B8%89%E5%8D%81%E6%AD%B2%E7%9A%84%E8%94%A3%E4%BB%8B%E7%9F%B3.png |
| `chiang26` | 0 | 4 | Chiang1926.jpg — Tác giả không rõ (International) — Public domain — https://commons.wikimedia.org/wiki/File%3AChiang1926.jpg |
| `council` | 1 | 18 | Tcitp d380 french municipal council offices in shanghai.jpg — Arnold Wright — Public domain — https://commons.wikimedia.org/wiki/File%3ATcitp_d380_french_municipal_council_offices_in_shanghai.jpg |
| `coupon` | 0 | 2 | Currency issued inside the settlement for use by the British Armed Forces inside the city - circa 1940.jpg — British Armed Forces — Public domain — https://commons.wikimedia.org/wiki/File%3ACurrency_issued_inside_the_settlement_for_use_by_the_British_Armed_Forces_inside_the_city_-_circa_1940.jpg |
| `fc37` | 1 | 6 | French Concession 1937.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3AFrench_Concession_1937.jpg |
| `greatworld` | 2 | 0 | The Great World (Shanghai).jpg — Legolas1024 — CC BY-SA 3.0 — https://commons.wikimedia.org/wiki/File%3AThe_Great_World_%28Shanghai%29.jpg |
| `huang` | 3 | 0 | 黄金荣肖像.jpg — Tác giả không rõ (Virtual Shanghai) — Public domain — https://commons.wikimedia.org/wiki/File%3A%E9%BB%84%E9%87%91%E8%8D%A3%E8%82%96%E5%83%8F.jpg |
| `izumo` | 0 | 4 | Japanese cruiser Izumo in Shanghai.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3AJapanese_cruiser_Izumo_in_Shanghai.jpg |
| `jinling` | 1 | 25 | East Jinling Rd. in 1930s.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3AEast_Jinling_Rd._in_1930s.jpg |
| `map1884` | 0 | 3 | Shanghai 1884.jpg — Xu Yucang, "Dian Shi Zhai" — Public domain — https://commons.wikimedia.org/wiki/File%3AShanghai_1884.jpg |
| `map1896` | 1 | 0 | The mystic flowery land; a personal narrative (1896) (14591881777).jpg — Internet Archive Book Images (Charles J. H. Halcombe, 1896) — No restrictions — https://commons.wikimedia.org/wiki/File%3AThe_mystic_flowery_land%3B_a_personal_narrative_%281896%29_%2814591881777%29.jpg |
| `map1933` | 0 | 2 | Shanghai 1933.jpg — U.S. Army Map Service — Public domain — https://commons.wikimedia.org/wiki/File%3AShanghai_1933.jpg |
| `map1935` | 1 | 3 | Shanghai 1935 S1 AMS-WO.jpg — United States Army Map Service — Public domain — https://commons.wikimedia.org/wiki/File%3AShanghai_1935_S1_AMS-WO.jpg |
| `map32` | 0 | 3 | Jichisan Shokai - Shanghai City Street Map - 上海市市街圖 (1932).jpg — Jichishan Shokai — Public domain — https://commons.wikimedia.org/wiki/File%3AJichisan_Shokai_-_Shanghai_City_Street_Map_-_%E4%B8%8A%E6%B5%B7%E5%B8%82%E5%B8%82%E8%A1%97%E5%9C%96_%281932%29.jpg |
| `marines` | 0 | 5 | American marines holding up a Japanese patrol in Shanghai, 1930s.png — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3AAmerican_marines_holding_up_a_Japanese_patrol_in_Shanghai%2C_1930s.png |
| `metropole` | 0 | 4 | Metropole Hotel under construction, Shanghai, 15 September 1930.jpg — Historical Photographs of China (Đại học Bristol) — Public domain — https://commons.wikimedia.org/wiki/File%3AMetropole_Hotel_under_construction%2C_Shanghai%2C_15_September_1930.jpg |
| `nanjingmap` | 1 | 0 | Nationalist government of Nanking - nominally ruling over entire China, 1930 (2675972715).jpg — Japanese Embassy; tải lên bởi tm — CC BY 2.0 — https://commons.wikimedia.org/wiki/File%3ANationalist_government_of_Nanking_-_nominally_ruling_over_entire_China%2C_1930_%282675972715%29.jpg |
| `nanking1` | 1 | 17 | Shanghai Nanking Road 1930s.jpeg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3AShanghai_Nanking_Road_1930s.jpeg |
| `nanking2` | 1 | 17 | Nanking Road, Shanghai, c. 1930s.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3ANanking_Road%2C_Shanghai%2C_c._1930s.jpg |
| `nanking3` | 0 | 23 | Nanking Road, Shanghai, circa 1930s.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3ANanking_Road%2C_Shanghai%2C_circa_1930s.jpg |
| `nra` | 0 | 6 | NRA Generals Northern Expedition1.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3ANRA_Generals_Northern_Expedition1.jpg |
| `opium1` | 1 | 1 | Chinese opium smokers.jpg — Thomas Allom (vẽ), G. Paterson (khắc) — Public domain — https://commons.wikimedia.org/wiki/File%3AChinese_opium_smokers.jpg |
| `opium2` | 0 | 2 | China opium den.tif — Anonyme, Société de Saint-Augustin, 1896 — Public domain — https://commons.wikimedia.org/wiki/File%3AChina_opium_den.tif |
| `opium3` | 1 | 4 | China, Opium smokers by Lai Afong, c1880.JPG — Lai Afong — Public domain — https://commons.wikimedia.org/wiki/File%3AChina%2C_Opium_smokers_by_Lai_Afong%2C_c1880.JPG |
| `opium4` | 0 | 2 | Opium Smokers - Beijing 1932.jpg — Tác giả không rõ — CC0 — https://commons.wikimedia.org/wiki/File%3AOpium_Smokers_-_Beijing_1932.jpg |
| `opiummap` | 1 | 1 | "Map showing where opium is grown in China" in 1908, from book - Present-Day Conditions in China; Notes Designed to Show the Moral and Spiritual Claims of the Chinese Empire, published 1908 (IA presentdaycondit00broo) (page 25 crop).jpg — Marshall Broomhall (China Inland Mission), 1908 — Public domain — https://commons.wikimedia.org/wiki/File%3A%22Map_showing_where_opium_is_grown_in_China%22_in_1908%2C_from_book_-_Present-Day_Conditions_in_China%3B_Notes_Designed_to_Show_the_Moral_and_Spiritual_Claims_of_the_Chinese_Empire%2C_published_1908_%28IA_presentdaycondit00broo%29_%28page_25_crop%29.jpg |
| `patna` | 0 | 1 | A busy stacking room in the opium factory at Patna, India. L Wellcome V0019154.jpg — W. S. Sherwill (Wellcome Collection) — Public domain — https://commons.wikimedia.org/wiki/File%3AA_busy_stacking_room_in_the_opium_factory_at_Patna%2C_India._L_Wellcome_V0019154.jpg |
| `pearl` | 0 | 1 | Pearl Harbor Attack, 7 December 1941 (24374354935).jpg — National Museum of the U.S. Navy — Public domain — https://commons.wikimedia.org/wiki/File%3APearl_Harbor_Attack%2C_7_December_1941_%2824374354935%29.jpg |
| `police_anam` | 1 | 10 | Tcitp d385 french settlement police of anamites.jpg — Arnold Wright — Public domain — https://commons.wikimedia.org/wiki/File%3ATcitp_d385_french_settlement_police_of_anamites.jpg |
| `police_ic` | 0 | 12 | Tcitp d385 native chinese police of the international settlement.jpg — Arnold Wright — Public domain — https://commons.wikimedia.org/wiki/File%3ATcitp_d385_native_chinese_police_of_the_international_settlement.jpg |
| `rueconsul` | 1 | 21 | Rue de Consulate, Shanghai.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3ARue_de_Consulate%2C_Shanghai.jpg |
| `sikh` | 0 | 8 | Shanghai Sikh 1935.jpg — Ảnh bưu thiếp c. 1935 — Public domain — https://commons.wikimedia.org/wiki/File%3AShanghai_Sikh_1935.jpg |
| `stamp` | 0 | 1 | Stamp Shanghai 1893 1c.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3AStamp_Shanghai_1893_1c.jpg |
| `tomb` | 1 | 0 | Tomb of Du Yuesheng.jpg — M940504 — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File%3ATomb_of_Du_Yuesheng.jpg |
| `whampoa` | 0 | 1 | Whampoa3.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3AWhampoa3.jpg |
| `zhang1` | 1 | 0 | Zhang Siaolin.jpg — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3AZhang_Siaolin.jpg |
| `zhang2` | 2 | 0 | 民國·張嘯林.png — Tác giả không rõ — Public domain — https://commons.wikimedia.org/wiki/File%3A%E6%B0%91%E5%9C%8B%C2%B7%E5%BC%B5%E5%98%AF%E6%9E%97.png |

Cần ghi công (CC): Huangjinrong Cangku (Fayhoo, CC BY-SA 3.0), The Great World (Legolas1024, CC BY-SA 3.0), Tomb of Du Yuesheng (M940504, CC BY-SA 4.0), bản đồ Nanking 1930 (CC BY 2.0). Ghi công cũng hiện trên khung qua dòng "ẢNH: …" của engine.

Clip: 7 clip AI chung (900001, 900002, 900004–900008) chép từ `output/long/cl-luu-gu/broll/` kèm sidecar (`ai_generated`, `tags: minh_hoa_chung`), nhãn "MINH HỌA CHUNG" trên khung, không phải tư liệu.

## 6. Lỗi còn lại và việc cần Lead quyết

1. **Clip chung là cảnh phòng/đền kiểu Trung Hoa chung chung** (lồng đèn, thư phòng, mực, thỏi bạc, thuyền sương, giấy, cửa tối), chép từ Lưu Gù. Hợp với "tờ giấy", "cánh cửa", Tô Châu, tiền; không phải Thượng Hải thập niên 1920. Nếu muốn sát hơn, nhờ bot tạo 7 clip mới (Thượng Hải mưa đêm, sảnh nhà hát, phố tô giới, bàn giấy cảnh sát, bến sông...) rồi đổi `CLIPS` trong gen_scenes.py. Sàn 30 cảnh b-roll buộc ít nhất 6 clip mỗi clip ≤ 5 lần.
2. **Chưa có TTS**: thời lượng thật phải đo lại bằng `check_scene_durations.py` ngay sau `build_long.py tts` (không cần `--out`). Câu ngắn (≤ 8 từ) đã gộp vào cảnh kế để chịu được tốc độ 3,4–5 từ/giây, nhưng vài cảnh lệch 0,1–0,3 giây khỏi ngưỡng có thể xuất hiện.
3. **Thẻ `file`** nay do `idcards.assign` chọn kiểu khi build (spec mới nên `idcards` bật); chưa soi khung hình. Cần mở contact sheet sau `html`.
4. **Tên video** đặt tạm "HOÀNG KIM VINH Ngoài Đời Thật: Ba Trang Giấy, Một Người" (55 ký tự); lịch `publish_at` tạm 26/11/2026 21:00 VN (Thứ Năm). Chưa có thumbnail `t1.jpg`. Lead đổi nếu cần. Không đặt `approved`.
5. **`say`** (bảng phiên âm) mới có 12 mục (Wikipedia, TVB, Wakeman, Frederic, Josef, Sternberg, Jules, Bigot, Vichy, Edward, von, le): nghe thử sau TTS và chỉnh.
6. Ảnh nhân vật rất ít: Hoàng chỉ có một chân dung (dùng 3 lần, tối đa của cổng), Trương hai ảnh, Đỗ không có ảnh sống nên chỉ hiện bằng thẻ chữ và mộ (ảnh ngày nay).
