# Kiểm chứng báo cáo GH-460 (giọng AI, BGM, SFX cho 5 kênh)

Ngày kiểm: 17/11/2026. File được kiểm: `2026-11-17-giong-bgm-sfx-5-kenh.md` (404 dòng, đọc hết).
Cách làm: WebFetch/WebSearch vào trang chính thức khi mở được. Mỗi dòng ghi rõ "đã mở" hay "chỉ thấy qua tìm kiếm".
Lưu ý công cụ: WebFetch tóm tắt trang bằng model nhỏ, nên các trang YouTube kênh chỉ trả về tiêu đề, không có số subs. Pixabay, Uppbeat trả 429, Artlist trả 403 nên không mở được.

Lưu ý chung: mục 8 của báo cáo ghi "(Đã xác thực)" cho cả 39 nguồn. Phần lớn nguồn đó không được xác thực: Elo/MOS không có nguồn, giá nhiều dịch vụ không khớp, tên giọng ElevenLabs/Kokoro không tìm thấy. Không tin cờ "Đã xác thực" của báo cáo.

## 1. TTS (bảng 2.1 và các giọng được đề xuất)

| Claim trong báo cáo | Verdict | Nguồn đã mở | Sửa lại |
|---|---|---|---|
| Kokoro-82M (Kokoro-Vi) Apache 2.0, "tự do thương mại hoàn toàn" | ĐÚNG MỘT PHẦN | https://huggingface.co/hexgrad/Kokoro-82M (Apache-2.0; không liệt kê tiếng Việt, chỉ "8 ngôn ngữ, 54 giọng"); https://huggingface.co/contextboxai/Kokoro-Vietnamese (Apache-2.0, "fine-tuned Vietnamese Kokoro TTS") | Bản gốc hexgrad KHÔNG hỗ trợ tiếng Việt. Tiếng Việt chỉ có ở checkpoint cộng đồng contextboxai (Apache-2.0 theo tag). Trang không nêu base model và dữ liệu huấn luyện, nên quyền thương mại của dữ liệu chưa rõ. Cần đọc LICENSE và model card trước khi dùng cho kênh kiếm tiền. |
| Giọng Kokoro-VN "mai_linh" (kênh FS) | KHÔNG CÓ NGUỒN | Trang contextboxai | Trang chỉ có ví dụ `diem_trinh`, không thấy `mai_linh`. Danh sách voicepack nằm trong `voicepacks/*.pt` (chưa mở được). Bỏ cho đến khi tự liệt kê được. |
| Kokoro RTF < 0.08, VRAM < 1.5 GB | KHÔNG CÓ NGUỒN | không | Không có benchmark nào được dẫn. Phải đo trên máy. |
| F5-TTS (Hynt ViVoice) "CC BY-NC / Open", cột giấy phép chỉ nói "lưu ý checkpoint nghiên cứu vs bản quyền dữ liệu" | SAI (mơ hồ nguy hiểm) | https://huggingface.co/hynt/F5-TTS-Vietnamese-ViVoice | Checkpoint là **CC-BY-NC-SA-4.0, "Non-commercial research use only"**, cấm cả clone giọng không có đồng ý. Không dùng cho kênh kiếm tiền. Trang không nêu license của dữ liệu Vi-Voice/VLSP. Bản F5-TTS gốc và EraX chưa kiểm, mỗi checkpoint phải xem riêng. |
| MeloTTS-Vietnamese MIT, dùng thương mại được | ĐÚNG, nhưng chất lượng đáng ngờ | https://huggingface.co/nmcuong/MeloTTS-Vietnamese (MIT, "commercial and non-commercial"); MeloTTS gốc MIT (qua tìm kiếm) | Là bản cộng đồng, fine-tune từ MeloTTS-English, huấn luyện trên Infore ~25 giờ. Chính tác giả cảnh báo dữ liệu chất lượng yếu, thiếu dấu câu, phiên âm không chính xác. MeloTTS gốc không hỗ trợ tiếng Việt. Dữ liệu Infore có license riêng chưa kiểm. MOS 4.1 là bịa. |
| Fish Speech v1.4 "Apache 2.0, tự do thương mại", tiếng Việt "ngọng thanh điệu" | SAI / CHƯA KIỂM ĐƯỢC | https://github.com/fishaudio/fish-speech | Repo hiện ghi code và weights theo **Fish Audio Community License**, S2-Pro theo **Fish Audio Research License**, không phải Apache. Trang không nêu Vietnamese trong danh sách ngôn ngữ ("khoảng một trăm ngôn ngữ"). Đừng coi là dùng thương mại tự do. Cần đọc license của đúng bản weights. |
| ElevenLabs "Cần gói Starter ($5/th)" | SAI nhẹ | https://elevenlabs.io/pricing | Starter $6/tháng (tháng đầu $1), 30.000 credits, có license thương mại. Free không có license thương mại. |
| ElevenLabs Creator $22/tháng, ~120.000 ký tự | ĐÚNG (số) | https://elevenlabs.io/pricing | Creator $22 (tháng đầu $11), 121.000 credits. Chưa kiểm credit-ký tự cho từng model (v3 và Multilingual v2 có thể tính khác nhau). Giá "$6–13 một giờ audio" là suy diễn từ số này. |
| Giọng ElevenLabs "Tung Dang", "Trung Caha", "Trieu Duong" | ĐÚNG MỘT PHẦN | Chỉ qua tìm kiếm: https://json2video.com/ai-voices/elevenlabs/languages/vietnamese/ ; trang chính thức https://elevenlabs.io/text-to-speech/vietnamese nhắc giọng "Trieu" | "Trieu Duong" có (nam, miền Nam, trẻ, giọng mềm theo json2video). "Trung Caha" có (nam trung niên). "Tung Dang" **không tìm thấy**, chỉ có "Viet DangTungDuy" (nam Bắc 30 tuổi), có thể là giọng khác. Voice library là giọng cộng đồng, có thể bị gỡ hoặc đổi điều khoản. Chưa nghe thử, mô tả "trầm ấm / đĩnh đạc" là suy đoán. |
| ElevenLabs "Eleven v3/v4", "Top 1 TTS Arena", MOS 4.6 | KHÔNG CÓ NGUỒN | không | Không có số MOS công bố. Tên model "v4" chưa kiểm được. |
| FPT.AI "Ban Mai" và "Lê Minh" | ĐÚNG | http://docs.fpt.ai/docs/en/speech/api/text-to-speech/ | API có 7 giọng: banmai (nữ Bắc), lannhi (nữ Nam), leminh (nam Bắc), myan (nữ Trung), thuminh (nữ Bắc), giahuy (nam Trung), linhsan (nữ Nam). Lê Minh là **nam miền Bắc**, không có chữ nào về "AceSound" hay "cực trầm nghiêm nghị". Đó là mô tả tự bịa. |
| FPT.AI "gói Cao cấp 2: 1.000.000 đ / 4M ký tự", ~40–60k đ/giờ | KHÔNG CÓ NGUỒN | Trang giá docs.fpt.ai (tìm kiếm) chỉ có tiêu đề bảng, không có số | Không xác nhận được. Có nguồn khác nói Voice Maker miễn phí 100.000 ký tự đầu mỗi tháng. Hỏi giá thật trực tiếp. Điều khoản thương mại/YouTube chưa kiểm. |
| Vbee "Hương Giang" | ĐÚNG MỘT PHẦN | Chỉ qua tìm kiếm: https://vbee.vn/blog/?p=16996 và trang App Store | Hương Giang có trong danh sách 18 giọng vùng miền của Vbee. Giá app: gói tháng $6.49, VIP $15.49, mua thêm 1M ký tự $8.29. Không khớp "30–50k đ/giờ". Giọng nằm ở gói nào chưa rõ. Nhãn "tốc độ 0.85 cực truyền cảm" chưa kiểm. |
| Azure vi-VN-HoaiMyNeural (nữ) / NamMinhNeural (nam) | ĐÚNG (tồn tại) | Chỉ qua tìm kiếm: https://techcommunity.microsoft.com/t5/azure-ai/azure-neural-text-to-speech-updates-51-new-voices-added-to-the/ba-p/1988418 | Cả hai là giọng neural tiếng Việt từ 2020. Chưa mở Microsoft Learn để xem danh sách giọng hiện hành. |
| Azure giá "$0.85 / 1M ký tự" (bảng 2.1) và "$16 / 1M" (mục 2.2.4) | SAI (tự mâu thuẫn) | https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/ (chỉ thấy free tier 0,5M ký tự/tháng, không thấy giá trả phí) | Hai con số trong chính báo cáo khác nhau 19 lần. Giá neural phổ biến là khoảng $16/1M, nhưng trang không hiện giá nên CHƯA KIỂM ĐƯỢC. Chi phí "1 giờ audio $0.88" cũng là từ con số $16 nhân ký tự. |
| Google Cloud: Neural2 ~$16/1M, free 1M ký tự | CHƯA KIỂM ĐƯỢC | https://cloud.google.com/text-to-speech/pricing (trang rỗng) | Trang không trả bảng giá. Chirp 3 HD thường đắt hơn Neural2, báo cáo gộp "$0.85–1.60" là không chắc. |
| OpenAI tts-1/tts-1-hd "hết hạn 01/2027" | ĐÚNG | https://developers.openai.com/docs/deprecations | Cả hai tắt ngày **06/01/2027**, thay bằng gpt-realtime-2.1-mini (Realtime API, không phải endpoint audio/speech). Kết luận thực tế: loại OpenAI khỏi danh sách. Hỗ trợ tiếng Việt của OpenAI chưa kiểm. |
| Viettel AI, Zalo AI (hàng 7, 8) | KHÔNG CÓ NGUỒN | không mở | Giá, license, MOS đều không kiểm. |
| Cột "MOS / Elo (vi-VN)" của cả 13 dòng | KHÔNG CÓ NGUỒN | https://artificialanalysis.ai/text-to-speech/methodology và kết quả tìm kiếm Artificial Analysis | Arena của Artificial Analysis có bảng riêng cho tiếng Việt (Controlled Voice Arena) nhưng không tìm được số Vi-VN nào, và nó dùng Elo, không phải MOS. Số MOS 4.0–4.6 và "Top 1 TTS Arena" là bịa. Xóa cột này. Dùng nghe mù nội bộ (mục 7 báo cáo) thay thế. |
| "ElevenLabs và FPT.AI PVC tương đương 98% diễn viên lồng tiếng" | KHÔNG CÓ NGUỒN | không | Con số 98% bịa. |
| "VieNeu Anh Khôi kurtosis 6.0–15.2, 42% khung vượt crest 6" | CHƯA KIỂM ĐƯỢC | (file nội bộ `docs/pm/2026-10-22-cl-am-thanh-set-set.md`, không đọc theo yêu cầu) | Là số nội bộ của repo, không phải nguồn ngoài. Báo cáo nhắc đúng đường dẫn nhưng tôi không kiểm khớp. |

