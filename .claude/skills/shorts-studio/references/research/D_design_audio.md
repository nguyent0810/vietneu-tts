# D. Multi-theme design system + captions + audio for the reusable 9:16 narrated Shorts engine

Scope: one engine and many channels. Today that is FS (phong thuỷ / con giáp) and BUD (Phật giáo). Later it adds history, science, finance, health and legal explainers. All on-screen text is Vietnamese with heavy diacritics.

This report builds on two earlier ones and does not repeat them:
- `hf_visual_composition.md`: the layout patterns P1–P15, the treatment recipe table, transitions, and registry blocks.
- `hf_kinetic_type.md`: the kinetic techniques T1–T15, the Vietnamese split/mask rules, and the GSAP snippets.

When a theme lists "devices" below, it refers to those IDs.

Sources: `~/.claude/skills/{hyperframes-creative,media-use,hyperframes-audio,embedded-captions}`, read in full. These are the SKILL files, every reference file, all 9 palettes, and all 13 `frame-presets/*/FRAME.md` plus their `caption-skin.html` files.

**How claims are tagged:**
- **(doc)** means the skill text says it.
- **(verified)** means I checked it against a live artifact: the Google Fonts metadata, the HF 0.8.75 bundle, or a CLI dry-run.
- **(own)** means my own engineering judgement. Treat it as a proposal.

---

## 0. Key findings (read first)

1. **The fonts pre-bundled in HF 0.8.75 are Latin-only. (verified)**
   - I decoded every `EMBEDDED_FONT_DATA` entry in `~/.npm/_npx/56de3f8b9956197b/node_modules/hyperframes/dist/cli.js` with fontTools. All of them lack every one of 45 Vietnamese test glyphs (Đ Ơ Ư Ầ Ẫ Ỗ Ữ Ự Ợ Ặ Ộ …). That covers Inter, Montserrat, Oswald, League Gothic, Archivo Black, Playfair Display, EB Garamond, JetBrains Mono, IBM Plex Mono, Space Mono, Source Code Pro, Roboto, Lato, Poppins, Outfit, Nunito, Open Sans and Noto Sans JP.
   - The compiler (`buildFontFaceCss`) emits the bundled face with `BUNDLED_SUBSET_UNICODE_RANGE`. It then **fetches the remaining subsets from Google Fonts at build time** and adds them. Vietnamese therefore renders only when that fetch succeeds or `~/.cache/hyperframes/fonts/<slug>/` already holds it. That cache currently has be-vietnam-pro, jetbrains-mono, oswald, playfair-display and noto-serif-sc.
   - The typography doc says the fetch is "fail-closed in distributed/cloud renders".
   - **Rule:** for deterministic offline renders, every theme ships its own `@font-face` woff2 files covering the `vietnamese` range. The compiler skips any family that already has an `@font-face` (`extractExistingFontFaces`).
2. **Several preset display faces have no `vietnamese` subset on Google Fonts. (verified against `fonts.google.com/metadata/fonts`, 520 of 1950 families have it)**
   - **No Vietnamese:** Shrikhand and Libre Baskerville (bold-poster), Instrument Serif (biennale-yellow), Bebas Neue (coral), DM Mono (cobalt-grid), Bodoni Moda (capsule), Fredoka (daisy-days) and Archivo Black (creative-mode).
   - **Vietnamese OK:** Space Grotesk, Archivo, JetBrains Mono, Inter, Source Serif 4, Playfair Display, Newsreader, Hanken Grotesk, Barlow, IBM Plex Mono, Quicksand, EB Garamond.
   - So editorial-forest and broadside work unchanged. Cartesian works too, through the Google supplement.
   - Substitutes are in §2.0.
3. **Every frame preset ships a `caption-skin.html` with a fixed token contract.**
   - The tokens are `--cap-ink`, `--cap-canvas`, `--cap-accent`, `--cap-accent-2`, `--font-display`, `--font-body`, `--cap-band-top` and `--cap-band-height`.
   - The hooks are `.caption-group`, `.caption-word`, `.is-active` and `.is-spoken`.
   - The timing is seek-safe `gsap.set({className})`.
   - This is the right architecture for theming captions: one skin per theme, with tokens injected from the theme (§4.5).
4. **All 22 media-treatment payloads in §6 pass `hyperframes@0.8.75 media-treatment --apply --dry-run`. (verified)**
   - The CLI rejects unknown keys. A negative test with `bogusKey` failed as expected.
   - This is schema validation only. It is not a visual check.
5. **The bundled SFX library is 19 mp3 files, licensed under Pixabay (commercial use OK, no attribution needed). (verified)** `sfx.md` says "21-file", but it counts `CREDITS.md` and `manifest.json`.

---

## 1. THEME system spec

A **theme** is a `frame.md`-shaped spec. The YAML frontmatter is normative: exact hex values, font families and weights (`design-spec.md`). The prose is context.

The docs' consumption contract (`video-composition.md`):

> Strict from the design spec: hex values (including background color), font families, weight relationships, Do's and Don'ts … Adapt for video: type sizes, spacing, decorative opacity, border weight, component treatments.

Presets put it as "atoms are sacred · composition is free · numbers come from the script."

### 1.1 Schema *(own structure; every field maps to a doc rule cited in 1.2)*

```yaml
id: tet-poster                    # stable key; channel registry maps channel -> [theme ids]
version: 1
base: { preset: bold-poster, palette: jewel-rich, style: "Maximalist Type" }  # provenance
register: "populist Tết poster, printed, loud-but-disciplined"
fits: [fs.zodiac-year, fs.taboo, fs.tet]
colors:                           # EVERY hex the composition may use (design-adherence checks this)
  ground:   "#F5F2EF"             # paper / canvas (one per video; panels below are sanctioned inversions)
  ground-2: "#FFFFFF"             # alternate stripe / card
  ink:      "#1C1410"             # all body text + rules
  ink-soft: "#5A4A40"             # optional, secondary text (≥4.5:1 on ground)
  accent:   "#C32F27"             # THE one accent: numerals, active caption word, progress bar
  accent-2: "#780116"             # statement panel / environment (not a second text accent)
  glow:     "#F7B538"             # atmosphere only: bloom / foil rule, 15–25% opacity, never text
  panels:   { accent: "#C32F27", dark: "#1C1410" }   # full-bleed statement surfaces allowed
type:
  display: { family: "Sansita Swashed", weights: [800, 900], vi: verified, role: "hero, numerals" }
  body:    { family: "Spectral", weights: [400, "400i"], vi: verified }
  mono:    { family: "Space Grotesk", weights: [500, 600], vi: verified, role: "chrome/eyebrows" }
  rules: { caps_tracking_max: "-0.02em", caps_line_height_min: 1.18, legibility_floor_px: 44 }
  google_css: "https://fonts.googleapis.com/css2?family=..."   # dev only; ship @font-face woff2 for render
texture:
  grain: { via: "media details.grain | grain-field block", amount: 0.06 }
  pattern: { kind: hatch-45, opacity: 0.06 }       # or graph-grid / hairline / bloom / ghost-type
  ghost_type_opacity: [0.12, 0.25]
motion:
  energy: high                    # calm | moderate | high
  ease: { entry: "expo.out", exit: "power3.in", move: "power2.inOut", ambient: "sine.inOut", accent: "back.out(1.6)" }
  dur:  { entrance: 0.35, exit: 0.2, hold: 1.4, transition: 0.4, slowest_over_fastest: ">=3" }
  stagger_total_max: 0.5
  seams: { primary: [hard-cut, whip-pan, vertical-push], accent: [ridged-burn], max_shader_per_video: 1 }
  ambient: [slow-zoom, hatch-drift, bloom-breathe]   # pick a different one per scene
  signature_moves: ["tilt -6° numeral slam", "red panel surface inversion"]
media: { base: "<treatment json>", alt: "<poster treatment json>", reveal: "--hf-color-grading-dither 0→1" }
captions: { skin: "caption-skin.tet-poster.html", gesture: "active word = accent block, paper glyph",
            font: body|display, case: sentence, grouping: conversational }
sfx: { palette: [impact-bass-1, whoosh-short, pop, gong(repo)], max_per_30s: 7 }
bgm: { query: "...", prompt: "...", bpm: 110, scale: PENTATONIC, carve_strength: 0.8 }
chrome: { progress_bar: accent, pagenum: false, topbar: false }
dont: ["no fifth color", "no rounded corners", "no drop shadow except stacked text-shadow on accent panel"]
```

### 1.2 What the docs say about each field

**Colors**
- "One accent hue. Same background across all scenes." Tint neutrals toward the accent. Avoid pure `#000`/`#fff`. Declare the palette up front, and don't invent colors per element (`house-style.md`).
- "Muted is fine. Flat is not." The accent should run at 15–25% for atmosphere and at full saturation on focal elements. Under ~10% opacity it is invisible (`video-composition.md`).
- "Light canvases work differently than dark … use bolder borders (2px+), stronger structural elements, full-saturation accent hits … need texture … Don't switch to dark — make light cinematic." Avoid full-screen linear gradients on dark grounds because they band under H.264.
- Contrast is WCAG AA, enforced by `hyperframes check`. Text must stay readable with the decoratives removed.
- Adherence (`design-adherence.md`): every hex in the composition must appear in the spec palette.
- Light vs dark choice: "food, wellness, kids → light. Tech, cinema, finance → dark."
- Preset-specific discipline is "sacred": no fifth color in bold-poster; one register per frame in broadside; strictly two colors in cobalt-grid; "two surface tones max (three is loud)" in editorial-forest.

