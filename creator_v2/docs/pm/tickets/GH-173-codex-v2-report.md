# GH-173 vòng 2 — báo cáo

Đã sửa bố cục nhãn giả định và bổ sung trọng lượng font trong phạm vi ticket. Chưa thể xác nhận hoàn tất vì bộ kiểm thử đầy đủ không xanh và chưa có QA hình ảnh; ticket không cho render.

- Cảnh có nhãn hợp lệ được gắn has-hypo. Với cards3d, table, board, kinetic, nội dung được gom riêng; đo chiều cao nhãn thực tế, kể cả hypo_sub, cộng khoảng hở 24 px. Dời điểm đầu nội dung xuống tối thiểu bằng đáy nhãn cộng 24 px. Nếu khối sau khi dời vượt y=1440 thì thu nhỏ đều để đáy tính toán nằm trong y=1440, chừa 38 px trước subtitle y=1478; phép tính cộng dự phòng 32 px vào đáy nội dung. Cảnh không có hypo giữ nguyên.
- Cards3d: vị trí đầu ban đầu khoảng y=304 với ba thẻ có tiêu đề. Ví dụ nhãn cao 140 px tại y=220: đầu nội dung tối thiểu y=384, dịch ít nhất 80 px trước khi tính phần bù scale. Thu nhỏ khi phần thẻ và ghi chú sau khi dời vượt giới hạn.
- Table: tiêu đề mặc định bắt đầu y=234; cần dời xuống tối thiểu y=384 với nhãn 140 px. Thu nhỏ toàn bảng nếu đáy vượt giới hạn, tránh chỉ đẩy các hàng vào subtitle.
- Board: mặc định bắt đầu y=450 nên thường không cần dời với nhãn cao 140 px. Vị trí/chiều cao tuỳ chỉnh và ghi chú vẫn được đo; chỉ dời hoặc thu nhỏ khi cần.
- Kinetic: đo các dòng chữ và thanh trang trí; vị trí phụ thuộc nội dung và cấu hình, chỉ dời hoặc thu nhỏ khi cần. Nền video nằm ngoài nhóm nội dung.
- Chart, counter, ledger giữ nguyên bố cục; ledger mặc định bắt đầu y=430 và đã đạt QA trước đó. Không áp dụng offset cho ba loại này.
- Giá trị offset không cố định theo loại: --hypo-offset là chiều cao nhãn đo được; --hypo-shift và --hypo-scale tính từ giới hạn thật của từng cảnh.
- Google Fonts đã thêm Playfair Display italic 900 và JetBrains Mono 800.

Kiểm tra:
- python -m pytest tests/test_hypo_label_173.py -q -p no:cacheprovider: 5 passed. Có kiểm tra cảnh cards3d có/không có hypo, hai chiều cao nhãn, giới hạn phụ đề và link font.
- python -m pytest tests -q: 600 passed, 43 skipped, 348 errors, 2 warnings. Các lỗi xuất hiện tại bước thiết lập fixture thư mục tạm với PermissionError; pytest cũng cảnh báo không ghi được cache. Không thể coi bộ test là xanh.
- Lệnh kiểm mất dấu nguyên văn trong ticket: mã thoát 0.
- Chưa render, chưa có clip sheet hoặc thumbnail mới theo yêu cầu ticket. Cần Grok chụp lại và kiểm tra trực quan vị trí nhãn, chữ và mép nội dung; số đo trong mã không chứng minh được hình học của các tween 3D trong mọi khung.
- Không có khẳng định nội dung cần factcheck; không chạy lint nội dung vì đây là ticket code.
