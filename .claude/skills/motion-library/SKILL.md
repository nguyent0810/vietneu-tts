---
name: motion-library
description: "Danh mục cảnh của kho hiệu ứng video dài (longform.js, style laban_long / inkwash_long): sơ đồ vòng 12 con giáp, ngũ hành, bản đồ, dòng thời gian, so sánh, số đếm, trích dẫn, chữ theo nghĩa, minh hoạ SVG, thẻ kết shader; bố cục ảnh (2.5D, ghim bảng, tràn khung...). Dùng khi viết `visuals`/`media` cho plan video dài, hoặc cần biết kho có hiệu ứng nào."
---

# Kho hiệu ứng video dài

Mã: `hyperframes_short/compositions/longform.js` + `longform.css`. Bộ chọn `pick()` lấy biến
thể ÍT DÙNG NHẤT trong video, không lặp lần ngay trước, rng hạt giống theo nội dung (render
lại y hệt). Ghi `"variant"` trong spec để ép. Xem cả kho: `python hf_showreel.py looks`
(Phase C riêng: thêm `c`).

## Sơ đồ — `visuals: {"<câu>": spec}`
Sơ đồ chiếm từ câu gốc tới `until` (mặc định = `at` lớn nhất trong steps/items/pins).
Không được đè ảnh/figure/sơ đồ khác (bridge chặn). Bước hiện đúng lúc đọc: `at` = số câu,
`word` = từ trong câu đó (mốc từ bám âm thanh thật, hf_align).

| type | spec | biến thể |
|---|---|---|
| `wheel` | `title, steps:[{at, rel: focus/xung/tamhinh/tamhop/luchop/hai/pha, chi:[...], label, word}]` | tilt, assemble, spin |
| `elements` | `title, year:{element, label}, steps:[{at, from, to, kind: sinh/khac/hoa, card:{yr,sub,note}, pill}]` | swing, rise |
| `years` | `items:[{yr, sub, note, at, word, mark}]` (mark = vòng tròn vẽ tay) | flip, deal, count |
| `list` | `title, items:[{at, text, word}]` (+ dạ quang mục đang đọc) | cascade, stack, spotlight |
| `timeline` | `title, items:[{yr, label, at, word, now}]` | — |
| `compare` | `title, left/right:{eyebrow, title, body, badge, at, word}` | — |
| `stat` | `value, suffix, label, at` (đừng đặt `word` ở cuối câu → vòng trống). QA 06/10: số + `suffix` dài ("260 chữ", "24 lá thư") hoặc số ≥ 5 chữ số TRÀN vòng → bỏ suffix, đưa đơn vị vào `label` ("CHỮ · ..."); số lớn dùng thẻ `word` | — |
| `doc` | `file` (+ `page` cho PDF Commons), `tag`, `tone`, `moves:[{x,y,z,at,word,d}]` — trang sách quét: phủ kín khung, lia tới dòng đang kể. Đừng dùng `photo` cho trang dọc (thu nhỏ không đọc được, nhãn đè phụ đề) | — |
| `quote` | `source?` — chữ = chính câu đang đọc, cụm `**...**` được tô | page (Vox), kinetic, glass |
| `map` | `countries, context, labels:{Tên: nhãn}, bbox:[lon0,lat0,lon1,lat1], route, pins:[{name, sub, lon, lat, at, word, side}]` | — (hf_geo nướng sẵn biên giới) |
| `word` | `text?, fx?` — mặc định cụm đánh dấu; fx theo nghĩa: dissolve, rays, split, crack, ripple, wave, flicker, grow, slam | — |
| `illus` | `scene: road/sunrise/lotus/moon/house, title?` | — |
| `endcard` | `text, sub` — nền shader WebGL | — |

Thẻ chương tự động cho câu in đậm trọn câu: zoom, slam, split, roll, depth, ink.
Chuyển cảnh tự chọn: push, pushup, zoom, wipe, iris, blurfade (vào thẻ chương = zoom/iris).

