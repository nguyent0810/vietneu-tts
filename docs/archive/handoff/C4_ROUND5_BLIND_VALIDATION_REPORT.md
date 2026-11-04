# C4 Round 5 — Blind Validation of Frozen Provenance Prototype (`CL_PROVENANCE_PROTO_v1`)

Ngày chạy: 2026-08-25/26 (tiếp nối Round 4, `handoff/C4_REPAIR_ROUND4_REPORT.md`, verdict `NEEDS_FIX`).

**Nhiệm vụ round này khác trước:** không hỏi "sẵn sàng cho 20-episode pilot" — chỉ hỏi kiến trúc có đủ bằng chứng BLIND để biện minh việc TÍCH HỢP VÀO PRODUCTION hay không. Verdict khả dĩ duy nhất mang tính tích cực: `READY_FOR_PRODUCTION_INTEGRATION`. **KHÔNG tích hợp vào production trong task này. KHÔNG bắt đầu 20-episode pilot.**

---

## 1. Đối soát 364 vs 524 test

```text
manifest trước đó (round 3, authoritative, 15 file):
  test_cl_case_batch.py, test_cl_case_generation.py, test_cl_claim_exposure_gate.py,
  test_cl_claim_ledger.py, test_cl_ledger_alias_sync.py, test_cl_real_person_safety.py,
  test_cl_risk_gate.py, test_cl_risk_gate_lifecycle.py, test_cl_risk_gate_orchestrator.py,
  test_cl_risk_gate_verification.py, test_cl_video_collapse_fix.py,
  test_criminal_law_storytelling_phase_a.py, test_run_cl_storytelling_phase_a.py,
  test_short_batch_runner_cl_gate.py, test_short_batch_runner_storytelling_binding.py
  => 524 passed (round 3)

manifest "364" trong báo cáo round 4 (7 file):
  test_cl_risk_gate.py, test_cl_risk_gate_verification.py, test_cl_claim_ledger.py,
  test_criminal_law_storytelling_phase_a.py, test_short_batch_runner_cl_gate.py,
  test_cl_risk_gate_lifecycle.py, test_cl_case_batch.py
  => 364 passed

file có trong CẢ HAI: 7 file trên (đúng)
file CHỈ có trong manifest 524 (bị thiếu ở round 4): 8 file --
  test_cl_case_generation.py, test_cl_claim_exposure_gate.py, test_cl_ledger_alias_sync.py,
  test_cl_real_person_safety.py, test_cl_risk_gate_orchestrator.py, test_cl_video_collapse_fix.py,
  test_run_cl_storytelling_phase_a.py, test_short_batch_runner_storytelling_binding.py
file CHỈ có trong "364": 0

test-count delta: 524 - 364 = 160 test nằm trong 8 file bị bỏ sót

LÝ DO: sai sót thật của round 4 -- khi liệt kê danh sách file để chạy lại, tôi tự dựng lại
danh sách 7 file từ trí nhớ hội thoại thay vì đọc lại chính xác danh sách 15-file đã ghi
trong C4_REPAIR_ROUND3_REPORT.md Phần 14. Đây KHÔNG PHẢI một manifest "đầy đủ" mới hay một
sự thay đổi phạm vi có chủ đích -- đó là 1 tập con KHÔNG ĐẦY ĐỦ, và báo cáo round 4 gọi nó
là "production test suite" là SAI, không nên viết vậy.
```

**Đã chạy lại CHÍNH XÁC manifest 15-file gốc:** `524 passed, 0 failed` (209.28s) — khớp hoàn toàn với con số round 3, xác nhận không có hồi quy thật nào (đúng như kỳ vọng, vì không file production nào bị sửa trong round 4 hay round 5 — toàn bộ prototype nằm trong scratchpad). **524 là con số đúng, được đối soát lại; 364 KHÔNG PHẢI một con số hợp lệ để trích dẫn cho bất kỳ mục đích nào, kể cả làm baseline cho round sau.**

---

## 2. Prototype đóng băng — `CL_PROVENANCE_PROTO_v1`

Snapshot sang thư mục riêng `scratchpad/frozen_CL_PROVENANCE_PROTO_v1/`, trước khi chạy bất kỳ blind topic nào:

