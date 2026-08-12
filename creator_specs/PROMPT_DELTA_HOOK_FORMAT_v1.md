# Prompt Delta — Hook Format v1.8 (revised per Codex rounds 1-8) — New hook strategy "Gương soi hành vi" (Behavioral Mirror Hook)

**Status: Codex-APPROVED (round 9, 2026-07-30) after 9 review rounds (1 BLOCKING round 1; sweep/wording rounds 2-4; withdrawal rounds 5-6; grounding blocker round 7; metadata rounds 8-9, 0 findings round 9). Nothing below has been applied to any file — awaiting your explicit approval before implementation, same as `PROMPT_DELTA_v1.md`'s Deltas 1-9 and `PROMPT_DELTA_RETENTION_v1.md`.**

**Round-8 fixes (this revision), summary:** Codex round 8 confirmed the round-7 blocker fix (example rewrite + "(0)" guardrail + C.2b judge-prompt addition) was applied correctly and verified against real code (Xử Nữ's `keyword` at `western_zodiac_short_generator.py:35`, facts dict at line 113), and found no CRITICAL/HIGH issues — only metadata/description staleness left over from the round-7 edit: (1) the `**Version:**` metadata field still said `1.6` while the document title already said `v1.7` — fixed, now `1.7`→`1.8` consistently everywhere in this revision; (2) Strategy D's `**Mechanism**` description still said the behavior/situation is one "the viewer may currently be in," a present-moment framing that contradicts both the "(0)" guardrail (behavior must come from `keyword`, not the instant) and the exclusion criterion 3 lines below it banning real-time claims — reworded to "a general behavioral tendency grounded directly in the subject's own facts/keyword... not a claim about the viewer's present moment, a single instant, or anything the facts don't already establish as a standing trait"; (3) the "safe alternatives" line still listed 3 patterns ("người ta thường...", neutral observation, hypothetical framing) as if all 3 were demonstrated in worked examples below, but 2 of those belonged to the now-withdrawn `zodiac_short_generator.py`/`educational_short_generator.py` examples — reworded to name only the 1 pattern the sole surviving pilot example actually uses, with an explicit note that the other 2 were only ever grounded by the withdrawn generators; (4) the retention-compatibility check still said the worked example was "14 words," stale from an earlier example wording — corrected to 10 words (whitespace count of the current example, matching the round-7 fix's own claim elsewhere in the document); (5) the round-7 summary's own citation of the `date_range`-construction line said `western_zodiac_short_generator.py:112`, off by one from the real line (113, confirmed by Codex reading the file directly) — corrected.

**Round-7 fixes (this revision), summary:** Codex round 7 found 1 blocker and 2 non-blocking issues, all now fixed. **Blocker:** even the sole remaining pilot's (`western_zodiac_short_generator.py`) Strategy D worked example — `"Người cung này thường để ý chi tiết nhỏ mà người khác lướt qua."` — still contained an ungrounded clause: "mà người khác lướt qua" is a claim about OTHER people's behavior, unsupported by the real facts (`sign_name`/`date_range`/`element`/`keyword`), even though "thường để ý chi tiết nhỏ" is legitimately derived from Xử Nữ's `keyword`="tỉ mỉ, cầu toàn, phân tích sắc bén". Fixed by rewriting the example to `"Người cung này thường để ý từng chi tiết nhỏ."` (10 words, directly traceable to `keyword`, no comparison to others) and adding a new "(0)" guardrail bullet to C.1's `QUY TẮC BẮT BUỘC` requiring the behavioral tendency be derived DIRECTLY from the sign's own `keyword`, with no new behavior invented and no comparison to other people/groups. Per Codex's explicit suggestion, C.2b's judge-prompt text now also carries the same requirement operationally: a new sentence requires the judge to verify D's behavioral claim is directly grounded in `keyword`, rejecting D if it adds behavior or comparisons not derivable from the background data. **Non-blocking #1:** C.2's header still referenced the deleted Delta B ("same gap as B.2's finding") — reworded to "the incomplete-sweep gap identified in round 2," which describes the actual round-2 finding without citing a section that no longer exists. **Non-blocking #2:** C.2b's fact-list description said "facts CHỈ có tên cung/element/keyword," missing `date_range` (which the real call site at `western_zodiac_short_generator.py:113` also constructs) — reworded to "facts không có dữ liệu riêng về người xem, chỉ có sign_name/date_range/element/keyword của cung," accurate to the real fact dict without implying a shorter list than what's actually there. Also fixed a stale "byte-for-byte identical to today's behavior" claim at ~line 112 that contradicted the already-corrected, more precise claim elsewhere in the same document — reworded to "equivalent accept/reject decision."

**Round-6 fixes (this revision), summary — SCOPE NARROWED AGAIN, to a single pilot generator:** Codex round 6 confirmed the round-5 withdrawal of `educational_short_generator.py` was executed cleanly (Delta D fully removed, no stray references in current content), but found the *same class* of problem in the remaining `zodiac_short_generator.py` example: "Không phải ai cũng để ý hôm nay là ngày con giáp gì" is itself an ungrounded attention/behavior claim — `zodiac_short_generator.py`'s real facts (`day_can_chi`, `hop_animals`, `ky_animal`) contain no data about viewer attention or behavior at all, milder than educational's examples but the same underlying issue. Also found: the judge prompt never operationalized strategy D's exclusion criteria (the judge doesn't see the generate-prompt's guardrail text, so nothing in `_JUDGE_PROMPT` actually checked for outcome/history/real-time/emotion violations), a stale "3 functions" claim in A.2's header (the diff touches 5 functions, 4 literal references in 2 of them), and a leftover `educational_short_generator.py` mention in the Scope line. Fixed by: (1) withdrawing `zodiac_short_generator.py` from the pilot too, leaving `western_zodiac_short_generator.py` as the **sole** pilot generator — its facts (per-sign personality/keyword data) are the only ones of the 3 originally tried that actually describe traits/tendencies, which is what makes a "behavioral mirror" claim grounded rather than invented; (2) adding a new sub-delta (C.2b) that inserts an explicit D-specific check into `_JUDGE_PROMPT`'s own `BƯỚC 1`, so the exclusion criteria are actually judge-enforced, not just generator-side guidance; (3) rewriting A.2's header to accurately describe 5 functions/4 references; (4) removing the stale Scope reference and documenting the generalizable finding (strategy D is category-dependent — safe only where facts already describe traits/tendencies, not proven category-agnostic) in "Not proposed" for whoever considers rollout later.

**Round-5 fixes, summary (carried forward from v1.5):** Codex round 5 caught a real structural self-contradiction in round-4's fix: telling `educational_short_generator.py` to "skip D, use A/B/C instead" when the excerpt doesn't support it is literally impossible to satisfy at the same time as the prompt's own "Viết 4 PHƯƠNG ÁN" / "4 chiến lược hook bắt buộc" instructions and the JSON schema requiring all of A/B/C/D — `_validate_candidates(..., _PILOT_STRATEGIES_ABCD)` rejects any result missing D, so a generator literally cannot comply with both "always submit exactly A/B/C/D" and "sometimes skip D." Separately, even the illustrative example given for the "excerpt supports it" branch didn't match its own stated condition (an excerpt showing a *confusion* pattern doesn't support a claim about *skimming/inattention* — two different behavioral claims), and the judge prompt had no explicit instruction to check the new eligibility condition at all.

After 5 rounds spent specifically on `educational_short_generator.py`'s example (rounds 1-5 each found a new problem with it — CR-1-adjacent outcome claims, a 19-word `"Nếu..."` opener, personal-history claims, ungrounded universal-behavior claims, and now a schema-incompatible conditional), the honest conclusion is that this generator's fact model — an excerpt about a *topic*, with no data about reader/viewer behavior at all — does not safely support a "declarative statement about the viewer's/people's behavior" mechanism without either fabricating a claim the excerpt can't support, or creating a structural contradiction with the rigid candidate-count schema. **`educational_short_generator.py` is withdrawn from this delta's pilot scope entirely** rather than continuing to patch a fit that doesn't work — see "Not proposed" for the full reasoning. **The pilot is now 2 generators, not 3**: `zodiac_short_generator.py` and `western_zodiac_short_generator.py`, both of which passed rounds 1-4 without a single finding against their own worked examples (only the shared engine and the withdrawn generator needed fixes). All references to a 3rd pilot generator, Delta D, and 3-generator category coverage are removed/updated accordingly below.

**Round-4 fixes, summary (carried forward from v1.4, superseded by the withdrawal above but kept for the record):** Codex round 4 confirmed 2 of the 3 round-3 fixes (guardrail's 6-item list, pilot criteria wording) and confirmed nothing else regressed, but found the educational example still unsafe on a subtler point: switching "Bạn" → "Người ta" (round-3's fix) correctly removed the specific-viewer claim, but the underlying behavioral-tendency assertion itself ("người ta thường lướt qua...") is still not grounded in the excerpt — it's a general claim the excerpt may or may not support, which still conflicts with "CHỈ được dùng thông tin có trong đoạn trích nguồn." Fixed by making strategy D **conditional on excerpt support**, mirroring the same conditional structure this file's own Strategy B already uses ("nếu đoạn trích có nội dung sửa hiểu lầm phổ biến; nếu không, dùng..."): D may only be selected when the excerpt itself shows evidence the concept is commonly glossed-over/misunderstood; otherwise the generator must pick A/B/C instead. This is a real constraint, not a formality — it makes the behavioral claim excerpt-grounded rather than a standing assumption.

**Round-3 fixes, summary (carried forward from v1.3):** Codex round 3 confirmed the "3 phương án" sweep was now complete across all 10 occurrences, the zodiac/western examples were safe, and the `frozenset` conversion had no side effects — but found 3 remaining issues: (1) the `educational_short_generator.py` guardrail listed competence-judgment as a 4th prohibited claim type but never explicitly named "outcome/result," which is a distinct category from competence — fixed, now 6 enumerated prohibitions including outcome. (2) the `educational_short_generator.py` example itself ("Bạn thường lướt qua...") still directly asserted a behavior of the specific viewer ("Bạn"), unsupported by the excerpt and self-contradicting its own guardrail — fixed by switching to an impersonal subject ("Người ta," matching this file's own existing Strategy B pattern), with an explicit disclosed note that this generator, unlike the other 2 pilots, has no viewer-behavior data at all in its facts, so a literal 2nd-person mirror isn't safely achievable here. (3) the pilot criterion "D's fact-check pass rate" assumed `_validate_verdict()` requires every strategy letter to appear in the `fact_check` dict — verified false: the validator only checks the winner's entry, so a verdict can validly omit non-winning letters entirely — corrected to disclose this is only as complete as what the model happens to include, not validator-guaranteed, without proposing a new validator requirement (that would be additional scope affecting the 7 untouched generators too). Also fixed a stale footer still reading "round 2."

**Round-2 fixes, summary (carried forward from v1.2):** Codex round 2 confirmed the A.1/A.2 architecture fix and the 3 rewritten examples' core direction were sound, but found: (1) an incomplete sweep — `_JUDGE_PROMPT`'s `"=== 3 PHƯƠNG ÁN ==="` heading in all 3 generators, plus `western_zodiac_short_generator.py`'s and `educational_short_generator.py`'s judge-prompt intro lines ("Chấm 3 phương án dưới đây"), were never updated to "4" even though v1.1 fixed the generate-prompt side — fixed, every remaining "3 phương án"/"3 PHƯƠNG ÁN" occurrence in all 3 pilot generators' `_JUDGE_PROMPT`s is now included in the diffs below. (2) each generator's new exclusion bullet only covered the ONE claim-type relevant to its own worked example, not the full 4-category list (outcome/history/real-time/emotion) — since the "Proposed new strategy" section's general principle is spec-document context, not actually injected into the runtime prompt, each generator now carries its own complete 4-category exclusion list. (3) the `educational_short_generator.py` example was still unsafe on 3 independent grounds: 19 words (violates its own "<15 words" claim), opens with a long `"Nếu..."` conditional clause (exactly the pattern `PROMPT_DELTA_RETENTION_v1.md`'s rule (a) already singles out as bad), and still implicitly judged the viewer's competence ("chưa chắc bạn trả lời được trọn vẹn") — rewritten to a short, non-judgmental, direct-address opener grounded in something true by construction (the viewer is, in that instant, about to hear the content) rather than a claim about their past or ability. (4) the western_zodiac example's exact wording ("thường để ý") didn't literally match its own instruction ("dùng ĐÚNG khung 'thường có xu hướng...'") — fixed by loosening the instruction to name the accepted marker set explicitly instead of demanding one literal phrase. (5) the pilot-criteria section asked for "hook_score distribution D vs A/B/C," which isn't derivable from the judge's actual return schema (`hook_score` is reported once, for the winner only — no per-candidate score exists) — removed that specific unmeasurable sub-claim, kept "D's fact-check pass rate" (which genuinely is measurable, since `fact_check` already reports PASS/FAIL per letter) and "D's win rate," and made explicit that token/latency must be measured externally (the engine doesn't collect this itself). (6) softened "byte-for-byte identical validation behavior" — true for accept/reject *decisions*, but the error-message string format changes (now interpolates `sorted(valid_strategies)` instead of a hardcoded "A/B/C" literal) even for the 7 untouched generators. (7) converted `_VALID_STRATEGIES` itself from a mutable `set` to a `frozenset` (same 3 elements, not a behavior change) so the new parameters' `frozenset[str]` type annotation is actually accurate, closing a real type mismatch Codex flagged. (8) added a "Comment hygiene" note listing the specific stale A/B/C-hardcoded comments in `short_judge_panel_engine.py` (lines ~101-107, 136, 252) that will read as inaccurate once a pilot generator can validly submit 4 candidates, without proposing to rewrite comment prose in this delta's diff (flagged for the implementer, not spec'd word-for-word here).

**Round-1 fixes, summary (carried forward from v1.1):** Codex round 1 returned NEEDS_REVISION with 1 blocking architecture bug + several real content-safety and completeness findings, all re-verified before fixing: (1) BLOCKING — A.1 (`_VALID_STRATEGIES = {"A","B","C","D"}`) and A.2 (`valid_strategies: set[str] = _VALID_STRATEGIES` as a *default*) directly contradicted each other — Python evaluates default arguments at function-definition time, so if A.1 shipped, A.2's default would silently become A/B/C/D too, breaking all 7 untouched generators. The claim "default preserves current behavior" was flatly wrong. Fixed: **A.1 is withdrawn entirely** — `_VALID_STRATEGIES` stays `{"A","B","C"}`, untouched. A new, separate constant `_PILOT_STRATEGIES_ABCD` is introduced instead, and only the 3 pilot generators pass it explicitly. (2) Found and fixed: every occurrence of "3 phương án"/"CẢ 3"/"=== 3 PHƯƠNG ÁN ===" in the 3 pilot generators' prompts, which would otherwise contradict the new 4-candidate JSON schema. (3) Found and fixed: the *shared* retention block (`_RETENTION_RULES_BLOCK`/`_RETENTION_CHECK_BLOCK`, used by all 10 generators) also hardcodes "CẢ 3 PHƯƠNG ÁN" — this text is shared, so it cannot say "4" without breaking the 7 non-pilot generators; reworded to be count-neutral for both this delta and the already-approved (not-yet-applied) `PROMPT_DELTA_RETENTION_v1.md`. (4) HIGH content-safety finding, re-verified as real: the `zodiac_short_generator.py` worked example ("Hôm nay bạn tự nhiên thấy mọi việc trôi chảy hơn bình thường") implicitly asserts a favorable outcome the Tam Hợp/xung data does not establish — a real `CR-1`-class violation risk. Rewritten to a neutral, outcome-free observation. The `western_zodiac_short_generator.py` example's "Ngay lúc này, có lẽ..." wording undercut the "confident declarative" premise and made an unfounded real-time claim (Barnum-statement-adjacent) — rewritten to match the category's own already-approved hedge pattern ("người cung này thường có xu hướng..."). The `educational_short_generator.py` example ("Bạn từng nghe qua...") asserted the viewer's personal history, which no excerpt can confirm — rewritten to a hypothetical framing instead. A new explicit exclusion criterion was added to all 3 generators' `QUY TẮC BẮT BUỘC`. (5) Softened the "not a multiplicative cost" claim to acknowledge real (if unmeasured) token/latency impact, and added a pilot acceptance-criteria section per Codex's request, gating any future rollout to the other 7 generators on actual pilot data rather than "validated in practice" left undefined. (6) Narrowed the mechanism-distinctness claim — acknowledged real overlap with the existing "concrete image/scenario" mechanism rather than claiming full separation.

- **Version:** 1.8
- **Source:** fills a gap explicitly disclosed in `PRODUCTION_CREATOR_PROMPT_v1.md` §6: *"Hook, Story structure, Pacing, Typography, CTA (all categories): no approved finding exists in the Creator Specification for these areas."* Requested by user as audit point #7 ("new hook content format"), scoped separately from point #3 (mid-script retention, already Codex-approved as `PROMPT_DELTA_RETENTION_v1.md`) and point #8 (FS hedge trimming, Codex-approved as `PROMPT_DELTA_FS_HEDGE_v1.md`).
- **Scope:** proposes 1 new hook strategy ("D"), added ALONGSIDE the existing 3 (A/B/C) in one generator's own hook-strategy menu — not a replacement. Targets **`western_zodiac_short_generator.py`** (Category `CREATIVE_ASTROLOGY`) as the sole proof-of-concept pilot, plus the shared engine change needed for ANY generator to use a 4th strategy letter without affecting the other 9. Two other candidate generators were tried and withdrawn — see "Not proposed" for the full reasoning. Full rollout to the remaining 9 generators is explicitly NOT included, and is now gated on real pilot data — see "Pilot acceptance criteria."
- **Status:** Codex-APPROVED (round 9), not yet applied — awaiting your explicit go-ahead.

**Purpose:** record proposed prompt/code changes as deltas against real, current file content — not a full rewrite. Same format as `PROMPT_DELTA_v1.md`/`PROMPT_DELTA_RETENTION_v1.md`.

---

## Survey of existing hook strategies (done before proposing anything new, to avoid duplicating an existing mechanism)

Read every `_GENERATE_CANDIDATES_PROMPT`'s "chiến lược hook bắt buộc" list across all 10 current generators. Every strategy in use falls into one of 4 mechanisms:

1. **Name-it-immediately** (`GỌI TÊN CON GIÁP NGAY`, `GỌI TÊN CUNG NGAY`, `GỌI TÊN THẦN NGAY`, `GỌI TÊN QUẺ NGAY`) — open with the subject itself.
2. **Question** (`CÂU HỎI TRỰC TIẾP`, `CÂU HỎI GÂY TÒ MÒ`, `CÂU HỎI ĐỒNG CẢM`, `CÂU HỎI TRIẾT LÝ`) — open with a question to the viewer.
3. **Warning/paradox/contrast** (`CẢNH BÁO...TRƯỚC`, `CẢNH BÁO/NGHỊCH LÝ`, `NGHỊCH LÝ THÚ VỊ`, `MYTH-BUST`) — open by contradicting an assumption.
4. **Concrete image/scenario** (`HÌNH ẢNH CỤ THỂ`, `HÌNH ẢNH ẨN DỤ`, `VÀO THẲNG TÌNH HUỐNG`, `"NẾU...THÌ SAO"`) — open with a specific image or situation.

**Gap identified, claim narrowed per Codex round-1 finding #3:** the proposed strategy D is **not** a fully separate 5th mechanism — it has real overlap with mechanism 4 (both open with a situation rather than naming the topic or asking a question). The genuine, narrower distinction is: (a) it is a **declarative statement about the viewer's own state**, not a scenario/image from the content's point of view, and (b) it uses a specific **speech act** (assertion, not question) that mechanism 2 doesn't. This is a controlled variant within an existing family, not an entirely new category — described honestly here rather than oversold, matching Codex's round-1 correction.

## Proposed new strategy: "D. GƯƠNG SOI HÀNH VI" (Behavioral Mirror Hook)

**Mechanism (narrowed per Codex round-8 finding — the wording below previously described a present-moment situation, which contradicted the exclusion criterion 3 lines down and the sole surviving pilot example):** open with a **declarative statement, not a question**, describing a **general behavioral tendency grounded directly in the subject's own facts/keyword** — not a claim about the viewer's present moment, a single instant, or anything the facts don't already establish as a standing trait — without naming the topic yet, and **without asserting any outcome, personal history, present-moment fact, or emotional state that the generator's own facts/excerpt cannot support.** The topic connects in the sentence(s) immediately after.

**New explicit exclusion criterion (added per Codex round-1 finding #3 — the guardrail that was missing and let all 3 original examples slip through):** strategy D must **NOT** assert any of the following unless the generator's facts/excerpt directly support it:
- a specific outcome or result for the viewer (fortune, luck, success — this is a `CR-1`-class violation, same rule already governing every other strategy);
- the viewer's personal history ("bạn từng...", "bạn đã từng nghe...");
- a real-time claim about what the viewer is doing "right now" ("ngay lúc này bạn đang...");
- a specific emotional state as established fact.
**Safe pattern used in the sole remaining worked example (corrected per Codex round-8 finding — this line previously listed 3 alternatives, 2 of which belonged to the now-withdrawn `zodiac_short_generator.py`/`educational_short_generator.py` examples and are no longer demonstrated below):** a **general behavioral tendency** ("người này thường...", matching the phrasing pattern already used and approved in `western_zodiac_short_generator.py`'s own `QUY TẮC BẮT BUỘC`), derived directly from the sign's `keyword` — not a neutral observation or hypothetical framing, since those were only ever grounded by the withdrawn generators' fact models.

**Guardrail, same as every other existing strategy:** must stay within the generator's own fact-check contract — this is a hook *mechanism*, not new license to add claims. The exclusion criterion above makes this concrete and checkable rather than a vague restatement.

**Retention-rule compatibility check (verified against the already-approved `PROMPT_DELTA_RETENTION_v1.md`, not assumed compatible):** rule (a) requires the hook sentence to land on the subject within ~12 words guideline / 20-word hard cap (`short_judge_panel_engine.py:56`, `HOOK_MAX_FIRST_SENTENCE_WORDS`). The worked example below (western zodiac) — **"Người cung này thường để ý từng chi tiết nhỏ."** — is 10 words by whitespace count (corrected per Codex round-8 finding; a prior revision said 14, stale from an earlier example wording), comfortably inside the existing cap.

---

## Delta A (primary, required for any generator to use strategy D) — `short_judge_panel_engine.py`

### A.1 — `_VALID_STRATEGIES` (line 23): same 3 elements, converted to `frozenset`; new pilot constant added

**Current text (verbatim):**
```
_VALID_STRATEGIES = {"A", "B", "C"}
```

**Proposed change (same 3 elements — NOT `{"A","B","C","D"}` — only the container type changes, plus a new, separate constant):**
```
_VALID_STRATEGIES = frozenset({"A", "B", "C"})
_PILOT_STRATEGIES_ABCD = frozenset({"A", "B", "C", "D"})  # dùng riêng cho 1 generator thí điểm strategy D -- KHÔNG đụng _VALID_STRATEGIES, 9 generator còn lại không bị ảnh hưởng.
```
**Correction from v1.0 (Codex round-1 finding, blocking):** v1.0 proposed changing `_VALID_STRATEGIES`'s *value* to `{"A","B","C","D"}`, which — combined with v1.0's own A.2 default-parameter design (Python defaults are bound at function-definition time) — would have silently forced all untouched generators to require a 4th candidate too. **Withdrawn.** `_VALID_STRATEGIES`'s value (`{"A","B","C"}`) is not modified by this delta at all — only its container type, `set` → `frozenset`, added per Codex round-2 (see A.2 below for why: the new `valid_strategies` parameters are typed `frozenset[str]`, and a mutable `set` default wouldn't actually match that type). A separate, explicitly-named constant (`_PILOT_STRATEGIES_ABCD`) is used only by the 1 pilot generator.

### A.2 — Replace the exact 4 `_VALID_STRATEGIES` references in the 2 validator functions, and thread a `valid_strategies` parameter through all 5 functions in the call chain (header corrected per Codex round-6 finding #3 — v1.5 said "3 functions," but the diff actually touches `_validate_candidates`, `_validate_verdict`, `generate_candidates`, `judge_candidates`, and `generate_verified_script` — 5 functions, of which only the first 2 contain the 4 literal `_VALID_STRATEGIES` references; the other 3 just thread the parameter through)

**Current text (verbatim):**
```python
# line 92-112
def _validate_candidates(result) -> list[dict]:
    ...
    strategies = [c["strategy"] for c in candidates]
    if set(strategies) != _VALID_STRATEGIES or len(strategies) != len(_VALID_STRATEGIES):
        raise ContentSeoError(f"agy trả về strategy không đúng bộ A/B/C duy nhất (nhận: {strategies}): {result!r}"[:500])
    return candidates


def _validate_verdict(verdict, candidates: list[dict]) -> dict:
    ...
    winner = verdict.get("winner")
    if winner not in _VALID_STRATEGIES and winner != "NONE":
        raise ContentSeoError(f"Codex trả về 'winner' không hợp lệ (phải là A/B/C/NONE): {winner!r}")
    if winner in _VALID_STRATEGIES:
        ...

# line 199-215
def generate_candidates(facts: dict, generate_prompt_template: str, prior_feedback: str | None = None) -> list[dict]:
    ...
    result = _extract_json(_run_agy(prompt))
    return _validate_candidates(result)


def judge_candidates(facts: dict, candidates: list[dict], judge_prompt_template: str) -> dict:
    ...
    verdict = _extract_json(_run_codex(prompt))
    return _validate_verdict(verdict, candidates)

# line 218-221
def generate_verified_script(
    facts: dict, generate_prompt_template: str, judge_prompt_template: str,
    max_rounds: int = MAX_ITERATIONS, hook_pass_threshold: int = HOOK_PASS_THRESHOLD,
) -> dict:
```

**Proposed change (every reference to the module-level constant becomes a parameter with the ORIGINAL constant as default, so omitting the parameter gives an equivalent accept/reject decision to today's behavior — corrected per Codex round-7 finding: this sentence still said "byte-for-byte identical," contradicting the more accurate correction already made further below at "Verified this closes the round-1 conflict"):**
```python
def _validate_candidates(result, valid_strategies: frozenset[str] = _VALID_STRATEGIES) -> list[dict]:
    ...
    strategies = [c["strategy"] for c in candidates]
    if set(strategies) != valid_strategies or len(strategies) != len(valid_strategies):
        raise ContentSeoError(f"agy trả về strategy không đúng bộ {sorted(valid_strategies)} duy nhất (nhận: {strategies}): {result!r}"[:500])
    return candidates


def _validate_verdict(verdict, candidates: list[dict], valid_strategies: frozenset[str] = _VALID_STRATEGIES) -> dict:
    ...
    winner = verdict.get("winner")
    if winner not in valid_strategies and winner != "NONE":
        raise ContentSeoError(f"Codex trả về 'winner' không hợp lệ (phải là {'/'.join(sorted(valid_strategies))}/NONE): {winner!r}")
    if winner in valid_strategies:
        ...

def generate_candidates(facts: dict, generate_prompt_template: str, prior_feedback: str | None = None,
                         valid_strategies: frozenset[str] = _VALID_STRATEGIES) -> list[dict]:
    ...
    result = _extract_json(_run_agy(prompt))
    return _validate_candidates(result, valid_strategies=valid_strategies)


def judge_candidates(facts: dict, candidates: list[dict], judge_prompt_template: str,
                      valid_strategies: frozenset[str] = _VALID_STRATEGIES) -> dict:
    ...
    verdict = _extract_json(_run_codex(prompt))
    return _validate_verdict(verdict, candidates, valid_strategies=valid_strategies)


def generate_verified_script(
    facts: dict, generate_prompt_template: str, judge_prompt_template: str,
    max_rounds: int = MAX_ITERATIONS, hook_pass_threshold: int = HOOK_PASS_THRESHOLD,
    valid_strategies: frozenset[str] = _VALID_STRATEGIES,
) -> dict:
    ...  # truyền valid_strategies xuống CẢ 2 lệnh gọi generate_candidates()/judge_candidates() bên trong vòng lặp
```
**`frozenset` used instead of a mutable `set` default per Codex round-1 note** — not a live bug today (nothing mutates the default), but the wrong type for a new API's default value.

**Verified this closes the round-1 conflict:** since `_VALID_STRATEGIES`'s *value* (line 23) is never modified (A.1 above), every default value in this diff still resolves to the same 3 elements at function-definition time — the untouched generators, which call `generate_verified_script()` without the new keyword argument, get an **equivalent accept/reject decision** to today. **Claim corrected per Codex round-2 finding #7:** "byte-for-byte identical" (v1.1's wording) was inaccurate — the error-message strings inside `_validate_candidates()`/`_validate_verdict()` change from a hardcoded `"A/B/C"` literal to an interpolated `sorted(valid_strategies)` representation (see A.2 diff above), so the exact string an exception carries is not byte-identical even for the untouched generators, though which inputs are accepted vs. rejected is unchanged. Only the 1 pilot generator (Delta C below) explicitly passes `valid_strategies=short_judge_panel_engine._PILOT_STRATEGIES_ABCD`.

### A.4 — Comment hygiene (flagged, not spec'd word-for-word — Codex round-2 finding #6)

`short_judge_panel_engine.py` has several comments that hardcode "A/B/C" or "3 phương án" as if that were the only possible strategy set (e.g. lines ~101-107's `"BẮT BUỘC đúng đủ 3 strategy A/B/C"`, line ~136's `"candidates đã ép đúng đủ A/B/C"`, line ~252's `"Cả 3 phương án đều fail fact-check"`). Once a pilot generator can validly submit 4 candidates, these comments become locally inaccurate (still true for the untouched generators, misleading for the 1 pilot one). **Flagged for the implementer to reword to count-neutral/`valid_strategies`-aware language when this delta is actually applied** — not spec'd as an exact diff here, since the comment prose itself carries useful historical bug-fix context (the "BUG THẬT phát hiện qua Codex CLI review" narrative) that shouldn't be mechanically find-replaced without care.

### A.3 — Shared retention block: count-neutral wording (Codex round-1 finding #2 — this text is shared across all 10 generators, so it cannot hardcode "3" or "4")

**Current text (verbatim, line 41):**
```
QUY TẮC NHỊP ĐỘ/GIỮ CHÂN NGƯỜI XEM (retention, ÁP DỤNG THÊM CHO CẢ 3 PHƯƠNG ÁN, ngoài mọi quy tắc riêng ở trên):
```

**Proposed change (count-neutral, correct for both 3-candidate and 4-candidate generators, applies regardless of whether this delta or `PROMPT_DELTA_RETENTION_v1.md` ships first):**
```
QUY TẮC NHỊP ĐỘ/GIỮ CHÂN NGƯỜI XEM (retention, ÁP DỤNG THÊM CHO TẤT CẢ CÁC PHƯƠNG ÁN, ngoài mọi quy tắc riêng ở trên):
```
Same fix applies to `_RETENTION_CHECK_BLOCK`'s opening line (`"với MỖI phương án còn lại sau fact-check"` — already count-neutral, uses "MỖI" not a number, verified no change needed there).

---

## Delta C — `western_zodiac_short_generator.py` (Category `CREATIVE_ASTROLOGY`) — the sole remaining pilot generator (round 6)

### C.1 — `_GENERATE_CANDIDATES_PROMPT` (lines 51, 55-58, 67)

**Current text (verbatim):**
```
Bạn là biên tập viên Short-form chiêm tinh phương Tây tiếng Việt, viết cho khán giả trẻ yêu thích 12 cung hoàng đạo. Viết 3 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) về TÍNH CÁCH ĐẶC TRƯNG của cung hoàng đạo sau, dựa trên dữ liệu:

...

3 chiến lược hook bắt buộc -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. GỌI TÊN CUNG NGAY: mở bằng "Cung [tên]..." kèm 1 đặc điểm nổi bật nhất, tạo cảm giác "đúng là mình" cho người thuộc cung đó.
B. CÂU HỎI ĐỒNG CẢM: mở bằng câu hỏi mà người thuộc cung này thường tự hỏi/hay gặp (vd với Xử Nữ: "Bạn có hay để ý từng chi tiết nhỏ mà người khác bỏ qua không?").
C. NGHỊCH LÝ THÚ VỊ: mở bằng 1 nghịch lý/mặt ít ai để ý của cung này.

QUY TẮC BẮT BUỘC cho CẢ 3 phương án (tiêu chuẩn Category 4 -- xem chi tiết):
- KHÔNG khẳng định chắc chắn điều sẽ xảy ra (không nói "bạn sẽ...", chỉ nói "người cung này thường có xu hướng...").
```
```
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}]}}
```

**Proposed changes (count wording + new strategy, reworded per Codex round-1 finding #3 to drop "Ngay lúc này"/"có lẽ" and reuse the category's own already-approved "thường có xu hướng" hedge pattern instead of inventing a new one):**
```
Bạn là biên tập viên Short-form chiêm tinh phương Tây tiếng Việt, viết cho khán giả trẻ yêu thích 12 cung hoàng đạo. Viết 4 PHƯƠNG ÁN kịch bản Short (~20-30 giây đọc, 4-6 câu) về TÍNH CÁCH ĐẶC TRƯNG của cung hoàng đạo sau, dựa trên dữ liệu:

...

4 chiến lược hook bắt buộc -- HOOK PHẢI RƠI TRONG CÂU ĐẦU TIÊN:
A. GỌI TÊN CUNG NGAY: mở bằng "Cung [tên]..." kèm 1 đặc điểm nổi bật nhất, tạo cảm giác "đúng là mình" cho người thuộc cung đó.
B. CÂU HỎI ĐỒNG CẢM: mở bằng câu hỏi mà người thuộc cung này thường tự hỏi/hay gặp (vd với Xử Nữ: "Bạn có hay để ý từng chi tiết nhỏ mà người khác bỏ qua không?").
C. NGHỊCH LÝ THÚ VỊ: mở bằng 1 nghịch lý/mặt ít ai để ý của cung này.
D. GƯƠNG SOI HÀNH VI: mở bằng 1 CÂU KHẲNG ĐỊNH (không phải câu hỏi, KHÁC Strategy B ở chỗ này) mô tả XU HƯỚNG HÀNH VI chung (không phải khoảnh khắc "ngay lúc này") của người thuộc cung này, PHẢI suy ra TRỰC TIẾP từ `keyword` của cung trong dữ liệu nền (không thêm hành vi/so sánh nào ngoài những gì `keyword` gợi ý), dùng 1 trong các marker xu hướng đã quy định ở QUY TẮC BẮT BUỘC bên dưới ("thường"/"hay"/"có xu hướng") -- KHÔNG bắt buộc đúng 1 cụm cố định, miễn thuộc nhóm marker đó (vd với Xử Nữ, `keyword`="tỉ mỉ, cầu toàn, phân tích sắc bén": "Người cung này thường để ý từng chi tiết nhỏ." -- **LƯU Ý: KHÔNG thêm vế so sánh như "mà người khác lướt qua/bỏ qua" — đó là khẳng định về hành vi của NGƯỜI KHÁC, không suy ra được từ `keyword` (vốn chỉ mô tả cung đang viết), là lỗi grounding cùng loại đã khiến zodiac/educational bị rút khỏi phạm vi, xem "Not proposed"**), rồi mới gọi tên cung.

QUY TẮC BẮT BUỘC cho CẢ 4 phương án (tiêu chuẩn Category 4 -- xem chi tiết):
- KHÔNG khẳng định chắc chắn điều sẽ xảy ra (không nói "bạn sẽ...", chỉ nói "người cung này thường có xu hướng...").
- RIÊNG PHƯƠNG ÁN D, câu mở đầu: (0) BẮT BUỘC xu hướng hành vi phải suy ra TRỰC TIẾP từ `keyword` của cung đang viết -- KHÔNG được thêm hành vi mới, KHÔNG được so sánh với người khác/nhóm khác (vd cấm "mà người khác lướt qua," "không giống ai," -- đây là claim về đối tượng KHÁC ngoài cung đang viết, `keyword` không xác nhận được); (1) PHẢI dùng 1 marker xu hướng hành vi chung ("thường"/"hay"/"có xu hướng" -- không bắt buộc đúng cụm "thường có xu hướng" nguyên văn, chỉ cần thuộc nhóm này), KHÔNG phải khoảnh khắc thời gian thực; (2) TUYỆT ĐỐI KHÔNG được viết "ngay lúc này bạn đang..." hay bất kỳ khẳng định thời điểm cụ thể nào về người xem (facts không biết người xem đang làm gì); (3) KHÔNG khẳng định lịch sử cá nhân của người xem (vd "bạn từng..."); (4) KHÔNG khẳng định 1 kết quả/cảm xúc cụ thể của người xem như sự thật đã xác lập -- chỉ mô tả xu hướng hành vi CHUNG của người thuộc cung này, không phải khẳng định riêng về người xem cụ thể.
```
```
{{"candidates": [{{"strategy": "A", "script": "..."}}, {{"strategy": "B", "script": "..."}}, {{"strategy": "C", "script": "..."}}, {{"strategy": "D", "script": "..."}}]}}
```

### C.2 — `_JUDGE_PROMPT` (lines 71, 76, 90 — **round-2 fix: lines 71/76 were missed in v1.1, added now, per the incomplete-sweep gap identified in round 2**)

**Current text (verbatim):**
```
Bạn là giám khảo chuyên gia short-form chiêm tinh/giải trí. Chấm 3 phương án dưới đây.

...

=== 3 PHƯƠNG ÁN ===
```
```
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}
```

**Proposed change:**
```
Bạn là giám khảo chuyên gia short-form chiêm tinh/giải trí. Chấm 4 phương án dưới đây.

...

=== 4 PHƯƠNG ÁN ===
```
```
{{"fact_check": {{"A": "PASS hoặc FAIL: lý do", "B": "PASS hoặc FAIL: lý do", "C": "PASS hoặc FAIL: lý do", "D": "PASS hoặc FAIL: lý do"}}, "winner": "A" hoặc "B" hoặc "C" hoặc "D" hoặc "NONE", "winner_script": "kịch bản đầy đủ kèm dấu **, rỗng nếu NONE", "hook_score": 1-10, "feedback": "vì sao chọn bản này"}}
```

### C.2b — `_JUDGE_PROMPT`'s `BƯỚC 1` (line 85) — new, added per Codex round-6 finding #1: the judge never sees `_GENERATE_CANDIDATES_PROMPT`'s guardrail text, so strategy D's exclusion criteria (marker requirement, no outcome/history/real-time/emotion claims) must be operationalized directly in the judge prompt's own fact-check step, not assumed inherited from the generation side.

**Current text (verbatim):**
```
BƯỚC 1 -- LOẠI TRỪ THEO TIÊU CHUẨN CATEGORY 4 Ở TRÊN: phương án nào SÁO RỖNG (đổi tên cung khác vẫn đúng y hệt), hoặc KHẲNG ĐỊNH CHẮC CHẮN tương lai ("bạn sẽ..."), hoặc dùng SAI element/tên cung trong dữ liệu nền → LOẠI.
```

**Proposed change (new sentence appended to the same step, not a new step):**
```
BƯỚC 1 -- LOẠI TRỪ THEO TIÊU CHUẨN CATEGORY 4 Ở TRÊN: phương án nào SÁO RỖNG (đổi tên cung khác vẫn đúng y hệt), hoặc KHẲNG ĐỊNH CHẮC CHẮN tương lai ("bạn sẽ..."), hoặc dùng SAI element/tên cung trong dữ liệu nền → LOẠI. RIÊNG PHƯƠNG ÁN D: kiểm tra thêm câu mở đầu có dùng marker xu hướng ("thường"/"hay"/"có xu hướng") không, có khẳng định kết quả/lịch sử cá nhân/thời điểm thực/cảm xúc cụ thể của người xem không (facts không có dữ liệu riêng về người xem, chỉ có sign_name/date_range/element/keyword của cung) -- vi phạm bất kỳ điểm nào → LOẠI D, không được chọn làm winner. Ngoài ra: xu hướng hành vi của D phải được bảo chứng trực tiếp bởi keyword của đúng cung đang xét; nếu thêm hành vi mới hoặc so sánh với người khác/nhóm khác mà không suy ra được trực tiếp từ keyword → LOẠI D.
```

### C.3 — Call site (`western_zodiac_short_generator.py:116`, verbatim: `result = generate_verified_script(facts, _GENERATE_CANDIDATES_PROMPT, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS)`)

**Proposed change:**
```
result = generate_verified_script(facts, _GENERATE_CANDIDATES_PROMPT, _JUDGE_PROMPT, max_rounds=MAX_ITERATIONS,
                                   valid_strategies=short_judge_panel_engine._PILOT_STRATEGIES_ABCD)
```
(requires `import short_judge_panel_engine` alongside the existing `from short_judge_panel_engine import generate_verified_script`, or exporting `_PILOT_STRATEGIES_ABCD` without the leading underscore — a naming detail to settle at implementation time, not a blocker for this delta.)

---

## Cost/tradeoff disclosure — softened per Codex round-1 finding #4

`generate_candidates()` and `judge_candidates()` are each already a SINGLE `_run_agy`/`_run_codex` call returning/evaluating ALL candidates in one JSON response (verified directly, `short_judge_panel_engine.py:199-215`) — adding a 4th candidate does **not** add extra API round-trips (still 1 generate call + 1 judge call per round). **Corrected claim:** going from 3 to 4 candidates is roughly a 33% increase in scripts generated and judged per call — this *does* increase output tokens, judge-input tokens, and likely latency per call, in a way not yet measured. "Modestly larger"/"small cost" (v1.0's wording) was an unmeasured, overly casual claim — replaced with: **no increase in round-trip count, but a real, unmeasured increase in per-call token usage and latency, to be measured during the pilot** (see below), not assumed negligible in advance.

## Pilot acceptance criteria (new section, added per Codex round-1 finding #5 — required before any rollout beyond the 1 pilot generator)

Before proposing rollout to the remaining 9 generators, the pilot on this 1 should report:
- **D's fact-check pass rate** (does strategy D survive `BƯỚC 1` fact-check as often as A/B/C, or does the new exclusion criterion cause it to fail disproportionately — a signal the mechanism is harder to execute safely)? **Corrected per Codex round-3 finding #3 — not guaranteed complete by the current validator.** Verified directly: `_validate_verdict()` (`short_judge_panel_engine.py:173-178`) only requires `fact_check` to be a dict and `fact_check[winner]` to start with `"PASS"` — it does **not** require every letter in `valid_strategies` to have an entry, so a verdict with `fact_check={"A": "PASS"}` alone (winner A, no B/C/D entries at all) still passes validation today, and would continue to after this delta. This means "D's fact-check pass rate" is **only as complete as whatever the model happens to include** in each verdict's `fact_check` dict — not something the validator guarantees. The pilot's own data collection must tally whatever `D` entries are actually present across runs (and separately track how often `D` is missing from `fact_check` entirely, since that's itself a signal), rather than assuming every verdict yields a usable D data point. **No validator change is proposed here** to force-require all 4 letters — that would be new scope beyond this delta (a stricter `_validate_verdict()` check affecting the untouched generators too, since `fact_check` completeness isn't currently `valid_strategies`-aware either) and is deferred, not silently assumed away.
- **D's win rate** (how often does the judge actually pick D as the best of 4 — near-zero would mean it's not pulling its weight despite the added cost)? Also directly readable from the existing `winner` field.
- **Corrected per Codex round-2 finding #5 — "hook_score distribution for D vs. A/B/C" is withdrawn as a pilot criterion.** Verified against the real schema: `hook_score` is reported exactly once per verdict, for the `winner` only (`_JUDGE_PROMPT`'s return JSON has a single top-level `"hook_score"` field, not one per candidate) — there is no per-candidate score to build a distribution from with the current schema. Extending the schema to score every candidate individually is a real option but is out of scope for this delta (would need its own validation/parsing changes to `_validate_verdict()`); not proposed here.
- **Measured token/latency delta** per generation round with 4 vs. 3 candidates — **clarified per Codex round-2 finding #5:** `short_judge_panel_engine.py` does not itself collect token/latency telemetry today; this must come from an external measurement (timing the `_run_agy`/`_run_codex` calls, or reading provider-side usage stats) during the pilot, not from anything the engine already logs.
- **Any `needs_human_review=True` outcomes specifically traceable to a D candidate** (the new exclusion criterion existing on paper doesn't guarantee the judge enforces it consistently — same category of risk the retention delta's rule (b)/(c) already navigate without a code-level backstop).

## Not proposed in this version

- **`educational_short_generator.py` / Category `EDUCATIONAL` — withdrawn from this delta's pilot scope (round 5).** Attempted across rounds 1-5 (outcome-adjacent claim → 19-word conditional opener → personal-history claim → ungrounded universal-behavior claim → schema-incompatible conditional-eligibility design) — each fix closed one problem and surfaced another, converging on a structural fact: this generator's only input is a topic excerpt with no viewer/reader-behavior data at all, so a "declarative statement about behavior" hook has no reliable, excerpt-grounded content to assert, and the rigid `_PILOT_STRATEGIES_ABCD` schema (exactly 4 candidates, no conditional subset) can't accommodate a "sometimes 3, sometimes 4" design without its own engine changes (a real option — see Delta A.2's `valid_strategies` mechanism, which *could* support a 5th, even-more-conditional strategy set — but that's new scope, not resolvable inside this delta's remaining review budget). Revisiting this generator is deferred to either: a future delta that designs strategy D differently for excerpt-only categories specifically, or a decision that this category simply doesn't get a D strategy.
- **`zodiac_short_generator.py` / Category `GROUNDED_DATA` — withdrawn from this delta's pilot scope (round 6).** Its worked example ("Không phải ai cũng để ý hôm nay là ngày con giáp gì") passed rounds 1-4 unchallenged, but Codex round 6 identified the same class of problem `educational_short_generator.py` had: this generator's real facts (`day_can_chi`, `hop_animals`, `ky_animal` — verified directly, `zodiac_short_generator.py:69-78`) contain zero data about viewer/human attention or behavior, so an "attention/behavior" claim has nothing to be grounded in even though it reads as milder/safer than the educational examples did. **The pattern is now clear across both withdrawals:** strategy D's "declarative behavioral-tendency" mechanism only has real grounding in a generator whose *facts themselves* already describe traits/tendencies — true for `western_zodiac_short_generator.py` (`CREATIVE_ASTROLOGY`'s whole domain is personality description) but not for `GROUNDED_DATA` (calendar/relationship facts) or `EDUCATIONAL` (topic excerpts). This is a useful, generalizable finding for any future rollout, not just a one-off fix: **strategy D should be considered category-dependent by design, not assumed to fit every generator uniformly** — see the pilot acceptance criteria below, which should be evaluated per-category if/when rollout is proposed, not as one blanket "did the pilot succeed" verdict.
- **Rollout to the remaining 9 generators** (the 7 originally out of scope, plus `educational_short_generator.py` and `zodiac_short_generator.py`, both now withdrawn) — explicitly gated on the pilot acceptance criteria above, not on a vague "validated in practice," and per the category-dependence finding above, should specifically prioritize other trait/tendency-describing categories (if any) over categories whose facts are purely factual/computed.
- **No change to `CR-1` hedge/certainty rules** (`PROMPT_DELTA_v1.md`) — strategy D is a hook *mechanism* only, bound by each generator's existing fact-check contract plus the new exclusion criterion; not a new content-claim license.
- **No change to `PROMPT_DELTA_RETENTION_v1.md`'s rule (c)** — strategy D's opening sentence still must be followed by real progression in the middle, same as any other strategy; not re-litigated here. (A.3 above only fixes count-neutral wording shared with the retention delta's blocks — it does not touch rule (c)'s substance.)
- **No code-level enforcement of the new exclusion criterion** (outcome/history/real-time/emotion claims) — same reasoning as the retention delta's rule (b)/(c): this is a semantic judgment with no reliable cheap proxy; relies on the judge prompt + fact-check, tracked via the pilot's human-review-rate metric above, not a regex.

---

**Codex-APPROVED (round 9).** Nothing here has been applied to `short_judge_panel_engine.py` or any generator file yet — awaiting your explicit go-ahead before implementation, same process as `PROMPT_DELTA_v1.md`'s Deltas 1-9 and `PROMPT_DELTA_RETENTION_v1.md`.
