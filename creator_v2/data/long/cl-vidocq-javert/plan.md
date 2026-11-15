<!-- plan-sources:start -->
## Kiểm nguồn tự động (2026-11-15)

> Kết quả hỗ trợ rà soát, không chứng minh nội dung đúng; CHAN và KHONG_MO_DUOC chưa được xác minh.

| URL | Trạng thái | Số file Commons (gồm một cấp con) | Chi tiết |
|---|---|---:|---|
| https://en.wikipedia.org/wiki/Eug%C3%A8ne_Fran%C3%A7ois_Vidocq | OK | — |  |
| https://fr.wikipedia.org/wiki/Eug%C3%A8ne-Fran%C3%A7ois_Vidocq | OK | — |  |
| https://en.wikipedia.org/wiki/Javert | OK | — |  |
| https://en.wikisource.org/wiki/Memoirs_of_Vidocq | OK | — |  |
<!-- plan-sources:end -->

<!-- plan-sources:start -->
## Kiểm nguồn tự động (2026-11-15)

> Kết quả hỗ trợ rà soát, không chứng minh nội dung đúng; CHAN và KHONG_MO_DUOC chưa được xác minh.

| URL | Trạng thái | Số file Commons (gồm một cấp con) | Chi tiết |
|---|---|---:|---|
| https://en.wikipedia.org/wiki/Eug%C3%A8ne_Fran%C3%A7ois_Vidocq | OK | — |  |
| https://fr.wikipedia.org/wiki/Eug%C3%A8ne-Fran%C3%A7ois_Vidocq | OK | — |  |
| https://en.wikipedia.org/wiki/Javert | OK | — |  |
| https://en.wikisource.org/wiki/Memoirs_of_Vidocq | OK | — |  |
<!-- plan-sources:end -->

# Kế hoạch Long CL: JAVERT Ngoài Đời Thật, Vidocq: tù khổ sai làm sếp cảnh sát Pháp

Kế hoạch gửi chủ kênh duyệt (15/11/2026, Claude Sonnet viết, nguồn đã mở ghi ở mục 6). Chưa viết kịch bản, chưa TTS, chưa render. Độ dài đích 12–18 phút. Dùng nếu chuỗi "Ngoài Đời Thật" (Lưu Gù 17/11, Hoàng Kim Vinh 19/11, Địch Nhân Kiệt 24/11) đạt sau 7 ngày; không phụ thuộc kết quả để duyệt đề tài.

## 1. Vì sao đề tài này, vì sao bây giờ

- **Người có thật đứng sau nhân vật quen thuộc:** Javert và Jean Valjean trong *Những người khốn khổ* là hai nhân vật khán giả Việt quen qua sách, phim, nhạc kịch. Trang Wikipedia "Javert" ghi Javert "loosely based on" Eugène François Vidocq, và ghi không hạn chế rằng Hugo cũng lấy cảm hứng từ cuộc đời Vidocq cho Valjean (theo lời giới thiệu bản hồi ký của Robin Walz). Nghịch lý chính của đề tài: **cả kẻ truy đuổi lẫn kẻ bị truy đuổi trong tiểu thuyết đều có mẫu từ một người.**
- **Khớp chất hồ sơ của CL:** hồ sơ tư pháp có thật (bản án 27/12/1796, sổ ghi nhà tù Bicêtre, đơn từ chức, sổ hôn thú, hồ sơ văn phòng thám tử bị tòa đóng). Commons giữ cả ảnh một số hồ sơ này. Giống mô-típ "cảnh sát kiêm tội phạm" của Hoàng Kim Vinh nhưng khác bối cảnh, khác thế kỷ và có hồ sơ kiểm chứng.
- **Khác các Long đã làm:** chưa có Long nào về Pháp hay lịch sử cảnh sát (đã đối chiếu `data/long/`: yakuza, mafia, shanghai, ripper, kowloon, golden, escobar, capone, bulger, mata-hari, hoa-than, dong-lang, bao-thanh-thien, cl-hoang-kim-vinh, cl-dich-nhan-kiet, cl-luu-gu). Khác Mata Hari (cùng nước Pháp) ở chỗ đây là câu chuyện về một thiết chế.
- **Khớp chỉ đạo chủ kênh 15/11:** tiêu đề và cold open bằng nghịch lý (tù khổ sai làm sếp cảnh sát), hình mạnh trong 40 giây đầu; thân bài kể theo cách hiện tại.
- **Sức hút tìm kiếm tiềm năng:** "Javert có thật" là câu hỏi người xem tự đặt sau khi xem phim hay nhạc kịch. Chưa có số đo cho kênh này; ghi là giả thuyết cần Test & Compare, không phải kết quả.

## 2. Cold open (~40 giây)

