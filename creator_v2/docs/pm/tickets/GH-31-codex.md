# GH-31 · Codex: Trend Engine P0 (scanner read-only)

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/31. Đọc kỹ `docs/pm/2026-11-02-trend-engine-v1.md`, mục P0.

## Được ghi
- `factory/trend/__init__.py`, `sources.py`, `sources.json`, `scan.py`, `cluster.py`, `independence.py`, `report.py`, `__main__.py`
- `tests/test_trend_*.py`
- `tests/fixtures/trend/`: các mẫu RSS/JSON đã lưu, cùng bộ 40 bài gán nhãn sự kiện
- `.gitignore`: thêm `data/trend/` và `output/trend/`
- báo cáo `docs/pm/tickets/GH-31-report.md`

**Không:** sửa code khác, đụng `state.sqlite` hay lịch, dùng yt-dlp hoặc Google autocomplete, thêm dependency ngoài stdlib, gọi API trả phí, commit.

## Việc
1. **`sources.json`.** Mỗi mục có các trường `id`, `url`, `kind` (`rss` | `json_hn` | `json_reddit` | `wiki_pageviews`), `owner_group`, `channels` (`["MIM"]`, `["CK"]` hoặc cả hai), `tos_status`, `tos_note`.
   - Tạm để mọi mục `tos_status: "pending"`. Grok đang rà điều khoản song song, Lead sẽ cập nhật sau.
   - `scan.py` **chỉ gọi** nguồn `ok`; có test chứng minh.
2. **`scan.py`.**
   - Dùng urllib, timeout 20 s, User-Agent nhận diện rõ, gọi tuần tự với nghỉ giữa các nguồn.
   - Parse RSS 2.0/Atom bằng `xml.etree`.
   - Nguồn lỗi thì ghi vào bảng `run`, rồi chạy tiếp.
   - Lưu `article`: url (unique), title, summary ≤ 300 ký tự, published_at, source_id, owner_group, fetched_at.
   - CSDL `data/trend/trend.sqlite`.
3. **`cluster.py`.** Gom bài trong cửa sổ 48 h thành sự kiện, tất định, không LLM.
   - Trích thực thể: cụm viết hoa hoặc tên riêng, mã, số kèm đơn vị (tỷ, triệu, USD, %).
   - Chuẩn hóa: bỏ dấu, lowercase, có bảng alias nhỏ.
   - Gom khi chung thực thể quan trọng và token Jaccard ≥ ngưỡng.
   - Ngưỡng chỉnh trên fixture 40 bài: precision ≥ 0,8, ghi số đo vào báo cáo.
   - Bảng `event`: id, label, entities, first_seen, last_seen, article_ids.
4. **`independence.py`.** `independent_sources` = số `owner_group` khác nhau. Tiêu đề gần trùng (bài dẫn lại) không tính thêm. Có test.
5. **`report.py`.** Ghi `output/trend/<YYYY-MM-DD>/<HH>.md`: top 20 sự kiện mỗi kênh, xếp theo số nguồn độc lập 24 h rồi đến tốc độ (bài 3 h so với trung bình 24 h). Mỗi sự kiện có giờ thấy lần đầu và các URL.
6. **CLI** `python -m factory.trend scan|report|run`, có gọi `utf8_console`. `run` = scan + cluster + report, mục tiêu ≤ 5 phút.
7. **Test** chạy offline bằng fixture: parse, chỉ gọi nguồn ok, cluster precision, độc lập, report. Chạy `python -m pytest -q -p no:cacheprovider tests/test_trend_*.py`; nếu sandbox chặn tmp thì ghi lại.
8. Bật tạm 2 nguồn công khai ít rủi ro là Hacker News API và Wikipedia pageviews, chỉ trong **một lần chạy thử thủ công** (biến môi trường `TREND_FORCE_SOURCES`). Ghi kết quả vào báo cáo. Không đổi `tos_status` trong file.

## Báo cáo
Cấu trúc, cách gom sự kiện, số precision, lệnh, kết quả test, output chạy thử, rủi ro.
