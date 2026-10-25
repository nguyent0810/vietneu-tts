# Viết retro sau mỗi đợt đăng; mỗi bài học thành một luật, lỗi lặp lại thành một đoạn code kiểm

Trạng thái: đã chấp nhận (19/10/2026, bổ sung 21/10).

Ngày 19/10, chủ kênh yêu cầu tự nhìn lại sau mỗi đợt đăng. Ghi nhận chung chung không làm đổi hành vi, nên cần một khuôn bắt buộc. Ngày 21/10 ta mượn ý vòng tự cải thiện "đề xuất – thử – ghép" của Harness², nhưng không cài framework đó.

Khuôn retro:

- File `output/cl_staging/retro/<ngày>_<đợt>.md` có 2 phần: "làm tốt", và bảng "Lỗi | Hậu quả | Đã đổi thành".
- Mỗi lỗi ghi một dòng vào `grok/improve/defects.jsonl`: khâu, ai bắt được, có lọt qua bước tự kiểm không, luật nào đã sửa.
- Lỗi lặp lại từ 2 lần trở lên thì viết **check bằng code** trước, rồi mới thêm luật chữ.
- Thứ Hai: đếm lỗi theo khâu, gộp hoặc bỏ luật thừa.

## Các phương án đã cân nhắc

- **Ghi nhận chung chung trong chat.** Không còn dấu vết, lần sau lặp lại.
- **Chỉ thêm luật chữ.** Luật chữ tăng nhanh (từ 8 lên 20 luật trong một tuần) nhưng thợ vẫn bỏ qua. Check bằng code mới thật sự chặn được.

## Hệ quả

- Nhiều check sinh ra từ retro:
  - bộ kiểm hoàng đạo độc lập;
  - kiểm chồng chéo nội bộ;
  - bộ kiểm phải FAIL khi có cờ;
  - so khung cuối với khung giữa;
  - ảnh dọc vào khung 16:9, khoá chương băm nội dung file (24/10).
- Sổ có 23 lỗi. Lead bắt 18, chủ kênh bắt 2, bộ kiểm của Lead bắt 2, runner bắt 1. Bước tự kiểm của thợ hầu như không bắt được lỗi, đó là lý do có ADR 0008.

## Bằng chứng

`output/cl_staging/retro/*.md` (9 bản), `output/cl_staging/grok/improve/README.md`, `defects.jsonl`, `output/cl_staging/retro/2026-10-24_long_ai_cb_dbdd.md`.
