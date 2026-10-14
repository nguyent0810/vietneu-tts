# LEGACY_IMPORT_AND_SYNC_PLAN.md

> **Viết lại toàn bộ (Codex v2R11).** Bản trước là di sản của mô hình "một bản ghi = một transaction"
> và liên tục mâu thuẫn với mô hình staging đã chốt — bốn vòng review liên tiếp đều phát sinh finding
> từ chính nó. Tài liệu này **thay thế hoàn toàn** bản cũ; **không** còn mục "superseded" để đối chiếu.
>
> Đọc kèm: `DATA_MODEL_PLAN.md §7`, `API_CONTRACT_PLAN.md §6.16`, `TARGET_ARCHITECTURE.md §5.1`.

---

## 1. Mục tiêu & nguyên tắc

| # | Nguyên tắc | Hệ quả |
|---|---|---|
| 1 | **Không làm mất file gốc** | Import **chỉ đọc**. Không sửa, không xoá, không di chuyển file nguồn |
| 2 | **Fail-closed** | Dữ liệu lạ/thiếu ⇒ **REJECTED**, không đoán, không điền mặc định |
| 3 | **Idempotent** | Chạy lại không nhân đôi, ở **cả hai** tầng: staging và nghiệp vụ |
| 4 | **All-or-nothing khi ghi nghiệp vụ** | `finalize` là **một** transaction; không có commit từng phần |
| 5 | **Insert-only ở MVP** | Đã tồn tại ⇒ `SKIPPED_DUPLICATE`. **Không UPDATE** ⇒ nhu cầu hoàn tác rất hẹp |
| 6 | **Không nuốt secret** | Allowlist field; gặp khoá nhạy cảm ⇒ **huỷ cả lô** |
| 7 | **Một chiều ở MVP** | File → DB (Phase A). Dual-write là Phase B, sau MVP |

---

## 2. Nguồn dữ liệu legacy (kiểm kê thực tế)

| Nguồn | Vị trí | Số lượng đo được | Ánh xạ |
|---|---|---|---|
| Registry Long | `output/long/*/registry.json` | 3 file | `content_item` + `content_revision` + `video` |
| Registry Short | `output/shorts/*/registry.json` | nhiều topic | như trên, `format=SHORT` |
| Content-Creator package | `content_repo_clone/DOMAINS/*/PRODUCTION_PACKAGES/**/manifest.json` | **97** | `content_item` + `content_revision` (nội dung text) |
| Source registry | `DOMAINS/*/SOURCES/SOURCE_REGISTRY.md` | 6 file | `source_document` — **hoãn**, xem §8 |
| Analytics review | `analytics_reviews/**/*.json` | nhiều | **chỉ** metadata video; **không** import metric (§8) |
| YouTube channel config | `.youtube_channels/*.json` | 3 | **chỉ** `channel_id`, `channel_label`, `channel_title`, `scopes`. **Tuyệt đối không** `client_secret`/`refresh_token` |

### 2.1 Khuyết tật dữ liệu đã xác minh (căn cứ thiết kế validate)

| ID | Khuyết tật | Bằng chứng | Xử lý |
|---|---|---|---|
| D1 | Có record **thiếu hẳn `status`** | `output/long/Hình Sự/registry.json :: EP001` | **REJECTED** — không đoán |
| D2 | `key` **không unique toàn cục** | cả 3 registry Long đều dùng key `EP001` | `legacy_id` phải **composite** (§3) |
| D3 | `manifest.episode_id` **đụng nhau** | `EP001` xuất hiện 2 lần | Chỉ `package_id` (97/97 unique) làm khoá |
| D4 | Đường dẫn treo / lẫn tuyệt đối-tương đối | `registry.json` trỏ sai thư mục topic | Chuẩn hoá + kiểm tồn tại; thiếu ⇒ cảnh báo, **không** chặn |
| D5 | Artifact **mồ côi** (không có registry) | `output/shorts/Hình Sự/`, `output/shorts/06/` | Bỏ qua, ghi vào report |
| D6 | `hook_score` phần lớn `None` | 10× `None`, 1× `8.0` | **Không** biến thành `score_run` (vi phạm S-2) |
| D7 | `short_mode` 13 biến thể cho 6 khái niệm | đo trên dữ liệu thật | Bảng ánh xạ **khai báo tường minh**, không heuristic chuỗi |

---

## 3. Chuẩn hoá định danh

