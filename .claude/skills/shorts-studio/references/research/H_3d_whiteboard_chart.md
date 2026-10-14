# HyperFrames: 3D, whiteboard, chart and stat techniques for BUD/FS Shorts

Research date: 2026-10-14. Read-only; no repo files changed, nothing installed.
Target: 1080x1920 narrated shorts (25-35 s), one paused GSAP timeline at `window.__timelines["main"]`, rendered sequentially on Apple Silicon (~1 min per 30 s today).

Sources read: `~/.claude/skills/hyperframes-animation/{adapters/three,typegpu,html-in-canvas-patterns,lottie,gsap-transforms-and-perf}.md`, rules `svg-path-draw, 3d-text-depth-layers, 3d-page-scroll, particle-burst, counting-dynamic-scale, multi-phase-camera, sine-wave-loop, reactive-displacement, stat-bars-and-fills, chart-scrub-readout, orbit-3d-entry, svg-icon-enrichment, hacker-flip-3d, 3d-camera-flight (constraints)`, blueprints `dataviz-countup, constellation-hub, camera-journey, logo-assemble-lockup`, `techniques.md`, `hyperframes-keyframes/{SKILL.md,references/keyframe-patterns.md}`, `hyperframes-creative/references/{data-in-motion,audio-reactive}.md`, `motion-graphics/{catalog-map.md,categories/{charts,stat,maps,asset-fusion}/module.md}`, `hyperframes-core/references/determinism-rules.md`, `hyperframes-registry/{SKILL.md,references/discovery.md}`.
I ran these live registry searches: `npx hyperframes@0.8.75 catalog --query ... --json`, under Node 22 via nvm, because the default Node 20 is rejected. 447 items. I also fetched the source of `whiteboard-ink`, `hw-boil`, `hw-write-title` and `three-orbiting-cards`, read-only, from the raw GitHub registry.
Existing repo pattern checked: `hyperframes_short/compositions/_rv_bud_khi.html`. It imports Three from `three@0.181.2/+esm`, uses `preserveDrawingBuffer: true`, `setPixelRatio(1)` and `setSize(W,H,false)`, and drives rendering from one `tl.to(st,{t:DUR, ease:"none", onUpdate})`.

---

## 1. Three.js inside HyperFrames: rules, rendering, perf, pitfalls

### Contract (adapters/three.md)
- The `three` adapter does not own the scene. It publishes time and dispatches a seek event: it sets `window.__hfThreeTime` and fires `CustomEvent("hf-seek", {detail:{time}})`. You render the exact frame for that time.
- There are two valid driving styles. Pick one per scene and never mix writers:
  1. **`hf-seek` listener** (doc default): `addEventListener("hf-seek", e => renderAt(e.detail.time)); renderAt(window.__hfThreeTime||0);`
  2. **GSAP proxy** (what our repo already does, and what the keyframes skill shows): `tl.to(state,{progress:1,duration,ease,onUpdate:()=>{/*derive camera/objects from state*/; renderer.render(scene,camera)}})`. Use this when the 3D motion must be eased or choreographed against narration on the main timeline.
- The root **must** have a static `data-duration` on `[data-composition-id]`. The three adapter cannot infer duration (lint: `root_composition_missing_duration_source`). Our shorts already set it on `#root`.
- Render from HyperFrames time only. Do not use `requestAnimationFrame`, `renderer.setAnimationLoop`, `Date.now()`, `performance.now()` or clock deltas. Do not use post-processing that depends on previous-frame history (accumulating trails, temporal AA, feedback buffers) unless it can be rebuilt from `t`.
- Assets (GLB, textures, HDRI) must be local and loaded before seeking. The runtime waits for `THREE.DefaultLoadingManager`. Never fetch at seek time.
- For heavy CPU setup (procedural meshes, shader compiles), register a promise on `window.__hf.buildReady["<unique-key>"] = buildScene()`. Do it synchronously, in the same script that starts the build. Without it, the first frames can be blank.
- Pin output: `renderer.setPixelRatio(1)` and `renderer.setSize(1080,1920,false)`. Camera aspect is `1080/1920`. Keep it independent of DPR.
- Addons such as GLTFLoader, EffectComposer and RenderPass need an importmap with **the same pinned version** for `three` and `three/addons/`. Mixed versions break silently. `examples/js/` is gone; use `examples/jsm/`. Note that the registry's `three-orbiting-cards` uses `three@0.184.0`. Our repo pins `0.181.2`. Do not mix them in one page.
- `AnimationMixer`: call `mixer.setTime(t)` on every render, never `mixer.update(delta)`.
- Seeded RNG only. `mulberry32(seed)` and the `prand(n)=fract(sin(n*127.1+311.7)*43758.5453)` hash both appear in the skills.

