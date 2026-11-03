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

## Final round (span_id)

Every non-empty packaging field is sentence segmented. Each sentence retains its full text and receives a stable ID in the form `field:index:sha1(sentence)[:8]`. Deterministic issues and semantic-review requirements point to that ID; numeric/name issues also retain their token or subspan. Empty fields produce no spans.

The reviewer receives `spans_to_review` entries (`span_id`, `field`, `sentence`) and only the verified facts retrieved for those sentences. It must return exactly one row per reviewed ID, with verdict, fact IDs and a non-empty reason. Unknown, duplicate, missing or malformed rows fail closed to `REVIEW`; a semantic `contradicted` row returns `REJECT`. `evidence_missing` is recorded when a sentence contains a number or known entity but no verified facts are retrieved; that sentence is not sent to the model and remains `REVIEW`. The result reports the unique retrieved fact count.

Decisions use span IDs only. Deterministic contradictions and reviewer contradictions reject. Other deterministic issues stay open, except `dropped_qualifier` and `unattributed_disputed`, and those can close only when the exact issue span is `supported`. An issue lacking a valid span ID stays in review. Approval requires every required semantic span to have exactly one supported row and no open deterministic issue.

Quantity matching uses explicit identity/conversion rules: `m` and `km` normalize to meters (factor 1 and 1,000), `%` remains distinct, `USD`/`$`/`đô` share a currency identity, and `tỷ`/`triệu` are applied as magnitude factors. There is no unit substring matching. Regression coverage includes all three previously reported P1s, malformed review IDs, evidence gaps, deterministic issue persistence, contradiction rejection and list-item topic mapping.

Token accounting follows the Codex JSONL `event_msg` → `payload.type=token_count` → `payload.info.total_token_usage` shape (also present in the repository's agent-ledger fixtures) and top-level `usage`/`token_usage` on result/turn events. The reported count is the **last usage-bearing event**, never a sum of cumulative token-count snapshots; if an event has input and output counts but no total, those two are added. Model and tokens are read only from CLI events, not reviewer-authored JSON. The local CLI reports version `codex-cli 0.165.0`; this implementation did not invoke a live model during tests.

Verification: `pytest -q research/fact_store/grounded/test_grounded.py` — 13 passed. Full-repository `pytest -q` could not complete collection: 26 unrelated test modules require unavailable `soundfile`, `scipy`, `huggingface_hub` or `sea_g2p` packages (6 tests skipped). No live reviewer/model invocation was made.
