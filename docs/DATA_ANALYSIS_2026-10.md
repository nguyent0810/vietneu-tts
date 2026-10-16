# Phân tích số liệu Studio 28 ngày: FS và BUD (10/2026)

Người viết: Claude (Code), 16/10/2026. Dành cho agent Lead. Chỉ tài liệu, không đổi code.
Đây là phần **số liệu thật** thay cho các số "tóm tắt chưa kiểm" trong [`RECOMMENDATIONS_2026-10.md`](RECOMMENDATIONS_2026-10.md).

## 0. Dữ liệu và cách tính
| Kênh | File xuất Studio (người dùng gửi) | Cửa sổ | Tổng (dòng Total) |
|---|---|---|---|
| FS (Phong Thủy) | Table data + Chart data (5 video theo ngày) + Totals (theo ngày) | 18/9–15/10/2026 | 162.078 view · 499,0 giờ · +158 người đăng ký · 49.213 lượt hiển thị hình thu nhỏ (CTR 3,68%) |
| BUD (Phật giáo) | cùng 3 loại file | 17/9–14/10/2026 | 120.485 view · 332,3 giờ · +239 người đăng ký · 21.676 lượt hiển thị (CTR 3,05%) |

- Short = thời lượng ≤ 180 giây. "Video mới" = đăng trong cửa sổ.
- **Tỉ lệ xem (APV) là số suy ra**: giờ xem × 3600 / lượt xem / thời lượng. Có thể khác "Average percentage viewed" chính thức (tính cả xem lại; nhiễu ở video ít view).
- Thống kê "trần" chỉ dùng Short đã đăng ít nhất 3 ngày (FS: đăng ≤ 12/10; BUD: ≤ 11/10).
- Gom chủ đề bằng từ khoá trong tiêu đề, nên chỉ là gần đúng.
- File chỉ có top 500 video; tổng theo dòng lệch nhẹ với dòng Total (FS 161.879/162.078; BUD 120.217/120.485).
- FS có thêm file xuất thứ hai với **"Stayed to watch (%)"** và "Engaged views" (mục 2b). BUD **chưa có** hai cột này. Chưa kênh nào có cột "Shown in feed" riêng (cột "Thumbnail impressions" không tính lượt hiện trong feed Shorts).

## 1. Điều chung của hai kênh (đã có số liệu)
| | FS | BUD |
|---|---|---|
| Short mới trong cửa sổ | 129 (4,4/ngày) | 141 (4,9/ngày) |
| % lượt xem đến từ video đăng trong cửa sổ | 96,3% | 99,2% |
| Lượt xem của toàn bộ video cũ (FS 363, BUD 353 video) trong 28 ngày | 4.311 | 978 |
| Short ≥ 3 ngày: trung vị / p25 / p75 / p90 | 896 / 424 / 1.035 / 1.202 | 926 / 757 / 1.024 / 1.107 |
| % Short trong khoảng 600–1.200 view | 54% | 72% |
| % Short dưới 300 view / trên 1.200 view | 20% / 10,5% | 13% / 7% |
| Thời lượng xem trung bình mỗi lượt Short | — | 7,9 giây (Short ~26 giây) |
| Người đăng ký / 1.000 view | 1,0 | 2,0 |
| Giờ xem từ video dài / tổng | 43,3 giờ (8,7%) | 68,0 giờ (20,5%) |

1. **Băng chuyền, không tích luỹ.** Gần như mọi lượt xem đến từ Short mới đăng. Biểu đồ theo ngày: mỗi Short nhận phần lớn lượt xem trong 24 giờ đầu rồi gần như dừng (BUD: 5/5 video mẫu nhận 1.100–1.400 view ngày đầu).
2. **Trần ~1.000 view là thật, và giữ chân quyết định việc vượt trần.** Trung vị APV theo nhóm view:

   | Nhóm view | FS | BUD |
   |---|---|---|
   | < 300 / < 600 | 0,16 (<300) | 0,17 (<600) |
   | 600–900 | 0,19 | 0,20 |
   | 900–1.100 | 0,22 | 0,24 |
   | 1.100–1.500 | **0,48** | **0,38** |
   | > 1.500 | **0,47–0,50** | **0,54** |

   Muốn vượt trần cần APV khoảng ≥ 0,4–0,5. Đa số Short hiện ở 0,2.
