# C4 Round 6 — Production Integration of `CL_PROVENANCE_PROTO_v1`

Ngày chạy: 2026-08-26. Tiếp nối Round 5 (`handoff/C4_ROUND5_BLIND_VALIDATION_REPORT.md`, verdict `READY_FOR_PRODUCTION_INTEGRATION` do user).

**Phạm vi round này, đúng như giao:** di chuyển prototype đã validate blind sang production codebase THẬT, giữ nguyên mọi bất biến an toàn, tạo regression coverage vĩnh viễn, chứng minh đường production đã tích hợp hoạt động end-to-end ở chế độ dry-run. **KHÔNG bắt đầu 20-episode pilot. KHÔNG publish/upload bất kỳ gì** — mọi lần chạy E2E trong round này dừng lại TRƯỚC TTS, và 1 artifact thật (đủ điều kiện publish) đã được **di chuyển RA KHỎI** thư mục staging thật (`drive_input/content_repo_staged/`) sang `handoff/round6_e2e_evidence/` ngay sau khi xác minh xong, để tránh pipeline batch tự động (launchd) vô tình nhặt và publish thật — xem Phần 10/16.

---

## 1. Kiến trúc tích hợp — Prototype → Production

```
Research topic (topic bank THẬT, chia sẻ với criminal_law_short_generator.py)
  ↓
cl_story_fact_pack.py::get_or_build_fact_pack()      [MỚI -- persist creator_specs/CL_STORY_FACT_PACKS/{topic_id}.json]
  ↓
cl_story_plan_and_generation.py::build_story_plan()   [MỚI]
  ↓
cl_story_plan_and_generation.py::generate_bound_script() [MỚI]
  ↓
validate_binding_integrity() / run_deterministic_guards() [MỚI, cơ học]
  ↓
run_drift_detector() -- TÁI DÙNG NGUYÊN _score_c4_adversarial_text (cl_risk_gate_verification.py), phạm vi hẹp
  ↓
cl_claim_ledger.verify_high_risk_claims_with_refs() -- TÁI DÙNG NGUYÊN (KHÔNG viết lại cổng ledger song song)
  ↓
generate_cl_seo() + _run_storytelling_person_check() -- TÁI DÙNG NGUYÊN
  ↓
criminal_law_storytelling_phase_a.py::compute_phase_a_result_provenance() [MỚI, orchestrator]
  ↓
Sidecar: .txt + .cl_meta.json + .story_plan.json + .script_binding.json + .topic_meta.json
  ↓
short_batch_runner.py's CL branch -- elif phase_a_variant=="storytelling_provenance_v1" [MỚI]
  ↓
_validate_provenance_binding() [MỚI, consumer, re-derive TOÀN BỘ từ đĩa] + validate_fact_verification_binding() [TÁI DÙNG NGUYÊN]
  ↓
publish_ready THẬT => "scripted" => (DỪNG Ở ĐÂY trong round này, KHÔNG chạm TTS)
```

**Nguyên tắc tích hợp đã tuân thủ:** không xây dựng lại từ trí nhớ — port trực tiếp logic đã validate blind (cùng thuật toán, cùng prompt, chỉ đổi import path + naming convention cho khớp production). Tái dùng tối đa hạ tầng có sẵn: `cl_risk_gate_verification.py` (C4), `cl_claim_ledger.py` (ledger, KHÔNG viết logic matching mới), `cl_case_generation.py` (SEO), `criminal_law_storytelling_phase_a.py`'s person-check (tái dùng nguyên `_run_storytelling_person_check`). Điểm mở rộng duy nhất mới hoàn toàn: fact pack + plan + bound generation + guard/drift hẹp (chính là phần kiến trúc mới của round 4/5).

## 2. File thay đổi (chỉ code production)

**File mới:**
- `cl_story_fact_pack.py` — StoryFact/StoryFactPack, extraction, persist theo topic_id (`creator_specs/CL_STORY_FACT_PACKS/`).
- `cl_story_plan_and_generation.py` — StoryPlan/PlanSegment, plan, bound generation, integrity/guard/drift.
- `criminal_law_provenance_generator.py` — entrypoint sinh nội dung mới (tương đương `criminal_law_short_generator.py` nhưng qua kiến trúc provenance), tái dùng topic bank THẬT.

