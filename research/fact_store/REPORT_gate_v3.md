# Ticket #123 — Gate v3 research report

## Files

- `gate.py`: added `gate_claims(extraction, store, verification, series_context=None, rounding=None)`. The legacy regex gate remains callable for compatibility; it is not used by v3 to decide claims.
- `claims.py`, `claims_extraction.schema.json`, `prompts/claim_extract_v1.md`: JSON extraction contract, prompt, CLI/replay runner and incremental reuse planner.
- `__main__.py`: added `extract-claims` and `reuse` commands.
- `predicates.json`: added `owns`.
- `pilot/stores_fixed/ck_bybit_2025.json`: added `part_of(bybit_infra, bybit)` and `owns(bybit, bybit_cold_wallet)`.
- `test_gate_v3.py`: offline replay checks.

## Replay and validation

Command: `python3 -m pytest research/fact_store/test_gate_v3.py -q`

Result: **3 passed** (Bybit attributed amount / missing attribution / near-2-billion contradiction / organization-victim hack; incomplete and empty extraction; Temiya duration remains REVIEW).

Command: `python3 -m research.fact_store validate research/fact_store/pilot/stores_fixed/ck_bybit_2025.json`

Result: **24 facts, 0 schema or semantic errors**.

## Limitations to resolve before relying on these outputs

- The Bybit store changed but its `store_sha256` in the existing verification file was not recomputed. That verification artifact is stale by contract. The new relationship facts also have provisional research verification entries; regenerate verification through the validator and independently check them before treating those relations as verified evidence.
- The API carries time, scope, condition, modality and attribution, but matching is not complete for every field. In particular, scope equivalence, full condition semantics, time precision, measure conversions, `<` quantities, and an exhaustive predicate-by-predicate contradiction proof still need implementation. Unimplemented or ambiguous comparisons should remain REVIEW; this draft does not claim full v3 conformance.
- `reuse` detects verified fact IDs using a sibling `.verification.json`; its source coverage is currently a conservative file listing, not semantic source-to-entity coverage. Token savings are estimated from per-fact `extraction.tokens_in`; legacy stores without that metadata report zero.
- The replay suite is representative, not the full requested matrix. No external CLI/LLM was invoked.

## Fix round 1

- Normalized extractor polarity (`true` affirmative, `false` negated) before comparison; time text now parses year/month/day forms and compares at the coarser precision. Series frames accept strings or objects and use `series_frames.json` only to satisfy modality framing.
- Restricted contradiction REJECTs to verified facts after matching subject, predicate, measure, unit, polarity, time, and scope; differing value uses `value_contradiction`, differing object role uses `role_contradiction`, and differing attribution uses `attribution_contradiction`. Unsupported dimensions remain REVIEW; negative compromised-system evidence uses `negated_system`.
- Added extractor-selected entity IDs with store membership checks and alias fallback, updated the prompt/schema to v2, and folded one-package runner context and CLI-log provenance parsing into `claims.py`.
- Validation: `python3 -m pytest research/fact_store -q` — **21 passed**. The initial requested #123 checks are covered by `test_gate_v3.py`; no benchmark directory was opened and no external extractor was invoked.
