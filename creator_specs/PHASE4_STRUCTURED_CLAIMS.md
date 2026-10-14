# Hợp đồng KHẲNG ĐỊNH CÓ CẤU TRÚC (thay cho dò chuỗi)

## Vì sao phải đổi

Năm lô đo ổn định liên tiếp bị vô hiệu. Bốn trong số đó hỏng vì CÙNG một
nguyên nhân: biểu thức chính quy không biết một tính từ đang bổ nghĩa cho danh
từ nào.

| Câu thật | Regex hiểu | Thực nghĩa |
|---|---|---|
| `Độ phủ impressions/CTR >0 và observedDates tăng` | CTR tăng | mục tiêu thu thập dữ liệu |
| `nếu CTR thấp + impressions cao sẽ hướng khác nhau` | CTR thấp | kế hoạch chẩn đoán có điều kiện |
| `retention cao–reach thấp thay vì đổi thumbnail` | thumbnail thấp | khuyên ĐỪNG đổi thumbnail |
| `views quá thấp để ổn định CTR` | CTR thấp | giới hạn độ tin cậy phép đo |
| `sample size view thấp làm CTR nhiễu` | CTR thấp | giới hạn cỡ mẫu |

Mỗi lần vá là thêm một ngoại lệ ngữ pháp: liên từ, mệnh đề điều kiện, câu hỏi,
mệnh đề mục đích, phủ định hành động. Không có lý do tin rằng lô thứ sáu không
sinh ra cấu trúc thứ sáu. Vấn đề không nằm ở từng mẫu regex mà ở chỗ **suy đoán
ngữ pháp từ văn xuôi**.

Cách sửa: bắt mô hình **khai báo tường minh** ngữ nghĩa, thay vì để bộ kiểm định
đoán. Dò chuỗi vẫn giữ, nhưng hạ xuống vai trò **lưới an toàn**: nó phát hiện
ngôn ngữ nhạy cảm CHƯA được khai báo, chứ không tự quyết định câu đó đúng hay sai.

## Cấu trúc

Mọi phát biểu liên quan tới chỉ số nhạy cảm (CTR, impressions, thumbnail,
packaging) phải xuất hiện trong `metricClaims[]`:

```
metricClaims[]:
  id                          MC-001…
  claimType                   OBSERVATION | COMPARISON | CAUSAL
                            | DIAGNOSTIC_PLAN | METHODOLOGY_LIMITATION
                            | RECOMMENDATION
  subjectMetric               chỉ số BỊ phán xét, hoặc NONE
  judgement                   HIGH | LOW | INCREASED | DECREASED
                            | EFFECTIVE | INEFFECTIVE | UNKNOWN | NOT_APPLICABLE
  assertionStatus             ASSERTED | CONDITIONAL | QUESTION
                            | NEGATED_ACTION | LIMITATION
  evidenceIds[]
  requiresMissingnessDisclosure  bool
  text                        nguyên văn câu
  relatedMetric?              chỉ số ĐƯỢC NHẮC TỚI nhưng không bị phán xét
```

Điểm mấu chốt: `subjectMetric` tách khỏi `relatedMetric`. Năm câu ở bảng trên
đều có `subjectMetric` KHÁC CTR — chính điều mà regex không thể biết:

| Câu | subjectMetric | relatedMetric | claimType | assertionStatus |
|---|---|---|---|---|
| `views quá thấp để ổn định CTR` | `views` | `impression_ctr` | METHODOLOGY_LIMITATION | LIMITATION |
| `sample size view thấp làm CTR nhiễu` | `sample_size` | `impression_ctr` | METHODOLOGY_LIMITATION | LIMITATION |
| `nếu CTR thấp thì hướng kiểm chứng khác` | `impression_ctr` | – | DIAGNOSTIC_PLAN | CONDITIONAL |
| `thay vì đổi thumbnail hàng loạt` | `thumbnail` | – | RECOMMENDATION | NEGATED_ACTION |
| `CTR thấp` | `impression_ctr` | – | OBSERVATION | ASSERTED |

Chỉ dòng cuối là khẳng định phải chặn khi độ phủ bằng 0.

## Quy tắc kiểm định (tất định, không đoán ngữ pháp)

1. `ASSERTED` + `subjectMetric` thuộc nhóm không có dữ liệu (độ phủ 0) → **CHẶN**.
   Không có ngoại lệ nào theo cách diễn đạt.
2. `ASSERTED` + `judgement` khác `UNKNOWN`/`NOT_APPLICABLE` → bắt buộc có
   `evidenceIds` neo được về bằng chứng của gói.
3. `CONDITIONAL`, `QUESTION`, `NEGATED_ACTION`, `LIMITATION` → được phép nhắc tới
   chỉ số thiếu dữ liệu, nhưng `judgement` **không được** là một phán xét khẳng
   định về chỉ số thiếu đó nếu `subjectMetric` chính là chỉ số ấy và
   `assertionStatus = ASSERTED`.
4. `METHODOLOGY_LIMITATION` bắt buộc `subjectMetric != relatedMetric`. Nếu bằng
   nhau thì đó là khẳng định trá hình → **CHẶN**.
5. `CAUSAL` chỉ hợp lệ khi `assertionStatus = CONDITIONAL` và có
   `evidenceIds`; `CAUSAL` + `ASSERTED` → **CHẶN** tuyệt đối.
6. `requiresMissingnessDisclosure = true` → câu phải nêu rõ dữ liệu thiếu, và
   `analysisSummary.primaryConstraint` phải nhắc tới chỉ số đó.
7. Tổ hợp mâu thuẫn bị chặn: `NEGATED_ACTION` + `claimType = OBSERVATION`;
   `LIMITATION` + `claimType = RECOMMENDATION`; `QUESTION` + `judgement` khẳng định.
8. Mọi `metricClaims` được trích trong `keyFindings`/`recommendations` phải neo
   transitively về bằng chứng gói — dùng lại thuật toán điểm bất động sẵn có.

## Lưới an toàn (giữ lại, nhưng đổi vai)

Bộ dò chuỗi cũ vẫn chạy trên toàn bộ văn xuôi, nhưng:

* nó **không** quyết định câu đúng hay sai;
* khi thấy ngôn ngữ nhạy cảm trong văn xuôi mà **không có** `metricClaims` nào
  có `text` tương ứng → báo lỗi `undeclared_metric_claim` (BLOCKER);
* thông điệp chỉ ra "thiếu khai báo", không phán xét ngữ nghĩa.

Nhờ vậy, cách diễn đạt mới lạ không còn gây từ chối oan: nó chỉ buộc mô hình
khai báo. Và một khẳng định muốn lọt qua thì phải tự khai `ASSERTED`, lúc đó
quy tắc 1 chặn nó một cách tất định.

## Phiên bản

* `CURSOR_OUTPUT_SCHEMA_VERSION` 1.0 → **2.0** (thêm trường bắt buộc)
* `PROMPT_VERSION` 1.0.0 → **2.0.0**
* Kết quả cũ (schema 1.0) vẫn đọc được; bộ kiểm định từ chối 1.0 cho lần chạy mới
* Không cần migration database: `payload` là JSONB, `schema_version` đã có sẵn cột
