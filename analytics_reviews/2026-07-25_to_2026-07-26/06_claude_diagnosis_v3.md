# Claude Diagnosis & Improvement Plan — v3 — 2026-07-25 to 2026-07-26

**Input:** `01_cursor_analytics_report.md` (Cursor CLI) + `03_codex_critique_round1.md` + `05_codex_critique_round2.md` (Codex CLI, round 2 verdict: CẦN SỬA, 8/9 points resolved, 1 High remaining).
**Status:** DRAFT v3 — v2 plus the single remaining round-2 fix (retroactive-snapshot achievability, §1.3/P0-2). Pending Codex round-3 re-review and user approval. **No production prompt or workflow has been modified.** Every recommendation below remains a proposal only.
**Scope:** unchanged — Phong Thủy is the actionable subject; Phật giáo is cross-channel context only.

## Changes from v2 (in response to Codex round 2)

Round 2 confirmed 8 of 9 round-1 fixes as fully resolved (P0-1 contract redesign, Kinh Dịch CTA removal, accuracy/tone audit + "aligned by construction" retraction, event-anchoring guardrail, causal-language downgrade, n≥10-15 reframing, KPI-before-comments, and the "for any video, ever" scoping — this last one further confirmed by Codex directly searching for and finding no surviving sidecar/log artifacts for the 8 videos).

One High-severity issue remained: §1.3 and P0-2 promised comparing the current 8-video batch at true T+24h/T+48h/T+72h post-publish snapshots. Codex verified this pipeline only ever captured one lifetime-stat snapshot (~2026-07-27) per video — not repeated timestamped pulls — so that exact comparison is not reconstructable retroactively for this batch. Fixed in §1.3 and P0-2 below: the current batch now gets an explicitly-labeled **daily approximation** from per-day Analytics rows; true hour-precision snapshots are scoped to **future cohorts only**, contingent on a new scheduled-pull mechanism that doesn't exist yet.

(All other sections are unchanged from v2 and are included in full below for a single self-contained artifact, per the requirement to save each revision as its own versioned artifact.)

---

## 0. Brand Manifesto constraints (read before any recommendation below)

Checked against `content_repo_clone/CORE_OS/BRAND_BIBLE.md` and `DOMAINS/FENG_SHUI/DOMAIN_GUIDE.md`:

- Core rule: **"accurate, humane, evidence-aware, non-manipulative, clear about uncertainty."**
- Feng Shui-specific: **"calm, reverent, non-manipulative voice,"** must **"treat viewer anxiety about luck/fortune with compassion rather than exploiting it,"** and must **"never structure a video, title, or Short around a manufactured deadline or threat."**
- Governing principle: **"Transform first, refuse only when transformation is impossible."**

Note: v1 claimed the rubric and Brand Manifesto are "aligned by construction." That claim was retracted in v2 — see §1.6: real, already-published content contains absolute/anxiety-adjacent phrasing the current rubric evidently does not catch. Alignment is a goal the rubric aims at, not a guaranteed property of the pipeline as it exists today. §3 includes an explicit audit item (P0-3) to close this gap rather than assume it's closed.

---

## 1. Root-cause analysis

### 1.1 Within-category variance is a notable pattern — not yet a confirmed root cause

Cursor's data: `western_zodiac_short_generator.py` produced both the weakest video (Song Tử, 8 lifetime views) and a mid-strong one (Bạch Dương, 799 views) — a ~100x spread, same generator/category/day. `iching_short_generator.py` shows the same pattern at smaller scale (Càn Vi Thiên 967 vs Tốn Vi Phong 307).

**[confidence: LOW]:** this is a striking pattern in the table, not yet an established root cause — with 2 observations per category, it's equally consistent with distribution/exposure differences, video age at snapshot time, topic popularity, or noise. "Execution-level factors matter more than category" is a **hypothesis to test**, not a conclusion.

