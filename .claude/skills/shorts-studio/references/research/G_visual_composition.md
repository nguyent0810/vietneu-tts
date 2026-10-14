# HyperFrames research: visual composition and media presentation for BUD / FS Shorts

Scope: 9:16 1080x1920 narrated Shorts (25–35 s) rendered with HyperFrames 0.8.75 (one paused GSAP timeline).
Problem to solve: every short reads as "dark gradient + thin ring + photo dropped into a circle/arch + centered uppercase text + numbered rows".
Channel data: lines carried by generic stock photos lose viewers about 2x faster than lines carried by kinetic text or data graphics. Opening frames built on kinetic text hold viewers better than opening frames built on photos.

All paths below are relative to `~/.claude/skills/`. Read-only research. I did not change any repo file.
Two read-only CLI listings were run with Node 22 from nvm (`~/.nvm/versions/node/v22.23.3/bin`). HyperFrames 0.8.75 refuses to run on Node 20. The commands were `hyperframes catalog --json`, ten `catalog --query` searches, and `media-treatment --capabilities/--capability`. Their raw output sits next to this file (`catalog.json`, `mt_caps.json`).

---

## 0. Why the current look fails, according to the docs

The docs name these failure modes directly:

- **One repeated framing.** `faceless-explainer/references/visual-design.md` § Layout says: "Use **≥3 different framings per video** so it doesn't read as one repeated template; never the same framing twice in a row." Our shorts use one framing (centered hero + ring) for every line.
- **"Generic decorative shapes standing in for a designed metaphor"** are on the "Don't show" list (same file). A thin ring that means nothing is exactly that. `motion-principles.md` § Visual Composition adds: "Connector lines earn their place… A line the frame can lose without losing meaning is decoration: cut it."
- **Centered-and-floating** is called a web pattern. "Anchor to edges… Zone-based layouts, not centered stacks" (`hyperframes-creative/references/video-composition.md`, `motion-principles.md`).
- **Full-screen linear gradients on dark backgrounds** "band visibly under H.264 compression. Use a radial gradient, a solid fill, or solid + localized glow instead" (`video-composition.md` § Color Presence).
- **Stock filler.** `faceless-explainer/sub-agents/frame-worker.md` says: "build the idea the narrative describes; never fall back to generic decorative bokeh or stock filler." That matches our retention data. A photo should be *evidence* or *atmosphere with a job*, never the line's only content.
- **The circle is the house cliché.** Many registry items are circle mechanics: `iris-reveal`, `sdf-iris`, `match-cut` (circle), `carousel-circle-*`, `constellation-hub`. In `transitions/overview.md` the circle iris is an *accent*, not a primary. Treat every circle as a one-per-video accent at most.

**Motion doctrine to adopt (`faceless-explainer/references/motion-language.md` Part 2):**
1. Use `power3` long-tail settles, not bounce.
2. Reveal each element when the VO names it, spread across the back ~50% of the beat. Never dump everything in the first 25%.
3. "No lazy breathing" and no slow pan/push in the back half: "I'd rather have NO motion than BAD motion." The only sanctioned aliveness on a hold is subtle low-amplitude jitter (`sine-wave-loop`).
4. Internal seams are velocity-matched cuts.

Note a doc conflict: `hyperframes-creative/references/video-composition.md` and `house-style.md` say "every decorative element should have ambient motion: breathe, drift". The faceless-explainer doctrine is stricter and was distilled from a golden corpus. For narrated explainers, follow faceless-explainer.

---

## 1. Scene/layout patterns that replace "photo in a circle" (15)

Portrait rules apply to all of them (`visual-design.md` § Portrait & square):
- Stack vertically, not side-by-side.
- Anchor a centered hero at y ≈ 0.42 × H, which is about 806 px on 1920.
- Run bigger type with fewer words per line.
- Keep the bottom ~17% (about 326 px) for captions. Plan key content into the top ~83%. Backgrounds may stay full-bleed.
- The invented hero should fill 40–60% of the frame. Keep at least 3 depth layers.

Patterns 1–15 are a menu. Per video, use at least 3 framings, never the same framing twice in a row. Allocate one deliberately held beat.

### P1. Full-bleed graded photo + Ken Burns + type in a band
- **When:** an establishing atmosphere beat (pagoda roof at dawn, Tết market, incense smoke). Keep it at 2–3 s, and never use it as the hook (channel data). Always pair it with a kinetic line or number in the same beat, so the photo is the `background` role and not the focal.
- **How:**
  - Put the photo full-bleed in an outer wrapper. Do the entrance (opacity/y) on the parent and Ken Burns on the child `<img>`. Never run two transform tweens on the same element; a `y` entrance plus a `scale` Ken Burns kills the entrance (`hyperframes-creative/references/motion-principles.md` § Load-Bearing GSAP Rules).
  - Ken Burns recipe: `tl.fromTo("#clip .inner", {scale:1.05, xPercent:0}, {scale:1.2, xPercent:-12, duration:4, ease:"none"}, 0)` (`hyperframes-core/references/creator-editing-recipes.md` § Pan / Ken Burns). For a calm feel use the subtler `scale 1 → 1.04` over the beat (`motion-principles.md` § Image Motion Treatment). `hyperframes-keyframes/SKILL.md` describes this as "Animate wrapper translation plus scale."
  - Dim the background 30–50% (`frame-worker.md`).
  - Grade with `data-color-grading` (see §2) instead of CSS filter overlays.
  - Text sits in a solid or translucent band anchored to an edge, such as a top band, not floating over the middle.
- **Source:** creator-editing-recipes.md, motion-principles.md, frame-worker.md, media-treatments.md.

### P2. Stacked split (top/bottom), the portrait form of split-screen
- **When:** comparisons, which are FS's bread and butter: hợp vs kỵ, tuổi A vs tuổi B, trước/sau, Tết xưa/nay. For Buddhism: wrong view vs right view.
- **How:**
  - Use two bands with a hard horizontal divider. Each band has its own color identity, with a faint glow per side (`blueprints/comparison-split.md`).
  - Wide split-screen does not travel to portrait. Use stacked equivalents (`visual-design.md`).
  - Animate the crop/mask wrappers and the divider geometry, not the clips (`hyperframes-keyframes/SKILL.md` "Split-screen handoff").
  - The registry component `comparison-split` does a persistent divider wipe of a vivid "after" layer over a muted "before" layer.
  - For a 3D variant, `split-tilt-cards` uses mirrored `rotateY` "book-open" tilts. It needs `perspective` on the root and `preserve-3d`. In portrait, tilt on `rotateX` (top card tilts back, bottom card tilts forward).
  - The signature punctuation is a pill badge popping at each card's inner edge. That is the one sanctioned overshoot.
- **Source:** blueprints/comparison-split.md, rules/split-tilt-cards.md, visual-design.md, hyperframes-keyframes/SKILL.md.

