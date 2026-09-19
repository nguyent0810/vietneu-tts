# C4 Repair — Báo cáo (follow-up cho 5-episode CL canary)

Ngày chạy: 2026-08-24. Git SHA nền: `027bd832ac682ff9071f1f8eb238feeb831ca2d3` (working tree, không đổi giữa lúc chạy). Ledger version cuối: `36a254300a01`.

**Kết luận cuối:** `NEEDS_FIX` — xem Phần 14.

Freeze trước khi sửa (§0 yêu cầu): git SHA, `git diff` tại thời điểm bắt đầu, C4 implementation/prompt gốc, 5 script/excerpt canary, toàn bộ evidence C4 gốc — lưu tại `handoff/c4_freeze/` (bao gồm `c4_golden_corpus_v1.json`).

---

## 1. C4 Contract

Đọc trực tiếp code + docstring (`cl_risk_gate_verification.py::_facts_block_for_draft`, viết TRƯỚC task này): *"C4/C7 chỉ kiểm tra draft có THÊM gì NGOÀI facts đã cho không — việc facts đã cho có đúng hay không là việc của C1/C2/C3 [case pipeline] / claim ledger [storytelling]."*

**Trả lời câu hỏi A/B/C/D:** Gần nhất với **C** (script không được thêm khẳng định thực chất mới ngoài dữ kiện đã cho) — KHÔNG phải A (không đòi literal textual presence — diễn giải lại hợp lệ) và KHÔNG hoàn toàn B (không phải full entailment-checking độc lập của mọi mệnh đề, C4 không tự xác minh dữ kiện gốc đúng hay sai).

**Phân biệt C4 vs claim ledger** (đúng như dự đoán trong yêu cầu task):
- **Claim ledger** (`cl_claim_ledger.py`): "Claim rủi ro cao NÀY có được xác minh ĐỘC LẬP bên ngoài (P0/P1) không?" — chỉ áp dụng cho nhóm rủi ro cao (forensic/security_system/motive/causal/allegation/legal_status + numeric/timeline material).
- **C4**: "Script có đưa vào 1 mệnh đề thực chất MỚI/mạnh hơn/mâu thuẫn so với chính đoạn trích nghiên cứu đã cho không?" — áp dụng cho MỌI mệnh đề thực chất, không giới hạn nhóm rủi ro cao, nhưng KHÔNG tự xác minh đoạn trích đó đúng thật ngoài đời hay không.

Ranh giới đã ghi rõ trong code (§10 yêu cầu task): C4 KHÔNG cần tái tạo lại full external fact verification — đó là việc của claim ledger.

## 2. Root Cause (4/5 episode canary bị false-block)

Đối chiếu 4 episode với evidence ĐÃ ĐÓNG BĂNG (`handoff/c4_freeze/`), phân loại theo đúng danh sách failure class yêu cầu:

| Episode | Câu bị chặn | Failure class |
|---|---|---|
| Lockheed (5 câu) | số liệu $, tên nước, hook question | **prompt ambiguity** (không phân biệt "khẳng định thiếu căn cứ" với câu hỏi tu từ/diễn giải lại) |
| Isdal Woman (3 câu) | ngày tháng, tự sát, podcast | **prompt ambiguity** (như trên) |
| Max Headroom (2 câu) | 15 giây/30 giây | **prompt ambiguity** + hedge-rounding (excerpt "khoảng 15 giây" → script "15 giây" bị coi mạnh hơn nguồn) |
| Maxi Trial (1-2 câu) | 475 thành viên, Palermo | **prompt ambiguity** |

**1 nguyên nhân gốc chung cho cả 4** (đúng câu hỏi §4 yêu cầu task): prompt C4 v1 hỏi "câu này có căn cứ TRỰC TIẾP không" cho MỌI câu, không phân biệt (a) diễn giải lại/nén câu hợp lệ, (b) câu hỏi tu từ/liên kết văn phong không chứa khẳng định gì, (c) làm tròn số liệu ước lượng thông thường ("khoảng X" → "X"). Không phải lỗi input-pipeline (đã kiểm tra §5, xem dưới), không phải lỗi voting-system, không phải parsing error.

## 3. Golden Corpus

