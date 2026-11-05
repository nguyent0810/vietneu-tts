# GH-146 · Codex: chặn hai item cùng kênh trùng `publish_at`

Issue: https://github.com/nguyent0810/vietneu-tts/issues/146. Đọc issue và retro `docs/pm/2026-11-04-retro-ck-short-suc-mua.md` trước.

**Hạn:** 60 phút. Làm trong worktree này (nhánh `mimck/146-chan-trung-publish-at`).

## Hiện trạng
- Bảng `item` (`factory/store.py`) có `channel`, `slug`, `publish_at` (UTC, `...Z`), `stage`. Bảng `upload_log` (`factory/channel.py`) cũng lưu `publish_at` của video đã upload, và `Channel.reschedule()` đổi giờ.
- Không chỗ nào chặn hai item cùng kênh trùng giờ. Lỗi này đã xảy ra 3 lần (Short CK).
- Các cửa ghi giờ: `motion/stier/enqueue_ck.py`, `motion/stier/enqueue_mim.py`, `motion/stier/enqueue.py` (nếu dùng chung), `motion/stier/upload_one.py`, `motion/long/publish_long.py`, `Channel.reschedule()`. Tự kiểm xem còn cửa nào khác (vd `scripts/publish_batch.py`) và liệt kê trong báo cáo.

## Việc
1. **Một hàm kiểm duy nhất** trong `factory/store.py`, ví dụ `slot_conflicts(conn, channel, publish_at, exclude_slug=None) -> list[str]`:
   - trả slug các item **cùng kênh, cùng `publish_at`**, khác slug đang xét;
   - không tính stage `failed` và stage mới `replaced`;
   - cũng kiểm `upload_log` cùng kênh (video đã upload có hẹn giờ đó), trừ chính slug đang xét.
2. **Thêm stage `replaced`** vào `STAGES` cho bản gốc bị bản `-r2`/`-v2` thay. Chỉ thêm hằng số và để hàm kiểm bỏ qua nó. **Không** cập nhật hàng nào trong DB thật.
3. **Gọi hàm ở mọi cửa ghi giờ** (mục Hiện trạng). Gặp trùng thì thoát mã ≠ 0 (hoặc raise lỗi rõ ràng trong hàm thư viện), in slug item đã giữ giờ đó và giờ VN (UTC+7). Phải chặn **cả khi `--dry`** ở `upload_one.py`. Không thêm cờ bỏ qua.
4. **Test** trong `tests/` (DB tạm, không chạm `state.sqlite` thật, không gọi API YouTube):
   - hai item cùng kênh cùng giờ → bị chặn, thông báo có slug cũ;
   - khác kênh cùng giờ → cho qua;
   - item `failed` hoặc `replaced` → không tính;
   - chính item đó upload lại hoặc enqueue lại (cùng slug) → không tự chặn mình;
   - trùng với `upload_log` → bị chặn;
   - `reschedule` sang giờ đã có → bị chặn.

   Chạy `python -m pytest tests -q`. Nếu môi trường sandbox làm test lỗi (thư mục tạm, `fcntl`), ghi rõ test nào và lý do; Lead sẽ chạy lại.

## Được ghi
`factory/store.py`, `factory/channel.py`, `motion/stier/enqueue*.py`, `motion/stier/upload_one.py`, `motion/long/publish_long.py`, cửa khác tìm thêm ở mục Hiện trạng (ghi trong báo cáo), test mới trong `tests/`, báo cáo `docs/pm/tickets/GH-146-codex-report.md`.

**Không:**
- sửa dữ liệu `state.sqlite` hay `bundles/`, đổi lịch, upload;
- gọi API YouTube;
- render;
- commit;
- đọc credentials hay biến `YT_CREDS_DIR`.

## Báo cáo (`docs/pm/tickets/GH-146-codex-report.md`)
- Diff tóm tắt từng file, kèm file:dòng chỗ gọi hàm kiểm.
- Danh sách mọi cửa ghi `publish_at` đã tìm thấy, cửa nào đã chặn, cửa nào chưa và vì sao.
- Kết quả pytest (dán dòng cuối).

Câu trả lời cuối: tối đa 3 dòng.
