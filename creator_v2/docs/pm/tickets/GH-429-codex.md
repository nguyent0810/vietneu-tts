# GH-429 (Codex): 10 giây đầu Long là hình động, không thẻ chữ — port PR #418

Đọc issue #429 (chép dưới), PR #418 ở gốc repo (`../long_script_lint.py` hàm `opening_visual_issues`, `../tests/test_long_script_lint.py`), `motion/long/opening_gate.py` (O1–O8, đã có O7/O8 từ #411 và tham số `out_root`), `motion/long/scene_params.py` (tên loại cảnh), `docs/pm/storytelling-guide.md` mục "Cửa sổ sốc".

## Việc (chỉ CẢNH BÁO, không chặn)
1. `opening_gate.py`, dùng giây thật (timing.json) nếu có, không thì ước lượng như O7:
   - **O9 `mo_hinh_tinh`:** cảnh đầu tiên (t0 = 0) không có `vid` và không phải photo/pano có `move`/`cam`/`tone`+chuyển động (xem cách engine nhận chuyển động máy: key `move` của photo, `cine`).
   - **O10 `mo_the_chu`:** có cảnh thẻ chữ bắt đầu trước 10 s: type thuộc {slam, kinetic, quote, counter, ledger, bars, waterfall, file, source, myth, question, date, chapter} — riêng `chapter` ở chương ch00 cũng tính. Ghi tên cảnh + giây.
   - **O11 `mo_cau_soc`:** 3 câu đầu (lines[0:3] của ch00) không có câu hỏi/câu móc/nghịch lý (tái dùng bộ dấu hiệu O7).
2. In cùng chỗ O7/O8.
3. Test mới (khuôn #418/#411): đủ ba trường hợp mỗi luật, theo giây thật.
4. Chạy thử (chỉ đọc, `--out-root "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\output\long"`) trên `cl-dich-nhan-kiet`, `mim-binance-6-3-ty-20-phut`, `ck-c8-10-trieu-mua-duoc-gi` (render đã dọn nên có thể chỉ còn timing; nếu không có timing thì ước lượng) — ghi kết quả.
5. `docs/pm/storytelling-guide.md`: thêm một dòng dưới "Cửa sổ sốc" tham chiếu O9–O11.

## Luật
- Chỉ sửa: `motion/long/opening_gate.py`, test mới trong `tests/`, `docs/pm/storytelling-guide.md`.
- **Ghi file bằng Python `open(..., 'w', encoding='utf-8')`, không PowerShell.** Không có `??` mới trong diff.
- Chỉ chạy test liên quan + `tests/test_console.py`; Lead chạy toàn bộ. Không render, không commit/push/đăng, không đọc credentials.

## Báo cáo
`docs/pm/tickets/GH-429-report.md` (tiếng Việt, Python utf-8).
