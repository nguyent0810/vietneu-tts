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
đề cắt ở `. ! ? ; :`, ở dấu phẩy, và ở các liên từ chỉ nối mệnh đề: `nhưng`,
`còn`, `đồng thời`, `trong khi`, `tuy nhiên`, `mặt khác`, `ngoài ra`.

**Dấu phẩy được xử lý riêng, vì nó gánh ba vai khác nhau.** Chỉ vai thứ nhất là
ranh giới mệnh đề:

1. ngăn cách MỆNH ĐỀ — *"CTR thấp, impressions cao"* → tách;
2. ngăn cách MỤC LIỆT KÊ — *"thumbnail, tiêu đề, hay packaging"* → **không** tách;
3. ngăn cách TRẠNG NGỮ ĐỨNG TRƯỚC — *"Khi có CTR, so sánh…"* → **không** tách.

Một chuỗi mảnh nối bằng dấu phẩy được gộp lại thành MỘT mệnh đề khi có một trong
hai dấu hiệu VỊ TRÍ: một mảnh (không phải mảnh đầu) mở đầu bằng `và`/`hay`/`hoặc`;
hoặc một mảnh như thế CHỨA liên từ liệt kê mà không mang dấu hiệu phán xét nào
(tiếng Việt thường bỏ dấu phẩy trước `và` ở mục cuối). Mảnh mở đầu bằng liên từ
đối lập/nhân quả (`nhưng`, `tuy nhiên`, `do đó`, `vì vậy`…) luôn là mệnh đề riêng
và cắt ngang phép gộp.

Điều kiện "không mang phán xét" là hàng rào: *"CTR thấp, impressions và thumbnail
đều cao"* có `cao` ở mảnh sau nên KHÔNG bị gộp.

**Cơ sở, không phải suy đoán:** quét 517 ô THẬT từ 74 lần chạy đã lưu. Trước khi
sửa, dấu phẩy làm đổi kết quả U1 ở 25 ô và **cả 25 đều là tách SAI** — không ô
nào là hai phát biểu thật. Sau khi sửa, con số đó là **0**, và tổng số ô bị U1
chặn giảm từ 72 xuống 55.

**Giới hạn còn lại của dấu phẩy:** cụm ĐỒNG VỊ không có liên từ
(*"impressions, chỉ số đo lượt hiển thị, hiện phủ 0%"*) vẫn bị đếm thành hai.
Phân biệt nó với hai mệnh đề thật cần phân tích cú pháp; ca này không xuất hiện
trong 517 ô đã quét, và có test ghi lại hành vi hiện tại.

Bộ tách **KHÔNG** cắt ở `và` trần, có chủ ý:
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


## Bổ sung sau rà soát đối kháng G8 (2026-08-06)

**Bản ghi nguồn gốc DÙNG CHUNG có thể cùng sai và mọi phép so vẫn xanh.**

`CONTRACT_PROVENANCE` được tính MỘT lần lúc nạp module rồi chép sang mọi bề mặt.
Điều đó làm phép so giữa các bề mặt có nghĩa — nhưng nó chỉ chứng minh các BẢN
SAO khớp nhau, KHÔNG chứng minh bản gốc đúng. Nếu bản ghi chung sai, cả sáu bề
mặt cùng sai giống hệt nhau và `checkProvenanceCoverage` báo ĐẠT.

Đã thu hẹp được một phần:

* Giá trị sentinel (`'unavailable'`, chuỗi rỗng) nay bị tính là THIẾU, nên
  "không đọc được tệp nguồn" không còn giả dạng thành một giá trị hợp lệ.
* Git không chạy được nay khai `dirty: true` thay vì `false` — trạng thái không
  xác định không được phép biến thành khẳng định "sạch".
* Có test đòi `CONTRACT_PROVENANCE` thật không chứa sentinel nào.

**Phần còn lại KHÔNG khắc phục được bằng thêm phép so, và được chấp nhận:**

* `gitDirtyDiffHash` tính từ `git diff HEAD`, vốn KHÔNG bao gồm tệp chưa theo
  dõi. Hai lần chạy chỉ khác nhau ở một module untracked được import gián tiếp
  sẽ có cùng băm diff.
* Sáu băm mã nguồn phủ đúng sáu tệp quyết định ngữ nghĩa, không phủ dependency
  gián tiếp.
* Băm đọc từ đĩa lúc nạp module; nó không chứng minh runtime đã thực thi đúng
  những byte ấy.

Đây vẫn là **bản ghi có kỷ luật**, không phải **attestation**. Nó phát hiện
được lệch và trôi dạt; nó không chống được một môi trường build đã bị can thiệp.
Ranh giới này phải được nêu lại nguyên văn ở mọi báo cáo lô chính thức.

**Ràng buộc database không chống được superuser.** Trigger 0028/0031 chặn sự cố,
chặn mã sai và chặn script ghi thẳng — ba nguồn rủi ro thật. Chúng không chặn
được người có quyền `ALTER TABLE ... DISABLE TRIGGER`.


## 5. KHÔNG NGHĨA VỤ NÀO — ranh giới quan trọng nhất của lượt hai (2026-08-07)

> `obligationCount: 0` nghĩa là **"bộ dò không thấy gì"**, KHÔNG phải
> **"bài phân tích sạch"**. Hai câu đó trông giống nhau ở mọi bảng biểu phía sau
> và phải được đọc khác nhau.

### Chuyện đã xảy ra

Kiến trúc hai lượt cưỡng chế U3 bằng CẤU TRÚC: tập nghĩa vụ **chính là** tập ô
nhạy cảm. Sức mạnh ấy có một mặt sau — nếu bộ dò không nhận ra một ô, ô đó không
sinh nghĩa vụ, và **không có gì để mà khai thiếu**. Sự vắng mặt của vi phạm trở
thành hệ quả trực tiếp của sự vắng mặt của phát hiện.

