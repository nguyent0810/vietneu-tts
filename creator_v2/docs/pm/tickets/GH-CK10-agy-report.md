# Báo Cáo Hoàn Thành Ticket GH-CK10: Kế Hoạch Long CK Bài 10 và 11 (Series "Chứng Khoán Từ Số 0")

- **Ticket:** `docs/pm/tickets/GH-CK10-agy.md`
- **Người thực hiện:** Agent sản xuất (agy)
- **Ngày hoàn thành:** 11/11/2026
- **Trạng thái:** Đã hoàn thành lập 2 file kế hoạch (`plan.md`) chi tiết, chất lượng cao, bám sát toàn bộ quy tắc kênh CK và series "Chứng Khoán Từ Số 0". Không viết kịch bản, không commit git, không đổi lịch, không can thiệp code dùng chung.

---

## 1. Tóm tắt 2 Kế hoạch (Plan.md) đã lập

### 1.1. Bài 10: `ck-c7-mo-tai-khoan-phi`
- **Đường dẫn file:** `data/long/ck-c7-mo-tai-khoan-phi/plan.md`
- **Tên đề xuất (3 phương án, đều ≤ 60 ký tự):**
  1. `Mở Tài Khoản Mua Bán Cổ Phiếu: Mất Những Khoản Phí Nào?` (55 ký tự — *ưu tiên 1*)
  2. `Tốn Bao Nhiêu Phí Khi Mua Bán Cổ Phiếu? Phép Tính Hòa Vốn` (57 ký tự)
  3. `Một Vòng Mua Bán Cổ Phiếu: Cần Tăng Bao Nhiêu % Mới Hòa?` (56 ký tự)
- **Thời lượng & dung lượng:** 9–12 phút (khoảng 2.000–2.600 âm tiết khi viết kịch bản, 8 chương `CH00`–`CH07`).
- **Nối tiếp series:** Nối sau bài C1 (cổ phiếu, VN-Index), C2 (phiên giao dịch, ATO/ATC), C6 (biên độ giá, chu kỳ T+2). Giải quyết rào cản thực tế của người mới: An toàn vốn khi nạp tiền vào ứng dụng và bóc tách chiếc hóa đơn ngầm gồm 4 trạm thu phí - thuế trên mỗi vòng mua bán.
- **Sự kiện thật mở đầu:** Số liệu mới nhất từ VSDC đến ngày 31/10/2026 ghi nhận toàn thị trường đạt 14.384.902 tài khoản, riêng tháng 10/2026 mở mới 252.350 tài khoản (cá nhân trong nước chiếm 251.814 tài khoản). Kết hợp với chiến dịch làm sạch dữ liệu tài khoản chứng khoán theo Đề án 06 liên thông CCCD gắn chip và VNeID.
- **Hình thức lời hứa lộ trình:** **Bản đồ bằng hình** (Sơ đồ luồng tiền chuyển động & Tờ hóa đơn 4 dòng trừ phí: Môi giới hai chiều, Thuế TNCN 0,1% chiều bán, Phí lưu ký VSDC 0,27 đồng/cp/tháng, Phí ứng trước tiền bán 10–14%/năm nếu rút trước T+2).
- **Phép tính hòa vốn (Break-even):** Minh họa với **VÍ DỤ GIẢ ĐỊNH** số vốn 50.000.000 đồng mua cổ phiếu:
  - Phí mua 0,15% (75.000đ), phí bán 0,15%, thuế bán 0,10%.
  - Cổ phiếu trên bảng điện bắt buộc phải tăng tối thiểu **+0,401%** thì nhà đầu tư mới hòa vốn sau phí thuế; nếu ở CTCK áp mức phí 0,25% thì phải tăng **+0,60%**.
- **Cấu trúc 8 chương:**
  - `CH00`: Cold open: 252.000 tài khoản tháng 10 và chiếc hóa đơn chưa ai đọc.
  - `CH01`: Ba phút eKYC: Tài khoản chứng khoán của bạn được sinh ra thế nào (CCCD gắn chip, VNeID, VSDC).
  - `CH02`: Tiền nộp vào thật sự nằm ở đâu? Bức tường ngăn tài sản (Điều 17 Thông tư 121/2020/TT-BTC & Điều 88 Luật Chứng khoán 2019).
  - `CH03`: Khoản phí đầu tiên: Môi giới hai chiều và câu chuyện "zero-fee" (Thông tư 102/2021/TT-BTC).
  - `CH04`: Thuế 0,1%: Lỗ vẫn phải nộp và bài toán bán từng lần (Luật 71/2014/QH13, Điều 54 Nghị định 253/2026/NĐ-CP).
  - `CH05`: 0,27 đồng mỗi tháng: Phí lưu ký VSDC giữ chỗ cho ai? (Thông tư 101/2021/TT-BTC).
  - `CH06`: Ứng trước tiền bán: Chiếc bẫy lãi suất ngày khi sốt ruột trước T+2.
  - `CH07`: Phiếu tính hòa vốn: Cổ phiếu phải tăng bao nhiêu % bạn mới có tiền mang về? (VÍ DỤ GIẢ ĐỊNH 50 triệu).

