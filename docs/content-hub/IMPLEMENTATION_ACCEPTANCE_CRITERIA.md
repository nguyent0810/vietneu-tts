# Implementation Acceptance Criteria

Chuyển 7 "Implementation Risks Remaining" (từ vòng Architecture Review cuối,
sau `ARCHITECTURE_APPROVED_FOR_IMPLEMENTATION`) thành **tiêu chí nghiệm thu
kiểm tra được**, gắn vào đúng phase phải đóng chúng.

Quy tắc: mỗi tiêu chí phải có **cách kiểm chứng tự động** (test/migration/lệnh),
không nghiệm thu bằng đọc tài liệu. Phase gate của phase tương ứng **không được
duyệt** nếu tiêu chí gắn với nó chưa PASS.

Trạng thái: `OPEN` → `DONE` (kèm bằng chứng) hoặc `WAIVED` (kèm lý do + người
quyết định).

---

## AC-1 — Composite FK cho artifact metadata

**Rủi ro:** `artifact.build_job_id`, `job_attempt_id`, `content_revision_id`,
`worker_machine_id` hiện là 4 FK độc lập. Một đường ghi bỏ qua validation ở
route có thể lưu metadata mâu thuẫn nội bộ (attempt không thuộc job đó).

**Phase:** 1 (schema) — **Không áp dụng cho MVP phân tích.**

**Tiêu chí:**
- `job_attempt` có unique `(id, build_job_id)`; `artifact` có FK composite
  `(job_attempt_id, build_job_id)` → `job_attempt(id, build_job_id)`.
- Integration test trên Postgres thật: chèn artifact với `job_attempt_id` thuộc
  job KHÁC `build_job_id` → phải bị DB từ chối (không phải chỉ app từ chối).

**Ghi chú phạm vi:** MVP mục tiêu là *analysis pipeline*, không build media.
Nếu Phase 1 không tạo bảng `artifact`/`job_attempt` thì AC-1 chuyển sang
`DEFERRED` và phải được nhắc lại khi bảng đó ra đời — **không được đóng im lặng**.

**Trạng thái:** OPEN

---

## AC-2 — `job_lease_history` ghi trong cùng câu lệnh claim

**Rủi ro:** câu CAS claim chỉ `UPDATE build_job`. Nếu ghi lịch sử lease bằng
câu lệnh thứ hai, hai worker chạy đua sẽ tạo lịch sử thiếu/lệch, và test
concurrency mất dữ liệu để khẳng định "đúng 1 worker thắng".

**Phase:** 1 nếu có hàng đợi job; nếu không → DEFERRED.

**Tiêu chí:**
- Việc ghi `job_lease_history` nằm trong **cùng một câu lệnh SQL** với CAS
  claim (writable CTE), không phải câu lệnh riêng.
- Test concurrency trên Neon thật: N=20 worker claim đồng thời 1 job → đúng
  1 thắng, và có đúng 1 dòng `job_lease_history` tương ứng.

**Trạng thái:** OPEN

---

## AC-3 — `run_sequence` khi `algorithm_version_id` NULL

**Rủi ro:** PostgreSQL coi các NULL là **khác nhau** trong ràng buộc UNIQUE.
Nếu `algorithm_version_id` nullable (audit do người/công cụ ngoài chạy), unique
`(content_revision_id, algorithm_version_id, run_sequence)` **không** ngăn được
hai run trùng `run_sequence`.

**Phase:** 1 (schema) + 3 (deterministic analysis ghi run đầu tiên).
**Đây là AC có khả năng gây hỏng dữ liệu cao nhất trong 7 mục** — analysis run
là thực thể trung tâm của MVP này.

**Tiêu chí:**
- Dùng **sentinel non-null** (ví dụ hàng `algorithm_version` đặc biệt cho
  "human/external") HOẶC partial unique index tách 2 nhánh NULL/NOT NULL.
- Integration test trên Postgres thật: chèn 2 analysis run cùng
  `(content_revision_id, run_sequence)` với `algorithm_version_id` NULL cả hai
  → phải bị từ chối.
- Test tương tự cho nhánh NOT NULL.

**Trạng thái:** OPEN

---

## AC-4 — Savepoint cho báo cáo import dry-run

**Rủi ro:** import cần rollback các hàng nghiệp vụ nhưng **giữ lại**
`import_record`, báo cáo và trạng thái batch cuối. Rollback cả transaction sẽ
xoá luôn bằng chứng đã chạy gì.

**Phase:** 2 (sync analytics là đường import thật đầu tiên).

