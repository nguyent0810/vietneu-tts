# GH-147: render thử một chương có ảnh AI (MIM/CK không còn nhãn ẢNH MINH HỌA)

**Bối cảnh:** code #147 đã merge (commit e97506f). Khi dựng Long MIM/CK, ảnh AI không còn `illus` ("ẢNH MINH HỌA"), vẫn giữ `credit: false` (không in "TƯ LIỆU"). Ảnh thật vẫn giữ nhãn minh họa nếu có. Test `tests/test_gh147_ai_media.py` đã đạt. Còn thiếu bước kiểm trên khung hình thật.

**Việc:**
1. Topic `ck-f3-tien-mung-cuoi`. Topic này không có hoặc không có ảnh AI thì chọn một Long CK hoặc MIM khác có ảnh trong `output/long/<topic>/img/ai*.jpg`, và ghi lý do.
2. Tìm một chương có cảnh dùng ảnh AI (key `ai0N`). Chạy `python motion/long/build_long.py <topic> html`, rồi `render chNN --draft` cho đúng chương đó. Không render cả video, không chạy `final`.
3. Chụp khung lúc cảnh ảnh AI đang hiện (contact sheet hoặc snapshot) và soát:
   - không có chữ "MINH HỌA";
   - không có "TƯ LIỆU · PHẠM VI CÔNG CỘNG" trên ảnh AI;
   - ảnh thật trong cùng chương (nếu có) vẫn đúng nhãn như trước.
4. Không sửa code hay spec. Lỗi thì ghi vào báo cáo.

**Được ghi:** output render của topic đó và báo cáo `docs/pm/tickets/GH-147-render-report.md` (UTF-8). Không commit, không upload.

**Báo cáo:** topic, chương, đường dẫn ảnh khung, kết quả từng điểm soát.
