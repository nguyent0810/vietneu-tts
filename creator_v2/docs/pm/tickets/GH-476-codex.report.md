# GH-476 — Báo cáo

## Kết quả

- Tạo scripts/prose_to_script.py để tách câu, chuyển PD, giữ phần đầu và cuối, chạy parser và gate, in thống kê và lỗi.
- Sửa motion/long/craft.py: cảnh báo trên 45 tiếng, chặn trên 70 tiếng; cập nhật test.
- Tạo scripts/tts_sample.py dùng engine, giọng và voice FX theo kênh; chèn khoảng nghỉ, loudnorm -16 LUFS, ghi riêng tts_test. Test dùng engine giả, không dùng cache sản xuất.
- Tách câu dùng heuristic với viết tắt; Lead cần kiểm bản thực tế. Marker PD nằm giữa câu bị từ chối.
- Không đọc issue trên mạng vì brief cấm gọi mạng; nội dung issue không kiểm chứng độc lập. Không có khẳng định nội dung video cần factcheck.

## Kiểm thử

- python -m py_compile scripts/prose_to_script.py scripts/tts_sample.py: qua.
- python -m pytest -q -p no:cacheprovider tests/test_gh476_prose_tts.py tests/test_scene_marks.py -k 'not nhan_phong_dung_khong_bi_go_khoi_canh_ai': 19 passed, 1 deselected. Test bị loại cần fixture thư mục tạm bị từ chối quyền.
- python -m pytest -q tests: 901 passed, 15 skipped, 67 warnings, 461 errors in 71.91s. Các traceback đã quan sát cho thấy lỗi thiết lập fixture tmp_path với PermissionError/WinError 5; bộ test đầy đủ chưa xanh. Pytest cũng báo không tạo được cache. Chưa kiểm từng traceback nên không khẳng định tất cả 461 lỗi cùng nguyên nhân.
- Lần kiểm thử tập trung đầu phát hiện lỗi mã hóa khi truyền văn bản qua PowerShell; đã sửa và chạy lại như trên.
- Không chạy TTS thật, render, lint video hay gọi mạng theo brief. Không có clip sheet hoặc thumbnail: ticket không sản xuất video.
- Không đăng, không commit, không đổi lịch.

## Cần Lead kiểm

Chạy lại toàn bộ pytest trong môi trường có quyền thư mục tạm; nghe TTS thật và kiểm định dạng script trên văn xuôi thực tế. Chưa thể báo ticket hoàn tất khi cổng pytest đầy đủ còn lỗi.
