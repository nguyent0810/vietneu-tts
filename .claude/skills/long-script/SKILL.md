---
name: long-script
description: "Viết kịch bản lời đọc cho video dài 30-90 phút (BUD Phật giáo, FS Phong Thuỷ / tử vi) đọc bằng TTS VieNeu, có mid-roll: brief -> gói nghiên cứu có nguồn -> khung vĩ mô 30/45/60/90 phút (cold open, lộ trình, chương 4-8 phút, re-hook 25/50/75%, vòng mở/trả) -> beat sheet -> viết từng dòng theo luật TTS tiếng Việt -> long_script_lint.py -> soát sự thật -> bàn giao build_X.py. Luật rút từ đường giữ chân thật của kênh. Dùng khi viết hoặc sửa kịch bản Long: Truyện Tiền Thân, Tử vi trọn đời tuổi X, Hỏi-đáp phong thuỷ, Đêm nghe lời Phật dạy, bản trụ 30 phút. Không dùng cho Short."
---

# Kịch bản video dài BUD / FS

Skill này lo **chữ**: từ ý tưởng đến `script[]` trong `build_X.py`. Phần hình, render, đăng là skill `long-video`
(đọc §0, §3 Soát sự thật, §4 Plan của nó). Hai skill không mâu thuẫn: luật ở đây chi tiết hoá checklist giữ chân của
`long-video` §2 và thêm luật mới có số liệu. Mỗi luật có nguồn: `references/sources.md` (sách nghề) hoặc
`references/evidence.md` (đường giữ chân thật của B3, B5, F1, F3, F4, F6).

Tốc độ đọc đo được trên 30 bản trụ: **185 tiếng/phút kể cả nghỉ** (179-189). Ngân sách: 30 phút ≈ 5.500 tiếng,
45 ≈ 8.300, 60 ≈ 11.000, 90 (đọc chậm) ≈ 14.000-15.000.

## 0. Mười luật quan trọng nhất (đọc trước khi viết)
| # | Luật | Bằng chứng (evidence.md) |
|---|------|--------------------------|
| 1 | **20-30 giây đầu là một cảnh cụ thể, và KHÔNG đóng vòng của nó.** Đừng lộ đáp án bí ẩn mở đầu trước khi một vòng lớn hơn đã mở. | B5: 0-18 giây chỉ mất 4 điểm; 18-55 giây mất 41 điểm, đúng lúc câu 5 lộ "Đức Phật" rồi vào thẻ chương + lộ trình. |
| 2 | **Không "Video này sẽ..." trước giây 25-30; lộ trình ≤ 2 câu, không đọc danh sách trong lộ trình.** | Câu nói về video ("Video này sẽ...", "cuối video là...") nằm trong cửa sổ rơi dốc nhất ở B3 (giây 12), F1 (18), F3 (20), B5 (32), F6 (35); ở F4 (giây 22) câu ấy cũng mất 6,5 điểm trong 7 giây. |
| 3 | **Không chương lý thuyết / định nghĩa trước lần trả đầu tiên.** Định nghĩa ≤ 2 câu, nhét vào trong câu trả lời. | F6 chương "Chìa khóa..." 3 phút mất 40% (13,4%/phút); F1 "Thái Tuế là gì?" 16,9%/phút so với 8-11 ở chương từng tuổi; F3 "Năm tuổi là gì?" 38%/phút so với 4,7 ở chương sau. |
| 4 | **Trả một phần thật trong 90 giây; chương nội dung đầu tiên bắt đầu ≤ 2:30.** Video gom nhiều nhóm khán giả (12 tuổi) phải cho mỗi người biết phần mình ở đâu. | F6: −52 điểm ở giây 21-42, phần tuổi Tý tới 4:17, còn 29% ở phút 1. F4 (trả ngay tuổi Tuất): còn 70% ở phút 1, tốt nhất kênh. |
| 5 | **Mỗi câu ≤ 35 tiếng ĐỌC** (chữ số đếm theo cách đọc: 1983 = 7 tiếng). **Không đọc quá 3 năm sinh / tên / mục trong một câu**; phần còn lại lên bảng màn hình. | F6: 5/8 lần rơi dốc nhất sau phút 1 đúng câu "...gồm những người sinh năm 1960, 1972, 1984, 1996 và 2008" (40-44 tiếng đọc; runner đếm 15 token nên không báo). |
| 6 | **Trả vòng nào, mở vòng mới ngay câu sau.** | F6 chương tuổi Mùi ("nhiều người chờ nhất"): mất 41% trong chương, rơi ngay sau câu trả "năm tuổi không có nghĩa là năm xấu". |
| 7 | **Không kết chương / video bằng "Tóm lại"; không đọc bảng tổng hợp từng dòng; lời gọi đăng ký ≤ 2 câu, sau lần trả cuối.** | F4 chương cuối (mở bằng "Tóm lại") mất 31% trong 50 giây; F1 chương cuối −29%; F6 bảng tổng hợp đọc to: −40% trong 1,1 phút. |
| 8 | **Câu ngắn ≤ 6 tiếng mỗi 4-6 câu, đặt sau khoảnh khắc; câu kinh / câu quen ở cao trào.** | Đoạn có câu ngắn rơi chậm hơn nền của chính video 4-8 điểm %/phút; B5 có người tua lại đúng "Và khi trời gần sáng, Ngài biết.", hồ sen, "Hãy tự mình làm ngọn đèn". |
| 9 | **Thẻ chương là mục lục để người xem nhảy tới**: tiêu đề = điều người xem tìm; mỗi chương tự đứng được (nhắc khái niệm 1 câu, móc riêng). | F6: đường giữ chân TĂNG +6/+7/+7 điểm đúng ở thẻ "Tuổi Mão", "Tuổi Tỵ", "Tuổi Ngọ" (người xem nhảy theo mốc chương). |
| 10 | **Tên Pali / Phạn, mã kinh, gạch nối giữa hai số phải viết theo cách đọc Việt.** | `phonemize_text` 14/10: "Jāṇussoṇi" ra âm Anh vỡ, "DN 16" -> "đi-en", "1-3 lần" -> "ngày một tháng ba lần". |

