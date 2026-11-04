# Thắng / thua tuần 26/10–01/11/2026 (MIM, CK) — bản dựng khi Studio chưa đọc được

Phạm vi: MIM (Mind in the Machine) và CK (Biểu Đồ Biết Nói). Không động tới CL. Chỉ đọc; không sửa video, lịch hay issue nào.
Đi cùng: `docs/pm/2026-11-02-plan-render-tuan-45.md`. Số thô và script nằm ở `output/analysis/week44/`.

## 0. Nguồn và giới hạn (đọc trước khi đọc kết luận)

| Nguồn | Dùng cho | Độ tin |
|---|---|---|
| `yt-dlp --flat-playlist` trên `/shorts` công khai, chạy 02/11 | tiêu đề, **lượt xem hiện tại** của 105 Short MIM và 61 Short CK | đo được. Từ 1.000 trở lên YouTube hiển thị làm tròn 0,1K: mọi giá trị ≥ 1.000 trong file đều chia hết cho 100 (vd. "1000" nghĩa là 1,00–1,05K) |
| `state.sqlite` (`item.publish_at`, `slug`, chỉ đọc) | giờ lên sóng, nối video id với spec | đo được. `publish_at` là giờ hẹn, giả định video lên đúng giờ |
| `data/stier/specs/*.json`, `output/stier/<slug>/timing.json` | câu mở, cảnh đầu, số từ, thời lượng giọng đọc | đo được. Chữ trên màn hình lấy từ spec, **chưa xem lại từng khung hình** |
| `data/analytics/{MIM,CK}/20261028*.json`, `output/webauto/studio/<UC>/2026-10-28/` | EVR (engagedViews/views), đường giữ chân, nguồn traffic, baseline Long | đo được nhưng **dừng ở 26–28/10**, không có Short đăng sau 26/10 |

**Không đo được tuần này (ghi rõ để khỏi suy diễn):**
- Không có CTR, hiển thị, "xem / lướt qua", % xem TB, sub, giờ xem cho tuần 26/10–01/11. Studio export hỏng (`docs/pm/2026-11-02-studio-tuan-44.md`).
- `yt-dlp -J` từng video thất bại cả 166 lần ("The page needs to be reloaded", bản yt-dlp 2025.05.22 đã cũ). Vì vậy **thiếu like, bình luận, thời lượng video, ngày đăng thật**. Ngày đăng lấy từ `publish_at`; thời lượng lấy từ `timing.json` (độ dài giọng đọc, ngắn hơn video khoảng 0,6 s).
- Tab `/videos` và playlist uploads trả 0 mục (Long đang riêng tư/hẹn giờ, hoặc yt-dlp không đọc được). **Không có số Long mới**; phần Long chỉ là baseline 28/10.
- Short đăng 01–02/11 mới 0,5–1,5 ngày tuổi: tốc độ đầu bị khuếch đại, không so thẳng với bài 9 ngày tuổi.
- Chuẩn hóa theo tuổi: chia bài theo nhóm tuổi (0–1,5 / 1,5–3 / 3–6 / 6–10 ngày), lấy **trung vị từng nhóm tuổi trong cùng kênh** làm mốc, rồi tính "lần so với trung vị nhóm". Cách này thô (nhóm nhỏ: CK chỉ có 2–7 bài mỗi nhóm). File: `output/analysis/week44/week_cohort_ratio.csv`.

## 1. Bức tranh chung (đo được)

| | MIM | CK |
|---|---|---|
| Short công khai đăng 24/10–01/11 | 43 bài, tổng 27.600 view | 16 bài, tổng 7.303 view |
| Trung vị view/bài (tuổi 1–9 ngày) | **718** (mốc 18–25/10: 713, `pilot-short-hook.md` mục 2) | **288,5** (mốc 21–25/10: 322; ngưỡng dừng thử 5 Short/ngày: 193) |
| Bài ≥ 990 view | 8 bài | 2 bài (1.000 và 1.100) |
| Bài lớn nhất | 1.000 (làm tròn) | 1.100 (làm tròn) |
| Trung vị thời lượng giọng (bài đến 31/10) | 25,9 s (21,3–34,4) | 33,0 s (26,5–37,6) |

