# GH-33-CK · Báo cáo Packaging và Factcheck cho Pilot Tin Nóng Tuần 45 (Kênh CK)

- **Issue:** https://github.com/nguyent0810/Youtube_Creator_V2/issues/33
- **Brief gốc:** `docs/pm/tickets/GH-33-grok-CK.md`
- **Kênh:** CK (Biểu Đồ Biết Nói) · **Giọng đọc cố định:** Ngọc Huyền
- **File dữ kiện đi kèm (cho Codex viết spec):** `docs/pm/tickets/GH-33-CK-facts.json`
- **File kế hoạch Long đề xuất:** `data/long/ck-xang-dien-thue-11-2026/plan.md`
- **Tuyên bố bắt buộc trong mọi mô tả CK:** *"Nội dung giáo dục, không phải tư vấn đầu tư."*

---

## 0. Cơ sở chọn đề tài: Phân tách Số đo và Suy đoán

### Số đo (đo được từ kho dữ liệu & báo cáo tuần 44)
1. **Đối chiếu kho hiện có (`data/stier/specs/ck-*.json` — 84 spec; `data/long/ck-*` — 27 chủ đề):**
   - Toàn bộ 6 sự kiện được chọn đều xảy ra trong khung **31/10–02/11/2026**, hoàn toàn **chưa trùng** với bất kỳ spec Short hay Long nào trong kho.
   - Hai sự kiện (`ck_03` vàng SJC và `ck_08` lãi suất/tiền gửi tiết kiệm) nối trực tiếp được sang hai Long **có thật** đã có trong kho (`ck-d1-vang-dinh` và `ck-2026-kenh-dau-tu`) nên được đóng gói theo chuẩn **Loại L**. Bốn sự kiện còn lại đóng gói theo chuẩn **Loại S** (trong đó 3 bài `ck_02`, `ck_01`, `ck_06` đồng thời là cụm vệ tinh cho đề xuất Long mới `ck-xang-dien-thue-11-2026`).
2. **Số đo thắng/thua tuần 44 (`docs/pm/2026-11-02-thang-thua-tuan-44.md`):**
   - Trên kênh CK, các Short có **chữ số ngay câu đầu** đạt trung vị **701,5 view** (n = 6), gấp **3,32 lần** nhóm không có số ở câu đầu (**211 view**, n = 8).
   - Cụm bài đặt **hai con số tiền đối nghịch trên cùng một vật** đạt hiệu suất vượt trội (`ck-hai-nam-dau-lai-vay-va-tien-thue` đạt **929 view**, gấp **5,08 lần** trung vị nhóm tuổi), trong khi cụm giải thích cơ chế thị trường chứng khoán chung (`ck-c2-*`) thua rõ rệt với trung vị chỉ **36 view**.
   - Vì vậy, báo cáo này **loại bỏ hoàn toàn** các sự kiện điểm số chứng khoán chung (`ck_04` VN-Index giảm 30 điểm) hoặc biến động nhân sự/lợi nhuận ngân hàng thương mại (`ck_09`, `ck_10` — đồng thời để tuân thủ luật cấm nêu tên ngân hàng thương mại và mã cổ phiếu).

### Suy đoán (giả thuyết biên tập cho tuần 45 — cần đo lại ở mốc 24h / 72h / 7d)
1. Người xem dừng lướt ở giây đầu tiên nhờ **mâu thuẫn định lượng sát túi tiền** trên `Khung hình 0` và `Câu mở ≤ 9 từ` (ví dụ: thuế xăng `0%` đối lập với giá cước chưa giảm; `20 năm` giá điện tăng đối lập với mức giảm `44 đồng/kWh`; `20 phút` mất `6,3 tỷ USD` đối lập với `3,64 tỷ USD` rút tháo chạy).
2. Việc kết hợp tin nóng vĩ mô vừa có hiệu lực ngày `01/11/2026` với phép tính `VÍ DỤ GIẢ ĐỊNH` trên hóa đơn hộ gia đình được kỳ vọng giúp vượt qua bài phát thử đầu tiên (seed pool) nhanh hơn các bài khái niệm tĩnh.

---

## 1. Bảng tổng hợp 6 Short CK (Sự kiện · Title ×3 · Hook 3s · Khung 0 · Loại · Hạn lên sóng)

*Mọi tiêu đề đều ≤ 60 ký tự, tiếng Việt có dấu, không phóng đại, không câu hỏi gây hiểu sai. Mọi câu đầu đều đúng 9 từ (≤ 9 từ), có tên người thật hoặc cặp số. Mọi chữ khung đầu đều 4–5 từ/cụm (≤ 6 từ theo brief và ≤ 5 từ theo quy tắc 8 điều), có số.*

