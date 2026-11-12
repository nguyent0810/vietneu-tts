# Benchmark Animation Style Catalog — ước lượng, chưa đo

- Ticket: GH-258, bước 3 **bỏ** theo brief `docs/pm/tickets/GH-258-grok.md`.
- Không cài Node package, Playwright hay Chrome. Không chạy `render_ornek.mjs`, `build.sh`, `yap.sh`.
- Mọi số thời gian, CPU, RAM dưới đây là **ước lượng từ mã**, không phải số đo máy. Không bịa miligiây hay MB đã chạy.

Repo khảo sát: clone `%TEMP%\anim_catalog`, commit `09e451d8b64ec85c1ec035fd39e00725c1ed5593`.

## 1. Vì sao chưa đo

Brief Grok cấm bước 3. Máy này không được phép cài Playwright hay `chrome-headless-shell`. Script gốc cũng không chạy được nguyên trạng trên Windows/Oracle Linux ARM vì đường Chrome gắn cứng macOS (mục 3).

## 2. Chuỗi xuất video trong catalog

1. Node `render.mjs` / `render_ornek.mjs` mở Playwright, viewport 1920×1080.
2. `page.goto(file://…/anim.html)`, chờ `window.ready` (font + nướng canvas ẩn).
3. Mỗi khung: `window.draw({t: n/30})` trả JPEG base64 (`toDataURL('image/jpeg', 0.92)`), ghi `00000.jpg`…
4. `ffmpeg` nối JPEG 30 fps, H.264 CRF 18, yuv420p, AAC (hoặc `anullsrc` nếu không có tiếng).

Dẫn:

- Hợp đồng vẽ: `BRIEF.md` dòng 16–19.
- Vòng worker: `render_ornek.mjs` dòng 1, 8–15, 23–32. Mặc định `workers=4`; BRIEF dòng 18 nói tối đa 2 trang song song.
- Chrome: `render_ornek.mjs` dòng 16–21 tìm `~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell`.
- Ghép catalog: `birlestir.sh` dòng 20–23, 48–49.
- Font: `README.md` dòng 78 (SIL OFL). Không có `package.json` trong repo catalog.

## 3. Chi phí theo giai đoạn (ước lượng)

### 3.1 Khởi tạo (`window.ready`) — một lần mỗi trang

Nặng nhất là nướng texture full-HD:

| Style | Việc nướng | Ước lượng |
|---|---|---|
| `linocut` | `buildPaper` + 4 mask `valueNoise` full 1920×1080 (`anim.html` 35–57, 265–266) | RAM vừa (5 canvas 1080p), CPU cao lúc mở trang |
| `kagit-kesik` | texture 768² + nhiều lớp `makeLayer` blur (`anim.html` 29–71) | RAM cao (mỗi lớp 1 canvas + 1 bóng) |
| `karakalem` | giấy + răng giấy `getImageData` full HD (`anim.html` 29–46) | CPU cao lúc mở |
| `belgesel-16mm` | `buildGrain(seed)` 960×540 + studio card (`anim.html` 140–144) | vừa |
| `kil` | nền + fingerprint 512² (`anim.html` 29–39) | vừa |
| `tek-cizgi` | giấy 1 canvas + resample 3 spline 2600 điểm (`anim.html` 13–73) | thấp–vừa |
| `blueprint` / bảng | giấy 1 canvas + `acts[]` | thấp |
| `veri` / `kinetik-tipografi` / `terminal` | hạt giấy `Math.random` lúc `prep` | thấp, **không tất định giữa các lần mở trang** |

### 3.2 Mỗi khung 1920×1080 @ 30 fps

Chi phí chung mọi style: `canvas.toDataURL('image/jpeg', 0.92)` — mã hóa JPEG full HD mỗi khung, rồi marshal base64 qua Playwright. Đây là phần đắt ổn định, không phụ thuộc độ đẹp của nét vẽ.

Thêm trên mỗi khung:

- **Thấp:** `bauhaus`, `memphis`, `veri`, `kinetik-tipografi`, `terminal` (vẽ primitive / chữ). `tek-cizgi` sau khi spline đã resample: vòng `strokePts` ~2600/6 đoạn.
- **Vừa:** `linocut` lượng tử 12 fps (`q = floor(t*12)/12`, dòng 77) nên 30 fps lặp khung; vẫn `destination-out` + 4 mask. `blueprint` duyệt `acts[]`. `kurzgesagt` / `izometrik` / `hud` nhiều `drawImage` canvas ẩn.
- **Cao:** `kagit-kesik` (nhiều `drawImage` lớp + bóng lệch theo ánh sáng). `belgesel-16mm` (jitter + grain + xước). `karakalem` (lớp chì). `kil` (12 fps + bump). `cizgi-roman` (halftone).

Clip mẫu trên đĩa (kích thước file có sẵn, **không** phải số đo render):

| Style | MP4 (KB) | GIF xem trước (KB) | `anim.html` (dòng) |
|---|---:|---:|---:|
| tek-cizgi | 377 | 281 | 123 |
| veri | 286 | 889 | 185 |
| piksel | 409 | 546 | 502 |
| kara-tahta | 415 | 1686 | 180 |
| beyaz-tahta | 426 | 1698 | 217 |
| hud | 434 | 413 | 308 |
| kinetik-tipografi | 502 | 1364 | 160 |
| bauhaus | 513 | 396 | 209 |
| kil | 532 | 1691 | 280 |
| terminal | 547 | 1675 | 282 |
| cizgi-roman | 5730 | 3489 | 384 |
| kagit-kesik | 629 | 597 | 333 |
| blueprint | 697 | 2558 | 212 |
| izometrik | 713 | 779 | 362 |
| karakalem | 732 | 1985 | 292 |
| kurzgesagt | 1065 | 976 | 343 |
| memphis | 1487 | 1028 | 295 |
| linocut | 2053 | 1905 | 269 |
| retro-70ler | 2162 | 2300 | 365 |
| belgesel-16mm | 7330 | 3702 | 301 |

