# GH-31 fix3 — báo cáo Codex

## Đã thay đổi

- Gộp ba feed thử vào `factory/trend/sources.json`: `thanhnien_cong_nghe`, `thanhnien_kinh_te`, `genk_tin_ict` có `tos_status: ok` và `trial: "internal"`. URL GenK dùng `/rss/tin-ict.rss`.
- Bổ sung các nguồn quốc tế mới từ Grok v2 với đúng trạng thái `blocked`/`pending`; không nguồn nào trong số đó được bật. Các nguồn cũ không bị đổi `tos_status`.
- Bộ quét chỉ gọi nguồn vừa `ok` vừa có cờ `trial: internal`, nên chỉ ba feed thử được gọi. Thêm User-Agent định danh, cache `robots.txt` 24 giờ, kiểm `Allow`/`Disallow`, `Crawl-delay`, trạng thái `robots_blocked`, và giới hạn một feed/3 giờ với `rate_skip` lưu trong `data/trend/trend.sqlite`.
- Báo cáo trend có bộ đếm 72 giờ cho từng kênh: bài, sự kiện hợp lệ, ứng viên liên quan, sự kiện nóng, cơ hội sản xuất; liệt kê tối đa 25 ứng viên với cờ `nóng`/`cơ hội`.
- Thêm lọc `vn_impact` cho bài tiếng Anh: phải nêu trực tiếp Việt Nam/VND/ASEAN/doanh nghiệp VN hoặc khớp cặp thực thể toàn cầu + sự kiện có ảnh hưởng tại VN.
- Thêm `factory/trend/benchmark.py` và lệnh `python -m factory.trend benchmark <benchmark.json>`. Điều kiện bắt được: 2 thực thể trùng, hoặc 1 thực thể trùng và URL cùng domain, trong ±48 giờ.
- Thêm fixture benchmark nhỏ và test robots, rate limit, lọc tác động VN, so khớp benchmark. Không đổi ngưỡng clustering. Từ khóa trụ cột CK được bổ sung các chủ đề tài chính cá nhân/vĩ mô còn thiếu (điện, năng lượng, lợi nhuận, doanh thu, thu nhập, bất động sản, thanh khoản...); số ứng viên CK của cùng dữ liệu chạy từ 8 lên 28. Đây không phải tinh chỉnh theo benchmark; recall sau đó vẫn 0/20 vì ba feed thử không đưa tin về các sự kiện benchmark bị bỏ lỡ.

## Lệnh đã chạy

| Lệnh | Kết quả |
|---|---|
| `python -m pytest tests/test_trend_scanner.py -q -p no:cacheprovider` | 15 passed |
| `python -m compileall -q factory/trend` | thành công |
| `python -m factory.trend run` | 3 nguồn, 161 bài, 0 lỗi; 146 sự kiện; báo cáo đã tạo |
| `python -m factory.trend run` (chạy lại trong 3 giờ) | 0 nguồn, 0 bài, 0 lỗi; cả ba feed được `rate_skip` |
| `python -m factory.trend benchmark docs/pm/tickets/GH-31-benchmark.json` | kết quả bên dưới |

Không còn lỗi lint/test đã biết.

## Bộ đếm 72 giờ

| Kênh | Bài | Sự kiện hợp lệ | Ứng viên liên quan | Sự kiện nóng | Cơ hội sản xuất |
|---|---:|---:|---:|---:|---:|
| MIM | 113 | 105 | 16 | 0 | 4 |
| CK | 79 | 64 | 28 | 1 | 6 |

Clip sheet: không áp dụng (ticket engine xu hướng, không render video).

Trend report: `output/trend/2026-11-02/12.md`.

## Benchmark recall

| Kênh | Tổng | Bắt được | Recall | High | Medium |
|---|---:|---:|---:|---:|---:|
| MIM | 18 | 6 | 33,3% | 5/9 (55,6%) | 1/9 (11,1%) |
| CK | 20 | 0 | 0,0% | 0/14 (0,0%) | 0/6 (0,0%) |

Các mục MIM bỏ lỡ: `mim_01`, `mim_02`, `mim_06`, `mim_08`, `mim_11`, `mim_12`, `mim_13`, `mim_14`, `mim_15`, `mim_16`, `mim_17`, `mim_18` — lý do sơ bộ: không có nguồn thử nào đưa tin trong cửa sổ.

Các mục CK bỏ lỡ: `ck_01` đến `ck_20` — lý do sơ bộ: không có nguồn thử nào đưa tin trong cửa sổ.

## Rủi ro / ghi chú nghiệm thu

- Ba feed hiện chỉ có hai owner group độc lập (Thanh Niên và VCCorp), nên hầu hết sự kiện không đạt cờ nóng cần hai nguồn độc lập. Đây là giới hạn nguồn P0, không phải lỗi bộ đếm.
- Recall thấp là kết quả đúng của cấu hình chỉ ba feed và benchmark 38 sự kiện độc lập; không dùng benchmark để thay đổi ngưỡng rồi báo đạt.
- Cần Lead chạy ba lượt nghiệm thu ngoài sandbox sau mỗi cửa sổ 3 giờ. VietNamNet, CafeF và toàn bộ nguồn quốc tế `pending`/`blocked` vẫn không được gọi.
