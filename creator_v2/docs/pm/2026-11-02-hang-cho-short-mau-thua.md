# Hàng chờ Short chưa lên sóng: phân loại theo mẫu thắng/thua tuần 44 (02/11/2026)

Chỉ đọc. Nguồn: `state.sqlite` bảng `item` (kind=short, MIM/CK, publish_at sau 09:53 UTC 02/11; tất cả đang stage `published` = đã upload private kèm lịch) và `data/stier/specs/<slug>.json`. Giờ là giờ VN (UTC+7). Bỏ qua 3 bài đã có kế hoạch thay: `ck-c2-mua-thu-nam-thu-sau`, `ck-c2-mot-lo-bao-nhieu`, `ck-c2-ban-lo-van-nop-thue`.
Mẫu: `docs/pm/2026-11-02-thang-thua-tuan-44.md` mục 4 (hook thắng = mâu thuẫn cụ thể ở khung đầu: cặp tiền đối nghịch (CK), người CÓ TÊN nói/làm điều trái kết quả (MIM)). Phân loại là đọc chữ (tiêu đề, câu 1, chữ khung 0), không xem hình, không có số xem của các bài này: đây là phỏng đoán theo mẫu n nhỏ, không phải dự đoán view.

Quy ước: THẮNG-MẪU = khớp mẫu thắng ngay câu/khung đầu. THUA-MẪU = nhân vật chỉ là vai trò/vô danh ở câu đầu hoặc hook khái niệm/thị trường chung, không cặp số tiền. TRUNG TÍNH = có số hoặc sự kiện cụ thể nhưng chưa đủ mâu thuẫn người có tên/cặp tiền. Công ty/tổ chức có tên (Samsung, Facebook, Nvidia, Google) tính là có tên.

## Tổng số

| Kênh | THẮNG-MẪU | TRUNG TÍNH | THUA-MẪU | Tổng |
|---|---|---|---|---|
| MIM | 10 | 53 | 42 | 105 |
| CK | 0 | 6 | 9 | 15 |
| Cộng | 10 | 59 | 51 | 120 |

Số bài tính cả các bản `-r2` (cùng nội dung, cùng giờ). Trong THUA-MẪU, mục ghi "không sửa được bằng hook" là ứng viên bỏ.

## 5 bài THUA-MẪU lên sóng sớm nhất (không tính -r2)

1. 02/11 19:00 CK `ck-e2-khong-phai-bao-hiem`: "Quỹ 24 triệu đỡ hoá đơn 15, thủng ở vài trăm." Khung: "15 TRIỆU ✓ ↔ VÀI TRĂM TRIỆU ✗ / quỹ 3 tháng = 24 triệu · VÍ DỤ GIẢ ĐỊNH"
2. 03/11 12:00 CK `ck-e2-ba-hay-sau-thang`: "Quỹ 24 triệu hay 48 triệu mới đủ?" Khung: "24 TRIỆU ↔ 48 TRIỆU / 3 THÁNG hay 6 THÁNG · VÍ DỤ GIẢ ĐỊNH (thiết yếu 8 triệu)"
3. 03/11 19:00 MIM `mim-qwerty-khong-lam-cham`: Yếu: "E và R đi liền nhất, vẫn nằm sát nhau." Khung: "E ↔ R / cặp hay đi liền nhất, nằm sát nhau". Không có tên: cân nhắc bỏ
4. 03/11 21:30 MIM `mim-qwerty-tu-dien-tin-vien`: Không sửa được bằng hook (spec không nêu tên tác giả Kyoto), cân nhắc bỏ
5. 04/11 06:30 MIM `mim-mcgurrin-muoi-ngon`: "Frank McGurrin gõ mười ngón, không nhìn xuống." Khung: "FRANK McGURRIN · 1888 / 10 NGÓN · KHÔNG NHÌN PHÍM"

Lưu ý: cả 5 đã ở stage `published` (đã upload private + hẹn giờ); thay bài theo `feedback-replace-uploaded-threshold` (hỏi chủ kênh trước). Bài đầu tiên lên 19:00 hôm nay.

## Bảng theo ngày lên sóng


