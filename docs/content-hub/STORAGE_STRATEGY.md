# STORAGE_STRATEGY.md

> Bổ trợ cho `TARGET_ARCHITECTURE.md §4` và `DATA_MODEL_PLAN.md §6`. Tài liệu này **không mở lại**
> các quyết định đã chốt; nhiệm vụ của nó là ghi rõ *dữ liệu nào nằm ở đâu, vì sao, giữ bao lâu,
> kiểm tra bằng gì, hỏng thì làm sao*.
>
> **Quyết định nền (người dùng, 2026-07-29):** media (`.mp4`, `.wav`) **ở lại filesystem local và
> KHÔNG BAO GIỜ upload**. Chỉ **nội dung dạng text** đi lên backend. **Vercel Blob KHÔNG dùng ở MVP.**

---

## 0. Ba tầng lưu trữ

| Tầng | Vai trò | Trạng thái MVP |
|---|---|---|
| **Neon PostgreSQL** | Source of truth cho dữ liệu có cấu trúc **+ toàn bộ nội dung text** | **BẬT** |
| **Local filesystem** (`output/`, `chunks_cache/`, `assets/`, `bgm/`, `.youtube_channels/`) | Media nhị phân, cache trung gian, credential OAuth | **BẬT** (đang là hiện trạng) |
| **Vercel Blob** | Object storage cho payload vượt ngưỡng / evidence bundle | **TẮT — thiết kế sẵn, không bật** |

Ba tầng này **không đối xứng**: Neon là nơi duy nhất có backup tự động và semantics giao dịch;
local là nơi duy nhất có media; Blob hiện là **cột trống trong schema**, không phải một hệ thống đang chạy.

---

## 1. Bảng quyết định: dữ liệu nào ở đâu và vì sao

### 1.1 Nội dung text → **Neon**

| Dữ liệu | Cột / kiểu | Kích thước đo được | Vì sao Neon |
|---|---|---|---|
| `audio_script` | `text` | **lớn nhất 67 832 B** (`03_AUDIO_SCRIPT_MASTER.md`) | Reviewer đọc, agent sửa, engine chấm điểm, cần diff giữa revision |
| Script TTS thô (`.txt`) | `text` | lớn nhất **61 631 B** | Là input tái dựng — mất là mất khả năng rebuild |
| `seo_package`, `shot_list` | `jsonb` + `payload_schema_version` | lớn nhất **194,8 KB**, trung bình **78 KB** (7 file) | Cần query theo field, cần version hoá |
| `hook`, `outline`, `description`, `pinned_comment`, `research_summary`, `risk_notes`, `title_final` | `text` | ≪ 67 KB | Diff/score/approval gắn trực tiếp |
| `keywords`, `hashtags`, `title_candidates` | `text[]` | nhỏ | Cần tìm kiếm, cần `GIN` |
| `visual_prompts`, `semantic_beats`, `thumbnail_concepts`, `chapters` | `jsonb` | nhỏ | Hình dạng đổi theo domain/template |
| File text lớn nhất trong `content_repo_clone/` | `text` | **444,9 KB** | Vẫn ≈ **10×** dưới giới hạn body 4,5 MB của Vercel |

**Kết luận số học:** payload text lớn nhất trong toàn hệ thống là **444,9 KB**; giới hạn
request/response của Vercel Function là **4,5 MB** (lỗi `413 FUNCTION_PAYLOAD_TOO_LARGE`).
Biên an toàn **≈ 10×** cho trường hợp xấu nhất, **≈ 23–66×** cho payload thường gặp
(194,8 KB / 67,8 KB). Đây chính là lý do kiến trúc "chỉ text lên backend" khả thi trên Vercel
mà **không cần** object storage.

### 1.2 Media nhị phân → **Local filesystem, không upload**

| Loại | Số file | Tổng | Trung bình | Nơi lưu | DB lưu gì |
|---|---|---|---|---|---|
| `.mp4` | **77** | **25,3 GB** | **336,9 MB** | `output/**` | `local_path`, `sha256`, `byte_size`, `mime_type` |
| `.wav` | **399** | **0,9 GB** | **2,4 MB** | `output/**` | như trên |
| `.srt` | 142 | 0,5 MB | 3,5 KB | `output/**` | như trên (đủ nhỏ để cân nhắc đưa vào `text` — xem §1.4) |
| `.ass` | 78 | 3,7 MB | 48,5 KB | `output/**` | như trên |
| `.jpg` (thumbnail/asset) | 234 | 15,7 MB | 68,7 KB | `output/**`, `assets/` | như trên |
| **Tổng `output/`** | **1 552 file** | **26 GB** | — | — | — |

**Phân bố `.mp4` là lưỡng cực — con số trung bình 336,9 MB che giấu điều này** (đo trực tiếp):

| Thư mục | n | Tổng | Trung bình | Nhỏ nhất | Lớn nhất |
|---|---|---|---|---|---|
| `output/long/` | 6 | 10,58 GiB | **1 804,8 MiB** | 1 509,2 MiB | 2 100,4 MiB |
| `output/video_test/` | 7 | 13,07 GiB | **1 911,9 MiB** | 21,7 MiB | **3 637,0 MiB** |
| `output/shorts/` | 64 | 1,65 GiB | **26,4 MiB** | 7,6 MiB | 50,3 MiB |

Hệ quả: **một** video long ≈ 1,8 GB đã lớn hơn giới hạn body Vercel **400×**. Không có biến thể
kỹ thuật nào (chunk, stream, multipart qua Function) khiến việc đẩy media qua control plane trở
nên hợp lý. Quyết định "media ở lại local" **loại bỏ** toàn bộ lớp vấn đề này thay vì giải nó.

Bằng chứng `output/` đã được loại khỏi git từ trước: `.gitignore:32` (`output/`).
Protocol đã ghi nhận đúng ngữ nghĩa này: `API_AND_WORKER_PROTOCOL.md:185` (`"storage_backend":"LOCAL"`),
`:187` (`byte_size` 353 370 112 — tức ~337 MB), `:307` (`FILE Ở LẠI LOCAL`).

### 1.3 Credential → **chỉ local, không tầng nào khác**

`.youtube_channels/*.json` chứa `client_id`, `client_secret`, `refresh_token`
(`youtube_auth.py:136-137`), được `chmod 0o600` (`youtube_auth.py:139`) và gitignore
(`.gitignore:42-44`). Xem §8.

### 1.4 Vùng xám — quyết định rõ ràng để tránh trôi dạt

| Dữ liệu | Quyết định | Lý do |
|---|---|---|
| `.srt` / `.ass` (3,5–48,5 KB) | **Vừa** `artifact` metadata (local) **vừa** có thể mirror nội dung vào `content_revision`/`jsonb` ở Phase C | Nhỏ, nhưng ở Phase A vẫn là output của job ⇒ giữ nguyên là artifact để không tạo hai nguồn sự thật |
| `timing.json` | Artifact `LOCAL` | Phái sinh, tính lại được |
| Thumbnail `.jpg` (68,7 KB) | Artifact `LOCAL` | Nhị phân; không có nhu cầu query |
| Log build (`output/**/*.log`, 7 file) | **Local**; chỉ trích đoạn đã redact vào `job_event.payload` | Log thô có nguy cơ chứa path/secret ⇒ không đẩy nguyên khối |
| `bgm/*.mp3` (12 MB, CC BY 4.0) | **Local**, versioned ngoài DB | Không đổi theo item; DB chỉ cần ghi track nào được dùng + text attribution (xem §1.5) |
| `chunks_cache/` (375 MB) | **Local, ephemeral** | Cache thuần; xoá được bất kỳ lúc nào |
| `comfyui_local/` (8,2 GB), `video_tool_clone/` (3,5 GB) | **Local, tooling** | Không phải dữ liệu nội dung; không thuộc phạm vi retention của Hub |

### 1.5 BGM và nghĩa vụ attribution

`bgm/` là **CC BY 4.0** (`bgm/LICENSE.txt`); text attribution nằm ở `mix_bgm.py:34` và được in nhắc
ở `mix_bgm.py:121`. Vì attribution **bắt buộc phải xuất hiện trong description của video publish**,
nó là **nội dung text ⇒ thuộc Neon**, không phải metadata của file nhạc.