```
b42fc87cf3099c5b663069080701a0a6a4ba27a020e53ed482ea46658f192448  mutation_tests.py
27fcb4c28d6332e1f7f0effd609e5e944294bf1ea7873f6808f553af23ed7a28  run_prototype_pipeline.py
d18e304624ca365ceaa05857c8ed5c42f2b36f610b0e5362ef1bc0f8fe58249c  story_fact_pack.py
1aacbbd9aac6978d947323e736d0f107817754b6dac1b4f354bc7df899752104  story_plan_and_generation.py
```

Git SHA nền production: `027bd832ac682ff9071f1f8eb238feeb831ca2d3` (không đổi từ canary pilot). Toàn bộ chạy blind round này import TRỰC TIẾP từ thư mục frozen (không phải bản scratchpad có thể bị sửa) — thực thi kỷ luật "không sửa sau khi đã freeze" một cách CƠ HỌC, không chỉ bằng lời hứa.

**Bất biến đã nêu và xác nhận thật (chi tiết đầy đủ trong `scratchpad/round5/FREEZE_MANIFEST.md`):**

| Bất biến | Cơ chế thực thi | Xác nhận |
|---|---|---|
| Fact-pack | `_span_exists()` cơ học, fact không đạt bị LOẠI khỏi pack | XÁC NHẬN |
| Plan | `build_story_plan()` raise fail-closed nếu fact_id lạ | XÁC NHẬN |
| Script | Guard cơ học (số liệu) + C4 drift (ngữ nghĩa) -- **phụ thuộc chất lượng phán đoán LLM cho phần phi-số liệu, không phải chứng minh cơ học tuyệt đối** | XÁC NHẬN có giới hạn, nêu rõ không phóng đại |
| Integrity | `plan.fact_pack_hash`, `pack_hash_at_generation`, `excerpt_hash` đều được so khớp cơ học | XÁC NHẬN |
| External verification | `run_external_verification_gate()` tách biệt khỏi `provenance_pass` | XÁC NHẬN |
| Consumer | `pack_hash_at_generation` chặn binding bị copy | XÁC NHẬN. **KHÔNG có** check nào cho việc sửa tay script SAU khi sinh (chưa có publish wiring để cần check này) — ghi nhận trung thực, không phải bỏ sót |

---

## 3. Mẫu blind — 5 chủ đề THẬT, hoàn toàn chưa dùng

