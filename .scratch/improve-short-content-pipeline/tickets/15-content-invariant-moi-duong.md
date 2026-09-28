# 15: Content invariant cho mọi đường vào còn lại

**Spec:** `../spec-2.md`, mục Content invariant (S6). Quyết định: D74, D78, D79, D83.

**What to build:** Mở rộng sidecar Content invariant (ticket 13) ra mọi đường sinh Short còn lại:
- **Các generator FS khác:** `claim_source` là `facts` của từng generator.
- **TRENDING:** `claim_source` là `extract_facts`, còn `source_excerpt` là excerpt đã được kiểm với nguồn.
- **BUD:** runner ghi đoạn trích gốc làm `source_excerpt` **trước** bước review viết lại.
- **CL provenance:** `claim_source` là fact pack; `content_hook`, `idea_order` và `payoff` lấy deterministic từ `StoryPlan` (HOOK/BEAT/REVEAL/PAYOFF), gắn `derived_by: story_plan`.
- **CL legacy / case pipeline:** excerpt hoặc `CoreFact` mà đường đó có. Phần thiếu ghi vào `missing`.

**Blocked by:** 13

**Prerequisite vận hành:** 01 (phần BUD và CL cần test runner/registry)

**Status:** done (grok review OK)

- [x] Mọi generator FS ghi sidecar với `claim_source` đúng `facts` đã dùng
- [x] TRENDING ghi `claim_source` và `source_excerpt`
- [x] BUD: đoạn trích gốc được ghi trước review; không bao giờ ghi vào trường script đã đăng (D79)
- [x] CL provenance: hook, thứ tự ý và Payoff lấy từ `StoryPlan`, `derived_by: story_plan`, không qua LLM
- [x] CL legacy/case: ghi phần có, phần thiếu kèm lý do
- [x] Test theo từng đường với fixture; test cần runner/registry thuộc nhóm CI/container
