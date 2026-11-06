# Plan Long và Short tháng 11/2026 (MIM, CK, CL), bản 06/11

Căn cứ:
- Analytics API kéo ngày 06/11, đủ video (#183);
- `docs/pm/title-patterns-cl.md`, `-mim.md`, `-ck.md`;
- lịch thật: sổ `state.sqlite` và lịch hẹn trên YouTube của CL, đọc ngày 06/11;
- kế hoạch #177.

## 1. Hiện trạng lịch (06/11)

| Kênh | Long đã hẹn | Short đã hẹn | Còn trống trong tháng 11 |
|---|---|---|---|
| MIM | 16 Long, tới 01/12 | 94 Short, tới 04/12 | Không. Chỉ đo bao bì |
| CK | 12 Long, tới 22/11 | 24 Short, tới 16/11 | Long 23–30/11; Short 17–30/11 |
| CL | 07/11 (Đại Cathay), 08/11 (Bao Thanh Thiên) | 5 Short rải rác tới 25/11 | Gần hết tháng |

## 2. Ưu tiên (theo số liệu)
1. **CL trước tiên.** Chỉ CL đang tích được giờ xem: Long 503 giờ / 28 ngày, khuôn "[phim/địa danh quen] Ngoài Đời Thật: [người] — [nghịch lý có số]" chiếm 85%. Mục tiêu là thêm Long đúng khuôn, mỗi tuần 1 Long, không dồn hàng loạt. CLAUDE.md giới hạn mỗi lần chỉ dựng một Long; plan và kịch bản được chuẩn bị song song.
2. **CK:** Short dữ liệu tiền bạc giữ người xem tốt; Long gắn một quyết định thật (#181).
3. **MIM:** lịch đã kín. Đo tiêu đề mới (PR #200) ở mốc 72 giờ và 7 ngày.

## 3. Lịch dựng

### CL
| Ngày lên (21:00 VN) | Long | Trạng thái 06/11 |
|---|---|---|
| 15/11 (CN) | Hòa Thân (Tể tướng Lưu gù Ngoài Đời Thật) | Cảnh xong; đang làm giọng |
| 22/11 (CN) | CL Long 3, cùng khuôn: đề châu Á quen thuộc, ≥ 50 ảnh tự do | Cần chọn đề |
| 29/11 (CN) | CL Long 4 | Cần chọn đề |

- **Short CL:** 2 mỗi ngày (12:00 và 19:00 VN) từ 09/11 đến 30/11, khoảng 44 Short.
  - Loại L, 2–3 Short mỗi Long: nối về Bao Thanh Thiên, Hòa Thân, Long 3, Long 4, và các Long thắng (Khun Sa, Đỗ Nguyệt Sanh).
  - Loại S: vụ án hoặc nhân vật có một chi tiết lạ, đúng kiểu các Short CL đứng đầu ("Mắt xích còn thiếu…", "Ned Kelly…").
  - Né các ngày đã có Short: 17, 18, 19, 24, 25/11.

### CK
| Ngày lên | Long | Trạng thái |
|---|---|---|
| 24/11 | `ck-g1-tra-no-truoc-han` (trả 100 triệu nợ nhà hay gửi) | Kịch bản xong; dựng sau Hòa Thân |
| 28/11 | CK Long 2: bảo hiểm liên kết đầu tư (#181, đề 2) | Cần plan |

- **Short CK:** 3 mỗi ngày (17:30, 19:00, 22:00) từ 17/11 đến 30/11, 42 Short. Ngày 12/11 chạy luật dừng; nếu ra DỪNG thì 3/ngày vẫn nằm trong mức 2–3.
  - 17–19/11: 9 Short đang lắp lại hình (#180).
  - 20–30/11: 33 Short, chia 3 lô 11.
  - Loại L nối về các Long 18–28/11. Loại S theo khuôn "một con số tiền bạc thật + một quyết định".

### MIM
Không dựng thêm. Đo CTR từ Đề xuất của 5 tiêu đề mới. Lô tháng 12 theo brief #182.

## 4. Chuẩn chất lượng (bắt buộc)
- **Long:** plan → tư liệu (≥ 50 ảnh tự do) → `visual_plan` → kịch bản (factcheck 0 lỗi, gate lời đọc 0 lỗi) → cảnh (floor, `cadence` ≤ 5 s và khoảng dài nhất ≤ 8 s) → giọng → render → Lead QA contact sheet → thẻ duyệt tiêu đề → upload private kèm `publishAt`.
- **Short:**
  - ≥ 5 loại cảnh;
  - số chính hiện cỡ lớn;
  - một ảnh stock tối đa 1 cảnh, không dùng cùng một ảnh cho 2 bài;
  - cảnh ví dụ giả định có `hypo`;
  - qua preflight;
  - Lead xem contact sheet trước khi upload.
- **Tiêu đề** theo khuôn của kênh. Mỗi lần chỉ thay đổi một biến.

## 5. Phân công
Grok hết quota (402, ngày 06/11). Phân công lại:

| Việc | Giao ai |
|---|---|
| Viết lời, plan, kịch bản | agy (Claude Sonnet hoặc Gemini) |
| Spec, code | Codex |
| Render, giọng, QA khung | agy (Gemini Flash) |
| Ảnh, clip | Grok Bot |
| Duyệt và upload | Lead |

## 6. Đo
- Mỗi Long đo ở mốc 24 giờ, 72 giờ và 7 ngày.
- Rà tổng khoảng 03/12. Nếu giờ xem CL không tăng thì đổi đề tài, không tăng số lượng.
