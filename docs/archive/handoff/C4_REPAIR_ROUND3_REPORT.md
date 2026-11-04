# C4 Repair — Round 3 (claim-centric hypothesis test, majority-vote decision, holdout v2)

Ngày chạy: 2026-08-25. Git SHA nền: `027bd832ac682ff9071f1f8eb238feeb831ca2d3`. Thay đổi code trong round này: bỏ đa số 2/3 khỏi `criminal_law_storytelling_phase_a.py::compute_phase_a_result()` (C4 giờ 1 lượt gọi duy nhất) + test tương ứng. **Prompt/logic C4 (`_score_c4_adversarial_text`, `cl_risk_gate_verification.py`) KHÔNG đổi từ round 1/2.**

**Kết luận cuối:** `NEEDS_FIX` — xem Phần 16. Bằng chứng round này NẶNG HƠN, không nhẹ hơn round 2.

Kiến trúc an toàn cốt lõi (claim-ledger producer/consumer, numeric-token consistency, source-tier policy, post-rewrite verification) **giữ nguyên, không đổi**, không phát sinh BLOCKER mới đòi hỏi sửa các hệ thống đó.

**Ghi chú ngôn ngữ báo cáo (đã sửa theo yêu cầu):** dev corpus, holdout, adversarial probe, và canary re-run được báo cáo TÁCH BIỆT, KHÔNG gộp chung thành 1 con số thống kê giả định. Dùng "N trường hợp/probe đã đánh giá", không dùng "N phép thử độc lập" trừ khi độc lập thật sự được xác lập.

---

## 1. Architectural Diagnosis

C4 v2 (round 1/2) phán đoán ở cấp độ CÂU (sentence-level). Giả thuyết trung tâm round này: đơn vị phán đoán quá gần với hình thức bề mặt của câu (chứa khung tu từ, đại từ, nén nhiều ý, tổng hợp không liền kề) trong khi mệnh đề thực chất bên dưới vẫn được căn cứ hỗ trợ đầy đủ — nên chuyển sang đơn vị MỆNH ĐỀ NGUYÊN TỬ (atomic material proposition) có thể giải quyết được.

**Giả thuyết đã bị BÁC BỎ bằng bằng chứng thật** (xem Phần 4) — không giả định thắng, đã prototype và đo trước khi kết luận, đúng yêu cầu.

## 2. Claim-Centric Prototype (Mode B)

Xây `_score_c4_claim_centric_text()` (`c4_claim_centric_prototype.py`): 1 lượt gọi LLM duy nhất, 2 bước NỘI BỘ trong CÙNG 1 prompt — (1) tách bản nháp thành mệnh đề nguyên tử (câu hỏi tu từ được chuẩn hóa thành tiền đề), (2) với MỖI mệnh đề, đối chiếu CĂN CỨ cho phép NHIỀU đoạn trích rời rạc (`evidence_spans[]`, hỗ trợ `CROSS_SENTENCE_SYNTHESIS`). Xác minh cơ học: mọi `evidence_spans` phải tồn tại nguyên văn trong excerpt (không tin LLM tự khai) + numeric guard (số trong mệnh đề phải khớp số trong evidence_spans).

## 3. Reuse of Existing Claim Infrastructure

Đã KHÔNG tạo `c4_claim_extractor.py` riêng — tái dùng `_facts_block_for_draft()`, `_run_codex`, `_extract_json` có sẵn (`cl_risk_gate_verification.py`). Đã CÂN NHẮC nhưng KHÔNG tái dùng `cl_claim_ledger.py`'s `classify_high_risk_claims()` làm cơ chế trích mệnh đề cho C4 (đúng lý do §6 yêu cầu task): hàm đó CHỈ trích claim thuộc nhóm rủi ro cao (forensic/security_system/motive/causal/allegation/legal_status + numeric/timeline material) — C4 cần MỌI mệnh đề thực chất, kể cả loại không rủi ro cao (vd "căn phòng đã trống"). Dùng chung filter rủi ro cao của ledger làm phạm vi C4 sẽ THU HẸP sai phạm vi C4. Kết luận: 2 khái niệm "material claim" (C4) và "high-risk claim" (ledger) có phạm vi khác nhau có chủ đích, không nên gộp cơ chế trích xuất -- xem thêm Phần 13 (đánh giá khả năng tích hợp, KHÔNG triển khai).

