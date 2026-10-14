# `needs_human_figure` chặn đăng, và là trạng thái dẫn xuất từ `figures`

Câu nào mà cả rule lẫn Gemini đều không đủ chắc (`confidence < 0.6`) sẽ nhận
`type: "none"` với `source` là `rule`/`gemini`, và `sentence_id` của nó nằm
trong `needs_human_figure`. Bước đăng (`upload_*.py`) fail-closed: list không
rỗng thì thoát khác 0 và liệt kê từng `sentence_id`; không đọc/parse được plan
cũng là chặn. Render **không** bị chặn — người duyệt phải xem được video mới
quyết định được.

Nguyên tắc đằng sau: AI được phép đề xuất, nhưng một artifact công khai không
được mang chỗ trống mà không ai chịu trách nhiệm.

## Consequences

`needs_human_figure` là **trạng thái dẫn xuất**, không phải nguồn sự thật:
nó tính lại được từ `figures` (mọi figure có `source != "human"` và
`type == "none"`). `figures` mới là artifact quyết định. Hệ quả thực tế: xoá
một `sentence_id` khỏi list **không** phải là hành động duyệt — duyệt là đổi
figure đó thành `source: "human"` (kể cả khi vẫn chọn `type: "none"`), rồi list
tự rỗng đi. Bất kỳ công cụ nào chỉ sửa list mà không chạm `figures` là sai.
