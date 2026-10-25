# TikTok chỉ cho kênh BUD: mỗi ngày 3 trong 5 short YouTube, đăng trễ 3 ngày

Trạng thái: đã chấp nhận (22–23/10/2026).

Kênh TikTok @hanhtrinhgiaithoat là kênh Phật giáo, đã có 817 bài, trung vị khoảng 140 view. Ngày 23/10 chủ kênh muốn mọi short BUD mới đều lên TikTok trước khi file bị dọn. FS không có kênh TikTok phù hợp.

Quy trình:

- Mỗi ngày đăng 3 trong 5 short YouTube, lúc 06:00, 12:00 và 19:45.
- Lô YouTube ngày D lên TikTok ngày D+3. Khoảng trễ này cho 48 giờ số liệu YouTube để chọn bài, và vẫn nằm trong cửa sổ 72 giờ giữ file của `hf_cleanup`.
- Thứ tự ưu tiên khi chọn: dạng ngách mới, rồi bài thắng sau 48 giờ, rồi bài về vật trong chùa.
- Bật nhãn AI và kiểm nhạc.

## Các phương án đã cân nhắc

- **Đăng cả FS.** Nội dung không hợp kênh TikTok hiện có.
- **Đăng cả 5 bài mỗi ngày.** Dữ liệu ngoài (Buffer, TT Calculator) cho thấy từ 4 bài/ngày trở lên, view mỗi bài giảm khoảng 57%. Số này chưa được kiểm trên kênh ta.

## Hệ quả

- TikTok chỉ hẹn giờ được trên Studio web, xa nhất 10 ngày.
- Tải file qua trình duyệt giới hạn khoảng 10 MB, nên phải nén 2 lượt xuống dưới 9 MB.
- Bài đã hẹn không đổi được quyền riêng tư, chỉ xoá được, và việc xoá chủ kênh tự làm.
- Bố cục TikTok Studio đổi theo độ rộng cửa sổ, nên bấm theo toạ độ cũ có thể rơi vào nút khác. Đọc lại danh sách trong Studio trước khi dọn file.

## Bằng chứng

`output/cl_staging/tiktok/plan_tiktok_bud.json`, `hf_cleanup.py` (`TIKTOK_WINDOW_H = 72`), `output/cl_staging/retro/2026-10-23_lo_thay_25-10_tiktok.md`.