### Practical pitfalls for our pipeline
- **The t=0 / pre-tween frame.** A proxy tween's `onUpdate` does not fire for times before the tween starts. Call `render()` once at setup, and start the driver tween at 0 or make it a `fromTo`. The 3d-camera-flight rule says "first leg is a fromTo AND applyCamera() runs once at setup". The same applies to Three cameras.
- **Text on 3D objects.** Do not use `TextGeometry`: it needs typeface JSON, has no Vietnamese diacritic coverage, and is heavy. Instead, draw labels with Canvas 2D in **Be Vietnam Pro** into a `CanvasTexture`, and only **after `document.fonts.ready`**. Draw once and set `texture.needsUpdate = true` once. Do not redraw per frame unless the label changes. Measuring or drawing before the font loads is a known trap in `motion-scene-dev`.
- **Async build vs timeline registration.** If the 3D build awaits fonts or textures, either register all tweens synchronously first and render inside `onUpdate` with a guard (`if (!ready) return`), or assign `window.__timelines["main"] = tl` only at the end of the async callback. Registering an empty timeline early renders blank (lint `gsap_timeline_registered_before_async_build`).
- **`preserveDrawingBuffer: true`** is already in our repo. Keep it so frame capture never reads a cleared buffer.
- **DOM-to-3D mapping.** The repo already maps SVG pixel coordinates to world space at z=0 (`px(x,y)` helper with `VIEW_H = 2*tan(fov/2)*dist`). Reuse it so DOM captions align with 3D anchors.
- **Text legibility.** Angled or moving text is texture. Anything the viewer must read needs a near-flat pose held for at least 1 s (3d-camera-flight).
- **Lighting.** `MeshStandardMaterial` plus Hemisphere and Directional lights is enough. Fake glow with additive sprites or planes, as `_rv_bud_khi` already does, not with UnrealBloom.

### When CSS 3D is better than Three.js
Use CSS 3D (DOM `perspective` + `preserve-3d` + GSAP `rotationX/Y`, `z`) for anything that is basically flat cards: calendar pages, wheel discs with text, tilted tables, coin flips. The text stays crisp, there is no WebGL cost, and the setup is simpler. CSS 3D rules:
- Put `perspective` on one static stage only.
- Use `preserve-3d` on every wrapper.
- Never put `filter`, `opacity<1`, `clip-path`, `mask` or `overflow` other than visible on the 3D world. Each of these flattens `translateZ`.
- Transform order is `translate3d` then `rotateX` then `rotateY`.

Reserve Three.js for real lighting and shading, many objects (instancing or points), and shader backgrounds.

### Other runtimes (short verdicts)
- **TypeGPU / WebGPU.** Not needed. Plain TypeGPU works in headless-shell. Liquid-glass blocks need Brave or Chrome Canary via `PRODUCER_HEADLESS_SHELL_PATH`, so skip them. The registry's WebGPU "Shaders library" blocks (`ripples`, `sun-burst`, `spiral`, `hologram`, `marble`...) are full-frame GPU shaders. Use at most one as a background, and benchmark it first.
- **html-in-canvas** (`<canvas layoutsubtree>` + `drawElementImage` into a Three texture). Very powerful: you can put any DOM card on a 3D rotating plane, sphere, cylinder or torus, with bloom, shatter or portal effects. It is also the most expensive option, because it captures plus uploads a texture every frame. The doc itself says "1-3 hero beats per video". For a 25-35 s short, use one beat or none. The renderer auto-enables the flag, but preview needs a fallback.
- **Lottie.** Possible for licensed decorative loops such as incense smoke, a lotus bloom or a candle flame. Rules:
  - Use local JSON with `autoplay:false` and an explicit `loop`, and push the player onto `window.__hfLottie`.
  - Every registered Lottie plays against **composition time, with no per-animation start offset**. A Lottie meant to start at 12 s must have that offset baked into the file, or live inside a sub-composition.
  - Never use remote `path`.

---

## 2. Whiteboard / path-draw technique

### Core mechanic (rules/svg-path-draw.md)
- `len = path.getTotalLength()` is measured, never guessed. Set `strokeDasharray = len` and `strokeDashoffset = len`, which hides the stroke. Tween `strokeDashoffset → 0`.
- It works on `path`, `circle`, `rect`, `line`, `polyline`, `polygon` and `ellipse`. `circle` and `rect` start at 3 o'clock, so rotate -90deg to start at 12.
- Use `fill:none` for outline draws. For **draw-then-fill**, start with `fill-opacity:0`, then tween `fillOpacity:1` after the stroke ends. This is ideal for closed silhouettes such as a lotus, a stupa or a zodiac animal.
- **Eases.** Use `power2.out` for a hand lifting at the end of a stroke, or `"none"` / `power1.inOut` for a constant pen. Never use `back` or `elastic`, because pens do not bounce.
- **Timing.** One segment takes 0.3-0.8 s. Start the next segment when the previous one is 70-80% done. A companion label fades in at least 0.2 s after the last stroke settles.
- If the length reads wrong on complex paths, overestimate with `len*1.05`.
- **Rule: a drawn line must land on something.** Connectors join two real elements. Do not add decorative strokes over empty space.
- The keyframes skill prefers GSAP `DrawSVGPlugin` (free in GSAP 3.13+, `gsap@3.14.2/dist/DrawSVGPlugin.min.js`). It supports `drawSVG:"0% 0%" → "0% 100%"` and moving-segment draws such as `"40% 60%"` for a comet. The dash fallback is identical in output.
- **Gotchas found in the skills:**
  - `getTotalLength()` can return 0 before layout or font load. That disables the dash, so a solid line shows at t=0. Gate every draw-on element with `autoAlpha:0` until its draw starts (or `gsap.set` the hidden state at build time), and fall back with `getTotalLength() || CONST` (asset-fusion module).
  - A bare `fromTo` does not apply its "from" state until the tween starts, so `gsap.set` hidden states at build time (maps module).
  - Use the SVG `transform` attribute, not CSS `transform-origin` + `transform-box`, to rotate small inner parts around a point (svg-icon-enrichment).
  - Use a user-space `stroke-width`. Never put `vector-effect: non-scaling-stroke` on dashed draw paths: the dash is in screen space and breaks under group scale (whiteboard-ink comment).

