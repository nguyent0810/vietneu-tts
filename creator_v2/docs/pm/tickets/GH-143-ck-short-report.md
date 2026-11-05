# GH-143 · Báo cáo lời Short CK sức mua

Slug `ck-them-10-trieu-gio-bot-mot-mon`. Loại S. Không sửa spec, không render, không upload, không commit, không đổi lịch.

## Số từ

107 từ, đếm theo khoảng trắng. 9 câu. Câu dài nhất 13 từ. Câu mở 9 từ.

| # | Từ | Loại | Câu |
|---|---:|:---:|---|
| 1 | 9 | T | Tài khoản thêm mười triệu, giỏ bớt một món. |
| 2 | 12 | M | Bạn thấy số dư tăng, nhưng giỏ hàng không tự lớn theo. |
| 3 | 13 | D | Theo Cục Thống kê, CPI tháng mười tăng 5,09% so với cùng kỳ. |
| 4 | 13 | G | Trong ví dụ giả định, bạn có 250 triệu, lãi 4% một năm. |
| 5 | 11 | D | Tiền lãi đúng 10 triệu, số dư mới là 260 triệu. |
| 6 | 12 | G | Cùng giỏ năm ngoái 250 triệu, giá tăng 5,09% thành 262,725 triệu. |
| 7 | 12 | D | Số dư 260 triệu thiếu 2.725.000 đồng cho cùng giỏ giả định. |
| 8 | 13 | M | Một món đúng khoản thiếu rời giỏ thì phần còn lại vừa khít. |
| 9 | 12 | T | Số dư lớn hơn chưa có nghĩa sức mua của bạn tăng. |

Khung 0: `10 TRIỆU↑ GIỎ -1 MÓN` (5 từ, hai cụm đối nhau).

## Phép tính ví dụ

CPI dùng trong ví dụ là **+5,09% so cùng kỳ** (tháng 10/2026 so với tháng 10/2025). Đây là mức giá của rổ sau một năm. Mức bình quân 10 tháng +4,57% là số thật khác, không thay cho cùng kỳ một năm.

Lãi 4%/năm là giả định, không phải lãi suất của tổ chức nào. Chọn 4% vì thấp hơn 5,09%, nên sức mua giảm, và vì 250 triệu × 4% ra đúng 10 triệu.

- Số dư đầu: 250.000.000 đồng
- Tiền lãi: 250.000.000 × 4 / 100 = 10.000.000 đồng
- Số dư cuối: 260.000.000 đồng
- Giỏ cùng các món, giá cũ bằng số dư đầu: 250.000.000 đồng
- Giá mới của cả giỏ: 250.000.000 × 10.509 / 10.000 = 262.725.000 đồng
- Khoản thiếu ở giá hôm nay: 262.725.000 − 260.000.000 = 2.725.000 đồng
- Bỏ một món giả định giá đúng 2.725.000 đồng thì phần còn lại = 260.000.000 đồng, khớp số dư mới

Sức mua của số dư mới, quy về giá cũ: 260.000.000 / 1,0509 ≈ 247.406.984 đồng, thấp hơn 250.000.000 đồng. Tỷ lệ (1,04 / 1,0509) − 1 ≈ −1,04%.

Giỏ tăng theo chỉ số chung. Một món bị bỏ được đặt giá đúng bằng khoản thiếu, để phần còn lại khít số dư. Không nói từng món trong giỏ đều có giá cũ tròn.

Phép thử, không đưa vào lời: nếu lấy nhầm 4,57% thì giỏ tăng 11.425.000 đồng, vẫn lớn hơn 10.000.000 đồng lãi. Chiều câu chuyện không đổi, khoản thiếu thì đổi. Lời giữ 5,09%.

## Bảng claim → nguồn

Đã mở 04/11/2026. Trang sơ cấp tiếng Việt của Cục Thống kê và bản tiếng Anh cùng số: https://www.nso.gov.vn/en/data-and-statistics/2026/11/consumer-price-index-cpi-gold-price-index-and-us-dollar-price-index-in-october-and-ten-months-of-2026/

| Claim | Giá trị | Nguồn đã mở | Trong lời |
|---|---|---|---|
| CPI tháng 10/2026 so cùng kỳ | +5,09% | NSO, VietNamNet 03/11/2026, VnExpress 03/11/2026 | Có |
| CPI bình quân 10 tháng 2026 | +4,57% | NSO, VietNamNet, VnExpress | Chỉ ở mô tả |
| CPI tháng 10/2026 so tháng trước | +0,20% (VietNamNet viết 0,2%) | NSO, VietNamNet | Không |
| CPI tháng 10/2026 so tháng 12/2025 | +4,41% | NSO, VietNamNet, VnExpress | Không |
| Lạm phát cơ bản bình quân 10 tháng | +4,24% | NSO, VietNamNet | Không |
| Chỉ số giá vàng tháng 10: −2,85% so tháng trước, −2,94% so cùng kỳ, bình quân 10 tháng +37,28% | như cột claim | Cùng trang NSO và bài VietNamNet | Không |
| Chỉ số giá đô la Mỹ tháng 10: −0,26% so tháng trước, bình quân 10 tháng +0,78% | như cột claim | Cùng trang NSO và bài VietNamNet | Không |

Trích NSO, đúng thứ tự trên trang: "tháng Mười tăng 0,20% so với tháng trước; tăng 4,41% so với tháng 12/2025 và tăng 5,09% so với cùng kỳ năm trước" và "Bình quân mười tháng năm 2026, CPI tăng 4,57% so với cùng kỳ năm trước; lạm phát cơ bản tăng 4,24%."

## CHƯA KIỂM

Không có số nào trong lời đọc ở trạng thái này.

- Nhóm nhà ở, điện nước, chất đốt và vật liệu xây dựng bình quân 10 tháng +6,66%: thấy trên VietNamNet và VnExpress, không có trong đoạn đã mở của trang sơ cấp NSO. Không dùng.
- Giá thuê nhà tháng 10 giảm 0,22%: thấy trên VietNamNet, không có trong đoạn đã mở của trang sơ cấp NSO. Không dùng.
- Mức tăng giảm từng nhóm trong tháng 10 (giao thông +2,66%, xăng +6,86%, điện sinh hoạt −1,99% và các nhóm khác): thấy trên VietNamNet, không có trong đoạn đã mở của trang sơ cấp NSO. Không dùng.

## Cách đọc và hình

`say` map cả cụm, không map số trần, để khỏi đọc đè chữ "triệu". "262,725 triệu" là 262 triệu 725 nghìn (dấu phẩy thập phân), đọc "hai trăm sáu mươi hai triệu bảy trăm hai mươi lăm nghìn". "2.725.000 đồng" đọc "hai triệu bảy trăm hai mươi lăm nghìn đồng". CPI đọc "xê pê i".

Clip M: giỏ và tay, không logo, không chữ thương hiệu, không biển hiệu. Số tự dựng trên hình gắn "VÍ DỤ GIẢ ĐỊNH". Số CPI không gắn nhãn đó.
