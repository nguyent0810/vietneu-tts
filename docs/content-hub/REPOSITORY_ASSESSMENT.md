# REPOSITORY_ASSESSMENT.md

> Khảo sát thực tế repository trước khi thiết kế **Content Intelligence Hub**.
> Mọi nhận định đều kèm `file:line` hoặc symbol. Phần suy đoán được đánh dấu rõ **[ASSUMPTION]**.
>
> - Ngày khảo sát: 2026-07-29
> - Branch: `main`
> - Working tree: **bẩn** — 7 file tracked bị modify, 56 entry untracked (xem §11)
> - Commit gần nhất: `126363b Add topic-based TTS automation pipeline`

---

## 1. Tóm tắt điều hành (đọc phần này trước)

Repository này **không phải** một web app. Nó là **fork của thư viện TTS mã nguồn mở
VieNeu-TTS** (`origin` = `pnnbao97/VieNeu-TTS`), trên đó người dùng đã **bồi thêm một lớp
tự động hoá sản xuất nội dung YouTube** dưới dạng ~47 script Python rời ở thư mục gốc.

Ba kết luận quan trọng nhất, ảnh hưởng trực tiếp tới toàn bộ kế hoạch:

| # | Phát hiện | Hệ quả |
|---|---|---|
| **F1** | **Không có web app, không có database, không có ORM, không có auth, không có API server, không có queue service.** Toàn bộ "web" hiện có là Gradio demo TTS (`apps/gradio_main.py`) và một FastAPI streaming demo không auth (`apps/web_stream.py:1-132`). | Content Intelligence Hub gần như **greenfield**. Phần "tái sử dụng" nằm ở *pipeline sản xuất*, không phải ở *tầng web*. |
| **F2** | **Đã tồn tại một hệ thống quản trị nội dung production-grade**: repo GitHub "Content-Creator" (clone tại `content_repo_clone/`) với **97 production package**, **JSON Schema chính thức** cho manifest, **state machine 7 trạng thái**, **QA enum 5 trạng thái**, **source registry phân Tier 1–6**, 5 registry toàn cục, và validator Python đang chạy (`TOOLS/package_audit.py`). Chi tiết §4.5. | Hub **chồng lấn nặng**. Phần lớn "tính năng mới" mà đề bài yêu cầu (content item, revision, source scoring, audit gate, dedupe registry) **đã tồn tại ở đó**. Đây là **quyết định kiến trúc lớn nhất** (§13/U1). Xây lại = lãng phí + tạo hai nguồn sự thật. |
| **F3** | **~9.064 dòng code tự động hoá ở thư mục gốc KHÔNG được commit** (47 file `.py` untracked). Chỉ 6 file (971 dòng) là tracked. | Rủi ro mất mát/regression rất cao. **Phase 0 bắt buộc phải đưa code này vào version control trước khi đụng bất cứ thứ gì.** |

---

## 2. Tech stack (đã xác minh)

| Hạng mục | Thực tế | Bằng chứng |
|---|---|---|
| Ngôn ngữ chính | Python 3.12 (`requires-python = ">=3.10"`) | `.python-version`, `pyproject.toml:65` |
| Package manager | **uv** 0.11.28 (+ setuptools build backend) | `pyproject.toml:1-3`, `[tool.uv]` |
| Frontend framework | **KHÔNG CÓ** cho app. Gradio 6.20 cho demo TTS | `apps/gradio_main.py` |
| Backend framework | **KHÔNG CÓ** cho app. FastAPI có mặt (transitively qua gradio) và dùng ở 1 demo | `apps/web_stream.py`, `.venv/.../fastapi` |
| Database | **KHÔNG CÓ**. State = JSON file trên đĩa | `output/*/registry.json` |
| ORM / query layer | **KHÔNG CÓ** | — |
| Auth | **KHÔNG CÓ** trong app. Chỉ có OAuth YouTube phía CLI | `youtube_auth.py` |
| Permission model | **KHÔNG CÓ** | — |
| API style | **KHÔNG CÓ** API nội bộ. Tích hợp ngoài qua REST thủ công (`urllib`) | `youtube_upload.py:37-39` |
| Background job / queue | File-based, tuần tự, có `flock` | `registry_lock.py:22`, `process_topics.py:64-111` |
| Storage | Filesystem cục bộ + Google Drive qua `rclone` | `drive_utils.py`, `PIPELINE.md` |
| Test framework | pytest (8 file, chủ yếu unit test TTS engine, dùng mock) | `tests/`, `pyproject.toml:139-140` |
| CI | GitHub Actions: pytest trên Py 3.11/3.12, Ubuntu. **Không lint, không type-check** | `.github/workflows/ci.yml` |
| Lint / format / typecheck | **KHÔNG CÓ** config (không ruff/black/mypy/pre-commit) | Đã grep toàn repo |
| Logging | `logging` stdlib, message tiếng Việt kèm emoji | `src/vieneu/base.py` |
| Observability | **KHÔNG CÓ** metrics/tracing. Log ra file + JSONL thủ công | `scripts/daily_short_batch.sh` |
| Schema migration | **KHÔNG CÓ** convention (vì chưa có DB) | — |
| Deployment | Chạy cục bộ trên máy macOS của người dùng (`darwin/arm64`) + Docker cho TTS server | `Makefile`, `docker/` |
| Scheduler | Shell wrapper cho cron/launchd | `scripts/daily_short_batch.sh` |

