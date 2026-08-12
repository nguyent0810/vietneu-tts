# Prompt Delta — FS Hedge Trimming v1.3 — Trim repeated/near-synonymous hedge phrasing in `iching_short_generator.py`

**Status: Codex-APPROVED (round 4, 2026-07-30) after 4 review rounds (2 HIGH + 1 MEDIUM round 1; 1 HIGH + 1 MEDIUM round 2; 1 LOW round 3; 0 findings round 4). Nothing below has been applied to any file — awaiting your explicit approval before implementation, same as `PROMPT_DELTA_v1.md`'s Deltas 1-9, `PROMPT_DELTA_RETENTION_v1.md`, and `PROMPT_DELTA_HOOK_FORMAT_v1.md`.**

**Round-3 fixes (this revision), summary:** Codex round 3 confirmed the round-2 lead-in-normalization fix was applied correctly and consistently, verified (by applying the rule literally as a judge would) that the 3 real evidence sentences are genuinely caught and the PASS example is genuinely not caught, and found no CRITICAL/HIGH/MEDIUM issues — only 1 LOW: Delta A's check used the fuller phrase "tiền tố/mệnh đề dẫn nhập ngắn KHÔNG MANG NỘI DUNG HEDGE" while Delta B and Delta C's checks used the shorter "tiền tố/mệnh đề dẫn nhập ngắn" without that qualifier, a wording inconsistency (not a substantive gap, since Codex confirmed the final noun-phrase-template match still anchors the check either way). Fixed by making Delta B and C's wording match Delta A's fuller phrasing exactly.

**Round-2 fixes (this revision), summary:** Codex round 2 found the round-1 rewrite's rule text and its own FAIL example contradicted each other: the rule only tripped on sentences that literally "đều mở đầu bằng" (begin with) the same noun-phrase template, but 2 of the 3 real evidence sentences place the hedge after a short lead-in clause ("Theo...", "Đây đại diện cho...") rather than at the literal sentence start — so, read literally, the rule as written would NOT have caught the very defect it was written to catch, and would have left an easy loophole (prepend any short lead-in to dodge the check while the underlying repeated phrase stays unchanged). Fixed in Delta A, B, and C by changing the check to normalize past short, non-hedge lead-in clauses ("Theo...", "Đây là...", "Đây đại diện cho...", "Điều này...") before comparing the noun-phrase template, with an explicit worked note in Delta C's judge-prompt text confirming the 3 real evidence sentences (different lead-ins, same inner template) count as a violation under the corrected wording. Also fixed 2 smaller inconsistencies Codex flagged: the evidence section's prose (previously said all 3 sentences "each open with" their hedge, which was literally false for 2 of them) now accurately describes the lead-in/template structure; and the "Not proposed" section's leftover "near-synonymous words back-to-back" phrasing (a relic of the round-1 vague criterion this revision replaced) was reworded to describe the actual surface-template check.

**Round-1 fixes (this revision), summary:** Codex round 1 confirmed the core defect, the "Current text" citations, the single-consumer scope claim, and the "no change to other generators/shared blocks" reasoning were all correct, but found 2 HIGH + 1 MEDIUM issues in the proposed rule wording itself: (1) HIGH — "MỖI câu" (every sentence) was broader than the actually-approved `PROMPT_DELTA_v1.md` Delta 9 scope, which only requires framing on "MỌI câu có nội dung diễn giải/gán ý nghĩa" (every sentence with interpretive/meaning-attributing content) — fixed in Deltas A and B by quoting Delta 9's exact scope instead of an unqualified "every sentence." (2) HIGH — "các cụm gần nghĩa" (near-synonymous phrases) was too vague to judge consistently, since any two valid hedges necessarily convey a similar underlying meaning ("theo truyền thống," "trong cách diễn giải," "dưới góc nhìn..." are all legitimate variants) — the real, checkable defect is repetition of the same surface **noun-phrase template** ("một cách [X] truyền thống," only swapping X), not similarity of meaning. Fixed in Deltas A, B, and C by redefining the check around the concrete template-repetition pattern, and added a worked FAIL/PASS example pair (after Delta A) showing 2 versions of the same 3 ideas — one that trips the check (same template 3x) and one that doesn't (3 different grammatical structures, similar hedge substance) — so the judge has a concrete boundary to apply, not just a description. (3) MEDIUM — the "gộp dưới 1 mệnh đề dẫn nhập chung" (consolidate under one governing clause) instruction needed an explicit guard against being misread as "hedge once, let later independent sentences ride on it" — the exact pattern Delta 8 already rejected — fixed by adding the explicit exclusion sentence to Delta A and B: hedging one sentence does not cover later grammatically-independent sentences, consolidation must be within a single sentence.

