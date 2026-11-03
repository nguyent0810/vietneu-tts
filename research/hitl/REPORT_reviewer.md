# #127 Reviewer chỉ gắn cờ

## Phạm vi

Đã thêm reviewer research-only tại `research/hitl/reviewer.py`. Tái dùng `_facts`, `_verified`, `_text`, `_names_in`, `_norm` và `_configured_model` từ `research.fact_store.simple.pipeline`; không sửa `reviewer_prompt_v2.md` và không đụng `research/hitl/history/`. Reviewer không tạo quyết định duyệt và output không có trường `verdict` hay biến thể accept/approved.

## Hành vi

- Đọc một file JSON hoặc mọi `*.json` trong thư mục; mỗi video lấy store và verification theo `topic_id` từ `--stores`.
- Chọn fact theo entity và `claims[].fact_ids`, rồi mở rộng quan hệ `conflicts_with`, `variant_group` và `comparable_group` theo cả hai chiều. Fact chưa có verification được gắn `unverified`; phía liên quan mâu thuẫn được gắn `conflicting: true`.
- Giới hạn mặc định 32 facts / 36.000 ký tự; mọi `fact_id` bị loại được ghi vào `sources_truncated`.
- Gọi `codex exec --json --skip-git-repo-check -s read-only -` theo batch; tính token từ `turn.completed.usage` gồm input, output và reasoning, giữ riêng cached input, thời lượng và model. Model cấu hình được lấy qua helper của pipeline simple.
- Báo lỗi parse/CLI/timeout và ID không hợp lệ trên record bị ảnh hưởng; thiếu candidate trong phản hồi được đánh dấu `review_failed`. Phản hồi ID thừa/trùng được báo trong `failure_reason`. Candidate được giữ riêng theo video.
- Mã cờ ngoài prompt được giữ với `unknown_code: true`; evidence có `source_id` không được gửi kèm được giữ và đánh dấu `evidence_invalid: true`. Không có nguồn thì mọi candidate nhận `missing_source` mức `high`.

## Chạy

```sh
python -m research.hitl.reviewer <candidates.json|dir> --stores research/fact_store/pilot/stores_fixed --out review.json [--batch 3] [--timeout 600] [--replay replay.json]
```

Replay có thể chứa object `{"videos": [...]}` hoặc list record video cùng cấu trúc. CLI trả `review_status: review_failed` thay vì dừng với lỗi runtime ở từng batch.

## Kiểm tra

Đã chạy `python3 -m unittest research.hitl.test_reviewer -v`: 9 test đạt. Bao gồm replay JSON hỏng, timeout, record không phải object, ID thiếu/trùng, candidate thiếu trong phản hồi, không có nguồn, conflict chưa verified được gửi, kết quả batch không rò giữa video, không có trường verdict và đọc usage từ `turn.completed`.

Đã kiểm tra `python3 -m research.hitl.reviewer --help`. Chưa gọi Codex CLI live; kiểm tra CLI được thực hiện bằng replay/mock để không phụ thuộc mạng.

## Fix round 1

- Bản vá phản hồi candidate: record không phải object, thiếu/ID rỗng, ID trùng hoặc ID lạ đều đặt `review_status: review_failed` và thêm nguyên nhân tương ứng vào `failure_reason`; các candidate thiếu trong câu trả lời vẫn nhận cờ `review_failed`. Có regression tests cho từng loại record/ID phản hồi.
- Bản vá hạch toán batch: `tokens`, `input_tokens`, `output_tokens`, `reasoning_tokens` và `cached_input_tokens` được chia đều theo video, phân phối phần dư để tổng phần mỗi video bằng tổng batch. Các tổng batch được ghi đúng một lần trên record video đầu tiên bằng các trường `batch_*_total`.
- Kiểm tra: `pytest -q research/hitl/test_reviewer.py` đạt 12 test. Lệnh toàn repo `pytest -q` không qua collection vì môi trường thiếu dependencies như `soundfile`, `scipy` và `sea_g2p` (26 lỗi collection; 6 skipped), không phải lỗi test reviewer.
- #132: workspace này không có implementation cho `decision.json`, content hash/version hay Markdown output cần sửa; các lần tìm chỉ thấy tài liệu thiết kế trong `docs/content-hub`. Vì vậy vòng này chỉ sửa code #127 hiện diện trong branch, không tạo implementation #132 ngoài phạm vi code có sẵn.
