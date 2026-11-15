<!-- plan-sources:start -->
## Kiểm nguồn tự động (2026-11-15)

> Kết quả hỗ trợ rà soát, không chứng minh nội dung đúng; CHAN và KHONG_MO_DUOC chưa được xác minh.

| URL | Trạng thái | Số file Commons (gồm một cấp con) | Chi tiết |
|---|---|---:|---|
| https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf | CHAN | — |  |
| https://www.sec.gov/newsroom/press-releases/2013-222 | CHAN | — |  |
| https://en.wikipedia.org/wiki/Knight_Capital_Group | TRANG_LOI | — |  |
| https://dougseven.com/2014/04/17/knightmare-a-devops-cautionary-tale/ | OK | — |  |
| https://commons.wikimedia.org/wiki/Category:New_York_Stock_Exchange | OK | 590 |  |
| https://commons.wikimedia.org/wiki/Category:Stock_exchanges | OK | 302 |  |
| https://commons.wikimedia.org/wiki/Category:Stock_market | OK | 150 |  |
| https://commons.wikimedia.org/wiki/Category:Server_rooms | TRANG_LOI | 522 |  |
| https://commons.wikimedia.org/wiki/Category:Data_centers | OK | 683 |  |
<!-- plan-sources:end -->

# Long tiếp theo: 45 PHÚT MẤT 460 TRIỆU ĐÔ, MỘT MÁY CHỦ QUÊN CẬP NHẬT (kế hoạch, gửi chủ kênh duyệt trước khi viết kịch bản)

- **Topic slug:** `mim-knight-capital-45-phut`
- **Kênh:** MIM (Mind in the Machine) — Giọng đọc: Thanh Bình (lời trích: Ngọc Huyền)
- **Độ dài mục tiêu:** 11–13 phút (~2.400–2.800 âm tiết), 9 chương (CH00 Cold open + CH01–CH08)
- **Trạng thái:** Chờ chủ kênh duyệt `plan.md` trước khi viết `script.md` và `factcheck.md`
- **Ý tưởng:** cùng tinh thần "sự cố có thật / cái giá / đồng hồ" với Binance (`mim-binance-6-3-ty-20-phut`) nhưng khác hẳn nội dung: không phải tin tặc, không phải tiền mã hoá, mà là phần mềm tự động của một công ty chứng khoán Mỹ tự phá mình vì một bản cập nhật sót máy.

---

## 1. Vì sao chọn đề tài này lúc này

- **Hồ sơ chính thức rất đầy đủ:** Lệnh xử lý của SEC ngày 16/10/2013 (Release No. 34-70694) kể lại sự cố 01/08/2012 bằng số cụ thể: 212 lệnh khách, hơn 4 triệu giao dịch, 154 mã cổ phiếu, hơn 397 triệu cổ phiếu, khoảng 45 phút, lỗ hơn 460 triệu đô. Hiếm sự cố công nghệ nào có đồng hồ rõ như vậy.
- **Cái giá và nghịch lý:** một công ty giao dịch hàng đầu nước Mỹ sống sót qua nhiều thập kỷ, mất gần như toàn bộ vốn chỉ vì một kỹ thuật viên không chép mã mới lên một trong tám máy chủ. Mã cũ ("Power Peg") đã bị bỏ dùng nhiều năm nhưng vẫn nằm đó. Cờ (flag) dùng cho chức năng mới trùng với cờ cũ.
- **Cảnh báo bị bỏ qua:** từ khoảng 8 giờ 01 sáng, hệ thống đã gửi 97 email báo lỗi "Power Peg disabled" trước giờ mở cửa 9 giờ 30; không ai xử lý vì đây không được thiết kế làm cảnh báo hệ thống.
- **Vì sao hợp MIM ("công nghệ quanh ta"):** thuật toán và phần mềm tự động quyết định tiền của nhiều người hơn người xem nghĩ (ví điện tử, chứng khoán, thanh toán). Câu hỏi "một máy chủ sót cập nhật hủy một công ty trong 45 phút?" dễ nhớ và dễ chia sẻ. Cần ghi rõ ngay từ đầu rằng đây là phần mềm giao dịch tự động, không phải mô hình AI.
- **Vì sao đóng gói lại:** Long MIM CTR 28 ngày ~1,2% dù giữ chân tốt. Đề tài có đồng hồ (45 phút), cái giá (460 triệu đô) và nghịch lý (một máy trong tám) sẵn để đưa lên tiêu đề và 40 giây đầu.
- **Không dính chuyện đầu tư:** không khuyên mua/bán, không bàn giá cổ phiếu Knight như cơ hội.

### Câu hỏi trung tâm
> **Làm sao một công ty giao dịch tự động hàng đầu Mỹ có thể mất 460 triệu đô trong 45 phút chỉ vì một bản cập nhật sót một máy chủ, và vì sao 97 email cảnh báo trước giờ mở cửa không cứu được họ?**

