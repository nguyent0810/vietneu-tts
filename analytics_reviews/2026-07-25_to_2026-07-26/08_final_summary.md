# Review & Analytics Workflow — Final Summary — 2026-07-25 to 2026-07-26

**Status: COMPLETE.** Codex CLI approved the final plan (`06_claude_diagnosis_v3.md`) after 3 critique rounds. **No production prompt, generator, or workflow file has been modified** — everything below is a reviewed proposal awaiting your explicit go-ahead.

**Full artifact trail** (all in `analytics_reviews/2026-07-25_to_2026-07-26/`):
`00_raw_data_bundle.json` → `01_cursor_analytics_report.md` → `02_claude_diagnosis.md` (v1) → `03_codex_critique_round1.md` (CẦN SỬA) → `04_claude_diagnosis_v2.md` → `05_codex_critique_round2.md` (CẦN SỬA) → `06_claude_diagnosis_v3.md` (**final plan**) → `07_codex_critique_round3.md` (APPROVED) → this file.

---

## 1. Cursor findings (real data, `01_cursor_analytics_report.md`)

**Coverage caveat, stated up front:** YouTube Analytics API has a real ~3-day processing lag, confirmed by direct testing. Retention, `averageViewPercentage`, traffic source, and subscriber deltas are **not available** for the 07-25/07-26 window as of this report. Everything below uses `lifetime_statistics` (Data API, cumulative-to-date) as an explicitly labeled proxy — not day-split growth.

**Facts:**
- Phong Thủy: 8 videos, 5168 lifetime views, 47 likes, 1 comment. Range: 8 (Song Tử, Western Zodiac) to 1120 (Storytelling) views.
- Phật giáo (context only): 9 videos, 5561 lifetime views, 108 likes, 1 comment.
- `hook_score` is `null` for all 8 Phong Thủy registry entries (verified against real code and registry, not assumed).
- Growth-by-day, retention, traffic source, viewed-vs-swiped-away: no data this window (API lag).

**Hypotheses (all tagged low confidence given n=8/2 days):** Storytelling/daily-grounded content may outperform other formats; within-category variance may reflect execution rather than category choice; evergreen (no date anchor) content may underperform; comment near-zero may reflect a structural gap or just be noise at this sample size.

## 2. Claude diagnosis (evolved across 3 revisions — final version summarized here; full reasoning in `06_claude_diagnosis_v3.md`)

**Confirmed facts:**
- `hook_score` is computed by every generator's judge panel but never reaches the registry — the data is discarded after generation, not just unlogged (verified against `short_batch_runner.py:276` and the real registry).
- Absolute/anxiety-adjacent phrasing already exists in **published** content — e.g. *"vận khí đại cát"* ("extremely auspicious energy"), *"gây khắc chế và làm năng lượng của bạn mất cân bằng"* ("causes conflict and unbalances your energy," stated as flat fact) — verified by me directly against the real registry, independent of Codex's claim.

**Root-cause hypotheses, all explicitly LOW confidence given sample size:** within-category variance may reflect execution rather than category (untested); low view counts may reflect a discovery problem (not yet shown to enough people) as easily as a retention problem — the two are indistinguishable without combined reach+retention+traffic-source data; evergreen underperformance is unconfirmed; comment scarcity may or may not indicate a structural gap, and comments may not even be the right KPI to chase for this channel's tone.

**Reusable pattern identified:** "score-then-discard" — a computed quality signal (hook_score) is produced and then not carried forward — is a repeat of a bug class already fixed elsewhere this session (rotation-state, topic-bank). Worth fixing once at the contract level, not per-symptom.

## 3. Codex feedback (3 rounds — full detail in `03_`, `05_`, `07_codex_critique_round*.md`)

Codex read the actual code and registry each round rather than taking claims at face value, and caught real issues in both rounds 1 and 2:

- **Round 1 (CẦN SỬA, 9 issues):** caught that v1 called the `hook_score` fix "one file, additive, zero risk" when it actually requires a new cross-file data contract; caught that a proposed Kinh Dịch comment-CTA risked violating that generator's own "not a personal reading" rule; caught that v1 claimed the rubric and Brand Manifesto were "aligned by construction" while real published content contained unhedged absolute claims; caught a retention-measurement error (retention alone doesn't distinguish discovery from CTR problems); caught an evergreen-anchoring loophole (a real event used only for false urgency is still manufactured relevance); flagged several confidence/causal-language overstatements.
- **Round 2 (CẦN SỬA, 1 issue):** confirmed 8/9 round-1 fixes were correctly resolved, and directly verified in the real filesystem that no recoverable `hook_score` artifact exists for any of the 8 videos (supporting the "cannot fix retroactively" claim). Caught one remaining overclaim: a promise to compare the current batch at exact T+24h/48h/72h snapshots the pipeline never actually captured.
- **Round 3 (APPROVED):** confirmed the final fix — the plan now correctly scopes hour-precision snapshots to future cohorts only, and uses a clearly-labeled daily approximation for the current batch.

**Process note (transparency):** the first round-1 attempt hung indefinitely — a nested-backgrounding mistake caused `codex exec` to wait on stdin it never received. Killed and re-run correctly with stdin closed; all 3 documented rounds are from correctly-completed runs.

## 4. Final approved improvement plan (`06_claude_diagnosis_v3.md` §3 — none of this is applied yet)

**P0 (do first):**
1. **Rebuild the hook_score pipeline contract** — generator writes a sidecar metadata file alongside each script → runner ingests it into the registry as `generation_hook_score` (kept separate from the Phật-giáo hook-review score) → include winning strategy + iteration count, not full raw judge history. Effort: medium. Risk: low-medium (schema/mapping/versioning, not zero). This cannot recover data for the 8 already-published videos — only future ones.
2. **Re-run this Analytics review in ~24-48h** (~2026-07-28) once the API backlog clears, verifying non-zero row coverage first; use per-day rows as a labeled approximation for this batch (true hour-precision snapshots require a not-yet-built scheduled-pull mechanism, out of scope for now).
3. **Audit already-published Phong Thủy scripts for absolute/anxiety-framed language** and assess whether the judge-panel rubric needs a stronger uncertainty-hedging check. Read-only audit, not a rewrite of live content.

**P1 (needs your brand review before any test, not "safe/low-risk"):**
4. A Western-Zodiac-only comment-inviting close (e.g. "which one sounds like you") — Kinh Dịch is explicitly excluded (risk of implying a personal reading, which that generator's own rules forbid). Gated on first confirming comments are actually the right KPI for this channel's tone.
5. Hold off on any category-level cuts/emphasis shifts until ~10-15 age-matched, same-prompt-version videos per category exist — this is a checkpoint, not a statistically sufficient threshold.

**P2 (do not start yet):**
6. Evergreen-content specificity investigation — only after real per-day/retention data exists; any event/season anchor must have organic, necessary content relevance, not just factual truth (a real-but-irrelevant date is still manufactured urgency).

**Explicit non-recommendations (unchanged through all 3 rounds):** no manufactured urgency/deadlines on evergreen content; no category cuts based on this week's numbers; no loosening of fact-check rigor or calm/reverent tone in pursuit of engagement.

## 5. Proposed experiments for the next iteration

1. **Ship P0-1 (score contract) before the next batch**, so the next review actually has `generation_hook_score` data to correlate against outcomes — this is the highest-leverage single change, since right now no batch, past or future, can answer "did the judge's own score predict anything?"
2. **Re-run this same review ~2026-07-28** and, this time, explicitly check whether the extra 24-48h of Analytics processing unlocks retention/traffic-source data — if it still doesn't, that itself is worth flagging as a bigger API-lag problem than currently assumed.
3. **Run the P0-3 rubric audit before the next generation batch**, not after — cheaper to catch an uncertainty-hedging gap in the rubric than to keep publishing content with the same pattern.
4. **If P1-1 (Western Zodiac CTA) is approved after brand review, run it as a small, clearly-versioned test batch** (not a blanket prompt change) so its effect can be isolated from the score-contract and rubric changes landing around the same time — otherwise three simultaneous changes will confound each other in the next review.

---

**What I'm confident about:** the `hook_score: null` gap is real and verified against code; the absolute-language content gap is real and verified against the actual registry; the ~3-day Analytics API lag is real and verified by direct A/B date-range testing. **What I'm not claiming:** that any of the performance hypotheses (category effects, evergreen underperformance, comment gap being content-driven) are confirmed — all remain low-confidence, n=8 hypotheses pending the 2026-07-28 re-run with real retention data.
