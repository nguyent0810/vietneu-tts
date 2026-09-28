# 17: Script evaluator shadow (một lần gọi), nối xuyên suốt với zodiac

**Spec:** `../spec-2.md`, các mục Script evaluator, Script fidelity shadow (S9), Tín hiệu chẩn đoán (S10), Opening pattern (S12). Quyết định: D69, D80, D83, D84, D86, D90.

**What to build:** Khi Short zodiac đi qua S7, một lần gọi LLM (model khác writer) trả về 4 phần tách riêng, mỗi phần có evidence riêng và không có điểm tổng:
- **Invariant do LLM trích:** Content hook, thứ tự ý và Payoff, gắn `derived_by: llm` kèm span. Kết quả này điền các trường còn thiếu của sidecar, không ghi đè trường do code hoặc `StoryPlan` sinh.
- **Script fidelity:** các finding claim mới, claim bị làm mạnh, trích dẫn sai nguyên văn, thuật ngữ bị thay lệch nghĩa; mỗi finding có mức độ chắc chắn.
- **Span chi tiết móc:** code quy ra Khoảng cách tới điểm móc bằng hàm của ticket 12.
- **Mô tả Opening pattern:** mô tả tự do kèm span. Không dùng taxonomy.

Mọi finding được ghi vào Quality record với `shadow: true` và **không bao giờ** làm đổi Gate status. Short không có nguồn claim thì fidelity ghi `Source không đủ`. Lỗi CR-1 không được ghi lại ở tầng Script.

**Blocked by:** 13, 14

**Status:** done (grok review OK)

- [x] Đúng một lần gọi evaluator cho mỗi Short; đầu ra có 4 phần tách riêng, có evidence, không có điểm tổng
- [x] Evaluator là model khác model writer; model được ghi vào record
- [x] Invariant do LLM trích không ghi đè trường do `code` hoặc `story_plan` sinh
- [x] Finding fidelity có cờ `shadow: true`; test khẳng định Gate status không đổi dù có finding
- [x] Không có nguồn claim: fidelity ghi `Source không đủ`
- [x] Không có finding CR-1 ở tầng Script
- [x] Span điểm móc được quy ra số từ và số giây; span không hợp lệ thì ghi lỗi, không đoán
- [x] Evaluator lỗi hoặc trả sai cấu trúc: ghi lỗi vào record, không chặn Short, không đổi Gate status
- [x] Test với evaluator giả lập ở cấp hàm gọi CLI
