# BUD + FS: nghiên cứu số liệu 28 ngày (15/10–11/11/2026)

Issue #327 (kèm bình luận bổ sung FS). Báo cáo trả lời 13 câu hỏi (7 BUD, 6 FS), danh sách thử nghiệm và đề xuất sửa 3 skill.
Ngày viết: 13/11/2026. Chỉ đọc dữ liệu có sẵn trong repo; không gọi YouTube API, không đăng nhập.

## 0. Cập nhật quyết định chủ kênh 13/11

- Mỗi kênh mỗi tuần giữ **2 Long dài ≥ 30 phút**. **1–2 Long còn lại được làm dạng ngắn 5–8 phút** (một tuổi / một chủ đề) để pilot.
  Mục này không còn là "chờ quyết định". Đề xuất cụ thể nằm ở §3 (Q10), §4 (Q10 BUD) và thử nghiệm E10, E11.
  Quyết định 21–22/10 "giữ ≥ 30 phút" vẫn đúng cho 2 suất dài; suất ngắn là phần được mở thêm.
- Chủ kênh đã đồng ý gắn "Video liên quan" từ Short > 100 nghìn lượt xem sang Long cùng chủ đề (Q6, Q11).

## 1. Nguồn dữ liệu và giới hạn (đọc trước)

Dữ liệu dùng:
- Số trong issue #327 và bình luận (YouTube Studio, chủ kênh gửi 13/11).
- `output/webauto/studio_v2/<kênh>/2026-11-11/videos.csv` (xuất `webauto studio collect`, 28 ngày tới 11/11). Đối chiếu từng video.
  Số trong CSV lệch nhẹ so với issue (ví dụ Short Kim Lâu 345.037 so với 352,4 nghìn) vì khác thời điểm xuất. Khi lệch, báo cáo ghi rõ nguồn.
- `output/cl_staging/long/retention_ledger.json` (đường giữ chân tới 21/10, 8 Long BUD và 10 Long FS; chưa có Long mới nhất).
- `output/cl_staging/long/audit_dong_goi_2026-10-30.md` (có đường giữ chân 36s/54s/90s của Trần Nhân Tông, mẫu 84 lượt xem).
- `docs/research/thumb_ctr/report.md` (11/11), `phan_tich_long_2026-10-21.md`, `phan_tich_fs_long_thang_2026-10-28.md`.
- Plan và `out/<id>.json` (mốc thời gian TTS) của các Long.

**Khoảng trống dữ liệu (không bịa):**
1. Không có đường giữ chân theo giây cho từng Long BUD mới (Tây Du Ký, Tiền Thân tập 4). Chỉ có hai con số từ issue (94% rồi 56% ở giây 54 của Tây Du Ký) và đường của Trần Nhân Tông từ audit 30/10.
2. Không có số "Shorts liên quan → Long" cho BUD; FS chỉ có con số tổng 325 lượt trong issue.
3. Impressions và CTR của Short gần như vô nghĩa trong CSV (Short xem chủ yếu từ feed, ví dụ câu thứ sáu Chú Đại Bi có 3.458 lượt xem mà chỉ 121 impressions). Không dùng CTR để xếp Short.
4. Mẫu Long nhỏ: Long BUD tốt nhất 626 lượt xem trong 28 ngày. Mọi so sánh Long dưới đây là gợi ý, chưa phải kết luận.
5. "Ở lại xem" (stayed to watch) của từng Short BUD không có trong CSV (cột có nhưng để trống). Chỉ có số kênh (30,3%) từ issue.
6. 5 Long tốt nhất so với 5 Long kém nhất cho Q3: không dựng được đủ. Xem §3 Q3.

## 2. Tóm tắt số liệu chính (đối chiếu)

| Chỉ số | BUD | FS |
|---|---|---|
| Lượt xem 28 ngày | 101.989 (−15,2%) | 3,79 triệu (+3.094%) |
| Đăng ký mới | +472 (4,6 / 1.000 lượt xem) | +2.045 (0,54 / 1.000 lượt xem) |
| Shorts | 99.027 lượt xem; ở lại xem 30,3% | 99,7% lượt xem; ở lại xem 63–68% (video 10s) |
| Long | 2.824 lượt xem; xem TB 7:06; CTR 3,35% | 10.234 lượt xem; xem TB 5:01; CTR 6,9% |
| Hiển thị Long theo nguồn | Đề xuất: 72% hiển thị, CTR 2,78% | Tìm kiếm CTR 9,7%; đề xuất 16,5% lượt xem nhưng 32,4% giờ xem |

Nhận xét kèm (tự tính từ CSV BUD): 277 Short BUD có lượt xem trong kỳ, **trung vị chỉ 40 lượt xem**, trung vị AVP 67,5%. Lượt xem tập trung vào vài video đầu bảng. Nghĩa là "chuỗi Đại Bi" và vài Short biểu tượng là phần thắng, còn lại là đuôi dài gần như không ai xem.
Trung vị CTR của 59 Long BUD (≥ 500 impressions) là 2,84%, nên 2,78% của nguồn đề xuất không tách khỏi mặt bằng kênh.

---

## 3. BUD: 7 câu hỏi

### Q1. Short, 3 giây đầu (70% lướt qua)

**Bằng chứng.**
- Short BUD giữ chân cao nhất đều là câu hỏi có đáp án cụ thể đưa ra ngay trong tiêu đề: "Đức Phật mỗi ngày ăn mấy bữa?" (AVP 134,9%), "Đức Phật dạy ngủ mấy tiếng mỗi đêm?" (139,0%), "Đứng xin cơm giữa mùa cày, Đức Phật bị nói gì?" (165,6%), "Câu thứ sáu Chú Đại Bi nghĩa là gì?" (170,8%). Theo issue, "Tam thế Phật là gì?" đạt 286,6%.
- Trong `shorts-lookup` §1, công thức thắng đã nêu: câu hỏi tìm kiếm + chi tiết lạ + khung dừng/lật. BUD chưa áp phần "dừng/lật" ở khuôn chuỗi.
- Giới hạn: nhóm có "ở lại xem" 30,3% là trung bình cả kênh, trong đó phần đuôi dài kéo xuống. Không có số "ở lại xem" riêng cho từng video nên không biết top Short có "ở lại xem" cao hơn bao nhiêu.

