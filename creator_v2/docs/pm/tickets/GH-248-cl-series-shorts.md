# GH-248 — CL Short lô 3: chỉ làm SERIES (chủ kênh duyệt 10/11)

Đọc trước: `docs/pm/2026-11-10-cl-diagnosis.md` (vì sao: Short CL kẹt trần ~1.000 views, vụ án Âu–Mỹ rời rạc không ra sub). Brief mẫu cũ: `docs/pm/tickets/GH-248-trend-shorts-agy.md` (luật chung vẫn áp dụng). Spec mẫu cùng kênh: `data/stier/specs/cl-hoa-than-*.json`.

## Lô này: 12 spec, đăng 2 bài/ngày 25–30/11
**Series A — "Hồ sơ Bao Chửng" (Short L, nối Long Bao Thanh Thiên đã công khai 08/11), 3 bài**, slug `cl-bao-s2-<x>`. Mỗi bài một chi tiết hồ sơ thật (Tống sử / Bao Chửng truyện, nguồn Wikipedia/Wikisource + bài học thuật), KHÔNG lấy tình tiết phim truyền hình làm sự thật. Không trùng các spec `cl-bao-*` sẵn có.
**Series B — "Hồ sơ Đông Lăng" (Short L, nối Long Đông Lăng công khai 22/11), 3 bài**, slug `cl-dong-lang-<x>`. Chỉ đăng SAU 22/11. Dữ kiện lấy từ `data/long/dong-lang/script.md` + factcheck.md (đã kiểm), không thêm chi tiết chưa có nguồn.
**Series C — "Vụ án châu Á" (Short S), 6 bài**, slug `cl-a-<x>`: Nhật, Hàn, Trung Hoa cận đại, Đông Nam Á (Thái, Malaysia, Singapore, Indonesia, Philippines), Việt Nam thời Pháp thuộc. Ưu tiên lừa đảo, trộm báu vật, vượt ngục, gián điệp, phá án bằng chứng cứ. LOẠI khủng bố, thảm sát, giết người hàng loạt, máu me, nạn nhân còn sống/người thân còn sống bị nêu tên.

## Luật 3 giây đầu (bắt buộc, quyết định 10/11)
- Cảnh 0: ẢNH (chân dung nhân vật hoặc hiện vật/hồ sơ) sáng (luma ≥ 50) + MỘT con số hoặc mốc lớn trên ảnh (vd "1793", "102 KÝ VÀNG", "3 LẦN VƯỢT NGỤC"). Không chữ trên nền trống.
- `lines[0]` ≤ 9 từ, có con số hoặc tên riêng của tiêu đề, là mâu thuẫn/nghịch lý ("Quan thanh liêm nhất triều Tống bị kiện tham ô"), không mở bằng "Bạn có biết".
- Câu 2 là hành động/chi tiết cụ thể, KHÔNG định nghĩa khái niệm.
- Series A/B: nhãn nhỏ ở cảnh 0 "HỒ SƠ BAO CHỬNG · 1/3" (hoặc Đông Lăng); câu cuối mời xem bản dài bằng một câu tự nhiên, không "đăng ký kênh".
- Tiêu đề ≤ 60 ký tự, mở bằng nghịch lý/con số, có tên riêng.

## Ảnh và nguồn
- Chỉ ảnh Wikimedia Commons PD/CC0 (preflight kiểm `license_ok`), mỗi bài ≥ 4 ảnh khác nhau, không dùng lại ảnh của spec khác. KHÔNG bịa tên file Commons: mở trang file thật, chép đúng tên.
- Mọi số/ngày lấy từ nguồn gốc, ghi URL vào `sources` của spec. `publish_at` để trống.

## Cổng
`PYTHONIOENCODING=utf-8 .venv\Scripts\python.exe motion/stier/build.py --preflight <slug>` → OK cho cả 12 bài (không dùng `--allow-hook`).
Ghi file bằng Python utf-8, `json.dump(ensure_ascii=False, indent=1)`; grep kiểm không có `?` thay chữ có dấu. Không render, không enqueue, không commit, không đổi nhánh, không sửa spec khác.

## Báo cáo
`docs/pm/tickets/GH-248-cl-series-shorts-report.md`: bảng slug · series · tiêu đề · lines[0] · ảnh cảnh 0 · nguồn chính · kết quả preflight.