- **Source:** audit point #8 ("FS hedge trimming"), scoped separately from point #7 (`PROMPT_DELTA_HOOK_FORMAT_v1.md`, Codex-approved round 9) and from `PROMPT_DELTA_v1.md`'s Deltas 7-9 (which added CR-1's hedge/belief-framing *requirement* — this delta does not touch that requirement's substance).
- **Investigation method:** before drafting anything, dispatched a research pass across (1) `short_judge_panel_engine.py`'s shared retention/CTA-adjacent prompt blocks, (2) all 7 FS-domain generators' end-of-script instructions, (3) real generated FS scripts' closing sentences (where a CTA would typically live), specifically checking the hypothesis "does CR-1's required hedge language collide with / bloat the CTA sentence(s) at the end of FS scripts?"
- **Finding — hypothesis NOT confirmed as stated, but a real, narrower defect found instead:** no FS generator's CTA/closing instruction interacts with hedge language at the prompt level, and 5 of 6 sampled real FS scripts (`element_color`, `element_luck`, `zodiac`, `twelve_gods`, `lich_hoang_dao`-style output) end cleanly — hedges stay in the body, closings are punchy and hedge-free or lightly hedged. **`short_judge_panel_engine.py`'s shared `_RETENTION_RULES_BLOCK`/`_RETENTION_CHECK_BLOCK` do not mention hedge/CR-1 language at all — no shared-block change is needed or proposed here.** The one real, confirmed defect is narrower than "hedge vs CTA": it is **hedge-phrase repetition/redundancy** — multiple consecutive sentences each independently satisfying CR-1's per-sentence framing requirement (correctly, per `PROMPT_DELTA_v1.md` Delta 8's already-approved sentence-level rule), but each reaching for a near-synonymous restatement of the same idea ("this is a traditional way of understanding"), which reads as repetitive/awkward when stacked. This is a **prose-economy defect, not a compliance failure** — CR-1 is being followed correctly; the wording variety around it is not.
- **Scope:** `iching_short_generator.py` is the **only** generator where this pattern was found, and it is also the sole consumer of `content_categories.INTERPRETATION` (verified: `grep -rl "content_categories.INTERPRETATION" *.py` returns only this one file) — so the shared rubric block for this category can be edited directly without any cross-generator blast radius, unlike `_RETENTION_RULES_BLOCK`. No other FS generator is touched by this delta.

## Evidence (real, current file content)

Real script, verbatim, `drive_input/content_repo_staged/Phong Thủy/Short/KINHDICH_TnViPhong_Short.txt`:
```
Hình ảnh **Tốn (Gió)** gợi mở ý niệm về sự **mềm mỏng nhưng bền bỉ**.
Đó là biểu tượng của quẻ **Tốn Vi Phong** trong **Kinh Dịch**.
Theo **một cách hiểu truyền thống**, từ khóa của quẻ là **Thấm Nhuần**.
**Một cách diễn giải truyền thống** miêu tả đặc tính **Âm linh hoạt** và **thấm nhuần từ từ**.
Đây đại diện cho **một góc nhìn truyền thống** kết hợp sự **mềm mỏng nhưng bền bỉ** để **Thấm Nhuần**.
```
Sentences 3-5 each carry their own independent hedge phrase built on the same underlying noun-phrase template ("một cách hiểu truyền thống" / "một cách diễn giải truyền thống" / "một góc nhìn truyền thống") — each individually CR-1-compliant, but two of the three ("Theo một cách hiểu truyền thống, ..." and "Đây đại diện cho một góc nhìn truyền thống...") place the hedge after a short lead-in clause ("Theo...", "Đây đại diện cho...") rather than at the literal start of the sentence, so any check for this pattern must look past such lead-ins rather than only at literal sentence-initial position (see Delta A/B/C below, corrected per Codex round-2 finding). Stacked in 3 consecutive sentences, the repetition reads as robotic rather than natural.

