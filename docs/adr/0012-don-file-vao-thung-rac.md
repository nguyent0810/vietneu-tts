# Dọn file sau khi đăng bằng cách chuyển vào Thùng rác, không xoá vĩnh viễn, và chỉ dọn khi YouTube đã xác nhận

Trạng thái: đã chấp nhận (02/10/2026, bổ sung 20/10 và 22/10).

Ổ đĩa đầy rất nhanh: một Long 30 phút cần khoảng 3 GB mp4, 3–6 GB file chương, và khoảng 12 GB tạm khi ghép cuối. Các sự cố đã gặp:

- **04/10:** đợt dọn lúc 3:30 sáng xoá mất bản render lại của F10/B10, vì `uploaded.json` vẫn trỏ id cũ. Chủ kênh đổ Thùng rác nên mất hẳn.
- **23/10:** short BUD đã đăng bị dọn mất mp4, nên bản TikTok phải render lại.

Quy trình:

1. Sau mỗi đợt đăng, chạy `hf_cleanup.py` ở chế độ thử.
2. Chạy `--apply` để chuyển file vào `~/.Trash/vieneu_tu_don/<ngày>/`.

Chỉ dọn video khi đủ ba điều kiện: có trong `uploaded.json`, YouTube báo `processed` đúng kênh, và video đã công khai hoặc đã hẹn giờ. Giữ lại `json`, `srt`, `txt` (vài KB). Cache giọng giữ 30 ngày, cache stock giữ 45 ngày.

## Các phương án đã cân nhắc

- **`rm` thẳng.** Không đảo ngược được.
- **Giữ hết.** Đầy đĩa giữa chừng khi đang render.
- **Job dọn tự động theo giờ.** Đã tắt ngày 20/10, vì dọn lúc không có người nhìn chính là nguyên nhân sự cố 04/10.

## Hệ quả

- Lead được dọn mà không cần hỏi (22/10), nhưng chỉ bằng cách chuyển vào Thùng rác. Đổ Thùng rác là việc của chủ kênh, vì dung lượng chỉ thật sự trống ra khi đổ. Ngày 24/10, Thùng rác giữ khoảng 21 GB.
- Không dọn bản render mới hơn `publishedAt` cộng 10 phút.
- Short BUD được giữ tới khi đã hẹn lên TikTok, hoặc 72 giờ sau giờ phát (ADR 0014).
- Render lại một video đã đăng thì gỡ id đó khỏi `uploaded.json` ngay, và ghi vào `uploaded_replaced.json`.
- Kiểm `df` trước mỗi lần render Long.

## Bằng chứng

`hf_cleanup.py` (docstring, `TIKTOK_WINDOW_H`), `tests/test_hf_cleanup_tiktok.py`, `output/cl_staging/retro/2026-10-23_lo_thay_25-10_tiktok.md`.
