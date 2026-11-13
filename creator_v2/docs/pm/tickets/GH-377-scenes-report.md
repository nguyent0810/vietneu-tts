# GH-377 — Báo cáo cảnh CK bài 11 (ck-c8-10-trieu-mua-duoc-gi)

Bộ sinh: `data/long/ck-c8-10-trieu-mua-duoc-gi/gen_scenes.py` (khuôn bài 10). Đã ghi cảnh vào ch00–ch07.json và spec.json (UTF-8, không dùng PowerShell).

## Số cảnh
ch00: 14, ch01: 14, ch02: 13, ch03: 12, ch04: 18, ch05: 16, ch06: 14, ch07: 12 · tổng 113 cảnh · 16 loại cảnh · kinetic 6% · chữ nền trống 0%.

## Kiểm tra
- `scripts/check_scene_durations.py`: mọi kiểm tra không phụ thuộc audio sạch (scene_params, lint html, craft, ledger, bars, counter, mốc neo, floor/idcards). Thời lượng thật chưa kiểm được vì chưa có TTS: kiểm bằng timing GIẢ LẬP (4,8 từ/giây, nghỉ 0,3 s, 1 s ở câu có ‖) đặt ngoài repo; kết quả 0 lỗi, cảnh ngắn nhất 3,0 s, dài nhất 8,0 s. Cần chạy lại sau TTS thật.
- `opening_gate`: 0 lỗi (clip ở giây 0, mọi cảnh 5 chương mở đầu có nền).
- `scripts/long_gate.py`: chỉ còn lỗi "chưa TTS".
- Giấy phép Commons kiểm lại bằng API Commons (bên dưới). CK cấm ShareAlike: không có ảnh BY-SA.

## Ảnh (mỗi khóa dùng tối đa 3 lần; một số khóa trỏ cùng một tệp)
| khóa | nguồn | giấy phép | số lần |
|---|---|---|---|
| ai01 | EXT:ai:ai_01 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai02 | EXT:ai:ai_02 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai03 | EXT:ai:ai_03 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai04 | EXT:ai:ai_04 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai05 | EXT:ai:ai_05 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai06 | EXT:ai:ai_06 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai07 | EXT:ai:ai_07 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai08 | EXT:ai:ai_08 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai09 | EXT:ai:ai_09 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai10 | EXT:ai:ai_10 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai11 | EXT:ai:ai_11 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai12 | EXT:ai:ai_12 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai13 | EXT:ai:ai_13 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai14 | EXT:ai:ai_14 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai15 | EXT:ai:ai_15 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| ai16 | EXT:ai:ai_16 | no restrictions (ảnh AI minh họa chung, kho chung) | 3 |
| hn4 | File:Ho Chi Minh City Opera House (53668610660).jpg | CC BY 2.0 (Hans Brian Brandsberg Berg) | 3 |
| hn5 | File:20190923 Independence Palace-13.jpg | CC0 | 3 |
| hn6 | File:Ho Chi Minh City Skyline at Night.jpg | CC0 | 3 |
| hnx | File:Ho Chi Minh City Skyline.jpg | CC0 | 3 |
| hose1 | File:Ho Chi Minh stock exchange.jpg | CC0 | 3 |
| hose2 | File:Ho Chi Minh stock exchange.jpg | CC0 | 3 |
| hose3 | File:Ho Chi Minh stock exchange.jpg | CC0 | 3 |
| hose4 | File:Ho Chi Minh City during sunset (50332857462).jpg | Public domain | 3 |
| sky1 | File:Ho Chi Minh City Skyline.jpg | CC0 | 3 |
| sky2 | File:Ho Chi Minh City Skyline at Night.jpg | CC0 | 3 |
| sky3 | File:Ho Chi Minh City during sunset (50332857462).jpg | Public domain | 3 |
| sky4 | File:DJI 0212-HDR-Pano (cropped).jpg | CC BY 2.0 (Lê Minh Phát) | 3 |
| vault2 | File:NTS - Bank Vault - after 2.jpg | Public domain | 3 |

URL Commons: hose1-3 = https://commons.wikimedia.org/wiki/File:Ho_Chi_Minh_stock_exchange.jpg (CC0, Syced) · hose4/sky3 = https://commons.wikimedia.org/wiki/File:Ho_Chi_Minh_City_during_sunset_(50332857462).jpg (Public domain) · hnx/sky1 = https://commons.wikimedia.org/wiki/File:Ho_Chi_Minh_City_Skyline.jpg (CC0, Pimnl) · sky2/hn6 = https://commons.wikimedia.org/wiki/File:Ho_Chi_Minh_City_Skyline_at_Night.jpg (CC0, Tran Van Ngoc) · vault2 = https://commons.wikimedia.org/wiki/File:NTS_-_Bank_Vault_-_after_2.jpg (Public domain) · hn4 = https://commons.wikimedia.org/wiki/File:Ho_Chi_Minh_City_Opera_House_(53668610660).jpg (CC BY 2.0) · hn5 = https://commons.wikimedia.org/wiki/File:20190923_Independence_Palace-13.jpg (CC0) · sky4 = https://commons.wikimedia.org/wiki/File:DJI_0212-HDR-Pano_(cropped).jpg (CC BY 2.0).

Ảnh/clip AI minh họa chung (`EXT:ai:ai_NN`, 900002–900006) lấy lại từ kho đã soát ở bài 10; chưa có tệp trong `output/long/ck-c8-10-trieu-mua-duoc-gi/` (img/ai, img/*.jpg, broll/). Cần chép từ `output/long/ck-c7-mo-tai-khoan-phi/` (hoặc kho chung) trước bước html.
Clip dùng: 900002 x1, 900003 x1, 900004 x1, 900005 x2, 900006 x2 (tối đa 2 lần).

## Việc còn lại / lưu ý
- Chưa có TTS nên chưa soi bằng mắt; cảnh ghép 2 câu dài 7–8 s có thể vượt 9 s nếu giọng chậm hơn 15%.
- `publish_at` đặt tạm 2026-12-07T13:00:00Z (Thứ Hai 20:00 VN); Lead kiểm lịch trước khi upload. Tiêu đề chọn phương án 1 của plan.
- Không dùng cảnh `file`/idcard và cảnh `brand` ở bài này.
- Kịch bản ch02 câu 9 viết "vượt khoản tiền giả định của chị hai triệu" (nghĩa là vượt hai triệu); cảnh hiển thị 12 triệu so với 10 triệu: Lead cân nhắc sửa lời.
