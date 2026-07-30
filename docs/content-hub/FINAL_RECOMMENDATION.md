# FINAL_RECOMMENDATION.md

> Bản tóm tắt để ra quyết định. **Phạm vi: backend-first.** Frontend hoãn tới Phase 8.
> Chi tiết kỹ thuật ở các tài liệu còn lại trong `docs/content-hub/`.

---

## 1. Kiến trúc đề xuất (một câu)

**Một backend Next.js chạy trên Vercel làm control plane, Neon PostgreSQL làm source of truth cho
dữ liệu có cấu trúc và nội dung text, còn toàn bộ việc nặng (TTS, ffmpeg, AI CLI, media) chạy trên
Local CLI vốn *kéo* job qua HTTPS — media không bao giờ rời máy local.**

```
Repo automation hiện có  +  Content-Creator (governance)
              ↓
        Local CLI / Worker (Python)
              ↓ HTTPS outbound
        Vercel Backend / API  (control plane)
              ↓
        Neon PostgreSQL  (source of truth)
        [Vercel Blob — thiết kế sẵn, KHÔNG bật ở MVP]
```

---

## 2. Ba quyết định định hình toàn bộ thiết kế

| # | Quyết định | Vì sao |
|---|---|---|
| **1** | **Chỉ nội dung text lên backend; media ở lại local** *(quyết định của người dùng)* | Script lớn nhất **67,8 KB**, JSON lớn nhất **194,8 KB** — vừa khít Postgres, dư **23–66×** so với giới hạn body 4,5 MB của Vercel. Media trung bình **337 MB/video** (25,3 GB) thì không thể và không cần đi qua API. |
| **2** | **Không dùng Vercel Blob ở MVP** | Hệ quả trực tiếp của (1): không còn gì lớn để lưu. Bớt một dịch vụ ⇒ bớt secret, bớt chi phí, bớt bề mặt tấn công. Cột `storage_backend`/`blob_url` đã có sẵn để bật sau mà không phải migrate phá vỡ. |
| **3** | **Vercel = control plane, không phải compute plane** | Giới hạn cứng: body **4,5 MB**, max **300s** (Hobby) / **800s** (Pro). TTS/ffmpeg/render **không thể** chạy ở đó. Đây là lý do kiến trúc CLI-kéo-job tồn tại, không phải lựa chọn phong cách. |

---

## 3. Backend MVP (lát cắt dọc)

**MVP = Phase 0 → Phase 5**, ước tính **~8–10 tuần** (1 người; ~6–7 tuần nếu P3 ∥ P4 có 2 người).

```
Import 1 content package có sẵn
→ content + revision lưu trong Neon (nội dung TEXT nằm trong DB)
→ source + metadata liên quan
→ CLI chạy audit → gửi audit result
→ lưu score nhiều dimension (kèm algorithm_version)
→ CLI tạo revision cải thiện (DRAFT)
→ USER **freeze** revision (chốt hash) → USER **approve** revision đã FROZEN
→ tạo build job → CLI claim → build 1 artifact (audio)
→ gửi metadata + checksum (FILE Ở LẠI LOCAL)
→ backend verify + promote → content PRODUCTION_READY
```

Tối thiểu: 1 channel · 1 content item · 2 revision · 1 source · 1 audit run · 2 score run ·
1 approval · 1 worker · 1 build job · 1 artifact · **1 test E2E API đầy đủ**.
Chỉ **4/9** job type được implement (`ANALYZE_CONTENT`, `SCORE_CONTENT`, `IMPROVE_CONTENT`, `BUILD_AUDIO`).

Chi tiết: `BACKEND_MVP_SPEC.md`.

---

## 4. Data ownership

| Dữ liệu | Nơi lưu | Khi nào thành source of truth |
|---|---|---|
| Structured (channel, item, revision, score, audit, approval, job, analytics) | **Neon** | Ngay từ P2 |
| Nội dung **text** (script, SEO, outline, hook, prompt, description) | **Neon** (`text`/`jsonb`) | Phase A: mirror từ file → Phase C: DB là gốc |
| Media (`.mp4` avg 337 MB, `.wav`) | **Local filesystem** | **Luôn luôn local**; DB chỉ giữ `local_path` + `sha256` + `size` |
| Log build lớn, evidence bundle | Local (hoặc Blob nếu bật sau) | — |
| Secret YouTube (`client_secret`, `refresh_token`) | **Chỉ máy local**, chmod 600 | **Không bao giờ** vào Neon/Blob/log |
| Nguồn biên tập gốc (research/script/QA) | **Content-Creator repo** (chỉ đọc) | Hub import + index, không ghi ngược |