**Node.js cũng đã có mặt trong toolchain** (v20.20.2) — dùng cho các tool render vendored:
`remotion_typography/` (React + Remotion) và `revideo_diagrams/` (Revideo), được gọi từ
`creative_director.py` và `typography_render.py`. `youtube_manager_clone/` là app Electron +
React/Vite **không được Python tham chiếu** (grep 0 hit) → coi như dead weight.

---

## 3. Module map

### 3.1 Thư viện TTS gốc (upstream — **KHÔNG ĐỤNG TỚI**)

```
src/vieneu/            # API công khai: Vieneu(mode=...) -> .infer()/.infer_stream()/.infer_batch()
  factory.py:3-43      # dispatch mode -> engine class
  base.py              # BaseVieneuTTS: codec, voice, watermark
  v3turbo.py           # mặc định; 48kHz; ONNX(CPU)/PyTorch(GPU)
  standard.py fast.py turbo.py remote.py core_xpu.py
  _v3_turbo_engine/    # engine nội bộ
  v3_turbo_serve/      # batching/serving
src/vieneu_utils/      # phonemize (sea-g2p), audio utils
apps/                  # gradio_main.py (UI demo), web_stream.py (FastAPI stream demo)
tests/                 # 8 file test cho engine, dùng mock
```

Đây là code upstream, có PyPI release (`vieneu` 3.2.3), CI riêng.
**Ranh giới cứng: không refactor, không đổi API, không thêm dependency nặng vào đây.**

### 3.2 Lớp tự động hoá nội dung (do người dùng viết — **vùng làm việc chính**)

Nhóm theo chức năng (tất cả ở thư mục gốc):

**Điều phối / batch**
- `process_topics.py` — entry point render theo chủ đề; giữ `_PipelineLock` (`:64-111`)
- `long_batch_runner.py` (21KB) — pipeline video dài 10 stage (`process_one_episode`, `:202-348`)
- `short_batch_runner.py` (33KB) — pipeline Shorts 7 stage (`process_one_segment`, `:275-455`)
- `process_drive_queue.py`, `process_short_queue.py` — hàng đợi theo folder
- `registry_lock.py:22` — `FileLock` dựa trên `flock`
- `rotation_state.py` — reservation 15 phút cho nội dung evergreen (`:39-58`)

**Nguồn nội dung**
- `content_repo.py` (15KB) — pull repo Content-Creator (chỉ đọc), `gate_episode()`, `stage_ready_episodes()`
- `topic_bank.py`, `content_categories.py`, `domain_creative_profiles.py`, `short_content_planner.py`

**Sáng tạo / kịch bản**
- `creative_director.py` (**73KB — file lớn nhất**) — sinh "Director Bible" / shot list
- `director_bible.py`, `short_judge_panel_engine.py` (19KB) — judge panel A/B/C
- Họ `*_short_generator.py` (10 file): zodiac, iching, twelve_gods, element_luck, storytelling, educational...

**Kiểm duyệt / SEO**
- `content_review.py`, `short_content_review.py` — review bằng Codex, có `needs_human_review`
- `content_seo.py`, `short_seo.py` — sinh + review SEO

**Render / hậu kỳ**
- `render_engine.py` (tracked) — lõi render TTS, chunk tự nhiên, QA, retry, xuất `.srt`/`.json`
- `render_short.py`, `_short_tts_render.py`, `typography_render.py`, `mix_bgm.py`, `finalize_episode.py`
- `asset_generation.py` (23KB) — sinh ảnh/video/typography cho từng beat
- `comfyui_client.py`, `codex_image_client.py`, `agy_image_client.py`, `cursor_image_client.py`
- `video_tool_bridge.py` — cầu nối sang `video_tool_clone/`

**YouTube**
- `youtube_auth.py`, `youtube_upload.py` (18KB), `short_upload.py`, `youtube_catalog.py`, `youtube_analytics.py`

**Vận hành**
- `short_health_check.py`, `font_glyph_check.py`, `generate_symbol_assets.py`, `bgm_tracks.py`

### 3.3 Thư mục vendored (gitignored, không phải code của repo)

| Thư mục | Bản chất | Được Python dùng? |
|---|---|---|
| `content_repo_clone/` | Repo Content-Creator (markdown/JSON specs) | **Có** — `content_repo.py` |
| `video_tool_clone/` | App Python/PySide6 + venv riêng + ffmpeg vendored | **Có** — subprocess (`long_batch_runner.py:44-47`) |
| `comfyui_local/` | ComfyUI, HTTP API cổng 8189 | **Có** — `comfyui_client.py` |
| `remotion_typography/` | React + Remotion | **Có** — `typography_render.py` |
| `revideo_diagrams/` | Revideo | **Có** — `creative_director.py` |
| `youtube_manager_clone/` | Electron + React/Vite | **KHÔNG** (grep 0 hit) → dead weight |

---

## 4. Data model hiện có

### 4.1 `registry.json` — tiền thân của "content item"

Vị trí: `output/long/{topic}/registry.json`, `output/shorts/{topic}/registry.json`.
Cấu trúc: dict `{key: record}`. Trường thực tế (xác minh bằng `jq` trên dữ liệu thật):

