# Báo cáo kết quả GH-173: Đề xuất kiểu nhãn VÍ DỤ GIẢ ĐỊNH theo phong cách điện ảnh (Phần thiết kế)

**Ticket:** `docs/pm/tickets/GH-173-agy.md`  
**Issue:** nguyent0810/vietneu-tts#173 (tách từ #145 theo retro 04/11 & chốt định hướng 05/11)  
**Mục tiêu:** Khảo sát thực trạng nhãn ví dụ giả định trong Short; thiết kế mockup HTML và xuất ảnh chụp khung hình 1080×1920 đạt chuẩn cỡ chữ không nhỏ hơn dòng phụ; đề xuất kiểu dáng điện ảnh cho từng kênh (CK, MIM, CL).

---

## 1. Khảo sát thực trạng nhãn "GIẢ ĐỊNH" trong Short hiện tại

### 1.1. Vị trí xuất hiện trong spec Short (`data/stier/specs/*.json`)
Qua rà soát toàn bộ các file spec Short, có **148 vị trí** đang dùng cụm từ "GIẢ ĐỊNH" hoặc "giả định" trong các cảnh hình ảnh, phân bổ theo các loại cảnh như sau:

| Loại cảnh (`type`) | Số lần xuất hiện | Vị trí đặt nhãn trong cảnh |
| :--- | :---: | :--- |
| **`chart`** (Biểu đồ cột/đường) | **46** | Đặt vào `unit` (dòng đơn vị trên đỉnh biểu đồ) hoặc `note` (dòng ghi chú ở đáy) |
| **`cards3d`** (Thẻ 3D) | **30** | Đặt vào `title` của khối thẻ hoặc dòng `note` nhỏ dưới cùng |
| **`counter`** (Số đếm tăng giảm) | **29** | Đặt vào `sub.text` ngay dưới các chữ số lớn |
| **`kinetic`** (Chữ động theo nhịp) | **13** | Đặt thành một dòng `item` phụ (`sm: true`) |
| **`ledger`** (Sổ kế toán / bảng kê) | **12** | Đặt vào `title` trên đầu sổ |
| **`board`** (Bảng sơ đồ nốt) | **9** | Đặt vào `note` dòng chân bảng hoặc `title` |
| **`slam`** (Chữ đập mạnh trung tâm) | **5** | Đặt vào `sub` ngay dưới dòng chữ lớn |
| **`table`** (Bảng tra đối chiếu) | **4** | Đặt vào `note` nhỏ ở đáy bảng |

### 1.2. Đo đạc cỡ chữ thực tế ở khung 1080×1920 và nguyên nhân người xem không đọc được

Khi đo kích thước chữ trên khung hình chuẩn 1080×1920 (theo thuật toán render trong `motion/hf/assets/engine/casefile.js` và CSS của engine):

1. **Cỡ chữ của nhãn giả định hiện tại:**
   - Trong `counter` (`sub.text`): tính bằng hàm `fsz(sub.text, 30, 980, 0.86)` $\rightarrow$ thực tế chỉ đạt **28px – 30px**, màu xám mờ `#94a3b8` (`var(--dim)`).
   - Trong `chart` (`unit`): tính bằng hàm `fsz(unit, 28, 1000, 0.82)` $\rightarrow$ chỉ đạt **24px – 28px**.
   - Trong `note` (của chart, cards3d, board, table): CSS cố định là **22px** (`.chnote`, `.bdnote mono`).
   - Trong `slam` (`sub`): tính bằng hàm `fsz(sub, 30, 980, 0.84)` $\rightarrow$ chỉ đạt **28px – 30px**.

2. **Cỡ chữ của dòng phụ và subtitle trong cùng video Short:**
   - **Subtitle thuyết minh (`#caps .cap`):** cố định ở mức **62px** (font-weight 800, line-height 1.22, đặt tại `top: 1478px`).
   - **Dòng phụ kinetic (`.kin.sm`):** có giới hạn trần `cap = 64px`, thực tế cho các câu 12–25 ký tự đạt **48px – 64px** (font-weight 700).
   - **Tiêu đề phân đoạn / Kicker:** Kicker bar đạt **30px** (chữ chính hoa) và **21px** (chữ nhỏ).