## 4. Candidate Comparison (Mode A vs Mode B, trên `C4_DEV_CORPUS_v1`)

| Mode | Grounded PASS đúng | Ungrounded BLOCK đúng | FALSE_PASS | FALSE_BLOCK |
|---|---|---|---|---|
| **A — structured single-call (production, không đổi)** | **17/20** | **15/15** | **0** | **3/20 (15%)** |
| B — claim-centric single-pass (prototype) | 15/20 | 15/15 | 0 | 5/20 (25%) |

Mode B KHÔNG sửa được G02/G03/G04 (vẫn lỗi, G04 còn bị tách thành 4 mệnh đề nhỏ, 2/4 bị gán sai UNCERTAIN/UNSUPPORTED dù nội dung trực tiếp có trong excerpt) VÀ gây lỗi MỚI trên G13 (twins-exception claim) + G15 (Gardner sensor claim) -- 2 fixture trước đó PASS ổn định qua nhiều vòng test. Cơ chế nghi ngờ: tách mệnh đề nguyên tử làm TĂNG số điểm phán đoán trên mỗi câu -- 1 câu bị chặn khi CHỈ 1 trong N mệnh đề con bị đánh giá sai, nên càng tách nhỏ càng tăng khả năng có ít nhất 1 mệnh đề bị phán sai. **Không xây/test Mode C** (extract-rồi-entailment 2 giai đoạn, chi phí cao hơn): vì cơ chế gốc gây lỗi ở Mode B (tách càng nhỏ càng tăng bề mặt lỗi) không phụ thuộc số giai đoạn gọi LLM -- không có lý do tin Mode C sẽ khá hơn, và mỗi mệnh đề cần 1 lượt entailment riêng sẽ tốn N+1 lượt gọi/script (rất tốn kém). Quyết định này ghi minh bạch, không lặng lẽ bỏ qua.

**Mode A vẫn là thiết kế production cuối cùng — Mode B KHÔNG được đưa vào production.**

## 5. Voting Decision: **REMOVE**

Sửa lại kết luận round 2 ("giữ vì chi phí=0") — SAI về mặt vận hành (đúng như user chỉ ra): đa số 2/3 tốn THÊM 1-3 lượt gọi LLM thật mỗi episode, có chi phí thật (tiền/thời gian/độ trễ), không phải 0. Với 2 lần đo độc lập (round 2: 3/20 cả 2 cách; round 3 gián tiếp qua Mode A giữ nguyên) xác nhận đa số 2/3 KHÔNG giảm false-block trên golden corpus — mặc định phải là REMOVE khi không có lợi ích đo được. **Đã triển khai thật**: bỏ vòng lặp đa số trong `compute_phase_a_result()` (`criminal_law_storytelling_phase_a.py`), thay bằng 1 lượt gọi C4 duy nhất. Cập nhật 3 test cũ (`test_c4_majority_recovers_from_single_transient_fail`, `test_c4_fails_closed_when_majority_of_independent_passes_fail`, `test_c4_stops_early_when_first_two_passes_succeed`) thành 2 test mới (`test_c4_single_call_pass`, `test_c4_single_call_fail_closed`).

## 6. Development Results

`C4_DEV_CORPUS_v1` (35 fixture, đã tune prompt round 1/2): Mode A 17/20 (15% false-block), Mode B 15/20 (25% false-block) — xem Phần 4.

`C4_HOLDOUT_CORPUS_v1` (24 fixture, Rosenberg/Cambridge Five — theo đúng §18, giờ coi là DEV EVIDENCE, KHÔNG còn hợp lệ làm holdout cuối vì đã bị inspect/dùng để định hướng redesign round này): kết quả round 2 (Mode A, chưa đổi): 8/12 PASS (33% false-block), 12/12 BLOCK đúng, 0 false-pass.

## 7. New Blind Holdout (v2)

