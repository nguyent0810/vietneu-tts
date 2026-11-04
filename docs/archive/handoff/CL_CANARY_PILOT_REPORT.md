# CL Production Canary Pilot — Báo cáo (5 episode STORYTELLING thật)

Ngày chạy: 2026-08-24. Git SHA nền: `027bd832ac682ff9071f1f8eb238feeb831ca2d3`. Ledger version trước pilot: `0c51f8bf75bd`.

**Kết luận cuối:** `NEEDS_FIX` — xem Phần 14.

---

## 1. Pilot Sample

5 episode STORYTELLING thật, sinh qua đúng `criminal_law_short_generator.py::generate_verified_script()` (judge-panel agy+codex thật), chọn theo chủ đề (không FIFO) để đa dạng category, phủ 4 research draft khác nhau:

| Episode | Chủ đề | source_file | claim_ledger_topic_id |
|---|---|---|---|
| ANDAXU_AlecJeffreys... | Alec Jeffreys & phát minh "dấu vân tay di truyền" (1984) | KHOA_HOC_PHAP_Y_MO_RONG | RESEARCH_DRAFT_KHOA_HOC_PHAP_Y_MO_RONG |
| ANDAXU_BbihilLockheed... | Bê bối hối lộ Lockheed & đạo luật FCPA (1976-77) | HOI_LOT_QUOC_TE | RESEARCH_DRAFT_HOI_LOT_QUOC_TE |
| ANDAXU_BnNgiphnThung... | Người phụ nữ Thung lũng Băng (Na Uy, 1970, cold case) | VU_AN_CHUA_LOI_GIAI_BATCH3 | RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3 |
| ANDAXU_Scxmnhpsng...MaxH | Xâm nhập sóng "Max Headroom" WGN-TV (1987) | VU_AN_CHUA_LOI_GIAI_BATCH4 | RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH4 |
| ANDAXU_inMaxiTrial...Cosa | Maxi Trial — Cosa Nostra (Ý, 1986-92) | TO_CHUC_TOI_PHAM | RESEARCH_DRAFT_TO_CHUC_TOI_PHAM |

Lý do chọn: phủ 4 loại rủi ro khác nhau (forensic/khoa học, hối lộ quốc tế/numerical, cold case không nghi phạm, an ninh phát sóng, tổ chức tội phạm/legal_status quy mô lớn) — không chỉ lặp lại fixture Gardner. Isdal Woman dùng chung `source_file`/topic_id với Gardner (đã có ledger từ trước) — có chủ đích, để test "claim mới trên topic_id đã có ledger cũ" khác với "topic_id hoàn toàn mới" (3 episode còn lại).

Input đã freeze (source_file, excerpt sha256, script sha256, claim_ledger_topic_id) — xem `pilot_freeze.json` trong scratchpad phiên làm việc.

## 2. Execution Summary

Chạy qua driver production THẬT `run_cl_storytelling_phase_a.py` (không gọi tắt hàm nội bộ nào).

| Episode | Kết quả Phase A | Điểm dừng | Sidecar ghi? |
|---|---|---|---|
| Alec Jeffreys | **BLOCKED_FACT** | Claim-ledger check (sau C4) | Không (đúng thiết kế) |
| Lockheed/FCPA | **FAIL** (STORYTELLING_C4_FAILED) | C4 (2/2 lượt fail) | Không |
| Isdal Woman | **FAIL** (STORYTELLING_C4_FAILED) | C4 (2/2 lượt fail) | Không |
| Max Headroom | **FAIL** (STORYTELLING_C4_FAILED) | C4 (2/2 lượt fail) | Không |
| Maxi Trial | **FAIL** (STORYTELLING_C4_FAILED) | C4 (2/2 lượt fail) | Không |

0/5 PASS, 1/5 BLOCKED_FACT (đúng nghĩa "an toàn"), 4/5 FAIL ở bước C4 — **bước có TRƯỚC phiên làm việc này**, không thuộc kiến trúc claim-ledger mới xây.

## 3. Factual Findings

