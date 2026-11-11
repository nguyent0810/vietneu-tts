# GH-264 — Áp lời v3 vào 9 spec Short CL và neo lại cảnh (Codex)

Chủ kênh đã duyệt giọng v3 ngày 11/11 ("Duyệt"). Lời cuối nằm ở `docs/pm/tickets/GH-264-rewrite-9-final.json`, trường `lines_v3`.

## Việc
Với mỗi slug trong file trên (9 bài, spec ở `data/stier/specs/<slug>.json`):

1. Thay `lines` bằng `lines_v3`, giữ nguyên từng chữ. Không sửa lời. Nếu buộc phải sửa để qua preflight, ghi rõ vào báo cáo.
2. **Neo lại `scenes`.** Mỗi `at` (và `label.at`, `headAt` nếu có) có dạng `[chỉ số câu, "từ đầu"]`, đang trỏ vào `lines` cũ. Với mỗi neo:
   - tìm câu mới chứa cùng dữ kiện hoặc tên mà ảnh minh họa, rồi neo vào câu đó với một từ có thật trong câu;
   - nếu câu cũ đã bị bỏ, neo cảnh vào câu mới gần nghĩa nhất, hoặc gộp cảnh, sao cho ảnh vẫn đúng với lời đang đọc;
   - thứ tự `at` phải tăng dần, mỗi cảnh dài ít nhất khoảng 2 giây;
   - cảnh 0 (`hero`) giữ `at: 0`.
3. `say`: thêm cách đọc cho tên mới xuất hiện trong lời, nếu có. Giữ gạch nối trong tên phiên âm như Con-gung, Ma-ri.
4. Không đổi `title`, `imgs`, `description`, `sources`, `publish_at`.

## Kiểm
- `PYTHONIOENCODING=utf-8 .venv\Scripts\python.exe motion/stier/build.py --preflight <9 slug>` phải OK cho cả 9 bài, không dùng `--allow-hook`.
- `motion/stier/script_lint.py <9 slug>`: 0 lỗi. Cảnh báo R5 với series Bao được phép.
- Ghi bằng Python utf-8, `json.dump(ensure_ascii=False, indent=1)`. Grep không có `?` thay chữ có dấu.

## Ràng buộc
Chỉ ghi 9 spec và file báo cáo. Không render, không enqueue, không commit, không đổi lịch.

## Báo cáo
`docs/pm/tickets/GH-264-apply-9-report.md`. Mỗi bài ghi:
- kết quả preflight;
- bảng neo cảnh, cũ → mới (câu, từ, ảnh);
- mọi chỗ phải sửa lời.
