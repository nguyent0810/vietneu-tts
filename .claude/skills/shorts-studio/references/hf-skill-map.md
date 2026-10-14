# Bản đồ skill HyperFrames gốc (khi nào nạp) -- chi tiết: research/A_process.md §5

| Skill | Cho shorts | Nạp khi |
|---|---|---|
| hyperframes | router, workflow catalog, production/review loop | cần quy trình đầy đủ cho video không phải short |
| hyperframes-core | hợp đồng composition: clip, data-start, sub-composition, variables, determinism, fonts | sửa core.js / builder; lỗi timing, clip |
| hyperframes-animation | 48 rule, 22 blueprint, transitions, adapters (gsap, three, lottie) | thiết kế/port thiết bị mới (đọc rule trước khi viết) |
| hyperframes-keyframes | path, mask, crop, Ken Burns, 3D keyframes | thiết bị có vẽ nét / mặt nạ / camera |
| hyperframes-creative | frame-presets, palettes, typography, story-spine, beat-direction | tạo theme mới, viết kịch bản kênh mới |
| hyperframes-cli | lint, check, snapshot, timeline, benchmark, render flags | QA, gỡ lỗi render |
| hyperframes-audio | mix, carve (hạ nhạc theo giọng), automation | thay ffmpeg post-mix (A/B trước) |
| hyperframes-registry | catalog 447 khối, add, wiring | trước khi tự viết thiết bị: `catalog --query` |
| media-use | media-treatment (grading, halftone, engraving...), tts/captions/bgm/sfx | có ảnh/video thật; đổi xử lý ảnh |
| faceless-explainer | học thuyết chuyển động, cut-catalog, story-design | hình mẫu gần nhất cho short có lời đọc |
| motion-graphics | short không lời < 10s (kinetic-type, stat, chart, maps) | thẻ đầu/cuối, stinger kênh |
| general-video / music-to-video / slideshow / embedded-captions / talking-head-recut | kênh có footage, nhạc, slide | kênh khác loại hình |

## Registry: khối đáng port (research/E_registry.md §2 có port card)
`per-word-rise` (ease settle), `line-swap`, `kinetic-type-swap`, `marker-highlight`, `vox-annotate`, `count-up`, `grid-card-assemble`,
`comparison-split` (dọc), `constellation-hub`, `radial-surround`, `testimonial-proof-card`, `cut-the-curve`, `torn-paper-rip`, `ink-bleed-reveal`, `scroll-camera-story`.
- Port logic vào device trên timeline của mình (không mount sub-composition), giữ header "ported from <path>@<sha>, modified" (Apache-2.0);
  `kinetic-center-build`, `caret-swap` là MIT © Remocn -- giữ nguyên notice.
- Bỏ font Latin-only của registry; thay `--font-mono` = JetBrains Mono; bỏ tải CDN/mạng lúc render; line-height >= 1.25 trong mask.
- Bỏ: 36 khối WebGPU shader, html-in-canvas/liquid-glass, khối UI sản phẩm.
