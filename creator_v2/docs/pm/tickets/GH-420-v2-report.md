# GH-420: báo cáo bản 2 (15/11/2026)

Người làm: Claude Sonnet (subagent). Worktree `wt-plan-cl2/creator_v2`. Không commit, không push, không TTS, không render, không upload. `script.md` giữ nguyên.

## Việc 1: `data/long/cl-sarin-tokyo-1995/script.v2.md`

- **Độ dài:** 6.593 âm tiết, 14 chương, 414 câu, câu dài nhất 32 âm tiết (khoảng 26 phút theo 250 âm tiết/phút của script_lines, hoặc khoảng 30 phút theo 215/phút của bước trước).
- **Tiêu đề:** chính "Bị Nghi Hại Vợ, Ông Là Nạn Nhân: Sarin Matsumoto 1994" (53 ký tự). Phương án 2 "Người Gọi Cấp Cứu Bị Gọi Là Thủ Phạm: Sarin Nhật 1994"; phương án 3 "Chín Tháng Bị Nghi, Hai Ngày Muộn: Từ Matsumoto Đến Tokyo". Ba phương án ghi đầu file. Không còn chữ "hạ độc" khẳng định.
- **Cold open (CH00, 194 âm tiết):** câu 1 và 2 là nghịch lý (người gọi cấp cứu bị gọi "Người Khí Độc", vợ hôn mê mà người bị nghi lại là ông), câu 3 nhảy sang Tokyo, câu hỏi ở câu 4, cảnh toa tàu, lời hứa ở câu cuối. Không chào, lộ trình nằm ở CH01.
- **Cảnh phỏng dựng đã thêm (mỗi câu gắn `{pd}`):** (1) toa tàu sáng thứ Hai 20/3/1995 (CH00); (2) khu nhà yên tĩnh Matsumoto đêm hè với đèn đường, cửa sổ mở (CH02); (3) ánh đèn đỏ xe cấp cứu ở xa (CH02); (4) phòng điều tra sáng hôm sau với bản đồ khu nhà (CH02); (5) phòng điều tra đêm thứ hai (CH03); (6) bàn biên tập duyệt bài Asahi (CH04); (7) bàn hồ sơ cảnh sát Kanagawa, bản tin nhắc "sarin" (CH05); (8) con đường núi trong sương dẫn đến khu Satyan (CH06); (9) phòng họp Tokyo cuối 1994 với hai chồng giấy (CH07); (10) tờ lịch tháng 3/1995 khoanh ngày thứ Tư (CH08); (11) sân ga giờ cao điểm và nhân viên ga (CH09); (12) hành lang bệnh viện (CH10); (13) cổng khu Kamikuishiki sáng 22/3 (CH11); (14) phòng xử án trống (CH12); (15) bó hoa trắng (CH13). Toàn bộ chỉ có người vô danh, đồ vật, ánh sáng. Ông Kono, bà Sumiko, ông Kakimi, luật sư Nakamura, ông Nagaoka không có lời hay cảm xúc bịa; các câu về ông Kono đều "theo báo cáo/theo Nippon.com", cộng câu "tôi không dựng lời cho ông".
- **Giả thuyết đã nói rõ là giả thuyết:** CH03 (câu trả lời gần nhất dễ chọn nhất), CH11 (lá thư "thí nghiệm": nếu đúng thì Matsumoto là một lần thử, nêu như câu hỏi), CH11 (cách hiểu lời ông Kono là cách hiểu của người kể).
- **Thay đổi khác so với v1:** thêm đoạn CH01 báo trước chữ "hãy hình dung/có lẽ" là phỏng dựng; bỏ tên người nạn nhân mất 2020 (factcheck không có tên); bỏ "cái ao" trong CH03 (factcheck không có); rào nguồn CH02, CH10, CH11, CH12, CH13 gom và đổi cách nói ("theo trang tiểu sử ông Asahara", "theo trang tiếng Nhật", "theo hồ sơ về giáo phái"), mỗi chương tối đa một cụm "bách khoa", không bỏ rào nào. Không có số mới: so với v1 tập số trong lời đọc không đổi (đã kiểm bằng regex).
- **Đánh dấu:** một dấu cuối câu mỗi dòng (script_lines chỉ nhận một dấu). Câu phỏng dựng dùng `{pd}`, không kèm `{beat}`; beat đặt ở câu kể thật quanh đó.

## Cổng đã chạy trên nội dung v2

- `script_lines.parse` + `gate`: `[]`. `craft.audio_problems`: `[]`.
- Cảnh báo còn lại (không chặn): `NHAY_MOC` ở CH04, CH06, CH10, CH12 (mốc lùi/tiến cố ý), như v1. Hết `SOURCE_DENSITY`, hết `NHIP_30S`.
- Chưa chạy `factcheck_lint` (Lead chạy sau khi thay v2). Bảng "Ghi chú kiểm chứng" cuối file đã cập nhật nhãn PHỎNG DỰNG; ba điều phải kiểm trước khi đăng: nhãn PHỎNG DỰNG trên hình cho mọi câu `{pd}`; "chiếc Mi-17" và Nonaka xin lỗi vẫn chỉ có ở bách khoa; Nagaoka (còn sống) giữ lời trích đã đăng báo.

## Việc 2: `data/long/cl-sarin-tokyo-1995/ai_prompts.md`

- 29 prompt (`ai_01.png` đến `ai_29.png`), đúng định dạng `_lib198`, tag lô `minh_hoa_chung` ghi ở đầu file.
- Nhóm: Matsumoto đêm hè (khu phố, ao nhỏ, cửa sổ mở, dãy nhà, đèn cấp cứu xa: 5 ảnh); phòng điều tra, hồ sơ, tờ báo, TV (5); sân ga giờ cao điểm, đồng hồ ga không đọc được, toa trống, toa có người đọc báo, cầu thang, lối thoát hiểm (6); cửa ga và xe cấp cứu từ xa, lực lượng khử độc không mặt, băng phong tỏa (3); hành lang bệnh viện (1); phòng xử và cửa phòng xử (2); khu nhà Kamikuishiki trong sương, đường núi, đoàn xe cảnh sát (3); tờ lịch tháng 3/1995 (2); bia hoa trắng (2).
- Mọi prompt có đủ bối cảnh, thời đại, ánh sáng, ống kính, màu, chất liệu phim, chừa chỗ chữ, và kết bằng câu cấm: không chữ/số/logo/watermark, không mặt rõ, không thương tích, không vũ khí, không hóa chất đang xử lý. Không có Asahara hay ông Kono.
