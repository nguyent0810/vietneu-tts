---
name: long-video
description: "Sản xuất video dài (16:9; bản chuẩn 8–10 phút, bản trụ 30+ phút render theo chương) cho kênh Phật giáo (BUD) và Phong Thuỷ (FS) bằng HyperFrames: nghiên cứu → kịch bản có hook/reward → soát sự thật → plan cảnh (sơ đồ, bản đồ, ảnh 2.5D, chữ theo nghĩa) → xem trước ảnh → render → soát khung hình → đăng hẹn giờ + playlist → dọn file. Dùng khi người dùng muốn làm/đăng một long mới cho BUD hoặc FS. Không dùng cho Short (output/cl_staging/bud|fs) hay kênh CL."
---

# Video dài BUD / FS

Mọi thứ nằm ở `output/cl_staging/long/` (gitignored): `plan_long_w40.json`, `out/`,
`thumbs/`, `upload_long.py`, `uploaded.json`. Kho hiệu ứng: skill `motion-library`.

## 0. Bản trụ 30+ phút (từ 01/10/2026) — đọc trước
- Mẫu: `output/cl_staging/long/build_B1.py` (Phật giáo) và `build_F1.py` + `canchi.py` (Phong Thuỷ):
  kịch bản viết bằng Python (`say()/vis()/head()`), số liệu can chi / nạp âm / tuổi âm SINH bằng code.
- Kiến trúc giữ chân (rút từ V2 `motion/long/RETENTION.md`): cold open dừng ở đỉnh → thẻ chương →
  lộ trình 3 câu hỏi → chương 3–6 phút (móc → bối cảnh → leo thang → đỉnh + lặng → bài học → câu nối)
  → giữa video quay lại cảnh mở → cảnh mạnh ở 3/4 → kết đóng 3 câu hỏi + motif. ≤3 mục mỗi danh sách
  trong lời đọc (bảng dài để trên màn hình: `ledger`). Câu ≤ 34 âm tiết.
- Plan: `"chapters": true` → `hf_batch_render` render từng chương (chạy lại được), nối hình, trộn tiếng
  một lần. `"tts"` (hf_voice, TTS từng câu) + `"sound"` (hf_foley, 4 lớp). **Preset C** (người dùng duyệt):
  BUD giọng `Binh` standard tempo 0.91, câu đỉnh 0.85–0.88 (`tempos`), câu kinh `Quang Sơn` v3 (`alt`),
  vang 0.045 / 0.16 s, `voice_eq`, `music_gap` 18, `sfx_peak` .32, amb/drone gap 27. FS giọng `Thái Sơn`
  v3 doc_truyen tempo .96, không vang. Không tăng vang/nhạc/tiếng động nếu chưa hỏi.
- Cảnh vẽ thay tư liệu: `shadow` (bodhi, departure, forest, lamp, turtle — luôn nhãn MINH HOẠ, không vẽ
  mặt Đức Phật), `hexagram`, `luoshu`, `ledger`, `breath`, `map` + `footsteps`.
- Tư liệu: Commons PD/CC0 (`hf_commons.search` rồi **lấy tên file đầy đủ từ kết quả, không tự điền
  phần đuôi bị cắt**; kiểm bằng `hf_commons.fetch` trước render), soát bằng tờ ảnh xem trước. Ảnh stock:
  loại tôn giáo khác, rượu, người phương Tây trong cảnh gia đình Việt, vật sai (táo ≠ mận hồng).
- 36 phút render ~60 phút (1,7× thời lượng); đừng chạy TTS song song với render nếu cần nhanh.

## 1. Chủ đề + nghiên cứu
- BUD: chuỗi "Lời Phật dạy" (chữa lành) kéo sub; hành hương/giáo lý vào playlist
  "Hành Trình Tâm Linh…". FS: chuỗi "12 Con Giáp Năm 2027" (con giáp + lịch kéo view).
- Retention thật của kênh: ~50% rời trong 30–60s đầu, đường cong phẳng sau phút 2–3
  → dài 5–7 phút, dồn sức vào 30 giây đầu. Muốn mid-roll cần ≥8 phút (~1.800 từ).

## 2. Kịch bản (skill faceless-explainer `references/story-design.md`)
- Một dòng = một câu. Câu in đậm TRỌN câu (`**...**`) = tiêu đề chương → thẻ chương
  + mốc trong mô tả. Cụm `**đánh dấu**` giữa câu = chữ khoá (dạ quang, callout, chữ động).
- Hook có tên chiến lược (counterintuitive, stakes…) trong 3–5 câu đầu; thesis ở beat 2;
  hứa reward ở đầu, TRẢ ở cuối; mỗi chương kết bằng một câu mở sang chương sau.
