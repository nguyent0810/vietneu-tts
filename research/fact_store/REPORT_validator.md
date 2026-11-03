# Báo cáo Ticket #123 — validator v0.2

## Tệp triển khai

- `research/fact_store/__init__.py`: `validate_store`, chuẩn hóa và `span_match`, `compute_verification`.
- `research/fact_store/__main__.py`: CLI `validate`/`verify`, thống kê và hash file store gốc.
- `research/fact_store/test_validator.py`: 7 kiểm thử offline.
- `research/__init__.py`: package marker để `research.fact_store` import được.

## Kiểm tra

Lệnh: `pytest -q research/fact_store/test_validator.py`

Kết quả: **7 passed**.

Lệnh: `python3 -m research.fact_store --help`

Kết quả: CLI hiển thị `validate` và `verify`.

Lệnh: `python3 -m research.fact_store validate /does/not/exist`

Kết quả: báo lỗi file không tồn tại (exit 1), xác nhận CLI trả lỗi đầu vào.

`verify` xác thực store trước, từ chối independent_llm khi model trùng extraction.by (hoặc extraction_model khai báo không khớp), ghi hash SHA-256 bytes của store JSON và xác thực output với `verification.schema.json`. `span_match` yêu cầu span đã chuẩn hóa dài ít nhất 12 ký tự; snapshot phải hash khớp `sources_index.json`. Offset là vị trí ký tự Unicode trong văn bản đã chuẩn hóa NFC/khoảng trắng/dấu nháy. `comparable_group` tự nó không làm certainty thành contested; `variant_group` thì có.

## Ghi chú schema/README

1. `README.md:18` nói `store_sha256` là hash file trích xuất. Hàm API nhận object nên dùng hash JSON canonical hóa; CLI dùng hash bytes file thực tế, phù hợp hơn với hợp đồng. Khác cách serialize có thể làm hai hash khác nhau dù object tương đương.
2. `README.md:20` yêu cầu cross_source publisher khác publisher evidence gốc. `sources_index.json` không có publisher và `fact_store.schema.json` định nghĩa publisher là tùy chọn (`fact_store.schema.json: source`); kiểm publisher dựa trên metadata `store.sources`. Check phải kèm publisher khác publisher evidence.
3. `fact_store.schema.json` cho `sources[].snapshot_path` tùy chọn và không đảm bảo snapshot/hash hiện diện dù README.md:18 mô tả sources có snapshot + sha. Index hiện có một mục bị chặn với `snapshot_path=null`, `snapshot_sha256=null`; mục này không thể làm evidence hỗ trợ.
4. `qualifiers.condition` schema chỉ bắt buộc `text`; `applies_when` và `outcome` là tùy chọn. `predicates.json` lại yêu cầu hai trường này cho `rule_traditional`; validator áp nghĩa vụ predicate khi `needs` khai báo.
5. README.md:35 phân loại disputed khi có variant/conflict hoặc checks trái nhau, còn rejected khi span thiếu/contradict. Quy tắc giao nhau chưa được định nghĩa rõ. Cài đặt ưu tiên status rejected nếu span không hỗ trợ hoặc có contradiction; certainty vẫn contested nếu fact thuộc variant/conflict.
6. README.md:36 nói variant/conflicts_with “khác giá trị”, nhưng schema không có cách khai báo hoặc xác định phép so sánh giá trị; implementation xem mọi variant_group/conflicts_with là contested. `comparable_group` được giữ riêng và cần ít nhất hai fact cùng measure/unit.
7. `verification.schema.json` định nghĩa cấu trúc checks nhưng không ràng buộc thời gian ISO, hash SHA-256 đúng định dạng, hoặc uniqueness fact_id; JSON Schema cũng không thể đối chiếu model/publisher/source. Validator xử lý kiểm model và metadata cross-source ở lớp semantic; các check do caller cung cấp vẫn phải tự khớp một trong các dạng schema khi output được xác thực.
8. `fact_store.schema.json` mô tả object string có thể là entity_id hoặc literal; chỉ `object_is_entity` phân biệt và trường này không bắt buộc. Vì vậy kiểu object chỉ kiểm được khi cờ được cung cấp; predicate có ràng buộc object sẽ báo lỗi nếu literal không hợp lệ.

Chưa tạo dữ liệu kiểm chứng LLM/cross-source, không truy cập mạng và không gọi LLM.
