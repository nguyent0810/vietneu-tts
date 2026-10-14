# Claude Diagnosis & Prioritized Plan — Cycle 2 — v1

**Input:** `00a_pt_utc_finding.md` + `00_raw_data_bundle_v2.json` + `01_cursor_report.md` (Cursor CLI, Data Analyst role — facts/metrics only, no recommendations).
**Status:** DRAFT v1 — pending Codex CLI independent review. **No production prompt, generator, or workflow file has been modified.**
**Carried forward from cycle 1** (`analytics_reviews/2026-07-25_to_2026-07-26/06_claude_diagnosis_v3.md`, Codex-approved): P0-1 (hook_score persistence contract) and P0-3 (accuracy/tone audit) were approved but **not yet applied** — no production change has happened since, so both remain open. This diagnosis re-evaluates them against new cycle-2 evidence rather than re-deriving them from scratch.

---

## 1. Root-cause analysis

### 1.1 FACT: for the first time this review process, two videos have genuinely interpretable retention data

`uHwa6nFBtkc` (Phong Thủy, 853 PT-day views) and `YStIdWWuXcU` (Phật giáo, 586 PT-day views) both landed in the one YouTube-Analytics-processed PT day (`2026-07-24`) captured in this cycle's pull. This is a direct consequence of the PT/UTC finding (`00a`) — these two happened to be the earliest-UTC-slot videos, which is why their activity fell on an already-processed day while their same-day siblings did not.

### 1.2 The 91.9% vs 35.13% retention gap is real, but the percentage framing overstates it — duration is a confound

