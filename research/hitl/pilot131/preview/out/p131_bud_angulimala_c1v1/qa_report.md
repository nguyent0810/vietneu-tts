# QA preview · p131_bud_angulimala_c1v1

- Chủ đề: bud_angulimala · phương án **c1 v1**
- content_sha256: `d19b2d762c7e675ed17d85913243d0521a8f06bce943d9cb564006efeec22f90`
- candidates_file_sha256: `b2b77ae34a86a4f4618e5d9ff247ef90eb76749b6cd188501050168eefd82657`
- Trạng thái duyệt: **APPROVED**
- Title: Ta đã dừng rồi, ngươi hãy dừng lại · Thumbnail: Ai mới dừng?
- Render: **RENDERED**  · máy: oracle vieneu-worker (A1 2 OCPU/12 GB)
- Thời lượng: 79.8 s · thời gian render: 1903 s · RAM đỉnh: 2352 MB
- Âm thanh: {'integrated_lufs': -17.9, 'true_peak_dbfs': 0.4}

- First frame: **FIRST_FRAME_MATCH** — Duyệt: con đường đất, người đi chậm phía trước, kẻ chạy phía sau. Thực tế: bích hoạ chùa Thái (CC BY 2.0) Angulimala cầm gươm đuổi theo Đức Phật trên đường — cùng cảnh, dạng tranh thay cho bóng người.

## Nguồn
- s1 MN 86 Aṅgulimālasutta, Bhikkhu Sujato (CC0), SuttaCentral
- s2 MN 86, Thanissaro, Access to Insight
- Ảnh: Photo Dharma (CC BY 2.0) x2, bích hoạ Angulimala.jpg (PD) — Wikimedia Commons

## Fact đã dùng
- f01, f02, f03, f04 (thần thông — theo yêu cầu PO), f05, f06, f07, f08, f10

## Lỗi / điểm còn tồn tại
- Tên đọc 'Angulimala' (bỏ dấu Pāli để TTS đọc được); title/hook đã duyệt viết 'Aṅgulimāla' — chữ trên màn hình giữ dạng có dấu ở source_card.
- Câu 'Hắn gọi: ngài đang đi, sao lại bảo đã dừng?' lấy từ escalation đã duyệt, không phải trích nguyên văn kinh (fact pack không có câu hỏi của Aṅgulimāla).
- Pasenadi/Kosala đọc theo tên Hán-Việt 'Ba Tư Nặc', 'Kiều Tát La'.
- Luật kênh BUD: lời Phật phải kiểm bằng hf_sutta.py — preview chỉ đối chiếu fact pack (Sujato/Thanissaro), CHƯA chạy hf_sutta.
- Render 2 lần: lần 1 nhãn ảnh đè kicker + câu trích vua Ba Tư Nặc tràn khung -> đã sửa (lưu ở qa_round1).

## Cảnh cần PO chú ý
- 0–3s: bích hoạ tròn Angulimala cầm gươm đuổi theo (khớp first frame đã duyệt)
- câu 7 (thần thông): bích hoạ Phật đi, Angulimala chạy
- câu 4: chữ 'Vòng cổ ngón tay' — kiểm có gây sợ không theo luật BUD
- Khoảng 44–46s: cảnh 'Đã dừng/Chưa dừng' chờ ~2s mới hiện chữ
- Âm thanh: true peak +0,4 dBTP (vượt trần −1 dBTP) và −17,9 LUFS — do bộ trộn short production (studio.mix_audio), không chỉnh tay

## File
- final_preview.mp4 · contact_sheet.jpg · first_frame.jpg · timing.json · status.json · render.log · mem_samples.txt
