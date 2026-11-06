# GH-228: lô Short CK 2, 8 bài còn lại (viết lời và spec)

Đã có 3 bài: `ck-f1-60-phan-tram-luong-dong`, `ck-f1-bac-thang-tro-cap`, `ck-f2-bhyt-nam-nam-lien-tuc`, xếp lịch 20/11 lúc 17:30, 19:00, 22:00. Codex không viết được phần còn lại: lời tiếng Việt bị mất dấu.

Làm đúng brief `docs/pm/tickets/GH-228-ck-shorts2-codex.md`, phần nội dung, luật lời và mẫu hình. **8 bài:**
- 1 bài L cho `ck-f2-vien-phi-bhyt`;
- 2 bài L cho `ck-f4-vo-chong-chia-tien`;
- 5 bài S.

**Lịch** (giờ VN):
- 21/11: 17:30, 19:00, 22:00;
- 22/11: 17:30, 19:00, 22:00;
- 23/11: 17:30, 19:00.

**Hình:**
- ≥ 5 loại cảnh;
- số lớn bằng cards3d, counter hoặc slam;
- đúng 1 cảnh ảnh, lấy từ kho chung `output/asset_library/` tag `ck`, không trùng 12 ảnh đã dùng (xem `GH-180-respec2-report.md` và 3 spec trên);
- luật phối cảnh của preflight phải đạt.

Viết spec bằng Python `json.dump(ensure_ascii=False)`, `encoding="utf-8"`. Chạy `python motion/stier/build.py --preflight <slug>` đến khi OK. Không render, không commit.

**Báo cáo** `docs/pm/tickets/GH-228-ck-shorts2c-report.md`.
