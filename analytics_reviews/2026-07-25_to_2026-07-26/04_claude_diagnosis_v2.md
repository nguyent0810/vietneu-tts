# Claude Diagnosis & Improvement Plan — v2 — 2026-07-25 to 2026-07-26

**Input:** `01_cursor_analytics_report.md` (Cursor CLI) + `03_codex_critique_round1.md` (Codex CLI, verdict: CẦN SỬA).
**Status:** DRAFT v2 — revised per Codex round-1 critique, pending Codex round-2 re-review and user approval. **No production prompt or workflow has been modified.** Every recommendation below remains a proposal only.
**Scope:** unchanged from v1 — Phong Thủy is the actionable subject; Phật giáo is cross-channel context only.

## Changes from v1 (in response to Codex round 1)

All 9 required fixes from `03_codex_critique_round1.md` are addressed below. Summary — full detail inline at each numbered point:
1. P0-1 rewritten as a contract change (generator → sidecar metadata → runner → registry), not a one-file additive patch. Risk re-rated none → **low-medium**.
2. Kinh Dịch "which one sounds like you" CTA **dropped**. P1-1 narrowed to Western Zodiac only, risk re-rated low → **medium**, gated on brand review before testing.
3. New **§1.6 + P0-3**: accuracy/tone audit of absolute/anxiety-framed language already live in production content — added as a P0, not skipped.
4. §1.3 retention claim corrected — no longer claims retention alone "immediately distinguishes" discovery from CTR/exposure problems.
5. §1.5 evergreen-anchoring guidance tightened — event anchors require organic content relevance, not just factual truth.
6. §1.1 language downgraded from "dominant signal / root cause" to "notable pattern, untested hypothesis."
7. §2 point 2 (n≥10-15) reframed as a preliminary checkpoint with cohort/version-matching conditions, not a sufficiency threshold.
8. §1.4 now states the comment-CTA idea requires establishing comments as the right KPI first, not assumed.
9. §1.2 "for any video, ever" scoped down to "for these 8 videos, retroactively."

---

## 0. Brand Manifesto constraints (read before any recommendation below)

Checked against `content_repo_clone/CORE_OS/BRAND_BIBLE.md` and `DOMAINS/FENG_SHUI/DOMAIN_GUIDE.md`:

- Core rule: **"accurate, humane, evidence-aware, non-manipulative, clear about uncertainty."**
- Feng Shui-specific: **"calm, reverent, non-manipulative voice,"** must **"treat viewer anxiety about luck/fortune with compassion rather than exploiting it,"** and must **"never structure a video, title, or Short around a manufactured deadline or threat."**
- Governing principle: **"Transform first, refuse only when transformation is impossible."**

**Correction from v1:** v1 claimed the rubric and Brand Manifesto are "aligned by construction." That claim does not survive scrutiny — see §1.6: real, already-published content contains absolute/anxiety-adjacent phrasing that the current rubric evidently does not catch. Alignment is a goal the rubric aims at, not a guaranteed property of the pipeline as it exists today. §3 now includes an explicit audit item (P0-3) to close this gap rather than assume it's closed.

---

## 1. Root-cause analysis

### 1.1 Within-category variance is a notable pattern — not yet a confirmed root cause

Cursor's data: `western_zodiac_short_generator.py` produced both the weakest video (Song Tử, 8 lifetime views) and a mid-strong one (Bạch Dương, 799 views) — a ~100x spread, same generator/category/day. `iching_short_generator.py` shows the same pattern at smaller scale (Càn Vi Thiên 967 vs Tốn Vi Phong 307).

**Revised framing [confidence: LOW]:** this is a striking pattern in the table, not yet a "dominant signal" or established root cause — with 2 observations per category, it's equally consistent with distribution/exposure differences, video age at snapshot time, topic popularity, or noise. "Execution-level factors matter more than category" is a **hypothesis to test**, not a conclusion.