| # | Mã sự kiện & Slug đề xuất | Sự kiện (31/10–02/11/2026) | 3 Phương án Title (≤ 60 ký tự) | Hook 3s — Câu đầu (≤ 9 từ) | Chữ khung đầu (≤ 6 từ, có số) | Loại | Hạn lên sóng đề xuất |
|---|---|---|---|---|---|---|---|
| **1** | `ck_02`<br>`ck-thue-xang-0-giam-1804` | Nghị quyết `45/2026/NQ-CP` đưa thuế TTĐB xăng về `0%` từ `01/11/2026` đến `31/03/2027`; xăng E5 RON 92 giảm `1.804đ/lít` (còn `24.223đ/lít`), E10 RON 95-III giảm `1.575đ/lít`, nhưng cước vận tải chưa giảm ngay. | 1. `Xăng giảm 1.804 đồng/lít từ 1/11: 5 tháng thuế 0%` *(49 kt)*<br>2. `Thuế xăng 0% suốt 5 tháng: Giảm 1.804 đồng mỗi lít` *(50 kt)*<br>3. `Từ 1/11 xăng giảm 1.804 đồng/lít, sao cước chưa hạ` *(50 kt)* | `"Thuế không phần trăm, xăng giảm một nghìn tám."` *(9 từ — cặp số `0%` & `1.800`)* | `THUẾ 0% ↔ GIẢM 1.804Đ/LÍT` *(4 cụm)* | **S** *(vệ tinh Long mới `ck-xang-dien-thue-11-2026`)* | **Trong 72h**<br>(03/11–05/11) |
| **2** | `ck_01`<br>`ck-dien-giam-44-dong-20-nam` | Quyết định `1305/QĐ-EVN` & `2892/QĐ-BCT` giảm `2%` giá bán lẻ điện bình quân (giảm `44,16đ/kWh`, từ `2.204,07` xuống `2.159,90đ/kWh`) từ `01/11/2026` — lần giảm đầu tiên sau gần `20 năm`. | 1. `Sau 20 năm, giá điện giảm 44 đồng/kWh từ ngày 1/11` *(50 kt)*<br>2. `Giá điện giảm 2% về 2.159 đồng/kWh lần đầu sau 20 năm` *(53 kt)*<br>3. `20 năm mới giảm 44 đồng/kWh: Hóa đơn điện bớt bao nhiêu` *(55 kt)* | `"Sau hai mươi năm, điện giảm hai phần trăm."` *(9 từ — cặp số `20 năm` & `2%`)* | `20 NĂM ↔ GIẢM 44Đ/KWH` *(4 cụm)* | **S** *(vệ tinh Long mới `ck-xang-dien-thue-11-2026`)* | **72h – 5 ngày**<br>(03/11–06/11) |
| **3** | `ck_06`<br>`ck-ho-kinh-doanh-giam-30-thue` | Nghị định `398/2026/NĐ-CP` (hướng dẫn Nghị quyết `43/2026/QH16`): cá nhân, hộ kinh doanh, doanh nghiệp có doanh thu `≤ 10 tỷ đồng/năm` được giảm `30%` thuế TNCN/TNDN năm `2026–2027` theo từng kỳ. | 1. `Doanh thu dưới 10 tỷ: Giảm 30% thuế thu nhập 2026–2027` *(54 kt)*<br>2. `Hộ kinh doanh dưới 10 tỷ/năm được giảm 30% tiền thuế` *(52 kt)*<br>3. `Giảm 30% thuế cho hộ doanh thu 10 tỷ: Bẫy vượt ngưỡng` *(53 kt)* | `"Dưới mười tỷ, thuế giảm ba mươi phần trăm."` *(9 từ — cặp số `10 tỷ` & `30%`)* | `DOANH THU ≤10 TỶ · -30% THUẾ` *(5 cụm)* | **S** *(vệ tinh Long mới `ck-xang-dien-thue-11-2026`)* | **5 – 7 ngày**<br>(03/11–08/11) |
| **4** | `ck_03`<br>`ck-vang-sjc-140-trieu-chenh-14-trieu` | Vàng SJC lao dốc cuối tháng 10 làm người mua lỗ `> 11 triệu đồng/lượng` sau `2 tuần`; sáng `02/11` đảo chiều lên `137–140 triệu đồng/lượng`, cao hơn thế giới quy đổi (`123,8 triệu`) từ `14,3` đến `> 16 triệu đồng/lượng`. | 1. `Vàng SJC 140 triệu ngày 2/11: Cao hơn thế giới 14,3 triệu` *(57 kt)*<br>2. `Lỗ 11 triệu sau 2 tuần, vàng SJC vẫn vênh 14,3 triệu` *(52 kt)*<br>3. `Mua 140 triệu, tiệm thu 137 triệu: Hai lớp chênh giá vàng` *(57 kt)* | `"Hai tuần lỗ mười một triệu mỗi lượng vàng."` *(9 từ — cặp số `2 tuần` & `11 triệu`)* | `SJC 140TR ↔ THẾ GIỚI 123,8TR` *(4 cụm)* | **L** *(dẫn sang Long có thật `ck-d1-vang-dinh`)* | **Trong 72h**<br>(03/11–05/11) |
| **5** | `ck_08`<br>`ck-lai-giam-05-tien-gui-80-ngan-han` | Đầu tháng `11/2026`, lãi tiết kiệm giảm tới `0,5 điểm %` nhưng tiền gửi vẫn chảy mạnh vào ngân hàng; Thống đốc NHNN **Phạm Đức Ấn** giải trình Quốc hội (`31/10`) rằng `80%` là tiền gửi ngắn hạn quay vòng. | 1. `Lãi giảm 0,5%, sao 80% tiền gửi vẫn nằm ở kỳ hạn ngắn` *(53 kt)*<br>2. `Thống đốc Phạm Đức Ấn: Vì sao lãi hạ mà tiền gửi vẫn tăng` *(57 kt)*<br>3. `Lãi tiết kiệm giảm 0,5% đầu tháng 11, tiền vẫn đổ vào sổ` *(56 kt)* | `"Ông Phạm Đức Ấn lý giải dòng tiền gửi."` *(9 từ — tên người thật `Phạm Đức Ấn`)* | `LÃI -0,5% ↔ 80% GỬI NGẮN` *(5 cụm)* | **L** *(dẫn sang Long có thật `ck-2026-kenh-dau-tu`)* | **5 – 7 ngày**<br>(04/11–08/11) |
| **6** | `ck_19`<br>*(Giao thoa `mim_01`, giữ góc CK)*<br>`ck-binance-63-ty-rut-36-ty` | Sàn Binance bị nhóm hacker TraderTraitor đánh cắp `6,3 tỷ USD` trong `20 phút` (thử nghiệm trước `36 tiếng`); mở lại cổng ngày `01/11`, nhà đầu tư rút ròng `3,64 tỷ USD` (`2,1%` tài sản) trong `9,5 giờ`, ETF Bitcoin mất `643 triệu USD`. | 1. `Mất 6,3 tỷ đô trong 20 phút: 3,6 tỷ đô rút khỏi Binance` *(55 kt)*<br>2. `Sau vụ hack 6,3 tỷ đô, 3,64 tỷ đô rời sàn trong 9 giờ` *(53 kt)*<br>3. `Sàn mất 6,3 tỷ đô, quỹ ETF Bitcoin bị rút 643 triệu đô` *(54 kt)* | `"Hai mươi phút mất sáu phẩy ba tỷ đô."` *(9 từ — cặp số `20 phút` & `6,3 tỷ đô`)* | `MẤT 6,3 TỶ ↔ RÚT 3,64 TỶ` *(5 cụm)* | **S** *(đứng riêng, góc rủi ro lưu ký)* | **Trong 72h**<br>(03/11–05/11) |

---

## 2. Chi tiết Dàn ý 6–9 câu đọc và Gợi ý hình cho từng Short

*(Tuân thủ nghiêm ngặt: mỗi bài đúng 8 câu đọc = 1 insight, kết bằng cú chốt, không CTA, không câu hỏi trong lời đọc, không nêu tên ngân hàng thương mại / công ty chứng khoán / hãng xe / mã cổ phiếu, gắn rõ `VÍ DỤ GIẢ ĐỊNH` cho mọi phép tính giả định, kèm tuyên bố `"Nội dung giáo dục, không phải tư vấn đầu tư."`)*

### Short 1 · `ck-thue-xang-0-giam-1804` (Sự kiện `ck_02` — Loại S)
- **Dàn ý 8 câu đọc:**
  1. Thuế không phần trăm, xăng giảm một nghìn tám. *(9 từ)*
  2. Từ ngày một tháng mười một năm hai nghìn không trăm hai mươi sáu, thuế tiêu thụ đặc biệt với mọi loại xăng đưa về mức không phần trăm suốt năm tháng.
  3. Nhờ quyết định này của Chính phủ, xăng E5 RON 92 giảm ngay một nghìn tám trăm linh bốn đồng mỗi lít, về mức hai mươi tư nghìn hai trăm hai mươi ba đồng.
  4. Xăng E10 RON 95 cũng giảm một nghìn năm trăm bảy mươi lăm đồng mỗi lít, xuống còn hai mươi tư nghìn một trăm năm mươi chín đồng.
  5. Trong **ví dụ giả định** bạn đổ năm mươi lít xăng mỗi tháng, ví tiền của bạn giữ lại được khoảng chín mươi nghìn đồng mỗi tháng cho tới hết tháng ba năm sau.
  6. Thế nhưng ngoài chợ, giá cước vận tải và hàng hóa tiêu dùng vẫn chưa hạ ngay theo giá xăng.
  7. Lý do là doanh nghiệp vận tải ký hợp đồng cước theo quý và còn gánh chi phí bến bãi, nhân công, nên cần lộ trình điều chỉnh thay vì giảm tức thì sau một đêm.
  8. Tiền đổ xăng trong ví bạn giảm ngay tại cây xăng hôm nay, còn hóa đơn đi chợ sẽ luôn đi chậm hơn giá nhiên liệu một nhịp hợp đồng.
