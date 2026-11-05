# Đề xuất nội dung ba kênh — 04/11/2026

Nguồn số: `docs/pm/2026-11-04-analytics-3-kenh.md`, kỳ 20–26/10 và 27/10–02/11. Lịch MIM/CK: `state.sqlite` chỉ đọc, `publish_at` từ 2026-11-04, 156 dòng. Giờ VN = UTC+7. `published` = đã upload, đang riêng tư, có lịch. Không đăng, không đổi lịch, không ghi DB.

Cách chốt chung, lấy từ mục 7 của báo cáo: một biến mỗi video; đọc CTR khi đủ 1.000 impressions mới; chốt khi đủ 3.000 hoặc đủ 7 ngày, mốc nào đến sau; tách Browse và Suggested. Short: tỷ lệ ở lại cao hơn baseline tuần B của chính kênh ít nhất 5 điểm, AVP và sub không giảm. Các % giây 30 dưới đây là card 365 ngày trong báo cáo, không phải retention của riêng tuần B.

## 1. Mười việc cần duyệt

1. CK: đổi một tiêu đề Long mua–thuê, giữ thumbnail. Không làm Long mới cùng cặp 19/6 triệu.
2. CK: chưa đổi video viện phí. Chỉ đổi sau khi video thật sự trả lời câu hứa mới.
3. CK: lấp đúng slot trống 04/11 19:00 bằng short sức mua, phương án 1 ở mục 5.
4. CK: giữ các short C2 và bảng quỹ đã hẹn. Không thêm bài hai cụm này.
5. MIM: đọc retention video thuật toán trước. Chưa đổi tiêu đề hay thumbnail video đó.
6. MIM: đổi một tiêu đề Long Sholes nếu video đã nói tới phím điện thoại.
7. MIM: giữ chuỗi Watson/Kasparov/Deep Blue đã hẹn. Không thêm bài cùng kiểu.
8. CL: đổi một tiêu đề Whitey thành lời của FBI, có cả việc ông phủ nhận. Giữ thumbnail.
9. CL: đọc retention Bảy Viễn. Hoãn đổi Capone. Hoãn Long và short Khun Sa khỏi 14 ngày này.
10. Cả ba kênh: không tăng số video. Mọi bài đã hẹn giữ nguyên cho đến khi có duyệt từng mục.

## 2. Biểu Đồ Biết Nói

Phân loại từng đề xuất mục 4 và dòng CK ở mục 7. Tiêu đề kênh phải ≤ 60 ký tự và theo dạng một khoản tiền × một mốc; số giả định phải có chữ "VÍ DỤ GIẢ ĐỊNH". Tuần 44 cho thấy hai khoản đối nghịch đi cùng view cao, và độ dài tiêu đề CK không kéo view xuống (tương quan hạng +0,33, n = 14). Chỗ luật và số lệch nhau được ghi trong từng dòng.

