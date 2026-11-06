# GH-173 — Báo cáo QA khung hình nhãn VÍ DỤ GIẢ ĐỊNH (Vòng 2)

QA xác nhận trên code nhãn vòng 2 của worktree (`casefile.js`, `casefile.css`, Google Fonts link). Không sửa engine hay code, không sửa spec gốc, không commit, không upload, không đổi lịch.

## 1. Dựng lại 3 project QA

Đã dựng lại toàn bộ 3 project QA trong `output/stier/_qa173/` (`ck`, `mim`, `cl`) theo đúng cách thức của vòng 1 nhưng áp dụng mã nguồn engine vòng 2 mới nhất:
- Cập nhật toàn bộ engine từ `motion/hf/assets/engine/` vào `output/stier/_qa173/<kenh>/assets/engine/`.
- Nhúng nội tuyến engine `beat.js` và `casefile.js` mới vào `index.html` của cả 3 project, bảo đảm StaticGuard của HyperFrames nhận diện `window.__timelines.main`.
- Cập nhật thẻ link Google Fonts hỗ trợ đầy đủ `Playfair Display:ital,wght@...;1,900` và `JetBrains Mono:wght@...;800`.
- Giữ nguyên `shots.json` và dữ liệu kịch bản `data.js` tương ứng với các spec thử `_qa173_ck.json`, `_qa173_mim.json`, `_qa173_cl.json`.

## 2. Cách chụp & Đo đạc

- Chụp bằng `hyperframes snapshot --at <giây> --no-end` (HyperFrames 0.9.19) trực tiếp trên từng project trong `output/stier/_qa173/<kenh>/`.
- Chụp đủ 7 cảnh có `hypo` tại đúng các mốc thời gian như vòng 1.
- Thêm 2 cảnh **không** có `hypo` (CK cảnh 0 kinetic tại t = 5.0s và MIM cảnh 4 board tại t = 26.0s) để đối chiếu chứng minh bố cục ban đầu không bị ảnh hưởng.
- Đo toạ độ khung hình thực tế bằng Chrome Headless (viewport chuẩn 1080×1920, `deviceScaleFactor: 1`), gọi `window.__timelines.main.seek(t)` và đo `getBoundingClientRect()` so với phần tử `#root`.
- Kiểm tra mật độ và toạ độ pixel sơn thực tế trên các ảnh chụp PNG bằng script phân tích hình ảnh (Pillow / NumPy).

---

## 3. Bảng cảnh × Kết quả (Đối chiếu Vòng 1 và Vòng 2)

Toạ độ pixel tính trên khung hình chuẩn 1080×1920. "Mép phải" là toạ độ x cực đại của hộp nhãn (gồm cả tab băng CL). Ngưỡng cột nút bên phải là x > 900. Vùng subtitle bắt đầu từ y = 1478.

| Kênh | Cảnh | Loại cảnh | Thời điểm | Hộp nhãn (L, T, R, B) | Mép phải | Cỡ chữ nhãn / Subtitle | Tỉ lệ scale / Shift | Khe hở tới tiêu đề | Đáy nội dung (max y) | Kết quả Vòng 1 | Kết quả Vòng 2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **CK** | 1 | chart | 20.00s | (52, 204, 638, 309) | 638 | 62px / 62px | 1.00 / 0px | 28px (dưới nhãn) | 1157 (cách sub 321px) | Đạt | **Đạt** |
| **CK** | 2 | counter | 25.24s | (64, 220, 636, 323) | 636 | 62px / 62px | 1.00 / 0px | 24px (dưới nhãn) | 850 (cách sub 628px) | Đạt | **Đạt** |
| **CK** | 3 | cards3d | 30.69s | (64, 220, 636, 358) | 636 | 62px / 62px | **0.9178 (91.8%)** / **+100.0px** | **21px (dưới nhãn)** | **1354 (cách sub 124px)** | **Lỗi: nhãn đè tiêu đề** | **ĐẠT (ĐÃ SỬA)** |
| **CK** | 0 | kinetic *(không hypo)* | 5.00s | *(Không nhãn)* | N/A | N/A / 62px | 1.00 / 0px | N/A | 970 (cách sub 508px) | N/A | **Đạt (Giữ nguyên bố cục)** |
| **MIM** | 2 | cards3d | 16.71s | (64, 220, 766, 366) | 766 | 62px / 62px | **0.9060 (90.6%)** / **+114.6px** | **24px (dưới nhãn)** | **1346 (cách sub 132px)** | **Lỗi: nhãn che hết tiêu đề** | **ĐẠT (ĐÃ SỬA)** |
| **MIM** | 3 | counter | 23.17s | (64, 220, 766, 366) | 766 | 62px / 62px | 1.00 / 0px | 20px (dưới nhãn) | 860 (cách sub 618px) | Đạt | **Đạt** |
| **MIM** | 4 | board *(không hypo)* | 26.00s | *(Không nhãn)* | N/A | N/A / 62px | 1.00 / 0px | N/A | 1342 (cách sub 136px) | N/A | **Đạt (Giữ nguyên bố cục)** |
| **CL** | 1 | ledger | 6.08s | (80, 226, 717, 361) [tab 722] | 722 | 62px / 62px | 1.00 / 0px | 60px (dưới nhãn) | 862 (cách sub 616px) | Đạt | **Đạt** |
| **CL** | 3 | counter | 16.08s | (80, 226, 717, 322) [tab 721] | 721 | 62px / 62px | 1.00 / 0px | 131px (dưới nhãn) | 860 (cách sub 618px) | Đạt | **Đạt** |

