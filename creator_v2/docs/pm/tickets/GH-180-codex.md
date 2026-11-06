# GH-180: script đánh giá luật dừng 5 Short/ngày của CK

**Bối cảnh:** CK chạy thử 5 Short/ngày từ 29/10 tới 11/11. Luật dừng: nếu lượt xem mỗi Short **dưới 60% mức 20–26/10 (median 322)**, tức dưới 193, thì quay về 2–3 Short/ngày. Phân tích cũ cho thấy 92–100% lượt xem của một Short CK đến trong 3 ngày đầu. Ngày 12/11 Lead sẽ kéo số liệu mới rồi chạy script này.

**Dữ liệu (chỉ đọc):** `data/analytics/CK/183/`. Script kéo là `scripts/analytics_pull_183.py`, bạn không chạy nó.
- `videos.json`: id, title, published_at, duration, privacy.
- `video_x_day.json`: lượt xem theo ngày của từng video, từ 1 ngày trước tới 8 ngày sau khi đăng.
- `byvideo_d28.json`, `byvideo_d7.json`.

**Việc:** viết `scripts/ck_stop_rule_180.py [--data data/analytics/CK/183] [--trial 2026-10-29:2026-11-11] [--base 2026-10-20:2026-10-26] [--base-median 322] [--ratio 0.6] [--days 3] [--out docs/pm/2026-11-12-ck-stop-rule.md]`.
1. Short là video có duration ≤ 3 phút (PT…S), privacy public.
2. Với mỗi Short: tính lượt xem trong `--days` ngày đầu (ngày đăng + 2 ngày theo giờ VN, UTC+7) từ `video_x_day.json`. Short chưa đủ tuổi (ngày cuối có dữ liệu < ngày đăng + days − 1) thì đánh dấu "chưa đủ tuổi" và không tính vào median.
3. Tính median và số Short của:
   - nhóm thử (đăng trong khoảng `--trial`);
   - nhóm gốc (`--base`), để so với 322 đã ghi; nếu lệch nhiều thì ghi rõ.
4. Kết luận: median nhóm thử < ratio × base-median → "DỪNG: quay về 2–3/ngày", ngược lại → "GIỮ 5/ngày".
   - Ghi thêm tổng lượt xem 3 ngày mỗi tuần và số Short mỗi tuần, để thấy tác động của khối lượng.
   - Nhóm thử có dưới 20 Short đủ tuổi thì ghi "chưa đủ dữ liệu".
5. Xuất Markdown tiếng Việt ra `--out`: bảng tóm tắt, top 5 và bottom 5 Short (tiêu đề, lượt xem 3 ngày), các giới hạn dữ liệu. Không suy ngược số thiếu.
6. Test `scripts/test_ck_stop_rule_180.py` (để trong scripts/, Lead sẽ chuyển sang tests/), dùng dữ liệu giả nhỏ:
   - tính đúng cửa sổ 3 ngày theo giờ VN;
   - bỏ Short chưa đủ tuổi;
   - kết luận DỪNG và GIỮ ở hai phía ngưỡng;
   - trường hợp dưới 20 Short.
7. Chạy thử trên dữ liệu thật hiện có (kéo ngày 05/11), ghi kết quả tạm vào báo cáo.

**Được ghi:** `scripts/ck_stop_rule_180.py`, `scripts/test_ck_stop_rule_180.py`, `docs/pm/2026-11-12-ck-stop-rule.md` (bản chạy thử), và báo cáo `docs/pm/tickets/GH-180-report.md`, ghi bằng Python với `encoding="utf-8"` (không dùng PowerShell Set-Content). Không commit, không gọi API.
