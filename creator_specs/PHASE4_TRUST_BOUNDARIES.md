# Ranh giới tin cậy — Phase 4

Tài liệu này ghi rõ hệ thống CHỨNG MINH được gì và KHÔNG chứng minh được gì.
Nó tồn tại vì loại lỗi tốn kém nhất trong cả phase này không phải lỗi tính toán,
mà là **tuyên bố mạnh hơn bằng chứng thực có**: "Migration xong" khi migration
chưa chạy, tệp cũ trông như vừa cập nhật, và một tiến trình treo trông như đang
phân tích.

## 1. Nguồn gốc (provenance)

### Chứng minh được

| Giá trị | Ghi ở đâu | Ý nghĩa |
|---|---|---|
| `schema_version`, `prompt_version` | cột DB, `_meta`, `INDEX.json` | phiên bản hợp đồng đã dùng |
| `validator_hash`, `schema_hash`, `prompt_source_hash` | như trên | băm NỘI DUNG TỆP đọc lúc nạp module |
| `package_hash` | `cursor_analysis_request` | gói bằng chứng đã dùng |
| `tool_name` | bản kê | đường dẫn THẬT của tệp thực thi sau khi bỏ symlink |
| lineage IDs | khoá ngoại phức hợp | quan hệ giữa các dòng là có thật |

Các giá trị này được gắn LÚC TẠO execution, không suy ngược từ artifact sau khi
chạy — suy ngược chỉ là đọc lại chính thứ mình vừa ghi.

### KHÔNG chứng minh được

* **Tiến trình đã thực thi đúng những byte đó.** Băm được tính bằng cách đọc tệp
  từ đĩa lúc nạp module. Nếu runtime chạy bản đã transpile trong cache, hoặc một
  module bị vá lúc chạy, băm vẫn khớp trong khi mã thực thi khác.
* **Tệp thực thi không bị thay sau khi phân giải.** Giữa `realpathSync` và
  `spawn` có một khoảng thời gian. Đây là TOCTOU cố hữu.
* **Phụ thuộc không đổi.** Chỉ ba tệp mã nguồn được băm; `node_modules` thì không.
* **Máy chủ không bị chiếm quyền.** Ai ghi thẳng được vào database thì cũng giả
  được mọi giá trị nguồn gốc, và trigger chống trộn phiên bản sẽ vui vẻ sao chép
  giá trị giả đó xuống toàn bộ chuỗi retry.

**Vì vậy: đây KHÔNG phải attestation.** Nó là bản ghi có kỷ luật, đủ để phát hiện
trôi dạt do vô ý và để hậu kiểm, không đủ để chống một kẻ tấn công có quyền ghi.
Không được gọi nó là bằng chứng mật mã ở bất kỳ đâu.

## 2. Ngữ nghĩa của bằng chứng

### Chứng minh được (tất định)

* evidence id CÓ TỒN TẠI trong gói;
* neo được về bằng chứng gói qua chuỗi trích dẫn (điểm bất động, phát hiện chu trình);
* thuộc đúng workspace / lần phân tích / kênh / gói;
* khuyến nghị P0 có bằng chứng;
* không tự trích chính nó.

### KHÔNG chứng minh được

Hệ thống **không** kiểm được rằng một bằng chứng THỰC SỰ ỦNG HỘ:

* chỉ số đã khai ở `subjectMetric`;
* chiều phán xét đã khai (`LOW` vs `HIGH`);
* diễn giải nhân quả;
* đúng kết luận cụ thể đó.

Ví dụ vẫn lọt: một claim khai `subjectMetric=views, judgement=LOW` trích `OBS-001`
trong khi `OBS-001` là quan sát về retention ở mức cao. Cả hai đều tồn tại, cùng
lineage, không chu trình — nhưng bằng chứng không nói điều claim nói.

**Lựa chọn có ý thức:** không dựng một phép so khớp mờ giữa tên chỉ số và khoá
feature. Nó sẽ tạo ra từ chối oan hàng loạt — đúng thứ đã làm hỏng năm lô đo ổn
định của tầng dò chuỗi. Thà ghi rõ đây là khoảng trống còn hơn dán lên một phép
kiểm trông có vẻ chặt.

**Hệ quả vận hành:** kết quả của tầng này KHÔNG đủ tin để hành động tự động mà
không có người xem. Nó đủ tin để *thu hẹp* việc phải xem thủ công.

## 3. Đối chiếu văn xuôi ↔ claim (schema 2.1)

Ở 2.0, claim SAO CHÉP câu vào `text` và bộ kiểm định phải nối bản sao với bản
gốc bằng Jaccard ba vùng. Cả lô 2.0 hỏng vì hai bản lệch nhau — 55 lỗi "khớp mập
mờ", 24 claim mồ côi. **Cơ chế đó đã bị bỏ hoàn toàn.** 2.1 dùng `sourceRef`
TRỎ tới ô gốc, nên chỉ còn MỘT bản văn bản và không còn gì để lệch.