**Chuyển source of truth có kiểm soát:** A (file là gốc, DB mirror) → B (dual-write qua adapter, có
reconciliation) → C (DB là gốc, file export) → D (file chỉ còn compatibility layer).
**MVP dừng ở A** (một chiều file→DB). **Cấm** nhảy thẳng DB-only.

**Xử lý conflict:** Phase A không có conflict (một chiều). Sang Phase B, mọi ghi phải qua **một
adapter duy nhất**; drift phát hiện bằng reconciliation report; quy tắc thắng phải khai báo tường
minh **trước** khi bật B.

---

## 5. API surface

| Nhóm | Prefix | Caller | Auth |
|---|---|---|---|
| **User API** | `/api/v1/*` | Frontend tương lai, người dùng, CLI-as-user | Session / PAT |
| **Worker API** | `/api/worker/*` | Local CLI | Worker token |
| **Cron** | `/api/cron/*` | Vercel Cron | `CRON_SECRET` |
| **Internal** | `/api/internal/*` | Nội bộ deployment | Không lộ ra ngoài |

Nhóm domain: `channels · videos · content · revisions · scores · audits · approvals · sources ·
artifacts · calendar · analytics · recommendations · workers · jobs · import · sync`.
Chi tiết từng endpoint: `API_CONTRACT_PLAN.md`.

**Tách nhóm auth là bắt buộc** — worker token **không** mở được User API và ngược lại. Chặn kịch bản
"CLI bị chiếm ⇒ đọc/sửa toàn bộ dữ liệu người dùng".

---

## 6. CLI integration & security boundary

**Năm luồng:** Pull content · Analyze/Score · Improve · Build · Sync analytics.

**Ranh giới bảo mật cốt lõi:**
- Server **không bao giờ** gửi shell command. Job mang `job_type` thuộc **allowlist đóng 9 loại**;
  worker tự ánh xạ sang hàm Python đã cài sẵn.
- `params` validate bằng Zod **`.strict()`** — field lạ bị **từ chối**.
- Subprocess luôn argv-list, **cấm `shell=True`** (repo hiện đã sạch — giữ bằng test AST).
- Secret YouTube **không rời máy local**.
- **Algorithm không được tự approve nội dung do chính nó tạo** — `approval.approved_by` bắt buộc là
  user thật; revision do agent tạo luôn vào `DRAFT`.
- Redaction log hai lớp (worker trước khi gửi, server trước khi ghi).
- Job lease + `job_attempt` + ba bộ đếm tách biệt (`claim_count` / `execution_attempt` /
  `quota_deferral_count`), `DEFERRED` nằm trong partial unique.

---

## 7. Tái sử dụng code hiện có

### Tái dùng ở mức **hàm thư viện** (gọi từ handler mới; không sửa file gốc)
| Thành phần | Vai trò |
|---|---|
| `render_engine.py` (`RenderSession`) | Lõi TTS cho handler `BUILD_AUDIO` |
| `youtube_auth.py` | OAuth đa kênh + refresh (chạy ở local) |
| `youtube_upload.py` | Upload resumable + quota + scheduling (P6+) |
| `youtube_catalog.py` | Danh mục video (P6) |
| `content_repo.py` | Đọc Content-Creator (chỉ đọc) |
| `content_seo.py`, `short_*_review.py`, `short_judge_panel_engine.py` | Audit/score runner |
| `TOOLS/package_audit.py` (repo ngoài) | Audit runner cho gate Content Ready |
| `registry_lock.py` | Pattern khoá file cho prune cục bộ |

### Tái dùng **khái niệm** (nâng từ file lên DB)
`registry.json` → `content_item` + `build_job` + `publish_record` ·
`FileLock`/`rotation_state` → job leasing · `needs_review` → audit gate ·
`TERMINAL_STATUSES`/`MAX_RETRIES` → chính sách retry · artifact `NN_*.json` → bảng `artifact` ·
manifest schema v2.0 + enum `content_status`/`qa_status` → state machine biên tập ·
source Tier 1–6 → `source_document.tier`

