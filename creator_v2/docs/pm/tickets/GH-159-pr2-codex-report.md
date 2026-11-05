# GH-159 PR 2 — báo cáo Codex

## Đã đổi

- `creator_v2/motion/channel_table.py`: helper nạp `library.tools.channel_profile` từ đường dẫn tương đối tới gốc repo; nạp hồ sơ Long và resolve kênh, không fallback CL.
- `creator_v2/motion/long/build_long.py`: dựng bảng CL/MIM/CK từ hồ sơ, resolve kênh một lần khi nạp spec và truyền mã viết hoa vào các cổng Long.
- `creator_v2/motion/variety.py`: dựng `CHANNEL_THEME` từ `theme.long` của hồ sơ.
- `library/channels/cl.yaml`: bỏ `theme.long`; CL không có `theme` trong bảng Long cũ.
- `library/channels/mim.yaml`, `library/channels/ck.yaml`: thêm `theme.pools: "mim"`.
- `creator_v2/data/long/{bulger,capone,escobar,golden,kowloon,mafia,ripper,shanghai,yakuza}/spec.json`: chỉ thêm `"channel": "CL"`.
- `creator_v2/tests/test_long_channel_profile.py`: snapshot bảng cũ (05-11-2026, base `6aaaf68a76d75f00df27624fe0cf1113324c3055`), `CHANNEL_THEME`, 64 spec Long và lỗi khi thiếu channel.
- `creator_v2/tests/test_mim_long.py`: các fixture CL nay khai báo `channel: CL`, vì thiếu channel phải lỗi rõ.

## CL

Đã chọn bỏ `theme.long` khỏi `cl.yaml`. Bảng tạo từ hồ sơ chỉ thêm `accent` khi có `theme.long`, nên CL vẫn không có `theme` hay `accent`, đúng bảng cũ; `typography.mau_nhan` của CL được giữ nguyên làm fallback hiện hữu.

## Kiểm tra

- `python -m pytest creator_v2/tests/test_long_channel_profile.py -q -p no:cacheprovider`: `4 passed in 1.59s`.
- `python -m pytest creator_v2/tests -q -p no:cacheprovider`: đã chạy; stdout bị cắt trước dòng tổng. Các lỗi đã thấy là Windows sandbox `PermissionError: [WinError 5]` khi pytest quét `C:\Users\Tung-QA\AppData\Local\Temp\pytest-of-Tung-QA`; các test bị lỗi môi trường trong lần chạy kiểm tra hẹp: `test_crime_channel_keeps_its_voices_theme_and_no_brand`, `test_mim_channel_gets_its_voice_lab_theme_brand_and_pools`, `test_mim_refuses_share_alike_images`, `test_bgm_picker_never_crosses_channels`, `test_long_bundle_uses_the_channel_voice`, `test_ck_routes_narrator_asker_and_quote_to_three_voices`, `test_channels_without_an_asker_read_ask_lines_with_the_narrator`.
- `python -m pytest tests/test_channel_profile.py -q -p no:cacheprovider`: `1 failed, 4 passed in 1.98s`; test cũ so sánh toàn bộ `theme` và chưa tính khóa bắt buộc mới `pools` ở MIM/CK (file này ngoài phạm vi ghi của ticket).
- `python -m compileall -q ...`: thành công. Kiểm tra trực tiếp bảng hồ sơ và 64 spec Long: `OK`.
- `git grep -n 'get("channel", "CL")' -- creator_v2/motion/long`: 0 kết quả. `git diff --check`: sạch.

Không render, không đọc credentials, không commit hay push.
