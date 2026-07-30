# TEST_STRATEGY.md

> **Backend-only.** Không có E2E trình duyệt trong giai đoạn này — frontend chưa tồn tại.
> Mọi luồng phải kiểm chứng được bằng **HTTP client**.
>
> Xuất phát điểm: repo hiện có 8 file test **chỉ cho TTS engine** (dùng mock);
> CI chỉ chạy `pytest`, **không** lint/typecheck (`.github/workflows/ci.yml`).
> `pytest` hiện **chưa** cài trong `.venv` — cần `uv sync --group dev`.

---

## 0. Nguyên tắc

1. **Bất biến trước, độ phủ sau.** Mỗi bất biến §1 phải có ít nhất một test **cố tình vi phạm** nó và khẳng định hệ thống chặn được.
2. **Không đụng test upstream.** `tests/` thuộc thư viện TTS. Test backend nằm ở `apps/hub/tests/`, test CLI ở `hub_cli/tests/`, mỗi bên một job CI riêng.
3. **Không gọi API thật trong CI.** YouTube/LLM/ComfyUI đều mock. Test thật gắn nhãn `live`, chạy thủ công.
4. **Fixture từ dữ liệu thật.** `analytics_reviews/2026-07-27_daily_factory_raw/*.json` là response YouTube thật; `content_repo_clone/**/manifest.json` là manifest thật. Dùng làm golden fixture thay vì bịa.
5. **Test đồng thời phải thật sự đồng thời** — nhiều connection thật tới **Neon thật**, không mock lock.
6. **Không test nào được phụ thuộc UI.**

---

## 1. Bất biến hệ thống (hợp đồng kiểm thử)

