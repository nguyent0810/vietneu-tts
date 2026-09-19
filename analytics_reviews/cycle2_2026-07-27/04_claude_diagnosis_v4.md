# Claude Diagnosis & Prioritized Plan — Cycle 2 — v4

**Input:** `01_cursor_report.md` + `03_codex_critique_round1.md` (10 issues) + `03c_codex_critique_round2.md` (4 partial + 3 new) + `03d_codex_critique_round3.md` (2 remaining Medium points) + accept/reject logs `03a`/`03b`/`03e` (25/25 total ACCEPT across 3 rounds, 0 REJECT).
**Status:** DRAFT v4 (patched) — round 4 confirmed the collision-contract fix; round 4 also caught that the Experiment C date range didn't actually reproduce "8 videos" (real registry has 12 in that range) — corrected in place, population expanded to the real 12. Pending round-5 re-review. **No production prompt, generator, or workflow file has been modified.**

## Changes from v3 (round 3 fixes — 2 precise points, both verified against real code before fixing)

- Experiment D collision handling: v3 incorrectly assumed uniform `.txt` collision behavior across generators. Verified against real code: `element_luck_short_generator.py` unconditionally overwrites; `western_zodiac_short_generator.py` uses a numbered-suffix loop. Fixed: sidecar naming now always derives from the generator's actual resolved `out_path`, covering both branches explicitly.
- Experiment C date range: v3 said "locked" but only wrote "as of this review" / "this cycle" — not an actual reproducible date range. Fixed: locked to `2026-07-18T00:00:00Z`–`2026-07-27T00:00:00Z` explicitly, matching this cycle's actual query window.

## Changes from v2 (round 2 fixes, unchanged from v3)

- §0 expanded: raw evidence now included inline; `status.publishAt`/`uploadStatus` checked and reported; overclaiming language ("not a script artifact," "ruled out") softened to match what isolated queries actually prove; quarantine reframed around the *public* publish day, with anomalous rows preserved (not discarded) and labeled with a reason code rather than implied to be corrupt/invalid.
- §2 table: priority-ordering basis clarified (by score, not raw Impact); Experiment E's Confidence rationale corrected (detection confidence, not mechanism confidence); per-row justification made specific.
- Experiment D: added concrete schema/version, naming contract, missing/corrupt/stale behavior, collision handling, backward compatibility, and a concrete registry-migration rollback plan.
- Experiment C: locked an actual population, date range, sample rule, and threshold instead of placeholders.
- Corrected the round-1 issue count (10, not 9) in all references.

---

## 0. Data-integrity investigation (top priority — expanded with raw evidence per round-2 request)

**What was found:** 3 videos show `real_pt_day_rows` with a PT day earlier than the PT-equivalent of their own public `publishedAt`: `_m0aX_gJbaw` (publish `2026-07-26T05:00:25Z`, real row PT `2026-07-24`), `AuUpRQZOcwc` (publish `2026-07-26T08:00:09Z`, real row PT `2026-07-24`), `B_i31QRy670` (publish `2026-07-26T16:20:34Z`, real row PT `2026-07-22`, 4 days earlier).

**Investigation performed, with raw evidence:**

1. **Channel/credential verification** via `channels.list?mine=true`: Phong Thủy credentials confirmed as `channelId=UCabOUyNfseJfu-Xy_KXz2rw` ("Astro Việt Insights"); Phật giáo credentials confirmed as `channelId=UCQRsHSC8dBcLvCvrj7CLvKA` ("Trần Kim Liên"). `_m0aX_gJbaw`/`AuUpRQZOcwc` snippet.channelId matches Phong Thủy; `B_i31QRy670` snippet.channelId matches Phật giáo — both correct, no cross-channel mismatch.

2. **A real bug found in my own first investigation pass:** I initially re-checked `B_i31QRy670` using the *wrong* (Phong Thủy) credentials, which is why that first isolated query returned nothing. Re-run with the correct Phật giáo credentials confirmed the video and reproduced the anomaly (see raw output below).