**Đề xuất khuôn mở (giữ AVP > 100%).** Chỉ đổi hình thức giây 0–3, giữ nguyên thân video:
1. **Câu hỏi trọng tâm hiện trên màn hình ở giây 0** (chữ lớn, ≥ 90 px, một dòng), giọng đọc nói **chính câu ấy** ở giây 0, không chào, không nhạc dạo.
2. **Hình thật có chi tiết lạ ngay khung đầu** (tượng/phù điêu/bát khất thực), không màn đen.
3. **Tiếng chuông xoay ở giây 0** (đã có trong `shorts-lookup` §6), không để im lặng.
4. Không đưa đáp án ở giây 0–3 (mất lý do ở lại); đưa tín hiệu "đáp án có số/có tên" ("Có ba ý. Ý thứ hai ít ai biết."). Câu này là giả thuyết, cần đo (E1).

### Q2. Chuỗi giải nghĩa kinh chú

**Bằng chứng từ CSV (28 ngày).**

| Tập | Ngày đăng | Lượt xem | AVP | Đăng ký |
|---|---|---|---|---|
| Câu thứ sáu | 01/11 | 3.458 | 170,8% | 22 |
| Câu thứ tư | 30/10 | 1.058 | 107,6% | 4 |
| Câu thứ hai | 25/10 | 1.054 | 158,7% | 6 |
| Câu thứ năm | 31/10 | 982 | 170,7% | 10 |
| Câu thứ ba | 29/10 | 671 | 260,3% | 9 |
| Câu thứ chín | 03/11 | 326 | 83,8% | 1 |
| Câu thứ bảy | 02/11 | 294 | 62,8% | 4 |
| Câu thứ tám | 03/11 | 55 | 239,0% | 1 |

Nhận xét:
- AVP cao **không** kéo theo lượt xem cao: câu thứ tám có AVP 239% nhưng chỉ 55 lượt xem. Giữ chân tốt chỉ chứng tỏ video đủ hay với người đã xem, không chứng tỏ được phân phối.
- Lượt xem **giảm dần từ câu thứ sáu xuống câu thứ chín**, khớp với quyết định PO 09/11 dừng nối "Câu thứ N". Câu thứ sáu là ngoại lệ có thể do thuật toán đẩy (22 đăng ký).
- Phụ thuộc vào số thứ tự khiến người mới xem câu 6 không hiểu câu 1–5. Tiêu đề "Câu thứ N" không phải câu hỏi tìm kiếm.

**Những chuỗi tương tự có thể làm** (mỗi chuỗi một nguồn kiểm được; nhãn truyền thống ghi rõ):

| Chuỗi | Mỗi tập | Nguồn / nhãn |
|---|---|---|
| Tâm Kinh (Bát-nhã) từng câu | Một câu 8–12 chữ | Kinh Bắc truyền (Hán tạng, bản Huyền Trang dịch). **Nhãn: Đại thừa, không phải lời Phật trong kinh tạng Pali.** |
| Mười danh hiệu Phật (Như Lai, Ứng Cúng, Chánh Biến Tri...) | Một danh hiệu | Kinh tạng Pali (công thức Phật hiệu lặp trong Trường Bộ, Tăng Chi); đối chiếu `hf_sutta.py` từng cụm. |
| Kệ Pháp Cú ngắn | Một kệ | Kinh Pháp Cú (có số kệ). |
| Tam quy / Ngũ giới | Một điều | Khuddakapāṭha; Tăng Chi. Đối chiếu `hf_sutta.py`. |
| Bài kệ Tứ Vô Lượng Tâm | Một tâm | Pali: Tăng Chi và Trường Bộ. |

**Lịch đăng để người xem tìm được tập kế:**
- Tiêu đề đứng một mình như câu hỏi tìm kiếm ("Phật hiệu Thiện Thệ nghĩa là gì?"), **không dùng "Câu thứ N"**; số thứ tự để ở phụ đề và mô tả.
- Mỗi chuỗi một playlist; Short cuối kết bằng câu mời bằng lời ("Danh hiệu tiếp theo: ...") và comment ghim có link video kế.
- Mỗi chuỗi đăng không quá 1 tập/ngày và tối đa 5 tập liên tiếp, rồi cách vài ngày (tránh dồn như Đại Bi 25/10 tới 03/11).
- Đo bằng E2: lượt xem tập N+1 chia cho tập N.

### Q3. Long, 60 giây đầu (mất 30–45%)

**Dữ liệu có thật (và thiếu).** Chỉ có đường giữ chân theo giây cho:
- Trần Nhân Tông (audit 30/10, mẫu 84 lượt xem): khoảng 79% ở giây 36, 72% ở giây 54, 60% ở giây 90.
- Tây Du Ký (issue): 94% rồi 56% ở giây 54.
- Tám Long BUD đến 21/10 (ledger, giữ chân phút 1 và phút 2): xem bảng dưới. Các Long mới hơn (Tiền Thân tập 4, Tây Du Ký) chưa có trong ledger.

Vì vậy **không dựng được so sánh "5 tốt nhất với 5 kém nhất" theo giữ chân 60 giây đầu**. Dưới đây là so sánh trung thực: lời mở thật của 3 Long mạnh (theo giờ xem/AVP) với 2 Long yếu nhất trong ledger.

| Long | View 28 ngày (CSV) | AVP | Giữ phút 1 / phút 2 (ledger 21/10) |
|---|---|---|---|
| Luật Nhân Quả (30 phút) | 626 | 22,8% | 65,5% / 51,1% |
| Tây Du Ký Ngoài Đời Thật | 586 | 30,1% | (không có trong ledger) |
| Trần Nhân Tông | 304 | 28,1% | khoảng 72% ở giây 54 (audit) |
| Tiền Thân tập 4 | 177 | 31,8% | (không có) |
| Khi Mọi Chuyện Không Như Ý (6 phút, rất ít view) | | | 45,8% / 29,2% (25 lượt xem) |
| Khi Bị Người Khác Làm Tổn Thương (6 phút) | | | 30,0% / 10,0% (54 lượt xem) |

