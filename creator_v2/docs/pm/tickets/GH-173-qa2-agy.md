# GH-173: QA lại khung hình nhãn (vòng 2)

Worktree này có code nhãn vòng 2: cảnh có `hypo` thì nội dung cards3d, table, board, kinetic được đẩy xuống dưới nhãn hoặc thu nhỏ. Xem `docs/pm/tickets/GH-173-codex-v2-report.md`.

Vòng 1, Grok làm theo `docs/pm/tickets/GH-173-qa-grok.md`; kết quả và cách chụp ở `docs/pm/tickets/GH-173-qa-report.md`. Đọc kỹ cách chụp: snapshot hyperframes trên project `output/stier/_qa173/<kenh>/`, inline engine, đo bằng Chrome headless. Hai cảnh lỗi: CK cảnh 3 cards3d và MIM cảnh 2 cards3d (nhãn đè tiêu đề cảnh).

**Việc:**
1. Dựng lại 3 project QA từ `data/stier/specs/_qa173_*.json` bằng **code hiện tại** của worktree (engine đã đổi), theo cách của vòng 1.
2. Chụp lại đủ 7 cảnh có `hypo`, cùng thời điểm như vòng 1. Thêm 1 cảnh **không** có `hypo` để chứng minh bố cục cũ không đổi.
3. Đo:
   - hộp nhãn không giao với tiêu đề hoặc nội dung cảnh;
   - nội dung không chạm vùng subtitle (top 1478);
   - mép phải nhỏ hơn 900;
   - cỡ chữ nhãn ≥ subtitle;
   - nếu nội dung bị thu nhỏ, ghi tỉ lệ thu nhỏ và xác nhận chữ vẫn đọc được.
4. Ghi bảng cảnh × kết quả, đặt cạnh kết quả vòng 1.

**Được ghi:** `output/stier/_qa173/*` và báo cáo `docs/pm/tickets/GH-173-qa2-report.md` (UTF-8). Không sửa engine hay code, không commit.