- **Trần ~1.000 vẫn còn:** không bài nào của tuần vượt 1,0–1,1K, trong khi baseline 28/10 có bài 1,4K (MIM) và 3,2K (CK). Khớp với `so-that-bai.md` dòng 12–18/10.
- **Tốc độ đạt trần khác nhau (suy từ so sánh hai lô, chưa phải thí nghiệm):** lô Lee Sedol đăng 30/10 chạm 1.000 trong khoảng 2,5 ngày; lô AlphaGo đăng 24/10 sau 9 ngày vẫn 978/925/830.
- **CK chưa chạy thử 5 Short/ngày** (hàng chờ chỉ 1–2 bài/ngày), nên không áp được quy tắc dừng 193. Trung vị tuần 288,5 vẫn cao hơn 193 nhưng thấp hơn mốc 322.
- **Giờ đăng (có nhiễu chủ đề và tuổi):**
  - MIM theo giờ UTC (VN = +7): 23:30Z (06:30 VN) n = 8, trung vị **441,5**; 04:30Z (11:30 VN) n = 8, 552,5; 10:00Z n = 8, 787,5; 12:00Z n = 9, 807; 14:30Z n = 9, 800.
  - CK: 05:00Z (12:00 VN) n = 8, 272,5; 12:00Z (19:00 VN) n = 5, 271; 10:30Z n = 2, 768.
  - Khung 06:30 VN của MIM thấp rõ nhất, nhưng chưa tách được khỏi chủ đề. Chỉ là điểm cần kiểm, không phải kết luận.
- **Traffic (baseline 28/10, cấp kênh):** Shorts feed 95,6% (MIM), 97,1% (CK). Chưa có số tuần này.

## 2. Ba bài/cụm thắng

Mốc so sánh là trung vị cùng nhóm tuổi, cùng kênh (cột "lần").

### Thắng 1 — MIM: cụm Lee Sedol / lời trích có tên người (30/10 và 28/10)

| id | Slug | View (tuổi) | Lần so nhóm tuổi |
|---|---|---|---|
| FsESIVdXoaY | `mim-lee-sedol-giai-nghe-2019` | 1.000 (~2,5 ngày) | 1,34 |
| i_u1TVXhM3U | `mim-lee-sedol-khong-nhan-kem-hon` | 1.000 (~2,5 ngày) | 1,34 |
| qTajbrHY70s | `mim-master-60-van-thang` | 1.000 (~4 ngày) | 1,24 |

- **3 giây đầu (spec):**
  - FsES: "Ngày 19 tháng 11 năm 2019, Lee Sedol giải nghệ. Ông mới ba mươi sáu tuổi." Khung 0: chữ "19/11/2019 / LEE SEDOL GIẢI NGHỆ / ông mới 36 tuổi" trên clip Pexels 39262883, màn che 0,5.
  - i_u1: "Thua bốn trên năm ván. Và ông vẫn không chịu nhận mình kém hơn." Khung 0: "THUA 4 TRÊN 5 VÁN / VẪN KHÔNG NHẬN KÉM HƠN" trên clip 39474349.
  - qTaj: "Sáu mươi ván thắng liên tiếp. Không thua ván nào." Khung 0: "60 VÁN THẮNG LIÊN TIẾP".
- **Tiêu đề:** FsES dùng lời trích ("Có một thực thể không thể bị đánh bại": vì sao Lee Sedol giải nghệ năm 2019); i_u1 cũng lời trích của chính nhân vật ("Thua 1–4, Lee Sedol vẫn nói: …").
- **Loại bài:** FsES là L (mô tả dẫn tới Long `nbNu6xYtoYg`); thời lượng giọng 29,8 s. Chủ đề: người–máy.
- **Cơ chế (đo + suy):**
  - *Đo:* cả 21 Short AlphaGo/Lee Sedol của tuần có trung vị 830 view, cao nhất trong 3 cụm MIM (AI bịa 591, AI giọng/lừa đảo 649; phân cụm bằng regex trên slug, `week_classified.json`). Bài đứng đầu đều có **tên người nhận ra được** và **một kết quả đảo kỳ vọng** (giải nghệ vì máy; thua 1–4 mà vẫn không nhận kém hơn).
  - *Suy đoán:* người xem dừng lại vì câu mở là một mâu thuẫn người thật nói ra, không phải vì kiểu chữ. Mâu thuẫn được giải ở giây 20–30, nên giữ tới cuối.
  - *Không rút ra được:* tại sao cụm 24/10 chậm hơn. Cùng chủ đề, chủ đề không giải thích được; chưa tách khỏi giờ đăng (24/10 có nhiều bài ở 04:30Z) và độ tuổi dữ liệu.
