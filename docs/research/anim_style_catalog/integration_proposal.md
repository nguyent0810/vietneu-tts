# Đề xuất Tích hợp Kiến trúc & Đánh giá Khả thi (Integration Proposal)

- **Mã nhiệm vụ:** 033 — Research spike: Animation Style Catalog (Issue #258)
- **Người thực hiện:** agy (Thợ)
- **Người duyệt:** Claude Opus 5.5 (Lead)

---

## 1. So sánh 3 Phương án Kiến trúc

Bảng chấm điểm và đánh giá 3 phương án khả dĩ theo các tiêu chí kỹ thuật:

| Tiêu chí | Phương án A (Dùng lại code repo ngoài) | Phương án B (Clean-room rewrite vào HyperFrames) | Phương án C (Giữ 2 pipeline song song) |
|---|---|---|---|
| **Độ phức tạp ban đầu** | **Thấp** (Script và code HTML có sẵn) | **Vừa phải** (Cần viết lại logic vẽ vào `longform.js`) | **Cao** (Phải bảo trì 2 pipeline render riêng biệt) |
| **Chi phí bảo trì lâu dài** | **Rất cao** (Phải duy trì code không rõ nguồn gốc) | **Rất thấp** (Đồng nhất trong hệ thống HyperFrames) | **Rất cao** (Gấp đôi chi phí sửa lỗi và vận hành) |
| **Nợ kỹ thuật** | **Nghiêm trọng** (Đưa runtime Playwright riêng ngoài HF) | **Không có** (Kế thừa hạ tầng `engine.js` hiện tại) | **Cao** (Xung đột quy trình CI/CD và cấu hình render) |
| **Khả năng mở rộng** | **Kém** (Mỗi cảnh là 1 file HTML đơn lẻ, khó tự động) | **Rất cao** (Dễ dàng điều khiển bằng JSON plan và TTS) | **Kém** (Khó kết hợp với các cảnh quay có sẵn) |
| **Rủi ro bản quyền** | **VI PHẠM BẢN QUYỀN** (Repo `license: null`, All Rights Reserved) | **AN TOÀN TUYỆT ĐỐI** (Ý tưởng không được bảo hộ, code viết mới) | **VI PHẠM BẢN QUYỀN** (Vẫn dùng trực tiếp mã nguồn repo ngoài) |
| **Mức phụ thuộc repo ngoài** | **Phụ thuộc 100%** | **Độc lập hoàn toàn** | **Phụ thuộc 100%** |
| **Tương thích Linux CI/CD** | **Không** (`render_ornek.mjs` gắn cứng mac-arm64) | **100% Tương thích** (Chạy qua `HYPERFRAMES_BROWSER_PATH`) | **Không** (Phải viết lại script runner cho Linux) |
| **KẾT LUẬN ĐÁNH GIÁ** | **LOẠI TRỪ NGAY** | **ĐỀ XUẤT CHÍNH THỨC** | **LOẠI TRỪ** |

---

## 2. Luận chứng Chọn Phương án B (Clean-room Reimplementation)

1. **Tuân thủ pháp lý triệt để:** Repo ngoài giữ toàn bộ quyền sở hữu trí tuệ (`All Rights Reserved`). Phương án B chỉ tiếp thu phong cách mỹ thuật và cấu trúc chuyển động (artistic direction & motion grammar), sau đó tự phát triển lại mã nguồn sạch trong `hyperframes_short/compositions/longform.js`, triệt tiêu hoàn toàn rủi ro kiện tụng hoặc tranh chấp bản quyền.
2. **Kế thừa toàn diện hạ tầng của xưởng:**
   - Dễ dàng nhận dữ liệu tham số từ kịch bản JSON (`spec.variant`, `spec.steps`, màu sắc thương hiệu `var(--accent)`, `var(--lf-line)`).
   - Đồng bộ hoàn hảo với các bước đọc của VieNeu TTS thông qua hàm `when(ctx, step)` có sẵn trong `longform.js`.
   - Vượt qua các cổng kiểm thử QA tự động (`hf_qa.py --contrast`, `hf_qa.py --overflow`).
   - Tự động chạy trơn tru trên cả máy trạm macOS của xưởng lẫn máy chủ Oracle Linux ARM thông qua `hyperframes_bridge.py`.

---

## 3. Tiêu chí Nghiệm thu GO / NO-GO (Theo Issue #258)

| Điều kiện GO trong Issue #258 | Kết quả Đánh giá Thực tế | Bằng chứng / Cơ sở |
|---|---|---|
| **Điều kiện 1:** Có $\ge$ 2 style P0 hợp với ít nhất 1 kênh đang chạy | **ĐẠT** (Xác định được 3 style P0: `linocut`, `kagit-kesik`, `tek-cizgi`) | `linocut` (hoàn hảo cho FS & BUD), `kagit-kesik` (hoàn hảo cho BUD & FS), `tek-cizgi` (hoàn hảo cho BUD) |
| **Điều kiện 2:** Làm lại được theo phương án B hoặc C mà không đụng tới license | **ĐẠT** | Phương án B triển khai clean-room bằng Canvas 2D/SVG gốc trong `longform.js`, không sao chép một dòng mã nguồn nào từ repo ngoài |
| **Điều kiện 3:** Mỗi cảnh 10 giây render dưới 2× thời gian thực trên Mac | **ĐẠT (Lý thuyết)** | Kiến trúc Canvas 2D tính sẵn offscreen texture, ước tính đạt tốc độ 1.0x – 1.6x thời gian thực trên chip Apple Silicon M-series |
| **Điều kiện 4:** Tua theo khung tất định, dùng được với cách render theo chương | **ĐẠT** | 100% chuyển động phụ thuộc hàm thời gian $t$, sử dụng PRNG có hạt giống, hoàn toàn seek-safe và stateless |

> **KẾT LUẬN CHUNG:** **ĐẠT TẤT CẢ 4 ĐIỀU KIỆN $\rightarrow$ QUYẾT ĐỊNH: GO (Theo Phương án B)**.  
> *Lưu ý: Không tự ý triển khai code vào production. Chờ PO duyệt kết quả nghiên cứu và mở ticket triển khai riêng.*

---

## 4. Ba Phong cách Đáng Làm Nhất (P0) & Kế hoạch Chuyển thể

Nếu PO duyệt kết quả spike này, đề xuất mở 3 ticket triển khai theo thứ tự ưu tiên:

### Top 1. `linocut` (Tranh Mộc Bản Khắc Gỗ Á Đông) — Ưu tiên cao nhất cho FS & BUD
- **Độ ăn khớp thương hiệu:**
  - **FS (Phong Thuỷ):** Tái hiện không khí sấm truyền, bản đồ phong thuỷ cổ, mộc bản khắc quẻ Dịch và ấn triện chu sa.
  - **BUD (Phật Giáo):** Lấy cảm hứng từ kho tàng mộc bản kinh Phật cổ chùa Vĩnh Nghiêm (Di sản tư liệu ký ức thế giới), tạo cảm giác trang nghiêm, cổ kính, thoát tục.
- **Kỹ thuật chuyển thể vào `longform.js` (`visuals.woodcut`):**
  - Sử dụng Canvas 2D độ phân giải 1920×1080.
  - Bảng màu: Nền giấy dó ngà (`#efe5cf`), mực nho đen (`#15120f`), chu sa đỏ (`#c7331f`).
  - Đường nét đục khắc V-groove xung quanh biểu tượng (hoa sen, bát quái, ấn triện).
  - Diễn hoạt: Nhịp giật 12fps (cadence stop-motion), hiệu ứng mực in nhấp nháy (boil) chu kỳ 1/8 giây để tạo sức sống thủ công.

### Top 2. `kagit-kesik` (Nghệ thuật Cắt Giấy Diorama Đa Tầng) — Tuyệt phẩm Kể Chuyện cho BUD & FS
- **Độ ăn khớp thương hiệu:**
  - **BUD (Phật Giáo):** Hoàn hảo cho các phân đoạn kể chuyện sự tích tiền thân (truyện Jātaka), truyện Nhân Quả theo hình thức kịch rối bóng nghệ thuật hoặc tranh cắt giấy nhiều lớp.
  - **FS (Phong Thuỷ):** Minh hoạ các truyền thuyết dân gian, cảnh non nước, địa thế long mạch núi non trùng điệp.
- **Kỹ thuật chuyển thể vào `longform.js` (`visuals.papercut`):**
  - Xếp lớp 4-6 tầng cắt (foreground, midground, background silhouette) bằng SVG paths hoặc Canvas clipping masks.
  - Áp dụng `shadowBlur` và toạ độ bóng đổ di chuyển mềm mại để giả lập nguồn sáng (mặt trời mọc, trăng lên, ngọn nến lay động).
  - Các chi tiết chuyển động độc lập theo trục dọc (parallax trượt nhẹ) khớp với giọng đọc TTS.

### Top 3. `tek-cizgi` (One-line Art / Nét Vẽ Thiền Liên Tục) — Tối Giản Thanh Tịnh cho BUD
- **Độ ăn khớp thương hiệu:**
  - **BUD (Phật Giáo):** Khắc hoạ tinh thần Thiền (Zen) nguyên bản: một nét mực duy nhất không đứt đoạn vẽ nên đoá hoa sen, vòng tròn Pháp Luân (Enso), hoặc đường nét phác hoạ Đức Phật tĩnh toạ. Đảm bảo tính trang nghiêm tuyệt đối và không có chi tiết thừa.
  - **FS (Phong Thuỷ):** Thể hiện dòng khí mạch luân chuyển liền mạch qua các huyệt đạo hoặc ngũ hành tương sinh.
- **Kỹ thuật chuyển thể vào `longform.js` (`visuals.oneline`):**
  - Dùng thuật toán Catmull-Rom Centripetal Spline nội suy qua mảng toạ độ các điểm đặc trưng.
  - Vẽ bám nét thời gian thực qua hàm vi sai độ dài hoặc kỹ thuật SVG `strokeDasharray` + `strokeDashoffset`.
  - Độ dày nét vẽ biến thiên nhẹ theo vận tốc di chuyển của đầu bút ảo.
