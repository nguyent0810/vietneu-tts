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