- **Gợi ý hình (không dùng ảnh/clip báo chí có bản quyền):**
  - *Khung 0:* Biểu đồ cột đôi động đối chiếu `THUẾ 0%` và `GIẢM 1.804Đ/LÍT` trên nền tối.
  - *Cảnh giữa:* Biểu đồ thác (`waterfall`) bóc tách giá xăng E5 RON 92 xuống `24.223đ/lít` và E10 RON 95-III xuống `24.159đ/lít` (hiện mã văn bản `Nghị quyết 45/2026/NQ-CP` trên màn hình); thẻ bảng tính ghi rõ nhãn `VÍ DỤ GIẢ ĐỊNH: 50 LÍT × 1.804Đ ≈ 90.000Đ/THÁNG`.
  - *Cảnh kết:* Biểu đồ cột chồng (`stack`) cơ cấu chi phí vận tải đặt cạnh clip Pexels tự do cảnh xe tải chở hàng trên quốc lộ (không lộ logo hãng xe).
- **Pháp lý CK:** *"Nội dung giáo dục, không phải tư vấn đầu tư."*

### Short 2 · `ck-dien-giam-44-dong-20-nam` (Sự kiện `ck_01` — Loại S)
- **Dàn ý 8 câu đọc:**
  1. Sau hai mươi năm, điện giảm hai phần trăm. *(9 từ)*
  2. Từ ngày một tháng mười một năm hai nghìn không trăm hai mươi sáu, giá bán lẻ điện bình quân hạ từ hai nghìn hai trăm linh bốn đồng xuống gần hai nghìn một trăm sáu mươi đồng mỗi số điện.
  3. Mức giảm hơn bốn mươi bốn đồng mỗi số này là lần đầu tiên giá điện bán lẻ đi xuống sau gần hai thập kỷ liên tục tăng.
  4. Trong **ví dụ giả định** gia đình bạn đang trả hóa đơn điện một triệu đồng mỗi tháng, mức giảm hai phần trăm giúp bạn bớt được đúng hai mươi nghìn đồng.
  5. Hai mươi nghìn đồng mỗi tháng nhìn riêng ở từng hộ gia đình thì chỉ tương đương một ly cà phê bình dân.
  6. Nhưng với các nhà máy sản xuất thép, xi măng hay dệt may tiêu thụ hàng triệu số điện, hai phần trăm tiết kiệm được là hàng trăm triệu đồng chi phí đầu vào mỗi tháng.
  7. Khi giá điện hạ cùng lúc với thuế xăng về không phần trăm, áp lực tăng giá hàng hóa dịp cuối năm được chặn ngay từ khâu sản xuất.
  8. Khoản tiền bạn giữ lại lớn nhất từ đợt giảm giá điện này không nằm trên tờ hóa đơn điện, mà nằm ở mặt bằng giá cả ngoài siêu thị cuối năm.
- **Gợi ý hình (không dùng ảnh/clip báo chí có bản quyền):**
  - *Khung 0:* Đường biểu đồ đi lên suốt 20 năm rồi gập xuống ở mốc `01/11/2026`, chữ lớn `20 NĂM ↔ GIẢM 44Đ/KWH`.
  - *Cảnh giữa:* Cảnh `counter` và `bars` đối chiếu mức giá cũ `2.204,0655 đồng/kWh` và mức mới `2.159,9037 đồng/kWh` (hiện mã `Quyết định 1305/QĐ-EVN` và `2892/QĐ-BCT`); thẻ tính `VÍ DỤ GIẢ ĐỊNH: HÓA ĐƠN 1.000.000Đ → GIẢM 20.000Đ`.
  - *Cảnh kết:* Sơ đồ truyền dẫn chi phí điện nhà máy sang rổ hàng tiêu dùng cuối năm, kèm clip Pexels tự do cảnh dây chuyền nhà máy sản xuất.
- **Pháp lý CK:** *"Nội dung giáo dục, không phải tư vấn đầu tư."*

### Short 3 · `ck-ho-kinh-doanh-giam-30-thue` (Sự kiện `ck_06` — Loại S)
- **Dàn ý 8 câu đọc:**
  1. Dưới mười tỷ, thuế giảm ba mươi phần trăm. *(9 từ)*
  2. Theo Nghị định vừa ban hành cuối tháng mười, cá nhân kinh doanh, hộ kinh doanh và doanh nghiệp có doanh thu một năm không quá mười tỷ đồng được giảm ba mươi phần trăm thuế thu nhập.
  3. Chính sách này áp dụng trọn vẹn cho cả hai kỳ tính thuế năm hai nghìn không trăm hai mươi sáu và hai nghìn không trăm hai mươi bảy.
  4. Điểm đáng giá nhất là bạn được tự trừ ngay ba mươi phần trăm số thuế phải nộp trong từng kỳ kê khai hằng quý thay vì phải chờ tới cuối năm.
  5. Trong **ví dụ giả định** cửa hàng của bạn có doanh thu tám tỷ đồng một năm và phát sinh bốn mươi triệu đồng thuế thu nhập cá nhân, bạn giữ lại được ngay mười hai triệu đồng.
  6. Nhưng văn bản này có một ngưỡng cắt cứng ở đúng mốc doanh thu mười tỷ đồng.
  7. Nếu bạn đã tạm trừ thuế các quý đầu năm mà tổng doanh thu cả năm vô tình vượt quá mười tỷ đồng, bạn bắt buộc phải kê khai điều chỉnh và nộp trả lại toàn bộ phần thuế đã giảm.
  8. Với hộ kinh doanh đang mấp mé mốc mười tỷ đồng dịp cuối năm, theo dõi sát doanh thu quý bốn quan trọng không kém việc bán thêm đơn hàng mới.
- **Gợi ý hình (không dùng ảnh/clip báo chí có bản quyền):**
  - *Khung 0:* Đồ họa chia đôi `DOANH THU ≤10 TỶ · -30% THUẾ` kèm số hiệu `Nghị định 398/2026/NĐ-CP`.
  - *Cảnh giữa:* Biểu đồ `waterfall` gắn nhãn `VÍ DỤ GIẢ ĐỊNH (DOANH THU 8 TỶ/NĂM)`: Thuế gốc `40 triệu` → Giảm 30% (`-12 triệu`) → Thực nộp `28 triệu`.
  - *Cảnh kết:* Biểu đồ bước nhảy (cliff chart) tại ranh giới doanh thu `10 tỷ đồng` (vượt ngưỡng phải hoàn lại 30% đã tạm trừ), kèm clip Pexels tự do cảnh đóng gói đơn hàng.