| ID | Bất biến | Test tiêu biểu | Phase |
|---|---|---|---|
| **I-1** | Job build luôn trỏ revision đã `FROZEN` | Tạo job với revision `DRAFT` → 409 | P4 |
| **I-2** | Không approve A rồi build B | Build B bằng approval A → chặn bằng **so khớp ID** | P2 |
| **I-3** | Một job không hai worker xử lý | N invocation claim đồng thời trên **Neon thật, dùng ĐÚNG HTTP driver của production**; `job_lease_history` không chồng lấn; toàn bộ M job cuối cùng đều được claim | P4 |
| **I-5** | Analytics không ghi đè lịch sử | Ingest D, ingest lại D (số đã hiệu chỉnh) → cả hai truy vấn được | P6 |
| **I-6** | Không truy cập ngoài quyền kênh | Ma trận role × endpoint × kênh; trả **404** không phải 403 | P1 |
| **I-7** | Worker không tạo được command tuỳ ý | `params` field lạ / chuỗi lệnh → Zod `.strict()` từ chối 422 | P4 |
| **I-8** | Log không chứa secret | Bơm token vào log → không có trong `job_event` | P4 |
| **I-9** | Artifact phải verify checksum | Sửa file sau khi báo cáo → verify fail | P4 |
| **I-11** | Revision `FROZEN` bất biến | UPDATE trực tiếp → trigger chặn | P2 |
| **I-12** | Không build trùng cùng revision | Hai job cùng `(revision, job_type)` còn sống → một fail. **Gồm cả `DEFERRED`** | P4 |
| **I-13** | Promote B ⇒ supersede A **cùng transaction** | Promote B → A `SUPERSEDED`, job đang chờ của A xử lý theo chính sách khai báo | P2 |
| **I-14** | Lease hết hạn ⇒ worker cũ không ghi được | Ép hết lease rồi `complete` → 409 | P4 |
| **I-15** | `complete` idempotent | Gọi 3 lần cùng key → 1 kết quả | P4 |
| **I-18** | Chính sách tự-duyệt được cưỡng chế đúng chế độ | `TWO_PERSON_REQUIRED` chặn `approved_by==created_by`; `SELF_APPROVAL_ALLOWED` cho phép **nhưng** bắt buộc xác nhận nâng cao + `audit_event.self_approved=true`. **Test cả hai** | P2 |
| **I-19** | Không `shell=True` trong code mới | Test tĩnh quét AST `hub_cli/` | P4 |
| **I-20** | Đường dẫn artifact không thoát workspace | Kiểm ở **worker** (`realpath`+no-follow+hash từ fd); server kiểm cú pháp + attestation | P4 |
| **I-23** | Chỉ artifact `PROMOTED` publish được | 2 attempt khác hash → đúng 1 `PROMOTED`/role. ⚠️ **Ca hồi quy bắt buộc**: attempt #1 promote xong **rồi** attempt #2 (hash khác) promote — phải **thành công**, không vi phạm partial unique ⇒ chứng minh thứ tự *supersede-trước, promote-sau* | P4 |
| **I-24** | Quota deferral không đốt `execution_attempt` | Hết quota 5 lần → job vẫn không `FAILED` | P4 |
| **I-25** | Approval A còn hiệu lực khi mới *soạn* B | Tạo B `DRAFT` → approval A vẫn `ACTIVE` | P2 |
| **I-26** | Analytics map theo `columnHeaders` | Đảo thứ tự cột trong fixture → kết quả không đổi | P6 |
| **I-27** | Ingest dở dang không đánh dấu hoàn chỉnh | Ngắt giữa chừng → `is_complete=false`, resume từ checkpoint | P6 |
| **I-S1** | `score_run` **và** `score_dimension` append-only | Chấm lại có chủ đích → `run_sequence` mới; UPDATE/DELETE trực tiếp trên **cả hai** bảng → trigger chặn; xoá `score_run` không cascade xoá dimension | P2 |
| **I-S2** | `input_snapshot_hash` khớp `content_sha256` — ép ở **CSDL** | FK composite tới `content_revision(id, content_sha256)`; ghi thẳng vào DB với hash sai → **CSDL từ chối** (không chỉ API). Kèm `input_truncated_at` khi bộ chấm cắt cụt đầu vào | P2 |
| **I-S3** | `overall_score` = Σ(dimension × weight) | Tính lại khớp theo `algorithm_version.weights` | P2 |
| **I-S4** | `algorithm_version` bất biến sau phát hành | Sửa version đã released → chặn | P2 |
| **I-S0** | **Chỉ chấm/audit revision `FROZEN`** | `score_run`/`audit_run` trỏ revision `DRAFT` ⇒ **CSDL từ chối** (FK hằng số). Và: chấm một revision **không** làm `DRAFT` khác mất khả năng `PATCH` — vì bản `DRAFT` **không thể** bị chấm | P2 |
| **I-S7** | `algorithm_version` hợp lệ khi publish | `keys(weights) != set(dimensions)` ⇒ **từ chối**; `Σ weights != 10000` ⇒ **từ chối**; `dimensions` có phần tử ngoài danh mục 17 ⇒ **từ chối**; `dimensions` rỗng ở version released ⇒ **từ chối** | P2 |
| **I-S5** | **`run_sequence` cấp phát an toàn khi đồng thời** | N tiến trình độc lập, **mỗi tiến trình một `Idempotency-Key` riêng**, cùng nhắm một `(revision, version, hash)` ⇒ sequence **liên tục, không trùng, không hổng**; tổng `score_run` == N; **không** `idempotency_record` mồ côi. Chạy trên **Neon thật** | P2 |
| **I-S6** | `previous_score_run_id` cùng `algorithm_version_id` | FK composite tự tham chiếu từ chối run khác version (test bằng SQL trực tiếp) | P2 |
| **I-PROMO1** | Promote **luôn** ghi `revision_promotion_event` | Promote thành công ⇒ có đúng 1 event; ép lỗi giữa transaction ⇒ **rollback toàn bộ** (không có event mồ côi, `production_revision_id` không đổi) | P2 |
| **I-PROMO2** | Event chỉ trỏ revision **thuộc đúng content item** | FK composite từ chối `to_revision_id` của item khác (SQL trực tiếp) | P2 |
| **I-PROMO3** | **Promote đồng thời — đúng một thắng** | Hai transaction cùng gửi `expected_production_revision_id = A`, một promote B một promote C ⇒ **đúng một** thắng; kẻ thua nhận **409 `CONCURRENT_PROMOTION`** và **không** ghi event. Chuỗi event tuyến tính (`from` sau == `to` trước). ⚠️ Test này **fail** nếu CAS so với giá trị đọc trong khoá thay vì kỳ vọng của caller. Chạy trên **Neon thật** | P2 |
| **I-PROMO5** | **Promote chỉ supersede gate `PRODUCTION_READY` của revision cũ** | Dựng item có approval `ACTIVE` ở **cả bốn** gate → promote → khẳng định **chỉ** approval `PRODUCTION_READY` của revision cũ thành `SUPERSEDED`; `RESEARCH_READY`/`CONTENT_READY`/`PUBLISH_READY` **giữ nguyên `ACTIVE`** | P2 |
| **I-PROMO4** | **Promote vs revoke (đua)** | Revoke xen giữa lúc promote ⇒ promote **fail**, không event mồ côi. Test **tất định** bằng barrier chứng minh bên nào giành khoá `approval` trước | P2 |
| **I-PROMO6** | **Revoke KHÔNG làm kẹt item vĩnh viễn** | Revoke approval của revision A (đang production) **commit xong**, sau đó promote B có approval `ACTIVE` ⇒ **THÀNH CÔNG**. Lịch sử `REVOKED` của A **giữ nguyên**, không bị đổi thành `SUPERSEDED` | P2 |
| **I-PROMO7** | Hợp đồng promote đầy đủ | `expected_production_revision_id` **thiếu** ⇒ 422; `null` (lần đầu) ⇒ hợp lệ; UUID sai ⇒ 409 `CONCURRENT_PROMOTION`; field lạ ⇒ 422 (`.strict()`); gửi qua `If-Match` thay vì body ⇒ **không** được chấp nhận | P2 |
| **I-PROMO8** | **Promote lần đầu (`NULL → A`)** | `production_revision_id` đang `NULL` ⇒ promote A thành công: con trỏ = A, event `NULL→A`, approval của A **giữ nguyên `ACTIVE`** (bước 4 và 7 **không** chạy) | P2 |
| **I-PROMO9** | **Từ chối promote chính nó (`A→A`)** | `:rid` == production hiện tại ⇒ **409 `ALREADY_PRODUCTION`**; con trỏ **không đổi**, **không** event mới, approval của A **vẫn `ACTIVE`** | P2 |
| **I-REV1** | **`revision_no` cấp nguyên tử** | N tiến trình cùng tạo revision cho một item ⇒ `revision_no` liên tục, không trùng, không hổng (chống `MAX+1` đọc ngoài khoá) | P2 |
| **I-DRAIN1** | **`DRAINING` chặn claim nhưng không đóng băng job dở** | Bật `DRAINING` ⇒ `claim` **503**; job đang chạy vẫn `start`/`heartbeat`/`complete`; drain xong khi **CẢ HAI** về 0: `job_attempt WHERE outcome IS NULL` **và** `build_job WHERE status IN ('LEASED','RUNNING')` | P4 |
| **I-DRAIN2** | **Worker không claim lại sau shutdown** | `shutdown` khi `DRAINING` bật ⇒ worker poll tiếp vẫn nhận **503**, **không** giành được job mới | P4 |
| **I-DRAIN3** | **`drain-reap` thu hồi được attempt treo khi claim bị chặn** | **Giết** worker ở **hai tình huống**: (a) đã `start` (attempt mở) và (b) **mới claim, chưa `start`** (job `LEASED`, **không** có attempt) — cả hai đều phải được `drain-reap` thu hồi. Bật `DRAINING`, **tắt cron** ⇒ chờ tới `drain_timeout` vẫn còn **`open_attempts_remaining > 0` hoặc `leased_jobs_remaining > 0`**; gọi `POST /api/internal/drain-reap` (`OPS_TOKEN`) ⇒ attempt đóng `EXPIRED`, job về `QUEUED`. **Batch limit trên TỔNG hai nhóm**: `max_rows=1` với 2 attempt mở + 2 lease chưa `start` ⇒ phải gọi **4 lần**; mỗi lần `reaped_attempts + reaped_leases ≤ 1`. **`has_more` = còn việc THU HỒI ĐƯỢC NGAY** (`reclaimable_remaining > 0`), **không** phải "còn bộ đếm bất kỳ > 0": attempt hết nhưng lease **quá hạn** còn ⇒ `has_more=true`; lease **chưa** quá hạn với `force=false` ⇒ `has_more=false` **nhưng** `blocked_remaining > 0`. Drain xong chỉ khi **cả hai** bộ đếm = 0. Gọi lại ⇒ **idempotent** | P4 |
| **I-DRAIN4** | Lease **chưa** quá hạn tại deadline | `force=false` ⇒ `has_more=false` **nhưng** `blocked_remaining>0` và `leased_jobs_remaining>0`, **không** đổi trạng thái nào ⇒ runbook **không được** coi là drain xong. `force=true` ⇒ cưỡng bức hết hạn, job về `QUEUED`, mọi bộ đếm về 0 | P4 |
| **I-OPS1** | **Tách token vận hành / test** | Với `VERCEL_ENV='production'`: nhóm **công cụ test** (`seed`/`reset`/`clock`/`reaper-tick`/`enqueue-tick`/`echo-limits`) trả **404**; nhóm **vận hành** (`health`/`version`/`readyz`/`drain-reap`) **vẫn hoạt động**. ⚠️ Test **không** được khẳng định "mọi `/api/internal/*` trả 404" — sẽ phá runbook restore. Dùng nhầm token chéo nhau ⇒ **404** | P1 |
| **I-OPS2** | **Token `ops` gắn user, audit ghi đúng người** | `drain-reap` bằng token `ops` của user **không** phải `ADMIN` ⇒ **404**; bằng token của `ADMIN` ⇒ 200 **và** `audit_event.actor_id` == đúng user đó. Thu hồi token của một người **không** ảnh hưởng người khác | P1 |
| **I-DRV1** | **Mọi route ghi đều khai báo chế độ driver** | Test **tĩnh**: đối chiếu **inventory OpenAPI** (mọi method ≠ `GET`) với bảng khai báo máy đọc được; thiếu ⇒ **CI fail**. Miễn trừ chỉ cho POST **chứng minh được chỉ đọc**, phải ghi lý do | P1 |
| **I-IMP4** | **Nạp staging idempotent theo `legacy_ref`** | Nạp trùng (khác `Idempotency-Key`, khác cách chia chunk) ⇒ **không** sinh dòng thừa; cùng `legacy_ref` khác `legacy_sha256` ⇒ **409 `IMPORT_RECORD_CONFLICT`** | P3 |
| **I-IMP5** | **`finalize` — hai loại thất bại** (`LEGACY_IMPORT §5.4`) | (a) **validation-reject**: 1 bản ghi lỗi ⇒ bản đó `REJECTED`, các bản **hợp lệ vẫn commit**. (b) **huỷ lô** (mã lỗi chí mạng: `SECRET_FIELD_PRESENT`, lỗi hạ tầng) ⇒ **0** hàng nghiệp vụ, `status=FAILED`. (c) Dry-run ⇒ bảng nghiệp vụ **sạch**, `import_record`+report **còn**. ⚠️ Không được đòi "1 bản ghi fail ⇒ 0 hàng" — đó là mâu thuẫn với partial-reject | P3 |
| **I-IMP6** | **Diễn tập runbook restore đầy đủ** | Chạy **trọn 8 bước** `LEGACY_IMPORT §6.1` trên Neon branch thật: (1) tạo restore point → (2a) bật **`DRAINING`** — khẳng định `claim` trả **503 `DRAINING`** nhưng `start`/`heartbeat`/`complete` **vẫn chạy** → (2b) `worker/shutdown`, chờ **CẢ HAI** về 0 (`open_attempts_remaining` **và** `leased_jobs_remaining`), có `drain_timeout` → (2b′) `drain-reap` lặp khi `has_more=true`; dừng khi `has_more=false` rồi **kiểm hai bộ đếm** (còn `blocked_remaining>0` ⇒ `force=true` hoặc huỷ cutover) → (2c) `READ_ONLY_MODE` — khẳng định **mọi** route ghi trả **503**, **không** miễn trừ nào → (3) kiểm chứng branch **trước** cutover → (4) đổi endpoint + redeploy → (5) **`GET /api/internal/readyz`** trả `db_ok=true` và **đúng** `db_branch` → (6) mở ghi, worker tự đăng ký lại và claim tiếp → (7) `audit_event(IMPORT_RESTORED)`. **Đo `RTO`**. Khẳng định API key Neon **không** có trong env ứng dụng | P3 |
| **I-IMP7** | **`APPLY` là insert-only** | Bản ghi đã có trong `legacy_id_map` ⇒ `SKIPPED_DUPLICATE`, **không** UPDATE; outcome `UPDATED` **không chọn được** ở MVP | P3 |
| **I-DRV2** | **Transaction tương tác chạy đúng trên Pool** | `start` đồng thời, `complete` vs lease-expiry/reaper, promote artifact cạnh tranh — chạy qua **route thật + driver thật**, không kết nối đặc quyền | P4 |
| **I-A1** | Agent/worker **không** approve được | Worker token gọi approve → 403/404; `approval.approved_by` NOT NULL → `user` | P2 |
| **I-A2** | **Chỉ approve được revision đã `FROZEN`** | Approve revision `DRAFT` → **CSDL từ chối** (FK composite), không chỉ API. Test cả đường ghi SQL trực tiếp | P2 |
| **I-A3** | **Approval khoá vào đúng bytes đã duyệt** | `approved_content_sha256` phải khớp `content_revision.content_sha256`; sửa nội dung sau approve là bất khả (revision `FROZEN`) | P2 |
| **I-A4** | **Bằng chứng approval cùng revision + đúng gate** | Approve rev B viện dẫn `audit_run`/`score_run` của rev A → **CSDL từ chối**; sai `gate` → từ chối | P2 |
| **I-11b** | `FROZEN` **không bao giờ** chuyển `SUPERSEDED` | UPDATE status trên hàng `FROZEN` → trigger chặn; supersession đọc từ `production_revision_id` + `revision_promotion_event` | P2 |
| **I-1b** | Job build trỏ revision `FROZEN` — ép ở CSDL | INSERT `build_job` trỏ revision `DRAFT` bằng **SQL trực tiếp** → FK từ chối; test đồng thời freeze/tạo-job | P4 |
| **I-IMP1** | Import idempotent | Import 2 lần → 0 nhân đôi (`legacy_id_map`) | P3 |
| **I-IMP2** | Secret ⇒ **HUỶ CẢ LÔ**, không phải reject bản ghi | Lô **hỗn hợp**: 1 bản ghi chứa `refresh_token` + ≥1 bản ghi hợp lệ ⇒ `status=**FAILED**`, **0** hàng nghiệp vụ, **0** `legacy_id_map`; **không** giá trị secret nào trong staging/report/log/`audit_event`; report cấp-lô đã redact. `REJECTED` **chỉ** dành cho lỗi validation không chí mạng | P3 |
| **I-IMP3** | Hoàn tác import bằng **Neon restore** | Tạo restore point → `APPLY` → restore → DB về đúng trạng thái trước; ghi `audit_event(IMPORT_RESTORED)`. ⚠️ **Không** test endpoint rollback ứng dụng — nó **không tồn tại** ở MVP | P3 |
| **I-30** | Media không rời máy local | Không request nào body > 1 MB; `artifact.storage_backend='LOCAL'` | P4 |