```
key, episode_dir_name, title, status, publish_at, video_id,
wav_path, json_path, shot_list_path, video_raw_path, ass_path, video_bgm_path,
seo{title,description,tags}, error_count, last_error
```

Bản Shorts thêm: `episode`, `segment_index`, `hook_score`, `final_script`,
`needs_human_review_hook`, `needs_human_review_seo`, `slot_label`, `video_path`.

**Đây đã là một content item + build record + publish record gộp làm một.**
Nó thiếu: revision history, approval, liên kết nguồn, multi-channel, calendar.

### 4.2 State machine hiện có (giá trị THẬT trong code)

```
long_batch_runner.py:67   TERMINAL_STATUSES = ("uploaded", "dry_run_done", "failed")
short_batch_runner.py:465 TERMINAL_STATUSES = ("uploaded", "dry_run_done", "failed", "needs_review")
content_repo.py:33        READY_CONTENT_STATUSES = {"READY_FOR_TTS_HANDOFF"}
content_repo.py:34        ACCEPTABLE_QA_STATUSES  = {"PASS", "PASS_WITH_ADVISORIES"}
```

Chuỗi trạng thái quan sát được trên đĩa: `scripted`, `video_ready`, `uploaded`,
`dry_run_done`, `failed`.

- **Long**: `pending → audio_ready → bible_ready → assets_ready → video_ready → bgm_ready → finalized → seo_ready → uploaded`
- **Short**: `pending → scripted → audio_ready → video_ready → seo_ready → uploaded`, với 2 cổng
  `needs_review` (hook & SEO) là **terminal, fail-closed**.

> **Nhận định quan trọng:** state machine mà đề bài đề xuất (IDEA → … → ARCHIVED) là **tầng
> biên tập**, còn state machine hiện có là **tầng build**. Chúng là hai vòng đời khác nhau và
> **không nên nhồi vào một enum**. Xem `TARGET_ARCHITECTURE.md §Content lifecycle`.

### 4.3 Manifest phía Content-Creator

`content_repo.py:35` — `REQUIRED_MANIFEST_KEYS = ("content_status", "qa_status", "domain_id", "package_id")`.
Gate là **fail-closed**: thiếu/lạ khoá thì coi như chưa sẵn sàng, không đoán (`content_repo.py:11-15`).

### 4.4 Data model của repo Content-Creator (**quan trọng nhất**)

Khảo sát trực tiếp `content_repo_clone/`. Đây **không phải** tài liệu ước vọng — nó là hệ thống
đang vận hành, có validator và 97 package thật.

**Cấu trúc:**
```
CORE_OS/               # Hợp đồng vận hành phi-domain: CONTENT_ENGINE, QA_ENGINE,
                       # RESEARCH_ENGINE, KNOWLEDGE_MODEL, GROWTH_ENGINE, PRODUCTION_ENGINE,
                       # VISUAL_ENGINE, SEO_ENGINE, SHORTS_ENGINE, MASTER_AGENT
DOMAINS/<D>/           # BUDDHISM, FENG_SHUI, CRIMINAL_LAW (active); TRUE_CRIME (deprecated);
                       # MUSIC, PSYCHOLOGY (planned)
  DOMAIN_GUIDE.md  DOMAIN_MANIFEST.md  CONTINUITY_REGISTRY.md
  SOURCES/  KNOWLEDGE_PACKETS/  CREATIVE_KNOWLEDGE/  SERIES_BIBLES/
  CHARACTER_BIBLES/  GLOSSARY/  PRODUCTION_PACKAGES/
REGISTRIES/            # ASSET_REGISTRY, DOMAIN_REGISTRY, ID_REGISTRY,
                       # DEPENDENCY_REGISTRY, VERSION_REGISTRY
DOMAIN_SPECIFICATION/  # JSON Schema + spec chính thức
SHARED_LIBRARIES/      # NARRATIVE_PATTERN_LIBRARY (189KB), EPISODE_BLUEPRINT_LIBRARY (173KB)
CROSS_DOMAIN/          # CONCEPT_REGISTRY, CROSS_DOMAIN_POLICY, RELATIONSHIP_REGISTRY
TOOLS/                 # package_audit.py (validator), build_short_package.py
```

**Production package = content item.** Layout cố định:
```
README.md
OUTPUT/03_AUDIO_SCRIPT_TTS.txt        # bản giao cho TTS (plain text)
_INTERNAL/
  01_RESEARCH_BRIEF.md                # nguồn, canonical claims, risk flags
  02_EPISODE_PLANNER.md               # narrative pattern + episode blueprint
  03_AUDIO_SCRIPT_MASTER.md           # canonical; narration trong <!--NARRATION_START/END-->
  06_QA_REPORT.md
  PACKAGE_AUDIT_RESULT.json           # output có cấu trúc của validator
  manifest.json                       # nguồn sự thật máy đọc được
_ARCHIVE/                             # asset đã bị thay thế
```

**`manifest.json` — schema chính thức** (`DOMAIN_SPECIFICATION/PRODUCTION_PACKAGE_MANIFEST_SCHEMA.json`, `schema_version: "2.0"`):
`package_id, episode_id, domain_id, series_id, title, language, version (semver),
content_status, canonical_master, tts_output, word_count, qa_status,
master_to_tts_coverage_percentage, normalization_count, external_processes,
dependencies[{asset_id,path,scope}], active_internal_assets[], archived_assets[], updated_at`

