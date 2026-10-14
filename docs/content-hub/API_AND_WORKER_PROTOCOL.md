# API_AND_WORKER_PROTOCOL.md

> Hợp đồng giữa **Vercel backend** và **Local CLI worker (Python)**.
> Nguyên tắc bất di bất dịch: **server không bao giờ gửi shell command; worker kéo dữ liệu và chạy
> verb thuộc allowlist đóng đã cài sẵn.**

---

## 1. Nền tảng

| Hạng mục | Quy định |
|---|---|
| Base URL | `https://<project>.vercel.app/api` |
| Định dạng | JSON, `Content-Type: application/json` |
| Auth user | Session cookie **hoặc** PAT `Authorization: Bearer hub_pat_…` |
| Auth worker | `Authorization: Bearer hub_wt_…` — **khác** user, chỉ chạm `/api/worker/*` |
| Auth cron | Header `Authorization: Bearer $CRON_SECRET`, so sánh hằng thời gian |
| Idempotency | Header `Idempotency-Key: <uuid>` cho mọi POST đổi trạng thái |
| Version | `X-Worker-Protocol: 1` + `X-Agent-Version: <semver>` |
| Request ID | Server trả `X-Request-Id`; worker ghi vào log để đối chiếu |
| Đồng hồ | **Mọi thời hạn do server quyết định.** Worker chỉ dùng khoảng tương đối (chống clock skew) |
| Lỗi | RFC 7807 `application/problem+json` |
| **Body limit** | **4,5 MB** (Vercel). Payload lớn nhất thực tế: 194,8 KB ⇒ an toàn. Endpoint nào có nguy cơ vượt phải phân trang/chia lô. |
| **Timeout** | Endpoint phải trả < 10s. Không có tác vụ dài trên Vercel. |

### Mẫu lỗi
```json
{
  "type": "https://hub/errors/lease-expired",
  "title": "Lease expired",
  "status": 409,
  "code": "LEASE_EXPIRED",
  "detail": "Lease token 3f2a… no longer valid for job 018f…",
  "request_id": "req_01J…"
}
```

---

## 2. Phân nhóm API (tách rõ theo caller)

| Nhóm | Prefix | Caller | Auth |
|---|---|---|---|
| **User API** | `/api/v1/*` | Frontend tương lai, người dùng, CLI-as-user | Session / PAT |
| **Worker API** | `/api/worker/*` | Local CLI worker | Worker token |
| **Cron API** | `/api/cron/*` | Vercel Cron | `CRON_SECRET` |
| **Internal** | `/api/internal/*` | Chỉ trong deployment | Không lộ ra ngoài |

> **Tách bạch là bắt buộc:** worker token **không** mở được User API, và ngược lại.
> Điều này chặn kịch bản "CLI bị chiếm ⇒ đọc/sửa toàn bộ dữ liệu người dùng".

Chi tiết endpoint, schema, phân trang, filter: xem `API_CONTRACT_PLAN.md`.

---

## 3. Đăng ký & xác thực worker

### 3.1 `POST /api/worker/register`
Dùng **enrollment code** một lần (TTL 15 phút) do admin tạo — không nhúng secret dài hạn vào lệnh cài.

```json
{
  "enrollment_code": "ENR-7K2P-9QX4",
  "name": "macbook-studio", "os": "darwin", "arch": "arm64",
  "agent_version": "1.0.0",
  "capabilities": ["ANALYZE_CONTENT","SCORE_CONTENT","IMPROVE_CONTENT",
                   "BUILD_AUDIO","BUILD_VIDEO","BUILD_SUBTITLE","BUILD_THUMBNAIL",
                   "SYNC_ANALYTICS","EXPORT_PACKAGE"],
  "capability_detail": {
    "ffmpeg": "7.1", "comfyui": true, "codex_cli": "0.144.6",
    "vieneu_mode": "v3turbo", "channels_available": ["phat_giao","phong_thuy","hinh_su"]
  }
}
```
**201** → `{ machine_id, worker_token (hiển thị MỘT lần), token_prefix, expires_at, heartbeat_interval_seconds, protocol_version }`

