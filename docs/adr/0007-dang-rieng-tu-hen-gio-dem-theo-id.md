# Luôn đăng ở chế độ riêng tư kèm hẹn giờ; đếm lịch theo ID video chứ không theo playlist; mỗi kênh tối đa 24 upload trong 24 giờ

Trạng thái: đã chấp nhận (20/10/2026).

Đăng công khai ngay thì mất cơ hội soát lại và không gỡ êm được. Ta cũng từng đếm sai lịch vì tin playlist "uploads":

- Playlist bỏ sót video riêng tư có `publishAt`. Ngày 28/09 sót 256 video. Ngày 20/10, Lead báo kênh có "0 video đã hẹn" trong khi thực tế là 71.
- Playlist xê dịch ngay sau mỗi lần đăng, nên vừa đếm lặp vừa đếm sót.
- Thông báo "HẾT QUOTA" ngày 20/10 thực ra là `UploadPacingHold`: trần tự đặt 24 upload trong 24 giờ cho mỗi kênh trong `youtube_upload.py`, không phải quota của API.

Quyết định:

- Mọi uploader mặc định chạy thử (dry-run); phải có `--confirm` mới đăng thật.
- Đăng `private` kèm `publishAt`, đặt `language="vi"`, có phụ đề `.vi.srt`.
- Dò khung giờ trống bằng `hf_coverage.occupied_slots`. Công cụ này gộp playlist, sổ `uploaded.json` và sổ ID bền vững, rồi hỏi API theo từng ID.
- Đăng xong thì kiểm lại từng ID bằng `videos.list`: phải là riêng tư, đúng `publishAt`, đúng kênh.
- `hf_coverage` bắt buộc khai `--credentials`, vì mặc định cũ trỏ sang kênh khác.

## Các phương án đã cân nhắc

- **Đăng công khai ngay.** Mất bước soát.
- **Đếm bằng playlist.** Sai, như các ví dụ trên.
- **Để thợ tự đăng.** Bộ phân loại an toàn chặn, và rủi ro khi để thợ ghi ra hệ thống ngoài (xem ADR 0008).

## Hệ quả

- **Phân quyền:**
  - Lead được tự hẹn giờ mà không cần hỏi (từ 20/10).
  - Xoá video, ẩn video, đổi lịch đã hẹn, hoặc đăng công khai ngay thì phải hỏi chủ kênh.
  - "Gỡ lịch" nghĩa là chuyển về riêng tư không hẹn giờ, và ghi sổ khôi phục trước khi gỡ.
- Short hoàng đạo theo ngày mà trễ lịch thì **huỷ, không dời**: qua ngày rồi thì bài hết giá trị dự báo.
- Trước một đợt đăng, cộng số bài của mọi chuỗi trên cùng kênh. Từ 6 bài trở lên thì chia ra nhiều ngày. Mốc được đăng tiếp = giờ của bài cũ nhất trong cửa sổ cộng 24 giờ.
- Từ PR #29, Long phải qua `seo_check` trước khi đăng: lỗi mức ERROR thì dừng (ADR 0016).

## Bằng chứng

`hf_coverage.py` (docstring), `youtube_upload.py` (`GUARDED`), `output/cl_staging/long/upload_long.py`, `output/cl_staging/retro/2026-10-20_*.md`, commit `3725e1d`.
