# Phase 4.1 — Thiết kế LƯỢT KHAI BÁO (declaration pass). Chưa sửa mã.

Trạng thái: **đề xuất**. Không đóng băng, không chạy lô chính thức dưới hợp đồng
2.1 một lượt. Bốn lần thăm dò và mọi lô trước giữ nguyên vai trò **bằng chứng
lịch sử bị loại khỏi mọi mẫu số**.

---

## 0. Vì sao phải đổi kiến trúc, không phải chỉnh thêm heuristic

Bốn lần thăm dò `hinh_su` trên prompt 3.0.0, cùng gói `8d8dd513b1ff`:

| Thăm dò | R | U1 | U2 | U3 | U4 | U tổng | S | số claim mô hình viết |
|---|---|---|---|---|---|---|---|---|
| #1 | 0 | 3 | 0 | 2 | 4 | 9 | 38 | 26 |
| #2 | 0 | 1 | 1 | 17 | 0 | 19 | 5 | 5 |
| #3 | 0 | 2 | 0 | 0 | 0 | **2** | 24 | ~17 |
| #4 | 0 | **0** | 1 | 13 | 0 | 14 | 11 | ~13 |

Hai điều đọc được, và chỉ đọc được vì có bốn điểm chứ không phải một:

1. **`R = 0` ở cả bốn lần.** Cơ chế `sourceRef` không hỏng. Mô hình trỏ đúng ô
   trên mọi claim nó viết, qua bốn lần chạy độc lập. Đây là phần 2.1 làm được.
2. **`U` dao động 2 → 19 và nghịch chiều với số claim mô hình viết.** Viết nhiều
   claim thì ăn lỗi tình thái; viết ít claim thì ăn lỗi thiếu khai báo. Không có
   điểm cân bằng nào trong bốn lần.

Nguyên nhân không nằm ở một quy tắc nào. Nó nằm ở chỗ **U3 giao cho mô hình một
việc SỔ SÁCH**: quét ~40 ô văn bản, tìm mọi ô có nhắc một trong bốn từ khoá, và
gắn đúng một claim cho từng ô — trong khi `enumerateUnits(output)` **tính được
chính xác tập ô đó một cách tất định**.

Đây là vi phạm chính nguyên tắc của tầng này: *thuật toán tính sự kiện, LLM suy
luận trên sự kiện*. Ta đang bắt LLM tính một tập hợp mà thuật toán đã có sẵn, rồi
phạt nó khi đếm sót.

---

## 1. Kiến trúc

```
   ┌─────────────────────────┐
   │ LƯỢT 1 — PHÂN TÍCH      │  execution role = ANALYSIS
   │ output: VĂN XUÔI        │  KHÔNG có metricClaims
   └───────────┬─────────────┘
               │  đóng băng + băm
               ▼
   ┌─────────────────────────┐
   │ ỨNG DỤNG (tất định)     │  enumerateUnits(output)
   │ -> TẬP NGHĨA VỤ KHAI    │  KHÔNG gọi LLM
   └───────────┬─────────────┘
               │  đóng băng + băm
               ▼
   ┌─────────────────────────┐
   │ LƯỢT 2 — KHAI BÁO       │  execution role = DECLARATION
   │ chỉ điền TRƯỜNG NGỮ NGHĨA│  không thêm/bớt/đổi mục tiêu
   └───────────┬─────────────┘
               ▼
        KIỂM ĐỊNH HỢP NHẤT -> KẾT QUẢ
```

### 1.1 R và U KHÔNG biến mất — chúng CHUYỂN CHỖ

Bản đầu của tài liệu này viết "biến mất theo cấu trúc". Cách nói đó SAI và nguy
hiểm: nó mời người đọc tin rằng không còn gì phải kiểm. Sự thật là bảo đảm được
DI CHUYỂN — từ chỗ "mô hình phải làm đúng" sang chỗ "ứng dụng và database không
cho phép làm sai". Bảo đảm chỉ có giá trị bằng đúng phép cưỡng chế đứng sau nó,
nên mỗi dòng dưới đây phải chỉ ra được phép cưỡng chế ấy nằm ở đâu.

| Quy tắc 2.1 | Chuyển thành | Cưỡng chế ở đâu |
|---|---|---|
| **R1–R5** phân giải | ứng dụng SINH `sourceRef`, không nhận từ mô hình | bộ sinh nghĩa vụ + `.strict()` lượt 2 (không có chỗ để viết) + **O-INV-2** |
| **U2** hai claim một ô | một nghĩa vụ ↔ một khai báo | **O-INV-3** (`declaration_duplicate`) + unique theo `id` |
| **U3** ô chưa khai | tập nghĩa vụ CHÍNH LÀ tập ô nhạy cảm | **O-INV-3** (`declaration_missing_obligation`) |
| **U4** claim mồ côi | không có claim ngoài tập nghĩa vụ | **O-INV-3** (`declaration_unknown_obligation`) |
| **U1** một ô một phát biểu | quy tắc VĂN XUÔI ở LƯỢT 1 | kiểm định chặng ANALYSIS |
| **S1–S8** | giữ nguyên, chạy trên văn bản đã đóng băng | kiểm định chặng DECLARATION |

### 1.2 Bốn bất biến BẮT BUỘC của tầng nghĩa vụ

Đây là phần thay cho nhóm R/U cũ. Không có bốn cái này thì kiến trúc mới YẾU HƠN
2.1, vì 2.1 ít nhất còn phân giải lại tham chiếu ở mỗi lần kiểm.

**O-INV-1 — tập nghĩa vụ thuộc ĐÚNG lần phân tích đó.**
- Ứng dụng: `obligationSet.analysisHash` phải bằng băm payload lượt 1 đang dùng;
  lệch → `obligation_analysis_mismatch` (BLOCKER).
- Database: `cursor_claim_obligation.analysis_execution_id` UNIQUE, và khoá ngoại
  PHỨC HỢP `(analysis_execution_id, workspace_id, analysis_run_id)` về
  `llm_execution` — không thể gắn tập nghĩa vụ của lần chạy này vào lần chạy khác
  dù mọi id đều tồn tại.
- Database: bản kê của lượt DECLARATION phải khai `analysis_execution_id` trỏ
  đúng lượt phân tích, và trigger đối chiếu `obligation_set_hash` của bản kê với
  hàng `cursor_claim_obligation` tương ứng.

**O-INV-2 — `sourceRef` và băm văn bản khớp bản phân tích ĐÃ ĐÓNG BĂNG.**
- Ở chặng COMPOSITE, ứng dụng **phân giải lại** từng `sourceRef` của từng nghĩa
  vụ trên payload lượt 1 và so `sha256(resolvedText)` với `resolvedHash` đã lưu.
- Lệch → `obligation_source_drift` (BLOCKER). Đây là phép kiểm giữ lại toàn bộ
  sức mạnh của R1–R5: nếu ai đó (worker cũ, ghi thẳng DB, lỗi ghép) đổi văn xuôi
  giữa hai lượt, băm không khớp và kết quả bị chặn.
- KHÔNG được bỏ phép kiểm này với lý do "ứng dụng tự sinh nên chắc đúng". Chính
  vì tự sinh nên không còn ai kiểm nó ngoài chỗ này.

**O-INV-3 — DANH TÍNH nghĩa vụ: không thiếu, không thừa, không trùng, không đảo.**
- So theo TẬP `id`, không theo thứ tự mảng:
  `set(declarations.id) === set(obligations.id)`, và `declarations.length ===
  obligations.length` (bắt trùng).
- Đảo thứ tự mảng `declarations` KHÔNG phải vi phạm (ghép theo `id`), nhưng đảo
  DANH TÍNH thì có: một `id` khai vào nghĩa vụ khác bị bắt vì `sourceRef` không
  do mô hình viết — nó không có cách nào "đổi mục tiêu".
- Bốn mã lỗi riêng, không gộp: `declaration_missing_obligation`,
  `declaration_unknown_obligation`, `declaration_duplicate`,
  `declaration_count_mismatch`.

**O-INV-4 — tập nghĩa vụ BẤT BIẾN kể từ khi lượt khai báo bắt đầu.**
- Database: trigger `cursor_obligation_immutable` chặn UPDATE và DELETE trên
  `cursor_claim_obligation`, giống `IMMUTABLE_CURSOR_RESULT` hiện có.
- Ứng dụng: tập nghĩa vụ được ghi TRƯỚC khi tạo execution lượt 2, và lượt 2 phải
  khai lại `obligationSetHash`; lệch → `obligation_set_drift`.
- Hệ quả có chủ ý: muốn đổi tập nghĩa vụ thì phải chạy lại LƯỢT 1. Không có
  đường nào sửa nghĩa vụ tại chỗ.

Nói ngắn: mô hình không còn cơ hội làm sai nhóm R/U, nhưng **hệ thống thì có** —
và bốn bất biến trên là chỗ bắt điều đó.

---

## 2. Thay đổi schema CHÍNH XÁC

### 2.1 `src/lib/cursor/schema.ts`

```ts
export const CURSOR_ANALYSIS_SCHEMA_VERSION    = '3.0'   // văn xuôi, lượt 1
export const CURSOR_DECLARATION_SCHEMA_VERSION = '3.0'   // khai báo, lượt 2
export const CURSOR_OUTPUT_SCHEMA_VERSION      = '3.0'   // hợp nhất, kết quả
export const LEGACY_SCHEMA_VERSIONS = ['1.0', '2.0', '2.1'] as const
```

