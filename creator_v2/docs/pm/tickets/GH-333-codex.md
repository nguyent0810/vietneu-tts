# GH-333: gắn "Video liên quan" Short→Long (Codex, phần code)

Đọc issue (chỉ đọc): `gh issue view 333 --repo nguyent0810/vietneu-tts`.

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-333`, nhánh `feat/333-related`. Đường dẫn tính từ `creator_v2/`.
- Lead commit, mở PR và **tự chạy trên trình duyệt thật**: sandbox của bạn không mở được Chrome. Không push, không gọi `gh` để ghi.

## Việc
1. **`scripts/related_map.py <CH> [--write]`**
   - Đọc DB (`factory/store.py`, bảng `item`): Short của kênh, gồm cả đã đăng (có video_id), và Long đã công khai (`publish_at` ≤ now, có video_id).
   - Ghép mỗi Short với 1 Long:
     - ưu tiên trường `long_target` trong spec hay bundle của Short nếu có;
     - nếu không có, lấy Long có từ khóa tiêu đề hoặc chủ đề trùng nhiều nhất (tách từ tiếng Việt đơn giản, bỏ stopword);
     - nếu không có gì trùng, lấy Long mới nhất cùng kênh và đánh dấu `fallback: true`.
   - In bảng gồm: slug Short, tiêu đề Short, Long, điểm, lý do.
   - `--write` ghi `output/channels/<CH>/related_map.json`.
2. **`webauto/studio_related.py` + lệnh `python -m webauto studio related <CH> --map <json> [--dry-run] [--limit N]`**
   - Theo mẫu code Studio sẵn có trong `webauto/` (`studio.py`, `browsentic.py`, `common.py`).
   - Mở `https://studio.youtube.com/video/<id>/edit`, tìm mục "Video liên quan" (Related video), chọn Long theo video_id, rồi Lưu.
   - Selector gom vào một chỗ ở đầu file, có chú thích. Chưa kiểm thật được, nên viết phòng thủ: timeout rõ ràng, chụp màn hình khi lỗi.
   - Ghi sổ `output/channels/<CH>/related_done.json`. Chạy lại không gắn lại những Short đã xong.
   - `--dry-run` chỉ in kế hoạch.
   - Không đổi tiêu đề, mô tả, thumbnail hay chế độ hiển thị.
3. **Test** `tests/test_related_map.py`: ghép theo `long_target`, ghép theo từ khóa, fallback, bỏ qua Long chưa công khai, đọc sổ để không gắn lại. Dùng DB tạm.

## File được ghi
- `scripts/related_map.py`
- `webauto/studio_related.py`
- Phần đăng ký lệnh trong `webauto/cli.py`, chỉ thêm subcommand
- `tests/test_related_map.py`
- Báo cáo `docs/pm/tickets/GH-333-report.md`, ghi bằng Python utf-8

Không sửa file khác. Không chạy trình duyệt thật, không đăng.
