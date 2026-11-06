# GH-190 (Codex): công cụ Long, 4 lỗ hổng lộ ra khi dựng Bao Thanh Thiên (#179)

Làm trong `creator_v2/`. Đọc `CLAUDE.md`, `AGENTS.md` và issue #190 trước.

## Phạm vi
- Được ghi: `motion/long/scene_params.py` (hoặc nơi có luật A7), `motion/long/stt_takes.py`, `motion/long/build_long.py` (chỉ phần kiểm ảnh ở bước `html`), `motion/long/lint_html.py` (chỉ phần báo thiếu font), `scripts/fetch_long_fonts.py` (mới, nếu cần), `tests/test_long_tools_190.py` (mới), và file báo cáo.
- Không được: render, upload, commit, đọc thư mục credentials, sửa `data/long/*`, hạ ngưỡng floor hay bất kỳ cổng nào khác.

## Việc
1. **A7 endcard:** luật thời lượng cảnh [2,5; 9] s đang chặn cảnh `endcard` 20 s mà golden dùng. Miễn trừ đúng loại `endcard`, có giới hạn trên hợp lý, ví dụ ≤ 25 s. Các loại cảnh khác giữ nguyên.
2. **STT không CUDA:** `stt_takes.py` hard-code CUDA và một đường dẫn venv. Thêm tự chọn thiết bị: có CUDA thì giữ như cũ, không có thì dùng faster-whisper CPU `int8`. Đầu ra `transcripts.json` giữ đúng định dạng. Không hard-code đường dẫn máy.
3. **Ảnh thiếu:** `build_long.py html` phải dừng với thông báo rõ (chương, cảnh, khóa ảnh) khi một cảnh tham chiếu `img`/`bg`/`a.img`/`b.img`/`pins[].img` không có trong `spec.imgs`. Lần trước lỗi này chỉ lộ khi render: ch13 đứng hình 185 s.
4. **Font lint:** `motion/long/fonts/*.ttf` bị gitignore. `lint_html.py` thiếu font thì báo một dòng hướng dẫn rõ, không traceback. Thêm script tải font từ google/fonts nếu đơn giản.

## Tiêu chí đạt
- Mỗi mục có test trong `tests/test_long_tools_190.py`, gồm ca chặn và ca cho qua.
- `python -m pytest -q tests` của creator_v2: không thêm lỗi mới so với trước (ghi số trước và sau).
- Chạy `python motion/long/build_long.py bao-thanh-thien html` KHÔNG ĐƯỢC (topic đang render ở nơi khác). Chỉ test bằng fixture.

## Báo cáo
Ghi `docs/pm/tickets/GH-190-report.md`: file đã đổi, lý do, kết quả test trước và sau, điểm còn nghi ngờ.

## Quyền cho ticket code (Lead cấp, 06/11)
Đây là ticket **code**, không phải ticket sản xuất video. Theo `CLAUDE.md` mục "Chọn agent" (code, spec và test giao Codex), Lead cho phép **riêng ticket này** ghi đúng các file nêu trong "Phạm vi", kể cả `factory/*`, `tests/*` và `motion/long/build_long.py`. Mọi điều cấm khác của `AGENTS.md` vẫn giữ: không upload, không commit hay đụng git, không ghi `state.sqlite`, không đọc credentials, không render.
Được chạy `python -m pytest -q tests`: các test liên quan đăng bài đều dùng mock, không gọi YouTube.

## Lượt 2 (06/11)
Lượt 1 đã sửa `scene_params.py`, `stt_takes.py`, `lint_html.py` (giữ nguyên các sửa đổi đó trong cây làm việc, xem `GH-190-report.run1.md`). Việc còn lại:
- mục 3: kiểm ảnh thiếu trong `build_long.py html`;
- `tests/test_long_tools_190.py` cho cả 4 mục;
- cập nhật `tests/test_scene_params.py::test_duration_bounds_and_image_usage_are_blocking_without_exceptions` theo hợp đồng A7 mới (endcard ≤ 25 s);
- chạy lại pytest. Nếu bị `PermissionError` ở thư mục tạm pytest thì dùng `--basetemp` trỏ vào thư mục trong worktree (ví dụ `.pytest_tmp`).
Ghi báo cáo mới vào `docs/pm/tickets/GH-190-report.md`.