- **Pháp lý CK:** *"Nội dung giáo dục, không phải tư vấn đầu tư."*

### Short 4 · `ck-vang-sjc-140-trieu-chenh-14-trieu` (Sự kiện `ck_03` — Loại L → dẫn sang Long `ck-d1-vang-dinh`)
- **Dàn ý 8 câu đọc:**
  1. Hai tuần lỗ mười một triệu mỗi lượng vàng. *(9 từ)*
  2. Cuối tháng mười vừa qua, nhịp lao dốc liên tiếp trên thị trường kim loại quý đã đẩy người mua vàng ngắn hạn vào cảnh lỗ hơn mười một triệu đồng một lượng chỉ sau hai tuần.
  3. Sáng ngày hai tháng mười một, giá vàng miếng SJC đảo chiều tăng một triệu đồng, niêm yết mua vào một trăm ba mươi bảy triệu và bán ra một trăm bốn mươi triệu đồng một lượng.
  4. Cùng thời điểm đó, giá vàng thế giới quy đổi chỉ nằm quanh mức một trăm hai mươi ba phẩy tám triệu đồng một lượng.
  5. Khoảng vênh giữa vàng miếng trong nước và thế giới vẫn neo cao từ mười bốn phẩy ba triệu đến hơn mười sáu triệu đồng mỗi lượng tùy cách quy đổi.
  6. Người mua vàng lướt sóng phải gánh cùng lúc hai lớp đệm rủi ro trước khi thấy đồng lãi đầu tiên.
  7. Lớp thứ nhất là chênh lệch ba triệu đồng giữa giá tiệm bán ra và giá tiệm mua vào ngay tại quầy, còn lớp thứ hai là khoản vênh hơn mười bốn triệu đồng so với quốc tế.
  8. Khi bước qua cửa tiệm với hai lớp chênh lệch đó, bạn đã tự chấp nhận đứng sau vạch xuất phát cả chục triệu đồng trên mỗi lượng vàng.
- **Gợi ý hình (không dùng ảnh/clip báo chí có bản quyền):**
  - *Khung 0:* Biểu đồ cột đôi `SJC 140TR ↔ THẾ GIỚI 123,8TR` với thanh đo độ vênh màu đỏ.
  - *Cảnh giữa:* Bảng điện tử mô phỏng tự dựng niêm yết ngày `02/11/2026`: Mua vào `137,0 triệu` – Bán ra `140,0 triệu`; biểu đồ cột chồng (`stack`) hiển thị 2 lớp chênh lệch (`3 triệu` chênh mua-bán + `14,3–16,2 triệu` chênh thế giới).
  - *Cảnh kết:* Sơ đồ vạch xuất phát âm của người mua lướt sóng. Gắn `"Video liên quan"` trong YouTube Studio trỏ về Long có thật `ck-d1-vang-dinh` (*"Xếp Hàng Mua Vàng Có Phải Là Đỉnh? Đọc Lại 11 Đợt Đổ Xô (2011-2026) Bằng Dữ Liệu"*).
- **Pháp lý CK:** *"Nội dung giáo dục, không phải tư vấn đầu tư."*

### Short 5 · `ck-lai-giam-05-tien-gui-80-ngan-han` (Sự kiện `ck_08` — Loại L → dẫn sang Long `ck-2026-kenh-dau-tu`)
- **Dàn ý 8 câu đọc:**
  1. Ông Phạm Đức Ấn lý giải dòng tiền gửi. *(9 từ)*
  2. Đầu tháng mười một năm hai nghìn không trăm hai mươi sáu, mặt bằng lãi suất tiết kiệm kỳ hạn từ sáu tháng trở lên giảm tới không phẩy năm điểm phần trăm một năm.
  3. Trong **ví dụ giả định** bạn gửi tiết kiệm năm trăm triệu đồng kỳ hạn một năm, mức giảm này làm tiền lãi cả năm vơi đi hai triệu năm trăm nghìn đồng.
  4. Thế nhưng bất chấp lãi suất hạ nhiệt, tiền nhàn rỗi của người dân vẫn chảy mạnh vào hệ thống ngân hàng.
  5. Giải trình trước Quốc hội ngày ba mươi mốt tháng mười, Thống đốc Ngân hàng Nhà nước Phạm Đức Ấn cho biết người dân gửi tiền nhiều vì cơ bản vẫn tin tưởng vào hệ thống.
  6. Đáng chú ý, tới tám mươi phần trăm tổng tiền gửi đang nằm ở các kỳ hạn ngắn, nhưng được người gửi quay vòng liên tục từ kỳ này sang kỳ khác.
  7. Khi vàng biến động hơn mười triệu đồng mỗi lượng và chứng khoán rung lắc mạnh, người giữ tiền chấp nhận mức sinh lời thấp hơn để đổi lấy thanh khoản và sự an toàn gốc.
  8. Chừng nào các kênh đầu tư khác chưa đủ ổn định, sổ tiết kiệm kỳ hạn ngắn vẫn là trạm trú ẩn mặc định của dòng tiền gia đình Việt.
- **Gợi ý hình (không dùng ảnh/clip báo chí có bản quyền):**
  - *Khung 0:* Hai mũi tên ngược chiều `LÃI -0,5% ↔ 80% GỬI NGẮN`.
  - *Cảnh giữa:* Thẻ tính toán `VÍ DỤ GIẢ ĐỊNH: GỬI 500 TRIỆU × (-0,5%/NĂM) = -2,5 TRIỆU TIỀN LÃI` (không nêu tên bất kỳ ngân hàng thương mại nào); thẻ trích dẫn phát biểu của Thống đốc NHNN Phạm Đức Ấn tại Quốc hội ngày `31/10/2026` kèm biểu đồ thanh `80% TIỀN GỬI NGẮN HẠN QUAY VÒNG`.
  - *Cảnh kết:* Biểu đồ đặt cạnh nhau độ biến động của các kênh tài sản năm 2026. Gắn `"Video liên quan"` trong Studio trỏ về Long có thật `ck-2026-kenh-dau-tu` (*"Năm 2026: Chứng Khoán, Vàng, Coin, Nhà Đất Đều Đỏ - Chỉ Sổ Tiết Kiệm Xanh. Nhưng Thắng Thật Không?"*).
- **Pháp lý CK:** *"Nội dung giáo dục, không phải tư vấn đầu tư."*

