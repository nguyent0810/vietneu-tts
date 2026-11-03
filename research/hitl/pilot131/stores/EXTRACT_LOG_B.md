# EXTRACT_LOG_B (agent B) — pilot131
Index nguồn: sources/sources_index_B.json. Store: stores/{fs_quet_nha_mung1_tet,vsd_thanh_nha_ho,vsd_bach_dang_1288}.json. Validator: 0 lỗi cả 3 (18 / 24 / 26 fact). Không có trạng thái verified.

## Nguồn dùng
- fs_quet_nha_mung1_tet: giaoduc.net.vn (s1), vietbao.vn (s2), znews.vn (s3), baophapluat.vn (s4) — toàn báo; không có nguồn học thuật/văn bản Sưu thần ký gốc.
- vsd_thanh_nha_ho: SGGP (s1), VGP tiếng Anh 29/06/2011 (s2, official), Wikipedia vi (s3), Wikipedia en (s4).
- vsd_bach_dang_1288: Wikipedia vi (s1), Wikipedia en (s2), PLO (s3), INA nauticalarch.org (s4).

## Nguồn bị chặn / không lấy được
- UNESCO whc.unesco.org/en/list/1358: HTTP 403, không vượt chặn (ghi status trong index). Thay bằng VGP (cơ quan nhà nước) + SGGP.
- Wikisource Đại Việt sử ký toàn thư (URL đoán): 404, không chụp. Không có bản toàn thư gốc; chỉ có trích dẫn toàn thư/Nguyên sử qua Wikipedia (kind=attributed).
- vjol.info.vn (bài Ghềnh Cốc): 404. vtcnews trang tag: quá ít nội dung, bỏ.

## Fact không trích được vì thiếu nguồn
- Chủ đề 1: văn bản gốc Sưu thần ký (chỉ có tóm tắt báo); nguồn học thuật về nguồn gốc tục lệ; ý kiến TS Nguyễn Đệ ("không phổ biến") chỉ xuất hiện trong kết quả tìm kiếm, không nằm trong bản chụp.
- Chủ đề 2: trang UNESCO (tiêu chí ghi danh dẫn từ SGGP, ngày 27/6/2011 từ Wikipedia en); nguồn tỉnh Thanh Hóa.
- Chủ đề 3: văn bản Đại Việt sử ký toàn thư/Việt sử lược; số liệu thương vong chỉ từ Wikipedia + báo.

## Điểm tranh chấp đã mã hoá (variant_group)
- T1: nhu_nguyet_name_spelling (Nguyệt x3 vs Nguyện x1), who_disposed_rubbish (vợ quét vs lái buôn đổ).
- T2: citadel_dimensions (5 phương án), stone_block_weight, stone_block_weight_max, stone_block_size (có mâu thuẫn ngay trong cùng bài Wikipedia vi).
- T3: yuan_ship_losses (>400 / 400 / 500), yuan_casualties (>40.000 / 80.000), yuan_fleet_size (500 / 500-600), phan_tiep_fate (3 dị bản), cao_quy_stakes_dating (Viện Khảo cổ: 1288 vs C14 2100–2400 năm: Đông Sơn).

## Lỗi/giới hạn còn lại
- Fact "4,000–4,500 killed": hộp thông tin Wikipedia en trích văn bản phẳng nên không rõ bên chịu thiệt hại (nhiều khả năng Đại Việt); để kind=assertion, hedge possible, ghi rõ trong statement_vi. Nên người duyệt xem lại.
- Quy đổi 120 trượng ≈ 480 m là của Wikipedia vi, không phải của Đại Nam nhất thống chí.
- Dị bản kích thước khối đá lưu bằng quantity m3 xấp xỉ kèm scope; kích thước gốc nằm ở qualifiers.scope.
- Hầu hết nguồn T2/T3 là Wikipedia (kind=wikipedia, nguồn phụ); T1 là báo, kind=press.
- Dùng predicate "other"+predicate_text cho nhiều fact (chưa có predicate phù hợp).
- accessed_at ghi giờ chạy script dựng store (đồng nhất cho cả 3 chủ đề).

## Thời gian (đồng hồ thật, gộp)
Tổng ~4 phút đồng hồ từ lúc bắt đầu tới khi validator đạt 0 lỗi (tải nguồn song song ~1 phút; dò tìm + đọc ~1,5 phút; viết fact + sửa 2 vòng lỗi validator ~1,5 phút). Không đo riêng từng chủ đề vì tải và trích xuất chạy xen kẽ.