**Ràng buộc:** `content_revision.description` của mọi revision có BGM phải chứa `ATTRIBUTION_TEXT`;
kiểm bằng một `audit_finding` ở gate `PUBLISH_READY` (severity `BLOCKER`). Nếu chỉ dựa vào lệnh
`print` ở `mix_bgm.py:121` thì nghĩa vụ pháp lý phụ thuộc việc con người đọc stdout — không chấp nhận được.

---

## 2. Vì sao **KHÔNG** dùng Vercel Blob ở MVP

### 2.1 Bốn lý do, theo thứ tự sức nặng

| # | Lý do | Bằng chứng cụ thể |
|---|---|---|
| **B1** | **Không có nhu cầu.** Blob chỉ cần khi có blob để lưu. Media không upload (§1.2); text lớn nhất 444,9 KB, dưới giới hạn 4,5 MB **10×** và nằm gọn trong Postgres. | Số đo §1.1 |
| **B2** | **Mất khả năng query / diff / version — thứ đắt nhất.** Đưa `audio_script` hay `seo_package` vào Blob nghĩa là: không `WHERE`, không `JOIN`, không index toàn văn, không diff hai revision bằng SQL, không tính `content_sha256` trong cùng transaction ghi revision. `content_revision` được thiết kế để reviewer đọc, agent sửa, engine chấm, diff tính lúc đọc. | `DATA_MODEL_PLAN.md:113-134`, `:130` ("Diff: tính lúc đọc từ hai revision — **không lưu diff**") |
| **B3** | **Mất tính nguyên tử.** Postgres cho phép ghi revision + `content_sha256` + `audit_event` trong **một** transaction. Blob là hệ thống thứ hai, không tham gia transaction ⇒ sinh trạng thái nửa vời (row trỏ blob chưa tồn tại, hoặc blob mồ côi) và cần reconciliation job — đúng loại phức tạp mà `TARGET_ARCHITECTURE.md §0.5` đang cố tránh. | — |
| **B4** | **Thêm secret + thêm bề mặt tấn công.** Bật Blob = thêm `BLOB_READ_WRITE_TOKEN` vào env Vercel, thêm một quyền ghi vào một store ngoài, thêm đường xuất dữ liệu (exfiltration path) mà nội dung không tin cậy (LLM/nguồn web) có thể chạm tới. `TARGET_ARCHITECTURE.md:266-267` coi nội dung nguồn/LLM là **dữ liệu không tin cậy**. | `TARGET_ARCHITECTURE.md:108`, `:266-267` |

Chi phí là lý do **thứ yếu**, không phải lý do chính — xem §7.3.

### 2.2 Blob được thiết kế sẵn nhưng không bật

Schema đã dành chỗ, nên bật sau **không cần migration phá vỡ**:

| Bảng | Cột dự trữ | Giá trị MVP |
|---|---|---|
| `artifact` | `storage_backend` (`LOCAL\|BLOB`), `blob_url` null, `blob_key` null | luôn `LOCAL`; `blob_*` luôn `NULL` |
| `source_version` | `storage_backend` (`DB\|LOCAL\|BLOB`), `blob_url` null | `DB` hoặc `LOCAL` |

**Bất biến MVP (thực thi bằng CHECK, không bằng quy ước):**

```sql
-- artifact
CHECK (storage_backend = 'LOCAL')                                  -- gỡ khi bật Blob
CHECK (storage_backend <> 'LOCAL' OR (local_path IS NOT NULL
       AND blob_url IS NULL AND blob_key IS NULL))
CHECK (storage_backend <> 'BLOB'  OR (blob_key IS NOT NULL))
```

CHECK thứ nhất là **cầu chì**: nó biến "vô tình bật Blob" từ một sự cố im lặng thành một lỗi ghi.
Gỡ nó là một migration có chủ đích, review được.

### 2.3 Điều kiện **cụ thể** để bật Blob sau này

Bật Blob chỉ khi **≥ 1 điều kiện** dưới đây được đo đạc chứng minh, **và** ghi lại thành một
quyết định có ngày tháng:

| ID | Điều kiện kích hoạt | Ngưỡng đo được | Trạng thái hiện tại |
|---|---|---|---|
| **T1** | Một payload text hợp lệ vượt ngưỡng an toàn của body Vercel | **> 3,5 MB** (≈ 78 % của 4,5 MB, chừa header/encoding overhead) | Lớn nhất 444,9 KB — **cách ngưỡng 8×** |
| **T2** | Tổng dung lượng cột `text`/`jsonb` gây áp lực thật lên Neon | > 60 % hạn mức storage của gói Neon đang dùng | Ước tính ≪ 1 % (§7.1) |
| **T3** | Xuất hiện nhu cầu **evidence bundle** nén (log build, HTML snapshot nguồn) mà local không phục vụ được | Bundle > 1 MB **và** cần truy cập từ frontend không qua worker | Chưa có frontend (Phase 8) |
| **T4** | Frontend cần phục vụ asset tĩnh (preview thumbnail) cho người dùng không ngồi trên máy local | Có yêu cầu sản phẩm rõ ràng | Chưa có |
| **T5** | Người dùng **đảo ngược** quyết định "media không upload" | Quyết định tường minh, có ngày tháng | Không — quyết định 2026-07-29 giữ nguyên |

**Không** bật Blob vì lý do "cho gọn", "cho hiện đại", hay "vì Vercel có sẵn".
Nếu T1 xảy ra đơn lẻ, phương án rẻ hơn Blob là **nén trước khi ghi**: `gzip` + `bytea` trong
Postgres, hoặc tách nội dung thành `revision_section` (đã có trong `DATA_MODEL_PLAN.md §0.0`,
nhóm "Sau (P1b)"). Cả hai giữ nguyên tính nguyên tử và không thêm secret.

---

## 3. Nếu bật Blob sau: private vs public, và bẫy 4,5 MB

*(Phần này là thiết kế điều kiện — không có gì được triển khai ở MVP.)*

### 3.1 Access mode là **BẤT BIẾN sau khi tạo store**

Đây là ràng buộc quan trọng nhất và là lý do phải quyết định **trước khi** tạo store:
chế độ truy cập (private / public) của một Blob store **không đổi được sau khi tạo**.
Chọn sai ⇒ phải tạo store mới và migrate toàn bộ key.

| | **Private store** | **Public store** |
|---|---|---|
| Ai đọc được | Chỉ qua kiểm soát truy cập của ứng dụng | **Bất kỳ ai có URL** |
| Đường phục vụ | Qua **Vercel Function** | Trực tiếp từ CDN/blob endpoint |
| Trần kích thước khi đọc | **Bị giới hạn 4,5 MB response của Function** (§3.3) | Không bị trần 4,5 MB |
| Phù hợp cho | Evidence bundle, log, source snapshot, bất cứ thứ gì gắn nội bộ | Thumbnail công khai, asset tĩnh đã duyệt |
| Rủi ro | Trần 4,5 MB, thêm invocation, thêm latency | **URL bị đoán/rò là lộ vĩnh viễn**; không có cách "thu hồi" ngoài xoá blob |

**Khuyến nghị có điều kiện:**
- Nếu bật vì **T1/T3** (evidence, log, payload nội bộ) ⇒ **private store**.
- Nếu bật vì **T4** (thumbnail preview cho frontend) ⇒ **public store riêng**, chỉ chứa asset đã
  qua approval, **không bao giờ** chứa script/SEO/nguồn.
- **[ASSUMPTION]** Nếu cả hai nhu cầu cùng tồn tại thì dùng **hai store tách biệt**, vì access mode
  bất biến khiến việc "dùng chung một store rồi phân quyền theo prefix" là bất khả thi.
  Giả định này cần xác nhận lại với tài liệu Vercel tại thời điểm bật.

### 3.2 Upload: client-side vs server-side

| Kiểu | Tính chất | Hệ quả |
|---|---|---|
| **Client upload** | **Không phát sinh phí data transfer**; byte đi thẳng từ client tới Blob | Rẻ hơn, nhưng cần server phát hành token upload có phạm vi hẹp |
| **Server upload** | Byte đi qua Vercel Function ⇒ chịu phí **Fast Data Transfer**, **và** bị chặn bởi trần request 4,5 MB | Chỉ dùng cho payload nhỏ |
| **Multipart** | Được khuyến nghị cho file **> 100 MB** | Chỉ liên quan nếu T5 xảy ra (media) — hiện không |

