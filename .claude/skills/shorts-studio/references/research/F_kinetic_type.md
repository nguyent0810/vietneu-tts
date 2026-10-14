# HyperFrames kinetic typography: research for the BUD/FS 9:16 shorts "beat text"

Read-only research, 2026-10-14. Sources are under `~/.claude/skills/`. Paths below are relative to that folder. Numbers in **bold** or `code` are quoted from the docs. Text marked *(own)* is my engineering advice, not doc content.

Docs read:
- `hyperframes-animation/{SKILL,rules-index,blueprints-index,techniques}.md`
- rules: `kinetic-beat-slam`, `gradient-text-sweep`, `3d-text-depth-layers`, `vertical-spring-ticker`, `counting-dynamic-scale`, `chromatic-glitch`, `sine-wave-loop`, `dynamic-content-sequencing`, `waterfall-entry`, `asr-keyword-glow`, `css-marker-patterns`, `hacker-flip-3d`, `spring-pop-entrance`, `discrete-text-sequence`, `depth-scatter-assemble`, `motion-blur-streak` (values), `split-tilt-cards` (values)
- blueprints: `kinetic-type-beats`, `typewriter-reveal`, `titlecard-reveal`, `video-text-pivot`, `ticker-takeover`, `overwhelm-surround`, `fixed-anchor-cycle`, `comparison-split`
- adapters: `animate-text`, `gsap-easing-and-stagger`, `gsap-timeline-and-labels`, `gsap-transforms-and-perf`
- `hyperframes-creative/references/{typography,beat-direction,motion-principles,house-style,visual-styles,data-in-motion}.md`
- `motion-graphics/categories/kinetic-type/module.md`, `motion-graphics/references/motion-vocabulary.md`
- `faceless-explainer/references/{motion-language,cut-catalog}.md`
- `media-use/audio/references/captions/{motion,authoring}.md`
- `hyperframes-keyframes/references/keyframe-patterns.md` (text subdivision)

For comparison I also read the current word scene, `hyperframes_short/compositions/longform.js` (about lines 1066–1280, `WORD.build/enter`), together with `longform.css` and `shortform.css`.

---

## 0. TL;DR: why the current beat text reads "not skilled enough"

The current engine already has many effects: `slam`, `rise`, `drop`, `type`, `sync`, `flip`, `wipe`, `zoom`, `breathe`, `rays`, `ripple`, `wave`, `flicker`, `grow`, `strike`, `split`, and `crack`. Each one is a single whole-card entrance followed by a static or zooming hold. Measured against the docs, four things are missing.

1. **No meaning-specific shapes.** The docs give each kind of content its own mechanism. A number counts and scales (`counting-dynamic-scale`). A list of options rolls on a slot ticker (`vertical-spring-ticker`). A contrast gets a marker strike plus a payoff arrival (`css-marker-patterns` sketchout plus inverse zoom-through). Spoken keywords get a karaoke envelope (`asr-keyword-glow`). In the current engine, every beat is "the phrase appears big".
2. **No seams between lines.** Lines cut card-to-card like slides. `cut-catalog.md` treats this as the primary failure: "Static cuts feel like a slideshow". Its fixes are velocity-matched cuts: zoom-through, inverse zoom-through, cut-the-curve, and waterfall cut.
3. **No development inside the hold.** Doctrine rule 2 in `motion-language.md` says to reveal pieces sequentially in the back ~50% of the scene, timed to the VO. The current pattern is the reverse: enter in the first 0.5s, then hold, with a slow `scale 1→1.035/1.05` zoom on `rise/drop/type/sync/flip/wipe/breathe/zoom`. The doctrine names that zoom explicitly: "No bad slow pan/push in the back half."
4. **Several current effects break the doctrine.**
   - `drop` uses `bounce.out`.
   - `sync`, `grow`, and `flip` use `back.out(1.6–2)`. The docs call bouncy "the **#1 instant turn-off**".
   - `breathe` tweens `letterSpacing`, a reflow property that "stutters". The doc fix is per-glyph `x`.
   - `wave` is a yoyo loop, which falls under "No lazy breathing".
   - `flicker` with opacity 0.55–1 jitter is borderline.

The upgrade path is mostly re-scoping effects you already have into a per-beat-type grammar (§4). The new pieces to add are karaoke emphasis, marker accents, the count-up, the slot ticker, and the seam cuts.

---

## 1. Technique catalog (15)

Each entry gives: what it looks like · when to use it in a narrated 30s short · implementation, quoting the doc numbers.

### T1. Kinetic beat slam: distinct entrance per phrase (`rules/kinetic-beat-slam.md`)
- **Look:** short phrases hit one at a time, each with a *different* transform axis, then stack into a locked finale.
- **When:** the hook line, or a 2–3 phrase punch inside one narrated line ("KHÔNG PHẢI MAY · MÀ LÀ NGHIỆP"). The docs call it "the recipe for 'punchy / rhythmic' taglines".
- **Implementation (doc values):**

  | Entrance | From | Duration | Ease |
  |---|---|---|---|
  | Scale-slam | `{scale:1.5, filter:"blur(16px)", opacity:0}` | `0.5` | `power4.out` |
  | Side-snap | `{x:-320, opacity:0}` | `0.45` | `expo.out` |
  | Rise-rotate | `{y:90, rotation:6, opacity:0}` | `0.55` | `circ.out` |

  - BEATS spacing **1.2–1.8s** ("<0.8s frantic, >2.5s loses the pulse").
  - Entrance **0.35–0.6s**. Exits **≤0.25s**.
  - Accent hue **exactly 1**. Display face **150px+, heavy weight**.
  - "Use **at least 3 distinct easings** across the piece."
  - "A reused `punchIn()` for all lines is the flat-but-competent tell. Vary the motion axis, reuse the ease *family*."
  - Finale: "don't just leave the last phrase sitting". Dress it with an underline sweep from `css-marker-patterns`.
  - Finale breath repeat must be `Math.max(0, Math.floor(holdDur/cycle) - 1)`. `Math.ceil` trips lint, and a negative repeat means infinite.

