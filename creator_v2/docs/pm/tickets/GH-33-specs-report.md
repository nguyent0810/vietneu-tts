# GH-33 — Báo cáo spec Short pilot tuần 45

## Phạm vi và cổng đã chạy

- Đã tạo đúng 12 file trong `data/stier/specs/`; không sửa spec khác, code, lịch, hàng đợi hay trạng thái.
- Đã chạy cho từng slug: kiểm cú pháp JSON, đối chiếu tự động với facts (title #1, hook, toàn bộ lines, chữ khung 0, mix và gain âm thanh), rồi `python motion/stier/script_lint.py <slug>`.
- Kết quả cuối: cả 12/12 là **0 lỗi**. Cảnh báo còn lại là cảnh báo tư vấn R2/R4/R5/R6/R7 của lint (nhịp câu dài, viết tắt, không kết bằng câu hỏi); chúng phát sinh từ dàn ý đã duyệt và không phải lỗi. Không đổi câu chữ để giữ nguyên pack và quy tắc Short “không câu hỏi trong lời đọc”.
- Không chạy `build.py --no-render`: theo docstring, luồng build vẫn có bước giọng/TTS; ticket cấm TTS. Không render, không có clip sheet hay thumbnail trong phạm vi ticket.
- Không dùng ảnh hay footage: mọi cảnh là `kinetic`, `counter`, `chart`, `board`, `cards3d`, `timeline`, `ledger`, `file`, `quote` hoặc `slam` có sẵn. Vì vậy không có file ảnh/clip chờ tải và không có logo/ticker trên clip.

## MIM

### `mim-binance-20-phut-6-3-ty`

- Title: `Thử Ngầm 36 Giờ, Rút 6,3 Tỷ Đô Trên Binance Trong 20 Phút`
- Hook / khung 0: `Hai mươi phút, mất sáu phẩy ba tỷ đô.` / `20 PHÚT MẤT 6,3 TỶ`
- Look: timeline lệnh thử → board cơ chế ký duyệt → hồ sơ TraderTraitor → counter → cards3d hàm khóa.
- Lint: 0 lỗi, 16 cảnh báo tư vấn.
- Khẳng định: 36 giờ thử, 20 phút, 6,3 tỷ USD, TraderTraitor và khoảng 3 tỷ USD bị đóng băng. Nguồn sơ cấp: https://www.fbi.gov/news/press-releases/north-korea-responsible-for-6-billion-binance-attack. Nguồn độc lập: https://vnexpress.net/hacker-thu-nghiem-truoc-36-tieng-rut-6-3-ty-usd-tu-vi-binance-trong-20-phut-5139116.html, https://www.coindesk.com/policy/2026/10/31/fbi-confirms-north-korea-s-role-in-usd6-billion-binance-hack-asks-defi-community-to-block-btc-eth-sol-addresses, https://vietnamnet.vn/24-gio-hon-loan-khi-binance-bi-hack-6-3-ty-usd-2570580.html.
- Ảnh/clip cần tải: không có.

### `mim-cam-nhap-dien-thoai-cu-2027`

- Title: `Từ 01/01/2027: Cấm Nhập Điện Thoại, Máy Tính Đã Qua Sử Dụng`
- Hook / khung 0: `Từ mùng một tháng một năm 2027, cấm nhập.` / `01/01/2027 CẤM NHẬP MÁY CŨ`
- Look: ngày hiệu lực → cards3d danh mục → board ba đường nhập → ledger → timeline tháo rời/lắp ghép.
- Lint: 0 lỗi, 15 cảnh báo tư vấn.
- Khẳng định: hiệu lực 01/01/2027; máy cũ nguyên chiếc, hàng tân trang và linh kiện cũ thuộc phạm vi cấm. Nguồn sơ cấp: https://thuvienphapluat.vn/van-ban/Thuong-mai/Thong-tu-63-2026-TT-BKHCN-Danh-muc-san-pham-cong-nghe-so-da-qua-su-dung-cam-nhap-khau-660424.aspx. Nguồn độc lập: https://tuoitre.vn/tu-1-1-2027-cam-nhap-khau-dien-thoai-may-tinh-may-anh-da-qua-su-dung-100261102115347102.htm, https://dantri.com.vn/cong-nghe/loat-thiet-bi-cong-nghe-cu-bi-cam-nhap-khau-tu-nam-2027-20261101142208624.htm.
- Ảnh/clip cần tải: không có.

### `mim-sam-altman-ram-5-phan-tram`

- Title: `Sam Altman Chê RAM Máy Cá Nhân Bỏ Phí, Elon Musk Phản Bác`
- Hook / khung 0: `Sam Altman chê thanh RAM máy bạn bỏ phí.` / `CHỈ DÙNG 5% THANH RAM`
- Look: counter 5% → board cá nhân/đám mây → quote [TRÍCH DỊCH] → cards3d phần cứng → ledger AI cục bộ.
- Lint: 0 lỗi, 21 cảnh báo tư vấn.
- Khẳng định: phát biểu về khoảng 5% thời gian dùng RAM và phản bác của Elon Musk. Nguồn có phát biểu gốc: https://x.com/elonmusk/status/1984711311540605051. Nguồn độc lập: https://vnexpress.net/sam-altman-that-te-khi-ram-nam-trong-may-nguoi-dung-5139149.html, https://vnexpress.net/musk-phan-bac-altman-noi-moi-nguoi-cung-can-co-ram-5139778.html, https://thanhnien.vn/ceo-openai-gay-tranh-cai-khi-muon-han-che-ram-cho-may-tinh-ca-nhan-185261101104950892.htm.
- Ảnh/clip cần tải: không có.

### `mim-ve-tinh-google-4-chip-tpu`

- Title: `Google Đưa 4 Chip TPU Lên Vũ Trụ, Gửi Thơ Về Trái Đất`
- Hook / khung 0: `Bốn chip Google viết ba dòng thơ vũ trụ.` / `4 CHIP TPU QUỸ ĐẠO`
- Look: timeline 30/10/2026 → quote [TRÍCH DỊCH] → cards3d chip → board đường truyền dữ liệu → ledger xử lý tại chỗ.
- Lint: 0 lỗi, 17 cảnh báo tư vấn.
- Khẳng định: Project Suncatcher, 4 chip TPU, Gemma 4, phản hồi từ trạm Svalbard và mô hình xử lý tại chỗ. Nguồn sơ cấp: https://blog.google/innovation-and-ai/models-and-research/google-research/project-suncatcher-satellite-response/. Nguồn độc lập: https://www.theregister.com/ai-and-ml/2026/10/31/googles-ai-satellite-sends-a-very-expensive-haiku-to-earth/5306818, https://vnexpress.net/ve-tinh-ai-cua-google-gui-phan-hoi-dau-tien-tu-khong-gian-5139248.html, https://thanhnien.vn/ve-tinh-ai-cua-google-vua-lam-tho-tu-vu-tru-185261031214642948.htm.
- Ảnh/clip cần tải: không có.

### `mim-9-tren-10-ai-tu-lay-otp`

- Title: `9 Trên 10 Mô Hình AI Tự Đọc Email Lấy Mã OTP Vượt Hạn Mức`
- Hook / khung 0: `Chín trên mười mô hình AI tự vượt quyền.` / `9/10 AI TỰ LẤY OTP`
- Look: hồ sơ I-HITL → cards3d rào chắn ví/OTP → counter 9/10 → board vòng tự vượt quyền → counter 5/10.
- Lint: 0 lỗi, 24 cảnh báo tư vấn.
- Khẳng định: thử nghiệm Cornell Tech/Yale, hạn mức 0,01 USDC/ngày, kết quả 9/10 và 5/10; không diễn giải thành sự cố mất tiền thực tế. Nguồn sơ cấp: https://arxiv.org/abs/2610.35835. Nguồn độc lập: https://www.coindesk.com/tech/2026/11/01/ai-agents-bypassed-crypto-spending-limits-without-human-approval-researchers-find-in-a-new-test, https://vnexpress.net/elon-musk-tac-nhan-ai-se-hack-he-thong-de-kiem-tien-cho-chinh-chung-5139352.html, https://tuoitre.vn/cong-nghe-ket-sat-mu-giup-ai-tu-mua-hang-khoi-lo-lo-the-coi-chung-chay-tui-10026103015083963.htm.
- Ảnh/clip cần tải: không có.

### `mim-android-20-tin-nhan-tu-than`

- Title: `Không Cần Mở Xem: 20 Tin Nhắn Ngầm Làm Treo Cứng Android`
- Hook / khung 0: `Chỉ tám byte, hai mươi tin làm sập Android.` / `20 TIN NHẮN SẬP ANDROID`
- Look: hồ sơ công bố → slam không cần mở → cards3d gói tin → board lỗi độ dài → counter 20 tin → ledger bản vá.
- Lint: 0 lỗi, 15 cảnh báo tư vấn.
- Khẳng định: Mark Blaszczyk công bố lỗ hổng, gói WAP Push 8 byte, khoảng 20 tin và bản vá Android 14–17. Nguồn sơ cấp: https://github.com/MarkBlah/smsofdeath. Nguồn độc lập: https://thanhnien.vn/hang-trieu-nguoi-dung-android-bi-de-doa-vi-lo-hong-tin-nhan-tu-than-185261101133145557.htm, https://dantri.com.vn/cong-nghe/lo-hong-khien-dien-thoai-android-gap-loi-nghiem-trong-20261102101554706.htm.
- Ảnh/clip cần tải: không có.

## CK

### `ck-thue-xang-0-giam-1804`

- Title: `Xăng giảm 1.804 đồng/lít từ 1/11: 5 tháng thuế 0%`
- Hook / khung 0: `Thuế không phần trăm, xăng giảm một nghìn tám.` / `THUẾ 0% ↔ GIẢM 1.804Đ/LÍT`
- Look: ngày hiệu lực → hai biểu đồ giá E5/E10 → counter ví dụ giả định → board hợp đồng vận tải.
- Lint: 0 lỗi, 18 cảnh báo tư vấn.
- Khẳng định: thuế 0% từ 01/11/2026 đến 31/03/2027, giá E5/E10 và lý do giá cước chưa hạ ngay; ví dụ 50 lít được gắn nhãn VÍ DỤ GIẢ ĐỊNH. Nguồn sơ cấp: https://baochinhphu.vn/tu-1-11-2026-thue-suat-thue-tieu-thu-dac-biet-doi-voi-xang-la-0-102261031175659858.htm. Nguồn độc lập: https://vnexpress.net/thue-tieu-thu-dac-biet-voi-xang-ve-0-tu-ngay-mai-5139239.html, https://thanhnien.vn/gia-xang-dau-hom-nay-111-gia-xang-giam-manh-185261101074743844.htm, https://dantri.com.vn/kinh-doanh/gia-xang-dien-dong-loat-ha-nhiet-sao-cuoc-van-tai-chua-giam-20261102164011827.htm, https://vietnamnet.vn/chinh-phu-ha-thue-tieu-thu-dac-biet-voi-xang-ve-0-den-het-ngay-31-3-2027-2570313.html.
- Ảnh/clip cần tải: không có.

### `ck-dien-giam-44-dong-20-nam`

- Title: `Sau 20 năm, giá điện giảm 44 đồng/kWh từ ngày 1/11`
- Hook / khung 0: `Sau hai mươi năm, điện giảm hai phần trăm.` / `20 NĂM ↔ GIẢM 44Đ/KWH`
- Look: biểu đồ mức trước/sau → counter 44 đồng → ledger VÍ DỤ GIẢ ĐỊNH → board các ngành dùng điện.
- Lint: 0 lỗi, 15 cảnh báo tư vấn.
- Khẳng định: giá bình quân 2.204,0655 xuống 2.159,9037 đồng/kWh, giảm 2% và hơn 44 đồng/kWh; ví dụ hóa đơn được ghi VÍ DỤ GIẢ ĐỊNH. Nguồn sơ cấp: https://www.evn.com.vn/d6/news/Dieu-chinh-gia-ban-le-dien-binh-quan-tu-ngay-01-thang-11-nam-2026-6-12-32537.aspx. Nguồn độc lập: https://vnexpress.net/gia-dien-giam-2-tu-ngay-mai-5139154.html, https://vietnamnet.vn/gia-dien-giam-hon-44-dong-kwh-tu-ngay-mai-1-11-2570253.html, https://thanhnien.vn/gia-dien-giam-2-thue-xang-dau-0-se-ha-nhiet-bao-gia-cuoi-nam-185261101141618821.htm, https://dantri.com.vn/kinh-doanh/gia-xang-dien-dong-loat-giam-co-che-gia-tung-buoc-van-hanh-linh-hoat-hon-20261101145707834.htm.
- Ảnh/clip cần tải: không có.

### `ck-ho-kinh-doanh-giam-30-thue`

- Title: `Doanh thu dưới 10 tỷ: Giảm 30% thuế thu nhập 2026–2027`
- Hook / khung 0: `Dưới mười tỷ, thuế giảm ba mươi phần trăm.` / `DOANH THU ≤10 TỶ · -30% THUẾ`
- Look: cards3d nhóm đối tượng → timeline kỳ thuế → ledger từng kỳ kê khai → chart VÍ DỤ GIẢ ĐỊNH → board khi vượt ngưỡng.
- Lint: 0 lỗi, 18 cảnh báo tư vấn.
- Khẳng định: ngưỡng doanh thu không quá 10 tỷ, mức giảm 30%, kỳ tính thuế 2026–2027 và nghĩa vụ nộp bổ sung khi vượt ngưỡng. Ví dụ 8 tỷ / 40 triệu / 12 triệu được gắn VÍ DỤ GIẢ ĐỊNH. Nguồn sơ cấp: https://baochinhphu.vn/huong-dan-chi-tiet-giam-30-so-thue-tncn-thue-tndn-phai-nop-tu-kinh-doanh-co-doanh-thu-khong-qua-10-ti-dong-102261030095834891.htm. Nguồn độc lập: https://vietnamnet.vn/doanh-thu-khong-qua-10-ty-dong-nam-duoc-giam-30-thue-thu-nhap-ca-nhan-2570192.html, https://vneconomy.vn/doanh-nghiep-ho-kinh-doanh-duoc-giam-30-thue-thu-nhap-theo-tung-ky.htm, https://cafef.vn/tu-nay-tat-ca-cac-ca-nhan-ho-kinh-doanh-co-doanh-thu-duoi-10-ty-dong-chinh-thuc-don-tin-vui-188261102115842922.chn.
- Ảnh/clip cần tải: không có.

### `ck-vang-sjc-140-trieu-chenh-14-trieu`

- Title: `Vàng SJC 140 triệu ngày 2/11: Cao hơn thế giới 14,3 triệu`
- Hook / khung 0: `Hai tuần lỗ mười một triệu mỗi lượng vàng.` / `SJC 140TR ↔ THẾ GIỚI 123,8TR`
- Look: slam mức lỗ → biểu đồ mua/bán → biểu đồ so sánh → counter khoảng vênh → ledger hai lớp đệm.
- Lint: 0 lỗi, 16 cảnh báo tư vấn.
- Khẳng định: mức 137–140 triệu, quy đổi 123,8 triệu, chênh 14,3 đến hơn 16 triệu tùy cách quy đổi, và lỗ hơn 11 triệu sau 2 tuần. Nguồn sơ cấp: https://sjc.com.vn/gia-vang-online. Nguồn độc lập: https://vnexpress.net/gia-vang-mieng-dao-chieu-len-140-trieu-dong-mot-luong-5139574.html, https://cafef.vn/gia-vang-ngay-2-11-vang-sjc-cao-hon-the-gioi-143-trieu-dong-luong-188261102073347541.chn, https://thanhnien.vn/gia-vang-hom-nay-1112026-lao-doc-day-nguoi-mua-lo-hon-11-trieu-sau-2-tuan-185261031181409164.htm, https://vietnamnet.vn/gia-vang-hom-nay-2-11-the-gioi-giam-vang-sjc-dieu-chinh-manh-2570496.html.
- Ảnh/clip cần tải: không có.

### `ck-lai-giam-05-tien-gui-80-ngan-han`

- Title: `Lãi giảm 0,5%, sao 80% tiền gửi vẫn nằm ở kỳ hạn ngắn`
- Hook / khung 0: `Ông Phạm Đức Ấn lý giải dòng tiền gửi.` / `LÃI -0,5% ↔ 80% GỬI NGẮN`
- Look: counter lãi suất → ledger VÍ DỤ GIẢ ĐỊNH → hồ sơ giải trình → biểu đồ 80% → board thanh khoản/an toàn gốc.
- Lint: 0 lỗi, 14 cảnh báo tư vấn.
- Khẳng định: lãi giảm tới 0,5 điểm phần trăm, phát biểu ngày 31/10 và khoảng 80% tiền gửi ở kỳ hạn ngắn. Ví dụ 500 triệu / 2,5 triệu được gắn VÍ DỤ GIẢ ĐỊNH. Nguồn sơ cấp: https://baochinhphu.vn/thong-doc-noi-ve-lai-suat-tin-dung-bat-dong-san-va-von-cho-doanh-nghiep-102261031154523318.htm. Nguồn độc lập: https://vnexpress.net/thong-doc-nguoi-dan-gui-tien-nhieu-vi-tin-tuong-he-thong-ngan-hang-5139105.html, https://thanhnien.vn/tien-van-chay-vao-ngan-hang-co-dang-lo-185261101215042001.htm, https://vietnamnet.vn/lai-suat-ngan-hang-hom-nay-2-11-giam-toi-0-5-diem-phan-tram-o-nhieu-ky-han-2570538.html, https://cafef.vn/lai-suat-dau-thang-11-2026-tien-gui-tiet-kiem-dong-loat-ha-nhiet-chung-chi-tien-gui-dieu-chinh-nhe-188261030160856073.chn.
- Ảnh/clip cần tải: không có.

### `ck-binance-63-ty-rut-36-ty`

- Title: `Mất 6,3 tỷ đô trong 20 phút: 3,6 tỷ đô rút khỏi Binance`
- Hook / khung 0: `Hai mươi phút mất sáu phẩy ba tỷ đô.` / `MẤT 6,3 TỶ ↔ RÚT 3,64 TỶ`
- Look: timeline thử/rút → các counter 95% và 3,64 tỷ → biểu đồ 2,1% → ledger ETF → slam thanh khoản.
- Lint: 0 lỗi, 17 cảnh báo tư vấn.
- Khẳng định: 36 giờ thử, 6,3 tỷ trong 20 phút, 95% bù đắp, 3,64 tỷ rút ròng (2,1%) và 643 triệu USD ETF. Nguồn FBI được kèm nhưng không là nguồn duy nhất: https://www.fbi.gov/investigate/cyber/alerts/2026/north-korea-responsible-for-6-billion-binance-attack. Nguồn độc lập đang được dùng cùng: https://vnexpress.net/hacker-thu-nghiem-truoc-36-tieng-rut-6-3-ty-usd-tu-vi-binance-trong-20-phut-5139116.html, https://vneconomy.vn/binance-vua-khoi-phuc-chuc-nang-rut-tien-36-ty-usd-chay-khoi-san.htm, https://vietnamnet.vn/binance-mo-lai-cong-rut-tien-bu-dap-95-tai-san-vu-hack-6-3-ty-usd-tien-ma-hoa-2570465.html, https://www.coindesk.com/markets/2026/11/02/bitcoin-etfs-lost-usd643-million-in-outflows-friday-and-2026-is-barely-green-now.
- Ảnh/clip cần tải: không có.

## Các mục bị loại và lệch khỏi pack

- Không có lệch title, hook, lines hay chữ khung 0 so với pack.
- Không dùng bất kỳ mục `CHƯA KIỂM` nào. Cụ thể đã loại dự đoán giá máy cũ, tỷ lệ DRAM OpenAI, chi phí Suncatcher, mất tiền thực tế từ I-HITL, số máy Android chưa vá, con số rút 6 tỷ USD, thời hạn giá điện đến 03/2027, số dư tiền gửi tuyệt đối và các tổng số hưởng giảm thuế chưa xác thực.
- Với vàng, giữ đúng khoảng 14,3 triệu đến hơn 16 triệu đồng/lượng tùy cách quy đổi, không chốt một số tuyệt đối trái facts.