Nhịp hình (cắt 3–5 giây, tông tối, không ảnh bạo lực thật, không chữ trần; Commons là nguồn chính, tất cả ảnh đều thuộc thế kỷ 19 hoặc trước đó):

| Giây | Hình | Lời / chữ |
|---|---|---|
| 0–5 | Ảnh mạnh nhất: `DIV CondamnationBagne.jpg` (ảnh hồ sơ bản án khổ sai, Commons), đẩy máy vào dòng tuyên án; cần soát mắt xem ảnh đọc được | "Douai, ngày 27 tháng 12 năm 1796. Tòa tuyên tám năm khổ sai cho một thanh niên làm giả giấy tờ." |
| 5–12 | Khắc gỗ "La cadène" / cảnh xích tù trong thư mục Bicêtre; slam chữ "KHỔ SAI 8 NĂM" | "Mười lăm năm sau, chính người đó đứng đầu đơn vị truy bắt tội phạm của Paris." (1796 đến 1811, theo trang fr ông đứng đầu brigade de sûreté từ 1811, chưa chính thức; kiểm khi viết) |
| 12–20 | Chân dung Achille Devéria và Cruikshank đẩy máy; đồ họa timeline 1796 / 1811 / 1813 | "Không phải vì ông đã hối cải. Mà vì cảnh sát cần một người biết rõ tù nhân nghĩ gì." (Đây là lời diễn giải, ghi vùng 2, cần câu bằng chứng ở Ch5) |
| 20–32 | Ảnh `Demission vidocq.jpg` (đơn từ chức) và trang hồi ký; quote lớn | "Ông đã chạy trốn khỏi bagne Toulon. Rồi ông nhận làm chỉ điểm để được thả, trong một màn dàn xếp trông như vượt ngục." |
| 32–40 | Câu hỏi nổi trên nền đen | "Và vì sao Victor Hugo lại lấy ông làm mẫu cho cả kẻ truy đuổi lẫn kẻ bị truy đuổi?" |

Câu hậu quả trước giây 8: "Một kẻ giả mạo giấy tờ làm sao thành người đứng đầu mật vụ?" Bằng chứng đối lập trước giây 15: bản án 8 năm khổ sai, đối với sắc lệnh 12/1813 giao ông đứng đầu lực lượng Sûreté. Không chào, không giới thiệu kênh, không đọc lộ trình trước giây 30. Thứ tự hình theo "cửa sổ sốc": ảnh tư liệu có chuyển động máy (không có clip thật thế kỷ 19), motion graphic; không AI mô phỏng người thật; đồ họa chung `minh_hoa_chung` chỉ cho cảnh phố Paris không rõ mặt.

## 3. Câu hỏi trung tâm và vòng lặp mở

**Câu hỏi trung tâm:** Vì sao Paris giao việc đứng đầu cảnh sát sûreté cho một cựu tù khổ sai, và cái giá của quyết định đó là gì?

- **Vòng 1 (thương lượng):** Làm sao một tù nhân vượt ngục thành chỉ điểm rồi chủ nhiệm đơn vị cảnh sát? Đóng ở Chương 5 và 6 (đề nghị 1809–1811, "vượt ngục" tháng 3/1811, sắc lệnh 12/1813).
- **Vòng 2 (lời buộc):** Ông có tự dựng tội phạm để bắt người, như các cựu tù tố cáo không? Đóng ở Chương 7 (tòa bác cáo buộc; cái nào là hồ sơ, cái nào là giai thoại).
- **Vòng 3 (người kể chuyện của chính mình):** Hồi ký 1828 do ai viết, và tin được bao nhiêu? Đóng ở Chương 8 (hồi ký có người viết thuê, theo trang Wikipedia fr).
- **Vòng 4 (Javert hay Valjean?):** Đóng ở Chương 11 (nguồn văn học, phân biệt cái có nguồn "loosely based" với cái người xem thường nghe).

## 4. Dàn ý 13 chương

