# YCV-adbc vòng 2 · Đo lại "khô" và làm prompt bám theo lời đọc (Codex)

Đọc lại báo cáo vòng 1: `docs/pm/tickets/YCV-adbc-report.md`. Claude review thấy hai lỗi.

## Lỗi 1: khoảng "không ảnh" đếm cả biểu đồ là trống

**Hiện trạng.** `_scene_has_image` chỉ tính `photo`, `print` và các key `img`/`vid`/`bg`. Các cảnh dữ liệu và sơ đồ có chuyển động (`candles`, `race`, `bars`, `ledger`, `counter`, `timeline`, `map`, `org`, `chat`, `go`, `chess`, `waterfall`, `stack`, `heat`, ...) bị coi là trống.

**Hậu quả.**
- `ck-c3-bieu-do-nen` có khoảng trống 425 giây, dù đó là bài về biểu đồ nến.
- Ngưỡng đề xuất 95 giây vì thế vô nghĩa.

**Cái chủ kênh gọi là khô:** chữ trên nền trống đứng lâu. Biểu đồ động không tính là khô.

**Việc cần làm:**
1. Chia cảnh thành 3 lớp:
   - **ảnh hoặc clip:** `photo`, `print`, hoặc có `img`/`vid`/`bg`;
   - **đồ họa động:** mọi loại cảnh không thuộc hai lớp kia;
   - **chỉ chữ:** đã định nghĩa trong `TEXT_TYPES`.
2. Chỉ số chính, dùng làm cổng:
   - % thời lượng chỉ chữ;
   - **chuỗi chỉ chữ liền nhau dài nhất** (tính bằng giây).
3. Chỉ số phụ, chỉ để tham khảo, không chặn: khoảng không có ảnh hay clip.
4. Không ghép khoảng qua ranh giới chương. Thẻ chương có `vid` là đã có hình.
5. Chạy lại `--all` và đề xuất ngưỡng sao cho 5 bài mốc qua được: `ck-f1`, `ck-i1`, `mim-qwerty`, `mim-flappy-bird`, `mim-ai-jobs`.
6. Ghi số video bị chặn ở từng ngưỡng.

## Lỗi 2: prompt AI gần như giống nhau, không bám lời đọc

**Hiện trạng.** Ví dụ trong `ck-d2-fomo`, câu "Mua gì cũng lên. Không vào bây giờ thì bao giờ?" ra cảnh mặc định ("household money decision scene..."). Lý do: `fallback_subject` được dùng cho hầu hết các khoảng.

**Việc cần làm:**
1. Viết lexicon cho từng kênh, theo đúng khuôn `.ref/vietneu-main/library/assets/lexicon/chung.json`: `docs/pm/ai-image/lexicon_mim.json` và `docs/pm/ai-image/lexicon_ck.json`.
   - Mỗi mục là một cụm từ khóa tiếng Việt trong lời đọc, kèm chủ thể hình bằng tiếng Anh.
   - Ít nhất 40 mục mỗi kênh.
   - Lấy từ khóa từ `script.md` của các Long cũ cùng kênh:
     - **MIM:** mô hình, dữ liệu, chip, GPU, máy chủ, thuật toán, robot, ảo giác, dịch, giọng nói, khuôn mặt, quyền riêng tư, nghề, bàn cờ, phòng thí nghiệm, ...
     - **CK:** đám đông mua, giá tăng, hoảng loạn, lương, chợ, vàng, tiết kiệm, nợ, thẻ, bảo hiểm, bệnh viện, đám cưới, Tết, ...
   - Chủ thể không được có chữ, logo hay người nổi tiếng thật. Với CK, không có hình ngân hàng, công ty chứng khoán hay bảng điện có mã.
2. `motion/long/ai_prompt.py` dùng lexicon để chọn chủ thể theo câu trong khoảng trống, ưu tiên câu ở giữa khoảng. Hai prompt liền nhau không được trùng chủ thể.
3. Chạy lại `coverage_gaps.json` cho `mim-ai-hallucinate` và `ck-d2-fomo`. Đích: **dưới 20% khoảng phải dùng `fallback_subject`**. Ghi tỉ lệ này vào báo cáo.

## Giới hạn

Giữ nguyên các giới hạn của vòng 1 (`docs/pm/tickets/YCV-adbc-codex.md`).
- Thêm được phép ghi: `docs/pm/ai-image/lexicon_*.json`.
- Không đụng `motion/long/scene_rules.py`: một agent khác đang sửa file đó.
- Không gọi bất kỳ API sinh ảnh nào.

## Báo cáo

Ghi đè `docs/pm/tickets/YCV-adbc-report.md`, thêm ở đầu file mục "Vòng 2: đã sửa gì". Báo cáo gồm:
- bảng 53 Long theo chỉ số mới;
- ngưỡng đề xuất kèm số video bị chặn;
- tỉ lệ prompt phải dùng `fallback_subject`;
- 3 prompt mẫu mỗi kênh, kèm câu lời đọc tương ứng;
- kết quả `pytest`.
