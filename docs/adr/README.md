# Quyết định kiến trúc (ADR): kinh nghiệm vận hành kênh BUD và FS

Mỗi file ghi một quyết định, theo khuôn: bối cảnh có số đo, các phương án đã loại, hệ quả, bằng chứng.

Số liệu tính tới 24/10/2026. Nguồn:

- `chunks_cache/brief/metrics_*.json` (Analytics, cửa sổ 7 ngày);
- Studio 28 ngày (đọc 22/10);
- đường giữ chân đo 14/10, 21/10, 24/10;
- báo cáo thợ, ticket 52–71.

Nhiều file bằng chứng nằm trong `output/` (gitignore), nên chỉ có trên máy dựng.

## Đọc nhanh cho chủ kênh khác: 10 điều nên mang theo

1. **Short bị nghẽn ở vòng thử đầu, chưa phải ở chủ đề.** Chỉ 1/407 short vượt 2.000 view; khoảng 97% view đến từ Shorts feed; stay tương quan với view r ≈ 0,5. Sửa giây 0 và câu 2 trước khi đổi đề. → [0006](0006-short-chi-lam-chuoi-thang.md)
2. **Câu thứ hai (giây 4–5) là chỗ rơi dốc nhất.** Câu 2 nói thông tin cụ thể thì rơi 3,4%/s, nói chung chung thì 8,1%/s. → [0006](0006-short-chi-lam-chuoi-thang.md), [0015](0015-cach-do-so-lieu-kenh.md)
3. **Chìa khoá cá nhân (năm sinh, tên chi) cộng mốc thời gian phá được trần.** Bảng 2027 của FS có bài 51k view với AVP 132%. Nhưng chép bề mặt công thức sang ngách khác thì thua: BUD dạng bảng chỉ được 2–6,5 view/giờ, so với nền 21–57. → [0006](0006-short-chi-lam-chuoi-thang.md)
4. **Long thua vì khuôn, không vì độ dài.** Long 30 phút chủ đề rộng mất 76–92% người xem trong 90 giây đầu. Kênh Hình Sự làm Long 27–32 phút theo khuôn nhân vật đạt AVD 9:28. Giữ độ dài, đổi khuôn: một nhân vật, cảnh mở có thật, câu hỏi hẹn chương. → [0001](0001-long-30-phut-khuon-nhan-vat.md)
5. **Luật kịch bản lấy từ chính đường giữ chân của kênh, rồi viết thành lint.** Đừng chép checklist chung. Đếm tiếng đọc, không đếm từ. → [0002](0002-luat-giu-chan-tu-duong-cong-that.md)
6. **Ngách tôn giáo/phong thủy sống bằng lòng tin.** Mọi dữ kiện có mã và nhãn lớp nguồn. Lời kinh đối chiếu bằng công cụ. Số liệu sinh bằng code. Bộ kiểm độc lập không để người viết sửa. → [0003](0003-ba-lop-nguon-va-du-kien-sinh-bang-code.md)
7. **Hình: tư liệu thật trước, rồi ảnh AI theo phong cách kênh, stock sau cùng.** Ảnh AI hạ "chữ trên nền trống" từ 51% xuống 21,5%. Soát từng ảnh, không dùng ảnh AI thay bằng chứng lịch sử. → [0004](0004-thu-bac-nguon-hinh-va-anh-ai.md), [0009](0009-nhip-hinh-la-diem-kiem-truoc-render.md)
8. **Thumbnail có tên mỏ neo cộng ≤ 3 chữ.** Nền AI không chữ, chữ tự đặt, xem ở cỡ 168 px. → [0005](0005-thumbnail-nen-ai-chu-tu-dat.md)
9. **Đăng riêng tư kèm hẹn giờ, đếm lịch theo ID.** Playlist từng báo "0 video đã hẹn" trong khi có 71. Dọn file vào Thùng rác, không xoá vĩnh viễn. → [0007](0007-dang-rieng-tu-hen-gio-dem-theo-id.md), [0012](0012-don-file-vao-thung-rac.md)
10. **Thợ AI làm nhanh nhưng hay báo "đạt" sai** (15/16 lỗi lọt qua bước tự kiểm của thợ). Một Lead kiểm bằng số liệu thật, viết retro sau mỗi đợt, lỗi lặp lại thì viết thành code kiểm. → [0008](0008-lead-va-tho-qua-hang-doi-file.md), [0013](0013-retro-sau-moi-dot.md)

## Danh mục

