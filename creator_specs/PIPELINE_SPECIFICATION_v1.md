# Pipeline Specification — v1

**Status: Codex-APPROVED (2 rounds). Nothing in this document has been applied to any production code, registry schema, or workflow file — awaiting your explicit approval before implementation.**

**Scope of this document:** analytics collection/interpretation, data-integrity validation, registry/schema engineering contracts, reporting-format requirements, and audit/QA processes. This document contains no content-generation rules — those live in `CREATOR_SPECIFICATION_v2.md`.

**Rule status semantics (apply throughout this document):**
- **ACTIVE** — currently enforced in production code/process today.
- **EXPERIMENTAL** — proposed and evidence-backed, not yet implemented in production.
- **DEPRECATED** — formerly active, now retired (with the reason).

---

## 1. Data Collection & Analytics Rules

### PR-1 — Analytics data used for any decision must pass the public-publish-day quarantine check

> Before any Analytics row is used to inform a publishing or content decision, it must be checked against the video's own public-publish PT day. Rows dated earlier are preserved (not discarded) but excluded from public-performance interpretation, tagged with a `quarantine_reason`.

- **Version:** 1.0
- **Source:** Cycle 2 §0, Codex-approved as **Experiment E** (`analytics_reviews/cycle2_2026-07-27/04_claude_diagnosis_v4.md` §3).
- **Scope:** Universal — both channels' Analytics tooling.
- **Status:** EXPERIMENTAL — not yet implemented in the review-pull tooling.
- **Evidence:** 3 videos showed real Analytics rows dated before their own public `publishedAt`, reproduced on isolated, credential-verified queries (root cause unconfirmed — most plausible unproven explanation is pre-public Studio preview views; the YouTube Data/Analytics APIs do not expose a historical scheduling/preview audit trail to confirm this).
- **Implementation:** validation step computes each video's public-publish PT day (from `snippet.publishedAt`, converted to PT) and flags any earlier-dated Analytics row with `"quarantine_reason": "PT day precedes public publish PT day"`.
- **Success metric:** on Cycle 2's known dataset, the check flags exactly the 3 identified rows (`_m0aX_gJbaw`, `AuUpRQZOcwc`, `B_i31QRy670`) and does not flag the 2 known-good large-sample videos (`uHwa6nFBtkc`, `YStIdWWuXcU`).
- **Rollback:** none needed — read-only validation logic in review tooling only, no production pipeline impact.

### PR-2 — Analytics pulls must use PT-aware rolling-window queries, not fixed UTC-labeled windows

> Future Analytics pulls for review cycles must query a rolling window (e.g. ~10 days) with `dimensions=day` per video, and read off whichever days actually return non-zero rows — not assume a fixed lag offset from a UTC-labeled 1-2 day window.

