# API_CONTRACT_PLAN.md

> **Phạm vi: HỢP ĐỒNG API HƯỚNG NGƯỜI DÙNG / FRONTEND.**
> Tài liệu này định nghĩa **contract + shape dữ liệu** mà một frontend *tương lai* sẽ tiêu thụ.
> **KHÔNG** thiết kế UI, component, styling, layout, visual design ở giai đoạn này
> (`TARGET_ARCHITECTURE.md §12`).
>
> **Không lặp lại Worker API.** Toàn bộ `/api/worker/*` (claim, lease, heartbeat, log, artifact,
> complete/fail, analytics snapshot) đã được đặc tả đầy đủ ở `API_AND_WORKER_PROTOCOL.md` —
> ở đây chỉ **tham chiếu chéo**.
>
> Đọc trước: `TARGET_ARCHITECTURE.md`, `DATA_MODEL_PLAN.md`, `API_AND_WORKER_PROTOCOL.md`.

---

## 0. Ranh giới tài liệu

| Nội dung | Ở đâu |
|---|---|
| Nhóm API, auth base, mẫu lỗi RFC 7807, ma trận quyền | `API_AND_WORKER_PROTOCOL.md §1, §2, §11` |
| Worker protocol (claim → start → heartbeat → artifact → complete/fail) | `API_AND_WORKER_PROTOCOL.md §3–§7` — **không lặp ở đây** |
| Entity, cột, index, bất biến CSDL | `DATA_MODEL_PLAN.md` |
| Ràng buộc Vercel, error taxonomy gốc | `TARGET_ARCHITECTURE.md §3, §10` |
| **Endpoint User API, schema I/O, phân trang, filter, sort, screen contract** | **Tài liệu này** |

**Quy tắc dữ liệu:** mọi field trong tài liệu này phải truy được về một cột trong
`DATA_MODEL_PLAN.md`. Field dẫn xuất (aggregate/tính lúc đọc) được đánh dấu *derived*.
Field chưa có chỗ chứa được đánh dấu **[ASSUMPTION]** và liệt kê lại ở §14.

---

## 1. Quy ước chung

### 1.1 Versioning

| Chủ đề | Quy định |
|---|---|
| Prefix | `/api/v1/*` — version nằm trong URL, **không** trong header |
| Vì sao URL chứ không header | Cache/CDN/log/OpenAPI đọc được ngay; Python client sinh từ OpenAPI không phải cấu hình thêm; Vercel route file-based ánh xạ 1-1 `app/api/v1/**/route.ts` |
| Phá vỡ tương thích | Tạo `/api/v2`; `v1` giữ tối thiểu 90 ngày *(một người dùng ⇒ thực tế ngắn hơn được, nhưng CLI đã cài phải còn chạy)* **[ASSUMPTION]** |
| Thay đổi tương thích | Thêm field optional, thêm giá trị enum **chỉ ở field output**. Thêm giá trị enum ở **input** là breaking với client cũ ⇒ không tính là additive |
| Header phiên bản CLI | `X-Agent-Version` (đã có ở worker protocol) áp dụng luôn cho CLI-as-user; server không hỗ trợ ⇒ **426 Upgrade Required** |
| Deprecation | Header `Deprecation: true` + `Sunset: <http-date>` + `Link: <doc>; rel="deprecation"` |

### 1.2 Envelope — quyết định

| Loại response | Hình dạng | Lý do |
|---|---|---|
| **Collection** | **Có envelope**: `{ "data": [...], "page": {...}, "meta"?: {...} }` | Cần chỗ mang `next_cursor`, `has_more`, aggregate. Trả mảng trần thì không có chỗ đặt mà không phá vỡ tương thích |
| **Single resource** | **Không envelope** — trả thẳng object | Bớt một lớp bóc; type sinh từ Zod dùng lại được nguyên vẹn giữa list-item và detail |
| **Mutation** | Trả **entity sau khi ghi** (không envelope) + `201`/`200` | Client không phải GET lại |
| **Lỗi** | **RFC 7807** `application/problem+json` — xem §2 | Đồng nhất với worker protocol §1 |
| **202 Accepted** (enqueue job) | `{ "job_id": "...", "status": "QUEUED", "poll_url": "/api/v1/jobs/{id}" }` | Frontend biết chỗ poll ngay |

Mọi response đều có header `X-Request-Id`. Không đặt `request_id` vào body thành công
(chỉ có ở body lỗi) — tránh làm bẩn shape entity.

```ts
// packages/api-contract/src/envelope.ts
export const Page = z.object({
  next_cursor: z.string().nullable(),   // opaque, base64url
  has_more:    z.boolean(),
  limit:       z.number().int(),
  total:       z.number().int().nullable(), // null trừ khi ?with_total=1 (xem §1.3)
});
export const Collection = <T extends z.ZodTypeAny>(item: T) =>
  z.object({ data: z.array(item), page: Page, meta: z.record(z.unknown()).optional() });
```

### 1.3 Phân trang — **cursor-based, không offset**

**Quy định:** mọi endpoint collection dùng `?limit=&cursor=`. **Không có `?page=` / `?offset=`.**

Vì sao cursor chứ không offset — bốn lý do, theo thứ tự nghiêm trọng:

| # | Vấn đề của OFFSET | Hệ quả cụ thể trong hệ này |
|---|---|---|
| 1 | **Kết quả không ổn định khi có ghi đồng thời** | `score_run`, `audit_event`, `job_event`, `artifact` là **append-only** và worker ghi liên tục. Chèn 1 hàng ở đầu ⇒ trang 2 lặp lại hàng cuối trang 1; xoá/supersede ⇒ **bỏ sót hàng**. Với bảng audit, bỏ sót là lỗi *đúng nghĩa*, không phải phiền toái UI |
| 2 | **`OFFSET n` phải quét và loại bỏ n hàng** | `job_event` và `video_daily_metric` là bảng lớn nhất. `OFFSET 10000` = Postgres đọc 10.000 hàng rồi vứt. Chi phí tuyến tính theo độ sâu trang |
| 3 | **Ràng buộc Vercel + Neon khuếch đại chi phí** | Function có max duration và tính tiền theo thời gian chạy; Neon tính theo compute-time. Trang sâu biến truy vấn O(1) thành O(n) **ngay trên đường đi tốn tiền nhất** |
| 4 | **`COUNT(*)` để dựng số trang cũng quét toàn bảng** | Offset gần như luôn kéo theo nhu cầu tổng số trang ⇒ thêm một full scan nữa |

**Cursor keyset trên khoá đã có index:**

```
cursor = base64url(json({ k: [<sort_key_value>, <id>], s: "<sort_spec>", v: 1 }))
```
- Luôn **tie-break bằng `id`**. `id` là **UUIDv7** (`DATA_MODEL_PLAN §0`) ⇒ đơn điệu theo thời gian
  ⇒ `ORDER BY created_at DESC, id DESC` khớp đúng index có sẵn và không bao giờ hoà.
- `s` (sort spec) được nhúng trong cursor. Đổi `?sort=` giữa hai lần gọi mà giữ cursor cũ ⇒
  **400 `CURSOR_SORT_MISMATCH`** (không âm thầm trả rác).
- `v` là version cursor; đổi schema cursor ⇒ **400 `CURSOR_INVALID`**, client phân trang lại từ đầu.
- Cursor **không** được ký/mã hoá — nó chỉ chứa giá trị đã nằm trong dữ liệu người dùng có quyền đọc.
  Nhưng server **phải áp lại toàn bộ filter quyền** khi giải mã (cursor không mang quyền).

**`total`:** chỉ tính khi `?with_total=1`, chỉ cho phép ở các endpoint có filter bắt buộc thu hẹp
(`/content`, `/jobs`), và dùng `COUNT(*)` trong cùng filter. Endpoint bảng lớn
(`/jobs/{id}/events`, `/analytics/**`) **cấm** `with_total` ⇒ **400 `TOTAL_NOT_SUPPORTED`**.

**Ngoại lệ duy nhất — cửa sổ thời gian thay cho cursor:** `/api/v1/calendar` và `/api/v1/analytics/**`
dùng `from`/`to` bắt buộc + giới hạn độ rộng cửa sổ (§13). Đây không phải phân trang mà là
**bounded window query**; vẫn hỗ trợ `cursor` khi số hàng trong cửa sổ vượt `limit`.

### 1.4 Sorting

| Quy định | Chi tiết |
|---|---|
| Cú pháp | `?sort=-created_at` (`-` = DESC). **Một khoá duy nhất**; tie-break `id` do server thêm |
| Allowlist | Mỗi endpoint khai báo tập `sortable` cố định trong Zod. Ngoài allowlist ⇒ **400 `SORT_FIELD_NOT_ALLOWED`** |
| Điều kiện vào allowlist | Field **phải có index** phù hợp trong `DATA_MODEL_PLAN`. Không có index ⇒ không cho sort. Không tồn tại "sort tuỳ ý" |
| Nhiều khoá | **Không hỗ trợ ở v1.** Đa khoá đòi index tổ hợp mà schema chưa có ⇒ mở ra là mở đường cho seq scan |

### 1.5 Filtering

| Quy định | Chi tiết |
|---|---|
| Cú pháp bằng | `?status=FROZEN` |
| OR trong cùng field | Lặp field: `?status=QUEUED&status=RUNNING` ⇒ `IN (...)`. Tối đa **20 giá trị**/field |
| AND giữa các field | Mặc định |
| Toán tử khoảng | Ngoặc vuông: `?planned_date[gte]=2026-07-01&planned_date[lt]=2026-08-01`. Toán tử: `gte, gt, lte, lt` |
| Null | `?series_id=null` (chuỗi literal `null`) ⇒ `IS NULL` |
| Tìm kiếm text | `?q=` — chỉ ở `/content` (trên `topic`, `angle`) và `/sources`. `ILIKE '%…%'` với **min 2 ký tự**, max 100. Không full-text search ở v1 **[ASSUMPTION]** |
| **Không có** | RSQL/OData/JSONPath/filter tuỳ ý trên `jsonb`. Lý do: (a) mọi filter phải ánh xạ được vào index đã khai báo; (b) ngôn ngữ filter tuỳ ý là bề mặt tấn công (DoS bằng truy vấn không index) và rất khó sinh OpenAPI đúng |
| Filter trên `jsonb` | **Cấm ở v1.** Cần filter ⇒ nâng lên cột quan hệ (`DATA_MODEL_PLAN §0` quy tắc chọn cột) |
| Field không trong allowlist | **400 `FILTER_FIELD_NOT_ALLOWED`** — *không* im lặng bỏ qua (im lặng bỏ qua khiến client tưởng đã lọc, hiển thị dữ liệu ngoài phạm vi) |
| Scope kênh | `channel_id` **luôn** bị giao với tập kênh user có quyền, kể cả khi client không gửi. Xin kênh ngoài quyền ⇒ **404** (`TARGET_ARCHITECTURE.md §6`) |

### 1.6 Sparse fieldsets & projection — **bắt buộc, không phải tối ưu**

Đây là cơ chế then chốt vì `content_revision` chứa cột nặng: `audio_script` (đo được **67,8 KB**),
`seo_package` jsonb (**194,8 KB**) — `DATA_MODEL_PLAN §0`.

| Cơ chế | Cú pháp | Ngữ nghĩa |
|---|---|---|
| **Projection mặc định theo endpoint** | — | List endpoint trả **summary projection**, đã loại sẵn mọi cột nặng. Không có cách nào để list trả full body |
| **Sparse fieldsets** | `?fields=id,status,hook,revision_no` | Chỉ ở **single-resource** endpoint. Allowlist theo resource; field ngoài allowlist ⇒ **400 `FIELD_NOT_ALLOWED`** |
| **Include quan hệ** | `?include=dimensions,findings` | Allowlist cố định, **tối đa 3 include**/request, **không lồng nhau** (`a.b` bị từ chối) — chặn N+1 và bùng nổ payload |
| **Cột nặng phải xin rõ ràng** | `?fields=audio_script` hoặc endpoint con riêng | `audio_script`, `seo_package`, `visual_prompts`, `semantic_beats`, `thumbnail_concepts`, `extracted_text`, `findings`, `recommendations` **không bao giờ** nằm trong projection mặc định của list |

```ts
export const HeavyFields = ['audio_script','outline','description','research_summary',
  'seo_package','semantic_beats','visual_prompts','thumbnail_concepts','chapters'] as const;
```

### 1.7 Idempotency

| Quy định | Chi tiết |
|---|---|
| Header | `Idempotency-Key: <uuid v4/v7>` — **bắt buộc** với mọi POST đổi trạng thái (đồng nhất worker protocol §1) |
| Không bắt buộc với | `GET`, `HEAD`, và `PATCH` field metadata thuần (PATCH đã idempotent theo bản chất *nếu* body là tập giá trị tuyệt đối — mọi PATCH ở đây đều vậy) |
| Cơ chế | Lưu `(principal_id, endpoint, key) → (request_body_sha256, http_status, response_body)` TTL **24h** |
| Replay đúng | Cùng key + cùng `request_body_sha256` ⇒ trả **nguyên response cũ**, không tác dụng phụ |
| Replay sai | Cùng key + body khác ⇒ **409 `IDEMPOTENCY_KEY_REUSED`** |
| Đang xử lý | Key đã nhận nhưng chưa xong ⇒ **409 `IDEMPOTENCY_IN_PROGRESS`** + `Retry-After: 1` |
| Thiếu header | **400 `IDEMPOTENCY_KEY_REQUIRED`** |
| Bảng lưu | **`idempotency_record`** — đã có trong `DATA_MODEL_PLAN §1.5`: `(scope, idempotency_key, principal_kind, principal_id, request_hash, response_snapshot, http_status, entity_type, entity_id, created_at, expires_at)`, **unique `(scope, idempotency_key, principal_id)`**, retention **30 ngày**. ✅ Khoảng trống này **đã được lấp**, không còn là assumption |

### 1.8 Concurrency control (ghi đè mất bản)

| Quy định | Chi tiết |
|---|---|
| PATCH tài nguyên có thể sửa | Yêu cầu `If-Match: "<etag>"`; ETag = `W/"<updated_at epoch_ms>-<id ngắn>"` |
| Thiếu `If-Match` | **428 `PRECONDITION_REQUIRED`** với `content_item`, `content_revision` (DRAFT), `channel` |
| Không khớp | **412 `PRECONDITION_FAILED`** |
| Vì sao cần | Revision `DRAFT` có thể bị **cả người dùng lẫn agent** (`POST /api/worker/revisions`) đụng vào. Không có optimistic lock ⇒ mất bản sửa lặng lẽ |
| GET | Trả `ETag`; hỗ trợ `If-None-Match` ⇒ **304** (dùng cho polling — §11) |

### 1.9 Ghi chú chuẩn hoá khác

| Chủ đề | Quy định |
|---|---|
| Thời gian | ISO-8601 UTC có `Z`. Field `*_date` là `date` thuần `YYYY-MM-DD` (calendar/analytics) — **không** timestamp, để tránh lệch múi giờ khi hiển thị lịch |
| Múi giờ | Server luôn UTC. `channel.timezone` được trả kèm để client tự quy đổi. Server **không** render theo timezone người dùng |
| Tỉ lệ | Số nguyên **basis-point** (0–10000), tên field kết thúc `_bp` (`DATA_MODEL_PLAN §0`). Client tự chia 100. Không trả float |
| ID | Chuỗi UUIDv7. Client coi là **opaque** |
| Enum | `SCREAMING_SNAKE`, khớp đúng `CHECK` trong DB |
| `null` vs vắng mặt | `null` = biết là rỗng; vắng mặt = không được chọn trong projection. **Hai thứ khác nhau**, client phải phân biệt |
| Soft delete | Bản ghi có `deleted_at` **không** xuất hiện trong list; GET trực tiếp ⇒ **404** (`ADMIN` có `?include_deleted=1`) |
| Charset | UTF-8. Nội dung tiếng Việt có dấu ⇒ mọi giới hạn độ dài tính bằng **ký tự Unicode** cho validation, bằng **byte** cho giới hạn payload |

---

## 2. Error taxonomy đầy đủ

Mọi lỗi theo **RFC 7807** `application/problem+json`, đúng mẫu ở `API_AND_WORKER_PROTOCOL.md §1`:
`{ type, title, status, code, detail, request_id, errors? }`.
`code` là **hợp đồng ổn định**; `title`/`detail` là văn bản người đọc, **client không được parse**.

### 2.1 Bảng mã lỗi

Cột **Retry**: `NO` = lặp lại y hệt sẽ lại lỗi · `SAFE` = client được retry với backoff ·
`AFTER-FIX` = sửa request rồi mới retry · `IDEMP` = retry được **chỉ khi** giữ nguyên `Idempotency-Key`.

| Lớp | `code` | HTTP | Retry | Ghi chú |
|---|---|:-:|:-:|---|
| **Validation** | `VALIDATION_FAILED` | 422 | AFTER-FIX | `errors[]: {path, code, message}` từ Zod |
| | `UNKNOWN_FIELD` | 422 | AFTER-FIX | Zod `.strict()` — chống payload injection |
| | `FILTER_FIELD_NOT_ALLOWED` | 400 | AFTER-FIX | §1.5 |
| | `SORT_FIELD_NOT_ALLOWED` | 400 | AFTER-FIX | §1.4 |
| | `FIELD_NOT_ALLOWED` | 400 | AFTER-FIX | `?fields=` ngoài allowlist |
| | `INCLUDE_NOT_ALLOWED` | 400 | AFTER-FIX | `?include=` ngoài allowlist / lồng nhau |
| | `CURSOR_INVALID` | 400 | AFTER-FIX | Cursor hỏng/sai version |
| | `CURSOR_SORT_MISMATCH` | 400 | AFTER-FIX | Đổi `sort` giữa chừng |
| | `RANGE_TOO_WIDE` | 400 | AFTER-FIX | `to - from` vượt trần (§13) |
| | `TOTAL_NOT_SUPPORTED` | 400 | AFTER-FIX | `with_total` ở endpoint bảng lớn |
| | `PAYLOAD_TOO_LARGE` | 413 | AFTER-FIX | Vượt trần endpoint (§13); Vercel trả `FUNCTION_PAYLOAD_TOO_LARGE` ở 4,5 MB |
| **Auth** | `UNAUTHENTICATED` | 401 | NO | Thiếu/hết hạn session, PAT |
| | `TOKEN_EXPIRED` | 401 | NO | `WWW-Authenticate` kèm lý do |
| | `FORBIDDEN` | 403 | NO | Có quyền kênh nhưng **sai vai trò** |
| | `NOT_FOUND` | 404 | NO | Không tồn tại **hoặc** ngoài phạm vi kênh — cố tình gộp (`TARGET_ARCHITECTURE §6`) |
| | `SCOPE_INSUFFICIENT` | 403 | NO | PAT thiếu scope (`api_token.scopes`) |
| | `WORKER_TOKEN_ON_USER_API` | 403 | NO | `hub_wt_…` gọi `/api/v1/*` — tách bạch bắt buộc |
| **Import** | `IMPORT_RECORD_CONFLICT` | 409 | AFTER-FIX | Cùng `legacy_ref` nhưng `legacy_sha256` khác — nội dung đã đổi giữa hai lần nạp |
| | `IMPORT_BATCH_STATE_INVALID` | 409 | AFTER-FIX | Thao tác không hợp lệ với trạng thái lô hiện tại |
| **Promote** | `CONCURRENT_PROMOTION` | 409 | AFTER-FIX | `expected_production_revision_id` không khớp `production_revision_id` đã khoá. Client phải **đọc lại** trạng thái rồi quyết định lại — **không** retry mù |
| | `APPROVAL_NOT_ACTIVE` | 409 | AFTER-FIX | Approval của revision đích không còn `ACTIVE` tại thời điểm khoá |
| | `ALREADY_PRODUCTION` | 409 | NO | `:rid` **đã là** `production_revision_id` — promote chính nó sẽ sinh event `A→A` và supersede nhầm chính approval đang dùng |
| | `STEP_UP_REQUIRED` | 403 | AFTER-FIX | Tự-duyệt cần xác nhận nâng cao (§6.7) |
| **Xung đột** | `REVISION_FROZEN` | 409 | NO | Sửa hàng `FROZEN` (bất biến B-R1) |
| | `REVISION_NOT_FROZEN` | 409 | NO | Freeze/approve/build trên revision chưa freeze (J-3) |
| | `INVALID_STATE_TRANSITION` | 409 | NO | Sai state machine `§8.1/§8.2` |
| | `DUPLICATE_JOB` | 409 | NO | Trúng partial unique `(revision, job_type) WHERE LIVE_STATUSES` |
| | `APPROVAL_EXISTS` | 409 | NO | Đã có approval `ACTIVE` cho `(revision, gate)` |
| | `APPROVAL_REVOKED` | 409 | NO | Approval bị thu hồi giữa chừng |
| | `APPROVAL_REQUIRED` | 409 | AFTER-FIX | Tạo build job khi chưa có approval `ACTIVE` |
| | `SELF_APPROVAL_FORBIDDEN` | 409 | NO | `channel.approval_policy = TWO_PERSON_REQUIRED` |
| | `SNAPSHOT_MISMATCH` | 409 | NO | `input_snapshot_hash ≠ content_revision.content_sha256` (bất biến S-2) |
| | `IDEMPOTENCY_KEY_REUSED` | 409 | NO | Cùng key, khác body |
| | `IDEMPOTENCY_IN_PROGRESS` | 409 | SAFE | + `Retry-After: 1` |
| | `PRECONDITION_REQUIRED` | 428 | AFTER-FIX | Thiếu `If-Match` |
| | `PRECONDITION_FAILED` | 412 | AFTER-FIX | ETag lệch ⇒ đọc lại rồi ghi lại |
| | `UNIQUE_VIOLATION` | 409 | NO | Vi phạm unique khác (vd `channel.label`) |
| | `JOB_NOT_CANCELLABLE` | 409 | NO | Job đã `DONE/FAILED/CANCELLED` |
| **Gate nghiệp vụ** | `CONTENT_GATE_NOT_MET` | 409 | NO | Chưa `READY_FOR_TTS_HANDOFF` + `qa_status ∈ {PASS, PASS_WITH_ADVISORIES}` (`TARGET_ARCHITECTURE §8.1`, fail-closed) |
| | `CLAIM_CONFLICT_UNRESOLVED` | 409 | NO | Claim có cả `SUPPORTS` lẫn `CONTRADICTS` ⇒ chặn gate Research Ready |
| | `ARTIFACT_NOT_PROMOTED` | 409 | NO | Dùng artifact chưa `PROMOTED` |
| **Quota ngoài** | `YOUTUBE_DAILY_QUOTA_EXCEEDED` | 409 | NO | Job → `DEFERRED`. **Không gộp** với rate limit |
| | `YOUTUBE_RATE_LIMITED` | 429 | SAFE | Backoff + jitter |
| **Rate limit** | `RATE_LIMITED` | 429 | SAFE | + `Retry-After`, `X-RateLimit-*` |
| **Hạ tầng** | `DB_UNAVAILABLE` | 503 | SAFE/IDEMP | Neon không sẵn sàng; retry có jitter |
| | `FUNCTION_TIMEOUT` | 504 | IDEMP | Vercel cắt; **phải** giữ `Idempotency-Key` khi retry vì ghi có thể đã xảy ra |
| | `INTERNAL_ERROR` | 500 | SAFE | Không lộ chi tiết; đối chiếu bằng `request_id` |
| | `NOT_IMPLEMENTED` | 501 | NO | Endpoint đã đặt chỗ, chưa bật ở MVP (vd `/uploads` — §6.15) |
| | `UPGRADE_REQUIRED` | 426 | AFTER-FIX | `X-Agent-Version` quá cũ; body có `min_supported_agent_version` |

