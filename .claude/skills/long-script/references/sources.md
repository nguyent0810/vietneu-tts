# Luật nào lấy từ đâu

Không có skill "viết kịch bản" sẵn trên chợ skill; skill này chưng cất các nguồn dưới đây + số liệu của kênh. Khi hai nguồn
mâu thuẫn, **số liệu kênh thắng** (evidence.md), sau đó tới luật kênh trong `long-video`.

| Nguồn | Lấy gì | Đổi gì cho BUD/FS + TTS tiếng Việt |
|---|---|---|
| `~/.claude/skills/hyperframes-creative/references/narration.md` | nhịp 2,5 từ/giây và "kịch bản phải ngắn hơn video"; viết như người nói, đổi độ dài câu, đọc to lên; **viết số đúng như muốn giọng đọc**; giọng làm tròn, màn hình giữ số; câu mở tạo căng / tò mò / bất ngờ, không "Chào mừng..." | nhịp đo thật 185 tiếng/phút; bảng cách VieNeu đọc số (line-rules §2); đếm tiếng ĐỌC trong lint |
| `.../story-spine.md` | móc nói ngôn ngữ người xem (kết quả, không thuật ngữ); thông điệp chạm tới chậm nhất beat 2; phép thử xoá bằng chứng / xoá thông điệp; câu chiến lược "Video này nói với [ai] rằng [thông điệp]"; hình ảnh lấy từ chính nguồn | luật 3-4 (không chương định nghĩa trước lần trả); brief §1; chi tiết giác quan phải từ nguồn (story.md §2) |
| `.../beat-direction.md` | mỗi beat là một "thế giới" có khái niệm + cảm xúc; **gọi tên nhịp trước khi viết** (fast-fast-SLOW...); điểm nhấn nặng nhất của lời đọc là đỉnh năng lượng | dòng nhịp `cảnh-HỎI-trả-chương...` ở bước 3; câu đỉnh + `pause`/`tempo` |
| `.../prompt-expansion.md` | bản nháp chỉ là hạt giống: luôn mở rộng thành đặc tả từng cảnh, thêm chi tiết vi mô, không chuyển thẳng | beat sheet bắt buộc có cột chi tiết giác quan và kỹ thuật (formats.md §6) |
| `~/.claude/skills/faceless-explainer/references/story-design.md` + `SKILL.md` | **không theo thứ tự bài nguồn**; tìm audience / gap / thesis / spine 3-6 ý / evidence / landing; chọn MỘT cấu trúc (concept / how-to / listicle / story); bảng chiến lược móc; catalog kỹ thuật (Make-concrete, Contrast, Callback...); cung cảm xúc; mỗi khung một việc; viết lời thành từng nhịp để hình lộ theo lời; quy trình có cổng | quy trình 8 bước có cổng; cột "Kỹ thuật" và "Cảm xúc" của beat sheet; Q&A (c) = listicle, Tiền Thân (a) = story-explainer, tử vi (b) = concept with process |
| `~/.claude/skills/research/SKILL.md` | điều tra trên nguồn gốc, lần mỗi khẳng định về nguồn sở hữu nó, ghi nguồn từng ý | gói nghiên cứu có nhãn `[kinh] [chú giải] [truyền thống] [sử] [code]` (bước 2, story.md §1) |
| `.claude/skills/long-video/SKILL.md` §0, §2, §3 | checklist giữ chân (rút từ RETENTION.md của Youtube_Creator_V2): câu 12-18 tiếng, ≤ 35; câu ngắn 1/4-6; ≤ 90 giây không ngắt nhịp; ≤ 3 mục; cold open; re-hook 50% / 75%; ≥ 3 vòng; motif ≥ 3; kết chương bằng cầu nối; tên chi; framing; soát kinh `hf_sutta.py`; preset C | giữ nguyên, lint gọi lại `retention_issues`, `crowded_chi_lines`, `zodiac_naming_errors` |
| `Youtube_Creator_V2/motion/long/RETENTION.md` | không còn trên máy (tìm 14/10/2026 trong ~ và thư mục nháp) -- nội dung đi vào qua long-video §2 | -- |
| Đường giữ chân B3, B5, F1, F3, F4, F6 (`evidence.md`) | 10 luật chính ở SKILL.md §0 | -- |
| `vieneu_utils.phonemize_text` (đo 14/10/2026) | cách đọc số, ngày, gạch nối, viết tắt, tên Pali | line-rules §2-3, lint `tts_*` |
| YouTube Data API (khoá FS, 7 lệnh, 14/10/2026) | cấu trúc đối thủ: Tiền Thân 1 truyện / tập, Hỏi-đáp bàn thờ, tử vi trọn đời theo giai đoạn tuổi, đêm nghe; không ai dùng mốc chương | formats.md §2-5 |