### 02/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 17:00 | MIM | `mim-luat-58-88-phan-tram` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | CK | `ck-e2-khong-phai-bao-hiem` | THUA-MẪU | khái niệm "không thay được"; cặp số 15 vs vài trăm triệu chỉ ở câu 3 và tiêu đề | "Quỹ 24 triệu đỡ hoá đơn 15, thủng ở vài trăm." Khung: "15 TRIỆU ✓ ↔ VÀI TRĂM TRIỆU ✗ / quỹ 3 tháng = 24 triệu · VÍ DỤ GIẢ ĐỊNH" |
| 19:00 | MIM | `mim-2000-quyet-dinh-toa-an` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 21:30 | MIM | `mim-9-tren-10-hoc-sinh-dung-ai` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 03/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-qwerty-tung-xep-abc` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 11:30 | MIM | `mim-typewriter-mot-hang-phim` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 12:00 | CK | `ck-e2-ba-hay-sau-thang` | THUA-MẪU | câu hỏi khái niệm, số tiền chỉ ở câu 6 | "Quỹ 24 triệu hay 48 triệu mới đủ?" Khung: "24 TRIỆU ↔ 48 TRIỆU / 3 THÁNG hay 6 THÁNG · VÍ DỤ GIẢ ĐỊNH (thiết yếu 8 triệu)" |
| 17:00 | MIM | `mim-may-danh-chu-125-do` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | MIM | `mim-qwerty-khong-lam-cham` | THUA-MẪU | khái niệm/giả thuyết, không người, không số tiền; chỉ có mâu thuẫn E-R | Yếu: "E và R đi liền nhất, vẫn nằm sát nhau." Khung: "E ↔ R / cặp hay đi liền nhất, nằm sát nhau". Không có tên: cân nhắc bỏ |
| 21:30 | MIM | `mim-qwerty-tu-dien-tin-vien` | THUA-MẪU | nhân vật chỉ là vai trò ("điện tín viên", "hai nhà nghiên cứu") | Không sửa được bằng hook (spec không nêu tên tác giả Kyoto), cân nhắc bỏ |

### 04/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-mcgurrin-muoi-ngon` | THUA-MẪU | câu đầu là sự kiện chung; Frank McGurrin có tên nhưng ở câu 4 | "Frank McGurrin gõ mười ngón, không nhìn xuống." Khung: "FRANK McGURRIN · 1888 / 10 NGÓN · KHÔNG NHÌN PHÍM" |
| 11:30 | MIM | `mim-nam-hang-sap-nhap-1893` | THUA-MẪU | sự kiện doanh nghiệp, không người, không mâu thuẫn | Không sửa được bằng hook (không tên, không cặp số), cân nhắc bỏ |
| 17:00 | MIM | `mim-dvorak-doi-24-chu` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:30 | CK | `ck-b1-lai-uu-dai-nam-ngoai` | TRUNG TÍNH | một số tiền (+6,25 triệu/tháng) ở khung đầu, chưa phải cặp đối nghịch | — |
| 19:00 | MIM | `mim-hai-quan-1944-74-phan-tram` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 21:30 | MIM | `mim-loi-mon-qwerty` | THUA-MẪU | khái niệm (lối mòn), câu đầu không người, không số | Yếu: "Paul David, 1985: bạn đổi, máy chỗ làm vẫn thế." Khung: "PAUL DAVID · 1985 / ĐỔI BÀN PHÍM KHÔNG PHẢI CHUYỆN RIÊNG BẠN". Cân nhắc bỏ |