**State machine biên tập ĐÃ CÓ** (`content_status`, 7 giá trị):
```
DRAFTING → READY_FOR_CONTENT_REVIEW → CONTENT_REVISION_REQUIRED
        → CONTENT_APPROVED → READY_FOR_TTS_HANDOFF → CONTENT_PACKAGE_COMPLETE
        (+ BLOCKED)
```
**QA state ĐÃ CÓ** (`qa_status`, 5 giá trị): `NOT_RUN | PASS | PASS_WITH_ADVISORIES | FAIL | BLOCKED`

> Đây gần như **trùng khớp** với workflow mà đề bài đề xuất (IDEA…APPROVED). Kế hoạch phải
> **kế thừa enum này**, không phát minh enum thứ ba. Xem `TARGET_ARCHITECTURE.md`.

**`external_processes` bị ép cứng `OUT_OF_SCOPE`** cho `voice_render`, `video_render`, `publish`.
→ Content-Creator **cố ý dừng ở bản giao TTS**. Đó chính là **đường ranh giới tự nhiên** giữa
Content-Creator và Hub: Hub sở hữu mọi thứ *sau* handoff.

**Source model ĐÃ CÓ** (`DOMAINS/*/SOURCES/SOURCE_REGISTRY.md`) — phân tầng theo domain:

| Tier | Loại | Trạng thái |
|---|---|---|
| 1 | Kinh điển gốc | active |
| 2 | Bản dịch được công nhận | active |
| 3 | Luận giải | active |
| 4 | Nguồn theo tông phái | active |
| 5 | Nghiên cứu học thuật | active |
| 6 | Diễn giải hiện đại | **restricted** |

Kèm confidence tier theo từng claim (High/Medium-high/Medium/Low), yêu cầu cross-verify
Tier 5/6 với Tier 1/2 trước khi trích làm giáo lý, và `CONTINUITY_REGISTRY.md` ghi nhận
lỗi thực tế đã phát hiện (ví dụ: một nguồn legacy bị hạ xuống Tier 6 vì không phải bản dịch kinh).
QA report còn ghi nhận **đã bắt được một "fabricated-source claim"** trong `KP_FS_001` và sửa 2026-07-24.

> **Hệ quả trực tiếp cho §3 của đề bài (pipeline lọc nguồn):** mô hình scoring rule-based
> theo domain **đã tồn tại và đang chạy**. Hub nên **số hoá và hiển thị** nó, không thiết kế
> lại công thức mới.

**QA_ENGINE** — 11 nhóm kiểm tra (Structure, Asset, Content, Derivation, Manifest, Registry,
Coverage…), phân tầng Core QA + Domain QA + Asset QA + Risk QA; điều kiện fail rõ ràng
(ví dụ coverage Master→TTS phải **100%**, TTS không được chứa markdown/metadata/ghi chú).

**REGISTRIES** — `ASSET_REGISTRY.md` (200+ dòng: asset_id, type, domain, canonical_path,
status, version, dependencies, source_lineage, qa_status) đóng vai trò chống trùng ID và
truy vết lineage; `ID_REGISTRY.md` cấp phát namespace tiền tố (KP/CK/CB/SB/EP/PKG…).

**Stack:** file-based, git là backend lưu trữ, Python stdlib thuần cho `TOOLS/`.
Không DB, không web framework.

#### ⚠️ Đính chính mức độ "production-grade" *(sửa theo Codex finding MEDIUM-20)*

Bản nháp trước gọi đây là "hệ thống quản trị production-grade". Cần nói chính xác hơn:

| Thành phần | Được **thực thi bằng code**? | Bằng chứng |
|---|---|---|
| Validate manifest theo JSON Schema | ✅ Có | `TOOLS/package_audit.py` |
| Suy ra TTS output + manifest cho Short | ✅ Có | `TOOLS/build_short_package.py` |
| Chuyển trạng thái `content_status` | ❌ **Không** — quy ước trong markdown | chỉ có mô tả ở `CORE_OS/PRODUCTION_ENGINE.md` |
| Source tiering 1–6, confidence tier | ❌ **Không** — bảng markdown do người duy trì | `DOMAINS/*/SOURCES/SOURCE_REGISTRY.md` |
| Registry chống trùng ID / lineage | ❌ **Không** — bảng markdown | `REGISTRIES/*.md` |
| Domain QA policy, cross-domain policy | ❌ **Không** — markdown | `CROSS_DOMAIN/`, `DOMAIN_QA/` |

Trong `content_repo_clone/TOOLS/` **chỉ có đúng 2 file Python**. Phần còn lại là **chính sách và
dữ liệu**, không phải cơ chế cưỡng chế: không có kiểm soát truy cập, không có cập nhật nguyên tử,
không có ràng buộc chuyển trạng thái.

**Hệ quả cho kế hoạch:** vẫn nên **kế thừa schema, enum và mô hình tier** (chúng là thiết kế tốt và
đã được dùng thật). Nhưng **không được giả định** rằng các gate đó *đang được cưỡng chế*.
Với mỗi rule tái sử dụng, phải lập **ma trận claim → enforcement**: tài liệu nguồn, validator thực thi,
mẫu pass/fail, điểm cưỡng chế quan sát được. Rule chưa có validator ⇒ xếp loại **"policy input"**,
và nếu Hub cần nó như một gate thì **Hub phải tự cưỡng chế**.

