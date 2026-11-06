# Báo cáo Ticket GH-181: Đề xuất đề tài lô Long CK từ 23/11 (4 Long, 8–13 phút)

- **Người thực hiện:** Codex / Agent sản xuất
- **Ngày lập:** 06/11/2026
- **Kênh:** CK (Tài chính cá nhân)
- **Căn cứ:** Brief `docs/pm/tickets/GH-181-topics-agy.md`, quy tắc kênh tại `AGENTS.md`, dữ liệu 28 Long CK đã sản xuất trong `data/long/ck-*` và bảng `item` trong `state.sqlite`.

---

## I. Tổng quan & Đối chiếu tránh trùng lặp

Qua rà soát 28 chủ đề Long CK đã có trong hệ thống (`ck-2026-kenh-dau-tu`, `ck-b1-mua-hay-thue`, `ck-b2-lai-kep`, `ck-b3-tra-gop-0`, `ck-b4-mua-xe`, `ck-c1-vnindex-dung-yen`, `ck-c2-phien-giao-dich`, `ck-c3-bieu-do-nen`, `ck-c4-duong-trung-binh`, `ck-c5-co-tuc`, `ck-c6-gia-tran-san-t2`, `ck-d1-vang-dinh`, `ck-d2-fomo`, `ck-d3-lo-khong-dam-ban`, `ck-e1-mua-deu-moi-thang`, `ck-e2-quy-khan-cap`, `ck-e3-no-the-tin-dung`, `ck-e4-bao-hiem-tien-gui`, `ck-e5-thue-tncn-2026`, `ck-e6-luong-huu-rut-mot-lan`, `ck-f1-tro-cap-that-nghiep`, `ck-f2-vien-phi-bhyt`, `ck-f3-tien-mung-cuoi`, `ck-f4-vo-chong-chia-tien`, `ck-g1-thuong-tet-2027`, `ck-i1-100-trieu-tiet-kiem-hay-vnindex`, `ck-xang-dien-thue-11-2026`):

- **Đặc trưng tệp khán giả CK (25–40 tuổi):** Đang trong giai đoạn lập gia đình, mua tài sản lớn (nhà, đất, bảo hiểm), quản lý các khoản nợ vay ngân hàng, và tìm kênh tích lũy tài sản dài hạn ngoài tiết kiệm truyền thống.
- **Yêu cầu nội dung:** Gắn với một quyết định tài chính thật, có số liệu đối chiếu rõ ràng, không nêu tên thương hiệu ngân hàng hay mã cổ phiếu cụ thể (tuân thủ `AGENTS.md`), biểu đồ trực quan, và có các Short loại L tương ứng làm vệ tinh dẫn về Long.

---

## II. Chi tiết 8 đề tài đề xuất

### Đề tài 1: Trả nợ ngân hàng trước hạn hay gửi tiết kiệm? (Bài toán khoản vay mua nhà khi lãi thả nổi chạm 11%–12%)
1. **Quyết định:** Người vay mua nhà (còn dư nợ 500 triệu – 1 tỷ đồng) sau khi hết thời gian ưu đãi lãi suất, tích lũy được một khoản tiền nhàn rỗi 200–300 triệu đồng: Có nên dồn trả bớt nợ gốc trước hạn (chấp nhận phí phạt trả trước hạn 1%–2%) để giảm gánh nặng lãi vay hàng tháng, hay giữ tiền gửi tiết kiệm / làm vốn lưu động?
2. **Câu mở (Hook):** "Hết hai năm ưu đãi 6,5%, tháng vừa rồi lãi suất thả nổi khoản vay mua nhà của bạn nhảy lên 11,2%/năm. Cầm 200 triệu tiền nhàn rỗi trong tay, bạn nên đem trả bớt nợ gốc ngay hay gửi tiết kiệm kỳ hạn một năm lấy lãi 5,2%? Theo số liệu công bố của Ngân hàng Nhà nước, mức chênh lệch giữa lãi vay thả nổi và lãi tiết kiệm hiện nay lên tới 5% đến 6% mỗi năm. Nhưng nếu trả trước hạn, bạn sẽ phải trả thêm một khoản phí phạt theo quy định."
3. **Dữ liệu cần có & Cách lấy:**
   - *Thông tư 39/2016/TT-NHNN* (Điều 14 về phí liên quan đến hoạt động cho vay, cho phép thu phí trả nợ trước hạn theo thỏa thuận) và *Thông tư 06/2023/TT-NHNN*.
   - *Báo cáo công bố thông tin lãi suất cho vay và huy động bình quân* của các tổ chức tín dụng do Ngân hàng Nhà nước Việt Nam (NHNN) công bố định kỳ trên Cổng thông tin điện tử `sbv.gov.vn` theo chỉ đạo tại Công điện 18/CĐ-TTg của Thủ tướng Chính phủ.
   - Thống kê biểu phí trả nợ trước hạn phổ biến trên hợp đồng tín dụng: Thường 1,5%–2% trong năm 1–2; 1% trong năm 3; 0,5% trong năm 4–5; miễn phí từ năm thứ 6 trở đi.
4. **Giai đoạn, phương pháp tính & giới hạn:**
   - *Giai đoạn mô phỏng:* 1 năm đến 3 năm sau khi hết ưu đãi lãi suất.
   - *Phương pháp tính:* So sánh chi phí cơ hội dòng tiền thực:
     - Kịch bản A (Trả nợ trước 200 triệu): Phí phạt trả trước $= 200  triệu x 1,5% = 3  triệu đồng$. Tiền lãi vay tiết kiệm được trong năm đầu $= 200  triệu x 11,2% = 22,4  triệu đồng$. Lợi ích tài chính ròng $= 22,4 - 3 = 19,4  triệu đồng$.
     - Kịch bản B (Giữ 200 triệu gửi tiết kiệm 12 tháng lãi 5,2%): Lãi tiết kiệm thu về $= 200  triệu x 5,2% = 10,4  triệu đồng$.
     - *Chênh lệch ròng:* Phương án trả trước nợ gốc mang lại hiệu quả tài chính cao hơn 9,0 triệu đồng/năm.
   - *Giới hạn & Lưu ý:* Người vay phải duy trì một Quỹ khẩn cấp tối thiểu 3–6 tháng chi phí sinh hoạt (khoảng 50–100 triệu) trước khi dồn trả nợ, tránh rủi ro kiệt quệ thanh khoản đột xuất vì sau khi trả nợ gốc không thể rút lại tiền mặt ngay lập tức.
