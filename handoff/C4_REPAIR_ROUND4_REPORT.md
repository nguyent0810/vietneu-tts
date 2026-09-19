# C4 Repair Round 4 — Provenance-Preserving Generation Prototype

Ngày chạy: 2026-08-25 (tiếp nối từ Round 3, `handoff/C4_REPAIR_ROUND3_REPORT.md`, verdict `NEEDS_FIX`).

**Đây là PROTOTYPE chạy SONG SONG với production, KHÔNG PHẢI thay thế.** Toàn bộ code nằm trong scratchpad phiên làm việc (`/private/tmp/.../scratchpad/story_fact_pack.py`, `story_plan_and_generation.py`, `run_prototype_pipeline.py`, `run_all_5_canary_prototype.py`, `mutation_tests.py`). **KHÔNG file production nào bị sửa trong round này** (`cl_risk_gate_verification.py`, `criminal_law_storytelling_phase_a.py`, `cl_claim_ledger.py` — xác nhận qua `git status`/`git diff`, không có thay đổi). Legacy C4 (`_score_c4_adversarial_text`) vẫn nguyên vẹn, đóng băng như `C4_LEGACY_SEMANTIC_v1` theo đúng yêu cầu — chỉ được TÁI DÙNG (import, gọi nguyên hàm) bởi `run_drift_detector()` mới, không viết lại logic của nó.

**Kết luận cuối:** `NEEDS_FIX` — xem Phần 15. Lý do ngắn gọn: kiến trúc mới cho kết quả rất hứa hẹn trên chính 5 canary episode nhưng **CHƯA có bằng chứng blind/holdout thật** (yêu cầu bắt buộc của round này) — 5/5 provenance-pass là kết quả SAU KHI đã tự vá 3 lỗi phát hiện TRÊN CHÍNH 5 topic đó, tương đương "dev corpus", không phải "holdout".

---

## 1. Kết luận kiến trúc

Giả thuyết làm việc của round này — "post-hoc semantic entailment không phải cơ chế thực thi chính đúng cho văn xuôi kể chuyện tự do; nên bảo toàn provenance QUA quá trình sinh thay vì cố tái dựng nó SAU KHI viết" — **được ủng hộ bởi bằng chứng round này, nhưng chưa được xác nhận đủ mạnh để kết luận dứt khoát** vì thiếu đánh giá blind.

Bằng chứng ủng hộ:
- Cùng 5 episode canary thật, legacy C4 (single-call, đã sửa ở round 1-3) chặn nhầm 4/5 (xem `CL_CANARY_PILOT_REPORT.md`). Kiến trúc mới, dùng ĐÚNG cùng hàm C4 (`_score_c4_adversarial_text`, không sửa 1 dòng logic nào) nhưng chỉ đưa vào phạm vi fact hẹp hơn (đã được plan chọn hợp lệ, không phải toàn bộ excerpt) → 5/5 provenance-pass sau khi vá 3 lỗi kiến trúc thật (Phần 11).
- Điều này gợi ý mạnh: **bản thân C4 không hỏng** — vấn đề là nó bị giao 1 bài toán judgment thiếu đặc tả (đoán xem văn xuôi tự do có "hợp lý" với TOÀN BỘ excerpt hay không, không biết nhà văn được phép dùng đúng những fact nào). Khi thu hẹp ground truth về ĐÚNG tập fact đã được chọn hợp lệ, C4 phán đoán chính xác hơn nhiều.

Giới hạn thật (không giấu):
- N=5, cùng 1 mẫu đã dùng suốt 4 round trước — không phải mẫu mới.
- 5/5 là SAU KHI tự vá 3 lỗi phát hiện ngay trên chính 5 topic này (Phần 11) → đây là "dev corpus" evidence, đúng kỷ luật đặt tên đã thiết lập từ round 2-3, KHÔNG được gọi là "validated" hay "holdout".
- Bộ đánh giá blind ≥5 topic hoàn toàn chưa dùng (yêu cầu bắt buộc của round này) **CHƯA được thực hiện** trong round này do giới hạn thời gian/tài nguyên thật — xem Phần 15.

## 2. Story Fact Pack — thiết kế thật đã dùng

`StoryFact{fact_id, proposition, source_spans[], source_type, risk_class, material, external_claim_id, external_status}` — `StoryFactPack{topic_id, source_file, excerpt_hash, ledger_version_at_build, facts[], pack_version}`.

