# GH-179 — báo cáo phần A: CHƯA HOÀN THÀNH

Đã tạo `data/long/hoa-than/gen_scenes.py`, `spec.json`, và `ch00.json`–`ch03.json`, với cảnh viết tay và lời đọc lấy từ kịch bản. Chưa đáp ứng nhịp 3–5 giây; không bàn giao như bản hoàn tất. Spec hiện chỉ liệt kê bốn chương đã dựng; các phần B–D phải bổ sung chương và hoàn thiện metadata. Không chạy TTS, render hay xuất bản.

## Số cảnh

- CH00: 10 — date 1, photo 3, file 1, slam 1, quote 1, ledger 1, question 2.
- CH01: 7 — photo 2, ledger 1, kinetic 1, date 1, timeline 1, question 1.
- CH02: 11 — date 3, file 1, photo 3, kinetic 1, ledger 2, question 1.
- CH03: 13 — date 1, photo 5, kinetic 2, timeline 1, ledger 1, file 1, slam 1, question 1.
- Tổng 41 cảnh. Cần thêm cảnh bám lời đọc và rà toàn bộ neo, nhãn ảnh, phân nhóm trước khi duyệt.

## Kiểm tra

- `python data/long/hoa-than/gen_scenes.py`: chạy thành công, sinh bốn chương.
- `python motion/long/cadence.py hoa-than`: CẢNH BÁO; ước tính theo 150 giây/chương vì chưa có timing TTS. CH00: 12 thay đổi, trung bình 12,50 giây, dài nhất 25,21 giây; CH01: 13, 11,54 giây, dài nhất 39,37 giây; CH02: 16, 9,38 giây, dài nhất 24,36 giây; CH03: 19, 7,89 giây, dài nhất 32,36 giây. Số thay đổi bao gồm các thay đổi bên trong cảnh, không phải số cảnh.
- Phân nhóm cadence theo thời lượng ước tính: tổng A 2,6%, B 0%, C 0%, D 21,4%, UNKNOWN 76%. Tỷ lệ này chưa đủ tin cậy để kết luận tỉ lệ A/B/C/D, vì công cụ chưa nhận diện được phần lớn tài nguyên; cần gán và rà nhóm thủ công.
- `python motion/long/scene_params.py hoa-than`: 0 lỗi, 0 cảnh báo trên bốn chương; không chứng minh nhịp hoặc hình ảnh đã đạt.
- `PYTHONIOENCODING=utf-8 python motion/variety.py audit hoa-than`: OK sau khi spec giới hạn danh sách ở bốn chương hiện có. Chưa thể coi là kiểm toán cả 14 chương.
- `python scripts/long_gate.py hoa-than --min-syl 5000`: TRƯỢT, 7 lỗi: thiếu TTS bốn chương; 1.420 âm tiết đang dựng dưới 5.000; trung bình 9,9 giây/cảnh trên ngưỡng 9; công cụ báo năm 1760 chưa khớp factcheck; thiếu bốn trường metadata YouTube; chưa có tám URL công khai trong spec; thiếu bảng phiên âm 19 tên/thuật ngữ. Không chạy TTS theo ticket. Các lỗi còn lại cần xử lý trong phạm vi phù hợp và chạy lại khi hoàn thiện bài.
- Chưa chạy floor, studio lint, clip sheet, thumbnail hay render; ticket không yêu cầu và không cho TTS/render. Chưa có đường dẫn clip sheet hoặc thumbnail cho phần này.

## Lệch visual plan và nguồn

Kịch bản bản 2 là nguồn thứ tự: CH00 mở ở nhà riêng ngày 22/2/1799; CH01 so hai ước tính và hai đồng liêu; CH02 là tuổi trẻ, thị vệ, vào Quân cơ; CH03 là đặc ân cưỡi ngựa và nhà riêng. Kế hoạch hình mô tả thêm ngựa ngự ban, hàng nghìn thợ, chi tiết xây phủ và mốc chuyển chương không có ở câu tương ứng; các chi tiết đó không được đưa lên màn hình như sự thật. CH03 dùng ảnh ngựa Càn Long chỉ làm minh họa có nhãn, không gán là Hòa Thân. Bản kê giữ các ước tính cạnh nhau, không cộng thành tổng.

Các khẳng định chưa kiểm được trong kho factcheck, như toàn văn McMahon, nhật ký Macartney nguyên văn và trang bảo tàng, không dùng làm khẳng định mới trong cảnh. Chưa kiểm thực tế hiển thị ảnh, nguồn cấp phép và clip sheet; không khẳng định cảnh đã đạt chất lượng hình ảnh. Ảnh AI `ai10` khai `credit: false` và nhãn tái dựng. Cần tiếp tục dựng cảnh, bổ sung metadata và chạy lại mọi cổng trước khi báo xong.
