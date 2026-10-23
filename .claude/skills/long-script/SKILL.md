---
name: long-script
description: "Viết kịch bản lời đọc Long BUD (Phật giáo) và FS (Phong Thuỷ / tử vi) bằng TTS VieNeu. Bản trụ ~30 phút: plan.md cho người dùng duyệt trước khi viết lời; cold open ≤ 60 giây (cảnh căng, thì hiện tại, dừng ở đỉnh); chạm người xem ≤ 30 giây; lộ trình ≤ 75 giây, đổi 1 trong 6 hình thức; 12-14 chương khoảng 2 phút, kết bằng câu móc; cung A→B và mô-típ ≥ 3; phần thưởng ở 50%, cảnh mạnh ở 75%; kết bằng câu hỏi. Khuôn nhân vật (format nhan_vat, 22/10): một người thật, ≥ 30 phút, 12–16 chương, câu hỏi hẹn chương. Rồi beat sheet, luật TTS, long_script_lint.py, soát sự thật, build_X.py. Đêm nghe 90 phút là ngoại lệ (--kind night). Dùng khi viết hoặc sửa kịch bản Long. Không dùng cho Short."
---

# Kịch bản video dài BUD / FS

Skill này lo **chữ**: từ ý tưởng đến `script[]` trong `build_X.py`. Phần hình, render, đăng là skill `long-video`
(đọc §3 Soát sự thật, §4 Plan của nó). Luật dòng chi tiết hoá checklist giữ chân của `long-video` §2.
Khung chương của bản trụ ~30 phút lấy quyết định 21/10 (mục 0), mới hơn câu "chương 3–6 phút" trong `long-video` §0.
Mỗi luật có nguồn: `references/sources.md` hoặc `references/evidence.md` (B3, B5, F1, F3, F4, F6) và
`output/cl_staging/long/phan_tich_long_2026-10-21.md`.

Tốc độ đọc đo được trên 30 bản trụ: **185 tiếng/phút kể cả nghỉ** (179-189). Ngân sách: 30 phút ≈ 5.500 tiếng,
45 ≈ 8.300, 60 ≈ 11.000, 90 (đọc chậm) ≈ 14.000-15.000.

## 0. Mười luật quan trọng nhất (đọc trước khi viết)
| # | Luật | Bằng chứng (evidence.md) |
|---|------|--------------------------|
| 1 | **Cold open ≤ 60 giây: cảnh căng nhất, thì hiện tại, dừng ở đỉnh, chưa giải thích, không chào.** Chưa đóng vòng ấy. | FS Long 30 phút mất 75–92% người xem trong 90 giây đầu (21/10/2026). B5 mất 41 điểm đúng lúc lộ đáp án rồi vào lộ trình. |
| 2 | **Lộ trình xong trước giây 75, một trong 6 hình thức, khác tập liền trước.** Không "Video này sẽ..." trước giây 25. Không đọc danh sách. | Câu nói về video nằm trong cửa sổ rơi ở B3 (giây 12), F1 (18), F3 (20), B5 (32), F6 (35). |
| 3 | **Không chương lý thuyết / định nghĩa trước lần trả đầu tiên.** Định nghĩa ≤ 2 câu, nhét vào trong câu trả lời. | F6 chương "Chìa khóa..." 3 phút mất 40% (13,4%/phút); F1 "Thái Tuế là gì?" 16,9%/phút so với 8-11 ở chương từng tuổi; F3 "Năm tuổi là gì?" 38%/phút so với 4,7 ở chương sau. |
| 4 | **Trả một phần thật trong 90 giây; chương nội dung đầu tiên bắt đầu ≤ 2:30.** Video gom nhiều nhóm khán giả (12 tuổi) phải cho mỗi người biết phần mình ở đâu. | F6: −52 điểm ở giây 21-42, phần tuổi Tý tới 4:17, còn 29% ở phút 1. F4 (trả ngay tuổi Tuất): còn 70% ở phút 1, tốt nhất kênh. |
| 5 | **Mỗi câu ≤ 35 tiếng ĐỌC** (chữ số đếm theo cách đọc: 1983 = 7 tiếng). **Không đọc quá 3 năm sinh / tên / mục trong một câu**; phần còn lại lên bảng màn hình. | F6: 5/8 lần rơi dốc nhất sau phút 1 đúng câu "...gồm những người sinh năm 1960, 1972, 1984, 1996 và 2008" (40-44 tiếng đọc; runner đếm 15 token nên không báo). |
| 6 | **Trả vòng nào, mở vòng mới ngay câu sau.** | F6 chương tuổi Mùi ("nhiều người chờ nhất"): mất 41% trong chương, rơi ngay sau câu trả "năm tuổi không có nghĩa là năm xấu". |
| 7 | **Không kết chương / video bằng "Tóm lại"; không đọc bảng tổng hợp từng dòng; lời gọi đăng ký ≤ 2 câu, sau lần trả cuối.** | F4 chương cuối (mở bằng "Tóm lại") mất 31% trong 50 giây; F1 chương cuối −29%; F6 bảng tổng hợp đọc to: −40% trong 1,1 phút. |
| 8 | **Câu ngắn ≤ 6 tiếng mỗi 4-6 câu, đặt sau khoảnh khắc; câu kinh / câu quen ở cao trào.** | Đoạn có câu ngắn rơi chậm hơn nền của chính video 4-8 điểm %/phút; B5 có người tua lại đúng "Và khi trời gần sáng, Ngài biết.", hồ sen, "Hãy tự mình làm ngọn đèn". |
| 9 | **Thẻ chương là mục lục để người xem nhảy tới**: tiêu đề = điều người xem tìm; mỗi chương tự đứng được (nhắc khái niệm 1 câu, móc riêng). | F6: đường giữ chân TĂNG +6/+7/+7 điểm đúng ở thẻ "Tuổi Mão", "Tuổi Tỵ", "Tuổi Ngọ" (người xem nhảy theo mốc chương). |
| 10 | **Tên Pali / Phạn, mã kinh, gạch nối giữa hai số phải viết theo cách đọc Việt.** | `phonemize_text` 14/10: "Jāṇussoṇi" ra âm Anh vỡ, "DN 16" -> "đi-en", "1-3 lần" -> "ngày một tháng ba lần". |