| # | Đề xuất trong báo cáo | Kết | Lý do |
|---|---|---|---|
| 1 | Long "19 triệu hay 6 triệu", kèm hook, thumb hai dòng, dựng tiếp nối | SỬA | 5.156 impr, CTR 1,0%, 131 views, 72% ở giây 30, AVD 5:10/13:48. Thân giữ người, bao bì yếu. Tiêu đề gợi ý dài 69 ký tự. Đã có video này: việc là đổi tiêu đề video cũ, không làm Long mới. |
| 2 | Long sức mua, giỏ hàng nhỏ đi | SỬA | Đúng cụm cần thử. Tiêu đề gợi ý không có khoản tiền × mốc. `long-ck-a2-luong-va-lam-phat` đã hẹn 16/11 20:00. Không thêm Long. Thử bằng short ở slot trống. |
| 3 | Long giá vàng trở lại đỉnh, người mua đã hoà vốn chưa | SỬA | Không khuyên mua/bán: đúng luật. Hoãn khỏi 14 ngày. Tháng 10/2026 không dùng làm "trở lại đỉnh": chỉ số giá vàng giảm 2,85% so với tháng trước và 2,94% so với cùng kỳ; bình quân 10 tháng vẫn tăng 37,28% (mục 6). |
| 4 | Short tách gốc/lãi của 19 triệu | SỬA | Đúng cụm nhà. Phải gắn giả định. Gần `ck-p1-thue-5-nam-cong-lai` (07/11 19:00). Không làm thêm trong tuần này. |
| 5 | Short "thuê rẻ hơn mà cuối năm vẫn không dư" | NHẬN | Câu mở là câu hỏi, chưa nhét số bịa. Dùng làm phương án 2 cho slot 04/11 19:00. Khi đưa 13 triệu thì ghi phép tính 19 − 6 và gắn giả định. |
| 6 | Short thêm 10 triệu nhưng mua được ít hơn | NHẬN | Chưa thấy slug cùng câu trong lịch từ 04/11. Đây là phương án 1. Số 10 triệu là giả định, không phải số CPI. |
| 7 | Short quỹ khẩn cấp, highlight một hàng | SỬA | AVP bảng tự dò 87,6% và 90,1% chưa chứng minh người xem đọc lại, chính báo cáo đã nói vậy. Tuần 44 cụm quỹ trung vị 236 view. Đã có `ck-e2-bang-tra-quy-khan-cap` (05/11) và `ck-e2-chia-nho-quy` (06/11). Không thêm. |
| 8 | Đổi viện phí thành "cầm cự 90 ngày?" và thumb "CÒN ĐỦ 90 NGÀY?" | SỬA | 2.895 impr, CTR 0,4%: đủ ngưỡng để xét bao bì. Báo cáo đã gắn điều kiện nội dung phải trả lời câu đó. Chưa có kịch bản trong nguồn được đọc: chưa đổi. |
| 9 | Rút tiêu đề hai vế cho ngắn | BỎ | Tuần 44: đừng rút tiêu đề CK vì độ dài. Nút thắt đang đo được là CTR 1,0% và 0,4%, không phải số ký tự. |
| 10 | Thumbnail tối đa một phép so sánh | NHẬN | Khớp CTR thấp của hai Long có đủ impr. Giữ cho đợt sau, khi tiêu đề đã chốt. Không đổi thumb cùng đợt với tiêu đề. |
| 11 | Mục 7: thêm 1 Long và 4 Short cùng cụm | SỬA | Giữ cụm tiền nhà / sức mua / quỹ. Lịch 05–12/11 đã có short 19:00. Chỉ lấp một lỗ 04/11 19:00. |

Tally CK: 11 đề xuất, 3 NHẬN, 7 SỬA, 1 BỎ.

### Ba việc, 14 ngày

1. Đổi tiêu đề Long mua–thuê. Biến: tiêu đề. Giữ thumbnail. Câu dùng nếu video đã nói đúng điều này: "Cùng một căn: 19 triệu hay 6 triệu mỗi tháng?" (45 ký tự, hai khoản và mốc "mỗi tháng"; số 6 triệu ở thumb cũ). Nếu title đang live đã có các chữ đó thì không đổi, vì không còn biến để đo. Chỉ số: CTR Browse và CTR Suggested so với 1,0%. Mốc 24h ghi impr đã chạy; đọc ở 1.000 impr mới; chốt ở 7 ngày hoặc 3.000 impr. Dừng: CTR cùng nguồn không cao hơn 1,0% thì trả tiêu đề cũ.
2. Đọc video viện phí, chưa sửa trên kênh. Cổng: có trả lời "cầm cự được bao lâu" hay chỉ nói hoá đơn 15 triệu. Không trả lời thì dừng, để câu 90 ngày cho một video sau. Có trả lời thì xếp hàng sau việc 1.
3. Một short sức mua vào 04/11 19:00, phương án 1. Biến: câu mở với hai hình đối nghịch và nhãn giả định. Chỉ số: tỷ lệ ở lại so với 34,2%. Mốc 24h, 72h, 7 ngày. Dừng: ở 72h không cao hơn baseline ít nhất 5 điểm thì không làm thêm short cùng cách mở.

### Bao bì Long đã có

Chỉ hai video trong báo cáo có từ 1.000 impr trở lên.

- Mua–thuê, 5.156 impr, CTR 1,0%. Đáng đổi tiêu đề, một lần, theo việc 1. Slug không có trong lịch từ 04/11.
- Viện phí, 2.895 impr, CTR 0,4%. Chưa đổi. Câu "Mất thu nhập 3 tháng: bạn cầm cự được bao lâu?" chỉ được duyệt sau cổng ở việc 2.