### 4.5 Config files (không chứa secret)

`topic_voices.json` (chủ đề→giọng), `domain_topics.json` (`BUD/FS/CL` → `Phật giáo/Phong Thủy/Hình Sự`),
`domain_creative_profiles.json` (12KB; khoá con: `bible_genre_label`, `broll_query_sanitizer`,
`context_label`, `image_style_anchor`, `symbol_library`, `tone_label`, `treatment_ratio`).

Content-Creator có **6 domain** (`BUDDHISM, FENG_SHUI, CRIMINAL_LAW, TRUE_CRIME, PSYCHOLOGY, MUSIC`)
nhưng chỉ **3 domain được nối dây** sang pipeline.

---

## 5. Auth, permission, secrets

- **Không có auth ứng dụng.** `apps/web_stream.py` bind `127.0.0.1:8001`, không auth — chấp nhận được vì local-only, nhưng **không được dùng làm nền cho Hub**.
- **OAuth YouTube tự viết tay bằng `urllib`** (`youtube_auth.py:34-49`), không dùng `google-auth-oauthlib` (thư viện này **không** được cài). Loopback flow, có CSRF `state` (`:90`).
- **Scopes** (`youtube_auth.py:45-49`): `youtube.upload`, **`youtube`** (toàn quyền — bao gồm xoá video), `yt-analytics.readonly`.
- **Lưu token**: `.youtube_channels/{label}.json`, chmod `0o600` (`youtube_auth.py:139`), gitignored. Chứa `client_id`, `client_secret`, `refresh_token` **dạng plaintext**.
- Token refresh: luôn refresh trước khi dùng (`youtube_auth.py:167-187`).
- Secrets khác: `.github_integration.env` (GITHUB_TOKEN), `.youtube_oauth_clients.env` (6 biến client id/secret cho 3 kênh). Cả hai đều gitignored.
- Điểm tốt: `content_repo.py:_git_auth` nhúng token qua `http.extraHeader` **tạm thời**, không ghi vào `.git/config` (`:55-58`) — có ý thức bảo mật.

**Đánh giá bảo mật nền tảng: tốt hơn kỳ vọng.** Không có `shell=True`, không `os.system`,
không `eval/exec` dữ liệu ngoài (đã grep toàn repo). Mọi subprocess đều dạng argv-list.
Đây là convention **phải giữ** khi thiết kế worker.

---

## 6. Background jobs / concurrency hiện có

Đây là phần **giá trị nhất để tái sử dụng về mặt ý tưởng**:

| Cơ chế | Vị trí | Ghi chú |
|---|---|---|
| `FileLock` (flock) | `registry_lock.py:22` | Chỉ giữ trong critical section đọc-merge-ghi JSON |
| Read-merge-write | `long_batch_runner.py:100-103` | Giữ entry chỉ có trên đĩa, tránh mất update |
| Pipeline lock | `process_topics.py:64-111` | Timeout 30', poll 15", `AlreadyRunningError` |
| Reservation | `rotation_state.py:39-58` | `peek_next()` giữ chỗ 15', `commit()` chốt |
| Retry có ngưỡng | `long_batch_runner.py:66`, `short_batch_runner.py:458` | `MAX_RETRIES = 3`, `error_count`, rồi `failed` |
| Idempotency | `process_drive_queue.py:78-86` | Bỏ qua nếu output đã tồn tại |
| Resume theo status | `long_batch_runner.py:231-348` | Trạng thái quyết định điểm chạy tiếp |
| Terminal status | `:67` / `:465` | Chặn retry vô hạn |
| Fail-closed gate | `short_batch_runner.py:340,382,401-406` | `needs_review` chặn upload, **kể cả re-check lần cuối** |

**Kết luận:** người viết đã tự khám phá ra leasing, idempotency, retry budget, fail-closed gate.
Hub không phát minh lại — Hub **nâng các khái niệm này từ file lên DB** và thêm multi-worker.

---

## 7. Tích hợp YouTube hiện có

- **Upload resumable 8MB/chunk**, retry 5 lần/chunk, backoff luỹ tiến, refresh token khi 401 (`youtube_upload.py:41-43,170-216`).
- **Quota-aware**: phân biệt `QuotaExceededError` với lỗi thường; gặp quota thì **dừng cả batch** (`youtube_upload.py:111-115,316-334`).
- **Scheduling**: `publish_at` ISO8601 UTC, ép `privacyStatus=private`, YouTube tự publish. Ràng buộc lead time 15' – 180 ngày (`youtube_upload.py:44-45,65-73`).
- **Analytics** (`youtube_analytics.py`): channel metrics theo `day`; video metrics; traffic sources theo `insightTrafficSourceType`. Endpoint `youtubeanalytics.googleapis.com/v2/reports`.
- **Không persist analytics** — hàm trả raw response, người gọi tự lo. Ảnh chụp thủ công nằm ở `analytics_reviews/2026-07-27_daily_factory_raw/*.json`.

**Khoảng trống so với yêu cầu đề bài** (đều là *chưa có*, cần xây):
impressions, CTR, audience retention (`audienceWatchRatio`), search terms
(`insightTrafficSourceDetail`), hiệu suất theo giờ đăng, theo series, theo pillar,
so sánh Long vs Short, phát hiện tăng/giảm, lưu lịch sử snapshot.

