# YCV-adbc — báo cáo

## Vòng 2: đã sửa gì

- `coverage_lint.py` nay chia đúng ba lớp: ảnh/clip, đồ họa động và chỉ chữ. Biểu đồ, bản đồ, counter, timeline không còn bị coi là cảnh khô.
- Cổng chính: tỷ lệ chỉ chữ và chuỗi chỉ chữ liên tiếp dài nhất. Không ảnh/clip và ảnh tĩnh dài là số liệu tham khảo, không chặn. Chuỗi không ghép qua chương; chapter có `vid` là ảnh/clip.
- Thêm lexicon theo khuôn `muc`: MIM 51 mục, CK 48 mục. Chủ thể cấm chữ, logo, gương mặt nhận ra được; CK cấm cả ngân hàng, công ty chứng khoán, hãng xe, mã và biểu tượng sàn.
- `ai_prompt.py` chọn lexicon theo `kenh`, ưu tiên cụm dài nhất trong câu giữa khoảng và tránh lặp chủ thể ở prompt kề nhau.
- Đã tạo lại `output/long/mim-ai-hallucinate/coverage_gaps.json` và `output/long/ck-d2-fomo/coverage_gaps.json`; không gọi API tạo ảnh.

## Đo lại 53 Long

Ngưỡng đề xuất: chỉ chữ **≤22%**, chuỗi chỉ chữ liên tiếp **≤17 giây**. Cột không ảnh/clip chỉ để tham khảo.

| Long | Chỉ chữ | Chuỗi chữ | Không ảnh/clip | Cổng |
| --- | ---: | ---: | ---: | --- |
| ck-2026-kenh-dau-tu | 43.49% | 34.54s | 85.62s | chặn |
| ck-a2-luong-va-lam-phat | 33.76% | 32.72s | 113.74s | chặn |
| ck-b1-mua-hay-thue | 34.43% | 24.88s | 111.38s | chặn |
| ck-b2-lai-kep | 21.37% | 15.10s | 59.30s | đạt |
| ck-b3-tra-gop-0 | 26.24% | 19.88s | 70.72s | chặn |
| ck-b4-mua-xe | 26.22% | 16.48s | 89.06s | chặn |
| ck-c1-vnindex-dung-yen | 37.88% | 31.48s | 103.82s | chặn |
| ck-c2-phien-giao-dich | 45.79% | 32.88s | 129.82s | chặn |
| ck-c3-bieu-do-nen | 38.55% | 33.84s | 118.60s | chặn |
| ck-c4-duong-trung-binh | 40.90% | 58.14s | 100.26s | chặn |
| ck-c5-co-tuc | 30.69% | 28.26s | 71.50s | chặn |
| ck-c6-gia-tran-san-t2 | 16.86% | 11.64s | 50.00s | đạt |
| ck-d1-vang-dinh | 44.49% | 38.90s | 121.50s | chặn |
| ck-d2-fomo | 53.71% | 32.84s | 96.58s | chặn |
| ck-d3-lo-khong-dam-ban | 26.70% | 24.80s | 74.26s | chặn |
| ck-e1-mua-deu-moi-thang | 31.26% | 19.36s | 79.12s | chặn |
| ck-e2-quy-khan-cap | 20.34% | 15.16s | 60.98s | đạt |
| ck-e3-no-the-tin-dung | 28.32% | 16.88s | 68.50s | chặn |
| ck-e4-bao-hiem-tien-gui | 36.37% | 42.04s | 120.70s | chặn |
| ck-e5-thue-tncn-2026 | 23.66% | 17.62s | 120.66s | chặn |
| ck-e6-luong-huu-rut-mot-lan | 29.39% | 36.90s | 114.62s | chặn |
| ck-f1-tro-cap-that-nghiep | 9.21% | 11.06s | 66.54s | đạt |
| ck-f2-vien-phi-bhyt | 18.98% | 11.72s | 65.72s | đạt |
| ck-f4-vo-chong-chia-tien | 13.84% | 14.50s | 50.60s | đạt |
| ck-i1-100-trieu-tiet-kiem-hay-vnindex | 17.31% | 14.58s | 55.20s | đạt |
| mim-ai-70 | 36.38% | 24.60s | 51.84s | chặn |
| mim-ai-chat-privacy | 45.75% | 34.66s | 76.06s | chặn |
| mim-ai-feed | 44.22% | 22.38s | 115.26s | chặn |
| mim-ai-gpu | 51.52% | 46.12s | 81.54s | chặn |
| mim-ai-hallucinate | 47.30% | 34.72s | 65.56s | chặn |
| mim-ai-jobs | 19.57% | 16.30s | 35.92s | đạt |
| mim-ai-khuon-mat | 24.15% | 21.50s | 57.14s | chặn |
| mim-ai-voice | 47.65% | 28.60s | 40.04s | chặn |
| mim-alphago-lee-sedol | 33.61% | 24.70s | 111.30s | chặn |
| mim-apollo-1202 | 34.56% | 27.18s | 105.62s | chặn |
| mim-captcha | 24.34% | 15.58s | 83.30s | chặn |
| mim-deep-blue-kasparov | 31.19% | 27.42s | 82.90s | chặn |
| mim-dich-may | 54.50% | 65.60s | 103.94s | chặn |
| mim-flappy-bird | 18.48% | 11.32s | 49.26s | đạt |
| mim-google-maps-kal007 | 38.06% | 21.52s | 91.42s | chặn |
| mim-katherine-johnson | 28.36% | 24.72s | 24.72s | chặn |
| mim-ke-huy-diet-petrov | 42.30% | 28.80s | 105.40s | chặn |
| mim-ma-qr | 24.85% | 13.08s | 61.34s | chặn |
| mim-macintosh-1984 | 32.07% | 23.92s | 31.12s | chặn |
| mim-may-choi-game | 30.97% | 32.10s | 54.30s | chặn |
| mim-may-thang-poker | 33.93% | 27.98s | 64.26s | chặn |
| mim-moneyball | 35.08% | 22.48s | 36.22s | chặn |
| mim-oppenheimer-feynman | 37.63% | 31.20s | 108.06s | chặn |
| mim-qwerty | 21.21% | 14.26s | 53.66s | đạt |
| mim-siri-susan-bennett | 36.68% | 26.44s | 65.88s | chặn |
| mim-social-network | 26.75% | 16.16s | 48.74s | chặn |
| mim-turing-bombe | 35.99% | 45.30s | 45.30s | chặn |
| mim-watson-jeopardy | 34.88% | 29.40s | 49.34s | chặn |

