# `hf_figure_schema.json` là hợp đồng liên ngôn ngữ cho semantic figure

ADR-0001 tước quyền "biết vẽ" của Python và trao toàn bộ phần trình bày cho
`engine.js`. Hệ quả là không layer nào còn tự mình biết **figure thế nào là hợp
lệ**. `hf_figure_schema.json` giữ vai trò đó: một file JSON Schema duy nhất,
Python validate theo nó, JavaScript đọc chính nó để biết hợp đồng. **Không
layer nào được định nghĩa lại contract ở phía mình** — kể cả "cho tiện".

Schema trả lời đúng một câu hỏi: *semantic figure nào hợp lệ?* Nó không trả lời
figure chiếm bao nhiêu pixel, chữ đặt ở đâu, animation ra sao — phần đó vẫn
thuộc `engine.js` theo ADR-0001.

## Schema phải khoá

- `type` (`none` · `threshold` · `flow` · `timeline` · `stat`), `data`,
  `relation`, `source`, `confidence`, và **required/optional riêng cho từng
  type**.
- `additionalProperties: false` ở mọi cấp — typo kiểu `threshhold` hay
  `pairs_wtih` phải fail ngay, không được lặng lẽ đi tiếp rồi biến mất trong
  frame render.
- `none` là một figure type **hợp lệ**, mang ngữ nghĩa "đã cân nhắc và quyết
  định không dùng hình". Nó không phải là thiếu dữ liệu, và không được biểu
  diễn bằng cách bỏ trống figure.
- `sentence_id` **nằm ở khoá của map `figures`**, không lặp lại bên trong figure
  — cùng lý do đã bỏ field `confirmed` ở ADR-0003: hai chỗ ghi cùng một sự thật
  thì sẽ có ngày lệch nhau.

## Ràng buộc quy trình

Validate xảy ra **trước render**, không phải sau. Thay đổi phá vỡ tương thích
là **contract change**: phải sửa schema, fixture, director và renderer trong
cùng một lần, không được âm thầm nới một phía.

## Không khoá

ADR này **không** chỉ định thư viện validate nào. Hợp đồng viết bằng JSON
Schema chuẩn nên bất kỳ validator đúng chuẩn nào cũng dùng được; việc chọn thư
viện là chuyện của lúc cài đặt và có thể đổi mà không đụng tới hợp đồng.