**Lời mở thật (15 câu đầu, trích từ plan trên đĩa).**

*Tây Du Ký (L_bud_22, thời gian từ `out/L_bud_22.json`):*
- 0–10 s: cảnh chùa làng năm giờ sáng, bà Tư tụng Tâm Kinh.
- 18 s: "Người dịch bài kinh ấy sang chữ Hán, chính là Đường Tăng." (nhân vật chính xuất hiện).
- 38 s: cảnh sa mạc, túi nước đổ sạch (căng nhất, tới giây 38 mới tới).
- 48–57 s: ông nằm xuống cát, ngựa không đứng dậy. **Giây 54 nằm đúng trong câu này.**
- 58 s: ba câu hỏi lớn; 69 s: lộ trình ba chặng; 80 s: câu nguồn tư liệu (phần lớn người xem đã đi hoặc đã ở lại).

*Trần Nhân Tông (L_bud_24):*
- 0–17 s: đêm 1/11/1308, đỉnh Ngọa Vân; vị sư già hỏi giờ; "chính là giờ ta đi" (cảnh căng nhất ở giây 0).
- Khoảng 37 s: lộ tên nhân vật; câu hỏi lớn; lộ trình ba chặng; câu nguồn.
- Sau đó là chuyển sang chị Thảo và con trai leo núi (nhân vật hư cấu minh họa).

*Tiền Thân tập 4 (L_bud_tt04):*
- Câu 1: nước dựng thành vách giữa biển, tiếng gầm. Câu 6: người mù bước ra. Câu 9: "ông chưa đọc câu nào trong bát". Cảnh căng ngay câu đầu, dừng ở đỉnh.

*Hai Long yếu (L_bud_01, L_bud_02):*
- "Có những giai đoạn, mọi thứ đều lệch khỏi dự tính của mình." (lời nhận định chung), câu 3 đã là "Video này là năm điều...", không có cảnh, không có nhân vật.

**Đọc kết quả (nêu rõ mức chắc):**
1. Long có cold open dạng cảnh có người và thời điểm (Tây Du Ký, Trần Nhân Tông, Tiền Thân 4) có AVP 28–32%, cao hơn trung vị Long BUD 22,7% (audit 30/10). Long mở bằng lời nhận định chung rơi từ phút đầu. Nhưng đây là so sánh khác độ dài và khác chủ đề (6 phút so với 30 phút), nên **chỉ là gợi ý**.
2. Ngay cả Long mở bằng cảnh vẫn mất 30–45% trong 60 giây. Cảnh mở của Tây Du Ký mất 18 giây (chùa làng) trước khi nhân vật chính xuất hiện và 38 giây trước khi tới cảnh căng nhất. Giả thuyết hợp lý: **mở bằng cảnh gián tiếp (người thứ ba) rồi mới tới nhân vật tốn thời gian**. Chưa chứng minh được; cần đường giữ chân theo giây của Long này.
3. Audit 30/10 ghi nhận thêm: hình 60 giây đầu của Trần Nhân Tông hơn một nửa là chữ trên nền trống và nhân vật chính không xuất hiện, lệch đêm với ngày. Lời mạnh nhưng hình không kể lại.

**Khuôn mở đề xuất ("10–15 giây kịch tính"):**

| Giây | Nội dung | Luật |
|---|---|---|
| 0–10 | Một câu cảnh cụ thể ở **đỉnh** của nhân vật chính (có tên hoặc "một người", có thời điểm/địa điểm), thì hiện tại, dừng giữa hành động | Không chào; không cảnh người thứ ba; hình **vẽ cảnh đó** (nhân vật xuất hiện trong 5 giây đầu) |
| 10–15 | Một câu **đặt cược**: điều gì có thể mất ("nếu ông gục xuống đây, bản kinh sẽ không bao giờ về") hoặc nghịch lý | Chưa giải thích; không "Video này sẽ..." |
| 15–35 | Quay về nhân vật thật + câu hỏi chính (2–3 câu, hẹn chương) | Giữ khuôn nhân vật của `long-script` |
| 35–75 | Lộ trình 1 hình thức; câu nguồn **đẩy xuống sau 90 giây** hoặc nhét vào mô tả | Câu "dựa trên tiểu sử..." hiện đang ở giây 80–92 của Tây Du Ký; dời nó vào chương 1 |

Với nhân vật BUD, mọi chi tiết cảnh phải có trong nguồn; chi tiết linh ứng gắn "theo chú giải kể" hay "theo truyền thuyết" (luật `long-script`, khuôn nhân vật mục 3 và 7).

### Q4. CTR từ đề xuất 2,78%

**Bằng chứng.**
- 72% hiển thị Long BUD nằm ở nguồn đề xuất, CTR 2,78%; trung vị CTR 59 Long BUD là 2,84% (CSV). Nguồn đề xuất có CTR thấp hơn browse là bình thường; **2,78% chưa phải lỗi thumbnail**.
- Audit 30/10 ghi nhận CTR Trần Nhân Tông (2,93%) ngang trung vị Long BUD (3,00%).
- Báo cáo `thumb_ctr` (11/11): 13 Long BUD nằm gọn trong 2,0–4,1%, tín hiệu duy nhất là tên riêng quen (Đường Tăng 4,11%). **Luật L1–L4 của FS không áp sang BUD.**
- **Ứng viên A/B rõ nhất:** Tiền Thân tập 4 có **AVP cao nhất nhóm (31,8%) mà CTR thấp nhất (2,0%)** với 4.790 impressions. Nghĩa là người đã bấm thì xem tốt, nhưng ít người bấm: nghẽn nằm ở đóng gói, không ở nội dung. Khớp ghi nhận của #97 ("nghẽn ở đóng gói").

