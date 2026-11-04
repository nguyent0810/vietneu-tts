# GH-31 · Codex vòng sửa 2 P0: Google Trends VN là nguồn tin chính, lọc độ mới, tách "nóng" và "theo dõi"

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/31. Vòng trước: `docs/pm/tickets/GH-31-fix-report.md`.

## Lead đã chạy ngoài sandbox (02/11)
Kết quả: 7 nguồn, 437 bài, 6 lỗi, 22 s. Báo cáo chưa dùng được:
- MIM toàn bài arXiv và hồ sơ SEC, mỗi sự kiện chỉ 1 nguồn;
- CK toàn thông cáo FOMC/Fed cũ (tháng 4, 6, 7);
- không có tin Việt Nam.

Lead đã thử các endpoint:
- **Google Trends:** URL cũ hỏng. URL mới `https://trends.google.com/trending/rss?geo=VN` trả 200, có `<item>` là từ khóa xu hướng (`ht:approx_traffic`) và các `ht:news_item` (`ht:news_item_title`, `ht:news_item_url`, `ht:news_item_source`) trỏ bài báo VN. Hôm nay có các mục như "cổ phiếu fpt", "dự báo thời tiết đà nẵng".
- **GDELT:** yêu cầu tối đa 1 request mỗi 5 s. `query=sourcecountry:vietnam` hoặc `sourcelang:vietnamese` (JSON hoặc RSS, 24 h) trả rỗng. Không trông vào GDELT cho tin VN.
- **`file sources.json`** có BOM UTF-8. Đọc bằng `utf-8-sig`, hoặc ghi lại không BOM.

## Được ghi
- `factory/trend/*`
- `tests/test_trend_*.py`
- `tests/fixtures/trend/`
- báo cáo `docs/pm/tickets/GH-31-fix2-report.md`

**Không:** đổi `tos_status`, gọi nguồn `pending`/`blocked`, dùng yt-dlp hoặc autocomplete, thêm dependency, commit.

## Việc
1. **Google Trends VN** (`google_trends_vn`, ToS ok) đổi sang URL mới, `role: "article+signal"`:
   - mỗi `ht:news_item` → một `article`: tiêu đề, URL, `owner_group` = `ht:news_item_source` chuẩn hóa hoặc domain;
   - từ khóa xu hướng và `approx_traffic` → `signal`, gắn vào event chứa các news item đó;
   - chỉ lưu tiêu đề, URL và nguồn.
2. **GDELT.** Giữ nguồn, gọi đúng 1 request mỗi lần chạy, chờ ≥ 5 s trước khi gọi, nhận JSON rỗng mà không báo lỗi. Thử thêm `sourcecountry:VM` (mã FIPS của Việt Nam). Ghi số bài nhận được vào bảng `run`.
3. **Wikipedia vi 404.** Khi ngày hôm qua chưa có dữ liệu thì lùi về hôm kia. Kiểm lại URL theo dạng `.../per-article/vi.wikipedia/all-access/user/<title>/daily/<start>/<end>` hoặc `top/vi.wikipedia/all-access/<yyyy>/<mm>/<dd>`.
4. **Độ mới.** Bài có `published_at` cũ hơn 72 h thì không đưa vào event. Bài không có ngày thì dùng `fetched_at` và đánh dấu `undated`.
5. **Vai trò nguồn.** arXiv, SEC, NIST, Fed, BLS và Google blog gắn `role: "primary"`:
   - vẫn lưu, để P1 dùng làm nguồn sơ cấp khi factcheck;
   - không tự tạo mục "nóng".
6. **Báo cáo mỗi kênh, 3 phần:**
   - **NÓNG:** event có ≥ 2 nguồn độc lập trong 24 h, hoặc có tín hiệu Google Trends VN. Xếp theo số nguồn độc lập, rồi `approx_traffic`, rồi tốc độ. Tối đa 15.
   - **THEO DÕI:** event 1 nguồn, chỉ từ nguồn `article`. Tối đa 5.
   - **SƠ CẤP MỚI:** tiêu đề mới từ nguồn `primary` khớp từ khóa kênh. Tối đa 5.

   Bỏ các event có nhãn rỗng hoặc vô nghĩa, kiểu `co · deere`, `effect · filer`: nhãn phải có ≥ 1 thực thể không nằm trong stoplist.
7. **Test fixture.** Thêm một mẫu Trends RSS thật đã lưu, có `ht:news_item`. Test:
   - news item → article, `owner_group` theo nguồn;
   - lọc 72 h;
   - nguồn `primary` không vào phần NÓNG;
   - đọc file có BOM;
   - GDELT rỗng không làm lỗi.
8. Chạy thử 1 lần, ghi số event NÓNG mỗi kênh và 5 event đầu mỗi kênh.

## Báo cáo
Thay đổi, test, kết quả chạy thử. Nêu rõ: chỉ với các nguồn `ok`, P0 có đạt "≥ 10 event mỗi kênh có URL" hay không. Nếu không đạt, ghi ước tính cần bật thêm nguồn `pending` nào.
