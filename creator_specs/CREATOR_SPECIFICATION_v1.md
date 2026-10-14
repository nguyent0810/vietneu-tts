# Creator Specification — v1

**Status: DRAFT — awaiting your approval. Nothing in this document has been applied to any production prompt, generator, rubric, or workflow file.** Per your instruction, no content generation or production-prompt update happens until you approve this spec.

**Source:** built exclusively from the two *approved* improvement plans — `analytics_reviews/2026-07-25_to_2026-07-26/06_claude_diagnosis_v3.md` (cycle 1, Codex-approved) and `analytics_reviews/cycle2_2026-07-27/04_claude_diagnosis_v4.md` (cycle 2, Codex-approved). Deferred items (duration-shortening test, Western Zodiac comment-CTA) and retracted hypotheses (v1-stage claims later corrected across the Codex review loops) are explicitly excluded — see §4 and the Changelog for what was left out and why.

**Discipline applied while writing this:** every rule below cites the specific approved finding and evidence behind it. Where a requested category (Hook, Story structure, Pacing, Typography, CTA) has no approved finding from either review cycle, that is stated explicitly as "no rule this version" rather than filled with an invented rule — per your instruction not to introduce speculative optimizations.

---

## 1. Universal Creator Rules (apply to every channel)

### 1.1 Hook
**No rule this version.** Neither review cycle produced an approved finding about hook construction. (Note for context, not part of this spec: `short_judge_panel_engine.py` already has a retention rubric and a hook-word-count cap, but those predate both review cycles and were not produced or modified by this workflow — nothing to add or change here.)

### 1.2 Story structure
**No rule this version.** No approved finding from either cycle addressed story structure.

### 1.3 Pacing
**No rule this version.** The one pacing-adjacent idea surfaced this cycle — shortening video duration based on the retention gap between `uHwa6nFBtkc` (27s) and `YStIdWWuXcU` (41s) — was explicitly **not approved**: cycle 2's diagnosis retracted the causal "duration is a confound" framing after Codex review (n=1 video per channel, AVP is duration-normalized by definition, cannot separate duration from hook/content/audience effects) and the duration-shortening experiment itself is listed as **Deferred** in the approved plan's prioritization table. Per your instruction to ignore unapproved suggestions, no pacing rule is introduced.

### 1.4 Typography
**No rule this version.** Not in scope of either review cycle.

### 1.5 CTA
**No rule this version.** The one CTA idea from this review process — an identity-based comment-inviting close ("which one sounds like you") for Western Zodiac content — is explicitly listed as **Deferred** in cycle 2's approved plan, gated on two unresolved conditions: (a) confirming comments are even the right KPI to optimize for this channel's tone, and (b) a brand-tone review of the specific wording before any test. Neither condition has been met. Per your instruction, this is not converted into a rule. (If you want this unblocked, see §3 Experiment Package for what would need to happen first — presented there as a candidate, not an active rule.)

### 1.6 Publishing

**Rule U-1 — Persist the generation-time quality score for every published Short, across every pipeline.**
> Every Short's generator/judge-panel pipeline must write its computed quality score (currently called `hook_score` in the Phật giáo pipeline, to be renamed `generation_hook_score` where newly implemented) to the registry entry for that video, before or at the point of publishing. A score computed and then discarded is not compliant.

- **Evidence:** verified as a code fact across both cycles — `short_batch_runner.py:276` explicitly sets `hook_score=None` for every topic other than the Phật giáo default; every Phong Thủy generator computes a real score via `short_judge_panel_engine.py` and then discards it (only the winning script text reaches the `.txt` output). Approved fix: cycle 1 §3 P0-1, carried and fully specified in cycle 2 as **Experiment D** (see §3).
- **Scope note:** this rule is universal in principle — it should hold for any current or future channel's pipeline. The Phật giáo pipeline already satisfies it today (`review_and_optimize_short()`'s score is correctly persisted). The currently-open implementation gap is scoped to the generator-based pipelines (currently Phong Thủy only); see Experiment D for the concrete fix.
- **Status:** approved, not yet implemented. Do not treat this rule as already in effect until Experiment D ships.

