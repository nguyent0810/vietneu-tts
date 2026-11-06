# GH title max: báo cáo

- Gate nhận diện kênh từ spec hoặc slug và đọc `luat_noi_dung.title_max` qua `channel_profile.resolve/load`. Nếu không đọc được, gate cảnh báo và dùng 60. Lỗi ghi kênh và giới hạn.
- Tiêu đề YouTube rỗng được thay bằng `spec.title`, theo logic của `chosen_title`. Không import hàm đó vì module publish kéo theo nhiều phụ thuộc đăng video.
- CL đổi 60 thành 100; MIM và CK không sửa. Thêm bốn test cho các trường hợp brief yêu cầu.
- `python -m pytest creator_v2/tests -q -k "gate or title"`: lần đầu bị lỗi quyền thư mục tạm pytest (31 passed, 7 skipped, 32 errors). Chạy lại cùng bộ test với wrapper Python khắc phục quyền tạo thư mục trên Windows, `--basetemp` ngoài repo và `-p no:cacheprovider`: **63 passed, 7 skipped, 926 deselected**.
- `tests/test_channel_profile.py`: cùng wrapper và cache tắt: **5 passed**.
- Không chạy lint riêng; không có kiểm chứng nội dung hay clip/thumbnail trong ticket code này. Không commit, không upload.