**Phát hiện quan trọng nhất của cả pilot: 4/5 FAIL ở C4 đều là FALSE POSITIVE.** Đối chiếu tay từng câu bị C4 gắn cờ "thiếu căn cứ" với excerpt gốc (source_file) cho cả 4 episode — MỌI câu bị gắn cờ đều được excerpt hỗ trợ trực tiếp, nhiều câu gần như nguyên văn:

- Lockheed: "22 triệu USD", "Nhật Bản, Hà Lan, Ý", "bảo lãnh vay 250 triệu USD", "hàng trăm doanh nghiệp Mỹ khác", "Jimmy Carter ký... 19/12/1977" — **tất cả đều có trong excerpt, khớp gần như nguyên văn**.
- Isdal Woman: "hồ sơ 134/70", "tự sát", "NRK + BBC World Service... podcast 2018", "mục tiêu tái điều tra không truy tố" — tất cả đều có trong excerpt.
- Max Headroom: "15 giây", "30 giây", "John Hancock Center", câu đùa của Dan Roan — tất cả có trong excerpt.
- Maxi Trial: "Antimafia Pool tại Palermo", "475 thành viên", "338 bị cáo, 2.665 năm tù, 19 chung thân" — tất cả có trong excerpt.

Docstring `compute_phase_a_result()` đã tự ghi nhận từ trước (task #270): C4 test thực nghiệm cho thấy CÙNG 1 script/excerpt chạy 4 lần độc lập ra FAIL,FAIL,PASS,PASS — "nhiễu ngẫu nhiên thật của judge". Cơ chế "đa số 2/3" đã được thêm để giảm nhiễu này nhưng **pilot cho thấy tỷ lệ false-block THẬT vẫn ở mức ~80% (4/5) ngay cả sau khi có đa số 2/3** — mitigation chưa đủ.

Alec Jeffreys (episode duy nhất qua được C4) bị BLOCKED_FACT ở bước ledger — **đúng, an toàn**: 5/5 claim rủi ro cao (forensic/motive) không có entry ledger nào khớp (ledger trước pilot chỉ có entry cho Gardner). Đây KHÔNG phải lỗi — đúng bất biến "INPUT IS NOT EVIDENCE".

## 4. High-Risk Claim Recall

Vì 4/5 episode chưa từng chạm bước `classify_high_risk_claims()`, không thể đánh giá recall của bộ phân loại trên các episode đó qua pipeline thật. Rà tay (adversarial) từng script:

- **Alec Jeffreys**: bộ phân loại (khi chạy) trích đúng 5 claim forensic/motive, bỏ qua đúng 1 câu mang tính mô tả kỹ thuật chung (VNTR) hợp lý (ordinary, không material). Không phát hiện thiếu sót.
- **Max Headroom**: script nêu **"người dẫn chương trình thể thao Dan Roan"** — TÊN THẬT của 1 người thật (phát thanh viên WGN thời điểm đó). Theo docstring `criminal_law_storytelling_phase_a.py`, rubric STORYTELLING có luật "không nêu tên người thật nào" tuyệt đối (bất kể vai trò) — script này LẼ RA sẽ bị `_run_storytelling_person_check()` chặn nếu qua được C4. **Chưa được pipeline thật kiểm chứng vì bị C4 chặn trước** — cần lưu ý khi C4 được sửa/nới, không mặc định episode này sẽ PASS.
- **Maxi Trial**: script nêu **"học thuyết Buscetta"** — chứa họ thật của 1 nhân vật lịch sử có thật (Tommaso Buscetta). Tương tự Dan Roan: là thuật ngữ pháp lý/lịch sử phổ biến (như "Miranda rights"), nhưng theo luật blanket hiện tại vẫn có khả năng bị person-check chặn. Cũng CHƯA được pipeline thật kiểm chứng.
- **Lockheed/FCPA, Isdal Woman**: không phát hiện tên người thật nào trong script cuối; recall check không phát hiện claim rủi ro cao nào bị bỏ sót so với nội dung.

**Kết luận Phần 4**: 2/5 episode (Max Headroom, Maxi Trial) có khả năng thật sẽ vướng luật "không tên người thật" ở bước sau — cần theo dõi khi C4 được khắc phục, không giả định các episode này sẽ PASS trơn tru.

## 5. Binding Quality (word-overlap threshold 55%)

**KHÔNG đổi ngưỡng 55% trong pilot này** (đúng yêu cầu). Nhưng pilot phát hiện 1 lỗ hổng thật liên quan tới cùng cơ chế matching — xem Phần 6 + Phần 11 (BLOCKER, đã vá).

- Paraphrase hợp lệ: baseline control (claim diễn giải lại bằng từ khác, đúng nghĩa) → PASS đúng như kỳ vọng.
- Negation ("ghi lại" → "KHÔNG ghi lại"): qua đường **producer thật** (classify + `_find_ledger_match`) → **BLOCKED_FACT đúng** (claim bị phân loại+match riêng, không khớp entry VERIFIED). Qua đường consumer-only (sidecar giả tay tham chiếu đúng claim_id thật) → vẫn PASS (giới hạn ĐÃ được ghi nhận từ vòng review trước, xem Phần 11).
- Số liệu bị đổi (81→45 phút): **BLOCKER thật, đã xác nhận qua đường producer** — xem Phần 6/11.

## 6. Negative Controls (2/5 topic — Gardner/Isdal shared topic_id)

Chạy qua CẢ 2 đường: (a) consumer-only (`validate_fact_verification_binding` với sidecar giả tay), (b) producer thật (`verify_high_risk_claims_with_refs`, gọi LLM classify thật).

| Case | Đường consumer-only | Đường producer thật |
|---|---|---|
| Baseline (control) | PASS ✓ | — |
| Negation | PASS (rủi ro, đã biết từ trước) | **BLOCKED_FACT ✓ (an toàn)** |
| Số liệu bị đổi (81→45 phút) | **PASS (BLOCKER, trước khi vá)** → BLOCK sau khi vá | **PASS (BLOCKER, trước khi vá)** → BLOCK sau khi vá |
| Claim CONTRADICTED bị khai verified | BLOCK ✓ | — |
| Sidecar copy sang script không liên quan | BLOCK ✓ | — |

**1 case pass khi lẽ ra phải BLOCK ở CẢ 2 đường (trước khi vá) → phân loại BLOCKER** (khớp đúng tiêu chí "contradicted fact publishable" người dùng đặt ra) — xem Phần 11.

## 7. Story Quality (đánh giá tay, /10, không rewrite)

| Episode | Hook | Curiosity | Cognitive load | Payoff/Last line | CL identity | Factual confidence |
|---|---|---|---|---|---|---|
| Alec Jeffreys | 8 | 6 | 6 | 6 (khoa học, không phải "vụ án") | **4 — yếu, giống khoa học-sử hơn CL** | Cao (chưa verified, nhưng grounded tốt) |
| Lockheed/FCPA | 5 (hook dạng câu hỏi) | 5 | 7 (nhiều số/tên nước) | 5 | **4 — giống bài giảng chính sách hơn CL** | Cao |
| Isdal Woman | 6 (hook câu hỏi) | 8 (bí ẩn chưa lời giải) | 6 | 8 (kết thúc bằng câu hỏi mở đúng chất CL) | 8 — đúng chất | Cao |
| Max Headroom | 8 (mở đầu bằng hình ảnh lạ) | 7 | 6 | 6 (kết bằng câu đùa, hơi lệch tông) | 7 | Cao (trừ vấn đề tên thật, Phần 4) |
| Maxi Trial | 5 (hook câu hỏi) | 6 | **4 — quá nhiều số/tên riêng dồn dập** | 6 | 6 | Cao (trừ vấn đề tên thật, Phần 4) |

Nhận xét chung: 2/5 episode (Alec Jeffreys, Lockheed) có bản sắc "CL" (true-crime/hình sự) khá yếu — nội dung đúng nhưng đọc như khoa học-sử/chính sách hơn là câu chuyện tội phạm có kịch tính. Đáng cân nhắc khi chọn topic cho các batch tiếp theo, không phải lỗi kỹ thuật.

## 8. Mini Anti-Sameness (5 episode, chỉ mang tính early-signal, KHÔNG thay thế validation 20-episode)

- **3/5 hook dùng công thức câu hỏi** ("Vì sao...", "Tại sao...", "Làm sao...") — Lockheed, Isdal Woman, Maxi Trial. Chỉ 2/5 mở bằng câu trần thuật/hình ảnh (Alec Jeffreys, Max Headroom). Đây là dấu hiệu lặp cấu trúc tu từ sớm — nếu duy trì qua 20 episode sẽ rõ rệt hơn nhiều.
- Payoff/last-line: đa dạng hơn hook (Isdal Woman kết mở, Max Headroom kết bằng trích dẫn hài, Maxi Trial/Lockheed kết bằng số liệu tổng kết) — không thấy công thức lặp lại rõ ở phần kết.
- Nhịp/transitions: không đủ dữ liệu để đánh giá (chỉ có text, chưa qua TTS/render).

## 9. Source-Pack Quality (per topic)

| Topic | Phân loại | Ghi chú |
|---|---|---|
| VU_AN_CHUA_LOI_GIAI_BATCH3 (Gardner) | **GOOD** | 5 entry VERIFIED/CONTRADICTED thật, P0 (gardnermuseum.org, fbi.gov) + P1 (wbur.org) |
| VU_AN_CHUA_LOI_GIAI_BATCH3 (Isdal Woman, cùng topic_id) | **WEAK** | Claim riêng của Isdal Woman (hồ sơ 134/70, tự sát, podcast NRK/BBC) CHƯA có entry ledger nào — cần xác minh riêng dù chung topic_id với Gardner |
| KHOA_HOC_PHAP_Y_MO_RONG (Alec Jeffreys) | **WEAK/BROKEN** | Sự thật có nguồn P0 thật (le.ac.uk — trang chính thức Đại học Leicester), nhưng **WebFetch bị chặn 403 (bot protection)** — không lấy được excerpt nguyên văn để đưa vào ledger. Không có domain nào khác trong CL_SOURCE_TIERS_v1.json đủ điều kiện P0/P1 cho nội dung khoa học-sử (cambridge.org/science.org hiện đang xếp "aggregator" theo tiền lệ đã có) |
| HOI_LOT_QUOC_TE (Lockheed) | **UNTESTED** | Chưa chạm ledger (bị chặn C4 trước); sự thật là hồ sơ SEC/DOJ công khai, khả năng cao verify được nếu C4 được sửa |
| VU_AN_CHUA_LOI_GIAI_BATCH4 (Max Headroom) | **UNTESTED** | Tương tự |
| TO_CHUC_TOI_PHAM (Maxi Trial) | **UNTESTED** | Tương tự |

## 10. Operational Metrics

- Episode attempted: 5. PASS: 0. BLOCKED_FACT: 1. FAIL (C4): 4. needs_review tại consumer (short_batch_runner, do thiếu sidecar): 5/5 — **xác nhận: KHÔNG episode nào có nguy cơ tự động publish**.
- Entry ledger mới thêm trong pilot: 0 (không fabricate excerpt khi WebFetch bị chặn — xem Phần 9).
- Real LLM calls: `classify_high_risk_claims` (codex) — 3 lần thật (Alec Jeffreys + 2 negative-control producer-path). C4 (`_score_c4_adversarial_text`) — ước tính ~10 lần (2 lượt × 4 episode fail, + Alec Jeffreys pass trong ≤3 lượt).
- Person-reference check: **0 lần chạy** — chưa episode nào chạm bước này (bị chặn ở C4 hoặc ledger trước đó). Đây là khoảng trống coverage thật của pilot, không phải bằng chứng cơ chế này hoạt động tốt/xấu.
- Runtime: sinh 5 episode (agy+codex judge panel) ~15-20 phút tổng; chạy Phase A driver 5 episode ~2-3 phút; negative-control producer-path ~1 phút.
- Cơ hội cache: không cấp thiết ở quy mô 5 episode; ở quy mô 20, C4 gọi lặp lại 2-3 lần/episode sẽ là chi phí đáng kể nếu tỷ lệ false-block ~80% duy trì (kéo theo re-run/rewrite lặp lại nhiều lần).

## 11. Findings

### BLOCKER (đã vá trong pilot này)
**[BLOCKER-1] Số liệu bị đổi vẫn khớp VERIFIED nhầm.** `_find_ledger_match()` (SequenceMatcher.ratio()) và `_claim_text_bound_to_script()` (bag-of-words overlap) đều không đủ nhạy khi 1 câu chỉ khác ledger entry ĐÚNG 1 con số ("...81 phút" → "...45 phút") — phần còn lại của câu giống hệt nên vẫn vượt ngưỡng 0.55 dễ dàng. Xác nhận THẬT qua cả đường producer (LLM classify + match) lẫn đường consumer (sidecar hợp lệ, claim_id thật) — không phải lỗi lý thuyết.
- **Pre-fix behavior**: cả 2 đường đều PASS/VERIFIED nhầm cho script nói "45 phút" trong khi ledger chỉ verify "81 phút".
- **Patch**: thêm `_numeric_tokens_mismatch()` (regex `\d+`, so khớp tập số) — áp dụng tại CẢ `_find_ledger_match()` (producer) và `_claim_text_bound_to_script()` (consumer), defense-in-depth đúng triết lý đã dùng xuyên suốt dự án.
- **Regression test**: 5 test mới trong `test_cl_claim_ledger.py` (L.9, L.10 + 3 test đơn vị cho `_numeric_tokens_mismatch`) — lock hành vi đã vá.
- **Post-fix behavior**: cả 2 đường đều BLOCK đúng cho case "45 phút"; toàn bộ 22 test trong `test_cl_claim_ledger.py` + 503 test toàn bộ CL suite pass, không hồi quy.

### HIGH (CHƯA vá — ngoài phạm vi kiến trúc phiên này, cần review riêng)
**[HIGH-1] C4 (`_score_c4_adversarial_text`, `cl_risk_gate_verification.py`) có tỷ lệ false-block ~80% (4/5) trên nội dung STORYTELLING thật, được grounding tốt.** Đây là bước có TRƯỚC phiên làm việc này, dùng chung với case pipeline nặng (real named individuals) — blast radius lớn hơn nhiều so với kiến trúc claim-ledger mới, KHÔNG sửa trong pilot này theo đúng nguyên tắc "không redesign kiến trúc trừ khi pilot lộ ra lỗi hệ thống cụ thể VÀ có thể vá an toàn/hẹp". Cần review riêng (khả năng: mở rộng "đa số 2/3" thành "đa số 3/5", hoặc xem lại prompt `_score_c4_adversarial_text` để giảm nhạy cảm quá mức với diễn giải lại). **Đây là yếu tố CHẶN chính khiến pilot chưa sẵn sàng lên 20 episode** — không phải vì kiến trúc claim-ledger có vấn đề, mà vì hầu hết episode không bao giờ chạm tới được kiến trúc đó.

### MEDIUM (ghi nhận, không vá)
**[MEDIUM-1]** Negation vẫn PASS ở đường consumer-only (sidecar giả tay tham chiếu đúng claim_id thật đã VERIFIED) — giới hạn đã biết từ review trước (docstring `_claim_text_bound_to_script`), phòng tuyến thật nằm ở producer (đã xác nhận hoạt động đúng). Không vá thêm (đòi hỏi phân tích ngữ nghĩa/NLI vượt "smallest safe mechanism").
**[MEDIUM-2]** `le.ac.uk` (nguồn P0 thật cho Alec Jeffreys) bị chặn WebFetch (403) — cần cơ chế thay thế (con người trực tiếp đọc trang, hoặc mở rộng CL_SOURCE_TIERS_v1.json để chấp nhận nguồn thay thế phù hợp) trước khi topic khoa học-sử có thể verify được.
**[MEDIUM-3]** CL_SOURCE_TIERS_v1.json hiện được thiết kế chủ yếu cho true-crime Mỹ/VN — chưa có tiền lệ rõ ràng cho nguồn khoa học-sử/kinh doanh-chính trị quốc tế (vd trường đại học, tạp chí khoa học hiện xếp "aggregator" theo tiền lệ cambridge.org/science.org).

### LOW (ghi nhận)
**[LOW-1]** Dan Roan (Max Headroom) và "học thuyết Buscetta" (Maxi Trial) — tên người thật, chưa được person-reference check pipeline thật kiểm chứng (bị C4 chặn trước). Theo dõi khi C4 được sửa.
**[LOW-2]** 3/5 hook dùng công thức câu hỏi — dấu hiệu lặp cấu trúc sớm, chưa đủ dữ liệu để kết luận là vấn đề hệ thống ở quy mô 20 episode.
**[LOW-3]** 2/5 episode (Alec Jeffreys, Lockheed) có bản sắc CL yếu — cân nhắc khi chọn topic, không phải lỗi kỹ thuật.

## 12. Changes Made During Pilot

Chỉ 1 thay đổi — đúng nguyên tắc "prefer none", chỉ vá khi BLOCKER thật:
- `cl_claim_ledger.py`: thêm `_numeric_tokens_mismatch()`, gọi tại `_find_ledger_match()` + `_claim_text_bound_to_script()` (xem Phần 11, BLOCKER-1).
- `test_cl_claim_ledger.py`: +5 test khóa hành vi đã vá.
- **KHÔNG đổi**: ngưỡng 55%, master prompt, C4, kiến trúc claim-ledger tổng thể, ngưỡng đa số 2/3.

## 13. Scale Assessment

- **Cơ chế có bắt được claim rủi ro cao không an toàn không?** CÓ — BLOCKED_FACT hoạt động đúng (Alec Jeffreys), consumer fail-closed đúng khi thiếu sidecar (5/5), BLOCKER số liệu đã được phát hiện VÀ vá thật qua pilot này (không phải lý thuyết).
- **Cơ chế có làm sản xuất CL trở nên bất khả thi không?** **CÓ, hiện tại** — nhưng nguyên nhân chính là C4 (bước có từ trước), không phải kiến trúc claim-ledger mới. 4/5 episode chưa bao giờ chạm tới kiến trúc mới vì bị chặn sớm hơn.
- **Cơ chế có tổng quát hóa ra ngoài fixture Gardner không?** MỘT PHẦN — bản thân matching/binding logic tổng quát tốt (đã chứng minh qua Alec Jeffreys, 1 topic hoàn toàn mới), nhưng việc populate ledger 100% thủ công + khoảng trống nguồn (Phần 9) là nút thắt cổ chai thật cho quy mô lớn.
- **Ledger có sẵn sàng mở rộng bền vững không?** CHƯA — cần quy trình xác minh nguồn nhanh hơn (vd giải quyết vấn đề WebFetch bị chặn) và mở rộng chính sách source-tier ra ngoài true-crime Mỹ/VN.
- **Toàn hệ thống sẵn sàng cho 20-episode pilot chưa?** CHƯA.

## 14. Final Verdict

## `NEEDS_FIX`

Lý do chính: **[HIGH-1] C4 false-block ~80%** là rào cản chặn thật cho quy mô 20 episode — không phải vì kiến trúc claim-ledger (phần chính phiên làm việc này xây) có vấn đề, mà vì phần lớn nội dung chưa bao giờ chạm tới được kiến trúc đó. Kiến trúc claim-ledger tự nó, sau khi vá BLOCKER số liệu, đã chứng minh hoạt động đúng trên dữ liệu THẬT, đa dạng (không chỉ Gardner) — nhưng không đủ để kết luận sẵn sàng cho pilot 20-episode khi bản thân bước gate trước đó đã chặn gần hết production thật.

**Khuyến nghị bước tiếp theo (KHÔNG thực hiện trong task này theo đúng yêu cầu)**: review riêng, hẹp, có kiểm soát cho C4 (khả năng: nới ngưỡng đa số lên 3/5, hoặc điều chỉnh prompt `_score_c4_adversarial_text` để giảm false-positive trên diễn giải lại hợp lệ) — xong review đó, chạy lại đúng 5 episode NÀY (đã sinh sẵn, không cần sinh lại) qua Phase A để xác nhận có chạm được tới kiến trúc claim-ledger hay không, trước khi cân nhắc pilot 20-episode.
