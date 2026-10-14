# Codex CLI — Independent Adversarial Critique (Round 2)

**Reviewed:** `04_claude_diagnosis_v2.md` against all 9 required fixes from round 1, cross-checked directly against `01_cursor_analytics_report.md`, `03_codex_critique_round1.md`, and real registry data (Codex re-grepped `output/shorts/Phong Thủy/registry.json` and searched for any surviving sidecar/log artifacts for the 8 videos).

**Verdict: CẦN SỬA** — 8 of 9 points fully resolved, 1 High-severity point partially resolved.

## Per-point results

1. **Critical — P0-1 rebuilt as a contract change: ĐÃ SỬA ĐỦ (fully resolved).**
2. **Critical — Kinh Dịch identity CTA removed: ĐÃ SỬA ĐỦ (fully resolved).** Kinh Dịch dropped entirely; Western Zodiac-only, risk raised to medium, gated on KPI confirmation + brand review.
3. **High — Accuracy/tone audit + "aligned by construction" retraction: ĐÃ SỬA ĐỦ (fully resolved).**
4. **High — Retention measurement claim + time-normalization: SỬA MỘT PHẦN (partially resolved).** The measurement-error fix (retention alone ≠ discovery-vs-CTR distinguisher) is correct. But v2's P0-2 promised comparing the *current 8-video batch* at true T+24h/T+48h/T+72h snapshots — Codex verified this pipeline only ever captured one lifetime-stat snapshot (~2026-07-27) per video, not repeated timestamped pulls, so those exact snapshots cannot be reconstructed retroactively for this batch. Required either (a) using per-day Analytics rows as a labeled daily approximation for the current batch, or (b) scoping true T+24/48/72h snapshots to future cohorts only.
5. **High — Event-anchoring guardrail: ĐÃ SỬA ĐỦ (fully resolved).**
6. **Medium — Causal-language downgrade: ĐÃ SỬA ĐỦ (fully resolved).**
7. **Medium — n≥10-15 reframed as checkpoint: ĐÃ SỬA ĐỦ (fully resolved).**
8. **Medium — KPI-before-comments: ĐÃ SỬA ĐỦ (fully resolved).**
9. **Medium — "for any video, ever" scoped correctly: ĐÃ SỬA ĐỦ (fully resolved).** Codex additionally checked for surviving sidecar/output-JSON/log artifacts for the 8 videos — confirmed none exist, so the retroactive-recovery limitation as stated is accurate.

## New issue surfaced

**Medium — the retroactive-snapshot plan in P0-2, as written, promised a kind of data the pipeline never collected for this batch.** Not a measurement error in the analysis itself, but an achievability gap between what P0-2 claims to deliver and what's actually reconstructable for the 8 videos already published.

## Fix applied (post-round-2, before round 3 submission)

`04_claude_diagnosis_v2.md` §1.3 and §3/P0-2 revised: current batch now explicitly limited to day-level Analytics approximation (clearly labeled as such, not claimed to be hour-precise), with true T+24/48/72h snapshots scoped to future cohorts via a new scheduled-pull mechanism, not retroactively promised for this batch.
