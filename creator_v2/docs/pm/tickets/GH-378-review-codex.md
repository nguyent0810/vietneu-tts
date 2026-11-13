# GH-378: review câu chuyện Long CL Hoàng Kim Vinh (cl-hoang-kim-vinh), Codex làm model thứ hai

Kịch bản `data/long/cl-hoang-kim-vinh/script.md` do subagent Sonnet viết, Lead sửa một chỗ rào thuế ở CH04. Bước review câu chuyện (#286) cần một model khác họ. Hạn mức agy Argon đã hết, Grok không được dùng cho lời kể, nên lần này giao cho bạn.

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-ck11`, nhánh `long/cl-hoang-kim-vinh`. Mọi đường dẫn tính từ `creator_v2/` của worktree. Lead commit.
- Không chạy agent nào khác, không gọi mạng.

## Việc
1. Với mỗi file `data/long/cl-hoang-kim-vinh/story_review/chNN.prompt.md` (ch00 đến ch07), làm đúng yêu cầu ghi trong file. File đã gồm prompt của chủ kênh, 6 luật §13, lời đọc đánh số câu và factcheck.
   Ghi kết quả ra `data/long/cl-hoang-kim-vinh/story_review/chNN.md`, gồm 3 mục:
   - "Review": 4–6 đoạn cần sửa, mỗi đoạn có vấn đề, lý do và cách sửa.
   - "Bản viết lại": toàn chương.
   - "Cần xác minh".
2. Bản viết lại phải giữ đúng định dạng `script.md`:
   - mỗi dòng một câu;
   - `‖` cuối dòng cho chỗ ngừng dài;
   - lời trích dạng `» ... [TRÍCH DỊCH]`.
   **Không thêm dữ kiện nào ngoài `factcheck.md`.** Số âm tiết mỗi chương giữ trong khoảng ±10% bản cũ.
3. Luật riêng CL (`docs/pm/storytelling-guide.md` §13, sáu luật mạch kể): giữ trục "bốn mốc, bốn cách người ta kể"; mọi lời rào nguồn ("Wikipedia ghi", "sách 1930 ghi", "theo một cuốn hồi ức", nhãn GIAI THOẠI) phải giữ; không kể hộ động cơ; không bình luận chính trị; không thêm sự kiện, tên hay số ngoài factcheck.md; mọi câu [TRÍCH DỊCH] giữ nguyên chữ; tên Hán-Việt giữ như bản gốc (Trương Khiếu Lâm, Lư Tiểu Gia, Lộ Lan Xuân).
4. Ghép các "Bản viết lại" thành `data/long/cl-hoang-kim-vinh/script.v2.md`, giữ nguyên phần đầu file (khối thông tin, cấu trúc) và mục "Ghi chú kiểm chứng" cuối file của `script.md`. **Không ghi đè `script.md`.**

## Tiêu chí đạt
- Có đủ 14 file `chNN.md` (CH00–CH13) và `script.v2.md`.
- Chép `script.v2.md` ra một thư mục tạm có tên topic khác rồi chạy `script_lines.py` trên đó. Nếu không làm được, đếm bằng hàm `parse` và `gate` của `motion/long/script_lines.py` gọi từ Python:
  - không có lỗi gate;
  - tổng âm tiết 5.600–6.500 (bản gốc 5.715, đang sát đáy: ưu tiên làm dày cảnh và chuyển ý bằng dữ kiện đã có trong factcheck, không bịa);
  - không phát sinh cảnh báo NHIP_DEU, RAO_NGUON mới (bản cũ có 0).
- Ghi mọi file bằng Python utf-8, rồi grep để chắc không có `?` thay chữ có dấu.

## Báo cáo
`docs/pm/tickets/GH-378-review-report.md`, tiếng Việt có dấu. Gồm: tổng âm tiết cũ và mới theo chương, số cảnh báo lint cũ và mới, và danh sách mục "Cần xác minh" gộp lại.

Không render, không commit, không đăng.

## Thêm (Lead 13/11, bài học Long trước)
- Mỗi câu ≤ 32 âm tiết (cổng craft chặn > 35). Trong 8 câu đầu phải có một câu hỏi. Có gọi "bạn" và có ít nhất một ‖.
- Sau khi ghép `script.v2.md`, chạy từ Python `craft.audio_problems(script_lines.parse(text))` (motion/long/craft.py) trên nội dung v2: phải ra danh sách rỗng.
- **Ghi mọi file bằng Python `open(..., 'w', encoding='utf-8')`. Không dùng PowerShell để ghi** (lượt trước bạn làm mất dấu tiếng Việt thành '?'). Sau khi ghi, kiểm bằng Python không có chuỗi `??` trong các file đã ghi.
