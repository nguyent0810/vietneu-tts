# GH-10 · Render bản preview và soát lại `mim-jobs-1985` (agy)

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/10

Codex đã sửa các cảnh trong báo cáo QA của bạn: `docs/pm/tickets/GH-10-qa-report.md` → `GH-10-fix-report.md`. Claude đã chạy lại các cổng:
- `long_gate`: ĐẠT;
- `floor` theo kênh: `[]`;
- chỉ chữ: 18,31%, chuỗi dài nhất 9,4 giây;
- `scene_rules`: 0 cảnh báo;
- mỗi ảnh tối đa 3 lần.

## Được ghi

- `output/long/mim-jobs-1985/**`
- báo cáo `docs/pm/tickets/GH-10-preview-report.md`

Không sửa `data/long/**`, engine hay code. **Không chạy `final`.** Không đăng, không commit.

## Việc

1. **Render bản preview:** `python motion/long/build_long.py mim-jobs-1985 render --draft`, đủ 9 chương.
2. **Trích khung:**
   - Trích từ từng file draft của chương, mỗi 3 giây một khung.
   - Ghép thành `output/long/mim-jobs-1985/qa/preview_chNN.jpg`, mỗi chương một sheet, lưới 6 cột, ghi mốc giây dưới mỗi khung.
   - Ghép thêm `qa/preview_all.jpg`, mỗi 6 giây một khung.
3. **Soát lại**, theo đúng các trục của lần QA trước:
   - kiểm lại từng scene ID đã ghi trong `GH-10-fix-report.md`, xác nhận lỗi đã hết;
   - tìm lỗi mới phát sinh do lần sửa.

   Đặc biệt kiểm:
   - chữ tràn hoặc bị cắt;
   - ledger đè lên phụ đề;
   - mặt Sculley bị phụ đề đè;
   - ảnh `nextcube` không còn lộ chữ "minitel";
   - "AMELIO" hiện đủ;
   - nhãn TRÍCH DỊCH;
   - không còn cảnh có chữ nào hiện dưới 2,5 giây;
   - màn trống hoặc đen quá 1 giây;
   - tiếng và hình khớp nhau.

## Báo cáo

Ghi `GH-10-preview-report.md`, gồm:

- bảng xác nhận các lỗi cũ: scene ID, đã hết hay còn, bằng chứng;
- bảng lỗi mới: scene ID, mốc giây, severity, bằng chứng, đề xuất sửa;
- kết luận: **"sẵn sàng final"** hoặc **"cần sửa tiếp"**.
