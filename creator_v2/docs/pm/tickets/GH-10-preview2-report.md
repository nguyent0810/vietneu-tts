# GH-10 · Preview lần 2: Claude QA (fallback)

agy hết quota ("Individual quota reached, resets in 33h"). Grok cũng hết hạn mức (402, "usage balance exhausted"). Vì vậy Claude soát thay, dựa trên:
- bản draft agy đã render xong lúc 14:07–14:26;
- các sheet `qa/preview_chNN.jpg` agy dựng lúc 14:27–14:28;
- khung hình Claude trích thêm từ `ch03/draft.mp4` và `ch04/draft.mp4`.

## Lỗi cũ: đã hết

- Không còn ảnh `nextcube`, không còn chữ "minitel".
- Tiêu đề của cảnh `print` đã hiện đủ: `ch03#6` "JOHN SCULLEY · 25.07.1985", `ch04#4` "NEXT COMPUTER".
- Nhãn TRÍCH DỊCH đã hiện ở `ch03#8`.

## Lỗi mới

| scene ID | mốc | severity | mô tả | bằng chứng | sửa |
|---|---|---|---|---|---|
| `ch03#6`, `ch07#6` | ch03 20–28 s, ch07 19–22 s | **chặn** | Khung `print` của `sculley06` co lại chỉ còn **một ô trắng khoảng 15 px**, ảnh không hiện. Nguyên nhân: `maxH: 0.52`, `maxW: 0.56` được hiểu là **pixel** (engine `B.print`: `k = min((s.maxW\|\|760)/m.w, (s.maxH\|\|700)/m.h)`). Ngoài ra `pos` phải là chuỗi CSS (`"50% 14%"`), không phải mảng. | khung ch03 @24 s | Bỏ `maxH`/`maxW`/`pos`, hoặc đặt theo pixel (ví dụ `maxH: 700`). Thẻ tên ghi chính tên Sculley không phải logo hay thương hiệu, nên chấp nhận được; không cần crop. |
| `ch03#?` (cảnh `org` "BƯỚC 1 · BỊ TƯỚC QUYỀN") | ch03 ≈ 29–32 s | nên sửa | Khoảng 3 giây chỉ có một nút nhỏ ở mép trên, phần còn lại của khung trống. | `preview_ch03.jpg` @30 s | Neo nút thứ hai sớm hơn, hoặc đổi sang loại cảnh khác. |
| `ch04#?` (`org` "TRUNG TÂM CỦA NEXT") | ch04 ≈ 36 s | nên sửa | Tương tự: lúc đầu cảnh chỉ có một nút. | `preview_ch04.jpg` @36 s | Neo các nút con cùng mốc với cảnh. |
| `ch04#4` | ch04 12–15 s | nhỏ | `nextcube2` hiện mặt lưới tản nhiệt của máy, nhìn không ra là máy tính. | khung ch04 @15 s | Nếu được, đổi sang `nextstation` hoặc một ảnh AI. |

**Kết luận:** cần sửa tiếp. Lỗi "chặn" là ảnh Sculley không hiện ở 2 cảnh.