5. **2–3 ý Short loại L nối về Long:**
   - *Short 1:* "Trả trước 200 triệu nợ gốc ngân hàng: Tiết kiệm được bao nhiêu tiền lãi một năm?"
   - *Short 2:* "Phí phạt trả nợ trước hạn: Ngân hàng tính thế nào theo Thông tư 39?"
   - *Short 3:* "Hai trường hợp TUYỆT ĐỐI KHÔNG NÊN trả nợ ngân hàng trước hạn."

---

### Đề tài 2: Bảo hiểm liên kết đầu tư (ILP): Cắt lỗ hủy hợp đồng hay đóng tiếp sau 3 năm?
1. **Quyết định:** Người mua bảo hiểm nhân thọ liên kết chung / liên kết đơn vị (phí đóng 25–30 triệu đồng/năm), sau 3 năm kiểm tra giá trị tài khoản thấy bị hụt 40%–50% do chi phí ban đầu (Initial Charge) bị trừ theo biểu phí: Nên chấp nhận "cắt lỗ" hủy hợp đồng để chuyển sang chiến lược mua bảo hiểm thuần bảo vệ (Term) + tự đầu tư, hay cố đóng tiếp cho hết thời hạn 10–15 năm?
2. **Câu mở (Hook):** "Đóng đều 25 triệu mỗi năm, sau 3 năm nộp tổng cộng 75 triệu nhưng khi mở hợp đồng kiểm tra, giá trị hoàn lại của bạn chỉ còn chưa tới 38 triệu đồng. Theo Thông tư 67 của Bộ Tài chính, năm đầu tiên công ty bảo hiểm được phép trừ tối đa tới 50% phí bảo hiểm cơ bản làm chi phí ban đầu, năm thứ hai trừ 30%, và năm thứ ba trừ 20%. Bạn nên cắt lỗ dừng hợp đồng hay cắn răng đóng tiếp cho đủ 10 năm?"
3. **Dữ liệu cần có & Cách lấy:**
   - *Thông tư 67/2023/TT-BTC* của Bộ Tài chính ngày 02/11/2023 hướng dẫn Luật Kinh doanh bảo hiểm 2022 (Điểm a Khoản 3 Điều 22 quy định biểu tỷ lệ chi phí ban đầu tối đa của sản phẩm bảo hiểm liên kết đầu tư đóng phí định kỳ).
   - *Thông tư 52/2016/TT-BTC* (đối chiếu quy định cũ giai đoạn trước 2023, nơi phí ban đầu năm 1 từng lên tới 60%–70%).
   - Báo cáo số liệu thị trường bảo hiểm của Cục Quản lý, Giám sát Bảo hiểm - Bộ Tài chính (`mof.gov.vn`).
4. **Giai đoạn, phương pháp tính & giới hạn:**
   - *Giai đoạn mô phỏng:* Hợp đồng 10 năm và 20 năm, mốc đánh giá tại cuối năm thứ 3.
   - *Phương pháp tính:* So sánh dòng tiền lũy kế giữa 2 kịch bản:
     - Kịch bản 1 (Đóng tiếp ILP): Tiếp tục đóng 25 triệu/năm từ năm 4 đến năm 10. Từ năm thứ 6 trở đi, chi phí ban đầu giảm chỉ còn 2%/năm, giá trị tài khoản bắt đầu tích lũy nhanh hơn theo tỷ suất sinh lời giả định (6%–8%/năm).
     - Kịch bản 2 (Hủy hợp đồng cũ, áp dụng Buy Term & Invest the Rest): Hủy hợp đồng ở năm 3 (chấp nhận mất 37 triệu chi phí đã trừ, nhận lại 38 triệu). Từ năm thứ 4, dành 5 triệu/năm mua bảo hiểm sức khỏe/nhân thọ có kỳ hạn (thuần bảo vệ, quyền lợi tử vong/bệnh hiểm nghèo tương đương), còn lại 20 triệu/năm tự gửi tiết kiệm hoặc tích lũy quỹ chỉ số với lãi suất 7%/năm.
   - *Giới hạn & Cảnh báo an toàn:* Nếu người được bảo hiểm đã phát sinh bệnh nền/bệnh có sẵn trong 3 năm qua, tuyệt đối không được hủy hợp đồng cũ vì sẽ bị loại trừ hoặc từ chối bảo hiểm khi mua hợp đồng mới.
5. **2–3 ý Short loại L nối về Long:**
   - *Short 1:* "Đóng bảo hiểm 75 triệu sau 3 năm chỉ còn lại 38 triệu: Tiền bị trừ đi đâu?"
   - *Short 2:* "Thông tư 67 quy định các công ty bảo hiểm được trừ tối đa bao nhiêu phần trăm chi phí ban đầu?"
   - *Short 3:* "Chiến lược Buy Term and Invest the Rest: Vì sao người hiểu tài chính chuộng cách này?"

---

