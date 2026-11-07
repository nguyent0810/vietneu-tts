# GH-228: lô Short CK 3 (20 Short, 24–30/11)

Mẫu chất lượng là lô 2, vừa đạt và đã đăng: 11 spec trong `docs/pm/tickets/GH-228-ck-shorts2c-report.md` và báo cáo 2b, hình ở `output/stier/<slug>/final_sheet.jpg`. Làm đúng như lô 2:
- ≥ 5 loại cảnh;
- số lớn bằng cards3d, counter hoặc slam;
- đúng 1 cảnh ảnh, lấy từ kho chung `output/asset_library/` tag `ck`, **không trùng 23 ảnh đã dùng** ở lô 1 và lô 2;
- luật phối cảnh của preflight phải đạt.

**Phá khuôn:** không bài nào dùng cùng chuỗi loại cảnh với bài khác trong lô. Đổi cảnh mở luân phiên giữa photo, counter, cards3d, chart, timeline.

**Lịch:** 3 bài mỗi ngày lúc 17:30, 19:00, 22:00 (giờ VN), từ 24/11 tới 29/11 (18 bài), cộng 30/11 lúc 17:30 và 19:00 (2 bài). Tổng 20 bài.

**Nội dung:**
- **L, 6 bài:** 2 bài cho mỗi Long CK sau, lấy một con số thật trong `data/long/<topic>/script.md` của Long đó:
  - `ck-c6-gia-tran-san-t2` (21/11);
  - `ck-i1-100-trieu-tiet-kiem-hay-vnindex` (19/11);
  - `ck-a2-luong-va-lam-phat` (16/11).

  Không làm L cho các Long chưa dựng.
- **S, 14 bài:** một con số tiền bạc thật cộng một quyết định đời thường. Số liệu lấy từ nguồn chính thức đã mở: NHNN, GSO hoặc Cục Thống kê, văn bản luật, BHXH, EVN. Không trùng đề với các Short CK đã có: grep tiêu đề trong `data/stier/specs/ck-*.json`. Chủ đề nên rải: tiết kiệm, vay, thuế, bảo hiểm, giá cả, lương, chứng khoán cơ bản (không nêu mã), tiêu dùng.

**Luật lời** (`docs/pm/2026-10-12-shorts-analysis.md` §7):
- hook ≤ 9 từ;
- 25–40 giây;
- câu ≤ 25 âm tiết;
- kết bằng câu chốt;
- không câu hỏi, không CTA;
- tiêu đề ≤ 60 ký tự;
- ví dụ giả định thì có `hypo`;
- mô tả có câu miễn trừ CK và nguồn URL.

**Làm:**
- viết spec bằng Python `json.dump(ensure_ascii=False)`, `encoding="utf-8"`;
- ghi lời và nguồn vào `docs/pm/tickets/GH-228-ck-shorts3-lines.md`;
- chạy `python motion/stier/build.py --preflight <slug>` cho cả 20 bài đến khi OK.

**Không:** render, enqueue, commit, đổi nhánh git.

**Báo cáo** `docs/pm/tickets/GH-228-ck-shorts3-report.md`: bảng 20 bài gồm slug, loại, ngày giờ, ảnh, chuỗi cảnh, preflight.
