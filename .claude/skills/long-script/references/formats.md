# Khung vĩ mô, bốn format, và khuôn nhân vật

Bản trụ FS và BUD là **khoảng 30 phút** (quyết định 21/10/2026). Đêm nghe 90 phút là ngoại lệ, lint `--kind night`.
185 tiếng/phút kể cả nghỉ → 30 phút ≈ 5.500 tiếng, khoảng 220–330 dòng `say()`.

## 1. Plan.md duyệt trước khi viết lời

Viết `plan.md` (hoặc một mục trong ghi chú tập) và **dừng chờ người dùng duyệt**. Chưa duyệt thì không viết `say()`.
Khuôn bốn phần. Mẫu cấu trúc lấy từ plan Long đã chứng minh của V2; ví dụ dưới đây là của FS và BUD, viết mới.

### 1. Vì sao chọn chủ đề này
Nhu cầu (câu người ta gõ, view/ngày của video cùng câu), gần tệp đang xem kênh, liên kết với Long đã làm,
một điểm chạm người Việt, tư liệu hình đủ chuẩn, và đề đã cân nhắc rồi loại.

### 2. Đóng gói
Tiêu đề: từ khoá đầu câu, kèm một con số gây tò mò. Thumbnail: 3 bản để thử, 0–3 chữ, cold open khớp hình.
Độ dài: 28–32 phút, 12–14 chương.

### 3. Xương sống
Một câu cung A→B.

**Cold open (≤ 60 giây), thì hiện tại, dừng ở đỉnh.**
FS: "Một người tuổi Sửu đứng trước cổng. Năm 2027. Bản dự toán nằm trên tay. La bàn hiện hai chữ trái nhau. Cửa chưa mở."
BUD: "Nước dựng thành vách. Bảy trăm người nhìn xuống một hố. Người mù cầm bát. Câu trong bát chưa được đọc."
Không chào. Chưa giảng. Trong 30 giây đầu: FS gọi năm sinh và tên chi; BUD gọi một nỗi khổ đời thường.

**Lộ trình xong trước giây 75.** Chọn một hình thức, ghi tên hình thức, đối chiếu tập liền trước cùng kênh.
Không lặp hình thức đó. "Ba câu hỏi" tối đa một lần trong năm tập.

| Hình thức | FS | BUD |
|---|---|---|
| Chặng đường | "Trước khi xem năm 2027, mình đi ba chặng của tuổi Ất Sửu: bản mệnh, sao hạn, rồi tháng nào thuận." | "Trước khi nghe câu trong bát, mình đi ba chặng: lời đã hứa, cái giá, rồi người giữ lời." |
| Cảnh hẹn trước | "Cuối video bạn gặp lại hai chữ trên la bàn, và lần ấy chúng không còn trái nhau." | "Cuối video bạn gặp lại người cầm bát, và lần ấy câu đã được đọc." |
| Câu hỏi duy nhất | "Vậy điều gì giữ một ngôi nhà đang định xây?" | "Một lời đã hứa, khi giữ thì có thể mất mạng, còn đáng giữ không?" |
| Lời thách | "Đoán trước: trong mười hai tháng, tháng nào kỵ động thổ? Giữ con số ấy tới chương sau." | "Đoán trước: người mù ấy xin gì? Giữ câu đoán tới chương sau." |
| Bản đồ bằng hình | Đọc một câu. Màn hình hiện các chương (timeline hoặc ledger), không đọc danh sách. | Đọc một câu. Màn hình hiện năm chặng của truyện. |
| Nghịch lý | "Hai người cùng một năm sinh, hai chiếc la bàn chỉ hai hướng. Tập này đi tìm lý do." | "Cả tàu kêu cứu, một người lại xin được tắm. Tập này đi tìm lý do." |

**Bảng vòng** (ít nhất 3). Cụm đóng là chữ sẽ có trong lời ở chương đóng, không phải chữ của cold open.

| # | Mở | Đóng ở chương | Cụm chữ đóng |
|---|---|---|---|
| 1 | Vì sao hai la bàn trái hướng? | 4 | hai hướng là một tuổi |
| 2 | Năm 2027 đào móng được không? | 8 | năm xung thì hoãn móng |
| 3 | Tháng nào trong mười hai tháng thuận? | 12 | tháng bảy để nền |