- **Long đi kèm (baseline 28/10):** `nbNu6xYtoYg` 45 view, 1.616 hiển thị, CTR 1,24%. Một Short chạm 1.000 view gần như không chuyển sang Long (lượt từ Short sang Long = 0 theo `pilot-short-hook.md` mục 2).

### Thắng 2 — CK: hai khoản tiền đối nghịch trên cùng một vật (cụm mua/thuê nhà, 24–30/10)

| id | Slug | View (tuổi) | Lần so nhóm tuổi |
|---|---|---|---|
| Rj9NAGSMP34 | `ck-hai-nam-dau-lai-vay-va-tien-thue` | 929 (~9 ngày) | **5,08** (nhóm 6–10 ngày, trung vị 183) |
| dSuFp1rtMrU | `ck-mot-ty-tra-truoc-co-gia` | 692 (~8 ngày) | 3,78 |
| LbsJhmTZA9s | `ck-tien-thue-tang-5-phan-tram` | 1.000 (~2,6 ngày) | 1,95 |

- **3 giây đầu:**
  - Rj9N: "Ba trăm mười bảy triệu, và một trăm năm mươi tư triệu. Đó là hai năm đầu của hai căn hộ giống hệt nhau." Khung 0: "317 TRIỆU ↔ 154 TRIỆU / hai năm đầu · hai căn hộ giống hệt" trên clip Pexels 7647330.
  - LbsJ: "Sáu triệu hai hôm nay, mười năm nữa thành gần chín triệu bảy." Khung 0: "6,2 → 9,7 TRIỆU".
- **Tiêu đề:** dài 85–100 ký tự, có "(ví dụ giả định)", ví dụ "Hai năm đầu mua nhà: 317 triệu tiền lãi vay, so với 154 triệu tiền thuê căn y hệt (ví dụ giả định)".
- **Loại bài:** Short phục vụ Long B1 `pXKfIo_nyVM` (công khai 30/10). Thời lượng giọng 32,4 s.
- **Cơ chế (đo + suy):**
  - *Đo:* 7 Short nhà ở có trung vị 692, cao hơn nhóm "tâm lý / vàng / VN-Index" (239) và quỹ khẩn cấp (236). Trong CK tuần này, bài có **chữ số ngay câu đầu** (6/14, bài đến 31/10) trung vị 701,5, so với 211 ở 8 bài còn lại. n nhỏ, cùng chiều với `so-that-bai.md` ("một con số tiền cụ thể so với một mốc") và baseline 28/10.
  - *Đo, đối chứng trong cùng chủ đề:* `ck-chi-phi-ngoai-gia-nha` (liệt kê bốn khoản phí, không có hai số đối nghịch) chỉ 80 view ở ~7 ngày (0,44 lần); `ck-hoa-von-7-phan-tram` (một tỷ lệ trừu tượng) 474 ở 3–6 ngày (0,78 lần).
  - *Suy đoán:* chủ đề "mua hay thuê" có nhu cầu tự nhiên, nhưng chính **hai số tiền cạnh nhau, cùng đơn vị, cùng một vật** mới tạo khoảng trống tò mò. Chưa có số "xem / lướt qua" để xác nhận.
- Tiêu đề dài không hại ở CK (tương quan thứ hạng giữa độ dài tiêu đề và view +0,33, n = 14), trái chiều với MIM (−0,28, n = 38): **không có hiệu ứng độ dài tiêu đề nhất quán**, đừng rút gọn vì lý do này.

