# GH-274 (đợt 2) — Codex: đa dạng chuyển động mỗi cửa sổ 2 phút + kết quả ổn định khi dựng từng chương

Issue: https://github.com/nguyent0810/vietneu-tts/issues/274. Đợt 1 đã merge (PR #283): `motion/long/cine_auto.py` (`Director`), gọi trong `motion/long/build_long.py` (tìm `director.apply`). Báo cáo đợt 1: `docs/pm/tickets/GH-274-report.md`.
Worktree của bạn: thư mục hiện tại (`wt-274`, nhánh `feat/274-cam-windows`). Chỉ ghi trong worktree này.

## Hai việc còn mở
1. **Cửa sổ 2 phút có dưới 3 kiểu chuyển động** (16/161 cửa sổ ở lần đo 11/11), xảy ra ở chương ít ảnh. Sửa trong `Director`:
   - Đếm "kiểu chuyển động" gồm `cam` của cảnh ảnh, `cam` nền của cảnh chữ (nền lấy ảnh gần nhất), `pano`, và b-roll (tính là một kiểu `video`).
   - Khi cửa sổ 120 s hiện tại sắp kết thúc mà chưa đủ 3 kiểu, ưu tiên gán kiểu còn thiếu cho cảnh ảnh/nền chữ kế tiếp (vẫn giữ luật không hai `cam` giống nhau liền nhau, 120 s đầu không đóng khung ảnh, cảnh ghi tay giữ nguyên).
   - Nếu cửa sổ không có cảnh nào gán được (toàn cảnh ghi tay) thì không ép, chỉ in cảnh báo.
2. **Dựng `html chNN` riêng phải ra đúng như dựng toàn bộ.** Hiện khi có `only`, chương bị bỏ qua không đi qua `director.apply` nên trạng thái (`index`, `image_index`, `last_cam`, số pano) lệch. Sửa để trạng thái của chương bỏ qua vẫn được "chạy khô" (apply trên bản sao cảnh, không ghi file) hoặc tính lại tất định. Test: với một spec giả 3 chương, `cam`/`fx`/`transition_in` của ch02 khi chạy `only={'ch02'}` bằng đúng khi chạy cả 3 chương.
3. In bảng phân bố hiện có thêm: số cửa sổ 2 phút < 3 kiểu (trước/sau).

## Đạt khi
- Test mới `tests/test_cine_windows.py`: (a) chương ít ảnh (ví dụ 4 ảnh + 10 cảnh chữ trong 240 s) đạt ≥ 3 kiểu mỗi cửa sổ; (b) dựng một chương ra kết quả bằng dựng toàn bộ; (c) cảnh ghi tay không đổi; (d) không `cam` lặp liền nhau.
- Spec không bật `cine_auto` (topic cũ) → HTML y hệt trước.
- `PYTHONIOENCODING=utf-8 python -m pytest tests -q` xanh (lỗi quyền thư mục tạm của sandbox thì ghi rõ).
- Cập nhật `motion/long/README.md` mục cine_auto (luật cửa sổ, dựng từng chương).

## Không làm
Không render, không commit/push/đăng, không đụng credentials, không sửa `data/long/*` thật. Ghi file bằng Python utf-8 và grep diff tìm `?` thay chữ có dấu.

## Báo cáo
`docs/pm/tickets/GH-274-report-2.md` (tiếng Việt): thay đổi, số cửa sổ <3 kiểu trước/sau trên một Long thật đọc từ `data/long/` (chạy khô, không ghi output), kết quả test.