### 3.2 Xoay / thu hồi / cập nhật năng lực
- `POST /api/worker/token/rotate` — token mới, token cũ còn hiệu lực **grace 24h** (không giết worker đang chạy).
- `POST /api/v1/workers/{machine_id}/tokens/{token_id}/revoke` *(ADMIN — **User API**, không phải Worker API)*. Đường chuẩn duy nhất; `API_CONTRACT_PLAN.md` dùng cùng đường này.
- `PUT /api/worker/capabilities` — worker gọi lại khi môi trường đổi (vd ComfyUI tắt).

⚠️ **Nói thẳng giới hạn:** đây là bearer token **liên kết** với máy, **không chứng minh sở hữu**.
Ai lấy được token đều mạo danh được. Bù bằng TTL ngắn, revoke nhanh, cảnh báo khi token dùng đồng
thời từ hai nguồn. mTLS/DPoP là bước sau MVP.

---

## 4. Nhận việc

### 4.1 `POST /api/worker/jobs/claim` — long-poll

```json
{ "capabilities": ["BUILD_AUDIO","SCORE_CONTENT"], "max_jobs": 1,
  "wait_seconds": 25, "busy_slots": 0, "max_concurrent": 2 }
```

> ⚠️ `wait_seconds` **≤ 25** để tổng thời gian function nằm an toàn dưới giới hạn Vercel và dưới
> timeout của proxy. Long-poll dài hơn phải chia thành nhiều lượt.

**200** → danh sách job; **204** → hết chờ, claim lại.

```json
{"jobs":[{
  "job_id":"018f3a…", "job_type":"BUILD_AUDIO",
  "content_item_id":"018f11…", "content_revision_id":"018f12…",
  "claim_count":1, "execution_attempt":0, "quota_deferral_count":0, "max_attempts":3,
  "lease_token":"lt_9c4e…", "lease_until":"2026-07-29T10:31:30Z",
  "lease_duration_seconds":90, "heartbeat_interval_seconds":30,
  "manifest_url":"/api/worker/jobs/018f3a…/manifest",
  "manifest_sha256":"b1946ac9…",
  "params":{"voice_profile":"Binh","channel_label":"phat_giao"}
}]}
```

**Claim nguyên tử — chốt: MỘT câu lệnh `UPDATE … RETURNING`, chạy trên HTTP driver.**

```sql
UPDATE build_job b
   SET status='LEASED', leased_by=:m, lease_token=:t,
       lease_until = now() + interval '90 seconds',
       claim_count = claim_count + 1          -- CHỈ claim_count tăng ở đây
 WHERE b.id = (
         SELECT id FROM build_job
          WHERE status IN ('QUEUED','DEFERRED') AND not_before <= now()
            AND required_capability = ANY(:caps) AND NOT cancel_requested
          ORDER BY priority DESC, created_at
          LIMIT 1)
   AND b.status IN ('QUEUED','DEFERRED')      -- CAS: điều kiện quyết định thắng/thua
   AND b.not_before <= now()
   AND NOT b.cancel_requested
RETURNING *;
```

> ⚠️ **Sửa theo Codex v2R1 HIGH-1.** Bản trước khẳng định "HTTP driver không hỗ trợ interactive
> transaction ⇒ **phải** dùng Pool/WebSocket, nếu không `SKIP LOCKED` mất tác dụng".
> **Khẳng định đó sai** và dạy một mô hình lỗi sai.

### 4.1.1 Phản biện hai phương án *(bắt buộc theo yêu cầu người dùng)*

