# Phase 4.1 — Điểm dừng pháp y (forensic checkpoint)

**Trạng thái: cài đặt DỞ DANG, KHÔNG an toàn để đóng băng. Chưa commit gì.**

Ngày: 2026-08-05 · Commit nền: `c4d5321` (commit của bạn, không liên quan Phase 4)
· 68 lỗi TypeScript · Không chạy test/lô nào sau điểm dừng này.

---

## 1. Kho hiện vật

| Tệp | Nội dung |
|---|---|
| `handoff/phase4_tracked.patch` | 252 KB — diff của các tệp ĐÃ theo dõi |
| `handoff/phase4_untracked.tar.gz` | 116 KB — toàn bộ tệp Phase 4 CHƯA theo dõi |
| `handoff/PHASE4_1_HANDOFF.md` | tài liệu này |

Phần lớn công việc Phase 4 nằm ở tệp **chưa theo dõi**, nên `git diff` một mình
KHÔNG đủ để khôi phục. Phải dùng cả hai hiện vật.

---

## 2. Phân loại từng thay đổi

### ✅ Đã kiểm chứng — giữ lại

| Tệp | Ghi chú |
|---|---|
| `drizzle/0016..0022*.sql` + snapshot + `_journal.json` | 23 migration, đã kiểm trực tiếp trên CẢ HAI database |
| `src/db/schema/cursor-analysis.ts` | lineage phức hợp, trigger, cột nguồn gốc |
| `src/lib/cursor/exec.ts` | sandbox, allowlist môi trường, dọn cây tiến trình, timeout — **không đụng tới ở 4.1** |
| `src/db/run-cursor.ts` | CLI, `--successes/--max-attempts`, INDEX.json, xoá artifact cũ |
| `verify_schema.mjs`, `verify_phase4.mjs`, `attempt_table.mjs` | công cụ kiểm chứng, chạy được |
| `tests/integration/cursor-persistence.test.ts` | 28 test, xanh trước 4.1 |
| `tests/unit/cursor-exec.test.ts` | 23 test, xanh |
| `creator_specs/PHASE4_*.md` | tài liệu thiết kế + ranh giới tin cậy |

### 🟡 Dở dang — cần hoàn thiện

| Tệp | Tình trạng |
|---|---|
| `src/lib/cursor/schema.ts` | schema 2.1 XONG (`sourceRef`, bỏ `text`, `LEGACY=['1.0','2.0']`) |
| `src/lib/cursor/source-ref.ts` | **MỚI, hoàn chỉnh, chưa có test** — resolver + `enumerateUnits` + `findDuplicateItemIds` |
| `src/lib/cursor/validate.ts` | R/U đã thay vào; **S-rules vẫn đọc `mc.text` (đã bị bỏ)** → 26 lỗi |
| `src/lib/cursor/run.ts` | drift đã theo danh tính chuẩn tắc + nội dung ô; chưa có bên gọi truyền `rootText`/`repairedText` |
| `tests/unit/cursor-validate.test.ts` | 42 lỗi — fixture còn dùng hình dạng claim 2.0 |
| `tests/unit/cursor-baseline.test.ts` | dùng `FULL` có `text`/`sourceSection`/`sourceId` — cần đổi sang `sourceRef` |

### 🔴 Tái dựng — **đã đối chiếu độc lập, KHÔNG còn "không nguồn tin cậy"**

Xem mục 4.

### ⛔ Không an toàn để giữ

Không có tệp nào cần xoá. `prompt.ts` vẫn ở bản 2.0.0 (chưa viết 3.0.0) — đây là
**thiếu**, không phải sai; nó vẫn nhất quán với schema 2.0 cũ nên đừng dùng lẫn
với schema 2.1.

---

## 3. Sự cố: xoá nhầm bảy schema

**Chuyện gì xảy ra.** Một lệnh thay chuỗi trong `schema.ts` dùng hai mốc:
`"MỘT phát biểu liên quan tới chỉ số…"` → `"export const cursorOutputSchema"`.
Bảy schema mục nằm GIỮA hai mốc đó và bị xoá cùng.

**Vì sao không phát hiện ngay.** Lệnh thay không có assert. Chỉ lộ ra khi
typecheck nhảy lên 244 lỗi.

**Vì sao khôi phục từ git thất bại.** Toàn bộ Phase 4 CHƯA commit, nên
`git show HEAD:apps/hub/src/lib/cursor/schema.ts` báo lỗi. Do dùng `&&`, bước
python phía sau **không chạy** và không in ra lỗi nào — một thất bại IM LẶNG,
đúng loại lỗi mà cả Phase 4 này chống lại.

**Bài học vận hành:** mọi lệnh sửa tệp bằng script phải `assert` mốc tồn tại; và
tệp chưa commit thì git KHÔNG phải mạng an toàn.

---

## 4. Bảy schema tái dựng — và bằng chứng đối chiếu

