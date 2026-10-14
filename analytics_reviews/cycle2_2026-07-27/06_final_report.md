# YouTube Analytics Review — Cycle 2 — Final Report

**Status: COMPLETE.** Codex approved the final plan after 5 review rounds. **No production prompt, generator, workflow file, or content has been modified.** Everything below is either a verified fact, an explicitly-labeled hypothesis, or a reviewed proposal awaiting your go-ahead.

**Full artifact trail:** `analytics_reviews/cycle2_2026-07-27/` — `00_raw_data_bundle_v2.json` → `00a_pt_utc_finding.md` → `01_cursor_report.md` → `02_claude_diagnosis_v1.md` → `03_codex_critique_round1.md` (NEEDS_REVISION) → `03a` accept log → `04_claude_diagnosis_v2.md` → `03c` round 2 (NEEDS_REVISION) → `03b` accept log → `04_claude_diagnosis_v3.md` → `03d` round 3 (NEEDS_REVISION) → `03e` accept log → `04_claude_diagnosis_v4.md` → `03f` round 4 (NEEDS_REVISION) → `03g` accept log → `04_claude_diagnosis_v4.md` (patched) → `03h` round 5 (**APPROVED**) → `05_candidate_knowledge_package.md` → this file.

---

## 1. Cursor's key findings (Data Analyst role — facts/metrics only, no recommendations)

- Independently confirmed the PT/UTC day-bucketing mechanism and its consequence: of 17 videos in this batch, only 2 have Analytics day-level data with a large enough sample to mean anything (`uHwa6nFBtkc`: 853 views; `YStIdWWuXcU`: 586 views); 6 more have real but uninterpretably small rows (1-3 views); 9 have no processed-day data at all yet.
- Full per-video table with lifetime stats, real PT-day rows where available, and explicit sample-size warnings on every small-sample number.
- Channel-level traffic sources (wide window): both channels' views are dominated by the Shorts feed (Phong Thủy ~79%, Phật giáo ~97%).
- Direct comparison of the 2 usable videos across every available metric, described without interpretation.
- 16 FACTS, 7 HYPOTHESES (all explicitly confidence-tagged), zero recommendations — role boundary respected throughout.

## 2. Claude's diagnosis (final, approved version — full detail in `04_claude_diagnosis_v4.md`)

**Confirmed facts, independently verified (not taken from Cursor or Codex on faith):**
- The two large-sample videos' `averageViewDuration`/`estimatedMinutesWatched`/`views` fields do not reconcile under a shared-denominator assumption (10.62s and 9.42s implied vs. 24s/14s reported) — real, unexplained.
- 3 videos show Analytics rows dated before their own public `publishedAt`, reproduced on isolated, credential-verified queries — real, unexplained (most plausible but unconfirmed explanation: pre-public Studio preview views).
- `hook_score` is computed by every generator's judge panel and discarded before reaching the registry — unchanged from cycle 1, still unfixed.
- Absolute/anxiety-adjacent phrasing exists in already-published content (carried from cycle 1, independently reverified this cycle).

**Root-cause hypotheses, all explicitly low-to-medium confidence:** duration as a potential (not established) design difference in retention; the engagement gap between the two large-sample videos being "real" pending denominator verification; whether the pre-publish-view anomaly reflects a benign preview-playback mechanism.

**Reusable pattern identified and escalated to a formal knowledge candidate:** "score-then-discard" is now a 3-times-observed anti-pattern across this codebase (rotation-state, topic-bank, hook_score), not a one-off.

## 3. Codex review history — all 5 rounds

| Round | Verdict | What Codex caught |
|---|---|---|
| 1 | NEEDS_REVISION (10 issues: 3 High, 5 Medium, 2 Low) | Escalated a data-integrity anomaly I had dismissed as low-sample noise; caught the AVD/views arithmetic mismatch; caught an overstated causal claim about duration; caught vague/unmeasurable experiment cards; caught false precision in the prioritization table |
| 2 | NEEDS_REVISION (4 carryforward partial + 3 new) | Caught that my anomaly investigation still overclaimed ("not a script artifact," "ruled out") beyond what isolated queries actually proved; caught that quarantining anomalous rows implied corruption when they might be genuine (just inapplicable) data; caught a round-1 bookkeeping error (9 vs. actual 10 issues) |
| 3 | NEEDS_REVISION (2 remaining Medium) | Caught that my "hook_score sidecar" collision-handling description assumed uniform behavior across generators that don't actually behave uniformly; caught that my "locked" audit date range wasn't actually a locked date range |
| 4 | NEEDS_REVISION (1 remaining Medium) | Caught that my corrected date range, when actually queried against the real registry, returned 12 videos, not the 8 I claimed |
| 5 | **APPROVED** | Confirmed the population/generator/date-range correction against the real registry and Cursor's report |