| Trục | (A) `FOR UPDATE SKIP LOCKED` trong transaction tường minh (Pool/WebSocket) | (B) CAS thuần `UPDATE … WHERE status='QUEUED' … RETURNING` |
|---|---|---|
| **1. Vercel serverless** | Invocation ngắn, không state chia sẻ ⇒ tính đúng đắn **phải** ở Postgres. Cả hai đều thoả. A thêm chi phí mở/đóng WebSocket mỗi lần gọi | Không cần vòng đời kết nối đặc biệt |
| **2. Neon driver** | Cần Pool/WebSocket **chỉ khi** tách SELECT và UPDATE thành hai câu | HTTP one-shot là đủ |
| **3. Có thật sự cần transaction?** | **Không**, nếu là *một* câu lệnh — PostgreSQL bọc mọi câu lệnh đơn trong transaction ngầm | Không |
| **4. Vòng đời kết nối** | WebSocket phải mở/đóng theo request; rủi ro rò kết nối khi function bị đóng băng | HTTP có connection caching, rẻ hơn |
| **5. Race dưới N worker** | `SKIP LOCKED` bỏ qua ngay hàng bị khoá ⇒ công bằng hơn, throughput tốt hơn | **An toàn tương đương**: read-committed đánh giá lại vị từ ⇒ đúng một worker thắng. Kém công bằng hơn; giảm nhẹ bằng jitter + chọn ngẫu nhiên trong `LIMIT k` |
| **6. Độ phức tạp** | Cao hơn nếu bắt buộc Pool | Thấp nhất |
| **7. Khả năng test** | Như nhau — phải chứng minh bằng test race trên Neon thật | Như nhau |

**CHỐT: phương án (B) — atomic conditional `UPDATE … RETURNING` trên Neon HTTP driver.**

> ⚠️ **Sửa lần hai theo Codex v2R2 HIGH-1.** Vòng trước tôi chọn một *phương án lai* (giữ
> `SKIP LOCKED` + thêm CAS). Codex bác bỏ đúng: người dùng yêu cầu **chọn dứt khoát A hoặc B**,
> và bản lai là **thứ ba** — không phải A (không có transaction tường minh qua Pool), cũng không
> phải B thuần. Giữ một phương án không tên khiến người triển khai không biết đâu là chuẩn.
> **Chấp nhận: bỏ `FOR UPDATE SKIP LOCKED`, dùng B thuần.**

Lý do theo đúng 7 trục:
1. **Vercel serverless** — invocation ngắn, không state chia sẻ ⇒ tính đúng đắn **phải** nằm ở
   PostgreSQL. B thoả hoàn toàn.
2. **Neon driver** — Neon tài liệu hoá HTTP cho truy vấn one-shot / transaction phi tương tác, và
   WebSocket cho transaction phiên/tương tác. B chỉ cần cái thứ nhất.
3. **Transaction** — B chỉ cần **transaction ngầm của một câu lệnh**. Không cần interactive.
4. **Vòng đời kết nối** — tránh hoàn toàn chi phí mở/đóng WebSocket mỗi invocation và rủi ro rò
   kết nối khi function bị đóng băng.
5. **Race dưới N worker** — mệnh đề `status` ở câu ngoài bảo đảm **nhiều nhất một** worker thắng
   trên một hàng: sau khi bên kia commit, PostgreSQL (read-committed) **đánh giá lại** vị từ, kẻ
   thua nhận **0 dòng**. An toàn tuyệt đối. Đánh đổi: **kém công bằng hơn** `SKIP LOCKED` — nhiều
   worker có thể cùng nhắm hàng đầu rồi cùng trượt. Giảm nhẹ bằng **retry ngay có jitter** và
   chọn ngẫu nhiên trong `LIMIT k` hàng đầu thay vì luôn hàng số 1.
6. **Độ phức tạp** — thấp nhất: một câu lệnh, một driver, không nhánh riêng theo driver.
7. **Khả năng test** — chứng minh bằng N **tiến trình độc lập** trên Neon branch thật, qua **đúng
   HTTP driver production**.

**Điều kiện xét lại:** nếu đo được tranh chấp hàng đầu gây mất throughput đáng kể, thì chuyển
**hẳn sang (A)** — `FOR UPDATE SKIP LOCKED` trong transaction tường minh qua Pool/WebSocket — và
ghi lại quyết định. **Không** quay lại phương án lai không tên.