`C4_HOLDOUT_CORPUS_v2` (`handoff/c4_freeze/c4_holdout_corpus_v2.json`): 30 fixture (15 grounded + 15 unsafe), derive từ 2 research draft THẬT hoàn toàn chưa dùng ở bất kỳ round nào: `RESEARCH_DRAFT_KET_AN_OAN_SAI.md` (Ronald Cotton/Jennifer Thompson, Kirk Bloodsworth — phong trào Innocence Project) và `RESEARCH_DRAFT_TOI_PHAM_NGHE_THUAT.md` (Han van Meegeren, Wolfgang Beltracchi — tội phạm nghệ thuật). KHÔNG dùng Gardner/Isdal/Alec Jeffreys/Lockheed/Max Headroom/Maxi Trial (dev) VÀ KHÔNG dùng Rosenberg/Cambridge Five (holdout v1, đã burned). Mỗi fixture ghi rõ ID/topic/excerpt/sentence/expected/category TRƯỚC khi chạy Mode A — không sửa nhãn sau khi thấy kết quả.

## 8. Blind Holdout Results (raw, KHÔNG tuning thêm)

```text
Grounded correctly PASS: 8 / 15
Unsafe correctly BLOCK: 15 / 15
FALSE_PASS (an toàn):    0 / 15
FALSE_BLOCK (grounded):  7 / 15
```

7 fixture false-block: N02 (cross-sentence synthesis), N04 (paraphrase biên/tăng mức độ chắc chắn -- có thể tranh cãi, xem ghi chú), N05 (câu hỏi tu từ — lần đầu ghi ContentSeoError [lỗi hạ tầng thoáng qua], CHẠY LẠI xác nhận vẫn UNSUPPORTED thật, không phải nhiễu hạ tầng), N09 (cross-sentence synthesis), N12 (paraphrase xa), N13 (giữ ĐÚNG hedge "một số lượng lớn" như excerpt khuyến nghị, vẫn bị chặn), N15 (paraphrase kỹ thuật pháp y, khá sát nghĩa).

**KHÔNG đạt mục tiêu ≤5%** — thực tế 47% (7/15), CAO HƠN cả dev corpus (15%) LẪN holdout v1 (33%). Xu hướng 3 phép đo liên tiếp (15% → 33% → 47%) trên nội dung ngày càng mới cho thấy con số dev-corpus 15% có khả năng bị lạc quan hóa do trùng lặp phong cách với chính nội dung đã dùng để tune prompt — hiệu năng THẬT trên nội dung hoàn toàn mới nhiều khả năng nằm trong khoảng 30-50%, không phải 15%.

**Đúng yêu cầu §14/§20 (không lặng lẽ tinh chỉnh thêm dựa trên holdout thất bại)**: KHÔNG sửa prompt C4 dựa trên 7 case này trong task này. Nếu muốn thử vá tiếp, corpus này (`C4_HOLDOUT_CORPUS_v2`) trở thành dev evidence, cần xây `C4_HOLDOUT_CORPUS_v3` MỚI trước khi công bố đã validate.

## 9. Failure-Family Results (tổng hợp 3 corpus)

| Failure family | Dev v1 (15% tổng) | Holdout v1 (33% tổng) | Holdout v2 (47% tổng) | Kết luận |
|---|---|---|---|---|
| Rhetorical framing/tiền đề ẩn | G03 | H06 | N05, probe#2 (fresh) | **Xác nhận 4 lần độc lập trên 4 bộ dữ liệu khác nhau — điểm yếu TỔNG QUÁT, không phải overfitting** |
| Cross-sentence synthesis | G04 | H09, H12 | N02, N09 | Xác nhận nhiều lần, tổng quát |
| Distant/paraphrase quá thoáng | (nhẹ, G02 biên) | H01, probe#9 (round 2) | N04, N12, N15 | Xác nhận nhiều lần, tổng quát |
| Approximate value/hedge | — | — | N13 (giữ đúng hedge vẫn lỗi) | **Phát hiện MỚI round này** — trước đây tưởng đã giải quyết (quy tắc làm tròn số trong prompt), nhưng vẫn lỗi khi hedge được GIỮ NGUYÊN đúng khuyến nghị nguồn |

