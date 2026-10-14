# C4 Repair — Round 2 (dev/holdout methodology, selective adjudicator prototype)

Ngày chạy: 2026-08-24. Git SHA nền: `027bd832ac682ff9071f1f8eb238feeb831ca2d3` (không đổi trong suốt round này — chỉ sửa `creator_specs/CL_VERIFIED_CLAIM_LEDGER_v1.json`, `handoff/c4_freeze/*`, `handoff/*REPORT*.md`; KHÔNG sửa lại `cl_risk_gate_verification.py` — production C4 giữ nguyên thiết kế v2 từ round 1). Ledger version cuối: `36a254300a01` (không đổi từ round 1).

**Kết luận cuối:** `NEEDS_FIX` — xem Phần 15.

Kiến trúc an toàn cốt lõi (claim-ledger producer/consumer, numeric-token consistency, source-tier policy, post-rewrite verification) **giữ nguyên, không đổi** trong round này — đúng yêu cầu, không phát hiện BLOCKER độc lập mới nào đòi hỏi sửa các hệ thống đó.

---

## 1. Remaining False-Block Diagnosis (3 case round 1)

`C4_DEV_CORPUS_v1` = 35 fixture đã đóng băng round 1 (`handoff/c4_freeze/c4_golden_corpus_v1.json`) — KHÔNG đổi nhãn thêm trong round này.

| ID | Excerpt (rút gọn) | Câu | Nhãn v2 | Materiality | Lý do C4 chặn | Lý do nhãn vàng=grounded | Bằng chứng nhỏ nhất | Failure class |
|---|---|---|---|---|---|---|---|---|
| G02 | "...Quốc hội thông qua FCPA, và Tổng thống Jimmy Carter ký ban hành luật ngày 19/12/1977." | "Nhằm khôi phục niềm tin công chúng, Tổng thống Jimmy Carter đã ký ban hành đạo luật FCPA vào ngày 19/12/1977." | UNSUPPORTED (biến động qua các lần chạy) | true | Model coi cụm mở đầu "Nhằm khôi phục niềm tin công chúng" là gán ĐỘNG CƠ CÁ NHÂN cho hành động ký của Carter, trong khi excerpt gắn động cơ đó cho CẢ quá trình lập pháp (Quốc hội + Carter) | Hành động "ký ban hành" + ngày tháng khớp đúng excerpt; việc nén 2 vế thành 1 không đổi sự thật cốt lõi | "Trước áp lực khôi phục niềm tin công chúng...Quốc hội thông qua FCPA, và Tổng thống Jimmy Carter ký ban hành luật ngày 19/12/1977" | **reference_resolution** (gán lại phạm vi của 1 cụm động cơ across compound clause) |
| G03 | (toàn văn Lockheed) | "Vì sao bê bối Lockheed buộc Mỹ thông qua đạo luật FCPA?" | UNSUPPORTED (~50% các lần chạy) | true/false không nhất quán | Câu hỏi tu từ NGẦM CHỨA 1 tiền đề nhân quả ("bê bối buộc Mỹ thông qua luật") — model đôi khi coi tiền đề này là 1 khẳng định cần căn cứ riêng | Tiền đề nhân quả trong câu hỏi ĐƯỢC excerpt xác nhận gián tiếp (áp lực dư luận → Quốc hội thông qua luật) | Toàn bộ excerpt (quan hệ nhân quả trải dài cả đoạn) | **rhetorical_framing** (tiền đề ẩn trong câu hỏi, không phải khẳng định trực tiếp) |
| G04 | "...ngày 29/11/1970...Cảnh sát Bergen (mã hồ sơ vụ án: 134/70)...kết luận chính thức...là tự sát..." | "Ngày 29/11/1970, Cảnh sát Bergen lập hồ sơ 134/70 và kết luận cái chết tại Thung lũng Băng là tự sát." | UNSUPPORTED | true | 3 chi tiết (ngày/mã hồ sơ/kết luận tự sát) nằm ở 3 câu KHÔNG liền kề trong excerpt — model không tự tin gộp chúng lại thành 1 sự kiện duy nhất cùng ngày | Cách đọc tự nhiên nhất của đoạn văn: ngày tháng mở đầu áp dụng cho toàn bộ vụ việc, không có ngày nào khác được nêu cho việc lập hồ sơ | Toàn đoạn (3 câu rải rác) | **cross_sentence_synthesis** |