Luật dòng vẫn giữ: ≤ 3 tên chi một dòng (runner chặn), FS gọi tên chi, gọi người xem là "bạn", câu ≤ 35 tiếng đọc,
liệt kê ≤ 3 mục, ≤ 90 giây không ngắt nhịp, ≥ 3 vòng mở được đóng, mô-típ ≥ 3 lần, kết video = callback + một câu hỏi thật.
`long-video` §0 còn câu "chương 3–6 phút" từ trước 21/10. Khi viết bản trụ ~30 phút, làm theo khung dưới đây.

### Khung vĩ mô bản trụ ~30 phút (quyết định 21/10; chi tiết và plan.md: `references/formats.md` §1)

Giữ độ dài khoảng 30 phút cho cả FS và BUD. 12–14 chương, mỗi chương khoảng 2 phút.

- **Cold open ≤ 60 giây.** Cảnh căng nhất, thì hiện tại, dừng đúng đỉnh, chưa giảng. Không "kính thưa", không "xin chào".
  FS: một người tuổi Sửu đứng trước cổng, năm 2027, bản dự toán trên tay, la bàn hiện hai chữ trái nhau, cửa chưa mở.
  BUD: nước dựng thành vách, người mù cầm bát, câu trong bát chưa được đọc.
- **Chạm người xem ≤ 30 giây.** FS gọi năm sinh và tên chi ở câu 2 hoặc 3 ("Bạn sinh năm Ất Sửu thì đang đứng đúng chỗ này.").
  BUD một nỗi khổ đời thường ("Bạn cũng từng hứa một câu, rồi sợ không giữ nổi.").
- **Lộ trình ≤ 75 giây**, đúng một hình thức, khác tập liền trước cùng kênh. Sáu hình thức: chặng đường; cảnh hẹn trước;
  câu hỏi duy nhất; lời thách; bản đồ bằng hình (đọc một câu, màn hình hiện các chương); nghịch lý.
  "Ba câu hỏi" tối đa một lần trong năm tập.
- **Kết chương bằng câu móc**, câu mở sang chương sau. Câu kết không bắt đầu bằng "tóm lại" hay "như vậy".
- **Cung A→B** viết một câu trong plan (từ trạng thái A thành trạng thái B). **Mô-típ** lặp ít nhất 3 lần: mở, giữa, kết.
- **Phần thưởng ở 50%** (thứ tiêu đề đã hứa: FS là câu trả lời năm/tháng; BUD là chỗ nhận ra trong truyện).
  **Cảnh mạnh ở 75%** (quyết định có hậu quả, hoặc lựa chọn khó nhất còn lại).
