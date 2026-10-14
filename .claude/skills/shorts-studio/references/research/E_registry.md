# E. HyperFrames registry: full classification for a modular 9:16 narrated Shorts engine

Scope: all 447 registry items (210 blocks, 237 components) from `npx hyperframes@0.8.75 catalog --json`, classified for reuse in the BUD/FS narrated Shorts engine: 1080x1920, Vietnamese copy with heavy diacritics, one paused GSAP timeline, word-timed cues (`ln.words[i] = {w, t, d, hot}`), deterministic renders with hyperframes 0.8.75.

Read-only research. No repo file was changed and nothing was installed into the repo.

**What I did**
- Read the `hyperframes-registry` skill and its references (discovery, wiring-blocks, wiring-components, install-locations, component-quality-bar, templates, placeholder-material).
- Read the two earlier reports so this one does not repeat them. `hf_visual_composition.md` §5 and `hf_3d_whiteboard_chart.md` §3 list many of these items by name. This report adds the full verdict for every item, source-level port cards and the licensing strategy.
- Fetched every item's `registry-item.json` (447) plus all its HTML/JS/CSS (598 text files, about 72 MB including the bundled shader and three.js libraries). They came from `raw.githubusercontent.com/heygen-com/hyperframes/main/registry/<blocks|components>/<name>/` into `scratchpad/research/registry_src/` (`manifests/`, `src/`). Registry `main` was at about `d77b03c` (2026-10-14).
- Scanned every item mechanically with comments stripped (`scan*.py`, results in `scan.json`). The scan covered fonts, shipped font files, container-query units versus px, the `<template>` mount contract, theme tokens, timing variables, sync points, timeline registration, WebGPU, WebGL, three.js, html-in-canvas, canvas2D, CSS `@keyframes`, `Math.random` and `Date.now`, network fetches, line-height with overflow masks, and uppercase.
- Hand-read about 45 sources for the port cards.
- Checked the Vietnamese subset of every Google font in use against the live Google Fonts CSS2 API (`fonts_subsets.txt`). Checked the system fonts on this Mac with `fc-list ':charset=1ec7 1ea5 01b0'`.
- Grepped the 0.8.75 runtime in the npx cache (`~/.npm/_npx/56de3f8b9956197b/node_modules/hyperframes/dist`). It supports `<template>` mounting, `window.__hyperframes.getVariables()`, `data-variable-values` on the host mount, `data-requires-webgpu` and `data-no-timeline`. So the new mount contract is not ahead of our pinned version.

**Legend**
- **rel:** A = adopt. Mount it, or copy it nearly verbatim into an engine device. B = adapt or port the logic, with real changes for 9:16, Vietnamese or the token mapping. C = reference only, as an idea or recipe. X = not relevant: product UI, developer, brand mock, WebGPU-only, or the house circle cliché.
- **Portrait-ready:**
  - "Yes (cq-elastic)" means a `<template>` mount with `#root{inset:0; container-type:size}` and cq units. It reflows to any host box, but it was tuned on 16:9, so check font fit (G7).
  - "Likely" means unitless or % sizing.
  - "Partial (px-sized)" means a px-tuned snippet.
  - "No (16:9 px layout)" means a fixed 1920x1080 block.
  - "Native 9:16" means 1080x1920 or 1440x2560.
- **Diacritic risk:**
  - High: the font has no Vietnamese subset or the item ships a Latin-only font file, or the glyphs or alphabet are baked in.
  - Med: tight `line-height` plus an `overflow` mask, uppercase, canvas text measurement or rasterising, char splitting, or a monospace/system fallback that has no Vietnamese.
  - Low: theme-variable font with an Inter fallback (Inter has Vietnamese).
  - "Inter" in the fonts column is almost always the fallback inside `var(--font-display, Inter, …)`.
- **Runtime risk:**
  - High: WebGPU or html-in-canvas, which need a special Chrome build or flag.
  - Med: WebGL/three.js, network fetch, CSS keyframes, Lottie, `Math.random` or `Date.now` in code.
  - Low: GSAP plus DOM/SVG/canvas2D painted from timeline time.
  - "no own timeline (X1)" means the file is a recipe that does not register `__timelines`.
- Every item also loads GSAP 3.14.2 from jsdelivr. That is the same version our compositions use, so it is not repeated per row.

---

## 0. Cross-cutting findings (read before porting anything)

**Two generations of items.**
- **Generation 1** (about 300 items) uses 1920x1080 px blocks and `NOTL` snippets. Examples are the older `caption-*`, `lt-*`, `mk-*`, `hw-*`, `yt-*` and transitions.dev ports. They carry hardcoded px, no tokens, often a Google-Fonts `<link>`, and often no timeline.
- **Generation 2** (140 items) uses the *mount contract*:
  - `<template>` wrapping, `#root{position:absolute; inset:0; container-type:size}` and cq units.
  - `data-composition-variables` with `role: content|timing|style`, plus `syncPoints` in the manifest.
  - A fixed **IN / elastic HOLD / OUT envelope** that is never time-scaled. When the clip is shorter than IN+OUT, the phases compress proportionally.
  - Seeded LCG tables baked at build.
  - `hf:sfx` CustomEvents at sync points instead of audio.
  - Almost every A and B item is Generation 2. The envelope law matches what our engine needs: a device receives the line span as its duration and fits.

**G1. Theme-token contract.** Generation 2 items read the following:
- Colour tokens: `--fg --bg --surface --muted --border --brand --accent --accent-2 --radius`.
- Spacing tokens: `--space-1..3`.
- Font tokens: `--font-display --font-body --font-mono`.
- The `accent` enum maps `green → --brand`, `blue → --accent` and `violet → --accent-2`.

One shim per channel makes every Generation 2 item on-brand:

```css
/* FS (fs_v3 tokens) */ --fg:var(--ink); --bg:var(--paper); --surface:var(--paper2); --muted:var(--mute);
  --border:rgba(28,20,16,.15); --brand:var(--red); --accent:var(--gold); --accent-2:var(--lac);
  --font-display:"Be Vietnam Pro",sans-serif; --font-body:"Be Vietnam Pro",sans-serif; --font-mono:"JetBrains Mono",monospace;
/* BUD: --brand saffron/temple gold, --accent robe maroon, --accent-2 indigo ink; display Lora/EB Garamond */
```

**G2. Fonts and Vietnamese (verified against the Google Fonts API).**
- **No Vietnamese subset:** Bebas Neue, Lato, Caveat, DM Sans, Poppins, Outfit, Gabarito, Instrument Serif, Libre Baskerville, Figtree, Archivo Black, Permanent Marker (latin only), Courier Prime.
- **Shipped as Latin-only files:** Caveat-700-latin (the whole `hw-*` family), Geist-Latin and Geist ttf, Recursive-latin, inter-latin-*, permanent-marker and courier-prime.
- **Has a Vietnamese subset:** Inter, JetBrains Mono, Space Mono, Montserrat, Space Grotesk, Anton, Gelasio, Playfair Display, Libre Franklin, Geist (Google build), Archivo, Roboto Flex, Big Shoulders Display, League Gothic, Barlow Condensed, Oswald, Recursive (Google build), Cormorant Garamond, Be Vietnam Pro, Lora, EB Garamond, Noto Sans/Serif.
- **Handwriting faces with Vietnamese**, to replace Caveat: Patrick Hand, Pangolin, Itim, Charm, Dancing Script.
- A Latin-only font does not show tofu boxes. `latin-ext` covers ă/đ/ơ/ư, but the tone-marked letters U+1EA0–1EF9 fall back per glyph to another face. The result is a mixed-font word such as "Phật" or "nghiệp", which reads as broken.
- On this Mac, Helvetica Neue and Georgia cover Vietnamese. **Menlo does not, and "SF Mono" is not installed.** About 34 items use `var(--font-mono, "SF Mono", …)`, so always set `--font-mono: "JetBrains Mono"`.

**G3. Masks clip stacked diacritics.** Most text primitives use `line-height` 0.78–1.14 inside `overflow:hidden` masks. Measured values:

| item | line-height |
|---|---|
| headline-slam | 0.88 |
| char-slam-explode, ticker-takeover | 0.9 |
| line-swap, count-up | 1.0 |
| per-word-rise, kinetic-type-swap | 1.08 |
| marker-highlight | 1.14 |
| caption-camera-follow | 0.78 |
| testimonial-proof-card mask | 0.6 |

Vietnamese caps with two marks (Ấ Ầ Ẩ Ẫ Ậ Ồ Ổ Ữ) and the dot below (ạ ặ ộ) are clipped top and bottom. Two fixes:
- Use `line-height ≥ 1.25` on every masked unit.
- Or keep the visual leading and pad the mask: `padding-block:.22em; margin-block:-.22em` on the overflow box.

Uppercase makes it worse. Many Generation 2 kickers and labels are `text-transform:uppercase`.

**G4. Measuring before fonts load (our known trap).** Only `variable-axis-type` awaits `document.fonts.ready`. The following measure synchronously while the timeline is built:
- `getBoundingClientRect` or `getTotalLength`: marker-highlight, vox-annotate, testimonial-proof-card, titlecard-lockup, chart-story, caption-camera-follow, mk-callout-highlight, text-match-cut.
- Canvas `measureText`: every older `caption-*`.

If Be Vietnam Pro arrives late, markers, underlines and line masks land on the wrong boxes. Build devices only after fonts are ready. The 0.8.75 runtime also exposes `window.__hyperframes.fitTextFontSize` and `pretext` for font-aware fitting.

**G5. Splitting and matching text.**
- `per-word-rise` (split=char), `char-slam-explode`, `count-up` and others split with `Array.from(text)`. That is safe for NFC, but NFD input splits tone marks into separate spans. Normalise to NFC first, or use `Intl.Segmenter` with grapheme granularity. Only one item in the whole registry uses it.
- `emphasis_word`, `keyword` and `underline_word` matching is `text.toLowerCase().indexOf(word.toLowerCase())`. Normalise both strings to NFC.
- Strip our `**hot**` markers before passing text in.

**G6. Seek-safety patterns worth copying.**
- `camera-shake` drives its per-frame work through a *property setter on a tweened driver object*. Its source says timeline `onUpdate` "GSAP suppresses on seek() and … would freeze the shake on frame 0".
- The canvas items (`ink-bleed-reveal`, `particle-image-reveal`, `halftone-dissolve`, `torn-paper-rip`) redraw from scratch as a pure function of (seeded table, t). Their source notes that Chrome's live SVG filter raster "patches damaged tiles with seek-history-dependent seam antialiasing", so they compute the gooey blur and threshold in a canvas.
- `scroll-camera-story` warns that "cq-unit transform tweens blow up under seeks". Tween numbers, percent or px, never `cqh` strings. Several items do tween cq strings (`per-word-rise` `y:"8cqh"`). They work in the runtime's eventful seeks, but treat it as a risk and convert to px in our port.

**G7. 9:16 fit.** The Generation 2 font fits assume one line across about 88cqw, for example `per-word-rise`: `min(9.5, 126/chars) cqw`. In 1080 width a 40-character Vietnamese sentence lands at about 34 px. Use our own multi-line fit for portrait.
- Orbits use % radii (`constellation-hub`: 38% × 39%). These become tall ellipses in 9:16. That is usable, but re-tune the radii.

**G8. Runtime classes we should not use in the default render.**
- **WebGPU** (36 shaders.com blocks plus liquid-glass and others). Each is `data-requires-webgpu data-no-timeline` and carries a 1.4 MB `shaders.iife.js` with its own clock. The runtime pushes time through `window.__hfTypegpuTime` on a `setInterval`.
- **html-in-canvas** (10 items). These need a Chrome canary flag.
- **Network:** `us-map`, `spain-map` and `us-map-bubble` call `fetch(topojson)`, and `world-map` calls `d3.json(cdn)`. The timeline is built inside an async `then`, which is a race against the first seek.
- `grain-overlay` animates with CSS `@keyframes`, so it is not seek-safe.

**G9. Licensing.**
- The registry repo is Apache-2.0 (root `LICENSE`, confirmed through the GitHub API). 407 manifests have no `license` field, so they inherit Apache-2.0. Some have an `author` field, for example Jake Moran, Miao Yang and Stronkter.
- The 36 shaders.com blocks are "Apache-2.0 AND MIT" and ship `lib/shaders.THIRD-PARTY-LICENSES.txt` (shaders 4.0.0 MIT, typegpu, …).
- `kinetic-center-build` is MIT, © 2026 Remocn, with the notice in the header. `caret-swap` is "MIT AND OFL-1.1" (Remocn plus Geist).
- `weight-wave` is OFL-1.1 because of the Recursive font. `lottie-character-walk` is Apache-2.0.
- Shipped faces are OFL (Caveat, Courier Prime, Geist, Inter) or Apache (Permanent Marker). `texture-mask-text` and `caption-texture` textures come from ambientCG (CC0).

---

## 1. Complete classification table (all 447 items)

Grouped by function. Inside each group, rows are sorted A → B → C → X, then by name.

Totals: 447 items (210 blocks, 237 components). Relevance: A=33, B=66, C=159, X=189.