**View counts alone can conflate two different problems:** a *discovery* failure (YouTube's algorithm hasn't shown the video to a meaningful test audience yet) and a *retention/quality* failure (shown, but doesn't hold attention). Song Tử's 8 views could be either, and nothing in this data set distinguishes them.

**Like-rate, not just totals:** Càn Vi Thiên (13/967) has a better like/view rate than the top-viewed video (Storytelling kê giường, 11/1120), while Tốn Vi Phong is weak on both dimensions (1/307). Track as a rate with a minimum-denominator caveat going forward, not just absolute counts.

**What would raise confidence:** retention data *combined with* reach/exposure and traffic-source data — not retention alone (see §1.3) — would meaningfully separate a discovery problem from a retention problem from "just needs more time."

### 1.2 `hook_score` is computed but not carried into the registry — a real pipeline gap, but the fix is a contract change, not a one-file patch

**Fact, verified directly against code and the real registry:** every Phong Thủy generator runs a fact-checked, category-aware judge panel (`short_judge_panel_engine.py`) that computes a real `hook_score` (1-10). `short_batch_runner.py:276` explicitly sets `entry["hook_score"] = None` for every topic other than the default (Phật giáo). All 8 Phong Thủy registry entries confirm this: `"hook_score": null`.

The reason the score is null isn't a missing field in the runner — the score is **never handed to the runner in the first place**. Each generator's `main()` currently writes only the winning script text to a `.txt` file; the `hook_score`/`history`/category/generator identity computed by `generate_verified_script()` are discarded at that point. The runner reads the `.txt` file later with no way to recover them. Fixing this requires:

- A small sidecar metadata artifact per generated Short (e.g. `{key}.meta.json` next to the script `.txt`), written by the generator at the same time as the script, keyed by a stable identifier that survives the runner's own key-derivation logic.
- Runner-side ingestion of that sidecar into the registry entry, with a schema version field (so future format changes don't silently break old sidecars).
- A separate `generation_hook_score` field, distinct from the Phật-giáo-pipeline's post-hoc hook-review score — these are two different measurements and should not be conflated in the registry schema.
- Selective persistence: the winning strategy, final score, and iteration count — not the full raw judge history (candidate scripts, per-round model feedback) by default, to avoid registry bloat and unnecessary retained model output.

**Honest limits:**
- `hook_score` is the AI judge's own assessment, not an independent quality signal, and it is post-selection (only threshold-passing scripts get published) — so its range is restricted and its correlation with real-world performance may be weak. Treat as a signal to *observe*, not a validated predictor, until tested.
- These **8 specific videos** cannot be fixed retroactively (no sidecar was written; Codex independently confirmed no surviving `--output-json`/log artifact exists for any of them). It is not true of future videos once this fix ships.

Consequence, scoped correctly: for this batch, there is no way to check whether the judge's own score predicted this batch's outcome. That gap closes going forward once P0-1 (§3) ships, not retroactively for these 8 videos.

### 1.3 Retention data unavailability is a timing artifact — and what's actually reconstructable for this batch is more limited than "matched snapshots"

Verified directly: querying `youtube_analytics.py` with an older date range (2026-07-10 to 07-24) returns full real rows; the exact window 07-25/07-26 returns zero rows across both channels' entire Analytics API surface. This is API processing lag (~3 days observed), not a data-collection bug.

Retention data alone will not "immediately distinguish" a discovery problem from a CTR/exposure problem — that claim is a measurement error. Retention describes viewer behavior *after* a view has already started; it says nothing on its own about impressions, CTR, or reach. Distinguishing a discovery problem from a retention problem requires retention data **combined with** reach/exposure and traffic-source data, and ideally the Studio "viewed vs swiped away" metric where available — not retention in isolation.

**Fixed per Codex round 2:** for the *current 8-video batch*, true T+24h/T+48h/T+72h snapshots are not achievable — this pipeline only ever captured one lifetime-stat snapshot (~2026-07-27) per video, not repeated timestamped pulls at those exact offsets. What P0-2 (§3) can actually deliver for this batch is **per-day Analytics rows, once processed**, used as a labeled daily approximation of age-matched comparison — not a true hour-precision snapshot. Genuine T+24/48/72h snapshot comparison is only possible for **future cohorts**, and only if a new scheduled-pull mechanism is built for it (not yet built, not proposed as required here).

### 1.4 Near-zero comment engagement — real gap, but comments may not be the right KPI to optimize first

1 comment across 8 videos. None of the 10 generators currently include an explicit comment-inviting close.

**Confidence: LOW-MEDIUM.** Before treating "add a comment CTA" as the fix, it's worth establishing that comments are actually the KPI worth optimizing for calm/reverent content. Saves, shares, returning viewers, watch-completion, or subscriber conversion may matter more to this channel's actual goals than comment count — chasing the most visible weak signal risks optimizing the wrong thing. This diagnosis does not have data to say which KPI matters most; §3 reflects that by holding P1-1 for brand review rather than treating it as a low-risk given.

### 1.5 Evergreen content underperformance — reason unconfirmed, guardrail on the "fix" is strict

`element_color_short_generator.py` (evergreen, no date/time anchor) produced the lowest non-outlier view count (79).

**Hypothesis [confidence: LOW]:** date/context-anchored titles may read as more timely to a scrolling viewer than a timeless title, independent of retention quality.

**Guardrail:** anchoring to "a real, already-true detail (season, an actual upcoming event)" is not sufficient on its own — a real event used *only* to create a sense of "watch now" for otherwise-unrelated evergreen content is still manufactured relevance, even though the date itself is true. An event/season anchor is only permitted when the content connection is organic, direct, and necessary to the point being made — not simply factually true and convenient.

### 1.6 Accuracy/tone gap already exists in published content

Independently verified (re-grepped the real registry myself and confirmed all four instances) against `output/shorts/Phong Thủy/registry.json`, in content with `"status": "uploaded"`:

- `CONGIAP20260726_ConGiap_01`: *"Mọi việc ... hứa hẹn diễn ra vô cùng thuận lợi"* ("everything promises to go extremely smoothly"), *"vận khí đại cát"* ("extremely auspicious energy") — stated as unhedged fact.
- `MENH_Kim_MauSacHopMenh_01`: *"gây khắc chế và làm năng lượng của bạn mất cân bằng"* ("causes conflict and unbalances your energy") — a causal claim with no hedge language, plus a title framed as a caution ("Đừng vội dùng ví... " — "Don't rush to use...").

**This is a fact, not a hypothesis.** None of these cross into "manufactured deadline/threat" territory (the Domain Guide's most explicit prohibition), but they sit uncomfortably close to the "clear about uncertainty" standard in the core Brand Bible — stated as certainties rather than traditional beliefs/interpretations. This is a real, already-existing content-rigor gap, more concrete and higher-priority than the comment-CTA idea in §1.4, and is addressed in §3 as P0-3.

---

## 2. Reusable patterns worth carrying into the system

1. **Score-then-discard is a systemic pattern**, not just this batch — same root cause as several bugs fixed earlier this session. Fixing it once in a shared generator→registry contract (§1.2) benefits every future batch.
2. **Small-batch, high-variance categories need a bigger sample before category-level judgments are safe — but "bigger" must also mean "comparable."** n≥10-15 is a **preliminary operational checkpoint**, not a statistically sufficient condition. It only means something if the cohort is also age-matched (similar time since publish) and run under a fixed prompt version — otherwise more samples just adds more confounded noise, not more signal.
3. **The retention-rubric + hook-word-count-cap fix built earlier this session was not active for this batch.** Next week's batch under that fix is not simply "a bigger sample of the same thing" — it's a different cohort/prompt-version. Comparing the two batches should be treated as a version comparison, not a sample-size increase of one continuous population.

---

## 3. Prioritized improvement plan (proposals only — none applied)

### P0 — do first

**P0-1. Build a generator→sidecar-metadata→runner→registry contract to persist `generation_hook_score`, winning strategy, iteration count, and category/generator identity.**
Effort: **medium** (touches every generator's output step + `short_batch_runner.py` ingestion + a new registry schema field + a schema version marker). Risk: **low-medium**, not none — real risks are metadata/key-mapping drift, registry schema versioning, and avoiding full-history bloat (persist score + winning strategy + iteration count, not full raw candidate/feedback history by default). Confidence this is worth doing: HIGH — the underlying gap is a verified fact (§1.2), but the fix is a pipeline-contract change, not a single-file additive patch.

**P0-2. Re-run this same Review & Analytics process in ~24-48h**, once Analytics API has processed 07-25/07-26:
- Verify non-zero row coverage before treating the re-run as valid (don't assume the lag has cleared just because the calendar date has passed).
- **For the current 8-video batch:** true T+24h/T+48h/T+72h snapshots are **not reconstructable** — only one lifetime-stat snapshot exists per video. Use per-day Analytics rows instead, explicitly labeled as a **daily approximation**, not an hour-precision snapshot.
- **For future batches:** true hour-precision age-matching requires a new, small scheduled-pull mechanism (repeated Data API snapshots at fixed post-publish offsets) that does not exist yet — out of scope for this P0-2 re-run itself.
Risk: none (read-only). Confidence: HIGH that this unlocks real per-day data for the current batch; retention alone will still need combining with reach/exposure (§1.3) to fully test hypothesis 1.1.

**P0-3. Audit existing published Phong Thủy scripts for absolute/anxiety-framed phrasing (§1.6) and assess whether the current judge-panel rubric needs a stronger uncertainty-hedging check.** Review/audit task, not a rewrite of already-published content — the two confirmed instances are already live; the point is understanding whether the rubric has a systemic blind spot before more content ships with the same pattern. Effort: small (rubric review + a sample re-read of recent scripts). Risk: none (read-only audit). Confidence: HIGH — the instances found are verified fact, not hypothesis.

### P1 — needs brand review before testing

**P1-1 (narrowed). Add an identity-based comment-inviting close to Western Zodiac only** (e.g., "which one sounds like you") — **Kinh Dịch is dropped entirely.** Kinh Dịch's generator explicitly forbids implying "this is your hexagram/today's reading for you"; an identity-CTA risks quietly crossing that exact line. Even for Western Zodiac, this remains a content change made *in order to* increase engagement — not risk-free just because the CTA is phrased as a genuine question. Effort: small (1 prompt file). **Risk: medium**, reversible, but requires: (a) confirming comments are a KPI worth optimizing for this channel first (§1.4), and (b) a brand-tone review of the specific CTA wording before any test batch.

**P1-2. Hold off on category-level cuts or emphasis shifts until sample size reaches ~10-15 videos per category, AND those videos are age-matched and share a fixed prompt version.** Process recommendation — a preliminary checkpoint, not a sufficiency threshold (see §2 point 2).

### P2 — needs more data before committing

**P2-1. Investigate evergreen-content hook specificity** (§1.5) — only after P0-2 provides day-level view data for the current batch (or true snapshot data for a future cohort). If pursued, any event/season anchor must have organic, necessary content relevance — not just factual truth — per the guardrail in §1.5.

---

## 4. Explicit non-recommendations

- **Not** proposing to manufacture urgency/deadlines on evergreen content (§1.5) — the anchoring guardrail means a technically-true-but-unrelated event doesn't count as an exception.
- **Not** proposing to drop Category 4 or Category 1 evergreen based on this week's numbers — sample size makes this premature.
- P1-1 *is* a tone-adjacent change made for engagement (explicitly labeled as such and gated on brand review, not claimed risk-free), and §1.6/P0-3 shows an accuracy/rigor gap already exists in production content, independent of any recommendation in this plan. This plan does not propose loosening rigor further — but does not claim rigor is already fully intact either.

---

*Next: submit this v3 diagnosis to Codex CLI for round-3 critique (artifact 07). If Codex returns APPROVED or only minor non-blocking notes, proceed to the final summary artifact (per the user's workflow, step 5).*