### Pen nib / hand cursor (registry `whiteboard-ink`, source read)
How it works:
- Each stroke owns one `{progress}` proxy. A **single `onUpdate`** sets `strokeDashoffset = (1-p)*len` and places the pen at `path.getPointAtLength(p*len)`.
- The point is mapped through the group's consolidated transform matrix: `activeGroup.transform.baseVal.consolidate().matrix` → `point.matrixTransform(matrix)`.
- Rotation is the tangent `atan2` between points at ±0.4% of the length.
- Between strokes, the pen **hops**: a 0.1 s lerp between the end pose and the next start pose, with an arc lift of `-sin(πp)*18` in y and an extra `-sin(πp)*8` on the nib art.
- Each stroke's duration is `MIN_DRAW (0.26 s) + LENGTH_BUDGET * len / totalLen`, so draw speed is proportional to length and the pen speed stays constant. If too many strokes would overflow the phase, the floors shrink together.
- At the end, the pen fades out and lifts while the caption fades in.
- It has a strokes slot: drop your own `<path>`s into `<g data-slot="strokes">` (viewBox 1000x560). `data-ink="accent"` gives a highlight stroke.

For 9:16, copy the logic into our own scene with a taller viewBox, for example `0 0 1000 1400`. Do not mount the block, because its canvas is 1920-based.

### Hand-drawn feel (registry `hw-*` family, `hw-boil` source read)
- **Boil.** The jitter re-poses only every N frames: `step = floor(tl.time()*fps/frameDrop)`. Then `x,y = hash(step*3+k+i*97, seed)*amp` and `rot = hash(...)*rot`. Classic values are `frameDrop` 3-4, calm `amp 1.6 / rot 0.5`, lively `2.6 / 0.9`. This is pure, seek-safe and cheap. **No `feTurbulence`.** The boil owns x/y/rotation of its target, so entrance tweens go on a wrapper.
- **One timeline has ONE `onUpdate`.** `hwOnUpdate(tl, fn)` is a dispatcher that lets several per-frame renderers coexist. This matters if we add boil plus a Three render plus counters to one timeline. GSAP `eventCallback("onUpdate")` replaces any previous callback.
- **`hwPenEase`.** A curvature-adaptive pen-velocity ease: fast on straights, slow into curves. It samples the path at 48 points, computes per-segment curvature and builds a custom ease. Use it for pen realism on long strokes.
- **Stroke matrix.** `plain / soft / sharp / spray`. Spray is index-seeded deterministic dots. Textured strokes live in their own SVG inside the boiled wrapper.
- **Wobbled shapes.** `hw-box-label`, `hw-arrow` (straight, gentle or swoop, with a head-arrival stretch pulse), `hw-callout-circle` (a wobbled ellipse around a target, plus a scribble fill, a connector and a label), `hw-underline`, `marker-highlight` (a highlight, circle, underline or scribble over one word on cue), `hw-pipeline` (wobbled boxes plus curved connectors from a node list) and `hw-scribble-transition`.

### Timing to narration
- We already have word timestamps (`wordts`). Schedule each stroke's start at its keyword's `t_start`, and make the stroke duration fit within that word or clause, typically 0.4-0.9 s. A whole sketch should finish **at or before the end of the clause that names it**. Then hold, with the boil running, while the narration explains.
- Pattern: **noun spoken → its shape draws. Relation spoken ("sinh", "khắc", "hợp") → the connector draws between two already-drawn nodes.** This follows the "line must land on something" rule.
- Leave at least 0.8-1 s of static hold for reading after the last stroke of a beat. Do not start a new sketch while the viewer still reads the previous one.
- Use `ease:"none"` or `hwPenEase` for "real pen" beats, and `power2.out` for punchy diagram connectors.