`belgesel-16mm.mp4` ~7,3 MB / ~10 s là tín hiệu bitrate hạt phim cao, khớp ước lượng “cao” ở trên. Không suy ra thời gian encode.

### 3.3 So với pipeline xưởng

`motion/long/README.md` dòng 165 ghi tốc độ render Long khoảng **2,7 lần thời lượng thực** (video 34 phút ~ 90 phút) trên máy đã đo trước đây. Đó là số của **cả chương HyperFrames + FFmpeg**, không phải của catalog ngoài.

Điều kiện GO của issue #258: “mỗi cảnh 10 giây render dưới 2× thời gian thực trên Mac”. **Chưa kiểm chứng.** Không khẳng định đạt hay không đạt.

Suy luận (không phải đo):

- HyperFrames cũng tua GSAP rồi chụp khung 1920×1080 qua Chrome (`engine.js` dòng 274 `gsap.timeline({ paused: true })`; `long/README.md` đoạn Chrome headless). Cùng họ chi phí I/O khung.
- Catalog còn **mã hóa JPEG trong page** rồi gửi base64. HyperFrames thường chụp PNG/raw từ CDP, tránh `toDataURL` trong page. Nếu giữ nguyên `render_ornek.mjs`, mỗi cảnh 10 s (300 khung) sẽ **nặng hơn** một cảnh DOM/SVG cùng độ phân giải.
- Phương án B (viết lại trong GSAP như `longform_styles.js`) đi đường chụp khung sẵn có, không thêm JPEG trong page. Ước lượng cùng lớp với cảnh `sketch` / `kinetic` hiện tại, tức nằm trong 2,7× của cả video, nhưng **không** chứng minh một cảnh 10 s < 2×.

## 4. CPU / RAM / đĩa — ước lượng

- **CPU:** 1 tiến trình Chrome headless + 2–4 tab (`workers`). BRIEF dòng 18 khuyên 2 tab vì “cùng lúc 4 agent khác cũng render”. Ước lượng: 1–2 nhân bận khi vẽ, cộng ffmpeg khi ghép.
- **RAM:** viewport 1920×1080 + N canvas ẩn. Style nhiều lớp (`kagit-kesik`, `linocut` 5+ canvas 1080p ≈ vài chục MB pixel chưa kể Chrome). Không có số RSS.
- **Đĩa tạm:** 300 JPEG 1080p chất lượng 0.92. Ước lượng thô 100–400 KB/khung → 30–120 MB/`_frames` rồi xóa (`yap.sh` dòng 10, `build.sh` dòng 7). Không đo.
- **Thời gian wall:** không có.

## 5. Headless macOS và Oracle Linux ARM

| Môi trường | Catalog nguyên trạng | Pipeline xưởng |
|---|---|---|
| macOS arm64 | Có thể, nếu đã `npm i -g @playwright/test` và Playwright đã tải `chrome-headless-shell-mac-arm64`. Đường dẫn gắn cứng. | Đã dùng Puppeteer/Chrome trong cache (`long/README.md` đoạn render). |
| Oracle Linux ARM | **Không chạy.** `render_ornek.mjs` dòng 16–21 chỉ tìm `Library/Caches` + `chrome-headless-shell-mac-arm64`. Không có nhánh `linux-arm64`. `birlestir.sh` / `build.sh` là bash/zsh, font tiêu đề Georgia của macOS (`birlestir.sh` dòng 4, 14–15). | Xưởng không phụ thuộc script này. |
| Windows (máy viết báo cáo) | Không chạy script catalog. | Không dùng cho bước này. |

Kết luận hạ tầng: **đừng** đưa `render_ornek.mjs` vào workflow. Tua theo khung thì tái sử dụng HyperFrames.

## 6. Tất định

- 17/20 style dùng PRNG có hạt (LCG `common.js` dòng 12, hoặc `rng` trong `anim.html`) cho giấy/nét. Cùng `t` sau cùng một lần `ready` → cùng khung.
- Ba style nướng hạt bằng `Math.random`: `veri/anim.html` dòng 177, `terminal/anim.html` dòng 220, `kinetik-tipografi/anim.html` dòng 135. Seek trong một lần mở trang ổn; **mở lại trang ra hạt khác**. `engine.js` dòng 8–10 cấm `Math.random`. Chép code các style này là NO-GO kỹ thuật lẫn license.
- `linocut` lượng tử 12 fps: tua giữa hai nấc ra cùng hình. Hợp seek-safe.

## 7. Điều kiện GO về hiệu năng

Issue #258: cảnh 10 s < 2× realtime trên Mac.

Trạng thái bước này: **chưa đo, không đạt điều kiện GO vô điều kiện.** Nếu PO vẫn mở ticket triển khai, bắt buộc đo 3 style P0 trên Mac bằng pipeline HyperFrames (không dùng `render_ornek.mjs`), ghi CPU/RAM/thời gian vào ticket đó.