3. **Kết luận về khiếm khuyết:**
   - Ở khung xem điện thoại thực tế (chiều rộng màn hình khoảng 360px – 390px vật lý), nhãn 22px – 28px chỉ hiển thị tương đương **7.3px – 9.3px**, bị chìm hoàn toàn vào nền và không thể đọc được nếu không phóng to.
   - Theo tiêu chí kỹ thuật đã chốt ngày 05/11 (phương án a): **Cỡ chữ nhãn không nhỏ hơn dòng phụ trong video** $\rightarrow$ Kích thước của nhãn bắt buộc phải đạt tối thiểu từ **≥ 48px đến 62px**, đồng thời phải có độ tương phản và vị trí an toàn riêng biệt, không thể tiếp tục dùng chung trường `sub` hay `note` cỡ 22px–28px.

---

## 2. Bảng tổng hợp các kiểu nhãn đề xuất (9 mockup cho 3 kênh)

Tất cả mockup đều được dựng thành file HTML độc lập tại `docs/pm/mockups/173/` với khung hình 1080×1920, dùng ảnh nền có sẵn trong repo (`motion/hf/assets/clips/sheets/`), không chứa bất kỳ chữ máy móc hay tên model/bot nào, và đã được chụp thành ảnh PNG chuẩn bằng Chrome headless (`--headless=new --window-size=1080,1920`).

| Kênh | Tên kiểu nhãn | File HTML / File PNG | Cỡ chữ nhãn | Màu sắc & Font chữ | Kiểu chuyển động (In/Out) | Đặc trưng phong cách điện ảnh |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **CK** | **Ruy-băng điện ảnh** *(Cinematic Gold Ribbon)* | `docs/pm/mockups/173/ck_ribbon.html`<br/>`docs/pm/mockups/173/ck_ribbon.png` | **54px** *(sub: 24px)* | Vàng kim `#fbbf24`, nền kính `#0f1b2e` mờ.<br/>Font: *Be Vietnam Pro 900* + *JetBrains Mono*. | Trượt êm từ lề trái (`cubic-bezier(0.16, 1, 0.3, 1)`), vạch vàng bừng sáng nhẹ. | Thước đo lề trên điện ảnh kiểu phim tài liệu tài chính Bloomberg/WSJ, sang trọng, uy tín. |
| **CK** | **Thẻ kính nổi bo tròn** *(Floating Glass Pill)* | `docs/pm/mockups/173/ck_badge_gold.html`<br/>`docs/pm/mockups/173/ck_badge_gold.png` | **52px** | Vàng sáng `#fde68a`, viền kép vàng hổ phách.<br/>Font: *JetBrains Mono 800*. | Nổi mờ (pop & scale 0.9 $\rightarrow$ 1.0) kèm đèn LED vàng nhịp thở chậm. | Viên nang capsule dữ liệu thị trường cao cấp (Market Simulation Tag). |
| **CK** | **Phân đoạn điện ảnh trung tâm** *(Cinematic Scene Slug)* | `docs/pm/mockups/173/ck_cinematic_slug.html`<br/>`docs/pm/mockups/173/ck_cinematic_slug.png` | **58px** *(eyebrow: 24px)* | Trắng ngà `#fff9ea`, hai đường kẻ vàng kim.<br/>Font: *Be Vietnam Pro 900*. | Mở rộng ngang từ tâm ra hai cánh (`scaleX(0.92 $\rightarrow$ 1)`). | Phân cảnh tiêu đề điện ảnh (Cinema Chapter Cue), trang trọng và đĩnh đạc. |
| **MIM** | **Khung ngoặc dòng lệnh HUD** *(Terminal HUD Bracket)* | `docs/pm/mockups/173/mim_terminal_bracket.html`<br/>`docs/pm/mockups/173/mim_terminal_bracket.png` | **54px** *(meta: 22px)* | Cyan neon `#22d3ee`, nền kính sẫm `#081221`.<br/>Font: *JetBrains Mono 800*. | Trượt định vị HUD nhanh + con trỏ lệnh `_` nhấp nháy, ký hiệu nhắc lệnh `> `. | Giao diện HUD máy học trong phim khoa học viễn tưởng (Sci-Fi Cybernetic Interface). |
| **MIM** | **Thẻ kính phòng thí nghiệm** *(Cyber Lab Glass)* | `docs/pm/mockups/173/mim_glass_cyber.html`<br/>`docs/pm/mockups/173/mim_glass_cyber.png` | **52px** *(sub: 22px)* | Trắng lơ `#e6f1ff`, viền cyan phát sáng `#22d3ee`.<br/>Font: *Be Vietnam Pro 900* + *Mono*. | Quét màng sáng (scan sweep) từ trái sang phải, icon chip mô phỏng `MIM`. | Thẻ chú thích mẫu vật / thông số phòng thí nghiệm AI (DeepMind / OpenAI Lab Slate). |
| **MIM** | **Thước đo điện ảnh viễn tưởng** *(Anamorphic Sci-Fi Slate)* | `docs/pm/mockups/173/mim_anamorphic_slate.html`<br/>`docs/pm/mockups/173/mim_anamorphic_slate.png` | **60px** *(tag: 24px)* | Trắng cyan `#e6f8ff`, dải gradient tối ngang.<br/>Font: *Be Vietnam Pro 900* (tracking rộng). | Tia laser quét mở vạt ngang hai đầu, chữ trôi chậm (anamorphic drift). | Title card phong cách phim viễn tưởng Christopher Nolan (Tenet, Interstellar). |
| **CL** | **Dấu son mộc hồ sơ lưu trữ** *(Archive Dossier Stamp)* | `docs/pm/mockups/173/cl_dossier_stamp.html`<br/>`docs/pm/mockups/173/cl_dossier_stamp.png` | **56px** *(meta: 22px)* | Đỏ son `#e2402d`, nền thấu quang đỏ mờ.<br/>Font: *Playfair Display 900* (serif cổ điển). | Dập mạnh (scale 1.25 $\rightarrow$ 1.0) có độ nảy cơ học, xoay nghiêng tự nhiên -3°. | Con dấu niêm phong mộc đỏ của cơ quan điều tra trên tài liệu vụ án mật. |
| **CL** | **Băng giấy ghi chú hiện trường** *(Evidence Note Ribbon)* | `docs/pm/mockups/173/cl_evidence_tape.html`<br/>`docs/pm/mockups/173/cl_evidence_tape.png` | **54px** | Đen sẫm `#1a1410` trên nền giấy kraft `#f3ecdc`.<br/>Font: *Playfair Display 900 Italic*. | Băng giấy dán dính vào hiện trường, hai đầu có vết băng keo đục mờ cố định. | Băng ghi chú tang chứng hiện trường phá án điện ảnh (Zodiac, Mindhunter). |
| **CL** | **Thẻ đánh máy phòng thẩm vấn** *(Typewriter Slate)* | `docs/pm/mockups/173/cl_typewriter_slate.html`<br/>`docs/pm/mockups/173/cl_typewriter_slate.png` | **52px** *(tag: 22px)* | Trắng ngà cổ `#f3ecdc`, vạch lề đỏ son `#e2402d`.<br/>Font: *JetBrains Mono 800*. | Trượt nhẹ từ lề trái như bản tin máy chữ cơ học gõ tại phòng thẩm vấn. | Thẻ chú thích thời gian - địa điểm trong phim hình sự cổ điển (The Godfather, Sicario). |