Tái dựng bằng tay: `keyFindingSchema`, `hypothesisSchema`, `recommendationSchema`,
`experimentSchema`, `manualReviewTargetSchema`, `dataRequestSchema`,
`selfCheckSchema` (95 dòng, hiện nằm trong `schema.ts`).

**Nguồn đối chiếu ĐỘC LẬP và có trước lúc xoá:** vòng rà soát Codex về tương ứng
prompt↔schema (log `codex_prompt.log`) đã liệt kê đầy đủ mọi ràng buộc chuỗi/mảng
của schema **trước** khi sự cố xảy ra.

**Kết quả đối chiếu tự động: 26/26 KHỚP, không sai lệch.**

| Trường | Codex ghi trước khi xoá | Bản tái dựng |
|---|---|---|
| `analysisSummary.overallAssessment` | 20–2000 | ✅ |
| `analysisSummary.confidenceRationale` | 10–1000 | ✅ |
| `analysisSummary.primaryConstraint` | 5–600 | ✅ |
| `keyFindings[].statement` | 10–600 | ✅ |
| `keyFindings[].supportingReasoning` | 10–1200 | ✅ |
| `keyFindings[].limitations[]` | ≤400 | ✅ |
| `hypotheses[].statement` | 10–600 | ✅ |
| `hypotheses[].missingEvidence[]` | ≤300 | ✅ |
| `hypotheses[].validationMethod` | 10–800 | ✅ |
| `recommendations[].action` | 10–600 | ✅ |
| `recommendations[].rationale` | 10–1200 | ✅ |
| `recommendations[].risks[]` | ≤400 | ✅ |
| `recommendations[].successMetric` | 3–400 | ✅ |
| `experiments[].change` | 10–600 | ✅ |
| `experiments[].baseline` | 3–400 | ✅ |
| `experiments[].successMetrics[]` | ≤300 | ✅ |
| `experiments[].sampleLimitations[]` | ≤400 | ✅ |
| `experiments[].stopConditions[]` | ≤300 | ✅ |
| `experiments[].interpretationRisks[]` | ≤400 | ✅ |
| `manualReviewTargets[].targetId` | 1–120 | ✅ |
| `manualReviewTargets[].reason` | 5–500 | ✅ |
| `manualReviewTargets[].reviewQuestions[]` | ≤300 | ✅ |
| `dataRequests[].metricOrArtifact` | 2–200 | ✅ |
| `dataRequests[].reason` | 5–500 | ✅ |
| `dataRequests[].decisionUnlocked` | 5–500 | ✅ |
| `explicitNonConclusions[]` | ≤500 | ✅ |

Ngoài ra khớp với các nguồn khác: `minimumWindowDays` 1–365, trần mảng
(`keyFindings` 1–10, `hypotheses` ≤8, `recommendations` ≤10, `experiments` ≤5,
`stopConditions` 1–5, `interpretationRisks` 1–6, `reviewQuestions` 1–6), và các
regex id `F-/H-/R-/E-` — tất cả đều xuất hiện trong log Codex và trong test.

**Vẫn CHƯA đối chiếu được:** `.default([])` trên các trường tuỳ chọn và
`z.literal('UNVERIFIED')` của `hypotheses[].status`. Cả hai đều có test bao phủ
(`mọi giả thuyết đều UNVERIFIED`), nhưng nên soát mắt một lượt khi tiếp tục.

**Kết luận phân loại:** ✅ *tái dựng có đối chiếu độc lập* — KHÔNG phải "không có
nguồn tin cậy". Vẫn nên review bằng mắt trước khi đóng băng.

---

## 5. 68 lỗi TypeScript — theo NGUYÊN NHÂN GỐC

| # | Nguyên nhân | Lỗi | Cách sửa |
|---|---|---|---|
| 1 | **S-rules vẫn đọc `mc.text`** (19 chỗ) | 26 ở `validate.ts` | đổi sang văn bản ĐÃ PHÂN GIẢI qua `resolvedByClaim` |
| 2 | **Thiếu import** từ `source-ref.ts` | 4 | thêm `resolveSourceRef`, `enumerateUnits`, `findDuplicateItemIds`, `ResolvedUnit` |
| 3 | **`clausesOf` bị xoá cùng khối cũ** | 1 | khôi phục (tách mệnh đề: `,` `;` `:` `và` `nhưng` `còn`) |
| 4 | **`scanTargets` không còn tồn tại** | 1 | phần quét chỉ số bịa phải chạy trên `enumerateUnits()` |
| 5 | **Fixture test dùng hình dạng 2.0** | 42 ở `cursor-validate.test.ts` | đổi `text`/`sourceSection`/`sourceId` → `sourceRef` |

Không có lỗi nào ở `exec.ts`, `run-cursor.ts`, `cursor-analysis.ts`, migration,
hay test tích hợp — các vùng đó không bị 4.1 đụng tới.

---

## 6. Thiết kế ĐÃ HOÀN THÀNH — giữ nguyên