### T2. Waterfall entry: per-word whip-in, binary opacity (`rules/waterfall-entry.md`)
- **Look:** words snap up from below, each starting before the previous one settles. It reads as an accelerating wave that resolves composed.
- **When:** segment openers and any statement line. It is the best default "build" for Vietnamese, because words are syllables and the wave reads as speech rhythm.
- **Implementation:**

  | Word weight | Y offset | Duration | Overlap |
  |---|---|---|---|
  | Anchor/heavy | **60–80px** | **0.16–0.20s** | **0–2f gap** |
  | Normal word | **40–50px** | **0.13–0.16s** | **1f overlap** |
  | Light/punctuation | **30–48px** | **0.10–0.13s** | **1–2f overlap** |

  - Ease `power4.out` (`expo.out` for extra snap). "never `.inOut` on an entry."
  - "Opacity is **BINARY 0→1 via `tl.set`** — never fade an arrival."
  - `nextStart = prevStart + prevDuration − overlapFrames×F`, with "gaps SHRINK across the cascade".
  - "Split the FINAL word into fragments to extend the climax; fragments travel further."
  - One direction per cascade.

### T3. VO-synced per-word reveal with decaying slide (`techniques.md` #4 "Per-Word Kinetic Typography")
- **Look:** each word appears exactly when it is spoken. The slide distance decays word by word (`slides = [80, 60, 50, 25, 12]`), which "mimics a camera settling".
- **When:** any line where you have word times. The docs call it "The core technique for narration-driven videos." Your current `sync` effect is the right idea with the wrong ease (`back.out(2)`) and no decay.
- **Implementation:**
  - `tl.from(word, {x: slides[i], y: 14, opacity: 0, duration: 0.35, ease: "power2.out"}, timings[i])`.
  - Use `fromTo` inside clips (`motion-principles.md`: "Prefer `tl.fromTo()` over `tl.from()` inside `.clip` scenes").
  - Combine with the T2 binary-opacity rule for a snappier feel.

### T4. Karaoke keyword glow: spoken-word envelope (`rules/asr-keyword-glow.md`, karaoke variant)
- **Look:** the whole line is on screen dim. The word currently being spoken lerps to bright plus larger plus glow, then decays to a "breadcrumb" rest level. "At any moment 1–2 words are bright."
- **When:** the hook answer, or the line that carries the thesis. Use it whenever a full sentence should stay readable but emphasis must follow the narrator. The docs mark it "RECOMMENDED for video narration … short phrases (5–10 words)".
- **Implementation:**
  - Karaoke values: `ATTACK 0.1–0.25s`, `RELEASE 0.2–0.5s`, `REST_LEVEL 0.05–0.2`, `MAX_BLUR 30–45px`, `MAX_SCALE_BOOST 0.15–0.25`.
  - **One linear driver** (`ease:"none"`, duration = scene) loops over all words in `onUpdate`. "never one tween per word."
  - Use `text-shadow`, not box-shadow.
  - Timings must be monotonic and non-overlapping.
  - "Brand word window 1.5–2× a normal word". For you, the key term gets the longer window.
  - "Climax dwell ≥1s."
  - "Commit to a style — values between the default and karaoke columns yield awkward 'half-loud' emphasis."

### T5. Masked line rise ("mask-reveal-up" / Vox rise) (`techniques.md` #12 clip-path reveal masks; `animate-text` IDs `mask-reveal-up`, `line-by-line-slide`)
- **Look:** text slides up from behind an invisible baseline edge. Glyphs are cropped while travelling and unclipped at rest.
- **When:** a calm statement, the BUD register, or a two-line "A · B" where line 2 rises under line 1.
- **Implementation:**
  - The docs give only the generic clip-path example: content `x:400→0`, `duration:1`, `power2.out` through a fixed `clip-path: inset()` window.
  - `animate-text` holds the exact `mask-reveal-up` spec, but it is an external Pixel Point skill that is **not installed here** (`npx skills add pixel-point/animate-text`).
  - Your existing `rise` (`yPercent:125→0, .46s, power3.out, +.07s/word`) is already this. It needs the diacritic-safe mask in §3.

### T6. Zoom-through / inverse zoom-through seam (`faceless-explainer/references/cut-catalog.md`)
- **Look:** the outgoing text accelerates toward the camera and blurs. A hard swap happens at peak blur. The incoming text continues the same Z motion and decelerates into focus. "You **never see both texts at the same time**."
- **When:** forward zoom-through for a state change (hook → context, between chapters). Inverse zoom-through for an **arrival/payoff** ("Forward … reads *progressing through*; inverse reads *arriving at*"). Never on body text.
- **Implementation:**

  | Phase | Forward zoom-through | Inverse zoom-through |
  |---|---|---|
  | Exit (scale/blur on `power3.in`, opacity separate on `none`) | scale `1.0→1.2`, blur `0→10px`, opacity `1→0.15`, **0.2s** | scale `1.0→0.8`, otherwise the same |
  | Cut (`tl.set`) | outgoing `opacity:0`; incoming `opacity:0.15, scale:0.75, blur:10px` | incoming `scale:1.25` |
  | Entry | scale `0.75→1`, blur `10→0`, opacity `0.15→1`, `expo.out` **0.5s** | `1.25→1`, `expo.out` 0.5s |

  - Blur logic: **10px for text-scale** ("At 20px text smears into illegibility") and 18–20px only for full-frame surfaces.
  - Both sides must use the same peak blur. "Apply blur to the WRAPPER, never to individual children."

### T7. Waterfall cut: word-by-word cut-the-curve seam (`cut-catalog.md` §4)
- **Look:** words of the outgoing line rip left one by one, and the incoming line cascades in from the right mid-flight. "A wave across the seam."
- **When:** for an "UNFINISHED phrase (building one larger idea across several visually distinct scenes)", meaning consecutive narrated lines of the same thought.
- **Implementation:**
  - **Exit, per word:** `x 0→-230`, **0.34s `power4.in`**. Fade 0.18s `power1.in` as a separate tween. Stagger ~**0.022s** per word, with the last word finishing its fade at the cut.
  - **Entry, per word:** `fromTo x:+230→0, opacity:0.35→1`, **0.3s `power4.out`**. Gaps start at **0.05s and multiply by ~0.84 per word**.
  - "Pre-set all words to `x:+230, opacity:0` at build time."
  - Cut-the-curve whole-element version: same distance and duration on both sides, mirrored `power4.in`/`power4.out`, "Partial travel + fade, never full off-screen moves".

