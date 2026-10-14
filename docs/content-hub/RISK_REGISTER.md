# RISK_REGISTER.md

> **Severity**: Critical / High / Medium / Low (thiệt hại nếu xảy ra).
> **Likelihood**: High / Medium / Low (khả năng xảy ra **nếu không** giảm thiểu).
> "Owner" = module chịu trách nhiệm, không phải cá nhân.
> Phạm vi: backend-first (Vercel + Neon + Local CLI). Frontend ngoài phạm vi giai đoạn này.

---

## 1. Rủi ro hiện hữu ngay lúc này

| ID | Rủi ro | Sev | Like | Tác động | Giảm thiểu | Phát hiện | Owner | Phase |
|---|---|:-:|:-:|---|---|---|---|:-:|
| **R01** | **9.064 dòng automation chưa commit** (47 file) | Critical | High | Mất toàn bộ hệ thống sản xuất nếu hỏng đĩa/`git clean`. Không có baseline rollback. | Push lên remote `audio_tool` **ngay P0**; rà secret trước khi push | `git status` | Repo | **P0** |
| **R02** | `client_secret` + `refresh_token` YouTube plaintext trên đĩa | High | Medium | Chiếm quyền kênh. Scope `youtube` cho phép **xoá video**. | chmod 600 + gitignore (đã có); **thu hẹp scope**; cân nhắc Keychain. **Secret không bao giờ vào Neon/Blob/log** | Kiểm quyền file; Google alert | `youtube_auth.py` | P0 |
| **R03** | `content_review.py` tồn tại nhưng **không** được `long_batch_runner.py` gọi | Medium | High | Video dài lên sóng **không** qua cổng kiểm duyệt nội dung mà Shorts đang có | Nối lại ở P2 như audit runner | Đọc code; test gate | `long_batch_runner.py` | P2 |
| **R04** | `output/` đã 26 GB, +337 MB/video | Medium | High | Hết đĩa ⇒ job fail hàng loạt | Retention như `cleanup_local.sh`; `storage_state`/`retention_status` trong DB; cảnh báo ngưỡng đĩa | Monitor dung lượng | `artifact` | P4 |
| **R05** | **Media local không có backup tự động** | High | Medium | Mất 25,3 GB video đã render nếu hỏng đĩa | Media **cố ý** không upload (quyết định người dùng) ⇒ rủi ro tồn dư. Đề xuất backup ngoài — **ngoài phạm vi hệ thống** | Kiểm tra định kỳ | Người dùng | — |

---

## 2. Bảo mật & kiểm soát truy cập

