# GH-159 B1 — kiểm kê chỉ đọc hai luồng dựng

Ngày đo: 2026-11-05. Chỉ đọc. Không sửa code, cấu hình, dữ liệu. Không render, không upload, không enqueue, không commit, không đổi lịch. Không in biến môi trường.

Đường dẫn tính từ `vietneu-main/`. Luồng A = BUD/FS/VSD. Luồng B = MIM/CK/CL trong `creator_v2/`.

## Cách đo

- Issue #159, mục Vì sao / Mục tiêu / Luật bắt buộc: một engine cho 6 kênh; kênh là dữ liệu trong `library/channels/*.yaml`; mỗi bước gộp là một PR nhỏ; không đụng video đã đăng hay đã hẹn.
- Hai luồng không gọi nhau. `creator_v2/**/*.py` không có chuỗi `hf_batch_render`, `hyperframes_bridge`, `library.tools`, `library/tools`. Trong `hf_*.py` ở gốc, chỗ nhắc `floor.py` là chú thích, `hf_batch_render.py:731`.
- Builder `output/cl_staging/*/build_*.py`: không có file `build_*.py` dưới `output/cl_staging` trên máy này. Ngoài phạm vi máy này.
- `output/cl_staging/scoreboard/hook_lint.py`: không có trên máy này (`tests/test_hook_lint.py:12` cũng ghi file này chỉ có trên máy dựng). Nội dung cổng đó: chưa kiểm.
- Repo `Youtube_Creator_V2/`: không chạy lệnh. Bản `webauto` cũ mà issue nhắc: chưa kiểm.
- `creator_v2/.ref/vietneu-main/` là một cây gương. Chưa kiểm có được import hay không. Không tính vào luồng chạy. Cặp trùng tên bên dưới chỉ tính file luồng chạy.

`git diff --no-index --stat`: exit 0 và không in dòng = giống hệt.

## Số dòng engine (đếm dòng vật lý)

| File | A `hyperframes_short/` | B `creator_v2/motion/hf/` |
|---|---:|---:|
| `compositions/longform.js` | 4100 | 1307 |
| `compositions/longform.css` | 941 | 296 |
| `compositions/engine.js` | 560 | 448 |
| `compositions/shortform.css` | 73 | 46 |
| `compositions/base.css` | 252 | 252, giống hệt |
| `compositions/wide.css` | 15 | 15, giống hệt |
| `assets/engine/casewide.js` | không có | 1171 |
| `assets/engine/casewide.css` | không có | 560 |
| `assets/engine/casefile.js` | không có | 727 |
| `assets/engine/casefile.css` | không có | 239 |
| `assets/engine/chart.js` | không có | 578 |
| `assets/engine/lab.js` | không có | 270 |
| `assets/engine/beat.js` | không có | 121 |
| `assets/engine/beat2.js` | không có | 46 |

Khớp bảng trong issue (4100 / 1307 / 941 / 296 / 560 / 448). `git diff --no-index --stat` bản A sang bản B:

- `compositions/longform.js`: 55 insertions, 2848 deletions
- `compositions/longform.css`: 2 insertions, 647 deletions
- `compositions/engine.js`: 8 insertions, 120 deletions
- `compositions/shortform.css`: 27 deletions

## Loại cảnh — đủ tên, kèm dòng đăng ký

Hai bên không cùng hợp đồng. A gắn sơ đồ vào câu (`visual.type`, `media.layout`). B gắn cảnh vào `scenes[].type` rồi `B[type]`.

### A — `longform.js` (Long/Short style nạp file này)

Bảng hợp đồng: `hyperframes_bridge.py:160-166`.

`VISUAL_TYPES`, 41 tên. Dòng là chỗ gán trong `hyperframes_short/compositions/longform.js`:

| Tên | Dòng | Tên | Dòng | Tên | Dòng |
|---|---:|---|---:|---|---:|
| wheel | 247 | elements | 357 | years | 469 |
| list | 514 | timeline | 560 | compare | 601 |
| stat | 634 | quote | 775 | map | 907, gán lại 3038 |
| region | 999 | profile | 1115 | word | 1777 |
| illus | 2036 | endcard | 2083 | doc | 2137 |
| photo | 2174 | clock | 2209 | ask | 2282 |
| shadow | 2449 | hexagram | 2525 | luoshu | 2589 |
| ledger | 2663 | breath | 2703 | museum | 2821 |
| napam | 2875 | cuudieu | 2906 | eclipse | 2954 |
| lookup | 3079 | annot | 3163 | relic | 3227 |
| chiwheel | 3301 | pie | 3375 | compass | 3423 |
| teaser | 3472 | clues | 3512 | stamp | 3568 |
| scroll | 3590 | dialog | 3626 | wind | 3662 |
| bagua | 3713 | studio | 3850 | | |

`list` và `years` được bọc lại ở 1188 và 1195, vẫn là hai loại đó.

Bố cục ảnh `MEDIA_LAYOUTS`, 7 tên (`hyperframes_bridge.py:164`): `full` 91, `split_r` 116, `polaroid` 136, `card3d` 146, `split` 156, `pinned` 839, `depth` 863. `LAYOUT_POOL` thêm `frame` (`hyperframes_bridge.py:229`).

Motion preset, 6 tên (`hyperframes_bridge.py:165`): `slow_zoom`, `pan_focus`, `push_detail`, `parallax`, `highlight`, `reveal`. Thân `slow_zoom` ở `longform.js:3927`.

`engine.js` còn 5 loại figure: `threshold` 72, `range` 86, `flow` 96, `timeline` 103, `stat` 120.

Kinetic của A là cờ plan, không phải `type` trong `VISUAL_TYPES`: `engine.js:184`, khối ở `longform.js:2731`.

Short Studio, 21 thiết bị (`studio.py:37-59`): `hook_poster`, `hook_slam`, `split`, `myth_strike`, `window`, `wheel`, `cycle_draw`, `calendar`, `time_spine`, `stamp`, `source_card`, `ledger`, `list_build`, `quote`, `close`, `pan_tour`, `count_ring`, `bars`, `unit_grid`, `month_sheet`, `thiep_cuoi`. File thiết bị: 12 file trong `hyperframes_short/studio/devices/`.

Style HTML (`hyperframes_bridge.py:238-270`) là lớp da (inkwash, laban, dossier, …), không phải loại cảnh. `dossier` / `casemap` nằm ở đây.

Short dọc chỉ được 12 visual (`hyperframes_bridge.py:235-236`): `word`, `quote`, `illus`, `stat`, `list`, `wheel`, `elements`, `doc`, `photo`, `clock`, `ask`, `timeline`.

### B — casefile / casewide (đường sản xuất MIM/CK/CL)

Long: `build_long.py` nạp `lab.js`, `chart.js`, `casewide.js` (`build_long.py:907-909`). Không nạp `compositions/longform.js`.

Short: `motion/stier/build.py` nạp `casefile.js` (`build.py:672`). `hfs/*.js` chỉ khi `theme == "bud"` và có cảnh `hf_*` (`build.py:477-484`).

`casefile.js` đăng ký 24 loại (`B.<tên> =`). Bảng README ghi 19 (`motion/stier/README.md:69-91`). Năm loại có trong engine, không có trong bảng README: `source` 369, `chart` 484, `board` 558, `cards3d` 597, `table` 622. `quote` gán hai lần; bản chạy là 365.

| 19 loại trong README | Dòng casefile.js |
|---|---:|
| hero | 53 |
| date | 102 |
| doc | 127 |
| photo | 144 |
| counter | 182 |
| calendar | 202 |
| clock | 221 |
| file | 239 |
| crowd | 254 |
| map | 297 |
| mug | 330 |
| question | 336 |
| quote | 365 |
| kinetic | 393 |
| evidence | 414 |
| split | 433 |
| timeline | 444 |
| ledger | 453 |
| slam | 463 |

`casewide.js` đăng ký 34 loại: `chapter` 125, `broll` 145, `photo` 171, `print` 202, `file` 232, `kinetic` 262, `slam` 269, `brand` 316, `endcard` 334, `question` 346, `counter` 353, `bars` 378, `myth` 404, `source` 421, `units` 437, `timeline` 453, `map` 469, `quote` 500, `org` 520, `ledger` 539, `split` 551, `date` 564, `cards` 587, `evidence` 604, `seismo` 626, `saint` 656, `paper` 680, `pizzini` 699, `dots` 715, `board` 732, `memorial` 749, `calendar` 768, `sticker` 785, `sketch` 1103. Loại lạ thì ném lỗi (`casewide.js:1133`).