### T8. Counting with dynamic scale (`rules/counting-dynamic-scale.md`)
- **Look:** the number counts up while its scale grows from about 50% to 100%, so the climb escalates visually. The suffix arrives after the count lands, and the big label arrives early.
- **When:** number, age, count, or percent beats ("12 con giáp", "60 năm một vòng", "49 ngày"). For a *year* (1984), count from a nearby anchor such as 1900 or 1980, or use T9 or T10 instead. Counting 0→1984 reads as a price.
- **Implementation:**
  - `COUNT_DUR` **1.2–2.5s** ("below ~0.8s reads as a flash").
  - `START_SIZE ≈ 40–60% of END`. `COUNT_EASE power3.out ⭐` shared by the value and scale tweens.
  - **`tabular-nums` mandatory** plus a fixed-width container. `Math.round`, not floor.
  - "**Avoid `back.out` / `elastic.out` on the counter itself**". Overshoot is fine on the suffix: `SUFFIX_DUR 0.3–0.6`, `back.out(1.4–2.0)`.
  - "Label is BIG TEXT, not a page-style caption."
  - From `data-in-motion.md`: "A number on its own floats in empty space. Pair every metric with a visual element". Use a ring, a fill bar, or the 12-branch wheel highlight.

### T9. Vertical spring ticker: slot machine (`rules/vertical-spring-ticker.md`)
- **Look:** a masked one-item window clicks through items, "click click click", each step with a small overshoot. It is a sum of overlapping springs.
- **When:** a **list of years** or options ("Tý · Ngọ · Mão · Dậu"; "1984 · 1996 · 2008"). Also for "could be X, Y, Z…" before the real answer (the `ticker-takeover` blueprint, "More than ~3 reads as filler").
- **Implementation:**
  - `ITEM_HEIGHT ~ fontSize × 1.25` ("must hold capital descenders"). For Vietnamese, see §3: use about 1.4×.
  - `STEPS 1–4`. `STEP_DUR 0.3–0.7s`. `STEP_SPACING 0.3–0.5s` with **≤ STEP_DUR** so steps overlap.
  - `BOUNCE_FACTOR 1.4` gentle / `2.0` firm / `2.5+` climax.
  - "Pause between groups … one dramatic final step with a bigger BOUNCE_FACTOR".
  - "**Sum the springs in onUpdate — never tween the final position directly.**" "Climax dwell ≥1s."
  - Use `tabular-nums` for numeric tickers.
  - This is the one place the docs sanction `back.out`, as a small per-step click.

### T10. Decode / flap flip (`rules/hacker-flip-3d.md`)
- **Look:** characters flip down from 90° like an airport flap board, flickering pseudo-random glyphs before the real one clicks in.
- **When:** a *year* or *date* reveal ("Năm 2026 — Bính Ngọ"), or a "hidden truth" decode. Use the "**Number-only pool**" variant for years, which avoids the Vietnamese glyph-pool problem.
- **Implementation:**
  - `FLIP_DURATION 0.4–1.0s`, `CHAR_STAGGER 0.03–0.08s`, `REVEAL_THRESHOLD 0.5–0.7`, flicker **3–6 frames per glyph swap**.
  - `perspective: 1500px` on the scene root is **required**. Use `transform-origin: bottom` and `preserve-3d` per char.
  - A ghost copy reserves the width. The seed is char index plus quantized progress.
  - "Center the flip dead-center and add NO decorative chrome."
  - Reference numbers: `163px, 0.55s, 0.033s, 0.6`.

### T11. 3D extruded depth layers (`rules/3d-text-depth-layers.md`)
- **Look:** the same word is stacked N times with offsets, giving a physical extrusion. The depth "builds forward" on entry.
- **When:** the climax word or the payoff noun (the stamp beat). It suits FS's "poster/gold" register.
- **Implementation:**
  - `LAYER_COUNT 4–6`. `OFFSET_X/Y 1–3px each` (">4px reads as glitch"). *(own)* At a 1080-wide frame with 150–200px type, 2–3px per layer is still correct.
  - Back alpha: `0.6–0.85` max, `0.08–0.15` step, `0.1–0.2` floor. Set it via `rgba()` in `color`, not element opacity.
  - Cascade step `0.04–0.10s`, layer fade `0.3–0.6s`, depth grow `0.4–0.8s`.
  - One light direction for the whole piece. No `text-shadow` alongside.
  - "**No per-letter animation on top of the stack**". Depth applies to the settled state only.

### T12. Gradient sweep inside the glyphs (`rules/gradient-text-sweep.md`)
- **Look:** light travels through the letterforms while the glyphs stay still. Three forms: a continuous sweep, a word-to-word traveling highlight, and a hue sweep that settles to solid.
- **When:** the held closing line (a sheen on the CTA question), or a "gradient climax word". `house-style.md` lists gradient text as a "lazy default", so use it on **one** word per video at most.
- **Implementation:**
  - `SWEEP_SPAN 200–400%` (it "MUST exceed 100%" or the tween is a no-op). Tween `backgroundPosition "100% 50%" → "0% 50%"` for left-to-right travel, with `ease:"none"`.
  - `SWEEP_DUR 1.2–3s`.
  - Word highlight: `WORD_LAG 0.25–0.5s`, `HOT_RISE 0.15–0.3s`, `HOT_FALL 0.25–0.45s`.
  - Hue sweep: `40–180°` over `0.8–1.6s`, settling with a crossfade to a solid twin in `0.1–0.35s`.
  - Both `-webkit-background-clip:text` and `background-clip:text` are required. "One-pass sheen" uses a band ≤ ~25% of the span.