Vì trần request 4,5 MB áp cho Function, **server upload không bao giờ là đường đi cho file lớn**.
Bất kỳ thiết kế Blob nào cho file > 4,5 MB **bắt buộc** là client upload (hoặc multipart client upload).

### 3.3 Bẫy: private blob + trần 4,5 MB response

Private blob được phục vụ **thông qua Function**, mà Function lại bị trần **4,5 MB response**.
Do đó:

> **Private store không thể phục vụ một object > 4,5 MB qua một lần đọc thông thường của Function.**

Hệ quả thiết kế nếu bật private store:

1. **Giữ mọi private object ≤ 3,5 MB.** Vượt ngưỡng ⇒ chia mảnh ở tầng ứng dụng (evidence bundle
   tách theo file, log xoay theo attempt) — không phải ở tầng transport.
2. Với object lớn hơn, phương án còn lại là **public store + key khó đoán**, tức đánh đổi bí mật
   lấy kích thước. Với evidence/log chứa nội dung nội bộ, đánh đổi này **không chấp nhận được**.
3. Vì vậy: **private store ⇒ trần cứng 3,5 MB/object là một ràng buộc thiết kế, không phải khuyến nghị.**

### 3.4 Mô hình tính phí (hình dạng, không phải con số)

Dung lượng Blob được tính bằng **trung bình theo tháng của các snapshot 15 phút**, không phải
đỉnh, cũng không phải giá trị cuối tháng. Hệ quả:
- Ghi rồi xoá nhanh thì **rẻ** (ít snapshot bắt được).
- Ghi rồi giữ nguyên tháng thì **đắt bằng đúng dung lượng đó**.
- Một retention policy hung hăng (xoá sớm) có tác dụng giảm phí **tuyến tính**.

**[ASSUMPTION]** Đơn giá cụ thể không được ghi ở tài liệu này vì nó thay đổi theo thời gian và theo
gói; phải tra lại bảng giá chính thức tại thời điểm ra quyết định T1–T5.

---

## 4. UNKNOWN: Python CLI không dùng được SDK `@vercel/blob`

### 4.1 Phát biểu vấn đề

`@vercel/blob` là SDK **JavaScript/TypeScript**. Worker của hệ thống này là **Python**
(`TARGET_ARCHITECTURE.md:127` — "CLI client: Python `httpx`"; toàn bộ pipeline hiện tại là Python).
Nếu Blob được bật và **worker** cần ghi/đọc blob, sẽ có một khoảng trống công cụ.

> **Đây là một UNKNOWN. Tài liệu này KHÔNG khẳng định có hay không một HTTP API công khai,
> được tài liệu hoá chính thức và ổn định cho Vercel Blob mà client Python có thể gọi trực tiếp.**
> Không có bằng chứng nào trong repo hay trong các ràng buộc đã xác minh cho phép kết luận điều đó.
> Bất kỳ thiết kế nào dựa trên giả định đó đều **chưa được chứng minh**.

### 4.2 Spike bắt buộc trước khi cam kết (SPIKE-BLOB-PY)

Chỉ chạy spike này **khi và chỉ khi** một điều kiện T1–T5 (§2.3) đã kích hoạt.

| Bước | Câu hỏi phải trả lời | Tiêu chí "xong" |
|---|---|---|
| S1 | Tài liệu chính thức của Vercel có mô tả một giao thức HTTP ổn định cho upload/download blob, dùng được ngoài SDK JS không? | Trích dẫn được URL tài liệu chính thức **hoặc** kết luận rõ ràng "không có" |
| S2 | Cơ chế **client upload token** có cho phép một client không-JS thực hiện upload không? Token phát hành ở đâu, phạm vi ra sao, TTL bao nhiêu? | Có luồng end-to-end chạy được, hoặc kết luận "không" |
| S3 | Nếu S1/S2 âm tính: chi phí duy trì một shim Node là bao nhiêu? | Đo được thời gian khởi động, kích thước dependency, số điểm lỗi thêm vào |
| S4 | Payload thực tế cần đẩy là bao nhiêu byte và có bị trần 4,5 MB không? | Con số đo được, không phải ước lượng |

**Điều kiện dừng spike:** nếu sau S1–S2 mà đường đi Python-thuần không được tài liệu chính thức
bảo chứng, **dừng** và chọn phương án 4.3-C hoặc 4.3-D. **Không** reverse-engineer giao thức nội bộ —
giao thức không được tài liệu hoá có thể đổi mà không báo trước, và một pipeline sản xuất không
được đặt trên nền đó.

### 4.3 Bốn phương án, kèm đánh giá

| | Phương án | Điều kiện khả thi | Ưu | Nhược | Vai trò |
|---|---|---|---|---|---|
| **A** | Python gọi trực tiếp giao thức HTTP của Blob | **Chỉ khi S1 dương tính** với tài liệu chính thức | Không thêm runtime | **Chưa chứng minh được**; rủi ro phụ thuộc bề mặt không được bảo chứng | Chỉ dùng nếu S1 rõ ràng |
| **B** | Proxy qua Vercel Function (`POST /api/blob/upload`, Function gọi SDK) | Payload **≤ 3,5 MB** | Dùng đúng SDK chính thức; secret không rời server | **Trần cứng 4,5 MB**; phát sinh **Fast Data Transfer** (server upload); thêm latency | Dùng được cho evidence/log nhỏ |
| **C** | **Shim Node cục bộ**: Python gọi `subprocess.run([...])` một script Node nhỏ dùng `@vercel/blob` | Máy local có Node | Dùng SDK chính thức, **không** phụ thuộc bề mặt không tài liệu; không bị trần 4,5 MB nếu là client upload | Thêm runtime Node vào worker; thêm một biên giới process | **Fallback được khuyến nghị** |
| **D** | **Không dùng Blob**: nén + `bytea` trong Postgres, hoặc để nguyên ở local | Luôn khả thi | Không thêm dịch vụ, không thêm secret, giữ nguyên tính nguyên tử | Không phục vụ được T4 (asset công khai cho frontend) | **Mặc định hiện tại** |

**Khuyến nghị:** giữ **D**. Nếu buộc phải bật Blob, thứ tự ưu tiên là **C → B → A**.
Phương án **C** cố ý đặt trước **A** vì nó đổi một phụ thuộc *runtime* (Node — đã có sẵn trên máy
dev, và `apps/hub/` đã là project Node theo `TARGET_ARCHITECTURE.md:150-152`) lấy việc loại bỏ một
phụ thuộc *không được bảo chứng*.

**Ràng buộc bảo mật cho phương án C:** shim Node được gọi bằng `subprocess.run` với
**list argv, tuyệt đối không `shell=True`** — đúng bất biến chống RCE ở `TARGET_ARCHITECTURE.md:266`.
Đường dẫn file truyền vào shim phải được validate là nằm trong thư mục cho phép; **không** nhận
đường dẫn phái sinh từ nội dung LLM/nguồn.

---

## 5. Retention policy

### 5.1 Nguyên tắc bất đối xứng

> **Bản ghi DB giữ vĩnh viễn. File media thì không.**

Điều này khả thi vì `artifact` là **metadata-only** (`DATA_MODEL_PLAN.md:248`): xoá file không làm
mất bản ghi. Ba trường mô tả ba khía cạnh **độc lập** và không được gộp:

| Trường | Miền giá trị | Ý nghĩa | Ai ghi |
|---|---|---|---|
| `storage_state` | `PRESENT \| PRUNED \| MISSING` | **Thực tế quan sát được**: file có còn trên đĩa không, và nếu không thì vì sao | Worker (sau khi quét) |
| `retention_status` | `KEEP \| PRUNABLE \| PRUNED` | **Chính sách**: được phép xoá hay không | Server (suy ra từ trạng thái nghiệp vụ) |
| `verification_status` | `UNVERIFIED \| VERIFIED \| MISMATCH` | **Tính toàn vẹn**: nội dung có khớp `sha256` không | Worker báo, server ghi |

