# GH-31 — báo cáo Codex

## Đã làm

- Thêm `factory/trend/` với scanner chỉ đọc bằng stdlib (`urllib`, `xml.etree`, `sqlite3`), SQLite tại `data/trend/trend.sqlite`, gom sự kiện, lọc nguồn độc lập, xuất Markdown và CLI `python -m factory.trend scan|report|run` (có `utf8_console`).
- Thêm `sources.json`. Cả ba nguồn đều giữ `tos_status: "pending"`; bình thường scanner không gọi chúng. Biến `TREND_FORCE_SOURCES` chỉ là cơ chế ép tạm theo ID cho lần thử thủ công.
- Thêm fixture RSS, JSON Wikipedia và bộ 40 bài đã gán nhãn (20 cặp sự kiện), cùng test parse, ToS gate, clustering, independence và report.
- Thêm `data/trend/` và `output/trend/` vào `.gitignore`.

## Gom sự kiện

- Chuẩn hóa bỏ dấu, lowercase, bảng alias nhỏ; trích cụm viết hoa/tên riêng và số có đơn vị.
- Hai bài nối cùng sự kiện khi cùng thực thể không chung chung, Jaccard token tiêu đề >= 0,25 và cách nhau không quá 48 giờ. Thành phần liên thông tạo một event tất định.
- Trên fixture 40 bài: 20 cụm dự đoán, mọi cụm đều thuần một nhãn; precision = **1,00** (>= 0,80).
- `independent_sources` gộp tiêu đề gần trùng trước, rồi chỉ đếm `owner_group` khác nhau.

## Lệnh và kết quả

```text
python -m pytest -q -p no:cacheprovider tests/test_trend_*.py
```

PowerShell không bung wildcard này cho pytest nên báo không tìm thấy đường dẫn. Khi gọi file rõ ràng, sandbox chặn pytest tạo/xóa `tmp_path` trong thư mục Temp của người dùng (`WinError 5`). Bốn test không cần thư mục tạm đạt (`4 passed, 2 deselected`). Hai test còn lại đã được gọi trực tiếp với fixture và thư mục `data/trend/test-direct-2`, đạt: `2 fixture-backed scanner/report checks passed`.

```text
python -m py_compile <mỗi file factory/trend/*.py>
python -m factory.trend --help
```

Đều đạt. Không còn lỗi lint nội bộ; ticket không chỉ định một linter riêng.

Lần chạy thử thủ công duy nhất, với đúng hai nguồn được phép tạm thời:

```text
TREND_FORCE_SOURCES=hacker_news,wikipedia_pageviews
python -m factory.trend run
# scan: 1 sources, 1000 articles, 1 errors
# cluster: 943 events
# report: output/trend/2026-11-02/10.md
```

Chạy mất khoảng 1,6 giây. Wikipedia pageviews thành công và tạo [báo cáo thử](../../../output/trend/2026-11-02/10.md). Hacker News lỗi DNS `getaddrinfo failed`; lỗi đã có hàng `run` với `status=error`, còn pipeline vẫn cluster và report. Không đổi `tos_status`, không đụng `state.sqlite`, lịch, YouTube hay credential.

## Rủi ro / việc còn lại

- ToS chưa được Lead/Grok xác nhận: ở trạng thái bình thường lần chạy sẽ không gọi nguồn nào và báo cáo trống. Chỉ Lead nên đổi từng nguồn sang `ok` sau khi rà điều khoản.
- Hacker News cần kiểm lại DNS/network trước nghiệm thu ba lần chạy liên tiếp.
- Báo cáo P0 là tín hiệu biên tập read-only; chưa phải xác minh dữ kiện hoặc hàng xuất bản.