## Ảnh / clip — `media: {"<câu>": {kind: image|video, query, reveal?, layout?}}`
Plan Long mới (`"layout_policy": "v2"`, skill long-video) bỏ trống `layout`/`cine` thì `hyperframes_bridge.assign_layouts_v2` gán. Plan thiếu khoá này giữ `auto_layouts` (chia đều). Tên layout: frame (ô của style), full (+ chữ khoá bật theo lời, da kính hoặc chữ), card3d, split, split_r, polaroid, pinned, **depth** (2.5D: tách chủ thể bằng Vision; không tách được → card3d). Clip video: full / card3d / frame, không gắn cine. `reveal`
(ink chỉ nền giấy, wipe, iris, rise) — depth bỏ reveal. Ảnh giữ qua các câu sau tới ảnh
kế / tiêu đề chương / sơ đồ / 22 giây.

## Không khí (tự động)
Hạt bay (bụi vàng nền chàm / cánh hoa nền giấy), vệt sáng ấm mỗi lần sang chương, chùm hạt
bung ở thẻ chương, vệt sáng kính lướt qua panel.

## Short dọc BUD (silence, oilpaint, lightfield, inkwash, dustbeam)
Các style này nạp `longform.js` + `shortform.css` (đặt lại vị trí cho 1080x1920). Plan short
(`output/cl_staging/bud/plan_b*.json`) thêm `visuals` như video dài, NHƯNG chỉ 5 loại:
`word`, `quote`, `illus`, `stat`, `list` (bridge chặn loại khác). Chuyển cảnh + không khí
vẫn là của style short. Công thức 5 câu: câu 1 hook = `word` (fx theo nghĩa) hoặc `stat`
(số đếm chạm đích đúng lúc đọc); 2–3 ảnh; câu có lời kinh = `quote` + `source` (thẻ chỉ mang
phần sau dấu hai chấm); câu kết = `illus` hoặc ảnh. `list` ≤ 4 mục, `until` nếu mục nằm ở
câu sau. Không đặt `title` cho illus (đè dòng kicker).
Câu 1 (hook) không dùng `reveal: ink`: vệt mực loang ~1 giây đầu là tờ giấy trống.
Mốc `word` phải là từ ở ĐẦU câu (vd "vòng", "nối"), không phải từ cuối câu -- nếu không
bước sơ đồ chỉ kịp hiện nửa giây trước khi chuyển cảnh.

## Phase D cho short (mặc định từ 30/09/2026, người dùng đã duyệt demo)
Mượn từ hồ sơ S-tier của Youtube_Creator_V2. Mỗi row short thêm:
`"caps": "chunk", "loop": true, "sfx": true, "silence": [<câu ask>]`.
- `sfx` (hf_sfx): tiếng động bám mốc cảnh -- BUD chuông/chuông xoay/mõ, FS cồng/tích tắc;
  mức mặc định `sfx_gain` 0.42 (người dùng xin nhỏ hơn bản demo 0.55).
- `caps: chunk`: phụ đề 2–4 chữ, chữ nhấn tô màu. `loop`: khung cuối về cảnh mở màn.
- `silence`: câu hỏi lặng (visual `ask`) -- không phụ đề, không tiếng, nhạc nền tắt.
- Cảnh mới: `doc` {file|query, moves[{at,word,x,y,z,d}], tone, tag} lia máy trên ảnh tư liệu;
  `photo` {file|query, circles[{x,y,r,at,word}], label} ảnh in + vòng khoanh đỏ;
  `clock` {title, until, steps[{at,word,chi}]} 12 canh giờ; `ask` {text?}; quote `variant: "type"`
  (máy chữ); `timeline` dọc ở khung dọc.
- Ảnh tư liệu: `hf_commons.py search "<từ khoá>"` (chỉ PD/CC0) -> `"file": "File:..."` trong
  visual doc/photo hoặc media `{"kind": "commons", "file": ...}`. Toạ độ khoanh: kẻ lưới ảnh rồi đọc.

## Thư viện tham khảo ngoài + quy ước dạng cảnh — `references/prompt_motion/`
234 mẫu prompt-motion.com phân loại cho FS/BUD (25/10/2026). Đọc `quy_uoc.md` trước khi chọn cảnh hay viết cảnh mới:
12 luật chung (một cảnh một ý, chuyển động bám lời, cấm crossfade / hạt bung / lens flare / glow / HUD góc, mọi khung là hàm
thuần của t, soát khung tĩnh trước render), 12 dạng cảnh D1–D12 kèm spec và mẫu, hàng đợi cảnh MỚI (ưu tiên `shadow_theatre`,
`paint_over`), và các thành phần engine đang vướng danh sách cấm (`blurfade`, hạt bung thẻ chương, `lens-flare`).
Giao thợ viết cảnh mới bằng `prompt_mau.md`.