**Kiểm chứng bằng test, không bằng lập luận** (`TEST_STRATEGY.md §2.6`): N invocation độc lập dùng
**đúng HTTP driver của production**, đối chiếu `job_lease_history` — mỗi job đúng một lease, không
chồng lấn, toàn bộ M job cuối cùng đều được claim.

### 4.2 `GET /api/worker/jobs/{id}/manifest`
Trả `production_manifest.payload` (đã đóng băng). Worker **phải** verify
`sha256(body) == manifest_sha256`; lệch ⇒ huỷ job, báo `MANIFEST_CHECKSUM_MISMATCH`.
Manifest **chỉ chứa dữ liệu** — không lệnh, không đường dẫn nhị phân, không tham số CLI thô.

### 4.3 `GET /api/worker/revisions/{id}`
Tải nội dung revision (script, SEO, outline…). Kiểm quyền theo channel của job.

### 4.4 `POST /api/worker/jobs/{id}/start` — bắt đầu thực thi

```json
{ "lease_token": "lt_9c4e…" }
```
**200** → `{ "job_attempt_id":"018f3b…", "attempt_no":1, "execution_attempt":1 }`

Trong **một** transaction: verify lease → `LEASED→RUNNING` → `execution_attempt += 1`
(vượt `max_attempts` ⇒ `FAILED`+409) → tạo `job_attempt(outcome=NULL)`.
**Idempotent:** gọi lại khi đã có attempt mở ⇒ trả đúng `job_attempt_id` cũ, không tăng bộ đếm.

> **Ba bộ đếm tách biệt** — đây là thứ chặn vòng lặp retry vô hạn:
>
> | Bộ đếm | Tăng khi | So với |
> |---|---|---|
> | `claim_count` | mỗi lần claim | phát hiện worker chết lặp |
> | `execution_attempt` | khi handler **thực sự bắt đầu** | `max_attempts` |
> | `quota_deferral_count` | hoãn vì quota | `max_deferral_age` |
>
> **Không chuyển trạng thái nào GIẢM bộ đếm.**

---

## 5. Thực thi

### 5.1 `POST /api/worker/jobs/{id}/heartbeat` (mỗi 30s)
`{ lease_token, job_attempt_id, progress_percent, stage, message }`
→ `{ lease_until, cancel_requested }` — **`cancel_requested` là kênh huỷ việc**, không cần push.
**409 `LEASE_EXPIRED`** ⇒ worker **dừng ngay**, không ghi kết quả.

### 5.2 `POST /api/worker/jobs/{id}/logs` — theo lô
`{ lease_token, job_attempt_id, seq, lines:[{ts,level,msg}] }`
- `seq` tăng dần ⇒ server bỏ lô trùng (idempotent).
- **Redaction hai lớp** (worker trước khi gửi, server trước khi ghi). Mẫu chặn:
  `ghp_…`, `hf_…`, `hub_wt_…`, `hub_pat_…`, `"client_secret"…`, `"refresh_token"…`,
  `Authorization:\s*\S+`, `access_token=…`
- Giới hạn: **256 KB/lô**, 10 MB/job (an toàn dưới 4,5 MB body). Vượt ⇒ cắt + ghi `LOG_TRUNCATED`.

### 5.3 `POST /api/worker/jobs/{id}/artifacts` — **metadata only**

```json
{ "lease_token":"lt_9c4e…", "job_attempt_id":"018f3b…",
  "artifacts":[{
    "role":"VIDEO_FINAL",
    "storage_backend":"LOCAL",
    "workspace_relative_path":"EP001 - Địa Tạng.mp4",
    "sha256":"9f86d081…", "byte_size":353370112, "mime_type":"video/mp4",
    "attestation":{"resolved_within_workspace":true,"workspace_id":"ws_018f3a…",
                   "opened_nofollow":true,"hashed_from_open_fd":true}
  }]}
```