### Schema 2.1
`sourceRef {section, itemId, field, ordinal}` thay cho `text`. Version `2.1`,
`LEGACY_SCHEMA_VERSIONS = ['1.0','2.0']`.

### `source-ref.ts` (mới, hoàn chỉnh)
`resolveSourceRef` · `enumerateUnits` · `findDuplicateItemIds` · `ResolvedUnit`
với `canonical = section|itemId|field` (KHÔNG gồm ordinal).
Fail-closed: `AMBIGUOUS_DUPLICATE_TEXT` khi một field mảng có hai phần tử trùng
nội dung — không phân giải bừa.

### Quy tắc R/U (đã viết trong `validate.ts`)
R1–R5 phân giải · U1 một-ô-một-phát-biểu (validator ĐẾM, không nhờ prompt) ·
U2 một ô một claim · U3 ô nhạy cảm phải được khai · U4 claim mồ côi.

### Drift theo danh tính chuẩn tắc (đã viết trong `run.ts`)
- `section|itemId|field` **không được đổi**, kể cả khi ô mới trùng nội dung —
  chặn việc đổi CHỦ SỞ HỮU kết luận.
- Chỉ `ordinal` (dữ liệu vị trí suy ra) được phép đổi sau khi đảo thứ tự.
- Nội dung ô được trỏ tới không được đổi; số trong ô không được đổi.

### Ranh giới tin cậy (đã ghi đúng)
- **Tất định:** phân giải tham chiếu, tính duy nhất `itemId`.
- **Heuristic ngôn ngữ:** đếm mệnh đề nhạy cảm, quy tắc "một ô một phát biểu".
- Không được gọi cả tầng R/U là tất định.

---

## 7. Việc còn lại — theo THỨ TỰ PHỤ THUỘC

1. Khôi phục `clausesOf`; thêm import từ `source-ref.ts` *(gỡ nguyên nhân 2,3)*
2. Viết lại S1–S8 trên văn bản đã phân giải; thay `scanTargets` bằng
   `enumerateUnits()` *(gỡ nguyên nhân 1,4)*
3. Nối `rootText`/`repairedText` vào `detectSemanticDrift` trong vòng lặp của `run.ts`
4. Viết `prompt.ts` 3.0.0: đặc tả `sourceRef`, `section`/`field` hợp lệ sinh từ
   schema, quy tắc một-ô-một-phát-biểu kèm ví dụ tách ô
5. Cập nhật fixture test sang `sourceRef` *(gỡ nguyên nhân 5)*
6. Thêm ma trận đối kháng 37 ca (mục 6 của `PHASE4_1_DESIGN_V2.md`), **bổ sung**:
   - văn bản TRÙNG HỆT ở hai item khác nhau → drift phải chặn khi đổi ref
   - văn bản trùng hệt ở hai section khác nhau
   - đổi quyền sở hữu (finding → recommendation) với nội dung y hệt
   - trùng nội dung trong cùng field → `AMBIGUOUS_DUPLICATE_TEXT`
7. Chứng minh round-trip JSONB 2.1 + CHECK 0022 trên **cả hai** database
8. Chạy full test + typecheck
9. Rà soát Codex phạm vi hẹp (mục 7 của `PHASE4_1_DESIGN_V2.md`)
10. **Một** lần thăm dò `hinh_su`; tiêu chí đóng băng: **0 lỗi R/U**
11. Đóng băng mới → lô chính thức 3 kênh × 3 mẫu × trần 6

---

## 8. Mốc so sánh — GIỮ NGUYÊN, không trộn mẫu

| Lô | hinh_su | phat_giao | phong_thuy |
|---|---|---|---|
| Batch 5 (lexical) | 3/4 | **2/6** | 3/3 |
| Cấu trúc 2.0 | 0/6 | 0/6 | 0/2 (bị ngắt) |

`phat_giao` = **2/6** theo chính sách mốc ngữ nghĩa (lần sửa sau JSON hỏng không
tính là mẫu hợp lệ). Giữ nguyên kết luận: **không an toàn cho vận hành tự động.**

Loại khỏi mọi mẫu số: 3 lô vô hiệu, 3 lần thăm dò.

---

## 9. Rủi ro còn tồn tại

1. Bảy schema tái dựng — đã đối chiếu 26/26 nhưng `.default()` và literal
   `UNVERIFIED` chưa có nguồn đối chiếu độc lập.
2. Ngữ nghĩa bằng chứng: chỉ kiểm cấu trúc, không kiểm nội dung có ủng hộ kết
   luận (`evidence_support_unverified`, HIGH, chặn).
3. Nguồn gốc là bản ghi có kỷ luật, **không phải attestation**.
4. Chưa đo được mô hình tuân thủ `sourceRef` tốt đến đâu — chưa có lần chạy thật nào.
5. Ràng buộc "một ô một phát biểu" là ràng buộc THẬT lên cách hành văn, chưa
   kiểm chứng thực tế.

---

`CHECKPOINT CREATED — implementation incomplete and unsafe to freeze`
