from pathlib import Path

report = '''# GH-180 vòng 3 — báo cáo phối cảnh

Đã sửa chín spec: mỗi bài có một cảnh `photo` dùng ảnh AI khác nhau, `credit: false`, có `cards3d` để hiện số so sánh lớn, và giữ nguyên lời đọc cùng các trường `hypo`/`hypo_sub`. Ảnh kho thực tế nằm ở `../output/asset_library/` so với repo; spec dùng đường dẫn `local:../output/...`. Đã mở tờ ảnh nguồn `docs/pm/tickets/GH-180-respec2-images.jpg`; chín file tồn tại và không trùng nhau. Preflight không chứng minh kết quả hiển thị.

| Bài | Loại cảnh | Ảnh AI trong `../output/asset_library/` | Preflight |
|---|---|---|---|
| ck-e5-thuong-tet-khau-tru | photo, cards3d, counter, slam, timeline | lib198/ai_22.png | OK, 132 từ, 40,0 giây ước lượng |
| ck-e6-bon-trieu-tam-rut-mot-lan | photo, counter, slam, timeline, cards3d | lib198b/ai_44.png | OK, 103 từ, 31,2 giây |
| ck-a2-mot-nua-sau-muoi-sau-nam | photo, counter, cards3d, slam, kinetic, timeline | lib198/ai_26.png | OK, 114 từ, 34,5 giây |
| ck-e5-mot-dua-tre-mot-to-dang-ky | photo, slam, cards3d, counter, timeline | lib198b/ai_31.png | OK, 130 từ, 39,4 giây |
| ck-e6-tro-cap-540-nghin | photo, counter, cards3d, timeline, slam | lib198b/ai_34.png | OK, 126 từ, 38,2 giây |
| ck-a2-thang-chin-nam-phay | photo, counter, slam, timeline, cards3d | lib198b/ai_39.png | OK, 105 từ, 31,8 giây |
| ck-dien-sinh-hoat-bac-mot-1901 | photo, cards3d, counter, slam, timeline | lib198/ai_28.png | OK, 106 từ, 32,1 giây |
| ck-ho-kinh-doanh-duoi-mot-ty | photo, slam, counter, timeline, cards3d | lib198/ai_27.png | OK, 123 từ, 37,3 giây |
| ck-tran-tro-cap-that-nghiep-26-trieu | photo, slam, counter, cards3d, timeline | lib198/ai_31.png | OK, 117 từ, 35,5 giây |

Đã chạy `python motion/stier/build.py --preflight <slug>` sau sửa cuối cho cả chín, đều exit 0. Đã chạy `PYTHONPATH=. python motion/stier/script_lint.py <slug>` cho cả chín: 0 lỗi, cảnh báo lần lượt 5, 6, 5, 7, 9, 4, 4, 12, 8; chủ yếu câu dài, thiếu móc hoặc câu cuối không hỏi; bài hộ kinh doanh có nhận nhầm trích kinh. Giữ lời theo brief.

Lệnh kiểm mất dấu của ticket gốc exit 1 vì bốn spec cũ ngoài phạm vi: `bud-bd-3-chu-khi-nghi-nhieu-v3.json`, `bud-bd-4-kieu-ban-that-v3.json`, `bud-kg-ke-5-han-thu-v3.json`, `mim-watson-toronto.json`; không có spec GH-180 trong kết quả.

Không kiểm lại các URL hoặc xác minh dữ kiện trong vòng sửa cảnh này; các điểm chưa xác minh và khác biệt lời nguồn đã ghi ở `GH-180-respec-report.md` vẫn cần Lead xem. Không render theo brief: chưa có clip sheet hay thumbnail mới, chưa kiểm được hình thực tế, chuyển động, kích thước số và độ đọc nhãn giả định ở 360 px. Cần kiểm các cổng này khi render. Không đăng, commit hay đổi lịch. Script làm việc `GH-180-respec2-work.py` là bản trung gian, không chạy lại trên spec đã sửa.
'''
Path('docs/pm/tickets/GH-180-respec2-report.md').write_text(report, encoding='utf-8')