| ID | Rủi ro | Sev | Like | Tác động | Giảm thiểu | Phát hiện | Owner | Phase |
|---|---|:-:|:-:|---|---|---|---|:-:|
| **R10** | **Remote code execution qua job params** | Critical | Medium | Server bị chiếm ⇒ chạy lệnh tuỳ ý trên máy local | `job_type` **enum đóng** ánh xạ tới hàm đã đăng ký; Zod **`.strict()`**; argv-list; **cấm `shell=True`**; job chứa dữ liệu không chứa lệnh | Test AST (I-19); fuzz params (I-7) | `hub_cli/handlers` | P4 |
| **R11** | Worker token bị lộ | High | Medium | Claim job, đọc nội dung, ghi kết quả giả | Hash `sha256` trong DB; TTL + xoay overlap 24h; revoke tức thì; rate limit; chỉ chạm `/api/worker/*`. ⚠️ Token **liên kết** máy, **không chứng minh sở hữu** — mTLS/DPoP sau MVP | `last_used_at` bất thường | `worker_token` | P4 |
| **R12** | Secret rò rỉ vào log | High | High | Token lộ ra `job_event`, response, file log | **Redaction hai lớp** (worker trước khi gửi + server trước khi ghi); test bơm token (I-8) | Quét mẫu `job_event` | `hub_cli/redact` | P4 |
| **R13** | Vượt quyền giữa các kênh | High | Medium | Người được giao kênh A đọc/sửa kênh B | Lọc qua `user_channel_role`; trả **404** không phải 403; permission matrix test **tự sinh** (endpoint mới thiếu khai báo ⇒ test fail) | Test I-6 | `apps/hub/auth` | P1 |
| **R14** | **Lẫn lộn nhóm auth** (worker token dùng được User API) | High | Medium | CLI bị chiếm ⇒ đọc/sửa toàn bộ dữ liệu người dùng | Tách hoàn toàn `/api/v1/*` vs `/api/worker/*`; token khác loại, middleware khác; test chéo hai chiều | Test tách nhóm | `apps/hub/auth` | P1 |
| **R15** | Path traversal khi ghi nhận artifact | High | Medium | Ghi/đọc file ngoài vùng cho phép | Kiểm ở **worker** (`realpath`, mở no-follow từ fd gốc-workspace, băm từ fd — chống TOCTOU) + attestation; server kiểm **cú pháp + phân quyền** | Test I-20 | `hub_cli` + `api/worker` | P4 |
| **R16** | Bypass approval | Critical | Medium | Nội dung chưa duyệt được build/publish | `approval` partial-unique `ACTIVE`; so khớp ID `job=approval=manifest`; artifact phải `PROMOTED`; test bypass trên **mọi** entry point | Audit trail; test | `apps/hub/domain` | P2 |
| **R17** | **Algorithm tự approve nội dung do chính nó tạo** | Critical | Medium | Vòng lặp tự phê duyệt, mất hoàn toàn kiểm soát chất lượng | `approval.approved_by` NOT NULL → bảng `user`; worker **không có** endpoint approve; revision do agent tạo luôn `DRAFT`/`REVIEW_REQUIRED` | Test I-A1 | `approval` | P2 |
| **R18** | Job replay / double-claim | Medium | Medium | Build/upload lặp | `Idempotency-Key` + `lease_token` + `job_attempt` + partial unique **gồm `DEFERRED`** | Trùng `idempotency_key` | `api/worker` | P4 |
| **R19** | **Prompt injection từ nội dung nguồn** | High | High | Nguồn/transcript chứa chỉ thị điều khiển agent ⇒ sinh nội dung sai hoặc lái handler | Coi nội dung nguồn/LLM là **dữ liệu không tin cậy**: không đưa vào tên file/tham số subprocess; tách system vs user content; validate JSON đầu ra (tiền lệ `short_judge_panel_engine.py:82-150`) | Test injection | `hub_cli` | P4 |
| **R20** | **CLI gửi dữ liệu giả** (score/audit bịa) | High | Medium | Nội dung kém được điểm cao ⇒ approve nhầm | Mọi ghi kèm `lease_token`+`job_attempt_id`; `input_snapshot_hash` server **verify** khớp `content_sha256`; score append-only truy vết được worker nào | Test I-S2 | `score_run` | P2 |
| **R21** | Worker bị chiếm (máy local nhiễm mã độc) | Critical | Low | Toàn bộ secret + kênh YouTube. **Không giảm thiểu được bằng thiết kế backend.** | Worker chạy user thường, không sudo; token phạm vi hẹp; chấp nhận rủi ro tồn dư | EDR của máy | Máy local | — |
| **R22** | SSRF khi fetch nguồn | High | Medium | Truy cập dịch vụ nội bộ/metadata cloud | **Fetch chạy ở CLI, không ở Vercel** ⇒ control plane không có bề mặt SSRF; ở CLI chặn IP riêng/loopback/link-local, `file://`, kiểm lại sau redirect, giới hạn kích thước + timeout | Test SSRF | `hub_cli` | P6+ |

---

## 3. Nền tảng Vercel / Neon / Blob

