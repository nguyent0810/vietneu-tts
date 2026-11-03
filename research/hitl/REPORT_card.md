# Báo cáo #132 — thẻ duyệt HITL (research)

## Đã làm

- Thêm `card.py` với HTML/Markdown card, ba lệnh CLI `render`, `decide`, `verify`; kèm package và tests.
- Card hiển thị thông tin video, trạng thái review/lý do, `sources_missing`, candidate, thumbnail chữ trên vùng nền tối cao 168 px, các nhịp, payoff, góc kể và cờ reviewer. Lỗi input khi render được hiển thị thay vì làm lệnh crash.
- `decide` yêu cầu action rõ ràng; APPROVE cần đúng một `candidate_id`, REQUEST_CHANGES/REJECT cần note. Lịch sử append-only nằm trong `decisions/<video_id>/`.
- Hash candidate là SHA-256 của JSON chuẩn hóa. `verify` dựng lại candidate cuối từ `candidates.json` cùng `decision.edits`, rồi so hash. Sửa edits sau duyệt cho kết quả `stale`.
- `content_version` dựa trên lịch sử hash của file candidates: cùng nội dung giữ version dù có nhiều quyết định; nội dung mới tăng version. Mỗi quyết định có tên file riêng để tránh ghi đè.
- `verify` trả `not_approved` cho REQUEST_CHANGES/REJECT, `stale` cho hash mismatch và `invalid` cho file thiếu hoặc JSON hỏng.
- Markdown escape nội dung untrusted từ metadata, candidate, flags và lỗi.
- Mẫu sidecar CL chỉ được tham khảo; không import production.

## Fix round 1

- Đã khắc phục P1 edits-hash: verifier tính lại hash từ candidate gốc cộng `decision.edits`; có regression test đổi edits sau lưu.
- Đã khắc phục P1 version: version chỉ tăng khi hash candidates khác lịch sử mới nhất; quyết định lặp cùng nội dung giữ version, nhưng được ghi file riêng. Có regression tests.
- Đã khắc phục P2 Markdown injection/formatting bằng escaping và test heading, link, table delimiter, newline.
- Đã khắc phục P2 trạng thái action: non-APPROVE trả `not_approved`, không dùng `stale`.
- Yêu cầu #127 về video `review_status`, cấu trúc reviewer answer và phân bổ token batch không thuộc module nào trong checkout này; `research/hitl/card.py` chỉ xử lý thẻ HITL và quyết định, không chạy batch video review/token accounting. Không sửa pipeline khác ngoài phạm vi #132.

## Kiểm tra

- `python3 -m pytest research/hitl/test_card.py -q` — 10 passed.
- `python3 -m pytest -q` toàn workspace không thu thập được: 26 lỗi import dependency hiện có, gồm `soundfile`, `scipy`, `sea_g2p`; 6 tests skipped.

## Lead (vòng 2)
- `content_version` theo hash nội dung `candidates.json` trong thư mục lịch sử của từng video (mặc định `decisions/<video_id>/`). Một video chỉ có một thư mục lịch sử, nên phiên bản bắt đầu từ 1 là đúng thiết kế; đổi thư mục lịch sử là tạo một chuỗi lịch sử mới và phải ghi rõ khi vận hành.
- Hai test về version không mâu thuẫn: một test đổi nội dung (1→2), một test giữ nội dung với hai quyết định (giữ 1) rồi đổi nội dung (→2).