35 fixture thật (20 grounded/PASS + 15 ungrounded/BLOCK), derive từ 5 script/excerpt canary + ledger Gardner có sẵn + 2 bug lịch sử thật (Gardner sensor-evasion, Gardner 81→45 phút) + biến thể adversarial mới. File: `handoff/c4_freeze/c4_golden_corpus_v1.json`.

Phân loại đầy đủ theo yêu cầu §3: exact restatement, paraphrase, compression, reordered, pronoun/reference, harmless connective, combined facts (nhóm grounded); new numerical, altered numerical, invented motive, invented emotion, unsupported causal, allegation→confirmed, suspect→perpetrator, may/might→definitely, negated fact, source contradiction, invented technical behavior (nhóm ungrounded).

**Phát hiện phụ quan trọng khi xây corpus**: vòng đầu (v1) dùng excerpt bị cắt xén ("...") cho 1 số fixture (G04/G06/G09/G12/G13) — tự gây false-block KHÔNG PHẢI do C4 mà do lỗi soạn fixture (thiếu ngữ cảnh/tiền đề mà script phụ thuộc). Đã sửa sang excerpt ĐẦY ĐỦ thật (khớp đúng nội dung production pipeline THẬT sẽ đưa cho C4) — bài học: golden corpus phải dùng chính xác input thật, không tóm tắt.

## 4. Before/After C4 Metrics (confusion matrix thật, single-call)

| Version | Grounded PASS đúng (tn) | Ungrounded BLOCK đúng (tp) | FALSE_PASS (an toàn) | FALSE_BLOCK |
|---|---|---|---|---|
| C4 v1 (gốc, single-call) | 7/20 | 15/15 | **0** | 13/20 (65%) |
| C4 v2, corpus v1 chưa sửa excerpt (single-call) | 8/20 → 14/20 (2 vòng prompt refine) | 15/15 | **0** | 12→6/20 |
| **C4 v2, corpus đã sửa excerpt đầy đủ (single-call)** | **17/20** | **15/15** | **0** | **3/20 (15%)** |
| C4 v2, majority-vote (2/3) | 17/20 | 15/15 | **0** | 3/20 (đổi fixture, KHÔNG giảm số lượng) |

**Majority-vote KHÔNG cải thiện** trên golden corpus này (vẫn 3/20 cả 2 cách) — đúng cảnh báo §7/§8 yêu cầu task: 3 lỗi còn lại (rhetorical-question materiality, 1-2 paraphrase biên) là thiên lệch hệ thống, không phải nhiễu ngẫu nhiên majority-vote lọc được. **Quyết định: giữ nguyên majority-vote wrapper đã có** (`compute_phase_a_result()`, không đổi) vì không có bằng chứng nó gây hại, chỉ đổi prompt/scoring bên trong — thay đổi tối thiểu.

**Không đạt mục tiêu ≤5%** (còn 15%) — ghi rõ, không giấu. Xem Phần 13.

## 5. C4 Patch

File: `cl_risk_gate_verification.py`. Thay `_C4_ADVERSARIAL_PROMPT` (binary PASS/FAIL toàn văn bản) bằng phiên bản structured claim-level: LLM trả `{"claims": [{"sentence", "verdict" (1/7 nhãn: ENTAILED/SUPPORTED_PARAPHRASE/HARMLESS_NARRATIVE/UNSUPPORTED/CONTRADICTED/STRONGER_THAN_SOURCE/UNCERTAIN), "materiality": bool, "reason"}]}`. `_score_c4_adversarial_text()` tính `passed` THUẦN CƠ HỌC (không tin verdict tổng do LLM tự claim): FAIL chỉ khi ≥1 câu `materiality=true` VÀ verdict ∈ {UNSUPPORTED, CONTRADICTED, STRONGER_THAN_SOURCE, UNCERTAIN}. Thêm quy tắc làm tròn số liệu (excerpt "khoảng X" → script "X" là SUPPORTED_PARAPHRASE, không phải STRONGER_THAN_SOURCE) + quy tắc đối chiếu số/tên trước khi gán CONTRADICTED + chỉ dẫn không tách nhỏ câu quá mức.

