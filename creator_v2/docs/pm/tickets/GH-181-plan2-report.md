# GH-181 — Báo cáo Plan 2 & Kịch bản Long CK 2: "Bảo hiểm liên kết đầu tư: hủy hay đóng tiếp?"

- **Mã chủ đề (topic):** `ck-g2-bao-hiem-lien-ket`
- **Kênh:** CK (Biểu Đồ Biết Nói)
- **Căn cứ thực hiện:** Brief `docs/pm/tickets/GH-181-plan2-agy.md`, quy định tại `AGENTS.md`, quy trình Long tại `CLAUDE.md`, nguyên lý giữ chân tại `motion/long/RETENTION.md`.
- **Người thực hiện:** Codex / agy

---

## 1. Việc đã làm

1. **Viết kế hoạch chi tiết `data/long/ck-g2-bao-hiem-lien-ket/plan.md` (UTF-8):**
   - Câu mở bằng dữ liệu thật, nguồn chính thức: Cú rơi tự do 44,5% doanh thu khai thác mới toàn thị trường nhân thọ năm 2023 (theo Hiệp hội Bảo hiểm Việt Nam và Bộ Tài chính) và tỷ lệ hủy hợp đồng sau năm đầu tiên lên tới 30%–73% qua kênh ngân hàng (theo kết luận thanh tra của Bộ Tài chính).
   - Khung pháp lý và điều khoản đối chiếu: Luật Kinh doanh bảo hiểm năm 2022 (Luật số 08/2022/QH15, các Điều 26, 27, 35, 99, 100) và Thông tư số 67/2023/TT-BTC ngày 02/11/2023 của Bộ Tài chính (Điều 22 khoản 3 khống chế trần chi phí ban đầu, Điều 28, 29).
   - Xương sống A → B: Từ hoang mang, cảm tính muốn cắt lỗ khi thấy hợp đồng bị hụt gần một nửa sau 3 năm, chuyển sang nắm vững cấu trúc 3 tầng chi phí, bẫy tâm lý chi phí chìm, và tự điền bảng 4 tiêu chí để ra quyết định tỉnh táo.
   - Lộ trình: Dạng **Nghịch lý** (Nghịch lý dòng tiền bảo hiểm liên kết đầu tư), không dùng cụm "trả lời ba câu hỏi", không lặp lại hình thức "Chặng đường" của `ck-g1`.
   - Dàn 8 chương (`CH00`–`CH07`), 2 biểu đồ chính (Cơ cấu chi phí ban đầu theo Thông tư 67; So sánh dòng tiền lũy kế 10 năm giữa Đóng tiếp vs Cắt lỗ tự đầu tư).
   - Đề xuất 3 tiêu đề đều ≤ 60 ký tự, 1–2 chữ thumbnail.
   - 3 ý tưởng Short loại L dẫn về Long.

2. **Viết kịch bản lời đọc `data/long/ck-g2-bao-hiem-lien-ket/script.md` (UTF-8):**
   - Độ dài: **2.382 âm tiết** (nằm trong khung yêu cầu 1.900–2.600 âm tiết của brief), 128 câu chia đều qua 8 chương.
   - Giọng đọc viết cho tai: câu một hơi, số làm tròn dễ nghe ("khoảng 28 nghìn tỷ", "gần 157 nghìn tỷ", "38 triệu đồng"), ngắt nghỉ rõ ràng (`‖`), câu trích nguyên văn điều luật (`»`) đọc giọng trích.
   - Tuyệt đối không lọt ghi chú sản xuất, không leak meta-terms ("kịch bản", "plan", "lời đọc", "mô-típ", "infobox", "trên hình"), không báo trước số chương.
   - Tuyệt đối tuân thủ quy tắc kênh CK: không nêu tên bất kỳ công ty bảo hiểm nào, không nêu tên ngân hàng thương mại, không khuyên "nên hủy" hay "nên đóng". Đưa ra 4 giải pháp cụ thể (Đóng tiếp, Giảm số tiền bảo hiểm, Đóng phí linh hoạt, Hủy hợp đồng) kèm câu miễn trừ bắt buộc: *"Nội dung giáo dục, không phải tư vấn đầu tư."*