**`legacy_id` là composite**, vì `key` và `episode_id` đều không unique (D2, D3):

```
REGISTRY_LONG   : "registry_long:{topic}:{key}"
REGISTRY_SHORT  : "registry_short:{topic}:{episode}:{segment_index}"
CC_PACKAGE      : "cc_package:{package_id}"          # package_id unique 97/97
YOUTUBE_CHANNEL : "yt_channel:{channel_label}"
```

`legacy_id_map(legacy_kind, legacy_id) → (entity_type, entity_id)` unique ⇒ **idempotency ở tầng nghiệp vụ**.
UUID vẫn là **UUIDv7 sinh mới** (giữ quy ước `DATA_MODEL_PLAN §0`), **không** dẫn xuất từ `legacy_id`.

---

## 4. Ánh xạ trạng thái

| Legacy | → Tầng sản xuất (Hub) | Ghi chú |
|---|---|---|
| `scripted` | `PLANNED` | |
| `video_ready` | `BUILT` | |
| `uploaded` | `PUBLISHED` **hoặc** `SCHEDULED` | `publish_at` **tương lai** ⇒ `SCHEDULED` (đã xác minh có record như vậy) |
| `dry_run_done` | `BUILT` | |
| `failed` | `BUILD_FAILED` | |
| `needs_review` | `NEEDS_REVISION` | |
| **thiếu / lạ** | — | **REJECTED** (D1) |

`content_status` (7) và `qa_status` (5) của Content-Creator giữ nguyên vào `cc_package_mirror`.
Chỉ package `READY_FOR_TTS_HANDOFF` + `qa_status ∈ {PASS, PASS_WITH_ADVISORIES}` mới tạo
`content_item` (khớp `content_repo.py:33-34`).

---

## 5. Quy trình import (mô hình chuẩn duy nhất)

| Bước | Endpoint | Driver | Ngữ nghĩa |
|---|---|---|---|
| 1 | `POST /import/batches` | HTTP | Mở lô, `mode ∈ {DRY_RUN, APPLY}` → `status=OPEN` |
| 2 | `POST /import/batches/:id/records` (lặp, ≤200) | HTTP | Ghi **`import_staging_record`**. Mỗi chunk **commit độc lập** — an toàn vì staging **không phải** bảng nghiệp vụ |
| 3 | `POST /import/batches/:id/finalize` | **Pool** | **Một transaction**: khoá lô → đọc **toàn bộ** staging → sắp theo **thứ tự phụ thuộc** → validate cả đồ thị → ghi |
| 4a | `DRY_RUN` | cùng transaction | **`ROLLBACK`** phần nghiệp vụ; `import_record` + report ghi **ngoài** transaction ⇒ **sống sót** |
| 4b | `APPLY` | cùng transaction | **`COMMIT`** các bản ghi hợp lệ; bản ghi lỗi ⇒ `REJECTED` (không import). **`ROLLBACK` toàn bộ** chỉ khi gặp **điều kiện huỷ lô** — xem §5.4 |
| 5 | *(hoàn tác)* | — | **Neon branch/PITR restore**, thao tác vận hành có runbook — §6 |

**Thứ tự phụ thuộc trong `finalize`:** `channel → content_item → content_revision → video → publish_record`.
Giải quyết **bên trong** transaction, **không** phụ thuộc thứ tự client nạp chunk.

### 5.1 Vòng đời lô — enum chính thức

```
OPEN → FINALIZING → { COMPLETED_DRY_RUN | APPLIED | FAILED }
```
*(Không có `ROLLING_BACK`/`ROLLED_BACK` — hoàn tác dùng Neon restore, §6.)*

| Trạng thái | Ý nghĩa | Cho phép |
|---|---|---|
| `OPEN` | đang nạp staging | `records`, `finalize` |
| `FINALIZING` | transaction đang chạy | — (khoá) |
| `COMPLETED_DRY_RUN` | mô phỏng xong, **không** ghi nghiệp vụ | đọc report |
| `APPLIED` | đã ghi nghiệp vụ | hoàn tác bằng **Neon restore** (§6) |
| `FAILED` | finalize lỗi ⇒ **không** ghi gì | đọc report |

> ⚠️ Enum này là **nguồn chuẩn**; `API_CONTRACT_PLAN §6.16` và `DATA_MODEL_PLAN §7` dùng **đúng** nó.

### 5.2 Outcome của từng bản ghi