**Rule U-2 — Uncertainty-hedging is mandatory for future-outcome and belief-based claims.**
> Any script sentence that (a) states a future outcome as certain, or (b) presents a belief/tradition-based claim as flat fact, must use hedge language appropriate to the domain (e.g. "có thể," "thường," "theo quan niệm," "theo truyền thống") rather than unqualified certainty.

- **Evidence:** this is not a new principle — it is the existing Core Brand Bible rule, quoted verbatim and unchanged: *"Core brand rules: be accurate, humane, evidence-aware, non-manipulative, and clear about uncertainty."* (`content_repo_clone/CORE_OS/BRAND_BIBLE.md`) What's new is the confirmed evidence that the current judge-panel rubric doesn't yet operationalize this into an explicit fact-check step: two live, uploaded Phong Thủy scripts were independently re-verified (grepped directly from the real registry, not taken on report) to contain unhedged absolute/anxiety-adjacent language — *"Mọi việc ... hứa hẹn diễn ra vô cùng thuận lợi," "vận khí đại cát"* (`CONGIAP20260726_ConGiap_01`), and *"gây khắc chế và làm năng lượng của bạn mất cân bằng"* stated as flat causal fact, with a caution-framed title (`MENH_Kim_MauSacHopMenh_01`).
- **This document does not change the Brand Manifesto** — it operationalizes an existing Manifesto line into an explicit, checkable rubric requirement, per your instruction that new rules must reference approved findings, not alter the Manifesto itself.
- **Status:** the underlying violation is a confirmed fact (approved basis for this rule). Whether it is isolated or systemic across the wider content set is what the approved-but-not-yet-executed **Experiment C** (accuracy/tone audit, §3) will determine. This rule stands regardless of that audit's outcome, since it addresses confirmed violations already found — the audit determines *scope of remediation*, not whether the rule is warranted.

**Rule U-3 — Analytics reports must reconcile derived metrics before citing them.**
> Any future report citing `averageViewPercentage` must also cite `averageViewDuration`, the video's own duration, and a reconciliation check (`estimatedMinutesWatched × 60 / views` compared against reported `averageViewDuration`, ±20% tolerance). Outside tolerance, the report carries an explicit warning instead of an interpretation.

- **Evidence:** cycle 2 §1.1 — independently recomputed, not just Codex's claim: two real videos' `estimatedMinutesWatched`/`views` fields implied 10.62s and 9.42s per view respectively, but the reported `averageViewDuration` was 24s and 14s — a gap far exceeding rounding error, cause unconfirmed. Approved as **Reporting Control B** in cycle 2's plan.
- **Note:** this is a data-reporting rule, not a creative-content rule, but it governs what "Publishing" analytics/performance claims are allowed to say — included here for completeness per your requested category structure.

**Rule U-4 — Analytics data used for any publishing/performance decision must pass the PT-day-vs-public-publish-day quarantine check.**
> Before any Analytics row is used to inform a publishing or content decision, it must be checked against the video's own public-publish PT day. Rows dated earlier are preserved (not discarded) but excluded from public-performance interpretation, tagged with a `quarantine_reason`.

- **Evidence:** cycle 2 §0 — 3 videos showed real Analytics rows dated before their own public `publishedAt`, reproduced on isolated, credential-verified queries (root cause unconfirmed; most plausible unproven explanation is pre-public Studio preview views). Approved as **Experiment E** in cycle 2's plan, ranked as that cycle's top-priority item.
- **Related:** Analytics pulls should also use the PT-aware rolling-window methodology (**Experiment A**) rather than a fixed UTC-labeled 1-2 day window, which was shown in both cycles to silently miss real, already-processed data.

---

## 2. Brand-specific Rules

### 2.1 Buddhist (Phật giáo)
**No new rule this version.** Both review cycles explicitly treated Phật giáo as cross-channel context only — "I do not have pipeline-internal visibility into how its videos were produced, so I make no prompt/workflow recommendations for it" (cycle 1 diagnosis scope statement, unchanged in cycle 2). No approved finding is Buddhist-specific. Existing Buddhist domain guardrails (`content_repo_clone/DOMAINS/BUDDHISM/DOMAIN_MANIFEST.md`, risk_level=high) are untouched by this spec.

