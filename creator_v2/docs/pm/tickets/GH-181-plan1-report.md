# GH-181 — báo cáo plan 1

**Việc đã làm:** viết `data/long/ck-g1-tra-no-truoc-han/plan.md` (UTF-8) cho Long CK 9–12 phút, trong khung 8–13 phút của brief. Plan có câu mở bằng bảng NHNN tháng 9/2026 (bài đăng 22/10/2026), phiếu tính trên gốc ví dụ 100 triệu, ba vòng mở, tám chương, hai biểu đồ, quyết định bốn ô người xem tự điền, ba tiêu đề ≤ 60 ký tự, hai chữ thumbnail, ba Short loại L, và câu miễn trừ CK.

**Không làm:** không viết script, không sinh cảnh, không đăng YouTube, không commit, không đẩy git, không sửa `state.sqlite`, không đổi lịch. Không đụng `data/long/ck-g1-thuong-tet-2027/`.

**Plan mẫu brief nêu không có file:** `data/long/ck-b1-mua-hay-thue/plan.md` không tồn tại. Khuôn lấy từ `data/long/ck-xang-dien-thue-11-2026/plan.md` và `motion/long/RETENTION.md`. Hình thức lộ trình của plan này là "Chặng đường", không dùng "Nghịch lý" của bài mua/thuê và không dùng cụm "trả lời ba câu hỏi".

**Kiểm tra đã chạy:** đếm ký tự tiêu đề bằng `len` của Python (51, 53, 48) và kiểm lại phép nhân trên 100.000.000 đồng bằng số nguyên. Chưa lint, chưa render, chưa đọc lời thoại vì brief dừng ở plan.

## URL đã mở và có chữ

1. Trang NHNN, bài "Diễn biến lãi suất của tổ chức tín dụng đối với khách hàng tháng 9/2026", ngày trên trang **22/10/2026**. Trang không dán bảng số (nút ẩn/hiện file). `https://sbv.gov.vn/vi/w/diễn-biến-lãi-suất-của-tổ-chức-tín-dụng-đối-với-khách-hàng-tháng-9/2026`
2. PDF của bài đó, đã đọc hết phần chữ. Trang 1 là các dải lãi. Trang 2 trắng. Một lần tải thẳng URL dạng `/documents/20117/0/...` trả 403. Bản đọc được lấy qua đường dẫn tài liệu khác của cùng file, lưu ở phiên làm việc.
3. Thông tư 39/2016/TT-NHNN, bản gốc 30/12/2016 trên tuyetnhunglaw.vn, đọc được đến hết Điều 21 (Điều 13, 14, 16, 18 khoản 2, 21). Phần sau bị cắt ở Điều 23. Đây không phải văn bản hợp nhất 06/VBHN-NHNN. `https://tuyetnhunglaw.vn/thong-tu-so-39-2016-tt-nhnn-ngay-30-12-2016/`
4. Luật 32/2024/QH15, chương V trên lawplayer.com, có Điều 100, 102 khoản 6, 103. Trang ghi nguồn vbpl.vn, đồng bộ 04/07/2026, tình trạng "hết hiệu lực một phần". `https://lawplayer.com/vn/act/vn-vbpl-166170/section/chapter-5`
5. Cùng luật, trang Điều 103 trên hethongphapluat.com (hiệu lực ghi 01/07/2024, ban hành 18/01/2024). `https://hethongphapluat.com/law-no-32-2024-qh15-dated-january-18-2024-on-credit-institutions/dieu-103`
6. Trang toàn văn Văn bản hợp nhất 112/VBHN-VPQH trên chinhphu.vn. Điều 4 khoản 6 miễn thuế thu nhập từ lãi tiền gửi tại tổ chức tín dụng. Trang ghi hiệu lực 1/7/2026. File PDF đính kèm trên trang chưa mở. `https://xaydungchinhsach.chinhphu.vn/luat-thue-thu-nhap-ca-nhan-119260623093630882.htm`
7. CafeBiz 22/08/2026, toàn văn bài đã mở. Câu 12–14%/năm và thả nổi có nơi 15–16%/năm được bài gán cho Báo cáo nhà ở và thị trường bất động sản quý II/2026 của Bộ Xây dựng. Bài còn đoạn và tiêu đề liên quan nêu tên tổ chức. Plan cấm đưa các tên đó lên hình. Không dùng mức cho vay tháng 7/2026 (8,3–10,5%) nằm trong cùng bài, vì PDF tháng 7 chưa mở. `https://cafebiz.vn/bo-xay-dung-co-ngan-hang-cho-vay-lai-suat-tha-noi-16-176260822142557507.chn`

## URL thấy chữ trong chỉ mục tìm, hoặc tải thẳng bị lỗi