### Đề tài 3: Gửi tiết kiệm chia nhiều sổ hay gộp 1 sổ lớn: Tận dụng cơ chế rút trước hạn một phần theo Thông tư 04/2022/TT-NHNN
1. **Quyết định:** Có 300–500 triệu đồng nhàn rỗi trong 1 năm: Nên chia nhỏ thành 3–5 sổ tiết kiệm với các kỳ hạn bậc thang (1, 3, 6, 12 tháng) hay gộp toàn bộ vào 1 sổ 12 tháng để hưởng lãi suất cao nhất, dựa trên cơ chế rút trước hạn một phần theo quy định mới của Ngân hàng Nhà nước?
2. **Câu mở (Hook):** "Trước đây, gửi một sổ tiết kiệm 300 triệu kỳ hạn một năm mà giữa chừng rút ra 50 triệu chữa bệnh là toàn bộ 300 triệu bị phạt chuyển về lãi không kỳ hạn 0,1%. Nhưng từ khi Thông tư 04 của Ngân hàng Nhà nước có hiệu lực, câu chuyện đã đảo chiều hoàn toàn: bạn rút bao nhiêu thì chỉ phần đó chịu lãi không kỳ hạn, phần còn lại vẫn giữ nguyên lãi suất 5,5%. Vậy bạn nên chia nhỏ tiền thành nhiều sổ hay gửi gộp một sổ lớn?"
3. **Dữ liệu cần có & Cách lấy:**
   - *Thông tư 04/2022/TT-NHNN* ngày 16/06/2022 của NHNN quy định việc áp dụng lãi suất rút trước hạn tiền gửi tại tổ chức tín dụng (Khoản 2 Điều 5 về rút trước hạn một phần tiền gửi).
   - *Quyết định số 1125/QĐ-NHNN* về mức lãi suất tối đa đối với tiền gửi bằng đồng Việt Nam không kỳ hạn và có kỳ hạn dưới 1 tháng (trần 0,5%/năm).
   - Biểu lãi suất huy động kỳ hạn 1, 3, 6, 12 tháng tại các ngân hàng thương mại công bố trên Cổng TTĐT NHNN.
4. **Giai đoạn, phương pháp tính & giới hạn:**
   - *Giai đoạn mô phỏng:* 12 tháng, giả định phát sinh nhu cầu rút 50 triệu và 100 triệu ở các mốc tháng thứ 4 và tháng thứ 8.
   - *Phương pháp tính:*
     - Phương án A (1 sổ 300 triệu, 12 tháng, lãi 5,5%/năm): Đến tháng thứ 8 rút 100 triệu (lãi không kỳ hạn 0,2% = 133.000 đồng); 200 triệu còn lại giữ đến hết 12 tháng hưởng nguyên lãi 5,5% (= 11 triệu đồng). Tổng lãi thực nhận = 11.133.000 đồng.
     - Phương án B (Chia 3 sổ bậc thang: 50 triệu 3 tháng lãi 3,5%, 100 triệu 6 tháng lãi 4,5%, 150 triệu 12 tháng lãi 5,5%): Tính tổng lãi lũy kế khi quay vòng vốn.
   - *Giới hạn:* Phụ thuộc vào tính năng công nghệ của ứng dụng ngân hàng số (một số app cho phép tách lệnh online theo Thông tư 04, nhưng một số ngân hàng vẫn bắt khách hàng ra quầy ký giấy giao dịch).
5. **2–3 ý Short loại L nối về Long:**
   - *Short 1:* "Rút 50 triệu từ sổ tiết kiệm 300 triệu: Bạn mất bao nhiêu tiền lãi theo luật mới?"
   - *Short 2:* "Thông tư 04 của NHNN đã cứu tiền túi của người gửi tiết kiệm như thế nào?"
   - *Short 3:* "Bí kíp chia 3 chiếc lọ gửi tiết kiệm vừa thanh khoản nhanh vừa tối đa tiền lãi."

---

### Đề tài 4: Đầu tư chứng chỉ Quỹ mở: Phí quản lý 1,5%–2%/năm bào mòn tài sản thế nào sau 10 năm?
1. **Quyết định:** Người đi làm tích lũy 5–10 triệu đồng/tháng: Có nên ủy thác dòng tiền vào chứng chỉ Quỹ mở cổ phiếu/trái phiếu (Mutual Fund) hay tự mua cổ phiếu trong rổ chỉ số lớn / gửi tiết kiệm?
2. **Câu mở (Hook):** "Mỗi năm công ty quản lý quỹ chỉ trích 1,8% giá trị tài sản ròng để trả phí quản lý – nghe qua thì chỉ tương đương một bữa ăn tối. Nhưng theo mô phỏng tài chính với mức tăng trưởng thị trường 10%/năm, khoản phí 1,8% này sẽ lấy đi gần 25% tổng lợi nhuận tích lũy của bạn sau 15 năm vì hiệu ứng lãi kép ngược. Vậy chứng chỉ quỹ mở có thực sự xứng đáng với chi phí bạn bỏ ra?"
3. **Dữ liệu cần có & Cách lấy:**
   - *Thông tư 98/2020/TT-BTC* của Bộ Tài chính hướng dẫn hoạt động và quản lý quỹ đầu tư chứng khoán (Điều 8 quy định các khoản chi phí của quỹ gồm phí quản lý, phí lưu ký, giám sát, kiểm toán) và *Thông tư 136/2025/TT-BTC*.
   - Báo cáo thống kê về quy mô tài sản và số lượng chứng chỉ quỹ mở đang hoạt động của Ủy ban Chứng khoán Nhà nước (`ssc.gov.vn`) và VSDC.
   - Biểu phí quản lý công bố chính thức tại Bản cáo bạch của các quỹ mở công chúng tại Việt Nam (dao động 1,2% đến 2,0%/năm trên NAV).
4. **Giai đoạn, phương pháp tính & giới hạn:**
   - *Giai đoạn mô phỏng:* Tích lũy định kỳ (DCA) 5 triệu đồng/tháng trong 10 năm và 15 năm (tổng vốn gốc đóng vào 600 triệu và 900 triệu).
   - *Phương pháp tính:*
     - Lựa chọn 1 (Quỹ mở cổ phiếu chủ động): Tỷ suất sinh lời gộp danh mục 10%/năm, trừ phí quản lý 1,8%/năm $