### Short 6 · `ck-binance-63-ty-rut-36-ty` (Sự kiện `ck_19` giao thoa `mim_01`, giữ góc CK — Loại S)
- **Dàn ý 8 câu đọc:**
  1. Hai mươi phút mất sáu phẩy ba tỷ đô. *(9 từ)*
  2. Đó là số tài sản số kỷ lục bị nhóm tin tặc rút khỏi ví nóng của sàn Binance sau khi âm thầm thử nghiệm trước ba mươi sáu tiếng.
  3. Dù sàn cam kết dùng quỹ dự trữ nội bộ bù đắp tới chín mươi lăm phần trăm thiệt hại, tâm lý phòng thủ của người giữ tiền đã lập tức kích hoạt.
  4. Ngay khi cổng rút tiền mở lại ngày một tháng mười một, nhà đầu tư đã rút ròng ba phẩy sáu mươi tư tỷ đô la chỉ trong chín tiếng rưỡi đầu tiên.
  5. Con số tháo chạy này tương đương hai phẩy một phần trăm tổng tài sản mà toàn bộ sàn đang quản lý.
  6. Cú sốc niềm tin còn lan sang cả thị trường tài chính truyền thống khi các quỹ ETF Bitcoin bị rút ròng sáu trăm bốn mươi ba triệu đô la trong phiên cuối tuần.
  7. Trong tài chính cá nhân, gửi tài sản trên một nền tảng lưu ký tập trung đồng nghĩa với việc bạn giao quyền kiểm soát khóa tài sản cho hệ thống của bên thứ ba.
  8. Khi sự cố bảo mật xảy ra, rủi ro lớn nhất với túi tiền của bạn không chỉ là số tiền bị đánh cắp, mà là cánh cổng rút tiền có thể đóng sập đúng lúc bạn cần thanh khoản nhất.
- **Gợi ý hình (không dùng ảnh/clip báo chí có bản quyền):**
  - *Khung 0:* Đồng hồ số 20 phút màu đỏ rực cùng cặp số `MẤT 6,3 TỶ ↔ RÚT 3,64 TỶ`.
  - *Cảnh giữa:* Timeline `36 giờ thử nghiệm → 20 phút mất 6,3 tỷ USD → Mở lại cổng 01/11 rút ròng 3,64 tỷ USD (2,1% tài sản) trong 9,5 giờ`; biểu đồ cột dòng vốn rút ròng `3,64 tỷ USD` trên sàn và `643 triệu USD` khỏi các quỹ ETF Bitcoin.
  - *Cảnh kết:* Sơ đồ minh họa rủi ro lưu ký tập trung và đóng băng thanh khoản cá nhân.
- **Pháp lý CK:** *"Nội dung giáo dục, không phải tư vấn đầu tư."*

---

## 3. Bảng Nguồn Factcheck (≥ 1 nguồn sơ cấp + ≥ 1 nguồn độc lập khác tòa soạn cho mỗi sự kiện, trích dẫn ≤ 25 từ)

