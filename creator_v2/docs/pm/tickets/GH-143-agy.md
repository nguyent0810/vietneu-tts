# GH-143: Đề xuất cải thiện nội dung MIM / CK / CL từ Analytics 04/11

Issue: https://github.com/nguyent0810/vietneu-tts/issues/143
Việc **phân tích và nghiên cứu**. Không sản xuất, không render, không đụng YouTube.

## Mục tiêu
Chủ kênh có một báo cáo Analytics ba kênh (kỳ 20/10–02/11). Hãy biến nó thành **đề xuất làm được** cho từng kênh, đối chiếu với dữ liệu và luật của repo. Đề xuất này phải xong trước khi Lead lấp các slot trống, bắt đầu từ slot **CK 04/11 19:00** (12:00Z).

## Đọc (chỉ những file này, không khám phá repo)
1. `docs/pm/2026-11-04-analytics-3-kenh.md`: báo cáo gốc, nguồn chính.
2. `AGENTS.md`: luật nội dung từng kênh (tiêu đề, CK, ảnh, mô tả).
3. Bối cảnh trước đó:
   - `docs/pm/2026-11-02-thang-thua-tuan-44.md`
   - `docs/pm/2026-11-02-studio-tuan-44.md`
   - `docs/pm/2026-10-27-chien-luoc-long-45-ngay.md`
   - `docs/pm/2026-10-28-huong-lam-mim-ck.md`
   - `docs/pm/2026-11-03-retro-ck-shorts-pilot.md`
   - `docs/pm/2026-11-03-retro-mim-shorts-pilot.md`
   - `docs/pm/2026-11-02-mim-30-chu-de.md`
   - `docs/pm/2026-11-02-ck-30-chu-de.md`
4. Lịch đã lên, **chỉ đọc**:
   ```python
   import sqlite3; c = sqlite3.connect('file:state.sqlite?mode=ro', uri=True)
   c.execute("select channel,kind,slug,publish_at,stage from item where publish_at>='2026-11-04' order by publish_at")
   ```
   - `stage='published'` nghĩa là đã upload (private, có lịch).
   - Giờ lưu ở UTC; giờ VN = UTC+7.
   - DB này chỉ có MIM và CK. CL không nằm trong đó.
5. Được tra web để kiểm đối thủ hoặc xu hướng. Mỗi khẳng định từ web phải có URL đã mở được.

## Câu hỏi phải trả lời

### Cho cả ba kênh (MIM, CK, CL)
1. **Phân loại đề xuất:** với mỗi đề xuất trong mục 4–7 của báo cáo (tiêu đề, hook, thumbnail, hướng dựng, Short), xếp vào **NHẬN / SỬA / BỎ**.
   - Lý do phải dựa trên dữ liệu, hoặc chỉ ra luật bị vi phạm. Ví dụ cần soi: tiêu đề quá 60 ký tự; CK nêu tên ngân hàng; CK thiếu "VÍ DỤ GIẢ ĐỊNH"; MIM dùng ảnh không phải PD/CC0/CC BY; chủ đề trùng video đã có.
2. **Ba việc đáng làm nhất trong 14 ngày**, xếp theo tác động/công sức. Mỗi việc ghi: một biến thay đổi, chỉ số quyết định, mốc 24h/72h/7d, ngưỡng dừng.
3. **Bao bì Long đã đăng.** Những video nào đáng đổi tiêu đề hoặc thumbnail, chỉ đổi một biến mỗi lần?
   - Chỉ chọn video có ≥1.000 impressions.
   - Đây là đề xuất chờ chủ kênh duyệt, không tự đổi.

### Riêng MIM và CK: điều chỉnh lịch
4. Soi các Short đã lên lịch từ 04/11 đến 15/11. Short nào **đi ngược** kết luận của báo cáo?
   - Ví dụ: MIM có chuỗi Watson/Kasparov dày đặc, trong khi báo cáo nói nhiều clip AlphaGo cùng tuần chỉ đạt AVP 44–57%.
   - Ghi danh sách slug, lý do, và đề xuất giữ, đổi giờ hay thay bằng gì.
5. **Slot CK 04/11 19:00 và các slot CK/MIM còn trống tuần 45–46:** đề xuất tối đa 3 phương án cho mỗi slot.
   - Ưu tiên cụm chủ đề tiền nhà, sức mua, quỹ khẩn cấp (CK) và kiểm nguồn AI, QWERTY (MIM).
   - Mỗi phương án ghi: câu mở, frame đầu, loại Short (**S** = tự đứng / **L** = dẫn sang Long có thật), và trùng hay không với video đã có (dẫn slug).

### Riêng CL
- Chỉ phân tích và đề xuất. Không đọc hay ghi file sản xuất CL.

## Ràng buộc
- **Chỉ được ghi đúng một file:** `docs/pm/2026-11-04-de-xuat-noi-dung-3-kenh.md`.
- **Cấm:**
  - git (commit, push, checkout…);
  - upload, enqueue, đổi lịch;
  - ghi `state.sqlite`;
  - đọc `YT_CREDS_DIR` hay `.youtube_channels`;
  - render;
  - sửa code.
- **Số liệu:**
  - Số dẫn từ báo cáo phải đúng như trong báo cáo, không tự tính lại giờ xem.
  - Số bạn tự tính thì ghi phép tính.
  - Giả thuyết ghi rõ là giả thuyết.
- **Không đề xuất tăng sản lượng** để bù hook yếu. Báo cáo đã kết luận ưu tiên hiệu quả mỗi video.

## Báo cáo (`docs/pm/2026-11-04-de-xuat-noi-dung-3-kenh.md`)
Viết tiếng Việt, gọn, tối đa khoảng 250 dòng, theo thứ tự:
1. **Tóm tắt 10 dòng cho chủ kênh:** quyết định cần duyệt, mỗi dòng một việc.
2. **Mỗi kênh một mục:**
   - bảng NHẬN / SỬA / BỎ;
   - 3 việc ưu tiên;
   - bao bì Long cần đổi.
3. **MIM/CK:** bảng Short đã lên lịch cần xem lại, và phương án cho slot trống.
4. **Nguồn web đã dùng:** URL.
5. **Những gì không kiểm được.**

Câu trả lời cuối của bạn trên terminal: tối đa 5 dòng, gồm số đề xuất mỗi kênh và đường dẫn báo cáo.
