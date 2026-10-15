# Khung vĩ mô và bốn format

## 1. Khung theo thời lượng (185 tiếng/phút; Đêm nghe đọc chậm ~160)
| | 30' | 45' | 60' | 90' (Đêm nghe) |
|---|---|---|---|---|
| Ngân sách tiếng | ~5.500 | ~8.300 | ~11.000 | ~14.000-15.000 |
| Số dòng `say()` (15-25 tiếng/dòng) | 220-330 | 330-500 | 450-650 | 600-850 |
| Cold open | 0:00-0:30 | 0:00-0:40 | 0:00-0:45 | 0:00-1:30 (êm) |
| Móc mở rộng + lộ trình ≤ 2 câu | -1:00 | -1:15 | -1:30 | 1 câu |
| Chương nội dung đầu tiên bắt đầu | ≤ 1:30 | ≤ 2:00 | ≤ 2:30 | ≤ 3:00 |
| Số chương × độ dài | 6-8 × 3-5' | 7-10 × 4-6' | 9-12 × 5-7' | 10-12 × 7-9' |
| Re-hook (mở vòng / trả vòng / câu hỏi) | ~7, 15, 22' | ~11, 22, 34' | ~15, 30, 45' | không móc gắt |
| Điểm nghỉ quảng cáo gợi ý (cuối chương, ngay sau câu mở vòng) | ~8, 15, 22' | ~8, 16, 24, 32, 40' | mỗi 7-8' | không đặt trong 20' cuối |
| Vòng lớn trả | 27-29' | 41-43' | 55-58' | (không) |

Quy tắc chung:
- Mở bằng cảnh / tình huống cụ thể có câu hỏi chưa trả; KHÔNG đóng vòng ấy trước khi vòng lớn hơn đã mở (B5: −41 điểm
  khi lộ "Đức Phật" ở giây 22 rồi vào lộ trình). Hook speaks viewer's language: kết quả người xem nhận, không thuật ngữ.
