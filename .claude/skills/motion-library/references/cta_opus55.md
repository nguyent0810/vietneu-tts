# CTA học được từ các thư viện video Opus 5.5

Ngày kiểm tra: 2026-10-26. Phạm vi: repo, README, CSV/Markdown/JSON trên GitHub và bài gốc được repo dẫn. Không tải video. Mọi điểm hợp là đánh giá biên tập cho FS/BUD, không phải kết quả thử nghiệm.

## Tóm tắt ba repo

| Repo | Tồn tại / quy mô | Chất lượng và giới hạn |
|---|---|---|
| [athemeroy/awesome-opus-5-5-videos](https://github.com/athemeroy/awesome-opus-5-5-videos) | Có. README tại thời điểm kiểm tra ghi 424 bài nguồn, 301 gắn nhãn Opus; thư mục case ghi 168 case được đọc sâu, còn issue mô tả 1.008 video và 152 case. Các con số mô tả khác thời điểm/đơn vị, nên 1.008/152 chưa kiểm được trong bản hiện tại. | Mạnh nhất cho truy nguyên: CSV case, bài gốc, ghi chú 9 khung, giới hạn chứng cứ. Không phải bảng xếp hạng; mẫu được tuyển chọn; 9 khung không chứng minh toàn bộ chuyển động, âm thanh hay hiệu quả CTA. [README](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/README.md), [case index](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/docs/cases-index.zh-CN.md), [statistics](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/docs/statistics.md) |
| [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) | Có. README hiện ghi 418 bản có remake trực tiếp trên Skillry, 703 prompt trong kho; 100 mục nổi bật. Con số “282 video viral” trong issue không khớp bản README hiện tại, chưa xác nhận cùng phạm vi. | Prompt và bài gốc dễ dò, một số có cặp bản gốc/remake. “Viral” là cách repo gọi bộ sưu tập; không có đối chứng hay dữ liệu CTA/retention chuẩn hóa. [README](https://raw.githubusercontent.com/yihui-dev/awesome-opus5-5-videos/main/README.md) |
| [LeaddeOpenLab/awesome-opus-5-5-video-prompts](https://github.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts) | Có. Banner README nêu 2.000+ prompt; có các nhóm motion graphics, explainers, 3D và template 15 giây. | Mạnh ở prompt, preview, thông tin đầu vào/công cụ; mỗi mục có nhãn kiểm chứng (ví dụ prompt phái sinh Manim được ghi “reference — not fully verified”, chưa thử tái tạo). Nhiều prompt quảng cáo/demo, không phải nghiên cứu về CTA hiệu quả. [README](https://raw.githubusercontent.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts/main/README.md), [case Manim](https://raw.githubusercontent.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts/main/prompts/2103128559174971663.md) |

## Mẫu có thể tham khảo

Điểm 0–3 là độ hợp với quy ước kênh, không chấm hiệu quả. “Chưa kiểm” nghĩa là nguồn không có số liệu cho CTA.

| Nguồn | Kỹ thuật / cách nói | Hình động quan sát được | FS | BUD | Rủi ro |
|---|---|---|---:|---:|---|
| [@shushant_l, case 2103829449359966629](https://x.com/shushant_l/status/2103829449359966629), được ghi trong [CSV case](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/data/cases.csv) | Video quảng cáo khoảng 15 giây; ghi chú mô tả có “CTA guiding card”. Câu chữ cụ thể của CTA: chưa kiểm. | 9 khung ghi UI sản phẩm nghiêng phối cảnh, mảng màu động, logo và thẻ CTA ở đoạn kết. | 2 | 1 | Cấu trúc bán hàng có thể gây cảm giác quảng cáo; không có chứng cứ CTA tăng bình luận hay giữ chân. |
| [@pivi___, case 2103024907965612250](https://x.com/pivi___/status/2103024907965612250), [bài quy trình gốc](https://x.com/pivi___/status/2103110409397952580) | Đóng video sản phẩm bằng end card; phần copy/CTA chính xác không được CSV xác nhận. | 9 khung cho thấy promo Dictus từ sóng âm tới UI điện thoại và end card; tác giả nói lấy logo/màu/copy từ repo sản phẩm. | 1 | 0 | Đây là promo thương mại; không suy rộng nội dung copy sang kênh. End card không đồng nghĩa có CTA tương tác. |
| [@cherry_mx_reds, case 2102472218269900876](https://x.com/cherry_mx_reds/status/2102472218269900876), [CSV case](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/data/cases.csv) | Kết truyện hoạt hình bằng end card; lời kêu gọi cụ thể: chưa kiểm. | Ghi chú 9 khung cho biết kết có tim, bệ nhún và end card; đây là điểm dừng hình ảnh rõ ràng. | 1 | 1 | Không có dấu hiệu CTA, càng không có dữ liệu hiệu quả; chỉ mượn nhịp chốt hình. |
| [Leadde product-launch 15s template](https://raw.githubusercontent.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts/main/README.md) | Template dành cho giới thiệu sản phẩm và lợi ích; README gọi trường cấu hình là “CTA”. Câu cụ thể: chưa kiểm. | README mô tả video 15 giây có cấu hình chỉnh sửa; chi tiết chuyển động cuối clip chưa kiểm trong hướng dẫn template. | 1 | 0 | Khung bán hàng không hợp BUD; không có kết quả A/B được công bố. |
| [@deedydas, case 2103174501345493197](https://x.com/deedydas/status/2103174501345493197), [CSV case](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/data/cases.csv) | Bài hướng dẫn có các bước đánh số; có thể chuyển nguyên tắc “hành động tiếp theo rõ” thành câu mời dò/lưu bảng, không bê lời gốc. | 9 khung cho thấy bước, nhãn bộ phận, cảnh báo và bảng hướng dẫn. | 2 | 1 | Chỉ là suy luận về tính dễ làm theo; nội dung gốc không phải CTA bình luận, retention chưa kiểm. |

### Số liệu hiệu quả CTA

Chưa tìm thấy case nào trong các nguồn đã đọc báo cáo đồng thời CTA cụ thể và số retention/bình luận/view gắn với CTA để kết luận mẫu thắng. Athemeroy ghi rõ thống kê là mô tả corpus, case tuyển chọn; 9 khung không xác minh toàn bộ video ([statistics, mục giới hạn](https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/docs/statistics.md)). Vì vậy không gán số view cho các hàng trên. Dữ liệu kênh nên lấy từ `hf_brief` tại cửa sổ 48 giờ và 7 ngày.

## Đề xuất thử (không tự đổi CTA video đã hẹn)

1. **FS – câu hỏi tự dò trên thẻ cuối:** ở khung giữ của bảng năm sinh, giữ CTA hiện tại “Bạn sinh năm nào? Bình luận…”; thử biến thể hỏi đúng tên chi và chỉ hiện câu hỏi sau khi hàng bảng đã đọc xong. A/B trong `experiments/`, áp vào [review_yeartable.html](../../../../hyperframes_short/compositions/review_yeartable.html). Đo % xem/retention, hạng và bình luận trong `hf_brief` (48 giờ, 7 ngày). Công: thấp, khoảng 1–2 giờ.
2. **FS – CTA đồ họa dẫn mắt:** thẻ kết có mũi tên nét mảnh trỏ xuống vùng bình luận, không vẽ giả giao diện YouTube; test A/B ở `experiments/` với [review_yeartable.html](../../../../hyperframes_short/compositions/review_yeartable.html). Đo ba chỉ số `hf_brief`: % xem, hạng, bình luận. Công: thấp, 1–2 giờ; bảo đảm safe-zone và dấu tiếng Việt.
3. **FS – game “chạm giữ”:** chỉ thêm vòng tiến trình/nhịp dừng hình đồng bộ để người xem biết lúc chạm giữ; không đổi luật trò chơi. A/B trong `experiments/`, dùng [fs_v3.html](../../../../hyperframes_short/compositions/fs_v3.html) hoặc builder short tương ứng. Đo % xem và bình luận 48 giờ/7 ngày; hạng làm chỉ số phụ. Công: vừa, 2–4 giờ.
4. **BUD – câu hỏi chiêm nghiệm được để yên:** giữ câu hỏi cuối bài, cho câu hiện tĩnh sau khi lời đọc kết thúc và không thêm mũi tên, bộ đếm hay hiệu ứng thúc giục. A/B ở `experiments/`, dùng [review_budtable.html](../../../../hyperframes_short/compositions/review_budtable.html) nếu đúng định dạng, hoặc builder BUD. Đo % xem, hạng, bình luận trong `hf_brief`; Lead duyệt câu chữ. Công: thấp, 1–2 giờ.

Ô A/B ghi vào `output/cl_staging/experiments/tn_<tháng>.json` (thư mục bị gitignore nên không có trong checkout sạch), nhắc đo bằng `output/cl_staging/review_due.py`.

## Không nên mượn

- Không bê CTA bán hàng/end card thương mại nguyên văn: repo nguồn là promo sản phẩm, không chứng minh hiệu quả, lệch giọng FS/BUD.
- Không dùng game, đếm ngược hoặc “kết quả thắng/thua” cho BUD; xung đột yêu cầu trang nghiêm và câu hỏi chiêm nghiệm.
- Không dùng đèn nhấp nháy, particle/glow hoặc mũi tên kiểu HUD. Danh sách này đã cấm trong quy ước motion hiện hành ([quy_uoc.md](./prompt_motion/quy_uoc.md)); mẫu CTA kiểu app có nguy cơ rập khuôn “mùi AI”.
- Không tuyên bố tăng view/retention/bình luận từ lượt thích hay nhãn viral của repo; dữ liệu không thiết lập quan hệ nhân quả.

## Nhận xét Lead (Claude, 26/10/2026)

Codex làm ticket. Lead đã kiểm chéo:
- `data/cases.csv` của athemeroy có 168 case.
- Bốn mã case dẫn trong bảng đều có trong CSV. Mô tả "CTA 引导卡片" của case 2103829449359966629 có thật.
- README yihui ghi 703 prompt.
- Hai file `fs_v3.html` và `review_budtable.html` có trong repo.

Không thấy chỗ nào bịa.

**Kết luận.** Ba repo là kho kỹ thuật dựng hình, không phải kho bằng chứng về CTA: không case nào gắn câu CTA với số giữ chân hay số bình luận. Vì vậy ticket này **không đổi luật CTA**. Bằng chứng tốt nhất vẫn là số liệu của chính kênh:
- FS: bình luận nhiều nhất là người xem tự ghi năm sinh, đúng như câu CTA "Bạn sinh năm nào?".
- BUD: bình luận nhiều nhất là câu niệm. Mẫu trả lời đã có ở `reply_voice.md`.

**Ưu tiên nếu thử:**
- **Đề xuất 1** (FS hỏi đúng tên chi, chỉ hiện câu hỏi sau khi đọc xong bảng): công thấp, khớp số liệu, đáng thử trước.
- **Đề xuất 4** (BUD câu hỏi đứng yên): làm kèm được.
- **Đề xuất 2** (mũi tên chỉ xuống vùng bình luận): chỉ thử khi đề xuất 1 có tín hiệu. Mũi tên phải là nét tĩnh, không dùng dạng HUD.
- **Đề xuất 3** (vòng tiến trình cho game): hoãn, vì game dừng hình còn chờ đo riêng.