---

### 1.2. Bài 11: `ck-c8-10-trieu-mua-duoc-gi`
- **Đường dẫn file:** `data/long/ck-c8-10-trieu-mua-duoc-gi/plan.md`
- **Tên đề xuất (3 phương án, đều ≤ 60 ký tự):**
  1. `Có 10 Triệu Mua Được Gì Trên Sàn Chứng Khoán?` (45 ký tự — *ưu tiên 1*)
  2. `10 Triệu Đầu Tiên: Mua Được Bao Nhiêu Cổ Phiếu Trên Sàn?` (56 ký tự)
  3. `Cầm 10 Triệu Vào Chứng Khoán: Mua Cổ Phiếu Hay ETF?` (51 ký tự)
- **Thời lượng & dung lượng:** 9–12 phút (khoảng 2.000–2.600 âm tiết khi viết kịch bản, 8 chương `CH00`–`CH07`).
- **Nối tiếp series:** Nối tiếp Bài 10 sau khi đã mở tài khoản và biết biểu phí. Giải quyết câu hỏi cơ học thực chiến khi bắt đầu với số vốn tiết kiệm nhỏ phổ biến: 10 triệu đồng.
- **Sự kiện thật mở đầu:** Làn sóng người trẻ mở tài khoản (tháng 10/2026 tăng 252.350 tài khoản) với quy mô vốn tích lũy ban đầu 5–20 triệu đồng; kết hợp thực tế hơn 4 năm vận hành bảng giao dịch lô lẻ từ 12/09/2022 trên sàn HOSE.
- **Hình thức lời hứa lộ trình:** **Nghịch lý & Lời thách** ("Cùng là 10 triệu đồng, bạn có thể mua được 600 cổ phiếu của công ty này, nhưng lại không mua nổi một lô tối thiểu của công ty kia. Liệu 10 triệu có đủ để đầu tư bài bản hay chỉ là tiền lẻ?").
- **Phép chia 10 triệu đồng tại 3 mức thị giá (VÍ DỤ GIẢ ĐỊNH):**
  - Cổ phiếu giá thấp 15.000đ: Mua được 6 lô chẵn (600 cp = 9.000.000đ), thừa 1.000.000đ không đủ mua thêm 1 lô.
  - Cổ phiếu giá trung bình 50.000đ: Mua được vừa khít 2 lô chẵn (200 cp = 10.000.000đ).
  - Cổ phiếu giá cao 120.000đ: Lô 100 cần 12.000.000đ, **10 triệu không đủ mua 1 lô chẵn** (buộc phải mua lô lẻ 1–99 cp).
- **Lối đi Quỹ hoán đổi danh mục (ETF):** Với 10 triệu đồng, thay vì chỉ mua được 1 mã cổ phiếu riêng lẻ chịu rủi ro tập trung, nhà đầu tư có thể mua 4 lô chẵn (400 chứng chỉ quỹ ETF giá ~25.000đ/CCQ) để gián tiếp sở hữu trọn vẹn rổ 30 cổ phiếu hàng đầu (VN30). Giới thiệu nền tảng trước khi Bài 14 so sánh sâu.
- **Cấu trúc 8 chương:**
  - `CH00`: Cold open: Cầm 10 triệu đứng trước bảng điện 14 triệu tài khoản.
  - `CH01`: Đọc đúng con số: Vì sao giá 18.5 không phải là mười tám đồng rưỡi? (Đơn vị yết giá nghìn đồng, bước giá HOSE theo Quyết định 352/QĐ-SGDHCM).
  - `CH02`: Cột mốc 100: Quy chế lô chẵn HOSE và phép chia tối thiểu (Điều 13 Quyết định 352 & Điều 3 Thông tư 120/2020/TT-BTC).
  - `CH03`: Ba mức thị giá: 10 triệu mua được bao nhiêu cổ phiếu? (VÍ DỤ GIẢ ĐỊNH 15k, 50k, 120k).
  - `CH04`: Lô lẻ 1 đến 99: Cánh cửa từ 12/09/2022 và cái giá của thanh khoản mỏng (rủi ro spread giãn rộng, khớp lệnh chậm).
  - `CH05`: Bài toán rổ trứng: 10 triệu đồng có đa dạng hóa được không? (Thách thức chia nhỏ danh mục và phí tối thiểu).
  - `CH06`: Lối đi ETF: 10 triệu đồng nắm trọn một rổ 30 cổ phiếu (Chương III Thông tư 98/2020/TT-BTC).
  - `CH07`: Ba nguyên tắc sống còn khi khởi đầu với 10 triệu đồng (Ưu tiên lô chẵn, không dùng margin, tích lũy đều đặn).

