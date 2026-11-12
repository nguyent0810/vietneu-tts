# Đề xuất tích hợp Animation Style Catalog (GH-258)

Repo ngoài: `yasinozmeen/animasyon-stil-katalogu` @ `09e451d8b64ec85c1ec035fd39e00725c1ed5593`.
Không chép mã nguồn catalog. Không sửa production trong lượt này.

## 1. Ba phương án

### A — Dùng lại code catalog

Nhúng `stiller/<slug>/anim.html` (hoặc `common.js`) vào composition HyperFrames, gọi `window.draw({t})` trên tween đồng hồ.

| Tiêu chí | Đánh giá |
|---|---|
| Độ phức tạp ban đầu | Thấp về mặt kỹ thuật (API `draw(t)` đã có). Cao về hạ tầng: Playwright global, Chrome mac-arm64 (`render_ornek.mjs` 16–21). |
| Bảo trì | Hai vòng đời Chrome (catalog vs HyperFrames). Font woff2 riêng từng style. |
| Nợ kỹ thuật | `Math.random` ở `veri`/`terminal`/`kinetik-tipografi`. Nội dung tiếng Thổ cứng. Không nhận JSON. |
| Mở rộng | Mỗi style một file 9–30 KB canvas, không dùng chung `when(ctx, step)`. |
| Chi phí render | JPEG `toDataURL` mỗi khung, ước lượng nặng hơn chụp GSAP. Chưa đo. |
| Rủi ro license | **Loại.** GitHub `license: null`, không file LICENSE. README chỉ cấp OFL cho font (dòng 78). Mặc định giữ mọi quyền. |
| Phụ thuộc repo ngoài | Cao: mọi sửa phải bám upstream không có cam kết API. |

**Loại A.**

### B — Lấy ý tưởng, viết lại clean-room thành cảnh JSON trong kho hiện có

Viết cảnh mới trong `longform.js` / `longform_styles.js` (BUD/FS) và móc `casewide.js` qua `hf_styles.js` (CL/MIM/CK). Tham số JSON, mốc `at`/`word` qua `when()` (`longform.js` 38–47), PRNG `HF.rng` (`engine.js` 16–23) hoặc `rnd` của casewide (`casewide.js` 23). Không mở mã catalog lúc viết.

| Tiêu chí | Đánh giá |
|---|---|
| Độ phức tạp | Vừa. Mỗi style 100–400 dòng SVG/Canvas/DOM + spec JSON. Đã có mẫu `longform_styles.js`. |
| Bảo trì | Một pipeline HyperFrames, một bộ font kênh, lint chữ sẵn có. |
| Nợ kỹ thuật | Thấp nếu opt-in: plan không gọi tên thì render_key chương cũ giữ nguyên (`hf_styles.js` 1–3, `build_long.py` 734). |
| Mở rộng | Thêm `type` vào `scene_params.py` + `B[type]` / `HF_LONG.visuals`. |
| Chi phí render | Cùng lớp cảnh hiện có. Ước lượng, chưa đo 2× realtime. |
| Rủi ro license | Thấp: ý tưởng/phong cách không phải biểu đạt mã. Không copy hằng số, path, bảng màu, asset. |
| Phụ thuộc repo ngoài | Không, sau khi nghiên cứu xong. |

**Chọn B.**

### C — Giữ pipeline xưởng, chỉ thêm vài template HTML độc lập

Giữ `anim.html` như “template”, đổi chữ bằng search-replace, render riêng rồi ghép FFmpeg vào chương.

| Tiêu chí | Đánh giá |
|---|---|
| Độ phức tạp | Cao: hai renderer, hai cách tua, khớp TTS bằng tay. |
| Bảo trì | Template tiếng Thổ, font riêng, `build.sh` zsh. |
| Nợ kỹ thuật | Cao. Chương HyperFrames và clip catalog lệch màu/fps. |
| Mở rộng | Mỗi video một bản sao HTML. |
| Chi phí render | Thêm một vòng Playwright catalog. |
| Rủi ro license | Vẫn chạm biểu đạt mã nếu giữ `anim.html`. |
| Phụ thuộc repo ngoài | Cao. |

**Loại C.**

## 2. Bảng so sánh ngắn

| | A chép code | B clean-room | C template phụ |
|---|---|---|---|
| License | Không đạt | Đạt | Không đạt nếu giữ HTML |
| JSON + TTS | Phải bóc cứng | Có sẵn `when()` / mốc giây casewide | Khớp tay |
| Tua theo khung | `draw(t)` | GSAP paused (`engine.js` 274, `casewide.js` 36) | Hai đồng hồ |
| macOS + Linux ARM | Script catalog vỡ trên Linux ARM | Pipeline xưởng | Vỡ cùng A |
| Khớp kho sẵn có | Dễ trùng kinetic/terminal/veri | Chỉ thêm khoảng trống | Trùng và lệch da |

