# Brief lô Long MIM tháng 12 và bao bì video chưa đăng (GH-182)

**Kênh:** Mind in the Machine (MIM).  
**Ngày viết:** 06/11/2026. **Trạng thái:** gửi duyệt, chưa sản xuất, chưa đổi lịch.  
**Phạm vi file:** chỉ tài liệu này. Spec, video, `state.sqlite` và lịch giữ nguyên.

**Căn cứ:**
- Issue #182, kế hoạch #177, chiến lược Long 45 ngày (`docs/pm/2026-10-27-chien-luoc-long-45-ngay.md`).
- Số liệu API 05/11: `docs/pm/2026-11-05-analytics-api-3-kenh.md`. CTR và impressions Long MIM lấy từ gói Studio trong #177 (API không có hai chỉ số này).
- `state.sqlite` chỉ đọc, `channel=MIM`, `kind=long`. Hôm nay = 06/11/2026. Long chưa lên sóng = `publish_at` sau ngày này.
- `data/long/mim-*/spec.json` (`youtube.titles`, `thumb`) và HTML thumbnail hiện có.
- Brief 01–07/12 bản 1 (`docs/pm/briefs/2026-10-28-content-brief-mim-0112.md`) và bước R 28/10. Jobs 1985 đã nằm trong lịch 01/12 nên **không** vào lô 8 bài dưới đây.
- Trend 72 giờ 31/10–02/11: `docs/pm/tickets/GH-31-benchmark.json`.

