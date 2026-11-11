# Báo cáo Hiệu năng & Khả năng Vận hành (Benchmark)

Nhiệm vụ: Research spike Animation Style Catalog (Issue #258).  
Repo mục tiêu: `output/research_tmp/animasyon-stil-katalogu` (Commit SHA: `09e451d8b64ec85c1ec035fd39e00725c1ed5593`).

---

## 1. Trạng thái Kiểm chứng Môi trường

Theo quy định bắt buộc của ticket 033 và luật vận hành thợ:
- **Kiểm tra dung lượng đĩa:** Chạy lệnh `df -g .`:
  ```
  Filesystem   1G-blocks Used Available Capacity iused     ifree %iused  Mounted on
  /dev/disk3s5       228  174        13    93% 2598921 138424200    2%   /System/Volumes/Data
  ```
  Dung lượng trống khả dụng là **13 GB** (dưới ngưỡng an toàn bắt buộc 20 GB).
- **Kiểm tra tiến trình hệ thống:** Chạy `pgrep -fl hf_batch_render`:
  ```
  74664 .venv/bin/python hf_batch_render.py output/cl_staging/long --only L_bud_P3_ananda --quality delivery
  ```
  Tiến trình render video dài của Lead đang chạy nền trên máy.

> **Kết luận thực nghiệm:** **Chưa kiểm chứng: thiếu đĩa (13 GB < 20 GB)** và Lead đang render song song. Tuân thủ tuyệt đối quy tắc của issue #258: không chạy render thử nghiệm để tránh làm cạn kiệt ổ cứng và gián đoạn pipeline production. Dưới đây là phân tích hiệu năng và kiến trúc dựa trên việc đọc trực tiếp mã nguồn.

---

## 2. Phân tích Kiến trúc Render từ Mã Nguồn

### 2.1 Cơ chế render của repo ngoài (`render_ornek.mjs`)
- **Bộ điều khiển:** Node.js script sử dụng Playwright và `chrome-headless-shell` (`output/research_tmp/animasyon-stil-katalogu/render_ornek.mjs:7-10`).
- **Đa luồng (Worker pooling):** Chia đều mảng công việc `jobs` gồm các mốc thời gian $t = n / 30$ cho $W$ workers (`render_ornek.mjs:24-34`):
  ```javascript
  // render_ornek.mjs:28-31
  for (let i = w; i < jobs.length; i += workers) {
    const b64 = await page.evaluate(j => window.draw(j), jobs[i]);
    fs.writeFileSync(jobs[i].file, Buffer.from(b64, 'base64'));
  }
  ```
- **Xuất khung hình:** Mỗi khung hình được trình duyệt render trên Canvas 2D độ phân giải 1080p (1920×1080) và trả về chuỗi Base64 JPEG (`cv.toDataURL('image/jpeg', 0.92)`).
- **Đóng gói video:** Shell script `birlestir.sh:16-19` gọi FFmpeg gom chuỗi file ảnh JPEG thành video H.264 MP4 với profile `yuv420p`, CRF 18, 30 fps.

### 2.2 Đánh giá tính Tất định (Determinism) & Khả năng Tua (Seek-safe)
- Trong cả 20 style tại `stiller/*/anim.html`, hàm `window.draw(job)` hoặc `window.draw({t})` nhận trực tiếp tham số thời gian $t$ (tính bằng giây).
- **Không có tích luỹ trạng thái:** Mọi toạ độ, góc xoay, độ mờ, độ dày nét đều được tính toán theo công thức đóng (closed-form interpolation) dựa trên các hàm easing (`lerp`, `seg`, `eInOut`, `eOut`, `eBack`).
- **Hạt giống ngẫu nhiên cố định:** Các style có yếu tố ngẫu nhiên (như nhiễu hạt giấy trong `linocut:20`, vệt phấn trong `kara-tahta`) đều sử dụng thuật toán PRNG với seed xác định (`rng(seed)` Linear Congruential Generator), đảm bảo tìm nạp bất kỳ khung hình $t$ nào cũng cho ra kết quả bit-to-bit giống hệt nhau.
- **Tương thích render theo chương:** Kiến trúc tua khung theo $t$ này hoàn toàn tương thích với cơ chế render theo chương (chapter offset) của HyperFrames.

---

## 3. Phân tích Chi phí Tính toán (CPU / RAM / Render Cost)

Dựa trên kiểm tra cấu trúc mã nguồn của 20 style:

1. **Nhóm chi phí nhẹ (Lightweight - Dự kiến < 0.8x realtime):**
   - *Styles:* `tek-cizgi`, `kinetik-tipografi`, `terminal`, `bauhaus`, `veri`.
   - *Đặc điểm:* Chỉ sử dụng các lệnh vẽ vector cơ bản (`stroke`, `fill`, `arc`, `lineTo`), không xử lý bộ đệm điểm ảnh (pixel manipulation), không đổ bóng.
2. **Nhóm chi phí vừa (Moderate - Dự kiến 0.8x - 1.4x realtime):**
   - *Styles:* `blueprint`, `izometrik`, `kurzgesagt`, `kara-tahta`, `beyaz-tahta`, `hud`, `cizgi-roman`.
   - *Đặc điểm:* Có sử dụng biến đổi ma trận 2.5D, đường nét đứt, hatch pattern, hoặc vẽ nhiều phần tử cùng lúc nhưng các texture tĩnh đã được nướng sẵn vào offscreen canvas ở bước chuẩn bị (`window.ready`).
3. **Nhóm chi phí nặng (Heavy - Dự kiến 1.4x - 1.9x realtime):**
   - *Styles:* `kagit-kesik`, `linocut`, `karakalem`, `belgesel-16mm`, `kil`.
   - *Đặc điểm:*
     - `kagit-kesik`: Bật tính năng đổ bóng canvas (`shadowBlur: 16-24px`, `shadowOffsetY`) trên 5-7 lớp cắt giấy xếp chồng, tiêu tốn nhiều thời gian xử lý Gaussian blur phần cứng.
     - `linocut`: Sử dụng `globalCompositeOperation = 'multiply'` và `destination-out` để giả lập thớ gỗ bị khoét và lớp mực rỗ; hiệu ứng mực nhảy (ink boil) chu kỳ 12fps đòi hỏi redraw lại lớp mực liên tục.
     - `belgesel-16mm`: Tạo và phủ lớp màng xước phim nhựa, vệt bụi nhảy ngẫu nhiên mỗi khung hình và hiệu ứng loá sáng (film gate flash).

> **Nhận định:** Toàn bộ 20 style đều tránh được việc tính toán lại texture lớn trên từng frame nhờ kỹ thuật tiền tạo mẫu (pre-rendering offscreen texture) được quy định chặt chẽ trong `BRIEF.md`. Do đó, thời gian render ước tính trên chip Apple Silicon (M-series) hoàn toàn nằm trong ngưỡng yêu cầu **< 2x thời gian thực**.

---

## 4. Rào cản Môi trường (macOS vs Oracle Linux)

Trong mã nguồn `render_ornek.mjs`:
```javascript
// render_ornek.mjs:7
const { chromium } = require(path.join(execSync('npm root -g').toString().trim(), '@playwright/test'));

// render_ornek.mjs:17-21
const exe = (() => {
  const base = path.join(process.env.HOME, 'Library/Caches/ms-playwright');
  const dirs = fs.readdirSync(base).filter(d => d.startsWith('chromium_headless_shell-')).sort().reverse();
  for (const d of dirs) { const p = path.join(base, d, 'chrome-headless-shell-mac-arm64/chrome-headless-shell'); if (fs.existsSync(p)) return p; }
})();
```
- **Gắn cứng nền tảng:**
  1. Yêu cầu gói `@playwright/test` cài đặt toàn cục (`npm -g`).
  2. Đường dẫn binary chỉ quét thư mục `Library/Caches/ms-playwright` của macOS và nhắm đúng thư mục con `chrome-headless-shell-mac-arm64`.
- **Hệ quả:** Script gốc của repo ngoài **KHÔNG THỂ CHẠY** trên môi trường Linux (như máy chủ Oracle Linux ARM đang dùng biến `HYPERFRAMES_BROWSER_PATH`). Nếu muốn chạy, bắt buộc phải viết lại logic tìm kiếm executable theo chuẩn POSIX và đường dẫn Linux.

---

## 5. Bổ sung 10/11/2026 — bộ style clean-room đã dựng (nhánh `feat/anim-style-set`)

Thợ dựng cảnh (Claude) viết lại 6 style theo phương án B thành `hyperframes_short/compositions/longform_styles.js` + `.css`
(mã tự viết, không mở mã nguồn repo ngoài; chỉ xem README/BRIEF và trích khung phim mẫu bằng ffmpeg để lấy cảm hứng).
Chọn: `woodcut` (linocut), `papercut` (kâğıt kesik), `oneline` (tek çizgi), `film16` (belgesel 16 mm), `blueprint`, `pencil`
(karakalem; bản tối = phấn bảng đá, thay cho kara-tahta). Bỏ kurzgesagt/izometrik (không hợp BUD/FS, chưa kênh nào cần).

### 5.1 Môi trường lúc đo
- `df -g .`: **1 GB trống** (228 GB dùng 186 + snapshot) → theo luật ticket, **không render video**, chỉ xuất PNG khung tĩnh.
- `ps`: không có `hf_batch_render.py` đang chạy.
- Máy: macOS 24.5 (Apple Silicon), node 22 qua nvm, `hyperframes@0.8.75`, `chrome-headless-shell` của HyperFrames.

### 5.2 Cách đo (không bịa số)
`python hf_style_demo.py stills s1|s2|s3`: chạy `hyperframes_bridge.render` tới hết bước dựng HTML (chặn đúng lệnh
`hyperframes render` bằng monkeypatch), dựng project tạm như `hf_qa`, rồi `hyperframes snapshot --at` 9 mốc (đầu/giữa/cuối của
3 cảnh style). Số đo là **thời gian chụp khung tĩnh qua CLI** (gồm khởi động trình duyệt + nạp font mạng), KHÔNG phải tốc độ render video.

| Cuộn | Cảnh style | Dựng HTML (bridge) | Chụp 9 khung | Giây/khung |
|---|---|---|---|---|
| s1 | woodcut, papercut, oneline | 0,1–0,2 s | 19,7–22,8 s (GPU) · 56,3 s (lần đầu sau đổi font, tải font) | 2,2–2,5 s |
| s2 | film16, blueprint, pencil | 0,1–0,2 s | 21,6–21,9 s · 48,1 s (tải font) | 2,4 s |
| s3 | woodcut (tối, số), blueprint (bars), papercut (citadel/dawn) | 0,1–0,2 s | 21,0–24,0 s | 2,3–2,7 s |

PNG 1920×1080 ≈ 1,5 MB/khung; 27 khung ≈ 42 MB trong `output/research_tmp/anim_styles_demo/` (không commit).
Chi phí mỗi khung của các cảnh (DOM + SVG + 1 canvas hạt phim 960×540 vẽ 40 tile/khung) nằm cùng cỡ các cảnh cũ của kho
(quote/list/stat cũng ~2,3 s/khung qua snapshot). Ước lượng render video thật (chưa đo vì thiếu đĩa): **không nặng hơn
cảnh `endcard` (shader WebGL mỗi khung) hay `depth` (filter blur)** — `papercut` dùng 7 lớp `drop-shadow` là cảnh tốn nhất.
Điều kiện GO #3 (10 s < 2× thời gian thực) **vẫn chưa kiểm bằng render video** — Lead chạy `python hf_showreel.py looks s1`
(và s2, s3) khi đĩa > 8 GB, đo bằng `time`.

### 5.2b Render video thật (bổ sung sau review, đĩa đã có ~30 GB)
`python hf_showreel.py looks s1|s2|s3` (HyperFrames render 1920×1080 30 fps, quality looks, 7 câu × 8 s = 56 s video, có ghép tiếng):

| Cuộn | Cảnh style | Thời gian render (real) | CPU user+sys | RAM đỉnh | Clip |
|---|---|---|---|---|---|
| s1 | woodcut, papercut, oneline | ≈ 91 s (Lead đo) | — | ≈ 0,6 GB | `output/cl_staging/reel_s1/showreel.mp4` |
| s2 | film16, blueprint, pencil | 92,8 s (lần 1) · 92,7 s (sau sửa clip pencil) | 148–158 s + 16–17 s | 616 MB / 611 MB | `output/cl_staging/reel_s2/showreel.mp4` (54,7 MB) |
| s3 | woodcut (tối, số), blueprint (bars), papercut (citadel/dawn) | 91,6 s | 129 s + 15 s | 607 MB | `output/cl_staging/reel_s3/showreel.mp4` (31,1 MB) |

→ ≈ **1,65× thời gian thực** cho cả cuộn (gồm 4 câu thường + thẻ chương của kho). Điều kiện GO #3 (< 2×) **ĐẠT**.
Nhạc nền lấy từ checkout chính qua biến `HF_BGM` (worktree không có `bgm/`, không copy nhạc vào repo).

### 5.3 Tính tất định (bit-một-bit)
`python hf_style_demo.py determinism` (chụp SwiftShader `--no-browser-gpu`, hai lượt trình duyệt riêng, cùng mốc giữa cảnh):
6/6 khung **md5 trùng** (woodcut 0c6b9f3465, papercut ee89379e0e, oneline 699ef4e99a, film16 1320724459, blueprint a25ab20622,
pencil 9ce7afd1ee). Với GPU tự chọn, 3 khung lệch ≤ 1/255 ở vài trăm điểm ảnh (nhiễu raster, không phải logic).

**Seek không theo thứ tự** (`python hf_style_demo.py seekorder`: Chrome + playwright-core trong cache npx, cùng một trang
seek tới mốc giữa cảnh → lùi 8 s → nhảy cuối cảnh → cuối cuộn → 0,5 s → quay lại mốc; và một trang mới seek thẳng):
6/6 "lùi-rồi-tiến" md5 trùng; 5/6 trang mới md5 trùng, papercut lệch 0,058 % điểm ảnh ở mức ≤ 1/255 (khử răng cưa chữ
giữa hai trang). Bài kiểm này bắt được một lỗi thật ở `pencil` (clip gạch chéo có `x` chỉ trong `from` của fromTo → GSAP lấy
giá trị hiện tại làm đích → phụ thuộc thứ tự seek); đã sửa (x đặt tĩnh lúc dựng, chỉ tween width) và ghi vào bảng bẫy
của `motion-scene-dev`.

### 5.4 Plan cũ không đổi
`python hf_style_demo.py regress <compositions của origin/main>`: plan chỉ có quote/list/stat, cùng HTML + biến đã nướng,
chụp với `compositions/` của nhánh này (có `longform_styles`) và của `origin/main` (không có): **6/6 khung md5 trùng**
(c2c73eca9c, 172fc2c800, e1c1ee0cf7, e1b4f0f21a, abb55e01c5, c4f073b669).
Bài học: bản đầu nhập lại Oswald/Playfair/Charm/Patrick Hand/JetBrains Mono/Cormorant Garamond (kho đã nạp) → chữ
JetBrains Mono của kicker/footer cảnh cũ lệch ~0,1 % điểm ảnh (khai báo `@font-face` kép). Đã đổi sang họ không trùng
(Anton, Yeseva One, Cormorant, Dancing Script, Itim, IBM Plex Mono — đều OFL, có dấu tiếng Việt); test
`tests/test_longform_styles.py` chặn nhập lại font kho.
