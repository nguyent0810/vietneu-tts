# QA · p131_fs_quet_nha_c1v2 · render lại bằng 5 ảnh AI · 05/11/2026

- Packaging c1 v2 đã APPROVE (content_sha256 `54dd0dd3…`): title, thumbnail, hook, lời đọc giữ nguyên; `lines` giống spec đã duyệt, dùng lại `voice.wav` 03/11.
- Spec: lấy từ bản `_img` PO đã APPROVE 04/11, đổi `id`/`out` về `p131_fs_quet_nha_c1v2`, **bỏ credit trên hình** (`credit: ""` ở 5 cảnh pan_tour, luật PO 04/11). Credit ảnh AI chỉ ghi ở `spec.credits` → `media_credits` và mô tả.
- Bản cũ (chữ động 03/11) sao lưu ở `oracle:~/pilot131/out/p131_fs_quet_nha_c1v2/bak_v2_text_2026-11-05/`.
- Ảnh: `ai_01..05.png` 1080×1920, sha256 khớp Mac ↔ Oracle (3e41d810/c40a75fd/a30b9f38/8ffa3df7/eee225b2). Lead đã soát: không chữ, không lộ mặt, không bạo lực.
- Render Oracle (2 OCPU/12 GB) qua `studio_runner.py`, `bash -c`, `/usr/bin/chromium`, nav timeout 300 s: rc=0, 908 s, RAM đỉnh 474 MB.
- Probe: h264 1080×1920 30 fps + AAC, 45,5 s.
- Loudness: mix production ra −20,0 LUFS (Oracle chưa có PR #133). Hậu kỳ: gain +7 dB + alimiter trần −1,5 dBTP (cách của PR #133), video copy → **−14,2 LUFS, true peak −1,3 dBTP**.
- hyperframes check: runtime 0 lỗi, contrast 0 lỗi, layout 1 lỗi `content_overlap` ở 31,75 s (kicker "TỪ ĐÓ · NGƯỜI TA" và chữ "Kiêng") — xem khung không thấy đè; bằng bản đã APPROVE.
- Contact sheet (`contact_sheet.jpg`, 15 khung, trái→phải, trên→dưới): 0 · 0,5 · 4,6 · 9,3 · 12 · 15 · 17,5 · 19,3 · 21,5 · 29,5 · 30,8 · 31,75 · 33 · 37 · 45,4 s.
  - Khung 0: ảnh ai_01 (đống rác, bóng cô hầu tan vào khói, đèn lồng đỏ) — đủ nghĩa, khớp first frame đã duyệt, giống khung 0 bản `_img` trừ dòng credit.
  - Không còn dòng "ẢNH MINH HOẠ AI" ở mọi khung.
  - Phụ đề nằm dưới khung ảnh, không đè mặt hay chủ thể.
- Còn mở:
  - Đầu cảnh pan_tour (ai_01, ai_02, ai_05) còn nền mờ hai bên lúc máy đang phóng vào (như bản `_img`).
  - Cảnh báo đa dạng (không chặn): cảnh 0 là pan_tour; 3 pan_tour liên tiếp.
  - 'Sưu thần ký' chỉ dựa 1 bài báo.
- Trạng thái: chờ PO xem bản cuối. Không publish, không hẹn lịch.
