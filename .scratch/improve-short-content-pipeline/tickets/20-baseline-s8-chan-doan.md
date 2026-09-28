# 20: Chạy S8 + chẩn đoán code trên script baseline

**Spec:** `../spec-2.md` (Further Notes: tạo dữ liệu baseline trước anchor). Quyết định: D78, D79, D80, D81.

**What to build:** Một lệnh thủ công chạy S8 (ticket 11) và các tín hiệu chẩn đoán bằng code (ticket 12) trên script của Baseline snapshot (ticket 10). Kết quả là báo cáo phân bố theo Domain: tỷ lệ lặp câu, markup sót, câu cụt, số từ câu đầu, độ dài câu, mật độ, fingerprint. Báo cáo chỉ dùng làm dữ liệu cho calibration sau này.

**Blocked by:** 10, 11, 12

**Status:** ready-for-agent

- [ ] Chỉ dùng script có `script_provenance` là `exact`, `revision` hoặc `rendered`
- [ ] Tuyệt đối không dùng `source_only`; test khẳng định Short `source_only` bị loại
- [ ] n được tính theo từng tiêu chí (chỉ đếm Short chấm được tiêu chí đó), không ghi một n chung
- [ ] Báo cáo tách theo `script_provenance` và theo Domain
- [ ] `rendered` không kiểm tra markup sót (đã bị strip), và báo cáo ghi rõ lý do bị loại khỏi n của tiêu chí đó
- [ ] Tín hiệu chẩn đoán không trở thành điểm; báo cáo không tự tạo threshold hay đánh giá đạt/không đạt
- [ ] Kết quả ghi vào vùng baseline bị gitignore, có version và thời điểm tạo
- [ ] Test với fixture nhỏ cho từng loại provenance
