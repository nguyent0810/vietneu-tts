# GH-33-L · Báo cáo Viết lại Lời đọc 12 Short Pilot (100–125 từ)

- **Issue:** https://github.com/nguyent0810/Youtube_Creator_V2/issues/33
- **Brief:** `docs/pm/tickets/GH-33-grok-lines.md`
- **File kết quả chính:** `docs/pm/tickets/GH-33-lines.json`
- **Phạm vi thực hiện:** Chỉ ghi `docs/pm/tickets/GH-33-lines.json` và `docs/pm/tickets/GH-33-lines-report.md`; không sửa spec hay code, không render, không commit, không đổi lịch.

---

## 1. Bảng thống kê số từ, độ dài câu và chuỗi `beats` (12/12 Short)

Tất cả 12 Short đều gồm **8 câu**, tổng số từ từ **119 đến 122 từ** (nằm gọn trong khung **100–125 từ** tính theo khoảng trắng), mọi câu lẻ đều **≤ 17 từ** (ngưỡng **≤ 18 từ**), giữ **nguyên văn 100%** `lines[0]` và `frame0` đã chốt trong `GH-33-{MIM,CK}-pack.md`, lấy đúng `title_recommended` từ `GH-33-titles.json`, có đủ 3 nhóm `M`, `D`, `G`, không có 3 câu liên tiếp cùng loại hình, và **12 chuỗi `beats` hoàn toàn khác nhau**.

| # | Slug | Kênh | Số câu | Số từ từng câu (`L1..L8`) | Câu dài nhất | Tổng số từ (`word_count`) | Chuỗi `beats` (đủ `M,D,G`, không 3 liền nhau, 12 mẫu duy nhất) |
|---:|---|---|---:|---|---:|---:|---|
| 1 | `mim-binance-20-phut-6-3-ty` | MIM | 8 | `9, 16, 16, 16, 15, 16, 16, 17` | 17 | **121** | `D-G-M-G-D-M-G-T` |
| 2 | `mim-cam-nhap-dien-thoai-cu-2027` | MIM | 8 | `9, 16, 16, 16, 16, 16, 16, 16` | 16 | **121** | `D-D-G-M-G-M-D-T` |
| 3 | `mim-sam-altman-ram-5-phan-tram` | MIM | 8 | `9, 17, 16, 16, 15, 16, 15, 16` | 17 | **120** | `M-D-G-T-M-G-D-G` |
| 4 | `mim-ve-tinh-google-4-chip-tpu` | MIM | 8 | `9, 16, 16, 16, 15, 15, 17, 16` | 17 | **120** | `D-G-T-G-M-G-D-M` |
| 5 | `mim-9-tren-10-ai-tu-lay-otp` | MIM | 8 | `9, 17, 16, 15, 16, 15, 15, 16` | 17 | **119** | `D-G-D-G-M-D-G-T` |
| 6 | `mim-android-20-tin-nhan-tu-than` | MIM | 8 | `9, 16, 16, 15, 16, 16, 16, 16` | 16 | **120** | `D-G-M-G-D-M-D-T` |
| 7 | `ck-thue-xang-0-giam-1804` | CK | 8 | `9, 17, 16, 15, 16, 15, 16, 15` | 17 | **119** | `D-D-G-D-D-M-G-T` |
| 8 | `ck-dien-giam-44-dong-20-nam` | CK | 8 | `9, 16, 16, 16, 15, 16, 16, 16` | 16 | **120** | `G-D-D-G-M-D-G-T` |
| 9 | `ck-ho-kinh-doanh-giam-30-thue` | CK | 8 | `9, 16, 15, 16, 17, 16, 16, 17` | 17 | **122** | `D-G-D-G-D-M-G-T` |
| 10 | `ck-vang-sjc-140-trieu-chenh-14-trieu` | CK | 8 | `9, 16, 17, 16, 16, 15, 16, 16` | 17 | **121** | `D-D-M-D-G-G-D-T` |
| 11 | `ck-lai-giam-05-tien-gui-80-ngan-han` | CK | 8 | `9, 16, 16, 16, 16, 16, 17, 16` | 17 | **122** | `G-D-D-M-G-D-M-T` |
| 12 | `ck-binance-63-ty-rut-36-ty` | CK | 8 | `9, 16, 16, 15, 16, 16, 16, 16` | 16 | **120** | `D-G-D-D-G-D-M-T` |