## Chọn cảnh cho kịch bản
Mỗi 3–5 giây một thứ mới trên màn hình. Con số/năm → years/timeline/stat. Quan hệ con giáp
→ wheel. Mệnh → elements. Địa danh → map. Hai vế đối lập → compare. Lời kinh / câu đáng
nhớ → quote. Một khái niệm mạnh (vô thường, tỉnh thức) → word. Mở chương cảm xúc → illus.
Lời chào cuối → endcard. Còn lại để ảnh/video theo `layout_policy` của plan (skill long-video).

## Công thức short v2 (BUD + FS, bắt buộc từ lịch 14/11/2026 — `hf_batch_render.short_v2_issues` chặn render)
Rút từ đánh giá 28 ngày tới 03/10/2026 (`python hf_shorts_report.py <từ> <đến> --curves`): short nào cũng dừng ở
~900–1.000 view (vòng thử feed Shorts), chỉ bài xem hết > 90% mới bứt lên. Bài yếu rơi người xem ở 20–50% thời
lượng = câu 2, khi câu 2 là định nghĩa/thuật ngữ. Bài < 20 giây bị feed đẩy kém (FS trung vị 122 view).
- Câu 1 (<= 22 tiếng): tình huống cụ thể có người xem trong đó ("Sếp khen đồng nghiệp trước cả phòng...").
- Câu 2: LẬT — đối lập bằng hình ảnh cụ thể ("người kia đã ngủ yên, còn mình nằm thức"). KHÔNG "gọi là / nghĩa là / Nhà Phật gọi đó là".
- Câu 3–4: nội dung, thuật ngữ, lời kinh (quote `variant: "type"` + số kinh), mẹo thực tế.
- Câu 5: trả lời đúng câu hỏi của tiêu đề, nối ý về câu 1 (vòng lặp `loop`).
- Câu 6: hỏi lặng (`ask`, `silence: [6]`) mời bình luận.
- BUD 80–102, FS 68–88 tiếng đọc (không tính câu hỏi lặng) ≈ 21–27 giây. Năm sinh dùng `word`, không dùng `stat` (stat in "1.990").
- Row thêm `insight` (câu trả lời một câu → dòng đầu mô tả + hashtag có dấu), `tags_vi` (tag có dấu),
  tuỳ chọn `hashtags`, `cta`. Uploader (upload_bud.py / upload_fs.py) tự dựng mô tả mới khi có `insight`.
- Chủ đề: BUD ưu tiên lane `niem`/`doi` (đời thường, cảm xúc — xem hết 78%), `phap` thuần lý thuyết yếu nhất (58%,
  0,3 đăng ký/1k) → giáo lý phải đi qua một tình huống. FS ưu tiên chuyện của chính người xem (năm sinh/mệnh/tuổi,
  mẹo nhà ở); Kinh Dịch lý thuyết chuỗi khái niệm (f29_c "Thái cực sinh lưỡng nghi" 34%) tránh, hoặc buộc vào đời sống.
