# Đo mỗi video trong cửa sổ 7 ngày PT; Short xếp hạng trong cùng tuần; chỉ tin số liệu sạch; Lead tính lại mọi con số

Trạng thái: đã chấp nhận (05/10/2026, bổ sung 24/10).

Lấy số liệu bừa thì dễ ra kết luận sai:

- YouTube Analytics tính ngày theo giờ Thái Bình Dương (PT) và trễ khoảng 3 ngày. Nếu đo "3 ngày sau khi đăng" thì thực tế dài 51–71 giờ tuỳ giờ đăng.
- Bản cập nhật Shorts ngày 01/10 cộng với đợt đăng dồn làm bẩn số liệu các tuần trước 05/10.
- Data API (view trọn đời) lệch với Analytics (theo cửa sổ). Ví dụ một bài: 28.459 so với 22.957.

Thợ cũng từng đưa số sai:

- "khung 10h30 tụt 50%", thực tế là 20%;
- "43 bài FS thua", thực tế khoảng 10;
- "sub tăng nhờ Long", thực tế Long chỉ mang khoảng 3% số sub.

Cách đo (`hf_brief.py`, chạy thứ Hai):

- **Cửa sổ.** Mỗi video đo trong 7 ngày PT kể từ ngày lên sóng. Chỉ đo khi Analytics đã có số của ngày cuối cửa sổ. Kết quả đã đóng thì cache lại, không đổi nữa.
- **Short.** Xếp hạng `engagedViews` trong cùng tuần ISO-PT, cùng kênh, và chỉ với tuần có ít nhất 15 short. Tuần từ 05/10 là "sạch"; tuần trước đó chỉ để tham khảo.
- **Long.** Mỗi tuần chỉ có 2 Long nên không xếp hạng trong tuần. So với trung vị 8 Long gần nhất, cộng mức giữ chân ở 2% đầu video.
- **Điểm rơi** (từ 24/10). Lấy chỗ rơi dốc nhất trên đường giữ chân của các short thấp nhất và cao nhất, kèm câu đang đọc lúc đó. Mỗi tuần sửa đúng một điểm rơi lặp lại.
- **Cầu bên ngoài.** Gợi ý tìm kiếm YouTube (miễn phí) và video nhiều view trong ngách (tốn quota tìm kiếm), lọc theo ngách, bỏ chủ đề kênh đã làm.

## Các phương án đã cân nhắc

- **So view thô giữa các tuần.** Lẫn hiệu ứng của thuật toán và của đợt đăng dồn.
- **Hồi quy nhiều biến, tự đổi chủ đề hoặc giờ đăng.** Dữ liệu sạch sau 01/10 chưa đủ. Giờ đăng chỉ tự đổi tối đa một giờ mỗi lần review (`hf_slots`).

## Hệ quả

- **Chưa đo được:**
  - "viewed vs swiped" (API không trả, dùng engagedViews/views thay thế, nên lệch Studio: 44% so với 50,1%);
  - `impressions` và CTR (API báo lỗi 400; CTR chỉ xem được trong Studio).
- **Mẫu nhỏ.** Long mỗi bài chỉ 12–624 view. Chỉ tin lần rơi ≥ 4 điểm, hoặc kiểu rơi lặp lại ở nhiều video.
- **Đọc chỉ số theo kênh.** Mỗi kênh có "đơn vị thắng" riêng:
  - FS thắng về lượng: 402,6k view trong 28 ngày, stay 50%, 0,89 sub/1k.
  - BUD thắng về chiều sâu: 2,34 sub/1k, 13% giờ xem trên TV, AVD Long 6,7 phút. CTR Long BUD 3,5% là điểm nghẽn.

## Bằng chứng

`hf_brief.py` (docstring), `hf_short_retention.py`, `hf_long_retention.py`, `hf_slots.py`, `chunks_cache/brief/metrics_{bud,fs}.json`, `output/cl_staging/phan_tich_studio_2026-10-22.md`, `tests/test_brief_drop_points.py`.
