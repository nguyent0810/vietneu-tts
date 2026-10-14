# Candidate Knowledge Package — Cycle 2 — For Manual Approval Only

**This package has NOT been applied anywhere.** No `CLAUDE.md`, domain guide, brand manifesto, or code comment has been modified. Everything below is a proposal for you to accept, reject, or edit — nothing here is production knowledge until you say so.

Selection criterion: only items with direct, verifiable evidence from this cycle (not speculation) and clear applicability to future work made the cut. Each entry states the learning, its evidence, and where it would plausibly live if approved.

---

## 1. YouTube Analytics `day` dimension is bucketed in Pacific Time, not UTC

**Learning:** any `youtube_analytics.py` query using `dimensions=day` (or a video-filtered date-range query) interprets `startDate`/`endDate` as Pacific Time calendar days, not UTC. A video published at `2026-07-25T05:00:31Z` (UTC) has its activity bucketed under Analytics date `2026-07-24`.

**Evidence:** direct A/B API test — querying `uHwa6nFBtkc`'s date-range `2026-07-23`–`2026-07-24` (PT) returned 853 real views/retention data; the UTC-labeled `2026-07-25`–`2026-07-26` window (the video's actual UTC publish dates) returned zero, even though the video was already live and accumulating views.

**Suggested location:** a code comment in `youtube_analytics.py` near `get_channel_analytics`/`get_video_analytics`, and/or a note in whatever runbook governs future analytics-review cycles.

**Confidence: HIGH** (directly, repeatably tested).

---

## 2. `averageViewDuration`/`averageViewPercentage` may not reconcile with `views`/`estimatedMinutesWatched` for Shorts — verify before trusting

**Learning:** for two real videos this cycle, `estimatedMinutesWatched × 60 / views` did not match the reported `averageViewDuration` (10.62s implied vs. 24s reported; 9.42s implied vs. 14s reported) — a gap far beyond rounding error. The cause is unconfirmed (different denominators? Shorts-specific counting semantics?). Any future analysis using these fields should run this reconciliation check first and flag/investigate before treating the numbers as consistent.

**Evidence:** `analytics_reviews/cycle2_2026-07-27/04_claude_diagnosis_v4.md` §1.1, independently recomputed, not just Codex's claim.

**Suggested location:** a validation helper in the review-pull tooling (Experiment E/B in the approved plan already cover this operationally); worth a standing note wherever Analytics field semantics are documented.

**Confidence: HIGH that the discrepancy is real; LOW on its cause** — flag this distinction if adopted, don't overstate it as "solved."

---

## 3. "Score-then-discard" is a recurring pipeline anti-pattern in this codebase

**Learning:** this is the third time this session a valuable computed signal has been produced and then not carried forward: rotation-state committing before success, topic-bank resets, and now `generation_hook_score` being computed by the judge panel but discarded before reaching the registry (`short_batch_runner.py:276`, unfixed since cycle 1). When adding a new computed signal to any generator/pipeline stage, explicitly ask "does this reach persistent storage, or does it die at the end of the function that computed it?"

**Evidence:** three concrete instances across this session (two fixed earlier, `hook_score` still open, approved-but-unshipped fix exists in `04_claude_diagnosis_v4.md` Experiment D).

**Suggested location:** a design-checklist note for anyone adding new generator features.

**Confidence: HIGH** (pattern-matched across 3 real, separately-discovered instances, not a one-off).

---

## 4. Generator `.txt` output-collision handling is inconsistent across the codebase

**Learning:** `element_luck_short_generator.py`'s `write_short_bundle_file()` unconditionally overwrites its output at a fixed path; `western_zodiac_short_generator.py`'s version instead loops to find a free numbered-suffix path and never overwrites. Any future tooling that touches generator output files (like the hook_score sidecar in Experiment D) must handle both behaviors explicitly, not assume one.

**Evidence:** direct code read, both generators, confirmed during this cycle's Experiment D revision.