### Thắng 3 — MIM: lời nói thật của người trong cuộc (cụm luật sư ChatGPT, 01/11) — còn sớm

| id | Slug | View (tuổi) | Lần so nhóm tuổi (0–1,5 ngày, trung vị 332) |
|---|---|---|---|
| rU201Iz57x4 | `mim-sieu-cong-cu-tim-kiem` | 792 (~1 ngày) | 2,39 |
| fRkD4rUoOtI | `mim-hoi-lai-chinh-may` | 759 (~1 ngày) | 2,29 |
| KbVrwi8hCGo | `mim-phat-5000-do-va-nhung-la-thu` | 718 (~1 ngày) | 2,16 |

- **3 giây đầu:** "Tôi đã lầm tưởng nó giống như một siêu công cụ tìm kiếm." (lời một luật sư ở New York, phiên điều trần 06/2023). Khung 0: "“MỘT SIÊU CÔNG CỤ TÌM KIẾM” / trích dịch lời luật sư · 06/2023". Thời lượng giọng 25,3 s.
- **Cơ chế (suy đoán, chưa đủ tuổi để kết luận):** câu mở là lời trích ngôi thứ nhất của người từng mắc lỗi; đối chiếu `mim-sau-vu-an-khong-co-that` (cùng vụ, mở bằng mô tả "Sáu vụ án … không vụ nào có thật") chỉ 94 view ở ~1 ngày, nhưng bài đó lên 06:30 VN, nên không so được sạch. **Phải đo lại ở 72 giờ và 7 ngày** trước khi dùng làm cơ sở.
- Bài phụ đáng ghi nhận: CK `ck-3-khoan-tra-them-vang` 1.100 view (~5 ngày, 1,81 lần): "Mua đúng đỉnh một chỉ vàng … hết hơn mười chín triệu. Đầu tháng mười bán lại, nhận hơn mười bốn triệu." Đây là định dạng cũ (không có `mix`), nên **chuẩn mix không phải điều kiện cần cho thắng**; điều kiện chung vẫn là hai số tiền đối nghịch.

## 3. Ba bài/cụm thua

### Thua 1 — CK: chùm "Chứng khoán từ số 0" (C2, 31/10–02/11)

| id | Slug | View (tuổi) |
|---|---|---|
| oMpHxkUSfJg | `ck-c2-ban-dung-gia-van-lo` | 28 (~2,5 ngày) |
| ZxgMF_29zzk | `ck-c2-muon-ban-khong-ban-duoc` | 111 (~1,3 ngày) |
| aHFuP-WRmUw | `ck-c2-dat-cao-tra-thap` | 36 (<1 ngày) |

- **3 giây đầu:** "Bán đúng giá mua, bạn vẫn lỗ." / "Thứ Hai, chín tháng ba, VN-Index mất một trăm mười lăm điểm." / "Đặt mua giá cao, lại trả giá thấp." Khung 0 của ZxgM: "VN-INDEX · THỨ HAI 09/03/2026 / −115 / ĐIỂM", không clip, `mix` trống (định dạng cũ). Chủ đề: cách thị trường vận hành. Thời lượng giọng 26–33 s.
- **Cơ chế (đo + suy):**
  - *Đo:* trung vị cụm 36 view; cả ba đều dưới nhóm tuổi tương ứng. Cùng nhóm "đọc thị trường chung" mà `so-that-bai.md` (12–18/10) đã ghi là yếu trên CK và quyết định dừng.
  - *Suy đoán:* hook là giải thích cơ chế ("khớp lệnh thế nào?"), không có khoản tiền của người xem hay hai số đối nghịch; khung đầu không có hình động. Không tách được hai yếu tố này (chủ đề vs. dựng) vì chưa có bài C2 nào dựng theo kiểu thắng.
- **Việc cần chú ý:** hàng chờ CK vẫn còn 3 Short C2 (03/11 `ck-c2-mua-thu-nam-thu-sau`, 04/11 `ck-c2-mot-lo-bao-nhieu`, 05/11 `ck-c2-ban-lo-van-nop-thue`). Chỉ nêu, không đổi lịch.

### Thua 2 — MIM: nhân vật chỉ gọi bằng vai trò (28/10–31/10)