**Lượt 1 — `cursorAnalysisSchema`.** Bằng đúng `cursorOutputSchema` hiện nay,
BỎ trường `metricClaims`. `selfCheck` giữ nguyên. `.strict()` giữ nguyên, nên
một output lượt 1 có `metricClaims` bị TỪ CHỐI — mô hình không được phép tự khai
sớm.

**Tập nghĩa vụ — `claimObligationSchema`.** Do ỨNG DỤNG sinh, không do mô hình:

```ts
export const claimObligationSchema = z.object({
  id:            idPattern('MC'),        // sinh tuần tự: MC-001, MC-002, …
  sourceRef:     sourceRefSchema,        // canonical, từ enumerateUnits
  canonical:     z.string().max(200),    // section|itemId|field#ordinal
  pointer:       z.string().max(200),    // chỉ để chẩn đoán
  resolvedText:  z.string().max(2000),   // VĂN BẢN THẬT tại ô
  resolvedHash:  z.string().length(64),  // sha256(resolvedText đã chuẩn hoá)
  mentionedMetrics: z.array(z.enum(SENSITIVE_METRICS)).min(1),
  requiredStatus:   z.enum(['REQUIRED']).default('REQUIRED'),
  /** Ô do CẤU TRÚC quy định tình thái -> tập assertionStatus hợp lệ đã bị thu hẹp. */
  allowedAssertionStatuses: z.array(assertionStatusEnum).min(1),
}).strict()

export const claimObligationSetSchema = z.object({
  schemaVersion: z.literal(CURSOR_ANALYSIS_SCHEMA_VERSION),
  analysisHash:  z.string().length(64),  // neo vào ĐÚNG bản phân tích
  obligations:   z.array(claimObligationSchema).max(120),
}).strict()
```

`allowedAssertionStatuses` là nơi `STRUCTURAL_SPEECH_ACT` hiện tại chuyển vào:
ứng dụng tính sẵn tập trạng thái hợp lệ cho ô nhãn, nên mô hình không còn phải
đoán, và `ASSERTED` ở ô nhãn trở thành bất khả biểu diễn.

**Lượt 2 — `declarationSchema`.** Mô hình CHỈ điền bảy trường ngữ nghĩa:

```ts
export const claimDeclarationSchema = z.object({
  id: idPattern('MC'),                   // PHẢI trùng id nghĩa vụ
  subjectMetric: z.enum(CLAIM_METRICS),
  relatedMetric: z.enum(CLAIM_METRICS).default('NONE'),
  claimType: claimTypeEnum,
  judgement: judgementEnum,
  assertionStatus: assertionStatusEnum,
  evidenceIds: z.array(z.string().max(120)).max(12).default([]),
  requiresMissingnessDisclosure: z.boolean().default(false),
}).strict()

export const declarationOutputSchema = z.object({
  schemaVersion: z.literal(CURSOR_DECLARATION_SCHEMA_VERSION),
  obligationSetHash: z.string().length(64),
  declarations: z.array(claimDeclarationSchema).max(120),
}).strict()
```