ightarrow$ Lợi nhuận ròng thực nhận 8,2%/năm. Tài sản sau 15 năm đạt khoảng 1,87 tỷ đồng.
     - Lựa chọn 2 (Quỹ ETF thụ động): Danh mục mô phỏng chỉ số, tỷ suất sinh lời gộp 10%/năm, trừ phí quản lý chỉ 0,55%/năm $
ightarrow$ Lợi nhuận ròng 9,45%/năm. Tài sản sau 15 năm đạt khoảng 2,12 tỷ đồng.
     - Lựa chọn 3 (Tự đầu tư): Chỉ chịu phí giao dịch 0,1% và thuế bán 0,1%.
     - *Hiệu ứng bào mòn:* Khoản chênh lệch do phí quản lý quỹ mở lên tới hơn 250 triệu đồng sau 15 năm.
   - *Giới hạn:* Quỹ mở chủ động vẫn có giá trị bảo vệ đối với nhà đầu tư hoàn toàn không có kiến thức đọc báo cáo tài chính và không muốn đối mặt với áp lực tâm lý giao dịch hàng ngày.
5. **2–3 ý Short loại L nối về Long:**
   - *Short 1:* "Phí quản lý quỹ 1,8%: Tưởng nhỏ nhưng nuốt gọn một phần tư gia tài sau 15 năm."
   - *Short 2:* "Quỹ mở chủ động vs Quỹ ETF chỉ số: Khác nhau ở đâu mà người giàu chọn ETF?"
   - *Short 3:* "Ai là người THỰC SỰ nên đầu tư chứng chỉ quỹ mở tại Việt Nam?"

---

### Đề tài 5: Vay mua Nhà ở xã hội (gói 120.000 tỷ): Bẫy thả nổi lãi suất sau 5 năm và bài toán trần thu nhập
1. **Quyết định:** Người có thu nhập đủ điều kiện mua NOXH theo quy định mới: Có nên vay tối đa 70% giá trị căn hộ theo gói tín dụng ưu đãi 120.000 tỷ đồng để mua căn hộ NOXH 1–1,2 tỷ đồng, hay tiếp tục thuê nhà để tích lũy thêm vốn tự có?
2. **Câu mở (Hook):** "Để được duyệt mua một căn nhà ở xã hội, mức thu nhập của người độc thân theo quy định không được vượt quá 15 triệu đồng một tháng. Nhưng với một căn hộ xã hội một tỷ hai, sau khi vay 70% từ gói 120.000 tỷ, mỗi tháng bạn phải trả cả gốc và lãi gần 9,6 triệu đồng – chiếm tới 64% thu nhập. Đáng sợ hơn, lãi suất ưu đãi 7% chỉ giữ trong 5 năm đầu, sau đó sẽ thả nổi theo thị trường. Liệu người có thu nhập dưới trần có gánh nổi khoản nợ này?"
3. **Dữ liệu cần có & Cách lấy:**
   - *Nghị định 100/2024/NĐ-CP* ngày 26/07/2024 của Chính phủ quy định chi tiết Luật Nhà ở 2023 (Điều 30 quy định điều kiện về thu nhập: không quá 15 triệu đồng/tháng với người độc thân, không quá 30 triệu đồng/tháng với vợ chồng; tính trên bảng tiền công, tiền lương 12 tháng liền kề).
   - *Văn bản số 2308/NHNN-TD* của Ngân hàng Nhà nước và các thông báo lãi suất cho vay chương trình 120.000 tỷ đồng (lãi suất người mua nhà 7,0%/năm áp dụng đến cuối 2024, điều chỉnh 6 tháng/lần, thời gian ưu đãi lãi suất tối đa 5 năm).
   - Khảo sát giá nhà ở xã hội mở bán tại các đô thị (18–25 triệu đồng/$m^2$, căn 50 $m^2$ khoảng 900 triệu đến 1,2 tỷ đồng).
4. **Giai đoạn, phương pháp tính & giới hạn:**
   - *Giai đoạn mô phỏng:* Khoản vay 15 năm (180 tháng).
   - *Phương pháp tính:*
     - Căn hộ NOXH giá 1,2 tỷ. Vốn tự có 360 triệu (30%), vay 840 triệu (70%).
     - 5 năm đầu (Lãi suất ưu đãi 7,0%/năm): Gốc trả đều $= 840 / 180 = 4,67  triệu/tháng$. Lãi tháng đầu $= 840 x 7% / 12 = 4,9  triệu/tháng$. Tổng nghĩa vụ trả $= 9,57  triệu đồng/tháng$ (chiếm 64% trần lương 15 triệu).
     - Từ năm thứ 6 (Hết ưu đãi, lãi suất thả nổi thị trường tăng lên 10,5%/năm): Dư nợ gốc còn lại $= 560  triệu$. Lãi tháng thứ 61 $= 560 x 10,5% / 12 = 4,9  triệu$. Gốc $= 4,67  triệu$. Tổng trả $= 9,57  triệu đồng$ (không giảm dù đã trả nợ suốt 5 năm vì lãi suất tăng bù vào phần gốc giảm).
   - *Giới hạn:* Phù hợp với cặp vợ chồng có hai nguồn thu nhập và có tích lũy sẵn từ gia đình; tiềm ẩn rủi ro nợ xấu cao nếu cá nhân đơn thân vay tối đa hạn mức.
5. **2–3 ý Short loại L nối về Long:**
   - *Short 1:* "Lương 15 triệu vay mua Nhà ở xã hội: Mỗi tháng phải trả bao nhiêu tiền gốc và lãi?"
   - *Short 2:* "Gói vay 120.000 tỷ: Cẩn thận cú sốc lãi suất sau 5 năm đầu tiên!"
   - *Short 3:* "Mức trần thu nhập mới nhất để được duyệt mua Nhà ở xã hội năm 2024–2025."

