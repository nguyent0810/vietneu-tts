# Issue tracker: Local Markdown

Spec và ticket của repo này nằm dưới dạng file markdown trong `.scratch/`. Chưa đưa lên GitHub Issues khi chủ repo chưa duyệt.

## Quy ước

- Mỗi feature một thư mục: `.scratch/<feature-slug>/`
- Spec: `.scratch/<feature-slug>/spec.md`
- Ticket: mỗi ticket một file `.scratch/<feature-slug>/tickets/<NN>-<slug>.md`, đánh số từ `01`, không gộp nhiều ticket vào một file
- Trạng thái ghi bằng dòng `Status:` ở đầu file ticket
- Phụ thuộc ghi bằng dòng `Blocked by: NN, NN`
- Bình luận/lịch sử thêm vào cuối file dưới heading `## Comments`
- Tài liệu làm việc khác của feature (research, interview, decisions, quality models, test matrix) nằm cùng thư mục feature

## Khi một skill nói "publish to the issue tracker"

Tạo file mới dưới `.scratch/<feature-slug>/` (tạo thư mục nếu cần).

## Khi một skill nói "fetch the relevant ticket"

Đọc file ở đường dẫn được nêu. Người dùng thường đưa đường dẫn hoặc số ticket.

## Chuyển sang GitHub

Chỉ chuyển ticket sang GitHub Issues của `nguyent0810/vietneu-tts` khi người dùng duyệt rõ ràng từng lần.
