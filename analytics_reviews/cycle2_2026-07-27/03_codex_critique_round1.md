# Codex CLI — Independent Adversarial Review (Cycle 2, Round 1)

**Reviewed:** `00a_pt_utc_finding.md`, `01_cursor_report.md`, `02_claude_diagnosis_v1.md`, cross-checked against `00_raw_data_bundle_v2.json` and real code (`short_batch_runner.py`, multiple generator files).

**Verdict: NEEDS_REVISION** — 3 High, 4 Medium, 2 Low issues, each with Severity/Evidence/Recommendation.

---

## High — Dismissing the "views before publish" anomaly was a priority mistake

- **Severity:** High
- **Evidence:** §1.7/§4 deferred investigation because each row only has 2-3 views. But the bundle shows: `_m0aX_gJbaw` (publish `2026-07-26T05:00:25Z`, real row dated PT `2026-07-24`), `AuUpRQZOcwc` (publish `2026-07-26T08:00:09Z`, row PT `2026-07-24`), `B_i31QRy670` (publish `2026-07-26T16:20:34Z`, row PT `2026-07-22`, 4 days earlier). This is not a retention-estimation problem requiring a large sample — a single view before the video existed is enough to prove at least one assumption (publishedAt, video filter, channel/credential, caching, or row-to-video mapping) is wrong. The "unlisted preview before public" explanation is not established either.
- **Recommendation:** Escalate to a P0 data-integrity investigation before using the bundle for any decision: re-run isolated single-video queries; save raw request params + raw response, not just the transformed bundle; verify channel/credentials, video ID, `publishedAt`/`publishAt`, upload/schedule history; add an automated invariant that a PT-day row cannot predate the video's own viewable PT day — violations should be quarantined, not labeled `real_pt_day_rows`.

## High — "Engagement difference is real" is not cleanly proven by the current data

