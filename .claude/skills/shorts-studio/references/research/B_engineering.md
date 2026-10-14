# B. Engineering contract for a modular, reusable 9:16 Shorts engine (HyperFrames 0.8.75)

Scope: how to structure a data-driven, multi-channel narrated Shorts engine so it obeys the HyperFrames
composition contract, reuses registry items, keeps one-timeline determinism, and can be gated headlessly.
Sources: `~/.claude/skills/hyperframes-{core,cli,keyframes,studio,registry,animation,audio}` (all references read),
`npx hyperframes@0.8.75 <cmd> --help`, and live `lint` / `check` / `snapshot` / `keyframes` / `timeline` runs
against scratch copies of `_v3_v3_a.html` / `_v3_v3_b.html` (repo files untouched).

---

## 0. TL;DR

1. **The engine is broadly contract-compliant but has one real seek-safety bug, proven with snapshots**:
   `SCN.calendar` does `tl.set(page, {visibility:"hidden"})` on a child of a hidden scene (fs_v3.html:290). After any backward
   seek (e.g. seek 26 s, then seek 2 s), GSAP reverts that set to the recorded inline `visibility:visible`. That inline value
   overrides the inherited `.scene{visibility:hidden}`, so **the "THÁNG 2 · 2026 / 17" calendar page paints over the hook, split,
   window and wheel scenes**. A forward-only render hides it; Studio scrubbing, `check`, out-of-order `snapshot`, or a
   non-monotonic worker seek all show it. `check` reported it as ~200 samples of `content_overlap` against `div.cl-stage > div:nth-of-type(2)`.
2. Lint: **1 error** (`font_family_without_font_face`: Noto Serif SC / Songti SC / STSong in `.st-han`). That error
   **silently disables every browser audit** (check then prints `0 issues across 0 sample(s)`). After patching it in a scratch copy:
   0 runtime errors, but 58 layout errors (the calendar leak plus intentional `#ghost` text), and 7 contrast errors
   (`#foot` 3.02:1, `#ghost` 1.09:1, dimmed caption words 1.83:1).
3. **Architecture recommendation: a hybrid.** Keep **one host composition per video with one paused GSAP timeline** (needed for
   cross-scene "cut-the-curve" seams, the caption driver and the shared background), but (a) emit every scene as a **static
   `class="clip"` element with `data-start`/`data-duration`** written by the Python builder, (b) move devices into
   **JS modules with a fixed interface** (`compositions/studio/devices/*.js`), (c) move all colours/fonts into **theme
   token CSS** (`--paper`, `--ink`, `--accent`… + optional `data-composition-variables` color vars), and (d) reuse the registry
   mainly through **components** (237 dimensionless snippets that join the host timeline). Registry **blocks** (195 of 210 are
   1920x1080; only 14 are portrait, 12 of them 1080x1920) are an optional per-scene sub-composition path, not the backbone.
4. Bake a **gate script**: `lint --json` → `check --json --at <scene midpoints + seam±0.1> --at-transitions` with a generated
   `index.motion.json` (asserts each key word appears by its voice timestamp) → `snapshot --at` for eyeballing → a
   **seek-order test** (`snapshot --at late,early` vs `--at early`, pixel diff) → render → `ffprobe` duration. Note that the static
   tools (`timeline`, `keyframes`) are **blind to runtime-built DOM**: on fs_v3 `timeline` shows no tracks and `keyframes --shot`
   finds nothing under `.cl-page`.
5. Audio: `hyperframes-audio` can replace most of the ffmpeg post-mix (placement, `data-volume`, `data-automation` fades,
   **voiceover carve** = spectral ducking, `<hf-audio-group>` buses with compressor/limiter, `normalize-audio` LUFS matching),
   with preview/render parity. Advisable as phase 2, after an A/B render. Keep a final ffmpeg loudness pass, because there is no
   master bus and no LUFS target, and BGM looping (`-stream_loop -1`) has no attribute equivalent.

---

## 1. Composition contract rules that matter for a data-driven engine

Quoted verbatim from the skills. "(core/…)" means `hyperframes-core/references/…`.

### 1.1 Root, canvas, duration
- Root needs `data-composition-id`, `data-width`, `data-height`; "The standalone root authors `width`/`height: 100%`. Canvas size is `data-width`/`data-height`. … Do not hardcode `1920px`/`1080px` on `#root`." (core/SKILL.md)
- Standalone vs sub-comp: "**Standalone** (top-level `index.html`): root … directly in `<body>`, **no `<template>` wrapper**. Wrapping a standalone root hides all content and `lint` rejects it." (core/SKILL.md)
- **Root duration is compile-time, not script-time**: "`data-duration` … **Read once at compile time, like `data-width` / `data-height`**: a static root `data-duration` is locked before scripts run, so a script (`root.setAttribute("data-duration", ...)`) or a `--variables`-driven value cannot change the render length. … (A clip's `data-duration` is different: re-read from the live DOM, so scripts/variables can drive it.) Only when the root omits `data-duration` does the renderer derive total length from the live DOM / timeline after scripts run." (core/data-attributes.md)
  - Engine implication: our build-time substitution of `__DUR__` is the correct pattern. If we ever want one static engine file
    rendered with `--variables`/`--batch`, the root must **omit** `data-duration` and let the timeline length define it
    (lint then only warns `root_composition_duration_derived`).
- "Render length is the root's `data-duration`, **not** the timeline's length: a timeline that runs past it is cut off, and one that ends early holds its last frame." (core/SKILL.md)
- "Do **not** create empty tweens only to set duration; use `data-duration` on the clip instead." (core/determinism-rules.md)

