# Báo cáo kết quả GH-173 vòng 2: Sửa 9 mockup nhãn VÍ DỤ GIẢ ĐỊNH

**Ticket:** `docs/pm/tickets/GH-173-agy-v2.md`  
**Căn cứ:** Review của Lead đối với `docs/pm/tickets/GH-173-report.md` và 9 mockup tại `docs/pm/mockups/173/`  
**Mục tiêu vòng 2:** Chụp ảnh ở trạng thái cuối (`?static`), nâng cỡ chữ nhãn lên ≥ 62px (đạt chuẩn không nhỏ hơn subtitle `#caps .cap`), bỏ chữ máy móc/mã giả, sửa lỗi đè tiêu đề biểu đồ ở `ck_badge_gold`, kiểm tra glyph tiếng Việt trên Playfair Display, và bảo đảm vùng an toàn (không đè subtitle 1478px và không nằm dưới cột nút bên phải x > 900px).

---

## 1. Bảng tổng hợp 9 kiểu nhãn sau khi sửa (Đo bằng `getComputedStyle`)

Toàn bộ 9 mockup HTML tại `docs/pm/mockups/173/` đã được bổ sung cơ chế tĩnh `?static` (tự động nhận diện query string qua JavaScript và CSS để tắt mọi animation, đưa mọi thành phần về trạng thái hoàn tất). Cỡ chữ và tọa độ hiển thị dưới đây được đo thực tế từ Chrome headless với khung hình chuẩn 1080×1920:

