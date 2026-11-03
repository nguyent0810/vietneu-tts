# EXTRACT_LOG_A (pilot131) — agent A, claude-sonnet
Ngày 2026-11-03. Quy trình: curl (không sandbox) -> HTML/JSON -> văn bản (h2t.py, html.parser) -> sources/*.txt -> trích fact bằng script, span được kiểm tự động có mặt trong snapshot (chuẩn hoá khoảng trắng/NFC) trước khi ghi. Không ghi trạng thái verified. Validator `python3 -m research.fact_store validate`: 3/3 store errors=0.

## Nguồn dùng
### bud_vessantara (20 fact, tất cả kind=legend trừ khi nêu; according_to_edition = bud_vessantara_s1)
- s1 ancient-buddhist-texts.net, Ja 547 (Cowell vol. VI; có đánh dấu trang [6.xxx]) — nguồn chính. URL thực: /English-Texts/Jataka/547.htm (đường dẫn /Texts-and-Translations/... trả 404, không phải bị chặn).
- s2 Wikipedia "Vessantara Jataka" — phụ, chỉ làm bằng chứng đối chiếu (fact 2, 3, 16).
- Lưu ý: bản ABT dùng bản Cowell có hiệu đính; nhãn edition ghi "Cowell vol. VI" theo đánh dấu trang, trang không in tên dịch giả ở đầu. Người duyệt nên đối chiếu.
### bud_angulimala (22 fact: 16 legend (f01-f11, f14-f18), 4 variant (f12/f13, f20/f21), 1 tradition (f19), 1 attributed (f22))
- s1 SuttaCentral Bilara API (Sujato, CC0) — chính; s2 Access to Insight (Thanissaro 2003, CC BY-NC) — bản dịch thứ hai độc lập (publisher khác); s3 Wikipedia — phụ (paritta, dị bản số ngón tay, tên Ahiṃsaka theo Buddhaghosa).
- Giao diện web suttacentral.net là SPA (không có văn bản trong HTML) nên dùng API JSON bilarasuttas; snapshot gồm các segment dịch nối theo thứ tự (có ký hiệu <j> của Bilara).
- Dị bản có thật: "obstructed labor" (Sujato, f12) vs "breech birth" (Thanissaro, f13) cùng variant_group; số ngón tay (trăm/nghìn, f20/f21) từ Wikipedia; MN 86 không nêu con số.
### fs_mau_than_1968_2027 (20 fact, kind=tradition trừ f03/f04 = variant, f19 = attributed)
- s1 thayungkhiem.vn tử vi Mậu Thân 2027; s2 huyenbi.net; s3 lasotuvi.io bảng sao hạn 2027; s4 thayungkhiem.vn Lục Thập Hoa Giáp; s5 xskt.com.vn lịch vạn niên 1968; s6 VietNamNet/Tuần Việt Nam (báo) bảng tam tai.
- Tất cả là nguồn tử vi/lịch thương mại + 1 báo; ghi rõ là tín ngưỡng (scope + f19: chính lasotuvi.io tự ghi "quan niệm truyền thống, không quyết định diễn biến cuộc sống").
- Dị bản nạp âm: yêu cầu giao nói Đại Dịch Thổ; thực tế nguồn chia đôi: s1/s2/s4 ghi "Đại Trạch Thổ" (s4 còn ghi 大驛土), s5 ghi "Đại Dịch Thổ" -> f03/f04 cùng variant_group nap_am_mau_than_name (certainty sẽ là contested, đúng ý). Cùng chữ Hán 大驛土.

## Fact không trích được vì thiếu nguồn / nguồn chặn
- Tử vi: không có nguồn chính thống nào bằng văn bản cho quy tắc tam tai/thái tuế ngoài sách vở/báo; thuvienphapluat.vn trả 403 (không vượt chặn, ghi status blocked_http_403). vi.wikipedia các trang Tam tai/Thái Tuế/Nạp âm trả 404 (tên trang sai/không có).
- Không trích được "Thái Tuế" tổng quát (xung/hình/hại/phá theo cặp chi): bảng lasotuvi s3 chỉ liệt kê theo tuổi, không có định nghĩa; chỉ trích quan hệ Thân–Mùi (bình hòa) và Thân xung Dần/hại Hợi (s4).
- Ghi chú dữ liệu: s4 "Hợp tuổi: Tý, Thìn, Tỵ" và s2 "hợp: Kỷ Dậu, Quý Sửu, Ất Mão" khác nhau (khung khác nhau, lục hợp vs hợp làm ăn); không trích để khỏi gán sai.
- Vessantara: không trích tên người đánh xe/số liệu chi tiết (Maddī bị hổ chặn, trái cây cúi cành) vì chỉ có ở Wikipedia hoặc phải đọc dài; 20 fact đủ cho khung chính (voi trắng, cho con, Sakka xin Maddī, trở về).

## Lỗi còn lại / cần người xem
- Spans có thể chứa chú thích nội dòng của bản dịch (ví dụ {6.487}, [6.251], <j>) vì chép nguyên văn snapshot.
- Vessantara f09: span thứ hai là bối cảnh hạn hán, không phải lời trích trực tiếp; f14 và f18 dùng object literal (tên Jūjaka) do validator cấm object entity cho predicate performed.
- kind=tradition cho cả can chi (f01/f02) theo yêu cầu "chỉ tradition".

## Thời gian đo (đồng hồ thật, giờ máy)
- Tổng phiên: bắt đầu ~21:03 (tải nguồn, chuyển văn bản, đọc schema) đến 21:10:36 (xong index + log) ≈ 7,5 phút cho cả 3 chủ đề.
- Phần viết/trích fact bằng script (đo bằng mốc script): bud_vessantara 21:08:38–21:09:27 (~50 giây tới khi validate pass); bud_angulimala 21:09:27–21:09:34 (viết sau khi đã đọc nguồn, ~ 7 giây chạy; thời gian đọc nguồn nằm trong phần tải); fs_mau_than_1968_2027 21:09:34–21:10:36.
- Thời gian đọc nguồn từng chủ đề không đo riêng (xen kẽ) — chỉ có mốc tổng.