Khi ghi plan JSON, chép bảng ấy thành:

```json
"vong": [
  {"mo": "Vì sao hai la bàn trái hướng?", "dong": "hai hướng là một tuổi"}
]
```

Lint (`vong_khong_dong`, CẢNH BÁO) đọc trường này. Không có trường thì không kiểm. Cụm `dong` phải xuất hiện trong lời sau thẻ chương đầu.

**Mô-típ**, một hình ảnh lặp ≥ 3 lần (mở, giữa, kết). FS ví dụ: "hai chữ trên la bàn". BUD ví dụ: "bát nước chưa đọc".

**Dàn chương** — 12–14 dòng, mỗi chương khoảng 2 phút. Chương 0 là cold open + lộ trình. Ghi chương nào đóng vòng nào.
Đánh dấu chương phần thưởng (~50%, khoảng phút 15) và chương cảnh mạnh (~75%, khoảng phút 22).

| Phút | Việc |
|---|---|
| 0:00–1:00 | Cold open, dừng ở đỉnh |
| ≤ 0:30 | Chạm người xem (FS: năm sinh / chi; BUD: nỗi khổ đời thường) |
| ≤ 1:15 | Lộ trình một hình thức + bảng vòng đã mở |
| 1:15–15:00 | Các chương khoảng 2 phút; chương nội dung đầu trả một phần trong 90 giây |
| ~15:00 (50%) | Phần thưởng: thứ tiêu đề đã hứa (FS: câu trả lời năm/tháng; BUD: chỗ nhận ra) |
| ~22:00 (75%) | Cảnh mạnh thứ hai |
| 28–30:00 | Gọi lại cảnh mở, đóng vòng cuối, một câu hỏi cho người xem |

Mỗi chương: móc 1–2 câu → bối cảnh → một nhịp leo → đỉnh + lặng → bài học một câu → **câu móc**. Chương tự đứng được khi người xem nhảy từ mục lục. Câu kết chương không bắt đầu bằng "tóm lại" hoặc "như vậy".

Kết video: callback cảnh mở + mô-típ + đóng các vòng + một câu hỏi thật + tối đa 2 câu mời đăng ký, sau lần trả cuối.

### 4. Luật kênh riêng của tập
FS: tên chi, "theo truyền thống / để tham khảo", số sinh bằng code, không doạ, không hứa tiền.
BUD: lời Phật chỉ khi đã đối chiếu `hf_sutta.py`; truyền thuyết gắn nhãn; không vẽ mặt Đức Phật.
Nhãn hình: MINH HỌA / DIỄN Ý / TRÍCH DỊCH.

Đêm nghe không dùng lưới 2 phút. Giữ 10–12 chương 7–9 phút, mở êm, một câu lộ trình.

## 2. (a) BUD — Truyện Tiền Thân (~30')
Đối thủ thắng: Quang Vô Sắc TV "Truyện tiền thân Phật – Tập 1" (45:02, 180 nghìn view / 27 ngày) kể **một** truyện
(Apaṇṇaka, `ja1`) cho cả tập. Bản mình giữ khoảng 30 phút (quyết định 21/10; tập 56 phút của kênh rơi mạnh). Hai biến thể:

**A1 — một truyện sâu**: chọn truyện có cốt dài (Apaṇṇaka ja1, Devadhamma ja6; Vessantara ja547 chia nhiều tập).
Chia 12–14 chương khoảng 2 phút. Cold open là khoảnh khắc căng nhất, thì hiện tại, dừng ở đỉnh.
**A2 — bốn truyện quanh một chủ đề**: mỗi truyện khoảng 3 chương (6 phút), truyện mạnh nhất mở tập, truyện cảm xúc nhất ở ~75%.

