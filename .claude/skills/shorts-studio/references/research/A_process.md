# A — Process / workflow layer for a reusable "short-video director" skill

Scope: the PROCESS layer only (pipeline, artifacts, gates, dispatch, story design, skill routing, director architecture). Visual technique catalogs are already covered in `../hf_kinetic_type.md`, `../hf_visual_composition.md`, `../hf_3d_whiteboard_chart.md` and are referenced, not repeated.

Sources read (all under `~/.claude/skills/`): `hyperframes/SKILL.md` + every file in `hyperframes/references/` (incl. `routes/*`) + `scripts/lib/frame-packets-core.mjs`; `faceless-explainer/` (SKILL, all 4 references, sub-agent delta, script headers incl. `captions.mjs` params, `audio.mjs` meta shape); `general-video/` (SKILL, delta, packet wrapper); `motion-graphics/` (SKILL, catalog-map, director/builder/finalize agents, shot-plan-ir, builder-contract, motion-vocabulary, grounding/PROTOCOL, phases/source/guide, all 10 category modules); `music-to-video/` (SKILL, planning, validate-plan header); `embedded-captions/` (SKILL flow, caption-grouping, non-negotiables); `talking-head-recut/` (storyboard + card-count + render-strategy sections); `product-launch-video/` + `pr-to-video/` (step/gate outline, story-design beats, transition rules); `hyperframes-creative/references/{story-spine, beat-direction, narration, design-picker, storyboard-recipe, prompt-expansion, design-spec}`; `hyperframes-animation/blueprints-index.md`; `hyperframes-studio` safe zones; `media-use/references/memory.md`.

---

## 1. The end-to-end pipeline the official skills prescribe

### 1.1 The four document layers

`brief-format.md`: "the project's files read as four layers: **`BRIEF.md`** (why, for whom, and everything the user asked for) → **`STORYBOARD.md`** (what, frame by frame) → **`frame.md`** (how it looks) → **`compositions/`** (the thing itself)." Plus `SCRIPT.md` (locked narration) and generated sidecars (`audio_meta.json`, `caption_groups.json`, `.hyperframes/frame-packets/*`, `snapshots/contact-sheet.jpg`).

### 1.2 Stage-by-stage (faceless-explainer is the closest match to a narrated 9:16 short)

| # | Stage | Owner | Artifact | Gate (quoted / paraphrased) | Human needed? |
|---|---|---|---|---|---|
| I | Intent layer (`/hyperframes` → `intent-interview.md`, 8 steps) | entry skill | locked brief summary | memory + recipes read before any question; one question per field; integration check; stated vs inferred listed apart | Only in collaborative runs. "just build it / surprise me" ⇒ `flow: automation, storyboard: no` ⇒ autonomous; every unanswered field becomes "a decision with a receipt" |
| 0 | Setup | workflow | `hyperframes.json`, `BRIEF.md` (written **after** `init`, which refuses a non-empty dir), prefs recorded | "`hyperframes.json` and `BRIEF.md` exist; the preference-backed answers were recorded; sign-in status was shown" | No (autonomous states auth status and continues offline) |
| 1 | Source text | workflow | `capture/extracted/visible-text.txt`, synthetic `tokens.json` | "you can state the explainer's topic and audience in one clear sentence" | No |
| 2 | Design system | `build-frame.mjs --preset <name>` | `frame.md` + `.hyperframes/caption-skin.html` | script exits 0; preset recorded as `style_preset --workflow` | Preference gate: collaborative asks (by eye, showcase HTML), autonomous decides + one-line reason |
| 3 | Story + script | orchestrator (not a subagent) | `STORYBOARD.md` (+ `SCRIPT.md`) | every frame has narrative fields; plan approved — **autonomous: "post the same summary as a heads-up and proceed"** | Checkpoint gate only in collaborative |
| 3.1 | Audio (background) | `audio.mjs` → media-use engine | `audio_meta.json` (voices with word timings, BGM, SFX) | job started, or project marked silent (`music: none` + no `SCRIPT.md`) | No |
| 4 | Visual design | orchestrator | same `STORYBOARD.md`, enriched in place: time-coded shot sequence per frame + one `## Video direction` block | "every frame has a time-coded shot sequence whose reveals are paced to the voiceover (no front-loading)…; `## Video direction` exists" (+ sketch sheet confirmed, collaborative only) | No (sketch pass skipped in autonomous) |
| 5 | Build | `sync-durations` → `fetch-sfx` → `frame-packets.mjs` → N frame workers → `captions.mjs` → `assemble-index.mjs` | `compositions/frames/NN-*.html`, `compositions/captions.html`, `index.html` | "every frame is marked `animated`…, `index.html` exists, and captions are built or explicitly skipped" | No |
| 6 | Finalize | `transitions.mjs inject/verify` → `lint` → `check` → `snapshot --at <frame-midpoints>` → preview/render | `snapshots/contact-sheet.jpg`, `renders/video.mp4` | lint+check pass, contact sheet inspected; **render only after approval in both modes** | **Yes, one question**: collaborative "render now, or what changes?"; autonomous "preview first, or render?" |
| 7 | Deliver + recipe | `media-use recipe.mjs freeze` | `.media/recipes/<name>/` | offered once after approval (autonomous: name the freeze command instead of asking) | Optional |

