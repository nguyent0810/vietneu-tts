# GH-143 · Grok: dữ kiện và lời đọc cho 1 Short CK sức mua (slot 04/11 19:00)

Issue: https://github.com/nguyent0810/vietneu-tts/issues/143. Chủ kênh duyệt 04/11: sản xuất Short này, không bỏ QA.
Đề xuất gốc ở `docs/pm/2026-11-04-de-xuat-noi-dung-3-kenh.md`, mục 5, phương án 1.

**Hạn:** xong trong 40 phút. Sau bước này còn lắp spec, render, QA và duyệt.

## Ý tưởng đã chốt
- **Slug:** `ck-them-10-trieu-gio-bot-mot-mon`
- **Loại:** S (đứng riêng).
- **Insight:** số dư tăng chưa chắc là giàu hơn. Đo bằng sức mua, tức giỏ hàng, thì tiền lãi có thể không theo kịp giá.
- **Hook gốc:** "Tài khoản thêm mười triệu. Cái giỏ lại bớt một món."
  - Được viết lại cho đạt ≤ 9 từ, nhưng giữ hai hình đối nghịch: số dư tăng, giỏ hàng nhỏ đi.
- **Frame đầu:** "10 TRIỆU ↑" đối diện "GIỎ −1 MÓN", ≤ 6 từ.

## Đầu vào
- `docs/pm/2026-11-04-de-xuat-noi-dung-3-kenh.md`: mục 5 và mục 6.
- Luật CK: `AGENTS.md`, mục "Luật nội dung".
- Luật Short: `docs/pm/2026-10-12-shorts-analysis.md` §7.
- Mẫu lời đã duyệt: `data/stier/specs/ck-dien-giam-44-dong-20-nam-v2.json`, trường `lines`.

## Được ghi
- `docs/pm/tickets/GH-143-ck-short-facts.json`
- `docs/pm/tickets/GH-143-ck-short-lines.json`
- báo cáo `docs/pm/tickets/GH-143-ck-short-report.md`

**Không:**
- sửa spec, code hay lịch;
- render;
- upload;
- commit;
- đọc credentials.

## Việc

### 1. Dữ kiện thật
- Lấy CPI Việt Nam mới nhất từ Cục Thống kê (nguồn sơ cấp), cùng ít nhất một nguồn độc lập. Cả hai phải mở được.
- Ứng viên là CPI tháng 10/2026: so cùng kỳ +5,09%, bình quân 10 tháng +4,57%, theo VietNamNet 03/11. Phải tự kiểm lại.
- Ghi vào facts dạng `{claim, value, url, quote≤25 từ, checked:"04/11/2026"}`.
- Số nào không kiểm được thì ghi `"CHƯA KIỂM"` và không dùng.

### 2. Ví dụ giả định
- Ví dụ tự dựng phải nhất quán, ghi phép tính, và trên màn hình gắn "VÍ DỤ GIẢ ĐỊNH".
- Gợi ý: số dư X, lãi suất giả định r%/năm → thêm 10 triệu. Giá tăng theo CPI thật → giỏ hàng cùng giá trị cần thêm Y.
- Không nêu tên ngân hàng, không nêu lãi suất của tổ chức cụ thể, không nói "nên gửi/rút/mua/bán".
- Kết luận phải đúng toán học. Nếu lãi giả định cao hơn CPI thì sức mua **không** giảm: chọn số sao cho câu chuyện đúng, và nói rõ đó là giả định.

### 3. Lời đọc (`lines`)
- 7–9 câu, tổng 100–125 từ, đếm theo khoảng trắng.
- Câu trọn nghĩa, đọc một hơi (≤ 18 từ), nói với "bạn".
- Một insight, kết bằng cú chốt.
- Không CTA, không câu hỏi, không dấu hai chấm trong lời đọc.
- Không mở bài bằng "trả lời ba câu hỏi".

### 4. Các trường còn lại
- **`say`:** cách đọc số và ký hiệu dễ đọc sai (CPI → "xê pê i", % …).
- **`beats`:** một loại cho mỗi câu, chọn trong M (clip Pexels, kèm từ khóa), D (số liệu), G (sơ đồ), T (chữ).
  - Bài phải có đủ M, D, G.
  - Không 3 câu liền nhau cùng loại.
  - Clip M không có logo, không có chữ thương hiệu.
- **`title`:** 3 phương án, mỗi phương án ≤ 60 ký tự, có dấu, dạng "một khoản tiền × một mốc thời gian". Đúng sự thật, không phóng đại.
- **`description`:**
  - 2–3 câu, có nguồn dữ kiện bằng lời (ví dụ "theo Cục Thống kê");
  - có "VÍ DỤ GIẢ ĐỊNH" cho số tự dựng;
  - kết bằng "Nội dung giáo dục, không phải tư vấn đầu tư.";
  - không có ký tự `<` `>`, không có chữ "CẦN", "agent", "factcheck", "data/long".

## Định dạng `GH-143-ck-short-lines.json`
`{slug, short_type:"S", titles[3], frame0, lines[], say{}, beats[], word_count, description, sources[]}`

## Báo cáo
- Số từ.
- Phép tính ví dụ.
- Bảng claim → nguồn.
- Danh sách CHƯA KIỂM.

Câu trả lời cuối trên terminal: tối đa 3 dòng.