---

## 2. Các tầng kiểm thử

### 2.1 Unit (thuần hàm, nhanh)
- Scoring: dimension → `overall`; `breakdown` cộng đúng; thiếu dữ liệu ⇒ `missing_data`, **không đoán**.
- Redaction: bảng mẫu token thật/giả.
- Chuẩn hoá nội dung trước khi hash (`content_sha256` ổn định khi chỉ khác whitespace không đáng kể — hoặc **cố ý không ổn định**, phải quyết và test đúng quyết định đó).
- Ánh xạ status legacy → mới; giá trị lạ ⇒ reject.
- Phân loại Long/Short.

### 2.2 Database
- Migration `up` chạy sạch, lặp lại được, trên Neon branch trống.
- ⚠️ **`downgrade` chỉ test trên DB dev dùng một lần.** Production **forward-only** — downgrade sẽ phá huỷ audit/approval/revision/score/analytics.
- Test **tương thích ngược một phiên bản**: binary cũ chạy được trên schema mới.
- Test **backup → restore** bằng Neon branching (diễn tập khôi phục).
- **Partial unique index** thực sự có hiệu lực: `approval ACTIVE`, `job LIVE_STATUSES` (**gồm `DEFERRED`**), `artifact PROMOTED`, `job_attempt outcome IS NULL`, `analytics_sync_partition RUNNING`.
- Trigger bất biến revision `FROZEN`.
- FK cascade/restrict đúng ý: xoá kênh **không** được xoá lịch sử analytics/score.
- ⚠️ Chạy trên **PostgreSQL thật (Neon)** — không dùng SQLite hay in-memory thay thế.