- Ch0: Douai, 27/12/1796: bản án tám năm khổ sai (cold open).
- Ch1: Arras 1775: sinh ra trong đêm 23 rạng 24/7; ghi chú hồi ký ghi 23/7 còn trang fr nói rạng 24/7. Lính 1791, đào ngũ 1792–93.
- Ch2: Tội giả mạo: "faux en écritures publiques" và vụ xử ở Douai.
- Ch3: Chuỗi xích tù ở Bicêtre (sổ ghi 20/5/1797) và các bagne: Brest (13/1/1798), Toulon; trốn Toulon 6/3/1800.
- Ch4: Kẻ trốn chạy: án tử vắng mặt 1805; cửa sổ tháng 11/1805; hôn nhân đổ vỡ và ly hôn 1805.
- Ch5: Món hời: 1809–1811, đề nghị làm chỉ điểm; tháng 3/1811 "vượt ngục" dàn xếp; quan hệ với tổng trấn cảnh sát Pasquier.
- Ch6: Sûreté: đơn vị mật vụ toàn cựu tù; sắc lệnh 12/1813; ân xá (1817 theo en, 1818 theo fr, cần kiểm).
- Ch7: Hồ sơ và giai thoại: số vụ bắt do chính ông và thuộc hạ nêu (hơn 16.000 vụ theo ông tự nói); cáo buộc dựng tội phạm bị tòa bác; ca bắn "so đạn" trong sách Dumas chỉ là truyện.
- Ch8: 1827 và hồi ký 1828–29: từ chức sau nhiều khiếu nại về thuộc hạ; hồi ký có người viết thuê (L'Héritier de l'Ain, Émile Morice theo fr); các hồi ký đối thủ.
- Ch9: 1832: trở lại ngày 31/3, từ chức 15/11; Sûreté giải thể rồi lập lại không còn cựu tù.
- Ch10: Văn phòng thám tử đầu tiên (1833): "Bureau de renseignements" ở rue Cloche-Perce, rồi galerie Vivienne; tòa đóng 1837; ở Sainte-Pélagie; được tha. Ghi rõ chỗ hai trang không khớp (mục 6).
- Ch11: Văn học và hai người cùng một mẫu: Balzac (Vautrin), Hugo (Valjean và Javert, "Brutus in Vidocq"), Poe (Dupin, chưa chứng minh).
- Ch12: KẾT: mất 11/5/1857 tại Paris, mộ không rõ; câu hỏi cuối: nếu cùng một người là cả kẻ truy đuổi và kẻ bị truy đuổi, ranh giới thật nằm ở đâu?

## 5. Ba tiêu đề đề xuất (≤ 60 ký tự) và thumbnail

Lead chọn trước sản xuất, chủ kênh duyệt. Mỗi phương án ghi đối tượng, lời hứa, bằng chứng, số ký tự.

- `Javert Ngoài Đời Thật: Tù Khổ Sai Làm Sếp Cảnh Sát Pháp` (55 ký tự)
  Mẫu survival: nghịch lý. Đối tượng: người từng xem phim, nhạc kịch Những người khốn khổ. Lời hứa: ai là người thật sau Javert và vì sao một tù khổ sai đứng đầu cảnh sát. Bằng chứng: bản án 27/12/1796 (Wikipedia fr), sắc lệnh 12/1813 (Wikipedia en), "loosely based on" (trang Javert). Dùng chữ "làm sếp" nghĩa là đã đứng đầu Sûreté, có nguồn.
- `Án Khổ Sai 8 Năm, Rồi Đứng Đầu Cảnh Sát: Vidocq Là Ai?` (54 ký tự)
  Mẫu: bi kịch + nghịch lý. Đối tượng: người thích hồ sơ nhân vật lịch sử. Lời hứa: kể trọn con đường từ án tù đến Sûreté. Bằng chứng như trên; dấu hỏi dùng cho điều Long sẽ trả lời.
- `Vidocq: Mở Văn Phòng Thám Tử Xong, Bị Tống Giam Gần Một Năm` (59 ký tự)
  Mẫu: đồng hồ / tình thế (cái giá). Đối tượng: người xem hồ sơ; Lời hứa: kết cục sau khi mở văn phòng thám tử đầu tiên. Bằng chứng: trang fr ghi tòa đóng văn phòng 1837, ở Sainte-Pélagie rồi được tha sau khoảng một năm; trang en ghi 1837–38 bị buộc tội rồi bác bỏ, và 1842–43 bị kết án 5 năm rồi được thả khi kháng cáo. Hai trang không khớp: chưa dùng phương án này nếu chưa kiểm được nguồn mạnh hơn.

### Thumbnail

- Ý 1: mặt to: chân dung Vidocq (Achille Devéria hoặc ảnh G.12180 trong Commons) cắt sát, nửa mặt tối, nền đỏ sẫm xích; chữ `JAVERT CÓ THẬT` (3 chữ).
- Ý 2: ảnh bản án khổ sai (DIV CondamnationBagne) làm nền mờ, mặt Vidocq to chồng lên, chữ `TÙ → SẾP` (2 chữ).

## 6. Nguồn chính

Đã mở được nội dung trong phiên này (một số bài dài chỉ đọc 100.000 ký tự đầu):

- https://en.wikipedia.org/wiki/Eug%C3%A8ne_Fran%C3%A7ois_Vidocq
- https://fr.wikipedia.org/wiki/Eug%C3%A8ne-Fran%C3%A7ois_Vidocq
- https://en.wikipedia.org/wiki/Javert
- https://en.wikisource.org/wiki/Memoirs_of_Vidocq