## 10. Safety Results (10 required + 14 required round này)

0 false-pass an toàn trên MỌI corpus/probe round này: dev (0/15 unsafe), holdout v1 (0/12, dữ liệu round 2), holdout v2 (0/15), 14 probe adversarial mới (13/14 đúng — 10/10 case BLOCK bắt buộc đều đúng, 1 case PASS bị false-block cùng pattern rhetorical framing). Cộng dồn cả 3 round: **0 false-pass an toàn** trên mọi corpus/probe đã chạy (dev+holdout v1+holdout v2+mọi round adversarial probe) — property an toàn cốt lõi giữ vững xuyên suốt, dù property "không làm phiền storytelling hợp lệ" chưa đạt.

## 11. Cost

Mode A: 1 lượt gọi/fixture (đã bỏ đa số). Mode B: 1 lượt gọi/fixture (cùng chi phí danh nghĩa với Mode A per-call, nhưng chính xác THẤP HƠN — không đáng đánh đổi). Đa số 2/3 (đã bỏ): 1-3 lượt/episode tùy kết quả — tiết kiệm được ~40-80% lượt gọi C4 so với trước, không giảm chất lượng đo được.

## 12. Five Frozen Canary Re-run

**KHÔNG chạy lại** — đúng §25/§19: chỉ chạy lại khi holdout MỚI đạt acceptance. Holdout v2 KHÔNG đạt (47% false-block, mục tiêu ≤5%) — dữ liệu round 2 (3/5 clear C4, 0/5 đạt `PASS_TO_DRY_RUN_BOUNDARY`) vẫn là kết quả canary gần nhất, với lưu ý: việc bỏ đa số 2/3 round này CHƯA được kiểm chứng lại trên chính 5 episode canary (thay đổi hành vi thật, dù dựa trên bằng chứng vững).

## 13. Downstream Ledger / Integration Observation

Không chạy lại canary nên không có số liệu MỚI về claim chặn sau C4 round này — dữ liệu round 2 (Alec Jeffreys 5 claim, Max Headroom 1 claim, Maxi Trial 11 claim cần xác minh P0/P1) vẫn là ước tính gần nhất. **Về khả năng tích hợp C4↔ledger (§26 yêu cầu task)**: XÁC NHẬN CHƯA khả thi/nên làm — 2 khái niệm "material claim" (C4, phạm vi RỘNG) và "high-risk claim" (ledger, phạm vi HẸP có chủ đích) không trùng nhau, gộp chung sẽ làm hỏng phạm vi 1 trong 2 bên (xem Phần 3). KHÔNG triển khai trong task này.

## 14. Test Results

```text
files (15, không đổi từ round 1/2):
  test_cl_case_batch.py, test_cl_case_generation.py, test_cl_claim_exposure_gate.py,
  test_cl_claim_ledger.py, test_cl_ledger_alias_sync.py, test_cl_real_person_safety.py,
  test_cl_risk_gate.py, test_cl_risk_gate_lifecycle.py, test_cl_risk_gate_orchestrator.py,
  test_cl_risk_gate_verification.py, test_cl_video_collapse_fix.py,
  test_criminal_law_storytelling_phase_a.py, test_run_cl_storytelling_phase_a.py,
  test_short_batch_runner_cl_gate.py, test_short_batch_runner_storytelling_binding.py

collected: 524
passed:    524
failed:    0
skipped:   0
duration:  ~191s
```

Delta so với round 2 (525 → 524, -1): ĐÃ GIẢI THÍCH ĐẦY ĐỦ -- thay 3 test đa số 2/3 cũ bằng 2 test single-call mới (net -1), không có drift ngoài dự kiến.

## 15. Remaining Risks

