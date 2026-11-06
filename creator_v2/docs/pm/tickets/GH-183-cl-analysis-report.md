# GH-183 — Báo Cáo Phân Tích Analytics CL & Bộ Khuôn Tiêu Đề CL

**Ticket:** `docs/pm/tickets/GH-183-cl-analysis-agy.md`  
**Ngày thực hiện:** 06/11/2026  
**Agent thực hiện:** Codex / Antigravity Agent  
**File được ghi:**
1. `docs/pm/2026-11-06-cl-analytics.md` (Báo cáo phân tích chuyên sâu Long/Short kênh CL).
2. `docs/pm/title-patterns-cl.md` (Bộ khuôn tiêu đề thực chiến chuẩn hóa cho CL).
3. `docs/pm/tickets/GH-183-cl-analysis-report.md` (File báo cáo nghiệm thu ticket này).

---

## 1. Đã Làm (Theo Đúng Phạm Vi Brief)

### Việc 1 — Phân tích Long CL (31 Long công khai) & Short CL:
1. **Bóc tách toàn diện 31 video Long công khai:** Khớp nối mã video, tiêu đề, thời lượng, thời điểm đăng, views 28d, giờ xem 28d, AVD, AVP, giờ xem trọn đời 365d và nguồn traffic chi tiết từ `data/analytics/CL/183/`.
2. **So sánh cơ chế thắng của Khun Sa vs Đỗ Nguyệt Sanh:**
   - *Khun Sa (215,3h):* Thắng nhờ **Browse / Trang chủ (SUBSCRIBER 97%)**. Đạt đỉnh 2.688 views/ngày vào Chủ Nhật (19/10), sau khi đăng vào tối Thứ Sáu (17/10). Yếu tố quyết định là IP "Tam Giác Vàng" quen thuộc với người Việt và hook "Mỹ Treo Thưởng 2 Triệu Đô".
   - *Đỗ Nguyệt Sanh (134,2h 28d, 307,9h trọn đời):* Thắng nhờ **Đề Xuất bền bỉ (RELATED_VIDEO chiếm 63,8% giờ xem trọn đời = 196,4h)**. Bám chắc vào biển nội dung phim ảnh "Bến Thượng Hải" với nghịch lý đảo quyền lực kinh điển ("Từ Cậu Bé Bán Lê Đến Ông Trùm Thanh Bang").
3. **Lý giải thất bại của Bulger, Capone, Escobar, Trịnh Nhất Tẩu, Bảy Viễn:**
   - Đều có đường cong "tắt lịm" (flatline) sau 24–48h, không kích hoạt được luồng Browse.
   - Bối cảnh phương Tây xa lạ (Boston, Chicago, Colombia) thiếu điểm tựa văn hóa với khán giả Việt Nam.
   - Điểm rơi ngày đăng rơi vào giữa tuần (Thứ Ba, Thứ Năm), không tận dụng được thời gian rảnh cuối tuần của người xem cho video 25–30 phút.
4. **Mổ xẻ video Pablo Escobar (AVP 68,7% nhưng chỉ 74 views):**
   - 43% lượt xem và 69% tổng phút xem (885 phút) đến từ nguồn link ngoài `EXT_URL` với AVD lên tới 28:33 (xem hết 97% video).
   - Với người xem tự nhiên từ YouTube Browse (`SUBSCRIBER`), AVD thực tế là 12:46 (AVP ~43%), vẫn là mức giữ chân rất tốt chứng minh kịch bản và nhịp dựng cuốn hút.
   - Nguyên nhân ít view là do thuật toán không phân phối (Browse chỉ 22 views, Related chỉ 7 views) bởi IP "Narcos" quá hẹp và tiêu đề chạm trần 100 ký tự khiến hook bị cắt cụt trên mobile.
5. **Phân tích 531 Short CL:**
   - Xác định top Short kéo sub tốt nhất: *Mata Hari* (+6 sub / 959 view = 0,63% chuyển đổi), *Ông hàng thịt* (+3 sub), *Người khổng lồ giả* (+3 sub, 61,6% ở lại), *Hai hoàng tử* (+3 sub), *Bắn người trước trăm nhân chứng* (+3 sub).
   - Chỉ ra 3 cơ chế Short thắng: Nghịch lý hành động trước cái chết/tòa án; Bóc trần cú lừa thân phận; Chi tiết hiện trường tử huyệt.
   - **Xác nhận đứt gãy phễu Short -> Long:** Toàn bộ 31 video Long có **0 lượt xem từ nguồn SHORTS**. Kênh chưa cài đặt tính năng Related Video link trong YouTube Studio và chủ đề Short/Long bị phân mảnh độc lập.

### Việc 2 — Xây dựng Bộ khuôn tiêu đề CL:
1. **Rút 5 khuôn tiêu đề Long thực chiến từ số liệu thực tế:**
   - Khuôn 1: `[IP / ĐỊA DANH QUEN THUỘC] Ngoài Đời Thật: [Nhân Vật] — [Nghịch Lý Có Số]` (Bằng chứng: Cực mạnh, chiếm 85% giờ xem VOD).
   - Khuôn 2: `[TỔ CHỨC / ĐỐI TƯỢNG]: [Nghịch Lý Hành Động] — [Hậu Quả Bất Ngờ]` (Bằng chứng: Mạnh về Evergreen, Yakuza hút 103h trọn đời).
   - Khuôn 3: `[ĐỊA DANH BÍ ẨN] Ngoài Đời Thật: [Bộ Ba Số Liệu Đối Lập]` (Bằng chứng: 1 mẫu, Cửu Long Thành Trại AVP 37%).
   - Khuôn 4: `[NHÂN VẬT LỊCH SỬ]: [Danh Xưng / Nhãn Đối Kháng] Và [Sự Kiện Chấn Động]` (Lưu Vĩnh Phúc, Bao Thanh Thiên, Hòa Thân).
   - Khuôn 5: `[TÊN TỘI PHẠM BÍ ẨN] Là Ai? [Chuỗi Số Nghịch Lý Hiện Trường]` (Jack the Ripper 5-100-0).