**Also worth noting (missed in v1):** view counts alone can conflate two very different problems — a *discovery* failure (YouTube's algorithm hasn't shown the video to a meaningful test audience yet) and a *retention/quality* failure (shown, but doesn't hold attention). Song Tử's 8 views could be either, and nothing in this data set distinguishes them.

**Like-rate, not just totals (missed in v1):** looking at like/view ratio rather than raw like counts changes the picture somewhat — Càn Vi Thiên (13/967) has a better rate than the top-viewed video (Storytelling kê giường, 11/1120), while Tốn Vi Phong is weak on both dimensions (1/307). This should be tracked as a rate with a minimum-denominator caveat going forward, not just absolute counts.

**What would raise confidence:** retention data *combined with* reach/exposure and traffic-source data — not retention alone (see §1.3) — would meaningfully separate a discovery problem from a retention problem from "just needs more time."

### 1.2 `hook_score` is computed but not carried into the registry — a real pipeline gap, but the fix is a contract change, not a one-file patch

**Fact, verified directly against code and the real registry:** every Phong Thủy generator runs a fact-checked, category-aware judge panel (`short_judge_panel_engine.py`) that computes a real `hook_score` (1-10). `short_batch_runner.py:276` explicitly sets `entry["hook_score"] = None` for every topic other than the default (Phật giáo). All 8 Phong Thủy registry entries confirm this: `"hook_score": null`.

**Corrected from v1 (this was under-specified before):** the reason the score is null isn't a missing field in the runner — it's that the score is **never handed to the runner in the first place**. Each generator's `main()` currently writes only the winning script text to a `.txt` file; the `hook_score`/`history`/category/generator identity computed by `generate_verified_script()` are discarded at that point. The runner reads the `.txt` file later with no way to recover them. Fixing this requires:

- A small sidecar metadata artifact per generated Short (e.g. `{key}.meta.json` next to the script `.txt`), written by the generator at the same time as the script, keyed by a stable identifier that survives the runner's own key-derivation logic.
- Runner-side ingestion of that sidecar into the registry entry, with a schema version field (so future format changes don't silently break old sidecars).
- A separate `generation_hook_score` field, distinct from the Phật-giáo-pipeline's post-hoc hook-review score — these are two different measurements and should not be conflated in the registry schema.
- Selective persistence: the winning strategy, final score, and iteration count — not the full raw judge history (candidate scripts, per-round model feedback) by default, to avoid registry bloat and unnecessary retained model output.

**Honest limits, corrected from v1:**
- `hook_score` is the AI judge's own assessment, not an independent quality signal, and it is post-selection (only threshold-passing scripts get published) — so its range is restricted and its correlation with real-world performance may be weak. This should be treated as a signal to *observe*, not a validated predictor, until tested.
- v1 claimed "no way to ever correlate hook_score with performance, for any video, ever" — this was overstated. It's true that these **8 specific videos** cannot be fixed retroactively (no sidecar was written, no way to recover the discarded score). It is not true of future videos once this fix ships, and is not necessarily true for any older videos where an intermediate `--output-json` artifact happens to still exist.

Consequence, scoped correctly: for this batch, there is no way to check whether the judge's own score predicted this batch's outcome. That gap is closed going forward once P0-1 (§3) ships, not immediately or retroactively for these 8 videos.

### 1.3 Retention data unavailability is a timing artifact — but retention alone will not answer everything once it arrives

Verified directly: querying `youtube_analytics.py` with an older date range (2026-07-10 to 07-24) returns full real rows; the exact window 07-25/07-26 returns zero rows across both channels' entire Analytics API surface. This is API processing lag (~3 days observed), not a data-collection bug.

**Corrected from v1:** v1 claimed retention data would "immediately distinguish a discovery problem from low impressions/CTR." That's a measurement error — retention describes viewer behavior *after* a view has already started; it says nothing on its own about impressions, CTR, or how many people were shown the video (exposure/reach). Distinguishing a discovery problem from a retention problem requires retention data **combined with** reach/exposure and traffic-source data, and ideally the Studio "viewed vs swiped away" metric where available — not retention in isolation.

**Also corrected:** views should ideally be compared at matched post-publish intervals (T+24h / T+48h / T+72h) rather than raw "views as of whenever the report happens to run." **Correction from v2 (Codex round 2):** true T+24/48/72h snapshots require timestamped captures taken at those exact intervals — this pipeline only ever captured one snapshot (lifetime stats around 2026-07-27) for these 8 videos, so that comparison cannot be reconstructed retroactively for the current batch. See P0-2 (§3) for what's actually achievable now vs. only for future cohorts.

### 1.4 Near-zero comment engagement — real gap, but comments may not be the right KPI to optimize first

1 comment across 8 videos. None of the 10 generators currently include an explicit comment-inviting close.

**Confidence: LOW-MEDIUM**, and now with an added caveat missing from v1: before treating "add a comment CTA" as the fix, it's worth establishing that comments are actually the KPI worth optimizing for calm/reverent content. Saves, shares, returning viewers, watch-completion, or subscriber conversion may matter more to this channel's actual goals than comment count — chasing the most visible weak signal risks optimizing the wrong thing. This diagnosis does not have data to say which KPI matters most; §3 reflects that by holding P1-1 for brand review rather than treating it as a low-risk given.

### 1.5 Evergreen content underperformance — reason unconfirmed, and the "fix" needs a stricter guardrail than v1 stated

`element_color_short_generator.py` (evergreen, no date/time anchor) produced the lowest non-outlier view count (79).

**Hypothesis [confidence: LOW], unchanged:** date/context-anchored titles may read as more timely to a scrolling viewer than a timeless title, independent of retention quality.

**Guardrail, tightened from v1:** v1 said the fix should anchor to "a real, already-true detail (season, an actual upcoming event)" rather than inventing a deadline. Codex correctly flagged that this is not sufficient on its own — a real event used *only* to create a sense of "watch now" for otherwise-unrelated evergreen content is still manufactured relevance, even though the date itself is true. The corrected rule: an event/season anchor is only permitted when the content connection is organic, direct, and necessary to the point being made — not simply factually true and convenient.

### 1.6 NEW — Accuracy/tone gap already exists in published content (added per Codex critique, §4)

This section did not exist in v1. Independently verified (not just Codex's claim — I re-grepped the real registry myself and confirmed all four instances) against `output/shorts/Phong Thủy/registry.json`, in content with `"status": "uploaded"`:

- `CONGIAP20260726_ConGiap_01`: *"Mọi việc ... hứa hẹn diễn ra vô cùng thuận lợi"* ("everything promises to go extremely smoothly"), *"vận khí đại cát"* ("extremely auspicious energy") — stated as unhedged fact.
- `MENH_Kim_MauSacHopMenh_01`: *"gây khắc chế và làm năng lượng của bạn mất cân bằng"* ("causes conflict and unbalances your energy") — a causal claim with no hedge language, plus a title framed as a caution ("Đừng vội dùng ví... " — "Don't rush to use...").

**This is a fact, not a hypothesis.** None of these cross into "manufactured deadline/threat" territory (the Domain Guide's most explicit prohibition), but they sit uncomfortably close to the "clear about uncertainty" standard in the core Brand Bible — stated as certainties rather than traditional beliefs/interpretations. This is a real, already-existing content-rigor gap that v1 missed entirely by assuming rubric/manifesto alignment "by construction." It is more concrete and higher-priority than the comment-CTA idea in §1.4, and is added to §3 as P0-3.

---

## 2. Reusable patterns worth carrying into the system

1. **Score-then-discard is a systemic pattern**, not just this batch — same root cause as several bugs fixed earlier this session. Fixing it once in a shared generator→registry contract (§1.2) benefits every future batch.
2. **Small-batch, high-variance categories need a bigger sample before category-level judgments are safe — but "bigger" must also mean "comparable."** Corrected from v1: an n≥10-15 threshold is a **preliminary operational checkpoint**, not a statistically sufficient condition. It only means something if the cohort is also age-matched (similar time since publish) and run under a fixed prompt version — otherwise more samples just adds more confounded noise, not more signal.
3. **The retention-rubric + hook-word-count-cap fix built earlier this session was not active for this batch.** Corrected framing from v1: next week's batch under that fix is not simply "a bigger sample of the same thing" — it's a different cohort/prompt-version. Comparing the two batches should be treated as a version comparison, not a sample-size increase of one continuous population.

---

## 3. Prioritized improvement plan (proposals only — none applied)

### P0 — do first

**P0-1 (re-scoped). Build a generator→sidecar-metadata→runner→registry contract to persist `generation_hook_score`, winning strategy, iteration count, and category/generator identity.**
Effort: **medium** (touches every generator's output step + `short_batch_runner.py` ingestion + a new registry schema field + a schema version marker). Risk: **low-medium**, not none — real risks are metadata/key-mapping drift, registry schema versioning, and avoiding full-history bloat (persist score + winning strategy + iteration count, not full raw candidate/feedback history by default). Confidence this is worth doing: HIGH — the underlying gap is a verified fact (§1.2), but the fix is a pipeline-contract change, not a single-file additive patch.

**P0-2 (re-scoped again per Codex round 2). Re-run this same Review & Analytics process in ~24-48h**, once Analytics API has processed 07-25/07-26 — with corrections from both rounds:
- Verify non-zero row coverage before treating the re-run as valid (don't assume the lag has cleared just because the calendar date has passed).
- **For the current 8-video batch specifically:** true T+24h/T+48h/T+72h snapshots are **not reconstructable** — this pipeline only captured one lifetime-stat snapshot (~2026-07-27) per video, not repeated timestamped pulls. The re-run should instead use Analytics' **per-day** rows (once available) to build day-level, not hour-precise, age-matched windows, and must explicitly label this as a daily approximation, not a true T+24/48/72h snapshot.
- **For future batches:** if hour-precision age-matching is actually wanted, it requires scheduling repeated Data API snapshot pulls at fixed post-publish offsets going forward — a new, small monitoring task, not something P0-2's one-time re-run can retroactively provide.
Risk: none (read-only). Confidence: HIGH that this unlocks real per-day data for the current batch; retention alone will still need combining with reach/exposure (§1.3) to fully test hypothesis 1.1.

**P0-3 (NEW). Audit existing published Phong Thủy scripts for absolute/anxiety-framed phrasing (§1.6) and assess whether the current judge-panel rubric needs a stronger uncertainty-hedging check.** This is a review/audit task, not a rewrite of already-published content — the two confirmed instances are already live; the point is understanding whether the rubric has a systemic blind spot before more content ships with the same pattern. Effort: small (rubric review + a sample re-read of recent scripts). Risk: none (read-only audit). Confidence: HIGH — the instances found are verified fact, not hypothesis.

### P1 — needs brand review before testing (downgraded from "safe to test" in v1)

**P1-1 (narrowed and re-rated). Add an identity-based comment-inviting close to Western Zodiac only** (e.g., "which one sounds like you") — **Kinh Dịch is dropped entirely from this recommendation.** Kinh Dịch's generator explicitly forbids implying "this is your hexagram/today's reading for you"; an identity-CTA risks quietly crossing that exact line. Even for Western Zodiac, this remains a content change made *in order to* increase engagement — it should not be described as risk-free just because the CTA itself is phrased as a genuine question. Effort: small (1 prompt file, not 2). **Risk: medium** (re-rated from low), reversible, but requires: (a) confirming comments are a KPI worth optimizing for this channel first (§1.4), and (b) a brand-tone review of the specific CTA wording before any test batch, not just a self-check against §0.

**P1-2. Hold off on category-level cuts or emphasis shifts until sample size reaches ~10-15 videos per category, AND those videos are age-matched and share a fixed prompt version.** Process recommendation — reframed as a preliminary checkpoint, not a sufficiency threshold (see §2 point 2).

### P2 — needs more data before committing

**P2-1. Investigate evergreen-content hook specificity** (§1.5) — only after P0-2 provides matched-interval view/retention data. If pursued, any event/season anchor must have organic, necessary content relevance — not just factual truth — per the tightened guardrail in §1.5.

---

## 4. Explicit non-recommendations (resolved contradictions from v1)

- **Not** proposing to manufacture urgency/deadlines on evergreen content (§1.5) — and the anchoring guardrail is now tightened so a technically-true-but-unrelated event doesn't count as an exception.
- **Not** proposing to drop Category 4 or Category 1 evergreen based on this week's numbers — sample size makes this premature.
- **Revised from v1:** v1 claimed no recommendation here changes tone/rigor "in pursuit of engagement" and that "none of this week's findings implicate content accuracy." Both claims no longer hold cleanly: P1-1 *is* a tone-adjacent change made for engagement (now explicitly labeled as such and gated on brand review, not claimed to be risk-free), and §1.6/P0-3 shows an accuracy/rigor gap does already exist in production content, independent of any recommendation in this plan. This plan does not propose loosening rigor further — but it no longer claims rigor is already fully intact either.

---

*Next: submit this v2 diagnosis to Codex CLI for round-2 critique (artifact 05). If Codex returns APPROVED or only minor non-blocking notes, proceed to the final summary artifact (per the user's workflow, step 5).*
