# GH-395-check (agy): NGƯỜI SOÁT kịch bản v3 Địch Nhân Kiệt

Vai của bạn theo `docs/pm/storytelling-guide.md` §14 mục 2: người soát CHỈ chặn 4 thứ, KHÔNG sửa giọng văn, KHÔNG cắt cảnh phỏng dựng `{pd}` hay giả thuyết:
1. Câu nói sai dữ kiện so với `data/long/cl-dich-nhan-kiet/factcheck.md` (tên, năm, nơi, quan hệ, ai làm gì).
2. Con số/ngày không có trong factcheck.md.
3. Lời trích `»` / `[TRÍCH DỊCH]` không khớp nguyên văn trong factcheck.md.
4. Bịa lời nói hay cảm xúc cho người còn sống; nội dung nguy hiểm.

Đọc `data/long/cl-dich-nhan-kiet/script.v3.md` và `factcheck.md`. Ghi báo cáo `docs/pm/tickets/GH-395-check-report.md` (tiếng Việt, Python `open(..., 'w', encoding='utf-8')`, không PowerShell): bảng các lỗi tìm được — chương · câu (trích nguyên câu) · loại lỗi (1–4) · dòng factcheck liên quan · cách sửa tối thiểu (một câu thay thế giữ giọng kể). Nếu không có lỗi loại nào thì ghi rõ "0". Không sửa file khác, không commit, không gọi mạng.