`long-ck-f2-vien-phi-bhyt` (20/11 20:00) là bài đã hẹn của lô mới. Chưa có căn cứ nói đó chính là video 2.895 impr. Không huỷ bài 20/11.

## 3. Mind in the Machine

Luật tiêu đề: ≤ 60 ký tự, và có người + năm + bước ngoặt, hoặc khuôn "[phim/app] Ngoài Đời Thật: [người]". Ảnh chỉ PD, CC0, CC BY.

| # | Đề xuất trong báo cáo | Kết | Lý do |
|---|---|---|---|
| 1 | Long ChatGPT, nguồn trông thật, vụ án không tồn tại | SỬA | 3.850 impr, CTR 1,2%, ngang Long cả kênh 1,1%; 76% ở giây 30; AVD 5:52/13:26. Bao bì không phải lỗ lớn. Tiêu đề gợi ý 60 ký tự, sát trần, không có người + năm. Cụm đã có short tuần 44 và `mim-y-chan-chatgpt-roi-toa-huy-phat` (21/11). Không làm Long mới. |
| 2 | Long "5 phút rồi mất một giờ" | SỬA | "Thuật toán đề xuất" = 13.628/22.908 impr Long tuần B, tức 59,5%; CTR 0,8%; AVD 2:48/13:36. Đổi thumbnail không đủ. Không làm Long mới. Việc là đọc retention. Tiêu đề gợi ý không theo khuôn MIM. |
| 3 | Long vì sao điện thoại vẫn theo máy chữ | SỬA | Sholes: AVD 6:07/8:54, CTR 0,6% trên 1.777 impr. Đổi tiêu đề video cũ, không làm Long mới. Tiêu đề gợi ý đúng 60 ký tự, sát trần, và không có người + năm. Hook không được chốt giai thoại kẹt phím (mục 6). |
| 4 | Short kiểm nguồn, "có số trang mà sách không tồn tại" | SỬA | Đúng kiểu hậu quả. Trùng góc `mim-sau-vu-an-khong-co-that`, `mim-sieu-cong-cu-tim-kiem`, `mim-phat-5000-do-va-nhung-la-thu` và short 21/11. Không thêm trong tuần 45–46. |
| 5 | Short "thua máy nhưng người đánh hay hơn" | NHẬN | Đúng một bài. Góc này 889 views, AVP 86,4%; nhiều clip AlphaGo cùng tuần chỉ 44–57%. Không mở chuỗi, không đặt vào 11/11 vì ngày đó đã có Deep Blue và AlphaZero. |
| 6 | Short một lần dừng xem, bảng gợi ý đổi | SỬA | `mim-p6-feed-cua-ban` đã hẹn 18/11 15:00. Không thêm. Làm loại S. Chưa dẫn sang Long thuật toán khi AVD còn 2:48. |
| 7 | Short QWERTY, máy chữ cắt sang điện thoại | SỬA | Đã có `mim-loi-mon-qwerty` và `mim-dvorak-doi-24-chu` cùng ngày 04/11. Không thêm bài thứ ba. Đối chiếu lời hai bài này với mục 6 trước giờ lên. |
| 8 | Cách dựng: hậu quả trong 3–5 giây, bỏ intro logo | NHẬN | Khớp short thắng tuần 44 và cảnh báo chuỗi giai thoại. |
| 9 | Mục 7: 1 Long mới + 4 Short; thứ tự luật sư rồi QWERTY rồi thuật toán | SỬA | Không Long mới, không 4 Short mới. Mười bốn ngày này: đọc retention thuật toán, rồi một tiêu đề Sholes. Luật sư để sau vì CTR đã 1,2%. |

Tally MIM: 9 đề xuất, 2 NHẬN, 7 SỬA, 0 BỎ.

### Ba việc, 14 ngày

