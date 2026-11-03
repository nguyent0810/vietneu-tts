# Ticket #120 — NO_LLM packaging baseline

**Phạm vi:** nhánh nghiên cứu, không production. Generator chỉ đọc `fact_table`, `contradiction`, `entity_roles`, `channel`, `format`, metadata framing để nhận diện chủ thể. Hàm nạp chủ đề không truy cập khóa `levels`; `levels.safe.title` chỉ được dùng ở bước lập bảng so sánh dưới đây. Không dùng mạng hoặc LLM.

## Cách chọn mẫu và luật

Mẫu nằm trong `nollm/templates.json`: 8 cơ chế, mỗi cơ chế có 4 title và 3 hook. Mẫu chứa slot thiếu dữ kiện sẽ bị bỏ. Chỉ fact `certainty: verified` được đưa vào provenance/slot; tên chủ đề lấy từ prefix framing khi chuỗi ấy cũng xuất hiện trong một fact verified. Fact disputed/unknown không được dùng.

Thứ tự cơ chế được quyết định bằng luật cố định:

1. Contradiction loại `factual` có fact IDs: xét `broken_expectations` và `impossible_outcome`; số chỉ lấy từ các fact verified được contradiction trỏ tới.
2. `entity_roles.compromised_system` và `harmed_org`: xét `hidden_vulnerability`/`system_failure`; Bybit được nêu là tổ chức chịu hại, Safe{Wallet} là hệ thống bị xâm nhập, thành phần gốc là JavaScript độc hại.
3. Fact verified có thời lượng và hành động: xét `impossible_outcome`.
4. Từ ngữ về thiệt hại, lựa chọn hoặc hệ quả trong fact verified lần lượt mở cơ chế human stakes, moral dilemma hoặc unexpected consequence.
5. Sinh tối đa 5 phương án theo thứ tự template cố định; ưu tiên cơ chế khác nhau trước. Điểm = +3 nếu có số +3 nếu có từ viết hoa, trừ 0,35 mỗi ký tự vượt ngưỡng độ dài, trừ 2 mỗi lần dùng gần đây cùng template, trừ 4 × Jaccard 3-gram giữa title và hook. Tie-break theo độ dài rồi template ID. History được giữ riêng theo channel.

Hook 0–3 giây lấy từ mẫu. Câu 3–10 giây hiện dùng câu dẫn “Dữ kiện đã xác nhận” kèm fact verified đầu tiên; đây là baseline bảo thủ, chưa phải bộ viết lời hoàn chỉnh. Thumbnail lấy 2–5 từ đầu title.

## Đối chiếu định lượng

So title NO_LLM với `levels.safe.title` (đọc riêng cho bước đánh giá). Specificity ở đây chỉ là tỷ lệ title có chữ số; không đo độ đúng hoặc chất lượng biên tập. N-gram là Jaccard 3-gram giữa mọi cặp title cùng channel.

| Chỉ số | Bản safe | NO_LLM |
|---|---:|---:|
| Độ dài title trung bình (ký tự) | 46,8 | 45,9 |
| Title có chữ số | 6/18 | 8/18 |
| Các cặp title trong cùng channel | — | 28 |
| Jaccard 3-gram trung bình / cao nhất | — | 0,006 / 0,176 |
| Phân bố cơ chế được chọn | — | human_stakes 7; broken_expectations 4; power_reversal 2; unexpected_consequence 2; hidden_vulnerability 1; moral_dilemma 1; impossible_outcome 1 |

Số liệu chỉ mô tả hình thức và độ trùng từ. Không có kết luận phương án nào hấp dẫn hơn; đánh giá đó để chấm mù độc lập ticket #122.

## Sáu ví dụ trước / sau

| Chủ đề | Bản safe (trước) | NO_LLM (sau) |
|---|---|---|
| Bybit | Vụ Bybit mất 1,5 tỷ USD diễn ra thế nào? | Bybit mất gì trong sự cố? |
| Fansipan | Fansipan: vì sao có hai con số độ cao? | Fansipan: 3143 m hay 3147.3 m? |
| Huyền Trang | Huyền Trang: Hành Trình Đến Ấn Độ Từ Năm 629 | Huyền Trang Và Hành Trình Thỉnh Kinh Ấn Độ Năm 629–645 và cái giá… |
| Temiya | Temiya: Hoàng Tử Giả Câm Suốt 16 Năm (Túc Sinh 538) | Sunanda làm điều ấy suốt 16 năm |
| Piprahwa | Piprahwa: Hòm Đá 1898 Và Báu Vật Liên Hệ Xá Lợi Phật | Xá Lợi Phật Piprahwa: 1897–1898 hay 5/2025? |
| Replit AI | AI của Replit xoá cơ sở dữ liệu thật | Replit AI agent và cái giá của cơ sở dữ liệu… |