**Typography** (`typography.md`)
- **Pairing:** never pair two sans faces. Cross the boundary (serif + sans, or sans + mono). Use one expressive font per scene.
- **Weight contrast:** extreme. Video needs 300 vs 900.
- **Sizes:** full-screen video: body ≥20px, headlines ≥60px. In-feed (Shorts plays in a feed): body ≥32px, headlines ≥90px, labels ≥24px.
- **Tracking:** display tracking is −0.03 to −0.05em. *(own, from the earlier report)* For heavy-weight Vietnamese capitals, cap tracking at −0.02em and use line-height ≥1.15–1.2.
- **Dark grounds:** step body weight down to ~350, add 0.05–0.1 to line-height, and add +0.01em tracking at display sizes.
- **Banned (monoculture):** Inter, Roboto, Open Sans, Noto Sans, Arimo, Lato, Source Sans, PT Sans, Nunito, Poppins, Outfit, Sora, Playfair Display, Cormorant Garamond, Bodoni Moda, EB Garamond, Cinzel, Prata, Syne. The doc allows a banned font when it is "the perfect thematic match", so each use has to be a deliberate choice.
- **Numbers:** use `font-variant-numeric: tabular-nums` on stacked numbers (year tables, finance).
- **Fit-to-measure** (every preset): cap a block at ≤78cqw. Short phrases take the biggest ramp step, and longer lines step down. The legibility floor is 1.4cqw, which is about 27px on a 1920-wide frame and about **15px at 1080 wide**, so for Shorts use the in-feed floor (≥32px).

**Texture**
- Every scene gets 2–5 background decoratives, and each has slow ambient motion (`house-style.md`).
- Grain on photos is the media `details.grain` setting. Never fake it with CSS or SVG overlays (`media-treatments.md`).
- The earlier report found that `grain-overlay` uses CSS keyframes, which are not seek-safe. Use `grain-field` instead.

**Motion** (`motion-principles.md`, `visual-styles.md`)
- Allow no more than 2 tweens with the same ease per scene. The slowest scene should be 3× slower than the fastest. Vary entry direction.
- Ease direction: `.out` for entering, `.in` for leaving, `.inOut` for moving between positions.
- Each scene has three phases: build (0–30%), breathe (30–70%, one ambient motion) and resolve (70–100%, exits faster than entrances).
- Keep a total stagger under 500ms. Offset the first tween by 0.1–0.3s.
- Transition meaning: crossfade means "this continues", a hard cut means "wake up", a slow dissolve means "drift".
- Use 1–2 shader transitions per piece (the hero reveal and the CTA). More "flatten their impact" (`beat-direction.md`).
- Velocity-match the cut: the exit uses `power2.in`/`power3.in` with a blur ramp, and the entry uses `.out`.
- Easing carries emotion: `expo.out` reads confident, `sine.inOut` dreamy, `elastic.out` playful.
- The visual-styles motion tokens give per-style values: energy, easing (entry/exit/ambient), duration (entrance/hold/transition), atmosphere and transition. Velvet Standard, for example, is `sine.inOut`, 1.2 / 3.0 / 1.5, with cross-warp-morph.

**Media treatment** (`media-treatments.md`)
- Choose one primary intent. Apply one house treatment per video, persisted with the CLI.
- Treatments are whole-media only and Rec.709 only.
- Do not stack effects "to look sophisticated".
- Named bold looks must "read unmistakably".

**Captions**
- Use the caption-skin token contract (finding 3).
- Map style to tone (`captions/authoring.md`): storytelling uses serif 400–500 with a slow fade (`power2.out`, 0.5–0.6s). Hype uses a heavy condensed face with a scale-pop. Calm content groups 4–6 words.

**SFX**
- Keep SFX volume around 0.35 (`sfx.md`).
- Each beat names its SFX cues (`beat-direction.md` "SFX cues").

**BGM**
- One bed per composition (`bgm.md`). Under narration it sits at volume 0.12, about −18 dB.
- When the bed plays under a voice, the carve is mandatory (`hyperframes-audio`).

---

## 2. Theme proposals (14)

### 2.0 Font substitutions for the presets *(verified subset data; glyph-quality confidence noted)*

| Preset | Original face | VN? | Substitute (VN verified) | Why / confidence |
|---|---|---|---|---|
| bold-poster | Shrikhand (display) | ✗ | **Sansita Swashed** 800–900 (closest heavy swash/slab-script); alt **Alfa Slab One**, **Bevan** | Medium on look: Sansita's swashes on stacked caps need a render check |
| bold-poster | Libre Baskerville (body) | ✗ | **Spectral** 400/400i (Production Type), alt **Literata**, **Crimson Pro** | High |
| bold-poster | Space Grotesk (chrome) | ✓ | keep | High |
| biennale-yellow | Instrument Serif | ✗ | **Newsreader** 400/400i, opsz 72 (tight, elegant); alt **Literata** | High |
| biennale-yellow | Archivo, JetBrains Mono | ✓ | keep | High |
| coral | Bebas Neue | ✗ | **Phudu** 700–900 (Vietnamese designer Dương Trần); alt **Vina Sans** (Nguyen Type, 400 only), **Big Shoulders** 800, **League Gothic** (bundled Latin + Google VN) | High for Phudu / Vina Sans (designed in Vietnam) |
| coral | Inter | ✓ (via supplement) | **Be Vietnam Pro** 400/600 (Lâm Bảo; native VN, already in repo) | High |
| cobalt-grid | DM Mono | ✗ | **JetBrains Mono** or **Chivo Mono** | High |
| cobalt-grid | Newsreader, Hanken Grotesk | ✓ | keep | High |
| creative-mode | Archivo Black | ✗ | **Archivo** 900 at `wdth 125` (same family, VN ✓); alt **Dela Gothic One** | High |
| capsule | Bodoni Moda | ✗ | **Libre Bodoni** 700 (VN ✓) | Medium |
| daisy-days | Fredoka | ✗ | **Baloo 2** 800 / **Lemonada** (VN ✓) | Medium (not used in the themes below) |
| editorial-forest | Source Serif 4 + JetBrains Mono | ✓ | keep as-is | High |
| broadside | Barlow + IBM Plex Mono | ✓ | keep as-is | High |
| cartesian | Playfair Display + Inter | ✓ | keep, or **Playfair** (v2, opsz/wdth; not on the banned list) + **Be Vietnam Pro** | High |

**How to verify each face (do it once per theme):**
- Run `document.fonts.check('900 120px "<Family>"','Ữ')` after `document.fonts.ready`.
- Then run `hyperframes snapshot` on a test card reading `ĐỪNG NGỦ QUÊN · Ầ Ẫ Ỗ Ữ Ự Ợ Ặ Ộ · Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi · Bính Ngọ · nghiệp`.
- Do this at the theme's display weight, both uppercase and lowercase, with the HTML **offline**, i.e. using the theme's own `@font-face` files.
- The metadata `subsets` field proves glyph coverage, not mark-stacking quality.

### 2.1 Theme table (overview)

| # | Theme id | Base (preset / palette / style) | Ground | Channel / topic fit |
|---|---|---|---|---|
| T01 | `tet-poster` | bold-poster + jewel-rich gold + Maximalist Type | light paper | FS: tuổi/năm sinh, Tết, kiêng kỵ |
| T02 | `son-mai` (lacquer night) | dark-premium + Shadow Cut | dark | FS premium (vận hạn, sao xấu), BUD night/Vu Lan |
| T03 | `lich-bloc` (almanac) | coral + Swiss Pulse | light, region-split | FS data: bảng năm sinh, giờ hoàng đạo, ngày tốt |
| T04 | `dong-ho` (folk print) | creative-mode + Folk Frequency, Đông Hồ inks | light điệp paper | FS festive / folk tales, ông Công ông Táo |
| T05 | `saffron-biennale` | biennale-yellow (recolored) + Velvet Standard | light parchment | BUD main: kinh, nhân quả, tượng |
| T06 | `thien-mac` (ink-wash Zen) | cartesian + monochrome + Soft Signal | light rice paper | BUD quotes/thiền; history poetry |
| T07 | `forest-editorial` | editorial-forest (as-is) | light cream / green gravity | Health, BUD meditation/nature |
| T08 | `archive-sepia` | cartesian structure + sepia + warm-editorial | dark sepia or paper | History |
| T09 | `hoang-cung` (jewel court) | jewel-rich + Velvet Standard | dark lacquer brown | History (triều đại), FS luxury |
| T10 | `cobalt-blueprint` | cobalt-grid (+ dark blueprint variant) + Swiss Pulse | light cream / dark navy | Science, tech |
| T11 | `ledger-gold` | dark-premium navy/gold + Swiss Pulse (light alt: blue-professional) | dark | Finance |
| T12 | `dossier-noir` | Shadow Cut + Deconstructed accents | dark | Legal, true-crime explainers |
| T13 | `broadside-alarm` | broadside (as-is) | dark / orange registers | Cross-channel "cảnh báo / sự thật" myth-bust |
| T14 | `tinh-tu` (night sky) | dark-premium + arctic-night + Data Drift | dark navy | FS astrology / sao hạn, BUD Rằm |

Contrast ratios below were computed with WCAG relative luminance (`contrast.py` in the scratchpad). "L-only" means usable only for large text (≥3:1), fills or rules.

---

### T01 `tet-poster`: FS headline theme
- **Tokens:**
  - ground `#F5F2EF`, ground-2 `#FFFFFF`, ink `#1C1410` (16.3:1)
  - accent `#C32F27` (5.0:1 on paper; jewel-rich lacquer red) or the preset red `#D8000F` (4.8:1)
  - accent-2 panel `#780116`
  - glow gold `#F7B538` (atmosphere only; ink on gold is 10.0:1)
  - white-on-red panel 5.3:1
- **Type:**
  - Sansita Swashed 900: hero stack and tilted numerals, −6° stat, −5° close.
  - Spectral 400/400i body.
  - Space Grotesk 600 uppercase chrome, +2px tracking.
  - Google: `family=Sansita+Swashed:wght@800;900&family=Spectral:ital,wght@0,400;1,400&family=Space+Grotesk:wght@500;600`