`IMPORTED | SKIPPED_DUPLICATE | REJECTED`

> ⚠️ **`UPDATED` KHÔNG tồn tại ở MVP** — vì `APPLY` là insert-only. Bản ghi đã có trong
> `legacy_id_map` ⇒ `SKIPPED_DUPLICATE`. Chỉ thêm `UPDATED` khi đã có before-image đầy đủ (hậu-MVP),
> và khi đó phải **chặn ở tầng API** cho tới lúc cơ chế phục hồi tồn tại.

### 5.3 Idempotency hai tầng

| Tầng | Cơ chế | Hành vi khi lặp |
|---|---|---|
| **Staging** | unique `(import_batch_id, legacy_ref)` | `ON CONFLICT DO NOTHING` rồi so `legacy_sha256`: **trùng** ⇒ trả dòng cũ; **khác** ⇒ **409 `IMPORT_RECORD_CONFLICT`** |
| **Nghiệp vụ** | unique `legacy_id_map(legacy_kind, legacy_id)` | Đã có ⇒ `SKIPPED_DUPLICATE` |

⇒ Nạp trùng, nạp lại sau crash, hoặc **chia chunk khác đi** đều không sinh dòng thừa.

### 5.4 Hai loại thất bại — **phân biệt rõ**

> ⚠️ *Codex v2R12 HIGH-3.* Bản trước vừa nói "bất kỳ bản ghi nào fail ⇒ rollback toàn bộ", vừa nói
> "chỉ `SECRET_FIELD_PRESENT` mới huỷ lô, các reject khác chỉ ghi report". Hai câu **loại trừ nhau**.

| Loại | Ví dụ | Hệ quả |
|---|---|---|
| **Reject bản ghi** (validation) | thiếu `status` (D1), status lạ, thiếu trường bắt buộc, phụ thuộc không giải được | Bản ghi ⇒ **`REJECTED`**, **không** import. **Lô vẫn commit** các bản ghi hợp lệ |
| **Huỷ lô** (abort) | **Danh sách đóng**: `SECRET_FIELD_PRESENT`, lỗi hạ tầng/CSDL, vi phạm ràng buộc ngoài dự kiến | **`ROLLBACK` toàn bộ**, `status=FAILED`, **không** hàng nghiệp vụ nào tồn tại |

`finalize` vẫn là **một transaction**: bản ghi `REJECTED` đơn giản là **không được INSERT**, không
phải là lỗi transaction. Điều này giữ nguyên tính all-or-nothing **đối với những gì được ghi**.

> ⚠️ **Chốt: KHÔNG có ngưỡng tỉ lệ reject ở MVP** (Codex v2R13 HIGH-2). Chỉ **danh sách mã lỗi đóng**
> ở trên mới huỷ lô. Ngưỡng theo tỉ lệ đòi hỏi định nghĩa mẫu số, toán tử so sánh, chủ sở hữu cấu
> hình và hành vi ở biên — thừa cho MVP và là nguồn mơ hồ. Người vận hành đọc report rồi tự quyết
> có chạy lại hay không. **Quyết định IMP-B vì vậy đã đóng, không còn là câu hỏi mở.**

---

## 6. Rollback — **dùng Neon restore, KHÔNG xây cơ chế ứng dụng**

> ⚠️ **Đơn giản hoá có chủ đích (sau Codex v2R13).** Sáu vòng review liên tiếp (R8→R13) đều sinh
> finding từ đúng một chỗ: cơ chế rollback **tự xây ở tầng ứng dụng**. Mỗi lần vá lại lộ ra bề mặt
> mới — sổ cái thực thể một-nhiều, hash từng dòng, projection theo entity, chuẩn hoá JSON, cột
> `updated_at` mà có bảng không có, ngữ nghĩa chặn khi bị tham chiếu…
>
> **Đó là dấu hiệu thiết kế sai, không phải thiếu chi tiết.** Neon đã cung cấp sẵn
> **branch + point-in-time restore**, và nó **mạnh hơn** bất kỳ bộ gỡ đồ thị nào ta tự viết:
> khôi phục *toàn bộ* trạng thái nhất quán, không phụ thuộc việc ta có liệt kê đủ thực thể hay không.

### 6.1 Runbook hoàn tác — **thực thi được, không phải khẩu hiệu**

