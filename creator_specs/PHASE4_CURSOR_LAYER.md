# Phase 4 — Tầng phân tích Cursor CLI

Nguyên tắc chi phối: **thuật toán tính sự kiện, Cursor suy luận trên sự kiện.**
Cursor không tính lại chỉ số, không bịa bằng chứng, không kết luận nhân quả.

## Ranh giới đầu vào

Cursor CHỈ nhận: gói bằng chứng đã nén (Phase 3), metadata nội dung có giới hạn,
phiên bản prompt đã duyệt, hợp đồng nhiệm vụ tường minh.

Cursor KHÔNG nhận: OAuth credential, refresh token, thông tin kết nối database,
biến môi trường ngoài allowlist, quyền truy cập repo, quyền chạy shell, kết nối
Neon trực tiếp, lịch sử chỉ số theo ngày dạng thô, dữ liệu của workspace/kênh khác.

## Kiểm soát tiến trình con (`exec.ts`)

| Kiểm soát | Cách làm |
|---|---|
| Tệp thực thi | Phân giải thành đường dẫn tuyệt đối đã bỏ symlink; ghi đường dẫn thật vào bản kê |
| Không shell | `spawn(..., { shell: false })`, argv cố định |
| Prompt | Truyền qua stdin — argv hiện trong `ps` của mọi tiến trình |
| Môi trường | Allowlist `PATH HOME LANG LC_ALL TMPDIR`; không kế thừa `process.env` |
| Thư mục làm việc | Sandbox phải TỒN TẠI, RỖNG, không phải symlink — fail-closed |
| Dọn tiến trình | `detached: true` + `process.kill(-pid)` để giết cả cây |
| Giới hạn | Timeout + trần kích thước output |
| stderr | Lọc secret TRƯỚC khi lưu hoặc ghi log |

Giới hạn đã biết và chấp nhận: `HOME` phải được truyền xuống vì `cursor-agent`
đọc thông tin đăng nhập của chính nó ở đó. Bỏ `HOME` sẽ làm hỏng xác thực. Đây
là thuộc tính của công cụ nhà cung cấp, không phải lựa chọn thiết kế của ta.

## Kiểm định output (`validate.ts`)

Chạy ĐỘC LẬP với `selfCheck` mà mô hình tự khai, và có quyền phủ quyết.

- **Cấu trúc** — Zod nghiêm ngặt, mảng có trần, phiên bản schema ghim cứng
- **Bằng chứng** — mọi id phải có trong gói; video phải thuộc đúng kênh
- **Neo bằng chứng** — mỗi phát hiện/giả thuyết/khuyến nghị phải neo được về ít
  nhất một id của GÓI. Trích chéo `F-*`/`H-*` chỉ được dùng thêm. Tự trích chính
  nó và trích dẫn vòng tròn đều bị chặn
- **Nhân quả** — cấm tuyệt đối ở phần khẳng định; ở giả thuyết phải có rào đón,
  xét theo TỪNG CÂU
- **CTR/impressions** — cấm mọi kết luận khi độ phủ bằng 0; ngoại lệ "đang nói
  về việc thiếu dữ liệu" xét theo TỪNG CÂU
- **Chất lượng** — phát hiện không bằng chứng, P0 không bằng chứng, tin cậy vượt
  độ phủ, chỉ số bịa (rpm/cpm/revenue)

ĐẠT đòi hỏi **không còn BLOCKER và không còn HIGH**.

## Chính sách thử lại

Chỉ thử lại với thất bại KỸ THUẬT: JSON hỏng, sai schema, CLI lỗi, timeout.

Thất bại NỘI DUNG — câu nhân quả, kết luận CTR, bằng chứng không neo được, lỗi
chất lượng mức HIGH — **không bao giờ** được thử lại. Thử lại vì kết luận không
vừa ý sẽ biến chữ "đạt" thành thước đo độ kiên nhẫn của vòng lặp chứ không phải
thước đo bằng chứng. Tối đa: 1 lần đầu + 2 lần sửa.

## Nguồn gốc

Mọi kết quả neo vào workspace + kênh + lần phân tích + lần chạy + băm gói + băm
prompt, **do ràng buộc database cưỡng chế**, không phải quy ước ứng dụng:

- `cursor_request_package_lineage_fk` buộc gói thuộc đúng (workspace, lần chạy, kênh)
- Kết quả khoá theo LẦN CHẠY nên các lần lặp lại không ghi đè nhau
- Kết quả bất biến sau khi chốt (trigger)
- Mọi lần thử đều được giữ, kể cả lần hỏng

## Đã kiểm chứng

- 171 test tự động (unit + integration trên PostgreSQL thật)
- Chạy thật trên cả 3 kênh
- Đo độ ổn định: cùng gói + cùng prompt, chạy lặp lại

## Giới hạn còn lại (backlog, không chặn Phase 5)

- Prompt bị lược do giới hạn kích thước: phần lược bỏ được ghi vào metadata
  nhưng chưa nêu tường minh trong prompt cho mô hình biết
- `schema_version` và `payload_hash` của kết quả là quy ước ứng dụng, database
  chưa tự kiểm
- Băm prompt SỬA LỖI chưa lưu riêng theo từng lần chạy
