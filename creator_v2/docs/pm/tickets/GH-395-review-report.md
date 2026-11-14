# Báo cáo GH-395: review kịch bản Địch Nhân Kiệt

Các file review gồm vấn đề, cách sửa cụ thể và toàn bộ chương tương ứng. Sáu luật §13 được áp vào việc gộp, giới hạn nguồn, giữ nhịp diễn biến, điểm đọng bằng dữ kiện, trật tự thời gian và không kể hộ động cơ; những chỗ phải duyệt tiếp nằm ở từng mục «Cần xác minh». Kịch bản gốc và phần ghi chú kiểm chứng được giữ nguyên.

## Độ dài và kiểm tra lời đọc

| Chương | Cũ | Mới | Thay đổi |
|---|---:|---:|---:|
| CH00 | 180 | 169 | -6.1% |
| CH01 | 309 | 303 | -1.9% |
| CH02 | 400 | 380 | -5.0% |
| CH03 | 293 | 295 | +0.7% |
| CH04 | 374 | 359 | -4.0% |
| CH05 | 519 | 527 | +1.5% |
| CH06 | 451 | 444 | -1.6% |
| CH07 | 456 | 453 | -0.7% |
| CH08 | 296 | 289 | -2.4% |
| CH09 | 407 | 408 | +0.2% |
| CH10 | 413 | 414 | +0.2% |
| CH11 | 510 | 517 | +1.4% |
| CH12 | 441 | 447 | +1.4% |
| CH13 | 613 | 608 | -0.8% |
| TOTAL | 5662 | 5613 | |

Dùng `motion/long/script_lines.py` qua `parse` và `gate`; dùng cách đếm số từ của chính CLI cho âm tiết. Cảnh báo phát ra từ `gate`: cũ 0, mới 0; riêng `NHIP_DEU` và `RAO_NGUON` đều 0 ở cả hai bản. `beat_warnings`: cũ 0, mới 0 sau bổ sung các dấu nhịp. `craft.audio_problems` trả `[]`; không có câu vượt 32 từ theo cách đếm của script; có câu hỏi trong 8 câu đầu, có «bạn» và có dấu `‖`.

## Đối chiếu bản dịch

Đã đối chiếu 36 câu có nhãn `[TRÍCH DỊCH]` với nguyên văn ghi trong factcheck; các câu không liệt kê dưới đây được giữ nguyên chữ. Đây là đối chiếu trên tư liệu được cung cấp, chưa phải thẩm định Hán văn độc lập từ nguồn gốc. Các thay đổi cần Lead duyệt:

| Chương | Câu cũ | Câu mới | Lý do |
|---|---|---|---|
| CH11 | Văn hoàng đế dãi gió dầm mưa, xông pha mũi tên hòn đạn để định thiên hạ, rồi truyền cho con cháu. [TRÍCH DỊCH] | Văn hoàng đế dãi gió dầm mưa, đích thân xông pha giáo mác và mũi tên để định thiên hạ, rồi truyền cho con cháu. [TRÍCH DỊCH] | 親冒鋒鏑 có ý đích thân xông pha binh khí và tên. |
| CH11 | Bệ hạ lập con, ngàn năm sau còn được thờ ở Thái miếu. Lập cháu, chưa từng có cháu làm thiên tử mà thờ cô trong miếu. [TRÍCH DỊCH] | Bệ hạ lập con, ngàn năm sau được thờ ở Thái miếu, nối thờ mãi mãi. Lập cháu, chưa từng có cháu làm thiên tử mà thờ cô trong miếu. [TRÍCH DỊCH] | Bản cũ bỏ ý 承繼無窮: sự nối tiếp không dứt. |
| CH11 | Bậc vương giả lấy bốn biển làm nhà. Việc gì chẳng là việc nhà của bệ hạ? [TRÍCH DỊCH] | Bậc vương giả lấy bốn biển làm nhà; người trong bốn biển đều là bề tôi. Việc gì chẳng là việc nhà của bệ hạ? [TRÍCH DỊCH] | Bản cũ bỏ mệnh đề 四海之內，孰非臣妾. |
| CH05 | Nếu nhất định tha Bản Lập, xin vứt thần ra nơi không người, để răn kẻ trung trinh về sau. [TRÍCH DỊCH] | Nếu nhất định tha Bản Lập một cách thiên vị, xin vứt thần ra nơi không người, để răn kẻ trung trinh về sau. [TRÍCH DỊCH] | 曲赦 là tha thiên vị, bản cũ thiếu ý tha trái lẽ. |
| CH06 | Chính sứ quân Địch đã cứu sống các ngươi! [TRÍCH DỊCH] | Sứ quân Địch của chúng ta đã cứu sống các ngươi sao! [TRÍCH DỊCH] | Nguyên văn 我狄使君活汝邪 có chữ chúng ta và lời hỏi ngạc nhiên 邪. |
| CH08 | Trời đất chứng giám, lại sai Địch Nhân Kiệt làm chuyện này sao! [TRÍCH DỊCH] | Trời đất lại sai Địch Nhân Kiệt làm chuyện này sao! [TRÍCH DỊCH] | 皇天后土遣 hỏi trời đất sai làm việc ấy; không có ý chứng giám. |

