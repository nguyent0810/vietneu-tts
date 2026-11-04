# GH-31 · Grok vòng 2: kiểm 3 feed thử, rà VietNamNet, benchmark độc lập, nguồn quốc tế

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/31. Chủ kênh chốt 02/11 (xem `docs/pm/2026-11-02-trend-engine-v1.md`, mục "Nguồn P0" và "Nghiệm thu P0"). Vòng trước: `docs/pm/tickets/GH-31-grok-report.md`, `GH-31-sources.json`.

## Được ghi
- `docs/pm/tickets/GH-31-benchmark.json`
- `docs/pm/tickets/GH-31-sources-v2.json`: chỉ chứa các mục thay đổi hoặc mới
- báo cáo `docs/pm/tickets/GH-31-grok2-report.md`

**Không:** đọc `output/trend/`, `data/trend/` hay `docs/pm/tickets/GH-31-fix*-report.md`, vì benchmark phải độc lập với kết quả scanner. Cũng không sửa code, đọc credentials hay commit.

## Việc
1. **Kiểm 3 feed thử nội bộ:** `thanhnien_cong_nghe`, `thanhnien_kinh_te`, `genk_tin_ict`. Mỗi feed ghi:
   - URL feed thật còn chạy và số item;
   - `robots.txt` của domain có `Disallow` nào chạm đường dẫn RSS không, có `Crawl-delay` không (trích dòng liên quan);
   - điều khoản có câu nào cấm bot hay khai thác tự động không (trích ≤ 25 từ, kèm URL);
   - giới hạn truy cập đề xuất (vd. ≤ 1 request mỗi feed mỗi 3 h).

   Kết luận `trial_ok` hoặc `blocked`. Feed nào bị robots.txt hoặc điều khoản cấm bot thì phải là `blocked`.
2. **VietNamNet:** rà tiếp điều khoản, robots.txt và trang RSS, kết luận `trial_ok`, `pending` hoặc `blocked`. CafeF giữ `pending`, không rà.
3. **Nguồn quốc tế được phép**, có tin tác động tới VN. Ví dụ cần rà:
   - RSS của Reuters, AP, BBC, The Verge, Ars Technica, TechCrunch, CoinDesk;
   - World Bank, IMF, ADB;
   - The Register, Krebs on Security, BleepingComputer (MIM: bảo mật/hack);
   - CISA advisories (công cộng).

   Mỗi nguồn ghi `tos_status` (ok/pending/blocked), robots.txt, `owner_group`, kênh. Đề xuất cách lọc "tác động tới Việt Nam": từ khóa (Vietnam, VND, Việt Nam, tên doanh nghiệp VN, ASEAN), hoặc chủ đề toàn cầu chạm người dùng VN (sự cố dịch vụ lớn, hack sàn crypto, giá vàng/dầu, Fed, chính sách của các nền tảng).
4. **Benchmark sự kiện nóng độc lập.** Lập danh sách sự kiện thật xảy ra hoặc được đưa tin trong 72 h gần nhất (31/10–02/11/2026), tự tìm bằng web/X/tin tức:
   - MIM ≥ 15 sự kiện: AI, công nghệ, bảo mật, nền tảng;
   - CK ≥ 15 sự kiện: tiền bạc, giá vàng, lãi suất, thuế, BHXH, chứng khoán VN, chính sách tác động tới túi tiền người VN.

   Mỗi sự kiện có các trường:
   - `id`, `channel`, `label`
   - `entities`: 2–4 thực thể nhận diện
   - `first_reported`: thời điểm đưa tin sớm nhất
   - `urls`: ≥ 2 URL từ hai `owner_group` khác nhau
   - `hotness`: high/medium, lý do một dòng
   - `angle`: góc khai thác cho kênh

   Sự kiện chạm cả hai kênh thì ghi cả hai góc. Ghi rõ cách tìm (truy vấn, trang), để Lead đo recall: scanner bắt được bao nhiêu sự kiện benchmark.

## Báo cáo
Bảng 3 feed thử, kết luận VietNamNet, bảng nguồn quốc tế, cách lọc tác động VN, mô tả benchmark (số sự kiện mỗi kênh, phân bố hotness).
