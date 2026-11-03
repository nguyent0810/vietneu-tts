## Kết luận: **FAIL**
Các P1 về ID/span và đơn vị đã được xử lý tốt hơn. Nhưng lượt này vẫn có lỗi P1: reviewer trả JSON sai định dạng hoặc không phải JSON sẽ làm pipeline ném exception và dừng, thay vì kết quả `REVIEW`. Ngoài ra, có lỗi P2 mới về cách đọc số thập phân kiểu Việt Nam và một P2 cũ về phát hiện mâu thuẫn vẫn chưa được khắc phục.
### Các phát hiện vòng trước
| Phát hiện | Trạng thái | Nhận xét |
|---|---|---|
| **[P1] `m` khớp nhầm `km`** | **FIXED** | `_unit_identity()` chuẩn hóa đơn vị và `_quantity_matches()` so sánh identity cùng hệ số chuyển đổi; có regression test `test_unit_identity_km_does_not_support_m`. |
| **[P1] So span review quá rộng** | **FIXED** | `decide()` gắn kết quả reviewer với `span_id`, từ chối ID lạ, thiếu hoặc trùng; có test span lạ và hàng review thiếu. `spans_for()` giữ nguyên câu đầy đủ cho reviewer. |
| **[P1] Review không liên quan gỡ lỗi quy kết** | **PARTLY FIXED** | Issue cần có `span_id` hợp lệ và chỉ hàng `supported` đúng span mới có thể gỡ `unattributed_disputed`. Tuy vậy, `dropped_qualifier` vẫn được cho phép gỡ bằng kết quả `supported` của span đó; điều này còn tùy cách diễn giải yêu cầu “reviewer must not clear unresolved deterministic issues”. |
| **[P2] Thiếu số viết bằng chữ tiếng Việt** | **NOT FIXED** | `_number_tokens()` chỉ nhận số dạng chữ số. “ba mối nguy”, “hai mươi ba lý do” không được token hóa; test hiện chỉ kiểm tra số chữ như một trường hợp bằng chứng, không kiểm tra dò số chữ trong câu đóng gói. |
| **[P2] Predicate phổ biến gây false contradiction** | **NOT FIXED** | Kiểm tra predicate hiện dùng ranh giới từ, tốt hơn phép chứa chuỗi cũ, nhưng không đối chiếu thời gian của fact với câu. Fact khác thời kỳ vẫn có thể làm số liệu bị đánh dấu `contradiction` và `REJECT`. |
| **[P2] Mapping list item–store chưa được kiểm thử** | **FIXED** | Có `test_list_item_topic_mapping` kiểm tra hai topic lấy đúng store tương ứng. Test không bao phủ replay hoặc `--workers`; mã hiện xử lý tuần tự. |
### Phát hiện mới và điểm cần lưu ý
- **[P1] Reviewer trả dữ liệu không phải JSON làm crash pipeline.** `semantic_review()` ném `ValueError` khi parse thất bại; `run_package()` không bắt lỗi này. Với replay chứa JSON không hợp lệ, lệnh cũng lỗi; replay có JSON array còn có thể lỗi tại `data.setdefault(...)` trước bước kiểm tra kiểu. Không có đường fallback thành verdict `REVIEW`.
- **[P2] Số thập phân kiểu Việt Nam bị token hóa sai.** Với `3.147,3`, regex chỉ nhận một dấu phân cách thập phân: có thể tạo token `3.147` rồi token riêng `3`. Giá trị không được hiểu là `3147,3`, nên kết quả grounding có thể sai. Chưa có regression test cho định dạng này.
- **Token accounting:** `_usage()` lấy `total_tokens` hoặc cộng input/output khi thiếu tổng; `semantic_review()` giữ giá trị cuối cùng gặp trong JSONL. Điều đó xử lý được snapshot tích lũy, nhưng các tệp được rà soát không chứng minh rằng mọi định dạng event thực tế đều được nhận diện hoặc usage cuối là tổng cuối cùng.
### Giới hạn kết luận
Không mở `~/vietneu_bench_frozen`; không chạy test vì đây là lượt review chỉ đọc. `REPORT.md` ghi đã có 13 test pass, nhưng lượt này chỉ kiểm tra mã và test source, không xác minh kết quả đó.