| ID | Rủi ro | Sev | Like | Tác động | Giảm thiểu | Phát hiện | Owner | Phase |
|---|---|:-:|:-:|---|---|---|---|:-:|
| **R30** | **Claim bị tách thành nhiều câu lệnh** | Critical | Medium | Nếu claim tách SELECT rồi UPDATE riêng, transaction ngầm không còn bao trùm ⇒ **hai worker nhận cùng một job**. *(Sửa theo Codex v2R1 HIGH-1: bản trước quy sai nguyên nhân cho HTTP driver — claim **một câu lệnh** chạy tốt trên HTTP)* | Giữ claim là **một** `UPDATE … RETURNING` (`API_AND_WORKER_PROTOCOL §4.1`); test race trên Neon thật + test chống hồi quy hình dạng câu lệnh | Test race (I-3) | `apps/hub/db` | **P4** |
| **R31** | Giới hạn body 4,5 MB của Vercel Function | Medium | Low | 413 khi payload lớn | Payload text lớn nhất thực đo **194,8 KB** (dư 23×); media **không** đi qua API; log batch ≤ 256 KB; endpoint rủi ro phải phân trang | Test gửi > 4,5 MB | `api` | P1 |
| **R32** | Max duration (300s Hobby / 800s Pro) | High | Medium | Tác vụ dài bị 504 | **Không** chạy TTS/ffmpeg/AI trên Vercel — đó là toàn bộ lý do có Local CLI. Endpoint < 10s; long-poll `wait_seconds ≤ 25` | Monitor p99 | `api` | P1 |
| **R33** | Cold start làm hỏng long-poll / claim | Medium | Medium | Latency tăng, worker timeout oan | `wait_seconds` ngắn + retry; timeout worker > timeout server; test cold start | Monitor | `api/worker` | P4 |
| **R34** | Vercel Cron không gọi được YouTube | Medium | High | Nếu thiết kế sai sẽ tưởng cron tự sync được | Cron **chỉ enqueue job**; token YouTube ở local, Vercel **không** có | Review kiến trúc | `api/cron` | P6 |
| **R35** | Neon connection/compute limit | Medium | Medium | Hết connection ⇒ 503 | Serverless driver + pooling; giới hạn concurrency worker; đo active connections | Monitor Neon | `apps/hub/db` | P1 |
| **R36** | **Lạm dụng Blob thay database** | Medium | Low | Mất khả năng query/diff/version nội dung | **Blob KHÔNG dùng ở MVP.** Nội dung text nằm trong Postgres (script lớn nhất 67,8 KB). Cột `blob_*` để sẵn nhưng không bật | Review schema | `storage` | — |
| **R37** | Chi phí Vercel/Neon tăng ngoài dự kiến | Medium | Medium | Hoá đơn bất ngờ | Media không upload ⇒ không có chi phí Blob/egress lớn. Cảnh báo usage; Neon autosuspend cho branch dev | Dashboard usage | Vận hành | P1 |
| **R38** | Vendor lock-in (Vercel + Neon) | Medium | Medium | Khó rời nền tảng | Logic nghiệp vụ ở `src/domain` **thuần**, không phụ thuộc HTTP/Vercel; Drizzle sinh SQL chuẩn Postgres ⇒ chuyển Postgres khác được; Blob không dùng ⇒ không thêm lock-in | Review kiến trúc | Kiến trúc | — |

---

## 4. Dữ liệu & tính đúng đắn