**Kiểm độ tương phản và số chữ trước khi thử (quy trình làm tay, 168 px):**
1. Xuất bản 168×94 cho thumbnail hiện tại; kiểm chữ đọc rõ trong 1–2 giây, chủ thể nhận ra, không chữ đè mặt tượng.
2. Đếm chữ: audit 30/10 ghi thumbnail Trần Nhân Tông dùng chữ nhỏ; mục tiêu 2–5 từ (tối đa 8 nếu cần nghịch lý, PO 03/11).
3. Ghi lại tương phản bằng mắt (chữ vàng trên nền tối) vào sổ; chưa có công cụ đo tự động trong `tools/long_packaging/`.

**Đề xuất 3 Long chạy Test & Compare** (theo `long-packaging` §3 bước 5, mỗi video đổi một biến: thumbnail, giữ nguyên title):
- Tiền Thân tập 4 (`r-B5LOPA_OA`): nhân vật người mù cận mặt + ba chữ "NGƯỜI MÙ DẪN TÀU" so với thumbnail hiện tại.
- Trần Nhân Tông (`_5jjFNFPBgk`): "BỎ NGAI VÀNG?" (audit 30/10 đề xuất A) so với hiện tại. Audit đã giữ HOLD tới 03/11; số liệu 28 ngày bây giờ đủ ≥ 1.500 impressions.
- Tây Du Ký (`zpM4H7K9v-A`): "ĐƯỜNG TĂNG MỘT MÌNH" nhân vật cận mặt so với hiện tại.
Điều kiện (L6): ≥ 1.500 impressions mỗi nhánh; ghi `ab_ledger.py add` trước khi bật; không đổi title cùng lúc.

### Q5. Chủ đề: 10 đề tài nhân vật kế tiếp, có nguồn

Đã làm (không lặp): Đường Tăng/Huyền Trang, Trần Nhân Tông, Đề Bà Đạt Đa, Ương Quật Ma La, Chūḷapanthaka, Kisā Gotamī, Ānanda, Temiya, xá lợi, Truyện Tiền Thân.

**Cảnh báo bắt buộc:** các số kinh dưới đây là điểm xuất phát; **trước khi viết lời phải đối chiếu `hf_sutta.py` từng cụm Phật nói** (hoặc bản dịch có số). Không gán cho Đức Phật điều không nằm trong kinh. Chi tiết nằm ở chú giải hoặc kinh Đại thừa phải gắn nhãn.

| # | Nhân vật / tích | Nguồn chính (cần đối chiếu) | Nhãn |
|---|---|---|---|
| 1 | Vua A-xà-thế (Ajātasattu) hỏi quả báo của đời tu | Trường Bộ 2 (Kinh Sa-môn quả, Sāmaññaphala Sutta) | Pali, kinh tạng |
| 2 | Cấp Cô Độc (Anāthapiṇḍika) mua vườn Kỳ Viên và lời dặn lúc lâm chung | Luật Tạng Tiểu phẩm (Cūḷavagga, chương về trú xứ); Trung Bộ 143 (Anāthapiṇḍikovāda) | Pali; chi tiết mua vườn là truyện trong Luật, ghi "Luật Tạng kể" |
| 3 | Đại Ca-diếp (Mahākassapa) khất thực, mặc y phấn tảo | Tương Ưng Bộ, Tương Ưng Kassapa (SN 16, khoảng SN 16.5); kết tập lần 1 ở Luật Tạng Tiểu phẩm chương 11 | Pali; kết tập 1 là Luật Tạng |
| 4 | Xá-lợi-phất (Sāriputta) về thăm mẹ và nhập diệt | Tương Ưng Bộ 47.13 (Cunda); chi tiết về thăm mẹ ở chú giải | Kinh + **chú giải** (tách rõ) |
| 5 | Mục-kiền-liên (Moggallāna) và việc bị hại | Tăng Chi Bộ (kinh về buồn ngủ, AN 7.58); đoạn bị cướp đánh chỉ có ở chú giải Pháp Cú | Kinh + **chú giải** |
| 6 | Vua Ba-tư-nặc (Pasenadi) hỏi Phật | Tương Ưng Kosala (SN 3), chọn một kinh rồi ghi số | Pali |
| 7 | Patācārā mất chồng con, đi tìm Phật | Trưởng Lão Ni Kệ (Therīgāthā, kệ Patācārā); tiểu sử ở chú giải | Pali + **chú giải** |
| 8 | Trần Thái Tông, vị vua đi tu và viết "Khóa Hư Lục" | Đại Việt sử ký toàn thư; Khóa Hư Lục (nguồn sử, thiền Việt) | **Sử + văn bản Thiền Việt, không phải kinh Pali** |
| 9 | Pháp Hiển (Faxian) đi Ấn Độ năm 399–412 | "Phật quốc ký" (Hán tạng, Đại Chánh tạng bộ 2085) | **Du ký Hán văn, nguồn sử** |
| 10 | Mục-liên cứu mẹ (Vu Lan) | Kinh Vu Lan Bồn (Hán tạng, Đại Chánh tạng bộ 685) | **Kinh Đại thừa/Hán tạng, một số học giả cho là kinh Trung Hoa; ghi rõ, không dẫn như lời Phật trong Pali** |

Thứ tự ưu tiên (theo "tên riêng quen" đo bằng CTR: Đường Tăng 4,11% và "đề xuất cụm"): 8 và 9 (cùng cụm Trần Nhân Tông và Đường Tăng, kéo lại suggested), rồi 1 (kịch tính, tên vua lớn), 2, 10 (theo mùa Vu Lan, tháng 7 âm lịch 2027). Nguồn tìm kiếm cần kiểm bằng `hf_trends` trước khi chốt (chưa có số trong repo).

### Q6. Dẫn từ Short sang Long (BUD)

