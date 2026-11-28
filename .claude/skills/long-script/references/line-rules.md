# Adapter lời đọc HBR / VieNeu

Giọng FS: luận giải trực tiếp, uyên thâm và có kịch tính; không chèn câu “chỉ dừng ở mức tham khảo” vào đầu/chương, chỉ một lời tham khảo ở cuối bài. Giọng BUD nhẹ nhàng, uyên thâm, nhân văn, tự tại, chữa lành; kể chuyện tự nhiên thay vì răn giảng. Cả hai kênh ưu tiên mạch kể cho tai, không ép vụn câu hoặc liệt kê.

[Chuẩn lời §2–7](../../../../docs/script/audio-script.md#2-hợp-đồng-giao-lời), [Long chuẩn](../../../../docs/script/profiles/long-standard.md), [BUD](../../../../docs/script/profiles/bud.md), [FS](../../../../docs/script/profiles/fs.md) sở hữu luật; file này chỉ giữ cách đọc và DSL. Ngân sách theo [bảng giọng](../../../../docs/script/voice-rates.md).

## 1. Dòng và nhịp
TTS đọc từng `say()`, rồi nghỉ theo cấu hình. Người kể viết văn xuôi tự do → `tools/prose_to_script.py` tách ở dấu kết câu → một dòng/câu trọn, TTS đọc nguyên câu, không tách vế ở phẩy/chấm phẩy/hai chấm. Long BUD/FS/VSD không giới hạn độ dài câu: máy không cảnh báo, không chặn (PO 17/11); câu dài thì nghe thử bằng tai. Không quota câu ngắn trong finding; nhịp ngắn/12–18 tiếng là gợi ý. Dựng plan, Lead nghe CH00–01 qua `tools/tts_sample.py <plan> --only <id> --chapters 0 1`, rồi mới viết tiếp. Trong120s đầu, viết câu theo ý; cổng hình vẫn động≤8s/tĩnh≤4s, chữ nền trống≤1,5s. Không lấy nhịp hình làm độ dài câu.

## 2. Cách VieNeu đọc — phép đo phonemize_text 14/10/2026
| Viết | Đọc ra | Dùng? |
|---|---|---|
| `1983`, `2027`, `2008` | một nghìn chín trăm tám mươi ba / hai nghìn không trăm hai mươi bảy / ... lẻ tám | được, nên 1–2 năm/câu, tối đa 3 mục |
| `1.068 m`, `2.500 năm`, `1,5 triệu` | một nghìn không trăm sáu mươi tám mét / hai nghìn năm trăm / một phẩy năm | được |
| `12/7/2025`, `23:00`, `3/4`, `50%` | mười hai tháng bảy năm... / hai mươi ba giờ không phút / ba trên bốn / năm mươi phần trăm | được nhưng nên viết chữ |
| `thế kỷ VIII`, `Chương II` | thế kỷ tám / chương hai | được |
| **`1-3 lần`, `23-1 giờ`** | **"ngày một tháng ba lần"** | KHÔNG: viết "từ một đến ba lần", "từ mười một giờ đêm đến một giờ sáng" |
| **`DN 16`, `MN 135`, `SN 36.6`** | **"đi-en mười sáu"** (kiểu Anh) | KHÔNG: lời đọc "Trường Bộ, kinh số mười sáu"; mã kinh để trên màn hình (`quote` source) |
| `(tức là Mộc)` | đọc liền, mất ngoặc, không ngắt hơi | viết bằng dấu phẩy |


Tên Pali/Phạn dùng Hán Việt/Việt hoá: Xá Lợi Phất, Cấp Cô Độc, Vi Đề Hi; tên chưa có ưu tiên gọi vai sau lần giới thiệu. Viết tắt lạ viết đầy đủ. Lexicon có thể sửa, cần nghe đúng giọng trong phiên sản xuất; đây không phải phép đo audio mới.

## 3. DSL hình và thẻ chương
`**cụm**` giữa câu là chữ khoá1–4 tiếng có nghĩa; một cụm/câu khi cần. Câu không ảnh/sơ đồ/visual cần đúng một chữ khoá; `bare_lines` chặn, không có fallback lấy chữ đầu để cứu câu trần. Ảnh full không tự phủ cụm ấy lên hình (PO16/11).
`chap(t)` là dòng **đậm trọn**, thẻ/mốc chương; HBR đọc tiêu đề. Tách số thứ tự khỏi title hiển thị/lời đọc, không chèn “Chương II”. Title2–7 tiếng có nghĩa; không bôi đậm trọn câu thường. V2 dùng title/sub/lines riêng, không ép bỏ/đọc thẻ chung mọi engine. Cảnh động có thể giữ lâu hơn khi hợp ngữ cảnh; cảnh tĩnh trơn giữ tối đa 8s trong 120s đầu. Không tạo cuts dưới 3s; dùng cine/pan/parallax để làm sống cảnh dài.

## 4. Pause/tempo — preset legacy, không ghi đè giọng mới
`pause`: đỉnh1,0–1,4s; câu hỏi lớn0,8–1,2; thẻ1,7–2,0 (`chap`2,0). Binh legacy0,91, đỉnh0,85–0,88; Sơn FS0,96. Giọng mới/cấu hình tập theo brief và bảng giọng, không dùng preset legacy cho Thục Đoan. `SILENCE`/`DROPS` cho điểm đọng; không tự tăng vang/nhạc. `alt=True` và nguồn theo hồ sơ BUD. Sửa dòng thì kiểm fingerprint pause/tempo.

## 5. Thoại và bàn giao
Một lượt/một dòng; người nói trước lời thoại; xưng hô/động từ dẫn để một giọng vẫn rõ vai. Không ngoặc kép lồng; câu thoại≤20 tiếng là gợi ý nghe. Lời/notes/hướng hình tách như lõi §2; chạy `.venv/bin/python long_script_lint.py <plan|nhap.txt> --strict`, ghi CB để Lead đọc. Không xem mọi finding văn phong là lỗi.