- **Short v3 (lịch từ 18/11/2026): "neo" + hồn riêng.** Bài học kênh CL (V2, 05/10/2026): short neo vào vụ án có tên riêng
  hồi từ 0 lên ~1.000 view trong vài giờ; mô tả mở bằng một đoạn kể ngắn + link nguồn; tag là tên riêng có dấu.
  KHÔNG chép nguyên xi: mỗi short ghi `"anchor"` (tên riêng / con số / chi tiết cụ thể) có mặt trong tiêu đề hoặc câu đầu.
  - BUD: neo = nhân vật, nơi chốn, vật trong kinh và Phật giáo Việt (Angulimāla, Kisā Gotamī, Anāthapiṇḍika, Kỳ Viên,
    Trần Nhân Tông, Yên Tử, chuông chùa, chiếc mõ). Giọng hiền, chữa lành; lời Phật kèm số kinh, `source` có link SuttaCentral
    (`hf_sutta.link("Trung Bộ 86")`). Ví dụ: "Angulimāla bị ném đá, Đức Phật chỉ nói một câu" thay cho "Lỡ làm sai có sửa được không?".
  - FS: neo = năm sinh, ngày cụ thể, địa danh/nhân vật Việt (Tả Ao, kinh thành Huế, Văn Miếu, Tết 6/2/2027), vật trong nhà
    (lọ hoa bàn thờ, hũ gạo muối nước). Giọng "truyền thống để tham khảo", có phần thực tế. Ví dụ: "Lọ hoa bàn thờ: trái hay phải,
    người xưa xếp theo nguyên tắc nào?" thay cho "Bàn thờ đặt hoa thế nào cho đúng?".
  - Runner CHẶN lời giật gân (`short_tone_issues`: chấn động, rợn người, tiền về ồ ạt, tiên tri, đổi đời...) và NHẮC thiếu
    neo / thiếu link kinh (`short_hook_hints`). Giờ đăng: `hf_slots.current(kênh)` (tự đổi giờ yếu, xem `hf_slots.py`).
- Nhạc nền short (lịch từ 18/11/2026): mỗi short một bài, `hf_music.short_pick` (ít dùng nhất trong 8 short gần nhất,
  sổ `output/cl_staging/<kênh>/bgm_shorts.json`, bản cắt cùng độ to bài chuẩn trong `chunks_cache/bgm_short/`); uploader
  ghi nguồn đúng bài từ render.json. Trước đó cả 240 short BUD / 113 short FS chung một bài.
- Chọn chủ đề/góc: đọc `output/cl_staging/briefs/<kênh>.md` (hf_brief: short cao/thấp nhất kèm câu mở, giờ, độ dài; cầu ngoài).
- Upload BUD/FS: `youtube_upload` giữ sổ `output/upload_log.json` (session trước byte đầu, đứt thì hỏi lại phiên, trần 24
  upload/24 giờ/kênh -> `UploadPacingHold`); "đã upload" / `UploadInDoubt` -> kiểm kênh rồi `python youtube_upload.py --forget <file>`.
- Trùng chủ đề: `python hf_novelty.py check <bud|fs> "Tiêu đề"` (so với ~1.700 video mỗi kênh, cả nguồn ngoài; làm mới bằng `hf_novelty.py refresh`). Guard v2 chặn; đã soát tay thấy khác thì ghi lý do vào `novelty_ok`.
- Mẫu: `output/cl_staging/build_shorts_v2_1.py` (b44, f40), `build_shorts_v2_2.py` (b45, f41).

## Kiểu chữ thẻ chữ `word` — plan `"wordts": true` (04/10/2026, mặc định cho long/short mới)
Trước đó mọi thẻ chữ cùng Be Vietnam Pro 800 màu kem. Giờ `pick()` xoay kiểu ÍT DÙNG NHẤT, không lặp liền kề
(ép bằng `"ts"` trong spec). Phông nạp ở bridge (WORDTS_FONTS, đều có bộ tiếng Việt), kèm Lora cho thẻ trích kinh.
- BUD: solid · duo (2 cỡ, từ nhấn màu) · editorial (Playfair nghiêng + 2 vạch) · serene (Cormorant) · script (Charm nét bút)
  · marker (chữ sẫm trên vệt dạ quang) · outline (Oswald rỗng, từ nhấn tô đặc).
- FS: solid · duo · editorial · gold (Fraunces mạ vàng, chỉ nền tối) · poster (League Gothic + vạch) · outline · marker (nền tối).
- `"A · B"` → vế A nhỏ, xuống dòng, vế B to màu nhấn. Một vế: nhấn 1–2 tiếng cuối.
- Chuyển động mượn beat.js của Youtube_Creator_V2: thẻ không có `fx` theo nghĩa thì xoay slam/rise/drop/type;
  `"KHÔNG PHẢI X · Y"` (cả ĐỪNG/SAI/CHẲNG PHẢI) tự `strike`: gạch vế X rồi làm mờ — hợp phá ngộ nhận.
