# Prompt review câu chuyện Long (nguyên văn của chủ kênh, 11/11/2026)

Dùng cho `scripts/long_story_review.py`. Không sửa câu chữ trong khối dưới đây; muốn đổi thì hỏi chủ kênh.

```text
Review đoạn audio script sau theo phong cách documentary storytelling: truyền cảm, tiết chế, tự nhiên khi đọc TTS. Chỉ rõ 4–6 đoạn cần sửa; với mỗi đoạn, nêu vấn đề và đưa bản viết lại cụ thể. Ưu tiên mạch diễn biến, hệ quả và điểm đọng cảm xúc bằng dữ kiện; giảm nhịp liệt kê và lời bình về nguồn. Không bịa cảnh, đối thoại, nội tâm, động cơ hay quan hệ nhân quả. Giữ mức độ chắc chắn của tư liệu; đánh dấu chi tiết cần xác minh. Sau phần review, viết lại toàn đoạn theo các đề xuất.
```

## Phần ngữ cảnh script ghép thêm sau prompt
1. Tên chương và vị trí trong bài (chương trước kết ở đâu, chương sau mở ở đâu: một câu mỗi bên).
2. Lời đọc của chương, đánh số câu.
3. `factcheck.md` của bài (phần liên quan, hoặc cả file nếu ngắn), để model biết dữ kiện nào đã có nguồn.
4. Yêu cầu định dạng đầu ra: mục "Review" (4–6 đoạn), mục "Bản viết lại" (toàn chương), mục "Cần xác minh" (gạch đầu dòng).