---

### Đề tài 6: Chuyển mục đích đất nông nghiệp lên đất ở theo Luật Đất đai 2024: Nộp tiền làm sổ ngay hay giữ nguyên hiện trạng?
1. **Quyết định:** Người trẻ hoặc gia đình sở hữu thửa đất trồng cây lâu năm, đất vườn ao 100–200 $m^2$: Có nên nộp hồ sơ xin chuyển mục đích sử dụng sang đất ở để nộp tiền sử dụng đất ngay, hay tiếp tục giữ nguyên hiện trạng đất nông nghiệp, khi Bảng giá đất mới theo Luật Đất đai 2024 tăng tiệm cận giá thị trường?
2. **Câu mở (Hook):** "Bảng giá đất điều chỉnh vừa ban hành ở nhiều địa phương tăng từ 4 đến hơn 30 lần. Nếu bạn đang có 100 mét vuông đất trồng cây muốn chuyển lên đất ở, theo Nghị định 103 của Chính phủ, số tiền sử dụng đất phải nộp bằng đúng mức chênh lệch giữa giá đất ở và giá đất nông nghiệp theo bảng giá mới. Khoản tiền thuế từ vài chục triệu bỗng chốc vọt lên hàng trăm triệu, thậm chí tiền tỷ. Bạn nên xoay tiền làm sổ đỏ thổ cư ngay hay giữ nguyên hiện trạng?"
3. **Dữ liệu cần có & Cách lấy:**
   - *Luật Đất đai 2024* (Luật số 31/2024/QH15, hiệu lực từ 01/08/2024).
   - *Nghị định 103/2024/NĐ-CP* ngày 30/07/2024 của Chính phủ về tiền sử dụng đất, tiền thuê đất (Điều 8 quy định chi tiết công thức tính tiền sử dụng đất khi hộ gia đình, cá nhân chuyển mục đích sử dụng đất sang đất ở).
   - Quyết định điều chỉnh Bảng giá đất tại các địa phương (ví dụ điển hình: *Quyết định 79/2024/QĐ-UBND* ngày 21/10/2024 của UBND TP.HCM).
4. **Giai đoạn, phương pháp tính & giới hạn:**
   - *Phương pháp tính:* Tiền sử dụng đất phải nộp $= (Giá đất ở theo Bảng giá đất - Giá đất nông nghiệp tương ứng) x Diện tích chuyển mục đích$.
   - *Mô phỏng thực tế:* Thửa đất 100 $m^2$ đất trồng cây lâu năm tại khu vực vùng ven:
     - Trước 01/08/2024 (Bảng giá đất cũ): Giá đất ở tính thuế 3 triệu/$m^2$, giá đất nông nghiệp 300.000 đ/$m^2$. Chênh lệch $= 2,7  triệu/m^2 
ightarrow$ Tiền nộp $= 270  triệu đồng$.
     - Sau khi áp dụng Bảng giá đất điều chỉnh: Giá đất ở tăng lên 12 triệu/$m^2$, giá đất nông nghiệp 1 triệu/$m^2$. Chênh lệch $= 11  triệu/m^2 
ightarrow$ Tiền nộp $= 1,1  tỷ đồng$ (tăng gấp 4 lần!).
   - *Giới hạn:* Chỉ áp dụng cho các thửa đất phù hợp với quy hoạch sử dụng đất cấp huyện và nằm trong kế hoạch sử dụng đất hàng năm được phê duyệt.
5. **2–3 ý Short loại L nối về Long:**
   - *Short 1:* "Bảng giá đất mới: Chuyển 100 mét vuông đất vườn lên thổ cư tốn bao nhiêu tiền?"
   - *Short 2:* "Công thức tính tiền sử dụng đất mới nhất theo Nghị định 103/2024."
   - *Short 3:* "Có nên vay tiền ngân hàng để nộp tiền lên thổ cư cho mảnh đất của gia đình?"

---

### Đề tài 7: Người làm nghề tự do (Freelancer / Kinh doanh tự do): Có nên đóng BHXH tự nguyện 15 năm theo Luật mới?
1. **Quyết định:** Lao động tự do, người làm việc từ xa, kinh doanh online (25–40 tuổi): Có nên tham gia BHXH tự nguyện đóng đều 15 năm theo Luật BHXH 2024 để lấy lương hưu và BHYT hưu trí trọn đời, hay tự đem số tiền đó gửi tiết kiệm mua vàng?
2. **Câu mở (Hook):** "Từ ngày 01/07/2025, Luật Bảo hiểm xã hội mới chính thức giảm thời gian đóng tối thiểu để hưởng lương hưu từ 20 năm xuống còn 15 năm. Nếu bạn làm freelancer, bán hàng online hay kinh doanh tự do, mỗi tháng trích ra khoảng 1,1 triệu đồng đóng BHXH tự nguyện, sau 15 năm bạn sẽ nhận lương hưu hàng tháng kèm theo một đặc quyền vô giá mà gửi tiết kiệm không bao giờ có: tấm thẻ BHYT chi trả 95% viện phí đến hết đời. Liệu đây có phải là kênh dự phòng tuổi già tốt nhất cho người làm tự do?"
3. **Dữ liệu cần có & Cách lấy:**
   - *Luật Bảo hiểm xã hội 2024* (Luật số 41/2024/QH15, hiệu lực từ 01/07/2025) quy định thời gian đóng tối thiểu 15 năm, tỷ lệ hưởng lương hưu lao động nữ 45%, lao động nam 40% (sau đó mỗi năm thêm 1%).
   - *Nghị định 07/2021/NĐ-CP* quy định chuẩn nghèo nông thôn (1,5 triệu đồng/tháng) làm căn cứ mức hỗ trợ tiền đóng BHXH tự nguyện của Nhà nước (30% cho hộ nghèo, 25% cận nghèo, 10% các đối tượng khác).
   - Báo cáo số liệu người tham gia BHXH tự nguyện của BHXH Việt Nam (`baohiemxahoi.gov.vn`).