## Cần xác minh gộp

- **CH10:** Năm và thứ tự việc ở Bành Trạch theo bản tiếng Trung; đối chiếu lại thời điểm câu chuyện Lâu Sư Đức so với các sự kiện Khiết Đan.
- **CH11:** Đối chiếu sắc thái sáu câu dịch đã chỉnh trên toàn bài với người giỏi Hán văn; hai giấc mơ khác nhau không tự chứng minh là dị bản của một sự kiện.
- **CH12:** Chương cố ý lùi về 697 sau chương 698 theo cấu trúc có sẵn; đã báo rõ hồi trước. Kiểm lại âm đọc tên Mặc Xuyết theo nguyên văn 默啜.
- **CH13:** Năm mất 700 hay 704 và vị trí mộ còn có ý kiến khác nhau; thời điểm Trương Giản Chi làm tể tướng cần được nêu rõ nếu Lead tái cấu trúc niên biểu.
- **CH00:** Năm bị tố: Tư trị thông giám và Wikipedia tiếng Anh ghi 692, Wikipedia tiếng Trung ghi 693; cần Lead chọn cách rào ngay ở cảnh mở. Vị trí Lạc Dương của cảnh mở cần đối chiếu lại tại nguồn đã ghi.
- **CH01:** Tiểu thuyết Địch công án, truyện van Gulik và các trang phim chưa được đọc trực tiếp; các thông tin hiện dựa vào Wikipedia như factcheck ghi.
- **CH02:** Nghĩa của 門人 trong chuyện người bị hại cần đối chiếu để xác nhận cách gọi «người trong nhà»; chi tiết chuyện nhỏ chỉ có trong hai bộ Đường thư đã nêu.
- **CH03:** Con số 17.000 là người theo hai bộ sử nhưng Wikipedia tiếng Anh ghi vụ; không có bảng kê từng vụ trong nguồn đã mở.
- **CH04:** Đối chiếu lại thứ tự câu can và tiền lệ Hán Văn Đế giữa các bộ sử, vì chương ghép chi tiết Tân Đường thư với lời dịch Tư trị thông giám.
- **CH05:** Vụ Kỳ Châu chỉ thấy trong Tân Đường thư; phân biệt lời kể về đền Đố Nữ với kết luận về toàn bộ các nguồn khác chưa đọc.
- **CH06:** Ba nhóm số là hộ bị liên lụy, người bị tịch thu và người bị án tử, không thể cộng hoặc coi là ba bản đếm cùng một đối tượng.
- **CH07:** Đối chiếu thời điểm Nghiêm Thiện Tư được gọi về và mức độ khái quát các vụ tru họ theo đúng lời Tư trị thông giám; không có nguồn mở mới trong lượt này.
- **CH08:** Năm 692 và 693 khác nhau giữa các bản đã ghi; bản dịch câu 皇天后土遣 cần người giỏi Hán văn rà lại sắc thái câu hỏi.
- **CH09:** Đối chiếu nhân vật nhận ra chữ ký giả và quan hệ thời gian giữa bức thư của Quang Viễn với lời tố cáo của cậu bé; không suy ra một chuỗi nhân quả duy nhất.

## Cổng dựng và phạm vi

Đã chạy `python scripts/long_gate.py cl-dich-nhan-kiet --min-syl 1900`: **TRƯỢT, 32 lỗi**. Cổng kiểm bản `script.md` gốc và dữ liệu dựng của topic, không kiểm riêng `script.v2.md`; hiện thiếu HUD và cảnh cho cả 14 chương, chưa có TTS, thiếu các trường xuất bản và URL trong spec. Ticket chỉ giao review, cấm render; không tạo cảnh, TTS hay sửa spec ngoài phạm vi. Không thể báo cổng ĐẠT.

Đã dùng phương án ticket cho phép: `script_lines.parse` và `script_lines.gate` trên nội dung v2 trong bộ nhớ, cùng `craft.audio_problems`. Không chạy render, không gọi mạng, không ghi đè `script.md`, không commit hoặc đăng. Đối chiếu nguyên văn dựa trên factcheck được bàn giao; chưa mở lại URL vì ticket cấm gọi mạng. Chưa có clip sheet hoặc thumbnail trong phạm vi review này.

Môi trường: ticket ghi worktree `D:\Tools\Youtube Creator v2\wt-ck11\creator_v2`, nhưng các file đầu vào không tồn tại tại đường dẫn đó. Công việc được thực hiện trong workspace được cung cấp `D:\Tools\Youtube Creator v2\wt-dnk\creator_v2`, nơi có đủ 14 prompt và kịch bản.