### 2.2 Ánh xạ về `TARGET_ARCHITECTURE §10`

| §10 nói | Ở đây |
|---|---|
| Validation `VALIDATION_FAILED` (422) | Giữ nguyên + 4 mã 400 cho **lỗi tham số truy vấn** (khác với lỗi body) |
| `UNAUTHENTICATED`/`FORBIDDEN`/`NOT_FOUND` | Giữ nguyên; thêm `SCOPE_INSUFFICIENT`, `WORKER_TOKEN_ON_USER_API` |
| `LEASE_EXPIRED`, `REVISION_FROZEN`, `DUPLICATE_JOB`, `APPROVAL_REVOKED` (409) | `LEASE_EXPIRED` **chỉ thuộc Worker API** — không xuất hiện ở `/api/v1/*` |
| Quota YouTube tách bạch | Giữ nguyên, không gộp |
| `DB_UNAVAILABLE` (503), `FUNCTION_TIMEOUT` (504) | Giữ nguyên |

**Bất biến lỗi:** không có mã nào vừa 4xx vừa 5xx tuỳ ngữ cảnh; không dùng 200 kèm `{error}`.
Test hợp đồng khẳng định **mọi** `code` trong bảng này có đúng một `status`.

---

## 3. Auth & authorization áp dụng cho User API

Cơ chế principal đã định nghĩa ở `TARGET_ARCHITECTURE §6` và `API_AND_WORKER_PROTOCOL §1`.
Ở đây chỉ nói phần **áp dụng cho `/api/v1/*`**:

| Chủ đề | Quy định |
|---|---|
| Nhận diện | Cookie session (`HttpOnly/Secure/SameSite=Strict`) **hoặc** `Authorization: Bearer hub_pat_…` |
| `hub_wt_…` (worker token) | **Luôn 403 `WORKER_TOKEN_ON_USER_API`** trên mọi route `/api/v1/*`, kiểm **trước** mọi logic khác |
| Vai trò | `ADMIN`, `EDITOR`, `REVIEWER`, `APPROVER`, `READONLY` — **scope theo kênh** qua `user_channel_role` |
| Ma trận hành động ↔ vai trò | `API_AND_WORKER_PROTOCOL.md §11` — **nguồn chuẩn, không lặp lại**. Cột "Role" ở §6 là ánh xạ endpoint vào ma trận đó |
| Tài nguyên **không thuộc kênh** | `worker_machine`, `worker_token`, `algorithm`, `algorithm_version`, `import_batch` ⇒ **`ADMIN` toàn cục** |
| Suy ra kênh | Mọi tài nguyên con suy `channel_id` qua `content_item.channel_id`; `artifact`/`score_run`/`audit_run`/`approval` suy qua `content_revision → content_item` |
| Ngoài phạm vi | **404**, không phải 403 (không lộ tồn tại) |
| PAT scope | `api_token.scopes` giao với vai trò: quyền hiệu lực = `min(role, scopes)`. Thiếu scope ⇒ 403 `SCOPE_INSUFFICIENT` |
| Step-up | Tự-duyệt (`SELF_APPROVAL_ALLOWED`) bắt buộc nhập lại mật khẩu ⇒ `reauth_token` hiệu lực **5 phút** **[ASSUMPTION]**; ghi `audit_event.self_approved=true` |

### 3.1 Endpoint auth (không thuộc 17 nhóm nhưng frontend cần)

| Endpoint | Method | Caller | Idem | Audit | Ghi chú |
|---|---|---|:-:|:-:|---|
| `/api/v1/auth/login` | POST | frontend | — | ✅ | `{email, password}` → set cookie; xoay `session.id`; rate limit **5/15 phút/IP+email** |
| `/api/v1/auth/logout` | POST | frontend | — | ✅ | Revoke session hiện tại |
| `/api/v1/auth/me` | GET | frontend, CLI | — | — | `{user, channels:[{channel_id,label,role}], must_change_password}` — **màn hình nào cũng cần đầu tiên** |
| `/api/v1/auth/reauth` | POST | frontend | — | ✅ | `{password}` → `{reauth_token, expires_at}` cho step-up |
| `/api/v1/auth/password` | PUT | frontend | ✅ | ✅ | Đổi mật khẩu ⇒ revoke **mọi** session khác |
| `/api/v1/auth/tokens` | GET/POST/DELETE | frontend | ✅ | ✅ | Quản lý PAT; giá trị token hiển thị **một lần** |

---

## 4. Ký hiệu dùng ở §6

Mỗi nhóm gồm: (a) **bảng endpoint** — Method · Caller · Auth · Role · Idem · Audit; (b) **schema Zod**;
(c) **bảng truy vấn** — Pagination · Filter · Sort; (d) **validation & error**; (e) **rate limit**.

| Ký hiệu | Nghĩa |
|---|---|
| **Caller** | `FE` = frontend tương lai · `CLI` = Local CLI (PAT, hành động với tư cách user) · `BOTH` · `ALGO` = thuật toán nội bộ chạy trong server route |
| **Auth** | `SESSION\|PAT` (mặc định toàn bộ User API) |
| **Role** | Vai trò tối thiểu **trên kênh của tài nguyên**; `ADMIN*` = ADMIN toàn cục |
| **Idem** | `Idempotency-Key` bắt buộc |
| **Audit** | Ghi `audit_event` (append-only, `DATA_MODEL_PLAN §1`) |
| **RL** | Rate limit — `<số>/<cửa sổ>` mỗi principal |

**Mặc định toàn cục (không lặp ở từng dòng):** Auth = `SESSION|PAT`; body Zod `.strict()`;
`limit` mặc định/tối đa theo §13; đọc = `READONLY`; mọi ghi có Audit; mọi 404 áp dụng quy tắc scope kênh.
Chỉ ghi ra khi **khác** mặc định.

**Rate limit — nền tảng.** Vercel serverless không có bộ nhớ chung giữa các invocation ⇒
counter phải nằm ở **Neon** (bảng `rate_limit_bucket`, token bucket, `INSERT … ON CONFLICT DO UPDATE`)
hoặc đẩy lên **Vercel Firewall/WAF rate limit** ở tầng edge. **[ASSUMPTION → §14 A-2]**
Ngưỡng mặc định: **đọc 600/phút**, **ghi 120/phút**, **enqueue job 30/phút** mỗi principal.
Header trả về: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`.

---

## 5. Schema dùng chung

```ts
// packages/api-contract/src/common.ts
export const Uuid   = z.string().uuid();
export const Bp     = z.number().int().min(0).max(10000);      // basis-point
export const Ts     = z.string().datetime({ offset: false });   // ISO-8601 UTC 'Z'
export const DateOnly = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
export const Sha256 = z.string().regex(/^[0-9a-f]{64}$/);

export const ListQuery = z.object({
  limit:      z.coerce.number().int().min(1).max(100).default(25),
  cursor:     z.string().max(512).optional(),
  sort:       z.string().max(64).optional(),
  with_total: z.coerce.boolean().default(false),
}).strict();

export const Problem = z.object({      // RFC 7807
  type: z.string().url(), title: z.string(), status: z.number().int(),
  code: z.string(), detail: z.string(), request_id: z.string(),
  errors: z.array(z.object({ path: z.string(), code: z.string(), message: z.string() })).optional(),
});

export const ActorRef = z.object({     // hiển thị "ai làm"
  kind: z.enum(['USER','WORKER','CRON','SYSTEM']),
  id: Uuid.nullable(), label: z.string().nullable(),   // derived: user.display_name | worker_machine.name
});

export const ContentStatus = z.enum([  // TARGET_ARCHITECTURE §8.1 — tầng sản xuất
  'PLANNED','FROZEN','BUILDING','BUILT','PUBLISH_READY','SCHEDULED','PUBLISHED','ANALYZING',
  'BUILD_FAILED','NEEDS_REVISION','ARCHIVED']);
export const RevisionStatus = z.enum(['DRAFT','REVIEW_REQUIRED','FROZEN']);
// ⚠️ KHÔNG có 'SUPERSEDED': hàng FROZEN bất biến tuyệt đối. Supersession là dữ liệu SUY RA:
//    is_production  = (content_item.production_revision_id === revision.id)
//    is_superseded  = revision.status==='FROZEN' && !is_production && đã từng là production
//                     (tra `revision_promotion_event`)
export const Gate = z.enum(['RESEARCH_READY','CONTENT_READY','PRODUCTION_READY','PUBLISH_READY']);
export const JobType = z.enum([        // TARGET_ARCHITECTURE §9 — allowlist ĐÓNG
  'ANALYZE_CONTENT','SCORE_CONTENT','IMPROVE_CONTENT',
  'BUILD_AUDIO','BUILD_VIDEO','BUILD_SUBTITLE','BUILD_THUMBNAIL',
  'SYNC_ANALYTICS','EXPORT_PACKAGE']);
export const JobStatus = z.enum(['QUEUED','DEFERRED','LEASED','RUNNING','DONE','FAILED','CANCELLED','EXPIRED']);
export const LIVE_STATUSES = ['QUEUED','DEFERRED','LEASED','RUNNING'] as const; // dùng chung, §J-4
export const Dimension = z.enum([      // DATA_MODEL_PLAN §5
  'SOURCE_QUALITY','FACTUAL_CONFIDENCE','RELEVANCE','ORIGINALITY','DUPLICATE_RISK',
  'HOOK_QUALITY','STRUCTURE_QUALITY','AUDIO_SUITABILITY','SEO_QUALITY','CHANNEL_FIT',
  'AUDIENCE_FIT','FORMAT_FIT','RETENTION_POTENTIAL','CTR_POTENTIAL','PRODUCTION_READINESS',
  'POLICY_RISK','FACTUAL_RISK']);
```

---

## 6. Đặc tả endpoint theo nhóm

### 6.1 `/api/v1/channels`

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/channels` | GET | BOTH | READONLY | — | — | 600/p |
| `/channels` | POST | FE | `ADMIN*` | ✅ | ✅ | 30/p |
| `/channels/{id}` | GET | BOTH | READONLY | — | — | 600/p |
| `/channels/{id}` | PATCH | FE | ADMIN | ✅ | ✅ | 120/p |
| `/channels/{id}` | DELETE | FE | `ADMIN*` | ✅ | ✅ | 30/p |
| `/channels/{id}/stats` | GET | FE | READONLY | — | — | 300/p |
| `/channels/{id}/credentials` | GET | BOTH | ADMIN | — | — | 120/p |
| `/channels/{id}/members` | GET/PUT/DELETE | FE | ADMIN | ✅ (ghi) | ✅ (ghi) | 120/p |

```ts
export const Channel = z.object({
  id: Uuid, label: z.string(), youtube_channel_id: z.string().nullable(), title: z.string(),
  domain_id: z.enum(['BUD','FS','CL']), default_voice: z.string().nullable(),
  timezone: z.string(), approval_policy: z.enum(['SELF_APPROVAL_ALLOWED','TWO_PERSON_REQUIRED']),
  is_active: z.boolean(), created_at: Ts, updated_at: Ts,
  my_role: z.enum(['ADMIN','EDITOR','REVIEWER','APPROVER','READONLY']),  // derived
});
export const ChannelCreate = z.object({
  label: z.string().regex(/^[a-z0-9_]{2,64}$/), title: z.string().min(1).max(200),
  domain_id: z.enum(['BUD','FS','CL']), youtube_channel_id: z.string().max(64).optional(),
  default_voice: z.string().max(64).optional(), timezone: z.string().default('Asia/Ho_Chi_Minh'),
  approval_policy: z.enum(['SELF_APPROVAL_ALLOWED','TWO_PERSON_REQUIRED']).default('SELF_APPROVAL_ALLOWED'),
}).strict();
export const ChannelPatch = ChannelCreate.partial().omit({ label: true });  // label bất biến
export const ChannelStats = z.object({          // TẤT CẢ derived — không có bảng riêng
  channel_id: Uuid,
  content_by_status: z.record(ContentStatus, z.number().int()),
  content_by_format: z.object({ LONG: z.number().int(), SHORT: z.number().int() }),
  jobs_live: z.record(JobStatus, z.number().int()),
  planned_next_7d: z.number().int(), overdue_planned: z.number().int(),
  pending_approval: z.number().int(), build_failed_24h: z.number().int(),
  last_analytics_sync_at: Ts.nullable(), computed_at: Ts,
});
export const ChannelCredentialRef = z.object({  // KHÔNG có giá trị secret
  worker_machine_id: Uuid, worker_name: z.string(), credential_path: z.string(),
  scopes: z.array(z.string()), status: z.enum(['OK','EXPIRED','REVOKED','UNKNOWN']),
  last_verified_at: Ts.nullable(), last_error_code: z.string().nullable(),
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | Cursor; `limit` 25/100 (thực tế < 10 kênh) |
| Filter | `is_active`, `domain_id`, `q` (label/title) |
| Sort | `label` (mặc định), `-created_at` |
| Validation | `label` unique + bất biến sau khi tạo (khớp `.youtube_channels/{label}.json`); `youtube_channel_id` unique; DELETE = soft delete, **từ chối 409** nếu còn job `LIVE_STATUSES` |
| Lỗi riêng | `UNIQUE_VIOLATION` (label/youtube_channel_id), `PRECONDITION_REQUIRED/FAILED` (PATCH) |

⚠️ `channel` **không** chứa `client_secret`/`refresh_token`; `/credentials` chỉ trả *tham chiếu + trạng thái*.
Trạng thái này do worker cập nhật qua Worker API — xem `API_AND_WORKER_PROTOCOL.md §3`.

---

### 6.2 `/api/v1/videos`

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/videos` | GET | BOTH | READONLY | — | — | 600/p |
| `/videos/{id}` | GET | BOTH | READONLY | — | — | 600/p |
| `/videos/{id}/link` | POST | FE | EDITOR | ✅ | ✅ | 120/p |
| `/videos/{id}/link` | DELETE | FE | EDITOR | ✅ | ✅ | 120/p |
| `/videos/{id}/metrics` | GET | FE | READONLY | — | — | 300/p |

```ts
export const Video = z.object({
  id: Uuid, channel_id: Uuid, youtube_video_id: z.string(), title: z.string(),
  published_at: Ts.nullable(), duration_seconds: z.number().int().nullable(),
  is_short: z.boolean(), privacy_status: z.string(),
  content_item_id: Uuid.nullable(), first_seen_at: Ts, last_synced_at: Ts.nullable(),
  // derived, chỉ khi ?include=latest_metrics
  latest_metrics: z.object({ metric_date: DateOnly, views: z.number().int(),
    impression_ctr_bp: Bp.nullable(), average_view_percentage_bp: Bp.nullable() }).nullish(),
});
export const VideoLink = z.object({ content_item_id: Uuid }).strict();
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | Cursor keyset `(published_at, id)`; 25/100 |
| Filter | `channel_id`, `is_short`, `privacy_status`, `content_item_id` (kể cả `=null` → video chưa gắn nội dung), `published_at[gte\|lt]`, `q` (title) |
| Sort | `-published_at` (mặc định), `-first_seen_at`, `title` |
| Include | `latest_metrics` (1 hàng/video, LATERAL join — **không** N+1) |
| Validation | `link`: `content_item.channel_id` phải **trùng** `video.channel_id`; `content_item.published_video_id` phải đang `null` hoặc trỏ chính video này |
| Lỗi riêng | `UNIQUE_VIOLATION` (video đã gắn item khác), `NOT_FOUND` (khác kênh) |
| Ghi chú | `description` **không** nằm trong projection mặc định (`?fields=description` ở single resource) |

`/videos/{id}/metrics` là **alias thu hẹp** của `/analytics/videos/{id}/daily` (§6.11) — cùng shape,
cùng giới hạn cửa sổ. Giữ alias để màn hình Video detail không phải ghép hai nhóm.

---

### 6.3 `/api/v1/content`

Nhóm nặng nhất. `content_item` đại diện **mọi** dạng: Long, Short, tập trong series, ý tưởng chưa
sản xuất, nội dung đã publish, Short tách từ Long (`DATA_MODEL_PLAN §3`).

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/content` | GET | BOTH | READONLY | — | — | 600/p |
| `/content` | POST | BOTH | EDITOR | ✅ | ✅ | 120/p |
| `/content/{id}` | GET | BOTH | READONLY | — | — | 600/p |
| `/content/{id}` | PATCH | FE | EDITOR | — (If-Match) | ✅ | 120/p |
| `/content/{id}` | DELETE | FE | `ADMIN*` | ✅ | ✅ | 30/p |
| `/content/{id}/transition` | POST | BOTH | EDITOR¹ | ✅ | ✅ | 120/p |
| `/content/{id}/timeline` | GET | FE | READONLY | — | — | 300/p |
| `/content/{id}/derivations` | GET | FE | READONLY | — | — | 300/p |

¹ Chuyển sang `PUBLISH_READY`/`SCHEDULED` yêu cầu `APPROVER`; `ARCHIVED` yêu cầu `ADMIN`.

```ts
export const ContentSummary = z.object({     // projection MẶC ĐỊNH của list — không cột nặng
  id: Uuid, channel_id: Uuid, format: z.enum(['LONG','SHORT']),
  topic: z.string(), angle: z.string().nullable(), status: ContentStatus,
  planned_date: DateOnly.nullable(), publish_date: Ts.nullable(), priority: z.number().int(),
  series_id: Uuid.nullable(), content_pillar_id: Uuid.nullable(),
  origin: z.enum(['CONTENT_REPO','HUB_IDEA','SHORT_GENERATOR','IMPORT']),
  derivation_kind: z.enum(['ORIGINAL','LONG_TO_SHORT','SHORT_TO_LONG','REUSE']).nullable(),
  parent_content_item_id: Uuid.nullable(),
  approved_revision_id: Uuid.nullable(), production_revision_id: Uuid.nullable(),
  published_video_id: Uuid.nullable(), source_package_id: z.string().nullable(),
  created_at: Ts, updated_at: Ts,
  // derived — tính bằng LATERAL, không N+1:
  revision_count: z.number().int(), latest_revision_no: z.number().int().nullable(),
  latest_overall_score_bp: Bp.nullable(),           // score_run mới nhất của production/approved revision
  latest_audit_status: z.enum(['RUNNING','PASS','PASS_WITH_ADVISORIES','FAIL','BLOCKED','ERROR']).nullable(),
  has_active_approval: z.boolean(), live_job_count: z.number().int(),
});
export const ContentDetail = ContentSummary.extend({
  objective: z.string().nullable(), target_audience: z.string().nullable(),
  created_by: Uuid.nullable(), deleted_at: Ts.nullable(),
  // chỉ khi ?include=…  (tối đa 3)
  production_revision: RevisionSummary.nullish(),
  approved_revision:  RevisionSummary.nullish(),
  active_approval:    ApprovalOut.nullish(),
  latest_score:       ScoreRunSummary.nullish(),
  latest_audit:       AuditRunSummary.nullish(),
});
export const ContentCreate = z.object({
  channel_id: Uuid, format: z.enum(['LONG','SHORT']),
  topic: z.string().min(3).max(300), angle: z.string().max(500).optional(),
  objective: z.string().max(1000).optional(), target_audience: z.string().max(500).optional(),
  planned_date: DateOnly.optional(), priority: z.number().int().min(0).max(100).default(50),
  series_id: Uuid.optional(), content_pillar_id: Uuid.optional(),
  parent_content_item_id: Uuid.optional(),
  derivation_kind: z.enum(['ORIGINAL','LONG_TO_SHORT','SHORT_TO_LONG','REUSE']).default('ORIGINAL'),
  origin: z.enum(['HUB_IDEA','CONTENT_REPO','SHORT_GENERATOR','IMPORT']).default('HUB_IDEA'),
  source_package_id: z.string().max(200).optional(),
}).strict();
export const ContentPatch = ContentCreate
  .pick({ topic:true, angle:true, objective:true, target_audience:true,
          planned_date:true, priority:true, series_id:true, content_pillar_id:true }).partial();
export const ContentTransition = z.object({
  to: ContentStatus, reason: z.string().max(500).optional(),
  expected_status: ContentStatus,          // optimistic — chặn double-click / race
}).strict();
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | Cursor keyset; mặc định `(created_at DESC, id DESC)` — khớp index `(channel_id, status)` + PK |
| Filter | `channel_id[]`, `status[]`, `format`, `series_id` (`=null` được), `content_pillar_id`, `origin`, `derivation_kind`, `parent_content_item_id`, `planned_date[gte\|lt]`, `publish_date[gte\|lt]`, `has_active_approval`, `has_production_revision`, `published_video_id=null`, `q` (topic/angle) |
| Sort | `-created_at` (mặc định), `planned_date`, `-priority`, `-publish_date` |
| Include | `production_revision`, `approved_revision`, `active_approval`, `latest_score`, `latest_audit` |
| `with_total` | ✅ được phép (luôn có filter `channel_id` từ scope) |
| Validation | `parent_content_item_id` phải **cùng kênh**; `derivation_kind ≠ ORIGINAL` ⇒ bắt buộc có parent; `source_package_id` unique (partial); PATCH **không** sửa được `status`, `channel_id`, `format`, `approved_revision_id`, `production_revision_id`, `published_video_id` — chúng chỉ đổi qua endpoint chuyên biệt |
| Transition | Kiểm state machine `TARGET_ARCHITECTURE §8.1`; sai ⇒ 409 `INVALID_STATE_TRANSITION`; `expected_status` lệch ⇒ 409 `PRECONDITION_FAILED`. Sang `FROZEN` đòi có revision `FROZEN`; sang `PUBLISH_READY` đòi approval `ACTIVE` + artifact `PROMOTED` |
| Gate | Nhận package từ Content-Creator chỉ khi `content_status = READY_FOR_TTS_HANDOFF` **và** `qa_status ∈ {PASS, PASS_WITH_ADVISORIES}` ⇒ vi phạm ⇒ 409 `CONTENT_GATE_NOT_MET` (fail-closed) |
| Lỗi riêng | `INVALID_STATE_TRANSITION`, `CONTENT_GATE_NOT_MET`, `APPROVAL_REQUIRED`, `PRECONDITION_REQUIRED/FAILED`, `UNIQUE_VIOLATION` |

**`/content/{id}/timeline`** *(derived)* — hợp nhất dòng thời gian từ `audit_event` lọc theo
`entity_type ∈ {content_item, content_revision, approval, build_job, score_run, audit_run}` và
`entity_id` thuộc item. Cursor `(occurred_at DESC, id DESC)` — khớp index
`(entity_type, entity_id, occurred_at DESC)`. Trả `{occurred_at, actor: ActorRef, action, entity_type, entity_id, summary}`;
`before`/`after` jsonb **chỉ** trả khi `?include=diff` và **chỉ** cho `ADMIN` (có thể chứa nội dung nhạy cảm).

**`/content/{id}/derivations`** *(derived)* — cây `parent_content_item_id` **một cấp lên, một cấp xuống**
(không đệ quy sâu — chặn truy vấn không giới hạn). Trả `{parent: ContentSummary|null, children: ContentSummary[]}`.

---

### 6.4 `/api/v1/content/:id/revisions`

Ràng buộc chi phối toàn nhóm: **`FROZEN` là bất biến** (B-R1, trigger chặn UPDATE);
**diff tính lúc đọc, không lưu**; **không bao giờ xoá**.

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/content/{id}/revisions` | GET | BOTH | READONLY | — | — | 600/p |
| `/content/{id}/revisions` | POST | BOTH | EDITOR | ✅ | ✅ | 60/p |
| `/content/{id}/revisions/{rid}` | GET | BOTH | READONLY | — | — | 300/p |
| `/content/{id}/revisions/{rid}` | PATCH | FE | EDITOR | — (If-Match) | ✅ | 120/p |
| `/content/{id}/revisions/{rid}/request-review` | POST | FE | EDITOR | ✅ | ✅ | 60/p |
| `/content/{id}/revisions/{rid}/freeze` | POST | FE | APPROVER | ✅ | ✅ | 30/p |
| `/content/{id}/revisions/{rid}/promote` | POST | FE | APPROVER | ✅ | ✅ | 30/p |
| `/content/{id}/revisions/diff` | GET | FE | READONLY | — | — | 60/p |
| `/content/{id}/revisions/{rid}/claims` | GET | BOTH | READONLY | — | — | 300/p |
| `/content/{id}/revisions/{rid}/manifest` | GET | BOTH | READONLY | — | — | 300/p |