### Tất định

Phân giải tham chiếu là tất định: một ref hoặc trỏ tới đúng một ô có thật, hoặc
không. Không có vùng xám, không có ngưỡng.

* ref không phân giải được (`source_ref_unresolved`) — id/field/ordinal sai;
* ref sai hình dạng (`source_ref_malformed`) — ví dụ khai `itemId` cho section
  không có id;
* `itemId` trùng trong một section (`duplicate_source_item`);
* hai phần tử TRÙNG NỘI DUNG trong cùng field (`source_ref_ambiguous`) — `ordinal`
  mất nghĩa, nên từ chối thay vì đoán;
* hai claim cùng trỏ một ô (`multiple_claims_for_source_unit`);
* claim mồ côi (`orphan_metric_claim`).

Danh sách `section`/`field` hợp lệ được SINH TỪ Zod schema, và cùng một danh
sách đó được dùng cho ba việc: in ra prompt, chặn ở bộ phân giải, liệt kê ô để
đòi khai báo. Một trường văn bản mới thêm vào schema tự động vào cả ba.

### Heuristic ngôn ngữ — KHÔNG được gọi là tất định

Bốn phép kiểm sau dựa trên tách mệnh đề và nhận diện từ khoá, không phải phân
tích cú pháp:

* `assertion_status_wrong_for_field` — **ngoại lệ tất định**: với ba trường NHÃN
  (`dataRequests[].metricOrArtifact`, `hypotheses[].missingEvidence`,
  `manualReviewTargets[].reviewQuestions`) tình thái đọc từ TÊN TRƯỜNG chứ không
  từ từ ngữ, và `ASSERTED` bị cấm. Lý do: nhãn không mang từ điều kiện/nghi
  vấn/giới hạn nào, nên trước đó `ASSERTED` là trạng thái DUY NHẤT đi qua được —
  tức hợp đồng ép khai trạng thái mạnh nhất ở đúng ô vô hại nhất. Cả hai lần
  thăm dò `hinh_su` của prompt 3.0.0 đều gãy ở đây;
* `multiple_assertions_in_source_unit` (U1) — đếm mệnh đề nhạy cảm trong một ô;
* `undeclared_sensitive_unit` (U3) — nhận diện ô có nhắc chỉ số nhạy cảm;
* `modality_not_supported_by_text` (S2) — dấu hiệu tình thái trong ô;
* `judgement_contradicts_text` (S3) và `claim_polarity_mismatch` (S4) — chiều và
  phân cực của mệnh đề chứa chủ ngữ.

**Giới hạn cụ thể của U1, ghi rõ vì nó dễ bị tưởng là đã phủ kín.** Bộ tách mệnh
đề cắt ở `. ! ? ; : ,`, ở gạch ngang dài `–` `—`, và ở các liên từ chỉ nối mệnh
đề: `nhưng`, `còn`, `đồng thời`, `trong khi`, `tuy nhiên`, `mặt khác`, `ngoài ra`.
Nó **KHÔNG** cắt ở `và`, có chủ ý:
trong tiếng Việt `và` nối danh ngữ cũng nhiều như nối mệnh đề, nên cắt ở đó sẽ
đếm câu *"Không thể đánh giá tiếp cận vì impressions và CTR có độ phủ 0%"* —
một phát biểu, chủ ngữ ghép — thành hai và chặn oan đúng kiểu câu mà hợp đồng
muốn khuyến khích.

Hệ quả: một ô chứa hai phán xét nối bằng `và` ("CTR thấp và impressions thấp")
được U1 đếm là MỘT. Nó vẫn bị chặn bởi `asserted_claim_on_missing_metric` khi chỉ
số có độ phủ 0, và bởi `undeclared_metric_in_claim_text` khi chỉ số nhắc tới
không nằm trong `subjectMetric`/`relatedMetric` đã khai — nhưng **không** bị U1
chặn. Đây là một lỗ đã biết, không phải một khoảng trống chưa ai nghĩ tới.

Không được mô tả tầng U/S là "đã chứng minh mỗi ô chỉ mang một phát biểu".

## 4. Chất lượng đầu ra của mô hình

Tầng kiểm định chặn được khẳng định không có căn cứ. Nó **không** làm mô hình
phân tích tốt hơn. Hai điều khác nhau, và không được lẫn:

* `phat_giao` ở Batch 5 sinh hai khuyến nghị P0 không bằng chứng và một lần JSON
  hỏng. Đó là khuyết điểm của MÔ HÌNH. Bộ dò tốt hơn không sửa được nó.
* Cải tiến bộ dò làm giảm TỪ CHỐI OAN. Nó không làm tăng chất lượng phân tích.

Khi báo cáo, luôn tách hai con số: "bị từ chối vì bộ dò sai" và "bị từ chối vì
mô hình sai".
