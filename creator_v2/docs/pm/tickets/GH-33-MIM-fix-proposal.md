# GH-33 MIM: đề xuất sửa lời đọc / scene / title / description (4 Short)

Ghi chú phương pháp: WebFetch trả về bản tóm tắt do model nhỏ trích, nên các "trích dẫn" dưới đây là câu nguyên văn mà công cụ trả lại; những chỗ ghi (diễn giải) là công cụ chỉ tóm ý, cần mắt người đọc lại trước khi publish. Không truy cập được: fbi.gov (ENOTFOUND), thuvienphapluat.vn (HTTP 403), x.com tweet (HTTP 402). Nguồn bổ sung ngoài spec (tìm qua WebSearch, mở được): Wikipedia "2026 Binance hack", Al Jazeera 30/10, CNBC 30/10.

Quy ước: [OK] có nguồn; [DIỄN GIẢI] có nguồn nhưng là tóm ý; [KHÔNG NGUỒN] không tìm thấy, phải bỏ/thay.

---

## mim-binance-20-phut-6-3-ty

### Bảng claim

| Claim | Trạng thái | Trích dẫn / ghi chú | URL |
|---|---|---|---|
| ~20 phút | [OK] | "Dữ liệu blockchain chỉ ra, phần lớn số tiền bị rút trong khoảng 20 phút" | vnexpress.net/...5139116 |
| 6,3 tỷ USD | [OK] nguồn là Binance | "Binance xác nhận vụ tấn công ảnh hưởng đến khoảng 6,3 tỷ USD." (TRM: ~6,36 tỷ) | vnexpress 5139116; CNBC |
| 10 chuỗi | [OK] nguồn TRM | "An attacker moved approximately 6.36 billion USD out of Binance wallets on 10 blockchains." (TRM, qua Al Jazeera). VnExpress chỉ nêu 6 mạng, VietNamNet/CoinDesk không nêu | aljazeera.com/news/2026/10/30/binance-says-6-3bn-stolen-... ; en.wikipedia.org/wiki/2026_Binance_hack |
| 29/10/2026 | [OK] | Wikipedia: "On 29 October 2026, US$6.3 billion worth of digital currency was stolen from Binance" ; VnExpress "ngày 29/10 theo múi giờ UTC" | wikipedia; vnexpress |
| 20:05 UTC | [OK] | "Từ 20h05 đến 20h09 ngày 29/10 theo múi giờ UTC" (đợt đầu trên XRP Ledger); CNBC/TRM: 20:05 đến 20:20 UTC | vnexpress; wikipedia |
| 36 giờ | [OK] nguồn TRM | "Quá trình chuẩn bị bắt đầu ít nhất 36 tiếng trước khi vụ hack xảy ra", TRM Labs nói. | vnexpress 5139116 |
| lệnh thử | [OK] | "ví của bên tấn công đã nhận 3 khoản tiền rút nhỏ trong giai đoạn thử nghiệm sáng 28/10" | vnexpress 5139116 |
| "ngầm" chạy lệnh thử | [KHÔNG NGUỒN] (từ "ngầm") | bài chỉ nói "thử nghiệm", bỏ "ngầm" | |
| ví nóng | [OK] | "Bốn giờ sau, đoạn mã được cài đặt trên một ví nóng của Binance" | vnexpress 5139116 |
| "dò cơ chế ký duyệt tự động" | [KHÔNG NGUỒN] | nguồn: "tin tặc xâm nhập 'hạ tầng ký kết' của Binance" và "hệ thống có chức năng phê duyệt giao dịch". Không có chuyện "dò" | vnexpress 5139116 |
| FBI quy trách nhiệm Triều Tiên | [OK] | tiêu đề cảnh báo FBI 31/10: "North Korea Responsible for $6 Billion+ Binance Attack" (qua Wikipedia; fbi.gov không mở được) | wikipedia |
| FBI xác nhận TraderTraitor | [OK] (diễn giải) | CoinDesk: FBI xác nhận vai trò Triều Tiên/TraderTraitor; VietNamNet: "FBI sau đó xác nhận những phát hiện này" (phát hiện của Chainalysis/TRM về TraderTraitor) | coindesk.com/...; vietnamnet.vn/...2570580 |
| FBI nói số tiền | Chỉ "hơn 6 tỷ" | CoinDesk: "the theft of over $6 billion from Binance". FBI KHÔNG nêu 6,3 hay 3,0. Bỏ "THEO FBI" khỏi bảng | coindesk |
| ~3 tỷ bị đóng băng | [OK] nguồn Binance | CNBC: Binance estimates "around $3 billion worth of cryptocurrency has been frozen so far"; TRM ~2,7 tỷ, Chainalysis ~2,8 tỷ (Wikipedia chú thích); VietNamNet: Tether và Circle đóng băng "tổng giá trị hơn 2 tỷ USD" | cnbc.com/2026/10/30/binance-hack-stolen-crypto-recovery.html; vietnamnet; wikipedia |
| "gần nửa" | [OK] suy ra | 3/6,3 = 48% theo ước tính Binance. Nếu dùng số TRM (2,7) thì ~43%: giữ cách nói "Binance ước tính" | |
| "tiền chết" / "con số chết" | [KHÔNG NGUỒN] (tu từ) | thay bằng "bị đóng băng" | |
| hàm từ xa / FREEZE / HỢP ĐỒNG THÔNG MINH | [KHÔNG NGUỒN] | CNBC: nói rõ không giải thích cơ chế; Wikipedia: không có "smart contract freeze function". Chỉ có: Tether và Circle "moved to freeze the funds" | cnbc; wikipedia |
| 2,4 tỷ nằm ngoài tầm đóng băng | [OK] | "theo TRM Labs, khoảng 2,4 tỷ USD tiền mã hóa đã nằm ngoài khả năng kiểm soát của các đơn vị phát hành." | vietnamnet |
| đổi sang BTC/ETH thì không đóng băng được | [OK] | CNBC: once stablecoins are swapped into assets like bitcoin or ether, "it's not possible to freeze the assets"; TRM: bán USDT, vay ether | cnbc |

