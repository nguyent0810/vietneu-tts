# GH-198: kho ảnh AI chung trên Drive (phần code)

Đọc issue #198 (`gh issue view 198 --repo nguyent0810/vietneu-tts`). Làm phần "mở rộng assets.py", trừ giai đoạn 2.

**File được sửa** (chỉ những file này; đường dẫn tính từ gốc repo, tức thư mục cha của creator_v2):
- `library/tools/assets.py`: mở rộng, giữ nguyên hành vi các lệnh hiện có.
- `tests/test_assets.py` ở GỐC repo (không phải creator_v2/tests): thêm test. File này nằm ngoài phạm vi cấm của creator_v2/AGENTS.md.
- `library/channels/cl.yaml`: chỉ khóa `kho_loc`.
- `creator_v2/docs/pm/tickets/GH-198-report.md`: báo cáo.

**Yêu cầu**
1. **Chống trùng gần** khi `add` và `scan`:
   - Ảnh: pHash 64 bit bằng numpy + Pillow (không thêm thư viện mới). Ghi vào record (`phash`).
   - Video: hash 5 khung chia đều qua ffmpeg.
   - Hamming ≤ ngưỡng (mặc định 8, chỉnh bằng `--near-threshold`) so với ảnh đã có → từ chối và in ID ảnh trùng. Có `--allow-near` để bỏ qua có chủ ý.
   - Thêm lệnh `near-dups` liệt kê các cặp gần trùng trong manifest.
2. **Lưu Drive qua rclone** (gọi `rclone` bằng subprocess, không thư viện Google):
   - Remote lấy từ biến môi trường `ASSET_REMOTE` (ví dụ `Ten:`), thư mục gốc từ `ASSET_REMOTE_ROOT` (mặc định `creator-assets`). Thiếu biến thì báo lỗi rõ ràng. Không ghi tên remote vào repo.
   - `push [--id ...|--all-local]`: dùng `rclone copyto`, sau đó `rclone hashsum`/`lsjson --hash` so sha. Khớp thì ghi `remote_path` vào record.
   - `pull --ids ...|--plan ...` → cache (`ASSET_CACHE`, mặc định `output/asset_cache`). Kiểm sha256 sau khi kéo.
   - `prune [--dry-run]`: chỉ xóa bản trên máy khi (a) record có `remote_path` và hash trên Drive khớp, (b) không plan nào đang dựng dùng asset, (c) lần dùng cuối đã public hơn 7 ngày. Mặc định là `--dry-run`; muốn xóa thật phải có `--yes`.
3. **Trần lần dùng:** `find` thêm `--max-uses N` (mỗi kênh) và `--min-gap-days D`, dùng lịch sử `mark-used`. Mặc định lấy từ `kho_loc` của kênh (`max_dung`, `cach_ngay`).
4. **CL** `kho_loc`: thay `cam_anh_ai: true` bằng luật chỉ cho ảnh AI có tag `minh_hoa_chung`. Cài luật này trong `passes_kho_loc`.
5. **Test:**
   - Giả lập rclone (monkeypatch subprocess), không gọi mạng.
   - Ảnh test sinh bằng Pillow.
   - Có test cho: phát hiện gần trùng, từ chối khi add, push ghi remote_path, pull kiểm sha, prune không xóa khi sha lệch hoặc asset đang dùng, trần lần dùng, luật CL.
   - Toàn bộ `python -m pytest tests/test_assets.py` phải xanh.

**Không:** commit, push git, upload YouTube, chạy rclone thật, đọc thư mục credentials.

**Báo cáo** `creator_v2/docs/pm/tickets/GH-198-report.md`: file đã đổi, lệnh mới, kết quả pytest (dán dòng tóm tắt), các giả định.