`lab.js` gắn thêm 11 loại, không kiểm `theme` (`lab.js:16`): `punch` 19, `guess` 40, `chat` 60, `nn` 76, `go` 93, `chess` 115, `qr` 144, `barcode` 179, `flap` 194, `captcha` 218, `keyboard` 255. `casewide.js:1127` gọi `labScenes` mỗi khi file đã nạp. Long CL/MIM/CK đều nạp file này.

`chart.js` chỉ gắn khi `C.theme === "chart"` (`chart.js:8-9`): `brand` 43 (đè `brand` của casewide), `candles` 81, `race` 143, `breadth` 237, `basket` 317, `waterfall` 404, `heat` 438, `stack` 465, `book` 507. Cheatsheet CK nêu `race`, `waterfall`, `heat`, `stack` (`docs/codex/long-cheatsheet.md:91-94`). Cheatsheet không phải bảng đủ loại.

`hfs`, 13 thiết bị, tên runtime là `hf_<tên>` (`hfs/bridge.js:3`, `casefile.js:667`): `stamp`, `source_card` (`mark.js:3,24`); `calendar`, `time_spine` (`time.js:3,31`); `split`, `myth_strike` (`compare.js:3,31`); `wheel`, `cycle_draw` (`cycle.js:5,53`); `ledger`, `list_build` (`table.js:3,37`); `count_ring`, `bars`, `unit_grid` (`number.js:2,31,59`).

Bản `compositions/longform.js` trong B chỉ có 12 visual: `wheel` 246, `elements` 356, `years` 468, `list` 513, `timeline` 559, `compare` 596, `stat` 627, `quote` 749, `map` 839, `word` 1052, `illus` 1210, `endcard` 1257. Bố cục: 5 cái trong object (`full` 89 … `split` 154) cộng `pinned` 796, `depth` 820. File này được vài HTML chép sang nạp (`inkwash_long.html:88`, `laban_long.html:74`, và các HTML short cùng thư mục). `build_long.py` và `stier/build.py` không trỏ tới các HTML đó.

Số lượng, đếm theo bảng đăng ký:

| Engine | Số loại |
|---|---:|
| A visual longform | 41 |
| A layout ảnh | 7 (+ `frame`) |
| A motion preset | 6 |
| A figure trong engine.js | 5 |
| A thiết bị Studio | 21 |
| B casefile | 24 (README liệt kê 19) |
| B casewide | 34 |
| B lab (cộng khi Long nạp lab.js) | 11 |
| B chart (chỉ theme chart; `brand` đè, 8 tên mới) | 9 gán / 8 tên mới |
| B hfs (chỉ short theme bud) | 13 |
| B longform.js (không phải đường Long/Short MIM/CK/CL) | 12 visual |

## Ma trận năng lực

Trạng thái: `chỉ A`, `chỉ B`, `trùng`, `lệch`.

### 1. Loại cảnh và engine