> ⚠️ *Codex v2R14 HIGH-3.* "Restore bằng Neon" **không** phải một lệnh SQL tự chạy: nó có thể **ngắt
> kết nối** tạm thời, và cơ chế branch thường đòi **đổi endpoint / connection string**. Không đặc tả
> thì đây chỉ là lời hứa.

**Cơ chế chuẩn (chọn dứt khoát): _branch-based restore_.**
Lý do: branch tạo ra một nhánh **bất biến, đặt tên được**, kiểm chứng được **trước** khi chuyển sang;
PITR theo timestamp phụ thuộc cửa sổ lưu trữ của gói và **không** kiểm chứng trước được.
`import_batch.restore_point` vì vậy lưu **tên branch**, không phải timestamp.

| # | Bước | Ai làm | Chi tiết |
|---|---|---|---|
| 0 | **Điều kiện** | — | Chỉ áp dụng cho lô `APPLIED`. Đã có `restore_point` (tên branch) |
| 1 | **Tạo restore point** *(trước `APPLY`)* | CLI, tự động | Gọi Neon API tạo branch `import-<batch_id>-pre`; lưu tên vào `import_batch.restore_point`. Thất bại ⇒ **không** chạy `APPLY` |
| 2a | **Bật `DRAINING`** | Người vận hành | Bật cờ `DRAINING` ⇒ `POST /worker/jobs/claim` trả **503 `DRAINING`** ngay (**không** cấp job mới), nhưng `start`/`heartbeat`/`complete`/`fail`/`shutdown` **vẫn chạy** để job đang dở kết thúc sạch |
| 2b | **Drain worker** | Người vận hành | Gọi `POST /worker/shutdown` (trả hết lease đang giữ). Chờ **cả hai** về 0: `open_attempts_remaining` **và** `leased_jobs_remaining` (tương ứng `job_attempt WHERE outcome IS NULL` và `build_job WHERE status IN ('LEASED','RUNNING')`) |
| 2b′ | **`drain-reap` khi quá hạn** | Người vận hành | Quá `drain_timeout` mà **`open_attempts_remaining > 0` HOẶC `leased_jobs_remaining > 0`** (không chỉ attempt mở) ⇒ gọi **`POST /api/internal/drain-reap`** (auth: **`api_token` scope `ops` + vai trò `ADMIN`**), **lặp khi `has_more=true`**. Dừng lặp khi `has_more=false`, rồi **kiểm quyết định**:
  · `open_attempts_remaining=0` **và** `leased_jobs_remaining=0` ⇒ **drain xong**, sang 2c;
  · còn `blocked_remaining > 0` ⇒ **hoặc** gọi lại với `force=true`, **hoặc** **huỷ cutover**.
  ⚠️ `has_more=false` **một mình không có nghĩa là drain xong**. Hợp đồng đầy đủ: `API_CONTRACT_PLAN §12.4` |
| 2c | **Quiesce ghi** | Người vận hành | Bật `READ_ONLY_MODE` ⇒ API trả **503 `READ_ONLY_MODE`** cho **mọi** route ghi (**không còn miễn trừ nào** — worker đã drain xong ở 2b). Chờ 0 transaction đang chạy |

> ⚠️ **Vì sao cần cờ `DRAINING` riêng, tách khỏi `READ_ONLY_MODE`** (Codex v2R15 HIGH-1, v2R16 HIGH-1):
>
> | Vấn đề | Nếu chỉ có `READ_ONLY_MODE` |
> |---|---|
> | `POST /worker/shutdown` **là route ghi** | Bật read-only trước ⇒ chính bước dừng worker bị **503 chặn** — runbook tự khoá mình |
> | Miễn trừ `heartbeat` để job chạy nốt | Worker **gia hạn lease vô hạn** ⇒ **không bao giờ** drain xong |
> | Sau khi shutdown | Worker **claim lại ngay** ở vòng poll kế tiếp ⇒ drain vô nghĩa |
>
> ⇒ **Hai cờ, hai mục đích:**
> - **`DRAINING`** — chỉ chặn **`claim`**. Job đang dở vẫn `start`/`heartbeat`/`complete`. Đây là thứ
>   khiến hàng đợi **cạn dần** thay vì bị đóng băng giữa chừng.
> - **`READ_ONLY_MODE`** — chặn **mọi** route ghi, bật **sau khi** đã drain xong. Không cần miễn trừ nào.
>
> ⚠️ **Điều kiện "drain xong" phải gồm cả job `LEASED` chưa `start`** (Codex v2R19 HIGH-1).
> Một job có thể đang **`LEASED`** mà **chưa có `job_attempt`** (worker đã claim nhưng chưa gọi
> `/start`). Nếu chỉ đếm `job_attempt WHERE outcome IS NULL`, drain sẽ **tưởng đã xong** trong khi
> worker vẫn giữ lease và có thể gọi `/start` ngay sau đó — tức là ghi vào DB **sau** khi ta tưởng
> đã đóng băng. ⇒ Điều kiện đúng là **cả hai** bộ đếm về 0, và `drain-reap` cũng phải thu hồi
> **lease không có attempt** (chuyển job `LEASED → QUEUED`), không chỉ attempt mở.

