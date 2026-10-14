# Claude's per-comment classification — Codex Round 2 (Cycle 2)

Round 2 verdict: NEEDS_REVISION. Codex also caught a real bookkeeping error: round 1 actually contained **10 findings (3 High, 5 Medium, 2 Low)**, not 9 as labeled in `03_codex_critique_round1.md`'s header and `03a`'s summary — corrected below and in all cross-references.

All 13 round-2 points (6 "fully resolved" confirmations + 4 "partially resolved" + 3 new issues) reviewed individually.

## Fully resolved, no action needed (6): #2, #3, #4, #7, #9, #10 (renumbered per corrected 10-item count)
Confirmed by Codex directly against v2 content — no further action.

## Partially resolved — accepted, addressed in v3 (4)

**#1 (High) — anomaly investigation gaps** → **ACCEPT.** Fair: v2 asserted "not a script artifact" and "ruled out" more strongly than the evidence supported (isolated queries rule out bulk cross-contamination specifically, not every possible shared-code-path bug), and didn't include the raw evidence directly or check `status.publishAt`/upload status. Fixed in v3: raw isolated-query output now included inline; `status.publishAt`/`uploadStatus` now checked and reported (all three: `publishAt=None`, `uploadStatus=processed` — confirms current state but the Data API does not expose historical pre-public scheduling/preview timelines for videos that are now public, a real platform limitation, stated explicitly rather than treated as solved); claim language softened per Codex's exact suggested wording.

**#5 (Medium) — Experiment D still underspecified** → **ACCEPT.** Added concrete schema/version, 1:1 naming contract, defined missing/corrupt/stale behavior, collision handling, backward compatibility, and an actual rollback plan for partially-migrated registry data (not just "must cover").

**#6 (Medium) — Experiment C still has placeholders** → **ACCEPT.** Locked an actual date range, population, sample rule, and numeric threshold instead of "e.g." placeholders.

**#8 (Medium) — Impact table still has issues** → **ACCEPT.** Fixed: (a) clarified priority ordering is by score, not Impact alone, since Codex correctly noted E's Impact=2 vs D's Impact=3 makes "E is top priority" look inconsistent unless the ranking basis is explicit; (b) corrected E's Confidence justification — only the anomaly's *reproducibility* is demonstrated, not the underlying *mechanism* (Studio-preview theory remains unconfirmed) — Confidence now scoped to "ability to detect the violation," not "understanding why it happens"; (c) added a specific (not boilerplate) justification per row.

## New issues (3) — all accepted

**Medium — quarantine framing implies corruption when the data may be genuinely valid, just inapplicable** → **ACCEPT.** Renamed the invariant to explicitly check against the *public* publish PT day, and changed handling: quarantined rows are preserved in the raw data with a reason code and provenance note, not discarded or implied to be invalid — they're excluded from *public-performance* analysis specifically, which is a narrower and more accurate claim.

**Medium — "mechanism directly demonstrated" overclaims what isolated queries prove** → **ACCEPT.** Same fix as #1 above — reworded throughout to "reproduced outside the bulk query; rules out bulk cross-contamination and the identified credential mismatch; does not rule out a shared-code-path bug since raw HTTP-level requests/responses were not captured before this round."

**Low — round-1 issue count was mislabeled (9 vs actual 10)** → **ACCEPT.** Corrected in this log and cross-references; `03_codex_critique_round1.md`'s own content is unchanged (it's Codex's original output, left as-is), but summaries referencing "9 issues" are corrected to 10 going forward.

---

**Summary: 13/13 accepted this round (10 carried-forward + 3 new).** Revision proceeds to `04_claude_diagnosis_v3.md`.
