# Luật từng dòng cho TTS VieNeu (BUD / FS)

TTS đọc **từng dòng `say()`** thành một đoạn tiếng, nghỉ `pause` (mặc định 0,42 giây) rồi sang dòng sau. Người nghe không
nhìn chữ: mỗi dòng phải nghe hiểu ngay ở lần đầu (narration.md: "đọc to lên, nghe như robot thì viết lại").
Lint: `python long_script_lint.py <plan|nháp.txt> [--only id]` bắt phần lớn các luật dưới đây (mã lỗi trong ngoặc).

## 1. Độ dài (cau_dai, it_cau_ngan)
- Bản nháp: **một dòng = một câu**. Gộp 2-3 câu vào một `say()` chỉ khi chúng là một khối (hỏi + đáp, lời kinh + nguồn,
  hai vế đối) và cả dòng ≤ ~45 tiếng.
- Câu nói: trung vị **12-16 tiếng**, không câu nào > **35 tiếng ĐỌC**. Đếm theo cách đọc, không theo chữ viết: chữ số
  đọc ra dài (1983 = "một nghìn chín trăm tám mươi ba" = 7 tiếng; 2027 = 7; 1.068 = 8). Runner đếm token nên câu
  "Tuổi Tý gồm những người sinh năm âm lịch 1960, 1972, 1984, 1996 và 2008." (15 token, **43 tiếng đọc**) lọt qua runner
  -- chính các câu kiểu này nằm ở 5/8 lần rơi dốc nhất của F6 (evidence.md).
- Tách câu dài ở dấu hai chấm, "mà là", "nhưng", "còn". Không tách thành mảnh cụt ("Hỏa là đỏ, cam. Thổ là vàng đất, nâu."
  từng làm TTS hỏng -- long-video §2): mỗi mảnh vẫn là một câu đủ chủ vị.
- **Câu ngắn ≤ 6 tiếng: ~1 câu mỗi 4-6 câu** (≥ 1/8 tổng, tốt nhất 1/6-1/4), đặt SAU khoảnh khắc: phán định ("Không phải."),
  cảm xúc ("Bà khóc."), kết cảnh ("Ngài biết."). Không ba câu ngắn liền trừ ở cao trào. Đoạn có câu ngắn rơi chậm hơn
  nền 4-8 điểm %/phút; B5 có người tua lại đúng câu "Và khi trời gần sáng, Ngài biết."
- Nhịp mẫu: dài - vừa - NGẮN; hoặc hỏi - lặng - trả. Đổi độ dài câu liên tục (narration.md "vary sentence length").

## 2. Con số (cau_dai, liet_ke, tts_gach_noi)
Cách VieNeu đọc (đo bằng `vieneu_utils.phonemize_text`, 14/10/2026):

| Viết | Đọc ra | Dùng? |
|---|---|---|
| `1983`, `2027`, `2008` | một nghìn chín trăm tám mươi ba / hai nghìn không trăm hai mươi bảy / ... lẻ tám | được, tối đa 2 năm một câu |
| `1.068 m`, `2.500 năm`, `1,5 triệu` | một nghìn không trăm sáu mươi tám mét / hai nghìn năm trăm / một phẩy năm | được |
| `12/7/2025`, `23:00`, `3/4`, `50%` | mười hai tháng bảy năm... / hai mươi ba giờ không phút / ba trên bốn / năm mươi phần trăm | được nhưng nên viết chữ |
| `thế kỷ VIII`, `Chương II` | thế kỷ tám / chương hai | được |
| **`1-3 lần`, `23-1 giờ`** | **"ngày một tháng ba lần"** | KHÔNG: viết "từ một đến ba lần", "từ mười một giờ đêm đến một giờ sáng" |
| **`DN 16`, `MN 135`, `SN 36.6`** | **"đi-en mười sáu"** (kiểu Anh) | KHÔNG: lời đọc "Trường Bộ, kinh số mười sáu"; mã kinh để trên màn hình (`quote` source) |
| `(tức là Mộc)` | đọc liền, mất ngoặc, không ngắt hơi | viết bằng dấu phẩy |

- Năm sinh, tuổi âm, số tiền: chữ số + `**đậm**` khi là chữ khoá (`**42**`). Số đếm trong văn kể: viết chữ ("ba lần",
  "năm người bạn"). Giọng có thể làm tròn, màn hình giữ số chính xác (narration.md).
