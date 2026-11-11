# GH-276 — báo cáo Codex

## Tình trạng

Đã triển khai bộ chọn, cổng mật độ, 20 kiểu Long, sáu kiểu Short, bộ sinh composition mẫu và tài liệu. **Chưa thể xác nhận ticket đạt đầy đủ**: chưa render hoặc kiểm tra hình theo brief; dữ liệu Mata Hari hiện có chín cặp thẻ vi phạm khoảng cách; toàn bộ test repo chưa cho được tổng kết do lỗi quyền thư mục tạm. Lead cần kiểm tra hình và chạy lại test ngoài sandbox trước khi duyệt.

## Đã làm

- `motion/long/idcards.py`: chọn tất định theo topic và thứ tự cảnh, lọc kênh, năm và gợi ý; giữ kiểu ghi tay; kiểm tra giới hạn và báo lỗi thay vì tự xóa cảnh. Ba kiểu nhạy cảm chỉ được chọn khi khai `convicted: true` và URL nguồn kết án; URL cần biên tập viên tự mở và xác minh.
- Tích hợp vào `build_long.py` khi `idcards` bật, in phân bố, chuyển kết quả đến cổng `floor.py`; bổ sung khóa cho `scene_params.py`. Spec cũ không bật khóa không được tự gán kiểu.
- Long: `clip_file`, `lower_third`, `callout`, `news_clip`, `telegram`, `polaroid`, `index_card`, `fingerprint`, `passport`, `verdict`, `wanted`, `envelope`, `edict_scroll`, `seal_slip`, `museum_label`, `case_divider`, `terminal`, `spec_sheet`, `receipt`, `app_card`. Sáu kiểu giấy tờ theo issue có nhãn “ĐỒ HỌA”; các kiểu dùng CSS và timeline GSAP, các dòng theo mốc `at`.
- Short: thêm `lower_third`, `callout`, `news_clip`, `polaroid`, `edict_scroll`, `receipt` khi khai `style`.
- `idcards_demo.py` sinh một composition 100 giây với 20 kiểu và dữ liệu giả lập; đã kiểm tra cấu trúc tạo ra trong bộ nhớ, chưa ghi composition ra đĩa hoặc render. Cập nhật README và thêm `tests/test_idcards.py`.

## Bản sao Mata Hari

Chỉ đọc dữ liệu thật; gán kiểu trên bản sao trong bộ nhớ. Không khai năm vì spec nguồn không có `era`; các kiểu phụ thuộc thời kỳ không được tự đoán.

| Kiểu | Số cảnh |
|---|---:|
| callout | 4 |
| case_divider | 4 |
| clip_file | 3 |
| envelope | 4 |
| index_card | 4 |
| lower_third | 4 |
| museum_label | 4 |
| polaroid | 4 |

Tổng 31/309 cảnh = 10,03%; lớn nhất 4/309 = 1,29%, có tám kiểu, không lặp trong sáu thẻ trước. **Khoảng cách chưa đạt:** các cặp sau dùng số thứ tự cảnh toàn phim bắt đầu từ 1: 5–9, 66–67, 114–117, 155–159, 181–185, 185–186, 186–190, 200–202, 274–278. Cổng báo đúng các cặp này; đổi kiểu không thể tạo thêm bốn cảnh đệm. Cần Lead biên tập lại cấu trúc hoặc quyết định yêu cầu khoảng cách cho dữ liệu đó.

Bảng issue chỉ cho CK bốn kiểu phù hợp; vì vậy nếu có từ năm thẻ CK liên tiếp trong chuỗi thẻ, không thể vừa giới hạn bốn kiểu vừa không lặp trong sáu thẻ trước. Bộ chọn giữ phạm vi kênh và cổng báo vi phạm; cần Lead quyết định mở rộng danh sách hay giảm số thẻ.

## Kiểm tra

- `python -m pytest tests/test_idcards.py tests/test_long_floor.py tests/test_floor.py -q --basetemp=tmp_pytest -p no:cacheprovider` bằng Python trong brief: **24 passed**. Bao gồm kiểm tra tính tất định, giữ kiểu tay, nguồn kết án, mật độ, bản sao Mata Hari, legacy và chạy engine Long giả lập với từng kiểu thiếu trường tùy chọn.
- `node --check motion/hf/assets/engine/casewide.js` và `node --check motion/hf/assets/engine/casefile.js`: qua.
- `python -W error -m py_compile` cho các file Python đã sửa và test mới: qua.
- Kiểm tra bộ sinh demo trong bộ nhớ: 20 kiểu khác nhau, 100 giây, chuỗi tiếng Việt UTF-8 được giữ. Đã kiểm tra nhãn “ĐỒ HỌA” trong cả hai engine sau khi sửa lỗi dấu do PowerShell.
- Đã chạy `python -m pytest tests -q --basetemp=tmp_pytest -p no:cacheprovider`: chạy tới 100% với cả lỗi E và F nhưng không xuất tổng kết do `PermissionError: [WinError 5]` khi pytest truy cập/dọn `tmp_pytest`. Thử lại dừng ở lỗi đầu với `tmp_pytest_276` vẫn gặp lỗi quyền khi kết thúc. Không thể quy toàn bộ các lỗi quan sát được cho `vnlunar`; Lead cần chạy lại toàn bộ và phân loại lỗi.
- Chưa chạy kiểm hình, render, HyperFrames lint/check hoặc kiểm tra hình trong trình duyệt theo ràng buộc brief. Cần Lead soi cả 20 kiểu, dấu, tràn chữ, chuyển động và các mốc lời; kiểm thử DOM giả lập không chứng minh chất lượng hình hay chuyển động thực.

## Lệnh Lead tạo và render mẫu

Chạy từ `creator_v2`; lệnh sau do Lead chạy, không chạy trong phiên Codex:

```powershell
& "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe" motion/long/idcards_demo.py
Push-Location motion/hf
npx.cmd -y -p node@22 -p hyperframes@0.8.75 hyperframes render . -c compositions/long/idcards_demo.html -o idcards_demo.mp4 --fps 30 -q draft
0..19 | ForEach-Object { ffmpeg -ss ($_ * 5 + 3) -i idcards_demo.mp4 -frames:v 1 ("idcards_{0:00}.png" -f ($_ + 1)) }
Pop-Location
```

Cần `ffmpeg` trong PATH. Khung ở các giây 3, 8, …, 98 tương ứng thứ tự 20 kiểu nêu trên. Kiểm thêm các khung vào/ra và mốc dòng; một ảnh tĩnh cho mỗi kiểu không kiểm được chuyển động.

Không có clip sheet hoặc thumbnail: ticket yêu cầu không render. Không đăng, không commit, không thay đổi lịch; không có khẳng định lịch sử nào được bổ sung vào demo.