### title mới
```
Binance Mất 6,3 Tỷ Đô Trong 20 Phút, Gần Nửa Bị Đóng Băng
```

### lines mới (đủ 8 dòng; dòng 0, 1, 4 giữ nguyên)
```json
[
  "Hai mươi phút, mất sáu phẩy ba tỷ đô.",
  "Ngày 29 tháng 10 năm 2026, sàn Binance bị hack rút tiền trên mười chuỗi khối.",
  "Theo TRM Labs, tin tặc chuẩn bị từ ít nhất ba mươi sáu giờ trước, gồm cả lệnh rút thử.",
  "Chúng xâm nhập hạ tầng ký kết của Binance, cài mã lên một ví nóng rồi rút tiền.",
  "Cơ quan FBI xác nhận thủ phạm là nhóm tin tặc Triều Tiên tên TraderTraitor.",
  "Nhưng Binance ước tính gần nửa, khoảng ba tỷ đô, đã bị đóng băng.",
  "Tether và Circle, hai nhà phát hành stablecoin, đã đóng băng hơn hai tỷ đô.",
  "Bài học: tiền đã đổi sang ether hay bitcoin thì không ai đóng băng được nữa."
]
```
Lưu ý "mười chuỗi khối" ở dòng 1: chỉ TRM nêu 10; nếu muốn chặt hơn đổi thành "Theo TRM Labs, trên mười chuỗi khối" (không bắt buộc, vì scene1 giữ keyword "mười").

### scene cần đổi (JSON đầy đủ; các scene khác giữ nguyên)
Scene 1 (timeline, chỉ đổi text mốc 20:05):
```json
{"type":"timeline","at":1,"items":[{"year":"29/10/2026","text":"sàn Binance bị hack","at":1},{"year":"20:05 UTC","text":"bắt đầu rút tiền","at":[1,"rút"]},{"year":"10 CHUỖI","text":"khối bị rút tiền","at":[1,"mười"]}]}
```
Scene 2 (bỏ "NGẦM", keyword mới "thử"):
```json
{"type":"kinetic","at":2,"items":[{"text":"TRƯỚC ĐÓ 36 GIỜ","at":2,"acc":true},{"text":"THEO TRM LABS · CÓ LỆNH RÚT THỬ","at":[2,"thử"],"sm":true}],"clip":"pexels:5377697","veil":0.6}
```
Scene 3 (board, bỏ "dò ký duyệt"/"xả"):
```json
{"type":"board","at":3,"title":"CÁCH TẤN CÔNG","nodes":[{"text":"XÂM NHẬP HẠ TẦNG KÝ KẾT","x":0.5,"y":0.27,"at":[3,"ký"],"shape":"box","w":720},{"text":"CÀI MÃ LÊN VÍ NÓNG","x":0.5,"y":0.5,"at":[3,"cài"],"shape":"box","w":700},{"text":"RÚT TIỀN","x":0.5,"y":0.8,"at":[3,"rút"],"shape":"box","w":640,"c":"acc"}],"arrows":[{"from":0,"to":1,"at":[3,"cài"]},{"from":1,"to":2,"at":[3,"rút"]}]}
```
Scene 4 (table: bỏ "THEO FBI", ghi đúng nguồn từng số):
```json
{"type":"table","at":4,"title":"BINANCE · TỶ ĐÔ","rowHead":"SỐ LIỆU","colHead":"ĐÔ LA MỸ · BINANCE / FBI","cols":["SỐ","NGUỒN"],"rows":[{"k":"BỊ RÚT","v":["6,3 TỶ","BINANCE"]},{"k":"ĐÓNG BĂNG","v":["~3,0 TỶ","BINANCE ƯỚC TÍNH"]},{"k":"THỦ PHẠM","v":["NHÓM","TRADERTRAITOR"],"at":[4,"nhóm"]}],"hl":[{"r":2,"at":[4,"nhóm"]}]}
```
Scene 5 (bỏ "THÀNH TIỀN CHẾT"):
```json
{"type":"kinetic","at":5,"items":[{"text":"GẦN NỬA SỐ TIỀN","at":5,"acc":true},{"text":"BỊ ĐÓNG BĂNG","at":[5,"đóng"]}],"clip":"pexels:5377991","veil":0.6}
```
Scene 6 (bỏ "hàm khóa/hợp đồng thông minh/FREEZE"):
```json
{"type":"cards3d","at":6,"title":"ĐÓNG BĂNG STABLECOIN","cards":[{"k":"NHÀ PHÁT HÀNH","v":"TETHER · CIRCLE","at":[6,"Tether"]},{"k":"ĐÃ ĐÓNG BĂNG","v":"HƠN 2 TỶ ĐÔ","at":[6,"đóng"],"c":"acc"}]}
```
Scene 7:
```json
{"type":"kinetic","at":7,"items":[{"text":"ĐỔI SANG ETHER","at":[7,"ether"]},{"text":"KHÔNG AI KHÓA ĐƯỢC","at":[7,"không"],"acc":true}]}
```
Cũng nên cập nhật `acc` top-level thành ["hai mươi","sáu","ba","đóng băng"] (cũ có "khóa" không còn trong lời).