### T13. Chromatic / slice glitch (`rules/chromatic-glitch.md`)
- **Look:** for a fraction of a second the word breaks (RGB copies jitter, or horizontal slices displace), then it snaps sharp. "The payoff is the resolve."
- **When:** FS only, on a warning or "xung/khắc/phạm" beat ("TUỔI NÀY PHẠM THÁI TUẾ"). It is too loud for BUD. The monochrome slice variant is "the restrained enterprise read".
- **Implementation:**
  - `MAX_SPLIT 4–14px`. `JITTER_STEP 1/30–1/12s`, which must be ≥ one render frame. `GLITCH_DUR 0.25–0.6s` as an entrance, `0.12–0.2s` as a burst.
  - The hash is `Math.sin(n*127.1+311.7)*43758.5453` fract over `Math.floor(tl.time()/JITTER_STEP)`.
  - Clamp the rest state with `tl.set`.
  - Slices: `4–10` bands, `12–60px` offsets, `steps(3–6)`, `0.2–0.4s`.
  - "Glitch-stretch entrance" uses `scaleX 1.3–1.8 → 1`.

### T14. Marker accents: highlight / circle / burst / scribble / sketchout (`rules/css-marker-patterns.md`)
- **Look:** hand-drawn emphasis around or behind the words, not a fill.
- **When:**
  - **Sketchout or strike** on the wrong half of a contrast ("KHÔNG PHẢI X").
  - **Circle** on a key term or number.
  - **Highlight sweep** on the answer word.
  - **Burst** on a hype word.
  - **Scribble** underline for something subtle.
- **Implementation:**

  | Mode | Doc values |
  |---|---|
  | Highlight | bar `scaleX 0→1`, `0.5s power2.out`, opacity `.35`, bleed `inset: 0 -6px`, optional `skewX:-2` |
  | Circle | ring `130%×160%`, `rotate(-3deg)`, `scale 0→1`, `0.6s back.out(1.7)` |
  | Burst | ~12 lines at 30°, **vary `--len` 40–80px**, `scaleY 0→1`, `0.4s power2.out`, stagger `0.03` |
  | Scribble | dash draw `0.8s power1.inOut` |
  | Sketchout | two lines at ±12°, `0.3s` each, second one `+0.15s` |

  - "Cycle modes across caption groups … every 2–3 groups for high energy, 3–4 for medium, 4–5 for low."

### T15. Fixed anchor + hard-cut token swap (`rules/discrete-text-sequence.md`, `blueprints/fixed-anchor-cycle.md`, `kinetic-type-beats` sub-shape A)
- **Look:** one line is pinned ("TUỔI ___ NĂM NAY:") and only a slot changes by **instant hard cut** ("no roll/scroll/blur"). The cadence can accelerate into a flurry and then brake on the answer.
- **When:** "which zodiac signs are affected" lists, "everyone says…" roll-calls, or a fast tour of years before the real one.
- **Implementation:**
  - Steady stepping at **0.5–1s per state**, or the accelerating form: `HOLD_START 0.8–1.2s`, `DECAY 0.75–0.88`, `FLURRY_FLOOR 0.15–0.3s`, brake **≥ 4× the floor**.
  - "3–8 [states] read as a roll-call; 12–16 read as 'everyone'."
  - The anchor gets "Zero movement … no drift, no breathe".
  - Swap the DOM only on transitions (`lastTitle` guard), and set `min-width` on the wrap.

**Also relevant but secondary:**
- `spring-pop-entrance`: `power3.out`, `POP_DUR 0.4–0.7`, stagger `min(0.06, 0.5/N)`, hero visible by **t ≤ 0.5s**.
- `motion-blur-streak`: `PEAK_BLUR 8–30 (default 18)`, `MOVE_DUR 0.25–0.6`, out-family eases only.
- `depth-scatter-assemble`: golden-angle cloud, `ASSEMBLE_DUR 0.7–1.4`, `STAGGER 0.03–0.09`, n **4–14**. It suits word-level assembly; per-char use is too busy for Vietnamese.
- `split-tilt-cards` / `comparison-split`: `TILT 10–18°`, `ENTRY_DUR 0.6–1.2`, `RIGHT_AT = LEFT_AT + 0–0.3s`. In 9:16, stack the pair top and bottom (rotateX) instead of side by side.
- The registry has ready caption blocks: `caption-kinetic-slam`, `caption-editorial-emphasis`, `caption-weight-shift`, `caption-matrix-decode`, `caption-clip-wipe`, `caption-parallax-layers`. The docs say to run `npx hyperframes catalog --query "<what you want>" --json` before hand-rolling. I did not run it.

---

## 2. Rules and anti-patterns from the docs

### Ease and feel
- "**Smooth beats bouncy** … `power3.out` (house default)". "Bouncy `back.out` is the **#1 instant turn-off** in agent-made videos." Overshoot is "a rare, explicitly-playful exception", with `OVERSHOOT ≤ ~2`. The sanctioned overshoot spots are a ticker step click, a suffix, and a single badge ("the lone overshoot in the shot").
- "Easings are tone of voice … draw on ~3 easing characters across its beats — but vary **within the smooth families by energy** (`sine`/`power1` calm → `power3` standard → `power4`/`expo` punch)."
- "No more than 2 independent tweens with the same ease in a scene."
- `.out` for entrances, `.in` for exits, `.inOut` for moves. "Ease-in for entrances feels sluggish."
- For an exact settle, use the `springEase({response, dampingFraction:1})` helper in `adapters/gsap-easing-and-stagger.md`. It is seek-safe, and `ζ 0.80–0.85` gives "alive, not bouncy".

### Speed and rhythm
- "Fast (0.15–0.3s) — energy, urgency · Medium (0.3–0.5s) · Slow (0.5–0.8s) — gravity · Very slow (0.8–2.0s) — cinematic."
- "The slowest scene should be 3× slower than the fastest."
- "Don't start at t=0. Offset the first animation 0.1–0.3s."
- "Entrances need longer than exits" (for example 0.4s in, 0.25s out). Kinetic slam exits are ≤0.25s.
- "Don't use the same stagger on every scene. Each scene needs its own rhythm."
- "Total stagger sequence under 500ms regardless of item count" (`items × stagger ≤ ~0.5s`).
- "Name the pattern — fast-fast-SLOW-fast-SHADER-hold — before implementing."

### Monotony ("same entrance every beat")
- "Different entrance per phrase — a reused `punchIn()` for all lines is the flat-but-competent tell. Vary the motion axis."
- "Don't enter everything from the same direction … Vary: from left, from right, from scale, opacity-only, letter-spacing."
- "Don't use ambient zoom on every scene … Stillness after motion is powerful."
- Captions: "Don't use the same highlight animation on every group — cycle through styles using the group index." "**Emphasis words always break the pattern.**"
- `kinetic-type-beats`: "each full-screen beat … gets its own distinct entrance/exit MOVE."

