# Benchmark đối kháng #123 — 5 chủ đề × 12 gói (20 tốt, 40 cố ý sai), đóng băng tại ~/vietneu_bench_frozen/adv123 (SHA256SUMS d62ab4ec…)

| Lượt | Thay đổi | False PASS (40 sai) | False REJECT (20 tốt) | Tốt được PASS | Extractor chưa đủ | Token trích |
|---|---|---|---|---|---|---|
| run2 | gate v3 ban đầu, driver tách từng gói | **0** | 2 | 0/20 | 0/60 | ~323k |
| run3 | Codex vòng sửa 1 (polarity, bỏ REJECT rơi, thời gian, series, entity_id) | **0** | **0** | 0/20 | 10/60 | ~411k |
| run4 | Lead vòng sửa 2 (đại lượng có kiểm soát, đối tượng theo kiểu quan hệ, siết entity_id) | **0** | 1 (Huế "hơn 100 m": extractor bỏ sót "hơn") | 0/20 | 36/60 | ~301k |

REVIEW run4 theo lý do (số claim): không có fact khớp 128 · thực thể mơ hồ 74 · extractor chưa đủ 36 gói · dị bản chưa quy kết 17 · thiếu khung modality 15 · lệch phạm vi 10 · fact chưa xác minh 9 · lời hứa không có fact 1.
Gói cố ý sai bị REJECT (run4): owns_to_compromised, implied_false_claim, rounding_abuse (3/40); 37 còn lại REVIEW.

Nhận định:
- An toàn: qua 3 lượt chưa có false PASS nào.
- Chưa dùng được: 0/20 gói tốt PASS. Nút thắt không còn ở gate mà ở (a) độ phủ của Fact Store — packaging chứa nhiều khẳng định mô tả/kể chuyện không có fact tương ứng (128 claim); (b) extractor: càng siết liên kết thực thể thì càng tự báo "chưa đủ" (10 → 36 gói), kéo cả gói về REVIEW; (c) REJECT phụ thuộc extractor bắt đúng từ làm tròn ("hơn") — cần chốt chặn: span có từ xấp xỉ mà marker trống thì chỉ REVIEW.
