# Thứ bậc nguồn hình: tư liệu thật trước, rồi ảnh AI vẽ theo phong cách kênh, stock sau cùng; được dùng ảnh AI có mặt Đức Phật

Trạng thái: đã chấp nhận (23/10/2026). Thay luật 21/10, luật này chỉ cho dùng ảnh tượng thật.

Có hai vấn đề cùng lúc:

- **Stock tìm bằng chữ tiếng Anh ra sai hàng loạt.** Ở tt04, khoảng 39/128 ảnh vi phạm luật kênh: đền Hindu, người phương Tây, đồ hiện đại, ảnh gợi cảm. Long thử ngày 23/10 phải gỡ khoảng 45 ảnh: Kinh Thánh, chữ Hebrew, khẩu hiệu "STOP WAR".
- **Thiếu hình** khiến tỉ lệ "chữ trên nền trống" vọt lên. Long thử Cao Biền có 51%, trong khi trần là 12%.

Luật cấm vẽ mặt Đức Phật có từ trước, vì model chạy trên máy vẽ méo. Ngày 23/10 chủ kênh bỏ cấm, vì các app hiện nay vẽ ổn.

Thứ tự chọn hình:

1. **Tư liệu thật**: ảnh bảo tàng CC0, Wikimedia Commons, Openverse. Mọi nguồn đều ghi đủ tác giả và giấy phép.
2. **Ảnh AI**, dùng cho cảnh truyền thuyết, cảnh tái dựng và nhân vật xuyên suốt:
   - ChatGPT: không có watermark nhìn thấy; bảng nhân vật giữ được mặt giữa các cảnh.
   - Flow/Veo cho clip động (tính tín dụng). Flow ở Việt Nam bắt buộc có watermark ✦ nhìn thấy, và không được gỡ.
3. **Stock** (Pexels) cho B-roll chung, phải soát từng ảnh.

## Các phương án đã cân nhắc

- **Chỉ dùng Commons và bảo tàng.** Không đủ hình cho cảnh truyền thuyết và cảnh tái dựng.
- **Vẽ bóng người bằng code.** Khô và lặp lại.
- **Chỉ dùng Flow.** Bị watermark ✦ nhìn thấy, không được cắt hay che.

## Hệ quả

- **Vẫn cấm:**
  - mặt méo;
  - hoạt hình, biếm hoạ, vẽ mặt Đức Phật bằng code;
  - chữ đè lên mặt; cắt ngang đầu;
  - zoom giật, kiểu meme;
  - dùng ảnh AI thay cho bằng chứng lịch sử (bia, sắc phong, trang sách);
  - gỡ watermark hoặc SynthID.
- Mô tả video ghi "Một số hình minh hoạ được tạo bằng AI". Ảnh trông như ảnh thật thì khai báo nội dung tổng hợp trên YouTube. Không in chữ "MINH HỌA" lên tranh đã cách điệu.
- **Engine cần thêm** (PR #29):
  - kiểu media `local` cho ảnh/clip đã tải về;
  - tự đặt ảnh dọc vào khung 16:9, vì chân dung dọc trong khung ngang từng bị cắt chỉ còn búi tóc;
  - `"crop"` để dùng lại một ảnh trong cùng chương, vì bridge chặn ảnh trùng byte;
  - khoá chương băm nội dung file, để thay ảnh mà giữ tên thì chương tự render lại.
- **Số đo L_bud_26 (Đề Bà Đạt Đa):**
  - 97 ảnh/clip, trong đó 24 ảnh ChatGPT, 30 khung cắt cận và 3 clip Veo;
  - chữ trên nền trống 21,5%, so với 51% ở Cao Biền;
  - ảnh và clip chiếm 68,4% thời lượng.
  
  Muốn xuống dưới 12% thì cần khoảng 110 ảnh riêng.

## Bằng chứng

`output/cl_staging/long/research/long_test/bao_cao_long_cb_2026-10-23.md`, `bao_cao_long_bud_2026-10-24.md`, `output/cl_staging/long/research/flow_playbook.md` (§6–§8: ChatGPT, Flow Pro, giữ nhân vật xuyên suốt), `output/cl_staging/grok/rules.md` luật 17, commit `3c3f00b`, `08c3d94`.