`sensitive.ts` thiếu **"ảnh bìa"** — cách gọi thumbnail phổ biến nhất trong
tiếng Việt. Bảng bí danh biết "hình thu nhỏ" (bản dịch sát nghĩa, ít ai dùng) và
"ảnh đại diện" (thật ra là avatar), nhưng không biết đúng từ mà người ta dùng.

Hậu quả **đổi bản chất** giữa hai vòng khắc phục:

| | Trước G-R3 | Sau G-R3 |
|---|---|---|
| Kết quả | short-circuit, `resultId: null` | hiện vật CHÍNH THỨC, đủ giấy tờ |
| Vào mẫu số? | không | **có** |
| Đọc như | "lần chạy hỏng" | **"phân tích sạch"** |

G-R3 (bỏ đường cấp phép thứ hai) **đúng** — một đường cấp phép không đi qua cổng
là lỗi nặng hơn. Nhưng nó **không thêm phép kiểm độc lập nào cho chính ca mà nó
vừa cấp phép**. Đó là khoảng trống, và nó nằm ở đúng chỗ nguy hiểm nhất: đầu ra
trông đẹp nhất lại là đầu ra mà hệ thống hiểu ít nhất.

### Đã làm gì

* `sensitive.ts` nhận thêm `ảnh bìa` / `hình bìa`, và
  `OBLIGATION_GENERATOR_VERSION` tăng `1.0 → 1.1` — đổi bảng bí danh là đổi định
  nghĩa "ô nào phải khai báo", nên **số đo trước và sau không được gộp**.
* Có test CHẠY cho cả năm cách gọi thumbnail và cho ca "toàn bộ kết luận nói về
  ảnh bìa" (`tests/unit/remediation-f-series.test.ts`).
* `obligationCount` được ma trận phủ nguồn gốc ĐÒI trên `artifactMeta`, không
  còn chỉ dựa vào một assertion viết tay.

### Vẫn KHÔNG chứng minh được — chấp nhận có điều kiện

* Bịt "ảnh bìa" đóng **một** lỗ đã biết. Nó **không** chứng minh bảng bí danh đã
  đầy đủ. Bộ dò là **heuristic ngôn ngữ**, và mọi lập luận dựa trên "0 nghĩa vụ"
  đều thừa hưởng đúng ranh giới ấy.
* Không có phép kiểm độc lập nào xác nhận một bài phân tích 0 nghĩa vụ *thật sự*
  không chạm chỉ số nhạy cảm. Muốn có thì cần một bộ dò thứ hai, độc lập về cách
  cài đặt — chưa tồn tại.
* **Quy tắc báo cáo, bắt buộc:** mọi lô chính thức phải in số mẫu có
  `obligationCount = 0` **tách riêng**, và không được mô tả chúng là "sạch". Cách
  gọi đúng: *"bộ dò không tìm thấy ô nhạy cảm nào"*.


## 6. Băm bản khai: cưỡng chế ở TẦNG ỨNG DỤNG, không ở database (2026-08-12)

> Ràng buộc database KHÔNG thể kiểm rằng `cursor_declaration_result.payload_hash`
> đúng là băm của `payload` cùng hàng. Đây là ranh giới ĐÃ BIẾT, có lý do, và
> được chấp nhận — không phải một chỗ bị bỏ quên.

### Điều gì được cưỡng chế ở đâu

| Bất biến | Nơi cưỡng chế |
|---|---|
| Bản khai TỒN TẠI cho execution ấy | trigger 0033 |
| Bản khai KHỚP bản kê: `analysis_execution_id`, `analysis_payload_hash`, `obligation_set_hash` | trigger 0037 |
| Hàng kết quả neo đúng bản phân tích và tập nghĩa vụ | trigger 0033 + 0037 |
| **`payload_hash` đúng là băm của `payload`** | **CHỈ `composite.ts`** (`composite_declaration_payload_hash_mismatch`) |

### Vì sao không đẩy xuống database

Băm được tính trên `stableStringify(payload)` — một phép chuẩn tắc hoá của
JavaScript (sắp khoá đệ quy, loại `undefined`). Viết lại nó bằng SQL để trigger
tự băm lại sẽ tạo ra **bản cài đặt THỨ HAI của cùng một định nghĩa**, và hai bản
cài đặt cho một khái niệm thì sớm muộn cũng lệch — đúng khuôn mẫu đã sinh ra
F4 (hai danh sách quy tắc CTR), khoảng trống "ảnh bìa" (hai bảng bí danh) và lỗ
bí danh của `CTR_SUBJECT`. Một trigger băm-lại bị lệch còn nguy hiểm hơn không
có trigger: nó sẽ TỪ CHỐI những hàng hợp lệ và tạo áp lực nới lỏng.

### Hệ quả, nói thẳng

* Đường ghi BÌNH THƯỜNG an toàn: `composite.ts` đọc lại bản khai từ database và
  băm lại trước khi cấp phép; có test cho ca băm sai.
* Đường ghi BẤT THƯỜNG (script SQL trực tiếp) **có thể** lưu một hàng bản khai mà
  `payload_hash` không khớp `payload`, miễn là ba trường lineage đúng. Trigger
  sẽ không chặn.
* Vì vậy: **hiện vật chính thức chỉ đáng tin ở mức "được sinh ra bởi đường ghi
  của ứng dụng"**. Ràng buộc database thu hẹp rất nhiều, nhưng không thay thế
  được điều đó — cùng kết luận với mục 1 (bản ghi có kỷ luật, không phải
  attestation) và với ghi nhận rằng ràng buộc database không chống được superuser.