⚠️ **Media KHÔNG được upload** *(quyết định người dùng 2026-07-29)*. Chỉ gửi metadata; file ở lại đĩa local.
Điều này đồng thời làm giới hạn 4,5 MB trở nên vô hại — không có file nào đi qua API.

**Ai xác minh cái gì:**

| Bên | Trách nhiệm |
|---|---|
| **Worker** | `realpath`; mở bằng fd gốc-workspace ngữ nghĩa **no-follow**; băm **từ chính fd đã mở** (chống TOCTOU); trả `attestation` |
| **Server** | Validate **cú pháp** (đường dẫn tương đối, không `..`, không tuyệt đối), **phân quyền**, `job_attempt_id` khớp lease, cờ attestation đủ. Server **không** tuyên bố đảm bảo containment mà nó không quan sát được (nó không thấy đĩa worker) |

Artifact vào `promotion_state='PROVISIONAL'`. Idempotent theo `(job_attempt_id, role, sha256)`.

### 5.4 Nội dung text (script/SEO) — đi thẳng vào DB
`POST /api/worker/revisions` (tạo revision đề xuất) và `POST /api/worker/jobs/{id}/scores`
mang **payload text trực tiếp trong JSON** (≤ vài trăm KB). Không qua Blob, không qua file.

---

## 6. Kết thúc

### 6.1 `POST /api/worker/jobs/{id}/complete`
`{ lease_token, job_attempt_id, idempotency_key, result:{ artifact_ids, duration_seconds } }`
- Server từ chối **409** nếu `(job_attempt_id, lease_token, worker_machine_id)` không khớp lease đang hoạt động — chặn worker cũ ghi kết quả muộn.
- Gọi lại cùng `Idempotency-Key` ⇒ **200 + cùng body**, không tác dụng phụ lần hai.

**Promotion artifact (cùng transaction) — ⚠️ THỨ TỰ QUAN TRỌNG:**

1. **SUPERSEDE TRƯỚC**: bản `PROMOTED` cũ cùng `(build_job_id, role)` → `SUPERSEDED`.
2. **PROMOTE SAU**: artifact của `job_attempt_id` này: `PROVISIONAL → PROMOTED`.
3. Partial unique là **chốt chặn cuối**, không phải cơ chế chính.

> ⚠️ **Sửa theo Final Architecture Review.** Bản trước ghi ngược thứ tự (promote trước, supersede sau).
> Với partial unique **immediate** trên `(build_job_id, role) WHERE promotion_state='PROMOTED'`, nếu
> job đã có một bản `PROMOTED` (trường hợp **retry sinh hash khác** — vốn là chuyện bình thường vì
> TTS/video không tất định), bước promote sẽ tạo **hai** hàng thoả điều kiện index **trước khi**
> bước supersede kịp chạy ⇒ **vi phạm unique, transaction rollback**, artifact mới không bao giờ được promote.
>
> **Hoặc** gộp cả hai vào **một câu lệnh** để không bao giờ lộ ra hai hàng `PROMOTED`:
> ```sql
> WITH demoted AS (
>   UPDATE artifact SET promotion_state='SUPERSEDED'
>    WHERE build_job_id = :job AND role = :role AND promotion_state = 'PROMOTED'
>   RETURNING id)
> UPDATE artifact SET promotion_state='PROMOTED'
>  WHERE job_attempt_id = :attempt AND role = :role AND promotion_state = 'PROVISIONAL'
> RETURNING *;
> ```
> Khoá job + artifact liên quan, verify lease/attempt, rồi mới chạy. Nếu dùng `DEFERRABLE` unique thì
> thứ tự bớt quan trọng — nhưng **không** dựa vào điều đó: giữ index **immediate** và sửa thứ tự.

**Chỉ `PROMOTED` mới được dùng để publish** — TTS/video không tất định nên retry sinh hash khác là
bình thường; dedupe theo hash **không đủ** để chọn bản dùng.

