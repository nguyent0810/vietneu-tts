# Research — hiện trạng Short content generator (branch tách từ feat/content-hub-backend)

Nguồn: khảo sát code 2026-09-28. Chỉ ghi sự thật, không ghi quyết định.

## Domain, category, voice

- 3 topic (so khớp chính xác): **Phật giáo (BUD)**, **Phong Thủy (FS)**, **Hình Sự (CL)** — `domain_topics.json`, `short_batch_runner.py:262-276`.
- Voice: BUD→Binh, FS→Sơn, CL→Tuyen (`topic_voices.json`).
- Content category (`content_categories.py:19-33`): GROUNDED_DATA, EDUCATIONAL, INTERPRETATION, CREATIVE_ASTROLOGY, STORYTELLING, TRENDING.
- FS: GROUNDED_DATA (lich_hoang_dao, twelve_gods, zodiac, zodiac_month, element_color, element_luck), INTERPRETATION (iching), CREATIVE_ASTROLOGY (western_zodiac), EDUCATIONAL, STORYTELLING.
- CL: STORYTELLING (`criminal_law_short_generator.py`, cl_case/cl_story pipeline).
- TRENDING: dùng cho BUD/FS/CL.
- BUD Short = trích từ Long `*_Short.txt` của repo Content-Creator bên ngoài (marker `*** N`), rồi viết lại.
- **Lục Trụ và Mafia chưa có generator.** Mafia chỉ xuất hiện như dữ liệu vụ án CL (fixture Maxi Trial).

## Luồng sinh Short

- FS/TRENDING/CL: fact sinh bằng code (vnlunar, bảng cứng, trích nguồn) → `short_judge_panel_engine.generate_verified_script`: agy viết 3 ứng viên theo chiến lược hook A/B/C (western_zodiac 4) → Codex chấm fact-check, chọn winner, `hook_score`/10 → tối đa 3 vòng, pass khi ≥8; fail thì không ghi gì.
- BUD: `short_content_review.py:59-95` viết lại đoạn trích Long theo A (câu hỏi trực tiếp) / B (phản niềm tin) / C (tình huống cụ thể), "KHÔNG đổi Ý GIÁO LÝ".
- Runner `short_batch_runner.py:694-1199`: review → TTS → render → SEO → upload. Non-BUD bỏ qua review; CL cần Phase-A sidecar gắn hash.
- Prompt là chuỗi Python inline, không có version; thay đổi ghi trong `creator_specs/PROMPT_DELTA_*.md` (nhiều delta ghi "Nothing applied" nhưng thực tế đã áp dụng — tài liệu lỗi thời).
- "prompt 3.0.0 / declaration pipeline / Phase 4.1 / R1c" thuộc tầng analytics của Content Hub (`apps/hub`), **không liên quan** script Short.

## Tiêu chí đang có (map vào 12 tiêu chí)

| Tiêu chí | Hiện trạng |
|---|---|
| Hook | Câu 1 ~12 từ; >20 từ → cap điểm 7; judge chấm `hook_score` không có rubric rõ |
| Curiosity | Gián tiếp qua chiến lược hook |
| Value | Câu giữa phải thêm ý mới (check c) |
| Accuracy | Rubric theo category (trừ 6 generator GROUNDED_DATA tự fact-check inline); overlap ≥0.4; CL gates C1-C7 + claim ledger; TRENDING kiểm substring nguồn |
| Structure | Kết phải vọng lại hook; payoff khớp loại câu hỏi (chỉ advisory); CL: HOOK/BEAT/REVEAL/PAYOFF |
| Retention | Luật như trên; không có feedback từ retention thật |
| Narration | Check "listening-load" chỉ advisory |
| Rhythm/Pause | **Không có** (chỉ silence map theo topic: FS/BUD 0.35s, CL 0.18s) |
| Emotion | **Không có**; emotion tag bị strip ở Short |
| Originality | **Gần như không** (dedup topic, luật lặp hedge cho INTERPRETATION) |
| CTA | **Không có** ("CTA: No rule" trong CREATOR_SPECIFICATION_v2) |
| Safety | CR-1 (hedge/không khẳng định chắc chắn), luật giáo lý BUD (chỉ Long), CL gate người thật/nạn nhân vị thành niên, SEO anti-clickbait |

