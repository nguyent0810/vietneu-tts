# CODEX_PLAN_REVIEW.md

> Biên bản phản biện bắt buộc bằng Codex CLI. **Không chỉnh sửa nội dung Codex trả về.**

## Bối cảnh: kế hoạch đã đổi phạm vi

| Vòng | Phạm vi | Kết quả |
|---|---|---|
| v1 R1 | Kế hoạch cũ (FastAPI/Python, full-stack) | CHANGES_REQUIRED — 1 BLOCKER, 11 HIGH, 8 MEDIUM — **đã sửa hết** |
| v1 R2 | Kế hoạch cũ, sau khi sửa | CHANGES_REQUIRED — 6 HIGH, 4 MEDIUM (chủ yếu mâu thuẫn chéo tài liệu) — **đã sửa hết** |
| v1 R3 | Kế hoạch cũ | **Bị dừng giữa chừng, không sinh finding** — người dùng đổi phạm vi sang backend-first Vercel/Neon, kế hoạch cũ không còn tồn tại |
| **v2 R1** | **Phạm vi mới (backend-first, Vercel + Neon + Blob-hoãn)** | *(bên dưới)* |

Biên bản v1 đầy đủ được lưu ngoài repo tại scratchpad `codex/CODEX_PLAN_REVIEW_v1_prescope.md`
(không giữ trong repo vì nó phản biện một kiến trúc đã bị thay thế, dễ gây nhầm lẫn).

**30 finding của v1 đều đã được chấp nhận và sửa**, và các bài học đó được **mang sang** kế hoạch v2:
lát cắt dọc thay vì MVP rộng, approval chỉ supersede khi promote, ba bộ đếm job tách biệt,
`DEFERRED` nằm trong partial unique, `job_attempt` + artifact promotion, score append-only,
analytics SCD-2 + `dimensions=day`, forward-only migration, không bọc batch runner nguyên trạng,
không hứa rebuild byte-identical.

---

## v2 ROUND 1 — kết quả thô

```bash
codex exec --sandbox read-only "$(cat prompt_v2r1b.txt)" < /dev/null
```

> ⚠️ **Sự cố công cụ đã khắc phục:** hai lần chạy trước bị **treo 32 phút** vì `codex exec` chờ EOF
> trên stdin (`Reading additional input from stdin...`). Khắc phục bằng `< /dev/null`. Không có finding nào bị mất.

**VERDICT: CHANGES_REQUIRED** — 2 BLOCKER, 6 HIGH.

### [BLOCKER] Score uniqueness contradicts append-only history
- **Severity:** BLOCKER
- **Document:** `DATA_MODEL_PLAN.md` §5; `ALGORITHM_VERSIONING_PLAN.md` §12.2; `IMPLEMENTATION_ROADMAP.md` Phase 2
- **Evidence:** `DATA_MODEL_PLAN.md:188` requires `UNIQUE (content_revision_id, algorithm_version_id, input_snapshot_hash)`, while `ALGORITHM_VERSIONING_PLAN.md:881` requires “chấm lại → hàng mới,” and `IMPLEMENTATION_ROADMAP.md:146` simultaneously calls identical rescoring idempotent. Since `input_snapshot_hash` must equal the revision hash, a second run of the same algorithm version on the same revision cannot be inserted.
- **Why it matters:** Non-deterministic scoring cannot retain repeated observations, retries cannot be distinguished from deliberate reruns, and the promised immutable score history is impossible to implement.
- **Remediation:** Add a first-class `score_request`/`run_key` or `evaluation_nonce`. Make transport retries idempotent via `(job_attempt_id, idempotency_key)` or an `idempotency_record`, while allowing multiple immutable `score_run` rows for the same revision/version/hash. Store `run_sequence`, `random_seed` when applicable, and `supersedes_score_run_id` only as lineage—not uniqueness.

### [BLOCKER] MVP requires 17 scores that its scoring specification forbids
- **Severity:** BLOCKER
- **Document:** `BACKEND_MVP_SPEC.md` §1–3; `IMPLEMENTATION_ROADMAP.md` Phase 2; `ALGORITHM_VERSIONING_PLAN.md` §3
- **Evidence:** `BACKEND_MVP_SPEC.md:17,39,55` requires 17 dimensions per run and 34 dimension rows across v1/v2. `IMPLEMENTATION_ROADMAP.md:161` repeats the 17-dimension acceptance criterion. Conversely, `ALGORITHM_VERSIONING_PLAN.md:139-147,161,188-203,369` says versions publish only computable subsets, missing inputs must produce no dimension row, and `AUDIENCE_FIT` is not publishable. The actual `youtube_analytics.py:19-20` also lacks audience-demographic and impression/CTR metrics.
- **Why it matters:** The backend-only E2E acceptance test cannot pass without fabricating prohibited scores or violating its required row counts. This blocks the stated MVP definition.
- **Remediation:** Change MVP acceptance to a declared v1 subset, assert explicit `missing_dimensions`, and require `overall_score=NULL` when coverage is below the configured threshold. Replace fixed `2 + 34` counts with counts derived from `algorithm_version.dimensions`. Defer unavailable dimensions to the phases that introduce their inputs.