Ảnh snapshot lưu tại:
- CK: `output/stier/_qa173/ck/frames/` (`frame-00-at-20s.png`, `frame-01-at-25.24s.png`, `frame-02-at-30.69s.png`, `frame-03-at-5s.png`, `contact-sheet.jpg`).
- MIM: `output/stier/_qa173/mim/frames/` (`frame-00-at-16.71s.png`, `frame-01-at-23.17s.png`, `frame-02-at-26s.png`, `contact-sheet.jpg`).
- CL: `output/stier/_qa173/cl/frames/` (`frame-00-at-6.08s.png`, `frame-01-at-16.08s.png`, `contact-sheet.jpg`).

---

## 4. Chi tiết khắc phục lỗi 2 cảnh Cards3D

### CK Cảnh 3 (cards3d), t = 30.69s
- **Hiện trạng Vòng 1:** Ruy-băng vàng có `hypo_sub` ("PHÉP TÍNH MINH HỌA") chiếm hộp y = 220–358. Tiêu đề `.c3t` "MỖI THÁNG · NĂM ĐẦU" cố định tại y = 304–380 nên bị ruy-băng đè mất nửa bên trái (chữ "MỖI THÁNG").
- **Kết quả Vòng 2:**
  - Nhờ cơ chế `hypo-content`, toàn bộ nhóm nội dung được dời xuống với `--hypo-shift: 100.0px` và co nhẹ với `--hypo-scale: 0.9178` (91.8%).
  - Tiêu đề `.c3t` được dời xuống vị trí DOM y = 379–449.
  - Phân tích pixel thực tế: nét vàng ruy-băng kết thúc tại y = 355; nét trắng tiêu đề "MỖI THÁNG · NĂM ĐẦU" xuất hiện từ y = 376 đến y = 437 (14.581 pixel sáng).
  - Khoảng cách an toàn giữa đáy nhãn và đỉnh tiêu đề đạt **21px**.
  - Không có pixel nào bị đè. Toàn bộ chữ "MỖI THÁNG · NĂM ĐẦU" hiển thị đầy đủ, rõ nét.
  - Đáy của thẻ thứ 3 và dòng ghi chú chạm y = 1354, cách vùng subtitle (top 1478) tới **124px**, vượt xa ngưỡng an toàn tối thiểu (38px).

### MIM Cảnh 2 (cards3d), t = 16.71s
- **Hiện trạng Vòng 1:** Khung lệnh cyan cao 146px (y = 220–366). Tiêu đề ngắn "PHÉP TÍNH" (y = 304–380) bị nuốt trọn hoàn toàn bên dưới khung nhãn.
- **Kết quả Vòng 2:**
  - Nhóm nội dung được dời xuống với `--hypo-shift: 114.6px` và co với `--hypo-scale: 0.9060` (90.6%).
  - Tiêu đề `.c3t` dời xuống toạ độ DOM y = 390–459.
  - Phân tích pixel thực tế: viền cyan của nhãn kết thúc ở y = 364; nét chữ trắng của "PHÉP TÍNH" nằm từ y = 391 đến y = 443 (6.756 pixel sáng).
  - Khoảng cách an toàn giữa đáy nhãn và đỉnh tiêu đề đạt **24px** (theo đúng thiết kế `target = labelBottom + 24`).
  - Tiêu đề "PHÉP TÍNH" nằm hoàn toàn dưới khung cyan, rõ ràng, sắc nét.
  - Đáy thẻ và ghi chú chạm y = 1346, cách vùng subtitle (top 1478) tới **132px**.