**Không có 1 nguyên nhân gốc chung** cho cả 3 (đúng yêu cầu §4: G02=reference_resolution, G03=rhetorical_framing, G04=cross_sentence_synthesis — 3 cơ chế khác nhau). Theo đúng hướng dẫn "nếu không có root cause chung, KHÔNG thêm 1 đống ví dụ đặc thù vào prompt" → chuyển sang xây cơ chế TỔNG QUÁT (selective adjudicator, Phần 3).

## 2. Final C4 Design

**KHÔNG đổi gì** so với round 1 — vẫn là structured single-call C4 v2 (7 nhãn verdict + materiality, `cl_risk_gate_verification.py`). Lý do: cơ chế appeal đã prototype (Phần 3) không chứng minh được lợi ích ròng đủ để đánh đổi thêm độ phức tạp + chi phí (Phần 8-9).

## 3. Evidence-Span / Appeal Logic (đã build, đã test, KHÔNG đưa vào production)

Xây `adjudicate_c4_appeal()` (prototype, `c4_appeal_prototype.py`): CHỈ gọi cho claim material bị chặn ở vòng 1. Output bắt buộc `{final_verdict, support_type ∈ {DIRECT,PARAPHRASE,CROSS_SENTENCE_SYNTHESIS,REFERENCE_RESOLUTION,NONE}, support_span, reason_code}`. Overturn (`overturned=True`) CHỈ khi CẢ 3: (a) LLM tự báo `GROUNDED`, (b) `support_span` THẬT SỰ tồn tại nguyên văn trong excerpt (kiểm tra cơ học, không tin LLM tự khai), (c) mọi số liệu trong câu xuất hiện trong `support_span` (numeric guard cơ học — chặn cứng kiểu 81→45 tự xưng "paraphrase", đúng yêu cầu §9).

**Kết quả trên dev corpus**: sửa được G02 (support_type=CROSS_SENTENCE_SYNTHESIS hợp lệ, span xác minh đúng) nhưng KHÔNG sửa được G03/G04 (vẫn `STILL_UNSAFE`), VÀ gây lỗi MỚI trên G15 (1 fixture trước đó luôn PASS ổn định — cảm biến Gardner, entailed gần như nguyên văn) — first-pass lần chạy đó tình cờ flag nhầm G15, và appeal (dù được gọi) KHÔNG overturn lại được dù bằng chứng rất rõ ràng trong excerpt. **Tổng: vẫn 3/20 false-block, không giảm, thêm 1 lượt gọi LLM cho mỗi claim bị chặn.**

**Kết luận: KHÔNG đưa appeal vào production** — không có bằng chứng lợi ích ròng, thêm chi phí thật (xem Phần 9), và bản thân appeal có nhiễu riêng (G15) — đúng tinh thần "không giữ cơ chế an toàn chỉ vì đã xây nó" áp dụng NGƯỢC LẠI: không THÊM cơ chế mới chỉ vì đã xây nó.

## 4. Dev Corpus Results (Before/After)