### Beat sync to narration
- "**Reveal each piece … when the voiceover mentions it**, sequencing reveals across the **later ~50%** of the scene." "Don't dump everything on screen in the first ~25%."
- One shared time spine: "every element times off `BEATS[]` … the single biggest lever for 'rhythmic'". For narration, the spine is the word timestamps (from `hf_align`).
- The karaoke driver is linear and spans the scene. "Driver must end in sync with the scene's seek window."

### Holds, reading time, and words on screen
- "Fixed reading time. 3 seconds on screen = must be readable in 2. Fewer words, larger type."
- Caption grouping: "High energy: **2–3 words**. Conversational: 3–5. Measured/calm: 4–6."
- "One caption group visible at a time."
- `dynamic-content-sequencing`: `BASE_DURATION 0.6–1.5s` plus `SEC_PER_CHAR 0.03–0.06` ("lean high for wide-character languages"). `HOLD_FINAL 1.0–2.0s` must clearly exceed `HOLD_MID 0.5–1.0s`. **3–6 entries**.
- "Climax dwell ≥1s after the final step / final word." "Long static hold — the lockup is the payoff, give it 20–30% of the runtime."

### Aliveness during a hold
- "I'd rather have NO motion than BAD motion." The only sanctioned aliveness is **subtle jitter** via `sine-wave-loop` at the low end: `SCALE_AMP 0.008–0.015`, `Y_AMP 2–3px`, period `1.5–3s`.
- Halve the amplitude for long idles (> 6s) and add a settle-and-fade over the last ~20%.
- With N concurrent idles, use amplitude ≤ default/√N and stagger the periods.
- No slow push or pan in the back half.

### Typography and contrast
- "Weight contrast must be extreme … Video needs 300 vs 900."
- In-feed viewing: "body ≥32px, headlines ≥90px".
- "Tracking tighter than web: -0.03em to -0.05em on display sizes." See §3 for the Vietnamese caveat.
- "One expressive font per scene." "Don't pair two sans-serifs."
- Dark backgrounds: "Increase `line-height` by 0.05–0.1"; for display text "add 0.01em letter-spacing".
- One accent hue. Contrast is enforced by `hyperframes check` (WCAG AA).
- "Hero text: 60–80% of width." "Three layers minimum per scene": background treatment, foreground, accent.
- Data: "Pair every metric with a visual element."

### Determinism and render correctness (hard rules)
- Use one paused timeline and `fromTo` with explicit from-states.
- No `Math.random`, `Date.now`, `repeat:-1`, CSS `transition`, or `@keyframes`.
- Animate transforms and opacity only. Never `letterSpacing` or `fontSize`, which "stutter" on slow tails. For spacing, use per-glyph `x`.
- No concurrent conflicting transform tweens on one element. Split them across parent and child, for example an entrance on the wrapper and an emphasis pulse on the inner span.
- Measure DOM only at build, after `document.fonts.ready`, in a single-scene composition.
- Hard-kill exiting inner elements with `tl.set({opacity:0, visibility:"hidden"})`. Captions: "Every group **must** have a hard kill."
- `overflow: visible` on caption containers ("hidden clips scaled emphasis words and glow effects"). If emphasis scales above 1, set `maxWidth = safeWidth / maxScale`.

---

## 3. Diacritic-heavy text (Vietnamese) caveats

**What the docs say:** almost nothing. The only related lines are:
- `vertical-spring-ticker`: `ITEM_HEIGHT ~ fontSize × 1.25` "must hold capital descenders".
- `gsap-transforms-and-perf`: use per-glyph `x` (via SplitText) for spacing animation.
- `diagram-design`: "treats combining marks as non-advancing".
- `cut-catalog`: 10px blur cap for text legibility.
- Caption `fitTextFontSize` for overflow.

There is no guidance on splitting text with combining marks, on line-height for stacked marks, or on clip masks cropping accents. Everything below is *(own)* engineering guidance, partly confirmed by fixes already in `longform.css` (the `.lf-ts-gold .ch` padding and the `.lf-fx-rise .wd` mask padding) and the comment "giữ một dòng: tách đôi 2 dòng cắt mất dấu" ("keep one line: splitting into 2 lines cuts off the marks").

1. **Splitting.**
   - Always `normalize("NFC")` before splitting. Every Vietnamese letter, including the uppercase stacked ones (Ầ U+1EA6, Ỗ U+1ED6, Ữ U+1EEE), exists precomposed, so after NFC, `Array.from` gives one code point per visible letter. The current `glyphs()` already does this.
   - For robustness against stray NFD input or combining marks that do not compose, prefer `new Intl.Segmenter("vi", {granularity: "grapheme"})`. It is deterministic.
   - Never split by UTF-16 index (`str[i]`, `substring` in typewriters). The `discrete-text-sequence` smooth slice uses `substring(0, Math.floor(len.v))`, so run it over a grapheme array instead.
   - Prefer **word-level (syllable) animation over char-level** for Vietnamese. Words are short, so char staggers of 0.03–0.05s read as stutter. Every inline-block char also loses kerning pairs.
   - Keep char-level for effects that are inherently per-glyph: decode (T10), ticker digits, and short single words only.
   - Keep `white-space: nowrap` per-word wrappers so lines never break mid-syllable. This is already done in `.wd`.

2. **Vertical metrics.**
   - Uppercase stacked marks (Ầ Ẫ Ỗ Ữ) rise about 0.25–0.35em above cap height. The dot below (Ặ Ộ Ợ) and the hook descend about 0.1–0.15em.
   - Multi-line uppercase needs `line-height ≥ 1.15–1.2`. Use more on dark backgrounds, where the docs add 0.05–0.1.
   - `.lf-ts-poster` (League Gothic, line-height .96) and `.lf-bigword` (1.05) will collide stacked marks on two-line cards. Either keep those cards to one line (as `split/crack` already does) or raise the line-height.
   - The ticker `ITEM_HEIGHT` should be about **1.4× fontSize** for Vietnamese caps, not 1.25×, and the mask must be pixel-exact to it.