### P3. Vertical "almanac strip": spatial pan across stations
- **When:** enumerations and sequences. Examples: 12 con giáp in order, a run of birth years (1984 → 1996 → 2008), the Tết days (23 tháng Chạp → 30 → Mùng 1), stages of a sutra story. This replaces the numbered list rows.
- **How:**
  - Pre-place all stations on one oversized tall canvas (e.g. 1080 × 5000).
  - One `.world` wrapper is the camera. Pan it ease-in-out from station to station, about 1 s per station, and reveal each label on arrival. Land and hold on the last station.
  - Camera math: `viewport-change` (single wrapper, `T = -offset × S`), sequenced by `multi-phase-camera`, each stop centered via `coordinate-target-zoom`.
  - Hand-drawn leading lines between stations use `svg-path-draw`.
  - No depth push: the pan is the camera.
  - Registry: `pan-stations` (lateral camera across labeled stations with dwell) and `scroll-camera-story` (a tall slotted scene travels past the camera with parallax layers and decelerates into a held final section). Pan vertically for 9:16.
  - Mark the moving `.world` with `data-layout-allow-overflow` and keep `overflow:hidden` on the scene root, or `check` will flag overflow (`blueprints/camera-journey.md` § Overflow).
- **Source:** blueprints/spatial-pan-stations.md, rules/viewport-change, multi-phase-camera, coordinate-target-zoom.

### P4. Camera journey across one big diegetic world
- **When:** a cause→effect or a "find it on the map" beat. Examples: a giant lịch vạn niên spread, a house floor plan with a door facing a direction, a la bàn (compass) dial, a temple layout.
- **How:**
  - Use a multi-leg journey: dive in → a beat fires → travel to the consequence → landing push. "Vary the leg verbs — a journey of four identical pushes reads as a slideshow."
  - Use `power4.out` on dives and landings and `power2.inOut` on repositioning legs. Never use spring/back easing on a camera.
  - Keep one camera state object with a single writer (`applyCamera()`). Measure targets once after `document.fonts.ready` and bake them. Never measure in `onUpdate`.
  - Add a `depth-of-field-blur` pull on neighbors and `motion-blur-streak` at peak leg velocity.
  - Sub-shape B, "cursorless flight" (`3d-camera-flight`: perspective stage + `preserve-3d` `.world`, tilt-to-flatten), fits a calendar grid with standing cards.
- **Source:** blueprints/camera-journey.md, rules/multi-phase-camera.md, coordinate-target-zoom.md, depth-of-field-blur, motion-blur-streak, 3d-camera-flight.

### P5. Macro → whole: a single decelerating zoom-out reveal
- **When:** hooks and "re-scope" payoffs. Examples:
  - Open full-bleed on one chữ Hán (福 / 禄 / 寿), then pull back to show it on a câu đối scroll on a door.
  - Open on a single day number, then pull back to show the whole month page and where that day sits.
  - Open on the hand mudra, then pull back to the whole Buddha statue.
- **How:**
  - Start `cam.scale` far in, centered on the detail. Tween scale → 1 and translate → 0 with one shared ease (`expo.out` / `power4.out`). Use `viewport-change` math, or the `coordinate-target-zoom` "zoom out" variant with nested wrappers.
  - HARD RULE: one zoom-out per shot, no zoom-in anywhere. The camera locks after the reveal and later motion is element-level only.
  - Always leave a post-lock act, such as a label or number landing.
  - Registry component `pull-back-reveal`: "a tight stat detail holds, then one decelerating camera pull-back reveals the headline and supporting cards."
- **Source:** blueprints/zoom-out-workspace-reveal.md, rules/coordinate-target-zoom.md.

### P6. Diegetic almanac / tear-off calendar page (lịch bloc), the FS signature
- **When:** any date/year line: ngày hoàng đạo, Tết dates, "năm 2026 là năm Bính Ngọ". This is far stronger than text on a gradient, because the page *is* the data. That fits the finding that data graphics retain better.
- **How (DOM, no photo needed):**
  - A paper sheet fills about 70% of the frame, with a red header band.
  - A jumbo day numeral at about 28cqw, following biennale-yellow's "Chapter Divider" jumbo numeral and bold-poster's "Hero Stat" (numeral rotated −6° with a stacked text-shadow).
  - Lunar date and can-chi underneath.
  - A ledger of giờ hoàng đạo rows: biennale-yellow "Ledger", a tabular calendar with mono time · serif title · hairline-soft rules.
  - Reveal rows on the VO cue, using `grid-card-assemble` vertical-list "SNAP" mode or `waterfall-entry`.
  - Make the date resolve mechanically with the registry block `split-flap-board` (Solari drum cascade) or the component `number-wheel` / `slot-machine-roll`.
  - Exit or seam with the registry component `torn-paper-rip`: a fibrous tear runs across and the sheet lifts away, revealing the next scene. It is literally tearing off the calendar page.
- **Source:** frame-presets/biennale-yellow/FRAME.md (Ledger, Chapter Divider), frame-presets/bold-poster/FRAME.md (Hero Stat), blueprints/grid-card-assemble.md, registry catalog.

### P7. Paper, scroll and ink surfaces (giấy dó, câu đối, sutra scroll)
- **When:** quotes, sayings, sutra lines (BUD), proverbs (FS). Use the scroll or paper as the ground instead of a dark gradient.
- **How:**
  - Ground is a warm paper token. Atmospheric depth comes from a radial bloom. Biennale-yellow's "sun bloom" is the primary depth layer, a layered radial covering 42–70% of the frame.
  - Quote set as "Manifesto / Quote": italic serif, centered, ~60% silence (biennale-yellow).
  - Brush strokes draw via `svg-path-draw`. Registry options: `svg-stroke-trace`, `whiteboard-ink` (pen nib follows the stroke), and `ink-bleed-reveal` (liquid ink blooms through paper under a gooey filter, then contracts as a crisp mark resolves, with seeded paper grain).
  - Seams: `paper-collage-reveal` (torn scraps flutter away) or `torn-paper-rip`.
  - A vertical scroll that unrolls is a `clip-path: inset()` reveal on a tall panel (`hyperframes-animation/techniques.md` §12 Clip-Path Reveal Masks) plus a roller element translating with the clip edge. Never tween `height` (`rules-index.md`: width/height tweens are forbidden; use scale/clip).
- **Source:** biennale-yellow FRAME.md, techniques.md §12, rules/svg-path-draw, registry catalog.