Root cause traced to `content_categories.py`'s `INTERPRETATION` rubric (the category-level rule that requires this framing) and `iching_short_generator.py`'s own generate/judge prompts (which enforce the rubric's substance but give no guidance on wording variety across sentences).

## Delta A — `content_categories.py`'s `INTERPRETATION` rubric (lines 47-50)

**Current text (verbatim):**
```
    INTERPRETATION: """TIÊU CHUẨN CATEGORY 3 -- TRADITIONAL INTERPRETATION (được diễn giải, không phải chân lý tuyệt đối):
- ĐƯỢC PHÉP diễn giải/ứng dụng truyền thống (vd giải nghĩa quẻ, biểu tượng văn hoá) -- đây là nội dung diễn giải, KHÔNG phải dữ liệu tính toán được như Category 1.
- BẮT BUỘC phải nói rõ đây là "1 cách hiểu"/"1 cách ứng dụng truyền thống" -- KHÔNG được trình bày như chân lý tuyệt đối duy nhất, KHÔNG được tuyên bố dự đoán chính xác tương lai của người xem cụ thể.
- Vẫn phải đúng KHUNG truyền thống thật (tên quẻ, ý nghĩa cổ điển...) -- không bịa khái niệm không tồn tại, chỉ được diễn giải MỞ trong khuôn khổ khái niệm có thật.""",
```

**Proposed change (new 4th bullet appended, substance of the existing 3 bullets unchanged):**
```
    INTERPRETATION: """TIÊU CHUẨN CATEGORY 3 -- TRADITIONAL INTERPRETATION (được diễn giải, không phải chân lý tuyệt đối):
- ĐƯỢC PHÉP diễn giải/ứng dụng truyền thống (vd giải nghĩa quẻ, biểu tượng văn hoá) -- đây là nội dung diễn giải, KHÔNG phải dữ liệu tính toán được như Category 1.
- BẮT BUỘC phải nói rõ đây là "1 cách hiểu"/"1 cách ứng dụng truyền thống" -- KHÔNG được trình bày như chân lý tuyệt đối duy nhất, KHÔNG được tuyên bố dự đoán chính xác tương lai của người xem cụ thể.
- Vẫn phải đúng KHUNG truyền thống thật (tên quẻ, ý nghĩa cổ điển...) -- không bịa khái niệm không tồn tại, chỉ được diễn giải MỞ trong khuôn khổ khái niệm có thật.
- MỖI câu có nội dung diễn giải/gán ý nghĩa (đúng phạm vi đã duyệt ở Delta 9, `PROMPT_DELTA_v1.md`: "MỌI câu có nội dung diễn giải/gán ý nghĩa, kể cả câu ngắn chỉ nêu biểu tượng/tên quẻ") vẫn PHẢI tự mang framing truyền thống của riêng câu đó (không được bỏ hedge) -- NHƯNG nếu từ 2 câu liên tiếp trở lên, SAU KHI bỏ qua các tiền tố/mệnh đề dẫn nhập ngắn không mang nội dung hedge đứng trước (vd "Theo...", "Đây là...", "Đây đại diện cho...", "Điều này..."), đều chứa CÙNG 1 khuôn cụm danh từ dạng "một cách [X] truyền thống"/"một [X] truyền thống" (chỉ đổi từ đầu X, vd hiểu/diễn giải/góc nhìn/nhìn nhận) → VI PHẠM (lặp khuôn bề mặt, dù mỗi câu riêng lẻ đều đúng khung, và dù khuôn không nằm ở vị trí mở đầu tuyệt đối của câu). Cách sửa hợp lệ: đổi CẤU TRÚC câu (không chỉ thêm/đổi tiền tố dẫn nhập trong khi giữ nguyên khuôn cụm danh từ bên trong) để hedge được tích hợp khác nhau qua từng câu (vd 1 câu dùng khuôn "một cách X truyền thống", câu kế tiếp không lặp lại khuôn đó mà hedge bằng cách khác, như gắn "truyền thống" vào tính từ/trạng ngữ thay vì cụm danh từ), HOẶC gộp các ý liên quan vào DUY NHẤT 1 câu dưới 1 mệnh đề dẫn nhập truyền thống chung bao trùm ngữ pháp trực tiếp (mẫu đã được duyệt ở Delta 8, `PROMPT_DELTA_v1.md`). KHÔNG chấp nhận 1 câu hedge độc lập rồi các câu sau, không liên quan ngữ pháp trực tiếp, dựa vào hedge đó (đây là lỗi Delta 8 đã từ chối, không được lặp lại ở đây).""",
```

**Worked example, added per Codex round-1 finding (illustrates the FAIL/PASS boundary concretely — same 3 underlying ideas, only the surface template changes):**

FAIL (the real defect this delta targets — 3 consecutive sentences share the same "một cách [X] truyền thống"/"một [X] truyền thống" noun-phrase template once each sentence's short lead-in — "Theo...", "Đây đại diện cho..." — is looked past; the template repeats even though literal sentence-initial wording differs, corrected per Codex round-2 finding):
```
Theo một cách hiểu truyền thống, từ khóa của quẻ là Thấm Nhuần.
Một cách diễn giải truyền thống miêu tả đặc tính Âm linh hoạt và thấm nhuần từ từ.
Đây đại diện cho một góc nhìn truyền thống kết hợp sự mềm mỏng nhưng bền bỉ để Thấm Nhuần.
```

PASS (same 3 ideas, same hedge substance, but each sentence integrates "truyền thống" through a different grammatical structure — no repeated noun-phrase template, so this does NOT trip check (d) even though the underlying meaning is similarly hedged throughout):
```
Theo một cách hiểu truyền thống, từ khóa của quẻ là Thấm Nhuần.
Đặc tính Âm linh hoạt và thấm nhuần từ từ vốn được mô tả như vậy trong khuôn khổ truyền thống này.
Sự mềm mỏng nhưng bền bỉ, gắn liền với Thấm Nhuần, là cách quẻ này thường được hiểu theo lối truyền thống.
```

## Delta B — `iching_short_generator.py`'s `_GENERATE_CANDIDATES_PROMPT` (`QUY TẮC BẮT BUỘC` block)

**Current text (verbatim):**
```
QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ dùng đúng ý nghĩa/từ khoá có trong dữ liệu (essence, keyword) -- KHÔNG bịa thêm chi tiết lịch sử, KHÔNG bịa hào từ/lời giải quẻ cụ thể không có trong dữ liệu.
- KHÔNG được dự đoán/khẳng định điều gì sẽ xảy ra với người xem -- đây là giới thiệu triết lý, không phải bói toán cho ai cả.
- ĐÁNH DẤU tên quẻ/từ khoá quan trọng bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
{revision_note}
```

**Proposed change (new bullet inserted before `{revision_note}`):**
```
QUY TẮC BẮT BUỘC cho CẢ 3 phương án:
- CHỈ dùng đúng ý nghĩa/từ khoá có trong dữ liệu (essence, keyword) -- KHÔNG bịa thêm chi tiết lịch sử, KHÔNG bịa hào từ/lời giải quẻ cụ thể không có trong dữ liệu.
- KHÔNG được dự đoán/khẳng định điều gì sẽ xảy ra với người xem -- đây là giới thiệu triết lý, không phải bói toán cho ai cả.
- ĐÁNH DẤU tên quẻ/từ khoá quan trọng bằng **hai dấu sao** -- 1-3 cụm mỗi câu.
- MỖI câu có nội dung diễn giải/gán ý nghĩa vẫn cần framing truyền thống riêng ("1 cách hiểu/diễn giải truyền thống"...) nhưng nếu từ 2 câu liên tiếp trở lên, SAU KHI bỏ qua tiền tố/mệnh đề dẫn nhập ngắn không mang nội dung hedge phía trước (vd "Theo...", "Đây là...", "Đây đại diện cho..."), đều chứa CÙNG 1 khuôn cụm danh từ dạng "một cách [X] truyền thống"/"một [X] truyền thống" (chỉ đổi từ X, vd hiểu/diễn giải/góc nhìn) → VI PHẠM. Sửa bằng cách đổi CẤU TRÚC câu (không chỉ thêm/đổi tiền tố trong khi giữ nguyên khuôn cụm danh từ bên trong) qua từng câu, hoặc gộp các ý liên quan vào DUY NHẤT 1 câu dưới 1 mệnh đề dẫn nhập chung (không được để 1 câu hedge độc lập rồi các câu sau không liên quan ngữ pháp trực tiếp dựa vào hedge đó).
{revision_note}
```

## Delta C — `iching_short_generator.py`'s `_JUDGE_PROMPT` (`BƯỚC 1`)

**Current text (verbatim):**
```
BƯỚC 1 -- KIỂM TRA (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) CHỈ dùng đúng essence/keyword trong dữ liệu, không bịa hào từ/chi tiết lịch sử khác, (b) có NGỤ Ý đây là "quẻ của hôm nay"/dự đoán riêng cho người xem không -- có thì FAIL NGAY (vi phạm quy tắc Category 3 nghiêm trọng nhất), (c) có khẳng định chắc chắn điều gì sẽ xảy ra không -- có thì FAIL. Vi phạm bất kỳ điểm nào → LOẠI.
```

**Proposed change (new sub-check `(d)` appended to the same step, not a new step — matches the pattern already used in `PROMPT_DELTA_HOOK_FORMAT_v1.md`'s C.2b):**
```
BƯỚC 1 -- KIỂM TRA (LOẠI TRỪ TRƯỚC): với MỖI phương án, kiểm tra: (a) CHỈ dùng đúng essence/keyword trong dữ liệu, không bịa hào từ/chi tiết lịch sử khác, (b) có NGỤ Ý đây là "quẻ của hôm nay"/dự đoán riêng cho người xem không -- có thì FAIL NGAY (vi phạm quy tắc Category 3 nghiêm trọng nhất), (c) có khẳng định chắc chắn điều gì sẽ xảy ra không -- có thì FAIL, (d) có từ 2 câu liên tiếp trở lên, SAU KHI bỏ qua tiền tố/mệnh đề dẫn nhập ngắn không mang nội dung hedge phía trước câu (vd "Theo...", "Đây là...", "Đây đại diện cho..."), đều chứa CÙNG 1 khuôn cụm danh từ dạng "một cách [X] truyền thống"/"một [X] truyền thống" (chỉ đổi từ X -- vd "Theo một cách hiểu truyền thống..." rồi "Một cách diễn giải truyền thống..." rồi "Đây đại diện cho một góc nhìn truyền thống..." dùng liên tiếp VẪN TÍNH LÀ VI PHẠM dù tiền tố mở đầu mỗi câu khác nhau, vì khuôn cụm danh từ bên trong giống nhau) không -- có thì FAIL (lặp khuôn bề mặt, đọc rối, dù mỗi câu riêng lẻ đúng khung Category 3; hedge dùng cấu trúc câu thật sự KHÁC nhau, không chỉ đổi tiền tố dẫn nhập, KHÔNG tính là vi phạm điểm này). Vi phạm bất kỳ điểm nào → LOẠI.
```

## Not proposed

- **No change to `short_judge_panel_engine.py`'s shared `_RETENTION_RULES_BLOCK`/`_RETENTION_CHECK_BLOCK`** — confirmed these contain no hedge/CTA-interaction text at all; the hypothesis that motivated this audit point was not evidenced there.
- **No change to any other FS generator** (`element_color_short_generator.py`, `element_luck_short_generator.py`, `zodiac_short_generator.py`, `zodiac_month_short_generator.py`, `twelve_gods_short_generator.py`, `lich_hoang_dao_generator.py`) — 5 of 6 sampled real scripts across these generators end cleanly with no hedge-repetition or CTA-collision pattern found. Extending this delta's rule to them would be an unevidenced, precautionary change, not a fix for a confirmed defect — consistent with this session's discipline of not touching generators without real evidence (see `PROMPT_DELTA_HOOK_FORMAT_v1.md`'s withdrawal of unsuitable pilot generators for the same reason, in the opposite direction).
- **No relaxation of CR-1's per-sentence hedge requirement** (`PROMPT_DELTA_v1.md` Delta 8, already Codex-approved) — this delta requires *wording variety or grammatical consolidation*, not fewer hedges. A script could still legally satisfy this delta while hedging every single sentence, as long as consecutive sentences don't repeat the same underlying noun-phrase hedge template (see Delta A/B/C's exact check, corrected per Codex round 2 to normalize past short lead-in clauses rather than only matching literal sentence-initial wording).
- **No CTA-specific rule anywhere** — investigation found no FS generator's closing instruction is CTA-specific in the first place (no generator instructs an explicit "subscribe/comment/like" sentence at script end); the "hedge vs CTA" framing in this audit point's original title does not describe a real mechanism in the current codebase, and is not carried into the delta's actual rule text.

---

**Codex-APPROVED (round 4).** Nothing here has been applied to `content_categories.py` or `iching_short_generator.py` yet — awaiting your explicit go-ahead before implementation, same process as `PROMPT_DELTA_v1.md`'s Deltas 1-9, `PROMPT_DELTA_RETENTION_v1.md`, and `PROMPT_DELTA_HOOK_FORMAT_v1.md`.