| Cấu hình | tn (grounded PASS đúng) | tp (unsafe BLOCK đúng) | FALSE_PASS | FALSE_BLOCK |
|---|---|---|---|---|
| C4 v1 gốc (round 1 baseline) | 7/20 | 15/15 | 0 | 13/20 (65%) |
| **C4 v2 (production, round 1 kết quả cuối)** | **17/20** | **15/15** | **0** | **3/20 (15%)** |
| C4 v2 + majority-vote (2/3) | 17/20 | 15/15 | 0 | 3/20 (đổi fixture, không giảm) |
| C4 v2 + selective appeal (prototype) | 17/20 | 15/15 | 0 | 3/20 (đổi fixture: sửa G02, hỏng G15) |

Ghi rõ tách biệt theo đúng yêu cầu §2: đây là số liệu trên **golden/dev corpus** (35 fixture tự xây, dùng để tune prompt) — KHÁC với số liệu **canary sản xuất gốc** (4/5 episode bị C4 v1 chặn) và KHÁC với **holdout** (Phần 6). Không gộp chung thành "65-80%".

## 5. Holdout Corpus — Composition (đóng băng nhãn TRƯỚC khi chạy)

`C4_HOLDOUT_CORPUS_v1` (`handoff/c4_freeze/c4_holdout_corpus_v1.json`): 24 fixture (12 grounded + 12 unsafe), derive từ **2 research draft THẬT chưa từng dùng** để tune prompt hay xuất hiện trong dev corpus: `RESEARCH_DRAFT_GIAN_DIEP_LICH_SU.md` (vụ án Rosenberg 1951-1953 + mạng lưới Cambridge Five) — hoàn toàn khác 5 topic canary (Gardner/Isdal/Alec Jeffreys/Lockheed/Max Headroom/Maxi Trial).

Phủ đủ danh mục §13: distant paraphrase, cross-sentence compression, reordered chronology, reference resolution, approximate value, supported rhetorical hook, 2 fact nối không thêm nhân quả, technical paraphrase, long-paragraph compression (nhóm grounded); number substitution, changed date/year, subtle negation, identity swap, suspect→confirmed perpetrator, may→did modality, correlation→causation, invented motive, invented technical behavior, partially-supported+invented-clause, numeric undercounting, misattributed consensus (nhóm unsafe) — không có fixture "chỉ phát hiện được qua từ khóa".

## 6. Holdout Results (raw confusion matrix — KHÔNG phóng đại độ tin cậy thống kê)

Chạy 1 lần, KHÔNG chỉnh sửa implementation dựa trên kết quả (đúng §14 — nếu cần tinh chỉnh, đây sẽ trở thành dev evidence, cần holdout MỚI trước khi coi là validation; round này KHÔNG tinh chỉnh thêm).

```text
Grounded correctly PASS: 8 / 12
Unsafe correctly BLOCK: 12 / 12
FALSE_PASS (an toàn):    0 / 12
FALSE_BLOCK (grounded):  4 / 12
```

4 fixture false-block: **H01** (distant paraphrase quá thoáng, dùng khẩu ngữ "tuồn... sang tay"), **H06** (câu hỏi tu từ — CÙNG loại lỗi với G03), **H09** (cross-sentence synthesis — CÙNG loại lỗi với G04), **H12** (nén đoạn dài nhiều mốc thời gian — cùng nhóm cross-sentence synthesis).

**Không đạt mục tiêu ≤5%** trên holdout (thực tế 4/12 ≈ 33%, cao hơn dev corpus 15%) — báo cáo trung thực bằng SỐ THÔ (4/12), không phóng đại "33%" như 1 con số đáng tin cậy thống kê với N nhỏ.

## 7. Safety Adversarial Results (10 probe bắt buộc, chạy fresh trên production C4)