- 2 chiều ĐỘC LẬP đúng yêu cầu: `source_grounded` (ngầm định true nếu fact còn trong pack — fact không grounded bị loại NGAY khi build qua `_span_exists()`, không có cách nào 1 fact không-grounded lọt vào pack) vs `external_status` (`NOT_REQUIRED` | `UNVERIFIED` | `VERIFIED` | `BLOCKED`, tra qua `cl_claim_ledger._find_ledger_match()`/`_claim_tier()` — TÁI DÙNG nguyên logic ledger, không viết lại).
- Trích 1 lượt LLM (`_FACT_EXTRACTION_PROMPT`), validate CƠ HỌC: mọi `source_spans` phải tồn tại NGUYÊN VĂN trong excerpt (substring match sau normalize) — fact không đạt bị LOẠI khỏi pack, không có ngoại lệ.
- **Yêu cầu bổ sung, phát hiện thật qua smoke test đầu tiên** (Phần 11, mục 2): propositon PHẢI tự đủ nghĩa, không chứa đại từ/từ chỉ định trỏ ra ngoài chính nó — nếu không, downstream (drift detector) không thể xác nhận được ngay cả khi văn xuôi trung thực 100% với fact.
- `pack_hash()` = sha256 của toàn bộ `facts[]` (sort_keys) — dùng làm mã định danh bất biến của 1 fact pack cụ thể, là cơ sở của mọi check chống giả mạo ở Phần 11.

## 3. Luồng bảo toàn provenance thật

```
excerpt → build_story_fact_pack() [1 LLM call + validate span cơ học + tra ledger]
        → StoryFactPack (bất biến, có pack_hash)
        → build_story_plan() [1 LLM call, CHỌN fact_id có sẵn, KHÔNG được bịa fact_id mới]
        → StoryPlan (segment[] × fact_ids[], có fact_pack_hash neo vào pack)
        → generate_bound_script() [N LLM call, 1/segment, binding LÀ CẤU TRÚC không tự khai]
        → script_text + bindings[] (mỗi binding neo pack_hash_at_generation)
        → run_deterministic_guards() [cơ học, numeric guard]
        → run_drift_detector() [N LLM call tái dùng NGUYÊN C4, scope = fact cộng dồn tới segment N]
        → run_external_verification_gate() [cơ học, check external_status thật qua ledger]
        → provenance_pass (guard+drift) và publish_ready (provenance_pass + external verified) — 2 khái niệm TÁCH BIỆT
```

Điểm thiết kế cố ý: sinh văn xuôi TỪNG SEGMENT riêng biệt (không phải 1 lượt viết cả kịch bản rồi tự báo cáo binding) — binding là cấu trúc xác định TRƯỚC từ plan, không phải tự khai của LLM sau khi viết. Đúng kỷ luật "không bao giờ tin self-report" đã áp dụng xuyên suốt phiên làm việc này.

## 4. Tái dùng hạ tầng có sẵn (không nhân đôi)

- `_score_c4_adversarial_text` (C4 legacy): tái dùng NGUYÊN, chỉ đổi `candidate.core_facts` từ "toàn bộ excerpt" xuống "fact đã plan chọn, cộng dồn tới segment N".
- `cl_claim_ledger._find_ledger_match()`, `_claim_tier()`, `HIGH_RISK_CLASSES`, `CONDITIONAL_RISK_CLASSES`, `_P0_P1_TIERS`, `load_claim_ledger()`, `load_source_tiers()`: tái dùng nguyên trong cả `build_story_fact_pack()` (tra external_status) và `run_external_verification_gate()` (check publish-readiness) — KHÔNG viết lại logic xác minh bên ngoài, KHÔNG nới điều kiện VERIFIED.
- **Đầu tư khả thi cho tương lai (chỉ khảo sát, KHÔNG triển khai round này):** cơ chế extraction của Story Fact Pack (trích mệnh đề + risk_class + material) và extraction của claim ledger (trích high-risk claim để verify) có cấu trúc tương tự nhưng phạm vi khác nhau (fact pack: mọi mệnh đề vật chất; ledger: chỉ claim rủi ro cao). Gộp 2 bước này thành 1 lượt LLM là khả thi về kỹ thuật (tiết kiệm ~1 call/topic) nhưng rủi ro làm mất tính tách bạch rõ ràng giữa "được phép kể" và "đã xác minh ngoài" — khuyến nghị KHÔNG gộp, giữ tách biệt cho tới khi có nhu cầu tối ưu chi phí thật sự cấp bách.

