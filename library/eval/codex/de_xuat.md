# Đề xuất thử nghiệm BUD — thư viện kỹ thuật

## 1. Nơi áp dụng và kỹ thuật

- **Nơi áp dụng:** ô thử nghiệm `tn_2026-10` trong `output/cl_staging/experiments/tn_2026-10.json`. `lib.py pick --channel bud --usage-root "/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS"` liệt kê ô này cùng các khuôn ngang/thua; không chọn dạng thắng hay chuỗi Chú Đại Bi.
- **Kỹ thuật:** `text_reveal` — **Reveal chữ**, kỹ thuật đầu tiên trong gợi ý của `pick` và hạng 1 trong `lib.py rank --channel bud` (điểm 15; độ hợp 3 × 5 nguồn; công thấp; trạng thái `chua_co`).
- **Thẻ:** [library/cards/canh/text_reveal.md](../../cards/canh/text_reveal.md). Thẻ mô tả reveal bằng mask/wipe/opacity, khuyên đặt mốc reveal tuyệt đối để trạng thái phụ thuộc thời gian và seek-safe. BUD hợp ngách 3; thẻ cũng nêu rủi ro dấu tiếng Việt bị mask cắt. Dùng một cụm ngắn, cỡ chữ lớn và mở từ trái qua phải để giảm rủi ro này.

## 2. Chủ đề và kiểm trùng

**Tiêu đề:** Vì sao tiếng chuông vẫn ngân sau cú gõ?

Đã chạy từ checkout chính, chỉ đọc:

```text
/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/.venv/bin/python /Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/hf_novelty.py check bud "Vì sao tiếng chuông vẫn ngân sau cú gõ?"
[không có dòng trùng được in ra]
```

Chi tiết bất ngờ là thân chuông tiếp tục rung sau khi dùi rời ra; từ hiện tượng nghe thấy được, short nối sang một nhịp dừng trước khi đáp lời lúc nóng giận.

## 3. Kịch bản 6 câu — khoảng 27–32 giây

1. Vì sao tiếng chuông vẫn ngân khá lâu sau cú gõ, dù dùi đã rời mặt chuông?
2. Điều bất ngờ là thân chuông còn rung, tạo ra nhiều lớp âm nối tiếp nhau.
3. Âm nghe lớn trước rồi nhỏ dần khi rung động yếu đi.
4. Kệ 5 Pháp Cú dạy: hận thù không thể dập hận thù; lòng thương mới làm nó lắng xuống.
5. Khi lời làm mình nóng giận, thử dừng một nhịp, thở ra, rồi chọn lời dịu hơn.
6. Lần tới, bạn muốn đáp ngay, hay để một hơi thở chọn lời trước?

Ước lượng khoảng 95 âm tiết, tương ứng khoảng 27 giây ở nhịp đọc BUD xấp xỉ 3,5 âm tiết/giây. Câu 1 là câu hỏi, câu 2 đưa chi tiết bất ngờ, câu 6 là câu hỏi mở.

### Đối chiếu kinh

Kịch bản ở câu 4 là diễn ý, không đặt lời Việt mới trong ngoặc kép. Đã chạy:

```text
/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/.venv/bin/python /Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS/hf_sutta.py dhp1-20 "laid to rest by love"
https://suttacentral.net/dhp1-20/en/sujato
  dhp5:3         it’s laid to rest by love:
```

Ngữ cảnh nguyên văn liên tục trong kết quả `hf_sutta.py dhp1-20`:

> UID `dhp1-20`, đoạn `dhp5:1–3`: “For never is hatred / laid to rest by hate, / it’s laid to rest by love:”

Nguồn: [Dhammapada 1–20, bản dịch Bhikkhu Sujato](https://suttacentral.net/dhp1-20/en/sujato), kệ 5. Câu 4 chỉ diễn ý nội dung trên; không coi phần giải thích về chuông là lời Phật hay lời kinh.

## 4. Spec dựng

- **ID thẻ kỹ thuật:** `text_reveal`.
- **Code sẽ dùng/mở rộng** (vị trí lấy bằng `grep -n`):
  - `hf_batch_render.py:174` — chuyển `visuals` từ plan vào bridge.
  - `hyperframes_bridge.py:152` — danh sách visual short đã cho phép `word`.
  - `hyperframes_short/compositions/engine.js:205` — điểm dispatch visual hiện chỉ gọi kho `LONG`; mở rộng dispatch cho visual chữ của short.
  - `hyperframes_short/compositions/longform.js:1083` — builder `visuals.word` có thể tái dùng làm nền cho cụm chữ.
- **Thiết kế:** ở câu 2, hiện “THÂN CHUÔNG VẪN RUNG” bằng mask ngang trong khoảng cố định (khoảng 4,4–5,1 giây từ đầu short), làm nhịp ngắt thị giác của ô thử nghiệm. Cụm chữ gọn, không chạy từng ký tự nên dấu tiếng Việt không bị cắt vụn. Không thêm footage cần tải hoặc nguồn hình bên ngoài.
- **Tất định, seek-safe:** khởi tạo mask ở trạng thái đóng; timeline GSAP đặt `fromTo` tại mốc tuyệt đối đã định, progress là hàm của thời gian clip, và trạng thái cuối giữ mask mở. Không dùng callback tích lũy state, `Date.now()` hay ngẫu nhiên khi seek.
- **Ước công:** **vừa** — cần nối visual `word` vào nhánh short và thêm/tái dùng animation reveal; không thay đổi khuôn đang thắng.

## 5. Tự kiểm

- **ADR 0018 mục 7:** chọn duy nhất ô thử nghiệm được `pick` trả về; không chạm dạng thắng. Chuỗi được bảo vệ Chú Đại Bi không được chọn, nhắc tới hay dùng làm nội dung.
- **Luật BUD:** đề xuất không có máu, vũ khí, người phương Tây hoặc tôn giáo khác. Câu có ý kinh ghi rõ Pháp Cú kệ 5 và đối chiếu UID/đoạn tiếng Anh ở trên.
- **Không mùi AI:** hình ảnh âm thanh cụ thể (dùi rời mặt chuông, thân chuông còn rung) dẫn sang một lựa chọn ứng xử đời thường; tránh lời khuyên chung chung và không gán hiện tượng âm học cho kinh.
- **Chỗ chưa chắc:** thời lượng là ước tính theo nhịp đọc; cần căn theo voice thực tế khi sản xuất. `text_reveal` chưa phải visual reveal độc lập của short, nên spec yêu cầu mở rộng điểm dispatch trước khi dùng. Đây là đề xuất plan, không phải xác nhận đã dựng hoặc đo kết quả.