| Năng lực | A | B | Trạng thái | Giữ | Rủi ro gộp |
|---|---|---|---|---|---|
| Cửa Long | `hf_batch_render.py` + style trong `hyperframes_bridge.py:259-269` | `motion/long/build_long.py:1`, HTML nạp casewide `885-909` | lệch | Giữ cả hai cửa đến khi B3 so được một chương `golden` và một Long BUD/FS | cao |
| Cửa Short | `studio.py:1` (thiết bị) và style short của bridge | `motion/stier/build.py`, casefile | lệch | Giữ cả hai | cao |
| Sơ đồ tử vi / phong thuỷ (wheel, bagua, lục hào, …) | 41 visual, bảng trên | longform B chỉ 12 visual đầu; casewide không có các tên này | chỉ A | Giữ bản A | cao nếu trộn vào casewide một lượt |
| Hồ sơ vụ án (file, mug, evidence, sketch, seismo, …) | style `dossier` là da, `hyperframes_bridge.py:240`; không có `B.file` | casewide `file` 232, `evidence` 604, `sketch` 1103; casefile `mug` 330 | chỉ B | Giữ casewide/casefile cho CL. Sáu Long đã đăng là chuẩn | cao |
| Bản đồ biên giới | `visuals.map` `longform.js:907`; nướng bằng `hf_geo.py` | casewide `B.map` 469, casefile `B.map` 297; nướng bằng `creator_v2/motion/hf_geo.py` | lệch | Giữ renderer B cho CL; giữ lớp đảo của A (dòng dưới) | cao |
| Lớp Hoàng Sa / Trường Sa | `hf_geo.py:8`, vẽ ở `hf_geo.py:421`; inset `longform.js:884` | `creator_v2/motion/hf_geo.py` không có chữ Hoàng Sa/Paracel; casewide không đọc `islands` | chỉ A | Giữ bản gốc `hf_geo.py` | vừa |
| Chữ kinetic | cờ plan, `engine.js:184`, `longform.js:2731` | `casewide.js:262`, `casefile.js:393` | lệch | Giữ hợp đồng từng bên đến B3 | cao |
| Motion preset Ken Burns | `hyperframes_bridge.py:165` | casewide `photo` có `reveal`/`zoom` tuỳ chọn, `casewide.js:185-193` | lệch | Giữ preset A; không đổi ảnh Long CL đã đăng | vừa |
| Biểu đồ CK | không có `race`/`waterfall`/`heat`/`stack` trong `VISUAL_TYPES` | `chart.js:8` | chỉ B | Giữ chart.js | thấp với A, vừa với casewide vì đè `brand` |
| Cảnh lab MIM | không có trong `VISUAL_TYPES` | `lab.js:16` | chỉ B | Giữ lab.js | thấp |
| Thiết bị Short Studio | 21 tên, `studio.py:37` | 13 tên `hf_*`, chỉ theme bud | lệch | Giữ đủ 21 của A; phần B là bản cắt | vừa |
| `longform.js` trong B | bản 4100 dòng là bản chạy của A | bản 1307 dòng, HTML chép nạp, builder MIM/CK/CL không nạp | lệch | Lấy A làm nguồn khi đụng style HTML; đừng render Long CL bằng file này | cao |

### 2. Cổng QA / lint

| Năng lực | A | B | Trạng thái | Giữ | Rủi ro gộp |
|---|---|---|---|---|---|
| QA bố cục trước render (`hyperframes check`, strict) | `hyperframes_bridge.py:1052-1064` gọi `hf_qa.py` khi `HF_QA=strict`; `--scenes` ở `hf_qa.py:23` và `1296` | Không import `hf_qa`. Short bud v2 gọi `check` riêng: `stier/build.py:838` và `937` | lệch | Giữ `hf_qa.py` làm một cổng; bật strict từng kênh | vừa |
| QA Studio `--qa` / `--strict` | `studio.py:327` chạy `lint` và `check`. `--strict` ở `studio.py:413` chặn luật đa dạng thiết bị, không phải `hf_qa` | `check_gate` chỉ `theme=="bud"` và `v2`, `build.py:838` | lệch | Giữ cả hai hành vi; ghi rõ cờ nào chặn cái gì | vừa |
| Sàn số cảnh / chữ nền trống | `hf_batch_render.py:731-742`: cảnh báo, không vào danh sách chặn | `floor.py:32-38` và `104`; chặn render thật `build_long.py:1198`, final `1264`, đăng `publish_long.py:117` | lệch | Giữ bản chặn của B cho CL. Bản A đang chỉ cảnh báo | cao |
| Sàn riêng MIM/CK (chữ nền trống theo giây) | không thấy ngưỡng 22% / 17s trong `hf_batch_render.py` | `floor.py:42-43` và `84` | chỉ B | Giữ trong floor.py | vừa |
| Đa dạng nhạc / look, Jaccard 0,35, cửa sổ 3 | `hf_music.py:1-10`, `WINDOW`/`MAX_OVERLAP` ở `36-37` | `variety.py:33-34`, `audit` `240`; chặn final `build_long.py:1354-1356` | lệch | Cùng ngưỡng, hai sổ. Giữ sổ đang nuôi video đã đăng của từng luồng | vừa |
| Lint kịch bản Long (re-hook, 90 giây, vòng mở) | `long_script_lint.py:720-735`, `--strict` ở dòng 19 | `scripts/long_gate.py:1`, `craft.py:22` (chỉ khi `craft: true`, `build_long.py:960-964`) | lệch | Giữ luật theo kênh; đừng một ngưỡng | cao |
| Lint câu / dấu / clip HDR | không thấy cổng đo con dấu và HDR trong `hf_qa.py` (cổng đó đo tràn, tương phản, bố cục) | `lint_html.py:217`, gọi ở `build_long.py:458` | chỉ B | Giữ lint_html cho casewide | thấp |
| Lint lời Short (hook, rehook, CTA) | `hook_lint.py` không có trên máy này | `script_lint.py:1`; chỉ chạy khi `theme=="bud"`, `build.py:759-765` | chỉ B | Giữ script_lint. Cổng hook A: chưa kiểm vì file không có | vừa |
| Cổng "approved" trước khi đăng | chưa thấy khoá `approved` trong các file upload A đã mở | `publish_long.py:118-124` | chỉ B | Giữ | thấp |
| Factcheck trước đăng Long | chưa kiểm một cổng tương đương trên A trong phiên này | `publish_long.py:121` gọi `factcheck_lint` | chỉ B | Giữ cho MIM/CK/CL. Cổng tương đương phía A: chưa kiểm | vừa |