- **Kết mở** bằng một câu hỏi cho người xem, sau khi gọi lại cảnh mở và đóng các vòng.

### Khuôn nhân vật (`format: "nhan_vat"`, quyết định 22/10)

Long giữ **từ 30 phút trở lên**. Không rút ngắn. Dùng khuôn này khi tập kể **một người thật, một hành trình**. Format (a)–(d) vẫn theo khung 21/10. Chi tiết, mẫu tiêu đề và JSON: `references/formats.md` §7.

| # | Việc |
|---|---|
| 1 | Tiêu đề có mỏ neo quen: tên người hoặc địa danh người Việt đã biết. Dạng: "[MỎ NEO VIẾT HOA] Ngoài Đời Thật: [nhân vật thật] — [chi tiết tò mò]". Ví dụ: "Tây Du Ký Ngoài Đời Thật: Đường Tăng…". |
| 2 | Một nhân vật, một hành trình. Không chủ đề rộng ("Lời Phật dạy về X", "Tử vi trọn đời một tuổi"). |
| 3 | Cold open là một cảnh có thật, có thời điểm hoặc địa điểm. BUD: mọi chi tiết có trong nguồn, không thêm. |
| 4 | 2–3 câu hỏi lớn trong 90 giây đầu. Mỗi câu hẹn rõ trả lời ở chương N. Lời đáp ở giữa hoặc cuối, đúng chương đã hẹn. Đây là lộ trình mở đầu của khuôn này, không thêm một lộ trình thứ hai. Luật "ba câu hỏi tối đa một lần trong năm tập" không áp vào format này. |
| 5 | 12–16 chương. Mỗi chương một bước ngoặt của nhân vật. |
| 6 | Lời trích: `alt=True` (giọng thứ hai, `tts.alt.lines`) nếu tập bật giọng ấy. Nguyên văn kinh vẫn phải đối chiếu `hf_sutta.py` trước. Tên riêng đọc âm Hán Việt hoặc tên Việt hoá quen; tên gốc chỉ hiện trên màn hình. |
| 7 | Chi tiết tranh cãi gắn "theo truyền thuyết" hoặc "chú giải kể". Không khẳng định. |

Mười luật ở trên vẫn giữ. Chỗ khác khung 21/10: số chương là 12–16 thẻ (không phải 12–14), sàn thời lượng là 30 phút, và câu hỏi mở phải gọi đúng số chương. Sau câu hỏi hẹn, vẫn một câu cảnh cụ thể trong 90 giây đầu; đó chưa phải lời đáp đã hẹn.

Plan ghi `"format": "nhan_vat"`, `"protagonist"`, `"questions"` và `"answers"` như `formats.md` §7. Lint (CẢNH BÁO, chỉ khi có đúng format ấy): `CAU_HOI_HEN_CHUONG`, `SO_CHUONG`, `THOI_LUONG`, `NHAN_VAT`.

## 1. Quy trình — làm theo thứ tự, mỗi bước có cổng
1. **Brief** (5 dòng, ghi vào docstring đầu `build_X.py`): format (a/b/c/d/e ở §2) + thời lượng + ngân sách tiếng;
   câu chiến lược **"Video này nói với [ai] rằng [thông điệp]"**; neo tìm kiếm (`hf_trends.py`, `briefs/<kênh>.md`,
   `hf_novelty.py check`); câu khán giả gõ tìm (dùng làm tiêu đề chương); motif. *Cổng*: nói được thông điệp trong 1 câu.
2. **Gói nghiên cứu** (phương pháp skill `research`: nguồn gốc, mỗi khẳng định một nguồn). Liệt kê sự kiện kèm nhãn
   `[kinh số…] [chú giải] [truyền thống] [truyền thuyết] [sử: sách] [dân gian] [code]`. BUD: mọi lời Phật đối chiếu
   `python hf_sutta.py <uid> "<cụm>"` (kệ Tiền Thân: `hf_sutta.py ja<N>`); FS: can chi / nạp âm / tuổi âm / sao hạn
   **sinh bằng code** (`canchi.py`, `amlich.py`, `batrach.py` trong `output/cl_staging/long/`), lời quẻ chỉ từ
   `hf_kinhdich.py`. *Cổng*: không câu nào trong kịch bản mang thông tin chưa có trong gói.
