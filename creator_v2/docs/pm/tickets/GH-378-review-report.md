# GH-378 — báo cáo review câu chuyện

**Trạng thái: chưa đạt toàn bộ cổng bàn giao.** Đã viết đủ 14 bản review và kịch bản v2, nhưng long_gate trượt vì chưa có cảnh, TTS và cấu hình xuất bản; không tự nhận hoàn tất.

## Phạm vi

- Đã review CH00–CH13: mỗi file có 4 đoạn review, bản viết lại và mục cần xác minh. Ticket phần việc ghi CH00–CH07 nhưng tiêu chí yêu cầu 14 chương; đủ 14 prompt nên xử lý cả 14.
- Ghép vào `data/long/cl-hoang-kim-vinh/script.v2.md`, giữ phần đầu và ghi chú kiểm chứng cuối; không ghi đè `script.md`. Giữ các câu trích dịch nguyên chữ, nhãn nguồn và trục bốn mốc.
- Không gọi mạng, không chạy agent khác, không render, không commit, không đăng. Các thông tin về việc nguồn từng mở được lấy từ factcheck có sẵn; chưa tự kiểm lại trong lượt này theo lệnh cấm mạng.

## Âm tiết theo chương

Đếm bằng `len(script_lines.spoken_text([chapter]).split())` sau `script_lines.parse`; cách này cho bản gốc đúng 5.715 như ticket.

| Chương | Cũ | V2 | Chênh lệch |
|---|---:|---:|---:|
| CH00 | 194 | 191 | -1.55% |
| CH01 | 233 | 243 | +4.29% |
| CH02 | 469 | 473 | +0.85% |
| CH03 | 433 | 437 | +0.92% |
| CH04 | 468 | 488 | +4.27% |
| CH05 | 228 | 249 | +9.21% |
| CH06 | 402 | 397 | -1.24% |
| CH07 | 514 | 494 | -3.89% |
| CH08 | 425 | 414 | -2.59% |
| CH09 | 557 | 566 | +1.62% |
| CH10 | 575 | 577 | +0.35% |
| CH11 | 493 | 506 | +2.64% |
| CH12 | 418 | 417 | -0.24% |
| CH13 | 306 | 299 | -2.29% |
| **Tổng** | **5715** | **5751** | **+0.63%** |

Tổng nằm trong 5.600–6.500; từng chương nằm trong ±10% so với bản gốc.

## Các cổng và cảnh báo

- Gọi trực tiếp `script_lines.parse` và `script_lines.gate` bằng Python cho từng nội dung: cả bản cũ và v2 đều trả `[]`, không lỗi integrity.
- `craft.audio_problems(script_lines.parse(text))` cho v2: `[]`. Các câu lời đọc không quá 32 âm tiết theo cách đếm từ của cổng; có câu hỏi trong tám câu đầu, có “bạn” và dấu ngừng dài.
- Toàn bộ các câu đánh dấu trích dịch trong v2 khớp từng chữ với bản gốc. Mỗi phần “Bản viết lại” trùng nội dung chương tương ứng trong v2.
- Cảnh báo phát ra khi gọi gate:
  - `META_NGUOI_KE`: cũ 1, v2 1.
  - `NHAY_MOC`: cũ 25, v2 25.
  - `RAO_NGUON`: cũ 1, v2 1.
  - `SOURCE_DENSITY`: cũ 9, v2 11.
