# GH-146 · Báo cáo Codex

Chặn hai item cùng kênh trùng `publish_at`. Không sửa `state.sqlite`, không đổi lịch, không upload, không commit.

Hàm kiểm: `factory/store.py` `slot_conflicts` (dòng 197). Trả slug khác cùng kênh, cùng chuỗi `publish_at`. Bỏ qua item `failed` và `replaced`. Vẫn tính `upload_log` (mọi state), trừ chính slug đang xét. So khớp đúng chuỗi đã lưu, không quy đổi `+07:00` sang `Z`.

`refuse_slot` (dòng 233) gọi hàm đó và `SystemExit` mã 1. Thông báo có slug đang giữ và giờ VN UTC+7, ví dụ `trùng giờ 05/11/2026 12:00 VN (2026-11-05T05:00:00Z): đã giữ bởi ck-giu`.

`enqueue` (dòng 252) ném `SlotConflict` khi **hàng mới** đụng slot. Nạp lại đúng id thì không kiểm và không đổi `publish_at`.

Stage `replaced` thêm vào `STAGES` (dòng 41). Không có hàng nào trong DB thật bị đổi stage.

## Diff từng file

- `factory/store.py` — `STAGES` thêm `replaced`. `slot_conflicts` / `refuse_slot` / `SlotConflict`. `enqueue` dòng 252–255 gọi `slot_conflicts` trước khi INSERT hàng mới.
- `factory/channel.py` — `reschedule` dòng 311 và `_take` (mọi `Channel.upload` có giờ) dòng 476 gọi `_refuse_taken_slot` (dòng 428 → `slot_conflicts`). Trùng thì `PublishError`, chưa gọi API đổi lịch / chưa INSERT `upload_log`. Gỡ lịch (`publish_at is None`) không kiểm.
- `motion/stier/enqueue_ck.py` dòng 65 — `refuse_slot` trước khi ghi bundle và `enqueue`.
- `motion/stier/enqueue_mim.py` dòng 61 — cùng vậy.
- `motion/stier/enqueue.py` dòng 62 — khi chọn ô, bỏ giờ `slot_conflicts` báo (thêm giờ chỉ có trong `upload_log`). Dòng 80 — `refuse_slot` trước khi in và trước khi ghi, cả `--dry`. Bộ chọn cũ vẫn né mọi `item.publish_at`, kể cả `failed`/`replaced`; muốn dùng lại giờ của bản `failed` thì chỉ định giờ ở `enqueue_ck` / `upload_one`.
- `motion/stier/upload_one.py` dòng 100 — `refuse_slot` trước nhánh `--dry` và trước mọi ghi. `--dry` mở DB chỉ để đọc slot, không ghi, không upload.
- `motion/long/publish_long.py` dòng 62 — `register` gọi `refuse_slot` trước `save_bundle` / `enqueue` (kể cả kênh upload tay). Upload API sau đó còn bị `_take` dòng 476 chặn lần nữa.
- `scripts/publish_batch.py` dòng 194 — `do_run` gọi `refuse_slot` trước `chan.upload`. `SystemExit` không bị `except Exception` nuốt. `probe` đặt `publish_at=None`, không chiếm slot.
- `tests/test_slot_conflict.py` — DB tạm: cùng kênh bị chặn và có slug cũ + giờ VN; khác kênh cho qua; `failed`/`replaced` không tính; cùng slug enqueue/upload lại không tự chặn; `upload_log` chặn; `reschedule` sang giờ đã có thì chặn và không đổi lịch; `upload_one --dry`, `enqueue_ck`/`enqueue_mim`, `publish_long.register` thoát mã ≠ 0.
- `tests/test_publish_batch.py` — `do_run` gặp hai item cùng giờ thì thoát, không upload.
- `tests/test_channel.py`, `test_one_store.py`, `test_manual.py`, `test_bundle_and_store.py`, `test_wait_upload.py` — các ca cũ tình cờ dùng chung một `publish_at` cho hai slug (để thử nhịp, tiêu đề, sync) nay mỗi slug một giờ. Hành vi đang thử không đổi.

Không thêm cờ bỏ qua.

## Cửa ghi `publish_at`

Đã chặn:

| Cửa | Chỗ gọi |
|---|---|
| `store.enqueue` (hàng mới) | `factory/store.py:252` |
| `enqueue_ck.py` | dòng 65 |
| `enqueue_mim.py` | dòng 61 |
| `enqueue.py` (kể cả `--dry`) | dòng 62 và 80 |
| `upload_one.py` (kể cả `--dry`) | dòng 100 |
| `publish_long.register` | `motion/long/publish_long.py:62` |
| `Channel.upload` / `_take` | `factory/channel.py:476` |
| `Channel.reschedule` | `factory/channel.py:311` |
| `publish_batch.py run` | `scripts/publish_batch.py:194` |
| `scripts/reschedule.py:45` | đi qua `Channel.reschedule` |
| `motion/stier/drip.py:60` | gọi `upload_one.py` |
| `store.sync_from_disk` | đi qua `enqueue` |
| `scripts/make_pillars_day.py:131`, `make_lich_oct.py:170`, `make_lich_month.py:100` | ghi JSON rồi `sync_from_disk` → `enqueue` ném `SlotConflict` |

Chưa chặn, và vì sao:

- `Channel.adopt` (`factory/channel.py:385`) — chép `status.publishAt` của video **đã có trên YouTube**. Từ chối thì sổ lệch Studio. `factory/manual.py` nhận video tay đi qua `adopt`.
- `publish_batch.py probe` (dòng 123) — cố ý không hẹn giờ (`publish_at=None`).
- `scripts/unschedule.py:141` và `Channel.hide` — gỡ lịch (`None`), không chiếm slot.
- `Channel._set_private` — chỉ ghi sau khi `reschedule` đã kiểm; `hide` truyền `None`.

`replaced` không xóa dòng `upload_log`. Bản gốc đã upload, đánh `replaced` mà sổ vẫn giữ giờ đó, thì slug khác vẫn bị chặn. Muốn nhường giờ cho `-r2`/`-v2` thì gỡ lịch bản gốc (hoặc để `publish_at` sổ không còn trùng) rồi `mark(..., "replaced")`. Ticket cấm sửa hàng trong DB thật; stage chỉ là hằng số.

## pytest

```
819 passed, 29 skipped, 1 warning in 25.57s
```

Warning là `SyntaxWarning` cũ trong `tests/test_console.py` (`\T`), không phát sinh từ ticket này. Không tạo `state.sqlite`.