`production-loop.md` restates this as a **dependency graph**, not numbered steps: Blocks&assets (registry blocks installed "once, before any parallel work (parallel workers race the registry)") → Audio (→ word timings; "when BGM plays under a voice, the bed is carved (`hyperframes-audio/scripts/carve.mjs`) before Verify — a duck alone is not a finished mix") → Frames → Duration sync ("real duration wins, silent scenes keep estimates, synced values are never hand-edited") → Assembly → Transitions → Captions → Verify → Deliver. "A stage whose need is absent simply doesn't run." "An edit request enters at the artifact it touches and re-runs verify."

Scheduling economics worth copying verbatim into our skill: "fire every generation whose prompt is already known concurrently or in the background"; and "Attaching an image re-prices your whole context… Batch visual checks (one contact sheet beats N single-frame views) and schedule them at phase boundaries, not mid-build."

### 1.3 Concrete formats

**BRIEF.md** (`brief-format.md`) — YAML frontmatter, one key per confirmed field:

```yaml
workflow: faceless-explainer      # executor
flow: automation                  # automation | companion
storyboard: no                    # yes | no  -> derives mode (automation+no = autonomous)
message: "Compound interest is a snowball, not a ladder"   # the ONE thing
destination: shorts               # -> aspect derivation
aspect: 1080x1920                 # "TikTok/Reels/Shorts → 1080x1920"
language: vi
length: 35s
angle: concept                    # concept | how-to | listicle | narrative
```
Body: `## Intent` (concept in user's wording, incl. chosen pitch), `## Assets` (`path — what it is, where it belongs`), `## Customizations` (accepted capabilities), `## Notes` (constraints, bans). Only `destination, aspect, language, flow, storyboard, voice, style_preset` are memory keys (`prefs.mjs record`); `style_preset` is per-workflow. BRIEF.md is "the no-repeat token" and must be written back on every mid-run decision ("a decision that lives only in chat is a decision resume never sees").

**STORYBOARD.md** (`storyboard-format.md`, parser `@hyperframes/core/storyboard`, vendored as `scripts/lib/storyboard.mjs`, lenient, never throws):
- Frontmatter: `format` (`1080x1920`), `duration` (advisory), `message`, `arc`, `audience`, `mode`, plus workflow extras (`music:` mood; `music: none` + no SCRIPT.md = canonical fully-silent marker).
- Sections above the first frame (storyboard-recipe § 1; must sit **above** frame 1 because packets slice from a frame heading to the next): Message, audience+arc, format (incl. caption keep-out), **the spine** ("the one device that threads every beat"), brand tokens, **Bans**, **Held frame**, and (faceless Step 4) `## Video direction`.
- Per frame: `## Frame N — Title` then bullets: `status` (`outline → built → animated`), `src` (`compositions/frames/NN-name.html`; the frame_id derives from it), `duration`, `transition_in`, `scene` (contact-sheet caption, **never visible DOM text**), `voiceover` (timing guide, never rendered), `poster`; workflow extras kept under `extra`: `type`, `persuasion`, `beat`, `blueprint`, `focal`, `roles`, `sfx`, `asset_candidates`, `rules`. Prose: `narrativeRole`, `keyMessage`, then the Step-4 shot sequence.

Faceless frame after Step 4 (from `visual-design.md`):
```
## Frame 3 — How interest compounds
- scene: a snowball rolls downhill, gaining a labeled ring each turn
- voiceover: "…"
- transition_in: crossfade
- type: feature_showcase
- persuasion: Concretization + progressive disclosure
- beat: comprehension
- blueprint: dataviz-countup (Adapt)
- focal: the snowball
- roles: snowball = foreground subject · hill = background gradient (dim ~40%) · ring labels = supporting
- sfx: whoosh-soft, tick
Adapt: keep the count-up-ring signature; …
Scene 1 (0.0–1.2s): … Scene 2 (1.2–3.4s): … Scene 3 (3.4–5.0s): …
```

**SCRIPT.md** (`script-format.md`): header `**Voice:**`, `**Voice settings:**`, `**Voice direction:**`; then `## Line N — <label> (Frame N)` with `**Time:**` (guide only), `**Delivery:**`, and an **indented block = the only text fed to TTS**. Silent frames are omitted. "Real per-word timing replaces the `**Time:**` guides."

**audio_meta.json** (consumed by `captions.mjs` / `assemble-index.mjs`, frame-keyed): `{ bgm:{path,volume,query,duration_s}|null, bgm_pending, voices:[{frame, path, duration_s, words:[{id,text,start,end}]}], sfx:[{frame,file,offset_s,duration_s,volume}] }` — word times are **frame-relative**, one voice file per frame. This is the seam where a non-HeyGen TTS (our Vietnamese engine) plugs in: emit this shape and every downstream script works unchanged.

**shot-plan.json** (motion-graphics IR, `shot-plan-ir.md`) — the single Director→Builder contract:
```jsonc
{ "category": "kinetic-type|stat|charts|logo-reveal|lower-thirds|webpage|news|tweet|asset-fusion",
  "duration_s": 6, "fps": 30, "canvas": {"w":1080,"h":1920,"aspect":"9:16"},
  "style": "…", "palette": ["#…"] /* or "derive-from-asset" */, "font": "<HF embed-list font>",
  "beats": [12,37], "export": "mp4|alpha-overlay",
  "asset_needs": [{ "role":"hero","kind":"image|icon|logo|svg|news|web|tweet","query":"…","source":"…","treatment":"cutout|recolor|vectorize|none"}],
  "block": "<catalog id>", "customize": {…},
  "content": { /* kinetic-type: scenes[] {id,start,end,text,emphasis_words[],emotion,motion,beats[]} */ } }
```
Invariants: "`scenes` (if present) partition `[0, duration_s]` with no gaps/overlaps · empty `asset_needs` ⇒ Step 2 (source) is skipped · a named `block` ⇒ the Builder reuses + customizes it". This IR is the right model for **one beat** of a short (a hook sting, a stat hit) — and a good template for a per-frame JSON our build scripts can validate.

**talking-head-recut `storyboard.json`** (cards: `id, intent, startSec, endSec, accentIndex 0–4, zone fullscreen|whiteboard-area|lower-third|side-panel|video-overlay, contentHints{kicker,title,detail}`) and **music-to-video groups** (template | free_design | asset per group, anchors from `audiomap.json`) are the two other plan shapes; both reinforce "plan = WHAT, worker = HOW — never write millisecond tweens into the storyboard" (music-to-video planning.md).

### 1.4 What an autonomous agent may run end-to-end

`brief-contract.md` § 1 gate table:

| Gate | Collaborative | Autonomous |
|---|---|---|
| Preference (preset, voice, caption identity) | ask | "Decide and state the choice with a one-line reason" |
| Checkpoint (plan, sketches, pre-render review) | ask and wait | "Post the same summary, then continue" |
| Quality (lint, check, workflow verification) | stop on errors | **stop on errors** |
| Routing ambiguity | resolve explicitly | same |
| Credentials unavailable | wait | continue through offline provider |

"Autonomous mode never silently drops a required capability… surface the blocker." "Rendering remains user-gated in both modes." "Autonomous is not silent": every delivery names the artifact, actual duration, and a contact sheet at scene midpoints.

Implication for a daily batch pipeline: everything through Verify is agent-runnable. The one official human gate is render approval. For unattended batch production our director must **replace** that gate with an explicit, recorded policy (e.g. channel profile `render_policy: auto_after_qa`) plus stronger automated QA, and say so in the delivery note — never silently skip it.

---

## 2. How the official workflows fight monotony and the "template look"

### 2.1 Divergence before convergence — the pitch round (`pitch-round.md`)
- Runs for unformed requests; **also in autonomous runs, internally** ("An autonomous run is where the median is most dangerous — no one is present to say 'this looks like every other video,' so the gate has to say it").
- Four questions first: what does the **subject** look like; what does the **target emotion** look like as a frame; what does the **playback surface** demand ("a feed fights for its first second; a story is vertical and fast"); what does **every other video on this subject** look like ("That is the anti-pattern").
- Five concepts, one per path: subject's world · emotion · audience (meet or break) · anti-pattern inverted · unusual format ("a letter, a countdown, a recipe, a front page, a map").
- **Tail constraint: "at least two of the five must sit below 0.10"** estimated probability; if all clear 0.10 "every pitch is the median — start over."
- **Silhouette check**: "sketch each concept's major elements as rough bounding boxes; two concepts with the same silhouette are one concept, so replace one."
- Autonomous heads-up names the chosen direction, the machinery it rides, and "the most typical direction deliberately left behind."
- Capability-naming discipline: "a capability that would fit all five pitches is decoration; name it only where this concept leans on it."

### 2.2 Design-system variety
- 13 shipped `frame-presets/` (each `FRAME.md` + `caption-skin.html` + `frame-showcase.html`); users pick **by eye**, never from names; `build-frame.mjs` remixes brand colors/fonts by role.
- Design picker (`design-picker.md`): 4–8 mood boards that "tell a different STORY", 5–6 palettes ("Every palette must be visually distinct at swatch size… If two palettes share the same background lightness AND a similar accent hue, cut one"), 5–6 type pairings — **must run the font-discovery script** because otherwise "You will otherwise reach for the same 8 fonts every time (Bricolage Grotesque, Instrument Serif, Fraunces, Archivo Black, DM Serif Display, Space Grotesk, Fredoka)".
- `story-spine.md` § 4: visuals trace to the source — "if the prop could appear unchanged in another product's video, it didn't come from the source."

### 2.3 Storyboard / shot-sequence variety rules (numbers)
- **Framings**: "Use **≥3 different framings per video** so it doesn't read as one repeated template; never the same framing twice in a row" (faceless `visual-design.md`). Portrait-safe framings: Centered, Layered Depth, Full-Width Strip (stacked band), vertical Rule-of-Thirds; avoid wide split/triptych → stacked equivalents.
- **Blueprints**: "Vary the shapes across the video. Reaching for the same blueprint every beat re-creates the sameness this exists to avoid. `kinetic-type-beats` is the workhorse (6 roles) — lean on it, but not everywhere" (product-launch story-design). 22 blueprints, each with a named **signature move** that may never be dropped (Reproduce / Adapt / Compose).
- **Transitions**: "Pick 2–3 transition types for the whole video and repeat them. Frame 1 uses `cut`." Registry: `cut | crossfade | blur-crossfade | push-slide L/R/U/D | zoom-through | squeeze`. Beat-direction: a 5–7-beat reel "usually wants 1–2 shader transitions… too many flatten their impact."
- **Rhythm declared up front**: "Name the pattern — fast-fast-SLOW-fast-SHADER-hold — before implementing"; "Derive the rhythm from the storyboard and the brand, not from a lookup."
- **Held frame**: storyboard-recipe "allocate one beat on purpose where nothing moves and the line lands"; visual-design: "Place held beats deliberately for rhythm so the video isn't uniformly busy."
- **Two named failure modes** in every Video direction negative list: **slideshow** ("front-load then freeze") and **screensaver** ("everything floating independently").
- **Per-beat bans**: storyboard-recipe "At least one explicit 'no …' per beat that could go generic."
- **Hook variety**: narration.md "Vary the hook type — don't default to a stat every time"; 9 hook strategies (§4).
- **Motion doctrine** (faceless motion-language Part 2): smooth `power3` over bouncy; reveal each piece on its VO cue across the back ~50%; "I'd rather have NO motion than BAD motion"; velocity-matched internal seams.
- **Every element gets a verb** (beat-direction): "If you can't name the verb, the element is not yet designed."
- **Registry search before hand-building any named look**: `npx hyperframes catalog --query "<look>" --json` (~400 items; needs nothing installed) — stated in faceless Step 4, general-video, motion-graphics, music-to-video.
- **Motion-graphics heuristics**: "Hook lands fast (~first 0.5s). One dominant motif. Pattern-interrupt if the piece runs >~2.5s (change exactly one thing)… a key element stays readable ≥~0.3s."
- **Embedded captions**: "embed is the scarce, earned peak… ≤1 hero per block… ≥ a beat of air between hero windows (the compiler warns under 0.6s)" — scarcity as anti-monotony.

### 2.4 What is missing officially (we must add it)
The official skills enforce variety **within one video**. Nothing tracks variety **across videos of one channel**. For a channel producing daily shorts, the director must add a cross-video ledger (hook type, structure, blueprints, framings, transitions, palette accent, music track, opening silhouette) and a rotation rule (e.g. no hook type / opening blueprint / signature layout repeated within the last N shorts of that channel). The pitch round's "anti-pattern" question should be fed with the channel's own last N storyboards, not only "other videos on this subject".

---

## 3. Subagent / frame-worker dispatch patterns

### 3.1 The harness-neutral contract (`subagent-dispatch.md`)
- `DISPATCH(role_file, dispatch_context)`: prompt = full role file + `## Dispatch context` "copied verbatim (never digested or paraphrased)"; "never rely on the child seeing your conversation, memory, or skills — the prompt and the files on disk are its entire world."
- **WAIT = artifact on disk**, never the completion notification; missing artifact ⇒ "re-dispatch it once with the same prompt before surfacing an error."
- Concurrency cap "reduces parallelism, not work": waves of cap size; "never drop scenes, never merge scenes into one worker to fit the cap" (the general-video exception below is deliberate batching, not cap-fitting).
- Fallback ladder: native delegation → headless CLI workers on shared FS → inline serial.

### 3.2 Packets: bounded, self-contained work orders (`frame-packets-core.mjs`)
- `frame-packets.mjs` splits `STORYBOARD.md` by `## Frame` headings; frame_id = basename of `src`; inlines the frame's exact block + the `blueprint:` body (`hyperframes-animation/blueprints/<id>.md`; `(Reproduce)/(Adapt)` qualifier stripped; unknown id = hard error) + every cited rule recipe (explicit `rules:` field or any rule id mentioned in the block) + `designTruthLine` (frame.md). **Packet hard limit 48,000 bytes.**
- `_role.md` = `frame-worker-core.md` + workflow delta, concatenated verbatim. Workflow-specific hooks: `designTruthLine`, `validateFrame`, `extraSections` (pr-to-video uses these for code-frame contracts).

### 3.3 The director↔builder contract (`frame-worker-core.md`)
Worker **decides nothing upstream**: not what is said, not duration ("Fixed upstream; never change it"), not transitions between frames ("the root transition IS the exit"), not audio ("No `<audio>` element"), not tokens (from frame.md; "never lift a word… out of `frame.md` as your copy"), not which motions/assets exist, never opens `STORYBOARD.md`. Output = exactly one `<template>…</template>` file at `compositions/frames/<frame_id>.html`, "Writing your assigned file(s)… is your terminal action". Must-follow constraints: caption keep-out (content above `0.83 × height`, i.e. **≤1600 px on 1920-tall**, even when captions disabled); fill the area (portrait hero at ~0.2–0.35 × height); visible text is short motion-graphics copy, never narration; reveal across full duration, never front-load; prefix ids with `<frame_id>-`; fonts only from shipped files ("Never name a font that has no file" — critical for Vietnamese diacritics). Self-check against lint codes (`missing_template_wrapper`, `subcomposition_root_styled_by_class`, `timeline_not_paused`, `gsap_css_transform_conflict`, `font_family_without_font_face`, `exit_animation_on_non_final_scene`…). Workers **do not run the CLI** (lint on an unassembled frame is "a false green"); the orchestrator runs lint/check after assembly and **re-dispatches with the findings** ("treat each as a hard constraint").

general-video delta adds a **motion sidecar** `compositions/<frame_id>.motion.json` `{scene, duration_s, rules[], exit{vector, still_moving}, entry{vector, from_rest}}` — measured, not planned values — so seams can be stamped/verified downstream.

### 3.4 When dispatch is worth it — the key number
general-video: "**Dispatch pays for itself only at scale**… a film of up to ~6 short scenes builds FASTER inline… (measured: 5 short scenes ≈ 9 min inline vs ≈ 21 min packetized). Fan out only when the plan exceeds that… give each worker **2–3 scenes**, not one, and spawn **all workers in a single wave** (a second wave nearly doubles the window)." faceless/product/pr still dispatch one worker per frame. motion-graphics uses **role** subagents instead (Director Part 1 → Source → Director Part 2 → Builder → Finalize/repair with "one in-place repair pass"; escalate only when "fundamentally wrong").

### 3.5 Other verification gates worth copying
- music-to-video `validate-plan.mjs`: machine check of the PLAN before any build — HARD: duration sum, frames tile timeline gap-free, every frame has `src` + positive duration, no unfilled skeleton frames; WARN: group shape. "Fix every ✗."
- faceless `transitions.mjs verify`; `assemble-index` reports cut length vs storyboard `duration`.
- embedded-captions: timing within 80 ms of transcript, each caption ≥0.5 s, group windows envelop their words, no time+space overlaps, face never 100% covered; "Visual QA — preview BEFORE you render" (~2 s/frame previews).
- general-video Done list: `check` passes, design adherence reviewed (`design-adherence.md`), contrast resolved, midpoint snapshots inspected, `animation-map.mjs` reviewed for multi-scene work.
- motion-graphics `grounding/PROTOCOL.md`: never eyeball pixel coordinates — grid-strip localization (9×9 → crop → 6×6 → `mark` + verify); measured center error 6.5% → 2.3%.
- Known false positive to whitelist: `text_box_overflow` of 1–4 px on caption words.

### 3.6 What to copy for a multi-channel short pipeline
1. Plan file as the dispatch unit (one `## Frame` block per beat, `src` declared) **even when nobody reviews it** (general-video: "The block is the dispatch unit; the storyboard sheet is only the review surface").
2. Packet builder reuse: call `hyperframes/scripts/lib/frame-packets-core.mjs` with our own delta (channel rules, VN font paths, our caption band) via `designTruthLine` / `extraSections`; keep the 48 KB cap.
3. For 25–40 s shorts (5–8 frames): **build inline, or 2–3 workers with 2–3 frames each in one wave** — never one worker per frame.
4. Workers write files only; orchestrator owns STORYBOARD state, audio, captions, assembly, CLI, re-dispatch with lint findings.
5. A deterministic plan validator (our analogue of `validate-plan.mjs`) before build, and a post-assembly QA bundle (lint → check → midpoint contact sheet → animation map → our channel checks).

---

## 4. Story design for narrated explainers, adapted to 25–40 s shorts

### 4.1 Official doctrine (faceless story-design + story-spine + narration)
- "An article is an information dump. A video is a guided act of understanding." Do not follow source order — "The single most common failure is paraphrasing the article in order."
- Extract: audience · gap/stakes · **thesis** (one line) · spine (3–6 ideas) · evidence · landing.
- One structure only: `concept-explainer` | `how-to-process` | `listicle` | `story-explainer` (compound allowed only when named, e.g. "concept-explainer with process").
- Shared `type` enum, repurposed: hook / pain_point / product_intro (name the idea) / feature_showcase (mechanism, step, item) / benefit_highlight (so-what) / social_proof (evidence, example, number) / branding (thesis, takeaway) / cta.
- Every frame: named `persuasion` technique (Make-concrete, Reveal-in-order, Contrast, Structure, Evidence, Memory & landing families), a specific `beat` emotion (valley → pivot → build → resolution), `narrativeRole`, `keyMessage`.
- **Hook strategies (9)**: shocking statistic · rhetorical question · counterintuitive claim · pain validation · visceral metaphor · concept announcement · direct address · imagine/scenario · stakes/consequence. "Do not open with a generic definition."
- **story-spine**: hook in viewer outcome language (no source-internal vocabulary); **thesis lands by beat 2**; delete-evidence self-check; storyboard presented as "This video tells [audience] that [message]" + frame table (Frame · Beat · On screen · Why).
- Script lines: "1–2 sentences per spoken frame; usually 6–20 words"; **write each line as discrete cues** ("First the snowball — then the hill — then the speed") because reveals are timed to named words. Silent frames are allowed.
- Pace: narration.md "2.5 words per second… 30s = ~75 words"; "The script should feel SHORTER than the video." Write numbers as they should be spoken; "The visual can show the exact figure while the voice rounds it."
- Body is a sequence (3–6 frames on a consistent stage, one repeated seam type); a genuine transform stays inside one frame.

### 4.2 Timing numbers from the official skills
- Hook window 3–5 s (faceless/product); motion-graphics "Hook lands fast (~first 0.5s)"; storyboard-recipe "First visible motion within 0.2 s of the beat starting."
- Beat length (storyboard-recipe): **1.5–3.5 s**; "A beat that must be read gets ~3 s; a beat that only hands off gets 1.5–2 s; a line of 5–7 words gets 2–2.5 s."
- Blueprint durations are mostly 3–12 s (titlecard-reveal 3–5 s; kinetic-type-beats 3.0–12.9 s) — a frame may contain several Scene windows.
- talking-head-recut density: <60 s reels → 6–8 s per card base pace, ×0.7 for high density; "a static one-liner gets boring past 8s".
- music-to-video: a readable word holds ≥1 beat; held <1 beat it is texture.
- Readability: key element readable ≥~0.3 s (motion-graphics); each caption ≥0.5 s (embedded-captions).

### 4.3 Captions band
- Faceless/product/pr caption pill owns the **bottom ~17%**; all frame content in the top ~83% (≤1600 px on 1920); centered hero at y ≈ 0.42 × H (≈806 px portrait). Background layers may stay full-bleed.
- `captions.mjs` grouping: split on silence gap ≥0.18 s; group lingers 0.12 s after last word; words per group from local density — **>3.5 w/s → 2 words, >2.5 → 3, else 4**; skin from `.hyperframes/caption-skin.html` with frame.md tokens; skip legally when no words.
- embedded-captions grouping: break at pause ≥500 ms, sentence end, strong comma + ≥250 ms, discourse resets; **≤6 words or 2.5 s**; min 2 words, min 0.5 s; `in = first.start − 0.08`, `out = min(next.in − 0.05, last.end + 0.6)`; ≤1 hero/"crown" group.
- Studio safe zones: title-safe 80% (10% margins), action-safe 90%; one caption track (`data-track-kind="captions"`).
- Not in the official docs (our own knowledge, verify per platform): YouTube Shorts overlays UI on the right edge and bottom (title/channel/buttons), so the caption band should sit above the very bottom and avoid the right ~12%.

### 4.4 Adapted beat template for 25–40 s Vietnamese shorts (proposal)
Assumptions: Vietnamese TTS rate must be measured per voice (syllable-timed; English's 2.5 w/s does not transfer). Budget words from the channel's measured syllables/second × target seconds × ~0.85 (the "script shorter than video" margin).

| Beat | type | Time (30 s example) | Rule |
|---|---|---|---|
| 1 Hook | hook | 0–2.5 s | one named hook strategy; first motion ≤0.2 s; outcome language; picture carries the claim without audio |
| 2 Thesis/turn | pain_point or product_intro | 2.5–6 s | the `message` lands here (story-spine "by beat 2"); channel rule e.g. BUD/FS "câu 2 không định nghĩa" fits this slot |
| 3–5 Body | feature_showcase / social_proof / benefit_highlight | 6–24 s, 3 frames of ~4–6 s each, each 2–3 Scene windows | consistent stage + one seam type; one key reveal per spoken cue; ≥3 framings across the video |
| 6 Held beat | branding | ~24–27 s | deliberate stillness, the line lands |
| 7 Landing/CTA | cta or callback | 27–30 s | callback to hook image; no generic "subscribe" unless channel profile requires |

Rules carried into the director: 5–8 frames total; frame 1 `cut`; 2–3 transition types; one held frame; ≥1 "no …" ban per generic-prone beat; every on-screen word short (never the narration sentence — captions already carry it); numbers spelled for TTS.

---

## 5. Capability map — what each official skill gives a shorts director, and when to load it

| Skill | What it gives us for shorts | When the director loads / delegates |
|---|---|---|
| `hyperframes` | Routing table, BRIEF/STORYBOARD/SCRIPT formats, brief contract (mode/gates), pitch round, review loop, production loop, dispatch adapter, frame-worker core + packet lib | Phase 0 (once per skill version: copy contracts), plan and dispatch phases; never route through its interview in batch mode — write BRIEF.md directly |
| `hyperframes-core` | Composition contract: `data-*` timing, `class="clip"`, sub-compositions, tracks, determinism, variables/media | Any HTML authoring or assembly change; frame-worker delta restates the essentials |
| `hyperframes-animation` | 22 blueprints + role→blueprint menu, rules index + recipe bodies (inlined into packets), transitions catalog, `animation-map.mjs`, 24 text effects, runtime adapters (Three.js etc.) | Storyboard (blueprint tag), visual design (rule ids), packet build, multi-scene QA |
| `hyperframes-keyframes` | Seek-safe punch-in/zoom/Ken Burns/camera, SVG draw/morph, masks, `hyperframes keyframes` diagnostics | When a frame needs a camera move or photo push (stock images) |
| `hyperframes-creative` | frame presets + showcases, design-spec resolution, design picker, house-style, typography (font discovery), story-spine, beat-direction, narration, storyboard-recipe (`storyboard.html`), prompt-expansion, design-adherence, data-in-motion | Channel onboarding (design system), story phase, final design-adherence check |
| `hyperframes-cli` | init, catalog, add, lint, check, snapshot (contact sheet), preview, render, batch render, tts (Kokoro), transcribe, remove-background, publish, upgrade/pin probe | Verify/render phases; render diagnostics; batch rendering |
| `hyperframes-audio` | VO carve of the BGM bed (`carve.mjs`), fades, ducking, FX chains, submix bus | After assembly whenever BGM plays under narration ("a duck alone is not a finished mix") |
| `hyperframes-studio` | One caption track, one element kind per track, every scene a sub-composition, title-safe 80% | Assembly conventions; manual review in Studio |
| `hyperframes-registry` | ~400 blocks/components (caption-*, charts, maps, overlays, shader transitions, grain/vignette) via `catalog --query` and `add` | Visual-design phase before inventing any named look; install **before** parallel work |
| `media-use` | `resolve` BGM/SFX/images/icons/logos with ledger; TTS/transcription engine; remove-bg; grading/treatments; prefs + recipes memory | Asset phase; photo treatment; per-channel memory (prefs/recipes); transcription to time an external TTS |
| `faceless-explainer` | **The genre lens and machinery for our case**: story-design (structures, hooks, persuasion, beats), visual-design (shot sequence, Video direction, layout vocab, portrait rules), motion-language, cut-catalog; scripts `build-frame`, `audio` (meta shape, `sync-durations`), `captions`, `assemble-index`, `transitions`, `frame-packets` | Default backbone for every narrated short; borrow references verbatim, reuse scripts via an audio_meta adapter |
| `general-video` | Freeform/companion host, plan-as-dispatch-unit rule, inline-vs-dispatch economics, motion sidecar, Done checklist | Non-standard shorts (montage, mixed footage), and as the source of the dispatch-economics rule |
| `motion-graphics` | Director/Builder/Finalize role split, shot-plan IR, category modules (kinetic-type, stat, charts, maps incl. baked basemap, news highlight, tweet, asset-fusion), grounding protocol | Unnarrated sub-10 s stings/beats inside a short (hook slam, stat hit, map zoom); news-article highlight beats; locating objects in photos |
| `music-to-video` | Deterministic beat grid (`analyze-beatgrid.py` → `audiomap.json`), template/primitive catalogs, plan validator | Music-only shorts; or to align cuts/accents to the BGM of a narrated short |
| `slideshow` | Navigable deck with presenter mode (not MP4) | Not for shorts; only if a channel wants an interactive explainer page |
| `embedded-captions` | 35 caption identities, rail+embed model, grouping rules, matte occlusion, timing/overflow validators | Only for shorts built on real talking-head footage; borrow its grouping/timing rules for our caption band |
| `talking-head-recut` | Card storyboard (zones), card-count formula, overlay layouts | Shorts cut from an existing interview/podcast clip |
| `product-launch-video` | Website capture, brand-token remix, product story-design + script bank by blueprint role | Sponsored/product shorts; borrow the "script bank by role" idea for our own hook bank |
| `pr-to-video` | PR ingest, code vocabulary, frame-contract validation hooks | Dev-channel shorts only; also an example of `validateFrame`/`extraSections` packet hooks |
| `remotion-to-hyperframes` | Remotion→HF port + SSIM eval harness | Only if migrating old Remotion templates |
| `figma` | Assets, tokens, components, frames-as-motion-states from Figma | Channel branding kept in Figma; one-time import into the channel's frame.md/assets |

---

## 6. Recommendations — architecture of a reusable "short director" skill

### 6.1 Principles
1. **Thin orchestrator, borrowed contracts.** The director owns phases, artifacts and gates; craft knowledge is loaded from official skills by path (faceless references, blueprints-index, frame-worker-core). Never copy their prose into our skill — link it, so `npx hyperframes skills update` keeps it current.
2. **Official artifacts, unchanged formats.** BRIEF.md / STORYBOARD.md / SCRIPT.md / frame.md / audio_meta.json in the official shapes, so official scripts (packets, captions, assemble, transitions) and Studio work on our projects.
3. **Autonomous by default, with receipts.** Batch shorts run `flow: automation, storyboard: no`. Every absorbed decision is logged as a one-line receipt in BRIEF.md `## Notes` and in the delivery note.
4. **Channel = data, not code.** Everything channel-specific lives in a channel folder the director reads; the skill text stays topic-agnostic.
5. **Cross-video variety is a gate**, not advice (the gap noted in §2.4).

### 6.2 Per-channel store (proposal: `channels/<id>/`)
- `profile.yaml`: language, voice id + measured syllables/sec, duration window (e.g. 25–40 s; a channel may narrow it), aspect, render policy, caption identity/skin, BGM mood list, SFX palette, CTA policy, upload metadata defaults, naming rules and forbidden vocabulary (e.g. FS zodiac must use chi names Tý…Hợi), fact-check sources, sensitive-topic rules.
- `frame.md` + `caption-skin.html` (derived once from a preset via `build-frame.mjs`, then frozen); `fonts/` with Vietnamese-capable `.woff2` files (frame-worker-core forbids fonts without files).
- `hook_bank.md` and `structure_bank.md`: the channel's own proven hook lines / structures by `type` (analogue of product-launch's "script bank by role"), seeded from analytics winners.
- `ledger.jsonl`: one record per published short — topic, message, hook strategy, structure, per-frame blueprint + framing + transition, palette accent, BGM id, opening silhouette, duration, later retention stats. Used by the variety gate and the pitch round's "anti-pattern" question.
- `recipes/` via `media-use recipe.mjs freeze` per proven format (e.g. "year-table short", "story short"), so a run can start from a frozen skeleton.

### 6.3 Phases, artifacts, gates
| Phase | Does | Artifact | Gate (blocking) |
|---|---|---|---|
| P0 Load | read channel profile, ledger tail (last N=10–20), recipes; probe CLI pin | in-memory context | profile valid; fonts exist |
| P1 Brief | write BRIEF.md from topic queue item; derive aspect 1080x1920, language vi | `BRIEF.md` | message is one sentence |
| P2 Pitch (internal) | pitch gate with the ledger as the anti-pattern; ≥2 of 5 concepts <0.10; silhouette check; pick | `## Intent` + receipt naming the typical direction left behind | novelty vs ledger (no repeated hook type / opening blueprint / silhouette within last N) |
| P3 Script | structure + hook strategy + beats; Vietnamese line budget; spoken-number rewriting; fact check | `SCRIPT.md`, draft `STORYBOARD.md` | word/syllable budget fits window; thesis by beat 2; channel lexical rules; facts sourced |
| P4 Shot design | Video direction block (palette roles, motion grammar, rhythm string, held frame, bans incl. slideshow/screensaver); per frame blueprint (Reproduce/Adapt/Compose), focal/roles, Scene windows on VO cues, sfx; registry search for named looks | enriched `STORYBOARD.md` | **plan validator**: 5–8 frames, durations sum in window, ≥3 framings, no framing twice in a row, 2–3 transition types, frame 1 `cut`, one held frame, every blueprint id exists, no adjacent duplicate blueprint, content above caption band |
| P5 Audio | Vietnamese TTS per frame (or one take split at frame boundaries), word timings (own aligner or `media-use transcribe`), BGM resolve, carve | `audio_meta.json` in faceless shape | durations synced into storyboard mechanically |
| P6 Build | registry `add` first; packets via `frame-packets-core.mjs` + our delta; inline build or 2–3 workers × 2–3 frames, single wave | `compositions/frames/*.html` | artifact on disk; re-dispatch once on missing file |
| P7 Assemble | `captions.mjs`, `assemble-index.mjs`, `transitions.mjs inject/verify` (borrowed) | `index.html`, `captions.html` | assembly length vs target reported |
| P8 QA | `lint` → `check` → `snapshot --at <frame-midpoints>` (one contact sheet) → `animation-map.mjs` → design adherence → channel checks (VN glyph coverage, banned words on screen, caption band, BGM carve) | QA report + contact sheet | quality gates block in all modes; one repair pass, then escalate |
| P9 Approve | collaborative: "render now, or what changes?"; batch: apply `render_policy` from profile and state it | decision receipt | never silent |
| P10 Render + record | `render --quality high`; verify duration/audio; append ledger; offer/name recipe freeze | `renders/video.mp4`, ledger row | output exists, duration in window |

### 6.4 Decision points inside the director (internal routing)
- Narrated, invented visuals (default) → faceless-explainer lens + our build.
- A beat that is an unnarrated stinger (stat slam, map zoom, news headline highlight) → author that frame with motion-graphics category module + shot-plan IR conventions.
- Real footage of a speaker → talking-head-recut or embedded-captions instead.
- Music-driven montage → music-to-video beat grid.
- Named look/effect → registry search before authoring.
- More than ~6 heavy frames → dispatch workers; otherwise inline.

### 6.5 Things to deliberately deviate from (and document)
- No intent interview in batch: BRIEF.md is generated from the topic queue (allowed: the contract only requires a confirmed brief; in batch, confirmation = channel policy).
- Render gate replaced by channel `render_policy` + stricter automated QA; human review happens on the schedule/upload side.
- Official TTS (HeyGen/Kokoro) replaced by the Vietnamese engine via an `audio_meta.json` adapter; Kokoro voices are not Vietnamese.
- One-worker-per-frame (faceless) replaced by general-video's measured economics (inline / batched single wave).
- Add the cross-video ledger + variety gate that no official skill has.
