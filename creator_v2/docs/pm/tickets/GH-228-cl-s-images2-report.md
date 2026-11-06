# GH-228 — Báo cáo thay ảnh

Đã sửa sáu spec: giữ lời đọc, thứ tự và loại cảnh; mỗi bài dùng bốn ảnh riêng, không trùng giữa các bài. Giữ chân dung tư liệu Elizabeth Short và Alger Hiss. Ảnh kho dùng credit: false. Kho nằm tại ../output/asset_library/ so với gốc repo.

## Ảnh theo bài

Các đường dẫn lib198 và lib198b dưới đây nằm trong ../output/asset_library/.

- cl-frank-grigware-van-tay: lib198/ai_56.png, lib198b/ai_03.png, lib198b/ai_02.png, lib198/ai_47.png.
- cl-black-dahlia-56-phut: File:Elizabeth-short.png, lib198/ai_49.png, lib198/ai_43.png, lib198/ai_59.png.
- cl-ross-tien-chuoc: lib198b/ai_09.png, lib198/ai_51.png, lib198/ai_48.png, lib198b/ai_10.png.
- cl-alger-hiss-khai-man: File:Alger Hiss, American statesman accused of espionage, mugs(14).jpg, lib198b/ai_13.png, lib198/ai_55.png, lib198b/ai_01.png.
- cl-diane-jackson-van-tay: lib198/ai_42.png, lib198b/ai_30.png, lib198/ai_44.png, lib198/ai_57.png.
- cl-james-ricks-ban-tu: lib198b/ai_24.png, lib198b/ai_11.png, lib198/ai_46.png, lib198b/ai_19.png.

## Kiểm tra

- Chạy python motion/stier/build.py --preflight với cả sáu slug: tất cả OK; thời lượng ước tính lần lượt 27,9; 29,1; 28,8; 27,0; 31,2; 32,4 giây.
- Chạy PYTHONPATH=. python motion/stier/script_lint.py <slug> cho từng bài: 0 lỗi; cảnh báo lần lượt 4, 8, 5, 4, 4, 7. Cảnh báo R2/R4 thiếu móc hoặc callback, R5 câu cuối không phải câu hỏi, R6 mệnh đề dài, R7 viết tắt FBI. Giữ nguyên lời theo brief; các bài có FBI có bảng đọc say.
- Kiểm tra bằng Python: mỗi bài có bốn ảnh thực sự được tham chiếu; không trùng giữa các bài; 22 ảnh kho tồn tại.
- Không kiểm lại các khẳng định có sẵn vì ticket chỉ thay ảnh; chưa xác minh lại nguồn và giấy phép hai ảnh tư liệu Commons trong lần này.
- Không render theo brief, nên không có clip sheet hoặc thumbnail mới. Không đăng, không commit, không đổi lịch.