3. **Isolated single-video queries (raw output, not just the transformed bundle), with credential source noted:**
   ```
   _m0aX_gJbaw (Phong Thủy creds): [['2026-07-20',0,0,0,0], ['2026-07-21',0,0,0,0], ['2026-07-22',0,0,0,0], ['2026-07-23',0,0,0,0], ['2026-07-24',2,0,0,116.23]]
   AuUpRQZOcwc (Phong Thủy creds): [['2026-07-20',0,0,0,0], ['2026-07-21',0,0,0,0], ['2026-07-22',0,0,0,0], ['2026-07-23',0,0,0,0], ['2026-07-24',3,0,0,216.69]]
   B_i31QRy670 (Phật giáo creds, corrected): [['2026-07-20',0,0,0,0], ['2026-07-21',0,0,0,0], ['2026-07-22',2,0,0,119.9], ['2026-07-23',0,0,0,0], ['2026-07-24',0,0,0,0]]
   ```
   (columns: `[day, views, likes, comments, averageViewPercentage]`)

4. **`status.publishAt`/`uploadStatus` checked (round-2 request):**
   ```
   _m0aX_gJbaw:  publishAt=None, privacyStatus=public, uploadStatus=processed
   AuUpRQZOcwc:  publishAt=None, privacyStatus=public, uploadStatus=processed
   B_i31QRy670:  publishAt=None, privacyStatus=public, uploadStatus=processed
   ```
   **Platform limitation, stated explicitly rather than treated as resolved:** `status.publishAt` is a scheduled-release field that YouTube clears once a video goes public — it cannot tell us anything about the video's state *before* it went public. The YouTube Data/Analytics APIs do not expose a historical scheduling or preview-playback audit trail for a video that is now public. This means the "Studio preview before public release" hypothesis below **cannot be confirmed or ruled out with the tools available** — this is a genuine platform-access limit, not a gap in effort.

