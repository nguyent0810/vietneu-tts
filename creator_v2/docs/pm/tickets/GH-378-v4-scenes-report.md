# GH-378 v4: báo cáo dựng lại cảnh Long CL `cl-hoang-kim-vinh`

Phạm vi: chỉ phần cảnh (`data/long/cl-hoang-kim-vinh/gen_scenes.py`, `gen_scenes2.py`, `spec_hkv.py`, `chNN.json` phần `scenes`/`hud`/`bgm`, `spec.json`). Không đổi lời đọc (`script.md`, `lines`). Không TTS, render, upload, commit.

## Số đo (timing giả 3,7 / 4,1 / 4,4 từ/giây)

- 5.894 âm tiết, 14 chương, 316 cảnh (≈ 5,0 s/cảnh), 16 loại cảnh, 42 ảnh tư liệu có ghi công, 32 cảnh b-roll, kinetic 25%, chữ nền trống 0%.
- `check_scene_durations.py`: 0 lỗi ở cả ba tốc độ (gồm cổng floor, lint html, craft, thời lượng cảnh 2,5–9 s, con đầu ≤ 1 s).
- `scripts/long_gate.py` (với timing giả 4,1): ĐẠT (≥ 5 loại cảnh mỗi chương, ảnh ≤ 3 lần, mỗi clip ≤ 4 lần, chữ hiển thị lặp ≤ 2).
- `opening_gate.py`: không lỗi ở 3,7 và 4,1. Ở 4,4 từ/giây còn 1 lỗi thuộc KỊCH BẢN, không phải cảnh (xem mục dưới).

## Cách dựng

- Trục hình: nhân vật + cái giá. Ba bản kể lệch nhau (sách 1930, Wikipedia, phim) chỉ làm cú twist ở CH00, CH05, CH09, CH13, không làm trục.
- **Cold open (CH00):** cảnh đầu là clip toàn khung (`broll`, tuyết trên mái ngói), không thẻ chữ trước giây 10; cảnh 2–3 là ảnh có `move`; slam "HOÀNG KIM VINH" ở câu 2 (≈ giây 10–12); sau đó câu hỏi, ngày 20.05.1951 (clip), quote bản tự thú. 40 s đầu có ≥ 3 nhịp mạnh (clip, ảnh động, slam, question, quote), cảnh 2,5–6 s, tông tối (`noir`).
- **41 câu `{pd}`:** mỗi câu nằm trong cảnh có nhãn `illus` bắt đầu bằng "PHỎNG DỰNG" (cảnh clip: "PHỎNG DỰNG · MINH HỌA CHUNG"; ảnh tư liệu: "PHỎNG DỰNG · <địa điểm/thời kỳ>"). `gen_scenes.py` có hàm `kiem_pd()` đọc `script.md` và dừng nếu một câu `{pd}` rơi vào cảnh không có nhãn.
- **Nguồn quan trọng** lên `srcnote` hoặc dòng `by` của thẻ quote/`sub` (Wikipedia tiếng Anh/Trung, Hải Thượng Danh Nhân Truyện, hồi ức Wikipedia dẫn, trang Wikipedia của phim); không đọc thành lời.
- Ảnh hiện đại (`greatworld`, `tomb`) luôn có nhãn "ẢNH NGÀY NAY"; không AI người thật; clip AI chỉ là cảnh chung không người, nhãn "MINH HỌA CHUNG".
- Clip: 8 clip × 4 lần = 32 cảnh vid. Thêm `900003` (mái ngói phủ tuyết, từ `cl-luu-gu/broll`) vào `output/long/cl-hoang-kim-vinh/broll/` kèm json `minh_hoa_chung`. Trần 4 lần/clip lấy theo `round(26,3/6)` ở 4,1 từ/giây; nếu TTS thật dài hơn ≈ 27 phút thì được 5 lần (còn dư chỗ).
- Dàn nền: `chia_nen()` dàn đều các ảnh phố chung làm nền thẻ chữ (trừ CH00, nền chọn tay) để không lặp một ảnh quá 14 lần.
- Thẻ `file` 11 cảnh (3,5%), cách nhau ≥ 5 cảnh. Tiêu đề thẻ ≤ 12 ký tự hoa/dòng, slam/kinetic ≤ 16 ký tự/dòng chính, nhãn org ≤ 14.

## Spec

- `title` và `youtube.titles[0]`: "Trùm Bến Thượng Hải: Cuối Đời Tự Thú Và Cầm Chổi Quét Rác" (57 ký tự, phương án 1 đầu `script.md`).
- `publish_at` "2026-11-26T14:00:00Z" (tạm), playlist "Ngoài Đời Thật", `approved` giữ nguyên, `mix_levels` CL gain 0.27 / threshold 0.08 / ratio 3.0, thumb `t1.jpg`, `summary` viết lại theo trục mới. `chapter_titles` theo tên chương mới.

## Việc còn lại cho Lead

1. **Script CH00, câu 17–19** là ba câu hỏi liền nhau. Ở 4,4 từ/giây cả ba rơi vào cửa sổ 20 s thuộc đoạn 36–90 s nên `opening_gate.py` báo "Có ít nhất 3 câu hỏi trong cửa sổ 20s". Ở 3,7 và 4,1 qua. Chỉ sửa được ở lời đọc (đổi một câu hỏi thành câu khẳng định), nên để Lead quyết; cổng này không có mã O9/O10 trong nhánh này.
2. Cảnh báo (không chặn): từ khóa tiêu đề "Trùm Bến Thượng Hải…" chưa được nói nguyên cụm trước giây 20 (câu 2 chỉ nói "ông trùm của Bến Thượng Hải").
3. Sau TTS thật chạy lại `check_scene_durations.py` và `opening_gate.py`: timing giả chỉ xấp xỉ, đặc biệt các cảnh 2,5–3,2 s (CH00 cảnh 1, CH06 cảnh 0, CH10 cảnh 24–25) nằm sát ngưỡng.
4. Chưa dựng thử khung hình: cần `clip_sheet` / contact sheet của agy trước render (focus của `huang`, `zhang1`, `zhang2` giữ nguyên giá trị đã soi ở bản trước; ảnh dọc `tram37` đặt trong thẻ `print`).