3. **Video dài: CTR ổn, giữ chân thấp.** FS: 8 video dài mới, CTR 4,2–13%, nhưng người xem chỉ xem ~1–2 phút. Bản 35 phút "Năm 2027 là năm con gì…" giữ ~4,6% thời lượng (trung bình ~98 giây); bản 7,6 phút "4 tuổi phạm Thái Tuế" giữ ~15% (68 giây). BUD: "Luật Nhân Quả…" (30 phút) giữ ~11%, "Cuộc Đời Đức Phật…" (31 phút) ~17%. → Vấn đề là **mấy phút đầu**, không phải tiêu đề/hình thu nhỏ.
4. **YPP:** giờ xem video dài 28 ngày là 43 giờ (FS) và 68 giờ (BUD). Nếu giữ nguyên tốc độ thì khoảng 560 và 900 giờ/năm, xa mốc 4.000 (ước tính thô, một cửa sổ; điều kiện hiện hành xem trong Studio).

## 2. FS — chủ đề quyết định rất mạnh
Short mới (129 video), gom theo chủ đề:

| Chủ đề | n | Trung vị view | < 300 | > 1.200 | **Ở lại xem** (trung vị) | APV trung vị | Đăng ký | % view |
|---|---|---|---|---|---|---|---|---|
| **2027** | 5 | **14.579** | 0 | 4 | **50%** | **0,50** | 75 | **38,4%** |
| **Năm sinh + mệnh** ("1978, 1979: mệnh…") | 17 | **1.196** | 1 | 8 | **52%** | 0,32 | 23 | 13,5% |
| **Quan hệ con giáp** (tam hợp, lục hợp, xung, hồ sơ tuổi) | 20 | 1.041 | 1 | 4 | **43%** | **0,44** | 15 | 12,7% |
| Nhân tướng (chỉ tay, nốt ruồi) | 2 | 1.131 | 0 | 1 | 35% | 0,26 | 1 | 1,4% |
| Phong thủy nhà/vật | 7 | 992 | 2 | 0 | 29% | 0,24 | 12 | 3,3% |
| Can / Tài tinh / Bát tự | 11 | 864 | 1 | 0 | 22% | 0,19 | 3 | 5,2% |
| Lịch: giải thích hoàng/hắc đạo | 13 | 761 | 2 | 0 | 24% | 0,17 | 6 | 6,0% |
| Ngũ hành / âm dương | 7 | 733 | 3 | 0 | 19% | 0,16 | 3 | 2,6% |
| **Kinh Dịch** | 15 | 677 | **6** | 0 | **15%** | **0,13** | 6 | 5,5% |
| Lịch ngày ("dd/mm — …") | 17 | 557 | 5 | 0 | 22% | 0,29 | 6 | 5,9% |
| Chiêm tinh phương Tây (gồm "12 cung tử vi khác gì cung hoàng đạo") | 7 | 479 | 0 | 0 | 24% | 0,24 | 4 | 2,6% |
| Tử vi (sao, cung) | 8 | 412 | 3 | 0 | 21% | 0,16 | 1 | 2,8% |

Cột "Ở lại xem" (= "Viewed vs swiped away" / "Stayed to watch") lấy từ file xuất thứ hai của FS, xem mục 2b. Số view lấy theo file đó (lệch vài view so với file đầu).

- **42 video (33% sản lượng) thuộc 2027 + năm sinh + quan hệ con giáp mang về 65% lượt xem; 78 video (60%) thuộc 7 nhóm trừu tượng ở nửa dưới bảng chỉ mang về ~31%.**
- **2027:** "Tam Tai năm 2027 là những tuổi nào?" 25.906 view và "Năm 2027: 3 tuổi được xem là hợp nhất" (10 giây, APV 0,72) 14.587 view, cả hai trong ngày đăng 15/10 (số ngày cuối có thể chưa đủ). "Năm 2027 là năm con gì, mệnh gì?" là Short duy nhất được đẩy nhiều ngày liền (1.742 → 4.010 view/ngày từ 7/10 đến 12/10, rồi rơi còn 291 ngày 13/10), tổng 16.952. Nhưng "Năm 2027 tuổi nào làm nhà được?" chỉ 1.446 sau 2 ngày: **chủ đề 2027 không tự động nổ**; ba video nổ đều là câu hỏi chung cho cả năm, đáp án là một danh sách để người xem tự dò tuổi mình.
- **Năm sinh + mệnh:** gần nửa số video vượt 1.200; vài video có đợt thứ hai ở ngày 3–5 (1978-79: 312 view ngày 12/10; 1982-83: 188 và 153). Đây là chuỗi ổn định nhất ngoài 2027.
- **Kinh Dịch:** giữ chân thấp nhất (0,13) và **đổi hook sang câu hỏi không giúp** (6 video dạng câu hỏi trung vị 398, 9 video dạng tiêu đề nhãn trung vị 853). Sáu video liên tiếp về quẻ Kiền từ 1/10 đến 6/10 được lần lượt 983, 198, 159, 337, 853 và 14 view: 4/6 dưới 350, video cuối gần như không được phát. Chuỗi khuôn "Can Giáp/Ất/Bính: hợp, xung và nơi ẩn" tụt 1.024 → 394 → 279. Ngược lại, chuỗi khuôn năm sinh không tụt. → Khuôn lặp không tự bị phạt; khuôn lặp **của chủ đề giữ chân kém** thì được phát ít đi. Số "ở lại xem" (mục 2b) ủng hộ cách giải thích này: các video Kinh Dịch ít view có tỉ lệ ở lại 12–16%, tức feed dừng thử sớm vì người xem lướt qua.
- **Sửa lại nhận định trước:** dữ liệu tháng 7 (n=20, chỉ view) gợi ý "đóng gói quan trọng hơn chủ đề". Với FS, số liệu 28 ngày cho thấy **chủ đề quyết định rất mạnh** (trung vị 412 đến 14.587; APV 0,13 đến 0,50). Kinh Dịch, Tử vi sao/cung, chiêm tinh phương Tây đã có đủ mẫu (6–15 video) để kết luận là yếu trên kênh này.
- Thời lượng: video ≤ 24 giây có trung vị thấp hơn (676 so với ~1.000 ở 28–36 giây), nhưng lẫn với chủ đề (lịch ngày, con giáp thường 16–21 giây) và video 10 giây "3 tuổi hợp nhất" nổ lớn. Chưa kết luận.

