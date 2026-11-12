# GH-286: review câu chuyện Long Lưu Gù (cl-luu-gu), Codex làm model thứ hai

Kịch bản `data/long/cl-luu-gu/script.md` do subagent Sonnet viết. Bước review câu chuyện (#286) cần một model khác họ. Hạn mức agy Argon đã hết, Grok không được dùng cho lời kể, nên lần này giao cho bạn.

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-luugu`, nhánh `long/cl-luu-gu`. Mọi đường dẫn tính từ `creator_v2/` của worktree. Lead commit.
- Không chạy agent nào khác, không gọi mạng.

## Việc
1. Với mỗi file `data/long/cl-luu-gu/story_review/chNN.prompt.md` (ch00 đến ch13), làm đúng yêu cầu ghi trong file. File đã gồm prompt của chủ kênh, 6 luật §13, lời đọc đánh số câu và factcheck.
   Ghi kết quả ra `data/long/cl-luu-gu/story_review/chNN.md`, gồm 3 mục:
   - "Review": 4–6 đoạn cần sửa, mỗi đoạn có vấn đề, lý do và cách sửa.
   - "Bản viết lại": toàn chương.
   - "Cần xác minh".
2. Bản viết lại phải giữ đúng định dạng `script.md`:
   - mỗi dòng một câu;
   - `‖` cuối dòng cho chỗ ngừng dài;
   - lời trích dạng `» ... [TRÍCH DỊCH]`.
   **Không thêm dữ kiện nào ngoài `factcheck.md`.** Số âm tiết mỗi chương giữ trong khoảng ±10% bản cũ.
3. Ưu tiên sửa chỗ lint cảnh báo, chạy `python motion/long/script_lines.py cl-luu-gu` để xem:
   - NHIP_DEU ở ch04, ch06, ch08, ch12 (chuỗi câu ngắn cùng khuôn "Sử không kể… Sử không ghi…");
   - RAO_NGUON ở ch11.
   Bỏ hoặc gộp các câu giảng giải chung chung. Mỗi chương chỉ rào nguồn một lần.
4. Ghép các "Bản viết lại" thành `data/long/cl-luu-gu/script.v2.md`, giữ nguyên phần đầu file (khối thông tin, cấu trúc) và mục "Ghi chú kiểm chứng" cuối file của `script.md`. **Không ghi đè `script.md`.**

## Tiêu chí đạt
- Có đủ 14 file `chNN.md` và `script.v2.md`.
- Chép `script.v2.md` ra một thư mục tạm có tên topic khác rồi chạy `script_lines.py` trên đó. Nếu không làm được, đếm bằng hàm `parse` và `gate` của `motion/long/script_lines.py` gọi từ Python:
  - không có lỗi gate;
  - tổng âm tiết 5.800–6.600;
  - số cảnh báo NHIP_DEU và RAO_NGUON ít hơn bản cũ (bản cũ có 5).
- Ghi mọi file bằng Python utf-8, rồi grep để chắc không có `?` thay chữ có dấu.

## Báo cáo
`docs/pm/tickets/GH-286-luugu-report.md`, tiếng Việt có dấu. Gồm: tổng âm tiết cũ và mới theo chương, số cảnh báo lint cũ và mới, và danh sách mục "Cần xác minh" gộp lại.

Không render, không commit, không đăng.