### Các vòng lặp mở
1. **Vòng 1, "một trong tám":** máy chủ nào không được cập nhật và vì sao nó đủ để phá cả hệ thống? *(đóng ở CH03)*
2. **Vòng 2, "97 email":** cảnh báo nào đã đến trước giờ mở cửa và vì sao không ai đọc? *(đóng ở CH04)*
3. **Vòng 3, "nút dừng":** tại sao 45 phút mới dừng được và có cách nào dừng sớm hơn? *(đóng ở CH05–CH06)*

---

## 2. Cold open 40 giây (cửa sổ sốc)

Nguyên tắc: thì hiện tại; hình mạnh nhất ở giây 0–5; câu hỏi hậu quả trước giây 8; bằng chứng đối lập trước giây 15; cắt 3–5 giây; tối thiểu 3 lần đập thị giác; không ảnh người thật bằng AI; không chữ trần.

| Giây | Hình | Lời / chữ |
|---|---|---|
| 0–4 | Đồng hồ số tối, `9:30` nhấp nháy, rồi chữ `45:00` đếm ngược đập lên; âm chuông mở cửa (nếu có tư liệu tự do) | "9 giờ 30 sáng, ngày 1 tháng 8 năm 2012. Chuông mở cửa thị trường chứng khoán Mỹ vang lên." |
| 4–9 | Ảnh/clip sàn giao dịch NYSE (Commons, tư liệu minh hoạ chung), đẩy chậm; counter giao dịch chạy vọt | "Một công ty nhận 212 lệnh nhỏ của khách hàng. Họ không biết rằng máy của mình sắp biến chúng thành hơn bốn triệu giao dịch." |
| 9–16 | Slam: `$460.000.000` (counter), cạnh dòng trích hồ sơ SEC, nhãn [TRÍCH DỊCH] | "Trong khoảng 45 phút, công ty này mất hơn 460 triệu đô la. Hồ sơ của cơ quan chứng khoán Mỹ gọi tên thủ phạm: một máy chủ." |
| 16–25 | Sơ đồ 8 ô máy chủ, 7 ô sáng xanh, 1 ô đỏ nhấp nháy (đồ hoạ tự dựng) | "Tám máy chủ. Bảy cái được cập nhật đúng. Một cái thì không." |
| 25–33 | Ô email, bộ đếm `97` tăng, nhãn "TRƯỚC 9:30"; chữ lớn "không ai đọc" | "Từ 8 giờ sáng, hệ thống đã gửi 97 email báo lỗi. Không ai coi đó là cảnh báo." |
| 33–40 | Đồng hồ dừng, câu hỏi trung tâm hiện chữ lớn | "Làm sao một dòng mã bỏ quên từ nhiều năm trước lại đủ để huỷ một công ty trong 45 phút?" |

*Ghi chú:* "Máy chủ sót cập nhật là nguyên nhân" là kết luận của SEC; "kỹ thuật viên không chép mã" cũng nằm trong lệnh xử lý (không nêu tên người; không đổ lỗi cá nhân). Ảnh NYSE chỉ làm bối cảnh chung: lệnh của Knight không được ghi là chạy trên sàn NYSE vật lý. Cảnh ghi nhãn MINH HỌA.

---

## 3. Dàn chương (9 chương)