Phân biệt then chốt: **`PRUNED` là mất mát có chủ đích; `MISSING` là mất mát ngoài ý muốn.**
Gộp hai thứ này là mất khả năng phát hiện sự cố đĩa.

### 5.2 Quy tắc suy ra `retention_status`

| Điều kiện của artifact | `retention_status` | Lý do |
|---|---|---|
| `promotion_state='PROMOTED'` **và** revision là `production_revision_id` **và** item chưa `PUBLISHED` | `KEEP` | Đang chờ publish — mất file là phải render lại |
| `role='VIDEO_FINAL'` **và** item đã `PUBLISHED` | `PRUNABLE` sau **N ngày** kể từ `published_at` | Bản đã publish tồn tại trên YouTube; local chỉ là bản sao (xem cảnh báo §9.4) |
| `promotion_state='PROVISIONAL'` **và** attempt đã `FAILED`/`EXPIRED` | `PRUNABLE` ngay | Rác của lần thử hỏng |
| `promotion_state='SUPERSEDED'` | `PRUNABLE` ngay | Đã bị bản khác thay thế |
| `role='VIDEO_RAW'` (trung gian trước mix/BGM) | `PRUNABLE` sau **7 ngày** | Dựng lại được từ `AUDIO_WAV` + asset |
| `role='AUDIO_WAV'` của revision `FROZEN` | `KEEP` cho tới khi item `PUBLISHED` | TTS đắt và **không tất định** (§5.4) — không rẻ như "render lại" |
| Bất kỳ artifact nào của revision đang bị tranh chấp (`audit_finding` mở, severity `BLOCKER`) | `KEEP` | Là bằng chứng |
| `content_revision` không `FROZEN` | `PRUNABLE` | Chưa phải sản phẩm |

**[ASSUMPTION]** `N = 30` ngày cho `VIDEO_FINAL` sau publish. Con số này chưa được người dùng chốt;
nó phải là tham số cấu hình, không phải hằng số nhúng trong code.

### 5.3 Xung đột đã tồn tại với `cleanup_local.sh` — **phải sửa**

`cleanup_local.sh` hiện tại:

| Dòng | Nội dung | Vấn đề |
|---|---|---|
| `cleanup_local.sh:13` | `DAYS=14` | Mặc định |
| `cleanup_local.sh:32` | `TARGETS=("chunks_cache" "drive_input" "output")` | `output/` nằm trong danh sách xoá |
| `cleanup_local.sh:48` | `find "$dir" -type f -mtime "+${DAYS}" -delete` | Xoá theo **`mtime`**, **không tra DB**, **không phân biệt** `KEEP` với `PRUNABLE` |

> **✅ Đính chính (đã kiểm chứng trực tiếp, 2026-07-29).** Bản nháp đầu của tài liệu này cảnh báo
> rằng `cleanup_local.sh` sẽ xoá vĩnh viễn master `.mp4` chưa từng upload. **Điều đó SAI** —
> đã xác minh lại và bác bỏ:
>
> | Kiểm chứng | Kết quả |
> |---|---|
> | `finalize_episode.py:38-56,96-113` có upload master `.mp4` lên `gdrive:TTS-Output/{topic}/Video/` | ✅ Có, và **chỉ dọn dẹp sau khi upload thành công** (`:108-113`) |
> | `rclone lsjson gdrive:TTS-Output/ -R` | **5 master `.mp4` (9,43 GB) đã có trên Drive** |
> | Đối chiếu tên: 5 master trên Drive vs 5 master canonical dưới local | **Khớp 1-1** (EP001 BUD, EP001 FS, EP005, EP006, EP007) |
> | `./cleanup_local.sh --dry-run` chạy hôm nay | **`Tổng cộng 0 file sẽ bị xoá`** |
> | 66/77 `.mp4` local là trung gian (`_render_raw`, `_with_bgm`, `_render.mp4`) | **Dựng lại được**, không phải master |
>
> ⇒ Giả định trong comment `cleanup_local.sh:2-4` **đúng cho master**: `finalize_episode.py` đã
> upload trước khi dọn. Không có nguy cơ mất dữ liệu cấp bách, và **không** cần hành động khẩn cấp
> trước `2026-08-04`.

**Vấn đề còn lại là thật, nhưng nhẹ hơn nhiều:** script xoá theo `mtime` chứ không theo *trạng thái
nghiệp vụ*. Khi Hub có bảng `artifact`, việc prune nên do `retention_status` quyết định thay vì
tuổi file — để không phụ thuộc vào việc mọi luồng đều nhớ upload trước khi dọn.

**Yêu cầu bắt buộc trước khi Hub được coi là tin cậy** (thuộc Phase P4, cùng bảng `artifact`):

1. `cleanup_local.sh` **không được xoá `output/` một cách mù quáng**. Nó phải hoặc (a) bỏ `output`
   khỏi `TARGETS`, hoặc (b) nhận một **danh sách cho phép xoá** do Hub sinh ra.
2. Thêm lệnh `hub_cli prune --plan` → gọi `GET /api/worker/artifacts/prunable` → xuất danh sách
   `local_path` có `retention_status='PRUNABLE'`; và `hub_cli prune --apply` để thực thi.
3. Sau khi xoá thành công: `POST` cập nhật `storage_state='PRUNED'`, `retention_status='PRUNED'`,
   ghi `audit_event`. **Bản ghi `artifact` không bao giờ bị xoá.**
4. Mặc định của mọi lệnh prune là **`--dry-run`** (`cleanup_local.sh:9,35,44-46` đã có sẵn cơ chế này — giữ nguyên).
5. Dùng lại pattern khoá file đã có (`registry_lock.py:23-34`, `fcntl.flock` blocking) để hai tiến
   trình prune không chạy chồng.

### 5.4 Vì sao `AUDIO_WAV` được ưu tiên giữ hơn `VIDEO_RAW`

`render_engine.py:195-207`: sampling TTS có `temperature`, retry tăng nhiệt, **không có seed**
(đã ghi nhận ở `DATA_MODEL_PLAN.md:144-145` — "**Không hứa output byte-identical**").
Do đó:

- **Render lại video** từ `AUDIO_WAV` + asset + config ⇒ kết quả tương đương, chi phí là thời gian CPU/GPU.
- **Render lại audio** từ script ⇒ ra **một bản đọc khác**, không phải bản cũ. Nếu bản cũ đã được
  con người duyệt (`approval`), bản mới **không** thừa hưởng approval đó.

Đây là lý do kỹ thuật, không phải sở thích: `AUDIO_WAV` mang thông tin không tái tạo được;
`VIDEO_RAW` thì không.

### 5.5 Retention của các tầng khác

| Đối tượng | Retention |
|---|---|
| `content_revision` (mọi trạng thái) | **Vĩnh viễn.** Không xoá — `DATA_MODEL_PLAN.md:130` |
| `score_run`, `audit_run`, `approval`, `audit_event` | **Vĩnh viễn, append-only** — `DATA_MODEL_PLAN.md:30, 190, 214` |
| `artifact` (bản ghi) | **Vĩnh viễn**, kể cả khi file đã `PRUNED` |
| `job_event` | Giữ ≥ 90 ngày; sau đó gộp/lưu trữ. **[ASSUMPTION]** — chưa chốt |
| `chunks_cache/`, `drive_input/` | Ephemeral — `cleanup_local.sh` xoá tự do, không cần Hub |
| `.youtube_channels/` | **Không bao giờ prune tự động** — mất là phải chạy lại `youtube_auth.py bootstrap` cho từng kênh |

---

## 6. Checksum & verification

### 6.1 Hiện trạng: **chưa có gì**

Quét toàn repo (loại các thư mục clone): `hashlib` chỉ xuất hiện ở `asset_generation.py:35`,
và chỉ dùng để **hash prompt** làm seed (`:66`) và làm tên file (`:94`).
**Không có một dòng code nào đang tính checksum cho artifact media.**
Toàn bộ §6 là **công việc mới**, không phải mô tả cái đang chạy.

### 6.2 Ai tính, tính khi nào