## 5. So sánh 5 canary: legacy C4 vs prototype

| Episode | Legacy C4 (production, round 1-3) | Prototype `provenance_pass` | Prototype `publish_ready` |
|---|---|---|---|
| Alec Jeffreys | BLOCKED_FACT (ledger, không tới C4) | PASS (5/5 segment) | **FAIL** (4 fact rủi ro cao UNVERIFIED) |
| Lockheed/FCPA | FAIL (C4, 2/2 lượt) | PASS (5/5 segment) | **FAIL** (7 fact UNVERIFIED) |
| Isdal Woman | FAIL (C4, 2/2 lượt) | PASS (5/5 segment) | **FAIL** (4 fact UNVERIFIED) |
| Max Headroom | FAIL (C4, 2/2 lượt) | PASS (5/5 segment) | **FAIL** (2 fact UNVERIFIED) |
| Maxi Trial | FAIL (C4, 2/2 lượt) | PASS (6/6 segment, sau vá) | **FAIL** (8 fact UNVERIFIED) |
| **Tổng** | **0/5 PASS, 4/5 FAIL ở C4** | **5/5 provenance_pass** | **0/5 publish_ready** |

**Đọc đúng 2 con số này KHÔNG ĐƯỢC GỘP LÀM 1 CLAIM:**
- `provenance_pass` = văn xuôi CHỈ nói đúng những fact đã được chọn hợp lệ (source-grounded, không drift) — đây là điều C4 legacy đang chặn nhầm 4/5. Prototype giải quyết đúng vấn đề này: 5/5.
- `publish_ready` = provenance_pass VÀ mọi fact rủi ro cao (forensic/security_system/motive/causal/allegation/legal_status, material=true) đã VERIFIED qua claim ledger thật (P0/P1). **0/5** — vì 5 topic này CHƯA từng có ai populate ledger thật cho chúng (đúng tình trạng "UNTESTED" đã ghi ở Phần 9 báo cáo canary gốc). Đây LÀ NÚT THẮT CỔ CHAI CÓ SẴN CỦA PRODUCTION (populate ledger thủ công), KHÔNG PHẢI hồi quy do kiến trúc mới — kiến trúc mới không hề nới lỏng yêu cầu này, chỉ làm rõ nó tách biệt khỏi vấn đề provenance.

**Kết luận thật:** kiến trúc mới giải quyết vấn đề "C4 chặn nhầm nội dung grounded" (4/5→0/5 false-block trên chính mẫu này) nhưng KHÔNG và KHÔNG ĐƯỢC tự động giải quyết vấn đề "chưa xác minh nguồn bên ngoài" — vẫn cần đúng quy trình populate ledger thủ công như production hiện tại trước khi bất kỳ episode nào trong 5 episode này có thể publish thật.

## 6. Kết quả 12 mutation test đối kháng

Chạy trên script THẬT của Maxi Trial (6 segment, provenance_pass) sau khi đã vá xong Phần 11.

| # | Mutation | Kết quả | Cơ chế chặn |
|---|---|---|---|
| 1 | 81→45 (đổi 475→290) | **BLOCKED** | Numeric guard |
| 2 | $22M→$28M (đổi 2.665→3.400) | **BLOCKED** | Numeric guard |
| 3 | 1984→1985 (đổi 1986→1987) | **BLOCKED** | Numeric guard |
| 4 | Đảo phủ định | **BLOCKED** | Drift (CONTRADICTED) |
| 5 | Đổi tên người | **BLOCKED** | Drift (CONTRADICTED) |
| 6 | suspect→perpetrator (hedge) | **BLOCKED** | Drift (UNSUPPORTED) |
| 7 | may→did (modal) | **BLOCKED** | Drift (STRONGER_THAN_SOURCE) |
| 8 | Bịa động cơ | **BLOCKED** | Drift (UNSUPPORTED) |
| 9 | Bịa hành vi kỹ thuật | **BLOCKED** | Drift (UNSUPPORTED) |
| 10 | Chèn mệnh đề không liên quan | **BLOCKED** | Drift (UNSUPPORTED) |
| 11 | Đảo chiều nhân quả | **BLOCKED** | Drift (CONTRADICTED) |
| 12 | Copy fact-binding từ topic khác | **BLOCKED** | Numeric guard (lần chạy thật) |