| Chương | Tiêu đề chương | Nội dung và dữ kiện chính (nguồn mục 4) |
|---|---|---|
| CH00 | Cold open: 45 phút | Như mục 2. |
| CH01 | Công ty đứng sau những lệnh tự động | Knight Capital là công ty giao dịch/môi giới lớn của Mỹ; hệ thống SMARS nhận lệnh cha, chia thành lệnh con gửi sàn. Giải thích bằng sơ đồ đơn giản. Vì sao tốc độ là sống còn. |
| CH02 | Bản cập nhật cho một chương trình mới của NYSE | Tháng 7–8/2012, Knight phải cập nhật hệ thống để tham gia Retail Liquidity Program của NYSE (khởi động 01/08/2012). Mã mới thay vào chỗ mã Power Peg đã bỏ dùng nhiều năm. |
| CH03 | Một trong tám (đóng vòng 1) | Kỹ thuật viên không chép mã mới lên một trong tám máy chủ; không có người thứ hai duyệt; không có quy trình bằng văn bản; cờ cũ bị dùng lại, nên máy thứ tám bật mã cũ. |
| CH04 | 97 email lúc 8 giờ sáng (đóng vòng 2) | Từ khoảng 8:01 sáng, hệ thống gửi 97 email "Power Peg disabled" trước giờ mở cửa. Email không được thiết kế làm cảnh báo, ít người đọc. Bài học: tín hiệu có mà không có đường dẫn đến hành động. |
| CH05 | 45 phút không có nút dừng | Máy thứ tám gửi lệnh con liên tục, không so với số lượng đã khớp. Hơn 4 triệu giao dịch trong 154 mã, hơn 397 triệu cổ phiếu; vị thế mua khoảng 3,5 tỷ đô trên 80 mã, bán khoảng 3,15 tỷ đô trên 74 mã. Công ty không có kiểm soát đối chiếu lệnh vào/ra, không có quy trình tự dừng. |
| CH06 | Thị trường cũng bị kéo theo | SEC: 75 mã, Knight chiếm hơn 20% khối lượng, giá nhích hơn 5%; 37 mã giá dịch hơn 10%. Người khác trên thị trường nhận giá tốt hơn hoặc xấu hơn. Vì sao nạn nhân không chỉ là Knight. |
| CH07 | Cái giá: 460 triệu đô và một tuần sinh tử | Khoản lỗ hơn 460 triệu đô (SEC) so với khoảng 440 triệu đô trước thuế trong báo cáo công ty (Wikipedia, cần đối chiếu). Ngày 05/08/2012 Knight huy động khoảng 400 triệu đô do Jefferies dẫn đầu; tháng 12/2012 đồng ý sáp nhập với Getco, hoàn tất tháng 07/2013. SEC phạt 12 triệu đô ngày 16/10/2013, vụ đầu tiên theo Rule 15c3-5. |
| CH08 | Kết: người xem rút ra gì | Trả lời câu hỏi trung tâm. Ba bài học kiểu kỹ thuật (triển khai có người duyệt thứ hai, xoá mã chết, cảnh báo có người nhận), không đổ lỗi cá nhân, không lời khuyên đầu tư. Quay lại đồng hồ và tám máy chủ. |

### Nhịp sau phút đầu
Mỗi cửa sổ 30 giây có một mới: mã chết, cờ trùng, máy thứ tám, email, lệnh con, vị thế, giá nhích, huy động vốn, mức phạt. Đánh dấu `{beat: ...}` khi viết script.

---

## 4. Nguồn chính và tư liệu hình

### Nguồn (trạng thái mở ngày 15/11/2026)
1. **[Sơ cấp, lệnh xử lý của SEC: ĐÃ MỞ, đã đọc toàn văn bằng trình đọc PDF cục bộ]** In the Matter of Knight Capital Americas LLC, Release No. 34-70694:
   https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf
   Các số trong CH03–CH06 lấy từ đoạn 12–22 của lệnh này.
2. **[Sơ cấp, thông cáo của SEC: ĐÃ MỞ]** SEC Charges Knight Capital With Violations of Market Access Rule (phạt, khoản lỗ, trích Andrew Ceresney và Daniel Hawke):
   https://www.sec.gov/newsroom/press-releases/2013-222
3. **[Tổng hợp: ĐÃ MỞ]** Wikipedia, Knight Capital Group (huy động vốn, sáp nhập Getco, số 440 và 460 triệu đô):
   https://en.wikipedia.org/wiki/Knight_Capital_Group
4. **[Phân tích kỹ sư, WebFetch lỗi DNS; script plan_sources mở được: chưa đọc nội dung, chỉ tham khảo, không dựa]** Doug Seven, Knightmare: A DevOps Cautionary Tale:
   https://dougseven.com/2014/04/17/knightmare-a-devops-cautionary-tale/

**Khoảng trống:** còn thiếu một nguồn báo độc lập đã mở được từ 01–03/08/2012 (Reuters, Bloomberg, NYT, WSJ) cho số 440 triệu đô (thử tải một bài NYT đã thất bại, URL đoán không đúng, đã bỏ), cú huy động vốn và lời công ty. Cần tìm trước script; nếu không có thì dùng số của SEC và ghi rõ "theo hồ sơ SEC".

### Tư liệu hình (đếm bằng API Commons, xem bảng tự động cuối file)
- **Commons, sàn giao dịch và thị trường:**
  https://commons.wikimedia.org/wiki/Category:New_York_Stock_Exchange
  https://commons.wikimedia.org/wiki/Category:Stock_exchanges
  https://commons.wikimedia.org/wiki/Category:Stock_market
- **Commons, máy chủ và trung tâm dữ liệu (minh hoạ khái niệm; đã xác nhận tồn tại, số lượng lớn):**
  https://commons.wikimedia.org/wiki/Category:Server_rooms
  https://commons.wikimedia.org/wiki/Category:Data_centers