```ts
export const RevisionSummary = z.object({    // projection list — KHÔNG có cột nặng
  id: Uuid, content_item_id: Uuid, revision_no: z.number().int(),
  parent_revision_id: Uuid.nullable(), status: RevisionStatus,
  title_final: z.string().nullable(), hook: z.string().nullable(),   // hook ≤ vài trăm ký tự
  created_by_kind: z.enum(['HUMAN','AGENT']),
  created_by_user_id: Uuid.nullable(), created_by_worker_id: Uuid.nullable(),
  generator_name: z.string().nullable(), generator_version: z.string().nullable(),
  algorithm_version_id: Uuid.nullable(), change_reason: z.string().nullable(),
  triggered_by_audit_run_id: Uuid.nullable(), triggered_by_score_run_id: Uuid.nullable(),
  content_sha256: Sha256.nullable(), payload_schema_version: z.number().int(),
  frozen_at: Ts.nullable(), frozen_by: Uuid.nullable(), created_at: Ts,
  // derived
  is_approved: z.boolean(), is_production: z.boolean(),
  script_chars: z.number().int().nullable(), script_bytes: z.number().int().nullable(),
  latest_overall_score_bp: Bp.nullable(),
});
export const RevisionFull = RevisionSummary.extend({   // CHỈ single-resource
  outline: z.string().nullable(), audio_script: z.string().nullable(),
  description: z.string().nullable(), pinned_comment: z.string().nullable(),
  community_post: z.string().nullable(), research_summary: z.string().nullable(),
  risk_notes: z.string().nullable(), production_notes: z.string().nullable(),
  title_candidates: z.array(z.string()), keywords: z.array(z.string()), hashtags: z.array(z.string()),
  seo_package: z.unknown().nullable(), semantic_beats: z.unknown().nullable(),
  visual_prompts: z.unknown().nullable(), thumbnail_concepts: z.unknown().nullable(),
  chapters: z.unknown().nullable(),
});
export const RevisionCreate = z.object({
  parent_revision_id: Uuid.optional(), change_reason: z.string().min(3).max(1000),
  hook: z.string().max(2_000).optional(),
  outline: z.string().max(100_000).optional(),
  audio_script: z.string().max(400_000).optional(),      // đo được lớn nhất 67,8 KB
  description: z.string().max(20_000).optional(),
  pinned_comment: z.string().max(10_000).optional(), community_post: z.string().max(10_000).optional(),
  research_summary: z.string().max(200_000).optional(), risk_notes: z.string().max(50_000).optional(),
  production_notes: z.string().max(50_000).optional(), title_final: z.string().max(300).optional(),
  title_candidates: z.array(z.string().max(300)).max(20).optional(),
  keywords: z.array(z.string().max(100)).max(100).optional(),
  hashtags: z.array(z.string().max(100)).max(60).optional(),
  seo_package: z.unknown().optional(), semantic_beats: z.unknown().optional(),
  visual_prompts: z.unknown().optional(), thumbnail_concepts: z.unknown().optional(),
  chapters: z.unknown().optional(), payload_schema_version: z.number().int().min(1),
}).strict();
export const RevisionFreeze = z.object({
  expected_content_sha256: Sha256.optional(),   // client đã đọc đúng bản định freeze
  note: z.string().max(500).optional(),
}).strict();
export const ImportBatchStatus = z.enum([
  'OPEN','FINALIZING','COMPLETED_DRY_RUN','APPLIED','FAILED',
]); // nguồn chuẩn: LEGACY_IMPORT_AND_SYNC_PLAN §5.1 (rollback dùng Neon restore ⇒ không có ROLLING_BACK/ROLLED_BACK)

export const ImportRecordItem = z.object({
  entity_type: z.string(),
  legacy_ref: z.string().max(500),          // định danh ổn định, KHÔNG phụ thuộc cách chia chunk
  legacy_sha256: z.string().length(64),
  depends_on_legacy_ref: z.string().max(500).nullable(),  // BẮT BUỘC có mặt (null nếu không phụ thuộc)
  raw_payload: z.unknown(),
}).strict();
export const ImportRecordsPush = z.object({ records: z.array(ImportRecordItem).max(200) }).strict();
// chunk_seq/row_seq do SERVER sinh — client không gửi, không dùng để định danh.


export const RevisionPromote = z.object({
  approval_id: Uuid,
  // ⚠️ BẮT BUỘC CÓ MẶT, kể cả khi null (lần promote đầu tiên).
  // Đây là token đồng thời cho CAS ở §6.4 — KHÔNG được suy ra trong server.
  expected_production_revision_id: Uuid.nullable(),
  reason: z.string().max(500).optional(),
}).strict();
// Chọn body làm biểu diễn CHÍNH THỨC DUY NHẤT. KHÔNG dùng `If-Match` cho promote:
// ETag chung ở §1 dẫn xuất từ (id, updated_at) nên không biểu diễn được "production hiện tại là NULL".
// Thiếu trường ⇒ 422 VALIDATION_FAILED (không mặc định, không đoán).
export const RevisionDiff = z.object({
  from_revision_id: Uuid, to_revision_id: Uuid,
  fields: z.array(z.object({
    field: z.string(), changed: z.boolean(),
    from_sha256: Sha256.nullable(), to_sha256: Sha256.nullable(),
    from_chars: z.number().int().nullable(), to_chars: z.number().int().nullable(),
    hunks: z.array(z.object({ op: z.enum(['EQUAL','INSERT','DELETE']),
                              from_line: z.number().int().nullable(),
                              to_line: z.number().int().nullable(),
                              text: z.string() })).nullish(),   // chỉ khi ?fields=
    truncated: z.boolean(),
  })),
  computed_at: Ts,
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | Cursor `(revision_no DESC)` — khớp unique `(content_item_id, revision_no)`; **limit 20/50** (thấp hơn mặc định vì hàng nặng hơn) |
| Filter | `status[]`, `created_by_kind`, `generator_name`, `algorithm_version_id`, `created_at[gte\|lt]` |
| Sort | `-revision_no` (mặc định), `-created_at` |
| Fields | Single-resource: `?fields=` trên allowlist `RevisionFull`. **Mặc định GET detail trả `RevisionFull` trừ `seo_package`/`visual_prompts`/`semantic_beats`/`thumbnail_concepts`** — phải xin rõ ràng (payload 194,8 KB) |
| Validation POST | `parent_revision_id` phải thuộc **cùng item**; `revision_no` do **server** cấp (`max+1`, trong transaction) — client gửi ⇒ 422 `UNKNOWN_FIELD`; revision mới **luôn** vào `DRAFT`; `payload_schema_version` bắt buộc với mọi jsonb (`DATA_MODEL_PLAN §0`) |
| Validation PATCH | Chỉ `DRAFT`/`REVIEW_REQUIRED`. `FROZEN` ⇒ **409 `REVISION_FROZEN`**. `If-Match` bắt buộc |
| Validation freeze | Chỉ từ `DRAFT`/`REVIEW_REQUIRED`; server tính `content_sha256` (chuẩn hoá) + set `frozen_at`/`frozen_by`; `expected_content_sha256` lệch ⇒ 409 `PRECONDITION_FAILED`. Sau freeze, hàng **bất biến** |
| Validation promote | **Phải tuần tự hoá + CAS theo kỳ vọng caller** — xem khối dưới bảng. Body **bắt buộc** có `expected_production_revision_id` (kể cả `null`). `If-Match` **không áp dụng** cho endpoint này |

> ⚠️ **Sửa theo Codex v2R4 HIGH-2 — promote phải được tuần tự hoá, không chỉ "trong một transaction".**
> Bản trước chỉ nói kiểm `approval.status='ACTIVE'` rồi cập nhật. Không có khoá hàng hay CAS ⇒ hai
> transaction có thể **cùng** thấy A là production và ghi `A→B` lẫn `A→C`, trong khi con trỏ cuối là C.
> Khi đó **chuỗi sự kiện không còn là lịch sử hợp lệ** — mà đây chính là cơ chế duy nhất thay cho
> trạng thái `SUPERSEDED` có thể ghi đè. Tương tự, revoke xen vào **sau** bước kiểm sẽ cho phép
> promote bằng approval đã hết hiệu lực.
>
> **Giao thức bắt buộc (một transaction tương tác — chạy trên Pool/WebSocket, xem `TARGET_ARCHITECTURE.md §5.1`).** Caller **phải** gửi
> `expected_production_revision_id` **trong JSON body** (`If-Match` **không** dùng cho endpoint này) — đây là điểm mấu chốt:
>
> ```sql
> BEGIN;
> -- 1) Khoá item, đọc production hiện tại
> SELECT production_revision_id AS locked_prev
>   FROM content_item WHERE id = :item FOR UPDATE;
>
> -- 2) SO VỚI KỲ VỌNG CỦA CALLER (không phải với chính giá trị vừa đọc)
> --    locked_prev <> :expected_production_revision_id  ⇒ ABORT 409 CONCURRENT_PROMOTION
>
> -- 2b) TỪ CHỐI PROMOTE CHÍNH NÓ (A→A) trước khi đụng approval
> --     :rid IS NOT DISTINCT FROM locked_prev  ⇒ ABORT 409 ALREADY_PRODUCTION
>
> -- 3) Khoá approval PRODUCTION_READY của revision ĐÍCH, kiểm trong khoá
> SELECT 1 FROM approval
>  WHERE id = :approval_id AND content_item_id = :item
>    AND content_revision_id = :rid AND gate = 'PRODUCTION_READY' AND status = 'ACTIVE'
>  FOR UPDATE;                                   -- 0 dòng ⇒ ABORT 409
>
> -- 4) Xác định ĐÚNG approval đã cho phép promote bản hiện tại, và khoá nó
> --    BẤT KỂ status (có thể đã REVOKED) — xem cảnh báo H2 bên dưới.
> --    Nguồn chuẩn: event promote gần nhất trỏ tới con trỏ hiện tại.
> SELECT a.id AS prev_approval_id, a.status AS prev_status
>   FROM revision_promotion_event e
>   JOIN approval a ON a.id = e.approval_id
>  WHERE e.content_item_id = :item
>    AND e.to_revision_id IS NOT DISTINCT FROM :expected_production_revision_id
>  ORDER BY e.promoted_at DESC
>  LIMIT 1
>  FOR UPDATE OF a;
> --    0 dòng CHỈ hợp lệ khi :expected_production_revision_id IS NULL (chưa từng promote).
> --    Ngược lại ⇒ ABORT 409 (dữ liệu không nhất quán).
>
> -- 5) Đổi con trỏ
> UPDATE content_item SET production_revision_id = :rid
>  WHERE id = :item
>    AND production_revision_id IS NOT DISTINCT FROM :expected_production_revision_id
> RETURNING production_revision_id;               -- 0 dòng ⇒ ABORT 409
>
> -- 6) Ghi sự kiện; from_revision_id = giá trị ĐÃ KHOÁ và ĐÃ đối chiếu
> INSERT INTO revision_promotion_event
>   (content_item_id, from_revision_id, to_revision_id, approval_id, promoted_by, reason)
> VALUES (:item, :expected_production_revision_id, :rid, :approval_id, :user, :reason);
>
> -- 7) CHỈ khi CÓ production cũ (locked_prev IS NOT NULL):
> --    supersede đúng approval PRODUCTION_READY của revision cũ, và CHỈ khi nó còn ACTIVE
> --    (đã REVOKED thì GIỮ NGUYÊN lịch sử). Nếu locked_prev IS NULL ⇒ BỎ QUA HẲN bước 4 và 7.
> UPDATE approval SET status='SUPERSEDED'
>  WHERE id = :prev_approval_id AND status = 'ACTIVE';
> COMMIT;
> ```
>
> ⚠️ **Nhánh promote lần đầu (`locked_prev IS NULL`)** — Codex v2R7 MEDIUM:
> **bỏ qua hoàn toàn bước 4 và bước 7.** `:prev_approval_id` **không tồn tại** ở nhánh này; chạy
> bước 7 với tham số chưa gán là lỗi lập trình. Event vẫn ghi `NULL → :rid`, và approval của `:rid`
> **giữ nguyên `ACTIVE`**.
>
> **Quy tắc "0 dòng" theo từng bước** *(thay cho quy tắc chung "0 dòng ⇒ rollback")*:
>
> | Bước | 0 dòng nghĩa là | Hành động |
> |---|---|---|
> | 1 | item không tồn tại | **404** |
> | 2 | kỳ vọng lệch thực tế | **409 `CONCURRENT_PROMOTION`** |
> | 3 | approval đích không `ACTIVE` | **409 `APPROVAL_NOT_ACTIVE`** |
> | 2b | `:rid` trùng production hiện tại | **409 `ALREADY_PRODUCTION`** — không đổi con trỏ, không ghi event, không đụng approval |
> | 4 | *(chỉ chạy khi `locked_prev IS NOT NULL`)* không tìm thấy event/approval trước | **409** — dữ liệu không nhất quán |
> | 4′ | `locked_prev IS NULL` (promote lần đầu) | **Bỏ qua bước 4 và 7** — không phải lỗi |
> | 5 | con trỏ đã đổi | **409 `CONCURRENT_PROMOTION`** |
> | 6 | — | INSERT luôn phải thành công |
> | **7** | **approval cũ đã `REVOKED`** | **Hợp lệ — bỏ qua, KHÔNG rollback** |
> | 7′ | bước 7 **không chạy** vì `locked_prev IS NULL` | **Hợp lệ** — promote lần đầu |

> ⚠️ **Sửa theo Codex v2R6 HIGH-2 — revoke không được làm kẹt item vĩnh viễn.**
> Bản trước khoá approval cũ với điều kiện `status='ACTIVE'` **và** áp quy tắc chung
> "bất kỳ bước nào 0 dòng ⇒ rollback". Hệ quả: sau khi approval của revision A bị **revoke**
> (một thao tác bảo mật **được hỗ trợ**), mọi lần promote B về sau đều trả 0 dòng ở bước 4 và
> **luôn rollback** ⇒ content item **kẹt vĩnh viễn** ở A, kể cả khi B đã có approval hợp lệ.
> Nay: khoá approval cũ **bất kể status**, và bước 7 chỉ đổi khi nó còn `ACTIVE` — lịch sử
> `REVOKED` được giữ nguyên.
>
> ⚠️ **Sửa theo Codex v2R5 HIGH-1 — CAS phải so với kỳ vọng của CALLER.**
> Bản trước đọc `:prev` **bên trong** khoá rồi CAS với chính nó. Khi B và C cùng promote từ A,
> giao dịch thứ hai **chờ**, rồi đọc kết quả của bên thắng làm `:prev` của mình ⇒ CAS **cũng thành
> công** ⇒ thành `A→B→C`, không phải "đúng một thắng". Tệ hơn: một request cũ muốn promote C "từ A"
> lại **âm thầm** biến thành promote từ B, ghi đè quyết định vừa xảy ra. CAS chỉ có tác dụng khi giá
> trị kỳ vọng đến **từ ngoài** transaction.
>
> ⚠️ **Sửa theo Codex v2R5 HIGH-2 — chỉ supersede đúng gate `PRODUCTION_READY` của revision cũ.**
> Bản trước dùng `WHERE content_item_id=:item AND status='ACTIVE' AND id<>:approval_id` ⇒ **xoá sạch**
> approval đang hoạt động ở **cả bốn** gate (`RESEARCH_READY`, `CONTENT_READY`, `PRODUCTION_READY`,
> `PUBLISH_READY`) của toàn bộ item. Vì promote là **con đường duy nhất** tới `SUPERSEDED`, những
> approval đó **không khôi phục được** nếu không tạo bản ghi mới.
>
>
> **Ràng buộc bổ sung:** `revision_promotion_event.approval_id` phải gắn với **đúng** item và revision:
> ```sql
> ALTER TABLE approval ADD CONSTRAINT uq_appr_item_rev UNIQUE (id, content_item_id, content_revision_id);
> ALTER TABLE revision_promotion_event ADD CONSTRAINT fk_promo_appr
>   FOREIGN KEY (approval_id, content_item_id, to_revision_id)
>   REFERENCES approval (id, content_item_id, content_revision_id);
> ```
>
> ⚠️ `content_revision.status` **không** đổi — nó ở lại `FROZEN` vĩnh viễn.
> Đây là **chỗ duy nhất** approval bị `SUPERSEDED`.
| Lỗi riêng | `REVISION_FROZEN`, `REVISION_NOT_FROZEN`, `INVALID_STATE_TRANSITION`, `APPROVAL_REQUIRED`, `APPROVAL_REVOKED`, `PRECONDITION_*`, `PAYLOAD_TOO_LARGE` |
| Ghi chú caller | **Worker không dùng nhóm này.** Agent tạo revision qua `POST /api/worker/revisions` (`API_AND_WORKER_PROTOCOL.md §5.4, §8.3`) và **không** được `freeze`/`promote` |

**`/revisions/diff?from=&to=&fields=`** — bất biến "không lưu diff" (`DATA_MODEL_PLAN §3`).
Rủi ro payload là cao nhất toàn API: hai bản `audio_script` 67,8 KB + hunks có thể vượt vài trăm KB.
Ràng buộc: `from`/`to` phải **cùng `content_item_id`**; `fields` tối đa **3**; không có `fields` ⇒
chỉ trả **tóm tắt thay đổi** (`changed`, sha256, số ký tự) — không hunk; hunk cắt ở
**512 KB/field** kèm `truncated: true`. Cache `Cache-Control: private, max-age=300` khi cả hai đều `FROZEN`
(bất biến ⇒ cache được vô hạn về mặt logic).

**`/revisions/{rid}/manifest`** — trả `production_manifest.payload` + `manifest_sha256`
(chỉ có khi revision đã `FROZEN`). Đây là bản **đọc cho người dùng**; worker lấy manifest qua
`GET /api/worker/jobs/{id}/manifest`. `?include=frozen_input` trả thêm `frozen_input_manifest`
(`repo_url`, `commit_sha`, `files[]`, `environment`) — `files[]` cắt ở **500 mục**, có `truncated`.

---

### 6.5 `/api/v1/content/:id/scores`

**`score_run` là append-only** (S-1: không UPDATE, không DELETE). Vì vậy User API **không có PUT/PATCH/DELETE**.
Ghi điểm **chỉ** qua `POST /api/worker/jobs/{id}/scores` (`API_AND_WORKER_PROTOCOL.md §8.2`).

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/content/{id}/scores` | GET | BOTH | READONLY | — | — | 600/p |
| `/content/{id}/scores` | POST | FE | REVIEWER | ✅ | ✅ | 30/p |
| `/content/{id}/scores/{run_id}` | GET | BOTH | READONLY | — | — | 300/p |
| `/content/{id}/scores/compare` | GET | FE | READONLY | — | — | 120/p |
| `/content/{id}/scores/trend` | GET | FE | READONLY | — | — | 300/p |

> `POST /content/{id}/scores` **không ghi điểm** — nó **enqueue job `SCORE_CONTENT`** và trả **202**.
> Đặt tên vậy để frontend không phải biết tới nhóm `/jobs` cho hành động "chấm lại".

```ts
export const ScoreRunSummary = z.object({
  id: Uuid, content_item_id: Uuid, content_revision_id: Uuid, revision_no: z.number().int(), // derived
  algorithm_id: Uuid, algorithm_version_id: Uuid,
  algorithm_key: z.string(), algorithm_version: z.string(), algorithm_kind: z.enum(['RULE','LLM','HYBRID']), // derived
  overall_score_bp: Bp, input_snapshot_hash: Sha256,
  previous_score_run_id: Uuid.nullable(), overall_delta_bp: z.number().int().nullable(),
  actor: ActorRef, job_attempt_id: Uuid.nullable(), created_at: Ts,
});
export const ScoreDimensionOut = z.object({
  dimension: Dimension, value_bp: Bp, weight_bp: Bp, rationale: z.string().nullable(),
  evidence: z.unknown().nullable(),
  weighted_bp: z.number().int(),          // derived = value_bp*weight_bp/10000
  delta_bp: z.number().int().nullable(),  // derived vs previous_score_run_id
});
export const ScoreRunDetail = ScoreRunSummary.extend({
  explanation: z.string().nullable(),
  dimensions: z.array(ScoreDimensionOut),
  findings: z.unknown().nullable(),          // chỉ khi ?include=findings
  recommendations: z.unknown().nullable(),   // chỉ khi ?include=recommendations
  weights_source: z.object({ algorithm_version_id: Uuid, weights: z.unknown() }), // giải thích được
  recomputed_overall_bp: z.number().int(),   // derived: Σ(value×weight) — PHẢI khớp overall_score_bp
  recompute_matches: z.boolean(),
});
export const ScoreRequest = z.object({
  content_revision_id: Uuid, algorithm_key: z.string().max(100).optional(),
  algorithm_version_id: Uuid.optional(), priority: z.number().int().min(0).max(100).default(50),
}).strict();
export const ScoreCompare = z.object({
  a: ScoreRunSummary, b: ScoreRunSummary,
  comparable: z.boolean(),                    // false nếu khác algorithm_version_id
  incomparable_reason: z.string().nullable(),
  overall_delta_bp: z.number().int(),
  dimensions: z.array(z.object({ dimension: Dimension, a_bp: Bp.nullable(), b_bp: Bp.nullable(),
                                 delta_bp: z.number().int().nullable() })),
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | Cursor `(created_at DESC, id DESC)` — khớp index `(content_item_id, created_at DESC)`; 25/100 |
| Filter | `content_revision_id`, `algorithm_id`, `algorithm_version_id`, `actor_kind`, `created_at[gte\|lt]`, `overall_score_bp[gte\|lt]` |
| Sort | `-created_at` (mặc định), `-overall_score_bp` |
| Include | `dimensions` (mặc định **có** ở detail, **không** ở list), `findings`, `recommendations` |
| Validation POST | `content_revision_id` phải thuộc item; **không** yêu cầu `FROZEN` (chấm được cả `DRAFT` để biết có nên sửa tiếp); `algorithm_version_id` phải `is_active` nếu không chỉ định version |
| Bất biến kiểm ở đọc | Server tính lại `recomputed_overall_bp` từ `score_dimension × algorithm_version.weights`; lệch ⇒ vẫn trả nhưng `recompute_matches=false` **và** ghi cảnh báo — **không** sửa dữ liệu (append-only) |
| Idempotency | Khử trùng **chỉ** qua `idempotency_record` `(scope='SCORE', idempotency_key, principal)`. Cùng key + cùng `request_hash` ⇒ trả `score_run` cũ; khác `request_hash` ⇒ **409 `IDEMPOTENCY_KEY_REUSED`**. Request **có chủ đích** với key mới ⇒ **`score_run` mới**, `run_sequence` kế tiếp. Unique bảng: `(content_revision_id, algorithm_version_id, input_snapshot_hash, run_sequence)` |
| `compare` | Bắt buộc `a`/`b` **cùng `content_item_id`**. Khác `algorithm_version_id` ⇒ `comparable=false` + lý do — **cấm** hiển thị delta như thể so sánh được (điểm khác thuật toán không cùng thang) |
| `trend` | Chuỗi `(created_at, overall_score_bp, revision_no, algorithm_version_id)` cho **một** `algorithm_id`, tối đa **200 điểm**, cửa sổ tối đa 180 ngày |
| Lỗi riêng | `NOT_FOUND`, `VALIDATION_FAILED`, `DUPLICATE_JOB` (đã có `SCORE_CONTENT` live cho revision này) |

---

### 6.6 `/api/v1/content/:id/audits`

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/content/{id}/audits` | GET | BOTH | READONLY | — | — | 600/p |
| `/content/{id}/audits` | POST | FE | REVIEWER | ✅ | ✅ | 30/p |
| `/content/{id}/audits/{run_id}` | GET | BOTH | READONLY | — | — | 300/p |
| `/content/{id}/audits/{run_id}/findings` | GET | BOTH | READONLY | — | — | 300/p |
| `/content/{id}/audits/{run_id}/findings` | POST | FE | REVIEWER | ✅ | ✅ | 120/p |
| `/content/{id}/audits/{run_id}/findings/{fid}/resolve` | POST | FE | REVIEWER | ✅ | ✅ | 120/p |
| `/content/{id}/gates` | GET | FE | READONLY | — | — | 300/p |

