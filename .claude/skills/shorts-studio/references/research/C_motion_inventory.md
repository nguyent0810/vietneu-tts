# C. Motion and device inventory for a reusable narrated 9:16 Shorts engine

Read-only research, 2026-10-14. No repo files were changed.

**Target.** A generic engine for 1080×1920 narrated Shorts of 25–40 s with Vietnamese TTS, on HyperFrames: one paused GSAP timeline, seek-safe and deterministic. Topics include feng shui (FS), Buddhism (BUD), history, science explainers and finance.

**Sources.** Every file was read. All paths are under `~/.claude/skills/`.

- `hyperframes-animation/`:
  - `SKILL.md`, `rules-index.md`, `blueprints-index.md`, `techniques.md`, `references/motion-blur.md`
  - all 48 `rules/*.md` and all 22 `blueprints/*.md`
  - `transitions/{overview,catalog,TRANSITION-REGISTRY}.md` and all 13 `transitions/css-*.md`
  - `adapters/animate-text.md`, plus the ease table in `adapters/gsap-easing-and-stagger.md`
- `faceless-explainer/references/{motion-language,cut-catalog}.md`
- The repo's own scene catalog, `.claude/skills/motion-library/SKILL.md` (headings only), so that devices can map to the existing `wheel/elements/years/list/timeline/compare/stat/doc/quote/map/word/illus/endcard` kinds.

**Relation to earlier reports.** These are in `../`:

- `hf_kinetic_type.md` covers kinetic type, the Vietnamese splitting and mask rules, the beat grammar and the seam snippets.
- `hf_visual_composition.md` covers layouts P1–P15, media treatments, the transition registry and registry blocks.
- `hf_3d_whiteboard_chart.md` covers Three.js, whiteboard, charts and device sketches D1–D12.

This file does not repeat their detail. It cites them as **[KT]**, **[VC]** and **[3D]**, adds the full rule, blueprint and transition inventory, and builds the device taxonomy and the variety engine on top.

**Legend.** Doc numbers are quoted from the rule files. *(own)* marks my engineering judgement, not doc content.

- **Fit for narrated Shorts.** ★ = core, ● = use situationally, ○ = rare or one-off, ✕ = skip (UI/product-specific).
- **Energy.** C = calm, M = medium, H = high.
- **VN risk** (Vietnamese diacritic risk):
  - L = safe
  - M = needs care (padding, blur caps, font check)
  - H = breaks marks unless it is restricted (digits only, word-level only, or extra mask padding)
- **Beat purposes:** hook, reveal-number, compare, list, process, quote, emotional, payoff, transition, ambient, plus place, time, story and evidence where relevant.

---

## 0. Doctrine that every device must obey (short; details in [KT] §2 and [VC] §0)

1. **Smooth beats bouncy.**
   - `power3.out` is the house settle. `expo.out` and `power4.out` give punch.
   - `back.out` and `elastic` are a "rare, explicitly-playful exception", `OVERSHOOT ≤ ~2`. Prefer `springEase` with ζ 0.80–0.85 for "alive, not bouncy".
   - Several rules still ship `back.out` defaults: hacker-flip, scale-swap, orbit, avatar-cloud, ticker, press, circle marker, ai-box, reactive-displacement. The engine must override them, except at the one budgeted overshoot moment.
2. **Sequential reveal in the back ~50% of each beat, timed to the VO.** Do not dump everything in the first 25%.
3. **"I'd rather have NO motion than BAD motion."**
   - No lazy breathing and no slow push or pan in the back half.
   - The only sanctioned hold aliveness is subtle jitter: `SCALE_AMP 0.008–0.015`, `Y 2–3px`, period 1.5–3 s.
4. **Internal seams are velocity-matched cuts** (cut-catalog). Between frames, a transition is the exit; exits are banned except on the final scene.
5. **Determinism.**
   - One paused timeline, `fromTo` with explicit from-states, index-hash pseudo-randomness.
   - No `repeat:-1`, no CSS `transition` or `@keyframes`.
   - Transforms and opacity only (never `width/height/top/left/fontSize/letterSpacing`).
   - Group stagger total ≤ ~0.5 s. Climax dwell ≥ 1 s.
6. **Variety laws in the docs.**
   - "Different entrance per phrase" and "vary the motion axis".
   - "≥3 different framings per video; never the same framing twice in a row".
   - "Every composition should use at least 3 different easings".
   - "No more than 2 independent tweens with the same ease in a scene".
   - "The slowest scene should be 3× slower than the fastest".
   - "Pick ONE primary transition (60-70%) + 1-2 accents".
7. **Portrait geometry (9:16).**
   - Stack vertically. The hero sits at y ≈ 0.42 H (≈806 px).
   - Keep the bottom ~17% (≈326 px) for captions. The hero fills 40–60% of the frame. Use ≥3 depth layers.
   - Hero text spans 60–80% of the width. In feed: body ≥32 px, headlines ≥90 px.
   - *(own)* Also keep key content out of the Shorts right-hand action rail (≈ right 140 px between y 900–1650) and the title/channel overlay (≈ bottom 300–420 px). In practice the usable "hero box" is about x 60–940, y 180–1500.

---

## 1. Rule inventory: all 48 rules

Rows are grouped by the rules-index categories. "Key params" quotes the documented ranges. The 9:16 column states what changes from the 1920×1080 defaults.

### 1a. Text and typography (12)

