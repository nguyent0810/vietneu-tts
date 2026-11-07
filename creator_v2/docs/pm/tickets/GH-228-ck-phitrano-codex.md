# GH-228: sửa Short CK ck-phi-tra-no-ngan-hang-truoc-han (claim không nguồn)

## Vấn đề
Câu 3 "Mức phí này thường dao động từ một đến hai phần trăm trên số dư nợ trả sớm." không có nguồn. Nguồn duy nhất trong spec là bài Thông tư cho vay của NHNN, bài này không nêu mức phí phổ biến. Hình cũng dùng số này: stat "1% - 2%", nhãn "PHẠT 1% - 2%", counter có suffix "%".

## Việc cần làm (chỉ sửa file này)
File được ghi: `data/stier/specs/ck-phi-tra-no-ngan-hang-truoc-han.json` và báo cáo `docs/pm/tickets/GH-228-ck-phitrano-report.md`.

1. Bỏ khoảng "1-2%" khỏi lời và hình. Thay bằng điều nguồn nói được: phí trả nợ trước hạn do hai bên thỏa thuận và phải ghi trong hợp đồng hoặc thỏa thuận cho vay.
2. Nếu cần một con số cho nhịp hình, dùng ví dụ giả định có nhãn: `"hypo": true`, lời có câu "Đây là ví dụ giả định", ví dụ "giả sử phí 1,5 phần trăm trên 200 triệu trả sớm là 3 triệu đồng". Phép tính phải đúng.
3. Câu 1 "Nhiều người gom đủ tiền..." là khái quát không nguồn: đổi thành tình huống "bạn".
4. Câu 4 (lý do bù đắp chi phí vốn) chỉ giữ nếu nói là "ngân hàng thường giải thích"; nếu không thì bỏ.
5. Giữ luật mix của Short: ≥ 5 loại cảnh, ≥ 1 ảnh/video, ≥ 1 board/cards3d/map, không loại nào > 60%. Giữ `publish_at` và các trường youtube; sửa title/description nếu có nhắc 1-2%.
6. Ghi file bằng Python `encoding="utf-8"`. Sau khi ghi, chạy `grep -n "?" ` trên các dòng tiếng Việt để chắc không mất dấu.

## Tiêu chí đạt
- `PYTHONIOENCODING=utf-8 python motion/stier/build.py --preflight ck-phi-tra-no-ngan-hang-truoc-han` không lỗi.
- Không còn chuỗi "1% - 2%", "một đến hai phần trăm" trong file.
- KHÔNG render, KHÔNG enqueue, KHÔNG commit, KHÔNG đổi nhánh git.

## Báo cáo
`docs/pm/tickets/GH-228-ck-phitrano-report.md`: lời mới từng câu, kết quả preflight.
