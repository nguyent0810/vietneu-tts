# Phase 4.1 — Thiết kế chốt (schema 2.1). Chưa sửa mã.

## Ý tưởng cốt lõi

Bỏ `text` (bản sao). Claim TRỎ tới ô văn bản gốc bằng tham chiếu ỔN ĐỊNH, và bộ
kiểm định **phân giải** tham chiếu đó để lấy văn bản THẬT.

Hệ quả quan trọng nhất: mọi phép kiểm ngữ nghĩa (chủ ngữ, tình thái, phân cực,
chiều phán xét) từ nay chạy trên **văn bản gốc**, không phải trên một bản sao có
thể lệch. Cả lớp lỗi "bản sao khác bản gốc" biến mất theo định nghĩa.

### Vì sao KHÔNG dùng JSON Pointer thuần

`keyFindings[2].limitations[0]` gắn chặt vào vị trí mảng. Đảo thứ tự, chèn hay
xoá một phần tử là mọi tham chiếu phía sau trỏ sai — mà trỏ sai vẫn *phân giải
được*, nên lỗi im lặng. Tham chiếu phải neo vào **danh tính**, không neo vào vị trí.

---

## 1. Hình dạng schema 2.1

```ts
export const sourceRefSchema = z.object({
  section: claimSourceEnum,      // KEY_FINDING | HYPOTHESIS | RECOMMENDATION |
                                 // EXPERIMENT | MANUAL_REVIEW | DATA_REQUEST |
                                 // ANALYSIS_SUMMARY | NON_CONCLUSION
  itemId:  z.string().max(20),   // 'F-001' | 'H-001' | 'R-001' | 'E-001';
                                 // '' với ANALYSIS_SUMMARY và mảng cấp cao nhất
  field:   z.string().max(40),   // 'statement' | 'limitations' | 'rationale' | …
  ordinal: z.number().int().min(0).max(20).default(0),  // vị trí TRONG field mảng
}).strict()

export const metricClaimSchema = z.object({
  id: idPattern('MC'),
  claimType, subjectMetric, relatedMetric, judgement, assertionStatus,
  evidenceIds, requiresMissingnessDisclosure,
  sourceRef: sourceRefSchema,    // THAY cho `text`
  // `text` BỊ BỎ. `sourceSection`/`sourceId` cũ gộp vào sourceRef.
}).strict()
```

Suy ra được, chỉ dùng để CHẨN ĐOÁN (không phải nguồn sự thật):

```
derivedPointer = "keyFindings[idx(F-001)].limitations[0]"
resolvedText   = <văn bản thật tại ô đó>
resolvedHash   = sha256(resolvedText)   // do VALIDATOR tính, không do mô hình
```

`itemId` neo vào danh tính (F-001 vẫn là F-001 dù `keyFindings` đảo thứ tự).
`ordinal` chỉ định vị TRONG một field mảng của MỘT item — bề mặt vị trí nhỏ hơn
nhiều, và được xử lý bằng cách so **nội dung đã phân giải** chứ không so ordinal
(xem bất biến D3).

---

## 2. Bất biến và quy tắc fail-closed

### Phân giải (R)

| | Quy tắc | Vi phạm |
|---|---|---|
| R1 | `section` + `itemId` phải trỏ tới một item CÓ THẬT | `source_ref_unresolved` — BLOCKER |
| R2 | `field` phải tồn tại trên item đó và là chuỗi hoặc mảng chuỗi | `source_ref_unresolved` — BLOCKER |
| R3 | Với field mảng, `ordinal` phải nằm trong phạm vi | `source_ref_unresolved` — BLOCKER |
| R4 | `itemId` phải DUY NHẤT trong section của nó | `duplicate_source_item` — BLOCKER |
| R5 | Với `ANALYSIS_SUMMARY` và mảng cấp cao nhất, `itemId` phải rỗng | `source_ref_malformed` — BLOCKER |

### Một ô — một phát biểu (U) — **do validator cưỡng chế**