3. **Clip masks and overflow.**
   - Any `overflow:hidden` or `clip-path` used as a reveal mask (T5, T7, `wipe`, `split/crack`, the slice glitch) must be padded and negatively margined so the resting state is unclipped. The current rise uses `padding:.3em .02em .1em; margin:-.3em 0 -.1em`. Use `.35em` top for Ẫ/Ỗ in heavy weights, and `.15em` bottom.
   - Use negative insets for `clip-path` wipes, as the current `inset(-30% 100% -30% 0)` does.
   - The slice glitch's `inset()` bands use percentages of the box. Make sure the box includes that padding, or the top band will not carry the marks.
   - `background-clip:text` (T12, gold): the background must cover the mark zone. The current `.lf-ts-gold .ch {padding:.32em 0 .24em; margin:-.32em 0 -.24em}` is the right pattern; apply it to any gradient-fill word.
   - 3D flips with `transform-origin: bottom`: the hinge should be the baseline, not the padded box bottom. Otherwise dot-below marks swing oddly. Acceptable either way, but verify with `snapshot`.

4. **Tracking.**
   - The docs say "-0.03em to -0.05em" for display sizes. For Vietnamese uppercase in heavy weights, cap at about **-0.02em**. Double marks (tilde plus circumflex, hook plus breve) are wider than their base letters and collide at tighter tracking.
   - Condensed faces (League Gothic, Oswald) are the worst case.

5. **Font coverage.**
   - The bundled display faces differ in Vietnamese support. Check each one before using it for a beat. To my knowledge, **Archivo Black has no Vietnamese subset**, which would mean fallback glyphs for marked letters, a broken look. I believe League Gothic, Oswald, Montserrat, and Anton ship Vietnamese, and Be Vietnam Pro does natively.
   - Check with `document.fonts.check('900 150px "X"', 'Ữ')`, plus a render snapshot of a pangram like "ĐỪNG NGỦ QUÊN: ẦẪỖỮỰỢẶỘ".
   - The kinetic-beat-slam doc suggests "Archivo Black / League Gothic / Oswald". For Vietnamese, use Be Vietnam Pro 800/900, plus one secondary that you have checked.

6. **Effects that degrade marks.**
   - Blur: marks vanish first. Keep text blur peaks ≤10px (the doc says so) and make sure blur is exactly 0 at settle. Use `filter:"blur(0px)"` and clear it with `tl.set(el, {filter: "none"})`, because a residual blur softens marks.
   - `-webkit-text-stroke` outlines (the `outline` style): thin strokes on the small marks look like noise at render scale. Use ≥3px stroke at 150px+, or fill the marks.
   - RGB split: `MAX_SPLIT` at the low end (4–8px), because offset marks read as extra accents.
   - Decode (T10): the glyph pool must not mix Vietnamese letters, which would flash wrong-tone words that read as real words. Use digits or symbols (`"0123456789"` for years), or Latin caps without marks.
   - `scaleY` "grow" from 0 squashes the marks into the letter for most of the tween. It is fine as a fast entrance but not as a slow one.

7. **Measuring.** Run `fitTextFontSize` (portrait `maxWidth 900`) with the real font, uppercase, after `document.fonts.ready`. If emphasis scales to 1.15–1.25 (T4 karaoke), set `maxWidth = 900/1.25`.

8. **Reading speed.** Use the high end of `SEC_PER_CHAR` (0.05–0.06 s/char). Uppercase Vietnamese with marks is slower to parse than Latin caps. Prefer mixed or title case for anything over about 5 words; your `TS_MIXED` set already does this.

---

## 4. Recommended beat grammar: 6 lines, ~30s narrated short

Assumptions: each line runs about 4–6s, with `ln.start/end` and word times `w.t` available. The subtitle stays in its band at the bottom. The beat text owns the 260–1500px zone.

### Principles applied
- Each line gets one **entrance**, one **development** in the back half on a VO cue, and one **seam** into the next line.
- Consecutive lines must differ in **motion axis**: Z/scale, Y-mask, X, 3D-rotate, in-glyph, discrete.
- **Ease characters** rotate: `power3` → `power4/expo` → `power2/sine`.
- There is **at most one** overshoot moment per video: a ticker click or a suffix.
- One accent hue is used throughout.
- Background: a faint oversized ghost word at 3–8% opacity with a slow drift counts as the background layer. No push on the text itself.

### Grammar table

| # | Beat kind | Entrance (axis · technique) | Back-half development (on VO cue) | Seam into next line |
|---|---|---|---|---|
| L1 | **Hook claim/question** (~0–4.5s) | **Z · scale-slam** (T1): `scale 1.5→1, blur 16→0, power4.out 0.5s`, first word at `+0.15s`. Full line max 2–3 words per group. | Climax word gets a **circle marker** (T14) when spoken. | **Forward zoom-through** (T6), a state change into the answer. |
| L2 | **Hook answer / thesis** (~4.5–10s) | **Y · waterfall entry** (T2), words whipping up on their own VO onsets (T3 timing), binary opacity. | **Karaoke glow** (T4) walks the line; the answer word (window 1.5–2×) then gets a **highlight sweep** (T14) and holds ≥1s. | **Waterfall cut** (T7), since the idea continues. |
| L3 | **Number / date reveal** (~10–15s) | **Discrete + in-place · count-up with dynamic scale** (T8): `power3.out`, 1.2–2.5s, tabular-nums, plus a ring or wheel-sector fill. For a *year*, use the **flap decode** (T10) with a digit pool instead. | Suffix or unit (`năm`, `tuổi`, `%`) slides in **after** the count, `back.out(1.5)`. This is the one overshoot. The big label sits above. | Cut-the-curve **upward** (y −230 → +230, power4 in/out). |
| L4 | **Contrast A vs B** (~15–20s) | **X · side-snap** for A (`x:-320→0, expo.out 0.45`), stacked top half, at 0.56em (the existing `.p1` style). | On "không phải / mà là", a **sketchout strike** (T14) crosses A and A dims to 0.55. B then arrives by **inverse zoom-through** (T6, 1.25→1, expo.out), the payoff "arriving at". Optional static **3D depth** (T11) on B. | **Hard cut** ("Hard cut = 'wake up' / disruption"), to reset energy before the list. |
| L5 | **List of years / signs** (~20–25s) | **3D/vertical · fixed anchor + spring ticker** (T15 + T9): the anchor ("TUỔI CẦN LƯU Ý:") is pinned and the slot ticks one step per spoken item. `STEP_DUR 0.45`, `STEP_SPACING ≤ STEP_DUR` when items are said fast, `BOUNCE 1.4`, and the final step at `2.0`. | A pause before the last item, then the big final step. Optional **circle** on the final item. A count of ≤4 steps; more than that becomes a flurry with T15's decay. | **Forward zoom-through** into the close. |
| L6 | **Closing question / CTA** (~25–30s) | **Mask · line rise** (T5), calm `power3.out`, words rising behind the baseline. Mixed case. | **One-pass sheen** (T12, `SWEEP_DUR` = the hold, `ease:none`) or a **scribble underline** on the question word. Final dwell ≥1–2s and dead still, with at most subtle jitter (`SCALE_AMP ≤0.01`). | End. Only the final scene may fade. |

