# Báo cáo GH-274, GH-275 và GH-280

## Trạng thái

Đã triển khai các thay đổi và kiểm thử dưới đây, **chưa đủ điều kiện kết luận hoàn tất**: tiêu chí ít nhất ba kiểu máy quay trong mọi cửa sổ hai phút chưa đạt trên Mata Hari; chưa chạy `html` thật trên bản sao để so byte đầu ra legacy; chưa kiểm tra hình hoặc nghe duyệt chương. Không render, không đăng, không commit, không đổi lịch.

## Thay đổi theo file

- `motion/hf/assets/engine/casewide.js`: thêm chuyển động GSAP cho ảnh trong `print`, `split`, ảnh đóng khung và nền ảnh cảnh chữ; thêm hiệu ứng cho `print` và `split`; B-roll chỉ nhận push/pull khi khai, mức phóng tối đa 1,06.
- `motion/long/scene_params.py`: cho phép và kiểm các trường tương ứng, giới hạn camera B-roll và cảnh chữ.
- `motion/long/cine_auto.py`: chọn camera tất định, hiệu ứng theo ngữ cảnh, chuyển cảnh, xử lý ảnh rộng có điểm neo và thống kê phân bố; giữ các trường tác giả đã khai.
- `motion/long/build_long.py`: áp mặc định trong bộ nhớ theo danh sách legacy; gọi director ở `html`; kiểm opening Long mới; tham số hóa mức trộn theo kênh, nhả sidechain ở thẻ chương, lưu và đo hai stem sau mix, chặn `final` nếu thiếu số đo hợp lệ hoặc nhạc nhỏ hơn giọng quá 18 dB. Ambience Long mới tăng 15 dB. Topic cũ giữ mức gốc.
- `motion/long/floor.py`: cảnh báo dưới 50% ảnh có camera, không chặn.
- `motion/long/README.md`: bảng mặc định, cách dùng và giải thích cổng âm thanh.
- `data/long/_legacy_topics.json`: danh sách mọi thư mục hiện có trong `data/long/` của bản sản xuất lúc kiểm tra, kể cả thư mục bắt đầu bằng dấu gạch dưới.
- `tests/test_cine_auto.py`, `tests/test_long_defaults.py`: 11 test mới về phân bố, giữ khai báo, pano, nền cảnh chữ, B-roll, mặc định, opening, mức âm và nhánh `html` legacy mô phỏng.
- Không sửa `casewide.css` hoặc `cadence.py`.

## Mata Hari: thử khô trên bản sao

Đã chép JSON của topic và `data.js` đã plan từ output sản xuất sang `tmp_dry/mata-hari/`, bật `cine_auto` trên bản sao và chạy director trực tiếp trong bộ nhớ. Đây là phép thử trên cảnh đã plan, **không phải chạy lại toàn bộ lệnh `html`**; ảnh và khung hình chưa được render. Bảng chi tiết lưu tại `tmp_dry/mata-hari/cine_report.json`.

| Chỉ số | Trước | Sau |
| --- | ---: | ---: |
| Ảnh photo/print/split/pano | 57 | 57 |
| Ảnh có cam | 0/57 (0%) | 38/57 (66,7%) |
| push_in / pan / pull_out / tilt_up / dolly | 0 / 0 / 0 / 0 / 0 | 5 / 10 / 9 / 7 / 7 |
| Ảnh có fx | 0% | 14,0% |
| Pano trên tổng số cảnh | 0% | 0% |
| Chuỗi cam ảnh trùng dài nhất | 0 | 1 |
| Cặp cam trùng liền nhau, tính cả nền cảnh chữ | 0 | 0 |

Kiểm 161 cửa sổ dài 120 giây, điểm đầu cách nhau 10 giây: **16 cửa sổ có dưới ba kiểu camera**, dù tính cả camera nền cảnh chữ. Đây là bằng chứng không đạt, không phải phép chứng minh cho mọi điểm đầu liên tục. Một số khoảng có ít ảnh, trong khi nền ba loại cảnh chữ chỉ được phép dùng push hoặc pan; cần Lead quyết định cách xử lý nhịp và cảnh phù hợp trước khi nhận. `scene_params.validate_topic` trên cảnh sau gán: 0 lỗi. Không có ảnh thỏa điều kiện chuyển pano trong phép thử này.

