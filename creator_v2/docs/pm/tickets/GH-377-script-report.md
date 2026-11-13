# GH-377 · Báo cáo kịch bản CK bài 11 (ck-c8-10-trieu-mua-duoc-gi)

Ngày 13/11/2026. Người viết: subagent Sonnet. Chưa render, TTS, commit hay đụng YouTube.

## File đã ghi
- `data/long/ck-c8-10-trieu-mua-duoc-gi/factcheck.md` (13 dòng dữ kiện + bảng mục plan bị bỏ/sửa)
- `data/long/ck-c8-10-trieu-mua-duoc-gi/script.md` (8 chương CH00-CH07, mục Ghi chú kiểm chứng có mọi phép tính)
- `data/long/ck-c8-10-trieu-mua-duoc-gi/ch00.json` ... `ch07.json` (do `script_lines.py` sinh)

## Đã kiểm chứng
- Nguồn chính tải trực tiếp: tài liệu HOSE "Các quy định cần biết khi giao dịch" (tên file T2.2026) và Quyết định 352/QĐ-SGDHCM (bản PDF đọc nguyên văn). Xác nhận: lô chẵn 100, lô lẻ 1 đơn vị tối đa 99 mỗi lệnh, nấc giá 10/50/100 đồng, ETF nấc 10 đồng, biên độ 7%.
- Lô lẻ từ 12/9/2022 (lsvn.vn trích thông báo HOSE). ETF: khoản 42 Điều 4 Luật Chứng khoán 2019 (qua luatvietnam.vn). 14.384.902 tài khoản tại 31/10/2026 (Thời báo Tài chính VN, mở lại 13/11).

## Bỏ hoặc sửa so với plan
- Sai số điều: Điều 13/15 QĐ 352 (đúng Điều 8); khoản 38 Luật CK (đúng khoản 42).
- "Đơn vị yết giá 1.000 đồng" sai: nấc giá là 10/50/100 đồng; 1.000 chỉ là hệ số hiển thị trên bảng giá.
- Bỏ: TT 120/2020 Điều 3-4 và TT 98/2020 Điều 46-60 (không mở được văn bản; TT 98 còn có "lô ETF 100.000" cho hoán đổi sơ cấp, dễ nhầm), URL baochinhphu (404) và hanoimoi (không chứa số), 252.350, 251.814, "người trẻ vốn 5-20 triệu", ETF VN30 giá 25.000 và "30 cổ phiếu", chi phí "15.000-25.000 đ", "ba nguyên tắc" (là lời khuyên).
- Sai cơ chế ở cold open plan: gõ 80 cổ phiếu là lô lẻ hợp lệ nên không bị từ chối. Đổi thành 160 cổ phiếu (không bội của 100, lớn hơn 99) rồi 200 cổ phiếu (12 triệu, thiếu tiền) trên cổ phiếu B giá 60.000 đ.

## Số âm tiết (script_lines.py)
| Chương | Câu | Âm tiết |
|---|---:|---:|
| CH00 | 13 | 269 |
| CH01 | 18 | 299 |
| CH02 | 17 | 265 |
| CH03 | 17 | 265 |
| CH04 | 17 | 355 |
| CH05 | 16 | 286 |
| CH06 | 17 | 336 |
| CH07 | 14 | 260 |
| Tổng | 129 | 2.335 |

Câu dài nhất không vượt 32 âm tiết.

## Kết quả cổng
- `craft.audio_problems`: danh sách rỗng (có câu hỏi trong 8 câu đầu, gọi "bạn", có ‖).
- `script_lines.py`: qua cổng toàn vẹn. Còn 1 cảnh báo mềm `NHIP_30S` (cửa sổ 270-300 giây ước lượng chưa có dấu beat); đã bỏ RAO_NGUON và META_NGUOI_KE sau khi sửa lời. Cần người duyệt kiểm lại timing sau TTS.
- Lời đọc không có chữ số, không tên công ty/ứng dụng/mã cổ phiếu, không khuyên mua bán, kết có "Nội dung giáo dục, không phải tư vấn đầu tư."

## Rủi ro mở
1. Nhân vật dùng phí 0,15% giả định như bài 10; mọi giá (15.000/60.000/120.000/18.000) là giả định, đã gắn nhãn.
2. CH04: lệnh 100 + lệnh 60 là suy luận từ định nghĩa lô, chưa có câu nguyên văn; bảng lô lẻ riêng, chỉ lệnh giới hạn, bán thấp 1-2 nấc chỉ từ một bài môi giới (rào một lần).
3. "Nhân một nghìn" lấy từ hướng dẫn môi giới, nên đối chiếu trên một bảng giá thật.
4. Quy chế HOSE có thể đã được thay bằng QĐ 22/QĐ-HĐTV (4/2025); lời đọc chỉ dẫn "tài liệu hướng dẫn của Sở" (bản 2/2026).
5. Chưa chạy `long_story_review.py` (ngoài phạm vi).
6. Plan chưa có cảnh `ledger` khớp lời; cảnh cần dựng lại theo script.md (ví dụ plan ghi ETF 25.000 đ, nay là 18.000 đ).