---

## 5. Đánh giá 5 tiêu chí QA bắt buộc

1. **Hộp nhãn không giao với tiêu đề hoặc nội dung cảnh:**
   - Cả 7 cảnh có `hypo` đều không có bất kỳ điểm giao cắt nào giữa hộp nhãn và tiêu đề/nội dung.
   - Các khe hở đo được từ đáy nhãn tới đỉnh phần tử nội dung liền kề:
     - CK chart: 28px
     - CK counter: 24px
     - CK cards3d: 21px
     - MIM cards3d: 24px
     - MIM counter: 20px
     - CL ledger: 60px
     - CL counter: 131px
2. **Nội dung không chạm vùng subtitle (top 1478):**
   - Vùng phụ đề tính từ y = 1478.
   - Đáy nội dung sâu nhất trong tất cả các cảnh là 1354px (CK cards3d) và 1346px (MIM cards3d).
   - Khoảng trống dự phòng còn lại lần lượt là **124px** và **132px** (yêu cầu thiết kế chừa ít nhất 38px trước 1478). Tuyệt đối không chạm phụ đề.
3. **Mép phải nhỏ hơn 900:**
   - Mép phải lớn nhất của hộp nhãn là MIM (766px) và CL (722px tính cả tab băng).
   - Toàn bộ nhãn nằm gọn bên trái vùng an toàn (x < 900), tránh hoàn toàn cột nút thao tác bên phải của YouTube Shorts.
4. **Cỡ chữ nhãn ≥ subtitle:**
   - Cỡ chữ `.hypo-title` đạt computed `62px`, bằng đúng cỡ chữ phụ đề `.cap` (`62px`, `var(--caption-size)`).
   - Dòng phụ `hypo-sub` đạt 24px (CK, CL) hoặc 22px (MIM).
5. **Tỉ lệ thu nhỏ và độ đọc được:**
   - CK cards3d co tỉ lệ 0.9178 (~91.8%).
   - MIM cards3d co tỉ lệ 0.9060 (~90.6%).
   - Với mức co rất nhẹ (chỉ giảm khoảng 8–9%), cỡ chữ trên các thẻ 3D vẫn ở mức ~44–48px, các số liệu và nhãn thẻ ("TIỀN NUÔI XE", "MẤT GIÁ", "CỘNG", "MỖI LẦN GIẢI", "TẦN SUẤT") cùng dòng note vẫn hoàn toàn rõ nét, dễ đọc trên màn hình điện thoại 1080×1920.
6. **Xác nhận bố cục cũ không đổi trên cảnh KHÔNG có hypo:**
   - Đã kiểm tra 2 cảnh không có `hypo`: CK cảnh 0 (kinetic, t = 5.0s) và MIM cảnh 4 (board, t = 26.0s).
   - Cả 2 cảnh đều không có class `has-hypo`, không sinh wrapper `.hypo-content`, các biến `--hypo-shift` và `--hypo-scale` không được gắn.
   - Khung hình render đúng 100% vị trí, tỉ lệ và animation ban đầu của engine cũ.
7. **Trọng lượng font chữ (Google Fonts):**
   - Đã kiểm tra `document.fonts`: `Playfair Display` 900 italic đã được tải thành công (`status: 'loaded'`).
   - `JetBrains Mono` trọng lượng 800 cho khung MIM hiển thị đúng chuẩn. Dấu tiếng Việt đầy đủ trên toàn bộ các nhãn và phụ đề.

## Kết luận

Bản sửa lỗi nhãn vòng 2 của Codex đã khắc phục triệt để lỗi đè tiêu đề trên cả 2 kênh CK và MIM. Tất cả 7 cảnh có `hypo` và 2 cảnh không `hypo` đều vượt qua toàn bộ các cổng kiểm tra hình học và độ sắc nét.