---

## 2. Kiểm tự động câu trọn nghĩa (Không cắt câu cụt)

Đã chạy script kiểm tự động (`verify_gh33_lines.ps1`, mã thoát `0`, **0 lỗi**) trên toàn bộ **96 câu** của 12 bài với các cổng:
1. **Cấu trúc câu & dấu câu:** Mọi câu kết thúc bằng dấu chấm `.`, không có dấu hai chấm `:`, chấm phẩy `;` hay dấu chấm hỏi `?`.
2. **Không kết thúc bằng hư từ / từ treo cắt cụt:** Kiểm tự động đối chiếu từ cuối của từng câu với tập từ nối, giới từ, phó từ và vị ngữ treo (`và, hoặc, nhưng, mà, thì, là, của, cho, với, tại, từ, để, khi, nếu, vì, do, bởi, như, đang, đã, sẽ, vẫn, còn, rất, quá, hơn, nhất, bị, được, phải, cần, muốn, âm, dương, trên, dưới, trong, ngoài, giữa, theo, về, ra, vào, lên, xuống, tới, đến`) → **0 câu vi phạm**.
3. **Bảng kiểm cụm kết câu (2–3 từ cuối) của cả 96 câu:**

| # | Slug | Kết câu `L1..L4` | Kết câu `L5..L8` | Trạng thái |
|---:|---|---|---|---|
| 1 | `mim-binance-20-phut-6-3-ty` | `tỷ đô.` · `chuỗi khối.` · `sáu giờ.` · `ví nóng.` | `tên TraderTraitor.` · `tiền chết.` · `tỷ đô.` · `giữ tiền.` | **PASS (Trọn nghĩa)** |
| 2 | `mim-cam-nhap-dien-thoai-cu-2027` | `cấm nhập.` · `ảnh cũ.` · `nguyên chiếc.` · `máy mới.` | `cấm nhập.` · `dựng lại.` · `vắng bóng.` · `khép lại.` | **PASS (Trọn nghĩa)** |
| 3 | `mim-sam-altman-ram-5-phan-tram` | `bỏ phí.` · `thời gian.` · `đám mây.` · `RAM riêng.` | `chủ AI.` · `dữ liệu.` · `từ xa.` · `đám mây.` | **PASS (Trọn nghĩa)** |
| 4 | `mim-ve-tinh-google-4-chip-tpu` | `vũ trụ.` · `Na Uy.` · `quỹ đạo.` · `vệ tinh.` | `Trái Đất.` · `băng thông.` · `tại chỗ.` · `không gian.` | **PASS (Trọn nghĩa)** |
| 5 | `mim-9-tren-10-ai-tu-lay-otp` | `vượt quyền.` · `nhân AI.` · `qua email.` · `chờ duyệt.` | `mức ví.` · `kẻ xấu.` · `người dùng.` · `bằng không.` | **PASS (Trọn nghĩa)** |
| 6 | `mim-android-20-tin-nhan-tu-than` | `sập Android.` · `tử thần.` · `màn hình.` · `cổng ngầm.` | `sập sóng.` · `khẩn cấp.` · `khởi động.` · `cổng sóng.` | **PASS (Trọn nghĩa)** |
| 7 | `ck-thue-xang-0-giam-1804` | `nghìn tám.` · `năm tháng.` · `mỗi lít.` · `24.159 đồng.` | `90.000 đồng.` · `hạ ngay.` · `nhân công.` · `một nhịp.` | **PASS (Trọn nghĩa)** |
| 8 | `ck-dien-giam-44-dong-20-nam` | `phần trăm.` · `mỗi kWh.` · `năm tăng.` · `20.000 đồng.` | `cà phê.` · `triệu đồng.` · `sản xuất.` · `cuối năm.` | **PASS (Trọn nghĩa)** |
| 9 | `ck-ho-kinh-doanh-giam-30-thue` | `phần trăm.` · `ngay 30%.` · `và 2027.` · `khai quý.` | `12 triệu.` · `tỷ đồng.` · `đã giảm.` · `bán hàng.` | **PASS (Trọn nghĩa)** |
| 10 | `ck-vang-sjc-140-trieu-chenh-14-trieu` | `lượng vàng.` · `triệu đồng.` · `một lượng.` · `một lượng.` | `cách tính.` · `rất dày.` · `quốc tế.` · `xuất phát.` | **PASS (Trọn nghĩa)** |
| 11 | `ck-lai-giam-05-tien-gui-80-ngan-han` | `tiền gửi.` · `một năm.` · `triệu đồng.` · `ngân hàng.` | `hệ thống.` · `vòng đều.` · `toàn gốc.` · `của bạn.` | **PASS (Trọn nghĩa)** |
| 12 | `ck-binance-63-ty-rut-36-ty` | `tỷ đô.` · `36 tiếng.` · `lên ngay.` · `giờ đầu.` | `quản lý.` · `cuối tuần.` · `thứ ba.` · `bị khóa.` | **PASS (Trọn nghĩa)** |