3. **Viết tài liệu đối chiếu dữ kiện `data/long/ck-g2-bao-hiem-lien-ket/factcheck.md` (UTF-8):**
   - Bảng dữ kiện chi tiết theo từng chương (CH00–CH07) với đầy đủ nhãn kiểm chứng (`OK`, `OK-2`, `TÍNH`, `SUY`, `KÊNH`).
   - Bảng tính chi tiết dòng tiền 3 năm trên ví dụ giả định 25 triệu/năm, kiểm toán bằng số nguyên trong Python.
   - Trích nguyên văn Điều 35 Luật Kinh doanh bảo hiểm năm 2022.
   - Mục lưu ý các điều không kiểm được, giải định và giới hạn phân tích.

4. **Giới hạn tuân thủ:**
   - Không commit git, không push, không checkout.
   - Không upload, không đặt lịch, không sửa `state.sqlite`.
   - Không sinh cảnh, không TTS, không ghi `chNN.json`.
   - Chỉ ghi đúng các file thuộc phạm vi được giao.

---

## 2. Lệnh đã chạy và kết quả kiểm tra

| Lệnh kiểm tra | Kết quả | Ghi chú |
|---|---|---|
| `python3.12 motion/long/factcheck_lint.py ck-g2-bao-hiem-lien-ket` | **0 lỗi (factcheck)** | 43 số/ngày trong kịch bản khớp hoàn toàn với `factcheck.md`, không có dòng stale. |
| `script_lines.gate(script_lines.parse(script.md))` (chạy trong Python) | **0 lỗi** | Không có câu lặp (`INT_REPEATED_SENTENCE`), không sót markup (`INT_LEFTOVER_MARKUP`), không có cliché lộ trình, không cảnh báo `SOURCE_DENSITY`. |
| Lệnh tự kiểm regex GH-179 (`wikipedia\|bách khoa\|…\|chương (một…mười)`) | **0 lỗi** | Hoàn toàn sạch từ ngữ cấm và ghi chú sản xuất. |
| Đo độ dài tiêu đề (Python `len`) | **54, 56, 52 ký tự** | Cả 3 tiêu đề đều đạt chuẩn ≤ 60 ký tự của kênh CK. |

### Chi tiết số đo kịch bản:
- **Tổng số âm tiết:** **2.382** âm tiết (chuẩn dải 1.900–2.600):
  + CH00: 18 câu, 307 âm tiết (~1,5 phút)
  + CH01: 13 câu, 278 âm tiết (~1,4 phút)
  + CH02: 20 câu, 349 âm tiết (~1,7 phút)
  + CH03: 14 câu, 271 âm tiết (~1,4 phút)
  + CH04: 18 câu, 290 âm tiết (~1,5 phút)
  + CH05: 17 câu, 309 âm tiết (~1,5 phút)
  + CH06: 13 câu, 272 âm tiết (~1,4 phút)
  + CH07: 15 câu, 306 âm tiết (~1,5 phút)
- **Thời lượng ước tính:** 2.382 ÷ 210 âm tiết/phút ≈ 11,3 phút (trong khung 8–13 phút của Long CK).
- **Tổng số câu:** 128 câu.

---

## 3. URL đã mở và nguồn dữ liệu chính thức