| | Quy tắc | Vi phạm |
|---|---|---|
| U1 | Văn bản đã phân giải chứa TỐI ĐA một mệnh đề nhắc chỉ số nhạy cảm | `multiple_assertions_in_source_unit` — BLOCKER |
| U2 | Mỗi ô nhạy cảm được trỏ tới bởi ĐÚNG một claim | `multiple_claims_for_source_unit` — BLOCKER |
| U3 | Mọi ô có nhắc chỉ số nhạy cảm phải có claim trỏ tới | `undeclared_sensitive_unit` — BLOCKER |
| U4 | Claim trỏ tới ô KHÔNG nhắc chỉ số nhạy cảm nào | `orphan_metric_claim` — BLOCKER |

U1 là điểm mấu chốt: đếm mệnh đề nhạy cảm trong văn bản đã phân giải bằng đúng bộ
tách mệnh đề hiện có. Không chỉ "yêu cầu trong prompt" — **chặn trong validator**.

### Ngữ nghĩa (S) — chạy trên VĂN BẢN ĐÃ PHÂN GIẢI

| | Quy tắc | Ghi chú |
|---|---|---|
| S1 | `subjectMetric` phải xuất hiện trong văn bản đã phân giải | như `subject_metric_not_in_text`, nay trên bản gốc |
| S2 | `assertionStatus` phải có dấu hiệu tình thái trong văn bản đã phân giải | như `modality_not_supported_by_text` |
| S3 | `judgement` không được ngược chiều văn bản | như `judgement_contradicts_text` |
| S4 | Phân cực mệnh đề chứa `subjectMetric` phải khớp `assertionStatus` | thay `claim_polarity_mismatch` — **không còn hai bản để lệch** |
| S5 | ASSERTED + chỉ số phủ 0% → chặn | giữ nguyên |
| S6 | CAUSAL + ASSERTED → chặn; CAUSAL luôn cần bằng chứng | giữ nguyên |
| S7 | METHODOLOGY_LIMITATION: subject ≠ related, subject phải có dữ liệu | giữ nguyên |
| S8 | Tổ hợp mâu thuẫn loại/trạng thái/phán xét | giữ nguyên |

### Bất biến khi SỬA LỖI (D)

| | Quy tắc | Vi phạm |
|---|---|---|
| D1 | Tập `id` của claim không đổi; không thêm, không bớt, không đổi tên | `bỏ mất/MỚI xuất hiện` |
| D2 | `subjectMetric`, `relatedMetric`, `claimType`, `assertionStatus`, `judgement`, `evidenceIds` không đổi | drift |
| D3 | **`resolvedText` của mỗi claim không đổi** (so nội dung, KHÔNG so ordinal) | `source_prose_changed` |
| D4 | `sourceRef` đổi mà `resolvedText` vẫn y hệt → CHO PHÉP (đảo thứ tự vô hại) | — |
| D5 | Số trong `resolvedText` không đổi | như quy tắc số hiện có |

D3+D4 là chỗ xử lý gọn toàn bộ nhóm đảo thứ tự / chèn / xoá: **so cái được trỏ
tới, không so con trỏ.**

---

## 3. Chứng minh xử lý được từng ca

| Ca | Cơ chế |
|---|---|
| Đảo thứ tự mảng | `itemId` bất biến; ordinal chỉ trong field; D3 so nội dung → không báo trôi dạt sai (D4) |
| Chèn phần tử | Các claim khác giữ nguyên `resolvedText` → không ảnh hưởng |
| Xoá phần tử được trỏ | R3 ngoài phạm vi → `source_ref_unresolved`; hoặc D3 nội dung đổi → `source_prose_changed` |
| `itemId` trùng | R4 chặn |
| `itemId` thiếu | R1 chặn |
| Một ô, hai phát biểu nhạy cảm | U1 chặn (validator đếm, không tin prompt) |
| Tham chiếu ĐÚNG nhưng chủ ngữ sai | S1 chặn |
| — phân cực sai | S4 chặn |
| — tình thái sai | S2 chặn |
| — chiều phán xét sai | S3 chặn |
| Sửa lỗi đổi `sourceRef` | D3: nội dung khác → chặn; nội dung giống → cho phép (D4) |
| Sửa lỗi đổi văn bản được trỏ | D3 chặn |
| Claim mồ côi | U4 chặn |
| Phát biểu nhạy cảm chưa khai | U3 chặn |
| Artifact schema 2.0 | Từ chối như 1.0 (mục 4) |
| Tách "phân giải" khỏi "ủng hộ ngữ nghĩa" | Hai nhóm mã lỗi riêng, hai cột riêng trong báo cáo (mục 5) |

---