| Short | Khẳng định / Con số / Tên / Ngày trong bài | Loại nguồn | Cơ quan / Tòa soạn | Trích dẫn nguyên văn (≤ 25 từ) | URL đã mở |
|---|---|---|---|---|---|
| **Short 1**<br>(`ck_02`) | Thuế TTĐB xăng về `0%` từ `01/11/2026` đến hết `31/03/2027` (`Nghị quyết 45/2026/NQ-CP`) | **Sơ cấp** | Báo Điện tử Chính phủ (Cổng TTĐT Chính phủ) | *"Từ 1/11/2026, thuế suất thuế tiêu thụ đặc biệt đối với xăng là 0%... có hiệu lực từ ngày 1/11 đến hết ngày 31/3/2027."* (24 từ) | https://baochinhphu.vn/tu-1-11-2026-thue-suat-thue-tieu-thu-dac-biet-doi-voi-xang-la-0-102261031175659858.htm |
| **Short 1**<br>(`ck_02`) | Phó Thủ tướng Nguyễn Văn Thắng ký `Nghị quyết 45/2026` ngày `31/10/2026` đưa thuế TTĐB xăng về `0%` | Độc lập 1 | VnExpress | *"Phó thủ tướng Nguyễn Văn Thắng vừa ký Nghị quyết 45/2026 ngày 31/10, quy định thuế suất thuế tiêu thụ đặc biệt với xăng các loại là 0%."* (25 từ) | https://vnexpress.net/thue-tieu-thu-dac-biet-voi-xang-ve-0-tu-ngay-mai-5139239.html |
| **Short 1**<br>(`ck_02`) | Xăng E5 RON 92 giảm `1.804 đồng/lít`, về không cao hơn `24.223 đồng/lít` từ `01/11/2026` | Độc lập 2 | Thanh Niên | *"Giá xăng E5RON 92 không cao hơn 24.223 đồng/lít, giảm 1.804 đồng/lít so với giá bán tối đa hiện hành."* (20 từ) | https://thanhnien.vn/gia-xang-dau-hom-nay-111-gia-xang-giam-manh-185261101074743844.htm |
| **Short 1**<br>(`ck_02`) | Xăng, điện giảm nhưng giá cước vận tải chưa giảm ngay vì cần lộ trình | Độc lập 3 | Dân Trí | *"Giá xăng, điện vừa được điều chỉnh giảm nhưng để doanh nghiệp giảm giá cước vận tải, dịch vụ cần lộ trình và thêm giải pháp hỗ trợ."* (25 từ) | https://dantri.com.vn/kinh-doanh/gia-xang-dien-dong-loat-ha-nhiet-sao-cuoc-van-tai-chua-giam-20261102164011827.htm |
| **Short 2**<br>(`ck_01`) | Giá bán lẻ điện bình quân giảm `2%` về `2.159,9037 đồng/kWh` từ `01/11/2026` (`Quyết định 1305/QĐ-EVN` & `2892/QĐ-BCT`) | **Sơ cấp** | Tập đoàn Điện lực Việt Nam (EVN) | *"Theo đó, giá bán lẻ điện bình quân là 2.159,9037 đồng/kWh (chưa bao gồm thuế giá trị gia tăng) áp dụng từ ngày 01 tháng 11 năm 2026."* (25 từ) | https://www.evn.com.vn/d6/news/Dieu-chinh-gia-ban-le-dien-binh-quan-tu-ngay-01-thang-11-nam-2026-6-12-32537.aspx |
| **Short 2**<br>(`ck_01`) | Giá điện giảm xuống gần `2.160 đồng/kWh` từ `01/11`, lần giảm đầu tiên sau gần `20 năm` liên tục tăng | Độc lập 1 | VnExpress | *"Giá bán lẻ điện bình quân giảm xuống gần 2.160 đồng mỗi kWh từ ngày 1/11, đánh dấu lần giảm đầu tiên sau gần 20 năm liên tục tăng."* (25 từ) | https://vnexpress.net/gia-dien-giam-2-tu-ngay-mai-5139154.html |
| **Short 2**<br>(`ck_01`) | Mức giảm tương đương hơn `44 đồng/kWh` (từ `2.204,0655` xuống `2.159,9037 đồng/kWh`) | Độc lập 2 | VietNamNet | *"Giá điện giảm hơn 44 đồng/kWh từ ngày mai 1/11."* (10 từ) | https://vietnamnet.vn/gia-dien-giam-hon-44-dong-kwh-tu-ngay-mai-1-11-2570253.html |
| **Short 3**<br>(`ck_06`) | `Nghị định 398/2026/NĐ-CP` giảm `30%` thuế TNCN, TNDN phải nộp từ kinh doanh có doanh thu không quá `10 tỷ đồng` | **Sơ cấp** | Báo Điện tử Chính phủ (Cổng TTĐT Chính phủ) | *"Hướng dẫn chi tiết giảm 30% số thuế TNCN, thuế TNDN phải nộp từ kinh doanh có doanh thu không quá 10 tỉ đồng."* (24 từ) | https://baochinhphu.vn/huong-dan-chi-tiet-giam-30-so-thue-tncn-thue-tndn-phai-nop-tu-kinh-doanh-co-doanh-thu-khong-qua-10-ti-dong-102261030095834891.htm |
| **Short 3**<br>(`ck_06`) | Áp dụng cho cá nhân kinh doanh và doanh nghiệp doanh thu `≤ 10 tỷ đồng/năm` trong năm `2026` và `2027` | Độc lập 1 | VietNamNet | *"Cá nhân kinh doanh và doanh nghiệp có doanh thu không quá 10 tỷ đồng/năm được giảm 30% số thuế thu nhập cá nhân, thuế thu nhập doanh nghiệp."* (25 từ) | https://vietnamnet.vn/doanh-thu-khong-qua-10-ty-dong-nam-duoc-giam-30-thue-thu-nhap-ca-nhan-2570192.html |
| **Short 3**<br>(`ck_06`) | Được tự giảm `30%` thuế thu nhập ngay theo từng kỳ kê khai quý; vượt `10 tỷ đồng` cả năm phải nộp bổ sung | Độc lập 2 | VnEconomy | *"Doanh nghiệp, hộ kinh doanh được giảm 30% thuế thu nhập theo từng kỳ."* (14 từ) | https://vneconomy.vn/doanh-nghiep-ho-kinh-doanh-duoc-giam-30-thue-thu-nhap-theo-tung-ky.htm |
| **Short 4**<br>(`ck_03`) | Bảng giá niêm yết vàng miếng SJC ngày `02/11/2026`: Mua vào `137 triệu` – Bán ra `140 triệu đồng/lượng` | **Sơ cấp** | Công ty Vàng bạc Đá quý Sài Gòn (SJC) | *"Vàng SJC 1L, 10L, 1KG: Mua vào 137.000.000 đồng/lượng - Bán ra 140.000.000 đồng/lượng."* (14 từ) | https://sjc.com.vn/gia-vang-online |
| **Short 4**<br>(`ck_03`) | Giá vàng thế giới quy đổi ngày `02/11` khoảng `123,8 triệu đồng/lượng`, SJC niêm yết `137–140 triệu`, cao hơn thế giới `14,3 triệu` | Độc lập 1 | CafeF | *"Giá vàng thế giới quy đổi hiện ở mức khoảng 123,8 triệu đồng/lượng, trong khi vàng miếng SJC được niêm yết ở mức 137-140 triệu đồng/lượng."* (25 từ) | https://cafef.vn/gia-vang-ngay-2-11-vang-sjc-cao-hon-the-gioi-143-trieu-dong-luong-188261102073347541.chn |
| **Short 4**<br>(`ck_03`) | Sáng `02/11`, mỗi lượng vàng đảo chiều tăng `1 triệu đồng` lên `140 triệu đồng/lượng` | Độc lập 2 | VnExpress | *"Sau phiên giảm mạnh vào cuối tuần, mỗi lượng vàng đảo chiều tăng 1 triệu đồng, chênh lệch với thế giới vẫn hơn 17 triệu đồng."* (25 từ) | https://vnexpress.net/gia-vang-mieng-dao-chieu-len-140-trieu-dong-mot-luong-5139574.html |
| **Short 4**<br>(`ck_03`) | Nhịp lao dốc cuối tháng 10 đẩy người mua lỗ hơn `11 triệu đồng/lượng` sau `2 tuần` | Độc lập 3 | Thanh Niên | *"Giá vàng hôm nay 1.11.2026: Lao dốc đẩy người mua lỗ hơn 11 triệu sau 2 tuần."* (17 từ) | https://thanhnien.vn/gia-vang-hom-nay-1112026-lao-doc-day-nguoi-mua-lo-hon-11-trieu-sau-2-tuan-185261031181409164.htm |
| **Short 5**<br>(`ck_08`) | Thống đốc NHNN **Phạm Đức Ấn** giải trình Quốc hội (`31/10/2026`): tiền gửi ngắn hạn chiếm `80%`, người dân gửi nhiều vì tin tưởng hệ thống | **Sơ cấp** | Báo Điện tử Chính phủ (Cổng TTĐT Chính phủ) | *"Người dân gửi nhiều tiền vào ngân hàng bởi cơ bản vẫn tin tưởng hệ thống."* (16 từ) | https://baochinhphu.vn/thong-doc-noi-ve-lai-suat-tin-dung-bat-dong-san-va-von-cho-doanh-nghiep-102261031154523318.htm |
| **Short 5**<br>(`ck_08`) | Thống đốc NHNN lý giải việc người dân vẫn gửi tiết kiệm nhiều dù lãi suất hạ là nét riêng khi thị trường vốn chưa hấp dẫn hơn | Độc lập 1 | VnExpress | *"Thống đốc cho rằng đây là một nét riêng của Việt Nam khi người dân vẫn gửi tiết kiệm nhiều."* (20 từ) | https://vnexpress.net/thong-doc-nguoi-dan-gui-tien-nhieu-vi-tin-tuong-he-thong-ngan-hang-5139105.html |
| **Short 5**<br>(`ck_08`) | Lãi suất tiết kiệm đầu tháng `11/2026` giảm tới `0,5 điểm phần trăm` ở nhiều kỳ hạn từ 6 tháng trở lên | Độc lập 2 | VietNamNet | *"Lãi suất ngân hàng hôm nay 2/11: Giảm tới 0,5 điểm phần trăm ở nhiều kỳ hạn."* (17 từ) | https://vietnamnet.vn/lai-suat-ngan-hang-hom-nay-2-11-giam-toi-0-5-diem-phan-tram-o-nhieu-ky-han-2570538.html |
| **Short 6**<br>(`ck_19`) | FBI xác nhận nhóm tin tặc Triều Tiên (**TraderTraitor**) đứng sau vụ đánh cắp hơn `6 tỷ USD` trên sàn Binance | **Sơ cấp 1** | Cục Điều tra Liên bang Mỹ (FBI) | *"North Korea Responsible for $6 Billion+ Binance Attack."* (8 từ) | https://www.fbi.gov/investigate/cyber/alerts/2026/north-korea-responsible-for-6-billion-binance-attack |
| **Short 6**<br>(`ck_19`) | Binance công bố số liệu bảo mật, sử dụng quỹ dự trữ SAFU bù đắp thiệt hại và mở lại rút tiền theo giai đoạn | **Sơ cấp 2** | Binance Official Blog | *"Key Security Numbers, Scam Alerts, and the SAFU Fund."* (9 từ) | https://www.binance.com/en/blog/all/key-security-numbers-scam-alerts-and-the-safu-fund-4339115714421111005 |
| **Short 6**<br>(`ck_19`) | Hacker thử nghiệm trước `36 tiếng`, rút cạn `6,3 tỷ USD` từ ví nóng Binance chỉ trong `20 phút` | Độc lập 1 | VnExpress | *"Nhóm tin tặc được cho là thực hiện giao dịch thử nghiệm trước ít nhất 36 tiếng, sau đó mới tổng tấn công Binance, rút cạn tiền trong 20 phút."* (25 từ) | https://vnexpress.net/hacker-thu-nghiem-truoc-36-tieng-rut-6-3-ty-usd-tu-vi-binance-trong-20-phut-5139116.html |
| **Short 6**<br>(`ck_19`) | Mở lại cổng rút tiền ngày `01/11/2026`, nhà đầu tư rút ròng `3,64 tỷ USD` (làm tròn `3,6 tỷ USD`, bằng `2,1%` tổng tài sản trên sàn) trong `9,5 giờ` | Độc lập 2 | VnEconomy | *"Khoảng 2,1% tổng tài sản mà Binance đang quản lý đã bị rút, sau khi nền tảng giao dịch tiền mã hóa lớn nhất thế giới hoạt động trở lại."* (25 từ) | https://vneconomy.vn/binance-vua-khoi-phuc-chuc-nang-rut-tien-36-ty-usd-chay-khoi-san.htm |
| **Short 6**<br>(`ck_19`) | Binance mở lại cổng rút tiền, bù đắp `95%` tài sản vụ hack `6,3 tỷ USD` | Độc lập 3 | VietNamNet | *"Binance mở lại cổng rút tiền, bù đắp 95% tài sản vụ hack 6,3 tỷ USD tiền mã hóa."* (19 từ) | https://vietnamnet.vn/binance-mo-lai-cong-rut-tien-bu-dap-95-tai-san-vu-hack-6-3-ty-usd-tien-ma-hoa-2570465.html |
| **Short 6**<br>(`ck_19`) | Các quỹ ETF Bitcoin bị rút ròng `643 triệu USD` trong phiên thứ Sáu | Độc lập 4 | CoinDesk | *"Bitcoin ETFs lost $643 million in outflows Friday, and 2026 is barely green now."* (14 từ) | https://www.coindesk.com/markets/2026/11/02/bitcoin-etfs-lost-usd643-million-in-outflows-friday-and-2026-is-barely-green-now |