### 1.2 Clips, timing, visibility ownership
- "**`data-start` is what makes an element a clip.** The runtime collects `[data-start]` and drives visibility off that attribute." `class="clip"` "is a **convention, not a requirement** … `lint` warns (`timed_element_missing_clip_class`)". (core/data-attributes.md)
- "**The visibility window is half-open: `[start, start + duration)`.** … Land an animation's resolved end state slightly **before** `data-duration`, not on it, or its last frame is never rendered." (core/data-attributes.md)
- "**Root-level clips get automatic layout.** For direct children of the composition root that carry `data-start`, the runtime forces `position: absolute` … Elements **without** `data-start` are skipped entirely: an untimed full-bleed background needs its own `position: absolute; inset: 0`." (core/data-attributes.md)
- "Two clips on the same track may overlap in time. Nothing rejects it … Visual layering (front/back) is controlled by CSS `z-index`, not by track index." (core/tracks-and-clips.md). Overlapping clips are how seams work.
- **The framework owns clip visibility**: "Never tween `display`, `visibility`, or `autoAlpha` on a `.clip` element. … `lint` rejects it (`gsap_animates_clip_element`). Animate a child instead." and "Do not add a scene-exit `tl.set(..., {visibility:"hidden"})`. The runtime already hides timed clips." (core/SKILL.md)
- For non-clip children: "For visibility changes, use `autoAlpha` on the registered seekable GSAP timeline, or a zero-duration `tl.set()` at an explicit boundary. Target only a non-clip element or a wrapper inside the clip; never target `.clip` itself." (keyframes/SKILL.md). *Our finding (§4.3) shows why `autoAlpha` (it restores `visibility:inherit`) is safer than a raw `visibility:"hidden"` set.*
- Relative timing (`data-start="intro + 2"`) fails **silently to 0** on typos or missing spaces; "Because every failure mode above is a silent 0, snapshot a reference-timed composition". (core/tracks-and-clips.md). **Engine rule: the builder writes absolute numbers only.**
- Studio: "`data-hidden` on any composition element hides it in BOTH preview and render". `data-track-index` is display-only.

### 1.3 Sub-compositions (`data-composition-src`)
- Transport: "**Finds the `<template>` element and clones ONLY its contents into the host slot.** … Everything **outside** the `<template>` (including the entire `<head>`) is **discarded**." Put `<style>`/`<script>` inside the template; "`<link>` is hoisted either way". (core/sub-compositions.md, core/SKILL.md)
- Ids must match three ways: host `data-composition-id` = inner root `data-composition-id` = `window.__timelines` key. Mismatch symptom: "`Sub-composition timelines not registered after 45000ms: <host-id>` … waits 45s per scene, then captures static initial-state frames". (core/sub-compositions.md)
- "**Do not** manually `master.add(child)` a sub-composition timeline into the host timeline. HyperFrames already drives them independently, and nesting them in GSAP causes double-seeks." (core/sub-compositions.md)
- "**a sub-composition timeline cannot reach or animate host elements**. Neither `document.querySelector("#host-id")` nor a gsap selector string … resolves across the boundary." (core/variables-and-media.md). **This is the main reason cross-scene seams are hard with one-sub-comp-per-scene.**
- "The host re-seeks the sub-composition every time its clip becomes visible; `gsap.from()` records the starting state at registration and can desync on seek-back, while `gsap.fromTo()` declares both endpoints explicitly". (core/sub-compositions.md)
- "Internal timeline shorter than the slot → the slot holds" its final frame; a full-bleed sub-comp shorter than the host is flagged `subcomposition_blanks_before_host`.
- Style the sub-comp root with `#root`, never a class (`subcomposition_root_styled_by_class`). Prefix inner ids with the composition id. Ids must be unique across the **assembled** page.
- `render -c` (CLI help): "Sub-compositions using `<template>` wrappers must be referenced from index.html via data-composition-src."

### 1.4 Variables (data injection)
- Declared on `<html data-composition-variables='[{id,type,label,default}]'>`; types `string|number|color|boolean|enum`. No object/array type, so structured scene data would have to travel as a JSON string.
- "Every scalar variable is applied automatically as a `--{id}` CSS custom property on the composition root, so `var(--id)` CSS responds to overrides". This is a ready-made **theme-token channel**: declare `accent`, `paper`, `ink` as `color` vars.
- Script access: `window.__hyperframes.getVariables()`; "Read values once during init, not on every animation tick".
- Per-instance: `data-variable-values='{"title":"…"}'` on a sub-comp host. Per-render: `--variables`, `--variables-file`, `--batch rows.json`, and `--strict-variables` in CI.
- Declarative bindings: `data-var-text`, `data-var-src`.

### 1.5 Media
- `<video>`/`<audio>` work at any nesting depth; "Every `<audio>` needs an `id`. The mixer selects `audio[id][src]`, so an id-less `<audio>` is never mixed and the render is **silent**." Never `crossorigin`. Never call `play()/pause()`/seek. Don't animate timed media dimensions; animate a wrapper.
- "`video_nested_in_timed_element`": do not put `<video data-start>` inside a plain `data-start` wrapper (sub-comp hosts are exempt).
- Audio inside a scene file uses scene-local `data-start` (host start is added).