Luật cũ vẫn giữ (long-video §2): ≤ 3 tên chi một dòng (runner chặn), FS gọi tên chi, không câu vụn cụt, ≤ 90 giây
không ngắt nhịp, ≥ 3 vòng mở được đóng, motif ≥ 3 lần, kết video = callback + một câu hỏi thật.

## 1. Quy trình — làm theo thứ tự, mỗi bước có cổng
1. **Brief** (5 dòng, ghi vào docstring đầu `build_X.py`): format (a/b/c/d ở §2) + thời lượng + ngân sách tiếng;
   câu chiến lược **"Video này nói với [ai] rằng [thông điệp]"**; neo tìm kiếm (`hf_trends.py`, `briefs/<kênh>.md`,
   `hf_novelty.py check`); câu khán giả gõ tìm (dùng làm tiêu đề chương); motif. *Cổng*: nói được thông điệp trong 1 câu.
2. **Gói nghiên cứu** (phương pháp skill `research`: nguồn gốc, mỗi khẳng định một nguồn). Liệt kê sự kiện kèm nhãn
   `[kinh số…] [chú giải] [truyền thống] [truyền thuyết] [sử: sách] [dân gian] [code]`. BUD: mọi lời Phật đối chiếu
   `python hf_sutta.py <uid> "<cụm>"` (kệ Tiền Thân: `hf_sutta.py ja<N>`); FS: can chi / nạp âm / tuổi âm / sao hạn
   **sinh bằng code** (`canchi.py`, `amlich.py`, `batrach.py` trong `output/cl_staging/long/`), lời quẻ chỉ từ
   `hf_kinhdich.py`. *Cổng*: không câu nào trong kịch bản mang thông tin chưa có trong gói.
3. **Khung vĩ mô** theo bảng thời lượng (`references/formats.md` §1): cold open, lộ trình, chương 1 trả ngay,
   chương 4-8 phút, re-hook ở ~25/50/75% (trùng điểm nghỉ quảng cáo: đặt câu mở vòng ngay TRƯỚC chỗ nghỉ), vòng lớn trả ở cuối.
   Viết dòng nhịp: `cảnh-HỎI-trả-chương-chuyện-ĐỈNH-lặng-cầu nối…` (beat-direction: gọi tên nhịp trước khi viết).
4. **Beat sheet** (`references/formats.md` §6 mẫu): mỗi chương một dòng — phút, vai (móc / căng / bước ngoặt / trả /
   bài học / cầu nối), kỹ thuật có tên (ví dụ có số, trước-sau, so sánh, chuỗi nhân quả, gọi lại…), cảm xúc, vòng mở/trả,
   chi tiết giác quan, câu kết chương. *Cổng*: xoá hết dòng bằng chứng mà thông điệp vẫn đứng; xoá dòng thông điệp
   mà video vẫn "chạy" nghĩa là nó chỉ là bản liệt kê (story-spine §2).