Test `test_legacy_html_does_not_add_cine_fields` gọi `do_html` với các thành phần IO, lập kế hoạch và trộn được mô phỏng, kiểm tra cảnh nguồn và cảnh xuất ra giữ nguyên khi thiếu `cine_auto`. Test này **không chứng minh byte HTML/data.js thật trên Mata Hari không đổi**; cần chạy so sánh trên bản sao đầy đủ ngoài sandbox.

## Âm thanh

Đã chạy `mix_chapter` với WAV tổng hợp 6 giây qua FFmpeg, không render video. RMS nhạc đo ở thẻ chương 0,02975; lúc có giọng 0,01118; khoảng lặng 0,02975; cảnh hỏi 0,00134. Cổng đo stem trả nhạc thấp hơn giọng 18,046 dB và sẽ chặn mẫu này; đây chỉ là kiểm tra cơ chế, không đại diện mức thực tế của Mata Hari. Cần Lead nghe thử nguồn thật và đánh giá mức cũng như cổng sau mastering. Khi Long có nhạc mà số đo thiếu hoặc không khớp hash của `mix.wav`, `final` bị chặn và yêu cầu chạy lại mix.

## Kiểm thử

Lệnh Python dùng bản `.venv` trong `vietneu-main` như brief, với `PYTHONIOENCODING=utf-8`.

- Trước sửa: `python -m pytest tests -q --basetemp=tmp_pytest -p no:cacheprovider`: **714 passed, 7 failed, 20 skipped, 419 errors**.
- Sau sửa: `python -m pytest tests -q --basetemp=tmp_pytest -p no:cacheprovider --tb=no --no-header`: **725 passed, 7 failed, 20 skipped, 419 errors**.
- Test mới: `python -m pytest tests/test_cine_auto.py tests/test_long_defaults.py -q --basetemp=tmp_pytest -p no:cacheprovider`: **11 passed**.
- Test liên quan: `python -m pytest tests -q -k "cine or long_defaults or mix_level or long" --basetemp=tmp_pytest -p no:cacheprovider --tb=no --no-header`: **103 passed, 995 deselected, 73 errors**.
- 419 lỗi setup của bộ toàn bộ và 73 lỗi của tập liên quan là lỗi quyền `PermissionError: [WinError 5]` khi pytest thao tác thư mục tạm. Thử thư mục tạm mới trong `tmp_dry` cũng bị từ chối quyền dọn hoặc đọc. Lead cần chạy lại ngoài sandbox.
- Bảy test thất bại có sẵn theo brief: năm test trong `tests/test_claims.py` (`test_wrong_month_statistic_is_caught`, `test_correct_month_statistic_passes`, `test_statistic_about_another_month_is_rejected`, `test_god_count_statistic_is_verified`, `test_statistics_are_recounted_not_trusted`), `tests/test_lines.py::test_lich_countdown_is_real` và `tests/test_pillars.py::test_daily_kind_takes_over_when_fixed_topics_run_out`; thiếu `vnlunar`.
- `python -m py_compile` cho các module Python đã sửa và `node --check motion/hf/assets/engine/casewide.js`: đạt. Chưa chạy lint HTML trên đầu ra mới vì không dựng HTML thật.

## Việc Lead cần làm

1. Quyết định cách đạt ba kiểu trong các đoạn ít ảnh và rà lại việc chạy `html` theo từng chương: director đang giữ trạng thái trong một lượt chạy, nên chọn riêng một chương có thể cho phân bố khác chạy toàn bộ.
2. Trên bản sao đầy đủ, so đầu ra `html` của Mata Hari không bật cờ với đầu ra cũ; sau đó bật `cine_auto`, dựng HTML và kiểm cảnh thực tế. Các file trong `tmp_dry/mata-hari` chỉ là dữ liệu thử khô, chưa phải topic dựng đầy đủ.
3. Sau khi chuẩn bị một bản sao có đủ spec, timing và asset ở cây `data/long` và `output/long` của môi trường thử, Lead có thể chạy ví dụ sau với `<topic-ban-sao>` thay bằng tên bản sao:

```powershell
python motion/long/build_long.py <topic-ban-sao> html ch03 --allow-opening
python motion/long/build_long.py <topic-ban-sao> render ch03 --draft --allow-opening
```

Soi contact sheet và nghe âm thanh chương 3; lệnh `--allow-opening` chỉ dành cho bản thử có chủ ý bỏ qua kiểm tra mở bài. Chưa có đường dẫn clip sheet hay thumbnail mới vì ticket cấm render.