| | Chi tiết |
|---|---|
| **Thuật toán** | `sha256`, hex thường, **bắt buộc**, không nullable |
| **Ai tính** | **Worker (Python)**, luôn luôn. Server **không bao giờ** tính vì server **không bao giờ** thấy byte của media. |
| **Khi nào** | Ngay sau khi file được ghi xong và đóng, **trước** `POST /api/worker/jobs/{id}/artifacts` (`API_AND_WORKER_PROTOCOL.md:179`) |
| **Cách tính** | Đọc theo chunk (1 MiB) — file lớn nhất đo được là **3 637 MiB**, không được nạp vào RAM |
| **Server làm gì** | Lưu `sha256` như dữ liệu **do worker khai báo**; dùng làm khoá idempotency `(job_attempt_id, role, sha256)` (`DATA_MODEL_PLAN.md:258`) |

**Giới hạn tin cậy phải nói rõ:** `sha256` do worker khai báo **không** là bằng chứng chống worker
độc hại — worker có thể khai bất kỳ giá trị nào. Nó là biện pháp chống **hỏng hóc** (đĩa lỗi,
ghi dở, xoá nhầm, đồng bộ sai), **không phải** chống **gian lận**. Điều này nhất quán với
`TARGET_ARCHITECTURE.md:173-175` (worker token là bearer, không chứng minh sở hữu).
Với dữ liệu mà server **verify được**, cơ chế khác được dùng: `input_snapshot_hash` phải khớp
`content_revision.content_sha256` (`DATA_MODEL_PLAN.md:191`), và `manifest_sha256` được verify hai chiều
(`API_AND_WORKER_PROTOCOL.md:135`).

### 6.3 Khi nào verify lại

| Thời điểm | Bắt buộc? | Lý do |
|---|---|---|
| Trước khi **publish** lên YouTube | **BẮT BUỘC** | Đây là hành động không hoàn tác được. `youtube_upload.py` đọc file từ đĩa (resumable, chunk 8 MB — `youtube_upload.py:2,8`); upload nhầm file hỏng là sự cố công khai. |
| Khi **resume** một job | **BẮT BUỘC** | `API_AND_WORKER_PROTOCOL.md:245` đã yêu cầu "worker verify lại `sha256`" trước khi tái dùng checkpoint |
| Trước khi **prune** một artifact `PRUNABLE` | **BẮT BUỘC** | Nếu file đã `MISMATCH`, việc xoá phải được ghi nhận khác với việc xoá một file lành |
| **Sweep định kỳ** (`VERIFY_ARTIFACTS`) | Khuyến nghị **hàng tuần** cho `retention_status='KEEP'` | Phát hiện bit-rot và xoá nhầm sớm |
| Sau khi **khôi phục** từ backup thủ công | **BẮT BUỘC** | Xác nhận bản khôi phục đúng |

**Chi phí sweep:** đọc lại toàn bộ 26 GB. **[ASSUMPTION]** Trên SSD nội bộ ~1 GB/s, sweep toàn phần
≈ 30 giây I/O thuần; tức chi phí **không đáng kể** và không cần tối ưu sớm. Nếu về sau tổng vượt
~500 GB, chuyển sang sweep phân tầng: `KEEP` hàng tuần, phần còn lại hàng tháng.

> Sweep định kỳ **chỉ đọc**, không sửa file. Nó chạy như một `job_type` mới; nếu thêm thì phải bổ
> sung vào allowlist đóng ở `TARGET_ARCHITECTURE.md §9` — allowlist là **đóng**, không được vượt rào.

### 6.4 Xử lý kết quả verify

| Quan sát | `storage_state` | `verification_status` | Hành động |
|---|---|---|---|
| File tồn tại, hash khớp | `PRESENT` | `VERIFIED` | Cập nhật `checksum_verified_at` |
| File tồn tại, **hash lệch** | `PRESENT` | **`MISMATCH`** | Xem §6.5 |
| File không tồn tại, `retention_status='PRUNED'` | `PRUNED` | giữ nguyên | Bình thường — không cảnh báo |
| File không tồn tại, `retention_status ∈ {KEEP, PRUNABLE}` | **`MISSING`** | giữ nguyên | Cảnh báo; xem §6.6 |
| File tồn tại nhưng `byte_size` lệch | `PRESENT` | **`MISMATCH`** | Như §6.5 (lệch size là dấu hiệu ghi dở) |

### 6.5 Quy trình xử lý `MISMATCH` — **fail-closed**

`MISMATCH` nghĩa là *file trên đĩa không phải file mà hệ thống đã ghi nhận và (có thể) đã duyệt*.
Đây là sự cố toàn vẹn, không phải cảnh báo.

1. **Chặn ngay:** artifact bị `MISMATCH` **không được** publish, **không được** dùng làm resume
   checkpoint, **không được** promote. Thực thi ở server, không ở worker.
2. **Không tự sửa.** Tuyệt đối **không** ghi đè `sha256` trong DB bằng giá trị mới đo được — làm vậy
   là biến bằng chứng sự cố thành dữ liệu hợp lệ. `artifact.sha256` là bất biến sau khi ghi.
3. **Không tự xoá file.** File lệch là bằng chứng để điều tra.
4. **Ghi `audit_event`** (`action='ARTIFACT_CHECKSUM_MISMATCH'`, `actor_kind='WORKER'`) kèm hash
   quan sát được trong `after`. Bảng audit là append-only (`DATA_MODEL_PLAN.md:73`).
5. **Nếu revision đã có `approval` `ACTIVE` dựa trên artifact này:** đây là tình huống nghiêm trọng
   nhất — nội dung đã duyệt không còn khớp file. Đề xuất: `approval.status='REVOKED'` với
   `revoke_reason='ARTIFACT_INTEGRITY'`, do **người dùng** xác nhận (`approval` chỉ nhận
   `actor_kind='USER'` — `DATA_MODEL_PLAN.md:212`).
6. **Khắc phục:** tạo `job_attempt` mới để sinh lại artifact. Artifact cũ chuyển
   `promotion_state='SUPERSEDED'`, **giữ nguyên** bản ghi và hash cũ.

### 6.6 Xử lý `MISSING`

`MISSING` (file biến mất mà chưa được đánh dấu `PRUNED`) hầu như luôn có ba nguyên nhân:
`cleanup_local.sh` chạy mù (§5.3), thao tác tay, hoặc lỗi đĩa.

- `retention_status='KEEP'` + `MISSING` ⇒ **cảnh báo mức cao**, chặn publish, đề xuất re-render.
- `retention_status='PRUNABLE'` + `MISSING` ⇒ ghi nhận, hạ xuống `PRUNED`, không cảnh báo.
- **Nhiều** artifact chuyển `MISSING` trong cùng một sweep ⇒ dấu hiệu prune mù hoặc sự cố đĩa;
  dừng mọi job build và yêu cầu can thiệp thủ công.

---

## 7. Ước tính chi phí và tăng trưởng dung lượng

### 7.1 Neon — text, nhỏ, tăng chậm

Ước tính worst-case cho **một** `content_revision`:

| Thành phần | Worst-case | Ghi chú |
|---|---|---|
| `audio_script` | 67,8 KB | Số đo lớn nhất thực tế |
| `seo_package` + `shot_list` (jsonb) | 194,8 KB | Số đo lớn nhất thực tế |
| `outline`, `description`, `hook`, `research_summary`, `risk_notes`, `production_notes` | ~50 KB | Cộng dồn ước lượng |
| `visual_prompts`, `semantic_beats`, `chapters`, `thumbnail_concepts` | ~30 KB | |
| **Tổng/revision (worst-case, chưa nén)** | **≈ 350 KB** | |

Postgres nén tự động các giá trị lớn (TOAST/`pglz`); text tiếng Việt nén tốt.
**[ASSUMPTION]** hệ số nén 3× ⇒ **≈ 120 KB/revision trên đĩa**.

| Kịch bản | Số revision | Dung lượng ước tính (đã nén) |
|---|---|---|
| Import toàn bộ hiện trạng (≈ 80 item × 2 revision) | 160 | **≈ 19 MB** |
| 1 năm ở nhịp hiện tại (§7.2) — ước 3 000 revision | 3 000 | **≈ 360 MB** |
| 5 năm | 15 000 | **≈ 1,8 GB** |

Cộng thêm chỉ mục, `audit_event`, `job_event`, `video_daily_metric(+_history)` —
**[ASSUMPTION]** nhân hệ số 2,5× cho tổng DB.