> ⚠️ **`drain_timeout` cần một thao tác THU HỒI THẬT, không chỉ "chờ lease hết hạn"** (Codex v2R17 HIGH-2).
> Lease hết hạn **không tự** đổi trạng thái CSDL: phải có **reaper** đóng `job_attempt` (`outcome='EXPIRED'`)
> và chuyển trạng thái job. Nhưng reaper **chính** chạy ở đầu `/jobs/claim` — mà `DRAINING` **đang chặn**
> claim; còn cron dự phòng trên Hobby chỉ chạy **1 lần/ngày**. ⇒ Nếu chỉ "chờ", điều kiện
> *0 attempt mở* có thể **không bao giờ** đạt.
>
> **`POST /api/internal/drain-reap`** (auth **`api_token` scope `ops` + `ADMIN`** — token **gắn user**, không phải secret dùng chung; **Pool**, hợp đồng đầy đủ ở
> `API_CONTRACT_PLAN §12.4`): thu hồi lease quá hạn, đóng attempt `EXPIRED`, chuyển job về
> `QUEUED`/`FAILED` theo `execution_attempt`.
> ⚠️ **Có batch limit** (`max_rows`/`max_ms`) — **không** một transaction quét hết; gọi lặp khi
> `has_more=true`. **Idempotent**.
>
> **Lease CHƯA quá hạn tại deadline:**
> **(a)** `force=true` ⇒ cưỡng bức hết hạn ngay (job về `QUEUED`, chạy lại sau restore);
> **(b)** `force=false` (**mặc định**) ⇒ `has_more=false` **nhưng** `blocked_remaining > 0`
> ⇒ người vận hành **huỷ cutover** hoặc gọi lại với `force=true`.
> ⚠️ Bộ đếm còn lại **có thể nằm ở nhóm nào cũng được**: job đã claim nhưng **chưa `/start`** sẽ có
> `open_attempts_remaining = 0` mà `leased_jobs_remaining > 0` (vì `job_attempt` chỉ được tạo ở
> `/start` — `API_AND_WORKER_PROTOCOL §4.4`). ⇒ **Luôn kiểm cả hai bộ đếm**, không suy từ một cái.
> Không có lựa chọn "im lặng bỏ qua".
| 3 | **Kiểm chứng branch** | Người vận hành | Kết nối **trực tiếp** vào branch khôi phục, chạy truy vấn kiểm tra (đếm bảng chính, xác nhận **không** có dữ liệu của lô) — **trước khi** chuyển |
| 4 | **Chuyển endpoint** | Người vận hành | Đổi endpoint production sang branch đã kiểm chứng, hoặc cập nhật `DATABASE_URL` trong Vercel env rồi **redeploy** |
| 5 | **Xác nhận hoàn tất** | Người vận hành | `GET /api/internal/readyz` (**có** chạm DB) trả 200 và báo đúng `db_branch`; chạy lại truy vấn kiểm chứng ở bước 3 qua API |

> ⚠️ `/api/internal/health` theo hợp đồng **không chạm DB** và chỉ trả thông tin process/build
> (Codex v2R15 HIGH-2) ⇒ **không** dùng nó để xác nhận restore. Dùng **`/readyz`** — endpoint riêng
> có kiểm tra DB — và bổ sung trường `db_branch` vào **hợp đồng của `/readyz`**, không phải `/health`.
| 6 | **Mở lại ghi** | Người vận hành | Tắt `READ_ONLY_MODE`; khởi động lại worker; worker **tự** đăng ký lại và claim tiếp |
| 7 | **Ghi audit** | Tự động | `audit_event(action='IMPORT_RESTORED', before={branch cũ}, after={branch mới, batch_id})` |

