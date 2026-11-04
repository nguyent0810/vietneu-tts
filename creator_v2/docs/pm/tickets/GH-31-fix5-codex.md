# GH-31 · Codex vòng sửa 5 P0: so khớp benchmark công bằng, tách 2 loại recall

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/31. Vòng trước: `docs/pm/tickets/GH-31-fix4-report.md`.

## Vấn đề
`benchmark.py` so thực thể theo chuỗi con. Thực thể trong benchmark là cụm dài, ví dụ `Tập đoàn Điện lực Việt Nam (EVN)`, `Giá bán lẻ điện bình quân`, `Vàng miếng SJC`. Vì vậy các bài rõ ràng cùng sự kiện vẫn bị tính là bỏ lỡ:
- `ck_01`: "EVN giảm giá điện từ ngày 1.11";
- `ck_03`: "Giá vàng hôm nay 2.11.2026: Vàng miếng SJC tăng đầu tuần";
- `ck_04`: "Chứng khoán Việt Nam giảm hơn 30 điểm".

Đây là lỗi của **công cụ đo**, không phải lỗi phát hiện.

## Được ghi
- `factory/trend/benchmark.py`
- `tests/test_trend_*.py`
- fixture
- báo cáo `docs/pm/tickets/GH-31-fix5-report.md`

**Không:** sửa scanner, ngưỡng gom sự kiện, từ khóa kênh hay benchmark JSON. Không commit.

## Việc
1. **Rút "lõi" thực thể.**
   - Tách viết tắt trong ngoặc, ví dụ `(EVN)` → `evn`.
   - Bỏ dấu, lowercase, bỏ stopword tiếng Việt và tiếng Anh. Đặt stoplist trong `keywords.json` hoặc trong module.
   - Mỗi thực thể thành tập token lõi; thực thể dài thì lấy 2–3 token có nghĩa nhất (danh từ riêng, mã, số có đơn vị).
2. **Định nghĩa khớp.** Viết luật trước, áp như nhau cho mọi sự kiện, không chỉnh theo từng mục. Một article khớp một sự kiện benchmark khi nằm trong cửa sổ ±48 h quanh `first_reported` và thỏa một trong hai điều kiện:
   - chứa ≥ 1 lõi thực thể dạng viết tắt hoặc tên riêng, **và** ≥ 1 token khác trong nhãn benchmark;
   - hoặc Jaccard token (không dấu, bỏ stopword) giữa tiêu đề article và nhãn benchmark ≥ 0,25.
3. **Hai loại recall mỗi kênh:**
   - **recall bao phủ:** tỷ lệ sự kiện benchmark có ≥ 1 article khớp đã được quét. Đo khả năng nguồn và scanner thấy tin;
   - **recall ứng viên:** tỷ lệ sự kiện benchmark có article khớp nằm trong một **ứng viên liên quan** của đúng kênh. Đo khả năng lọc và gom.

   Mỗi loại tách theo `hotness`.
4. **Lý do bỏ lỡ:** "không có nguồn đưa tin" (không article nào khớp), "bị lọc từ khóa", hoặc "không gom được", kèm tiêu đề article khớp tốt nhất. Thêm danh sách khớp **dương tính giả** để Lead soát tay: 10 cặp article–benchmark có điểm khớp thấp nhất mà vẫn được tính là khớp.
5. **Test:** viết tắt trong ngoặc, bỏ dấu, ngưỡng Jaccard, một ca phải không khớp (khác sự kiện, chung một từ phổ thông như "giá").
6. Chạy `benchmark` trên dữ liệu đã lưu. Báo 2 loại recall trước/sau.

## Báo cáo
Luật khớp, test, bảng recall, danh sách bỏ lỡ kèm lý do, 10 cặp dương tính giả để soát.
