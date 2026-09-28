# Interview log — improve-short-content-pipeline

Nhật ký các vòng grill (câu hỏi, đề xuất của agent, câu trả lời). Quyết định rút gọn nằm ở `decisions.md`.

## Vòng 1 — Phạm vi và setup

- **Q1 Branch** — đề xuất: branch mới từ `feat/content-hub-backend`. Trả lời: (a), tên `feat/improve-short-content-pipeline`; cần cả content generator để tìm nguyên nhân gốc.
- **Q2 "Cải thiện" là gì** — đề xuất: script đọc tự nhiên trước. Trả lời: (d) kết hợp, thứ tự P0 content → P1 script → P2 pipeline; phân biệt Content / Script / TTS-audio quality, mỗi tầng một bộ criteria.
- **Q3 Định dạng** — đề xuất: Short. Trả lời: Short trước, nhưng domain model không hard-code cho Short.
- **Q4 Issue tracker** — đề xuất: local. Trả lời: `.scratch/improve-short-content-pipeline/` với research, interview, decisions, content-quality, audio-quality, pipeline-quality, test-matrix, tickets/.
- **Q5 Ngôn ngữ** — trả lời: tiếng Việt + thuật ngữ code tiếng Anh (Đoạn short/segment, Khoảng nghỉ/gap, Kịch bản đọc/narration script, Từ điển phát âm/pronunciation dictionary, Content Quality Gate, Publish Gate, Retention, Hook, CTA).
- **Yêu cầu thêm:** grill định nghĩa "một Short là content tốt khi nào" theo 12 tiêu chí (Hook, Curiosity, Value, Accuracy, Structure, Retention, Narration, Rhythm/Pause, Emotion, Originality, CTA, Safety), phân theo content domain (Phật giáo; Phong thủy/12 con giáp/Lục Trụ; Crime/Mafia/Law).

## Vòng 2 — Hình dạng Content Quality Model

- **Q1 Chia tầng 12 tiêu chí** — chấp nhận; vòng này chỉ Content + ý hook; Content hook ≠ Script hook.
- **Q2 Trục rubric** — (c) Base + Domain overlay + Category overlay.
- **Q3 Lục Trụ/Mafia** — (b) Lục Trụ ∈ FS, Mafia ∈ CL; chưa viết rubric riêng.
- **Q4 Đo "tốt"** — (c) rubric trước publish, metrics để calibration; lưu điểm từng tiêu chí.
- **Q5 Gate vs điểm** — Accuracy/Safety là hard gate, không bù bằng điểm khác; ngưỡng để sau.
- **Q6 BUD** — (a) chấm ở bước cắt + rewrite; nguồn yếu → fail closed, không embellish.
- **Q7 Instruction file** — ưu tiên AGENTS.md, kiểm tra agent nào đọc file nào, không tạo hai file trùng. → Đã kiểm tra, chỉ tạo AGENTS.md.
- **Yêu cầu vòng 3:** grill objective của Content Quality Model trước (value, retention, trust, curiosity, publish an toàn), rồi mới định nghĩa tiêu chí, scale, anchor, gate, threshold, cách tổng hợp, lưu điểm, calibration. Dùng evidence trong research.md để challenge.

## Vòng 3 — Objective

- **Q1 Đích vs phương tiện** — chấp nhận: constraint (Safety, Trust) → outcome (Value) → mechanism (Curiosity, Retention).
- **Q2 Trust vs Retention** — (b) curiosity trung thực; CR-1 cho mọi category FS kể cả CREATIVE_ASTROLOGY; hedge lặp là lỗi.
- **Q3 Gate chặn** — (b) backup pool, cấm hạ ngưỡng; đo False Reject/False Accept Rate.
- **Q4 Value promise** — chấp nhận BUD/FS; sửa CL thành "giải trí có thông tin, hiểu một vụ án/tình tiết/nguyên tắc pháp lý cụ thể".
- **Q5 Đơn vị chấm** — (b) Short-level + Catalog-level (trùng hook, hook formula, takeaway, opening, CTA).
- **Q6 Evaluator** — (b) khai báo evaluator mỗi tiêu chí; code trước LLM; SKIP_JUDGE_PANEL → needs_review.
- **Q7 Thành công** — baseline trước; metrics mở rộng; phân phối + kiểm soát biến nhiễu; chu trình v1 → calibration → v1.1.

## Vòng 4 — Định nghĩa tiêu chí