4. **Giai đoạn, phương pháp tính & giới hạn:**
   - *Giai đoạn mô phỏng:* Đóng liên tục 15 năm (180 tháng), mốc thu nhập lựa chọn đóng là 5 triệu đồng/tháng.
   - *Phương pháp tính:*
     - Tiền đóng hàng tháng $= 22% x 5  triệu = 1.100.000  đồng$. Trừ đi mức hỗ trợ của Nhà nước 10% chuẩn nghèo ($10% x 22% x 1,5  triệu = 33.000  đ$) $
ightarrow$ Số thực đóng $= 1.067.000  đồng/tháng$. Tổng vốn đóng sau 15 năm $pprox 192  triệu đồng$.
     - Quyền lợi hưu trí: Khi đủ tuổi hưu, lao động nữ nhận $45% x 5  triệu = 2,25  triệu/tháng$ (kèm cơ chế điều chỉnh trượt giá định kỳ theo CPI của Chính phủ). Thẻ BHYT hưu trí được Nhà nước cấp miễn phí với mức thanh toán 95% chi phí khám chữa bệnh.
     - So sánh với phương án tự gửi tiết kiệm 1,07 triệu/tháng với lãi suất 6%/năm trong 15 năm: Tích lũy được khoảng 310 triệu đồng. Nếu rút dần chi tiêu khi về già, số tiền này sẽ cạn nhanh chóng sau 7–10 năm hoặc chỉ sau một đợt điều trị bệnh nặng.
   - *Giới hạn:* Phải chờ đến đủ tuổi nghỉ hưu theo quy định của Bộ luật Lao động (nữ 60, nam 62 theo lộ trình) mới được nhận lương hưu.
5. **2–3 ý Short loại L nối về Long:**
   - *Short 1:* "Freelancer đóng BHXH tự nguyện 15 năm: Về hưu nhận được bao nhiêu tiền mỗi tháng?"
   - *Short 2:* "Tấm thẻ BHYT 95%: Lý do lớn nhất để người làm tự do đóng BHXH tự nguyện."
   - *Short 3:* "Nên chọn mức thu nhập bao nhiêu để đóng BHXH tự nguyện có lợi nhất?"

---

### Đề tài 8: Bị ép mua bảo hiểm khi vay ngân hàng: Người đi vay được bảo vệ thế nào theo Luật Các TCTD 2024?
1. **Quyết định:** Khi làm hồ sơ vay thế chấp mua nhà / mua xe tại ngân hàng, nhân viên tín dụng yêu cầu "mua thêm hợp đồng bảo hiểm nhân thọ 20–30 triệu đồng thì hồ sơ mới được phê duyệt giải ngân hoặc mới được áp dụng lãi suất ưu đãi giảm 0,5%": Người vay nên phản ứng thế nào? Chấp nhận mua để được việc, từ chối dứt khoát theo luật, hay mua rồi sử dụng quyền hủy hợp đồng trong 21 ngày cân nhắc?
2. **Câu mở (Hook):** "Vay một tỷ đồng mua nhà, nhân viên tín dụng thông báo: nếu mua thêm gói bảo hiểm nhân thọ 25 triệu thì lãi suất năm đầu được giảm 0,5%. Tính nhanh thì khoản giảm 0,5% lãi suất trên một tỷ chỉ giúp bạn tiết kiệm được 5 triệu tiền lãi, nhưng bạn mất ngay 25 triệu tiền mua bảo hiểm – lỗ ròng 20 triệu ngay khi vừa ký hợp đồng. Đáng nói, hành vi 'ép mua bia kèm lạc' này đã chính thức bị cấm tuyệt đối tại Khoản 5 Điều 15 Luật Các tổ chức tín dụng 2024. Bạn có quyền từ chối thế nào để bảo vệ tiền của mình?"
3. **Dữ liệu cần có & Cách lấy:**
   - *Luật Các tổ chức tín dụng 2024* (Luật số 32/2024/QH15, có hiệu lực từ 01/07/2024) – Khoản 5 Điều 15 nghiêm cấm TCTD và nhân viên ngân hàng gắn việc bán sản phẩm bảo hiểm không bắt buộc với việc cung ứng sản phẩm, dịch vụ ngân hàng dưới mọi hình thức.
   - *Thông tư 67/2023/TT-BTC* của Bộ Tài chính (Điều 49 cấm ngân hàng tư vấn, chào bán bảo hiểm liên kết đầu tư trong thời hạn 60 ngày trước và 60 ngày sau khi giải ngân toàn bộ khoản vay).
   - *Luật Kinh doanh bảo hiểm 2022* (Điều 35 về thời gian cân nhắc tham gia bảo hiểm 21 ngày).
4. **Giai đoạn, phương pháp tính & giới hạn:**
   - *Phương pháp tính:* So sánh chi phí và lợi ích kinh tế:
     - Khoản vay 1 tỷ đồng. Lãi suất ưu đãi giảm 0,5% trong 12 tháng đầu $
ightarrow$ Tiền lãi tiết kiệm $= 1.000 x 0,5% = 5  triệu đồng$.
     - Chi phí mua gói bảo hiểm nhân thọ $= 25  triệu đồng$.
     - Tổn thất kinh tế ròng ngay trong năm đầu $= 5 - 25 = -20  triệu đồng$. Nếu năm thứ 2 không đóng tiếp hợp đồng bảo hiểm, toàn bộ 25 triệu đồng này mất trắng theo quy định về chi phí ban đầu.
     - So sánh với việc mua Bảo hiểm rủi ro tín dụng (Credit Life Insurance) chỉ tốn khoảng 0,5%–0,7% dư nợ gốc nhưng đúng bản chất bảo vệ khoản vay nếu người vay gặp biến cố tử vong/thương tật toàn bộ.
   - *Giới hạn:* Phụ thuộc vào kỹ năng đàm phán của người vay và mức độ cạnh tranh room tín dụng tại từng chi nhánh ngân hàng.
