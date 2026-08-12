# Prompt Delta — v1.4 (Deltas 7-9 revised per Codex round 1)

**Status: Codex-APPROVED in full — Deltas 1-6 (3 rounds) and Deltas 7-9 (2 rounds). Nothing below has been applied to any file — awaiting your explicit approval before implementation.**

**Round-1 fixes to Deltas 7-9 (this revision):** Delta 7's proposed rule strengthened from advisory wording ("nên tránh") to an explicit FAIL criterion, matching Deltas 1-6's enforcement pattern. Delta 8 corrected on two points: the "no certainty/belief-framing check at all" claim was inaccurate (a certainty-adjacent check already exists in the real judge prompt — verified directly) — the delta now claims only the belief-framing branch; and the "hedge once per script" wording was removed, since it created a script-level relaxation inconsistent with the sentence-level counting methodology and would have let later unhedged sentences ride on an earlier, grammatically-unconnected hedge.

- **Version:** 1.4
- **Source:** Deltas 1-6: Creator Rule `CR-1` (`CREATOR_SPECIFICATION_v2.md`), sourced from Cycle 1 §1.6 + Cycle 2 §1.6. Deltas 7-9: `PR5_AUDIT_REPORT_v1.md`'s executed, Codex-approved audit (rate threshold triggered, 32/12 = 2.67/script), which recommended widening `CR-1` enforcement to `western_zodiac`/`educational`/`iching`.
- **Scope:** Deltas 1-6 target the 6 `GROUNDED_DATA` generators individually (shared rubric confirmed unused by them — see below). Deltas 7-9 target `content_categories.py`'s shared rubric constants for `CREATIVE_ASTROLOGY`, `EDUCATIONAL`, and `INTERPRETATION` respectively — confirmed each is used by exactly one generator, and each generator correctly wires in the shared rubric (unlike the `GROUNDED_DATA` generators).
- **Status:** EXPERIMENTAL — not applied.

**Purpose:** record proposed prompt changes as deltas against real, current file content — not full rewrites.

---

## Correction from v1.0 of this document — a real implementation gap was found, changing the whole approach

**v1.0 of this delta proposed editing only `content_categories.py`'s shared `CATEGORY_RUBRICS[GROUNDED_DATA]` string, on the assumption that this text reaches every `GROUNDED_DATA`-tagged generator's judge prompt via `category_rubric_block()`. That assumption was wrong, caught during Codex round-1 review and independently re-verified before accepting.**

**Verification performed:** grepped `content_categories\.` usage across all 6 files that declare `CONTENT_CATEGORY = content_categories.GROUNDED_DATA`:
```
element_luck_short_generator.py   -- only the CONTENT_CATEGORY declaration, no category_rubric_block() call
zodiac_short_generator.py         -- only the CONTENT_CATEGORY declaration, no category_rubric_block() call
element_color_short_generator.py  -- only the CONTENT_CATEGORY declaration, no category_rubric_block() call
twelve_gods_short_generator.py    -- only the CONTENT_CATEGORY declaration, no category_rubric_block() call
zodiac_month_short_generator.py   -- only the CONTENT_CATEGORY declaration, no category_rubric_block() call
lich_hoang_dao_generator.py       -- only the CONTENT_CATEGORY declaration, no category_rubric_block() call
```
Positive control — `iching_short_generator.py` (`CONTENT_CATEGORY = content_categories.INTERPRETATION`) **does** call `content_categories.category_rubric_block(content_categories.INTERPRETATION)` in its judge prompt (line 81).

**Conclusion:** all 6 `GROUNDED_DATA` generators have fully inline, hand-written judge prompts. `content_categories.py`'s shared `CATEGORY_RUBRICS[GROUNDED_DATA]` constant currently has **no effect** on any of their actual behavior. Editing it alone (v1.0's proposal) would not implement `CR-1` for these generators — this is corrected below with per-generator deltas instead.

