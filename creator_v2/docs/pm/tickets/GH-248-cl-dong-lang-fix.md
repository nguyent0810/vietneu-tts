# GH-248 — Sửa 3 spec "Hồ sơ Đông Lăng" (Lead review 10/11)

Bối cảnh: `docs/pm/tickets/GH-248-cl-series-shorts.md` (luật 3 giây đầu) và báo cáo `GH-248-cl-series-shorts-report.md`. Lead đã duyệt series A (Bao Chửng) và C (vụ án châu Á). Series B chưa đạt vì hai lý do dưới đây.

## Spec cần sửa
`data/stier/specs/cl-dong-lang-min-1928.json`, `cl-dong-lang-da-min-chau.json`, `cl-dong-lang-tu-1947.json`.

## Lỗi
1. **Ảnh.** Cả ba bài dùng đồ sứ đời Thanh và sơ đồ viên tẩm phi tần không liên quan đến vụ án. Luật cảnh 0 là chân dung nhân vật hoặc hiện vật của chính vụ án.
   - Thay bằng ảnh Commons PD/CC0 có liên quan trực tiếp. Gợi ý: chân dung Tôn Điện Anh (Sun Dianying), chân dung/ảnh chụp Từ Hi, ảnh Càn Long, ảnh Thanh Đông Lăng (Eastern Qing Tombs: Dụ Lăng, Định Đông Lăng), ảnh Tưởng Giới Thạch / Tống Mỹ Linh nếu lời có nhắc.
   - Cảnh 0 của mỗi bài phải là chân dung hoặc ảnh lăng thật.
   - Mỗi bài ≥ 4 ảnh. Không trùng giữa 3 bài. Không trùng ảnh Long `data/long/dong-lang` nếu tránh được.
   - Mở trang file Commons thật, chép đúng tên, ghi giấy phép.
2. **Thứ tự kể.** `cl-dong-lang-min-1928` nhảy lùi thời gian: câu 5 "Ngày một tháng bảy…" nằm sau "ngày bảy tháng bảy". Kể theo một mạch:
   - câu 1 là nghịch lý;
   - các câu sau đi theo thời gian;
   - câu cuối mời xem bản dài.
   - Không liệt kê các câu rời không nối với nhau. Hai bài kia soát cùng lỗi này.

## Giữ nguyên
- Mọi dữ kiện chỉ lấy từ `data/long/dong-lang/script.md` và `factcheck.md`.
- `lines[0]` ≤ 9 từ. Tiêu đề ≤ 60 ký tự. Nhãn `HỒ SƠ ĐÔNG LĂNG · n/3`.
- `publish_at` để trống.

## Cổng
- `PYTHONIOENCODING=utf-8 .venv\Scripts\python.exe motion/stier/build.py --preflight <slug>` → OK cho cả 3 bài, không dùng `--allow-hook`.
- Ghi file bằng Python utf-8, `json.dump(ensure_ascii=False, indent=1)`. Grep kiểm không có `?` thay chữ có dấu.
- Không render, không enqueue, không commit. Không sửa spec khác.

## Báo cáo
`docs/pm/tickets/GH-248-cl-dong-lang-fix-report.md`: bảng slug · ảnh mới (tên file + giấy phép) · lines mới · kết quả preflight.