> `POST /content/{id}/audits` **enqueue `ANALYZE_CONTENT`** → **202**. Người dùng **được** ghi
> `audit_finding` thủ công (ma trận quyền: "Ghi audit finding" = REVIEWER/APPROVER) — đó là lý do
> có `POST …/findings` ở User API.

```ts
export const AuditRunSummary = z.object({
  id: Uuid, content_item_id: Uuid, content_revision_id: Uuid, revision_no: z.number().int(),
  gate: Gate, runner_kind: z.enum(['HUMAN','AGENT','TOOL']), runner_ref: z.string().nullable(),
  algorithm_version_id: Uuid.nullable(),
  status: z.enum(['RUNNING','PASS','PASS_WITH_ADVISORIES','FAIL','BLOCKED','ERROR']),
  started_at: Ts, finished_at: Ts.nullable(),
  finding_counts: z.object({ BLOCKER: z.number().int(), HIGH: z.number().int(),
    MEDIUM: z.number().int(), LOW: z.number().int(), ADVISORY: z.number().int() }),   // derived
  unresolved_blockers: z.number().int(),   // derived
});
export const AuditFindingOut = z.object({
  id: Uuid, audit_run_id: Uuid, check_id: z.string(), category: z.string(),
  severity: z.enum(['BLOCKER','HIGH','MEDIUM','LOW','ADVISORY']), message: z.string(),
  evidence: z.unknown().nullable(),        // chỉ khi ?include=evidence
  resolved_at: Ts.nullable(), resolved_by: Uuid.nullable(), resolution_note: z.string().nullable(),
});
export const AuditFindingCreate = z.object({
  check_id: z.string().max(100), category: z.string().max(100),
  severity: z.enum(['BLOCKER','HIGH','MEDIUM','LOW','ADVISORY']),
  message: z.string().min(1).max(4000), evidence: z.unknown().optional(),
}).strict();
export const AuditFindingResolve = z.object({
  resolution_note: z.string().min(3).max(2000),
}).strict();
export const GateStatus = z.object({       // TẤT CẢ derived — tổng hợp cho màn hình Approval
  content_item_id: Uuid, content_revision_id: Uuid,
  gates: z.array(z.object({
    gate: Gate, latest_audit_run_id: Uuid.nullable(),
    status: z.enum(['NOT_RUN','RUNNING','PASS','PASS_WITH_ADVISORIES','FAIL','BLOCKED','ERROR']),
    unresolved_blockers: z.number().int(),
    blocking_reasons: z.array(z.string()),   // vd 'CLAIM_CONFLICT_UNRESOLVED'
    approval_id: Uuid.nullable(), approval_status: z.enum(['ACTIVE','REVOKED','SUPERSEDED']).nullable(),
    can_approve: z.boolean(),                 // theo quyền + policy của người gọi
  })),
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | `audits`: cursor `(started_at DESC, id DESC)`, 25/100. `findings`: cursor `(severity_rank, id)`, **50/200** |
| Filter | `audits`: `gate`, `status[]`, `content_revision_id`, `runner_kind`, `started_at[gte\|lt]`. `findings`: `severity[]`, `category`, `resolved` (bool), `check_id` |
| Sort | `audits`: `-started_at`. `findings`: `severity` (BLOCKER→ADVISORY, mặc định), `-id` |
| Include | `evidence` (jsonb, có thể lớn ⇒ mặc định **không** trả) |
| Validation | POST finding: chỉ vào `audit_run` có `runner_kind='HUMAN'` **hoặc** run đã `finished_at` (không chèn vào run của agent đang chạy). Resolve: đã resolve ⇒ 409 `INVALID_STATE_TRANSITION`; `resolution_note` bắt buộc |
| Ánh xạ QA | `status` cố ý khớp `qa_status` của Content-Creator 1-1 (`DATA_MODEL_PLAN §5`) ⇒ frontend không cần bảng chuyển đổi |
| Lỗi riêng | `INVALID_STATE_TRANSITION`, `DUPLICATE_JOB`, `CLAIM_CONFLICT_UNRESOLVED` (khi `/gates` cho gate `RESEARCH_READY`) |

---

### 6.7 `/api/v1/content/:id/approvals`

Nhóm nhạy cảm nhất. Bất biến bắt buộc: **A-1** `approved_by` phải là USER thật (agent/worker
không có đường vào endpoint này); **A-2** approval của A chỉ `SUPERSEDED` **trong transaction promote B**
(xem `POST …/revisions/{rid}/promote`, §6.4); **A-3** không xoá — thu hồi = đổi `status`.

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/content/{id}/approvals` | GET | BOTH | READONLY | — | — | 600/p |
| `/content/{id}/approvals` | POST | **FE** | APPROVER | ✅ | ✅ | 30/p |
| `/content/{id}/approvals/{aid}` | GET | BOTH | READONLY | — | — | 300/p |
| `/content/{id}/approvals/{aid}/revoke` | POST | **FE** | APPROVER | ✅ | ✅ | 30/p |

```ts
export const ApprovalOut = z.object({
  id: Uuid, content_item_id: Uuid, content_revision_id: Uuid, revision_no: z.number().int(),
  gate: Gate, approved_by: Uuid, approved_by_label: z.string(),   // derived
  approved_at: Ts, audit_run_id: Uuid.nullable(), score_run_id: Uuid.nullable(),
  overall_score_at_approval_bp: Bp.nullable(),
  status: z.enum(['ACTIVE','REVOKED','SUPERSEDED']),
  revoked_by: Uuid.nullable(), revoked_at: Ts.nullable(), revoke_reason: z.string().nullable(),
  self_approved: z.boolean(),                                      // derived từ audit_event
});
export const ApprovalCreate = z.object({
  content_revision_id: Uuid, gate: Gate,
  audit_run_id: Uuid.optional(), score_run_id: Uuid.optional(),
  reason: z.string().min(3).max(1000),
  reauth_token: z.string().optional(),        // BẮT BUỘC khi tự-duyệt (§3)
}).strict();
export const ApprovalRevoke = z.object({ revoke_reason: z.string().min(3).max(1000) }).strict();
```

| Kiểm tra | Quy định |
|---|---|
| Revision | Phải thuộc item **và** `status='FROZEN'` ⇒ ngược lại **409 `REVISION_NOT_FROZEN`** |
| Trùng | Partial unique `(content_revision_id, gate) WHERE status='ACTIVE'` ⇒ **409 `APPROVAL_EXISTS`** |
| Principal | `actor_kind` phải là `USER`. PAT được phép **nếu** scope chứa `approvals:write`; worker token đã bị chặn ở tầng §3 |
| Tự-duyệt | `channel.approval_policy='TWO_PERSON_REQUIRED'` **và** `approved_by == content_revision.created_by_user_id` ⇒ **409 `SELF_APPROVAL_FORBIDDEN`**. `SELF_APPROVAL_ALLOWED` ⇒ đòi `reauth_token` hợp lệ, thiếu ⇒ **403 `STEP_UP_REQUIRED`**; ghi `audit_event` với `self_approved=true` |
| Bằng chứng | `audit_run_id`/`score_run_id` (nếu gửi) phải trỏ **đúng `content_revision_id` này**; server tự chép `overall_score_at_approval_bp` từ `score_run.overall_score` — client **không** được gửi giá trị điểm |
| Gate `PUBLISH_READY` | Đòi `audit_run.status ∈ {PASS, PASS_WITH_ADVISORIES}` và `unresolved_blockers=0` ⇒ ngược lại **409 `CONTENT_GATE_NOT_MET`** |
| Revoke | Chỉ từ `ACTIVE`; `revoke_reason` bắt buộc; **không** đụng `content_item.production_revision_id` (việc đó là transition riêng) — nhưng publish sau đó **phải** kiểm lại approval `ACTIVE` |
| Pagination/Filter/Sort | Cursor `(approved_at DESC, id)`; filter `gate`, `status[]`, `content_revision_id`; sort `-approved_at` |
| Audit | **Luôn** ghi, kể cả khi thất bại vì policy (cần dấu vết ý định tự-duyệt) |
| Caller | **Chỉ FE/người dùng.** CLI-as-user *về mặt kỹ thuật* gọi được bằng PAT nhưng **không có luồng CLI nào được thiết kế để approve** — worker tuyệt đối không |

---

### 6.8 `/api/v1/content/:id/sources`