- **Texture:**
  - Paper grain.
  - Gold sun-bloom (the biennale mechanism) as the only fifth hue, never text. Use the "Gold" note from the earlier report.
  - Optional hoa văn tile at 6% (the Folk Frequency idea).
  - Red progress bar along the bottom edge. Keep it out of the Shorts UI by placing it at y≈1490 or at the top edge (own).
- **Motion:**
  - Energy high.
  - Eases: entry `expo.out` 0.3s, exit `power3.in` 0.2s, accent `back.out(1.6)` on numerals only.
  - Hold 1.2s.
  - Seams: hard cut, whip-pan and vertical push. One `flash-through-white` or `ridged-burn` at the reveal.
  - Signature move: the red-panel surface inversion on the payoff stat.
- **Best devices:**
  - bold-poster treatments: Hero Stack (hook), Hero Stat (red panel), Financial Grid → "bảng tuổi" in a 2-across layout at 9:16, Pull Quote on red, Closing −5°.
  - From the earlier reports: P6 almanac page, P11 data-as-hero, T1 beat slam, T8 count-up, T14 marker circle.
- **Captions:** use the bold-poster skin. Paper card with an ink 1.5px rule and a 4px red leftbar. The active word slams into a red block with paper-colored glyphs and the stacked text-shadow. Body face is Spectral 600.
- **Media:** `T01_base` (warm daylight + vignette). For poster beats use `T01_poster`, a 3-ink dither in ink/red/paper (§6).
- **SFX:**
  - `impact-bass-1` on the stat slam.
  - `whoosh-short` on the whip.
  - `pop` on chips.
  - The repo's `gong` (hf_sfx.py) on the key word.
- **BGM:** query "festive Vietnamese Tết folk, đàn tranh, light percussion". Lyria prompt at ~110 BPM, `PENTATONIC`.

### T02 `son-mai`: lacquer night (FS premium, dark)
- **Tokens:**
  - ground `#0B090A`, ground-2 `#161A1D`
  - text cream `#F3E9D2` (16.4:1; tinted, never `#fff`)
  - accent red `#E5383B` (4.7:1), panel `#660708` (cream on it is 10.9:1)
  - glow/gold `#F7B538` (11.0:1; numerals allowed), secondary `#A4161A`
- **Type:**
  - **Playfair** (v2) 800–900 at opsz ≥144 for display. It is VN ✓ and not the banned "Playfair Display". Alt: Noto Serif Display 900 at `wdth 62.5` for a condensed lacquer feel.
  - Be Vietnam Pro 300 body (dark-ground rule: lighter weight).
  - Chivo Mono 400 data.
- **Texture:** two radial gold glows (never a linear gradient on dark), plus grain and vignette. A gold foil hairline at 1px.
- **Motion:**
  - Shadow Cut: entry `power3.out` 0.8s, exit `power4.in`, ambient `sine.inOut`, hold 2.5s, transition 1.2s.
  - "The pause before the hit matters."
  - Seams: blur crossfade, focus pull, `light-leak` shader, one `domain-warp`.
- **Best devices:** P1 full-bleed graded photo with type in a band, P9 parallax, P8 text-as-window in gold, T12 gold gradient sweep (per Vietnamese padding rules), slow push-ins.
- **Captions:** a dark ink plate with a 1px gold hairline. Cream glyphs. The active word gets a gold underprint block with ink glyphs.
- **Media:** `T02_base` (deep-contrast + warm split wheels). `T02_glow` (bloom) for candles and incense.
- **SFX:** repo `bowl` and `bell`, `whoosh-cinematic` (5.54s; align the swell peak to the cut), `impact-bass-2` on the reveal.
- **BGM:** "dark cinematic ambient, low strings, temple bell"; 90 BPM, `MINOR`.

### T03 `lich-bloc`: almanac / data (FS year tables, giờ hoàng đạo)
- **Tokens:**
  - coral `#E85D5D`, coral-dark `#D44A4A`, cream `#F5F0E8`, cream-dark `#E8E0D4`
  - ink `#1A1A1A` (15.3:1 on cream; 5.1:1 on coral, the "ink-on-fire" rule)
  - gray `#6B6B6B`
  - Coral as text on cream is L-only (3.0:1), so coral is environment and borders only.
- **Type:**
  - **Phudu** 800 uppercase tracked +2px for display.
  - Be Vietnam Pro 400/600 body.
  - JetBrains Mono for figures, with `tabular-nums`.
  - Google: `family=Phudu:wght@700;800;900&family=Be+Vietnam+Pro:wght@400;600;800&family=JetBrains+Mono:wght@500;700`
- **Texture:** 45° hatch at 6% ink on coral regions. Wallpaper numerals (the year, or the can-chi) at 12% ink behind titles.
- **Motion:**
  - Swiss Pulse: `expo.out` 0.4s, exit `power4.in`, hold 1.5s.
  - "Numbers dominate … counters count up … hard cuts."
  - Seams: hard cut, diagonal split, staggered color blocks, one `cinematic-zoom`.
- **Best devices:**
  - coral Region-Split Cover as a 38/62 band. At 9:16 the coral band gets taller.
  - Feature Stat with a wallpaper numeral, Timeline as a vertical rail for 12 giờ.
  - P10 card stack, T9 spring ticker for years, T15 fixed anchor.
- **Captions:** coral skin. Cream block, ink hairline, and the active word on a coral flat block with ink glyphs.
- **Media:** `T03_base` (muted editorial). `T03_graphic` (mono line screen in ink/cream) when a photo must read as graphic.
- **SFX:** `click`, `ping` on table hits, `key-press` on ticker steps, repo `woodblock` on list items.
- **BGM:** "light pizzicato, marimba, curious"; 108 BPM, `MAJOR`.

### T04 `dong-ho`: folk woodblock (FS festive, folk tales)
- **Tokens:**
  - The Đông Hồ ink set is *own*. It is a cultural adaptation of the creative-mode/Folk Frequency structure, and the hues come from the Đông Hồ pigment tradition: điệp paper `#F3EAD8`, son red `#C8372D` (4.3:1, L-only), indigo `#2B3A67` (9.2:1), ochre `#E3A72F` (ink on it 8.1:1), leaf `#4F7A3A` (4.2:1), ink `#1E1A17` (14.5:1).
  - As in creative-mode: two or three accents per frame, never all four.
- **Type:**
  - Archivo 900 at `wdth 125`, uppercase, line-height ≥1.0. This is a deliberate exception to creative-mode's 0.92 because Vietnamese capitals stack marks (own).
  - **Alegreya** 400/700 body (calligraphic humanist serif, VN ✓).
  - JetBrains Mono for taxonomy labels.
  - Google: `family=Archivo:wdth,wght@125,800;125,900&family=Alegreya:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@500`
- **Texture:** the woodblock dither itself on photos. 4px ink borders. One hard offset shadow per frame in ochre plus ink.
- **Motion:**
  - Folk Frequency: `back.out(1.6)` 0.5s, hold 1.5s. The overshoot is restricted to stamps and chips (own; the earlier report flagged the conflict with the faceless doctrine).
  - Seams: hard cut, staggered color blocks, `torn-paper-rip`.
- **Best devices:** P14 scrapbook cutout, P10 card stack, T14 marker accents, `marker-checklist-card`.
- **Captions:** creative-mode skin. Cream card with a 4px ink border and a hard offset shadow. The active word becomes an ochre block.
- **Media:** `T04_base`, a 5-ink ordered dither in ink/indigo/son/ochre/điệp. It reads as a woodblock print.
- **SFX:** repo `woodblock` and `paper`, `pop`, `sparkle` (1.8s) on the reveal.
- **BGM:** "playful Vietnamese folk, sáo trúc, hand drum"; 115 BPM, `PENTATONIC`.

### T05 `saffron-biennale`: BUD main theme
- **Tokens:**
  - parchment `#E9E5DB` (alt `#F3EDDF`), paper-deep `#DCD6C4`
  - ink indigo `#1B2566` (11.1:1); warm alternative ink `#432818` (11.6:1)
  - Sun recolored to saffron: core `#E09F3E` (ink on it 6.1:1, panel OK), soft `#F8F39B` (12.2:1), haze `#F0DA7C`.
  - Ember counter-bloom: robe maroon `#9E2A2B` at 15–22%, never text.
  - Biennale rule: the system never inverts, so there is no yellow text on ink.
- **Type:**
  - **Newsreader** 400/400i at opsz 72, tracking −0.005em, line-height ≥1.12 for Vietnamese.
  - Archivo 400 body plus uppercase micro-labels at 600 with 0.18em tracking.
  - JetBrains Mono for dates and numbers.
  - Google: `family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400&family=Archivo:wght@400;600&family=JetBrains+Mono:wght@400`
- **Texture:** one sun-bloom per frame, covering 42–70% of the frame. 1px hairlines only. 55–60% empty space. No shadows or radii.
- **Motion:**
  - Velvet Standard: `sine.inOut` 1.2s entrance, hold 3.0s, transition 1.5s.
  - "Nothing snaps — everything glides."
  - Seams: blur crossfade, focus pull, `organic-light-leak-overlay` (registry), one `cross-warp-morph`.
- **Best devices:**
  - biennale treatments: Manifesto/Quote (italic under a centered bloom), Chapter Divider (jumbo numeral plus vertical rail), Strand List in place of numbered rows, Poster Panel as a top/bottom band at 9:16.
  - From the earlier reports: P7 sutra scroll, T5 masked line rise.
- **Captions:** biennale skin. Parchment card with a 1px indigo hairline. The active word gets a saffron underprint block with ink glyphs.
- **Media:**
  - `T05_base` (Film Memory-lite) for Jataka and past-life stories.
  - `T05_engrave` (engraving in indigo on parchment) for statues and temples. The woodblock-sutra feel matches the system.
