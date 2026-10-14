# Ngữ pháp chuyển động + nhịp (tóm tắt từ research F, G, C)

## Học thuyết (faceless-explainer motion-language, áp cho mọi kênh)
1. Mượt hơn nảy: `power3/expo.out` vào, `.in` ra, `.inOut` di chuyển. Nảy (`back.out`) là ngoại lệ có ngân sách (theme `overshoot`, BUD = 0).
2. Hiện đúng lúc giọng nói tới, rải ở ~50% sau của cảnh; không đổ hết trong 25% đầu.
3. Không "thở" lười, không phóng chậm nửa sau cảnh. "Thà không chuyển động còn hơn chuyển động dở."
4. Chuyển cảnh = cắt khớp vận tốc (cut-the-curve, zoom-through), không như trình chiếu.

## Mỗi loại nội dung một cơ chế
| Nội dung | Cơ chế | Thông số |
|---|---|---|
| Câu thường | waterfall theo mốc từ, hiện nhị phân | từ nặng 60-80px/0,16-0,2s; nhẹ 30-48px/0,1-0,13s; power4.out |
| Câu luận đề / trích dẫn | karaoke (một driver tuyến tính) | attack .15, release .35, nền .3, từ khoá giữ >= 1s |
| Con số | đếm + phóng (scale .5->1), có hình đi kèm (vòng/thanh/lưới) | 1,2-2,5s power3.out, tabular-nums, đơn vị vào sau; năm KHÔNG đếm từ 0 |
| Danh sách năm/tuổi | neo cố định + ô quay / bảng tra / danh sách tích lũy | bước .3-.7s, mục cũ mờ |
| Đối lập | gạch chéo vế sai (±12°, .3s) -> vế đúng inverse zoom | |
| Ngày tháng | lịch lật trang + dấu son | |
| Câu kết | mask rise, gạch chân, tĩnh >= 1,5s, khung cuối ~ khung đầu (loop) | |

## Seam
| Seam | Dùng khi | Thông số |
|---|---|---|
| `curve` (y) / `side` (x) | ý tiếp nối, mặc định | ra -230 power4.in .3s, vào +230 power4.out .34s |
| `zoom` | đổi trạng thái (móc -> ngữ cảnh) | ra 1->1.2 blur 10px .2s, vào .75->1 expo.out .5s |
| `inv` | trả lời / payoff | ra 1->.8, vào 1.25->1 |
| `blur` | êm (BUD, lịch sử) | .4-.55s × speed |
| `hard` | đánh thức, đổi chủ đề | |
Một seam chính (60-70%) + 1-2 seam phụ / video.

## Luật đa dạng (studio.py kiểm)
- >= 3 khung khác nhau / video; không lặp khung liền kề; không lặp trục chuyển động liền kề.
- <= 1 cơ chế tròn (wheel, cycle_draw, count_ring...); <= 1 cảnh 3D/WebGL nặng; <= 2 cảnh do camera dẫn, không liền nhau.
- Ảnh là tiêu điểm <= 30% câu, không bao giờ ở câu 0.
- Đúng một nhịp tĩnh trước payoff.
- Sổ kênh: móc không lặp trong 3 video; chữ ký (móc|seam|nền|biểu tượng) không trùng 10 video. Định dạng thắng (series) được ghim móc + bố cục,
  chỉ xoay thân -- dữ liệu thắng luôn trên sự mới lạ.

## Tiếng Việt
- Chuẩn hoá NFC; tách theo từ (âm tiết), không tách theo ký tự trừ chữ số.
- Mask có đệm `.36em` trên, `.16em` dưới (đã có `.wd.mask`). Chữ hoa nhiều dòng line-height >= 1.15-1.2; tracking không chặt hơn -0.02em.
- Blur chữ <= 10px và về `none`; glitch RGB <= 6px; decode chỉ dùng bộ chữ số.
- Vùng an toàn Shorts: nội dung x 100-940, y 250-1460; phụ đề y 1500-1690; tránh cột nút bên phải (x > 940).