- TTS đọc lồng khi liệt kê ≥4 tên liền nhau → tách câu, tối đa 3 tên.
- Câu vụn nhiều mảnh cụt ("Hỏa là đỏ, cam. Thổ là vàng đất, nâu.") có lần làm TTS hỏng
  liên tục (short f31_f) → viết thành câu liền ("Hỏa ứng với đỏ và cam, ...").
- **FS: gọi con giáp bằng tên chi** (Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu,
  Tuất, Hợi), không "tuổi Lợn/Dê". Runner chặn (`zodiac_naming_errors`).
- Framing: FS "được xem là / theo truyền thống", có lời "kiến thức truyền thống để tham khảo".
  BUD: lời Phật chỉ gán khi có kinh (vd DN 16, Pháp Cú câu n); hình ảnh không từ kinh
  thì nói "một hình ảnh quen thuộc trong truyền thống Phật giáo".

### Checklist giữ chân (mượn RETENTION.md của Youtube_Creator_V2, 04/10/2026)
Runner in `!! giữ chân:` (retention_issues, chỉ cảnh báo) — đo trên CÂU NÓI, không phải dòng:
- Câu nói 12–18 tiếng, **không câu nào > 35 tiếng** (TTS hụt hơi). Tách ở dấu hai chấm / "mà là".
  Lời kinh giữ nguyên nhịp tụng được, nhưng đừng để dài quá 2 câu.
- **Câu ngắn ≤ 6 tiếng ~1 câu mỗi 4–6 câu**: câu đỉnh sau phán định ĐÚNG/SAI, sau khoảnh khắc cảm xúc
  ("Bà khóc.", "Tầng ấy vẫn ở đó."). Đo 04/10: F10–B14 chỉ 1/10–1/48 → điểm yếu chính.
- Không quá 90 giây liền không ngắt nhịp (câu hỏi, con số, câu ngắn, trích kinh, thẻ chương).
- Liệt kê trong lời đọc tối đa 3 mục, mục thứ ba bất ngờ nhất; phần còn lại lên màn hình.
- Cold open bằng cảnh cụ thể, câu hỏi chưa trả lời; lộ trình 3 điều trong 1 phút đầu.
- ~50%: re-hook (quay lại cảnh mở, đóng một vòng, mở vòng lớn hơn); ~75%: cảnh mạnh thứ hai.
- ≥ 3 vòng mở được đóng ở chương sau; motif xuất hiện ≥ 3 lần (đầu, giữa, kết).
- Kết chương bằng câu cầu nối, KHÔNG bằng câu tóm tắt. Kết video: callback + một câu hỏi thật.

## 3. Soát sự thật (bắt buộc, trước khi plan)
- Can chi, nạp âm, quan hệ (xung/hình/hại/phá/tam hợp/lục hợp) tra tay theo bảng chuẩn,
  **không dùng vnlunar** cho thần/trực/nạp âm (sai). Tuổi âm = năm xem − năm sinh + 1.
- Tự đọc lại từng câu tìm khẳng định kinh không nói ("ít nhất một lần", "Phật chưa từng…").
- **BUD: đối chiếu mọi câu dẫn kinh với nguyên văn** — `python hf_sutta.py <uid> "<cụm từ>"` (SuttaCentral,
  bản Sujato CC0 + Pali; `hf_sutta.py cite "Tăng Chi Bộ 11.15"` -> an11.15; Pháp Cú tự đổi khoảng kệ). Soát 04/10
  bắt được b45_b viết "tự bắn mũi tên thứ hai" trong khi SN 36.6 là "bị trúng mũi tên thứ hai".
- **FS mảng Kinh Dịch: lời quẻ/hào/Tượng chỉ trích từ** `python hf_kinhdich.py <tên quẻ>` (Ngô Tất Tố, phạm vi
  công cộng, Wikisource — mới 9/64 quẻ: Kiền, Khôn, Truân, Mông, Nhu, Tụng, Sư, Hàm, Hằng; chạy `hf_kinhdich.py`
  định kỳ để lấy quẻ mới). Quẻ chưa có: dùng nguyên văn chữ Hán có nguồn, nói rõ là diễn ý.

## 4. Plan (một phần tử trong `plan_long_w40.json`)
`id, day, slot (UTC, "13:00" = 20:00 VN), style (laban_long | inkwash_long), series (bud|fs),
lane: "long", title, tags, script[], media{}, visuals{}, figures{} (mọi câu type none),
thumbnail, playlists[{title, description?}], hold?` — cú pháp `visuals`/`media`: skill
`motion-library`. Ảnh không ghi `layout` → bridge tự luân phiên bố cục.