⚠️ **Fetch nguồn chạy ở CLI, không ở Vercel** (`DATA_MODEL_PLAN §4`) — giữ SSRF ra khỏi control plane.
Vì vậy User API **không có** endpoint kiểu "nhập URL, server đi tải". Server chỉ nhận **kết quả đã tải**.

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/content/{id}/sources` | GET | BOTH | READONLY | — | — | 600/p |
| `/content/{id}/sources` | POST | FE | EDITOR | ✅ | ✅ | 120/p |
| `/content/{id}/sources/{sid}` | DELETE | FE | EDITOR | ✅ | ✅ | 120/p |
| `/sources` | GET | BOTH | READONLY¹ | — | — | 600/p |
| `/sources` | POST | **CLI** | EDITOR | ✅ | ✅ | 120/p |
| `/sources/{sid}` | GET / PATCH | BOTH | READONLY / REVIEWER | ✅ (PATCH) | ✅ | 300/p |
| `/sources/{sid}/versions` | GET | BOTH | READONLY | — | — | 300/p |
| `/sources/{sid}/versions/{vid}/text` | GET | FE | READONLY | — | — | 60/p |
| `/content/{id}/claims` | GET | BOTH | READONLY | — | — | 300/p |
| `/claims/{cid}` | GET | BOTH | READONLY | — | — | 300/p |
| `/claims/{cid}/evidence` | GET | BOTH | READONLY | — | — | 300/p |

¹ `source_document` gắn `domain_id` (`BUD|FS|CL`), **không** gắn `channel_id`. Quyền = có ≥1 kênh
cùng `domain_id`. **[ASSUMPTION → §14 A-3]** — đây là điểm khác biệt duy nhất so với scope theo kênh.

```ts
export const SourceDocument = z.object({
  id: Uuid, domain_id: z.enum(['BUD','FS','CL']), origin_url: z.string().nullable(),
  origin_kind: z.enum(['WEB','RSS','YOUTUBE','PDF','LOCAL_FILE','API','TRANSCRIPT','MANUAL','AGENT']),
  title: z.string().nullable(), author: z.string().nullable(), publisher: z.string().nullable(),
  published_at: Ts.nullable(), retrieved_at: Ts, language: z.string().nullable(),
  tier: z.number().int().min(1).max(6), is_primary: z.boolean(),
  license_note: z.string().nullable(),
  status: z.enum(['DISCOVERED','APPROVED','REJECTED','RESTRICTED']),
  rejected_reason: z.string().nullable(),
  version_count: z.number().int(), latest_version_id: Uuid.nullable(),   // derived
  usage_note: z.string().nullable(),      // chỉ ở ngữ cảnh /content/{id}/sources
});
export const SourceVersion = z.object({
  id: Uuid, source_document_id: Uuid, fetched_at: Ts, content_sha256: Sha256,
  storage_backend: z.enum(['DB','LOCAL','BLOB']), local_path: z.string().nullable(),
  byte_size: z.number().int(), http_status: z.number().int().nullable(),
  has_extracted_text: z.boolean(),        // derived — text KHÔNG nằm ở đây
});
export const SourceText = z.object({      // endpoint riêng vì có thể tới 444,9 KB
  source_version_id: Uuid, content_sha256: Sha256,
  text: z.string(), byte_offset: z.number().int(), byte_length: z.number().int(),
  total_bytes: z.number().int(), truncated: z.boolean(),
  is_untrusted: z.literal(true),          // nội dung nguồn LUÔN là dữ liệu không tin cậy
});
export const ContentSourceAttach = z.object({
  source_document_id: Uuid, usage_note: z.string().max(1000).optional(),
}).strict();
export const ClaimOut = z.object({
  id: Uuid, domain_id: z.enum(['BUD','FS','CL']), text: z.string(),
  confidence_tier: z.enum(['HIGH','MEDIUM_HIGH','MEDIUM','LOW']),
  status: z.enum(['PROPOSED','VERIFIED','DISPUTED','REJECTED']), risk_level: z.string().nullable(),
  role: z.string().nullable(),            // từ content_revision_claim
  evidence_counts: z.object({ SUPPORTS: z.number().int(), CONTRADICTS: z.number().int(),
                              CONTEXT: z.number().int() }),                 // derived
  has_unresolved_conflict: z.boolean(),   // derived: SUPPORTS>0 && CONTRADICTS>0 && status≠VERIFIED/REJECTED
});
export const ClaimEvidenceOut = z.object({
  id: Uuid, claim_id: Uuid, source_version_id: Uuid,
  source_document_id: Uuid, source_title: z.string().nullable(), source_tier: z.number().int(), // derived
  stance: z.enum(['SUPPORTS','CONTRADICTS','CONTEXT']),
  quote: z.string(), locator: z.string().nullable(), added_by_kind: z.string(),
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | Cursor `(retrieved_at DESC, id)`; 25/100. Evidence: 50/200 |
| Filter | `/sources`: `domain_id`, `tier[]`, `status[]`, `origin_kind[]`, `is_primary`, `published_at[gte\|lt]`, `q` (title). `/claims`: `status[]`, `confidence_tier[]`, `has_unresolved_conflict` |
| Sort | `-retrieved_at` (mặc định), `tier`, `-published_at` |
| Fields | `extracted_text` **không bao giờ** nằm trong `/versions`; phải gọi `…/text` |
| `…/text` | Query `?offset=&length=` (mặc định `length=262144` = 256 KB). File text lớn nhất đo được **444,9 KB** ⇒ tối đa **2 lô**. `truncated=true` khi còn phần chưa trả |
| Validation | Attach: `source_document.domain_id` phải trùng `channel.domain_id` của item ⇒ lệch ⇒ 422. `POST /sources`: `canonical_url_hash` do **server** tính từ `origin_url` chuẩn hoá; trùng ⇒ trả **200 + bản ghi cũ** (dedupe tự nhiên theo unique `(domain_id, canonical_url_hash)`), không 409 |
| PATCH `/sources/{sid}` | Chỉ `status`, `rejected_reason`, `tier`, `is_primary`, `license_note`. `REJECTED` đòi `rejected_reason` |
| Prompt injection | Mọi trả về text nguồn kèm `is_untrusted: true`. Frontend/agent **không** được đưa giá trị này vào tên file, đường dẫn hay tham số subprocess (`TARGET_ARCHITECTURE §11`) |
| Lỗi riêng | `CLAIM_CONFLICT_UNRESOLVED` (khi gate Research Ready hỏi), `UNIQUE_VIOLATION`, `NOT_FOUND` |

---

### 6.9 `/api/v1/content/:id/artifacts`

**Metadata only.** Media **không** upload và **không** đi qua API (`TARGET_ARCHITECTURE §0.3`).
API **không** phục vụ byte của `.mp4`/`.wav` — không có endpoint download, không có signed URL ở MVP.

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/content/{id}/artifacts` | GET | BOTH | READONLY | — | — | 600/p |
| `/artifacts/{aid}` | GET | BOTH | READONLY | — | — | 300/p |
| `/artifacts/{aid}/retention` | PATCH | FE | ADMIN | ✅ | ✅ | 120/p |
| `/artifacts/{aid}/verify` | POST | FE | EDITOR | ✅ | ✅ | 30/p |

```ts
export const ArtifactOut = z.object({
  id: Uuid, build_job_id: Uuid, job_attempt_id: Uuid, content_revision_id: Uuid,
  revision_no: z.number().int(),                                   // derived
  role: z.enum(['AUDIO_WAV','SUBTITLE_SRT','SUBTITLE_ASS','TIMING_JSON','VIDEO_RAW','VIDEO_FINAL',
                'THUMBNAIL','SHOT_LIST','SEO_JSON','PACKAGE_EXPORT']),
  storage_backend: z.enum(['LOCAL','BLOB']),
  worker_machine_id: Uuid, worker_name: z.string(),                // derived
  local_path: z.string().nullable(), blob_url: z.null(),           // luôn null ở MVP
  sha256: Sha256, byte_size: z.number().int(), mime_type: z.string(),
  artifact_version: z.number().int(), created_by_kind: z.string(), created_at: Ts,
  checksum_verified_at: Ts.nullable(),
  verification_status: z.enum(['UNVERIFIED','VERIFIED','MISMATCH']),
  storage_state: z.enum(['PRESENT','PRUNED','MISSING']),
  retention_status: z.enum(['KEEP','PRUNABLE','PRUNED']),
  promotion_state: z.enum(['PROVISIONAL','PROMOTED','SUPERSEDED']),
  is_publishable: z.boolean(),   // derived = promotion_state==='PROMOTED' && storage_state==='PRESENT'
});
export const RetentionPatch = z.object({ retention_status: z.enum(['KEEP','PRUNABLE']) }).strict();
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | Cursor `(created_at DESC, id)`; 25/100 |
| Filter | `role[]`, `promotion_state[]` (mặc định **`PROMOTED`** — xem dưới), `storage_state[]`, `verification_status[]`, `content_revision_id`, `build_job_id`, `worker_machine_id` |
| Sort | `-created_at`, `role` |
| **Mặc định lọc** | List **mặc định chỉ trả `promotion_state='PROMOTED'`**. Muốn thấy bản thử ⇒ `?promotion_state=PROVISIONAL`. Lý do: TTS/video **không tất định** — retry sinh hash khác là bình thường; hiển thị lẫn lộn PROVISIONAL/PROMOTED khiến người dùng chọn nhầm bản để publish (`API_AND_WORKER_PROTOCOL §6.1`) |
| Validation | `retention_status` chỉ đổi được `KEEP ↔ PRUNABLE`; đặt `PRUNED` qua API ⇒ 422 (chỉ worker/reaper đặt được). `promotion_state` **không** sửa được qua User API |
| `verify` | **Enqueue** kiểm tra checksum ở worker → **202**. Server không đọc được đĩa local ⇒ không tự verify được. **[ASSUMPTION → §14 A-4]**: job allowlist `§9` **không có** `VERIFY_ARTIFACT`; hoặc mở rộng allowlist, hoặc gộp vào `EXPORT_PACKAGE`. **Khuyến nghị: hoãn endpoint này khỏi MVP** (`501 NOT_IMPLEMENTED`) thay vì mở allowlist đóng |
| Lỗi riêng | `ARTIFACT_NOT_PROMOTED` (khi endpoint khác tham chiếu), `NOT_FOUND` |
| Ghi chú | Ghi artifact **chỉ** qua `POST /api/worker/jobs/{id}/artifacts` (`API_AND_WORKER_PROTOCOL §5.3`). User API **read-mostly** |

---

### 6.10 `/api/v1/calendar`

⚠️ **`calendar_entry` thuộc phase "Sau (P1b)"** (`DATA_MODEL_PLAN §0.0`). Ở MVP, calendar là
**view dẫn xuất thuần** từ `content_item.planned_date` / `publish_date` / `status` / `priority` +
`publish_record.scheduled_publish_at`. Không có bảng riêng, không có sự kiện tự do.

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/calendar` | GET | FE | READONLY | — | — | 300/p |
| `/calendar/entries/{content_item_id}` | PATCH | FE | EDITOR | — (If-Match) | ✅ | 120/p |
| `/calendar/conflicts` | GET | FE | READONLY | — | — | 120/p |

```ts
export const CalendarQuery = z.object({
  from: DateOnly, to: DateOnly,                       // BẮT BUỘC cả hai
  channel_id: z.array(Uuid).max(20).optional(),
  format: z.enum(['LONG','SHORT']).optional(),
  status: z.array(ContentStatus).max(20).optional(),
  bucket: z.enum(['PLANNED','PUBLISH','BOTH']).default('BOTH'),
}).strict();
export const CalendarDay = z.object({
  date: DateOnly,
  planned: z.array(CalendarItem), published: z.array(CalendarItem),
  counts: z.object({ planned: z.number().int(), published: z.number().int(),
                     blocked: z.number().int(), building: z.number().int() }),
});
export const CalendarItem = z.object({    // projection cực gọn — lịch có thể có hàng trăm mục
  content_item_id: Uuid, channel_id: Uuid, channel_label: z.string(),
  format: z.enum(['LONG','SHORT']), topic: z.string().max(300), status: ContentStatus,
  priority: z.number().int(), has_active_approval: z.boolean(),
  live_job_count: z.number().int(), scheduled_publish_at: Ts.nullable(),
});
export const CalendarResponse = z.object({
  days: z.array(CalendarDay), range: z.object({ from: DateOnly, to: DateOnly, days: z.number().int() }),
  totals: z.object({ planned: z.number().int(), published: z.number().int() }),
  truncated_days: z.array(DateOnly),      // ngày bị cắt vì vượt max_items_per_day
});
export const CalendarPatch = z.object({
  planned_date: DateOnly.nullable(), priority: z.number().int().min(0).max(100).optional(),
}).strict();
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | **Không cursor** — bounded window. `to - from` tối đa **92 ngày** (một quý); vượt ⇒ **400 `RANGE_TOO_WIDE`** |
| Giới hạn hàng | Tối đa **60 mục/ngày**; vượt ⇒ cắt + liệt kê ngày đó trong `truncated_days` (client gọi `/content?planned_date=…` để xem hết) |
| Filter | `channel_id[]`, `format`, `status[]`, `bucket` |
| Sort | Cố định: theo ngày, trong ngày theo `-priority, topic` |
| Aggregate | `counts` mỗi ngày + `totals` — tính bằng **một** truy vấn `GROUP BY`, không N+1 |
| Múi giờ | Server nhóm theo **ngày UTC**. Trả kèm `channel.timezone`; client tự dịch. Server **không** nhóm theo timezone kênh — làm vậy sẽ khiến kết quả đổi theo DST và không cache được |
| Validation PATCH | Chỉ `planned_date`, `priority`. Đặt `planned_date` cho item `PUBLISHED`/`ARCHIVED` ⇒ 409 `INVALID_STATE_TRANSITION` |
| `conflicts` | *derived* — cùng `channel_id` + cùng `planned_date` + cùng `format` > 1 mục ⇒ cảnh báo. Chỉ **cảnh báo**, không chặn |
| Realtime | **Không cần** (§11) |

---

### 6.11 `/api/v1/analytics`

**Chỉ đọc.** Mọi ghi đi qua `POST /api/worker/analytics/snapshots` (`API_AND_WORKER_PROTOCOL §8.5`);
Vercel Cron chỉ **enqueue** (`/api/cron/enqueue-analytics`) vì token YouTube nằm ở máy local.

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/analytics/summary` | GET | FE | READONLY | — | — | 300/p |
| `/analytics/channels/{id}/daily` | GET | BOTH | READONLY | — | — | 300/p |
| `/analytics/videos/{id}/daily` | GET | BOTH | READONLY | — | — | 300/p |
| `/analytics/videos/{id}/traffic-sources` | GET | FE | READONLY | — | — | 300/p |
| `/analytics/top-videos` | GET | FE | READONLY | — | — | 300/p |
| `/analytics/content-performance` | GET | FE | READONLY | — | — | 120/p |
| `/analytics/freshness` | GET | FE | READONLY | — | — | 300/p |

```ts
export const AnalyticsWindow = z.object({
  from: DateOnly, to: DateOnly,                        // BẮT BUỘC
  granularity: z.enum(['DAY','WEEK','MONTH']).default('DAY'),
  metrics: z.array(z.enum(['views','estimated_minutes_watched','average_view_duration_seconds',
    'average_view_percentage_bp','impressions','impression_ctr_bp','likes','comments','shares',
    'subscribers_gained','subscribers_lost'])).max(11).optional(),
  as_of: Ts.optional(),                                // đọc bản ta TỪNG thấy tại thời điểm này (SCD-2)
  limit: z.coerce.number().int().min(1).max(400).default(100),
  cursor: z.string().optional(),
}).strict();
export const DailyMetricRow = z.object({
  metric_date: DateOnly,
  views: z.number().int(), estimated_minutes_watched: z.number().int(),
  average_view_duration_seconds: z.number().int().nullable(),
  average_view_percentage_bp: Bp.nullable(),
  impressions: z.number().int().nullable(), impression_ctr_bp: Bp.nullable(),
  likes: z.number().int(), comments: z.number().int(), shares: z.number().int(),
  subscribers_gained: z.number().int(), subscribers_lost: z.number().int(),
  revision_no: z.number().int(), synced_at: Ts,        // SCD-2: số này đã bị hiệu chỉnh mấy lần
});
export const AnalyticsSeries = z.object({
  subject: z.object({ kind: z.enum(['CHANNEL','VIDEO']), id: Uuid, label: z.string() }),
  granularity: z.enum(['DAY','WEEK','MONTH']),
  rows: z.array(DailyMetricRow),
  coverage: z.object({                                  // TRUNG THỰC về lỗ hổng dữ liệu
    requested_days: z.number().int(), present_days: z.number().int(),
    missing_dates: z.array(DateOnly).max(60),
    incomplete_partitions: z.number().int(),            // analytics_sync_partition.is_complete=false
    provisional_until: DateOnly.nullable(),             // 72h gần nhất: YouTube còn hiệu chỉnh
  }),
  page: Page,
});
export const AnalyticsFreshness = z.object({
  channel_id: Uuid, last_complete_date: DateOnly.nullable(), last_synced_at: Ts.nullable(),
  running_sync_run_id: Uuid.nullable(),
  stale_hours: z.number().int().nullable(), has_failed_partitions: z.boolean(),
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | Cursor keyset `(metric_date DESC)`; `limit` **100/400** — cao hơn mặc định vì hàng rất nhẹ (~200 B) ⇒ 400 hàng ≈ 80 KB |
| Cửa sổ | `to - from` tối đa **400 ngày** (`DAY`), **1095 ngày** (`WEEK`/`MONTH`); vượt ⇒ **400 `RANGE_TOO_WIDE`** |
| Filter | `/top-videos`: `channel_id`, `is_short`, `metric` (khoá sắp xếp), `min_views`. `/content-performance`: `channel_id`, `format`, `status[]` |
| Sort | Cố định `-metric_date` cho series; `/top-videos` sort theo `metric` đã chọn |
| `with_total` | **Cấm** ⇒ `400 TOTAL_NOT_SUPPORTED` |
| **SCD-2** | Mặc định trả **bản mới nhất** (`video_daily_metric`). `?as_of=<ts>` đọc từ `_history` để trả "số ta từng thấy tại thời điểm đó". `revision_no` cho biết hàng đã bị hiệu chỉnh mấy lần |
| Tính tạm thời | 72 giờ gần nhất YouTube còn hiệu chỉnh hồi tố ⇒ `coverage.provisional_until` bắt buộc có mặt. Hợp đồng **cấm** trả số gần nhất mà không kèm cờ này |
| ⚠️ Nguồn dữ liệu | Hàm hiện có `youtube_analytics.get_video_analytics()` **không truyền `dimensions`** ⇒ trả tổng gộp cả khoảng (`DATA_MODEL_PLAN §8`). API này **chỉ** phục vụ dữ liệu đã normalize theo `dimensions=day` và map theo `columnHeaders` |
| `/analytics/summary` | *derived* — theo `channel_id[]` + cửa sổ: tổng views, watch-time, CTR trung bình có trọng số, Δ so với cửa sổ liền trước cùng độ dài. Một truy vấn aggregate |
| `/analytics/content-performance` | Join `content_item → video → video_daily_metric`, trả `{content_item_id, topic, format, published_at, views_7d, views_28d, ctr_bp, avp_bp, latest_overall_score_bp}` — đây là bảng nối "chất lượng dự đoán ↔ hiệu quả thực tế" |
| Lỗi riêng | `RANGE_TOO_WIDE`, `TOTAL_NOT_SUPPORTED`, `NOT_FOUND` |

---

### 6.12 `/api/v1/recommendations`

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/recommendations/latest` | GET | FE | READONLY | — | — | 300/p |
| `/recommendations/runs` | GET | BOTH | READONLY | — | — | 300/p |
| `/recommendations/runs` | POST | FE | EDITOR | ✅ | ✅ | 10/p |
| `/recommendations/runs/{id}` | GET | BOTH | READONLY | — | — | 300/p |
| `/recommendations/runs/{id}/items` | GET | BOTH | READONLY | — | — | 300/p |
| `/recommendations/runs/{id}/items/{iid}/promote` | POST | FE | EDITOR | ✅ | ✅ | 60/p |
| `/recommendations/accuracy` | GET | FE | READONLY | — | — | 120/p |

```ts
export const RecommendationRun = z.object({
  id: Uuid, channel_id: Uuid, algorithm_version_id: Uuid,
  algorithm_key: z.string(), algorithm_version: z.string(),          // derived
  computed_at: Ts, input_window_start: DateOnly, input_window_end: DateOnly,
  input_snapshot_hash: Sha256, item_count: z.number().int(),         // derived
});
export const RecommendationItem = z.object({
  id: Uuid, recommendation_run_id: Uuid, rank: z.number().int(),
  content_item_id: Uuid.nullable(), topic_candidate: z.string().nullable(),
  content_topic: z.string().nullable(),                              // derived khi có content_item_id
  total_score_bp: Bp, breakdown: z.unknown(),                        // jsonb
  missing_data: z.unknown(),                                         // jsonb — vì sao điểm chưa chắc chắn
  predicted_metrics: z.unknown().nullable(), actual_metrics: z.unknown().nullable(),
  compared_at: Ts.nullable(),
});
export const RecommendationRunCreate = z.object({
  channel_id: Uuid, algorithm_version_id: Uuid.optional(),
  input_window_start: DateOnly, input_window_end: DateOnly,
}).strict();
export const RecommendationPromote = z.object({    // biến gợi ý thành content_item thật
  topic: z.string().min(3).max(300).optional(),    // mặc định lấy topic_candidate
  format: z.enum(['LONG','SHORT']), planned_date: DateOnly.optional(),
}).strict();
export const RecommendationAccuracy = z.object({   // predicted vs actual
  channel_id: Uuid, compared_items: z.number().int(),
  buckets: z.array(z.object({ metric: z.string(), mape_bp: Bp.nullable(),
    over_predicted: z.number().int(), under_predicted: z.number().int() })),
  window: z.object({ from: DateOnly, to: DateOnly }),
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | `runs`: cursor `(computed_at DESC, id)`, 25/100. `items`: cursor `(rank ASC)`, **50/200** |
| Filter | `runs`: `channel_id`, `algorithm_version_id`, `computed_at[gte\|lt]`. `items`: `has_content_item` (bool), `total_score_bp[gte]` |
| Sort | `runs`: `-computed_at`. `items`: `rank` (cố định — thứ hạng là bản chất của dữ liệu) |
| Include | `breakdown`, `missing_data`, `predicted_metrics`, `actual_metrics` — jsonb, **không** trong projection mặc định của list |
| **Nơi tính** | ⚠️ Job allowlist `TARGET_ARCHITECTURE §9` **đóng** và **không có** job type recommendation. Hai lựa chọn: (a) **tính trong server route** bằng SQL aggregate thuần trên Neon (đọc `video_daily_metric` + `score_run` + `content_item`) — khả thi vì dữ liệu nhỏ và phải trả < 10s; (b) mở rộng allowlist. **Khuyến nghị (a)** — giữ allowlist đóng là control chống RCE, không nên nới vì tiện. **[ASSUMPTION → §14 A-5]** |
| Timeout | Nếu (a): route phải hoàn tất < 10s; vượt ⇒ **504 `FUNCTION_TIMEOUT`** và **không** ghi `recommendation_run` dở dang (transaction) |
| `promote` | Tạo `content_item` mới với `origin='HUB_IDEA'`; ghi ngược `recommendation_item.content_item_id`. Promote lần hai ⇒ trả **200 + item cũ** (idempotent theo `recommendation_item.id`) |
| `accuracy` | Chỉ tính trên item có **cả** `predicted_metrics` và `actual_metrics` (`compared_at IS NOT NULL`); trả `compared_items` để người đọc biết mẫu lớn cỡ nào — **cấm** trả chỉ số chính xác mà giấu cỡ mẫu |
| Lỗi riêng | `RANGE_TOO_WIDE`, `FUNCTION_TIMEOUT`, `NOT_FOUND` |

---

### 6.13 `/api/v1/workers`

Đây là **mặt quản trị** của worker (người dùng nhìn vào worker). Mặt còn lại — worker tự đăng ký,
xoay token, khai báo capability — nằm ở `/api/worker/*`, `API_AND_WORKER_PROTOCOL.md §3`.

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/workers` | GET | FE | `ADMIN*` | — | — | 300/p |
| `/workers/{id}` | GET | FE | `ADMIN*` | — | — | 300/p |
| `/workers/{id}` | PATCH | FE | `ADMIN*` | ✅ | ✅ | 60/p |
| `/workers/{id}/tokens` | GET | FE | `ADMIN*` | — | — | 120/p |
| `/workers/{id}/tokens/{tid}/revoke` | POST | FE | `ADMIN*` | ✅ | ✅ | 30/p |
| `/workers/enrollment-codes` | POST | FE | `ADMIN*` | ✅ | ✅ | 10/p |
| `/workers/enrollment-codes` | GET | FE | `ADMIN*` | — | — | 120/p |
| `/workers/{id}/jobs` | GET | FE | `ADMIN*` | — | — | 300/p |

```ts
export const WorkerMachine = z.object({
  id: Uuid, name: z.string(), os: z.string(), arch: z.string(), hostname: z.string().nullable(),
  agent_version: z.string().nullable(), capabilities: z.array(JobType),
  capability_detail: z.unknown().nullable(),          // ?include=capability_detail
  status: z.enum(['ACTIVE','DISABLED']),
  registered_at: Ts, last_seen_at: Ts.nullable(),
  // derived
  liveness: z.enum(['ONLINE','STALE','OFFLINE','DISABLED']),   // ngưỡng theo heartbeat_interval
  seconds_since_seen: z.number().int().nullable(),
  live_job_count: z.number().int(), running_job_ids: z.array(Uuid).max(10),
  active_token_count: z.number().int(), next_token_expiry: Ts.nullable(),
});
export const WorkerTokenMeta = z.object({             // KHÔNG BAO GIỜ có giá trị token
  id: Uuid, worker_machine_id: Uuid, token_prefix: z.string(),
  issued_at: Ts, expires_at: Ts.nullable(), revoked_at: Ts.nullable(), last_used_at: Ts.nullable(),
  state: z.enum(['ACTIVE','EXPIRED','REVOKED']),      // derived
});
export const WorkerPatch = z.object({ status: z.enum(['ACTIVE','DISABLED']) }).strict();
export const EnrollmentCodeCreate = z.object({
  label: z.string().max(100), ttl_minutes: z.number().int().min(1).max(60).default(15),
}).strict();
export const EnrollmentCodeOut = z.object({
  id: Uuid, code: z.string().nullable(),   // hiển thị MỘT lần khi tạo; GET sau đó luôn null
  label: z.string(), expires_at: Ts, used_at: Ts.nullable(), used_by_machine_id: Uuid.nullable(),
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | Cursor `(last_seen_at DESC NULLS LAST, id)`; 25/100 (thực tế 1–3 máy) |
| Filter | `status`, `liveness`, `capability` (một `JobType`) |
| Sort | `-last_seen_at` (mặc định), `name` |
| `liveness` *(derived)* | `DISABLED` nếu `status='DISABLED'`; `ONLINE` nếu `now - last_seen_at ≤ 2× heartbeat_interval`; `STALE` nếu ≤ 10×; `OFFLINE` còn lại. Ngưỡng là **hằng server**, client không tự tính (chống clock skew — `API_AND_WORKER_PROTOCOL §1`) |
| `PATCH status=DISABLED` | **Không** huỷ job đang chạy; chỉ chặn claim mới. Muốn dừng ⇒ `POST /jobs/{id}/cancel` (§6.14). Hợp đồng phải nói rõ để người dùng không tưởng đã dừng |
| Token | Endpoint **chỉ** trả metadata (`token_prefix`, thời hạn). Giá trị token hiển thị **một lần** duy nhất tại `POST /api/worker/register` / `…/token/rotate`. Revoke có hiệu lực **tức thì**; token đang trong grace 24h cũng bị giết |
| Alias | `API_AND_WORKER_PROTOCOL §3.2` ghi `POST /api/worker/token/{id}/revoke *(ADMIN, User API)*`. **Đường dẫn chuẩn là `/api/v1/workers/{id}/tokens/{tid}/revoke`**; giữ alias cũ trả `308` để không phá tài liệu đã phát hành |
| Enrollment code | Một lần dùng, TTL ≤ 60 phút (mặc định 15). Sinh bằng CSPRNG, lưu **hash**; `code` trả về đúng **một lần** |
| Bảo mật | Cảnh báo khi cùng `worker_token` được dùng từ **hai IP** trong cửa sổ ngắn ⇒ hiển thị ở `WorkerMachine` **[ASSUMPTION → §14 A-6]** (cần cột/bảng theo dõi, `DATA_MODEL_PLAN` chưa có) |
| Lỗi riêng | `FORBIDDEN` (không phải ADMIN), `INVALID_STATE_TRANSITION` (revoke token đã revoke) |

---

### 6.14 `/api/v1/jobs`

Nhóm duy nhất có nhu cầu **gần realtime** (§11). Đây là mặt người dùng của `build_job`;
vòng đời thực thi thuộc Worker API (`API_AND_WORKER_PROTOCOL §4–§7`).

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/jobs` | GET | BOTH | READONLY | — | — | 600/p |
| `/jobs` | POST | BOTH | EDITOR¹ | ✅ | ✅ | 30/p |
| `/jobs/{id}` | GET | BOTH | READONLY | — | — | 900/p² |
| `/jobs/{id}/cancel` | POST | BOTH | EDITOR | ✅ | ✅ | 60/p |
| `/jobs/{id}/retry` | POST | FE | EDITOR | ✅ | ✅ | 30/p |
| `/jobs/{id}/attempts` | GET | BOTH | READONLY | — | — | 300/p |
| `/jobs/{id}/events` | GET | FE | READONLY | — | — | 900/p² |
| `/jobs/{id}/logs` | GET | FE | READONLY | — | — | 900/p² |
| `/jobs/stream-cursor` | GET | FE | READONLY | — | — | 900/p² |

¹ `BUILD_*` cần `EDITOR` hoặc `APPROVER` (ma trận §11) · ² ngưỡng cao vì đây là endpoint **polling**.

```ts
export const JobSummary = z.object({
  id: Uuid, channel_id: Uuid.nullable(), content_item_id: Uuid.nullable(),
  content_revision_id: Uuid.nullable(), revision_no: z.number().int().nullable(),   // derived
  content_topic: z.string().nullable(),                                             // derived
  job_type: JobType, status: JobStatus, priority: z.number().int(),
  claim_count: z.number().int(), execution_attempt: z.number().int(),
  quota_deferral_count: z.number().int(), max_attempts: z.number().int(),
  required_capability: z.string().nullable(),
  leased_by: Uuid.nullable(), leased_by_name: z.string().nullable(),                // derived
  lease_until: Ts.nullable(), not_before: Ts.nullable(), cancel_requested: z.boolean(),
  created_at: Ts, started_at: Ts.nullable(), finished_at: Ts.nullable(),
  error_code: z.string().nullable(), error_message: z.string().nullable(),          // đã redact
  // derived — cho thanh tiến độ mà KHÔNG cần realtime
  progress_percent: z.number().int().min(0).max(100).nullable(),
  stage: z.string().nullable(), last_heartbeat_at: Ts.nullable(),
  duration_seconds: z.number().int().nullable(), is_terminal: z.boolean(),
});
export const JobDetail = JobSummary.extend({
  params: z.unknown(),                       // jsonb đã validate strict lúc tạo
  attempts: z.array(JobAttemptOut),          // ?include=attempts
  artifacts: z.array(ArtifactOut),           // ?include=artifacts (chỉ PROMOTED)
});
export const JobAttemptOut = z.object({
  id: Uuid, attempt_no: z.number().int(), worker_machine_id: Uuid, worker_name: z.string(),
  lease_token_prefix: z.string(),            // KHÔNG trả lease_token đầy đủ
  started_at: Ts, ended_at: Ts.nullable(),
  outcome: z.enum(['SUCCEEDED','FAILED','EXPIRED','CANCELLED']).nullable(),  // null = đang chạy
});
export const JobCreate = z.object({
  job_type: JobType,
  content_item_id: Uuid.optional(), content_revision_id: Uuid.optional(),
  channel_id: Uuid.optional(),
  priority: z.number().int().min(0).max(100).default(50),
  not_before: Ts.optional(),
  params: z.unknown(),                       // validate bằng schema RIÊNG theo job_type, .strict()
}).strict();
export const JobEventOut = z.object({
  id: Uuid, seq: z.number().int(), occurred_at: Ts, event_type: z.string(),
  job_attempt_id: Uuid.nullable(), worker_machine_id: Uuid.nullable(),
  payload: z.unknown(),                      // ĐÃ redact hai lớp
});
export const JobLogLine = z.object({
  seq: z.number().int(), ts: Ts, level: z.enum(['DEBUG','INFO','WARN','ERROR']), msg: z.string(),
  job_attempt_id: Uuid.nullable(),
});
export const JobLogPage = z.object({
  lines: z.array(JobLogLine), next_after_seq: z.number().int().nullable(),
  has_more: z.boolean(), truncated: z.boolean(), job_status: JobStatus,
  poll_after_ms: z.number().int(),           // server điều khiển nhịp poll — xem §11
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | `jobs`: cursor `(priority DESC, created_at ASC, id)` để khớp index `(status, priority DESC, not_before)`; 25/100. `events`/`logs`: cursor **`after_seq`** (số nguyên tăng dần), 200/500 dòng |
| Filter | `status[]`, `job_type[]`, `channel_id[]`, `content_item_id`, `content_revision_id`, `worker_machine_id`, `error_code`, `created_at[gte\|lt]`, `is_live` (bool → `LIVE_STATUSES`) |
| Sort | `-priority` (mặc định, khớp thứ tự claim), `-created_at`, `-finished_at` |
| Include | `attempts`, `artifacts`, `params` |
| Validation POST | (a) `job_type` thuộc allowlist đóng `§9`; (b) `params` validate bằng **schema riêng cho từng `job_type`**, `.strict()` — field lạ ⇒ **422 `UNKNOWN_FIELD`**; (c) **không** field nào chứa lệnh/đường dẫn nhị phân/tham số CLI thô; (d) `BUILD_*` ⇒ revision phải `FROZEN` (J-3) ⇒ ngược lại **409 `REVISION_NOT_FROZEN`**; (e) `BUILD_*` ⇒ phải có `approval` `ACTIVE` cho revision ⇒ ngược lại **409 `APPROVAL_REQUIRED`**; (f) trùng partial unique `(content_revision_id, job_type) WHERE status ∈ LIVE_STATUSES` ⇒ **409 `DUPLICATE_JOB`** kèm `existing_job_id` |
| `cancel` | Đặt `cancel_requested=true`; **không** đổi `status` ngay. Worker thấy ở heartbeat rồi tự dọn (`API_AND_WORKER_PROTOCOL §6.3`). Job đã terminal ⇒ **409 `JOB_NOT_CANCELLABLE`**. Response nói rõ `"cancellation is cooperative"` |
| `retry` | **Tạo job MỚI**, không hồi sinh job cũ. Bộ đếm **không bao giờ giảm** (`API_AND_WORKER_PROTOCOL §4.4`) ⇒ reset counter là vi phạm bất biến. Chỉ cho `FAILED`/`CANCELLED`; kiểm lại toàn bộ điều kiện của POST. Trả `{new_job_id, source_job_id}` |
| **Redaction** | `error_message`, `params`, `payload`, log line đều đã redact **hai lớp** (worker trước khi gửi, server trước khi ghi). API **không** redact lúc đọc — nếu phải redact ở đọc nghĩa là đã ghi sai |
| `lease_token` | **Không bao giờ** xuất hiện trong response User API (chỉ `lease_token_prefix`) |
| Payload lớn | `logs` cắt ở **256 KB/trang** (khớp giới hạn lô log của worker); vượt ⇒ `truncated=true` + `next_after_seq` |
| Realtime | Có — bằng **polling**, xem §11. `poll_after_ms` do **server** quyết định |
| Lỗi riêng | `DUPLICATE_JOB`, `REVISION_NOT_FROZEN`, `APPROVAL_REQUIRED`, `JOB_NOT_CANCELLABLE`, `UNKNOWN_FIELD`, `VALIDATION_FAILED` |

**`/jobs/stream-cursor`** *(derived, cho màn hình Build queue)* — một request trả **toàn bộ trạng thái
đang sống** để frontend poll **một** endpoint thay vì N: `{ jobs_live: JobSummary[] (≤50),
counts_by_status, max_updated_at, poll_after_ms }`. Hỗ trợ `If-None-Match` ⇒ **304** khi không đổi.
Đây là thay thế trực tiếp cho WebSocket (§11).

---

### 6.15 `/api/v1/uploads` — **KHÔNG bật ở MVP**

Đây là kết luận thẳng thắn từ hai quyết định đã chốt:

| Quyết định | Hệ quả cho `/uploads` |
|---|---|
| **Media không rời máy local** (`TARGET_ARCHITECTURE §0.3`) | Không có `.mp4`/`.wav`/`.ass`/`.srt` nào cần upload. Nhu cầu upload lớn nhất (337 MB/video) **biến mất hoàn toàn** |
| **MVP không dùng Vercel Blob** (`TARGET_ARCHITECTURE §4`) | Không có backend lưu trữ nhị phân. Upload đi đâu? Không đâu cả |
| Payload text lớn nhất **194,8 KB** | Đi thẳng trong JSON body — không cần cơ chế upload riêng |

**Quy định MVP:** mọi method trên `/api/v1/uploads/*` trả **501 `NOT_IMPLEMENTED`**
với `detail` giải thích lý do. **Không** stub im lặng, **không** trả 404 (404 khiến người sau tưởng
là bug định tuyến).

**Hợp đồng đặt chỗ cho giai đoạn bật Blob** (khi `artifact.storage_backend='BLOB'` được dùng):

| Endpoint | Method | Caller | Ghi chú |
|---|---|:-:|---|
| `/uploads/tickets` | POST | FE/CLI | Cấp upload ticket (client-side upload thẳng lên Blob, **không** qua function — tránh trần 4,5 MB) |
| `/uploads/tickets/{id}/finalize` | POST | FE/CLI | Xác nhận `sha256` + `byte_size`; server đối chiếu rồi tạo/cập nhật `artifact.blob_url`/`blob_key` |

```ts
export const UploadTicketCreate = z.object({
  purpose: z.enum(['ARTIFACT','EVIDENCE_BUNDLE','IMPORT_PAYLOAD']),
  content_type: z.string().max(100),          // allowlist bắt buộc
  byte_size: z.number().int().min(1).max(50_000_000),
  sha256: Sha256,                              // BẮT BUỘC khai trước — checksum-first
  artifact_role: z.string().optional(),
}).strict();
```
Ràng buộc đã định sẵn: allowlist content-type, giới hạn kích thước, **checksum bắt buộc**
(`TARGET_ARCHITECTURE §11`), ticket TTL ngắn, một ticket dùng một lần.
**Không** implement cho tới khi Blob được bật — và đó **không** thuộc MVP.

---

### 6.16 `/api/v1/import`

⚠️ **Import chủ yếu là endpoint của CLI, không phải của frontend.** Lý do vật lý: dữ liệu legacy nằm
trên **filesystem local** (`registry.json`, package Content-Creator, `analytics_reviews/`,
`.youtube_channels/`, `output/`) — Vercel function **không đọc được**. CLI đọc, chuẩn hoá, rồi **đẩy lên**.
Frontend chỉ **đọc báo cáo**.

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/import/batches` | POST | **CLI** | `ADMIN*` | ✅ | ✅ | 10/p |
| `/import/batches/{id}/records` | POST | **CLI** | `ADMIN*` | ✅ | ✅ | 120/p |
| `/import/batches/{id}/finalize` | POST | **CLI** | `ADMIN*` | ✅ | ✅ | 30/p |
| `/import/batches/{id}/report` | GET | BOTH | `ADMIN*` | — | — | 300/p |
| `/import/batches` | GET | BOTH | `ADMIN*` | — | — | 300/p |
| `/import/batches/{id}` | GET | BOTH | `ADMIN*` | — | — | 300/p |
| `/import/batches/{id}/records` | GET | BOTH | `ADMIN*` | — | — | 300/p |

#### Hoàn tác import — **không có endpoint ở MVP**

> Rollback dùng **Neon branch / point-in-time restore** (`LEGACY_IMPORT_AND_SYNC_PLAN §6`), là thao
> tác **vận hành** có runbook, **không** phải endpoint. Lý do: cơ chế gỡ ở tầng ứng dụng đòi hỏi sổ
> cái thực thể, hash từng dòng và projection theo entity — phức tạp hơn giá trị nó mang lại cho một
> lô **insert-only** chạy trước khi có dữ liệu vận hành thật.
> Mã lỗi `IMPORT_ROLLBACK_BLOCKED` và trạng thái `ROLLING_BACK`/`ROLLED_BACK` **đã bị gỡ**.


| Truy vấn | Giá trị |
|---|---|
| Pagination | `batches`: cursor `(started_at DESC, id)`, 25/100. `records`: cursor `(id)`, **100/500** |
| Filter | `batches`: `source_kind`, `mode`, `status` (`ImportBatchStatus`), `started_at[gte\|lt]`. `records`: `outcome[]`, `entity_type`, `legacy_ref` (prefix) |
| Sort | `-started_at`; records: `id` |
| Idempotency | **Hai tầng**: (a) `Idempotency-Key` cho HTTP replay; (b) **unique `(import_batch_id, legacy_ref)`** + **unique `legacy_id_map(legacy_kind, legacy_id)`** ⇒ chạy lại toàn bộ import không tạo bản trùng. Đẩy lại lô đã đẩy ⇒ trả `SKIPPED_DUPLICATE`, **không** 409 |
| `DRY_RUN` | **Không** ghi entity thật, **không** ghi `legacy_id_map`; chỉ ghi `import_record` + `report`. Đây là cơ chế bắt buộc trước mọi `APPLY` (`TARGET_ARCHITECTURE §7` Phase A) |
| `finalize` | Chốt `finished_at`, `status`, tổng hợp `report`. Sau finalize, push thêm ⇒ **409 `INVALID_STATE_TRANSITION`** |
| `legacy-map` | `?legacy_kind=&legacy_id=` (hoặc `legacy_id[]` ≤ 200) → `{entity_type, entity_id}`. CLI dùng để **tự kiểm tra trước khi đẩy** ⇒ giảm hẳn lưu lượng |
| Payload | Lô ≤ **200 bản ghi** và ≤ **1 MB** (§13). `raw_payload_excerpt` phải là **trích đoạn**, không phải nguyên file |
| Lỗi riêng | `INVALID_STATE_TRANSITION`, `PAYLOAD_TOO_LARGE`, `VALIDATION_FAILED` |
| Frontend | Chỉ 3 endpoint GET. Không có nút "import" nào ở frontend gọi được trực tiếp — vì server không thấy đĩa |

---

### 6.17 `/api/v1/sync`

Hai loại đồng bộ khác hẳn nhau, **không gộp**:
(1) **Analytics sync** — kéo số liệu từ YouTube (worker giữ token);
(2) **Reconciliation** — đối chiếu file ↔ DB trong lộ trình A→B→C→D (`TARGET_ARCHITECTURE §7`).

| Endpoint | Method | Caller | Role | Idem | Audit | RL |
|---|---|:-:|:-:|:-:|:-:|:-:|
| `/sync/analytics` | POST | BOTH | EDITOR | ✅ | ✅ | 10/p |
| `/sync/runs` | GET | BOTH | READONLY | — | — | 300/p |
| `/sync/runs/{id}` | GET | BOTH | READONLY | — | — | 300/p |
| `/sync/runs/{id}/partitions` | GET | BOTH | READONLY | — | — | 300/p |
| `/sync/status` | GET | FE | READONLY | — | — | 600/p |
| `/sync/reconciliation` | GET | BOTH | `ADMIN*` | — | — | 120/p |
| `/sync/reconciliation` | POST | **CLI** | `ADMIN*` | ✅ | ✅ | 10/p |

```ts
export const SyncAnalyticsRequest = z.object({
  channel_id: Uuid, from: DateOnly, to: DateOnly,
  report_types: z.array(z.enum(['CHANNEL_DAILY','VIDEO_DAILY','TRAFFIC_SOURCE_DAILY'])).min(1),
  video_ids: z.array(Uuid).max(200).optional(),
  force_refetch: z.boolean().default(false),     // bỏ qua checkpoint, kéo lại cả cửa sổ
}).strict();
export const SyncRun = z.object({
  id: Uuid, channel_id: Uuid, started_at: Ts, finished_at: Ts.nullable(),
  status: z.string(), initiated_by_kind: z.enum(['USER','CRON']),
  partition_counts: z.record(z.string(), z.number().int()),   // derived
  complete_partitions: z.number().int(), total_partitions: z.number().int(),
});
export const SyncPartition = z.object({
  id: Uuid, channel_id: Uuid, report_type: z.string(), video_id: Uuid.nullable(),
  partition_date_start: DateOnly, partition_date_end: DateOnly,
  dimensions: z.string(), filters: z.string().nullable(), reporting_timezone: z.string(),
  request_hash: Sha256, response_hash: Sha256.nullable(),
  checkpoint_date: DateOnly.nullable(), is_complete: z.boolean(),
  status: z.string(), attempt: z.number().int(),
});
export const SyncStatus = z.object({           // derived, cho dashboard
  channels: z.array(z.object({
    channel_id: Uuid, label: z.string(),
    last_complete_date: DateOnly.nullable(), stale_hours: z.number().int().nullable(),
    running: z.boolean(), failed_partitions: z.number().int(),
    next_cron_at: Ts.nullable(),
  })),
});
export const ReconciliationReport = z.object({  // Phase A/B — TARGET_ARCHITECTURE §7
  id: Uuid, computed_at: Ts, phase: z.enum(['A','B','C','D']),
  scope: z.string(), compared: z.number().int(),
  matched: z.number().int(), file_only: z.number().int(),
  db_only: z.number().int(), content_mismatch: z.number().int(),
  drift_zero: z.boolean(),                      // điều kiện chuyển phase
  samples: z.array(z.object({ legacy_ref: z.string(), kind: z.string(),
                              detail: z.string() })).max(50),
});
```

| Truy vấn | Giá trị |
|---|---|
| Pagination | `runs`: cursor `(started_at DESC, id)`, 25/100. `partitions`: cursor `(partition_date_start DESC, id)`, **100/400** |
| Filter | `runs`: `channel_id`, `status`, `started_at[gte\|lt]`. `partitions`: `report_type`, `status`, `is_complete`, `video_id` |
| Sort | `-started_at`; partitions: `-partition_date_start` |
| `POST /sync/analytics` | **Chỉ enqueue** job `SYNC_ANALYTICS` → **202**. Server **không** gọi YouTube (token ở local, `TARGET_ARCHITECTURE §3`). Cửa sổ `to - from` tối đa **400 ngày** |
| Chặn chồng | Partial unique `(channel_id, report_type, video_id, partition_date_start) WHERE status='RUNNING'` ⇒ trùng ⇒ **409 `DUPLICATE_JOB`** kèm `existing_run_id`. Đây là cùng cơ chế chặn cron chạy chồng |
| Bất biến hiển thị | `is_complete=true` **chỉ khi** `checkpoint_date = partition_date_end`. API **không** suy diễn "hoàn tất" từ `status` |
| `force_refetch` | Đòi `ADMIN`; ghi `audit_event` riêng (tốn quota YouTube) |
| Reconciliation | `POST` do **CLI** đẩy kết quả đối chiếu (CLI mới đọc được file). `GET` cho người dùng xem. `drift_zero` là **cổng** để chuyển Phase A→B (`TARGET_ARCHITECTURE §7`: 0 khác biệt trong 7 ngày) |
| ⚠️ Khoảng trống schema | `DATA_MODEL_PLAN` **chưa có** bảng reconciliation report. **[ASSUMPTION → §14 A-7]** — hoặc thêm bảng, hoặc tái dùng `import_batch` với `mode='DRY_RUN'` + `source_kind` mới. **Khuyến nghị tái dùng `import_batch`** để không mở thêm entity |
| Lỗi riêng | `DUPLICATE_JOB`, `RANGE_TOO_WIDE`, `FORBIDDEN` |
| Cron | `/api/cron/enqueue-analytics` là bản song song **cho Vercel Cron** (`CRON_SECRET`), **không** thuộc `/api/v1/*`. Cùng logic, khác auth |

---

## 7. Màn hình frontend **tương lai** → hợp đồng cần thiết

> ⚠️ **Đây KHÔNG phải thiết kế UI.** Không nói gì về layout, component, màu, thứ tự hiển thị,
> tương tác. Mỗi dòng chỉ trả lời: *màn hình đó cần gọi gì, nhận về shape nào, lọc/phân trang ra sao,
> ghi được gì, ai được vào, có cần realtime không.* Frontend sẽ được thiết kế ở **Phase 8**.

**Mọi màn hình đều gọi `GET /api/v1/auth/me` trước** để biết tập kênh + vai trò ⇒ không lặp ở bảng.

| # | Màn hình | Query cần thiết | Response shape | Pagination · Filter · Aggregate | Mutation | Permission | Realtime |
|---|---|---|---|---|---|:-:|:-:|
| 1 | **Channel dashboard** | `GET /channels`<br>`GET /channels/{id}/stats`<br>`GET /analytics/summary?channel_id=&from=&to=`<br>`GET /sync/status`<br>`GET /jobs?is_live=true&limit=10` | `Channel[]`, `ChannelStats`, `AnalyticsSummary`, `SyncStatus`, `JobSummary[]` | Không phân trang (≤10 kênh). **Aggregate:** `content_by_status`, `jobs_live`, `pending_approval`, `build_failed_24h`, Δ views vs cửa sổ trước | — | READONLY | **Không** (poll 60s là đủ) |
| 2 | **Content calendar** | `GET /calendar?from=&to=&channel_id[]=&bucket=`<br>`GET /calendar/conflicts?from=&to=` | `CalendarResponse` (`CalendarDay[]` + `CalendarItem[]` gọn) | **Bounded window ≤ 92 ngày**, không cursor. Filter: `channel_id[]`, `format`, `status[]`. **Aggregate:** `counts`/ngày, `totals`. ≤60 mục/ngày, dư ⇒ `truncated_days` | `PATCH /calendar/entries/{cid}` (`planned_date`, `priority`) — **If-Match** | đọc READONLY · ghi EDITOR | **Không** |
| 3 | **Content list** | `GET /content?channel_id[]=&status[]=&format=&q=&sort=&cursor=&with_total=1` | `Collection<ContentSummary>` | **Cursor** `(created_at DESC, id)`; 25/100. Filter: 13 field (§6.3). Sort: 4 khoá. **Aggregate:** `total` (opt-in) + `revision_count`, `latest_overall_score_bp`, `live_job_count` mỗi hàng | `POST /content`<br>`DELETE /content/{id}` | đọc READONLY · tạo EDITOR · xoá ADMIN | **Không** |
| 4 | **Content detail** | `GET /content/{id}?include=production_revision,active_approval,latest_score`<br>`GET /content/{id}/timeline?limit=25`<br>`GET /content/{id}/gates` | `ContentDetail`, `Collection<TimelineEvent>`, `GateStatus` | Timeline: cursor `(occurred_at DESC, id)`. **Aggregate:** `gates[]` với `unresolved_blockers`, `can_approve` | `PATCH /content/{id}` (If-Match)<br>`POST /content/{id}/transition` | đọc READONLY · sửa EDITOR · transition EDITOR/APPROVER | **Không** (trừ khi có job live ⇒ mượn §11) |
| 5 | **Revision history** | `GET /content/{id}/revisions?limit=20&sort=-revision_no`<br>`GET /content/{id}/revisions/diff?from=&to=` (không `fields` ⇒ chỉ tóm tắt) | `Collection<RevisionSummary>`, `RevisionDiff` (tóm tắt) | Cursor `(revision_no DESC)`; **20/50**. Filter: `status[]`, `created_by_kind`, `generator_name`. **Aggregate:** `script_chars`, `is_approved`, `is_production` mỗi hàng | — (chỉ đọc) | READONLY | **Không** |
| 6 | **Script editor** | `GET /content/{id}/revisions/{rid}?fields=audio_script,outline,hook,title_final,chapters` (ETag)<br>`GET …/diff?from=&to=&fields=audio_script` khi cần so | `RevisionFull` (sparse), `RevisionDiff` có `hunks` | Không phân trang. **Cột nặng phải xin rõ**: `audio_script` 67,8 KB. Diff cắt **512 KB/field** | `PATCH …/{rid}` (**If-Match bắt buộc**)<br>`POST …/{rid}/request-review`<br>`POST /content/{id}/revisions` (tạo bản mới) | EDITOR (chỉ `DRAFT`/`REVIEW_REQUIRED`) | **Không** — nhưng **phải** xử lý 412 vì agent có thể ghi cùng lúc |
| 7 | **SEO editor** | `GET …/revisions/{rid}?fields=seo_package,title_final,title_candidates,keywords,hashtags,description,thumbnail_concepts` | `RevisionFull` (sparse) | Không phân trang. `seo_package` jsonb **194,8 KB** — payload lớn nhất toàn hệ ⇒ tải riêng, không kèm script | `PATCH …/{rid}` (If-Match) — kèm `payload_schema_version` | EDITOR | **Không** |
| 8 | **Source viewer** | `GET /content/{id}/sources`<br>`GET /sources/{sid}/versions`<br>`GET /sources/{sid}/versions/{vid}/text?offset=&length=`<br>`GET /content/{id}/claims` | `Collection<SourceDocument>`, `Collection<SourceVersion>`, `SourceText`, `Collection<ClaimOut>` | Cursor 25/100. Text: **phân lô 256 KB**, tối đa 2 lô (max 444,9 KB). **Aggregate:** `evidence_counts`, `has_unresolved_conflict` | `POST /content/{id}/sources` (attach)<br>`DELETE …/{sid}`<br>`PATCH /sources/{sid}` (status/tier) | đọc READONLY · attach EDITOR · duyệt nguồn REVIEWER | **Không** |
| 9 | **Audit viewer** | `GET /content/{id}/audits?content_revision_id=`<br>`GET …/audits/{run_id}/findings?severity[]=&resolved=false` | `Collection<AuditRunSummary>`, `Collection<AuditFindingOut>` | Findings: cursor `(severity_rank, id)`, **50/200**. Filter: `severity[]`, `category`, `resolved`, `check_id`. **Aggregate:** `finding_counts` theo severity, `unresolved_blockers` | `POST …/findings` (thủ công)<br>`POST …/findings/{fid}/resolve`<br>`POST /content/{id}/audits` (enqueue → 202) | đọc READONLY · ghi/resolve REVIEWER | **Không** — trừ khi vừa enqueue ⇒ poll job (§11) |
| 10 | **Score breakdown** | `GET /content/{id}/scores?content_revision_id=`<br>`GET …/scores/{run_id}` (mặc định kèm `dimensions`)<br>`GET …/scores/compare?a=&b=`<br>`GET …/scores/trend?algorithm_id=` | `Collection<ScoreRunSummary>`, `ScoreRunDetail`, `ScoreCompare`, chuỗi ≤200 điểm | Cursor `(created_at DESC)`. **Aggregate:** `weighted_bp`/dimension, `recomputed_overall_bp` + `recompute_matches`, `delta_bp` vs run trước | `POST /content/{id}/scores` (enqueue → 202) | đọc READONLY · chấm lại REVIEWER | **Không** |
| 11 | **Approval screen** | `GET /content/{id}/gates`<br>`GET /content/{id}/approvals`<br>`GET …/revisions/{rid}` (bản định duyệt)<br>`GET …/audits/{run_id}` + `GET …/scores/{run_id}` (bằng chứng) | `GateStatus`, `Collection<ApprovalOut>`, `RevisionFull`, `AuditRunSummary`, `ScoreRunDetail` | Không phân trang. **Aggregate:** `can_approve`, `blocking_reasons[]`, `unresolved_blockers` — server quyết định, client **không** tự suy | `POST /auth/reauth` (step-up)<br>`POST /content/{id}/approvals` (**Idempotency-Key**)<br>`POST …/approvals/{aid}/revoke`<br>`POST …/revisions/{rid}/promote` | **APPROVER** (worker/agent tuyệt đối không) | **Không** |
| 12 | **Build queue** | `GET /jobs/stream-cursor` (**một** endpoint, `If-None-Match`)<br>`GET /jobs?status[]=&job_type[]=&cursor=` (lịch sử)<br>`GET /jobs/{id}?include=attempts` | `{jobs_live: JobSummary[≤50], counts_by_status, max_updated_at, poll_after_ms}`, `Collection<JobSummary>`, `JobDetail` | Cursor `(priority DESC, created_at, id)`; 25/100. Filter: 8 field. **Aggregate:** `counts_by_status`, `progress_percent`, `duration_seconds` | `POST /jobs`<br>`POST /jobs/{id}/cancel`<br>`POST /jobs/{id}/retry` | đọc READONLY · tạo/huỷ EDITOR (BUILD_* cần EDITOR/APPROVER) | **CÓ** — polling, §11 |
| 12b | **Job log** *(một phần Build queue)* | `GET /jobs/{id}/logs?after_seq=&limit=200` lặp lại | `JobLogPage` (`lines[]`, `next_after_seq`, `poll_after_ms`, `job_status`) | **Cursor `after_seq`** (số nguyên tăng), 200/500 dòng, cắt **256 KB/trang** | — | READONLY | **CÓ** — polling tăng dần, §11 |
| 13 | **Artifact viewer** | `GET /content/{id}/artifacts` (mặc định chỉ `PROMOTED`)<br>`GET /artifacts/{aid}`<br>`GET /jobs/{id}?include=artifacts` | `Collection<ArtifactOut>`, `ArtifactOut` | Cursor `(created_at DESC)`; 25/100. Filter: `role[]`, `promotion_state[]`, `storage_state[]`, `verification_status[]`. **Aggregate:** `is_publishable` | `PATCH /artifacts/{aid}/retention` | đọc READONLY · retention ADMIN | **Không** |
| 14 | **Analytics dashboard** | `GET /analytics/summary`<br>`GET /analytics/channels/{id}/daily?from=&to=&granularity=`<br>`GET /analytics/top-videos`<br>`GET /analytics/content-performance`<br>`GET /analytics/freshness` | `AnalyticsSummary`, `AnalyticsSeries` (+`coverage`), `Video[]`, hàng `content_performance`, `AnalyticsFreshness` | **Cửa sổ bắt buộc**, ≤400 ngày (`DAY`). Cursor `(metric_date DESC)`, **100/400**. `with_total` **cấm**. **Aggregate:** tổng, Δ cửa sổ trước, CTR có trọng số | `POST /sync/analytics` (enqueue → 202) | đọc READONLY · sync EDITOR | **Không** (dữ liệu theo ngày) |
| 15 | **Recommendation dashboard** | `GET /recommendations/latest?channel_id=`<br>`GET /recommendations/runs/{id}/items?limit=50`<br>`GET /recommendations/accuracy` | `RecommendationRun`, `Collection<RecommendationItem>`, `RecommendationAccuracy` | Cursor `rank ASC`, **50/200**. `breakdown`/`missing_data` chỉ khi `?include=`. **Aggregate:** `mape_bp`, `compared_items` (bắt buộc lộ cỡ mẫu) | `POST /recommendations/runs`<br>`POST …/items/{iid}/promote` | đọc READONLY · chạy/promote EDITOR | **Không** |
| 16 | **Worker status** | `GET /workers`<br>`GET /workers/{id}?include=capability_detail`<br>`GET /workers/{id}/tokens`<br>`GET /workers/{id}/jobs?is_live=true` | `Collection<WorkerMachine>`, `WorkerMachine`, `WorkerTokenMeta[]`, `Collection<JobSummary>` | Cursor `(last_seen_at DESC NULLS LAST)`; 25/100. **Aggregate:** `liveness`, `seconds_since_seen`, `live_job_count`, `next_token_expiry` — **server tính**, chống clock skew | `PATCH /workers/{id}` (ACTIVE/DISABLED)<br>`POST …/tokens/{tid}/revoke`<br>`POST /workers/enrollment-codes` | **ADMIN** toàn cục | **Gần** — poll 15s là đủ; §11 |

### 7.1 Ba quy tắc hợp đồng rút ra từ bảng trên

| Quy tắc | Vì sao |
|---|---|
| **Aggregate tính ở server, không ở client** | `can_approve`, `liveness`, `unresolved_blockers`, `is_publishable`, `recompute_matches` là **quyết định nghiệp vụ**. Để client tự suy ⇒ hai nơi cùng cài luật ⇒ chắc chắn lệch. Client tự suy `can_approve` rồi bấm ⇒ server vẫn 409, nhưng người dùng đã mất thời gian |
| **Cột nặng không bao giờ đi kèm miễn phí** | Màn hình 6 và 7 tách riêng chính vì `audio_script` (67,8 KB) và `seo_package` (194,8 KB) không nên tải cùng lúc. Đây là ràng buộc **hợp đồng**, không phải tối ưu tuỳ chọn |
| **Chỉ 3/16 màn hình cần cập nhật liên tục** | 12, 12b, và (nhẹ) 16. Mọi màn hình còn lại là dữ liệu do **người** hoặc **cron theo ngày** thay đổi ⇒ realtime là chi phí không có người trả (§11) |

---

## 8. Endpoint phục vụ ai — **frontend / CLI / cả hai**

Ba caller trên User API (`/api/v1/*`). Worker token **không** vào được đây (§3).

| Nhóm | Chỉ **frontend** | Chỉ **CLI** (PAT) | **Cả hai** |
|---|---|---|---|
| `/channels` | POST, PATCH, DELETE, `/members`, `/stats` | — | GET list/detail, `/credentials` |
| `/videos` | `/link`, `/metrics` | — | GET list/detail |
| `/content` | PATCH, DELETE, `/timeline`, `/derivations` | — | GET, POST, `/transition` |
| `/content/:id/revisions` | PATCH, `/request-review`, `/freeze`, `/promote`, `/diff` | — | GET list/detail, POST, `/claims`, `/manifest` |
| `/content/:id/scores` | POST (enqueue), `/compare`, `/trend` | — | GET list/detail |
| `/content/:id/audits` | POST (enqueue), `/findings` POST, `/resolve`, `/gates` | — | GET list/detail/findings |
| `/content/:id/approvals` | **toàn bộ** | — | — |
| `/content/:id/sources` | attach/detach, `PATCH /sources/{sid}`, `…/text` | `POST /sources` (CLI mới fetch được) | GET các loại, `/claims` |
| `/content/:id/artifacts` | `/retention`, `/verify` | — | GET list/detail |
| `/calendar` | **toàn bộ** | — | — |
| `/analytics` | `/summary`, `/top-videos`, `/content-performance`, `/freshness`, `/traffic-sources` | — | `/channels/{id}/daily`, `/videos/{id}/daily` |
| `/recommendations` | POST run, `/promote`, `/accuracy`, `/latest` | — | GET runs/items |
| `/workers` | **toàn bộ** (ADMIN UI) | — | — |
| `/jobs` | `/retry`, `/events`, `/logs`, `/stream-cursor` | — | GET, POST, `/cancel`, `/attempts` |
| `/uploads` | *(501 — không bật ở MVP)* | — | — |
| `/import` | GET batches/records | `POST /import/*`, `/legacy-map` | — |
| `/sync` | `/status` | `POST /sync/reconciliation` | `POST /sync/analytics`, GET runs/partitions, GET `/reconciliation` |

### 8.1 Vì sao chia như vậy

| Nguyên tắc | Hệ quả |
|---|---|
| **Endpoint nào cần đọc đĩa local ⇒ CLI** | `POST /sources` (fetch web — giữ SSRF khỏi Vercel), `POST /import/*` (đọc `registry.json`, package CC), `POST /sync/reconciliation` (so file ↔ DB). Server **không thấy** filesystem của người dùng |
| **Endpoint nào cần con người ⇒ frontend** | `/approvals`, `/freeze`, `/promote`, `/retention`, `/workers`. Đặc biệt approval: A-1 buộc `approved_by` là user thật |
| **Endpoint đọc thuần ⇒ cả hai** | CLI cần đọc để kiểm tra trạng thái trước khi hành động; frontend cần đọc để hiển thị. Cùng schema, cùng phân trang ⇒ **cùng một client sinh từ OpenAPI** (§10) |
| **Enqueue job ⇒ cả hai** | `POST /jobs`, `POST /sync/analytics` — người dùng bấm hay script chạy đều hợp lệ; server không phân biệt |
| **Không có endpoint nào chỉ dành cho worker ở `/api/v1`** | Toàn bộ luồng worker ở `/api/worker/*` (`API_AND_WORKER_PROTOCOL`). Trộn lẫn sẽ phá tách bạch principal — chính là control chặn "CLI bị chiếm ⇒ đọc/sửa toàn bộ dữ liệu người dùng" |

---

## 9. Danh mục trường *derived* — nguồn tính

Mọi field không phải cột trong `DATA_MODEL_PLAN` đều nằm ở đây. Không có field nào "từ trên trời".

| Field | Xuất hiện ở | Tính từ |
|---|---|---|
| `my_role` | `Channel` | `user_channel_role` của principal |
| `ChannelStats.*` | `/channels/{id}/stats` | `GROUP BY` trên `content_item`, `build_job`, `approval`, `analytics_sync_run` |
| `revision_count`, `latest_revision_no` | `ContentSummary` | `content_revision` (LATERAL) |
| `latest_overall_score_bp` | `ContentSummary`, `RevisionSummary` | `score_run` mới nhất theo `(content_revision_id, created_at DESC)` |
| `latest_audit_status` | `ContentSummary` | `audit_run` mới nhất |
| `has_active_approval` | `ContentSummary` | `EXISTS(approval WHERE status='ACTIVE')` |
| `live_job_count` | `ContentSummary`, `WorkerMachine` | `build_job.status ∈ LIVE_STATUSES` |
| `is_approved`, `is_production` | `RevisionSummary` | So `content_item.approved_revision_id` / `production_revision_id` |
| `script_chars`, `script_bytes` | `RevisionSummary` | `char_length`/`octet_length(audio_script)` — **thay cho** việc trả cả script |
| `weighted_bp`, `recomputed_overall_bp`, `recompute_matches` | `ScoreRunDetail` | `score_dimension × algorithm_version.weights` |
| `delta_bp` | `ScoreDimensionOut` | So với `previous_score_run_id` |
| `finding_counts`, `unresolved_blockers` | `AuditRunSummary` | `GROUP BY severity` trên `audit_finding`, `resolved_at IS NULL` |
| `GateStatus.*`, `can_approve`, `blocking_reasons` | `/content/{id}/gates` | Hợp `audit_run` + `approval` + `claim` conflict + `channel.approval_policy` + vai trò người gọi |
| `self_approved` | `ApprovalOut` | `audit_event` của hành động approve |
| `evidence_counts`, `has_unresolved_conflict` | `ClaimOut` | `GROUP BY stance` trên `claim_evidence` |
| `is_publishable` | `ArtifactOut` | `promotion_state='PROMOTED' AND storage_state='PRESENT'` |
| `progress_percent`, `stage`, `last_heartbeat_at` | `JobSummary` | `job_event` mới nhất kiểu heartbeat |
| `duration_seconds`, `is_terminal` | `JobSummary` | `started_at`/`finished_at`; `status ∈ {DONE,FAILED,CANCELLED,EXPIRED}` |
| `liveness`, `seconds_since_seen` | `WorkerMachine` | `now() - last_seen_at` **theo giờ server** |
| `coverage.*`, `provisional_until` | `AnalyticsSeries` | `analytics_sync_partition` + quy tắc 72h hiệu chỉnh của YouTube |
| `CalendarDay.counts`, `totals` | `/calendar` | Một `GROUP BY` trên `content_item` |
| `drift_zero` | `ReconciliationReport` | `file_only + db_only + content_mismatch = 0` |

**Ràng buộc chung:** mọi field derived phải tính được bằng **một** truy vấn (LATERAL/CTE/GROUP BY)
trong cùng request. Cấm N+1 — đó là đường ngắn nhất tới `FUNCTION_TIMEOUT` trên Vercel.

---

## 10. Sinh OpenAPI & client

### 10.1 Zod là **nguồn chuẩn duy nhất**

```
packages/api-contract/
  src/
    common.ts          # Uuid, Bp, Ts, ListQuery, Problem, enum dùng chung (§5)
    envelope.ts        # Collection<T>, Page
    errors.ts          # bảng code → status (§2) — sinh cả TS union lẫn hằng cho test
    channels.ts  videos.ts  content.ts  revisions.ts  scores.ts  audits.ts
    approvals.ts sources.ts artifacts.ts calendar.ts analytics.ts
    recommendations.ts workers.ts jobs.ts imports.ts sync.ts
    worker/            # schema của /api/worker/* — dùng chung với apps/hub, KHÔNG lặp định nghĩa
    routes.ts          # đăng ký: method + path + input + output + status + auth + role
  scripts/
    build-openapi.ts   # → openapi.json (OpenAPI 3.1)
    check-drift.ts     # CI: openapi.json commit ≟ sinh lại
  openapi.json
```

| Vai trò | Cách dùng |
|---|---|
| **Runtime validation** | Route handler: `Schema.parse(body)` — `.strict()` bắt buộc cho mọi input body |
| **Type TypeScript** | `z.infer<typeof X>` — dùng chung cho handler và (Phase 8) frontend, **không** khai lại type |
| **OpenAPI** | `zod-to-openapi` (hoặc `@asteasolutions/zod-to-openapi`) đọc `routes.ts` → `openapi.json` |
| **Python client cho CLI** | `openapi-python-client` từ `openapi.json` → `hub_cli/generated/` (httpx, có type hint) |
| **Test hợp đồng** | Schema output dùng để assert response thật trong Vitest ⇒ contract test không viết tay |

### 10.2 Quy trình

```
Zod (packages/api-contract)
  ├─► z.infer ──────────────► apps/hub (route handler + type nội bộ)
  ├─► zod-to-openapi ───────► openapi.json ──► openapi-python-client ──► hub_cli/generated/
  │                                        └──► (Phase 8) frontend client
  └─► test fixture ─────────► Vitest contract test
```

| Quy định | Chi tiết |
|---|---|
| `openapi.json` **được commit** | Diff của nó là **review bề mặt API**. PR đổi API mà không đổi file này ⇒ bất thường |
| CI kiểm drift | `check-drift.ts` sinh lại và so; lệch ⇒ **fail build** |
| Python client **được sinh, không sửa tay** | `hub_cli/generated/` có header "DO NOT EDIT"; lint chặn sửa. Logic bọc nằm ở `hub_cli/client.py` |
| Pin phiên bản generator | `openapi-python-client` pin chính xác — nâng cấp là PR riêng, vì output đổi là đổi API surface của CLI |
| Worker schema dùng chung | Schema `/api/worker/*` **cũng** nằm trong `packages/api-contract/src/worker/` ⇒ CLI có một client duy nhất cho cả hai mặt. **Không** định nghĩa lại job payload ở hai nơi — đó là chỗ dễ lệch nhất |
| `params` theo `job_type` | Dùng `z.discriminatedUnion('job_type', […])` ⇒ OpenAPI ra `oneOf` + `discriminator`; Python client sinh đúng 9 lớp payload cho 9 job type của allowlist |
| Bảng lỗi | `errors.ts` sinh ra: (a) TS union `ErrorCode`; (b) JSON `code → {status, retryable}` để CLI quyết định retry **không phải đoán**; (c) fixture cho test §2 |
| Ngày sinh/`info.version` | `info.version` = semver của `packages/api-contract`, tăng theo quy tắc §1.1 |

### 10.3 Điều generator **không** làm được — phải viết tay

| Hạng mục | Vì sao Zod/OpenAPI không diễn đạt được | Ghi ở đâu |
|---|---|---|
| Ma trận vai trò theo endpoint | OpenAPI chỉ có `security`, không có RBAC theo kênh | `routes.ts` metadata + `API_AND_WORKER_PROTOCOL §11` |
| Bất biến nghiệp vụ (A-1..A-3, J-3, S-2, B-R1) | Là ràng buộc chéo entity | Test tích hợp (`TEST_STRATEGY.md`) |
| Ngữ nghĩa cursor | Chuỗi opaque | §1.3 + test |
| Idempotency | Là hành vi, không phải shape | §1.7 + test replay |
| Giới hạn payload theo endpoint | OpenAPI không có `maxBodySize` | §13 + middleware |

---

## 11. Realtime — **polling, không WebSocket**

### 11.1 Màn hình nào *thực sự* cần cập nhật liên tục

| Màn hình | Cần? | Nguồn thay đổi | Nhịp đủ dùng |
|---|:-:|---|---|
| **Build queue** (12) | **CÓ** | Worker đổi trạng thái job trong vài giây–vài phút | 3s khi có job `RUNNING`; 15s khi chỉ có `QUEUED`/`DEFERRED`; 60s khi rỗng |
| **Job log** (12b) | **CÓ** | Worker đẩy log theo lô (`API_AND_WORKER_PROTOCOL §5.2`) | 2s khi job `RUNNING`; **dừng hẳn** khi `is_terminal` |
| Worker status (16) | Gần | Heartbeat mỗi 30s | 15s — nhanh hơn vô nghĩa vì nguồn chỉ đổi mỗi 30s |
| Content detail (4) khi có job live | Gần | Như Build queue | Mượn `/jobs/stream-cursor`, 5s |
| **12 màn hình còn lại** | **KHÔNG** | Người dùng bấm, hoặc cron chạy **theo ngày** | Tải lại khi vào màn hình; poll 60s nếu muốn |

**Kết luận:** chỉ **2 màn hình** (một trong đó là panel con) cần cập nhật dưới 10 giây.
Xây hạ tầng realtime cho 2/16 màn hình, một người dùng, là sai tỉ lệ đầu tư.

### 11.2 Vì sao **không** WebSocket / SSE trên kiến trúc này

| Ràng buộc | Nguồn | Hệ quả |
|---|---|---|
| Vercel Function là **request-scoped**, không có tiến trình sống lâu | `TARGET_ARCHITECTURE §3` | Không có nơi giữ kết nối WebSocket. Muốn có phải thuê dịch vụ ngoài (Pusher/Ably/Upstash) ⇒ **thêm một dịch vụ, thêm secret, thêm bề mặt tấn công** — đi ngược §4 ("bớt một dịch vụ") |
| **Max duration** Hobby 300s / Pro 800s | `TARGET_ARCHITECTURE §3` | SSE cũng chỉ sống tối đa bằng ngần đó rồi đứt ⇒ client vẫn phải tự nối lại ⇒ vẫn phải cài logic resume. Nếu đằng nào cũng phải có cursor resume thì polling **là** giải pháp, chỉ đơn giản hơn |
| Function **tính tiền theo thời gian chạy** | Vercel | SSE giữ function mở suốt build 10 phút = trả tiền cho 10 phút *chờ*. Polling 2s trả tiền cho ~300 request ngắn — rẻ hơn và **dự đoán được** |
| Concurrency Vercel | Vercel | Mỗi SSE chiếm một slot invocation. Mở 3 tab = 3 slot bị giữ liên tục |
| Không có inbound tới máy local | `TARGET_ARCHITECTURE §1` | Worker **không** push được cho frontend; mọi trạng thái đã phải đi vòng qua DB. Nguồn sự thật là **Postgres**, không phải một kênh sự kiện ⇒ realtime chỉ là "đọc DB nhanh hơn" |
| `TARGET_ARCHITECTURE §12` | Đã chốt | "không WebSocket/realtime" nằm trong danh sách **không làm** ở giai đoạn này |
| **Long-poll** đã dùng ở Worker API | `API_AND_WORKER_PROTOCOL §4.1` | ⚠️ `wait_seconds ≤ 25` cho worker claim. **Không** tái dùng cho frontend: một người dùng mở 3 tab × long-poll 25s = 3 function bị giữ liên tục, tranh slot với worker claim — thứ **thực sự** cần long-poll |

### 11.3 Cơ chế polling — hợp đồng

| Thành phần | Quy định |
|---|---|
| **Server điều khiển nhịp** | Mọi response polling trả `poll_after_ms`. Client **phải** tôn trọng. Server tự tăng khi job terminal / khi tải cao ⇒ **backpressure nằm ở server**, không phụ thuộc client cư xử tử tế |
| **ETag / 304** | `GET /jobs/stream-cursor` và `GET /jobs/{id}` trả `ETag` (từ `max(updated_at)`). Client gửi `If-None-Match` ⇒ **304 rỗng**. Đây là chỗ tiết kiệm lớn nhất: đa số vòng poll không có gì đổi |
| **Cursor tăng dần cho log** | `GET /jobs/{id}/logs?after_seq=N` — chỉ trả dòng mới. `seq` do worker gửi và tăng đơn điệu (đã idempotent theo lô ở `§5.2`) ⇒ không trùng, không sót |
| **Một endpoint cho cả màn hình** | `/jobs/stream-cursor` gộp danh sách job sống + `counts_by_status` ⇒ Build queue poll **một** request, không phải N |
| **Dừng khi terminal** | `JobLogPage.job_status` terminal + `has_more=false` ⇒ client **ngừng poll**. Hợp đồng nói rõ để không có tab poll vĩnh viễn |
| **Rate limit riêng** | Endpoint polling để **900/phút** (§6.14) — cao hơn hẳn, vì poll 2s × 3 tab ≈ 90/phút, còn dư biên |
| **Cache header** | `Cache-Control: private, no-store` cho endpoint polling (dữ liệu sống); `private, max-age=300` cho tài nguyên **bất biến** (revision `FROZEN`, `score_run`, `production_manifest`) |
| **Không cần WAL/LISTEN-NOTIFY** | Postgres `LISTEN/NOTIFY` vô dụng ở serverless — không có kết nối thường trú để nghe |

### 11.4 Khi nào mới nên xem lại quyết định này

| Điều kiện | Khi đó cân nhắc |
|---|---|
| Có > 5 người dùng đồng thời xem Build queue | Đẩy sang SSE hoặc dịch vụ pub/sub |
| Log cần độ trễ < 1s (debug tương tác) | SSE cho **riêng** log stream |
| Hệ chuyển khỏi Vercel (host có tiến trình thường trú) | WebSocket trở nên rẻ |

Chưa điều kiện nào đúng ⇒ **polling**.

---

## 12. Bề mặt debug/test tối thiểu cho backend

Mục tiêu: **"không có bước nào phụ thuộc frontend để kiểm thử"** (`TARGET_ARCHITECTURE §0.6`).
Toàn bộ nằm ở `/api/internal/*` — nhóm thứ tư trong `API_AND_WORKER_PROTOCOL §2`.

| Endpoint | Method | Mục đích | Env cho phép | Auth |
|---|---|---|---|---|
| `/api/internal/health` | GET | Liveness: process sống, build info (`commit_sha`, `api_contract_version`, `VERCEL_ENV`) | **mọi env, kể cả production** | Không (không lộ dữ liệu) |
| `/api/internal/readyz` | GET | Readiness: ping Neon (`SELECT 1`), đo latency, `migration_version`, **`db_branch`** | **mọi env, kể cả production** | **`api_token` scope `ops`** (§12.3) |
| `/api/internal/version` | GET | `{hub_commit_sha, api_contract_version, min_supported_agent_version, protocol_version}` | **mọi env** | Không |
| `/api/internal/seed` | POST | Nạp dataset xác định: channel, user 5 vai trò, content + revision (`DRAFT`/`FROZEN`), score, audit, approval, job mọi trạng thái, artifact, video + metric | **preview / test / dev** | `INTERNAL_TOKEN` |
| `/api/internal/reset` | POST | `TRUNCATE … RESTART IDENTITY CASCADE` toàn schema test | **preview / test / dev** | `INTERNAL_TOKEN` |
| `/api/internal/clock` | POST | Đặt lệch giờ ảo cho test lease/TTL/quota-reset **[ASSUMPTION → §14 A-8]** | **test / dev** | `INTERNAL_TOKEN` |
| `/api/internal/reaper-tick` | POST | Chạy reaper lease ngay (thay vì chờ cron) — test lease hết hạn | **preview / test / dev** | `INTERNAL_TOKEN` |
| **`/api/internal/drain-reap`** | **POST** | **Vận hành thật**: cưỡng bức thu hồi lease quá hạn khi `DRAINING` chặn reaper-ở-claim (runbook restore §6.1). **Có batch limit** — xem §12.4 | **mọi env, kể cả production** | **scope `ops` + `ADMIN`** (§12.3) |
| `/api/internal/enqueue-tick` | POST | Chạy logic cron enqueue ngay | **preview / test / dev** | `INTERNAL_TOKEN` |
| `/api/internal/echo-limits` | GET | Trả cấu hình đang hiệu lực: page size, rate limit, body limit — để test khẳng định §13 | **preview / test / dev** | `INTERNAL_TOKEN` |

### 12.1 Cách tắt ở production — **ba lớp, không phải một**

| Lớp | Cơ chế | Vì sao cần thêm lớp |
|---|---|---|
| **1. Chặn runtime** | Handler kiểm `process.env.VERCEL_ENV !== 'production'` **ngay dòng đầu**, ngược lại trả **404** (không phải 403 — 403 xác nhận endpoint tồn tại) | Lớp cơ bản |
| **2. Chặn build** | Script prebuild: nếu `VERCEL_ENV === 'production'` mà thư mục `app/api/internal/{seed,reset,clock}` tồn tại trong bundle ⇒ **fail build**. Hoặc loại bằng route group có điều kiện | Lớp 1 phụ thuộc code chạy đúng; lớp 2 khiến code **không tồn tại** trong artifact production |
| **3. Chặn secret** | `INTERNAL_TOKEN` **chỉ** được cấp cho environment Preview/Development trong Vercel project settings. Production **không có biến này** ⇒ kể cả route lọt vào cũng không auth được | Phòng khi lớp 1 và 2 cùng hỏng |

**Test bắt buộc** *(`TEST_STRATEGY.md`)*: một test chạy với `VERCEL_ENV='production'` khẳng định
**mọi** route trong `/api/internal/{seed,reset,clock,reaper-tick,enqueue-tick,echo-limits}` trả **404**.
Đây là test **an ninh**, không phải test tiện ích.

> ⚠️ **Danh sách trên là ĐÓNG và cố ý KHÔNG gồm** `health`, `version`, `readyz`, `drain-reap`.
> Ba lớp tắt của §12.1 chỉ áp cho **nhóm công cụ test**. `readyz` và `drain-reap` là **thao tác vận
> hành thật, bắt buộc hoạt động trên production** (runbook restore `LEGACY_IMPORT §6.1`); chúng được
> bảo vệ bằng **token gắn user scope `ops`** (§12.3) — `readyz` chỉ cần scope, `drain-reap` cần thêm
> vai trò **`ADMIN`** — chứ không phải bằng cách tắt route.
> Test an ninh tương ứng cho nhóm này là **I-OPS1/I-OPS2**, không phải "phải trả 404".

### 12.3 Hai loại token nội bộ — **không được lẫn**

> ⚠️ *Codex v2R18 HIGH-1.* Bản trước vừa nói `/readyz` cần `INTERNAL_TOKEN` ở **mọi env**, vừa nói
> production **cố tình không có** `INTERNAL_TOKEN` (lớp 3 §12.1). Hai điều đó loại trừ nhau.

| Token | Có ở production? | Dùng cho | Vì sao tách |
|---|:-:|---|---|
| **`INTERNAL_TOKEN`** | **KHÔNG** (chỉ preview/test/dev) | `seed`, `reset`, `clock`, `reaper-tick`, `enqueue-tick`, `echo-limits` | Đây là **công cụ test có sức phá hoại**; vắng token ở production là **lớp phòng thủ thứ 3** |
| **`api_token` scope `ops`** (gắn user) | **CÓ** | `readyz`, `drain-reap` | Thao tác vận hành thật, phải chạy được **trên** production. ⚠️ **Phải gắn với một user cụ thể** — xem dưới |

> ⚠️ **`OPS_TOKEN` không được là secret dùng chung** (Codex v2R19 HIGH-2). Nếu là một chuỗi chia sẻ
> thì: (a) **không** kiểm được vai trò `ADMIN`, và (b) `audit_event(actor_kind='USER', actor_id=?)`
> trở thành **ghi chép sai sự thật** — không truy được ai đã chạy `drain-reap` trên production.
>
> **Chốt:** `OPS_TOKEN` là **`api_token` gắn user** (§1 `api_token`) với `scopes = ['ops']`:
> - Xác thực ⇒ ra **`user_id` thật** ⇒ kiểm được `ADMIN` ⇒ `audit_event.actor_id` **đúng người**.
> - Xoay/thu hồi **theo từng người**, không phải xoay một secret toàn hệ thống.
> - **`readyz`**: chỉ cần scope `ops` — **không** cần `ADMIN` (chỉ đọc trạng thái, không đổi gì).
> - **`drain-reap`**: cần scope `ops` **VÀ** vai trò `ADMIN` (thao tác thay đổi trạng thái job).
> - Thiếu scope ⇒ **404** (không xác nhận tồn tại).
>
> `INTERNAL_TOKEN` **vẫn** là secret dùng chung — chấp nhận được vì nó **không tồn tại ở production**
> và chỉ mở các route test.

⇒ Lớp 3 của §12.1 giữ nguyên hiệu lực cho nhóm test, mà vẫn cho phép vận hành production.

### 12.4 `POST /api/internal/drain-reap` — hợp đồng đầy đủ

| Mục | Quy định |
|---|---|
| **Auth** | `api_token` scope **`ops`** + vai trò **`ADMIN`** (§12.3). Sai/thiếu/không đủ quyền ⇒ **404** |
| **Điều kiện tiên quyết** | Cờ `DRAINING` **đang bật**. Nếu tắt ⇒ **409 `DRAINING_NOT_ACTIVE`** (tránh dùng nhầm lúc vận hành bình thường) |
| **Driver** | **Pool** (transaction tương tác) |
| **Request** | `DrainReap = { force: boolean = false, max_rows: int = 100, max_ms: int = 5000 }.strict()` |
| **Phạm vi thu hồi** | **Hai nhóm, không chỉ một** (Codex v2R19 HIGH-1 / v2R20 HIGH-1):<br>**(a)** `job_attempt` **đang mở** (`outcome IS NULL`) ⇒ đóng `EXPIRED`, chuyển job theo `execution_attempt`;<br>**(b)** job **`LEASED` chưa có attempt** (đã claim nhưng chưa `/start`) ⇒ **`LEASED → QUEUED`**, xoá `lease_token`/`lease_until`.<br>Bỏ nhóm (b) thì drain **tưởng xong** trong khi worker vẫn giữ lease và có thể `/start` sau đó |
| **Ngữ nghĩa `force`** | `false` (mặc định): **chỉ** thu hồi lease **đã quá hạn** (cả hai nhóm). `true`: **cưỡng bức** cả lease chưa tới hạn |
| **Giới hạn** | ⚠️ **Batch limit tính trên TỔNG hai nhóm**: `reaped_attempts + reaped_leases ≤ max_rows`, **hoặc** `max_ms` mili-giây — tuỳ cái nào tới trước. **Không** transaction không chặn |
| **`has_more`** | ⚠️ **Nghĩa duy nhất: "còn việc THU HỒI ĐƯỢC NGAY, hãy gọi lại"** = `reclaimable_remaining > 0`, trong đó `reclaimable_remaining` đếm các mục **đủ điều kiện theo `force` hiện tại** ở **cả hai** nhóm. Không được tính từ một nhóm — nếu không, nhóm (b) sẽ bị bỏ đói sau khi nhóm (a) cạn |
| **`blocked_remaining`** | Số mục **còn tồn tại nhưng KHÔNG thu hồi được** với `force` hiện tại (lease **chưa** quá hạn khi `force=false`). ⚠️ Đây là lý do `has_more` **không** được định nghĩa là "còn bộ đếm > 0": khi `force=false` và chỉ còn lease chưa hết hạn, `has_more=false` (gọi lại vô ích) nhưng `blocked_remaining > 0` (chưa drain xong) |
| **Thứ tự xử lý** | Nhóm **(a) trước, (b) sau** trong cùng lời gọi, cho tới khi chạm `max_rows`/`max_ms`. Nhờ vậy job đang chạy dở được đóng sạch trước khi thu hồi lease chưa `start` |
| **Thứ tự khoá** | Luôn `build_job` → `job_attempt` (cùng thứ tự với reaper thường) ⇒ tránh deadlock. Áp dụng cho **cả hai** nhóm (a) và (b) |
| **Response 200** | `{ reaped_attempts, reaped_leases, open_attempts_remaining, leased_jobs_remaining, reclaimable_remaining, blocked_remaining, has_more, forced, duration_ms }` |
| **Điều kiện "drain xong"** | `open_attempts_remaining == 0` **VÀ** `leased_jobs_remaining == 0`. Chỉ khi **cả hai** bằng 0 mới được bật `READ_ONLY_MODE`. `has_more=false` **một mình KHÔNG** đủ — phải kiểm hai bộ đếm này |
| **Lặp** | `has_more=true` ⇒ gọi lại. **Idempotent**: hết việc ⇒ mọi bộ đếm `0`, `has_more=false`, `blocked_remaining=0` |
| **`force=false` mà vẫn còn lease chưa hết hạn** | `has_more=false` (không còn gì thu hồi **được**) **nhưng** `blocked_remaining > 0` ⇒ **người vận hành huỷ cutover** hoặc gọi lại với `force=true`. Báo **bằng dữ liệu**, không bằng mã lỗi |
| **Audit** | ✅ `audit_event(action='DRAIN_REAP', actor_kind='USER', actor_id=<user thật từ token>)` — truy được **ai** đã chạy trên production |
| **Rate limit** | 60/phút |

> ⚠️ **Vì sao phải có batch limit** (Codex v2R18 HIGH-3): bản trước nói "một transaction thu hồi
> **mọi** lease". Trên serverless điều đó là **transaction không chặn** — có thể vượt `max_duration`,
> giữ khoá lâu, và fail toàn bộ mà không tiến triển gì. Reaper thường **đã** có giới hạn
> hàng/thời gian (`API_AND_WORKER_PROTOCOL §7`); `drain-reap` dùng **cùng** kỷ luật đó và tiến
> triển từng lô qua nhiều lời gọi.

### 12.2 Ràng buộc khác

| Quy định | Chi tiết |
|---|---|
| `/health` và `/version` **được** bật ở production | Không đọc DB, không lộ dữ liệu; cần để giám sát deploy |
| `/readyz` bật ở production nhưng có token | Ping DB ⇒ có thể bị dùng để dò trạng thái hạ tầng |
| Không có endpoint internal nào **đọc/sửa dữ liệu người dùng thật** | `seed`/`reset` chỉ chạy trên **Neon branch riêng cho test** (`TARGET_ARCHITECTURE §5`) |
| `reset` phải từ chối nếu `DATABASE_URL` không trỏ branch test | Kiểm bằng tên branch/tên DB; sai ⇒ **403** + log. Đây là chốt chặn cuối chống xoá nhầm production |
| Không nằm trong `openapi.json` công khai | Sinh file riêng `openapi.internal.json`, không phát cho client |
| Audit | `seed`/`reset`/`clock` **không** ghi `audit_event` (sẽ làm bẩn bảng append-only); ghi vào log function |

---

## 13. Phân trang & giới hạn payload

### 13.1 Trần cứng

| Giới hạn | Giá trị | Nguồn |
|---|---|---|
| **Body request/response (Vercel)** | **4,5 MB** → 413 `FUNCTION_PAYLOAD_TOO_LARGE` | `TARGET_ARCHITECTURE §3` |
| **Trần tự đặt cho User API** | **1 MB** request, **2 MB** response | Dư 4,5× so với trần Vercel ⇒ không bao giờ chạm 413 của nền tảng, lỗi luôn là `PAYLOAD_TOO_LARGE` của ta (có `code` đọc được) |
| **Payload text lớn nhất đo được** | **194,8 KB** (SEO/shot-list JSON) · **67,8 KB** (audio script) · **444,9 KB** (file text lớn nhất trong Content-Creator) | `TARGET_ARCHITECTURE §3`, `DATA_MODEL_PLAN §0` |
| **Biên an toàn** | 194,8 KB / 4,5 MB ⇒ **dư ~23×**; so với trần tự đặt 2 MB ⇒ dư ~10× | — |
| Thời gian phản hồi | **< 10s** mọi endpoint | `API_AND_WORKER_PROTOCOL §1` |

### 13.2 Bảng page size theo endpoint

| Endpoint | Default | Max | Khoá cursor | Ước lượng/hàng | Payload ở max |
|---|:-:|:-:|---|---:|---:|
| `/channels` | 25 | 100 | `label, id` | ~0,4 KB | ~40 KB |
| `/videos` | 25 | 100 | `published_at, id` | ~0,5 KB | ~50 KB |
| `/content` | 25 | 100 | `created_at, id` | ~1,0 KB | ~100 KB |
| `/content/{id}/timeline` | 25 | 100 | `occurred_at, id` | ~0,4 KB | ~40 KB |
| **`/content/{id}/revisions`** | **20** | **50** | `revision_no` | ~1,2 KB | ~60 KB |
| `/content/{id}/scores` | 25 | 100 | `created_at, id` | ~0,6 KB | ~60 KB |
| `/content/{id}/audits` | 25 | 100 | `started_at, id` | ~0,5 KB | ~50 KB |
| `…/audits/{run}/findings` | 50 | 200 | `severity_rank, id` | ~0,6 KB | ~120 KB |
| `/content/{id}/approvals` | 25 | 100 | `approved_at, id` | ~0,5 KB | ~50 KB |
| `/sources`, `/content/{id}/sources` | 25 | 100 | `retrieved_at, id` | ~0,7 KB | ~70 KB |
| `/sources/{sid}/versions` | 25 | 100 | `fetched_at, id` | ~0,3 KB | ~30 KB |
| `/claims/{cid}/evidence` | 50 | 200 | `id` | ~0,8 KB | ~160 KB |
| `/content/{id}/artifacts` | 25 | 100 | `created_at, id` | ~0,7 KB | ~70 KB |
| **`/analytics/**/daily`** | **100** | **400** | `metric_date` | ~0,2 KB | ~80 KB |
| `/recommendations/runs/{id}/items` | 50 | 200 | `rank` | ~0,6 KB | ~120 KB |
| `/workers` | 25 | 100 | `last_seen_at, id` | ~0,8 KB | ~80 KB |
| `/jobs` | 25 | 100 | `priority, created_at, id` | ~1,0 KB | ~100 KB |
| `/jobs/{id}/attempts` | 25 | 100 | `attempt_no` | ~0,3 KB | ~30 KB |
| `/jobs/{id}/events` | 100 | 500 | `seq` | ~0,5 KB | ~250 KB |
| **`/jobs/{id}/logs`** | **200** | **500** | `seq` | ~0,3 KB | **cắt cứng 256 KB** |
| `/import/batches` | 25 | 100 | `started_at, id` | ~0,5 KB | ~50 KB |
| `/import/batches/{id}/records` | 100 | 500 | `id` | ~0,6 KB | ~300 KB |
| `/sync/runs` | 25 | 100 | `started_at, id` | ~0,5 KB | ~50 KB |
| `/sync/runs/{id}/partitions` | 100 | 400 | `partition_date_start, id` | ~0,5 KB | ~200 KB |

`limit` vượt max ⇒ **kẹp về max** (không lỗi) nhưng trả header `X-Limit-Clamped: 1`.
`limit` không phải số / ≤ 0 ⇒ **422 `VALIDATION_FAILED`**.

### 13.3 Endpoint **có nguy cơ payload lớn** và cách chia lô

| # | Endpoint | Nguy cơ | Cách chia lô / chặn |
|---|---|---|---|
| 1 | `GET …/revisions/{rid}` (full) | `audio_script` 67,8 KB + `seo_package` 194,8 KB + các jsonb khác ⇒ **~300 KB** một bản ghi | Projection mặc định **loại** `seo_package`, `visual_prompts`, `semantic_beats`, `thumbnail_concepts`. Muốn có ⇒ `?fields=`. Không có cách nào lấy tất cả trong một lần mà không nêu tên |
| 2 | `GET …/revisions/diff` | Hai bản ×2 + hunk ⇒ có thể > 1 MB | Mặc định **không** hunk (chỉ sha256 + số ký tự). `?fields=` tối đa **3 field**. Hunk cắt **512 KB/field** + `truncated` |
| 3 | `POST …/revisions` | Client gửi trọn nội dung | Zod giới hạn từng field (`audio_script ≤ 400 000` ký tự…), tổng body **≤ 1 MB** ⇒ 413 `PAYLOAD_TOO_LARGE` |
| 4 | `GET /sources/{sid}/versions/{vid}/text` | `extracted_text` tới **444,9 KB** | Endpoint riêng + `?offset=&length=` (mặc định 256 KB) ⇒ tối đa 2 lô. `truncated` + `total_bytes` bắt buộc |
| 5 | `GET /jobs/{id}/logs` | Job dài sinh nhiều MB log (worker được phép 10 MB/job) | Cursor `after_seq`, **256 KB/trang** (khớp trần lô của worker), `next_after_seq`. Client tự nối |
| 6 | `GET /jobs/{id}/events` | `payload` jsonb mỗi event | `payload` chỉ khi `?include=payload`; mặc định trả `event_type` + tóm tắt |
| 7 | `GET /calendar` | 92 ngày × nhiều mục | Cửa sổ ≤ 92 ngày + **≤60 mục/ngày** + projection cực gọn ⇒ trần thực tế ~5 520 mục × 0,2 KB ≈ 1,1 MB. Vượt ⇒ `truncated_days` |
| 8 | `GET /analytics/**/daily` | 400 ngày × N video | Bắt buộc `from`/`to` ≤ 400 ngày; **một subject/request** (không batch nhiều video); cursor 400 hàng |
| 9 | `POST /import/batches/{id}/records` | Import nghìn bản ghi | **≤200 bản ghi/lô** *và* **≤1 MB/lô**; `raw_payload_excerpt` là trích đoạn, không phải nguyên file. Nhiều lô ⇒ nhiều request, idempotent theo `(batch_id, legacy_ref)` |
| 10 | `GET …/revisions/{rid}/manifest?include=frozen_input` | `files[]` của repo Content-Creator có thể hàng nghìn mục | Cắt **500 mục** + `truncated` |
| 11 | `GET /content?with_total=1` | `COUNT(*)` trên bảng lớn | Chỉ cho `/content` và `/jobs` (luôn có filter `channel_id`); cấm ở analytics/events/logs ⇒ `TOTAL_NOT_SUPPORTED` |
| 12 | `GET …/audits/{run}/findings?include=evidence` | `evidence` jsonb tự do | `evidence` chỉ khi xin; mỗi finding cắt **64 KB** evidence + `truncated` |

**Nhận xét về trần 4,5 MB:** không endpoint nào ở bảng trên chạm tới, kể cả trường hợp xấu nhất
(`/calendar` ~1,1 MB). Đây là hệ quả trực tiếp của quyết định **"chỉ lưu nội dung text, media ở lại local"**
(`TARGET_ARCHITECTURE §0.3`) — nếu media đi qua API, mọi bảng ở trên sẽ vô nghĩa.

### 13.4 Ngưỡng rate limit tổng hợp

| Nhóm | Ngưỡng/phút/principal | Ghi chú |
|---|---:|---|
| Đọc thường | 600 | Mặc định |
| Đọc polling (`/jobs/{id}`, `/events`, `/logs`, `/stream-cursor`) | 900 | Poll 2s × 3 tab ≈ 90 ⇒ dư biên lớn |
| Ghi thường (PATCH/POST metadata) | 120 | |
| Enqueue job (`POST /jobs`, `/scores`, `/audits`, `/sync/analytics`) | 30 | Mỗi lần tạo việc thật cho worker |
| Hành động nhạy cảm (approve, revoke, freeze, promote, token) | 30 | |
| Tạo tốn kém (`/recommendations/runs`, enrollment code, import batch) | 10 | |
| Đăng nhập | 5 / 15 phút / (IP + email) | Chống dò mật khẩu |

Vượt ⇒ **429 `RATE_LIMITED`** + `Retry-After` + `X-RateLimit-*`.

---

## 14. Giả định & khoảng trống so với `DATA_MODEL_PLAN.md`

Mọi mục dưới đây **chưa có chỗ chứa** trong data model hiện tại. Cần quyết định trước khi implement.

| # | Giả định | Ảnh hưởng | Đề xuất |
|---|---|---|---|
| ~~A-1~~ | ~~Bảng `idempotency_record`~~ | ✅ **ĐÃ ĐÓNG** — bảng đã được định nghĩa chính thức ở `DATA_MODEL_PLAN §1.5` với khoá `(scope, idempotency_key, principal_id)` và retention **30 ngày**. ⚠️ Dùng **đúng** hình dạng đó; mọi mô tả cũ (`endpoint`/`key`/`request_sha256`/`response_body`, unique `(principal_id, endpoint, key)`, TTL 24h) **đã bị thay thế** | — |
| **A-2** | Bảng **`rate_limit_bucket`** `(principal_id, bucket_key, window_start, count)` **hoặc** dùng Vercel Firewall | §4 — serverless không có bộ nhớ chung | Ưu tiên **Vercel Firewall** cho ngưỡng thô + bảng DB cho ngưỡng nghiệp vụ (approve/enqueue) |
| **A-3** | Quyền trên `source_document` suy theo `domain_id` (có ≥1 kênh cùng domain), vì bảng này **không** có `channel_id` | §6.8 — đây là ngoại lệ duy nhất của "scope theo kênh" | Chấp nhận ở MVP (một người dùng); ghi rõ trong test cross-channel |
| **A-4** | `POST /artifacts/{aid}/verify` cần job type `VERIFY_ARTIFACT` — **không có** trong allowlist đóng `§9` | §6.9 | **Trả 501 ở MVP.** Không nới allowlist vì tiện — allowlist đóng là control chống RCE |
| **A-5** | `recommendation_run` tính **trong server route** (SQL aggregate), không qua worker, vì allowlist không có job type tương ứng | §6.12 | Chấp nhận; ràng < 10s, transaction, không ghi run dở dang |
| **A-6** | Phát hiện worker token dùng đồng thời từ hai nguồn cần lưu vết `(token_id, ip, ts)` | §6.13 — `TARGET_ARCHITECTURE §6` yêu cầu "cảnh báo khi dùng đồng thời từ hai nguồn" nhưng không có bảng | Thêm cột vào `worker_token` (`last_used_ip`) hoặc bảng `worker_token_use` gọn |
| **A-7** | Reconciliation report chưa có entity | §6.17 | **Tái dùng `import_batch`** với `source_kind='RECONCILIATION'` + `mode='DRY_RUN'`, `report` jsonb — không mở entity mới |
| **A-8** | `/api/internal/clock` cần cơ chế giờ ảo | §12 | Chỉ ở env test; inject `now()` qua lớp trừu tượng trong `src/domain/*`, **không** đụng `now()` của Postgres ở production |
| **A-9** | `reauth_token` cho step-up (TTL 5 phút) chưa có chỗ lưu | §3, §6.7 | Dùng `session` với cột `reauth_at` **hoặc** token đục lưu hash TTL ngắn |
| **A-10** | `enrollment_code` (`API_AND_WORKER_PROTOCOL §3.1`) chưa có bảng trong data model | §6.13 | Thêm `worker_enrollment_code(id, code_sha256, label, expires_at, used_at, used_by_machine_id, created_by)` |
| **A-11** | `q` (tìm kiếm) dùng `ILIKE`, chưa có index trigram | §1.5 | Thêm `pg_trgm` + GIN index trên `content_item.topic` khi dữ liệu > vài nghìn hàng; MVP chấp nhận seq scan có filter `channel_id` |
| **A-12** | `progress_percent`/`stage` đọc từ `job_event` kiểu heartbeat — data model không quy định `event_type` chuẩn | §6.14, §9 | Chốt danh sách `event_type` đóng (`HEARTBEAT, STAGE, LOG, WARN, ERROR, ARTIFACT, LEASE`) trong `packages/api-contract` |
| **A-13** | `/calendar` là view dẫn xuất; `calendar_entry` thuộc P1b | §6.10 | Giữ dẫn xuất ở MVP. Khi bật `calendar_entry`, hợp đồng `/calendar` **giữ nguyên shape** — chỉ đổi nguồn |
| **A-14** | Thời hạn hỗ trợ `/api/v1` (90 ngày) và ngưỡng `liveness` worker | §1.1, §6.13 | Cấu hình được, lộ qua `/api/internal/echo-limits` |

---

## 15. Ngoài phạm vi tài liệu này

| Không làm | Ở đâu / khi nào |
|---|---|
| **Thiết kế UI**: component, layout, styling, visual design, luồng tương tác | **Phase 8**, sau khi người dùng duyệt mockup (`TARGET_ARCHITECTURE §12`) |
| Worker protocol chi tiết | `API_AND_WORKER_PROTOCOL.md` |
| Migration SQL, index thật | `DATA_MODEL_PLAN.md` + drizzle-kit khi implement |
| Chiến lược test, Neon branch | `TEST_STRATEGY.md` |
| Import legacy chi tiết, reconciliation | `LEGACY_IMPORT_AND_SYNC_PLAN.md` |
| Version thuật toán chấm điểm | `ALGORITHM_VERSIONING_PLAN.md` |
| Lưu trữ, Blob, retention media | `STORAGE_STRATEGY.md` |
| WebSocket/SSE/pub-sub | §11 — không làm; điều kiện xem lại ở §11.4 |
| Upload nhị phân | §6.15 — 501 ở MVP |
| Multi-tenant, `workspace_id` | `DATA_MODEL_PLAN §12` |
| GraphQL, gRPC, batch endpoint kiểu `/graphql` | Không — REST + OpenAPI đủ cho 16 màn hình và một CLI |

---

## 16. Checklist trước khi implement

| # | Việc | Chặn bởi |
|---|---|---|
| 1 | Duyệt **A-1** (`idempotency_record`) và **A-10** (`worker_enrollment_code`) — hai bảng bắt buộc có mới chạy được §1.7 và §6.13 | Quyết định người dùng |
| 2 | Chốt **A-4** (`/artifacts/verify` = 501) và **A-5** (recommendation tính trong server) — cả hai nhằm **giữ nguyên allowlist đóng §9** | Quyết định người dùng |
| 3 | Chốt **A-7** (reconciliation tái dùng `import_batch`) | Quyết định người dùng |
| 4 | Dựng `packages/api-contract` với `common.ts` + `errors.ts` trước mọi route — bảng lỗi §2 là thứ mọi test dựa vào | — |
| 5 | Viết middleware theo thứ tự: **worker-token-reject → auth → channel-scope → rate-limit → body-size → Zod strict → idempotency** | — |
| 6 | Cài helper cursor dùng chung (§1.3) — cấm route tự viết phân trang | — |
| 7 | Test an ninh: **nhóm công cụ test** (`seed`/`reset`/`clock`/`reaper-tick`/`enqueue-tick`/`echo-limits`) trả **404** khi `VERCEL_ENV='production'`; **nhóm vận hành** (`health`/`version`/`readyz`/`drain-reap`) **vẫn hoạt động** (bảo vệ bằng token, không bằng tắt route) (§12.1) | — |
| 8 | Test hợp đồng: mỗi `code` ở §2 ánh xạ đúng một HTTP status | — |
| 9 | CI drift check `openapi.json` (§10.2) | — |
| 10 | Test cross-channel: mọi endpoint có `{id}` trả **404** (không phải 403) khi ngoài phạm vi kênh | — |