### 1.6 Determinism
- Banned for visual state: "`Date.now()`, `performance.now()` … Unseeded `Math.random()` … Render-time network fetches for required assets. Inline or pre-bundle them. … Hover, scroll, pointer, or focus state … Infinite loops such as `repeat: -1`." (core/determinism-rules.md)
- "Animating the same property on the same element from multiple timelines at the same time … is order-dependent and can flip between renders."
- Lint enforces a **denylist**: "`filter`, `clipPath`, `strokeDashoffset`, `width`, `height` and similar are all legitimate targets." Prefer transforms for smoothness: "the browser compositor snaps layout properties to whole device pixels … motion that … visibly stutters when slow" (gsap-transforms-and-perf.md), so no `letterSpacing`/`fontSize` tweens and no `roundProps`.
- "**Pre-calculated layout constants** — never derive positions from `getBoundingClientRect()` at tween time … compute coordinates once at composition setup and reuse." (animation/SKILL.md)
- Registry quality bar F5 is the operational definition of seek-safety: "two snapshots of the same timestamp reached by different seek paths differ" means the item is broken.

### 1.7 Fonts
- "A named CSS `font-family` needs an in-file `@font-face` to a shipped local file, or `lint` fires `font_family_without_font_face`." For an OS font: "use `src: local('Exact Font Name')` … the declaration alone satisfies this check". (core/SKILL.md, lint output)
- Observed: our Google-Fonts `<link>` families (Be Vietnam Pro, Playfair Display, JetBrains Mono) pass lint because they are in the CLI's "auto-resolved font list" (snapshot printed `Fonts: 4 loaded`). Only the CJK fallbacks failed. For hermetic, offline-reproducible renders, still ship local woff2 files that include the Vietnamese subset.
- Text fitting for data-driven copy: `window.__hyperframes.fitTextFontSize(text, { maxWidth, fontFamily, fontWeight })` and `window.__hyperframes.pretext` (canvas measurement, no reflow). No `<br>` in body text.

### 1.8 Async build + timeline registration (the fonts.ready question)
- **Allowed (core, GSAP adapter)**: "Building inside an async callback (`document.fonts.ready`) is supported; what matters is that you **register only after the build completes**." "An empty timeline registered early is treated as ready and nested empty, so the animation renders blank (`lint`: `gsap_timeline_registered_before_async_build`, error). Assign `window.__timelines[id] = tl` at the **end** of the callback … and optionally call `window.__hfForceTimelineRebind()` right after." (core/determinism-rules.md)
- **Contradicting guidance** in the same skill set: animation/SKILL.md lists "no timeline construction inside `async` / `setTimeout` / `Promise`", and keyframes/SKILL.md says "build synchronously at page load" and "Never use … async-created timelines". Core and the GSAP adapter are the more specific sources and cite a lint rule, so they win. **Engine rule**: build the DOM and all tweens synchronously, and use `fonts.ready` only for measurement-dependent tweens followed by registration (what fs_v3 already does). Better still, remove the need to measure (see §2.5).
- "If the key does not match the root's `data-composition-id`, the runtime still binds it **when it is the only registered timeline**. With two or more registered, a mismatched key leaves the render frozen at t=0."
- `window.__timelines = window.__timelines || {}` is unnecessary ("the runtime creates the registry before your inline scripts run") but harmless.

### 1.9 Seek-safety specifics for GSAP
- "`immediateRender` — default `true` for from()/fromTo(). Set `false` on later tweens targeting the same property+element." (gsap.md)
- `tl.play()` is forbidden for render-critical motion. Use finite `repeat`: `Math.max(0, Math.floor(duration / cycle) - 1)` (`gsap_repeat_ceil_overshoot`).
- Callback-driven state (`onUpdate` writing DOM) is fine **only** if the written state is a pure function of the tween's progress. fs_v3's rain, counter, wheel `place()` and caption driver all satisfy this.
- Zero-duration `set`s record their "from" value **when first rendered**, and backward seeks restore it. Never `set` a raw `visibility:"visible"` / `"hidden"` on an element whose visibility is meant to be inherited (see §4.3).

### 1.10 Studio conventions (if humans will open the project)
- "The root composition holds only timed hosts, media and audio. Any scene with nested structure … is its own file loaded with `data-composition-src`." "All captions live on one track … marked `data-track-kind="captions"`." Safe boxes: action-safe 90% (5% inset), title-safe 80% (10% inset). On 1080x1920 the title-safe box is x 108–972, y 192–1728. fs_v3's kicker/caption at x=64 sit outside it.
- Lint now warns `composition_file_too_large` (fs_v3: 311 lines).

---

## 2. Architecture: devices as (a) JS modules, (b) sub-compositions, or (c) registry components?

### 2.1 What each option buys, per the docs

| | (a) JS modules in one composition (today) | (b) one sub-composition per scene | (c) registry-style components |
|---|---|---|---|
| Timeline | One paused tl; seams, caption driver, ghost word and topbar all see every scene | One tl per scene file, seeked independently by the runtime; host tl near-empty | Snippet joins the **host** timeline ("Components inherit the host composition's dimensions and duration") |
| Cross-scene seams (cut-the-curve, zoom-through, carry-over elements) | Trivial: `seam(a, b, T)` touches both roots | Hard: "a sub-composition timeline cannot reach or animate host elements". The exit must be authored in A's file and the entry in B's file, with overlapping host clips; velocity matching spans two files. The docs suggest "**C. Multi-scene merge**" (phases in one sub-comp) exactly when scenes share continuous state | Same as (a) |
| Data injection | DATA JSON inlined by the builder | `data-variable-values` per host (scalars; JSON must be a `string` var), or builder-templated files | Function arguments |
| Registry reuse | Components paste in; blocks can still mount as sub-comps | Blocks plug in natively (they *are* sub-comps) | This is how components are meant to be used |
| Studio / `timeline` CLI | Opaque (fs_v3: `timeline` prints no tracks) unless scenes are static clips | Best: one row per scene | Same as host |
| Static tooling (`keyframes`) | Blind to runtime-built targets | Better if scene markup is static | Same as host |
| Failure modes | Monolith size (`composition_file_too_large`); manual visibility bugs (§4.3) | 45 s timeout per id mismatch; `<head>` styles dropped; id collisions on the assembled page; async fonts.ready registration per scene; re-seek on mount needs `fromTo` everywhere | Name/id collisions; must prefix |
| Determinism | One clock | Runtime keeps all scene timelines on one clock ("seeks the block in sync with the host, offset by `data-start`"), so determinism holds | One clock |

