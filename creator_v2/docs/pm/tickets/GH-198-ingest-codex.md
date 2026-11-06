# GH-198 (tiếp): lệnh nạp cả thư mục vào kho chung

Bối cảnh: `library/tools/assets.py` đã có `add` (nạp một file, chống trùng gần bằng pHash), `push`, `pull`, `prune` (PR #199). Grok Bot sắp trả về lô 60 ảnh, sau đó có cả clip. Cần nạp cả lô trong một lệnh.

**File được sửa:** `library/tools/assets.py`, `tests/test_assets.py` (ở gốc repo), báo cáo `creator_v2/docs/pm/tickets/GH-198-ingest-report.md`.

**Yêu cầu:** thêm lệnh `ingest-dir <thư mục> --pham-vi <kênh|chung> [--ai] [--tags a,b] [--tags-from-prompts <ai_prompts.md>] [--push] [--near-threshold N] [--dry-run]`.
1. Quét ảnh và video trong thư mục, theo thứ tự tên file ổn định. Mỗi file gọi đúng logic của `add_asset`, không chép lại logic.
2. Ảnh gần trùng với kho **hoặc với file khác trong cùng lô** thì bỏ qua, không dừng cả lô. Ghi lại cặp trùng.
3. `--tags-from-prompts`: đọc file prompt dạng `## ai_NN.png — <nhóm>` và dòng `- Prompt (tiếng Anh): ...`. Gắn prompt vào record. Gắn tag theo nhóm, có ánh xạ: "MIM"→mim,cong_nghe; "CK"→ck,tien_bac; "CL"→cl,hinh_su,minh_hoa_chung. Ánh xạ khai báo thành hằng số dễ sửa.
4. `--push`: sau khi nạp, đẩy các asset mới lên Drive bằng `push_assets`.
5. In tóm tắt JSON: đã nạp, gần trùng (kèm id trùng), lỗi, đã push.
6. `--dry-run`: không ghi manifest, không push.
7. Test (giả lập rclone như các test GH-198 sẵn có): lô có hai ảnh gần trùng nhau thì chỉ nạp một; tag lấy đúng từ prompt; dry-run không ghi; push được gọi cho asset mới.
   `python -m pytest tests/test_assets.py -q` phải xanh.

**Không:** commit, push git, gọi rclone thật, upload, đọc thư mục credentials.

**Báo cáo:** file đổi, cách dùng lệnh, dòng tóm tắt pytest.