**File sửa (mở rộng, không đổi hành vi cũ):**
- `criminal_law_storytelling_phase_a.py` — thêm `compute_phase_a_result_provenance()`, `write_provenance_sidecars()`, mở rộng `StorytellingPhaseAResult` (2 field mới có default giữ tương thích ngược), mở rộng `write_storytelling_sidecar()` để ghi `phase_a_variant` động thay vì hardcode.
- `short_segment_discovery.py` — thêm `cl_story_plan_sidecar_path()`, `cl_script_binding_sidecar_path()` (cùng "1 nguồn sự thật" convention đã có).
- `short_batch_runner.py` — thêm `_validate_provenance_binding()` (hàm mới), 1 nhánh `elif` mới trong `process_one_segment()`'s CL branch, mở rộng điều kiện OCR person-check (dòng ~493) để nhận cả 2 variant.

**File test mới:**
- `test_cl_story_fact_pack.py` (11 test), `test_cl_story_plan_and_generation.py` (18 test), `test_short_batch_runner_provenance_gate.py` (8 test).

**File test mở rộng:**
- `test_criminal_law_storytelling_phase_a.py` (+6 test cho `compute_phase_a_result_provenance`/`write_provenance_sidecars`).

**KHÔNG sửa:** `cl_risk_gate_verification.py`, `cl_claim_ledger.py`, `cl_case_generation.py`, `cl_case_batch.py`, `cl_risk_gate_orchestrator.py`, `criminal_law_short_generator.py` (chỉ được IMPORT để tái dùng topic bank, không sửa nội dung) — xác nhận qua `git diff` không có thay đổi nào ở các file này.

## 3. Schema artifact bền vững

**`creator_specs/CL_STORY_FACT_PACKS/{topic_id}.json`** (topic-scoped, tái dùng qua nhiều episode/retry cùng topic):
```json
{"topic_id": "...", "source_file": "...", "excerpt_hash": "sha256[:12]", "ledger_version_at_build": "...",
 "facts": [{"fact_id": "F001", "proposition": "...", "source_spans": [...], "risk_class": "...", "material": true,
            "external_claim_id": null, "external_status": "UNVERIFIED|VERIFIED|BLOCKED|NOT_REQUIRED"}], "pack_hash": "..."}
```

**`{episode}_Short.story_plan.json`** (episode-scoped): `{topic_id, fact_pack_hash, plan_hash, segments: [{segment_id, role, fact_ids}]}`.

**`{episode}_Short.script_binding.json`** (episode-scoped, artifact consumer re-derive dùng trực tiếp): `{script_hash, fact_pack_hash, plan_hash, bindings: [{segment_id, fact_ids, prose, pack_hash_at_generation}]}`.

**`{episode}_Short.cl_meta.json`** mở rộng (field mới, KHÔNG đổi field cũ):
```json
{"...(mọi field cũ giữ nguyên)...", "phase_a_variant": "storytelling_provenance_v1",
 "provenance_state": {"fact_pack_hash": "...", "plan_hash": "...", "script_hash": "...", "provenance_pass": true}}
```
`fact_verification` dùng ĐÚNG schema cũ (`state`/`topic_id`/`ledger_version`/`verified_claim_ids`/`blocked_claim_ids`/`checked_at`) — không có schema mới cho phần ledger, vì tái dùng nguyên `cl_claim_ledger.verify_high_risk_claims_with_refs()`.

## 4. Bất biến production hiện đang thực thi