---

## 3. Đối chiếu dữ kiện giữa `title_recommended` (`GH-33-titles.json`) và `lines` mới

**Kết quả:** **12/12 bài** giữ đầy đủ toàn bộ dữ kiện có trên `title_recommended` trong lời đọc mới (**0 bài bị rơi dữ kiện tiêu đề**).

| # | Slug | `title_recommended` | Dữ kiện trong `lines` mới |
|---:|---|---|---|
| 1 | `mim-binance-20-phut-6-3-ty` | `Binance Bị Hack 6,3 Tỷ Đô Trong 20 Phút: Khóa Cứng 3 Tỷ Đô` | L1 (`Hai mươi phút, mất sáu phẩy ba tỷ đô`), L2 (`sàn Binance bị hack`), L7 (`khóa cứng ba tỷ đô`). |
| 2 | `mim-cam-nhap-dien-thoai-cu-2027` | `Cấm Nhập Điện Thoại Cũ 01/01/2027: Khóa Cả Hàng Tân Trang` | L1 (`mùng một tháng một năm 2027, cấm nhập`), L2 (`cấm nhập khẩu điện thoại... cũ`), L4 (`khóa luôn cả hàng tân trang`). |
| 3 | `mim-sam-altman-ram-5-phan-tram` | `Sam Altman Chê RAM Máy Cá Nhân Chỉ Dùng 5%: Musk Phản Bác` | L1 (`Sam Altman chê thanh RAM`), L2 (`RAM máy cá nhân chỉ dùng năm phần trăm thời gian`), L4 (`Elon Musk liền phản bác`). |
| 4 | `mim-ve-tinh-google-4-chip-tpu` | `Vệ Tinh AI Google Chạy 4 Chip TPU: Viết 3 Dòng Thơ Vũ Trụ` | L1 (`Bốn chip Google viết ba dòng thơ vũ trụ`), L2 (`vệ tinh AI Suncatcher của Google`), L4 (`bốn chip TPU`). |
| 5 | `mim-9-tren-10-ai-tu-lay-otp` | `Tác Nhân AI Tự Đọc Email Lấy OTP: 9/10 Mô Hình Vượt Hạn Mức` | L1 (`Chín trên mười mô hình AI tự vượt quyền`), L4 (`Chín trên mười tác nhân AI đã tự vượt hạn mức`), L5 (`tự mở email lấy mã OTP`). |
| 6 | `mim-android-20-tin-nhan-tu-than` | `Lỗ Hổng Android Tin Nhắn Tử Thần: 8 Byte, 20 Tin Sập Máy` | L1 (`Chỉ tám byte, hai mươi tin làm sập Android`), L2 (`lỗ hổng Android mang tên tin nhắn tử thần`), L7 (`hai mươi tin nhắn này, máy sẽ kẹt`). |
| 7 | `ck-thue-xang-0-giam-1804` | `Giá xăng hôm nay giảm 1.804 đồng/lít: 5 tháng thuế 0%` | L2 (`thuế tiêu thụ đặc biệt với xăng về 0% trong năm tháng`), L3 (`Giá xăng hôm nay với E5 RON 92 giảm 1.804 đồng... mỗi lít`). |
| 8 | `ck-dien-giam-44-dong-20-nam` | `Giá điện giảm 44 đồng/kWh: Lần đầu hạ sau gần 20 năm tăng` | L3 (`Giá điện giảm 44 đồng mỗi kWh là lần đầu hạ sau gần 20 năm tăng`). |
| 9 | `ck-ho-kinh-doanh-giam-30-thue` | `Thuế hộ kinh doanh giảm 30% năm 2026: Ngưỡng cắt cứng 10 tỷ` | L2 (`Thuế hộ kinh doanh có doanh thu không quá mười tỷ đồng được giảm ngay 30%`), L3 (`năm 2026`), L6 (`ngưỡng cắt cứng ở đúng mốc doanh thu mười tỷ đồng`). |
| 10 | `ck-vang-sjc-140-trieu-chenh-14-trieu` | `Giá vàng SJC 140 triệu ngày 2/11: Vênh thế giới 14,3 triệu` | L3 (`Ngày 2 tháng 11, giá vàng SJC mua vào 137 triệu, bán ra 140 triệu`), L5 (`Mức vênh thế giới vẫn từ 14,3 triệu đến hơn 16 triệu đồng`). |
| 11 | `ck-lai-giam-05-tien-gui-80-ngan-han` | `Lãi suất tiết kiệm giảm 0,5%/năm: Sao 80% vẫn gửi ngắn hạn?` | L2 (`lãi suất tiết kiệm ở nhiều kỳ hạn giảm tới 0,5% một năm`), L6 (`80% tiền gửi đang nằm ở kỳ hạn ngắn`). |
| 12 | `ck-binance-63-ty-rut-36-ty` | `Binance bị hack 6,3 tỷ đô: Rút 3,64 tỷ đô trong 9,5 giờ đầu` | L1 (`Hai mươi phút mất sáu phẩy ba tỷ đô`), L2 (`Sàn Binance bị hack`), L4 (`rút ròng 3,64 tỷ đô trong 9,5 giờ đầu`). |