1. Đọc retention video thuật toán ở giây 30 và phút 1–3. Biến trên kênh: không có. Báo cáo không có % giây 30 của riêng video này. Dừng: giây 30 đã thấp thì lúc đó mới xét tiêu đề; giây 30 cao mà AVD tuần B vẫn 2:48 thì lỗi ở thân, không vá bằng thumbnail.
2. Một tiêu đề Long Sholes, sau việc biết video có nói tới điện thoại hay không. Có nói: "Máy chữ hết rồi, sao còn phím Sholes 1873?" (42 ký tự, có người và năm, câu hỏi đặt trước tên). Không nói: chưa đổi, vì gắn lời hứa điện thoại sẽ thành câu viện phí. Biến: tiêu đề. Chỉ số: CTR so với 0,6%, tách nguồn. Dừng: 3.000 impr mới mà CTR cùng nguồn không vượt 0,6% thì trả tiêu đề cũ. AlphaGo Long chỉ 238 impr: chưa đủ để đổi bao bì.
3. Giữ chuỗi đã hẹn. Nếu được thay đúng một bài ngày 07/11, dùng một short loại S theo đề xuất 5. Chỉ số: tỷ lệ ở lại so với 25,7%, và AVP không về vùng 44–57%. Dừng: không làm bài thứ hai trong cùng tuần dù 72h đẹp.

### Bao bì Long đã có

- Sholes, 1.777 impr, CTR 0,6%, AVD 6:07. Đây là một tiêu đề, theo việc 2. Slug không có trong lịch từ 04/11.
- Luật sư / ChatGPT, 3.850 impr, CTR 1,2%. Chưa đổi trong 14 ngày này. CTR đã ngang mức Long cả kênh.
- Thuật toán đề xuất, 13.628 impr, CTR 0,8%, AVD 2:48. Chưa đổi tiêu đề, chưa đổi thumbnail.
- AlphaGo, 238 impr, 25 views tuần B. Dưới 1.000. Không đổi.

## 4. Into the Killer's Mind

CL không có trong `state.sqlite`. Không đọc file sản xuất. Tiêu đề vẫn ≤ 60 ký tự.

| # | Đề xuất trong báo cáo | Kết | Lý do |
|---|---|---|---|
| 1 | Long Whitey, "ông trùm là người của FBI", tái đóng gói | SỬA | 7.422 impr, CTR 1,5%, AVD 8:57/27:08: đủ để đổi một biến. Tiêu đề gợi ý 56 ký tự. "Là người của FBI" mạnh hơn hook của chính báo cáo ("người giúp FBI") và mạnh hơn nguồn đã mở: FBI nói ông là chỉ điểm từ 1975, ông phủ nhận. Đổi tiêu đề, không làm bản mới, không đổi thumb cùng đợt. |
| 2 | Long Capone, hồ sơ thuế thay súng đạn | SỬA | 2.272 impr, CTR 1,7%, 78% ở giây 30, AVD 12:41/27:17. Thân tốt. Tiêu đề gợi ý 67 ký tự, vượt 60. Hoãn sang sau mốc 7 ngày của Whitey. |
| 3 | Long mới: tiền Khun Sa đi qua đâu, bản đồ Tam Giác Vàng | BỎ | Khỏi 14 ngày này. Khun Sa 2.919 views xuống 7. Long trừ Khun Sa tăng 135,1% views: việc trước là bao bì nhóm mới. Tiêu đề gợi ý 55 ký tự, dưới 60, nhưng chưa tới lượt. |
| 4 | Short Whitey, hai hồ sơ, dẫn sang Long | NHẬN | Một bài, loại L, sau khi tiêu đề Long đã chốt để hai bài cùng một lời hứa. Lời đọc có cả khẳng định của FBI và việc ông phủ nhận. Không lãng mạn hoá. |
| 5 | Short dấu tiền Al Capone | SỬA | Đúng mẫu vật chứng. Hoãn, không phát cùng đợt với short Whitey. |
| 6 | Short băng cướp và ảnh tự chụp | SỬA | Clip cùng kiểu đã có 1.052 views. Chỉ làm khi có chi tiết mới đã kiểm. Không đăng lại clip cũ. |
| 7 | Short một địa danh của Khun Sa | BỎ | Khỏi 14 ngày này, cùng lý do hạ nhiệt. Nếu làm sau: một quan hệ lịch sử, không mô tả tuyến vận chuyển. |
| 8 | Cold open có mâu thuẫn và vật chứng; tới giây 30 phải rõ ai và câu hỏi | NHẬN | Khớp Shorts đang ra sub (+25 tuần B, ở lại 37,0%) và các clip khá: 1.052, 1.032 views, AVP kim cương 81,4%. |
| 9 | Mục 7: test Whitey và Capone, thêm Long Khun Sa, thêm 4 Short | SỬA | Giữ một tiêu đề Whitey và việc đọc Bảy Viễn. Bỏ Long mới và bốn short khỏi 14 ngày. |