| # | Quyết định | Trạng thái |
|---|---|---|
| [0001](0001-long-30-phut-khuon-nhan-vat.md) | Long ≥ 30 phút, khuôn nhân vật, không rút ngắn | đang thử, điểm duyệt 22/11 |
| [0002](0002-luat-giu-chan-tu-duong-cong-that.md) | Luật giữ chân từ đường cong thật → lint + duyệt plan | chấp nhận |
| [0003](0003-ba-lop-nguon-va-du-kien-sinh-bang-code.md) | Ba lớp nguồn, dữ kiện sinh bằng code, bộ kiểm độc lập | chấp nhận |
| [0004](0004-thu-bac-nguon-hinh-va-anh-ai.md) | Tư liệu thật > ảnh AI > stock; được dùng ảnh AI có mặt Đức Phật | chấp nhận |
| [0005](0005-thumbnail-nen-ai-chu-tu-dat.md) | Thumbnail nền AI không chữ, chữ tự đặt, tên mỏ neo | chấp nhận |
| [0006](0006-short-chi-lam-chuoi-thang.md) | Short chỉ làm chuỗi thắng; chép cơ chế, không chép bề mặt | chấp nhận |
| [0007](0007-dang-rieng-tu-hen-gio-dem-theo-id.md) | Đăng riêng tư + hẹn giờ, đếm theo ID, 24 upload/24 giờ | chấp nhận |
| [0008](0008-lead-va-tho-qua-hang-doi-file.md) | Lead và thợ qua hàng đợi file; phản biện ngoài chỉ để tham khảo | chấp nhận |
| [0009](0009-nhip-hinh-la-diem-kiem-truoc-render.md) | Nhịp hình kiểm trước render: chặn ít, cảnh báo nhiều | chấp nhận |
| [0010](0010-do-to-dau-ra-va-giong-doc.md) | Độ to hai lượt + limiter (Short −14, Long −16 LUFS); giọng preset C | chấp nhận (PR #29) |
| [0011](0011-nhac-nen-theo-so-chong-trung.md) | Nhạc nền theo sổ chống trùng | chấp nhận |
| [0012](0012-don-file-vao-thung-rac.md) | Dọn vào Thùng rác, chỉ khi YouTube đã xác nhận | chấp nhận |
| [0013](0013-retro-sau-moi-dot.md) | Retro sau mỗi đợt; lỗi lặp thành check code | chấp nhận |
| [0014](0014-tiktok-chi-bud.md) | TikTok chỉ BUD, 3/5 bài mỗi ngày, trễ D+3 | chấp nhận |
| [0015](0015-cach-do-so-lieu-kenh.md) | Đo theo cửa sổ 7 ngày PT, tuần sạch, Lead tính lại số | chấp nhận |
| [0016](0016-seo-la-diem-kiem-truoc-khi-dang.md) | Soát SEO trước khi đăng Long, khai keyword | chấp nhận (PR #29) |

## Bẫy hay gặp (có ví dụ thật)

- **Đếm, đo**
  - Đếm video đã hẹn bằng playlist thì sót video riêng tư (0 thay vì 71).
  - "HẾT QUOTA" có thể là trần upload tự đặt, không phải quota API.
  - Lint ước 185 tiếng/phút, giọng thật đọc khoảng 178.
  - Runner đếm token nên bỏ sót câu nhiều năm sinh.
- **Hình**
  - Stock tìm bằng tiếng Anh ra người phương Tây và biểu tượng tôn giáo khác.
  - Thợ bịa tên file Commons.
  - Chân dung dọc trong khung ngang bị cắt chỉ còn búi tóc.
  - Dùng lại một ảnh trong cùng chương làm render dừng.
- **Chữ**
  - Thẻ chữ khoá cắt dấu chồng của chữ hoa ("THỀ" thành "THÊ").
  - Con dấu 吉 (cát tường) đóng cạnh chữ nghĩa xấu.
  - Năm hiện thành "1.863".
  - Tên Pali đọc vỡ ("DN 16" thành "đi-en").
- **Render, đĩa**
  - Thay ảnh mà giữ tên thì chương cũ vẫn được dùng lại (đã sửa ở PR #29).
  - Ghép cuối Long cần khoảng 12 GB tạm.
  - Thùng rác chỉ trả dung lượng khi đổ.
- **Đăng**
  - `--playlist` chọn playlist theo bảng ánh xạ, không theo spec dựng.
  - Gỡ lịch bài cũ trước khi chạy thử uploader bài thay thì để trống khung.
  - Lời nhắn Codex CLI phải đặt trước `-i`.

## Viết ADR mới

Tên file `NNNN-ten-ngan.md`. Tiêu đề là chính câu quyết định. Sau đó: một đoạn bối cảnh có số đo, "Các phương án đã cân nhắc", "Hệ quả", "Bằng chứng". Dùng từ trong `GLOSSARY.md` (kênh, chuỗi, cảnh, kịch bản, spec dựng, điểm duyệt). Khi lệch một ADR cũ, ghi rõ "thay ADR NNNN vì …".