### 2.3 API integration
- Mỗi endpoint: 200/400/401/403/404/409/422.
- **Permission matrix test tự sinh**: mỗi (role, endpoint, kênh) khẳng định cho phép/từ chối theo `API_AND_WORKER_PROTOCOL.md §11`. **Endpoint mới thiếu khai báo quyền ⇒ test fail** (chống quên).
- **Tách nhóm auth**: worker token gọi User API → 401/403; PAT gọi Worker API → 401/403.
- Zod `.strict()` cho mọi input từ worker.
- Phân trang: cursor ổn định khi có bản ghi mới chèn vào.
- Body limit: gửi payload > 4,5 MB → 413 xử lý đàng hoàng (không 500).

### 2.4 State machine
- Sinh mọi cặp chuyển trạng thái; khẳng định tập hợp lệ đúng khai báo.
- Vòng đời biên tập (7 trạng thái CC) và sản xuất (Hub) test **riêng**, không trộn.
- Property-based (fast-check): chuỗi chuyển ngẫu nhiên không bao giờ đạt trạng thái không hợp lệ.

### 2.5 Worker protocol
- Đường hạnh phúc: register → claim → start → heartbeat → artifacts → complete.
- Token: hết hạn, bị revoke, sai, xoay có overlap 24h.
- Long-poll trả 204 đúng lúc hết chờ; `wait_seconds ≤ 25`.
- `X-Worker-Protocol` không hỗ trợ → **426**.
- Capability không đủ → không nhận job đó.
- `manifest_sha256` lệch → worker huỷ job.
- `start` idempotent: gọi 2 lần → cùng `job_attempt_id`, bộ đếm không tăng.