**This is itself a newly-discovered fact worth flagging beyond this delta's immediate scope:** the `content_categories.py` module's stated purpose ("mỗi category thực sự được đánh giá đúng chuẩn của nó" via `category_rubric_block()`) is not actually wired up for the `GROUNDED_DATA` category at all, even though 6 real generators declare that category. This is not part of `CR-1`'s original evidence and is not proposed as a new rule here — noted for a future review cycle to assess as its own finding, not acted on in this delta.

---

## What each generator's existing judge prompt actually checks today (verified per-file, not assumed uniform)

**`CR-1` has two independent branches — every delta below must cover both, not just one (corrected per Codex round 2, which caught that v1.1 of this delta mostly only added the certainty-language branch):**
1. **Certainty branch:** a future outcome/result stated as certain (e.g. "chắc chắn," "vô cùng," "tuyệt đối," "hứa hẹn").
2. **Belief-framing branch (independent of branch 1 — a claim can pass branch 1 and still violate branch 2):** a belief/tradition-based claim (phong thủy/tử vi/lịch pháp relationships, e.g. "màu X khắc mệnh Y," "giờ này cát khí") presented as flat objective fact, without hedge/attribution language ("theo quan niệm," "được xem là," "có thể," "thường").

| Generator | Existing certainty-branch check? | Existing belief-framing-branch check? |
|---|---|---|
| `zodiac_short_generator.py` | **Yes** — quoted verbatim: *"(d) LỖI THẬT ĐÃ GẶP -- có dùng cụm tăng cường mức độ chắc chắn không (vô cùng, đại cát, chắc chắn, tuyệt đối, hứa hẹn...)? ... có thì FAIL."* Names the exact phrases in the confirmed violation. | **No** — (d) only catches intensity words, not the *absence* of belief-framing on an otherwise plainly-worded claim. **Corrected per Codex round 2:** v1.1 of this delta wrongly called this "an equivalent, arguably stronger check" and proposed no delta for this file — that overstated coverage; a delta is needed here too (Delta 6 below). |
| `element_color_short_generator.py` | Narrow — *"(b) không cam kết kết quả chắc chắn (giàu có/may mắn tuyệt đối)"*, scoped to wealth/luck only. | No. |
| `element_luck_short_generator.py` | **Yes — corrected per Codex round 2:** v1.1 of this delta wrongly claimed "No certainty/hedging check present." The real text has *"(c) không cam kết kết quả chắc chắn"* (re-verified directly, `element_luck_short_generator.py:114`). | No. |
| `twelve_gods_short_generator.py` | Has a threat/doom-language check, but only for `god_status=bad` — no certainty check for `good` status. | No, for either status. |
| `zodiac_month_short_generator.py` | Has a threat-language check ("không doạ dẫm hậu quả"), not a certainty check. | No. |
| `lich_hoang_dao_generator.py` | No. | No. |

**Open question, not resolved here:** `zodiac_short_generator.py`'s existing certainty-branch check names the exact phrases found in `CONGIAP20260726_ConGiap_01`, yet that video was still published with those phrases. No git history exists for this file (untracked) to determine whether the check predates or postdates that video. Flagged for whoever implements this delta to investigate — not assumed either way here.

---

Each delta below is written to independently satisfy **both** `CR-1` branches, and each is worded not to duplicate a criterion that already exists in that file.

## Delta 1 — `element_color_short_generator.py`

**Target location:** the `BƯỚC 1 -- FACT-CHECK` line in `_JUDGE_PROMPT`.

**Current text (verbatim):**
```
BƯỚC 1 -- FACT-CHECK (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) CHỈ dùng đúng màu/tên mệnh có trong dữ liệu, không thêm màu khác, (b) không cam kết kết quả chắc chắn (giàu có/may mắn tuyệt đối), (c) không bịa vật phẩm cụ thể ngoài ví/hình nền/trang phục. Vi phạm bất kỳ điểm nào → LOẠI.
```