- **[HIGH — nâng cấp từ MEDIUM round 2]** False-block trên nội dung thật, hoàn toàn mới có xu hướng TĂNG DẦN qua 3 phép đo liên tiếp (15% → 33% → 47%), KHÔNG giảm/ổn định. Bằng chứng round này cho thấy con số dev-corpus 15% không đại diện cho hiệu năng thật trên nội dung production đa dạng — rủi ro thật: ở quy mô 20 episode, PHẦN LỚN (không chỉ thiểu số) episode có khả năng bị chặn nhầm ít nhất 1 câu, đòi hỏi review thủ công quy mô lớn hơn nhiều so với ước tính trước đây.
- **[MEDIUM]** 4 pattern lỗi cụ thể giờ đã xác nhận nhiều lần, tổng quát, KHÔNG phải overfitting: rhetorical framing (4 lần), cross-sentence synthesis (4 lần), distant paraphrase (5 lần), approximate-value/hedge (phát hiện mới, 1 lần — cần thêm dữ liệu để xác nhận tổng quát).
- **[MEDIUM]** Giả thuyết kiến trúc chính của round này (chuyển đơn vị phán đoán xuống mệnh đề nguyên tử) đã bị bác bỏ bằng bằng chứng thật — cần hướng tiếp cận KHÁC (không phải chỉ tinh chỉnh prompt thêm, không phải tách nhỏ hơn) cho vòng sửa tiếp theo, có khả năng cần: ví dụ few-shot cụ thể cho 4 pattern đã xác nhận, HOẶC chấp nhận tỷ lệ false-block cao hơn dự kiến ban đầu và xây quy trình review thủ công hiệu quả thay vì tiếp tục tối ưu thuật toán.
- **[LOW]** Việc bỏ đa số 2/3 (thay đổi thật round này) chưa được kiểm chứng lại trên 5 episode canary thật — nên làm ở vòng tiếp theo trước khi coi là đã xác nhận đầy đủ trên production path.

## 16. Final Verdict

## `NEEDS_FIX`

Round này đóng góp 2 kết quả thật, có giá trị: (1) **bác bỏ dứt khoát giả thuyết claim-centric** bằng thực nghiệm (không chỉ suy đoán) — tiết kiệm công sức cho hướng đi sai ở vòng sau; (2) **đơn giản hóa kiến trúc thật** (bỏ đa số 2/3, giảm 40-80% lượt gọi C4) dựa trên bằng chứng vững, không phải "giữ vì đã có sẵn".

Nhưng bằng chứng holdout v2 (47% false-block trên nội dung hoàn toàn mới) **nghiêm trọng hơn** ước tính round 2 (33%, holdout v1) — xu hướng 3 phép đo liên tiếp tăng dần cho thấy vấn đề gốc CHƯA được giải quyết, và có khả năng LỚN HƠN những gì corpus tune-riêng (dev corpus) từng cho thấy. 0 false-pass an toàn được giữ vững xuyên suốt MỌI corpus/probe (dev + 2 holdout + adversarial) — thuộc tính an toàn cốt lõi không bị đe dọa — nhưng thuộc tính "không làm phiền storytelling hợp lệ thường xuyên" hiện đang thất bại rõ ràng, không phải biên độ nhỏ.

**Khuyến nghị bước tiếp theo (KHÔNG thực hiện trong task này)**: (a) chấp nhận `C4_HOLDOUT_CORPUS_v2` (đã "burn") làm dev evidence, xây `C4_HOLDOUT_CORPUS_v3` từ chủ đề CL khác trước khi thử bất kỳ thiết kế mới nào; (b) thử hướng khác biệt kiến trúc, KHÔNG lặp lại claim-centric (đã bác bỏ) — có thể: few-shot cụ thể ngay trong prompt v2 hiện tại cho 4 pattern đã xác nhận tổng quát, hoặc 1 bước "second opinion" CHỈ cho câu bị chặn với contextual hint rõ ràng hơn (không phải appeal chung chung đã thử round 2); (c) song song, chấp nhận khả năng false-block ở mức 20-40% là chi phí vận hành THẬT của gate này ở giai đoạn hiện tại, và đầu tư vào quy trình review thủ công/human-in-the-loop hiệu quả cho các trường hợp bị chặn nhầm, thay vì tiếp tục kỳ vọng đạt ≤5% thuần túy bằng kỹ thuật prompt.
