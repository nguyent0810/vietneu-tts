# BACKEND_MVP_SPEC.md

> Đặc tả **chính xác** lát cắt dọc đầu tiên. Đây là hợp đồng nghiệm thu của MVP.
> Không frontend. Toàn bộ chứng minh bằng **một test E2E gọi HTTP**.

---

## 1. Định nghĩa MVP

**MVP = Phase 0 → Phase 5.** Một content item đi trọn vòng qua backend thật.

```
Import 1 content package có sẵn (từ content_repo_clone hoặc registry.json)
 → content_item + content_revision lưu trong Neon (nội dung TEXT nằm trong DB)
 → source_document + content_item_source
 → **FREEZE** revision v1  ← bắt buộc TRƯỚC mọi audit/score (bất biến S-0)
 → CLI claim job ANALYZE_CONTENT → gửi audit_run + audit_finding
 → CLI claim job SCORE_CONTENT   → gửi score_run + score_dimension theo `algorithm_version.dimensions`
 → CLI claim job IMPROVE_CONTENT → tạo content_revision v2 ở DRAFT (sửa tự do vì **chưa** bị chấm)
 → USER **freeze** revision (chốt `content_sha256`)
 → USER **approve** revision **đã FROZEN**  (agent KHÔNG được approve)
 → tạo build_job BUILD_AUDIO
 → CLI claim → start → build audio cục bộ bằng render_engine
 → CLI gửi artifact metadata + sha256 (FILE Ở LẠI LOCAL)
 → backend verify + promote artifact
 → content_item.status = PRODUCTION_READY
```

---

## 2. Phạm vi tối thiểu

| Thực thể | Số lượng | Ghi chú |
|---|:-:|---|
| `channel` | 1 | `phat_giao` (đã có sẵn cấu hình) |
| `content_item` | 1 | `format=SHORT` (rẻ và nhanh nhất để chạy trọn vòng) |
| `content_revision` | 2 | v1 import, v2 do CLI cải thiện |
| `source_document` | ≥1 | từ `SOURCE_REGISTRY.md` của domain BUD |
| `audit_run` + `audit_finding` | 1 + n | gate `CONTENT_READY` |
| `algorithm` + `algorithm_version` | 1 + 1 | vd `HOOK_QUALITY_RULE@1.0.0` |
| `score_run` + `score_dimension` | 2 runs + **đúng số dimension mà `algorithm_version` v1 công bố** | chấm v1 và v2 để chứng minh delta |

> ⚠️ **Sửa theo Codex v2R1 BLOCKER-2.** Bản trước đòi "17 dimension mỗi lần chấm" và "34 dòng
> dimension", trong khi `ALGORITHM_VERSIONING_PLAN.md §3` quy định version **chỉ công bố tập
> dimension thật sự tính được**, và dimension thiếu đầu vào thì **không sinh dòng nào**.
> Hai điều đó loại trừ nhau ⇒ test E2E chỉ có thể xanh bằng cách **bịa điểm**.
>
> **Bằng chứng từ code:** `youtube_analytics.py:19-20` `DEFAULT_VIDEO_METRICS` **không có**
> `impressions`/`impressionClickThroughRate`, cũng không có dữ liệu nhân khẩu ⇒ `CTR_POTENTIAL`,
> `AUDIENCE_FIT`, `RETENTION_POTENTIAL` **chưa tính được** cho tới P6.
>
> **Tiêu chí đúng:**
> - Số dòng `score_dimension` = **`len(algorithm_version.dimensions)`** — suy ra từ dữ liệu, không hằng số.
> - Dimension thiếu đầu vào ⇒ **không có dòng**, phải nằm trong `score_run.missing_dimensions`.
> - `coverage_bp` < ngưỡng ⇒ `overall_score = NULL` (fail-closed), **không** điền 0.
> - v1 chỉ công bố tập tính được ở P2; dimension phụ thuộc analytics dời sang **P6**.
| `approval` | 1 | trên v2, do **user thật** |
| `worker_machine` + `worker_token` | 1 + 1 | máy local |
| `build_job` + `job_attempt` | 1 + 1 | `BUILD_AUDIO` |
| `artifact` | 1 | `AUDIO_WAV`, `storage_backend=LOCAL` |
| **Test E2E** | **1** | **chạy toàn bộ chuỗi trên** |

---

## 3. Job type trong MVP

Chỉ **4** trong allowlist 9 loại được implement ở MVP:

| Job type | MVP? | Handler gọi gì |
|---|:-:|---|
| `ANALYZE_CONTENT` | ✅ | rule engine cục bộ (+ tuỳ chọn `codex exec`) |
| `SCORE_CONTENT` | ✅ | rule-based scorer, **tập dimension v1 công bố** (không phải cả 17) |
| `IMPROVE_CONTENT` | ✅ | agy/codex sinh bản cải thiện → POST revision DRAFT |
| `BUILD_AUDIO` | ✅ | `render_engine.RenderSession` (handler hẹp, một revision, workspace riêng) |
| `BUILD_VIDEO` | ❌ | P6+ |
| `BUILD_SUBTITLE` | ❌ | P6+ |
| `BUILD_THUMBNAIL` | ❌ | P6+ |
| `SYNC_ANALYTICS` | ❌ | P6 |
| `EXPORT_PACKAGE` | ❌ | sau |

> Enum **đầy đủ 9 loại** vẫn được khai báo từ P4 để không phải migrate enum về sau;
> chỉ có 4 handler được đăng ký ở worker. Job type chưa có handler ⇒ worker **từ chối claim**
> (capability không khớp), không im lặng bỏ qua.

---

## 4. Endpoint tối thiểu

### User API
```
POST   /api/v1/auth/login
GET    /api/v1/me
GET    /api/v1/channels
POST   /api/v1/import/batches                 (mở batch: mode=DRY_RUN|APPLY)
POST   /api/v1/import/batches/:id/records     (nạp chunk ≤200 bản ghi vào STAGING; lặp)
POST   /api/v1/import/batches/:id/finalize    (chạy MỘT transaction: validate → mô phỏng/áp dụng)
GET    /api/v1/import/batches/:id/report

GET    /api/v1/content                       ?channel_id&status&cursor
GET    /api/v1/content/:id
GET    /api/v1/content/:id/revisions
GET    /api/v1/revisions/:id
GET    /api/v1/revisions/:a/diff/:b
POST   /api/v1/revisions/:id/freeze
POST   /api/v1/revisions/:id/approve
POST   /api/v1/approvals/:id/revoke
GET    /api/v1/content/:id/scores
GET    /api/v1/content/:id/audits
POST   /api/v1/jobs
GET    /api/v1/jobs/:id
POST   /api/v1/jobs/:id/cancel
GET    /api/v1/workers
POST   /api/v1/workers/enrollment-codes
```

### Worker API
```
POST   /api/worker/register
POST   /api/worker/token/rotate
PUT    /api/worker/capabilities
POST   /api/worker/jobs/claim
GET    /api/worker/jobs/:id/manifest
GET    /api/worker/revisions/:id
POST   /api/worker/jobs/:id/start
POST   /api/worker/jobs/:id/heartbeat
POST   /api/worker/jobs/:id/logs
POST   /api/worker/jobs/:id/audits
POST   /api/worker/jobs/:id/scores
POST   /api/worker/revisions                 (tạo revision cải thiện, luôn DRAFT)
POST   /api/worker/jobs/:id/artifacts
POST   /api/worker/jobs/:id/complete
POST   /api/worker/jobs/:id/fail
POST   /api/worker/shutdown
```

### Internal
```
GET    /api/internal/health                   (không auth, không chạm DB)
GET    /api/internal/readyz                   (token scope `ops`, chạm DB → db_ok, db_branch, migration_version)
POST   /api/internal/drain-reap               (token scope `ops` + ADMIN; thu hồi lease quá hạn khi DRAINING; có batch limit)
POST   /api/cron/reap-leases          (Vercel Cron, CRON_SECRET — chỉ là lưới an toàn)

> ⚠️ Reap **chính** chạy cơ hội ngay đầu mỗi `/api/worker/jobs/claim`, **không** phụ thuộc cron.
> Vercel Hobby chỉ cho cron 1 lần/ngày ⇒ nếu dựa vào cron thì kịch bản "giết worker → nhận lại job"
> của MVP **không chạy được** trên Hobby. Test phục hồi phải xanh **khi đã tắt cron**.
```

**Không có endpoint nào phục vụ UI.** Không có trang web nào ngoài `/api/*`.

---

## 5. Bất biến phải chứng minh trong MVP

