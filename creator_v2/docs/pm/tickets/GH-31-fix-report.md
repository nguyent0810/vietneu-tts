# GH-31 — báo cáo vòng sửa Codex

## Đã làm

- Thay `factory/trend/sources.json` bằng toàn bộ cấu hình từ `GH-31-sources.json`, giữ nguyên mọi metadata ToS, owner group và kênh. File đầu vào thực tế có **46** mục (13 `ok`, 17 `pending`, 16 `blocked`), không phải 45 như mô tả brief; báo cáo giữ nguyên 46 mục đó. Thêm `role`: `google_trends_vn`, `wikipedia_pageviews_vi`, `wikipedia_pageviews` là `signal`; 43 mục còn lại là `article`.
- Bỏ cơ chế ép chạy nguồn bằng biến môi trường. Scanner chỉ gọi nguồn có `tos_status: ok`; `pending`/`blocked` luôn là “không gọi”.
- Thêm parser RSS/Atom, Hacker News Firebase (tối đa 60 story), Google Trends RSS, Wikipedia pageviews lịch sử 8 ngày, GDELT với `owner_group` là hostname gốc của URL bài báo; timeout là 20 giây và User-Agent có placeholder email.
- Wikipedia và Trends chỉ đi vào bảng `signal`, không thể tạo `article` hay event. Lọc namespace như `Special:`, `Wikipedia:`, `File:`, `Main_Page`, `Trang_Chính`.
- Thêm `keywords.json`, lọc kênh theo cả `channels` của nguồn lẫn từ khóa trụ cột. Báo cáo tối đa 20 event/kênh, chỉ liệt kê event đã có URL article/nguồn sơ cấp, và đính signal trùng thực thể.
- Thêm migration SQLite cho cột `event.signals`, để database của vòng trước không làm hỏng lần chạy mới. Mỗi scan dọn cửa sổ article/signal/event cũ trước khi ingest, tránh lặp lại 943 event Wikipedia từ vòng trước.
- Thêm/cập nhật test fixture offline cho signal-only, namespace, GDELT domain độc lập, ToS gate và keyword gate.

## Lệnh đã chạy và kết quả

```text
python -m pytest -q -p no:cacheprovider tests/test_trend_scanner.py
# 6 passed in 0.19s

python -m py_compile <mọi file factory/trend/*.py>
# đạt

python -m factory.trend run
# quét thật chỉ 13 nguồn ok; sau migration chạy cluster/report cục bộ,
# không gọi mạng thêm:
# cluster: 476
# report: output/trend/2026-11-02/11.md
```

Lưu ý: PowerShell không bung `factory/trend/*.py` khi truyền thẳng cho Python; lệnh kiểm tra biên dịch cuối cùng đã dùng danh sách file đã resolve.

Không có linter riêng được ticket chỉ định; không còn lỗi lint/compile nội bộ.

## Kết quả lượt quét thật

- Article: **495**; signal: **985**; event thô: **476**.
- Báo cáo hiển thị **20** event MIM và **15** event CK (đều không vượt trần 20); số URL Wikipedia trong báo cáo event: **0**.
- Năm event MIM đầu: `devfest`; `a2ui · build generative ui apps`; `google play · gpu`; `a working prototype · building conversational commerce`; `drive · google docs`.
- Năm event CK đầu: `april · federal open market committee`; `federal reserve · fomc`; `federal open market committee · federal reserve board`; `federal open market committee · june`; `federal reserve`.
- Bảng trạng thái 46 nguồn nằm cuối báo cáo. Tất cả 17 `pending` và 16 `blocked` là `không gọi`.

Ba lỗi endpoint trong lượt quét được ghi vào bảng `run`; các nguồn còn lại tiếp tục chạy:

- `gdelt_vi_news`: HTTP 429.
- `google_trends_vn`: phản hồi không phải JSON/XML hợp lệ (`Expecting value`).
- `wikipedia_pageviews_vi`: HTTP 404.

## Khẳng định/chứng cứ chưa kiểm được

Không có khẳng định nội dung video hay factcheck trong ticket này. Ba endpoint lỗi ở trên chưa thể kiểm lại trong sandbox; Lead có thể dùng bảng trạng thái của report để chạy nghiệm thu ngoài sandbox.

## Đường dẫn bàn giao

- Báo cáo trend: `output/trend/2026-11-02/11.md`
- Clip sheet/thumbnail: không áp dụng cho ticket pipeline này.

Không truy cập hoặc thay đổi `state.sqlite`, lịch, YouTube, credential; không commit hoặc publish.
