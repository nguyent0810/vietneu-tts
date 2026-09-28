# 19: Concentration signal từ Quality record (advisory)

**Spec:** `../spec-2.md`, mục Opening pattern và concentration (S12/S13). Quyết định: D71, D72, D73, D86, D87.

**What to build:** Sau khi một Short qua S7, hệ thống đọc các Quality record PASS `layer: script` gần nhất của cùng Domain (window tính theo số lượng, kích thước là tham số), tính tỷ trọng theo fingerprint, và ghi một record `layer: catalog` dạng advisory. Mô tả Opening pattern tự do (nếu đã có từ ticket 17) được giữ nguyên trong dữ liệu để chuẩn hoá sau khi có baseline.

**Blocked by:** 14

**Status:** ready-for-agent

- [ ] Đọc record từ kho Quality record; không có store mới, không dùng khoá chỉ có trên Unix
- [ ] Window tính theo số lượng record PASS của Domain; kích thước là tham số, không phải ngưỡng
- [ ] Tỷ trọng theo fingerprint đúng trên tập record fixture
- [ ] Record `layer: catalog` không có cờ đạt/không đạt, không có ngưỡng, không whitelist hay blacklist
- [ ] Test khẳng định không có đường nào từ signal tới Gate status hay tới prompt của writer
- [ ] Chạy được trên Windows
