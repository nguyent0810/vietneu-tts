# Báo cáo GH-180

Đã viết scripts/ck_stop_rule_180.py, scripts/test_ck_stop_rule_180.py và bản chạy thử docs/pm/2026-11-12-ck-stop-rule.md. Script lọc Short công khai, loại ID lặp, quy đổi ngày đăng UTC+7, không tự suy ngày thiếu thành 0. Ngưỡng mặc định chính xác là 193,2; cảnh báo chênh lệch median gốc từ 10%.

- Lệnh python scripts/test_ck_stop_rule_180.py: 4 kiểm thử đạt, gồm cửa sổ VN, chưa đủ tuổi, thiếu ngày, DỪNG/GIỮ và bằng ngưỡng, dưới 20 Short, lọc và ID lặp.
- Lệnh python scripts/ck_stop_rule_180.py: chạy thành công với dữ liệu hiện có.
- Nhóm thử: 15 Short duy nhất, 3 đủ dữ liệu, 12 chưa đủ tuổi theo ngày cuối có dữ liệu, median 622. Kết luận: chưa đủ dữ liệu.
- Nhóm gốc: 13 Short đủ dữ liệu, median 185, thấp hơn 322 là 137 lượt, khoảng 42,5%. Lead cần kiểm tra phạm vi và cách tính mức gốc.

Chưa kiểm chứng được múi giờ của nhãn ngày trong video_x_day.json; có lượt xem ghi ngày trước ngày đăng theo giờ VN. Script tạm xem nhãn ngày là ngày VN, nhưng không thể quy đổi chính xác từ dữ liệu tổng hợp nếu nguồn dùng múi giờ khác. Cần xác minh và kéo dữ liệu phù hợp trước khi quyết định.

Không có bản ghi hoặc ngày cuối chưa đến cuối cửa sổ được xếp chưa đủ tuổi; có thể do dữ liệu thiếu hoặc trễ. Nếu có ngày cuối nhưng thiếu ngày giữa, script loại riêng. Tổng tuần là tổng cửa sổ đầu của các video đăng trong khoảng gốc/thử, không phải lượt xem phát sinh trong tuần; tuần có thể không đầy đủ. Bản thử chỉ có 3 video nhóm thử đủ điều kiện nên top và bottom trùng nhau.

Không gọi API hoặc chạy script kéo. Không chạy lint riêng; kiểm thử Python đã đạt. Không có clip sheet hoặc thumbnail vì ticket chỉ yêu cầu phân tích.
