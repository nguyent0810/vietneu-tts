# SPECIALIST_LOG (pilot131) - agent claude-sonnet, 2026-11-03, prompt_version "pilot131-specialist"
Bổ sung nguồn chuyên ngành cho vsd_thanh_nha_ho (f25-f56, +32 fact) và vsd_bach_dang_1288 (f27-f76, +50 fact). Chỉ APPEND, không sửa fact cũ. Validator: thanh_nha_ho facts=56 errors=0; bach_dang facts=76 errors=0. Không đăng nhập, không vượt chặn, không CAPTCHA (DuckDuckGo bật CAPTCHA -> bỏ).
Lưu ý định dạng: snapshot_path của entry MỚI là tên file trần (theo yêu cầu) ở cả sources_index.json và mục sources trong store; entry cũ trong store vẫn là đường dẫn tương đối repo.

## 1. Nguồn đã thử (HTTP)
Thành nhà Hồ
- thanhnhaho.gov.vn: không kết nối được (000). Cổng chính thức thật là https://thanhnhaho.vn : 200 (dùng).
- thanhnhaho.vn GioiThieu Id=2028 / Id=19 / NewsDetail 12784, 11721, 12802: 200 (dùng).
- dsvh.gov.vn/thanh-nha-ho: 200 nhưng trang chung, không có số liệu; bài dsvh.gov.vn/...-353: 200 (dùng).
- UNESCO whc.unesco.org/en/list/1358/documents, /document/138033, /document/152461, /archive/advisory_body_evaluation/1358.pdf, /uploads/nominations/1358.pdf, /archive/2011/whc11-35com-8B-Add-en.pdf: tất cả 403 (không vượt chặn). Ghi status blocked_http_403 trong sources_index.
- web.archive.org bản lưu của PDF ICOMOS: 429 (không thử lại).
- vjol.info.vn tckhdhhv: 404; vjol search "thành nhà hồ": 200 nhưng chỉ form tìm kiếm (không có kết quả tĩnh). Bài TNU Journal 49765 trên vjol (PDF) tải được nhưng về du lịch tâm linh Quảng Yên -> KHÔNG dùng.
- duckduckgo html: CAPTCHA (bỏ); tapchicongsan tìm kiếm: trang rỗng.
Bạch Đằng
- nauticalarch.org project page: 200 (đã có s4). INA Quarterly 39.1/2 (2012) PDF 13,9 MB và 35.2 (2008) PDF 8,1 MB: 200 (dùng; PDF là ảnh quét, xoay ngược 180 độ -> OCR tesseract sau khi xoay; văn bản OCR có thể sai chính tả).
- tandfonline (Kimura et al., IJNA 2010, DOI đoán): 403. tandfonline 10.1080/10572409.2020.1760433: 403.
- vi.wikisource Toàn thư: trang Bản_kỷ_quyển_5 404 (URL đoán sai); Wikisource Tập I/II tải được (200) nhưng bản dịch Mạc Bảo Thần 1945 chỉ gồm 5 cuốn tới đời Ngô/sứ quân, KHÔNG có đời Trần -> không dùng, ghi vào index là not_applicable. API wikisource với URL không mã hoá: 400.
- baotanglichsu.vn (Bảo tàng Lịch sử quốc gia): 4 bài 200 (dùng). baovanhoa.vn một URL: 404. znews.vn: 200 (dùng, kind=press vì là báo, nhưng trích lời chuyên gia Viện Khảo cổ).
- khaocohoc.vass.gov.vn: 200 nhưng chỉ trang chủ tạp chí, không có bài toàn văn tĩnh. Archive.org tìm "ho citadel vietnam": chỉ tài liệu CIA, không liên quan.

## 2. Nguồn dùng (snapshot, status ok)
Thành nhà Hồ: s5 báo cáo khai quật 4 cổng thành 2022 (ThS Nguyễn Thắng và đoàn Viện Khảo cổ học, đăng trên thanhnhaho.vn); s6 bài học thuật TS Đỗ Quang Trọng (có trích Bezacier, Kikuchi 2005, Tống Trung Tín 2008, ĐVSKTT); s7 "Giá trị di sản" (cổng chính thức); s8 Nhà trưng bày bổ sung (Trung tâm BTDS); s9 Cục Di sản văn hóa; s10 bài đăng lại trên cổng (không rõ tác giả; coi là thứ cấp).
Bạch Đằng: s5 INA Quarterly 39 (Sasaki, Kimura, Morriss, Inglis), s6 INA Quarterly 35.2 tin ngắn 2008 (đều là OCR); s7 Tống Trung Tín - Lê Thị Liên (Viện Khảo cổ học, Đại Đoàn Kết 2013, đăng lại ở Bảo tàng LSQG); s8 bài tổng quan 2020 trên Bảo tàng LSQG (phỏng vấn Lê Thị Liên, Đặng Hồng Sơn, Staniforth); s9 bài Bảo tàng LSQG về khai quật Cao Quỳ 2019; s10 bài Bảo tàng LSQG về cọc Bạch Đằng trưng bày; s11 Znews (press, tường thuật tiểu ban khảo cổ học dưới nước, Hội nghị Thông báo khảo cổ học lần 55).
Lưu ý: không lấy được văn bản gốc UNESCO/ICOMOS, báo cáo khai quật Cao Quỳ đầy đủ, bài IJNA của Kimura, bản dịch Toàn thư đời Trần.