### 2.6 Race condition *(bắt buộc — chạy trên **Neon thật**, không mock, không SQLite)*

> **Yêu cầu tường minh của người dùng.** Bộ test này **không được** dùng mock, in-memory, hay SQLite.
> Nó phải chạy trên một **Neon branch thật**, qua **đúng HTTP driver của production**, với N tiến
> trình/invocation **độc lập** (không phải N promise trong cùng một process — điều đó không tái hiện
> được tranh chấp thật ở tầng CSDL).
>
> | Thiết lập | Giá trị tối thiểu |
> |---|---|
> | Neon branch riêng cho mỗi CI run | ✅ |
> | Số claimant đồng thời | ≥ 10 (P1 slice), ≥ 50 (P4) |
> | Số job trong hàng đợi | ≥ 100 |
> | Khẳng định | mỗi job đúng **một** lease · `job_lease_history` không chồng lấn · tổng `DONE` == số job · **không** job nào kẹt `QUEUED` khi còn worker rảnh |
- N worker × M job: mỗi job đúng một lần; tổng `DONE` == M.
- ⚠️ **Test phải chạy trên đúng driver của production (HTTP).** Claim là **một câu lệnh** nên
  transaction ngầm của PostgreSQL đã đủ — **không** cần Pool/WebSocket. Điều phải chứng minh bằng
  test là *hành vi*, không phải *lựa chọn driver*: N invocation đồng thời ⇒ mỗi job đúng một lease.
