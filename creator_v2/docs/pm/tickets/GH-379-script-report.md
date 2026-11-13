# GH-379: báo cáo kịch bản `mim-binance-6-3-ty-20-phut`

Ngày: 13/11/2026. Người viết: agent Sonnet. Chưa render, chưa TTS, chưa commit.

## 1. Sự kiện lõi: ĐÃ XÁC MINH, có chỉnh

Binance bị rút khoảng 6,3 tỷ USD ngày 29/10/2026 là sự kiện có thật (Reuters qua NBC, CoinDesk, TechCrunch, The Block, Halborn, VnExpress; TRM, Elliptic, FBI qua tìm kiếm). Điểm khác so với `plan.md`:

- "20 phút" là khung của TRM Labs cho phần lớn số tiền (bắt đầu 20:05 UTC). Cả đợt rút kéo dài đến 23:56 UTC theo Elliptic. Lời đọc nói "phần lớn" và nói thẳng có đợt hai.
- Tiền bị đóng băng: 2,4 (CoinDesk) đến 2,84 tỷ (Elliptic), TRM 2,7. Không phải "3 tỷ". Phần kẻ trộm còn giữ (2,4–3 tỷ) phần lớn là ETH, BTC, không khóa được: ngược với ý "3 tỷ tiền chết trong ví hacker".
- 36 giờ = dàn dựng (nạp ví điều hành bằng Tornado Cash, chạy thử trên ba ví), không phải "lệnh thử vào hệ thống phê duyệt".
- FBI gán cho TraderTraitor (31/10), Triều Tiên (Kim Yo Jong, 02/11) phủ nhận: cả hai phía đều có trong lời đọc.

## 2. Số liệu

- 9 chương (CH00–CH08), 159 câu, 2.420 âm tiết (khoảng 10–12 phút), trong ngưỡng 2.000–3.000.
- `script_lines.py`: không có lỗi cổng. `craft.audio_problems`: `[]`. `factcheck_lint.lint`: `[]`.
- Đã ghi `ch00.json`–`ch08.json` (do `script_lines.py` sinh, chưa có cảnh).
- Gồm 3 câu `[TRÍCH DỊCH]` (FBI đề nghị chặn, Levin của Chainalysis, Richard Teng), mỗi câu có nguyên văn và URL trong `factcheck.md`.

## 3. Phần bỏ so với plan

- Đám đông "xin tiền hacker" và "gửi 1 nhận 10" (cả chương CH07 của plan): chỉ có tin nhỏ lẻ, số liệu mâu thuẫn, không đọc được bài gốc.
- Vụ DOJ nhắm 1,2 tỷ USD: không tìm ra nguồn.
- Danh sách "tám tòa soạn", BBC, The Verge, The Register, VietNamNet, VnEconomy: chưa kiểm, không dùng.
- CZ, quỹ "FIF", hàm `freeze` "nằm sâu": không có trong nguồn đã đọc.
- Cơ cấu "3,8 tỷ ETH, 1,5 tỷ BTC" ở CH01 plan: không kiểm được, bỏ (lời đọc chỉ nêu XRP 233 triệu, BTC 18.270, USDT 1,6 tỷ, ETH 167 nghìn, đều từ Halborn/VnExpress).

## 4. Rủi ro

1. Các mốc giờ chi tiết (20:24, 21:01, 21:04, 00:10) chỉ có ở Halborn. Máy không mở được fbi.gov (403), trmlabs.com và elliptic.co (không phân giải được tên miền), nên chưa đối chiếu bản gốc. Cần người xem lại nếu có thể.
2. CH07: "hai mươi hai giờ ba mươi" là giờ UTC, lời đọc không nói múi giờ. Khi dựng cảnh nên ghi UTC.
3. Sự kiện mới (13/11/2026), số có thể đổi (số bị khóa, tỷ lệ bù). Kiểm lại trước khi render.
4. Lời cuối CH08 ("chiếc chìa khóa của bạn đang nằm trong tay ai?") là câu kết tiết chế, không khuyên đầu tư hay cách bảo mật cụ thể. Người duyệt cân nhắc có cần thêm lời khuyên bảo mật hay không.
5. Chưa chạy `long_story_review.py` (ngoài phạm vi ticket); `{beat: …}` đã đặt thưa, chưa soát cửa sổ 30 giây sau TTS.
6. Tiêu đề phương án (3) dùng "2,8 tỷ" (làm tròn của Halborn); an toàn hơn là phương án (1) hoặc (2).

## 5. Tệp

- `data/long/mim-binance-6-3-ty-20-phut/script.md`
- `data/long/mim-binance-6-3-ty-20-phut/factcheck.md`
- `data/long/mim-binance-6-3-ty-20-phut/ch00.json` … `ch08.json`