### Drawing Vietnamese text and symbols
- **Registry handwriting assets are Latin-only.** `hw-write-title`, `hw-boil` and `hw-path-text` ship `Caveat-700-latin.woff2`. `hw-write-title`'s true glyph write-on uses a **baked per-glyph centerline table** (`assets/baked/caveat-pen.js`). Characters missing from that table fall back to a plain fade. Vietnamese letters with diacritics (ắ, ộ, ữ, đ...) are not in the table or the font subset. **Do not use these blocks for Vietnamese copy as shipped.**
- Workable options, from cheapest to richest:
  1. **Brush-wipe write-on (any font, including diacritics).**
     - Render the word in a Vietnamese-capable font, e.g. Be Vietnam Pro, or a handwriting face with a `vietnamese` subset such as Patrick Hand, Pangolin, Itim, Mali or Dancing Script. Verify the subset on Google Fonts and bundle the woff2 locally.
     - Reveal it with `clip-path: inset(0 X% 0 0)` (or an SVG mask rect) sweeping left to right, with the pen nib riding the wipe edge (`x` derived from the same proxy).
     - Optionally per line, staggered.
     - This covers 95% of "handwritten caption" needs.
  2. **Outline draw-then-fill.**
     - Convert the text to SVG paths **offline**. Python `fontTools` or Node `opentype.js` can emit `<path d>` per glyph from the bundled TTF, in a build step in `hyperframes_bridge.py`. Diacritics come out as separate contours.
     - Draw each glyph outline with dashoffset (base letter first, then the diacritic contour, because Vietnamese is written that way), then fade the fill in.
     - Good for 1-3 big hero words such as "TAM HỢP" or "NGHIỆP". Avoid it for long lines: there are too many contours, and outline-tracing reads as "tracing", not writing.
  3. **Mask-reveal with centerlines** (the hw-write-title approach): a fat stroke inside a `<mask>`, following each glyph's centerline in stroke order, over the filled glyph. This is the truest look, but needs centerline data per glyph. There is no Vietnamese dataset, so it is not worth building for shorts.
- **Hán characters** (甲子, 八卦 trigram names, 卍 should be avoided because it is easily misread). Stroke-order SVG data exists (Make Me a Hanzi / Hanzi Writer data, which carries the Arphic Public License, so check the license and attribute). Each stroke is a median polyline plus an outline, which is exactly the mask-reveal model. A nice touch for can chi beats, but optional.
- **Symbols** (trigrams ☰☷, the yin-yang, a lotus, the dharma wheel, zodiac animals): hand-author or vectorize to SVG paths. Potrace can vectorize licensed line art; keep the paths simplified, under about 40 per sketch. Trigram bars are just `<line>`s and are trivial to draw stroke by stroke.
- **Always label with the chi names Tý, Sửu, Dần... Hợi** (FS rule). Never use "tuổi Lợn/Dê".

---

## 3. Chart, stat and data-viz guidance

### Doctrine (data-in-motion, charts, stat modules)
- One chart, one message. Every number needs a **paired graphic** (bar, ring, fill or shape) so it has visual weight.
- Visual continuity: successive stats about one concept stay in the same space. Only the value changes.
- **Avoid web patterns:** no pie charts, no multi-axis charts, no 6-panel dashboards, **no gridlines, tick marks or legends**, and no chart-library output. Build with GSAP plus SVG or CSS. D3 or visx is fine for data-to-geometry math only.
- Use one accent hue; everything else stays muted.

### Count-up (rules/counting-dynamic-scale.md, stat module)
- Use a proxy tween `{v:0}→target`, with `onUpdate` writing only `textContent = Math.round(v).toLocaleString("vi-VN")`.
- Run a parallel `scale: START/END → 1` with the **same start, duration and ease**. Never tween `fontSize`.
- Use `font-variant-numeric: tabular-nums` (mandatory) and a fixed-width container.
- Duration is 1.2-2.5 s, with ease `power3.out` / `expo.out`. **No `back` or `elastic` on the number**, because data must not bounce.
- The suffix ("năm", "%", "+") slides in after the count lands. The label arrives before the peak, as big text, not a caption.
- Use `Math.round`, not `floor`. The `snap:{innerText:1}` shortcut is fine for plain integers.
- **Years.** Do not count up from 0 to 1990. That reads absurd. Count over a short span, or use a `number-wheel` odometer roll or a split-flap.

### Bars, fills, rings (rules/stat-bars-and-fills.md)
- **Bars:**
  - Set each bar's final height in CSS and tween `scaleY: 0→1` with `transform-origin: bottom`.
  - Use 4-6 bars, a 0.06-0.1 s stagger, and accent the last or current bar.
  - In 9:16, horizontal bars (`scaleX`, origin left) usually read better, because labels fit on the left.
- **Progress fill:** `scaleX` on a `.fill` with **`width:100%`**. A zero-width fill is invisible and gates may miss it.
- **Ring:** `circle` rotated -90deg, with dashoffset to `LEN*(1-pct)`, measured via `getTotalLength`.
- Star or fractional fill: `clip-path: inset()` wipe.
- Fill and count share the same start and ease, so they land as one beat.
- **Never tween `height`, `width`, `top`, `left`, `letterSpacing` or `fontSize`.** These are layout properties, which snap to pixels and visibly stutter in slow tails (gsap-transforms-and-perf). Lint: `gsap_non_transform_motion`.