**Hiện trạng.** Audit 30/10: màn hình kết thúc chưa gắn (ghi chú 04/10). 85% lượt xem Trần Nhân Tông đến từ đề xuất nên một cụm Long cùng chủ đề có giá trị.
**Đề xuất (chủ kênh đã đồng ý gắn "Video liên quan" cho Short > 100k; BUD không có Short nào đạt ngưỡng đó, cao nhất 3.458):**
- Với BUD hạ ngưỡng thử: Short ≥ 1.000 lượt xem và AVP ≥ 100% thì gắn "Video liên quan" tới Long cùng chủ đề. Ghép mẫu: "Đức Phật mỗi ngày ăn mấy bữa?" (2.662) và "Vị sư bệnh nằm một mình, Đức Phật làm gì?" (1.676), nhưng **chỉ ghép khi có Long đúng chủ đề**; chưa có thì không ép ghép.
- Short Đại Bi trỏ sang Long có Tâm Kinh hoặc chú Đại Bi (nếu làm).
- Thêm comment ghim và thẻ trong video; màn hình kết thúc 20 giây gắn Long cùng cụm (Phật Hoàng, Đề Bà Đạt Đa, Ương Quật, Tây Du Ký).
- Đo sau 14 ngày: lượt xem nguồn "Shorts liên quan" của Long và tỷ lệ chuyển = lượt xem Long từ nguồn đó chia lượt xem Short. Hiện chưa có số gốc BUD; ghi mốc đầu ngày gắn.

### Q7. Đoạn được xem lại

Dò mốc thời gian từ TTS (`out/<id>.json`; độ lệch có thể vài giây do video có nghỉ và hiệu ứng):

| Mốc | Video | Nội dung đoạn |
|---|---|---|
| 26:11 | Tiền Thân tập 4 | "Nhưng từ trong màn sương mờ, một bóng người ung dung bước tới." (kẻ ác tưởng không ai dại quay lại nộp mạng; người hoa tiêu trở lại) |
| 10:15 | Trần Nhân Tông | "Trong vị vua cầm quân, có một người tu." Lòng từ với kẻ thù hôm qua (sau trận Bạch Đằng) |
| 22:19 | Trần Nhân Tông | Cảnh ra đi: "Rồi ông nằm nghiêng như thế sư tử..."; giai thoại vả miệng người thị giả: "chớ nói mớ!" |

**Đây là kiểu đoạn nào:** (a) **bước ngoặt đã được hẹn từ cold open** (người đọc đã được hỏi "người hoa tiêu có quay lại không?", "ông nói gì lúc ra đi?"); (b) đoạn **câu tương phản chính nhân vật** (vua cầm quân đối với người tu); (c) đoạn có **câu ngắn, hình ảnh một người đơn độc** (bóng người trong sương, nằm nghiêng ra đi). Khớp với luật 8 của `long-script`: câu ngắn đặt sau khoảnh khắc, có người tua lại.
**Nhân rộng được không:** Có thể thiết kế có chủ ý: mỗi Long nhân vật có đủ ba loại đoạn trên, đặt **bước ngoặt chính ở 75–85% thời lượng** (tt04 ở 26:11/32:20 = 81%; Trần Nhân Tông ở 22:19/30:09 = 74%, khớp "cảnh mạnh ở 75%"). Ràng buộc: đoạn phải thật, không bịa; đoạn "bóng người trong sương" là chi tiết có trong bản dịch Tiền Thân, không được thêm vào.
Đây là giả thuyết từ 3 điểm; chưa đủ để kết luận "đỉnh 75%" là quy luật. Cần dò đường giữ chân theo giây cho ≥ 5 Long nhân vật (xem §6 Dữ liệu cần).

---

## 4. FS: 6 câu hỏi (8–13)

### Q8. Khuôn Short 10 giây dạng bảng tra

**Bằng chứng (CSV 28 ngày).** Top FS: Kim Lâu 345.037 lượt xem (AVP 300%, 144 đăng ký); Thái Tuế 273.673 (223%); 3 tuổi hợp 167.233 (192%); sao hạn nam 122.574 (204%); sao hạn nữ 109.024 (236%); tuổi 49/53/61 113.927 (175%). Video 26–30 giây chung chung: "Năm 2027 là năm con gì" 127.229 lượt xem, AVP 116%; "Tuổi nào phạm Thái Tuế" 110.820, AVP 134%. Khớp issue: bảng tra 10s hơn xa video nói chung.

**Khuôn chuẩn hóa (đưa vào `shorts-lookup` §2 dạng 1):**
1. 0–2 s: dòng nhắm thẳng người xem: "Bạn sinh năm bao nhiêu?" hoặc "Tuổi nào phạm Kim Lâu năm 2027?"
2. 2–7 s: bảng **đủ 12 con giáp** gọi bằng tên chi (Tý…Hợi), các ô liên quan sáng; năm sinh ≥ 90 px.
3. 7–10 s: câu "Dừng hình tìm năm sinh của bạn rồi lưu lại nha" và **khung cuối đứng ≥ 3 giây** (đã có luật hold frame).
4. Hai giây cuối rơi nhẹ (Kim Lâu từ 285% xuống 267%): thử vòng lặp.

**Thử tiếp để tăng "ở lại xem" từ ~65% lên > 70%:**
- E6: mở nhắm nhóm tuổi (câu 1 ở trên) so với mở bằng tên chủ đề hiện tại.
- E7: vòng lặp liền mạch (câu cuối nối vào câu đầu: "...tuổi nào phạm Kim Lâu năm 2027?" kết bằng "Còn tuổi nào nữa? Xem lại từ đầu").
Mỗi thử một biến, cùng bảng, cùng chủ đề; đo "ở lại xem" ở ≥ 6 cặp (số lượng 2 nhánh mỗi nhánh). Giữ 60/40 của `shorts-lookup` §7.

### Q9. Mở rộng chuỗi 2027 (lịch ra trước Tết)

Tết Đinh Mùi 2027 theo `plan_long_w55` rơi vào tháng 2 dương lịch 2027 (kiểm bằng `amlich.py` trước khi chốt ngày). Lịch đề xuất (một chủ đề mỗi tuần, Short bảng tra + Long cùng chủ đề; số liệu sinh bằng code `canchi.py`, `amlich.py`, `tuvi_year.py`, không gõ tay):