**What this evidence actually proves (corrected from v2's overclaim):**
- Reproducing on isolated, credential-verified, channel-matched queries rules out **bulk-query cross-contamination** and the **specific credential mismatch found for `B_i31QRy670`** as explanations.
- It does **not** rule out a bug shared by both the bulk and isolated code paths (both use the same underlying `_query()` function and request-construction logic) — raw HTTP-level request/response pairs were not captured and independently inspected outside this codebase's own request layer.
- **Corrected claim:** the anomaly is *reproduced outside the bulk query*; the phenomenon itself (non-zero rows on a PT day preceding public release) is confirmed real, not a transient fluke — but its *root cause/mechanism* is not established. "Not a script artifact" (v2's phrasing) overstated this; withdrawn.

**Most plausible explanation, presented as an unconfirmed hypothesis, not a conclusion:** YouTube Studio permits owner preview playback of a scheduled/private video before it goes public. If such preview plays are counted by Analytics and attributed to the actual PT day they occurred, that would produce exactly this pattern — genuine data, just not applicable to *public* audience performance. **Confidence: LOW that this specific mechanism is correct** (plausible, consistent with the evidence, but unconfirmed and unconfirmable with available tools) — not MEDIUM as v2 stated for the mechanism itself (v2's MEDIUM confidence was intended for "the investigation is complete," which is a different claim; this is now stated separately to avoid conflating the two).

**Resolution applied in this revision:**
- The invariant is now defined against the **public** publish PT day specifically (not just "the video's own viewable PT day," which round 2 correctly noted is ambiguous for a channel owner who could preview it earlier).
- Anomalous rows are **preserved in the raw data with a reason code and provenance note** (e.g. `"quarantine_reason": "PT day precedes public publish PT day"`) — not discarded, and not labeled as corrupt or untrustworthy. They are excluded specifically from *public-performance* analysis, which is the narrower and more defensible claim.
- This affects only the 3 small-sample rows (2-3 views each); it does not affect `uHwa6nFBtkc` or `YStIdWWuXcU`, so no §1 conclusion changes as a result.

---

## 1. Root-cause analysis

*(§1.1-§1.6 content unchanged from v2 — that content was confirmed fully resolved in round 2. Reproduced here for a self-contained artifact.)*

### 1.1 Two videos have large, real retention samples — but "engagement difference is real" is not yet established

`uHwa6nFBtkc` (853 PT-day views) and `YStIdWWuXcU` (586 PT-day views). The bundle's own fields don't reconcile under a shared-denominator assumption: `uHwa6nFBtkc` — 151 min / 853 views ≈ 10.62s/view vs. reported AVD 24s; `YStIdWWuXcU` — 92 min / 586 views ≈ 9.42s/view vs. reported AVD 14s. This gap far exceeds rounding error. Until the denominator/definition question is resolved against current API documentation or an `engagedViews` field, this diagnosis states only that the API returned substantially different AVD/AVP values for the two videos — not that the difference is statistically established. **Confidence: LOW** on any interpretation of the retention gap.

### 1.2 Duration is a potential design difference — not established as a confound

The arithmetic (24/27=88.9%, 14/41=34.1%, 91.9%/35.13%=2.62x, 24s/14s=1.71x) is correct, but AVP is duration-normalized by definition, so the two ratios necessarily differ — this is a property of the metric, not evidence of causation. With one video per channel, duration cannot be separated from hook, content, topic, or audience effects. The earlier "loop/rounding methodology" explanation for the 24.81s-vs-24s discrepancy was unsupported speculation and is retracted; the discrepancy remains unexplained.

### 1.3 `hook_score` persistence gap (carried from cycle 1) — unchanged, still open

No production change has been made.

### 1.4 The Analytics pull methodology gap (PT/UTC) — confirmed mechanism, availability claims scoped down

Querying with `dimensions=day` is confirmed interpreted in Pacific Time, and the `2026-07-24` bucket contains 853 real views for `uHwa6nFBtkc` specifically. No broader claim about "entire first-day activity" or a complete explanation of every sibling video's availability is made, given §0's anomaly.

### 1.5 9 of 17 videos still show no processed-day data; the rest are quarantined or too small to interpret

Of the 8 videos with any non-empty `real_pt_day_rows`: 2 large-sample and usable (§1.1, with caveat), 3 quarantined per §0 (public-day-preceding anomaly), 3 small-sample (1-3 views) and uninterpretable but not quarantined.

### 1.6 Traffic overwhelmingly comes from the Shorts feed

Unchanged — channel-level, wide-window, not attributable to individual videos in this batch.

---

## 2. Prioritization — Impact × Confidence × Effort (revised)

Scale 1(low)-3(high) for Impact and Confidence; 1(low)-3(high) for Effort (higher = more work). Score = (Impact × Confidence) / Effort. **Priority order below is by Score, not by Impact alone — noted explicitly because Score and Impact can rank items differently (e.g. Experiment D has higher Impact than Experiment E, but a lower Score due to its much higher Effort).** Scores remain ordinal-derived approximations, not precise measurements.

| # | Item | Impact | Confidence | Effort | Score | Justification (per-row, specific) | Verdict |
|---|---|---|---|---|---|---|---|
| E | Automated public-day quarantine invariant | 2 — prevents future silent misinterpretation of anomalous rows, doesn't itself fix any content or unlock new data | 3 — **this is confidence in the tooling's ability to detect a row that violates the invariant** (a simple date comparison, directly testable), **not confidence in why the anomaly happens** (that remains LOW, per §0) | 1 — a validation function over already-fetched data, no new API calls or fetch-logic changes | **6.0** | Cheapest possible fix for the specific gap that caused this cycle's most serious miss; low effort makes it top-of-queue even though its impact ceiling is lower than D's | Approved → Experiment E |
| A | Rolling-window + per-video day-dimension pull | 2 — improves data completeness for every future cycle | 3 — mechanism (PT bucketing) is independently verified | 2 — real fetch-logic work: quota, pagination, duplicate-row and partial-response handling, plus tests | **3.0** | Meaningful engineering effort, correctly no longer scored as trivial | Approved → Experiment A |
| D | hook_score persistence contract | 3 — highest ceiling: the only path to ever correlating judge scores with real outcomes, for every future video | 3 — root cause (score computed then discarded) is a verified code fact | 3 — confirmed (via direct code read, both by me and independently by Codex) to touch every generator using the `write_short_bundle_file(script)`-only pattern, not just the runner | **3.0** | Highest-impact item on this list; its Effort is genuinely large, which is why its Score ties with A despite outranking it on Impact | Approved → Experiment D |
| C | Accuracy/tone audit | 2 — brand-risk mitigation on a verified, already-live gap | 2 — a locked population/rubric now exists (this revision), but the audit hasn't been run yet, so confidence in *delivering* a reliable answer is still moderate, not high | 2 — real rubric + stratified sampling + two-pass adjudication is a genuine review task | **2.0** | Scope now executable (see Experiment C below), but still real effort, not a quick pass | Approved → Experiment C |
| B | AVD/AVP reconciliation reporting control | 1 — necessary hygiene, but doesn't by itself resolve whether the underlying numbers are trustworthy (that's §1.1, still open) | 2 — the reconciliation-check mechanism itself is straightforward to implement correctly | 1 — a report-formatting and one-arithmetic-check addition | **2.0** | Necessary but explicitly not sufficient — paired with the still-open §1.1 question, not a fix for it | Approved → reclassified as reporting control |
| 5 | Duration-shortening content test | 2 | 1 | 2 | 1.0 | Unchanged from v1/v2 | Deferred |
| 6 | Western Zodiac comment-CTA test | 1 | 1 | 2 | 0.5 | Unchanged from v1/v2 | Deferred |

---

## 3. Experiment / action cards

### Experiment E — Automated public-day quarantine invariant

- **Objective:** stop treating rows dated before a video's *public* publish PT day as ordinary `real_pt_day_rows` without manual re-discovery each cycle.
- **Change:** validation step in review-pull tooling computes each video's public-publish PT day (from `snippet.publishedAt`, converted to PT) and flags any Analytics row dated earlier with `"quarantine_reason": "PT day precedes public publish PT day"` — row is preserved in the raw bundle with this label, not discarded, and excluded specifically from public-performance interpretation (not labeled invalid/corrupt).
- **Expected metric:** count of quarantined rows per pull, surfaced explicitly.
- **Success criteria:** on this cycle's dataset, the check flags exactly the 3 rows identified in §0 (`_m0aX_gJbaw`, `AuUpRQZOcwc`, `B_i31QRy670`) and does not flag `uHwa6nFBtkc` or `YStIdWWuXcU`.
- **Rollback condition:** none needed — read-only validation logic in review tooling only.

### Experiment A — Rolling-window Analytics pull

- **Objective:** retrieve real, already-processed per-day Analytics data without assuming a fixed UTC lag offset.
- **Change:** rolling ~10-day window, `dimensions=day` per video, with explicit quota, pagination, duplicate-row, and partial-response handling.
- **Expected metrics:** *Retrieval correctness* — on a known-good video/day set, returns 100% of the rows a single-day control query returns. *Analytical usability* — count of videos per cycle with `views ≥ 500` in non-quarantined `real_pt_day_rows`.
- **Success criteria:** retrieval-correctness test passes on the known-good fixture; usability metric reported per cycle without a fixed target (depends on real-world elapsed time, outside this experiment's control).
- **Rollback condition:** revert to fixed-window query if quota/pagination handling introduces failures; read-only tooling, no production impact either way.

### Experiment D — hook_score persistence contract

- **Objective:** stop discarding `generation_hook_score` before it reaches the registry.
- **Change — now fully specified per round-2 request:**
  - **Schema/version:** sidecar file `{key}.meta.v1.json` (version in filename and as a top-level `schema_version: 1` field), containing `{generation_hook_score, winning_strategy, iteration_count, category, generator_name, schema_version}`.
  - **Naming/mapping contract:** sidecar filename is derived 1:1 from the same `key` the generator already uses to name its `.txt` output (e.g. `CUNGHD_BchDng_Short.txt` → `CUNGHD_BchDng_Short.meta.v1.json`), so the runner can locate it via simple filename substitution — no separate ID-mapping table needed.
  - **Missing/corrupt/stale sidecar behavior:** if the sidecar file is absent, unparseable JSON, or has a `schema_version` the runner doesn't recognize, the runner logs a warning and proceeds with `generation_hook_score: null` (fail-open on this specific field only — does not block TTS/render/upload, since the score is observational metadata, not a content gate).
  - **Collision handling — corrected per Codex round 3 (verified against real code, not assumed uniform):** generators are NOT uniform here. `element_luck_short_generator.py`'s `write_short_bundle_file()` unconditionally overwrites its `.txt` at a fixed date-derived path. `western_zodiac_short_generator.py`'s version instead loops (`while out_path.exists(): n += 1`) to find a free numbered-suffix path (`CUNGHD_{slug}_2_Short.txt`, etc.) and never overwrites. The sidecar contract must follow whichever path the `.txt` actually resolved to, not assume one behavior: the sidecar filename is always derived from the generator's *actual* `out_path` after its own collision logic has run (e.g. `.txt` becomes `CUNGHD_BchDng_2_Short.txt` → sidecar is `CUNGHD_BchDng_2_Short.meta.v1.json`; if a generator overwrites its `.txt`, the matching sidecar is overwritten too). Tests must cover both branches (overwrite-style and numbered-suffix-style generators), not just one.
  - **Backward compatibility:** registry entries created before this ships keep `hook_score: null` permanently (already established in cycle 1 as non-recoverable — no migration attempted).
  - **Resume/idempotency:** if the batch runner is interrupted after the sidecar is written but before registry ingestion, re-running the batch must re-read the sidecar (not silently skip it) — the sidecar's existence, not the registry state, is the source of truth for whether a score is available to ingest.
- **Expected metric:** non-null `generation_hook_score` in the registry for videos generated after this ships.
- **Success criteria:** tests covering every generator in scope (the 9 named in v2), missing/corrupt/stale sidecar handling, collision handling, and registry persistence across an interrupted-then-resumed batch run.
- **Rollback condition — concrete plan:** revert in three independent layers if needed: (1) generators stop writing sidecars (simple flag/revert per generator, does not affect `.txt` output or content), (2) runner stops attempting sidecar ingestion (reverts to always writing `null`, current behavior), (3) any registry entries that already have a non-null `generation_hook_score` from a partial rollout are left as-is (additive data, does not need to be un-written — it doesn't gate or alter any pipeline behavior).

### Experiment C — Accuracy/tone audit

- **Objective:** determine whether the two confirmed absolute-language instances from cycle 1 (`CONGIAP20260726_ConGiap_01`, `MENH_Kim_MauSacHopMenh_01`) are isolated or systemic.
- **Change — now locked, not placeholder:**
  - **Population, date range corrected per Codex round 4 (previous claim was wrong — verified against the real registry before fixing):** all Phong Thủy Short scripts with `status="uploaded"` in `output/shorts/Phong Thủy/registry.json`, with `publish_at` between **2026-07-18T00:00:00Z and 2026-07-27T00:00:00Z** inclusive. Querying the real registry against this exact range returns **12 entries, not 8** — the previous version of this card incorrectly assumed the range would isolate only this cycle's 8-video batch; it does not, because 4 additional videos from 2026-07-24 (`THAN20260724_12ViThan_01`, `CONGIAP20260724_ConGiap_01`, `MENH_Hoả_MauSacHopMenh_01`, `KIENTHUC_HnhnhndtrcquanvchukNgHnhTngKhc_01`) also fall in this range and were not part of this cycle's 17-video analytics batch. **Resolution: the population is expanded to the real 12, not narrowed to fabricate a match with 8** — a larger real population is strictly better for this audit's actual purpose (determining isolated vs. systemic), not a compromise. (Separately corrected: the earlier claim that this range "matches `01_cursor_report.md`'s wide-window query" was also wrong — that report's traffic-source query window is `2026-07-20`–`2026-07-27`, not `2026-07-18`–`2026-07-27`; this population's date range is defined on its own terms for audit purposes, not tied to that unrelated query window.) This remains a fixed, reproducible snapshot: re-querying the registry with the same `publish_at` bounds at a later date should be expected to return 12 or more (if more are uploaded later within range) — the bound, not "current registry state," defines the population, and any growth is additive/discoverable, not a silent redefinition.
  - **Stratification:** by generator — 8 generators represented in the corrected 12-video population: `element_luck`, `western_zodiac`, `iching`, `storytelling`, `zodiac`, `element_color` (this cycle's 8-video batch) plus `twelve_gods` and `educational` (the 4 additional 2026-07-24 entries).
  - **Checklist (operational, not just categories):** for each script, flag any sentence that (a) states a future outcome as certain without a hedge word (không có "có thể/thường/theo quan niệm..."), (b) frames an anxiety/threat scenario, (c) implies a deadline/urgency not organically present in the topic, (d) omits a "theo quan niệm/truyền thống" framing for a belief-based claim presented as fact.
  - **Adjudication:** two independent passes (both performed by me, at least 24 real hours apart if feasible within this workflow, otherwise two independent read-throughs in the same session using a fresh context) — any sentence flagged by only one pass is marked "disputed" and reported separately, not silently dropped or silently included.
  - **Decision threshold:** any instance of (b) or (c) above is zero-tolerance and escalates immediately, regardless of count. An overall rate of (a)/(d) instances above **1 per script on average** across the population triggers a rubric-strengthening follow-up proposal (a separate item, not folded into this audit's own success criteria).
- **Expected metric:** numerator/denominator (instances found / scripts reviewed) per checklist category, with the disputed-sentence list reported separately.
- **Success criteria:** audit completed against the full locked population (12 scripts) with both passes recorded; decision threshold applied and stated explicitly (triggered or not).
- **Rollback condition:** N/A — read-only audit.

### Reporting control B — AVD/AVP reconciliation

- **Objective:** prevent future reports from citing `averageViewPercentage` without surfacing whether the underlying fields actually reconcile.
- **Change:** every future report citing AVP must also cite AVD, the video's own duration, and a reconciliation check: `estimatedMinutesWatched × 60 / views` compared against reported AVD, with a **defined tolerance of ±20%** (chosen to be well outside plausible rounding error, given this cycle's actual gaps were 2.3x/1.5x — the tolerance is intentionally strict enough to flag both of this cycle's videos). If outside tolerance, the report carries an explicit warning instead of an interpretation.
- **Success criteria:** future reports include the reconciliation check with the stated tolerance; §1.1 in this document is the reference example of a flagged (not interpreted) case.
- **Rollback condition:** none — reporting format only.

---

## 4. Explicit non-recommendations

- **Not** proposing a duration-shortening content experiment — one video pair (n=1 per channel) cannot support this; reinforced by §1.2's retracted causal framing.
- **Not** re-opening the Western Zodiac comment-CTA question — unchanged from v1/v2.
- **Not** proposing any category-level cuts or emphasis shifts — unchanged.
- **Not** claiming Experiment A "accumulates" real-retention videos — it retrieves/observes already-processed data only. Experiment E (public-day quarantine) is a prerequisite for Experiment A's output being trustworthy, and for any future duration/category analysis.
- **Not** claiming the anomaly investigation (§0) has identified its root cause — only that specific alternative explanations (bulk contamination, the found credential bug) have been ruled out. The preview-playback hypothesis remains unconfirmed and is stated as such throughout.

---

*Next: submit this patched v4 diagnosis to Codex CLI for round-5 review.*