- **X1, X2, X3, Q1–Q7:** OK toàn bộ theo khuyến nghị (xem D22–D32).
- **Q8 CTA:** Short không mặc định là funnel sang Long; CTA phục vụ chính Short; Short trích từ Long có thể CTA về Long tương ứng. Tách Short độc lập / Short trích từ Long.
- **Ghi chú người dùng:** C4 không sửa ngay (mẫu số chưa rõ); anchor vòng 5 phải là điều kiện kiểm tra được + case thật, không phải nhãn.

## Vòng 5 — Baseline, nhãn, lưu điểm, calibration

- **Q1–Q6:** OK (D35–D40). Q4: người thứ hai không phải dependency.
- **Q7:** không giảm n cho CL; CL chạy v1 lâu hơn; n ≥ 30 là điều kiện kết luận, không phải điều kiện chạy (D41).
- **Follow-up nguồn 20 case C4:** không đoán; kiểm tra registry CL, pilot_freeze.json; xác minh tồn tại, source of truth, đủ script, timestamp/version (D42).

## Vòng 5 follow-up

- **Q8:** (a) + (c); sửa D29; gate decision + reason codes; tách sentence-level vs Short-level.
- **Q9:** (c) spec 7 hạng mục không phụ thuộc anchor; rồi to-tickets; `/compact` trước Script Quality.

## Script Quality — Vòng 1: objective và model (2026-09-28)

- Đã hỏi Q1–Q8 (objective, ranh giới Content/Script/Audio, đơn vị đo, danh sách tiêu chí, hard gate, Script hook, retention theo câu, overlay + thang điểm). Chờ trả lời.
- **Trả lời:** Q1–Q8 OK (D58–D65). Nuance: Q5 — "không tạo/làm mạnh claim" là Script fidelity, CR-1 vẫn là Content Safety, không double-count. Q7 — retention theo câu là calibration evidence, không thành tiêu chí dự đoán retention; S-c phải sửa/bỏ nếu không liên hệ retention. Q6 — 12/20 từ là diagnostic baseline, không phải quality definition.
- **Vòng 2 phạm vi:** Script FAIL rewrite phần nào; evaluator cho S-a→S-g; Catalog-level cho opening pattern mà không thành template cứng. Chưa viết anchor 0–4.

## Script Quality — Vòng 2: rewrite, evaluator, Catalog-level (2026-09-28)

- **Trả lời:** Q1–Q8 OK (D66–D73). Nhấn mạnh: Content và Script không trộn khi rewrite; rewrite phải chạy lại hard gate Content. Code không biến diagnostic thành score; LLM phải có evidence; người chấm nghe audio rồi phân tầng, không phân tầng được → `chưa phân tầng`. Domain voice = consistency, Surface pattern = diversity.
- **Vòng 3 phạm vi:** overlay/constraint riêng của Short trích từ Long; mức reconstruct baseline cho Short thiếu `final_script` và phần nào là `Source không đủ`. Sau đó sang Audio Quality.

## Script Quality — Vòng 3: Short trích từ Long, baseline cũ (2026-09-28)

- **Trả lời:** Q1–Q8 OK (D74–D81). Khoá: `source_only` tuyệt đối không phải `final_script`, chỉ là tham chiếu Script fidelity; không xác định được text đã publish → `Source không đủ`. `script_provenance` vào baseline (mở rộng ticket 10), gồm 5 tầng + trạng thái xác minh; không phải tiêu chí chất lượng. n theo từng tiêu chí, không ghi n chung.
- **Phạm vi:** không mở Audio Quality; sau Script Quality → anchor/threshold → spec → tickets → implementation (D82).

## Duyệt seam Spec 2 (2026-09-28)

- **Trả lời:** Q1, Q2, Q4, Q5 OK; Q3 OK có giới hạn: S11 chỉ contract + seam tối thiểu, chưa có retry/rewrite loop đầy đủ (D83–D87). Nhấn mạnh shadow finding ≠ Gate PASS/FAIL; một Quality record store cho Content/Script/Catalog. Out of scope giữ rõ: anchor, threshold, Script score làm publish gate, Script fidelity hard gate, Catalog threshold, Audio, TTS engine, Pipeline Reliability.

## To-tickets Spec 2 (2026-09-28)

- Q1–Q4 chi tiết spec OK (D88–D91); spec duyệt.
- Breakdown 11–20 duyệt, không gộp; dependency giữ nguyên; giữ ticket 20 với các khoá provenance/n/không threshold (D92).