Tally CL: 9 đề xuất, 2 NHẬN, 5 SỬA, 2 BỎ.

### Ba việc, 14 ngày

1. Đổi tiêu đề Whitey. Câu để duyệt: "FBI nói Whitey Bulger là chỉ điểm: ai bảo vệ ai?" (48 ký tự). Hình và lời phải có việc ông phủ nhận, nếu không thì câu này cũng vượt nguồn. Biến: tiêu đề. Chỉ số: CTR so với 1,5%, tách Suggested (47,5% views Long tuần B) và Browse (27,4%). Dừng: không cao hơn 1,5% cùng nguồn sau 3.000 impr thì trả tiêu đề cũ.
2. Đọc retention Bảy Viễn. Không đổi bao bì. 1.930 impr, CTR 2,1%, cao hơn Whitey và Capone; AVD 5:51/26:07, ngắn hơn Capone. Dừng: giây 30 đã tụt thì xét hook; giây 30 còn cao thì xét thân.
3. Một short Whitey loại L, sau khi tiêu đề Long đã chốt. Chỉ số: tỷ lệ ở lại so với 37,0%. Dừng: ở 72h không cao hơn ít nhất 5 điểm thì chưa làm short Capone. Không làm Long Khun Sa trong cửa sổ này.

### Bao bì Long đã có

- Whitey Bulger, 7.422 impr, CTR 1,5%. Đổi một tiêu đề, việc 1.
- Al Capone, 2.272 impr, CTR 1,7%. Chưa đổi. Khi tới lượt, một tiêu đề dưới 60 ký tự, ví dụ "Al Capone: hồ sơ thuế làm được, súng thì không" (46 ký tự), và chỉ nếu video đã kể đúng trình tự đó.
- Bảy Viễn, 1.930 impr, CTR 2,1%. Không đổi bao bì. Đọc thân.
- Khun Sa có rất nhiều impr ở tuần A (tổng Long 13.704 trừ 1.374 của phần còn lại). Tuần B chỉ còn 7 views. Không đổi tiêu đề để đu theo đợt đã nguội. Không lấy giờ xem để xếp bài: báo cáo đã ghi lệch Khun Sa tuần A giữa views × AVD và 95,4 giờ.

## 5. Short đã hẹn và slot trống

Tuần 45 là 02–08/11, tuần 46 là 09–15/11. Cửa sổ soi: 04–15/11. Bản `failed` không tính là đã hẹn.

### Đi ngược kết luận

Giả thuyết, chưa có AVP của các bài chưa lên: nhiều giai thoại máy-thắng-người trong cùng tuần là kiểu báo cáo gắn với AVP AlphaGo 44–57%. Dời giờ không gỡ được kiểu đó.

| Slug | Giờ VN | Lý do | Đề xuất |
|---|---|---|---|
| `ck-c2-mot-lo-bao-nhieu` | 04/11 12:00 | Cụm C2. Tuần 44 trung vị cụm này 36 view. Cùng giờ với `ck-thue-xang-0-giam-1804-v2` | Giữ. Nếu phải bỏ một trong hai bài cùng giờ, bỏ bài này |
| `ck-c2-ban-lo-van-nop-thue` | 05/11 19:00 | Cùng cụm C2. Cùng giờ với `ck-ho-kinh-doanh-giam-30-thue` | Giữ. Nếu phải chọn một, bỏ bài này |
| `ck-e2-bang-tra-quy-khan-cap` | 05/11 12:00 | Đúng chủ đề quỹ, sai cách mở (bảng tra). Cùng giờ với `ck-dien-giam-44-dong-20-nam-v2` | Giữ. Không làm thêm bảng |
| 11 short Watson/Jeopardy + `long-mim-watson-jeopardy` (04/11 20:00) | 06–15/11 | Dày nhất là 07/11 giờ VN, năm bài: `mim-watson-toronto` (06:30), `mim-watson-nguong-50`, `mim-watson-90-may-chu`, `mim-jennings-74-van`, `mim-watson-77-nghin-do`. Các bài còn lại: `mim-rush-holt-thang-watson` (08/11 06:30), `mim-watson-62-trieu-do`, `mim-watson-health-ban-2022`, `mim-watson-tieng-chuong`, `mim-watson-lickel-nha-hang`, `mim-watson-khong-co-tai-oreo` | Giữ cả chuỗi. Không thêm |
| `mim-kasparov-xin-thua-19-nuoc`, `mim-kasparov-noi-khong-2017`, `mim-deep-blue-van-dau-1996`, `mim-alphazero-28-72-0`, `mim-deep-blue-bi-thao-do` | 05/11, 06/11, 11/11 | Cùng kiểu cờ / máy thắng người. Ngày 11/11 có ba bài cờ | Giữ. Không thêm |

