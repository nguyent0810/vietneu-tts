# Quy trình đạo diễn (rút từ research A + số liệu kênh)

| Bước | Sản phẩm | Ai | Cổng |
|---|---|---|---|
| 1 Brief | kênh, khán giả, câu hỏi chính, nguồn số liệu, luật kênh | agent | số liệu kiểm bằng code / nguồn |
| 2 Kịch bản | 6-8 câu (`lines`) | agent | câu 1 <= 10 chữ + trả lời; câu 2 cụ thể; <= 3 tên chi/câu (FS); không câu > 35 âm tiết |
| 3 Beat sheet | mục đích từng câu + năng lượng | agent | có hook, có nhịp tĩnh trước payoff, có close |
| 4 Kế hoạch thiết bị | `scenes[]` | agent | luật đa dạng (studio.py) |
| 5 Dựng | job + mp4 | studio.py | lint 0 lỗi, check ok |
| 6 Soát mắt | qa_sheet.jpg | agent | khung 0, mỗi cảnh, seam, dấu tiếng Việt, vùng an toàn |
| 7 Duyệt | gửi người dùng khi là thiết kế/thiết bị mới | người dùng | — |
| 8 Đăng | pipeline kênh | agent | riêng tư + hẹn giờ |

## Khuôn 25-40 giây (tiếng Việt, đo: giọng FS ~3,4 âm tiết/giây, BUD ~3,5)
| Câu | Vai trò | Thiết bị gợi ý |
|---|---|---|
| 1 | Móc = câu hỏi + trả lời ngay (<= 10 chữ) | hook_poster, hook_slam (allAtStart), split(static) |
| 2 | Thông tin cụ thể thứ hai, gắn người xem | split, count_ring, quote (nếu là trích dẫn) |
| 3-4 | Giải thích bằng hình dữ liệu | wheel, cycle_draw, bars, unit_grid, calendar, time_spine |
| 5 | Nhịp tĩnh / bằng chứng | source_card, stamp, window |
| 6 | Payoff / danh sách tự dò | ledger, list_build, myth_strike |
| 7 | Câu hỏi kết (vòng lặp) | close |

## Bài học từ số liệu kênh (10/2026)
- Short bứt lên nhờ: (1) đối tượng là cả nước (năm 2027, Tết), (2) xem lại nhiều (dồn 3-4 thông tin + danh sách tự dò), (3) tiêu đề = câu người ta gõ.
- Câu hỏi có/không mà câu trả lời làm hết tò mò thì thua.
- Câu 2 ẩn dụ + ảnh stock = chỗ rơi người xem mạnh nhất. Câu có chữ động/hình dữ liệu giữ người gấp ~2 câu ảnh stock.
- Khán giả FS 74% trên 35 tuổi: ưu tiên năm sinh 1960-1990.
