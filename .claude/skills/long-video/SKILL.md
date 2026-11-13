---
name: long-video
description: "Sản xuất video dài (16:9; bản chuẩn 8–10 phút, bản trụ 30+ phút render theo chương) cho kênh Phật giáo (BUD) và Phong Thuỷ (FS) bằng HyperFrames: nghiên cứu → kịch bản có hook/reward → soát sự thật → plan cảnh (sơ đồ, bản đồ, ảnh 2.5D, chữ theo nghĩa) → xem trước ảnh → render → soát khung hình → đăng hẹn giờ + playlist → dọn file. Dùng khi người dùng muốn làm/đăng một long mới cho BUD hoặc FS. Không dùng cho Short (output/cl_staging/bud|fs) hay kênh CL."
---

# Video dài BUD / FS

Mọi thứ nằm ở `output/cl_staging/long/` (gitignored): `plan_long_w40.json`, `out/`,
`thumbs/`, `upload_long.py`, `uploaded.json`. Kho hiệu ứng: skill `motion-library`.

## 0. Bản trụ 30+ phút (từ 01/10/2026) — đọc trước
> Mới hơn mục này (thắng khi lệch): Long ≥ 30 phút theo **khuôn nhân vật** "X Ngoài Đời Thật", 12–16 chương ~2 phút,
> 2–3 câu hỏi hẹn chương (docs/adr/0001, skill long-script §0 và formats.md §7); luật giữ chân 21/10 (docs/adr/0002).
- Mẫu: `output/cl_staging/long/build_B1.py` (Phật giáo) và `build_F1.py` + `canchi.py` (Phong Thuỷ):
  kịch bản viết bằng Python (`say()/vis()/head()`), số liệu can chi / nạp âm / tuổi âm SINH bằng code.
- Kiến trúc giữ chân (rút từ V2 `motion/long/RETENTION.md`): cold open dừng ở đỉnh → thẻ chương →
  lộ trình 3 câu hỏi → chương 3–6 phút (móc → bối cảnh → leo thang → đỉnh + lặng → bài học → câu nối)
  → giữa video quay lại cảnh mở → cảnh mạnh ở 3/4 → kết đóng 3 câu hỏi + motif. ≤3 mục mỗi danh sách
  trong lời đọc (bảng dài để trên màn hình: `ledger`). `ledger` chỉ cho bảng ≥ 4 dòng nhiều cột: bảng 2-3 dòng hiện chữ rất nhỏ ở góc (QA F18 06/10) → dùng `list`/`compare`. Câu ≤ 34 âm tiết.
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

## 0b. Skin studio_long (15/10/2026)
`"style": "studio_long", "theme": "saffron"|"tet-poster"|"son-mai"|"archive"|"blueprint"` -> màu/chữ/nhịp từ theme Shorts Studio,
thêm visual `{"type": "studio", "device": ...}` (18 thiết bị khổ ngang). Xem skill `shorts-studio` -> `references/long.md`.

## 1. Chủ đề + nghiên cứu
- **Chủ đề "neo" (06/10/2026)**: `python hf_trends.py bud fs` -> `briefs/<kênh>_trends.md` (Long đối thủ xếp theo view/ngày +
  gợi ý tìm kiếm cho nhân vật, địa danh, phim khán giả đã biết). Bài học CL: "Bến Thượng Hải ngoài đời thật" gấp 5 lần Long thường.
  Tránh mảng drama tin tức, tiên tri, hứa tiền bạc dù view cao: không hợp hồn kênh.
- **Đọc bản tóm tắt tuần trước khi chọn chủ đề**: `output/cl_staging/briefs/<bud|fs>.md` (`python hf_brief.py`, tự chạy
  thứ Hai trong daily batch). Gồm: Long so trung vị 8 tập trước + giữ chân 2% đầu; short xếp hạng engagedViews trong
  tuần (cửa sổ 7 ngày PT, tuần sạch từ 05/10/2026); gợi ý tìm kiếm YouTube + video nhiều view/ngày trong ngách 30 ngày
  (đánh dấu "kênh đã có"). Chọn chủ đề có cầu ngoài + chưa trùng (`hf_novelty.py check`), ghi lý do chọn vào build.
