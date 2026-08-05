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

## 3. Đối chiếu văn xuôi ↔ claim

### Tất định

* thiếu khai báo (`undeclared_metric_claim`);
* claim mồ côi (`orphan_metric_claim`);
* nhiều claim cùng một phát biểu (`multiple_claims_for_one_statement`);
* claim nói về chỉ số khác câu (`claim_metric_mismatch`);
* lệch phân cực (`claim_polarity_mismatch`);
* trạng thái khai không có dấu hiệu trong câu (`modality_not_supported_by_text`);
* chủ ngữ không xuất hiện trong câu (`subject_metric_not_in_text`).

### Heuristic

Phép nối dùng Jaccard đối xứng ở mức CÂU, ba vùng: ≥0.75 khớp, 0.45–0.75 mập mờ
(chặn, mức HIGH), <0.45 không khớp. Ngưỡng là lựa chọn kỹ thuật, không phải hằng
số tự nhiên. Một câu diễn đạt lại rất xa vẫn có thể rơi xuống "không khớp" và bị
báo thiếu khai báo — tức là **thiên về từ chối**, không thiên về cho qua.

Không được mô tả phép nối này là "đã chứng minh hai câu tương đương ngữ nghĩa".

## 4. Chất lượng đầu ra của mô hình

Tầng kiểm định chặn được khẳng định không có căn cứ. Nó **không** làm mô hình
phân tích tốt hơn. Hai điều khác nhau, và không được lẫn:

* `phat_giao` ở Batch 5 sinh hai khuyến nghị P0 không bằng chứng và một lần JSON
  hỏng. Đó là khuyết điểm của MÔ HÌNH. Bộ dò tốt hơn không sửa được nó.
* Cải tiến bộ dò làm giảm TỪ CHỐI OAN. Nó không làm tăng chất lượng phân tích.

Khi báo cáo, luôn tách hai con số: "bị từ chối vì bộ dò sai" và "bị từ chối vì
mô hình sai".