| Thứ tự | Chủ đề | Short (10 s bảng) | Long | Ghi chú |
|---|---|---|---|---|
| 1 | Làm nhà / Kim Lâu | Đã có Kim Lâu (345k) | "Tuổi nào làm nhà đẹp nhất 2027" (643 lượt xem, đã có) | Gắn Short Kim Lâu sang Long này (Q11) |
| 2 | Cúng sao giải hạn | Từ sao hạn nam/nữ (122k/109k) | Long 5–8 phút một tuổi hoặc bảng tra | Không hứa tiền; "theo truyền thống" |
| 3 | Sinh con 2027 | Bảng tháng tốt | "Sinh con năm 2027 mệnh gì" (525 lượt xem, xem TB 8:23, đã có) | |
| 4 | Cưới hỏi | `thiep_cuoi` | Long tuổi cưới | Đăng trước 3–5 tháng (memory ngày tốt) |
| 5 | Xông đất, hướng xuất hành, màu hợp | "Tuổi nào xông đất Tết 2027" (97.667, đã có) | Long Tết (L_fs_20 đã lên lịch 25/11) | Màu hợp tính bằng ngũ hành code |

Cổng: mỗi mục phải có số kiểm từ code; không hứa số tiền (luật FS trong `long-packaging` §2).

### Q10. Hai dạng Long song song và tỷ lệ sản xuất

**Bằng chứng (CSV FS):**

| Dạng | Ví dụ | Lượt xem 28 ngày | CTR | AVP | Ghi chú |
|---|---|---|---|---|---|
| Một tuổi, 5–8 phút | Tuất (5:26), Mùi (6:00), Sửu (5:51), Thái Tuế (7:36) | 1.144 / 632 / 391 / 395 | 12,1% / 11,8% / 10,5% / 9,2% | 51,7% / 47,2% / 54,8% / 45,4% | AVP cao gấp 2 lần Long 30 phút; xem TB chỉ 2:48–3:28 |
| ≥ 30 phút tổng hợp | Mão T10 (30 phút) | 2.039 | 9,0% | 22,3% | Issue ghi 2.586 lượt xem, 176 giờ xem; xem TB 6:46 |
| ≥ 30 phút bảng tra | Làm nhà (30 phút) | 618 | 5,8% | 10,0% | AVP thấp nhất nhóm |

Theo `phan_tich_long_2026-10-21.md`: Long 30+ phút mất 75–92% người xem trong 90 giây đầu; 5–8 phút giữ 75–86% ở mốc 5%. Long ≥ 30 phút của FS thắng nhờ **mùa/lịch âm** (Mão tháng 10 âm), không nhờ độ dài (`phan_tich_fs_long_thang_2026-10-28.md`).

**Đề xuất tỷ lệ (theo quyết định 13/11).** Mỗi tuần: **2 Long ≥ 30 phút** (một theo tháng âm lịch/tuổi đang tìm nhiều, một tổng hợp/tra cứu) và **1–2 Long 5–8 phút một tuổi** (suất ngắn). Chạy 4 tuần rồi so, kết luận chỉ sau ≥ 1.500 impressions mỗi video (luật L6).

**Cách chọn đề cho suất ngắn FS (một tuổi 2027):**
1. Chọn tuổi có Short bảng tra liên quan > 100 nghìn (để gắn Video liên quan, Q11) hoặc có tháng âm đang tìm (Q12).
2. Ưu tiên tuổi **chưa có Long 5–8 phút** (đã có: Thái Tuế 4 tuổi, Sửu, Mùi, Tuất, Tý). Danh sách tuổi còn lại phải lấy từ `tuvi_year.py`; không tự điền.
3. Tiêu đề theo L1: `TUỔI X 2027` ở đầu + câu hỏi thật ("... năm 2027 có thật sự đáng lo?").
4. Thumbnail theo L1–L4 của FS (tên tuổi lớn, linh vật cận mặt, ≤ 9 từ).

**Khuôn mở 5–8 phút (áp `long-script` luật 4 và 5, không thêm luật):**
- 0–15 s: gọi đúng năm sinh và tên chi + lời đáp một phần ("Tuổi Tuất năm 2027 gặp Hình và Phá; nhưng mức nặng chỉ ở hai điều này").
- 15–45 s: **bảng tóm tắt trên màn hình** (luật Long tra cứu 05/11), chương một tuổi bắt đầu trước 1:00.
- Mỗi câu ≤ 35 tiếng đọc; không đọc quá 3 năm sinh một câu.
- Kết: callback + một câu hỏi, không "Tóm lại".

**Chỉ số đo 14 ngày cho suất ngắn:** CTR ≥ 10% (so với 12,1% Tuất); AVP ≥ 45%; giữ ở mốc 5% ≥ 75%; lượt xem từ Tìm kiếm; đăng ký trên 1.000 lượt xem. So với 3 Long ngắn trước đã có.

### Q11. Dẫn từ Short sang Long (FS)

**Hiện trạng:** 325 lượt xem chuyển từ Short sang Long (issue) trong khi Short có 3,79 triệu lượt xem. Chủ kênh đã đồng ý gắn "Video liên quan".
**Việc cụ thể:**
- Danh sách ghép (kiểm bằng `webauto`/Studio): Kim Lâu → Long làm nhà 2027; Thái Tuế → Long "4 tuổi phạm Thái Tuế"; 3 tuổi hợp nhất → Long hợp tuổi (đang ghi 2,2% CTR, nên làm Long mới); Sao hạn nam/nữ → Long sao hạn; tuổi 49/53/61 → tv06 Kỷ Mùi 1979 (L_fs_tv06, hẹn 17/11).
- Chỉ ghép khi Long cùng chủ đề; Long đã có phải xem qua giữ chân trước.
- Mô tả Short ghi tên Long ở dòng đầu; comment ghim.
- Đo: lượt xem nguồn "Shorts liên quan" của từng Long sau 14 ngày; mốc đầu là 325. Mục tiêu đặt sau khi có số mốc, không đặt con số trước.

### Q12. SEO tìm kiếm (CTR 9,7%)

