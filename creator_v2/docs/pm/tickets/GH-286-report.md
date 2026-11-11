# GH-286 — báo cáo sản xuất

## Đã làm

- Thêm `flow_warnings(chs)` và nối vào `gate()` bằng cảnh báo, không bổ sung lỗi chặn và không đổi dữ liệu ghi vào chNN.json. Chỉ số câu bắt đầu từ 0.
- Thêm `scripts/long_story_review.py`: dùng `script_lines.parse`, lấy nguyên khối text trong prompt cố định, ghép ngữ cảnh và tối đa 12.000 ký tự factcheck; hỗ trợ chọn chương, dry-run, chuyển c → local → grok khi lỗi hoặc rỗng, và ghi agent/model/ngày trong review.
- Bước TTS cảnh báo thiếu review của mọi chương đối với topic mới; topic legacy giữ nguyên. Cập nhật README và bổ sung test cho lint, prompt, chuyển agent và cảnh báo TTS.
- Đã đọc issue #286 và §13 storytelling guide. Không gọi agent thật, không đăng, không commit, không đổi lịch. Ticket code không có khẳng định nội dung mới cần kiểm nguồn; không có clip sheet hoặc thumbnail thuộc phạm vi này.

## Lint dữ liệu thật

Mata Hari CH03, chỉ số câu từ 0:

| Mã | Câu |
|---|---|
| RAO_NGUON | 9–15, 22–30 |
| NHIP_DEU | 3–7 |
| NHAY_MOC | 32 (1919; mốc đầu 1897) |
| META_NGUOI_KE | 10, 14, 24 |

Các cửa sổ nguồn chồng nhau được gom để không báo lặp cùng một đoạn. Trên toàn bộ golden: 14 chương, 9 cảnh báo — RAO_NGUON 0, NHIP_DEU 0, NHAY_MOC 8, META_NGUOI_KE 1 (trung bình 0,64/chương). Không cần đổi ngưỡng vì dưới một cảnh báo mỗi chương trung bình. Đây là cảnh báo gợi ý, cần người đọc đánh giá; tám NHAY_MOC của golden chưa được kết luận là lỗi biên tập.

## Kiểm tra

- `python scripts/long_story_review.py mata-hari ch03 --dry-run`: thành công; file `data/long/mata-hari/story_review/ch03.prompt.md`. Đã kiểm khối prompt nguyên văn, chương, câu kề, lời đọc đánh số, factcheck và ba mục đầu ra.
- `python -m pytest tests/test_flow_lint.py tests/test_long_story_review.py tests/test_long_defaults.py --basetemp=tmp_pytest -p no:cacheprovider`: không hoàn tất; Windows báo `PermissionError: [WinError 5]` khi truy cập/dọn `tmp_pytest`. Lần dùng basetemp mới thông thường cũng gặp cùng lỗi. Không xóa các thư mục đó.
- Chạy lại cùng ba file test bằng `pytest.main`, `-p no:cacheprovider`, basetemp riêng `data/long/mata-hari/story_review/tmp_pytest`, với wrapper chỉ trong tiến trình đổi quyền tạo thư mục 0700 thành 0777: **15 passed**. Wrapper không sửa pytest hay code repo. Test subprocess giả lập c lỗi → local rỗng → grok; cũng kiểm c lỗi → local thành công và chỉ lấy result cuối.
- Không có lỗi lint chặn được tạo bởi thay đổi này; không chạy chuyển script thật thành chNN.json để tránh ghi dữ liệu bài.

## Lệnh Lead chạy review thật

Tại thư mục repo, với máy C và tài khoản agent đã sẵn sàng:

```powershell
& "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe" scripts/long_story_review.py mata-hari ch03 --agent c
```

Kết quả dự kiến: `data/long/mata-hari/story_review/ch03.md`. Nếu máy C lỗi hoặc trả rỗng, script thử local rồi grok. Lead cần đọc review, đối chiếu các chi tiết cần xác minh với factcheck và đánh giá chất lượng bản viết lại; lượt này chưa kiểm chất lượng đầu ra agent thật.
