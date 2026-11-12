# GH-307 — Báo cáo cảnh phần B

**Trạng thái: CHƯA ĐẠT CỔNG TỔNG.** Đã viết cảnh CH07–CH13 và sinh JSON, nhưng `long_gate` vẫn TRƯỢT vì chưa có TTS và metadata xuất bản. Ticket cấm TTS và giao metadata cho Lead ở bước 8; không tạo timing giả hoặc tự điền lịch. Cũng chưa chứng minh qua sàn `floor.py`: bản hiện có không có clip b-roll, trong khi sàn CL yêu cầu ít nhất 30 cảnh b-roll. Không thể tuyên bố hoàn tất video.

## Sản phẩm

- `data/long/cl-luu-gu/gen_scenes2.py`: cảnh biên tập CH07–CH13; thêm khóa ảnh cần dùng vào `gen_scenes.py`, không sửa định nghĩa cảnh CH00–CH06. Lệnh sinh ghi lại các JSON và spec theo cơ chế sẵn có.
- Số cảnh: CH07 **44**, CH08 **39**, CH09 **32**, CH10 **40**, CH11 **28**, CH12 **33**, CH13 **41**; cộng **257**. Không dùng cảnh `auto` trong phần B.
- Toàn bài: **479 cảnh**, **14 loại cảnh**, `long_gate` đếm **44 ảnh khác nhau**, **10 URL nguồn**, **5.814 âm tiết**. Số 14 là đếm loại trong JSON, chưa phải kết luận sàn floor đạt.
- Ảnh dùng trong phần B, chỉ số tổng trong `research.json`:
  - CH07: #29, #31, #63, #111, #130, #131, #154, #160.
  - CH08: #30, #41, #53, #66, #71, #106, #108, #154.
  - CH09: #126, #150, #154, #162.
  - CH10: #1, #29, #31, #110, #127, #131, #166.
  - CH11: #112, #119, #120.
  - CH12: #0, #106, #111, #113, #119, #120, #126, #127, #128.
  - CH13: #30, #111, #114, #125, #126, #127, #151.

Đã xem năm bảng `output/long/cl-luu-gu/sheet_0.jpg`–`sheet_4.jpg`; không dùng #121–124, #129 (ảnh lạc đề). Không dùng ảnh AI, ảnh phim hay clip phim. Ảnh thư pháp Lưu Dung dùng làm tư liệu hoặc minh họa giấy chữ, không gán là văn bản vụ án cụ thể. Các ảnh quan khác không được gán là Lưu Dung. Cảnh CH07 quy việc xin niêm kho cho Tiền Phong; CH10 thể hiện nhóm được giao kê biên, không dựng thẩm vấn; CH11 tách nhãn SỬ, GIAI THOẠI, PHIM.

## Các lệnh kiểm

1. `python data/long/cl-luu-gu/gen_scenes.py`: thoát 0; sinh 14 chương với số cảnh phần B như trên.
2. `python motion/long/cadence.py cl-luu-gu`: thoát 0. Bảng sau là số thay đổi / giây trung bình mỗi thay đổi / khoảng tối đa, **ước tính 150 giây/chương**, không phải thời gian thật:

   | Chương | Thay đổi | Giây/thay đổi | Tối đa |
   |---|---:|---:|---:|
   | CH07 | 67 | 2,24 | 7,07 |
   | CH08 | 56 | 2,68 | 5,94 |
   | CH09 | 50 | 3,00 | 7,02 |
   | CH10 | 56 | 2,68 | 6,51 |
   | CH11 | 39 | 3,85 | 7,77 |
   | CH12 | 48 | 3,12 | 7,71 |
   | CH13 | 59 | 2,54 | 7,14 |

   CH00 của phần A vẫn cảnh báo tối đa 14,31 giây theo giả định. Một số chương phần B đổi hình nhanh hơn mục tiêu 3–5 giây theo cách đo này; cần rà lại theo timing TTS thật. Chưa thể chứng minh nhịp thực hoặc cảnh nào dài dưới 2,5 giây khi chưa có timing.
3. `python motion/long/scene_params.py cl-luu-gu`: thoát 0, **0 lỗi, 0 cảnh báo**.
4. `PYTHONIOENCODING=utf-8 python motion/variety.py audit cl-luu-gu`: thoát 0, **OK**, theme noir và look jade. Danh sách `bgm: []` vì nhạc khai theo mood, chưa chọn file thực; cần kiểm lại nhạc sau bước chọn nhạc.
5. `python scripts/long_gate.py cl-luu-gu --min-syl 1900`: **TRƯỢT, 2 lỗi**, mã thoát 1: chưa TTS CH00–CH13; thiếu `spec.youtube.publish_at`, `playlist`, `video_credits`. Không còn báo lặp ảnh quá giới hạn. Yêu cầu in ĐẠT chưa được đáp ứng.
6. `python motion/long/studio_lint.py cl-luu-gu --strict`: 0 lỗi, 7 cảnh báo: tỉ lệ câu ngắn tại CH00, CH01, CH05, CH06, CH09, CH12 và ba ảnh liên tiếp ở CH03. Kịch bản và các cảnh phần A ngoài phạm vi sửa.
7. Kiểm UTF-8 các tệp cảnh, spec và báo cáo: không có chuỗi ba dấu hỏi hoặc ký tự thay thế; toàn video không có cảnh `auto`, không có trường video/clip trong cảnh.
8. `python motion/long/floor.py cl-luu-gu`: thoát 0, không in kết quả; không coi đây là chứng nhận đạt. Không có b-roll trong các cảnh hiện tại; cần Lead bổ sung tư liệu và kiểm sàn theo quy trình trước render.

## Giới hạn và điểm khó minh họa

- Không có tư liệu xác nhận cảnh trong kho hay việc thẩm vấn. Dùng bản đồ, thẻ và chữ theo điều sử chép; không tạo lại hành động hoặc khẳng định Lưu Dung làm điều sử không ghi. Các tranh kiến trúc, triều đình và văn bản được gắn nhãn minh họa.
- Nguồn về biệt danh là giai thoại; không xác quyết vóc dáng thật. Ngày và nơi mất dùng nguồn thứ cấp; việc kê biên theo bản ghi khuyết danh. Lượt dựng kế thừa các URL đã được ghi trong `factcheck.md`, không mở lại độc lập toàn bộ nguồn; các điểm chưa kiểm được vẫn giữ nguyên như factcheck.
- Chưa dựng khung, kiểm chữ/nhãn, hình ảnh, chuyển động hay nhạc thực tế. Ticket không giao thumbnail hoặc clip sheet và cấm TTS/render; chưa tạo tờ clip hoặc thumbnail mới trong lượt này. Các bảng ảnh đã xem nằm ở `output/long/cl-luu-gu/sheet_0.jpg` đến `sheet_4.jpg`.
- Lead cần bổ sung hoặc xử lý sàn b-roll theo đúng nguồn và phạm vi cho phép; tạo TTS, hoàn tất metadata thật, chạy lại cadence, floor và `long_gate --min-syl 1900`, rồi QA trực quan ở bước được giao.