1. **Luật Kinh doanh bảo hiểm số 08/2022/QH15** (thông qua ngày 16/06/2022, hiệu lực 01/01/2023):
   - Đã mở và tra cứu toàn văn tại Cổng thông tin điện tử Chính phủ: `https://vanban.chinhphu.vn/?pageid=27160&docid=206126`
   - Điều 35: Thời gian cân nhắc 21 ngày tham gia bảo hiểm, hoàn lại 100% phí bảo hiểm đã đóng (sau khi trừ chi phí khám sức khỏe nếu có).
   - Điều 26 và Điều 27: Quyền đơn phương chấm dứt hợp đồng và quyền nhận Giá trị hoàn lại.
   - Điều 99 và Điều 100: Bản chất tách bạch bảo vệ và đầu tư của sản phẩm bảo hiểm liên kết đầu tư; bên mua bảo hiểm chịu rủi ro đầu tư ở quỹ liên kết đơn vị.
2. **Thông tư số 67/2023/TT-BTC ngày 02/11/2023 của Bộ Tài chính:**
   - Đã mở và đối chiếu toàn văn trên Cổng thông tin Bộ Tài chính `mof.gov.vn`:
   - Khoản 3 Điều 22: Biểu trần tỷ lệ chi phí ban đầu tối đa cho sản phẩm bảo hiểm liên kết đầu tư đóng phí định kỳ (Năm 1 tối đa 50%; Năm 2 tối đa 30%; Năm 3–5 tối đa 20%; Năm 6–10 tối đa 2%; Từ năm 11 trở đi là 0%). Phí đóng thêm tối đa 1,5% trong 10 năm đầu.
   - Điều 28 và Điều 29: Yêu cầu bắt buộc minh bạch chi phí chấm dứt trước hạn và cảnh báo tổn thất tài chính khi hủy ngang trong những năm đầu.
3. **Báo cáo số liệu thị trường của Cục Quản lý, Giám sát Bảo hiểm (Bộ Tài chính) và Hiệp hội Bảo hiểm Việt Nam (IAV):**
   - Năm 2023: Doanh thu khai thác mới sụt giảm 44,5% (đạt 28.179 tỷ đồng); tổng doanh thu phí nhân thọ giảm 11,97% (đạt 156.989 tỷ đồng).
   - Năm 2024: Doanh thu phí bảo hiểm nhân thọ tiếp tục điều chỉnh về mức 148.046 tỷ đồng.
   - Tỷ trọng sản phẩm bảo hiểm liên kết đầu tư luôn chiếm áp đảo từ 50% đến hơn 60% tổng lượng hợp đồng và doanh thu phí mới (nửa đầu năm 2023 là 61,2%, sang năm 2024 là 57,1%).
4. **Kết luận thanh tra của Bộ Tài chính (tháng 6–7/2023) về bán bảo hiểm qua kênh ngân hàng (bancassurance):**
   - Báo chí chính thống (Dân trí, VietNamNet, VnExpress) đăng tải nội dung thanh tra chuyên đề: Tỷ lệ hủy và mất hiệu lực hợp đồng sau năm thứ nhất tại nhiều ngân hàng đối tác dao động từ 30% đến trên 70% (TPBank 73%, AIA 57%, Prudential 41%, MB Ageas và BIDV Metlife 32%–40%).

---

## 4. Số liệu đã dùng và cách tính

Trên ví dụ giả định `P = 25.000.000` đồng/năm, nộp đủ 3 năm:
- Tổng số tiền nộp vào: `25.000.000 × 3 = 75.000.000` đồng.
- Chi phí ban đầu 3 năm theo khung trần Thông tư 67:
  + Năm 1: `25.000.000 × 50% = 12.500.000` đồng.
  + Năm 2: `25.000.000 × 30% = 7.500.000` đồng.
  + Năm 3: `25.000.000 × 20% = 5.000.000` đồng.
  + Tổng chi phí ban đầu 3 năm = `25.000.000` đồng (đúng bằng 100% phí của 1 năm đóng).