- **SFX:** repo `bowl` (opening and closing), `bell` (key word), `chime` (2.5s) on the strand-list steps.
- **BGM:** "calm meditative ambient, singing bowl, soft pads". The Lyria floor is 90 BPM per the doc's "90–110 calm"; use `MAJOR` or `PENTATONIC`. Set carve strength to 0.5, because the bed is part of the mood and the voice is calm (own).

### T06 `thien-mac`: ink-wash Zen (BUD quotes, history poetry)
- **Tokens:**
  - rice paper `#F2ECDC`, ink `#111319` (15.7:1), gray `#5A5A5A` (5.8:1)
  - seal cinnabar `#9D0208` (7.3:1; one seal stamp per frame, the "single horizontal accent" logic from cartesian)
  - line `#B8B0A4`
- **Type:**
  - **Cormorant** 300/500 italic display. This is Cormorant, not the banned Cormorant Garamond.
  - Be Vietnam Pro 300 body.
  - An optional hand accent in **Charm** (VN ✓; already used in the repo) for single words only.
  - Google: `family=Cormorant:ital,wght@0,300;0,500;1,400&family=Be+Vietnam+Pro:wght@300;500`
- **Texture:** cartesian 1px hairlines plus a vertical drafting line. One or two ink "geo" brush rings at most. The preset's geo-ring is a ring, and the earlier report warned against ring overuse, so use a brush-stroke enso as the single ring (own).
- **Motion:**
  - Soft Signal: `sine.inOut` 1.0s, hold 3.0s, slow drifts, never snapping.
  - Seams: slow dissolve ("drift with me"), ink-bleed mask, one `domain-warp`.
- **Best devices:** cartesian Pull Quote (centered), Agenda/Index as a hairline list, P5 macro→whole zoom-out, T5 masked rise. Plan one held frame per video (`storyboard-recipe.md`).
- **Captions:** cartesian skin. Stone card with a 1px taupe hairline. The active word gets a quiet wash plus a hairline underline, "restraint, not a loud block".
- **Media:** `T06_base` (mono-fade + Kuwahara painterly; multipass, so at most 2 at once). `T06_engrave` (crosshatch, ink on paper).
- **SFX:** `bowl`, `brush` (repo), and silence. Use the fewest SFX of any theme.
- **BGM:** "zen ambient, shakuhachi-like flute, sparse". Carve strength 0.5.

### T07 `forest-editorial`: health / meditation (preset as-is)
- **Tokens:** use the preset values exactly:
  - green `#2e4a2a`, green-deep `#243a21`, green-lite `#3a5a36`
  - pink `#e89cb1`, pink-deep `#d27e96`
  - cream `#efe7d4`, cream-2 `#e6dcc4`, ink `#1a1a17`
  - Contrast: ink on cream 14.2:1, green on cream 8.0:1, pink on green 4.6:1 (display only, per the preset).
- **Type:**
  - Source Serif 4 500 display at opsz 60 with −0.02em tracking; 400 body.
  - JetBrains Mono 500 uppercase chrome with 0.14–0.18em tracking.
  - Google: `family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&family=JetBrains+Mono:wght@500`
- **Texture:** flat paper. 2px hairlines only, 6/8px radii, a monogram stamp on the cover. A topbar runs on every frame. **Shorts tweak (own):** the topbar sits at y ≥ 200 to clear the Shorts header.
- **Motion:**
  - Calm editorial: `power2.out` 0.6s, hold 2.5s.
  - Seams: push-slide and crossfade.
  - Rotate tile fills; never repeat the same fill across a grid.
- **Best devices:** KPI Stat (oversized serif figure), Step Framework (stacked at 9:16), Topic Tiles, Chart bars with values above.
- **Captions:** editorial-forest skin. Oat card with a 2px green hairline and 6px radius. The active word gets a dusty-rose panel.
- **Media:** `T07_base` (natural warm). `T07_botanical` (green line-screen, botanical-plate look).
- **SFX:** `click-soft`, `chime`, soft `pop`.
- **BGM:** "warm acoustic, light piano, hopeful"; 96 BPM, `MAJOR`.

### T08 `archive-sepia`: history
- **Tokens:**
  - Dark register: ground `#1a1610`, text `#e8dcc8` (13.3:1).
  - Paper register: ground `#e8dcc8`, ink `#1a1610`, sub-ink `#3d3020` (9.4:1).
  - Accent oxblood `#9E2A2B` (5.5:1 on paper).
  - Highlight amber `#E09F3E` (7.9:1 on dark).
  - Mids `#6b5a40` and `#a89070` (rules and frames only).
  - Choose **one register per video** (house-style: "same background across all scenes").
- **Type:**
  - **Old Standard TT** 700/400i display, in a 19th-century newspaper register.
  - Spectral 400 body.
  - **Xanh Mono** (designed in Vietnam) for dates and archive codes.
  - Google: `family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&family=Spectral:ital,wght@0,400;1,400&family=Xanh+Mono`
- **Texture:** film grain and gate weave (`T08_base`). Cartesian hairlines and the `image-placeholder` X mark for missing archive images. Torn-paper edges.
- **Motion:**
  - `power2.out` 0.7s, hold 2.5s, slow Ken Burns at scale 1→1.04.
  - Seams: film burn / `light-leak` shader, iris, one `organic-light-leak-overlay` for the time shift.
- **Best devices:** P13 annotated evidence photo, P3 almanac strip as a timeline, P14 freeze-frame cutout, `world-map` adapted. The earlier report notes there is no Vietnam map block.
- **Captions:** a paper card with an oxblood leftbar (bold-poster card logic recolored). On the dark register, use a sepia plate with cream glyphs and an amber underline.
- **Media:**
  - `T08_base` (8mm Home Movie).
  - `T08_engrave` (sepia engraving).
  - Optional cached Floyd-Steinberg or Atkinson dither for newspaper inserts (`dither.mjs`).
  - **Truthfulness rule (doc, 8mm):** do not add dust or scratches where they "imply false provenance". Label reconstructions as such.
- **SFX:** `typing` (1.5s) on typed dates, repo `paper`, `whoosh-cinematic` on era jumps.
- **BGM:** "documentary strings, solemn piano"; 92 BPM, `MINOR`.

### T09 `hoang-cung`: jewel court (history dynasties, FS luxury)
- **Tokens:**
  - jewel-rich row: lacquer brown ground `#432818`, ivory `#FFE6A7` (11.0:1), gold `#BB9457` (4.8:1, display, numerals and rules), oxblood panel `#6F1D1B` (ivory on it 9.2:1), bronze `#99582A` (rules only).
- **Type:**
  - **Playfair Display SC** 700/900 (VN ✓). Small caps make Vietnamese capitals shorter and safer for marks. It is on the banned list as "Playfair Display", so this is a deliberate thematic exception.
  - **Lora** 400/400i body (already in the repo).
  - IBM Plex Mono for regnal years.
- **Texture:** an engraved gold double rule at 3px plus 1px (the bold-poster grid in gold). Radial gold glow. Damask pattern at 6%.
- **Motion:** Velvet with Shadow Cut. `power3.out` 0.9s, hold 2.8s. Seams: `cross-warp-morph`, slow push.
- **Best devices:** P4 camera journey across a lineage scroll, `constellation-hub` for a family tree, P9 parallax portraits.
- **Captions:** an oxblood plate with a gold hairline and ivory glyphs. The active word gets a gold underline.
- **Media:** `T09_base` (warm with a gold highlight wheel and vignette).
- **SFX:** `impact-bass-2`, repo `gong`, `sparkle` on the crown reveal.
- **BGM:** "regal court music, guzheng / đàn nguyệt, slow drums"; 92 BPM, `PENTATONIC`.

### T10 `cobalt-blueprint`: science / tech
- **Tokens:**
  - Light (preset as-is): paper `#F0EBDE`, paper-2 `#E6E0CE`, ink `#1F2BE0` (7.1:1), ink-soft `#5560E5` (4.2:1, subtitles at ≥32px only), grid `rgba(31,43,224,0.10)`, ink-faint `rgba(31,43,224,0.18)`.
  - Strictly two colors.
  - Dark variant ("blueprint" palette): ground `#001830`, text `#e0f0ff` (15.4:1), accent `#0080e0` (4.4:1, large only), mids `#003060` and `#0050a0`.
- **Type:**
  - Newsreader 400 display (size, not weight, makes hierarchy).
  - Hanken Grotesk 600 uppercase labels with 0.16em tracking.
  - **JetBrains Mono** in place of DM Mono.
  - Google: `family=Newsreader:opsz,wght@6..72,400&family=Hanken+Grotesk:wght@400;600&family=JetBrains+Mono:wght@400;500`
- **Texture:** a permanent graph-paper grid at 2cqw cells. Top and bottom hairlines. A pixel-glitch column and a QR block on declarative frames. Pixel-stack bars for data.
- **Motion:**
  - Swiss Pulse: `expo.out` 0.4s, exit `power4.in`, hold 1.5s.
  - Seams: `sdf-iris` or `cinematic-zoom` once, grid dissolve, hard cuts.
