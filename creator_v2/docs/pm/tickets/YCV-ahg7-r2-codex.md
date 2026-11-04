# YCV-ahg7 vòng 2 · Sửa `scene_rules.py` theo đúng engine Long (Codex)

Báo cáo vòng 1 (`docs/pm/tickets/YCV-ahg7-report.md`) so nhầm file engine. Long bên này không được dựng bằng `motion/hf/compositions/longform.js` hay `engine.js`. Long dựng bằng `motion/hf/assets/engine/casewide.js`, kèm `lab.js` và `chart.js`; `motion/long/build_long.py` nạp file `casewide.css`.

Trong `casewide.js`:

- **`B.photo`:**
  - `move` mặc định là `"in"` (scale 1 → 1,12); có thêm `"out"` và `"pan"`.
  - `reveal {kind: "wipe"|"circle", at, d}` và `zoom {x, y, z, at, d}` là thẻ thư viện FS/BUD, đã port từ 27/10.
  - `circles` dùng để khoanh chi tiết.
- **`B.print`:** hiện vào trong 0,5 giây, sau đó phóng chậm lên 1,04.

Vậy không có ảnh nào đứng yên hoàn toàn. Luật "ảnh thiếu `move`/`zoom` thì đề xuất preset" là sai tiền đề.

## Việc

1. Viết lại mục "So engine" trong báo cáo, so với `casewide.js`. Ghi rõ phần nào của `motion_picker` đã có sẵn: `slow_zoom` tương ứng `move` in/out, `pan_focus` tương ứng `pan`, `push_detail` tương ứng `zoom`, `reveal` tương ứng `reveal`, `highlight` tương ứng `circles`. Phần nào chưa có thì ghi là chưa có, ví dụ parallax.
2. Sửa `motion/long/scene_rules.py`:
   - **Bỏ** luật "thiếu `move`/`zoom`". Thay bằng hai luật:
     - hai ảnh liền nhau cùng hiệu ứng thực tế (tính cả giá trị mặc định `in`) thì đề xuất đổi hiệu ứng;
     - `print` dài quá 8 giây thì chỉ trôi rất nhẹ, nên đề xuất thêm `circles` hoặc chia shot.
   - Với ảnh dài quá 8 giây:
     - ưu tiên đề xuất `zoom`, với mốc `at` là đầu câu giữa cảnh, hoặc `reveal`, nếu engine đã hỗ trợ;
     - chỉ đề xuất chia shot khi ảnh dài quá 12 giây.
   - Mọi đề xuất phải dùng tên trường mà `casewide.js` đọc được, để người dựng chép thẳng vào spec.
3. Cập nhật test và chạy lại `--all`. Cập nhật bảng top 10 trong báo cáo.

## Giới hạn

Giữ nguyên các giới hạn của vòng 1 (`docs/pm/tickets/YCV-ahg7-codex.md`):
- chỉ ghi `motion/long/scene_rules.py`, `tests/test_long_scene_rules.py`, `output/long/*/scene_rules.json` và báo cáo;
- không render, không commit, không sửa `data/long`, không sửa engine.

Một agent khác đang viết `motion/long/coverage_lint.py` và `motion/long/ai_prompt.py`: không đụng vào hai file đó.

## Báo cáo

Ghi đè `docs/pm/tickets/YCV-ahg7-report.md`. Thêm ở đầu file một mục "Vòng 2: đã sửa gì".