- split/crack chỉ dùng kiểu một dòng (không duo/marker/outline).
- Chuyển động thêm (04/10 tối): `sync` — mỗi từ hiện ĐÚNG lúc giọng đọc tới (mốc hf_align), từ nhấn nảy khi được
  đọc; cụm nằm cuối câu thì hiện mờ trước (luật dead-air của V2) · `flip` lật 3D từng từ · `wipe` vệt quét + gạch chân
  · `zoom` lao từ xa tới rồi trôi · `breathe` giãn chữ + nhoè khép lại (chỉ xoay vào khi kiểu serene/script).
  Các chuyển động mới cho cả khung chữ trôi chậm (scale 1→1.035) để thẻ không đứng im. Ép bằng `"fx"` trong spec.

## Kho ảnh ngoài Commons — `hf_extmedia.py` (media `{"kind": "ext", "ref": "<nguồn>:<id>", "tagged": true}`)
Wellcome (tranh Ấn/Hoa xưa, Phật bằng màu bột PD), Art Institute of Chicago (CC0; IIIF tối đa 843px + header
AIC-User-Agent — đây là lý do `aic:` từng 403), Europeana (ảnh Đông Dương: Rijksmuseum, Deutsche Fotothek…; từ khoá
"Hanoi", "Tonkin" chứ không "Indochine pagode"). `hf_media_sheet.py find` hiện các ứng viên này với mã X.

## Phim tư liệu PD/CC — `hf_pdvideo.py` (media `{"kind": "pdvideo", "ref": "...", "start": 12, "dur": 15, "fit": "cover", "label": "TƯ LIỆU 1921"}`)
Clip động thật thay cho Pexels: Wikimedia Commons (Lumière/Veyre 1896-1900, Albert-Kahn/Léon Busy 1913-1921 ở Hà Nội,
chùa Hương, Phù Đổng, Angkor — CC0), Internet Archive (chỉ Prelinger / FedFlix-NARA / cơ quan liên bang Mỹ / phim
≤1930 có PDM; giấy phép người tải tự khai bị loại), NASA (trăng, sao). `ref`: `commons:File:X.webm` | `ia:<id>[/<file>]` |
`nasa:<id>`. Cắt tối đa 20 s → mp4 1920x1080 không tiếng (`fit`: cover · pad · blur — phim 4:3 nên dùng `blur`).
Chọn đoạn bằng `python hf_pdvideo.py strip <ref>` (dải khung hình kèm mốc giây). Danh mục đã kiểm:
`output/cl_staging/long/research/pdvideo_refs.json`. Giữ file .json cạnh mp4 (bằng chứng giấy phép).

## Bộ style bổ sung (#258) — dùng tiết chế, CHỈ khi plan gọi tên
Sáu cảnh "điểm nhấn" lấy ý tưởng thị giác từ catalog animation ngoài (viết lại clean-room trong
`longform_styles.js` + `longform_styles.css`, nạp sau `longform.js` ở 7 style Long). Chúng KHÔNG phải nền chính:
không bộ chọn nào (pick, LAYOUT_POOL, studio, builder) tự chèn; không đổi mặc định của cảnh nào ở trên. Luật PO:
mỗi video Long **tối đa 3 cảnh style**, **không hai cảnh style liền nhau** (bridge chặn mỗi lần render,
`hf_batch_render.style_scene_issues` chặn cả plan). Mọi cảnh bám mốc câu như thường (`at`/`word`, `until`); tất định
(hạt phim, bút, mực sôi tính từ t); chữ tiếng Việt có dấu (Anton, Yeseva One, Cormorant, Dancing Script, Itim, IBM Plex Mono —
cố ý KHÔNG trùng họ font kho đã nạp, vì @font-face kép làm lệch raster chữ của cảnh cũ).
Xem mẫu: `python hf_style_demo.py stills` (PNG) hoặc `python hf_showreel.py looks s1|s2|s3` (video).

