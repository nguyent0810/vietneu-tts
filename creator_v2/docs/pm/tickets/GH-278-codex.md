# GH-278 — Codex: phim tư liệu phạm vi công cộng làm b-roll cho Long creator_v2

Issue: https://github.com/nguyent0810/vietneu-tts/issues/278 (đọc phần "Việc", "Đạt khi" và "Luật chung").
Worktree của bạn: thư mục hiện tại (`wt-278`, nhánh `feat/278-pdvideo-long`). Chỉ ghi trong worktree này.

## Bối cảnh đã có
- `../hf_pdvideo.py` (gốc repo, cùng repo với `creator_v2/`): search / info / strip / fetch cho `commons:`, `ia:`, `nasa:`; cắt mp4 1920×1080 không tiếng ≤ 20 s, `--fit cover|pad|blur`, ghi `.json` giấy phép cạnh mp4. **Dùng lại hàm của file này (import), không viết lại cách lấy nguồn/giấy phép.**
- Long builder: `motion/long/build_long.py` (cảnh `broll` hiện lấy clip Pexels/ổ đĩa; tìm cách nó resolve `vid`/clip và credits → `credits.json` → `describe.py`).
- `motion/long/media_search.py`: tìm ảnh/clip cho Long.
- Danh mục ref đã kiểm cho Mata Hari: `docs/pm/tickets/GH-278-agy-refs-report.md` (trên main có thể chưa có; nếu thiếu thì đọc ở `../../vietneu-main/creator_v2/docs/pm/tickets/`). Lead đã loại `ia:H-1518` (community, tự khai) và clip CC BY 3.0 "Third Aviation Instruction Center".

## Việc
1. Cảnh `broll` nhận khoá `"pd": "<ref>"`, `"start"`, `"dur"` (≤ 20), `"fit"` (mặc định `blur` nếu nguồn 4:3, ngược lại `cover`), `"label"` (mặc định `TƯ LIỆU <năm>` lấy từ metadata nếu có). `build_long.py html` tải/cắt qua hf_pdvideo vào `output/long/<topic>/pd/` (hoặc cache chung rồi copy/hardlink), giữ `.json` giấy phép, và đưa clip vào HTML như b-roll thường. Nhãn hiển thị trên khung theo kiểu nhãn nguồn/tư liệu đang có của engine (không tạo kiểu chữ mới lạc theme).
2. **Bộ lọc giấy phép chặt hơn hf_pdvideo** (đặt trong wrapper creator_v2, không sửa luật BUD/FS):
   - Commons: chỉ CC0 / Public domain / PDM. CC BY, BY-SA → từ chối (lý do rõ).
   - Internet Archive: chỉ collection `prelinger`, FedFlix/NARA (`fedflix`, `national_archives`…), cơ quan liên bang Mỹ, hoặc phim năm ≤ 1930 có PDM. Collection `opensource_movies`/community tự khai → từ chối.
   - NASA: nhận (bỏ item có ©) như hf_pdvideo.
   - Ref bị từ chối → `build_long.py html` dừng với thông báo nêu ref + lý do (không im lặng bỏ cảnh).
3. Credit tự vào mô tả: mỗi clip pd thêm một dòng nguồn (tiêu đề, nơi lưu, giấy phép, trang nguồn) vào `credits.json` để `describe.py` in ra như với ảnh.
4. `media_search.py`: lệnh con `pd "<từ khoá>" [--decade 1910] [--src commons|ia|nasa] [--n 20]` liệt kê ref đạt luật mục 2; và `pd-strip "<ref>"` in dải khung hình (dùng `strip` của hf_pdvideo).
5. `floor.py`: các cảnh `broll` có `pd` được tính là b-roll (như clip thường).
6. Spec cũ không có `pd` → HTML y hệt trước (test so byte hoặc so cấu trúc cảnh).
7. Cập nhật `motion/long/README.md`: bảng khoá `pd`, ví dụ JSON, luật giấy phép.

## Test (mạng bị chặn thì mock hàm lấy metadata của hf_pdvideo)
- `tests/test_pdvideo_long.py`: ref CC BY bị chặn; ref IA community bị chặn; ref hợp lệ (mock) sinh mp4 path + json và có dòng credit; spec cũ không đổi; floor đếm pd là b-roll.
- `PYTHONIOENCODING=utf-8 python -m pytest tests -q` phải xanh (nếu sandbox chặn thư mục tạm, ghi rõ lỗi nào do môi trường).

## Không làm
- Không render, không gọi Chrome/ffmpeg ngoài phạm vi fetch (nếu sandbox chặn mạng/ffmpeg thì ghi lệnh để Lead chạy).
- Không commit, không push, không đăng, không đụng credentials, không sửa `data/long/*` của topic thật.
- Ghi file bằng Python utf-8; grep diff để chắc không có `?` thay chữ có dấu.

## Báo cáo
Ghi `docs/pm/tickets/GH-278-report.md` (tiếng Việt): file đã sửa, khoá mới, kết quả test, lệnh để Lead dựng thử 3 clip Mata Hari (`build_long.py <bản sao> html chNN` + render draft).