- **Test chống hồi quy hình dạng câu lệnh:** nếu ai đó tách claim thành SELECT rồi UPDATE riêng
  (hai câu), transaction ngầm **không còn** bao trùm ⇒ test race phải fail. Đây mới là bẫy thật.
- Claim đồng thời với reaper đang chạy.
- Cancel đúng lúc worker đang complete.
- Freeze revision đồng thời với tạo job.
- Hai request approve cùng lúc → một thắng.
- Hai cron sync chồng nhau → partial unique chặn.

### 2.7 Idempotency, retry, lease
- Cùng `Idempotency-Key` lặp N lần → một kết quả, body giống nhau — kiểm trên **`idempotency_record`**
  dùng chung (score/audit/approve/freeze/promote/import), **không chỉ** `build_job`.
- Cùng key nhưng **khác** `request_hash` → **409 `IDEMPOTENCY_KEY_REUSED`**.
- Lease hết hạn → `QUEUED`; `claim_count` tăng, **không** reset.
- `execution_attempt >= max_attempts` → `FAILED`, không lặp vô hạn.
- **Ba bộ đếm tách biệt**; **không nhánh nào giảm bộ đếm**.
- `DEFERRED` → `QUEUED` khi qua `not_before`; quá `max_deferral_age` → `FAILED`.
- Backoff có jitter.