---

## 3. Kiểu đề xuất cho mỗi kênh và lý do

Sau khi thử nghiệm hiển thị trên khung 1080×1920 với đầy đủ các thành phần thực tế (Kicker, thẻ dữ liệu, biểu đồ cột, số đếm và Subtitle 62px ở đáy):

### 3.1. Kênh CK (Tài chính cá nhân - Biểu Đồ Biết Nói)
- **Kiểu đề xuất chính:** **`ck_ribbon` (Ruy-băng điện ảnh - Cinematic Gold Ribbon)**.
- **Lý do lựa chọn:**
  1. **Tương thích bố cục không gian:** Đặt ở vị trí `top: 220px`, `left: 64px` (ngay dưới Kicker 96px, phía trên khối biểu đồ/cards ở `top: 450px`). Vị trí này hoàn toàn nằm trong vùng an toàn của Shorts, không bị vướng các nút Like/Share bên phải và không đè lên Subtitle ở đáy (`top: 1478px`).
  2. **Độ tương phản và thị giác:** Vạch vàng kim `#fbbf24` dày 10px ở mép trái giúp định vị mắt người xem ngay lập tức; cỡ chữ **54px** đậm nét đọc rất rõ ràng ở màn hình điện thoại 360px mà không bị thô ráp.
  3. **Chất điện ảnh tài chính:** Tạo cảm giác một thước đo thông số tư liệu đĩnh đạc của Bloomberg hoặc WSJ, hoàn toàn thoát khỏi cảm giác "ô cảnh báo pháp lý" hay "watermark vụng về".