### 05/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-kasparov-xin-thua-19-nuoc` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 11:30 | MIM | `mim-con-bo-van-mot` | THUA-MẪU | "nhà vô địch thế giới" chỉ vai trò, tên Kasparov nằm ở câu 3 | "Kasparov lo sợ vì một con bọ phần mềm." Khung: "KASPAROV · 1997 / LO SỢ VÌ MỘT CON BỌ" |
| 12:00 | CK | `ck-e2-bang-tra-quy-khan-cap` | THUA-MẪU | câu hỏi chung "mất bao lâu?", cặp số ở câu 4-5 | "Để dành 1,5 triệu: 16 tháng. 3 triệu: 8 tháng." Khung: "1,5 TRIỆU → 16 THÁNG ↔ 3 TRIỆU → 8 THÁNG / thiết yếu 8 triệu · VÍ DỤ GIẢ ĐỊNH" |
| 17:00 | MIM | `mim-van-hai-co-the-hoa` | THUA-MẪU | "nhà vô địch thế giới" chỉ vai trò, đúng mẫu thua dù có mâu thuẫn | "Kasparov xin thua ở thế cờ có thể hoà." Khung: "KASPAROV XIN THUA / thế cờ vẫn có thể hoà · 1997" |
| 19:00 | MIM | `mim-32-may-hamburg` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 21:30 | MIM | `mim-bao-ve-loai-nguoi-1989` | THẮNG-MẪU | Kasparov nói ngôi thứ nhất "bảo vệ loài người" (giống lời trích thắng) | — |

### 06/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-levy-cuoc-1968` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 11:30 | MIM | `mim-200-trieu-the-co` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 12:00 | CK | `ck-b1-o-cang-lau` | THUA-MẪU | câu hỏi chung "ở bao lâu?", số là tỷ lệ, không phải cặp tiền | Một phần: "Ở 5 năm cần 8% mỗi năm, ở 20 năm 6,6%." Khung: "5 NĂM → ~8% ↔ 20 NĂM → ~6,6% / giá nhà phải tăng mỗi năm để mua ngang thuê · VÍ DỤ GIẢ ĐỊNH". Spec không có cặp tiền ở đầu |
| 17:00 | MIM | `mim-co-dam-da-giai` | THUA-MẪU | khái niệm "trò chơi đã có lời giải", không người | "Mười tám năm để chứng minh cờ đam luôn hoà." Khung: "18 NĂM / cờ đam luôn hoà · Alberta · 2007". Không có tên người |
| 19:00 | CK | `ck-e2-chia-nho-quy` | TRUNG TÍNH | số tiền cụ thể (10 triệu so với cả sổ) nhưng chưa là cặp đối nghịch; có thể thêm "30 triệu" ở khung đầu | — |
| 19:00 | MIM | `mim-nhan-ma-2005` | THUA-MẪU | "hai tay chơi nghiệp dư" vô danh, đúng mẫu thua | Không sửa được bằng hook (spec không nêu tên), cân nhắc bỏ |
| 21:30 | MIM | `mim-kasparov-noi-khong-2017` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 07/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-watson-toronto` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 11:30 | MIM | `mim-watson-nguong-50` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-watson-90-may-chu` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | CK | `ck-p1-thue-5-nam-cong-lai` | TRUNG TÍNH | một số tiền ở khung đầu, câu hỏi mở, chưa có cặp đối nghịch | — |
| 19:00 | MIM | `mim-jennings-74-van` | THẮNG-MẪU | 74 ván thắng liền rồi thua máy: đảo kết quả, giống master-60 (tên ở tiêu đề, chưa ở câu đầu) | — |
| 21:30 | MIM | `mim-watson-77-nghin-do` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 08/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-rush-holt-thang-watson` | THUA-MẪU | "một nhà vật lý" vô danh ở câu đầu; tên Rush Holt ở câu 3 | "Rush Holt thắng Watson, 8.600 đô so với 6.200." Khung: "RUSH HOLT 8.600 ↔ WATSON 6.200 / 28/02/2011" |
| 11:30 | MIM | `mim-watson-62-trieu-do` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-watson-ca-benh-gia-dinh` | THUA-MẪU | khái niệm, "một cỗ máy", không người | Không sửa được bằng hook (không tên), cân nhắc bỏ |
| 19:00 | CK | `ck-p2-tra-truoc-mot-ty` | THUA-MẪU | câu đầu là lãi suất trừu tượng 6,8%/năm (như hoa-von-7%); cặp tiền ở câu 3-5 | "Lãi một tỷ trong sổ: 5,7 triệu. Thuê: 6,2." Khung: "5,7 TRIỆU ↔ 6,2 TRIỆU / MỖI THÁNG · lãi 1 tỷ gửi sổ ↔ thuê căn y hệt · VÍ DỤ GIẢ ĐỊNH" |
| 19:00 | CK | `ck-p2-tra-truoc-mot-ty-r2` | THUA-MẪU | như bản gốc | như bản gốc |
| 19:00 | MIM | `mim-project-debater-79-62` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 21:30 | MIM | `mim-con-ngua-da-con-ngua-da` | THUA-MẪU | khái niệm ngôn ngữ, không người, không số | Không sửa được bằng hook, cân nhắc bỏ |