**Chữ ký hàm KHÔNG đổi** (`_score_c4_adversarial_text(draft, candidate) -> CriterionResult`) — mọi caller hiện có (`score_c4_adversarial()`, `compute_phase_a_result()`'s majority loop, case pipeline Stage 2) không cần sửa. Test cập nhật: `test_cl_risk_gate_verification.py` (schema mock mới, +3 test case mới cho validation cơ học).

## 6. Alec Jeffreys Source Decision

Canary trước kết luận `BLOCKED_FACT` cho cả 5 claim vì P0 (le.ac.uk) bị WebFetch chặn 403. Theo đúng chính sách thật (`_P0_P1_TIERS = (REPUTABLE_PRESS, PUBLIC_RECORD)` — P0 HOẶC P1), việc đó **quá vội** cho claim "duy nhất trừ song sinh cùng trứng" — tìm thấy **TIME Magazine** ("Science: DNA Prints", 26/1/1987, `time.com` — đã có sẵn trong allowlist REPUTABLE_PRESS) với trích dẫn nguyên văn xác nhận claim này. Đã thêm entry ledger thật `JEFFREYS_DNA_FINGERPRINT_UNIQUE_EXCEPT_TWINS` (P1, TIME) cho topic `RESEARCH_DRAFT_KHOA_HOC_PHAP_Y_MO_RONG`.

**Kết quả đối với 5 claim gốc:**

| Claim | Trạng thái trước | Trạng thái sau | Đánh giá |
|---|---|---|---|
| "...trừ song sinh cùng trứng...duy nhất..." | BLOCKED (TOO_STRICT) | **VERIFIED** (P1 TIME) | TOO_STRICT — đã sửa |
| "Alec Jeffreys chọn nghiên cứu DNA biến đổi" | BLOCKED | BLOCKED | CORRECT/UNRESOLVED — thử nhiều truy vấn báo chí thật, không tìm được reputable-press đủ chi tiết |
| "Tấm phim X-quang...dấu vân tay" | BLOCKED | BLOCKED | CORRECT/UNRESOLVED (như trên) |
| "VNTR độ dài khác biệt" | BLOCKED | BLOCKED | CORRECT/UNRESOLVED (như trên) |
| "Mô hình vạch mang tính gia đình + phân định từng người" | BLOCKED | BLOCKED | CORRECT/UNRESOLVED (như trên) |

**Không fabricate provenance** cho 4 claim còn lại — nguồn P0 thật (Đại học Leicester) vẫn bị 403; các nguồn khoa học-sử khác tìm được (yourgenome.org, PNAS, NIH) xếp `aggregator` theo đúng tiền lệ đã có (`cambridge.org`/`science.org` cũng `aggregator`), không đủ điều kiện P0/P1. Episode vẫn `BLOCKED_FACT` hợp lệ (5/6 claim chưa xác minh) — KHÔNG phải lỗi.

## 7. Numeric Regression

Đã có sẵn từ pilot trước (81→45 phút, BLOCKER thật đã vá) + bổ sung 2 case theo đúng yêu cầu §12:

- `test_numeric_tokens_mismatch_true_when_dollar_amount_differs`: "22 triệu USD" vs "28 triệu USD" → `True` (BLOCK).
- `test_numeric_tokens_mismatch_true_when_year_differs`: "năm 1984" vs "năm 1985" → `True` (BLOCK).
- Xác nhận THÊM qua C4 THẬT (không chỉ claim-ledger): probe trực tiếp "10/9/1984" → "10/9/1985" bị C4 gán `CONTRADICTED`, BLOCK đúng.

Không làm hồi quy paraphrase số liệu hợp lệ (test `test_numeric_tokens_mismatch_false_when_number_matches` vẫn pass).

## 8. Five Canary Re-run (script/excerpt ĐÓNG BĂNG, KHÔNG sinh lại)

| Episode | C4 (trước vá) | C4 (sau vá) | Ledger (nếu qua C4) |
|---|---|---|---|
| Alec Jeffreys | PASS (đã qua) | PASS | BLOCKED_FACT 5/6 (1 claim VERIFIED mới -- Phần 6) |
| Lockheed | FAIL (5 câu) | **FAIL (1-3 câu, đa số 2/2)** | chưa chạm tới |
| Isdal Woman | FAIL (3 câu) | **FAIL (1-2 câu, đa số 2/2)** | chưa chạm tới |
| Max Headroom | FAIL (2 câu) | **PASS** ✓ | BLOCKED_FACT 1/1 (chưa có ledger entry) |
| Maxi Trial | FAIL (1-2 câu) | **PASS** ✓ | BLOCKED_FACT 11/11 (chưa có ledger entry) |

**3/5 clear C4** (tăng từ 1/5) — cải thiện thật, đo được trên chính 5 episode canary thật, không chỉ trên golden corpus tổng hợp.

## 9. Full Dry-run Outcomes

| Episode | Điểm dừng cuối | Sidecar? |
|---|---|---|
| Alec Jeffreys | BLOCKED_FACT (ledger) | Không |
| Lockheed | C4_BLOCK | Không |
| Isdal Woman | C4_BLOCK | Không |
| Max Headroom | BLOCKED_FACT (ledger) | Không |
| Maxi Trial | BLOCKED_FACT (ledger) | Không |

0/5 `PASS_TO_DRY_RUN_BOUNDARY`. 5/5 không có sidecar → consumer (`short_batch_runner.py`) sẽ đánh dấu `needs_review`, KHÔNG tự động publish (xác nhận lại behavior đã kiểm chứng ở pilot trước).

## 10. Story Quality Observation

Không có episode nào PASS hoàn toàn qua mọi gate để đánh giá "chất lượng có bị giữ nguyên khi qua được gate không" một cách đầy đủ. Quan sát gián tiếp: C4 v2 hoạt động THUẦN TÚY như 1 bộ lọc nhị phân trên script GỐC — không hề sửa/viết lại nội dung script ở bất kỳ bước nào (đúng yêu cầu "we want to know whether factual gates permit the existing quality through", không tối ưu hóa văn bản). 2 episode giờ qua được C4 (Max Headroom, Maxi Trial) giữ nguyên 100% nội dung/văn phong đã tạo trong canary trước — chất lượng câu chuyện (hook, nhịp, last line) không đổi.

## 11. Test Manifest Reconciliation

```text
previous suite files (báo cáo trước, 15 file):
  test_cl_case_batch.py, test_cl_case_generation.py, test_cl_claim_exposure_gate.py,
  test_cl_claim_ledger.py, test_cl_ledger_alias_sync.py, test_cl_real_person_safety.py,
  test_cl_risk_gate.py, test_cl_risk_gate_lifecycle.py, test_cl_risk_gate_orchestrator.py,
  test_cl_risk_gate_verification.py, test_cl_video_collapse_fix.py,
  test_criminal_law_storytelling_phase_a.py, test_run_cl_storytelling_phase_a.py,
  test_short_batch_runner_cl_gate.py, test_short_batch_runner_storytelling_binding.py
  => 516 passed

current suite run (pilot report trước, LỖI THỰC THI):
  14/15 file trên -- VÔ TÌNH BỎ SÓT test_short_batch_runner_cl_gate.py khi gõ lệnh
  => 503 passed

added files: (không có file mới bị thêm nhầm)
removed files: test_short_batch_runner_cl_gate.py (bỏ sót, KHÔNG chủ đích)
test-count delta: 516 - 503 = 13 = ĐÚNG BẰNG số test trong test_short_batch_runner_cl_gate.py
reason: lỗi copy-paste danh sách file khi chạy lệnh, KHÔNG phải hồi quy thật.
  "503 passed" trong báo cáo canary trước KHÔNG PHẢI bằng chứng đầy đủ "0 hồi quy" --
  đã bị coi là vậy trong báo cáo đó, nay đính chính.

authoritative reconciled manifest (15 file, SAU khi vá C4 + thêm test mới):
  cùng 15 file trên
  => 525 passed, 0 failed, 0 skipped, ~192s
  (521 trước khi thêm 4 test C4-schema mới trong bước vá; +4 = 525, khớp)
```

Không còn drift chưa giải thích.

## 12. Adversarial Review (patched C4)

Tấn công qua golden corpus (15 fixture ungrounded, nhiều vòng single+majority) + 2 probe mới trực tiếp (changed year, modality escalation "có thể" → "đã khiến"):

| Loại tấn công | Nguồn test | Kết quả |
|---|---|---|
| Negation tinh vi | B09 + canary negative control | BLOCK đúng |
| Đổi số liệu | B02, B10 + probe mới ($ , năm) | BLOCK đúng |
| Đổi năm/ngày | probe mới (1984→1985) | BLOCK đúng (CONTRADICTED) |
| suspected→confirmed | B06, B07 | BLOCK đúng |
| may/might→definitely | probe mới ("có thể"→"đã khiến") | BLOCK đúng (STRONGER_THAN_SOURCE) |
| person A→person B | B12 (Dan Roan→Walter Jacobson) | BLOCK đúng |
| nhân quả bịa "vì vậy" | B05 | BLOCK đúng |
| paraphrase đúng, từ ngữ rất khác | G01,G02,G09,G19 (nhiều) | PASS đúng |
| đảo thứ tự 2 dữ kiện | G13, G20 | PASS đúng |
| nén nhiều câu | G02, G19 | PASS đúng |

**0 BLOCKER, 0 HIGH** — không có false-pass an toàn nào trong TOÀN BỘ quá trình test (35 fixture × nhiều vòng + 5 episode canary re-run thật + 2 probe mới). **MEDIUM**: tỷ lệ false-block grounded vẫn 15% (mục tiêu ≤5% chưa đạt) — xem Phần 13.

## 13. Remaining Risks

- **[MEDIUM] False-block 15% trên golden corpus, chưa đạt mục tiêu ≤5%.** Còn 3 pattern cụ thể: (a) câu hỏi tu từ mở đầu đôi khi vẫn bị gán materiality=true/STRONGER_THAN_SOURCE (nhiễu ~50%, chưa hệ thống hóa được lý do); (b) 1-2 câu paraphrase biên (VD ngày/hồ sơ cảnh sát) thỉnh thoảng bị coi UNSUPPORTED dù đối chiếu tay xác nhận đúng nguồn. 2/5 episode canary thật (Lockheed, Isdal Woman) vẫn KHÔNG qua được C4 sau vá.
- **[MEDIUM, đã biết từ trước, KHÔNG đổi]** Negation vẫn PASS ở đường consumer-only (sidecar giả tay) — phòng tuyến thật nằm ở producer (đã xác nhận hoạt động đúng qua canary trước + lần này).
- **[LOW]** Majority-vote hiện không chứng minh được lợi ích đo được trên golden corpus — giữ nguyên vì không gây hại, nhưng nên theo dõi thêm nếu chi phí/latency trở thành vấn đề thật ở quy mô lớn.
- **[LOW]** 4/5 claim Alec Jeffreys còn lại + hầu hết claim Max Headroom/Maxi Trial vẫn cần xác minh P0/P1 thật trước khi các episode này có thể PASS -- công việc nghiên cứu thủ công riêng, ngoài phạm vi task này.

## 14. Final Verdict

## `NEEDS_FIX`

Lý do: cải thiện THẬT và đo được (tỷ lệ qua C4 trên 5 canary episode: 1/5 → 3/5; false-block trên golden corpus: 65% → 15%; 0 safety-critical false-pass xuyên suốt), nhưng **chưa đạt mục tiêu định lượng ≤5% false-block** đã đặt ra, và **0/5 episode canary đạt PASS_TO_DRY_RUN_BOUNDARY** hoàn toàn (2/5 vẫn kẹt ở C4, 3/5 kẹt ở ledger vì thiếu xác minh P0/P1 thật -- không phải lỗi kỹ thuật, là công việc nghiên cứu chưa làm).

**Khuyến nghị bước tiếp theo (KHÔNG thực hiện trong task này)**: 1 vòng tinh chỉnh hẹp, có kiểm soát nhắm đúng 2 pattern còn lại (câu hỏi tu từ + paraphrase biên ngày/hồ sơ) bằng thêm ví dụ cụ thể vào prompt, đo lại trên ĐÚNG golden corpus này (không mở rộng phạm vi) trước khi coi C4 đã đạt chuẩn 20-episode pilot. Song song: xác minh P0/P1 thật cho 4 claim Alec Jeffreys còn lại + toàn bộ claim Max Headroom/Maxi Trial nếu muốn có ít nhất 1 ví dụ PASS_TO_DRY_RUN_BOUNDARY hoàn chỉnh trước khi mở pilot 20-episode.