**Quyền & bí mật:**
- Thao tác **Neon** (tạo branch, đổi endpoint) cần **API key Neon riêng cho vận hành**, **không** nằm
  trong env ứng dụng — ứng dụng không được tự restore chính nó.
- Thao tác **HTTP** trong runbook dùng **`api_token` scope `ops` gắn user** (§12.3 `API_CONTRACT_PLAN`)
  — **không** phải secret dùng chung, để `audit_event.actor_id` ghi **đúng người** đã chạy:
  · **`readyz`** — chỉ cần scope `ops` (chỉ đọc trạng thái);
  · **`drain-reap`** — cần scope `ops` **và** vai trò **`ADMIN`** (đổi trạng thái job).

**Client kết nối lại:** Vercel function tạo kết nối **theo request** ⇒ tự động dùng
`DATABASE_URL` mới sau redeploy. Worker gặp lỗi kết nối ⇒ retry có backoff; lease đang giữ hết hạn
tự nhiên và job quay lại `QUEUED`.

**Hệ quả phải chấp nhận (nói thẳng):**
- Restore là **toàn cơ sở dữ liệu**, **không** chọn lọc theo lô. Mọi thay đổi **sau** restore point
  — kể cả `import_record`, report, `audit_event` — **đều mất**. Vì vậy phải **xuất report ra ngoài DB**
  (file/artifact cục bộ) **trước** khi restore nếu muốn giữ.
- Có **downtime**. Đo `RTO` trong diễn tập (I-IMP6) và ghi vào runbook.
- ⇒ Chỉ dùng khi import hỏng **trước khi** có dữ liệu vận hành thật. Sau giai đoạn đó, nhu cầu
  hoàn tác chọn lọc phải được thiết kế lại **có chủ đích**, không chắp vá.

**Hệ quả — những thứ **KHÔNG** còn tồn tại ở MVP:**
- ❌ `POST /import/batches/:id/rollback` (endpoint bị **gỡ khỏi MVP**)
- ❌ Bảng `import_entity_link` và mọi cột ảnh chụp (`inserted_row_sha256`, `inserted_updated_at`)
- ❌ Mã lỗi `IMPORT_ROLLBACK_BLOCKED`
- ❌ Trạng thái lô `ROLLING_BACK` / `ROLLED_BACK`

**Đánh đổi (nói thẳng):** restore là thao tác **toàn cơ sở dữ liệu**, không chọn lọc theo lô. Ở MVP
điều đó chấp nhận được vì import chạy **trước khi** có dữ liệu vận hành thật, và `APPLY` là
insert-only nên trường hợp cần hoàn tác rất hẹp. Nếu về sau cần rollback chọn lọc, hãy thiết kế lại
**có chủ đích** — với đầy đủ ledger, hash và projection — chứ không nhét vào MVP.

**Vòng đời lô rút gọn:**
```
OPEN → FINALIZING → { COMPLETED_DRY_RUN | APPLIED | FAILED }
```

## 7. Reconciliation & sync

**MVP = Phase A, một chiều file → DB.** Reconciliation **chỉ báo cáo**, không tự sửa.

| Loại lệch | Phát hiện | Hành động ở MVP |
|---|---|---|
| Có ở file, thiếu ở DB | quét `legacy_id_map` | Báo cáo ⇒ chạy import lô mới (insert-only) |
| Có ở DB, mất ở file | đối chiếu đường dẫn | Báo cáo; **không** xoá DB |
| Cùng `legacy_id`, **khác** `legacy_sha256` | so hash | **Báo cáo drift** — **không** tự re-import, **không** UPDATE (insert-only). Do người dùng quyết |

Chuyển sang Phase B (dual-write) chỉ khi reconciliation **sạch 7–14 ngày liên tục**, và mọi ghi đi
qua **một adapter duy nhất** với quy tắc thắng khai báo trước.

---

## 8. Cố ý HOÃN (có lý do)

| Hạng mục | Vì sao hoãn |
|---|---|
| `SOURCE_REGISTRY.md` → `source_document` | `grep -c http` = **0** trên cả 6 file ⇒ `canonical_url_hash` luôn NULL ⇒ **phá khoá dedupe**. 3/6 file là stub rỗng |
| Metric analytics từ `analytics_reviews/` | 4/6 file `resultTable` có `rows: []`; bundle tự khai "day dimension là PT-bucketed, không phải UTC" ⇒ import vào bảng theo ngày sẽ **sai lịch sử vĩnh viễn** |
| `hook_score` → `score_run` | Phần lớn `None` (D6); tạo score giả vi phạm S-2 |
| Approval hồi tố cho 14 video đã đăng | **Cần người dùng quyết** — §11 |

