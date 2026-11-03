# Rebuttal evidence: Codex FAIL on pilot glue (#131)

Branch: research/hitl-pilot. No code modified. Commands run from the repo root.

## Verdicts

| Claim | Verdict |
|---|---|
| (a) reviewer.run output is {"videos": [...]}, so render_card misses flags | REFUTED |
| (b) e2e test cannot pass / assertion would fail | REFUTED |
| (c) research.hitl.history does not exist | REFUTED |
| (d) wrapped {"videos": [...]} review: silent or explicit? | CONFIRMED as to behaviour (explicit error, not silent). Not a FAIL. |

## (a) Output shape and flag rendering

Shape of the on-disk output of reviewer.run:
```
$ python3 -c "import json; d=json.load(open('research/hitl/pilot131/review.json')); print(type(d).__name__, len(d))"
list 6
```
Per-video status and flags (from review.json):
```
bud_vessantara_v1 ok None [('c1', ['unsupported']), ('c2', ['unsupported']), ('c3', ['unsupported', 'misleading_implication'])]
```
reviewer.py run() (lines ~ "returned = parsed.get("videos") if isinstance(parsed, dict) else parsed") unwraps the {"videos": ...} envelope the model returns, then writes `outputs` (a list) via json.dumps. The {"videos"} wrapper exists only in the model reply and in the INPUT_JSON sent to the model, not in review.json.

Render with the real review.json:
```
$ python3 -m research.hitl.card render research/hitl/pilot131/candidates/bud_vessantara.json --review research/hitl/pilot131/review.json --out <scratchpad>/x_card.html
exit=0
Trạng thái review: ok —
misleading_implication   (1)
unsupported              (3)
```
All flag codes present in review.json for bud_vessantara_v1 (unsupported, misleading_implication) appear in the card. render_card also accepts a list and selects the row by video_id (card.py ~line 112-117), so the list output is read correctly.

## (d) Wrapped input (Codex nit)

Same entry wrapped as {"videos": [entry]} and rendered:
```
exit=0
Trạng thái review: review_format_unrecognized — review.json không đúng định dạng reviewer v2 (thiếu review_status hoặc candidates)
review_result_missing   (3)
```
Behaviour: explicit format error in the card header, and each candidate is marked review_result_missing. No flags from another video are shown and nothing is silently rendered as "no flags". Codex's description of this path is accurate, but it is a robustness point, not a bug that hides flags.

## (b) Integration test

```
$ python3 -m pytest -q research/hitl/test_integration.py -v
platform darwin -- Python 3.10.1, pytest-8.4.1
collected 1 item
research/hitl/test_integration.py .   [100%]
1 passed in 0.08s
```
The test's replay uses a {"videos": [...]} envelope, which run() unwraps (correct, as above), so the modality_dropped flag reaches the card and the `"modality_dropped" in html` assertion holds. The Codex claim that the assertion "would fail" is not reproduced.

Note (not a rebuttal point): the final assertion `hist["n"] == 10 or len(hist["items"]) == 3` is weak. It passes, but it is not a strict check.

## (c) history module

```
$ python3 -c "import research.hitl.history.history as h; print(h.__file__)"
.../research/hitl/history/history.py
$ python3 -c "import research.hitl.history as h; print(h.__file__)"
.../research/hitl/history/__init__.py
```
research/hitl/history/ is a package containing history.py, __init__.py, and test_history.py. test_integration.py imports `from research.hitl.history import history`, which resolves to the submodule. Codex's claim that it does not exist is wrong.

## Also checked
- Store fixture: research/fact_store/pilot/stores_fixed/vsd_fansipan.json exists. The integration test passes, so reviewer.run read the store and verification files without error.
- Untracked files in the repo (research/hitl/pilot131/indep/*.jsonl and *.input.json) were already present before this check. Not touched.