## 4. Tương thích và migration

**Quyết định: KHÔNG cần migration.**

* `payload` là JSONB — hình dạng claim đổi không đụng cột nào.
* `CURSOR_OUTPUT_SCHEMA_VERSION` → `'2.1'`; `LEGACY_SCHEMA_VERSIONS` → `['1.0','2.0']`.
* CHECK `cursor_result_schema_matches_payload` (0022) tự động phủ 2.1 vì nó so
  `payload->>'schemaVersion'` với cột, không hardcode giá trị.
* Trigger 0020/0022 không đọc nội dung claim.
* Artifact 2.0 cũ: giữ trong DB làm lịch sử; validator từ chối cho lần chạy mới;
  `INDEX.json` chỉ liệt kê tệp của lô hiện hành nên không thể "lên ngôi" nhầm.

**Cần kiểm chứng bằng test, không giả định:** payload 2.1 round-trip qua JSONB,
và CHECK 0022 chấp nhận 2.1 mà vẫn từ chối payload không khai `schemaVersion`.

---

## 5. Mã BỎ ĐI và mã THÊM VÀO

### Bỏ (`validate.ts`)

| Thành phần | Lý do |
|---|---|
| `overlapRatio` | không còn hai bản văn bản để so |
| `sharesSubstantialText` | như trên |
| `sensitiveSentences` (tách câu để khớp) | đơn vị nay là Ô |
| `polarityNear` so giữa claim.text và prose | chỉ còn một bản |
| Ba vùng MATCHED / AMBIGUOUS / UNMATCHED | phân giải là tất định |
| `ambiguous_claim_correspondence` | không còn khái niệm mập mờ |
| `incomplete_claim_coverage` | thay bằng U1 (đếm trong ô) |
| `claim_metric_mismatch` | gộp vào S1 |
| `undeclared_metric_in_claim_text` | không còn `text` |
| `multiple_claims_for_one_statement` | thay bằng U2 |

Ước tính bỏ ~180 dòng, gồm phần lớn khối đã tốn năm vòng Codex.

### Thêm

| Thành phần | Vai trò |
|---|---|
| `resolveSourceRef(output, ref)` | trả `{ text, pointer } \| null` — tất định |
| `sensitiveClauseCount(text)` | dùng `clausesOf` sẵn có; nền của U1 |
| `buildSourceIndex(output)` | map `section+itemId` → item; phát hiện trùng (R4) |
| `enumerateSensitiveUnits(output)` | mọi ô có nhắc chỉ số nhạy cảm; nền của U3 |
| Mã lỗi mới | `source_ref_unresolved`, `source_ref_malformed`, `duplicate_source_item`, `multiple_assertions_in_source_unit`, `multiple_claims_for_source_unit`, `undeclared_sensitive_unit`, `source_prose_changed` |

### Sửa

* `prompt.ts` → `PROMPT_VERSION = '3.0.0'`; thay mục "sao chép nguyên văn" bằng
  đặc tả `sourceRef`; liệt kê `section`/`field` hợp lệ **sinh từ schema**; nêu rõ
  quy tắc một-ô-một-phát-biểu kèm ví dụ tách ô.
* `run.ts` → `detectSemanticDrift` nhận thêm `resolvedText` theo claim id; áp D3/D4/D5.
* Báo cáo → tách hai cột: **phân giải** (R/U) và **ủng hộ ngữ nghĩa** (S + evidence).

---

## 6. Ma trận test đối kháng

### Phân giải
1. ref hợp lệ tới `keyFindings/F-001/statement`
2. ref tới `itemId` không tồn tại → R1
3. `field` không tồn tại → R2
4. `ordinal` ngoài phạm vi → R3
5. hai item cùng `itemId` → R4
6. `ANALYSIS_SUMMARY` kèm `itemId` khác rỗng → R5
7. ref tới field không phải chuỗi (ví dụ `confidence`) → R2

### Ổn định
8. đảo thứ tự `keyFindings` → mọi ref vẫn phân giải đúng
9. chèn finding mới → ref cũ không đổi
10. xoá phần tử được trỏ → R3 hoặc D3
11. đảo thứ tự `limitations` trong cùng item, sửa ordinal cho khớp → D4 cho phép
12. đảo thứ tự nhưng KHÔNG sửa ordinal → D3 chặn

