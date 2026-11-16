# Đánh bóng lời Long `cl-hoang-kim-vinh` theo PR #436 (chủ kênh 16/11) trước khi TTS

Đọc `docs/pm/storytelling-guide.md` §14 (bản mới nhất, nhất là mục 3 "kể thẳng chi tiết không khí", mục "Câu cho tai nghe", mục "Lời thoại phỏng dựng", mục người soát chỉ sửa tư liệu).

Kịch bản `data/long/cl-hoang-kim-vinh/script.md` hiện có 28 lần "Hãy hình dung" — chủ kênh: lặp mỗi chương "nghe như xin lỗi, kéo người nghe ra khỏi truyện". Việc:
1. Câu không khí (thời tiết, ánh sáng, âm thanh, đồ vật, người vô danh): bỏ "hãy hình dung…" và kể thẳng, thì hiện tại hoặc quá khứ đều được. Giữ tối đa 2 lần "hãy hình dung" cả bài, ở chỗ thật sự cần mời người nghe.
2. "Có lẽ/biết đâu" chỉ giữ khi đoán nội tâm/động cơ người thật có tên.
3. Câu đỉnh cảm xúc: được tách hai nhịp (một câu ngắn lặng + một câu dài) như ví dụ trong guide. Không cắt một câu thành hai dòng kết bằng dấu phẩy.
4. Được thêm 0–3 câu thoại phỏng dựng ngắn cho nhân vật lịch sử đã mất (đánh `{pd}`, không ngoặc trích, không [TRÍCH DỊCH]).
5. GIỮ nguyên mọi dữ kiện, số, tên, lời trích thật; giữ dấu `{pd}`, `{beat:…}`; số câu mỗi chương giữ gần như cũ (±5%); không đổi chữ đầu câu nếu câu đó là mốc neo cảnh — sau khi sửa phải chạy `python data/long/cl-hoang-kim-vinh/gen_scenes.py`; nếu báo câu không có chữ neo, sửa neo trong gen_scenes*.py cho khớp (chỉ sửa chữ neo, không đổi cảnh).
Sau đó: `python motion/long/script_lines.py cl-hoang-kim-vinh` (ghi lại chNN.json lines) rồi chạy lại gen_scenes.py (ghi lại scenes); kiểm `craft.audio_problems` == [], `factcheck_lint.lint` == [], `python scripts/check_scene_durations.py cl-hoang-kim-vinh --out <timing giả 4,1 từ/giây ngoài repo>` 0 lỗi (gen_scenes cần `output/long/cl-hoang-kim-vinh/research.json`; nếu thiếu, chép tạm từ `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\output\long\cl-hoang-kim-vinh\` rồi xoá sau).
Ghi bằng Python utf-8. Không commit, không TTS/render. Báo cáo ngắn: số "hãy hình dung" trước/sau, số câu đổi, thoại phỏng dựng thêm (nếu có).