3. **plan.md cho người dùng duyệt, trước khi viết một dòng lời.** Khuôn `references/formats.md` §1 (vì sao chọn đề,
   đóng gói, cung A→B, cold open, bảng vòng, mô-típ, 12–14 chương, hình thức lộ trình, mốc 50% và 75%).
   Khuôn nhân vật dùng §7 (12–16 chương, ≥ 30 phút), không dùng dàn 12–14 của §1.
   Chép bảng vòng vào plan JSON: `"vong": [{"mo": "câu hỏi mở", "dong": "cụm chữ nằm ở chương đóng"}]`.
   *Cổng*: người dùng đã duyệt plan. Chưa duyệt thì dừng, không viết `say()`.
4. **Beat sheet** (`references/formats.md` §6 mẫu), bám plan đã duyệt: mỗi chương một dòng — phút, vai (móc / căng /
   bước ngoặt / trả / bài học / cầu nối), kỹ thuật có tên, cảm xúc, vòng mở/trả, chi tiết giác quan, câu kết là câu móc.
   Dòng nhịp: `cảnh-HỎI-trả-chương-chuyện-ĐỈNH-lặng-cầu nối…`. *Cổng*: xoá hết dòng bằng chứng mà thông điệp vẫn đứng;
   xoá dòng thông điệp mà video vẫn "chạy" nghĩa là nó chỉ là bản liệt kê (story-spine §2).
5. **Viết từng dòng** theo `references/line-rules.md` (độ dài, số, nhịp, chữ khoá, thoại, giác quan, ngôi thứ hai,
   bẫy TTS). Truyện: `references/story.md` (mẫu kể trung thành nguồn, nhãn truyền thuyết).
6. **Tự soát bằng lint** — 0 LỖI, mỗi CẢNH BÁO sửa hoặc ghi lý do trong docstring:
   ```bash
   python long_script_lint.py nhap.txt                       # bản nháp: mỗi dòng một dòng say(), **tiêu đề chương**
   python long_script_lint.py output/cl_staging/long/plan_long_wNN.json --only <id> --strict
   python long_script_lint.py <plan> --only <id> --kind night   # Đêm nghe lời Phật dạy
   ```
   Lint gọi nguyên `hf_batch_render.retention_issues` (dòng "runner") và đo thêm: câu > 35 tiếng đọc (`cau_dai`, LỖI),
   liệt kê ≥ 4 (`liet_ke`), "quý vị" (`quy_vi`), chương mở không câu hỏi/móc (`chuong_mo_khong_moc`),
   cold open có lời chào (`cold_open_chao`), kết chương "tóm lại" / "như vậy" (`ket_chuong_tom_tat`),
   đoạn > 90 giây không ngắt (`khong_ngat_nhip`), bảng `vong` thiếu chỗ đóng (`vong_khong_dong`),
   re-hook 25/50/75%, bản trụ ≥ 20 phút mà không đủ 12–14 chương (`so_chuong`) hoặc chương > 3,5 phút (`chuong_dai`).
   Plan `format: "nhan_vat"` không dùng đích 12–14 ấy. Lint bật thêm `CAU_HOI_HEN_CHUONG`, `SO_CHUONG` (12–16 thẻ),
   `THOI_LUONG` (≥ 30 phút), `NHAN_VAT` (`protagonist` trong cold open và ≥ 70% số thẻ).
   Có `out/<id>.json` thì dùng giây thật.
7. **Soát sự thật** (long-video §3, bắt buộc): đọc lại từng câu có "kinh", "Phật dạy", "Ngài nói", con số, năm sinh;
   câu nào không có trong gói nghiên cứu thì xoá hoặc gắn nhãn. FS: chạy lại code sinh số, so từng con số trong lời đọc.
8. **Bàn giao** `build_X.py` (mẫu `build_B20.py`, `build_F20.py`): `say(text, pause=, tempo=, media=, alt=)`, `chap(t)`
   (= dòng in đậm trọn, `pause=2.0`), `vis(n, spec)` / `quote(n, source)` (skill `motion-library`), `SILENCE`, `DROPS`.
   `python build_X.py --words` (đếm) -> `python build_X.py` (ghi plan) -> lint lại trên plan -> long-video §4 trở đi.
   Render ≈ 1,7× thời lượng (60 phút ≈ 1 giờ 40), TTS cache theo câu: sửa chữ sau render chỉ tốn câu đã sửa.

