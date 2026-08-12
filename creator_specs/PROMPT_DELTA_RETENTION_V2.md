# Prompt Delta — Retention v2 (ÁP DỤNG, sau 3 vòng Codex adversarial review)

**Nguồn:** `generator_retention_audit_v2.md` (2 vòng phân tích độc lập) + `audio_script_quality_rubric_v1.md` (1 vòng phản biện) — cả 2 tài liệu thiết kế, không copy lại nội dung ở đây.

**Quy trình review:** draft v1 → Codex round 1 (2 vấn đề tổng thể: Delta C overclaim, blast radius quá rộng cho engine dùng chung) → v3 (hạ Delta A/C xuống soft/advisory, thu hẹp Delta B chỉ INTERPRETATION) → Codex round 2 (2 HIGH mới: worked example tự vi phạm rubric, Delta A tự mâu thuẫn về JSON schema) → tự sửa 2 lỗi cơ học cuối (không chạy thêm vòng Codex, tự verify vì đây là lỗi rõ ràng không cần phán đoán thêm) → áp dụng code.

## Đã áp dụng (3 file, py_compile + pytest 201/202 pass, 1 fail không liên quan)

### 1. `short_judge_panel_engine.py` — Delta A (Type-matched Payoff) + Delta C (Listening-load)
Thêm 2 dòng THAM KHẢO vào `_RETENTION_RULES_BLOCK`, thêm sub-check (d)/(e) vào `_RETENTION_CHECK_BLOCK`. **CẢ HAI ĐỀU SOFT/ADVISORY** — chỉ ghi vào `feedback`, KHÔNG ép trần `hook_score`, KHÔNG thêm field JSON mới, không code enforcement. Áp dụng cho MỌI generator (vì không hard-gate nên rủi ro thấp).

### 2. `content_categories.py` — Delta B (Repetitive Framing mở rộng), CHỈ rubric `INTERPRETATION`
Thêm điều khoản mở rộng: ≥3 câu liên tiếp cùng NHỊP NGHE (không chỉ cùng từ vựng) → vi phạm hard; 2 câu → cảnh báo soft. **KHÔNG đụng `EDUCATIONAL`/category khác** — EDUCATIONAL chưa có hạ tầng chống lặp tương đương, để riêng cho audit sau nếu có bằng chứng.

### 3. `iching_short_generator.py` — khớp Delta B với rubric mới
Cập nhật `_GENERATE_CANDIDATES_PROMPT` + `_JUDGE_PROMPT` (sub-check (e) mới) đúng ngưỡng 3+/2 câu.

## Cố tình KHÔNG áp dụng (theo đúng đánh giá Codex qua 2-3 vòng)
- Causal Chain/Logical Progression taxonomy đầy đủ, Concrete Anchor, Re-open Curiosity — evidence "Trung bình/Yếu", chưa qua pilot kappa.
- Hard-gate cho Delta A/C — Codex: prompt-only chưa đủ tin cậy cho enforcement production, cần output JSON có cấu trúc + validation trước, việc đó để lần sau nếu pilot cho thấy cần.
- Mở rộng Delta B sang EDUCATIONAL — chưa có bằng chứng, mô tả sai ở draft đã tự sửa.

## Đã tự sửa 2 lỗi cơ học phát hiện ở vòng cuối (không cần Codex duyệt lại)
1. Worked example "HỢP LỆ" ban đầu của Delta B tự vi phạm chính rubric nó minh hoạ (thiếu framing câu 2) — sửa lại ví dụ giữ đủ framing, chỉ đổi vị trí đặt.
2. Delta A ban đầu tự mâu thuẫn (vừa nói "chỉ feedback" vừa đề xuất field JSON `retention_notes` mới) — bỏ hẳn field JSON, chỉ dùng `feedback` sẵn có.

## Trạng thái sau áp dụng
Không có hard-gate MỚI nào trong lần này — cả 3 delta dừng ở mức thu hẹp/ghi chú, đúng tinh thần giảm rủi ro cho engine dùng chung theo đúng yêu cầu Codex. Cần audit lại `feedback` sau 1 thời gian chạy thật để biết tần suất (d)/(e)/(rule mới ở INTERPRETATION) được kích hoạt, trước khi cân nhắc nâng cấp bất kỳ mục nào lên hard-gate.