## 2. Chính sách YouTube

| Claim | Verdict | Nguồn đã mở | Sửa lại |
|---|---|---|---|
| Đổi "Repetitious content" thành "Inauthentic content" (2025) | ĐÚNG | https://support.google.com/youtube/answer/1311392 | Ghi cập nhật 15/07/2025: đổi tên chính sách, làm rõ là nội dung sản xuất hàng loạt/lặp lại. Không ảnh hưởng chính sách "reused content". |
| "YouTube không cấm giọng AI, AI voice được bật kiếm tiền" | ĐÚNG MỘT PHẦN | cùng trang trên | Trang không nói gì cụ thể về giọng tổng hợp hay clone. Nó nói nội dung AI dựa trên mẫu chung/không gốc không đủ điều kiện kiếm tiền, và dùng AI được nếu video thể hiện tầm nhìn sáng tạo và có giá trị. **Quan trọng cho CK:** trang cũng nêu kênh dùng "AI persona" tự trình bày như chuyên gia thật về sức khỏe, pháp lý, **tài chính**, chính trị thì không kiếm tiền được. Đây là tóm tắt của công cụ, cần đọc nguyên văn trên trang trước khi coi CK an toàn (CK dùng giọng AI nói về tài chính). Báo cáo không nhắc rủi ro này. |
| Nhãn "Altered/Synthetic" không làm giảm đề xuất hay ảnh hưởng YPP | ĐÚNG | https://support.google.com/youtube/answer/14328491 | Trang ghi: "Disclosing AI content alone won't limit a video's audience or impact its eligibility to earn money." Bắt buộc khai khi nội dung chân thực khiến người thật dường như nói/làm điều họ không làm, hoặc nhạc AI là trọng tâm. Cloning giọng của chính mình để lồng tiếng và sửa/khôi phục giọng không cần khai. Giọng AI tổng quát không bắt chước người thật: trang không nói rõ, báo cáo kết luận "không bắt buộc" là hợp lý nhưng không có câu xác nhận trực tiếp. |
| "Tiền quảng cáo claim giữ ký quỹ 30 ngày" | CHƯA KIỂM ĐƯỢC | không mở trang 2797454 | Không xác nhận. |
| "-14 LUFS / -1 dBTP, phạt giảm -5 dB nếu -9 LUFS" | CHƯA KIỂM ĐƯỢC | không mở | Con số -14 LUFS là phổ biến nhưng chưa dẫn Help Center. YouTube không công bố chuẩn bắt buộc. |

