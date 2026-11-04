# GH-33 · Codex: viết 12 spec Short pilot tin nóng tuần 45 (6 MIM, 6 CK)

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/33.

## Đầu vào (Lead đã review)
- MIM: `docs/pm/tickets/GH-33-MIM-pack.md`, `GH-33-MIM-facts.json`
- CK: `docs/pm/tickets/GH-33-CK-pack.md`, `GH-33-CK-facts.json`
- Mẫu spec SS-tier mới nhất: `data/stier/specs/mim-p6-feed-cua-ban.json`, `mim-p5-recsys-2016.json` (MIM); `ck-b4-bay-tram-thanh-tam-tram.json`, `ck-p1-thue-5-nam-cong-lai.json` (CK). Xem định dạng trong docstring `motion/stier/build.py`.
- Chuẩn Short:
  - `motion/stier/README.md`;
  - `docs/pm/2026-10-12-shorts-analysis.md` §7: hook ≤ 9 từ, một insight, kết bằng cú chốt, không CTA, không câu hỏi trong lời đọc;
  - chuẩn mix: `"mix": true`; cảnh xen kẽ chữ theo nhịp, footage/ảnh tự do, data viz, `board`/`cards3d`; clip có `"win"`; look xoay qua `motion/stier/looks.py`, không lặp look hay chuỗi cảnh giữa hai Short liền nhau;
  - âm thanh: `music_gain` 0.18, `music_duck` 3, `sfx_gain` 0.36.

## Được ghi
- `data/stier/specs/<slug>.json` cho đúng 12 slug trong hai file facts
- báo cáo `docs/pm/tickets/GH-33-specs-report.md`

**Không:** render, TTS, upload, enqueue, sửa code, sửa spec khác, commit.

## Việc
1. **Mỗi Short một spec:**
   - `title` = phương án title số 1 trong pack;
   - `lines[0]` = đúng hook 3 s trong pack;
   - các câu tiếp theo theo dàn ý;
   - chữ khung đầu (cảnh 0) = đúng chữ khung đầu trong pack, xuất hiện ngay giây 0.
2. **Dữ kiện.**
   - Mọi số, tên, ngày trong `title`/`lines`/chữ trên màn hình phải có trong facts JSON, có nguồn. Mục "CHƯA KIỂM" không được dùng.
   - `sources` liệt kê URL nguồn sơ cấp và nguồn độc lập.
   - Nguồn FBI (`fbi.gov/...binance-attack`) Lead chưa mở được: nếu là nguồn duy nhất cho một khẳng định thì dựa vào nguồn độc lập đã mở (VnExpress, CoinDesk) và ghi rõ trong báo cáo.
3. **Riêng CK:**
   - `description` có câu "Nội dung giáo dục, không phải tư vấn đầu tư.";
   - số ví dụ ghi VÍ DỤ GIẢ ĐỊNH;
   - không khuyến nghị mua bán, kể cả vàng và crypto.
4. **Hình.**
   - Chỉ dùng ảnh Wikimedia Commons tự do, clip Pexels (`vid`) và cảnh đồ họa có sẵn trong engine.
   - Không ảnh hay clip báo chí, không logo hay ticker công ty trên clip CK (`feedback-clip-sheet-before-render`).
   - Ảnh hoặc clip chưa có trong `output/stier/<slug>/` thì chỉ ghi id hoặc File; agy sẽ tải lúc render.
5. **Kiểm.** Chạy `python motion/stier/script_lint.py <slug>` cho cả 12 slug và sửa đến hết LỖI. Nếu có thể chạy `build.py --no-render` mà không cần TTS hay mạng thì chạy để bắt lỗi neo chữ; không chạy được thì ghi lại.

## Báo cáo
Mỗi slug ghi:
- title, hook, look;
- kết quả lint;
- các khẳng định kèm nguồn;
- ảnh/clip cần tải.

Liệt kê mọi chỗ phải lệch khỏi pack, kèm lý do.