## 3. Fact mới và quan hệ với fact cũ
### vsd_thanh_nha_ho
- Năm xây 1397 (f25 s9/s7) ủng hộ f01. f26 = đoạn Toàn thư (qua Đỗ Quang Trọng): giêng 1397 sai Đỗ Tỉnh đo đạc, đắp thành đào hào..., "tháng 3 thì công việc hoàn tất" (nguồn sử gốc; nói "công việc" chứ không riêng thành đá).
- "3 tháng": f27, f28 (trang chính thức nói 3 tháng, "chưa được khoa học lý giải" f29) ủng hộ f03; f30 (bài đăng lại) nói lõi 3 tháng nhưng hoàn thiện tiếp tới 1402 (làm rõ giới hạn của "3 tháng"); f31 Đàn Nam Giao xây 8/1402; f32 chuyển đô 3/1398; f33 sụp đổ 1401 (ĐVSKTT, qua trang Nhà trưng bày) ủng hộ f23 (văn bản hơi khác: không có chữ "lại").
- Kích thước thành (variant_group citadel_dimensions, cùng nhóm f09-f13): f34 870,5 (Bắc-Nam) & 883,5 (Đông-Tây) trên cổng Thành Nhà Hồ (bài đăng lại) ủng hộ f09; f35-f38 Viện Khảo cổ học 2022: khoảng cách cổng Nam-Bắc 886,5; cổng Đông-Tây 883,5; TƯỜNG bắc-nam 878,5; tường đông-tây 875,5 -> MÂU THUẪN với 870,5 cho chiều Bắc-Nam; f39 chu vi 3.508 (nguồn ghi nhầm đơn vị m2), diện tích 769.126 m2; f40 chu vi hơn 3,5 km.
  Nhận xét suy ra (không phải fact của nguồn): 2x(870,5+883,5)=3.508 khớp chu vi chính thức; 878,5x875,5=769.126,75 khớp diện tích chính thức. Tức hai bộ số cùng tồn tại trong tài liệu chính thức; 870,5 KHÔNG xuất hiện trong báo cáo Viện Khảo cổ 2022. Khi nói "870,5 m" cần ghi rõ thành nội, nguồn, và có số 878,5 khác.
- Chiều cao tường (group wall_height, đối chiếu f20 "trung bình 8 m" của SGGP): f41 Viện Khảo cổ: hiện còn trung bình 5-6 m; f42 tường Tây thấp 3-4 m; f43 "nâng đá lên độ cao trên 10 m" (tiêu chí iv, nói về kỹ thuật xây). Mâu thuẫn với f20 (8 m).
- Cổng Nam (group south_gate_height): f44 cao còn lại 7,65 m, rộng 34,85 m (Viện Khảo cổ 2022); f45 vòm giữa 8,5 m (Đỗ Quang Trọng). Cả hai khác f22 (9,5 m cao, 15,17 m rộng, Wikipedia en).
- Đá: f46, f47 "10-26 tấn" (cổng chính thức, Cục Di sản; cùng group stone_block_weight với f14 10-20 t); f48 lớn nhất ~26,7 t (Kikuchi 2005 qua Đỗ Quang Trọng; ủng hộ f16); f49 kích thước TB 2,2x1,5x1,2 m, f50 lớn nhất 4,2x1,7x1,5 và 5,1x1x1,2 m (group stone_block_size, mâu thuẫn f18 2x1x0,7 m của Wikipedia). Kiểm tra thể tích: 2,2x1,5x1,2=3,96 m3 (~10,7 t với đá vôi 2,7 t/m3) phù hợp mức 10 t; 2x1x0,7=1,4 m3 (~3,8 t) KHÔNG phù hợp "10-20 t" nên f18 có vẻ là số của Wikipedia cho khối nhỏ hơn.
- Khác: f51 tổng 20.000 m3 đá + gần 100.000 m3 đất; f52 mỏ đá núi An Tôn; f53 độ dày chân tường phía Đông 21,36 m; f54 đá tường/cổng Bắc nhỏ hơn, một phần do tu sửa; f55 >300 địa danh trên gạch; f56 UNESCO công nhận 27/6/2011.