### P8. Text-as-window (photo seen through giant type)
- **When:** one hero word per video, as a hook or chapter word: "TẾT", "NGỌ", "PHẬT", "NGHIỆP". The photo becomes the texture of the word instead of a rectangle.
- **How:**
  - Registry `svg-mask-reveal`: "A soft token-colored sweep reveals media only through an editable SVG wordmark mask."
  - `texture-mask-text`: CSS luminance masks that cut through letterforms, 66 textures.
  - `caption-texture`: a flowing texture mask over large uppercase text, with lava/marble/metal/wood/concrete/rock.
  - Hand-rolled: `background-clip:text` / `mask-image` on a heavy display face, or SVG `<clipPath>` with `<text>`.
  - Follow with a forward zoom-through *into* a letter that becomes the full-bleed photo. Scale the word wrapper 1 → ~8 with blur peaking at 18–20 px for a full-frame subject (cut-catalog Blur Logic).
  - Caveat: `house-style.md` lists gradient text as a lazy default. Image-through-type is different, but cap it at once per video.
- **Source:** registry catalog, cut-catalog.md, house-style.md.

### P9. Parallax depth layers (2.5D) / text behind subject
- **When:** a stock photo with a clear subject (Buddha statue, lion dance head, hoa mai branch, kitchen altar). The headline sits *between* sky and subject, so the photo looks designed.
- **How (`hyperframes-creative/references/composition-patterns.md` § Text Behind Subject):**
  - Three layers: base photo (z1), headline (z2), and a background-removed cutout of the same photo (z3) that occludes the text.
  - Make the cutout with `npx hyperframes remove-background in.png -o cutout.png`.
  - Put opacity on a *wrapper* div, never on a timed media element. The framework forces opacity:1 on active clips.
  - Drive parallax by moving the layers at different rates on one camera push.
  - Registry options: `caption-parallax-layers` (behind-subject 3D text layering), `camera-rig-depth-stack` (card stack with depth, parallax, focus shift), `focus-rack` (focus shifts once between two depths via blur/dim/scale/parallax).
  - Use rack focus between subject and headline with the `depth-of-field-blur` rule.
- **Source:** hyperframes-creative/references/composition-patterns.md, rules/depth-of-field-blur, registry catalog.

### P10. Card stack / slot-machine list (replaces numbered rows)
- **When:** "3 tuổi hợp", "5 điều kiêng", "4 đại nguyện".
- **How:**
  - From `grid-card-assemble` → Benefits vertical-list, use one of three sub-modes:
    - (a) BUILD: marker pop + check draw + pill mask-wipe per line.
    - (b) SNAP: the whole stack steps up one slot per beat so the newest lands in a bright focal slot and older lines dim by position.
    - (c) STREAM: the list scrolls fast past a focal slot and decelerates onto the chosen item.
  - SNAP and STREAM are the slot-machine feel, built with `vertical-spring-ticker`.
  - For photos, use the registry block `mk-placeholder-grid` (2-up/3-up/hero+two rounded media grid with per-cell inside-scale framing). Then, as a transition, `parallax-zoom`: the center card scales to fill the frame while siblings parallax outward. For example, a grid of 12 zodiac tiles where the one tuổi being discussed takes over the frame. `parallax-unzoom` is the reverse.
  - Never use identical same-size card grids by default (`house-style.md` lazy-default list). Give the hero card scale and forward overlap.
- **Source:** blueprints/grid-card-assemble.md, rules/vertical-spring-ticker, house-style.md, registry catalog.

### P11. Data-as-hero (count-up, ring/bar fill, year table)
- **When:** any number, which is where our retention is strongest. Examples: năm sinh, khoảng cách tuổi, số ngày còn lại đến Tết, percentages, a can-chi cycle position (60-year cycle).
- **How:**
  - Use `counting-dynamic-scale`: font scale grows with the value, with `tabular-nums` and `Math.round` in a seek-safe `onUpdate`.
  - Pair the number with a graphic that fills (`stat-bars-and-fills`: bar `scaleY` stagger, progress `scaleX`, measured SVG ring). The rule is "Numbers need visual weight. A number on its own floats in empty space" (`hyperframes-creative/references/data-in-motion.md`).
  - Same-concept stats keep the same visual space, and only the value changes.
  - No pie charts, gridlines, legends, or chart libraries; build with GSAP + SVG/CSS.
  - Blueprint `dataviz-countup`: the camera pushes THROUGH the data to land on one hero metric. Its Hook variant is a "cold-open counter burst".
  - Registry: `chart-story` (bars/line/donut/progress landing exact supplied values), `conic-progress-ring`, `number-wheel`, `star-rating-fill`, `mk-line-graph`, and the block `bar-chart-race`.
  - A 60-cycle can-chi "position" reads well as a horizontal progress strip with a marker (P3 strip) rather than another ring.
- **Source:** data-in-motion.md, blueprints/dataviz-countup.md, rules/counting-dynamic-scale, stat-bars-and-fills.

### P12. Kinetic type beats / fixed anchor with cycling token (hooks)
- **When:** the first 1–3 s of every short (data: kinetic openers retain best), and for punchy pivots.
- **How:**
  - `kinetic-type-beats` is "the workhorse (6 roles)". A fixed line swaps tokens in place by hard cut ("Tuổi **Tý** … **Ngọ** … **Mão** đừng làm điều này"), or a statement builds across full-screen beats onto a payoff.
  - `fixed-anchor-cycle`: one element pinned and never moving while the adjacent slot cycles, often accelerating.
  - Rules: `discrete-text-sequence` (hard-cut word swap), `dynamic-content-sequencing` (per-word staggered reveal), `kinetic-beat-slam`, `3d-text-depth-layers` (stacked extrusion on huge type).
  - Registry: `kinetic-type-swap` (held sentence with one masked slot rolling through alternatives), `line-swap`, `ticker-takeover`, `headline-slam`, `per-word-rise`, `variable-axis-type`, `weight-wave`.
  - First visible motion should land within 0.2 s of the beat start (`storyboard-recipe.md` beat table).
- **Source:** blueprints-index.md, blueprints/kinetic-type-beats.md, fixed-anchor-cycle.md, motion-language.md.

### P13. Annotated evidence photo (Vox-style), the way to make stock *earn* its time
- **When:** the photo shows the thing being discussed. Examples: a door facing the street (FS), the mudra or the robe color (BUD), a mâm ngũ quả arrangement.
- **How:**
  - Show the full-bleed photo, then `coordinate-target-zoom` punches into the relevant region (measure its center; `T = -offset` for nested wrappers).
  - A hand-drawn marker circles it while a connector draws to a mono label.
  - Registry: `vox-annotate` (keyword marker + connector + callout as one beat), `hw-callout-circle`, `hw-arrow`, `hw-box-label`, `cursor-annotate` (pen nib draws loop/underline/arrow), `marker-highlight`.
  - Rule `css-marker-patterns` covers highlight / circle / burst / scribble / sketchout.
  - This turns "generic image" into "evidence", which is the opposite of the retention-killing pattern.