| Bất biến | Cơ chế | Xác nhận |
|---|---|---|
| Fact-pack: mọi fact có source_span thật | `_span_exists()` cơ học, loại NGAY khi build | Test: `test_span_must_exist_verbatim_in_excerpt` |
| Fact tự đủ nghĩa | Hướng dẫn prompt (không cơ học được) | Test khóa hướng dẫn còn tồn tại trong prompt |
| Plan: fact_id phải thuộc ĐÚNG pack | `build_story_plan()` raise fail-closed | Test: `test_plan_fails_closed_on_fake_fact_id` |
| Script: không thêm claim mới/đổi số/đổi danh tính/tăng chắc chắn | Numeric guard (cơ học) + C4 drift hẹp (ngữ nghĩa) | 12/12 mutation round 4/5 + regression Kenneth Lay/Boy-in-Box |
| Integrity: plan/pack/script/binding hash khớp nhau | `plan.fact_pack_hash`, `pack_hash_at_generation`, consumer re-derive TOÀN BỘ | Test: 8 test trong `test_short_batch_runner_provenance_gate.py`, TẤT CẢ PASS |
| External verification: fact rủi ro cao dùng thật phải VERIFIED P0/P1 | `verify_high_risk_claims_with_refs()` trên CHÍNH script cuối, TÁI DÙNG nguyên | E2E thật: Enron/Piracy → BLOCKED_FACT đúng; Gardner → VERIFIED_CLAIM_LEDGER đúng |
| Consumer không tin self-report | `_validate_provenance_binding()` đọc LẠI fact pack/plan/binding từ đĩa, tính lại mọi hash | Xác nhận qua E2E thật (Phần 9) |

## 5. Quyết định Legacy C4

**Không đổi vai trò của C4 broad-semantic cho pipeline CŨ (`storytelling_v1`, `criminal_law_short_generator.py`).** `compute_phase_a_result()` (hàm gốc) hoàn toàn KHÔNG bị sửa — vẫn dùng C4 rộng (đối chiếu script với toàn bộ excerpt) làm gate chặn chính cho content sinh qua đường free-form cũ, đúng "preserve current behavior until explicitly migrated, do not remove legacy support blindly".

Cho pipeline MỚI (`storytelling_provenance_v1`): C4 KHÔNG còn là judge chính cho việc "văn xuôi paraphrase hợp lệ có được phép không" — vai trò đó do Story Plan (chọn fact hợp lệ TRƯỚC khi viết) đảm nhiệm. C4 (tái dùng nguyên hàm) chỉ còn vai trò DRIFT DETECTOR hẹp: phát hiện lệch giữa văn xuôi và ĐÚNG fact đã chọn cho segment đó.

**→ `KEEP_DIAGNOSTIC`** cho C4 rộng ở pipeline cũ (đúng khuyến nghị mặc định của nhiệm vụ, được củng cố thêm bởi bằng chứng round 4/5: 15%→47% false-block leo thang trên nội dung mới qua 3 corpus độc lập). Không xoá/tắt C4 rộng — hai pipeline chạy song song, người vận hành chọn dùng generator nào.

## 6. Tích hợp xác minh ngoài (external verification)

Quyết định thiết kế: KHÔNG dùng lại `run_external_verification_gate()` của prototype (kiểm tra per-fact tại thời điểm build fact pack) làm cổng publish cuối — thay vào đó **tái dùng ĐÚNG** `cl_claim_ledger.verify_high_risk_claims_with_refs()` chạy trên CHÍNH script cuối, giống hệt cách `compute_phase_a_result()` cũ đã làm. Lý do: đây là hàm ĐÃ có test thật, ĐÃ chạy production, và cho phép `validate_fact_verification_binding()` (consumer) hoạt động KHÔNG ĐỔI cho cả 2 variant — không cần viết cổng xác minh song song mới, đúng nguyên tắc tích hợp §16.