**12/12 BLOCKED.** Nhưng đọc kỹ mục #12: lần chạy thật, nó CHỈ bị chặn vì 2 topic (Maxi Trial vs Alec Jeffreys) tình cờ không trùng số liệu nào — numeric guard bắt được nhờ MAY RỦI nội dung, KHÔNG PHẢI vì có check cấu trúc nào xác nhận binding thuộc đúng pack. Phát hiện gap thật này ngay sau khi có kết quả, đã vá THÊM (Phần 11, mục 6: `pack_hash_at_generation` neo trong mỗi binding, kiểm tra cơ học trong `validate_binding_integrity()`) và xác minh lại bằng test cơ học riêng (không cần chạy lại 12 mutation, vì đây là guard cơ học không phụ thuộc LLM) — xác nhận: binding bị copy từ pack khác giờ bị chặn NGAY LẬP TỨC, không phụ thuộc nội dung 2 topic có trùng số hay không.

## 7. Chất lượng câu chuyện (prototype vs canary gốc)

**Giới hạn phương pháp phải nói rõ:** văn bản gốc của 5 script canary bị C4 chặn KHÔNG được lưu lại nguyên văn dưới dạng file riêng (chỉ có điểm số đã chấm tay + nhận xét trong `CL_CANARY_PILOT_REPORT.md` Phần 7) — nên đây KHÔNG PHẢI so sánh mù song song 2 văn bản, mà là chấm điểm prototype bằng CÙNG khung tiêu chí rồi đối chiếu với điểm/nhận xét đã ghi trước đó.

| Episode | Canary gốc (round 1, /10) | Prototype — nhận xét |
|---|---|---|
| Alec Jeffreys | Hook 8, CL identity **4 (yếu)** | Hook mạnh tương đương (mở bằng cảnh cụ thể 9h05 sáng); CL identity vẫn yếu tương tự — kết thúc bằng ghi nhận học thuật (huân tước, đóng góp khoa học), không phải kịch tính hình sự. **Cùng điểm yếu cấp-chủ-đề đã ghi nhận trước đó, không phải lỗi kỹ thuật mới.** |
| Lockheed/FCPA | Hook 5, CL identity **4 (yếu, giống bài giảng chính sách)** | Mở bằng câu trần thuật hành chính, không có hook rõ; kết bằng ngày ký luật — cùng vấn đề "giống bài giảng chính sách" đã ghi nhận. |
| Isdal Woman | Hook 6, Payoff **8 (kết mở đúng chất CL)** | Payoff giữ được: kết bằng "hoàn cảnh thực sự... chưa được làm sáng tỏ" — đúng công thức kết mở. Hook hơi phẳng hơn bản gốc (khai báo sự kiện thay vì câu hỏi/hình ảnh) — có thể do sinh riêng từng đoạn làm giảm khả năng tối ưu câu mở đầu tổng thể. |
| Max Headroom | Hook 8 (hình ảnh lạ), Payoff 6 (lệch tông) | Hook mạnh tương đương (giữ nguyên hình ảnh cụ thể: màn hình tối đen 15 giây); payoff giữ nguyên câu đùa gốc (Dan Roan) — cùng "lệch tông" như bản gốc ghi nhận, không tệ hơn. |
| Maxi Trial | Cognitive load **4 (quá nhiều số/tên dồn dập)** | Đoạn mở vẫn dồn nhiều số liệu (475, 120, ngày tháng) trong 1 câu — CÙNG vấn đề cognitive-load đã ghi nhận ở bản gốc, kiến trúc mới KHÔNG cải thiện vấn đề này (vì fact vẫn được nhóm theo đúng cách plan chọn, không có cơ chế nào chủ động giãn nhịp số liệu). |

**Đánh giá chung, trung thực:** không thấy suy thoái chất lượng có hệ thống so với bản gốc — các điểm yếu quan sát được ở prototype trùng khớp với đúng các điểm yếu ĐÃ ghi nhận ở bản gốc (vấn đề cấp chủ đề: chọn chủ đề khoa học-sử/chính sách sẽ luôn yếu "CL identity" bất kể kiến trúc sinh nào). **Có 1 chi phí cấu trúc thật, cần ghi nhận trung thực:** sinh văn xuôi TỪNG SEGMENT riêng biệt (bắt buộc để binding là cấu trúc, không tự khai) đánh đổi lấy khả năng tối ưu nhịp/hook/chuyển đoạn ở TẦM TOÀN BỘ câu chuyện — mỗi đoạn được viết "biệt lập" hơn 1 chút so với 1 lượt viết liền mạch cả kịch bản. Không đủ bằng chứng (N=5, không có đánh giá mù bên thứ 3) để nói chi phí này lớn hay nhỏ tới đâu — chỉ có thể nói nó TỒN TẠI THẬT về mặt thiết kế và cần theo dõi nếu mở rộng quy mô.

