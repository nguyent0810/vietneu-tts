# GH-16 · Codex: sửa AVD rỗng và bổ sung chỉ số Studio (`webauto studio`)

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/16. Thêm lỗi AVD do retro ngày 02/11 phát hiện (`docs/pm/2026-11-02-studio-tuan-44.md`).

## Được ghi
- `webauto/studio.py`, `webauto/studio_summary.py`
- `tests/test_webauto_studio.py` (thêm test)
- báo cáo `docs/pm/tickets/GH-16-report.md`
- thư mục tạm dưới `output/webauto/_codex_tmp/` (để chạy thử `summarize`)

## Không được
- Không mở Chrome, không chạy `studio collect` thật (sandbox của bạn không điều khiển được trình duyệt; Claude sẽ chạy thật sau).
- Không ghi đè dữ liệu trong `output/webauto/studio/*/2026-10-28/`. Chỉ đọc, hoặc chép sang `_codex_tmp`.
- Không đọc `.youtube_channels` hay credentials. Không commit.

## Việc

1. **AVD rỗng (lỗi, ưu tiên 1).**
   - Hiện tượng: `videos.csv` trong cả 3 thư mục `output/webauto/studio/*/2026-10-28/` có cột `7d_avd_s` … `lifetime_avd_s` trống ở mọi dòng (0/106, 0/542, 0/106).
   - Trong khi đó `raw/videos__7d/table.csv` có cột "Average view duration" dạng `0:00:16`.
   - Tìm nguyên nhân trong `studio_summary.py` (`video_rows`, `duration_seconds`, khâu ghi CSV), rồi sửa.
   - Test hồi quy dùng một bảng mẫu có `0:00:16`, `1:02:03` và ô trống.
   - Chạy `python -m webauto studio summarize` trên **bản chép** sang `_codex_tmp`, xác nhận cột AVD có số.
2. **Shorts "Shown in feed" và "Stayed to watch" (#16).**
   - Tìm mã chỉ số trong catalog đã cache (`catalog_path()` / `load_catalog`) và trong code hiện có.
   - Thêm các mã này vào bộ chỉ số của báo cáo `videos`, có fallback: Studio từ chối bộ chỉ số mới thì vẫn xuất được như cũ.
   - Thêm 2 cột vào `summary.md` và `videos.csv`, chỉ cho Short.
   - Mã nào chưa chắc chắn thì ghi rõ là **chưa xác minh** trong báo cáo. Claude sẽ kiểm thật trên CK với `o75eN6_1enI` và `AVDmUn0nEXU`.
3. **Traffic source theo từng video.**
   - Thêm tùy chọn `collect --videos id1,id2,...` để xuất `traffic_source` lọc theo từng video.
   - Video cần lấy: `sywk-F-yW7k`, `CAYQtYA1NJA`, `LeckrmjPkdI`, `a45PR7ejNgk`.
   - Ghi bảng vào `summary.md`.
4. **Cột Hạn chế (restrictions)**, chỉ đọc. Nếu bản xuất Studio có cột này thì đưa vào `videos.csv`. Không có thì ghi rõ trong báo cáo.
5. **Lỗi "export produced no file" ngày 02/11** (chỉ phân tích, không chạy thật).
   - Đọc luồng tải file trong `studio.py` và `browsentic.py`.
   - Nêu các điểm có thể làm hỏng việc tải: thư mục tải, thời gian chờ, tab nền bị throttle.
   - Thêm thông báo lỗi rõ hơn, ví dụ in đường dẫn thư mục tải đang chờ và thời gian chờ.

## Gate
- `python -m pytest -q tests/test_webauto_studio.py tests/test_webauto.py`: phải qua hết.
- Không sửa test cũ để cho qua.

## Báo cáo `docs/pm/tickets/GH-16-report.md`
- Nguyên nhân gốc của lỗi AVD.
- Danh sách thay đổi theo file.
- Mã chỉ số đã thêm, mỗi mã ghi đã xác minh hay chưa.
- Kết quả test.
- Các lệnh để Claude chạy thật khi Chrome sẵn sàng.