Mỗi truyện theo 5 phần của Tiền Thân (Jātaka), đảo thứ tự cho giữ chân -- chi tiết `story.md`:
| Phần | Nguồn | Trong kịch bản |
|---|---|---|
| Khủng hoảng của chuyện quá khứ | chú giải | cold open / móc chương: dừng ở khoảnh khắc chọn lựa |
| Chuyện hiện tại (vì sao Đức Phật kể) | chú giải | 3-6 câu, nối với câu hỏi đời thường của người xem |
| Chuyện quá khứ | chú giải | thân chương: bối cảnh -> leo thang -> đỉnh |
| Kệ (gāthā) | **kinh** (Tiểu Bộ) | `alt=True`, đối chiếu `hf_sutta.py ja<N>`, diễn ý ≤ 2 câu |
| Nhận diện (ai là ai đời nay) | chú giải | cú lật cuối truyện ("người lái buôn khôn ngoan ấy là Bồ Tát") |
| Bài học hôm nay | kênh | 1-2 câu + câu cầu nối sang truyện sau |

Khung A2 (~30'): 0:00 khủng hoảng truyện 1 (≤ 60 giây) -> lộ trình một hình thức -> truyện 1 -> truyện 2
-> **phút 15**: quay lại câu hỏi chung -> truyện 3 -> **phút 22**: truyện cảm xúc nhất -> kết: kệ + callback + câu hỏi cho người xem.

## 3. (b) FS — Tử vi trọn đời tuổi X + năm 2027 (~30')
Đối thủ "Quý Hợi 1983" (30-58', 75-350 nghìn view): chia theo giai đoạn tuổi, tách nam / nữ mạng, hứa tiền bạc
(không theo phần hứa). Của mình: **mọi con số sinh bằng code** (`canchi.py`, `amlich.py`, `batrach.py`), mọi nhận định
"theo truyền thống", có lời khuyên thực tế. Các mốc dưới đây trải trên 12–14 chương khoảng 2 phút.
| Phút | Chương | Nội dung |
|---|---|---|
| 0:00 | cold open ≤ 60 giây | một người tuổi X (nhân vật minh hoạ, ghi rõ), thì hiện tại, trước một quyết định năm 2027; dừng khi hậu quả chưa xảy ra |
| ≤ 0:30 | chạm người xem | gọi năm sinh và tên chi |
| ≤ 1:15 | lộ trình | một trong 6 hình thức, khác tập liền trước; bảng tra nam nữ ở cuối là vòng lớn |
| ~2' | Bạn là ai trong vòng 60 năm | can chi, nạp âm, mỗi khái niệm ≤ 2 câu kèm ý nghĩa ngay (không chương lý thuyết) |
| ~6' | Năm 2027 gặp tuổi X thế nào | quan hệ Thái Tuế, sao hạn **nam và nữ trong cùng chương** ("Nếu bạn là nữ, ...") |
| ~10' | Từng giai đoạn đời | tuổi trẻ / trung niên / hậu vận theo tuổi âm tính bằng code; mỗi giai đoạn một chương khoảng 2 phút |
| ~15' (50%) | Phần thưởng | câu người ta gõ tìm (`hf_trends`), trả ngay câu đầu |
| ~20' | Tháng cần để ý | bảng 12 tháng trên màn hình, lời đọc chỉ 2–3 tháng nổi bật |
| ~22' (75%) | Cảnh mạnh | quyết định có hậu quả (làm nhà, chuyển chỗ) đúng năm ấy |
| ~26' | Quý nhân | tam hợp, lục hợp, ≤ 3 tên chi một dòng |
| cuối | Bảng tra + kết | bảng trên màn hình, không đọc từng dòng; callback + câu hỏi "bạn sinh tháng mấy?" |

## 4. (c) FS — Hỏi-đáp (~30')
Mẫu: "Lọ hoa bàn thờ đặt bên trái hay phải?" 36-47' (425 nghìn view); dàn ý đối thủ: lỗi phổ biến -> nguyên tắc
("Đông bình tây quả") -> giờ giấc, chọn hoa quả -> một câu chuyện thực tế -> ý nghĩa con số.
- Mỗi câu hỏi = một chương khoảng 2 phút, **tiêu đề chương đúng chữ người ta gõ tìm** (gợi ý tìm kiếm trong `briefs/fs_trends.md`).
- **Trả trong 2 câu đầu chương** (đáp án + "theo phong tục / theo truyền thống"), lý do và biến thể theo sau.
- 12–14 câu cho 30 phút; câu nhiều người tìm nhất đặt chương 1 (trả sớm); cứ 3 câu chen một câu chuyện (nhân vật minh hoạ,
  ghi rõ) hoặc một "hiểu lầm thường gặp" để đổi nhịp; câu khó / gây tranh luận để ~75%.
- Framing: "mỗi nhà có nếp riêng, nhà mình theo nếp nào thì giữ" khi các truyền thống khác nhau; không doạ.

## 5. (d) BUD — Đêm nghe lời Phật dạy (90', ngoại lệ)
Không dùng lưới 12–14 chương × 2 phút. Mẫu: "Tịnh Tâm Ngủ Ngon", "Mỗi đêm nghe 15 phút lời Phật dạy" (63-302', 0,5-7 triệu view). Chưa có số liệu giữ chân của kênh.
- Êm: không móc gắt, không cliffhanger, câu hỏi chỉ để mời quán chiếu; tempo 0,85-0,88; `pause` 1,2-2,0; nhiều câu ngắn.
- **Vẫn có 10-12 chương 7-9'** (người nghe nhảy tới bài mình thích): mỗi chương = 1 lời dạy có số kinh (Pháp Cú, Kinh Từ Bi
  Snp 1.8, Kinh Điềm Lành Snp 2.4, Kinh Mũi Tên SN 36.6...) đối chiếu `hf_sutta.py` + 1 hình ảnh / truyện ngắn + 1 nhịp thở.
- Một lời mời đăng ký nhẹ ở phút 2, không ở cuối; 10' cuối chậm dần, lặp (rải tâm từ). Lint: `--kind night`.

## 6. Beat sheet mẫu (điền trước khi viết dòng)
Câu chiến lược: **"Video này nói với [ai] rằng [thông điệp]."** Nhịp: `cảnh-HỎI-lộ trình | chuyện-ĐỈNH-lặng | ...`

| # | Phút | Chương / beat | Vai | Kỹ thuật | Cảm xúc | Vòng mở (M) / trả (T) | Chi tiết giác quan | Câu kết (cầu nối) |
|---|---|---|---|---|---|---|---|---|
| 0 | 0:00 | cold open: đoàn buôn giữa sa mạc, người lạ áo ướt nói "phía trước có nước" | móc | Imagine / scenario | căng | M1: họ có đổ nước? | cát, áo ướt, hoa sen trên xe | "Năm trăm người tin. Một người không." |
| 1 | 1:00 | lộ trình, một hình thức | hứa | Frame-then-fill | tò mò | M2: vì sao Đức Phật kể chuyện này | -- | "Bắt đầu từ thành Xá Vệ." |
| 2 | 1:10 | chuyện hiện tại | bối cảnh | Analogy với người xem | nhận ra mình | -- | tinh xá Kỳ Viên | "Đức Phật kể lại một chuyện cũ." |
| ... | | | | | | | | |
| n | 29' | kết | trả | Callback | an | T1, T2 | cát, nước | câu hỏi cho người xem |

Cột "Kỹ thuật" lấy từ catalog của faceless-explainer story-design (Make-concrete, Reveal-in-order, Contrast, Structure,
Evidence, Memory & landing). Không ghi "giải thích ý" chung chung. Ví dụ trên là dàn ý để thử -- trước khi viết phải
đối chiếu cốt truyện với nguồn (story.md).

## 7. Khuôn nhân vật (`format: "nhan_vat"`, quyết định 22/10)

Nguồn: `output/cl_staging/trao_doi/03_mimck_cl_long.md` và chốt ở `04_chot.md`. Kênh Hình Sự thắng với Long 27–32 phút:
96,8k lượt hiển thị thumbnail, thời lượng xem trung bình 9:28, 69% view từ trang chủ. Long FS/BUD chủ đề rộng giữ người xem kém.
Người dùng chốt: Long giữ **≥ 30 phút**, không rút ngắn. Format (a)–(d) vẫn theo §1–§5. Khuôn này dùng khi kể **một người thật**.

Plan phải có đúng `"format": "nhan_vat"` thì lint mới bật bốn mã ở §7.3.

### 7.1 Bảy việc

1. **Mỏ neo quen trong tiêu đề.** Tên người hoặc địa danh người Việt đã biết. Dạng dùng được:
   `[MỎ NEO VIẾT HOA] Ngoài Đời Thật: [nhân vật thật] — [chi tiết tò mò]`.
   Ví dụ của kênh mình: "Tây Du Ký Ngoài Đời Thật: Đường Tăng…".
2. **Một nhân vật, một hành trình.** Không "Lời Phật dạy về X", không "Tử vi trọn đời một tuổi".
3. **Cold open** là một cảnh có thật, có thời điểm hoặc địa điểm, thì hiện tại, dừng ở đỉnh. BUD: mọi chi tiết có trong nguồn, không thêm (luật truyện kinh).
4. **2–3 câu hỏi lớn trong 90 giây đầu.** Mỗi câu hẹn rõ, ví dụ "lời đáp ở chương sáu?". Lời đáp đặt giữa hoặc cuối bài, đúng chương đã hẹn — không trả trong cold open. Đây là lộ trình mở đầu. Không thêm lộ trình thứ hai. Luật "ba câu hỏi tối đa một lần trong năm tập" (§1) không áp vào format này.
5. **12–16 chương.** Mỗi chương một bước ngoặt của nhân vật.
6. **Lời trích** đọc bằng giọng thứ hai nếu tập bật `tts.alt`: trong `build_X.py` đặt `alt=True` trên đúng dòng (plan ghi số dòng, từ 1, vào `tts.alt.lines`). Nguyên văn kinh vẫn đối chiếu `hf_sutta.py` trước khi gắn `alt=True` (line-rules §5). Tên riêng trong lời đọc là âm Hán Việt hoặc tên Việt hoá quen. Tên gốc chỉ hiện trên màn hình.
7. **Chi tiết tranh cãi** gắn "theo truyền thuyết" hoặc "chú giải kể". Không viết thành khẳng định.

Sau câu hỏi hẹn, vẫn một câu cảnh cụ thể trong 90 giây đầu (luật 4 của SKILL). Câu ấy chưa phải lời đáp đã hẹn.

### 7.2 Cách đếm

- Cold open = các dòng **trước** thẻ `**...**` đầu tiên. Không tính vào 12–16.
- Chương N = thẻ thứ N theo thứ tự. Chương 1 là thẻ đầu. Không đọc số trong tiêu đề, không dùng số La Mã ("chương II" không được tính).
- Viết "chương sáu" hoặc "chương 6".
- 90 giây đầu và thời lượng dùng đồng hồ của lint: giây thật nếu có `out/<id>.json` khớp số dòng; không thì số token ÷ 185 mỗi phút.
- `protagonist` là đúng cụm tên trong lời đọc. Cụm ấy phải có trong cold open và trong ít nhất 70% số thẻ.

```json
"format": "nhan_vat",
"protagonist": "Đường Tăng",
"questions": [
  {"id": "q1", "chapter": 6},
  {"id": "q2", "chapter": 12}
],
"answers": [
  {"chapter": 6, "answers": ["q1"]},
  {"chapter": 12, "answers": ["q2"]}
]
```

Mỗi chương được câu hỏi trong 90 giây đầu gọi tên phải có một `questions[].id`, và `answers` của đúng chương ấy phải chứa id đó.

### 7.3 Lint (CẢNH BÁO, chỉ khi `format` đúng `nhan_vat`)

| Mã | Đạt khi |
|---|---|
| `CAU_HOI_HEN_CHUONG` | ≥ 2 câu hỏi (có dấu ?) hẹn "chương N" trong 90 giây đầu; N có thẻ; `answers` của chương N chứa mọi id khai ở `questions` |
| `SO_CHUONG` | 12–16 thẻ. Không cộng thêm đích 12–14 của bản trụ (`so_chuong`) |
| `THOI_LUONG` | đồng hồ lint ≥ 30 phút |
| `NHAN_VAT` | có `protagonist`; tên trong cold open; tên trong ≥ 70% thẻ |
