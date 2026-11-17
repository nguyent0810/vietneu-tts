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

## 0. Chuẩn lời đọc và hồ sơ

Đọc [lõi audio-script §1–10](../../../docs/script/audio-script.md); ngân sách theo [giọng đo](../../../docs/script/voice-rates.md). Chọn [Long chuẩn](../../../docs/script/profiles/long-standard.md) hoặc [nhân vật](../../../docs/script/profiles/long-nhan-vat.md)/[đêm nghe](../../../docs/script/profiles/night.md), cộng [BUD](../../../docs/script/profiles/bud.md)/[FS](../../../docs/script/profiles/fs.md); tra cứu/tuyển tập/Q&A có delta riêng trong mục hồ sơ. Các heuristic nghề kể là CB/gợi ý, không bắt đệm câu hay sửa chữ để chiều regex.

Mở bằng hình (PO15/11) giữ ở long-video §4: 10 giây đầu clip/pano/ảnh camera, không chữ khoá/thẻ chữ. Câu trọn đi theo ý; 120 giây đầu hình động ≤8s/tĩnh ≤4s (PO17/11), không ép thời lượng câu. Cổng hình không đổi.

## 1. Quy trình — làm theo thứ tự, mỗi bước có cổng
1. **Brief** (5 dòng, ghi vào docstring đầu `build_X.py`): format (a/b/c/d/e ở §2) + thời lượng + ngân sách tiếng;
   câu chiến lược **"Video này nói với [ai] rằng [thông điệp]"**; neo tìm kiếm (`hf_trends.py`, `briefs/<kênh>.md`,
   `hf_novelty.py check`); câu khán giả gõ tìm (dùng làm tiêu đề chương); motif. Đóng gói tiêu đề & kiểm lời hứa: xem skill `long-packaging`. *Cổng*: nói được thông điệp trong 1 câu.
2. **Gói nghiên cứu** (phương pháp skill `research`: nguồn gốc, mỗi khẳng định một nguồn). Liệt kê sự kiện kèm nhãn
   `[kinh số…] [chú giải] [truyền thống] [truyền thuyết] [sử: sách] [dân gian] [code]`. BUD: mọi lời Phật đối chiếu
   `.venv/bin/python hf_sutta.py <uid> "<cụm>"` (kệ Tiền Thân: `hf_sutta.py ja<N>`); FS: can chi / nạp âm / tuổi âm / sao hạn
   **sinh bằng code** (`canchi.py`, `amlich.py`, `batrach.py` trong `output/cl_staging/long/`), lời quẻ chỉ từ
   `hf_kinhdich.py`. *Cổng*: sự thật cứng/lời trích có trong gói; phỏng dựng/giọng kể theo hồ sơ BUD, không bắt nguồn cho mọi câu không khí.
3. **plan.md cho người dùng duyệt, trước khi viết một dòng lời.** Khuôn `references/formats.md` §1 (vì sao chọn đề,
   đóng gói, cung A→B, cold open, bảng vòng, mô-típ, 12–14 chương, hình thức lộ trình, mốc 50% và 75%).
   Khuôn nhân vật dùng §7 (12–16 chương, ≥ 30 phút), không dùng dàn 12–14 của §1.
   Chép bảng vòng vào plan JSON: `"vong": [{"mo": "câu hỏi mở", "dong": "cụm chữ nằm ở chương đóng"}]`.
   *Cổng*: người dùng đã duyệt plan. Chưa duyệt thì dừng, không viết `say()`.
4. **Beat sheet** (`references/formats.md` §6 mẫu), bám plan đã duyệt: mỗi chương một dòng — phút, vai (móc / căng /
   bước ngoặt / trả / bài học / cầu nối), kỹ thuật có tên, cảm xúc, vòng mở/trả, chi tiết giác quan, câu kết là câu móc.
   Dòng nhịp: `cảnh-HỎI-trả-chương-chuyện-ĐỈNH-lặng-cầu nối…`. *Cổng*: xoá hết dòng bằng chứng mà thông điệp vẫn đứng;
   xoá dòng thông điệp mà video vẫn "chạy" nghĩa là nó chỉ là bản liệt kê (story-spine §2).
5. **Viết văn xuôi tự do, đọc thử rồi mới viết tiếp.** Giao người viết (Sonnet hoặc thợ) thì dán `references/writer-brief.md` đã điền: cách kể, ba lớp nguồn / diễn giải / hư cấu, bàn giao `source_notes_<id>.md`, phiếu tám mục của lõi §7. Luật dòng theo `references/line-rules.md` (độ dài, số, nhịp, chữ khoá, thoại, giác quan, ngôi thứ hai,
   bẫy TTS). Viết trước CH00–01 trong `prose.md`, tiêu đề `## …`; chạy `.venv/bin/python tools/prose_to_script.py prose.md script.txt` → dựng plan qua `tools/long_plan_build.py --script` → Lead đọc thử `.venv/bin/python tools/tts_sample.py <plan.json> --only <id> --chapters 0 1` → viết tiếp. TTS nguyên câu, không tách vế; Long BUD/FS/VSD 46–70 tiếng đọc cảnh báo, >70 lỗi (số đọc ra chữ). Bỏ quota câu ngắn khỏi lint/retention, chỉ còn gợi ý nhịp. Cổng hình giữ nguyên; bridge chưa có đổi ảnh ở mốc từ giữa dòng (xem lõi §5).
   Truyện: `references/story.md` (mẫu kể trung thành nguồn, nhãn truyền thuyết).