---

## 4. Tóm tắt Plan Long CK đề xuất (`data/long/ck-xang-dien-thue-11-2026/plan.md`)

- **Chủ đề:** `ck-xang-dien-thue-11-2026` (độ dài mục tiêu **10–12 phút**, ~2.250–2.600 âm tiết, **9 chương** `CH00`–`CH08`, giọng đọc **Ngọc Huyền**).
- **Vì sao chọn đề tài này:** Bám sát cụm 3 quyết định chính sách lớn nhất tuần 45 cùng hội tụ quanh mốc `01/11/2026`: thuế TTĐB xăng về `0%` trong 5 tháng kéo xăng E5 RON 92 giảm `1.804 đồng/lít` (`ck_02`), giá bán lẻ điện bình quân giảm `2%` (`44,16 đồng/kWh`) lần đầu tiên sau gần `20 năm` (`ck_01`), và giảm `30%` thuế thu nhập cho cá nhân/hộ kinh doanh có doanh thu `≤ 10 tỷ đồng/năm` (`ck_06`). Khớp với số đo tuần 44: chủ đề hóa đơn đời sống có cặp số tiền đối nghịch đạt trung vị view cao gấp hơn 3 lần chủ đề thị trường chung.
- **3 phương án tiêu đề (≤ 60 ký tự):**
  1. `Xăng Giảm 1.804Đ, Điện Hạ Sau 20 Năm: Ví Bạn Dư Bao Nhiêu?` *(58 ký tự)*
  2. `Từ 1/11 Xăng Giảm 1.804Đ, Điện Hạ 2%: Sao Giá Chợ Chưa Hạ?` *(58 ký tự)*
  3. `5 Tháng Thuế Xăng 0% Và Điện Giảm 2%: Phép Tính Cho Ví Bạn` *(58 ký tự)*
- **Cold open (0–35 giây, dữ kiện thật 100%):** Mở tại cột mốc 0h ngày `01/11/2026` khi xăng E5 RON 92 giảm `1.804 đồng/lít` về `24.223 đồng/lít`, giá điện bán lẻ bình quân giảm `2%` về `2.159,9037 đồng/kWh` sau gần `20 năm` liên tục tăng, và hộ kinh doanh dưới `10 tỷ đồng` được cắt `30%` thuế thu nhập — đối lập với thực tế sáng `02/11` khi bảng giá cước vận tải và hàng hóa ngoài chợ vẫn đứng yên. Biểu đồ `bars` đầu tiên xuất hiện trước giây 15.
- **3 vòng lặp mở:**
  1. Ghép cả xăng và điện suốt 5 tháng hiệu lực (`11/2026–03/2027`), một gia đình giữ lại được chính xác bao nhiêu tiền mặt? *(Đóng ở CH03).*
  2. Vì sao xăng và điện giảm tức thì sau một đêm nhưng cước vận tải và hàng tiêu dùng luôn trễ nhịp? *(Đóng ở CH05).*
  3. Vì sao quy định giảm `30%` thuế hộ kinh doanh có một "vách đá" ở đúng mốc doanh thu `10 tỷ đồng` có thể khiến chủ hộ phải nộp hoàn lại toàn bộ thuế đã tạm giảm của các quý trước? *(Đóng ở CH07).*
- **Dàn 9 chương (`CH00`–`CH08`):**
  - `CH00`: Cold open — Đêm 01/11 và ba con số giảm giá cùng lúc (`bars`, `date`, `counter`, `question`).
  - `CH01`: Giải phẫu 1 lít xăng `24.223 đồng` khi thuế TTĐB về `0%` suốt 5 tháng (`waterfall`, `bars`, `ledger` dòng 1).
  - `CH02`: `44,16 đồng` mỗi số điện — Lần bẻ lái đầu tiên sau gần 20 năm (`race` + `abs`, `counter`, `ledger` dòng 2).
  - `CH03`: Phép tính 5 tháng cho ví tiền một hộ gia đình — `VÍ DỤ GIẢ ĐỊNH` 80 lít xăng + 400 kWh điện/tháng tiết kiệm `> 818.000 đồng` trong 5 tháng (`heat`, `stack`, `ledger` dòng 3).
  - `CH04`: Vì sao cây xăng hạ giá sau một đêm mà bảng giá cước vận tải vẫn đứng yên? (`stack` cấu thành chi phí vận tải, `timeline` độ trễ hợp đồng quý).
  - `CH05`: Tác động gián tiếp — Khi `2%` giá điện chặn cơn sốt giá hàng hóa mùa Tết 2027 (`bars`, `ledger` dòng 4).
  - `CH06`: Mảnh ghép thứ ba (`Nghị định 398/2026/NĐ-CP`) — Giảm `30%` thuế thu nhập cho hộ kinh doanh dưới `10 tỷ đồng` (`waterfall` `VÍ DỤ GIẢ ĐỊNH`, `ledger` dòng 5).
  - `CH07`: Cẩn thận "vách đá 10 tỷ đồng" dịp cao điểm cuối năm (`bars` đối chiếu doanh thu `9,95 tỷ` vs `10,05 tỷ` `VÍ DỤ GIẢ ĐỊNH`, `slam`, `ledger` dòng 6).
  - `CH08`: Kết luận & 3 con số cần nhớ cho ví tiền từ `11/2026` đến `03/2027` (`ledger` hoàn chỉnh 6 dòng, `kinetic`).