### 3. TTS / giọng

| Năng lực | A | B | Trạng thái | Giữ | Rủi ro gộp |
|---|---|---|---|---|---|
| Mốc từng từ theo năng lượng TTS | `hf_align.py` (112 dòng) | `creator_v2/motion/hf_align.py` (112 dòng), giống hệt | trùng | Một file. B đang import bản trong `motion/` vì `build_long.py:34-40` nhét `motion/` lên `sys.path` | thấp |
| Giọng theo kênh | `hf_voice.py:138` `new_tts(channel)`; Short Studio đọc `tts` trong yaml, `studio.py:73-85` | Long: bảng trong code `build_long.py:110-116` (CL Anh Khôi, MIM Thanh Bình, CK Ngọc Huyền). Short: `themes.py:106-161` | lệch | Yaml là đích của issue; hôm nay bản chạy của B là bảng trong code | vừa |
| Vài take rồi chọn | Trong `hf_voice.py` có retry nhiệt (`hf_voice.py:145`). Bước `takes`/`pick` kiểu Long B: chưa thấy ở file A đã mở. `render_engine.py`: chưa kiểm | `build_long.py:284` `do_takes`, `318` `do_pick` | chỉ B | Giữ take/pick của B. `render_engine.py`: chưa kiểm | vừa |
| Master giọng CL (lọc "sẹt") | chưa thấy `VOICE_FX_CL` ở luồng A trong phần đã mở | `themes.py:100-108`; Long CL lấy cùng chuỗi, `build_long.py:109-110` | chỉ B | Giữ | thấp |

### 4. Nhạc / âm thanh

| Năng lực | A | B | Trạng thái | Giữ | Rủi ro gộp |
|---|---|---|---|---|---|
| Sổ nhạc chống trùng bài | `hf_music.py:21` sổ `output/cl_staging/long/bgm_ledger.json` | `variety.py:30` sổ `data/variety/ledger.json`; Short MIM/CK/BUD có sổ riêng trong `themes.py:19` và `138-155` | lệch | Giữ sổ đã ghi video đăng. Gộp sổ là việc dữ liệu, không gộp trong PR engine | vừa |
| Nhạc nền phát theo chương | `hf_foley.py:510` `music_bed` | `variety.py:186` `resolve_bgm`; mô tả ghi công ở `describe.py:13-23` | lệch | Giữ cách phát của từng luồng | vừa |
| SFX bám mốc cảnh | `hf_sfx.py:1` (palette chuông/mõ cho BUD/FS) | `stier/sfx.py:1`; Long gọi lại qua `sfx_long.py:1` và `16` | lệch | Giữ palette theo kênh. Một bảng âm chung sẽ làm CL nghe như BUD hoặc ngược lại | cao |
| Âm lặng khi câu hỏi | `hf_sfx.py:8` | `sfx.py:5` cảnh `question` lặng | lệch | Giữ hành vi cả hai | thấp |