### ⚠️ **KHÔNG** tái dùng
`long_batch_runner.py`, `short_batch_runner.py` — là **orchestrator phạm vi-topic** với state dùng
chung: `run_audio_stage(topic)` xử lý **mọi tập sẵn sàng của topic** (`:155-160`), `run_step(cmd)`
nhận argv tuỳ ý (`:195-199`). Worker **không bao giờ** gọi chúng; chúng ở ngoài Hub làm đường chạy
song song trong lúc chuyển đổi.

### Không đụng tới
`src/vieneu/**`, `src/vieneu_utils/**`, `apps/gradio_main.py`, `apps/web_stream.py`, `tests/`,
`docker/`, `pyproject.toml [project].dependencies`, CI hiện có, và nội dung `content_repo_clone/`.

---

## 8. Thứ tự triển khai

```
P0 Stabilize ─► P1 Backend foundation ─► P2 Content core ─┬─► P3 Legacy import ─┬─► P5 E2E MVP ⭐
                                                          └─► P4 CLI protocol ──┘        │
                                                                                          ▼
                                                                    P6 Analytics ─► P7 Recommendation
                                              P8 Frontend ◄── (chỉ sau khi có mockup người dùng duyệt)
```
Đường găng: **P0 → P1 → P2 → {P3 ∥ P4} → P5**.

---

## 9. Quyết định cần người dùng duyệt

| # | Quyết định | Khuyến nghị | Vì sao quan trọng |
|---|---|---|---|
| **D1b** | **Chiến lược transaction**: Pool/WebSocket cho luồng tương tác, hay dồn vào hàm PL/pgSQL để giữ HTTP thuần? | **Pool/WebSocket** cho promote/score/freeze-approve; HTTP cho claim và truy vấn đơn | Neon HTTP **không** giữ được `FOR UPDATE` qua nhiều lời gọi ⇒ tách nhiều lời gọi sẽ mở lại race. PL/pgSQL giữ được HTTP thuần nhưng đẩy logic nghiệp vụ vào DB, khó test/review |
| **D1** | **ORM / query layer** | **Drizzle + drizzle-kit** | Không có engine binary ⇒ cold start tốt hơn Prisma trên serverless; SQL trong suốt để viết câu **CAS** của job claim và các **FK composite** (snapshot/approval/job-frozen) mà vẫn giữ type-safety; migration là file SQL review được |
| **D2** | **Ngôn ngữ backend: TypeScript?** | **TypeScript** | Vercel tối ưu cho Node; Drizzle/Zod là hệ sinh thái TS. ⚠️ Repo hiện **thuần Python** ⇒ rủi ro năng lực thật (R68). Nếu bác bỏ, cân nhắc Python runtime trên Vercel nhưng mất Drizzle/Zod |
| **D3** | **Auth strategy** | Tự dựng tối thiểu: Argon2id + token đục + session; PAT cho CLI-as-user; worker token riêng | Chưa có frontend ⇒ không cần OAuth/social. Auth.js là thừa và thêm lock-in |
| **D4** | **Chế độ migration file→DB** | **Phase A (một chiều) ở MVP**; B chỉ sau khi reconciliation sạch 7–14 ngày | Nhảy thẳng dual-write/DB-only sẽ tạo hai nguồn sự thật |
| **D5** | **Worker authentication** | Bearer token liên kết máy + TTL + xoay overlap; mTLS/DPoP **sau** MVP | Phải nói thẳng: bearer **không** chứng minh sở hữu máy |
| **D6** | **Blob retention** | **Không bật Blob ở MVP**; media local theo `retention_status` | Xem §2 |
| **D7** | **Khi nào DB thành source of truth** | Sau Phase B ổn định ≥14 ngày không drift | Cần tiêu chí đo được, không cảm tính |
| **D8** | **Analytics sync model** | Vercel Cron **chỉ enqueue**; CLI thực thi (token ở local); channel daily, video ≤28 ngày daily, video cũ weekly | Vercel **không thể** tự gọi YouTube |
| **D9** | **Multi-tenant/workspace ngay MVP?** | **Không.** Chỉ multi-**channel**; `workspace_id` thêm vào `channel` sau | Một người dùng; thêm sớm là over-engineering |
| **D10** | Thu hẹp OAuth scope (bỏ `youtube` toàn quyền) | **Có**, nếu không cần xoá/sửa video ngoài upload | Giảm thiệt hại nếu token lộ |

