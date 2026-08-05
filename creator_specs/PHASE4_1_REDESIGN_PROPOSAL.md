# Phase 4.1 — Đề xuất thiết kế lại (chưa sửa mã)

## Bằng chứng nền

Lô chính thức (validator `1913b3d558a7`, schema/prompt 2.0/2.0.0): `hinh_su` 0/6,
`phat_giao` 0/6, `phong_thuy` 0/2 (lô bị ngắt). Giữ nguyên làm mốc so sánh.

Điểm mấu chốt của dữ liệu: **bằng chứng neo được 100% ở mọi lần chạy**, chỉ 2 vi
phạm nhân quả và 1 P0 thiếu bằng chứng trong 16 execution. Các quy tắc an toàn
cốt lõi gần như không bị chạm. 386/486 lỗi BLOCKER/HIGH nằm ở **cơ chế khai báo**:

| Lỗi | Số lần | Thuộc về |
|---|---|---|
| `modality_not_supported_by_text` | 147 | khai báo |
| `undeclared_metric_claim` | 126 | khai báo |
| `subject_metric_not_in_text` | 95 | khai báo |
| `undeclared_metric_in_claim_text` | 63 | khai báo |
| `ambiguous_claim_correspondence` | 55 | **sao chép nguyên văn** |
| `multiple_claims_for_one_statement` | 27 | khai báo |
| `orphan_metric_claim` | 24 | **sao chép nguyên văn** |
| `contradictory_claims_for_one_statement` | 19 | khai báo |
| `causal_claim` | 2 | an toàn nội dung |
| `p0_without_evidence` | 1 | an toàn nội dung |

Chi phí nằm ở chỗ mô hình phải VỪA viết phân tích VỪA sao chép lại chính nó
từng ký tự. Cả hai phương án dưới đây đều nhắm vào đúng chỗ đó.

---

## Phương án 1 — Tham chiếu VỊ TRÍ thay cho sao chép nguyên văn

Bỏ `text`, thay bằng con trỏ tới đúng ô văn bản:

```
metricClaims[]:
  sourcePath   "keyFindings[2].limitations[0]"   // JSON pointer, ô văn bản
  (bỏ text)
```

Kèm một ràng buộc viết lách: **mỗi ô văn bản tự do chứa TỐI ĐA MỘT phát biểu về
chỉ số nhạy cảm.** Muốn nói hai điều thì tách thành hai phần tử mảng.

### Thay đổi cần làm

| Tầng | Thay đổi |
|---|---|
| Schema | bỏ `text`, thêm `sourcePath` (chuỗi, regex JSON-pointer); giữ nguyên 9 trường còn lại |
| Prompt | thay mục "sao chép nguyên văn" bằng "trỏ đường dẫn"; nêu quy tắc một-phát-biểu-một-ô; danh sách đường dẫn hợp lệ sinh từ schema |
| Validator | bỏ `overlapRatio`, `sensitiveSentences`, `polarityNear`, `sharesSubstantialText`, ba vùng MATCHED/AMBIGUOUS/UNMATCHED, `incomplete_claim_coverage`; thay bằng phân giải đường dẫn |
| Persistence | không đổi (JSONB) |
| Provenance | không đổi |

### Danh tính và bất biến ngữ nghĩa

Không đổi bản chất: `detectSemanticDrift` vẫn so theo `id`, và các trường ngữ
nghĩa vẫn bị khoá. Thay `text` bằng `sourcePath` trong danh sách trường bất biến
— trỏ sang ô khác là đổi ngữ nghĩa, bắt được y như cũ. Quy tắc số trong `text`
chuyển thành: **nội dung ô được trỏ tới** không được đổi số.

### Kiểm định từng khía cạnh

* **Tương ứng** — trở thành TẤT ĐỊNH. Đường dẫn phân giải được hoặc không.
  Không còn ngưỡng, không còn vùng mập mờ, không còn heuristic.
* **Tính đầy đủ** — quét từ vựng vẫn chạy: ô nào nhắc chỉ số nhạy cảm mà không
  có claim nào trỏ tới → `undeclared`. Đơn giản hơn hẳn vì đơn vị là Ô, không
  phải câu.
* **Phân cực / tình thái / chủ ngữ** — đọc thẳng từ ô được trỏ tới, tức đúng
  văn bản thật. Hết hẳn lớp lỗi "text khác prose".
* **Bằng chứng** — không đổi.

### Lỗi mới và ranh giới tin cậy

* **Trỏ sai ô** — mô hình trỏ vào ô lân cận. Bắt được: ô được trỏ phải nhắc
  đúng `subjectMetric` (quy tắc `subject_metric_not_in_text` áp lên nội dung ô).
* **Ràng buộc viết lách** — "một phát biểu một ô" là ràng buộc THẬT lên cách
  hành văn. Rủi ro: mô hình nhồi hai phát biểu vào một ô. Bắt được bằng quy tắc
  đếm: ô có ≥2 mệnh đề nhạy cảm mà chỉ một claim → chặn.
* **Còn lại**: ngữ nghĩa bằng chứng vẫn không chứng minh được (không đổi).

### Migration

Không cần. `payload` là JSONB; `schema_version` lên `2.1`; payload 2.0 bị từ
chối như 1.0 hiện nay. Trigger 0021/0022 không đụng tới nội dung claim.

### Kế hoạch test

* Phân giải đường dẫn: hợp lệ, sai chỉ số mảng, đường dẫn không tồn tại, trỏ vào
  ô không phải chuỗi.
* Ô có hai phát biểu nhạy cảm, một claim → chặn.
* Trỏ sang ô khác giữa root và sửa lỗi → trôi dạt.
* Toàn bộ ca thật của lô hỏng, viết lại theo dạng tham chiếu.
* Giữ nguyên mọi test an toàn nội dung (nhân quả, CTR, P0, chu trình).