- **Severity:** High
- **Evidence:** §1.2 uses "853 and 586 views" to argue the numbers "aren't noise," but the bundle's own fields don't reconcile if they share a denominator: `uHwa6nFBtkc` — 151 min / 853 views ≈ **10.62 s/view**, not the reported 24s average view duration. `YStIdWWuXcU` — 92 min / 586 views ≈ **9.42 s/view**, not the reported 14s. This gap is far larger than rounding error, and suggests different fields may use different denominators/semantics (or there's a real data issue). Without `engagedViews` or a confirmed denominator, large view counts alone don't establish that AVD/AVP are statistically reliable.
- **Recommendation:** Before calling the engagement difference "real," verify the current API's definitions of `views`, `averageViewDuration`, `averageViewPercentage` for Shorts specifically; pull `engagedViews` if available; state the denominator explicitly. Until verified, describe this only as "the API returned substantially different AVD/AVP values," without asserting statistical reliability from the raw view counts.

## High — "Duration is a confound" is presented close to a causal conclusion

- **Severity:** High
- **Evidence:** The arithmetic is correct (24/27=88.89%, 14/41=34.15%, 91.9/35.13=2.616x, 24/14=1.714x), but a smaller ratio in absolute seconds doesn't prove duration causes or confounds the retention gap — AVP is already duration-normalized by definition, so the two representations naturally produce different ratios. With exactly one video per channel, duration cannot be separated from hook, content, audience, or traffic. Additionally, 91.9% × 27 = 24.81s, not the reported 24s — more consistent with AVD being truncated/rounded to whole seconds than with the "loop/rounding methodology" explanation offered, which has no supporting evidence.
- **Recommendation:** Reframe as: "duration is a potential design difference, and AVP should be read alongside AVD; the data is insufficient to quantify or attribute the gap to duration." Drop the "percentage framing overstates engagement" claim and the unsupported loop/rounding explanation.

## Medium — Experiment A's metric and success criterion don't measure the change's actual impact

- **Severity:** Medium
- **Evidence:** Card A defines "usable" as `views > 0`, while §1.5 and the Cursor report both say 1-3-view rows are "too small to interpret." By the card's own stated threshold, 8/17 videos count as usable, not 2/17. The success criterion ("materially more than 2/17 ... assuming enough real-world time has passed") is fully confounded by processing time — a rolling window doesn't make Analytics process faster — and neither "materially more" nor "enough time" has a defined threshold.
- **Recommendation:** Split into two metrics: retrieval correctness (on a known-good video/day set, the rolling query must return 100% of the rows a single-day control query returns) and analytical usability (define the threshold up front, e.g. `views ≥ 500`, measured after a fixed PT delay). Success criteria should be a defined test fixture/A-B query, not a cross-cycle video count comparison across videos of different ages. Add explicit rollback/failure conditions for quota, pagination, duplicate rows, and partial responses.

## Medium — Experiment D is underspecified; effort is likely underrated and rollback scope is wrong

- **Severity:** Medium
- **Evidence:** `short_batch_runner.py:276-283` only sets `hook_score=None` and saves the registry; the runner currently reads only the text segment, with no sidecar discovery/validation logic. In the sample generator `element_luck_short_generator.py`, `write_short_bundle_file(...)` only accepts `script` and writes a `.txt`; `main()` calls it with `result["script"]`. The same pattern appears across many generators (`educational`, `twelve_gods`, `western_zodiac`, `iching`, `zodiac`, `zodiac_month`, `element_color`, `storytelling`). This touches many writers, a naming/mapping contract, resume/idempotency, and ingestion tests — not a small runner-only fix. The card's "revert runner ingestion only" rollback doesn't undo the generator/sidecar side or handle partially-written registry entries.
- **Recommendation:** Rate effort at least 3, or narrow scope. Specify schema/version, a 1:1 sidecar-to-source-file/segment naming contract, behavior on missing/corrupt JSON, resume, collisions, and backward compatibility. Success criteria must include tests across every generator in scope, missing/corrupt/stale sidecars, and registry persistence across resume. Rollback must cover writers, reader, and any already-migrated registry data.

## Medium — Experiment C has no sampling frame or measurable rubric for high-risk content

- **Severity:** Medium
- **Evidence:** The card only says "recently-published," "count of additional instances," and "categorized by severity" — no defined script count, date range, category, rater, severity rubric, or a threshold for concluding isolated vs. systemic. Given `risk_level=high` and the mandatory calm/reverent/non-manipulative requirement, "audit completed and documented" as a success criterion only measures that the task happened, not its coverage or reliability. The card's Confidence=3 has no basis reflected in its own content.
- **Recommendation:** Lock a population/window, stratify by generator/category, define a checklist (absolute claims, anxiety/threat, manufactured deadlines, certainty-hedging, reverent tone), use two independent passes or an adjudication process, and report numerator/denominator with evidence examples. Set decision rules up front — e.g. any threat/deadline is zero-tolerance, an absolute-claims rate above a set threshold triggers a rubric-strengthening proposal.

## Medium — Experiment B isn't really an experiment, and its success criterion doesn't check correctness

- **Severity:** Medium
- **Evidence:** The card itself lists expected metric "N/A" and rollback "none" — this is a reporting requirement, not an experiment. Success only requires two numbers "side by side," while the bundle already shows AVD, AVP, estimated minutes, and views don't reconcile under a shared-denominator assumption (see the High finding above). A report could satisfy this card's format while still being semantically wrong.
- **Recommendation:** Rename to a reporting control. Require metric definitions/denominators, source field, precision, a sample-size threshold, and a reconciliation check between the aggregates. When reconciliation fails, the report must carry a warning instead of an interpretation.

## Medium — The Impact×Confidence×Effort table lacks per-cell justification and is biased toward the pre-selected actions

- **Severity:** Medium
- **Evidence:** A, B, and C all score 2×3÷1=6 despite very different real effort (A needs fetch changes, day-row handling, quota handling, and tests; B is a presentation rule; C is an audit with no defined population/rubric that could consume significant manual review time). Meanwhile the data-integrity anomaly has no row in the table at all. C's Confidence=3 doesn't match an objective that is explicitly asking whether an error is systemic. The inverted-effort scale also divides ordinal 1-3 ratings arithmetically, producing false precision.
- **Recommendation:** Add the data-integrity investigation as the top-priority row. Document the justification behind every score. Separate one-time implementation effort from recurring operational effort and risk. Don't use decimal scores as a ranking decision when the inputs are only ordinal — or at minimum pair them with a sensitivity/tie-break rule.

## Low — §1.1/§1.5 overstate certainty about data availability

- **Severity:** Low
- **Evidence:** §1.1 calls the two-video availability a "direct consequence" of the PT/UTC mechanism and attributes it to the "earliest UTC slot" landing on an already-processed day. `YStIdWWuXcU` at 03:30Z fits, but the 08:00/11:00/14:00Z videos still show 1-2 views attributed to PT `2026-07-24` despite their publish timestamps already falling on PT `2026-07-25` by simple offset math — which the anomaly itself contradicts. `00a` also states the "entire first day of activity" lands on `07-24` for a video published at 22:00 PT, but only activity before midnight PT belongs to that bucket — activity after midnight belongs to `07-25`.
- **Recommendation:** Limit the claim to what was actually tested: the day dimension is interpreted in PT, and the `07-24` bucket had 853 views for one specific video. Don't generalize to "entire first-day activity" or explain every sibling video until the anomaly/filtering question is resolved.

## Low — "Explicit non-recommendations" isn't fully internally consistent

- **Severity:** Low
- **Evidence:** §4 says more real-retention videos are needed first, "which Experiment A is intended to help accumulate." Experiment A only retrieves rows Analytics has already processed — it doesn't create new videos, views, or retention observations, and doesn't speed up processing. §4 also declines to investigate the anomaly while §3 proposes changing the very tooling that shows signs of mis-attributing rows.
- **Recommendation:** Change the wording to "Experiment A helps retrieve/observe available data correctly," not "accumulate" evidence. Make data-integrity validation a prerequisite of both Experiment A and any duration/category analysis.

---

**NEEDS_REVISION**