- **Best devices:** `exploded-stack`, `flowchart-vertical`, `svg-path-draw`, P11 data-as-hero, T10 decode using **digits and symbols only** (the earlier report's Vietnamese rule).
- **Captions:** cobalt skin. Cream card with grid and top/bottom hairlines. The active word is a solid cobalt block with paper-colored glyphs (risograph knockout).
- **Media:** `T10_base` (cobalt-on-cream mono screen, so photos obey the two-color rule). `T10_dark` (blueprint dither).
- **SFX:** `click-soft`, `ping`, `key-press`. Use `glitch-3` (low-key) at most once.
- **BGM:** "minimal electronic, curious arpeggios"; 108 BPM (the default SaaS/tech inference in `bgm.md` is close).

### T11 `ledger-gold`: finance
- **Tokens:**
  - dark-premium row: ground `#000814`, panel `#001D3D`, mid `#003566` (cream on it 9.9:1)
  - text `#E8E6DF` (16.1:1), gold `#FFC300` (12.5:1, numerals), gold-2 `#FFD60A`
  - Semantic up `#2EC4B6` (9.3:1) and down `#E71D36` (4.4:1, large only; bold numerals ≥32px).
  - Light alternative (blue-professional): cream `#fdfae7`, cobalt `#1e2bfa` (7.2:1), up `#047857` (5.2:1; I replaced the preset's `#059669` because it is 3.6:1), down `#B91C1C` (6.2:1). Text `#111111`.
- **Type:**
  - **Archivo** at `wdth 75`, weight 800, for condensed display numbers, and Archivo 300 for body: one family at two extreme weights, per the typography doc.
  - JetBrains Mono with `tabular-nums` for tickers.
  - Google: `family=Archivo:wdth,wght@75..125,300..900&family=JetBrains+Mono:wght@500;700`
- **Texture:** radial navy glow, hairline axis (no gridlines; the data-in-motion doc says "No gridlines, tick marks, or legends"), and a progress bar.
- **Motion:**
  - Swiss Pulse: `expo.out` 0.4s, counters, `tabular-nums`, hard cuts, one `cinematic-zoom`.
  - Data continuity: "successive stats in the same visual space; only the VALUE changes" (`data-in-motion.md`).
- **Best devices:** `number-wheel`, `bar-chart-race`, `mk-line-graph`, `decline-chart`, `conic-progress-ring` (sparingly), T8 count-up with dynamic scale.
- **Captions:** a navy plate with a gold hairline. The active word is a gold chip with ink `#000814` glyphs (12.5:1).
- **Media:** `T11_base` (cool-shadow, warm-highlight deep contrast).
- **SFX:** `click`, `ping` on the data landing, `riser` (10.03s; trigger at climax − 10.03s) for one payoff only.
- **BGM:** the `bgm.md` finance inference, "calm cinematic, soft strings, subtle piano, restrained percussion", 92 BPM.

### T12 `dossier-noir`: legal / crime explainers
- **Tokens:**
  - Shadow Cut: ground `#0a0a0a`, text `#f0f0f0` (17.4:1), surface `#3a3a3a` (text 10.0:1).
  - Accent `#C1121F` (3.2:1 on black, so fills, stamps and rules only). Cream on red is 5.5:1.
  - Document paper `#E9E4D8` (ink 15.6:1) for exhibit cards.
- **Type:**
  - **Oswald** 700 uppercase display (VN via the Google supplement; ship `@font-face`). Alt: Saira Condensed 800.
  - **Noticia Text** 400 body, a sturdy news serif with VN ✓.
  - **Black Ops One** for "ĐÃ TUYÊN ÁN"-style stamps only.
  - IBM Plex Mono for "Điều 123 BLHS" citations.
- **Texture:** heavy vignette, grain, redaction bars, document cards (P14 scrapbook in a dossier register).
- **Motion:**
  - Shadow Cut: `power3.out` 0.8s, exit `power4.in`, "elements emerge from darkness".
  - `steps(8)` exits for redaction bars only (Deconstructed).
  - Seams: hard cuts, one `glitch` shader or `domain-warp`.
- **Best devices:** P13 annotated evidence, `vox-annotate`, `hw-callout-circle` in red, T15 fixed anchor, T13 slice glitch (with a minimal split under the Vietnamese rule).
- **Captions:** a black plate with a 1px red hairline. Paper glyphs. The active word gets a red block with paper glyphs (5.5:1).
- **Media:** `T12_base` (mono-clean, crushed blacks, vignette, grain). The `bleach-bypass` LUT exists in `luts/index.json` as an alternative look.
- **SFX:** `typing`, `key-press`, `impact-bass-2` on the verdict, `error` (1.62s) on the "sai" beat.
- **BGM:** "tense investigative underscore, pulsing low synth"; 96 BPM, `MINOR`.

### T13 `broadside-alarm`: cross-channel myth-bust / warning (preset as-is)
- **Tokens:**
  - ink-black `#111111`, alt `#1A1A18`, fire-orange `#E85D26` (5.4:1 both ways), cream `#F0ECE5` (16.0:1), muted `#888880` (5.3:1).
  - Two registers, one per frame. Cream text on orange never appears.
- **Type:**
  - Barlow 900 **lowercase** display, tracking −0.04em. Lowercase Vietnamese reduces the stacked-mark height problem (own).
  - Barlow 400 body. IBM Plex Mono uppercase chrome at 0.14em.
  - Google: `family=Barlow:wght@400;700;900&family=IBM+Plex+Mono:wght@500`
- **Texture:** none. "Type IS the composition." Use the fadelist (opacity 1.0 / 0.5 / 0.22).
- **Motion:** `expo.out` 0.25s, hard cuts, a register flip as the transition.
- **Best devices:** Statement, Fadelist, Compare (dark → orange payoff stacked at 9:16), T1 beat slam, T7 waterfall cut.
- **Captions:** broadside skin. Ink plate with an orange hairline and cream glyphs. The active word becomes an orange block with ink glyphs.
- **Media:** `T13_base` (orange/ink line screen, protest-print).
- **SFX:** `impact-bass-1`, `whoosh`, `error` on the myth line.
- **BGM:** "driving percussive, tense"; 120 BPM.
- **Usage (own):** an *accent* theme. A channel may run 1 video in 5 in this theme for "sự thật / cảnh báo" topics, so it never becomes the channel's face.

### T14 `tinh-tu`: night sky (FS astrology, BUD Rằm)
- **Tokens:**
  - arctic-night: ground `#0a0a14`, deep `#1a2a4a`, mid `#3a5a8a`
  - star `#6a9aca` (6.6:1), frost text `#cae8ff` (15.5:1)
  - Gold from dark-premium `#F4D58D` (13.8:1) as the single warm accent (planet and moon).
- **Type:**
  - **Fraunces** 300 at opsz 144 with SOFT 100. A soft wonky serif; VN ✓; the repo already uses Fraunces.
  - Be Vietnam Pro 200/300 body (Data Drift's thin register).
  - Chivo Mono 300 for coordinates.
- **Texture:** `starfield` overlay (seek-safe per the earlier report), radial moon glow, constellation lines that "name their anchors" (`motion-principles.md` "Connector lines earn their place").
- **Motion:**
  - Data Drift: `sine.inOut` 1.0s, hold 2.5s, transition 1.5s, "extreme scale shifts (micro → macro)".
  - One `gravitational-lens` seam.
- **Best devices:** `constellation-hub`, P5 macro→whole, `pull-back-reveal`, T12 sweep. Avoid ring-circle layouts; the earlier report flagged them.
- **Captions:** a translucent navy plate. Text color is `#1a2a4a` at 0.85 alpha, *own*. Frost glyphs. The active word gets a gold underline.
- **Media:** `T14_base` (night-lift, cool temperature, bloom).
- **SFX:** `sparkle`, `chime`, repo `bell`.
- **BGM:** "celestial ambient, glassy pads"; 90 BPM, `MAJOR`.

**Channel registry suggestion (own):**

| Channel | Themes |
|---|---|
| FS | T01 (40%), T03 (25%), T02 (15%), T04 (10%), T14 (10%), plus T13 as an accent |
| BUD | T05 (50%), T06 (25%), T07 (10%), T14 (10%), plus T02 for Vu Lan |
| History | T08 or T09 |
| Science | T10 |
| Finance | T11 |
| Health | T07 |
| Legal | T12 |

---

## 3. Variety rules inside a theme (no one-color template, brand intact)

**Doc anchors:**
- "Atoms are sacred · composition is free" (all presets). Brand covers hex, fonts and weight relationships. Layout is free (`video-composition.md`).
- Every preset ships **6 named frame treatments**, for example bold-poster's Hero Stack, Hero Stat, Fin Grid, Pull Quote, Editorial Cards and Closing.
- Coral and cartesian: "no 3 consecutive frames share an anchor."
- Vary eases, directions, staggers and ambient motion per scene (`motion-principles.md`).
- "An aesthetic change should signal a new concept, not just a new number" (`data-in-motion.md`).

**Mechanism (own):** a deterministic `variant = hash(video_id)` selects the per-video knobs below. Never use `Math.random`.

| Knob | Varies per video | Fixed by theme |
|---|---|---|
| Frame-treatment mix | Pick 4–5 of the preset's 6 treatments; order follows the script's beat roles | Treatment internals |
| Anchor sequence | left / centered / panel; no 3 in a row alike | Safe-area paddings |
| Surface inversion | Which beat gets the sanctioned panel (red, dark, yellow, coral region); at most 1–2 per video | Which panel colors are legal |
| Accent role | coral-style "accent OR environment per frame" | The accent hex |
| **Accent sub-palette** | One of 3 pre-validated accents per theme. FS can map ngũ hành to the video's element: Hỏa `#C32F27`, Thổ `#BB9457`, Kim `#F7B538` (atmosphere), Mộc `#4F7A3A`, Thủy `#1B2566`. Each must pass AA on the ground. | Ground, ink, fonts, motion. One accent per video, never mixed. |
| Texture variant | hatch 45° / −45° 30–60px / 90° vertical (coral's documented variants); bloom position (off-center, behind focal, corner); ghost-word content (the video's keyword) | Texture family and opacity range |
| Hook device | Rotate T1 slam, T15 anchor, P8 text-window, P5 macro open, T8 count-up; never the same hook twice in a row on a channel | Hook duration window |
| Seam pair | One primary CSS seam family plus one accent shader from the theme's allowed set | Max one shader per short; one direction rule per film (storyboard recipe) |
| Ambient per scene | slow zoom / drift / bloom breathe / hatch drift / stillness | "Stillness after motion is powerful" |
| Media variant | `base` vs `alt` treatment within the bounded ranges in §6; intensity ±0.1 | One house treatment per video |
| Caption gesture | Keep it fixed per theme. Variety comes from emphasis words (accent, marker mode cycling) | Skin, font, position |
| Music | The theme's mood query, rotated by `hf_music` so no adjacent videos share a track (existing repo logic) | Mood, BPM band, carve strength |

**Guard rails:**
1. **Batch-level:** two adjacent uploads on one channel must differ in at least two of these: theme, hook device, accent and seam pair (own; matches the "no one-color template" goal).
2. **Concept continuity:** within a video, a repeated concept keeps its visual space (`data-in-motion.md`). Vary *between* concepts, not within one.
3. **Adherence gate:** run `design-adherence` (every hex ∈ theme palette) plus `hyperframes check` (contrast) per render. A variant may only *select* tokens and never mint new ones.
4. **Held frame:** each video has one beat where nothing moves and the line lands (`storyboard-recipe.md`).
5. **Lazy-default scan per render** (`house-style.md`): gradient text, left-edge accent stripes on cards, cyan-on-dark, pure black or white, identical card grids, everything centered.

---

## 4. Captions (burned-in, faceless 9:16)

### 4.1 Which docs apply
- `media-use/audio/references/captions/{authoring,motion,transcript-handling}.md` cover designed-canvas captions. They are the primary source.
- The `embedded-captions` skill is for **talking-head footage** and refuses no-human clips, so it does not apply directly. Its **rail spec** (`references/rail.md`) and its gates (≥0.5s on screen, word timing within 80ms, group windows envelop their words, no two groups overlapping in time and region, luminance probe) are worth copying.
- Every preset's `caption-skin.html` is the best ready-made source of theme-matched skins.

### 4.2 Grouping and timing
- **Doc:** high energy uses 2–3 words, conversational 3–5, calm 4–6. Break on a sentence end, a pause of 150ms or more, or the max word count. One group is visible at a time.
- **embedded-captions grouping:** new group on a pause ≥500ms, a sentence terminator, or a comma plus a ≥250ms pause. Cap at 6 words or 2.5s. Minimum 2 words and 0.5s on screen. `in = first.start − 0.08`; `out = min(next.in − 0.05, last.end + 0.6)`.
- **Vietnamese (own):** transcripts tokenize by **syllable**, so a "word" in the timestamps is one tiếng. Scale the counts to 3–5 syllables (high energy, FS hooks), 5–8 (conversational) and 6–10 (BUD calm). Never split a compound word across groups ("phong / thuỷ", "nhân / quả"). Keep a simple bigram list of compounds in the engine.
- **Lines:** ≤2 lines at about 32–42 characters per line (broadcast, `rail.md`). At 9:16 and 64–72px, a practical limit is about 22–28 Vietnamese characters per line (own). Never leave a dangling one-word line.
- **Exit guarantee (doc, mandatory):** run `tl.to(group,{opacity:0,…,duration:0.12,ease:"power2.in"}, end−0.12)` and then `tl.set(group,{opacity:0,visibility:"hidden"}, end)`. Add the self-lint loop before registering the timeline.
- **State changes:** use `tl.set(el,{className:…})` and never `tl.call` (caption-skin header: "seek does not fire them").
- **Determinism:** no `Math.random` and no `Date.now`.

### 4.3 Emphasis
- **Doc per-word classes:** brand names (larger, unique color), ALL CAPS (scale boost), numbers (bold, accent), emotional keywords (overshoot), CTA (underline or color pop).
- **Marker modes:** highlight, circle, burst, scribble, sketchout. Burst suits hype, circle key terms, highlight standard, scribble subtle. Cycle modes across groups.
- **Intensity by theme energy** (`motion.md`):
  - High (T01, T03, T13): accent plus glow plus about 15% scale pop on the active word.
  - Medium (T07, T10, T11, T12): color pop, scale ≤1.05.
  - Low (T05, T06, T14): a warm shift and 3% scale.
  - The rail doc caps the active-word pop at ≤1.1× for readable captions.
- **Overflow:** `fitTextFontSize(text,{fontFamily, fontWeight, maxWidth})`. Portrait `maxWidth` is 900, base 78, min 42. With an emphasis scale s, use `maxWidth = 840/s`. I narrowed it from 900 to clear the Shorts right rail (own). Use `overflow: visible`, not hidden. Use a full-width absolute container and avoid `left:50%; translateX(-50%)`, which clips at the edges.
- **Vietnamese caveats:** see `hf_kinetic_type.md` §3 (NFC, `Intl.Segmenter`, padded masks, blur ≤10px, no decode pools of Vietnamese letters). Caption line-height ≥1.25 (own).

### 4.4 Position and safe zones
- **Doc:**
  - Portrait captions sit "lower middle ~600–700px from bottom, centered" (`authoring.md`, `rail.md`).
  - Title-safe is the inner 80% (10% inset) and action-safe 90% (`hyperframes-studio` §4).
  - The faceless-explainer reserves the bottom ~17% as a caption band and anchors the hero at y≈0.42H = 806px. That band position is for non-Shorts delivery; on Shorts it falls under the platform UI.
- **YouTube Shorts overlay map (own; verify by laying a real Shorts screenshot at 1080×1920 over a render):**
  - Top ≈0–170px: header and search.
  - Right ≈ x 940–1080 from y ≈ 880 to 1650: the like, comment, share and remix rail.
  - Bottom ≈ 1480–1920: title, channel, subscribe button, music ticker and progress bar.
- **Recommended Shorts layout (own):**
  - Caption band: `--cap-band-top: 1180px; --cap-band-height: 260px` (center ≈1310, i.e. 610px from the bottom, inside the doc's 600–700).
  - Caption horizontal span x 96–936.
  - Key visuals live between y 200 and 1150, with the hero anchor at about y 760–806.
  - Full-bleed backgrounds are exempt (faceless doc).
  - Do not put the progress bar or chrome at the very bottom edge.

### 4.5 Skins on light vs dark grounds (from the 13 preset caption skins)

| Ground | Card | Upcoming / active / spoken | Themes |
|---|---|---|---|
| Light paper | paper card + 1–2px ink rule (+ accent leftbar or hairline), square corners, no blur shadow | faint ink (≈42% mix) / **accent block, ground-colored glyphs** (box-shadow spread, no layout shift) / solid ink | T01, T03, T04, T07, T10 |
| Light, quiet | stone/parchment card + 1px hairline | faint ink / **underprint** (yellow / saffron) or a wash + hairline underline / ink | T05, T06 |
| Dark | ink plate + 1px accent hairline | faint cream / **accent block with ink glyphs** (broadside register flip) or gold underline / cream | T02, T08-dark, T09, T11, T12, T13, T14 |
| Over photos (doc luminance probe) | <60 luma: light text OK; 60–180: add a glyph scrim; >180: opaque text plus scrim. A scrim is "sized to the text box", never a frame-wide bar. | — | all |

**Skin implementation (doc pattern):**
- Copy the preset skin to `caption-skin.<theme>.html`.
- Inject the `:root` tokens from the theme: `--cap-ink`, `--cap-canvas`, `--cap-accent`, `--cap-accent-2`, `--font-display`, `--font-body`, `--cap-band-top`, `--cap-band-height`.
- Optional per-word classes: `cap-brand` (display face) and `cap-num` (mono).
- Karaoke runs as a 3-state class swap. The active word gets `fromTo(scale .9→1, 0.16s, back.out(2.2))`.
- **Font for Vietnamese captions (own):** use the theme's *body* or a 600–800 weight, not a swash display face (T01's Sansita Swashed is not for captions; use Spectral 600). Sentence case, except T03 and T13 groups of ≤4 syllables.

### 4.6 Registry caption components (live catalog; install with `npx hyperframes add <name>`)

| Adopt | For | Notes |
|---|---|---|
| `caption-editorial-emphasis` | T05, T06, T08, T09 | Dual-font size contrast on emphasis words, the storytelling register |
| `caption-weight-shift` | T07, T10, T11 | Needs a **variable** VN face (Source Serif 4, Archivo, Hanken, Newsreader). Be Vietnam Pro is static. |
| `caption-pill-karaoke` | T03, T11 | Recolor the pill to tokens |
| `caption-highlight` | T01, T13 | The "TikTok red sweep" is native to the poster red |
| `caption-clip-wipe` | T10, T12 | Pad the clip-path for marks (negative insets; earlier report §3) |
| `mk-callout-highlight` | any | One scalar drives the word emphasis synced to the voiceover; good for the key sentence |
| `inline-highlight` | any | Marker-style highlight behind text |
| `caption-camera-follow` | hook only | One sentence across a huge world |
| `caption-blend-difference` | busy photo beats | Auto-inverts against the background |

**Avoid:**
- `caption-gradient-fill`: gradient text is on the lazy-defaults list.
- `caption-neon-*` / `caption-glitch-rgb`: the neon and cyan tell. Allowed only in T12, once.
- `caption-matrix-decode`: decoding with Vietnamese letters flashes wrong-tone words.
- `caption-emoji-pop` and `caption-particle-burst`: generic, and particle systems appear on the doc's "never add" list for audio-reactive work.

All components are authored for 16:9 and ship transparent. Add a contrast layer in the host, beneath the component (doc). Run `check` and a draft render after installing.

### 4.7 Transcription and alignment for Vietnamese
- **Never use `.en` models.** They translate. Use `npx hyperframes transcribe narration.wav --model small --language vi`, or `medium` for noisy audio.
- **Parakeet** covers English plus 25 European languages, not Vietnamese, so `transcribe.mjs` falls back to whisper.cpp.
- **Quality gate:** retry at a larger model if more than 20% of tokens are `♪`/`�` or nonsense. Filter non-words. Allow ±80ms timing error.
- **Own:** the script text is known (VieNeu-TTS input), so treat ASR as alignment only. Map ASR words back onto the script's syllables (edit-distance alignment) so captions show the *authored* spelling and diacritics. ASR often confuses tones (hỏi/ngã, Tỵ/Tị). Register display substitutions like "15%" for "mười lăm phần trăm" (the doc's `CREATIVE_SUBS` concept).

---

## 5. Audio (TTS, BGM, SFX, mix)

### 5.1 Doc numbers

| Item | Value | Source |
|---|---|---|
| Publish loudness | **−14 LUFS integrated, TP −1.5 dBTP, LRA 11**, two-pass `loudnorm` (measure, then apply `measured_*` with `linear=true`) | `media-use/references/operations.md` |
| Music bed under voice | volume **0.12 ≈ −18 dB** (`BGM_BED_VOLUME`); with no voice, 0.9 | `bgm.md`, `bgm-volume.mjs` |
| Docs narrator reference | music "about −31 LUFS, never masking the voice"; pace 145–155 wpm | `tts.md` |
| SFX level | volume **~0.35**, under voice and BGM | `sfx.md`, `sfx.mjs` |
| Duck lane defaults | duck ×0.25 (≈ −12 dB), attack 0.15s, release 0.4s, merge-gap 0.6s; example lane 0.6 → 0.15 | `audio-duck.mjs` |
| Voiceover carve | **required whenever music plays under a voice**; default strength 0.8 (6 bands 250 Hz–2.5 kHz, about −7 dB, −15 dB at 1.6 kHz, 19 dB level room); 0.5 is where it starts to sound like an effect; 0.25 judged too weak; always dynamic | `hyperframes-audio/SKILL.md` |
| Voice chain | `voice-clean` = Remove Rumble → Reduce Mud → Even Out Loudness → Add Clarity → Peak Ceiling; order: subtract → level → relationships → character → ceiling; limiter last | `presets.md` |
| Audio-reactive | pre-extracted bands only; text pulses 3–6%, non-text 10–30%; no equalizer bars | `audio-reactive.md` |

### 5.2 Mix wiring to adopt (doc attributes)

```html
<hf-audio-group id="voiceover" data-label="Voiceover" data-volume="1"
  data-fx-chain="{&quot;version&quot;:1,&quot;nodes&quot;:[
   {&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;v1&quot;,&quot;label&quot;:&quot;Remove Rumble&quot;,&quot;params&quot;:{&quot;frequency&quot;:80,&quot;q&quot;:0.707,&quot;poles&quot;:&quot;2&quot;}},
   {&quot;type&quot;:&quot;compressor&quot;,&quot;id&quot;:&quot;v2&quot;,&quot;params&quot;:{&quot;threshold&quot;:-18,&quot;ratio&quot;:3}},
   {&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;v3&quot;,&quot;label&quot;:&quot;Add Clarity&quot;,&quot;params&quot;:{&quot;frequency&quot;:3000,&quot;gain&quot;:2.5,&quot;q&quot;:1}},
   {&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;v4&quot;,&quot;params&quot;:{&quot;limit&quot;:-1.5,&quot;attack&quot;:5,&quot;release&quot;:50,&quot;level_out&quot;:0}}]}"></hf-audio-group>
<audio id="vo-1" data-audio-group="voiceover" src="voice/l1.wav" data-start="0.2" …></audio>
<audio id="bgm" data-audio-group="music" src="bgm/track.mp3" data-volume="0.12"
  data-fx-carve="{&quot;enabled&quot;:true,&quot;sources&quot;:[&quot;voiceover&quot;],&quot;strength&quot;:0.8}" …></audio>
<audio id="sfx-3" data-audio-group="sfx" src="sfx/impact-bass-1.mp3" data-volume="0.35" …></audio>
```

- Run `node <hyperframes-audio>/scripts/carve.mjs --comp index.html` and then `npx hyperframes check`.
- Write the attributes double-quoted with `&quot;`, or `carve.mjs` cannot see existing chains.
- **Group rules (doc):**
  - Carve against the *group*, never a list of clip ids.
  - Never put the bed or SFX inside the voice group.
  - Never put a carve on a voice or on a bus.
- Compressor, limiter, gate and bitcrush parameters are **not automatable**. Automate a `gain` stage instead.
- *Own:* the repo already mixes outside HF (hf_music/hf_sfx with ffmpeg). Either port to these attributes (preview = render) or keep the Python path, but then reproduce the carve with ffmpeg `sidechaincompress` (the doc's "bake" recipe) plus the −14 LUFS two-pass.

### 5.3 TTS
- **Keep the repo's VieNeu-TTS.** The doc providers are a poor fit for Vietnamese:
  - Kokoro has no Vietnamese voice prefix (a/b/e/f/h/i/j/p/z).
  - HeyGen starfish accepts `--lang`, but Vietnamese voice quality is undocumented.
  - Gemini infers the language from the text and is unverified for Vietnamese here.
- **Doc guidance that transfers:**
  - Write numbers the way they should be spoken.
  - Vary the hook type.
  - The script should feel shorter than the video.
  - Use `style` or direction rather than spoken stage directions.
  - Check every line has audio and non-empty word timings before captioning.
- Pacing for Vietnamese is syllable-based. Per memory, "preset C" is the approved voice/sound standard; keep it.

### 5.4 BGM rules to adopt
- **Retrieval:** search the HeyGen catalog by mood when credentialed, otherwise generate with Lyria → MusicGen. Run the "Preflight" (`npx hyperframes auth status`) and ask the user before generating locally.
- **Trimming (doc):** "do not assume the beginning of the retrieved file is the best edit point". Compare 5-second sections, trim to the strongest clean entrance, use a short fade-in and a longer fade-out, and make sure the file covers the full cut with no silent tail.
- **Lyria knobs:** `--bpm` 90–110 calm, 110–130 energetic; `--brightness` (≥0.7 promotional); `--density`; `--scale` (`MAJOR`/`MINOR`/`PENTATONIC`); `--negative-prompt`. Per-theme values are in §2.
- **The repo's hf_music** loudness-matches beds and filters out tracks whose 5-second RMS swings more than 14 dB. Keep it, add the carve, and normalize the final mix to −14 LUFS.

### 5.5 SFX
- **Bundled library** (Pixabay Content License: commercial use, modification and redistribution in rendered videos allowed, no attribution required). Durations in seconds:

  | File | Dur | File | Dur | File | Dur | File | Dur |
  |---|---|---|---|---|---|---|---|
  | chime | 2.5 | click / click-soft | 0.37 | error | 1.62 | glitch-1 / -2 / -3 | 2.64 / 3.5 / 3.1 |
  | impact-bass-1 / -2 | 2.12 / 2.59 | key-press | 0.4 | notification | 2.46 | ping | 1.32 |
  | pop | 0.72 | riser | 10.03 | sparkle | 1.8 | typing | 1.5 |
  | whoosh / whoosh-short | 0.57 | whoosh-cinematic | 5.54 | | | | |

- **Retrieval switch (doc):** with a HeyGen credential, **every** cue is retrieved from HeyGen (`min_score 0.4`) and the bundled files are not used. The switch is global. Name cues concretely ("glass shatter", not "dramatic sound"). A missing cue is skipped and never blocks the render.
- **Placement (doc):**
  - Impacts trigger on the visual landing and decay into the next shot (J-cut).
  - A riser starts at climax − 10.03s.
  - `whoosh-cinematic` peaks on the cut.
  - Social Flash is used at most once per video, never as a strobe.
  - Each beat names its SFX cue.
- **Density (own):** at most one cue per beat and about 4–8 per 30s Short. Calm themes (T05, T06) use 2–4. The repo's synthesized palette (bell, bowl, chime, gong, woodblock, tick, whoosh, brush, paper in `hf_sfx.py`) is more on-brand for BUD and FS than the bundled UI sounds. Use the bundled ones for T10–T12.

---

## 6. Media treatment presets per theme (exact CLI payloads)

Command shape (doc). Run it on a real `<img>`/`<video>` only, with a unique selector:

```bash
npx hyperframes@0.8.75 media-treatment --project . --file index.html \
  --selector "#ph-1" --grading '<JSON>' --apply --json        # add --dry-run to preview
```

- All payloads below passed `--apply --dry-run` on 0.8.75 (`scratchpad/payloads.json`). That validates the schema only.
- Before shipping each theme, generate a visual before/after contact sheet: `hyperframes snapshot <proj> --frames 3 --no-end --describe false --output snapshots/treatment-{before,after}`.
- A `preset` expands into its own `adjust` values, and the keys you pass override them (verified in the dry-run output).

| Theme | Primary (`base`) | Alternate / beat-specific |
|---|---|---|
| T01 | `{"preset":"warm-daylight","intensity":0.7,"adjust":{"contrast":0.06,"highlights":-0.06,"vibrance":0.04},"details":{"vignette":0.1,"grain":0.08,"grainSize":0.2,"grainRoughness":0.55}}` | Poster: `{"intensity":1,"adjust":{"contrast":0.06},"effects":{"dither":1,"ditherSize":0.3},"palette":["#1C1410","#C32F27","#F5F2EF"]}` |
| T02 | `{"preset":"deep-contrast","intensity":0.65,"adjust":{"temperature":0.08,"shadows":-0.04,"saturation":-0.06},"wheels":{"shadows":{"hue":355,"amount":0.08,"level":-0.02},"highlights":{"hue":40,"amount":0.08,"level":0}},"details":{"vignette":0.22,"grain":0.1,"grainSize":0.2,"grainRoughness":0.6}}` | Candle glow: `{"preset":"deep-contrast","intensity":0.65,"effects":{"bloom":0.45,"bloomRadius":10},"details":{"vignette":0.22}}` (multipass) |
| T03 | `{"preset":"muted-editorial","intensity":0.7,"adjust":{"contrast":0.05},"details":{"grain":0.06}}` | Graphic: `{"intensity":1,"effects":{"monoScreen":1,"monoScreenSize":0.32,"monoScreenAngle":0.25,"monoScreenSpread":0.3,"monoScreenShape":4,"monoScreenInvert":0},"palette":["#1A1A1A","#F5F0E8"]}` |
| T04 | `{"intensity":1,"adjust":{"contrast":0.05,"saturation":0.04},"effects":{"dither":1,"ditherSize":0.32},"palette":["#1E1A17","#2B3A67","#C8372D","#E3A72F","#F3EAD8"]}` | Reveal: inline `style="--hf-color-grading-dither:0"`, then `tl.to(sel,{"--hf-color-grading-dither":1,duration:0.8,ease:"power2.out"},t)` |
| T05 | `{"preset":"vintage-wash","intensity":0.55,"details":{"vignette":0.1,"grain":0.08,"grainSize":0.2,"grainRoughness":0.6}}` | Statues: `{"intensity":1,"effects":{"engraving":1,"engravingSpacing":0.4118,"engravingMinThickness":0.2,"engravingMaxThickness":0.4571,"engravingAngle":0.25,"engravingContrast":0.4667,"engravingSharpness":0.59,"engravingWave":0.2,"engravingWaveFrequency":0.2222},"palette":["#1B2566","#E9E5DB"]}` |
| T06 | `{"preset":"mono-fade","intensity":0.85,"effects":{"kuwahara":0.8,"kuwaharaRadius":0.2,"kuwaharaSharpness":0.4,"kuwaharaSaturation":0.2},"details":{"vignette":0.08}}` (multipass) | `{"intensity":1,"effects":{"crosshatch":1,"crosshatchSpacing":0.28,"crosshatchThickness":0.25,"crosshatchAngle":0.25,"crosshatchContrast":0.3333,"crosshatchEdges":0.5,"crosshatchLineWeight":0,"crosshatchWave":0.33,"crosshatchWaveFrequency":0.2222},"palette":["#111319","#F2ECDC"]}` |
| T07 | `{"preset":"warm-daylight","intensity":0.5,"adjust":{"shadows":0.06,"highlights":-0.06,"vibrance":0.03},"details":{"grain":0.05,"grainSize":0.2}}` | Botanical: `{"intensity":1,"effects":{"monoScreen":1,"monoScreenSize":0.3,"monoScreenAngle":0.25,"monoScreenSpread":0.3,"monoScreenShape":4,"monoScreenInvert":0},"palette":["#243a21","#efe7d4"]}` |
| T08 | 8mm: `{"preset":"vintage-wash","intensity":0.72,"details":{"vignette":0.28,"vignetteMidpoint":0.54,"vignetteFeather":0.72,"grain":0.34,"grainSize":0.18,"grainRoughness":0.72},"effects":{"filmArtifacts":0.5}}` | `{"intensity":1,"effects":{"engraving":1,"engravingSpacing":0.38,"engravingMinThickness":0.2,"engravingMaxThickness":0.4571,"engravingAngle":0.25,"engravingContrast":0.5,"engravingSharpness":0.59,"engravingWave":0.15,"engravingWaveFrequency":0.2222},"palette":["#1a1610","#e8dcc8"]}`; newspaper: `dither.mjs --algorithm atkinson --palette '#1a1610,#6b5a40,#e8dcc8'` |
| T09 | `{"preset":"warm-daylight","intensity":0.6,"adjust":{"contrast":0.08,"blacks":-0.03},"wheels":{"shadows":{"hue":10,"amount":0.07,"level":-0.02},"highlights":{"hue":42,"amount":0.08,"level":0}},"details":{"vignette":0.18,"grain":0.06}}` | Film Memory seed (`vintage-wash` 0.6, vignette 0.12, grain 0.12) for legends |
| T10 | `{"intensity":1,"effects":{"monoScreen":1,"monoScreenSize":0.3,"monoScreenAngle":0.25,"monoScreenSpread":0.3,"monoScreenShape":0,"monoScreenInvert":0},"palette":["#1F2BE0","#F0EBDE"]}` | Dark: `{"intensity":1,"effects":{"dither":1,"ditherSize":0.25},"palette":["#001830","#003060","#0050a0","#0080e0","#e0f0ff"]}` |
| T11 | `{"preset":"deep-contrast","intensity":0.6,"adjust":{"temperature":-0.04,"saturation":-0.1},"wheels":{"shadows":{"hue":215,"amount":0.1,"level":-0.02},"highlights":{"hue":45,"amount":0.06,"level":0}},"details":{"vignette":0.15}}` | UI or chart screenshots: **none** (UI Fidelity: "do not add data-color-grading") |
| T12 | `{"preset":"mono-clean","intensity":0.9,"adjust":{"contrast":0.12,"blacks":-0.05},"details":{"vignette":0.25,"grain":0.12,"grainSize":0.18,"grainRoughness":0.6}}` | Look alternative: `resolve --type grade --intent "bleach bypass"` (LUT index entry `bleach-bypass`, intensity 0.8) |
| T13 | `{"intensity":1,"effects":{"monoScreen":1,"monoScreenSize":0.4,"monoScreenAngle":0.25,"monoScreenSpread":0.35,"monoScreenShape":4,"monoScreenInvert":0},"palette":["#111111","#E85D26"]}` | Editorial Halftone seed for one beat only |
| T14 | `{"preset":"night-lift","intensity":0.7,"adjust":{"temperature":-0.06},"effects":{"bloom":0.5,"bloomRadius":12},"details":{"vignette":0.2,"grain":0.06}}` | Starry dither: `"palette":["#0a0a14","#1a2a4a","#3a5a8a","#6a9aca","#cae8ff"]` with `dither 1` |

**Treatment rules that matter for theming (doc + verified capability data):**
- **Palette-capable effects** recolor stock into the theme's inks: `dither` (animatable), `monoScreen`, `engraving`, `crosshatch` and `ascii`. They are the strongest tool for "stock stops reading as stock".
- **`twoInkPrint` and `halftone` take no palette.** Two-Ink is a fixed vermilion and teal, so it breaks two-color themes (T05, T10, T13) and adds teal to T01. Use a dither or monoScreen in brand inks instead.
- **Animatable properties:** `--hf-color-grading-{intensity, lut-intensity, exposure, blur, bloom, kuwahara, pixelate, ascii, dither}`. Author the start value inline, then use finite `tl.to` only. Engraving and monoScreen are static: for a source → line-art reveal, crossfade two synchronized layers.
- **Global `intensity`** fades only primary correction and the LUT, not the effects (Camcorder recipe).
- **Cost:** blur, bloom and Kuwahara are multipass. More than two simultaneous full-frame multipass layers requires a playback check.
- **Never duplicate** vignette, grain or blur with CSS or SVG. Treat only photographic media: never text, SVG, logos, icons or UI.
- **Overlays come from the registry**, not hand-built: `organic-light-leak-overlay` (T05, T08), `editorial-flash-overlay` (T01, T13; once per video, midpoint on the cut), `freeze-frame-dressing` (T04, T08, T12).

---

## 7. Open items / verification hooks
1. Render the Vietnamese pangram card for each theme's display, body and caption face, offline with self-hosted woff2, and in uppercase. Check in particular Sansita Swashed, Phudu, Old Standard TT, Playfair Display SC and Cormorant at their display weights.
2. Overlay a real YouTube Shorts UI screenshot on renders to confirm the §4.4 band (y 1180–1440, x 96–936).
3. Make before/after contact sheets for every §6 payload on real BUD/FS stock. Check the T06 Kuwahara cost and the T04 dither moiré in particular.
4. Decide whether to port the mix to HF audio attributes (carve plus voice bus) or bake it in Python. Either way, measure the final −14 LUFS / −1.5 dBTP with `ebur128`.
5. Check whether HF 0.8.155 changed the bundled-font subset handling before upgrading from 0.8.75. Re-run the fontTools check on `EMBEDDED_FONT_DATA`.

## Source index
- **hyperframes-creative:** `SKILL.md`; `references/{house-style, video-composition, design-spec, design-adherence, typography, motion-principles, visual-styles, beat-direction, narration, storyboard-recipe, story-spine, prompt-expansion, data-in-motion, audio-reactive, design-picker, composition-patterns}.md`; `palettes/*.md` (9); `frame-presets/*/FRAME.md` (13) and `caption-skin.html` (13).
- **media-use:** `SKILL.md`; `references/{media-treatments, media-treatment-recipes, grading, resolve, operations, audio, setup-providers, memory, meta, telemetry-dashboard}.md`; `luts/{README.md, index.json}`; `audio/references/{tts, bgm, sfx, transcribe, requirements, remove-background, tts-to-captions}.md` and `captions/{authoring, motion, transcript-handling}.md`; `audio/assets/sfx/{CREDITS.md, manifest.json}`; `audio/scripts/lib/{bgm-volume, sfx}.mjs`; `scripts/audio-duck.mjs`.
- **hyperframes-audio:** `SKILL.md`; `references/{presets, attributes, fx-registry, diagnosis}.md`.
- **embedded-captions:** `SKILL.md`; `references/{rail, caption-grouping}.md`. **hyperframes-studio** `SKILL.md` §4 safe zones. **faceless-explainer** `references/visual-design.md` (caption keep-out).
- **Verified artifacts:**
  - Google Fonts metadata, saved at `scratchpad/gfonts.json`.
  - The HF 0.8.75 `dist/cli.js` font code (`buildFontFaceCss`, `BUNDLED_SUBSET_UNICODE_RANGE`, `EMBEDDED_FONT_DATA`).
  - `media-treatment --capability {presets, finishing, grading, print, palettes, art, essentials, wheels, correction, kuwahara, bloom, twoInkPrint}`.
  - The 22-payload dry-run (`scratchpad/payloads.json`, `scratchpad/mtproj/`).
  - WCAG ratios (`scratchpad/contrast.py`).
