# Claude Diagnosis & Prioritized Plan — Cycle 2 — v2

**Input:** `01_cursor_report.md` + `03_codex_critique_round1.md` (verdict: NEEDS_REVISION, 9 issues) + `03a_accept_reject_log_round1.md` (9/9 ACCEPT).
**Status:** DRAFT v2 — revised per Codex round-1 review, pending round-2 re-review. **No production prompt, generator, or workflow file has been modified.**

## Changes from v1

All 9 accepted issues addressed below (see `03a_accept_reject_log_round1.md` for the per-issue investigation and classification). Headline change: a real data-integrity anomaly, initially under-prioritized in v1, was investigated in depth (isolated queries, credential verification) and is now the top-priority item — ahead of every experiment carried from v1.

---

## 0. NEW — Data-integrity investigation (now the top priority; supersedes v1's dismissal)

**What was found:** 3 videos show `real_pt_day_rows` with a PT day earlier than the PT-equivalent of their own `publishedAt`: `_m0aX_gJbaw` and `AuUpRQZOcwc` (published 2026-07-26, real rows dated PT `2026-07-24`), and `B_i31QRy670` (published 2026-07-26, real row dated PT `2026-07-22`, 4 days earlier).

**Investigation performed (this revision, not deferred):**
1. Verified channel/credential identity via `channels.list?mine=true` for both credential sets used. Confirmed `_m0aX_gJbaw`/`AuUpRQZOcwc` genuinely belong to the Phong Thủy credentials (`channelId=UCabOUyNfseJfu-Xy_KXz2rw`, matching).
2. Found and fixed a real bug in my own investigation: `B_i31QRy670` was first re-checked using the *wrong* (Phong Thủy) credentials. Re-run with the correct Phật giáo credentials (`channelId=UCQRsHSC8dBcLvCvrj7CLvKA`) — video ID and channel match confirmed.
3. Re-ran all 3 as **isolated single-video queries** (not the original bulk multi-video pull). **The anomaly reproduced identically on all 3**, ruling out bulk-query cross-contamination as the cause.

**Conclusion:** this is a real, reproducible phenomenon — not a credentials mix-up, not a bulk-query artifact, not (for 2 of 3) a script bug. The most plausible explanation, not proven: YouTube Studio permits preview playback of a scheduled/private video before it goes public, which could register a small number of genuine views attributed to whenever the preview happened, predating the public `publishedAt`. This cannot be confirmed without YouTube's own internal upload/preview audit log, which is not accessible here.

**Practical resolution applied to this revision:** a quarantine rule — any `real_pt_day_rows` entry whose PT day predates the video's own PT-equivalent publish day is excluded from interpretation entirely (not just downweighted). This affects only small-sample rows (2-3 views each); it does not affect the two large-sample videos (`uHwa6nFBtkc`, `YStIdWWuXcU`), so no §1-level conclusion in this document changes as a result — but the underlying tooling gap (no automatic invariant check) is now Experiment E below, ranked above all v1 experiments.

**Confidence this investigation is complete:** MEDIUM. The credential/query-bug hypotheses are ruled out with direct evidence. The preview-playback hypothesis remains unconfirmed. Given the tiny scale involved (2-3 views per anomalous row) and that no current decision depends on these specific rows, further investigation is not pursued this cycle — but the automated invariant (Experiment E) is added so future occurrences are caught systematically rather than requiring manual re-discovery.

---

## 1. Root-cause analysis (revised)

### 1.1 Two videos have large, real retention samples — but "engagement difference is real" is not yet established

`uHwa6nFBtkc` (853 PT-day views) and `YStIdWWuXcU` (586 PT-day views).

**Corrected from v1:** the bundle's own fields don't reconcile under a shared-denominator assumption:
- `uHwa6nFBtkc`: `estimatedMinutesWatched=151`, `views=853` → 151×60/853 ≈ 10.62s/view — but the reported `averageViewDuration` is 24s.
- `YStIdWWuXcU`: `estimatedMinutesWatched=92`, `views=586` → 92×60/586 ≈ 9.42s/view — but the reported `averageViewDuration` is 14s.

This gap is far larger than rounding error. It's not yet known whether `views`, `estimatedMinutesWatched`, and `averageViewDuration` use the same population/denominator for Shorts specifically (e.g. `views` could count replays differently than the duration metrics do). **Until this is verified against current API documentation or an `engagedViews` field, this diagnosis does not claim the AVD/AVP difference between these two videos is statistically reliable** — only that the API returned substantially different AVD/AVP values for the two videos. The large raw view counts (853, 586) rule out small-sample noise as an explanation for the *view counts themselves*, but do not by themselves validate the derived duration/percentage metrics.

