# GH-378: báo cáo bước 2–3 Long CL "Hoàng Kim Vinh Ngoài Đời Thật" (13/11/2026)

Người làm: Claude (Sonnet), theo brief của Lead. Chưa render, chưa TTS, chưa commit, chưa chạm YouTube.

## 1. Ảnh (bước 2)

- `output/long/cl-hoang-kim-vinh/research.json`: **141 ảnh** tự do (sau hai lượt chạy `research_long.py`), kèm `sheet_0..3.jpg`.
- Lượt 1 (14 bài Wikipedia): 105 ảnh. Lượt 2 (6 truy vấn Commons): thêm 36 ảnh.
- Giấy phép: Public domain 53+ ảnh, còn lại CC BY / CC BY-SA (cần ghi công), 1 CC0.
- **Phải lọc tay trước khi dùng:** ~31 ảnh đến từ bài Tưởng Giới Thạch (phần lớn không liên quan), và truy vấn "Zhang Xiaolin", "Huang Jinrong" kéo về ảnh rác (khủng long, chim, sợi alginate, ảnh phiên âm trùng tên). Ước tính còn khoảng 95–105 ảnh dùng được. Vượt ngưỡng 50 của CLAUDE.md.
- **Ảnh nhân vật trực tiếp rất ít:** File:黄金荣肖像.jpg (PD), File:Huangjinrong Cangku.JPG (CC BY-SA 3.0, kho hàng), File:Zhang Siaolin.jpg và File:民國·張嘯林.png (PD), File:Tomb of Du Yuesheng.jpg. **Không có ảnh Đỗ Nguyệt Sanh thời trẻ** trong kết quả, và không có ảnh Hoàng quét đường 1951. Phần còn lại là bối cảnh: Đại lộ Nam Kinh, Tô giới Pháp, cảnh sát Annam tô giới Pháp, cảnh sát Ấn tô giới, Bund, Đại Thế Giới, ảnh chặt đầu 1927 (PD, nặng, cân nhắc trước khi dùng).
- Ba tên file plan Flash đưa (Garde municipale 1900, Great world in 1930s, Opium den) không tìm thấy trong kết quả (đúng như cảnh báo 404 trong `plan.md`).

## 2. Kịch bản (bước 3)

- `data/long/cl-hoang-kim-vinh/script.md`: 14 chương (CH00 đến CH13), **5.715 âm tiết** theo `script_lines.py` (ước khoảng 29 phút). Trong khoảng 5.500–6.800; không dư nhiều, nếu Lead muốn thêm đệm thì thêm vào CH05, CH12.
- Góc kể khác Long `shanghai`: không kể lại tiểu sử Đỗ Nguyệt Sanh. Trục là "bốn mốc, bốn cách người ta kể về ông": trang sách 1930, bản kể đêm bị bắt 1924, vụ mua Đại Thế Giới 1931, bản tự thú 1951. Phát hiện làm nên chương 9: ba mục (Hoàng, Đỗ, Trương) của cuốn *Hải Thượng Danh Nhân Truyện* (1930) đều không nhắc Thanh bang, trong khi mục Đỗ và mục Trương gọi cuộc thanh trừng 1927 là việc ba người "thực sự chủ trì" và "huyết chiến một đêm"; mục Hoàng cùng năm ấy gọi là "một đêm quét sạch" để giữ tô giới.

| Chương | Âm tiết | Câu |
|---|---|---|
| CH00 Mở đầu | 194 | 12 |
| CH01 Lộ trình | 233 | 16 |
| CH02 Đứa trẻ Tô Châu | 469 | 34 |
| CH03 Chiếc ghế của người thám tử | 433 | 29 |
| CH04 Một trang sách năm 1930 | 468 | 32 |
| CH05 Thứ hàng nằm trong kho | 228 | 16 |
| CH06 Tam Hâm và cậu học trò | 402 | 29 |
| CH07 Người đào hát và đêm bị bắt | 514 | 36 |
| CH08 Khu vườn ở Tào Hà Kính | 425 | 30 |
| CH09 Mùa xuân 1927 | 557 | 32 |
| CH10 Đại Thế Giới | 575 | 34 |
| CH11 Người ở lại | 493 | 35 |
| CH12 Bản tự thú | 418 | 28 |
| CH13 Kết | 306 | 20 |
| **Tổng** | **5.715** | **383** |

## 3. Kết quả các cổng

- `python motion/long/script_lines.py cl-hoang-kim-vinh`: **qua** (không lỗi; ghi lại `ch00..ch13.json`). Còn cảnh báo không chặn: SOURCE_DENSITY (nhiều chương nêu "Wikipedia/bách khoa"; cố ý, vì mọi chỗ có số đều phải nói rõ nguồn thứ cấp), NHAY_MOC (dòng thời gian nhiều năm), NHIP_30S (cửa sổ chưa có beat, đã gắn ~20 `{beat:}`), RAO_NGUON ch09 câu 15–21, META_NGUOI_KE ch04 câu 31.
- `craft.audio_problems(script_lines.parse(...))`: **[]**. Câu dài nhất 32 âm tiết. Có câu hỏi trong 8 câu đầu, gọi "bạn", có nghỉ dài ‖.
- `factcheck_lint.lint('cl-hoang-kim-vinh')`: **[]**. 15 dòng `[TRÍCH DỊCH]` trong bài, đều có dòng trong `factcheck.md` với "TRÍCH DỊCH", "nguyên văn:" và URL cùng dòng.
- Chưa chạy: `long_story_review.py` (bước review câu chuyện, việc của Lead sau bước này), `plan_sources.py`.

## 4. Dữ kiện đã xác minh và đã bỏ

