# #125 Simplified source-grounded review — kết quả pilot (03/11)
Reviewer: Codex CLI (gpt-6-luna), batch 6 gói/lượt. Creative: Claude Sonnet (15 gói của #124). Lượt chính thức: simple_run2 (sau khi sửa đọc token).

| Ngưỡng PO | adv123 (60, thiếu trường) | heldout124 (40) | heldout125 (30, lỗi ngụ ý) | Đạt |
|---|---|---|---|---|
| False acceptance = 0 | 0/40 | 0/20 | 0/15 | ĐẠT |
| Chấp nhận gói tốt ≥ 50% | 0/20 (tự chuyển người vì thiếu trường) | 6/20 = 30% | 5/15 = 33% | KHÔNG |
| Chuyển người ≤ 50% gói tốt | 20/20 | 14/20 = 70% | 10/15 = 67% | KHÔNG |
| Gói sai: REJECT / chuyển người | 11 / 29 | 3 / 17 | 4 / 11 | — |
| ≤ 15k token/gói chấp nhận | — | 219k review / 6 = 36,6k | 156k / 5 = 31,2k | KHÔNG |
| Không crash | 0 crash trong chạy thật | | | ĐẠT (nhưng review chỉ ra P1 crash với record không phải dict) |
| Review Codex không P1 | | | | KHÔNG (FAIL, 3 P1) |

Precision ACCEPT: 11/11 gói ACCEPT trên bộ có đáp án đều là gói tốt. Creative 15: 3 ACCEPT, Lead kiểm: 3/3 đúng dữ kiện, 1 gói lỗi thời ("tháng 11/2024") — đúng nhưng không đăng được.
Token theo công đoạn: creative ~8k/gói; review ~5–7k/gói (một lượt Codex rỗng đã ~18k input, batch 6 chia còn ~3k/gói); tính cả creative, mỗi gói được chấp nhận ~75k (creative15: 225k/3).
Bỏ sót ngụ ý (heldout125): không gói sai nào được ACCEPT, nhưng reviewer chỉ REJECT dứt khoát 4/15; 11/15 đẩy sang người.
Review Codex (FAIL): ACCEPT được dù không có nguồn/nguồn bị cắt (cờ không vào decide); nguồn mâu thuẫn chưa verified bị loại khỏi gói gửi reviewer; record không phải dict làm crash; P2: "3.5" đọc thành 35, số không đơn vị khớp lỏng, citation fact_id không được kiểm.
Kết luận STOP RULE: không mở vòng vá tự động. Giữ Creative LLM + reviewer dựa trên nguồn làm CÔNG CỤ HỖ TRỢ, người duyệt trước production.
