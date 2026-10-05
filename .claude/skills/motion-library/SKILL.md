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
| `stat` | `value, suffix, label, at` (đừng đặt `word` ở cuối câu → vòng trống) | — |
| `quote` | `source?` — chữ = chính câu đang đọc, cụm `**...**` được tô | page (Vox), kinetic, glass |
| `map` | `countries, context, labels:{Tên: nhãn}, bbox:[lon0,lat0,lon1,lat1], route, pins:[{name, sub, lon, lat, at, word, side}]` | — (hf_geo nướng sẵn biên giới) |
| `word` | `text?, fx?` — mặc định cụm đánh dấu; fx theo nghĩa: dissolve, rays, split, crack, ripple, wave, flicker, grow, slam | — |
| `illus` | `scene: road/sunrise/lotus/moon/house, title?` | — |
| `endcard` | `text, sub` — nền shader WebGL | — |

Thẻ chương tự động cho câu in đậm trọn câu: zoom, slam, split, roll, depth, ink.
Chuyển cảnh tự chọn: push, pushup, zoom, wipe, iris, blurfade (vào thẻ chương = zoom/iris).

## Ảnh / clip — `media: {"<câu>": {kind: image|video, query, reveal?, layout?}}`
`layout` bỏ trống → tự luân phiên: frame (ô của style), full (+ chữ khoá bật theo lời, da
kính hoặc chữ), card3d, split, split_r, polaroid, pinned, **depth** (2.5D: tách chủ thể
bằng Vision; không tách được → card3d). Clip video ưu tiên full/card3d/frame. `reveal`
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

## Chọn cảnh cho kịch bản
Mỗi 3–5 giây một thứ mới trên màn hình. Con số/năm → years/timeline/stat. Quan hệ con giáp
→ wheel. Mệnh → elements. Địa danh → map. Hai vế đối lập → compare. Lời kinh / câu đáng
nhớ → quote. Một khái niệm mạnh (vô thường, tỉnh thức) → word. Mở chương cảm xúc → illus.
Lời chào cuối → endcard. Còn lại để ảnh/video tự luân phiên.

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