### 2.2 Feng Shui / Tử Vi (Phong Thủy)
**No new distinct rule beyond Universal Rule U-2.** The confirmed unhedged-language violations (§1.6, Rule U-2) were both found in Phong Thủy content specifically — this is noted here as a priority flag, not a separate rule, to avoid duplicating U-2 under a different name: **Experiment C's audit (§3) should run against the Phong Shui/Phong Thủy content population first**, since that's where the only confirmed evidence currently exists. This does not change or override any existing Feng Shui Domain Guide content (`content_repo_clone/DOMAINS/FENG_SHUI/DOMAIN_GUIDE.md` §9's Anti-Fear-Sales Standard, §14's "Transform first, refuse only when transformation is impossible" principle) — those stay exactly as written; U-2 is downstream of and consistent with them, not a replacement.

### 2.3 Crime (Hình Sự)
**No rule proposed — no data.** No evidence of an active, content-producing Crime/Hình Sự channel was found in either review cycle's data pull (the string "Hình Sự" appears only as an example value in `short_batch_runner.py`'s `--topic` CLI help text, not as a channel with real registry entries or Analytics data). Per your instruction against speculative optimizations, this section is intentionally left empty rather than populated with invented rules.

### 2.4 Other channels
None identified with approved findings from either cycle.

---

## 3. Experiment Package

**Honest framing:** none of the items below are hypothesis-driven A/B content experiments in the classic sense (testing one creative variant against another) — every approved item from both cycles is a deterministic engineering, instrumentation, or audit fix with a defined correct outcome, not an uncertain creative bet. They are presented in the requested hypothesis/implementation/success-metric/rollback format for consistency with your requested structure, adapted where "hypothesis" more accurately means "the specific gap this fix addresses."

### Experiment E — Automated public-day quarantine invariant
- **Hypothesis (in the adapted sense — the gap this closes):** Analytics rows dated before a video's public-publish PT day are currently trusted as ordinary data without a systematic check, risking silent misinterpretation in future reviews.
- **Implementation:** validation step in review-pull tooling computes each video's public-publish PT day and flags/quarantines any earlier-dated row with a `quarantine_reason`, preserving the row rather than discarding it.
- **Success metric:** on cycle 2's known dataset, the check flags exactly the 3 identified anomalous rows and does not flag the 2 known-good large-sample videos.
- **Rollback condition:** none needed — read-only validation logic in review tooling, no production pipeline impact.

### Experiment A — Rolling-window Analytics pull
- **Hypothesis:** a fixed UTC-labeled 1-2 day query window silently misses real, already-processed Analytics data due to the PT/UTC day-boundary mismatch (verified fact, cycle 2 §0a-equivalent finding).
- **Implementation:** rolling ~10-day window, `dimensions=day` per video, with quota/pagination/duplicate-row/partial-response handling.
- **Success metric:** retrieval correctness (100% row match against a known-good single-day control query) and analytical usability (count of videos per cycle with `views ≥ 500` in non-quarantined rows).
- **Rollback condition:** revert to fixed-window query if quota/pagination handling introduces failures; read-only, no production impact either way.

