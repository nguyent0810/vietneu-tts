# Ảnh tĩnh và độ phủ hình trong Long MIM/CK (29/10/2026)

**Câu hỏi của chủ kênh:** bên AI Learning thấy một ảnh tĩnh đứng quá lâu thì khô; mức tốt là 5–8 giây mỗi ảnh, có hiệu ứng chuyển động. Long MIM/CK có cần thêm ảnh AI không?

## Cách đo

- **Dữ liệu:** `data/long/<topic>/chNN.json` (cảnh, `at` = số câu) ghép với `output/long/<topic>/chNN/timing.json` (giờ bắt đầu từng câu). Thời lượng một cảnh tính từ câu bắt đầu của nó tới câu bắt đầu của cảnh kế.
- **Phạm vi:** 26 Long CK và 28 Long MIM đã render.
- **Phân loại cảnh:**
  - **Ảnh tĩnh:** cảnh `photo` hoặc `print`.
  - **Chỉ chữ:** cảnh `kinetic`, `slam`, `question`, `quote`, `myth` hoặc `brand` mà không có `vid`, `bg` hay `img`.
  - **"Không có hình":** biểu đồ và chữ, không có ảnh và không có clip.

## Kết quả

| | MIM | CK |
|---|---|---|
| Tổng thời lượng | 370 phút | 265 phút |
| Thời gian lên hình: ảnh tĩnh / clip / đồ họa và chữ | 8% / 10% / 82% | 1% / 11% / 87% |
| Số cảnh ảnh tĩnh | 250 | 35 |
| Ảnh tĩnh: trung vị / trung bình | 6,5 s / 7,1 s | 5,2 s / 5,5 s |
| Ảnh tĩnh trên 8 s / trên 12 s | 86 / 15 (dài nhất 30 s) | 6 / 0 |
| Ảnh tĩnh có chuyển động | 250/250 | 35/35 |

Sửa ngày 29/10: bản đầu ghi 149/250 và 28/35, vì chỉ đếm ảnh có khai báo `move`/`zoom` trong spec. Thực ra `motion/hf/assets/engine/casewide.js` tự cho mọi ảnh chuyển động:
- `photo` mặc định `move: "in"`, tức phóng dần;
- `print` trôi phóng chậm sau khi hiện vào;
- `reveal` và `zoom` (thẻ thư viện FS/BUD) đã có từ 27/10.
| Phần chỉ chữ trong mỗi video | 18–55% | 9–55% |
| Hình riêng mỗi phút | 0,6–2,6 | 0,5–1,9 |
| Đoạn dài nhất không có hình | 14–72 s | 15–71 s |

Video yếu nhất:
- **Chỉ chữ trên 45%:** `mim-dich-may` (55%), `ck-d2-fomo` (55%), `mim-ai-gpu` (52%), `mim-ai-hallucinate` (50%), `ck-c2-phien-giao-dich` (46%), `mim-ai-chat-privacy` (46%).
- **Đoạn trên 60 s không có hình:** `mim-dich-may` (72 s), `ck-c3-bieu-do-nen` (71 s), `ck-c2` và `ck-d2` (66 s), `mim-ai-hallucinate` (60 s).

## Kết luận

1. **Thời lượng ảnh tĩnh đã nằm trong mức 5–8 s.**
   - Trung vị là 6,5 s ở MIM và 5,2 s ở CK, phần lớn ảnh có chuyển động.
   - Cần sửa: 86 ảnh MIM trên 8 s, trong đó 15 ảnh trên 12 s. Những ảnh này nên chia thành nhiều shot hoặc thêm chuyển động. Đây đúng là việc của `motion_picker` (vietneu #71).
2. **Chỗ khô thật là thiếu hình, không phải ảnh đứng lâu.**
   - 82–87% thời gian là đồ họa và chữ.
   - Nhiều video có 40–55% thời gian chỉ có chữ, và có đoạn 45–72 s liền không có hình.
   - CK gần như không dùng ảnh: 35 cảnh trên 26 video.
3. **Bù bằng ảnh AI là hợp lý, nhưng chỉ sau khi kho ảnh công cộng không đủ.**
   - MIM: các đề tài trừu tượng (GPU, hallucinate, dịch máy, quyền riêng tư) khó có ảnh PD, CC0 hay CC BY sát nghĩa.
   - CK: ảnh đời sống tiền bạc dễ sinh bằng AI, miễn không có logo, mã cổ phiếu hay chữ. `prompt_builder` (vietneu #60) đã cấm sẵn chữ, số, logo và mặt người.
4. **Ảnh AI không phải nút thắt chính.**
   - Chẩn đoán Long (`docs/pm/tickets/LONG-DIAG-report.md`) cho thấy vấn đề lớn là impressions và CTR.
   - Giữ chân không phải vấn đề chính: AVD của MIM từ Browse/Suggested khoảng 3:30.
   - Vì vậy phủ hình là việc nâng chất lượng xem, đi song song. Nó không thay việc sửa thumbnail và tiêu đề.

## Đề xuất cổng và cách bù (ticket riêng)

- **Cổng phủ hình cho Long MIM/CK.** Ngưỡng nháp, sẽ chỉnh theo dữ liệu:
  - không đoạn nào quá 25 s không có hình;
  - phần chỉ chữ không quá 30%;
  - ảnh tĩnh không quá 8 s nếu không chia shot.
- **Thứ tự lấp chỗ trống:**
  1. clip hoặc ảnh tự do;
  2. nếu không có, ảnh AI qua `prompt_builder` rồi Grok Bot (`scripts/ai_img_request.py`).
- **Ghi rõ nguồn:** ảnh AI ghi nhãn "ẢNH MINH HỌA AI" và đưa vào `credits.json`.
- **Phạm vi:** không áp cho CL. Luật của CL cấm ảnh AI.