2. **Tổng hợp 3 khuôn hook Short đỉnh cao:** Dùng làm mẫu tham chiếu cho hook 15 giây đầu của Long.
3. **Chỉ mặt điểm tên 3 Anti-Patterns đã thua:**
   - Tính từ cảm tính rỗng tuếch kiểu Wiki cũ ("Bí ẩn kinh hoàng", "Sự thật rùng rợn", "Quyền lực máu" — 19 video đều dưới 10 views).
   - Đề tài phương Tây xa lạ không có neo văn hóa.
   - Nhồi nhét ký tự rác, tiếng Anh làm mất diện tích hiển thị trên mobile.
4. **Quy tắc độ dài tiêu đề cho CL (Mobile Safe Zone 45):**
   - Đề xuất hạ trần kỹ thuật từ 100 ký tự xuống **65–75 ký tự** (tối đa 85 ký tự).
   - Toàn bộ IP neo + tên nhân vật + từ khóa nghịch lý đầu tiên bắt buộc phải xuất hiện trước ký tự thứ 45 để không bị YouTube Mobile cắt cụt.
5. **Đối chiếu nghiên cứu packaging #111:** Kiểm tra toàn bộ git log và các nhánh `research/*`, không có tài liệu #111; đã quy đổi thành 4 cơ chế tâm lý thực chiến theo số liệu kênh.

---

## 2. Các Lệnh Đã Chạy

- Kiểm tra git branch và log tìm kiếm nhánh `research/*` và issue #111 (sử dụng `$env:GIT_CONFIG_GLOBAL="nul"` an toàn).
- Chạy Python 3.12 (`C:\Users\Tung-QA\.local\bin\python3.12.exe`) phân tích dữ liệu JSON trong `data/analytics/CL/183/`:
  - `videos.json` (686 video);
  - `byvideo_d28.json` (345 video có view 28 ngày);
  - `byvideo_d365.json` (556 video có view 365 ngày);
  - `video_x_source.json` (548 video có phân tách nguồn traffic);
  - `video_x_day.json` (đường cong lượt xem theo ngày);
  - `analysis.md`, `meta.json`, `probe.json`.
- Ghi 2 file tài liệu và 1 file báo cáo bằng Python `encoding="utf-8"`, không dùng PowerShell `Set-Content` làm lỗi font tiếng Việt.

---

## 3. Giả Định & Chỗ Thiếu Dữ Liệu

| Hạng mục | Thực tế dữ liệu | Hệ quả / Hướng xử lý |
|---|---|---|
| **CTR & Impressions** | API trả về mã lỗi 400 (`probe.json` xác nhận query không được hỗ trợ). | Không tự suy đoán CTR hay số lượt hiển thị thô; đánh giá sức hút mở đầu dựa trên lượt xem ngày đầu, tỷ trọng Browse (Home) và Đề xuất (Suggested). |
| **Dữ liệu chuyển đổi Short -> Long** | API ghi nhận 0 view từ nguồn `SHORTS` cho Long. | Không thể tính tỷ lệ click-through cụ thể giữa Short và Long; kết luận phễu hiện tại bị đứt gãy về mặt kỹ thuật và đề xuất giải pháp. |
| **Nghiên cứu packaging #111** | Không tìm thấy file trên các nhánh `research/*`. | Bỏ qua phần đối chiếu tài liệu theo hướng dẫn trong brief; thay thế bằng 4 cơ chế tâm lý thực tế rút ra từ số liệu kênh CL. |
| **Video mới Lưu Vĩnh Phúc (05/11)** | Vừa xuất bản hôm qua, chưa có số liệu 28d/365d trong đợt kéo 06/11. | Đưa vào nhóm Khuôn 4 với mức bằng chứng tiềm năng dựa trên công thức neo nhân vật lịch sử Á Đông. |

---

## 4. Tuân Thủ Quy Tắc AGENTS.md

- **Không upload, không sửa và không xoá gì trên YouTube.**
- **Không ghi `state.sqlite`** (chỉ đọc dữ liệu file json).
- **Không can thiệp git:** Không `git commit`, `git push`, `git reset`, `git checkout`, `git stash`.
- **Không sửa code dùng chung.**
- **Ghi toàn bộ file tiếng Việt bằng Python `encoding="utf-8"`** (không dùng PowerShell `echo`/`Set-Content`).
- **Không làm lộ credentials / token API.**

---

## 5. Kết Luận & Bàn Giao

Các file bàn giao đã hoàn tất:
1. Phân tích chi tiết: [`docs/pm/2026-11-06-cl-analytics.md`](file:///D:/Tools/Youtube%20Creator%20v2/vietneu-main/creator_v2/docs/pm/2026-11-06-cl-analytics.md)
2. Bộ khuôn tiêu đề chuẩn: [`docs/pm/title-patterns-cl.md`](file:///D:/Tools/Youtube%20Creator%20v2/vietneu-main/creator_v2/docs/pm/title-patterns-cl.md)

Ticket GH-183 hoàn thành đúng phạm vi, sẵn sàng để Lead và Claude điều phối sử dụng cho các ticket sản xuất CL tiếp theo (kế hoạch #177 Bao Thanh Thiên, Hòa Thân).
