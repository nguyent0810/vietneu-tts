# GH-31 · Codex vòng sửa 4 P0: giải mã HTML entity trong tiêu đề và tóm tắt

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/31. Vòng trước: `docs/pm/tickets/GH-31-fix3-report.md`.

## Lỗi (Lead kiểm trong `data/trend/trend.sqlite`)
Tiêu đề của `thanhnien_kinh_te` lưu còn nguyên HTML entity, ví dụ:
- `Gi&aacute; v&agrave;ng h&ocirc;m nay 2.11.2026: V&agrave;ng miếng SJC tăng đầu tuần`
- `Chứng kho&aacute;n Việt Nam giảm hơn 30 điểm, thanh khoản tăng đột biến`

Vì vậy từ khóa, thực thể và so khớp benchmark tiếng Việt đều trượt: `title like '%vàng%'` trả 0. CK recall 0/20 vì lỗi này, không phải vì "không có nguồn đưa tin". Bài thứ hai ở trên chính là `ck_04`.

## Được ghi
- `factory/trend/*`
- `tests/test_trend_*.py`
- `tests/fixtures/trend/`
- báo cáo `docs/pm/tickets/GH-31-fix4-report.md`

**Không:** thêm nguồn, đổi ngưỡng gom sự kiện, sửa benchmark, commit.

## Việc
1. Chuẩn hóa văn bản ngay lúc parse, áp cho mọi nguồn:
   - `html.unescape`, lặp tối đa 2 lần nếu còn entity, để xử lý chuỗi bị escape hai lần;
   - bỏ thẻ HTML còn sót trong summary;
   - chuẩn hóa Unicode NFC;
   - gộp khoảng trắng.
2. Migration: chuẩn hóa lại `title` và `summary` của các article đã lưu trong `trend.sqlite`, rồi cluster lại.
3. Kiểm lại lý do "bỏ lỡ" trong `benchmark.py`. Chỉ ghi "không có nguồn đưa tin" khi không có article nào trong cửa sổ chứa ≥ 1 thực thể benchmark (đã chuẩn hóa không dấu). Có article chứa thực thể mà không thành ứng viên khớp thì ghi "bị lọc" hoặc "không gom được", kèm tiêu đề article gần nhất.
4. Test: fixture RSS có entity (`&agrave;`, `&#039;`, `&amp;aacute;`), kiểm tiêu đề lưu ra đúng tiếng Việt NFC; test lý do bỏ lỡ.
5. Chạy lại `cluster`, `report` và `benchmark` trên dữ liệu đã lưu, không cần quét lại (feed đang `rate_skip`). Ghi lại bảng 4 số mỗi kênh và recall trước/sau.

## Báo cáo
Thay đổi, test, bảng trước/sau, danh sách bỏ lỡ kèm lý do mới.
