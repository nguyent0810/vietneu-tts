# GH-228: Short CK ck-phi-tra-no-ngan-hang-truoc-han, vòng 2

Vòng 1 (`docs/pm/tickets/GH-228-ck-phitrano-report.md`) đã bỏ đúng claim 1-2%. Nhưng bài giờ không có con số nào và tiêu đề "vì sao vẫn bị phạt phí?" không được lời trả lời. Short CK phải có số lớn trên hình.

File được ghi: `data/stier/specs/ck-phi-tra-no-ngan-hang-truoc-han.json`, báo cáo `docs/pm/tickets/GH-228-ck-phitrano2-report.md`.

1. Thêm một ví dụ giả định có số, đánh dấu `"hypo": true` ở cảnh số và lời nói rõ "Đây là ví dụ giả định": giả sử còn nợ 200 triệu đồng, hợp đồng ghi phí trả trước hạn 1,5 phần trăm, trả sớm toàn bộ thì phí là 3 triệu đồng. Hiện 3 TRIỆU cỡ lớn (counter hoặc ledger), có dòng phép tính 200 triệu × 1,5% = 3 triệu.
2. Hook ≤ 9 từ, có số: ví dụ "Trả sớm 200 triệu, có thể mất thêm 3 triệu."
3. Đổi tiêu đề cho khớp lời, ≤ 60 ký tự, không hứa điều lời không trả lời (ví dụ "Trả nợ trước hạn: phí nằm ở dòng nào trong hợp đồng?"). Sửa mô tả tương ứng, giữ nguồn.
4. Giữ các câu về thỏa thuận và điều khoản hợp đồng. Không nêu mức phí "phổ biến" hay "thường". 25–35 giây.
5. Giữ luật mix (≥ 5 loại cảnh, ≥ 1 ảnh/video, ≥ 1 board/cards3d/map, không loại nào > 60%), giữ `publish_at`.
6. Ghi bằng Python `encoding="utf-8"`, kiểm mất dấu.

Đạt: `PYTHONIOENCODING=utf-8 python motion/stier/build.py --preflight ck-phi-tra-no-ngan-hang-truoc-han` OK. Không render, không enqueue, không commit, không đổi nhánh.