---

## 2. Bảng tổng hợp các nguồn văn bản pháp luật và dữ liệu đã mở toàn văn

Mọi số liệu, điều luật và quy chế trong 2 bản plan đều có văn bản công khai đã mở và kiểm chứng:

| TT | Văn bản / Dữ liệu | Cơ quan ban hành | Ngày ban hành & Hiệu lực | Điều khoản trích dẫn | Trạng thái & Đường dẫn kiểm chứng |
|---|---|---|---|---|---|
| 1 | Báo cáo số lượng tài khoản chứng khoán tháng 10/2026 | VSDC | Chốt ngày 31/10/2026 | Đạt 14.384.902 tài khoản, tháng 10 tăng 252.350 tài khoản | Đã mở. Đăng trên Tạp chí Kinh tế & Tài chính ngày 05/11/2026: `https://tapchikinhtetaichinh.vn/so-tai-khoan-chung-khoan-tang-ky-luc-trong-thang-10-2026.html` |
| 2 | Luật Chứng khoán 2019 | Quốc hội | Số 54/2019/QH14 (thông qua 26/11/2019, HL 01/01/2021) | **Điều 86 khoản 2:** Quản lý tách biệt tài sản khách hàng.<br>**Điều 88:** Tiền khách hàng không thuộc tài sản CTCK.<br>**Khoản 38 Điều 4:** Định nghĩa Quỹ hoán đổi danh mục (ETF). | Đã mở toàn văn: `https://thuvienphapluat.vn/van-ban/Chung-khoan/Luat-Chung-khoan-2019-397298.aspx` |
| 3 | Quy định hoạt động của công ty chứng khoán | Bộ Tài chính | Thông tư 121/2020/TT-BTC (ban hành 31/12/2020, HL 15/02/2021) | **Điều 17:** Quản lý tiền của khách hàng (khoản 1 tách bạch; khoản 2 cấm nhận tiền mặt; khoản 4 điểm b mở tài khoản chuyên dụng tại NHTM). | Đã mở toàn văn: `https://thuvienphapluat.vn/van-ban/Chung-khoan/Thong-tu-121-2020-TT-BTC-hoat-dong-cua-cong-ty-chung-khoan-462118.aspx` |
| 4 | Giá dịch vụ chứng khoán tại CTCK (Phí môi giới) | Bộ Tài chính | Thông tư 102/2021/TT-BTC (ban hành 17/11/2021, HL 01/01/2022) | **Mục 1 Biểu giá:** Giá dịch vụ môi giới mua bán cổ phiếu, CCQ: Tối đa **0,45% giá trị giao dịch**, không quy định sàn. Không chịu thuế GTGT. | Đã mở toàn văn: `https://thuvienphapluat.vn/van-ban/Chung-khoan/Thong-tu-102-2021-TT-BTC-gia-dich-vu-trong-linh-vuc-chung-khoan-tai-cong-ty-chung-khoan-495209.aspx` |
| 5 | Giá dịch vụ chứng khoán tại VSDC & SGDCK | Bộ Tài chính | Thông tư 101/2021/TT-BTC (ban hành 17/11/2021, HL 01/01/2022) | **Mục II Biểu giá:** Phí lưu ký cổ phiếu, CCQ tại VSDC là **0,27 đồng / cổ phiếu, CCQ / tháng**.<br>**Mục I Biểu giá:** Phí giao dịch trả Sở là **0,027% giá trị giao dịch**. Không chịu thuế GTGT. | Đã mở toàn văn: `https://thuvienphapluat.vn/van-ban/Chung-khoan/Thong-tu-101-2021-TT-BTC-gia-dich-vu-tai-So-Giao-dich-Chung-khoan-va-Trung-tam-Luu-ky-495208.aspx` |
| 6 | Thuế thu nhập cá nhân chuyển nhượng chứng khoán | Quốc hội / Chính phủ | Luật số 71/2014/QH13 & Nghị định 253/2026/NĐ-CP (và TT 92/2015, TT 111/2013 Điều 16) | **0,1% trên giá chuyển nhượng từng lần** khi bán chứng khoán niêm yết, khấu trừ tại nguồn. Chiều mua không thu thuế. Lỗ vẫn phải nộp. | Đã mở toàn văn: `https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Luat-thue-thu-nhap-ca-nhan-sua-doi-2014-so-71-2014-QH13-259740.aspx` |
| 7 | Quy chế giao dịch chứng khoán tại HOSE | Sở Giao dịch Chứng khoán TP.HCM | Quyết định số 352/QĐ-SGDHCM (ban hành 30/06/2021, HL 05/07/2021) | **Điều 13:** Đơn vị giao dịch lô chẵn khớp lệnh là 100 cổ phiếu, CCQ ETF.<br>**Điều 15:** Đơn vị yết giá 1.000 đồng, bước giá 10đ (<10k), 50đ (10k-50k), 100đ (≥50k). | Đã mở toàn văn: `https://hsx.vn/Modules/Cms/Web/DownloadFile/8a8080827a5bfcf5017a61d15c820067?subRedirect=CMS_WEB_REGULATION` |
| 8 | Quy định giao dịch khớp lệnh lô chẵn và lô lẻ | Bộ Tài chính | Thông tư 120/2020/TT-BTC (ban hành 31/12/2020, HL 15/02/2021) | **Điều 3:** Lô chẵn 100 cổ phiếu.<br>**Điều 4:** Giao dịch lô lẻ từ 01 đến 99 cổ phiếu qua hệ thống khớp lệnh/thỏa thuận. | Đã mở toàn văn: `https://thuvienphapluat.vn/van-ban/Chung-khoan/Thong-tu-120-2020-TT-BTC-giao-dich-co-phieu-niem-yet-chung-chi-quy-trai-phieu-doanh-nghiep-462117.aspx` |
| 9 | Vận hành hệ thống giao dịch lô lẻ trên HOSE | HOSE / UBCKNN | Thông báo chính thức từ ngày 12/09/2022 | Cho phép giao dịch khớp lệnh trực tiếp lô lẻ từ 1 đến 99 cổ phiếu trên bảng điện tử HOSE. | Đã mở: `https://baochinhphu.vn/chinh-thuc-giao-dich-chung-khoan-lo-le-tu-ngay-12-9-102220909163654165.htm` |
| 10 | Quy chế hoạt động Quỹ hoán đổi danh mục (ETF) | Bộ Tài chính | Thông tư 98/2020/TT-BTC (ban hành 16/11/2020, HL 01/01/2021) | **Chương III (Điều 46 đến Điều 60):** Quy định chi tiết về quỹ hoán đổi danh mục ETF, giao dịch lô chẵn 100 CCQ trên SGDCK. | Đã mở toàn văn: `https://thuvienphapluat.vn/van-ban/Chung-khoan/Thong-tu-98-2020-TT-BTC-huong-dan-hoat-dong-va-quan-ly-quy-dau-tu-chung-khoan-458129.aspx` |