### 5. Cấu hình kênh

| Năng lực | A | B | Trạng thái | Giữ | Rủi ro gộp |
|---|---|---|---|---|---|
| Hồ sơ yaml bud, fs, vsd | `library/channels/bud.yaml`, `fs.yaml`, `vsd.yaml`. Đọc bằng `library/tools/lib.py:91-94`. Không có `mim.yaml` / `ck.yaml` / `cl.yaml` | `creator_v2` không đọc `library/channels` | chỉ A | Giữ yaml làm chỗ chứa. B chưa đọc | vừa |
| mim, ck, cl trong yaml | Chỉ `_external.yaml`: kho lọc, không giọng, không theme. `assets.py:207-215` có đọc file này | Giọng, theme, brand, luật ảnh nằm trong `build_long.py:104-125` và `themes.py:106-161`. Luật chữ nằm trong `creator_v2/AGENTS.md` | lệch | Thêm yaml đầy đủ trước; code B vẫn là nguồn chạy cho đến PR chuyển người đọc | vừa |
| Theme màu / font Long | skin HTML + token studio, `hyperframes_bridge.py:273` | `variety.py:35` theme mặc định MIM=lab, CK=chart; look ở `variety.py:42` | lệch | Giữ look đã đăng | vừa |
| Theme Short | `studio.py` theme JSON trong `hyperframes_short/studio/themes/` | `themes.py` khoá `case`/`mim`/`ck`/`bud`, CSS `theme-mim.css`, `theme-ck.css`, `theme-bud.css` | lệch | Giữ CSS đã đăng của từng kênh | vừa |
| Bảng kênh upload (pacing, prefix) | không nằm trong yaml; upload A không đi qua `factory/` | `factory/channels.py:31-58` có FS, CL, BUD, MIM, CK | chỉ B | Giữ. File này cũng khai FS và BUD. Đổi pacing là đổi lịch vận hành | cao |

### 6. Ảnh / web

| Năng lực | A | B | Trạng thái | Giữ | Rủi ro gộp |
|---|---|---|---|---|---|
| Kho tài sản có manifest, kho_loc | `library/tools/assets.py:1`, `passes_kho_loc` `313` | không import | chỉ A | Dùng cho bài mới sau khi yaml MIM/CK/CL đủ. Không đổi ảnh sáu Long CL | vừa |
| Commons | `hf_commons.py:1` mặc định PD/CC0, `allow_by` là cờ | Long: PD/CC0/CC BY/CC BY-SA, trừ NC/ND, `build_long.py:13` và `68`; MIM/CK thêm `no_sa`, `122-125`. Short research: PD/CC0, `stier/research.py:8` | lệch | Giữ bộ lọc theo kênh. Một hàm lọc chung phải nhận luật kênh | cao |
| Openverse, bảo tàng, NASA, IA | `hf_openverse.py:1`, `hf_pdvideo.py:1` | `motion/long/media_search.py:1` (Openverse, Wellcome, Artic, Europeana, NASA, Smithsonian) | lệch | Giữ cả hai cho đến khi một bài thử ra cùng giấy phép | vừa |
| Ảnh AI và gỡ dấu | `library/tools/ai_image_batch.py:1` | `webauto/flow.py:166` `--strip-mark`; Long MIM/CK bỏ nhãn `illus` trên ảnh AI, `build_long.py:160-164` | lệch | Giữ luật nhãn đã chốt (credit false, không in "ẢNH MINH HỌA", không nhắc AI trong mô tả) | vừa |
| Stock Pexels / Pixabay | `stock_image.py:40` | Short/Long B gắn clip Pexels qua trường cảnh (`AGENTS.md` trong creator_v2, mục clip). Module tải: `stier` có footage; chưa đối chiếu từng hàm với `stock_image.py` | lệch | Giữ đường đang chạy. Hàm tải của B chưa đối chiếu hết với `stock_image.py` | vừa |
| webauto | không có thư mục `webauto` ở gốc repo này | `creator_v2/webauto/` (`flow.py`, `cli.py:1`) | chỉ B | Một bản = bản này. Bản repo V2 cũ: chưa kiểm | thấp trong repo này |
| Chọn cảnh / preset từ hồ sơ | `library/tools/scene_picker.py`, `motion_picker.py:1` | không import | chỉ A | Nối sau, không bật trên Long CL đã có cảnh tay | vừa |

