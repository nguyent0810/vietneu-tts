# GH-416 (Codex): cổng khung đầu 0–3 s phải có hình rõ (Long + Short)

Đọc issue #416 (chép dưới), `motion/long/build_long.py` (lệnh `final`: phần cổng sau khi ghép, cạnh `check_mix_level`), `motion/stier/build.py` (bước QA final, `retention_hook_lint`, `hook_errors`), `motion/long/thumb.py` (lint (c) độ lệch chuẩn sáng < 40 — tham khảo cách đo).

Bối cảnh: final Long cl-dich-nhan-kiet 15/11 có 3 giây đầu chỉ là giấy xám trống (ảnh dọc bị cắt sai `focus`); mọi cổng đều ĐẠT. Cần cổng đo khung thật.

## Việc
1. Module mới `motion/first_frames.py` (dùng chung Long/Short): hàm `measure(video_path, times) -> list[dict]` dùng ffmpeg (`FFMPEG` như các module khác) trích khung ở các mốc, cắt vùng giữa (bỏ 12% trên cho HUD, 22% dưới cho phụ đề, 5% hai bên), tính `std` độ sáng (0–255) và `edge` = tỉ lệ pixel có gradient Sobel/độ chênh láng giềng > ngưỡng. Hàm `flat(m)` -> True nếu std < STD_MIN và edge < EDGE_MIN. Hàm `problems(video, times)` trả lỗi khi **mọi** khung đều flat.
2. Hiệu chỉnh ngưỡng: tạo khung tổng hợp (xám đồng màu + nhiễu hạt nhẹ + chữ nhỏ ở HUD) phải flat; khung có ảnh tư liệu/chân dung phải qua. Dùng file thật còn trên đĩa để kiểm không báo nhầm: `D:\Tools\Youtube Creator v2ietneu-main\creator_v2\output\stier\*inal.mp4` (Short, mốc 0,3/1,0/2,0) — ít nhất 10 Short; Long final còn trên đĩa nếu có trong `...\output\long\*inal.mp4` (mốc 0,5/1,5/2,5). Ghi bảng giá trị đo vào báo cáo.
3. `build_long.py final`: sau khi ghép final, gọi `first_frames.problems(final, [0.5, 1.5, 2.5])` cho topic không legacy (`is_legacy_topic`); có lỗi thì SystemExit với thông điệp tiếng Việt nêu giá trị đo và gợi ý (kiểm focus ảnh dọc, cảnh đầu phải là hình mạnh nhất). Không áp cho legacy.
4. `stier/build.py`: ở bước QA final, spec `rules >= 3` gọi với [0.3, 1.0, 2.0]; lỗi thì in "LỖI khung đầu" và trả mã lỗi như các cổng QA khác.
5. Test `tests/test_first_frames.py`: khung phẳng → lỗi; khung có chi tiết → qua; một khung phẳng hai khung tốt → qua; legacy bỏ qua. Dùng ffmpeg tạo video ngắn từ ảnh tổng hợp; test cần ffmpeg dùng marker/skip như `tests/test_mix_level.py` (needs_ffmpeg).

## Luật
- Chỉ sửa: `motion/first_frames.py` (mới), `motion/long/build_long.py`, `motion/stier/build.py`, `tests/test_first_frames.py` (mới). CLI mới (nếu có) gọi `factory.console.utf8_console()`.
- **Ghi file bằng Python `open(..., 'w', encoding='utf-8')`, không PowerShell.** Sau khi ghi, `git diff` không có `??` mới.
- Không render production, không chạy toàn bộ pytest nếu có test gọi render (chỉ chạy test liên quan + `tests/test_console.py`); Lead sẽ chạy toàn bộ.
- Không commit, không push, không đăng, không đọc thư mục credentials.

## Báo cáo
`docs/pm/tickets/GH-416-report.md` (tiếng Việt, Python utf-8): thay đổi, ngưỡng + bảng đo, kết quả test.