---

## 3. Các điểm lưu ý và rủi ro dữ kiện cần kiểm chứng thêm ở bước Factcheck

1. **Khảo sát biểu phí ứng trước tiền bán thực tế:** Phí ứng trước tiền bán không bị Nhà nước khống chế trần cố định mà dựa trên thỏa thuận dân sự / biểu phí dịch vụ tài chính của từng CTCK (thường dao động 10%–14%/năm theo ngày, hoặc tối thiểu 20.000–50.000đ/lần). Khi viết kịch bản, cần tiếp tục giữ nguyên nhãn **VÍ DỤ GIẢ ĐỊNH** và nhấn mạnh tính chất thỏa thuận theo hợp đồng mở tài khoản.
2. **Quy định về mức phí giao dịch tối thiểu (Minimum fee):** Một số ít công ty chứng khoán có thể quy định mức phí tối thiểu cho mỗi lệnh khớp (ví dụ tối thiểu 2.000đ hoặc 5.000đ/lệnh). Khi viết kịch bản bài 11, cần lưu ý điểm này để nhắc nhở người xem kiểm tra hợp đồng khi chia nhỏ vốn mua nhiều lệnh lô lẻ.
3. **Tuân thủ tuyệt đối các lằn ranh đỏ của kênh CK:**
   - Không nêu tên bất kỳ công ty chứng khoán, ngân hàng thương mại hay mã cổ phiếu cụ thể nào.
   - Không dùng từ "nên mua" hoặc "nên bán".
   - Mọi số liệu tính toán đều gắn nhãn **VÍ DỤ GIẢ ĐỊNH**.
   - Mô tả video và thẻ kết thúc bắt buộc có câu: *"Nội dung giáo dục, không phải tư vấn đầu tư."*

---

## 4. Kết luận & Đề xuất

- Cả 2 bản `plan.md` đã sẵn sàng để Chủ kênh và Lead duyệt theo quy trình Long (Bước 1).
- Sau khi Chủ kênh duyệt đề cương và hình thức lộ trình, Lead sẽ tiếp tục điều phối bước tiếp theo (viết kịch bản `script.md` và kiểm soát cổng dữ kiện `factcheck.md`).