- Bộ Xây dựng, `https://moc.gov.vn/vn/Pages/chitiettin.aspx?ChuyenmucID=1206&IDNews=96449`. Tải thẳng bị lỗi gửi yêu cầu. Chỉ mục tìm của đúng URL trả về ngày **thứ Sáu 21/08/2026** và câu 12–14% / 15–16%. File PDF gốc của Bộ chưa mở. Plan gắn nhãn tương ứng, không gọi đây là số NHNN.
- Công báo, Thông tư 29/2026/TT-NHNN: `https://congbao.chinhphu.vn/van-ban/thong-tu-so-29-2026-tt-nhnn-469916.htm`. Chỉ thấy thuộc tính (ban hành 30/06/2026, hiệu lực 15/08/2026), không thấy điều khoản.
- Các đoạn tìm về Thông tư 29 (CafeBiz 04/07/2026, hethongphapluat, bản tiếng Anh luatvietnam) nói Điều 4 sửa khoản 4 Điều 18 về thứ tự thu nợ quá hạn. Chưa mở toàn văn thông tư. Plan không trích như điều đã đọc hết và không nói thông tư này đặt trần phí trả trước.
- vbpl.vn trang Luật 32/2024 (phiên trước) gần như trống vì trang động. Lần này không mở lại viewer. Trích điều luật lấy từ hai trang ở mục trên, chưa đối chiếu PDF Quốc hội.

## URL lỗi, không dùng làm nguồn

- `https://thoibaonganhang.vn/ngan-hang-thong-bao-toi-phai-dong-them-phi-phat-tra-no-truoc-han-co-dung-khong-166438.html` — DNS không phân giải. Không trích bài hỏi đáp này.
- Lao Động: lần tải không trả về thân bài. Không trích.
- Công văn 1576/NHNN-CSTT không mở. Quy tắc "nhiều mức thì lấy mức thấp nhất" lấy từ Điều 13 khoản 5 của Thông tư 39 đã đọc, không lấy từ công văn.

## Số còn chưa có nguồn — không được nói như sự thật

- 11,2% thả nổi, 6,5% ưu đãi, phí 1,5%, gốc 200 triệu, lãi gửi 5,2%, "hơn 9 triệu/năm", và lịch phí 1,5–2% / 1% / 0,5% / miễn từ năm thứ 6 trong báo cáo đề tài.
- Một mức lãi gửi đúng kỳ hạn 12 tháng cho tháng 11/2026. Bản tin tháng 9/2026 chỉ có dải 6–12 tháng: 6,6–8,1%.
- Chuỗi NHNN cho riêng lãi vay mua nhà sau ưu đãi. Dải 8,4–10,9% là bình quân mọi khoản vay.
- Mức phí trả nợ trước hạn toàn quốc, hoặc bậc phí theo năm. Các điều đã mở chỉ có thỏa thuận.
- Số hiệu văn bản của chỉ đạo cuối tháng 10/2026 về giảm lãi huy động từ 0,5 điểm và giảm lãi cho vay 1,5–2 điểm. Không đưa vào plan.
- File gốc báo cáo nhà ở quý II/2026 của Bộ Xây dựng. Câu 12–14% / 15–16% đang dựa trên chỉ mục trang Bộ và bài CafeBiz đã mở.
- Toàn văn Thông tư 29/2026/TT-NHNN và văn bản hợp nhất Thông tư 39.
- PDF Văn bản hợp nhất 112/VBHN-VPQH. Trang HTML đã có Điều 4 khoản 6.
- Lãi vay mua nhà có được trừ khi tính thuế thu nhập cá nhân hay không. Plan không khẳng định.
- Một chuẩn tháng của quỹ sinh hoạt (ví dụ 3–6 tháng). Plan để người xem tự điền. Bài `ck-e2-quy-khan-cap` không được lấy số sang.

## Số đã dùng, và cách tính

Từ PDF tháng 9/2026: gửi 6–12 tháng 6,6–8,1%/năm; cho vay bình quân 8,4–10,9%/năm; trần ngắn hạn ưu tiên 4%/năm ghi trong bản tin.

Trên 100.000.000 đồng, 12 tháng, lãi đơn, gốc không giảm (ví dụ, và cách này làm lãi tránh được lớn hơn khoản vay trả dần):

- 8,4% và 8,1% → 8.400.000 và 8.100.000 → chênh 300.000 → phí hòa 0,3% gốc.
- 10,9% và 6,6% → 10.900.000 và 6.600.000 → chênh 4.300.000 → phí hòa 4,3% gốc.
- 13% và 8,1% (mốc trong câu Bộ, không phải NHNN) → chênh 4.900.000 → phí hòa 4,9% gốc.
- 16% và 6,6% → chênh 9.400.000 → phí hòa 9,4% gốc. Không vẽ thành đường thứ tư.

Độ nhạy 36 tháng nếu hai lãi đứng yên: 300.000 × 3 = 900.000 (phí hòa 0,9% gốc); 4.300.000 × 3 = 12.900.000 (phí hòa 12,9% gốc). Plan ghi đây là giả định, không phải dự báo.

Plan đang chờ chủ kênh duyệt trước khi viết script.
