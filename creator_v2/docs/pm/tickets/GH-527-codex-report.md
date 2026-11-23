# GH-527 — báo cáo

Đã sửa `do_html` để chặn sớm các chương có cấu hình nhạc mà không có bài, gom lỗi cảnh quá ngắn, lỗi kiểm tra tham số và tốc độ pano qua các chương, và kiểm tra số mốc `groupAt` của cảnh date trước khi dựng âm thanh. Đã thêm ba kiểm thử không render hoặc gọi ffmpeg.

Kiểm thử (tắt pytest cache bằng `PYTEST_ADDOPTS=-p no:cacheprovider` vì quyền cache của môi trường):

- `python -m pytest -q tests/test_build_long_html_gather.py`:
  `3 passed in 1.71s`
- `python -m pytest -q tests -k build_long`:
  `15 passed, 1397 deselected, 1 error in 7.38s`

Bộ kiểm thử rộng chưa xanh: test `test_visual_mix_creator_legacy_matches_build_long` lỗi ở bước tạo `tmp_path`, do Windows báo `PermissionError: [WinError 5] Access is denied` với thư mục tạm pytest. Đã thử chuyển thư mục tạm vào repo và dùng `--basetemp`, vẫn gặp lỗi quyền. Lần chạy đầu của bộ mới cũng gặp lỗi thư mục tạm; sau đó các test mới được chuyển sang mock đường dẫn và chạy xanh.

Không chạy lint riêng; ticket chỉ định hai lệnh pytest. Không có khẳng định nội dung cần kiểm nguồn, clip sheet hoặc thumbnail. Không render, đăng, commit hay đổi lịch.
