# CL_VERIFIED_PUBLIC_RECORD_SNAPSHOTS

Thư mục này chứa snapshot cục bộ (text đã lưu từ trang bản án/quyết định
công khai thật) mà **con người** đọc và tự tay lưu lại khi điền 1 entry vào
`creator_specs/CL_VERIFIED_PUBLIC_RECORD_v1.json`. KHÔNG có bất kỳ hàm nào
trong codebase này ghi vào thư mục này -- chỉ đọc, qua
`cl_risk_gate_verification.py`'s `_read_and_verify_snapshot()`.

## Quy trình điền 1 entry (thủ công, con người)

1. Tự đọc bản án/quyết định thật tại URL (vd `congbobanan.toaan.gov.vn`).
2. Lưu nội dung text của trang đó thành 1 file `.txt` (UTF-8) trong thư mục
   này, đặt tên `<case_id>__<canonical_name_ascii>.txt` (tuỳ ý, miễn duy
   nhất và không có `../`).
3. Tính sha256 của file đó:
   ```bash
   shasum -a 256 creator_specs/CL_VERIFIED_PUBLIC_RECORD_SNAPSHOTS/<file>.txt
   ```
4. Thêm 1 entry vào `CL_VERIFIED_PUBLIC_RECORD_v1.json`, key
   `"{case_id}::{canonical_name}"`, các field:
   - `url`: URL bản án gốc.
   - `verified_by`: tên người xác minh (con người thật).
   - `verified_at`: timestamp ISO 8601 hiện tại.
   - `decision_identifier`: số hiệu bản án/quyết định (bắt buộc, không rỗng).
   - `disposition`: `"convicted"`.
   - `finality_state`: `"final"`.
   - `excerpt`: đoạn trích NGUYÊN VĂN (phải là substring thật trong chính
     file snapshot ở bước 2 -- code sẽ kiểm tra cơ học, không tin lời khai).
   - `snapshot_path`: đường dẫn tương đối từ project root tới file ở bước 2
     (vd `"creator_specs/CL_VERIFIED_PUBLIC_RECORD_SNAPSHOTS/<file>.txt"`).
   - `snapshot_sha256`: hash tính ở bước 3.

## Vì sao cần snapshot + hash (không chỉ tin `excerpt` trong JSON)

Codex CLI adversarial review (round 1, C6 sidecar) chỉ ra: nếu chỉ tin
`excerpt` viết tay trong JSON, không có gì chứng minh nó thật sự thuộc nội
dung tại `url` -- 1 entry có thể dùng URL hợp lệ nhưng excerpt tự soạn/lấy
từ tài liệu khác. Snapshot cục bộ + hash + grounding cơ học (substring
check y hệt cách `case_text` được grounding-check) là artifact kiểm tra
được, không chỉ là lời tự nhận.

## Giới hạn CHƯA đóng được (residual risk đã chấp nhận có chủ đích)

Codex CLI round 2 (cùng review trên) chỉ ra: sha256 chỉ chứng minh snapshot
KHÔNG bị đổi SAU KHI được lưu -- KHÔNG chứng minh được snapshot đó THẬT SỰ
lấy từ chính `url` đã khai (cần hạ tầng fetch tự động để verify, đã loại
khỏi v1 có chủ đích vì rủi ro SSRF/prompt-injection mới). Người điền entry
VẪN LÀ mắt xích chịu trách nhiệm cho việc snapshot khớp đúng URL -- đây là
lý do file này CHỈ được con người (không phải agent tự động) chỉnh sửa.
Người dùng đã xác nhận trực tiếp chấp nhận dùng ở mức này (task #264,
2026-08-17) thay vì xây fetch tự động ngay.
