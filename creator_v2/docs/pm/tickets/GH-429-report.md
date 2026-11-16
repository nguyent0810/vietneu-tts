# GH-429 — báo cáo

Đã thêm O9, O10, O11 vào `motion/long/opening_gate.py` cùng đường cảnh báo O7/O8; không thêm lỗi chặn. O9 nhận video, photo/pano có move, cam hoặc cine, hoặc pano có các điểm dừng khác vị trí; tone đơn thuần không chứng minh chuyển động. O10 báo từng loại thẻ và giây bắt đầu trước 10s, bao gồm chapter. O11 dùng đúng ba dòng đầu của chapter, theo bộ dấu hiệu O7. Các mốc cảnh lấy từ plan với timing thật nếu có, nếu không thì ước lượng như cũ. Đã thêm test `tests/test_gh429_opening_visual.py` và một dòng tham chiếu trong guide.

## Kiểm thử

- `python -m pytest -q tests/test_gh429_opening_visual.py tests/test_gh411_shock_window.py tests/test_opening_gate.py tests/test_console.py`: lượt đầu 54 qua, 8 lỗi setup do Windows từ chối truy cập thư mục tạm pytest. Thử basetemp trong workspace vẫn bị từ chối.
- Chạy lại cùng bốn file bằng pytest với wrapper tạm đổi mode tạo thư mục của pathlib từ 0700 sang 0777: 60 qua, 2 thất bại. Hai case của `tests/test_console.py::test_qa_blank_cli_prints_vietnamese_on_cp1252_console` không chạy xong do tiến trình con `qa_blank.py` tạo thư mục tạm 0700 và ffmpeg bị Permission denied khi ghi frame. Đây là giới hạn môi trường, chưa xác nhận hai case console xanh.
- Sau chỉnh sửa cuối, chạy lại ba file test mở đầu với cùng wrapper: **56 passed**, 53 cảnh báo, exit 0. Wrapper: `python -c "import pathlib,pytest; original=pathlib.Path.mkdir; pathlib.Path.mkdir=lambda self,mode=511,parents=False,exist_ok=False: original(self,mode=511,parents=parents,exist_ok=exist_ok); raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','--basetemp=.gh429_pytest_run4','tests/test_gh429_opening_visual.py','tests/test_gh411_shock_window.py','tests/test_opening_gate.py','--disable-warnings']))"`.
- `rg -n -F '??' motion/long/opening_gate.py tests/test_gh429_opening_visual.py docs/pm/storytelling-guide.md`: không có kết quả. Không chạy toàn bộ test theo brief.
- Các thư mục tạm pytest sinh trong workspace và thư mục tạm hệ thống có thể còn tồn tại vì luật repo cấm xóa ngoài phạm vi topic.

## Chạy thử topic

Lệnh mỗi topic: `python motion/long/opening_gate.py <topic> --out-root "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\output\long"`. Cả ba có timing ch00 thật, không có voice.wav; nội suy từ trong từng câu theo timing.

- `cl-dich-nhan-kiet`: exit 0, OK; cảnh báo O9, O10 kinetic 9.52s, O11; thêm cảnh báo cũ từ khóa tiêu đề.
- `mim-binance-6-3-ty-20-phut`: exit 1 do lỗi cũ từ khóa tiêu đề “6,3 tỷ” chưa nói trước 20s; cảnh báo O10 counter 4.56s và O11.
- `ck-c8-10-trieu-mua-duoc-gi`: exit 0, OK; không có cảnh báo O9–O11.

Không có khẳng định nội dung mới cần kiểm nguồn. Không render video sản xuất, không đăng, không commit, không đổi lịch. Các cảnh báo là heuristic, người duyệt vẫn cần xem nội dung thực tế. Việc giao chưa đạt đủ cổng kiểm vì hai test console bị lỗi quyền thư mục tạm; Lead cần chạy lại trong môi trường có quyền phù hợp và chạy toàn bộ test.