- **Source:** rules/coordinate-target-zoom.md, rules/css-marker-patterns, registry catalog.

### P14. Freeze-frame cutout / scrapbook (photo as a taped object)
- **When:** a person, deity statue or object should "pop" off the page. Examples: Ông Táo, Quan Âm statue, a lucky object.
- **How:**
  - `npx hyperframes remove-background still.png -o cutout.png`.
  - Place it as a direct-root timed `<img class="clip">`.
  - Install `freeze-frame-dressing`, which owns the paper, tape and flash. The host only animates the cutout (`fromTo y:42, scale:.86, rotation:-2 → 0/1/0.4`).
  - Inspect the matte over light and dark plates, and reject halos or missing edges.
  - Related: `hw-frame` (media in a hand-drawn border with doodles and a handwritten caption).
- **Source:** media-use/references/media-treatment-recipes.md § Freeze-Frame Cutout, registry catalog.

### P15. Media → stat → line pivot (image yields its weight)
- **When:** a beat that has one genuinely good photo plus a number and a takeaway, 4–6 s.
- **How:**
  - From blueprint `video-text-pivot`: the media holds big, then SLIDES aside (x + scale down) into the space the hero stat fills. It is one weight-transfer at a shared anchor (`scale-swap-transition`).
  - Then both clear and kinetic text types into the vacated center. Seal it with a pill `scaleX` snap.
  - In portrait: the photo slides UP into a top band while the stat rises into the lower-middle.
- **Source:** blueprints/video-text-pivot.md, rules/scale-swap-transition.

### Also available, used sparingly
- **Constellation hub** (nodes ring a center, then a push-in with DoF onto the core) fits a 12-con-giáp wheel or ngũ hành cycle. It is another circle, so use it at most once per video and prefer the linear strip P3 (`blueprints/constellation-hub.md`).
- **Zoom-through into a card** uses the `zoom-through-transition` component.
- **Cinemagraph** (registry block `cinemagraph`) freezes a still with one living feathered region, such as incense smoke rising. It is good for BUD calm beats.

### Proposed per-short layout rotation (actionable for engine.js)
Assign each VO line a framing from a pool with constraints:
- Line 1 is always P12 or P5 (kinetic or macro hook, never a photo-first open).
- Use at least 3 distinct framings per short.
- Never use the same framing on adjacent lines.
- Use at most one circle mechanic per short.
- Use at most about 30% of lines with a photo as focal. Photo lines must be P9/P13/P14/P15 or P1-as-background, never a bare photo with a line of text.
- Allocate exactly one held beat (stillness) before the payoff.

This mirrors `visual-design.md` § Layout and § Video direction (held-frame allocation, negative list naming both failure modes: slideshow and screensaver).

---

## 2. Canonical media treatments (`media-use/references/media-treatments.md` + `media-treatment-recipes.md`)

### 2.1 Policy and rules
- **Scope.**
  - Target meaningful photographic `<img>`/`<video>` only. Skip text, SVG, logos, icons and UI.
  - Treatments are whole-media. They cannot isolate a face or region; crop or mask a separate layer first.
  - The path is Rec.709/SDR only.
- **Classify the request into a lane before choosing a recipe:**
  - correction (dark/flat/cast)
  - wheels/curves/HSL
  - preset or custom treatment ("polished, premium, warm, cinematic, fit the topic")
  - shader effect ("retro, print, ASCII, glitch")
  - privacy blur/pixelate
  - framing/motion only ("draw attention without changing pixels")
  - finite seek-safe treatment keyframes ("reveal, focus, depixelate")
  - Registry overlay ("REC HUD, light leak, flash, freeze-frame cutout")
- **One primary intent** is the creative anchor. "Do not add a stylized Effect when correction solves the complaint." "Do not stack effects merely to make the answer look more sophisticated." Generate at most two candidates. A second candidate is an escalation.
- **Match strength to intent.** A named bold look (halftone, engraving, print) must "read unmistakably". Correction and polish stay restrained.
- **Persist with the CLI**, not hand-written CSS: `hyperframes media-treatment --selector "#img" --grading '<json>' --apply --json`. It validates keys and ranges and writes `data-color-grading='{…}'` on the element. Use the canonical `details`/`effects` fields for vignette, grain, blur and pixelate. "Do not duplicate them with CSS filters, SVG turbulence, opacity, or decorative DOM overlays."
- **Animatable (seek-safe) properties.** Author the start value inline on the media element, then use finite `tl.to()` only: no frame-zero `tl.set`, no CSS animation, no random, no `onUpdate` (`media-use/references/grading.md`).
  - `--hf-color-grading-intensity` 0..1
  - `-lut-intensity` 0..1
  - `-exposure` −2..2
  - `-blur` 0..1
  - `-bloom` 0..3
  - `-kuwahara` 0..1
  - `-pixelate` 0..1
  - `-ascii` 0..1
  - `-dither` 0..1
- **Cost.** Blur, Bloom and Kuwahara are multipass. More than two simultaneous full-frame multipass layers needs a playback check.
- **Verify.** Before/after contact sheets (`hyperframes snapshot <proj> --frames 3 --no-end --describe false --output snapshots/treatment-before`). Keep the source unchanged if the result is not clearly better.
- **Overlays.** Install the named Registry block (`hyperframes add <name> --no-clipboard --json`) once, and never recreate it by hand.

### 2.2 Recipe list (names → what it does → when)

| Recipe | Payload seed / mechanism | Use / avoid |
|---|---|---|
| **Natural Portrait** | `{"preset":"skin-soft","intensity":0.6}` | People-focused photos; not a face mask or retouch |
| **Product Polish** | restrained correction protecting label/material color | Physical objects (e.g. lì xì envelope, incense, a bowl); not UI |
| **UI Fidelity** | preserve pixels | Screenshots and UI; never stylize |
| **Film Memory** | `vintage-wash` 0.6 + vignette 0.12 + grain 0.12 (+ optional gate weave and gentle exposure flicker ±0.03 on the paused timeline) | "Warm memory, restrained flashback": Tết xưa, Jataka past-life stories. Not the default meaning of "cinematic" |
| **Creator Camcorder** / **VHS Playback** / **8mm Home Movie** | tape/film character presets (+ `camcorder-hud` overlay) | Retro / home-video beats only |
| **Editorial Halftone** | `effects.halftone 0.75–1, halftoneSize 0.15–0.55`, real CMYK screen | Poster/print/newsprint beats; keep captions as DOM above |
| **Two-Ink Editorial Print** | `effects.twoInkPrint`: warm midtones → vermilion, shadows → teal, on warm paper | Poster frames, bold print transitions. Vermilion suits FS red; do not combine with halftone |
| **Monochrome Screen Print** | `monoScreen` cells (circle/square/diamond/triangle/line) + 2-color palette | Graphic portrait inserts, newspaper feel |
| **Engraved Illustration** | `effects.engraving` line art + palette `["#101216","#f3eddf"]` | Editorial/historical illustration, source → line-art reveal. Strong fit for BUD (woodblock/sutra print feel) |
| **Crosshatched Sketch** | `effects.crosshatch` multi-direction lines | Hand-rendered documentary cutaways |
| **CRT Display** / **Procedural ASCII** | display/glyph art | Not on-brand here |
| **Ordered Palette Dither** | 4×4 Bayer + palette, e.g. **Warm Print** `["#17121a","#824c50","#e09873","#f7ddb1"]` | Posterized social beats, finite source→palette reveal |
| **Cached Error Diffusion** | exact Floyd–Steinberg (pre-baked) | Historical dither look |
| **Organic Light Leak** | registry `organic-light-leak-overlay` (finite rise/peak/recovery) | "One motivated memory beat, time shift, warm scene handoff". Good BUD transition |
| **Freeze-Frame Cutout** | ffmpeg still → remove-background → `freeze-frame-dressing` | Scrapbook hold / subject pop (P14) |
| **Social Flash / Editorial Reveal** | registry `editorial-flash-overlay`, midpoint on the cut | One high-energy cut per video, never every scene |

