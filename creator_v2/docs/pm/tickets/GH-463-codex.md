# GH-463 bước 3 — Lọc nhạc Short MIM/CK theo mood + đề xuất thống nhất loudness

Bạn đang chạy TRONG worktree riêng `D:\Tools\Youtube Creator v2\wt-463` (nhánh `lead/463-music-pools`). Đường dẫn tính từ `creator_v2/` trừ khi ghi khác. Không đụng checkout `vietneu-main`.

## Bối cảnh
Chủ kênh duyệt 17/11/2026 (#463). Báo cáo `docs/research/2026-11-17-giong-vieneu-bgm-sfx-theo-kenh.md` (có trên main) chỉ ra: pool nhạc Short MIM (24 bài) và CK (26 bài) trong `motion/stier/themes.py` có nhiều bài upbeat/jazz không hợp giọng kể chuyện tài liệu; và hai chuẩn loudness cùng tồn tại (-14 LUFS ở creator_v2, -16 LUFS ở `hf_sound.py` gốc repo cho FS/BUD).

## Việc
1. Gắn nhãn mood cho từng bài trong pool MIM và CK của `motion/stier/themes.py` (vd `calm`, `tense`, `wonder`, `upbeat`, `jazz`). Căn cứ: tên bài, thể loại Incompetech (trang incompetech.com có genre/feel cho từng bài; được phép mở web), và đo nhanh nếu file có trong `output/music/` (tempo/độ sáng phổ bằng ffmpeg/numpy). Ghi nhãn ở dạng dữ liệu (dict trong themes.py hoặc JSON trong `data/variety/`), không đổi tên file nhạc.
2. Bộ chọn nhạc Short MIM/CK chỉ lấy bài có mood hợp kể chuyện (`calm`, `tense`, `wonder`; CK thêm `light` nếu có); bài `upbeat`/`jazz` bị loại khỏi vòng xoay mặc định nhưng vẫn chọn được nếu spec ghi rõ tên bài. Giữ luật xoay vòng/không lặp hiện có.
3. Loudness: CHỈ viết đề xuất, không sửa `hf_sound.py` hay pipeline FS/BUD (thuộc luồng khác). Đo/đọc code để nêu: mỗi pipeline đặt mục tiêu ở đâu (file:dòng), chênh lệch thực tế, và phương án thống nhất (một hằng số chung hoặc tài liệu hoá lý do khác nhau).

## Test
Thêm test cho bộ lọc mood (bài upbeat không vào vòng xoay mặc định; spec ghi tên vẫn chọn được). Chạy `python -m pytest -q tests` và báo dòng cuối.

## File được ghi
`motion/stier/themes.py`, file chọn nhạc liên quan trong `motion/stier/` (ghi rõ trong báo cáo), `data/variety/*mood*.json` nếu tạo, test mới trong `tests/`, báo cáo `docs/pm/tickets/GH-463-codex.report.md` (UTF-8, ghi bằng Python; gồm danh sách nhãn mood từng bài và đề xuất loudness). Không commit, không render, không tải nhạc mới.
