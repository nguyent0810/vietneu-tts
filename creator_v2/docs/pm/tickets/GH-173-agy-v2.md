# GH-173 vòng 2: sửa 9 mockup nhãn VÍ DỤ GIẢ ĐỊNH

Lead đã soát `docs/pm/mockups/173/*.png` vòng 1 (báo cáo `docs/pm/tickets/GH-173-report.md`). Sửa đúng các lỗi sau trên chính 9 file đó, giữ nguyên ý tưởng từng kiểu:

1. **Chụp ở trạng thái cuối của hiệu ứng.** Ở nhiều ảnh nhãn còn mờ vì chụp giữa animation (ck_ribbon, ck_badge_gold, mim_terminal_bracket, mim_glass_cyber...). Thêm chế độ tĩnh: khi URL có `?static` thì tắt animation và hiện mọi thứ ở trạng thái cuối. Chụp PNG với `?static`.
2. **Cỡ chữ nhãn ≥ 62px**, bằng cỡ subtitle `#caps .cap` đo được. Tiêu chí của chủ kênh là nhãn không nhỏ hơn dòng phụ, và subtitle là dòng phụ. Dòng chữ nhỏ đi kèm nhãn (eyebrow/meta) được nhỏ hơn, nhưng **chữ "VÍ DỤ GIẢ ĐỊNH" phải ≥ 62px**. Nếu dài quá một dòng thì xuống dòng hoặc thu hẹp letter-spacing, không được giảm cỡ.
3. **Bỏ chữ kiểu máy móc hay giả kỹ thuật:** "SIMULATION ENVIRONMENT", "SYS_SIM", mã số giả, tên model/bot. Dòng phụ đi kèm nhãn (nếu có) chỉ là tiếng Việt tự nhiên, ví dụ "Số liệu minh họa".
4. **ck_badge_gold:** chữ "6,75 tr" đang đè lên tiêu đề biểu đồ, sửa cho hết đè.
5. **Font tiếng Việt:** kiểm tra dấu (Ầ Ệ Ở Ữ) hiển thị đúng với Playfair Display. Nếu font thiếu glyph thì đổi sang font serif khác có đủ dấu tiếng Việt.
6. **Vùng an toàn:** nhãn không đè subtitle (top 1478px) và không nằm dưới cột nút bên phải (x > 900px).

**Được ghi:** chỉ `docs/pm/mockups/173/*` và `docs/pm/tickets/GH-173-report-v2.md`. Không sửa engine, stier, factory, tests. Không commit.

**Báo cáo v2:** bảng 9 kiểu với cỡ chữ nhãn mới (đo bằng `getComputedStyle`), xác nhận ảnh chụp ở trạng thái `?static`, các chữ đã bỏ, font đã đổi (nếu có).