**Không mở được:** Britannica (HTTP 403). **Chưa đọc:** văn bản gốc *Mémoires de Vidocq* (có trên Wikisource nhưng chưa đọc từng chương), *Les Misérables* bản gốc để kiểm câu "Brutus dans Vidocq", nghiên cứu học thuật (Robin Walz, Dominique Kalifa), tài liệu Archives nationales / Préfecture de police. **Kết luận: hiện chỉ có Wikipedia và trang giới thiệu hồi ký; chưa có sách sử hay bài báo học thuật đã mở.** Bước tư liệu phải mở ít nhất một nghiên cứu chuyên ngành trước khi viết lời.

Các điểm nguồn mâu thuẫn hoặc yếu, ghi vào `factcheck.md`:
- Ngày ân xá: 1817 (trang en) hay 1818 (trang fr, do Louis XVIII).
- Số năm sau 1832: trang en nói 1842 bị bắt, kết án 5 năm, được thả tháng 7/1843; trang fr không nhắc 1842, chỉ nêu 1837 đóng văn phòng và tù Sainte-Pélagie khoảng một năm. Không dùng 1842 trong tiêu đề hay cold open.
- Hồi ký 1828 là chuyện đã qua tay người viết thuê; chi tiết thời trẻ là tự thuật tự đề cao, không kiểm độc lập. Các số "hơn 16.000 vụ bắt", "hơn 8.000 khách hàng" là số ông tự nêu.
- Giai thoại không dùng như sự thật: cáo buộc ông dựng tội phạm (bị tòa bác theo fr, "không có sự thật" theo en), trí nhớ ảnh, ca so đạn (Dumas), ông phát minh mực không tẩy và khuôn dấu giày (en ghi một số bị tranh cãi).
- Ngày sinh: đêm 23 rạng 24/7/1775.

## 7. Ảnh tự do (đếm bằng API Commons, 15/11/2026)

- `Category:Eugène François Vidocq` (trực tiếp): **50 file**, gồm bản scan hồi ký (djvu, PDF/scan, bỏ khỏi đếm ảnh), chân dung Devéria, ảnh G.12180, nhiều tranh khắc của Cruikshank, sổ ghi án, sổ hôn thú, bản từ chức, tranh khắc chuỗi xích tù ở Bicêtre.
- Gồm cả thư mục con (`Landstreicherleben`): **424 file, trong đó 413 ảnh** jpg/png (không tính djvu, PDF).
- Bối cảnh: `Category:Bagne de Brest` 47 file trực tiếp (thêm thư mục con bản đồ, bưu thiếp, Pierre Coignard), `Category:Bagne de Toulon` 10 file (thêm một thư mục con). Truy vấn "bagne Toulon forçats" 99 kết quả, "Les Misérables Javert Valjean illustration" 79, "Cour d'assises Paris 19th century" 56, "Vidocq" 941.
- **Tổng ảnh trực tiếp về Vidocq và hồ sơ của ông: hơn 400.** Vượt xa ngưỡng 50. Chỉ ảnh thế kỷ 19 và trước đó (PD); chưa soát từng file giấy phép (làm ở bước `research_long`). Bỏ áp phích phim 1923 (`René Navarre dans Vidocq - affiche.jpg`) vì CL không dùng hình phim.

## 8. Rủi ro

- **Nguồn:** chỉ có Wikipedia và trang hồi ký. Cần sách sử hoặc bài báo học thuật (Walz, Kalifa) và Wikisource bản gốc trước khi viết lời.
- **Giai thoại:** hồi ký và truyền thuyết về Vidocq (ảnh trí nhớ, dựng tội phạm, phát minh) hầu hết chưa kiểm chứng; kịch bản phân biệt rõ "hồ sơ", "theo hồi ký", "giai thoại".
- **Dễ lẫn tiểu thuyết với đời thật:** Javert chỉ "loosely based" trên Vidocq. Không nói "Vidocq là Javert"; không gán cho ông hành động trong truyện của Hugo.
- **Nạn nhân và người bị bắt:** ít người có tên được hồ sơ ghi; không gán tội cho người thật khi thiếu căn cứ. Không ảnh bạo lực thật (không có ảnh thế kỷ 19 loại đó), hình khắc xích tù chỉ dùng ở mức tư liệu.
- **Khác biệt nguồn về 1832–1843:** xem mục 6; nếu không kiểm được, kết Ch10 bằng "theo các nguồn", không chốt số năm tù.
- **Mối nguy trùng ý với Hoàng Kim Vinh:** cả hai là "cảnh sát kiêm giang hồ". Kịch bản không so sánh, không nhắc kênh Thượng Hải.
