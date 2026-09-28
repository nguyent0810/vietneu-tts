# Quyết định — improve-short-content-pipeline

Ghi quyết định đã chốt trong phiên grill. Mỗi dòng: mã, quyết định, lý do ngắn.

## Vòng 1 (2026-09-28)

- **D1 — Branch:** làm trên `feat/improve-short-content-pipeline`, tách từ `origin/feat/content-hub-backend`. Không sửa trực tiếp branch cũ. Lý do: content generator chỉ tồn tại trên branch đó; mục tiêu là cả chuỗi Content → Script → Audio.
- **D2 — Ưu tiên:** P0 Content quality → P1 Script quality (đọc tự nhiên) → P2 Pipeline reliability. Không tối ưu TTS trước khi định nghĩa được thế nào là content/script tốt. Mỗi tầng có bộ quality criteria riêng.
- **D3 — Định dạng:** Short trước (stress test, ~5 Shorts/ngày). Domain model không hard-code cho Short; phải mở rộng được sang Long.
- **D4 — Issue tracker:** local markdown trong `.scratch/improve-short-content-pipeline/` (ticket trong `tickets/`). Chỉ chuyển sang GitHub khi được duyệt.
- **D5 — Ngôn ngữ tài liệu:** tiếng Việt + thuật ngữ code tiếng Anh.
- **D6 — Thứ tự grill:** Content Quality Model (theo từng content domain/channel) → Script Quality → Audio/TTS Quality → Pipeline Reliability. Chưa bàn implementation.

## Vòng 2 (2026-09-28) — Hình dạng Content Quality Model