| Rule | One-line effect | Key params (doc) | Best beat purpose | Energy | 9:16 notes | VN risk |
|---|---|---|---|---|---|---|
| ★ **kinetic-beat-slam** | Short phrases slam in on ONE `BEATS[]` grid. Each has a distinct entrance (scale+blur slam / side-snap / rise-rotate), then a locked finale. | BEATS spacing 1.2–1.8 s (<0.8 frantic, >2.5 loses pulse); entrance 0.35–0.6 s; exits ≤0.25 s; 1 accent hue; display ≥150 px heavy; ≥3 easings (`power4.out` default, `expo.out` snap, `circ.out` heavy rise, `back.out(2)` accents only). | hook, emotional punch, payoff tagline | H | Stack the 2–4 phrases vertically. At 150 px+ a 900 px measure holds only ~6–9 Vietnamese syllable-characters per line, so phrases must be 1–3 words. In narration, BEATS = VO word onsets, not a metronome. | M: the doc fonts (Archivo Black/League Gothic/Oswald) need a Vietnamese coverage check. Keep the slam blur peak ≤10 px and clear it to `none`. |
| ★ **waterfall-entry** | Per-word whip-in from below with binary opacity (`tl.set`), overlapping into an accelerating cascade. | Y 60–80 / 40–50 / 30–48 px (anchor/normal/light); dur 0.16–0.20 / 0.13–0.16 / 0.10–0.13 s; overlap 0–2 frames; `power4.out`/`expo.out`; one direction; final word can split into fragments. | statement/answer, list intro, title | M–H | Ideal in portrait: words wrap to 2–3 centered lines. Pair with `nudge-curve` to slide the block up afterwards. | L (word = syllable, `nowrap` per word) |
| ★ **asr-keyword-glow** | One linear driver gives every word an attack→sustain→rest envelope of glow and scale. The karaoke variant keeps inactive words dim. | ATTACK 0.1–0.25; RELEASE 0.2–0.5; REST 0.15–0.4 (karaoke 0.05–0.2); MAX_BLUR 15–25 (karaoke 30–45) px; SCALE_BOOST 0.03–0.10 (karaoke 0.15–0.25); brand/key word window 1.5–2×; dwell ≥1 s; driver ease `none`. | quote/scripture, emphasis inside any statement | M | 5–10 words per line. Set `maxWidth = safe/1.25` for karaoke scale, and `overflow: visible`. | M: a 30–45 px text-shadow halo muddies dot-below marks. Use a low-alpha glow color and word-level spans only. |
| ● **gradient-text-sweep** | A gradient moves *through* the glyphs (`background-clip:text`). Three forms: continuous sweep, word-to-word highlight, and hue-sweep that settles to solid. | SWEEP_SPAN 200–400% (>100% or no-op); SWEEP_DUR 1.2–3 s `none`; WORD_LAG 0.25–0.5; HOT_RISE 0.15–0.3 / FALL 0.25–0.45; HUE 40–180° over 0.8–1.6 s; settle snap 0.1–0.35 s; position axis inverted (100%→0% = L→R). | payoff word, title hold, "gold" lucky word (FS), quote hold | C–M | No change. | H: the clip box must include the mark zone (padding/negative-margin trick, [KT] §3.3). Stacked twins must be pixel-identical. |
| ● **3d-text-depth-layers** | Text rendered N times at stepped offsets and alpha, giving a stacked extrusion. | LAYER_COUNT 4–6; OFFSET 1–3 px (>4 reads as glitch); back alpha 0.6–0.85 step 0.08–0.15 floor 0.1–0.2; font 200–340 px hero (≥60 min); cascade 0.04–0.10; grow 0.4–0.8 s; no per-letter anim on top; no `text-shadow`. | hero number/word reveal, payoff (once per video) | M–H | Only one short word fits at 200+ px over 900 px (≈4–6 chars). | M: every layer repeats the marks, so offsets should be ≤2 px and tracking ≥ −0.02 em. |
| ● **hacker-flip-3d** | Per-character `rotateX` 90→0 flip while cycling seeded glyphs, then settles on the real character (decode / split-flap). | font 6–10% of min dimension (65–108 px at 1080 w); FLIP 0.4–1.0 s; CHAR_STAGGER 0.03–0.08; REVEAL_THRESHOLD 0.5–0.7; flicker every 3–6 frames; ghost placeholder required; `perspective` on root; no chrome around it. | reveal-number (year/date/price), mystery hook word | H | Center it. Years read well at ~180–220 px (*own*: above the doc's 6–10% because a 4-digit year is the hero). | H for letters: the glyph pool flashes wrong-tone words. Use the digit pool only. With a bottom hinge, dot-below marks swing. |
| ★ **vertical-spring-ticker** | Slot machine: additive spring steps inside a masked window. | ITEM_HEIGHT ≈1.25×font (VN: 1.4×, [KT]); window = item height exactly; STEPS 1–4; STEP_DUR 0.3–0.7; STEP_SPACING 0.3–0.5 ≤ STEP_DUR; BOUNCE 1.4 gentle / 2.0 firm / 2.5+ climax; never swap `innerHTML`; dwell ≥1 s. | list (years, signs, options), reveal-number odometer | M–H | The masked window is 30–60% of width, so it fits easily. A fixed anchor label above suits portrait. | H: the mask clips stacked capitals unless the item height is 1.4× and pixel-exact. |
| ★ **counting-dynamic-scale** | A number counts up while its transform scale grows to the static final size. The suffix lands after the count. | 2–3 digits ideal; START_SIZE 40–60% of END; COUNT_DUR 1.2–2.5 s; `power3.out` ⭐ (power2/expo ok); suffix 0.3–0.6 s, bounce 1.4–2.0 (the sanctioned overshoot); label before the count peaks; `tabular-nums`; `Math.round`; no `back` on the number. | reveal-number, hook stat | M–H | Number at y≈0.35–0.42 H, label as BIG text below. A 4+ digit `vi-VN` value ("84.000") needs a wide box, so put the unit in the label. | L (digits). Suffixes like "năm/tuổi" are fine. |
| ★ **discrete-text-sequence** | Whole text states `{t,text}` are swapped by reverse search. Covers typing, typos, backspace, bulk paste, token swaps and bg-invert flips. | keystrokes 0.06–0.20 s apart; word pauses 0.3–0.6; think hold 0.8–2.0; smooth slice `chars×0.06–0.12 s`; blink one cycle per 0.5–0.8 s; `min-width` on the wrap; instant jumps only. | hook (typed question), token-swap list, correction ("sai→đúng"), CTA build | M | Use short lines. A long typed line needs `camera-cursor-tracking` because 1080 px is narrow. | H if it is sliced by UTF-16 index. Slice a grapheme array (`Intl.Segmenter`); prefer word-level states. |
| ● **dynamic-content-sequencing** | Utility. Computes each item's window from its content length; adds an accelerating "flurry" cadence. | BASE 0.6–1.5; SEC_PER_CHAR 0.03–0.06 ("lean high" for VN: 0.05–0.06); HOLD_MID 0.5–1.0 < HOLD_FINAL 1.0–2.0; N 3–6. Flurry: HOLD_START 0.8–1.2, DECAY 0.75–0.88, FLOOR 0.15–0.3, brake ≥4× floor, 12–18 states allowed. | list/roll-call timing, reading-time checks | n/a | n/a. With narration, the VO timestamps drive timing; use this for flurries and as a reading-time lint. | L |
| ● **context-sensitive-cursor** | The caret color and height follow the segment being typed. Blink is a sine square wave. | 3–4 segment colors; cursor 8–24 px wide, 0.85–1.0× font tall (1.1–1.25× on brand); blink period 0.6–1.2 s in whole cycles; TYPING_GRACE 0.15–0.3 s; monospace; `white-space:pre`. | typed hook, search-bar question | M | Fine. | M: needs a monospace face with Vietnamese (JetBrains Mono ok). |
| ● **chromatic-glitch** | RGB-split or slice displacement on a hash of *quantized* time, then a hard snap to sharp. | MAX_SPLIT 4–14 px; JITTER_STEP 1/30–1/12 s; GLITCH_DUR 0.25–0.6 entrance / 0.12–0.2 burst; SPLIT_OPACITY 0.5–0.9; slices 4–10, offsets 12–60 px; clamp the rest state; base copy on top. | hook disruption, myth-bust, "warning" contrast | H | Fine. | H: ghost copies read as extra accent marks. Cap MAX_SPLIT at 4–6 px, and slice bands must include the mark padding. Not for BUD; FS at most once. |

### 1b. Data and stats (2; counting-dynamic-scale is listed above)

| Rule | Effect | Key params | Purpose | Energy | 9:16 | VN |
|---|---|---|---|---|---|---|
| ★ **stat-bars-and-fills** | Number plus graphic: growth bars (`scaleY`), progress bar or ring, fractional star wipe. | bars 4–6, last bar = accent; fill 0.8–1.2 s on the same ease as the count; stagger 0.06–0.1; one accent hue; pick single-focus OR split-frame and keep it for the whole video; origin bottom/left. | reveal-number, compare (bars), proportion | M | "Split-frame" becomes top/bottom. Single-focus (number over ring) is the natural portrait form. | L |
| ● **chart-scrub-readout** | A playhead or cursor reads an already-drawn chart. The tooltip steps on index change. Optional activation of a second series. | N 10–40 points; SCRUB 1.5–3 s; `power1.inOut` (or `none` playhead / `power3.out` peak stop); CROSS_P 0.55–0.75; tooltip offset 16–48 px; marker r 6–12; hold ≥0.8 s; data literal and baked. | evidence (finance trend, temperature, population), reveal-number | M | Chart ≈900×600 in the upper half. Flip the tooltip side near the right edge, because the Shorts action rail is there. | L–M (date labels: use short "T3/2024") |

### 1c. Camera and viewport (6)

| Rule | Effect | Key params | Purpose | Energy | 9:16 | VN |
|---|---|---|---|---|---|---|
| ● **coordinate-target-zoom** | Zoom onto an off-center target with nested wrappers: outer scale, inner counter-translate `T = −offset`. | ZOOM 1.5× modest, 3× dominant, 5×+ extreme; target ≤88% of canvas; DUR 1.0–2.0 s; start = layout landed + 0.5–1.5 s; DWELL ≥1 (1.5–2 ideal); measure the offset once after `fonts.ready`. | evidence detail, map zoom-in, payoff focus | M | Raster needs `sourceRes ≥ rendered×S`; a 1080-wide photo cannot zoom 3×. | L |
| ★ **viewport-change** | A single `.world` camera, `translate(x,y) scale(S)` with `T = −offset×S`. Pan, zoom, focus-lock. The extreme 4–12× outward "workspace reveal". | scale guide 1.02–1.05 subtle / 1.05–1.15 emphasis / 1.15–1.3 focus / 1.5–2.5 dramatic / 3+ full; ZOOM 1.0–2.0 s; DWELL ≥1 s; author the world at 1× and open zoomed in, never the reverse. | place/map pan, timeline traversal, zoom-out reveal | M | Vertical pans feel native in 9:16 (a scroll metaphor). | L at the 1× landing |
| ● **multi-phase-camera** | Phased scale (pull-back → neutral → push) plus Lissajous micro-drift, one writer. | PHASE scales 0.88–0.96 / 0.98–1.02 / 1.04–1.15; P2 at 0.3–1.0 s for 1.0–1.8 s; P3 at 2.0–4.0 s for 1.0–2.0 s; DRIFT 2–8 / 1–4 px, 1–3 cycles, ratio 1.2–1.5; patterns: focus-in, dramatic reveal, steady push, bookend pull; shake variant. | push-through between beats, punch-in on a number | C–M | Fine. The doctrine bans slow back-half pushes, so use it only as a front-half or punch move. | L |
| ● **camera-cursor-tracking** | Two-phase camera: static, then locked to a growing focal point (a caret), with continuous `Math.min` math. | CURSOR_TARGET 0.5–0.75 of width; REVEAL `chars×0.05–0.15 s` linear; TRACK 0.8–2.0 s `power2/3.inOut`; build the timeline synchronously (no `fonts.ready` gate); `font-display:block`. | long typed question in a narrow frame | M | *More* useful in portrait (1080 px fits ~22 chars at 90 px). | M: measure the real VN font; proportional widths vary. |
| ○ **3d-camera-flight** | A perspective camera flies leg by leg through a 3D world (dive, tilt-to-flatten, lateral, final dive). One `cam` state, one writer. | PERSPECTIVE 700–1400 (800–1200 for moving); rx 30–55° (≤65), ry ≤30; z budget `cam.z+PROP_Z ≤0.6×P`; dive/land 0.6–1.0 `power4.out`; flatten 1.2–2.0 `power2.inOut`; pan 0.8–1.5 (whip 0.5–0.8); holds ≥0.8; dwell ≥1; no filter/opacity on `.world`. | process journey, calendar/board dive, story world | H | The world can be tall (calendar column). Reads happen only at flat landings. | M: angled text is "texture"; read only when flat. |
| ★ **depth-of-field-blur** | Rack focus: `--dof` blur plus dim on off-focus layers; the focal layer stays sharp. | BLUR_PER_DEPTH 3–6 px; MAX 8/16/24; GRID 6–12; DIM 0.4/0.55/0.7; FOCUS 0.5–1.2 s; rack = shared window; focal breath ≤0.6 px (omit); blur small layers, not full-frame. | spotlight one row/item, compare rack A↔B, list focus | C–M | Fine. | M: blurred VN text turns to mush, which is acceptable only for de-emphasized layers. The focal layer must be at 0. |

### 1d. Layout and network (8)

| Rule | Effect | Key params | Purpose | Energy | 9:16 | VN |
|---|---|---|---|---|---|---|
| ● **avatar-cloud-network** | Avatars or icons on an ellipse with dashed lines drawn *outward* from the hub, then a breathing dwell. | COUNT 8–12; RX 20–30% W, RY 18–25% H, ratio X/Y 1.5–3; avatar 80–120 px; hub 0.4–0.6 s (bounce 1.4–1.8; override to `power3`); avatar 0.4–0.7 s, stagger 0.06–0.10; lines 0.4–0.7, stagger 0.02–0.05; dwell ≥1 s. | process hub (12 signs around a year, causes around an effect, disciples around a teaching) | M | Width-limited: RX ≈ 380, RY ≈ 200 at 1080 w. Use 6–8 nodes and labels ≥32 px. **Counts as a circle.** | L–M (label size) |
| ● **3d-page-scroll** | A tall content card is tilted statically; its content scrolls; a spotlight lands. | tiltY ±4–12°, tiltX 0–6°; perspective 800–2000; SCROLL 0.8–1.8 s `power3.out` (one ease for all scrolls); spotlight 0.4–0.8 s; real DOM, not a screenshot. | evidence document, sutta page, news article, report | M | Native fit: a tall card scrolls vertically. | M: small text on a tilt. Spotlight plus a large font for the cited line. |
| ★ **center-outward-expansion** | Items clustered at the center expand to their slots; can be chorded to a counter. | ITEM_COUNT 3–8 (>8 chaos); EXPAND 1.0–1.8 s `power3.out` (never `in`); STAGGER 0.04–0.08; START_PROGRESS 0–0.5 (0.3 avoids pile-up); the burst IS the beat (label after). | list burst (5 elements, 4 directions), hook counter chord | M–H | Targets on a vertical 2×N grid. | L |
| ● **split-tilt-cards** | Two cards open like a book with opposing `rotateY`, enter from their own sides, then float in counter-phase. | perspective 1000–2400; TILT 10–18°; overshoot 4–12°; gap 40–120; card 480–820 px @1920; entry 0.6–1.2 s; right card +0–0.3 s; float 3–8 px; ≤2 lines of body per card; badges outside the cards. | compare | M | Side by side gives ~430 px cards, which is too tight. *(own)* Rotate the metaphor: stack top/bottom with opposing `rotateX` (±10–14°), entering from top and bottom. | M: tilted body copy blurs. Keep 1–2 short lines. |
| ○ **orbit-3d-entry** | Items flip in place at their orbital start, then orbit an ellipse continuously. | RX 300–900; Y/X 0.4–0.7; 4–25 s per revolution (≥ time on screen); entry 0.4–0.8; stagger 0.06–0.12; rot from ±60–120°, z −200…−400; 4–12 items; label `translateZ(220px)`; ring must clear the label. | ambient cycle (zodiac, planets), "everything revolves around X" | M | RX ≤ 420. **Counts as a circle.** | L–M |
| ✕/○ **ai-tracking-box** | Yellow L-bracket box tracks a moving target; confidence 95–99%. | ENTRY 0.3–0.8 `back`; track 2–8 s, < 0.6 Hz; size jitter 5–10% at a non-integer freq; yellow `#facc15` on dark. | evidence "detection" (science/finance tech only); static HUD-bracket variant for photo framing | H | Fine. | L |
| ● **depth-scatter-assemble** | N elements fly from an index-derived 3D cloud (golden angle) into a flat layout. Tumble-swap and radial-explode variants. | n 4–14; RADIUS 250–700; Z +150…+450 / −150…−500; TUMBLE 40–110° (cap 80 for one-faced); ASSEMBLE 0.7–1.4 `power3.out`; STAGGER 0.03–0.09 (n×stagger < dur); cloud spin 15–60°; SWAP 0.5–1.0 s; resolve flat. | hook "pieces come together", tumble-swap seam between two phrases | H | Fine. | M–H: per-glyph fragments separate letters from their marks only if split wrong. Fragment by word or syllable. |
| ★ **anchored-layout-expand** | An edge-pinned container grows on one axis while the content below rides the same tween (mask + sheet, or proxy counter-scale). | GROW 0.35–0.6 `power3.out` (`back.out(1.1–1.3)` playful); rows start ~25% into the grow, stagger 0.04–0.08, fade 0.2–0.3; COLLAPSE 0.2–0.35 `power3.in`; `data-layout-allow-overflow`. | list accumulation, "chi tiết" detail card, answer card under a question | M | **Native for portrait** (vertical growth). | L (counter-scale keeps glyphs unsquashed) |

### 1e. SVG and icons (2)

| Rule | Effect | Key params | Purpose | Energy | 9:16 | VN |
|---|---|---|---|---|---|---|
| ★ **svg-path-draw** | Stroke draws itself (`dasharray/dashoffset` = measured length); draw-then-fill; ring from 12 o'clock. | segment 0.3–0.8 s; final segment 60–80%; next starts at 70–80% of previous; `power2.out` or `none` (never back/elastic); fill fade `power1.out` after; "a drawn line must land on something". | process arrows, cycles, map routes, underline, whiteboard, rings | C–M | Fine. | L. Never draw VN text as paths; keep text in DOM ([3D] §2). |
| ● **svg-icon-enrichment** | An icon's internal parts animate (rotation, oscillation, pulse, dash flow) via the SVG `transform` attribute. | revolutions 0.5–2 (non-integer if the end is visible), seconds 4–10; pulse 2–4 cycles; dot amp 0.05–0.2; ring amp 0.04–0.12 (< dot); dash offset = integer × period; phase-offset the parts. | ambient on icons (clock hands, compass needle, incense dash-flow, coin spin), process | C | Fine. | L |

### 1f. Idle and ambient (2)

| Rule | Effect | Key params | Purpose | Energy | 9:16 | VN |
|---|---|---|---|---|---|---|
| ★ **sine-wave-loop** | Bounded idle: yoyo (finite repeat) or an `onUpdate` sine phase. "Reach for this last." | SCALE_AMP **0.008–0.015**; Y 2–3 px (4–6 only when gated); period 1.5–3 s (2.5–4 long); CYCLES IDLE/3…IDLE/1.5; N concurrent → amplitude/√N plus staggered periods; settle-and-fade over the last 20% if idle >6 s. | ambient hold (jitter only) | C | Fine. | L |
| ● **ambient-glow-bloom** | A soft radial glow blooms behind a hero, landing on its settle as one beat. Or a one-pass sheen sweep. Or a text-clipped shimmer for "working". | peak opacity 0.15–0.30 (hard cap 0.45); inset −200…−450 px; start scale 0.80–1.0; bloom 0.6–1.4 s; breathe 2.5–4 s period, amp 0.02–0.05/0.01–0.03; sweep width 15–35% (8–15% wordmark), 0.8–1.6 s, opacity 0.10–0.40; shimmer period 1.2–1.8 s, whole passes, killed at resolve. | payoff/number backing, BUD halo, quote hold | C | Fine. Radial glow also prevents the H.264 banding that linear gradients cause ([VC] §0). | L (shimmer-in-text has the same VN risk as gradient-text-sweep) |

### 1g. Transition and motion (14)

| Rule | Effect | Key params | Purpose | Energy | 9:16 | VN |
|---|---|---|---|---|---|---|
| ● **reactive-displacement** | An intruder's entry drives a victim's opposite exit from one driver: a causal collision. | DRIVER 0.6–1.4 s; bounce 1.2–2.0 (blueprint ticker-takeover overrides to a long `power2` settle; use that); VICTIM_FRACTION 0.4–0.5 (cap 0.6); tilt 5–15°; fade sharpness 3–8; dwell ≥1 s. | myth→truth, hero crash-in payoff | H | Vertical collision (dropped from the top, victim shoved down) suits portrait. | L |
| ● **press-release-spring** | Linear press, spring release, optional burst and bg glow; state-change variant (success + check stamp). | PRESS_SCALE 0.88/0.92/0.96; PRESS 0.10–0.30; RELEASE 0.40–0.90; bounce 1.4/2.0/2.8; burst 3/6/8× scale, opacity 0.4–1.0; bg glow 0.1/0.25/0.45; footprint ≥3–5% of canvas; dwell ≥1 s (≥2 s dramatic). | CTA, seal/stamp (FS red seal, "đã kiểm chứng"), confirm | M | Fine. | L |
| ○ **physics-press-reaction** | Cursor and element compress together through one targets array, then release. | approach 0.7–1.3; press 0.1–0.25; release 0.4–0.7 `back.out(1.6/2.0/2.4)`; intensity 0.05/0.10/0.15; hold variant 0.3–0.8; cursor 48–96 px. | CTA tap | M | *(own)* Use a finger-tap glyph instead of a mouse arrow on mobile. | L |
| ○ **cursor-click-ripple** | Cursor moves, clicks, rings expand. | move 0.4–1.0; click +0–0.3; press 0.06–0.12; cursor 0.80–0.90 / target 0.92–0.97; ripple 0.5–1.0 s, scale 3–6, stagger 0.06–0.12; rings in DOM from t=0. | CTA; *(own)* ripple rings alone = pulsing map pin | M | Fine. | L |
| ✕ **cursor-drag** | Grab, ghost travel in lockstep, drop-snap; fill-handle, resize, reorder variants. | travel 0.6–1.2 `power2.inOut`; ghost 0.5–0.75; lift 1.03–1.08; drop exactly at travel end. | (rare) sorting game: drag a year chip into its group | M | Possible, but it reads as UI. | L |
| ✕ **multi-cursor-choreography** | 2–4 labeled cursors working a canvas (collaboration ambience). | legs 0.6–1.2 s; rests 0.5–1.5; action spacing ≥1 s; zones. | none for these channels | M | — | — |
| ● **control-target-sync** | A scrubbed control and its bound target move in the SAME beat (same label, duration, ease), or share one discrete state array. | SCRUB 0.8–1.6 `power1/2.inOut` (no back); HOLD 0.3–0.8; 2–4 beats; visible endpoints; `tabular-nums`; end on a landed edit. | process/what-if ("lãi suất 5%→10%: tiền tăng thế nào"), science parameter | M | Control at the bottom of the hero box, target above. Both must be co-visible. | L |
| ● **scale-swap-transition** | Same-center morph: the outgoing element shrinks and fades (`power2.in`) while the incoming pops in. | EXIT 0.3–0.5; ENTER 0.45–0.7 (doc `back.out(1.4–2.2)`; doctrine: `power3`/spring ζ0.85); OVERLAP 0.1–0.2; EXIT_SCALE 0.6–0.8; incoming on top. | term → meaning, icon → icon, "trước → sau" in place | M | Fine. | L |
| ● **card-morph-anchor** | A container morphs apparent size (uniform scale), radius, background and shadow between two shots. | HOLD 0.6–1.5; MORPH 0.6–1.2 `power2.inOut` (never back); old/new content fades 0.3–0.5 each; radius ≤ half the side; pixel-identical handoff. | bridge: card → badge/pin, rect photo → round seal, last word → CTA pill | M | Fine. | L |
| ● **theme-crossfade-morph** | A whole-theme reskin through N stacked complete layers (opacity only, ~0.3 s) while one anchor never moves. | N 3–5; SKIN_HOLD 0.8–1.5; MORPH 0.25–0.4 (~0.3); adjacent windows only; brake = final hold 2–3×; camera static. | compare ×N ("cùng một chữ qua 4 thời kỳ", currencies, seasons) | M | Fine. | L–M: the anchor must be pixel-identical in every skin. |
| ★ **spring-pop-entrance** | The canonical arrival: `scale 0→1` with a `power3.out` settle; group stagger. | POP 0.4–0.7; stagger `min(0.06, 0.5/N)`; N 3–9 (>9 use a wipe); Y_RISE 0–32; hero visible by t ≤0.5 s; playful: `back.out ≤2` or spring ζ0.6–0.7; origin-anchored variant. | icons, badges, chips, pins, callouts | M | Fine. | L (a brief squash only) |
| ● **motion-blur-streak** | Fake velocity blur coupled to a fast `out` move: SVG `feGaussianBlur` on the axis, or 2–4 echo ghosts. Camera-travel carve-out (whip sweep). | MOVE 0.25–0.6 s `expo/power4/power3.out`; ENTER_FROM 40–120% of size; PEAK_BLUR 8–30 (18; wrapper 18–20, whip ≤24); SCALE_FROM 1.3–2.5; ghosts 2–4, step 12–40 px, opacity 0.3–0.6; dwell ≥1 s; entrances only. Registry `motion-blur` component: `shutterAngle` 720, `samplesPerFrame` 16 (8 halves cost); blur 1–3 beats per video. | hook slam, whip between stations | H | Fine. | H mid-streak (marks vanish first). Acceptable because it lands sharp; ensure blur reaches 0 and is cleared. |
| ★ **particle-burst** | Ballistic deterministic particles: confetti pop, dot burst behind a word, glyph dissolve. | count 10–18 (pop/dots), 24–40 (dissolve), cap ~40; G 900–1600 (confetti) / 0–200 (dots, dissolve); speed 250–700; cone 0.35–0.8 rad; flight 0.7–1.4 s (dots 0.4–0.7); size 5–14 / 4–8 px; fade 0.2–0.35; fire on a cause; behind the word. | number-landing punctuation, payoff; *(own)* glyph dissolve = impermanence ("vô thường") | M–H | Fine. | L (the dissolve uses particles colored like the text) |
| ★ **nudge-curve** | A slow-fast-slow group slide: `power3.in` ramp → linear burst → `power4.out` tail. | distance 10/65/25%, time ~20/18/62%; tail ≥3× ramp in time; reference 270 px in 0.57 s; reveal new content during the burst. | make room (block slides up for the answer), list grows | M | Vertical nudge suits portrait. | L |

### 1h. Effect recipes (2)

| Rule | Effect | Key params | Purpose | Energy | 9:16 | VN |
|---|---|---|---|---|---|---|
| ● **gsap-effects** | (a) TextPlugin typewriter: basic, blink, backspace, word rotation, appending words. (b) Audio visualizer from pre-extracted bands. | typing CPS 3–5 dramatic / 8–12 natural / 15–20 fast / 30+ fill; one cursor visible; idle blink; no flex `gap`. Audio: sync-load JSON, bass → big moves, treble → detail, RMS → globals; 2–3 properties; never equalizer bars (techniques #11: text ≤5% scale, ≤30% glow). | typed hook; *(own)* RMS of the VO drives a faint bg glow | M | Fine. | H for char-level TextPlugin. Use the "appending words" mode (word granularity). |
| ★ **css-marker-patterns** | Five hand-drawn accents: highlight (`scaleX`), circle (ellipse), burst (12 lines), scribble (SVG underline draw), sketchout (two crossed lines). | highlight 0.5 s `power2.out` (multi-line stagger 0.3); circle 0.6 s `back.out(1.7)`, rot −3°, width 130% (150% short words) (override to `power3`); burst 12 lines × 30°, len 40–80 varied, 0.4 s stagger 0.03; scribble 0.8 s `power1.inOut`, wave ~25–50 px per half-wave; sketchout 0.3 s + 0.15 s; cycle modes every 2–3 groups (high), 3–4 (medium), 4–5 (low). | emphasis on a spoken word, compare (sketchout wrong), check item, quote underline | M | Fine. | M: the circle must enclose the marks (height ≥140% for capitals with marks). Scribble/underline sits below the dot-below zone (+0.15 em). |

### 1i. Non-rule technique vocabulary (techniques.md, animate-text)

These have no rule file but are first-class building blocks.

| Technique | Notes for shorts |
|---|---|
| Per-word kinetic typography | VO-synced onsets with a decaying slide of 80→12 px, `power2.out` 0.35 s. Prefer `power3/4` per doctrine. [KT] T3. |
| Clip-path reveal masks | Static window, moving content; `circle()` iris; `polygon()` shapes. VN needs negative insets ([KT] §3.3). |
| CSS 3D transforms | `perspective` on the parent, `preserve-3d` on the moving element. Card flip, calendar page, coin. |
| Canvas 2D procedural | A hash-seeded field drawn from a GSAP proxy. Ambient backgrounds (stars, incense smoke, grain). |
| WebGL fragment shader art | Domain-warped FBM backgrounds with a Canvas fallback. ≤1 beat per video ([3D] §5 perf). |
| Lottie | `autoplay:false` plus `window.__hfLottie.push`. Characters and gestures (story devices). |
| Video compositing | Muted `<video>`, framework-seeked. Footage b-roll. |
| Variable font axes | Tween `font-variation-settings` (opsz, wght). *(own)* A weight morph 300→900 on one VN word is a quiet emphasis device, if the font is variable *and* covers VN. |
| MotionPath | A dot or icon along an SVG path: route travel on maps, a lotus petal falling. |
| Velocity-matched transitions | Exit y −150, blur 30, 0.33 s `power2.in`; entry 1.0 s `power2.out`. The same idea as cut-the-curve. |
| Audio-reactive | Per-frame `tl.call` from extracted bands. Text ≤5% scale, ≤30% glow; backgrounds 10–30%. |
| animate-text, 24 IDs | per-char: soft-blur-in, per-character-rise, typewriter, bottom-up-letters, top-down-letters, stagger-from-center, stagger-from-edges. per-word: per-word-crossfade, spring-scale-in, shared-axis-y, blur-out-up, kinetic-center-build, short-slide-right, short-slide-down, depth-parallax-words. per-line: mask-reveal-up, line-by-line-slide. whole: micro-scale-fade, shimmer-sweep, fade-through, shared-axis-z, scale-down-fade, focus-blur-resolve, shared-axis-x. **For VN, use only per-word, per-line and whole-element IDs**; per-char only for digits. |

---

## 2. Blueprint inventory: all 22

Blueprints are product-launch shot templates mined from 178 golden clips. For a narrated short, one blueprint usually spans **one to three VO lines**, not a whole video. The "portrait adaptation" column says how to re-aim each one for 9:16 and non-product topics. *(own)* marks my adaptation ideas.

| Blueprint | Scene it builds | Beat purpose (our shorts) | Duration (doc) | Portrait / topic adaptation | Fit |
|---|---|---|---|---|---|
| **kinetic-type-beats** | A flat centered bold-type shot where the words changing is the motion. Sub-shape A: fixed line with token swaps by hard cut. Sub-shape B: multi-beat statement build, each beat with its own move, landing a spring-pop payoff. 60+ named variant moves (scale-pop relay, letter-tumble, karaoke sweep, corner arrows converging, bg-invert flip, outline-echo stack, word-run with per-hero-word gags). | hook, emotional statement, list-as-relay, close | 3.0–12.9 s (staccato ~0.4 s/beat; relay ≥1.5 s/beat) | The workhorse. Portrait: phrases of 1–3 words stacked. Use relay holds ≥1.5 s for Vietnamese reading speed; the staccato (8–12 phrases in 4 s) is too fast for VN TTS. | ★ |
| **typewriter-reveal** | A caret types and edits a line, then collapses it to a point and springs a payoff; or a persistent mark with a typed CTA rail. | hook (relatable typed question), close (CTA rail under the channel mark) | 3.6–7 s | The ticker-push sub-variant (assembly slides left to keep the caret centered) solves the narrow width. *(own)* Frame 0 must show text, so open with the full line typed, then do a backspace-retype edit. | ★ |
| **spatial-pan-stations** | Pre-placed stations on one oversized canvas, visited by repeated camera pans with callouts; holds on the last. Variants: milestone timeline, diagonal pain web ending in a scribble knot, decode-then-pan. | time/history, process steps, list of places | 7–10 s | *(own)* Portrait: a **vertical** strip (pan down) reads like scrolling. Horizontal panning still works with one station per frame. Each station ≈1 s. | ★ |
| **camera-journey** | The camera is the storyteller: dive → hinge beat → travel to the consequence → landing. Sub-shape A: action round trip (cause → effect). Sub-shape B: cursorless 3D flight. | process cause→effect, finance mechanism, story world | 5.6–11.1 s | Vary the leg verbs; `power4.out` dives, `power2.inOut` repositioning. *(own)* Heavy: at most one per video, mid-body. | ● |
| **zoom-out-workspace-reveal** | Open tight on a full-bleed detail with micro-action, then ONE decelerating zoom-out reveals the containing whole. No zoom-in anywhere; locked after. | hook mystery (statue's hand → whole statue → temple; coin → banknote → market), payoff "scale" | 6.8–11 s | Superb hook because frame 0 is a full subject. Raster limits S0 to ~2–3× for photos; use vector/DOM detail for 4–12×. | ★ |
| **constellation-hub** | Nodes spring into a ring around a center, then resolve: push-in with DoF onto the core, orbit finisher, orbit-collapse into CTA, or scatter-drift end card. | process hub, "everything connects to X", close | 5–8 s (end card ~2.5 s) | Ring RX ≈ 380. **Circle budget.** The scatter-drift end card (icons around a serif headline drifting outward) is a good non-circle close. | ● |
| **grid-card-assemble** | N items cascade into a grid or list and hold; optional zoom-out. Variants: vertical benefit list (build/snap/stream), live-populate board, logo wall, item-field → payoff card. | list, breadth ("12 con giáp", "7 thói quen"), evidence wall | 3.0–10.5 s (lists ~1 item/s) | The **vertical list** and **stream-past-focal-slot → stop on chosen item** variants are the most portrait-native shapes in the whole library. The year table goes here. | ★ |
| **logo-assemble-lockup** | A brand mark comes to exist (parts assemble, stroke draw, morph chain, text-clear bloom, parts-arrive with confetti) and resolves into a lockup. | close (channel lockup), *(own)* symbol build (lotus, taiji, Dharma wheel assembling from parts) | 4.4–11 s | *(own)* The re-aim is the strongest use: "**symbol assemble**" builds a religious or scientific symbol from its parts while the VO explains each part (stroke-draw per part on its cue). | ● |
| **cursor-ui-demo** | A custom cursor drives an app UI; the camera chases each interaction. | (rare) finance app demo, how-to on a phone | 4.0–12.9 s | Use a phone-frame mock and finger taps instead of a cursor. Mostly off-brand for BUD/FS. | ○ |
| **device-surface-showcase** | A device mockup held as hero while screens cycle; camera static to continuous 3D push. | (rare) "check this on your phone", calendar app, banking app | 5–11.3 s | A phone held in portrait fills the frame naturally. | ○ |
| **prompt-type-submit-generate** | A query types into a real input, the machine works, the answer arrives (streaming, card, chart). | hook for search-demand topics ("Năm 2027 là năm con gì?") → answer card | 5.2–12 s | *(own)* A search-pill hook directly mirrors how viewers search. The answer arrives via `anchored-layout-expand`. Frame 0 shows the typed query in full. | ● |
| **agent-progress-theater** | Trigger → working state (spinners, status swaps, shimmer) → receipt card whose rows check off. | list as checklist ("3 việc nên làm"), "đang tính…" suspense before a number | 4.2–11.6 s | *(own)* Use only the receipt half: rows cascade and check off (badge flip, strike-through) on VO cues. Skip the AI loader theater. | ● |
| **panel-edit-live-sync** | An inspector panel bound to a target; a control scrubs and the target updates in the same beat. Camera locked, one continuous move, or punch-and-return. | process/what-if (finance, science) | 5.3–11.9 s | Control below, target above. 2–4 edit beats map to 2–4 VO clauses. | ● |
| **transcript-scroll-artifact-reveal** | Travel down one long content surface as evidence, then ONE focal interaction (quote highlight) pivots into a detail reveal. ≤2 camera moves. | evidence, quote from a document (sutta, decree, report) | 5–11.8 s | Native vertical scroll. Highlight sweep plus push-in onto the cited line. | ★ |
| **dataviz-countup** | Numbers and charts are the hero: count-up ring → trend chart → stat grid via push-through; hook counter burst; scrub montage; gauge beat. | reveal-number, evidence, hook stat | ~4–12 s | The hook counter-burst (icons clustered → number explodes as icons fling out) and the gauge beat are the short-friendly members. | ★ |
| **titlecard-reveal** | A calm breather: one restrained move then a still hold; card chain with hard cuts or blur-snap handoffs. | held stillness beat before the payoff, close | 3–5 s (chains 5.5–9.5 s) | The deliberate stillness beat every video needs ([VC]). | ★ |
| **comparison-split** | A title slides down, two cards enter from opposite wings with mirrored `rotateY`, inner-edge badges pop (the lone overshoot), counter-phase float, two side glows. | compare | 4–6 s | *(own)* Rotate to a top/bottom stack with mirrored `rotateX`, badges at the inner (middle) edges, and glows at 30%/70% height. | ★ |
| **overwhelm-surround** | Accumulation; the center subject morphs into the viewer's avatar; elements close in from all sides. Or clutter-shove to a question. | emotional (stress, debt, "nghiệp chồng chất"), problem framing | 6–9 s (~10 s) | *(own)* The "clutter-shove-to-question" variant fits a hook: bills/notifications pile up, a push shoves them out, a question builds in the cleared center. | ● |
| **ticker-takeover** | A typed lead-in plus a slot word cycling 2–3 options, then a hero crashes in and shoves the text aside. | hook ("Không phải A, không phải B… mà là C"), payoff | 5–7 s | Vertical collision variant (hero drops from the top). | ● |
| **fixed-anchor-cycle** | A pinned anchor while the adjacent region cycles (hard-cut chips, per-word highlight walk, carousel, accelerating flurry) or the whole theme morphs; resolves into a lockup. | hook roll-call (signs/years), list, close | 6.6–11.1 s (engine 3–5 s) | Anchor at the top third, cycling slot below. Lockup gets 20–30% of runtime. | ★ |
| **video-text-pivot** | Video holds, slides aside to hand weight to a 3D-depth stat, then kinetic text types into the center, sealed by a gradient pill. | evidence → number → takeaway | 6–8 s | *(own)* Portrait: the footage slides *up* and shrinks to a top band; the stat fills the middle; a gradient pill seals the takeaway. | ● |
| **cta-morph-press** | A brand mark condenses into a CTA at the same center; a cursor clicks with press feedback. Hook variant: a widget morphs in place, performs, vanishes to a typed title. | close CTA | 4–6 s (Hook 5–7.5 s) | Finger tap; keep it subtle (CTA presses read salesy). | ○ |

---

## 3. Transition catalog

There are two layers. HyperFrames keeps them separate:

- **A. Between-frame transitions**, between scene clips. In faceless/PLV pipelines a harness injects them from the registry. In our single-composition short engine we author them ourselves.
- **B. Within-frame seams**, built by the device inside its own scene (cut-catalog).

### 3A. Between-frame transitions: every documented transition

**Registry Tier-B set**: transform/opacity/filter only, safe to auto-inject. *(own)* Portrait travel distances: push `x ±1080`, `y ±1920`.

| Name | Duration | Ease | Energy | Mechanics (doc) |
|---|---|---|---|---|
| crossfade | 0.5 s | `power2.inOut` | any | opacity swap |
| blur-crossfade | 0.6 s (registry); 0.5 s medium | `power2.inOut` | calm (**`default_calm`**) | old → blur 10 px, scale 1.03, fade; new from blur 10 px, scale 0.97 (+0.1 s). Calm: 25 px with a hold at abstract color. Default when backgrounds differ. |
| push-slide L/R/U/D | 0.5 s | `power3.inOut` | medium | both scenes travel the full frame |
| zoom-through | 0.4 s | `power3.in` / `power3.out` | high (**`default_high_energy`**) | old scale 2.5 + blur 8 + fade; new from 0.5 + blur 8 (+0.15 s) |
| squeeze | 0.4 s | `power3.inOut` | medium | old `scaleX`→0 at the left edge; new expands from the right (+0.1 s) |

`max_duration_s` = 2.0. Tier-A `shared-element` morph (narrative `intent: morph`) is exempt from the type budget.

**Full CSS catalog** (`css-*.md`). Durations and eases are as documented.

| Family | Transition | Duration / ease | Energy / mood | Notes |
|---|---|---|---|---|
| Dissolve | Crossfade | 0.5 s `power2.inOut` | any | baseline |
| | Blur crossfade | medium 10 px / 0.5 s; calm 25 px, 0.6 + 0.6 s `power1`, hold | calm, premium, warm | BUD primary |
| | Focus pull | medium 15 px 0.5 s `power1.in`, swap at +0.25; calm 30 px 0.8 s, hold, 20 px incoming | calm, premium | |
| | Color dip | 0.2 s out `power2.in` + 0.2 s in at +0.25 | dramatic, premium, outro | dip to black or brand color |
| Blur | Blur through | calm 30 px: 0.5 s `power1.in` + 0.7 s `power1.out`; medium 15 px 0.4 s | calm (heavy) | "content becomes abstract" |
| | Directional blur | medium 12 px, skew 8°, x 200, 0.4 s `power3`; calm 20 px, skew 4°, x 100, 0.6 s `power1` | medium | |
| Push | Push slide | 0.5 s `power3.inOut` | medium, editorial | |
| | Vertical push | 0.5 s `power3.inOut` | medium, editorial | **FS primary (UP)**: read order in 9:16 |
| | Elastic push | 0.4 s `power4.out` + overshoot 30/−15 px | playful | violates doctrine except in a playful register |
| | Squeeze | 0.4 s `power3.inOut` | medium, cold/clinical | |
| Scale | Zoom through | 0.4 s `power3.in/out` | high, dramatic | |
| | Zoom out | 0.4 s `power3.in`, old → scale 0.3, z-index | dramatic, clinical | |
| 3D | 3D card flip | 0.6 s `power2.inOut`, `perspective 1200` | playful | *(own)* calendar or coin flip |
| Radial | Circle iris | 0.5 s `power2.out`, `circle(0→75%)` | calm accent, playful | **circle budget** |
| | Diamond iris | 0.5 s `power2.out` | playful | |
| | Diagonal split | 0.5 s `power3.inOut` | editorial | outgoing on top |
| Mechanical | Shutter | 0.25 s `power3.in` + 0.25 s `power3.out` | clinical, editorial | portrait halves are 960 px tall |
| | Clock wipe | 4 × 0.1 s `none`, 9-point polygon | playful, retro | *(own)* a "time passes" accent |
| Cover | Staggered blocks | 2 blocks: 0.25 s `power3.inOut`, stagger 0.06 (5 blocks: 0.04) | medium, tech, topic change | full-frame blocks in palette colors |
| | Horizontal/vertical blinds | 0.2 s per strip; 6 strips @0.03 / 12 @0.018 | clinical, tech | count by energy: calm 4h/6v, medium 6–8h/8v, high 12–16h/16v |
| Grid | Grid dissolve | 12 cells / 120 cells (opacity 0.75), ripple from center | tech/data | cycle 5 palette colors. Note the doc warning about visible geometric repetition. |
| Light | Light leak | ~0.5–0.9 s, `sine.inOut` washes, swap at +0.45 | warm, retro | overlays ≥2400 px, never a visible shape. **BUD accent** |
| | Overexposure burn | 0.55 s, `brightness` 1.5→3, swap at peak white | dramatic, high | |
| | Film burn | ~0.6 s, staggered amber/orange/red | warm, retro | |
| Distortion | Glitch | RGB overlays at 35% normal blend, large jitter | tense, tech | |
| | Chromatic aberration | ±80 px over 0.3 s `power2.in`, converge | tech, tense | |
| | Ripple | ±30 px, 0.04 s steps, blur rising | tense, playful | |
| | VHS tape | 20 cloned strips with seeded offsets, R/B copies at 35% | retro | |
| Other | Gravity drop | 0.5 s `power3.in`, y +1200 (*(own)* +2100 in portrait), rot 4° | dramatic | |
| | Morph circle | 0.5 s `power3.in`, circle scale 30 | playful | **circle budget** |
| Destruction | Page burn | noise fire front plus clip; the new scene fades from black at 90% over 0.8–1.2 s | most dramatic, once | *(own)* "burn the old belief" myth-bust, FS only |
| Shader | `@hyperframes/shader-transitions` | per package | — | Calm: cross-warp morph, thermal distortion. Medium: whip pan, cinematic zoom. High: ridged burn, glitch, chromatic split. Plus gravitational lens, SDF iris, domain warp, light leak, ripple waves, swirl vortex. **≤2 shader transitions per video** ([VC] §3.1). Shader-compatible CSS rules apply: no `transparent` in gradients, no `var()` on captured elements, explicit scene `background-color` = `bgColor`. |
| Don't use | star iris, tilt-shift, lens flare, hinge/door | — | — | broken in CSS |

The registry blocks/components (`torn-paper-rip`, `ink-bleed-reveal`, `paper-collage-reveal`, `halftone-dissolve`, `whip-pan-cut`, `text-match-cut`, `line-swap`, `hw-scribble-transition`, `organic-light-leak-overlay`, `editorial-flash-overlay`, `curtain-reveal`) are covered in [VC] §3.2.

### 3B. Within-frame seams (cut-catalog), the device-internal vocabulary

| Seam | Mechanics | Use when |
|---|---|---|
| Zoom-through (forward) | Exit: scale 1→1.2 and blur 0→10 px (text) or 18–20 px (full-frame), `power3.in`, 0.2 s; opacity 1→0.15 linear as a separate tween. Hard cut via `tl.set`. Incoming 0.15 / 0.75 / blur 10 → 1, `expo.out` 0.5 s. Never both texts visible. | state change (hook → context, new chapter) |
| Inverse zoom-through | Exit 1→0.8; incoming from 1.25 + blur 10 → 1, `expo.out` 0.5 s. | arrival / payoff |
| Cut-the-curve | x or y 0→−230, `power4.in` 0.2–0.4 s, fade done at 25–30% of travel; entry +230→0 `power4.out`, same distance and duration (~3,070 px/s at the cut). Partial travel only. | unfinished phrase across visuals (the default scene seam) |
| Waterfall cut | Per word x 0→−230 over 0.34 s `power4.in`, fade 0.18 s, stagger ~0.022; entry +230→0 with opacity 0.35→1 over 0.3 s `power4.out`, shrinking gaps (0.05 × 0.84ⁿ). | text-to-text line change, same thought |
| Hard cut | `tl.set` swap at full opacity | "wake up" / disruption; title-card chains |
| Tumble-swap | `depth-scatter-assemble`: one shared progress drives both glyph sets, 0.5–1.0 s | playful phrase change (FS, science) |
| Whip sweep | `nudge-curve` burst-dominant plus `motion-blur-streak` carve-out; swap content during the burst | station-to-station inside a world |

### 3C. Rules for choosing primary vs accent (consolidated)

1. **Type budget.**
   - Pick ONE primary for 60–70% of scene changes, plus 1–2 accents.
   - "Pick 2-3 transition types for the whole video and repeat them."
   - "Never use a different transition for every scene."
   - The shared-element morph and within-frame seams do not count toward the budget.
2. **Primary by energy.**
   - Calm: blur crossfade or focus pull, 0.5–0.8 s, `sine.inOut`/`power1`.
   - Medium: push slide or staggered blocks, 0.3–0.5 s, `power2`/`power3`.
   - High: zoom through or overexposure, 0.15–0.3 s, `power4`/`expo`.
3. **Mood decides the family.** See the mood table in `overview.md`: warm → light leak or blur; editorial → push or shutter; tech → grid, blocks or glitch; premium → focus pull, blur or dip; retro → film burn or VHS.
4. **Narrative position.**

   | Position | Choice | Duration |
   |---|---|---|
   | Opening | the most distinctive transition | 0.4–0.6 s |
   | Related points | the primary | ~0.3 s |
   | Topic change | something different (blocks, shutter, squeeze) | — |
   | Climax | the boldest accent | — |
   | Wind-down | blur crossfade | 0.5–0.7 s |
   | Outro | crossfade or dip to black | 0.6–1.0 s |

5. **Blur by energy.** Calm 20–30 px over 0.8–1.2 s with a 0.3–0.5 s hold. Medium 8–15 px over 0.4–0.6 s. High 3–6 px over 0.2–0.3 s. Text seams are capped at 10 px.
6. **Presets.**

   | Preset | Duration | Ease |
   |---|---|---|
   | snappy | 0.2 s | `power4.inOut` |
   | smooth | 0.4 s | `power2.inOut` |
   | gentle | 0.6 s | `sine.inOut` |
   | dramatic | 0.5 s | `power3.in→out` |
   | instant | 0.15 s | `expo.inOut` |
   | luxe | 0.7 s | `power1.inOut` |

7. **Defaults when unspecified.** `blur-crossfade`. Use `zoom-through` when the incoming beat is high-energy.
8. **Hard rules.**
   - Outgoing and incoming animate at the same T.
   - No exit animations before a transition.
   - Only the final scene may fade out.
   - Overlays must be full-frame.
9. **Seam choice inside a device** (cut-catalog), by relation to the previous line:

   | Relation | Seam |
   |---|---|
   | continues the thought | cut-the-curve / waterfall |
   | new state | zoom-through |
   | payoff | inverse zoom |
   | disruption | hard cut |

*(own)* **Suggested per-channel profiles.** Each profile is a primary plus two accents.

| Channel | Primary | Accents |
|---|---|---|
| BUD | blur-crossfade 0.6 s | light-leak at the emotional turn; color-dip outro |
| FS | vertical push UP 0.4 s | zoom-through at hook → context; `torn-paper-rip` (or 3D page flip) at the payoff |
| History | focus pull (medium) | film burn for an era change; diagonal split for then/now |
| Science | cut-the-curve / zoom-through | grid dissolve for "zoom to micro"; shader cinematic zoom once |
| Finance | push slide LEFT | staggered blocks (palette) at topic change; overexposure at the reveal |

---

## 4. Device taxonomy: 40 reusable scene devices

A **device** is one narrated beat (usually one VO line, 2.5–6 s). It owns:

- its framing,
- its entrance on the line's first words,
- its development on later VO cues,
- its exit seam into the next device.

Every device takes `{line_start, line_end, words:[{w,t}], purpose, rel_prev}` from the planner, plus the JSON fields listed. The "Composes" column cites rules (`r:`) and blueprints (`bp:`). The "Existing kind" column maps a device onto the repo's longform kinds (motion-library) where it can extend one.

Common fields on every device *(own)*:

```json
{"device": "num_countup_ring", "at": [12.4, 17.9], "cue": {"<field>": "<spoken word that triggers it>"},
 "theme": "bud|fs|hist|sci|fin", "energy": "C|M|H", "seam_in": "auto|cut-curve|zoom|inv-zoom|hard",
 "bg": "solid|radial|paper|photo-dim|shader|canvas", "accent": "#hex"}
```

Timing never hard-codes seconds inside the device. Every reveal is keyed to `cue` words resolved against `hf_align` word times, following doctrine rule 2.

### HOOK devices: the first 0–3 s. Frame 0 must already show a full subject (see the frame-0 note in memory/[KT]).

| # | Device | What the viewer sees | Composes | Data inputs | Energy · theme |
|---|---|---|---|---|---|
| H1 | `hook_slam` | 2–3 word groups slam in on their VO onsets, each on a different axis (Z-slam with blur → X side-snap → Y rise); the climax word gets a circle or underline marker; forward zoom-through out. Group 1 is already landed at frame 0 (or by 0.15 s). | r: kinetic-beat-slam, motion-blur-streak (group 1 only), css-marker-patterns; bp: kinetic-type-beats B; seam zoom-through | `groups:[{text, cue}]`, `climax_word`, `marker: circle\|underline\|highlight` | H · all, BUD in calm variant (no blur, `power3`) |
| H2 | `hook_search_query` | A search pill with the query already fully typed at frame 0; the caret backspaces one word and retypes the sharper word; press; an answer card grows down from the pill. | r: discrete-text-sequence, context-sensitive-cursor, camera-cursor-tracking, press-release-spring, anchored-layout-expand; bp: prompt-type-submit-generate A, typewriter-reveal | `query`, `edit:{remove, insert, cue}`, `answer_preview`, `submit_cue` | M · FS search-demand topics, finance, science "what is…" |
| H3 | `hook_counter_burst` | 3–5 icons clustered at center (visible at frame 0); the hero number counts and scales up as the icons fling outward (chord); dot burst at landing; label snaps in. | r: counting-dynamic-scale, center-outward-expansion (synced chord), particle-burst (dots), ambient-glow-bloom; bp: dataviz-countup Hook | `value`, `from`, `suffix`, `label`, `icons[3–5]` | H · fin, sci, hist, BUD ("84.000 pháp môn") |
| H4 | `hook_roll_call` | Pinned anchor ("Tuổi … năm 2027") over a slot that cycles tokens in an accelerating flurry (hard cuts), braking on the target; optional hero crash-in that shoves the line aside. | r: discrete-text-sequence, dynamic-content-sequencing (accelerating cadence), vertical-spring-ticker, reactive-displacement (crash variant); bp: fixed-anchor-cycle A, ticker-takeover | `anchor`, `tokens[]`, `target`, `cadence: steady\|flurry`, `resolve: brake\|crash` | M–H · FS (signs/years), fin (tickers), hist (dates) |
| H5 | `hook_macro_reveal` | Extreme close-up of a detail at frame 0 (mudra, coin inscription, a single calendar cell, a cell under a microscope); micro-action; ONE decelerating zoom-out reveals the whole; the frame locks; a label lands. | r: viewport-change (extreme outward), svg-path-draw (callout), spring-pop; bp: zoom-out-workspace-reveal | `asset` (svg/DOM or hi-res image), `focus:{x,y}`, `S0` (≤3 for raster), `reveal_cue`, `label` | C–M · BUD iconography, hist artifacts, sci |
| H6 | `hook_myth_strike` | The common belief is set big; as the VO says "sai/không phải", a sketchout strike crosses it and it dims to 0.55; the truth arrives by inverse zoom-through (or crashes in from the top). Optional slice glitch on the strike (FS/sci/fin only). Also usable mid-body as a compare device. | r: css-marker-patterns (sketchout), reactive-displacement, chromatic-glitch (slice, optional); seam inverse zoom | `myth`, `truth`, `strike_cue`, `truth_cue`, `crash: bool` | H · all (BUD: calm, no glitch) |

### NUMBER devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| N1 | `num_countup_ring` | A count-up with dynamic scale; a ring (progress / lotus outline / taiji / plain arc) draws on the same ease; the suffix slides in after; dot burst; glow blooms behind. | r: counting-dynamic-scale, stat-bars-and-fills (ring), svg-path-draw, particle-burst, ambient-glow-bloom | `value, from, suffix, label, ring: progress\|lotus\|taiji\|arc\|none, pct?` | M · all | extends `stat` |
| N2 | `num_odometer` | A 4-digit year or price rolls on per-digit spring tickers (or split-flap decode with the digit pool); the last digit gets the big step; an optional 60-tick cycle ring lights its twin. | r: vertical-spring-ticker (numeric), hacker-flip-3d (digits only), svg-icon-enrichment (clock hands variant) | `digits, mode: odometer\|flap, label, twin_year?` | M–H · FS years, hist dates, fin prices | new |
| N3 | `num_bars` | 4–6 bars grow (`scaleY`, stagger 0.06–0.1); the accent bar's value counts on the same ease; the other bars dim (DoF dim). | r: stat-bars-and-fills, counting-dynamic-scale, depth-of-field-blur | `bars:[{label,value}], accent, unit, title` | M · fin, sci, hist | new |
| N4 | `num_chart_scrub` | A line chart draws left→right, breaks above a band; a playhead scrubs to the peak; the tooltip steps values; the peak dot and a pill pop; it lands on a count lockup. | r: svg-path-draw, chart-scrub-readout, spring-pop-entrance, counting-dynamic-scale; bp: dataviz-countup scrub | `series:[{d,v}], unit, peak_index, label, band?` | M · fin, sci, hist | new |
| N5 | `num_unit_grid` | "1 trong 10": a grid of N icons populates; a subset lights in the accent while the others dim; a fraction label counts. | r: spring-pop-entrance (group, ≤0.5 s), depth-of-field-blur (dim), counting-dynamic-scale; bp: grid-card-assemble live-populate | `total (≤40), highlight, icon, label` | M · sci, fin, health | new |

### COMPARE devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| C1 | `cmp_stack_split` | A title drops in; two cards enter from top and bottom with mirrored `rotateX` tilts; side glows (top warm / bottom cool); inner-edge badges pop (the video's single overshoot); counter-phase jitter. | r: split-tilt-cards (rotated to vertical), spring-pop-entrance, ambient-glow-bloom, sine-wave-loop; bp: comparison-split | `title, top:{eyebrow,title,body,badge,tone,cue}, bottom:{…}` | M · all | extends `compare` |
| C2 | `cmp_balance` | An SVG balance beam; each pan's value counts; the beam angle is bound to the value difference in the same beat (control-target couple); it settles critically damped. | r: control-target-sync, counting-dynamic-scale, svg-path-draw, springEase ζ1 | `left:{label,value,icon}, right:{…}, unit` | M · fin, BUD (merit), sci | new |
| C3 | `cmp_theme_morph` | One pinned anchor (a word, an object silhouette, a price) while the whole surrounding skin crossfades through 3–5 eras, regions or currencies (~0.3 s each), braking on the last. | r: theme-crossfade-morph; bp: fixed-anchor-cycle B | `anchor, skins:[{label, bg, accent, caption, cue}]` | M · hist (then/now), fin, FS (4 seasons) | new |
| C4 | `cmp_rack_focus` | Two layered planes (A behind B); the VO names A, then the rack shifts focus to B while A blurs and dims; optional camera push on B. | r: depth-of-field-blur (rack), multi-phase-camera (punch), coordinate-target-zoom | `a:{text|img}, b:{…}, rack_cue` | C–M · BUD (two views), hist | new |

### LIST devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| L1 | `list_slot_ticker` | An anchor label is pinned; the masked slot steps once per spoken item; a pause, then a big final step (the climax bounce); optional circle on the final item. | r: vertical-spring-ticker, css-marker-patterns; bp: fixed-anchor-cycle A | `anchor, items[2–5]` (with cues), `final_marker` | M–H · FS, fin, hist | new |
| L2 | `list_accumulate` | A vertical list builds one row per VO cue: a marker pops, a check draws, the text mask-wipes; earlier rows dim by position; the block nudges up to make room. | r: spring-pop-entrance, svg-path-draw (check), anchored-layout-expand, nudge-curve, depth-of-field-blur (dim); bp: grid-card-assemble (vertical list BUILD/SNAP), agent-progress-theater (receipt) | `title, items:[{text, cue, icon?}], mode: build\|snap\|check` | M · all | extends `list` |
| L3 | `list_burst_spotlight` | 3–8 chips burst from the center to a 2-column grid; the VO picks one, which is spotlit (others blur/dim) and gets a highlight. | r: center-outward-expansion, depth-of-field-blur, css-marker-patterns highlight | `items:[{label, icon}], focus_index, focus_cue` | M–H · all | new |
| L4 | `list_year_table` | A year table (groups × years): rows cascade (waterfall), or the table streams past a focal slot and decelerates onto the viewer's row; that row gets a highlight swipe while the others dim; it holds long (screenshot/rewatch value). | r: waterfall-entry, vertical-spring-ticker (continuous stream), css-marker-patterns, depth-of-field-blur; bp: grid-card-assemble stream / item-field → payoff | `groups:[{title, years[], tone}], highlight_year?, mode: cascade\|stream` | M · FS (the winning format per review brief) | extends `years` |
| L5 | `list_relay` | A slow statement relay: each item fills the frame alone, built by its own engine (typed / mask rise / slam), held ≥1.5 s, then hard-cut. For 3–4 heavyweight points. | r: kinetic-beat-slam, discrete-text-sequence, waterfall-entry; bp: kinetic-type-beats (flat-void statement relay) | `items:[{text, engine?, cue}]` | M · all | extends `word` |

### PROCESS / CYCLE devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| P1 | `proc_cycle_draw` | Nodes on a pentagon or ring; one arrow draws per spoken clause and its target node pops on landing; the counter-cycle (khắc) draws as a dashed inner star at the twist. | r: svg-path-draw, spring-pop-entrance (wrapper), svg-icon-enrichment; [3D] D2 | `nodes:[{id,label,color}], edges:[{from,to,kind,cue}]` | M · FS ngũ hành, sci cycles (water, carbon), fin (business cycle) | extends `elements` |
| P2 | `proc_flow_steps` | A vertical flow of step chips joined by drawing arrows; the camera pans down one station per step (vertical spatial pan); each station holds ~1 s. | r: viewport-change (pan), svg-path-draw, spring-pop-entrance, nudge-curve; bp: spatial-pan-stations | `steps:[{label, icon, cue}]` | M · how-to, sci, fin, BUD (practice steps) | new |
| P3 | `proc_slider_whatif` | A control (slider, dial or year stepper) scrubs 2–4 times; the bound target (curve, jar of coins, plant height, balance) answers in the same beat; it lands on the final edit. | r: control-target-sync, counting-dynamic-scale, stat-bars-and-fills; bp: panel-edit-live-sync | `control:{label, unit, values:[{v, cue}]}, target:{kind, map}` | M · fin, sci | new |
| P4 | `proc_hub_spokes` | A central concept with satellites springing onto an ellipse and connectors drawing outward; at the insight, a push-in with DoF collapses onto the hub (or a scatter-drift variant with no ring). | r: avatar-cloud-network, spring-pop-entrance, svg-path-draw, depth-of-field-blur, multi-phase-camera; bp: constellation-hub | `hub, spokes:[{label, icon, cue}], resolve: push\|scatter` | M · all. **Circle budget.** | new |
| P5 | `proc_wheel_lock` | A tilted wheel (zodiac 12 / compass 24 / bát quái 8) spins and decelerates to lock on the target sector; the sector lifts; tam hợp / xung lines draw. | r: svg-path-draw, viewport-change, springEase, CSS 3D; [3D] D1/D6/D7 | `kind: zodiac\|compass\|bagua, target, lines?:[{set, kind, cue}]` | M–H · FS. **Circle budget.** | extends `wheel` |
| P6 | `proc_symbol_assemble` | A symbol builds part by part as the VO names each part (lotus petals, Dharma-wheel spokes, taiji halves, atom orbits, a chart axis); each part stroke-draws and then fills; it ends in a lockup with a sheen. | r: svg-path-draw (draw-then-fill), depth-scatter-assemble (parts fly-in variant), ambient-glow-bloom; bp: logo-assemble-lockup (parts-assembly) | `svg_parts:[{id, label, cue}], lockup_label` | C–M · BUD, FS, sci | extends `illus` |

### PLACE / MAP devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| M1 | `map_pin_route` | A map pans to the region; pins drop (spring pop) with pulsing rings; a route draws between them with a travelling dot (MotionPath); labels slide out. | r: viewport-change, spring-pop-entrance, cursor-click-ripple (rings only), svg-path-draw, techniques MotionPath | `bbox, pins:[{name, lon, lat, cue}], route?` | M · hist, BUD (pilgrimage), fin (markets) | extends `map` |
| M2 | `map_zoom_nest` | Region → country → province → site: a chain of target zooms, each landing labelled. *(own)* This is the push-in inverse of H5, so never use both in one video. | r: coordinate-target-zoom (chain), depth-of-field-blur | `levels:[{bbox, label, cue}]` (≤3) | M–H · hist, BUD, sci (cosmic → micro) | new |
| M3 | `place_floorplan` | A top-down house plan (SVG); a compass or bát quái overlay rotates to the facing direction; zones highlight in turn (good/bad tone); furniture icons pop; one "mistake" zone gets a sketchout. | r: svg-path-draw, svg-icon-enrichment (needle), spring-pop-entrance, depth-of-field-blur (dim), css-marker-patterns | `plan: preset\|svg, facing, zones:[{zone, label, tone, cue}]` | M · FS (the "3 lỗi phong thủy nhà ở" winner), home/science | new |

### TIME / HISTORY devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| T1 | `time_spine` | A vertical spine draws down; year nodes pop; labels slide in from alternating sides; the camera keeps the active node at y ≈ 40%; an optional age counter steps. | r: svg-path-draw, spring-pop-entrance, viewport-change, chart-scrub-readout (playhead form); [3D] D10 | `items:[{yr, label, cue, now?}]` | M · hist, BUD (life of the Buddha) | extends `timeline` |
| T2 | `time_calendar_tear` | A tear-off calendar: pages flip (`rotateX`) with accelerating timing; the final page holds the solar date, lunar date and can chi; a red seal stamps (press state change) with a micro dot burst. | r: CSS 3D card flip, press-release-spring (stamp), particle-burst (≤12 dots), counting-dynamic-scale (date); [3D] D5 | `pages_n, final:{solar, lunar, canchi}, stamp_text, cue` | M–H · FS dates, hist anniversaries | new |
| T3 | `time_era_strip` | A horizontal strip of era stations panned leftward; a callout pops at each stop (triangle-tip origin); the secondary year label rises; it lands on "today". | r: viewport-change, multi-phase-camera, spring-pop-entrance (anchored origin), discrete-text-sequence; bp: spatial-pan-stations (Hook) | `stations:[{yr, label, cue}], present_label` | M · hist, sci (discoveries), fin (crises) | new |

### QUOTE / SCRIPTURE devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| Q1 | `quote_karaoke` | Serif quote lines on paper or a dark field. Mode `karaoke`: the glow walks the spoken words, and the key phrase gets a one-pass sheen or scribble underline. Mode `rise`: lines mask-rise on their cues. The source (e.g. "AN 3.100") slides in last in small caps. Dead-still hold ≥1 s. | r: asr-keyword-glow (karaoke), gradient-text-sweep (one-pass sheen), css-marker-patterns (scribble), ambient-glow-bloom; animate-text `mask-reveal-up` | `lines[], source, emphasis[], mode: karaoke\|rise` | C · BUD primary, hist quotes | extends `quote` |
| Q2 | `quote_document_scroll` | A tilted scan of a page or document scrolls to the cited passage; the spotlight dims the rest; a highlight sweeps the line; one push-in onto it. | r: 3d-page-scroll, depth-of-field-blur, css-marker-patterns (highlight), coordinate-target-zoom; bp: transcript-scroll-artifact-reveal | `file/page, scroll_to, highlight:{line|bbox}, cues` | C–M · BUD suttas, hist decrees, fin reports | extends `doc` |
| Q3 | `quote_ink_seal` | A short phrase blooms in through ink (registry `ink-bleed-reveal`, or a feathered mask reveal); a seal stamp presses beside it; light leak. Text stays DOM in a VN-safe serif or brush face. | r: press-release-spring (stamp), ambient-glow-bloom; registry ink-bleed-reveal | `text, seal_text, cue` | C · BUD, FS câu đối, hist | new |

### STORY / CHARACTER devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| S1 | `story_whiteboard` | Line-art sketches draw with a pen nib, stroke by stroke, then a watercolor fill; the board pans down per story beat; finished sketches get hw-boil. | r: svg-path-draw, viewport-change, techniques MotionPath (nib); [3D] D8 | `sketches:[{svg, cue}], board_bg` | C · BUD Jataka, hist anecdotes, sci thought experiments | extends `illus` |
| S2 | `story_parallax_tableau` | A 2.5D layered tableau (back / mid / front silhouettes) with one short camera move that gives parallax; one character gesture (an SVG joint rotation or Lottie); DoF on the front layer. | r: multi-phase-camera (one phase only), depth-of-field-blur, svg-icon-enrichment / adapters Lottie | `layers[], character:{svg|lottie, gesture, cue}, mood` | C–M · BUD stories, hist | new |
| S3 | `story_3d_scene` | A Three.js mini-world (moon over water, fire particles, a mountain path) driven by one proxy; at most 1 per video (render cost, [3D] §5). | adapters three; existing `_rv_bud_khi.html` pattern | `scene preset, beats:[{event, cue}]` | C · BUD, sci (planets) | new |

### EVIDENCE / PHOTO devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| E1 | `ev_photo_annotate` | A graded photo; a hand-drawn ellipse circles a grounded target, a connector draws to a label pill, a light wash covers the rest; optional target zoom (scale the whole scene, never under a fixed overlay). | r: css-marker-patterns (circle), svg-path-draw, coordinate-target-zoom, depth-of-field-blur; [3D] D11, [VC] P13 | `image, targets:[{x,y,rx,ry,label,cue}]` | M · BUD iconography, hist, sci | extends media `photo` |
| E2 | `ev_scrapbook` | Photos as taped polaroids drop in with small rotations (index sign), a caption stamp, a paper texture; up to 3 stack. | r: spring-pop-entrance (origin-anchored), press-release-spring (stamp); registry paper-collage; [VC] P14 | `photos:[{img, caption, cue}]` | M · hist, BUD, FS (old Tết) | new |
| E3 | `ev_text_window` | A giant word acts as a mask window onto a photo; the window scales down or the word opens up to reveal the full photo underneath. | techniques clip-path / CSS mask; r: viewport-change; [VC] P8 | `word, image, cue` | M–H · hist, BUD, sci | new |
| E4 | `ev_source_card` | A citation card (source name, date, snippet) slides up; a highlight sweep crosses the key clause; a "verified" seal presses. It builds trust before a claim. | r: anchored-layout-expand, css-marker-patterns, press-release-spring (state change) | `source, date, snippet, highlight, cue` | C–M · all (pairs with fact-check policy) | new |

### CLOSE / CTA devices

| # | Device | Viewer sees | Composes | Data inputs | Energy · theme | Existing kind |
|---|---|---|---|---|---|---|
| X1 | `close_question_rise` | The closing question mask-rises in mixed case; one-pass sheen on the question word; dead still ≥1.5 s; the last frame is composed to match frame 0 for loopability. | r: gradient-text-sweep (one-pass), sine-wave-loop (≤0.01 jitter only); animate-text `mask-reveal-up`; bp: titlecard-reveal | `question, sheen_word, loop_ref?` | C · all | extends `word` |
| X2 | `close_lockup_stamp` | Title-card chain: takeaway line → hard cut → channel lockup, with a seal stamp pressing (state change) and a soft glow; held still. | r: press-release-spring, ambient-glow-bloom; bp: titlecard-reveal (card chain), logo-assemble-lockup (text-clear bloom) | `takeaway, channel, cta?` | C–M · all | extends `endcard` |
| X3 | `close_word_to_cta` | The last spoken keyword morphs (card-morph-anchor) into a pill "Bình luận tuổi của bạn"; a finger tap presses it with a subtle ripple. ≤1 in 3 videos. | r: card-morph-anchor, physics-press-reaction, cursor-click-ripple; bp: cta-morph-press | `from_word, cta_label` | M · FS, fin | new |

**Count:** 6 H + 5 N + 4 C + 5 L + 6 P + 3 M + 3 T + 3 Q + 3 S + 4 E + 3 X = **45 devices**. The *core set* is 40; S3 `story_3d_scene`, M2, C4, X3 and N5 can wait for phase 2.

### Orthogonal treatments: modifiers that multiply variety without new devices

| Treatment | Applies to | Source | Budget |
|---|---|---|---|
| `hero_depth` (3D extruded word or number) | H1, N1, N2, X1 | r: 3d-text-depth-layers | ≤1 per video |
| `gold_fill` (gradient in glyphs plus hue settle) | any hero word | r: gradient-text-sweep | ≤1 per video |
| `glitch_accent` (slice or RGB on one word) | H1, H6 | r: chromatic-glitch | ≤1 per video; never BUD |
| `punctuation_particles` (dot burst or confetti) | number landings, payoff | r: particle-burst | ≤2 per video |
| `halo` (radial bloom behind the hero) | any held hero | r: ambient-glow-bloom | ≤3 per video; peak ≤0.30 |
| `streak_arrival` (motion blur on the entrance) | H1, N2, L1 | r: motion-blur-streak / registry `motion-blur` | 1–3 per video |
| `camera` | per device | multi-phase-camera / 3d-camera-flight | ≤2 camera-led devices per video; never adjacent |
| `bg` (`solid` / `radial` / `paper` / `photo-dim 30–50%` / `canvas-procedural` / `shader`) | per device | techniques #2/#13, [VC] | shader bg ≤1 per video; never a full-screen linear gradient (banding) |
| `jitter` (hold aliveness) | held finals | r: sine-wave-loop (low register) | only on holds >1.5 s; ≤√N amplitude rule |

---

## 5. The variety engine: deterministic auto-selection with brand guardrails

Goal: an agent (or `engine.js` / `hf_batch_render.py`) picks devices, eases, seams and transitions per line so that:

- no two consecutive shorts share a look;
- adjacent lines differ;
- every doc law and channel rule holds;
- a re-render of the same plan is byte-identical.

### 5.1 Inputs

- **Plan lines.** Each line has `text`, `words[{w,t}]`, an optional `hint` (device or kind), and optional `data` (numbers, years, places).
- **Channel profile** *(own)*:

  ```json
  {"channel":"fs","allow":["H1","H2","H4","H6","N1","N2","C1","C3","L1","L2","L4","P1","P5","M3","T2","Q3","E4","X1","X2","X3"],
   "deny_treatments":[],"transition":{"primary":"push-slide UP","accents":["zoom-through","torn-paper-rip"]},
   "ease_chars":["power3","expo","power2"],"palette":"fs_red_gold","overshoot_max":1,"glitch":true}
  ```

  BUD differs: `glitch:false`, `overshoot_max:0` (spring ζ ≥0.85 only), primary `blur-crossfade`, eases `["power3","sine","power2"]`, and the hook may not use H6's crash. Other channels are configured the same way.

- **Rotation memory per channel** (persisted, e.g. `output/cl_staging/<ch>/variety_ledger.json`):

  ```json
  {"videos":[{"id":"…","date":"2026-10-13","devices":["H5","Q1","P6","X1"],"hook":"H5","primary":"blur-crossfade",
   "bg_seq":["paper","radial","paper","solid"],"signature":"H5|blur-crossfade|paper|lotus"}],
   "device_uses":{"H5":{"last":3,"count30":4}}}
  ```

### 5.2 Step 1: classify each line's purpose (deterministic)

Run these in priority order *(own)*; Vietnamese cues are shown:

1. Line index 0 → `hook`. The last line → `close`. The line before the payoff → candidate `hold` (stillness).
2. Explicit `hint` wins.
3. A number with a unit or ≥2 digits that are not a year → `number`. Patterns like "%", "lần", "triệu", "nghìn", "84.000".
4. 4-digit years or "thế kỷ / năm … trước" → `time`. If ≥3 years → `list` (year-list).
5. "không phải … mà là", "khác với", "trước … nay", "A hay B" → `compare`. Phrases like "sai lầm / ngộ nhận" → `myth`.
6. Ordinals "thứ nhất / một là / 3 điều / các" or enumerations with ≥3 commas → `list`.
7. Causal or cyclic words ("sinh ra", "dẫn đến", "vòng", "chu kỳ", "nếu … thì") → `process`.
8. A place name from the gazetteer (hf_geo), "hướng / phía / nhà" (FS) → `place`.
9. Citation markers (sutta code, "Đức Phật dạy", "sách … viết", quotation marks) → `quote`.
10. Narrative past tense with a character ("có một …", "ngày xưa") → `story`.
11. A media hint or a photo-worthy proper noun → `evidence`.
12. Otherwise → `statement`, served by kinetic text devices H1-style, L5 or Q1-rise.

Also compute `rel_prev` ∈ {`continue`, `new_state`, `payoff`, `disrupt`}:

- `payoff` = the line after the hold or containing "vì vậy / hóa ra / thật ra";
- `disrupt` = "nhưng / tuy nhiên" at the start;
- `new_state` = a purpose change;
- otherwise `continue`.

### 5.3 Step 2: candidate devices per purpose

| Purpose | Candidates (in rough preference order) |
|---|---|
| hook | H5, H1, H3, H4, H2, H6 |
| number | N1, N2, N3, N4, N5, H3 (mid-video) |
| compare | C1, H6, C2, C3, C4 |
| list | L1, L2, L4, L3, L5 |
| process | P1, P2, P4, P3, P6, P5 |
| place | M1, M3, M2 |
| time | T1, T3, T2, N2 |
| quote | Q1, Q2, Q3 |
| story | S1, S2, S3 |
| evidence | E1, E4, E3, E2, Q2 |
| statement | L5 single, Q1-rise, H1-calm, E3 |
| hold | X1-style still card (titlecard-reveal), Q1 with no development |
| close | X1, X2, X3 |

Filter the candidates by the channel `allow` list and by data availability (no `series`, no N4).

### 5.4 Step 3: deterministic scoring

For each line *i* and each candidate *d*:

```
score(d) = base[d][purpose]                       # preference order: 1.0, 0.9, 0.8 …
         + energy_fit(d, curve[i])                # +0.3 if d.energy matches the target energy at i
         - 0.6 * recent_use(d)                    # Σ over the last K=6 videos of 0.5^age (from the ledger)
         - 0.4 * used_in_this_video(d)            # reuse within one video is discouraged (the same device max 2×)
         - INF if violates_hard_constraint(d, i)  # see 5.5
         + tiebreak(hash(video_id, i, d)) * 1e-3  # FNV/xmur3 hash, never Math.random
pick argmax(score)
```

**Target energy curve for 25–40 s** *(own; matches the doc rhythm laws)*:

| Section | Share of runtime | Energy |
|---|---|---|
| hook | 0–8% | H |
| context | 8–25% | M |
| body | 25–70% | alternate M / H / M |
| hold | 70–78% | C (stillness) |
| payoff | 78–90% | H |
| close | 90–100% | C |

The slowest beat's main move must be ≥3× the duration of the fastest. Name the pattern in the plan, e.g. `fast-fast-SLOW-fast-PAYOFF-hold`.

### 5.5 Hard adjacency constraints (line *i* vs *i−1*)

Each device declares `framing`, `axis`, `ease_char`, `bg`, `camera` and `circle` in a static registry *(own)*.

| Dimension | Values | Constraint |
|---|---|---|
| framing | `center-hero`, `stacked-split`, `edge-band`, `world-camera`, `grid/list`, `full-bleed-media`, `card-on-field` | ≠ previous. ≥3 distinct per video. |
| motion axis (entrance) | `Z-scale`, `Y-rise`, `X-side`, `3D-rot`, `in-glyph` (glow/gradient), `discrete` (cut/ticker), `mask`, `draw` (path), `camera` | ≠ previous. Never 3 consecutive text-only axes (`Y/X/Z` on plain type). |
| ease character | `power3`, `power4`, `expo`, `power2/sine` (calm), `linear-driver` (scrub/karaoke/draw), `spring ζ1` | ≠ previous main ease. ≥3 characters per video. ≤2 same-ease tweens per scene. |
| background | `solid`, `radial`, `paper`, `photo-dim`, `canvas`, `shader` | ≠ previous unless the seam is a cut-the-curve inside the same "world". |
| camera-led | yes / no | No two camera-led devices adjacent (H5, P2, P4-push, M1, M2, T1, T3, Q2, S1). |
| photo-focal | yes / no | ≤30% of lines. Never line 0 (data: photo hooks lose viewers ~2× faster, [VC]). |
| circle mechanic | yes / no | ≤1 per video (P4, P5, N1 ring, orbit, iris, morph-circle transition, circle marker counts as ½). |

### 5.6 Per-video budgets (from the docs, plus *(own)* caps for Shorts)

| Item | Budget | Source |
|---|---|---|
| Overshoot moments (`back.out`, ticker climax bounce, badge pop, suffix) | 1 (FS/fin/sci); 0 for BUD (use ζ 0.85 spring) | spring-pop-entrance, comparison-split ("the lone overshoot"), doctrine |
| Circle mechanics | 1 | [VC] §0, transitions overview (iris = accent) |
| Gradient-in-type (`gold_fill`, sheen) | 1 | [KT] §4 |
| 3D depth hero text | 1 | 3d-text-depth-layers (hero use) |
| Glitch | 1 (FS/sci/fin), 0 (BUD) | chromatic-glitch "match the register" |
| Shader transitions or shader backgrounds | ≤2 total | registry discovery ([VC]) |
| Motion-blur beats | 1–3 | references/motion-blur.md |
| Particle events | ≤2, each fired on a cause | particle-burst "punctuation" |
| Three.js / WebGL heavy beat | ≤1 | [3D] §5 |
| Transition types | 1 primary (60–70%) + ≤2 accents | overview, registry |
| Held stillness beats | exactly 1, before the payoff | titlecard-reveal stillness note, [VC] |
| Camera-led devices | ≤2 | motion-language (no bad pan/push); transcript-scroll (≤2 moves) |
| Distinct framings | ≥3 | visual-design |
| Easings | ≥3 characters | techniques.md |
| Text blur peak | ≤10 px (full-frame surfaces 18–20) | cut-catalog |
| Reading time | each text device: `dur ≥ 0.6 + 0.055 × chars` (VN high end) | dynamic-content-sequencing |

### 5.7 Seam and transition assignment

- **Inside a device's line-to-line change:** pick the seam by `rel_prev` (§3C.9). If the next device is in the same "world" (same bg and camera world), use only the seam and no between-frame transition.
- **Between devices:** use the channel's primary. An accent goes at (a) hook → context, if `rel = new_state`, and (b) the payoff, if `rel = payoff`. The outro uses crossfade or a color dip (0.6–1.0 s).
- **Duration by energy:** calm 0.5–0.8 s, medium 0.3–0.5 s, high 0.15–0.3 s. Opening transition 0.4–0.6 s.

### 5.8 Cross-video rotation memory (the "two shorts in a row never look alike" guarantee)

1. **Hook device cooldown.** The same hook device is not used within the last **3** videos of the channel.
2. **Signature uniqueness.** `signature = hook | primary_transition | dominant_bg | hero_symbol`. It must not match any of the last **10** videos. If it does, re-pick the hook (next best) or the bg variant.
3. **Device fatigue.** `recent_use` decays at 0.5 per video. Heavy devices (S1, S3, P5, M2, H5, T2) get an extra cooldown of 2 videos.
4. **Treatment rotation.** Rotate `gold_fill / hero_depth / glitch_accent / punctuation_particles` round-robin per channel, so each video gets at most one "flourish" family, and that family is not the same as the previous video's.
5. **Palette micro-rotation** *(own)*. Keep the brand palette fixed, but rotate the accent tone (FS: vermilion / gold / jade; BUD: saffron / ivory-gold / lotus-pink) on a 3-video cycle.
6. **Series consistency override.** A series flag (e.g. "Năm 2027" FS series) *pins* the hook device and the layout for brand recognition and rotates only the body devices. The data-driven winners ([VC], memory "chỉ làm kiểu thắng") outrank novelty. Variety must never displace the winning format; it varies around it.
7. **Write the choices back.** The planner writes the chosen `devices[]`, eases, seams and transitions into the plan JSON before rendering, so renders are reproducible and QA can audit. The ledger is updated only after a successful render.

### 5.9 Pseudocode (engine side, deterministic)

```python
def plan_motion(video_id, lines, profile, ledger):
    rng = xmur3(video_id)                       # hash-based tiebreak only
    purposes = [classify(l, i, len(lines)) for i, l in enumerate(lines)]
    rels = [relation(purposes, i, l) for i, l in enumerate(lines)]
    curve = energy_curve(len(lines))
    budget = Budget.from_profile(profile)       # overshoot, circle, gradient, glitch, shader, camera, photo
    picks = []
    for i, line in enumerate(lines):
        cands = [d for d in CANDIDATES[purposes[i]] if allowed(d, profile, line.data)]
        scored = []
        for d in cands:
            if violates(d, picks, i, budget, ledger, profile):   # §5.5–5.8 hard checks
                continue
            s = BASE[d][purposes[i]] + energy_fit(d, curve[i]) \
                - 0.6 * ledger.recent_use(d) - 0.4 * picks.count(d) \
                + 1e-3 * rng.frac(i, d)
            scored.append((s, d))
        d = max(scored)[1] if scored else FALLBACK[purposes[i]]  # fallback = L5/Q1-rise, always legal
        budget.consume(d)
        picks.append(d)
    seams = [choose_seam(rels[i], picks[i-1], picks[i]) for i in range(1, len(picks))]
    trans = assign_transitions(picks, rels, profile)            # primary + ≤2 accents
    eases = assign_ease_chars(picks, profile)                   # ≥3 chars, no adjacent repeat
    assert lint(picks, seams, trans, eases, budget)             # §5.10
    return MotionPlan(picks, seams, trans, eases)
```

### 5.10 Lint checks to run before render

- **Budgets.** Overshoot, circle, gradient, glitch, shader, particles, camera-led and stillness counts are all within budget.
- **Variety.** ≥3 framings; no adjacent repeats in framing, axis, ease or bg; ≥3 ease characters; hook device and signature pass the ledger.
- **Timing.** Every reveal is keyed to a VO cue word, and ≥50% of each device's reveals fall in its back half (doctrine 2). Climax dwell ≥1 s. Stagger windows ≤0.5 s. Reading time is met.
- **VN safety** ([KT] §3):
  - font coverage check on the device's face (`document.fonts.check('900 150px X','Ữ')`);
  - masks and tickers use 1.4× item height and padded clip boxes;
  - no char-level splitting except digits; glyph pools are digits only;
  - blur peaks ≤10 px and cleared to `none`; RGB split ≤6 px;
  - line-height ≥1.15 on multi-line uppercase.
- **Determinism.** No `Math.random`, `Date.now`, `repeat:-1`, CSS transition or `@keyframes`. Only `fromTo` entrances. Any years or dates are baked from Python.
- **Portrait safe zones.** The hero box is x 60–940, y 180–1500. Nothing load-bearing sits in the bottom ~17% caption band or the right action rail.
- **Perf** ([3D] §5): one WebGL canvas at most; ≤40 DOM particles; no full-frame SVG filters outside the transition window; benchmark a 3 s test render for any new device.

---

### Appendix: gaps and caveats found while reading

- **Rule defaults that conflict with the doctrine.** These rules ship `back.out` or bounce defaults: hacker-flip-3d, vertical-spring-ticker (intentional "click"), scale-swap, orbit-3d-entry, avatar-cloud-network, press-release-spring, physics-press, ai-tracking-box, reactive-displacement, the css-marker circle, and elastic push. The engine should centralise eases in one table so that a single budgeted overshoot is enforceable.
- **Doc conflict on ambient motion.** `hyperframes-creative` says every decorative element should drift or breathe. The faceless-explainer doctrine and `sine-wave-loop` say "reach for this last". For narrated explainers, follow faceless-explainer ([VC] §0).
- **Font fallbacks.** `kinetic-beat-slam` recommends Archivo Black, League Gothic and Oswald. Vietnamese coverage must be verified per face; Archivo Black is likely missing VN ([KT] §3.5).
- **Unbuildable at our scale.** `kinetic-type-beats` names "full-frame repeating-word pattern on a rolling 3D wave" and `zoom-out-workspace-reveal` names "blob → wavy line SVG morph". Both are flagged out of rule scope (they need hyperframes-keyframes morph or WebGL). Treat them as phase-2 only.
- **`animate-text`.** The 24 IDs are vocabulary only. The implementations live in the external Pixel Point skill, which is not installed. Use the IDs as names in plans and implement the per-word and per-line ones inline.
