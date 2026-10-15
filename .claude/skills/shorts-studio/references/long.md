# Studio trong video dài (16:9) — skin `studio_long` + visual `studio`

Từ 15/10/2026 bộ thiết bị và theme của Shorts Studio chạy được trong pipeline video dài (`hf_batch_render.py`, render theo chương,
TTS từng câu, foley, upload) mà không phải viết lại engine Long.

## Bật
Trong một mục plan Long (`output/cl_staging/long/plan_long_wNN.json`, build_X.py viết ra):
```json
{ "style": "studio_long", "theme": "saffron", ... }
```
- `theme` = file trong `hyperframes_short/studio/themes/` (saffron BUD, tet-poster FS, son-mai FS tối, archive lịch sử, blueprint).
  Bridge (`studio_long_inject`) tiêm: token `:root`, `--lf-theme` (paper/night theo độ sáng nền), `@font-face` trỏ
  `../studio/fonts` (woff2 có tiếng Việt, render không cần mạng), `kit.css`, `core.js` + mọi `devices/*.js`, `window.HFS_THEME`.
- Accent của video = accent của theme. Theme `"karaoke": false` -> phụ đề không chạy từng từ (BUD).
- Mọi sơ đồ cũ của `longform.js` (list, compare, stat, ledger, map, quote, shadow...) vẫn chạy: `--lf-*` ánh xạ từ token theme.
- Không bật `"kinetic"` với studio_long: thẻ chữ khoá của skin đã là chữ động kiểu studio (từng từ trồi theo giọng, gạch chân từ cuối).

## Visual `studio` = một thiết bị cho một câu (hoặc nhiều câu với `until`)
```json
"visuals": { "12": { "type": "studio", "device": "ledger", "until": 14, "title": "...",
                      "rows": [ { "y": "1990", "value": 38, "at": "@1990" },
                                { "y": "2002", "value": 26, "at": { "at": 13, "word": "2002" } } ] } }
```
- Trường giống hệt spec short (`references/devices.md`), riêng **mốc**:
  - `"@từ"` = lúc giọng đọc tới từ đó trong CHÍNH câu gắn thiết bị;
  - `{"at": n, "word": "từ", "offset": giây}` = câu n (số câu toàn video, bridge tự đổi sang câu trong chương).
  - Mốc phải nằm trong khoảng câu `n..until` (bridge kiểm như sơ đồ thường).
- Thiết bị vẽ bằng `cssW` (khổ ngang): vùng nội dung x 150..1770, y 120..850; dưới là dải phụ đề (đừng đặt chữ y > 860).
  Toạ độ do spec đưa (vd `stamps[].x/y`, `stampX/Y`) là toạ độ khung 1920x1080.
- Khác short: thiết bị hiện/ẩn theo cảnh của engine Long (chuyển cảnh của kho longform), không có seam studio.
  `calendar` khổ ngang có thêm `side` + `sideAt` (lời giải bên phải tờ lịch); `time_spine` nằm ngang; `split` thành hai cột.

## Thêm thiết bị cho cả hai khổ
`references/adding-a-device.md` + viết thêm `cssW`; geometry trong JS đọc `c.L` (`{W,H,wide,cx,top,bottom,left,right}`).

## Thử
`output/cl_staging/long_lab/build_lab.py` -> `plan_lab.json` (22 câu, đủ 18 thiết bị + sơ đồ cũ + ảnh + thẻ chương):
`HF_KEEP_HTML=1 .venv/bin/python hf_batch_render.py output/cl_staging/long_lab --only L_lab_fs --quality draft`.