**Đã xác minh (mở thật, nguồn trong `factcheck.md`):** 1868 Tô Châu; học việc 1884; vào sở 1892 (W1, W2) hay 1900 (bài phổ thông), lời đọc nói rõ lệch; tô giới Pháp 6/4/1849 và các lần mở rộng 1900, 1914; Lâm Quế Sinh 1900; Tam Hâm 1918; Lộ Lan Xuân 1922; Lư Tiểu Gia và vụ bắt giữ 1924; Ba Đại Hanh; nghỉ việc: ba cách kể (1924, 1925, và chính cuốn sách 1930 nói mùa đông Giáp Tý xin nghỉ, mùa xuân Bính Dần được mời lại làm cố vấn); 1927 (6/4, 11/4, 12/4, 13/4); Đại Thế Giới 1917, 1928, 1931 và vụ bom 14/8/1937; trận Thượng Hải 13/8–26/11/1937; Vichy trao tô giới 30/7/1943; Trương bị bắn 14/8/1940; Đỗ rời Thượng Hải 1/5/1949, mất 16/8/1951; chiến dịch Thượng Hải 12–27/5/1949; tự thú viết 7/5, đăng 20/5/1951; mất 20/6/1953. Toàn bộ quote từ sách 1930 lấy từ Wikisource (mục Hoàng, Đỗ, Trương), mở được và có nguyên văn.

**Đã bỏ hoặc hạ thành giai thoại (nhãn rõ trong lời):**
- "Lộ Tiểu Muội" (sai tên, đúng là Lộ Lan Xuân), "bắt cóc đào hát", "trại lính Long Hoa", "tiền chuộc bạc tỷ": không có nguồn nào.
- Thập Lục Phố và Lâm Quế Sinh "mưu mô gầy dựng Thanh bang": không kiểm được.
- Tưởng Giới Thạch quỳ bái sư (chỉ thấy tiêu đề một bài báo, không đọc được nội dung).
- Cảnh quét rác "20/5/1951 trước cổng Đại Thế Giới": plan gộp hai việc. Nguồn chỉ cho phép: 20/5 đăng tự thú; mùa đông 1951 quét tầng một (chuyên mục lưu trữ quận Hoàng Phố); ảnh quét đường chỉ được một trang zh.wiki nhắc, không dẫn nguồn, chưa thấy ảnh gốc.
- Chuyện "tự dàn cảnh cướp rồi tự bắt": giữ **một lần**, gắn nhãn GIAI THOẠI (chỉ có ở bài phổ thông không dẫn nguồn).
- Mọi tả chi tiết trên các bài mạng về ngày quét rác (ai đưa chổi...), vụ "chiếc còng số 8", "tha mạng cho công chúa" kiểu plan: bỏ.
- Bình luận chính trị 1951 và "thể chế dung dưỡng tội ác" của plan: bỏ; lời đọc chỉ kể mốc có nguồn.
- Tuổi thọ (84 hay 85) và ngày sinh (14/12 hay 10/5/1868): nguồn lệch, lời đọc chỉ nêu năm hoặc nêu cả hai.

## 5. Rủi ro Lead cần quyết

1. **Không mở được nguồn sơ cấp chuẩn:** Wakeman "Policing Modern Shanghai", Martin "The Shanghai Green Gang", Virtual Shanghai; baike.baidu.com bị 403, vài trang báo Trung Quốc (thepaper, shda) không phân giải. Wakeman và Martin chỉ được biết qua chú thích Wikipedia; lời đọc luôn nói "Wikipedia ghi", không gán trực tiếp. Phần lớn nền của video là nguồn thứ cấp (Wikipedia en/zh) cộng cuốn sách 1930 (nguồn sơ cấp đương thời, nhưng là sách chân dung, không phải hồ sơ). Lead có thể giao agy Gemini hoặc Sonnet mở lại JSTOR/archive.org nếu muốn nguồn sơ cấp hơn.
2. **Số tiền "hơn một triệu đồng" (CH07)** chỉ có ở một hồi ức dẫn qua zh.wiki 盧小嘉; lời đọc đã rào. Nếu Lead thấy mỏng thì bỏ 4 câu đó.
3. **Giai đoạn 1950–1951 (CH12)** có điện Mao 21/1/1951 ("một đến hai nghìn án tử" ở Thượng Hải) làm bối cảnh; trang nguồn không nêu tên Hoàng Kim Vinh và lời đọc nói rõ điều đó. Nhạy cảm; Lead cân nhắc giữ hay cắt (chỉ cần bỏ 3 câu).
4. **Ảnh:** thiếu ảnh nhân vật (Hoàng chỉ có một chân dung PD cộng kho hàng CC BY-SA; Đỗ không có ảnh sống). Floor yêu cầu 40 ảnh: đủ, nhưng nhiều cảnh phải dùng ảnh bối cảnh. Ảnh chặt đầu 1927 và các ảnh CC BY-SA cần ghi công.
5. **Tên Hán-Việt:** dùng Trương Khiếu Lâm, Lư Tiểu Gia, Lộ Lan Xuân cho khớp Long `shanghai` đã đăng (plan Flash viết Trương Tiêu Lâm).
6. **Độ dài:** 5.715 âm tiết, sát đáy khoảng cho phép; mọi câu ≤32 âm tiết nên TTS có thể ra ngắn hơn 29 phút. Nên kiểm sau TTS.
7. **Phần thưởng giữa video:** vụ bắt giữ 1924 ở CH07 (đúng quãng một nửa); cảnh mạnh ở CH09 (ba mục sách 1930 cùng nói về đêm 1927).
8. **Bước review câu chuyện** (`long_story_review.py`) và duyệt của Lead chưa làm.
