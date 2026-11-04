# GH-28 — báo cáo Codex

## Kết quả

- Đã thêm `--slug <slug>` lặp được cho `scripts/unschedule.py`. Khi có slug,
  script chỉ truy vấn các video đó và xác nhận **tất cả** còn `private` với
  `publishAt` ở tương lai trước khi gọi `reschedule` cho bất kỳ video nào.
  Slug thiếu trong store, video đã public/không còn lịch, hoặc video không được
  YouTube trả về đều làm lệnh thoát khác 0, không gỡ một phần danh sách.
- Tách `select_scheduled(rows, videos, now, slugs)` thành hàm thuần; test không
  cần credential, API hay `state.sqlite`. Khi `--slug` có mặt, cột `error` ghi
  đúng lý do: `UNSCHEDULED YYYY-MM-DD: thay bằng Short khác (GH-28)`.
- `motion/stier/upload_one.py` nay nhận `--channel CK`. Nó dùng trực tiếp
  `enqueue_ck.bundle_for`, nên giữ các kiểm tra CK về theme, câu miễn trừ,
  nguồn, credit clip và credit nhạc. `--dry` không mở store và không upload;
  `--wait` chờ luật giãn nhịp của `Channel` cho lần chạy thật.
- Đã thêm `tests/test_unschedule_slug.py` và `tests/test_upload_one_ck.py`.

## Cổng đã chạy

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m pytest -q -p no:cacheprovider tests/test_unschedule_slug.py
# 4 passed in 0.19s

python -m pytest -q -p no:cacheprovider tests/test_unschedule_slug.py tests/test_upload_one_ck.py
# 6 passed in 0.22s

python -m py_compile scripts/unschedule.py motion/stier/upload_one.py
# pass
```

Đã chạy ba preflight CK bằng `upload_one --dry`, không đọc credential, không
gọi YouTube và không ghi `state.sqlite`:

- `ck-b4-tra-gop-them-184-trieu` — đạt, giờ `2026-11-04T05:00:00Z`.
- `ck-b1-muoi-nam-sau` — đạt, giờ `2026-11-05T12:00:00Z`.
- `ck-b4-bay-tram-thanh-tam-tram` — **chặn**: `BundleInvalid`, title dài 104
  ký tự, vượt giới hạn 100 của YouTube.

Không còn lỗi lint nào đã chạy. Không có claim nội dung cần factcheck trong
ticket này. Không tạo clip sheet hoặc thumbnail (không thuộc phạm vi).

## Chuỗi lệnh Lead cần chạy

**Chưa được gỡ ba lịch cũ trước khi sửa và duyệt tiêu đề của
`ck-b4-bay-tram-thanh-tam-tram` xuống tối đa 100 ký tự.** Việc đổi title/spec
không nằm trong phạm vi GH-28 này. Sau khi title đã được duyệt, chạy từng bước
dưới đây từ repo, và chỉ chạy dòng `--wait` ngay sau dry run tương ứng đã đạt.

```powershell
$env:PYTHONIOENCODING='utf-8'

# 1) Preflight cả ba thay thế — không ghi store, không upload
python motion/stier/upload_one.py ck-b4-bay-tram-thanh-tam-tram '2026-11-03 19:00' --channel CK --dry --wait
python motion/stier/upload_one.py ck-b4-tra-gop-them-184-trieu '2026-11-04 12:00' --channel CK --dry --wait
python motion/stier/upload_one.py ck-b1-muoi-nam-sau '2026-11-05 19:00' --channel CK --dry --wait

# 2) Xác nhận chính xác ba lịch cũ, chưa thay đổi gì
python scripts/unschedule.py --channel CK --slug ck-c2-mua-thu-nam-thu-sau --slug ck-c2-mot-lo-bao-nhieu --slug ck-c2-ban-lo-van-nop-thue

# 3) Gỡ thật ba lịch cũ (private, bỏ publishAt; không xoá video)
python scripts/unschedule.py --channel CK --slug ck-c2-mua-thu-nam-thu-sau --slug ck-c2-mot-lo-bao-nhieu --slug ck-c2-ban-lo-van-nop-thue --apply

# 4) Upload từng Short: private + publishAt. --wait tôn trọng nhịp CK.
python motion/stier/upload_one.py ck-b4-bay-tram-thanh-tam-tram '2026-11-03 19:00' --channel CK --wait
python motion/stier/upload_one.py ck-b4-tra-gop-them-184-trieu '2026-11-04 12:00' --channel CK --wait
python motion/stier/upload_one.py ck-b1-muoi-nam-sau '2026-11-05 19:00' --channel CK --wait
```

Các giờ VN trên đổi lần lượt thành `03/11 12:00Z`, `04/11 05:00Z`,
`05/11 12:00Z`, đúng thứ tự ticket. Lệnh actual ở bước 3 và 4 đều có dry run
ngay phía trước với cùng slug/tuỳ chọn; không có upload/public ngay lập tức.

## Kiểm tra công cụ và rủi ro

- `enqueue_ck.py` chỉ đưa item vào store (`assembled`), không upload và hiện
  không có dry mode; không dùng nó trong chuỗi trên vì `upload_one --channel CK`
  dựng cùng Bundle rồi upload một item, với dry mode tương ứng.
- `upload_one.py` trước đây gắn cứng CL; đây là lý do đã sửa tối thiểu file này.
  `drip.py` cũng gắn cứng CL, nên không dùng cho CK.
- `publish_batch.py --channel CK check` hữu ích để xem queue, nhưng `run` lấy
  cả item CK `assembled` hợp lệ, không chọn chính xác ba slug; không dùng cho
  thay thế có thứ tự này.
- `factory/channel.py` kiểm title trùng trong `upload_log` và danh sách title
  hiện có của kênh trước upload. `factory/channels.py` đặt CK `pacing=(1, 90)`:
  tối thiểu một phút giữa hai lần upload và tối đa 90 lần trong 24 giờ;
  `--wait` dùng chính mốc này, không tự đoán thời gian chờ.
- Dry run của `upload_one` cố ý không truy vấn YouTube, vì vậy title trùng hoặc
  một tiến trình khác vừa chiếm slot chỉ có thể bị phát hiện ở actual. Actual
  dừng an toàn với lỗi trùng hoặc chờ với `--wait`; Lead cần xem kết quả từng
  dòng trước khi tiếp tục.
- Tôi không chạy lệnh ở bước 2–4: chúng cần credential/API và bước 3–4 thay
  đổi lịch/store, nằm ngoài quyền thực thi của ticket session này.