## 2. Năm format (chi tiết, khung thời gian, beat sheet mẫu: `references/formats.md`)
| Format | Dài | Xương sống | Nguồn mẫu |
|--------|-----|-----------|-----------|
| (a) BUD Truyện Tiền Thân | ~30' | 1 truyện sâu, 12-14 chương khoảng 2 phút, vẫn đủ 5 phần Tiền Thân (hiện tại, quá khứ, kệ, nhận diện, bài học). Cold open = khoảnh khắc căng nhất | Quang Vô Sắc TV tập 1 (45', 180 nghìn view/27 ngày); bản mình giữ ~30 phút (21/10) |
| (b) FS Tử vi trọn đời tuổi X + 2027 | ~30' | cold open một quyết định năm 2027, gọi năm sinh/chi trong 30 giây, rồi 12-14 chương khoảng 2 phút (bản mệnh, sao hạn nam/nữ, giai đoạn đời, tháng, quý nhân) | đối thủ "Quý Hợi 1983" 30-58'; FS 30 phút của kênh rơi 75–92% trong 90 giây đầu |
| (c) FS Hỏi-đáp | ~30' | mỗi câu hỏi tìm kiếm = một chương khoảng 2 phút, **trả trong 2 câu đầu chương**, 12-14 câu | "Lọ hoa bàn thờ đặt bên trái hay phải" 36-47' (425 nghìn view) |
| (d) BUD Đêm nghe | 90' | ngoại lệ: êm, không móc gắt, 10-12 chương 7-9'; lint `--kind night` | "Đêm nghe lời Phật dạy" 63-143' (5-7 triệu view) |
| (e) Khuôn nhân vật | ≥ 30' | một người thật, một hành trình; cold open có thời điểm hoặc địa điểm; 2–3 câu hỏi hẹn chương; 12–16 chương. Plan `format: "nhan_vat"` | Kênh Hình Sự, Long 27–32 phút (formats.md §7) |

## 3. Tài liệu
- `references/evidence.md` — đường giữ chân B3, B5, F1, F3, F4, F6 khớp với câu đang đọc: chỗ rơi, chỗ giữ, số liệu, giới hạn mẫu.
- `references/line-rules.md` — luật từng dòng cho TTS VieNeu (bảng cách đọc đo bằng `phonemize_text`).
- `references/formats.md` — khuôn plan.md, khung 30 phút (Đêm nghe 90 phút), 4 format, khuôn nhân vật §7, beat sheet mẫu.
- `references/story.md` — mẫu kể chuyện trung thành nguồn (Tiền Thân, sử, truyện minh hoạ), nhãn truyền thuyết.
- `references/sources.md` — luật nào lấy từ đâu (hyperframes-creative, faceless-explainer, research, long-video, số liệu kênh).
- `long_script_lint.py` (gốc repo) + `tests/test_long_script_lint.py`.

## Thumbnail Long V2 (quyết định 21/10; ticket 54b)
- Mỗi Long chuẩn bị ba bản A/B/C để Lead chọn; mỗi thumbnail chỉ có 0–3 từ, từ khóa viết HOA, bám chi tiết trong cold open.
- Mỗi bản có một chủ thể lớn, rõ: BUD dùng ảnh chụp tượng/phù điêu/tranh cổ có nguồn công cộng hoặc giấy phép tự do; FS dùng bảng, la bàn hoặc bát quái. Không tự vẽ/tạo mặt Đức Phật.
- Không thêm nhãn series, dòng hứa hẹn hay chữ phụ. Bản xuất 1280×720 và bản xem 168×94; ghép tờ so sánh cả ba bản ở hai cỡ để Lead duyệt.
- Kiểm tra thủ công ở 168 px: chữ đọc rõ, chủ thể nhận diện được, với ảnh tượng thì không cắt đầu hay đặt chữ lên mặt. Lead chọn và tự cập nhật ảnh đã đăng.
- Công cụ: `hf_long_thumbnail.make_v2(...)`; ví dụ gọi A/B/C riêng bằng `variant="A"`, `"B"`, `"C"`.
