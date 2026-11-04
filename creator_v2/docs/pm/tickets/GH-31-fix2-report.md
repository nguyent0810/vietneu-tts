# GH-31 fix 2 — báo cáo Codex

## Đã thay đổi

- `factory/trend/sources.json`: Google Trends VN dùng endpoint RSS mới, có vai trò `article+signal`; GDELT dùng đúng một endpoint JSON `sourcecountry:VM`; các feed SEC, Google blog, arXiv, NIST, Fed và BLS chuyển sang `primary`.
- `factory/trend/scan.py`: tách `ht:news_item` thành article chỉ gồm tiêu đề, URL và publisher/domain; lưu `undated` khi dùng `fetched_at`; nhận JSON GDELT rỗng; đợi 5 giây trước request GDELT; Wikipedia lùi về ngày trước nữa khi dữ liệu ngày hôm qua chưa sẵn sàng.
- `factory/trend/cluster.py` và `report.py`: chỉ cluster bài không quá 72 giờ và không phải `primary`; report tách NÓNG/THEO DÕI/SƠ CẤP MỚI, giới hạn 15/5/5, xếp NÓNG theo nguồn độc lập → traffic Trends → tốc độ. Khớp keyword theo token để `ai` không khớp nhầm vào `hai`; loại nhãn nhiễu.
- Thêm fixture RSS Trends VN đã ghi từ lần chạy và test cho news item/publisher, BOM, 72 giờ, primary, GDELT JSON rỗng và fallback Wikipedia.

## Lệnh kiểm và kết quả

- `python -m pytest tests/test_trend_scanner.py -q -p no:cacheprovider` → **11 passed**.
- `python -m compileall -q factory/trend` → thành công.
- `python -m factory.trend run` → lần chạy kiểm cuối trên các nguồn `ok`: **10 nguồn thành công, 217 articles, 1.976 signals, 3 errors; 71 events**. Kết quả được xác nhận từ bảng `run` và report sau khi tiến trình hoàn tất.

Lỗi còn lại trong lần quét: `google_devs_blog_rss` và `arxiv_cs_ai` không phân giải được DNS (`getaddrinfo failed`); `gdelt_vi_news` hết thời gian đọc. GDELT vẫn đã chờ 5 giây trước request; JSON rỗng được test là trạng thái thành công.

## Kết quả biên tập

- NÓNG MIM: **1** — `google` (tối đa 5 đầu: chỉ có 1).
- NÓNG CK: **0** — không có event để liệt kê.
- Đường dẫn report/clip sheet: `output/trend/2026-11-02/11.md`.
- Thumbnail: không áp dụng cho ticket scanner này.

P0 **chưa đạt** mục tiêu “ít nhất 10 event mỗi kênh có URL”: MIM 1/10, CK 0/10. Không có nguồn `pending` hoặc `blocked` nào được gọi. Ước tính cần tối thiểu ba nguồn tin Việt Nam đã được review ToS mỗi kênh để có cơ hội đạt mật độ đó: MIM nên ưu tiên `thanhnien_cong_nghe`, `genk_tin_ict`, `vietnamnet_cong_nghe`; CK nên ưu tiên `thanhnien_kinh_te`, `cafef_tai_chinh`, `cafef_vi_mo`, `vietnamnet_kinh_doanh`. Đây chỉ là đề xuất review/bật nguồn; ticket không cho phép thay đổi `tos_status`.

Không có khẳng định nội dung video nào cần fact-check trong ticket này. Không đổi lịch, không đụng YouTube, credential, `state.sqlite` hay git.