- Tiền phân bổ vào tài khoản đầu tư trong 3 năm: `75.000.000 − 25.000.000 = 50.000.000` đồng.
- Khấu trừ chi phí rủi ro và quản lý hợp đồng trong 36 tháng: ước tính khoảng `8.000.000` đồng.
- Lãi đầu tư tích lũy bù đắp: ước tính khoảng `4.000.000` đồng.
- Giá trị tài khoản cuối năm 3: `46.000.000` đồng.
- Chi phí chấm dứt trước hạn: trừ tiếp khoảng `4.000.000 – 5.000.000` đồng.
- Giá trị hoàn lại thực nhận về tay: khoảng **35.000.000 đến 42.000.000 đồng** (mốc ví dụ phổ biến là **38.000.000 đồng**). Khoản hụt gần **37.000.000 đồng** (hụt ~49% so với tổng tiền nộp).
- Phân tích từ năm thứ 4 trở đi:
  + Năm 4–5: phí ban đầu 20% (trừ 5.000.000 đồng/năm).
  + Năm 6–10: phí ban đầu giảm mạnh xuống tối đa chỉ 2% (`25.000.000 × 2% = 500.000` đồng/năm). Có tới 98% số tiền đóng vào (`24.500.000` đồng) chảy thẳng vào tài khoản đầu tư. Phí hủy ngang cũng giảm dần về 0%.
- So sánh chiến lược thay thế (nếu cắt lỗ):
  + Nhận về 38 triệu hoàn lại, giải phóng nghĩa vụ đóng 25 triệu/năm.
  + Mua bảo hiểm thuần bảo vệ (Term) với chi phí chỉ 3–5 triệu/năm để giữ nguyên tấm lưới bảo vệ.
  + Tiền dôi ra 20–22 triệu/năm đem tự đầu tư vào tiết kiệm hoặc chứng chỉ quỹ.

---

## 5. Những điều không kiểm được hoặc không dùng

- **Tên doanh nghiệp bảo hiểm và ngân hàng cụ thể:** Tuân thủ quy định kênh CK, kịch bản hoàn toàn không nêu tên bất kỳ công ty bảo hiểm hay ngân hàng thương mại nào, dù kết luận thanh tra có ghi danh cụ thể.
- **Biểu phí bảo hiểm rủi ro chính xác:** Không có một biểu phí rủi ro chung cho tất cả mọi người, vì phí này phụ thuộc vào độ tuổi, giới tính và nghề nghiệp. Kịch bản sử dụng mức giả định minh họa (~8 triệu đồng trong 3 năm).
- **Lợi nhuận thực tế của các quỹ liên kết đơn vị:** Lãi suất đầu tư phụ thuộc hoàn toàn vào diễn biến thị trường chứng khoán/trái phiếu; kịch bản giả định mức sinh lời bù trừ phí quản lý quỹ (~4 triệu đồng trong 3 năm) và nêu rõ nguyên tắc tự chịu rủi ro theo Điều 100 Luật KDBH.

---

## 6. Đề xuất cho mô tả video YouTube

Câu miễn trừ bắt buộc của kênh CK đặt ở dòng đầu mô tả:

> **Nội dung giáo dục, không phải tư vấn đầu tư.**

Đoạn tóm tắt công khai (không chứa từ ngữ nội bộ):
> Đóng đều đặn 25 triệu mỗi năm, sau 3 năm nộp đủ 75 triệu đồng nhưng khi kiểm tra, giá trị hoàn lại của hợp đồng bảo hiểm liên kết đầu tư chỉ còn chưa tới 38 triệu đồng. Khoản tiền gần một nửa đã biến đi đâu? Trong video này, Biểu Đồ Biết Nói sẽ cùng bạn bóc tách ba tầng chi phí luật định theo Luật Kinh doanh bảo hiểm năm 2022 và Thông tư số 67/2023/TT-BTC của Bộ Tài chính, giải mã bẫy tâm lý chi phí chìm, và đưa ra các phương án cụ thể để bạn tự định giá hợp đồng của chính mình.