> **Lưu ý quota [ASSUMPTION dựa trên tài liệu Google, không phải từ repo]:** Data API mặc định
> 10.000 unit/ngày/project. Hiện mỗi kênh dùng **OAuth client riêng** → nhiều khả năng là 3
> project riêng, tức 3 quota pool riêng. Cần xác nhận (§Unknowns U3).

---

## 8. Tích hợp AI/LLM hiện có (quan trọng cho security review)

Chuỗi fallback thực tế:

- **Text**: `agy` CLI (`~/.local/bin/agy`, gọi `[AGY_BIN, "-p", prompt]`) → **`codex exec`**
  (`["codex", "exec", prompt]`, `content_seo.py:109,124-136`). Parse output giữa marker
  `\ncodex\n` … `\ntokens used\n`.
- **Ảnh**: ComfyUI HTTP `127.0.0.1:8189` → Codex image → agy image → stock footage (Pexels) → typography card.
- **Circuit breaker**: ComfyUI lỗi lần đầu → bỏ qua toàn bộ beat IMAGE trong batch (`asset_generation.py:31,50`).
- **Quota detection** cho agy: quét output tìm `429`/`quota`/`resource exhausted` (`agy_image_client.py:26-28`).
- **Idempotent image**: seed = `sha256(prompt)[:8]` → cùng prompt cho cùng ảnh (`asset_generation.py:63-66`).
- **Cache**: `chunks_cache/director_bibles/`, `chunks_cache/beat_assets/{hash}` — dựa vào sự tồn tại của file.

**Không có `shell=True`** ở bất kỳ lời gọi nào → không có injection surface từ prompt.

**TikTok / social platform khác: KHÔNG CÓ** (grep 0 hit). Chỉ YouTube.

---

## 9. Thành phần TÁI SỬ DỤNG được (reuse)

Xếp theo giá trị:

| # | Thành phần | Vị trí | Cách dùng lại |
|---|---|---|---|
| R1 | Upload YouTube resumable + quota + scheduling | `youtube_upload.py` | Gọi các **hàm** của nó từ handler mới (không sửa file gốc, không bọc batch runner). Đã production-tested. |
| R2 | OAuth đa kênh + refresh | `youtube_auth.py` | Giữ nguyên; chỉ đổi nơi lưu token (§Debt D3). |
| R3 | Client Analytics API | `youtube_analytics.py` | ⚠️ **Chỉ tái dùng được một phần.** `get_channel_analytics()` có `dimensions="day"` (`:41-51`) nên dùng được. Nhưng `get_video_analytics()` **không truyền `dimensions`** (`:54-60`) ⇒ trả tổng gộp cả khoảng, **không** dùng cho bảng theo ngày được. `_query()` gộp mọi `HTTPError` thành một exception (`:37-38`) ⇒ **không có** phân loại quota. Phải viết mới trong `hub/`. |
| R4 | Render TTS + QA + `.srt`/`.json` | `render_engine.py` | Lõi build, worker gọi lại. |
| R5 | Các **stage** trong pipeline Long/Short | `long_batch_runner.py`, `short_batch_runner.py` | ⚠️ **Không bọc nguyên cả runner.** `run_audio_stage(topic)` chạy `process_topics.py --topic <topic>` và xử lý **mọi tập sẵn sàng của topic** (`long_batch_runner.py:155-160`), không phải một revision; `run_step(cmd)` nhận argv tuỳ ý (`:195-199`); state là JSON dùng chung. Phải **trích từng stage** thành handler hẹp một-revision, có workspace riêng. |
| R6 | Ngữ nghĩa lock/retry/idempotency | `registry_lock.py`, `rotation_state.py` | Tái dùng **khái niệm**, chuyển sang DB. |
| R7 | Judge panel + review gate | `short_judge_panel_engine.py`, `short_content_review.py` | Chính là "audit run" + "audit finding". |
| R8 | Sinh SEO + review | `content_seo.py`, `short_seo.py` | Chính là "SEO package". |
| R9 | Domain creative profiles | `domain_creative_profiles.json` | Chính là "content pillar config" theo domain. |
| R10 | Artifact có đánh số stage | `output/**/NN_*.json` | Đã là artifact manifest sơ khai. |
| R11 | Gate fail-closed từ Content-Creator | `content_repo.py:gate_episode` | Mẫu cho approval gate của Hub. |
| **R12** | **JSON Schema manifest v2.0** | `content_repo_clone/DOMAIN_SPECIFICATION/PRODUCTION_PACKAGE_MANIFEST_SCHEMA.json` | **Dùng làm schema chuẩn cho content item của Hub.** Không thiết kế lại. |
| **R13** | **Enum `content_status` (7) + `qa_status` (5)** | cùng file trên | **Dùng làm state machine biên tập.** Hub chỉ thêm vòng đời *build/publish*. |
| **R14** | **Source tiering 1–6 + confidence tier theo domain** | `DOMAINS/*/SOURCES/SOURCE_REGISTRY.md` | Chính là "scoring model rule-based theo domain" đề bài yêu cầu. Số hoá, đừng phát minh lại. |
| **R15** | **`package_audit.py`** (validator 11 nhóm check) | `content_repo_clone/TOOLS/package_audit.py` | Worker gọi lại → sinh ra `audit_run` + `audit_finding`. |
| **R16** | **ASSET/ID/DEPENDENCY/VERSION registry** | `content_repo_clone/REGISTRIES/` | Nền cho dedupe + lineage; Hub index lại vào DB để truy vấn. |
| **R17** | `CONTINUITY_REGISTRY.md` | `DOMAINS/BUDDHISM/` | Mẫu cho "conflict detection" giữa các nguồn. |