### 09/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-libratus-120-nghin-van` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 11:30 | MIM | `mim-poker-10-mu-161` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-hoc-bang-hoi-tiec` | THUA-MẪU | khái niệm thuật toán, không người | Không sửa được bằng hook, cân nhắc bỏ |
| 19:00 | CK | `ck-p3-nuoi-xe-moi-thang` | TRUNG TÍNH | một số tiền (130.000 đ), không cặp đối nghịch | — |
| 19:00 | CK | `ck-p3-nuoi-xe-moi-thang-r2` | TRUNG TÍNH | như bản gốc | — |
| 19:00 | MIM | `mim-to-bip-bang-toan` | THUA-MẪU | khái niệm, không người | Không sửa được bằng hook, cân nhắc bỏ |
| 21:30 | MIM | `mim-va-3-lo-hong-moi-dem` | THUA-MẪU | "con người", "cao thủ" vô danh | Không sửa được bằng hook (spec không nêu tên), cân nhắc bỏ |

### 10/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-claudico-thua-2015` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 11:30 | MIM | `mim-chia-bai-doi-xung` | THUA-MẪU | khái niệm phương pháp, không người | Không sửa được bằng hook, cân nhắc bỏ |
| 17:00 | MIM | `mim-pluribus-150-do` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | CK | `ck-p4-xe-mat-gia-moi-thang` | TRUNG TÍNH | một số tiền (700 triệu) và câu hỏi, không cặp đối nghịch | — |
| 19:00 | MIM | `mim-deepstack-11-nguoi` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 21:30 | MIM | `mim-cepheus-68-ngay` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 11/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-turing-co-tren-giay` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 11:30 | MIM | `mim-deep-blue-van-dau-1996` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-alphazero-28-72-0` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | CK | `ck-p5-mua-sau-nam-tang-40` | THUA-MẪU | thị trường chung (VN-Index), tỷ lệ %, không cặp tiền | Không sửa được thành cặp tiền; thay thế yếu: "Tám trên mười lần mua sau đà tăng 40% đều lỗ." Cân nhắc bỏ |
| 19:00 | MIM | `mim-deep-blue-bi-thao-do` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 21:30 | MIM | `mim-watson-health-ban-2022` | THUA-MẪU | khái niệm/tóm tắt "mười một năm", không người | "Watson Health bị bán, giá hơn một tỷ đô." Khung: "WATSON HEALTH / BÁN 01/2022 · HƠN 1 TỶ ĐÔ (theo Bloomberg)". Không có tên người |

### 12/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 06:30 | MIM | `mim-noam-brown-nghi-lau-hon` | THUA-MẪU | khái niệm ("nghĩ lâu hơn"), tên Noam Brown ở câu 4 | "Noam Brown rời bàn poker, sang OpenAI năm 2023." Khung: "NOAM BROWN · 2023 / POKER → OPENAI". Yếu, không có mâu thuẫn |
| 11:30 | MIM | `mim-telex-tu-dien-tin` | THUA-MẪU | khái niệm kiểu gõ, không người | Không sửa được bằng hook, cân nhắc bỏ |
| 17:00 | MIM | `mim-chinook-tinsley-1994` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | CK | `ck-p6-270-nghin-tai-khoan-3-2022` | THUA-MẪU | thị trường chung, số tài khoản và chỉ số, không cặp tiền | "270 nghìn tài khoản mới, rồi chỉ số mất gần 40%." Khung: "270.217 TÀI KHOẢN MỚI ↔ −38,9% / 3/2022 → 11/2022 · NGUỒN: VSD". Không phải số tiền, yếu |
| 19:00 | CK | `ck-p6-270-nghin-tai-khoan-3-2022-r2` | THUA-MẪU | như bản gốc | như bản gốc |
| 19:00 | MIM | `mim-watson-tieng-chuong` | THUA-MẪU | khái niệm (cuộc đua bấm chuông), không người | Không sửa được bằng hook, cân nhắc bỏ |
| 21:30 | MIM | `mim-pluribus-khong-doc-vi` | THUA-MẪU | khái niệm, không người | Không sửa được bằng hook, cân nhắc bỏ |