Tìm kiếm: 32,9% lượt xem Long, CTR 9,7%; tương quan CTR và tỷ trọng Search r = 0,87 (n = 16) trong `thumb_ctr`. **Bộ mẫu tiêu đề** (tất cả viết theo cụm người xem gõ; đáp án thật trong video, `promise_check.py` ≥ 3 câu):

| Mẫu | Ví dụ |
|---|---|
| `TUỔI <chi> <năm sinh> NĂM 2027: <sao/hạn> — <câu hỏi>` | Tuổi Dần 2027: gặp sao gì, có thật sự đáng lo? |
| `Tuổi <chi> làm nhà năm 2027: <kết luận có điều kiện>` | Tuổi Tuất làm nhà 2027 được không? |
| `Tuổi <chi> sinh con năm 2027: tháng nào hợp?` | |
| `<năm sinh> <can chi> tháng <N> âm lịch <năm>: <tuổi> nên làm / tránh gì?` | Ất Mão 1975 tháng 11 âm lịch |
| `Cúng sao giải hạn 2027: tuổi nào, ngày nào?` | |

Quy tắc: không "sự thật gây sốc"; không hứa tiền; thumbnail `TUỔI X 2027` đồng khớp tiêu đề (L1). Theo dõi thang đo L6. Ghi các mẫu vào `long-packaging` (mục 4 thêm bảng).

### Q13. Áp khuôn FS cho BUD (chuỗi kinh chú, dừng hình để đọc theo)

**So sánh thận trọng.** "Ở lại xem" FS 63–68% so với BUD 30,3% **không so trực tiếp được**: Short FS 10 giây, Short BUD 26–36 giây, và BUD tính trên cả đuôi dài 277 video có trung vị 40 lượt xem. Cả hai đều có AVP > 100% ở top. Tuy vậy cơ chế FS (một chìa khóa cá nhân + hành động dừng hình) là có thật. Đáng chú ý: BUD có 4,6 đăng ký mỗi 1.000 lượt xem so với FS 0,54; người xem BUD ít hơn nhưng gắn kết hơn.

**BUD áp được khuôn này cho chuỗi kinh chú** vì đoạn văn bản ngắn cho phép "đọc theo". Thiết kế thử:
- Short 12–15 s: câu hỏi ("Câu thứ nhất của Chú Đại Bi nghĩa là gì?") rồi **một khung chữ phiên âm + nghĩa đứng ≥ 3 giây** kèm câu "dừng hình đọc theo từng câu".
- Chuông xoay ở giây 0; nền tĩnh, chữ lớn, phiên âm Hán-Việt đúng.
- Câu cuối nối đầu (vòng lặp) như E7 của FS.

**Ràng buộc nội dung:** Chú Đại Bi thuộc kinh Đại thừa (Hán tạng, Thiên Thủ Thiên Nhãn Quán Thế Âm Bồ Tát ... Đà-la-ni, Đại Chánh tạng khoảng bộ 1060; cần đối chiếu số). **Nhãn "kinh Đại thừa / Bắc truyền", không gọi là "lời Phật dạy trong Pali".** Giải nghĩa gắn "theo cách giải thích phổ biến" (luật `shorts-lookup` §8).
**Lưu ý:** PO 09/11 đã dừng nối "Câu thứ N" (lượt xem giảm dần). Thử E11 là **một video gộp "nghĩa cả bài"** hoặc chuỗi tiêu đề độc lập, không phải nối tập.

---

## 5. Bảng thử nghiệm (mỗi thử nghiệm chỉ đổi một biến)

Mốc đo là 14 ngày sau khi đăng (hoặc sau khi bật thử nghiệm). Ghi sổ ở `output/cl_staging/experiments/` và `ab_ledger.py` (Long). Không thay title/thumbnail của video đã lên lịch trừ khi chủ kênh yêu cầu.

| # | Kênh | Biến duy nhất | Nhánh | Chỉ số (mốc 14 ngày) | Điều kiện |
|---|---|---|---|---|---|
| E1 | BUD Short | Hình thức giây 0–3 | A: câu hỏi chữ + giọng nói cùng lúc ở giây 0; B: mở hiện tại | "ở lại xem", AVP | Cùng chủ đề, cùng độ dài, ≥ 6 cặp |
| E2 | BUD Short | Câu mời tập kế (cuối video) | A: có "Danh hiệu tiếp theo: ..." + comment ghim; B: không | Lượt xem tập N+1 chia tập N | Chuỗi mới (Tâm Kinh hoặc danh hiệu Phật), 1 tập/ngày, 5 tập |
| E3 | BUD Long | Cảnh mở | A: hình nhân vật hiện trong 5 giây đầu + cảnh căng nhất ở câu 1; B: khuôn hiện tại | Giữ chân giây 30 / 60 / 90 | So 3 Long gần nhất; chỉ khi có đường theo giây |
| E4 | BUD Long | Thumbnail (Test & Compare) | A: hiện tại; B: nhân vật cận mặt + 3 chữ | CTR theo nhánh (nhất là nguồn đề xuất) | ≥ 1.500 impressions mỗi nhánh; title giữ nguyên; tt04 làm trước |
| E5 | BUD | Gắn "Video liên quan" Short ≥ 1.000 lượt xem → Long | A: gắn; B: Short tương đương không gắn | Lượt xem nguồn Shorts liên quan; tỷ lệ chuyển | Short cùng chủ đề mới có Long |
| E6 | FS Short | Câu mở | A: "Bạn sinh năm bao nhiêu?"; B: tên chủ đề | "ở lại xem" (mục tiêu > 70%), AVP | Cùng bảng, cùng ngày đăng |
| E7 | FS Short | Vòng lặp | A: câu cuối nối câu đầu; B: kết thường | AVP, "ở lại xem" | Cùng bảng |
| E8 | FS Long | Mẫu tiêu đề Search | A: mẫu mới Q12; B: tiêu đề cũ | CTR Search, lượt xem Search | Cùng tuổi, cùng khuôn thumbnail; ≥ 1.500 impressions |
| E9 | FS | "Video liên quan" Short > 100k → Long | A: gắn; B: Short tương đương không gắn | Lượt xem Shorts liên quan (mốc 325) | Chủ kênh đã duyệt |
| E10 | FS Long ngắn | Độ dài | 5–8 phút một tuổi (suất ngắn) so với 3 Long ngắn có sẵn | CTR ≥ 10%, AVP ≥ 45%, giữ 5% ≥ 75% | Một tuổi chưa có Long ngắn; số bằng code |
| E11 | BUD Long ngắn | Độ dài | 5–8 phút một nhân vật/tích ngắn (suất ngắn) so với Long 30 phút cùng nhân vật | CTR, AVP, đăng ký/1.000 lượt xem | Nhân vật trong §3 Q5; **không** làm hai bản cùng nhân vật cùng tuần |
| E12 | BUD Short | Khung "dừng hình đọc theo" cho kinh chú | A: có khung chữ ≥ 3 giây + câu mời dừng; B: không | AVP, tỷ lệ xem lại | Kinh Đại thừa gắn nhãn; một câu mỗi video |

