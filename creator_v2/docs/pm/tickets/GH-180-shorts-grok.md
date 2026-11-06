# GH-180: lời cho lô Short CK 13–15/11 (9 Short, 3 mỗi ngày)

Lịch Short CK chỉ kéo tới 12/11. Luật dừng của đợt thử 5/ngày sẽ đánh giá ngày 12/11, nhưng nhịp tối thiểu vẫn là 2–3 Short mỗi ngày, nên lô này làm trước.

**Đọc:**
- `docs/pm/2026-10-12-shorts-analysis.md` §7 (8 luật Short: hook ≤ 9 từ, một ý, kết bằng câu chốt, không CTA, không câu hỏi trong lời);
- skill `../.claude/skills/shorts-studio/SKILL.md`;
- 3–4 spec CK đang thắng trong `data/stier/specs/`. Bản tin Studio 05/11: *lạm phát là lãi kép* (3.210 lượt xem) và *bảo hiểm tiền gửi 350 triệu* (2.271). Tìm spec có slug tương ứng.

**Loại Short:**
- **S** (kéo người đăng ký) và **L** (kéo người xem sang Long), theo memory chủ kênh 28/10.
- L phải là phần nối thật của Long, không phải trailer.

**9 Short:**
- **L, 2 Short mỗi Long**, cho 3 Long sắp lên. Đọc `data/long/<topic>/script.md` của từng Long để lấy một con số hoặc một tình huống thật trong đó:
  - `ck-e5-thue-tncn-2026` (lên 13/11);
  - `ck-e6-luong-huu-rut-mot-lan` (lên 15/11);
  - `ck-a2-luong-va-lam-phat` (lên 16/11).
- **S, 3 Short**, theo công thức đang thắng: một con số tiền bạc thật cộng một quyết định đời thường của người Việt.

**Mỗi Short ghi:**
- slug đề xuất và loại S/L;
- Long nối tới (nếu là L);
- hook (≤ 9 từ);
- lời đọc 25–40 giây (khoảng 90–140 âm tiết);
- câu chốt;
- tiêu đề ≤ 60 ký tự;
- cảnh nào là ví dụ giả định (khi đó cảnh có `"hypo": true`, theo nhãn mới #173);
- nguồn kèm URL đã mở cho mọi con số.

Ví dụ giả định thì ghi rõ là ví dụ, không trình bày như số thật.

**Được ghi:** chỉ `docs/pm/tickets/GH-180-shorts-lines.md` (lời) và báo cáo `docs/pm/tickets/GH-180-shorts-report.md` (UTF-8). Không tạo spec (Codex lắp sau), không render, không commit, không đổi lịch.