---

## 9. An toàn

1. **Allowlist field** khi đọc `.youtube_channels/*.json`: chỉ 4 khoá. Gặp `client_secret`/`refresh_token`
   ⇒ **`SECRET_FIELD_PRESENT`, huỷ cả lô** (ngoại lệ duy nhất của quy tắc reject-từng-bản-ghi).
2. **Không log** giá trị nhạy cảm; `raw_payload` trong staging phải qua redaction **trước khi ghi**.
3. Checksum `legacy_sha256` cho mọi bản ghi ⇒ phát hiện file đổi giữa hai lần nạp.
4. Import chạy ở **CLI** (đọc filesystem local); Vercel **không** đọc được `content_repo_clone`.

---

## 10. Bất biến & test

| ID | Bất biến | Test |
|---|---|---|
| I-IMP1 | Import idempotent ở tầng nghiệp vụ | Import 2 lần ⇒ 0 nhân đôi (`legacy_id_map`) |
| I-IMP2 | Không nuốt secret | Payload có `refresh_token` ⇒ **huỷ lô**, DB sạch |
| I-IMP3 | **Hoàn tác bằng Neon restore** | Tạo restore point → `APPLY` → chạy runbook §6.1 → DB về **đúng** trạng thái trước `APPLY` (kể cả `import_record`/report — restore là toàn DB). Ghi `audit_event(IMPORT_RESTORED)` **sau** khi restore xong. ⚠️ **Không** kỳ vọng giữ lại dòng sinh sau restore point — Neon restore **không** chọn lọc được |
| I-IMP4 | Staging idempotent theo `legacy_ref` | Nạp trùng / chia chunk khác ⇒ không dòng thừa; khác hash ⇒ **409** |
| I-IMP5 | `finalize` all-or-nothing **đối với điều kiện huỷ lô** | (a) 1 bản ghi **validation-reject** ⇒ các bản ghi hợp lệ **vẫn commit**, bản lỗi `REJECTED` trong report. (b) Gặp **điều kiện huỷ lô** (§5.4) ⇒ **không** hàng nghiệp vụ nào tồn tại, `status=FAILED`, report vẫn ghi |
| I-IMP6 | **Runbook restore chạy được thật** | Diễn tập trên Neon branch thật: quiesce → restore → đổi endpoint → kiểm chứng → client kết nối lại. Đo được **RTO** và khẳng định ứng dụng hoạt động bình thường sau đó |
| I-IMP7 | `APPLY` insert-only | Đã có ⇒ `SKIPPED_DUPLICATE`; outcome `UPDATED` **không tồn tại** |
| I-IMP8 | Fail-closed với dữ liệu lỗi | Record thiếu `status` (D1) ⇒ `REJECTED`, có lý do trong report |
| I-IMP9 | `legacy_id` composite | Ba registry cùng key `EP001` (D2) ⇒ ba `content_item` khác nhau |
| I-IMP10 | Restore point được tạo trước `APPLY` | `import_batch.restore_point` **NOT NULL** sau khi `finalize` ở `mode=APPLY`; runbook restore chạy được trên Neon branch thật |
| I-IMP11 | Enum trạng thái lô đúng | Parse cả 5 giá trị hợp lệ; **từ chối** `RUNNING`/`COMPLETED`/`ABORTED`/`ROLLING_BACK`/`ROLLED_BACK` (đã gỡ) |

**Fixture:** copy **chính** các file registry thật — chúng đã chứa sẵn D1/D2/D4/D6/D7, không cần bịa.

---

## 11. Quyết định cần người dùng

| ID | Câu hỏi | Vì sao cần |
|---|---|---|
| **IMP-A** | 14 video đã đăng có cần **approval hồi tố** không? | Nếu có, sổ approval sẽ mang tên người vận hành cho nội dung họ chưa từng duyệt — làm sai lệch lịch sử. Nếu không, chúng tồn tại ở trạng thái "đã publish nhưng chưa approve" |
| ~~IMP-B~~ | ~~Ngưỡng reject để huỷ lô~~ | ✅ **ĐÃ ĐÓNG** — không có ngưỡng tỉ lệ ở MVP; chỉ danh sách mã lỗi đóng ở §5.4 |