| ID | Rủi ro | Sev | Like | Tác động | Giảm thiểu | Phát hiện | Owner | Phase |
|---|---|:-:|:-:|---|---|---|---|:-:|
| **R40** | **Mất lịch sử score do ghi đè** | High | High | Không trả lời được "điểm tăng/giảm vì sao" — yêu cầu cốt lõi | `score_run` **và `score_dimension`** append-only (trigger + thu hồi quyền); `run_sequence` cho phép nhiều quan sát; idempotency tách sang `idempotency_record`; `algorithm_version` bất biến | Test I-S1 | `score_run` | P2 |
| **R41** | **Mất lịch sử analytics do ghi đè** | High | High | Mất khả năng phân tích xu hướng | UPSERT + `_history` (SCD-2); YouTube hiệu chỉnh hồi tố 48–72h | Test I-5 | `analytics` | P6 |
| **R42** | **Lưu tổng gộp khoảng vào bảng theo ngày** | High | High | **Bịa số liệu ngày**, hỏng lịch sử vĩnh viễn | `get_video_analytics()` hiện **không** có `dimensions` (`youtube_analytics.py:54-60`) ⇒ **viết hàm mới** có `dimensions=day`; ingest **từ chối** response thiếu dimensions; map theo `columnHeaders` | Test I-26 | `analytics_query` | P6 |
| **R43** | **Hai nguồn sự thật** (file vs DB) | High | High | Dữ liệu trôi lệch, không biết tin bên nào | Chuyển A→B→C→D có kiểm soát; MVP dừng ở **A (một chiều file→DB)**; reconciliation report; **cấm** nhảy thẳng DB-only | Reconciliation | `import/sync` | P3 |
| **R44** | Race condition hàng đợi | High | Medium | Job chạy hai lần | Claim nguyên tử **CAS một câu lệnh trên HTTP driver** (phương án B — xem R30 và `API_AND_WORKER_PROTOCOL §4.1.1`); `lease_token` + `job_attempt`; `DEFERRED` trong partial unique | Test I-3 | `queue` | P4 |
| **R45** | AI hallucination trong script/SEO | High | High | Nội dung sai về tôn giáo/pháp luật lên kênh | Judge panel đã có; audit gate; claim phải có citation; `PASS_WITH_ADVISORIES` **không** tự đủ để publish nội dung rủi ro cao | Audit finding | `audit_run` | P2 |
| **R46** | Sai sự thật về giáo lý/pháp luật | Critical | Medium | Tổn hại uy tín, rủi ro pháp lý (domain CL) | Source tier 1–6 theo domain (đã có); cross-verify Tier 5/6 với Tier 1/2; conflict detection qua `claim_evidence` | Conflict detection | `source`/`claim` | P2 |
| **R47** | Import làm hỏng/mất dữ liệu gốc | High | Medium | Mất dữ liệu sản xuất | Import **chỉ đọc** file gốc; `DRY_RUN` bắt buộc trước `APPLY`; **restore point Neon** tạo trước `APPLY`; checksum; idempotent qua `legacy_id_map` | Test I-IMP1/3 | `import` | P3 |
| **R48** | Import nuốt secret vào DB | High | Medium | `refresh_token` nằm trong content DB | Allowlist field khi import; chặn khoá nhạy cảm; test I-IMP2 | Test | `import` | P3 |
| **R49** | Nội dung trùng lặp / cạnh tranh video cũ | Medium | High | Tự ăn thịt lượt xem | `DUPLICATE_RISK` dimension; dedupe theo title/tag/registry ở P7 | Recommendation | `recommendation` | P7 |
| **R50** | Migration phá huỷ lịch sử | High | Medium | Mất audit/approval/score/analytics | **Forward-only** ở production; tương thích ngược một phiên bản; Neon branching + diễn tập restore; `downgrade` chỉ cho DB dev | Review migration | Drizzle | mọi phase |
| **R51** | Không rebuild được revision cũ | Medium | Medium | Không tái lập/điều tra được | Nội dung text **nằm trong DB** ⇒ không phụ thuộc clone shallow. `frozen_input_manifest.environment` ghi model/lockfile/config. ⚠️ **Không** hứa byte-identical: `render_engine.py:195-207` sampling có nhiệt độ, **không seed** | Test I-21 | `revision` | P2 |
| **R52** | So điểm giữa hai `algorithm_version` khác nhau | Medium | High | Kết luận sai về "nội dung tốt lên" | Chặn so sánh chéo version ở tầng API; muốn so phải chấm lại cùng version | Test | `score` | P2 |

---

## 5. Dự án & vận hành