| id | Slug | View (tuổi) | Lần so nhóm |
|---|---|---|---|
| LrXupeaJRoQ | `mim-nghiep-du-thang-may-14-15` | **22** (~2,5 ngày) | 0,03 |
| sxvBflhOkEk | `mim-kha-khiet-0-3` | 180 (~5 ngày) | 0,22 |
| CfKp3Bnqflw | `mim-bo-xac-thuc-giong-noi` | 121 (~7 ngày) | 0,18 |
| FoIr9hw0w10 | `mim-sau-vu-an-khong-co-that` | 94 (~1 ngày, 06:30 VN) | 0,28 |

- **3 giây đầu:** "Mười bốn trên mười lăm ván. Một người chơi nghiệp dư, thắng cỗ máy cờ vây hàng đầu." / "Kỳ thủ số một thế giới từng nói: cỗ máy này không thắng nổi tôi." / "Mười lăm giây giọng mẫu. Và một lời khuyên lạ, từ chính nơi làm ra cỗ máy." / "Sáu vụ án được nộp lên toà án liên bang Mỹ …".
- **Cơ chế (đo + suy):**
  - *Đo:* cả bốn đều **không nêu tên** nhân vật chính trong câu mở ("kỳ thủ nghiệp dư", "kỳ thủ số một", "nơi làm ra cỗ máy", "một văn phòng luật"), trái với ba bài thắng nêu tên (Lee Sedol, Master) hoặc lời nói ngôi thứ nhất. Có cùng chủ đề với bài thắng (AlphaGo, giọng giả), nên chủ đề không giải thích được.
  - *Đo, hạn chế:* LrXu (22 view) thấp hơn trung vị nhóm ~30 lần; chênh quá lớn để chỉ do hook. **Cần kiểm cột Hạn chế (Restrictions) và tỷ lệ view từ Shorts feed** trước khi gán nguyên nhân (bước 0 của `pilot-short-hook.md` mục 6). Chưa đọc được.
  - *Suy đoán:* "người không tên làm chuyện lạ" không đủ điểm bám để người xem nhận ra mình đang xem chuyện gì trong 1 giây.
  - Nhiễu: FoIr lên 06:30 VN (khung yếu của tuần, mục 1).

### Thua 3 — CK: hook khái niệm hoặc danh sách, không có số tiền đối nghịch (24–28/10)

| id | Slug | View (tuổi) | Lần so nhóm |
|---|---|---|---|
| 8Dol9ofPRfo | `ck-chi-phi-ngoai-gia-nha` | 80 (~7 ngày) | 0,44 |
| N7GUOQqYeEg | `ck-fomo-den-khi-gia-cao` | 239 (~4 ngày) | 0,39 |
| L6_kopRn8OA | `ck-barber-odean-su-chu-y` | 183 (~9 ngày) | 1,00 (nhóm 6–10 ngày trung vị 183) |

- **3 giây đầu:** "Mua một căn hộ, bạn không chỉ trả đúng con số ghi trên hợp đồng." / "Nỗi sợ bị bỏ lỡ không bao giờ đến khi thị trường đang rẻ." / "Người ta thường mua thứ đang được nhắc tới nhiều nhất. Có hẳn một nghiên cứu về chuyện này."
- **Cơ chế (đo + suy):** cả ba mở bằng nhận định chung, số đầu tiên chỉ xuất hiện ở câu 2 ("không phẩy năm phần trăm"). *Đo:* nhóm tâm lý/vàng/VN-Index trung vị 239; tương quan hạng giữa số chữ số trong kịch bản và view là **âm** ở cả hai kênh (CK −0,40, n = 26; MIM −0,26, n = 49, baseline 28/10): nhiều số rải đều không giúp, **một cặp số đặt ở khung đầu mới giúp**. *Suy đoán:* hai điều trên không mâu thuẫn, nhưng chưa tách bằng thí nghiệm.

## 4. Cơ chế rút ra (số đo và suy đoán tách riêng)

