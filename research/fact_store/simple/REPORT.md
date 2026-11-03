# Ticket #125 — simplified source grounded review

Implemented a research-only package in `research.fact_store.simple`, with independent deterministic checks, source selection, a batched CLI reviewer, a fail-closed decision layer, replay support, and a `python -m research.fact_store.simple run` command.

`certain_checks` validates required packaging strings and optional claims shape, checks self-declared fact IDs against the store and verification statuses, and matches digit-form numbers only against verified quantity/time fields or explicit fact/source text. Vietnamese punctuation is interpreted as requested; explicit length and scale units are converted. Unmatched numbers and invalid/self-declared IDs create reviewer flags, never a Python rejection. Entity names are only used as exact NFC-normalized store aliases for source retrieval; unknown names are ignored.

`select_sources` retrieves verified facts by mentioned store entity and suggested fact IDs, then adds verified conflict/variant/comparable neighbors. Results carry the fields intended for the reviewer and evidence spans. Count/character caps mark `sources_truncated`; an empty retrieval marks `no_sources`.

`review_batch` sends batches through one `codex exec --json --skip-git-repo-check -s read-only -` invocation per batch, accepts replay JSON, records model and token totals, and divides batch tokens evenly among entries. The prompt is in `review_prompt_v1.md`. The command returns HUMAN_REVIEW for unavailable, malformed, timed-out, missing, duplicate, or unknown reviewer entries; Python ACCEPT additionally requires citations and clean certain-check flags.

## Verification

Ran `python3 -m unittest research.fact_store.simple.test_simple -v`: all 7 tests passed, covering Vietnamese number matching and unit mismatch, unverified IDs, missing citations, REJECT pass-through, malformed replay JSON, missing review entries, duplicate/unknown IDs, missing stores, and timeout behavior.

The implementation does not load production components, tokenizer/NLP code, `gate.py`, or any `~/vietneu_bench_frozen/*/key` path. No network calls were used. No commit or push was made.