### 1. Kinetic typography and text effects (51 items: A 8, B 13, C 26, X 4)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `headline-slam` | component | motion-primitive, typography, headline | A heavyweight headline scales down into frame, lands with a deterministic three-frame shake, holds with subtle... | **A** | Yes (cq-elastic) | Med (Inter; lh 0.88 + overflow mask) | Low - GSAP/DOM |
| `kinetic-type-swap` | component | motion-primitive, text-effects, kinetic-type | A held sentence keeps its fixed text in place while one widest-word masked slot rolls through alternatives and... | **A** | Yes (cq-elastic) | Med (Inter; lh 1.08 + overflow mask) | Low - GSAP/DOM |
| `line-swap` | component | motion-primitive, text-effects, swap | A masked full-line beat replacement: line A holds center then exits up through an overflow-hidden mask as line B... | **A** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `mk-emphasis-type` | component | typography, text-treatment, minimal | Oversized low-contrast background word drifting slowly behind the subject — typography as texture | **A** | Likely (unitless/%) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |
| `number-wheel` | component | video-primitive, motion-primitive, number | A rolling digit counter primitive for metrics, prices, counts, and scoreboards | **A** | Likely (unitless/%) | Low (theme var / system) | Low - no own timeline (X1) |
| `per-word-rise` | component | motion-primitive, text-effects, typography | Words or characters rise into place in a controlled blur-to-sharp cascade, settle softly on landing, and hold still... | **A** | Yes (cq-elastic) | Med (Inter; lh 1.08 + overflow mask; char split) | Low - GSAP/DOM |
| `text-shimmer` | component | motion-primitive, text-effects, shimmer | A static headline receives one clean specular gradient sweep through its glyphs, then returns to its ordinary text... | **A** | Yes (cq-elastic) | Med (Inter; lh 0.96 + overflow mask) | Low - GSAP/DOM |
| `ticker-takeover` | component | motion-primitive, typography, ticker | A mono ticker rolls through options, locks on a final word with an accent flash, and promotes it into a full-frame... | **A** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 0.9 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `char-slam-explode` | component | motion-primitive, typography, text-treatment | Headline glyphs hold in a deterministic scatter, then reassemble with an overshooting slam and a three-frame landing... | **B** | Yes (cq-elastic) | Med (Inter; lh 0.9 + overflow mask; char split) | Low - GSAP/DOM |
| `extended-keyframe` | component | motion, ease, arrival | The never-fully-lands arrival: an element covers most of its move in the first fifth of the duration and creeps the... | **B** | Likely (unitless/%) | n/a (no copy) | Low - GSAP/DOM |
| `focus-blur-resolve` | component | motion-primitive, typography | A premium focus pull from heavy blur to crisp text, then a soft blur-out exit. | **B** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `kinetic-center-build` | component | motion-primitive, text-effects, kinetic-type | Words enter from the right and push the growing phrase left until the final line locks centered. | **B** | Likely (unitless/%) | Med (Geist; lh 1.0 + overflow mask; canvas text/measure) | Low - canvas2D, Google Fonts link |
| `per-word-crossfade` | component | motion-primitive, typography | Words gently fade into place with a short vertical drift for calm keynote rhythm. | **B** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `slot-machine-roll` | component | video-primitive, motion-primitive, typography | A vertical reel scrolls characters from one value to another. | **B** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `soft-blur-in` | component | motion-primitive, text, reveal | A soft opacity, blur, and lift reveal for headlines, captions, and product UI callouts | **B** | Partial (px-sized) | Low (theme var / system) | Low - no own timeline (X1) |
| `split-flap-board` | block 1920x1080 | text, kinetic, mechanical | Solari-style departure board: every cell walks its drum forward through the intervening characters of a fixed... | **B** | No (16:9 px layout) | **High** (flap alphabet var (default A-Z0-9)) | Low - GSAP/DOM |
| `strikethrough-replace` | component | motion-primitive, typography | Draw a strike line across old text, then reveal the replacement. | **B** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `svg-mask-reveal` | component | effect, svg, mask | A soft token-colored sweep reveals media only through an editable SVG wordmark mask. | **B** | Yes (cq-elastic) | Low (theme var / system) | Low - GSAP/DOM |
| `text-match-cut` | component | motion-primitive, transition, typography | One line of text becomes another mid-move: both ride a single 85 % easy-ease curve and hard-swap at the speed peak,... | **B** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `texture-mask-text` | component | text, text-effect, effect | CSS luminance masks that cut holes through letterforms - 66 pre-built texture masks from ambientCG PBR color maps | **B** | Likely (unitless/%) | Low (theme var / system) | Low - no own timeline (X1) |
| `type-match-cut` | component | motion-primitive, transition, typography | A headline splits vertically around an incoming panel, which grows from the negative space and takes the frame as... | **B** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 0.88 + overflow mask; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `blur-in` | component | video-primitive, blur-in, text-effect | An Operator Black word-level content reveal that resolves its own text from controlled blur | **C** | Partial (px-sized) | Low (theme var / system) | Low - no own timeline (X1) |
| `blur-out-up` | component | motion-primitive, typography | Words arrive clean and depart upward with increasing blur for airy exits. | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `bottom-up-letters` | component | motion-primitive, text, letters | Splits text into letters and reveals each glyph from below with deterministic staggered timing | **C** | Likely (unitless/%) | Med (theme var / system; char split) | Low - no own timeline (X1) |
| `caption-blend-difference` | component | text, text-effect, effect | Auto-inverting text using mix-blend-mode: difference — flips between white and black per-pixel against the background | **C** | Likely (unitless/%) | Med (theme var / system; uppercase) | Low - blend, no own timeline (X1) |
| `caret-swap` | component | motion-primitive, text-effects, typography | A gradient caret expands over one phrase, collapses to the left, then types its replacement with a blinking caret. | **C** | Likely (unitless/%) | **High** (ships Geist-Latin.woff2) | Low - GSAP/DOM |
| `colorama-wipe` | component | text, reveal, wipe | Headline reveal through a feathered, leaning wipe front that is blurred and colour-mapped as it passes, then settles... | **C** | Likely (unitless/%) | Med (theme var / system; canvas text/measure) | Low - canvas2D |
| `line-by-line-slide` | component | motion-primitive, typography | Each line enters from the left with staggered slide and exits to the right. | **C** | Partial (px-sized) | Med (Inter; lh 1.0 + overflow mask) | Low - no own timeline (X1) |
| `morph-text` | component | text, text-effect, typography | Gooey text morph — cycles through an editable word list using SVG threshold + GSAP-driven blur for a fluid,... | **C** | Partial (px-sized) | **High** (Figtree has no VI subset) | Low - SVG filter, Google Fonts link |
| `particle-text-dissolve` | component | motion-primitive, text-effects, particles | Text assembles from a seeded particle cloud (or dissolves into it): per-particle targets sampled once from the... | **C** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask; canvas text/measure) | Low - canvas2D |
| `perspective-marquee` | component | motion-primitive, typography | A 3D tilted marquee with depth feel as items roll toward the horizon. | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `scan-band` | component | motion-primitive, typography, scan | A diagonal distortion band sweeps once across a clean wordmark, revealing clipped red and cyan offsets only inside... | **C** | Yes (cq-elastic) | Med (Inter; lh 0.86 + overflow mask) | Low - GSAP/DOM |
| `shared-axis-y` | component | motion-primitive, typography | Per-word vertical shared-axis transition for sharp editorial swaps. | **C** | Likely (unitless/%) | Low (Inter) | Low - no own timeline (X1) |
| `shared-axis-z` | component | motion-primitive, typography | Scale-based shared-axis transition for focus shifts and context depth. | **C** | Likely (unitless/%) | Low (Inter) | Low - no own timeline (X1) |
| `shimmer-sweep` | component | text, shimmer, highlight | Animated light sweep across text or elements using a CSS gradient mask — ideal for AI accents and premium reveals | **C** | Likely (unitless/%) | Low (theme var / system) | Low - blend, no own timeline (X1) |
| `shutter-slam` | component | effect, motion-blur, shutter | One word thrown through six single-property beats under integrated shutter blur — two translate slams, a scale... | **C** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `staggered-fade-up` | component | video-primitive, motion-primitive, typography | Words fade in and slide up one after another with configurable delay. | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `streaming-text` | component | video-primitive, text-effect, ai | Words arrive the way an AI answer streams - in uneven bursts on a measured token rhythm, each word landing grey and... | **C** | Partial (px-sized) | Low (theme var / system) | Low - no own timeline (X1) |
| `text-stagger` | component | video-primitive, transition-primitive, transitions-dev-port | A transitions.dev-inspired text stagger primitive with enter, shimmer, and exit-ready words | **C** | Likely (unitless/%) | Low (theme var / system) | Low - no own timeline (X1) |
| `text-state-swap` | component | video-primitive, transition-primitive, transitions-dev-port | A text state swap primitive with outgoing blur and incoming lift | **C** | Partial (px-sized) | Low (theme var / system) | Low - no own timeline (X1) |
| `top-down-letters` | component | video-primitive, motion-primitive, typography | Letters descend from above in a pronounced staircase with zero blur. | **C** | Likely (unitless/%) | Med (Inter; lh 0.9 + overflow mask; char split) | Low - no own timeline (X1) |
| `tracking-in` | component | motion-primitive, text, reveal | A precise letter-spacing reveal for premium headings and interface labels | **C** | Likely (unitless/%) | Low (theme var / system) | Low - no own timeline (X1) |
| `typewriter` | component | video-primitive, motion-primitive, typography | Character-by-character text reveal with a deterministic blinking cursor. | **C** | Partial (px-sized) | Med (Inter; char split) | Low - no own timeline (X1) |
| `variable-axis-type` | component | typography, variable-font, kinetic-type | A locked one-line headline whose weight or width axis morphs into a decisive emphasis beat. | **C** | Yes (cq-elastic) | Med (Roboto Flex; lh 0.9 + overflow mask) | Low - Google Fonts link |
| `variable-font-flex` | component | motion-primitive, experiment, type | A word lands while its variable-font weight and width axes flex from hairline-condensed to black-wide with... | **C** | Yes (cq-elastic) | Med (Roboto Flex Variable; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `weight-wave` | block 1920x1080 | typography, kinetic-type, title | A crest of thickness travels along a headline: each character swells from light to black and leans forward as the... | **C** | No (16:9 px layout) | **High** (ships Recursive-wght-slnt-latin.woff2) | Low - canvas2D |
| `wordmark-tiles` | component | typography, wordmark, tiles | A wordmark resolves from deterministic color noise into correctly cropped glyph tiles through a spatially modulated... | **C** | Yes (cq-elastic) | **High** (glyph tile raster) | Low - GSAP/DOM |
| `matrix-decode` | component | motion-primitive, typography | Random scramble resolves left-to-right into the target text. | **X** | Partial (px-sized) | **High** (random Latin glyphs) | Low - no own timeline (X1) |
| `rgb-glitch-text` | component | motion-primitive, typography | RGB-offset text copies jitter briefly for a controlled glitch window. | **X** | Likely (unitless/%) | Low (Inter) | Low - no own timeline (X1) |
| `scramble-reveal` | component | motion-primitive, text-effects, scramble | A deterministic hacker-style text reveal that cycles fixed glyph rows and locks the target string from left to right. | **X** | Yes (cq-elastic) | **High** (Latin glyph rows) | Low - GSAP/DOM |
| `stitched-text-draw` | component | motion-primitive, experiment, type | Text drawn as thread stitches: a single-stroke display alphabet draws via attribute-driven dashoffset with... | **X** | Yes (cq-elastic) | **High** (single-stroke Latin alphabet) | Low - GSAP/DOM |

### 2. Captions and VO-synced word highlight (18 items: A 0, B 6, C 7, X 5)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `caption-camera-follow` | component | captions, caption-style, camera | One sentence written across a world far larger than the frame. | **B** | Likely (unitless/%) | Med (Helvetica Neue; lh 0.78 + overflow mask; uppercase) | Low - GSAP/DOM |
| `caption-editorial-emphasis` | component | captions, caption-style, editorial | Dual-font system with dramatic size contrast for emphasis words | **B** | Partial (px-sized) | Med (Inter, Playfair Display; lh 0.9 + overflow mask; canvas text/measure) | Low - canvas2D, Google Fonts link |
| `caption-highlight` | component | captions, caption-style, highlight | Red background sweep behind each active word, TikTok-style | **B** | Partial (px-sized) | Med (Montserrat; lh 1.0 + overflow mask; uppercase; canvas text/measure) | Low - canvas2D, Google Fonts link |
| `caption-pill-karaoke` | component | captions, caption-style, karaoke | Pill-shaped container with per-word karaoke color highlight | **B** | Partial (px-sized) | **High** (Poppins has no VI subset) | Low - canvas2D, Google Fonts link |
| `inline-highlight` | component | motion-primitive, text, highlight | A clean marker-style inline highlight that animates behind text using a CSS scale variable | **B** | Likely (unitless/%) | Low (theme var / system) | Low - no own timeline (X1) |
| `mk-callout-highlight` | block 1920x1080 | typography, karaoke, captions | A sentence whose word-by-word emphasis is driven by a single scalar — tween it to sync the highlight with a voiceover | **B** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `caption-clip-wipe` | component | captions, caption-style, wipe | Left-to-right clip-path wipe reveal per word | **C** | Likely (unitless/%) | **High** (Poppins has no VI subset) | Low - canvas2D, Google Fonts link |
| `caption-gradient-fill` | component | captions, caption-style, gradient | Gradient-clipped text with elastic bounce entrance | **C** | Likely (unitless/%) | Med (Montserrat; canvas text/measure) | Low - canvas2D, Google Fonts link |
| `caption-kinetic-slam` | component | captions, caption-style, kinetic | Full-screen single-word display with alternating entrance directions | **C** | Likely (unitless/%) | Med (Anton; lh 1.0 + overflow mask; uppercase; canvas text/measure) | Low - canvas2D, Google Fonts link |
| `caption-parallax-layers` | component | captions, caption-style, parallax | Behind-subject 3D text layering with vertical stretch effect | **C** | Partial (px-sized) | **High** (Instrument Serif has no VI subset) | Low - canvas2D, Google Fonts link |
| `caption-particle-burst` | component | captions, caption-style, particles | Keyword words trigger colored particle explosions | **C** | Partial (px-sized) | **High** (Outfit has no VI subset) | Low - canvas2D, Google Fonts link |
| `caption-texture` | component | captions, caption-style, texture | Flowing texture mask over large uppercase text — ships with 6 textures (lava, marble, metal, wood, concrete, rock),... | **C** | Likely (unitless/%) | Med (Anton; lh 1.0 + overflow mask; uppercase; canvas text/measure) | Low - canvas2D, Google Fonts link |
| `caption-weight-shift` | component | captions, caption-style, minimal | Elegant font-weight transition between caption lines | **C** | Partial (px-sized) | Med (Montserrat; lh 1.1 + overflow mask; canvas text/measure) | Low - canvas2D, Google Fonts link |
| `caption-emoji-pop` | component | captions, caption-style, emoji | Emoji integration with stroked text and horizontal squeeze entrance | **X** | Partial (px-sized) | **High** (Gabarito has no VI subset) | Low - canvas2D, Google Fonts link |
| `caption-glitch-rgb` | component | captions, caption-style, glitch | RGB chromatic aberration with CRT scanline overlay | **X** | Partial (px-sized) | Med (Space Grotesk; lh 0.96 + overflow mask; uppercase; canvas text/measure) | Low - canvas2D, Google Fonts link |
| `caption-matrix-decode` | component | captions, caption-style, matrix | Character scramble animation before text reveal | **X** | Likely (unitless/%) | **High** (Latin scramble glyphs) | Low - canvas2D, Google Fonts link |
| `caption-neon-accent` | component | captions, caption-style, neon | Multi-color neon glow accents with wiggle drift animation | **X** | Partial (px-sized) | Med (Montserrat; lh 1.1 + overflow mask; uppercase; canvas text/measure) | Low - canvas2D, Google Fonts link |
| `caption-neon-glow` | component | captions, caption-style, neon | Cyan and magenta neon glow with keyword accent colors | **X** | Partial (px-sized) | **High** (Outfit has no VI subset) | Low - canvas2D, Google Fonts link |

### 3. Emphasis, annotation and hand-drawn (23 items: A 5, B 9, C 8, X 1)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `marker-highlight` | component | motion-primitive, typography, emphasis | Display text settles in, then one hand-drawn marker stroke (highlight, circle, underline, or scribble) draws over... | **A** | Yes (cq-elastic) | Med (Inter; lh 1.14 + overflow mask) | Low - GSAP/DOM |
| `svg-stroke-trace` | component | motion-primitive, intro, reveal | An authored SVG path draws from its measured length, holds with subtle drift, and optionally fills when the path is... | **A** | Yes (cq-elastic) | n/a (no copy) | Low - GSAP/DOM |
| `vox-annotate` | component | motion-primitive, typography, annotation | The Vox-style annotate gesture: a keyword in a held sentence gets a hand-drawn marker while a thin connector draws... | **A** | Yes (cq-elastic) | Med (Inter, SF Mono; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `whiteboard-ink` | component | motion-primitive, intro, reveal | A whiteboard sketch draws one measured stroke at a time while a pen nib follows the active tip. | **A** | Yes (cq-elastic) | Med (Inter; lh 1.1 + overflow mask) | Low - GSAP/DOM |
| `yt-feather-highlight` | component | highlight, spotlight, effect | Dims the frame except a feathered ellipse; the hole's position and size are CSS variables, so helpers glide the... | **A** | Likely (unitless/%) | n/a (no copy) - demo Inter | Low - GSAP/DOM |
| `hw-arrow` | component | handwritten, annotation, arrow | Wobbled draw-on arrow with straight, gentle, and swoop curve poses, a four-way stroke texture matrix... | **B** | Partial (px-sized) | **High** (ships Caveat-700-latin.woff2) | Low - GSAP/DOM |
| `hw-boil` | component | handwritten, effect, annotation | Hand-drawn jitter that re-poses every N frames, as seek-safe helpers: pose derives from quantized timeline time... | **B** | Partial (px-sized) | n/a (no copy) - demo Caveat, Inter | Low - GSAP/DOM |
| `hw-box-label` | component | handwritten, annotation, overlay | Wobbled rounded rectangle draws on — across the authored stroke matrix (plain/soft/sharp/spray) — or drops in and... | **B** | Partial (px-sized) | **High** (ships Caveat-700-latin.woff2) | Low - GSAP/DOM |
| `hw-callout-circle` | component | handwritten, annotation, callout | Wobbled ellipse draws around a target with optional scribble fill and curved connector; the handwritten label pops... | **B** | Partial (px-sized) | **High** (ships Caveat-700-latin.woff2) | Low - GSAP/DOM |
| `hw-frame` | block 1920x1080 | handwritten, frame, media | Media in a hand-drawn border with corner doodles and a handwritten caption; the unit tilts slightly and boils... | **B** | No (16:9 px layout) | **High** (ships Caveat-700-latin.woff2) | Low - GSAP/DOM |
| `hw-pipeline` | block 1920x1080 | handwritten, diagram, data-viz | Wobbled boxes with handwritten labels joined by curved connectors, drawing on in sequence from a node list | **B** | No (16:9 px layout) | **High** (ships Caveat-700-latin.woff2) | Low - GSAP/DOM |
| `hw-scribble-transition` | block 1920x1080 | handwritten, transition, wipe | Overlay transition: scribble bands accumulate to cover the frame with a solid backstop, the host cuts beneath, and... | **B** | No (16:9 px layout) | Low (theme var / system) | Low - GSAP/DOM |
| `hw-underline` | component | handwritten, annotation, text-treatment | Hand-drawn squiggle underline, double-pass strikethrough, and bracket marks that draw on | **B** | Partial (px-sized) | **High** (ships Caveat-700-latin.woff2) | Low - GSAP/DOM |
| `marker-checklist-card` | component | motion-primitive, handwritten, checklist | A hand-lettered paper card: marker headline with an underline and a drawn ellipse around one word, then three... | **B** | Yes (cq-elastic) | **High** (ships permanent-marker-400.woff2, courier-prime-700.woff2) | Low - GSAP/DOM |
| `cursor-annotate` | component | cursor, motion-primitive, pen | A marker pen glides onto the frame and hand-draws a loose loop, an underline, or an arrow around a region, the ink... | **C** | Likely (unitless/%) | Low (theme var / system) | Low - GSAP/DOM |
| `hw-path-text` | block 1920x1080 | handwritten, typography, path | Handwriting flowing along any SVG path with a per-character reveal; the path is the only geometry input | **C** | No (16:9 px layout) | **High** (ships Caveat-700-latin.woff2) | Low - GSAP/DOM |
| `hw-text-cloud` | block 1920x1080 | handwritten, speech-bubble, overlay | Hand-drawn speech bubble with a positionable tail: outline draws on, paper fill fades in, handwritten text types per... | **C** | No (16:9 px layout) | **High** (ships Caveat-700-latin.woff2) | Low - GSAP/DOM |
| `hw-title` | block 1920x1080 | handwritten, typography, title-card | Handwritten display text with a scalar-driven word-by-word highlight sweep and a seeded squiggle underline sized to... | **C** | No (16:9 px layout) | **High** (ships Caveat-700-latin.woff2) | Low - GSAP/DOM |
| `outline-draw` | component | motion-primitive, effects, outline | A rounded outline that proves a callout by drawing clockwise as a hollow conic-gradient border with a clean closure. | **C** | Yes (cq-elastic) | Low (theme var / system) | Low - GSAP/DOM |
| `svg-line-draw-loader` | component | video-primitive, advanced-motion, anime-inspired | An Anime.js-style path drawing loader implemented as a seekable GSAP stroke timeline. | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `tracing-beam` | component | motion-primitive, product-demo, attention | A glowing dash follows one SVG path through three UI elements, lifting and brightening each element in sequence. | **C** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.05 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - SVG filter |
| `yt-circle-pointer` | component | annotation, countdown, overlay | Draw-on annotation ellipse around a target plus a countdown chip that pulses each tick | **C** | Partial (px-sized) | Low (Inter) | Low - GSAP/DOM |
| `hw-write-title` | block 1920x1080 | handwritten, typography, title-card | True glyph write-on: filled Caveat letterforms revealed by baked per-glyph centerline strokes traced in real stroke... | **X** | No (16:9 px layout) | **High** (baked Latin glyph centerlines) | Low - GSAP/DOM |

### 4. Data, stats and charts (18 items: A 3, B 3, C 7, X 5)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `chart-story` | component | motion-primitive, proof, stats | One chart builds from data in reading order and lands the exact supplied values: staggered bars, a left-to-right... | **A** | Yes (cq-elastic) | Med (Inter, SF Mono; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `conic-progress-ring` | component | data, progress, ring | A token-driven conic progress ring whose angular fill and center count settle together from one registered percentage. | **A** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `count-up` | component | motion-primitive, proof, stats | A token-native stat counter that eases between values, counting up or down, and lands with a restrained scale pulse. | **A** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `mk-line-graph` | block 1920x1080 | data-viz, chart, graph | One or two SVG series draw on with dots popping and value labels riding the draw front; dim baseline axis, x-labels,... | **B** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `mk-progress-stat` | block 1920x1080 | data-viz, stat, minimal | Big-numeral statistic with count-up, label, thin progress track filling to value/max, and caption; light and dark... | **B** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `mk-specs-list` | block 1920x1080 | data-viz, list, minimal | Left-aligned specs/traits checklist over footage or a board: rows slide in staggered with an accent underline sweep;... | **B** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `animated-bar-chart` | component | data | A compact data card with deterministic bar growth and value callouts. | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `bar-chart-race` | block 1920x1080 | data, chart, statistics | Ranked bars grow and overtake each other as a time series advances, with the axis rescaling as values climb and the... | **C** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |
| `data-chart` | block 1920x1080 | data, chart, statistics | Animated bar + line chart with staggered reveal, NYT-style typography, and value labels | **C** | No (16:9 px layout) | **High** (Libre Baskerville has no VI subset) | Low - Google Fonts link |
| `decline-chart` | component | motion-primitive, data, chart | A metric line draws downward as its value counts down and the ambient background darkens in lockstep. | **C** | Yes (cq-elastic) | Med (Inter; lh 0.8 + overflow mask; uppercase) | Low - GSAP/DOM |
| `mk-usage-arc` | component | data-viz, gauge, minimal | Thin circular gauge that draws on while its percentage counts up; one helper call drives both | **C** | Partial (px-sized) | Low (Inter) | Low - GSAP/DOM |
| `number-pop-in` | component | video-primitive, transition-primitive, transitions-dev-port | A transitions.dev-inspired digit pop-in with blur, lift, and staggered value reveal | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `star-rating-fill` | component | data, rating, stars | A token-driven star row whose colored layer sweeps to a rating, preserves the fractional final star, and can count... | **C** | Yes (cq-elastic) | Med (theme var / system; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `avatar-cloud` | component | effects, avatars, community | Lettermark avatars populate a loose elliptical cloud while fine SVG links draw between the community and its central... | **X** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |
| `logo-wall` | component | data, logos, social-proof | A trusted-by wall of placeholder lettermark logos that fades and scales into place with a deterministic per-cell... | **X** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |
| `oscilloscope-trace` | block 1920x1080 | instrument, data, showcase | CRT oscilloscope beam sweeping a waveform across a 10x8 graticule, with closed-form phosphor persistence: the tail... | **X** | No (16:9 px layout) | Low (JetBrains Mono) | Low - canvas2D |
| `trust-strip` | component | motion-primitive, proof, trust | A monochrome trust row of wide-tracked mono wordmarks that fade in with an opacity-only left-to-right stagger, then... | **X** | Yes (cq-elastic) | Med (SF Mono; lh 1.0 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `week-in-merges` | block 1080x1350 | data, chart, ranking | Each author's avatar bounces across their row at a speed set by how many pull requests they merged | **X** | Partial (square/4:5) | Med (Inter; lh 1.05 + overflow mask; uppercase) | Low - GSAP/DOM |

### 5. Maps and geography (8 items: A 0, B 1, C 2, X 5)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `world-map` | block 1920x1080 | data, map, geography | Animated world choropleth with country-by-country reveal, tooltip labels, and rotating globe inset — D3 Natural... | **B** | No (16:9 px layout) | Low (Inter) | Med - network fetch (topojson CDN), d3 CDN, backdrop-filter, Google Fonts link |
| `north-korea-locked-down` | block 1920x1080 | showcase, map, annotation | Realistic map zoom into North Korea with a red scribble circle, locked-down pop-up label, and reddish editorial wash. | **C** | No (16:9 px layout) | Med (Helvetica Neue; lh 0.9 + overflow mask; uppercase) | Low - blend |
| `nyc-paris-flight` | block 1920x1080 | showcase, travel, map | Apple-style realistic map animation with a plane flying from New York to Paris, marker circle, landing pop, and... | **C** | No (16:9 px layout) | Med (Helvetica Neue; lh 0.92 + overflow mask) | Low - backdrop-filter, blend |
| `spain-map` | block 1920x1080 | data, map, geography | Animated Spain choropleth by autonomous community with staggered reveals and gradient legend — D3 conic conformal... | **X** | No (16:9 px layout) | Low (Inter) | Med - network fetch (topojson CDN), d3 CDN, Google Fonts link |
| `us-map` | block 1920x1080 | data, map, geography | Animated US choropleth map with staggered state reveals, value labels, and gradient legend — pure inline SVG with GSAP | **X** | No (16:9 px layout) | Low (Inter) | Med - network fetch (topojson CDN), d3 CDN, Google Fonts link |
| `us-map-bubble` | block 1920x1080 | data, map, geography | Animated US bubble map with proportional city markers, value callouts, and connection lines — composable with us-map | **X** | No (16:9 px layout) | Low (Inter) | Med - network fetch (topojson CDN), d3 CDN, Google Fonts link |
| `us-map-flow` | block 1920x1080 | data, map, geography | Animated connection arcs between US cities over a base map — composable origin-destination flow visualization | **X** | No (16:9 px layout) | Low (Inter) | Med - network fetch (topojson CDN), d3 CDN, SVG filter, Google Fonts link |
| `us-map-hex` | block 1920x1080 | data, map, geography | Animated hexagonal tile grid map — each state as an equal-weight hex with data fill and abbreviation label | **X** | No (16:9 px layout) | Low (Inter) | Low - Google Fonts link |

### 6. Diagrams, lists, structure and compare (32 items: A 5, B 9, C 17, X 1)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `comparison-split` | component | prop, ui-props, compare | Two full-bleed panels compare before and after states as a persistent divider wipes the vivid after layer over the... | **A** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |
| `constellation-hub` | component | motion-primitive, feature-tour, hub | Feature nodes brighten in narration order as real-length SVG connectors draw outward from a fixed central hub, then... | **A** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `grid-card-assemble` | component | motion-primitive, layout, grid | N capability cards (thin-line icon that draws on, mono label, optional muted body) stagger-assemble into a grid or... | **A** | Yes (cq-elastic) | Med (SF Mono, Segoe UI; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `radial-surround` | component | motion-primitive, problem-setup, radial | Labeled hairline chips assemble around a centered subject on an elliptical ring, then optionally converge inward... | **A** | Yes (cq-elastic) | Med (SF Mono; lh 1.0 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `testimonial-proof-card` | component | motion-primitive, proof, testimonial | A quote card whose testimonial reveals per-line through a soft mask, with an avatar disc (initials default, image... | **A** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 0.6 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `before-after-wipe` | component | prop, ui-props, compare | Two full-bleed content slots compare before and after states as a persistent divider wipes the after layer over the... | **B** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |
| `flowchart-vertical` | block 1440x2560 | diagram, flowchart, interactive | Portrait animated decision tree with SVG connectors, sticky-note nodes, cursor interaction, and typing correction | **B** | Yes (native 9:16) | Low (Inter) | Low - Google Fonts link |
| `focus-swap` | component | effect, ui-props, focus | Moves attention between two side-by-side cards as one recedes with scale, blur, and dimming while the other advances... | **B** | Yes (cq-elastic) | Med (theme var / system; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |
| `gloss-sweep` | component | motion-primitive, celebration, gloss | A card lands with a restrained slam, catches one diagonal specular gloss, and holds perfectly still. | **B** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `offset-path-traveler` | component | motion-primitive, product-demo, path | A slotted traveler follows an authored path with tangent rotation, curved entry, and curved exit. | **B** | Yes (cq-elastic) | n/a (no copy) - demo Inter | Low - GSAP/DOM |
| `pendulum-swing` | component | motion-primitive, physics, swing | Content hangs from a fixed pivot and swings into rest with gravity-damped oscillation, like a hanging sign settling... | **B** | Likely (unitless/%) | Low (Inter) | Low - no own timeline (X1) |
| `split-tilt-cards` | component | motion-primitive, layout, compare | Two equal-weight cards arrive from opposite wings with mirrored rotateY book-open tilts under one shared... | **B** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.0 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `spring-stack-shuffle` | component | motion-primitive, product-demo, physics | A stack of 3 to 5 slotted cards reshuffles on cues: the back card throws over the top and lands at the front with... | **B** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.0 + overflow mask; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `stagger-cascade` | component | effects, grid, stagger | A responsive grid of tile cards that fades and travels into place with an evenly spaced per-item GSAP stagger. | **B** | Yes (cq-elastic) | Med (theme var / system; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `arc-motion-path` | component | video-primitive, motionpath, gsap-plugin | A GSAP MotionPath primitive that flies a callout along a curved arc with autorotation. | **C** | Partial (px-sized) | n/a (no copy) - demo Inter | Low - no own timeline (X1) |
| `beat-timeline` | component | orchestration, transitions, sequencing | A paused master-timeline orchestration spine that pins titled beat rows to evenly spaced named labels. | **C** | Yes (cq-elastic) | Med (theme var / system; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `camera-rig-depth-stack` | component | advanced-motion, hyperframes-native | A 3D camera-rig-style card stack with depth, parallax, and focus shift. | **C** | Partial (px-sized) | Low (Inter) | Low - backdrop-filter, no own timeline (X1) |
| `echo-trail` | component | motion-primitive, demonstrate, trail | A moving element renders with N ghosted copies of itself at t minus i times delta, opacity stepped down per ghost;... | **C** | Yes (cq-elastic) | n/a (no copy) - demo Inter | Low - GSAP/DOM |
| `exploded-stack` | block 1920x1080 | 3d-object, three-js, webgl | Isometric layer plates explode apart with a label beside each layer, hold, then collapse back into one stack. | **C** | No (16:9 px layout) | Low (ES Inter) | Med - three.js, canvas2D |
| `facet-morph` | component | motion-primitive, intro, morph | A faceted low-poly mass of 36 triangles continuously reshapes between three authored silhouettes (blob, mark, badge)... | **C** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `flowchart` | block 1920x1080 | diagram, flowchart, interactive | Animated decision tree with SVG connectors, sticky-note nodes, cursor interaction, and typing correction | **C** | No (16:9 px layout) | Low (Inter) | Low - Google Fonts link |
| `icon-morph-beat` | component | motion-primitive, product-demo, icon | An icon morphs between authored state silhouettes, shifts to an accent color, and marks completion with one... | **C** | Yes (cq-elastic) | Low (theme var / system) | Low - GSAP/DOM |
| `keyframe-scrub-stack` | component | advanced-motion, anime-inspired, hyperframes-native | A keyframe-sequenced stack of cards with offset timing and easing presets. | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `locked-nucleus-orbit` | component | motion-primitive, intro, reveal | A fixed center nucleus anchors deterministic satellite orbits that settle into a composed lockup. | **C** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.0 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `overwhelm-surround` | component | effects, agitate, overwhelm | Tasks, tabs, pings, and notification bubbles accelerate inward around a calm central subject, turning overload into... | **C** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `physical-exit` | component | motion-primitive, exit, momentum | A card exits with physical momentum in toss, drop, or slide mode, carrying acceleration and rotation through the... | **C** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `separator` | component | video-primitive, separator, layout | A one-pixel structural separator with horizontal and vertical variants plus a seek-safe progress reveal | **C** | Partial (px-sized) | Low (theme var / system) | Low - no own timeline (X1) |
| `spring-pop` | component | motion-primitive, effects, spring | A badge pops in from a visible near-rest scale, overshoots full size once, and settles cleanly. | **C** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `stagger-lattice` | component | advanced-motion, anime-inspired, hyperframes-native | A staggered grid reveal inspired by Anime.js v4 stagger utilities, implemented with GSAP for HyperFrames. | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `stop-motion-cadence` | component | motion-primitive, time-law, stop-motion | The stepped-time law as a demo primitive: one driver quantizes timeline time to floor(t * fps) / fps and feeds ALL... | **C** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `testimonial-card` | component | prop, ui-props, testimonial | Reveals a customer quote at reading pace, then settles its avatar, author name, and handle beneath as a clean proof... | **C** | Yes (cq-elastic) | Med (theme var / system; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `state-chip-rail` | component | motion-primitive, product-demo, state-machine | A rail of mono status chips advances a seek-safe data-state snap machine on a cue schedule: active chip ink on... | **X** | Yes (cq-elastic) | Med (SF Mono; lh 1.0 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |

### 7. Camera, depth and reframing (15 items: A 3, B 5, C 4, X 3)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `camera-shake` | component | camera, shake, handheld | Procedural handheld, telephoto and rig camera shake for any wrapper: nine measured profiles with per-lens... | **A** | Partial (px-sized) | n/a (no copy) - demo Helvetica Neue, Menlo | Low - GSAP/DOM |
| `scroll-camera-story` | component | camera, scroll, parallax | A compressed forced-scroll cinematic pass: a tall scene of slotted sections travels past the camera top to bottom,... | **A** | Yes (cq-elastic) | Med (SF Mono; lh 1.0 + overflow mask; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `yt-camera-move` | component | camera, zoom, effect | Dynamic zoom, slide, and 3D tilt-pan helpers for any wrapper (video, include, card) with cubic-easing defaults and... | **A** | Partial (px-sized) | n/a (no copy) - demo Inter | Low - backdrop-filter |
| `drift-hold` | component | motion-primitive, camera, ambient | A centered content card stays subtly alive through loop-exact rotation, scale breathing, and a slow light sweep. | **B** | Yes (cq-elastic) | n/a (no copy) - demo Inter | Low - GSAP/DOM |
| `focus-rack` | component | motion-primitive, camera, focus | Focus shifts once between two cards at different apparent depths through synchronized blur, dimming, scale, and... | **B** | Yes (cq-elastic) | Med (Inter; lh 0.94 + overflow mask; uppercase) | Low - GSAP/DOM |
| `pan-stations` | component | camera, pan, stations | A lateral camera move across a continuous row of labeled feature stations, with a steady dwell at each stop before... | **B** | Yes (cq-elastic) | Med (Inter; lh 0.98 + overflow mask; uppercase) | Low - GSAP/DOM |
| `pull-back-reveal` | component | motion-primitive, camera, pull-back | A tight stat detail holds, then one decelerating camera pull-back reveals the headline and supporting cards that... | **B** | Yes (cq-elastic) | Med (Inter; lh 0.9 + overflow mask; uppercase) | Low - GSAP/DOM |
| `push-in` | component | motion-primitive, camera, push-in | A centered headline gains focus through one slow, continuous camera push and a gentle fade out. | **B** | Yes (cq-elastic) | Med (Inter; lh 0.94 + overflow mask) | Low - GSAP/DOM |
| `camera-dolly-zoom` | block 1920x1080 | camera, depth, 3d | Camera tracks toward or away from the subject while the field of view changes the opposite way, so the subject holds... | **C** | No (16:9 px layout) | Med (Inter; uppercase) | Low - GSAP/DOM |
| `motion-blur` | component | effect, motion-blur, shutter | After Effects-style motion blur — integrates each element over a shutter window (shutter angle, phase, samples per... | **C** | Likely (unitless/%) | n/a (no copy) | Low - GSAP/DOM |
| `rack-focus` | block 1920x1080 | webgl, shader, camera | A focus pull with real aperture bokeh: the focal plane travels from a near subject to a far one, so one resolves as... | **C** | No (16:9 px layout) | Low (theme var / system) | Med - WebGL |
| `ui-focus-zoom` | component | camera, product-demo, zoom | A full app surface establishes with one settle, then the camera zooms and pans to an anchored region on its cue and... | **C** | Yes (cq-elastic) | Low (theme var / system) | Low - GSAP/DOM |
| `cursor-zoom-follow` | component | cursor, camera, zoom | Screen-recording auto-zoom: the camera pushes in toward each upcoming click, trails the cursor on a smooth spring,... | **X** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `filmed-screen` | component | filmed, screen, monitor | Your scene, filmed off a screen: perspective, depth of field that follows an element you name, LED sub-pixels and... | **X** | Likely (unitless/%) | Low (theme var / system) | High - html-in-canvas (Chrome flag), WebGL, canvas2D |
| `parallax-device-dive` | component | motion-primitive, camera, device | A canonical phone rises into view before the camera pushes through its screen and layered app UI expands to fill the... | **X** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |

### 8. Media framing and image treatments (15 items: A 1, B 5, C 6, X 3)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `ink-bleed-reveal` | component | motion-primitive, texture, reveal | Liquid ink blooms through paper under a gooey blur-plus-threshold filter, merges, then contracts as a crisp slotted... | **A** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - canvas2D, SVG filter, blend |
| `cinemagraph` | block 1920x1080 | effect, cinemagraph, photo | A still photograph with one living region: the frame is frozen while a single feathered window keeps moving - here,... | **B** | No (16:9 px layout) | n/a (no copy) | Low - canvas2D |
| `freeze-frame-dressing` | block 1920x1080 | freeze-frame, cutout, scrapbook | Timeline-driven paper, tape, and flash dressing for a freeze-frame or background-removed subject | **B** | No (16:9 px layout) | n/a (no copy) | Low - blend |
| `grade-split-reveal` | component | color-grading, media, compare | The same picture twice, one flat and one finished, with a hard edge sweeping between them. | **B** | Partial (px-sized) | Med (Helvetica Neue; uppercase) | Low - GSAP/DOM |
| `mk-placeholder-grid` | block 1920x1080 | placeholder, media, grid | N-up rounded-corner media grid (2-up, 3-up, 4-up, 3x2, hero plus two): per-cell inside-scale framing, staggered... | **B** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `particle-image-reveal` | component | motion-primitive, intros-reveals, particles | A seeded deterministic particle field converges and settles while a slotted image reveals beneath it, the trail... | **B** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - canvas2D |
| `camcorder-hud` | block 1920x1080 | camcorder, camera, recording | Responsive REC, battery, editable date placeholder, and timeline-driven counter overlay for creator-camera and... | **C** | No (16:9 px layout) | Low (theme var / system) | Low - GSAP/DOM |
| `light-sweep-pass` | component | motion-primitive, overlay, light | A traveling key light re-shades a slotted scene: a soft diagonal gradient band crosses the frame once while every... | **C** | Yes (cq-elastic) | n/a (no copy) - demo Inter | Low - blend |
| `ordered-dither-pass` | component | motion-primitive, experiment, texture | Bayer-matrix ordered dithering quantizes a slotted scene (rasterized once at mount): the image emerges from pure... | **C** | Yes (cq-elastic) | n/a (no copy) - demo Inter | Low - canvas2D |
| `slit-scan-reveal` | component | motion-primitive, time, slit-scan | The frame's rows sample an authored subject at offset times: a canvas painter draws row slices of one pure position... | **C** | Yes (cq-elastic) | n/a (no copy) - demo Inter | Low - canvas2D |
| `yt-screen-warp` | component | effect, overlay, texture | Grid, scanline, vignette, and sheen overlay plus a 3D-warp wrapper class that makes footage read as if playing on a... | **C** | Partial (px-sized) | n/a (no copy) - demo Inter | Low - GSAP/DOM |
| `yt-vertical-fill` | block 1920x1080 | placeholder, vertical, media | Portrait media filling a widescreen frame via blurred-scale, mirror, or copy side fills; grid texture and foreground... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `ascii-render-pass` | component | motion-primitive, experiment, texture | A slotted scene renders as live ASCII: a canvas samples the source's luminance grid (rasterized once at mount) and... | **X** | Yes (cq-elastic) | n/a (no copy) - demo SF Mono | Low - canvas2D |
| `segmentation-flood` | component | motion-primitive, product-demo, ai | Machine-vision read of a slotted subject: translucent accent segmentation masks flood on in quantized scanline... | **X** | Yes (cq-elastic) | Med (Inter, SF Mono; uppercase; mono/system fallback lacks VI) | Low - canvas2D |
| `telemetry-hud` | component | motion-primitive, product-demo, hud | Quiet mono debug-HUD readouts frame a slotted subject: corner brackets draw on, label:value lines tick their values... | **X** | Yes (cq-elastic) | Med (SF Mono; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |

### 9. Transitions and seams (DOM/canvas) (24 items: A 6, B 5, C 11, X 2)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `cut-the-curve` | component | transition, directional-cut, velocity-match | A velocity-matched directional hard cut: the outgoing subject accelerates with power4.in, swaps at peak velocity,... | **A** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `fade-through` | component | motion-primitive, transition, fade | A calm transition primitive that fades one layer out, passes through a wash, and reveals the next layer | **A** | Likely (unitless/%) | n/a (no copy) | Low - no own timeline (X1) |
| `halftone-dissolve` | component | motion-primitive, transition, texture | Scene A dissolves into scene B through a growing halftone dot field: accent ink dots pop onto a fixed grid... | **A** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - canvas2D |
| `paper-collage-reveal` | component | collage, scrapbook, torn paper | A scrapbook patchwork of torn paper scraps, each with its own texture and tilt, flutters away in a staggered scatter... | **A** | Yes (cq-elastic) | Med (Inter; uppercase) | Low - SVG filter, blend |
| `torn-paper-rip` | component | torn paper, paper rip, paper tear | A fibrous paper tear runs across the frame: the torn sheet shows its white paper core along the edge and lifts away... | **A** | Yes (cq-elastic) | Med (Inter; uppercase) | Low - SVG filter, blend |
| `whip-pan-cut` | component | transition, whip-pan, motion-blur | A full-frame whip pan: scene A whips off laterally with capped directional motion blur while scene B enters in the... | **A** | Yes (cq-elastic) | Low (Inter) | Low - SVG filter |
| `curtain-reveal` | component | curtain, stage reveal, transition | Two pleated stage curtains gather outward from center, the way real velvet bunches at the tieback, revealing the... | **B** | Yes (cq-elastic) | n/a (no copy) - demo Inter | Low - blend |
| `editorial-flash-overlay` | block 1920x1080 | flash, editorial, social | Finite neutral-warm light layers for a seek-safe camera-flash cut or social reveal | **B** | No (16:9 px layout) | n/a (no copy) | Low - blend |
| `iris-reveal` | component | transition, iris, circle-reveal | A circle clip-path opens from an authored origin revealing state B over state A in one confident pass, then holds on B. | **B** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `morph-swap` | component | transition, morph, swap | Two slotted siblings stacked at one shared center: A holds, then condenses or reshapes into B on a shared 50% 50%... | **B** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `organic-light-leak-overlay` | block 1920x1080 | light-leak, film, memory | Finite CSS light-leak overlay for memory beats and motivated transitions | **B** | No (16:9 px layout) | n/a (no copy) | Low - blend |
| `beat-freeze-cut` | block 1920x1080 | transition, music, beat-driven | A beat-driven speed ramp, freeze-frame hit, and hard-cut sequence for music-led promos and montages. | **C** | No (16:9 px layout) | Med (Inter; lh 0.92 + overflow mask; uppercase) | Low - backdrop-filter, blend, Google Fonts link |
| `directional-wipe` | component | transition-primitive | A directional scene push that slides one panel over another. | **C** | Partial (px-sized) | Low (Inter) | Low - blend, no own timeline (X1) |
| `grid-pixelate-wipe` | component | transition, wipe, grid | Transition effect where the screen dissolves into a grid of squares that fade out with staggered timing — use... | **C** | Likely (unitless/%) | Low (theme var / system) | Low - no own timeline (X1) |
| `match-cut` | component | motion-primitive, transition, match-cut | A circle accelerates into a hard single-frame scene swap, matches the incoming circle exactly, and continues into a... | **C** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.0 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `mk-clone-wall-transition` | block 1920x1080 | transition, typography, wipe | Overlay transition: a tiled word wall covers the frame, inverts via difference blending, and clears — hard-cut the... | **C** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask) | Low - blend |
| `page-slide` | component | video-primitive, transition-primitive, transitions-dev-port | A transitions.dev-inspired page slide primitive with outgoing and incoming panels | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `panel-reveal` | component | transition-primitive, transitions-dev-port, panel | A panel reveal primitive with height expansion and content fade | **C** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `parallax-unzoom` | component | transition, reveal, unzoom | Reveal transition — focus card scales down from full frame as siblings parallax in to form a grid (reverse of... | **C** | Likely (unitless/%) | Low (theme var / system) | Low - no own timeline (X1) |
| `parallax-zoom` | component | transition, zoom, parallax | Center card scales up to fill the frame while siblings parallax outward — inspired by the eBay Playbook hero transition | **C** | Likely (unitless/%) | Low (theme var / system) | Low - no own timeline (X1) |
| `rubber-band-bumper` | component | motion-primitive, transition, rubber-band | An outgoing panel pulls against increasing resistance, holds at tension, then snaps past an edge with overshoot as... | **C** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 0.95 + overflow mask; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `zoom-through-transition` | component | transition-primitive | A transition that zooms through a focal card into the next scene. | **C** | Yes (cq-elastic) | Low (Inter) | Low - blend |
| `ascii-trail-reveal` | component | motion-primitive, intro, reveal | An authored S-curve sweeps through a deterministic ASCII grid, flipping cells away to reveal a labeled panel. | **X** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 0.96 + overflow mask; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `chromatic-aberration-wipe` | component | video-primitive, transition-primitive | A fast slide wipe with RGB channel split on peak frames. | **X** | Partial (px-sized) | Low (Inter) | Low - blend, no own timeline (X1) |

### 10. Shader transition blocks (WebGL showcase) (14 items: A 0, B 3, C 8, X 3)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `cross-warp-morph` | block 1920x1080 | transition, shader | Shader transition with cross-warped morphing | **B** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `domain-warp-dissolve` | block 1920x1080 | transition, shader | Shader transition with fractal noise domain warping | **B** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `light-leak` | block 1920x1080 | transition, shader | Shader transition with cinematic light leak overlay | **B** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `chromatic-radial-split` | block 1920x1080 | transition, shader | Shader transition with chromatic aberration radial split | **C** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `cinematic-zoom` | block 1920x1080 | transition, shader | Shader transition with dramatic zoom blur | **C** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `flash-through-white` | block 1920x1080 | transition, shader | Shader transition with white flash crossfade | **C** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `gravitational-lens` | block 1920x1080 | transition, shader | Shader transition with gravitational lensing distortion | **C** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `ridged-burn` | block 1920x1080 | transition, shader | Shader transition with ridged turbulence burn effect | **C** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `ripple-waves` | block 1920x1080 | transition, shader | Shader transition with concentric ripple wave distortion | **C** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `sdf-iris` | block 1920x1080 | transition, shader | Shader transition with signed distance field iris reveal | **C** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `whip-pan` | block 1920x1080 | transition, shader | Shader transition simulating a fast camera whip pan | **C** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `glitch` | block 1920x1080 | transition, shader | Shader transition with digital glitch artifacts | **X** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `swirl-vortex` | block 1920x1080 | transition, shader | Shader transition with swirling vortex distortion | **X** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |
| `thermal-distortion` | block 1920x1080 | transition, shader | Shader transition with heat haze thermal distortion | **X** | No (16:9 px layout) | n/a (no copy) - demo Space Mono, Bebas Neue, JetBrains Mono | Med - WebGL, canvas2D, Google Fonts link |

### 11. Transition galleries (showcase blocks) (13 items: A 0, B 0, C 13, X 0)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `transitions-3d` | block 1920x1080 | transition, showcase | Showcase of 3D perspective flip and rotate transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-blur` | block 1920x1080 | transition, showcase | Showcase of blur-based transitions between scenes | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-cover` | block 1920x1080 | transition, showcase | Showcase of cover/uncover slide transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-destruction` | block 1920x1080 | transition, showcase | Showcase of destructive break-apart transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - canvas2D |
| `transitions-dissolve` | block 1920x1080 | transition, showcase, crossfade | Showcase of dissolve and fade transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-distortion` | block 1920x1080 | transition, showcase | Showcase of warp and distortion transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - blend |
| `transitions-grid` | block 1920x1080 | transition, showcase | Showcase of grid-based tile transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-light` | block 1920x1080 | transition, showcase | Showcase of light-based glow and flash transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-mechanical` | block 1920x1080 | transition, showcase | Showcase of mechanical shutter and iris transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-other` | block 1920x1080 | transition, showcase | Showcase of miscellaneous creative transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-push` | block 1920x1080 | transition, showcase | Showcase of push and slide transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-radial` | block 1920x1080 | transition, showcase | Showcase of radial wipe and reveal transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |
| `transitions-scale` | block 1920x1080 | transition, showcase | Showcase of scale and zoom transitions | **C** | No (16:9 px layout) | n/a (no copy) - demo Segoe UI | Low - GSAP/DOM |

### 12. Backgrounds, atmosphere and overlays (16 items: A 1, B 4, C 10, X 1)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `vignette` | component | vignette, overlay, cinematic | Cinematic radial vignette overlay using a pure-CSS gradient — darkens the edges to pull focus toward the center | **A** | Likely (unitless/%) | n/a (no copy) | Low - no own timeline (X1) |
| `aurora-drift` | component | motion-primitive, background, aurora | Three soft accent-derived aurora fields drift in an exact ambient loop over a deep base and faint vignette. | **B** | Yes (cq-elastic) | n/a (no copy) | Low - blend |
| `grain-field` | component | motion-primitive, background, grain | A clearly visible accent-tinted dot field drifts over a subtle luminance gradient in an exact ambient loop. | **B** | Yes (cq-elastic) | n/a (no copy) | Low - GSAP/DOM |
| `mk-background` | block 1920x1080 | background, gradient, minimal | Procedural soft-blob gradient backdrop in a minimalist presentation style: two radial blobs drifting over a base... | **B** | No (16:9 px layout) | n/a (no copy) - demo Inter | Low - GSAP/DOM |
| `starfield` | block 1920x1080 | starfield, night-sky, stars | Seek-safe night-sky overlay: sparse or dense stars in three size tiers that twinkle and drift in two parallax... | **B** | No (16:9 px layout) | n/a (no copy) | Low - GSAP/DOM |
| `beat-pulse-background` | component | motion-primitive, background, beat | An accent-derived backdrop pulses its glow intensity and saturation on a deterministic, supplied beat grid. | **C** | Likely (unitless/%) | n/a (no copy) | Low - blend |
| `cosmic-orb` | block 1920x1080 | webgl, shader, background | An iridescent soap-bubble planet: a slowly spinning sphere of nebula bands, dust lanes and twinkling stars wrapped... | **C** | No (16:9 px layout) | n/a (no copy) | Med - WebGL |
| `dynamic-grid` | component | video-primitive, motion-primitive, background | A responsive animated grid background driven by CSS variables for SaaS, code, and data scenes | **C** | Partial (px-sized) | n/a (no copy) | Low - no own timeline (X1) |
| `grain-overlay` | component | texture, grain, overlay | Animated film grain texture overlay using CSS keyframes — adds warmth and analog character to any composition | **C** | Likely (unitless/%) | n/a (no copy) | Med - CSS @keyframes (not seek-safe), SVG filter, no own timeline (X1) |
| `halftone-field` | block 1920x1080 | webgl, shader, background | A full-bleed halftone light field: a grid of dots whose size and colour track a slow flowing simplex-noise field, so... | **C** | No (16:9 px layout) | n/a (no copy) | Med - WebGL |
| `mesh-gradient-bg` | component | effect | A render-safe mesh gradient using animated radial layers. | **C** | Partial (px-sized) | n/a (no copy) - demo Inter | Low - blend, no own timeline (X1) |
| `snow` | block 1920x1080 | snow, snowfall, winter | Seek-safe falling-snow overlay: sparse or dense flakes drift down with size, speed and opacity correlated per flake... | **C** | No (16:9 px layout) | n/a (no copy) | Low - GSAP/DOM |
| `spiral-galaxy` | block 1920x1080 | hero, space, particles | A spiral galaxy seen from outside, turning with real differential rotation: inner stars orbit faster than outer... | **C** | No (16:9 px layout) | n/a (no copy) | Med - three.js, blend |
| `vfx-anamorphic-flare` | block 1920x1080 | vfx, background, showcase | A drifting field of bright points, each one throwing the long horizontal blue-violet streak a real anamorphic cinema... | **C** | No (16:9 px layout) | n/a (no copy) | Low - canvas2D |
| `yt-lcd-background` | block 1920x1080 | background, texture, creator | Textured paper board: scanlines with slow drift, optional pixel grid, static grain, and display text with a... | **C** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - SVG filter |
| `gallery-tunnel` | block 1920x1080 | webgl, 3d, background | An infinite corridor of panels: a square tunnel receding to a vanishing point, its floor, ceiling and walls tiled... | **X** | No (16:9 px layout) | n/a (no copy) | Low - GSAP/DOM |

### 13. WebGPU shader blocks (shaders.com library) (36 items: A 0, B 0, C 3, X 33)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `godrays` | block 1920x1080 | webgpu, webgpu-shader, background | Rays of light fan out from a corner and drift across a deep blue field. | **C** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `marble` | block 1920x1080 | webgpu, webgpu-shader, background | Ink-dark veins wind through white in a marbled pattern that slowly shifts. | **C** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `sun-burst` | block 1920x1080 | webgpu, webgpu-shader, background | Cream and black rays fan out from the centre and slowly turn. | **C** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `aurora` | block 1920x1080 | webgpu, webgpu-shader, background | Green and violet aurora curtains ripple across a night sky. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `blob` | block 1920x1080 | webgpu, webgpu-shader, background | A soft coral and pink blob with a warm highlight slowly changes shape on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `chrome-orb` | block 1920x1080 | webgpu, webgpu-shader, object | A mirror-chrome orb reflects a bright studio light, on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `color-wheel` | block 1920x1080 | webgpu, webgpu-shader, background | A wide gradient slides slowly through the colours of the rainbow. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `falling-lines` | block 1920x1080 | webgpu, webgpu-shader, background | White lines fall down the frame at varied speeds, each fading into a trail. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `flowing-gradient` | block 1920x1080 | webgpu, webgpu-shader, background | Bands of orange and violet flow across the frame in a smooth gradient. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `fractal-noise` | block 1920x1080 | webgpu, webgpu-shader, background | Soft grey fractal noise drifts across the frame like slow clouds. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `frost` | block 1920x1080 | webgpu, webgpu-shader, orb | A frozen blue orb with frost creeping in from its edge, on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `gabor-noise` | block 1920x1080 | webgpu, webgpu-shader, background | Grey streaky noise drifts across the frame like a moving fingerprint. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `goo` | block 1920x1080 | webgpu, webgpu-shader, liquid | A glossy green liquid ball whose surface bulges and ripples like wet goo, centred on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `heatmap` | block 1920x1080 | webgpu, webgpu-shader, object | Thermal colours flow through a glowing orb, on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `hologram` | block 1920x1080 | webgpu, webgpu-shader, object | A pale blue holographic orb with scan rings and flicker, on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `holographic` | block 1920x1080 | webgpu, webgpu-shader, holographic | An iridescent foil orb with a shifting rainbow sheen, centred on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `lens-flare` | block 1920x1080 | webgpu, webgpu-shader, background | A camera lens flare: a bright star burst and a faint rainbow halo that slowly shimmer on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `light-edge` | block 1920x1080 | webgpu, webgpu-shader, object | Purple and cyan light races around the edge of an orb on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `liquid-metal` | block 1920x1080 | webgpu, webgpu-shader, object | A chrome sphere ripples and flows like molten metal on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `mesh-gradient` | block 1920x1080 | webgpu, webgpu-shader, background | Soft coral, orange and violet fields blend and drift in a mesh gradient. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `nebula` | block 1920x1080 | webgpu, webgpu-shader, object | A small world of pink and blue gas swirls inside a sphere on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `obsidian` | block 1920x1080 | webgpu, webgpu-shader, object | A dark glass orb catches pink and cyan iridescent light on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `plasma` | block 1920x1080 | webgpu, webgpu-shader, background | Deep violet plasma folds and churns across the whole frame. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `plastic` | block 1920x1080 | webgpu, webgpu-shader, object | A glossy white plastic orb with soft studio reflections, on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `prism` | block 1920x1080 | webgpu, webgpu-shader, background | A white beam of light splits into a slowly turning rainbow. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `ripples` | block 1920x1080 | webgpu, webgpu-shader, background | Concentric rings ripple outward from the centre, white on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `sine-wave` | block 1920x1080 | webgpu, webgpu-shader, background | A glowing white sine wave travels across a black frame. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `spiral` | block 1920x1080 | webgpu, webgpu-shader, background | A bold black and white spiral turns in the frame. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `strands` | block 1920x1080 | webgpu, webgpu-shader, background | Thin ribbons of pink and blue light weave across a black field. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `stripes` | block 1920x1080 | webgpu, webgpu-shader, background | Bold black and white diagonal stripes slide across the frame. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `swirl` | block 1920x1080 | webgpu, webgpu-shader, background | Orange and blue color fields swirl and flow into each other across the whole frame. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `thin-film` | block 1920x1080 | webgpu, webgpu-shader, object | An orb's rim shimmers with soap-bubble iridescence on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `voronoi` | block 1920x1080 | webgpu, webgpu-shader, background | Magenta cells with glowing blue centres shift and reshape across the frame. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `water` | block 1920x1080 | webgpu, webgpu-shader, orb | A sphere of wind-rippled water reflecting a blue sky, on black. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `waveform` | block 1920x1080 | webgpu, webgpu-shader, audio | Equalizer bars in a blue to pink gradient pulse across the middle of the frame, like an audio visualizer. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |
| `worley-noise` | block 1920x1080 | webgpu, webgpu-shader, background | A field of drifting cells, light at their centres and dark at their edges. | **X** | Re-size (full-bleed shader) | n/a (no copy) | High - WebGPU, lib uses rAF/clock, no own timeline (X1) |

### 14. 3D / WebGL hero and title blocks (13 items: A 0, B 0, C 5, X 8)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `canopy-part-title` | block 1920x1080 | 3d-motion, title-card, leaves | Leaves sweep through the frame and part to reveal the headline. | **C** | No (16:9 px layout) | Med (Gelasio; canvas text/measure) | Med - three.js, canvas2D, Google Fonts link |
| `extruded-logo` | block 1920x1080 | 3d-object, three-js, webgl | Beveled 3D letters flip up one by one, the word swings so light runs across the bevels, then settles for a readable... | **C** | No (16:9 px layout) | Low (EL Inter) | Med - three.js, canvas2D |
| `glass-hero` | block 1920x1080 | 3d-object, three-js, webgl | A solid glass object rises in front of a giant headline and keeps turning, so the type bends and splits into colour... | **C** | No (16:9 px layout) | Med (GH Caption; canvas text/measure) | Med - three.js, canvas2D |
| `lottie-character-walk` | block 1920x1080 | character, character-animation, mascot | A jointed flat character walks in on planted feet, stops and points at a card; the body acting is a Lottie file and... | **C** | No (16:9 px layout) | Med (Inter; lh 1.05 + overflow mask) | Med - Lottie, Google Fonts link |
| `three-orbiting-cards` | component | video-primitive, three-js, webgl | A Three.js-powered orbit scene driven by a paused GSAP timeline for deterministic renders. | **C** | Partial (px-sized) | Low (Inter) | Med - three.js, no own timeline (X1) |
| `code-slice-hero` | block 1920x1080 | 3d-motion, transition, typography | A tiled headline surface flips cell by cell under a sweeping depth field to reveal the rear headline. | **X** | No (16:9 px layout) | **High** (ships Geist-Bold.ttf) | Med - WebGL, Math.random/Date.now in code, canvas2D |
| `cuboid-carousel` | block 1920x1080 | 3d-motion, carousel, cards | A chain of bevelled cuboids rides a travelling wave as a content carousel. | **X** | No (16:9 px layout) | Med (Inter; canvas text/measure) | Med - three.js, lib uses rAF/clock, Math.random/Date.now in code, canvas2D, Google Fonts link |
| `frost-sequence-camera-orbit` | block 1920x1080 | 3d-motion, ice, frost | An orbiting camera follows an ice logo as it breaks apart, reforms into two text moments, and fades. | **X** | No (16:9 px layout) | **High** (ships Geist-Bold.ttf, Geist-Regular.ttf) | High - WebGPU, lib uses rAF/clock, Math.random/Date.now in code |
| `glass-shard-title` | block 1920x1080 | 3d-motion, title-card, glass | Glass shards fly in through fog and tile themselves into the headline. | **X** | No (16:9 px layout) | **High** (ships Geist-Bold.ttf, Geist-Regular.ttf) | Med - three.js bundle, lib uses rAF/clock, d3 CDN |
| `gooey-split` | block 1920x1080 | effect, gooey, metaball | A dot splits into a three-dot menu with a gooey metaball neck, spins into a swirl mark under directional shutter... | **X** | No (16:9 px layout) | Low (theme var / system) | Low - SVG filter |
| `orbit-card` | block 1920x1080 | 3d-motion, cards, feature-reveal | A single feature card orbits a dot sphere on approved Blender camera motion. | **X** | No (16:9 px layout) | Med (Archivo; canvas text/measure) | Med - three.js, lib uses rAF/clock, Math.random/Date.now in code, canvas2D |
| `product-turntable` | block 1920x1080 | 3d-object, three-js, webgl | A product turns a full revolution on a studio plinth in a seamless loop. | **X** | No (16:9 px layout) | Med (PT Caption; canvas text/measure) | Med - three.js, canvas2D |
| `wireframe-portal-title` | block 1920x1080 | 3d-motion, title-card, wireframe | A wireframe portal bursts open, the title comes through, then its letters swap into a second phrase. | **X** | No (16:9 px layout) | **High** (ships Geist-Bold.ttf, Geist-Regular.ttf) | Med - three.js, network fetch (assets), canvas2D |

### 15. VFX, html-in-canvas and liquid glass (11 items: A 0, B 0, C 0, X 11)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `ios26-liquid-glass` | block 1920x1080 | liquid-glass-html-in-canvas, webgpu, 3d | 3D iPhone with a normal iOS 26 home screen, liquid glass app icons, shader wallpaper, dock, and fluid glass... | **X** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask; canvas text/measure) | High - WebGPU, html-in-canvas (Chrome flag), three.js, canvas2D, backdrop-filter |
| `liquid-glass-notification` | block 1920x1080 | html-in-canvas, liquid-glass-html-in-canvas, webgpu | Frosted glass notification cards floating over an aurora shader background | **X** | No (16:9 px layout) | Low (Inter) | High - WebGPU, html-in-canvas (Chrome flag), three.js, canvas2D |
| `liquid-glass-widgets` | block 1920x1080 | html-in-canvas, liquid-glass-html-in-canvas, webgpu | Frosted glass stat cards, showcase panel and pill chips over an aurora shader background | **X** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask; uppercase) | High - WebGPU, html-in-canvas (Chrome flag), three.js, canvas2D, blend |
| `macos-tahoe-liquid-glass` | block 1920x1080 | html-in-canvas, 3d, macos | 3D MacBook with a macOS Tahoe-style desktop, glass menu bar, Finder window, dock, and cinematic device camera move. | **X** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask; canvas text/measure) | High - html-in-canvas (Chrome flag), three.js, canvas2D, backdrop-filter, blend |
| `vfx-iphone-device` | block 1920x1080 | html-in-canvas, 3d, device | Real GLTF iPhone 15 Pro Max and MacBook Pro models with live HTML-in-Canvas screen content, morphing glass lens,... | **X** | No (16:9 px layout) | Med (Inter; lh 1.1 + overflow mask) | High - html-in-canvas (Chrome flag), three.js, canvas2D |
| `vfx-liquid-background` | block 1920x1080 | html-in-canvas, liquid, webgl | Organic liquid simulation with vertex displacement on a subdivided plane. | **X** | No (16:9 px layout) | Med (Inter; uppercase; canvas text/measure) | Med - three.js, canvas2D, Google Fonts link |
| `vfx-liquid-glass` | block 1920x1080 | html-in-canvas, webgl | VFX composition block | **X** | No (16:9 px layout) | Med (Inter; lh 0.9 + overflow mask; uppercase; canvas text/measure) | High - html-in-canvas (Chrome flag), three.js, canvas2D, Google Fonts link |
| `vfx-magnetic` | block 1920x1080 | html-in-canvas, webgl | VFX composition block | **X** | No (16:9 px layout) | Med (SF Mono; mono/system fallback lacks VI) | High - html-in-canvas (Chrome flag), WebGL, canvas2D, backdrop-filter |
| `vfx-portal` | block 1920x1080 | html-in-canvas, webgl | VFX composition block | **X** | No (16:9 px layout) | Med (Inter; lh 1.05 + overflow mask) | High - html-in-canvas (Chrome flag), three.js, canvas2D, Google Fonts link |
| `vfx-shatter` | block 1920x1080 | html-in-canvas, webgl | VFX composition block | **X** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask; uppercase) | High - html-in-canvas (Chrome flag), three.js, canvas2D, Google Fonts link |
| `vfx-text-cursor` | block 1920x1080 | html-in-canvas, text, shader | Dramatic text reveal with cursor glow, chromatic shadow rays, and directional lighting on a black stage. | **X** | No (16:9 px layout) | Med (Inter, Big Shoulders Display; lh 0.88 + overflow mask; uppercase) | Med - WebGL, canvas2D, backdrop-filter, Google Fonts link |

### 16. Title cards, end cards and brand stings (11 items: A 1, B 3, C 5, X 2)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `titlecard-lockup` | component | motion-primitive, typography, title-card | The calm breather titlecard: an optional mono kicker fades up, the wordmark settles dead-center with one restrained... | **A** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.0 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `cta-close` | component | motion-primitive, ui-props, cta | A display-scale action line lands per word and fills the frame with air, one generous CTA capsule pops beneath it... | **B** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `logo-sting` | component | motion-primitive, brand, logo | A wordmark slams into its final scale, fires one accent ring and one white impact frame, then holds completely still. | **B** | Yes (cq-elastic) | Med (Inter; lh 0.9 + overflow mask) | Low - GSAP/DOM |
| `titlecard-calm` | component | motion-primitive, typography, title-card | A restrained title card where a mono kicker and generous grotesque headline fade upward, drift almost imperceptibly,... | **B** | Yes (cq-elastic) | Med (Helvetica Neue, SF Mono; lh 0.94 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `cta-lockup` | component | motion-primitive, ui-props, cta | A canonical closing lockup that reveals an action line, pops in an accent CTA capsule, settles supporting microcopy,... | **C** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `logo-brand-close` | component | motion-primitive, typography, brand | A display-scale wordmark cascades letter by letter into a centered lockup, the accent brand period lands last, an... | **C** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.0 + overflow mask; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `logo-outro` | block 1920x1080 | branding, outro, logo | Cinematic logo reveal with piece-by-piece assembly, glow bloom, tagline fade-in, and URL pill | **C** | No (16:9 px layout) | Low (Inter) | Low - Google Fonts link |
| `yt-logo-intro` | block 1920x1080 | logo, intro, creator | Logo stamp pops on a lined board, a kicker line gives way to the title with an accent arrow chip; seeded line distortion | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `yt-prism-title` | block 1920x1080 | typography, title-card, creator | Display title on a transparent root: blur-focus entrance, red/blue fringe that settles then breathes, perspective... | **C** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `social-proof-card` | component | motion-primitive, social-proof, end-card | The app-store close as one mountable scene: wordmark, five stars, a proof line, three feature icons and a CTA... | **X** | Yes (cq-elastic) | Low (Georgia) | Low - GSAP/DOM |
| `store-badge-lockup` | component | prop, ui-props, mobile | Settles a short headline above equal-size App Store and Google Play badges as a token-driven mobile end-card call to... | **X** | Yes (cq-elastic) | Med (theme var / system; lh 1.0 + overflow mask) | Low - GSAP/DOM |

### 17. Social, platform overlays and lower thirds (23 items: A 0, B 0, C 3, X 20)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `lt-kicker-name` | block 1920x1080 | lower-third, overlay, podcast | Cardless lower third with an accent eyebrow/kicker tag, heavy name, and a drawn baseline; for footage | **C** | No (16:9 px layout) | **High** (Archivo Black has no VI subset) | Low - GSAP/DOM |
| `lt-side-rule` | block 1920x1080 | lower-third, overlay, podcast | Cardless lower third with a vertical accent bar; condensed display name + mono role, text-shadowed for footage | **C** | No (16:9 px layout) | Med (League Gothic, JetBrains Mono; lh 0.86 + overflow mask; uppercase) | Low - GSAP/DOM |
| `yt-comment-card` | block 1920x1080 | social, comments, creator | Social comments typing on over footage: avatar pop, username and time, per-character typewriter, likes row; image... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `instagram-follow` | block 1080x1920 | social, overlay, instagram | Animated Instagram follow overlay with profile card and follow button | **X** | Yes (native 9:16) | **High** (DM Sans has no VI subset) | Low - Google Fonts link |
| `lower-third-bild` | block 1920x1080 | broadcast, lower-third, news | News-style lower third with tight-fit text boxes: white headline bar with red drop-shadow, red sub-line with white... | **X** | No (16:9 px layout) | Med (Barlow Condensed; lh 1.05 + overflow mask; uppercase) | Low - GSAP/DOM |
| `lt-accent-underline` | block 1920x1080 | lower-third, overlay, podcast | Cardless lower third for footage overlay: name rises, an accent rule draws left-to-right, role fades in;... | **X** | No (16:9 px layout) | Med (Oswald, Space Mono; lh 0.96 + overflow mask; uppercase) | Low - GSAP/DOM |
| `lt-bold-block` | block 1920x1080 | lower-third, overlay, podcast | High-energy podcast lower third: solid dark block wipes in, uppercase name slams up, accent tag pops | **X** | No (16:9 px layout) | **High** (Archivo Black has no VI subset) | Low - GSAP/DOM |
| `lt-clean-bar` | block 1920x1080 | lower-third, overlay, podcast | Minimal white-card lower third for podcasts/interviews: accent tab, name + role, clip-wipe entrance | **X** | No (16:9 px layout) | Med (Montserrat; lh 1.06 + overflow mask) | Low - GSAP/DOM |
| `lt-color-block` | block 1920x1080 | lower-third, overlay, podcast | High-energy lower third: bold accent-color block slides in with overshoot, condensed name + mono role | **X** | No (16:9 px layout) | Med (League Gothic, Space Mono; lh 0.86 + overflow mask; uppercase) | Low - GSAP/DOM |
| `lt-dark-card` | block 1920x1080 | lower-third, overlay, podcast | Charcoal card lower third for bright footage: name, drawn accent underline, role; slide-up entrance | **X** | No (16:9 px layout) | Med (Montserrat; lh 1.02 + overflow mask) | Low - GSAP/DOM |
| `lt-mask-reveal` | block 1920x1080 | lower-third, overlay, podcast | Cardless lower third: an accent sweep crosses and clip-path-reveals a heavy name, role fades up; for footage | **X** | No (16:9 px layout) | Med (Montserrat; lh 0.98 + overflow mask) | Low - GSAP/DOM |
| `lt-neon-border` | block 1920x1080 | lower-third, glow, loop | Two arcs of light travel the edge of a rounded panel and snap corner to corner, trailing a soft three-layer bloom. | **X** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |
| `lt-soft-pill` | block 1920x1080 | lower-third, overlay, podcast | Rounded white pill lower third for podcasts/interviews: status dot, name + role, scale-pop entrance | **X** | No (16:9 px layout) | Med (Montserrat; lh 1.04 + overflow mask) | Low - GSAP/DOM |
| `lt-stack-bars` | block 1920x1080 | lower-third, overlay, podcast | Two stacked bars: a dark name bar wipes from the left, an accent role bar wipes from the right | **X** | No (16:9 px layout) | **High** (Archivo Black has no VI subset) | Low - GSAP/DOM |
| `macos-notification` | block 1920x1080 | social, overlay, notification | Animated macOS-style notification banner with app icon and message | **X** | No (16:9 px layout) | Med (Inter; uppercase) | Low - backdrop-filter, Google Fonts link |
| `news-ticker` | block 1920x1080 | lower-third, overlay, news | Premium broadcast-style lower-third ticker with live label, headline ribbon, and scrolling news crawl. | **X** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - GSAP/DOM |
| `reddit-post` | block 1920x1080 | social, overlay, reddit | Animated Reddit post card overlay with upvotes and comments | **X** | No (16:9 px layout) | **High** (DM Sans has no VI subset) | Low - Google Fonts link |
| `spotify-card` | block 1080x1920 | social, overlay, spotify | Animated Spotify now-playing card with album art and progress bar | **X** | Yes (native 9:16) | Low (Inter) | Low - backdrop-filter, Google Fonts link |
| `thread-message-stack` | block 1920x1080 | social, conversation, messages | A source-owned editable conversation stack with arbitrary incoming and outgoing messages | **X** | No (16:9 px layout) | Med (Helvetica Neue; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `tiktok-follow` | block 1080x1920 | social, overlay, tiktok | Animated TikTok follow overlay with profile card and follow button | **X** | Yes (native 9:16) | **High** (DM Sans has no VI subset) | Low - Google Fonts link |
| `x-follow-card` | component | social-overlay | A social follow card with avatar, handle, and follower motion. | **X** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `x-post` | block 1920x1080 | social, overlay, twitter | Animated X/Twitter post card overlay with engagement metrics | **X** | No (16:9 px layout) | Low (Inter) | Low - Google Fonts link |
| `yt-lower-third` | block 1920x1080 | social, overlay, youtube | Animated YouTube subscribe lower third with avatar and channel info | **X** | No (16:9 px layout) | **High** (DM Sans has no VI subset) | Low - Google Fonts link |

### 18. Mock UI, cursors, gestures, chat and notifications (54 items: A 0, B 0, C 6, X 48)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `beat-accent` | component | motion-primitive, effects, burst | A single music-hit sting: impact flash, micro scale-pulse on the subject, immediate decay. | **C** | Yes (cq-elastic) | n/a (no copy) | Low - GSAP/DOM |
| `chat-thread` | component | motion-primitive, chat, mock-ui | The measured conversation as one mountable scene at full fidelity: status bar, back badge, avatar and name pill,... | **C** | Yes (cq-elastic) | Low (theme var / system) | Low - GSAP/DOM |
| `confetti` | component | effect | A deterministic celebration burst with seeded particles and gravity. | **C** | Partial (px-sized) | n/a (no copy) - demo Inter | Low - blend, no own timeline (X1) |
| `notes-typing` | component | motion-primitive, notes, typing | The notes-app confession as a mountable scene: a bold title, then body lines typed character by character on the... | **C** | Yes (cq-elastic) | Low (theme var / system) | Low - GSAP/DOM |
| `notification-stack` | component | motion-primitive, product-demo, notification | 1 to 5 token notification cards slide-settle into a vertical stack on cues, newest on top; one card grows slightly... | **C** | Yes (cq-elastic) | Med (Segoe UI; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `typing-indicator` | component | video-primitive, chat, mock-ui | The three-dot chat bubble that says someone is writing: it pops in at the thread's edge exactly as messaging apps... | **C** | Partial (px-sized) | Low (theme var / system) | Low - no own timeline (X1) |
| `agent-cursor` | component | cursor, motion-primitive, agent | An AI agent operating a UI: a cursor with an accent name label that types out each step, clicks each target with a... | **X** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `avatar-group-hover` | component | video-primitive, transition-primitive, transitions-dev-port | A distance-falloff avatar group lift with bouncy hover return | **X** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `badge-pop` | component | video-primitive, transition-primitive, transitions-dev-port | A transitions.dev-inspired notification badge pop with elastic scale and count reveal | **X** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `browser-device-stage` | component | stage, product-demo, device | A generic app surface in token-native device chrome (browser, window, or phone). | **X** | Yes (cq-elastic) | Med (SF Mono; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `camera-scan-gate` | component | prop, ui-props, camera | A camera and QR recognition moment with a viewfinder sweep, bracket lock, confirmation pulse, and verified next beat. | **X** | Yes (cq-elastic) | Med (Inter; lh 1.1 + overflow mask) | Low - GSAP/DOM |
| `card-resize` | component | video-primitive, transition-primitive, transitions-dev-port | A transitions.dev-inspired card resize primitive that expands a compact card into a detail panel | **X** | Partial (px-sized) | Med (Inter; uppercase) | Low - no own timeline (X1) |
| `chat-message` | component | video-primitive, chat, mock-ui | One message arrives on the measured entry - scale 0.75, 0.12s, growing from its sender's corner. | **X** | Yes (cq-elastic) | Low (theme var / system) | Low - GSAP/DOM |
| `cursor-context-menu` | component | cursor, motion-primitive, menu | A cursor right-clicks a file, a context menu blooms from its tip, the hover highlight tracks the item under it, and... | **X** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `cursor-drag-drop` | component | cursor, motion-primitive, drag | A cursor grabs a task card, lifts and tilts it into its motion, carries it in lockstep to an empty column, drops it... | **X** | Partial (px-sized) | Low (Inter) | Low - GSAP/DOM |
| `cursor-glyph-trail` | component | cursor, motion-primitive, demonstrate | A tutorial cursor path: on a settings screen the arrow clicks through three steps, leaving a dotted trail spaced... | **X** | Yes (cq-elastic) | Med (Inter; uppercase) | Low - GSAP/DOM |
| `cursor-marquee-select` | component | cursor, motion-primitive, select | A cursor drags a selection rectangle across a photo grid; each tile rings and pops a check the frame the rectangle... | **X** | Partial (px-sized) | Low (Inter) | Low - SVG filter |
| `cursor-text-select` | component | cursor, motion-primitive, text | An arrow turns into an I-beam over a document, drags a selection across a phrase character by character, raises a... | **X** | Yes (cq-elastic) | Med (Inter; uppercase) | Low - GSAP/DOM |
| `dart-cursor` | component | cursor, motion-primitive, pointer | A bold outlined arrowhead that dives in from camera depth, flies nose-first with motion blur along its path,... | **X** | Likely (unitless/%) | Low (theme var / system) | Low - SVG filter |
| `device-frame-stage` | component | prop, device, mobile | A phone or tablet mockup staged as a physical scene prop with a screen slot for arbitrary reconstructed UI, rising... | **X** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `gesture-tap` | component | motion-primitive, gesture, tap | A contact circle taps a mobile pill button, releases it into a new labeled accent state, and lifts away. | **X** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.05 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `icon-swap` | component | video-primitive, transition-primitive, transitions-dev-port | A scale-and-blur icon swap primitive for toolbar and action state changes | **X** | Partial (px-sized) | Low (theme var / system) | Low - no own timeline (X1) |
| `input-feedback` | component | transition-primitive, transitions-dev-port, input | A transitions.dev-inspired input feedback primitive with shake, clear affordance, and success state | **X** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `magnetic-cursor` | component | cursor, motion-primitive, pointer | A soft dot pointer glides across an editor toolbar, is pulled into each button and morphs into its rounded hover... | **X** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `menu-morph` | component | video-primitive, transition-primitive, transitions-dev-port | A transitions.dev-inspired hamburger and plus-menu morph primitive for compact action menus | **X** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `micro-transitions` | component | transition-primitive, motion-primitive, transitions-dev-port | A transitions.dev-inspired pack of badge, dropdown, modal, tabs, tooltip, and success-check micro transitions | **X** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `modal-morph` | component | motion-primitive, structure, flip | A small card expands into a full panel, shared-element style: both layouts measured once at mount, the container... | **X** | Yes (cq-elastic) | Med (Inter, SF Mono; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `multi-device-splay` | component | motion-primitive, device, phone | Phone, tablet, and desktop product mockups fan from a centered stack into a proud splayed arrangement with a subtle... | **X** | Yes (cq-elastic) | Low (theme var / system) | Low - GSAP/DOM |
| `multiplayer-cursors` | component | cursor, pointer, multiplayer | Labeled collaborator cursors with token-derived colors and soft glows drift from spread positions into a shared... | **X** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `native-notification-pop` | component | motion-primitive, product-demo, overlay | One system-faithful notification banner (iOS or macOS) drops in over any scene on an accurate interruptible spring:... | **X** | Yes (cq-elastic) | Med (Inter; uppercase) | Low - backdrop-filter |
| `notification-pileup` | component | notification, mobile, ui-props | Mobile notification cards arrive faster and faster, each new alert pushing the existing stack downward into a dense,... | **X** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `onboarding-stepper-flow` | component | ui-flow, onboarding, stepper | A composed onboarding flow with milestone rail, active step card, and next-action button | **X** | Partial (px-sized) | Med (Inter; uppercase) | Low - no own timeline (X1) |
| `oversized-cursor` | component | cursor, motion-primitive, actor | The look-here pointer for a video: the macOS arrow at 3.5x its normal size lands its tip on one control, clicks it... | **X** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `press-ripple` | component | cursor, motion-primitive, product-demo | A cursor decel-arrives from off-stage, lands slightly off-center on a caller-positioned target, compresses with it... | **X** | Yes (cq-elastic) | Med (Inter; lh 1.0 + overflow mask) | Low - GSAP/DOM |
| `pull-to-refresh` | component | pointer, pointers, mobile | A mobile list pulls through nonlinear rubber-band resistance, arms at a threshold, commits to a bounded loading... | **X** | Yes (cq-elastic) | Med (Inter; uppercase) | Low - GSAP/DOM |
| `screen-flow-carousel` | component | product-demo, feature-tour, carousel | Two to five app screens ride a horizontal rail: one primary at center, neighbors receded, advancing on cues with a... | **X** | Yes (cq-elastic) | Med (SF Mono; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `scroll-feed` | component | motion-primitive, effects, scroll | A loop-friendly column of varied skeleton post cards scrolls upward with subtle motion trails and an agitated pace. | **X** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `settings-toggle-flow` | component | ui-flow, settings, toggle | A composed settings flow with preference rows, toggle switches, and active-state feedback | **X** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `sheet-spring-up` | component | video-primitive, sheet, spring | A bottom sheet rushes up from below the frame on a real spring sampled frame by frame from reference footage,... | **X** | Partial (px-sized) | Low (theme var / system) | Low - no own timeline (X1) |
| `signup-flow` | component | ui-flow, signup, form | A composed signup flow with social action, email field, password field, and submit button | **X** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `skeleton-reveal` | component | video-primitive, transition-primitive, transitions-dev-port | A skeleton loader transition that pulses, then cross-fades into content | **X** | Likely (unitless/%) | Low (Inter) | Low - no own timeline (X1) |
| `soft-blob-touch` | component | motion-primitive, product-demo, material | A granular soft blob idles with slow internal drift; a scripted touch dot decel-arrives, the blob deforms toward it... | **X** | Yes (cq-elastic) | Low (Inter) | Low - canvas2D |
| `spotlight-card` | component | effect | A card with a scripted cursor spotlight and lit border. | **X** | Partial (px-sized) | Low (Inter) | Low - blend, no own timeline (X1) |
| `sticky-mock-swap` | component | motion-primitive, product-demo, sticky | A pinned product mock cross-fades through accent-tinted feature states while matching captions rise, hold, and exit... | **X** | Yes (cq-elastic) | Med (Inter; lh 1.04 + overflow mask) | Low - GSAP/DOM |
| `success-check` | component | video-primitive, transition-primitive, transitions-dev-port | A success check primitive with ring pop, path draw, and subtle rotate blur | **X** | Partial (px-sized) | Low (theme var / system) | Low - no own timeline (X1) |
| `swipe-rail` | component | motion-primitive, interaction, gesture | A contact circle leads a horizontal card rail through a fast drag, momentum carry, and settled snap to the next card. | **X** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.05 + overflow mask; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `tabs-slide-indicator` | component | transition-primitive, transitions-dev-port, tabs | A pill indicator transition that slides between active tabs | **X** | Partial (px-sized) | Low (Inter) | Low - no own timeline (X1) |
| `tilt-card` | component | video-primitive, transition-primitive, transitions-dev-port | A transitions.dev-inspired tilt card primitive with depth layers and hover-style parallax | **X** | Partial (px-sized) | Med (Inter; lh 0.96 + overflow mask; uppercase) | Low - no own timeline (X1) |
| `toggle-flip` | component | prop, ui-props, toggle | An oversized UI toggle switch that flips with real physicality: thumb overshoot, track color crossfade, and a soft... | **X** | Yes (cq-elastic) | Low (Inter) | Low - GSAP/DOM |
| `touch-indicator` | component | cursor, motion-primitive, mobile | A translucent contact-circle gesture actor for mobile UI scenes: it touches the glass on the frame the host target... | **X** | Yes (cq-elastic) | Low (theme var / system) | Low - GSAP/DOM |
| `typed-prompt` | component | motion-primitive, product-demo, typing | A prompt line types itself in chunked human cadence behind a deterministic blinking caret, with optional... | **X** | Yes (cq-elastic) | Med (SF Mono; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `ui-3d-reveal` | block 1920x1080 | showcase, 3d, reveal | Perspective 3D reveal animation for UI elements | **X** | No (16:9 px layout) | Med (Inter; lh 1.0 + overflow mask; uppercase) | Low - Google Fonts link |
| `vector-editor-rig` | component | prop, ui-props, demonstrate | A dark design-tool app chrome with a live vector pen path, sequential anchor points, bezier handles, a selection... | **X** | Yes (cq-elastic) | Med (Inter; uppercase) | Low - GSAP/DOM |
| `velocity-throw-snap` | component | motion-primitive, feature-tour, rail | A five-shot rail whips past on a fast decaying curve, then overshoots and snaps the selected hero shot exactly to... | **X** | Yes (cq-elastic) | Med (Inter, SF Mono; lh 1.0 + overflow mask; mono/system fallback lacks VI) | Low - GSAP/DOM |

### 19. Code and developer (13 items: A 0, B 0, C 0, X 13)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `code-3d-extrude` | block 1920x1080 | code, code-animation, 3d | Syntax-highlighted code on a lit, beveled 3D slab that rotates through real space and settles to a readable rest —... | **X** | No (16:9 px layout) | Med (theme var / system; canvas text/measure) | Med - three.js, canvas2D |
| `code-diff` | block 1920x1080 | code, code-animation, diff | An edit shown as a colored diff — removed lines collapse in red, added lines expand in green. | **X** | No (16:9 px layout) | Low (JetBrains Mono) | Low - GSAP/DOM |
| `code-highlight` | block 1920x1080 | code, code-animation, highlight | A highlight band sweeps across a target line while the surrounding context dims — draws the eye to one line. | **X** | No (16:9 px layout) | Low (JetBrains Mono) | Low - GSAP/DOM |
| `code-morph` | block 1920x1080 | code, code-animation, morph | One snippet transforms into another — tokens glide between positions, leavers fade out, enterers fade in. | **X** | No (16:9 px layout) | Low (JetBrains Mono) | Low - GSAP/DOM |
| `code-particle-assemble` | block 1920x1080 | code, code-animation, particles | Thousands of GPU points scatter through space and fly to the exact glyph pixels of the code, resolving into readable... | **X** | No (16:9 px layout) | Med (theme var / system; canvas text/measure) | Med - three.js, canvas2D |
| `code-scroll` | block 1920x1080 | code, code-animation, scroll | The camera scrolls a long file to bring a target line to center and spotlights it — for walking through real modules. | **X** | No (16:9 px layout) | Low (JetBrains Mono) | Low - GSAP/DOM |
| `code-shader-dissolve` | block 1920x1080 | code, code-animation, shader | The code compiles into existence: a GPU fragment shader resolves it out of seeded noise with a chromatic dissolve... | **X** | No (16:9 px layout) | Med (theme var / system; canvas text/measure) | Med - three.js, canvas2D |
| `code-snippet-apple-terminal-pro` | block 1920x1080 | code, developer, showcase | Apple Terminal Pro profile: black background with grey text and lime green cursor, per-character typing animation of... | **X** | No (16:9 px layout) | Med (SF Mono, SF Pro Text; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `code-snippet-dark-2026` | block 1920x1080 | code, developer, showcase | VS Code workbench with per-character typing animation in the Dark 2026 theme. | **X** | No (16:9 px layout) | Med (Inter, Menlo; lh 1.0 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `code-snippet-dark-modern` | block 1920x1080 | code, developer, showcase | VS Code workbench with per-character typing animation in the Dark Modern theme. | **X** | No (16:9 px layout) | Med (Inter, Menlo; lh 1.0 + overflow mask; uppercase; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `code-terminal-run` | component | motion-primitive, product-demo, terminal | A token-chrome terminal panel runs one command: the prompt line types deterministically behind an integer-cycle... | **X** | Yes (cq-elastic) | Med (SF Mono; mono/system fallback lacks VI) | Low - GSAP/DOM |
| `code-typing` | block 1920x1080 | code, code-animation, typing | Token-streamed typing reveal with a caret that tracks the frontier — deterministic, no CSS animation. | **X** | No (16:9 px layout) | Low (JetBrains Mono) | Low - GSAP/DOM |
| `terminal-simulator` | component | code-animation | A terminal window types commands and streams log output. | **X** | Partial (px-sized) | Med (Inter, Menlo; mono/system fallback lacks VI) | Low - no own timeline (X1) |

### 20. Image carousels and galleries (25 items: A 0, B 0, C 15, X 10)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `carousel-path-1` | block 1920x1080 | carousel, gallery, images | Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-path-2` | block 1920x1080 | carousel, gallery, images | Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-path-3` | block 1920x1080 | carousel, gallery, images | Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-path-4` | block 1920x1080 | carousel, gallery, images | Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-path-5` | block 1920x1080 | carousel, gallery, images | Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-text-circle-1` | block 1920x1080 | carousel, title-card, kinetic-text | A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line,... | **C** | No (16:9 px layout) | Low (Inter) | Low - Google Fonts link |
| `carousel-text-circle-2` | block 1920x1080 | carousel, title-card, kinetic-text | A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line,... | **C** | No (16:9 px layout) | Low (Inter) | Low - Google Fonts link |
| `carousel-text-circle-3` | block 1920x1080 | carousel, title-card, kinetic-text | A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line,... | **C** | No (16:9 px layout) | Low (Inter) | Low - Google Fonts link |
| `carousel-text-circle-4` | block 1920x1080 | carousel, title-card, kinetic-text | A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line,... | **C** | No (16:9 px layout) | Low (Inter) | Low - Google Fonts link |
| `carousel-text-circle-5` | block 1920x1080 | carousel, title-card, kinetic-text | A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line,... | **C** | No (16:9 px layout) | Low (Inter) | Low - Google Fonts link |
| `carousel-vision-1` | block 1920x1080 | carousel, gallery, images | A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-vision-2` | block 1920x1080 | carousel, gallery, images | A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-vision-3` | block 1920x1080 | carousel, gallery, images | A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-vision-4` | block 1920x1080 | carousel, gallery, images | A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-vision-5` | block 1920x1080 | carousel, gallery, images | A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style... | **C** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-circle-1` | block 1920x1080 | carousel, gallery, images | Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 1);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-circle-2` | block 1920x1080 | carousel, gallery, images | Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 2);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-circle-3` | block 1920x1080 | carousel, gallery, images | Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 3);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-circle-4` | block 1920x1080 | carousel, gallery, images | Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 4);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-circle-5` | block 1920x1080 | carousel, gallery, images | Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 5);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-orbit-1` | block 1920x1080 | carousel, gallery, images | Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 1);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-orbit-2` | block 1920x1080 | carousel, gallery, images | Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 2);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-orbit-3` | block 1920x1080 | carousel, gallery, images | Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 3);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-orbit-4` | block 1920x1080 | carousel, gallery, images | Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 4);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |
| `carousel-orbit-5` | block 1920x1080 | carousel, gallery, images | Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 5);... | **X** | No (16:9 px layout) | Low (Inter) | Low - GSAP/DOM |

### 21. Showcases and ad templates (14 items: A 0, B 0, C 3, X 11)

| name | type | tags | one-line effect | rel | portrait-ready? | diacritic risk (fonts) | runtime risk |
|---|---|---|---|---|---|---|---|
| `apple-money-count` | block 1920x1080 | showcase, finance, kinetic | Apple-style finance counter that counts from $0 to $10,000, flashes green, and bursts money icons with sound. | **C** | No (16:9 px layout) | Med (theme var / system; lh 0.9 + overflow mask) | Low - GSAP/DOM |
| `message-thread-reveal` | block 1080x1920 | showcase, mock-ui, chat | A full text conversation plays out on a phone - bubbles popping in, typing indicators, a shared link card, emoji,... | **C** | Yes (native 9:16) | Low (Georgia) | Low - GSAP/DOM |
| `notes-reveal` | block 1080x1920 | showcase, mock-ui, notes | A personal note is typed character by character in a notes app - caret riding every letter, the page scrolling up on... | **C** | Yes (native 9:16) | **High** (ships permanent-marker-400.woff2, courier-prime-400.woff2) | Low - GSAP/DOM |
| `ai-answer-rank` | block 1080x1080 | mock-ui, ai, chat | Is your brand in the AI answer? | **X** | Partial (square/4:5) | Low (Inter) | Low - GSAP/DOM |
| `ai-chat-reveal` | block 1080x1920 | showcase, mock-ui, ai | A question is typed on a rising keyboard, sent, and answered by an AI that streams its reply word by word on a... | **X** | Yes (native 9:16) | Low (Helvetica Neue) | Low - GSAP/DOM |
| `app-showcase` | block 1920x1080 | showcase, app, 3d | Fitness app product showcase with three floating smartphone screens | **X** | No (16:9 px layout) | **High** (DM Sans has no VI subset) | Low - Google Fonts link |
| `blue-sweater-intro-video` | block 1920x1080 | showcase, ai, creator | Warm AI creator intro sequence that resolves into an X follow card for @_blue_sweater_. | **X** | No (16:9 px layout) | Med (Helvetica Neue, Georgia; lh 0.9 + overflow mask) | Low - GSAP/DOM |
| `chatgpt-exchange` | block 1080x1920 | showcase, mock-ui, ai | A portrait ChatGPT-style exchange types and sends a prompt, streams an answer, assembles a comparison table, and... | **X** | Yes (native 9:16) | **High** (ships inter-latin-400-normal.woff2, inter-latin-500-normal.woff2) | Low - backdrop-filter |
| `claude-exchange` | block 1080x1920 | showcase, mock-ui, ai | A portrait Claude-style exchange types a prompt, works through search and reasoning steps, then streams a detailed... | **X** | Yes (native 9:16) | **High** (ships eb-garamond-latin-400-normal.woff2, eb-garamond-latin-700-normal.woff2) | Low - GSAP/DOM |
| `heygen-avatar-promo-card` | block 1080x1920 | showcase, avatar, promotion | A portrait HeyGen offer card pairs a moving avatar mosaic with bold promotional typography and a branded callout | **X** | Yes (native 9:16) | **High** (ships inter-latin-400-normal.woff2, inter-latin-500-normal.woff2) | Low - GSAP/DOM |
| `notification-cascade` | block 1080x1920 | showcase, mock-ui, notification | Phone notifications land one after another and stack up the screen, each banner pushing the pile down as it arrives,... | **X** | Yes (native 9:16) | Low (Helvetica Neue, Georgia) | Low - GSAP/DOM |
| `share-sheet-carousel` | block 1080x1920 | showcase, mock-ui, share-sheet | A share sheet springs up from the bottom of the phone and cycles previews inside its card on a fast cut rhythm while... | **X** | Yes (native 9:16) | Med (Helvetica Neue; uppercase) | Low - GSAP/DOM |
| `slack-notification-ad` | block 1080x1920 | showcase, mock-ui, notification | A portrait lock screen fills with escalating Slack video requests before HeyGen delivers the payoff | **X** | Yes (native 9:16) | **High** (ships inter-latin-400-normal.woff2, inter-latin-500-normal.woff2) | Low - backdrop-filter |
| `vpn-youtube-spot` | block 1920x1080 | app, showcase, youtube | Snappy Apple-style YouTube insert showing a phone finding and installing a friendly VPN app with sound effects. | **X** | No (16:9 px layout) | Med (SF Pro Display; lh 0.84 + overflow mask) | Low - GSAP/DOM |

---

## 2. Port cards: the top ~40 (A/B)

The cards share these conventions:
- A device is `HF.devices.<name>.build(stage, spec, ctx) → {inEnd, syncs}`. It appends tweens to the master `tl` at `ctx.at` (the scene start), takes `spec.dur = ln.end - ln.start`, and turns cues into scene-relative times: `cues = ln.words.filter(...).map(w => w.t - ln.start)`.
- Every device reads only the G1 tokens.
- "Envelope" means the source's fixed IN, elastic HOLD and OUT law. Keep it: it is what lets one device fit any narrated line.
- Effort: S = under 2 h, M = half a day to a day, L = several days.
- The gotchas G1–G9 from §0 apply to every card and are cited by number.

### 2.1 Kinetic typography

**1. `per-word-rise` (A, S).**
- **Source:** splits `text` by words (or chars with `split:"char"`) into `.pwr-unit` spans. Each unit lands at `cues[i]`. Units past the cue list extrapolate at the last cue gap, and every landing is clamped before OUT. Units rise from `y:8cqh` with blur 1.4cqh on a custom C1-continuous `landEase`: a cubic-out that keeps 7% of the travel for the last 22% so the word "settles" instead of stopping dead. HOLD is dead still. Exit is none, fade or up.
- **Port:** our default "beat text" device. Cues come straight from `ln.words[k].t`, with `hot` words routed to `--brand`. Copy `landEase` verbatim. It is a pure function and the best single piece of code in the text set.
- **Gotchas:** G3 (lh 1.08 plus mask), G5 (`Array.from`), G6 (tweens `cqh` strings, so convert to px), G7 (one-line fit, so replace it with our multi-line fit).

**2. `line-swap` (A, S).**
- **Source:** line A rises into an overflow mask (0.5 s). At `swap_at`, A exits up (0.35 s) while B enters bottom-up 0.22 s later and lands 0.5 s after that. An optional `underline_word` inside B gets a scaleX bar draw (0.15 s beat, then 0.45 s).
- **Port:** the "myth → truth" or question → answer beat. `swap_at` is the `t` of the first word of the second clause. `underline_word` is the `hot` word.
- **Gotchas:** lh 1.0 mask (G3). Underline width comes from a word box measured at build time (G4).

**3. `kinetic-type-swap` (A, S/M).**
- **Source:** a prefix and suffix hold still. One CSS-grid slot stacks every option in the same grid cell, so the slot keeps the widest option's width and the sentence never reflows. Words roll vertically through the mask on `cues`, then the final word locks with a soft pulse. IN is 2.25 s plus cue stretch.
- **Port:** the FS signature beat: "Tuổi **Tý · Sửu · Dần** … hợp màu đỏ", and BUD lists like "tham · sân · si". Cues are the spoken times of each option.
- **Gotchas:** grid widest-word sizing needs fonts loaded (G4). Mask lh 1.08 (G3). Vietnamese options differ a lot in width, so a centred sentence leaves a visible gap when a short option is showing. Left-align the slot.

**4. `headline-slam` (A, S).**
- **Source:** the stage scales 1.6 → 1 with `expo.out` over the 0.72 s IN. The landing drives a three-frame shake: `x:0.55cqw, y:-0.3cqh`, then reversed, then 0, each tween lasting one frame (1/30 s). Then one drift cycle and a 0.46 s whip up.
- **Port:** the hook line, line 1. Land it on the first stressed word's `t`. Use `accent_word_index` for the hot word.
- **Gotchas:** lh 0.88 with an overflow mask is the worst diacritic case (G3). Convert the shake to px numbers (G6). Use it at most once per short.

**5. `ticker-takeover` (A, M).**
- **Source:** a mono ticker accelerates through 4–6 `options`, decelerates and locks on `final_word` with an accent flash, then promotes that word into a 15cqh full-frame headline. IN is 3.15 s.
- **Port:** the "which year or sign is it?" reveal: the ticker rolls can chi or years and promotes the answer.
- **Gotchas:** uppercase plus lh 0.9 plus `--font-mono` falls back to SF Mono or Menlo, which have no Vietnamese. Set JetBrains Mono (G2, G3). The fixed 3.15 s IN needs about a 4 s line, so the timing does not come from cues.

**6. `text-shimmer` (A, S).**
- **Source:** one 0.9 s narrow specular gradient band crosses the glyphs (`background-clip:text`) at `sweep_at`. The text is clean before and after. The hold has an off-glyph drift.
- **Port:** a gold sheen on the BUD title or FS "đại cát" word, cued to the word's `t`.
- **Gotchas:** `background-clip:text` crops at the line box, so the stacked marks lose the sheen (cosmetic). The mask is lh 0.96 (G3).

**7. `mk-emphasis-type` (A, S).**
- **Source:** two helpers. `mkEmphasisIn(tl, el, at, {drift, hold})` fades an oversized low-contrast word in over 1 s and drifts it x by `drift` over `hold` with `sine.inOut`. `mkEmphasisOut` fades it.
- **Port:** the "ghost word" background, for example a giant faint "NGHIỆP" or "TÝ" behind the scene. The earlier report recommends it as the replacement for the thin ring.
- **Gotchas:** it calls `gsap.set(target,{opacity:0,x:40})` *outside* the timeline. Convert it to `fromTo` (our "always fromTo" rule). It is px-based (x:40), so scale by the frame. Uppercase means taller marks; keep the word inside the frame.

**8. `text-match-cut` (B, M).**
- **Source:** text A and text B ride one value curve, `cubic-bezier(.85,0,.15,1)`, and hard-swap opacity at the speed peak (1.00 s of a 2.0 s move).
- **Modes:** scale-down 170→100%, scale-up 60→100%, tracking-in +0.22→−0.05em, or slides.
- **Extra:** an optional gradient bar sweeps through the glyphs on its own 87% curve.
- **Port:** a seam between two consecutive lines with no transition chrome. Use the `t` of the boundary word as `CUT_AT`.
- **Gotchas:** tracking-in squeezes Vietnamese letters and their marks into each other, so prefer the scale modes. Hardcoded Inter. Measured (G4).

**9. `strikethrough-replace` (B, S).**
- **Source:** CSS draws the strike via `--hf-strike-progress` 0→1 on an `<i>` pseudo-element, then reveals the replacement. Recipe only, with no timeline (X1).
- **Port:** the "Sai: … → Đúng: …" myth-busting beat that suits FS kiêng kỵ content. Cue the strike on the wrong word's `t` and the replacement on the right word's `t`.
- **Gotchas:** px sizing. The strike is at mid x-height and passes through the dot-below marks only when the line-height is tight.

**10. `number-wheel` (A, S).**
- **Source:** a `.hf-number-wheel[data-value]` builds one column strip of 0–9 per digit (×1, ×2 or ×3 spins) and writes `--hf-number-target-y`. The recipe tweens the strips' `y` to the target with `power3.out` over 1.1 s, `stagger:0.05`. No timeline.
- **Port:** a birth-year odometer ("1990 → 2026") or an age count. Write the y values as numbers into our `tl`.
- **Gotchas:** digits only, so no diacritic risk. Use tabular numerals in Be Vietnam Pro (`font-variant-numeric: tabular-nums`).

**11. `split-flap-board` (B, M).**
- **Source:** a Solari board in a 1920 px block. Each cell walks its drum forward through the intervening characters of `flapAlphabet` (default `" A–Z0–9.,'"`, maxLength 64) until it lands on its target. Cell width is `min(130, (1920-240-gaps)/count)`.
- **Port:** an FS "Năm Bính Ngọ 2026" or "Giờ hoàng đạo" board in portrait. Rebuild the geometry for a width of 1080. Put only the needed precomposed Vietnamese capitals in the alphabet, in a deliberate drum order, for example `" 0123456789ABCDĐGHIKLMNOPQSTUVXYÂĂÊÔƠƯÁÀẢÃẠẤẦ…"`.
- **Gotchas:** a full Vietnamese capital set exceeds the 64-char manifest bound, and the drum walk time grows with alphabet length. Use digits plus a minimal set. The cell's line box must fit the stacked marks.

### 2.2 Captions and VO-synced highlight

**12. `mk-callout-highlight` (B, S).**
- **Source:** one scalar `st.p` (0..1) tweened linearly from `sweep.start` to `sweep.end`. `render()` sets each word's colour to `interpolate(FAINT, FULL)(clamp(p·N − i))`. The comment says to replace the linear tween "with several tweens between per-phrase progress values" to follow a real VO.
- **Port:** our karaoke caption already uses real `w.t`. Borrow the *scalar-driver* idea: one proxy and one painter, and drive `p` with keyframes at each `w.t`. That gives smooth ink-in per word with far fewer tweens.
- **Gotchas:** fixed 1920×1080 box with `x:1030`. The painter hangs on `tl.eventCallback("onUpdate", render)`, which is the exact pattern `camera-shake` warns can freeze on seek. Port it as a driver-property setter (G6). It measures the box with no font gate (G4).

**13. `caption-camera-follow` (B, M).**
- **Source:** a self-similar layout. Each new word is sized as a fraction of the bounding box of everything already written, dropped right of the box or on a new line below it, alternating. The camera pulls back exponentially, so every word arrives at about the same on-screen size.
- **Extra:** a hand-solved cubic-bezier ease, and a radial motion blur shared by one tweened amount multiplied by each word's distance share.
- **Port:** a hook device for 3–6-word openers ("Bạn sinh năm **1990**?"). Time the words with `w.t` instead of a fixed STEP of 0.52 s.
- **Gotchas:** Helvetica Neue does cover Vietnamese on macOS, but swap it to the token font. lh 0.78 plus uppercase plus a mask is the worst case (G3). Layout measured with no font gate (G4).

**14. `caption-editorial-emphasis` and `caption-highlight` (B, M).**
- **Source, editorial-emphasis:** word list `{text,start,end}`, the same shape as our words. A dual-font system (Inter body, Playfair Display 800 italic for emphasis words) with large size contrast.
- **Source, caption-highlight:** a TikTok-style background sweep behind the active word.
- **Both:** fit-to-width with a canvas `measureText` loop. Fixed 1920 px safe zone (`top:580px`).
- **Port:** add both as caption *skins* to `engine.js` caps, not as components. Playfair has a Vietnamese subset and suits BUD emphasis words; Montserrat (caption-highlight) is fine too.
- **Gotchas:** lh 0.9–1.0 with `overflow:hidden` (G3). `measureText` runs before the font loads (G4). Do not take `caption-pill-karaoke`, `caption-clip-wipe` (Poppins) or `caption-particle-burst`/`neon-glow` (Outfit). Those fonts have no Vietnamese.

### 2.3 Emphasis and annotation

**15. `marker-highlight` (A, S).**
- **Source:** text settles in (0.55 s). At `draw_at`, one hand-drawn SVG stroke draws over the first case-insensitive match of `emphasis_word`. Styles are highlight, circle, underline or scribble, each a fixed viewBox path with `preserveAspectRatio="none"`. The draw is a `getTotalLength` dash tween over 0.6 s plus a settle pop.
- **Port:** emphasis on the `hot` word, with `draw_at` set to that word's `t`. This is the cleanest annotation device in the registry.
- **Gotchas:** match with NFC on both sides (G5). Word box measured at build (G4). The highlight style sits behind the x-height, so add about 0.15em of top bleed for capital marks.

**16. `vox-annotate` (A, M).**
- **Source:** the marker from #15, plus a connector that draws up from the marker 0.36 s later, plus a mono `note` label that fades in at the connector end after 0.66 s. It is one 0.96 s gesture.
- **Port:** a gloss on a Hán-Việt term, for example "**Bát Nhã**" with the note "trí tuệ". It suits BUD.
- **Gotchas:** the mono label needs `--font-mono: JetBrains Mono` (G2). The label must stay in the 9:16 safe area above the caption band.

**17. `whiteboard-ink` (A, M).**
- **Source:** authored SVG strokes draw one at a time while a pen nib samples `getPointAtLength`, with a short lifted hop between strokes. Cadence is weighted by measured length. There is an empty `<g data-slot="strokes">` for your own paths, and `data-ink="accent"` marks one accent path. IN is 3.55 s.
- **Port:** the Jataka whiteboard (D8 in the 3D report): a lotus, bodhi leaf or la bàn drawn in narration order. Pace stroke groups to word cues instead of total length.
- **Gotchas:** the presets (bulb, flow, rocket) are useless to us, so we must author our own paths. The caption is lh 1.1.

**18. `svg-stroke-trace` (A, S).**
- **Source:** one authored `path` draws over its measured length (1.85 s). A closed path gets a restrained fill afterwards. The hold has one drift cycle.
- **Port:** an ensō circle, a chữ Vạn, or an element glyph traced on cue.
- **Gotchas:** none beyond the path authoring itself.

**19. `hw-*` family: `hw-callout-circle`, `hw-underline`, `hw-arrow`, `hw-box-label`, `hw-boil` (B, M).**
- **Source:** helper APIs (`hwCalloutBuild/On/Off`, `hwMarkPath/On`, `hwBoil`, `hwStrokeApply`, `hwDrawOn`).
  - The **boil** re-poses every N frames from a seeded hash of the quantised timeline time, so it is seek-safe.
  - The stroke matrix offers plain, soft, sharp and spray textures, with a mask clone for sharp and spray.
  - There is a curvature-adaptive pen ease.
- **Port:** copy the helpers into an `annotate.js` device library.
- **Gotchas:**
  - The whole family ships **Caveat-700-latin.woff2**. Caveat has no Vietnamese subset at all, so every handwritten label breaks (G2). Swap to Patrick Hand, Pangolin or Itim.
  - px-sized, and there is no timeline in the components.
  - `hw-write-title` (X) bakes Caveat glyph centerlines, so it cannot be ported to Vietnamese.

**20. `yt-feather-highlight` (A, S).**
- **Source:** `.yt-hl` dims the frame except a feathered ellipse. The ellipse's x, y, rx and ry are CSS variables, and `ytHighlightIn/To/Out(tl, …)` glides the hole between targets.
- **Port:** a spotlight on statue iconography (D11), moving to the mudra and then the lotus seat on word cues.
- **Gotchas:** none. There is no text in it.

### 2.4 Data and stats

**21. `count-up` (A, S).**
- **Source:** precomputes one display string per frame (`frameRows[frame] = format(start+(end-start)·sine.inOut(frame/last))`) and writes them as one `tl.set(el,{textContent:row}, t_frame)` per frame on the paused timeline. That makes reverse and random seeks exact with no update callbacks. Tabular numerals, fixed prefix and suffix, one landing pulse.
- **Port:** a stat or age count ("**108** hạt", "**12** năm"). Land it on the number word's `t`.
- **Gotchas:** the suffix uses the token font. lh 1.0 mask (G3) matters only if the suffix has marks, as in "năm" and "tuổi".

**22. `conic-progress-ring` (A, S).**
- **Source:** a registered `@property` percentage drives the conic-gradient frontier. A radial mask cuts the centre. The centre label is derived from the same value.
- **Port:** "tỉ lệ hợp tuổi 80%". Keep it to *one* ring per video: the ring is the house cliché, so make it carry data or leave it out.
- **Gotchas:** depends on CSS `@property`, which is fine in Chrome.

**23. `chart-story` (A, M).**
- **Source:** bars, line, donut or progress built synchronously from `data`, `labels`, `unit` and `emphasize`. Dashes come from `getTotalLength`. The callout number uses authored frame rows. Labels appear in reading order. IN is 3.3 s.
- **Port:** an FS "vận trình 12 tháng" line, or a BUD statistics bar.
- **Gotchas:** label fonts come from `--font-mono` and `--font-body` (G2). Labels must be short in a 1080 width.

### 2.5 Structure, diagrams and compare

**24. `constellation-hub` (A, M).**
- **Source:** a fixed hub label. N nodes sit on an ellipse at 50 + cos·38%, 50 + sin·39%. Each connector reads its real `getTotalLength` and draws hub → node on `cues` while the node brightens. Then everything settles into one lockup with a subtle orbital drift.
- **Port:** ngũ hành around a "Mệnh" hub, tam hợp, or Tứ Diệu Đế around "Khổ". Cues are the spoken node names.
- **Gotchas:** in 9:16 the ellipse becomes 410×750 px, so re-tune the radii (G7). Node labels use a mask with lh 1.0 (G3).

**25. `radial-surround` (A, M).**
- **Source:** up to 12 hairline chips placed once with cos/sin on an elliptical ring around a `[data-slot="center"]` subject. Optional `close_in`: the chips converge while an edge vignette dims and the centre never moves. Per-chip `cues`.
- **Port:** "12 con giáp vây quanh tuổi bạn", or the six realms around a figure. Put a photo in the centre slot.
- **Gotchas:** chips are mono and uppercase, so set JetBrains Mono and an lh of at least 1.25 (G2, G3).

**26. `grid-card-assemble` (A, S).**
- **Source:** `items` as "Label: body" CSV, laid out as a grid or a list. Each card fades and slides a short way into its own slot with `power3.out`, and a thin-line icon draws on (`getTotalLength`). Per-item `cues`. The hold is perfectly still.
- **Port:** replaces our numbered rows. Use list layout for 9:16 and cue each item to its spoken label.
- **Gotchas:** the item body cannot contain commas, so pass an array in our port. The six generic icons (shield, chart, cloud…) are off-brand, so supply our own paths.

**27. `comparison-split` (A, S).**
- **Source:** before and after panels. The after panel wipes over the before panel along a persistent divider and rests at `split`%. **`orientation: vertical`** gives a horizontal divider travelling top → bottom, which is the native 9:16 "stacked split" (P2 in the earlier report). It dispatches `hf:sfx` "wipe-land-soft".
- **Port:** "kiêng vs nên", or two images.
- **Gotchas:** labels are uppercase (G3).

**28. `testimonial-proof-card` (A, M).**
- **Source:** the quote reveals line by line through soft overflow masks with a 0.18 s stagger. Lines are measured after wrapping. The byline appears, then the `emphasis` substring (expanded to whole words) gets a hand-drawn underline (0.55 s). An avatar slot. A dead-still hold.
- **Port:** a sutra or proverb quote card for BUD ("Kinh Pháp Cú, kệ 5"). The name is the sutra and the role is the chapter.
- **Gotchas:**
  - The `line-height:0.6` is only on the decorative quote glyph. The real risk is that the per-line masks are measured after wrapping, at build time (G4), and the masks must clear stacked marks (G3).
  - Font size is fitted by `Array.from(quote).length`, which is NFC-sensitive (G5). Initials use `Array.from(part)[0].toUpperCase()`.
  - The company mark is uppercase mono.

**29. `spring-stack-shuffle` (B, M).**
- **Source:** 3–5 slotted cards. On each cue the back card throws over the top to the front with mass and overshoot. Interruptible-spring redirects work as follows: the covering segment is cut analytically and continued with a Hermite ease whose start slope equals the cut velocity. Everything is still compiled to `fromTo` tweens, so it is seek-safe.
- **Port:** a "rút quẻ" (draw a lot) or tarot-like reveal for FS, with a card per sign.
- **Gotchas:** complex code. Copy it whole rather than re-implementing.

**30. `pendulum-swing` (B, S).**
- **Source:** one unitless `--hf-swing-angle` eased 1→0. The rotation is a damped oscillation about the top pivot (18°, 34° or 52°).
- **Port:** a hanging câu đối or lồng đèn sign entering on a Tết beat.
- **Gotchas:** no timeline (X1). Write the tween yourself.

### 2.6 Camera and reframing

**31. `scroll-camera-story` (A, M).**
- **Source:** a tall world (100 + `travel` cqh) moves past the camera top to bottom. There are four parallax depth layers, and sections rise as the camera reaches them, ending in a held final section.
- **Camera law:** all camera state lives in one plain object, and a single writer derives every transform. Integer sine micro-drift cycles end at exactly zero. Sections come from a host-level `<template data-slot>`. `cues` set the section arrival times.
- **Port:** it is already vertical. Use it for the almanac strip (P3) or a lineage or timeline (D10).
- **Gotchas:** its own comment is the warning: never tween cq units (G6). Mono section labels (G2).

**32. `pull-back-reveal` (B, S).**
- **Source:** tight on a stat chip, then a whip-out pull-back reveals the headline and two supporting cards (2.4 s IN). The chip is the same DOM element throughout.
- **Port:** the "macro → whole" P5 beat: "**3** điều kiêng" pulls back to the full list.
- **Gotchas:** lh 0.9 plus uppercase (G3).

**33. `camera-shake` (A, S).**
- **Source:** nine profiles (handheld normal, wide or tele; rig 6D) from Cinemachine noise presets. Each axis is a sum of three octaves of `cos((f·t+φ)·2π)·A`. The lens model includes overscan and `data-cs-z` depth layers. It is driven by a property setter on a tweened `driver.t` (G6).
- **Port:** `HF.camera.shake(tl, rig, {profile, at, dur})` under media scenes, using the mild profiles only.
- **Gotchas:** none. There is no text. It overscans, so the image needs bleed.

**34. `yt-camera-move` (A, S).**
- **Source:** `ytCameraMove(tl, el, at, {zoom, slideX/Y, tilt, pan, roll, dur, ease})` is one tween with `transformPerspective:1200`. `ytCameraReset` returns to rest, and `ytDefocusPulse` adds an edge-blur overlay.
- **Port:** Ken Burns and punch-ins on photos.
- **Gotchas:** it calls `gsap.set` outside the timeline for perspective (static, harmless). `backdrop-filter` defocus is costly at 1080×1920.

**35. `focus-rack` (B, S).**
- **Source:** card A starts near and sharp while B is far, blurred and dim. One 0.7 s rack moves blur, scale and parallax together.
- **Port:** "điều bạn nghĩ → điều thật sự", a two-depth contrast.
- **Gotchas:** blur filters are costly. lh 0.94 plus uppercase (G3).

### 2.7 Media, transitions and texture

**36. `ink-bleed-reveal` (A, M).**
- **Source:** 4–6 seeded ink blobs bloom and merge, then the puddle contracts as a slotted mark resolves crisp. The gooey blur plus alpha threshold runs in a **canvas work buffer** redrawn from (table, t), not as a live SVG filter (G6). The paper grain is a static fixed-seed `feTurbulence`.
- **Port:** the BUD signature reveal: ink blooms into a chữ Hán, a lotus, or the channel mark. The slot is `<template data-slot="ink-bleed-reveal-mark">`.
- **Gotchas:** the canvas raster basis is measured once at mount, so mount it after layout. Light paper is the home register, which matches the BUD parchment plan.

**37. `torn-paper-rip` (A, M).**
- **Source:** a fibrous tear (low-frequency wander plus per-vertex jitter, LCG seed `0x7a9e11cf`) travels across the frame. The from-sheet lifts away on a growing shadow, and the exposed paper core shows in cream, kraft or white. IN is 1.0 s: `power2.in` for the first 20%, then `power3.out`. Uses from and to `<template data-slot>`s.
- **Port:** the FS chapter seam, in a giấy dó or Tết red-paper look.
- **Gotchas:** the `direction` enum is left/right only, so for a portrait top→bottom tear you rotate the geometry yourself.

**38. `paper-collage-reveal` (A, S/M).**
- **Source:** 4–8 seeded torn scraps (deckle edges, grain, cast shadows) lift away on arcs, one by one, to uncover a content slot. IN is 1.35 s.
- **Port:** the FS scrapbook or almanac reveal of the hero photo.
- **Gotchas:** SVG deckle filters use fixed seeds but cost GPU time; test render time.

**39. `halftone-dissolve` (A, S/M).**
- **Source:** scene A dissolves to B through a halftone dot grid. Dots pop smallest-first and then open as windows onto B. Each dot radius is a pure function of (grid position, t) from a seeded threshold map (ltr, center or noise). The ink is painted on a canvas and B's `clip-path` is rebuilt on every frame.
- **Port:** the FS print-poster seam (bold-poster preset).
- **Gotchas:** the raster basis is measured once at mount.

**40. `cut-the-curve` + `whip-pan-cut` (A, S).**
- **Source, cut-the-curve:** velocity-matched hard cut. OUT is `power4.in` over T·cutFraction (0.33). IN is `power4.out` over the rest, with the incoming distance derived so the seam velocity matches. Matched blur at the cut.
- **Source, whip-pan-cut:** both scenes ride one strip on a single `power3.inOut` tween. Directional `feGaussianBlur (X 0)` is capped at 16 px and peaks mid-whip.
- **Both:** fire `hf:sfx` ("whip-cut").
- **Port:** the default energetic seams between lines. `CUT_AT` is the boundary word's `t`. Map `hf:sfx` to our whoosh SFX.
- **Gotchas:** the direction enum is lateral in whip-pan-cut. For 9:16, also allow up and down (cut-the-curve already supports them).

**41. `fade-through` (A, S).**
- **Source:** the outgoing layer fades, a wash (paper, white, ink or accent; flat or bloom; strength 0.1–1) peaks, and the incoming layer reveals. Recipe only (X1).
- **Port:** the calm BUD seam (with `wash:paper`, `shape:bloom`).
- **Gotchas:** none.

**42. `cinemagraph` (B, M).**
- **Source:** the frame is frozen except one feathered window. The demo is steam drawn on a canvas from the seek time alone, with a period that divides the duration so the loop is seamless. The recipe: a base looping video, a freeze-frame still above it, and the feathered window moved onto the still.
- **Port:** incense smoke over a still altar photo, or a candle flame. Our own seeded smoke painter goes inside the window.
- **Gotchas:** 1920 px layout. "One living region per frame".

**43. `particle-image-reveal` (B, M).**
- **Source:** a seeded particle field (LCG `0x50a71c1e`) converges while the slotted image reveals beneath it, left-to-right or as a centre iris. The canvas is redrawn from scratch per frame. The hold must be truly still to keep frames byte-identical.
- **Port:** the "relic or statue materialises" beat for BUD.
- **Gotchas:** particle counts at 1080×1920 increase render time.

**44. Atmosphere: `starfield` / `aurora-drift` / `grain-field` / `mk-background` (B, S).**
- **Source:**
  - `starfield`: seeded stars in three tiers, each twinkling an *integer* number of sine cycles per mount so t=0 equals t=D, with two parallax layers and a radial centre mask.
  - `aurora-drift`: three blurred accent fields over one normalised sine phase.
  - `grain-field`: a dot field.
  - `mk-background`: two radial blobs.
- **Port:** an "ambient layer" device whose loop length equals the short's duration. `starfield` suits Rằm or night themes, `aurora-drift` re-tinted gold suits BUD dawn, and `mk-background` makes a warm paper wash.
- **Gotchas:** `starfield` is a 1920 px block with a mask of 230/653 px, so re-centre it for portrait. Do not use the WebGPU `aurora` or `godrays` blocks. Do not use `grain-overlay` either, because it uses CSS keyframes (G8).

**45. `organic-light-leak-overlay` + `editorial-flash-overlay` (B, S).**
- **Source:** finite CSS layers (warm radial gradients with `mix-blend-mode:screen`), driven by the timeline: opacity 0 → 0.46 at 42% → 0 at 68% of the duration. Also a neutral-warm camera-flash cut.
- **Port:** memory or Jataka beats (light leak) and the FS reveal flash. Overlay devices of about 1 s, cued to the seam.
- **Gotchas:** sized 1920×1080 with `inset:-16%`; re-size to the portrait frame.

**46. `vignette` (A, S).** A pure CSS radial vignette with no motion. Put it on the shared `#bg` layer once per video.

### 2.8 Titles, end cards and the shader port

**47. `titlecard-lockup` (A, S).**
- **Source:** a mono kicker fades up, the wordmark settles from scale 0.96 → 1, a hairline rule draws (`getTotalLength`), and a label appears. IN is 1.8 s, then a dead-still hold.
- **Port:** a chapter or "breather" card and the BUD channel lockup.
- **Gotchas:** the kicker and label are uppercase mono (G2, G3).

**48. `logo-sting` / `cta-close` (B, S).**
- **Source, logo-sting:** the wordmark lands from scale 1.15, then one accent ring and one frame of white. IN is 0.95 s.
- **Source, cta-close:** a 2–4-word action line lands per word with a character-aware fit (70–85% width), then a capsule pops with one overshoot.
- **Port:** the channel sting and the "Theo dõi để xem phần 2" close.
- **Gotchas:** the character-aware fit counts characters, which works for Vietnamese because NFC letters are single code points. lh 0.9–1.0 (G3).

**49. Shader seam GLSL from `light-leak`, `domain-warp-dissolve`, `cross-warp-morph` (B, M).**
- **Source:** each block is a showcase. It rasterises two demo DOM scenes into canvases with a *toy* text-only `captureScene()`, uploads them as textures, and runs one fragment shader `mix(u_from, u_to, u_progress)` from the timeline `onUpdate`. The light leak uses Beer–Lambert falloff with ACES tone mapping.
- **Port:** take only the fragment shaders into the shader infrastructure we already use for end cards, and feed them real frame textures. Do not use `captureScene`: it drops images and draws only centred text.
- **Gotchas:** the demo pulls Bebas Neue, Lato and Space Mono from Google Fonts, but that text is demo-only. Drive the shader from a driver setter rather than `onUpdate` (G6).

**50. `world-map` (B, M).**
- **Source:** a D3 Natural Earth choropleth with country-by-country reveal, tooltip labels and a rotating globe inset. It calls `d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json")`, and the timeline is built in the async `then`.
- **Port:** a pilgrimage route (Lumbini → Bodh Gaya → Sarnath → Kusinara) or a "Phật giáo truyền vào Việt Nam" map. Vendor the topojson locally and build synchronously. Add a route draw (the `nyc-paris-flight` idea) with our own path.
- **Gotchas:** network fetch (G8). At 110 m resolution, Vietnam and Nepal are coarse; consider 50 m. 1920 px layout.

**Also B, no card (pattern is the same as a card above):**
- `char-slam-explode` (like 4)
- `type-match-cut` (like 8)
- `kinetic-center-build`: MIT, keep the Remocn notice. It uses Geist, so swap to the token font.
- `svg-mask-reveal` and `texture-mask-text`: text-as-window, P8. The textures are CC0.
- `inline-highlight`, `mk-specs-list`, `mk-progress-stat`, `mk-line-graph`, `stagger-cascade`, `split-tilt-cards`, `before-after-wipe`, `focus-swap`, `flowchart-vertical` (native 1440×2560), `offset-path-traveler`
- `pan-stations`: rotate it to a vertical pan.
- `push-in`, `drift-hold`, `freeze-frame-dressing`, `grade-split-reveal`, `mk-placeholder-grid`
- `iris-reveal` and `morph-swap`: use as accents only.
- `curtain-reveal`, `hw-pipeline`, `hw-frame`, `hw-scribble-transition`, `marker-checklist-card` (swap Permanent Marker and Courier Prime), `titlecard-calm`, `gloss-sweep`, `extended-keyframe` (use its `EK.ease()` alone), `soft-blur-in`, `focus-blur-resolve`, `per-word-crossfade`, `slot-machine-roll`
- Caption skins `caption-highlight` and `caption-pill-karaoke`: take the mechanism only, because Poppins has no Vietnamese.

---

## 3. Recommended install and port strategy (licensing and determinism)

**3.1 Port into engine devices. Do not mount sub-compositions.**
- The engine is one paused GSAP timeline that builds scenes in JS from `LINES`.
- Mounting with `data-composition-src` plus `data-variable-values` works in 0.8.75 (verified in the runtime). But every mount brings its own timeline, its own font-size fit and its own `#root` CSS. The runtime would then seek N timelines, and the device could not see `ln.words` timing except through string `cues`.
- **Port the logic** into `compositions/devices/<name>.js`. Each device exports `build(stage, spec, ctx)` and writes tweens into the master `tl` at `ctx.at`. Keep the source's envelope law (IN, elastic HOLD, OUT; compress when the line is short; never `timeScale`). Keep its seeded tables and its `fromTo` discipline.
- Keep mounting only for the rare self-contained block that has nothing to sync, such as an ambient layer. Even then, prefer the port.

**3.2 Snapshot, do not `hyperframes add` on a working branch.**
- `hyperframes add` fetches `main` HEAD every time. The registry moves fast: `main` was pushed on 2026-10-14, the day of this research. The installed copy then drifts from what was reviewed.
- Vendor a **read-only snapshot at a pinned commit** instead, for example `third_party/hyperframes-registry/<sha>/<blocks|components>/<name>/`, with the fetched `registry-item.json` beside each item. Keep it out of `compositions/` so lint and render never load it.
- The fetch is a plain GET of `https://raw.githubusercontent.com/heygen-com/hyperframes/<sha>/registry/<type>s/<name>/<file>` for each file in the item's `files[]` (this research used `main` at about `d77b03c`).
- If an item is ever installed with `add`, do it on a throwaway branch, run `hyperframes check`, render a snapshot, then copy the result in.

**3.3 Licensing and attribution checklist.**
- **Apache-2.0** (repo default; covers 407 items whose manifest has no `license` field). Ship a copy of the Apache-2.0 LICENSE in `third_party/hyperframes-registry/`.
  - Give every ported device a header: `Ported from heygen-com/hyperframes registry/<type>/<name> @ <sha> (Apache-2.0). Modified: <what changed>.` Section 4(b) requires stating changes.
  - Keep any NOTICE. The repo root has no NOTICE file; the raw request returned 404.
  - The `author` field (Jake Moran, Miao Yang, Stronkter, HeyGen) is credit, not a different licence. Keep it in the header.
- **MIT items: `kinetic-center-build`, and the Remocn part of `caret-swap`.** Copy the full MIT notice ("Copyright (c) 2026 Remocn …") verbatim into the ported file.
- **shaders.com blocks ("Apache-2.0 AND MIT").** We do not recommend using them (WebGPU). If ever used, keep `lib/shaders.THIRD-PARTY-LICENSES.txt` next to the library. It covers shaders 4.0.0 (MIT) and typegpu.
- **Fonts.** Do not redistribute the registry's Latin-only font files at all; they are useless for Vietnamese. If an OFL face is ever shipped, as `weight-wave` (Recursive) and `caret-swap` (Geist) do, include the OFL-1.1 text and do not sell the font alone. Our own faces (Be Vietnam Pro, Lora, JetBrains Mono, EB Garamond, Patrick Hand and others) are OFL from Google Fonts.
- **Textures** (`texture-mask-text`, `caption-texture`): ambientCG, CC0. No attribution is required, but note the source.
- **Brand depictions** (`*-exchange`, `ios26-*`, `spotify-card`, `tiktok-follow` and others) are X anyway. Do not ship third-party trademarks in channel videos.

**3.4 Determinism checklist for each port** (from the source patterns plus our `motion-scene-dev` rules).
1. No `Math.random`, `Date.now`, `performance.now` or `requestAnimationFrame`. Use seeded tables built once, with the engine's `mulberry32` and a seed derived from the line. All 4 items that had real `Math.random` or `Date.now` are X 3D blocks.
2. Every per-frame painter (canvas, derived transforms, colour interpolation) runs from a **driver-property setter**, as in `camera-shake`, or from a tween's own `onUpdate` that is verified under seek. Never use `tl.eventCallback("onUpdate")`. The painter redraws from scratch from (table, t), with no accumulators.
3. Use `fromTo` with both endpoints authored. Replace any `gsap.set` outside the timeline that the source uses for initial state (`mk-emphasis-type`, `yt-camera-move`).
4. Tween numbers (px or %), **never cq strings** (G6). Measure once after `document.fonts.ready` (G4), then build.
5. No CSS `@keyframes`, `animation` or `transition` for motion (`grain-overlay` is out).
6. No network at render: strip GSAP CDN `<script>` tags (the engine already loads GSAP 3.14.2), strip Google Fonts `<link>`s (use the engine's fonts or the 0.8.75 `fontLocalize`), and vendor topojson.
7. NFC-normalise all copy before splitting or matching (G5). Strip `**` markers.
8. Vietnamese mask rule: `line-height ≥ 1.25`, or pad masks by 0.22em in block direction (G3).
9. Verify each device with a seek-order test: render frames at t in shuffled order, compare hashes, then run `hf_qa` on a contact sheet. Generation 2 sources already claim "eventful seeks land identical frames"; keep that property.

**3.5 Suggested order of work** (value ÷ effort).
1. **Token shim and font rules** (G1–G3): S. This unlocks every Generation 2 port.
2. **Text devices:** `per-word-rise` (landEase), `line-swap`, `kinetic-type-swap`, `marker-highlight`/`vox-annotate`, `count-up`, `number-wheel`.
3. **Structure:** `grid-card-assemble` (replaces numbered rows), `comparison-split` vertical, `constellation-hub`/`radial-surround` (FS diagrams), `testimonial-proof-card` (BUD quotes).
4. **Seams and atmosphere:** `cut-the-curve`, `fade-through`, `torn-paper-rip` (FS), `ink-bleed-reveal` (BUD), `halftone-dissolve`, `camera-shake`/`yt-camera-move`, ambient `starfield`/`aurora-drift`.
5. **Later:** `scroll-camera-story`, `whiteboard-ink` (needs authored paths), the `hw-*` library with a Vietnamese handwriting face, `split-flap-board`, `world-map` with local topojson, and the shader-seam GLSL.

**3.6 Things the registry does not have** (hand-build, or file a `hyperframes feedback --search-miss`):
- No Vietnam or Asia map.
- No vertical text rail for Hán-Nôm.
- No lunar-calendar tear-off.
- No 12-sign zodiac wheel.
- No Vietnamese-capable handwriting write-on (`hw-write-title` is Latin-baked).
- No grapheme-aware text splitter (only one item uses `Intl.Segmenter`).
- No caption skin that ships a Vietnamese-subset display font.

---

## Appendix: reproduce

Scratch files are in `scratchpad/research/` and none are in the repo:
- `registry_src/registry.json`: the manifest index.
- `registry_src/manifests/*.json`: 447 item manifests.
- `registry_src/src/<name>/…`: 598 source files.
- `scan.py`, `scan2.py` … `scan5.py` produce `scan.json`.
- `gen_table.py` produces `table.md` and `classes.json`, which holds the A/B/C/X and category of every item.
- `fonts_subsets.txt`: the Google Fonts subset check.