### Line or timeline charts (svg-path-draw + chart-scrub-readout)
- Bake a `DATA` literal. Compute `points` once via pure `X(i)`, `Y(v)` functions.
- The line draws left to right with dashoffset. Optionally a scrub head (one driver `p`) moves the tracking line and marker, and updates the tooltip text **only when the index changes**.
- Hold the landed value for at least 0.8 s. For a "line breaks above the band" climax, use the peak-stop variant (`power3.out` plus a dot pop).

### Cycle diagrams and hubs
- `orbit-3d-entry`: items flip in **in place** at their orbital position (`gsap.set` x/y on the ellipse first), then orbit via their own progress tween each. The z-index band is [1..50], and the center label uses `translateZ(220px)`. `Y/X ratio 0.4-0.7` gives a tilted ring.
- `constellation-hub`: nodes spring-pop around a center, connectors draw hub to node, then a push-in with depth-of-field on the core.
- `radial-surround` (registry component): labeled chips assemble on an elliptical ring around a fixed center.
- `multi-phase-camera`: one camera wrapper, with phase scale plus sine drift composed in a single writer. `overflow:hidden` and the background go on `.scene`.

### Particles and punctuation (rules/particle-burst.md)
- Use a fixed DOM pool of at most about 40 particles, with seeded `prand(i)`. Position is a pure ballistic function of the driver `T` (`ease:"none"`).
- Particles start and end at opacity 0, and are fired by a cause (a number landing, a stamp).
- For thousands of particles, use Three `Points` (as in `_rv_bud_khi`) or the `particle-text-dissolve` component (canvas, one painter).

### Audio-reactive (optional)
- Pre-extract bands with the skill script `extract-audio-data.py`, then map them to scale or glow. **Never** use spectrum bars or waveform clichés.
- The doc samples with `tl.call` per frame. However, the maps module warns that `tl.call` stateful updates can freeze under seek. Prefer one long proxy tween whose `onUpdate` reads `AUDIO_DATA.frames[floor(t*fps)]`. That is a pure function of time.

### Registry blocks and components relevant to us (live catalog, v0.8.75)
Install: `npx hyperframes add <name>` from `hyperframes_short/`, with Node 22 (`nvm use 22`, as `hyperframes_bridge.py` does). Blocks land in `compositions/<name>.html`. Most are **1920x1080** with data baked in the script. For 9:16, treat them as reference source to copy logic from, not as drop-in sub-compositions. Components are snippets to paste.

| Need | Item (type) | Notes |
|---|---|---|
| Bar + line chart | `data-chart` (block 1920x1080, 15 s) | NYT style, staggered bars, value labels; edit the data array in place |
| Story chart (bars, line+area, **donut**, progress) | `chart-story` (component) | Lands exact values with an accented callout; covers the donut gap noted in the charts module |
| Bar race | `bar-chart-race` (block) | Time-series ranking; probably too busy for a short |
| Compact bar card | `animated-bar-chart` (component) | Deterministic growth plus callouts |
| Line draw + dots | `mk-line-graph` (block) | 1-2 series draw on, labels ride the draw front |
| Big stat + progress | `mk-progress-stat` (block) | Count-up, label, track fill, caption; light and dark |
| Counter | `count-up` (component), `number-wheel` (component, odometer roll), `number-pop-in` | `count-up` also counts **down** (countdowns) |
| Ring / gauge | `conic-progress-ring`, `mk-usage-arc` (components) | Ring plus center count from one percentage |
| Finance counter | `apple-money-count` (block) | $-styled with SFX; not a fit |
| Whiteboard pen sketch | `whiteboard-ink` (component) | Measured strokes, pen nib, hop; custom strokes slot |
| Hand-drawn kit | `hw-boil`, `hw-arrow`, `hw-box-label`, `hw-callout-circle`, `hw-underline`, `marker-highlight`, `marker-checklist-card` (components); `hw-pipeline`, `hw-title`, `hw-write-title`, `hw-path-text`, `hw-text-cloud`, `hw-frame`, `hw-scribble-transition` (blocks) | Caveat **Latin-only** font: use our own Vietnamese font for any copy |
| SVG stroke | `svg-stroke-trace`, `svg-line-draw-loader` (components) | Simple draw plus optional fill |
| Path travel | `offset-path-traveler`, `arc-motion-path` (components) | Follower with tangent rotation (e.g., a boat on a river) |
| Ink reveal | `ink-bleed-reveal` (component) | Gooey ink bloom resolving into a mark; fits inkwash styles |
| Split-flap | `split-flap-board` (block, 3.5 s) | Mechanical text resolve; fixed alphabet, so **digits for years are safe**, diacritics are not |
| Annotation on a photo | `north-korea-locked-down` (block), `yt-circle-pointer`, `hw-callout-circle` | Scribble circle plus pop-up label (asset-fusion kit) |
| Radial ring | `radial-surround` (component) | Chips on an ellipse around a center |
| Three.js primitives | `three-orbiting-cards` (component; three@0.184.0), `extruded-logo` (block: beveled 3D letters flip up, chrome or gold), `product-turntable` (GLB on a plinth), `code-3d-extrude`, `cuboid-carousel`, `exploded-stack`, `glass-hero`, `cosmic-orb`, `spiral-galaxy`, `starfield` | `extruded-logo`: check font coverage before using Vietnamese words |
| 3D card rings | `carousel-circle-1..5`, `carousel-orbit-1..5` (blocks, 12-24 image slots) | Image cards on a circle or sphere; could host 12 zodiac images |
| 3D transitions reference | `transitions-3d` (block gallery) | Perspective flip and rotate reference |
| Maps | `world-map` (rotating globe inset), plus the basemap bake pipeline in the maps module | For pilgrimage-site beats (Bodh Gaya, Lumbini) |
| Confetti / particles | `confetti`, `particle-text-dissolve`, `particle-image-reveal` (components) | Seeded, deterministic |

