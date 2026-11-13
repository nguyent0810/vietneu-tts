# GH-377 — Báo cáo review câu chuyện

## Kết quả

Đã review đủ tám chương, viết `data/long/ck-c8-10-trieu-mua-duoc-gi/story_review/ch00.md` đến `ch07.md`, và ghép thành `data/long/ck-c8-10-trieu-mua-duoc-gi/script.v2.md`. Mỗi chương có 4–6 đoạn review, bản viết lại đầy đủ và mục cần xác minh. Đã giữ nguyên phần đầu và toàn bộ Ghi chú kiểm chứng của `script.md`; không ghi đè kịch bản gốc. Đây là bản review để Lead duyệt, chưa đủ điều kiện báo hoàn tất cổng Long.

Các sửa chữa đáng chú ý: lý do lệnh hai trăm cổ phiếu thiếu tiền là giá của **hai** lô; tiền dư ở ví dụ cổ phiếu A và quỹ được ghi rõ trước phí; ba lô trị giá bảy triệu rưỡi còn lại hai triệu rưỡi trước phí, không phải gần dùng hết. Giữ rào về nguồn của hệ số nhân một nghìn, bảng lô lẻ riêng và lệnh giới hạn; các khả năng chờ hoặc chênh giá không được trình bày như kết quả chắc chắn.

## Âm tiết theo chương

Đếm các dòng đã parse bằng `motion/long/script_lines.py`, theo số từ cách nhau bằng khoảng trắng như kết quả CLI của bản gốc. Mọi chương nằm trong ±10%.

| Chương | Cũ | Mới | Thay đổi |
|---|---:|---:|---:|
| CH00 | 269 | 262 | −2,6% |
| CH01 | 299 | 317 | +6,0% |
| CH02 | 265 | 270 | +1,9% |
| CH03 | 265 | 271 | +2,3% |
| CH04 | 355 | 376 | +5,9% |
| CH05 | 286 | 307 | +7,3% |
| CH06 | 336 | 338 | +0,6% |
| CH07 | 260 | 264 | +1,5% |
| **Tổng** | **2.335** | **2.405** | |

## Kiểm tra đã chạy

- `python motion/long/script_lines.py ck-c8-10-trieu-mua-duoc-gi`: bản gốc qua gate; có 1 cảnh báo `NHIP_30S` ở khoảng 270–300 giây.
- Theo phương án dự phòng được ticket cho phép, dùng Python gọi trực tiếp `script_lines.parse`, `script_lines.gate`, `script_lines.flow_warnings`, `script_lines.beat_warnings` trên cả bản gốc và v2. Gate v2 không lỗi; `NHIP_DEU` và `RAO_NGUON` đều 0 ở cả hai bản. Tổng cảnh báo nhịp mỗi bản là 1: bản v2 còn `NHIP_30S` ở khoảng 630–647 giây, Lead cần nghe và duyệt nhịp. Vị trí cảnh báo đã thay đổi.
- `craft.audio_problems(script_lines.parse(text))` với v2 trả danh sách rỗng. Từng câu dài nhất theo từng chương lần lượt là 27, 24, 24, 23, 29, 26, 28 và 26 âm tiết; có câu hỏi trong tám câu đầu, có “bạn” và dấu ngừng dài.
- Python `Decimal` kiểm lại các phép chia, nhân, phí, số dư, giá trần/sàn và tỷ lệ được nhắc; 21 phép kiểm đều đạt. Ví dụ ba lệnh tổng bảy triệu rưỡi, nếu tính phí giả định 0,15% trên đúng giá trị này, phí là 11.250 đồng; 15.000 đồng áp dụng khi tính trên đủ mười triệu. Ghi chú kiểm chứng gốc giữ nguyên theo ticket.
- Đối chiếu phần bản viết lại của từng review với chương tương ứng trong v2; kiểm phần đầu và Ghi chú kiểm chứng khớp nguyên bản. Toàn bộ file ghi bằng Python UTF-8. Kiểm Python không có hai dấu hỏi liên tiếp; các dấu `?` đơn còn lại là dấu câu hỏi trong nội dung.
- `python scripts/long_gate.py ck-c8-10-trieu-mua-duoc-gi --min-syl 1900`: **TRƯỢT, 20 lỗi**, không in ĐẠT. Lệnh kiểm topic gốc, không tự thay bằng `script.v2.md`: thiếu HUD và loại cảnh ở tám chương, chưa TTS, thời lượng/cảnh vượt ngưỡng do chưa có cảnh, thiếu các trường `spec.youtube` và nguồn công khai trong spec. Việc sản xuất cảnh, TTS và hoàn thiện spec nằm ngoài ticket review này; ticket còn cấm render. Vì vậy chưa thể báo cổng Long đạt.

## Cần xác minh — danh sách gộp

1. Thông báo và cách từ chối hai lệnh ở đoạn mở chỉ là giả định; đối chiếu giao diện và điều kiện đặt lệnh thực tế. Số tài khoản cuối tháng mười là số tài khoản theo nguồn thứ cấp, không phải số người.
2. Đối chiếu hệ số nhân một nghìn với bảng giá thực tế trước khi dựng; nguồn hiện là hướng dẫn của một công ty chứng khoán. Các mức trần và sàn là phép tính giả định theo biên độ thông thường, không tự xác nhận mọi điều kiện đặt lệnh.
3. Việc chia 160 cổ phiếu thành một lệnh lô chẵn và một lệnh lô lẻ là suy luận từ định nghĩa, chưa có câu nguyên văn xác nhận trong factcheck. Thông tin bảng lô lẻ riêng, lệnh giới hạn, khả năng chờ và giá bán thấp hơn dựa trên nguồn thứ cấp; kiểm điều kiện thực tế. Hai nấc chỉ là giả sử.
4. Kiểm cách tính sức mua và biểu phí thực tế, bao gồm phí tối thiểu mỗi lệnh nếu có. Mức 0,15% là giả định; số dư trước và sau phí cần thể hiện tách bạch. Ngưỡng giá khoảng 33.300 đồng trong CH05 tính trước phí và còn phải tuân theo nấc giá.
5. Nhận định ETF thường phản ánh chỉ số dựa trên nguồn thứ cấp; kiểm tài liệu của từng quỹ. Giá, nhân vật và các phép tính trong phiếu đều giả định; khả năng đặt mua không bảo đảm lệnh sẽ khớp.

Không gọi mạng, không render, không đăng và không thao tác Git. Clip sheet và thumbnail: không tạo vì ticket chỉ review kịch bản.
