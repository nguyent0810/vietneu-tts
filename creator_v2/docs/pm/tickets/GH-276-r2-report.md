# GH-276 vòng 2 — báo cáo Codex

## Tình trạng

Đã triển khai đủ tám bố cục và chuyển động vòng 2; đã tạo composition demo và chạy các kiểm tra được yêu cầu. Chưa xác nhận chất lượng hình thực tế: brief giao Lead render và xem. Không render, không đăng, không commit, không đổi lịch.

## Tám kiểu

- `lower_third`: ảnh tràn màn hình với cam; dải tên và vai trò góc dưới trái, vạch nhấn quét ngang, sau đó chữ trượt lên qua mặt nạ.
- `callout`: ảnh tràn khung, SVG vòng khoanh tại `focus` trong tọa độ ảnh gốc và đường gấp khúc nối với nhãn; vòng vẽ trước, đường vẽ tiếp, nhãn hiện sau. Ảnh và SVG cùng theo cam.
- `news_clip`: mẩu giấy mép răng cưa, măng-sét chung TIN TỨC và năm khi có `date`, tít lớn, hai cột dòng, ảnh nhỏ đen trắng nếu có. Mẩu báo rơi xoay rồi phóng chậm.
- `telegram`: nền giấy, băng điện tín xiên, tem ĐIỆN TÍN; chữ máy đánh chữ in hoa và STOP, các dòng được mở theo từng ký tự tại `at`, băng trượt vào.
- `polaroid`: ảnh chiếm phần lớn khung, chân trắng dày và chú thích font viết tay; khung rơi xoay, ảnh chuyển từ xám sang màu.
- `edict_scroll`: tờ cuộn ở giữa hai trục gỗ, nội dung và ấn son vuông; giấy mở ngang cùng hai trục, ấn dập xuống và rung.
- `receipt`: hóa đơn hẹp mono, chân răng cưa, hai cột tên và giá trị căn phải; dòng có nhãn TỔNG hoặc `total: true` được gạch đôi. Giấy xuất từ trên xuống và từng dòng hiện tại `at`.
- `museum_label`: ảnh hiện vật chiếm hai phần ba khung bên trái; nhãn nền trắng ngà bên phải chứa tên, ngày, mô tả/chất liệu và dòng bổ sung. Ảnh hiện trước, nhãn trượt vào sau.

Tiêu đề serif dùng line-height 1.25 và chừa khoảng trên cho dấu; chỉ báo và điện tín có nhãn ĐỒ HỌA. Đã khai Comic Sans MS và Courier New trong `KIN_FONTS`, dùng các font Windows hiện có; máy render khác cần có các font này. Chưa kiểm tra hình thực tế hoặc khả năng dự phòng font trên máy khác.

Bộ chọn chỉ chọn `lower_third`, `callout`, `polaroid`, `museum_label` khi chính cảnh có `img`; cổng cũng báo kiểu khai tay thiếu ảnh. Không tự bổ sung ảnh hay đoán năm. Không thay ngưỡng cổng.

## Dữ liệu Mata Hari — lưu ý cho Lead

Thử chỉ đọc trên bản sao trong bộ nhớ, không khai năm: chỉ 1/31 cảnh thẻ có `img`. Phân bố: envelope 7, case_divider 8, index_card 7, clip_file 8, callout 1. Cổng báo 22 lần lặp trong sáu thẻ và 9 cặp thiếu khoảng cách. Đây là hệ quả của điều kiện ảnh mới cộng bộ lọc thời kỳ; không thể vừa giữ lựa chọn hợp lệ vừa đạt tám kiểu và không lặp với dữ liệu hiện tại. Test Mata Hari được cập nhật để kiểm cổng báo đúng thay vì giữ kỳ vọng cũ không còn khả thi; test tổng hợp có ảnh và năm vẫn kiểm tính tất định, ít nhất tám kiểu, mật độ và không lặp. Cần Lead quyết định bổ sung ảnh hợp lệ vào cảnh hoặc điều chỉnh dữ liệu/biên tập trước khi dùng bộ chọn cho bài này.

## Kiểm tra

- `node --check motion/hf/assets/engine/casewide.js`: đạt.
- `python -m pytest tests/test_idcards.py tests/test_long_floor.py --basetemp=tmp_pytest -p no:cacheprovider`: 18 passed, dùng Python của brief.
- Kiểm tự động cấu trúc DOM tám kiểu, tọa độ vòng khoanh, mốc dòng, ảnh, nhãn, dòng tổng, điều kiện ảnh, line-height CSS và đăng ký font; không thay thế việc xem render.
- `python motion/long/idcards_demo.py`: tạo `motion/hf/compositions/long/idcards_demo.html`, 20 kiểu, mỗi kiểu 6 giây; tám kiểu vòng 2 đứng đầu. Hai ảnh tư liệu có sẵn `mh_hat.jpg`, `vin_gate.jpg` được nhúng vào demo, không tải ảnh mới. Demo dùng dữ liệu giả lập, không bổ sung khẳng định lịch sử cần kiểm nguồn.
- Không chạy render, HyperFrames lint/check hay kiểm hình theo yêu cầu brief. Không có clip sheet hoặc thumbnail cho ticket code này.

## Lệnh Lead render và soi

Chạy từ `creator_v2`; các lệnh render dưới đây chưa được Codex chạy:

```powershell
& "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe" motion/long/idcards_demo.py
Push-Location motion/hf
npx.cmd -y -p node@22 -p hyperframes@0.8.75 hyperframes render . -c compositions/long/idcards_demo.html -o idcards_demo.mp4 --fps 30 -q draft
0..19 | ForEach-Object { ffmpeg -ss ($_ * 6 + 3) -i idcards_demo.mp4 -frames:v 1 ("idcards_{0:00}.png" -f ($_ + 1)) }
Pop-Location
```

Kiểm thêm chuyển động đầu cảnh, từng mốc dòng, dấu tiếng Việt, vị trí focus, ảnh, chiều dài chữ và font. Các khung giữa cảnh không chứng minh chuyển động hay mọi trường hợp tràn chữ.