### 13/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-cuda-canh-bac-2006` | THẮNG-MẪU | Ian Buck có tên, làm điều trái thường: card game đi làm toán | — |
| 11:30 | MIM | `mim-cuda-canh-bac-2006-r2` | THẮNG-MẪU | như bản gốc | — |
| 15:00 | MIM | `mim-p1-quang-cao-giong-gia` | THẮNG-MẪU | Scarlett Johansson có tên + "cô chưa từng nhận lời" | — |
| 19:00 | MIM | `mim-nvidia-quan-an-dem` | THUA-MẪU | "ba kỹ sư" vô danh; Jensen Huang ở câu 2 | "Jensen Huang lập Nvidia ở quán, không ai nhắc AI." Khung: "JENSEN HUANG · 1993 / QUÁN DENNY'S · KHÔNG AI NHẮC TỚI AI" |

### 14/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-tahoe-44-trieu-hinton` | THUA-MẪU | "công ty ba người" vô danh; Hinton ở câu 3 (mâu thuẫn có sẵn) | "Hinton rao bán công ty ba người, chưa có sản phẩm." Khung: "GEOFFREY HINTON · 12/2012 / CHƯA CÓ SẢN PHẨM ↔ 44 TRIỆU ĐÔ" |
| 15:00 | MIM | `mim-p2-tin-nhan-thoai` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | MIM | `mim-watson-lickel-nha-hang-im-lang` | THUA-MẪU | "cả nhà hàng" vô danh; Charles Lickel ở câu 2 | "Charles Lickel thấy cả quán bỏ ăn xem Ken Jennings." Khung: "CHARLES LICKEL · 2004 / CẢ QUÁN NÍN LẶNG / Ken Jennings · 74 ván thắng" |

### 15/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-nghin-may-chu-con-ba-2013` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 15:00 | MIM | `mim-p3-nghe-nhap-lieu` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | MIM | `mim-watson-khong-co-tai-oreo` | THẮNG-MẪU | Ken Jennings có tên, đáp sai, Watson sai y hệt | — |