**Tiêu chí:**
- Đường import dùng savepoint (hoặc 2 transaction tách bạch) sao cho: lỗi giữa
  chừng → dữ liệu nghiệp vụ rollback, nhưng `sync_run` vẫn kết thúc ở trạng
  thái `FAILED` **có ghi lỗi**, không phải biến mất.
- Integration test: ép lỗi giữa batch → khẳng định `sync_run.status='FAILED'`
  tồn tại VÀ không có metric nào của batch lỗi được lưu.

**Trạng thái:** OPEN

---

## AC-5 — Thứ tự FK `content_item.published_video_id`

**Rủi ro:** bảng `video` chỉ ra đời ở P6 trong lộ trình gốc; tạo FK sớm sẽ
migration fail.

**Phase:** 1 → 2 (Phase 2 tạo bảng `video` cho analytics, sớm hơn lộ trình gốc).

**Tiêu chí:**
- Cột thêm dạng **nullable, chưa có FK** ở migration sớm; FK thêm ở migration
  sau khi bảng `video` tồn tại.
- `npm run db:migrate` chạy sạch **từ database rỗng** theo đúng thứ tự
  migration (test này bắt buộc, không phải tuỳ chọn).

**Trạng thái:** OPEN

---

## AC-6 — Rate limit dùng chung cho serverless

**Rủi ro:** đếm trong bộ nhớ **không hoạt động** trên Vercel — mỗi invocation
là một process riêng, biến đếm reset liên tục. Rate limit sẽ *trông như* đang
chạy nhưng không chặn gì.

**Phase:** 1 (trước khi có route công khai đầu tiên).

**Tiêu chí:**
- Chọn **một** cơ chế dùng chung: Vercel Firewall HOẶC token bucket lưu ở Neon.
  Ghi rõ lựa chọn + lý do.
- Không tồn tại biến đếm rate limit ở module scope (kiểm bằng test/grep).
- Test: vượt ngưỡng → `429` kèm `Retry-After`, và ngưỡng đó phải giữ đúng khi
  request đến từ **2 instance khác nhau** (giả lập bằng 2 kết nối/2 process).

**Trạng thái:** OPEN

---

## AC-7 — Độ bền media local (rủi ro đã chấp nhận có ý thức)

**Rủi ro:** Neon giữ text + metadata; mất media local nghĩa là phải render lại.
Đây là hệ quả trực tiếp của quyết định "media ở lại máy local", **không phải
lỗi thiết kế**.

**Phase:** không phase nào phải "sửa" — nhưng phải **hiển thị được**.

**Tiêu chí:**
- Không có phase nào ngầm giả định media local là bền vững.
- Nếu Phase 1+ lưu metadata artifact: phải có `sha256` + đường dẫn local +
  `machine_id`, đủ để phát hiện file mất và biết phải render lại cái gì.
- Với MVP phân tích: **không có media nào tham gia** → xác nhận rõ điều này ở
  báo cáo cuối thay vì im lặng.

**Trạng thái:** OPEN (theo dõi, không chặn)

---

## Backlog bảo mật phát sinh ở Phase 0

| ID | Mô tả | Mức | Xử lý |
|---|---|---|---|
| `SEC-1` | `youtube_auth.py bootstrap --client-secret <...>` để lộ giá trị trong `ps`/shell history của máy local | LOW | Không chặn: chạy 1 lần/kênh, cả 3 kênh đã bootstrap xong. Nếu sau này cần bootstrap lại, đọc từ env/stdin thay vì argv. |
| `SEC-2` | Pre-commit hook chưa cài (cố ý) | LOW | Người dùng tự chạy `./scripts/install_hooks.sh` nếu muốn. Kiểm soát thật là quét toàn repo ở phase gate. |

---

## Bảng theo dõi tổng hợp

| AC | Chủ đề | Phase đóng | Chặn phase gate | Trạng thái |
|---|---|---|---|---|
| AC-1 | Composite FK artifact | 1 (nếu có bảng) | có, nếu bảng tồn tại | OPEN |
| AC-2 | Lease history trong CAS | 1 (nếu có job queue) | có, nếu queue tồn tại | OPEN |
| AC-3 | `run_sequence` + NULL | 1 và 3 | **có — luôn luôn** | OPEN |
| AC-4 | Savepoint import | 2 | **có** | OPEN |
| AC-5 | Thứ tự FK video | 1→2 | **có** | OPEN |
| AC-6 | Rate limit serverless | 1 | **có** | OPEN |
| AC-7 | Độ bền media local | mọi phase | không (theo dõi) | OPEN |