### [HIGH] Job claiming chooses an unnecessary WebSocket transaction
- **Severity:** HIGH
- **Document:** `API_AND_WORKER_PROTOCOL.md` §4.1; `IMPLEMENTATION_ROADMAP.md` Phase 4; `TEST_STRATEGY.md` §2.6
- **Evidence:** `API_AND_WORKER_PROTOCOL.md:115-131` selects `FOR UPDATE SKIP LOCKED` and claims Pool/WebSocket is required to prevent duplicate claims. `IMPLEMENTATION_ROADMAP.md:211-222` and `TEST_STRATEGY.md:103-105` hard-code that driver choice. However, the displayed claim is one SQL statement: PostgreSQL already executes it in an implicit transaction. Neon HTTP supports one-shot queries and non-interactive transactions; only interactive/session transactions require WebSockets. [Neon serverless-driver documentation](https://neon.com/docs/serverless/serverless-driver?a=b7adc640-18e3-4f41-a6b9-053df360d2f7)
- **Why it matters:** The plan imposes per-invocation WebSocket connection setup/teardown and connection-pressure risk on a short-lived Vercel route for no correctness benefit, while teaching an incorrect failure model.
- **Remediation:** Choose **(B) atomic conditional compare-and-set**. Use one HTTP query such as `UPDATE build_job SET … WHERE id=(SELECT id … ORDER BY … LIMIT 1) AND status='QUEUED' AND not_before<=now() AND NOT cancel_requested RETURNING *`. (1) Vercel has no shared process state, so correctness must live in PostgreSQL; both options satisfy that. (2) Neon HTTP directly supports the one-shot statement, whereas A’s stipulated Pool/WebSocket requires a request-scoped connection that must be closed. (3) B needs no explicit transaction because selection and conditional mutation are one statement; A needs an interactive transaction only if selection and update are split. (4) B uses HTTP connection caching and avoids WebSocket lifecycle cost. (5) Under N workers, PostgreSQL rechecks B’s outer predicate after a conflicting updater commits, so at most one claimant receives the row; losers return zero rows and retry. A also prevents duplicate claims and can skip immediately to other locked rows, giving better batch throughput. B may cause contenders to select the same top job and return empty despite other jobs being available, so add jittered immediate retry or claim several candidates. (6) B is simpler and removes driver-specific branching. (7) Prove it with N independent HTTP-driver invocations against a real Neon branch, checking one lease token/history row per job, no overlapping leases, and eventual claiming of all M jobs; also race it against cancellation and reaping. Reject A here because the workload is a single-row claim, not because locking is unfamiliar or categorically unsupported.

### [HIGH] Minute-level lease recovery is undeployable on an allowed Vercel plan
- **Severity:** HIGH
- **Document:** `API_AND_WORKER_PROTOCOL.md` §7; `FINAL_RECOMMENDATION.md` §10; `BACKEND_MVP_SPEC.md` §4
- **Evidence:** `API_AND_WORKER_PROTOCOL.md:262-264` mandates a reaper “cron mỗi phút” for 90-second leases. `FINAL_RECOMMENDATION.md:187` leaves Hobby versus Pro unresolved, while `BACKEND_MVP_SPEC.md:119` makes the Vercel Cron endpoint part of MVP. Vercel Hobby cron can run only once daily and has hourly scheduling precision; per-minute cron requires Pro. [Vercel Cron limits](https://vercel.com/docs/cron-jobs/usage-and-pricing)
- **Why it matters:** On Hobby, a dead worker can strand work for nearly a day instead of approximately 90 seconds. The kill-and-recover MVP acceptance path is therefore not portable to the stated deployment options.
- **Remediation:** Either make Vercel Pro an explicit MVP prerequisite or perform bounded opportunistic reaping atomically at the beginning of every claim request, with cron as a safety sweep. Test recovery with cron disabled. Document cold-start-safe, idempotent reaping and cap each sweep by row count/time.

### [HIGH] Cross-row snapshot integrity is assigned to an impossible CHECK constraint
- **Severity:** HIGH
- **Document:** `ALGORITHM_VERSIONING_PLAN.md` §12.1; `DATA_MODEL_PLAN.md` §5
- **Evidence:** `ALGORITHM_VERSIONING_PLAN.md:865` says `input_snapshot_hash == content_revision.content_sha256` is enforced by “API + CHECK,” while the values live in different tables (`DATA_MODEL_PLAN.md:124,182-191`). PostgreSQL `CHECK` expressions cannot enforce a lookup against another table.
- **Why it matters:** The documented database invariant cannot be implemented as specified. Any alternate writer, import path, migration, or defect bypassing API validation can attach a score to the wrong revision snapshot.
- **Remediation:** Add `UNIQUE (id, content_sha256)` on `content_revision` and use a composite foreign key from `score_run(content_revision_id,input_snapshot_hash)` to it. Apply the same pattern wherever revision identity and snapshot hash must agree. Retain API validation for a clear 409 response, but make the database authoritative.

### [HIGH] Score dimensions remain mutable underneath an immutable score run
- **Severity:** HIGH
- **Document:** `DATA_MODEL_PLAN.md` §5; `ALGORITHM_VERSIONING_PLAN.md` §12; `TEST_STRATEGY.md` §1
- **Evidence:** `DATA_MODEL_PLAN.md:190` and `ALGORITHM_VERSIONING_PLAN.md:864,881` protect only `score_run` from UPDATE/DELETE. `score_dimension` at `DATA_MODEL_PLAN.md:193-195` has uniqueness but no immutability control. `TEST_STRATEGY.md:48-51` likewise tests score-run history and formula consistency but does not attempt direct UPDATE/DELETE of dimensions.
- **Why it matters:** An actor with database write access can change dimension values, weights, rationale, or evidence without changing the supposedly immutable run, invalidating `overall_score`, approval evidence, and historical explanations.
- **Remediation:** Make both tables append-only with triggers or table privileges, prevent deleting a run through child cascades, and insert run plus dimensions atomically. Add adversarial tests for UPDATE/DELETE on both tables and a database audit that detects any stored `overall_score` inconsistent with its immutable dimensions.

### [HIGH] Legacy rollback cannot restore updated records
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §4.4 and §6.1; `IMPLEMENTATION_ROADMAP.md` Phase 3
- **Evidence:** `IMPLEMENTATION_ROADMAP.md:173-195` promises batch rollback returning the database to its previous state. Yet `LEGACY_IMPORT_AND_SYNC_PLAN.md:599` commits partial progress on abort, and `:798-803` refuses rollback whenever any record has outcome `UPDATED` because no complete `before` image is stored.
- **Why it matters:** The mandated rollback property is only true for insert-only batches. A normal reconciliation import that updates an existing entity cannot be rolled back, so the advertised A→B migration safety is overstated.
- **Remediation:** Persist complete typed before-images for every updated row, including relationship rows and prior hashes, or implement import by staging into shadow tables and promoting atomically. Define rollback ordering and conflict checks from those snapshots. If update rollback is deliberately excluded, narrow all roadmap/MVP claims to “rollback insert-only batches” and prevent APPLY updates until a restorable mechanism exists.

### [HIGH] Operational disk pressure is incorrectly made a backend gate
- **Severity:** HIGH
- **Document:** `STORAGE_STRATEGY.md` §12
- **Evidence:** `STORAGE_STRATEGY.md:731` makes freeing local disk “Ngay, trước mọi code Hub,” even though `:732` records that canonical masters are on Drive and the cleanup dry-run deletes zero files.
- **Why it matters:** This creates a false phase dependency and can halt backend implementation for an operational condition that neither changes the backend architecture nor threatens the canonical data under the stated facts.
- **Remediation:** Remove disk cleanup from backend implementation prerequisites. Track it solely as an operational risk with monitoring and a separate response threshold. Do not delete or reprioritize backend work based on the current 19–20 GiB figure.

VERDICT: CHANGES_REQUIRED
tokens used
93,404
### [BLOCKER] Score uniqueness contradicts append-only history

---

## v2 ROUND 1 — Bảng disposition

Mọi finding đều được **tự xác minh lại trên chính tài liệu/code** trước khi chấp nhận:

| Kiểm chứng | Kết quả |
|---|---|
| `DATA_MODEL_PLAN.md:188` unique `(revision, algo_version, input_hash)` chặn dòng thứ hai | ✅ Đúng — tự mâu thuẫn với "chấm lại → hàng mới" |
| `BACKEND_MVP_SPEC.md` đòi "2 + 34" và "17 dimension" vs `ALGORITHM_VERSIONING §3` "không phải version nào cũng phát hành đủ 17" | ✅ Đúng — loại trừ nhau |
| `STORAGE_STRATEGY.md:731` ghi "**Ngay, trước mọi code Hub**" cho việc dọn đĩa | ✅ Đúng — tạo phụ thuộc phase giả |
| PostgreSQL `CHECK` không tra cứu được bảng khác | ✅ Đúng — S-2 không cài đặt được như mô tả |
| `score_dimension` không có cơ chế bất biến nào | ✅ Đúng — chỉ `score_run` được bảo vệ |
| Vercel Hobby cron chỉ 1 lần/ngày | ✅ Đúng — reaper "mỗi phút" không portable |

**Tất cả 8 finding được CHẤP NHẬN.** Một finding được **chấp nhận phần đúng nhưng chọn cách sửa khác** (HIGH-1) — giải thích ở dưới.

| # | Finding | Sev | Quyết định | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|:-:|---|---|
| B1 | Unique key của score mâu thuẫn với append-only | BLOCKER | Accepted | Tách **idempotency truyền tải** (bảng `idempotency_record` mới) khỏi **lịch sử chấm** (`run_sequence`). Unique thành `(revision, algo_version, input_hash, run_sequence)`; `previous/supersedes` chỉ là lineage. Thêm `evaluation_nonce`, `random_seed` | `DATA_MODEL_PLAN` §1+§5, `IMPLEMENTATION_ROADMAP` P2, `TEST_STRATEGY` I-S1, `ALGORITHM_VERSIONING` |
| B2 | MVP đòi 17 dimension mà spec cấm | BLOCKER | Accepted | Số dòng dimension **suy ra từ `algorithm_version.dimensions`**, không hằng số. Thêm `coverage_bp`, `missing_dimensions`, `overall_score=NULL` khi coverage thấp. Dimension phụ thuộc analytics dời **P6** (bằng chứng: `youtube_analytics.py:19-20` thiếu impressions/CTR) | `BACKEND_MVP_SPEC` §1–5, `IMPLEMENTATION_ROADMAP` P2, `DATA_MODEL_PLAN` §5 |
| H1 | Job claim chọn WebSocket transaction không cần thiết | HIGH | **Accepted (phần đúng) + chọn cách sửa khác** | Chấp nhận điểm cốt lõi: **HTTP driver là đủ**, bỏ hoàn toàn ràng buộc Pool/WebSocket. Nhưng **giữ `SKIP LOCKED`** trong subquery **và thêm mệnh đề CAS ở câu ngoài** — vì claim vẫn là *một câu lệnh* (nên HTTP chạy được), đồng thời tránh nhược điểm của (B) thuần: nhiều worker cùng nhắm hàng đầu rồi trả rỗng. Thêm §4.1.1 phản biện đủ 7 trục | `API_AND_WORKER_PROTOCOL` §4.1+§4.1.1, `TARGET_ARCHITECTURE` §5, `RISK_REGISTER` R30, `TEST_STRATEGY` §2.6, `FINAL_RECOMMENDATION` §12 |
| H2 | Reaper mỗi phút không chạy được trên Hobby | HIGH | Accepted | Reaper **hai tầng**: reap cơ hội ngay đầu mỗi `claim` (chính, không phụ thuộc gói) + cron thưa (lưới an toàn). Test phục hồi phải xanh **khi đã tắt cron** | `API_AND_WORKER_PROTOCOL` §7, `BACKEND_MVP_SPEC` §4 |
| H3 | `CHECK` không thể ép ràng buộc liên bảng | HIGH | Accepted | Thay bằng **FK composite**: `UNIQUE(id, content_sha256)` trên `content_revision` + FK `(content_revision_id, input_snapshot_hash)`. CSDL phán quyết, API vẫn trả 409 | `DATA_MODEL_PLAN` §5, `TEST_STRATEGY` I-S2, `BACKEND_MVP_SPEC` §5 |
| H4 | `score_dimension` vẫn sửa được | HIGH | Accepted | Append-only cho **cả hai** bảng (trigger + thu hồi quyền + ghi cùng transaction + cấm cascade). Thêm audit đối chiếu `overall_score` với Σ(dimension×weight) | `DATA_MODEL_PLAN` §5, `TEST_STRATEGY` I-S1, `BACKEND_MVP_SPEC` §5 |
| H5 | Rollback import không phục hồi được bản ghi UPDATED | HIGH | Accepted | Thu hẹp phạm vi: batch `APPLY` **chỉ insert-only** ở MVP; trùng ⇒ `SKIPPED_DUPLICATE`. Bật UPDATE phải có before-image đầy đủ và **chặn ở tầng API** | `LEGACY_IMPORT_AND_SYNC_PLAN` header, `IMPLEMENTATION_ROADMAP` P3, `TEST_STRATEGY` I-IMP3 |
| H6 | Áp lực đĩa bị biến thành cổng chặn backend | HIGH | Accepted | Gỡ khỏi điều kiện tiên quyết; chuyển thành **rủi ro vận hành song song**, có ngưỡng cảnh báo riêng. Khớp chỉ đạo tường minh của người dùng | `STORAGE_STRATEGY` §12, `FINAL_RECOMMENDATION` §12 |

### Sửa bổ sung (tự phát hiện qua cross-check, không do Codex nêu)

| # | Vấn đề | Xử lý |
|---|---|---|
| X1 | `Idempotency-Key` hứa cho mọi POST nhưng chỉ `build_job` có cột lưu | Thêm bảng **`idempotency_record`** `(scope, key, principal)` + 409 khi key dùng lại với body khác |
| X2 | `enrollment_code` dùng ở protocol nhưng **không có entity** | Thêm **`worker_enrollment_code`** (hash, TTL, dùng một lần) |
| X3 | `source_document` scope theo `domain_id`, **ngoại lệ duy nhất** của quy tắc `channel_id` | Ghi rõ ngoại lệ + quy tắc suy quyền qua `domain_id → tập kênh`; test cross-channel phải phủ riêng nhánh source |
| X4 | Đường revoke worker token lệch giữa hai tài liệu | Chốt **`/api/v1/workers/{id}/tokens/{tid}/revoke`** (User API) |
| X5 | `content_seo.py:173` cắt input `[:8000]`/`[:15000]` ⇒ `input_snapshot_hash` cho đảm bảo **sai** | Bắt buộc `score_run.input_truncated_at` |
| X6 | File có BOM (`efbbbf`) + macOS NFD ⇒ hash không ổn định | Bắt buộc strip BOM + chuẩn hoá **NFC** trước khi hash |

---

## v2 ROUND 2 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 1 BLOCKER, 5 HIGH.

### [BLOCKER] Approval can be attached before the revision becomes immutable
- **Severity:** BLOCKER
- **Document:** `BACKEND_MVP_SPEC.md` §1; `IMPLEMENTATION_ROADMAP.md` Phase 5; `DATA_MODEL_PLAN.md` §5 `approval`
- **Evidence:** `BACKEND_MVP_SPEC.md:18-20` specifies “CLI … tạo content_revision mới ở DRAFT → USER approve + freeze revision → tạo build_job”. `IMPLEMENTATION_ROADMAP.md:267-269` repeats “CLI tạo revision cải thiện (DRAFT) → user approve + freeze revision”. But `DATA_MODEL_PLAN.md:281-287` defines no constraint that an approval may reference only a `FROZEN` revision. Draft revisions remain mutable until frozen (`DATA_MODEL_PLAN.md:122-144`).
- **Why it matters:** A user can approve draft contents, after which the same revision row can be modified before it is frozen. The approval ID remains bound to the same revision ID but no longer represents the bytes the user reviewed. Checking only that `job.content_revision_id == approval.content_revision_id` does not prevent this.
- **Remediation:** Change the mandatory sequence to `create DRAFT → edit → freeze atomically and compute final content_sha256 → approve the already-FROZEN revision → create job`. Enforce at the database boundary with a trigger or composite FK proving `(content_revision_id, FROZEN)`, and store `content_sha256_at_approval` with a composite FK to `content_revision(id, content_sha256)`. Add a negative race test: concurrent mutation/freeze/approval must never leave an active approval for bytes other than those reviewed.

### [HIGH] Revised job-claim decision is contradicted by two unrevised Pool mandates
- **Severity:** HIGH
- **Document:** `API_AND_WORKER_PROTOCOL.md` §§4.1.1 and 10; `IMPLEMENTATION_ROADMAP.md` Phase 4
- **Evidence:** `API_AND_WORKER_PROTOCOL.md:149-160` chooses a one-statement HTTP-driver hybrid, while `API_AND_WORKER_PROTOCOL.md:395` still says “`FOR UPDATE SKIP LOCKED` trên Pool/WebSocket driver (HTTP driver không đủ).” `IMPLEMENTATION_ROADMAP.md:218-230` likewise mandates Pool/WebSocket and requires the race test to use Pool. This contradicts `TEST_STRATEGY.md:103-119`, which requires the production HTTP driver.
- **Why it matters:** The plan gives implementers and CI mutually exclusive production-driver requirements. It also fails the mandate to choose exactly A or B by selecting a third “hybrid.” The hybrid SQL itself is valid as a single PostgreSQL statement: the subquery row lock and outer update share the statement’s implicit transaction, so Neon HTTP can execute it. But that makes it neither option A as defined—explicit interactive transaction over Pool/WebSocket—nor pure option B.
- **Remediation:** Choose **B: atomic conditional `UPDATE … RETURNING` over Neon HTTP**, and remove `FOR UPDATE SKIP LOCKED` plus every Pool mandate. Axis-by-axis: (1) Vercel invocations are short-lived and share no process state, so correctness belongs in PostgreSQL; (2) Neon documents HTTP as appropriate for one-shot/non-interactive transactions and WebSocket for session/interactive transactions; (3) B needs only the implicit transaction of one statement; (4) B avoids per-invocation WebSocket lifecycle and pooling cost; (5) under N workers, an outer status predicate guarantees at most one winner for a selected row, while losers may return zero and retry—safe but potentially less fair than `SKIP LOCKED`; (6) B has fewer driver and cleanup paths; (7) prove safety using independent processes against a real Neon branch through the production HTTP driver, asserting unique leases, no overlapping lease histories, and eventual draining under retries. If throughput testing later proves head-row contention material, then explicitly switch to **A** with Pool/WebSocket and a real transaction; do not retain an unnamed third option. Neon’s driver distinction is documented in [Neon serverless driver documentation](https://neon.com/docs/serverless/serverless-driver?a=b7adc640-18e3-4f41-a6b9-053df360d2f7).

### [HIGH] Round-1 score-history fix was not propagated across the plan
- **Severity:** HIGH
- **Document:** `ALGORITHM_VERSIONING_PLAN.md` §10.4; `DATA_MODEL_PLAN.md` §11
- **Evidence:** `DATA_MODEL_PLAN.md:211-224` correctly introduces uniqueness on `(content_revision_id, algorithm_version_id, input_snapshot_hash, run_sequence)`. But `ALGORITHM_VERSIONING_PLAN.md:774-784` still asserts uniqueness without `run_sequence`, says a second score cannot be stored, rejects adding a sequence as breaking idempotency, and requires a new algorithm version merely to rescore identical input. `DATA_MODEL_PLAN.md:432` also retains the old unique key `(revision, algo_version, input_hash)`.
- **Why it matters:** These are incompatible schemas and scoring semantics. One implementation preserves intentional reruns; the other rejects them. The stale algorithm document also reintroduces the exact conflation between transport idempotency and score history that round 1 was meant to remove.
- **Remediation:** Rewrite §10.4 around the accepted model: one intentional evaluation creates one append-only `score_run` with an atomically allocated `run_sequence`; its K raw LLM samples remain inside that run’s immutable evidence. Network retries deduplicate through `idempotency_record`. Update `DATA_MODEL_PLAN.md` §11 and grep all 14 documents for the obsolete three-column uniqueness and “must publish a new version to rescore” rule.

### [HIGH] Frozen revision immutability conflicts with the declared SUPERSEDED transition
- **Severity:** HIGH
- **Document:** `DATA_MODEL_PLAN.md` §3 and §11; `TARGET_ARCHITECTURE.md` §8.2
- **Evidence:** `DATA_MODEL_PLAN.md:125` includes `SUPERSEDED` in `content_revision.status`, but `DATA_MODEL_PLAN.md:142` and `:424` require a trigger that rejects every UPDATE to a `FROZEN` row. `TARGET_ARCHITECTURE.md:213-218` declares `FROZEN → SUPERSEDED` and says promotion of B supersedes A.
- **Why it matters:** The transition cannot pass the specified trigger. Weakening the trigger generically would instead make frozen content mutable and undermine hashes, approvals, audits, scores, and build reproducibility.
- **Remediation:** Keep immutable revision payload and lifecycle metadata separate. Prefer leaving revision status permanently `FROZEN` and deriving supersession from `content_item.production_revision_id`, approval status, and an append-only promotion/supersession event. Alternatively allow a narrowly defined transition that may change only lifecycle columns while verifying every content/provenance/hash field remains byte-for-byte unchanged. Specify and test the exact trigger behavior.

### [HIGH] Job-to-frozen-revision integrity is assigned to another impossible CHECK
- **Severity:** HIGH
- **Document:** `DATA_MODEL_PLAN.md` §6 `build_job` and §11
- **Evidence:** `DATA_MODEL_PLAN.md:315` states that build jobs must reference a `FROZEN` revision. The constraint table at `DATA_MODEL_PLAN.md:425` assigns this to “`content_revision_id NOT NULL + CHECK trạng thái`.” The status lives in `content_revision`, not `build_job`.
- **Why it matters:** PostgreSQL `CHECK` constraints cannot query another table. An API-only check is race-prone: the revision state can change between validation and insertion, and direct/import paths can bypass it. This repeats the cross-row CHECK design error already fixed for score snapshots.
- **Remediation:** Enforce the invariant with a trigger that locks and verifies the referenced revision, or with a composite FK such as a constant `required_revision_status='FROZEN'` plus a unique referenced key `(id,status)`. Keep the API validation only for a clear 409 response. Add direct-SQL and concurrent freeze/create-job tests.

### [HIGH] Approval evidence can come from a different revision or content item
- **Severity:** HIGH
- **Document:** `DATA_MODEL_PLAN.md` §5 `approval`; `API_CONTRACT_PLAN.md` §9 derived gates
- **Evidence:** `DATA_MODEL_PLAN.md:281-283` gives approval independent FKs for `content_revision_id`, `audit_run_id`, and `score_run_id`, but specifies no constraint that the referenced audit and score belong to the approved revision, snapshot, content item, or gate. The gate computation in `API_CONTRACT_PLAN.md:1565` relies on combining these records.
- **Why it matters:** An approval for revision B can cite a passing audit or high score from revision A. All individual foreign keys remain valid, so database integrity does not catch the substitution. This defeats revision-bound approval even if the worker itself cannot call the approval endpoint.

---

## v2 ROUND 2 — Bảng disposition

**Tất cả 6 finding được CHẤP NHẬN.**

| # | Finding | Sev | Quyết định | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|:-:|---|---|
| B1 | Approve được revision **chưa freeze** | BLOCKER | Accepted | Đổi **thứ tự bắt buộc**: `DRAFT → sửa → FREEZE (chốt hash) → APPROVE → tạo job`. Ép ở CSDL hai lớp: FK composite `(revision_id, required_revision_status='FROZEN')` + `approved_content_sha256` FK tới `content_revision(id, content_sha256)` | `DATA_MODEL_PLAN` §5, `BACKEND_MVP_SPEC` §1+§5, `IMPLEMENTATION_ROADMAP` P2+P5, `FINAL_RECOMMENDATION` §3 |
| H1 | Quyết định claim bị mâu thuẫn bởi 2 chỗ còn bắt buộc Pool | HIGH | Accepted | **Bỏ phương án lai, chọn (B) thuần**: gỡ `FOR UPDATE SKIP LOCKED`, CAS một câu lệnh trên HTTP driver. Gỡ **mọi** ràng buộc Pool ở §10, roadmap P4, R44. Ghi rõ đánh đổi công bằng + cách giảm nhẹ (jitter, `LIMIT k` ngẫu nhiên) + **điều kiện xét lại** để chuyển hẳn sang (A) | `API_AND_WORKER_PROTOCOL` §4.1+§4.1.1+§10, `IMPLEMENTATION_ROADMAP` P4, `RISK_REGISTER` R44 |
| H2 | Sửa score vòng 1 chưa lan sang các tài liệu khác | HIGH | Accepted | Viết lại `ALGORITHM_VERSIONING §10.4` quanh mô hình đã chốt; sửa bảng bất biến `DATA_MODEL §11`; quét sạch unique 3 cột cũ và luật "muốn chấm lại phải phát hành version mới" | `ALGORITHM_VERSIONING_PLAN` §1+§10.4+§10.x, `DATA_MODEL_PLAN` §11 |
| H3 | `FROZEN → SUPERSEDED` xung đột với trigger bất biến | HIGH | Accepted | **Bỏ `SUPERSEDED`** khỏi `content_revision.status`; status dừng vĩnh viễn ở `FROZEN`. Supersession **suy ra** từ `content_item.production_revision_id` + bảng append-only **`revision_promotion_event`** | `DATA_MODEL_PLAN` §3+§11, `TARGET_ARCHITECTURE` §8.2 |
| H4 | Job→revision FROZEN lại giao cho `CHECK` liên bảng | HIGH | Accepted | FK composite `(content_revision_id, required_revision_status)` → `content_revision(id, status)` + cột hằng. API chỉ để trả 409. Thêm test SQL trực tiếp + test đồng thời freeze/tạo-job | `DATA_MODEL_PLAN` §6+§11, `TEST_STRATEGY` I-1b |
| H5 | Bằng chứng approval có thể lấy từ revision khác | HIGH | Accepted | FK composite buộc `audit_run`/`score_run` được viện dẫn **cùng `content_revision_id`, cùng `input_snapshot_hash`, đúng `gate`**; nhiều bằng chứng ⇒ bảng con `approval_evidence` bất biến | `DATA_MODEL_PLAN` §5+§11, `TEST_STRATEGY` I-A4 |

---

## v2 ROUND 3 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 1 BLOCKER, 4 HIGH, 1 MEDIUM.

### [BLOCKER] Old score uniqueness still forbids intentional rescoring
- **Severity:** BLOCKER
- **Document:** `API_CONTRACT_PLAN.md` §7; `ALGORITHM_VERSIONING_PLAN.md` §10.4
- **Evidence:** `API_CONTRACT_PLAN.md:717` still specifies `Unique (content_revision_id, algorithm_version_id, input_snapshot_hash)` and says identical scoring returns the old run. `ALGORITHM_VERSIONING_PLAN.md:784,788` says intentional rescoring creates a new `run_sequence`, but `:795-799` again rejects additional runs and requires publishing a new algorithm version. These statements directly contradict `DATA_MODEL_PLAN.md:225-238`.
- **Why it matters:** Implementing the API contract recreates the round-1 blocker: a second intentional evaluation of the same revision/version cannot be stored. Implementers cannot determine whether `run_sequence` or the obsolete three-column key is authoritative.
- **Remediation:** Delete the obsolete API-contract uniqueness and all of `ALGORITHM_VERSIONING_PLAN.md:791-799`. Specify the four-column unique key everywhere. Define retry deduplication exclusively through `idempotency_record`; an intentional request with a fresh idempotency key must allocate a new immutable run.

### [HIGH] `run_sequence` has no concurrency-safe allocation protocol
- **Severity:** HIGH
- **Document:** `ALGORITHM_VERSIONING_PLAN.md` §6.4; `DATA_MODEL_PLAN.md` §5; `TEST_STRATEGY.md` §2.6–2.7
- **Evidence:** `ALGORITHM_VERSIONING_PLAN.md:453` merely says to create a score with the “next” `run_sequence`. `DATA_MODEL_PLAN.md:225` only supplies a uniqueness constraint. No document defines an atomic allocator, lock, retry-on-conflict transaction, or concurrency test for two fresh scoring requests targeting the same `(revision, algorithm_version, input_hash)`.
- **Why it matters:** Two legitimate requests can both calculate `MAX(run_sequence)+1`; one then fails its unique constraint after doing expensive local scoring. Worse, if `idempotency_record` is committed separately, a failed score insert can leave a cached response without a corresponding run.
- **Remediation:** Define one transaction that reserves idempotency and allocates the sequence. Use a per-key counter row updated with `INSERT … ON CONFLICT … DO UPDATE SET next_sequence=… RETURNING`, or serialize on an existing parent row/advisory lock. Insert `score_run`, dimensions, and the completed idempotency response atomically. Add a real-Neon test with concurrent distinct idempotency keys asserting contiguous unique sequences and no orphan idempotency records.

### [HIGH] Revision `SUPERSEDED` remains in the authoritative API and architecture
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §§3, 6.4; `TARGET_ARCHITECTURE.md` §8.2
- **Evidence:** `API_CONTRACT_PLAN.md:343` still exposes `RevisionStatus = ['DRAFT','REVIEW_REQUIRED','FROZEN','SUPERSEDED']`; `:635` treats `SUPERSEDED` as a stored revision status. `TARGET_ARCHITECTURE.md:213-218` still declares `FROZEN → (SUPERSEDED)`. This contradicts `DATA_MODEL_PLAN.md:125,142-156`, where a frozen row rejects every update and supersession is derived from `production_revision_id` plus `revision_promotion_event`.
- **Why it matters:** Generated clients and route validation will accept a state the database forbids. An implementer following the architecture will attempt an update that the immutability trigger must reject.
- **Remediation:** Remove `SUPERSEDED` from every revision enum and transition. Keep it only for entities that genuinely have that state, such as approval or artifact promotion. Make revision responses derive `is_production`/`is_superseded` without mutating `content_revision.status`.

### [HIGH] Pure-B job claiming is still contradicted by stack-selection documents
- **Severity:** HIGH
- **Document:** `TARGET_ARCHITECTURE.md` §5; `FINAL_RECOMMENDATION.md` §9
- **Evidence:** `TARGET_ARCHITECTURE.md:121,130-136` says job claiming needs `SELECT … FOR UPDATE SKIP LOCKED` and uses that as the principal Drizzle-over-Prisma justification. `FINAL_RECOMMENDATION.md:169` repeats that justification. The adopted protocol explicitly chooses pure B and removes `SKIP LOCKED` at `API_AND_WORKER_PROTOCOL.md:150-177`.
- **Why it matters:** The plan still gives implementers incompatible query requirements and bases a foundational technology decision on a query the selected design does not use. It also fails the round-3 mandate to remove pure-B leftovers across all 14 documents.
- **Remediation:** Remove every statement that the current queue requires `FOR UPDATE SKIP LOCKED`. Justify Drizzle using SQL transparency, migration reviewability, bundle characteristics, and support for the actual CAS statement. Mention Pool/WebSocket only inside the documented future option-A reevaluation path.

### [HIGH] Scoring invariants again rely on impossible cross-row `CHECK` constraints
- **Severity:** HIGH
- **Document:** `ALGORITHM_VERSIONING_PLAN.md` §12.1
- **Evidence:** `ALGORITHM_VERSIONING_PLAN.md:880` says snapshot equality is enforced by “API + CHECK,” despite `DATA_MODEL_PLAN.md:248-256` correctly replacing that impossible cross-table check with a composite FK. `ALGORITHM_VERSIONING_PLAN.md:881` says a `CHECK` verifies that `previous_score_run_id` references a run with the same algorithm version, which also requires inspecting another row.
- **Why it matters:** PostgreSQL `CHECK` constraints cannot perform these referenced-row lookups. Following this document leaves lineage integrity unenforced or produces migrations that cannot implement the stated invariant.
- **Remediation:** Replace S-2 with the documented composite FK. Enforce S-3 using a composite self-FK such as `(previous_score_run_id, algorithm_version_id)` referencing a unique `(id, algorithm_version_id)`, plus a local check governing `overall_delta_bp` nullability. Add direct-SQL negative tests.

### [MEDIUM] `revision_promotion_event` is referenced but not fully modeled or written
- **Severity:** MEDIUM
- **Document:** `DATA_MODEL_PLAN.md` §§2–3, 11; `API_CONTRACT_PLAN.md` §6.4
- **Evidence:** `DATA_MODEL_PLAN.md:13` omits `revision_promotion_event` from the P2 entity inventory. `:153-154` gives only an informal field list, without foreign keys proving both revisions belong to `content_item_id`, append-only enforcement, or indexes. `API_CONTRACT_PLAN.md:637` describes the promote transaction but never inserts the required promotion event.
- **Why it matters:** The plan removed mutable revision supersession and made this event the sole historical record, yet the declared promotion transaction can discard that history. Cross-item promotion events would also remain representable unless constrained.

---

## v2 ROUND 3 — Bảng disposition

**Tất cả 6 finding được CHẤP NHẬN.** Bốn finding là **dư âm lan truyền** (sửa đúng ở tài liệu gốc nhưng còn sót ở tài liệu khác) — đúng điểm yếu mà Codex bắt lặp lại; hai finding là **vấn đề mới** do chính bản sửa vòng 2 sinh ra.

| # | Finding | Sev | Loại | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|---|
| B1 | Unique score cũ vẫn cấm chấm lại có chủ đích | BLOCKER | Dư âm | Sửa `API_CONTRACT_PLAN:717` sang mô hình `idempotency_record` + `run_sequence`; **xoá hẳn** khối `ALGORITHM_VERSIONING:791-799` (bảng phương án A/B/C cũ + luật "phải phát hành version mới để chấm lại") | `API_CONTRACT_PLAN`, `ALGORITHM_VERSIONING_PLAN` §10.4 |
| H1 | `run_sequence` **không có giao thức cấp phát an toàn** | HIGH | **Mới** | Thêm bảng **`score_run_counter`** + `INSERT … ON CONFLICT DO UPDATE … RETURNING`; định nghĩa **một transaction** làm 4 việc (chiếm idempotency → cấp sequence → ghi run+dimensions → cập nhật response), rollback toàn bộ nếu lỗi. Thêm test I-S5 trên Neon thật | `DATA_MODEL_PLAN` §5, `TEST_STRATEGY` I-S5, `IMPLEMENTATION_ROADMAP` P2 |
| H2 | `SUPERSEDED` vẫn còn trong enum API + kiến trúc | HIGH | Dư âm | Gỡ khỏi `RevisionStatus` (Zod), khỏi validation PATCH, khỏi `TARGET_ARCHITECTURE §8.2`. Bổ sung cách **suy ra** `is_production`/`is_superseded` không cần sửa hàng `FROZEN` | `API_CONTRACT_PLAN`, `TARGET_ARCHITECTURE` §8.2 |
| H3 | Pure-B bị mâu thuẫn bởi tài liệu chọn stack | HIGH | Dư âm | Viết lại lý do chọn Drizzle quanh **SQL trong suốt cho CAS + FK composite**, bỏ mọi khẳng định "hàng đợi cần `SKIP LOCKED`". `SKIP LOCKED`/Pool chỉ còn trong **đường xét lại sang (A)** | `TARGET_ARCHITECTURE` §5, `FINAL_RECOMMENDATION` D1 |
| H4 | Bất biến scoring lại giao cho `CHECK` liên bảng | HIGH | Dư âm | S-2 → **FK composite** tới `content_revision(id, content_sha256)`; S-3 → **FK composite tự tham chiếu** `(previous_score_run_id, algorithm_version_id)` + `CHECK` **cục bộ** cho `overall_delta_bp`. Thêm test I-S6 bằng SQL trực tiếp | `ALGORITHM_VERSIONING_PLAN` §12.1, `TEST_STRATEGY` I-S6 |
| M1 | `revision_promotion_event` được nhắc nhưng chưa mô hình hoá | MEDIUM | **Mới** | Mô hình đầy đủ: trường, **FK composite buộc cả hai revision thuộc đúng `content_item`**, append-only trigger, index, và **bắt buộc INSERT trong cùng transaction promote**. Đưa vào inventory P2 + ER diagram. Thêm test I-PROMO1/2 | `DATA_MODEL_PLAN` §0.0+§3+§10+§11, `TEST_STRATEGY`, `API_CONTRACT_PLAN` |

---

## v2 ROUND 4 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] End-to-end test still approves before freezing
- **Severity:** HIGH
- **Document:** `TEST_STRATEGY.md` §2.10
- **Evidence:** `TEST_STRATEGY.md:165-166` specifies `improve → approve → freeze → job`. This contradicts `BACKEND_MVP_SPEC.md:18-21`, `TARGET_ARCHITECTURE.md:224`, and the database FK in `DATA_MODEL_PLAN.md:364-373`, which requires the revision to be `FROZEN` before inserting an approval.
- **Why it matters:** The mandatory frontend-free acceptance test cannot complete against the planned schema: approval must fail before reaching job creation. This is propagation drift from the previously accepted round-2 BLOCKER and means the documented MVP is not executable end-to-end as written.
- **Remediation:** Change §2.10 to `improve → freeze → approve → job`. Explicitly assert that approval before freeze returns 409 and that the successful approval records the finalized `content_sha256`.

### [HIGH] Promotion transaction does not serialize concurrent promotions or revocations
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.4; `DATA_MODEL_PLAN.md` §3; `TEST_STRATEGY.md` §2.1
- **Evidence:** `API_CONTRACT_PLAN.md:641` only says to check an active approval, update `production_revision_id`, insert an event, and supersede the old approval; it specifies no row lock, CAS predicate, or isolation requirement. `revision_promotion_event.from_revision_id` is intended to record the previous production revision (`DATA_MODEL_PLAN.md:156-173`). Tests I-PROMO1/2 cover rollback and cross-item FKs only (`TEST_STRATEGY.md:54-55`), not concurrent promotions or approval revocation.
- **Why it matters:** Two transactions can both observe revision A as production and record `A→B` and `A→C`, while the final pointer is C; the event stream then ceases to be a valid history. A concurrent revoke can also occur after the “ACTIVE” check, allowing promotion with an approval that is no longer active. This breaks the sole history mechanism introduced to replace mutable `SUPERSEDED` revision state.
- **Remediation:** Lock the `content_item` and supplied `approval` rows with `SELECT … FOR UPDATE` before validation, or use an explicit CAS update against the expected previous revision and require exactly one returned row. Derive `from_revision_id` from the locked/update-returned value. Bind `revision_promotion_event.approval_id` to its `content_item_id` and `to_revision_id` with a composite FK. Add real-PostgreSQL concurrency tests for B/C promotion races and promote-versus-revoke, asserting a linear event chain and an active revision-bound approval at commit.

VERDICT: CHANGES_REQUIRED
tokens used

---

## v2 ROUND 4 — Bảng disposition

**Cả 2 finding được CHẤP NHẬN.**

| # | Finding | Sev | Loại | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|---|
| H1 | Test E2E vẫn approve **trước** freeze | HIGH | Dư âm | Đổi §2.10 thành `improve → **freeze** → **approve** → job`; thêm khẳng định approve-trước-freeze ⇒ **409** và `approved_content_sha256` khớp hash đã chốt | `TEST_STRATEGY` §2.10 |
| H2 | Transaction promote **không tuần tự hoá** | HIGH | **Mới** | Thêm giao thức SQL đầy đủ: `SELECT … FOR UPDATE` trên `content_item` **và** `approval`, **CAS** `production_revision_id IS NOT DISTINCT FROM :prev`, `from_revision_id` lấy từ giá trị đã khoá, FK composite buộc `approval_id` khớp item+revision. Thêm test I-PROMO3 (promote đua) và I-PROMO4 (promote vs revoke) | `API_CONTRACT_PLAN` §6.4, `DATA_MODEL_PLAN` §3+§11, `TEST_STRATEGY`, `BACKEND_MVP_SPEC` §5 |

---

## v2 ROUND 5 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Promotion locking does not enforce the documented single-winner race
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.4; `TEST_STRATEGY.md` §2.1; `BACKEND_MVP_SPEC.md` §5
- **Evidence:** `API_CONTRACT_PLAN.md:653-667` first locks `content_item`, then reads `production_revision_id` into `:prev`, and performs a CAS against that newly locked value. If B and C race from A, the second transaction waits, then reads the winner’s revision as its own `:prev`; its CAS therefore succeeds too, producing `A→B→C`. This contradicts `TEST_STRATEGY.md:56` and `BACKEND_MVP_SPEC.md:149`, which require “đúng một thắng” and the loser to fail because production changed.
- **Why it matters:** The round-4 race test cannot pass against the prescribed SQL. More importantly, a stale user request to promote C “from A” can silently become a valid promotion from B, overriding a decision made while it waited. The CAS provides no optimistic-concurrency protection because its expected value originates inside the same locked transaction.
- **Remediation:** Require the caller to provide `expected_production_revision_id` through the request body or `If-Match`. After locking the item, compare the locked value with that caller-supplied expectation and return `409 CONCURRENT_PROMOTION` on mismatch; use the supplied expectation in the CAS. Keep `from_revision_id` equal to the verified locked value. Alternatively, explicitly adopt serialized multi-winner semantics and rewrite I-PROMO3, but that would not satisfy the currently documented single-winner requirement. Make I-PROMO4 deterministic with barriers proving whether revoke or promote acquired the approval lock first.

### [HIGH] Promotion supersedes unrelated approval gates
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.4; `DATA_MODEL_PLAN.md` §§3, 5
- **Evidence:** The promotion SQL at `API_CONTRACT_PLAN.md:673-675` executes `UPDATE approval SET status='SUPERSEDED' WHERE content_item_id=:item AND status='ACTIVE' AND id<>:approval_id`. Approvals are gate-specific—`RESEARCH_READY`, `CONTENT_READY`, `PRODUCTION_READY`, and `PUBLISH_READY`—per `DATA_MODEL_PLAN.md:352-355,360-364`. The update has no `gate='PRODUCTION_READY'` or previous-revision predicate. This conflicts with `DATA_MODEL_PLAN.md:406`, which says only A’s approval is superseded when B becomes production.
- **Why it matters:** Promoting one production revision destroys active research, content, and publish approvals for the entire item. It can invalidate unrelated evidence, block publishing, and falsify approval history. Because promotion is the only documented path to `SUPERSEDED`, those approvals cannot be restored without creating new approval records.
- **Remediation:** Supersede only the prior production approval: constrain the update to `gate='PRODUCTION_READY' AND content_revision_id=:prev`, preferably using the exact locked prior approval ID. Lock that prior approval row before changing it. Leave other gates untouched and add an integration test with active approvals at all four gates proving that promotion supersedes only the prior revision’s `PRODUCTION_READY` approval.

VERDICT: CHANGES_REQUIRED
tokens used

---

## v2 ROUND 5 — Bảng disposition

**Cả 2 finding được CHẤP NHẬN.** Cả hai đều là **lỗi thật trong SQL do chính tôi viết ở vòng 4** — không phải dư âm lan truyền.

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | CAS **vô dụng** vì `:prev` đọc bên trong khoá | HIGH | Caller **bắt buộc** gửi `expected_production_revision_id` (body/`If-Match`); sau khi khoá thì đối chiếu **giá trị đã khoá với kỳ vọng của caller**, lệch ⇒ **409 `CONCURRENT_PROMOTION`**. Không còn chuyện kẻ đến sau lấy kết quả của kẻ thắng làm kỳ vọng rồi cũng thành công (`A→B→C`). I-PROMO3 viết lại để **fail** nếu ai đó quay về CAS nội bộ; I-PROMO4 thêm barrier cho tất định | `API_CONTRACT_PLAN` §6.4, `DATA_MODEL_PLAN` §3+§11, `TEST_STRATEGY`, `BACKEND_MVP_SPEC` |
| H2 | Promote **xoá sạch approval ở cả 4 gate** | HIGH | `UPDATE approval … WHERE id = :prev_approval_id` — đúng **một** hàng đã khoá, gate `PRODUCTION_READY`, revision cũ. `RESEARCH_READY`/`CONTENT_READY`/`PUBLISH_READY` **không bị đụng**. Thêm I-PROMO5: dựng item có approval `ACTIVE` ở cả 4 gate, promote, khẳng định chỉ 1 bị supersede | `API_CONTRACT_PLAN` §6.4, `DATA_MODEL_PLAN` §3+§11, `TEST_STRATEGY`, `BACKEND_MVP_SPEC` |

---

## v2 ROUND 6 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Promotion request contract rejects the required concurrency token
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.4, request schemas and error taxonomy
- **Evidence:** `API_CONTRACT_PLAN.md:615` defines `RevisionPromote` as `z.object({ approval_id: Uuid }).strict()`, while `:641` and `:650-651` require `expected_production_revision_id` in the body or `If-Match`. Because the schema is strict, a body containing that field is rejected. The generic `If-Match` contract at `:162-163` represents a resource ETag derived from `updated_at` and ID—not a nullable production revision UUID—and no promote-specific encoding is defined. `CONCURRENT_PROMOTION`, used at `:660` and in `TEST_STRATEGY.md:56`, is also absent from the error registry at `API_CONTRACT_PLAN.md:205-239`.
- **Why it matters:** The prescribed single-winner CAS cannot be implemented interoperably from the authoritative API contract. Clients cannot express the first-promotion expectation (`NULL`) or a previous revision UUID through the declared strict body, and implementers must invent incompatible `If-Match` semantics. I-PROMO3 could pass against a private test interface while the published endpoint remains unusable or silently reverts to an internally sourced expectation.
- **Remediation:** Define one canonical representation, preferably `RevisionPromote = z.object({ approval_id: Uuid, expected_production_revision_id: Uuid.nullable(), reason: ... }).strict()`. Require the property to be present even when null. Alternatively, fully specify a promote-specific `If-Match` grammar including the null case and remove “body” as an option. Add `CONCURRENT_PROMOTION` to the error registry with HTTP 409 and test request validation for UUID, null, missing, and unknown-field cases.

### [HIGH] Revoking the current production approval can permanently block later promotion
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.4, “Giao thức bắt buộc”; `DATA_MODEL_PLAN.md` §5 `approval`
- **Evidence:** `API_CONTRACT_PLAN.md:668-672` locks the previous revision’s approval only with `status='ACTIVE'`, while `:704` states that any step returning zero rows rolls back the whole transaction; the only documented exception is “lần promote đầu” at `:672`. However, approvals explicitly support revocation (`DATA_MODEL_PLAN.md:364-368`), and `:412` says revocation changes status rather than deleting the record. Therefore, after production revision A’s approval becomes `REVOKED`, promotion of an actively approved B finds zero rows at step 4 and must always roll back.
- **Why it matters:** A supported security action—revoking an approval—can strand the content item on that revision indefinitely. No later corrected revision can become production through the documented protocol, even with a valid active target approval. This also leaves the required behavior of promote-versus-revoke undefined once revocation wins before the promotion begins.
- **Remediation:** Resolve the exact approval that authorized the current production promotion, preferably from the latest `revision_promotion_event` whose `to_revision_id` equals the locked current pointer, and lock it regardless of status. Permit no previous approval/event only when the locked pointer is null. At step 7, change that exact row from `ACTIVE` to `SUPERSEDED` conditionally; leave an already `REVOKED` row unchanged. Replace the blanket “any zero rows” rule with step-specific outcomes, and extend I-PROMO4 with the case “revoke A commits, then promote approved B” to prove promotion succeeds without altering A’s revoked history.


---

## v2 ROUND 6 — Bảng disposition

**Cả 2 finding được CHẤP NHẬN.** Cả hai là **hệ quả dây chuyền** của chính bản sửa vòng 5 — đúng loại lỗi mà chỉ review lặp mới bắt được.

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Schema `RevisionPromote` `.strict()` **từ chối** chính token đồng thời vừa thêm | HIGH | Thêm `expected_production_revision_id: Uuid.nullable()` **bắt buộc có mặt** (kể cả `null` cho lần promote đầu) + `reason`. Chốt **body là biểu diễn chính thức duy nhất**, loại bỏ `If-Match` cho promote (ETag chung dẫn xuất từ `(id, updated_at)` nên **không** biểu diễn được "production hiện tại là NULL"). Đăng ký `CONCURRENT_PROMOTION` (409) và `APPROVAL_NOT_ACTIVE` (409) vào error registry. Thêm I-PROMO7 test thiếu/null/sai/field-lạ | `API_CONTRACT_PLAN` §5+§2+§6.4, `TEST_STRATEGY` |
| H2 | **Revoke làm kẹt item vĩnh viễn** | HIGH | Approval cũ nay xác định từ `revision_promotion_event` gần nhất trỏ tới con trỏ hiện tại và **khoá bất kể `status`**. Bước supersede chỉ đổi khi còn `ACTIVE`; đã `REVOKED` ⇒ **bỏ qua, không rollback**. Thay quy tắc chung "0 dòng ⇒ rollback" bằng **bảng ngữ nghĩa 0-dòng theo từng bước**. Thêm I-PROMO6: revoke A commit xong ⇒ promote B vẫn **thành công**, lịch sử `REVOKED` giữ nguyên | `API_CONTRACT_PLAN` §6.4, `DATA_MODEL_PLAN` §3, `TEST_STRATEGY` |

---

## v2 ROUND 7 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH, 1 MEDIUM.

### [HIGH] Promote transport remains internally contradictory
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.4; `DATA_MODEL_PLAN.md` §3
- **Evidence:** `API_CONTRACT_PLAN.md:624-626` declares the request body the “CHÍNH THỨC DUY NHẤT” representation and explicitly prohibits `If-Match`. However, `API_CONTRACT_PLAN.md:652,661-663` still says the value may be supplied through “Body/If-Match” or “trong body hoặc If-Match.” `DATA_MODEL_PLAN.md:174-177` repeats “body hoặc If-Match.”
- **Why it matters:** The round-6 transport fix is not resolved across the normative documents. An implementer can still create an incompatible promote-specific `If-Match` representation, particularly for the required first-promotion `NULL` expectation. Tests written only against the body schema would not detect that divergence.
- **Remediation:** Replace every “body hoặc `If-Match`” occurrence with the single canonical rule: `expected_production_revision_id` is a required JSON property in `RevisionPromote`, including explicit `null`. State that the generic `If-Match` policy does not apply to this endpoint.

### [HIGH] Promoting the current revision corrupts approval and event history
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.4
- **Evidence:** The protocol validates the target approval at `API_CONTRACT_PLAN.md:673-677`, but never requires `:rid` to differ from `locked_prev`. The pointer update at `:693-697` accepts an unchanged value, the event insert at `:699-702` records `A→A`, and step 7 at `:704-708` then changes the same approval locked as the active target to `SUPERSEDED`. `DATA_MODEL_PLAN.md:170` makes uniqueness of `(content_item_id, to_revision_id)` optional (“nếu cấm”), so the schema does not reliably prevent this path.
- **Why it matters:** A successful request can leave the production revision authorized only by a superseded approval, create a self-loop in the supposedly linear promotion history, and cause later event-derived previous-approval resolution to select corrupted history. This violates revision-bound approval and the promotion-chain invariants.
- **Remediation:** After locking the item, reject `:rid IS NOT DISTINCT FROM locked_prev` with a specified 409 error before locking approvals. Make the event constraint reject `from_revision_id = to_revision_id`. Add a real-PostgreSQL test that attempts `A→A` and asserts no pointer, event, or approval mutation.

### [MEDIUM] First-promotion execution uses an undefined previous-approval value
- **Severity:** MEDIUM
- **Document:** `API_CONTRACT_PLAN.md` §6.4; `TEST_STRATEGY.md` I-PROMO7
- **Evidence:** Step 4 returns no row when `expected_production_revision_id IS NULL` and declares that valid at `API_CONTRACT_PLAN.md:679-691`. Step 7 nevertheless always executes `WHERE id = :prev_approval_id` at `:704-708`, although no value was produced for that parameter. The zero-row table at `:722` incorrectly says step 7 can return zero only because the old approval was `REVOKED`. `TEST_STRATEGY.md:60` checks that `null` is accepted but does not assert the complete first-promotion transaction.
- **Why it matters:** Implementations may throw an unbound-parameter error, accidentally reuse a stale value, or handle the first promotion differently across drivers. The existing contract test can pass while the first real promotion still rolls back.
- **Remediation:** Specify an explicit branch: when the locked previous pointer is `NULL`, skip steps 4 and 7 entirely. Update the zero-row table to distinguish “no previous production” from “previous approval already revoked.” Extend I-PROMO7 or add I-PROMO8 to assert that first promotion commits the pointer and `NULL→A` event while leaving A’s target approval `ACTIVE`.

---

## v2 ROUND 7 — Bảng disposition

**Cả 3 finding được CHẤP NHẬN.**

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Transport promote vẫn tự mâu thuẫn ("body **hoặc** If-Match") | HIGH | Thay **mọi** chỗ bằng quy tắc duy nhất: `expected_production_revision_id` là **thuộc tính JSON bắt buộc** (kể cả `null`); `If-Match` **không áp dụng** cho endpoint này. Thêm case test gửi qua `If-Match` phải bị từ chối | `API_CONTRACT_PLAN` §5+§6.4, `DATA_MODEL_PLAN` §3, `TEST_STRATEGY` I-PROMO7 |
| H2 | Promote **chính revision đang production** (`A→A`) làm hỏng lịch sử | HIGH | Chặn ở bước **2b** trước khi đụng approval: `:rid IS NOT DISTINCT FROM locked_prev` ⇒ **409 `ALREADY_PRODUCTION`**. Thêm **CHECK** `from_revision_id IS DISTINCT FROM to_revision_id` làm lưới an toàn ở CSDL (thay cho unique "nếu cấm" tuỳ chọn). Thêm I-PROMO9 | `API_CONTRACT_PLAN` §6.4+§2, `DATA_MODEL_PLAN` §3, `TEST_STRATEGY`, `BACKEND_MVP_SPEC` |
| M1 | Nhánh promote lần đầu dùng `:prev_approval_id` **chưa được gán** | MEDIUM | Nêu **nhánh tường minh**: `locked_prev IS NULL` ⇒ **bỏ qua hẳn** bước 4 và 7. Bảng ngữ nghĩa 0-dòng tách riêng "chưa từng promote" (4′/7′) khỏi "approval cũ đã REVOKED". Thêm I-PROMO8 khẳng định `NULL→A` commit đúng và approval A vẫn `ACTIVE` | `API_CONTRACT_PLAN` §6.4, `TEST_STRATEGY`, `BACKEND_MVP_SPEC` |

---

## v2 ROUND 8 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 1 HIGH.

### [HIGH] Selected Neon HTTP driver cannot execute the mandatory promotion transaction
- **Severity:** HIGH
- **Document:** `TARGET_ARCHITECTURE.md` §5; `API_CONTRACT_PLAN.md` §6.4; `DATA_MODEL_PLAN.md` score-run transaction
- **Evidence:** `TARGET_ARCHITECTURE.md:122` selects `@neondatabase/serverless` HTTP and says Pool/WebSocket is needed only if a multi-statement interactive transaction appears “về sau.” But `API_CONTRACT_PLAN.md:662-713` already mandates an interactive transaction containing multiple lock/read/conditional-write steps. Steps 2, 2b, 4′, and 7′ require application-side branching after examining earlier query results. `DATA_MODEL_PLAN.md:310-314` independently mandates another multi-step transaction for idempotency, sequence allocation, score insertion, and response persistence.
- **Why it matters:** Neon HTTP supports one-shot queries and non-interactive batched transactions, but it cannot preserve a session transaction while a Route Handler reads `locked_prev`, decides whether to return `CONCURRENT_PROMOTION` or `ALREADY_PRODUCTION`, conditionally skips steps 4 and 7, and then continues using the same row locks. Implementing the displayed protocol as separate HTTP calls releases the `FOR UPDATE` locks after each call, reopening the promotion/revocation races the protocol is intended to close. The newly explicit step 2b and first-promotion branch make this incompatibility unavoidable. The same mismatch threatens atomic score/idempotency writes. [Neon serverless driver documentation](https://neon.com/docs/serverless/serverless-driver)
- **Remediation:** Choose and document one executable transaction strategy before implementation: either use request-scoped `Pool`/WebSocket interactive transactions for promotion, score persistence, reaping, and every other multi-statement state transition, with guaranteed connection cleanup; or move each workflow into one PostgreSQL statement/server-side function that performs all validation, branching, locking, mutation, and typed error return atomically through Neon HTTP. Update `TARGET_ARCHITECTURE.md:122`, the roadmap, deployment configuration, and tests accordingly. I-PROMO3/4/6/8/9 must run through the exact production driver and route implementation, not a privileged test connection.

VERDICT: CHANGES_REQUIRED
tokens used

---

## v2 ROUND 8 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | **HTTP driver không chạy được transaction promote** | HIGH | **Accepted.** Tôi đã tổng quát hoá sai: từ việc *job claim là một câu lệnh* suy ra "HTTP cho toàn bộ backend". Nhưng promote và ghi score **đã** là transaction **tương tác** (đọc → rẽ nhánh trong app → ghi tiếp **trong khi vẫn giữ `FOR UPDATE`**). Tách thành nhiều lời gọi HTTP sẽ **nhả khoá sau mỗi lời gọi** ⇒ mở lại đúng race vừa đóng.<br>**Sửa:** thêm **§5.1 Chính sách driver theo workload** — HTTP cho câu lệnh đơn (claim, list, get); **Pool/WebSocket cho transaction tương tác** (promote, ghi score, freeze/approve, reaper nếu không gộp được). Kèm quy tắc vận hành Pool trên Vercel (`pool.end()` trong `finally`, `statement_timeout`, `idle_in_transaction_session_timeout`, transaction ngắn, giới hạn kết nối). Nêu phương án thay thế PL/pgSQL và đưa thành **quyết định D1b**. Test phải đi qua **route + driver thật**, không dùng kết nối đặc quyền | `TARGET_ARCHITECTURE` §5+§5.1, `API_AND_WORKER_PROTOCOL` §10, `API_CONTRACT_PLAN` §6.4, `DATA_MODEL_PLAN` §5, `IMPLEMENTATION_ROADMAP` P1, `TEST_STRATEGY` §3, `FINAL_RECOMMENDATION` D1b |

---

## v2 ROUND 9 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Dual-driver policy leaves several state transitions unassigned
- **Severity:** HIGH
- **Document:** `TARGET_ARCHITECTURE.md` §5.1; `API_AND_WORKER_PROTOCOL.md` §§4.4, 6.1; `API_CONTRACT_PLAN.md` §6.4; `IMPLEMENTATION_ROADMAP.md` Phases 1 and 4
- **Evidence:** `TARGET_ARCHITECTURE.md:139-146` assigns Pool/WebSocket only to promote, score persistence, reaper, freeze, and approve. But `API_AND_WORKER_PROTOCOL.md:198-200` requires job start to verify a lease, conditionally update state and counters, and create `job_attempt` “trong một transaction.” Lines 263-271 require completion, idempotency, job completion, and artifact promotion/supersession in one transaction. `API_CONTRACT_PLAN.md:650` allocates `revision_no` using `max+1` inside a transaction. None is assigned either a single-statement HTTP implementation or Pool/WebSocket. `IMPLEMENTATION_ROADMAP.md:88` repeats only “promote, ghi score, freeze/approve,” while Phase 4 at lines 228-244 does not assign the driver for start, complete, fail, artifact promotion, heartbeat, or reaping. The actual repository confirms these are new backend semantics rather than reusable transactional code: `long_batch_runner.py:157-163` runs a topic-wide subprocess, and `registry_lock.py:1-17` explicitly says its file lock does not solve concurrent processing of the same key.
- **Why it matters:** Implementers can reasonably use the default HTTP path and split these transitions into multiple calls, causing duplicate `attempt_no`/`revision_no`, consumed retry budget without a corresponding attempt, or a completed job with partially promoted artifacts. Conversely, using Pool ad hoc expands WebSocket connection pressure without planned lifecycle and production-driver tests. The Round-8 requirement that every interactive transaction be assigned is therefore not fully resolved.
- **Remediation:** Expand §5.1 into an exhaustive route/workload matrix. For every mutating route, specify either: (a) the exact one-statement SQL/CTE executed over HTTP, or (b) one request-scoped Pool/WebSocket transaction. At minimum cover revision creation, start, heartbeat, logs, artifact registration, complete, fail/defer, cancel, approval revoke, audit persistence, import, rollback, and reaper. Update each owning protocol section and roadmap phase, not merely the architecture overview. Add route-level Neon tests using the declared production mode for concurrent start, concurrent revision creation, completion versus lease expiry/reaper, and competing artifact promotion.

### [HIGH] Legacy dry-run semantics cannot be executed through the defined import API
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §4.3; `API_CONTRACT_PLAN.md` §6.16; `BACKEND_MVP_SPEC.md` §§1, 4, 6
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:578-590` requires the entire apply algorithm to run in one transaction ending in `ROLLBACK`, including temporary entity and `legacy_id_map` writes. The API instead splits import into `POST /import/batches`, repeated `POST /import/batches/{id}/records`, and `finalize` (`API_CONTRACT_PLAN.md:1475-1483`), permits only 200 records per request (`:1500-1507`), explicitly anticipates multiple requests for larger imports (`:1525` and §13), and states that dry-run writes only `import_record` and report (`:1522`). A request-scoped Pool cannot preserve one rollback-only transaction across those HTTP requests. Rolling back each record batch independently also removes parent rows needed to validate later dependent records, despite the required import order in `LEGACY_IMPORT_AND_SYNC_PLAN.md:604-605`. Separately, the authoritative MVP acceptance contract lists nonexistent `POST /api/v1/import/dry-run` and `/apply` routes (`BACKEND_MVP_SPEC.md:93-94`) instead of the batch protocol, even though its E2E must import a real package (`:13-15`) and run on a Vercel preview (`:177-180`). The local-only premise is real: `content_repo.py:37` points at `content_repo_clone`, and `API_CONTRACT_PLAN.md:1470-1473` correctly acknowledges Vercel cannot read it.
- **Why it matters:** The prescribed dry-run cannot faithfully exercise foreign keys, uniqueness constraints, ordering, or insert-only behavior through the published API. A dry-run may pass while apply fails, violating the mandatory dry-run guarantee. The MVP E2E also has two incompatible endpoint contracts, so no single generated OpenAPI client can implement the stated acceptance flow.
- **Remediation:** Choose one executable model and make every document match it. Prefer uploading the normalized manifest in bounded chunks into staging tables, then invoking one server-side transaction/function that validates and simulates the complete ordered import before rolling back business-table writes while persisting the report separately. Alternatively, constrain the entire import manifest to one request and run one request-scoped Pool transaction, with an explicit size ceiling compatible with Vercel. Define how cross-record dependencies are resolved during simulation. Replace `/import/dry-run` and `/import/apply` in `BACKEND_MVP_SPEC.md` with the finalized batch endpoints—or define those routes consistently—and make the preview E2E use the generated Python client against that exact contract.


---

## v2 ROUND 9 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Chính sách driver **bỏ sót nhiều transition** | HIGH | Thay bảng 6 dòng bằng **ma trận route đầy đủ**: mọi route ghi đều được gán HTTP (một câu lệnh) hoặc Pool (transaction tương tác) — gồm `start`, `complete`, `fail`, `artifacts`, `scores`, `audits`, tạo revision, freeze, approve, promote, revoke, cancel, reaper, import, analytics ingest, worker token. Thêm quy tắc **`revision_no` phải cấp nguyên tử** (không `MAX+1` ngoài khoá) + test I-REV1. Thêm **I-DRV1** (test tĩnh: route ghi thiếu khai báo ⇒ CI fail) và **I-DRV2** (chạy qua route+driver thật) | `TARGET_ARCHITECTURE` §5.1, `IMPLEMENTATION_ROADMAP` P1, `TEST_STRATEGY` |
| H2 | Dry-run import **không thực thi được** qua HTTP nhiều request | HIGH | Chốt mô hình **staging + một transaction**: mở batch → nạp chunk ≤200 vào **`import_staging_record`** (không đụng bảng nghiệp vụ) → `finalize` chạy **một** transaction đọc toàn bộ staging theo **đúng thứ tự phụ thuộc**, validate, rồi `ROLLBACK` (dry-run) hoặc `COMMIT` (apply). Báo cáo **được giữ** dù nghiệp vụ bị rollback. Xoá hai route ảo `/import/dry-run`, `/import/apply` khỏi `BACKEND_MVP_SPEC`, thay bằng bộ endpoint batch thật; E2E preview gọi qua client Python sinh từ OpenAPI | `LEGACY_IMPORT_AND_SYNC_PLAN`, `BACKEND_MVP_SPEC` §4, `DATA_MODEL_PLAN` §0.0+§7 |

---

## v2 ROUND 10 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 4 HIGH.

### [HIGH] “Exhaustive” route/driver matrix omits mutating routes
- **Severity:** HIGH
- **Document:** `TARGET_ARCHITECTURE.md` §5.1
- **Evidence:** `TARGET_ARCHITECTURE.md:139-140` says every writing route must appear in the matrix. However, the MVP declares mutating routes `POST /api/v1/auth/login`, `PUT /api/worker/capabilities`, and `POST /api/worker/shutdown` at `BACKEND_MVP_SPEC.md:90,119,132`, none of which appears in the matrix at `TARGET_ARCHITECTURE.md:142-165`. The worker protocol also defines `POST /api/worker/jobs/{id}/cancelled`, token revocation, analytics enqueue, and analytics snapshot ingestion at `API_AND_WORKER_PROTOCOL.md:79,294,379,383`; only analytics ingestion is represented generically. The broader API contract adds mutating recommendation routes at `API_CONTRACT_PLAN.md:1227,1230`, also absent. Consequently, the proposed I-DRV1 static check would either fail the plan’s own routes or require undocumented exclusions.
- **Why it matters:** Driver selection determines whether multi-statement state transitions are atomic. For example, shutdown must release several leases and close attempts consistently, while capability updates and token rotation/revocation have concurrency-sensitive state. Leaving these routes unclassified permits implementations that use HTTP calls across multiple statements and expose partial updates or races.
- **Remediation:** Generate the matrix from the canonical OpenAPI route inventory and include every non-GET method, including login/session creation, capability update, shutdown, cancelled, enrollment/register/rotate/revoke, import batch creation, recommendation run/promote, cron enqueue, and analytics snapshots. For each route, specify one exact production mode and transaction boundary. Make I-DRV1 compare the OpenAPI inventory against this machine-readable declaration, with explicit reviewed exemptions only for provably read-only POST routes.

### [HIGH] Staging-based import is contradicted by the old per-record apply algorithm
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §§3.3, 4.3–4.4, 6.2
- **Evidence:** The round-9 model requires `finalize` to process all staging rows in one transaction and says APPLY is insert-only (`LEGACY_IMPORT_AND_SYNC_PLAN.md:10-18,27-33`). But §3.3 still mandates “one transaction for each record” and updates existing entities when hashes differ (`:469-486`). Section 4.4 again says “one record = one transaction,” allows already committed rows to survive an aborted batch, and describes update-oriented idempotency (`:624-638,650-658`). Section 6.2 likewise relies on partially committed APPLY batches (`:845-851`). These behaviors directly contradict the single finalize transaction and insert-only rule.
- **Why it matters:** Both designs cannot be implemented simultaneously. One produces atomic all-or-nothing finalize; the other deliberately produces partially applied batches and `UPDATED` entities. This changes rollback guarantees, error handling, idempotency, report outcomes, and the database transaction/driver implementation. An implementer following §4.4 would recreate the round-9 defect.
- **Remediation:** Replace §§3.3, 4.3–4.4, 6.1–6.2 and related tests with one authoritative algorithm: staging uploads commit independently; finalize locks the batch, validates the complete staged graph, treats every existing `legacy_id_map` as `SKIPPED_DUPLICATE`, inserts all new business rows plus mappings and import records in one transaction, then commits or rolls back the entire APPLY. Remove `UPDATED` from the MVP outcome enum or reserve it explicitly for a post-MVP mode that cannot be selected. Remove partial-commit and abort-survival language.

### [HIGH] Import staging cannot provide the idempotency claimed by the API
- **Severity:** HIGH
- **Document:** `DATA_MODEL_PLAN.md` §7 and `API_CONTRACT_PLAN.md` §6.16
- **Evidence:** `import_staging_record` is unique only on `(import_batch_id, chunk_seq, row_seq)` (`DATA_MODEL_PLAN.md:499-505`), while the request contract supplies neither `chunk_seq`, `row_seq`, nor `depends_on_legacy_ref` (`API_CONTRACT_PLAN.md:1500-1507`). The contract nevertheless claims pushing a duplicate batch returns `SKIPPED_DUPLICATE` based on unique `(import_batch_id, legacy_ref)` (`:1521`), but that uniqueness exists only on `import_record`, which is created during finalize, not on staging (`DATA_MODEL_PLAN.md:507-509`). Two logically identical uploads with different HTTP idempotency keys can therefore create duplicate staged rows and make finalize ambiguous or fail on the later `import_record` constraint.
- **Why it matters:** Network retries, CLI restarts, and chunk re-partitioning are normal for this protocol. Without stable row-level staging identity, the same input can be processed twice, parent-child dependencies cannot be represented by the published request, and a supposedly idempotent import may fail only at finalize after every chunk has uploaded.
- **Remediation:** Add unique `(import_batch_id, legacy_ref)` to `import_staging_record`; make record insertion `ON CONFLICT` compare `legacy_sha256`, returning the existing row for an identical replay and `409 IMPORT_RECORD_CONFLICT` for different bytes. Add `depends_on_legacy_ref` to the strict request schema, or specify deterministic server-side derivation. Either expose stable `chunk_seq` plus `row_seq` in the request or remove them from identity and use them only as server-generated ordering metadata. Add concurrent duplicate-upload, changed-hash replay, restart-with-different-chunk-boundaries, and dependency-resolution tests.

### [HIGH] Rollback exists in the MVP but is absent from the canonical import API contract
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.16
- **Evidence:** The MVP exposes `POST /api/v1/import/batches/:id/rollback` at `BACKEND_MVP_SPEC.md:97`, and the driver matrix classifies import rollback as Pool at `TARGET_ARCHITECTURE.md:163`. Yet the import endpoint table in `API_CONTRACT_PLAN.md:1475-1483` has no rollback route, role, idempotency requirement, request schema, response schema, or error behavior. The legacy plan further proposes partial rollback selectors such as `--only-reason-code` and `--only-legacy-kind` at `LEGACY_IMPORT_AND_SYNC_PLAN.md:843`, with no corresponding HTTP contract.
- **Why it matters:** The backend-first MVP must be executable and testable without a frontend, but a required recovery operation has no implementable API contract. Clients cannot be generated for it, authorization and idempotency are undefined, and the E2E test cannot exercise rollback through the real route and production driver as I-DRV2 requires.

---

## v2 ROUND 10 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Ma trận driver "đầy đủ" vẫn **sót route** | HIGH | Bổ sung: `auth/login`, `logout`/đổi mật khẩu, `worker/capabilities`, `worker/shutdown`, `jobs/{id}/cancelled`, `worker/register`, `token/rotate`, `cron/enqueue-analytics`, `import/batches`, `records`, `finalize`, `rollback`, `recommendations/runs`. **Nguồn chuẩn của ma trận nay là inventory OpenAPI**; `I-DRV1` đối chiếu **mọi method ≠ GET**, miễn trừ chỉ cho POST chứng minh được chỉ đọc | `TARGET_ARCHITECTURE` §5.1, `TEST_STRATEGY` I-DRV1 |
| H2 | Mô hình staging **bị mâu thuẫn** bởi thuật toán per-record cũ | HIGH | Thêm **§0 "Mô hình chuẩn (có hiệu lực)"** ở đầu tài liệu và **đánh dấu SUPERSEDED** 6 mục cũ (§3.3, §4, §4.3, §4.4, §6, §6.1, §6.2). Chốt: staging commit độc lập, `finalize` **all-or-nothing**, **không commit từng phần**, `APPLY` **insert-only**, **`UPDATED` bị loại khỏi enum MVP** | `LEGACY_IMPORT_AND_SYNC_PLAN` §0 + 6 mục |
| H3 | Staging **không cung cấp được** idempotency mà API hứa | HIGH | Đổi khoá định danh sang **unique `(import_batch_id, legacy_ref)`**; `chunk_seq`/`row_seq` thành metadata **do server sinh**, không định danh. `ON CONFLICT` so `legacy_sha256`: trùng ⇒ replay an toàn, khác ⇒ **409 `IMPORT_RECORD_CONFLICT`**. Thêm `depends_on_legacy_ref` **bắt buộc có mặt** vào schema request. Thêm I-IMP4 | `DATA_MODEL_PLAN` §7, `API_CONTRACT_PLAN` §5+§2 |
| H4 | Rollback có trong MVP nhưng **không có hợp đồng API** | HIGH | Thêm endpoint `POST /import/batches/{id}/rollback` với hợp đồng đầy đủ: `ADMIN`, idempotency bắt buộc, `confirm_batch_id`, trạng thái lô cho phép, all-or-nothing, **409 `IMPORT_ROLLBACK_BLOCKED`** khi bị tham chiếu, giữ `import_record`/report/`audit_event`, response schema, audit. **Loại bỏ rollback từng phần khỏi MVP**. Thêm I-IMP6 + E2E qua client sinh từ OpenAPI | `API_CONTRACT_PLAN` §6.16, `BACKEND_MVP_SPEC` §4, `IMPLEMENTATION_ROADMAP` P3, `TEST_STRATEGY` |

---

## v2 ROUND 11 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 4 HIGH (toàn bộ trong phân hệ import).

### [HIGH] Canonical import schemas still contradict the round-10 staging fix
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §5 and §6.16; `DATA_MODEL_PLAN.md` §7
- **Evidence:** `API_CONTRACT_PLAN.md:621-629` correctly defines required `depends_on_legacy_ref` and `raw_payload`, but the endpoint-local schema at `API_CONTRACT_PLAN.md:1539-1546` redefines the request without `depends_on_legacy_ref`, calls the content field `payload`, and permits `raw_excerpt`. The response at `:1547-1552` still exposes `UPDATED`. `DATA_MODEL_PLAN.md:515-517` likewise retains `outcome ('IMPORTED|UPDATED|SKIPPED_DUPLICATE|REJECTED')`, despite `LEGACY_IMPORT_AND_SYNC_PLAN.md:41-44` declaring that `UPDATED` is removed from the MVP enum.
- **Why it matters:** OpenAPI generation or implementation from §6.16 will reject the newly required dependency field because the schema is strict, making dependency ordering impossible through the published API. The conflicting outcome enums also permit implementations and generated clients to support an update path that the authoritative insert-only transaction and rollback model explicitly forbid.
- **Remediation:** Define `ImportRecordItem`, `ImportRecordsPush`, and `ImportRecordOut` exactly once and reference those definitions from §6.16/OpenAPI. Require `depends_on_legacy_ref` with nullable value, standardize on `raw_payload`, and remove `UPDATED` from every MVP request, response, database constraint, report, and generated-client enum. Add a schema-generation test proving that a dependency-bearing request is accepted and `UPDATED` cannot be represented.

### [HIGH] Superseded import semantics remain active in invariants, reports, reconciliation, and tests
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §§5, 7, 10.2, 11
- **Evidence:** Although §§3.3, 4.3, 4.4, and 6 are marked superseded, active text still requires `updated` in report arithmetic at `LEGACY_IMPORT_AND_SYNC_PLAN.md:793-795`, says reconciliation can re-import drift as `UPDATED` at `:966-970`, describes checksums as detecting `UPDATED` at `:1171-1175`, and defines invariant I-5 with `updated` at `:1207-1209`. Most seriously, active test T-R4 at `:1252-1255` requires an `ABORTED` batch to retain already committed entities—the exact partial-commit behavior prohibited by authoritative §0 at `:39-45`.
- **Why it matters:** These are executable acceptance criteria, not harmless historical prose. Implementers following the test plan must either violate the all-or-nothing finalize contract or make the prescribed tests fail. Reconciliation also has no valid insert-only action for a changed legacy record.
- **Remediation:** Delete superseded implementation text instead of retaining it inline, or move it to a clearly non-normative history appendix excluded from requirements. Remove `updated` from report totals and tests; define changed legacy data as explicit drift requiring a new post-MVP update workflow or manual revision. Replace T-R4 with a failure-during-finalize test asserting zero committed business rows and a retained failure report.

### [HIGH] Rollback cannot reliably identify the complete graph created by an import batch
- **Severity:** HIGH
- **Document:** `DATA_MODEL_PLAN.md` §7; `LEGACY_IMPORT_AND_SYNC_PLAN.md` §1.1; `API_CONTRACT_PLAN.md` §6.16
- **Evidence:** A single registry source record creates several entities—`content_item`, `content_revision`, `legacy_id_map`, and `video`—at `LEGACY_IMPORT_AND_SYNC_PLAN.md:91-95`. However, `import_record` has only one polymorphic `entity_type`/`entity_id` pair (`DATA_MODEL_PLAN.md:515-517`), and `legacy_id_map` also has only one `entity_type`/`entity_id` pair (`:519-521`). The new rollback contract promises to remove all business rows in reverse dependency order while preserving `import_record` at `API_CONTRACT_PLAN.md:1512-1515`, but defines no batch provenance on each created row or one-to-many import-to-entity ledger.
- **Why it matters:** The server cannot distinguish every row created by the target batch from pre-existing, internally referenced, or subsequently created rows. It may leave imported revisions/videos behind, delete unrelated descendants, or conservatively classify an imported child as a blocking reference and make clean rollback impossible. This invalidates the promised all-or-nothing recovery.
- **Remediation:** Add an append-only `import_entity_effect(import_batch_id, import_record_id, entity_type, entity_id, operation='INSERT', created_at)` ledger with a unique key per affected entity. Populate it atomically inside finalize for every inserted business row, including relationships. Rollback must lock the batch, derive the deletion graph exclusively from this ledger, distinguish intra-batch references from external blockers, delete in declared reverse-FK order, and preserve the ledger as rollback evidence.

### [HIGH] Rollback uses lifecycle states absent from the canonical batch model
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.16; `DATA_MODEL_PLAN.md` §7
- **Evidence:** The rollback contract permits only `APPLIED` and changes/replays against `ROLLED_BACK` at `API_CONTRACT_PLAN.md:1511`. Yet the canonical `ImportBatch` response enum at `:1531-1537` contains only `RUNNING|COMPLETED|FAILED|ABORTED`; neither `APPLIED` nor `ROLLED_BACK` is representable. `DATA_MODEL_PLAN.md:496-497` lists `status` without defining an enum or rollback transition.
- **Why it matters:** The endpoint’s precondition and idempotent replay behavior cannot be implemented against its own database/API state machine. A generated client cannot deserialize the states rollback requires, and concurrent finalize/rollback calls have no specified CAS transition to serialize them.

---

## v2 ROUND 11 — Bảng disposition

> **Quyết định về cách sửa:** bốn vòng liên tiếp (R8→R11) đều sinh finding từ cùng một tài liệu.
> Nguyên nhân gốc: `LEGACY_IMPORT_AND_SYNC_PLAN.md` được viết trên mô hình cũ *"một bản ghi = một
> transaction"*, và cách vá từng dòng (kể cả đánh dấu "superseded") vẫn để lại **ngữ nghĩa cũ đang
> hoạt động** trong invariant, report, reconciliation và test. Vì vậy vòng này tôi **viết lại toàn bộ**
> tài liệu đó trên mô hình staging, thay vì vá tiếp.

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Schema import ở endpoint **mâu thuẫn** schema chuẩn §5 | HIGH | Xoá schema định nghĩa lại; endpoint dùng **đúng** `ImportRecordItem`/`ImportRecordsPush` ở §5 (có `depends_on_legacy_ref` bắt buộc, `raw_payload` đúng tên, không `raw_excerpt`). `ImportRecordOut` bỏ `UPDATED`, đổi cặp entity đơn thành **danh sách `entities[]`**. Bỏ `UPDATED` khỏi `DATA_MODEL_PLAN` | `API_CONTRACT_PLAN` §5+§6.16, `DATA_MODEL_PLAN` §7 |
| H2 | Ngữ nghĩa cũ **vẫn hoạt động** trong invariant/report/reconciliation/test | HIGH | **Viết lại toàn bộ** `LEGACY_IMPORT_AND_SYNC_PLAN.md` trên mô hình staging — không còn mục "superseded", không còn số học report dùng `updated`, không còn reconciliation re-import thành `UPDATED`, không còn test T-R4 đòi lô `ABORTED` giữ dòng đã commit. Bộ invariant mới I-IMP1…I-IMP10 | `LEGACY_IMPORT_AND_SYNC_PLAN` (toàn bộ) |
| H3 | Rollback **không xác định được** đủ đồ thị đã tạo | HIGH | Thêm **`import_entity_link`** (sổ cái một-nhiều: `batch, record, entity_type, entity_id, created_order`). `finalize` ghi **mọi** hàng nghiệp vụ nó tạo; rollback duyệt **ngược** `created_order`. Thêm I-IMP10 | `DATA_MODEL_PLAN` §7+§0.0+ER, `LEGACY_IMPORT_AND_SYNC_PLAN` §6.1 |
| H4 | Rollback dùng trạng thái **không có** trong enum lô | HIGH | Định nghĩa enum chính thức `OPEN\|FINALIZING\|COMPLETED_DRY_RUN\|APPLIED\|FAILED\|ROLLING_BACK\|ROLLED_BACK` ở `LEGACY_IMPORT §5.1` (nguồn chuẩn), thêm `ImportBatchStatus` vào Zod và vào `import_batch.status` | `LEGACY_IMPORT §5.1`, `API_CONTRACT_PLAN` §5, `DATA_MODEL_PLAN` §7 |

---

## v2 ROUND 12 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 4 HIGH, 1 MEDIUM.

### [HIGH] Canonical batch lifecycle is still contradicted by the API response schema
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.16
- **Evidence:** `API_CONTRACT_PLAN.md:1531-1535` defines `ImportBatch.status` as `RUNNING|COMPLETED|FAILED|ABORTED`. The same section later defines `ImportBatchStatus` as `OPEN|FINALIZING|COMPLETED_DRY_RUN|APPLIED|FAILED|ROLLING_BACK|ROLLED_BACK` at `:1552-1554`. `DATA_MODEL_PLAN.md:496-502` and `LEGACY_IMPORT_AND_SYNC_PLAN.md:98-114` require the latter enum.
- **Why it matters:** Generated OpenAPI clients cannot represent the actual database states needed to finalize or roll back a batch. An `APPLIED` or `ROLLED_BACK` database row would fail response validation, while clients would be generated with nonexistent states such as `ABORTED`. Round-11 H4 is therefore not resolved.
- **Remediation:** Change `ImportBatch.status` to `status: ImportBatchStatus`; delete the old inline enum everywhere. Add a contract-generation test asserting all seven canonical values are accepted and `RUNNING`, `COMPLETED`, and `ABORTED` are impossible.

### [HIGH] Import request and response terminology still conflicts with the canonical schema
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.16 and §13.3; `DATA_MODEL_PLAN.md` §7
- **Evidence:** The canonical request stores `raw_payload` at `API_CONTRACT_PLAN.md:621-628`, and §6.16 explicitly says the former `raw_excerpt` contract was removed at `:1539-1543`. Nevertheless, `ImportRecordOut` still exposes `raw_excerpt` at `:1545-1549`; the endpoint rules require it at `:1566`; the payload-size table describes sending it at `:1964`; and `DATA_MODEL_PLAN.md:520-522` still stores it in `import_record`.
- **Why it matters:** Implementers cannot determine whether the uploaded payload is preserved, reduced to an excerpt, or transformed between staging and reporting. The size table incorrectly describes the POST body, so independently implemented CLI, Zod schema, database migration, and generated client will disagree. This leaves round-11 H1 only partially fixed.
- **Remediation:** Define the distinction explicitly and use separate unambiguous names: POST accepts only canonical `raw_payload`; if reports retain a redacted excerpt, name it `redacted_payload_excerpt` and specify the deterministic redaction/truncation process and size bound. Update §6.16, §13.3, the database schema, and generated-client tests together.

### [HIGH] Finalize has mutually exclusive failure semantics
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §5, §10, and §11
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:92` says APPLY rolls back everything “if any record fails.” I-IMP5 at `:216` likewise requires one failing record to leave no business rows. Conversely, `:16`, `:118`, and `:232` define record-level `REJECTED` outcomes and state that, by default, only `SECRET_FIELD_PRESENT` aborts the whole batch; other rejected records merely appear in the report.
- **Why it matters:** These rules yield different databases from the same input. One implementation will commit valid records alongside rejected ones; another will fail the entire batch. That changes idempotency, report arithmetic, dependency handling, retry behavior, and whether an `APPLIED` batch may contain rejected records.
- **Remediation:** Choose one executable rule. For strict all-or-nothing APPLY, any `REJECTED` record must transition the batch to `FAILED` and commit no business rows. If partial acceptance is intended, explicitly permit an `APPLIED` batch with rejected records and rewrite I-IMP5 and the all-or-nothing claims accordingly. Define dependency rejection propagation and exact final status/report counts.

### [HIGH] Rollback cannot detect entities modified after import
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1–6.2; `DATA_MODEL_PLAN.md` §7
- **Evidence:** Rollback promises to return `409 IMPORT_ROLLBACK_BLOCKED` when an imported entity “đã bị sửa sau import” at `LEGACY_IMPORT_AND_SYNC_PLAN.md:159-168`. But `import_entity_link` stores only `entity_type`, `entity_id`, and `created_order` at `:145-152`; the database definition is identical at `DATA_MODEL_PLAN.md:527-533`. It stores no inserted-row hash, version, or expected `updated_at`.
- **Why it matters:** The server cannot reliably distinguish the row originally inserted by the batch from that row after legitimate edits. Rollback may therefore delete post-import user work while claiming it checks for modifications. Reverse deletion order solves foreign-key ordering but not modification detection.
- **Remediation:** Persist a canonical `created_snapshot_hash` or typed before-delete fingerprint for every linked row, including relationship rows, and compare it under lock during rollback. Alternatively make imported rows immutable until rollback eligibility expires. Add a test that modifies an imported mutable row without adding a new foreign-key reference and verifies rollback returns `IMPORT_ROLLBACK_BLOCKED` without deleting anything.


---

## v2 ROUND 12 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | `ImportBatch.status` vẫn dùng enum cũ `RUNNING\|COMPLETED\|FAILED\|ABORTED` | HIGH | Thay bằng `ImportBatchStatus` (7 giá trị) ở **mọi** nơi; `import_batch.status` trong data model cũng dùng đúng enum đó | `API_CONTRACT_PLAN` §5+§6.16, `DATA_MODEL_PLAN` §7 |
| H2 | Thuật ngữ `raw_excerpt` vs `raw_payload` mâu thuẫn | HIGH | Thống nhất: request dùng **`raw_payload`**; response trả **`raw_payload_excerpt`** (trích đoạn **đã redact**). Đổi cả `import_record` và bảng kích thước payload | `API_CONTRACT_PLAN` §5+§6.16+§13, `DATA_MODEL_PLAN` §7 |
| H3 | `finalize` có **hai ngữ nghĩa thất bại loại trừ nhau** | HIGH | Thêm **§5.4 phân biệt hai loại**: *reject bản ghi* (validation ⇒ bản ghi `REJECTED`, lô **vẫn commit** phần hợp lệ) và *huỷ lô* (`SECRET_FIELD_PRESENT`, lỗi hạ tầng, vượt ngưỡng IMP-B ⇒ **rollback toàn bộ**, `status=FAILED`). Viết lại I-IMP5 thành hai nhánh (a)/(b) | `LEGACY_IMPORT_AND_SYNC_PLAN` §5.4+§10 |
| H4 | Rollback **không phát hiện được** thực thể đã bị sửa sau import | HIGH | Thêm **`inserted_row_sha256`** + **`inserted_updated_at`** vào `import_entity_link`. Rollback so ảnh chụp lúc tạo với hiện tại; lệch ⇒ **409 `IMPORT_ROLLBACK_BLOCKED`**. Thêm I-IMP11 | `DATA_MODEL_PLAN` §7, `LEGACY_IMPORT_AND_SYNC_PLAN` §6.2+§10 |
| M1 | Ngôn ngữ `UPDATED` cũ vẫn sống **ngoài** tài liệu import | MEDIUM | Gỡ khỏi `IMPLEMENTATION_ROADMAP` (P3 scope + acceptance), `TEST_STRATEGY` I-IMP3, `BACKEND_MVP_SPEC` bất biến #15 | 3 file |

---

## v2 ROUND 13 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 4 HIGH.

### [HIGH] Import batch schema references its enum before initialization
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §6.16
- **Evidence:** `ImportBatch` evaluates `status: ImportBatchStatus` at `API_CONTRACT_PLAN.md:1531-1534`, but `export const ImportBatchStatus = z.enum(...)` is not initialized until `:1552-1554`. JavaScript/TypeScript `const` bindings are in the temporal dead zone until initialization.
- **Why it matters:** Importing the generated schema module will throw `ReferenceError: Cannot access 'ImportBatchStatus' before initialization`. The Round-12 enum correction therefore cannot run as written, preventing OpenAPI generation and the backend import routes from loading.
- **Remediation:** Declare and export `ImportBatchStatus` before `ImportBatch`. Add a test that imports the compiled schema module, parses all seven valid statuses, and rejects the removed statuses `RUNNING`, `COMPLETED`, and `ABORTED`.

### [HIGH] The abort threshold remains undecided and contradicts the executable failure table
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §5.4 and §11
- **Evidence:** The authoritative failure table says “tỉ lệ reject vượt ngưỡng **IMP-B**” aborts the batch at `LEGACY_IMPORT_AND_SYNC_PLAN.md:138-141`. But IMP-B remains an unresolved user decision at `:241-246`, whose stated current default is “chỉ `SECRET_FIELD_PRESENT` mới huỷ lô; các reject khác chỉ ghi report.”
- **Why it matters:** There is no implementable predicate for finalization. Two conforming implementations can process the same batch differently: one applies all valid records because no threshold is configured, while another aborts after an invented threshold. This affects persisted data, batch status, retries, reports, and idempotent replay.
- **Remediation:** Make the MVP rule explicit and executable. Either remove reject-rate abort from §5.4 and state that only enumerated fatal codes abort, or define a concrete threshold, denominator, comparison operator, configuration owner, and boundary behavior. IMP-B must not remain open in an implementation-ready MVP specification.

### [HIGH] Secret detection still has incompatible test outcomes
- **Severity:** HIGH
- **Document:** `TEST_STRATEGY.md` import invariants; `LEGACY_IMPORT_AND_SYNC_PLAN.md` §5.4, §9, and §10
- **Evidence:** `TEST_STRATEGY.md:77` requires a payload containing `refresh_token` to be “**rejected**,” which denotes the record-level outcome introduced by §5.4. Conversely, `LEGACY_IMPORT_AND_SYNC_PLAN.md:141`, `:213-215`, and `:225-229` require `SECRET_FIELD_PRESENT` to abort the entire batch, roll back all business rows, and set the batch to `FAILED`.
- **Why it matters:** The backend test suite can pass while implementing the wrong security boundary—committing other records from a batch that contains secret material. It also fails the mandate that backend tests enforce storage and import invariants.
- **Remediation:** Rewrite the test as a mixed batch containing one secret-bearing record and at least one otherwise-valid record. Assert `status=FAILED`, zero business rows and `legacy_id_map` rows, no secret value in staging/report/log/audit data, and only a redacted batch-level failure report. Reserve `REJECTED` for nonfatal record validation.

### [HIGH] Rollback snapshots are not consistently or sufficiently specified
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1–6.2; `DATA_MODEL_PLAN.md` §7

---

## v2 ROUND 13 — Bảng disposition

> **Quyết định thiết kế, không chỉ sửa lỗi.** Sáu vòng liên tiếp (R8→R13) đều sinh finding từ **đúng một chỗ**:
> cơ chế rollback **tự xây ở tầng ứng dụng**. Mỗi lần vá lại lộ bề mặt mới — sổ cái thực thể một-nhiều,
> hash từng dòng, projection theo entity, chuẩn hoá JSON, bảng thiếu `updated_at`, ngữ nghĩa chặn…
> Đó là **dấu hiệu thiết kế sai, không phải thiếu chi tiết**.
>
> **Neon đã có sẵn branch + point-in-time restore**, và nó **mạnh hơn** bộ gỡ đồ thị tự viết: khôi phục
> *toàn bộ* trạng thái nhất quán, không phụ thuộc việc ta có liệt kê đủ thực thể hay không.
> ⇒ **Gỡ toàn bộ rollback tầng ứng dụng khỏi MVP.** Điều này xoá luôn bề mặt của 2/4 finding vòng này
> và chặn nguồn phát sinh finding cho các vòng sau.

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | `ImportBatch` dùng `ImportBatchStatus` **trước khi khởi tạo** (temporal dead zone) | HIGH | Khai báo `ImportBatchStatus` **trước** `ImportBatch`. Enum rút còn 5 giá trị. Thêm I-IMP11: parse 5 giá trị hợp lệ, **từ chối** `RUNNING`/`COMPLETED`/`ABORTED`/`ROLLING_BACK`/`ROLLED_BACK` | `API_CONTRACT_PLAN` §5, `LEGACY_IMPORT §10` |
| H2 | Ngưỡng huỷ lô **vẫn để mở** (IMP-B) nhưng bảng thất bại lại viện dẫn nó | HIGH | **Đóng IMP-B**: **không có ngưỡng tỉ lệ** ở MVP; chỉ **danh sách mã lỗi đóng** mới huỷ lô. Người vận hành đọc report rồi tự quyết. Gỡ IMP-B khỏi danh sách câu hỏi mở | `LEGACY_IMPORT §5.4+§11` |
| H3 | Test secret mâu thuẫn: "rejected" (bản ghi) vs "huỷ lô" | HIGH | Viết lại I-IMP2 thành **lô hỗn hợp**: 1 bản ghi chứa secret + ≥1 bản hợp lệ ⇒ `status=FAILED`, **0** hàng nghiệp vụ, **0** `legacy_id_map`, **không** secret trong staging/report/log/audit. `REJECTED` **chỉ** cho lỗi validation không chí mạng | `TEST_STRATEGY` I-IMP2 |
| H4 | Ảnh chụp rollback **không nhất quán và không đủ đặc tả** | HIGH | **Không đặc tả thêm — gỡ hẳn cơ chế.** Xoá `import_entity_link`, `inserted_row_sha256`, `inserted_updated_at`, endpoint `rollback`, mã lỗi `IMPORT_ROLLBACK_BLOCKED`, trạng thái `ROLLING_BACK`/`ROLLED_BACK`. Thay bằng `import_batch.restore_point` + runbook **Neon restore**. Nêu rõ đánh đổi (restore toàn DB, không chọn lọc theo lô) và điều kiện thiết kế lại nếu sau này cần | `LEGACY_IMPORT §6`, `DATA_MODEL_PLAN §7`, `API_CONTRACT_PLAN §6.16+§2`, `TARGET_ARCHITECTURE §5.1`, `BACKEND_MVP_SPEC §4`, `IMPLEMENTATION_ROADMAP` P3, `TEST_STRATEGY` |

---

## v2 ROUND 14 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 3 HIGH.

### [HIGH] Removed application rollback survives in canonical contracts
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §5; `TARGET_ARCHITECTURE.md` §5.1; `IMPLEMENTATION_ROADMAP.md` Phase 3; `DATA_MODEL_PLAN.md` §11; `RISK_REGISTER.md` R47
- **Evidence:** `API_CONTRACT_PLAN.md:634-637` still exports `ImportRollback` with `confirm_batch_id`; `TARGET_ARCHITECTURE.md:163` still assigns “Import: dry-run / apply / rollback” to the Pool driver; `IMPLEMENTATION_ROADMAP.md:183,198,203-205` still promises “reconciliation, rollback,” says “rollback always correct,” requires “rollback batch,” and specifies “revert bằng dữ liệu theo batch”; `DATA_MODEL_PLAN.md:619` still claims “Import idempotent + rollback” is provided by import tables; `RISK_REGISTER.md:69` says `import_batch` is rollback-capable.
- **Why it matters:** These are implementation-driving schemas, driver inventories, acceptance criteria, invariants, and risk controls. An implementer can legitimately rebuild the exact per-batch rollback endpoint and data-deletion behavior that round 13 removed. The driver inventory also conflicts with its own later row at `TARGET_ARCHITECTURE.md:177`, so its static route/driver conformance test has no single expected result.
- **Remediation:** Delete `ImportRollback`; change the driver row to `dry-run / apply` only; replace all “rollback batch” and “revert by batch data” language with the explicitly operational, whole-database Neon restore; update the data-model invariant and R47 mitigation accordingly. Run a repository-wide residual check excluding the historical `CODEX_PLAN_REVIEW.md`, allowing `ROLLBACK` only when it means SQL transaction abort or Neon restore.

### [HIGH] Canonical legacy-import tests still require the deleted per-batch undo
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §10
- **Evidence:** Despite §6 declaring that no application rollback exists, `LEGACY_IMPORT_AND_SYNC_PLAN.md:229` still defines I-IMP3 as “Apply insert-only → rollback,” requires preserved `import_record`/report/audit rows, and expects an idempotent HTTP-style `200` replay. Line `232` still defines I-IMP6 as creating a later reference and expecting rollback to return `409` without partial deletion. Those are the former application endpoint’s semantics; Neon restore cannot selectively preserve post-restore audit/report rows, detect later references as per-batch blockers, or return endpoint status codes.
- **Why it matters:** The authoritative import plan simultaneously requires two mutually exclusive recovery designs. The stated tests cannot pass against the replacement architecture without secretly restoring the removed entity ledger, blocker detection, error code, and endpoint.
- **Remediation:** Replace I-IMP3 and I-IMP6 with the Neon-restore cases already intended by `TEST_STRATEGY.md:67,78`: verify pre-import state restoration on an isolated Neon branch, stable application reconnection, and a newly written `IMPORT_RESTORED` audit event after recovery. Remove every expectation of selective preservation, reference blocking, idempotent endpoint replay, or HTTP `409`.

### [HIGH] The Neon recovery mechanism has no executable runbook
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6; `STORAGE_STRATEGY.md` §9.2; `IMPLEMENTATION_ROADMAP.md` Phase 3
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:167-169` reduces recovery to “create Neon branch (or record timestamp), restore, write audit event”; `STORAGE_STRATEGY.md:618-628` only lists PITR/branching and leaves the retention window as an assumption; `IMPLEMENTATION_ROADMAP.md:195,211` nevertheless makes a runbook and successful restore an acceptance requirement. No document defines which of the non-equivalent branch/timestamp mechanisms is canonical, who invokes Neon, required API credentials, how writes are quiesced, how the active branch/endpoint is reset or switched, how completion is detected, or how clients reconnect and verify the restored state. Neon restore can briefly interrupt database connectivity, and branch-based recovery may require endpoint transfer or a connection change, so “restore” is not a self-executing database operation.
- **Why it matters:** Whole-database restore is now the only promised recovery path. Without a concrete procedure, P3 cannot satisfy its acceptance test, and an operator can restore the wrong timestamp, leave Vercel connected to the damaged branch, or allow concurrent writes that are then silently discarded.
- **Remediation:** Add the promised runbook before P3 acceptance: choose one supported Neon restore operation; specify required plan/retention and API permissions; capture an unambiguous branch ID plus timestamp/LSN before `APPLY`; block imports and other writes; execute and poll the restore; handle connection interruption and endpoint/branch reassignment; force Vercel/worker reconnection; verify schema and pre-import checksums; then write `IMPORT_RESTORED` on the active restored database. Define failure and retention-expiry behavior, and automate the same sequence on a disposable Neon branch in I-IMP3/I-IMP6.

---

## v2 ROUND 14 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Rollback đã gỡ nhưng **vẫn sống** trong hợp đồng chuẩn | HIGH | Xoá `ImportRollback` schema; sửa ma trận driver; gỡ "reconciliation, rollback"/"rollback luôn đúng"/"revert bằng dữ liệu theo batch" khỏi roadmap; sửa bảng bất biến data model; sửa R47 risk register | `API_CONTRACT_PLAN` §5, `TARGET_ARCHITECTURE` §5.1, `IMPLEMENTATION_ROADMAP` P3, `DATA_MODEL_PLAN` §11, `RISK_REGISTER` R47 |
| H2 | Test import vẫn đòi **ngữ nghĩa endpoint đã xoá** | HIGH | Viết lại I-IMP3 theo ngữ nghĩa **restore toàn DB** (nói rõ: **không** giữ được dòng sinh sau restore point — Neon restore không chọn lọc). Đổi I-IMP6 thành **diễn tập runbook** đo `RTO`, bỏ kỳ vọng `409`/`200 idempotent` kiểu HTTP | `LEGACY_IMPORT §10`, `TEST_STRATEGY` I-IMP3/I-IMP6 |
| H3 | Cơ chế Neon **không có runbook thực thi được** | HIGH | Thêm **§6.1 runbook 8 bước**: chốt **branch-based** làm cơ chế chuẩn (kiểm chứng được trước khi chuyển, không phụ thuộc cửa sổ PITR) ⇒ `restore_point` lưu **tên branch**; quiesce bằng `READ_ONLY_MODE` + dừng worker; **kiểm chứng branch trước khi chuyển**; đổi endpoint/`DATABASE_URL` + redeploy; xác nhận qua `/health` báo `db_branch`; mở lại ghi; ghi audit. Nêu rõ **API key vận hành tách khỏi env ứng dụng** (app không tự restore chính nó), cách client kết nối lại, và **hệ quả mất dữ liệu sau restore point** ⇒ phải xuất report ra ngoài DB trước. Thêm tiêu chí nghiệm thu diễn tập vào MVP | `LEGACY_IMPORT §6.1`, `BACKEND_MVP_SPEC` §6, `STORAGE_STRATEGY` A-ST4 |

---

## v2 ROUND 15 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 4 HIGH.

### [HIGH] Read-only cutover blocks its own worker shutdown
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1, steps 2 and 6
- **Evidence:** Line 178 enables `READ_ONLY_MODE` so the API returns **503 for every write route**, then instructs the operator to call `POST /worker/shutdown`. That endpoint is itself a write operation which updates leases (`TARGET_ARCHITECTURE.md:169`; `API_AND_WORKER_PROTOCOL.md:296`). No document defines an exemption, middleware ordering, flag propagation, or drain mechanism.
- **Why it matters:** The prescribed sequence cannot return active leases. Workers may continue heartbeat, completion, or result writes, while shutdown itself receives 503. Switching database branches with active workers can produce writes against the old branch or replayed jobs on the restored branch.
- **Remediation:** Define a privileged maintenance/drain protocol before enabling the global write barrier: stop new claims, allow authenticated shutdown/lease-return and in-flight completion for a bounded period, verify zero active attempts and transactions, then enable the hard barrier. Explicitly enumerate exempt routes, cron behavior, flag propagation/redeployment, timeout handling, and tests proving no writes reach either branch during cutover.

### [HIGH] Restore verification requires a health field forbidden by the API contract
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1 step 5; `API_CONTRACT_PLAN.md` §12
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:181` requires `/api/internal/health` to report the correct `db_branch`. `API_CONTRACT_PLAN.md:1827` defines the health response only as process/build information, while line 1853 explicitly says `/health` **does not read the database**. No `db_branch` field exists in its contract.
- **Why it matters:** The canonical completion check cannot distinguish a successful branch cutover from a healthy deployment still connected to the old database. Implementers following the API contract will omit the field required by the restore runbook.
- **Remediation:** Put authenticated database identity verification on `/api/internal/ready` or add a dedicated operations-only endpoint. Define its response schema using a stable Neon branch ID plus project/endpoint identity, its source of truth, authorization, and failure behavior. Update the runbook and add a negative test that intentionally retains the old `DATABASE_URL`.

### [HIGH] Round-14 restore-drill test was not propagated to the canonical test strategy
- **Severity:** HIGH
- **Document:** `TEST_STRATEGY.md` §1 invariants I-IMP6 and I-IMP3
- **Evidence:** `TEST_STRATEGY.md:67` still defines I-IMP6 as only “create restore point → APPLY → restore branch → database returns to prior state”; line 78 duplicates essentially the same requirement as I-IMP3. Neither test includes quiescing writes, endpoint cutover, client reconnection, `db_branch` verification, operations-credential separation, or measured RTO. This conflicts with the runbook drill required by `LEGACY_IMPORT_AND_SYNC_PLAN.md:261` and `BACKEND_MVP_SPEC.md:188`.
- **Why it matters:** The test suite can pass without exercising the failure-prone operational steps introduced to resolve round 14. The plan therefore provides no enforceable evidence that the production restore procedure works.
- **Remediation:** Keep I-IMP3 for whole-database state restoration. Replace I-IMP6 in `TEST_STRATEGY.md` with the complete disposable-Neon drill: drain and barrier, branch verification, endpoint switch/redeploy, old-branch negative check, authenticated database-identity check, worker reconnection, post-restore audit, credential-boundary assertion, and recorded RTO.

### [HIGH] Import atomicity test contradicts the canonical partial-reject behavior

---

## v2 ROUND 15 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | **Runbook tự khoá mình**: `READ_ONLY_MODE` chặn chính bước dừng worker | HIGH | Tách bước 2 thành **2a drain worker TRƯỚC** (khi API còn ghi được) rồi **2b bật `READ_ONLY_MODE`**. Thêm **allowlist miễn trừ** tường minh cho `worker/shutdown` + `heartbeat` (chỉ **thu hồi** tài nguyên, không tạo dữ liệu mới), phải khai báo trong code và có test | `LEGACY_IMPORT §6.1` |
| H2 | Xác nhận restore đòi trường mà hợp đồng `/health` **cấm** | HIGH | `/health` giữ nguyên (**không** chạm DB, chỉ process/build). Thêm **`/api/internal/readyz`** — endpoint **có** chạm DB — trả `{ ok, db_ok, db_branch, migration_version, checked_at }`; runbook bước 5 dùng `/readyz`. `db_branch` chỉ lộ **tên branch**, và endpoint nằm dưới `/api/internal/*` nên tắt ở production public | `API_CONTRACT_PLAN` §12, `LEGACY_IMPORT §6.1` |
| H3 | Test diễn tập restore **chưa lan** sang test strategy chuẩn | HIGH | Viết lại I-IMP6 thành **diễn tập trọn 8 bước** với khẳng định cụ thể ở từng bước (503 cho route ghi, `worker/shutdown` vẫn gọi được qua allowlist, kiểm chứng trước cutover, `/readyz` báo đúng `db_branch`, worker tự đăng ký lại, `audit_event`), **đo `RTO`**, và khẳng định API key Neon **không** nằm trong env ứng dụng | `TEST_STRATEGY` I-IMP6 |
| H4 | Test atomicity import **mâu thuẫn** partial-reject | HIGH | Viết lại I-IMP5 thành **ba nhánh** (a) validation-reject ⇒ bản hợp lệ **vẫn commit**; (b) huỷ lô ⇒ 0 hàng, `status=FAILED`; (c) dry-run ⇒ bảng sạch nhưng report còn. Ghi rõ **không được** đòi "1 bản ghi fail ⇒ 0 hàng" | `TEST_STRATEGY` I-IMP5 |

---

## v2 ROUND 16 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Worker drain still permits immediate re-claim and indefinite lease renewal
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1 steps 2a–2b; `API_AND_WORKER_PROTOCOL.md` §§4.1, 5.1, 6.3
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:178-179` calls `/worker/shutdown` while ordinary writes and claims remain enabled, then waits for attempts to close. Meanwhile `API_AND_WORKER_PROTOCOL.md:90-130` leaves `/worker/jobs/claim` available, so a worker can claim another job after shutdown. The emergency allowlist at `LEGACY_IMPORT_AND_SYNC_PLAN.md:185-188` exempts heartbeat on the assertion that it “chỉ thu hồi tài nguyên,” but `API_AND_WORKER_PROTOCOL.md:216-219` shows heartbeat returns a renewed `lease_until`; it extends rather than releases the resource. The Worker API also requires a worker token (`API_AND_WORKER_PROTOCOL.md:42-49`), yet the runbook assigns the shutdown call to an operator without defining how that operator can authenticate as every worker.
- **Why it matters:** Step 2a has no monotonic path to zero active attempts. Workers can re-claim jobs, and exempt heartbeats can keep leases alive after the write barrier. The branch can therefore be switched while work still targets the old database, causing lost results, duplicated execution, or divergent job state.
- **Remediation:** Add an explicit maintenance state before drain that atomically rejects new claims and cron enqueueing. Let authenticated workers complete, cancel, or release current attempts for a bounded interval; then force-expire remaining attempts and verify zero live leases/transactions before enabling the hard read-only barrier. Do not exempt normal heartbeat after the barrier; define a dedicated release-only operation that closes the attempt and lease without extending it. Specify an admin-authorized drain endpoint or worker broadcast mechanism and test claim-versus-drain and heartbeat-versus-barrier races on Neon.

### [HIGH] The required `/readyz` endpoint does not exist in the canonical API contract
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §12; `BACKEND_MVP_SPEC.md` §4; `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1 step 5
- **Evidence:** The runbook requires `GET /api/internal/readyz` and fields including `db_branch` at `LEGACY_IMPORT_AND_SYNC_PLAN.md:191-195`; I-IMP6 repeats that dependency at `TEST_STRATEGY.md:67`. But the canonical endpoint table defines `/api/internal/ready`, not `/readyz`, with only “ping Neon, latency, migration count” and no response schema or `db_branch` (`API_CONTRACT_PLAN.md:1825-1829`). Its rules likewise refer exclusively to `/ready` (`API_CONTRACT_PLAN.md:1853-1855`). The backend MVP inventory lists only `/api/internal/health` (`BACKEND_MVP_SPEC.md:135-143`). This repository contains no existing web backend that could supply an implicit endpoint.
- **Why it matters:** An implementation generated from the canonical contract and MVP inventory will omit `/readyz`, so the mandatory restore drill cannot pass. Even renaming `/ready` ad hoc would not define how `db_branch` is obtained, authenticated, validated against the intended Neon project/endpoint, or returned when the database is unreachable. A healthy deployment could still be connected to the wrong branch.
- **Remediation:** Add one canonical operations endpoint consistently across the API contract, MVP inventory, OpenAPI inventory, security tests, and runbook—preferably `/api/internal/readyz`. Define its authentication and production availability, exact success and failure statuses, and schema `{ok, db_ok, db_project_id, db_branch_id, db_branch, db_endpoint_id, migration_version, checked_at}`. Derive identity from a database-side trusted value or verified Neon connection metadata, not an unchecked environment label. Add a negative drill that intentionally retains the old `DATABASE_URL` and must fail the cutover assertion.


---

## v2 ROUND 16 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Drain vẫn cho **claim lại ngay** và **gia hạn lease vô hạn** | HIGH | Tách **hai cờ, hai mục đích**: **`DRAINING`** chỉ chặn `claim` (job dở vẫn `start`/`heartbeat`/`complete` ⇒ hàng đợi **cạn dần**), rồi **`READ_ONLY_MODE`** chặn **mọi** route ghi **sau khi** drain xong ⇒ **không cần miễn trừ nào**. Thêm `drain_timeout` để worker treo không chặn runbook vô hạn. Runbook thành 2a/2b/2c. Thêm I-DRAIN1 + I-DRAIN2 | `LEGACY_IMPORT §6.1`, `TEST_STRATEGY`, `TARGET_ARCHITECTURE §5.1` |
| H2 | `/readyz` được runbook yêu cầu nhưng **không có trong hợp đồng** | HIGH | Thêm **bảng endpoint nội bộ chuẩn**: `/health` (**không** chạm DB, chỉ process/build) và `/readyz` (**có** chạm DB, trả `{ ok, db_ok, db_branch, migration_version, checked_at }`). Cả hai dưới `/api/internal/*` ⇒ tắt ở production public. Thêm vào ma trận driver | `API_CONTRACT_PLAN` §12, `TARGET_ARCHITECTURE §5.1` |

---

## v2 ROUND 17 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Internal readiness contract remains contradictory and absent from the MVP
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §12; `BACKEND_MVP_SPEC.md` §4; `IMPLEMENTATION_ROADMAP.md` P0
- **Evidence:** `API_CONTRACT_PLAN.md:1824-1827` calls `/api/internal/health` and `/api/internal/readyz` canonical, unauthenticated, and disabled in public production. Immediately afterward, `API_CONTRACT_PLAN.md:1834-1838` defines `/api/internal/ready` instead, requires `INTERNAL_TOKEN`, and enables both readiness and health in production. Lines `1862-1863` again refer to `/ready`, not `/readyz`. `BACKEND_MVP_SPEC.md:135-143` and `IMPLEMENTATION_ROADMAP.md:93,101,111` inventory only `/api/internal/health`. The actual repository has no backend that could supply an implicit implementation (`REPOSITORY_ASSESSMENT.md:35-41`).
- **Why it matters:** Implementing the canonical contract, MVP inventory, or roadmap produces three different systems. The mandatory restore drill can omit `/readyz`, deploy an inaccessible endpoint, or expose it under unintended authentication and production rules. I-IMP6 therefore is not implementable deterministically.
- **Remediation:** Delete the obsolete `/ready` definitions and make one machine-readable route inventory authoritative. Add `/api/internal/readyz` to `BACKEND_MVP_SPEC.md`, the roadmap phase that creates infrastructure endpoints, OpenAPI/internal OpenAPI, permission policy, and production security tests. Specify one auth rule, one production-availability rule, success and failure statuses, and the exact response schema.

### [HIGH] Drain timeout cannot reap a hung attempt while claims are disabled
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1; `API_AND_WORKER_PROTOCOL.md` §7; `TEST_STRATEGY.md` I-DRAIN1/I-IMP6
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:178-180` blocks every claim, waits for zero open attempts, but says that after `drain_timeout` it will “để lease hết hạn tự nhiên rồi tiếp tục.” Lease expiry alone does not update database state: `API_AND_WORKER_PROTOCOL.md:319-328` says the reaper must close the open attempt and change job status. Its primary reaper runs only at the beginning of `/jobs/claim` (`:321`), which DRAINING rejects; its fallback cron can run only daily on Hobby (`:314-322`). Nevertheless, `TEST_STRATEGY.md:69` expects zero open attempts before enabling `READ_ONLY_MODE`.
- **Why it matters:** A killed or unreachable worker can leave `job_attempt.outcome IS NULL` after the timeout. The runbook must either wait potentially a day, violate its zero-attempt precondition, or cut over while work remains logically active. That risks stale writes, replayed work, and divergent state across database branches.
- **Remediation:** Add an explicit admin-authorized `drain-reap` operation, or have the drain controller invoke the existing reaper directly after the deadline, while claims remain blocked. It must atomically expire overdue leases, close their attempts as `EXPIRED`, transition jobs, and repeat until zero live attempts. Define behavior for leases not yet expired at the deadline—force-expire them or abort the cutover—and test a killed worker with cron disabled.


---

## v2 ROUND 17 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Hợp đồng endpoint nội bộ **tự mâu thuẫn** (`/ready` vs `/readyz`) và **vắng khỏi MVP** | HIGH | Xoá mọi `/ready` cũ; lập **bảng chuẩn duy nhất** cho `/health` (không auth, không chạm DB, **có** ở production — liveness probe), `/readyz` (**`INTERNAL_TOKEN`**, chạm DB, trả `db_ok`/`db_branch`/`migration_version`, 503 khi lỗi), `/seed` (tắt cứng ở production). Đưa cả `/readyz` và `/drain-reap` vào inventory MVP + roadmap P1 + acceptance | `API_CONTRACT_PLAN` §12, `BACKEND_MVP_SPEC` §4, `IMPLEMENTATION_ROADMAP` P1 |
| H2 | `drain_timeout` **không thu hồi được** attempt treo khi claim bị chặn | HIGH | Chỉ ra vòng lặp chết: reaper **chính** nằm ở đầu `/jobs/claim` mà `DRAINING` **đang chặn**; cron dự phòng trên Hobby chỉ 1 lần/ngày ⇒ điều kiện *0 attempt mở* có thể **không bao giờ** đạt. Thêm **`POST /api/internal/drain-reap`** (Pool, idempotent): cưỡng bức hết hạn lease + đóng attempt `EXPIRED` + chuyển job, gọi lặp tới `open_attempts=0`. Với lease **chưa** quá hạn: `force=true` (mặc định, cưỡng bức) hoặc `force=false` (**huỷ cutover**) — không có "im lặng bỏ qua". Thêm I-DRAIN3 (giết worker + **tắt cron**) và I-DRAIN4 | `LEGACY_IMPORT §6.1`, `TARGET_ARCHITECTURE §5.1`, `TEST_STRATEGY`, `BACKEND_MVP_SPEC` |

---

## v2 ROUND 18 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 3 HIGH.

### [HIGH] Authoritative internal-route contract remains contradictory
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §12 “Endpoint nội bộ”
- **Evidence:** `API_CONTRACT_PLAN.md:1820-1828` calls a three-route table the “bảng chuẩn DUY NHẤT” and says obsolete `/ready` references were deleted, but `:1843-1849` defines seven additional internal routes, while `:1868` still explicitly specifies ``/ready` bật ở production``. More critically, `/readyz` requires `INTERNAL_TOKEN` in production at `:1825`, while `:1857` says production is deliberately not given `INTERNAL_TOKEN`. The repository has no existing backend implementation that could resolve these conflicts.
- **Why it matters:** `/readyz` cannot authenticate in production under the documented secret policy, so the restore verification required by `LEGACY_IMPORT_AND_SYNC_PLAN.md:211` cannot run. The competing route inventories also prevent reliable OpenAPI generation, production route filtering, and security testing.
- **Remediation:** Make one genuinely exhaustive internal-route inventory, including `/version`, `/reset`, `/clock`, test ticks, and `/drain-reap`. Replace the remaining `/ready` reference with `/readyz`. Provision a distinct production operations credential for `/readyz` and `/drain-reap`, or define an ADMIN-session authentication flow; do not simultaneously require and prohibit `INTERNAL_TOKEN` in production. Generate `openapi.internal.json` and production allow/deny tests from that inventory.

### [HIGH] Drain-reap has no implementable API contract
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §12; `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1; `BACKEND_MVP_SPEC.md` §4
- **Evidence:** The purported authoritative table at `API_CONTRACT_PLAN.md:1822-1826` omits `/api/internal/drain-reap` entirely. `BACKEND_MVP_SPEC.md:139` describes its auth as `ADMIN/INTERNAL_TOKEN`, while `LEGACY_IMPORT_AND_SYNC_PLAN.md:202-208` alternates `INTERNAL_TOKEN/ADMIN` and introduces `force=true|false` without defining a request schema, response schema, status codes, DRAINING precondition, authorization semantics, or idempotency key. The only test, `TEST_STRATEGY.md:66-67`, assumes `open_attempts=0` and “huỷ cutover” but does not define how `force=false` communicates that outcome.
- **Why it matters:** Independent implementations can disagree on whether `force` is a query parameter or JSON field, whether an ADMIN cookie is accepted on an internal endpoint, and whether a non-expired lease yields 200, 409, or 503. The runbook therefore cannot reliably decide whether it is safe to enable `READ_ONLY_MODE` and switch the Neon endpoint.
- **Remediation:** Add `/api/internal/drain-reap` to the authoritative internal OpenAPI inventory. Define a strict body such as `{force:boolean}`, one production-capable authentication mechanism, required `DRAINING=true`, and exact responses containing at least `expired_attempts`, `requeued_jobs`, `failed_jobs`, `open_attempts`, and `cutover_safe`. Specify that `force=false` with live leases performs no mutations and returns a defined conflict response. Add contract, RBAC, wrong-environment, and concurrent heartbeat/complete/reap tests.

### [HIGH] Force-drain performs an unbounded serverless transaction
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1 drain procedure; `TARGET_ARCHITECTURE.md` §5.1 driver matrix
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:202-204` requires one transaction to expire “mọi lease” and update their attempts and jobs. `TARGET_ARCHITECTURE.md:171` repeats the single-transaction design. This conflicts with the ordinary reaper’s explicit row/time bounds in `API_AND_WORKER_PROTOCOL.md:324-325`. No batch limit, cursor, statement timeout, lock order, or partial-progress response is defined for drain-reap.

---

## v2 ROUND 18 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Hợp đồng endpoint nội bộ **vẫn mâu thuẫn** | HIGH | **Nguyên nhân do tôi**: vòng trước tôi thêm một bảng nhỏ **trùng lặp** cạnh bảng 9-route đã có ⇒ hai nguồn sự thật. **Xoá bảng trùng**, giữ bảng đầy đủ. Sửa `/ready` → `/readyz`. Giải mâu thuẫn token bằng **§12.3: tách `OPS_TOKEN` (có ở production, cho `readyz`/`drain-reap`) khỏi `INTERNAL_TOKEN` (chỉ preview/test, cho `seed`/`reset`/`clock`)** ⇒ lớp phòng thủ 3 của §12.1 giữ nguyên hiệu lực mà vẫn vận hành được production. Thêm I-OPS1 | `API_CONTRACT_PLAN` §12+§12.3, `IMPLEMENTATION_ROADMAP` P1, `BACKEND_MVP_SPEC` |
| H2 | `drain-reap` **không có hợp đồng khả thi** | HIGH | Thêm **§12.4 hợp đồng đầy đủ**: auth `OPS_TOKEN`, tiền điều kiện `DRAINING` bật (tắt ⇒ **409 `DRAINING_NOT_ACTIVE`**), driver Pool, request `{force, max_rows, max_ms}.strict()`, response `{reaped, open_attempts_remaining, has_more, forced, duration_ms}`, thứ tự khoá, idempotency, audit, rate limit. Làm rõ `force=false` "báo huỷ cutover" **bằng dữ liệu** (`open_attempts_remaining>0`, `has_more=false`), không bằng mã lỗi | `API_CONTRACT_PLAN` §12.4, `LEGACY_IMPORT §6.1`, `BACKEND_MVP_SPEC` |
| H3 | Force-drain là **transaction không chặn** trên serverless | HIGH | Thêm **batch limit** `max_rows`/`max_ms` (cùng kỷ luật với reaper thường ở `API_AND_WORKER_PROTOCOL §7`), cursor qua `has_more`, tiến triển từng lô qua nhiều lời gọi, thứ tự khoá `build_job → job_attempt` chống deadlock. Test khẳng định batch limit: `max_rows=1` với 3 attempt treo ⇒ phải gọi 3 lần | `API_CONTRACT_PLAN` §12.4, `TARGET_ARCHITECTURE §5.1`, `LEGACY_IMPORT §6.1`, `TEST_STRATEGY` I-DRAIN3 |

---

## v2 ROUND 19 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Drain completion ignores leased jobs that have not started
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1 steps 2a–2c; `API_AND_WORKER_PROTOCOL.md` §4.4; `TEST_STRATEGY.md` I-DRAIN1–I-DRAIN4
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:178-180` defines safety as zero open `job_attempt` rows, while `:192-194` says `DRAINING` blocks only `claim` and explicitly permits `start`. `API_AND_WORKER_PROTOCOL.md:191-200` shows that a claimed job remains `LEASED` without an open attempt until `/start` changes it to `RUNNING` and creates the attempt. Thus `drain-reap` can return `open_attempts_remaining=0`, after which an already-leased worker can call `/start` before `READ_ONLY_MODE` is enabled. Tests at `TEST_STRATEGY.md:64-67` cover attempts but not this `start`-versus-drain race.
- **Why it matters:** The runbook can declare the system drained and switch Neon branches while a worker starts or continues work against the old branch. That can lose results, duplicate execution, or split job state across branches.
- **Remediation:** Make the drain barrier cover both `LEASED` jobs and open attempts. Once `DRAINING` begins, reject `/start` for leases that were not already running, or atomically revoke/requeue all `LEASED` jobs before reporting cutover-safe. Return separate `leased_jobs_remaining` and `open_attempts_remaining` fields and require both to be zero. Add deterministic `start`-versus-drain-reap and `start`-between-final-reap-and-read-only tests using transaction barriers.

### [HIGH] Shared OPS_TOKEN cannot enforce ADMIN authorization or truthful auditing
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §§12.3–12.4; `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1 “Quyền & bí mật”; `DATA_MODEL_PLAN.md` §1 `audit_event`
- **Evidence:** `API_CONTRACT_PLAN.md:1858` assigns one static `OPS_TOKEN` to both read-only `/readyz` and destructive `/drain-reap`; `:1866` makes possession of that token the entire authorization rule. Nevertheless, `:1876` records the action as `actor_kind='USER'`. `DATA_MODEL_PLAN.md:85-87` requires audit events to contain `actor_id`, but the shared token identifies no user. This contradicts `LEGACY_IMPORT_AND_SYNC_PLAN.md:222-223`, which says only `ADMIN` may run the restore procedure. `TEST_STRATEGY.md:68` checks token separation only and never verifies ADMIN authorization, actor attribution, or read/write scope separation.
- **Why it matters:** Any monitor or operator holding the readiness credential can force-expire production work during `DRAINING`. The backend cannot prove which administrator performed the action, revoke one operator independently, enforce RBAC, or truthfully populate the append-only audit record.
- **Remediation:** Separate readiness and mutation credentials. Keep a narrowly scoped read-only token for `/readyz`; require an authenticated ADMIN session or user PAT with an explicit `ops:drain` scope for `/drain-reap`, preferably with step-up authentication. Bind the credential to a persisted principal, write its real `actor_id`, support per-principal rotation/revocation, and add tests for non-admin denial, read-token denial, revoked credentials, actor attribution, and cross-token misuse.


---

## v2 ROUND 19 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Drain bỏ sót job **`LEASED` nhưng chưa `start`** | HIGH | Một job có thể `LEASED` mà **chưa có `job_attempt`** (worker đã claim, chưa gọi `/start`). Chỉ đếm attempt mở ⇒ drain **tưởng đã xong** trong khi worker vẫn giữ lease và có thể `/start` ngay sau đó — ghi vào DB **sau** khi ta tưởng đã đóng băng. **Sửa:** điều kiện drain xong là **cả hai** về 0 (`job_attempt WHERE outcome IS NULL` **và** `build_job WHERE status IN ('LEASED','RUNNING')`); `drain-reap` cũng phải thu hồi **lease không có attempt** (`LEASED → QUEUED`). Test I-DRAIN3 nay phủ **hai** tình huống giết worker | `LEGACY_IMPORT §6.1`, `TEST_STRATEGY` I-DRAIN1/I-DRAIN3 |
| H2 | `OPS_TOKEN` dùng chung ⇒ **không kiểm được `ADMIN`, audit ghi sai sự thật** | HIGH | Đổi thành **`api_token` gắn user** với `scopes=['ops']`: xác thực ra `user_id` thật ⇒ kiểm được `ADMIN` ⇒ `audit_event.actor_id` **đúng người** đã chạy `drain-reap` trên production; xoay/thu hồi **theo từng người**. `readyz` cần scope `ops`; `drain-reap` cần scope `ops` **và** `ADMIN`. `INTERNAL_TOKEN` **vẫn** là secret dùng chung — chấp nhận được vì nó **không tồn tại ở production**. Thêm I-OPS2 | `API_CONTRACT_PLAN` §12+§12.3+§12.4, `DATA_MODEL_PLAN` §1, `TEST_STRATEGY`, `BACKEND_MVP_SPEC`, `IMPLEMENTATION_ROADMAP` P1 |

---

## v2 ROUND 20 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, **1 HIGH**.

### [HIGH] Two-counter drain fix is absent from the executable API contract
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §12.4; `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1; `TEST_STRATEGY.md` I-DRAIN3/I-DRAIN4/I-IMP6
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:179` correctly requires both `job_attempt WHERE outcome IS NULL` and `build_job WHERE status IN ('LEASED','RUNNING')` to reach zero, but `:180` invokes `drain-reap` only when “còn attempt mở” and loops only until `open_attempts_remaining=0`. The authoritative contract at `API_CONTRACT_PLAN.md:1884-1888` limits work by number of “attempt” rows and returns only `{ reaped, open_attempts_remaining, has_more, forced, duration_ms }`; it defines neither a live-job counter nor the required `LEASED → QUEUED` handling for a lease without an attempt. `TEST_STRATEGY.md:66-67` likewise terminates on `open_attempts_remaining`, while I-IMP6 at `:73` checks only zero open attempts. This matters because `API_AND_WORKER_PROTOCOL.md:198-200` creates `job_attempt` only during `/start`, so a claimed-but-not-started job has no row in the counter used by the endpoint and runbook.
- **Why it matters:** Round-19 H1 remains implementationally unresolved. An attempt-less `LEASED` job may not trigger `drain-reap`, may not consume its batch limit, and cannot be represented in its response. The runbook can therefore proceed to `READ_ONLY_MODE` and branch cutover while a worker still owns a valid lease. Independent implementations following §12.4 would also be fully contract-compliant while never reclaiming that lease.
- **Remediation:** Make §12.4 operate on live leases/jobs, not merely open attempts. Return separate `open_attempts_remaining` and `live_jobs_remaining` (or `leased_jobs_remaining` plus `running_jobs_remaining`) and define `cutover_safe` as all required counters being zero. Specify CAS transitions for both `LEASED` without an attempt (`LEASED → QUEUED`, clear lease fields) and `RUNNING` with an attempt (close it `EXPIRED`, then requeue/fail). Define `max_rows` over locked `build_job` candidates so attempt-less leases count toward the batch. Update the runbook to invoke reaping whenever either counter is nonzero and loop until both are zero. Update I-DRAIN3, I-DRAIN4, and I-IMP6 to assert both response counters, including an isolated batch containing only claimed-but-not-started jobs.

VERDICT: CHANGES_REQUIRED
tokens used
33,968

---

## v2 ROUND 20 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Sửa "hai bộ đếm" ở vòng 19 **chưa vào hợp đồng API thực thi** | HIGH | Đưa vào §12.4: **phạm vi thu hồi hai nhóm** — (a) `job_attempt` đang mở ⇒ đóng `EXPIRED`; (b) job **`LEASED` chưa có attempt** ⇒ `LEASED → QUEUED`, xoá `lease_token`/`lease_until`. Response đổi thành **hai bộ đếm riêng** (`reaped_attempts`/`reaped_leases`, `open_attempts_remaining`/`leased_jobs_remaining`). Thêm dòng **"điều kiện drain xong"** = cả hai bằng 0. `force=false` báo huỷ khi **một trong hai** > 0. Thứ tự khoá áp dụng cho cả hai nhóm. Test khẳng định response có đủ hai bộ đếm | `API_CONTRACT_PLAN` §12.4, `LEGACY_IMPORT §6.1`, `TEST_STRATEGY` I-DRAIN3 |

---

## v2 ROUND 21 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 1 HIGH, 1 MEDIUM.

### [HIGH] Two-group drain still has a one-group batch limit
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §12.4; `TEST_STRATEGY.md` I-DRAIN3
- **Evidence:** `API_CONTRACT_PLAN.md:1883` expands reclaiming to two groups: open attempts and `LEASED` jobs without attempts. However, `API_CONTRACT_PLAN.md:1885` still defines `max_rows` as “tối đa `max_rows` attempt,” so attempt-less leases do not consume the documented limit. `TEST_STRATEGY.md:66` expects `max_rows=1` with three unspecified mixed “mục treo” to require three calls, contradicting the attempt-only contract and failing to isolate a batch containing only claimed-but-not-started jobs. The actual job lifecycle confirms these rows have no attempt: `API_AND_WORKER_PROTOCOL.md:198-200` creates `job_attempt` only during `/start`.
- **Why it matters:** An implementation can comply with §12.4 while reclaiming an unbounded number of attempt-less leases in one Pool transaction. A large queue can therefore exceed the Vercel duration budget, hold locks excessively, or roll back without progress—the exact serverless failure the batch limit was introduced to prevent.
- **Remediation:** Define `max_rows` over locked `build_job` candidates across both groups, with each reclaimed job consuming one slot. Specify deterministic candidate ordering and make `has_more` mean that another eligible candidate remains. Add a test containing only at least three `LEASED` jobs without attempts; with `max_rows=1`, assert exactly one transition per call and three calls before both remaining counters reach zero.

### [MEDIUM] Restore drill still validates only one drain counter
- **Severity:** MEDIUM
- **Document:** `TEST_STRATEGY.md` I-IMP6 and I-DRAIN4; `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1
- **Evidence:** `TEST_STRATEGY.md:73` still proceeds from shutdown after checking only “0 `job_attempt` mở,” without asserting zero `LEASED`/`RUNNING` jobs or both API response counters. `TEST_STRATEGY.md:67` tests `force=false` using only `open_attempts_remaining>0`. `LEGACY_IMPORT_AND_SYNC_PLAN.md:180` invokes `drain-reap` only when “còn attempt mở,” even though the same line later requires both counters to reach zero; `:217` likewise documents only `open_attempts_remaining > 0` for abort signaling.
- **Why it matters:** The focused drain test cannot compensate for the end-to-end restore drill. A claimed-but-not-started job can remain leased while I-IMP6 passes and enables `READ_ONLY_MODE`, so the mandatory recovery acceptance test does not prove the corrected cutover invariant.

---

## v2 ROUND 21 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Drain hai nhóm nhưng **batch limit chỉ tính một nhóm** | HIGH | Batch limit nay tính trên **TỔNG**: `reaped_attempts + reaped_leases ≤ max_rows`. **`has_more` = còn việc ở BẤT KỲ nhóm nào** (`open_attempts_remaining > 0 OR leased_jobs_remaining > 0`) — nếu tính từ một nhóm thì nhóm (b) có thể **không bao giờ** được xử lý sau khi nhóm (a) cạn. Nêu rõ **thứ tự xử lý (a) trước (b) sau** trong mỗi lời gọi | `API_CONTRACT_PLAN` §12.4 |
| M1 | Diễn tập restore chỉ kiểm **một** bộ đếm | MEDIUM | I-IMP6 bước 2b nay chờ **cả hai** bộ đếm về 0 và thêm bước **2b′** gọi `drain-reap` lặp khi `has_more`. I-DRAIN3 kiểm batch limit trên tổng (`max_rows=1`, 2 attempt + 2 lease ⇒ **4 lần gọi**) và khẳng định `has_more` đúng khi một nhóm cạn còn nhóm kia chưa | `TEST_STRATEGY` I-IMP6, I-DRAIN3 |

---

## v2 ROUND 22 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Restore runbook still ignores attempt-less leases at the decision point
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1; `TEST_STRATEGY.md` I-DRAIN4
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:180` invokes `drain-reap` only when “còn attempt mở,” despite requiring both counters to reach zero later in the same sentence. At `:217`, the `force=false` abort condition reports only `open_attempts_remaining > 0`. Likewise, `TEST_STRATEGY.md:67` tests only `open_attempts_remaining>0`. Yet `LEGACY_IMPORT_AND_SYNC_PLAN.md:196-201` explicitly recognizes that a `LEASED` job may have no attempt and requires `leased_jobs_remaining=0`.
- **Why it matters:** If all attempts are closed but an attempt-less `LEASED` job remains, step 2b′ is not triggered. The restore cannot safely advance or recover that lease. The force-false test would also miss an implementation that incorrectly reports zero attempts while leaving leased jobs alive.
- **Remediation:** Change the step-2b′ predicate to “either counter remains nonzero.” Change the force-false abort description to `open_attempts_remaining > 0 OR leased_jobs_remaining > 0`. Extend I-DRAIN4 with an isolated unexpired, attempt-less `LEASED` job and require `leased_jobs_remaining>0`, `open_attempts_remaining=0`, `has_more=false`, and no mutation.

### [HIGH] `has_more` has mutually incompatible definitions
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §12.4
- **Evidence:** `API_CONTRACT_PLAN.md:1886` unconditionally defines `has_more=true` when `open_attempts_remaining > 0 OR leased_jobs_remaining > 0`. But `:1892` requires `has_more=false` under `force=false` while either of those same counters remains positive because leases are not yet expired. `:1891` instructs callers to repeat whenever `has_more=true`.
- **Why it matters:** A conforming implementation cannot satisfy both rules. Following line 1886 makes a force-false operator loop indefinitely over ineligible leases; following line 1892 violates the advertised round-21 invariant. The ambiguity also prevents a reliable test oracle and conflates “live work remains” with “another eligible batch can be reaped now.”

---

## v2 ROUND 22 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Runbook vẫn bỏ qua **lease không có attempt** ở điểm quyết định | HIGH | Bước 2b/2b′ nay nêu **tường minh** điểm quyết định: dừng lặp khi `has_more=false`, rồi kiểm **hai** bộ đếm; còn `blocked_remaining>0` ⇒ **hoặc** `force=true` **hoặc** huỷ cutover. Ghi rõ **`has_more=false` một mình KHÔNG có nghĩa là drain xong** | `LEGACY_IMPORT §6.1` |
| H2 | **`has_more` có hai định nghĩa loại trừ nhau** | HIGH | Đây là mâu thuẫn **do tôi tạo ra** ở vòng 21: vừa định nghĩa `has_more` = "còn bộ đếm > 0", vừa nói `force=false` trả `has_more=false` **trong khi** bộ đếm > 0. **Tách hai khái niệm**: `has_more` = *còn việc **thu hồi được ngay*** (`reclaimable_remaining > 0`) — dùng để quyết định gọi lại; `blocked_remaining` = *còn việc nhưng **không** thu hồi được với `force` hiện tại*. Điều kiện drain xong vẫn kiểm hai bộ đếm gốc, **không** dựa vào `has_more` | `API_CONTRACT_PLAN` §12.4, `LEGACY_IMPORT §6.1`, `TEST_STRATEGY` I-DRAIN4 |

---

## v2 ROUND 23 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Restore runbook still ignores attempt-less leases at the reaping trigger
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1, steps 2b′ and “Lease CHƯA quá hạn tại deadline”
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:180` still says “Quá `drain_timeout` mà còn attempt mở ⇒ gọi `drain-reap`,” so an attempt-less `LEASED` job does not trigger the endpoint. `:220` still specifies only `open_attempts_remaining > 0` for the blocked `force=false` outcome. This conflicts with `API_CONTRACT_PLAN.md:1883`, which explicitly includes `LEASED` jobs without attempts, and with the actual planned lifecycle in `API_AND_WORKER_PROTOCOL.md:198-200`, where a `job_attempt` is created only during `/start`.
- **Why it matters:** If a worker claims a job but never starts it, `open_attempts_remaining` can be zero while `leased_jobs_remaining` is positive. The runbook can wait indefinitely or fail to invoke the only recovery operation. The round-22 decision logic added after the call cannot help because the endpoint is never called.
- **Remediation:** Change the trigger at line 180 to invoke `drain-reap` whenever `open_attempts_remaining > 0 OR leased_jobs_remaining > 0` after `drain_timeout`. Change line 220 to describe the blocked case using `blocked_remaining > 0` and explicitly allow `open_attempts_remaining=0, leased_jobs_remaining>0`.

### [HIGH] Drain test retains the obsolete “any remaining work means has_more” definition
- **Severity:** HIGH
- **Document:** `TEST_STRATEGY.md` I-DRAIN3 and I-DRAIN4
- **Evidence:** `TEST_STRATEGY.md:66` requires “attempt hết nhưng lease còn ⇒ vẫn `has_more=true`.” That contradicts `API_CONTRACT_PLAN.md:1886-1887`, where `has_more` is true only when `reclaimable_remaining > 0`; an unexpired remaining lease under the default `force=false` must instead produce `has_more=false` and `blocked_remaining>0`. I-DRAIN3 does not constrain the remaining lease to be expired or use `force=true`. I-DRAIN4 at `:67` also does not explicitly establish the required isolated attempt-less state (`open_attempts_remaining=0`).
- **Why it matters:** The QA oracle directs implementations back to the round-21 semantics and can reject a correct implementation or accept one that loops on unreclaimable leases. It also fails to prove that the attempt-less case fixed in round 22 works independently.

---

## v2 ROUND 23 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | **Điều kiện kích hoạt** `drain-reap` vẫn chỉ nhắc attempt | HIGH | Bước 2b′ đổi điều kiện thành **`open_attempts_remaining > 0` HOẶC `leased_jobs_remaining > 0`** (không chỉ "còn attempt mở"). Test I-DRAIN3 sửa theo | `LEGACY_IMPORT §6.1`, `TEST_STRATEGY` I-DRAIN3 |
| H2 | Test còn giữ định nghĩa `has_more` **đã lỗi thời** | HIGH | Sửa I-DRAIN3: `has_more` = **còn việc thu hồi được ngay** (`reclaimable_remaining > 0`), **không** phải "còn bộ đếm bất kỳ > 0". Phân biệt rõ hai ca: attempt hết + lease **quá hạn** còn ⇒ `has_more=true`; lease **chưa** quá hạn với `force=false` ⇒ `has_more=false` nhưng `blocked_remaining > 0`. I-IMP6 bước 2b′ thêm bước kiểm hai bộ đếm sau khi dừng lặp | `TEST_STRATEGY` I-DRAIN3, I-IMP6 |

---

## v2 ROUND 24 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH. *(Vòng này Codex quét lại **toàn bộ** plan, không chỉ vùng drain/restore.)*

### [HIGH] Restore runbook still misreports attempt-less blocked leases
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1, “Lease CHƯA quá hạn tại deadline”
- **Evidence:** [`LEGACY_IMPORT_AND_SYNC_PLAN.md:220`](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/docs/content-hub/LEGACY_IMPORT_AND_SYNC_PLAN.md:220>) says `force=false` returns `open_attempts_remaining > 0` with `has_more=false`. This is false for a claimed-but-not-started job: [`API_AND_WORKER_PROTOCOL.md:198`](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/docs/content-hub/API_AND_WORKER_PROTOCOL.md:198>) creates `job_attempt` only at `/start`, so such a job can have `open_attempts_remaining=0`, `leased_jobs_remaining>0`, and `blocked_remaining>0`. The authoritative response contract confirms the separate counters at [`API_CONTRACT_PLAN.md:1890`](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/docs/content-hub/API_CONTRACT_PLAN.md:1890>).
- **Why it matters:** Round-23’s fix is not consistent across all documents. An operator or implementation following this normative runbook paragraph can treat `open_attempts_remaining=0` as evidence that no blocked work exists and proceed while a valid lease remains, risking writes during branch cutover.
- **Remediation:** Replace line 220 with: “`force=false` ⇒ `has_more=false`, `blocked_remaining>0`, and at least one drain counter remains positive (`open_attempts_remaining>0 OR leased_jobs_remaining>0`)”. Explicitly state that an attempt-less lease produces `open_attempts_remaining=0, leased_jobs_remaining>0`.

### [HIGH] API contract carries an obsolete, conflicting idempotency schema
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §1.7 and §14 A-1; `DATA_MODEL_PLAN.md` §1
- **Evidence:** [`API_CONTRACT_PLAN.md:156`](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/docs/content-hub/API_CONTRACT_PLAN.md:156>) and [`API_CONTRACT_PLAN.md:2003`](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/docs/content-hub/API_CONTRACT_PLAN.md:2003>) claim the shared table is missing and prescribe `(endpoint, key, request_sha256, response_body)`, unique `(principal_id, endpoint, key)`, with 24-hour retention. The actual data-model plan already defines it at [`DATA_MODEL_PLAN.md:74`](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/docs/content-hub/DATA_MODEL_PLAN.md:74>) using `(scope, idempotency_key, request_hash, response_snapshot)`, unique `(scope, idempotency_key, principal_id)`, with 30-day retention at [`DATA_MODEL_PLAN.md:86`](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/docs/content-hub/DATA_MODEL_PLAN.md:86>). Other contracts depend explicitly on the latter shape, including score handling at [`API_CONTRACT_PLAN.md:864`](</Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/docs/content-hub/API_CONTRACT_PLAN.md:864>).
- **Why it matters:** This is a foundational distributed-write invariant, not cosmetic naming. Independent P1/P2 implementations can create incompatible migrations and conflict keys, breaking retry deduplication for score, approval, freeze, promotion, import, and job completion. A retry could then duplicate state transitions or fail because the code queries columns absent from the chosen migration.

---

## v2 ROUND 24 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Runbook **báo sai** loại lease bị chặn | HIGH | Câu "`force=false` ⇒ `open_attempts_remaining > 0`" **sai** với job đã claim mà **chưa `/start`**: `job_attempt` chỉ được tạo ở `/start` (`API_AND_WORKER_PROTOCOL §4.4`), nên ca đó có `open_attempts_remaining = 0` **nhưng** `leased_jobs_remaining > 0`. Sửa thành `has_more=false` **kèm** `blocked_remaining > 0`, và nhấn mạnh **luôn kiểm cả hai bộ đếm**, không suy từ một cái | `LEGACY_IMPORT §6.1` |
| H2 | Hợp đồng API mang **schema idempotency lỗi thời, xung đột** | HIGH | `API_CONTRACT_PLAN` vẫn nói bảng "chưa có" và đề xuất hình dạng khác (`endpoint`/`key`/`request_sha256`/`response_body`, unique `(principal_id, endpoint, key)`, TTL 24h) trong khi `DATA_MODEL_PLAN §1.5` **đã** định nghĩa chính thức (`scope`/`idempotency_key`/`request_hash`/`response_snapshot`, unique `(scope, idempotency_key, principal_id)`, retention **30 ngày**) và các hợp đồng khác **đã phụ thuộc** hình dạng đó. **Đóng A-1**, trỏ về định nghĩa chuẩn, đánh dấu mô tả cũ đã bị thay thế | `API_CONTRACT_PLAN` §1.7+§14 |

---

## v2 ROUND 25 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Production operations endpoints are disabled by the implementation checklist
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §16, checklist item 7
- **Evidence:** `API_CONTRACT_PLAN.md:2048` requires testing that “`/api/internal/*` trả 404 khi VERCEL_ENV='production'`.” This contradicts the canonical endpoint table at `API_CONTRACT_PLAN.md:1827-1834`, where `/api/internal/health`, `/api/internal/readyz`, `/api/internal/version`, and `/api/internal/drain-reap` explicitly operate in production. The correctly scoped test at `API_CONTRACT_PLAN.md:1846-1848` names only `{seed,reset,clock,reaper-tick,enqueue-tick,echo-limits}`.
- **Why it matters:** Implementing the checklist literally disables `readyz` and `drain-reap` in production. That makes the mandatory Neon restore runbook impossible: it cannot reclaim stranded leases or verify the restored database branch. It also creates mutually incompatible security tests.
- **Remediation:** Replace the wildcard in checklist item 7 with the exact preview-only route set from §12.1. Add separate production tests proving `health` and `version` remain available, `readyz` accepts an `ops`-scoped PAT, and `drain-reap` requires both `ops` scope and `ADMIN`.

### [HIGH] Restore runbook still specifies a forbidden shared operations token
- **Severity:** HIGH
- **Document:** `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1, steps 2b′ and drain-reap explanation
- **Evidence:** `LEGACY_IMPORT_AND_SYNC_PLAN.md:180` and `:212` identify drain-reap authentication as `OPS_TOKEN`. The canonical contract instead requires a user-bound `api_token` with `ops` scope and `ADMIN` role (`API_CONTRACT_PLAN.md:1875-1894`) and explicitly states that “`OPS_TOKEN` không được là secret dùng chung” (`API_CONTRACT_PLAN.md:1860` onward). `DATA_MODEL_PLAN.md:63-68` likewise defines operations authentication as a user-bound PAT so the audit event records the real operator.
- **Why it matters:** The production recovery instructions can be implemented or followed using a shared bearer secret, defeating per-user revocation, RBAC, and truthful attribution for the destructive force-reap operation. It also leaves two incompatible authentication contracts for a mandatory MVP acceptance workflow.

---

## v2 ROUND 25 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Test an ninh **tắt luôn** endpoint vận hành production | HIGH | §12.1 yêu cầu "**mọi** `/api/internal/*` trả 404 ở production" — nhưng `readyz` và `drain-reap` **bắt buộc** hoạt động trên production cho runbook restore. **Sửa:** danh sách tắt là **ĐÓNG** và chỉ gồm **nhóm công cụ test** (`seed`/`reset`/`clock`/`reaper-tick`/`enqueue-tick`/`echo-limits`); nhóm vận hành (`health`/`version`/`readyz`/`drain-reap`) được bảo vệ bằng **token scope `ops` + `ADMIN`**, không bằng cách tắt route. Sửa I-OPS1 để **không** khẳng định "mọi route trả 404" | `API_CONTRACT_PLAN` §12.1, `TEST_STRATEGY` I-OPS1 |
| H2 | Runbook vẫn ghi **`OPS_TOKEN` dùng chung** | HIGH | Thay bằng **`api_token` scope `ops` gắn user + vai trò `ADMIN`** ở mọi chỗ trong runbook; tách rõ **hai loại bí mật**: API key **Neon** (thao tác hạ tầng, ngoài env ứng dụng) vs **token HTTP gắn user** (để `audit_event.actor_id` ghi đúng người) | `LEGACY_IMPORT §6.1`, `IMPLEMENTATION_ROADMAP` P1 |

---

## v2 ROUND 26 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] Production security checklist still disables required operations routes
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §16 “Checklist trước khi implement”
- **Evidence:** `API_CONTRACT_PLAN.md:2054` still requires: “Test an ninh: `/api/internal/*` trả 404 khi `VERCEL_ENV='production'`.” This directly contradicts the closed production policy at `API_CONTRACT_PLAN.md:1846-1854`, which disables only `seed`, `reset`, `clock`, `reaper-tick`, `enqueue-tick`, and `echo-limits`, while explicitly keeping `health`, `version`, `readyz`, and `drain-reap` operational. `TEST_STRATEGY.md:68` also explicitly warns that asserting all `/api/internal/*` return 404 breaks the restore runbook.
- **Why it matters:** The implementation checklist is the handoff developers are likely to follow. Its wildcard test would either fail a correct implementation or cause developers to disable `/readyz` and `/drain-reap` in production, making the mandatory Neon restore/cutover procedure inoperable.
- **Remediation:** Replace `API_CONTRACT_PLAN.md:2054` with the exact closed-list assertion from I-OPS1: only `/seed`, `/reset`, `/clock`, `/reaper-tick`, `/enqueue-tick`, and `/echo-limits` return 404 in production; `/health`, `/version`, `/readyz`, and `/drain-reap` remain available under their declared authentication rules. Add a static test that fails if either route set drifts from the canonical inventory.

### [HIGH] Production `readyz` authorization still contradicts the restore runbook
- **Severity:** HIGH
- **Document:** `API_CONTRACT_PLAN.md` §12 and `LEGACY_IMPORT_AND_SYNC_PLAN.md` §6.1
- **Evidence:** `API_CONTRACT_PLAN.md:1828` assigns `/api/internal/readyz` only an `api_token` with scope `ops`; `API_CONTRACT_PLAN.md:1873` explicitly says it “không cần `ADMIN`.” Conversely, `LEGACY_IMPORT_AND_SYNC_PLAN.md:239-241` states that the runbook’s HTTP operations—explicitly including `readyz` and `drain-reap`—use an `ops`-scoped user token “với vai trò `ADMIN`.” `API_CONTRACT_PLAN.md:1851-1853` also describes both operational routes as protected by an ops-scoped token plus `ADMIN`.
- **Why it matters:** The canonical API contract and mandatory recovery runbook authorize different principals. An implementer cannot know whether a non-admin ops token may inspect production database branch identity. Tests derived from the contract can pass while the runbook’s required authorization invariant fails.

---

## v2 ROUND 26 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | Checklist an ninh vẫn **tắt** route vận hành | HIGH | Còn sót một dòng checklist "`/api/internal/*` trả 404 ở production" mâu thuẫn với chính sách đã chốt. Sửa thành: **nhóm công cụ test** trả 404; **nhóm vận hành** (`health`/`version`/`readyz`/`drain-reap`) **vẫn hoạt động**, bảo vệ bằng token chứ không bằng tắt route | `API_CONTRACT_PLAN` §14 checklist |
| H2 | Quyền `readyz` **mâu thuẫn** giữa hai tài liệu | HIGH | `API_CONTRACT_PLAN` nói `readyz` "không cần `ADMIN`", runbook lại nói cả hai route đều cần `ADMIN`. **Chốt theo nguyên tắc đặc quyền tối thiểu**: `readyz` **chỉ cần scope `ops`** (chỉ đọc trạng thái, không đổi gì); `drain-reap` cần scope `ops` **và** `ADMIN` (đổi trạng thái job). Đồng bộ cả ba chỗ | `API_CONTRACT_PLAN` §12+§12.3, `LEGACY_IMPORT §6.1` |

---

## v2 ROUND 27 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

> 🔎 **Đáng chú ý:** vòng này Codex **không còn** tìm thấy lỗi ở vùng drain/restore (đã ổn định sau
> nhiều vòng), mà chuyển sang phát hiện lỗi **mới, thật** ở vùng scoring — dấu hiệu việc quét rộng
> đang có tác dụng.

### [HIGH] Scoring a draft silently makes it immutable
- **Severity:** HIGH
- **Document:** `DATA_MODEL_PLAN.md` §5 “score_run”; `API_CONTRACT_PLAN.md` §10.2 frontend contract matrix; `API_AND_WORKER_PROTOCOL.md` §11 authorization
- **Evidence:** `DATA_MODEL_PLAN.md:331-334` defines a composite FK from `(score_run.content_revision_id, input_snapshot_hash)` to `(content_revision.id, content_sha256)`. Consequently, changing a draft’s content and hash after scoring is rejected by PostgreSQL while that score exists. However, `API_AND_WORKER_PROTOCOL.md:429` explicitly permits users to “Tạo/sửa revision DRAFT”, and `API_CONTRACT_PLAN.md:1613` exposes `PATCH …/{rid}` for `DRAFT`/`REVIEW_REQUIRED`. `BACKEND_MVP_SPEC.md:17-18` also scores content before producing an improved draft, while `BACKEND_MVP_SPEC.md:40` requires score runs for both v1 and v2.
- **Why it matters:** A perfectly authorized edit to a scored draft will fail at the database FK, even though the API contract says drafts are editable. Removing or overwriting the score is forbidden because score history is append-only. The implementation must therefore either violate revision editing, violate score immutability, or weaken snapshot integrity. The advertised edit–score–improve workflow cannot behave consistently.
- **Remediation:** Choose and document one coherent lifecycle. Prefer immutable revision payload rows: replace draft `PATCH` with creation of a child revision, and keep mutable review workflow state outside `content_revision`. Alternatively prohibit audit/score creation until a revision is `FROZEN`, update the MVP ordering accordingly, and create a new revision for every subsequent change. Add a DB/API test that scores a revision and then attempts the currently advertised edit path.

### [HIGH] The canonical schema omits fields required to construct and validate algorithm versions
- **Severity:** HIGH
- **Document:** `DATA_MODEL_PLAN.md` §5 “algorithm / algorithm_version”; `ALGORITHM_VERSIONING_PLAN.md` §§2.3 and 12.1; `BACKEND_MVP_SPEC.md` §2
- **Evidence:** `DATA_MODEL_PLAN.md:260-264` defines `algorithm_version` with `ruleset`, `prompt_template`, `prompt_sha256`, `weights`, `released_at`, and `is_active`, but no `dimensions`, `comparability_group`, `determinism`, `weights_provenance`, or `superseded_by_version_id`. Those fields exist only as “Trường bổ sung đề xuất” in `ALGORITHM_VERSIONING_PLAN.md:74-87`. Nevertheless, `BACKEND_MVP_SPEC.md:40-52` requires the E2E test to derive the exact score-dimension count from `algorithm_version.dimensions`, and `ALGORITHM_VERSIONING_PLAN.md:885-887` requires validating `keys(weights) == set(dimensions)` and every submitted dimension against that field.
- **Why it matters:** Implementing the declared data model produces no place to store the MVP’s published dimension set, so the server cannot enforce the score payload, calculate expected coverage, or satisfy the E2E acceptance criterion without inventing an undocumented representation. Implementers following different documents can create incompatible migrations and API behavior.

---

## v2 ROUND 27 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | **Chấm một `DRAFT` âm thầm khoá nó lại** | HIGH | FK composite `(revision_id, input_snapshot_hash)` khiến sửa `DRAFT` sau khi chấm bị PostgreSQL **từ chối**, trong khi API vẫn quảng cáo `PATCH` cho `DRAFT` ⇒ lỗi FK khó hiểu ở thao tác được phép. **Chốt bất biến S-0: `score_run`/`audit_run` chỉ nhận revision `FROZEN`** (FK hằng số `required_revision_status`). Lý do: điểm chấm trên nội dung **còn sửa được** vốn vô nghĩa — đó chính là lý do có `input_snapshot_hash`. Muốn đánh giá bản nháp ⇒ **freeze trước**. Sửa luồng MVP: freeze v1 **trước** khi chấm. Thêm I-S0 | `DATA_MODEL_PLAN` §5, `BACKEND_MVP_SPEC` §1, `TEST_STRATEGY` |
| H2 | Schema `algorithm_version` **thiếu trường bắt buộc** để dựng/validate | HIGH | Nâng từ "đề xuất" lên **schema chính thức**: `dimensions` text[] **NOT NULL**, `weights` jsonb **NOT NULL**, `min_coverage_bp`, `comparability_group`, `determinism`, `weights_provenance`, `superseded_by_version_id`. Thêm **CHECK khi publish**: `keys(weights) == set(dimensions)`, `Σ weights = 10000`, `dimensions ⊆` danh mục 17, không trùng lặp. Cần vì `BACKEND_MVP_SPEC` **suy số dòng `score_dimension` từ `dimensions`**. Thêm I-S7 | `DATA_MODEL_PLAN` §5, `TEST_STRATEGY` |

---

## v2 ROUND 28 — kết quả thô

**VERDICT: CHANGES_REQUIRED** — 0 BLOCKER, 2 HIGH.

### [HIGH] MVP audits v1 before freezing it
- **Severity:** HIGH
- **Document:** `BACKEND_MVP_SPEC.md` §1 “Định nghĩa MVP”
- **Evidence:** `BACKEND_MVP_SPEC.md:16-18` orders the acceptance flow as “CLI claim job `ANALYZE_CONTENT` → gửi `audit_run` + `audit_finding`” and only afterward “**FREEZE** revision v1.” This contradicts the new S-0 database invariant in `DATA_MODEL_PLAN.md:332-350`, which states that both `score_run` and `audit_run` may reference only `FROZEN` revisions through a constant composite FK. `TEST_STRATEGY.md:52` explicitly expects a direct DB insert of an audit for a `DRAFT` revision to fail.
- **Why it matters:** The mandatory end-to-end MVP flow cannot pass: its first audit write targets an imported revision that is still `DRAFT`, so Neon must reject it. This means the round-27 S-0 correction was not propagated across all 14 documents, and the stated frontend-free MVP acceptance test is internally impossible.
- **Remediation:** Move the v1 freeze immediately after import/source association and before the first `ANALYZE_CONTENT` job. Remove the redundant second audit if only one audit is required, or clearly distinguish two post-freeze audit/score jobs. Update the E2E test to assert that auditing before freeze returns `409 REVISION_NOT_FROZEN`, then freeze v1 and successfully persist the audit.

### [HIGH] Canonical algorithm provenance enum rejects the planned lifecycle values
- **Severity:** HIGH
- **Document:** `DATA_MODEL_PLAN.md` §5 `algorithm / algorithm_version`
- **Evidence:** `DATA_MODEL_PLAN.md:265` canonically restricts `weights_provenance` to `EXPERT_JUDGMENT|FITTED`. In contrast, `ALGORITHM_VERSIONING_PLAN.md:87` defines the field as `EXPERT_JUDGMENT|FITTED_FROM_ANALYTICS|INHERITED`; lines 379-381 require `FITTED_FROM_ANALYTICS`, and line 857 instructs the calibration workflow to publish a new version using exactly that value. Round 27 explicitly promoted this field to canonical schema, so this is no longer a merely proposed naming difference.
- **Why it matters:** Implementing the canonical Neon constraint makes the documented analytics-calibration path fail at publication, while loosening or renaming it ad hoc makes migrations, generated API validation, and stored provenance inconsistent. `INHERITED` versions also cannot be represented. This defeats the purpose of storing auditable algorithm provenance.

---

## v2 ROUND 28 — Bảng disposition

| # | Finding | Sev | Đã xử lý thế nào | File đã sửa |
|---|---|:-:|---|---|
| H1 | MVP **audit v1 trước khi freeze** | HIGH | Luồng nghiệm thu vẫn để `ANALYZE_CONTENT` **trước** bước freeze, mâu thuẫn bất biến **S-0** vừa thêm ở R27 (`audit_run` cũng chỉ nhận revision `FROZEN`). Đổi thứ tự: **FREEZE v1 → ANALYZE → SCORE → IMPROVE (v2 DRAFT) → FREEZE v2 → APPROVE**. Nay khớp cả FK ở CSDL lẫn test I-S0 | `BACKEND_MVP_SPEC` §1 |
| H2 | Enum `weights_provenance` **từ chối giá trị vòng đời đã thiết kế** | HIGH | `DATA_MODEL_PLAN` (vừa nâng lên canonical ở R27) ghi `EXPERT_JUDGMENT\|FITTED`, trong khi `ALGORITHM_VERSIONING_PLAN` dùng `FITTED_FROM_ANALYTICS` ở quy trình hiệu chỉnh. Thống nhất theo bản đầy đủ: **`EXPERT_JUDGMENT\|FITTED_FROM_ANALYTICS\|INHERITED`** | `DATA_MODEL_PLAN` §5 |

---

# FINAL ARCHITECTURE REVIEW (phạm vi thu hẹp)

> Sau 29 vòng review toàn tài liệu, chiến lược được đổi: **đóng băng planning package**, chỉ review
> **tính đúng đắn để triển khai**. Wording / consistency / drift **ngoài phạm vi** và không được chặn duyệt.
> Mỗi ứng viên BLOCKER/HIGH phải qua **bộ lọc 4 câu hỏi**; trả lời **No** cả bốn ⇒ hạ xuống backlog.

```bash
codex exec --sandbox read-only "$(cat prompt_final_arch.txt)" < /dev/null
```

**Kết quả: 1 HIGH qua được bộ lọc, 7 mục hạ xuống backlog.**

### [HIGH] Artifact promotion order violates the partial unique index
- **Severity:** HIGH
- **Area:** job lifecycle
- **Q1 incorrect implementation:** Yes — following the specified order can make artifact replacement fail with a uniqueness violation.
- **Q2 data corruption:** No — PostgreSQL should roll back the transaction.
- **Q3 security vulnerability:** No — this is a transactional ordering defect.
- **Q4 MVP impossible:** No — the ordering is straightforward to correct.
- **Evidence:** [API_AND_WORKER_PROTOCOL.md:268](/Users/nguyenthanhtung/Documents/Local%20AI/Vietneu-TTS/docs/content-hub/API_AND_WORKER_PROTOCOL.md:268) requires promoting the new artifact before superseding the existing promoted artifact. [DATA_MODEL_PLAN.md:521](/Users/nguyenthanhtung/Documents/Local%20AI/Vietneu-TTS/docs/content-hub/DATA_MODEL_PLAN.md:521) defines an immediate partial unique index on `(build_job_id, role) WHERE promotion_state='PROMOTED'`. If a promoted artifact already exists for that job and role, step 1 creates two qualifying rows before step 2 can run.
- **Remediation:** Within the locked completion transaction, first change the existing promoted artifact to `SUPERSEDED`, then promote the selected provisional artifact. Alternatively, perform both transitions in one SQL statement/CTE that never exposes two promoted rows. Lock the job and relevant artifacts, verify the lease and attempt, and retain the partial unique index as the final concurrency guard.

## IMPLEMENTATION BACKLOG

- Add composite foreign keys tying each artifact’s `build_job_id`, `job_attempt_id`, `content_revision_id`, and `worker_machine_id` together; the current independent FKs permit internally inconsistent metadata if another write path bypasses route validation.
- Make claim-time `job_lease_history` insertion part of the same single HTTP statement, using a writable CTE; the documented CAS currently only updates `build_job`, although concurrency tests depend on complete lease history.
- Define audit `run_sequence` allocation for nullable `algorithm_version_id`. PostgreSQL uniqueness treats `NULL` values as distinct, so the current unique constraint does not serialize unversioned human/tool audits.
- Specify savepoint or transaction boundaries for import dry-run and fatal-abort reporting so business rows roll back while `import_record`, report, and terminal batch status survive.
- Add the `content_item.published_video_id` foreign key only when the P6 `video` table exists, or introduce the nullable column without its FK earlier and add the constraint later.
- Finalize a shared serverless rate-limit mechanism before implementation; in-memory counters are unsuitable across Vercel invocations.
- The local media durability risk remains consciously accepted: Neon preserves text and metadata, but loss of unpublished local media requires rerendering.

VERDICT: ARCHITECTURE_CHANGES_REQUIRED
tokens used
107,037
### [HIGH] Artifact promotion order violates the partial unique index
- **Severity:** HIGH
- **Area:** job lifecycle
- **Q1 incorrect implementation:** Yes — following the specified order can make artifact replacement fail with a uniqueness violation.
- **Q2 data corruption:** No — PostgreSQL should roll back the transaction.
- **Q3 security vulnerability:** No — this is a transactional ordering defect.
- **Q4 MVP impossible:** No — the ordering is straightforward to correct.

---

## Disposition

| # | Finding | Sev | Q1 | Q2 | Q3 | Q4 | Quyết định | Đã sửa thế nào |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| 1 | Thứ tự promote artifact **vi phạm partial unique** | HIGH | **Yes** | No | No | No | **Accepted & FIXED** | Đảo thứ tự trong transaction: **SUPERSEDE bản cũ TRƯỚC, PROMOTE bản mới SAU** (hoặc gộp một CTE để không bao giờ lộ hai hàng `PROMOTED`). Đây là lỗi thật: partial unique là **immediate**, nên ở ca **retry sinh hash khác** (chuyện bình thường vì TTS/video không tất định) bước promote tạo hàng `PROMOTED` thứ hai ⇒ **rollback cả transaction**, artifact mới không bao giờ promote được. Thêm **ca hồi quy** vào I-23 | `API_AND_WORKER_PROTOCOL §6.1`, `DATA_MODEL_PLAN §6`, `TEST_STRATEGY` I-23 |

**Sau khi sửa: 0 BLOCKER, 0 HIGH còn lại trong phạm vi kiến trúc.**