- **D7 — Chia tầng:** Content / Script / Audio. Vòng Content Quality chỉ xét Curiosity, Value, Accuracy, Originality, Safety, Structure, CTA + Content hook. Content hook (ý tò mò) ≠ Script hook (câu chữ).
- **D8 — Cấu trúc rubric:** Base rubric → Domain overlay → Category overlay. Không tạo rubric độc lập cho từng domain/category (tránh duplication và drift).
- **D9 — Lục Trụ / Mafia:** Lục Trụ là hướng/category trong FS; Mafia là loại case trong CL. Chưa viết rubric riêng khi chưa có generator/output thật.
- **D10 — Định nghĩa "tốt":** rubric định nghĩa Content quality trước khi publish; số liệu sau publish chỉ dùng để calibration. Không vứt điểm: lưu điểm từng tiêu chí của từng Short cùng post-publish metrics.
- **D11 — Hard gate:** Accuracy FAIL hoặc Safety FAIL → Content Quality Gate FAIL. Không weighted average nào bù được. Ngưỡng cụ thể để vòng sau.
- **D12 — BUD:** chỉ chịu trách nhiệm quality tại bước cắt + rewrite trong repo này. Nguồn yếu → trạng thái "Source không đủ", fail closed, không embellish.
- **D13 — Instruction file:** chỉ dùng `AGENTS.md` (Codex CLI đọc AGENTS.md; Claude Code tự đọc AGENTS.md khi không có CLAUDE.md — docs code.claude.com/docs/en/memory#agents-md). Không tạo CLAUDE.md song song; nếu buộc phải có thì chỉ chứa `@AGENTS.md`.

## Vòng 3 (2026-09-28) — Objective của Content Quality Model

- **D14 — Thứ bậc objective:** (1) Hard constraint: Safety + Trust/Accuracy; (2) Primary outcome: Viewer Value; (3) Mechanism/signal: Curiosity + Retention. Curiosity chỉ được thưởng khi được payoff; không thưởng clickbait/promise không trả.
- **D15 — Curiosity trung thực:** tò mò phải đến từ chi tiết thật, cụ thể, có payoff; cấm claim chắc chắn, fear, misinformation. CR-1 áp dụng cho MỌI category của FS, kể cả CREATIVE_ASTROLOGY (được framing diễn giải/giải trí, không biến interpretation thành factual certainty). Hedge lặp lại là lỗi chất lượng.
- **D16 — Khi gate FAIL:** lấy từ backup pool (Short đã PASS, chưa đăng) → publish. Cấm hạ threshold để đủ 5 Short/ngày (operational target, không phải quality objective). Đo riêng False Reject Rate và False Accept Rate; false accept ở Accuracy/Safety là lỗi nghiêm trọng.
- **D17 — Value promise theo Domain:**
  - BUD: một góc nhìn áp dụng được ngay hôm nay, giữ nguyên ý giáo lý.
  - FS: hướng dẫn cụ thể cho ngày/tuổi/tháng, có hedge, người xem tự quyết (Anti-Fear-Sales).
  - CL: giải trí có thông tin — hiểu một vụ án/tình tiết/nguyên tắc pháp lý cụ thể. Entertainment là phương thức, Understanding là value chính.
- **D18 — Hai cấp chất lượng:** Short-level Content Quality Gate + Catalog-level quality (so với Short cùng Domain trong recent window: trùng Content hook, trùng hook formula, trùng takeaway, lặp opening pattern, lặp CTA). Originality không chỉ do LLM chấm trên một Short.
- **D19 — Evaluator:** mỗi tiêu chí khai báo evaluator (deterministic/code, LLM judge, human sampling). Đo được bằng code thì dùng code. `SKIP_JUDGE_PANEL` không được bypass thẳng tới Publish ở production; bypass → `needs_review` → human approval mới Publish.
- **D20 — Baseline trước, sửa sau:** baseline snapshot của Short đã đăng (views, average view %, retention curve nếu có, hook score hiện tại, vi phạm CR-1, vi phạm Safety, publish/pass rate, ước lượng false reject). Đánh giá sau 4–6 tuần; không chỉ dùng average view % — xem median/phân phối, kiểm soát topic, traffic source, độ dài nếu dữ liệu cho phép. Vòng: Baseline → Quality Model v1 → post-publish data → calibration → v1.1.

## Bổ sung sau vòng 3 — tinh chỉnh glossary (2026-09-28)

- **D21 — Glossary:** người dùng tinh chỉnh định nghĩa Value promise, Curiosity trung thực, Payoff, Catalog-level quality, Backup pool, Evaluator, Needs review, False reject/accept, Baseline snapshot, Operational target → đã cập nhật `CONTEXT.md`. Các luật đi kèm định nghĩa được giữ ở đây thay vì glossary:
  - Backup pool và Operational target không bao giờ là lý do hạ quality threshold (D16).
  - False reject phải được đo bằng human sampling để phát hiện gate quá chặt, tránh giảm sản lượng âm thầm.
  - False accept Accuracy/Safety đặc biệt nghiêm trọng khi nội dung đã Publish.
  - Mọi đường bypass judge ở production → `needs_review`, không bypass trực tiếp Content Quality Gate (D19).
  - Evaluator: đo được bằng code thì ưu tiên code (D19).

## Vòng 4 (2026-09-28) — Định nghĩa tiêu chí Content Quality

### Kiến trúc scoring
- **D22 — Thang điểm (X1):** Hard gate = PASS/FAIL + reason code (vd `ACC_UNSOURCED_CLAIM`, `SAF_CR1_CERTAINTY`). Tiêu chí scored = thang 0–4 có anchor, mỗi mức có case thật từ baseline. Advisory = ghi nhận, không chặn. `hook_score` 0–10 cũ chỉ giữ trong baseline để so sánh.
- **D23 — Tổng hợp (X2):** không bù giữa tiêu chí. Gate PASS ⇔ mọi hard gate PASS **và** mọi tiêu chí scored ≥ mức tối thiểu riêng. Tổng điểm chỉ dùng xếp hạng các ứng viên A/B/C của cùng một Short.
- **D24 — Đặt ngưỡng (X3):** human gán nhãn + chấm rubric ~30 Short (10/Domain), ưu tiên case lỗi đã biết → chọn ngưỡng sao cho mọi lỗi đã biết FAIL và false reject nhỏ nhất → LLM judge chấm lại cùng tập; tiêu chí nào judge lệch người nhiều thì chưa được làm gate. Anchor = danh sách điều kiện kiểm tra được + ít nhất một case thật, không phải nhãn "yếu/tốt".

### Tiêu chí (Base rubric)
- **D25 — Hook (Content hook):** lời hứa/câu hỏi cụ thể trong ~3s đầu, dựa trên chi tiết thật. Chỉ xét ý; "vào ý muộn" là lỗi Script hook. Evaluator: LLM judge + code kiểm chi tiết hook có trong fact set/source. Scored. Evidence: trích lời hứa, fact gốc, câu payoff. Overlay: BUD hiểu lầm/nỗi khổ đời thường; FS chi tiết ngày/tuổi, không đe doạ; CL điểm bất thường cụ thể; GROUNDED_DATA chi tiết là fact do code sinh; TRENDING nằm trong trích đoạn nguồn. Lưu nhãn hook formula (A/B/C/D) cho Catalog-level.
- **D26 — Payoff fidelity thay Curiosity:** Curiosity không còn là tiêu chí riêng. Payoff fidelity = Short trả đúng và đủ điều Content hook hứa. Evaluator: LLM judge phải chỉ ra câu payoff; không có → 0. Scored, mức tối thiểu cao (tiêu chí chặn clickbait). Chuỗi: Hook → Promise → Payoff fidelity → Value.
- **D27 — Value:** takeaway khớp Value promise của Domain và nói được bằng một câu. LLM judge viết takeaway một câu (không viết được → tối đa 1); code đo fact thừa (fact trong script ngoài tập fact được chọn). Fact thừa là lỗi Value, không phải Accuracy. CL đo thêm mật độ số/tên mỗi câu. GROUNDED_DATA phải có ≥1 hàm ý thực tế; INTERPRETATION takeaway phải được đóng khung là diễn giải.
- **D28 — Accuracy (hard gate):** mọi claim sự thật truy được về fact set/source, không vượt quá source, diễn giải đóng khung là diễn giải. Code trước (số/ngày/giờ/tên vs fact set; substring cho TRENDING), LLM sau (paraphrase giữ nghĩa), human sampling đo false accept. Evidence: claim ledger. **Bỏ word overlap ≥0.4.** Thống nhất category rubric cho 6 generator GROUNDED_DATA. BUD: giữ nguyên ý giáo lý so với đoạn trích. CL: C1–C7 + claim ledger. **(Sửa ở D48: phần 'bỏ overlap 0.4' được thay bằng candidate_id, không phải claim ledger.)**
- **D29 — Điều tra C4 trước khi sửa (đã sửa ở D43):** không kết luận C4 đúng hay sai khi chưa có mẫu số chất lượng. ~~Lấy 20 case CL bị C4 chặn~~ — giả định này sai: reject C4 không được lưu ở đâu (xem research.md, mục C4). Cách đo thay thế: D43.
- **D30 — Structure:** mạch hook → các nhịp, mỗi nhịp thêm ý mới → payoff; không lặp ý, không nhịp thừa. Việc kết có trả hook hay không thuộc Payoff fidelity. Code chặn khi có câu lặp nguyên văn ≥2 lần; LLM kiểm mỗi nhịp thêm ý mới. Scored. Category overlay: STORYTELLING HOOK/BEAT/REVEAL/PAYOFF; GROUNDED_DATA hook → fact chính → hàm ý thực tế → payoff; INTERPRETATION hook → biểu tượng → diễn giải → gợi ý.
- **D31 — Safety (hard gate):** không gây hại, không thao túng: CR-1 (chắc chắn, gây sợ, bán nỗi sợ), bóp méo giáo lý, bôi nhọ người thật, nạn nhân vị thành niên, giật gân bạo lực. **CR-1 thuộc Safety** (thao túng niềm tin), Accuracy chỉ giữ claim kiểm chứng được. Code: lexicon CR-1; LLM: bắt khẳng định chắc chắn diễn đạt lại; human sampling đo false accept. Evidence: reason code + câu vi phạm.
- **D32 — Originality (Catalog-level):** v1 advisory, trừ trùng takeaway trong window → chặn ở cấp danh mục, lấy Short từ Backup pool. Window v1 = 14 ngày cùng Domain. Code đo tương đồng; LLM chỉ gán nhãn hook formula. Điều phối tỷ lệ hook formula là việc của generator, không phải rubric.
- **D33 — CTA:** Short **không** mặc định là funnel sang Long. CTA phục vụ mục tiêu của chính Short; không trừ điểm vì không dẫn sang Long. Short trích từ Long có thể có CTA về Long tương ứng — trường hợp cụ thể, không phải objective chung. v1 advisory + ràng buộc Safety: cấm CTA dựa trên nỗi sợ. Code phát hiện CTA và lặp trong window; LLM kiểm CTA khớp Value promise. Tách hai khái niệm Short độc lập / Short trích từ Long để FS/CL có chiến lược CTA riêng mà không sửa model.

### Quy ước tài liệu
- **D34 — Vai trò tài liệu:** `CONTEXT.md` = thuật ngữ là gì; `decisions.md` = hệ thống quyết định gì; spec = phải làm gì; tests = chứng minh quyết định đúng.

## Vòng 5 (2026-09-28) — Dữ liệu baseline, gán nhãn, lưu điểm, calibration

- **D35 — Nguồn baseline (Q1):** người dùng copy `output/shorts/` từ máy production vào `.scratch/improve-short-content-pipeline/baseline/raw/` (gitignore, xem trước khi đưa vào) + export `video`, `video_daily_metric` từ Hub DB ra CSV. Trong lúc chờ, bắt đầu với dữ liệu đã commit cho FS (PR-5).
- **D36 — Retention curve + traffic source (Q2):** thêm bước lấy `audienceWatchRatio` theo `elapsedVideoTimeRatio` và `insightTrafficSourceType` thành ticket riêng (người dùng chạy vì cần OAuth). P2, không chặn việc gán nhãn.
- **D37 — Tập gán nhãn (Q3):** FS 10 từ PR-5; BUD 10 gồm bắt buộc 2 video retention 31%/25% + 8 trải đều theo average view %; CL = 6 đã đăng + case bị C4 chặn (nguồn chưa chốt, xem D41). Audit 8 Short bỏ khỏi tập nhãn (không còn danh sách video), chỉ giữ làm bằng chứng định tính.
- **D38 — Người gán nhãn (Q4):** người dùng chấm toàn bộ; LLM judge chấm mù; tiêu chí lệch >±1 ở >20% mẫu thì viết lại anchor. Người thứ hai chấm 10 mẫu nếu có — không phải dependency để bắt đầu.
- **D39 — Case "tốt" (Q5):** top performer chỉ là ứng viên; người dùng chấm theo checklist; đạt mới thành anchor. Retention cao + rubric thấp → ghi là bất thường cho calibration.
- **D40 — Quality record (Q6):** mỗi Short lưu định danh (video_id, domain, category, generator, Short độc lập/trích từ Long, nguồn Long), phiên bản (rubric version, judge model, prompt version), kết quả (điểm, reason code, evidence, evaluator từng tiêu chí), mọi ứng viên A/B/C/D + điểm + nhãn hook formula, trạng thái gate (PASS/FAIL/needs_review/Source không đủ, có bypass không). Chỗ lưu để spec quyết.
- **D41 — Calibration (Q7):** quyết định calibration chỉ khi n ≥ 30 Short/Domain/rubric version; không giảm n cho CL. Đo trong từng Domain; rank correlation + so median PASS vs baseline; không đổi rubric giữa đợt đo (đổi → version mới, reset n). **n ≥ 30 là điều kiện để kết luận, không phải điều kiện để chạy:** khi chưa đủ n, gate, logging, quality record, post-publish metrics, đo False Reject/False Accept và ghi case bất thường vẫn chạy; chỉ cấm dùng dữ liệu đó để đổi threshold hoặc hạ tiêu chí scored → advisory. Thiếu dữ liệu → thiếu quyền kết luận, không phải giảm tiêu chuẩn.
- **D42 — Nguồn 20 case C4 (Q3 follow-up):** chưa chốt; không suy đoán path. Phải xác minh: case có tồn tại, file nào là source of truth, đủ script để blind-label, có timestamp/version để khử trùng.

## Vòng 5 follow-up (2026-09-28)

- **D43 — Đo C4 (Q8):**
  - (a) Quality record bền vững cho **mọi** Short đã qua Content Quality Gate: PASS, FAIL, Source không đủ, needs_review. Record FAIL lưu đủ để sau này xác định False Reject: script, source excerpt, case_id nếu có, timestamp, rubric version, reason code.
  - (c) Dùng golden/holdout C4 hiện có (89 fixture) để đo false reject **cấp câu** ngay bây giờ.
  - Không suy ra False Reject cấp Short từ fixture cấp câu. Hai đơn vị đo khác nhau, báo cáo riêng: một Short FAIL khi chỉ một câu FAIL.
- **D44 — Gate decision + reason code:** không chỉ lưu PASS/FAIL. Mỗi record lưu `gate_status` và danh sách `reason_codes` (một Short có thể FAIL vì nhiều lý do, vd Safety CR-1 + Accuracy source mismatch + Structure repetition), để calibration biết gate nào đang quá chặt. Bổ sung D40.
- **D45 — Phạm vi spec đầu tiên (Q9 = c):** chỉ spec phần đã đủ quyết định và không phụ thuộc anchor/threshold:
  1. Baseline snapshot
  2. Lấy retention curve + traffic source
  3. Quality record bền vững cho mọi gate outcome
  4. Ghi nhận Content Gate FAIL / Source không đủ
  5. Loại đường bypass `SKIP_JUDGE_PANEL` khỏi production Publish path
  6. Bỏ word overlap 0.4
  7. Đánh giá C4 cấp câu bằng golden/holdout
  Không đưa anchor/threshold chưa calibration vào spec. Sau đó to-tickets → `/compact` → grill Script Quality → Audio Quality → Pipeline Reliability, rồi spec tổng thể bốn tầng.
  Chuỗi: Content decisions → to-spec (phần đủ quyết định) → to-tickets → implement instrumentation → baseline + labels → anchor/threshold calibration → Content Quality Model v1.

## Seam cho spec đầu tiên (2026-09-28)

- **D46 — S1 Content Quality Gate là seam duy nhất:** điểm hội tụ mọi outcome của BUD, FS, TRENDING, CL trước Publish: generator PASS, generator FAIL/không sinh script, fact-check không PASS, dưới threshold, CL gate FAIL, SKIP_JUDGE_PANEL, Source không đủ, needs_review. Runner không tự diễn giải outcome theo domain. S1 vừa là gate vừa là audit boundary: giữ nguyên **source outcome** (source, raw_status, raw_reason) bên cạnh Gate decision đã chuẩn hoá (status, reason_codes).
- **D47 — Kho Quality record:** append-only, JSONL theo Domain, tách khỏi registry. Registry không phải source of truth, chỉ giữ reference nếu cần. Có record cho PASS/FAIL/needs_review/Source không đủ. Record có identity bất biến và version đủ để truy nguyên, tối thiểu: quality_record_id, created_at, domain, video_id/content_id, rubric_version, generator_version, judge_model, gate_status, reason_codes, source_outcome, evidence. Schema đầy đủ không chốt ở grill. Hub ingest ngoài scope.
- **D48 — Thay overlap 0.4 (sửa D28):** judge không được trả script mới, chỉ trả `candidate_id` của ứng viên thắng; code lấy nguyên văn ứng viên. candidate_id không tồn tại hoặc verdict không hợp lệ → reject verdict. Bỏ text overlap 0.4.
- **D49 — SKIP_JUDGE_PANEL:** giữ cho debug; khi bật, mọi domain → gate status `needs_review`, reason code `BYPASS_JUDGE`, không `scripted`, không auto-upload/publish. Test bắt buộc cho CL và mọi domain dùng chung engine.
- **D50 — Retention curve + traffic source:** spec này chỉ fetch và ghi vào baseline local; Hub schema + ingest ngoài scope. Không vì thế mà bỏ hai dữ liệu này khỏi baseline v1.
- **D51 — Test và Windows:** S1–S5 không phụ thuộc `fcntl`, chạy được trên Windows. Test cần `registry_lock` là nhóm CI/WSL test. Kiểm tra môi trường 2026-09-28: máy chỉ có distro `docker-desktop` (không có WSL distro để dev), có Docker → nhóm test registry chạy qua CI Ubuntu hoặc container; đây là prerequisite của riêng nhóm đó, không phải dependency của S1–S5.

## Duyệt spec + tickets (2026-09-28)

- **D52 — Fail closed khi ghi Quality record:** áp dụng cho Publish path. Ghi record lỗi → Short đó bị chặn khỏi Publish; không bắt buộc crash cả batch, batch tiếp tục với Short khác.
- **D53 — rubric_version:** record của spec đầu tiên dùng `"legacy"`. Không thay thế version thực tế khác (generator_version, judge_model, prompt_version vẫn ghi giá trị thật).
- **D54 — Reason code:** tập đóng, tiền tố `ACC_`, `SAF_`, `STR_`, `JUDGE_`, `SRC_`, `BYPASS_`. Outcome chưa map được **không** được map ngầm vào code gần giống: dùng reason code dành cho unmapped/internal (vd `INTERNAL_UNMAPPED`) + Gate status `needs_review`.
- **D55 — CI trên branch:** ticket 01 là prerequisite vận hành của các ticket integration (cần chạy test registry/runner), không phải dependency của unit test độc lập.
- **D56 — Cấu trúc ticket:** 01, 02, 03, 04, 05a (S1 → CL sidecar + Phase A/C4), 05b (S1 → CL orchestrator escalation + CL generators/storytelling/educational), 06, 07, 08, 09, 10. Không gộp 03 vào 02 (02 lập seam, 03 mở rộng coverage). Dependency: 02→03, 02→04, 02→05a→05b, 03+04+05b→06, 09→10. 07, 08, 09 độc lập (07 test được candidate_id mà không cần S1; nối S1 qua cơ chế chung của engine outcome). Frontier ban đầu: 01, 02, 07, 08, 09. Không thêm dependency chỉ vì hai ticket cuối cùng tích hợp cùng một seam.
- **D57 — Nguyên tắc vòng Script Quality:** không biến vấn đề TTS hiện tại thành solution; trước hết xác định Script Quality Model muốn đo gì, rồi mới quyết seam/code.

## Script Quality — Vòng 1: objective và model (2026-09-28)

- **D58 — Objective Script Quality:** "Cách viết để đọc có giúp nội dung được truyền đạt rõ, tự nhiên và giữ người xem không?" Thứ tự khi xung đột: ràng buộc (Script fidelity, toàn vẹn văn bản) → Rõ (hiểu ở lần nghe đầu) → Tự nhiên (văn nói, đúng giọng Domain) → Giữ người xem. Mẹo giữ người xem làm giảm độ rõ/tự nhiên là lỗi, không được cộng điểm.
- **D59 — Ranh giới Content/Script (phép thử viết lại):** sửa được chỉ bằng viết lại câu chữ mà giữ nguyên claim, thứ tự ý, Payoff → lỗi Script; phải đổi ý/fact/thứ tự ý/Payoff → lỗi Content. Áp dụng: hook chậm do dạo đầu → Script hook, do thứ tự ý → Structure; thiếu Payoff → Payoff fidelity, câu cuối lơi → Script; có hedge → Safety/CR-1, lặp hedge → Script + Catalog; dồn số/tên, lặp câu → Script.
- **D60 — Ranh giới Script/Audio:** Script chấm văn bản viết để nghe, độc lập giọng và engine. Chỉ tồn tại khi đọc thành tiếng (ngữ điệu, phát âm, khoảng nghỉ thật, tốc độ thật, cảm xúc giọng) → Audio. Rhythm: nhịp câu chữ ∈ Script, khoảng nghỉ thật ∈ Audio. Emotion: sắc thái lời văn ∈ Script, cảm xúc giọng ∈ Audio.
- **D61 — Tiêu chí Script Quality Model:** S-a Script hook, S-b Nghe hiểu ngay (listenability), S-c Mạch câu, S-d Câu chốt, S-e Tự nhiên + giọng Domain, S-f Tiết kiệm, S-g Độ dài phù hợp (S-g là check, không phải điểm chất lượng). S-c/S-d không gộp vào Structure của Content (tách được bằng D59).
- **D62 — Hard gate tầng Script:** (1) **Script fidelity**: lời văn không tạo claim mới, không làm mạnh claim quá Claim ledger (Short trích từ Long: so với đoạn trích nguồn); (2) **Toàn vẹn văn bản**: không lặp câu, câu cụt, markup/ký hiệu sót vào lời đọc. Không bù điểm. Từ ngữ vi phạm CR-1 vẫn là Content Safety; cùng một lỗi không bị đếm ở cả hai tầng.
- **D63 — Script hook đo bằng khoảng cách tới điểm móc:** số từ trước chi tiết móc của Content hook, quy ra giây theo 170–200 wpm, cộng độ rõ câu đầu. Luật "câu đầu ~12 từ / >20 từ cap 7" chỉ là diagnostic baseline, không phải định nghĩa chất lượng (ví dụ câu 10–12 từ vẫn có thể toàn dạo đầu). Ngưỡng giây chỉ đặt sau calibration với retention 3–5s đầu (ticket 09).
- **D64 — Retention theo câu là calibration evidence:** pre-publish chỉ chấm S-c; post-publish căn retention curve theo mốc thời gian từng câu để tìm câu làm rời người xem. Không biến thành tiêu chí "dự đoán retention" trong Script Quality. Chưa kết luận khi n < 30/Domain. Nếu dữ liệu cho thấy S-c không liên hệ với retention thì sửa hoặc bỏ S-c theo nguyên tắc calibration của Content.
- **D65 — Overlay + thang điểm Script:** dùng lại khung Content: Base → Domain overlay → Category overlay, thang 0–4 có anchor, evaluator theo tiêu chí, Quality record có trường tầng. Domain overlay Script viết dưới dạng kiểu lỗi đã biết (CL: dồn số/tên, lặp công thức câu hỏi; FS: lặp hedge, câu dày can chi; BUD: giọng giảng đạo, câu văn viết dài), không phải hướng dẫn văn phong. Anchor để trống tới khi có baseline; anchor lấy từ case thật, không viết ở vòng 2.

## Script Quality — Vòng 2: rewrite, evaluator, Catalog-level (2026-09-28)

- **D66 — Phạm vi rewrite khi FAIL:** lỗi Script (kể cả hard gate Script fidelity, Toàn vẹn văn bản) → chỉ rewrite Script, giữ Content invariant. Lỗi Content → regenerate cả Short, không vá bằng câu chữ. Content và Script không được trộn khi rewrite. Hết số lần rewrite → Backup pool, không hạ ngưỡng; số lần giữ như hiện tại tới khi có baseline.
- **D67 — Content invariant + chạy lại gate:** Content invariant = Content hook (chi tiết móc), Claim ledger, thứ tự ý, Payoff, + đoạn trích nguồn nếu Short trích từ Long. Rewrite làm đổi bất kỳ phần nào → coi là đổi Content, về Content gate. Luồng: Content invariant giữ nguyên → Script rewrite → Script Quality Gate → chạy lại hard gate của Content Quality Gate. "Chỉ sửa Script" không có nghĩa Content Gate pass một lần là vĩnh viễn. Nơi lưu/dạng lưu Content invariant là câu hỏi seam, để sau.
- **D68 — Evaluator theo tiêu chí Script:** Toàn vẹn văn bản: code (lặp câu, sót markup/ký hiệu) chạy trước + LLM (câu cụt). Script fidelity: LLM so Claim ledger/nguồn, không chắc → Needs review. S-a: LLM đánh dấu vị trí chi tiết móc, code đếm từ/quy giây (LLM không chấm). S-b: code cho tín hiệu chẩn đoán + LLM chấm. S-c, S-d: LLM + human sampling. S-e: LLM + human sampling bắt buộc. S-f: code (lặp nguyên văn) + LLM (lặp ý, lặp hedge). S-g: code (check). Code không tự biến tín hiệu chẩn đoán thành điểm.
- **D69 — Điều kiện evaluator LLM:** evaluator khác model writer; mỗi finding kèm evidence (câu/cụm cụ thể) dùng cho reason code và feedback rewrite; chấm từng tiêu chí riêng, không điểm tổng chia ngược. Không lặp mẫu `hook_score` không evidence.
- **D70 — Human sampling:** người chấm nghe audio cuối cùng, rồi phân tầng từng lỗi Script/Audio bằng Phép thử viết lại. Không phân tầng được → nhãn `chưa phân tầng`, không đoán. Mục đích: tránh đẩy mọi lỗi nghe khó chịu về Script.
- **D71 — Catalog-level đo concentration:** mỗi Short gán Opening pattern trừu tượng (theo cảm nhận người xem, không theo nhãn chiến lược A/B/C/D); đo tỷ trọng pattern trong recent window theo Domain. Không whitelist/blacklist, không giao pattern cho writer; khi pattern quá dày chỉ báo writer tránh các pattern đang dày. Nhãn chiến lược vẫn lưu để chẩn đoán (A/B/C/D có thể là nguồn của lặp).
- **D72 — Phạm vi và tác dụng Catalog-level:** phủ Opening pattern, pattern câu chốt, cách hedge, câu chữ CTA, signature phrase. Chỉ là tín hiệu mềm, không bao giờ là hard gate. Kích thước window và ngưỡng tập trung để trống tới baseline.
- **D73 — Domain voice vs Surface pattern:** Domain voice (register, xưng hô, độ trang trọng, nhịp điển hình) = đồng nhất, Catalog-level không đo. Surface pattern (câu mở, câu chốt, cụm cố định) = đa dạng, Catalog-level đo. Tránh lỗi ngược: chống lặp đến mức mỗi video đổi giọng, mất identity kênh.

## Script Quality — Vòng 3: Short trích từ Long, baseline cũ (2026-09-28)

- **D74 — Script fidelity với đoạn trích:** được diễn đạt lại khi giữ nguyên nghĩa. Trích dẫn trực tiếp (lời kinh, lời Phật, lời thầy) giữ nguyên văn; diễn đạt lại thì không được trình bày như câu trích. Thuật ngữ giáo lý không thay bằng từ đời thường làm lệch nghĩa. Vi phạm → FAIL hard gate Script fidelity, reason code riêng theo loại.
- **D75 — Tự đứng được (overlay Short trích từ Long):** không sót tham chiếu tới Long ("như đã nói", "câu chuyện trên", đại từ chỉ ngữ cảnh Long). Sửa được bằng câu chữ → lỗi Script; cần bổ sung ngữ cảnh → lỗi Content (đổi Content invariant, về Content gate).
- **D76 — Đảo thứ tự ý của đoạn trích:** được phép nhưng là đổi Content (D67), phải về Content gate; không tính là Script rewrite.
- **D77 — Giọng Short trích từ Long:** Domain voice giữ như tập Long (D73); dạng câu chuyển sang văn nói short-form. Câu châm ngôn văn viết giữ nguyên vẫn bị chấm S-b, S-e; không miễn vì "nguyên văn".
- **D78 — `script_provenance` (thứ bậc nguồn):** `exact` (registry `final_script`) → `revision` (Hub `content_revision.audioScript`, phải khớp revision lúc đăng) → `rendered` (`.srt` + manifest Drive: đúng lời đã đọc, mất `**`, số thành chữ, có timing thật) → `source_only` (`*_Short.txt` staged) → `missing`. Kèm trạng thái xác minh `verified`/`unverified`. Không reconstruct bằng ASR. Người vận hành tự export Drive/Hub. Provenance phục vụ độ tin cậy dữ liệu calibration, không phải tiêu chí chất lượng.
- **D79 — `source_only` không bao giờ là `final_script`:** chỉ là tham chiếu để kiểm Script fidelity; không dùng để chấm chất lượng script đã đăng. Không xác định được text thực sự đã publish → `Source không đủ`, không reconstruct bằng suy đoán.
- **D80 — Tiêu chí chấm được theo tầng nguồn:** `exact`/`revision` verified: mọi tiêu chí. `rendered`: S-a (giây thật), S-c, S-d, S-e, S-f, S-g, phần lặp câu của Toàn vẹn văn bản; S-b một phần; không kiểm được sót markup. Script fidelity chỉ khi có tham chiếu (đoạn trích `source_only` cho BUD, phán xét PR-5 cho 12 script FS), không có → `Source không đủ`. Chiến lược hook thắng, lịch sử vòng, fact-check, feedback judge → `Source không đủ` vĩnh viễn; không đoán A/B/C/D từ lời văn; Opening pattern được gán từ text. Claim ledger FS không sinh lại bằng code hiện tại để coi như ledger lúc đăng; nếu dùng thì gắn `tái tạo`, tách riêng, không tính vào kết luận Script fidelity.
- **D81 — n theo tiêu chí:** n = số Short thực sự chấm được cho từng tiêu chí, không phải số Short thu thập (vd BUD tổng 30: S-a n=28, S-b n=24, Script fidelity n=17). Không ghi một con số n chung. Báo cáo tách theo `script_provenance`; gộp tầng trừ khi phân bố lệch rõ. Short `missing` chỉ ở baseline metrics.

## Phạm vi sau Script Quality (2026-09-28)

- **D82 — Không mở Audio Quality Model trong phạm vi hiện tại:** mục tiêu là Content Creator + Audio Script Creator. Sau Script Quality → anchor/threshold → spec → tickets → implementation. Audio Quality và Pipeline Reliability ngoài phạm vi hiện tại (thay thứ tự trong README cũ). Nhãn `chưa phân tầng` (D70) vẫn giữ để không đẩy lỗi Audio về Script.

## Seam Spec 2 — Script Quality Instrumentation (2026-09-28)

- **D83 — Tạo Content invariant (S6):** nguồn claim do code ghi (FS `facts`, CL fact pack, BUD/TRENDING đoạn trích); Content hook, thứ tự ý, Payoff do LLM trích từ script thắng, gắn `derived_by: llm` + span evidence; CL provenance lấy deterministic từ `StoryPlan`. Thiếu trường → ghi lý do; invariant không đủ → không được Script rewrite, về Needs review. Không refactor generator thành Content Plan → Script trong Spec 2.
- **D84 — Script fidelity shadow (S9):** chạy và ghi finding có evidence, không chặn Publish. Shadow finding ≠ Gate PASS/FAIL; chỉ là dữ liệu calibration. Chỉ S8 Toàn vẹn văn bản là gate chặn thật trong Spec 2 (deterministic).
- **D85 — Script rewrite tối thiểu (S11):** Spec 2 chỉ chuẩn hoá S8 finding → rewrite contract → candidate rewritten script → deterministic invariant guard (token claim giữ nguyên, không token số mới; vi phạm = đổi Content → về Content gate). So sánh invariant bằng LLM chạy shadow. Chưa xây retry loop, retry count, feedback loop đầy đủ hay tối ưu rewrite; để spec sau nếu baseline cho thấy cần.
- **D86 — Opening pattern (S12/S13):** LLM mô tả pattern tự do + evidence; code tính fingerprint N từ đầu đã chuẩn hoá. Không cố định taxonomy trước baseline; không threshold; không blacklist/whitelist; không đưa feedback "tránh pattern" vào writer. Concentration signal chỉ advisory, không có quyền FAIL.
- **D87 — Một Quality record store duy nhất:** Content (S1), Script (S7), Catalog (S12/S13) ghi vào store của Spec 1, phân biệt bằng trường `layer`. Catalog history đọc từ Quality record, không store mới, không `fcntl`. S6, S8, S10 độc lập; S7, S12, S13 tích hợp sau khi seam S1/Quality record (ticket 02) tồn tại.
- **Sau Spec 2:** ưu tiên implementation tạo dữ liệu baseline trước khi viết anchor. Spec 2 không được thành rubric mới bằng cảm tính.

## Duyệt Spec 2 (2026-09-28)

- **D88 — Tiền tố reason code `SCR_`:** thêm vào tập đóng D54 (vd `SCR_REPEATED_SENTENCE`, `SCR_LEFTOVER_MARKUP`, `SCR_TRUNCATED`, `SCR_INVARIANT_INCOMPLETE`).
- **D89 — `rubric_version` record Script:** `"script-instrumentation-v0"`, tách khỏi `"legacy"` của Content và khỏi v1 sau này.
- **D90 — Một lần gọi evaluator:** trích invariant (hook/thứ tự ý/Payoff), fidelity shadow, span điểm móc, mô tả Opening pattern gộp trong một lần gọi; đầu ra vẫn tách từng phần, mỗi phần có evidence, không điểm tổng (giữ D69).
- **D91 — S8 chỉ chặn lỗi chắc chắn:** lặp câu và markup/ký hiệu sót → chặn. Câu cuối thiếu dấu kết → finding không chặn (có thể cố ý kết bằng `…` hoặc câu hỏi).
- Spec 2 được duyệt; chạy to-tickets.
- **D92 — Tickets Spec 2:** 11 (S8), 12 (chẩn đoán code + fingerprint), 13 (invariant zodiac), 14 (S7 zodiac), 15 (invariant mọi đường), 16 (S7 mọi đường), 17 (evaluator shadow), 18 (rewrite contract + guard), 19 (concentration), 20 (S8 + chẩn đoán trên baseline). Không gộp 11+12 (finding/gate vs measurement) hay 15+16 (dữ liệu invariant vs kiểm chứng mọi đường qua S7). Dependency: 14←02,11,12,13 (giữ 12 để record S7 đủ instrumentation từ integration đầu); 17←13,14 (không cần 16); 18←13,14; 19←14; 15←13; 16←14,15,03,04,05b; 20←10,11,12. Frontier Spec 2: 11, 12, 13.
