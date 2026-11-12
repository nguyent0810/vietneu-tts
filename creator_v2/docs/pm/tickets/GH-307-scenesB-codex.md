# GH-307: Lưu Gù, bước 4 phần B (CH07–CH13) (Codex)

Đọc issue: `gh issue view 307 --repo nguyent0810/vietneu-tts`. Chủ kênh đã duyệt đề tài, Lead đã duyệt kịch bản bản 2. Bước 4 chia hai phần. Phần A (CH00–CH06, khung `gen_scenes.py`, `spec.json`) đã xong và đã commit; đọc `docs/pm/tickets/GH-307-scenesA-report.md`. Phần này làm **CH07–CH13** trong `gen_scenes2.py` (`from gen_scenes import ...`, chỉ khai `CH`). **Phải viết code cảnh thật, không được chỉ báo cáo.**

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-luugu`, nhánh `long/cl-luu-gu`. Mọi đường dẫn tính từ `creator_v2/` của worktree. Lead commit.
- Python: `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`, hoặc `python`.
- Ảnh: `output/long/cl-luu-gu/research.json` (167 ảnh tự do) cùng các bảng `sheet_0.jpg` đến `sheet_4.jpg` (36 ảnh mỗi bảng, đánh số). Hãy xem các bảng ảnh. Một số ảnh lạc đề không được dùng:
  - đồ ăn;
  - ga tàu, cửa hàng tiện lợi, tòa nhà Hàn Quốc hiện đại;
  - ảnh một chính khách hiện đại trùng tên Lưu Dung.
  Ở bảng `sheet_3`, đó là các ảnh #13, #14, #15, #16 và #21 (chỉ số trong bảng; chỉ số tổng = 3×36 + chỉ số trong bảng). Tự kiểm lại bằng tên file trong `research.json`.

## Khuôn mẫu
Chép cấu trúc `data/long/hoa-than/`, đây là Long CL gần nhất và cùng bối cảnh nhà Thanh:
- `gen_scenes.py`: `IMGS` theo số thứ tự trong `research.json`, hàm `im(i, must)`, `GEO`, `CH["chNN"] = dict(hud=..., bgm=..., scenes=[sc(...), ...])`, `__main__` nạp `gen_scenes2.py`, và ghi ra bằng `scenekit.write`.
- `balance.py`: chép nếu dùng.
- Đọc thêm `data/long/bao-thanh-thien/gen_scenes.py`, `data/long/golden/gen_scenes.py`, `motion/long/README.md` (thẻ thông tin #276, chữ động #277) và `CLAUDE.md` bước 4.
- Brief cũ đã chạy tốt ở Long Hòa Thân: `docs/pm/tickets/GH-179-hoathan-scenesA-codex.md` và các báo cáo scenesA–D, densify, gatefix. Đọc để tránh các lỗi đã gặp.

## Nguồn sự thật
- Thứ tự và chữ theo `data/long/cl-luu-gu/script.md`. Mỗi `sc(kind, câu_số, ...)` neo vào câu thật; `hitAt` và `at` dùng từ có thật trong câu đó.
- Mọi số, ngày, tên, trích dẫn trên màn hình phải có trong `factcheck.md`. Câu gán biệt danh hay vai trong phim phải đúng người: "Lưu gù" trong phim là **Lưu Dung**, không phải Hòa Thân.
- Giai thoại hiện trên màn hình phải gắn nhãn GIAI THOẠI, phim gắn nhãn PHIM.
- Không có ảnh AI ở phần này. Không cần nhóm B/C; nếu cần lấp nhịp, dùng motion graphics (timeline, bản đồ Sơn Đông, Hồ Nam, Bắc Kinh, thẻ thông tin, chữ động, ledger).
- Không ảnh hay clip từ phim 1996.

## Yêu cầu
- Nhịp trung bình 3–5 giây/cảnh, không khoảng nào quá 8 giây. Không còn cảnh `"auto": true`.
- Ảnh chân dung Lưu Dung và thư pháp của ông là xương sống. Ảnh chân dung quan lại khác thì chỉ dùng khi lời đọc nói về "quan lại" chung, không gán là Lưu Dung.
- `spec.json`:
  - `channel: "CL"`, `title` ≤ 60 ký tự, `acc` gồm tên nhân vật chính;
  - `say` cho tên nước ngoài nếu có;
  - theme, look và nhạc theo Long CL gần nhất, nhưng phải khác 3 video gần nhất (`motion/variety.py`).
- Đây là topic mới (không có trong `_legacy_topics.json`), nên chữ động #277, thẻ thông tin #276, cine_auto và nhạc dài hạn #285 tự bật. Đừng tắt.

## File được ghi
- `data/long/cl-luu-gu/gen_scenes2.py` (mới), `ch07.json` đến `ch13.json`. Được sửa `gen_scenes.py` chỉ để thêm ảnh vào `IMGS` hoặc helper dùng chung; không đổi cảnh CH00–CH06. `spec.json` chỉ thêm khóa nếu cần cho phần B.
- Báo cáo.
- Không sửa engine, `scenekit`, `build_long.py`, `factory/`, `script.md`, `factcheck.md`. Không chạy TTS hay render.

## Kiểm sau khi viết (từ creator_v2 của worktree)
1. `python data/long/cl-luu-gu/gen_scenes.py`: sinh được `chNN.json`.
2. `python motion/long/cadence.py cl-luu-gu`: ghi số các chương đã làm.
3. `python motion/long/scene_params.py cl-luu-gu`.
4. `PYTHONIOENCODING=utf-8 python motion/variety.py audit cl-luu-gu` phải đạt.
5. `python scripts/long_gate.py cl-luu-gu`: lỗi còn lại chỉ được là thiếu TTS và `spec.youtube` (publish_at, playlist, video_credits: Lead điền ở bước 8). Mọi lỗi khác phải sửa. Đặc biệt: số ảnh khác nhau ≥ 40 trên toàn video và số loại cảnh theo `floor.py`.

## Tiếng Việt
Ghi mọi file bằng Python `encoding="utf-8"`. Grep để chắc không có `???` hay `�`.

## Báo cáo
`docs/pm/tickets/GH-307-scenesB-report.md`: số cảnh từng chương, ảnh đã dùng, kết quả 4 lệnh kiểm, và những chỗ kịch bản khó minh họa.

Không render, không commit, không đăng.


## Lưu ý riêng phần B
- CH07 (Sơn Đông 1782) là phần thưởng giữa video. Dùng bản đồ Sơn Đông và thẻ thông tin cho Quốc Thái, Tiền Phong. Không gán hành động ở kho bạc cho Lưu Dung khi kịch bản không nói vậy.
- CH10 (tháng 2/1799) đóng vòng mở bài. Không dựng cảnh thẩm vấn. Lệnh kê biên giao cho một nhóm người.
- CH11 (biệt danh) là cảnh mạnh. Ba khối SỬ / GIAI THOẠI / PHIM tách bằng nhãn rõ. Không dùng ảnh hay clip phim.
- CH12 (thư pháp): dùng nhiều ảnh thư pháp thật của Lưu Dung trong research.json.
