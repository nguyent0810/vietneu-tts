# Báo cáo nghiên cứu: Animation Style Catalog (GH-258)

- Ticket: issue [#258](https://github.com/nguyent0810/vietneu-tts/issues/258), brief `docs/pm/tickets/GH-258-grok.md`.
- Ngày: 2026-11-12. Thợ: Grok. Không sửa code production, không commit, không đăng, không đổi lịch.
- Phạm vi: bước 1 (đọc repo), bước 2 (bảng style), bước 4 (so kiến trúc). **Bỏ bước 3** — không render, không cài Playwright/Chrome.
- Clone: `%TEMP%\anim_catalog` (ngoài `vietneu-main`). Commit khảo sát: `09e451d8b64ec85c1ec035fd39e00725c1ed5593` (2026-09-27, `README: ızgara galeri…`).
- GitHub API `license`: `null` (`gh api repos/yasinozmeen/animasyon-stil-katalogu`).

Bàn giao cùng thư mục: `style_matrix.csv`, `benchmark.md`, `integration_proposal.md`.

## 1. Mục tiêu

Trả lời issue #258: các kỹ thuật trong [yasinozmeen/animasyon-stil-katalogu](https://github.com/yasinozmeen/animasyon-stil-katalogu) có giúp nâng chất hình, giảm slideshow, và dùng lại được với HyperFrames (`engine.js` / `longform.js`), `hyperframes_bridge.py`, FFmpeg, VieNeu TTS hay không.

## 2. Cách làm

- Đếm thư mục thật trong `stiller/`, không tin README.
- Đọc `README.md`, `BRIEF.md`, `render_ornek.mjs`, `birlestir.sh`, `common.js`, từng `anim.html`.
- Đối chiếu kho xưởng: skill `motion-library`, `creator_v2/motion/hf/compositions/longform.js`, `casewide.js`, `motion/long/README.md`, `longform_styles.js`, `hf_styles.js`.
- Mọi nhận định quan trọng dẫn path/dòng hoặc SHA.

## 3. Kiểm kê style

`stiller/` có **đúng 20** thư mục, khớp bảng `birlestir.sh` dòng 26–45 và lưới README:

| # | slug | Nhóm (birlestir.sh) | `anim.html` | MP4 mẫu | GIF | `common.js` |
|---:|---|---|---:|---|---|---|
| 1 | kurzgesagt | Düz grafik | 343 dòng | có | có | không |
| 2 | izometrik | Düz grafik | 362 | có | có | không |
| 3 | bauhaus | Düz grafik | 209 | có | có | không |
| 4 | memphis | Düz grafik | 295 | có | có | không |
| 5 | beyaz-tahta | El çizimi | 217 | có | có | có |
| 6 | kara-tahta | El çizimi | 180 | có | có | có |
| 7 | blueprint | El çizimi | 212 | có | có | có |
| 8 | tek-cizgi | El çizimi | 123 | có | có | có |
| 9 | kagit-kesik | Doku ve zanaat | 333 | có | có | không |
| 10 | karakalem | Doku ve zanaat | 292 | có | có | không |
| 11 | linocut | Doku ve zanaat | 269 | có | có | không |
| 12 | kil | Doku ve zanaat | 280 | có | có | không |
| 13 | retro-70ler | Nostalji | 365 | có | có | không |
| 14 | piksel | Nostalji | 502 | có | có | không |
| 15 | belgesel-16mm | Nostalji | 301 | có | có | không |
| 16 | cizgi-roman | Nostalji | 384 | có | có | không |
| 17 | terminal | Teknik | 282 | có | có | không |
| 18 | hud | Teknik | 308 | có | có | không |
| 19 | veri | Teknik | 185 | có | có | không |
| 20 | kinetik-tipografi | Deneysel | 160 | có | có | không |

Không có style thứ 21. README dòng 66–67 nói Vox / màu nước / cyberpunk **không** nằm trong repo.

Mỗi style là một klip vitrin 9–10 giây, nội dung tiếng Thổ cứng (ví dụ `tek-cizgi/anim.html` dòng 114: `bir çizgi, bir söz.`; `linocut` dòng 9: `SÖZ / SENDE!`). **Không file JSON đầu vào.** Không `JSON.parse`, không `fetch`.

## 4. Kiến trúc catalog

### 4.1 Công nghệ

- Toàn bộ 20 style: **HTML5 Canvas 2D** 1920×1080. Không SVG, không GSAP, không WebGL, không `package.json`.
- `izometrik` chiếu isometric bằng toán trên Canvas (`anim.html` dòng 39–47), không Three.js (từ “three” trong phân tích tự động là dương tính giả).
- Bốn style vẽ nét dùng `common.js` (`beyaz-tahta`, `kara-tahta`, `blueprint`, `tek-cizgi`): lớp `Path` Bézier/Catmull-Rom + `trace(ctx, s0, s1)` (`common.js` 23–52), PRNG LCG (`common.js` 12).
- Texture đắt (giấy, hạt, mask mực) nướng một lần vào canvas ẩn — `BRIEF.md` dòng 19.

### 4.2 Thời gian và xuất video

Hợp đồng `BRIEF.md` dòng 16–17: `window.draw({t})` trả JPEG base64; `window.ready` chờ font/texture.

Hai dạng chữ ký, cùng nghĩa:

- `window.draw = ({ t }) => { render(t); return cv.toDataURL('image/jpeg', 0.92).split(',')[1]; }` (`tek-cizgi/anim.html` 121).
- `window.draw = function (job) { renderFrame(job.t); … job.q || 0.92 }` (`linocut/anim.html` 264).

`render_ornek.mjs` dòng 29–31: `page.evaluate(j => window.draw(j), jobs[i])` với `jobs[i] = { t: n/30, file }`. Seek theo `t` giây, không cần chạy khung trước. Đó là điểm gần HyperFrames.

Xuất: Playwright + `chrome-headless-shell` → JPEG → ffmpeg H.264 CRF 18 30 fps (`build.sh` dòng 5–6, `yap.sh` dòng 8–9). Tiếng: `sfx.py` / `synth.py` hoặc `anullsrc` (`yap.sh` dòng 7). Không file WAV có sẵn trong git.

`birlestir.sh` ghép 20 clip + thẻ tiêu đề PIL/Georgia macOS thành `katalog/katalog_1080p.mp4`.

### 4.3 Headless macOS và Oracle Linux ARM

`render_ornek.mjs` dòng 16–21:

```javascript
const base = path.join(process.env.HOME, 'Library/Caches/ms-playwright');
// …
path.join(base, d, 'chrome-headless-shell-mac-arm64/chrome-headless-shell')
```

- macOS arm64: chạy được nếu Playwright global đã tải shell.
- Oracle Linux ARM: **không chạy** nguyên trạng (sai OS path, sai tên binary, `birlestir.sh` font `/System/Library/Fonts/Supplemental/Georgia.ttf`).
- Playwright lấy từ `npm root -g` + `@playwright/test` (`render_ornek.mjs` dòng 7). Không khai trong repo.

Xưởng đã có Chrome headless qua HyperFrames (`motion/long/README.md` đoạn `puppeteer-core` / `~/.cache/puppeteer`). Không cần script catalog.

### 4.4 Tất định

Vẽ là hàm của `t` (lerp/seg/ease). Hạt giấy đa số `rng(seed)`.

Ngoại lệ `Math.random` lúc nướng (seek trong một session ổn, reload khác hạt):

- `veri/anim.html` 177
- `terminal/anim.html` 220
- `kinetik-tipografi/anim.html` 135

`engine.js` dòng 8–10 cấm `Math.random` / `Date.now`. Chép ba style này phá luật xưởng.

`linocut/anim.html` 77: `q = t => Math.floor(t * 12) / 12` — mực sôi 12 fps, tua an toàn.

## 5. License

- GitHub API: `license: null`. Thư mục gốc không có `LICENSE` / `COPYING` / `UNLICENSE`.
- `README.md` dòng 78: chỉ font Google Fonts **SIL Open Font License**, nằm trong `stiller/<slug>/fonts/`.
- Không câu nào cấp MIT/Apache/BSD cho HTML/JS.
- Công ước Berne: không giấy phép = giữ mọi quyền.

**Được:** xem README, BRIEF, phim mẫu; mượn ý tưởng phong cách; tự viết lại; dùng font Google độc lập theo OFL.

**Không được:** chép `anim.html`, `common.js`, `render.mjs`, path/hằng màu/asset.

Phương án A (chép code) loại. Font OFL không cứu mã nguồn.

## 6. Chi phí CPU/RAM/thời gian

Xem `benchmark.md`. Tóm tắt: **ước lượng, chưa đo.** Điều kiện GO “10 s < 2× realtime trên Mac” chưa kiểm. Render Long xưởng từng được ghi ~2,7× realtime (`motion/long/README.md` 165) — số cả video, không phải catalog.

## 7. Tương thích HyperFrames, FFmpeg, TTS

Hai cửa Long trong monorepo (đã ghi ở `docs/codex/long-rules.md` và ticket GH-159):

| Cửa | Engine | Kênh |
|---|---|---|
| `hf_batch_render` + `hyperframes_bridge.py` | `engine.js` + `longform.js` | BUD, FS |
| `motion/long/build_long.py` | `casewide.js` (không phải `longform.js`) | CL, MIM, CK |

Điểm khớp catalog:

- Catalog: `draw(t)` thuần. Xưởng: `gsap.timeline({ paused: true })` (`engine.js` 274, `casewide.js` 36), `tl.seek` (`engine.js` 410). `longform.js` 1298 đã có mẫu đồng hồ canvas: `tl.to(clock, { t: …, ease: "none", onUpdate: () => S.draw(clock.t) })`.
- TTS: catalog gắn mốc giây cứng (`tek-cizgi` `TL.end = 10` dòng 96; `blueprint` `acts.push({ t0, t1 })` dòng 28–31). Xưởng có `when(ctx, step)` (`longform.js` 38–47) và mốc lời đã quy về giây (`casewide.js` 1–3). Viết lại: `steps[].at`/`word` → `when()`. Không nhét VieNeu vào `anim.html`.
- FFmpeg: catalog tự ghép JPEG. Xưởng đã mux giọng + nhạc + CRF trong `build_long.py` / HyperFrames. Thêm cảnh DOM/SVG/canvas trong composition là đủ; không thêm renderer JPEG.
- JSON: catalog không nhận JSON. Kho xưởng nhận spec/`visuals` JSON. Đây là lý do B rẻ hơn A: bọc `draw(t)` rồi vẫn phải bóc nội dung Thổ.

## 8. Đối chiếu kho cảnh sẵn có

### 8.1 `longform.js` (BUD/FS)

`creator_v2/motion/hf/compositions/longform.js` @ `8805e9a2a2b9aa1d0c167d596391f16a2bf7c737` (~1307 dòng). Visuals: `wheel`, `elements`, `years`, `list`, `timeline`, `compare`, `stat`, `quote`, `map`, `word`, `illus`, `endcard` (gán từ dòng 246–1257). Chữ theo nhịp nằm ở `word` + preset trong skill `motion-library`.

Bản `creator_v2` này không khai `doc`/`photo`/`clock`/`ask` bằng `visuals.X =` (skill mô tả chúng ở bản `hyperframes_short` đầy đủ hơn). Không làm suy giảm kết luận trùng kinetic/dataviz.

### 8.2 `casewide.js` (CL/MIM/CK)

`casewide.js` @ `fb4f25dc9dd8afc44d203b5c6df4679ec2088371`. `B.<type>` gồm chapter, broll, photo, pano, print, file, kinetic, slam, brand, endcard, question, counter, bars, myth, source, units, timeline, map, quote, org, ledger, split, date, cards, evidence, seismo, saint, paper, pizzini, dots, board, memorial, calendar, sticker, sketch (dòng 126–1430). `B[s.type]` dòng 1460.

Thẻ `file` style `terminal` (dòng 478) và `spec_sheet` kiểu blueprint (484). `film: true` hạt 12 fps (dòng 80).

Chữ động: `motion/hf/assets/engine/beat.js` (pop/rise/blur/slice/drop/marker/redact/stamp/tape/type/scramble…).

### 8.3 motion-library (234 mẫu prompt-motion)

`.claude/skills/motion-library/references/prompt_motion/`: 234 mẫu; 23 hợp FS/BUD mức 2–3. Hàng đợi cảnh MỚI ưu tiên `shadow_theatre` (rối bóng giấy cắt, mẫu x4b47x-9cc84f) và `paint_over` (`quy_uoc.md` 161–168). Luật 4 cấm HUD góc, hạt bung, lens flare, neon (`quy_uoc.md` 26–29).

### 8.4 Bộ #258 đã có trong repo

PR `#293` `2294923784ca5a45c4a8931ba670a5904adfa9ea` thêm clean-room:

`woodcut`, `papercut`, `oneline`, `film16`, `blueprint`, `pencil` trong `longform_styles.js` (đăng ký dòng 119–536, danh sách dòng 604). `hf_styles.js` móc vào casewide. `scene_params.py` 84–89. `build_long.py` 734–735 chỉ nhúng khi chương có type đó.

Đây là phương án B đã triển khai cho sáu ý tưởng P0/P1. Spike này không mở lại ticket viết chúng.

### 8.5 Trùng và khoảng trống

| Catalog | Kho xưởng | Việc |
|---|---|---|
| kinetik-tipografi | beat.js + word/kinetic/slam | không thêm |
| veri | bars, ledger, counter, stat, compare, chart.js | không thêm |
| terminal | idcard `terminal`, look `mim-crt` | không thêm |
| hud | cấm quy_uoc luật 4 | không thêm |
| beyaz-tahta / kara-tahta | sketch | giá trị thấp |
| linocut / kagit-kesik / tek-cizgi / blueprint / belgesel-16mm / karakalem | woodcut / papercut / oneline / blueprint / film16 / pencil | **đã có** (#293) |
| kurzgesagt, izometrik | chưa có explainer phẳng / isometric | khoảng trống MIM, đợt sau nếu PO muốn |
| memphis, piksel, kil, retro-70ler, cizgi-roman | không | lệch thương hiệu |

`kagit-kesik` gần hàng đợi `shadow_theatre` (rối bóng) nhưng khác: diorama nhiều lớp có màu, không phải bóng đen trên màn. `papercut` đã lấp một phần; `shadow_theatre` vẫn có thể là cảnh riêng (chỉ bóng).

## 9. Phù hợp kênh

Luật: FS huyền bí (`quy_uoc.md` 9: nền chàm, nhấn vàng); BUD trang nghiêm, không biếm họa Đức Phật (`motion-library` SKILL, `long-rules.md` ảnh AI). CK/MIM hiện đại, số liệu có nguồn. Kênh biểu đồ = CK + `chart.js`.

| Kênh | P0/P1 hợp | Tránh |
|---|---|---|
| BUD | linocut, kagit-kesik, tek-cizgi (đã = woodcut/papercut/oneline) | memphis, kil, cizgi-roman, piksel, hud, retro |
| FS | linocut, kagit-kesik, tek-cizgi, blueprint | memphis, kil, hud, piksel |
| CL | belgesel-16mm, karakalem, linocut | memphis, piksel, kil |
| MIM | kurzgesagt, izometrik, blueprint | kil, memphis (ồn) |
| CK | blueprint, veri (đã có bars), izometrik | kil, cizgi-roman |
| Biểu đồ | veri (đã có), blueprint dạng `bars` | hud |

P0 độc lập từ catalog (trước khi trừ #293): **linocut, kagit-kesik, tek-cizgi** — ≥2 style, ≥1 kênh đang chạy.

P1: blueprint, belgesel-16mm, karakalem, kurzgesagt, izometrik.

P2: còn lại.

Chấm chi tiết: `style_matrix.csv`.

## 10. GO / NO-GO

Issue #258 cần đủ 4 điều kiện GO:

1. ≥2 P0 hợp kênh đang chạy — **đạt** (ba P0 trên).
2. Làm lại B hoặc C không đụng license — **đạt B**. A loại vì không license. C loại nếu giữ HTML.
3. 10 s < 2× realtime trên Mac — **chưa đo**.
4. Tua khung tất định, render theo chương — **đạt trên engine xưởng**; catalog `draw(t)` seek được nhưng xuất mac-only.

NO-GO nếu chỉ còn cách chép code, hoặc style trùng hết, hoặc render không tất định/quá nặng. Không rơi vào nhánh “chỉ còn A”: B khả thi. Một phần style trùng kho (kinetic/veri/terminal) nhưng P0 thì không trùng **trước** #293; **sau** #293 thì P0 đã có bản clean-room.

**Kết luận: GO có điều kiện, phương án B.** Không GO vô điều kiện vì thiếu số đo hiệu năng. Không mở ticket triển khai mới cho sáu style đã vào `#293`. Đợt sau (PO duyệt riêng): đo `woodcut`/`papercut`/`oneline` trên Mac; tuỳ chọn explainer MIM (`kurzgesagt`/`izometrik`) viết mới.

## 11. File dẫn chính

| Nguồn | SHA / chỗ |
|---|---|
| Catalog clone | `09e451d8b64ec85c1ec035fd39e00725c1ed5593` |
| GitHub license | API `null` |
| Font OFL | `README.md:78` |
| Hợp đồng draw(t) | `BRIEF.md:16-19` |
| Chrome mac-arm64 | `render_ornek.mjs:16-21` |
| 20 slug | `birlestir.sh:26-45` |
| Path/trace | `stiller/tek-cizgi/common.js:12,23-52` |
| 12 fps linocut | `stiller/linocut/anim.html:77,264` |
| acts[] blueprint | `stiller/blueprint/anim.html:27-31` |
| Math.random | `veri/anim.html:177`, `terminal/anim.html:220`, `kinetik-tipografi/anim.html:135` |
| GSAP paused | `engine.js:274`, `casewide.js:36` |
| when() TTS | `longform.js:38-47` |
| Cấm Math.random | `engine.js:8-10` |
| Render 2,7× | `motion/long/README.md:165` |
| Bộ style #258 | `longform_styles.js:604`, PR `#293` `2294923784ca5a45c4a8931ba670a5904adfa9ea` |
| HUD cấm | `motion-library/references/prompt_motion/quy_uoc.md:26-29` |