| STT | Kênh | Tên kiểu nhãn | File HTML / PNG | Cỡ chữ nhãn (`fontSize`) | Font chữ & Trọng số | Tọa độ khung nhãn (`rect`) | Trạng thái `?static` | Các chữ đã bỏ / sửa |
| :---: | :---: | :--- | :--- | :---: | :--- | :---: | :---: | :--- |
| 1 | **CK** | **Ruy-băng điện ảnh** *(Cinematic Gold Ribbon)* | `docs/pm/mockups/173/ck_ribbon.html`<br/>`docs/pm/mockups/173/ck_ribbon.png` | **64px** | `Be Vietnam Pro`<br/>weight: 900 | left: 64px, top: 220px<br/>right: **694px**, bottom: 357px | Đã bật<br/>*(trượt hoàn tất, 100% nét)* | Không có mã giả; giữ dòng phụ tiếng Việt tự nhiên "PHÉP TÍNH MINH HOẠ · LÃI 4% NĂM". |
| 2 | **CK** | **Thẻ kính nổi bo tròn** *(Floating Glass Pill)* | `docs/pm/mockups/173/ck_badge_gold.html`<br/>`docs/pm/mockups/173/ck_badge_gold.png` | **62px** | `JetBrains Mono`<br/>weight: 800 | left: 64px, top: 216px<br/>right: **693px**, bottom: 318px | Đã bật<br/>*(pop hoàn tất, LED sáng rõ)* | **Đã sửa lỗi đè tiêu đề biểu đồ:** tăng khoảng cách tiêu đề lên 75px, hạ chiều cao cột giúp "18,75 tr" cách tiêu đề > 100px. |
| 3 | **CK** | **Phân đoạn điện ảnh trung tâm** *(Cinematic Scene Slug)* | `docs/pm/mockups/173/ck_cinematic_slug.html`<br/>`docs/pm/mockups/173/ck_cinematic_slug.png` | **64px** | `Be Vietnam Pro`<br/>weight: 900 | left: 64px, top: 250px<br/>right: **884px**, bottom: 392px | Đã bật<br/>*(dải mở phẳng 100%)* | Eyebrow đổi thành tiếng Việt tự nhiên "✦ SỐ LIỆU MINH HOẠ ✦". **Thu hẹp chiều rộng về 820px** để cạnh phải đạt 884px < 900px (vùng an toàn nút bên phải). |
| 4 | **MIM** | **Khung ngoặc dòng lệnh HUD** *(Terminal HUD Bracket)* | `docs/pm/mockups/173/mim_terminal_bracket.html`<br/>`docs/pm/mockups/173/mim_terminal_bracket.png` | **62px** | `JetBrains Mono`<br/>weight: 800 | left: 64px, top: 220px<br/>right: **717px**, bottom: 363px | Đã bật<br/>*(con trỏ `_` cố định, bracket rõ)* | **Bỏ hoàn toàn:** "SYS_SIM // 01" và "SYNTHETIC_DATA". Thay bằng tag "MÔ PHỎNG" và dòng "SỐ LIỆU MINH HOẠ". |
| 5 | **MIM** | **Thẻ kính phòng thí nghiệm** *(Cyber Lab Glass)* | `docs/pm/mockups/173/mim_glass_cyber.html`<br/>`docs/pm/mockups/173/mim_glass_cyber.png` | **62px** | `Be Vietnam Pro`<br/>weight: 900 | left: 64px, top: 216px<br/>right: **758px**, bottom: 349px | Đã bật<br/>*(kính trượt hoàn tất)* | Dòng phụ đổi thành tiếng Việt tự nhiên: "SỐ LIỆU MINH HOẠ · THÔNG SỐ TỔNG HỢP", không dùng thuật ngữ máy móc. |
| 6 | **MIM** | **Thước đo điện ảnh viễn tưởng** *(Anamorphic Sci-Fi Slate)* | `docs/pm/mockups/173/mim_anamorphic_slate.html`<br/>`docs/pm/mockups/173/mim_anamorphic_slate.png` | **64px** | `Be Vietnam Pro`<br/>weight: 900 | left: 64px, top: 250px<br/>right: **884px**, bottom: 391px | Đã bật<br/>*(vạt sáng mở trọn vẹn)* | **Bỏ hoàn toàn:** "SIMULATION ENVIRONMENT". Thay bằng "◈ SỐ LIỆU MINH HOẠ ◈". **Thu hẹp chiều rộng về 820px** (cạnh phải 884px < 900px). |
| 7 | **CL** | **Dấu son mộc hồ sơ lưu trữ** *(Archive Dossier Stamp)* | `docs/pm/mockups/173/cl_dossier_stamp.html`<br/>`docs/pm/mockups/173/cl_dossier_stamp.png` | **64px** | `Playfair Display`<br/>weight: 900 | left: 77px, top: 203px<br/>right: **719px**, bottom: 382px | Đã bật<br/>*(dập son cố định nghiêng -3°)* | **Đổi tiêu đề:** từ "TÌNH HUỐNG GIẢ ĐỊNH" sang chuẩn "VÍ DỤ GIẢ ĐỊNH". Bỏ mã số giả "HS-04 //", đổi thành "HỒ SƠ THỰC NGHIỆM MINH HOẠ". |
| 8 | **CL** | **Băng giấy ghi chú hiện trường** *(Evidence Note Ribbon)* | `docs/pm/mockups/173/cl_evidence_tape.html`<br/>`docs/pm/mockups/173/cl_evidence_tape.png` | **64px** | `Playfair Display`<br/>weight: 900 Italic | left: 80px, top: 226px<br/>right: **701px**, bottom: 324px | Đã bật<br/>*(băng keo dán phẳng hoàn tất)* | Giữ nhãn "VÍ DỤ GIẢ ĐỊNH", không có mã số giả hay chữ kỹ thuật. |
| 9 | **CL** | **Thẻ đánh máy phòng thẩm vấn** *(Typewriter Slate)* | `docs/pm/mockups/173/cl_typewriter_slate.html`<br/>`docs/pm/mockups/173/cl_typewriter_slate.png` | **62px** | `JetBrains Mono`<br/>weight: 800 | left: 80px, top: 220px<br/>right: **759px**, bottom: 353px | Đã bật<br/>*(thẻ dừng trượt hoàn tất)* | **Bỏ mã số giả:** bỏ "// CASE-09", đổi dòng phụ thành "GIẢ THUYẾT ĐIỀU TRA · SỐ LIỆU MINH HOẠ". |

---

## 2. Chi tiết xử lý 6 yêu cầu kỹ thuật từ Brief