## 2b. FS — "Ở lại xem" (Stayed to watch), số chính thức của Studio
File xuất thứ hai của FS (cùng cửa sổ) có thêm "Stayed to watch (%)" và "Engaged views". Toàn kênh: **39,3%** ở lại; 58.636 engaged views trên 162.042 views.

- **Giả định cần biết:** với Shorts, "Views" hiện đếm mỗi lần Short bắt đầu phát (kể cả lướt qua), còn "Engaged views" gần với cách đếm cũ. Tỉ lệ engaged/views của kênh (36%) sát với tỉ lệ ở lại (39%), nên tôi coi **Views ≈ số lần hiện trong feed**. Nếu Studio có cột "Shown in feed" thì nên đối chiếu một lần.
- **Ở lại xem quyết định việc vượt trần** (Short ≥ 3 ngày, n=114; Spearman với view 0,64):

  | Ở lại xem | n | Trung vị view | % video vượt 1.100 view |
  |---|---|---|---|
  | ≤ 25% | 52 | 518 | 0% |
  | 25–35% | 28 | 891 | 4% |
  | 35–45% | 12 | 1.053 | 25% |
  | 45–55% | 13 | 1.140 | **69%** |
  | > 55% | 9 | 1.196 | 56% |

  Ngưỡng thực tế để thoát trần ~1.000 view là **khoảng 45% ở lại**. Video dưới 300 view có trung vị chỉ 17% ở lại: chúng không phải "không được phát", mà được phát vài trăm lần, bị lướt qua, và feed dừng thử sớm.
- **Chủ đề quyết định tỉ lệ ở lại** (cột trong bảng mục 2): năm sinh 52%, 2027 50%, con giáp 43%; Kinh Dịch 15%, ngũ hành 19%, Tử vi 21%, lịch ngày 22%, Can 22%.
- **Kênh tăng từ ~20–28% (giữa tháng 9) lên 43–53% ở lại (từ 6/10)** theo bảng tổng theo ngày. Trung vị theo tuần đăng: 20% (18–24/9), 28% (25/9–1/10), 29% (2–8/10), **45%** (9–15/10). So từng nhóm trước và sau 4/10: con giáp tăng 35% → 45%, còn Kinh Dịch (14% → 16%), Can (22% → 23%), lịch ngày (19% → 22%) gần như không đổi. → Phần lớn mức tăng đến từ **đổi cơ cấu chủ đề** (thêm năm sinh, 2027, con giáp), không phải từ việc sửa hook cho nhóm yếu. (Commit "Short v2" ngày 4/10 có thể góp phần cho nhóm con giáp, nhưng không tách được.)
- Ngoại lệ đáng thử: trong 15 video Kinh Dịch, duy nhất "Trời trên Đất dưới lại là quẻ xấu?" (dạng nghịch lý) đạt 56% ở lại; các video khác 6–22%. Một điểm dữ liệu, chưa đủ kết luận.

## 3. BUD — chủ đề ít ảnh hưởng view, ảnh hưởng mạnh tới người đăng ký
Short đăng 17/9–11/10 (127 video):