## Giới hạn nhìn thấy trong lần chạy (bản trước round 1)

Đây là baseline luật mẫu, chưa phải bản đóng gói đạt chuẩn xuất bản. Một số title còn ghép slot chưa tự nhiên (đặc biệt Temiya chọn “Sunanda”, một vai từ fact khác; Huyền Trang bị cắt bằng dấu ba chấm). Nguồn dữ liệu hiện không cung cấp vai ngữ nghĩa thống nhất cho mọi chủ đề, nên các mẫu tổng quát có thể gán sai quan hệ dù từng slot có provenance. Cần mở rộng schema fact/slot và thêm kiểm tra tương thích ngữ nghĩa trước khi dùng đầu ra ngoài benchmark. Báo cáo giữ nguyên kết quả thực tế để các lỗi này hiện rõ, không tự sửa bằng tri thức ngoài fact table.

## Fix round 1

Đã thay cách gán slot bằng ràng buộc quan hệ đơn: ứng viên có câu khẳng định chỉ khi một relation verified cung cấp nguyên subject, predicate và object. Relation kiểu “được lệnh” bị bỏ qua vì subject là người nhận lệnh, không chứng minh người đó thực hiện hành động. Thời lượng chỉ được dùng nếu chính fact đó có relation đặt actor và action; fact Temiya F1 không có relation, nên không thể gán 16 năm cho Sunanda hoặc actor khác. Mẫu đối chiếu số bị tắt cho tới khi schema biểu diễn cùng subject, đại lượng và đơn vị.

Mỗi ứng viên ghi provenance triples cùng fact IDs riêng cho title, hook 0–3 giây và hook 3–10 giây. Câu 3–10 giây lấy statement từ fact hỗ trợ title/hook. Không có relation phù hợp thì đầu ra giữ tiêu đề tham chiếu chủ đề và không tạo ứng viên khẳng định. Độ dài quá giới hạn và Jaccard 3-gram ≥ 0,5 loại ứng viên trước xếp hạng. Specificity trong generator hiện chỉ là có chữ số; đây là metric hình thức, không đo độ đúng hoặc chất lượng biên tập.

| Chủ đề | Trước round 1 | Sau round 1 |
|---|---|---|
| Temiya | “Sunanda làm điều ấy suốt 16 năm” | Không sinh ứng viên: không có relation cùng fact gắn Temiya với hành động giả câm và thời lượng |
| Piprahwa | “Xá Lợi Phật Piprahwa: 1897–1898 hay 5/2025?” | Không sinh ứng viên số: schema không chứng minh cùng đại lượng/đơn vị/subject |
| Bybit | “Bybit mất gì trong sự cố?” | “Bybit: harmed — 1” (một relation verified; provenance triple kèm theo) |
| Tổng 18 chủ đề | 5 ứng viên mỗi chủ đề | 1 ứng viên có quan hệ đủ điều kiện; 17 chủ đề không có ứng viên khẳng định an toàn |

Giảm mạnh số phương án là kết quả chủ ý của nguyên tắc slot an toàn; schema hiện tại không đủ typed relation để giữ các mẫu tự nhiên. Relation tổng quát vẫn có thể nghe cứng hoặc thiếu ngữ cảnh, nên output nghiên cứu cần được gate/biên tập ở bước sau. Module không phụ thuộc `fact_gate`.

## Chạy và kiểm tra

```bash
python -m research.narrative.nollm gen research/narrative/bench114 --out research/narrative/nollm_out.json --history
python -m pytest -q research/narrative/nollm/test_nollm.py
```

Lệnh `--history` không kèm đường dẫn mô phỏng chạy tuần tự 18 chủ đề theo channel và cập nhật template history trong lần chạy. Có thể truyền file JSON làm giá trị `--history` để nạp/lưu history giữa các lần chạy.
