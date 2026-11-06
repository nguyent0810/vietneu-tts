# GH-21: cache render chương Long (báo cáo)

Codex làm, Lead viết lại báo cáo (bản gốc bị mất dấu do ghi qua PowerShell) và sửa 4 comment mất dấu trong code.

## Nguyên nhân
- Mỗi chương mang `prog0`/`prog1` (vị trí thanh tiến độ) tính theo thời lượng cộng dồn trên tổng video. Sửa lời làm một chương dài hoặc ngắn đi thì `data.js` của **mọi** chương đổi, kéo theo đổi key, kể cả chương phía trước, vì mẫu số đổi. Đây là lý do Bao Thanh Thiên phải render lại cả video ngày 06/11.
- Mọi khai báo ảnh và bản đồ dùng chung được chép vào data của từng chương, nên sửa ảnh của chương khác cũng làm đổi key.
- Key cũ không băm cả repo hay commit. Merge code chỉ đổi key khi chạm file engine mà composition thật sự nạp.

## Đã sửa (`motion/long/build_long.py`)
- Thanh tiến độ chia đều theo thứ tự chương (`prog0 = i/N`, `prog1 = (i+1)/N`). Đây là thay đổi hình, Lead đã duyệt: các chương dài xấp xỉ nhau.
- `do_html` chỉ đưa vào data những ảnh mà cảnh của chính chương đó tham chiếu.
- Key mới băm: data, HTML thật, spec chương, voice và timing của chương, CSS/JS engine mà HTML nạp, nội dung ảnh và clip được tham chiếu, chế độ draft/final, phiên bản HyperFrames/Node. Thiếu asset được tham chiếu thì báo lỗi, không lặng lẽ dùng cache.
- Định dạng key đổi, nên cache cũ mất hiệu lực **một lần**.

## Giới hạn
- `geo` (bản đồ) vẫn đưa vào mọi chương: sửa bản đồ có thể gây render thừa.
- Font Google và GSAP lấy từ CDN; key băm URL, không băm nội dung.
- Nhạc nền trộn riêng trong `mix.wav` của từng chương, final nối các bản mix (không đổi).

## Kiểm thử
- `tests/test_chapter_render_key_21.py`: sửa ch07 thì key ch03 và ch10 giữ nguyên; script không liên quan không đổi key; CSS dùng chung, ảnh, clip làm đổi key; thiếu clip thì báo lỗi.
- Toàn bộ `tests/`: 967 passed (Lead chạy).