### Ảnh hưởng dự kiến

Xoá thẳng ~79 lỗi (`ambiguous` 55 + `orphan` 24) và giảm mạnh nhóm
`undeclared`/`subject`/`in_claim_text` vì không còn hai bản văn bản để lệch nhau.
Gánh nặng còn lại của mô hình: chọn đúng nhãn ngữ nghĩa — việc khó nhưng ngắn.

---

## Phương án 2 — Tách làm HAI LƯỢT có kiểm định riêng

* **Lượt A**: sinh phân tích, KHÔNG có `metricClaims`.
* **Lượt B**: nhận nguyên văn output lượt A, chỉ sinh `metricClaims`.

### Thay đổi cần làm

| Tầng | Thay đổi |
|---|---|
| Schema | tách `analysisSchema` (A) và `claimsSchema` (B); output cuối là hợp của hai |
| Prompt | hai prompt riêng, hai phiên bản riêng, hai băm riêng |
| Validator | kiểm A (cấu trúc + bằng chứng), kiểm B (khai báo), kiểm hợp nhất |
| Persistence | **mỗi lần thử = hai execution**; cần liên kết A→B bất biến |
| Provenance | thêm `phase` (A/B), băm payload A gắn vào B; chuỗi retry phải phân biệt "sửa A" và "sửa B" |

### Danh tính và bất biến ngữ nghĩa

Phức tạp hơn hẳn. Cần bất biến MỚI: **lượt B không được sửa văn bản của A.** Phải
so payload A với phần A trong output cuối — thêm một tầng phát hiện trôi dạt nữa,
đúng loại mã đã cần ba vòng rà soát mới đúng.

### Kiểm định

Giống phương án 1 nếu lượt B cũng dùng tham chiếu vị trí. Nếu lượt B vẫn sao chép
nguyên văn thì **lỗi cũ quay lại nguyên vẹn** — chỉ khác là bây giờ mô hình có
văn bản trước mặt, nên tỉ lệ sao chép đúng có thể cao hơn (chưa đo được).

### Lỗi mới và ranh giới tin cậy

* Lượt B sửa trộm văn bản của A.
* Chuỗi retry hai chiều: hỏng ở A hay ở B, sửa cái nào.
* Mẫu số ổn định phức tạp: một "lần thử" giờ gồm hai execution có thể hỏng độc lập.
* **Chi phí gấp đôi**: hai lần gọi LLM cho mỗi lần thử, ~2× thời gian lô.

### Migration

Cần: thêm cột `phase`, băm payload lượt trước, và ràng buộc A→B. Ít nhất một
migration mới kèm trigger — chính là vùng đã sinh ra nhiều lỗi nhất từ trước tới nay.

### Kế hoạch test

Tất cả của phương án 1, cộng: liên kết A→B, B không sửa được A, chuỗi retry hai
pha, mẫu số hai execution, và hỏng một phần.

### Ảnh hưởng dự kiến

Có thể cải thiện tuân thủ vì mỗi lượt đơn giản hơn. Nhưng **không loại bỏ** lớp
lỗi sao chép nguyên văn trừ khi kèm phương án 1 — và làm phức tạp thêm đúng những
tầng (persistence, provenance, retry) mà mỗi lần sửa đều cần vài vòng rà soát.

---

## Khuyến nghị: **Phương án 1**

Ba lý do:

1. **Xoá lớp lỗi, không né lớp lỗi.** Tham chiếu vị trí làm cho tương ứng trở
   thành phép phân giải tất định. Phương án 2 chỉ làm nhiệm vụ sao chép dễ hơn,
   không bỏ được nó — trừ khi cũng dùng tham chiếu, tức là phương án 1 nằm bên trong.
2. **Bề mặt rủi ro nhỏ hơn.** Không cột mới, không trigger mới, không mô hình
   execution mới. Chi phí lô giữ nguyên thay vì gấp đôi.
3. **Bỏ được nhiều mã hơn là thêm.** `overlapRatio`, tách câu, phân cực theo mệnh
   đề, ba vùng khớp, quy tắc độ phủ — tất cả biến mất. Đó cũng chính là đám mã đã
   ngốn năm vòng Codex và vẫn còn giới hạn.

Phương án 2 là **bước leo thang** nếu phương án 1 chạy thật vẫn không đạt: lúc đó
đã biết rõ nút thắt là "chọn nhãn ngữ nghĩa" chứ không phải "sao chép".

## Lộ trình tối thiểu

1. Schema 2.1: bỏ `text`, thêm `sourcePath`; từ chối 2.0 và 1.0.
2. Prompt 3.0.0: trỏ đường dẫn + quy tắc một-phát-biểu-một-ô; ràng buộc vẫn sinh từ schema.
3. Validator: bỏ toàn bộ máy móc tương ứng heuristic; thêm phân giải đường dẫn và
   đếm mệnh đề nhạy cảm trong ô.
4. Cập nhật `detectSemanticDrift`: `sourcePath` vào nhóm trường bất biến; quy tắc số
   áp lên nội dung ô được trỏ.
5. Test: bộ mới cho phân giải + toàn bộ ca thật của lô hỏng viết lại; giữ nguyên
   test an toàn nội dung.
6. Rà soát Codex một vòng, phạm vi hẹp: phân giải đường dẫn, đếm mệnh đề, trôi dạt.
7. **Một** lần thăm dò trên `hinh_su` trước khi đóng băng.
8. Đóng băng mới (hash mới toàn bộ) → lô chính thức 3 kênh × 3 mẫu × trần 6.

Lô hỏng hiện tại giữ nguyên làm mốc: **0/6, 0/6, 0/2**. Lô mới không được trộn
mẫu với nó.