### Thành phần **KHÔNG NÊN ĐỤNG**

- `src/vieneu/**`, `src/vieneu_utils/**`, `tests/**`, `.github/workflows/**`, `pyproject.toml`
  (phần `[project]`), `docker/**` — là upstream, có release PyPI.
- `content_repo_clone/` — repo của hệ thống khác, `content_repo.py` **chỉ đọc, không bao giờ push**
  (quyết định có chủ ý, `content_repo.py:2-5`).
- `apps/web_stream.py` — demo, không phải nền tảng.

---

## 10. Technical debt ảnh hưởng tới dự án

| ID | Nợ kỹ thuật | Bằng chứng | Ảnh hưởng |
|---|---|---|---|
| **D1** | **47 file (9.064 dòng) automation chưa commit** | `git ls-files --others` | **Chặn mọi thứ.** Không có baseline để refactor an toàn. |
| D2 | `creative_director.py` 73KB đơn khối | file size | Khó test, khó tách thành job worker. |
| D3 | Secret plaintext trên đĩa (`client_secret` + `refresh_token`) | `.youtube_channels/*.json` | Worker compromise = mất kênh. Scope `youtube` cho phép **xoá video**. |
| D4 | State là JSON file, không transaction | `registry_lock.py` | Không chịu được multi-worker/multi-machine. |
| D5 | Analytics không được lưu lịch sử | `youtube_analytics.py` không persist | Yêu cầu cốt lõi của đề bài chưa có nền. |
| D6 | Không lint/format/typecheck, CI chỉ chạy pytest engine | `.github/workflows/ci.yml` | Subsystem mới cần tự dựng chuẩn chất lượng. |
| D7 | `pytest` **không có** trong `.venv` hiện tại | `python -m pytest` → No module named pytest | Test hiện không chạy được cục bộ nếu không `uv sync --group dev`. |
| D8 | Automation ở root không thuộc package | `pyproject.toml:146-154` | Import lẫn nhau bằng đường dẫn tương đối; khó đóng gói/deploy. |
| D9 | `output/` đã **26GB** | `du -sh output` | Artifact **không được** đưa vào DB/cloud một cách ngây thơ. |
| D10 | `youtube_manager_clone/` dead weight | grep 0 hit | Gây nhiễu khi khảo sát. |
| D11 | `content_review.py` viết xong nhưng **không được batch runner gọi** | không xuất hiện trong `long_batch_runner.py` | Long-form hiện **không có** cổng kiểm duyệt nội dung như Shorts. |

---

## 11. Trạng thái working tree (bắt buộc xử lý trước khi code)

- Branch: `main`. Remote: `origin` = **upstream của người khác** (`pnnbao97/VieNeu-TTS`),
  `audio_tool` = fork của người dùng (`nguyent0810/vietneu-tts`).
- **Không được push lên `origin`.**
- Modified (tracked): `.gitignore`, `process_drive_queue.py`, `process_short_queue.py`,
  `process_topics.py`, `pyproject.toml`, `render_engine.py`, `run.sh`, `uv.lock`
- Untracked: 47 file `.py` + `scripts/`, `assets/`, `bgm/`, `creator_specs/`, `analytics_reviews/`, …

---

## 11b. Khảo sát bổ sung cho quyết định stack backend (Vercel + Neon)

*Bổ sung 2026-07-29 sau khi phạm vi đổi sang backend-first trên Vercel.*

### 11b.1 Hiện trạng JS/TS trong repo

| Câu hỏi | Kết quả |
|---|---|
| Có `package.json` ở root? | **Không** |
| Có `tsconfig.json` / `next.config.*` / `vercel.json`? | **Không có cái nào** |
| `package.json` tồn tại ở đâu? | Chỉ trong 3 thư mục **vendored, gitignored**: `remotion_typography/` (React+Remotion), `revideo_diagrams/` (Revideo), `youtube_manager_clone/` (Electron+React/Vite, **không được Python tham chiếu**) |
| Node/npm sẵn có? | **Node v20.20.2**, npm 10.8.2 |
| Có TypeScript nào của dự án? | **Không** |

⇒ Backend TypeScript trên Vercel là **greenfield hoàn toàn**, không có nợ kế thừa, nhưng cũng
**không có kinh nghiệm TS sẵn trong repo** — đây là rủi ro năng lực thật (`RISK_REGISTER.md` R68)
và là quyết định **D2** cần người dùng duyệt.

### 11b.2 Số đo quyết định kiến trúc storage

