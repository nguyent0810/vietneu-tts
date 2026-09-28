# 12: Tín hiệu chẩn đoán bằng code + fingerprint

**Spec:** `../spec-2.md`, mục Tín hiệu chẩn đoán (S10) và phần fingerprint của S12. Quyết định: D63, D68, D86.

**What to build:** Các hàm thuần tính tín hiệu chẩn đoán từ script: số từ câu đầu, độ dài từng câu, số câu, tổng số từ, mật độ số, tên và thuật ngữ theo từng câu, fingerprint N từ đầu đã chuẩn hoá (N là tham số cấu hình). Thêm một hàm nhận span chi tiết móc và trả về Khoảng cách tới điểm móc, gồm số từ đứng trước span và số giây quy ra theo cả 170 và 200 wpm. Tất cả chỉ là dữ liệu đo, không có trường điểm và không có ngưỡng.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Có số từ câu đầu, độ dài từng câu, số câu và tổng số từ, tính trên text sẽ được đọc
- [ ] Có mật độ số, tên và thuật ngữ theo từng câu; cách nhận diện được ghi rõ và có version
- [ ] Fingerprint N từ đầu đã chuẩn hoá, ổn định giữa các lần chạy; N là tham số
- [ ] Hàm Khoảng cách tới điểm móc nhận span, trả về số từ và số giây ở 170 và 200 wpm; span không hợp lệ thì báo lỗi rõ
- [ ] Kết quả không có trường điểm, không có ngưỡng, không có cờ đạt hoặc không đạt
- [ ] Hàm thuần, test chạy được trên Windows