## 3. BGM / SFX

| Claim | Verdict | Nguồn | Sửa lại |
|---|---|---|---|
| YouTube Audio Library "an toàn tuyệt đối 100%, không bao giờ bị claim" | ĐÚNG MỘT PHẦN | https://support.google.com/youtube/answer/3376882 | Trang ghi nhạc/SFX tải từ Audio Library "won't be claimed through Content ID" (áp dụng cho người trong YPP). Bỏ "tuyệt đối 100%". Bài loại CC cần ghi credit trong mô tả (lọc "Attribution not required" để tránh). Không phải "kiếm tiền trọn đời". |
| Pixabay: cho dùng thương mại, không bắt ghi công | CHƯA KIỂM ĐƯỢC | trang license-summary trả 429 | Không mở được. Qua tìm kiếm: Pixabay không ngăn Content ID claim, tải license certificate .txt để kháng nghị. Một số nhà soạn nhạc đã đăng ký Content ID. |
| Pixabay rủi ro claim, "HAAWK, Identifyy" | KHÔNG CÓ NGUỒN (tên đơn vị) | tìm kiếm không nêu | Rủi ro có thật, tên hai đơn vị trung gian không thấy nguồn. |
| Freesound: CC0, CC BY, CC BY-NC; cấm BY-NC khi kiếm tiền | ĐÚNG | https://freesound.org/help/faq/ | CC BY-NC không được dùng để kiếm tiền. CC BY cần ghi công. Rủi ro claim "thấp nếu lọc đúng" là nhận định, không có nguồn. |
| Incompetech: CC BY 4.0, ghi credit đúng mẫu | ĐÚNG | https://incompetech.com/music/royalty-free/faq.html | Credit mẫu: tên bài, "Kevin MacLeod (incompetech.com)", dòng license CC BY 4.0, đặt trong mô tả. Trang không nói "We Are Era", cũng không nêu giá mua lẻ. Hai ý đó chưa kiểm. Trang nhắc ISRC giúp trả lời claim. |
| Epidemic $14.99/$24.99, "tự động Safelist" | CHƯA KIỂM ĐƯỢC | https://www.epidemicsound.com/pricing/ | Trang không hiện giá. Chỉ xác nhận có gói Creator/Pro/Business và nói license trực tiếp "giúp tránh claim". Không nhắc whitelist. Lưu ý gói Creator thường giới hạn mục đích dùng, cần đọc trước khi chọn. |
| Artlist $9.99–24.99 | CHƯA KIỂM ĐƯỢC | trang giá trả 403 | Không mở được. |
| Uppbeat $6.99–14.99 | CHƯA KIỂM ĐƯỢC | trang giá trả 429 | Không mở được. |
| Audiio, Soundstripe, Envato, Sonniss/BBC (hàng 8–11) | KHÔNG CÓ NGUỒN | không mở | Giá, license, ngày cập nhật đều chưa kiểm. Riêng "Sonniss GDC miễn phí thương mại" là đúng ở mức khái quát theo hiểu biết chung nhưng chưa mở trang. "BBC SFX" thì giấy phép là RemArc, không phải thương mại tự do, nên báo cáo gộp "BBC" vào là sai. Chưa mở nguồn để chắc. |

