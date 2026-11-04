# Báo cáo GH-33-T · Tinh chỉnh Title, Mô tả, Hashtag và Tag theo từ khóa xu hướng cho 12 Short Pilot

- **Ticket:** `docs/pm/tickets/GH-33-grok-titles.md` (Issue [#33](https://github.com/nguyent0810/Youtube_Creator_V2/issues/33))
- **Thời gian thực hiện:** 02/11/2026 (UTC+7)
- **File kết quả đề xuất:** `docs/pm/tickets/GH-33-titles.json`
- **Phạm vi tuân thủ:** Chỉ ghi `docs/pm/tickets/GH-33-titles.json` và `docs/pm/tickets/GH-33-titles-report.md`. Không sửa 12 file spec trong `data/stier/specs/*.json` (`lines`, `hook`, `scenes` đã render giữ nguyên), không dùng Google Autocomplete API, không ghi `state.sqlite`, không chạy lệnh git, không đăng YouTube.

---

## 1. Phương pháp thu thập từ khóa & kiểm chứng

1. **Google Trends VN (`geo=VN`, ngày 01–02/11/2026) & Báo chí Việt Nam dẫn đầu:**
   - Đối chiếu dữ liệu xu hướng tại Việt Nam (`trends.google.com`, `GH-31-benchmark.json`, `output/trend/2026-11-02/12.md`) và các bài báo đang dẫn đầu trên VnExpress, Thanh Niên, Tuổi Trẻ, Dân Trí, VietNamNet, VnEconomy, CafeF, GenK cùng nguồn sơ cấp trong `docs/pm/tickets/GH-33-CK-facts.json` và `docs/pm/tickets/GH-33-MIM-facts.json`.
2. **Tìm kiếm YouTube VN (gõ tay, không dùng autocomplete API):**
   - Tra cứu trực tiếp các cụm từ khóa người Việt tìm kiếm cho từng sự kiện trên YouTube VN để xác định cách đặt từ khóa ở 3–4 từ đầu tiêu đề.
3. **Cấu trúc Title SS-Tier áp dụng cho 24 phương án (12 Short × 2 phương án):**
   - **3–4 từ đầu:** Đặt chính xác cụm từ khóa chính (`keyword_primary`) mà người dùng đang tìm (`Giá xăng hôm nay`, `Giá điện giảm`, `Giá vàng SJC`, `Thuế hộ kinh doanh`, `Lãi suất tiết kiệm`, `Binance bị hack`, `Cấm nhập điện thoại cũ`, `Sam Altman chê RAM`, `Lỗ hổng Android`, `Tác nhân AI`, `Vệ tinh AI Google`).
   - **Vế sau:** Nối trực tiếp bằng cặp số đối nghịch hoặc mâu thuẫn thật có trong `facts.json` và được giải quyết trọn vẹn trong `lines` của kịch bản.
   - **Độ dài:** Toàn bộ 24 phương án đều đạt **53–59 ký tự** (≤ 60 ký tự, tiếng Việt có dấu).
   - **Tuân thủ luật kênh:**
     - **CK:** Mỗi tiêu đề đều có **một khoản tiền/tỷ lệ × một mốc thời gian**; không nêu tên ngân hàng thương mại, công ty chứng khoán, hãng xe hay mã cổ phiếu; không khuyến nghị mua/bán; giữ nguyên câu miễn trừ `"Nội dung giáo dục, không phải tư vấn đầu tư."` ở cuối `description_head`.
     - **MIM:** Nêu rõ tên tổ chức/nhân vật thật + con số kỹ thuật/bước ngoặt; giữ nguyên câu ghi công `"Giọng đọc tổng hợp từ nguồn công khai."` ở cuối `description_head`.
     - **Từ cấm trong mô tả công khai (`AGENTS.md`):** Đã quét tự động, đảm bảo 0 trường hợp chứa `<`, `>`, `"CẦN"`, `"cần kiểm"`, `"WebFetch"`, `"factcheck"`, `"data/long"`, `"tìm kiếm"`, `"agent"`.

---

## 2. Bảng tổng hợp từ khóa và 2 phương án Title cho 12 Short Pilot

### Kênh CK — Biểu Đồ Biết Nói (6 Short)

| # | Slug | Từ khóa chính (3–4 từ đầu) | Title hiện tại trong Spec | Phương án khuyên dùng (`title_recommended`) | Phương án thay thế (`title_alt`) | Bằng chứng từ khóa (Trends VN / Báo VN / YouTube VN) |
|---|---|---|---|---|---|---|
| 1 | `ck-thue-xang-0-giam-1804` | `giá xăng hôm nay` | Xăng giảm 1.804 đồng/lít từ 1/11: 5 tháng thuế 0% *(49c)* | **Giá xăng hôm nay giảm 1.804 đồng/lít: 5 tháng thuế 0%** *(53c)* | Giá xăng hôm nay hạ 1.804đ: 5 tháng thuế 0%, cước chưa giảm *(59c)* | **Trends VN (01–02/11):** "giá xăng hôm nay" tăng nhiệt khi NQ 45/2026/NQ-CP có hiệu lực. **Báo VN:** [Thanh Niên](https://thanhnien.vn/gia-xang-dau-hom-nay-111-gia-xang-giam-manh-185261101074743844.htm), [VnExpress](https://vnexpress.net/thue-tieu-thu-dac-biet-voi-xang-ve-0-tu-ngay-mai-5139239.html), [Dân Trí](https://dantri.com.vn/kinh-doanh/gia-xang-dien-dong-loat-ha-nhiet-sao-cuoc-van-tai-chua-giam-20261102164011827.htm). **YouTube VN:** các bản tin mở đầu bằng "Giá xăng hôm nay" + mức giảm "1.804 đồng/lít". |
| 2 | `ck-dien-giam-44-dong-20-nam` | `giá điện giảm` | Sau 20 năm, giá điện giảm 44 đồng/kWh từ ngày 1/11 *(50c)* | **Giá điện giảm 44 đồng/kWh: Lần đầu hạ sau gần 20 năm tăng** *(57c)* | Giá điện giảm 2% về 2.159 đồng/kWh: Lần đầu sau 20 năm *(54c)* | **Trends VN (01–02/11):** "giá điện giảm" được tra cứu mạnh ngày 01/11. **Báo VN:** [VnExpress](https://vnexpress.net/gia-dien-giam-2-tu-ngay-mai-5139154.html), [VietNamNet](https://vietnamnet.vn/gia-dien-giam-hon-44-dong-kwh-tu-ngay-mai-1-11-2570253.html), [EVN](https://www.evn.com.vn/d6/news/Dieu-chinh-gia-ban-le-dien-binh-quan-tu-ngay-01-thang-11-nam-2026-6-12-32537.aspx). **YouTube VN:** kết quả đầu đều đặt "Giá điện giảm 2%" / "44 đồng/kWh" ở đầu tít. |
| 3 | `ck-vang-sjc-140-trieu-chenh-14-trieu` | `giá vàng SJC` | Vàng SJC 140 triệu ngày 2/11: Cao hơn thế giới 14,3 triệu *(57c)* | **Giá vàng SJC 140 triệu ngày 2/11: Vênh thế giới 14,3 triệu** *(58c)* | Giá vàng SJC 140 triệu: Sau 2 tuần lỗ 11 triệu vì chênh giá *(59c)* | **Trends VN (01–02/11):** "giá vàng", "giá vàng SJC" dẫn đầu xu hướng tài chính tại VN. **Báo VN:** [CafeF](https://cafef.vn/gia-vang-ngay-2-11-vang-sjc-cao-hon-the-gioi-143-trieu-dong-luong-188261102073347541.chn), [VnExpress](https://vnexpress.net/gia-vang-mieng-dao-chieu-len-140-trieu-dong-mot-luong-5139574.html), [Thanh Niên](https://thanhnien.vn/gia-vang-hom-nay-1112026-lao-doc-day-nguoi-mua-lo-hon-11-trieu-sau-2-tuan-185261031181409164.htm). **YouTube VN:** bản tin giá vàng đều mở bằng "Giá vàng SJC". |
| 4 | `ck-ho-kinh-doanh-giam-30-thue` | `thuế hộ kinh doanh` | Doanh thu dưới 10 tỷ: Giảm 30% thuế thu nhập 2026–2027 *(54c)* | **Thuế hộ kinh doanh giảm 30% năm 2026: Ngưỡng cắt cứng 10 tỷ** *(59c)* | Thuế hộ kinh doanh dưới 10 tỷ/năm: Giảm ngay 30% năm 2026 *(57c)* | **Báo VN dẫn đầu:** [Báo Chính phủ](https://baochinhphu.vn/huong-dan-chi-tiet-giam-30-so-thue-tncn-thue-tndn-phai-nop-tu-kinh-doanh-co-doanh-thu-khong-qua-10-ti-dong-102261030095834891.htm), [VietNamNet](https://vietnamnet.vn/doanh-thu-khong-qua-10-ty-dong-nam-duoc-giam-30-thue-thu-nhap-ca-nhan-2570192.html), [CafeF](https://cafef.vn/tu-nay-tat-ca-cac-ca-nhan-ho-kinh-doanh-co-doanh-thu-duoi-10-ty-dong-chinh-thuc-don-tin-vui-188261102115842922.chn). **YouTube VN:** video hướng dẫn của LuatVietnam và VTV dùng cụm "hộ kinh doanh" + "giảm 30% thuế". |
| 5 | `ck-lai-giam-05-tien-gui-80-ngan-han` | `lãi suất tiết kiệm` | Lãi giảm 0,5%, sao 80% tiền gửi vẫn nằm ở kỳ hạn ngắn *(53c)* | **Lãi suất tiết kiệm giảm 0,5%/năm: Sao 80% vẫn gửi ngắn hạn?** *(59c)* | Lãi suất tiết kiệm tháng 11 hạ 0,5%: 80% tiền gửi ngắn hạn *(58c)* | **Báo VN dẫn đầu:** [VietNamNet](https://vietnamnet.vn/lai-suat-ngan-hang-hom-nay-2-11-giam-toi-0-5-diem-phan-tram-o-nhieu-ky-han-2570538.html), [VnExpress](https://vnexpress.net/thong-doc-nguoi-dan-gui-tien-nhieu-vi-tin-tuong-he-thong-ngan-hang-5139105.html), [CafeF](https://cafef.vn/lai-suat-dau-thang-11-2026-tien-gui-tiet-kiem-dong-loat-ha-nhiet-chung-chi-tien-gui-dieu-chinh-nhe-188261030160856073.chn). **YouTube VN:** người gửi tiền tìm trực tiếp cụm "lãi suất tiết kiệm tháng 11". |
| 6 | `ck-binance-63-ty-rut-36-ty` | `Binance bị hack` | Mất 6,3 tỷ đô trong 20 phút: 3,6 tỷ đô rút khỏi Binance *(55c)* | **Binance bị hack 6,3 tỷ đô: Rút 3,64 tỷ đô trong 9,5 giờ đầu** *(59c)* | Binance bị hack 6,3 tỷ đô: Bù 95%, khách vẫn rút 3,64 tỷ đô *(59c)* | **Trends VN & Báo VN:** [VnEconomy](https://vneconomy.vn/binance-vua-khoi-phuc-chuc-nang-rut-tien-36-ty-usd-chay-khoi-san.htm), [VietNamNet](https://vietnamnet.vn/binance-mo-lai-cong-rut-tien-bu-dap-95-tai-san-vu-hack-6-3-ty-usd-tien-ma-hoa-2570465.html), [VnExpress](https://vnexpress.net/hacker-thu-nghiem-truoc-36-tieng-rut-6-3-ty-usd-tu-vi-binance-trong-20-phut-5139116.html). **YouTube VN:** cụm "Binance bị hack" chiếm ưu thế tuyệt đối ở 3 từ đầu. |

---

### Kênh MIM — Mind in the Machine (6 Short)

| # | Slug | Từ khóa chính (3–4 từ đầu) | Title hiện tại trong Spec | Phương án khuyên dùng (`title_recommended`) | Phương án thay thế (`title_alt`) | Bằng chứng từ khóa (Trends VN / Báo VN / YouTube VN) |
|---|---|---|---|---|---|---|
| 7 | `mim-binance-20-phut-6-3-ty` | `Binance bị hack` | Thử Ngầm 36 Giờ, Rút 6,3 Tỷ Đô Trên Binance Trong 20 Phút *(57c)* | **Binance Bị Hack 6,3 Tỷ Đô Trong 20 Phút: Khóa Cứng 3 Tỷ Đô** *(58c)* | Binance Bị Hack 6,3 Tỷ Đô 2026: FBI Điểm Tên TraderTraitor *(58c)* | **Trends VN & Báo VN:** [VietNamNet](https://vietnamnet.vn/24-gio-hon-loan-khi-binance-bi-hack-6-3-ty-usd-2570580.html), [VnExpress](https://vnexpress.net/hacker-thu-nghiem-truoc-36-tieng-rut-6-3-ty-usd-tu-vi-binance-trong-20-phut-5139116.html), [FBI](https://www.fbi.gov/news/press-releases/north-korea-responsible-for-6-billion-binance-attack). **YouTube VN:** tìm kiếm "Binance bị hack" trả về các video mổ xẻ vụ trộm 6,3 tỷ USD trong 20 phút. |
| 8 | `mim-cam-nhap-dien-thoai-cu-2027` | `cấm nhập điện thoại cũ` | Từ 01/01/2027: Cấm Nhập Điện Thoại, Máy Tính Đã Qua Sử Dụng *(59c)* | **Cấm Nhập Điện Thoại Cũ 01/01/2027: Khóa Cả Hàng Tân Trang** *(57c)* | Cấm Nhập Điện Thoại Cũ Năm 2027: Chặn Cả Linh Kiện Tháo Rời *(59c)* | **Báo VN dẫn đầu:** [Tuổi Trẻ](https://tuoitre.vn/tu-1-1-2027-cam-nhap-khau-dien-thoai-may-tinh-may-anh-da-qua-su-dung-100261102115347102.htm), [Dân Trí](https://dantri.com.vn/cong-nghe/loat-thiet-bi-cong-nghe-cu-bi-cam-nhap-khau-tu-nam-2027-20261101142208624.htm), [GenK](https://genk.vn/chinh-thuc-1-1-2027-cam-nhap-khau-dien-thoai-may-tinh-may-anh-da-qua-su-dung-165261102155917362.chn). **YouTube VN:** người dùng tìm cụm "cấm nhập điện thoại cũ 2027". |
| 9 | `mim-sam-altman-ram-5-phan-tram` | `Sam Altman chê RAM` | Sam Altman Chê RAM Máy Cá Nhân Bỏ Phí, Elon Musk Phản Bác *(57c)* | **Sam Altman Chê RAM Máy Cá Nhân Chỉ Dùng 5%: Musk Phản Bác** *(57c)* | Sam Altman Chê RAM PC Dùng 5% Thời Gian, Elon Musk Đáp Trả *(58c)* | **Báo VN dẫn đầu:** [VnExpress (31/10)](https://vnexpress.net/sam-altman-that-te-khi-ram-nam-trong-may-nguoi-dung-5139149.html), [VnExpress (02/11)](https://vnexpress.net/musk-phan-bac-altman-noi-moi-nguoi-cung-can-co-ram-5139778.html), [Thanh Niên](https://thanhnien.vn/ceo-openai-gay-tranh-cai-khi-muon-han-che-ram-cho-may-tinh-ca-nhan-185261101104950892.htm), [GenK](https://genk.vn/giua-luc-openai-hup-het-ram-toan-cau-sam-altman-cho-rang-ram-o-trong-may-ban-va-toi-dang-bi-bo-phi-165261031114631001.chn). **YouTube VN:** các video thảo luận đặt "Sam Altman" + "RAM" ở 4 từ đầu. |
| 10 | `mim-android-20-tin-nhan-tu-than` | `lỗ hổng Android` | Không Cần Mở Xem: 20 Tin Nhắn Ngầm Làm Treo Cứng Android *(56c)* | **Lỗ Hổng Android Tin Nhắn Tử Thần: 8 Byte, 20 Tin Sập Máy** *(56c)* | Lỗ Hổng Android CVE-2026-58882: 20 Tin Nhắn Ngầm Treo Máy *(57c)* | **Trends VN (02/11):** từ khóa "lỗ hổng" lọt top Google Trends VN ngày 02/11. **Báo VN:** [Thanh Niên](https://thanhnien.vn/hang-trieu-nguoi-dung-android-bi-de-doa-vi-lo-hong-tin-nhan-tu-than-185261101133145557.htm), [Dân Trí](https://dantri.com.vn/cong-nghe/lo-hong-khien-dien-thoai-android-gap-loi-nghiem-trong-20261102101554706.htm). **YouTube VN:** kết hợp cả 2 cụm "Lỗ hổng Android" và "Tin nhắn tử thần" ngay phần mở tiêu đề. |
| 11 | `mim-9-tren-10-ai-tu-lay-otp` | `tác nhân AI` | 9 Trên 10 Mô Hình AI Tự Đọc Email Lấy Mã OTP Vượt Hạn Mức *(57c)* | **Tác Nhân AI Tự Đọc Email Lấy OTP: 9/10 Mô Hình Vượt Hạn Mức** *(59c)* | Tác Nhân AI Vượt Khóa Ví 1 Xu: 9/10 Mô Hình Tự Lấy Mã OTP *(57c)* | **Báo VN dẫn đầu:** [VnExpress](https://vnexpress.net/elon-musk-tac-nhan-ai-se-hack-he-thong-de-kiem-tien-cho-chinh-chung-5139352.html), [GenK](https://genk.vn/elon-musk-tac-nhan-ai-co-the-hack-he-thong-de-tu-kiem-tien-16526110210020866.chn), [arXiv:2610.35835](https://arxiv.org/abs/2610.35835). **YouTube VN:** cụm Việt hóa "Tác nhân AI" đứng đầu tít (đồng thời tránh từ cấm `"agent"` trong mô tả công khai). |
| 12 | `mim-ve-tinh-google-4-chip-tpu` | `vệ tinh AI Google` | Google Đưa 4 Chip TPU Lên Vũ Trụ, Gửi Thơ Về Trái Đất *(53c)* | **Vệ Tinh AI Google Chạy 4 Chip TPU: Viết 3 Dòng Thơ Vũ Trụ** *(57c)* | Vệ Tinh AI Google Gắn 4 Chip TPU: Đưa Máy Chủ Lên Quỹ Đạo *(57c)* | **Báo VN dẫn đầu:** [VnExpress](https://vnexpress.net/ve-tinh-ai-cua-google-gui-phan-hoi-dau-tien-tu-khong-gian-5139248.html), [Thanh Niên](https://thanhnien.vn/ve-tinh-ai-cua-google-vua-lam-tho-tu-vu-tru-185261031214642948.htm), [Google Research](https://blog.google/innovation-and-ai/models-and-research/google-research/project-suncatcher-satellite-response/). **YouTube VN:** cụm "Vệ tinh AI Google" / "Vệ tinh AI của Google" dẫn đầu kết quả. |

---

## 3. Cấu trúc Mô tả (`description_head`), Hashtag và Tag

Trong `docs/pm/tickets/GH-33-titles.json`, mỗi mục cung cấp:
- `description_head`: Gồm **2 câu đầu chứa từ khóa chính và từ khóa phụ**, tóm tắt đúng dữ kiện đã kiểm chứng trong kịch bản, nối tiếp bằng câu miễn trừ bắt buộc của CK (`"Nội dung giáo dục, không phải tư vấn đầu tư."`) hoặc câu ghi công của MIM (`"Giọng đọc tổng hợp từ nguồn công khai."`). Khi Lead áp vào spec, trường `sources` hiện có trong từng file `data/stier/specs/<slug>.json` được giữ nguyên 100%.
- `hashtags`: **5 hashtag/video** (gồm hashtag nhận diện kênh `#BieuDoBietNoi`, `#TaiChinhCaNhan` cho CK; `#MindInTheMachine`, `#AI` / `#CongNghe` / `#AnNinhMang` cho MIM, kết hợp 3 hashtag từ khóa sự kiện).
- `tags`: **10–11 tag/video** (nằm trong khung 8–12 tag), bao phủ từ khóa chính, từ khóa phụ, số hiệu văn bản/CVE và tên riêng đã xác thực.

---

## 4. Kết quả chạy lệnh kiểm tra & Kiểm trùng tiêu đề

Đã chạy lệnh kiểm tra tự động bằng PowerShell kết hợp `sqlite3.exe` ở chế độ chỉ đọc (`file:state.sqlite?mode=ro`):
- **Đối chiếu trùng lặp:**
  - `data/channel_titles/CK.json`: 104 tiêu đề hiện có.
  - `data/channel_titles/MIM.json`: 116 tiêu đề hiện có.
  - `state.sqlite` (`upload_log`): 360 bản ghi tiêu đề đã lên lịch / xuất bản.
  - **Kết quả:** `Dup=False,False` trên cả 12 Short (0 trùng lặp cho cả `title_recommended` và `title_alt`).
- **Kết quả kiểm tra độ dài và từ cấm:**
  ```text
  ck-thue-xang-0-giam-1804 | Rec=53c | Alt=59c | H=5 | T=11 | Dup=False,False | Bad=
  ck-dien-giam-44-dong-20-nam | Rec=57c | Alt=54c | H=5 | T=11 | Dup=False,False | Bad=
  ck-vang-sjc-140-trieu-chenh-14-trieu | Rec=58c | Alt=59c | H=5 | T=10 | Dup=False,False | Bad=
  ck-ho-kinh-doanh-giam-30-thue | Rec=59c | Alt=57c | H=5 | T=10 | Dup=False,False | Bad=
  ck-lai-giam-05-tien-gui-80-ngan-han | Rec=59c | Alt=58c | H=5 | T=10 | Dup=False,False | Bad=
  ck-binance-63-ty-rut-36-ty | Rec=59c | Alt=59c | H=5 | T=10 | Dup=False,False | Bad=
  mim-binance-20-phut-6-3-ty | Rec=58c | Alt=58c | H=5 | T=10 | Dup=False,False | Bad=
  mim-cam-nhap-dien-thoai-cu-2027 | Rec=57c | Alt=59c | H=5 | T=10 | Dup=False,False | Bad=
  mim-sam-altman-ram-5-phan-tram | Rec=57c | Alt=58c | H=5 | T=10 | Dup=False,False | Bad=
  mim-android-20-tin-nhan-tu-than | Rec=56c | Alt=57c | H=5 | T=10 | Dup=False,False | Bad=
  mim-9-tren-10-ai-tu-lay-otp | Rec=59c | Alt=57c | H=5 | T=10 | Dup=False,False | Bad=
  mim-ve-tinh-google-4-chip-tpu | Rec=57c | Alt=57c | H=5 | T=10 | Dup=False,False | Bad=
  ```

---

## 5. Khẳng định không kiểm được (đã loại trừ khỏi Title, Mô tả và Tag)

Theo đúng hồ sơ `GH-33-CK-facts.json` và `GH-33-MIM-facts.json`, các chi tiết chưa kiểm chứng sau đã bị loại hoàn toàn khỏi mọi phương án tiêu đề và mô tả:
1. **`ck-binance-63-ty-rut-36-ty`:** Không dùng con số *"rút 6 tỷ USD khi mở lại cổng"* (con số thực tế rút ròng trong 9,5 giờ đầu là **3,64 tỷ USD**, tương đương 2,1% tổng tài sản trên sàn; 6,3 tỷ USD là số tiền bị hack hôm 29/10).
2. **`ck-dien-giam-44-dong-20-nam`:** Không gắn mốc *"giá điện giảm 2% áp dụng đến hết 31/03/2027"* (mốc 31/03/2027 là của Nghị quyết 45/2026/NQ-CP về thuế TTĐB xăng, còn Quyết định 1305/QĐ-EVN chỉ ghi hiệu lực từ 01/11/2026).
3. **`ck-vang-sjc-140-trieu-chenh-14-trieu`:** Chỉ nêu mức vênh đã xác thực trong kịch bản (*"từ 14,3 triệu đồng/lượng"* theo công thức quy đổi của CafeF sáng 02/11) kèm chênh mua-bán 3 triệu đồng tại quầy.
4. **`ck-lai-giam-05-tien-gui-80-ngan-han`:** Không nêu số dư tuyệt đối tiền gửi dân cư hết tháng 10/2026 (chưa công bố chính thức tại phiên giải trình 31/10), chỉ dùng tỷ trọng **80% tiền gửi ngắn hạn** và mức giảm **0,5%/năm**.
5. **`ck-ho-kinh-doanh-giam-30-thue`:** Không đưa con số ước tính tổng giảm thu ngân sách của Nghị định 398/2026/NĐ-CP.
6. **`mim-binance-20-phut-6-3-ty`:** Không đưa tin đồn chưa xác thực về việc kỹ sư nội bộ mở file độc hại trên laptop cá nhân.
7. **`mim-cam-nhap-dien-thoai-cu-2027`:** Không đưa dự đoán cảm tính *"giá điện thoại cũ tăng 15–30%"*.
8. **`mim-sam-altman-ram-5-phan-tram`:** Không đưa tin đồn phần trăm sản lượng DRAM toàn cầu mà OpenAI đặt mua trước năm 2027.
9. **`mim-ve-tinh-google-4-chip-tpu`:** Không nêu chi phí chế tạo bằng tiền USD của vệ tinh Suncatcher (Google không công bố).
10. **`mim-9-tren-10-ai-tu-lay-otp`:** Ghi rõ đây là kết quả **thử nghiệm bảo mật** của Cornell Tech và Đại học Yale (chưa có vụ mất tiền ngoài đời thực từ lỗi I-HITL).
11. **`mim-android-20-tin-nhan-tu-than`:** Không tự gán số triệu máy Android 12–13 cụ thể tại Việt Nam.