| Số đo | Giá trị | Ảnh hưởng |
|---|---|---|
| `output/` tổng | **26 GB** | Không thể đưa lên API |
| `.mp4` | **77 file, 25,3 GB, trung bình 336,9 MB** | Vượt xa giới hạn body 4,5 MB ⇒ **bắt buộc** ở lại local |
| `.wav` | 399 file, 0,9 GB, trung bình 2,4 MB | Cũng ở lại local |
| Audio script lớn nhất | **67 832 B** (`03_AUDIO_SCRIPT_MASTER.md`) | Dư **66×** so với 4,5 MB ⇒ vào Postgres thoải mái |
| SEO/shot-list JSON | trung bình 78 KB, **lớn nhất 194,8 KB** | Dư **23×** |
| File text lớn nhất trong Content-Creator | **444,9 KB** | Dư 10× |
| Đĩa còn trống | **19 GiB / 228 GiB (90 %)**, media +~2,8 GB/ngày | ≈ **7 ngày runway** — rủi ro vận hành, xem `STORAGE_STRATEGY.md §7` |

> **Đây là căn cứ số học cho quyết định "chỉ text lên backend, media ở lại local".**
> Nó biến giới hạn 4,5 MB của Vercel từ chướng ngại thành không liên quan.

### 11b.3 Kiểm chứng an toàn dữ liệu media

| Kiểm chứng | Kết quả |
|---|---|
| `finalize_episode.py:38-56,96-113` có upload master `.mp4` lên Drive? | ✅ Có (`gdrive:TTS-Output/{topic}/Video/`), và **chỉ dọn dẹp sau khi upload thành công** |
| Master `.mp4` thực tế trên Drive | **5 file, 9,43 GB** — khớp 1-1 với 5 master canonical dưới local |
| 77 `.mp4` local phân loại | **66 trung gian** (`_render_raw`, `_with_bgm`, `_render.mp4` — dựng lại được) + 11 "final-ish" (trùng lặp 5 master + 2 file test nhỏ) |
| `./cleanup_local.sh --dry-run` hôm nay | **`0 file sẽ bị xoá`** |

⇒ **Không có nguy cơ mất dữ liệu cấp bách.** Vấn đề còn lại là `cleanup_local.sh` xoá theo `mtime`
chứ không theo trạng thái nghiệp vụ — nên chuyển sang `retention_status` ở P4, nhưng **không khẩn cấp**.

### 11b.4 Ràng buộc Vercel (từ tài liệu chính thức, 2026-07)

| Ràng buộc | Giá trị |
|---|---|
| Request/response body | **4,5 MB** (413 `FUNCTION_PAYLOAD_TOO_LARGE`) |
| Max duration | Hobby **300s**; Pro **800s** (1800s beta) |
| Memory | Hobby 2 GB; Pro/Ent 4 GB |
| Bundle (Node, uncompressed) | 250 MB |

⇒ Xác nhận: **không** chạy TTS/ffmpeg/render trên Vercel. Đây là căn cứ kỹ thuật cho mô hình
"Vercel là control plane, CLI local là compute plane".

---

## 12. Ràng buộc quan trọng

1. **C1 — Máy đơn, macOS ARM.** Mọi thứ nặng (TTS, ffmpeg, ComfyUI, Remotion) chạy trên máy người dùng. Web app **không thể** tự build.
2. **C2 — Phụ thuộc CLI ngoài** (`agy`, `codex`, `rclone`, `ffmpeg` vendored, venv riêng của `video_tool_clone`). Không container hoá được dễ dàng.
3. **C3 — Artifact rất lớn** (26GB). Phải lưu ngoài DB, DB chỉ giữ đường dẫn + checksum.
4. **C4 — Upstream là dự án công khai.** Không làm bẩn `src/`, `pyproject.toml`, CI.
5. **C5 — Nguồn nội dung nằm ở repo khác** và chỉ được đọc.
6. **C6 — Single user.** Multi-tenant hiện **không có thật**; multi-*channel* mới là nhu cầu thật.

---

## 13. Unknowns / câu hỏi cần xác nhận

| ID | Câu hỏi | Vì sao quan trọng |
|---|---|---|
| U1 | Hub **thay thế**, **bọc**, hay **đọc** repo Content-Creator? | Quyết định toàn bộ data model. Xem D1 trong `FINAL_RECOMMENDATION.md`. |
| U2 | Web app chạy ở đâu — chỉ localhost hay có deploy cloud? | Quyết định mô hình worker, auth, và trust boundary. |
| U3 | 3 OAuth client = 3 Google Cloud project riêng? | Quyết định ngân sách quota. |
| U4 | Có cần multi-user thật (nhiều người review/approve) không? | Quyết định độ phức tạp của RBAC. |
| U5 | Có được phép commit lớp automation vào fork `audio_tool` không? | Chặn Phase 0. |
| U6 | Auto-publish hay chỉ chuẩn bị gói publish? | Quyết định publish gate. |

---

## 14. Bằng chứng lệnh đã chạy (read-only)

```
git branch --show-current; git status --porcelain | wc -l   # main; 63
git ls-files --others --exclude-standard '*.py' | wc -l     # 47
du -sh output                                               # 26G
jq 'keys[]' .youtube_channels/phat_giao.json                # tên khoá, KHÔNG in giá trị
grep -rn "shell=True" --include='*.py' .                    # 0 hit
.venv/bin/python -m pytest -q                               # No module named pytest
codex exec --sandbox read-only "..."                        # CODEX_OK
```

Không có lệnh nào ghi/xoá/deploy. Không in giá trị secret.