These searches found nothing: "zodiac" (empty), "compass dial", "calendar page flip", "book page turn". **The zodiac wheel, la bàn, lunar calendar flip and ngũ hành cycle must be hand-authored.** Per the registry skill, file a gap report: `npx hyperframes feedback --search-miss "<query>" --wanted "<move>" --tier words`. That command sends the query, so run it only if the user agrees.

---

## 4. Device ideas for BUD/FS (implementation sketches)

Short v2 beat map, for reference: **Hook (0-3 s) → twist line (câu 2) → body/explain → insight → CTA/payoff (21-27 s total)**.

### D1. 3D zodiac wheel that turns to the viewer's sign (FS)
- **Beat:** hook or address ("Nếu bạn tuổi Dần..."), where the wheel spins and lands on Dần within the first 2.5 s. It can recur at the insight beat to draw tam hợp lines (see D7).
- **Build (CSS 3D first):**
  - The stage has `perspective:1600px`. The disc is a `div` with `preserve-3d`, `rotationX: 58` (static tilt via `gsap.set`) and 12 sectors as conic-gradient wedges plus absolutely positioned labels (Tý...Hợi in Be Vietnam Pro, with the chi glyph or animal icon). Per sector: `rotate(i*30deg) translateY(-R)`.
  - A spin proxy `{a}` uses `tl.fromTo(spin,{a:0},{a: -(720 + idx*30), duration:2.2, ease:"power4.out"})`. Its `onUpdate` sets the disc `rotationZ`, and counter-rotates each label so it stays upright.
  - When it lands: the selected wedge lifts (`z:+40`, accent fill, a short spring on the **label only**), a ring draws around it (svg-path-draw), and the rest dims to 40%.
- **Three.js version** (if we want lit gold or lacquer):
  - `CylinderGeometry(R, R, 0.15, 96)` plus 12 `RingGeometry(thetaStart, thetaLength)` sector meshes with `MeshStandardMaterial({metalness:.6, roughness:.35})`, and labels on one `CanvasTexture` (2048², drawn after `fonts.ready`).
  - Camera at (0, -6, 9) looking at the origin. A GSAP proxy `{angle, lift}` drives `disc.rotation.z` and `sector[idx].position.z`.
  - Glow via an additive plane, not bloom.

### D2. Ngũ hành cycle draws itself (FS, whiteboard)
- **Beat:** body/explain ("Mộc sinh Hỏa, Hỏa sinh Thổ..."), one arrow per clause. The khắc star comes at the twist ("nhưng Thủy lại khắc Hỏa").
- **Build:**
  - Use an SVG viewBox `0 0 1000 1000` with 5 nodes on a pentagon (−90° start). The nodes are colored circles: Mộc green, Hỏa red, Thổ ochre, Kim white/gold, Thủy blue/black.
  - Arrows are curved `path`s between node rims, along the outer arc. The arrow head is a separate short path that draws after the shaft.
  - Each arrow's `strokeDashoffset→0` is timed to that clause's `wordts`, with a `whiteboard-ink`-style nib riding the tip. The target node pops (scale 0.6→1 on the **wrapper**) when the arrow lands. Apply `hw-boil` calm to the finished diagram during the hold.
  - The khắc cycle is an inner pentagram in a dashed red stroke. Draw dashed lines with a mask: draw a solid stroke in a `<mask>` over the dashed path, because dasharray is already used by the dash pattern.
  - Use the chi-agnostic element names in Vietnamese with full diacritics, from a bundled font (not Caveat).

### D3. Birth-year reveal: split-flap / odometer plus year table (FS)
- **Beat:** hook or address ("Sinh năm 1986, 1998, 2010...") or the payoff list.
- **Build:**
  - A **split-flap** of 4-digit years in its own 9:16 scene: copy the `split-flap-board` drum logic, where each cell walks through `0-9` to its target and the stagger runs left to right.
  - Alternatively, use a `number-wheel` odometer roll.
  - Then the existing `review_yeartable` layout: rows slide in staggered (waterfall-entry), the viewer's row gets a `marker-highlight` swipe, and other rows dim.
- Years come from Python and are baked into the HTML. **Never compute them from `Date` in the browser.**

