# GH-16 report

## Đã làm

- `webauto/studio_summary.py`
  - Tách `Average view duration` khỏi bộ chuyển số chung. `video_rows()` giờ luôn đọc AVD bằng `duration_seconds()` trước khi ghi vào dữ liệu theo kỳ; giữ được `0:00:16` (16 giây), `1:02:03` (3.723 giây), và ô trống (`None`).
  - Thêm hai cột xuất CSV theo kỳ: `shown_in_feed`, `stayed_to_watch`. Khi export có hai header Studio tương ứng, chỉ các hàng Short có số; hàng Long vẫn rỗng.
  - Thêm bảng Short trong `summary.md` khi hai chỉ số có dữ liệu, bảng nguồn lưu lượng theo từng video, và cột `restrictions` có điều kiện khi export thực sự chứa header `Restrictions`.
- `webauto/studio.py`
  - Thêm bộ metric Shorts ưu tiên trước các bộ đã cache, rồi fallback lần lượt về bộ cũ nếu Studio từ chối. Bộ cache không cần reset để thử lại metric mới.
  - Thêm `collect --videos id1,id2,...`; mỗi id sinh export `traffic_source` riêng với filter `VIDEO==<id>`, lưu `video_id` trong manifest và thư mục raw không đè nhau.
  - Thông báo lỗi export giờ ghi rõ thư mục chờ download (`~\\browsentic\\download`) và thời gian chờ 45 giây.
- `tests/test_webauto_studio.py`
  - Thêm regression AVD với `0:00:16`, `1:02:03`, ô trống; kiểm tra Restrictions; kiểm tra URL filter, parse `--videos`, fallback metric, và bảng traffic-source theo video.

## Nguyên nhân AVD

AVD là thời lượng có dấu `:` chứ không phải số thập phân. Đường xử lý tổng quát `num()` trả `None` với các giá trị như `0:00:16`; vì vậy không được để AVD đi qua đường số chung trước khi ghi `videos.csv`. `video_rows()` nay xử lý AVD riêng bằng `duration_seconds()`. CSV cũ là output đã sinh trước khi có đường xử lý an toàn này nên mọi cột AVD đều trống dù raw CSV có dữ liệu.

Đã chạy trên bản sao tại `output/webauto/_codex_tmp/GH-16/2026-10-28`:

```text
python -m webauto studio summarize --dir output/webauto/_codex_tmp/GH-16/2026-10-28
7d_avd_s=38
28d_avd_s=62
90d_avd_s=62
365d_avd_s=70
lifetime_avd_s=102
```

## Metric Shorts

| Metric Studio candidate | Cột export | Trạng thái |
|---|---|---|
| `SHORTS_FEED_SHOWN` | `Shown in feed` / `shown_in_feed` | **Chưa xác minh**: không có trong `studio_catalog.json`; chưa được phép mở Studio/Chrome để export thật. |
| `SHORTS_STAYED_TO_WATCH` | `Stayed to watch` / `stayed_to_watch` | **Chưa xác minh**: không có trong `studio_catalog.json`; chưa được phép mở Studio/Chrome để export thật. |

Nếu một hoặc cả hai metric bị Studio từ chối, collect tiếp tục dùng `METRICS_FULL`, rồi `METRICS_BASE` và `METRICS_MIN`; báo cáo cũ vẫn được xuất.

## Restrictions

Đã chỉ đọc toàn bộ 15 `raw/videos__*/table.csv` của ba thư mục Studio ngày `2026-10-28`: không file nào có header `Restrictions`. Code đã sẵn sàng ghi cột khi Studio cung cấp nó, nhưng hiện chưa thể xác nhận export thật có hỗ trợ cột này.

## Phân tích "export produced no file"

Không chạy Chrome hay collect thật. Luồng hiện tại tạo tab mới, click tin cậy nút export, chờ `page_captureDownload` tối đa 45 giây, rồi quét thư mục `~\\browsentic\\download` theo mtime. Điểm có thể hỏng:

- Chrome/Browsentic đang dùng thư mục download khác thư mục quét.
- Export lớn chưa hoàn tất trong 45 giây.
- Tab mới nền bị Chrome throttle nên export hoặc download khởi động chậm.
- Capture báo xong nhưng file chưa xuất hiện trong thư mục, hoặc guardrail download chưa cho phép.

Thông báo mới nêu rõ thư mục và thời gian chờ để phân biệt các trường hợp này trong lần chạy thật.

## Kiểm tra

Đã chạy:

```text
python -m py_compile webauto/studio.py webauto/studio_summary.py
python -m pytest -q -p no:cacheprovider \
  tests/test_webauto_studio.py::test_num_va_ngay \
  tests/test_webauto_studio.py::test_avd_thoi_luong_va_han_che_duoc_giu_trong_dong_video \
  tests/test_webauto_studio.py::test_build_url_co_du_tham_so \
  tests/test_webauto_studio.py::test_video_ids_va_metric_shorts_co_fallback
```

Kết quả: `4 passed`; `py_compile` qua, không có lỗi lint riêng trong ticket.

Đã thử gate bắt buộc:

```text
python -m pytest -q tests/test_webauto_studio.py tests/test_webauto.py
```

Kết quả sandbox: `33 passed, 9 skipped, 16 errors`. Mọi lỗi là `PermissionError` khi pytest quét/cấp phát `%USERPROFILE%\AppData\Local\Temp\pytest-of-<user>`; đổi `--basetemp` sang `output/webauto/_codex_tmp/GH-16-pytest` vẫn bị sandbox chặn `os.scandir`. Đây là lỗi môi trường fixture, không phải assertion thất bại. Claude cần chạy lại gate trên máy có quyền đọc thư mục tạm.

## Lệnh Claude chạy thật khi Chrome sẵn sàng

Kiểm chứng metric Shorts trên CK và đồng thời lấy traffic-source theo video:

```text
python -m webauto studio collect --channel UCseQ5p0-e0_DW35M__d_oHg --reports videos,traffic_source --periods 7d,28d,90d,365d,lifetime --videos o75eN6_1enI,AVDmUn0nEXU
```

Lấy riêng nguồn lưu lượng cho bốn video được ticket yêu cầu:

```text
python -m webauto studio collect --channel UCseQ5p0-e0_DW35M__d_oHg --reports traffic_source --periods 28d,lifetime --videos sywk-F-yW7k,CAYQtYA1NJA,LeckrmjPkdI,a45PR7ejNgk
```

Sau đó kiểm tra `summary.md`, `summary.json`, `videos.csv` của thư mục ngày mới tạo. Không có clip sheet hoặc thumbnail trong ticket này.
