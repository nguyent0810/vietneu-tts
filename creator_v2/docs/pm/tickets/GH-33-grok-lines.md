# GH-33 · Grok: viết lại lời đọc 12 Short pilot cho vừa 100–125 từ

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/33.

## Vì sao làm lại
Dàn ý cũ dài 189–237 từ (≈ 60 s), trong khi `build.py` chỉ nhận 55–135 từ. Codex đã rút bằng cách **cắt câu giữa chừng** ("nhóm tin tặc đã âm.", "xác nhận thủ phạm là."), nên Lead loại bản đó. Cần viết lại cho tai nghe, câu trọn nghĩa.

## Đầu vào
- packaging và dàn ý: `docs/pm/tickets/GH-33-{MIM,CK}-pack.md`
- facts đã kiểm: `docs/pm/tickets/GH-33-{MIM,CK}-facts.json`
- title mới theo từ khóa: `docs/pm/tickets/GH-33-titles.json`
- luật Short: `docs/pm/2026-10-12-shorts-analysis.md` §7

## Được ghi
- `docs/pm/tickets/GH-33-lines.json`
- báo cáo `docs/pm/tickets/GH-33-lines-report.md`

**Không:** sửa spec hay code, render, commit.

## Việc
Mỗi slug (12 slug trong facts):
1. **`lines`: 7–9 câu, tổng 100–125 từ** (tính theo khoảng trắng).
   - `lines[0]` giữ **đúng nguyên văn** hook đã chốt trong pack.
   - Mỗi câu trọn nghĩa, đọc một hơi (≤ 18 từ), nói với "bạn".
   - Một insight, kết bằng cú chốt.
   - Không CTA, không câu hỏi trong lời đọc, không dấu hai chấm.
   - Số đọc bằng chữ nếu dễ đọc sai, hoặc ghi số và thêm vào `say`.
   - Mọi số, tên, ngày lấy từ facts; mục CHƯA KIỂM không được dùng.
   - CK: số ví dụ nói rõ "ví dụ".
2. **`say`:** cách đọc cho mọi tên riêng nước ngoài, viết tắt, ký hiệu, số có thể đọc sai. Ví dụ: `Binance` → "Bai-nen-xơ", `=FBI` → "ép bi ai", `=TPU` → "tê pê u", `=OTP` → "ô tê pê", `kWh` → "ki lô oát giờ", `E5` → "e năm", `RON` → "rôn".
3. **`frame0`:** chữ khung đầu đã chốt trong pack, giữ nguyên.
4. **`title`:** lấy `title_recommended` trong `GH-33-titles.json`. Nếu lời đọc mới không còn chứa dữ kiện của title thì báo.
5. **`beats`:** gợi ý hình cho từng câu, chọn một trong các loại:
   - `M`: clip hoặc ảnh tự do, mô tả cảnh cụ thể kèm từ khóa Pexels;
   - `D`: số liệu (counter/chart/ledger/table);
   - `G`: sơ đồ (board/cards3d/map/timeline);
   - `T`: chữ.

   Mỗi bài có đủ M, D, G; không 3 câu liền cùng loại; chuỗi beats của 12 bài phải khác nhau.

## Định dạng
`[{slug, title, frame0, lines[], say{}, beats[], word_count}]`. Báo cáo: bảng số từ, kèm kiểm tự động không câu nào bị cắt cụt (câu kết thúc bằng từ trọn nghĩa).