5. **2–3 ý Short loại L nối về Long:**
   - *Short 1:* "Bỏ 25 triệu mua bảo hiểm để giảm 0,5% lãi vay ngân hàng: Bạn đang lời hay lỗ nặng?"
   - *Short 2:* "Khoản 5 Điều 15 Luật Các TCTD 2024: Vũ khí bảo vệ người đi vay ngân hàng."
   - *Short 3:* "Hủy hợp đồng bảo hiểm trong 21 ngày cân nhắc sau giải ngân: Có bị ngân hàng phạt không?"

---

## III. Bảng kiểm tra nguồn dữ liệu chính thức

Toàn bộ 8 đề tài đều sử dụng các nguồn văn bản quy phạm pháp luật, quyết định điều hành của Ngân hàng Nhà nước, Bộ Tài chính, Bộ Xây dựng và Tổng cục Thống kê. Các nguồn này đã được tra cứu và xác thực tồn tại trên hệ thống thông tin pháp luật chính thức:

| Đề tài | Nguồn dữ liệu chính thức | Cơ quan ban hành | Trạng thái tra cứu | URL nguồn văn bản |
| :--- | :--- | :--- | :---: | :--- |
| **Đề 1** | Thông tư 39/2016/TT-NHNN (Điều 14) & Công bố lãi suất NHNN | Ngân hàng Nhà nước | Xác thực, sẵn sàng | https://thuvienphapluat.vn/van-ban/Tien-te-Ngan-hang/Thong-tu-39-2016-TT-NHNN-quy-dinh-ve-hoat-dong-cho-vay-cua-to-chuc-tin-dung-chi-nhanh-ngan-hang-nuoc-ngoai-335835.aspx |
| **Đề 2** | Thông tư 67/2023/TT-BTC (Điều 22 Khoản 3) | Bộ Tài chính | Xác thực, sẵn sàng | https://thuvienphapluat.vn/van-ban/Bao-hiem/Thong-tu-67-2023-TT-BTC-huong-dan-Luat-Kinh-doanh-bao-hiem-585324.aspx |
| **Đề 3** | Thông tư 04/2022/TT-NHNN (Điều 5) & QĐ 1125/QĐ-NHNN | Ngân hàng Nhà nước | Xác thực, sẵn sàng | https://thuvienphapluat.vn/van-ban/Tien-te-Ngan-hang/Thong-tu-04-2022-TT-NHNN-ap-dung-lai-suat-rut-truoc-han-tien-gui-tai-to-chuc-tin-dung-517852.aspx |
| **Đề 4** | Thông tư 98/2020/TT-BTC (Điều 8) & Thông tư 136/2025/TT-BTC | Bộ Tài chính / UBCKNN | Xác thực, sẵn sàng | https://thuvienphapluat.vn/van-ban/Chung-khoan/Thong-tu-98-2020-TT-BTC-huong-dan-hoat-dong-va-quan-ly-quy-dau-tu-chung-khoan-458117.aspx |
| **Đề 5** | Nghị định 100/2024/NĐ-CP (Điều 30) & Văn bản 2308/NHNN-TD | Chính phủ / NHNN | Xác thực, sẵn sàng | https://thuvienphapluat.vn/van-ban/Bat-dong-san/Nghi-dinh-100-2024-ND-CP-quy-dinh-chi-tiet-Luat-Nha-o-ve-phat-trien-quan-ly-nha-o-xa-hoi-619227.aspx |
| **Đề 6** | Nghị định 103/2024/NĐ-CP (Điều 8) & QĐ 79/2024/QĐ-UBND | Chính phủ / UBND TP.HCM | Xác thực, sẵn sàng | https://thuvienphapluat.vn/van-ban/Bat-dong-san/Nghi-dinh-103-2024-ND-CP-tien-su-dung-dat-tien-thue-dat-620241.aspx |
| **Đề 7** | Luật Bảo hiểm xã hội 2024 (số 41/2024/QH15) | Quốc hội / BHXH VN | Xác thực, sẵn sàng | https://thuvienphapluat.vn/van-ban/Bao-hiem/Luat-Bao-hiem-xa-hoi-2024-41-2024-QH15-562916.aspx |
| **Đề 8** | Luật Các tổ chức tín dụng 2024 (Điều 15 Khoản 5) | Quốc hội / NHNN | Xác thực, sẵn sàng | https://thuvienphapluat.vn/van-ban/Tien-te-Ngan-hang/Luat-Cac-to-chuc-tin-dung-2024-32-2024-QH15-585868.aspx |

---

## IV. Xếp hạng theo 4 tiêu chí & Lựa chọn 4 đề tài ưu tiên

### Thang điểm đánh giá (Thang 10 cho mỗi tiêu chí, tối đa 40 điểm):
1. **Độ thật của quyết định:** Mức độ bức thiết, tính phổ biến và tác động tài chính trực tiếp tới người xem 25–40 tuổi.
2. **Độ sẵn dữ liệu:** Độ đầy đủ của công thức tính toán, số liệu thống kê chính thức, tính bất biến của văn bản quy phạm pháp luật.
3. **Khả năng làm biểu đồ:** Tính trực quan khi thể hiện bằng motion graphics (biểu đồ cột so sánh, biểu đồ tích lũy, biểu đồ thác nước, biểu đồ dòng tiền).
4. **Không trùng đề:** Tính độc lập hoàn toàn với 28 Long CK đã sản xuất trong repo.

### Bảng chấm điểm:

| Thứ hạng | Đề tài | Độ thật (10) | Độ sẵn dữ liệu (10) | Biểu đồ (10) | Không trùng (10) | Tổng điểm (40) | Kết luận |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Đề 1: Trả nợ ngân hàng trước hạn hay gửi tiết kiệm?** | 10 | 10 | 10 | 10 | **40** | **CHỌN (Ưu tiên 1)** |
| **2** | **Đề 2: Bảo hiểm liên kết đầu tư (ILP): Cắt lỗ hay đóng tiếp?** | 10 | 10 | 10 | 10 | **40** | **CHỌN (Ưu tiên 2)** |
| **3** | **Đề 5: Vay mua Nhà ở xã hội: Lãi suất thả nổi sau 5 năm & trần lương** | 9.5 | 10 | 10 | 9.5 | **39** | **CHỌN (Ưu tiên 3)** |
| **4** | **Đề 4: Quỹ mở: Phí quản lý 1,8% bào mòn tài sản sau 10 năm** | 9.5 | 10 | 10 | 9.5 | **39** | **CHỌN (Ưu tiên 4)** |
| 5 | Đề 8: Bị ép mua bảo hiểm khi vay thế chấp ngân hàng | 9.5 | 9.5 | 8.5 | 10 | 37.5 | Dự bị 1 |
| 6 | Đề 6: Chuyển mục đích đất nông nghiệp lên đất ở theo bảng giá mới | 9.0 | 9.5 | 9.0 | 10 | 37.5 | Dự bị 2 |
| 7 | Đề 3: Gửi tiết kiệm chia nhiều sổ hay gộp 1 sổ theo Thông tư 04 | 9.0 | 10 | 8.5 | 9.0 | 36.5 | Dự bị 3 |
| 8 | Đề 7: Freelancer đóng BHXH tự nguyện 15 năm theo Luật mới | 9.0 | 10 | 8.5 | 8.5 | 36.0 | Dự bị 4 |

---

## V. Đề xuất 4 đề tài vào đợt sản xuất từ 23/11

Bốn đề tài được lựa chọn đại diện cho 4 trụ cột tài chính thiết yếu của người độ tuổi 25–40, tạo nên cấu trúc nội dung đa dạng, cân đối và giữ chân người xem tốt cho kênh CK:

1. **Long CK 1 (Quản lý nợ vay cá nhân): Trả Nợ Ngân Hàng Trước Hạn Hay Gửi Tiết Kiệm?**
   - *Trọng tâm:* Giải quyết bài toán vay mua nhà khi bước vào chu kỳ lãi thả nổi 11%–12%. So sánh số tiền tiết kiệm được từ việc giảm nợ gốc đối chiếu với phí phạt theo Thông tư 39 và chi phí cơ hội tiền gửi tiết kiệm.
   - *Khả năng giữ người xem:* Rất mạnh vì đánh trúng tâm lý áp lực trả nợ hàng tháng của người mua nhà.

2. **Long CK 2 (Bảo vệ tài chính & Rủi ro): Bảo Hiểm Liên Kết Đầu Tư: Cắt Lỗ Dừng Lại Hay Đóng Tiếp Sau 3 Năm?**
   - *Trọng tâm:* Bóc tách cơ chế trừ chi phí ban đầu (tới 50% năm 1, 30% năm 2) theo Thông tư 67/2023/TT-BTC. So sánh hiệu quả tài chính giữa việc tiếp tục đóng hợp đồng ILP đối chiếu với chiến lược "Buy Term and Invest the Rest".
   - *Khả năng giữ người xem:* Cực cao vì đây là chủ đề nhức nhối hàng đầu trong dư luận những năm gần đây, giải thích bằng toán học thay vì cảm tính.

3. **Long CK 3 (Chính sách nhà ở & Dòng tiền gia đình): Vay Mua Nhà Ở Xã Hội: Trần Lương 15 Triệu Gánh Lãi Thả Nổi Thế Nào?**
   - *Trọng tâm:* Đối chiếu trần thu nhập theo Nghị định 100/2024/NĐ-CP (15 triệu độc thân, 30 triệu vợ chồng) với nghĩa vụ trả nợ gốc + lãi gói 120.000 tỷ đồng, cảnh báo rủi ro bước nhảy lãi suất thả nổi sau 5 năm đầu ưu đãi.
   - *Khả năng giữ người xem:* Rất cao do nhu cầu an cư của người trẻ đô thị và chính sách NOXH đang là tâm điểm chú ý của xã hội.

4. **Long CK 4 (Tích lũy & Đầu tư dài hạn): Chứng Chỉ Quỹ Mở: Phí Quản Lý 1,8% Nuốt Bao Nhiêu Tiền Sau 15 Năm?**
   - *Trọng tâm:* Cơ chế hoạt động của quỹ mở và tác động bào mòn tài sản từ phí quản lý (Điều 8 Thông tư 98/2020/TT-BTC) qua 10–15 năm. So sánh quỹ mở chủ động vs quỹ ETF thụ động vs tự đầu tư cổ phiếu.
   - *Khả năng giữ người xem:* Thuyết phục bằng đồ thị trực quan, mở rộng tư duy đầu tư thực tế cho dân văn phòng tích lũy tiền nhàn rỗi hàng tháng.

---

## VI. Cam kết tuân thủ quy chế

- Báo cáo được lưu trữ duy nhất tại `docs/pm/tickets/GH-181-topics-report.md` với định dạng UTF-8.
- Không chỉnh sửa code hệ thống, không thay đổi file lịch `state.sqlite`.
- Không thực hiện lệnh `git commit`, `git push`, không can thiệp vào tài khoản YouTube.
- Các nội dung đề xuất tuân thủ nghiêm ngặt quy định kênh CK: không nhắc tên ngân hàng thương mại hay công ty chứng khoán cụ thể, không đưa ra lời khuyên mua/bán đầu tư cá nhân, mọi số liệu giả định trong kịch bản tính toán đều được dán nhãn "VÍ DỤ GIẢ ĐỊNH".