| type | khi nào | kênh | spec |
|---|---|---|---|
| `woodcut` | một thông điệp mạnh, châm ngôn, con số, mở/kết chương kiểu mộc bản (mực đen + son đỏ trên giấy dó) | BUD (kinh mộc bản), FS (sấm ký, ấn), Văn Sử Địa, CL (poster tuyên ngôn) | `text` ("A · B": A nhỏ, B to), `motif`: lotus/bagua/enso/pagoda/house/mountain/incense/meditator/gate/tower, hoặc `value` (số lớn thay motif), `tone`: paper/dark (mặc định theo theme), `steps[0]` = lúc băng chữ hiện |
| `papercut` | mở cảnh kể chuyện, không khí nơi chốn (diorama giấy cắt nhiều lớp, thị sai, nguồn sáng đổi) | BUD (tích Phật, chùa), FS (long mạch, làng), Văn Sử Địa (thành cổ) | `scene`: pagoda/mountain/citadel/village, `time`: night/dawn/day/dusk, `text`, `sub`, `steps[0]` = thẻ chữ, `steps[1]` = cửa sáng đèn |
| `oneline` | nối 2–4 ý bằng một nét liền (thiền, khí mạch, chuỗi khái niệm tối giản) | BUD, FS, MIM (ý tưởng nối ý tưởng) | `items:[{motif, label, at, word}]` (≤4; motif như woodcut), `title`, `tone` |
| `film16` | tư liệu lịch sử, mở hồ sơ vụ án, "năm ấy…" (đen trắng, hạt, xước, thẻ tiêu đề khung kép, đếm ngược) | Văn Sử Địa, CL, BUD/FS khi kể sử | `kicker`, `title`, `sub`, `year` (→ số La Mã), `leader: true` (đếm ngược 2 s), `caption` (gõ máy, góc trên trái), ảnh nền tuỳ chọn `file`/`query`/`museum` (bridge tải như `doc`); `steps[0]` = thẻ (khi có ảnh), `steps[1]` = caption |
| `blueprint` | mặt bằng, mặt cắt, hướng nhà, sơ đồ hệ thống, biểu đồ cột có kích thước | FS (bát trạch, mặt bằng), Văn Sử Địa (thành luỹ, địa lý), MIM (sơ đồ máy), CK (biểu đồ) | `scene`: house/wall, hoặc `items:[{kind: rect/circle/line/poly/dim/label/hatch, …, at, word}]` (toạ độ 1920×1080), hoặc `bars:[{label, value, at, word}]` + `unit`; khung tên: `title`, `sub`, `scale`, `code`, `sheet` |
| `pencil` | ký hoạ di tích/vật chứng, "hình dung lại" không lộ mặt (dựng hình → nét → tô bóng) | Văn Sử Địa, CL (ký hoạ hiện trường), BUD (ký hoạ chùa), MIM | `scene`: pagoda/gate/boat/tower/bust/lotus/house/mountain, `title`, `sub`, `notes:[{text, x, y, at, word}]` (≤4, x/y = điểm mũi tên trỏ), `steps[0]` = tiêu đề |

Ví dụ (Long Văn Sử Địa, 3 cảnh cách nhau):
```json
"visuals": {
  "4":  {"type": "film16", "kicker": "Phim tư liệu", "title": "Lũy Thầy", "sub": "Đào Duy Từ", "year": 1631, "leader": true, "caption": "Đồng Hới, 1631"},
  "19": {"type": "blueprint", "scene": "wall", "title": "Luỹ Thầy · mặt cắt", "scale": "1 : 500", "code": "LT-01"},
  "41": {"type": "woodcut", "text": "Một luỹ · chặn cả đàng ngoài", "motif": "gate", "steps": [{"at": 41, "word": "chặn"}]}
}
```
Không hợp: BUD không dùng `film16` cho hình Đức Phật (ảnh phải nguyên vẹn, trang nghiêm — chỉ thẻ tiêu đề/ảnh chùa);
FS giữ `tone: dark` cho woodcut/oneline/pencil trên nền chàm (mặc định theo theme: night → tối, paper → giấy).
Short dọc chưa mở (bridge chặn như các cảnh Long khác). CL/MIM/CK (creator_v2): Long của họ dựng bằng
`motion/hf/assets/engine/casewide.js` (HyperFrames, không nạp longform.js) → muốn dùng thì đồng bộ hai file
`longform_styles.*` sang `creator_v2/motion/hf/compositions/` (bản sao của `hyperframes_short/`) và thêm một loại cảnh
casewide gọi `HF_LONG.visuals.<style>.build/enter` với `ln`/`ctx` cùng khuôn (`start`, `end`, `words`, `until`).
