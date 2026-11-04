# Retro MIM Shorts pilot (GH-33), 03/11/2026

Phạm vi: 6 Short đã upload private + hẹn lịch. Đối chiếu `data/stier/specs/<slug>.json`, `docs/pm/tickets/GH-33-MIM-facts.json` (quote + facts_supported), `output/stier/<slug>/final_sheet.jpg` và `credits.json`. Không fetch lại URL (tin cậy nguồn đã lưu). Không sửa gì.

## Kết luận nhanh
- Số liệu lõi (6,3 tỷ/20 phút/36 giờ/10 chuỗi/3 tỷ, 8 byte/cổng 2948/20 tin/Android 14–17, 01/01/2027, 9/10, 5/10, 0,01 USDC, 5%, 4 chip TPU, 3 dòng haiku) đều truy được về facts hoặc nguồn.
- Điểm yếu giống CK: các câu **lý do/nhân quả** do biên tập thêm, không có trong quote. Không có tên công ty/logo ngoài ý muốn trong clip (clip chỉ là bo mạch, màn hình mờ, người cầm điện thoại, Trái Đất). Không có khung rỗng hay chữ giữ chỗ; vài khung chuyển cảnh trống ngắn là bình thường.
- Không có ghi chú nội bộ (CẦN KIỂM, `<>`, data/long) trong title, description, sources.
- Không có ảnh AI, không dùng `EXT:ai:`.

## A. Có thể đổi nghĩa (chủ kênh quyết định có thay video private không)

**A1. Vệ tinh Google: "gửi dữ liệu thô gây nghẽn băng thông" là lý do Google đưa chip lên quỹ đạo** (lời đọc + cảnh board "NGHẼN BĂNG THÔNG"). Không quote nào nói vậy; Thanh Niên chỉ đỡ ý điện mặt trời liên tục. Câu "trước đây vệ tinh chỉ chụp ảnh rồi gửi dữ liệu thô" cũng không có nguồn. Đồng thời "mở màn kỷ nguyên đưa trung tâm dữ liệu lên không gian" là suy diễn.

**A2. Cấm nhập điện thoại cũ: "chặn đứng chiêu tháo rời máy cũ rồi nhập về lắp dựng lại"** và "hàng dựng từ linh kiện rời dần vắng bóng". Dân Trí chỉ nói cấm cả linh kiện cũ và hàng tân trang, không nêu mục đích chống "chiêu" nào hay dự báo thị trường. Thêm: cảnh ledger ghi mã HS 8517/8471/8525 không có trong quote nào (chỉ có trong gợi ý visual). Nếu mã sai, đây là lỗi thật, cần đối chiếu với Thông tư.

**A3. Sam Altman: "muốn gom chip nhớ về các trung tâm dữ liệu đám mây"** gán ý định cho người thật (cả mô tả: "gom bộ nhớ DRAM lên trung tâm dữ liệu"). Quote VnExpress chỉ nói RAM cá nhân dùng 5% thời gian là phân bổ tài nguyên tệ; Thanh Niên chỉ có tiêu đề "muốn hạn chế RAM". Kèm các vế không nguồn: "máy chủ đám mây 24/7" (biểu đồ), "không phải đóng phí thuê bao" / "0Đ THUÊ BAO", "giữ kín dữ liệu". Nên chỉnh thành "theo ông, RAM nên được dùng hiệu quả hơn" nếu thay.

**A4. Binance: cơ chế "hàm khóa từ xa tích hợp sẵn trong hợp đồng thông minh" và "ví nóng", "ký duyệt tự động".** VietNamNet chỉ nói ~3 tỷ USD bị nhà phát hành và sàn đóng băng trên chuỗi. Cơ chế hàm freeze và "ví nóng" không có quote. Mô tả viết "nhờ hàm khóa..." như nguyên nhân. Ngoài ra bảng ghi "ĐÔ LA MỸ · THEO FBI" cho 6,3 tỷ và 3,0 tỷ: FBI chỉ nói ">6 tỷ"; 6,3 từ VnExpress, 3 tỷ từ VietNamNet (sai attribution). "20:05 UTC" trên màn hình cũng không có trong quote.

## B. Cosmetic (giữ nguyên, ghi nhận)