- **Đồ hoạ tự dựng (bắt buộc):** đồng hồ 45 phút, sơ đồ 8 máy chủ (7 xanh 1 đỏ), bộ đếm email 97, sơ đồ lệnh cha thành lệnh con, counter 4 triệu giao dịch, thanh vị thế mua/bán, dòng thời gian 8:01 → 9:30 → 10:15 (chỉ khi nguồn xác nhận mốc cuối; hiện SEC chỉ nói "khoảng 45 phút").
- Không có ảnh tự do của người trong vụ; không ảnh AI người thật. Không tên cá nhân kỹ thuật viên.
- Soi từng ảnh: bỏ ảnh có biển hiệu/hãng nổi bật, ảnh licence không hợp lệ (chỉ PD/CC0/CC BY/BY-SA); ảnh sàn NYSE dùng làm bối cảnh chung và ghi nhãn minh hoạ.
- **Ước tính:** ít nhất 15–20 ảnh/clip tự do dùng được; số chính xác nằm ở bảng tự động.

---

## 5. Đóng gói

### 5a. Ba phương án tiêu đề (tối đa 60 ký tự)
Mỗi phương án ghi đối tượng, lời hứa, bằng chứng, số ký tự.

1. `45 Phút Mất 460 Triệu Đô: Một Máy Chủ Quên Cập Nhật 2012` (56 ký tự). *Mẫu đồng hồ + cái giá.* Đối tượng: người quan tâm công nghệ và tiền. Lời hứa: biết chuyện gì xảy ra trong 45 phút đó. Bằng chứng: lệnh xử lý SEC (45 phút, 460 triệu đô, máy chủ thứ tám).
2. `97 Email Cảnh Báo Không Ai Đọc: Mất 460 Triệu Đô Năm 2012` (57 ký tự). *Mẫu nghịch lý (cảnh báo có mà vẫn mất).* Đối tượng: người làm kỹ thuật và quản lý. Lời hứa: biết vì sao cảnh báo không cứu được. Bằng chứng: lệnh xử lý SEC đoạn 19 (97 email, không ai xử lý).
3. `Quên Cập Nhật 1 Trong 8 Máy Chủ: Mất 460 Triệu Đô Năm 2012` (58 ký tự). *Mẫu bi kịch (một sơ suất nhỏ, kết cục lớn).* Đối tượng: người xem tò mò về sự cố công nghệ. Lời hứa: biết sơ suất đó là gì. Bằng chứng: lệnh xử lý SEC đoạn 15–17.

*Đề xuất:* phương án 1 làm chính, Test & Compare với phương án 2. Phương án 2 dùng "mất 460 triệu đô" (không viết "mất công ty": SEC không ghi phá sản, Knight được cứu bằng huy động vốn). 

### 5b. Hai ý thumbnail (tối đa 4 chữ)
- **T1:** sơ đồ tám ô, bảy ô xanh một ô đỏ lớn; chữ `1 TRONG 8` (3 chữ). Một vật thể: ô đỏ.
- **T2:** đồng hồ số tối kèm chữ `45 PHÚT` và `$460M` (2 cụm). Một vật thể: đồng hồ.

---

## 6. Rủi ro

- **Nguồn:** số 460 triệu đô lấy từ SEC; nguồn khác dùng 440 triệu đô (số trước thuế do công ty công bố) — phải nói rõ "theo SEC" và giải thích lệch số, không trộn. Còn thiếu báo độc lập mở được.
- **Chưa xác minh được:** mốc đầu và mốc cuối đúng của 45 phút (SEC chỉ nói "khoảng 45 phút"), thời điểm Knight dừng hệ thống, diễn biến "rollback làm tệ hơn" thường thấy trên mạng (không có trong lệnh xử lý; không dùng nếu không có nguồn).
- **Đạo đức:** không nêu tên kỹ thuật viên, không đổ lỗi cho cá nhân; lệnh xử lý nói thiếu quy trình và kiểm soát của công ty. Nhân viên Knight mất việc sau vụ việc: không dựng cảnh bi kịch ngoài nguồn.
- **Phù hợp kênh:** đây là phần mềm giao dịch tự động, không phải AI; cần nói thẳng ở cold open hoặc CH01 ("thuật toán tự động, không phải AI") để khỏi bị hiểu nhầm; nếu chủ kênh muốn đúng tuyệt đối AI thì đổi đề tài.
- **Trùng:** `mim-binance-6-3-ty-20-phut` cũng là "20 phút / mất tiền tỷ" và có từ "đồng hồ"; cần khác cách kể: ở Binance có kẻ tấn công, ở đây không ai tấn công. Không dùng lại ngôn ngữ "kỷ lục" hay hình đồng hồ giống hệt (đổi tông màu và kiểu số).
- **Đầu tư:** không khuyên mua bán, không nhận xét giá cổ phiếu hiện tại.
- **Hình:** ảnh NYSE là bối cảnh chung; không gây hiểu nhầm là chính sàn đã gây ra lỗi (sàn không có lỗi trong lệnh xử lý).
