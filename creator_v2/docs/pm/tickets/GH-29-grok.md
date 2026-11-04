# GH-29 · Grok: kiểm trùng, đối thủ, nguồn cho 30 chủ đề Short MIM

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/29. Đầu vào: `docs/pm/2026-11-02-mim-30-chu-de.md`.

## Được ghi
- Báo cáo `docs/pm/tickets/GH-29-report.md`

**Không:** sửa file khác, upload, đổi lịch, đọc credentials, commit.

## Việc
1. **Kiểm trùng với kho MIM.** Với từng chủ đề trong 30, grep:
   - `data/stier/specs/mim-*.json`: trường `title`, `lines`, `sources`;
   - `data/long/mim-*/`: `script.md`, `spec.json`;
   - `state.sqlite`: bảng `item`, `slug` có tiền tố `mim-`.

   Đánh dấu TRÙNG / GẦN / MỚI, kèm slug làm bằng chứng. Ví dụ đã biết: luật sư ChatGPT có rồi; deepfake Long Biên có Long `mim-deepfake-lua-dao-2025`.
2. **Đối thủ YouTube và tín hiệu tìm kiếm.** Tìm trên web và YouTube video tiếng Việt cùng chủ đề trong 12 tháng gần đây: kênh, lượt xem, ngày đăng (tối đa 3 video mỗi chủ đề). Có Google Trends VN hoặc tín hiệu X/tin tức thì ghi kèm. Không có số thì ghi "không đo được", không ước lượng.
3. **Nguồn gốc.** Cho 12 chủ đề không TRÙNG có tiềm năng nhất (gồm các chủ đề shortlist 01, 02, 06, 11, 13, 15 nếu không trùng), ghi:
   - 1–2 nguồn chính mở được (URL);
   - các dữ kiện then chốt: ngày, số, tên người;
   - câu nào trong hook nháp chưa kiểm được hoặc sai.

   Riêng mục 01/08: kiểm xem "Reuters tháng 10/2026" có thật không.
4. **Hook theo mẫu thắng tuần 44.** Mẫu thắng (`docs/pm/2026-11-02-thang-thua-tuan-44.md`): người có tên, hoặc con số cụ thể, tạo mâu thuẫn ngay câu đầu. Viết lại hook ≤ 9 từ cho 12 chủ đề ở mục 3, chỉ dùng dữ kiện vừa kiểm.
5. **Đề xuất 6 pilot.** Xếp hạng theo: không trùng, nguồn chắc, có tên người hoặc số, tín hiệu đối thủ hay tìm kiếm.

## Báo cáo `docs/pm/tickets/GH-29-report.md`
Bảng 30 dòng (trùng, đối thủ, tín hiệu); bảng 12 chủ đề có nguồn và hook mới; 6 pilot đề xuất kèm lý do. Ghi rõ dòng nào là số đo, dòng nào là suy đoán.