## 3. Trạng thái kho lúc viết (12/11/2026)

PR `#293` (`2294923784ca5a45c4a8931ba670a5904adfa9ea`) đã làm đúng B cho sáu cảnh:

| Ý tưởng catalog | Cảnh trong kho | File |
|---|---|---|
| linocut | `woodcut` | `motion/hf/compositions/longform_styles.js` 119 |
| kagit-kesik | `papercut` | cùng file 250 |
| tek-cizgi | `oneline` | 311 |
| belgesel-16mm | `film16` | 385 |
| blueprint | `blueprint` | 480 |
| karakalem | `pencil` | 536 |

Móc CL/MIM/CK: `motion/hf/assets/engine/hf_styles.js` đăng `B[name]` qua `chartScenes`, không sửa `casewide.js`. Spec: `motion/long/scene_params.py` 84–89. Builder chỉ nhúng script khi chương có loại này (`build_long.py` 734–735).

Skill `motion-library` (`SKILL.md` đoạn “Bộ style bổ sung (#258)”) đã ghi luật PO: tối đa 3 cảnh style / Long, không hai cảnh liền nhau.

Lượt nghiên cứu này **không** mở ticket triển khai mới cho sáu tên trên.

## 4. Đề xuất cụ thể (B)

1. **Giữ A/C đóng.** Không vendor catalog, không submodule.
2. **Không viết lại sáu cảnh đã có** trừ khi Lead so showreel thấy lệch brief kênh.
3. **Khoảng trống còn lại, chỉ nếu PO muốn đợt sau (không làm trong spike này):**
   - MIM: explainer phẳng kiểu Kurzgesagt (hình khối, một ý một cảnh) — catalog `kurzgesagt` / `izometrik`. Viết mới, JSON `items`/`steps`, không copy path.
   - Không làm `hud` (cấm `quy_uoc.md` luật 4), `memphis`/`piksel`/`kil`/`cizgi-roman` (thương hiệu BUD/FS), `veri`/`kinetik-tipografi`/`terminal` (đã có `bars`/`ledger`/`beat.js`/`idcard terminal`).
4. **Hợp đồng kỹ thuật bắt buộc** nếu có đợt sau:
   - Mọi trạng thái = f(t), `HF.rng` / `rnd`, không `Math.random`/`Date`.
   - Spec JSON: `type`, `at`/`word`/`until`, màu theo look/theme, chữ tiếng Việt.
   - Opt-in: không bộ chọn tự chèn; plan cũ byte-identical.
   - Đo 10 s trên Mac trước khi tuyên bố < 2× realtime.
5. **TTS:** map `steps[i].at`/`word` sang `when(ctx, step)` như `longform_styles.js` 34–43. Casewide đã quy mốc về giây (`casewide.js` 1–3).
6. **FFmpeg:** không đổi. Giọng VieNeu + mix hiện tại. Catalog tự synth SFX (`sfx.py` / `synth.py`) — không lấy file tiếng của họ.

## 5. GO / NO-GO

Điều kiện issue #258:

| Điều kiện | Kết quả lượt này |
|---|---|
| ≥ 2 style P0 hợp ≥ 1 kênh đang chạy | **Đạt.** `linocut`, `kagit-kesik`, `tek-cizgi` hợp BUD và FS; CL dùng được `linocut`/`belgesel-16mm`. |
| Làm lại B hoặc C không đụng license | **Đạt với B.** A/C không đạt license. |
| 10 s render < 2× realtime trên Mac | **Chưa đo.** |
| Tua theo khung tất định, render theo chương | **Đạt với B** trên engine hiện tại. Catalog gốc đạt seek `draw(t)` nhưng script xuất không chạy Linux ARM. |

**Kết luận: GO có điều kiện theo phương án B.** Ba điều kiện pháp lý/khoảng trống/tua khung đạt. Điều kiện hiệu năng chưa đo nên không GO vô điều kiện.

Vì sáu P0/P1 cốt lõi đã vào `#293`, spike này **không** mở ticket triển khai mới. Việc còn lại nếu PO duyệt: (1) đo benchmark HyperFrames cho `woodcut`/`papercut`/`oneline`; (2) tuỳ chọn 1–2 cảnh MIM explainer clean-room, ticket riêng.

## 6. Việc không làm

- Không chép `anim.html` / `common.js` / `render.mjs`.
- Không cài Playwright vào `.venv` hay máy dựng.
- Không đổi lịch, không commit, không đăng.
