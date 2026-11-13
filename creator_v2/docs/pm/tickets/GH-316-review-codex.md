# GH-316: review câu chuyện Long CK bài 10 (ck-c7-mo-tai-khoan-phi), Codex làm model thứ hai

Kịch bản `data/long/ck-c7-mo-tai-khoan-phi/script.md` do subagent Sonnet viết, Lead sửa một chỗ rào thuế ở CH04. Bước review câu chuyện (#286) cần một model khác họ. Hạn mức agy Argon đã hết, Grok không được dùng cho lời kể, nên lần này giao cho bạn.

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-ck10`, nhánh `long/ck-c7-mo-tai-khoan-phi`. Mọi đường dẫn tính từ `creator_v2/` của worktree. Lead commit.
- Không chạy agent nào khác, không gọi mạng.

## Việc
1. Với mỗi file `data/long/ck-c7-mo-tai-khoan-phi/story_review/chNN.prompt.md` (ch00 đến ch07), làm đúng yêu cầu ghi trong file. File đã gồm prompt của chủ kênh, 6 luật §13, lời đọc đánh số câu và factcheck.
   Ghi kết quả ra `data/long/ck-c7-mo-tai-khoan-phi/story_review/chNN.md`, gồm 3 mục:
   - "Review": 4–6 đoạn cần sửa, mỗi đoạn có vấn đề, lý do và cách sửa.
   - "Bản viết lại": toàn chương.
   - "Cần xác minh".
2. Bản viết lại phải giữ đúng định dạng `script.md`:
   - mỗi dòng một câu;
   - `‖` cuối dòng cho chỗ ngừng dài;
   - lời trích dạng `» ... [TRÍCH DỊCH]`.
   **Không thêm dữ kiện nào ngoài `factcheck.md`.** Số âm tiết mỗi chương giữ trong khoảng ±10% bản cũ.
3. Luật riêng CK (`docs/pm/storytelling-guide.md`): không hứa lợi nhuận; chị Hạnh và mọi số giả định giữ nhãn VÍ DỤ GIẢ ĐỊNH; không nêu tên công ty chứng khoán, ngân hàng, ứng dụng, mã cổ phiếu. Mọi phép tính trong bản viết lại phải đúng số học: tự tính lại bằng Python và đối chiếu "Ghi chú kiểm chứng". Lời rào về mức thuế 0,1% (CH04) phải giữ: chưa có nguồn xác nhận nguyên văn.
4. Ghép các "Bản viết lại" thành `data/long/ck-c7-mo-tai-khoan-phi/script.v2.md`, giữ nguyên phần đầu file (khối thông tin, cấu trúc) và mục "Ghi chú kiểm chứng" cuối file của `script.md`. **Không ghi đè `script.md`.**

## Tiêu chí đạt
- Có đủ 8 file `chNN.md` và `script.v2.md`.
- Chép `script.v2.md` ra một thư mục tạm có tên topic khác rồi chạy `script_lines.py` trên đó. Nếu không làm được, đếm bằng hàm `parse` và `gate` của `motion/long/script_lines.py` gọi từ Python:
  - không có lỗi gate;
  - tổng âm tiết 2.350–2.900;
  - không phát sinh cảnh báo NHIP_DEU, RAO_NGUON mới (bản cũ có 0).
- Ghi mọi file bằng Python utf-8, rồi grep để chắc không có `?` thay chữ có dấu.

## Báo cáo
`docs/pm/tickets/GH-316-review-report.md`, tiếng Việt có dấu. Gồm: tổng âm tiết cũ và mới theo chương, số cảnh báo lint cũ và mới, và danh sách mục "Cần xác minh" gộp lại.

Không render, không commit, không đăng.