5. **Viết từng dòng** theo `references/line-rules.md` (độ dài, số, nhịp, chữ khoá, thoại, giác quan, ngôi thứ hai,
   bẫy TTS). Truyện: `references/story.md` (mẫu kể trung thành nguồn, nhãn truyền thuyết).
6. **Tự soát bằng lint** — 0 LỖI, mỗi CẢNH BÁO sửa hoặc ghi lý do trong docstring:
   ```bash
   python long_script_lint.py nhap.txt                       # bản nháp: mỗi dòng một dòng say(), **tiêu đề chương**
   python long_script_lint.py output/cl_staging/long/plan_long_wNN.json --only <id> --strict
   python long_script_lint.py <plan> --only <id> --kind night   # Đêm nghe lời Phật dạy
   ```
   Lint gọi nguyên `hf_batch_render.retention_issues` (dòng "runner") và đo thêm: phân bố tiếng, câu > 35 tiếng đọc,
   liệt kê ≥ 4, câu mở lặp, từ lặp cục bộ, câu trừu tượng liền, vòng mở/trả, re-hook 25/50/75%, 90 giây đầu, độ dài chương,
   kết chương "tóm lại", lời gọi đăng ký, bẫy TTS. Có `out/<id>.json` thì dùng giây thật.
7. **Soát sự thật** (long-video §3, bắt buộc): đọc lại từng câu có "kinh", "Phật dạy", "Ngài nói", con số, năm sinh;
   câu nào không có trong gói nghiên cứu thì xoá hoặc gắn nhãn. FS: chạy lại code sinh số, so từng con số trong lời đọc.
8. **Bàn giao** `build_X.py` (mẫu `build_B20.py`, `build_F20.py`): `say(text, pause=, tempo=, media=, alt=)`, `chap(t)`
   (= dòng in đậm trọn, `pause=2.0`), `vis(n, spec)` / `quote(n, source)` (skill `motion-library`), `SILENCE`, `DROPS`.
   `python build_X.py --words` (đếm) -> `python build_X.py` (ghi plan) -> lint lại trên plan -> long-video §4 trở đi.
   Render ≈ 1,7× thời lượng (60 phút ≈ 1 giờ 40), TTS cache theo câu: sửa chữ sau render chỉ tốn câu đã sửa.

## 2. Bốn format (chi tiết, khung thời gian, beat sheet mẫu: `references/formats.md`)
| Format | Dài | Xương sống | Nguồn mẫu |
|--------|-----|-----------|-----------|
| (a) BUD Truyện Tiền Thân | 45-60' | 1 truyện sâu (như đối thủ, 45-57'/tập) **hoặc** 5-8 truyện quanh một chủ đề, mỗi truyện 6-9' theo 5 phần Tiền Thân (hiện tại -> quá khứ -> kệ -> nhận diện -> bài học) | Quang Vô Sắc TV tập 1 (45', 180 nghìn view/27 ngày) |
| (b) FS Tử vi trọn đời tuổi X + 2027 | 35-45' | bảng tính bằng code -> chương theo giai đoạn đời + 2027 (sao hạn nam/nữ, Thái Tuế, tháng cần để ý) | đối thủ "Quý Hợi 1983" 30-58' (chia theo tuổi 41-45, 44 về sau) |
| (c) FS Hỏi-đáp | 40-60' | mỗi câu hỏi tìm kiếm = một chương, **trả trong 2 câu đầu chương**, 10-14 câu | "Lọ hoa bàn thờ đặt bên trái hay phải" 36-47' (425 nghìn view) |
| (d) BUD Đêm nghe | 90' | êm, không móc gắt, vẫn 10-12 chương 7-9' để nhảy; mỗi chương 1 lời dạy có kinh + 1 hình ảnh + 1 nhịp thở | "Đêm nghe lời Phật dạy" 63-143' (5-7 triệu view) |

## 3. Tài liệu
- `references/evidence.md` — đường giữ chân B3, B5, F1, F3, F4, F6 khớp với câu đang đọc: chỗ rơi, chỗ giữ, số liệu, giới hạn mẫu.
- `references/line-rules.md` — luật từng dòng cho TTS VieNeu (bảng cách đọc đo bằng `phonemize_text`).
- `references/formats.md` — khung 30/45/60/90 phút, 4 format, beat sheet mẫu, cấu trúc đối thủ.
- `references/story.md` — mẫu kể chuyện trung thành nguồn (Tiền Thân, sử, truyện minh hoạ), nhãn truyền thuyết.
- `references/sources.md` — luật nào lấy từ đâu (hyperframes-creative, faceless-explainer, research, long-video, số liệu kênh).
- `long_script_lint.py` (gốc repo) + `tests/test_long_script_lint.py`.
