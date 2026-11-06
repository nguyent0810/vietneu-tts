# GH-179 — Báo cáo cadence

Đã tạo `motion/long/cadence.py` và `tests/test_cadence.py`. CLI xuất từng chương và toàn video, JSON khi có `--json`; cảnh báo trung bình chương trên 5 giây hoặc khoảng trên 8 giây, không chặn.

## Kiểm tra

- `python -B -m unittest tests.test_cadence -v`: 5 test đạt, gồm đếm cảnh, bước con và sự kiện đồng thời, phân nhóm, timing và ước lượng.
- Lần chạy test đầu dùng thư mục tạm mặc định của Windows bị từ chối quyền ghi; đã chuyển test sang dữ liệu giả trong bộ nhớ và chạy lại thành công. Không dọn các thư mục tạm do quy định không xóa ngoài phạm vi ticket.
- `python motion/long/cadence.py bao-thanh-thien --json` và lệnh tương tự với `golden`: thành công.
- Không chạy lint riêng; không render, upload hoặc commit. Không có clip sheet hay thumbnail vì ticket không yêu cầu dựng video.

## Mốc so sánh ước lượng

Cả hai topic không có `output/long/<topic>/` trong worktree. Mỗi chương được gán 150 giây theo fallback trong `build_long.py`, rồi phân bổ theo số từ. Đây không phải thời gian video thực; số thay đổi và khoảng dài nhất cũng phụ thuộc mốc ước lượng, không dùng làm kết luận chất lượng bản render.

| Topic | Thay đổi | Giây/thay đổi | Khoảng dài nhất | D | B-roll | UNKNOWN | Chương cảnh báo |
|---|---:|---:|---|---:|---:|---:|---:|
| bao-thanh-thien | 639 | 3,29 | 16,86 s, ch00#4 (slam) | 6,96% | 38,44% | 54,61% | 10/14 |
| golden | 634 | 3,31 | 16,53 s, ch03#13 (file) | 21,27% | 10,01% | 68,72% | 14/14 |

Các nhóm A/B/C/AI hiện 0% vì không có metadata ảnh output; UNKNOWN không có nghĩa là không có ảnh tư liệu. Chỉ số cảnh tính từ 0. CLI cung cấp chi tiết từng chương và tỷ lệ nhóm.

## Giới hạn cần Lead review

- `scene_params.py` không có công thức ước lượng thời lượng; 150 giây là fallback của `build_long.py`, không phải thời lượng TTS. Có `data.js` sẽ ưu tiên timing cảnh đã lập kế hoạch; nếu chỉ có `timing.json`, mốc từ được nội suy theo vị trí từ, không phải căn âm thanh thực. `data.js` có thể cũ hơn spec và cần được xây lại để kết quả phản ánh spec hiện tại.
- Luật đếm chỉ bao phủ các chuỗi có lịch được `build_long.plan` khai báo rõ (gồm ledger, timeline, map, kinetic và một số loại khác). Chưa chứng minh đầy đủ mọi bước ảnh, zoom/pan và các hiệu ứng khác; chuyển động liên tục không được tính. Không đọc engine theo luật repo, nên cần Lead xác nhận các bước có thực sự xuất hiện theo thời gian và mở rộng nếu cần. Vì vậy chưa thể coi đây là phép đo đầy đủ mọi thay đổi hình đáng kể.
- Tỷ lệ chỉ gán một nhóm cho mỗi cảnh, b-roll ưu tiên khi có clip; ảnh không có metadata nguồn hoặc cảnh chứa nhiều nhóm ảnh khác nhau là UNKNOWN. Không có số liệu xác minh thực tế cho hai topic trong worktree này.
