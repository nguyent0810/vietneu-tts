# GH-173: QA khung hình nhãn VÍ DỤ GIẢ ĐỊNH (bản code Codex)

Thư mục này là worktree riêng, chứa code nhãn mới, chưa merge:
- `motion/hf/assets/engine/casefile.js` và `casefile.css`, lớp `.hypo-*`;
- preflight trong `motion/stier/build.py`.

Xem `docs/pm/tickets/GH-173-codex-report.md`. Spec bật nhãn bằng `"hypo": true` (tuỳ chọn thêm `"hypo_sub"`).

**Việc:**
1. Chọn 3 spec Short đã có trong `data/stier/specs/`: một CK, một MIM, một CL. Ưu tiên spec đang có chữ "giả định" trong `sub`/`note`, và nhiều loại cảnh (chart, counter, cards3d, ledger).
2. Chép từng spec sang `data/stier/specs/_qa173_<kenh>.json`. Thêm `"hypo": true` vào 2–3 cảnh có ví dụ giả định. Đừng sửa spec gốc.
3. Chạy `python motion/stier/build.py` ở chế độ preflight cho 3 spec thử (đọc `motion/stier/README.md` để biết cờ đúng). Ghi lại cảnh báo của spec gốc so với spec thử: spec gốc phải có cảnh báo, spec thử thì hết cảnh báo ở các cảnh đã thêm hypo.
4. Dựng và chụp khung QA lúc nhãn đang hiện, cho từng cảnh có hypo: `qa_t*.png` hoặc snapshot của hyperframes (README có cách). Không cần render mp4 đầy đủ nếu chụp được khung.
5. Soát mỗi ảnh:
   - nhãn rõ nét;
   - cỡ chữ bằng hoặc lớn hơn subtitle;
   - không đè subtitle, kicker hay nội dung chính của cảnh;
   - không nằm dưới cột nút bên phải (x > 900);
   - đúng kiểu từng kênh: CK ruy-băng vàng, MIM khung lệnh cyan, CL băng giấy hiện trường;
   - dấu tiếng Việt đủ.

   Ghi các lỗi bố cục theo từng loại cảnh.

**Được ghi:** `data/stier/specs/_qa173_*.json`, thư mục output QA do script tạo, và báo cáo `docs/pm/tickets/GH-173-qa-report.md` (UTF-8). Không sửa engine hay code, không commit, không upload.

**Báo cáo:** bảng cảnh × kết quả (đạt / lỗi gì), đường dẫn ảnh QA, cảnh báo preflight trước và sau.