### 16/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-dgx1-qua-tang-openai-2016` | THUA-MẪU | "ông chủ Nvidia" chỉ vai trò, Jensen Huang ở câu 2 | "Jensen Huang tự mang siêu máy tính tới OpenAI." Khung: "JENSEN HUANG → OPENAI · 08/2016 / DGX-1 · ~129 NGHÌN ĐÔ" |
| 15:00 | MIM | `mim-p4-ilo-2023-van-phong` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-watson-ferrucci-sai-gan-het` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-watson-ferrucci-sai-gan-het-r2` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 17/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-fei-fei-li-14-trieu-anh` | THUA-MẪU | "cô" đại từ, tên Lý Phi Phi ở câu 2 | "Lý Phi Phi muốn gom ảnh cho mọi danh từ." Khung: "LÝ PHI PHI · 2006 / ẢNH CHO MỌI DANH TỪ · 2009: MỘT TẤM ÁP PHÍCH" |
| 15:00 | MIM | `mim-p5-recsys-2016` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | MIM | `mim-chat-nguoi-la-20-3-2023` | THUA-MẪU | "người lạ" vô danh, không mâu thuẫn ở câu đầu | "1,2% người dùng trả phí có thể bị lộ trong chín giờ." Khung: "1,2% · 9 GIỜ / ChatGPT · 20/03/2023". Không có tên người |

### 18/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-patrascu-card-game-2009` | THUA-MẪU | "người dựng máy" chỉ vai trò, Relu Patrascu ở câu 2 | "Relu Patrascu thử card game thay card Tesla đắt." Khung: "RELU PATRASCU · 2009 / CARD GAME THAY CARD TESLA" |
| 15:00 | MIM | `mim-p6-feed-cua-ban` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | MIM | `mim-samsung-ba-vu-truoc-khi-cam` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | MIM | `mim-samsung-ba-vu-truoc-khi-cam-r2` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 19/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-jensen-ha-noi-nha-thu-hai` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-chat-da-xoa-van-bi-giu` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-chat-da-xoa-van-bi-giu-r2` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 20/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-watson-buoi-tap-kem-mot-nghin-do` | THẮNG-MẪU | Ken Jennings có tên, chỉ kém Watson 1.000 đô (kết quả trái kỳ vọng) | — |
| 19:00 | MIM | `mim-4500-chat-link-chia-se` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 21/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-polaris-2007-2008` | THUA-MẪU | "máy poker thua người" vô danh; Laak, Eslami ở câu 2 | "Phil Laak và Ali Eslami thắng Polaris, sát nút." Khung: "LAAK · ESLAMI vs POLARIS · 2007 / 2 THẮNG · 1 THUA · 1 HOÀ" |
| 19:00 | MIM | `mim-y-chan-chatgpt-roi-toa-huy-phat` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 22/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-jeopardy-julann-tren-may-bay` | THUA-MẪU | "một người vợ" chỉ vai trò, Julann Griffin ở câu 2 | "Julann Griffin đọc đáp án trước, trên máy bay." Khung: "JULANN GRIFFIN / 5.280 → MỘT DẶM DÀI BAO NHIÊU FEET?" |
| 19:00 | MIM | `mim-meta-ai-sua-xe-cong-khai` | THUA-MẪU | "anh" vô danh, spec không nêu tên | "Meta AI đăng công khai chat sửa xe của anh." Khung: "6/2025 · META AI / ANH KHÔNG ĐỊNH ĐĂNG CÔNG KHAI". Không có tên người |
| 19:00 | MIM | `mim-meta-ai-sua-xe-cong-khai-r2` | THUA-MẪU | như bản gốc | như bản gốc |

### 23/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-face-id-san-khau-2017` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-altman-khong-nhu-bac-si` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 24/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-viola-jones-2001-may-tim-mat` | THUA-MẪU | "hai người" vô danh; Paul Viola, Michael Jones ở câu 2 | "Paul Viola và Michael Jones dạy máy tìm mặt người." Khung: "VIOLA · JONES · 2001 / 15 HÌNH/GIÂY · PENTIUM III 700 MHz" |
| 19:00 | MIM | `mim-elias-bai-toan-to-bip` | THUA-MẪU | "kỷ lục gia poker" chỉ vai trò, Darren Elias ở câu 2 | "Darren Elias kém máy bốn cược lớn mỗi trăm ván." Khung: "DARREN ELIAS vs 5 BẢN SAO / −4 CƯỢC LỚN / 100 VÁN" |

### 25/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-nist-2018-bon-nam-20-lan` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 19:00 | MIM | `mim-deepseek-kho-chat-khong-mat-khau` | THUA-MẪU | "một kho dữ liệu" vô danh ở câu đầu | "Wiz thấy kho chat DeepSeek không cần mật khẩu." Khung: "WIZ · 29/01/2025 / KHO CHAT DEEPSEEK · KHÔNG CẦN MẬT KHẨU". Không có tên người |

### 26/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-facenet-2015-mot-tram-hai-muoi-tam-byte` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-sandholm-hai-cap-doi-than` | THUA-MẪU | "hai người lạ" vô danh; Tuomas Sandholm ở câu 5 | "Tuomas Sandholm viết thuật toán ghép hai quả thận." Khung: "TUOMAS SANDHOLM · 06/12/2010 / 2 NGƯỜI LẠ · 2 QUẢ THẬN · 1 THUẬT TOÁN" |