- BUD: chuỗi "Lời Phật dạy" (chữa lành) kéo sub; hành hương/giáo lý vào playlist
  "Hành Trình Tâm Linh…". FS: chuỗi "12 Con Giáp Năm 2027" (con giáp + lịch kéo view).
- Retention thật của kênh: ~50% rời trong 30–60s đầu, đường cong phẳng sau phút 2–3
  → (đo 01/10, đã thay) dồn sức vào 30–90 giây đầu; độ dài giữ ≥ 30 phút theo quyết định 22/10 (docs/adr/0001).

## 2. Kịch bản (skill faceless-explainer `references/story-design.md`)
- **Viết kịch bản 30-90 phút: skill `long-script`** (quy trình brief -> nghiên cứu -> khung -> beat sheet -> dòng,
  4 format, 10 luật rút từ đường giữ chân B3/B5/F1/F3/F4/F6). Soát trước TTS:
  `python long_script_lint.py output/cl_staging/long/plan_long_wNN.json --only <id>` (gọi lại `retention_issues`).
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
- Dựng plan Long mới từ script/base: `python tools/long_plan_build.py --script <txt> --id <id> --series bud|fs --base <plan.json> --out <plan.json>`.
`id, day, slot (UTC, "13:00" = 20:00 VN), style (laban_long | inkwash_long), series (bud|fs),
lane: "long", title, tags, script[], media{}, visuals{}, figures{} (mọi câu type none),
thumbnail, playlists[{title, description?}], hold?, layout_policy?` — cú pháp `visuals`/`media`: skill
`motion-library`. Plan Long mới ghi `"layout_policy": "v2"` (`hf_batch_render.save_plan_rows` gọi `wire_plan_row` và ghi sẵn lúc tạo plan mới). Ảnh/clip không ghi `layout` hay `cine` thì `hyperframes_bridge.assign_layouts_v2` gán: full kèm cine khoảng 55–65%, depth khoảng 10%, nhóm có khung (frame, card3d, polaroid, pinned, split, split_r) khoảng 25–35%; 120 giây đầu chỉ full+cine hoặc depth. Plan thiếu khoá này giữ `auto_layouts` (chia đều 8 kiểu). Ghi tay `layout` hoặc `cine` thì giữ đúng giá trị đó.
- Bộ style bổ sung (#258): `save_plan_rows` ghi 1–3 cảnh vào `visuals` của id Long mới (`lane: "long"` hoặc `style` kết thúc `_long`), kênh đã biết. Id đã có trên đĩa giữ nguyên `visuals`. Người viết xoá hoặc viết lại được. `"style_suggest": false` thì không đề xuất.
  Kênh được dùng: BUD `papercut` / `oneline` / `woodcut` (`tone: "paper"`); FS `woodcut` (`tone: "dark"`) / `blueprint` / `papercut`; Văn Sử Địa `film16` / `blueprint` / `papercut` / `pencil`; CL `film16` / `pencil` / `woodcut`. Field từng type nằm ở skill `motion-library`, mục #258.
  Chỗ đặt, sau giây 40 (chưa có TTS thì 185 tiếng/phút): thẻ chương (câu `**...**` trọn), mặt bằng hoặc bản đồ, năm 3–4 chữ số, dòng tư liệu. Tối đa 3 cảnh, giữa hai cảnh style có ít nhất một câu thường. Máy đánh dấu `"suggested": true` và `"role"`. Chữ trên thẻ là cụt của câu — viết lại thành tiêu đề.
  Ví dụ FS, người viết giữ hoặc sửa:
  ```json
  "41": {"type": "woodcut", "text": "Cổng thành · còn đứng", "motif": "gate", "tone": "dark", "steps": [{"at": 41, "word": "cổng"}], "suggested": true, "role": "thẻ chương"}
  ```
  Long mới còn 0 cảnh style: lúc render in `CẢNH BÁO style` kèm câu nên đặt, rồi vẫn render. Xem gợi ý, không ghi đĩa: `.venv/bin/python hf_style_suggest.py <plan.json> --dry-run`.
  CL/MIM/CK dựng bằng casewide: cùng sáu `type`, script chỉ được nhét vào HTML chương nào có cảnh ấy. `steps[].at` là số câu 1-based trong `lines` của chương. Một cảnh casewide vẫn 2,5–9 giây.
- Cảnh giữ hình > 25 giây bị runner chặn (pacing) trừ khi plan ghi lý do: `"slow_hold": {"<câu đầu cảnh>": "đọc nguyên văn bia"}`
  (ticket 65, 24/10/2026). Runner in thêm p50/p90 giây/cảnh và nhịp phút đầu/phút cuối (mục tiêu 2–4 giây, cảnh báo).
- Ảnh local chỉ được nằm trong `output/cl_staging/long/research/ai_media/` hoặc `output/cl_staging/grokbot/`. Ảnh ở chỗ khác, ví dụ `plans_*/<id>/assets/img/`, thì bước dựng chương báo lỗi "media local phải là file trong…". Vì vậy ticket ảnh Long phải ghi thẳng ảnh vào `output/cl_staging/long/research/ai_media/<id>/` (Lead 12/11).
- 120 giây đầu: mọi cảnh ≤ 4 giây (`pace_gate_issues`). Viết sẵn câu ngắn theo `long-script/references/writer-brief.md` §120 GIÂY ĐẦU, không tách câu máy móc.
- Ảnh/clip AI đã tải về: `{"kind": "local", "path": "output/cl_staging/long/research/ai_media/..."}`. Ảnh
  dọc (chân dung) bridge tự đặt vào khung 16:9 (chân dung giữa, nền mờ hai bên). Một ảnh không dùng hai lần trong
  cùng chương (bridge chặn trùng byte): lần hai thêm `"crop": [fx, fy]` (khung cắt cận 72%, chân dung để fy = 0).
  Thay nội dung ảnh local mà giữ tên thì chương có ảnh ấy tự render lại (khoá chương băm nội dung file).

### 4c. Làm giàu cảnh cho plan mới (038)
Builder gọi `library.tools.plan_enrich.enrich_long_plan(plan, "bud"|"fs")`, sau đó `hf_batch_render.save_plan_rows(out, [plan], channel=..., legacy=False)` để wire giọng/âm, đóng dấu layout v2 và áp gợi ý style. Builder tập cũ (`build_B*`, `build_F*`, `build_p2/p3/p4`) không chạy lại.

- Trần `ask`: 1 thẻ / 2 phút (`giây // 120`) và ≤ 25% số visual. Thẻ bộ chọn dư đổi sang loại kho đã có (`stat`, `quote`, `list`, `timeline`, `map`, `compare`, `illus`, `word`) khi câu đủ dữ liệu. Thẻ ghi tay vượt trần chỉ in `!! ask trần`.
- `kinetic_suggest`: 3–6 gợi ý opt-in, seed theo `id`. Không liền nhau, không đè dòng đã có visual ghi tay, không vào 40 giây đầu của cold open. Cold open là các dòng trước thẻ chương nội dung (thẻ ở dòng 1 là tiêu đề mở, mốc chặn là thẻ kế; không có thẻ kế thì tới hết kịch bản). Không có thẻ thì từ dòng 1 tới clip kế; một clip trơ thì cả kịch bản. Trần 40 giây cắt lúc gợi ý. Renderer không đọc khoá này. Bật bằng cách chép `"preset"` vào visual đúng `host`, rồi xoá mục. Tên preset vẫn khóa QA — không ghi vào `type`.
- Build in một dòng `visuals <id>: ...`. Bảng preset: skill `motion-library`, mục chữ theo nhịp.

## 4b. Tra kho trước khi tạo ảnh
Ảnh AI thiếu ảnh thật phải lưu vào kho và lần sau tra trước khi tạo mới (`library/tools/assets.py`):
1. `.venv/bin/python library/tools/assets.py find --pham-vi <bud|fs|chung> --tag "<chủ thể>" --kind img` — ảnh kênh trước, `chung` fallback.
2. Không có mới tạo GrokBot (ChatGPT / Flow, luật 17 cho hình Đức Phật).
3. Ảnh đã soát (`LEAD_DA_XEM`) → `.venv/bin/python library/tools/assets.py add <file> --pham-vi <kênh|chung> --prompt "..." --tags ...`
4. Dùng xong → `mark-used <asset_id> <video_id> <kênh> <YYYY-MM-DD>`; `find --exclude-used-days 7 --channel <kênh>` loại ảnh đã dùng 7 ngày trên kênh đó.

## 5. Xem trước ảnh TRƯỚC khi render

> **Không in credit lên hình (PO 04/11/2026):** không ghi "ảnh minh hoạ AI", tên công cụ/bot, tên tác giả ảnh, giấy phép lên video. Credit chỉ ở mô tả. Dòng nguồn kinh/sử ngắn là nội dung thì được giữ.
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
- Độ to đầu ra (ticket 68, 24/10/2026): trộn → đo → tăng tới đích → limiter đỉnh thật −1 dBTP → đo lại.
  Long −16 LUFS, Short −14 LUFS (`hyperframes_bridge.LOUD_TARGET`). Nhạc nén theo giọng `"duck_db"` (mặc định 6),
  đỉnh tiếng động `"sfx_peak"` mặc định .25 (−12 dB so giọng). Bài dễ lấn giọng (`hf_music.MASKS_VOICE`) không vào Long.
- Nhạc nền tự đặt dưới giọng 21 dB, xoay pool track; video dài tự render luồng
  (`HF_CAPTURE_PARALLEL_STREAM`) — không tốn đĩa, ~4–5 phút.
- `HF_QA=1` chạy `hyperframes check` trước render (WCAG, bố cục) → `<id>.qa.json`; tốn thêm
  ~2 phút. Sửa nhỏ thì chạy lại riêng mốc lỗi: sửa `chunks_cache/qa/<id>/index.html`, rồi
  `npx hyperframes@0.8.75 check . --json --at <t1>,<t2>` trong thư mục đó (Node 22).
- Rút khung giữa từng cảnh (ffmpeg -ss), dựng lưới, NHÌN: chữ đọc được trên ảnh, ảnh đúng
  nghĩa, sơ đồ đúng dữ liệu, không khung trống. Sửa → render lại (TTS được cache).
- Gửi người dùng bản nén 720p + thumbnail khi là thiết kế mới; chờ duyệt (`hold`).

## 7. Thumbnail & Đóng gói
Xem toàn bộ quy chuẩn đóng gói theo số liệu thực nghiệm, luật L1–L6 và công cụ kiểm lời hứa trong skill `long-packaging` (`.claude/skills/long-packaging/SKILL.md`).
Từ 23/10 (docs/adr/0005): nền AI không chữ (ChatGPT, mặt cận, chừa mảng trống) + chữ tự đặt
(`long/research/long_test/thumb_cb.py <nền> <ra> full q=175 "t=DÒNG1|DÒNG2|CÂU HỎI" pal=BUD|FS`): tên mỏ neo + chữ ưu tiên 2–5 từ (tối đa 8 khi cần nói rõ nghịch lý; PO 03/11: hiểu trong 1–2 giây trên điện thoại, không lặp title, đúng nguồn),
soát bản 168 px, so tờ đối thủ. Cũ: `hf_long_thumbnail.make(...)` (2 chữ lớn, 1 câu hứa, nhãn series) chỉ còn dự phòng.
Không trùng ảnh hero trong cùng series. Kiểm lời hứa bằng `python tools/long_packaging/promise_check.py <plan>`.

## 8. Đăng
`upload_long.py --only <id> --confirm`: riêng tư + hẹn giờ, dò sâu khung giờ (search.list
cộng dồn), mục lục chương có mốc, ghi nguồn ảnh + nhạc đúng track đã trộn, gắn thumbnail,
thêm playlist (công khai, idempotent). Mỗi kênh một API project, quota riêng; hết quota
search thì chờ reset 14:00 VN, không đăng mù. Kiểm lại bằng video ID (privacy, publishAt).
`upload_long` gọi `seo_check.check_row` (ticket 69) trước mỗi lần đăng: ERROR thì dừng (bỏ qua bằng `--seo-ok`).
Plan khai `"seo": {"keyword": "..."}` + tag đầu trùng keyword; keyword nằm trong 4 từ đầu tiêu đề, 150 ký tự đầu
mô tả và 3 câu đầu lời đọc. Tiêu đề > 60 ký tự, < 8 tag, > 5 hashtag chỉ cảnh báo.

## 9. Dọn
Sau khi đăng: chuyển mp4/wav của video đã đăng, bản render cũ, bản xem thử vào một thư mục
trong Thùng rác, đưa người dùng lệnh `rm -rf ~/.Trash/"<thư mục>"` — không tự xoá vĩnh viễn.