| # | Topic | Nguồn thật | Dạng dữ kiện |
|---|---|---|---|
| 1 | Kevin Mitnick | `RESEARCH_DRAFT_TOI_PHAM_MANG.md` | chronology + identity + case đã khép (qua đời 2023) |
| 2 | "Boy in the Box" (Philadelphia, 1957) | `RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH2.md` | unresolved case + forensic genetic genealogy + **ràng buộc không nêu tên nạn nhân vị thành niên (§6, không ngoại lệ)** |
| 3 | Lịch sử vân tay / People v. Jennings 1911 | `RESEARCH_DRAFT_KY_THUAT_DIEU_TRA.md` | forensic/evidence + institutional science + hedging độ tin cậy khoa học |
| 4 | Black Sox Scandal 1919 | `RESEARCH_DRAFT_GIAN_LAN_THE_THAO.md` | legal status (trắng án vs cấm tư nhân) + kỷ luật hedging ("bị cáo buộc", không phải "đã dàn xếp") |
| 5 | Enron — Skilling/Fastow/**Kenneth Lay** | `RESEARCH_DRAFT_TOI_PHAM_CO_CO_KHOANG.md` | numerical/financial + **bẫy đảo ngược tình trạng pháp lý** (Lay "bị kết tội" nhưng bản án sau đó bị HỦY BỎ hoàn toàn) |

Xác nhận KHÔNG trùng: 5 canary gốc, mọi episode trong C4 dev corpus, mọi topic trong holdout v1/v2, Gardner, hay bất kỳ lần tuning nào của round 4 (danh sách đối chiếu đầy đủ trong `blind_topics.py::EXCLUDED_TOPICS_CHECKED`). Excerpt là trích đoạn TRUNG THỰC (không bịa) từ các research draft THẬT đã có sẵn trong repo, có nguồn/độ tin cậy ghi kèm trong tài liệu gốc. Hash excerpt đã đóng băng TRƯỚC khi chạy (Phần 2, `FREEZE_MANIFEST.md`).

---

## 4. Chất lượng Fact Pack

```text
Tổng số Story Fact (5 topic): 19 + 24 + 15 + 14 + 15 = 87
VALID: 87
TOO_STRONG: 0
UNSUPPORTED: 0
CONTRADICTED: 0
AMBIGUOUS: 0
```

Rà tay TOÀN BỘ 87 fact (không chỉ mẫu) — không phát hiện fact nào vượt quá mức chắc chắn của span nguồn, không phát hiện đại từ/từ chỉ định dangling, không phát hiện tổng hợp vượt quá bằng chứng.

**2 điểm kiểm tra trọng tâm được yêu cầu rõ trong task này:**

- **Bẫy Kenneth Lay (đảo ngược tình trạng pháp lý):** fact pack tách RIÊNG `F013` ("Kenneth Lay bị kết tội... ngày 25/5/2006") và `F015` ("...một thẩm phán liên bang tại Houston đã ra lệnh hủy bỏ toàn bộ kết luận có tội của Kenneth Lay") thành 2 fact độc lập, đúng với 2 giai đoạn pháp lý thật. Story Plan đưa F015 vào segment PAYOFF (S5) — câu CUỐI CÙNG của kịch bản là "Sau khi Kenneth Lay qua đời, một thẩm phán liên bang tại Houston đã ra lệnh hủy bỏ toàn bộ kết luận có tội của ông theo học thuyết đình chỉ tố tụng do tử vong." **Không có câu nào trong toàn kịch bản khẳng định "Kenneth Lay đã bị kết án" như một sự thật cuối cùng, không kèm ngữ cảnh hủy bỏ.** Đây là kết quả ĐÚNG, xử lý đúng bẫy pháp lý tinh vi nhất trong bộ 5 topic.
- **Ràng buộc không nêu tên nạn nhân vị thành niên (Boy in the Box):** bản excerpt gốc CHÍNH NÓ không chứa tên đầy đủ của nạn nhân (research draft cố ý không đưa tên vào theo đúng §6) — nên đây không phải bài test "model có TỪ CHỐI nêu tên khi có sẵn trong input hay không", mà là "model có TỰ THÊM tên từ kiến thức nền (vụ án đã lên tin quốc tế 2022, có khả năng cao nằm trong dữ liệu huấn luyện) hay không". Toàn bộ 24 fact + kịch bản cuối chỉ dùng "bé trai"/"em", không một lần nào chèn thêm tên riêng từ kiến thức ngoài nguồn — vượt qua đúng phép thử này, nhưng **cần ghi nhận trung thực: đây là phép thử "không tự thêm", không phải phép thử "từ chối khi bị dụ trực tiếp"** — round sau nếu muốn stress-test mạnh hơn nên cố ý đưa tên vào excerpt rồi kiểm tra fact pack có LOẠI nó ra hay không.

## 5. Chất lượng Story Plan

Rà toàn bộ 28 segment (5 topic) tìm cầu nối nhân quả bị bịa từ chỉ riêng trình tự sắp xếp: **không phát hiện trường hợp nào**. Mỗi segment REVEAL/PAYOFF chỉ dùng fact đã có sẵn quan hệ nhân quả tường minh trong chính fact đó (vd F009 "Lý do được nêu cho phán quyết trắng án... là bằng chứng không đủ thuyết phục" — quan hệ nhân quả đã có sẵn trong fact, không phải do plan tự suy ra từ việc đặt 2 fact cạnh nhau).

**Điểm chất lượng cấu trúc đáng ghi nhận (không phải lỗi an toàn):** ở 2/5 topic (Lịch sử vân tay, Enron), plan chọn đúng fact "gây bất ngờ nhất" (báo cáo NAS 2009 phê phán độ tin cậy vân tay; việc bản án Lay bị hủy) làm HOOK mở đầu — khiến đoạn PAYOFF cuối cùng chỉ LẶP LẠI đúng nội dung đã tiết lộ ở đầu thay vì xây dựng cao trào mới. Đây là 1 xu hướng thật, xuất hiện 2/5 lần độc lập — không phải ngẫu nhiên 1 lần — xem Phần 11.

## 6. Binding — claim vật chất có được neo đúng không

Rà tay từng câu trong cả 5 kịch bản cuối (28 câu văn xuôi): **mọi mệnh đề thực chất đều BOUND_CORRECTLY** vào đúng fact_id đã chọn cho segment đó — không phát hiện `UNBOUND`, không phát hiện `BOUND_BUT_MEANING_CHANGED`. Không có câu văn phong/tu từ thuần túy nào bị tính nhầm là claim vật chất (khung kể chuyện tối giản, mỗi câu đều neo trực tiếp vào ≥1 fact).

```text
Unbound material factual claims: 0/28 câu (mục tiêu §28: 0) -- ĐẠT
```

## 7. Kết quả C4_DRIFT_DETECTOR

```text
segment kiểm tra: 28 (6+6+6+5+5)
PASS: 28
BLOCK (false hoặc true): 0
false block: 0
false pass: 0 (xác nhận qua 12 mutation test, Phần 8 -- toàn bộ drift/số liệu THẬT bị chặn khi cần)
```

**0/28 grounded false-block trên blind set — khác biệt căn bản so với legacy C4 (4/5 EPISODE bị chặn nhầm trên chính 5 canary gốc).** Đây là lần đầu tiên trong 5 round, mẫu MỚI (chưa từng dùng để tune) đạt 0 false-block ngay từ lần chạy đầu tiên, không cần vá gì thêm — khác hẳn pattern round 1-3 (15%→33%→47% false-block leo thang qua các holdout liên tiếp của kiến trúc CŨ).

## 8. Mutation & Integrity Attack — kết quả đầy đủ

Chạy trên script THẬT của Enron (5 segment, nhiều số liệu + bẫy pháp lý), qua đúng bản frozen.

| # | Mutation | Kết quả | Cơ chế |
|---|---|---|---|
| 1 | Đổi số (98→60) | BLOCKED | Numeric guard |
| 2 | Đổi tiền ($42M→$55M) | BLOCKED | Numeric guard |
| 3 | Đổi năm (2001→2003) | BLOCKED | Numeric guard |
| 4 | Đảo phủ định | BLOCKED | Drift (CONTRADICTED) |
| 5 | Đổi danh tính | BLOCKED | Drift (CONTRADICTED) |
| 6 | Nghi phạm→chủ mưu xác nhận | BLOCKED | Drift (UNSUPPORTED) |
| 7 | may→did (modal) | BLOCKED | Drift (STRONGER_THAN_SOURCE) |
| 8 | Bịa động cơ | BLOCKED | Drift (UNSUPPORTED) |
| 9 | Bịa chi tiết kỹ thuật | BLOCKED | Drift (UNSUPPORTED) |
| 10 | Chèn mệnh đề không liên quan | BLOCKED | Drift (UNSUPPORTED) |
| 11 | Đảo nhân quả | BLOCKED | Drift (CONTRADICTED) |
| 12 | Copy fact-binding từ topic khác | **BLOCKED** | **Integrity (`pack_hash_at_generation`)** |

**12/12 BLOCKED.** Điểm khác biệt quan trọng so với round 4: mục #12 lần này bị chặn CƠ HỌC (hash không khớp), KHÔNG phải nhờ may rủi 2 topic tình cờ không trùng số liệu như lần đầu ở round 4 — xác nhận bản vá round 4 tổng quát hóa đúng trên dữ liệu blind hoàn toàn mới.

**5 phép thử copy/stale bổ sung (§15 nhiệm vụ), chạy cơ học trực tiếp qua bản frozen, không cần LLM:**

| Attack | Kết quả |
|---|---|
| Plan từ Topic A + Fact Pack B | BLOCKED (`plan.fact_pack_hash` không khớp) |
| Script A bindings + Pack B | BLOCKED (`validate_binding_integrity`: fact_id không tồn tại) |
| Fact Pack cũ + excerpt nguồn mới | BLOCKED (xác nhận ở round 4, `excerpt_hash` staleness check) |
| Fact Pack rebuilt + Plan cũ (stale) | BLOCKED (`plan.fact_pack_hash` không khớp pack mới) |
| Binding bị sửa `pack_hash_at_generation` (proxy cho "script sửa sau xác thực") | BLOCKED |

Toàn bộ 5 phép thử copy/stale + 12 mutation đều chặn ĐÚNG NHƯ THIẾT KẾ, phần lớn CƠ HỌC (không cần phán đoán LLM) trước khi drift detector cần chạy — đúng tinh thần "ưu tiên chặn cơ học trước phán đoán LLM" của nhiệm vụ.

## 9. Provenance vs Publish Readiness

| Topic | provenance_pass | Fact rủi ro cao đã dùng | Đã xác minh ngoài | publish_ready |
|---|---:|---:|---:|---:|
| Kevin Mitnick | True | 10 | 0 | False |
| Boy in the Box | True | 13 | 0 | False |
| Lịch sử vân tay | True | 10 | 0 | False |
| Black Sox 1919 | True | 11 | 0 | False |
| Enron | True | 8 | 0 | False |
| **Tổng** | **5/5** | **52** | **0** | **0/5** |

**0/5 publish_ready là kết quả ĐÚNG, không phải lỗi** — đúng §16 nhiệm vụ, không được coi kiến trúc là tệ chỉ vì `publish_ready=False` khi ledger chưa có coverage. Đây là 5 topic HOÀN TOÀN MỚI, chưa ai populate `CL_VERIFIED_CLAIM_LEDGER_v1.json` cho chúng — cùng nút thắt cổ chai production hiện có, không phải do kiến trúc mới.

## 10. Nhận xét Source-Pack

| Topic | Phân loại | Ghi chú |
|---|---|---|
| Kevin Mitnick | **GOOD** | Nguồn tier cao (Washington Post, CNN, Dignity Memorial), đã qua đời — không rủi ro §4 mới phát sinh |
| Boy in the Box | **GOOD** | Nguồn tier cao (PPD chính thức, báo chí tier 1-2), 1 mâu thuẫn ngày nhỏ (25/2 vs 26/2) đã ghi trong tài liệu gốc, KHÔNG dùng trong excerpt |
| Lịch sử vân tay | **GOOD** | Nguồn định chế/khoa học (Smithsonian, NAS, DOJ) |
| Black Sox 1919 | **GOOD** | Cực kỳ well-documented (SABR, Britannica, HISTORY.com, ESPN); 1 chi tiết độ tin cậy trung bình (vai trò Rothstein) đã CHỦ ĐỘNG loại khỏi excerpt |
| Enron | **GOOD** | Nguồn tier cao (NPR, FBI, CBC, CFO.com) |

**Gánh nặng xác minh (facts rủi ro cao THẬT SỰ được dùng, không phải toàn bộ research draft):** 52 fact trên 5 topic (trung bình 10.4/topic) — đây là con số THẬT của công sức xác minh P0/P1 cần thiết nếu muốn 5 episode này đạt `publish_ready=True`, KHÔNG PHẢI ước tính lý thuyết. Không xác minh thật trong round này (đúng phạm vi được giao — chỉ đo, không redesign source-pack).

## 11. Chất lượng câu chuyện

| Topic | Hook | Clarity | Curiosity | Cognitive load | Payoff | CL identity | Ghi chú |
|---|---:|---:|---:|---:|---:|---:|---|
| Kevin Mitnick | 4 | 8 | 5 | 6 | 5 | 5 | Hook YẾU -- plan chọn fact hành chính (làm việc với FBI/Fortune 500) thay vì mở bằng "hacker bị truy nã gắt gao nhất" kịch tính hơn nhiều |
| Boy in the Box | 8 | 8 | 8 | 6 | 8 | 8 | Mạnh nhất trong 5 -- dạng unresolved-case hợp tự nhiên với công thức "kết mở" CL |
| Lịch sử vân tay | 7 | 7 | 7 | 6 | **4** | 5 | Payoff YẾU -- lặp lại đúng nội dung đã tiết lộ ở hook, không xây cao trào mới (Phần 5) |
| Black Sox 1919 | 7 | 7 | 7 | 6 | 6 | 7 | Kỷ luật hedging xuất sắc ("bị cáo buộc" xuyên suốt, không 1 lần khẳng định đã dàn xếp) |
| Enron | 5 | 6 | 6 | 7 | **4** | 6 | Payoff YẾU -- cùng pattern lặp-hook-ở-payoff như vân tay; mật độ số liệu cao (98 tội danh, $42M, nhiều năm tù) |

**Phát hiện có hệ thống, không phải ngẫu nhiên:** pattern "payoff lặp lại hook" xuất hiện ĐỘC LẬP ở 2/5 topic — cả hai lần đều do Story Plan chọn fact "giật gân nhất" (báo cáo phê phán khoa học pháp y; bản án bị hủy) làm HOOK thay vì PAYOFF, khiến đoạn kết không còn gì mới để tiết lộ. Đây là điểm CẦN CẢI THIỆN thật ở `_PLAN_PROMPT` (chưa hướng dẫn rõ: fact "twist" mạnh nhất nên dành cho REVEAL/PAYOFF, không phải HOOK) — không phải lỗi an toàn, không chặn verdict, nhưng là 1 khoản nợ chất lượng có bằng chứng cụ thể, đáng vá ở round tiếp theo.

**Không quan sát thấy suy thoái có hệ thống so với baseline phong cách cũ:** so với bảng điểm round 1 canary gốc (Hook 5-8, CL identity 4-8 tùy chủ đề) và round 4's ghi nhận tương tự, mức điểm blind-set round này nằm trong CÙNG khoảng dao động — sự khác biệt về chất lượng theo TỪNG chủ đề (Mitnick/vân tay yếu hơn Boy in the Box/Black Sox) phản ánh đúng bản chất chủ đề (case đóng/khoa học-sử luôn yếu "CL identity" hơn unresolved-case/scandal kịch tính), không phải do kiến trúc provenance-preserving.

## 12. Chi phí vận hành

```text
Blind set (5 topic, 28 segment): 1 fact-pack + 1 plan + N sinh văn xuôi + N drift = 2+2N/topic
  Mitnick (N=6): 14 lượt | Boy in Box (N=6): 14 | Vân tay (N=6): 14 | Black Sox (N=5): 12 | Enron (N=5): 12
  Tổng: 66 lượt LLM thật cho 5 topic, KHÔNG cần vá/chạy lại lần nào (khác round 4 cần 3 vòng vá)

12 mutation test (Enron, N=5 cumulative): 4/12 chặn cơ học tức thì (guard/integrity, KHÔNG tốn lượt LLM);
  8/12 cần drift -- tối đa 8×5=40 lượt, thực tế ít hơn vì mutation ở segment sau không cần lượt segment trước
```

So với legacy C4 hiện tại (1 lượt/toàn bộ script): prototype vẫn tốn **~12-14× lượt/episode** — không đổi so với ước tính round 4, chi phí thật, chưa được tối ưu trong round này (đúng phạm vi — chỉ đo).

**Fact pack tái dùng được:** xác nhận qua cơ chế `excerpt_hash` — không cần build lại nếu excerpt không đổi.

## 13. Quyết định Legacy C4 (dựa trên bằng chứng BLIND, không phải 5 canary đã "cháy")

- **KEEP_BLOCKING:** KHÔNG — không có bằng chứng MỚI nào trong round này ủng hộ giữ vai trò chặn chính hiện tại của legacy C4 cho pipeline free-form; ngược lại, bằng chứng blind round này (0/28 false-block khi cùng cơ chế C4 được thu hẹp scope) càng củng cố giả thuyết vấn đề nằm ở SCOPE phán đoán, không phải bản thân judgment engine.
- **RETIRE:** CHƯA — kiến trúc mới đã qua 1 vòng blind với kết quả rất tích cực (0/28 false-block, 12/12 mutation + 5/5 integrity attack chặn đúng, 0/87 fact sai), nhưng **1 vòng blind với N=5 topic KHÔNG đủ để retire hoàn toàn 1 cơ chế an toàn đang hoạt động trong production** mà chưa có: (a) publish wiring thật, (b) một vòng blind THỨ HAI độc lập để xác nhận kết quả này không phải may mắn thống kê, (c) giải quyết pattern "payoff lặp hook" (Phần 11) ảnh hưởng chất lượng dù không ảnh hưởng an toàn.
- **→ KEEP_DIAGNOSTIC**, giữ nguyên khuyến nghị từ round 4, NAY ĐƯỢC CỦNG CỐ bởi bằng chứng blind thật (không chỉ dev-corpus): legacy C4 tiếp tục là công cụ chẩn đoán/tham chiếu cho pipeline hiện tại, kiến trúc mới tiếp tục phát triển như 1 con đường THAY THẾ tiềm năng, chưa đủ chín để tích hợp production.

## 14. Test Production

Manifest 15-file authoritative, chạy lại đầy đủ: **524 passed, 0 failed, 0 skipped**, 209.28s (Phần 1). Không đổi từ round 3 — không có thay đổi code production nào trong round 4 hoặc round 5.

## 15. Test Prototype

**Vẫn KHÔNG có bộ pytest cố định cho prototype** — đây là khoản nợ kỹ thuật thật, đã ghi nhận từ round 4, CHƯA được trả trong round 5 (ưu tiên round này là chạy blind set thật trước). Danh sách 10 defect thật cần chuyển thành regression test cố định trước khi cân nhắc bất kỳ bước tích hợp nào xa hơn: dangling-reference fact pack, số dạng chữ vs chữ số, fact_id lạ (`validate_binding_integrity`), `plan.fact_pack_hash` không khớp, fact pack cache cũ (`excerpt_hash`), thiếu external-verification gate, binding bị copy (`pack_hash_at_generation`), script bị sửa sau validate (chưa có publish wiring để test), unbound material clause, cross-topic plan attack. **KHUYẾN NGHỊ RÕ: đây phải là hạng mục ưu tiên số 1 của round tiếp theo nếu muốn tiến gần hơn tới `READY_FOR_PRODUCTION_INTEGRATION`.**

## 16. Rà đối kháng — tổng hợp toàn bộ phát hiện (round 4 + round 5)

| # | Hạng mục tấn công | Kết quả | Mức độ |
|---|---|---|---|
| 1 | Fake fact_id trong plan | BLOCKED (fail-closed raise) | — (đã đúng từ thiết kế) |
| 2 | Copy plan từ topic khác | BLOCKED (`plan.fact_pack_hash`) | — |
| 3 | Stale fact-pack hash / excerpt đổi | BLOCKED (`excerpt_hash`) | — |
| 4 | Plan chọn fact có `external_status=BLOCKED` | **CHƯA test trực tiếp round này** — `run_external_verification_gate` sẽ chặn publish_ready nếu fact đó material+high-risk, nhưng chưa có ca thật nào trong 5 blind topic có sẵn 1 fact BLOCKED để thử; hành vi được suy ra từ code, không phải quan sát thật | MEDIUM (chưa quan sát thật, chỉ suy luận từ code) |
| 5 | High-risk fact không có provenance ngoài, coi như đã authorize | BLOCKED (`run_external_verification_gate`, xác nhận qua 52/52 fact rủi ro cao ở blind set đều đúng bị gắn UNVERIFIED, không silent-pass) | — |
| 6 | Segment claim fact_ids nhưng prose mâu thuẫn | BLOCKED (drift, mutation #4/#5/#11) | — |
| 7 | Prose thêm mệnh đề không đại diện | BLOCKED (drift, mutation #8/#9/#10) | — |
| 8 | Fact-pack hallucination | BLOCKED (`_span_exists()` cơ học) | — |
| 9 | Span tồn tại nhưng không thực sự entail | **CHƯA có phòng thủ cơ học/hệ thống** — rà tay 87 fact blind set không phát hiện case thật nào, nhưng đây là spot-check, không phải chứng minh | MEDIUM (không đổi từ round 4) |
| 10 | Copy fact-binding từ topic khác | BLOCKED cơ học (`pack_hash_at_generation`), xác nhận KHÔNG còn phụ thuộc may rủi nội dung (round 4 → round 5 fix đã tổng quát hóa đúng) | — |
| 11 | Stale plan sau khi pack rebuild | BLOCKED (`plan.fact_pack_hash`) | — |
| 12 | Script bị sửa tay sau khi validate | **KHÔNG THỂ test** — chưa có publish wiring nào để "sau validate" có nghĩa | Ghi nhận là giới hạn phạm vi, không phải lỗ hổng đang mở |
| 13 | Legacy-C4-bypass-interaction | N/A — prototype hoàn toàn tách biệt production, không đường nào để bypass 1 gate chưa từng chạm tới | — |
| 14 | Rhetorical wording che presupposition sai | Không phát hiện case thật trong 28 segment blind set (không câu nào dùng rhetorical framing đáng ngờ để né drift) | — |
| 15 | Pattern "payoff lặp hook" (Phần 11) | Xác nhận 2/5, KHÔNG PHẢI lỗ hổng an toàn, là khoản nợ chất lượng thật | MEDIUM (chất lượng, không phải an toàn) |

**Không có BLOCKER nào phát sinh round này.** 2 MEDIUM tồn đọng thật (#4 chưa quan sát trực tiếp, #9 chưa có phòng thủ hệ thống) — cả hai đều KHÔNG mới, đã ghi nhận từ round 4, KHÔNG cần "burn" blind set vì không có patch nào được áp dụng sau khi thấy kết quả blind (đúng kỷ luật §26 — không sửa code sau khi thấy blind result rồi tiếp tục gọi nó là blind).

## 17. Rủi ro còn lại

1. **N=5, 1 vòng duy nhất** — dù kết quả rất tích cực, thống kê mẫu nhỏ vẫn là rủi ro thật; 1 vòng blind thứ hai (bộ topic MỚI, khác 10 topic đã "cháy" tính tới nay: 5 canary + 5 blind round 5) sẽ củng cố đáng kể độ tin cậy trước khi tích hợp production.
2. **Chưa có bộ test prototype cố định** (Phần 15) — rủi ro hồi quy thật nếu bất kỳ ai sửa code prototype trong tương lai mà không có regression test khóa lại 10 defect đã tìm thấy.
3. **Pattern payoff lặp hook** (Phần 11, #15) — nợ chất lượng, không phải an toàn, nhưng ảnh hưởng khả năng dùng thật nếu không vá.
4. **Chi phí ~12-14×/episode** — chưa tối ưu, chưa đánh giá tác động ở quy mô lớn.
5. **0/5 publish_ready xuyên suốt 2 round** — không phải lỗi kiến trúc, nhưng là điều kiện tiên quyết CHƯA giải quyết để bất kỳ episode nào (canary hay blind) thực sự publish được — cần 1 kế hoạch xác minh nguồn thật (không chỉ đo, mà thực hiện) trước khi nói tới quy mô sản xuất.
6. **Chưa có publish wiring** — nghĩa là hạng mục #12 rà đối kháng (script sửa sau validate) hoàn toàn chưa được test — khi wiring thật được xây, đây PHẢI là việc đầu tiên cần kiểm chứng.

## 18. Kết luận cuối

Round 5 cung cấp bằng chứng blind THẬT SỰ đầu tiên cho kiến trúc provenance-preserving — 5 chủ đề hoàn toàn chưa dùng, đóng băng trước khi chạy, không tinh chỉnh sau khi thấy kết quả. Kết quả: 0/28 grounded false-block, 0/87 fact sai (UNSUPPORTED/CONTRADICTED/TOO_STRONG/AMBIGUOUS), 12/12 mutation an toàn bắt buộc bị chặn, 5/5 phép thử copy/stale bị chặn (phần lớn cơ học), 2 bẫy tinh vi nhất (Kenneth Lay vacatur, ràng buộc không nêu tên nạn nhân vị thành niên) đều được xử lý đúng. Đây là kết quả mạnh hơn nhiều so với bất kỳ vòng đánh giá nào của kiến trúc C4 cũ ở bất kỳ round nào trước đây.

Nhưng: `READY_FOR_PRODUCTION_INTEGRATION` đòi hỏi nhiều hơn 1 vòng blind tích cực, đặc biệt khi (a) chưa có bộ test prototype cố định để khóa lại 10 defect đã tìm thấy qua 2 round, (b) 1 pattern chất lượng thật (payoff lặp hook) chưa được vá, (c) chưa có publish wiring nên 1 hạng mục rà đối kháng bắt buộc (#12) hoàn toàn chưa kiểm chứng được, (d) N=5 là mẫu nhỏ cho 1 quyết định tích hợp production. Không có BLOCKER, nhưng các khoảng trống này là thật, cụ thể, và nên được đóng trước khi verdict tích cực.

`NEEDS_FIX`