## 8. Kết quả an toàn (mutation) — tóm tắt

12/12 mutation bắt buộc BLOCKED (Phần 6). 0 false-pass an toàn quan sát được trong toàn bộ round này (5 canary + 12 mutation + 3 vòng vá-và-xác-minh-lại).

## 9. Chi phí vận hành

Mỗi topic: 1 (fact-pack extraction) + 1 (story plan) + N (sinh văn xuôi/segment) + N (drift detector/segment) = **2 + 2N lượt gọi LLM thật**, N=segment (5-6 trong mẫu này) → **12-14 lượt/topic**.

So với legacy C4 hiện tại (sau round 3, single-call, không còn đa số-3): **1 lượt/toàn bộ script**.

→ Prototype tốn **≈10-14× lượt gọi LLM/episode** so với legacy C4 hiện tại — chi phí thật, không nhỏ, PHẢI cân nhắc khi quyết định có mở rộng kiến trúc này hay không.

**Fact pack tái dùng được:** `load_fact_pack(topic_id)` cache theo topic_id trên đĩa — nếu retry/regenerate script cho CÙNG topic (không đổi excerpt), fact pack KHÔNG cần build lại (tiết kiệm 1 lượt/retry). Đã thêm check `excerpt_hash` (Phần 11, mục 7) để tự rebuild nếu excerpt đổi, không dùng nhầm pack cũ.

## 10. Quyết định Legacy C4: **KEEP DIAGNOSTIC** (chưa đủ căn cứ RETIRE)

- **KEEP BLOCKING** (giữ nguyên vai trò chặn chính hiện tại): KHÔNG — bằng chứng round 1-4 nhất quán cho thấy false-block rate leo thang trên nội dung mới (15%→33%→47% qua 3 corpus độc lập) và round này cho thấy khi thu hẹp scope, cùng cơ chế phán đoán chính xác hơn nhiều.
- **RETIRE hoàn toàn**: KHÔNG — chưa đủ căn cứ. Kiến trúc mới CHƯA qua đánh giá blind (Phần 15), và retire hoàn toàn nghĩa là mất luôn khả năng chặn của C4 cho pipeline free-form hiện tại đang chạy production — không có gì thay thế nó ở đó cho tới khi (nếu) kiến trúc mới được validate đủ và migrate thật.
- **→ KEEP DIAGNOSTIC**: giữ legacy C4 làm công cụ chẩn đoán/tham chiếu (không blocking chính) cho pipeline hiện tại trong lúc kiến trúc mới tiếp tục được đánh giá blind ở round tiếp theo — đúng quyết định đã đề xuất từ đầu round 4, được củng cố thêm bởi bằng chứng round này chứ chưa bị bác bỏ hay xác nhận dứt khoát.

## 11. Adversarial review — các lỗ hổng thật đã phát hiện VÀ vá trong chính round này

Phát hiện qua rà đối kháng trực tiếp lên code thật (không chỉ liệt kê lý thuyết), TẤT CẢ đã vá và xác minh lại trước khi đóng round:

1. **REFERENCE_RESOLUTION false-block (segment quy chiếu ngược qua đoạn trước)** — smoke test đầu tiên (Maxi Trial S2, "đứng đầu nỗ lực NÀY") lộ ra drift detector chặn nhầm khi scope chỉ gồm fact của riêng 1 segment. **Vá:** `run_drift_detector()` dùng scope CỘNG DỒN (fact của segment 1..N theo thứ tự plan) thay vì chỉ segment N.
2. **Đại từ/từ chỉ định dangling ngay trong chính proposition đã trích** — vá #1 KHÔNG đủ vì gốc vấn đề nằm ở EXTRACTION (fact F009 tự nó chứa "nỗ lực này" chưa resolve). **Vá:** sửa `_FACT_EXTRACTION_PROMPT` bắt buộc mệnh đề tự đủ nghĩa, resolve đại từ ngay tại thời điểm trích.
3. **Numeric guard false-positive do khác biệt định dạng chữ số/chữ viết** — fact F011 (Maxi Trial) có proposition ghi "Mười chín" (chữ) trong khi prose (đúng nguồn) dùng "19" (số) → guard cũ chỉ regex `\d+` trên proposition, không thấy "19" đâu. **Vá:** `run_deterministic_guards()` gộp `source_spans` (nguyên văn, đã validate cơ học) vào tập số liệu chấp nhận được, không chỉ `proposition`.
4. **`validate_binding_integrity()` thiếu — fact_id lạ gây crash KeyError thay vì fail-closed có kiểm soát** — hạng mục "copied fact-binding-across-scripts" trong yêu cầu round 4. **Vá:** hàm mới, chạy TRƯỚC mọi guard/drift khác, trả violation string thay vì để exception thoát crash pipeline.
5. **`generate_bound_script()` không kiểm tra `plan.fact_pack_hash`** — fact_id là namespace CHUNG (F001, F002...) không gắn topic_id, nên 1 plan bị copy từ topic khác (hoặc plan cũ trước khi pack rebuild) sẽ ÂM THẦM bind sang fact SAI. **Vá:** check hash TRƯỚC khi dùng, raise fail-closed nếu không khớp.
6. **`mutation #12` (copy binding) chỉ bị chặn nhờ may rủi nội dung, không phải check cấu trúc** — phát hiện SAU KHI chạy 12 mutation test thật và soi lại LÝ DO nó bị chặn. **Vá:** thêm `pack_hash_at_generation` neo trong mỗi binding tại thời điểm sinh, kiểm tra cơ học trong `validate_binding_integrity()` — xác minh lại bằng test trực tiếp (không cần chạy lại LLM), xác nhận chặn 100% không phụ thuộc nội dung 2 topic có trùng hay không.
7. **`run_topic()` dùng lại fact pack cũ dù excerpt đã đổi** — hạng mục "stale fact-pack hash"/"modified excerpt". **Vá:** so `pack.excerpt_hash` với hash excerpt hiện tại trước khi tái dùng cache, tự rebuild nếu lệch.
8. **THIẾU HOÀN TOÀN gate kiểm tra `external_status`** — phát hiện lớn nhất round này: `overall_pass` (đổi tên `provenance_pass`) ban đầu KHÔNG hề kiểm tra fact rủi ro cao đã được xác minh bên ngoài chưa — đúng lỗ hổng "high-risk fact without external provenance treated as if authorized". **Vá:** `run_external_verification_gate()` mới, tách biệt `publish_ready` khỏi `provenance_pass` — xác nhận qua Phần 5: 5/5 provenance nhưng 0/5 publish_ready (đúng, vì chưa ai populate ledger cho 5 topic này).

### Hạng mục đã rà nhưng KHÔNG cần vá (đã có cơ chế đúng từ thiết kế ban đầu)
- Fake fact_id trong plan → `build_story_plan()` fail-closed raise ngay từ đầu (đã thiết kế đúng, không phải vá thêm).
- Fact-pack hallucination (fact không có thật trong excerpt) → `_span_exists()` cơ học loại NGAY khi build, không có ngoại lệ.
- Segment claiming fact_ids nhưng prose mâu thuẫn / prose thêm mệnh đề không đại diện → chính là điều drift detector (C4 tái dùng) tồn tại để bắt — xác nhận qua mutation #4, #5, #10, #11.
- Legacy-C4-bypass-interaction → N/A round này vì KHÔNG có wiring nào vào production; không đường nào để prototype "bypass" 1 gate mà nó chưa hề chạm tới.

### Rủi ro tồn đọng CHƯA vá (ghi nhận, không phải bỏ sót — quyết định có chủ đích do giới hạn phạm vi)
- **Span-exists-but-doesn't-entail (MEDIUM):** hiện KHÔNG có check cơ học/semantic xác nhận `source_spans` THỰC SỰ hỗ trợ `proposition` (chỉ check span tồn tại nguyên văn, không check nó có Ý NGHĨA đúng như proposition khai). Rà tay 5 fact pack thật (61 fact tổng) không phát hiện trường hợp nào — nhưng đây là spot-check thủ công, KHÔNG PHẢI phòng thủ có hệ thống. Khuyến nghị round sau: thêm 1 lượt cross-check nhẹ (có thể tái dùng chính C4 với vai trò khác) nếu mở rộng quy mô.
- **Modified-script-post-generation:** ngoài phạm vi round này vì CHƯA có bất kỳ publish wiring nào — không có "sau khi generate" để sửa. Ghi chú THIẾT KẾ bắt buộc cho round nào wiring vào production thật: guard/drift PHẢI chạy trên văn bản CUỐI CÙNG sẽ publish, không phải bản nháp trước khi có chỉnh sửa thủ công nào.