### 2.8 Analytics ingestion *(P6)*
- Golden fixture từ `analytics_reviews/**_raw.json`.
- **SCD-2**: ingest D → sửa số → ingest lại D → bảng chính mới, `_history` giữ cũ.
- Map theo `columnHeaders`, không theo vị trí cột (I-26).
- **Từ chối** response thiếu `dimensions=day` (chống lưu tổng gộp khoảng vào bảng theo ngày).
- Phân loại lỗi: fixture riêng cho `quotaExceeded`, `dailyLimitExceeded`, `rateLimitExceeded`, `401`, `400 invalid metric` → mỗi loại một nhánh.
- Backfill chồng lấn (1–7/7 rồi 5–10/7) → không nhân đôi, không mất ngày.
- Biên timezone (video đăng 23:59 local).

### 2.9 Bảo mật
- Chống RCE: fuzz `params` với payload chèn lệnh.
- Path traversal artifact (`..`, tuyệt đối, symlink).
- **SSRF** *(P6+, khi có source fetch)*: URL trỏ `127.0.0.1`, `169.254.169.254`, `file://`, redirect vào mạng nội bộ → chặn. Fetch chạy ở **CLI**, không ở Vercel.
- **Prompt injection**: nội dung nguồn chứa chỉ thị ("ignore previous instructions…") → không làm đổi hành vi handler; không lọt vào tên file/tham số subprocess.
- Không secret trong: log, response, thông báo lỗi, `job_event`, `import_record`.
- Session: cố định phiên, CSRF, cookie flag, xoay id sau login.
- Rate limit login + claim.
- Quét tĩnh: `semgrep`/`eslint-plugin-security` cho `apps/hub`; test AST cấm `shell=True` cho `hub_cli`.

### 2.10 E2E API *(thay cho E2E trình duyệt)*
**Một** test chạy trọn chuỗi `BACKEND_MVP_SPEC.md §1` bằng HTTP client:
import → revision → audit → score → improve → **freeze** → **approve** → job → claim → build →
artifact → promote → `PRODUCTION_READY`.

> ⚠️ **Sửa theo Codex v2R4 HIGH-1.** Bản trước ghi `improve → approve → freeze` — **ngược thứ tự** so
> với BLOCKER đã chấp nhận ở vòng 2. Với FK composite
> `(content_revision_id, required_revision_status='FROZEN')`, approve một revision `DRAFT` sẽ **bị CSDL
> từ chối**, nên bài test E2E bắt buộc **không thể chạy hết** như mô tả cũ.
>
> Bài test phải khẳng định thêm:
> - Approve **trước** khi freeze ⇒ **409** (và CSDL từ chối nếu ghi thẳng SQL).
> - Approve thành công ⇒ `approval.approved_content_sha256` **bằng đúng** `content_revision.content_sha256`
>   đã chốt lúc freeze.
- Phải **lặp lại được** và tự dọn.
- Phải chạy được cả trên **Vercel preview deployment**, không chỉ localhost.
- ⚠️ **Không** dùng trình duyệt, không Playwright — frontend chưa tồn tại.

### 2.11 Failure injection
- Kill worker giữa job (SIGKILL) → phục hồi.
- Ngắt mạng khi gửi artifact metadata.
- Neon tạm không kết nối được → 503, không mất dữ liệu.
- Cold start Vercel giữa lúc long-poll.
- LLM CLI trả rác/không phải JSON → không làm sập job (tiền lệ `short_judge_panel_engine.py:82-150`).
- ComfyUI chết → circuit breaker (tiền lệ `asset_generation.py:31,50`).

### 2.12 Performance (ngưỡng cảnh báo hồi quy, không phải benchmark)
- Claim job < 200ms ở 10 worker đồng thời (tính cả cold start).
- Đọc content list 100 item < 500ms.
- Ingest 10k dòng metric < 60s.
- Endpoint bất kỳ < 10s (an toàn dưới giới hạn Vercel).

### 2.13 Cross-channel *(thay cho cross-tenant)*
Hệ thống **chưa** multi-tenant. Test hiện tại: user chỉ có quyền kênh A không đọc/ghi được kênh B
qua **bất kỳ** endpoint nào — kể cả list, search, export, và **thông báo lỗi** (404 không phải 403).
Khi thêm `workspace_id`, bộ test này nhân bản thành cross-workspace.

---

## 3. Công cụ & CI