Giữ, vì đúng hướng hoặc vì là pilot đã chốt: `mim-dvorak-doi-24-chu` và `mim-loi-mon-qwerty` (04/11); `ck-b1-lai-uu-dai-nam-ngoai`, `ck-b1-o-cang-lau`; `ck-p1` đến `ck-p6` (07–12/11 19:00). `ck-p3` và `ck-p4` là chuyện xe, lệch cụm nhà, vẫn giữ: đổi chủ đề sẽ hỏng pilot câu mở. Không dùng hai bài xe để kết luận cụm nhà. Pilot MIM `mim-p1` đến `mim-p3` (13–15/11 15:00) giữ.

Cùng một `publish_at` còn có cặp bản và bản `-r2`: `ck-p2` (08/11 19:00), `ck-p3` (09/11), `ck-p6` (12/11), `mim-cuda-canh-bac-2006` (13/11 11:30). Sau 15/11 còn ferrucci, samsung, chat-da-xoa, meta-ai. Không rõ bản nào sẽ công khai. Chủ kênh soi trước giờ lên.

### Slot trống

- CK 04/11 19:00 (`2026-11-04T12:00:00Z`): không có dòng. Đây là lỗ trong nhịp 19:00 đang chạy 05–12/11.
- CK 13/11, 14/11, 15/11 lúc 19:00: trống so với nhịp đó. Không lấp. Pilot kết thúc 12/11; thêm ba ngày là tăng sản lượng.
- MIM từ 12/11 23:30Z trở đi bỏ bớt mốc 17:00, 21:30 và 06:30. Không lấp. Khung 06:30 VN tuần 44 có trung vị 441,5 view (n = 8, lẫn chủ đề).

Ba phương án cho CK 04/11 19:00. Chọn một. Mọi số tiền trên hình gắn "VÍ DỤ GIẢ ĐỊNH".

| | Phương án 1, nên chọn | Phương án 2 | Phương án 3 |
|---|---|---|---|
| Câu mở | "Tài khoản thêm mười triệu. Cái giỏ lại bớt một món." | "Thuê rẻ hơn mười ba triệu mỗi tháng. Cuối năm ví vẫn không dư." | "Lương mười lăm triệu chưa cho biết quỹ của bạn là bao nhiêu." |
| Frame đầu | "10 TRIỆU ↑" đối diện "GIỎ −1 MÓN" | "13 TRIỆU/THÁNG" tách ba nhánh tiêu / giữ / trả nợ. 13 = 19 − 6 | Một hàng "CHI 10 TRIỆU → QUỸ 3 THÁNG". Không mở cả bảng |
| Loại | S. `long-ck-a2-luong-va-lam-phat` (16/11) cùng cụm lương–lạm phát; chưa đọc kịch bản nên chưa gắn L | S. Gần Long mua–thuê đã có và `ck-p1` (07/11); khác câu hỏi | S |
| Trùng | Không thấy slug giỏ hàng/sức mua từ 04/11 | Không trùng slug. Gần cụm 19/6 và `ck-p1` | Gần `ck-e2-bang-tra-quy-khan-cap` và `ck-e2-chia-nho-quy`. Xếp cuối |

Ba phương án MIM chỉ dùng khi chủ kênh thay một bài đã hẹn, không dùng để thêm slot. Chọn một, ưu tiên phương án 1 nếu bỏ một bài Watson ngày 07/11.

