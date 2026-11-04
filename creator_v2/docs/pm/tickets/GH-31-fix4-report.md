# GH-31 fix4 — báo cáo Codex

## Đã thay đổi

- Thêm `normalize_text()` cho toàn bộ đường parse: giải mã HTML entity tối đa hai lượt, chuẩn hoá Unicode NFC và gộp khoảng trắng. `summary` được bỏ thẻ HTML còn sót trước khi lưu.
- Áp dụng chuẩn hoá cho RSS, Google Trends (bài và signal), Wiki signal và mọi article đi qua `_article`.
- Thêm migration `normalize_stored_articles()`. `cluster_db()` gọi migration trước khi đọc article và dựng lại event, nên dữ liệu cũ trong `data/trend/trend.sqlite` được chuẩn hoá rồi cluster lại mà không quét feed.
- Sửa benchmark: chỉ ghi `không có nguồn đưa tin` nếu không có article nào trong cửa sổ ±48 giờ chứa ít nhất một thực thể benchmark sau khi bỏ dấu. Nếu có article thì báo `bị lọc từ khóa` hoặc `không gom được`, kèm tiêu đề article gần nhất.
- Bổ sung RSS fixture có `&agrave;`, `&#039;`, `&amp;aacute;`; test xác nhận title/summary lưu ra tiếng Việt NFC. Bổ sung fixture và test ba lý do bỏ lỡ benchmark.

## Lệnh đã chạy

| Lệnh | Kết quả |
|---|---|
| `python -m pytest tests/test_trend_scanner.py -q -p no:cacheprovider` | 17 passed |
| `python -m compileall -q factory/trend` | Thành công, không có lỗi lint/compile còn lại |
| `python -c "from factory.trend.cluster import cluster_db; print(cluster_db())"` | 149 event; migration dữ liệu cũ đã chạy trước khi cluster |
| `python -m factory.trend report` | `output/trend/2026-11-02/12.md` |
| `python -m factory.trend benchmark docs/pm/tickets/GH-31-benchmark.json` | Kết quả bên dưới |

Không chạy `scan`/`run`: feed đang `rate_skip` và ticket chỉ yêu cầu xử lý dữ liệu đã lưu. Không thay đổi ngưỡng gom sự kiện, benchmark, nguồn, lịch, commit hay thao tác đăng.

## Bảng 4 số mỗi kênh

| Kênh | Bài trước → sau | Sự kiện hợp lệ trước → sau | Ứng viên liên quan trước → sau | Cơ hội sản xuất trước → sau |
|---|---:|---:|---:|---:|
| MIM | 113 → 113 | 105 → 105 | 16 → 16 | 4 → 4 |
| CK | 79 → 79 | 64 → 67 | 28 → 37 | 6 → 11 |

Sự kiện nóng CK cũng tăng từ 1 lên 2. Các thay đổi trên đến từ việc tiêu đề/summary đã lưu được chuẩn hoá trước khi lọc và cluster.

## Benchmark recall trước/sau

| Kênh | Trước | Sau |
|---|---:|---:|
| MIM | 6/18 (33,3%) | 6/18 (33,3%) |
| CK | 0/20 (0,0%) | 0/20 (0,0%) |

Recall không đổi vì ticket không cho thay ngưỡng gom hay điều kiện bắt benchmark. Tuy nhiên, kết quả bỏ lỡ không còn quy mọi trường hợp về thiếu nguồn: CK hiện có 10 mục `không gom được` và 2 mục `bị lọc từ khóa`, bao gồm `ck_03` với tiêu đề giá vàng đã được giải mã chính xác.

## Danh sách bỏ lỡ sau sửa

### MIM

- `mim_01`, `mim_02`, `mim_06`, `mim_08`, `mim_11`, `mim_12`, `mim_16`, `mim_17`, `mim_18`: không có nguồn đưa tin.
- `mim_13`: không gom được — Apple tung bản cập nhật bảo mật khẩn cấp cho 3 mẫu iPhone cũ.
- `mim_14`: bị lọc từ khóa — Cảnh báo giao dịch tiền số: Vì sao tài khoản ngân hàng bị khóa?
- `mim_15`: không gom được — Lợi nhuận LG Electronics tăng gần 56% sau 9 tháng, đơn hàng làm mát trung tâm dữ liệu AI vượt 3.000 tỷ won.

### CK

- `ck_01`: không gom được — EVN giảm giá điện từ ngày 1.11, còn hơn 2.159 đồng/kWh.
- `ck_02`: không gom được — Xăng dầu tiếp tục được ưu đãi thuế đến hết năm nay.
- `ck_03`: không gom được — Giá vàng hôm nay 2.11.2026: Vàng miếng SJC tăng đầu tuần.
- `ck_04`: bị lọc từ khóa — Cổ phiếu doanh nghiệp sản xuất Anh trai 'Say Hi' DatVietVAC lên sàn HOSE.
- `ck_05`: không có nguồn đưa tin.
- `ck_06`: không gom được — Tổng lực giảm chi phí cho người dân, doanh nghiệp.
- `ck_07`: không có nguồn đưa tin.
- `ck_08`: không gom được — Thống đốc Phạm Đức Ấn nói về việc người dân gửi nhiều tiền vào ngân hàng.
- `ck_09`: không có nguồn đưa tin.
- `ck_10`: không gom được — Sacombank có quyền tổng giám đốc mới.
- `ck_11`: không có nguồn đưa tin.
- `ck_12`: bị lọc từ khóa — Cổ phiếu doanh nghiệp sản xuất Anh trai 'Say Hi' DatVietVAC lên sàn HOSE.
- `ck_13`: không gom được — Giá vàng hôm nay 2.11.2026: Vàng miếng SJC tăng đầu tuần.
- `ck_14`, `ck_15`, `ck_16`: không có nguồn đưa tin.
- `ck_17`: không gom được — Thiếu thông tin về thuế đất phi nông nghiệp.
- `ck_18`, `ck_19`, `ck_20`: không có nguồn đưa tin.

Khẳng định không kiểm được: không có.

Clip sheet và thumbnail: không áp dụng; đây là ticket `factory/trend`, không render video.