### description (thay đoạn đầu; đoạn 2 giữ)
```
Binance xác nhận bị tấn công với khoảng 6,3 tỷ USD bị rút vào ngày 29/10/2026; theo TRM Labs, tiền bị rút khỏi ví trên 10 chuỗi khối, phần lớn trong khoảng 20 phút, và việc chuẩn bị bắt đầu ít nhất 36 giờ trước đó. FBI xác nhận Triều Tiên chịu trách nhiệm, nhóm TraderTraitor. Binance ước tính khoảng 3 tỷ USD đã bị đóng băng, trong đó Tether và Circle đóng băng hơn 2 tỷ USD stablecoin; phần đã đổi sang ether hoặc bitcoin thì không đóng băng được. Giọng đọc tổng hợp từ nguồn công khai.
```
Thêm vào `sources` của spec: CNBC (https://www.cnbc.com/2026/10/30/binance-hack-stolen-crypto-recovery.html), Al Jazeera (https://www.aljazeera.com/news/2026/10/30/binance-says-6-3bn-stolen-in-biggest-crypto-heist-in-history-what-we-know).

### say cần thêm
```json
{"Tether":"Tê-thơ","Circle":"Sơ-cồ","stablecoin":"xtây-bồ-coin","ether":"i-thơ","bitcoin":"bít-coin"}
```
(giữ các say cũ; "TRM Labs" cũ vẫn dùng được.) Tags: bỏ "hợp đồng thông minh", "đóng băng 3 tỷ USD" nên giữ vì Binance ước tính.

---

## mim-cam-nhap-dien-thoai-cu-2027

### Bảng claim

| Claim | Trạng thái | Trích dẫn / ghi chú | URL |
|---|---|---|---|
| Thông tư 63/2026/TT-BKHCN, ban hành 27/10 | [OK] | Dân Trí: "có hiệu lực từ ngày 1/1/2027" (Thông tư 63/2026/TT-BKHCN, ban hành ngày 27/10) | dantri.com.vn/...20261101142208624.htm |
| Hiệu lực 01/01/2027 | [OK] | Tuổi Trẻ: "có hiệu lực từ ngày 1-1-2027." | tuoitre.vn/...100261102115347102.htm |
| Cấm điện thoại, máy tính, máy ảnh đã qua sử dụng | [OK] | Tuổi Trẻ: "các thiết bị thuộc diện cấm nhập khẩu khi đã qua sử dụng"; Dân Trí còn nêu thiết bị âm thanh, màn hình | tuoitre; dantri |
| Mã HS 8517, 8471, 8525 | [OK] (mã), [DIỄN GIẢI] (gán tên) | Dân Trí: Thông tư "công bố danh mục theo hệ thống mã HS hiện hành", các nhóm nêu gồm 8517, 8471, 8470, 8525 và 8518. Báo chỉ liệt kê mã; tên nhóm (8517 điện thoại, 8471 máy tính, 8525 máy ảnh) là danh pháp HS chuẩn, không nằm trong trích dẫn | dantri |
| Mã 4 số cấm cả mã 8 số | [OK] | Tuổi Trẻ: "lệnh cấm áp dụng cho toàn bộ mã HS 8 chữ số thuộc nhóm đó" | tuoitre |
| Tân trang vẫn bị cấm | [OK] | Tuổi Trẻ: tân trang "vẫn bị cấm nhập khẩu nếu có mã HS thuộc danh mục"; Dân Trí: "việc được tân trang không đồng nghĩa thiết bị được phép nhập khẩu." | tuoitre; dantri |
| "sửa chữa lại như máy mới" | [KHÔNG NGUỒN] | định nghĩa tân trang trong facts không có trong nguồn đọc được | |
| Bộ phận, phụ kiện, cụm linh kiện bị cấm | [OK] | "áp dụng đối với bộ phận, phụ kiện, cụm linh kiện" và "linh kiện điện tử đã qua sử dụng của những sản phẩm thuộc danh mục" (chỉ những cái thuộc danh mục) | tuoitre; dantri |
| "chặn chiêu tháo rời rồi lắp lại" | [KHÔNG NGUỒN] | Tuổi Trẻ và Dân Trí đều không nhắc tháo rời/lắp ráp; Tuổi Trẻ còn nói không nêu lý do ban hành. Bỏ cả line5 và scene5 | |
| "hàng dựng từ linh kiện dần vắng bóng" | [KHÔNG NGUỒN] (suy diễn) | bỏ | |
| "ba cửa hải quan" | [KHÔNG NGUỒN] | không nguồn nào dùng; "3 nhóm" chỉ là cách chia của spec. Bỏ cụm "ba cửa hải quan" | |
| Ngoại lệ máy in/photocopy, dây chuyền, máy móc sản xuất hoặc nghiên cứu | [OK] | Dân Trí: "không phải mọi thiết bị công nghệ cũ đều bị cấm trong mọi trường hợp" (ngoại lệ gồm một số máy in, máy photocopy, dây chuyền, máy móc phục vụ sản xuất hoặc nghiên cứu); Tuổi Trẻ: "thiết bị phục vụ trực tiếp dự án đầu tư sản xuất, đóng gói, kiểm thử vi mạch bán dẫn" | dantri; tuoitre |
| Hàng đã được cấp phép trước 2027 vẫn theo giấy phép cũ | [DIỄN GIẢI] | Tuổi Trẻ (tóm ý); chưa dùng trong lời đọc | tuoitre |

Văn bản gốc (thuvienphapluat) trả 403, nên chưa đối chiếu Điều khoản trực tiếp; mọi điều trên dựa vào Tuổi Trẻ và Dân Trí. Nên mở bản PDF Thông tư để kiểm tra danh mục mã chi tiết trước khi publish nếu muốn đưa thêm mã.

### title: giữ nguyên
```
Cấm Nhập Điện Thoại Cũ 01/01/2027: Khóa Cả Hàng Tân Trang
```

### lines mới (đủ 8; dòng 0, 1, 2 giữ nguyên)
```json
[
  "Từ mùng một tháng một năm 2027, cấm nhập.",
  "Thông tư 63 năm 2026 cấm nhập khẩu điện thoại, máy tính và máy ảnh cũ.",
  "Quy định của Bộ Khoa học và Công nghệ không chỉ chặn máy cũ nguyên chiếc.",
  "Hàng tân trang cũng không thoát: vẫn bị cấm nếu mã HS nằm trong danh mục.",
  "Các bộ phận, phụ kiện, cụm linh kiện cũ thuộc danh mục cũng bị cấm nhập.",
  "Nhưng có ngoại lệ: dây chuyền, máy móc cũ phục vụ sản xuất hoặc nghiên cứu.",
  "Danh mục lập theo mã HS: cấm cả mã tám chữ số thuộc nhóm bốn chữ số.",
  "Trước khi mua máy cũ về, bạn hãy tra mã HS và xem có ngoại lệ không."
]
```
Dòng 7 là lời khuyên (không gán sự kiện); kết bằng khẳng định mệnh lệnh, dấu "." không phải câu hỏi (cụm "có ngoại lệ không" nằm trong câu mệnh lệnh; nếu preflight bắt "không." cuối câu thì đổi thành "...hãy tra mã HS và đọc kỹ phần ngoại lệ.").

### scene cần đổi
Scene 3:
```json
{"type":"kinetic","at":3,"items":[{"text":"KHÔNG THOÁT","at":3},{"text":"HÀNG TÂN TRANG","at":[3,"tân"],"acc":true},{"text":"VẪN CẤM NẾU TRÚNG MÃ HS","at":[3,"mã"],"sm":true}],"clip":"pexels:6755162","veil":0.6}
```
Scene 4 (đổi "cụm linh kiện" thành "thuộc danh mục"; keyword bộ/phụ/cụm vẫn có trong lời mới, board giữ nguyên, chỉ đổi nhãn nút acc):
```json
{"type":"board","at":4,"title":"CẤM NHẬP","nodes":[{"text":"BỘ PHẬN","x":0.25,"y":0.27,"at":[4,"bộ"],"shape":"box","w":360},{"text":"PHỤ KIỆN","x":0.75,"y":0.27,"at":[4,"phụ"],"shape":"box","w":360},{"text":"CỤM LINH KIỆN CŨ THUỘC DANH MỤC","x":0.5,"y":0.7,"at":[4,"cụm"],"shape":"box","w":760,"c":"acc"}],"arrows":[{"from":0,"to":2,"at":[4,"cụm"]},{"from":1,"to":2,"at":[4,"cụm"]}]}
```
Scene 5 (thay hẳn, vẫn là kinetic có clip cũ):
```json
{"type":"kinetic","at":5,"items":[{"text":"CÓ NGOẠI LỆ","at":5,"acc":true},{"text":"MÁY MÓC SẢN XUẤT, NGHIÊN CỨU","at":[5,"sản"],"sm":true}],"clip":"pexels:6755168","veil":0.6}
```
Scene 6 (thay bảng "trước/sau" không nguồn bằng bảng mã HS):
```json
{"type":"table","at":6,"title":"MÃ HS · PHẠM VI CẤM","rowHead":"NHÓM HÀNG","colHead":"THEO DÂN TRÍ · TUỔI TRẺ","cols":["MÃ 4 SỐ","PHẠM VI CẤM"],"rows":[{"k":"ĐIỆN THOẠI","v":["8517","CẢ MÃ 8 SỐ"]},{"k":"MÁY TÍNH","v":["8471","CẢ MÃ 8 SỐ"]},{"k":"MÁY ẢNH","v":["8525","CẢ MÃ 8 SỐ"]}],"hl":[{"r":1,"at":[6,"bốn"]}]}
```
Scene 7:
```json
{"type":"kinetic","at":7,"items":[{"text":"TRA MÃ HS TRƯỚC","at":[7,"tra"],"acc":true},{"text":"XEM NGOẠI LỆ","at":[7,"ngoại"],"sm":true}]}
```
Scene 1 (ledger HS) và scene 2 (3 nhóm) giữ nguyên (đã có nguồn). Cập nhật `acc` top-level: ["một","cấm","cũ","tân trang"] vẫn đúng.

### description (thay đoạn đầu)
```
Từ ngày 01/01/2027, Thông tư 63/2026/TT-BKHCN của Bộ Khoa học và Công nghệ cấm nhập khẩu điện thoại, máy tính, máy ảnh và một số thiết bị công nghệ số đã qua sử dụng thuộc danh mục mã HS. Hàng tân trang vẫn bị cấm nếu có mã HS thuộc danh mục; bộ phận, phụ kiện, cụm linh kiện cũ thuộc danh mục cũng bị cấm. Có ngoại lệ cho một số dây chuyền, máy móc đã qua sử dụng phục vụ sản xuất, nghiên cứu. Giọng đọc tổng hợp từ nguồn công khai.
```

### say cần thêm
```json
{"HS":"hát ét"}
```
(thêm "=HS": "hát ét" để đọc viết tắt; số 8517 viết trên hình, không đọc.) Đổi cách nói "bốn chữ số", "tám chữ số" đã là chữ.

---

## mim-sam-altman-ram-5-phan-tram (nặng nhất)

### Bảng claim

| Claim | Trạng thái | Trích dẫn / ghi chú | URL |
|---|---|---|---|
| Altman nói trên Cheeky Pint (phát 30/10) | [OK] | VnExpress: phỏng vấn kênh YouTube Cheeky Pint, đăng 30/10 | vnexpress.net/sam-altman-that-te-khi-ram-nam-trong-may-nguoi-dung-5139149.html |
| Tiêu đề "thật tệ khi RAM nằm trong máy người dùng" | [OK] | VnExpress (tiêu đề + slug "that-te") | vnexpress 5139149 |
| RAM máy cá nhân chỉ được dùng 5% thời gian | [OK] | "thật tệ khi nguồn cung RAM hạn chế lại nằm trong máy tính của mọi người và chỉ được dùng trong 5% thời gian hoạt động." (VnExpress đặt trong ngoặc kép) | vnexpress 5139149 |
| Nên tối đa hóa điện toán đám mây | [OK] | Thanh Niên: "Nếu bạn muốn sử dụng tài nguyên hiệu quả trong môi trường cung cấp cực kỳ hạn chế này"; "bạn nên tối đa hóa việc sử dụng điện toán đám mây". VnExpress: "Chúng ta cần tận dụng tối đa tài nguyên trên đám mây." | thanhnien.vn/...185261101104950892.htm; vnexpress 5139149 |
| Altman "muốn gom chip nhớ về trung tâm dữ liệu" | [KHÔNG NGUỒN] như lời Altman | Thanh Niên/VnExpress: ông nói về hiệu quả sử dụng; "trung tâm dữ liệu chạy 24/7" là lập luận; việc "gom"/"hút" là diễn giải. Bỏ | |
| Data center chạy 24/7 | [DIỄN GIẢI] | Thanh Niên (tóm): trung tâm dữ liệu chạy 24/7 dùng bộ nhớ hiệu quả hơn PC | thanhnien |
| Altman nói gì về "cơn khát chip nhớ" | [KHÔNG NGUỒN] như lời Altman | bỏ gán cho Altman | |
| Altman nói về chạy AI tại chỗ giữ kín dữ liệu | [KHÔNG NGUỒN] | Altman chỉ nói: "Rất nhiều người muốn dùng tính năng suy luận cục bộ." Không có "giữ kín dữ liệu" | vnexpress 5139149 |
| "không phí thuê bao" | [KHÔNG NGUỒN] | Tom's Hardware (qua VnExpress): "khả năng chạy suy luận cục bộ đồng nghĩa người dùng sẽ trả ít tiền hơn cho những mô hình như GPT-6 Luna." Đây là nhận định của báo, không phải của Altman | vnexpress 5139149 |
| Musk đăng trên X "Mọi người cũng xứng đáng sở hữu RAM" | [OK] | "Ngày 2/11, Musk đăng trên X thông điệp 'Mọi người cũng xứng đáng sở hữu RAM'" kèm meme Christoph Waltz: "Các người đang giữ lại DRAM của điện toán đám mây, phải không?" | vnexpress.net/musk-phan-bac-altman-noi-moi-nguoi-cung-can-co-ram-5139778.html |
| Ngày Musk đăng | SAI trong spec | spec ghi 01/11/2026; VnExpress ghi 2/11. Sửa thành 02/11/2026 | vnexpress 5139778 |
| URL tweet x.com/elonmusk/status/1984711311540605051 | SAI | Snowflake ID giải mã ra 2025-11-01 19:57 UTC, tức một năm trước. Không phải tweet 2/11/2026. Bỏ khỏi sources; VnExpress không dẫn link tweet | tính từ ID |
| Musk phản bác / đáp trả Altman | [DIỄN GIẢI] | VnExpress: meme "được cho là" đáp trả quan điểm Altman. Altman không phản hồi Musk | vnexpress 5139778 |
| Giá RAM tăng mạnh do cơn sốt trung tâm dữ liệu AI | [OK] nguồn Gadgets Now | VnExpress (dẫn Gadgets Now): bình luận của Musk "trong bối cảnh giá RAM tăng mạnh do cơn sốt trung tâm dữ liệu AI" | vnexpress 5139778 |
| The Verge: tiền tỷ đô đặt mua RAM làm thiết bị đắt | [OK] (tóm ý) | "Hàng tỷ USD được các hãng bỏ ra để đặt hàng RAM là lý do mà máy tính, điện thoại và nhiều công nghệ khác ngày càng trở nên đắt đỏ." | vnexpress 5139149 |
| Chuyên gia: thiếu chip nhớ đến ít nhất 2028 | [DIỄN GIẢI] | VnExpress (tóm) - chưa dùng | vnexpress 5139149 |
| Ảnh Altman CC BY | Có dùng | credits.json trong output/stier/mim-sam-altman-ram-5-phan-tram/ liệt kê ảnh "Sam Altman" by Village Global, CC BY 2.0, qua Wikimedia Commons; spec.imgs.sam_altman có khai báo | credits.json |

Lưu ý lập luận: Altman nói về hiệu quả sử dụng trong bối cảnh khan hiếm; ý "ảnh hưởng đến mô hình thuê bao/OpenAI" là phân tích của báo (Thanh Niên, Tom's Hardware), không được nói thành lời của ông.

### title mới
```
Sam Altman: Thật Tệ Khi RAM Nằm Trong Máy Bạn, Musk Phản Bác
```
(bỏ "Chê"; "Phản Bác" là chữ trong tiêu đề VnExpress.)

### lines mới (đủ 8; dòng 1 giữ nguyên)
```json
[
  "Sam Altman nói thật tệ khi RAM nằm trong máy của bạn.",
  "Trên Cheeky Pint, ông nói thanh RAM máy cá nhân chỉ dùng năm phần trăm thời gian.",
  "Ông nói nên tối đa hóa điện toán đám mây khi nguồn cung hạn chế.",
  "Ngày hai tháng mười một, Elon Musk đăng trên X: mọi người cũng xứng đáng sở hữu RAM.",
  "Theo Gadgets Now, giá RAM đang tăng mạnh vì cơn sốt trung tâm dữ liệu AI.",
  "Tom's Hardware nhận định: chạy AI cục bộ nghĩa là bạn trả ít tiền hơn cho mô hình.",
  "The Verge viết: hàng tỷ đô đặt mua RAM khiến máy tính và điện thoại đắt dần.",
  "Altman ưu tiên đám mây, còn Musk đứng về phía người dùng có RAM riêng."
]
```
Dòng 0 là câu tóm theo tiêu đề VnExpress ("thật tệ khi RAM nằm trong máy người dùng"), không dùng từ "chê".

### scene cần đổi
Scene 2 (bỏ "HÚT VỀ", "chip nhớ về trung tâm dữ liệu"):
```json
{"type":"board","at":2,"title":"ALTMAN NÓI GÌ","nodes":[{"text":"NGUỒN CUNG HẠN CHẾ","x":0.5,"y":0.27,"at":[2,"hạn"],"shape":"box","w":720},{"text":"TỐI ĐA HÓA","x":0.5,"y":0.5,"at":[2,"tối"],"shape":"box","w":560},{"text":"ĐIỆN TOÁN ĐÁM MÂY","x":0.5,"y":0.8,"at":[2,"đám"],"shape":"box","w":720,"c":"acc"}],"arrows":[{"from":0,"to":1,"at":[2,"tối"]},{"from":1,"to":2,"at":[2,"đám"]}]}
```
Scene 3 (sửa ngày 01/11 thành 02/11; câu quote đúng dịch VnExpress, bỏ dấu "!"):
```json
{"type":"quote","at":3,"text":"Mọi người cũng xứng đáng sở hữu RAM","by":"ELON MUSK · MẠNG X · 02/11/2026 · TRÍCH DỊCH"}
```
Scene 4 (đổi chữ "siêu máy chủ AI" thành điều báo nói):
```json
{"type":"kinetic","at":4,"items":[{"text":"GIÁ RAM TĂNG MẠNH","at":4,"acc":true},{"text":"CƠN SỐT TRUNG TÂM DỮ LIỆU AI","at":[4,"sốt"],"sm":true}],"clip":"pexels:6755168","veil":0.6}
```
Scene 5:
```json
{"type":"cards3d","at":5,"title":"TOM'S HARDWARE NHẬN ĐỊNH","cards":[{"k":"CHẠY AI CỤC BỘ","v":"TRẢ ÍT TIỀN HƠN","at":[5,"cục"]},{"k":"NHẬN ĐỊNH CỦA","v":"TOM'S HARDWARE","at":[5,"Tom"],"c":"acc"}]}
```
Scene 6:
```json
{"type":"ledger","at":6,"title":"THE VERGE VIẾT","rows":[{"k":"HÀNG TỶ ĐÔ","v":"ĐẶT MUA RAM","at":[6,"tỷ"]},{"k":"MÁY TÍNH, ĐIỆN THOẠI","v":"ĐẮT DẦN","at":[6,"đắt"]}]}
```
Scene 7:
```json
{"type":"board","at":7,"title":"HAI QUAN ĐIỂM","nodes":[{"text":"ALTMAN: TỐI ĐA HÓA ĐÁM MÂY","x":0.5,"y":0.27,"at":[7,"đám"],"shape":"box","w":760},{"text":"MUSK: NGƯỜI DÙNG ĐÁNG CÓ RAM","x":0.5,"y":0.7,"at":[7,"Musk"],"shape":"box","w":760,"c":"acc"}]}
```
Scene 0 và scene 1 giữ nguyên (scene 1 "≈5%" và "24/7" dựa vào Altman/Thanh Niên; chấp nhận). `acc` top-level đổi thành ["Altman","RAM","năm","bạn"] hoặc giữ nguyên (các từ vẫn có trong lời).

Sources trong spec: bỏ URL x.com (sai ngày); thêm nếu muốn: Thanh Niên (đã có).

### description (thay đoạn đầu)
```
Trên chương trình Cheeky Pint (đăng 30/10/2026), Sam Altman nói thật tệ khi nguồn cung RAM hạn chế lại nằm trong máy tính của mọi người và chỉ được dùng khoảng 5% thời gian hoạt động, và nên tối đa hóa điện toán đám mây. Ngày 02/11/2026, Elon Musk đăng trên mạng X: "Mọi người cũng xứng đáng sở hữu RAM". Theo Gadgets Now, giá RAM đang tăng mạnh do cơn sốt trung tâm dữ liệu AI. Giọng đọc tổng hợp từ nguồn công khai.

Ảnh: "Sam Altman" by Village Global, CC BY 2.0, qua Wikimedia Commons (https://commons.wikimedia.org/wiki/File%3A%E2%80%9CSam_Altman%E2%80%9D_by_Village_Global.jpg).
```
(description cũ không có dòng ghi công ảnh CC BY; cần thêm để đúng giấy phép. Kiểm lại ảnh có thật được dùng trong scene/video, hiện credits.json liệt kê.)

### say cần thêm
```json
{"Gadgets Now":"Ga-chéc Nao","Tom's Hardware":"Tom Hát-quây","The Verge":"Đờ Vớ-ch"}
```

---

## mim-ve-tinh-google-4-chip-tpu

### Bảng claim

| Claim | Trạng thái | Trích dẫn / ghi chú | URL |
|---|---|---|---|
| Phản hồi đầu tiên từ vệ tinh nguyên mẫu Suncatcher | [OK] | "We've received our first response from the Project Suncatcher prototype satellite." (Oct 30, 2026) | blog.google/.../project-suncatcher-satellite-response/ |
| Tên dự án Suncatcher; mục tiêu | [OK] | Google: "long-term research moonshot to explore powering AI compute in space"; VnExpress: "dự án dài hạn Suncatcher, phục vụ mục đích nghiên cứu khả năng xây trung tâm dữ liệu AI trên quỹ đạo" | blog.google; vnexpress.net/...5139248.html |
| Haiku do Gemma 4 viết | [OK] | Google: "uplinked our first prompt to our onboard Gemma 4 open model"; haiku: "Blue marble below / Data streams in silent grace / Starlight feeds my core." Thanh Niên chỉ nói "Gemma" | blog.google; theregister.com/...5306818 |
| Svalbard, Na Uy | [OK] | "As the satellite passed by Svalbard, Norway, the downlinked poem confirmed success." Google không nói rõ "trạm"; VnExpress, Thanh Niên không nhắc Na Uy | blog.google; theregister |
| Ngày | [OK] | Google blog 30/10/2026; The Register 31/10/2026 15:36 UTC; phóng "ngày 1.10" (Thanh Niên) | blog.google; theregister; thanhnien.vn/...185261031214642948.htm |
| 4 chip TPU | [OK] | VnExpress: "trang bị 4 bộ xử lý Tensor (TPU)"; Thanh Niên: "bốn chip TPU". Google/Register không nêu số (chỉ "TPU trays") | vnexpress; thanhnien |
| TPU "cấp máy chủ"/"cấp trung tâm dữ liệu" | [OK] mức thấp | Google: "a data center class TPU" | blog.google |
| Chip "gắn ngay trong thân vệ tinh" | [KHÔNG NGUỒN] | bỏ | |
| "Đột phá" | [KHÔNG NGUỒN] (đánh giá) | bỏ | |
| Quỹ đạo đồng bộ mặt trời | [OK] | Thanh Niên: "quỹ đạo đồng bộ mặt trời" (nơi pin mặt trời gần như không bị che khuất); The Register: "low Earth orbit" (tương thích) | thanhnien; theregister |
| "điện mặt trời liên tục" | [DIỄN GIẢI] | Thanh Niên: "nguồn năng lượng mặt trời gần như vô tận", "pin mặt trời gần như không bị che khuất". Không có chữ "liên tục"; dùng cách nói của nguồn | thanhnien |
| Pin mặt trời ~1 kW | [OK] | VnExpress: "pin mặt trời công suất khoảng 1 kW" | vnexpress |
| "gửi dữ liệu thô... nghẽn băng thông" | [KHÔNG NGUỒN] | Google/Register không nêu băng thông, không nêu dữ liệu thô. VnExpress/Thanh Niên chỉ nói băng thông là thách thức của trung tâm dữ liệu không gian. Bỏ line4–5 và scene4–5 | |
| Xử lý tại chỗ | [DIỄN GIẢI] | Google ngụ ý (chạy Gemma 4 trên vệ tinh) nhưng không dùng chữ "dữ liệu tại chỗ" | blog.google |
| "trung tâm dữ liệu lên không gian" | [OK] có điều kiện | The Register: "first experimental orbital AI datacenter satellite"; VnExpress: "xây trung tâm dữ liệu AI trên quỹ đạo". Chỉ là nghiên cứu, chưa phải kỷ nguyên | theregister; vnexpress |
| Chi phí | [DIỄN GIẢI] | The Register: haiku "very expensive", vệ tinh ~500 kg, giá phóng "around $7,000 per kg"; Google tính phóng $200/kg có thể làm điện toán quỹ đạo ngang chi phí điện mặt đất, kỳ vọng khoảng 2035 (chưa dùng) | theregister |

### title: giữ nguyên
```
Vệ Tinh AI Google Chạy 4 Chip TPU: Viết 3 Dòng Thơ Vũ Trụ
```

### lines mới (đủ 8; dòng 0, 1, 2 giữ nguyên)
```json
[
  "Bốn chip Google viết ba dòng thơ vũ trụ.",
  "Tháng 10 năm 2026, vệ tinh AI Suncatcher của Google gửi tín hiệu về Na Uy.",
  "Đó là bài thơ haiku ba dòng do mô hình Gemma 4 viết ngoài quỹ đạo.",
  "Vệ tinh mang bốn chip TPU và pin mặt trời công suất khoảng một ki-lô-oát.",
  "Nó phóng ngày một tháng mười, bay trên quỹ đạo đồng bộ mặt trời.",
  "Quỹ đạo ấy giúp pin mặt trời gần như không bị che khuất.",
  "Dự án Suncatcher nghiên cứu khả năng xây trung tâm dữ liệu AI trên quỹ đạo.",
  "Bài thơ ngắn ấy là phản hồi đầu tiên từ vệ tinh nguyên mẫu Suncatcher."
]
```
Dòng 1: Google chỉ nói bài thơ "downlinked" khi vệ tinh bay qua Svalbard, Na Uy. Nếu muốn khắt khe: "...gửi bài thơ về khi bay qua Na Uy." (cần đổi keyword scene1 vẫn là "Na").

### scene cần đổi
Scene 3:
```json
{"type":"cards3d","at":3,"title":"VỆ TINH SUNCATCHER","cards":[{"k":"CHIP TPU","v":"4 CHIP","at":[3,"bốn"]},{"k":"PIN MẶT TRỜI","v":"~1 KW","at":[3,"pin"],"c":"acc"}]}
```
Scene 4:
```json
{"type":"kinetic","at":4,"items":[{"text":"PHÓNG NGÀY 1/10","at":4,"acc":true},{"text":"QUỸ ĐẠO ĐỒNG BỘ MẶT TRỜI","at":[4,"đồng"],"sm":true}],"clip":"pexels:39433173","veil":0.6}
```
Scene 5:
```json
{"type":"board","at":5,"title":"VÌ SAO CHỌN QUỸ ĐẠO NÀY","nodes":[{"text":"QUỸ ĐẠO ĐỒNG BỘ MẶT TRỜI","x":0.5,"y":0.27,"at":5,"shape":"box","w":800},{"text":"PIN KHÔNG BỊ CHE KHUẤT","x":0.5,"y":0.5,"at":[5,"che"],"shape":"box","w":700,"c":"acc"},{"text":"NĂNG LƯỢNG GẦN NHƯ VÔ TẬN","x":0.5,"y":0.82,"at":[5,"như"],"shape":"box","w":760}],"arrows":[{"from":0,"to":1,"at":[5,"che"]},{"from":1,"to":2,"at":[5,"như"]}]}
```
Scene 6:
```json
{"type":"ledger","at":6,"title":"PROJECT SUNCATCHER","rows":[{"k":"MỤC TIÊU","v":"NGHIÊN CỨU DÀI HẠN","at":[6,"nghiên"]},{"k":"NƠI ĐẶT","v":"QUỸ ĐẠO","at":[6,"quỹ"]}],"total":{"k":"TRUNG TÂM DỮ LIỆU AI","v":"ĐANG NGHIÊN CỨU","at":[6,"trung"]}}
```
Scene 7:
```json
{"type":"kinetic","at":7,"items":[{"text":"PHẢN HỒI ĐẦU TIÊN","at":7},{"text":"VỆ TINH NGUYÊN MẪU","at":[7,"nguyên"],"acc":true}],"clip":"pexels:39433173","veil":0.6,"ms":8}
```
Scene 0, 1, 2 giữ nguyên. Cập nhật `acc` top-level: ["bốn","ba","chip","quỹ đạo"] vẫn có trong lời.

### description (thay đoạn đầu)
```
Ngày 30/10/2026, Google công bố phản hồi đầu tiên từ vệ tinh nguyên mẫu Project Suncatcher: một bài thơ haiku 3 dòng do mô hình Gemma 4 chạy trên vệ tinh viết, gửi xuống khi vệ tinh bay qua Svalbard, Na Uy. Theo báo VnExpress và Thanh Niên, vệ tinh mang 4 chip TPU, pin mặt trời công suất khoảng 1 kW và bay trên quỹ đạo đồng bộ mặt trời. Suncatcher là dự án nghiên cứu dài hạn về khả năng xây trung tâm dữ liệu AI trên quỹ đạo. Giọng đọc tổng hợp từ nguồn công khai.
```

### say cần thêm
```json
{"kW":"ki-lô-oát","Svalbard":"Xvan-ba"}
```
(chữ "ki-lô-oát" đã viết thẳng trong lời; chỉ cần "Svalbard" nếu đưa vào lời đọc, hiện chỉ có trên hình.) Giữ say cũ.

---

## Tóm tắt phần không xác minh được

- Binance: cơ chế "hàm khóa từ xa / hợp đồng thông minh / FREEZE" không có nguồn nào (CNBC nói rõ không giải thích cơ chế). "Dò cơ chế ký duyệt" cũng không có; "10 chuỗi" chỉ TRM/Al Jazeera/Wikipedia nêu, VnExpress chỉ liệt kê 6 mạng. fbi.gov không mở được nên số "hơn 6 tỷ" lấy qua CoinDesk; "20:05 UTC" hơi khác giữa VnExpress (20h05-20h09 đợt đầu) và CNBC (20:05-20:20, cả vụ).
- Điện thoại cũ: toàn bộ "tháo rời rồi lắp lại", "hàng dựng từ linh kiện vắng bóng", "ba cửa hải quan" không có nguồn. Văn bản Thông tư gốc (thuvienphapluat) trả 403; việc gán 8517/8471/8525 cho điện thoại/máy tính/máy ảnh là danh pháp HS chuẩn, báo chỉ liệt kê mã. Điều khoản chuyển tiếp (giấy phép cũ) mới chỉ có tóm ý, chưa dùng.
- Altman: không có nguồn cho "gom chip nhớ", "giữ kín dữ liệu", "không phí thuê bao" như lời Altman; URL tweet trong spec là tweet 01/11/2025 (sai năm); ngày Musk đăng là 02/11 không phải 01/11; chưa mở được tweet gốc (x.com 402). Câu trích Altman "chỉ được dùng 5%" là lời VnExpress đặt trong ngoặc kép (dịch), chưa có bản gốc tiếng Anh. Description cũ thiếu ghi công ảnh CC BY.
- Google: băng thông/dữ liệu thô không có nguồn; "4 chip TPU" chỉ VnExpress/Thanh Niên (Google không nêu số); "cấp máy chủ" chỉ ở mức "data center class"; "điện mặt trời liên tục" thay bằng cách nói của báo. Lời Thanh Niên chỉ ghi "Gemma", Google ghi "Gemma 4".