### 6.2 `POST /api/worker/jobs/{id}/fail`
`{ lease_token, job_attempt_id, error_code, error_message (đã redact), retryable }`

⚠️ **Giữ nguyên `reason` gốc của Google, không gộp.** Hàm hiện có `_is_quota_exceeded()` gộp
`quotaExceeded` + `dailyLimitExceeded` + `rateLimitExceeded` làm một (`youtube_upload.py:111-115`) —
nhưng `rateLimitExceeded` là throttling **ngắn hạn**, gộp lại sẽ treo việc khôi phục nhiều giờ.

| `error_code` | Trạng thái | Bộ đếm | `not_before` |
|---|---|---|---|
| `YOUTUBE_DAILY_QUOTA_EXCEEDED` | `DEFERRED` | `quota_deferral_count++` | mốc reset kế tiếp, **timezone có DST** |
| `YOUTUBE_RATE_LIMITED` | `QUEUED` | — | backoff luỹ thừa + jitter |
| `YOUTUBE_PROJECT_LIMIT` | `FAILED` | — | cần người xử lý |
| `NETWORK_TIMEOUT`, `HTTP_5XX` | `QUEUED` | — | `2^execution_attempt × 30s` + jitter |
| `FFMPEG_EXIT_*`, `TTS_QA_FAIL` | `QUEUED` | — | `now + 60s` |
| `MANIFEST_CHECKSUM_MISMATCH` | `FAILED` | — | lỗi toàn vẹn |
| `APPROVAL_REVOKED`, `REVISION_NOT_FROZEN` | `FAILED` | — | — |

### 6.3 Huỷ / tiếp tục / tắt máy
- Huỷ: user `POST /api/v1/jobs/{id}/cancel` → `cancel_requested=true`; worker thấy ở heartbeat → dọn dẹp → `POST /api/worker/jobs/{id}/cancelled`. Không phản hồi tới khi hết lease ⇒ reaper chuyển `CANCELLED`.
- `POST /api/worker/jobs/{id}/resume-info`: chỉ trả checkpoint **được khai báo dùng lại được** (cùng `manifest_sha256`, attempt không `EXPIRED`, `promotion_state != SUPERSEDED`, worker verify lại `sha256`). Cơ chế "skip nếu file đã tồn tại" (`process_drive_queue.py:78-86`) là idempotency theo file, **không** an toàn khi nhiều attempt cạnh tranh.
- `POST /api/worker/shutdown`: trả mọi lease đang giữ ⇒ job về `QUEUED` ngay.

---

## 7. Chuyển trạng thái job

```
QUEUED ──claim──► LEASED ──start──► RUNNING ──complete──► DONE
  ▲                 │                  │
  │                 │ lease hết hạn    │ fail(retryable) & execution_attempt<max
  └─────────────────┴──────────────────┤
  ▲                                    ├──fail(không retry)──► FAILED
DEFERRED ◄──fail(daily quota)──────────┘
  └──► QUEUED khi qua not_before;  ──► FAILED nếu quá max_deferral_age
```

**Reaper — hai tầng, không phụ thuộc gói Vercel.**

> ⚠️ **Sửa theo Codex v2R1 HIGH-2.** Bản trước yêu cầu "cron mỗi phút" cho lease 90 giây.
> **Vercel Hobby chỉ cho cron chạy 1 lần/ngày** ⇒ trên Hobby, worker chết sẽ giam job gần **một
> ngày** thay vì ~90 giây, và kịch bản nghiệm thu "giết worker → job được nhận lại" của MVP
> **không chạy được**.

| Tầng | Cơ chế | Vì sao |
|---|---|---|
| **1. Reap cơ hội (chính)** | Ngay đầu mỗi `POST /jobs/claim`, thu hồi tối đa `K` job có `lease_until < now()` | Không phụ thuộc cron ⇒ chạy trên **mọi gói**. Worker vốn poll liên tục nên tần suất thu hồi bám sát tần suất claim |
| **2. Cron quét an toàn (phụ)** | Lịch thưa (Hobby: hằng ngày; Pro: mỗi phút) | Bắt job mồ côi khi **không còn** worker nào poll |