**Confidence: LOW on any interpretation of the retention gap** until the denominator question is resolved (downgraded from v1's MEDIUM).

### 1.2 Duration is a potential design difference — not established as a confound

**Corrected from v1:** the arithmetic (24/27=88.9%, 14/41=34.1%, 91.9%/35.13%=2.62x, 24s/14s=1.71x) is correct, but a smaller absolute-seconds ratio does not prove duration causes or explains the retention-percentage gap — `averageViewPercentage` is duration-normalized by definition, so the two representations will always produce different ratios; this is a mathematical fact about the metric, not evidence of a causal relationship. With one video per channel, duration cannot be separated from hook, content, topic, or audience effects.

**Also corrected:** v1 offered a "loop/rounding methodology" explanation for why 91.9%×27=24.81s doesn't match the reported 24s AVD. That explanation was unsupported speculation with no documentation or field precision to back it up — retracted. The discrepancy is noted as unexplained, not resolved.

**Revised framing:** duration is a potential design difference worth tracking in future data; the current data is insufficient to quantify or attribute any part of the retention gap to it.

### 1.3 `hook_score` persistence gap (carried from cycle 1) — unchanged, still open

No production change has been made. This remains a verified fact, not re-litigated here.

### 1.4 The Analytics pull methodology gap (PT/UTC) — confirmed mechanism, but availability claims scoped down

**Corrected from v1:** the claim that data availability is a "direct consequence" of the PT/UTC mechanism, with "the earliest UTC slot" cleanly explaining which videos have data, does not survive the §0 anomaly — several later-slot videos also show (quarantined) rows on `2026-07-24`, contradicting a simple single-mechanism story. The claim is now scoped to only what was directly tested: querying with `dimensions=day` is interpreted in Pacific Time, and the `2026-07-24` bucket contains 853 real views for `uHwa6nFBtkc` specifically. No broader claim about "entire first-day activity" or a full explanation of every sibling video's availability pattern is made until §0's quarantine/investigation work is extended.

### 1.5 9 of 17 videos still show no processed-day data; the rest are quarantined or too small to interpret

Unchanged from v1 in substance, but reclassified: of the 8 videos with any non-empty `real_pt_day_rows`, 2 are large-sample and usable (§1.1, with the caveat above), 3 are quarantined per §0 (timing-anomalous), and 3 are small-sample (1-3 views) and not quarantined but still uninterpretable at that size.

### 1.6 Traffic overwhelmingly comes from the Shorts feed (unchanged from v1)

Unchanged — still channel-level, wide-window, not attributable to individual videos in this batch.

---

## 2. Prioritization — Impact × Confidence × Effort (revised, with justification per cell)

Scale 1(low)-3(high) for Impact and Confidence; 1(low)-3(high) for Effort (higher = more work). Score = (Impact × Confidence) / Effort. **Scores are ordinal-derived and approximate — not a precise ranking; ties and near-ties should be broken by judgment, not by the decimal value alone.**

| # | Item | Impact | Confidence | Effort | Score | Justification | Verdict |
|---|---|---|---|---|---|---|---|
| E | Add automated PT-day-vs-publish-day invariant check (quarantine anomalous rows automatically) | 2 (prevents future silent misinterpretation) | 3 (mechanism directly demonstrated in §0) | 1 (a validation function on already-fetched data) | **6.0** | Directly closes the gap that caused v1's most serious miss | **Approved → Experiment E, now top priority** |
| A | Rolling-window + per-video day-dimension Analytics pull | 2 | 3 | 2 *(raised from 1 — needs quota/pagination/partial-response handling per Codex)* | **3.0** | Real fetch-logic and test work, not a trivial query-string change | Approved → Experiment A (revised) |
| D | P0-1 hook_score persistence contract (carried from cycle 1) | 3 | 3 | 3 *(raised from 2 — confirmed to touch every generator, not just the runner)* | **3.0** | Codex verified the multi-generator scope directly against code | Approved → Experiment D (revised) |
| C | P0-3 accuracy/tone audit (carried from cycle 1) | 2 | 2 *(lowered from 3 — no defined population/rubric yet, so current confidence in delivering a reliable answer is not yet earned)* | 2 *(raised from 1 — a real rubric + stratified sampling + adjudication is more than a quick read-through)* | **2.0** | Still valuable, but was previously overrated on ease and underrated on rigor needed | Approved → Experiment C (revised) |
| B | Report absolute watched-seconds alongside AVP% | 1 *(lowered — see §1.1, the underlying numbers may not even reconcile, so this is necessary but not sufficient)* | 2 | 1 | **2.0** | Necessary hygiene, not sufficient on its own without the reconciliation check in Experiment B below | Approved → reclassified as reporting control, not an experiment |
| 5 | Duration-shortening content test | 2 | 1 | 2 | 1.0 | Unchanged from v1 | Deferred |
| 6 | Western Zodiac comment-CTA test | 1 | 1 | 2 | 0.5 | Unchanged from v1 | Deferred |

---

## 3. Experiment / action cards (revised)

### Experiment E — Automated PT-day-vs-publish-day quarantine invariant (NEW, top priority)

- **Objective:** stop treating anomalous rows (real views attributed to a PT day before the video's own viewable PT day) as trustworthy `real_pt_day_rows` without manual discovery each time.
- **Change:** add a validation step to the review-pull tooling that computes each video's PT-equivalent publish day and automatically excludes/flags any Analytics row dated earlier, labeling it `quarantined_anomalous_row` rather than `real_pt_day_rows`.
- **Expected metric:** count of quarantined rows per pull, surfaced explicitly in the bundle (not silently dropped).
- **Success criteria:** on this cycle's known dataset, the check correctly flags exactly the 3 rows identified in §0 and does not flag `uHwa6nFBtkc` or `YStIdWWuXcU`.
- **Rollback condition:** none needed — read-only validation logic added to review tooling; does not touch production pipeline code.

### Experiment A — Rolling-window Analytics pull (revised scope/effort)

- **Objective:** retrieve real, already-processed per-day Analytics data without assuming a fixed UTC lag offset (unchanged objective from v1).
- **Change:** same as v1 (rolling ~10-day window, `dimensions=day` per video), but now explicitly scoped to include quota handling, pagination, duplicate-row handling, and partial-response handling — not a one-line query-string change.
- **Expected metrics (split per Codex's recommendation):**
  - *Retrieval correctness:* on a known-good video/day set, the rolling query returns 100% of the rows a single-day control query returns.
  - *Analytical usability:* count of videos per cycle with `views ≥ 500` in `real_pt_day_rows` (explicit threshold, not "materially more than 2/17").
- **Success criteria:** retrieval-correctness test passes on the known-good fixture; usability metric is reported per cycle without a specific target (since it depends on real-world time elapsed, which this experiment cannot control).
- **Rollback condition:** revert to the fixed-window query if quota/pagination handling introduces failures; this is read-only tooling, no production impact either way.

### Experiment D — hook_score persistence contract (revised scope/effort)

- **Objective:** unchanged from cycle 1 — stop discarding `generation_hook_score` before it reaches the registry.
- **Change:** unchanged core design (generator → sidecar → runner → registry), but scope now explicitly acknowledged as touching every generator matching the `write_short_bundle_file(script)`-only pattern (confirmed via code read: `element_luck`, `educational`, `twelve_gods`, `western_zodiac`, `iching`, `zodiac`, `zodiac_month`, `element_color`, `storytelling`), not a single-file change.
- **Expected metric:** unchanged — non-null `generation_hook_score` in the registry for videos generated after this ships.
- **Success criteria (expanded):** must include tests across every generator in scope, missing/corrupt/stale sidecar handling, and registry persistence across a resumed (interrupted-then-restarted) batch run.
- **Rollback condition (expanded):** must cover the generator/sidecar-writing side, the runner's reader side, and any partially-migrated registry data — not just "revert the runner's ingestion step" as v1 stated.

### Experiment C — Accuracy/tone audit (revised, with sampling frame)

- **Objective:** unchanged — determine whether the two confirmed absolute-language instances from cycle 1 are isolated or systemic.
- **Change:** now requires a locked population (e.g. all Phong Thủy scripts published in a defined date range), stratified by generator/category, a defined checklist (absolute claims, anxiety/threat framing, manufactured deadlines, missing uncertainty-hedging, reverent-tone violations), and two independent passes or an adjudication step for disagreements.
- **Expected metric:** numerator/denominator (instances found / scripts reviewed), with evidence examples per instance.
- **Success criteria:** audit completed against the locked population with the defined rubric; a pre-set decision rule applied (e.g. any threat/deadline instance is zero-tolerance and escalates immediately; an absolute-claims rate above a set threshold triggers a rubric-strengthening proposal as a separate follow-up item, not folded into this audit's own success criteria).
- **Rollback condition:** N/A — read-only audit.

### Reporting control B — Report AVD alongside AVP%, with a reconciliation check (reclassified from "Experiment B")

- **Objective:** prevent future reports from citing `averageViewPercentage` without also surfacing whether the underlying fields actually reconcile with each other.
- **Change:** every future report citing AVP must also cite AVD, the video's own duration, and a reconciliation check (`estimatedMinutesWatched × 60 / views` compared against reported AVD). If the two don't match within a reasonable tolerance, the report must carry an explicit warning rather than an interpretation — this is the direct fix for the §1.1 finding.
- **Success criteria:** future reports include the reconciliation check; §1.1 in this document is the reference example of what an unreconciled case should look like (flagged, not interpreted).
- **Rollback condition:** none — reporting format only.

---

## 4. Explicit non-recommendations (revised)

- **Not** proposing a duration-shortening content experiment — unchanged reasoning from v1, reinforced by §1.2's retraction of the causal duration-confound framing.
- **Not** re-opening the Western Zodiac comment-CTA question — unchanged from v1.
- **Not** proposing any category-level cuts or emphasis shifts — unchanged from v1.
- **Not** claiming Experiment A "accumulates" real-retention videos — corrected wording: Experiment A retrieves/observes already-processed data; it does not create new observations or speed up Analytics processing. Data-integrity validation (Experiment E) is a prerequisite for Experiment A and any future duration/category analysis, not an optional add-on.

---

*Next: submit this v2 diagnosis to Codex CLI for round-2 review.*
