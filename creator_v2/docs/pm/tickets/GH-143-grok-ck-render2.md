# GH-143 · Grok: render lại Short `ck-them-10-trieu-gio-bot-mot-mon`

Issue: https://github.com/nguyent0810/vietneu-tts/issues/143. Lần render trước (`docs/pm/tickets/GH-143-render-report.md`) hỏng: hình đứng ở cảnh mở suốt 34 giây, vì spec dùng `"type": "clip"` mà engine không có loại cảnh này.

Lead đã sửa spec: cảnh 1 và 7 thành `kinetic`, có `"clip": "pexels:6288844"` và `"clip": "pexels:7889399"` (đúng hai clip bạn đã chọn), `win: top`. Preflight: `OK — 108 từ, ước lượng 32.7s`.

**Hạn:** 40 phút.

## Được ghi
- `output/stier/ck-them-10-trieu-gio-bot-mot-mon/**`
- báo cáo `docs/pm/tickets/GH-143-render2-report.md`

**Không:**
- sửa spec, `lines`, code;
- upload, enqueue, đổi lịch;
- commit;
- đọc credentials.

## Việc
1. Render lại: `python motion/stier/build.py ck-them-10-trieu-gio-bot-mot-mon`.
2. **Kiểm cảnh thật sự chạy.** Lấy khung ở giây 1, 4, 8, 12, 16, 20, 24, 28, 32. Mỗi khung phải khác cảnh mở, và phải thấy được:
   - clip giỏ hàng;
   - bộ đếm CPI;
   - các thẻ VÍ DỤ GIẢ ĐỊNH;
   - clip súp lơ;
   - câu kết.

   Nếu vẫn đứng hình, đọc log hoặc console của composition, ghi lỗi rồi dừng.
3. Tờ soát:
   - `qa_sheet.png`, 20 khung đều theo thời gian;
   - đo LUFS và true peak.
4. Ghi lại khung nào có chữ tràn, chữ đè, hoặc nhãn VÍ DỤ GIẢ ĐỊNH bị che.

## Báo cáo
- Trạng thái.
- Thời lượng.
- Đường dẫn file.
- Mô tả ngắn từng khung đã lấy.
- LUFS và true peak.
- Lỗi quan sát được.

Không tự kết luận "đạt". Câu trả lời cuối: tối đa 3 dòng.