---

## 4. Cổng chất lượng & Luật kênh đã kiểm

- **Không dùng mục `CHƯA KIỂM`:** Đã loại trừ hoàn toàn mọi chi tiết nằm trong `unverified_chua_kiem` / `unverified_claims_chua_kiem` của cả 2 tệp facts (không nhắc laptop kỹ sư Binance, không dự báo giá iPhone cũ tăng 15–30%, không nêu % sản lượng DRAM OpenAI mua gom, không đoán chi phí USD vệ tinh Suncatcher, nêu rõ là *thử nghiệm của Cornell Tech và Yale*, không nêu số triệu máy Android 12–13 tại VN, không gắn hạn 31/03/2027 cho giá điện, nêu biên độ vênh vàng *từ 14,3 triệu đến hơn 16 triệu đồng tùy cách tính*).
- **Luật riêng kênh CK:** Không nêu tên ngân hàng thương mại, công ty chứng khoán, hãng xe hay mã cổ phiếu; không khuyên mua/bán; cả 4 bài có phép tính minh họa (`ck-thue-xang-0-giam-1804`, `ck-dien-giam-44-dong-20-nam`, `ck-ho-kinh-doanh-giam-30-thue`, `ck-lai-giam-05-tien-gui-80-ngan-han`) đều đọc rõ cụm **"Trong ví dụ giả định..."** ngay trong lời đọc và gắn nhãn `VÍ DỤ GIẢ ĐỊNH` trên `beats`.
- **Từ điển phát âm `say`:** Đã khai báo đầy đủ cách đọc cho toàn bộ tên riêng nước ngoài, từ viết tắt có tiền tố `=`, đơn vị và toàn bộ con số viết bằng chữ số trong `lines` (bao gồm các mẫu chuẩn trong brief: `Binance` → `"Bai-nen-xơ"`, `=FBI` → `"ép bi ai"`, `=TPU` → `"tê pê u"`, `=OTP` → `"ô tê pê"`, `kWh` → `"ki lô oát giờ"`, `E5` → `"e năm"`, `RON` → `"rôn"`).
