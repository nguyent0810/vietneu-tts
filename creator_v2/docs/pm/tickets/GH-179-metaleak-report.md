# Cổng META_LEAK / SOURCE_DENSITY trong `script_lines.gate`: báo cáo

Codex làm, Lead chỉnh danh sách từ khóa. Bản gốc của báo cáo bị mất dấu ở phần trích, đã viết lại.

- **`META_LEAK` (chặn):** câu sẽ đọc có thuật ngữ chắc chắn là ghi chú sản xuất: lời đọc, brief, mô-típ, motif, infobox, prompt, factcheck, tts, "kịch bản này", "trên hình", "plan đã". Cũng chặn mẫu tự nói về cấu trúc: "(sẽ) quay lại/đóng/mở ở chương …", "vòng thứ … đóng", "cảnh ấy ta không dựng".
- **`SOURCE_DENSITY` (cảnh báo):** một chương nhắc wikipedia, bách khoa, bài tiếng Việt/Anh, cùng trang quá 1 lần.
- **Lead bỏ khỏi danh sách chặn** các từ mà bản đầu của Codex bắt nhầm khi chạy trên các Long đã có: "kịch bản" (CK dùng theo nghĩa tình huống), "trên màn hình" (MIM/CK kể về điện thoại, máy tính), "render", "agent" (MIM nói về AI agent).
- **Chạy trên mọi `data/long/*/script.md`:** chỉ `hoa-than` bản 1 bị chặn (22 câu, đúng lỗi Lead đã thấy). Các Long khác không có `META_LEAK`.
- **Test:** toàn bộ `tests/` xanh.
