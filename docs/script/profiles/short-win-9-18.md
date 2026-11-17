# Short thắng 9–18s — ngân sách riêng (PO17/11)
Chọn `audio_profile: short_win_9_18` cho bảng tra, câu kinh ngắn, biểu tượng. `style: daytable` tự chọn cùng profile vì đã có trên lịch. Đây là cấu hình dùng lại, không xin miễn từng bài. Không tự nhận dạng chỉ từ chữ “bảng” hoặc lane để tránh đổi nhầm truyện.

Ngân sách **tổng9–18s**, lời thường1–3 câu, không có sàn68–102 token của v2, không buộc insight/định nghĩa/cú lật theo khuôn v2. Trừ tail/nhạc đầu/khung tĩnh ≥3s khi dự trù: `tiếng ≈ giây lời × tốc độ cả nghỉ của đúng giọng / 60`, xem [bảng](../voice-rates.md); Short chưa có mẫu cùng giọng chỉ là ước tính. Đo thời lượng thật sau TTS ở phiên sản xuất, không gọi số token là giây. `duration_band: [9,18]` tận dụng guard band hiện có nếu spec có duration đo; profile không thêm cổng mới khi thiếu timing.

Bảng12s với một–hai câu được qua; BUD giữ nguồn đã kiểm, FS giữ code/tên chi/khung tham khảo, câu trọn và integrity vẫn áp dụng. Hình bảng/hero và khung giữ cuối ở shorts-lookup/studio; profile giữ cách mở bằng bảng đã thắng thay vì hook truyện. Dạng chỉ tay8s cũ là nhánh ngoài dải profile này, theo brief hiện có, không tự mở rộng dải9–18.
