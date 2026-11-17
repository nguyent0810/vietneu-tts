# GH-471 — báo cáo

## Thực hiện

- Long: `script_lines.gate` kiểm `CAU_TRON` theo `youtube.publish_at` mốc 18/11/2026 (thiếu ngày hoặc cũ hơn: cảnh báo); `MARKUP_LEAK` chặn URL, JSON key, dấu ngoặc nhọn, PAUSE và markup trong lời cuối. Parser gỡ nhãn hợp lệ trước khi kiểm. `script_lines.py` đọc spec khi chạy CLI.
- Nối spec vào cổng integrity của `build_long.py` trước `takes`, `tts` và `html`; vẫn giữ cờ cho câu lặp cố ý. Dùng logic tương đương bản HBR, không phụ thuộc import từ repo cha.
- Short: ear check hiện có chặn dấu phẩy từ 29/11, ngày cũ cảnh báo; thiếu ngày vẫn chặn. Không đổi kiểm rào nguồn cũ cho bài trước mốc.
- Thêm `tests/test_gh471_audio_gates.py` cho câu trọn, nhãn sau parser, markup và mốc ngày.

## Kiểm tra

- `python -m pytest -q tests/test_gh471_audio_gates.py tests/test_late_first.py::test_script_gate_never_lets_markup_through`: **12 passed, 1 warning** (pytest không ghi được cache).
- `python -m pytest -q tests`: dòng cuối sau thay đổi cuối: **1 failed, 891 passed, 15 skipped, 67 warnings, 457 errors in 65.97s (0:01:05)**. Không đạt cổng toàn bộ. Lỗi setup quan sát được: `PermissionError [WinError 5]` khi pytest truy cập `C:/Users/Tung-QA/AppData/Local/Temp/pytest-of-Tung-QA`; cache cũng bị từ chối. Lần chạy tập trung xác định test thất bại `tests/test_stier_ear.py::test_comma_all_and_date_boundary` vẫn đòi Short cũ trả `([], [])`, trái yêu cầu mới phải cảnh báo. Brief chỉ cho ghi test mới, nên không sửa test cũ; Lead cần cập nhật kỳ vọng và chạy lại trong môi trường có quyền temp.
- `python -c` đọc spec và các chapter JSON, gọi `script_lines.gate` không ghi dữ liệu: `cl-sarin-tokyo-1995`: 11 cảnh báo tổng, 0 `CAU_TRON`, 0 lỗi, 0 `MARKUP_LEAK`; `cl-dich-nhan-kiet`: 0 cảnh báo, 0 lỗi, 0 `MARKUP_LEAK`. Các cảnh báo khác là kiểm mạch sẵn có.
- Không có khẳng định nội dung cần kiểm nguồn; ticket là thay đổi code. Không áp dụng clip sheet và thumbnail. Không render hoặc chạy TTS.