`.strict()` ở đây làm hầu hết việc: không có chỗ nào để viết `sourceRef`, `text`,
hay một claim mới. Điều 4 của đề bài ("không thêm, bớt, đảo, nhân bản, đổi mục
tiêu") được cưỡng chế bởi HÌNH DẠNG chứ không bởi một phép kiểm chạy sau.

**Kết quả hợp nhất — `cursorOutputSchema` 3.0.** Ứng dụng ghép: văn xuôi lượt 1 +
`metricClaims` dựng từ (nghĩa vụ ⋈ khai báo) theo `id`. Hình dạng `metricClaim`
giữ NGUYÊN như 2.1, nên mọi quy tắc S và mọi báo cáo phía sau không phải viết lại.

---

## 3. Mô hình thực thi và lưu trữ

### 3.1 Vai của execution

`cursor_execution_manifest` thêm `execution_role`:

```
ANALYSIS     — lượt 1, sinh văn xuôi
DECLARATION  — lượt 2, sinh khai báo
REPAIR       — sửa lỗi KỸ THUẬT của một trong hai lượt trên
```

**Đây là chỗ va chạm cụ thể với mã hiện có, và phải xử lý tường minh.** Trigger
`cursor_repair_version_immutable` (0020) đang áp cho MỌI execution có
`parent_execution_id`, và nó đòi cha–con cùng `prompt_version`. Lượt khai báo
dùng một prompt KHÁC, nên nếu nối bằng `parent_execution_id` thì trigger sẽ từ
chối — đúng như nó phải làm, vì nó được viết cho chuỗi SỬA LỖI.

Giải pháp: hai quan hệ khác nhau, hai cột khác nhau.

| Cột | Ý nghĩa | Ai kiểm |
|---|---|---|
| `parent_execution_id` | lần thử TRƯỚC trong cùng một lượt | 0020, chỉ khi `execution_role = 'REPAIR'` |
| `analysis_execution_id` | lượt PHÂN TÍCH mà lượt khai báo này phục vụ | trigger mới 0023 |

Trigger 0020 được sửa để trả `NEW` ngay khi `execution_role <> 'REPAIR'`. Điều 5
của đề bài ("D1 còn nguyên cho repair") vì thế đúng theo nghĩa đen: quy tắc cũ
không bị nới, chỉ được nói rõ nó áp cho cái gì.

### 3.2 Bảng mới

```sql
cursor_claim_obligation
  id                  uuid PK
  workspace_id        uuid NOT NULL
  analysis_run_id     uuid NOT NULL
  channel_id          uuid NOT NULL
  request_id          uuid NOT NULL
  analysis_execution_id uuid NOT NULL     -- lượt 1 sinh ra nó
  obligation_set_hash text NOT NULL       -- băm TOÀN BỘ tập, tất định
  analysis_hash       text NOT NULL       -- băm payload lượt 1
  obligations         jsonb NOT NULL      -- claimObligationSetSchema
  generator_version   text NOT NULL       -- phiên bản bộ sinh nghĩa vụ
  created_at          timestamptz NOT NULL DEFAULT now()
```

Bất biến: `UNIQUE (analysis_execution_id)` — một lượt phân tích sinh đúng một tập
nghĩa vụ. Trigger chặn UPDATE/DELETE như `IMMUTABLE_CURSOR_RESULT` hiện có.

### 3.3 Kiểm định hai chặng

`analysis_validation` thêm `stage` (`ANALYSIS` | `DECLARATION` | `COMPOSITE`).
Unique index đổi từ `(llm_execution_id)` sang `(llm_execution_id, stage)`.

| Chặng | Quy tắc chạy |
|---|---|
| ANALYSIS | schema, id duy nhất, neo bằng chứng, **U1**, ngôn ngữ nhân quả trên văn xuôi, chỉ số bịa, chất lượng (P0, tin cậy) |
| DECLARATION | **S1–S8**, tình thái theo cấu trúc, bằng chứng ↔ subjectMetric, tổ hợp mâu thuẫn |
| COMPOSITE | selfCheck đối chiếu, đếm tổng, `passed` cuối cùng |

Chỉ chặng COMPOSITE mới cho phép ghi `cursor_analysis_result`. Trigger 0022 được
mở rộng: kết quả đòi dòng kiểm định ĐẠT ở **cả ba** chặng, không phải một.

#### 3.3.1 Ngữ nghĩa CHÍNH XÁC của ba chặng

| | ANALYSIS | DECLARATION | COMPOSITE |
|---|---|---|---|
| Gắn vào execution | lượt 1 | lượt 2 | **lượt 2** |
| Đầu vào | payload lượt 1 | payload lượt 2 + tập nghĩa vụ | cả hai payload + nghĩa vụ + gói |
| Quy tắc | schema lượt 1, id trùng, neo bằng chứng, **U1**, nhân quả, chỉ số bịa, chất lượng | **chỉ hợp đồng CỤC BỘ**: schema lượt 2, O-INV-3 (danh tính), O-INV-4 (băm tập), `assertionStatus` ∈ tập hợp lệ của ô | O-INV-1, O-INV-2, **S1–S8**, tình thái theo cấu trúc, bằng chứng↔subject, selfCheck, đếm tổng |
| Cho phép ghi kết quả | vai ANALYSIS (văn xuôi bất biến) | không | **vai COMPOSITE, và chỉ nó** |

**S1–S8 là quy tắc của chặng COMPOSITE, KHÔNG phải của chặng DECLARATION.**
Bản đầu tài liệu này xếp chúng vào DECLARATION; khi cài đặt thì rõ là không
được, và lý do có tính nguyên tắc chứ không phải tiện lợi:

* S1–S8 phán xét một `metricClaim` HOÀN CHỈNH — cần bảy trường ngữ nghĩa GHÉP
  với `sourceRef` và với văn bản ô đã phân giải. Lượt khai báo chỉ sinh ra một
  nửa; nửa kia nằm ở tập nghĩa vụ. Phép ghép đó CHÍNH LÀ bước hợp nhất.
* S5 còn cần `dataCoverage` của GÓI (chỉ số nào phủ 0%), thứ không có mặt trong
  hợp đồng lượt 2 và cố ý không được gửi vào prompt lượt 2.
* Đặt chúng ở DECLARATION sẽ buộc chặng đó phải tự ghép claim — tức làm đúng
  việc của chặng hợp nhất, dưới một cái tên khác.

Vì vậy chặng DECLARATION chỉ kiểm **hợp đồng CỤC BỘ của chính nó**: bản khai có
đúng hình dạng không, có trả lời đúng tập nghĩa vụ đã đóng băng không (băm), có
đủ/không thừa/không trùng không (danh tính), và trạng thái khai có nằm trong tập
hợp lệ mà cấu trúc đã quy định cho ô đó không. Tất cả đều là phép kiểm BẤT BIẾN
và DANH TÍNH — không phép nào cần biết ô nói gì.

Hệ quả vận hành, ghi rõ để không ai đọc nhầm: **chặng DECLARATION xanh KHÔNG có
nghĩa là bản khai đúng ngữ nghĩa.** Nó chỉ có nghĩa là bản khai đầy đủ và neo
đúng chỗ. Phán quyết về tính đúng nằm ở COMPOSITE.

**Vì sao COMPOSITE gắn vào execution LƯỢT 2, không phải một execution thứ ba.**
Nó không gọi LLM; tạo thêm một `llm_execution` cho một việc thuần tính toán sẽ
làm hỏng ý nghĩa của bảng đó (mọi hàng ở đó là một lần gọi mô hình) và làm lệch
`execution_sequence`. Chặng COMPOSITE là PHÁN QUYẾT về cặp (lượt 1, lượt 2), và
lượt 2 là mắt xích cuối nên nó mang phán quyết ấy.

**Đúng MỘT phán quyết COMPOSITE được phép cấp phép cho một kết quả chính thức.**
Cưỡng chế ở hai tầng:
- unique index `(llm_execution_id, stage)` → một execution không thể có hai dòng
  COMPOSITE;
- trigger `cursor_result_semantic_lineage` mở rộng: trước khi cho INSERT vào
  `cursor_analysis_result` với `result_role = 'COMPOSITE'`, đòi tồn tại đúng một
  dòng `analysis_validation` chặng COMPOSITE, `passed = true`, thuộc CHÍNH
  execution đó; và đòi dòng ANALYSIS `passed = true` của
  `manifest.analysis_execution_id`; và đòi dòng DECLARATION `passed = true` của
  chính execution đó.

**Idempotency.** Ghi kiểm định là *upsert theo `(llm_execution_id, stage)`*, không
phải insert mù: chạy lại bộ kiểm định trên cùng dữ liệu phải cho cùng kết quả và
không sinh hàng thứ hai. Nhưng dòng kiểm định vẫn BẤT BIẾN sau khi đã có kết quả
gắn vào — trigger `IMMUTABLE_VALIDATION` hiện có giữ nguyên vai trò đó. Hai điều
này không mâu thuẫn: upsert chỉ hợp lệ khi chưa có `cursor_analysis_result` nào
trỏ tới execution ấy.

**Chặng hỏng thì sao.**

| Chặng hỏng | Hành vi |
|---|---|
| ANALYSIS hỏng KỸ THUẬT | sửa trong ngân sách lượt 1; KHÔNG sinh nghĩa vụ, KHÔNG chạy lượt 2 |
| ANALYSIS hỏng NỘI DUNG (U1, nhân quả, chỉ số bịa) | dừng hẳn; không retry; lưu lại lần thử ở trạng thái thất bại |
| Sinh nghĩa vụ hỏng | LỖI LẬP TRÌNH, không phải lỗi mô hình → `systemFailure`, không gọi lượt 2 |
| DECLARATION hỏng KỸ THUẬT | sửa trong ngân sách RIÊNG của lượt 2; **không chạy lại lượt 1** |
| COMPOSITE hỏng — `SYSTEM_OR_INTEGRITY` | dừng hẳn, KHÔNG retry, điều tra tay |
| COMPOSITE hỏng — `DECLARATION_SEMANTIC` | **sửa được**, trong ngân sách RIÊNG của lượt 2 |

### 3.3.2 HAI LOẠI thất bại COMPOSITE — và vì sao phải tách

Bản đầu tài liệu này viết "COMPOSITE hỏng LUÔN là lỗi hệ thống". Sai, và sai theo
cách đắt: nó gộp hai thứ có nguyên nhân, chủ thể và cách xử lý ngược nhau.

| | `SYSTEM_OR_INTEGRITY` | `DECLARATION_SEMANTIC` |
|---|---|---|
| Gồm | thiếu hàng đã lưu; lineage/vai/băm lệch; văn xuôi hoặc tập nghĩa vụ bị đổi; ghép/ghi hỏng; validator ném ngoại lệ | S1–S8; phân cực, tình thái, chiều phán xét, chủ ngữ; nhân quả; P0; bằng chứng, kể cả `evidence_support_unverified` |
| Ai gây ra | **mã hoặc dữ liệu của ta** | **bản khai của mô hình** |
| Thử lại | **KHÔNG** | **CÓ**, trong ngân sách lượt 2 |
| Đếm vào lô | KHÔNG phải "mô hình thất bại" | LÀ một lần thử độ ổn định thất bại |
| Ghi ở đâu | `systemFailure`, `status = FAILED` | phán quyết COMPOSITE `passed = false`, gắn ĐÚNG execution khai báo |

**Vì sao `DECLARATION_SEMANTIC` ĐƯỢC phép thử lại, trong khi hợp đồng một lượt
cấm retry mọi lỗi ngữ nghĩa.** Ở một lượt, retry lỗi ngữ nghĩa nghĩa là chạy lại
tới khi mô hình nói điều ta muốn nghe — vì mô hình có thể đổi cả KẾT LUẬN. Ở hai
lượt, **văn xuôi đã đóng băng**: lần khai lại không chạm được vào một chữ nào của
bản phân tích, chỉ dán nhãn lại cho những kết luận đã cố định. Không gian nhãn
hợp lệ cho một ô do chính chữ trong ô đó quy định.

**Rủi ro còn lại, ghi rõ:** mô hình vẫn có thể dò dần tới một bộ nhãn lọt lưới S.
Ba thứ giới hạn điều đó, và không thứ nào loại bỏ nó: trần lần thử; mọi lần thử
hỏng đều được LƯU và đọc được; và một lần "đạt ở lần thứ ba" nhìn khác hẳn một
lần "đạt ngay" trong bảng lần thử.

### 3.3.3 Phán quyết: BẰNG CHỨNG khác QUYỀN

Trigger `cursor_single_composite_verdict` của 0027 chặn MỌI phán quyết COMPOSITE
thứ hai. Chặt quá và chặt sai chỗ: nó khiến một bản khai hỏng ngữ nghĩa không ghi
lại được, nên cũng không sửa được — lần thử thứ hai bị từ chối trước khi ai kịp
đọc lần thứ nhất hỏng vì sao. 0028 tách hai khái niệm:

* **Bằng chứng** — mọi phán quyết COMPOSITE **KHÔNG ĐẠT** được ghi thoải mái.
  Đây chính là yêu cầu "giữ lại mọi lần thử" của cả Phase 4.
* **Quyền** — đúng MỘT phán quyết **ĐẠT** cho mỗi lượt phân tích, và đúng MỘT kết
  quả chính thức. Hai phán quyết đạt là hai kết quả cạnh tranh cho cùng một bài
  phân tích, tức "chạy lại tới khi được số đẹp".

Cưỡng chế bằng HAI hàng rào độc lập: trigger trên `analysis_validation` (chỉ xét
`passed = true`) và trigger trên `cursor_analysis_result` (chỉ xét
`result_role = 'COMPOSITE'`). Hàng rào thứ hai suy ra được từ hàng rào thứ nhất —
nhưng "suy ra được" không phải "được cưỡng chế", và nếu ai đó về sau nới cái thứ
nhất thì tầng kết quả mất bảo vệ mà không có gì báo.

Không có trạng thái "một nửa đạt". Nếu lượt 2 cạn ngân sách hoặc COMPOSITE hỏng
thì cả lần chạy là THẤT BẠI; văn xuôi lượt 1 vẫn được lưu ở dòng `ANALYSIS` làm
bằng chứng nhưng KHÔNG được trình bày là kết quả đạt, và `INDEX.json` không liệt
kê tệp nào cho kênh đó.

### 3.4 Lưu trữ payload

`cursor_analysis_result` thêm `result_role` (`ANALYSIS` | `COMPOSITE`):

- một dòng `ANALYSIS` giữ **văn xuôi bất biến** + `payload_hash = analysis_hash`;
- một dòng `COMPOSITE` giữ **kết quả hợp nhất** (văn xuôi + metricClaims).

Giữ cả hai, không chỉ bản hợp nhất: nếu chỉ lưu bản hợp nhất thì không còn cách
nào chứng minh lượt khai báo đã không sửa một chữ nào của văn xuôi.

---

## 4. Nguồn gốc bổ sung

Thêm vào bản kê, `_meta`, và `INDEX.json`:

| Trường | Ở đâu | Vì sao |
|---|---|---|
| `executionRole` | manifest, `_meta` | phân biệt hai lượt khi đọc lại |
| `analysisExecutionId` | manifest (DECLARATION), `_meta` | nối lượt 2 về lượt 1 |
| `analysisHash` | manifest, result, `_meta`, INDEX | chứng minh khai báo gắn đúng văn xuôi |
| `obligationSetHash` | manifest, obligation, `_meta`, INDEX | chứng minh khai báo gắn đúng tập nghĩa vụ |
| `obligationCount` | manifest, `_meta` | đọc nhanh, đối chiếu với số khai báo |
| `obligationGeneratorVersion` | manifest, INDEX | bộ sinh nghĩa vụ là MÃ; đổi nó là đổi ngữ nghĩa |
| `declarationPromptVersion` | manifest, INDEX | prompt lượt 2 có vòng đời riêng |
| `declarationPromptSourceHash` | manifest | như trên |

Băm `obligationSetHash` tính trên `stableStringify` của tập nghĩa vụ đã sắp xếp
theo `id` — tất định, và trùng nghĩa với `packageHash` hiện có.

### 4.0 MA TRẬN PHỦ — yêu cầu đến từ ma trận, không đến từ người gọi

`checkProvenanceAgreement` nhận một danh sách trường do CALLER truyền vào. Nó so
đúng những gì được hỏi — nên caller quên một trường thì nhận về "đồng thuận:
đúng", không phải vì mọi bề mặt khớp nhau mà vì không ai hỏi. Lỗi này đã xảy ra
thật ở vòng G7 đầu tiên và chỉ lộ ra vì một phép kiểm khác tình cờ kêu.

`PROVENANCE_MATRIX` (trong `src/lib/cursor/provenance.ts`) khai báo, cho MỖI bề
mặt: trường **bắt buộc**, trường **không áp dụng**, và các quan hệ **bằng nhau**
giữa những bề mặt cùng mang một trường. `checkProvenanceCoverage` đọc yêu cầu từ
ma trận. Người gọi không thu hẹp được phạm vi; quên là hỏng.

MƯỜI BỐN bề mặt được khai báo, MƯỜI HAI trong số đó có mặt ở mỗi lần chạy đạt
(hai bề mặt sửa lỗi chỉ xuất hiện khi có lần thử lại):

| Bề mặt | Vai trò | Không áp dụng — vì sao |
|---|---|---|
| `request` | gói + prompt đã gửi | băm nghĩa vụ: ra đời sau nó |
| `analysisExecution` / `analysisRepairExecution` | lượt 1 và chuỗi sửa của nó | `analysisExecutionId`: lượt 1 không trỏ về chính mình (CHECK 0023) |
| `obligationSet` | tập nghĩa vụ tất định | mọi thứ thuộc lượt 2: hàng này ra đời TRƯỚC lượt khai báo |
| `declarationExecution` / `declarationRepairExecution` | lượt 2 và chuỗi sửa | — (mang đủ cả sáu hợp đồng) |
| `analysisValidation` / `declarationValidation` / `compositeValidation` | ba phán quyết | băm hợp đồng: dòng kiểm định là PHÁN QUYẾT, không phải kho băm |
| `resultRow` | hiện vật chính thức | `obligationCount`: đã có ở tập nghĩa vụ |
| `storedMeta` | `_meta` trong payload đã lưu | — |
| `artifactMeta` | `_meta` trong tệp artifact | — |
| `indexJson` | khối nguồn gốc của lô | — |
| `attemptTable` | một dòng bảng lần thử | môi trường: thuộc về lô, không thuộc về từng dòng |

Phân biệt **"không áp dụng"** với **"quên"** là phần mang giá trị: nếu đòi một
bề mặt mang trường nó không thể có, thì "thiếu" mất hết ý nghĩa và phép kiểm
không còn phát hiện được lệch thật.

`INDEX.json` và `_meta` của artifact được dựng bởi `runIdentity` /
`buildArtifactMeta` / `buildIndexProvenance` trong `src/lib/cursor/identity.ts`,
CÙNG hàm mà bộ test gọi. Trước đó chúng được dựng ngay tại chỗ ghi tệp, nên test
chỉ có hai lựa chọn: chạy cả CLI, hoặc chép lại logic — và bản chép lại thì xanh
kể cả khi bản thật thiếu trường.

### 4.2 CHỐNG MỒ CÔI đã có sẵn — `0029` là một bước thừa, `0030` gỡ nó

Yêu cầu "phán quyết ĐẠT và kết quả chính thức không mồ côi được" đã được thoả
mãn TỪ TRƯỚC, bởi `cursor_result_immutability` (IMMUTABLE_CURSOR_RESULT) và
`analysis_validation_immutability` (IMMUTABLE_VALIDATION). Cả hai chặn MỌI
UPDATE và DELETE trên hai bảng đó — rộng hơn hẳn phạm vi cần thiết.

`0029` thêm hai trigger làm đúng việc đó lần nữa, vì khi viết nó tôi chỉ tìm
trigger xoá trong `0026`–`0028` rồi kết luận "chưa có gì bảo vệ". Bộ test mới là
thứ phát hiện: nó đòi thông điệp lỗi của `0029` và nhận về thông điệp của trigger
cũ. `0030` gỡ hai trigger thừa.

Vì sao gỡ chứ không để đó cho chắc: hai trigger cùng canh một bảng thì trigger
chạy trước quyết định THÔNG ĐIỆP LỖI, và ở đây trigger thừa lại thắng về thứ tự
tên. Người đọc log sẽ thấy thông báo của một ràng buộc phụ và đi tìm sai chỗ.

`0029` vẫn nằm trong nhật ký, có chủ ý: một migration đã áp lên database thật thì
lịch sử phải cho thấy nó từng tồn tại và đã được gỡ.

**Hệ quả cho ngữ nghĩa thử lại:** phán quyết COMPOSITE **không đạt** cũng KHÔNG
xoá được. Điều này mạnh hơn ý định ban đầu và đúng hơn nó — một phán quyết trượt
là bằng chứng về một lần thử. Dọn dữ liệu test dùng `TRUNCATE`, vốn không kích
hoạt trigger hàng, nên không phải nới lỏng gì.

### 4.3 BẢNG LẦN THỬ: so phiên bản TRONG TỪNG VAI, không so gộp

Kiến trúc hai lượt làm hỏng phép kiểm "lô trộn phiên bản" cũ trong
`attempt_table.mjs`. Nó gom `schema_version/prompt_version` của MỌI execution vào
một tập rồi kêu nếu tập có quá một phần tử. Từ nay lượt PHÂN TÍCH chạy prompt
`3.0.0` còn lượt KHAI BÁO chạy prompt khai báo `1.0.0`, nên tập gộp LUÔN có hai
phần tử và cảnh báo sẽ kêu ở MỌI lô đúng đắn. Một cảnh báo luôn kêu là một cảnh
báo không ai đọc — và đó là cách hỏng nguy hiểm nhất, vì nó vẫn trông như đang
bảo vệ.

Nay so ba tầng:

1. **Trong từng vai** — `ANALYSIS` và `DECLARATION` mỗi vai phải đồng nhất
   `schema/prompt`. Băm validator vẫn phải đồng nhất trên TOÀN lô, vì chỉ có một
   bộ kiểm định.
2. **Bốn hợp đồng của lượt khai báo** — `obligationGeneratorVersion`,
   `declarationPromptVersion`, `declarationPromptSourceHash`,
   `compositeValidatorVersion` đồng nhất trên toàn lô.
3. **Trong từng LẦN THỬ ỔN ĐỊNH** — nghiêm trọng hơn cả hai mức trên. Một lần thử
   là một lượt phân tích cùng mọi lượt khai báo phục vụ nó. Nếu hai lượt khai báo
   của CÙNG một bài phân tích neo vào hai `obligation_set_hash` khác nhau thì một
   trong hai đang khai cho một tập nghĩa vụ không còn tồn tại, và phán quyết
   "đạt" của nó vô nghĩa. Số lần thử bị trộn được in ra rõ ràng và làm hỏng cổng.

### 4.1 SÁU hợp đồng, SÁU phiên bản, SÁU băm — không gộp

Bài học của 2.1: một `schemaVersion` duy nhất che ba hợp đồng khác nhau, nên
không truy vấn được "lô này hỏng vì đổi prompt hay vì đổi validator". Kiến trúc
hai lượt có SÁU hợp đồng độc lập; mỗi cái phải phiên bản hoá và băm RIÊNG.

| # | Hợp đồng | Phiên bản | Băm | Đổi khi nào |
|---|---|---|---|---|
| 1 | schema PHÂN TÍCH | `ANALYSIS_SCHEMA_VERSION` | `analysisSchemaHash` | đổi hình dạng văn xuôi |
| 2 | prompt PHÂN TÍCH | `ANALYSIS_PROMPT_VERSION` | `analysisPromptSourceHash` | đổi chữ trong prompt lượt 1 |
| 3 | schema + BỘ SINH nghĩa vụ | `OBLIGATION_GENERATOR_VERSION` | `obligationGeneratorHash` | đổi `enumerateUnits`, quy tắc chọn ô nhạy cảm, hay `allowedAssertionStatuses` |
| 4 | schema KHAI BÁO | `DECLARATION_SCHEMA_VERSION` | `declarationSchemaHash` | đổi bảy trường ngữ nghĩa |
| 5 | prompt KHAI BÁO | `DECLARATION_PROMPT_VERSION` | `declarationPromptSourceHash` | đổi chữ trong prompt lượt 2 |
| 6 | validator HỢP NHẤT | `COMPOSITE_VALIDATOR_VERSION` | `compositeValidatorHash` | đổi bất kỳ quy tắc S/U/O nào |

Cộng thêm hai băm DỮ LIỆU (không phải mã):

| Băm | Trên cái gì | Vai trò |
|---|---|---|
| `analysisPayloadHash` | payload lượt 1 đã chuẩn hoá | neo O-INV-1, O-INV-2 |
| `obligationSetHash` | tập nghĩa vụ đã sắp theo `id` | neo O-INV-4 |

**Quy tắc bắt buộc:** `OBLIGATION_GENERATOR_VERSION` là một hợp đồng NGANG HÀNG
với schema, không phải chi tiết cài đặt. Bộ sinh nghĩa vụ quyết định ô nào phải
khai — tức nó quyết định NGỮ NGHĨA của tính đầy đủ. Đổi nó mà không tăng phiên
bản là đổi thước đo giữa chừng, đúng loại lỗi làm hỏng ba lô trước.

**Chuỗi retry:** trigger `cursor_repair_version_immutable` phải so CẢ SÁU, không
chỉ năm cột hiện nay. Một lần sửa lỗi đổi `obligationGeneratorHash` là đang sửa
một bài toán khác.

**Mặt bằng lô:** cả sáu phiên bản và hai băm dữ liệu phải có mặt ở `INDEX.json`
và `_meta`. Điều kiện đóng băng bao gồm "cả sáu khớp nhau giữa artifact và
database" — gọi là **đồng thuận nguồn gốc đầy đủ** ở mục 11.

**Ranh giới tin cậy không đổi:** đây vẫn là *bản ghi có kỷ luật*, không phải
attestation. Băm vẫn tính lúc nạp module. Thêm hai lượt không làm nó mạnh hơn về
mặt mật mã, chỉ làm nó KIỂM được nhiều bất biến hơn.

---

## 5. Trôi dạt và bất biến

Tách làm ba nhóm, đừng gộp:

**D-A (văn xuôi bất biến).** Sau khi lượt 1 đạt, `analysis_hash` đóng băng. Lượt
khai báo không nhận được chỗ nào để viết văn xuôi (schema lượt 2 không có trường
nào cho nó). Kiểm lại bằng cách so `analysis_hash` của kết quả hợp nhất với dòng
`ANALYSIS`.

**D-O (tập nghĩa vụ bất biến).** `obligationSetHash` đóng băng cùng lúc. Lượt 2
phải khai lại đúng băm đó trong `obligationSetHash` của nó; lệch là từ chối. Đây
là cách bắt trường hợp lượt 2 chạy trên một tập nghĩa vụ cũ.

**D-D (khai báo).** Áp cho SỬA LỖI KỸ THUẬT của lượt 2, tương ứng D1/D2 hiện nay:
tập `id` không đổi (mà nó không thể đổi, vì phải khớp nghĩa vụ), và bảy trường
ngữ nghĩa không đổi giữa các lần sửa. D3/D5 (văn bản ô, số trong ô) **không còn
cần thiết ở lượt 2** vì văn bản không nằm trong tầm với của lượt 2 — nhưng vẫn
giữ ở lượt 1 cho chuỗi sửa lỗi của lượt 1.

Bảng đối chiếu ba điều kiện từ chối:

| Vi phạm | Mã lỗi |
|---|---|
| số khai báo ≠ số nghĩa vụ | `declaration_count_mismatch` |
| id khai báo không có trong nghĩa vụ | `declaration_unknown_obligation` |
| nghĩa vụ không có khai báo | `declaration_missing_obligation` |
| id khai báo trùng | `declaration_duplicate` |
| `obligationSetHash` lệch | `obligation_set_drift` |
| `analysis_hash` lệch giữa hai dòng kết quả | `analysis_payload_drift` |

---

## 6. Ngữ nghĩa thử lại

Không đổi triết lý, chỉ nhân đôi phạm vi áp dụng:

- **Lượt 1** giữ nguyên `MAX_ATTEMPTS = 3` (1 + 2 sửa). Chỉ thất bại KỸ THUẬT mới
  được sửa. **U1 là thất bại NỘI DUNG** → không retry, đúng như hiện nay với
  `UNSUPPORTED_CLAIM`.
- **Lượt 2** có ngân sách RIÊNG, cũng 3. Thất bại kỹ thuật của lượt 2 (JSON hỏng,
  sai schema, thiếu trường) được sửa mà **không chạy lại lượt 1** — đây chính là
  khoản tiết kiệm lớn nhất của kiến trúc: hiện nay một lỗi khai báo bắt phải bỏ
  cả bài phân tích 100–235 giây.
- Thất bại NGỮ NGHĨA của lượt 2 (S1–S8) **không được retry**. Retry chúng là chạy
  lại tới khi mô hình khai điều ta muốn nghe.
- Nếu lượt 2 cạn ngân sách: cả lần chạy là THẤT BẠI. Không có "một nửa kết quả".
  Văn xuôi lượt 1 vẫn được lưu ở dòng `ANALYSIS` làm bằng chứng, KHÔNG được trình
  bày là kết quả đạt.

`llm_execution_iteration_bounds` hiện là `1..3`; hai lượt là hai execution riêng
nên mỗi lượt vẫn nằm trong trần đó. `execution_sequence` là duy nhất theo
`(analysis_run, provider)` nên hai lượt lấy hai số thứ tự — không va chạm.

---

## 7. Migration cần thiết

**Cạm bẫy đã gặp ở `0029`:** tạo tệp `drizzle/00NN_*.sql` là CHƯA ĐỦ. Drizzle chỉ
áp những gì có trong `drizzle/meta/_journal.json`; một tệp không đăng ký sẽ bị bỏ
qua **trong im lặng**, và `migrate()` in ra đúng dòng "không lỗi" y hệt lần thành
công. Lần đó nhật ký báo 29 dòng, trigger không tồn tại, và không có gì trong log
nói lên điều đó. Chỉ `pg_trigger` nói ra.

Quy tắc: sau mỗi lần áp, đọc `pg_proc.prosrc` và `pg_trigger` — không đọc log.
`verify_0028_0030.mjs` làm đúng việc này, và nó CHỈ ĐỌC nên chạy được cả trên MAIN.



Kế tiếp `0022`, journal hiện có 23 mục.

| # | Nội dung | Rủi ro |
|---|---|---|
| `0023_execution_role` | enum `cursor_execution_role`; cột `execution_role` NOT NULL DEFAULT `'ANALYSIS'` trên manifest; cột `analysis_execution_id` nullable + FK phức hợp về `(llm_execution, workspace, run)`; **sửa `cursor_repair_version_immutable` để chỉ áp cho `REPAIR`** | Thấp. Dữ liệu cũ mặc định `ANALYSIS`, trigger cũ vẫn áp cho các chuỗi repair cũ vì chúng có `parent_execution_id`. **Phải kiểm trực tiếp `pg_proc.prosrc`** sau khi áp — đây đúng là loại migration đã ba lần in "xong" mà chưa chạy. |
| `0024_claim_obligation` | bảng `cursor_claim_obligation` + FK phức hợp + `UNIQUE(analysis_execution_id)` + trigger bất biến | Thấp, bảng mới. |
| `0025_validation_stage` | enum `validation_stage`; cột `stage` NOT NULL DEFAULT `'COMPOSITE'`; đổi `analysis_validation_execution_key` thành `(llm_execution_id, stage)` | **CAO — xem 7.1.** Đổi unique index trên bảng CÓ DỮ LIỆU. |
| `0026_result_role_and_lineage` | cột `result_role`, `analysis_hash`, `obligation_set_hash` trên `cursor_analysis_result`; mở rộng `cursor_result_semantic_lineage` đòi ĐẠT ở cả ba chặng | **Trung bình.** Trigger siết hơn; dòng cũ không bị đụng vì trigger chỉ chạy khi INSERT. |

Cả bốn phải chạy trên **cả hai** database và được kiểm bằng
`information_schema` + `pg_proc.prosrc`, không tin log. `verify_schema.mjs` mở
rộng thêm bốn nhóm kiểm tương ứng.

### 7.1 `0025` là migration RỦI RO CAO — quy trình riêng

Đây là migration DUY NHẤT đụng vào một ràng buộc duy nhất trên bảng đã có dữ
liệu. Bỏ `analysis_validation_execution_key` rồi dựng lại theo
`(llm_execution_id, stage)` **nới lỏng** ràng buộc: trước đó một execution có tối
đa một dòng kiểm định, sau đó là ba. Nới ràng buộc trên dữ liệu sống là chỗ dễ để
lọt nhất, và một `DROP` thành công theo sau một `CREATE` thất bại sẽ để bảng
KHÔNG có ràng buộc nào — tệ hơn hẳn trạng thái ban đầu.

**Sáu bước bắt buộc, theo đúng thứ tự:**

1. **Truy vấn TIỀN KIỂM trùng lặp.** Trước khi đụng gì:
   ```sql
   SELECT llm_execution_id, count(*) FROM analysis_validation
    GROUP BY llm_execution_id HAVING count(*) > 1;
   ```
   Phải trả 0 hàng trên CẢ HAI database. Khác 0 → DỪNG, không chạy migration;
   dữ liệu đang vi phạm chính ràng buộc sắp bỏ, và phải hiểu vì sao trước đã.

2. **Migration CHẠY TRONG MỘT TRANSACTION.** `DROP CONSTRAINT` và `CREATE UNIQUE
   INDEX` nằm cùng một `BEGIN/COMMIT`. Drizzle chạy từng tệp trong transaction,
   nhưng phải kiểm chứng điều đó chứ không giả định — nếu tệp bị tách bởi
   `--> statement-breakpoint` thành nhiều transaction thì phải gộp lại. Không
   dùng `CREATE INDEX CONCURRENTLY` (nó không chạy được trong transaction).

   **KẾT QUẢ TIỀN KIỂM ĐÃ CHẠY (2026-08-05), qua `preflight_0025.mjs`:**

   | | MAIN | TEST |
   |---|---|---|
   | tổng dòng `analysis_validation` | 102 | 0 |
   | execution có >1 dòng | **0** | **0** |
   | có trong `pg_constraint` | **KHÔNG** | **KHÔNG** |
   | có trong `pg_indexes` | CÓ | CÓ |

   **Phát hiện quan trọng: `analysis_validation_execution_key` là một UNIQUE
   INDEX, KHÔNG phải một CONSTRAINT.** Vì vậy 0025 phải dùng `DROP INDEX`, không
   phải `DROP CONSTRAINT` — `DROP CONSTRAINT IF EXISTS` sẽ chạy "thành công" mà
   không gỡ gì, và bước 4 sẽ dựng index mới trong khi index cũ VẪN CÒN. Kết quả:
   một bảng có hai unique index, cái cũ tiếp tục chặn dòng thứ hai, và kiến trúc
   ba chặng hỏng ngay ở lần ghi đầu tiên — với một migration đã báo thành công.

   Đây đúng là lý do bước 3 phải soi CẢ HAI catalog thay vì chỉ một.

3. **Xác minh ĐÃ GỠ index cũ:**
   ```sql
   SELECT conname FROM pg_constraint WHERE conname = 'analysis_validation_execution_key';
   SELECT indexname FROM pg_indexes WHERE indexname = 'analysis_validation_execution_key';
   ```
   Cả hai phải trả 0 hàng. Kiểm cả `pg_constraint` lẫn `pg_indexes`: một unique
   index có thể tồn tại mà không có constraint tương ứng, và ngược lại.

4. **Xác minh ĐỊNH NGHĨA index mới trên CẢ HAI database:**
   ```sql
   SELECT indexdef FROM pg_indexes WHERE indexname = 'analysis_validation_execution_stage_key';
   ```
   Chuỗi trả về phải chứa cả `llm_execution_id` và `stage`, và phải là `UNIQUE`.
   So khớp chuỗi, không chỉ đếm số hàng — một index đúng tên mà sai cột là đúng
   loại lỗi tài liệu này tồn tại để chống.

5. **Test PHỦ ĐỊNH: ghi trùng chặng phải bị từ chối.** Trong test tích hợp, chèn
   hai dòng cùng `(llm_execution_id, stage)` và đòi lỗi. Không có ca này thì index
   mới có thể là non-unique mà không ai biết.

6. **Tương thích TRUY VẤN ĐỘ ỔN ĐỊNH.** `cursor-stability.ts`, `attempt_table.mjs`
   và mọi truy vấn giả định "một execution ⇒ một dòng kiểm định" nay sẽ đếm gấp
   ba. Phải rà từng chỗ và thêm `WHERE stage = 'COMPOSITE'`. Đây là rủi ro ÂM
   THẦM nguy hiểm nhất của 0025: không có gì báo lỗi, chỉ có các con số lô đo bị
   nhân ba.

**Rollback:** nếu bước 3 hoặc 4 thất bại trên bất kỳ database nào, dựng lại
`analysis_validation_execution_key` NGAY và dừng toàn bộ việc triển khai. Không
đi tiếp với một bảng đang không có ràng buộc duy nhất nào.

### 7.2 Cổng MIGRATION chạy TÁCH RIÊNG — và không được retry ngầm

`tests/integration/migrations.test.ts` dựng lại TOÀN BỘ lược đồ từ database rỗng.
Nó phải chạy MỘT MÌNH:

```
npm run test:gate         # toàn bộ suite TRỪ migration
npm run test:migrations   # cổng migration, chạy riêng
```

Hai lý do, và cả hai đều là lý do đúng đắn chứ không phải né tránh:

1. Nó DROP và dựng lại lược đồ trên chính database mà mọi test tích hợp khác
   đang dùng. Chạy chung là để một test xoá nền dưới chân test khác.
2. Ở một lần chạy đầy đủ (~820 giây) nó từng gãy vì Neon đóng WebSocket giữa
   chừng — lỗi TẦNG KẾT NỐI, không phải lỗi lược đồ. Chạy riêng, nó đi hết trong
   ~108 giây.

**KHÔNG được bọc nó bằng retry tự động.** Một migration hỏng thật và một kết nối
rớt đều hiện ra là "test đỏ"; thêm retry sẽ nuốt cái thứ nhất để chữa cái thứ
hai, và đó đúng là kiểu che lỗi mà cả Phase 4 chống lại. Đỏ thì đọc lỗi: lỗi
`information_schema`/`pg_*` là lược đồ hỏng — dừng; lỗi `Connection terminated`
là hạ tầng — chạy lại TAY, một lần, và ghi lại rằng đã chạy lại.

---

## 8. Ma trận test đối kháng

### Sinh nghĩa vụ (tất định — nhóm O)

1. tập nghĩa vụ = đúng tập ô có nhắc chỉ số nhạy cảm theo `enumerateUnits`
2. cùng một payload → cùng `obligationSetHash` (tất định, chạy 100 lần)
3. đảo thứ tự `keyFindings` → tập nghĩa vụ ĐỔI `sourceRef` nhưng KHÔNG đổi tập
   `resolvedText`; băm phải đổi và điều đó là ĐÚNG
4. ô có 2 mệnh đề nhạy cảm → chặn ở LƯỢT 1 (U1), không bao giờ tới sinh nghĩa vụ
5. output không có ô nhạy cảm nào → tập nghĩa vụ RỖNG → lượt 2 bị BỎ QUA, không
   phải gọi LLM với danh sách rỗng
6. `resolvedHash` khớp `sha256` của chính `resolvedText`
7. ô nhãn → `allowedAssertionStatuses` không chứa `ASSERTED`

### Ràng buộc lượt khai báo (nhóm C)

8. thiếu một khai báo → `declaration_missing_obligation`
9. thừa một khai báo → `declaration_unknown_obligation`
10. trùng id → `declaration_duplicate`
11. đảo thứ tự mảng `declarations` → KHÔNG phải trôi dạt (ghép theo id)
12. khai `sourceRef` trong declaration → `.strict()` từ chối cả payload
13. khai văn bản trong declaration → như trên
14. `obligationSetHash` sai → `obligation_set_drift`
15. lượt 2 chạy trên tập nghĩa vụ của một lần phân tích KHÁC → chặn bởi 14 + FK

### Ngữ nghĩa (nhóm S — giữ nguyên, chạy lại toàn bộ)

16–23. S1–S8 nguyên vẹn, nay chạy trên `resolvedText` của nghĩa vụ
24. `assertionStatus` ngoài `allowedAssertionStatuses` → chặn
25. `ASSERTED` ở ô nhãn → bất khả (24 đã chặn), kiểm bằng test

### Bất biến và nguồn gốc (nhóm P)

26. văn xuôi dòng `ANALYSIS` ≠ văn xuôi trong dòng `COMPOSITE` → `analysis_payload_drift`
27. `cursor_claim_obligation` không UPDATE được
28. không ghi được `COMPOSITE` khi thiếu kiểm định chặng `ANALYSIS`
29. không ghi được `COMPOSITE` khi thiếu kiểm định chặng `DECLARATION`
30. `execution_role = DECLARATION` mà thiếu `analysis_execution_id` → chặn
31. lượt khai báo trỏ sang lần phân tích khác → chặn bởi FK phức hợp
32. trigger 0020 KHÔNG còn chặn lượt DECLARATION dùng prompt khác
33. trigger 0020 VẪN chặn chuỗi REPAIR trộn phiên bản (hồi quy của 0020)

### Tương thích (nhóm V)

34. payload 2.1 → `UNSUPPORTED_SCHEMA_VERSION`
35. payload 2.0 / 1.0 → như trên
36. round-trip JSONB của tập nghĩa vụ trên **cả hai** database
37. CHECK payload↔cột vẫn đúng cho `result_role` cả hai giá trị

### Tính chất

38. không tổ hợp khai báo hợp-lệ-schema nào đi qua toàn bộ S
39. mọi ô nhạy cảm trong 517 ô thật đã lưu đều sinh được nghĩa vụ khai được

---

## 9. Chi phí và timeout

Số đo thật từ bốn lần thăm dò: lượt phân tích 99–235 giây, prompt 61–64 KB,
stdout 22–40 KB.

| | Hiện nay (2.1) | Đề xuất |
|---|---|---|
| Số lần gọi LLM / lần chạy đạt | 1 | 2 |
| Prompt lượt 1 | ~64 KB | ~58 KB (bỏ phần đặc tả claim) |
| Prompt lượt 2 | — | ~25–45 KB (văn xuôi đã đóng băng + bảng nghĩa vụ) |
| Thời gian / lần chạy đạt | 100–235 s | **160–350 s** (ước tính lượt 2 bằng ~60% lượt 1) |
| Timeout mỗi execution | 600 s | 600 s, KHÔNG đổi |
| Chi phí một lỗi khai báo | chạy lại CẢ bài phân tích | chỉ chạy lại lượt 2 |

**Hai con số ở trên là ƯỚC TÍNH CHƯA ĐO, và phải được đối xử như vậy.**

Bản đầu của tài liệu này viết "gần như chắc chắn là tiết kiệm ròng" và đề xuất
trần 300 s cho lượt 2. Cả hai đều là suy đoán từ 0 lần chạy lượt 2. Ghi lại ở đây
vì đó đúng là kiểu tuyên bố mạnh hơn bằng chứng mà tài liệu ranh giới tin cậy
tồn tại để chặn.

| Điều chưa biết | Vì sao không suy ra được |
|---|---|
| Lượt 2 chạy bao lâu | Chưa có lần nào. "Bằng ~60% lượt 1" là phỏng đoán từ kích thước prompt, mà thời gian của lượt 1 dao động 99–235 s trên CÙNG một gói — tức phương sai lớn hơn hiệu ứng đang phỏng đoán |
| Có tiết kiệm ròng không | Phụ thuộc tỉ lệ hỏng ở lượt 2, mà tỉ lệ đó chưa đo |
| Trần 300 s có đủ không | Trần đặt quá thấp sẽ biến một lượt 2 chậm thành `CLI_TIMEOUT` và tiêu một lần thử — tự tạo ra thất bại |

**Quy tắc cho tới khi có số đo:**
- Lượt 2 chạy với `DEFAULT_TIMEOUT_MS = 600_000`, GIỐNG lượt 1. Không siết trước.
- Lần thăm dò phải GHI LẠI: thời gian lượt 1, thời gian lượt 2, số nghĩa vụ, kích
  thước prompt lượt 2, kích thước stdout lượt 2.
- Trần lượt 2 chỉ được ĐÓNG BĂNG SAU khi có số đo đó, và phải đặt theo quan sát
  (đề xuất: p95 quan sát được × 3), không theo trực giác.
- Báo cáo chi phí của lô chính thức phải nêu con số ĐO ĐƯỢC, không nêu lại ước
  tính này.

---

## 10. So sánh với hai phương án còn lại

| | Lượt khai báo | U3 → HIGH-có-rà-soát | Schema 2.2 khai inline |
|---|---|---|---|
| Công sức | 4 migration, 2 prompt, ~600 dòng | ~1 dòng | schema + prompt + validator viết lại phần lớn |
| U3 | biến mất theo cấu trúc | **còn nguyên, chỉ thôi chặn** | biến mất theo cấu trúc |
| U2, U4, R1–R5 | biến mất theo cấu trúc | còn nguyên | U2/U4 biến mất; R vẫn do mô hình viết |
| Rủi ro chính | bề mặt nguồn gốc rộng thêm; 4 migration | **kết quả "ĐẠT" có phát biểu chưa khai** | mô hình phải vừa viết văn vừa khai — tải nhận thức TĂNG, đúng thứ đã hỏng |
| Chi phí chạy | +60–90% khi đạt, giảm khi hỏng | 0 | ~0 |
| Ảnh hưởng tới thứ lô đo | giữ nguyên ý nghĩa | **đổi ý nghĩa**: lô không còn đo được tính đầy đủ | giữ nguyên |
| Đảo ngược được không | có — hai lượt là hai execution, bỏ lượt 2 là về 2.1 | có | khó: đổi hình dạng mọi trường văn bản |

**U3 → HIGH-có-rà-soát** nhỏ hơn thật, nhưng nó không giải quyết vấn đề — nó
tuyên bố vấn đề không còn là vấn đề. Lô chính thức sinh ra để trả lời câu "tầng
này đã đủ tin để vận hành tự động chưa"; hạ U3 xuống mức khuyến cáo khiến chính
câu hỏi đó không đo được nữa. Đây là dạng thành công giả mà cả Phase 4 chống lại.

**Schema 2.2 inline** giải quyết đúng gốc nhưng đi ngược bằng chứng đã có: bốn
lần thăm dò cho thấy mô hình càng phải vừa viết vừa khai thì càng lệch. Inline
làm việc đó nặng hơn, không nhẹ đi. Nó cũng biến mọi trường văn bản thành đối
tượng, tức viết lại `enumerateUnits`, `resolveSourceRef`, toàn bộ prompt và phần
lớn 515 test — với một hợp đồng chưa từng chạy thật lần nào.

---

## 11. Khuyến nghị

**Có — lượt khai báo là bước tiếp theo AN TOÀN NHỎ NHẤT.** Ba lý do, theo thứ tự
sức nặng:

1. **Nó lấy đi khỏi mô hình đúng phần việc mô hình đã chứng minh là làm không
   được, và không lấy đi phần nó làm được.** `R = 0` qua bốn lần chạy nói rằng
   suy luận trên một ô cụ thể thì mô hình ổn; `U` dao động 2–19 nói rằng sổ sách
   thì không. Kiến trúc mới cắt đúng theo đường đó.
2. **Nó biến quy tắc thành bất khả vi phạm thay vì kiểm chặt hơn.** R1–R5, U2,
   U3, U4 không còn là phép kiểm có thể sai — chúng không còn biểu diễn được.
   Đây là kiểu sửa duy nhất không sinh ra một heuristic mới để cãi nhau.
3. **Nó đảo ngược được.** Hai lượt là hai execution riêng; bỏ lượt 2 và gộp lại
   là quay về 2.1. Không có bước nào phá dữ liệu cũ.

**Nhưng không nên bắt đầu bằng cách viết mã.** Đề nghị thứ tự sau, mỗi bước có
cổng riêng:

| Cổng | Việc | Điều kiện qua |
|---|---|---|
| G1 | schema + vai execution | tsc 0, test schema xanh |
| G2 | bộ sinh nghĩa vụ + băm bất biến | test nhóm O xanh, tất định qua 100 lần |
| G3 | lưu trữ + migration 0023–0030 | `verify_schema.mjs` cả hai DB; **quy trình 7.1 cho 0025** |
| G4 | execution lượt khai báo | test vòng lặp, không gọi LLM thật |
| G5 | kiểm định theo chặng + phán quyết hợp nhất | O-INV-1..4 có test riêng |
| — | **cổng migration TÁCH RIÊNG** | `npm run test:migrations`, chạy MỘT MÌNH |
| G6 | quy tắc retry và trôi dạt | test nhóm D |
| G7 | nguồn gốc trên MỌI bề mặt | **ma trận phủ (4.0)** không thiếu/không lạ/không lệch trên 12 bề mặt |
| G8 | test đối kháng + kiểm DB trực tiếp | toàn bộ suite; kiểm `information_schema`/`pg_proc` |
| G9 | rà soát Codex phạm vi hẹp **bắt buộc** | sửa hết BLOCKER/HIGH |
| G10 | **MỘT** lần thăm dò `hinh_su` | ghi đủ số đo thời gian/kích thước |
| G11 | đóng băng | `R=0`, `U=0`, **và đồng thuận nguồn gốc đầy đủ** |
| G12 | lô chính thức | trần **3 mẫu đạt / 6 lần thử** GIỮ NGUYÊN |

**Đồng thuận nguồn gốc đầy đủ** (điều kiện của G11) nghĩa là `checkProvenanceCoverage`
trả về `ok` với cả bốn danh sách rỗng — `missing`, `unexpected`, `mismatches`,
`absentSurfaces` — trên toàn bộ 12 bề mặt của lần chạy. Nói riêng: cả sáu phiên bản
hợp đồng và hai băm dữ liệu ở mục 4.1 phải KHỚP TỪNG KÝ TỰ giữa ba nơi — hàng
database (`cursor_execution_manifest`, `cursor_claim_obligation`,
`cursor_analysis_result`), `_meta` trong tệp artifact, và `INDEX.json`. Lệch một
trường là không đóng băng, kể cả khi `R=0` và `U=0`.

### Kế hoạch thăm dò và lô chính thức

- **Thăm dò:** đúng một lần trên `hinh_su`, sau bước 6. Tiêu chí đi tiếp: `R = 0`
  và `U = 0`. Với kiến trúc mới, `U = 0` gần như là hệ quả cấu trúc — nếu nó vẫn
  khác 0, đó là bằng chứng bộ sinh nghĩa vụ sai, và phải dừng để xem lại thiết
  kế chứ không chỉnh heuristic.
- Lỗi S mức thấp ở lần thăm dò là CHẤP NHẬN ĐƯỢC. Lô chính thức mới là phép đo.
- **Đóng băng:** 5 băm mã nguồn + băm prompt lượt 2 + `obligationGeneratorVersion`
  + lockfile + commit + dirty-diff + mtime + realpath + số migration (27) + số test.
- **Lô chính thức:** 3 kênh × 3 mẫu đạt × trần 6 lần thử, một bộ hash duy nhất,
  không nới trần, không chạy lại để lấy kết quả đẹp.

### Mẫu số — giữ nguyên, không trộn

Loại khỏi MỌI mẫu số: 3 lô vô hiệu trước đó, **4 lần thăm dò của prompt 3.0.0**,
và mọi lần chạy dưới hợp đồng 2.1 một lượt. Chúng là bằng chứng CHẨN ĐOÁN, không
phải mẫu đo.

Mốc so sánh giữ nguyên, không trộn mẫu:

| Lô | hinh_su | phat_giao | phong_thuy |
|---|---|---|---|
| Batch 5 (lexical) | 3/4 | **2/6** | 3/3 |
| Cấu trúc 2.0 | 0/6 | 0/6 | 0/2 |

`phat_giao` = 2/6 giữ nguyên kết luận: **không an toàn cho vận hành tự động** trừ
khi lô mới có bằng chứng ngược lại rõ ràng.

---

## 11.5 RÀ SOÁT ĐỐI KHÁNG G8 — 9 khiếm khuyết, và vì sao chúng đi lọt

Bốn lượt Codex độc lập (vòng chạy hai lượt · bộ sinh nghĩa vụ + hợp nhất ·
nguồn gốc · migration) tìm ra **1 BLOCKER, 7 HIGH, 1 MEDIUM**. Tất cả đã được
sửa và có test hồi quy. Điểm chung của chúng đáng ghi lại:

**Chúng nằm ngoài phần KIỂM ĐỊNH NGỮ NGHĨA (S1–S8), nhưng KHÔNG nằm ngoài đường
ra quyết định.** Phân biệt này quan trọng và tôi đã nói sai một lần: D1 nằm
CHÍNH GIỮA đường CẤP PHÉP CHÍNH THỨC — nó quyết định một hiện vật có trở thành
kết quả chính thức hay không, và nó cho phép HAI hiện vật cùng làm điều đó. Nói
"không cái nào ở trong đường ra quyết định" là sai: đúng hơn phải nói chúng nằm
ngoài phần kiểm ngữ nghĩa, ở lớp CẤP PHÉP, lớp ĐẾM và lớp GHI ARTIFACT — những
chỗ mà một bộ test tuần tự, chạy qua đường ứng dụng chuẩn, không bao giờ đi tới.

Một cổng ngữ nghĩa hoàn hảo không cứu được điều đó: S1–S8 có thể phán quyết đúng
tuyệt đối cho từng bản khai, mà hệ thống vẫn cấp phép hai kết quả cạnh tranh cho
cùng một bài phân tích.

| # | Mức | Khiếm khuyết | Xử lý |
|---|---|---|---|
| D1 | BLOCKER | Hai giao dịch đồng thời cùng ghi phán quyết ĐẠT: trigger 0028 "SELECT rồi INSERT", ảnh chụp không thấy hàng chưa commit của bên kia | 0031 lấy `pg_advisory_xact_lock` theo lượt phân tích TRƯỚC khi đọc; test hai kết nối thật |
| A1 | HIGH | Bảng lần thử đếm cả lượt khai báo vào mẫu số, và lấy tử số từ `status='SUCCEEDED'` thay vì từ hiện vật chính thức — một lô KHÔNG có kết quả nào vẫn hiện "ĐỦ 3 MẪU" | tách `attempt_accounting.mjs`, 7 test |
| A2 | HIGH | Execution khai báo không bao giờ được chốt `SUCCEEDED`, nên truy vấn ổn định trả RỖNG với mọi lô và báo cáo thoát 0 | chốt trong `persistComposite`; nhánh thiếu dữ liệu nay thoát khác 0 |
| B1 | HIGH | Payload đã lưu không bao giờ được đối chiếu với băm của chính nó | tính lại băm trong `loadCompositeInputs`, ba phép neo mới |
| B2 | HIGH | `_meta` chỉ kiểm SỰ CÓ MẶT của phiên bản, không kiểm GIÁ TRỊ | ghim theo hằng số hợp đồng |
| C1 | HIGH | `{ _meta: ..., ...r.output }` — spread ghi đè `_meta` vừa dựng, artifact mất `resultId`, `compositeValidationId`, số lần thử | `buildArtifactFile` + test phép GHÉP |
| C2 | HIGH | Test `INDEX.json` không đọc `INDEX.json`; tally và danh tính nằm ngoài mọi phép kiểm | `buildIndexJson` + test |
| C3 | HIGH | `'unavailable'` được coi là giá trị nguồn gốc hợp lệ; git hỏng thì khai là cây SẠCH | sentinel tính là THIẾU; git hỏng nay khai `dirty: true` |
| D2–D4 | HIGH | Cấp phép được khi chưa có bản khai; `analysis_execution_id` trỏ được vào lượt KHAI BÁO; trần lần thử giới hạn GIÁ TRỊ cột chứ không giới hạn SỐ HÀNG | 0031: ba trigger mới |
| D5 | MEDIUM | Bộ xác minh không so băm migration ĐÃ ÁP với mã nguồn; bộ test có thể skip toàn bộ khi thiếu `TEST_DATABASE_URL` | so băm toàn nhật ký; `gate-preconditions.test.ts` làm ĐỎ cổng khi thiếu database |

### 0031 làm QUÁ TAY hai lần — và bộ test bắt được, không phải rà soát

Sửa BLOCKER xong, cổng đầy đủ ĐỎ: **15 ca hỏng trên 2 tệp**. Cả hai nguyên nhân
đều do 0031 chặn nhiều hơn phần nó được phép chặn, và cả hai đều là lỗi của tôi:

**(A) `COMPOSITE_VERDICT_WITHOUT_LINEAGE` chặn nhầm toàn bộ đường ghi CŨ.** Cột
`analysis_validation.stage` có DEFAULT `'COMPOSITE'`, nên MỌI lệnh ghi kiểm định
không nêu `stage` — tức toàn bộ mã Phase 1–3 — tạo ra một phán quyết COMPOSITE
trên execution không có lineage. 0028 xử lý đúng: không lineage thì không thuộc
phạm vi quy tắc. 0032 trả lại hành vi ấy.

**(B) Trigger mới che mất chẩn đoán cũ — ĐÚNG lỗi tôi vừa mắc ở 0029.** Postgres
chạy trigger theo thứ tự TÊN; `cursor_result_requires_declaration` đứng trước
`cursor_result_semantic_lineage`, nên "phân tích KHÔNG ĐẠT" bị báo thành "thiếu
bản khai". 0032 gộp phép kiểm vào CUỐI hàm lineage và bỏ trigger song song.

**(C) Và 0032 vẫn sai phạm vi.** Điều kiện `NEW.result_role = 'COMPOSITE'` bao
luôn kiến trúc MỘT LƯỢT, vốn ghi kết quả vai COMPOSITE trên execution vai
ANALYSIS và không bao giờ có bản khai. 0033 đổi điều kiện sang VAI EXECUTION.

Ba lần thu hẹp liên tiếp một ràng buộc vừa thêm. **Quy tắc rút ra: một ràng buộc
mới phải nêu rõ nó áp cho ĐƯỜNG CHẠY NÀO trước khi viết dòng SQL đầu tiên**, vì
cây mã còn mang cả kiến trúc cũ lẫn kiến trúc mới, và mặc định của một cột (ở
đây là `stage`) có thể lặng lẽ kéo đường cũ vào phạm vi quy tắc mới.

### Hai bài học ghi lại vì chúng sẽ lặp lại

**Một test tuần tự không nói gì về đồng thời.** D1 là hỏng nặng nhất và cũng là
hỏng vô hình nhất: mọi test cũ đều đúng, vì chúng chạy nối tiếp. Ràng buộc kiểu
"đọc rồi ghi" trong trigger CHỈ đúng khi có khoá.

**"Không kiểm được" phải khác "đã kiểm và đạt".** Ba trong chín khiếm khuyết
(A2, C2, D5) đều có cùng hình dạng: một phép kiểm trả về RỖNG rồi được đọc thành
ĐẠT. Đây là kiểu hỏng nguy hiểm nhất trong cả hệ thống, vì nó trông y hệt thành
công và không để lại dấu vết nào.

## 12. Điều thiết kế này KHÔNG giải quyết

Ghi ở đây để không ai đọc nhầm phạm vi:

- **Lỗi S vẫn còn.** Thăm dò #4 có 11 lỗi S. Lượt khai báo không làm mô hình khai
  đúng ngữ nghĩa hơn; nó chỉ đảm bảo mô hình khai ĐỦ. Tính đúng vẫn do S1–S8 chặn
  và vẫn là heuristic ngôn ngữ.
- **Ngữ nghĩa bằng chứng vẫn chỉ kiểm cấu trúc.** `evidence_support_unverified`
  vẫn là HIGH và vẫn chặn; không có gì ở đây chứng minh bằng chứng ỦNG HỘ kết luận.
- **Nguồn gốc vẫn không phải attestation.**
- **Giới hạn của bộ tách mệnh đề vẫn còn** (đồng vị không liên từ; "hay" nghĩa
  "thường xuyên"; hai phán xét nối bằng "và" trần). U1 chuyển sang lượt 1 nhưng
  vẫn là cùng heuristic đó.
- **Chưa đo được mô hình tuân thủ lượt 2 tốt đến đâu.** Chưa có lần chạy nào.