### vsd_bach_dang_1288
- Niên đại cọc Cao Quỳ (group cao_quy_stakes_dating, cùng f24/f25): C14 "năm 1270" (Bảo tàng LSQG, s9) ; "1270-1430" và "chưa ai khẳng định" (TS Kiên, s11); mẫu "hơn 700 năm", các mẫu khác nhau, có thể tận dụng cọc cũ (PGS Miên, s11); Viện Khảo cổ nhận định thuộc trận lần 3 1288 (s9, ủng hộ f24); GS Ngọc "nhiều khả năng 1288"; TS Kiên nghi ngờ đó là bãi cọc; TS Hiếu: nhiều ý kiến. Không có nguồn nào ủng hộ f25 (C14 2100-2400 năm trước, Đông Sơn): nguồn chuyên ngành mới cho thấy C14 Cao Quỳ ~1270 và >700 năm, tức f25 (Wikipedia vi) đang MÂU THUẪN với số liệu của chính Viện Khảo cổ học.
- Lấy mẫu (group cao_quy_c14_sampling): Bảo tàng LSQG nói cán bộ Bảo tàng Hải Phòng lấy mẫu; Znews nói có mẫu do trưởng thôn mang lên; TS Đông: sai quy trình sẽ cho kết quả sai.
- Số cọc Cao Quỳ: 27 cọc/3 hố/950 m2 (11/2019) vs 37 cọc bước đầu (Znews); đường kính 26-46 cm vs 35-50 cm; cách nhau 3-4 m; cách Bạch Đằng 18 km ngược dòng.
- Đồng Má Ngựa C14: 4 mẫu 1280-1400; Yên Giang: lần định niên đại cuối 1980s (CHDC Đức) không thuyết phục; diện tích 3 bãi cọc; lịch sử khai quật (1953 phát hiện, 1958, 1965, 1969, 1976, 1984, 1988; Vạn Muối 2005); cọc lớn 20-30 cm; lớp than 2-2,3 m (giả thuyết hỏa công); loại gỗ.
- Vị trí cọc (group stake_placement): INA 2012 mô tả cọc "dưới mặt nước" trong sông (kiểu truyền thuyết) vs Tống Trung Tín - Lê Thị Liên, Vũ Minh Giang, Staniforth: KHÔNG cắm cọc ngang dòng Bạch Đằng (rộng/sâu 15-16 m), cọc ở nhánh cổ, ghềnh đá. Đây là điểm sửa quan trọng cho "kịch bản hậu kỳ": không nói "cọc cắm ngang sông Bạch Đằng".
- Thủy triều: triều rút mạnh rạng sáng 8/3, triều cạn trưa 8/3 (Tống Trung Tín - Lê Thị Liên); triều lên ngập bãi cọc, Nguyễn Khoái giả thua, Ô Mã Nhi đuổi theo, ghềnh Cốc nhô lên chặn đường ra biển (Bảo tàng LSQG).
- Đường của Ô Mã Nhi / quân Nguyên: đường rút Vạn Kiếp -> Lục Đầu -> Kinh Thầy -> sông Đá Bạch -> cửa Bạch Đằng (s8); bị ép vào sông Đá Bạc (s10); Cao Quỳ có thể buộc quân Nguyên đi sông Đá Bạc thay vì sông Giá (hypothesis, s9). Ô Mã Nhi chỉ có vai trò chỉ huy truy đuổi/bị bắt, chưa có nguồn chuyên ngành nào ở trên nêu "tuyến riêng" của ông.
- Thiệt hại/tàu (groups yuan_ship_losses, yuan_casualties, yuan_fleet_size): "trên 400 chiến thuyền, 8 vạn quân" (Bảo tàng LSQG s10) vs "toàn bộ 500 chiếc" (s8) vs INA "over 400 ships" (legend); 500 chiến thuyền + 70 thuyền lương (s8, khớp f22); ngày 9/4/1288 (khớp f01). Lưu ý 8 vạn >> "hơn 4 vạn" của f17.
- Khác: nhóm nghiên cứu quốc tế lập năm 2008 (INA) vs 2009 (Bảo tàng LSQG); INA 2012: "chưa có hiện vật nào khác" vs Đồng Má Ngựa có mảnh sứ thời Nguyên (group battle_artifacts); >100 dị thường từ (2011).

## 4. Khoảng trống còn lại
- UNESCO/ICOMOS (403): chưa có số liệu 870,5 m / độ dày tường / thời gian xây từ hồ sơ đề cử; cần tải thủ công hoặc nguồn mirror.
- Chưa có báo cáo khai quật Cao Quỳ đầy đủ, phương pháp/phòng thí nghiệm C14, sai số (cal BP) -> chưa thể tuyên bố "C14 1270" có nghĩa gì với 1288.
- Chưa có nguồn chuyên ngành riêng về hành trình Ô Mã Nhi (chỉ có tổng quan); chưa có bản dịch Toàn thư đời Trần mở (Wikisource 1945 không phủ), nên các trích dẫn Toàn thư đều gián tiếp (qua Đỗ Quang Trọng, Bảo tàng LSQG).
- Chưa truy cập bài Kimura et al. (IJNA), Staniforth (Archaeology 2016), Hà Văn Tấn - Phạm Thị Tâm.
- OCR INA: văn bản có thể sai chữ; span đã khớp với snapshot nhưng nên đối chiếu PDF gốc khi duyệt.
- "3 tháng": nguồn sử gốc (Toàn thư) chỉ nói "tháng 3 công việc hoàn tất" (từ tháng giêng, gồm cả đắp thành đào hào, tông miếu...); chưa có nguồn khảo cổ độc lập đo tuổi/thời gian xây thành đá.
