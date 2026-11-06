# GH-198: đưa ảnh kho chung vào Long, tự ghi lần dùng khi đăng

**Bối cảnh:**
- Kho chung `library/tools/assets.py` (gốc repo) đã có `add`, `ingest-dir`, `push`, `pull`, `prune`, `mark-used --public-date`.
- `prune` chỉ xoá bản trên máy khi mọi lần dùng có `ngay_public` quá 7 ngày, nên phải ghi lần dùng đúng lúc đăng.
- Engine Long đọc ảnh ở `creator_v2/output/long/<topic>/img/<key>.jpg` kèm `<key>.json`. Xem `creator_v2/scripts/ai_img_import.py` để biết định dạng: RGB 1920×1080 cover, `.json` có license "no restrictions", cảnh dùng ảnh AI đặt `credit: false`.

**File được sửa:**
- `library/tools/assets.py`
- `tests/test_assets.py` (gốc repo)
- `creator_v2/motion/long/publish_long.py`
- test mới `creator_v2/scripts/test_publish_markused_198.py` (để trong scripts/; Lead sẽ chuyển sang tests/)
- báo cáo `creator_v2/docs/pm/tickets/GH-198-place-report.md`, ghi bằng Python với `encoding="utf-8"`

`build_long.py` và engine KHÔNG sửa.

**Việc:**
1. `assets.py place <topic> <key> <asset_id> [--creator-root creator_v2]`:
   - asset chưa có trên máy thì `pull` về cache;
   - đổi sang JPG RGB 1920×1080 (cover) tại `creator_v2/output/long/<topic>/img/<key>.jpg`;
   - ghi `<key>.json` cùng khoá như ai_img_import, thêm `"asset_id"` và `"ai_generated"`;
   - không ghi đè file đã có, trừ khi có `--force`.
2. `publish_long.py`: sau khi upload thành công (có `video_id`), duyệt `output/long/<topic>/img/*.json`. Mỗi file có `asset_id` thì gọi `mark_used(asset_id, video_id, <mã kênh>, <ngày hôm nay>, ngay_public=<publish_at[:10]>)`.
   - Import `library/tools/assets.py` theo đường dẫn tuyệt đối từ gốc repo.
   - Lỗi ghi manifest chỉ in cảnh báo, không làm hỏng lần đăng.
   - Chạy lại khi video đã đăng thì không ghi trùng; `mark_used` đã chống trùng.
3. Test, không gọi rclone hay YouTube thật:
   - `place` tạo đúng jpg 1920×1080 và json có asset_id;
   - không ghi đè khi thiếu `--force`;
   - bước ghi lần dùng của publish ghi đúng asset_id, kênh, ngay_public, và không ghi trùng khi chạy lại. Tách bước này thành hàm riêng để test được mà không upload.
4. `python -m pytest tests/test_assets.py -q` (gốc repo) và test mới đều xanh.

**Không:** commit, upload, gọi API thật, đọc thư mục credentials.