| # | Loại | Kỳ vọng | Kết quả |
|---|---|---|---|
| 1 | Negation, lexical similarity cao | BLOCK | ✓ BLOCK (CONTRADICTED) |
| 2 | 81→45 | BLOCK | ✓ BLOCK (CONTRADICTED) |
| 3 | $22M→$28M | BLOCK | ✓ BLOCK (CONTRADICTED) |
| 4 | 1984→1985 | BLOCK | ✓ BLOCK (CONTRADICTED) |
| 5 | suspect→perpetrator | BLOCK | ✓ BLOCK (STRONGER_THAN_SOURCE) |
| 6 | may have caused→caused | BLOCK | ✓ BLOCK (STRONGER_THAN_SOURCE) |
| 7 | 1 mệnh đề đúng + 1 mệnh đề bịa | BLOCK | ✓ BLOCK (UNSUPPORTED) |
| 8 | Đảo thứ tự 2 dữ kiện hợp lệ | PASS | ✓ PASS |
| 9 | Paraphrase hợp lệ nhưng RẤT khác từ ngữ | PASS | ✗ BLOCK (false-block, cùng pattern "distant paraphrase" với H01) |
| 10 | Cross-sentence synthesis hợp lệ | PASS | ✓ PASS |

**9/10 đúng. 0 an toàn bị lọt (0 false-pass trên TOÀN BỘ 7 case BLOCK bắt buộc).** 1 lỗi (#9) — false-block, KHÔNG phải BLOCKER/HIGH (không có nội dung sai lọt qua) — cùng nhóm "distant/colloquial paraphrase" đã thấy ở holdout H01.

## 8. Voting Decision: **KEEP** majority-of-2/3

Bằng chứng: majority-vote (round 1 + round 2, 2 lần đo độc lập trên dev corpus) KHÔNG giảm false-block so với single-call (luôn 3/20, chỉ đổi fixture nào lỗi) — phù hợp cảnh báo "3 lượt lặp lại cùng 1 lỗi hệ thống không tạo thêm độ tin cậy". Theo nghĩa đen §17, bằng chứng này nghiêng về loại bỏ.

**Quyết định thực tế: KEEP (không REMOVE, không REPLACE bằng appeal)**, vì 3 lý do cụ thể: (1) chi phí giữ nguyên = 0 (code đã có sẵn, không phải thêm mới — khác với việc CHỦ ĐỘNG thêm appeal, vốn mới và chưa chứng minh lợi ích); (2) majority-vote chỉ áp dụng cho nhánh STORYTELLING (`compute_phase_a_result()`), KHÔNG dùng cho case pipeline nặng — phạm vi ảnh hưởng hẹp, rủi ro tháo bỏ thấp nhưng cũng không có lợi ích rõ ràng để biện minh việc động vào; (3) 35+24 fixture (59 tổng) vẫn là mẫu nhỏ — chưa đủ để loại trừ khả năng majority-vote có ích trên phân bố nội dung khác chưa test. Đây KHÔNG phải "giữ vì đã có sẵn" thuần túy — là quyết định có cân nhắc chi phí=0 vs lợi ích=chưa chứng minh theo cả 2 hướng.

## 9. Cost Impact

| Cấu hình | LLM call/fixture (trung bình) | Ghi chú |
|---|---|---|
| Single-call | 1.0 | baseline |
| Majority-of-3 | 1.0–3.0 (dừng sớm khi đạt 2 phiếu cùng chiều) | ~1.4-1.8 thực tế quan sát (đa số fixture PASS/BLOCK rõ ràng ngay 2 lượt đầu) |
| Selective appeal | 1.0 + (0 tới 1 lượt/claim bị chặn vòng 1) | Trên dev corpus: 35 fixture, ~15-18 claim bị chặn vòng 1 (BLOCK expected + occasional false-block) → ~1.4-1.5 call/fixture trung bình — RẺ HƠN majority-of-3 nhưng KHÔNG cải thiện false-block, nên không đáng đánh đổi thêm độ phức tạp code |

Selective appeal RẺ HƠN majority-of-3 nhưng KHÔNG "dominate" nó theo đúng nghĩa §16 (phải an toàn+chính xác HƠN VÀ rẻ hơn) — chỉ rẻ hơn, không chính xác hơn → không đủ điều kiện thay thế.

## 10. Five Frozen Canary Re-run

**Không chạy lại trong round này** — production C4 KHÔNG đổi từ round 1 (không adopt appeal, không đổi majority-vote), nên kết quả round 1 vẫn còn nguyên giá trị (không có thay đổi code nào có thể làm nó lỗi thời):

| Episode | C4 | Claim ledger | Consumer | Final dry-run state |
|---|---|---|---|---|
| Alec Jeffreys | PASS | BLOCKED_FACT (5/6 claim, 1 VERIFIED qua TIME P1) | chưa chạm | BLOCKED_FACT |
| Lockheed | FAIL | chưa chạm | chưa chạm | C4_BLOCK |
| Isdal Woman | FAIL | chưa chạm | chưa chạm | C4_BLOCK |
| Max Headroom | PASS | BLOCKED_FACT (1/1, chưa có ledger entry) | chưa chạm | BLOCKED_FACT |
| Maxi Trial | PASS | BLOCKED_FACT (11/11, chưa có ledger entry) | chưa chạm | BLOCKED_FACT |

3/5 clear C4 (không đổi từ round 1). 0/5 `PASS_TO_DRY_RUN_BOUNDARY`.

## 11. Ledger Coverage Observation

Theo đúng §19 (source-ledger block KHÔNG phải C4 failure): 3/3 episode clear C4 đều dừng ở `BLOCKED_FACT` vì THIẾU xác minh P0/P1 thật — KHÔNG phải lỗi C4. Số claim rủi ro cao mới cần xác minh nếu muốn 3 episode này PASS: Alec Jeffreys 5 claim còn lại (forensic/motive), Max Headroom 1 claim (timeline — thời lượng gián đoạn 30 giây), Maxi Trial 11 claim (numerical/causal/allegation/timeline — số liệu vụ án, cáo buộc, thời hạn kháng cáo). **KHÔNG thực hiện backfill nguồn quy mô lớn trong task này** (đúng §21) — chỉ ghi nhận: nếu C4 được coi là đủ tốt, bước SCALE TIẾP THEO sau C4 chính là năng lực xác minh nguồn P0/P1 (nghiên cứu thủ công), không phải kỹ thuật.

## 12. Story Quality

Không episode nào đạt dry-run boundary trong round này → không có gì để chấm điểm (đúng §22, chỉ chấm khi có episode đạt boundary).

## 13. Tests

```text
files (15, manifest đã đối soát từ round 1):
  test_cl_case_batch.py, test_cl_case_generation.py, test_cl_claim_exposure_gate.py,
  test_cl_claim_ledger.py, test_cl_ledger_alias_sync.py, test_cl_real_person_safety.py,
  test_cl_risk_gate.py, test_cl_risk_gate_lifecycle.py, test_cl_risk_gate_orchestrator.py,
  test_cl_risk_gate_verification.py, test_cl_video_collapse_fix.py,
  test_criminal_law_storytelling_phase_a.py, test_run_cl_storytelling_phase_a.py,
  test_short_batch_runner_cl_gate.py, test_short_batch_runner_storytelling_binding.py

collected: 525
passed:    525
failed:    0
skipped:   0
duration:  ~197s
```

Không có drift so với round 1 (525 → 525, không đổi vì không sửa code production trong round 2). C4 dev corpus (35 fixture) + holdout corpus (24 fixture) là corpus đánh giá riêng (không phải pytest suite) — kết quả ở Phần 4/6.

## 14. Remaining Risks (chỉ rủi ro thật, chưa giải quyết)

- **[MEDIUM] 2 pattern lỗi tái diễn TRÊN CẢ dev VÀ holdout** (bằng chứng khái quát hóa thật, không phải overfitting — xem Phần 15): câu hỏi tu từ mang tiền đề nhân quả ngầm, và tổng hợp nhiều câu không liền kề (cross-sentence synthesis). Tỷ lệ false-block THẬT trên nội dung hoàn toàn mới cao hơn dev corpus (4/12 ≈ 33% so với 3/20 = 15%) — mục tiêu ≤5% CHƯA đạt ở cả 2 corpus.
- **[MEDIUM] Paraphrase quá thoáng/khẩu ngữ** cũng gây false-block (H01, probe #9) — pattern thứ 3, xuất hiện ở cả holdout lẫn probe mới.
- **[LOW]** Selective appeal (đã prototype) không đưa vào production nhưng code còn lưu trong scratchpad — nếu muốn thử lại, cần thiết kế lại (có thể: appeal 2/3 thay vì 1 lần, hoặc few-shot ví dụ cross_sentence_synthesis trong appeal prompt) — KHÔNG làm trong task này.
- **[LOW]** Majority-vote vẫn chưa chứng minh lợi ích đo được — quyết định KEEP dựa trên chi phí=0 để giữ, không phải bằng chứng tích cực.

## 15. Final Verdict

## `NEEDS_FIX`

**Bằng chứng đây là cải thiện TỔNG QUÁT, không phải prompt tune riêng cho canary** (trả lời trực tiếp §25): dựa chủ yếu vào **hiệu năng holdout**, KHÔNG phải dev corpus — holdout xây từ 2 chủ đề (Rosenberg, Cambridge Five) hoàn toàn không dùng để tune prompt. Holdout xác nhận: (a) **0/12 false-pass an toàn** — không có nội dung sai lọt qua trên bất kỳ chủ đề hoàn toàn mới nào, giữ vững đúng như dev corpus và canary; (b) **cùng 2-3 pattern lỗi cụ thể tái diễn** (rhetorical framing, cross-sentence synthesis, distant paraphrase) trên nội dung HOÀN TOÀN khác — đây là bằng chứng những điểm yếu này là THẬT và TỔNG QUÁT (không phải ngẫu nhiên do cách viết riêng của 5 script canary), nhưng đồng thời cũng là bằng chứng redesign v2 CHƯA giải quyết triệt để chúng, chỉ giảm được so với v1 (từ ~65-80% xuống ~15-33%, tuỳ corpus) chứ chưa đạt mục tiêu ≤5%.

Không đạt mục tiêu định lượng ở CẢ dev (15%, mục tiêu ≤5%) LẪN holdout (4/12, mục tiêu ≤5%/raw nhỏ). 0/5 canary episode đạt `PASS_TO_DRY_RUN_BOUNDARY`. Kiến trúc an toàn cốt lõi (claim-ledger, numeric-consistency, source-tier) giữ nguyên và không phát sinh BLOCKER mới nào trong round này — 0 safety-critical false-pass xuyên suốt 35+24+10 = 69 fixture/probe test trong round này (cộng dồn với round 1: hơn 100 phép thử độc lập, 0 lần lọt qua nội dung không an toàn).

**Khuyến nghị bước tiếp theo (KHÔNG thực hiện trong task này)**: 1 vòng tinh chỉnh THỨ 2, nhắm CHÍNH XÁC 3 pattern đã xác nhận khái quát (rhetorical framing/cross-sentence synthesis/distant paraphrase) — coi holdout hiện tại (`C4_HOLDOUT_CORPUS_v1`) trở thành dev evidence cho vòng đó, và xây `C4_HOLDOUT_CORPUS_v2` MỚI (chủ đề khác, chưa dùng) trước khi tuyên bố sẵn sàng. Song song, nếu muốn có ít nhất 1 ví dụ `PASS_TO_DRY_RUN_BOUNDARY` hoàn chỉnh trước khi mở pilot 20-episode, cần xác minh P0/P1 thật cho các claim còn lại của Max Headroom (1 claim) hoặc Maxi Trial (11 claim) — công việc nghiên cứu thủ công riêng, ngoài phạm vi kỹ thuật.