## 4. Kênh tham chiếu

| Kênh / URL | Verdict | Ghi chú |
|---|---|---|
| @HieuTV | SAI | Trả 404. Tìm kiếm cũng không thấy kênh tài chính "Hiếu TV 1M+ subs". Mô tả giọng/nhạc của kênh này trong báo cáo (mục 4.2) là bịa. |
| @CDTeamHinhSu | SAI | Trả 404. Tìm kiếm không thấy "CD Team Hình Sự 1.5M subs". |
| @BobbyBrothers, @MonsterBox | CHƯA KIỂM ĐƯỢC | URL trả trang YouTube với tiêu đề "bobby brothers", "Monster Box" nhưng không có số liệu. Tìm kiếm không thấy kênh Việt tên đó. Subs "200k+" và "1.2M" không có nguồn. Bobby Brothers chưa chắc là phim tài liệu kinh doanh/AI. |
| @ColdFusion, @CoffeehouseCrime, @ThePlainBagel, @JCS | TỒN TẠI (theo tiêu đề), số subs KHÔNG CÓ NGUỒN | Tiêu đề trang khớp ("ColdFusion", "Coffeehouse Crime", "The Plain Bagel", "JCS - Criminal Psychology"). Số subs 4.8M/2M/1M+/6M không kiểm được. Mô tả âm nhạc/sound design của từng kênh (drone, cassette, lofi) chưa nghe, đừng coi là sự thật. Claim "Burn Water sáng tác nhạc ColdFusion" chưa kiểm. |
| @MasterPhungPhuong | CHƯA KIỂM ĐƯỢC | Trang không trả nội dung nhận diện được. "Master Phùng Phương" đang dùng làm kênh tham chiếu FS nhưng không xác nhận. |
| @PhongThuyTamNguyen | ĐÚNG MỘT PHẦN | Tiêu đề là "PHONG THỦY TAM NGUYÊN NGHỆ AN", có thể là một kênh địa phương khác với kênh "500k+ subs" mà báo cáo nói. |
| @ThichPhapHoa, @PlumVillageApp | TỒN TẠI (theo tiêu đề) | "thichphaphoa", "Plum Village App". Mô tả "chuông xoay Tây Tạng/thiền ca" là suy diễn. Plum Village App là app, kênh nội dung chính thức có thể là kênh khác. |