**Suggested location:** a code comment at the top of `short_judge_panel_engine.py` or wherever generators are documented as a family, flagging this as a known inconsistency (not necessarily a bug to fix — may be intentional per-generator, but should be known).

**Confidence: HIGH** (read directly, not inferred).

---

## 5. Cross-channel credential/video-ID mismatches fail silently, not loudly

**Learning:** querying `youtube_analytics.py`/`youtube_catalog.py` with one channel's credentials but a different channel's video ID does not raise an authorization error — it silently returns an empty result, as if the video simply had no data. This can mask real bugs (as it did in this cycle's own investigation, where using the wrong credentials for `B_i31QRy670` looked identical to "the anomaly disappeared" rather than "wrong credentials").

**Evidence:** directly observed this cycle — `B_i31QRy670` queried under Phong Thủy credentials returned a clean empty-rows result, not an error, even though the video doesn't belong to that channel.

**Suggested location:** a note in `youtube_analytics.py`/`youtube_catalog.py` docstrings, and a standing reminder for any future multi-channel debugging: always independently verify channel/credential match via `channels.list?mine=true` before trusting an empty result as meaningful.

**Confidence: HIGH** (directly observed and reproduced).

---

## 6. The judge-panel rubric's fact-check rigor does not guarantee tone/certainty rigor

**Learning:** cycle 1 found, and this cycle's audit spec (Experiment C) is designed to further test, that already-published Phong Thủy content contains unhedged absolute/anxiety-adjacent phrasing (e.g. "vận khí đại cát," "gây khắc chế và làm năng lượng của bạn mất cân bằng") despite passing the current judge panel's fact-check step. The rubric evidently checks factual/doctrinal accuracy well but doesn't have an explicit uncertainty-hedging check. These are two different kinds of rigor and a rubric needs to check both explicitly, not assume one implies the other.

**Evidence:** two confirmed, verified-in-the-real-registry instances (cycle 1), re-affirmed this cycle, with a proper audit (Experiment C, now population=12, approved) queued to determine if this is isolated or systemic.

**Suggested location:** `content_categories.py`'s rubric documentation, or wherever `category_rubric_block()` is defined — as a candidate rubric-strengthening item, contingent on Experiment C's actual results (not yet run).

**Confidence: MEDIUM** — the two instances are verified facts, but whether this is isolated or systemic is exactly what Experiment C (approved, not yet executed) is designed to determine. This entry itself should be revisited after that audit runs.

---

## 7. Review-methodology lesson: verify what a filter/query actually returns — don't state it from memory or intent

**Learning:** across this cycle's own review process, two separate claims about "what a data filter returns" turned out to be wrong when actually checked: an AVP-duration relationship assumed without recomputing it, and an audit population claimed to be "8 videos" that, when the stated date range was actually queried against the real registry, returned 12. Both were caught by Codex's insistence on evidence, and both were fixed only after I ran the real query myself rather than trusting the stated intent.

**Evidence:** `03_codex_critique_round1.md` (AVD/views mismatch), `03d_codex_critique_round3.md`/round 4 (population count), both independently reverified by me before accepting.

**Suggested location:** this is a process lesson for how I (Claude) should conduct any future structured review — worth keeping in mind for the next analytics cycle or any adversarial-review workflow, not a codebase artifact.

**Confidence: HIGH** (two concrete, independently-verified instances within a single cycle).

---

## What was deliberately excluded from this package

- Content-performance hypotheses (e.g. "grounded-data content outperforms evergreen," "duration affects retention") — all remain LOW confidence, n=1-2 per comparison, explicitly not proposed as reusable knowledge yet. Revisit after Experiment A/E accumulate more real, non-quarantined data across multiple cycles.
- The unconfirmed "Studio preview view" explanation for the §0 anomaly — stated as a hypothesis throughout the diagnosis, not elevated to a "learning" here since it remains unproven.

---

*This package is a proposal only. Nothing in it has been written to any production file, prompt, rubric, or documentation.*