CLI 0.8.75 presets available: neutral, warm-daylight, clean-studio, skin-soft, food-pop, night-lift, muted-editorial, vintage-wash, mono-clean, mono-fade, soft-boost, bright-pop, deep-contrast, creator-camcorder, vhs-playback, home-movie-8mm, editorial-halftone, two-ink-print.

Named palettes for art effects: noir, ink-paper `#1a1a2e/#f5f5dc`, amber-glow, golden-hour `#1a1205 #4a3510 #8b6914 #d4a017 #fff8dc`, sepia, warm-print, electric-ink, forest, deep-sea, and others. Custom palettes take 2–6 `#rrggbb` colors. Run `hyperframes media-treatment --capability <family>` for exact ranges.

### 2.3 Making stock photos feel intentional (synthesis)
1. **One house treatment per channel, applied to every photo in a video.**
   - FS: `warm-daylight` or `muted-editorial` + vignette ~0.12 + light grain. Optionally Two-Ink Print for poster beats.
   - BUD: `vintage-wash` / Film Memory, or Engraved Illustration with a golden-hour or ink-paper palette.
   - A consistent grade makes unrelated stock read as one photographed world. (Inferred from "keep one primary intent as the creative anchor" + `data-in-motion.md` visual continuity.)
2. **Never a raw flat image.** Every image gets motion treatment: perspective tilt, slow zoom, a device or frame wrapper, a parallax layer, or a clipped scroll reveal (`motion-principles.md` § Image Motion Treatment).
3. **Give the photo a role.** Either `background` (full-bleed, dimmed 30–50%, type is the focal) or `foreground subject` (cutout, annotated, framed). The 2x drop-off happens when a stock photo is the *only* focal.
4. **Crop to the meaningful detail.** Zoom-to-target (P13) or a macro open (P5) instead of showing the whole generic frame.
5. **Turn stock into illustration** (Engraving / Two-Ink / Halftone / Monochrome Screen) so it matches a paper/ink design system. Stylized stock stops reading as stock. Keep text as DOM above the treated media.
6. **Embed it in a diegetic object.** A photo slot inside the almanac page (P6), a taped cutout (P14), a hand-drawn frame (`hw-frame`), or the inside of a letter (P8).
7. **Keep photo beats short and never first.** Lead with kinetic type or data, and put photos in the middle as evidence or atmosphere.
8. For a grade reveal moment, use `grade-split-reveal` (flat vs finished, hard edge sweep, real shader grading), or animate `--hf-color-grading-intensity` 0 → 1 on the entrance.

---

## 3. Transition and cut vocabulary

### 3.1 Between frames: the `transition_in` registry (`faceless-explainer/scripts/lib/transitions.json`, `references/story-design.md`)
Valid names: `cut | crossfade | blur-crossfade | push-slide LEFT/RIGHT/UP/DOWN | zoom-through | squeeze`.

| Name | Default dur | Energy | Mechanics |
|---|---|---|---|
| crossfade | 0.5 s | any | opacity swap, `power2.inOut` |
| blur-crossfade | 0.6 s | calm | old → blur 10px, scale 1.03, fade; new from blur 10px, scale .97. Default when two frames' backgrounds differ a lot |
| push-slide DIR | 0.5 s | medium | x or y travel, `power3.inOut` |
| zoom-through | 0.4 s | high | old scale 2.5 + blur 8 + fade (`power3.in`); new from scale .5 + blur 8 (`power3.out`) |
| squeeze | 0.4 s | medium | old scaleX → 0 at left edge, new expands from right edge |
| (max) | 2.0 s | | `default_high_energy: zoom-through`, `default_calm: blur-crossfade` |

**Variety rules:**
- "Pick **2-3 transition types for the whole video** and repeat them" (story-design.md).
- Ordered steps use a consistent `push-slide`. A soft layer or atmosphere shift uses crossfade / blur-crossfade. Zooming into a detail or pulling back uses zoom-through. A clean topic switch uses `cut`.
- `hyperframes-animation/transitions/overview.md`: "Pick ONE primary (60-70% of scene changes) + 1-2 accents. **Never use a different transition for every scene.**"
- "Every composition uses transitions." "Exit animations are BANNED except on the final scene. The transition IS the exit."
- Outgoing and incoming animate at the same T.

**Energy table (overview.md):**
- Calm (wellness/brand story/luxury): blur crossfade / focus pull. Shader: cross-warp morph, thermal distortion. Accent: light leak, circle iris. 0.5–0.8 s, `sine.inOut`/`power1`. Use for BUD.
- Medium (explainer): push slide / staggered blocks. Shader: whip pan / cinematic zoom. 0.3–0.5 s, `power2`/`power3`. Use for FS.
- High: zoom through / overexposure, 0.15–0.3 s, `power4`/`expo`.

**Mood:**
- Warm/inviting: light leak, blur crossfade, focus pull, film burn.
- Editorial/magazine: push slide, vertical push, diagonal split, shutter, whip pan. Fits FS.
- Premium: focus pull, blur crossfade, color dip to black, cross-warp morph. Fits BUD.

**Narrative position:**
- Opening: the most distinctive transition, 0.4–0.6 s.
- Between related points: the primary, ~0.3 s.
- Topic change: something different (staggered blocks, shutter, squeeze).
- Climax: the boldest accent.
- Wind-down: blur crossfade, 0.5–0.7 s.
- Outro: crossfade or dip to black, 0.6–1.0 s.

**Blur by energy:** calm 20–30 px / 0.8–1.2 s; medium 8–15 px / 0.4–0.6 s; high 3–6 px / 0.2–0.3 s.

