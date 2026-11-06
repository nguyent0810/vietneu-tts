# GH-183: phân tích Analytics CL và bộ khuôn tiêu đề CL

**Dữ liệu (chỉ đọc, kéo ngày 06/11, đủ 686 video):** `data/analytics/CL/183/`
- `analysis.md`: bảng đã dựng;
- `videos.json`;
- `byvideo_d28/d7/d365.json`;
- `video_x_source.json`: nguồn traffic từng video. `SUBSCRIBER` = Browse/Home, `RELATED_VIDEO` = Đề xuất, `EXT_URL` = bên ngoài;
- `video_x_day.json`;
- `channel_windows.json`.

Không suy ngược số thiếu. API không có impressions hay CTR (xem `probe.json`).

**Việc 1, phân tích Long CL (31 Long công khai):**
- Vì sao *Khun Sa* (215 giờ, Browse 97%) và *Đỗ Nguyệt Sanh* (134 giờ, Đề xuất 38%) thắng, còn *Bulger*, *Capone*, *Escobar* và các bài khác thì không? So theo:
  - nguồn traffic;
  - AVD/AVP;
  - đường cong lượt xem theo ngày sau khi đăng (`video_x_day`);
  - ngày và giờ đăng;
  - tiêu đề.
- Long *Escobar* có AVP 69% nhưng ít lượt xem: lý do là gì, và giữ người xem vẫn tốt đến đâu.
- Short CL: Short nào kéo sub tốt nhất, Short loại nào nối được sang Long (nếu dữ liệu cho thấy).

**Việc 2, bộ khuôn tiêu đề CL:**
- Từ số thật, rút 4–6 khuôn tiêu đề. Mỗi khuôn ghi:
  - cấu trúc, ví dụ `[PHIM/NƠI] Ngoài Đời Thật: [người] — [nghịch lý có số]`;
  - video đã dùng khuôn đó và số liệu của chúng;
  - độ dài ký tự;
  - phần gây tò mò nằm trong bao nhiêu ký tự đầu;
  - mức bằng chứng: mạnh, yếu, hay chỉ 1 mẫu.
- Các khuôn đã thua, ví dụ kiểu "Bí Ẩn…" cũ.
- Luật độ dài cho CL (hiện `title_max` 100).
- Đối chiếu 8 cơ chế kể của nghiên cứu packaging #111 (vỡ kỳ vọng, đảo quyền lực…), nếu tìm thấy file trên nhánh `research/*`. Không tìm thấy thì bỏ qua.

**Được ghi:**
- `docs/pm/2026-11-06-cl-analytics.md` (báo cáo phân tích);
- `docs/pm/title-patterns-cl.md` (bộ khuôn);
- báo cáo ticket `docs/pm/tickets/GH-183-cl-analysis-report.md`.

Tất cả UTF-8. Repo public: không dán số liệu thô từng video vượt quá các bảng tóm tắt, không ghi token hay đường dẫn credentials. Không sửa code, không commit.
