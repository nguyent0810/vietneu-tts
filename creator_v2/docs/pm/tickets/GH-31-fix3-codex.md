# GH-31 · Codex vòng sửa 3 P0: 3 feed thử nội bộ, bộ đếm mới, đo recall theo benchmark

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/31.

Chủ kênh chốt 02/11 (`docs/pm/2026-11-02-trend-engine-v1.md`, mục "Nguồn P0" và "Nghiệm thu P0"):
- bật một phần nguồn;
- nghiệm thu là ≥ 10 **ứng viên liên quan** mỗi kênh trong 72 h, không phải ≥ 10 tin NÓNG;
- tỷ lệ phát hiện đo trên benchmark độc lập.

Đầu vào:
- `docs/pm/tickets/GH-31-sources-v2.json`: Grok vòng 2. 3 feed `ok`: `thanhnien_cong_nghe`, `thanhnien_kinh_te`, `genk_tin_ict`. VietNamNet `pending`. Nguồn quốc tế `blocked`/`pending`.
- `docs/pm/tickets/GH-31-grok2-report.md`: robots.txt và giới hạn truy cập.
- `docs/pm/tickets/GH-31-benchmark.json`: 38 sự kiện, MIM 18, CK 20.

## Được ghi
- `factory/trend/*`, gồm file mới `factory/trend/benchmark.py`
- `tests/test_trend_*.py`
- `tests/fixtures/trend/`
- báo cáo `docs/pm/tickets/GH-31-fix3-report.md`

**Không:** bật nguồn nào khác ngoài 3 feed trên (VietNamNet và CafeF giữ `pending`), đổi `tos_status` của nguồn khác, sửa benchmark, render, đổi lịch, commit, dùng yt-dlp hoặc autocomplete.

## Việc
1. **3 feed thử.** Gộp các mục thay đổi từ `GH-31-sources-v2.json` vào `factory/trend/sources.json`:
   - 3 feed giữ `tos_status: ok`, thêm `trial: "internal"`;
   - các nguồn quốc tế mới giữ đúng trạng thái Grok ghi, nên không được gọi.
2. **Giới hạn truy cập.** Đọc `robots.txt` của domain lúc chạy, cache 24 h:
   - đường dẫn feed bị `Disallow` → không gọi, ghi `run` = `robots_blocked`;
   - có `Crawl-delay` thì tôn trọng;
   - mỗi feed tối đa 1 request mỗi 3 h, nhớ thời điểm gọi trong `trend.sqlite`, chạy lại sớm thì bỏ qua và ghi `rate_skip`;
   - User-Agent nhận diện rõ.
3. **Bộ đếm báo cáo mỗi kênh**, ghi ở đầu báo cáo:
   - **bài:** số article của kênh trong 72 h;
   - **sự kiện hợp lệ:** event có nhãn ≥ 1 thực thể ngoài stoplist và ≥ 1 URL;
   - **ứng viên liên quan:** sự kiện hợp lệ khớp từ khóa trụ cột của kênh, trong 72 h. Nghiệm thu: ≥ 10 mỗi kênh;
   - **sự kiện nóng:** ≥ 2 nguồn độc lập trong 24 h, hoặc có tín hiệu Google Trends VN;
   - **cơ hội sản xuất:** ứng viên liên quan có chất liệu hook theo mẫu thắng tuần 44 (tên người hoặc tổ chức cụ thể, kèm ≥ 1 con số có đơn vị trong tiêu đề hay tóm tắt). Chỉ là cờ sơ bộ, không phải VOS.

   Báo cáo liệt kê ứng viên liên quan (tối đa 25 mỗi kênh), mỗi mục có cờ `nóng` / `cơ hội`.
4. **Lọc tác động VN** cho nguồn `primary` quốc tế (SEC, Fed, BLS, NIST, arXiv) và các nguồn quốc tế được bật về sau. Chỉ vào ứng viên khi khớp bộ từ khóa `vn_impact` trong `keywords.json`: Vietnam, Việt Nam, VND, ASEAN, tên doanh nghiệp VN; hoặc chủ đề toàn cầu chạm người VN như hack sàn crypto, sự cố nền tảng lớn, giá vàng/dầu, Fed lãi suất, chính sách Apple/Google/Meta/TikTok. Có test.
5. **`benchmark.py`:** `python -m factory.trend benchmark docs/pm/tickets/GH-31-benchmark.json`.
   - Một sự kiện benchmark coi là **bắt được** khi có ứng viên liên quan cùng kênh trùng ≥ 2 thực thể, hoặc trùng 1 thực thể kèm URL cùng domain, trong cửa sổ ±48 h quanh `first_reported`.
   - In recall mỗi kênh, recall theo `hotness` (high/medium), danh sách bỏ lỡ kèm lý do sơ bộ: không có nguồn đưa tin, bị lọc từ khóa, hoặc không gom được.
   - Không sửa benchmark. Không dùng benchmark để chỉnh tham số rồi báo là đạt. Nếu có chỉnh ngưỡng thì ghi rõ trước/sau.
6. **Test offline:** robots `Disallow`, `rate_skip`, bộ đếm, lọc `vn_impact`, logic so khớp benchmark (fixture nhỏ).
7. **Chạy kiểm chứng.** Chạy `python -m factory.trend run` rồi `benchmark`, ghi 4 số mỗi kênh và recall. Sandbox chặn mạng hay DNS thì ghi lại; Lead sẽ chạy 3 lần nghiệm thu ngoài sandbox.

## Báo cáo
Thay đổi, test, bảng 4 số mỗi kênh, recall và danh sách bỏ lỡ, rủi ro.
