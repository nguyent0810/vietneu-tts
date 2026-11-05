# GH-146 · Báo cáo fix

`slot_conflicts` không còn tính `item.publish_at` của item đã có dòng `upload_log` cùng kênh, cùng slug. Giờ trong sổ là chuẩn. Sổ còn giữ đúng giờ thì câu truy vấn `upload_log` vẫn chặn. Item chưa có dòng sổ giữ hành vi cũ. Bảng sổ chưa có thì bỏ qua, vẫn kiểm `sqlite_master`.

Không sửa `state.sqlite`, không đụng `bundles/`, không gọi API YouTube, không đổi lịch, không commit.

## Diff

- `factory/store.py:219` — một lần kiểm `sqlite_master` cho cả hai phần.
- `factory/store.py:224-228` — khi sổ tồn tại, truy vấn `item` thêm `NOT EXISTS` dòng `upload_log` cùng `channel` và `slug`. Bản `published` đã gỡ lịch (`upload_log.publish_at` NULL) không còn chiếm slot theo `item.publish_at`.
- `factory/store.py:233-239` — truy vấn `upload_log` giữ nguyên: sổ còn đúng giờ thì slug đó vẫn bị chặn.
- `tests/test_slot_conflict.py:110` — item `published`, sổ NULL, cùng `item.publish_at` với slug khác → không chặn; enqueue slug kia được.
- `tests/test_slot_conflict.py:121` — item `published`, sổ còn đúng giờ → vẫn chặn (`ck-goc`).
- `tests/test_slot_conflict.py:193` — cặp gốc/`-r2` (`ck-p2-tra-truoc-mot-ty`) cùng `published` và cùng `item.publish_at`; gốc và một bản gốc khác (`ck-p2-khac`) đã gỡ lịch. `Channel.reschedule` của `-r2` sang chính giờ của nó và sang giờ `item.publish_at` của bản gốc kia không bị chặn. Sổ và video của hai bản gốc không đổi.

## pytest

```
822 passed, 29 skipped, 1 warning in 21.39s
```

Warning là `SyntaxWarning` cũ trong `tests/test_console.py` (`\T`), không phát sinh từ ticket này.
