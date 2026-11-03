# Ticket #124 — Fact-grounded check + Selective Semantic Review

Implementation is research-only under `research/fact_store/grounded/`. The deterministic checker consumes a package, store and verification result; it makes no model call. The semantic reviewer sends the package and selected facts in one call and supports offline `--replay`. The pipeline includes primary packaging and alternates, plus an adversarial batch mode.

## Review status

### Fix round 1

Fixed Vietnamese number tokenization to preserve NFC diacritics and recognize spelled-out quantities only when attached to a unit or magnitude. Bare “năm” is not a quantity. Verified number and date grounding now checks quantity/time fields, Vietnamese fact statements, and evidence spans; the deterministic explanation mode (`--explain`) includes grounded tokens and the matching fact IDs. Contradictions require a verified fact with the same mentioned entity, measure and time role; the issue records token, entity, measure, fact ID and fact value. Other unmatched tokens remain review issues.

The reviewer now collects token totals from usage metadata across JSON events and token-count events. `eval-adversarial` accepts a top-level JSON list (using the input filename stem as the topic for each entry) and accepts `--workers`. Added focused regressions for 1909 evidence grounding, the year word, and 16-year duration grounding. Focused tests pass. The `--workers` argument is accepted for CLI compatibility; processing remains sequential in this round.

Implemented fail-closed checks for unknown IDs, unverified references, disputed-fact attribution, names, numeric/date tokens, semantic-risk sentences, and dropped conditions, attribution and modality. A deterministic contradiction sets `REJECT`; semantic `contradicted` also sets `REJECT`. An incomplete review or any unresolved deterministic review issue remains `REVIEW`.

## Evaluation

The adversarial CLI reports the count of packages accepted by this pipeline as `false_acceptance_count`; that is a mechanical tally, not a human accuracy score. The legacy adversarial corpus was not present in a safe, identified `items_dir` during this implementation, so no corpus result is claimed. Lead review remains necessary to label false acceptance and evaluate pipeline quality, precision and cost.

## Limits

Token parsing currently covers Arabic numerals, common Vietnamese number words, common magnitudes, dates and store entity aliases. This is intentionally a conservative first pass and needs adversarial corpus calibration. Reviewer token/model metadata is read from CLI JSON events and reported as unknown when the CLI emits no metadata; model-authored claims are ignored.