- B1. OTP: "ví 10 USDC" (bảng thiết lập) không có trong facts. "Nhờ quyền đọc thư" là lý do suy ra, hợp lý nhưng không quote. Quote arXiv chỉ nói "often", con số 9/10 và 5/10 lấy từ facts.
- B2. Sam Altman: ảnh CC BY 2.0 (Village Global) có trong `credits.json` nhưng description **không** có dòng ghi công. final_sheet không thấy ảnh hiện trên khung nào, nên có thể nghĩa vụ chưa phát sinh; cần kiểm uploader có nối credits vào description không (chưa kiểm). Nếu ảnh có xuất hiện thì thiếu attribution là lỗi giấy phép, nâng lên A.
- B3. Dòng tweet Musk ghi ngày 01/11/2026 nhưng ID status 1984711311540605051 trông không khớp ngày đó; nên mở lại URL xác nhận.
- B4. Android: hook "20 tin làm sập Android" dễ hiểu 20 tin mới sập; thực tế 1 gói đã sập tiến trình, 20 tin mới kẹt vòng lặp khởi động. Phần thân nói đúng.
- B5. Cả 6 description lặp câu "Giọng đọc tổng hợp từ nguồn công khai." hai lần.
- B6. Câu chốt mang tính bình luận ("quyền đóng băng trong mã nguồn mới quyết định ai giữ tiền", "bảo mật 2 lớp → 0", "cuộc chiến thanh RAM định đoạt...") là ý kiến, không nên đọc như sự thật; chấp nhận.
- B7. Crediting Pexels đã có trong `credits.json` cho mọi clip; mô tả chưa kiểm tra có hiển thị (Pexels không bắt buộc).

## Bài học (sửa gốc, không sửa video đã đăng)
1. Mỗi câu "vì/do/nên/để" và mỗi con số trên màn hình phải có dòng `facts_supported` hoặc quote; thêm lint so `on_screen_codes` và câu nhân quả với facts.
2. Gán ý định cho người thật chỉ dùng đúng quote.
3. Ảnh CC BY: lint bắt buộc description chứa `credits.json` khi spec có `imgs`.

## Đợt thay -v2 (03/11)

Phạm vi: 4 Short thay bài cũ (binance, cam-nhap-dien-thoai-cu, sam-altman-ram, ve-tinh-google), đối chiếu spec, bundle (title/description đã đăng), final_sheet.jpg và bảng claim GH-33-MIM-fix-proposal.md. Không fetch lại nguồn; không sửa gì.

### Kết luận
Không còn lỗi đổi nghĩa nặng như đợt đầu (hết "hàm khóa", "gom chip", "chiêu tháo rời", "nghẽn băng thông"). Còn các điểm nhỏ dưới đây; riêng title vệ tinh nên cân nhắc.