**26 total findings across 5 rounds, 26 accepted, 0 rejected.** Several of these were things I would not have caught on my own — Codex functioned as a genuine adversarial check, not a rubber stamp, and every one of its load-bearing claims was independently reverified by me against real code/data before being accepted (never taken purely on Codex's word).

## 4. Accepted vs. rejected Codex comments

**All 26 comments across 5 rounds: ACCEPTED. Zero rejected. Zero left as NEED_MORE_EVIDENCE** at the close of the loop (a few items were briefly marked as needing more investigation mid-loop — e.g. the pre-publish-view anomaly — but were investigated to a defensible resting point, not left open). Full per-comment reasoning, including the specific evidence I checked before accepting each one, is in `03a`, `03b`, `03e`, `03g` (accept/reject logs for rounds 1-4; round 5 had no new comments to classify).

This is a genuinely high accept rate, and it's earned rather than automatic: every comment was checked against real code, the real registry, or recomputed arithmetic before being accepted — not accepted merely because Codex asserted it. Two examples of this in practice: I independently recomputed the AVD/views arithmetic myself before agreeing it was a real problem, and I ran the actual registry query myself before agreeing the "8 videos" population claim was wrong (confirming it was actually 12).

## 5. Final approved improvement plan (`04_claude_diagnosis_v4.md` §3 — none of this is applied yet)

**Top priority — Experiment E (new this cycle):** add an automated invariant to review tooling that quarantines (not discards) any Analytics row dated before a video's real public-publish day, closing the exact gap that caused this cycle's most serious back-and-forth with Codex.

**Also approved:**
- **Experiment A:** rolling-window, per-video day-dimension Analytics pull with explicit quota/pagination/partial-response handling — replaces the fixed-window UTC query that silently missed real data in cycle 1.
- **Experiment D (carried from cycle 1, still unshipped):** the `hook_score` persistence contract — generator → sidecar → runner → registry — now fully specified (schema/version, 1:1 naming derived from each generator's actual resolved output path, missing/corrupt/stale handling, resume behavior, and a 3-layer rollback plan).
- **Experiment C (carried from cycle 1, still unshipped):** accuracy/tone audit — now locked to a real, reproducible population (12 Phong Thủy scripts, `publish_at` 2026-07-18 to 2026-07-27, 8 generators), a concrete checklist, two-pass adjudication, and pre-set decision thresholds.
- **Reporting control B:** every future report citing `averageViewPercentage` must also show `averageViewDuration` and a reconciliation check against `estimatedMinutesWatched`/`views`, with a defined ±20% tolerance, flagging (not interpreting) anything outside it.

**Deferred, explicitly not recommended this cycle:** duration-shortening content experiments (n=1 per channel, nowhere near enough data); the Western Zodiac comment-CTA test (KPI-priority question from cycle 1 still unresolved, no new evidence this cycle); any category-level cuts or emphasis shifts (sample size unchanged).

## 6. Candidate knowledge extracted (full detail in `05_candidate_knowledge_package.md` — not applied anywhere)

Seven candidate learnings proposed for your manual approval: (1) the PT/UTC day-bucketing mechanism, (2) the unresolved AVD/views reconciliation gotcha, (3) "score-then-discard" as a named, 3-times-observed anti-pattern, (4) inconsistent file-collision handling across generators, (5) silent (not loud) failure on cross-channel credential/video-ID mismatches, (6) the judge panel's fact-check rigor not implying tone/certainty rigor, (7) a review-methodology lesson about verifying query results rather than stating them from memory. Content-performance hypotheses were deliberately excluded — still too low-confidence/low-sample to promote to reusable knowledge.

## 7. Open risks and unknowns

- **The pre-publish-view anomaly's root cause is unconfirmed** and, per the YouTube Data/Analytics APIs' own limitations, may be unconfirmable with the tools available (no historical scheduling/preview audit trail is exposed for a video once it's public). Mitigated, not resolved, by the quarantine invariant (Experiment E).
- **The AVD/views/AVP reconciliation gap's cause is unconfirmed** — could be a genuine denominator difference in the API's own Shorts-specific semantics, or something else. Reporting control B flags future instances; doesn't explain this one.
- **All content-performance conclusions remain low-confidence** — this cycle's real contribution is 2 usable data points, not a statistically meaningful sample. Experiment A is designed to accumulate more over future cycles, but that takes real time (each cycle can only observe what's actually happened).
- **Experiment C (the accuracy/tone audit) has not been run yet** — its population/method are now locked and approved, but whether the two known instances are isolated or systemic is still an open question pending actual execution.
- **`hook_score` persistence (Experiment D) has been approved across two full cycles now (cycle 1 and cycle 2) without shipping** — this is the single most consequential unshipped item, since it's the only path to ever correlating the judge panel's own quality signal with real outcomes.

---

## Facts vs. Hypotheses vs. Recommendations — summary

**Facts (verified, not claims):** PT/UTC day-bucketing (directly tested); `hook_score` discarded in code (read directly); AVD/views arithmetic mismatch (recomputed); pre-publish-view anomaly reproduces on isolated queries (re-run and verified); absolute-language phrasing exists in 2 live scripts (re-grepped from the real registry); Experiment C's corrected population is 12, not 8 (re-queried from the real registry).

**Hypotheses (explicitly unconfirmed, confidence stated):** the pre-publish-view anomaly's mechanism (LOW, Studio-preview theory); duration as a retention confound (LOW, n=1 per channel); whether the two large-sample videos' engagement difference is statistically meaningful (LOW, pending denominator verification); whether the accuracy/tone gap is isolated or systemic (pending Experiment C's actual execution).

**Recommendations (proposed, none applied):** Experiments E, A, D, C, and reporting control B, all detailed above with objective/metric/success-criteria/rollback per item, per your workflow's requirement. Nothing here has touched a production prompt, generator, or workflow file — every item awaits your explicit approval before implementation.