| # | Phát biểu | Loại | Bằng chứng |
|---|---|---|---|
| 1 | Hook thắng khi nêu **một mâu thuẫn cụ thể ở khung đầu**: hai khoản tiền đối nghịch (CK), hoặc người có tên nói điều trái kết quả (MIM) | Đo (tương quan, n nhỏ) + suy | Thắng 1–3, đối chứng Thua 2–3; CK có số ở câu đầu 701,5 vs 211 |
| 2 | Nhân vật có tên hoặc lời trích ngôi thứ nhất thắng nhân vật gọi bằng vai trò | Đo (so sánh trong cùng chủ đề, n = 4 vs 3) | Thua 2 vs Thắng 1, 3 |
| 3 | "Mua hay thuê nhà" là chủ đề tốt hơn "thị trường chứng khoán chung" trên CK | Đo (cụm 692 vs 239/36); nhắc lại sổ thất bại | Thắng 2, Thua 1, `so-that-bai.md` |
| 4 | Trần ~1.000 view chưa phá được; số lượng không đổi trần | Đo (không bài nào vượt 1,0–1,1K) | mục 1, `so-that-bai.md` 12–18/10 |
| 5 | Giữ chân sớm và "ở lại xem" có liên quan tới view | Đo (Spearman, baseline 28/10): view với EVR 0,32 (MIM, n = 49) và 0,38 (CK, n = 26); với giữ chân ở 10% video 0,27 và 0,30 | `output/analysis/week44/baseline_curve_rows.json` |
| 6 | Độ dài giọng đọc và độ dài tiêu đề **không** là yếu tố nhất quán | Đo (|ρ| ≤ 0,3, đổi dấu giữa hai kênh) | mục 2–3 |
| 7 | Khung giờ 06:30 VN của MIM yếu | Đo thô, có nhiễu | mục 1 |
| 8 | Người xem dừng vì chữ trên màn hình đầu tiên, không phải kiểu hiệu ứng chữ | **Suy đoán**; không có thí nghiệm hay "xem / lướt qua" | Thua 1–3 có hiệu ứng chữ giống thắng |
| 9 | Hook mâu thuẫn **tăng tốc**, không nâng trần | Suy (so hai lô, mục 1) | Thắng 1 |

## 5. Khoảng trống số liệu và việc cần chờ (không đổi ngưỡng để hợp thức hoá)

| Thiếu | Ảnh hưởng | Lấy thế nào |
|---|---|---|
| CTR, hiển thị, "xem / lướt qua" của Short tuần này | Không biết hook thắng nhờ lướt hay nhờ xem lại | Studio khi export chạy lại (issue #16) |
| Cột Hạn chế của `mim-nghiep-du-thang-may-14-15` (22 view), `ck-c2-*` | Có thể một phần "thua" là phân phối | Đọc tay trong Studio |
| Like, bình luận, thời lượng video thật | Không chấm được tương tác | Nâng `yt-dlp` hoặc dùng Analytics API (kênh đã có token; không đọc ở đây) |
| Long tuần này (24h/72h/7d, CTR 2%, AVD 3:00 của #15) | Chưa biết Long mới của MIM/CK có phá được vách hiển thị không | Chạy `collect --periods 7d` đúng mốc, sau khi khôi phục export |
| Short 01–02/11 mới 0,5–1,5 ngày tuổi | Thắng 3 chưa chắc | Đọc lại 03/11 (72 h) và 08/11 (7 ngày) |

**Baseline Long còn dùng được (28/10, `docs/pm/2026-11-02-studio-tuan-44.md` mục 4):** CTR là nút thắt, AVD không (13/15 Long ước tính ≥ 3:00; 5/15 đạt CTR ≥ 2%). Long 7d: MIM 8 video 790 view, CK 8 video 138 view. Không có số mới.

## 6. Hệ quả cho kế hoạch tuần 45

- Hook ở khung đầu phải có **mâu thuẫn cụ thể**: hai số tiền cạnh nhau (CK) hoặc người có tên + điều trái kết quả (MIM).
- Không thêm Short chứng khoán chung hay giải thích cơ chế cho CK; không dùng nhân vật vô danh ở câu mở của MIM.
- Mọi kết luận ở mục 4 là giả thuyết cho tuần 45, đo lại bằng mốc 24h/72h/7d (xem plan).