| # | Bất biến | Chứng minh bằng |
|---|---|---|
| 1 | Revision `FROZEN` không sửa được | Test: UPDATE trực tiếp → trigger chặn |
| 2 | Job build trỏ revision đã `FROZEN` | Test: tạo job với revision `DRAFT` → 409 |
| 3 | Agent **không** approve được | Test: worker token gọi approve → 403/404 |
| 4 | Soạn revision v2 **không** thu hồi approval v1 | Test: tạo v2 DRAFT → approval v1 vẫn `ACTIVE` |
| 4b | **Không approve được revision chưa FROZEN** | Test: approve revision `DRAFT` → **CSDL từ chối** (FK composite), API trả 409 |
| 4c | **Approval khoá vào đúng bytes đã duyệt** | Test: `approved_content_sha256` phải khớp `content_revision.content_sha256` |
| 4d | **Bằng chứng approval không lấy từ revision khác** | Test: approve rev B viện dẫn audit/score của rev A → **CSDL từ chối** |
| 4e | **Promote đồng thời tuần tự hoá** | Test: hai transaction cùng `expected_production_revision_id=A`, promote B và C → **đúng một** thắng (kẻ thua 409); chuỗi event tuyến tính; revoke xen giữa ⇒ promote fail |
| 4f | **Promote không xoá approval gate khác** | Test: item có approval `ACTIVE` ở cả 4 gate → promote → chỉ `PRODUCTION_READY` của revision cũ bị `SUPERSEDED` |
| 4g | **Promote lần đầu & chống tự-promote** | `NULL→A` thành công (approval A vẫn `ACTIVE`); `A→A` ⇒ **409 `ALREADY_PRODUCTION`**, không đổi gì |
| 5 | Score **và dimension** append-only | Test: chấm lại → `run_sequence` mới, hàng cũ nguyên vẹn; UPDATE/DELETE trực tiếp trên **cả hai** bảng → trigger chặn |
| 6 | `overall_score` = Σ(dimension × weight), hoặc **NULL** khi coverage thấp | Test: tính lại khớp; thiếu dimension ⇒ `missing_dimensions` + `overall_score=NULL` |
| 7 | `input_snapshot_hash` khớp `content_sha256` — **ép bằng FK composite**, không phải CHECK | Test: gửi hash sai → **CSDL từ chối**; API trả 409 `SNAPSHOT_MISMATCH` |
| 8 | Một job một worker | Test race: 10 invocation đồng thời **trên Neon thật, dùng đúng HTTP driver của production** |
| 9 | Lease hết hạn ⇒ worker cũ bị từ chối | Test: ép hết lease rồi `complete` → 409 |
| 10 | Idempotency dùng chung (`idempotency_record`) | Test: `complete`/`approve`/`freeze`/`score` gọi 3 lần cùng key → 1 kết quả; cùng key khác body → 409 `IDEMPOTENCY_KEY_REUSED` |
| 11 | Chỉ artifact `PROMOTED` dùng được | Test: 2 attempt khác hash → 1 `PROMOTED` |
| 12 | Media **không** rời máy | Test: không request nào có body > 1 MB; `artifact.storage_backend='LOCAL'` |
| 13 | Log không chứa secret | Test: bơm `ghp_…` vào log → không có trong `job_event` |
| 14 | `params` field lạ bị từ chối | Test: Zod `.strict()` → 422 |
| 15 | Import idempotent + **insert-only** | Test: import 2 lần → 0 nhân đôi (`legacy_id_map`); trùng ⇒ `SKIPPED_DUPLICATE`; outcome `UPDATED` **không tồn tại** trong enum |
| 16 | Cross-channel bị chặn | Test: user kênh A đọc kênh B → **404**; **kể cả nhánh `source_document`** vốn scope theo `domain_id` |

---

## 6. Định nghĩa "xong" (Definition of Done)

- [ ] `pnpm test:e2e` chạy trọn chuỗi §1, xanh, **lặp lại được** (tự dọn dữ liệu)
- [ ] 16 bất biến §5 đều có test và đều xanh (gồm test race trên **Neon thật**)
- [ ] Deploy được lên Vercel preview và chạy E2E trên đó (không chỉ localhost)
- [ ] Migration chạy sạch trên Neon branch trống
- [ ] `apps/hub` CI xanh; CI upstream **không đổi**
- [ ] Không có secret trong DB, log, hay response
- [ ] Tài liệu OpenAPI sinh được từ Zod; client Python sinh được từ OpenAPI
- [ ] Media vẫn nằm ở `output/` — dung lượng DB < 50 MB
- [ ] **Diễn tập runbook restore** (`LEGACY_IMPORT_AND_SYNC_PLAN §6.1`) chạy được trên Neon branch thật, đo được RTO

---

## 7. Rõ ràng NGOÀI phạm vi MVP

Frontend, calendar UI, auto-publish, recommendation, phân tích analytics, Vercel Blob,
multi-tenant/workspace, dual-write (Phase B), migrate đủ 97 package, realtime/WebSocket,
web-based video/audio editor, embeddings, ML model.

---

## 8. Ước lượng

| Phase | Phức tạp | Ước tính (1 người) |
|---|:-:|---|
| P0 | M | ~1 tuần |
| P1 | M | ~1 tuần |
| P2 | L | ~2–3 tuần |
| P3 | M | ~1 tuần |
| P4 | L | ~2–3 tuần |
| P5 | M | ~1 tuần |
| **Tổng MVP** | | **~8–10 tuần** |

*(P3 ∥ P4 chạy song song được nếu có 2 người ⇒ rút còn ~6–7 tuần.)*