### 7. Packaging / upload

| Năng lực | A | B | Trạng thái | Giữ | Rủi ro gộp |
|---|---|---|---|---|---|
| Upload private + publishAt | `youtube_upload.py:143-146`; Long gọi từ `long_batch_runner.py:40`; Short từ `short_upload.py:14` | `factory/publish.py:26-28`; mọi ghi đi qua `factory/channel.py`. Long: `publish_long.py:1` và `33`. Short: `upload_one.py:33`, `enqueue.py:1` | lệch | Không gộp ở B2. Hai sổ chống trùng khác nhau | cao |
| Chống trùng file / thời lượng | `duplicate_check.py:250`, gọi ở `long_batch_runner.py:43` | khoá `(channel, slug)` trong `factory/channel.py:69` | lệch | Giữ cả hai lớp | cao |
| Chống trùng chủ đề / tiêu đề | chưa thấy bigram tiêu đề trong đường `youtube_upload.py` đã mở | `factory/lines/novelty.py:1`; `enqueue.py:7` bỏ tiêu đề trùng | chỉ B | Giữ novelty cho B. Bigram tiêu đề phía A: chưa kiểm hết | vừa |
| Mô tả + ghi công | `hf_batch_render.py:903` gom `media_credits` | `describe.py:1` (ảnh thật sự hiện, nhạc Kevin MacLeod) | lệch | Giữ mẫu mô tả đang đăng của từng kênh | vừa |
| Hàng đợi giờ đăng | lịch trong runner A (`long_batch_runner.py`, `short_batch_runner.py`) | `enqueue.py`, `enqueue_mim.py:3`, `enqueue_ck.py:3`, `upload_one.py:3` | lệch | Không chạy các lệnh này trong issue gộp | cao |
| Giãn nhịp upload | chưa thấy pacing kiểu `factory/channels.py` trên `youtube_upload.py` trong phần đã đọc (`youtube_upload.py` có `pacing_hold_until` ở dòng 93) | `factory/channels.py:18-29` | lệch | Giữ số đang chạy. Đổi số là đổi lịch | cao |

## Cặp file trùng tên

### Cùng đường tương đối `hyperframes_short/` và `creator_v2/motion/hf/`

Giống hệt (git diff --stat rỗng, exit 0): `AGENTS.md`, `CLAUDE.md`, `compositions/base.css`, `compositions/casemap.html`, `compositions/dossier.html`, `compositions/inkwash_wide.html`, `compositions/interrogation.html`, `compositions/laban_wide.html`, `compositions/night.html`, `compositions/vhs.html`, `compositions/wide.css`, `index.html`, `meta.json`, `package.json`.

Khác:

| File | git diff --stat (A → B) |
|---|---|
| `.gitignore` | khác (không phải engine) |
| `compositions/dustbeam.html` | 1 insertion, 3 deletions |
| `compositions/engine.js` | 8 insertions, 120 deletions |
| `compositions/hongchi.html` | 1 insertion, 8 deletions |
| `compositions/inkwash.html` | 2 insertions, 8 deletions |
| `compositions/inkwash_long.html` | 4 insertions, 12 deletions |
| `compositions/laban.html` | 1 insertion, 6 deletions |
| `compositions/laban_long.html` | 3 insertions, 8 deletions |
| `compositions/lightfield.html` | 1 insertion, 3 deletions |
| `compositions/longform.css` | 2 insertions, 647 deletions |
| `compositions/longform.js` | 55 insertions, 2848 deletions |
| `compositions/oilpaint.html` | 1 insertion, 3 deletions |
| `compositions/shortform.css` | 27 deletions |
| `compositions/silence.html` | 1 insertion, 3 deletions |
| `hyperframes.json` | 1 insertion, 38 deletions |

