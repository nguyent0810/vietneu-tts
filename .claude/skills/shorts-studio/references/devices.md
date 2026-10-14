# Thiết bị hình (devices)

Mỗi thiết bị = một nhịp (thường một câu, 2,5-6s): khung riêng, vào cảnh theo từ đầu, phát triển theo mốc lời sau, seam ra cảnh sau.
Metadata (purpose / framing / axis / circle) dùng cho luật đa dạng -- khớp giữa `devices/*.js` (`meta`) và `DEVICES` trong `studio.py`.

## Đã có (engine 1.x)
| Thiết bị | Mục đích | Khung · trục | Trường chính | Ghi chú |
|---|---|---|---|---|
| `hook_poster` | hook | edge-band · static | `num` (số/năm nghiêng đỏ), `kick`, `big` (**nhấn**), `markWord`, `markAt` | Khung 0 đủ nghĩa; gạch chân vẽ ở `markAt` |
| `hook_slam` | hook | edge-band · Z | `kick`, `groups:[{text, big?, at}]`, `markAt`, `allAtStart` | Mỗi nhóm một trục (Z-slam/X-snap/Y-rise); `allAtStart:true` = mọi nhóm hiện ở khung 0, tới mốc thì nhấn lại |
| `split` | compare | stacked-split · mask | `a`/`b`: `{lab, val, num, at}`, `static` | Hai vùng cắt cạnh; `static:true` làm móc |
| `myth_strike` | compare | center-hero · X | `mythLab, myth, truthLab, truth, strikeAt, truthAt` | Gạch chéo ngộ nhận, sự thật đến bằng inverse zoom |
| `window` | statement | center-hero · in-glyph | `word, fill: rain\|solid\|image, img, lab, sub, subAt, size, y` | Chữ khổng lồ làm cửa sổ; `rain` vẽ bằng code |
| `wheel` | process | center-hero · 3D · **tròn** | `labels` (mặc định 12 chi), `target, also, alsoAt, links, linkR, linkAt, linkTone, kick, tag, tagAt` | Đĩa nghiêng quay về ô đích, làm phẳng, vẽ đường tam hợp/lục hợp |
| `cycle_draw` | process | center-hero · draw · **tròn** | `kick, nodes:[{id,label,tone,at}], edges:[{from,to,kind:outer\|inner,at}]` | Ngũ hành sinh/khắc, chu trình nước, vòng kinh tế |
| `calendar` | time | card-on-field · 3D | `pages:[{head,day,wd,lun}], flips:[anchor], stamp, stampAt, stampX, stampY` | Lịch bloc lật trang + dấu son |
| `time_spine` | time | world-camera · draw | `kick, items:[{yr,label,at}]` | Trục thời gian dọc, nhãn luân phiên |
| `stamp` | statement | edge-band · X | `han, kick, big, stamps:[{text,at,x,y,rot}]` | Chữ lớn + chữ Hán mờ + dấu son đóng theo lời |
| `source_card` | evidence | card-on-field · Y | `source, ref, snippet ([[cụm sáng]]), hlAt, seal, sealAt` | Dẫn nguồn trước phán định (kinh, sách, báo cáo) |
| `ledger` | list | grid · Y | `title, head[], rows:[{y, value, from, unit, at, valueAt, cells:[{k,v,at}]}]` | Bảng tra (năm sinh -> tuổi -> sao) |
| `list_build` | list | grid · X | `title, items:[{text, sub, key, at} \| {group, at}]` | Danh sách tích lũy, mục cũ mờ dần |
| `quote` | quote | center-hero · in-glyph | `text` (mặc định = câu `line`), `mode: karaoke\|rise`, `source, sourceAt` | Karaoke theo mốc từng từ thật |
| `count_ring` | number | center-hero · count · **tròn** | `label, value, from, decimals, suffix, at, pct, note, noteAt` | Đếm + vòng; đơn vị vào sau |
| `bars` | number | grid · X | `title, unit, bars:[{label,value,at,hot}], diff, diffAt` | Thanh ngang (9:16) |
| `unit_grid` | number | grid · Z | `title, total, cols, lit:[...], litAt, unitLabel` | "k trên N" |
| `close` | close | edge-band · mask | `q` (**nhấn**), `markWord, markSpan` | Câu hỏi kết, gạch chân cụm cuối |

## Lộ trình (taxonomy 45 thiết bị, chi tiết + rule nguồn: research/C_motion_inventory.md §4)
Ưu tiên tiếp theo (theo giá trị cho nhiều kênh):
- HOOK: `hook_search_query` (ô tìm kiếm gõ sẵn -- hợp chủ đề có nhu cầu tìm), `hook_roll_call` (neo cố định + ô quay token), `hook_macro_reveal` (cận cảnh -> lùi ra).
- NUMBER: `num_odometer` (năm/giá cuộn từng chữ số), `num_chart_scrub` (đường biểu đồ + đầu dò).
- COMPARE: `cmp_balance` (cán cân gắn giá trị), `cmp_theme_morph` (neo cố định, nền đổi qua các thời kỳ).
- LIST: `list_slot_ticker` (máy đánh bạc, ITEM_HEIGHT 1,4× cỡ chữ cho dấu tiếng Việt), `list_year_table` (bảng năm sinh dài, giữ lâu để chụp màn hình).
- PROCESS: `proc_flow_steps` (camera trượt dọc qua các bước), `proc_symbol_assemble` (biểu tượng ráp từng phần: sen, pháp luân, thái cực).
- PLACE: `place_floorplan` (sơ đồ nhà + la bàn xoay -- FS "lỗi phong thủy nhà ở"), `map_pin_route` (cần SVG bản đồ VN tự vẽ; registry không có).
- STORY: `story_whiteboard` (nét bút tự vẽ, không dùng font Caveat -- không có tiếng Việt), `story_3d_scene` (Three.js, <= 1/video; mẫu: jataka_engine.html).
- EVIDENCE: `ev_photo_annotate` (ảnh + vòng chú thích tay + nhãn; cần media-treatment), `ev_scrapbook`.
- CLOSE: `close_lockup_stamp` (câu chốt -> logo kênh + dấu).
Mỗi thiết bị mới: viết theo `references/adding-a-device.md`, thêm metadata vào `studio.py`, demo trong một spec, QA sạch rồi mới dùng cho lô.