**Cách chọn đề cho suất ngắn BUD (một nhân vật / một tích ngắn):**
1. Tích có đúng **một bước ngoặt** và nguồn gọn (một kinh hoặc một đoạn Tiền Thân): Patācārā (Therīgāthā), Đại Ca-diếp (SN 16), Pasenadi (SN 3), Cấp Cô Độc (MN 143).
2. Nhân vật đã có tên riêng quen (CTR "tên riêng quen" là tín hiệu duy nhất ở BUD).
3. Chỉ làm khi có nguồn kiểm bằng `hf_sutta.py`; Tiền Thân thì `hf_sutta.py ja<N>`.

**Khuôn mở 5–8 phút BUD:** 0–10 s cảnh đỉnh của nhân vật (có thời điểm); 10–25 s câu hỏi một và hẹn trả lời ở phút nào; 25–60 s lộ trình một hình thức; kết bằng câu hỏi cho người xem. Câu nguồn dời xuống cuối chương một.
**Chỉ số 14 ngày (BUD ngắn):** AVP ≥ 45% (hiện Long 30 phút 22–32%), CTR so với trung vị Long BUD 2,84%, đăng ký/1.000 lượt xem, lượt xem từ nguồn đề xuất. Số này là mục tiêu thử, không phải dự báo.

## 6. Dữ liệu cần thêm để kết luận chắc hơn

1. Đường giữ chân theo giây (`audienceWatchRatio`) của Tây Du Ký, Tiền Thân 4, Luật Nhân Quả: để chốt Q3 và Q7.
2. Số "Shorts liên quan" của BUD trước khi gắn (mốc đầu).
3. "Ở lại xem" riêng từng Short BUD hàng đầu.
4. Chưa có công cụ đo tương phản thumbnail tự động.

## 7. Đề xuất sửa 3 skill (chưa áp dụng)

**`.claude/skills/long-packaging/SKILL.md`**
- Mục "Đặc thù kênh BUD": thêm dòng "CTR nguồn đề xuất 2,78% bằng mặt bằng Long BUD (trung vị 2,84%); không coi là lỗi riêng; ứng viên A/B ưu tiên: video có AVP cao mà CTR thấp (tt04: 31,8% và 2,0%)".
- Thêm luật BUD B1: thumbnail nhân vật cận mặt, 2–5 chữ, kiểm ở 168 px; Test & Compare chỉ đổi thumbnail, giữ title.
- Thêm bảng mẫu tiêu đề Search FS (Q12).
- Thêm "Long ngắn 5–8 phút": tiêu đề `TUỔI X 2027: ... ?`, ≥ 1.500 impressions mới kết luận (L6).
- Bước 7: thêm mốc "14 ngày sau khi bật" cho Test & Compare.

**`.claude/skills/long-script/SKILL.md` (và `references/formats.md`)**
- Luật 1 (cold open): thêm "nhân vật xuất hiện (tên hoặc 'một người') trong 5 giây đầu; cảnh đỉnh ở câu 1; không mở bằng cảnh người thứ ba rồi mới tới nhân vật chính (Tây Du Ký: nhân vật chính ở giây 18, cảnh căng nhất ở giây 38)".
- Luật 2: dời câu "dựa trên nguồn..." xuống sau giây 90 (nhét vào chương 1 hoặc mô tả); hiện đang ở giây 80–92.
- Khuôn nhân vật: thêm "đặt bước ngoặt chính khoảng 75–85% thời lượng; mỗi Long có đủ 3 loại đoạn: bước ngoặt đã hẹn, câu tương phản nhân vật, câu ngắn đơn độc".
- Thêm format (f) "Long ngắn 5–8 phút" (một tuổi cho FS, một tích cho BUD): khuôn mở §4, ngân sách ~925–1.500 tiếng (185 tiếng/phút), 4–6 chương, không chương lý thuyết.
- Lint: cảnh báo mới `NHAN_VAT_MUON` khi tên nhân vật chưa xuất hiện trước ~20 giây (tính theo tiếng đọc).

**`.claude/skills/shorts-lookup/SKILL.md`**
- §1/§2 dạng 1: thêm khuôn 10 giây ("Bạn sinh năm bao nhiêu?" → bảng đủ 12 chi → "dừng hình" → khung cuối ≥ 3 giây) và hai thử nghiệm E6, E7.
- §2: thêm dạng 7 "Chuỗi kinh chú dừng hình đọc theo" (BUD, 12–15 s; nhãn Đại thừa/Bắc truyền cho Đại Bi, Tâm Kinh).
- §7: thêm luật chuỗi: tiêu đề độc lập, không "Câu thứ N", tối đa 5 tập liên tiếp (căn cứ giảm dần 3.458 xuống 326, 294, 55).
- Thêm mục "Dẫn sang Long": Short FS > 100 nghìn, Short BUD ≥ 1.000 và AVP ≥ 100% gắn Video liên quan, mô tả và comment ghim.
- §1: thêm lưu ý "AVP cao không bằng phân phối"; CTR Short không dùng để xếp hạng.
