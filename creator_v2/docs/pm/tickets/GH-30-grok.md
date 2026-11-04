# GH-30 · Grok: kiểm trùng, nguồn, đối thủ cho 30 chủ đề Short CK

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/30. Đầu vào: `docs/pm/2026-11-02-ck-30-chu-de.md`. Mẫu thắng/thua tuần 44: `docs/pm/2026-11-02-thang-thua-tuan-44.md`. Ở CK, hook thắng là cặp số tiền đối nghịch ngay câu đầu; hook khái niệm và chủ đề thị trường chung thì thua.

## Được ghi
- Báo cáo `docs/pm/tickets/GH-30-report.md`

**Không:** sửa file khác, upload, đổi lịch, đọc credentials, commit.

## Việc
1. **Kiểm trùng với kho CK.** Grep các nguồn sau:
   - `data/stier/specs/ck-*.json`: `title`, `lines`;
   - 19 Short đã có `output/stier/ck-*/final.mp4` mà chưa vào hàng chờ;
   - `data/long/ck-*/` (Long: b2 lãi kép, b3 trả góp 0%, b4 xe, d1 vàng, e3 thẻ tín dụng, e5 thuế TNCN, e6 BHXH, f2 BHYT, g1 thưởng Tết…);
   - `state.sqlite` bảng `item`.

   Mỗi chủ đề ghi một nhãn kèm slug làm bằng chứng:
   - TRÙNG-SHORT: đã có Short gần giống;
   - CÓ-LONG: có Long, nên làm Short loại L dẫn sang Long;
   - MỚI.
2. **Văn bản chính thức.** Mở nguồn gốc và trích số hiệu, ngày, nội dung chính:
   - Nghị định 398/2026/NĐ-CP: có thật không, giảm thuế cho ai, bao nhiêu phần trăm, hiệu lực từ ngày nào;
   - giảm trừ gia cảnh 2026: 15,5 triệu cho bản thân, 6,2 triệu cho mỗi người phụ thuộc;
   - chênh lệch giá mua/bán vàng (#19): nguồn giá niêm yết;
   - trả tối thiểu thẻ tín dụng (#24): quy định NHNN hoặc biểu phí ngân hàng.

   Không mở được nguồn chính thức thì ghi "chưa kiểm được".
3. **Đối thủ và tín hiệu tìm kiếm.** Tìm video YouTube tiếng Việt cùng chủ đề trong 12 tháng gần đây: kênh, lượt xem, ngày đăng (tối đa 3 video mỗi chủ đề). Ghi thêm Google Trends VN nếu có. Không có số thì ghi "không đo được", không ước lượng.
4. **Viết lại hook.** Với 12 chủ đề tốt nhất (gồm 19, 11, 24, 21, 02, 14), viết lại hook ≤ 9 từ theo mẫu cặp số đối nghịch, kèm chữ khung đầu. Số minh họa ghi VÍ DỤ GIẢ ĐỊNH. Số chính sách chỉ dùng số đã kiểm ở mục 2.
5. **Đề xuất 4 pilot và 2 dự phòng**, kèm lý do. Nếu chủ đề trùng một Short có sẵn, nói rõ nên dùng lại Short đó hay làm mới.

## Báo cáo `docs/pm/tickets/GH-30-report.md`
- bảng 30 dòng;
- bảng nguồn chính thức;
- 12 hook mới;
- đề xuất pilot.

Ghi rõ đâu là số đo, đâu là suy đoán.
