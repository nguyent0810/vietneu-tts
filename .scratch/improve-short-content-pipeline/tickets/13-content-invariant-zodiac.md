# 13: Content invariant (phần code), nối xuyên suốt với generator zodiac

**Spec:** `../spec-2.md`, mục Content invariant (S6). Quyết định: D67, D83.

**What to build:** Khi generator 12 con giáp sinh một Short, nó ghi một sidecar Content invariant đặt cạnh file script staged. Sidecar có schema version và chứa:
- `claim_source` là đúng dict `facts` đã dùng để sinh, do code ghi, không qua LLM;
- `content_hook`, `idea_order`, `payoff` nằm trong `missing`, kèm lý do "chưa trích" (phần LLM làm ở ticket 17);
- các version.

Không đổi cách generator viết script.

**Blocked by:** None (can start immediately)

**Status:** done (grok review OK)

- [x] Có schema sidecar cho mọi trường: `claim_source`, `source_excerpt`, `content_hook`, `idea_order`, `payoff` (mỗi trường có `derived_by`: `code` / `story_plan` / `llm` và span evidence), `missing` (trường và lý do), các version, schema version
- [x] Generator zodiac ghi sidecar với `claim_source` đúng bằng `facts` đã đưa cho writer
- [x] Trường chưa có được ghi vào `missing` kèm lý do, không bỏ trống lặng lẽ
- [x] Có hàm thuần xác định invariant có "đủ để Script rewrite" hay không
- [x] Generator FAIL (không có script) thì không ghi sidecar mồ côi
- [x] Test qua generator zodiac với agy/Codex giả lập ở cấp hàm gọi CLI; chạy được trên Windows