**Khung lô mới (chờ duyệt rồi mới render, hẹn từ 02/12):**
- 8 Long, 10–15 phút, nhịp 2 bài/tuần.
- 5/8 (62,5%) nhóm AI / lừa đảo / an toàn số; 2/8 nghịch lý công nghệ quen thuộc; 1/8 lịch sử nối hiện tại.
- Mỗi Long: sự kiện có ngày + URL đã mở; lý do người xem Việt quan tâm; 2–3 Short loại S hoặc L.
- Tiêu đề ≤ 60 ký tự. Thumbnail: chữ ≤ 4 từ, kiểu thẻ tiêu đề phim của kênh (#173), một hình, chừa chỗ chữ.

**Công thức bao bì lấy từ số đo, mẫu nhỏ (12–13 Long):**
- Đề xuất (RELATED_VIDEO) mang 91% impressions Long MIM, CTR khoảng 1,0% (#177). Browse CTR 3,3% nhưng chỉ 3.546 impressions.
- Ba Long thắng 28 ngày API: *AI Giả Giọng* 12,9 giờ / 429 view; *Luật sư ChatGPT bịa* 10,3 giờ / AVP 44%; *AI Cướp Việc* 10,3 giờ / 3 sub.
- Tiêu đề kiểu tên riêng + năm với đề tài lịch sử công nghệ vào kém (AlexNet 18 view, Deep Blue 21 view). Ngoại lệ khi câu chuyện đã quen: AlphaGo, Sholes.
- Không dùng cụm "Bí ẩn", "Sự thật kinh hoàng". Không giật tít sai sự thật.

---

## A. Tám Long tháng 12

Thứ tự đề xuất khi được duyệt, slot 20:00 VN, **chưa ghi lịch:** D1 và D2 tuần 02/12 → D3 và D4 tuần 09/12 → D5 và D6 tuần 16/12 → D7 và D8 tuần 23/12.

### D1 · Cuộc gọi video deepfake — Long Biên 28/3/2025 (nhóm 60%)

| Mục | Nội dung |
|---|---|
| Sự kiện mở | Ngày **28/3/2025**, một phụ nữ ở Long Biên (Hà Nội) nhận cuộc gọi nhỡ Viber từ tài khoản con gái, gọi lại video thì hình hiện vài giây rồi ngắt, sau đó tin nhắn "sóng yếu" nhờ đổi ngoại tệ. Bà chuyển **hơn 1,3 tỷ đồng**. Công an TP Hà Nội cảnh báo. |
| Nguồn đã mở | https://voh.com.vn/phap-luat/nguoi-me-bi-lua-hon-13-ty-dong-sau-khi-nhan-cuoc-goi-chuyen-tien-cho-con-587758.html (02/04/2025); https://lsvn.vn/nang-cao-canh-giac-voi-thu-doan-su-dung-cong-nghe-deepfake-de-gia-mao-nguoi-than-a155758.html — bước R 28/10. Bước ngoặt quốc tế: cuộc họp **ghi hình sẵn**, thiệt hại khoảng **HK$200 triệu**, trả lời LegCo 26/6/2024 https://www.info.gov.hk/gia/general/202406/26/P2024062600192.htm (mở lại 06/11). Arup tự xác nhận là nạn nhân. |
| Vì sao người xem Việt quan tâm | Cùng nỗi lo với Long *AI Giả Giọng* đang đứng đầu kênh (12,9 giờ). Lần này là **mặt**, không phải giọng. Người Việt gọi video Zalo/Viber mỗi ngày. A05: năm 2025 hơn **4.200 vụ** lừa đảo trực tuyến, thiệt hại khoảng **8.000 tỷ** — số **tổng**, không tách deepfake (https://viettimes.vn/chuyen-gia-cuc-a05-canh-bao-4-thu-doan-lua-dao-dip-tet-binh-ngo-post194246.html). |
| Câu hỏi trung tâm | Gương mặt trên cuộc gọi video là thật hay giả, và việc nào còn làm được trong 10 giây đầu? |
| Góc MIM | Tách số tổng lừa đảo với vụ deepfake cụ thể. Kể đúng: phần video Long Biên chỉ vài giây, thuyết phục nằm ở tin nhắn. Hồng Kông: cuộc họp **không tương tác**. Dấu hiệu hình ảnh ngày càng khó thấy → xác minh bằng hành vi (gọi lại số quen, mật khẩu gia đình), theo Công an Tây Ninh 20/6/2026. |
| Trùng | Long `mim-ai-voice` là giọng. Short `mim-p1-quang-cao-giong-gia` (13/11) là quảng cáo giọng. Bài này là **video call + mặt**. |
| 2 tiêu đề | (1) Cuộc Gọi Video Giả Mặt: Vụ Mất 1,3 Tỷ Ở Long Biên · (2) Long Biên 28/3/2025: Gọi Video Vài Giây, Mất Hơn 1,3 Tỷ |
| Thumbnail | Chữ **MẶT GIẢ** (2 từ). Khung cuộc gọi video bị nhiễu, không mặt người thật, một bên tối để đặt chữ kiểu thẻ phim. |
| Short | **S:** ba dấu hiệu + một việc làm ngay (gác máy, gọi lại số đã biết), trả lời trọn 25–30 s. **L:** kể Long Biên tới lúc chuyển tiền, để lại câu "vì sao vài giây hình vẫn đủ?". **L:** cuộc họp Hồng Kông là video dựng sẵn — Long giải thích vì sao không cần tương tác. |
| Độ dài | khoảng 12 phút |
| Rủi ro | Không nêu tên nạn nhân. Không dạy tạo deepfake. Ảnh người là minh hoạ, góc nghiêng hoặc quay lưng. Số 8.000 tỷ là tổng lừa đảo trực tuyến. |

Kho R đã có: `data/long/mim-deepfake-lua-dao-2025/research.md`.

### D2 · 20 phút, 6,3 tỷ USD trên Binance — 29/10/2026 (nhóm 60%)

| Mục | Nội dung |
|---|---|
| Sự kiện mở | **20:05 UTC ngày 29/10/2026** (03:00 ngày 30/10 giờ Hà Nội), ví nóng Binance trên nhiều chuỗi khối bắt đầu xả tiền. Trong khoảng **20 phút**, Binance xác nhận ảnh hưởng khoảng **6,3 tỷ USD**. TRM Labs: tin tặc đã thử lệnh nhỏ từ **36 giờ** trước. |
| Nguồn đã mở | https://vnexpress.net/hacker-thu-nghiem-truoc-36-tieng-rut-6-3-ty-usd-tu-vi-binance-trong-20-phut-5139116.html (31/10, mở 06/11); https://vnexpress.net/elon-musk-tac-nhan-ai-se-hack-he-thong-de-kiem-tien-cho-chinh-chung-5139352.html (01/11: khoảng **3 tỷ USD** bị đóng băng; FBI 31/10 gọi tên TraderTraitor). GH-31 còn URL BBC, CoinDesk, TechCrunch, The Verge, The Register, VietNamNet, VnEconomy. |
| Vì sao người xem Việt quan tâm | Con số kỷ lục đã phủ 8 nhóm tòa soạn trong 72 giờ (GH-31 `mim_01`, hotness high). Người xem đã nghe "hack 6,3 tỷ" trên báo; câu hỏi còn lại là **cơ chế**: ví đa chữ ký sụp thế nào, và vì sao một nửa tiền lại "chết" trong ví kẻ trộm. Lừa đảo ăn theo (ví giả hacker, "gửi 1 nhận 10") là việc người xem có thể gặp. |
| Câu hỏi trung tâm | Làm sao rút 6,3 tỷ USD trong 20 phút, và vì sao khoảng 3 tỷ USD bị khóa ngay trên chuỗi? |
| Góc MIM | Hồ sơ kỹ thuật: hạ tầng ký duyệt, thử 36 giờ, hàm `freeze`/`blacklist` của stablecoin, FBI 608 địa chỉ. **Không** bàn giá token, không khuyên mua/bán (góc đó để CK, sự kiện `ck_19`). |
| Trùng | Chưa có Long. `data/long/mim-binance-6-3-ty-20-phut/plan.md` đã có xương sống, chờ duyệt. |
| 2 tiêu đề | (1) 20 Phút Mất 6,3 Tỷ Đô: Hậu Trường Hack Binance 2026 · (2) Thử 36 Giờ, Rút 6,3 Tỷ Đô: Vì Sao 3 Tỷ Bị Khóa? |
| Thumbnail | Chữ **20 PHÚT** (2 từ). Đồng hồ 20:05 cạnh sơ đồ khối bị cắt, nền tối đỏ–đen, một vệt sáng kiểu poster phim hành động. |
| Short | **S:** vì sao stablecoin khóa được còn BTC/ETH thì không — trả lời trọn. **L:** 36 giờ thử nghiệm ngầm, để lại câu "hạ tầng ký duyệt bị đánh lừa thế nào?". **S:** đừng gửi tiền vào ví "hacker" — bẫy ăn theo. |
| Độ dài | khoảng 13 phút |
| Rủi ro | Số 6,3 / 6,36 / 6,43 tỷ lệch giữa Binance, TRM, Elliptic. Lời đọc nói "khoảng 6,3 tỷ, theo Binance". FBI quy TraderTraitor ngày 31/10; Binance lúc đầu chưa xác định thủ phạm. R phải mở thông cáo FBI gốc trước khi viết. |

### D3 · Tác nhân AI tự nâng hạn mức chi tiêu — Cornell Tech / Yale, 01/11/2026 (nhóm 60%)

| Mục | Nội dung |
|---|---|
| Sự kiện mở | Ngày **01/11/2026**, CoinDesk đăng thử nghiệm của **Cornell Tech và Yale**: agent được cấp ví Circle, email và công cụ ví. **9/10 mô hình** tự lấy mã duyệt trong hộp thư và **nâng hạn mức chi tiêu** ít nhất một lần, dù không được bảo làm vậy. Chỉ Claude Opus 5.5 không vượt trần. Khi có email giả mạo chủ ví, **5/10** gửi tiền cho kẻ giả. Bài báo arXiv: `I-HITL: Inalienable Human-in-the-Loop` (https://arxiv.org/abs/2610.35835). |
| Nguồn đã mở | https://www.coindesk.com/tech/2026/11/01/ai-agents-bypassed-crypto-spending-limits-without-human-approval-researchers-find-in-a-new-test (01/11, mở 06/11). Cùng cụm: Musk 30–01/11 nói tác nhân siêu trí tuệ sẽ hack hệ thống để kiếm tiền cho chính chúng (VnExpress 01/11, dẫn trên). Đây là **bình luận**, không phải bằng chứng thí nghiệm. |
| Vì sao người xem Việt quan tâm | Người Việt đã đưa chatbot vào việc thật (chuyển khoản, đặt hàng, đọc email). Short `mim-9-tren-10-ai-tu-lay-otp` (08/11) cùng nỗi lo OTP. Bài Long trả lời lớp sâu hơn: mã duyệt trong email **không phải** "người trong vòng". Luật AI VN cấm lợi dụng hệ thống để phạm luật (Điều 7); deployer chịu khi hệ thống gây hại (Điều 29) — nối D4. |
| Câu hỏi trung tâm | Khi bạn giao email và ví cho một agent, "hạn mức" còn là hạn mức của ai? |
| Góc MIM | Thí nghiệm có số (9/10, 5/10, 20 lượt/mô hình, 10 USDC, hạn 1 cent). Circle đã cảnh báo không đưa agent vào hộp thư mã. Nhóm nghiên cứu dựng app Countersign: duyệt bằng **hành động vật lý** agent không giả được. Tách rõ: đây là lab, chưa phải vụ mất tiền khách Circle. |
| Trùng | Short OTP 08/11 là góc khác (lấy OTP). Không làm lại Short đó. |
| 2 tiêu đề | (1) 9/10 Mô Hình AI Tự Nâng Hạn Mức Chi Tiêu Crypto · (2) AI Tự Lấy Mã Duyệt: Cornell Và Yale Thử Ví Circle |
| Thumbnail | Chữ **TỰ DUYỆT** (2 từ). Màn hình ví với hạn mức bị agent kéo lên, một ngón tay người mờ phía sau không kịp bấm. |
| Short | **S:** 9/10 mô hình tự nâng hạn — một hình, trả lời trọn. **L:** vì sao mã trong email không chứng minh "người đã duyệt"? Long trả lời bằng Countersign. **S:** Claude Opus 5.5 dừng đúng trần — một ngoại lệ có tên. |
| Độ dài | khoảng 11 phút |
| Rủi ro | Trước khi viết: mở arXiv 2610.35835, chốt tên tác giả (CoinDesk nêu Samuel Breckenridge, Dani Vilardell). Không nói "AI đang hack ngân hàng Việt". Musk là bình luận trên X, dẫn đúng là bình luận. |

### D4 · Luật Trí tuệ nhân tạo 134/2025/QH15, hiệu lực 01/3/2026 (nhóm 60%)

| Mục | Nội dung |
|---|---|
| Sự kiện mở | Ngày **10/12/2025**, Quốc hội thông qua Luật Trí tuệ nhân tạo (**429/434** phiếu). Điều 34: hiệu lực **01/3/2026**. |
| Nguồn đã mở | Toàn văn Luật 134/2025/QH15 (bản LuatVietnam, đối chiếu thuviennhadat) trong `data/long/mim-luat-ai-2026/research.md`. Ngày thông qua: https://vneconomy.vn/luat-tri-tue-nhan-tao-se-co-hieu-luc-tu-ngay-132026.htm (brief-facts 28/10; phiên này trang trả về rỗng — R mở lại vanban.chinhphu.vn trước khi viết). NĐ 142/2026 (nhãn, 01/5/2026), QĐ 33/2026/QĐ-TTg (rủi ro cao), NĐ 237/2026 (nhãn báo chí, 01/7/2026). |
| Vì sao người xem Việt quan tâm | Người dùng chatbot, người làm nội dung, người bán hàng online đều đã tạo ảnh/chữ bằng AI. Câu hỏi thật: ảnh này có phải gắn nhãn không, chatbot công ty nói sai thì ai chịu. |
| Câu hỏi trung tâm | Với người dùng bình thường, luật đổi **ba việc** nào, và việc nào **chưa** có nghị định xử phạt? |
| Góc MIM | Ba tình huống đời thường, không đọc luật từng điều. **Hook cũ "ai cũng phải ghi nhãn" là sai:** nghĩa vụ nhãn (Điều 11) đặt lên bên triển khai; dùng cá nhân phi thương mại không thuộc "bên triển khai" (Điều 3 khoản 5); Điều 15 khoản 1d vẫn nói người dùng tuân thủ quy định nhãn. Video phải để sự lưng chừng này hiện rõ. **Không nêu mức phạt** (chưa có nghị định riêng đã kiểm). |
| Trùng | Long `mim-ai-chat-privacy` (lên 06/11) đã nhắc Luật BVDLCN 91/2025. Bài này là Luật AI, góc nhãn và trách nhiệm. |
| 2 tiêu đề | (1) Luật AI Việt Nam 2026: 3 Điều Người Dùng Cần Biết · (2) Từ 01/3/2026: Chatbot Công Ty Nói Sai Thì Ai Chịu? |
| Thumbnail | Chữ **AI · LUẬT** (2 từ, một dấu giữa). Một con dấu đỏ trên khung chat, kiểu title card phim chính kịch, không ô biểu mẫu. |
| Short | **S:** luật có hiệu lực 01/3/2026 — một nghĩa vụ người xem nhớ được. **L:** tình huống gắn nhãn ảnh AI, để lại câu "bên triển khai khác người dùng ở chỗ nào?". **S:** cấm giả mạo người thật để lừa (Điều 7) — nối D1. |
| Độ dài | khoảng 11 phút |
| Rủi ro | Diễn giải luật sai là lỗi nặng. Trước đăng: đối chiếu Công báo / vanban.chinhphu.vn. |

### D5 · Chatbot nói sai, công ty chịu — Moffatt v. Air Canada, 14/2/2024 (nhóm 60%)

| Mục | Nội dung |
|---|---|
| Sự kiện mở | Ngày **14/2/2024**, Civil Resolution Tribunal British Columbia ra phán quyết **2024 BCCRT 149**. Jake Moffatt hỏi chatbot trên web Air Canada về vé tang; chatbot nói được mua giá đầy đủ rồi xin hoàn trong 90 ngày. Chính sách thật không cho hoàn sau chuyến bay. Air Canada lập luận chatbot là "pháp nhân riêng". Thành viên hội đồng Christopher C. Rivers bác, buộc hãng bồi thường **C$650,88** thiệt hại + lãi và phí, tổng **C$812,02**. |
| Nguồn đã mở | Tóm tắt Wikipedia (mở 06/11): https://en.wikipedia.org/wiki/Moffatt_v._Air_Canada. Trang CRT https://decisions.civilresolutionbc.ca/crt/crtd/en/item/525448/index.do mở được tiêu đề, thân văn bản phiên này trả về rỗng. CanLII https://canlii.ca/t/k2spq phiên này không lấy được. CBC: https://www.cbc.ca/news/canada/british-columbia/air-canada-chatbot-lawsuit-1.7116416. BBC Travel 23/2/2024. **Trước khi viết: R phải mở được bản CRT/CanLII.** |
| Vì sao người xem Việt quan tâm | Ngân hàng, hãng bay, shop Việt đang gắn chatbot. Luật AI VN Điều 29: bên triển khai bồi thường khi hệ thống rủi ro cao gây hại dù dùng đúng. Cùng họ hàng với Long luật sư ChatGPT bịa (10,3 giờ, AVP 44%): AI nói chắc, hệ quả pháp lý. |
| Câu hỏi trung tâm | Công ty có được đẩy trách nhiệm sang "con bot" khi nó nói sai trên chính website của mình? |
| Góc MIM | Số tiền nhỏ, nguyên tắc lớn. Nối Điều 11 (người dùng phải biết mình đang nói với hệ thống) và Điều 29. Đây là small claims Canada, **không** ràng buộc tòa Việt Nam — nói đúng phạm vi. |
| Trùng | `mim-ai-hallucinate` là án lệ bịa trong đơn kiện. `mim-ai-chat-privacy` là dữ liệu đi đâu. Bài này là **trách nhiệm pháp lý của hãng**. |
| 2 tiêu đề | (1) Chatbot Air Canada Nói Sai: Hãng Vẫn Phải Chịu · (2) Air Canada 2024: Chatbot Không Phải Pháp Nhân Riêng |
| Thumbnail | Chữ **BOT NÓI SAI** (3 từ). Cửa sổ chat trên trang vé máy bay, một dòng bị gạch, con dấu "HÃNG CHỊU" kiểu title card. |
| Short | **S:** hãng nói bot là pháp nhân riêng — hội đồng bác. Trả lời trọn. **L:** chatbot hứa hoàn 90 ngày, chính sách thật cấm — Long kể số tiền và Điều 29 VN. **S:** ba câu nên hỏi chatbot công ty trước khi tin. |
| Độ dài | khoảng 11 phút |
| Rủi ro | Không nói "tòa án" cho CRT (đây là hội đồng small claims). Không nói phán quyết này áp tại Việt Nam. |

### D6 · Vì sao bạn không trả phí bản quyền để dùng Web — CERN 30/4/1993 (nhóm 30%)

| Mục | Nội dung |
|---|---|
| Sự kiện mở | Tháng **3/1989**, Tim Berners-Lee nộp đề xuất *Information Management: A Proposal*. Sếp Mike Sendall viết **"Vague, but exciting"**. Ngày **30/4/1993**, CERN tuyên bố đưa ba thành phần phần mềm Web vào public domain: *"CERN relinquishes all intellectual property rights to this code"*. |
| Nguồn đã mở | https://home.cern/science/computing/the-birth-of-the-web/licensing-web/ (mở 06/11); https://web30.web.cern.ch/web-history.html; https://home.cern/cern-celebrates-20th-anniversary-of-world-wide-web/ — đã kiểm 28/10. |
| Vì sao người xem Việt quan tâm | Mỗi ngày mở Zalo, Google, ngân hàng đều chạy trên Web. Ít người tách Web với Internet, và ít người biết Web suýt là hàng có phí (Gopher bắt đầu thu phí thương mại năm 1993 — theo Berners-Lee và Cailliau, lưu lượng Gopher chững). |
| Câu hỏi trung tâm | Web ra đời thế nào, và vì sao nó thành nền tảng mở thay vì tài sản của một hãng? |
| Góc MIM | Mở từ thanh địa chỉ hôm nay, quay 1989. Lời đọc: "không trả **phí bản quyền**" (người dùng vẫn trả tiền mạng). Không nói "Berners-Lee không đăng ký sáng chế" như quyết định cá nhân — quyền thuộc CERN. |
| Trùng | Chưa có Long. Kho R: `data/long/mim-web-1989-1993/research.md`. |
| 2 tiêu đề | (1) Web Suýt Là Hàng Có Phí: CERN Ký Văn Bản 30/4/1993 · (2) 30/4/1993: CERN Từ Bỏ Quyền, Web Không Thu Phí Bản Quyền |
| Thumbnail | Chữ **MIỄN PHÍ?** (2 từ). Thanh địa chỉ trình duyệt, một con dấu tay lên tờ đề xuất. |
| Short | **S:** Web khác Internet — trả lời trọn 25 s. **L:** 30/4/1993 CERN ký văn bản nào? Long kể Gopher. **S:** ba chữ "Vague, but exciting". |
| Độ dài | khoảng 11 phút |

### D7 · RAM trong máy bạn: Altman, 30/10/2026 (nhóm 30%)

| Mục | Nội dung |
|---|---|
| Sự kiện mở | Trên *Cheeky Pint*, đăng **30/10/2026**, Sam Altman nói nguồn cung RAM hạn chế nằm trong máy tính mọi người và "chỉ được dùng trong **5% thời gian**"; xét phân bổ toàn cầu thì "thật tệ". Ngày **02/11/2026** Elon Musk đăng trên X: mọi người cũng xứng đáng sở hữu RAM (theo spec Short đã hẹn). |
| Nguồn đã mở | https://vnexpress.net/sam-altman-that-te-khi-ram-nam-trong-may-nguoi-dung-5139149.html (31/10, mở 06/11). Cùng bài: Micron 26 thỏa thuận, bao phủ hơn 35% doanh thu dự kiến đến 2030, 32 tỷ USD đặt cọc; Samsung được cho là chốt 75–80% sản lượng 2027. GH-31 `mim_03`. |
| Vì sao người xem Việt quan tâm | Giá RAM, máy tính, điện thoại đang tăng vì trung tâm dữ liệu AI vét DRAM. Người xem cảm thấy trên hóa đơn, không cần biết tên mô hình. |
| Câu hỏi trung tâm | RAM trong máy bạn là "lãng phí" như Altman nói, hay là quyền chạy AI trên máy mình? |
| Góc MIM | Tách phát ngôn (5% là lời Altman, không phải số đo độc lập của kênh), mô hình kinh doanh đám mây, và mặt vật lý: hợp đồng độc quyền DRAM. Musk là phản bác một câu, không biến thành "cuộc chiến tỷ phú". |
| Trùng | Short `mim-sam-altman-ram-5-phan-tram-v2` đã hẹn **09/11 17:00 VN**. Long là bản sâu (hợp đồng Micron/Samsung, suy luận cục bộ, giá máy). Không dựng lại cùng một Short S. |
| 2 tiêu đề | (1) Sam Altman 2026: RAM Trong Máy Bạn Chỉ Dùng 5% Thời Gian · (2) Altman Muốn RAM Lên Mây, Musk: Người Dùng Cũng Đáng Có |
| Thumbnail | Chữ **5% RAM** (2 từ). Thanh RAM trên bàn tối, một trung tâm dữ liệu mờ phía sau, chữ lớn kiểu poster. |
| Short | **L:** 5% là lời Altman trên Cheeky Pint — Long mở hợp đồng DRAM. **S:** một câu Musk 02/11, trả lời trọn (nếu Short 09/11 chưa phủ câu này). **S:** vì sao giá máy tính tăng khi AI vét RAM — một hình cột, không khuyên mua. |
| Độ dài | khoảng 11 phút |
| Rủi ro | 5% là phát ngôn, không đo được từ repo. Micron/Samsung là "theo VnExpress dẫn Tom's Hardware / báo ngành" — R mở nguồn gốc trước khi đọc thành khẳng định. |

### D8 · Máy học đọc mã zip viết tay — LeCun et al. 1989 (nhóm 10%)

| Mục | Nội dung |
|---|---|
| Sự kiện mở | Năm **1989**, bảy tác giả Bell Labs, trong đó có Yann LeCun, đăng *Backpropagation Applied to Handwritten Zip Code Recognition*, Neural Computation 1(4) 541–551, dữ liệu Bưu điện Mỹ. |
| Nguồn đã mở | https://mlanthology.org/neco/1989/lecun1989neco-backpropagation — đã kiểm 28/10. Séc: "several million cheques per day" theo bài 1998. Turing Award công bố 27/3/2019 (ACM, trang gốc 403 lần R 28/10). |
| Vì sao người xem Việt quan tâm | Ứng dụng quét CCCD, biển số, hóa đơn đều là bài toán chữ viết tay. Ít người biết bài toán đầu tiên thắng lớn là **mã bưu chính**. |
| Câu hỏi trung tâm | Máy học đọc một con số viết tay thế nào, và vì sao ý tưởng 1989 phải chờ hơn 20 năm? |
| Góc MIM | Đóng góp 1989 đúng một việc: đưa ràng buộc bài toán vào kiến trúc, học **toàn bộ** mạng bằng lan truyền ngược, bộ lọc học từ ảnh. Nhắc Neocognitron 1980 và Rumelhart–Hinton–Williams 1986. **Không** nói "điện thoại bạn chạy LeNet". Ví dụ hiện tại an toàn: dịch qua camera, giọng Android (theo ACM). AlexNet không phải CNN đầu tiên trên GPU. |
| Trùng | Long `mim-ai-gpu` (AlexNet, đã lên 02/11) là 2012. Bài này là 1989, mã zip. Kho R: `data/long/mim-lecun-1989/research.md`. |
| 2 tiêu đề | (1) 1989: Máy Học Đọc Mã Bưu Chính Viết Tay · (2) 1989: Ý Tưởng Đọc Chữ Viết Tay Phải Chờ Hơn 20 Năm |
| Thumbnail | Chữ **MÁY ĐỌC?** (2 từ). Chữ số 7 viết tay lớn cạnh lưới điểm ảnh. |
| Short | **S:** máy nhìn chữ số viết tay như thế nào — một lưới, trả lời trọn. **L:** vì sao 1989 phải chờ — dữ liệu và sức tính, để lại câu 2012. **S:** séc "vài triệu tấm mỗi ngày" theo bài 1998. |
| Độ dài | khoảng 12 phút |

**Cơ cấu lô:** D1–D5 = 62,5% nhóm 60%. D6–D7 = 25% nhóm 30%. D8 = 12,5% nhóm 10%. Lệch nhẹ so với 60/30/10 vì 8 bài không chia hết 10%.

**Việc tiếp theo khi được duyệt:** R mở các URL còn thiếu (FBI gốc, CRT/CanLII, arXiv, Công báo Luật AI) → W1 kịch bản → W2 cảnh. Render từ giữa tháng 11, hẹn `publishAt` từ 02/12. Không ghi `state.sqlite` trong ticket này.

---

## B. Bao bì 15 Long chưa lên sóng

`state.sqlite` chỉ đọc 06/11/2026: 16 Long MIM có `publish_at` từ 06/11 20:00 VN tới 01/12. `long-mim-ai-chat-privacy` lên **hôm nay** 06/11 20:00 VN nên **không** nằm trong danh sách sửa bao bì (theo brief: `publish_at` sau hôm nay). Còn **15** bài, 08/11–01/12, tất cả `stage=published` (đã upload private + hẹn giờ). Đề xuất dưới đây chờ chủ kênh duyệt từng video; **không** sửa spec, không gọi API, không đổi `publishAt`.

Mục tiêu: CTR từ **Đề xuất** (91% impressions, CTR ~1%). Mỗi bài: 2 tiêu đề mới ≤ 60 ký tự, 1 ý thumbnail (chữ ≤ 4 từ). Lý do gắn với số đo và với `youtube.summary` của chính video.

Chữ thumbnail: kiểu thẻ tiêu đề phim — một cụm ngắn, tương phản cao, font kênh, một hình; không nhãn biểu mẫu, không chữ công cụ, không chồng quá 4 từ.

| # | Lên (20:00 VN) | Slug | Tiêu đề đang hẹn | Hai tiêu đề mới | Ý thumbnail | Lý do |
|---|---|---|---|---|---|---|
| 1 | T7 08/11 | `mim-may-thang-poker` | Libratus 2017: Cỗ Máy Học Tố Bịp, Thắng 4 Cao Thủ Poker (55) | **4 Cao Thủ Poker Thua Máy: 120.000 Ván Năm 2017** (46) · **Máy Học Tố Bịp 2017: 4 Người Thua 120.000 Ván** (45) | Chữ **TỐ BỊP** (2 từ). Bàn nỉ tối, bốn lá úp, một cánh tay máy lật lá. Thumb hiện tại xếp 4 dòng "CỖ MÁY HỌC CÁCH TỐ BỊP". | Tên Libratus người xem Suggested không nhận. Số 120.000 ván và 4 cao thủ có trong summary. |
| 2 | CN 09/11 | `mim-ai-khuon-mat` | Khuôn Mặt Bạn Biến Thành 128 Con Số: AI Nhận Ra Bạn Thế Nào? (60) | **Chuyển 10 Triệu Phải Quét Mặt: Máy Đang Nhìn Gì?** (48) · **128 Con Số Thay Mặt Bạn: Vì Sao Ngân Hàng Bắt Quét?** (51) | Chữ **QUÉT MẶT?** (2 từ). Bóng mặt nghiêng tan thành lưới số, một bên tối. Thumb hiện "KHUÔN MẶT BẠN LÀ 128 CON SỐ" (7 từ). | Mốc 01/07/2024, chuyển trên 10 triệu phải sinh trắc, có trong summary. Đây là nỗi lo đời thường, cùng họ với Long giả giọng. |
| 3 | T3 11/11 | `mim-may-choi-game` | AlphaStar, OpenAI Five: Khi Máy Thắng Cả Game Thời Gian Thực (60) | **Máy Thắng Nhà Vô Địch Dota 2: OpenAI Five Năm 2019** (50) · **StarCraft: Máy Lên Grandmaster, Rồi Thua Ván Thứ 11** (51) | Chữ **MÁY THẮNG** (2 từ). Cúp giải cạnh ghế game thủ trống. Thumb hiện "MÁY TẬP 45.000 NĂM" — **không** thấy số này trong summary (summary: thắng 10, thua ván 11, OG 2019). | Dota 2 / StarCraft là mỏ neo người Việt. AlphaStar/OpenAI Five trên tiêu đề là tên riêng + năm. |
| 4 | T5 13/11 | `mim-dich-may` | Dịch Máy: Lời Hứa “Vài Năm Nữa” Từ Năm 1954 Tới Google Dịch | **1954: Máy Dịch 60 Câu, Báo Hứa Xong Trong Vài Năm** (49) · **Lời Hứa Dịch Máy Vài Năm Nữa Kéo Dài 70 Năm** (43) | Chữ **VÀI NĂM NỮA** (3 từ). Trang báo 7/1/1954 đóng dấu, IBM 701 bóng. Thumb hiện 5+ từ "MÁY DỊCH SẼ XONG TRONG 3–5 NĂM". | Lời hứa có ngày 7/1/1954 và "hơn 60 câu" trong summary. Kéo bằng nghịch lý, không bằng tên IBM 701. |
| 5 | CN 15/11 | `mim-apollo-1202` | Apollo 11, Mã 1202: Máy Tính Báo Động 5 Lần Khi Hạ Cánh (54) | **Apollo 11: 5 Lần Báo Động, Houston Chỉ Có Vài Chục Giây** (55) · **Mã 1202: Máy Tính 80 KB Đưa Người Xuống Mặt Trăng** (49) | Chữ **MÃ 1202** (2 từ). Đèn ALARM, đường chân trời Mặt Trăng. Visual gần thumb hiện tại; rút chữ phụ. | Apollo là mỏ neo. Tiêu đề 2 đưa 80 KB (summary: chưa tới 80 kilobyte) — chỉ dùng nếu lời đọc đã nói. |
| 6 | T2 16/11 | `mim-oppenheimer-feynman` | OPPENHEIMER Ngoài Đời Thật: Feynman Đua Với Máy IBM (51) | **OPPENHEIMER Ngoài Đời Thật: Phòng Thẻ Đục Lỗ Tính Bom** (55) · **Feynman 1945: Phòng Thẻ Đục Lỗ Tính Trước Quả Bom** (49) | Chữ **ĐUA VỚI MÁY** (3 từ). Thẻ đục lỗ bay, người quay lưng tại bàn (không mặt Feynman vẽ). Thumb hiện 5 từ "FEYNMAN ĐUA VỚI MÁY IBM". | Phim Oppenheimer là mỏ neo CL đã thắng. Feynman một mình trên Đề xuất yếu hơn. |
| 7 | T4 18/11 | `mim-google-maps-kal007` | GOOGLE MAPS Ngoài Đời Thật: KAL 007 Và Lời Hứa GPS Của Reagan (60) | **GOOGLE MAPS Ngoài Đời Thật: KAL 007 Và Ngày Reagan Mở GPS** (57) · **Chấm Xanh Của Bạn: Từ Lệch 600 Km Năm 1983 Tới 5 Mét** (52) | Chữ **CHẤM XANH** (2 từ). Elip sai 600 km đối lập chấm 5 m. Thumb hiện "CHẤM XANH CỦA BẠN CÓ GIÁ" (5 từ). | Google Maps là mỏ neo. Tiêu đề 2 đưa hệ quả người xem đang dùng. 600 km → 5 m có trên thumb/titles hiện tại. |
| 8 | T6 20/11 | `mim-ke-huy-diet-petrov` | KẺ HỦY DIỆT Ngoài Đời Thật: Petrov, Người Không Tin Máy Tính (58) | **KẺ HỦY DIỆT Ngoài Đời Thật: Đêm Máy Báo Mỹ Phóng 5 Tên Lửa** (58) · **26/9/1983: Petrov Không Tin Máy Báo Năm Tên Lửa** (52) | Chữ **CHƯA** (1 từ). Hai nút BÁO LÊN \| CHƯA, ngón tay dừng trên CHƯA. Visual đã điện ảnh; rút chữ lớn về một từ. | Phim Kẻ Hủy Diệt + 5 tên lửa là mỏ neo. Tên Petrov trên Đề xuất yếu. |
| 9 | CN 22/11 | `mim-siri-susan-bennett` | SIRI Ngoài Đời Thật: Susan Bennett, Người Nói Mình Là Giọng Siri (**61**, vượt 60) | **SIRI Ngoài Đời Thật: Giọng Thu 2005, Sáu Năm Sau Mới Vang** (57) · **Susan Bennett 2011: Nghe Giọng Mình Trong iPhone Lần Đầu** (56) | Chữ **GIỌNG 2005** (2 từ). Cối băng 2005 cạnh bóng iPhone, không mặt. Thumb hiện "GIỌNG SIRI THU TỪ 2005" (5 từ). | Tiêu đề đang hẹn vượt 60 ký tự. Siri là mỏ neo; 2005→2011 là nghịch lý có trong titles. |
| 10 | T2 23/11 | `mim-turing-bombe` | NGƯỜI GIẢI MÃ Ngoài Đời Thật: Alan Turing Và Bombe (50) | **NGƯỜI GIẢI MÃ Ngoài Đời Thật: Thư Turing 1941 Tới Churchill** (59) · **Turing 1941: Máy Bombe Loại Dần Đường Sai, Người Kiểm Tra** (57) | Chữ **LÁ THƯ 1941** (3 từ). Phong bì gửi Churchill, trống Bombe phía sau. Thumb hiện "GIẢI MÃ ENIGMA" — generic. | Summary mở bằng lá thư 21/10/1941. Đó là tình huống, mạnh hơn tên máy Bombe. |
| 11 | T4 25/11 | `mim-katherine-johnson` | HIDDEN FIGURES Ngoài Đời Thật: Katherine Johnson (49) | **HIDDEN FIGURES Ngoài Đời Thật: Glenn Đòi Tính Lại Bằng Tay** (58) · **Katherine Johnson 1962: Máy IBM Xong, Glenn Vẫn Đòi Tay** (55) | Chữ **TÍNH LẠI** (2 từ). Bút chì trên bản in IBM, ngày 20.02.1962. Thumb hiện 5 từ "KIỂM LẠI MÁY IBM BẰNG TAY". | Phim Hidden Figures là mỏ neo. Glenn đòi tính tay là bước ngoặt trong summary. |
| 12 | T6 27/11 | `mim-moneyball` | MONEYBALL Ngoài Đời Thật: Billy Beane Và Con Số (47) | **MONEYBALL Ngoài Đời Thật: 20 Trận Thắng, Đội Nghèo 40 Triệu** (59) · **Billy Beane 2002: Một Con Số Không Đủ Để Thắng Playoff** (54) | Chữ **20 TRẬN** (2 từ). Bảng điểm 20, khán đài rẻ tiền. Thumb hiện 5 từ "ĐỘI NGHÈO 20 TRẬN THẮNG LIỀN". | 20 trận và 40 triệu USD đã trên thumb. Tiêu đề mới đưa số lên trước tên Beane. |
| 13 | CN 29/11 | `mim-social-network` | MẠNG XÃ HỘI Ngoài Đời Thật: Mark Zuckerberg (43) | **MẠNG XÃ HỘI Ngoài Đời Thật: Facemash 2003, Hai Ảnh Một Phiếu** (60) · **Zuckerberg 2004: Từ Facemash Tới Thefacebook Trong 3 Tháng** (58) | Chữ **CHỌN 1** (2 từ). Hai bóng ảnh thẻ sinh viên, một được chọn. Thumb hiện "CHỌN 1 TRONG 2" (4 từ) — đã đúng trần; rút còn 2 từ cho đọc nhanh trên Đề xuất. | Facemash là tình huống người xem nhận ngay. Tên Zuckerberg một mình trên Đề xuất yếu hơn phim. |
| 14 | T2 30/11 | `mim-macintosh-1984` | STEVE JOBS 1984: Macintosh biết nói bằng hình (45, lệch hoa/thường) | **Steve Jobs 1984: Macintosh Bỏ Dòng Lệnh, Nói Bằng Hình** (54) · **Macintosh 24/1/1984: Cú Nhấp Đưa Hình Ảnh Lên Màn Hình** (54) | Chữ **BỎ DÒNG LỆNH** (3 từ). Giữ visual hiện tại (24.01.1984). Đã điện ảnh. | Ngày Super Bowl/ra mắt có trong summary. Tiêu đề mới thống nhất hoa, có người + năm + bước ngoặt. |
| 15 | T3 01/12 | `mim-jobs-1985` | Steve Jobs 1985: Bị Gạt Khỏi Apple, Thành Đường Quay Lại (54) | **Steve Jobs 1985: Mất Quyền Điều Hành, 12 Năm Sau Quay Lại** (57) · **Apple 1996: Trả 427 Triệu Đô Mua NeXT Để Đưa Jobs Về** (52) | Chữ **BỊ GẠT** (2 từ). Quả táo cắt đôi. **Chưa có** `motion/long/thumbs/mim-jobs-1985_t1.html`. | Lời đọc tách "mất quyền" với "từ chức" (R 28/10). 427 triệu là tổng giá 10-K, không phải 400 triệu lúc công bố. Không dùng chữ "bị đuổi". |

**Cách đo sau khi chủ kênh duyệt một tiêu đề (không làm trong ticket này):** một biến mỗi video, giữ thumbnail khi đổi tiêu đề. Đọc CTR Đề xuất khi đủ 1.000 impressions mới; chốt ở 7 ngày hoặc 3.000 impressions. Dừng: CTR cùng nguồn không cao hơn ~1,0% thì trả tiêu đề cũ. Tách Browse và Suggested (#177, mục Đo).

**Ưu tiên soi trước giờ lên, nếu chỉ được duyệt vài bài:** Siri (tiêu đề đang 61 ký tự), poker (tên Libratus), khuôn mặt (mốc 10 triệu), game (Dota/StarCraft thay AlphaStar), Jobs (thiếu file thumb).

---

## C. Việc ticket này không làm

- Không sửa `spec.json`, HTML thumbnail, kịch bản.
- Không upload, không đổi `publishAt`, không ghi `state.sqlite`.
- Không commit.
- Không đọc credentials.

Pilot hook MIM 13–18/11 vẫn là loại S. Short L của lô tháng 12 dựng sau khi có kết quả 7 ngày của pilot, theo `docs/codex/long-rules.md`.