**Kết luận:** dữ liệu text **không phải** là bài toán chi phí. Ngay cả sau 5 năm, DB ở thang **vài GB**.
Chi phí Neon sẽ bị chi phối bởi compute/branch, không bởi storage.
**[ASSUMPTION]** Gói Neon cụ thể chưa được chốt; nếu dùng gói free (hạn mức storage ~0,5 GB) thì
kịch bản 1 năm vẫn nằm trong hạn mức, kịch bản 5 năm thì không — cần đánh giá lại ở mốc ~2 năm.

### 7.2 Local — đây **mới** là bài toán

Đo trực tiếp, tất cả 77 `.mp4` được tạo trong cửa sổ **2026-07-21 → 2026-07-29** (9 ngày):

| Ngày | n | GiB |
|---|---|---|
| 2026-07-21 | 1 | 0,98 |
| 2026-07-22 | 3 | 1,44 |
| 2026-07-23 | 20 | **15,38** |
| 2026-07-24 | 13 | 0,36 |
| 2026-07-27 | 5 | 0,15 |
| 2026-07-28 | 31 | **6,86** |
| 2026-07-29 | 4 | 0,12 |
| **Tổng** | **77** | **25,29** |

- **Tốc độ trung bình: ≈ 2,8 GB/ngày** (25,3 GB / 9 ngày), ≈ **8,6 video/ngày**.
- Rất **bùng nổ**: hai ngày (07-23, 07-28) chiếm **88 %** tổng dung lượng.
- Dung lượng bị chi phối bởi **long/test** (avg 1,8–1,9 GB), không bởi shorts (avg 26,4 MB).
  **Một** video long ≈ **68 shorts**.

**Tình trạng đĩa (đo được):**

| Chỉ số | Giá trị |
|---|---|
| Dung lượng volume | 228 Gi |
| Đã dùng | 164 Gi |
| **Còn trống** | **20 Gi** |
| Mức sử dụng | **90 %** |