6. **Tự soát bằng lint** — 0 LỖI, mỗi CẢNH BÁO sửa hoặc ghi lý do trong docstring:
   ```bash
   .venv/bin/python long_script_lint.py nhap.txt                       # bản nháp: mỗi dòng một dòng say(), **tiêu đề chương**
   .venv/bin/python long_script_lint.py output/cl_staging/long/plan_long_wNN.json --only <id> --strict
   .venv/bin/python long_script_lint.py <plan> --only <id> --kind night   # Đêm nghe lời Phật dạy
   ```
   Danh mục mức kiểm ở [lõi §9](../../../docs/script/audio-script.md#9-adapter-và-mức-kiểm); runner retention vẫn CB. Clock thật chỉ khi kiểm manifest khớp bản lời/giọng; cùng số dòng chưa đủ.
7. **Soát sự thật** (long-video §3, bắt buộc): đọc lại từng câu có "kinh", "Phật dạy", "Ngài nói", con số, năm sinh;
   sự thật/lời trích thiếu căn cứ thì sửa; diễn giải/phỏng dựng theo hồ sơ, không đồng nhất với claim thật. FS: chạy lại code sinh số, so từng con số trong lời đọc.
8. **Bàn giao** `build_X.py` (mẫu `build_B20.py`, `build_F20.py`): `say(text, pause=, tempo=, media=, alt=)`, `chap(t)`
   (= dòng in đậm trọn, `pause=2.0`), `vis(n, spec)` / `quote(n, source)` (skill `motion-library`), `SILENCE`, `DROPS`.
   Plan Long mới đi qua `save_plan_rows` nhận thêm 1–3 cảnh style #258 trong `visuals` (skill `long-video` §4): sau giây 40, tối đa 3, không liền nhau, đúng bảng kênh. Viết tay thì cùng dạng, hoặc `"style_suggest": false`. Ví dụ FS: `"41": {"type": "woodcut", "text": "Cổng thành · còn đứng", "motif": "gate", "tone": "dark", "steps": [{"at": 41, "word": "cổng"}]}`. Field từng style: skill `motion-library` mục #258.
   `.venv/bin/python build_X.py --words` (đếm) -> `.venv/bin/python build_X.py` (ghi plan) -> lint lại trên plan -> long-video §4 trở đi.
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
- `references/writer-brief.md` — mẫu brief giao người viết lời (#266): cách kể, ba lớp nội dung, bàn giao, tự kiểm.
- `references/line-rules.md` — luật từng dòng cho TTS VieNeu (bảng cách đọc đo bằng `phonemize_text`).
- `references/formats.md` — khuôn plan.md, khung 30 phút (Đêm nghe 90 phút), 4 format, khuôn nhân vật §7, beat sheet mẫu.
- `references/story.md` — mẫu kể chuyện trung thành nguồn (Tiền Thân, sử, truyện minh hoạ), nhãn truyền thuyết.
- `references/sources.md` — luật nào lấy từ đâu (hyperframes-creative, faceless-explainer, research, long-video, số liệu kênh).
- `long_script_lint.py` (gốc repo) + `tests/test_long_script_lint.py`.

## Thumbnail Long V2 (quyết định 21/10; ticket 54b)
> Chi tiết luật đóng gói tiêu đề + thumbnail theo số liệu thực nghiệm kênh: xem skill `long-packaging` (`.claude/skills/long-packaging/SKILL.md`). Kiểm tra lời hứa bằng `.venv/bin/python tools/long_packaging/promise_check.py <plan>`.
- Mỗi Long chuẩn bị ba bản A/B/C để Lead chọn; thumbnail ưu tiên 2–5 từ, tối đa 8 từ khi cần để nói rõ nghịch lý (PO 03/11: không xét bằng số từ đơn thuần) — đọc hiểu trong 1–2 giây trên điện thoại, dễ đọc, bổ sung cho hình và title, không lặp nguyên title, mọi tuyên bố đúng nguồn; từ khóa viết HOA, bám chi tiết trong cold open.
- Mỗi bản có một chủ thể lớn, rõ: BUD dùng ảnh chụp tượng/phù điêu/tranh cổ có nguồn công cộng hoặc giấy phép tự do; FS dùng bảng, la bàn hoặc bát quái. BUD cũng được dùng nền AI không chữ rồi đặt chữ tự dựng (docs/adr/0005). Không vẽ mặt Đức Phật bằng code, hoạt hình, biếm hoạ.
- Không thêm nhãn series, dòng hứa hẹn hay chữ phụ. Bản xuất 1280×720 và bản xem 168×94; ghép tờ so sánh cả ba bản ở hai cỡ để Lead duyệt.
- Kiểm tra thủ công ở 168 px: chữ đọc rõ, chủ thể nhận diện được, với ảnh tượng thì không cắt đầu hay đặt chữ lên mặt. Lead chọn và tự cập nhật ảnh đã đăng.
- Công cụ: `hf_long_thumbnail.make_v2(...)`; ví dụ gọi A/B/C riêng bằng `variant="A"`, `"B"`, `"C"`.