**Verified by direct calculation (not Cursor's claim — I recomputed this myself against the raw bundle):**
- `uHwa6nFBtkc`: duration 27s, average view duration 24s → 24/27 = 88.9% (reported AVP: 91.9%, consistent within YouTube's own rounding/loop-inclusive methodology).
- `YStIdWWuXcU`: duration 41s, average view duration 14s → 14/41 = 34.1% (reported AVP: 35.13%, consistent).

**The percentage gap (91.9% vs 35.13%, a ~2.6x difference) is much larger than the absolute-seconds gap (24s vs 14s, a 1.7x difference)**, because `averageViewPercentage` is normalized by video length, and these two videos have very different lengths (27s vs 41s). A shorter video needs less absolute watch time to reach a high percentage of its own length. This does not mean the percentage difference is wrong — both numbers are real — but treating "91.9% vs 35.13%" as the headline finding, without also reporting the absolute-seconds numbers, would overstate how different these two videos' viewer engagement actually was.

**Confidence: MEDIUM that the underlying engagement difference is real** (both videos have solid sample sizes — 853 and 586 views — so the numbers themselves aren't noise). **Confidence: LOW that we can attribute the difference to any specific cause** (content style, hook, topic, duration itself) — this is n=1 video per channel; a single pair cannot support a channel-level or category-level conclusion.

### 1.3 `hook_score` persistence gap (carried from cycle 1) is unchanged and now more valuable to fix

Cycle 1 identified and Codex-approved a plan to persist `generation_hook_score` per video (currently discarded after generation — `short_batch_runner.py:276` sets it to `null` for all non-default topics). That fix has **not been applied** — no production file has changed. This cycle's new real retention data (§1.1) makes this gap more costly: even now that we finally have two videos with trustworthy retention numbers, there is still no `hook_score` on file for either of them to check against. The correlation this fix would eventually enable remains entirely unrealized.

### 1.4 The Analytics pull methodology itself was part of the problem, not just API lag

Confirmed (`00a`): querying with a fixed 1-2 day UTC-labeled window silently misses data that is actually available, because YouTube buckets by Pacific Time. A rolling-window pull with `dimensions=day` per video — reading off whichever days actually return non-zero rows — retrieves real data that a fixed-window UTC query would report as "no data available." This is a **process/tooling gap**, independent of any content decision, and independent of the underlying (still real) processing lag.

### 1.5 9 of 17 videos still show no processed-day data at all; 6 more have samples too small to interpret

This is expected given the mechanism in §1.4 — same-day videos published a few hours later than the earliest slot fall on a PT day that hasn't been processed yet. Cursor's report correctly declines to interpret the 1-3 view rows despite their AVP being real (>100%, a genuine Shorts-loop artifact, not an error) — sample size makes them uninformative regardless of the metric's validity.

### 1.6 Traffic overwhelmingly comes from the Shorts feed on both channels

Phong Thủy: 3377/4286 ≈ 79% of the wide-window traffic-source views came from `SHORTS`. Phật giáo: 9527/9847 ≈ 97%. **Confidence: LOW on any interpretation** — this is channel-level, wide-window (07-20 to 07-27) data that includes videos outside this cycle's 17-video batch, and cannot be attributed to individual videos with the data available. Recorded as a fact worth monitoring, not a basis for action yet.

### 1.7 Open, unresolved anomaly: 3 videos show `real_pt_day_rows` dated before their own `published_at_utc`

`_m0aX_gJbaw`, `AuUpRQZOcwc` (both published 2026-07-26, real row dated PT `2026-07-24`), and `B_i31QRy670` (published 2026-07-26, real row dated PT `2026-07-22`, i.e. 4 days earlier). Cursor flagged this correctly as very-low-confidence given n=2-3 views per row. I looked for a mundane explanation (e.g. views accrued while unlisted before going public) but do not have enough information to confirm one. **This is an open question, not resolved in this cycle** — flagged for the next pull rather than investigated further now, since at n=2-3 it cannot change any real decision either way.

---

## 2. Prioritization — Impact × Confidence × Effort

Scale 1 (low) – 3 (high) for Impact and Confidence; 1 (low) – 3 (high) for Effort. Score = (Impact × Confidence) / Effort — higher is better return for the work involved.

| # | Item | Impact | Confidence | Effort | Score | Verdict |
|---|---|---|---|---|---|---|
| 1 | Rolling-window + per-video day-dimension Analytics pull (replace fixed UTC 1-2 day window) | 2 | 3 | 1 | **6.0** | Approved → Experiment A |
| 2 | Report retention as absolute avg-watched-seconds alongside AVP%, flag duration confound explicitly | 2 | 3 | 1 | **6.0** | Approved → Experiment B |
| 3 | P0-3 accuracy/tone audit of absolute-language content (carried from cycle 1, still undone) | 2 | 3 | 1 | **6.0** | Approved → Experiment C |
| 4 | P0-1 hook_score persistence contract (carried from cycle 1, still undone) | 3 | 3 | 2 | **4.5** | Approved → Experiment D |
| 5 | Duration-shortening content test | 2 | 1 | 2 | 1.0 | **Deferred** — n=1 video pair, nowhere near enough data to justify a content change |
| 6 | Western Zodiac comment-CTA test (P1-1, carried from cycle 1) | 1 | 1 | 2 | 0.5 | **Deferred** — KPI-priority question from cycle 1 still unresolved; no new evidence this cycle |
| 7 | Any category-level cuts/emphasis shifts | — | — | — | — | **Still not applicable** — sample size unchanged from cycle 1 |

Items 1-4 are converted into experiment/action cards below (§3). Items 5-7 are explicitly not converted — listed in §4 as non-recommendations for this cycle, not silently dropped.

---

## 3. Experiment cards (approved items only — none applied yet, pending your sign-off)

### Experiment A — Rolling-window Analytics pull

- **Objective:** stop silently missing real, already-processed Analytics data due to UTC/PT day-boundary mismatch.
- **Change:** replace the fixed 1-2 day UTC-labeled query window in the review-pull script with a rolling ~10-day window using `dimensions=day` per video; read off whichever rows are actually non-zero rather than assuming a fixed lag offset.
- **Expected metric:** number of videos per review cycle with usable (`views > 0`) day-level retention data.
- **Success criteria:** each future review cycle retrieves real per-day data for materially more than 2/17 videos (this cycle's count), assuming enough real-world time has passed since publish.
- **Rollback condition:** none needed — this is a read-only query-pattern change to the review tooling, not a production content/pipeline change. If it produces confusing output, revert to the fixed-window query as a fallback.
- **Scope:** analytics review tooling only (the fetch script used by this workflow) — does not touch `youtube_analytics.py`'s public function signatures or any generator/runner code.

### Experiment B — Report absolute watched-seconds alongside AVP%

- **Objective:** prevent future reviews from overstating retention differences between videos of different durations.
- **Change:** every future Cursor/Claude report that cites `averageViewPercentage` must also cite `averageViewDuration` (seconds) and the video's own duration, so the reader can see both the normalized and absolute view.
- **Expected metric:** N/A (a reporting-format requirement, not a content metric).
- **Success criteria:** future reports include both figures side by side wherever AVP is discussed; this diagnosis §1.2 is the reference example.
- **Rollback condition:** none — this only affects report formatting.

### Experiment C — Accuracy/tone audit of absolute-language content (carried from cycle 1 P0-3)

- **Objective:** confirm whether the two already-verified instances of unhedged absolute/anxiety-adjacent phrasing (cycle 1, `CONGIAP20260726_ConGiap_01`, `MENH_Kim_MauSacHopMenh_01`) are isolated or indicate a systemic rubric gap.
- **Change:** read-only audit of recently-published Phong Thủy scripts against the judge-panel rubric's uncertainty-hedging requirements; no content is rewritten as part of this audit.
- **Expected metric:** count of additional instances found, categorized by severity.
- **Success criteria:** audit completed and documented; if additional instances are found, a follow-up recommendation (rubric strengthening) is proposed as a separate, explicitly-flagged next step — not silently folded into this audit.
- **Rollback condition:** N/A — read-only.

### Experiment D — Ship the hook_score persistence contract (carried from cycle 1 P0-1)

- **Objective:** stop discarding the judge panel's computed `hook_score` before it reaches the registry, so future batches can be checked against real outcomes — including the two videos in this cycle that, for the first time, have real retention data to eventually check it against.
- **Change (unchanged from cycle 1's Codex-approved scope):** generator writes a sidecar metadata file per generated Short → runner ingests it into the registry as `generation_hook_score` (kept separate from the Phật-giáo hook-review score) → persist winning strategy + iteration count, not full raw judge history.
- **Expected metric:** for all Phong Thủy videos generated after this ships, `generation_hook_score` is non-null in the registry.
- **Success criteria:** next batch's registry entries show real scores; after enough future videos accumulate real per-day retention data (via Experiment A), a first real correlation check becomes possible — not part of this experiment's own success criteria, but the thing it unlocks.
- **Rollback condition:** if the sidecar/ingestion contract breaks the batch runner, revert the runner's ingestion step only — this does not touch script generation or the judge panel itself, so a revert cannot affect what gets published.

---

## 4. Explicit non-recommendations for this cycle

- **Not** proposing a duration-shortening content experiment — one video pair (n=1 per channel) cannot support any conclusion about optimal duration; would need many more real-retention videos first (which Experiment A is intended to help accumulate over time).
- **Not** re-opening the Western Zodiac comment-CTA question (cycle 1 P1-1) — no new evidence this cycle bears on whether comments are the right KPI to optimize; still held pending brand review, unchanged from cycle 1.
- **Not** proposing any category-level cuts or emphasis shifts — same sample-size constraint as cycle 1, unchanged.
- **Not** resolving the §1.7 timing anomaly — flagged for future data, not investigated further now given its negligible sample size and inability to change any current decision.

---

*Next: submit this diagnosis to Codex CLI for independent adversarial review — Severity/Evidence/Recommendation per issue, verdict APPROVED or NEEDS_REVISION.*