### 27/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-game-dendi-2017` | THẮNG-MẪU | Dendi có tên, thua máy trên sân khấu lớn nhất | — |
| 19:00 | MIM | `mim-robert-williams-2020-theo-aclu` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 28/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-game-tlo-thua-roi-viet-luat` | THẮNG-MẪU | TLO có tên, thua 0-5 rồi viết luật cho máy | — |
| 19:00 | MIM | `mim-deepface-2014-bon-trieu-khuon-mat` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 29/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-game-khan-gia-chon-tuong-hai-may` | THUA-MẪU | "khán giả" vô danh (Blitz chỉ ở câu 3) | "Khán giả cố ý chọn đội hình dở cho máy." Khung: "OPENAI FIVE · 05/08/2018 / KHÁN GIẢ CHỌN ĐỘI DỞ → NGƯỜI THẮNG". Yếu, không có tên người |
| 19:00 | MIM | `mim-jason-les-ba-co-may` | THUA-MẪU | "một cao thủ poker" vô danh ở câu đầu (Jason Les ở câu 2) | "Jason Les: cả nhóm hơn máy, riêng anh thua." Khung: "JASON LES · 2015 / NHÓM +730.000 PHỈNH · RIÊNG ANH: ĐỨNG SAU MÁY" |

### 30/11

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-game-google-mua-atari-2014` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |
| 17:00 | MIM | `mim-joy-buolamwini-mat-na-trang-2018` | THUA-MẪU | "cô" đại từ, tên Joy Buolamwini ở câu 2 | "Máy chỉ thấy Joy Buolamwini khi cô đeo mặt nạ." Khung: "JOY BUOLAMWINI · MIT / MÁY CHỈ THẤY CÔ KHI ĐEO MẶT NẠ TRẮNG" |

### 01/12

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-game-mana-thua-nam-van-roi-thang` | THẮNG-MẪU | MaNa có tên, thua 0-5 rồi thắng | — |
| 19:00 | MIM | `mim-facebook-xoa-mot-ti-mau-khuon-mat-2021` | TRUNG TÍNH | số/sự kiện cụ thể ở câu đầu nhưng nhân vật không tên hoặc không có mâu thuẫn người; tên (nếu có) chỉ ở tiêu đề | — |

### 02/12

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-game-alpha-red-tran-thang-dau` | THUA-MẪU | "con người" vô danh; đội Alpha Red ở câu 3 | "Đội Alpha Red thắng OpenAI Five sau vài giờ." Khung: "ALPHA RED (THÁI LAN) / THẮNG TRẬN ĐẦU SAU VÀI GIỜ · 18/04/2019" |

### 03/12

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-game-tai-khoan-an-danh-grandmaster` | THUA-MẪU | "tài khoản ẩn danh" vô danh, không người, không số | Không sửa được bằng hook, cân nhắc bỏ |

### 04/12

| Giờ VN | Kênh | Slug | Phân loại | Lý do | Hook đề xuất (câu đầu ≤ 9 từ + chữ khung đầu) |
|---|---|---|---|---|---|
| 11:30 | MIM | `mim-game-og-thua-may-roi-vo-dich` | THUA-MẪU | "nhà vô địch" chỉ vai trò, OG ở câu 2 | "OG vô địch từ vòng loại, rồi thua OpenAI Five." Khung: "OG · TI 2018: 3–2 / 04/2019: THUA OPENAI FIVE" |

## Ghi chú

- Hook đề xuất chỉ dùng dữ kiện có trong spec (lines, description, sources) của chính bài đó. "5,7 triệu/tháng" của `ck-p2-*` là 68 triệu chia 12 theo chính câu 3 của spec ("chia ra, khoảng năm triệu bảy"). Chưa kiểm khung hình, chưa chạy lint mix.
- CK không có bài THẮNG-MẪU trong hàng chờ: không bài nào có cặp tiền đối nghịch ngay câu đầu.
- Bài `-r2` là bản lặp cùng nội dung của bài gốc cùng giờ; thay hook thì thay cả hai (hoặc bỏ một).
- Các bài "không sửa được bằng hook" không có tên người hay cặp tiền trong spec; hướng xử lý (bỏ, đổi đề tài, thêm dữ kiện có nguồn) là quyết định của chủ kênh.