> **⚠️ Ở tốc độ 2,8 GB/ngày, 20 GiB trống tương đương ≈ 7 ngày runway.**
> Đây là hiện thực hoá cụ thể của `RISK_REGISTER.md:16` (**R04** — *"`output/` đã 26GB và đang tăng …
> Hết đĩa → job fail hàng loạt"*), nhưng khẩn cấp hơn mức "Medium likelihood" đang ghi ở đó.
> Nếu một ngày kiểu 07-23 (15,4 GiB) lặp lại, đĩa đầy **trong một ngày**.

**Chiếm dụng ngoài `output/` (không thuộc dữ liệu nội dung, nhưng cạnh tranh cùng một đĩa):**

| Thư mục | Dung lượng | Có thể thu hồi? |
|---|---|---|
| `output/` | 26 GB | Có — theo policy §5 |
| `comfyui_local/` | 8,2 GB | Tooling — cài lại được |
| `video_tool_clone/` | 3,5 GB | Clone — cài lại được |
| `remotion_typography/` | 637 MB | Tooling |
| `chunks_cache/` | 375 MB | Ephemeral — xoá tự do |
| `revideo_diagrams/` | 302 MB | Tooling |
| `content_repo_clone/` | 23 MB | Shallow clone (`content_repo.py:80-90`) |

**Ba việc theo thứ tự ưu tiên:**

| # | Việc | Thu hồi ước tính | Ghi chú |
|---|---|---|---|
| 1 | Xoá `output/video_test/` (7 file, **13,07 GiB**) | **~13 GB** | Là output thử nghiệm; chứa file `.mp4` lớn nhất (3 637 MiB). Cần người dùng xác nhận — tài liệu này **không** tự quyết. |
| 2 | Prune `VIDEO_RAW` sau 7 ngày (§5.2) | Tuỳ | Cần bảng `artifact` mới phân loại được |
| 3 | Cảnh báo ngưỡng đĩa (**< 15 % trống ⇒ chặn job `BUILD_VIDEO`**) | 0 | Fail-fast thay vì fail giữa chừng làm hỏng file |

Mục 3 nên là **kiểm tra tiền điều kiện trong worker trước khi claim job build** — nhất quán với
nguyên tắc fail-closed. Job bị hoãn thay vì thất bại giữa lúc ghi file, tránh sinh file cụt
(thứ sẽ trở thành `MISMATCH` ở §6.4).

### 7.3 Blob — chi phí **nếu** bật (không bật)

Không tính đơn giá cụ thể (§3.4). Chỉ ghi hình dạng chi phí để so sánh phương án:

| Kịch bản giả định | Dung lượng tính phí | Data transfer |
|---|---|---|
| **MVP hiện tại** | **0** | **0** |
| Bật cho evidence/log (T3) | ~vài trăm MB | Nhỏ; server upload ⇒ chịu Fast Data Transfer |
| Bật cho thumbnail công khai (T4) | 15,7 MB (234 `.jpg`) | Nhỏ |
| **Giả định phản thực: upload toàn bộ media (T5)** | **≥ 26 GB trung bình tháng, +2,8 GB/ngày** | Nếu client upload: **0 phí transfer** khi ghi; nếu server upload: bất khả thi (trần 4,5 MB) |

Điểm đáng chú ý: vì phí dung lượng tính theo **trung bình tháng của snapshot 15 phút**, kịch bản
media (26 GB **và đang tăng**) sẽ tạo một khoản chi phí **thường trực và tăng đơn điệu** — trái ngược
hoàn toàn với chi phí biên gần bằng 0 của việc giữ file trên đĩa đã mua. Đây là một luận cứ định
lượng bổ sung cho quyết định 2026-07-29, không phải luận cứ chính (luận cứ chính là §2.1 B2).

---

## 8. Điều **TUYỆT ĐỐI** không lưu — ở bất kỳ tầng nào

| Dữ liệu | Neon | Blob | Log/audit | Được lưu ở đâu |
|---|---|---|---|---|
| `client_secret` (Google OAuth) | ❌ | ❌ | ❌ | Chỉ `.youtube_channels/*.json`, `chmod 0600` |
| `refresh_token` (YouTube) | ❌ | ❌ | ❌ | như trên |
| `access_token` (kể cả đã hết hạn) | ❌ | ❌ | ❌ | Chỉ trong RAM tiến trình worker |
| `worker_token` / `api_token` / session token **giá trị thô** | ❌ | ❌ | ❌ | Chỉ `sha256` của token vào DB (`DATA_MODEL_PLAN.md:60, 64, 223`) |
| `CRON_SECRET`, `DATABASE_URL` | ❌ | ❌ | ❌ | Vercel env |
| Password thô | ❌ | ❌ | ❌ | Chỉ Argon2id hash |
| Response body thô từ Google API | ❌ | ❌ | ❌ | Có thể chứa token; chỉ lưu field đã normalize |

**Cơ sở hiện trạng:**
- `.gitignore:42-44` — comment tường minh: *"Chứa refresh_token OAuth YouTube -- tuyệt đối …"* + `.youtube_channels/`
- `youtube_auth.py:136-137` — file credential chứa `client_id`, `client_secret`, `refresh_token`
- `youtube_auth.py:139` — `creds_path.chmod(0o600)`
- Đã xác nhận trên đĩa: cả 3 file kênh (`hinh_su.json`, `phat_giao.json`, `phong_thuy.json`) đều `-rw-------`
- `channel` **không có** cột secret; `channel_credential_ref` chỉ giữ `credential_path` (`DATA_MODEL_PLAN.md:81, 84`)

**Cơ chế thực thi (không dựa vào kỷ luật con người):**

| Lớp | Kiểm soát |
|---|---|
| Schema | Không tồn tại cột nào để chứa secret ⇒ không thể ghi nhầm |
| Worker (trước khi gửi) | Redact theo pattern (`refresh_token`, `client_secret`, `Bearer …`, `ya29.…`) — `TARGET_ARCHITECTURE.md:270` |
| Server (trước khi ghi) | Redact lần hai trên `job_event.payload` (`DATA_MODEL_PLAN.md:245` — "**đã redact**") |
| Test | Test tự động quét mọi payload mẫu và mọi cột `text`/`jsonb` tìm pattern secret; fail build nếu trúng |
| CHECK (nếu Blob bật) | Allowlist content-type + giới hạn kích thước (`TARGET_ARCHITECTURE.md:272`) |

**Bất biến kiến trúc đứng sau:** token OAuth **không cần** rời máy vì mọi lệnh gọi YouTube đều chạy
ở worker; Vercel Cron **chỉ enqueue job**, không tự gọi YouTube (`TARGET_ARCHITECTURE.md:85, 126`).
Nếu một thiết kế tương lai đòi Vercel gọi YouTube trực tiếp, nó **buộc** phải đưa refresh token lên
cloud — và vì thế bị **từ chối**.

---

## 9. Backup & disaster recovery

### 9.1 Ba loại mất mát, ba mức nghiêm trọng khác nhau

| Mất gì | Khôi phục được không | Mức |
|---|---|---|
| Neon (script, SEO, approval, score, audit) | Có — PITR/branch (§9.2) | **Thảm hoạ nếu không có backup** |
| Media local (`.mp4`, `.wav`) | **Không có backup**; nhưng **render lại được** từ nội dung trong Neon | **Trung bình** (§9.4) |
| `.youtube_channels/` (credential) | Chạy lại `youtube_auth.py bootstrap` từng kênh, **cần tương tác trình duyệt** | **Thấp — nhưng gây gián đoạn** |

Điểm mấu chốt: **vì nội dung text nằm ở Neon (có backup), media trở thành dữ liệu *phái sinh*.**
Đây chính là thứ khiến quyết định "media ở lại local, không backup" trở nên chấp nhận được —
chứ không phải vì media không quan trọng.

### 9.2 Neon — có backup thật

| Cơ chế | Dùng cho |
|---|---|
| **PITR (point-in-time restore)** | Khôi phục sau xoá nhầm / migration hỏng, về một mốc thời gian |
| **Branching** | Tạo branch từ một mốc để *kiểm tra* dữ liệu trước khi khôi phục lên nhánh chính; cũng là branch test (`TARGET_ARCHITECTURE.md:128`) |

**Yêu cầu vận hành:**
1. **Diễn tập khôi phục ít nhất một lần** trước khi Phase B (dual-write) bắt đầu.
   `TARGET_ARCHITECTURE.md:193` đã yêu cầu "rollback đã diễn tập" — mở rộng sang restore DB.
2. Trước mỗi migration: tạo branch mốc, ghi lại tên branch vào `audit_event`.
3. **[ASSUMPTION]** Cửa sổ PITR phụ thuộc gói Neon (gói thấp thường chỉ vài ngày). Phải xác nhận
   cửa sổ thực tế; nếu < 7 ngày thì thêm `pg_dump` hàng tuần ra đĩa ngoài (dump chỉ vài trăm MB — §7.1).

### 9.3 Media local — **KHÔNG có backup tự động. Đây là rủi ro tồn dư.**

Đã xác minh:

| Kiểm tra | Kết quả |
|---|---|
| Time Machine | `tmutil destinationinfo` → **`No destinations configured.`** |
| Git | `output/` bị ignore (`.gitignore:32`) |
| Cloud sync | Chỉ luồng drive-queue upload (`render_engine.py:103-120`), chỉ `wav`+`srt`+`json`, chỉ khi có `rclone` (`render_engine.py:107-109` — thiếu `rclone` thì **im lặng bỏ qua**); **`.mp4` không nằm trong luồng này** với `output/long`, `output/shorts`, `output/video_test` |
| RAID / snapshot | Không có bằng chứng |

> **Kết luận thẳng: 25,3 GB video hiện tại tồn tại đúng một bản, trên một đĩa đã dùng 90 %,
> không có bản sao nào ở bất kỳ đâu.** Hỏng đĩa = mất toàn bộ.

Lưu ý thêm về `render_engine.py:107-109`: khi thiếu `rclone`, hàm chỉ in cảnh báo và `return False` —
tức **thất bại upload là im lặng đối với pipeline**. Nếu ai đó tin rằng "Drive đã có bản sao"
(niềm tin được `cleanup_local.sh:2-4` khuyến khích), niềm tin đó có thể sai mà không có tín hiệu nào.

### 9.4 Đề xuất DR cho media — ba mức, chọn theo khẩu vị rủi ro

| Mức | Nội dung | Chi phí | Bảo vệ được gì |
|---|---|---|---|
| **DR-0 — Chấp nhận** *(mặc định hiện tại)* | Không backup. Dựa vào: (a) nội dung text ở Neon; (b) video đã publish có bản trên YouTube; (c) render lại được | 0 | Mất **thời gian render**, không mất **nội dung** — trừ trường hợp §5.4 (giọng đọc đã duyệt không tái tạo y hệt) |
| **DR-1 — Sao chép chọn lọc** *(khuyến nghị)* | `rsync` ra đĩa ngoài, **chỉ** artifact `retention_status='KEEP'` + `promotion_state='PROMOTED'` + `role ∈ {AUDIO_WAV, VIDEO_FINAL}` | Một đĩa ngoài; ước lượng ≪ 26 GB vì loại `VIDEO_RAW` và `video_test` | Bảo vệ đúng phần không tái tạo được |
| **DR-2 — Sao chép toàn phần** | Mirror toàn bộ `output/` | ≥ 26 GB và tăng 2,8 GB/ngày | Bảo vệ tất cả, kể cả rác |

**Khuyến nghị: DR-1.** Lý do định lượng: `VIDEO_RAW` và `video_test` chiếm phần lớn dung lượng
(riêng `video_test` là 13,07 GiB / 51 %) nhưng gần như không mang giá trị không tái tạo được.
Sao lưu có chọn lọc đổi một lượng nhỏ dung lượng lấy phần lớn giá trị.

**Điều kiện tiên quyết của DR-1:** phải có bảng `artifact` với `role` + `retention_status` +
`promotion_state` để *biết được* file nào cần sao. **Trước Phase P4 thì DR-1 chưa thực hiện được** —
lúc đó chỉ có DR-0 hoặc DR-2. Đây là một lý do độc lập để ưu tiên P4.

### 9.5 Ba cảnh báo về việc coi YouTube là backup

1. **Chỉ áp dụng cho video đã publish.** Video ở `BUILT`/`PUBLISH_READY` không có bản sao nào.
2. **YouTube trả về bản đã transcode**, không phải master. Tải xuống rồi re-upload sẽ mất chất lượng.
3. **Kênh bị đình chỉ / video bị gỡ ⇒ mất luôn "backup".** Sự kiện gỡ nội dung và sự kiện hỏng đĩa
   là độc lập, nhưng một kênh bị strike có thể mất nhiều video cùng lúc — tương quan cao.

Do đó YouTube được tính là **bản sao cơ hội**, không phải backup. `retention_status='PRUNABLE'` cho
`VIDEO_FINAL` sau publish (§5.2) là một đánh đổi có chủ đích, cần người dùng biết rõ, không phải mặc định vô hại.

### 9.6 Credential — DR đơn giản nhưng đừng bỏ sót

Ba file `.youtube_channels/*.json` (578 B, 572 B, 577 B) là thứ **nhỏ nhất nhưng gây gián đoạn nhất**
khi mất: khôi phục cần chạy lại `youtube_auth.py bootstrap` cho từng kênh với **tương tác trình duyệt**
(`youtube_auth.py:84, 195`), và `youtube_auth.py:123-125` cảnh báo Google **chỉ trả `refresh_token` ở
lần consent thật sự MỚI** — tức phải vào Google Account gỡ quyền ứng dụng trước.

**Đề xuất:** sao lưu **thủ công, ngoài băng tần**, vào một password manager (không phải đĩa ngoài
không mã hoá, không phải cloud sync). **Không** đưa vào bất kỳ script tự động nào — mỗi automation
chạm tới file này là một đường rò secret mới.

---

## 10. Bảng tổng hợp bất biến storage

| ID | Bất biến | Thực thi bằng | Vi phạm thì sao |
|---|---|---|---|
| **ST-1** | Media **không bao giờ** đi qua Vercel API | `artifact` là metadata-only; API không có endpoint nhận binary (`API_AND_WORKER_PROTOCOL.md:179` "**metadata only**") | Chạm trần 4,5 MB — thất bại rõ ràng, không âm thầm |
| **ST-2** | `storage_backend='LOCAL'` cho mọi artifact ở MVP | `CHECK (storage_backend = 'LOCAL')` — cầu chì, gỡ bằng migration có chủ đích | Ghi thất bại |
| **ST-3** | `LOCAL` ⇒ `local_path NOT NULL` **và** `blob_url IS NULL` **và** `blob_key IS NULL` | CHECK ghép | Ghi thất bại |
| **ST-4** | `BLOB` ⇒ `blob_key NOT NULL` | CHECK ghép | Ghi thất bại |
| **ST-5** | `sha256` **bắt buộc**, do worker tính, **bất biến sau khi ghi** | `NOT NULL` + trigger chặn UPDATE cột này | Không ghi được artifact thiếu hash; không "sửa" hash để che lỗi |
| **ST-6** | Bản ghi `artifact` **không bao giờ bị xoá**, kể cả khi file đã bị prune | Không có endpoint DELETE; prune chỉ đổi `storage_state`/`retention_status` | Mất lịch sử sản xuất |
| **ST-7** | `PRUNED` ≠ `MISSING` — xoá có chủ đích tách khỏi mất mát ngoài ý muốn | Enum `storage_state` ba giá trị; prune **phải** đặt `retention_status='PRUNED'` **trước** khi xoá file | Không phân biệt được sự cố với vận hành bình thường |
| **ST-8** | Chỉ artifact `promotion_state='PROMOTED'` mới publish được | Partial unique `(build_job_id, role) WHERE promotion_state='PROMOTED'` (`DATA_MODEL_PLAN.md:259`) | Publish nhầm bản thử |
| **ST-9** | Artifact `verification_status='MISMATCH'` **không được** publish / promote / dùng làm resume checkpoint | Kiểm ở server trước mỗi hành động; fail-closed | Upload file hỏng lên YouTube |
| **ST-10** | Verify `sha256` **bắt buộc** trước publish, trước resume, trước prune | Điều kiện tiên quyết ở server + worker (`API_AND_WORKER_PROTOCOL.md:245`) | Hành động không hoàn tác trên dữ liệu chưa xác minh |
| **ST-11** | Prune **chỉ** dựa trên `retention_status='PRUNABLE'` do server tính, **không** dựa trên `mtime` | `hub_cli prune --plan/--apply`; `cleanup_local.sh` không được tự xoá `output/` (§5.3) | Xoá vĩnh viễn master chưa publish |
| **ST-12** | Mặc định của mọi lệnh prune là **dry-run** | Cờ `--apply` bắt buộc để xoá thật (`cleanup_local.sh:9` đã có tiền lệ) | Xoá nhầm do gõ nhầm |
| **ST-13** | Secret (`client_secret`, `refresh_token`, `access_token`, token thô) **không tồn tại** ở Neon, Blob, log, audit | Không có cột chứa được + redact hai lớp + test quét pattern | Lộ quyền kiểm soát kênh YouTube |
| **ST-14** | Nội dung text là **source of truth**; media là **phái sinh** | Mọi trường text ở `content_revision`; artifact chỉ trỏ file | Không rebuild được sau khi mất đĩa |
| **ST-15** | Không có tiến trình nào **ghi ngược** vào `content_repo_clone/` | Chỉ đọc (`TARGET_ARCHITECTURE.md:73`); clone là shallow + `reset --hard` (`content_repo.py:80-90`) — ghi vào đó **sẽ mất** ở lần sync sau | Mất dữ liệu âm thầm |
| **ST-16** | Attribution BGM (CC BY 4.0) nằm trong `content_revision.description`, không chỉ ở stdout | `audit_finding` `BLOCKER` ở gate `PUBLISH_READY` (§1.5) | Vi phạm điều khoản giấy phép |
| **ST-17** | Hai tiến trình prune/verify **không chạy chồng** | `fcntl.flock` theo pattern `registry_lock.py:23-34` | Race làm sai `storage_state` |
| **ST-18** | Job `BUILD_VIDEO` **không được claim** khi đĩa trống < 15 % | Kiểm tiền điều kiện ở worker trước claim (§7.2) | Fail giữa lúc ghi ⇒ file cụt ⇒ `MISMATCH` |

---

## 11. Tổng hợp assumption cần chốt

| ID | Assumption | Ai chốt | Chặn cái gì |
|---|---|---|---|
| **A-ST1** | `N = 30` ngày trước khi `VIDEO_FINAL` đã publish thành `PRUNABLE` (§5.2) | Người dùng | Policy prune |
| **A-ST2** | `job_event` giữ 90 ngày (§5.5) | Người dùng | Policy prune DB |
| **A-ST3** | Hệ số nén Postgres 3×; hệ số tổng DB 2,5× (§7.1) | Đo lại sau import thật | Ước tính chi phí Neon |
| **A-ST4** | Gói Neon và cửa sổ PITR thực tế (§9.2) | Người dùng | Kế hoạch DR. ⚠️ Cơ chế hoàn tác import đã chốt là **branch-based restore** (`LEGACY_IMPORT_AND_SYNC_PLAN §6.1`), **không** phụ thuộc cửa sổ PITR |
| **A-ST5** | Sweep verify hàng tuần là đủ; chi phí I/O không đáng kể (§6.3) | Đo lại khi > 500 GB | Lịch sweep |
| **A-ST6** | Nếu bật Blob cho cả nhu cầu nội bộ và công khai thì phải dùng **hai store** do access mode bất biến (§3.1) | Xác nhận lại tài liệu Vercel tại thời điểm bật | Thiết kế Blob |
| **A-ST7** | Xoá `output/video_test/` (13,07 GiB) là an toàn (§7.2) | **Người dùng — chưa xác nhận** | Giải phóng đĩa khẩn cấp |
| **A-ST8** | Đơn giá Blob (§3.4, §7.3) | Tra bảng giá chính thức khi cần | So sánh chi phí |

---

## 12. Việc phải làm, theo thứ tự khẩn cấp

| # | Việc | Vì sao gấp | Phase |
|---|---|---|---|
| 1 | Theo dõi 20 GiB trống / 2,8 GB mỗi ngày (§7.2) | ⚠️ **Sửa theo Codex v2R1 HIGH-6: đây là rủi ro VẬN HÀNH, KHÔNG phải điều kiện tiên quyết của backend.** Bản trước ghi "Ngay, trước mọi code Hub" — tạo phụ thuộc phase giả, có thể chặn oan việc backend vì một tình trạng không đổi kiến trúc và không đe doạ dữ liệu canonical (master đã có trên Drive; `--dry-run` xoá 0 file). Xử lý song song, có ngưỡng cảnh báo riêng | **Vận hành — song song, KHÔNG chặn phase nào** |
| 2 | ~~Vô hiệu hoá `cleanup_local.sh`~~ → **Không còn gấp** (§5.3 đính chính) | Đã xác minh: `finalize_episode.py` upload master lên Drive **trước khi** dọn; 5/5 master canonical có mặt trên Drive; `--dry-run` hôm nay xoá **0 file**. Việc chuyển prune sang `retention_status` vẫn nên làm, nhưng ở **P4**, không khẩn cấp | P4 |
| 3 | Sao lưu thủ công `.youtube_channels/` vào password manager (§9.6) | Nhỏ, rẻ, khôi phục lại rất phiền | Ngay |
| 4 | Triển khai `artifact` + `sha256` + `storage_state` + `retention_status` | Là tiền đề của prune có kiểm soát **và** của DR-1 | **P4** |
| 5 | `hub_cli prune --plan/--apply` thay cho xoá theo `mtime` | Biến retention từ quy ước thành cơ chế | P4 |
| 6 | Sweep `VERIFY_ARTIFACTS` định kỳ | Phát hiện `MISSING`/`MISMATCH` sớm | P4 |
| 7 | DR-1: rsync chọn lọc ra đĩa ngoài | Cần `artifact.role`/`retention_status` nên phải sau #4 | Sau P4 |
| 8 | Diễn tập restore Neon (PITR + branch) | `TARGET_ARCHITECTURE.md:193` yêu cầu rollback đã diễn tập | Trước Phase B |
| 9 | SPIKE-BLOB-PY | **Chỉ khi** T1–T5 kích hoạt | Có điều kiện |
