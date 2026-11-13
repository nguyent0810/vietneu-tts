# GH-316 — Báo cáo review câu chuyện

Đã review đủ tám chương theo sáu luật mạch kể, viết tám bản review và ghép `script.v2.md`; giữ nguyên đầu file và mục Ghi chú kiểm chứng của bản gốc, không ghi đè `script.md`. Không gọi mạng, không render, không commit, không đăng. Các ví dụ tính tiền, phí và thuế được gắn giả định; thuế 0,1% có rào chưa xác nhận nguyên văn ngay tại CH04. Bản mười vòng nêu giả định tái đầu tư toàn bộ kể cả phần lẻ của một cổ phiếu, không xét ràng buộc lô và các khoản khác; đây là mô hình toán học, không phải kết quả giao dịch thực tế.

## Âm tiết

Đếm số từ lời đọc bằng `spoken_text` của `motion.long.script_lines`, nhất quán với tổng của `long_gate` trên bản cũ. Mức thay đổi từng chương đều nằm trong ±10%.

| Chương | Cũ | Mới | Thay đổi |
|---|---:|---:|---:|
| CH00 | 311 | 303 | -2.6% |
| CH01 | 344 | 318 | -7.6% |
| CH02 | 336 | 323 | -3.9% |
| CH03 | 273 | 255 | -6.6% |
| CH04 | 327 | 345 | +5.5% |
| CH05 | 280 | 269 | -3.9% |
| CH06 | 259 | 258 | -0.4% |
| CH07 | 487 | 500 | +2.7% |
| **Tổng** | **2617** | **2571** | |

## Kiểm tra

- Gọi trực tiếp `parse`, `gate`, `flow_warnings` của `motion.long.script_lines` bằng Python cho cả hai bản: lỗi gate cũ 0, mới 0; cảnh báo lint luồng cũ 0, mới 0, trong đó NHIP_DEU và RAO_NGUON đều 0 ở cả hai bản. Không phát sinh cảnh báo mới. Tổng âm tiết mới đạt khoảng 2.350–2.900.
- Tính lại bằng Python `decimal`, đối chiếu Ghi chú kiểm chứng: phí 75.000 đồng mỗi chiều; thuế giả định 50.000 hoặc 45.000 đồng; chênh lệch 200.000 đồng; hòa vốn 50.200,501 đồng/cổ phiếu, tăng 0,4010025%; phương án phí 0,25% hòa vốn 50.301,054 đồng; phí Sở minh họa 13.500 đồng mỗi chiều; lưu ký 270 đồng/tháng và 3.240 đồng/năm; ứng trước 32.876,712 đồng; mười vòng còn 48.038.508 đồng. Tỷ lệ cộng phí Sở và ứng trước chỉ là ước lượng, không khẳng định là nghiệm hòa vốn chính xác.
- `python scripts/long_gate.py ck-c7-mo-tai-khoan-phi --min-syl 1900`: **TRƯỢT, 20 lỗi**, không in ĐẠT. Đây là cổng trên `script.md` gốc và cấu hình sản xuất của topic, không phải cổng riêng của `script.v2.md`: chưa có cảnh và HUD cho tám chương, chưa TTS, thiếu trường `spec.youtube` và nguồn công khai trong spec. Ticket chỉ giao review câu chuyện và cấm render; dựng spec/cảnh/TTS hoặc sửa kịch bản gốc vượt phạm vi. Vì vậy không thể báo toàn bộ cổng Long đã đạt.
- Soát UTF-8 các file giao: không có ký tự thay thế U+FFFD hoặc chuỗi dấu hỏi bất thường; các dấu `?` là dấu câu hoặc URL nguyên trạng. Không tạo clip sheet hay thumbnail vì ticket không yêu cầu dựng hoặc render.
- Lệnh `python motion/long/script_lines.py --help` không hỗ trợ `--help` và trả lỗi vì coi đây là tên topic; không ghi file. Sau đó đã dùng cách `parse`/`gate` mà ticket cho phép.

## Cần xác minh gộp

- **CH00:** Nguồn thống kê tài khoản cần Lead mở lại bản gốc; không suy ra số người hay cách mở từ số tài khoản.
- **CH00:** T cộng hai và thời điểm tiền có thể sử dụng: đối chiếu quy định, phương thức thanh toán áp dụng.
- **CH01:** Đối chiếu nguyên văn Điều 17 Thông tư 121/2020 và Điều 88 Luật Chứng khoán cùng hiệu lực sửa đổi.
- **CH01:** Xử lý tài sản khi công ty gặp sự cố hoặc phá sản chưa được xác minh; bản viết lại không bảo đảm kết quả.
- **CH02:** Kiểm văn bản hiện hành về cơ chế định giá môi giới; nguồn về quyền tự định giá trong factcheck là bài giai đoạn dự thảo.
- **CH02:** Đối chiếu biểu phí thực tế và điều kiện phí mỗi chiều.
- **CH03:** Đối chiếu Quyết định 1541 bản gốc, phạm vi Sở Hà Nội và mức áp dụng cho các thị trường khác.
- **CH03:** Kiểm biểu phí thực tế xem khoản Sở gộp hay tách; không tính trùng.
- **CH04:** Chưa xác nhận nguyên văn điều khoản hiện hành về mức thuế 0,1% trên giá bán cổ phiếu niêm yết của cá nhân cư trú; Lead phải đối chiếu trực tiếp trước khi đọc.
- **CH04:** Kiểm hiệu lực và phạm vi áp dụng Luật 109/2025, Nghị định 253/2026 và Thông tư 87/2026 bằng văn bản gốc.
- **CH05:** Đối chiếu Quyết định 1541 và quy định chuyển tiếp năm 2026 bằng văn bản gốc, gồm ngày hiệu lực.
- **CH05:** Kiểm thuế giá trị gia tăng, cách tính theo tháng và phí thực tế do công ty thu.
- **CH06:** Kiểm số tiền được ứng thực tế sau phí, thuế, thời gian tính lãi và mọi phí tối thiểu trong hợp đồng.
- **CH06:** Đối chiếu thời điểm tiền bán sẵn sàng sử dụng theo T+2 trong điều kiện cụ thể.
- **CH07:** Mức thuế 0,1% chỉ là giả định vì chưa xác nhận nguyên văn điều khoản hiện hành.
- **CH07:** Kiểm bước giá, lô giao dịch, phí tối thiểu, thuế và các khoản khác trước khi áp dụng giá hòa vốn; ví dụ mười vòng giả định mua lượng cổ phiếu tương ứng, không xét ràng buộc lô.
- **CH07:** Kiểm phí Sở gộp hay tách và chi phí ứng thực tế; tỷ lệ cộng thêm chỉ là ước lượng, không phải nghiệm hòa vốn chính xác.

Các đường dẫn bàn giao: `data/long/ck-c7-mo-tai-khoan-phi/story_review/ch00.md` đến `ch07.md`; `data/long/ck-c7-mo-tai-khoan-phi/script.v2.md`. Clip sheet và thumbnail: không tạo trong ticket review này.