---

## 10. Giả định còn lại

| ID | Giả định | Cách xác minh |
|---|---|---|
| A1 | Người dùng chấp nhận backend TypeScript (D2) | Người dùng xác nhận |
| A2 | Có tài khoản Vercel + Neon, **gói nào** — ảnh hưởng max duration 300s vs 800s | Người dùng xác nhận |
| A3 | 3 OAuth client = 3 Google Cloud project ⇒ 3 quota pool riêng | Google Cloud Console |
| A4 | Content-Creator **tiếp tục** là nơi biên tập, không bị bỏ | Người dùng xác nhận |
| A5 | Chỉ một người dùng thao tác ⇒ `SELF_APPROVAL_ALLOWED` là mặc định hợp lý | Người dùng xác nhận |
| A6 | Máy macOS này là máy build duy nhất ≥6 tháng tới | Người dùng xác nhận |
| A7 | Chấp nhận backend chạy song song pipeline cũ một thời gian | Người dùng xác nhận |

---

## 11. Tiêu chí để bắt đầu implement

- [ ] D1, D2, D3 được chốt (**D2 quan trọng nhất** — quyết định ngôn ngữ)
- [ ] D4, D8, D9 được chốt
- [ ] Automation code đã commit an toàn (P0), không lọt secret
- [ ] Xác nhận phạm vi MVP = **P0→P5**, chỉ 4/9 job type
- [ ] Xác nhận A2 (gói Vercel/Neon) và A4
- [ ] Codex review đạt **APPROVED** (`CODEX_PLAN_REVIEW.md`)

---

## 12. Đánh giá thẳng thắn

**Điểm mạnh của hiện trạng:** người viết đã tự khám phá ra leasing, idempotency, retry budget,
circuit breaker, fail-closed gate và kỷ luật bảo mật (không `shell=True`, token không vào
`.git/config`, attribution license tự động, `finalize_episode.py` chỉ dọn sau khi upload thành công).
Nền tảng tư duy tốt hơn nhiều dự án cùng quy mô.

**Điểm yếu nghiêm trọng nhất:** 9.064 dòng code đang chạy production mà **không có version control**.
Phải sửa trước cả khi bàn tới kiến trúc.

**Rủi ro kỹ thuật dễ bỏ sót nhất:** claim job phải giữ nguyên hình dạng **một câu lệnh**
`UPDATE … RETURNING`. PostgreSQL bọc mọi câu lệnh đơn trong transaction ngầm ⇒ HTTP driver của
Neon là đủ. Nhưng nếu ai đó tách thành SELECT rồi UPDATE riêng, transaction ngầm **không còn** bao
trùm và **hai worker sẽ nhận cùng một job** — lỗi âm thầm, chỉ lộ khi tải cao. Bắt buộc có test race
trên Neon thật **và** test chống hồi quy hình dạng câu lệnh (R30, `API_AND_WORKER_PROTOCOL §4.1.1`).

**Cạm bẫy lớn nhất về phạm vi:** phần lớn tầng *nội dung* đã tồn tại trong Content-Creator
(97 package, manifest schema, enum status, source tier 1–6). Nhưng **không được giả định các gate đó
đang được cưỡng chế** — trong `content_repo_clone/TOOLS/` chỉ có **2 file Python** thật; phần còn lại
là markdown do người duy trì. Kế thừa schema: có. Giả định đã enforced: không.

**Về vận hành — rủi ro song song, KHÔNG chặn backend:** đĩa còn **19 GiB / 228 GiB (90 %)**, media
tăng **~2,8 GB/ngày** ⇒ khoảng **7 ngày runway**. `output/video_test/` (13 GiB) là ứng viên giải
phóng an toàn nhất — đã xác minh 3 master trong đó **có mặt trên Drive**, và `cleanup_local.sh
--dry-run` hiện xoá **0 file**. Đây là việc vận hành: theo dõi và xử lý song song, **không** đặt làm
điều kiện tiên quyết của bất kỳ phase backend nào.
