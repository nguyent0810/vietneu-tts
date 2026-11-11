# GH-285 phần 1: tải bù nhạc thiếu và thêm nhạc sĩ CC BY (agy hoặc Grok)

Đọc issue: `gh issue view 285 --repo nguyent0810/vietneu-tts`. Phần code (`variety.py`, `describe.py`) giao Codex sau. Bạn chỉ **tải file và kiểm giấy phép**.

## Môi trường
- Thư mục làm việc: `D:\Tools\Youtube Creator v2\wt-285\creator_v2`.
- Danh mục hiện có (chỉ đọc): `motion/long/music_catalog.json`. Khóa `tracks` là dict `slug -> {file, title, author, license, mood, channel?}`.
- Kho file hiện có (chỉ đọc, **không ghi vào đây**): `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\output\music\`.
- **Chỉ được ghi** vào `tmp_music/` (tạo mới) trong thư mục làm việc và vào file báo cáo. Không sửa `music_catalog.json`.

## Việc
1. **Bài thiếu file:** so `tracks[*].file` với kho file hiện có, liệt kê bài thiếu (khoảng 23 bài, chủ yếu loạt SCP, Anguish, Plaint, Disquiet). Tải từng bài từ incompetech.com (Kevin MacLeod, CC BY 4.0) vào `tmp_music/macleod/<file>` đúng tên trong danh mục. Kiểm tên bài khớp `title`.
2. **Nhạc sĩ mới**, mỗi người khoảng 15–25 bài:
   - **Scott Buckley** (scottbuckley.com.au, CC BY 4.0): điện ảnh, dàn dây, piano tối. Hợp CL và Long lịch sử.
   - **Chris Zabriskie** (chriszabriskie.com hoặc Free Music Archive, CC BY 4.0): ambient, tò mò. Hợp MIM.
   - **Kai Engel** (Free Music Archive): piano, ambient. Hợp CK và đoạn lắng. **Chỉ lấy bài ghi CC BY 4.0 hoặc CC BY 3.0.** Bỏ mọi bài có NC hoặc ND.
   - Lưu vào `tmp_music/<tác giả>/<slug>.mp3`, slug viết thường, gạch dưới.
   - **Không** dùng Pixabay, YouTube Audio Library hay trang tổng hợp không rõ nguồn.
   - Ưu tiên bài không lời, dài ≥ 2 phút, không có đoạn trống dài.
3. Với **mỗi bài** (cả bài tải bù), ghi một mục vào `tmp_music/proposed_catalog.json`, cùng khuôn với danh mục:
   `{"<slug>": {"file", "title", "author", "license", "license_url", "source_url", "mood": [...], "channel": [...] hoặc bỏ trống nếu là CL, "duration_s"}}`
   - `source_url`: trang của chính bài đó (không phải trang chủ).
   - `license`: đúng chữ ghi trên trang bài. Không thấy ghi giấy phép thì **không tải**.
   - `mood`: chọn trong tense | dark | sad | epic | mystery | quiet (CL), hoặc curious | upbeat | calm | epic | warm | mystery (MIM/CK).
   - `duration_s`: đo bằng ffprobe.

## Tiêu chí đạt
- Không còn bài thiếu file, hoặc ghi rõ lý do từng bài không tải được.
- Mỗi kênh có thêm đủ bài để đạt ≥ 40 bài dùng được, từ ≥ 3 tác giả.
- 100% bài mới có `source_url` và `license` kiểm được.

## Báo cáo
Ghi `docs/pm/tickets/GH-285-agy-report.md` (tiếng Việt có dấu, utf-8): số bài tải theo tác giả và kênh, danh sách bài bỏ kèm lý do, mọi nghi ngờ về giấy phép.

Không commit, không sửa danh mục, không xóa file. **Phải làm đủ. Dừng giữa chừng tính là hỏng.**