- Bảng ≥ 4 năm sinh / ≥ 4 ô: **lên màn hình** (`ledger` khi ≥ 4 dòng nhiều cột, `list`/`compare` khi 2-3 dòng -- long-video §0),
  lời đọc chỉ nói 1-2 ví dụ và cách tra: "Nếu bạn sinh năm 1984, bạn ở dòng thứ ba."

## 3. Liệt kê và tên (liet_ke, nhieu_chi, ten_con_vat)
- Tối đa **3 mục** trong lời đọc, mục thứ ba bất ngờ nhất (long-video §2). ≥ 4 tên chi trong một dòng: runner **chặn**
  (TTS đọc lồng, hỏng cả 3 lần thử). Lộ trình mở đầu không đọc danh sách địa danh (B5 mất 17 điểm khi đọc 4 địa danh).
- FS gọi con giáp bằng **tên chi** (Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi), không "tuổi Lợn/Dê"
  (runner chặn với series fs).
- Tên Pali / Phạn / ngoại: **dùng tên Hán-Việt hoặc phiên âm Việt**: Xá Lợi Phất (không "Sāriputta" -> đọc thành "ét-ri-pưt-ơ"),
  Cấp Cô Độc (không "Anāthapiṇḍika" -> "en-ta-pi-i-cơ"), Vi Đề Hi (không "Vedehikā" -> "viđ-hích"). Chưa có tên Việt:
  bỏ dấu Pali, viết tách âm ("Su-bha" vẫn đọc kiểu Anh; ưu tiên gọi theo vai: "chàng trai trẻ Subha" một lần rồi "chàng").
  Lint `tts_dau_la` bắt dấu ā ī ū ṅ ñ ṭ ḍ ṇ ḷ ṃ.
- Viết tắt chữ hoa (UNESCO, DN, TP) đọc kiểu Anh -> viết đủ (lint `tts_viet_tat`).

## 4. Chữ khoá và tiêu đề chương (DSL build_X.py)
- `**cụm**` giữa câu = chữ khoá (chữ động, callout). **Một cụm mỗi câu, 1-4 tiếng**, là danh từ / con số mang nghĩa
  ("**da bọc lấy xương**", "**năm tuổi**", "**42**"), không phải hư từ. Câu không có visual, ảnh hay chữ khoá thì engine
  lấy mấy chữ đầu câu làm tiêu đề lớn (`bare_lines`, lỗi F1/B1 01/10) -> mỗi câu cần một chữ khoá hoặc một visual.
- `chap("Tiêu đề")` = dòng in đậm TRỌN -> thẻ chương + mốc trong mô tả + điểm cắt render. Tiêu đề **được đọc to**:
  2-7 tiếng, là điều người xem tìm hoặc một cảnh ("Tuổi Tý", "Lọ hoa đặt bên nào?", "Đêm dưới cội Bồ Đề"); không
  "Phần 1", không định nghĩa ("X là gì?") làm chương thứ hai (F1, F3, F6 rơi mạnh ở đúng chương ấy).
- Không đặt `**...**` trọn dòng cho câu thường: nó sẽ thành chương.

## 5. Nghỉ và tốc độ (preset C, long-video §0)
- `pause=`: sau câu đỉnh 1,0-1,4 giây; sau câu hỏi lớn 0,8-1,2; quanh thẻ chương 1,7-2,0 (`chap()` = 2,0). B5 dùng
  0,6-1,0 sau câu thường có nhấn, 1,7-1,8 trước / ở thẻ chương.
- `tempo=` 0,85-0,88 cho câu đỉnh BUD (mặc định 0,91); FS 0,96 không đổi. `SILENCE.append(n)` / `DROPS.append(n)` cho
  khoảnh khắc lớn (nhạc lặng). Không tăng vang / nhạc khi chưa hỏi người dùng.
- `alt=True` (giọng Quang Sơn v3) **chỉ** cho nguyên văn kinh đã đối chiếu `hf_sutta.py`, ≤ 2 câu liền.

