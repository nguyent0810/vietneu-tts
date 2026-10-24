# Một Lead điều phối nhiều thợ qua hàng đợi file; phản biện từ ngoài chỉ để tham khảo, Lead có quyền phủ quyết bằng số liệu

Trạng thái: đã chấp nhận (19–22/10/2026).

Hạn mức của nhà cung cấp LLM chính (Claude) có giới hạn, và chủ kênh không muốn ngồi gửi lệnh liên tục. Mặt khác, thợ thường báo "đạt" mà sai: 15/16 lỗi tháng 10 đã lọt qua bước tự kiểm của thợ. Các kiểu lỗi: bịa tên file Commons, gõ tay số liệu, báo đã xem ảnh mà không mở ảnh.

Mô hình được chọn:

- **Lead (Claude).** Viết ticket nhỏ vào `output/cl_staging/grok/queue/*.md`; chọn đề; khoá dữ kiện; render Long; đăng; dọn; viết retro.
- **Thợ.** Vòng lặp `loop_v3.sh` giao ticket cho thợ theo thứ tự ưu tiên Agy > Grok > Codex. `worker_status.py` phân biệt ba kiểu hết hạn mức chỉ bằng chữ ký lỗi trong 60 dòng log cuối:
  - reset: tin vào giờ reset;
  - hết số dư: giãn 1–12 giờ;
  - giới hạn tốc độ: chờ 15 phút.
- **Báo cáo.** Thợ báo cáo ≤ 300 chữ trong `grok/reports/`. Chỉ được ghi "đã kiểm" khi dán kèm output.
- **Phản biện.** Agy, Gemini, Codex được dùng để phản biện kế hoạch, cho góc nhìn nhiều chiều. Lead kiểm từng ý bằng số liệu thật rồi mới làm theo.

## Các phương án đã cân nhắc

- **Lead làm hết.** Tốn hạn mức, nghẽn ở một chỗ.
- **Giao thợ đăng YouTube.** Bị bộ phân loại an toàn chặn, và rủi ro khi để thợ ghi ra hệ thống ngoài.
- **Tin phản biện ngoài như kết luận.** Các ví dụ phản biện từng sai:
  - "2027 thắng nhờ tìm kiếm", trong khi thực tế 95,8% view đến từ feed;
  - Codex nói sai về nạp âm;
  - thợ ghi "khung 10h30 tụt 50%", trong khi thực tế chỉ 20%.

## Hệ quả

- Có 20 luật thợ trong `rules.md`.
- Task lớn phải chia nhỏ: Grok từng hết 150 lượt giữa chừng.
- Thợ không chạy render thật (`hf_batch_render --only`), mà chỉ gọi các hàm chỉ-kiểm. Thợ cũng không tự cài thành phần HyperFrames.
- Mọi con số thợ đưa ra phải được Lead tính lại.
- Bẫy công cụ:
  - Codex CLI: lời nhắn phải đặt **trước** `-i`, vì `-i` nuốt mọi tham số phía sau; cần `</dev/null` để khỏi treo; sandbox không có mạng.
  - Agy: lệnh thử nhẹ có thể báo OK trong khi task thật vẫn đang hết hạn mức.

## Bằng chứng

`output/cl_staging/grok/rules.md`, `worker_status.py`, `tests/test_worker_status.py`, `trao_doi/04_chot.md` (bảng "Ai đúng ở đâu").
