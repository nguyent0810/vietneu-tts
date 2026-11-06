# GH-183: bộ khuôn tiêu đề MIM và CK từ số liệu thật

**Mẫu cần làm theo:** `docs/pm/title-patterns-cl.md`, gồm cả ghi chú mức bằng chứng ở đầu file, và `docs/pm/2026-11-06-cl-analytics.md`.

**Dữ liệu** (chỉ đọc, kéo ngày 06/11): `data/analytics/MIM/183/` và `data/analytics/CK/183/`. Mỗi thư mục có `analysis.md`, `videos.json`, `byvideo_*.json`, `video_x_source.json`, `video_x_day.json`. Mã nguồn: `SUBSCRIBER` = Browse/Home, `RELATED_VIDEO` = Đề xuất, `EXT_URL` = bên ngoài, `YT_SEARCH` = tìm kiếm.

**Việc**, làm riêng cho MIM và cho CK:
1. Long công khai: xếp theo giờ xem 28 ngày. Cho top 5 và bottom 5, so tiêu đề, độ dài, nguồn traffic, AVD và AVP. MIM có 5 Long vừa đổi tiêu đề ngày 06/11 (PR #200), chưa có số mới; ghi rõ như vậy.
2. Short: top 10 theo lượt xem, cùng tỉ lệ ở lại xem (engagedViews/views) nếu có.
3. Rút 3–5 khuôn tiêu đề Long và 2–3 khuôn tiêu đề Short. Mỗi khuôn ghi:
   - cấu trúc;
   - video đã dùng, kèm số liệu;
   - độ dài;
   - mức bằng chứng: **đo** hay **suy luận**, và số mẫu.

   Ghi riêng các khuôn đã thua.
4. Giới hạn ký tự: MIM và CK đang ở 60. Nếu số liệu cho thấy bài dài hơn vẫn thắng thì ghi đề xuất, nhưng **không sửa** `library/channels/*.yaml`.
5. Không suy ngược số liệu API không có (impressions, CTR, thiết bị).

**Được ghi:**
- `docs/pm/title-patterns-mim.md`;
- `docs/pm/title-patterns-ck.md`;
- báo cáo `docs/pm/tickets/GH-183-mimck-patterns-report.md`.

**Bắt buộc:**
- ghi file bằng Python `open(..., "w", encoding="utf-8")`, không dùng PowerShell `Set-Content`/`echo`;
- trước khi kết thúc, chạy `python -c "import sys;bad=[f for f in ['docs/pm/title-patterns-mim.md','docs/pm/title-patterns-ck.md'] if '???' in open(f,encoding='utf-8').read() or 'Kh?ng' in open(f,encoding='utf-8').read()];print(bad);sys.exit(1 if bad else 0)"`;
- repo public: chỉ đưa bảng tóm tắt, không dán dữ liệu thô;
- không commit.