## 12. Test suite

Production (7 file CL liên quan: `test_cl_risk_gate.py`, `test_cl_risk_gate_verification.py`, `test_cl_claim_ledger.py`, `test_criminal_law_storytelling_phase_a.py`, `test_short_batch_runner_cl_gate.py`, `test_cl_risk_gate_lifecycle.py`, `test_cl_case_batch.py`): **không có thay đổi code production round này** → không kỳ vọng hồi quy. Chạy đầy đủ cả 7 file: **364 passed, 0 failed** (216s). Không có hồi quy nào, đúng như kỳ vọng vì không file production nào bị đụng tới trong round 4.

**Prototype:** KHÔNG có bộ pytest riêng — toàn bộ xác minh round này dựa trên chạy thật (5 canary + 12 mutation + re-verify cơ học sau mỗi lần vá), không phải unit test cô lập. Đây là giới hạn thật của prototype, phù hợp với giai đoạn "chứng minh khái niệm" nhưng CẦN bộ test cố định trước khi cân nhắc bất kỳ bước wiring nào xa hơn.

## 13. Rủi ro còn lại

1. **Chưa có đánh giá blind** (Phần 15) — rủi ro lớn nhất, có thể đảo ngược toàn bộ kết luận tích cực của round này giống hệt cách holdout v1/v2 đã đảo ngược kết luận lạc quan ban đầu ở round 1-2.
2. **Chi phí ~10-14× LLM call/episode** — chưa đánh giá tác động lên latency/ngân sách thật ở quy mô 20-episode.
3. **Chi phí chất lượng câu chuyện do sinh per-segment** — chưa đo được mức độ, chỉ ghi nhận tồn tại (Phần 7).
4. **Span-entailment chưa có phòng thủ hệ thống** (Phần 11) — MEDIUM, chưa có sự cố thật nhưng chưa được chứng minh an toàn.
5. **0/5 publish_ready** — bất kỳ mở rộng thật nào của kiến trúc này CŨNG THỪA HƯỞNG nguyên nút thắt cổ chai populate-ledger-thủ-công của production hiện tại, kiến trúc mới không giải quyết vấn đề này (và không có ý định giải quyết — đúng phạm vi).

## 14. Việc KHÔNG làm trong round này (đúng phạm vi được giao)

- KHÔNG wiring prototype vào bất kỳ đường production nào.
- KHÔNG bắt đầu 20-episode pilot.
- KHÔNG sửa legacy C4 thêm.
- KHÔNG đổi kiến trúc claim-ledger.
- KHÔNG hoàn thành bộ đánh giá blind ≥5 topic mới — **đây là điểm khác biệt duy nhất so với yêu cầu ban đầu, ghi nhận trung thực, không che giấu.**

## 15. Kết luận cuối

Round này chứng minh được cơ chế provenance-preserving generation HOẠT ĐỘNG ĐÚNG NHƯ THIẾT KẾ trên 5 episode canary — giải quyết trực tiếp vấn đề C4 false-block đã quan sát 4 round liên tiếp — và phát hiện + vá 8 lỗ hổng kiến trúc thật thông qua chính quá trình xây dựng và rà đối kháng (không phải liệt kê lý thuyết). 12/12 mutation an toàn bắt buộc đều bị chặn đúng.

Nhưng: yêu cầu bắt buộc "NEW blind topic-level evaluation trên ≥5 topic hoàn toàn chưa dùng, đóng băng nhãn trước khi chạy, không tinh chỉnh sau khi thấy kết quả" **CHƯA được thực hiện** trong round này — đây là đúng loại bằng chứng đã 2 lần (round 1→2, round 2→3) cho thấy kết quả "dev corpus" lạc quan không phản ánh đúng hiệu năng thật trên nội dung mới. Không có lý do để tin round này là ngoại lệ chỉ vì kiến trúc khác — phải đo, không giả định.

`NEEDS_FIX`