- **Version:** 1.0
- **Source:** Cycle 2 finding — verified fact via direct A/B test that YouTube Analytics buckets `day` in Pacific Time, not UTC (`analytics_reviews/cycle2_2026-07-27/00a_pt_utc_finding.md`). Codex-approved as **Experiment A** (`04_claude_diagnosis_v4.md` §3).
- **Scope:** Universal — both channels' Analytics tooling.
- **Status:** EXPERIMENTAL — not yet implemented.
- **Evidence:** a video published `2026-07-25T05:00:31Z` UTC showed its full 853-view, 91.9%-AVP day entirely under Analytics date `2026-07-24` (PT); a UTC-labeled query for `2026-07-25`–`2026-07-26` (the video's own UTC publish dates) returned zero, despite the video already being live and accumulating views.
- **Implementation:** rolling ~10-day window, `dimensions=day` per video, with explicit quota, pagination, duplicate-row, and partial-response handling.
- **Success metric:** *Retrieval correctness* — on a known-good video/day set, returns 100% of the rows a single-day control query returns. *Analytical usability* — count of videos per cycle with `views ≥ 500` in non-quarantined rows (per PR-1).
- **Rollback:** revert to fixed-window query if quota/pagination handling introduces failures; read-only tooling, no production impact either way.
- **Depends on:** PR-1 (quarantine check) as a prerequisite for treating this rule's output as trustworthy for public-performance analysis.

### PR-3 — Analytics reports must reconcile derived metrics before citing them

> Any future report citing `averageViewPercentage` must also cite `averageViewDuration`, the video's own duration, and a reconciliation check (`estimatedMinutesWatched × 60 / views` compared against reported `averageViewDuration`, ±20% tolerance). Outside tolerance, the report carries an explicit warning instead of an interpretation.

- **Version:** 1.0
- **Source:** Cycle 2 §1.1, independently recomputed (not just Codex's claim). Codex-approved as **Reporting Control B** (`04_claude_diagnosis_v4.md` §3).
- **Scope:** Universal — any future analytics review report, either channel.
- **Status:** EXPERIMENTAL — not yet implemented.
- **Evidence:** two real videos' `estimatedMinutesWatched`/`views` fields implied 10.62s and 9.42s per view respectively, but reported `averageViewDuration` was 24s and 14s — a gap far exceeding rounding error, cause unconfirmed.
- **Success metric:** future reports include the reconciliation check with the stated ±20% tolerance; `04_claude_diagnosis_v4.md` §1.1 is the reference example of a flagged (not interpreted) case.
- **Rollback:** none — reporting format only, no production pipeline impact.

---

## 2. Registry / Schema Engineering Rules

### PR-4 — Persist the generation-time quality score for every published Short, across every pipeline

> Every Short's generator/judge-panel pipeline must write its computed quality score to the registry entry for that video, before or at the point of publishing, via a sidecar-metadata contract — not discard it after generation.

- **Version:** 1.0
- **Source:** Cycle 1 §3 P0-1 (`analytics_reviews/2026-07-25_to_2026-07-26/06_claude_diagnosis_v3.md`), fully specified in Cycle 2 as **Experiment D** (`04_claude_diagnosis_v4.md` §3, revised across 3 Codex rounds).
- **Scope:** Universal in principle. Current implementation gap is scoped to generator-based pipelines (currently Phong Thủy only) — the Phật giáo pipeline's `review_and_optimize_short()` already persists its score correctly today and needs no change.
- **Status:** EXPERIMENTAL — not yet implemented. **Do not treat this rule as in effect until shipped.**
- **Evidence:** verified as a code fact across both cycles — `short_batch_runner.py:278` (`entry["hook_score"] = None`, inside the `if topic != DEFAULT_TOPIC` branch) explicitly sets `hook_score=None` for every topic other than the Phật giáo default; every Phong Thủy generator computes a real score via `short_judge_panel_engine.py` and discards it (only the winning script text reaches the `.txt` output). (Line number corrected from `276` to `278` per Codex round-1 review — re-verified directly against the file, not just Codex's claim.)
- **Schema/version:** sidecar file `{key}.meta.v1.json` (version in filename and as top-level `schema_version: 1`), containing `{generation_hook_score, winning_strategy, iteration_count, category, generator_name, schema_version}`. Field named `generation_hook_score` — deliberately distinct from the Phật giáo pipeline's `hook_score` field, since they are two different measurements and must not be conflated in the registry schema.
- **Naming/mapping contract:** sidecar filename is derived from the generator's *actual resolved* `.txt` output path after that generator's own collision logic has run — verified that generators are NOT uniform here (`element_luck_short_generator.py` unconditionally overwrites at a fixed path; `western_zodiac_short_generator.py` loops to a numbered-suffix path and never overwrites). Both branches must be covered.
- **Missing/corrupt/stale sidecar behavior:** runner logs a warning and proceeds with `generation_hook_score: null` (fail-open on this field only — does not block TTS/render/upload, since this is observational metadata, not a content gate).
- **Backward compatibility:** registry entries created before this ships keep `hook_score: null` permanently — no migration attempted (established non-recoverable in Cycle 1).
- **Resume/idempotency:** if the batch runner is interrupted after the sidecar is written but before registry ingestion, re-running must re-read the sidecar — its existence, not registry state, is the source of truth.
- **Success metric:** non-null `generation_hook_score` in the registry for every video generated after this ships.
- **Rollback (3 independent layers):** (1) generators stop writing sidecars — reverts per-generator, does not affect `.txt` output or content; (2) runner stops ingesting sidecars — reverts to current always-`null` behavior; (3) any registry entries with a non-null score from a partial rollout are left as-is (additive, non-gating, doesn't alter pipeline behavior).

---

## 3. Validation / QA Process Rules

### PR-5 — Accuracy/tone audit process for judge-panel rubric coverage

> A fixed-list, stratified, two-pass-adjudicated audit of published scripts, checking two distinct things: compliance with Creator Rule `CR-1` (new, from this review process) and compliance with the pre-existing Feng Shui Domain Guide §9 Anti-Fear-Sales Standard (not new — already normative, unmodified).

- **Version:** 1.2 (executed — see notes below)
- **Source:** Cycle 1 §3 P0-3, fully specified in Cycle 2 as **Experiment C** (`04_claude_diagnosis_v4.md` §3, population corrected across Codex rounds 3-4 from an initially-miscounted 8 to the verified real 12).
- **Scope:** Phong Thủy content — a **fixed list of exactly 12 registry keys**, snapshotted from `output/shorts/Phong Thủy/registry.json` at the time this document was written, `publish_at` between `2026-07-18T00:00:00Z` and `2026-07-27T00:00:00Z`: `THAN20260724_12ViThan_01`, `CONGIAP20260724_ConGiap_01`, `MENH_Hoả_MauSacHopMenh_01`, `KIENTHUC_HnhnhndtrcquanvchukNgHnhTngKhc_01`, `MENHNGAY20260725_MenhTaiLoc_01`, `CUNGHD_SongT_01`, `KINHDICH_TnViPhong_01`, `CUNGHD_BchDng_01`, `KINHDICH_CnViThin_01`, `CHUYENKE_Chicgingkhinnginmlunbtan_01`, `CONGIAP20260726_ConGiap_01`, `MENH_Kim_MauSacHopMenh_01` (8 generators represented: `element_luck`, `western_zodiac`, `iching`, `storytelling`, `zodiac`, `element_color`, `twelve_gods`, `educational`). The population is this exact key list, not a re-evaluatable date-range query — re-running the audit later means re-auditing this same 12-key list.
- **Status:** EXECUTED — see `PR5_AUDIT_REPORT_v1.md` (v4.0, Codex-approved). Rate threshold **triggered** (31/12 = 2.58, well above 1.0); produced an evidence-backed follow-up proposal to widen `CR-1` enforcement, drafted and Codex-approved as `PROMPT_DELTA_v1.md` Deltas 7-9.
- **Checklist:**
  - **(a) states a future outcome as certain without a hedge word**, and **(d) omits a "theo quan niệm/truyền thống" framing for a belief-based claim presented as fact** — these two enforce **Creator Rule `CR-1`** (`CREATOR_SPECIFICATION_v2.md`), the new rule from this review process.
  - **(b) frames an anxiety/threat scenario**, and **(c) implies a deadline/urgency not organically present in the topic** — these two are **not new rules from this workflow**. They check compliance with the pre-existing, unmodified `content_repo_clone/DOMAINS/FENG_SHUI/DOMAIN_GUIDE.md` §9 Anti-Fear-Sales Standard. If this audit finds violations of (b)/(c), that is a Domain Guide compliance finding, not a new rule created by this document.
- **Counting-unit methodology (formalized here — resolves a category of disputed items found during execution, not an ad hoc per-case judgment call):** the checklist unit is an independent script sentence, evaluated on its own explicit content. Within that unit:
  - A **declarative clause** (a statement asserting a fact, relationship, mechanism, or outcome) is checked for hedging on its own terms, regardless of what an adjacent sentence says — no "already covered by a nearby sentence" exemption, no "it's just naming a classification" exemption. Any classification/relationship/status attribution stated as fact without a hedge word counts as `(d)`, whether or not it appears standalone or bundled inside a longer sentence.
  - An **imperative/directive clause** (an instruction — "hãy," "đừng," "nên") that carries **no embedded declarative clause** (no "để..."/"vì..." purpose or reason clause asserting a mechanism as fact) is not itself a claim and does not require its own hedge — CR-1 governs claims presented as fact, not instructions. If an imperative sentence *does* contain an embedded declarative clause (e.g. "Hãy ưu tiên màu X **để hỗ trợ năng lượng cá nhân**" — the "để..." clause asserts an efficacy mechanism), that embedded clause is evaluated as a declarative claim under the rule above, independent of the imperative wrapping it.
  - This single rule applies uniformly to every generator/category audited — no category-specific carve-outs.
- **Adjudication:** two independent passes; any sentence flagged by only one pass is marked "disputed" and reported separately, not silently dropped or included.
- **Decision threshold:** any instance of (b) or (c) is zero-tolerance and escalates immediately, per the existing Domain Guide standard they check. An overall rate of (a)/(d) instances above 1 per script on average triggers a rubric-strengthening follow-up proposal for `CR-1`'s enforcement scope (a separate item, not folded into this audit's own success criteria).
- **Success metric:** numerator/denominator per checklist category, reported against the full fixed-list population (12 scripts), decision threshold explicitly applied (triggered or not).
- **Rollback:** N/A — read-only audit; produces a follow-up recommendation only if triggered.

---

## 4. Rules to Remove

None identified. Neither review cycle's approved findings propose removing any existing pipeline behavior — both cycles are purely additive (new validation checks, new persistence contract, new reporting requirement).

---

## 5. Changelog

**This is v1 of the Pipeline Specification — split out of `CREATOR_SPECIFICATION_v1.md`, which previously mixed content and pipeline rules together.**

| Change | Reason |
|---|---|
| `PR-1` (public-publish-day quarantine) | Moved from v1's "Rule U-4" / Experiment E — data-validation rule, not content generation |
| `PR-2` (PT-aware rolling-window pulls) | Moved from v1's Experiment A reference under U-4 — analytics-tooling rule |
| `PR-3` (AVD/AVP reconciliation) | Moved from v1's "Rule U-3" / Reporting Control B — analytics-reporting rule |
| `PR-4` (hook_score persistence contract) | Moved from v1's "Rule U-1" / Experiment D — registry/schema engineering rule |
| `PR-5` (accuracy/tone audit process) | Moved from v1's Experiment C — validation/QA process rule, explicitly cross-referenced to Creator Rule `CR-1`, which it enforces |
| Added Version/Source/Scope/Status metadata to every rule | New requirement — none of these rules were previously tagged with structured metadata |
| Added explicit rollback notes to every rule, and dependency/cross-reference notes where applicable (`PR-2`→`PR-1`, `PR-5`→`CR-1`) | Carried forward from the underlying approved experiment cards; not every rule has a dependency (`PR-1`, `PR-3`, `PR-4` have none), corrected from an earlier overclaim that all rules had one |

**Round-1 Codex review fixes (this revision):**
- `PR-4`: corrected the `short_batch_runner.py` line citation from `276` to `278` (re-verified directly).
- `PR-5`: separated checklist items (a)/(d) — which enforce Creator Rule `CR-1` — from (b)/(c), which check the pre-existing Feng Shui Domain Guide §9 standard and are not new rules from this workflow. Locked the audit population to an exact 12-key list (snapshotted from the real registry) instead of a re-evaluatable date range, since the date range alone does not reproduce a fixed count over time.