- `NHIP_DEU`: cũ 0, v2 0; `RAO_NGUON`: cũ 1, v2 1. Thực tế bản cũ có một cảnh báo CH09, khác nhận định “bản cũ có 0” trong ticket; không phát sinh thêm cảnh báo loại này.
- `beat_warnings`: cũ 34 và v2 41 cảnh báo `NHIP_30S`; bản v2 có nhiều cảnh báo hơn, cần Lead nghe lại nhịp. Không lẫn loại này với `NHIP_DEU`.
- Đã chạy `python scripts/long_gate.py cl-hoang-kim-vinh --min-syl 1900`: **TRƯỢT (33 lỗi)**, mã thoát 1. Lệnh đọc topic hiện tại và `script.md`, không kiểm nội dung v2. Các lỗi gồm thiếu HUD và loại cảnh ở 14 chương, chưa TTS, thời lượng/cảnh, thiếu trường `spec.youtube`, nguồn công khai trong spec và bảng SAY.
- Ticket chỉ giao review và cấm render; việc tạo cảnh, cấu hình sản xuất và TTS nằm ngoài phạm vi được giao. Cần Lead quyết định ticket sản xuất tiếp theo và chạy lại long_gate sau khi hoàn thành phần đó.
- Kiểm UTF-8 và chuỗi `hai dấu hỏi liên tiếp` bằng Python trên các file đã viết; dấu `?` đơn trong lời đọc là dấu hỏi có chủ ý.

## Các mục cần xác minh gộp

- **CH00:** Toàn văn bản tự thú chưa mở được; câu trích chỉ đối chiếu qua cụm chữ được hai nguồn dẫn lại.
- **CH01:** Trang phim được kiểm không khẳng định nhân vật Bến Thượng Hải dựa trên Hoàng Kim Vinh; không suy diễn.
- **CH02:** Ngày sinh giữa hai bản bách khoa khác nhau; năm vào sở được ghi là 1892 hoặc 1900; nghề của cha chưa rõ có thể đồng thời hay không.
- **CH03:** Năm lên đốc sát trưởng lệch giữa các nguồn; giai thoại dàn cảnh cướp thiếu nguồn dẫn; trang về cấp bậc và trang về thuốc phiện là hai trang khác nhau.
- **CH04:** Chưa biết tác giả cụ thể của mục và Hoàng có đọc trước khi in không; sách không gán từng huân chương cho từng năm.
- **CH05:** Đối chiếu lại phạm vi và cách hiểu hiệp ước năm 1907; không suy rằng toàn bộ chính quyền cùng quan điểm về thuốc phiện.
- **CH06:** Hai trang bách khoa lệch về người và thời điểm gắn với Tam Hâm; quan hệ quản sòng bạc và thuốc phiện phải giữ đúng từng nguồn.
- **CH07:** Nguyên nhân xung đột có hai bản; người bắt khác cách ghi giữa các trang; khoản hơn một triệu chỉ có hồi ức được dẫn lại, chưa có nguồn thứ hai; Wakeman chưa mở được.
- **CH08:** Năm rời cảnh sát là 1924 hoặc 1925 tùy nguồn; sách năm 1930 kể thêm việc xin nghỉ và được mời lại, chưa đủ đối chiếu để hợp nhất các bản.
- **CH09:** Ước tính thương vong và mất tích khác nhau; chưa biết từng việc Hoàng làm đêm 11 tháng 4; cần đối chiếu bản dịch các mục sách năm 1930 với nguyên văn.
- **CH10:** Con số thương vong vụ bom khác nhau giữa các bài; lời Sternberg được Wikipedia dẫn lại, cần đối chiếu bản gốc nếu có.
- **CH11:** Chi tiết giả lú lẫn bị trang bách khoa gắn nhãn thiếu nguồn; tháng Đỗ rời Thượng Hải khác nhau; chưa biết lý do Hoàng ở lại.
- **CH12:** Chưa mở được ảnh gốc quét đường; không đồng nhất ảnh kể lại với việc quét tầng một; tuổi lúc mất khác nhau trong nguồn.
- **CH13:** Nghi vấn về mộ Đỗ là lời kể do Wikipedia dẫn; tình trạng Đại Thế Giới hiện tại chưa được kiểm.

## Đường dẫn

- Bản ghép: `data/long/cl-hoang-kim-vinh/script.v2.md`.
- Review: `data/long/cl-hoang-kim-vinh/story_review/ch00.md` đến `ch13.md`.
- Clip sheet và thumbnail: không tạo trong ticket review; không có đường dẫn mới để báo.