**Presets:** snappy 0.2 `power4.inOut`, smooth 0.4 `power2.inOut`, gentle 0.6 `sine.inOut`, dramatic 0.5 `power3.in→out`, instant 0.15 `expo.inOut`, luxe 0.7 `power1.inOut`.

**Don't use:** star iris, tilt-shift, lens flare, hinge/door (catalog.md).

**Shader transitions:** use at most 2 per video (`hyperframes-registry/references/discovery.md`).

### 3.2 Inside a frame: seam cuts (`faceless-explainer/references/cut-catalog.md`)
The principle for all of these: "cut at peak velocity, match direction and speed on both sides of the cut."

- **Zoom-Through (forward), for a within-scene text swap / state change** (hook → context, new chapter):
  - Exit 0.2 s: scale 1 → 1.2 and blur 0 → 10 px (text; 18–20 px for a full-frame surface) on `power3.in`. Opacity 1 → 0.15 on linear, as a separate tween.
  - Hard cut via `tl.set`: incoming at opacity .15, scale .75, blur 10.
  - Entry 0.5 s `expo.out` → scale 1, blur 0, opacity 1.
  - Never show both texts at once.
- **Inverse Zoom-Through, for arrival/payoff:**
  - Exit scale 1 → 0.8 (0.2 s).
  - Incoming from scale 1.25 + blur 10 → 1 in 0.5 s `expo.out`.
  - Reads as "arriving at".
- **Cut the Curve, the default for every scene-to-scene seam on x/y:**
  - Exit `x 0 → −230` (or y) on `power4.in`, 0.2–0.4 s.
  - Entry from +230 → 0 on `power4.out`, same distance and duration (≈3,070 px/s at the cut).
  - The exit fade completes at ~25–30% of travel (0.18–0.3 s). Entry fades in fast from ~0.35.
  - Partial travel only, never full off-screen moves. Entry duration ≥ exit duration.
  - Registry component `cut-the-curve`.
- **Waterfall Cut, a text-to-text seam at word granularity:**
  - Per word exit `x 0 → −230` over 0.34 s `power4.in`, fade 0.18 s `power1.in`, stagger ~0.022 s.
  - Entry `x +230 → 0`, opacity .35 → 1 over 0.3 s `power4.out`, with SHRINKING gaps (start 0.05 s, ×0.84 per word).
  - Pre-set all words at build time.
- **Choosing:** an unfinished phrase spanning visuals uses cut-the-curve or waterfall. A state change uses zoom-through. A payoff uses inverse zoom.
- **Anti-patterns:** 20 px blur on text, elements on different paths across a cut, gentle `power2.out` entries, full off-screen moves, zoom-through on body text.

**Registry seam/transition pieces worth adopting** (all names verified in the live catalog):

| Item | Type | What it does | Fit |
|---|---|---|---|
| `torn-paper-rip` | component | Fibrous paper tear lifts away to reveal the next scene | FS signature: tear-off calendar |
| `ink-bleed-reveal` | component | Ink blooms through paper, contracts to a crisp mark | BUD / FS quotes |
| `paper-collage-reveal` | component | Torn scraps flutter off | Scrapbook beats |
| `halftone-dissolve` | component | A → B through a growing halftone dot field | Pairs with print treatments |
| `whip-pan-cut` | component | Velocity-matched whip with capped motion blur | FS energy accent |
| `text-match-cut` / `type-match-cut` | component | Line becomes line at the speed peak; headline splits around an incoming panel | Text seams |
| `line-swap` | component | Masked full-line replacement on a beat | Text seams |
| `hw-scribble-transition` | block | Scribble bands cover, cut beneath, then clear | Hand-drawn FS style |
| `organic-light-leak-overlay` | block | Finite warm leak | BUD calm transition |
| `editorial-flash-overlay` | block | Camera-flash cut | One per video max |
| `curtain-reveal` | component | Velvet curtains part | Reveal of a "lucky" answer (theatrical) |
| Shader blocks | block | `cross-warp-morph`, `thermal-distortion`, `light-leak`, `whip-pan`, `cinematic-zoom`, `domain-warp-dissolve`, `sdf-iris` | ≤2 per video |

### 3.3 Suggested grammar for a 25–35 s short
- 6–9 beats of 2.5–5 s each. Beat-length guidance is 1.5–3.5 s, ~3 s for a beat that must be read (`storyboard-recipe.md`).
- One seam family as primary, plus one accent at the payoff.
- **FS:** primary `push-slide UP` (vertical read order in 9:16) plus internal cut-the-curve on y. Accent `torn-paper-rip` at the payoff and `zoom-through` on the hook → context seam.
- **BUD:** primary `blur-crossfade` (0.6 s), internal waterfall cuts for sutra lines, one `organic-light-leak-overlay` at the emotional turn, and a dip to dark at the end.

---

## 4. Palette / frame-preset recommendations

### Vietnamese glyph caveat (blocker)
Several preset fonts lack a Vietnamese subset on Google Fonts. This is from my own font knowledge, not the skill docs, so verify it per font: render "Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi, Bính Ngọ, Phật, nghiệp".
- **No Vietnamese subset:** Shrikhand (bold-poster), Instrument Serif (biennale-yellow), Bebas Neue (coral).
- **Have Vietnamese:** Playfair Display, EB Garamond, Lora, Source Serif 4, Newsreader, Noto Serif / Noto Serif Display, Be Vietnam Pro, Archivo, Barlow, Oswald, Anton, Inter, Space Grotesk, JetBrains Mono.
- The repo already uses Be Vietnam Pro + Lora + JetBrains Mono.
- So adopt the presets' *composition systems and color discipline*, and swap display faces. Each FRAME.md lists font substitution as a "Known Gap" path, e.g. bold-poster's CJK note: "keep tilts + red + double-borders to carry the identity".

### 4a. Feng shui / zodiac channel (FS): warm red + gold, Tết feel
**Primary base: `bold-poster`**, with `coral`'s region-split as the second framing.

- **Why bold-poster:** "Populist editorial poster… vintage Italian sports-magazine cover / mid-century European annual report".
  - Four colors only: white / brown-black ink `#1C1410` / tomato red `#D8000F` / off-white `#F5F2EF`. Red is the lone accent and every numeral is red.
  - Tilted display (−6° stat, −5° close).
  - "Hero Stat" is a full red panel with a white tilted numeral and stacked text-shadow.
  - Double-border grids for data. Red em-dash bullets capped at 3. A red progress bar on every frame.
  - This maps almost one-to-one onto Tết print culture (red paper, black ink, poster numerals). Its 9:16 table is documented: Hero Stat "numeral centered, taller", Financial Grid "2 across / stacked".
  - It is a *light* canvas, which immediately breaks the "dark gradient + ring" sameness. `video-composition.md`: "Don't switch to dark — make light cinematic" (grain plus strong structure).