**Axis sequence:** Z → Y → in-place → X(+Z payoff) → vertical/discrete → mask. No two neighbours repeat.

**Ease sequence:** power4 → power4-cascade+linear driver → power3 → expo → back(step) → power3+none. The power4 on L1 and L2 is fine because they use different mechanisms (scale versus word cascade). If you want strictness, switch L2 to `expo.out`.

### Rotation algorithm *(own)*, to keep variety across a batch of shorts
1. Classify each narrated line: `hook | answer | number | year | contrast | list | close | statement`. Use regex and plan hints. The existing `KHÔNG PHẢI … · …` detector already catches contrast.
2. Each class has a candidate list of (technique, axis). For example, `statement → [waterfall(Y), rise(mask), slam(Z), karaoke(in-glyph), side-snap(X)]`.
3. Pick the least-recently-used candidate (the same idea as the current `pick()`), with two hard constraints:
   - its axis is not equal to the previous line's axis;
   - its ease family is not equal to the previous line's.
4. Choose the seam from the relationship between the lines:
   - same thought → waterfall cut or cut-the-curve;
   - new state → zoom-through;
   - payoff → inverse zoom-through;
   - disruption → hard cut.
5. Budget one overshoot per video and one gradient per video. Glitch is FS only, at most once.
6. Retire or rework these current effects:
   - `drop`: bounce.out.
   - `wave`: a yoyo loop.
   - `grow` and `flip`: back.out. Switch them to `power3.out` or `springEase ζ0.85`.
   - `breathe`: tweens `letterSpacing`. Replace it with per-word `x` spread or per-glyph `x`.
   - The slow `scale→1.035/1.05` push on 8 effects, which the doctrine flags as a "bad back-half push". Replace it with VO-cued development or nothing.

---

## 5. Deterministic GSAP snippets (top 5)

All snippets assume `tl` is the single paused timeline registered at `window.__timelines["main"]`. Times are absolute seconds and nothing is random. `words` are `{w, t}` from hf_align.

### Helper: Vietnamese-safe split and mask CSS
```js
const SEG = new Intl.Segmenter("vi", { granularity: "grapheme" });
const graphemes = (s) => Array.from(SEG.segment(String(s).normalize("NFC")), (x) => x.segment);
// Build: one .wd (nowrap) per syllable; .mask wrapper only when the effect needs clipping.
function buildWords(box, text, { mask = false } = {}) {
  return text.split(/\s+/).filter(Boolean).map((word, i) => {
    if (i) box.appendChild(document.createTextNode(" "));
    const wd = document.createElement("span"); wd.className = "wd" + (mask ? " mask" : "");
    const inner = document.createElement("span"); inner.className = "in"; inner.textContent = word;
    wd.appendChild(inner); box.appendChild(wd); return { wd, inner, word };
  });
}
```
```css
.wd { display:inline-block; white-space:nowrap; }
.wd > .in { display:inline-block; will-change:transform; }
/* mask that never crops Ầ/Ỗ/Ữ above or the dot-below: pad + cancel with negative margin */
.wd.mask { overflow:hidden; vertical-align:bottom; padding:.36em .04em .16em; margin:-.36em -.04em -.16em; }
.big { font-family:"Be Vietnam Pro"; font-weight:900; line-height:1.18; letter-spacing:-.02em; }
```

### S1. VO-synced waterfall build (T2 + T3): binary opacity, weight-scaled travel, decaying offsets
```js
// Each word lands on ITS spoken onset; anchors travel further, light words snap.
function waterfallSynced(tl, items, times, { heavy = new Set() } = {}) {
  const F = 1 / 60;
  let prevEnd = -1;
  items.forEach(({ inner, word }, i) => {
    const isHeavy = heavy.has(i) || i === items.length - 1;           // last word = climax
    const light = word.length <= 2;                                    // "là", "và", "ở"
    const y = isHeavy ? 72 : light ? 36 : 46;                          // doc: 60–80 / 30–48 / 40–50 px
    const dur = isHeavy ? 0.19 : light ? 0.12 : 0.15;                  // doc: .16–.20 / .10–.13 / .13–.16 s
    const at = Math.max(times[i] - 0.04, prevEnd - F);                 // never queue; ≤1f overlap
    tl.set(inner, { opacity: 1, y }, at);                              // BINARY reveal — no fade
    tl.fromTo(inner, { y }, { y: 0, duration: dur, ease: "power4.out", immediateRender: false }, at);
    prevEnd = at + dur;
  });
}
// CSS start state for .in: opacity:0 (set once at build with gsap.set, not CSS-only).
```

