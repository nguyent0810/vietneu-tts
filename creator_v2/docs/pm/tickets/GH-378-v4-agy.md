# GH-378-v4 (agy Gemini): hoàn thiện lời Long Hoàng Kim Vinh từ bản đã soát

Bản bạn viết (v3) đã được người soát sửa thành `data/long/cl-hoang-kim-vinh/script.v3c.md`. Đọc bảng sửa `docs/pm/tickets/GH-378-v3-check.md`: 111 chỗ sai dữ kiện, 81 chỗ chi tiết bịa bị cắt (còng số tám, xà lim, cắt máu ăn thề, "hàng chục nghìn tay anh chị", quét đường trước cổng…). Bản v3c chỉ còn 4.567 âm tiết — dưới sàn sản xuất 5.000; cần 5.600–6.500.

Việc: viết `data/long/cl-hoang-kim-vinh/script.v4.md` từ v3c, GIỮ mọi sửa của người soát, kéo dài bằng:
- cảnh phỏng dựng đúng luật (§14 storytelling-guide): chỉ không gian, thời tiết, đồ vật, người vô danh; báo bằng lời "hãy hình dung…"/"có lẽ…" và `{pd}` cuối câu; KHÔNG gán hành động/lời/nội tâm cụ thể cho nhân vật thật nếu factcheck không có;
- chi tiết có thật trong `factcheck.md` chưa dùng (đọc kỹ factcheck, ưu tiên chi tiết đắt, xung đột, hệ quả);
- câu hỏi giữ chân, nhịp kể.
Tuyệt đối không thêm sự kiện, con số, tên, chức danh, lời trích mới ngoài factcheck. Giữ trục nhân vật + cái giá, cold open sốc, rào nguồn ≤ 8%, câu ≤ 32 âm tiết, định dạng như v3c.

Kiểm bằng Python trên v4: `motion/long/script_lines.py` parse+gate == [], `motion/long/craft.py` audio_problems == [], tổng âm tiết 5.600–6.500. Ghi file bằng Python `open(..., 'w', encoding='utf-8')`, không PowerShell; không sửa file khác; không commit; không gọi mạng. Báo cáo `docs/pm/tickets/GH-378-v4-report.md`: âm tiết, cảnh {pd} thêm, chi tiết factcheck mới dùng (kèm dòng factcheck).