- **Why add coral's structure:** "three solid surfaces meeting at hard edges… the region boundary IS the layout"; 45° hatch texture; oversized wallpaper numerals at 12% behind titles. In 9:16 that is a 38/62 top band + body split. It is a ready second framing for P2 (stacked split) and P6 (almanac header band).
- **Gold:** bold-poster forbids a fifth color. For Tết, add gold only as *atmosphere*, borrowing biennale-yellow's "sun bloom" mechanism (a radial bloom 42–70% of the frame, never text) or as a foil rule. Candidate hexes:
  - `jewel-rich` row `#780116 #F7B538 #DB7C26 #D8572A #C32F27` (lacquer red + gold)
  - `dark-premium` row `#0B090A #161A1D #660708 #A4161A #E5383B`
  - `jewel-rich` `#6F1D1B #BB9457 #432818 #99582A #FFE6A7` (lacquer brown/gold)
- **Suggested FS `frame.md` tokens** (adapted, not invented hues):
  - paper `#F5F2EF`, ink `#1C1410`, red `#C32F27` (or bold-poster `#D8000F`), lacquer `#780116` for full-bleed statement panels, gold bloom `#F7B538` at 15–25%.
  - Display: Playfair Display 900 or Noto Serif Display Black, tilted on numerals. Body: Be Vietnam Pro. Data: JetBrains Mono.
- **Visual-style reference:** "Folk Frequency" (cultural, festive, pattern tiles) is the closest named style to Tết. Its bouncy easing (`back.out`, `elastic`) conflicts with the faceless motion doctrine, so take its *pattern/texture* idea (hoa văn tiles as a hatch-like texture) but keep `power3` motion.
- **Media treatment:** `warm-daylight` / `muted-editorial` + vignette, or Two-Ink Print (vermilion/teal on warm paper) for poster beats.
- **Transitions:** editorial/magazine (push slide, vertical push, whip pan) plus `torn-paper-rip`.

### 4b. Buddhism channel (BUD): calm, gold/ivory
**Primary base: `biennale-yellow` structure, recolored**, with `editorial-forest` / `cartesian` as calm alternates.

- **Why biennale-yellow:**
  - Warm parchment ground on every frame; never white, never gray.
  - A single ink for all type and rules, and one sun bloom per frame as the depth layer, plus an optional subordinate ember counter-bloom.
  - 55–60% empty frames ("sparse reads as elegant"). 1 px hairline rules only, no shadows.
  - Treatments that map to sutra content: "Manifesto / Quote" (centered italic serif under a centered bloom), "Chapter Divider" (jumbo numeral + rotated vertical rail, which also suits vertical Hán-Nôm rails), "Ledger", "Strand List" (numbered editorial rows: the elegant replacement for our list rows).
  - 9:16 is documented: Poster Panel becomes a "top/bottom panel band"; numerals centered.
- **Recolor.** Swap the solar yellow `#F1EE2E` for saffron/temple gold:
  - `golden-hour` palette `#8b6914 #d4a017 #fff8dc`, or `warm-editorial` `#E09F3E` / `#FFF3B0`.
  - Ink: keep deep indigo `#1B2566` (calm, scholarly) or use a warm brown-black `#432818`.
  - Ember counter-bloom: robe maroon `#9E2A2B` / `#6F1D1B` at 15–22%, never as text.
  - Paper: `#E9E5DB` (preset) or `#F3EDDF`, which matches the engraving palette paper `#f3eddf`.
- **Fonts:** Instrument Serif lacks Vietnamese, so use EB Garamond or Lora italic for display (Lora is already in the repo) with Be Vietnam Pro body.
- **Alternates:**
  - `cartesian` (warm stone `#EDE8E0`, Playfair, museum-catalog quiet). Its signature "geo-ring" compass decoration *is a ring*, so skip that component.
  - `editorial-forest` (green/cream literary triad) for nature/meditation topics.
- **Visual-style reference:** "Velvet Standard" motion (calm, `sine.inOut`, entrance 1.2 s, hold 3 s, "nothing snaps — everything glides") and "Soft Signal" (warm, intimate, humanist serif).
- **Media treatment:** Film Memory (`vintage-wash` 0.6) for Jataka/past stories, and Engraved Illustration / Monochrome Screen Print with an ink-paper or golden-hour palette for statues and temples. The woodblock-print feel fits the parchment system.
- **Transitions:** blur crossfade, focus pull, `organic-light-leak-overlay`, cross-warp-morph.

### Not recommended for these channels
- blockframe, capsule, daisy-days, creative-mode: neobrutalist or kawaii.
- cobalt-grid, blue-professional: cobalt corporate.
- code-editorial: developer.
- broadside: protest poster. It is usable for FS "warning" lines, but its fire-orange on black is aggressive.

---

## 5. Registry blocks/components relevant to these shorts

### How to discover and add (verified against CLI 0.8.75)
```bash
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"   # HF 0.8.75 needs Node >= 22; repo default is Node 20
cd "/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/hyperframes_short"
npx hyperframes@0.8.75 catalog --query "<what the beat should do, IN ENGLISH>" --json   # local ranked search, installs nothing
npx hyperframes@0.8.75 catalog --type component --tag captions --json                  # browse/filter
npx hyperframes@0.8.75 add <name> --dir . --no-clipboard --json                        # install (writes files; do on a branch)
```
- Always query in English. A non-Latin or Vietnamese query can return "No searchable words".
- Blocks install to `compositions/<name>.html` and components to `compositions/components/<name>.html`. These paths come from the repo's `hyperframes.json`.
- **Block wiring:** `<div data-composition-id="<id>" data-composition-src="compositions/<name>.html" data-start data-duration data-track-index data-width data-height>`. The block's own timeline is auto-seeked; do not reference it from the host timeline (`references/wiring-blocks.md`).
- **Components:** paste HTML + style + script into the host and add their GSAP hooks (`wiring-components.md`).
- The live catalog has 447 items (210 blocks, 237 components).

**Caveats:**
1. Almost all blocks are authored at 1920×1080. In 9:16 they must be re-laid-out, or wired at `data-width=1080 data-height=1920` and checked. Components have no fixed dimensions and adapt more easily.
2. The registry serves `main` HEAD while the repo pins 0.8.75 (latest is 0.8.155). Run `check` and a draft render on every installed item.
3. WebGPU shader backgrounds (aurora, godrays, sun-burst, marble…) and Liquid Glass need WebGPU. Liquid Glass explicitly requires Brave/Chrome canary via `PRODUCER_HEADLESS_SHELL_PATH`. Test before relying on them.
4. `grain-overlay` animates with CSS keyframes, which violates the seek-safe "no CSS @keyframes for motion" rule (`motion-language.md` Part 3). Prefer media-treatment `details.grain` on photos, or `grain-field` (GSAP loop).