"One-timeline determinism" is a per-composition rule ("Each composition registers **exactly one** `gsap.timeline({ paused: true })`"), not a per-project one. (b) is deterministic too. Its real cost is the **lost cross-scene choreography and the shared caption/background layers**, which are core to our style.

### 2.2 Recommendation: hybrid "one host timeline, static clips, device modules, token themes"

1. **One host composition per video** (standalone `index.html` in a per-job mini project), **one paused timeline** keyed `main`.
2. **Every scene is a static timed clip** written by the Python builder:
   `<section id="s3" class="clip scene" data-start="9.58" data-duration="5.12" data-track-index="1" data-device="wheel"><div class="stage"></div></section>`.
   Scene windows overlap by the seam length. The **runtime then owns scene visibility**, which removes every `visibility` set from
   the engine. Seams tween `.stage` (the inner wrapper): `y`, `opacity`, `scale`, `filter`. `timeline`/Studio now show one row per scene,
   and `check` audits only visible scenes.
3. **Devices = JS modules with a fixed interface** (registry "component" discipline, without becoming sub-comps):
   ```js
   // compositions/studio/devices/wheel.js
   HFS.device("wheel", {
     css: "wheel.css",                         // optional, inlined by the builder
     build(ctx, spec, stage) { /* create DOM inside stage only; no tweens on .clip */ return handle; },
     enter(ctx, handle, t0)  { /* add tweens at absolute times via ctx.at(anchor) */ },
     after(ctx, handle)      { /* optional: measurement-dependent tweens (run inside fonts.ready) */ },
     exitHint: { axis: "y", dir: -1 },          // lets the seam engine match velocity
   });
   ```
   `ctx` provides: `tl`, `at(anchor)` (word-time resolver), `words()`, `waterfall()`, `rng(seedKey)` (**per-scene seeded PRNG**;
   today one global LCG `seed=7` is consumed in build order, so adding a scene changes another scene's rain/burst), `theme`
   (tokens resolved once via `getComputedStyle`), `svg()` helpers, and `diag.error(code, detail)`.
4. **Core module** (`studio/core.js`) owns: DATA parsing/validation, anchor resolution, the seam library, the caption track,
   shared layers (bg/bloom/grain/ghost/topbar), the build order, `fonts.ready` → `after()` → registration →
   `__hfForceTimelineRebind()`, and diagnostics (`window.__hfsDiag`).
5. **Registry reuse**:
   - **Components** (237, dimensionless) are first-class: install with `hyperframes add <name>` into `compositions/components/`,
     then wrap each one as a device or a shared-layer effect. Its JS/CSS gets inlined, and its "Timeline integration" calls go on `ctx.tl`.
     Prefer ones whose ink already routes through `var(--…)` (quality bar X5).
   - **Blocks** (sub-comps with their own timeline): only 14 of 210 are portrait (12 at 1080x1920) (e.g. `flowchart-vertical`, `notes-reveal`,
     `notification-cascade`, `message-thread-reveal`). Support them as an **optional device kind `block`**: the builder emits
     `<div class="clip" data-composition-id="X" data-composition-src="compositions/X.html" data-start data-duration data-width="1080" data-height="1920" data-variable-values='…'>`.
     Accept that seams into and out of a block can only tween the host wrapper, not the block's internals. 16:9 blocks would need
     re-layout, so treat them as recipes to port into a device, not as drop-ins.
   - Run `npx hyperframes catalog --query "<move in English>" --json` before hand-building a new device (registry skill rule),
     and `feedback --search-miss` on a miss.
6. **Captions**: one caption layer (`#cap`, untimed, or a single clip spanning the video, `data-track-kind="captions"` if Studio matters).
   Prefer **pre-built caption groups** toggled with `tl.set(group,{opacity})` plus a "hard kill" at group end (registry caption
   template) over the current `onUpdate` + `innerHTML` swap. Both are deterministic, but pre-built groups are visible to `check`'s
   layout and contrast passes and to `--caption-zone`.

### 2.3 File layout

```
hyperframes_short/
  hyperframes.json                      # paths.blocks=compositions, components=compositions/components
  compositions/
    studio/                             # ENGINE SOURCE (versioned, never rendered directly)
      core.js                           # ctx, anchors, seams, captions, layers, registration, diag
      seams.js                          # curve-cut, zoom-through, page-flip ... (pure tween builders)
      devices/{hook,split,window,wheel,calendar,stamp,ledger,close}.js
      devices/{hook,...}.css            # device CSS using ONLY tokens
      themes/base.css                   # structural tokens: safe insets, caption band, type scale
      themes/fs-poster.css              # :root{--paper;--ink;--accent;--accent-2;--gold;--mute;--font-display;...}
      themes/bud-ink.css
      themes/<channel>.json             # JS-side tokens: eases, durations, seam defaults, svg palette
      fonts/*.woff2 + fonts.css         # local @font-face (Vietnamese subsets, CJK serif subset for 未 etc.)
      engine.version                    # hash written into every built job
    components/                         # registry snippets (hyperframes add)
    <registry-block>.html               # portrait blocks only, mounted as sub-comps
  jobs/<video_id>/                      # one mini project per video = one gate/render unit
    hyperframes.json
    index.html                          # GENERATED: inlined core+devices+theme+DATA, static scene clips
    index.motion.json                   # GENERATED motion assertions (§3.3)
    assets/{vo.wav,bgm.*,sfx.wav,img_*.jpg}
```
Why one mini project per job: `lint`/`check` scan `index.html` + `compositions/`, and `check` only audits a project's
`index.html`. Linting the shared `compositions/` dir would mix in every `_rv_*`/`_v3_*` file. The repo's `hf_qa.py` already uses
the temp-project trick for long videos.

**Inline or `<script src>`?** Inline at build time and stamp `engine.version`. Reasons: (1) "Inline or pre-bundle" required
assets; (2) re-rendering an old job must not pick up a newer `core.js`, which is the reproducibility the pinned CLI version
already aims at; (3) it avoids relative-path differences between `render -c compositions/x.html` and `index.html`. The trade-off is that
`composition_file_too_large` keeps warning. Accept that warning, or point the gate at it.

### 2.4 How theme tokens and variables should flow

```
channel theme (themes/fs-poster.css + .json)
   └─> builder inlines CSS; writes <html data-composition-variables> for the few tokens worth overriding per render
         (color: accent, paper, ink; string: kicker; enum: seamStyle)
           └─> runtime sets --accent/--paper/... on the root automatically ("--{id}")
                 └─> all device CSS uses var(--token, <fallback>) only
                 └─> core.js resolves tokens ONCE at init: theme = read(getComputedStyle(root)) for JS/SVG use
                       └─> devices use theme.accent etc. for SVG fills and GSAP attr/color tweens
registry components: same var(--token) contract (quality bar X5); CSS custom properties inherit into
                     sub-comp DOM because the template is cloned into the host page (no iframe).
```
Rules: no hex literals in devices. fs_v3 hardcodes ~15 hexes in SVG attributes and tweens (lines 212–264, e.g.
`attr:{fill:"#C32F27"}`), which breaks re-theming for BUD. SVG presentation attributes do not resolve `var()`, so set `style="fill:var(--ink)"`,
use classes, or pass `theme.*` values. Root `data-duration` and per-scene clip windows remain **builder outputs**, never variables.

### 2.5 Kill the measurement dependency where possible
`hook.after()` and `close.after()` use `getBoundingClientRect()` after fonts load to place underlines. Make them layout-relative
instead: put the underline as an absolutely positioned child (or `::after`) of the measured word span and tween `scaleX`. Then no
measurement is needed, the build is fully synchronous, and the fonts.ready caveat goes away. Keep `fonts.ready` only for
`fitTextFontSize` / pretext sizing of long data-driven headlines, followed by registration.

### 2.6 Builder (Python) contract
- Validate spec → resolve every word anchor in Python (the same `at()` exists twice today, in JS and in `build_v3.sfx`). Emit
  absolute seconds into DATA **and** fail the build on unresolved anchors (JS currently only `console.warn`s and falls back
  to line start).
- Emit static scene clips with `data-start`/`data-duration` = [seam-in start, next seam end], plus `index.motion.json`.
- Single source of truth for SFX/visual cue times: devices declare cue anchors; the builder places SFX from the same resolved
  times (in-composition `<audio>` clips or the hf_sfx mix).

---

## 3. QA / verification toolchain to bake into the skill

All commands: `export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"; cd jobs/<id>; npx --yes hyperframes@0.8.75 …`
(Node ≥ 22 and FFmpeg required; `doctor --json | jq -e .ok` first on a new machine).

| Step | Command | Catches | Read it |
|---|---|---|---|
| 1 Static | `lint --json` (`--verbose` for info) | contract errors: root/template shape, `gsap_animates_clip_element`, `gsap_css_transform_conflict`, `gsap_timeline_registered_before_async_build`, `font_family_without_font_face`, `media_missing_id`, `negative_z_index`, `gsap_repeat_ceil_overshoot`, file size | **Any error blocks the browser audits**: `check` then shows `0 sample(s)` / `0/0 text checks`, which is NOT a pass |
| 2 Browser gate | `check --json --at <scene mids, seam T±0.1> --at-transitions --max-transition-samples 80` | **Runtime**: console errors, unhandled exceptions, failed requests/4xx/5xx. **Layout**: `content_overlap`, `text_occluded`, `canvas_overflow`, `container_overflow`, `escaped_container`, `text_not_painted`, `sweep_static`. **Motion**: sidecar assertions. **Contrast**: WCAG AA with `suggestedColor` | JSON envelope `{ok, lint, runtime, layout, motion, contrast, hdr, snapshots}`; gate on `ok`; findings carry selector, bbox, `t`. Severity is persistence-aware (single-sample transients become info) |
| 2b Shorts UI zone | `check --caption-zone "x0=0;y0=.86;x1=1;y1=1;severity=error;seek=.25,.5,.75"` (tune band to the Shorts overlay) and `--frame-check` | text under the YouTube UI; media pushed off-frame | waive intentional copy with `data-layout-allow-caption-zone` |
| 3 Motion intent | `index.motion.json` next to `index.html` (auto-discovered) | `appearsBy` (opacity ≥ 0.5 by t) = **text-on-voice sync**, `before(a,b)` = order, `staysInFrame`, `keepsMoving` (default `maxStaticSec` 2 s) | errors by default; typo'd selectors fail loudly (`motion_selector_missing`) |
| 4 Eyeball | `snapshot --at <t1,t2,…> --no-end -o snaps/` (contact-sheet.jpg); `snapshot --zoom "#cap"` for crops | anything `check` can't judge ("`hyperframes check` is not a visual gate. It passes compositions that render nothing") | look at every scene midpoint and every seam |
| 5 Seek-order test | `snapshot --at T_late,T_early --no-end -o A` vs `snapshot --at T_early --no-end -o B`, then pixel-diff `A/frame-01*` vs `B/frame-00*` (PIL/ffmpeg `psnr`) | non-seek-safe state (quality bar F5), e.g. the calendar leak in §4.3 | any diff above noise blocks the render |
| 6 Keyframes | `keyframes . --json`; `keyframes . --selector S --shot k.png --layout strip --from a --to b` | trajectory, ghosts, 3D projection | **Limited for us**: static analysis cannot resolve runtime-built targets ("`__unresolved__`", all at `@0s`) and `--shot` reported "nothing animates under '.cl-page'". Useful only for statically authored selectors |
| 7 Timeline | `timeline --json` | clip windows, audio rows, lanes, durations (`absStart/absEnd`) | becomes useful once scenes/audio are static clips (§2.2); today it shows only `timeline 31.38s` |
| 8 Render | `render . -o out.mp4 --quality looks --fps 30 --strict` (`--strict-all` once warnings are clean) | `--strict` fails on lint errors | read the summary's 2nd line (`beginframe` vs `screenshot`, GPU, stage timings) |
| 9 Output | `ffprobe -v error -show_format -show_streams out.mp4` | duration vs root `data-duration`, fps, audio stream present | — |
| 10 Perf (occasional) | `benchmark --runs 2 --json` | fastest acceptable preset/worker count on this M1 | not a gate |

**Catching JS runtime errors headlessly**: `check` (runtime section) is the supported path. It wires listeners before
navigation and reports console errors, unhandled exceptions and failed requests. To make engine-level problems gate:
- use `console.error` (not `console.warn`) or `throw` for unresolved anchors, unknown device types, missing assets and font fallback;
- expose `window.__hfsDiag = {errors:[…], anchors:{…}, engine:"<hash>"}` for a custom probe, and keep a `motion.json`
  `appearsBy` on a sentinel element that only becomes visible if the build completed;
- `validate --json` (deprecated alias) still works and `check --timeout 30000` raises the render-ready budget for heavy builds.

**Generated `index.motion.json` example** (builder writes one `appearsBy` per anchored word/element):
```json
{ "duration": 31.38, "assertions": [
  {"kind":"appearsBy","selector":"#s0 .hk-big .wd:nth-child(1) .in","bySec":0.35},
  {"kind":"appearsBy","selector":"#s3 .pill","bySec":17.9},
  {"kind":"before","a":"#s1 .sp-a .sp-val","b":"#s1 .sp-b .sp-val"},
  {"kind":"staysInFrame","selector":".stage"},
  {"kind":"keepsMoving","withinSelector":"#root","maxStaticSec":2.5}
]}
```
(Use stable ids/`data-*` hooks generated by devices so selectors don't depend on `nth-of-type`.)

**Escape hatches to place at construction time** (not after check complains): `#ghost`, `#grain`, `#bloom` →
`data-layout-ignore`; rain/burst decor → `data-layout-allow-overflow` on the narrowest wrapper; stacked calendar pages →
`data-layout-allow-overlap` on the page stack only. Don't put allow-overflow on scene roots: it suppresses `text-clipping` /
`foreground-over-panel` for all descendants.

---

## 4. Findings on the current v3 engine (fs_v3.html → _v3_v3_a / _v3_v3_b)

### 4.1 `lint` (both samples; real run, repo untouched)
```
⚠ composition_file_too_large (311 lines)
⚠ negative_z_index  .hl  (fs_v3.html:94, z-index:-1 — ledger highlight; parent .lg-s has no stacking context → can vanish behind an opaque context)
✗ font_family_without_font_face  noto serif sc, songti sc, stsong  (fs_v3.html:80, .st-han)
1 error, 2 warnings
```
The `font_family_without_font_face` error makes `check` skip runtime, layout and contrast entirely (observed: `0 issues across 0 sample(s)`).
Because the builder never ran lint, this has gone unnoticed. The 未 glyph in `stamp` renders in a random fallback face.

### 4.2 `check` (scratch copy with `@font-face{src:local(...)}` added to unblock it; `--at-transitions`)
- **Runtime: 0 errors, 0 warnings.**
- **Layout: 58 errors, 15 warnings.**
  - ~45 `content_overlap` / `text_occluded` findings involving `div.cl-stage > div:nth-of-type(2)`, the **2026 calendar page**, against
    the hook (0.13–4.36 s), split (4.48–9.46 s), window "MƯA" (9.71–14.32 s) and wheel labels (14.57–20.05 s). This is the leak in §4.3.
  - `text_not_painted #ghost` (alpha .045 by design) and `canvas_overflow #ghost` (left 40 px / right 328 px). These are intentional and need `data-layout-ignore`.
  - Calendar page-vs-page overlap 20.3–28 s: intentional stack, needs `data-layout-allow-overlap` scoped to the stack.
  - `container_overflow` of rain rects (2 samples), mask overflow `span.in inside span.wd.mask` at 28.36 s (close-scene entrance transient).
  - Info: hook text overflowing left at 4.44 s, which is the seam's motion (transient).
- **Motion**: no sidecar, nothing asserted.
- **Contrast: 7 errors.** `#foot` 3.02:1 (needs 4.5; suggested `rgb(108,99,89)`); `#ghost` 1.09:1 (decor, so ignore); dimmed
  caption words `.w` at 28% ink = 1.83:1 (needs 3:1; this is the karaoke "not yet read" state, so raise it to roughly 45–50% or mark it).

### 4.3 Proven seek-order bug (`snapshot`)
- `snapshot --at 2,12` gives the correct hook and "MƯA" window frames.
- `snapshot --at 26,2,12` shows the **"THÁNG 2 · 2026 / 17 / THỨ BA" page covering the hook at 2 s and the window at 12 s**.
- Mechanism: `tl.set(pages[k], {visibility:"hidden"}, tf+.36)` (fs_v3.html:290). When first rendered (scene visible), GSAP
  records the start value `visible`. A backward seek writes inline `visibility:visible` on the page, and an explicitly visible
  child of a `visibility:hidden` parent **is painted**. The same hazard exists for any `tl.set(x,{visibility:…})` on a
  descendant of a hidden scene.
- Fix pattern (for the next phase, not applied): never set `visibility` on children. Use `autoAlpha` (which restores
  `visibility:inherit`) or `opacity` on the page, and let the runtime own scene visibility through static clips (§2.2).

### 4.4 Contract deviations seen by reading the code (not all flagged by lint)
| # | Where | Issue | Rule |
|---|---|---|---|
| 1 | fs_v3.html:31, 349 | Scenes are untimed `.scene` divs. No `data-start`/`data-duration`/`class="clip"`, so the framework's clip lifecycle is bypassed and `timeline`/Studio/`keyframes` see nothing | core: "`data-start` is what makes an element a clip"; studio §1 |
| 2 | :356, :363, :357, :364, :368 | Scene show/hide via `tl.set(root,{visibility})`. Legal on non-clips, but this is the manual reimplementation core warns against ("The runtime already hides timed clips"), and §4.3 shows its fragility | core/SKILL.md pitfall |
| 3 | :290 | `visibility:"hidden"` set on a child, which causes the backward-seek leak | §4.3 |
| 4 | :80 | CJK fallback fonts without `@font-face` (lint error) | core: fonts |
| 5 | :6–8 | Google Fonts over the network at render time. Lint tolerates it through the auto-resolve list, but it is a network dependency | determinism: "Render-time network fetches … Inline or pre-bundle them" |
| 6 | :182, :340 | `getBoundingClientRect()` measurement after `fonts.ready`. Allowed at setup, but it depends on no transforms being applied at measure time (immediate-render `fromTo`s are, e.g. `calendar` stage `y:120`) | animation: "compute coordinates once at composition setup" |
| 7 | :392–396 | Async registration is correct (registered at end), but `__hfForceTimelineRebind()` is not called. `tl.seek(0)` and `__timelines ||= {}` are redundant | core/determinism-rules |
| 8 | :372, :376 | `tl.set(ghost,{textContent})`: GSAP sets a DOM property, it is not a tween. It works and is seek-reverted, but it is invisible to `keyframes`, and the ghost changes copy without any transition | prefer per-scene ghost elements inside each scene clip |
| 9 | :383–390 | Caption driver rewrites `innerHTML` in `onUpdate`. Deterministic, but captions do not exist as DOM between updates, so `check`'s caption-zone/contrast passes sample only whatever chunk is current | studio: one caption track; registry caption template |
| 10 | :121 | One global LCG shared by all scenes in build order. Deterministic, but not stable under spec edits | quality bar X7 spirit; use per-scene seeds |
| 11 | :212–264 | Hardcoded hex in SVG attrs and GSAP `attr` tweens bypass the theme | quality bar X5 |
| 12 | :354–359 | `filter: blur()` animated on full-frame scene roots during zoom seams. Legal (denylist), but it is the most expensive property on the largest element; keep it short or blur a snapshot layer | gsap perf |
| 13 | :374–375 | Loop-back seam starts at `DUR-.45` with a 0.5 s tween, so the final frame lands mid-tween (ends at DUR+0.05) | "Land an animation's resolved end state slightly before `data-duration`" |
| 14 | :94 | `z-index:-1` highlight with no stacking-context parent (lint warning) | lint `negative_z_index` |
| 15 | :129 | Unresolved word anchor only `console.warn`s and silently falls back to line start | make it an error so `check` gates |
| 16 | build_v3.py | `img` for `window` is copied to `_media` but never used (the device draws a gradient) | spec/device mismatch, so validate the spec |
| 17 | kicker/cap at x=64 | Outside the 10% title-safe inset (x ≥ 108 on 1080 wide) | studio safe zones |

Things that are already right: root sized 100% with `data-width/height` and a static `data-duration`; one paused timeline keyed
`main` matching `data-composition-id`; registration at the end of the async callback; no `Math.random`/`Date.now`; no
`repeat:-1`; `immediateRender:false` on later `fromTo`s; no CSS-transform/GSAP conflicts (rotated `.hk-num`, `.sp-num`, `.cl-day`
are never tweened); `onUpdate` state is a pure function of progress.

---

## 5. Audio: can `hyperframes-audio` replace the ffmpeg post-mix?

Current post-mix (`build_v3.py`): render silent MP4 → ffmpeg `amix` of VO (apad) + BGM (`-stream_loop -1`, `volume=gain`,
`afade out 1.2 s`) + one synthesized SFX wav → AAC 192k, `-t dur`, `normalize=0`. No ducking or carve; BGM sits at a fixed gain under the voice.

What HyperFrames offers (all attributes on `<audio id src data-start …>`; preview and render use **the same Web Audio graph**, so
"what you hear while scrubbing is what gets written"):
- **Placement/gain**: `data-start`, `data-duration`, `data-media-start`, `data-volume` (0–3.98, i.e. +12 dB), `data-playback-rate`.
- **Fades/automation**: `data-automation` volume lane (`t` is clip-local seconds, max 512 points). This replaces `afade`. "Never add a lane
  to a track that already has a `volume` tween." On a group bus, lanes use composition time.
- **Effects**: `data-fx-chain` with highpass/lowpass/peaking/shelves, compressor, limiter, gate, saturate, delay, reverb, chorus,
  phaser, bitcrush. Presets include `voice-clean` and `voice-broadcast` (rumble cut → mud → evenness → clarity → peak ceiling).
- **Ducking done right, "Voiceover carve"**: `data-fx-carve` on the **bed**, pointing at a **voice group**. A dynamic, multi-band dip
  plus a level-match gain envelope that follows the speech. "**Carve by default — required whenever music plays under a voice.**"
  Headless: `node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html [--bed id --voice id --strength 0.8 --dry-run]`.
  It needs ffmpeg plus `@hyperframes/core` installed in the project (`npm i -D @hyperframes/core`), and it writes the chain and lanes into the HTML.
- **Buses**: `<hf-audio-group id="sfx" data-volume data-fx-chain data-automation>` gives one chain/fader/clock over members
  (`data-audio-group="sfx"`). Keep groups role-pure (`voiceover`, `music`, `sfx`) or the carve rots.
- **Loudness matching**: `npx hyperframes normalize-audio --reference vo --target bgm [--write]` (integrated LUFS; `--write`
  edits index.html).
- **Inspection**: `timeline --json` lists audio rows with `vol=`, `group=`, lanes. Lint covers only `media_missing_id`,
  `duplicate_audio_track`, `audio_volume_double_automation`, `audio_volume_tween_overrides_gain`, `audio_carve_ungrouped_sources`,
  `audio_group_carve_attr`. "Nothing validates the chain or the effect lanes at all", but a chain the render cannot parse **fails the
  whole mix** (it does not silently write a dry mix).

Is in-composition audio advisable for our pipeline?
- **Yes for: placement, fades, the carve and per-role buses.** It gives one source of truth (SFX cue times come from the same resolved
  anchors as the visuals), Studio preview with sound, and no separate ffmpeg graph to keep in sync. The carve is a real quality
  upgrade over today's fixed-gain BGM, and the skill treats a plain duck as unfinished.
- **Keep from ffmpeg (or add)**: (1) BGM looping. There is no loop attribute, so either pre-render the bed to ≥ `dur` (hf_music
  already picks the track) or tile several `<audio>` clips with `data-media-start`. (2) A **master loudness/true-peak stage**.
  There is no master bus or LUFS target. Measure the rendered MP4 with `ffmpeg -af ebur128` and apply a final `loudnorm`/limiter only if it is
  off target, or put every track in groups that each end in a limiter. (3) The AAC bitrate. The render CLI exposes no audio
  bitrate flag (to verify), so if 192k matters, remux the audio.
- Risks: chain parse failures abort the mix (good), effect tails extend tracks, and `carve.mjs` regex-reads **double-quoted**
  attributes only ("Write these attributes double-quoted, with the JSON's own quotes as `&quot;`"), so the Python
  builder must emit them that way.
- Rollout: render one job both ways (current ffmpeg mix vs in-composition plus carve), compare integrated LUFS and true peak, and
  listen. Switch only if the result is equal or better. SFX can stay as one pre-mixed `sfx.wav` `<audio id="sfx">` (simplest) or become
  per-hit clips. Overlapping hits need distinct `data-track-index` values, or lint warns `duplicate_audio_track`.

---

## 6. Open items to verify before codifying in the skill
1. How the runtime hides clips (`display:none` vs `visibility:hidden`). If it uses `visibility`, child inline `visibility:visible` would
   leak even with static clips, which is more reason to ban raw visibility sets on descendants.
2. Whether a standalone `index.html` may load local `<script src="studio/core.js">` in preview and render (expected yes; `check`
   would show a failed request). Inlining avoids the question.
3. Whether HF's "auto-resolved font list" fetches Google Fonts at render time or bundles them (offline render test with networking off).
4. Default AAC bitrate and sample rate of `render` output when `<audio>` is present.
5. Whether `check --at-transitions` sees GSAP tweens added inside `fonts.ready` (it did sample many transition points on v3).
6. Seek order used by parallel render workers. The §4.3 leak only shows on non-monotonic seeks; confirm by rendering a frame range
   that starts after 25 s.

Scratch artifacts from this research (not in repo): `…/scratchpad/lintproj_v3a|v3b/` (copies, with the font-face patch added only after
the first lint), `…/scratchpad/snapA|snapB/contact-sheet.jpg` (seek-order evidence), `…/scratchpad/catalog.json`.