### 2.1. Chụp ở trạng thái cuối của hiệu ứng (`?static`)
- **Triển khai kỹ thuật:**
  - Trong thẻ `<head>` của cả 9 file HTML, script kiểm tra query string đồng bộ:
    ```javascript
    if (window.location.search.includes('static')) {
      document.documentElement.classList.add('is-static');
    }
    ```
  - Trong CSS:
    ```css
    html.is-static *,
    html.is-static *::before,
    html.is-static *::after {
      animation: none !important;
      transition: none !important;
    }
    html.is-static .cursor,
    html.is-static .dot {
      opacity: 1 !important;
      transform: none !important;
    }
    ```
- **Kết quả chụp PNG:** Toàn bộ 9 file ảnh PNG đã được chụp lại bằng Chrome headless với URL `?static`. Không còn hiện tượng mờ nét do chụp giữa animation (ở `ck_ribbon`, `ck_badge_gold`, `mim_terminal_bracket`, `mim_glass_cyber`), nhãn hiển thị ở 100% độ tương phản, các thành phần động như con trỏ lệnh (`_`) và đèn LED đều sáng cố định.

### 2.2. Chuẩn hóa cỡ chữ nhãn ≥ 62px
- Cỡ chữ của nhãn "VÍ DỤ GIẢ ĐỊNH" trên cả 9 mockup đều đạt từ **62px đến 64px** (được đo đạc chính xác qua `window.getComputedStyle`).
- So sánh trực tiếp với subtitle thuyết minh (`#caps .cap`) trong cùng khung hình (đạt 62px): nhãn có kích thước ngang bằng hoặc lớn hơn dòng phụ, bảo đảm khi xem trên màn hình điện thoại (chiều rộng 360px), chữ "VÍ DỤ GIẢ ĐỊNH" đạt kích cỡ vật lý ≥ 20px, hoàn toàn đọc rõ mà không cần phóng to.
- Khoảng cách ký tự (`letter-spacing`) được tinh chỉnh từ `0.02em` đến `0.08em` để dòng chữ vừa vặn trong một hàng, không bị tràn hay xuống dòng thô ráp.

### 2.3. Loại bỏ chữ máy móc, giả kỹ thuật và mã số giả
- Đã rà soát và loại bỏ 100% các cụm từ máy móc tiếng Anh và mã số giả:
  - Bỏ `"SIMULATION ENVIRONMENT"` $\rightarrow$ đổi thành `"◈ SỐ LIỆU MINH HOẠ ◈"` (`mim_anamorphic_slate`).
  - Bỏ `"SYS_SIM // 01"` và `"SYNTHETIC_DATA"` $\rightarrow$ đổi thành tag `"MÔ PHỎNG"` và dòng `"SỐ LIỆU MINH HOẠ"` (`mim_terminal_bracket`).
  - Bỏ `"HỒ SƠ HS-04 // THỰC NGHIỆM"` $\rightarrow$ đổi thành `"HỒ SƠ THỰC NGHIỆM MINH HOẠ"` (`cl_dossier_stamp`).
  - Bỏ `"// CASE-09"` $\rightarrow$ đổi thành `"GIẢ THUYẾT ĐIỀU TRA · SỐ LIỆU MINH HOẠ"` (`cl_typewriter_slate`).
  - Dòng phụ đi kèm nhãn chỉ sử dụng ngôn ngữ tiếng Việt tự nhiên.

### 2.4. Khắc phục lỗi đè chữ ở `ck_badge_gold`
- **Nguyên nhân vòng 1:** Chiều cao cột 11%/năm (`bar-col.b2`) là 410px cộng thêm số liệu `18,75 tr` và khoảng cách đệm vượt quá chiều cao khối chứa biểu đồ, khiến số liệu nhô lên đè sát vào đáy của tiêu đề biểu đồ (`chart-title`).
- **Khắc phục vòng 2:**
  - Tăng khoảng cách dưới của tiêu đề biểu đồ (`margin-bottom: 75px`).
  - Giảm chiều cao cột b1 xuống 200px và b2 xuống 295px (vẫn giữ nguyên tỷ lệ toán học 11% so với 6%).
  - Số liệu `18,75 tr` hiện cách tiêu đề biểu đồ một khoảng thoáng hơn 100px, bảo đảm phân tách thị giác rõ ràng và thẩm mỹ.