| ID | Rủi ro | Sev | Like | Tác động | Giảm thiểu | Phát hiện | Owner | Phase |
|---|---|:-:|:-:|---|---|---|---|:-:|
| **R60** | **Hồi quy pipeline đang chạy** | Critical | Medium | Dừng dây chuyền sản xuất hằng ngày | Backend chạy **song song**, không thay thế; feature flag từng `job_type`; **không gỡ** `scripts/daily_short_batch.sh` cho tới khi P5 ổn định ≥2 tuần | `daily_run_log.jsonl`; `short_health_check.py` | Roadmap | mọi phase |
| **R61** | **MVP phình to** | High | High | Không bao giờ ra được bản dùng thật | MVP = P0→P5, chốt ở `BACKEND_MVP_SPEC.md`; chỉ **4/9** job type; danh sách "KHÔNG làm" ở `TARGET_ARCHITECTURE.md §12` | Rà phạm vi mỗi phase | Roadmap | — |
| **R62** | **Frontend lẫn vào phạm vi backend** | Medium | High | Lãng phí; UI làm ra không khớp mockup người dùng sẽ vẽ | Quy tắc cứng: không UI component/styling/dashboard. Chỉ API contract. Frontend là **Phase 8**, chỉ sau khi có mockup duyệt | Review PR | Roadmap | mọi phase |
| **R63** | Xây lại thứ Content-Creator đã có | High | High | Lãng phí lớn nhất có thể | Import + index, không thay thế; kế thừa manifest schema, enum status, source tier. ⚠️ Nhưng **không giả định** gate đang được cưỡng chế — chỉ có **2** validator Python thật | Ma trận claim→enforcement | Kiến trúc | P3 |
| **R64** | Đụng code upstream | Medium | Medium | Xung đột merge; hỏng release PyPI | Ranh giới cứng: không sửa `src/`, `apps/`, `tests/`, `[project].dependencies`, CI hiện có. `apps/hub` là project Node riêng | Review diff | Repo | mọi phase |
| **R65** | Push nhầm lên `origin` (upstream người khác) | High | Medium | Lộ code/dữ liệu riêng ra dự án công khai | Chỉ push remote `audio_tool`; kiểm `git remote -v` trước mỗi push | Review trước push | Repo | **P0** |
| **R66** | Không lint/typecheck ⇒ nợ chất lượng | Medium | High | Lỗi runtime khó lường | ruff/mypy cho `hub_cli`; eslint/tsc/semgrep cho `apps/hub` — **ngay P1**, job CI riêng | CI | CI | P1 |
| **R67** | `creative_director.py` 73 KB đơn khối | Medium | Medium | Khó tách thành handler, khó test | Chưa bọc ở MVP (chỉ `BUILD_AUDIO`); khi bọc phải qua 7 test characterization | — | Automation | sau MVP |
| **R68** | **Team hiện thuần Python, backend mới là TypeScript** | Medium | Medium | Chậm tiến độ, chất lượng thấp | Đây là **quyết định cần duyệt (D2)**. Vercel tối ưu cho Node; Drizzle/Zod là hệ sinh thái TS. Nếu rủi ro quá cao, cân nhắc Python runtime trên Vercel — nhưng mất Drizzle/Zod và hỗ trợ kém hơn | Đánh giá sớm | Người dùng | **P1** |

---

## 6. Top 6 cần xử lý trước tiên

1. **R01** — commit automation code (Critical/High, **P0**, chặn mọi thứ)
2. **R30** — Neon HTTP driver phá vỡ claim nguyên tử (Critical/High, **P4**; bẫy kỹ thuật dễ bỏ sót nhất)
3. **R60** — bảo vệ pipeline đang chạy (Critical/Medium, xuyên suốt)
4. **R17** — chặn algorithm tự approve (Critical/Medium, **P2**)
5. **R10** — chống RCE cho worker (Critical/Medium, **P4**)
6. **R42** — không lưu tổng gộp khoảng vào bảng theo ngày (High/High, **P6**; hỏng thì không sửa được)

## 7. Rủi ro tồn dư chấp nhận có ý thức

| ID | Vì sao chấp nhận |
|---|---|
| R05 (media không backup) | Hệ quả trực tiếp của quyết định "không upload media". Backup là việc của người dùng, ngoài phạm vi hệ thống |
| R21 (worker bị chiếm) | Không giảm thiểu được bằng thiết kế backend; máy local vốn đã giữ mọi secret ngay hôm nay |
| R38 (vendor lock-in) | Đã chọn thành phần trung lập nhất có thể trong ràng buộc "phải deploy Vercel" |