- **3 Short đi kèm:** Short 1 (`ck-thue-xang-0-giam-1804`), Short 2 (`ck-dien-giam-44-dong-20-nam`), Short 3 (`ck-ho-kinh-doanh-giam-30-thue`).
- **Grok Bot ảnh AI (`scripts/ai_img_request.py`):** Chưa gọi webhook ở bước lập plan này (đúng quy định tại `docs/codex/long-rules.md` và chờ chủ kênh duyệt `plan.md` trước khi viết kịch bản + `ai_prompts.md`).

---

## 5. Danh sách CHƯA KIỂM (Không dùng cho Hook và Lời khẳng định)

| Mã | Sự kiện liên quan | Chi tiết / Con số ghi nhận trên tít phụ hoặc nguồn thứ cấp | Trạng thái | Lý do & Cách xử lý an toàn trong kịch bản |
|---|---|---|---|---|
| **CK-UK-01** | `ck_15` (Xét xử vụ Phó Đức Nam / Mr Pips) | Con số *"thu giữ 5.300 tỷ đồng tài sản của Mr Pips"* | **CHƯA KIỂM** *(mâu thuẫn tại tòa)* | Tại phiên xét xử ngày `02/11/2026` (Tuổi Trẻ: `...thu-giu-5300-ti-dong-tai-san-mr-pips-tai-sao-lai-nhieu-tien-the-100261102111233302.htm`), khi luật sư hỏi về con số `5.300 tỷ đồng` từng đăng trên báo chí, cả bị cáo Phó Đức Nam và Lê Khắc Ngọ đều thắc mắc vì sao nhiều tiền như vậy; trong khi cáo trạng xác định số tiền chiếm đoạt/thu lợi bất chính từ 920 bị hại là khoảng `1.568 tỷ đồng` và rửa tiền hơn `560 tỷ đồng`. **Đã loại khỏi 6 Short chính và tuyệt đối không dùng số 5.300 tỷ đồng làm hook.** |
| **CK-UK-02** | `ck_19` (Rút tiền khỏi sàn Binance sau vụ hack) | Con số *"rút tới 6 tỷ USD khỏi sàn Binance ngay khi mở lại cổng"* | **CHƯA KIỂM** *(nhầm lẫn với số bị hack)* | Nhãn tóm tắt ghi khoảng `"rút 3,6–6 tỷ USD"`. Đối chiếu thông báo của Binance và bài viết trên VnEconomy (`...36-ty-usd-chay-khoi-san.htm`), lượng rút ròng xác thực trong `9,5 giờ` đầu là **`3,64 tỷ USD`** (`2,1%` tổng tài sản), còn `6,3 tỷ USD` là số tiền bị hacker đánh cắp ngày `29/10`. **Không dùng mốc "rút 6 tỷ USD" trong hook và lời đọc.** |
| **CK-UK-03** | `ck_01` (Giảm 2% giá bán lẻ điện bình quân) | Mốc thời hạn *"giá điện giảm 2% áp dụng đến hết tháng 03/2027"* | **CHƯA KIỂM** | Khác với Nghị quyết `45/2026/NQ-CP` về thuế TTĐB xăng ghi rõ hiệu lực đến hết `31/03/2027`, thông cáo gốc của EVN về Quyết định `1305/QĐ-EVN` và `2892/QĐ-BCT` chỉ ghi *"áp dụng từ ngày 01 tháng 11 năm 2026"* (điều chỉnh theo cơ chế 3 tháng/lần của Nghị định `72/2025/NĐ-CP` và `278/2026/NĐ-CP`). **Không gắn mốc "đến hết 31/03/2027" cho giá điện trong hook và lời đọc.** |
| **CK-UK-04** | `ck_03` (Giá vàng SJC ngày 02/11/2026) | Một con số chênh lệch duy nhất giữa vàng SJC và thế giới sáng `02/11` (`14,3 triệu` vs `> 17 triệu đồng/lượng`) | **CHƯA KIỂM** *(khác công thức quy đổi tỷ giá/phí)* | Sáng `02/11/2026`, CafeF ghi giá thế giới quy đổi là `123,8 triệu đồng/lượng` và tít ghi SJC (`140 triệu`) cao hơn thế giới `14,3 triệu đồng/lượng` (tính theo công thức quy đổi cộng phí/tỷ giá riêng), trong khi VnExpress ghi chênh lệch `hơn 17 triệu đồng/lượng`. **Không dùng số chênh lệch ở câu mở đầu (câu mở dùng `2 tuần lỗ 11 triệu`), và trong lời đọc nêu rõ biên độ "từ 14,3 triệu đến hơn 16 triệu đồng mỗi lượng tùy cách quy đổi".** |
| **CK-UK-05** | `ck_08` (Tiền gửi chảy vào ngân hàng) | Số dư tuyệt đối tiền gửi dân cư toàn hệ thống tính đến hết tháng `10/2026` | **CHƯA KIỂM** | Tại phiên giải trình Quốc hội ngày `31/10/2026`, Thống đốc NHNN Phạm Đức Ấn công bố tỷ trọng tiền gửi ngắn hạn chiếm khoảng `80%`, chưa công bố số dư tuyệt đối hết tháng `10/2026`. **Chỉ dùng tỷ trọng `80%` và mức giảm lãi suất `0,5 điểm phần trăm`.** |
| **CK-UK-06** | `ck_06` (Giảm 30% thuế thu nhập dưới 10 tỷ đồng) | Tổng số tiền giảm thu ngân sách nhà nước của riêng Nghị định `398/2026/NĐ-CP` | **CHƯA KIỂM** | Bản tin công bố Nghị định `398/2026/NĐ-CP` xác nhận mức giảm `30%` và ngưỡng doanh thu `10 tỷ đồng/năm` cho kỳ tính thuế `2026–2027`, nhưng chưa trích bảng tổng dự toán giảm thu ngân sách. **Không đưa ước tính tổng thu ngân sách vào hook hay lời đọc.** |