- Escape hatch `VIETNEU_SKIP_JUDGE_PANEL=1` bỏ qua toàn bộ judge.
- Độ dài: "~20-30 giây, 4-6 câu"; không có giới hạn ký tự.
- `hook_score` bị bỏ đi (None cho non-BUD) — mẫu "chấm rồi vứt".

## Feedback từ analytics

Không có vòng feedback vào sinh script. `youtube_analytics.py` có lấy averageViewPercentage; `short_health_check.py` chỉ nhận xét slot (BUD).

## Vấn đề chất lượng đã ghi nhận

- 6/8 Short audit mất 4-8s đầu mới vào ý; 5/8 kết ở chi tiết lỏng.
- Fact thừa rò vào script (day_type, ngày, danh sách giờ).
- Vi phạm CR-1 đã publish ("vận khí đại cát"); PR-5 đếm 31 vi phạm/12 script.
- iching lặp cách hedge.
- BUD: 2 video view cao nhưng retention thấp (31%, 25%); rubric "initial payoff" đề xuất nhưng chưa làm.
- CL canary: 3/5 hook cùng công thức câu hỏi; bản sắc CL yếu; dồn số và tên; C4 chặn 4/5 tập (báo cáo tự đánh giá cả 4 là chặn nhầm; mẫu số chỉ 5 — xem mục C4 bên dưới).
- Script E2E round 6 lặp một câu ba lần.

## Nguyên tắc hiện hành

- Brand: "accurate, humane, evidence-aware, non-manipulative, clear about uncertainty".
- Fact do code sinh, LLM chỉ diễn đạt; fail closed; con người quyết khi `needs_review`; giới hạn số lần thử.
- Director Bible chỉ về hình ảnh, không quản lời đọc.

## Dữ liệu cho Baseline snapshot (khảo sát 2026-09-28)

- **Registry local** `output/shorts/<topic>/registry.json` (`short_batch_runner.py:67`): lưu video_id, publish_at, slot_label, status, `final_script`, `hook_score`, needs_human_review. `output/` bị gitignore, **không có trong checkout này** → cần lấy từ máy chạy production.
- Script staged `drive_input/content_repo_staged/<Domain>/Short/*_Short.txt` — cũng không commit.
- Dữ liệu đã commit:
  - `creator_specs/WEEKLY_PUBLISHING_LEDGER_v1.json`: 35 item (FS 15, BUD 14, CL 6), có youtube_video_id, category, prompt version; **không có script**.
  - `analytics_reviews/2026-07-27_daily_factory_raw/*_videos_list_raw.json`: 20 video BUD + 20 FS (18 BUD, 19 FS ≤180s); không có CL.
- Hub DB (Postgres, remote): `video` (duration, format), `content_revision.audioScript`, `video_daily_metric` (per video/ngày). **Không có cột domain, category, generator, hook strategy, judge.**
- Truy ngược script: một phần (PR5 thấy nhiều entry thiếu `final_script`). Domain: có. Category/generator: gián tiếp qua prefix key/ledger. `hook_score`: có (CL và đường skip-judge lưu None).
- **Bị vứt:** chiến lược hook thắng (A/B/C/D), fact_check từng ứng viên, feedback judge, lịch sử vòng (`short_batch_runner.py:828-830` chỉ giữ hook_score, needs_human_review, final_script). Không khôi phục được cho video đã đăng.
- Metrics: `youtube_sync.py` lưu views, averageViewDuration, averageViewPercentage, likes, comments, shares, subscribers (per ngày); impressions/CTR tuỳ chọn. **Retention curve (audienceWatchRatio) và traffic source không được lấy/lưu ở đâu cả.**
- Audit có nhãn:
  - PR5_AUDIT_REPORT_v1.md: 12 script FS, phán xét từng câu (script gần như tái tạo được).
  - Audit 8 Short (retention): chỉ là comment tóm tắt `short_judge_panel_engine.py:27-39`, **không có danh sách video hay script**.
  - CL canary: 5 tập Phase A (có điểm tay), có thể chưa đăng; script không commit.
  - `analytics_reviews/2026-07-27_daily_factory_review.md`: 4 video có raw analytics, không có script.

## C4 của CL — reject được lưu ở đâu (khảo sát 2026-09-28)