### Experiment D — hook_score persistence contract
- **Hypothesis:** see Rule U-1 above — this experiment *is* the implementation of that rule.
- **Implementation:** fully specified sidecar contract (schema/version, 1:1 naming derived from each generator's actual resolved output path — verified to differ across generators — missing/corrupt/stale handling, resume behavior, 3-layer rollback). Full detail in `04_claude_diagnosis_v4.md` §3.
- **Success metric:** non-null `generation_hook_score` in the registry for every video generated after this ships.
- **Rollback condition:** 3 independent layers — generators stop writing sidecars, runner stops ingesting them (reverts to current `null` behavior), any already-migrated registry data is left as-is (additive, non-gating).

### Experiment C — Accuracy/tone audit
- **Hypothesis:** the two confirmed unhedged-language instances (basis for Rule U-2) may be isolated or may indicate a systemic rubric gap — not yet known.
- **Implementation:** locked population (12 Phong Thủy scripts, `publish_at` 2026-07-18 to 2026-07-27, 8 generators — corrected during Codex review from an initially-miscounted population of 8), defined checklist, two-pass adjudication, pre-set zero-tolerance/threshold decision rules. Full detail in `04_claude_diagnosis_v4.md` §3.
- **Success metric:** numerator/denominator per checklist category, reported against the full locked population, with the decision threshold explicitly applied (triggered or not).
- **Rollback condition:** N/A — read-only audit, produces a follow-up recommendation only if triggered.

### Reporting Control B — AVD/AVP reconciliation
- **Hypothesis:** see Rule U-3 above — this control *is* the implementation of that rule.
- **Implementation / success metric / rollback:** as stated in Rule U-3.

### Not included — Western Zodiac comment-CTA (deferred, not approved)
Listed here only for transparency, not as an active experiment: cycle 2's plan explicitly holds this pending (a) KPI-priority confirmation (are comments even the right signal to optimize for this channel's tone) and (b) a brand-tone review of the specific wording. If you want to unblock this, it would need to return through the review process as a newly-approved item before it belongs in this package — it is not included as approved here.

---

## 4. Rules to Remove

**None identified.** Neither review cycle's approved findings propose removing, contradicting, or obsoleting any existing creator rule, rubric, or Domain Guide provision. Both cycles' approved plans are purely additive (new persistence contract, new audit, new reporting/data-quality checks) or reinforcing (Rule U-2 operationalizes an existing Brand Bible line; it does not replace anything). Per your instruction not to speculate, this section is left empty rather than populated with a plausible-sounding but unevidenced removal.

---

## 5. Changelog

**This is v1 — there is no prior Creator Specification document** (confirmed by search; no file matching this description exists anywhere in the repository before this one). The "changes" below are therefore against the *implicit* prior state — whatever rules existed only informally in code (`short_judge_panel_engine.py`, `content_categories.py`, generator prompts) and in the Brand Manifesto/Domain Guides — not against a previous version of this document.

| Change | Source | Type |
|---|---|---|
| Added Rule U-1 (persist generation-time quality score) | Cycle 1 §3 P0-1 → Cycle 2 Experiment D (fully specified) | New universal rule, not yet implemented |
| Added Rule U-2 (uncertainty-hedging mandatory) | Cycle 1 §1.6 finding + Cycle 2 re-verification → Experiment C (audit pending) | New universal rule, operationalizing existing Brand Bible language — Manifesto itself unchanged |
| Added Rule U-3 (AVD/AVP reconciliation before citing) | Cycle 2 §1.1 finding → Reporting Control B | New universal reporting rule |
| Added Rule U-4 (PT-day quarantine before using Analytics for decisions) | Cycle 2 §0 finding → Experiment E + Experiment A | New universal data-hygiene rule |
| Hook / Story structure / Pacing / Typography / CTA | — | **Explicitly not modified** — no approved finding in either cycle touched these categories; sections left empty rather than filled speculatively |
| Western Zodiac comment-CTA | Cycle 1/2, both times listed as Deferred | **Explicitly excluded** — not approved, not converted to a rule or active experiment |
| Duration-shortening | Cycle 2, listed as Deferred, causal framing retracted during Codex review | **Explicitly excluded** |
| Category-level cuts/emphasis shifts | Cycle 1/2, both times listed as Deferred (sample size) | **Explicitly excluded** |
| "Rubric and Manifesto are aligned by construction" | Cycle 1 v1 draft claim | **Retracted during Codex review, never reached any production artifact** — not part of this spec in any form |

---

**Awaiting your approval.** Nothing above has been written to `short_judge_panel_engine.py`, `content_categories.py`, any generator, any Domain Guide, or the Brand Manifesto. Tell me which rules/experiments to proceed with (all, some, or none) and I will implement only what you approve.