Ràng buộc: mỗi lượt reap **giới hạn theo số dòng và thời gian** để route claim không vượt ngân sách
thời gian; thao tác **idempotent**, an toàn với cold start.
Hành vi: đóng `job_attempt` đang mở với `outcome='EXPIRED'` → so `execution_attempt` với
`max_attempts` → `QUEUED` hoặc `FAILED`. Artifact của attempt hết hạn giữ `PROVISIONAL` và
**không bao giờ** được promote.

**Kiểm thử bắt buộc:** kịch bản phục hồi phải xanh **khi đã tắt cron** — chứng minh tầng 1 tự đủ.

---

## 8. Năm luồng CLI *(theo brief §6)*

### 8.1 Pull content
```
CLI POST /api/worker/jobs/claim
 → API xác thực worker + trả job + manifest_sha256
 → CLI GET /manifest (verify sha256)
 → CLI GET /revisions/{id}  (script, SEO — text trong JSON)
 → CLI GET /revisions/{id}/sources (source manifest)
```

### 8.2 Analyze / Score
```
CLI chạy rule engine hoặc AI CLI (agy/codex) cục bộ
 → POST /api/worker/jobs/{id}/audits   { gate, status, findings[] }
 → POST /api/worker/jobs/{id}/scores   { algorithm_key, algorithm_version,
                                          input_snapshot_hash, dimensions[], overall_score,
                                          explanation, findings, recommendations }
```
Server **verify** `input_snapshot_hash == content_revision.content_sha256`; lệch ⇒ 409
`SNAPSHOT_MISMATCH` (chống gán điểm cho nội dung khác với nội dung đã chấm).
Ghi **append-only** — không bao giờ ghi đè `score_run` cũ.

### 8.3 Improve content
```
CLI GET revision hiện tại → phân tích → sinh bản cải thiện
 → POST /api/worker/revisions
     { content_item_id, parent_revision_id, change_reason,
       generator_name, generator_version, algorithm_version_id,
       triggered_by_score_run_id, ...nội dung text }
```
**Bất biến:** revision mới luôn vào `DRAFT` hoặc `REVIEW_REQUIRED`.
**Không bao giờ** ghi đè bản đã approve. Worker **không** được set `FROZEN` hay tạo `approval`.

### 8.4 Build content
```
API tạo build job (từ revision đã FROZEN + approval ACTIVE)
 → CLI claim → start → lấy production_manifest
 → CLI build audio/video/subtitle/thumbnail cục bộ
 → CLI POST /artifacts (metadata + sha256; FILE Ở LẠI LOCAL)
 → CLI POST /complete → server promote artifact
```

### 8.5 Sync analytics
```
Vercel Cron POST /api/cron/enqueue-analytics   (chỉ tạo job — token YouTube ở local)
 → CLI claim SYNC_ANALYTICS
 → CLI gọi YouTube Data/Analytics API bằng OAuth cục bộ
 → CLI normalize theo columnHeaders
 → POST /api/worker/analytics/snapshots  { partition, rows[], request_hash, response_hash }
 → API UPSERT + đẩy bản cũ sang _history (SCD-2)
```

---

## 9. Bảo mật

