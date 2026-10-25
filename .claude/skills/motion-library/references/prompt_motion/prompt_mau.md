# Mẫu prompt giao thợ viết một cảnh mới

Khuôn 6 khối rút từ các prompt có cấu trúc tốt nhất trong thư viện (notdwd-7de38a, twoclipping-6dd14e, ultimaxbt-bbebf5,
daniel-haida-8691d4, gdgtify-287ddf). Điền phần trong `{{…}}`, xoá dòng không dùng. Dùng cho Grok/Codex hay một phiên Claude khác
khi viết cảnh `MỚI` ở `quy_uoc.md` mục 3.

```text
<inputs>
Cảnh: {{tên cảnh, ví dụ shadow_theatre}} — dạng {{D9}} trong .claude/skills/motion-library/references/prompt_motion/quy_uoc.md.
Kênh: {{FS | BUD | cả hai}}. Khung: {{1920x1080 Long | 1080x1920 short}}.
Dữ liệu vào (từ plan): {{ví dụ: steps [{at, word, label, pos}]}} — mặc định nếu thiếu: {{…}}.
Mẫu tham khảo (chỉ mượn kỹ thuật, không chép thiết kế): {{link prompt-motion}}.
</inputs>

<direction>
Nền {{xanh đen #0e1626 | nâu ấm}}; một màu nhấn duy nhất {{vàng #d9b45a | vàng nghệ}}; phông có dấu tiếng Việt
({{Be Vietnam Pro / Lora / Charm}}). Thẩm mỹ: {{FS huyền bí: bát quái, khói hương, Đông Hồ | BUD trang nghiêm, ấm, sen, ánh sáng}}.
Một cảnh một ý. Chuyển động bám mốc lời (at/word), không bám nhạc.
Cấm: crossfade, blur-in, hạt bung, lens flare, glow neon, tách RGB, rung camera, easing nảy, sàn lưới, nền nháy,
chữ/khung ở bốn góc, khung tô sau chữ, gradient tím hồng, glassmorphism, xoay 3D vô cớ, thứ trông như template.
Không người phương Tây. {{BUD: không máu, không vũ khí, không hoạt hình hoá Đức Phật.}} Không bịa số, ngày, lời kinh.
</direction>

<structure>
Cue sheet theo câu đọc (giây tính từ đầu cảnh):
{{0.0  vào: …}}
{{at=N word="…"  bước 1: …}}
{{…}}
{{cuối: giữ yên ≥ 0,4 s, ra bằng vật dùng chung với cảnh sau hoặc cắt cứng}}
</structure>

<build>
Viết vào hyperframes_short/compositions/longform.js (Long) hoặc devices/*.js (Studio short), đăng ký trong hyperframes_bridge.py.
Mọi chuyển động nằm trên timeline GSAP đã pause; mọi khung là hàm thuần của t:
không Math.random (dùng HF.rng(HF.hashSeed(...))), không Date, timer, CSS transition, không mạng lúc render;
lò xo dạng nghiệm đóng; trạng thái liên tục dùng MỘT tween tiến trình + onUpdate tính từ t.
Easing mặc định cubic-bezier(0.16,1,0.3,1), vượt đích < 2 %. Mọi xuất hiện ≥ 0,3 s.
Làm theo skill motion-scene-dev (bảng bẫy đã dính).
</build>

<gotchas>
- Phần tử ẩn mặc định bằng CSS + tl.set + tl.to (fromTo vẽ trạng thái đầu ngay lúc dựng).
- Đo chữ chỉ sau khi font nạp; dấu chữ hoa tiếng Việt không được bị cắt (kiểm chữ Ờ, Ẫ, Ậ).
- Không opacity/filter trên phần tử preserve-3d; không will-change trên thứ bị camera scale.
- Khối màu tràn khung phải vượt góc xa nhất và kéo ~0,35 s.
- Class riêng có tiền tố (lf-*), không đụng class phụ đề.
- {{bẫy riêng của cảnh này}}
</gotchas>

<start>
Chưa viết code ngay. Trước hết trình: (1) cue sheet trên lưới mốc lời; (2) 4 khung tĩnh ở {{0 %, 30 %, 60 %, 95 %}} thời lượng cảnh.
Chờ duyệt rồi mới dựng. Dựng xong: chạy showreel + hf_qa, quét "bật một khung" bằng chênh lệch khung, soát dấu tiếng Việt,
và gửi contact sheet cho người soát (không phải người vừa dựng).
</start>
```

## Mẫu ngắn cho ảnh nền AI (thumbnail, cảnh tái hiện)

Khi cảnh cần ảnh do ChatGPT / Flow / Muse vẽ (xem `project_thumb_refresh_1025` trong bộ nhớ và ADR 0004, 0005):

```text
ẢNH NỀN KHÔNG CHỮ, khổ {{16:9 | 9:16}}, {{mô tả cảnh cụ thể: ai, làm gì, ở đâu, lúc nào, cảm xúc}}.
Bố cục: chủ thể ở nửa {{PHẢI}}, mặt chiếm 30–45 % chiều cao; nửa {{TRÁI}} tối, trống để đặt chữ.
Người châu Á / Ấn Độ cổ đại, không người phương Tây, không máu, không vũ khí.
TUYỆT ĐỐI không có chữ, chữ số, ký tự, chữ Hán đọc được, logo hay watermark. Chỉ tạo 1 ảnh.
```
Chữ luôn đặt bằng phần mềm (`thumb_cb.py`), không để AI viết chữ tiếng Việt.
