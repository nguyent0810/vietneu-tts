# Báo cáo GH-274 đợt 2

## Trạng thái

Đã sửa và kiểm thử một phần, **chưa đủ điều kiện nhận ticket**. Đo thử với thời gian ước lượng trên Mata Hari đạt 0 cửa sổ dưới ba kiểu sau sửa, nhưng chưa chứng minh đạt trên thời gian thật. Bộ pytest toàn repo chưa xanh do lỗi quyền thư mục tạm. Không render, đăng, commit, đổi lịch hay ghi dữ liệu topic thật.

## Thay đổi

- `motion/long/cine_auto.py`: theo dõi các kiểu trong 120 giây gần nhất, ưu tiên camera ảnh khác `push_in` và `pan` (hai kiểu hợp lệ cho nền chữ), tránh lặp camera tự chọn, tính `pano` và video thành kiểu riêng. Thêm bộ đếm cửa sổ đủ 120 giây, bước 10 giây, tính theo khoảng giao của cảnh.
- `motion/long/build_long.py`: khi chọn chương, lập cảnh và chạy director cho các chương trước trong bộ nhớ, không dựng đầu ra hay trộn tiếng các chương bỏ qua. In số cửa sổ dưới ba kiểu trước/sau và cảnh báo nếu còn thiếu. Muốn chạy riêng cần timing và voice của các chương trước.
- `tests/test_cine_windows.py`: kiểm cửa sổ ở ví dụ 4 ảnh và 10 cảnh chữ, camera không lặp, trường khai tay, đếm pano/video và so trường camera/hiệu ứng/chuyển cảnh của ch02 khi dựng riêng và cả ba chương bằng IO mô phỏng.
- `motion/long/README.md`: mô tả cách đếm và điều kiện dựng riêng.

Giới hạn: bộ chọn dùng lịch sử 120 giây, không nhìn trước hoặc tối ưu mọi cửa sổ; cửa sổ chỉ có nền chữ hoặc các lựa chọn bị khóa có thể không đủ kiểu. Camera nền chữ hiện chỉ cho phép `push_in` và `pan`; không sửa engine hoặc validator ngoài phạm vi. Các trường ghi tay được giữ; camera ghi tay liên tiếp giống nhau không thể tự sửa mà vẫn giữ nguyên lựa chọn.

## Đo thử khô trên Long thật

Đọc `data/long/mata-hari/spec.json` và 14 chương, chỉ chạy trong bộ nhớ, không ghi output. Máy không có `output/long/mata-hari` và timing/voice thật. Ước lượng thời gian từ lời đọc ở 2,7 từ/giây cộng khoảng nghỉ, neo cảnh vào đầu câu; không có metadata ảnh nên không mô phỏng chuyển ảnh rộng thành pano. Dùng cùng dữ liệu ước lượng cho director cũ và mới, tính cửa sổ 120 giây cách nhau 10 giây:

| Chỉ số | Director cũ | Director mới |
| --- | ---: | ---: |
| Tổng cửa sổ | 230 | 230 |
| Cửa sổ dưới 3 kiểu | 3 | 0 |

Đây là phép đo gần đúng, không thể so trực tiếp với 16/161 của lượt trước có timing thật; cần chạy lại trên timing thật và xác định cảnh của bất kỳ cửa sổ còn thiếu. Không có clip sheet hoặc thumbnail vì ticket cấm render.

## Kiểm thử

- `python -m pytest tests/test_cine_windows.py tests/test_cine_auto.py tests/test_long_defaults.py::test_legacy_html_does_not_add_cine_fields -q -p no:cacheprovider`: **10 passed**. Test legacy mô phỏng IO; chưa so byte HTML thật trước/sau.
- `PYTHONIOENCODING=utf-8 python -m pytest tests -q --tb=no --disable-warnings -p no:cacheprovider`: **858 passed, 15 skipped, 452 errors**; lỗi thiết lập `tmp_path` do `PermissionError: [WinError 5]` với thư mục tạm pytest trong sandbox. Bộ test toàn repo đã chạy lại sau chỉnh sửa cuối.
- Không chạy lint HTML hay render; không có phát hiện factcheck thuộc phạm vi ticket code.

Cần Lead chạy toàn bộ test ngoài sandbox và kiểm bằng dữ liệu timing thật. Chưa thể khẳng định HTML legacy thật giống byte đầu ra cũ hoặc mọi cửa sổ hai phút đã đạt.
