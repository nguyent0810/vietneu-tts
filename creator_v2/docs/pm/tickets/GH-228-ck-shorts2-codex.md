# GH-228: lô Short CK 2 (11 Short, 20–23/11)

**Lịch:** 3 bài mỗi ngày lúc 17:30, 19:00, 22:00 giờ VN, ngày 20, 21, 22/11; ngày 23/11 có 2 bài lúc 17:30 và 19:00.

**Mẫu hình đã đạt:** 9 spec vừa đăng (danh sách trong `docs/pm/tickets/GH-180-respec2-report.md`), ví dụ `data/stier/specs/ck-e6-tro-cap-540-nghin.json` và `ck-dien-sinh-hoat-bac-mot-1901.json`. Hình xem ở `output/stier/<slug>/final_sheet.jpg`. Làm đúng như vậy:
- ≥ 5 loại cảnh;
- `cards3d` và counter hoặc slam cho số lớn;
- đúng 1 cảnh ảnh, mỗi bài một ảnh khác nhau, từ kho chung `output/asset_library/` tag `ck`. Không lặp ảnh đã dùng cho 9 bài trước;
- luật phối cảnh của preflight phải đạt.

**Nội dung, 11 bài:**
- **L, 6 bài:** 2 bài cho mỗi Long CK lên trong tuần, mỗi bài lấy 1 con số hoặc 1 tình huống thật trong `data/long/<topic>/script.md`:
  - `ck-f1-tro-cap-that-nghiep` (18/11);
  - `ck-f2-vien-phi-bhyt` (20/11);
  - `ck-f4-vo-chong-chia-tien` (22/11).
- **S, 5 bài:** một con số tiền bạc thật cộng một quyết định đời thường, ví dụ giá vàng, lãi tiết kiệm, phí, thuế, BHXH. Số liệu từ nguồn chính thức đã mở: NHNN, GSO, văn bản luật. Không trùng các Short CK đã có; kiểm bằng `grep` tiêu đề trong `data/stier/specs/ck-*.json`.

**Luật lời** (`docs/pm/2026-10-12-shorts-analysis.md` §7):
- hook ≤ 9 từ;
- 25–40 giây;
- một ý, kết bằng câu chốt;
- không câu hỏi, không CTA;
- tiêu đề ≤ 60 ký tự;
- ví dụ giả định thì có `hypo`;
- mô tả có câu miễn trừ CK và nguồn URL.

**Việc:**
- viết 11 spec bằng script Python `json.dump(ensure_ascii=False)`, `encoding="utf-8"`;
- ghi lời và nguồn vào `docs/pm/tickets/GH-228-ck-shorts2-lines.md`;
- chạy `python motion/stier/build.py --preflight <slug>` cho cả 11 đến khi OK;
- chạy lệnh kiểm mất dấu.

**Không:** render, enqueue, upload, commit.

**Báo cáo** `docs/pm/tickets/GH-228-ck-shorts2-report.md`.