| | Phương án 1 | Phương án 2 | Phương án 3 |
|---|---|---|---|
| Câu mở | "Thua máy, rồi người đánh cờ lại hay hơn." | "Có cả số trang. Cuốn sách vẫn không có." | "Không còn thanh kim loại. Sao điện thoại vẫn QWERTY?" |
| Frame đầu | Hai chuỗi nước đi, một kết quả. Chưa đặt tên và năm ở khung 0 | Một dòng trích giả, dấu "KHÔNG CÓ SÁCH". Không logo | Máy chữ cắt sang điện thoại. Ảnh phải là PD, CC0 hoặc CC BY. Không dùng ảnh Getty trên bài Smithsonian |
| Loại | S | S | S, cho đến khi biết Long Sholes có trả lời câu này |
| Trùng | Gần cụm Lee Sedol tuần 44. Đây là một lần của góc AVP 86,4%, không phải chuỗi Kasparov | Trùng góc các short luật sư tuần 44 và `mim-y-chan-chatgpt-roi-toa-huy-phat` | Trùng `mim-loi-mon-qwerty` và `mim-dvorak-doi-24-chu` ngày 04/11. Chỉ dùng câu này để sửa lời bài đã có nếu lời đó chốt giai thoại |

## 6. Nguồn web đã mở

- CPI và giá vàng, Cục Thống kê qua VietNamNet, 03/11/2026: https://vietnamnet.vn/gia-xang-dau-tang-day-cpi-thang-10-tang-0-2-2570927.html — CPI tháng 10/2026 +0,2% so với tháng trước, +5,09% so với cùng kỳ; 10 tháng +4,57%; lạm phát cơ bản 10 tháng +4,24%; nhóm nhà ở, điện nước, chất đốt và vật liệu xây dựng 10 tháng +6,66%; giá thuê nhà tháng 10 giảm 0,22%; chỉ số giá vàng tháng 10 giảm 2,85% so với tháng trước, giảm 2,94% so với cùng kỳ, bình quân 10 tháng +37,28%. Short sức mua không được đọc các số này nếu chưa có dòng factcheck. Không viết "thuê nhà tháng này đang tăng".
- QWERTY, Smithsonian, mở được bản cập nhật 2025 của bài 2013: https://www.smithsonianmag.com/arts-culture/fact-of-fiction-the-legend-of-the-qwerty-keyboard-49863249/ — giả thuyết kẹt phím là chuyện phổ biến; bài dẫn nghiên cứu Kyoto 2011 kết luận cơ khí không quyết bố cục phím và bác ý định làm người gõ chậm lại; E và R vẫn nằm cạnh nhau.
- QWERTY, New Scientist, 2019: https://www.newscientist.com/article/2200664-the-truth-about-the-qwerty-keyboard/ — cách giải thích "để đánh chậm" không đứng vì các cặp chữ phổ biến vẫn gần nhau; một phân tích 1949 thấy QWERTY có nhiều cặp gần hơn bàn phím ngẫu nhiên; Jan Noyes kết luận không có lý do rõ cho vị trí các chữ. Hai nguồn không chốt một nguyên nhân. Lời đọc chỉ được đặt câu hỏi, chưa được khẳng định "để khỏi kẹt" hay "để đánh chậm".
- Whitey Bulger, Wikipedia, mở 04/11/2026: https://en.wikipedia.org/wiki/Whitey_Bulger — FBI nói ông là chỉ điểm nhiều năm từ 1975; ông phủ nhận; người điều phối John Connolly báo trước cáo trạng cuối 1994. Không gọi ông là nhân viên FBI.

## 7. Chưa kiểm được

- Chưa xem video, chưa có đường retention từng giây, chưa có CSV để đối soát giờ xem. Không tính lại giờ xem từ views × AVD.
- Chưa có title đang live từng ký tự, chỉ có cách báo cáo gọi tên. Slug của Long mua–thuê, viện phí, Sholes, luật sư, thuật toán, và mọi Long CL, không nằm trong query từ 04/11.
- Chưa đọc kịch bản các short đã hẹn, trừ chỗ retro 03/11 đã ghi. Chưa biết `mim-loi-mon-qwerty` có khẳng định giai thoại hay không.
- Chưa biết trong mỗi cặp cùng giờ, kể cả bản `-r2`, video nào sẽ ra công khai.
- Chuỗi Watson/Kasparov đi ngược kiểu biên tập của báo cáo. AVP 44–57% là số của AlphaGo, không phải số đã đo trên các bài chưa lên.
- Trung vị 06:30 VN của MIM (441,5, n = 8) lẫn chủ đề, theo chính bản tuần 44.
- Trang Britannica và history.com không mở được trong lượt này. Kết luận Whitey dùng Wikipedia và chữ trong báo cáo.