## 5. Xem trước ảnh TRƯỚC khi render
- Tìm ứng viên đúng chủ đề: `python hf_media_sheet.py find "wiki:vi:Chùa Bút Tháp" --by` lấy ảnh nằm trong một bài
  Wikipedia (vi/en, chỉ file Commons giấy phép tự do) — chùa, di tích, phong tục Việt ra sát hơn tìm từ khoá.
- Nhạc nền: **sổ nhạc `hf_music.py`** (04/10/2026, ý từ V2 `motion/variety.py`) — chính sách Spam của YouTube nêu đích
  danh "cùng nhạc nền trên nhiều video". Mỗi video được 4 bài chọn một lần (ít dùng nhất trong 3 video cùng kênh gần
  ngày đăng nhất; bộ Meditation/Deliberate/Thinking/Mystery cũ xếp sau), ghi `output/cl_staging/long/bgm_ledger.json`;
  `music_bed` phát lần lượt, chỉ đổi bài ở thẻ chương, chồng mờ 3 giây, san đều độ to (dynaudnorm). Bài thực sự phát vào
  `render.json` `bgm_used` → upload_long ghi nguồn đủ mọi bài. Runner in `!! nhạc nền:` khi trùng > 35% với video gần đó.
  `python hf_music.py library` xem kho; bài mới: tải từ incompetech (CC BY), đo RMS 5 giây dao động ≤ ~14 dB, thêm vào
  `CATALOG` + `bgm/LICENSE.txt`. `"bgm"` trong plan ghim một bài; `"bgm_rotate": false` tắt đổi bài.
  Đổi âm thanh video đã render: `hf_batch_render.py ... --only <id> --remix-audio` (video dài trộn lại 4 lớp, ~2 phút).

Tải ảnh ngang (`stock_image.get_or_fetch_stock_image(sanitize_query(q, "BUD"|"FS"), "landscape")`)
và dựng contact sheet. Loại: tôn giáo khác (Hindu, Hồi giáo…) trên kênh Phật giáo, người
nước ngoài khi câu nói về người Việt, chữ/logo/năm sai ("2024", "SALE"), trâu bò Ấn/Phi
cho tuổi Sửu (dùng trâu nước), cây "sala" là cây đầu lân (không phải Shorea). Hai query có
thể về cùng một ảnh → bridge chặn trùng.

## 6. Render + soát
```
.venv/bin/python hf_batch_render.py output/cl_staging/long --only <id> --quality looks
```
- Mặc định KHÔNG chạy QA tự động (người dùng tự review video, ưu tiên render nhanh).
  Chỉ thêm `HF_QA=1` khi viết cảnh/style mới hoặc người dùng yêu cầu.
- Nhạc nền tự đặt dưới giọng 21 dB, xoay pool track; video dài tự render luồng
  (`HF_CAPTURE_PARALLEL_STREAM`) — không tốn đĩa, ~4–5 phút.
- `HF_QA=1` chạy `hyperframes check` trước render (WCAG, bố cục) → `<id>.qa.json`; tốn thêm
  ~2 phút. Sửa nhỏ thì chạy lại riêng mốc lỗi: sửa `chunks_cache/qa/<id>/index.html`, rồi
  `npx hyperframes@0.8.75 check . --json --at <t1>,<t2>` trong thư mục đó (Node 22).
- Rút khung giữa từng cảnh (ffmpeg -ss), dựng lưới, NHÌN: chữ đọc được trên ảnh, ảnh đúng
  nghĩa, sơ đồ đúng dữ liệu, không khung trống. Sửa → render lại (TTS được cache).
- Gửi người dùng bản nén 720p + thumbnail khi là thiết kế mới; chờ duyệt (`hold`).

## 7. Thumbnail
`hf_long_thumbnail.make(hero, out, domain="BUD"|"FS", big1, big2, promise, tag)` — một chủ thể,
2 chữ rất lớn, 1 câu hứa, nhãn series; soát bản 168px. Không trùng ảnh hero trong cùng series.

## 8. Đăng
`upload_long.py --only <id> --confirm`: riêng tư + hẹn giờ, dò sâu khung giờ (search.list
cộng dồn), mục lục chương có mốc, ghi nguồn ảnh + nhạc đúng track đã trộn, gắn thumbnail,
thêm playlist (công khai, idempotent). Mỗi kênh một API project, quota riêng; hết quota
search thì chờ reset 14:00 VN, không đăng mù. Kiểm lại bằng video ID (privacy, publishAt).

## 9. Dọn
Sau khi đăng: chuyển mp4/wav của video đã đăng, bản render cũ, bản xem thử vào một thư mục
trong Thùng rác, đưa người dùng lệnh `rm -rf ~/.Trash/"<thư mục>"` — không tự xoá vĩnh viễn.