### 2.5. Kiểm tra hiển thị font tiếng Việt (Playfair Display)
- **Kiểm tra thực tế:** Đã thử nghiệm render bộ ký tự dấu phức tạp viết hoa tiếng Việt (`Ầ Ệ Ở Ữ` và `VÍ DỤ GIẢ ĐỊNH`) với `Playfair Display 900` và `Playfair Display 900 Italic`:
  - Font Google Fonts tải về đầy đủ glyph cho subset tiếng Việt.
  - Các ký tự có dấu mũ + dấu huyền/nặng/hỏi/ngã (`Ầ`, `Ệ`, `Ở`, `Ữ`) và dấu gạch ngang chữ `Đ` đều hiển thị sắc nét, không bị rơi về font hệ thống fallback.
  - Cụm từ "VÍ DỤ GIẢ ĐỊNH" trong `cl_dossier_stamp` (Playfair 900) và `cl_evidence_tape` (Playfair 900 Italic) đạt độ trang trọng cổ điển rất cao, phù hợp với phong cách hồ sơ điều tra của kênh CL.
  *(Ghi chú kỹ thuật: Font Lora 700 cũng đã được kiểm tra sẵn sàng làm phương án serif dự phòng nếu kênh cần nét dấu hiện đại hơn).*

### 2.6. Bảo đảm vùng an toàn (Safe Zone)
- **Không đè Subtitle:** Cả 9 mockup nhãn đều đặt ở khu vực lề trên (`top: 203px – 250px`, đáy nhãn `bottom: 318px – 392px`), cách subtitle ở đáy (`top: 1478px`) hơn 1080px.
- **Không nằm dưới cột nút bên phải Shorts (`x > 900px`):**
  - Các nhãn dạng khối (`inline-flex`): có cạnh phải (`rect.right`) nằm trong khoảng `693px – 759px`, cách mép an toàn 900px hơn 140px.
  - Hai kiểu nhãn dải ngang (`ck_cinematic_slug` và `mim_anamorphic_slate`): ở vòng 1 từng trải rộng toàn màn hình (`right: 64px`, tức x chạm tới 1016px). Ở vòng 2, dải đã được cố định chiều rộng ở mức **820px** với lề trái 64px $\rightarrow$ cạnh phải đạt đúng **884px**, hoàn toàn nằm trong vùng an toàn trước cột nút Like/Share/Comment.

---

## 3. Danh mục file bàn giao

1. **Mockup HTML & PNG (đã cập nhật vòng 2):**
   - `docs/pm/mockups/173/ck_ribbon.html` & `docs/pm/mockups/173/ck_ribbon.png`
   - `docs/pm/mockups/173/ck_badge_gold.html` & `docs/pm/mockups/173/ck_badge_gold.png`
   - `docs/pm/mockups/173/ck_cinematic_slug.html` & `docs/pm/mockups/173/ck_cinematic_slug.png`
   - `docs/pm/mockups/173/mim_terminal_bracket.html` & `docs/pm/mockups/173/mim_terminal_bracket.png`
   - `docs/pm/mockups/173/mim_glass_cyber.html` & `docs/pm/mockups/173/mim_glass_cyber.png`
   - `docs/pm/mockups/173/mim_anamorphic_slate.html` & `docs/pm/mockups/173/mim_anamorphic_slate.png`
   - `docs/pm/mockups/173/cl_dossier_stamp.html` & `docs/pm/mockups/173/cl_dossier_stamp.png`
   - `docs/pm/mockups/173/cl_evidence_tape.html` & `docs/pm/mockups/173/cl_evidence_tape.png`
   - `docs/pm/mockups/173/cl_typewriter_slate.html` & `docs/pm/mockups/173/cl_typewriter_slate.png`
2. **File báo cáo v2:**
   - `docs/pm/tickets/GH-173-report-v2.md`

*Cam kết tuân thủ quy tắc:* Không sửa engine/stier/factory/tests, không sửa git/commit, không upload/đổi lịch YouTube, chỉ ghi đúng phạm vi được giao.