**Proposed change to criterion (b) (widen the certainty branch, don't remove) plus a new (d) for the belief-framing branch:**
```
(b) không cam kết kết quả chắc chắn dưới bất kỳ hình thức nào -- không chỉ "giàu có/may mắn tuyệt đối" mà cả các khẳng định nhân quả không dè dặt (vd "gây khắc chế và làm năng lượng mất cân bằng" nói như sự thật tuyệt đối)
(d) có trình bày mối quan hệ Ngũ Hành (khắc chế, tương sinh, bổ trợ...) như SỰ THẬT KHÁCH QUAN, không có framing dè dặt ("theo quan niệm Ngũ Hành", "được xem là", "có thể") không? Đây là điểm ĐỘC LẬP với (b) -- 1 câu có thể không "cam kết chắc chắn" (không dùng từ tuyệt đối) nhưng VẪN vi phạm nếu trình bày quan hệ Ngũ Hành như sự thật khoa học. Có thì FAIL.
```

## Delta 2 — `element_luck_short_generator.py`

**Target location:** the `BƯỚC 1 -- FACT-CHECK` line — add a new criterion `(f)` after existing `(e)`. **Corrected per Codex round 2:** existing `(c)` already covers the certainty branch — this delta only adds the belief-framing branch, and does not duplicate `(c)`.

**Proposed addition:**
```
(f) có trình bày mối quan hệ mệnh/ngũ hành/can chi như SỰ THẬT KHÁCH QUAN mà không có framing dè dặt phù hợp ("theo quan niệm", "được xem là") không? Đây là điểm ĐỘC LẬP với (c) -- 1 câu có thể pass (c) (không dùng từ chắc chắn/tuyệt đối) nhưng vẫn FAIL ở đây nếu thiếu framing dè dặt cho 1 nhận định dựa trên niềm tin truyền thống.
```

## Delta 3 — `twelve_gods_short_generator.py`

**Target location:** `BƯỚC 1 -- FACT-CHECK` — add a new criterion `(f)`. **Corrected per Codex round 2:** must apply to BOTH `god_status=good` and `god_status=bad`, not just `good` — existing `(d)` only bans severe-threat language for `bad` status, it does not ban plain certainty language for either status.

**Proposed addition:**
```
(f) (áp dụng cho CẢ god_status=good VÀ bad, độc lập với check doạ dẫm ở (d)): có dùng ngôn ngữ khẳng định chắc chắn cho kết quả (vd "chắc chắn", "tuyệt đối", "vô cùng may mắn") KHÔNG, và có trình bày quyền năng/ảnh hưởng của vị Thần như sự thật khách quan mà không có framing dè dặt ("theo tín ngưỡng dân gian", "được cho là") không? Vi phạm 1 trong 2 → FAIL.
```

## Delta 4 — `zodiac_month_short_generator.py`

**Target location:** `BƯỚC 1 -- FACT-CHECK` — add a new criterion `(f)`.

**Proposed addition:**
```
(f) (độc lập với check doạ dẫm ở (c)): có dùng ngôn ngữ khẳng định chắc chắn/tuyệt đối cho hậu quả/kết quả không, và có trình bày quan hệ xung khắc/tương hợp theo tháng như sự thật khách quan mà không có framing dè dặt ("theo quan niệm", "được xem là") không? Vi phạm 1 trong 2 → FAIL.
```

## Delta 5 — `lich_hoang_dao_generator.py`

**Target location:** `BƯỚC 1 -- FACT-CHECK (LÀM TRƯỚC, LOẠI TRỪ)` — add a new sentence.

**Proposed addition:**
```
Cũng kiểm tra: có dùng ngôn ngữ khẳng định chắc chắn/tuyệt đối cho mức độ tốt xấu của ngày/giờ/hướng không (vd "chắc chắn đại cát", "tuyệt đối thuận lợi"), VÀ có trình bày ý nghĩa cát/hung của ngày như sự thật khách quan mà không có framing dè dặt ("theo lịch pháp truyền thống", "được xem là") không? Vi phạm 1 trong 2 → FAIL, cùng mức nghiêm trọng như sai lệch dữ liệu.
```

## Delta 6 — `zodiac_short_generator.py` (NEW — corrected per Codex round 2, this file was wrongly left out of v1.1)

**Target location:** `BƯỚC 1 -- FACT-CHECK` — add a new criterion `(e)` after existing `(d)`. Existing `(d)` already covers the certainty branch (and directly names the phrases in the confirmed violation) — this delta only adds the belief-framing branch.

**Proposed addition:**
```
(e) có trình bày quan hệ Tam Hợp/Tứ Hành Xung hoặc mức độ hợp/kỵ như SỰ THẬT KHÁCH QUAN mà không có framing dè dặt ("theo quan niệm dân gian", "được xem là") không? Đây là điểm ĐỘC LẬP với (d) -- 1 câu có thể pass (d) (không dùng từ cường điệu) nhưng vẫn FAIL ở đây nếu thiếu framing dè dặt.
```

---

## Deltas 7-9 — added following `PR-5`'s executed audit (`PR5_AUDIT_REPORT_v1.md`, Codex-approved v3.0, disputed items resolved in v4.0)

**Architectural note — these 3 target a different layer than Deltas 1-6, verified before drafting, not assumed:** `western_zodiac_short_generator.py`, `iching_short_generator.py`, and `educational_short_generator.py` — unlike the 6 `GROUNDED_DATA` generators above — each correctly call `content_categories.category_rubric_block(...)`, and each is the *only* generator using its respective category (`CREATIVE_ASTROLOGY`, `INTERPRETATION`, `EDUCATIONAL` — confirmed by grepping every `CONTENT_CATEGORY = content_categories.X` declaration in the repo, one match each). This means, unlike Deltas 1-6, a single edit to the shared `content_categories.py` rubric string for each category takes effect for exactly the one generator using it — no per-generator duplication needed here, and no risk of an edit affecting an unintended second generator.

Applying the same uniform `CR-1` two-branch structure as Deltas 1-6 — no category-specific relaxation of the branches themselves. Where a category's design has a genuine, real tension with applying the branches, that tension is disclosed below, not silently resolved by narrowing the rule for that category.

### Delta 7 — `content_categories.py`, `CATEGORY_RUBRICS[CREATIVE_ASTROLOGY]`

**Target:** `content_categories.py`, `CREATIVE_ASTROLOGY` entry (currently lines 49-52).

**Current text (verbatim):**
```
CREATIVE_ASTROLOGY: """TIÊU CHUẨN CATEGORY 4 -- CREATIVE ASTROLOGY (đánh giá sáng tạo, KHÔNG fact-check dữ liệu):
- KHÔNG áp dụng fact-check kiểu đối chiếu số liệu -- thể loại này (cung hoàng đạo, tính cách, tình yêu...) vốn không có "đúng-sai" tính toán được.
- Đánh giá theo CHẤT LƯỢNG SÁNG TẠO: có sáo rỗng/chung chung không (áp dụng cho cung nào cũng đúng = sáo rỗng, LOẠI), có tuyệt đối hoá không (nói chắc chắn điều sẽ xảy ra = LOẠI), có giọng văn hấp dẫn/cụ thể cho ĐÚNG cung đang nói không.
- Đây là nội dung GIẢI TRÍ CÓ TRÁCH NHIỆM -- không khẳng định chắc chắn tương lai, nhưng vẫn được vui/hấp dẫn/cụ thể.""",
```

**Evidence this category needs a delta:** the existing "tuyệt đối hoá" check only bans certain-future-outcome language ("nói chắc chắn điều sẽ xảy ra") — it does not require traditional-belief framing on flat personality/element-trait attributions. `PR5_AUDIT_REPORT_v1.md` found 6 confirmed instances across the 2 sampled scripts (e.g. "...thực ra họ lại sở hữu tư duy rất sắc bén," "Mang năng lượng Hoả, Bạch Dương dễ cháy hết mình...") — none use future-certainty language, so the existing check doesn't catch them; all are flat trait/element attributions with no hedge.

**Proposed addition (new 4th bullet — corrected per Codex round 1, strengthened to an explicit FAIL criterion, matching Deltas 1-6's enforcement pattern instead of advisory wording):**
```
- ĐỘC LẬP với việc không "tuyệt đối hoá tương lai": mỗi khẳng định về đặc điểm tính cách/nguyên tố PHẢI dùng framing chủ quan/xu hướng phù hợp cho nội dung chiêm tinh giải trí (vd "thường/hay có xu hướng/dễ...") thay vì khẳng định trực tiếp như sự thật khách quan về cung đó. Phương án nào có câu khẳng định trực tiếp đặc điểm tính cách/nguyên tố mà KHÔNG dùng framing này → LOẠI, độc lập với việc có "tuyệt đối hoá tương lai" hay không.
```

**Real design tension — disclosed, not resolved unilaterally:** `CREATIVE_ASTROLOGY`'s own stated design explicitly rejects fact-checking and rewards "giọng văn hấp dẫn/cụ thể" (vivid, specific, confident voice) as a positive quality. Adding a hedge-everywhere requirement risks conflicting with that design goal — hedged personality writing ("Bạch Dương CÓ THỂ ĐƯỢC XEM LÀ dễ cháy hết mình...") reads noticeably weaker than the current confident style, and confident trait-writing is arguably what makes this category's content engaging by design, not a defect. This delta applies `CR-1` faithfully as approved (uniform application, no category-specific rule relaxation), but this tension is real and is surfaced here for your decision, not quietly resolved by watering down the delta's wording.

### Delta 8 — `content_categories.py`, `CATEGORY_RUBRICS[EDUCATIONAL]`

**Target:** `content_categories.py`, `EDUCATIONAL` entry (currently lines 41-44).

**Current text (verbatim):**
```
EDUCATIONAL: """TIÊU CHUẨN CATEGORY 2 -- EDUCATIONAL KNOWLEDGE (đúng tài liệu, được kể chuyện):
- Nội dung phải ĐÚNG theo tài liệu tham khảo (facts/excerpt) -- không phát minh kiến thức mới, không diễn giải sai lệch ý gốc.
- ĐƯỢC PHÉP giải thích, kể chuyện, minh hoạ bằng ví dụ, so sánh -- miễn là không mâu thuẫn với tài liệu gốc. KHÔNG cần tạo "dữ liệu của hôm nay" -- đây là kiến thức nền, không gắn ngày.
- Mục tiêu là GIÁO DỤC dễ hiểu, không phải liệt kê khô khan.""",
```

**Evidence:** `PR5_AUDIT_REPORT_v1.md` found 4 confirmed instances in the one sampled script (`KIENTHUC_HnhnhndtrcquanvchukNgHnhTngKhc_01`) — the entire Ngũ Hành Tương Khắc cycle explanation ("Rễ cây Mộc hút cạn dưỡng chất... Mộc khắc Thổ," etc.) presented as physical-causal mechanism fact, with zero "theo hệ thống Ngũ Hành truyền thống" framing anywhere in the script.

**Corrected per Codex round 1 — the "no check at all" claim was inaccurate.** The real judge prompt already has a certainty-branch-adjacent check: *"tuyệt đối hoá quá mức → LOẠI"* (`educational_short_generator.py:105`), and the generation prompt also instructs against absolutizing. This delta therefore adds **only the belief-framing branch** (matching how Deltas 2 and 6 were scoped after the same correction was made for them in round 2) — it does not claim to add "both branches," since one is already present.

**Proposed addition (new 4th bullet, belief-framing branch only — corrected per Codex round 1 to remove the script-level "once is enough" relaxation, which contradicted the sentence-level counting methodology and would let later unhedged sentences ride on an earlier hedge elsewhere in the same script):**
```
- Nếu nội dung trình bày một hệ thống/khái niệm truyền thống (Ngũ Hành, Âm Dương, Can Chi...) như cơ chế nhân quả, MỖI câu trình bày một quan hệ/cơ chế cụ thể trong hệ thống đó (vd "X khắc Y", "X sinh Y") PHẢI tự mang framing truyền thống trong chính câu đó hoặc trong mệnh đề ngữ pháp trực tiếp bao trùm nó (vd 1 câu dẫn nhập "Theo hệ thống Ngũ Hành truyền thống, chu trình này gồm:" ngay trước một danh sách liệt kê các quan hệ, nếu mối liên hệ ngữ pháp giữa câu dẫn và danh sách là rõ ràng và liên tục -- KHÔNG chấp nhận 1 câu hedge ở đầu kịch bản rồi các câu sau, không liên quan ngữ pháp trực tiếp, trình bày cơ chế như sự thật khách quan). KHÔNG được trình bày cơ chế này như quy luật vật lý đã được chứng minh khách quan.
```

### Delta 9 — `content_categories.py`, `CATEGORY_RUBRICS[INTERPRETATION]`

**Target:** `content_categories.py`, `INTERPRETATION` entry (currently lines 45-48).

**Current text (verbatim):**
```
INTERPRETATION: """TIÊU CHUẨN CATEGORY 3 -- TRADITIONAL INTERPRETATION (được diễn giải, không phải chân lý tuyệt đối):
- ĐƯỢC PHÉP diễn giải/ứng dụng truyền thống (vd giải nghĩa quẻ, biểu tượng văn hoá) -- đây là nội dung diễn giải, KHÔNG phải dữ liệu tính toán được như Category 1.
- BẮT BUỘC phải nói rõ đây là "1 cách hiểu"/"1 cách ứng dụng truyền thống" -- KHÔNG được trình bày như chân lý tuyệt đối duy nhất, KHÔNG được tuyên bố dự đoán chính xác tương lai của người xem cụ thể.
- Vẫn phải đúng KHUNG truyền thống thật (tên quẻ, ý nghĩa cổ điển...) -- không bịa khái niệm không tồn tại, chỉ được diễn giải MỞ trong khuôn khổ khái niệm có thật.""",
```

**Evidence this needs only a small, precise addition (not a rewrite):** this category already has the strongest belief-framing requirement of any category audited — `PR5_AUDIT_REPORT_v1.md` found only **1 confirmed instance** across 2 sampled scripts (`KINHDICH_TnViPhong_01` sentence 2: "Đó là biểu tượng của quẻ Tốn Vi Phong trong Kinh Dịch" — stated flatly), with the second sampled script (`KINHDICH_CnViThin_01`) fully clean. The existing requirement evidently works well for substantive interpretive claims (essence, keyword meaning) but the one gap is a bare symbol/name attribution sentence, which may be getting judged as "just naming the hexagram" rather than as a claim needing its own framing.

**Proposed addition (clarifying sentence appended to the existing 2nd bullet, not a new bullet):**
```
Áp dụng yêu cầu framing này cho MỌI câu có nội dung diễn giải/gán ý nghĩa, kể cả câu ngắn chỉ nêu biểu tượng/tên quẻ (vd "Đó là biểu tượng của quẻ X" cũng cần framing truyền thống nếu đứng như 1 khẳng định độc lập, không chỉ các câu diễn giải dài).
```

---

## Not proposed in this version

- No change to `content_categories.py`'s `CATEGORY_RUBRICS[GROUNDED_DATA]` — since it's confirmed unused by any of the 6 `GROUNDED_DATA` generators, editing it would have no effect.
- No change to `content_categories.py`'s `category_rubric_block()` wiring for the `GROUNDED_DATA` generators — a real, larger refactor beyond a prompt-text delta, not proposed here.
- No changes for `STORYTELLING` — `PR5_AUDIT_REPORT_v1.md` found 0 confirmed instances in its 1 sampled script; no evidence to act on.

---

**Awaiting approval.** None of Deltas 1-9 have been applied to any generator or `content_categories.py`.