`external_status` tính ở fact-pack level (round 4/5's cơ chế) VẪN GIỮ LẠI nhưng chỉ còn vai trò TÍN HIỆU SỚM cho Story Plan (ưu tiên fact đã verify khi có lựa chọn) — không còn là quyết định publish cuối cùng.

## 7. Thực thi ở Consumer

`short_batch_runner.py`'s `_validate_provenance_binding()` KHÔNG tin bất kỳ field tự khai nào trong `.cl_meta.json`, kể cả `provenance_state` — **thực tế, hàm này không hề đọc `provenance_state` của sidecar** (xác nhận qua code: chỉ đọc `fact_verification` cho phần ledger). Toàn bộ phần provenance (fact pack/plan/binding) được RE-DERIVE HOÀN TOÀN từ 3 file riêng trên đĩa (`.story_plan.json`, `.script_binding.json`, fact pack theo topic_id) — nghĩa là **1 `provenance_state` bị giả mạo trong `.cl_meta.json` không có tác dụng gì với quyết định publish** (miễn nhiễm cấu trúc, không chỉ "được giảm thiểu"). Đây là lý do hạng mục rà đối kháng #8 ("forged provenance state") không tìm được cách khai thác nào — xem Phần 15.

## 8. Truy vết defect → test vĩnh viễn

| Defect thật (round 4/5) | Test production |
|---|---|
| Dangling pronoun trong fact | `test_self_contained_proposition_instruction_present_in_prompt` |
| Số dạng chữ vs chữ số | `test_numeric_guard_accepts_digit_form_when_proposition_uses_words` |
| fact_id lạ | `test_integrity_rejects_unknown_fact_id`, `test_foreign_fact_id_in_binding_fails_closed` |
| plan/fact-pack hash lệch | `test_generate_bound_script_fails_closed_on_plan_pack_hash_mismatch`, `test_stale_fact_pack_hash_fails_closed` |
| Fact pack cache cũ (excerpt đổi) | `test_get_or_build_fact_pack_rebuilds_when_excerpt_changes` |
| Thiếu external-verification gate | `test_provenance_pass_but_ledger_blocked_fact` |
| Binding bị copy | `test_integrity_rejects_copied_binding_across_packs`, `test_copied_binding_from_another_topic_fails_closed` |
| Script bị sửa sau validate | `test_modified_script_after_validation_fails_closed` (**MỚI hoàn toàn round này** — round 4/5 KHÔNG test được vì chưa có publish wiring) |
| Unbound material clause | `test_drift_detector_fails_closed_on_integrity_violation_without_calling_c4` + Kenneth Lay/Boy-in-Box regression |
| Cross-topic plan attack | `test_generate_bound_script_fails_closed_on_plan_pack_hash_mismatch` |

## 9. Round-5 regression (5 topic blind cũ giờ là dữ liệu regression)

Chạy lại Enron/Kenneth Lay qua ĐÚNG đường production thật (`criminal_law_provenance_generator.run_one()`):

```
status: BLOCKED_FACT (đúng như round 5 dự đoán -- publish_ready=False)
15/15 claim rủi ro cao KHÔNG có entry ledger (topic mới, chưa ai populate ledger)
provenance_pass ngầm định True (đã qua tới bước ledger nghĩa là guard/drift đã PASS)
```

**Không thay đổi kết quả kỳ vọng để "làm xanh" tích hợp** — đúng kỷ luật §25 nhiệm vụ. Kết quả khớp chính xác pattern round 5 (0/5 publish_ready do thiếu ledger coverage, không phải lỗi kiến trúc).

## 10. Smoke topic mới hoàn toàn chưa dùng

Chủ đề "Hostis Humani Generis / Cicero misattribution" (`RESEARCH_DRAFT_CUOP_BIEN_HANG_HAI.md`) — CHƯA từng dùng ở bất kỳ round nào trước (5 canary, C4 dev/holdout, 5 blind round 5, hay tuning round 6). Chạy qua đường production thật:

```
status: BLOCKED_FACT (2/2 claim rủi ro cao chưa có ledger -- đúng kỳ vọng, topic hoàn toàn mới)
provenance_pass: True (fact pack -> plan -> bound generation -> guard/drift đều PASS)
```

Xác nhận wiring THẬT xử lý đúng 1 topic hoàn toàn chưa chạm tới bất kỳ đâu trong quá trình tích hợp.

## 11. 2 kịch bản Provenance vs Publish-Ready (bắt buộc §30) — cả 2 đều THẬT, không giả lập

| Topic | provenance_pass | publish_ready (consumer re-derive) | Ghi chú |
|---|---:|---:|---|
| Enron/Kenneth Lay (round-5 regression) | True | **False** | 15 claim rủi ro cao chưa có ledger — `_validate_provenance_binding` PASS, `validate_fact_verification_binding` FAIL |
| Cicero/piracy (smoke mới) | True | **False** | 2 claim rủi ro cao chưa có ledger |
| **Gardner "81 phút"** (topic có ledger VERIFIED THẬT từ trước) | True | **True** | 2/2 claim khớp `GARDNER_DURATION_81MIN` + `GARDNER_SENSOR_RECORDED` (VERIFIED, P0 thật: fbi.gov, gardnermuseum.org) |

Với topic Gardner: chạy TOÀN BỘ pipeline thật, sidecar THẬT ghi `fact_verification.state="VERIFIED_CLAIM_LEDGER"` với 2 claim_id THẬT khớp ledger. Sau đó gọi TRỰC TIẾP cả 2 hàm consumer (`_validate_provenance_binding()` + `cl_claim_ledger.validate_fact_verification_binding()`) trên artifact THẬT trên đĩa — cả 2 PASS, xác nhận `publish_ready=True` đạt được thật qua wiring thật, KHÔNG fabricate. **Điểm cần nói rõ, trung thực:** đạt được kết quả này cần 3 lần thử excerpt khác nhau — 2 lần đầu bị `BLOCKED_FACT` một phần (2/5 và 3/5 claim khớp) do fresh LLM claim-extraction phân rã câu khác với cách entry ledger gốc từng được trích — đây là 1 phát hiện THẬT về độ nhạy cảm phrasing của cơ chế fuzzy-match ledger CÓ SẴN (không phải lỗi do round này gây ra, kế thừa nguyên từ `cl_claim_ledger.py`), ghi nhận ở Phần 16.

## 12. Chất lượng nội dung — quy tắc payoff/hook

Đúng §32: thêm hướng dẫn nhẹ cấp plan vào `_PLAN_PROMPT` (KHÔNG tạo semantic blocker cứng): "PAYOFF phải bổ sung thông tin/diễn giải lại/hệ quả/ý nghĩa còn bỏ ngỏ MỚI so với HOOK — không được chỉ lặp lại đúng nội dung đã tiết lộ ở HOOK". Khóa lại bằng test (`test_plan_prompt_instructs_payoff_must_add_new_info`). Chưa đo lại hiệu quả thật của hướng dẫn này trên quy mô lớn (cần dữ liệu telemetry từ pilot thật sau này, đúng khuyến nghị §32 "thu thập telemetry trong 20-episode pilot sau này").

## 13. Test Production

Manifest 15-file authoritative + 4 file test mới/mở rộng cho round 6:

```text
baseline (15-file manifest, round 3 authoritative): 524
test mới round 6: 41 (11 + 18 + 8 + 6-đã-tính-vào-criminal_law_storytelling_phase_a mở rộng)
tổng collected: 564
passed: 564
failed: 0
skipped: 0
duration: ~199s
```

Không có file nào bị bỏ sót — đối soát đầy đủ (đúng bài học round 5's 364-vs-524).

## 14. Độc lập khỏi scratchpad

`grep -rn "scratchpad\|/private/tmp"` trên toàn bộ file production mới/sửa: **0 kết quả là import/dependency thật** — 1 dòng khớp duy nhất là trong COMMENT tiếng Việt mô tả 1 kịch bản tấn công giả định ("sidecar viết tay/scratchpad"), không phải code path thật. Xác nhận: production KHÔNG import bất kỳ module nào từ thư mục scratchpad phiên làm việc.

## 15. Rà đối kháng — 16 hạng mục bắt buộc

| # | Hạng mục | Kết quả |
|---|---|---|
| 1 | Source đổi sau khi build Fact Pack | MITIGATED — `excerpt_hash` staleness check |
| 2 | Fact Pack stale | MITIGATED — cùng cơ chế #1 + consumer re-derive |
| 3 | Plan stale | MITIGATED — `plan.fact_pack_hash` check (build + consumer) |
| 4 | fact_id lạ | MITIGATED — `validate_binding_integrity()` |
| 5 | Story Plan bị copy | MITIGATED — `generate_bound_script()`'s fact_pack_hash check |
| 6 | Binding bị copy | MITIGATED — `pack_hash_at_generation` (cơ học, không phụ thuộc nội dung 2 pack trùng hay không) |
| 7 | Script bị sửa sau validate | MITIGATED — **MỚI round này**, so khớp joined_prose vs script text đang publish |
| 8 | Provenance state bị giả mạo | **MIỄN NHIỄM CẤU TRÚC** — consumer không hề đọc field này |
| 9 | High-risk fact chưa có ledger verification | MITIGATED — `validate_fact_verification_binding()` (tái dùng, đã test kỹ từ trước) |
| 10 | Contradicted external claim | MITIGATED — entry CONTRADICTED không bao giờ status==VERIFIED |
| 11 | Đổi số | MITIGATED — numeric guard |
| 12 | Phủ định | MITIGATED — drift detector (C4 tái dùng) |
| 13 | Đổi danh tính | MITIGATED — drift detector |
| 14 | Mệnh đề thực chất chưa được bind | MITIGATED — drift detector UNSUPPORTED |
| 15 | Legacy artifact đưa vào consumer mới | MITIGATED — dispatch tách biệt tuyệt đối bằng `phase_a_variant` string match, sidecar thiếu file provenance bị chặn ngay |
| 16 | Provenance artifact qua nhánh consumer khác | MITIGATED cấu trúc — `if topic == CL_TOPIC` / `elif` loại trừ lẫn nhau, `cl_case_batch.py`'s heavy pipeline hoàn toàn tách biệt luồng dữ liệu |

**Phát hiện bổ sung qua kiểm tra thứ tự ghi file (không nằm trong 16 mục nhưng liên quan trực tiếp #7/#8):** `write_provenance_sidecars()` ghi `.story_plan.json`/`.script_binding.json` TRƯỚC, `.cl_meta.json` ghi SAU CÙNG — vì `short_batch_runner.py` kiểm tra sự tồn tại của `.cl_meta.json` TRƯỚC TIÊN, 1 tiến trình khác chạy song song không bao giờ thấy episode "sẵn sàng" trước khi toàn bộ 3 sidecar provenance đã ghi xong (atomic write từng file) — xác nhận AN TOÀN theo thiết kế, không phải rủi ro còn mở.

**0 BLOCKER, 0 HIGH.**

## 16. Rủi ro còn lại

1. **Độ nhạy phrasing của ledger fuzzy-match** (Phần 11) — phát hiện THẬT qua E2E, không phải do round này gây ra (kế thừa từ `cl_claim_ledger._find_ledger_match`), nhưng ảnh hưởng trực tiếp tỷ lệ đạt `publish_ready=True` thật ở quy mô — cần 2-3 lần thử phrasing khác nhau để 1 claim ĐÃ verify trong ledger khớp lại qua fresh extraction. Rủi ro vận hành (chi phí/độ trễ), không phải lỗ hổng an toàn.
2. **Chưa đo lại quy tắc payoff/hook trên quy mô lớn** (Phần 12) — cần dữ liệu pilot thật.
3. **Chưa có locking rõ ràng cho topic bank dùng chung** giữa `criminal_law_short_generator.py` và `criminal_law_provenance_generator.py` nếu chạy đồng thời — chưa kiểm tra race condition thật (nằm ngoài phạm vi an toàn nội dung của round này, nhưng cần trước khi vận hành song song 2 generator ở quy mô).
4. **1 vòng blind (round 5) + 1 vòng integration (round 6) là bằng chứng tích lũy 2 lớp**, chưa phải hàng trăm episode thật — quyết định cuối vẫn nên thận trọng ở quy mô nhỏ trước khi mở 20-episode pilot (quyết định NGOÀI phạm vi round này).
5. **`creator_specs/CL_STORY_FACT_PACKS/` mới tạo trong round này** chứa 3 fact pack thật (Enron, piracy, Gardner) từ E2E test — vô hại (chỉ là cache tái sử dụng), không xoá.

## 17. Kết luận cuối

Kiến trúc provenance-preserving đã được port từ prototype (đã blind-validate ở round 5) sang code production thật, giữ nguyên mọi bất biến an toàn đã chứng minh, có test vĩnh viễn khóa lại toàn bộ 10 defect thật đã phát hiện qua round 4/5 — bao gồm 1 hạng mục (script bị sửa sau validate) mà round 4/5 KHÔNG kiểm chứng được vì chưa có publish wiring, nay đã kiểm chứng thật. E2E thật (không mock) trên 3 topic khác nhau chứng minh cả 2 nhánh publish-readiness bắt buộc hoạt động đúng, dừng chính xác ở ranh giới trước TTS như yêu cầu. Rà đối kháng 16 hạng mục: 0 BLOCKER, 0 HIGH — 1 hạng mục (forged provenance state) miễn nhiễm cấu trúc, không chỉ giảm thiểu.

Sẵn sàng để round tiếp theo cân nhắc `READY_FOR_20_EPISODE_CL_PILOT` — nhưng đó là quyết định của round SAU, KHÔNG PHẢI round này.

`READY_FOR_20_EPISODE_CL_PILOT`
