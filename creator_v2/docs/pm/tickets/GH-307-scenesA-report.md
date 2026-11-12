# GH-307 — Báo cáo cảnh phần A

**Trạng thái: CHƯA ĐẠT CỔNG TỔNG.** Đã viết cảnh CH00–CH06, khung bộ sinh và spec; chưa thể coi ticket hoàn tất vì `long_gate` còn 19 lỗi và nhịp thực chưa được kiểm. Không chạy TTS hay render theo ticket. Không tạo timing giả, không sửa kịch bản hoặc factcheck.

## Sản phẩm

- `data/long/cl-luu-gu/gen_scenes.py`, `spec.json`, `ch00.json`–`ch06.json`; bộ sinh có chỗ nạp `gen_scenes2.py` khi phần B được bổ sung. Giữ lời đọc đã có, không tạo cảnh `auto` trong phần A.
- Số cảnh: CH00 **14**, CH01 **33**, CH02 **38**, CH03 **34**, CH04 **38**, CH05 **33**, CH06 **33**; cộng **223**.
- Ảnh dùng theo chỉ số tổng trong `research.json` (đã xem `sheet_0.jpg`–`sheet_4.jpg`):
  - CH00: #4 Càn Long, #30 sách, #109 thư pháp, #0 Lưu Dung.
  - CH01: #31 sách, #130 chân dung Lưu Dung.
  - CH02: #162, #10, #25, #153 tranh bối cảnh; #3 Càn Long; #131 Lưu Dung.
  - CH03: #47, #36, #51 tranh thi cử; #0 Lưu Dung; #35 ô thi; #63 bài thi.
  - CH04: #130 Lưu Dung; #108 thư pháp; #155 phong cảnh.
  - CH05: #135 tranh quan văn minh họa; #110, #112, #113, #114 thư pháp.
  - CH06: #158 triều phục; #125, #128 thư pháp; #52 tranh quan văn; #29 Hòa Thân.
- Ảnh quan văn khác người được ghi nhãn minh họa, không gán là Lưu Dung. Không dùng ảnh #121–124 và #129 là những ảnh lạc đề được ticket nêu. Không dùng ảnh AI, clip phim hay ảnh diễn viên. Các ảnh được dùng có nhãn Public domain hoặc CC0 trong `research.json`.

## Kiểm tra

1. `python data/long/cl-luu-gu/gen_scenes.py`: thoát 0, sinh đủ bảy chương trên. Lần thử đầu thiếu `spec.json`; đã bổ sung khởi tạo spec và chạy lại thành công.
2. `python motion/long/cadence.py cl-luu-gu`: thoát 0, **cảnh báo CH00**. Mỗi ô dưới đây là số lần thay đổi / giây trung bình mỗi lần / khoảng tối đa (giây), bao gồm cả thay đổi bên trong cảnh:

   | Chương | Kết quả ước tính |
   |---|---|
   | CH00 | 21 / 7,14 / 14,31 |
   | CH01 | 52 / 2,88 / 7,14 |
   | CH02 | 58 / 2,59 / 6,47 |
   | CH03 | 52 / 2,88 / 6,68 |
   | CH04 | 65 / 2,31 / 5,66 |
   | CH05 | 50 / 3,00 / 7,76 |
   | CH06 | 51 / 2,94 / 6,83 |

   Không có timing TTS, công cụ giả định **150 giây cho từng chương**, kể cả CH00 mà script dự kiến khoảng 45 giây. Vì vậy các số trên không chứng minh nhịp thật 3–5 giây hoặc giới hạn 8 giây. Không chia thêm liên tiếp từng từ ở cold open chỉ để làm đẹp ước lượng; cần chạy lại và biên tập theo timing thật. Các chương còn lại hiện có lời nhưng chưa có cảnh.
3. `python motion/long/scene_params.py cl-luu-gu`: thoát 0, 0 lỗi, 0 cảnh báo; không chứng minh khung hình đã hiển thị đúng.
4. `PYTHONIOENCODING=utf-8 python motion/variety.py audit cl-luu-gu`: thoát 0, in `OK`, theme noir, look jade. Đầu ra `bgm: []`: nhạc đang khai theo mood và chưa được chọn thành file, nên chưa thể kết luận các bản nhạc thực tế khác ba video gần nhất; kiểm lại sau khi chọn nhạc.
5. `python scripts/long_gate.py cl-luu-gu --min-syl 1900`: **TRƯỢT 19 lỗi**, thoát 1; 5.813 âm tiết, 223 cảnh, 29 ảnh, 10 URL nguồn. CH07–CH13 mỗi chương thiếu HUD và cảnh đủ loại (14 lỗi); toàn bộ thiếu TTS; cổng báo cụm `trong kho`, năm `1796`, thiếu `publish_at`, `playlist`, `video_credits` và bảng `say` cho 26 tên/thuật ngữ. `trong kho` là một phần câu kể CH07 về bạc; `1796` xuất hiện trong phần ghi chú kịch bản dù dòng sự kiện tương ứng đã được bỏ. Cần Lead rà các cảnh báo này và bảng say, bổ sung metadata sau khi có quyết định thực tế, dựng phần B và chạy TTS ở bước được giao. Không tự đặt lịch xuất bản.
6. `python motion/long/studio_lint.py cl-luu-gu --strict`: 0 lỗi, 7 cảnh báo: sáu cảnh báo tỉ lệ câu ngắn ở CH00, CH01, CH05, CH06, CH09, CH12 và một cảnh báo ba ảnh liên tiếp ở CH03. Không sửa lời đã duyệt ngoài phạm vi ticket.
7. `python motion/long/floor.py cl-luu-gu`: thoát 0 nhưng không in kết quả; không có căn cứ kết luận đạt floor.
8. Kiểm chuỗi ba dấu hỏi, ký tự thay thế và neo dạng `[câu, từ]` bằng Python: không phát hiện chuỗi lỗi hay từ neo vắng trong câu. Chưa kiểm thời điểm hiển thị và bố cục trên video.

## Giới hạn nội dung và việc cần tiếp tục

- Lời trích vụ án văn tự chia thành hai đoạn liên tiếp, giữ nhãn TRÍCH DỊCH và quy thuộc Đông Hoa lục qua bản trích; cần soi bố cục và đồng bộ lời đọc. Tư liệu về việc kê biên 1799 là ghi chép khuyết danh, không gán quyền quyết định riêng cho Lưu Dung.
- CH02 không có ảnh xác nhận của Lưu Thống Huân hay cảnh chiếc kiệu; dùng tranh bối cảnh có nhãn minh họa và đồ họa. CH04 không có tài liệu hình về việc đày quân đài; dùng chữ và tranh minh họa, không dựng thêm diễn biến. CH05 thư pháp dùng như mô-típ minh họa, không nhận là bài thơ trong vụ án. CH06 không có ảnh riêng cho từng chức vụ; dùng thẻ chức và bản đồ.
- Kế thừa nguồn đã mở theo `factcheck.md`; lượt này không mở lại độc lập từng URL. Thanh thực lục gốc và bản gốc Đông Hoa lục chưa được mở theo chính factcheck; giữ cách quy thuộc nguồn thứ cấp/bản trích. Các điểm chưa kiểm chứng khác được giữ nguyên trong factcheck, không thêm khẳng định mới để lấp chỗ trống.
- Chưa có clip sheet hoặc thumbnail mới trong ticket này; không có đường dẫn đã kiểm. Chưa soi khung render, ảnh tải thực tế, chữ, bản đồ, nhạc và nhịp TTS; cần kiểm ở bước sau.