`python motion/long/coverage_lint.py --all` đã chạy 53 Long, trả mã 1 như dự kiến: 43 video bị chặn bởi ít nhất một cổng; 43 vượt tỷ lệ chỉ chữ, 38 vượt chuỗi 17 giây. Năm bài mốc đều đạt: `ck-f1`, `ck-i1`, `mim-qwerty`, `mim-flappy-bird`, `mim-ai-jobs`.

`ck-c3-bieu-do-nen` có khoảng không ảnh/clip 118.60 giây để tham khảo, không còn kết luận sai 425 giây hay dùng số này để chặn đồ họa động. Bài vẫn bị chặn bởi hai cổng chỉ chữ.

## Prompt bù ảnh

- `mim-ai-hallucinate`: 13 khoảng, `fallback_subject` 0/13 (0.00%).
- `ck-d2-fomo`: 8 khoảng, `fallback_subject` 0/8 (0.00%).
- Đã kiểm bằng mã: không có hai chủ thể prompt kề nhau giống nhau trong mỗi file.

Mẫu MIM:

1. “Không, những vụ khác tôi đưa ra đều có thật.” → `a row of closed unlettered case folders in a quiet archive`.
2. “Sau chữ \"ngày\" thường là một con số, rồi chữ \"tháng\", rồi một con số nữa.” → `a blank paper calendar with empty geometric date spaces and no numbers`.
3. “Phần phân tích pháp lý của nó là những lời vô nghĩa.” → `a legal research desk with blank evidence cards and sealed folders`.

Mẫu CK:

1. “Mất bốn mươi phần trăm.” → `a tilted stack of plain household blocks with a few fallen pieces`.
2. “Nghe thì nhỏ so với bây giờ, nhưng khi ấy, đó là cả một làn sóng.” → `an abstract wave of anonymous silhouettes moving through a city street`.
3. “Lần này không có khủng hoảng thế giới nào lớn như năm hai nghìn không trăm lẻ tám.” → `a quiet global cityscape under heavy rain, without signs or logos`.

Prompt đầy đủ, câu đầu/cuối và câu giữa của từng khoảng nằm trong hai file `coverage_gaps.json`. Không có khẳng định nội dung mới cần factcheck.

## Lệnh đã chạy và kết quả

- `python -m py_compile motion/long/coverage_lint.py motion/long/ai_prompt.py`: đạt.
- `python -m pytest tests/test_long_coverage.py -q -p no:cacheprovider`: **4 passed**.
- `python motion/long/coverage_lint.py --all`: chạy 53 Long; mã 1 đúng do 43 bài chưa đạt cổng.
- `python -m pytest -q -p no:cacheprovider --maxfail=1`: dừng trước test nghiệp vụ vì `PermissionError: [WinError 5] Access is denied` tại thư mục tạm `pytest-of-<user>`; đây là lỗi môi trường test.

Không render, không tạo clip sheet hoặc thumbnail, không đổi lịch, không đăng và không commit. Không còn lỗi lint/biên dịch trong phạm vi ticket.