## 6. Thoại trong truyện (hai_luot_thoai)
- Một lượt thoại một dòng; dẫn người nói TRƯỚC câu thoại ("Người thị giả thưa: giờ Tý."); câu thoại ≤ 20 tiếng.
- Một giọng TTS đọc mọi vai -> vai phải nghe ra từ chữ: xưng hô (ta / ngươi cho vua, quỷ; con / thưa cho người dưới;
  Như Lai / các con cho Đức Phật), động từ dẫn (hỏi, thưa, quát, thì thầm). Không ngoặc kép lồng nhau.
- Lời Đức Phật trong truyện Tiền Thân phần văn xuôi là **chú giải**, không phải kinh: dẫn "theo truyện kể" (story.md).

## 7. Cụ thể trước, trừu tượng sau (truu_tuong_lien, ly_thuyet_som)
- Mỗi cảnh ≥ 1 chi tiết giác quan (thấy / nghe / chạm / đói / lạnh): "da bọc lấy xương", "ngựa đá lấm bùn",
  "cánh cửa sổ lúc giờ Tý". Chi tiết phải có trong nguồn, hoặc là bối cảnh trung tính (trời tối, gió) -- không thêm vật hay
  hành động làm đổi cốt truyện (story.md).
- Không quá 4 câu trừu tượng liền; sau mỗi khái niệm là một ví dụ có số / tên / cảnh trong ≤ 2 câu
  (story-design: "Concretization", "Worked example with real numbers").
- Định nghĩa ≤ 2 câu và nằm TRONG câu trả lời, không thành chương riêng trước lần trả đầu.

## 8. Ngôi thứ hai, giọng
- Gọi khán giả là **"bạn"**; BUD dùng "chúng ta" khi cùng thực tập / quán chiếu; tự xưng "mình" trong lời mời bình luận.
- Không phán: FS "được xem là", "theo truyền thống", "người xưa khuyên"; có câu "kiến thức truyền thống để tham khảo";
  không doạ ("lộc rời đi", "90% làm sai"), không hứa tiền. BUD: lời Phật chỉ khi có số kinh; hình ảnh không từ kinh thì nói
  "một hình ảnh quen thuộc trong truyền thống Phật giáo" (long-video §2).
- Câu hỏi trực tiếp cho người xem ở re-hook ("Bạn sinh năm nào trong năm năm ấy?") giữ người nghe hơn câu khẳng định dài.

## 9. Vòng mở / trả và câu cầu nối (it_vong_mo, khong_tra_vong, thieu_rehook, ket_chuong_tom_tat)
Lint nhận diện vòng bằng cụm từ; viết rõ để người nghe (và lint) nghe ra:
- Mở: "lát nữa", "ở cuối video", "ta sẽ quay lại...", "hãy giữ câu hỏi này", "còn một điều", "nhưng đó chưa phải tất cả",
  "câu hỏi thứ hai".
- Trả: "còn nhớ...", "hãy quay lại đêm ấy", "câu trả lời là...", "đó là lý do...", "giờ thì bạn đã hiểu...".
- Kết chương = câu cầu nối mở sang chương sau (KHÔNG "Tóm lại", "Như vậy" -- F4, F1 rơi 29-31% ở chương cuối kiểu đó).
- Trả một vòng thì câu kế tiếp mở vòng mới (F6 chương tuổi Mùi mất 41% ngay sau câu trả).

## 10. Câu mở và từ lặp (mo_cau_lap, tu_lap)
- Không quá ~2% số câu mở bằng cùng hai tiếng. F6 có 61 câu "Người sinh năm...", 12 câu "Nước gặp...": đổi khuôn
  (bắt đầu bằng năm, bằng hệ quả, bằng câu hỏi, bằng so sánh với năm sinh kề).
- Điệp có chủ ý (ba câu "Lần thứ nhất / thứ hai / thứ ba") được, tối đa 3.
- Cùng một cụm 2 tiếng thường ≥ 3 lần trong 5 dòng: thay bằng đại từ hoặc từ đồng nghĩa.

## 11. Lời gọi đăng ký (cta_giua, cta_nhieu)
- Tối đa 2 câu, đặt SAU lần trả vòng cuối, ngay trước câu hỏi bình luận. Không "hãy xem đến cuối", "nếu bạn thuộc những tuổi
  khác, cũng xem tiếp" ở phút đầu (F1, F3 rơi 16-27 điểm quanh các câu ấy).
