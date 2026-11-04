# GH-31 fix5 — báo cáo Codex

## Đã thay đổi

- Sửa riêng `factory/trend/benchmark.py`; không thay scanner, ngưỡng gom sự kiện, từ khóa kênh, benchmark JSON, lịch hay thao tác đăng.
- Chuẩn hoá token khi đo: lowercase, bỏ dấu tiếng Việt, bỏ stopword Việt/Anh và các từ chủ đề quá rộng như `giá`. Mỗi thực thể chỉ giữ tối đa ba token lõi; viết tắt trong ngoặc và chữ hoa (ví dụ `EVN`) được tách thành lõi riêng.
- Luật khớp thống nhất cho mọi mục benchmark: article phải ở trong ±48 giờ quanh `first_reported`, và hoặc (1) chứa một lõi viết tắt/tên riêng cùng một token khác trong nhãn benchmark, hoặc (2) Jaccard token giữa tiêu đề và nhãn benchmark từ 0,25 trở lên. Điều kiện (1) tìm trong title + summary; Jaccard chỉ đo title.
- Tách `recall bao phủ` (có article đã quét khớp) và `recall ứng viên` (có article khớp trong event hợp lệ, liên quan đúng kênh). Giữ trường `caught` như alias tương thích cho recall ứng viên.
- Lý do bỏ lỡ giờ dựa trên article khớp theo chính luật này: không có article, bị lọc từ khóa, hoặc không gom được; mục có article kèm tiêu đề có điểm khớp cao nhất.
- Thêm fixture `tests/fixtures/trend/benchmark_coverage.json` và test cho EVN trong ngoặc, không dấu, biên Jaccard 0,25, ca chung từ `giá` không được khớp, và hai recall tách rời.

## Lệnh đã chạy

| Lệnh | Kết quả |
|---|---|
| `python -m pytest tests/test_trend_scanner.py -q -p no:cacheprovider` | 19 passed |
| `python -m compileall -q factory/trend` | Thành công |
| `python -m factory.trend benchmark docs/pm/tickets/GH-31-benchmark.json` | Kết quả bên dưới, dùng dữ liệu đã lưu |

Lỗi lint/compile còn lại: không có.

## Recall trước/sau

Số “trước” là metric `caught` duy nhất của báo cáo fix4; nó không tách được độ bao phủ và ứng viên. “Sau” là kết quả benchmark mới trên cùng dữ liệu lưu.

| Kênh | Trước | Sau: bao phủ | Sau: ứng viên |
|---|---:|---:|---:|
| MIM | 6/18 (33,3%) | 14/18 (77,8%) | 12/18 (66,7%) |
| CK | 0/20 (0,0%) | 9/20 (45,0%) | 8/20 (40,0%) |

| Kênh | Hotness | Bao phủ | Ứng viên |
|---|---|---:|---:|
| MIM | high | 7/9 (77,8%) | 6/9 (66,7%) |
| MIM | medium | 7/9 (77,8%) | 6/9 (66,7%) |
| CK | high | 7/14 (50,0%) | 6/14 (42,9%) |
| CK | medium | 2/6 (33,3%) | 2/6 (33,3%) |

## Bỏ lỡ sau sửa

### MIM

- `mim_01`: không có nguồn đưa tin.
- `mim_02`: bị lọc từ khóa — Chính thức 1/1/2027, cấm nhập khẩu điện thoại, máy tính, máy ảnh đã qua sử dụng.
- `mim_11`: không có nguồn đưa tin.
- `mim_14`: không có nguồn đưa tin.
- `mim_16`: không có nguồn đưa tin.
- `mim_18`: bị lọc từ khóa — Cảnh báo giao dịch tiền số: Vì sao tài khoản ngân hàng bị khóa?

### CK

- `ck_05`: không có nguồn đưa tin.
- `ck_06`: không có nguồn đưa tin.
- `ck_08`: không có nguồn đưa tin.
- `ck_11`: không có nguồn đưa tin.
- `ck_12`: bị lọc từ khóa — Cổ phiếu doanh nghiệp sản xuất Anh trai 'Say Hi' DatVietVAC lên sàn HOSE.
- `ck_13`: không có nguồn đưa tin.
- `ck_15`: không có nguồn đưa tin.
- `ck_16`: không có nguồn đưa tin.
- `ck_17`: không có nguồn đưa tin.
- `ck_18`: không có nguồn đưa tin.
- `ck_19`: không có nguồn đưa tin.
- `ck_20`: không có nguồn đưa tin.

## 10 cặp khớp điểm thấp nhất để Lead soát tay

Điểm là Jaccard title–label; `entity` nghĩa là cặp được tính nhờ nhánh lõi thực thể, nên điểm có thể là 0.

1. `ck_04` — Các hãng AI thống nhất tiêu chuẩn chặn thu thập dữ liệu huấn luyện (0,000; entity).
2. `ck_14` — Siêu El Nino 'hâm nóng' giá gạo Việt (0,000; entity).
3. `mim_04` — Cú đảo chiều trên đỉnh thế giới: Một công ty vừa soán ngôi Nvidia giành lại vị trí số 1 với vốn hoá hơn 5.000 tỷ USD (0,000; entity).
4. `mim_05` — 2 ngày tắm máu cổ phiếu công nghệ Mỹ: Alphabet mất 500 tỷ USD, Intel lao dốc gần 30% (0,000; entity).
5. `mim_05` — Điện thoại Galaxy gặp khó, Samsung vẫn lãi kỷ lục hơn 80 tỉ USD (0,000; entity).
6. `mim_06` — Phần Lan điều tra hình sự Google (0,000; entity).
7. `mim_06` — Điện thoại Galaxy gặp khó, Samsung vẫn lãi kỷ lục hơn 80 tỉ USD (0,000; entity).
8. `mim_07` — Phần Lan điều tra hình sự Google (0,000; entity).
9. `mim_08` — 2 ngày tắm máu cổ phiếu công nghệ Mỹ: Alphabet mất 500 tỷ USD, Intel lao dốc gần 30% (0,000; entity).
10. `mim_08` — Điện thoại Galaxy gặp khó, Samsung vẫn lãi kỷ lục hơn 80 tỉ USD (0,000; entity).

Khẳng định không kiểm được: không có; ticket chỉ đo dữ liệu nội bộ, không tạo nội dung xuất bản.

Clip sheet và thumbnail: không áp dụng; đây là ticket `factory/trend`, không render video.