### Một ô một phát biểu
13. ô có hai mệnh đề nhạy cảm, một claim → U1
14. ô có hai mệnh đề nhạy cảm, hai claim cùng trỏ vào → U1 (vẫn chặn: phải tách ô)
15. hai claim cùng trỏ một ô → U2
16. ô nhạy cảm không có claim → U3
17. claim trỏ ô không nhạy cảm → U4

### Ngữ nghĩa trên văn bản đã phân giải
18. `subjectMetric` không có trong ô → S1
19. tình thái không khớp → S2
20. chiều phán xét ngược → S3
21. phân cực ngược → S4
22. ASSERTED về chỉ số phủ 0% → S5
23. CAUSAL+ASSERTED → S6; CAUSAL không bằng chứng → S6
24. METHODOLOGY_LIMITATION subject=related → S7
25. tổ hợp mâu thuẫn → S8

### Sửa lỗi
26. đổi `sourceRef` sang ô nội dung khác → D3
27. đổi văn bản ô được trỏ → D3
28. đổi số trong ô được trỏ → D5
29. đổi `sourceRef` mà nội dung y hệt → cho phép (D4)
30. thêm/bớt/đổi tên claim → D1; đổi trường ngữ nghĩa → D2

### Tương thích
31. payload 2.0 → `UNSUPPORTED_SCHEMA_VERSION`
32. payload 1.0 → như trên
33. round-trip 2.1 qua JSONB nguyên vẹn
34. CHECK 0022 nhận 2.1, từ chối payload thiếu `schemaVersion`

### Tính chất (quét tổ hợp)
35. mọi `section` × mọi `field` hợp lệ đều phân giải được
36. mọi chỉ số nhạy cảm × mọi `assertionStatus` giữ đúng S1–S5
37. không tổ hợp hợp-lệ-schema nào lọt qua toàn bộ nhánh R/U/S

---

## 7. Phạm vi rà soát Codex

Một vòng, phạm vi HẸP:

1. `resolveSourceRef` — có ca nào phân giải sai mà vẫn trả kết quả không?
2. `buildSourceIndex` — trùng `itemId`, `itemId` rỗng, section lạ.
3. U1 đếm mệnh đề — có cách nhồi hai phát biểu vào một mệnh đề không?
4. U3 liệt kê ô nhạy cảm — có bề mặt văn bản nào bị bỏ sót?
5. D3/D4 — đổi ref + đổi nội dung cùng lúc có lọt không?
6. Có đường nào để `EVIDENCE_SUPPORT_UNVERIFIED` hay lỗi HIGH lọt thành SUCCEEDED?
7. Ràng buộc sinh từ schema có phủ `sourceRef` không?

Không hỏi lại các vùng đã ổn định (persistence, provenance, migration, timeout,
subprocess) trừ khi mã của chúng thay đổi.

---

## 8. Kế hoạch thăm dò và lô chính thức

1. Cài đặt + test cho tới khi toàn bộ ma trận mục 6 xanh.
2. Rà soát Codex phạm vi mục 7; sửa hết BLOCKER/HIGH.
3. **Một** lần thăm dò trên `hinh_su`. Tiêu chí đi tiếp: 0 lỗi phân giải (R/U).
   Lỗi ngữ nghĩa (S) ở mức thấp là chấp nhận được — lô chính thức sẽ đo.
   Nếu còn lỗi R/U → sửa, rà soát lại, thăm dò lại. Không đóng băng khi R/U còn lỗi.
4. Đóng băng mới: 5 băm mã nguồn + lockfile + commit + dirty-diff + mtime +
   realpath tệp thực thi + số migration + số test.
5. Lô chính thức: 3 kênh × 3 mẫu đạt × trần 6 lần thử, một bộ hash duy nhất,
   không nới trần, không chạy lại để lấy kết quả đẹp.
6. Sau lô: đối chiếu lại băm/mtime, bảng lần thử, mẫu số, so sánh ngữ nghĩa,
   đối chiếu với mốc Batch 5 và mốc lô hỏng 4.0.

**Mốc giữ nguyên, không trộn mẫu:**
* Batch 5 (lexical): `hinh_su` 3/4, `phat_giao` 3/6, `phong_thuy` 3/3
* Lô cấu trúc 2.0: `hinh_su` 0/6, `phat_giao` 0/6, `phong_thuy` 0/2