### Theo video
- **Binance**: lời đọc khớp bảng claim. Nhỏ: dòng 1 và scene "10 CHUỖI" nêu mười chuỗi không ghi "theo TRM" (đề xuất ban đầu đã đánh dấu không bắt buộc); dòng 0 và title "Mất 6,3 Tỷ Trong 20 Phút" mạnh hơn nguồn (phần lớn số tiền bị rút trong ~20 phút, description nói đúng). Title "Gần Nửa Bị Đóng Băng" là ước tính của Binance, không ghi nguồn trong title. Giữ.
- **Điện thoại**: title "Hàng Tân Trang Cũng Không Thoát" bỏ điều kiện "nếu mã HS thuộc danh mục" (lời đọc và description có điều kiện). Nhỏ. Nhưng scene 2 "BỘ KH&CN · 3 NHÓM" (máy cũ / tân trang / linh kiện) gán cách chia ba nhóm cho Bộ, bảng claim ghi là cách chia của spec, không có nguồn. Nhỏ (nhãn trên hình). Tên nhóm mã HS (8517/8471/8525) là danh pháp HS chuẩn, báo chỉ liệt kê mã. Thông tư gốc chưa đối chiếu (thuvienphapluat 403) nhưng vẫn nằm trong danh sách nguồn công khai.
- **Altman/Musk**: quote Musk đúng nguồn, ngày 02/11 đã sửa, lời Altman chỉ gồm 5%, tối đa hóa đám mây, nguồn cung hạn chế. Bỏ tên báo khỏi lời đọc ổn (description và hình vẫn ghi Tom's Hardware, Gadgets Now, The Verge). Nhỏ: (1) title "Musk Phản Bác" là chữ tiêu đề VnExpress, nhưng nguồn nói meme "được cho là" đáp trả và Altman không phản hồi; (2) chart cột "MÁY CHỦ ĐÁM MÂY 24/7 = 100" biến "chạy 24/7" (Thanh Niên tóm ý) thành mức sử dụng 100%, mạnh hơn nguồn; (3) line 4 "Đằng sau là giá RAM tăng" ngầm nối nhân quả với tweet, nguồn chỉ nói "trong bối cảnh"; (4) line 7 "Musk đứng về phía người dùng" là diễn giải. Ghi công CC BY ảnh Altman có trong description; ảnh không hiện trên khung nào của sheet (không thiếu nghĩa vụ, chỉ thừa an toàn).
- **Vệ tinh**: title mới "Thứ Đầu Tiên Gửi Về Là 3 Dòng Thơ" là điểm rủi ro nhất: nguồn nói "first response" cho prompt đầu tiên gửi lên Gemma 4, không nói đây là thứ đầu tiên vệ tinh gửi về (vệ tinh phóng 1/10, chắc chắn đã gửi telemetry trước). Có thể gây hiểu sai. Phân loại: nhỏ-sát-ngưỡng; nếu sửa title thì dùng "Phản Hồi Đầu Tiên Là 3 Dòng Thơ" (đúng chữ Google). Nhỏ khác: line 0 "Bốn chip Google viết ba dòng thơ" ngầm nói chip TPU chạy Gemma (nguồn chỉ nói "TPU trays"/data center class TPU); nhãn arrow "30/10/2026" trên hình là ngày Google công bố, không phải ngày bài thơ được gửi; "ĐIỂM THEN CHỐT" là đánh giá biên tập.
- **Khung hình (4 sheet)**: không chữ tràn, không logo/thương hiệu công ty ngoài ý muốn (clip bo mạch, Trái Đất), không khung trống ngoài cảnh chuyển, không lỗi chính tả thấy được. Khung giữa chừng của counter/table/ledger là hiệu ứng đang xuất hiện.
- **Description**: không ghi chú nội bộ, không lặp vô lý; nguồn và credit đủ. Dòng "Giọng đọc tổng hợp từ nguồn công khai" nhất quán.

### Phân loại
Đổi nghĩa (cần thay): không có. Nhỏ (giữ): tất cả điểm trên; title vệ tinh là mục nên sửa nếu có dịp cập nhật metadata (không cần render lại).

### Nguyên nhân gốc đợt đầu và chặn (liên hệ issue #34)
Gốc: câu lý do/nhân quả và ý định gán cho người thật do biên tập viết thêm từ facts "diễn giải", không đối chiếu quote; số liệu trên hình không đi qua lint nguồn. Chặn (issue #34): (1) lint bắt câu có "vì/do/nên/để/nhờ" và mọi số/mã trên hình phải ánh xạ vào `facts_supported` hoặc quote; (2) lời gán cho người thật chỉ được lấy từ quote; (3) bắt buộc credits.json CC BY có trong description; (4) lint cảnh biểu đồ/bảng: giá trị không có trong facts thì cấm (ví dụ cột 100 = 24/7); (5) lint title: mọi danh từ riêng/số/từ "đầu tiên, duy nhất, cấm hoàn toàn" phải có claim.

### Bài học quy trình từ đợt thay
1. Giữ nguyên title bị chống trùng chặn (đã thấy ở bản đầu): chỉ đổi khi cần, và giữ cách nói của chính nguồn (VnExpress "Phản Bác"), không chế thêm.
2. Đổi title phải bám nguồn: title mới vệ tinh đã thêm "thứ đầu tiên" vượt quote; sau mỗi lần đổi title chạy lại bảng claim cho riêng title.
3. Từ so sánh/thứ tự ("đầu tiên", "cũng không thoát", "gần nửa") phải mang điều kiện hoặc người ước tính của nguồn.
4. Nhãn trên hình (3 nhóm, ngày arrow, 24/7 = 100) cần kiểm cùng cấp với lời đọc: chúng thoát khỏi lint văn bản.
5. Khi nguồn gốc không mở được (thuvienphapluat, fbi.gov), không để vào danh sách nguồn công khai như đã đối chiếu, hoặc ghi rõ ở retro.
