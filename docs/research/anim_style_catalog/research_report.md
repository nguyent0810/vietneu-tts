# Báo cáo Nghiên cứu Kỹ thuật: Animation Style Catalog

- **Mã nhiệm vụ:** 033 — Research spike: Animation Style Catalog (Issue #258)
- **Người thực hiện (Thợ):** agy
- **Người duyệt (Lead):** Claude Opus 5.5
- **Kho nguồn nghiên cứu:** `https://github.com/yasinozmeen/animasyon-stil-katalogu`
- **Thư mục làm việc:** `output/research_tmp/animasyon-stil-katalogu`
- **Commit SHA đã clone:** `09e451d8b64ec85c1ec035fd39e00725c1ed5593`

---

## 1. Mục tiêu Nghiên cứu

Đánh giá bộ sưu tập 20 phong cách animation trong kho `yasinozmeen/animasyon-stil-katalogu` nhằm trả lời 3 câu hỏi cốt lõi:
1. Có thể ứng dụng để nâng cao chất lượng hình ảnh và giảm cảm giác "slideshow tĩnh" trong video hay không?
2. Có tương thích và tái sử dụng được trong pipeline hiện tại của xưởng (HyperFrames `engine.js` / `longform.js`, `hyperframes_bridge.py`, FFmpeg, VieNeu TTS) không?
3. Rủi ro bản quyền, chi phí render và mức độ nợ kỹ thuật của từng phương án tích hợp ra sao?

---

## 2. Kiểm kê Thực tế Kho Mã Nguồn (`stiller/`)

Kiểm tra trực tiếp cấu trúc thư mục tại commit `09e451d8b64ec85c1ec035fd39e00725c1ed5593`, kho chứa **chính xác 20 thư mục phong cách** trong `stiller/` (khớp với kịch bản ghép `birlestir.sh:22-41`):

| Nhóm nghệ thuật (`birlestir.sh`) | Thư mục phong cách (`stiller/<slug>`) | File mã nguồn | Clip mẫu & Demo |
|---|---|---|---|
| **Düz grafik** (Đồ hoạ phẳng) | `kurzgesagt`, `izometrik`, `bauhaus`, `memphis` | `anim.html` (13KB – 26KB) | `<slug>.mp4` (9-10s), `onizleme.gif` |
| **El çizimi** (Nét vẽ tay) | `beyaz-tahta`, `kara-tahta`, `blueprint`, `tek-cizgi` | `anim.html` + `common.js` | `<slug>.mp4` (9-10s), `onizleme.gif` |
| **Doku ve zanaat** (Chất liệu thủ công) | `kagit-kesik`, `karakalem`, `linocut`, `kil` | `anim.html` (20KB – 27KB) | `<slug>.mp4` (9-10s), `onizleme.gif` |
| **Nostalji** (Hoài niệm / Cổ điển) | `retro-70ler`, `piksel`, `belgesel-16mm`, `cizgi-roman` | `anim.html` (18KB – 29KB) | `<slug>.mp4` (9-10s), `onizleme.gif` |
| **Teknik** (Giao diện kỹ thuật) | `terminal`, `hud`, `veri` | `anim.html` (15KB – 23KB) | `<slug>.mp4` (9-10s), `onizleme.gif` |
| **Deneysel** (Thực nghiệm) | `kinetik-tipografi` | `anim.html` (11.8KB) | `<slug>.mp4` (9-10s), `onizleme.gif` |

Toàn bộ 20 style đều có mã nguồn độc lập, file cấu hình phông chữ (`yazi-tipleri.css` hoặc `fonts/`), video demo 1080p và ảnh động xem trước.

---

## 3. Kiến trúc Kỹ thuật & Nguyên lý Vận hành

### 3.1 Công nghệ kết xuất (100% HTML5 Canvas 2D)
- **Không dùng thư viện ngoài:** Không phụ thuộc Three.js, WebGL hay Anime.js/GSAP. Toàn bộ hình khối, đường nét, hiệu ứng chữ đều được vẽ trực tiếp qua Canvas 2D Context (`ctx = cv.getContext('2d')`).
- **Tối ưu kết cấu (Offscreen Canvas Caching):** Tuân thủ chỉ đạo kỹ thuật tại `BRIEF.md:21-23`, các hiệu ứng tốn kém (vân giấy `buildPaper()`, nhiễu hạt `valueNoise()`, vệt bụi phim `GRAIN`, bảng phấn `paper`) đều được tính toán và vẽ một lần duy nhất vào một Canvas ẩn (`document.createElement('canvas')`) trong giai đoạn khởi tạo (`window.ready`). Khi tua khung hình, engine chỉ việc gọi `ctx.drawImage(offscreenCanvas, ...)` kết hợp với chế độ hoà trộn (`globalCompositeOperation`).
- **Thư viện dùng chung (`common.js`):** Xuất hiện tại 4 style vẽ nét (`beyaz-tahta`, `blueprint`, `kara-tahta`, `tek-cizgi`). Cung cấp lớp toán học đường cong `Path` hỗ trợ Bezier bậc 2, bậc 3 và Catmull-Rom Centripetal Spline (`common.js:37-47`), kèm tính năng bám nét vẽ vi sai `trace(ctx, s0, s1)` (`common.js:52-54`).

### 3.2 Cơ chế kiểm soát thời gian & Tính tất định (Deterministic Seek)
- **Hàm vẽ:** Mỗi file `anim.html` phơi ra hàm `window.draw(job)` hoặc `window.draw({t})` nhận tham số thời gian $t \in [0, 10.0]$ giây.
- **Tính phi trạng thái (Statelessness):** Mọi vị trí, góc quay, độ co giãn và độ mờ đục đều là hàm giải tích trực tiếp của $t$ thông qua các hàm nội suy (`lerp`, `seg`, `eInOut`). Trình kết xuất có thể nhảy tới bất kỳ thời điểm $t$ nào mà không cần chạy qua các khung hình trước đó.
- **Tính tất định của hạt giống (Seeded PRNG):** Các style có nhiễu ngẫu nhiên đều sử dụng bộ sinh số giả ngẫu nhiên có hạt giống (`rng(seed)` tại `linocut/anim.html:20`, `common.js:12`), đảm bảo tại cùng một giá trị $t$, kết quả khung hình là nhất quán bit-to-bit.

### 3.3 Quy trình xuất video (`render_ornek.mjs` + `birlestir.sh`)
- Node.js script khởi chạy trình duyệt không đầu (`chrome-headless-shell`) qua Playwright, mở đồng thời nhiều worker tab (mặc định 4 trang).
- Mỗi worker tải `anim.html`, chờ `window.ready`, sau đó lần lượt đánh giá `window.draw({t: n/30})` để lấy chuỗi Base64 JPEG và ghi ra đĩa thành các file ảnh đánh số `00000.jpg`, `00001.jpg`...
- Script shell `birlestir.sh:16-19` dùng FFmpeg nối chuỗi ảnh JPEG thành MP4 (CRF 18, 30fps, H.264) và ghép thêm âm thanh rỗng hoặc âm thanh hiệu ứng.

---

## 4. Rà soát Bản quyền & Pháp lý (License Audit)

- **Trạng thái GitHub:** API trả về `license: null`. Không có file `LICENSE`, `COPYING` hay `UNLICENSE` ở thư mục gốc cũng như các thư mục con.
- **Điều khoản trong tài liệu:**
  - `README.md:78` ghi rõ: *"Yazı tipleri Google Fonts'tan (SIL Open Font License); her klasörün `fonts/` dizininde."* — Chỉ có các tệp phông chữ được cấp phép theo SIL Open Font License.
  - Mã nguồn JavaScript/HTML/CSS hoàn toàn không có giấy phép mã nguồn mở (MIT, Apache, BSD, GPL...).
- **Hệ quả pháp lý quốc tế (Berne Convention / Bản quyền mặc định):**
  - Mọi quyền được bảo lưu bởi tác giả (`All Rights Reserved`).
  - **Phương án A (Sao chép trực tiếp mã nguồn vào repo):** **HOÀN TOÀN BỊ LOẠI TRỪ** do rủi ro xâm phạm bản quyền nghiêm trọng.
  - **Phương án B (Tiếp thu ý tưởng nghệ thuật & thuật toán, tự viết lại clean-room):** **HỢP PHÁP VÀ ĐƯỢC BẢO VỆ**. Luật bản quyền chỉ bảo vệ cách thể hiện cụ thể của mã nguồn (expression), không bảo vệ phong cách mỹ thuật (style), ý tưởng diễn hoạt (concept) hay công thức toán học nội suy (interpolation algorithms).

---

## 5. Đối chiếu với Kho Phong cách Sẵn có của Xưởng

### 5.1 Kho `longform.js` (Hơn 40 loại visual đang chạy trong production)
Trong `hyperframes_short/compositions/longform.js`, kênh đã có:
- **Hệ thống dữ liệu / Đồ thị:** `stat`, `pie`, `compare`, `ledger`, `timeline`, `years`, `map`, `region`.
- **Hệ thống phong thuỷ / Văn hoá:** `wheel` (vòng 12 chi), `elements` (ngũ hành tương sinh), `bagua` (bát quái), `luoshu` (lạc thư), `hexagram` (quẻ dịch), `chiwheel`, `cuudieu`, `napam`.
- **Hệ thống thẻ & chữ:** `quote`, `word`, `ask`, `doc`, `stamp`, `scroll`, `teaser`, `clues`.
- **Hệ thống chữ động nhịp:** `KINETIC` (`longform.js:651, 671, 689`) hỗ trợ gõ nhịp từng từ theo beat của audio.

### 5.2 Kho `motion-library` (`.claude/skills/motion-library/`)
- Đã lưu trữ 234 mẫu motion tham khảo (`prompt_motion/catalog.json`), phân tích chi tiết các thư viện video Opus 5.5 (`references/opus55_styles.md`).

### 5.3 Nhận định trùng lặp & Khoảng trống thực sự:
1. **Trùng lặp hoàn toàn:**
   - `kinetik-tipografi` trùng 100% với `KINETIC` đã có trong `longform.js`.
   - `terminal` trùng 100% với block có sẵn trong HyperFrames registry (`components/terminal`).
2. **Trùng lặp phần lớn (Không cần bổ sung):**
   - `veri` (Dataviz) đã được giải quyết rất tốt bởi cụm `stat`, `pie`, `compare`, `ledger` trong `longform.js`.
   - `kara-tahta` / `beyaz-tahta`: Kênh đã có `annot` và `sketch` vẽ vector SVG, việc bổ sung bảng phấn hay bảng bút dạ mang lại giá trị gia tăng rất thấp, dễ tạo cảm giác video bài giảng công sở đại trà.
3. **Khoảng trống thực sự (Giá trị đột phá):**
   - **`linocut` (Tranh mộc bản khắc gỗ):** Hiện kênh chỉ có `stamp` (đóng dấu triện đỏ phẳng). Cần một cảnh mộc bản toàn phần với vết đục gỗ V-groove, hai màu mực in đen/chu sa tương phản cao, và hiệu ứng mực nhấp nháy 12fps (ink boil).
   - **`kagit-kesik` (Cắt giấy diorama đa tầng đổ bóng động):** Hiện kênh chỉ có `shadow` (rối bóng 2D phẳng). Diorama cắt giấy có đổ bóng 3D động theo hướng chiếu sáng là định dạng kể chuyện tuyệt phẩm cho truyện kinh Phật giáo và truyền thuyết dân gian.
   - **`tek-cizgi` (One-line art liên tục):** Hiện kênh chưa có cơ chế vẽ đơn nét mềm mại liên tục biến hình (morphing spline). Cực kỳ thanh thoát cho các biểu tượng Phật giáo thiền định và dòng khí mạch phong thuỷ.
   - **`blueprint` (Bản vẽ kiến trúc kỹ thuật cyanotype):** Phù hợp xuất sắc cho các video giải thích mặt bằng nhà đất, phong thuỷ bát trạch.
   - **`belgesel-16mm` (Thước phim tư liệu 16mm xước rung):** Cực kỳ phù hợp cho các đoạn trích tư liệu lịch sử trong kênh Chiến Lược.

---

## 6. Đánh giá Mức độ Phù hợp theo Từng Kênh

| Kênh | Yêu cầu định vị thương hiệu | Phong cách phù hợp nhất | Phong cách cấm kỵ / Tránh dùng |
|---|---|---|---|
| **FS** (Phong Thuỷ) | Huyền bí, cổ kính, truyền thống Á Đông, số liệu tính toán chính xác bằng code | `linocut` (mộc bản phong thuỷ, sấm ký), `kagit-kesik` (tích cổ dân gian), `tek-cizgi` (khí mạch luân chuyển), `blueprint` (mặt bằng bát trạch) | `memphis`, `piksel`, `kil` (quá nhí nhố, phá vỡ tính huyền bí) |
| **BUD** (Phật Giáo) | Trang nghiêm, thanh tịnh, mực thước, không cợt nhả/biếm hoạ, Đức Phật tôn nghiêm | `linocut` (mộc bản kinh Phật chùa Vĩnh Nghiêm), `kagit-kesik` (kể chuyện Jātaka / tích tiền thân), `tek-cizgi` (thiền định, hoa sen một nét) | `cizgi-roman`, `memphis`, `kil`, `retro-70ler` (vi phạm nghiêm trọng tính trang nghiêm của Phật môn) |
| **CL** (Lịch Sử / Chiến Lược) | Chân thực, hào hùng, tư liệu lịch sử chuẩn xác | `belgesel-16mm` (tư liệu cổ), `linocut` (tuyên ngôn, chiếu chỉ, mộc bản sắc phong) | `memphis`, `piksel` |
| **CK** (Chứng Khoán) | Trực quan, sắc bén, hiện đại, uy tín | `veri` (đã có), `izometrik` (chuỗi giá trị), `blueprint` (cơ cấu hạ tầng) | `kil`, `cizgi-roman` |
| **MIM** (Giải thích khoa học) | Sinh động, sáng rõ, kích thích tò mò | `kurzgesagt`, `izometrik`, `blueprint`, `bauhaus` | — |

---

## 7. Khả năng Tương thích Hạ tầng

1. **Với HyperFrames (`engine.js` / `longform.js`):**
   - **Đồng bộ thời gian:** HyperFrames điều khiển mọi chuyển động thông qua GSAP Timeline bị tạm dừng (`tl.seek(t)`). Cơ chế vẽ Canvas theo tham số $t$ trong repo này có thể tích hợp hoàn hảo vào GSAP thông qua tween giả lập đồng hồ:
     ```javascript
     tl.to(clock, { t: dur, duration: dur, ease: "none", onUpdate: () => window.drawCanvas(clock.t) }, startAt);
     ```
   - **Tránh phình to DOM:** Vẽ Canvas 2D giúp DOM của HyperFrames hoàn toàn sạch sẽ, không tạo hàng nghìn node SVG hay `<div>`, giúp giảm áp lực bộ nhớ khi render video dài trên 40 phút.
2. **Với Timing Segments của VieNeu TTS:**
   - Cấu trúc e-action dạng danh sách sự kiện có mốc thời gian (`acts.push({ kind, t0, t1 })` tại `blueprint/anim.html:28-31`) cho phép gắn trực tiếp toạ độ thời gian của từng từ (`word.t`) hoặc từng câu (`sentence.start`) từ manifest TTS vào các điểm kích hoạt diễn hoạt.
3. **Với FFmpeg:**
   - Đầu ra của Canvas ở mỗi khung hình có thể đưa trực tiếp vào luồng pipe `image2pipe` của FFmpeg mà không cần ghi hàng nghìn file ảnh tạm ra đĩa, giúp tiết kiệm triệt để không gian ổ cứng.