### D4. Lục thập hoa giáp ring: the 60-year can chi cycle (FS)
- **Beat:** insight ("cứ 60 năm mới lặp lại một lần").
- **Build:**
  - An SVG ring of 60 ticks. A progress ring draws clockwise (ring-fill), while a count-up shows 0→60 with `tabular-nums` and the "năm" suffix after landing.
  - Then the viewer's year tick and its twin (+60) light up, and an arc connector draws between them.
  - Optional: a 10-segment inner ring (Thiên can) and a 12-segment outer ring (Địa chi) counter-rotate (two proxies with `ease:"none"`) to show how the can and chi combine. Lock them to the year's pair with `power3.out`.

### D5. Lunar calendar tear-off flip to a key date (FS: Tết, rằm, hoàng đạo)
- **Beat:** date reveal ("Mùng 1 Tết năm 2027 rơi vào...") or the twist.
- **Build (CSS 3D):**
  - A tear-off calendar block (lịch bloc): a stack of 6-8 page `div`s, each showing the big solar date plus the small lunar date and can chi. All use `transform-origin: top center` on a `perspective:1400px` stage.
  - Each page flips `rotationX: 0 → -110` (and fades as it passes the edge), staggered with accelerating timing (0.35 s, 0.28, 0.22... for the "days passing" feel). The ease is `power2.in` per page.
  - The final page stays. Its date number counts or stamps in, then a red "seal" stamp (scale 1.4→1 plus a particle micro-burst of at most 12 dots) marks Tết or hoàng đạo.
  - Back faces use `backface-visibility:hidden` plus a second face rotated 180°.
- **Caveat** from memory: hoàng đạo dates expire, so build the date from data at render time in Python.

### D6. La bàn / bát quái compass 3D lock-on (FS)
- **Beat:** direction advice ("hướng tốt nhất cho tuổi Ngọ là...").
- **Build:**
  - Three or four concentric rings: 8 trigrams with drawn bars, 24 sơn labels, degree ticks, and the center taiji.
  - **CSS 3D:** the stage has a `rotationX:50` tilt. Each ring has its own proxy angle. They counter-rotate at different rates (`ease:"none"`), then each decelerates (`power3.out`) and **locks** in sequence from the outside in.
  - The needle settles with a deterministic damped spring computed in `onUpdate`: `θ(t)=θ₀·e^{−ζωt}·cos(ωt)`, a pure function of the driver, so it is seek-safe.
  - The chosen direction wedge highlights and a label slides out.
  - Three.js alternative: a lacquer or bronze disc with relief rings (`LatheGeometry`), with labels on a CanvasTexture.
- Trigram bars can also draw on (whiteboard) the first time they appear.

### D7. Tam hợp / tứ hành xung lines on the zodiac wheel (FS)
- **Beat:** insight or twist ("Thân - Tý - Thìn là tam hợp, nhưng Dần - Thân - Tỵ - Hợi xung nhau").
- **Build:** reuse D1's wheel, flattened to 2D (tilt to 0 via a camera leg) for reading.
  - An equilateral triangle connecting Thân, Tý and Thìn draws in gold, with its vertices pulsing as each line lands.
  - Then a red square (tứ hành xung) draws with `hw-arrow`-style wobble.
  - Lines connect real node centers, following the "must land on something" rule.

### D8. Jataka story as a live whiteboard (BUD)
- **Beat:** the narrative body. One sketch per story beat, e.g. Sasa Jataka: the hare, the fire, the moon.
- **Build:**
  - Use a paper background (the inkwash palette), with 3-5 sketches of up to 40 paths each, drawn with a pen nib (`whiteboard-ink` logic), `hwPenEase` and `hw-boil` calm during holds.
  - Draw-then-fill: a watercolor fill fades in under the line art after the outline completes.
  - Camera: one `multi-phase-camera` wrapper pans down the "board" between sketches (vertical scroll suits 9:16). Drift is 2-4 px.
- **Source:** hand-authored SVG, or potrace vectorization of licensed or AI-generated line art. Simplify the paths, and order the strokes manually: big contour first, then details, then the accent.
- Captions stay in DOM, not drawn.

### D9. Count-up stat with a symbolic ring (BUD/FS)
- **Beat:** hook number or payoff ("547 kiếp tiền thân", "84.000 pháp môn", "12 con giáp, 5 hành, 60 năm").
- **Build:** use `counting-dynamic-scale` plus `stat-bars-and-fills` ring form, with the same 1.6 s and `power3.out`.
  - The ring is a lotus outline that draws with the count; for FS, a taiji ring.
  - Then a `particle-burst` dot burst behind the number at landing (14 dots, radial, G≈0).
  - Format with `toLocaleString("vi-VN")` to get "84.000".
- Fact-check every number (soát sự thật) before it becomes a hero stat.

### D10. Vertical timeline of the Buddha's life or a lineage (BUD)
- **Beat:** context or history (e.g., "Thái tử Tất Đạt Đa → xuất gia năm 29 tuổi → thành đạo năm 35 tuổi → nhập Niết bàn năm 80").
- **Build:**
  - A vertical spine `line` draws top to bottom, timed to the narration.
  - Dots pop at year nodes (spring on the dot only), and labels slide in from alternating sides.
  - The camera wrapper translates up so the active node stays at y≈40% (viewport-change).
  - Optional: a scrub head (chart-scrub-readout "playhead form") with an age counter in `tabular-nums` that steps per node.

