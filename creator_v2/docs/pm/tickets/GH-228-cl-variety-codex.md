# GH-228: 12 Short CL đang dùng chung một khuôn, phải phá khuôn

Lead soát contact sheet (`output/stier/cl-*/final_sheet.jpg`). Bài nào cũng đi đúng một trình tự:
1. ảnh "HỒ SƠ LỊCH SỬ";
2. thẻ tên kẹp giấy;
3. ảnh;
4. mốc năm nhỏ trên nền trống;
5. slam **"DẤU VẾT"**, lặp 2–3 khung, cùng một chữ ở mọi bài;
6. thẻ "HỒ SƠ / MỐC".

12 Short giống nhau như vậy là dấu hiệu nội dung sản xuất hàng loạt theo khuôn, YouTube coi là spam (CLAUDE.md, `motion/long/RESEARCH-million-views.md`).

**Việc:** sửa 12 spec trong `docs/pm/tickets/GH-228-cl-shorts1-report.md`:
- **Bỏ chữ "DẤU VẾT".** Mỗi slam dùng một cụm **lấy từ chính lời của bài đó**, 2–4 chữ, ví dụ "LƯỠI BÒ BỊ CẮT", "20 TỘI", "NGHIÊN MỰC". Không bài nào trùng cụm slam với bài khác.
- **Đổi trình tự cảnh** để không 2 bài nào có cùng chuỗi loại cảnh. Cảnh mở chia đều giữa photo, quote, date lớn, file và ledger. Dùng thêm map, timeline có nhiều mốc, quote trích nguyên văn (nếu lời có), split 2 ảnh.
- **Không còn khung gần trống:** mốc năm nhỏ trên nền đen phải có ảnh nền, hoặc đổi thành date lớn.
- Giữ ≥ 4 ảnh khác nhau mỗi bài, lời không đổi, preflight OK.

Sửa bằng Python UTF-8, chạy preflight cho cả 12 bài và lệnh kiểm mất dấu. Không render, không commit.

**Báo cáo** `docs/pm/tickets/GH-228-cl-variety-report.md`: bảng 12 bài gồm chuỗi loại cảnh mới và các cụm slam.