| Hạng mục | Lựa chọn |
|---|---|
| Backend runner | **Vitest** (nhanh, hợp TS/Vite) |
| HTTP | `fetch` tới app handler hoặc preview URL |
| DB test | **Neon branch riêng cho mỗi CI run** — cùng engine **và đúng chế độ driver của từng route** (HTTP cho claim; Pool/WebSocket cho promote/score — `TARGET_ARCHITECTURE.md §5.1`). ⚠️ Test race/bất biến phải đi qua **route thật**, **không** dùng kết nối test đặc quyền |
| Property-based | `fast-check` |
| Mock HTTP ngoài | `msw` / `nock` |
| CLI test | `pytest` trong `hub_cli/` (venv riêng, **không** đụng `.venv` của thư viện) |
| Bảo mật | `semgrep`, test AST tự viết |
| Coverage | **80% cho `apps/hub/src/domain`** (logic nghiệp vụ). **Không** áp coverage lên `src/` upstream |

**CI (thêm job mới, không sửa job cũ):**
```yaml
hub-backend:
  - pnpm lint && pnpm typecheck
  - pnpm drizzle:check          # migration khớp schema
  - pnpm test:unit
  - pnpm test:integration       # Neon test branch
  - pnpm test:e2e               # chuỗi MVP
  - semgrep --config auto apps/hub
hub-cli:
  - ruff check hub_cli && mypy hub_cli
  - pytest hub_cli/tests -m "not live"
  - python -m tests.no_shell_true_ast   # I-19
```
Test race + E2E chạy job riêng (chậm hơn), bắt buộc trên PR vào `main`.

---

## 4. Ma trận bất biến × loại test

| Bất biến | Unit | DB | API | Race | E2E | Security |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| I-1, I-11, I-12 | | ✅ | ✅ | ✅ | ✅ | |
| I-2, I-13, I-25, I-A1 | | ✅ | ✅ | ✅ | ✅ | ✅ |
| I-3, I-14, I-15, I-24 | | ✅ | ✅ | ✅ | | |
| I-9, I-20, I-23, I-30 | ✅ | ✅ | ✅ | | ✅ | ✅ |
| I-5, I-26, I-27 | ✅ | ✅ | ✅ | | | |
| I-6 | | | ✅ | | ✅ | ✅ |
| I-7, I-19 | ✅ | | ✅ | | | ✅ |
| I-8 | ✅ | | ✅ | | | ✅ |
| I-S1…I-S4 | ✅ | ✅ | ✅ | | ✅ | |
| I-IMP1…I-IMP3 | | ✅ | ✅ | | ✅ | ✅ |

---

## 5. Test bắt buộc TRƯỚC khi bọc bất kỳ executor nào

Với **mỗi** stage được trích thành job handler, phải có trước:

1. **Characterization** — ghi lại hành vi hiện tại (input → output) làm mốc.
2. **Cô lập một revision** — dựng trạng thái có **nhiều** tập sẵn sàng cùng topic; chạy handler cho revision X; khẳng định **chỉ** X bị đụng.
   *(Bài test này bắt trực tiếp lỗi `run_audio_stage(topic)` xử lý cả topic — `long_batch_runner.py:155-160`.)*
3. **Giới hạn workspace** — handler không ghi ngoài workspace của job.
4. **Cancellation** — đặt cờ cancel → handler dừng và dọn dẹp.
5. **Retry/resume** — chạy lại sau fail giữa chừng → không hỏng, không trùng.
6. **Báo cáo artifact tất định** — đúng tập artifact, đúng role.
7. **Dry-run không gọi mạng** — khẳng định **không** có upload/API thật ở chế độ dry-run.

**Không đủ 7 mục ⇒ không đưa stage đó vào hàng đợi.**

> ⚠️ **Không có miễn trừ "code cũ đang chạy production nên không test".** Chính lớp code đó là
> executor mà worker sẽ chạy; hàng đợi đúng không cứu được executor sai.

---

## 6. Nợ kiểm thử chấp nhận có ý thức

| Bỏ qua | Lý do | Xem lại khi |
|---|---|---|
| E2E trình duyệt | Frontend chưa tồn tại (ngoài phạm vi giai đoạn này) | Phase 8 |
| Test đa máy worker | Chỉ có 1 máy | Khi thêm máy thứ hai |
| Load test quy mô lớn | 3 kênh, 1 người dùng | Khi >10 kênh |
| Render TTS/video thật trong CI | Cần model + ~26GB | Chạy thủ công `live` trước mỗi release |
| Test Blob | Blob **không dùng** ở MVP | Khi bật Blob |