### D11. Iconography annotation on a statue photo (BUD)
- **Beat:** explain ("bàn tay chạm đất là Ấn Xúc Địa...").
- **Build:** use the asset-fusion annotation kit.
  - Ground the hand position with the locate protocol (`motion-graphics/grounding/PROTOCOL.md`). Do not eyeball it.
  - Draw a `hw-callout-circle` wobbled ellipse around the mudra, with a curved connector to a label pill and a light wash outside the target.
  - **No camera push under a fixed overlay.** Scale the whole scene together or not at all.
  - Use even dimensions and gate the draw-on with `autoAlpha:0`.

### D12. Element "proportion" bar for a birth year (FS, use with care)
- **Beat:** a body point such as "mệnh Kim nhưng thiếu Thủy".
- **Build:** 5 horizontal bars in element colors (`scaleX` from the left, 0.08 s stagger), with the viewer's dominant element accented and the others muted. Labels are on the left, values hidden (no ticks or legends).
- Only use this if the numbers come from a defined method we can cite. Otherwise it is fake precision, so prefer D2.

Also usable anywhere: `3d-text-depth-layers` for one hero word per video (4-6 layers, 1-3 px offsets, black weight, at least 200 px). `hacker-flip-3d` is mono-font and decode-styled, and does not suit our register.

---

## 5. Performance and render-time cautions (sequential Apple Silicon renders)

1. **Budget per frame, not per scene.** About 1 min per 30 s means about 900 captured frames at about 65 ms each. Anything that adds 20-30 ms per frame across the whole short adds 30-50% render time. Scope heavy layers to their beat:
   - Make the Three canvas a clip, or toggle `opacity:0` (do not `display:none` a clip).
   - Return early in `onUpdate` when the time is outside the beat window.
   - Check that frames outside the window are still correct, which they will be because the canvas is hidden.
2. **WebGL in headless Chrome.** It may run on SwiftShader (software) rather than the Metal GPU, depending on launch flags. Full-frame fragment shaders at 1080x1920 (2 Mpx) and post-processing are the main cost.
   - Avoid `EffectComposer`/`UnrealBloomPass`, which add several full-resolution passes per frame. Fake glow with additive quads.
   - Keep `antialias` on but `pixelRatio` at 1.
   - Prefer one WebGL canvas per composition.
   - Measure with `npx hyperframes benchmark` (listed in the CLI skill) or by timing a 3 s test render before committing a device to the batch.
3. **Texture uploads.** Do not set `CanvasTexture.needsUpdate = true` every frame for a 2048² label sheet; upload once. html-in-canvas (`drawElementImage` plus a texture upload per frame) is the most expensive pattern: one hero beat at most, and preferably none in shorts.
4. **SVG filters.** `feTurbulence`, `feDisplacementMap` and large `feGaussianBlur` on full-frame layers are costly and re-rasterize every frame. The hw family deliberately uses frame-quantized transform boil and seeded spray dots instead. Prefer `filter: drop-shadow` on small elements only.
5. **Path cost.** `getPointAtLength` per frame is fine for a few active strokes. For long or complex paths, pre-sample about 64-200 points at setup and interpolate. Keep sketches under about 40 paths, and simplify potrace output (it is often 10x more nodes than needed).
6. **DOM particles.** Cap at about 40, with transform and opacity writes only. Use Three `Points` for more.
7. **Layout properties.** No `top/left/width/height/fontSize/letterSpacing` tweens and no `roundProps`. These are correctness bugs (sub-pixel stutter on slow tails), not just perf issues.
8. **Clip-path and mask.** Do not animate a large `clip-path` or mask while the same surface also scales or travels. Nest the reveal after the move settles (keyframes skill).
9. **One `onUpdate` per timeline** if we adopt hw-boil-style dispatchers. `tl.eventCallback("onUpdate")` overwrites. Per-tween `onUpdate`s, as our repo uses, are fine and independent.
10. **Infinite repeats are banned.** Use `repeat: Math.max(0, Math.floor(dur/cycle)-1)`, with `floor`, not `ceil` (lint `gsap_repeat_ceil_overshoot`). Orbit and drift tweens must span the full time on screen, or the objects freeze.
11. **Fonts before measurement.** Any `getTotalLength`, `getBBox`, text measuring or Canvas2D label drawing must wait for `document.fonts.ready`. The skills recommend building inside that callback and registering the timeline at the end. Bundle woff2 locally: the renderer does not auto-resolve web fonts like Caveat, and render-time network is forbidden.
12. **Verification.** Run `npx hyperframes lint` and `npx hyperframes check` after every new device. For WebGL use `keyframes --ghost` and `snapshot --at` at 0, mid and final, because DOM boxes cannot see canvas internals. Snapshot the partial mid-draw frame and the completed frame for every path draw. Our `hf_qa` and showreel flow (motion-scene-dev skill) remains the gate.
