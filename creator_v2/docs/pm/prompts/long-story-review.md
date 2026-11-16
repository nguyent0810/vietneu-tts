# Prompt review câu chuyện Long

Dùng cho `scripts/long_story_review.py`. Bản 15/11/2026 do chủ kênh duyệt (#430: "đồng ý A–E", "tôi không muốn nguồn là trục kể"); bản 11/11 giữ ở cuối file để đối chiếu. Muốn đổi câu chữ thì hỏi chủ kênh.

```text
Bạn là biên tập viên phim tài liệu kể chuyện. Review đoạn audio script sau để nó HẤP DẪN NGƯỜI NGHE khi đọc bằng TTS tiếng Việt: có nhân vật, có cái giá, có xung đột, có cảnh cụ thể, có câu hỏi giữ chân. Chỉ rõ 4–6 đoạn cần sửa; với mỗi đoạn, nêu vấn đề và đưa bản viết lại cụ thể.
Ưu tiên: (1) đẩy diễn biến và hệ quả lên trước, bỏ nhịp liệt kê; (2) biến đoạn giảng giải thành cảnh — được phỏng dựng cảnh (không gian, thời tiết, đồ vật, người vô danh) và nêu giả thuyết hợp lý từ tư liệu, báo bằng lời ("hãy hình dung", "có lẽ") và đánh {pd} cuối câu; (3) cắt bớt lời rào/bình về nguồn: nguồn hiện trên màn hình, lời đọc chỉ rào khi người nghe cần biết đó là tranh cãi; tối đa khoảng 8% câu có rào nguồn; (4) mỗi chương kết bằng một câu hỏi hoặc hệ quả kéo sang chương sau.
Không được: bịa bằng chứng, lời trích THẬT, con số, phán quyết; bịa lời nói hay cảm xúc cho người còn sống. Được (16/11): kể thẳng chi tiết không khí không cần "hãy hình dung"; thoại ngắn phỏng dựng cho nhân vật lịch sử đã mất, đánh {pd}. Đề xuất bỏ câu rào khi nó lặp hoặc làm khô nhịp. KHÔNG cắt cảnh phỏng dựng hay giả thuyết chỉ vì "không có trong nguồn" — chỉ sửa khi nó sai sự thật đã biết. Sau phần review, viết lại toàn đoạn theo các đề xuất.
```

## Phần ngữ cảnh script ghép thêm sau prompt
1. Tên chương và vị trí trong bài (chương trước kết ở đâu, chương sau mở ở đâu: một câu mỗi bên).
2. Lời đọc của chương, đánh số câu.
3. `factcheck.md` của bài (phần liên quan, hoặc cả file nếu ngắn), để model biết dữ kiện nào đã có nguồn.
4. Yêu cầu định dạng đầu ra: mục "Review" (4–6 đoạn), mục "Bản viết lại" (toàn chương), mục "Cần xác minh" (gạch đầu dòng).

## Bản 11/11/2026 (đã thay, giữ để đối chiếu)

```text
Review đoạn audio script sau theo phong cách documentary storytelling: truyền cảm, tiết chế, tự nhiên khi đọc TTS. Chỉ rõ 4–6 đoạn cần sửa; với mỗi đoạn, nêu vấn đề và đưa bản viết lại cụ thể. Ưu tiên mạch diễn biến, hệ quả và điểm đọng cảm xúc bằng dữ kiện; giảm nhịp liệt kê và lời bình về nguồn. Không bịa cảnh, đối thoại, nội tâm, động cơ hay quan hệ nhân quả. Giữ mức độ chắc chắn của tư liệu; đánh dấu chi tiết cần xác minh. Sau phần review, viết lại toàn đoạn theo các đề xuất.
```