- *Kiểu dự phòng:* `ck_badge_gold` (thẻ pill nổi 52px) có thể dùng linh hoạt cho các cảnh đơn giản hoặc cảnh mở đầu hero.

### 3.2. Kênh MIM (AI & Công nghệ - Mind in the Machine)
- **Kiểu đề xuất chính:** **`mim_terminal_bracket` (Khung ngoặc dòng lệnh HUD)**.
- **Lý do lựa chọn:**
  1. **Đúng bản sắc thương hiệu công nghệ:** Dấu nhắc lệnh `>` cùng con trỏ nhấp nháy `_` và thẻ chỉ mục `SYS_SIM // 01` hòa quyện hoàn hảo với ngôn ngữ phòng lab tối và lưới vi mạch cyan của MIM.
  2. **Dễ đọc vượt trội:** Cỡ chữ **54px** font `JetBrains Mono` kết hợp màu cyan neon `#22d3ee` trên nền kính đen sâu `#081221` tạo độ tương phản cực kỳ sắc nét.
  3. **Không xung đột nội dung:** Độ cao khối nhãn chỉ chiếm khoảng 120px ở góc trên lề trái, để trọn vẹn khu vực trung tâm cho các sơ đồ nốt (board) hay biểu đồ thuật toán.
- *Kiểu dự phòng:* `mim_anamorphic_slate` (thước đo 60px) rất hợp cho các cảnh mở màn kịch bản mô phỏng diện rộng.

### 3.3. Kênh CL (Hình Sự - Hồ Sơ Vụ Án)
- **Kiểu đề xuất chính:** **`cl_dossier_stamp` (Dấu son mộc hồ sơ lưu trữ)**.
- **Lý do lựa chọn:**
  1. **Ngôn ngữ hình ảnh hồ sơ phá án:** Dạng khung dấu son đỏ mộc điều tra nghiêng nhẹ -3° với font serif `Playfair Display 900` đem lại cảm giác tài liệu điều tra thực tế, như một con dấu đóng lên hồ sơ giải mật của FBI hoặc cơ quan tố tụng.
  2. **Cỡ chữ 56px đập vào mắt người xem:** Nhãn nổi bật nhưng thuộc về chất liệu của câu chuyện vụ án, người xem tiếp nhận thông tin "tình huống giả định / dựng lại theo lời khai" một cách tự nhiên như một phần của thủ pháp kể chuyện tài liệu.
  3. **Chuyển động có lực:** Hiệu ứng dập nảy nhẹ (slam) kết hợp với âm thanh thud/dập mộc sẵn có của engine CL tạo ấn tượng điện ảnh mạnh mẽ.
- *Kiểu dự phòng:* `cl_evidence_tape` (băng giấy ghi chú dán băng keo 54px) đặc biệt phù hợp cho các cảnh thực nghiệm hiện trường thực địa ban đêm.

---

## 4. Danh sách các file bàn giao

Các file HTML và ảnh khung hình PNG đã sẵn sàng để Chủ kênh và Lead duyệt:
1. `docs/pm/mockups/173/ck_ribbon.html` & `docs/pm/mockups/173/ck_ribbon.png`
2. `docs/pm/mockups/173/ck_badge_gold.html` & `docs/pm/mockups/173/ck_badge_gold.png`
3. `docs/pm/mockups/173/ck_cinematic_slug.html` & `docs/pm/mockups/173/ck_cinematic_slug.png`
4. `docs/pm/mockups/173/mim_terminal_bracket.html` & `docs/pm/mockups/173/mim_terminal_bracket.png`
5. `docs/pm/mockups/173/mim_glass_cyber.html` & `docs/pm/mockups/173/mim_glass_cyber.png`
6. `docs/pm/mockups/173/mim_anamorphic_slate.html` & `docs/pm/mockups/173/mim_anamorphic_slate.png`
7. `docs/pm/mockups/173/cl_dossier_stamp.html` & `docs/pm/mockups/173/cl_dossier_stamp.png`
8. `docs/pm/mockups/173/cl_evidence_tape.html` & `docs/pm/mockups/173/cl_evidence_tape.png`
9. `docs/pm/mockups/173/cl_typewriter_slate.html` & `docs/pm/mockups/173/cl_typewriter_slate.png`
10. Báo cáo kết quả: `docs/pm/tickets/GH-173-report.md`.

*Cam kết tuân thủ:* Không sửa code engine (`motion/hf/assets/engine/*`, `motion/stier/*`), không sửa git, không render video, không chỉnh sửa lịch YouTube.