- Lộ trình: "ba câu hỏi" là đủ, đọc gọn trong 1-2 câu; không đọc địa danh / tên chương. Lời rào nguồn ("kiến thức truyền
  thống để tham khảo", "lời kinh có số kinh") ≤ 1 câu, đặt sau móc, hoặc dời vào chương 1.
- Thông điệp (value) chạm tới chậm nhất ở beat 2 (story-spine §2); phần sau là bằng chứng.
- Giữa video (~50%): quay lại cảnh mở, đóng một vòng nhỏ, mở vòng lớn hơn; nhắc lại câu hỏi lớn trong 1 câu cho người
  mới tua tới. ~75%: cảnh mạnh thứ hai (long-video §2).
- Mỗi chương: móc riêng (1-2 câu) -> bối cảnh -> leo thang -> đỉnh + lặng -> bài học 1-2 câu -> **câu cầu nối**.
  Chương phải tự đứng được khi người xem nhảy tới từ mục lục (F6 tăng +6..+7 điểm ở thẻ chương).
- Kết: callback cảnh mở + motif + đóng các vòng + MỘT câu hỏi thật cho bình luận + ≤ 2 câu đăng ký.

## 2. (a) BUD — Truyện Tiền Thân (45-60')
Đối thủ thắng: Quang Vô Sắc TV "Truyện tiền thân Phật – Tập 1" (45:02, 180 nghìn view / 27 ngày) kể **một** truyện
(Apaṇṇaka, `ja1`) cho cả tập; tập 2 (57') thêm mục chú giải thuật ngữ có số kinh trong mô tả. Hai biến thể:

**A1 — một truyện sâu (45')**: chọn truyện có cốt dài (Apaṇṇaka ja1, Devadhamma ja6, Vessantara ja547 chia nhiều tập).
**A2 — tuyển tập 5-8 truyện quanh một chủ đề (45-60')**: "5 chuyện tiền thân về lời nói", "6 lần Bồ Tát chọn nhẫn nhục";
mỗi truyện 6-9' = một chương; xếp truyện mạnh nhất ở chương 1 và truyện cảm xúc nhất ở ~75%.

Mỗi truyện theo 5 phần của Tiền Thân (Jātaka), đảo thứ tự cho giữ chân -- chi tiết `story.md`:
| Phần | Nguồn | Trong kịch bản |
|---|---|---|
| Khủng hoảng của chuyện quá khứ | chú giải | cold open / móc chương: dừng ở khoảnh khắc chọn lựa |
| Chuyện hiện tại (vì sao Đức Phật kể) | chú giải | 3-6 câu, nối với câu hỏi đời thường của người xem |
| Chuyện quá khứ | chú giải | thân chương: bối cảnh -> leo thang -> đỉnh |
| Kệ (gāthā) | **kinh** (Tiểu Bộ) | `alt=True`, đối chiếu `hf_sutta.py ja<N>`, diễn ý ≤ 2 câu |
| Nhận diện (ai là ai đời nay) | chú giải | cú lật cuối truyện ("người lái buôn khôn ngoan ấy là Bồ Tát") |
| Bài học hôm nay | kênh | 1-2 câu + câu cầu nối sang truyện sau |

Khung A2 (50'): 0:00 khủng hoảng truyện 1 (40") -> lộ trình "sáu truyện, một câu hỏi" -> truyện 1 (8') -> truyện 2 (7')
-> **re-hook 12'**: câu hỏi chung của cả tập -> truyện 3-4 -> **25'**: quay lại câu hỏi, mở "truyện cuối là chính Đức Phật
nói về mình" -> truyện 5 (cảm xúc nhất ~36') -> truyện 6 -> kết: kệ chung + callback + câu hỏi bình luận.

## 3. (b) FS — Tử vi trọn đời tuổi X + năm 2027 (35-45')
Đối thủ "Quý Hợi 1983" (30-58', 75-350 nghìn view): chia theo giai đoạn tuổi, tách nam / nữ mạng, hứa tiền bạc
(không theo phần hứa). Của mình: **mọi con số sinh bằng code** (`canchi.py`, `amlich.py`, `batrach.py`), mọi nhận định
"theo truyền thống", có lời khuyên thực tế.
| Phút | Chương | Nội dung |
|---|---|---|
| 0:00 | cold open | một người tuổi X (nhân vật minh hoạ, ghi rõ) trước một quyết định năm 2027 + con số cụ thể của tuổi ấy |
| 0:40 | lộ trình | 1 câu "ba câu hỏi" + "bảng tra đủ nam nữ ở cuối" (vòng lớn) |
| 1:00 | Bạn là ai trong vòng 60 năm | can chi, nạp âm, mỗi khái niệm ≤ 2 câu kèm ý nghĩa ngay cho người xem (KHÔNG chương lý thuyết) |
| ~4' | Năm 2027 gặp tuổi X thế nào | quan hệ Thái Tuế, sao hạn **nam và nữ trong cùng chương** ("Nếu bạn là nữ, ...") -- không tách hai nửa video |
| ~10' | Từng giai đoạn đời | tuổi trẻ / trung niên / hậu vận theo tuổi âm tính bằng code; mỗi giai đoạn 1 dữ kiện -> cách đọc truyền thống -> việc nên làm |
| ~18' (re-hook) | Câu hỏi người ta gõ tìm | 3-4 câu từ `hf_trends` ("tuổi X hợp màu gì", "làm nhà năm nào") trả ngay câu đầu |
| ~25' | Tháng cần để ý / tháng thuận | bảng 12 tháng lên màn hình, lời đọc chỉ 2-3 tháng nổi bật |
| ~32' | Quý nhân và người nên tránh xung đột | tam hợp, lục hợp, ≤ 3 tên chi một dòng |
| cuối | Bảng tra + kết | bảng trên màn hình, KHÔNG đọc từng dòng (F6 −40% / 1,1'); callback + câu hỏi "bạn sinh tháng mấy?" |

## 4. (c) FS — Hỏi-đáp (40-60')
Mẫu: "Lọ hoa bàn thờ đặt bên trái hay phải?" 36-47' (425 nghìn view); dàn ý đối thủ: lỗi phổ biến -> nguyên tắc
("Đông bình tây quả") -> giờ giấc, chọn hoa quả -> một câu chuyện thực tế -> ý nghĩa con số.
- Mỗi câu hỏi = một chương, **tiêu đề chương đúng chữ người ta gõ tìm** (gợi ý tìm kiếm trong `briefs/fs_trends.md`).
- **Trả trong 2 câu đầu chương** (đáp án + "theo phong tục / theo truyền thống"), lý do và biến thể theo sau.
- 10-14 câu cho 45'; câu nhiều người tìm nhất đặt chương 1 (trả sớm); cứ 3 câu chen một câu chuyện (nhân vật minh hoạ,
  ghi rõ) hoặc một "hiểu lầm thường gặp" để đổi nhịp; câu khó / gây tranh luận để ~75%.
- Framing: "mỗi nhà có nếp riêng, nhà mình theo nếp nào thì giữ" khi các truyền thống khác nhau; không doạ.

## 5. (d) BUD — Đêm nghe lời Phật dạy (90')
Mẫu: "Tịnh Tâm Ngủ Ngon", "Mỗi đêm nghe 15 phút lời Phật dạy" (63-302', 0,5-7 triệu view). Chưa có số liệu giữ chân của kênh.
- Êm: không móc gắt, không cliffhanger, câu hỏi chỉ để mời quán chiếu; tempo 0,85-0,88; `pause` 1,2-2,0; nhiều câu ngắn.
- **Vẫn có 10-12 chương 7-9'** (người nghe nhảy tới bài mình thích): mỗi chương = 1 lời dạy có số kinh (Pháp Cú, Kinh Từ Bi
  Snp 1.8, Kinh Điềm Lành Snp 2.4, Kinh Mũi Tên SN 36.6...) đối chiếu `hf_sutta.py` + 1 hình ảnh / truyện ngắn + 1 nhịp thở.
- Một lời mời đăng ký nhẹ ở phút 2, không ở cuối; 10' cuối chậm dần, lặp (rải tâm từ). Lint: `--kind night`.

## 6. Beat sheet mẫu (điền trước khi viết dòng)
Câu chiến lược: **"Video này nói với [ai] rằng [thông điệp]."** Nhịp: `cảnh-HỎI-lộ trình | chuyện-ĐỈNH-lặng | ...`

| # | Phút | Chương / beat | Vai | Kỹ thuật | Cảm xúc | Vòng mở (M) / trả (T) | Chi tiết giác quan | Câu kết (cầu nối) |
|---|---|---|---|---|---|---|---|---|
| 0 | 0:00 | cold open: đoàn buôn giữa sa mạc, người lạ áo ướt nói "phía trước có nước" | móc | Imagine / scenario | căng | M1: họ có đổ nước? | cát, áo ướt, hoa sen trên xe | "Năm trăm người tin. Một người không." |
| 1 | 0:40 | lộ trình | hứa | Frame-then-fill | tò mò | M2: vì sao Đức Phật kể chuyện này | -- | "Bắt đầu từ thành Xá Vệ." |
| 2 | 1:10 | chuyện hiện tại | bối cảnh | Analogy với người xem | nhận ra mình | -- | tinh xá Kỳ Viên | "Đức Phật kể lại một chuyện cũ." |
| ... | | | | | | | | |
| n | 44' | kết | trả | Callback | an | T1, T2 | cát, nước | câu hỏi bình luận |

Cột "Kỹ thuật" lấy từ catalog của faceless-explainer story-design (Make-concrete, Reveal-in-order, Contrast, Structure,
Evidence, Memory & landing). Không ghi "giải thích ý" chung chung. Ví dụ trên là dàn ý để thử -- trước khi viết phải
đối chiếu cốt truyện với nguồn (story.md).
