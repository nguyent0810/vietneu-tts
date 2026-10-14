# HF Director chỉ xuất figure ngữ nghĩa, renderer sở hữu toàn bộ phần trình bày

Director đọc kịch bản và quyết định *nên biểu diễn câu này bằng gì*
(`{type, data, confidence, source}`); `engine.js` quyết định *vẽ ra sao* — toạ
độ, tỉ lệ, cỡ chữ, định dạng số. `hyperframes_bridge.py` chỉ chuyển tiếp figure
xuống, không tính props và không hiểu hình học. Chọn vậy để đổi cách hiển thị
chỉ phải sửa một nơi, và để quyết định của director còn đọc được sau sáu tháng
khi thiết kế đã đổi vài lần.

## Considered Options

Cho Python tính sẵn props (`at_percent`, nhãn, toạ độ) rồi đẩy xuống JS. Bị loại
vì mỗi lần đổi bố cục sẽ phải sửa cả Python lẫn CSS/JS, và plan sẽ đầy số đo —
thứ không ai review nổi.

## Consequences

Python mất khả năng suy ra "figure này vẽ có hợp lý không". Bù lại bằng
`hf_figure_schema.json` (ADR-0004 nếu cần tách riêng): Python validate theo
schema, JS đọc cùng schema đó. Schema phải `additionalProperties: false` —
typo kiểu `threshhold` không được lặng lẽ lọt qua rồi biến mất ở frame render.