- **Không lưu ở đâu cả.** Reject C4 chỉ in ra stdout và nằm trong list in-memory; không ghi vào registry.json, CL_CASE_LEDGER_v1.json hay sidecar.
  - C4 thật: `cl_risk_gate_verification.py:796-868` (`_score_c4_adversarial_text`, Codex phân loại claim; chặn khi material + UNSUPPORTED/CONTRADICTED/STRONGER_THAN_SOURCE/UNCERTAIN; lỗi → fail closed). `cl_risk_gate.py:1315` chỉ là stub.
  - Call site: `cl_risk_gate_orchestrator.py:75` (audit_log không bao giờ được ghi; `REJECTED_POLICY` không bao giờ được set), `cl_risk_gate_lifecycle.py:365`, `criminal_law_storytelling_phase_a.py:549`, `criminal_law_provenance_generator.py:69` — tất cả chỉ ghi khi PASS.
- `pilot_freeze.json`: **không có code nào đọc/ghi**; chỉ nhắc trong `handoff/CL_CANARY_PILOT_REPORT.md:23` là nằm ở scratchpad phiên làm việc cũ, không có trong repo.
- **Con số "~80%":** mẫu số chỉ là **5 tập** STORYTELLING, 4/5 bị C4 chặn (`CL_CANARY_PILOT_REPORT.md:27-35`), và chính báo cáo đó đánh giá **cả 4 là chặn nhầm** (dòng 39). `C4_REPAIR_ROUND2_REPORT.md:44` có con số khác "65-80%".
- **Đã có tập nhãn C4 cấp câu, được commit:** `handoff/c4_freeze/c4_golden_corpus_v1.json` (35 fixture), `c4_holdout_corpus_v1.json` (24), `c4_holdout_corpus_v2.json` (30); trường: id, episode, excerpt, sentence, expected, category, materiality, rationale. Không có full script, case_id, timestamp, hash.

## Seam cho Script Quality (khảo sát 2026-09-28)

- **Content và Script sinh chung một lần:** agy viết thẳng script từ `facts` (`short_judge_panel_engine.generate_candidates` :208-217). Engine không đọc `facts`, chỉ `json.dumps` vào prompt. Candidate chỉ có `{strategy, script}`.
- **Không có Content invariant tách riêng**, trừ CL provenance: `StoryFactPack` (F001…, span nguyên văn, `cl_story_fact_pack.py:68-91`) + `StoryPlan` (HOOK/BEAT/REVEAL/PAYOFF + fact_ids, `cl_story_plan_and_generation.py:36-51`) + sidecar `.story_plan.json`/`.script_binding.json` (`criminal_law_storytelling_phase_a.py:751-784`), runner kiểm lại ở `short_batch_runner.py:592-663`.
- **FS:** `facts` là dict phẳng từ vnlunar/bảng cứng, không ID; mất sau khi sinh (chỉ lưu nếu `--output-json`). Runner chỉ thấy text (`final_script = seg["text"]`, :821).
- **BUD:** đoạn trích gốc chỉ nằm trong `facts={"original_script"}` (`short_content_review.py:103`); runner không lưu (`:828-830`), chỉ còn file staged.
- **TRENDING:** `extract_facts` có excerpt kiểm substring với source (:138-142). CL legacy/case: `{topic_title, excerpt}` / `CoreFact`, không có beat plan.
- **Runner:** chọn `final_script` ở :807 (CL), :821 (FS/khác), :830 (BUD) → TTS :853. `**` và emotion tag bị bỏ trong `_short_tts_render.py` (:292, :297), registry vẫn giữ `**`.
- **Check văn bản hiện có:** câu đầu >20 từ cap 7 (engine :65, :200-204); ~12 từ chỉ trong prompt; lặp câu, listening-load chỉ là prompt LLM. **Không có** check code cho lặp câu, markup sót, câu cụt, độ dài.
- **Đường "chỉ sửa câu chữ" có sẵn:** `content_review.py` (Long BUD): findings `{quote, issue, suggested_fix}` → agy chỉ sửa câu bị chỉ ra, tối đa 3 vòng. CL `generate_bound_script` + `run_deterministic_guards` (token số phải có trong fact) là guard giữ fact bằng code duy nhất.
- **Catalog:** không có lịch sử hook/opening nào; không prompt nào nhận opening cũ. Registry theo topic (≈ Domain), không có domain/category/created_at, dùng `fcntl`. `CONTENT_CATEGORY` là hằng số trong generator nhưng không code nào đọc. Luật lặp hedge chỉ là prompt (`content_categories.py:52-55`).
