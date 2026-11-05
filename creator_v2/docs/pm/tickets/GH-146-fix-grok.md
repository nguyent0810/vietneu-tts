# GH-146 fix · Grok: `slot_conflicts` chặn nhầm item đã gỡ lịch

Đọc trước `docs/pm/tickets/GH-146-codex.md` và `GH-146-codex-report.md` (bản đã làm, còn chưa commit trong worktree này).

**Hạn:** 30 phút.

## Lỗi Lead tìm thấy khi review
DB thật có 8 cặp gốc/`-r2` (vd `ck-p2-tra-truoc-mot-ty` / `-r2`). Ở **cả hai**, `item.stage='published'`, cùng `item.publish_at`.
Tuy nhiên bản gốc đã gỡ lịch trên YouTube nên `upload_log.publish_at` của nó là `NULL`, còn của `-r2` là giờ hẹn.

`slot_conflicts` hiện chỉ đọc `item.publish_at`, nên:
- `Channel.reschedule` bản `-r2` sang chính giờ của nó, hoặc sang giờ của bản gốc nào đó, sẽ bị chặn nhầm;
- mọi cửa ghi giờ đều coi giờ đó đã bị bản gốc giữ, dù bản gốc không còn lịch.

## Việc
1. Trong `factory/store.py` `slot_conflicts`, phần truy vấn bảng `item`: nếu item có dòng `upload_log` **cùng kênh, cùng slug** thì giờ trong `upload_log` là chuẩn. Không tính item đó theo `item.publish_at` nữa. Phần truy vấn `upload_log` hiện có sẽ bắt nó nếu sổ còn giữ giờ.
   - Chỉ làm khi bảng `upload_log` tồn tại, giữ kiểu kiểm `sqlite_master` đang dùng.
   - Item chưa có dòng `upload_log` thì giữ hành vi cũ.
2. Test thêm vào `tests/test_slot_conflict.py`:
   - item `published`, `upload_log.publish_at = NULL`, cùng `item.publish_at` với slug khác → không chặn;
   - item `published`, `upload_log` còn đúng giờ đó → vẫn chặn;
   - `Channel.reschedule` của `-r2` trong tình huống 8 cặp trên → không bị chặn bởi bản gốc.
3. Chạy `python -m pytest tests -q`.

## Được ghi
`factory/store.py`, `tests/test_slot_conflict.py`, báo cáo `docs/pm/tickets/GH-146-fix-report.md`.

**Không:**
- sửa `state.sqlite` thật hay `bundles/`;
- gọi API YouTube, upload, đổi lịch;
- render;
- commit;
- đọc credentials hay `YT_CREDS_DIR`.

## Báo cáo
Diff tóm tắt, kèm file:dòng. Dán dòng cuối pytest.

Câu trả lời cuối: tối đa 3 dòng.