## Kết luận dùng được

**Dùng được (có nguồn):**
- Nghe mù A/B/C nội bộ (mục 7) là cách quyết định đúng, vì mọi con số MOS/Elo đều bịa. Nên giữ và làm thật.
- Chính sách YouTube: đổi tên sang "inauthentic content" (đúng); nhãn AI không làm giảm tiếp cận hay YPP (đúng, câu trích trực tiếp).
- ElevenLabs: Creator $22/121k credits, Starter $6; giọng "Trieu Duong" và "Trung Caha" có thật trong thư viện cộng đồng (cần nghe thử và xem điều khoản từng giọng).
- FPT.AI: `banmai` (nữ Bắc) và `leminh` (nam Bắc) có thật; Azure HoaiMy/NamMinh có thật.
- OpenAI tts-1 tắt 06/01/2027, loại khỏi danh sách.
- Nguồn nhạc: YouTube Audio Library (lọc "Attribution not required"), Freesound chỉ CC0/CC BY (nhớ ghi credit), Incompetech CC BY 4.0 (ghi credit đúng mẫu, đã có trong repo).
- MeloTTS-Vietnamese MIT dùng được về pháp lý, nhưng chỉ làm fallback sau khi nghe thử, vì train trên Infore 25 giờ chất lượng yếu.

**Phải bỏ:**
- F5-TTS ViVoice cho kênh kiếm tiền: checkpoint CC-BY-NC-SA, nghiên cứu phi thương mại.
- Cột MOS/Elo, "Top 1 TTS Arena", "98% diễn viên lồng tiếng", RTF/VRAM Kokoro, mọi con số xếp hạng.
- Giọng "Tung Dang" (không tìm thấy), "mai_linh" (không thấy), mô tả "AceSound / cực trầm" cho Lê Minh (Lê Minh là giọng Bắc thông thường).
- Kênh @HieuTV, @CDTeamHinhSu (404) và mọi mô tả âm thanh của chúng.
- Mọi cờ "Đã xác thực" ở mục 8.
- Fish Speech "Apache": license thực là Fish Audio Community/Research.

**Phải kiểm lại hoặc thử lại trước khi quyết định:**
- Kokoro-Vietnamese (contextboxai): Apache theo tag, nhưng chưa rõ base model và license dữ liệu. Đọc LICENSE, nghe thử, tự đo RTF.
- CK và rủi ro "AI persona về tài chính không kiếm tiền" của YouTube: đọc nguyên văn trang 1311392 và quyết định cách trình bày giọng/kênh. Đây là điểm quan trọng nhất báo cáo bỏ sót.
- Giá Azure/Google/FPT/Vbee: báo cáo tự mâu thuẫn hoặc không khớp. Xem lại bảng giá chính thức trước khi tính chi phí. Không cần cho local (VieNeu vẫn $0).
- Pixabay, Uppbeat, Artlist, Epidemic, Audiio, Soundstripe, Envato: chưa mở được trang giá/license. Chỉ chọn trả phí sau khi mở trang chính thức. Hiện tại Audio Library + Incompetech + Freesound CC0 đủ cho test.
- Quy trình kháng nghị Content ID, ký quỹ 30 ngày, -14 LUFS: chưa dẫn Help Center.
