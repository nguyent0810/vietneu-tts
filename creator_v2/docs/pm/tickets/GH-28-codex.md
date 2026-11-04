# GH-28 · Codex: gỡ lịch theo slug + quy trình thay Short CK

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/28.

## Bối cảnh
Cần thay 3 Short CK đã upload private + hẹn giờ:
- `ck-c2-mua-thu-nam-thu-sau` (03/11 12:00Z)
- `ck-c2-mot-lo-bao-nhieu` (04/11 05:00Z)
- `ck-c2-ban-lo-van-nop-thue` (05/11 12:00Z)

Thay bằng 3 Short đã có `output/stier/<slug>/final.mp4`: `ck-b4-bay-tram-thanh-tam-tram`, `ck-b4-tra-gop-them-184-trieu`, `ck-b1-muoi-nam-sau`, đăng đúng 3 giờ cũ (theo thứ tự trên). `scripts/unschedule.py` hiện chỉ gỡ lịch CẢ kênh.

## Được ghi
- `scripts/unschedule.py`
- test mới `tests/test_unschedule_slug.py`
- báo cáo `docs/pm/tickets/GH-28-report.md`

**Không:** gọi API YouTube, upload, enqueue, đổi `state.sqlite`, đọc credentials, commit.

## Việc
1. Thêm `--slug <slug>` (lặp được) cho `scripts/unschedule.py`.
   - Có `--slug` thì chỉ xét các item có slug đó. Slug nào không có trong store, hoặc không ở trạng thái private + publishAt tương lai, thì in lỗi và thoát mã khác 0 trước khi gỡ bất cứ gì.
   - Không có `--slug` thì giữ nguyên hành vi cũ.
   - Lý do ghi vào `error` khi có `--slug`: `UNSCHEDULED <ngày>: thay bằng Short khác (GH-28)`.
   - Chạy khô vẫn là mặc định.
   - Tách phần lọc thành hàm thuần để test được mà không cần API (mock `publish._api` / `Channel`).
2. Đọc `motion/stier/enqueue_ck.py`, `motion/stier/upload_one.py`, `motion/stier/drip.py`, `scripts/publish_batch.py` và `factory/channel.py`. Trong báo cáo, ghi **chính xác chuỗi lệnh** Lead cần chạy để đưa 3 Short thay thế lên kênh CK, private + `publishAt` đúng 3 giờ trên. Mỗi lệnh phải có chế độ chạy khô.
   - Công cụ hiện có chỉ dành cho kênh khác (vd. `upload_one.py` gắn với CL) thì nói rõ, và đề xuất sửa tối thiểu: ghi luôn sửa đó vào file nếu nằm trong `motion/stier/upload_one.py`, kèm test.
   - Kiểm luật chống trùng tiêu đề và giới hạn upload theo kênh (`factory/channels.py`).
3. Chạy `python -m pytest -q -p no:cacheprovider tests/test_unschedule_slug.py` (nếu sandbox chặn tmp thì ghi lại).

Được ghi thêm `motion/stier/upload_one.py` và test của nó, chỉ khi cần cho mục 2.

## Báo cáo
Diff tóm tắt, chuỗi lệnh từng bước (chạy khô → chạy thật), rủi ro.
