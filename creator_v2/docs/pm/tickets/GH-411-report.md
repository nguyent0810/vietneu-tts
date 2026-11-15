# Báo cáo GH-411

## Thay đổi

- `motion/long/opening_gate.py`: thêm O7 và O8 là cảnh báo không chặn. O7 dùng dấu hỏi, HOOK_MARK, OPEN_LOOP và PARADOX_MARK của PR #407; chỉ tính câu bắt đầu trước 40 giây. O8 đếm từng cảnh mạnh một lần, chỉ tính cảnh bắt đầu trước 40 giây. Áp dụng cả bài cũ để người duyệt thấy cảnh báo.
- Thêm tham số `--out-root` / `out_root` để đọc timing ngoài worktree. Khi có timing nhưng không có `voice.wav`, dùng mốc câu thật và nội suy thời điểm từng từ trong câu; khi không có timing dùng `estimated_lines` như cũ.
- `motion/stier/build.py`: Short `rules >= 3` được cảnh báo nếu câu đầu trên 9 từ, không chặn vì độ dài này; luật cũ giữ nguyên cho `rules < 3`.
- `tests/test_gh411_shock_window.py`: 8 trường hợp pytest, bao gồm ranh giới 40 giây, mốc thật, tín hiệu móc/nghịch lý, số cảnh mạnh và cảnh báo Short. Đã kiểm bằng Python: không có `??` trong ba file sửa/thêm.

## Kiểm thử

- `python -m pytest -q tests/test_gh411_shock_window.py` khi tạo thư mục tạm bằng quyền 0777: **8 passed**. Dùng `pytest.main` trong Python và điều chỉnh `os.mkdir` trong tiến trình vì sandbox Windows từ chối truy cập thư mục pytest tạo với mode 0700.
- Lệnh yêu cầu `python -m pytest -q tests`: **826 passed, 15 skipped, 445 errors**, do thư mục tạm mặc định bị `PermissionError`.
- Chạy lại toàn bộ bằng `pytest.main(['-q', 'tests', '-p', 'no:cacheprovider', '--basetemp=gh411_pytest_full'])`, điều chỉnh `os.mkdir` thành mode 0777 trong tiến trình: **1260 passed, 15 skipped, 11 failed**, 37 warnings. Còn lỗi tại `test_branch_gate` (thư mục tạm nằm trong worktree), hai `test_console` (tiến trình con không truy cập được temp), hai `test_run_chain`, và sáu `test_stier_render_gates` (npm/cache và render thử trong môi trường bị chặn). Chưa đạt cổng toàn bộ pytest xanh; Lead cần chạy lại trên môi trường đủ quyền và xem chi tiết các lỗi còn lại.
- Sự cố: việc chạy toàn bộ pytest theo brief đã kích hoạt các test có sẵn tự gọi render thử và ffmpeg. Các lệnh render thử HyperFrames thất bại vì npm/cache; không chủ động chạy render sản xuất. Lẽ ra cần kiểm tra tác dụng phụ bộ test trước khi chạy để tuân thủ lệnh không render.

## Bốn Long — chỉ đọc

Lệnh: `python motion/long/opening_gate.py <topic> --out-root "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\output\long"`. Cả bốn tìm thấy timing chương đầu; ba bài sau không có WAV nên nội suy mốc từ trong khoảng câu thật.

| Topic | O7/O8 | Kết quả cổng khác |
| --- | --- | --- |
| `cl-dich-nhan-kiet` | Không in O7/O8 | Exit 0, OK; cảnh báo từ khóa tiêu đề chưa nói trước 20s. |
| `mim-binance-6-3-ty-20-phut` | Không in O7/O8 | Exit 1: từ khóa tiêu đề `6,3 tỷ` chưa nói trước 20s. |
| `ck-c8-10-trieu-mua-duoc-gi` | Không in O7/O8 | Exit 0, OK. |
| `mata-hari` | Không in O7/O8 | Exit 1: từ khóa `MATA HARI` chưa nói trước 15s, thiếu hình/clip 5s đầu, chữ trống 9,7s và O2b 6,9s. |

Các cảnh báo là heuristic, không chứng minh nội dung thực sự có sức hút hay nhịp dựng đạt yêu cầu. Không có khẳng định nội dung mới cần factcheck; không có clip sheet hay thumbnail vì ticket code không yêu cầu sản xuất video. Không đăng, không commit, không đổi lịch.