Các HTML khác nhau ít dòng: chưa đọc diff từng hunk. Chưa kết luận hunk đó là gì.

### `hf_*.py`

| Cặp | Kết quả |
|---|---|
| `hf_align.py` và `creator_v2/motion/hf_align.py` | giống hệt, 112 dòng, exit 0 |
| `hf_geo.py` (432 dòng) và `creator_v2/motion/hf_geo.py` (135 dòng) | 3 insertions, 300 deletions. Bản B không có lớp đảo |
| Các `hf_*.py` khác ở gốc | không có bản luồng chạy trong `creator_v2` (chỉ thấy dưới `.ref/`) |

B dùng bản trong `creator_v2/motion/` (`build_long.py:40-41`, `stier/build.py:39-40`). A dùng bản ở gốc.

## Thứ tự gộp đề xuất cho B2

Mỗi mục một PR. Chưa đụng engine (đó là B3) và chưa đụng upload (hai sổ, đụng lịch).

1. webauto. Trong repo này chỉ có `creator_v2/webauto`. PR ghi một lối gọi, không nhân bản. Bản ở repo V2 cũ phải đối chiếu trên máy có thư mục đó.
2. Thêm `library/channels/mim.yaml`, `ck.yaml`, `cl.yaml` từ `_external.yaml` cộng giọng/theme đang nằm trong `build_long.py:110-116` và `themes.py:106-161`. PR chỉ thêm file. Code B chưa chuyển sang đọc yaml.
3. `hf_align.py` đã trùng: một PR xoá đường import đôi, trỏ cả hai luồng vào một file, có test mốc từ. Không đổi số.
4. `hf_geo.py`: đưa lớp đảo của bản gốc sang module dùng chung, test một bbox có Việt Nam. Renderer `casewide.js:469` giữ nguyên ở PR này.
5. Một cổng QA cảnh báo: `hf_qa.py --scenes` gọi được từ short bud, chế độ cảnh báo. Chưa bật strict lên MIM/CK/CL, chưa thay `floor.py`.
6. `library/tools/assets.py` cho một bài MIM mới, sau khi yaml có `kho_loc`. `build_long.fetch_img` của Long đã đăng giữ nguyên trong PR này.

Chưa xếp vào B2: gộp `longform.js`, gộp casewide với visual A, gộp `floor.py` với sàn cảnh báo của `hf_batch_render.py`, gộp sổ nhạc, gộp `youtube_upload.py` với `factory/channel.py`.

## Điểm cần chủ kênh quyết

1. Duyệt bảng B1 và thứ tự sáu PR trên trước khi làm B2.
2. Duyệt `kho_loc` MIM/CK/CL trong `_external.yaml` và bản yaml đầy đủ (giọng, theme, luật ảnh, luật CK).
3. Trong lúc gộp, MIM/CK/CL tiếp tục dựng bằng `creator_v2` hay tạm dừng. Issue ghi ngày 05/11 đang tạm dừng để chờ workflow mới, và #140 chỉ áp BUD/FS.
4. Lớp Hoàng Sa/Trường Sa có đi theo mọi bản đồ sau gộp hay chỉ bài BUD/FS. Hôm nay chỉ bản `hf_geo.py` gốc có lớp này.
5. Hai đường upload có gộp không, và gộp ở bước nào. Đề xuất của phiên này: không phải B2.
6. `hook_lint.py` có còn là cổng BUD/FS không. File không có trên máy này và không có trong git theo `tests/test_hook_lint.py:12`.

## Chưa kiểm

- Nội dung `hook_lint.py` và mọi `build_*.py` trong `output/cl_staging` (không có trên máy này).
- Bản `webauto` trong `Youtube_Creator_V2/`.
- `render_engine.py` có bước chọn take hay không.
- Từng hunk của các HTML lệch vài dòng.
- Cây `creator_v2/.ref/` có được runtime nạp hay không.
- Mọi khoá trong yaml kênh (`luat_title`, packaging) đã có người đọc hay chưa. Đã thấy người đọc: `lib.py` trả cả hồ sơ; `assets.py` đọc `kho_loc`, `tts`, `sound`; `studio.py:73` đọc `tts`; `hf_sound.py:64` đọc `sound`.