| Chủ đề | n | Trung vị view | < 300 | Đăng ký / 1.000 view |
|---|---|---|---|---|
| **Giải mã biểu tượng, tượng, hộ pháp** | 21 | 932 | 5% | **4,9** |
| Thực hành (Chú Đại Bi, phóng sinh, hồi hướng, dâng cúng) | 9 | 1.149 | 11% | 2,6 |
| Địa ngục / tái sinh / niết bàn | 7 | 1.000 | 0% | 2,2 |
| Chùa / nghi lễ | 9 | 1.015 | 22% | 1,0 |
| Đời thường / tâm lý | **81 (64%)** | 911 | 15% | 1,2 |

- Ba video vượt 1.500: "Địa ngục có phải là bản án vĩnh viễn?" 2.517 (APV 0,41), "Câu đầu Chú Đại Bi thật ra nghĩa là gì?" 2.315 (APV 0,67), "Dâng đồ cúng vì nghĩ Phật đang đói sao?" 1.909.
- Nhóm "đời thường/tâm lý" chiếm 64% sản lượng và 11/16 video dưới 300 view; những video này mở bằng câu hỏi trừu tượng ("Biết đủ có phải là thôi cố gắng?", "Chánh niệm có phải là mặc kệ ngày mai?") và có APV 0,11–0,20.
- 134/141 tiêu đề kết thúc bằng dấu hỏi, thời lượng 21–34 giây, 5 video/ngày: rất đồng đều (tín hiệu "theo khuôn").
- 21 video "Vì sao tượng Phật…" là một công thức; kho đề tài hữu hạn, đẩy lên 3–4 video/ngày sẽ tăng rủi ro khuôn lặp.

## 4. Khuyến nghị cập nhật theo số liệu
**FS**
1. **Tăng 2027 dạng "câu hỏi chung cả năm, đáp án là danh sách tuổi"** (Tam Tai, tuổi hợp, Kim Lâu, xông đất, sao hạn theo năm sinh). Theo `SERIES_PROPOSAL_2027.md` S1–S5; ưu tiên câu hỏi mà mọi người xem đều tự dò được tuổi mình.
2. **Hoàn tất chuỗi năm sinh + mệnh** (17/30 cặp nạp âm đã làm) và thêm góc 2027. Giữ **quan hệ con giáp** (APV cao nhất ngoài 2027).
3. **Dừng** Kinh Dịch, Tử vi sao/cung, chiêm tinh phương Tây trong lịch thường. Kinh Dịch chỉ thử lại dạng "xin quẻ đầu năm" mùa Tết, tối đa 1 video/tuần. Can/Tài tinh chỉ giữ dạng theo năm sinh. **Thay khuyến nghị R6 cũ** (thử đóng gói lại 2 tuần): các nhóm này đã đủ mẫu.
4. **Lịch ngày dd/mm → 1 video gộp theo tuần**; giảm mạnh "giải thích hoàng/hắc đạo".
5. **Không xếp nhiều video cùng một đề tài liền nhau** (6 video quẻ Kiền trong 6 ngày): giãn cách theo lane như `hf_novelty.py`.

**BUD**
6. **Nâng "giải mã biểu tượng" và "thực hành"**; giảm "đời thường/tâm lý" từ 64% xuống khoảng 30%, chỉ giữ khi neo vào một cảnh cụ thể. Đa dạng công thức tiêu đề (không chỉ "Vì sao…?").
7. Mục tiêu giữ chân: APV ≥ 0,4 cho Short mới (hiện trung vị ~0,24).

**Chỉ số theo dõi hằng tuần (cả hai kênh):** "Stayed to watch" theo video và theo nhóm chủ đề. Mục tiêu ≥ 45% (ngưỡng vượt trần thấy ở FS); nhóm nào có trung vị dưới 25% sau 6 video thì dừng.

**Cả hai kênh**
8. **Video dài: sửa 2 phút đầu trước khi làm thêm.** Ưu tiên bản 6–15 phút theo tuổi/chủ đề có tìm kiếm (FS: video theo tuổi 2027 dài 6–8 phút đã có CTR 5,6–13%). Dừng lên lịch thêm video 30+ phút cho tới khi giữ chân cải thiện.
9. Giữ R1–R3 trong `RECOMMENDATIONS_2026-10.md` (dừng video lấp chỗ, quota theo lane, lưu metadata hook).

## 5. Còn thiếu
1. **BUD: "Stayed to watch" và "Engaged views" theo video** (xuất như FS) để kiểm ngưỡng ~45% và so các nhóm chủ đề. FS đã có (mục 2b).
2. Nguồn lưu lượng theo video cho ba Short 2027 (feed hay tìm kiếm) và cho video dài.
3. Đường giữ chân của video dài (rơi ở phút nào).
4. Số liệu 15/10 của FS có thể chưa xử lý xong; nên xuất lại sau 3 ngày để chốt số của hai Short 2027.