| Kiểm soát | Chi tiết |
|---|---|
| **Chống RCE** | `job_type` enum đóng ánh xạ tới **hàm Python đã đăng ký**. `params` validate bằng Zod **`.strict()`** — field lạ bị **từ chối**. Không trường nào truyền lệnh/đường dẫn nhị phân. Subprocess luôn argv-list, **cấm `shell=True`** (repo hiện đã sạch — giữ bằng test AST). |
| **Job payload injection** | Mỗi `job_type` có schema riêng; giá trị enum whitelist; độ dài giới hạn. |
| **Path traversal** | Đường dẫn **tương đối** trong workspace; worker resolve + no-follow; server kiểm cú pháp. |
| **Prompt injection từ nguồn** | Nội dung nguồn/LLM là **dữ liệu không tin cậy** — không đưa vào tên file/tham số subprocess; đánh dấu khi nạp vào prompt. |
| **CLI gửi dữ liệu giả** | Mọi ghi kèm `lease_token` + `job_attempt_id`; score gắn `input_snapshot_hash` server verify được. |
| **Agent tự approve** | `approval.approved_by` bắt buộc là **user thật**; worker không có endpoint approve. |
| **Cross-channel** | Truy vấn lọc theo quyền; trả **404** không phải 403. |
| **Replay** | `Idempotency-Key` + partial unique. |
| **Secret** | YouTube secret **không rời máy local**, không vào DB/Blob/log. |
| **Rate limit** | 60 claim/phút, 600 log-batch/phút mỗi worker. |
| **Kích thước** | Body ≤ 1 MB (log batch ≤ 256 KB) — dưới xa giới hạn 4,5 MB. |
| **Version** | `X-Worker-Protocol` không hỗ trợ ⇒ **426 Upgrade Required** + `min_supported_agent_version`. |

---

## 10. Xử lý race condition

| Tình huống | Cách xử lý |
|---|---|
| Hai worker claim cùng lúc | CAS **một câu lệnh** ⇒ nhiều nhất một worker thắng (read-committed đánh giá lại vị từ). Chạy trên **HTTP driver**. ⚠️ Các luồng **nhiều câu lệnh** (promote, ghi score, freeze/approve) phải dùng **Pool/WebSocket** — xem `TARGET_ARCHITECTURE.md §5.1` |
| Worker "chết rồi sống lại" ghi muộn | Mọi ghi kèm `lease_token` + `job_attempt_id`; lệch ⇒ 409 |
| Lease hết hạn giữa lúc complete | Kiểm lease **trong cùng transaction** với UPDATE trạng thái |
| Retry sinh artifact khác hash | `job_attempt` + promotion; chỉ `PROMOTED` publish được |
| Job hoãn vì quota bị tạo trùng | `DEFERRED` **nằm trong** partial unique |
| Revision bị sửa khi job đang chạy | `FROZEN` không sửa được; sửa = revision mới |
| Approval bị thu hồi khi đang build | Build vô hại; **publish** phải kiểm lại approval `ACTIVE` ngay trước khi gọi YouTube |
| Hai cron sync chồng nhau | Partial unique trên `analytics_sync_partition WHERE status='RUNNING'` |
| Đồng hồ worker lệch | Mọi hạn dùng giờ server |

---

## 11. Ma trận quyền (User API)

| Hành động | EDITOR | REVIEWER | APPROVER | READONLY |
|---|:-:|:-:|:-:|:-:|
| Xem nội dung kênh được gán | ✅ | ✅ | ✅ | ✅ |
| Tạo/sửa revision `DRAFT` | ✅ | — | — | — |
| Chạy audit / score | ✅ | ✅ | ✅ | — |
| Ghi audit finding | — | ✅ | ✅ | — |
| Freeze revision | — | — | ✅ | — |
| Approve / revoke | — | — | ✅ | — |
| Tạo build job | ✅ | — | ✅ | — |
| Quản lý worker/token | — | — | — | — |
*(`ADMIN` có tất cả.)*

**Tự-duyệt** theo `channel.approval_policy`:
- `SELF_APPROVAL_ALLOWED` (mặc định MVP, vì hệ thống hiện **một người dùng**): cho phép, **nhưng**
  bắt buộc xác nhận nâng cao (nhập lại mật khẩu + lý do) và ghi `audit_event.self_approved=true`.
- `TWO_PERSON_REQUIRED`: chặn `approved_by == created_by`.
- **Cả hai chế độ đều phải có test.**

> Cấm tuyệt đối tự-duyệt sẽ khiến hệ một người dùng không bao giờ approve được ⇒ người dùng sẽ tắt
> hẳn approval, phá đúng control cần bảo vệ.
