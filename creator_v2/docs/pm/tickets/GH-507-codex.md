# GH-507 — factcheck_lint chạy từ bước html/render (Codex)

Issue: #507. Làm việc trong worktree do Lead tạo (đường dẫn hiện tại). Không commit, không push, không render video, không đăng.

## Bối cảnh
`motion/long/factcheck_lint.py` (`lint(topic) -> list[str]`) hiện chỉ được gọi trong `motion/long/publish_long.py` (~dòng 152). Vidocq bị chặn lúc đăng sau 2 giờ render.

## Sửa (chỉ các file này)
- `motion/long/build_long.py`:
  - `do_html(...)` (~dòng 1112): sau khi sinh html xong, gọi `factcheck_lint.lint(topic)`; mỗi lỗi in `  ! factcheck: <lỗi>`. Không chặn.
  - `cmd_render(topic, only, rest)` (~dòng 1613): khi KHÔNG có `--draft` trong `rest` và KHÔNG có `--allow-factcheck`, có lỗi factcheck thì `raise SystemExit` với danh sách lỗi và gợi ý "thêm nguồn vào data/long/<topic>/factcheck.md hoặc chạy với --allow-factcheck".
  - `do_final(...)` (~dòng 1680) và nhánh `final` trong `__main__`: chặn tương tự, cờ `--allow-factcheck` qua `rest`.
  - Import theo cách các module cạnh đó đang import (`motion/long` đã trong sys.path).
- Test mới `tests/test_build_long_factcheck_gate.py`: dùng monkeypatch `factcheck_lint.lint` trả 1 lỗi → `cmd_render` không `--draft` ném SystemExit; có `--draft` hoặc `--allow-factcheck` thì không ném vì cổng (mock phần render thật để không chạy render). Xem `tests/test_factcheck_lint*.py` làm mẫu.

## Kiểm
- `python -m pytest -q tests/test_build_long_factcheck_gate.py tests/test_factcheck_lint.py tests/test_factcheck_lint_label.py` xanh.
- `python -c "import sys; sys.path[:0]=['motion/long','motion','.']; import factcheck_lint; print(factcheck_lint.lint('cl-vidocq-javert'))"` in `[]`.

## Báo cáo
`docs/pm/tickets/GH-507-codex-report.md`: diff tóm tắt, lệnh test + kết quả nguyên văn dòng cuối.