### S2. Karaoke keyword glow (T4): one linear driver, attack/sustain/release
```js
function karaoke(tl, items, wins, t0, t1, { keyIdx = -1 } = {}) {
  const A = 0.15, R = 0.35, REST = 0.12, BLUR = 38, BOOST = 0.18;     // doc karaoke column
  const REST_RGB = [150, 140, 125], ON_RGB = [255, 244, 222], KEY_RGB = [232, 178, 70];
  const env = (t, s, e) => t < s ? 0 : t < e ? Math.min((t - s) / A, 1)
    : t < e + R ? 1 - ((t - e) / R) * (1 - REST) : REST;
  const lerp = (a, b, k) => Math.round(a + (b - a) * k);
  const d = { t: t0 };
  tl.fromTo(d, { t: t0 }, { t: t1, duration: t1 - t0, ease: "none", onUpdate: () => {
    items.forEach(({ inner }, i) => {
      const [s, e] = wins[i];                                          // key word: window ×1.5–2 upstream
      const k = env(d.t, s, e), tgt = i === keyIdx ? KEY_RGB : ON_RGB;
      inner.style.color = `rgb(${lerp(REST_RGB[0], tgt[0], k)},${lerp(REST_RGB[1], tgt[1], k)},${lerp(REST_RGB[2], tgt[2], k)})`;
      inner.style.textShadow = `0 0 ${(BLUR * k).toFixed(1)}px rgba(255,214,140,${(0.55 * k).toFixed(3)})`;
      inner.style.transform = `scale(${(1 + BOOST * k).toFixed(4)})`; // .in only — entrance lives on .wd
    });
  }}, t0);
}
```
This drives the inner span. Run any entrance tween on the `.wd` wrapper so the two never fight over `transform`.

### S3. Zoom-through / inverse zoom-through seam (T6)
```js
// wrapOut/wrapIn = whole-line wrappers. tCut = seam time (≈ next line start).
function zoomSeam(tl, wrapOut, wrapIn, tCut, inverse = false) {
  const exitScale = inverse ? 0.8 : 1.2, inScale = inverse ? 1.25 : 0.75, B = 10; // 10px = text-scale
  tl.fromTo(wrapOut, { scale: 1, filter: "blur(0px)" },
    { scale: exitScale, filter: `blur(${B}px)`, duration: 0.2, ease: "power3.in" }, tCut - 0.2);
  tl.fromTo(wrapOut, { opacity: 1 }, { opacity: 0.15, duration: 0.2, ease: "none" }, tCut - 0.2);
  tl.set(wrapOut, { opacity: 0, visibility: "hidden" }, tCut);                 // hard kill
  tl.set(wrapIn, { visibility: "visible", opacity: 0.15, scale: inScale, filter: `blur(${B}px)` }, tCut);
  tl.to(wrapIn, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, tCut);
  tl.set(wrapIn, { filter: "none" }, tCut + 0.5);                              // no residual blur on marks
}
```

### S4. Number count-up with dynamic scale and a late suffix (T8)
```js
// <div class="cnt-wrap"><span class="cnt">0</span><span class="sfx">năm</span></div>; .cnt{font-variant-numeric:tabular-nums}
function countUp(tl, el, sfx, from, to, at, { dur = 1.6, startScale = 0.5, yearMode = false } = {}) {
  const st = { v: from };
  const fmt = (v) => yearMode ? String(Math.round(v)) : Math.round(v).toLocaleString("vi-VN");
  el.textContent = fmt(from);
  tl.fromTo(st, { v: from }, { v: to, duration: dur, ease: "power3.out",
    onUpdate: () => { el.textContent = fmt(st.v); } }, at);
  tl.fromTo(el, { scale: startScale, opacity: 0 }, { scale: 1, opacity: 1, duration: dur, ease: "power3.out" }, at);
  tl.fromTo(sfx, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.45, ease: "back.out(1.5)" }, at + dur); // the one overshoot
}
// Year: countUp(tl, el, sfx, 1980, 1984, t, { dur: 1.2, yearMode: true }) — count from a near anchor, never from 0.
```

### S5. Spring ticker for a spoken list of years or signs (T9 + T15 anchor)
```js
// <div class="tk" style="height:H;overflow:hidden"><div class="tk-in">[items, each height H]</div></div>
// H ≈ 1.4 × fontSize for Vietnamese caps (doc says 1.25× for Latin). Anchor line above stays pinned.
function springTicker(tl, inner, H, stepTimes, { bounce = 1.4, finalBounce = 2.0, dur = 0.45 } = {}) {
  const springs = stepTimes.map(() => ({ p: 0 }));
  const apply = () => { inner.style.transform = `translateY(${-springs.reduce((a, s) => a + s.p, 0) * H}px)`; };
  apply();
  springs.forEach((s, i) => {
    const last = i === springs.length - 1;
    tl.fromTo(s, { p: 0 }, { p: 1, duration: last ? dur + 0.15 : dur,
      ease: `back.out(${last ? finalBounce : bounce})`, onUpdate: apply }, stepTimes[i]); // step on spoken onset
  });
}
// stepTimes = onset of each spoken item (hf_align). If consecutive onsets are > STEP_DUR apart the
// steps don't overlap -> fine for a narrated list (each "click" lands on its word); keep ≥1s dwell after the last.
```

### Bonus: sketchout strike on the wrong half of a contrast (T14)
```js
// .strike-wrap{position:relative} .sl{position:absolute;top:50%;left:-4px;right:-4px;height:6px;background:var(--accent);transform-origin:left center}
tl.fromTo(slashA, { scaleX: 0, rotation: -12 }, { scaleX: 1, rotation: -12, duration: 0.3, ease: "power2.out" }, tSaid);
tl.fromTo(slashB, { scaleX: 0, rotation: 12 },  { scaleX: 1, rotation: 12,  duration: 0.3, ease: "power2.out" }, tSaid + 0.15);
tl.to(partA, { opacity: 0.55, duration: 0.3, ease: "power2.out" }, tSaid + 0.15);
```

---

## 6. Open items and verification hooks
- `animate-text` (24 named effects with exact specs, including `mask-reveal-up`, `kinetic-center-build`, `depth-parallax-words`) is **not installed**. Install it with `npx skills add pixel-point/animate-text` if you want exact named specs. Note that its upstream license is undeclared.
- Run `npx hyperframes catalog --query "caption kinetic" --json` to see whether a registry block (`caption-kinetic-slam`, `caption-weight-shift`, `caption-clip-wipe`) can be adapted, rather than hand-rolling.
- After implementing, run `scripts/animation-map.mjs` to flag dead zones and stagger consistency. Run `hyperframes snapshot --at` on each seam's cut frame and on each beat's settled frame, using a diacritic pangram, to catch cropped marks.