### Relevant items by category

**Camera / depth / layout:**
- `pan-stations`
- `scroll-camera-story`
- `pull-back-reveal`
- `push-in`
- `ui-focus-zoom` (zoom/pan to an anchored region)
- `focus-rack`
- `camera-rig-depth-stack`
- `keyframe-scrub-stack`
- `parallax-zoom` / `parallax-unzoom`
- `zoom-through-transition`
- `camera-dolly-zoom` (block)
- `rack-focus` (block, WebGL bokeh)
- `camera-shake` (use sparingly)
- `exploded-stack` (block; isometric layers, good for "ngũ hành layers")

**Images / media framing:**
- `mk-placeholder-grid` (block)
- `hw-frame` (block)
- `freeze-frame-dressing` (block)
- `cinemagraph` (block)
- `svg-mask-reveal`
- `texture-mask-text`
- `particle-image-reveal`
- `grade-split-reveal`
- `comparison-split` (component; before/after divider)
- `yt-vertical-fill` (block; portrait media fills)
- Carousels: `carousel-path-*`, `carousel-vision-*`, `carousel-orbit-*`. These are 16:9 and circle-ish, so use with care.

**Data / charts / numbers:**
- `chart-story`
- `conic-progress-ring`
- `number-wheel`
- `slot-machine-roll`
- `split-flap-board` (block)
- `star-rating-fill`
- `mk-line-graph` (block)
- `data-chart` (block)
- `bar-chart-race` (block)
- `animated-bar-chart`
- `decline-chart`
- `constellation-hub` (component; nodes + connectors in narration order)
- `hw-pipeline` (block; handwritten flow diagram)
- `flowchart-vertical` (portrait decision tree)

**Maps:**
- `world-map`, `spain-map`, `us-map*`, `nyc-paris-flight` (route), `north-korea-locked-down` (zoom + red scribble circle).
- There is no Vietnam or Asia map block. `world-map` (D3 Natural Earth) is the closest base. For pilgrimage routes (Bodh Gaya, Lumbini) or Vietnamese provinces, adapt `world-map` or `nyc-paris-flight`, or hand-build with SVG and `svg-path-draw`.

**Captions** (the faceless-explainer caption band is the bottom ~17%):
- `caption-editorial-emphasis` (dual-font size contrast on emphasis words)
- `caption-weight-shift`
- `caption-pill-karaoke`
- `caption-highlight` (TikTok red sweep)
- `caption-clip-wipe`
- `caption-texture`
- `caption-parallax-layers`
- `caption-camera-follow` (one sentence across a huge world, with a steady camera pull-back; very strong for a hook)
- `mk-callout-highlight` (word-by-word emphasis driven by one scalar synced to VO)
- Check each for Vietnamese diacritic clipping (line-height, `paint-order` strokes).

**Kinetic type:**
- `kinetic-type-swap`, `kinetic-center-build`, `line-swap`, `per-word-rise`, `headline-slam`, `char-slam-explode`
- `ticker-takeover`, `variable-axis-type`, `weight-wave` (block), `text-shimmer`, `focus-blur-resolve`, `tracking-in`
- `mk-emphasis-type` (oversized ghost word as texture: a far better background than a thin ring)

**Annotation / hand-drawn:**
- `vox-annotate`, `marker-highlight`, `cursor-annotate`
- `hw-callout-circle`, `hw-arrow`, `hw-underline`, `hw-box-label`
- `hw-title`, `hw-write-title` (glyph write-on; check Vietnamese support of Caveat), `hw-path-text`
- `whiteboard-ink`, `svg-stroke-trace`, `marker-checklist-card` (paper card with drawn checks; replaces numbered rows)

**Transitions/seams:** see the table in §3.2.

**Backgrounds / atmosphere** (replacing the dark gradient + ring):
- `mk-background` (procedural soft-blob gradient; recolor warm)
- `halftone-field` (WebGL)
- `grain-field`
- `aurora-drift` (re-tint gold for BUD dawn)
- `starfield` / `snow` (seek-safe overlays; starfield for night or Rằm themes)
- `sun-burst` (block; cream/black rays, Tết sunburst feel; WebGPU)
- `godrays` (WebGPU)
- `yt-lcd-background` (textured paper board)
- `canopy-part-title` (block; leaves part to reveal the headline, which suits a hoa mai/đào branch reveal)
- `glass-hero` / `extruded-logo` (gold bevel letters for a channel sting)

**Treatment overlays:** `organic-light-leak-overlay`, `editorial-flash-overlay`, `freeze-frame-dressing`, `camcorder-hud`.

---

## Quick source index
- faceless-explainer: `SKILL.md` (Step 4 + catalog-first rule), `references/visual-design.md` (shot sequence, layout vocab, portrait, caption band), `references/motion-language.md` (vocab + doctrine + seek-safe core), `references/cut-catalog.md` (seams), `references/story-design.md` (transition_in vocabulary + 2–3 types rule), `scripts/lib/transitions.json` (durations), `sub-agents/frame-worker.md` (roles, no stock filler).
- hyperframes-creative: `references/video-composition.md`, `composition-patterns.md` (text-behind-subject), `visual-styles.md` (8 named styles), `design-spec.md` (preset table), `data-in-motion.md`, `storyboard-recipe.md`, `house-style.md`, `motion-principles.md` (Image Motion Treatment, transform-overlap rule), `palettes/*.md`, `frame-presets/{bold-poster,coral,biennale-yellow,cartesian,editorial-forest}/FRAME.md`.
- hyperframes-animation: `blueprints-index.md`; blueprints `spatial-pan-stations`, `camera-journey`, `zoom-out-workspace-reveal`, `comparison-split`, `grid-card-assemble`, `constellation-hub`, `video-text-pivot`, `overwhelm-surround`; rules `multi-phase-camera`, `coordinate-target-zoom`, `viewport-change`, `card-morph-anchor`, `split-tilt-cards`, `3d-page-scroll`, `reactive-displacement`, `depth-of-field-blur`; `techniques.md` §12; `transitions/overview.md`, `transitions/catalog.md`.
- media-use: `references/media-treatments.md`, `media-treatment-recipes.md`, `grading.md`.
- hyperframes-core: `references/full-screen-motion.md` (shared untimed `#bg` layer + transparent timed scenes; drive grain/vignette/hue once on the shared layer), `composition-patterns.md`, `creator-editing-recipes.md` § Pan / Ken Burns.
- hyperframes-keyframes: `SKILL.md` (Ken Burns, split-screen handoff, crop/mask reframe).
- hyperframes-registry: `SKILL.md`, `references/discovery.md`, `wiring-blocks.md`, `templates.md`. Live CLI listing is in `catalog.json` next to this file.
