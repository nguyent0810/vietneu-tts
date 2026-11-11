# GH-262 — Review "Văn phong storytelling v3"

Người review: agent review văn phong (Sonnet), 10/11/2026. Chỉ đọc repo và viết tài liệu. Không sửa guide v2, không sửa lời Short, không render, không đăng, không comment lên GitHub.

Kèm theo: `creator_v2/docs/pm/storytelling-guide.v3-draft.md` (bản nháp guide v3, chờ PO duyệt).

---

## 0a. Chỉ đạo bổ sung của PO (10/11) và cách tài liệu này đã điều chỉnh

PO nhắc: luật kiểm nguồn phải **linh hoạt**, nghiêng về cho phép sáng tạo ở vùng 2 và 3, **không thêm luật cứng mới**, lằn ranh đỏ giữ đúng 3 điều của issue (BUD thêm: không gán cho Đức Phật lời hay việc không có trong kinh), và guide phải được **nối vào chỗ agent đọc/chạy thật**. Bản đầu của tôi nặng tay hơn mức đó. Đã sửa như sau (guide nháp và các mục dưới đã cập nhật; mục 2, 3 và 5 giữ nguyên vì là phân tích):

| Trong bản đầu | Sau chỉ đạo PO |
|---|---|
| Mở rộng lằn ranh đỏ 2 thành "cấm mọi nội tâm" | **Trả về đúng chữ của issue** (gán tội/tính cách xấu khi không có căn cứ). Tầng A/B/C hạ thành **khuyến nghị** |
| Bốn phép thử "bắt buộc qua cả bốn" | Ba câu **tự hỏi** + mẹo xoá câu; không là cổng |
| Ba điều cấm vùng 3, danh sách từ cấm, giới hạn đếm | "Cái bẫy nên tránh" và cảnh báo; bỏ giới hạn đếm cứng |
| Lint chặn (zones bắt buộc, chặn tầng B/C) | **Chỉ cảnh báo**, `zones` tuỳ chọn, không chặn spec cũ |
| Không có chỗ nối | Mục 4b dưới đây và mục 12 trong guide |

Nhận xét về phân tích ở mục 1–3 vẫn đúng như điểm yếu, nhưng **cách vá** giờ là gợi ý và cảnh báo, không phải luật. Riêng các cổng preflight đã có sẵn (hook ≤ 9 từ, 55–135 từ, 25–40 giây, viết tắt) là cổng cũ, không do v3 thêm.

## 0. Kết luận một dòng

**DUYỆT CÓ SỬA** (nhẹ tay, nghiêng về sáng tạo theo chỉ đạo PO 10/11). Hướng đi đúng: luật "mọi chi tiết đều phải có nguồn" làm văn robot, và tách "sự thật" khỏi "cách kể" là đúng bản chất. Nhưng bản đề xuất trong issue còn ba lỗ có thể làm agent trượt sang bịa, ví dụ mẫu của chính issue đã dính hai lỗ, và tiêu chí đo 72 giờ không đo được thứ nó muốn đo. Danh sách chỉnh ở mục 7.

## 0b. Giới hạn của lần review này (đọc trước)

Bốn đầu vào mà brief nêu **không có trong checkout nào của máy này**. Tôi đã tìm trong cây làm việc, mọi nhánh local và remote (sau `git fetch --all`), các worktree, `git stash`, và các thư mục tạm của phiên:

| Đầu vào | Kết quả tìm |
|---|---|
| `creator_v2/docs/pm/storytelling-guide.md` (v2) | không có |
| `creator_v2/docs/pm/tickets/GH-248-storytelling-review-report.md` (phản biện Codex) | không có (chỉ có `GH-248-v1-port-code-report.md`, chuyện khác) |
| `creator_v2/docs/pm/2026-11-10-cl-diagnosis.md` | không có |
| Lời 9 Short series (`cl-bao-s2-loi-cam`, ...) | không có spec nào tên `cl-bao-s2-*`; chỉ có 5 spec `cl-bao-*` cũ và 24 spec `cl-*` khác |

Hệ quả, để PO biết chỗ nào tin được đến đâu:

1. **Tôi chỉ biết v2 qua mô tả trong issue #262** ("bắt mọi chi tiết đều phải có nguồn"). Mọi nhận xét về v2 và về lập luận của Codex là suy từ đó: *chưa kiểm chứng*. Nếu Lead có file này ở máy khác, nên đối chiếu mục 3 và guide nháp với v2 thật.
2. **Chẩn đoán "kẹt khoảng 1.000 views" tôi không đọc được.** Tôi thay bằng `creator_v2/docs/pm/2026-11-06-cl-analytics.md` (có trong repo) và dùng số của nó ở mục 1, câu 5.
3. **Ví dụ Short:** vì không có spec 9 bài, tôi lấy làm kho đối chiếu các lời đọc CL đã có thật trong repo: `docs/pm/tickets/GH-228-cl-shorts1-lines.md`, `GH-228-cl-shorts2-lines.md` và `data/stier/specs/cl-*.json` (Bao Chửng, Hòa Thân, và các vụ án FBI). Riêng `cl-bao-s2-loi-cam` tôi chỉ có đúng đoạn "Hiện tại" và các dữ kiện nằm trong issue (Tống sử quyển 316, lời dặn không được chôn vào mộ tổ). Tôi **không thêm** dữ kiện nào ngoài đó. Hai bài mẫu còn lại (`cl-bao-nghien-muc`, `cl-hoa-than-hai-muoi-toi`) lấy từ spec có thật; chúng không nằm trong 9 bài của issue nhưng cùng loại (Bao Chửng, Hòa Thân châu Á). Khi có 9 spec thật, nên chạy lại phần mẫu.
4. Tôi **không chạy** `build.py --preflight` trên bản mới vì spec chưa tồn tại. Tôi tự đo bằng tay đúng các ngưỡng của `motion/stier/build.py`: số từ 55–135, thời lượng ước lượng 25–40 giây ở 3,3 từ/giây, lời mở tối đa 9 từ (`HOOK_MAX_WORDS`), lời mở phải có số hoặc từ khoá tiêu đề. Số đo nằm ở mục 5.
5. Tôi không mở lại URL nguồn (Wikisource, FBI...) trong phiên này. Các dữ kiện lịch sử trong tài liệu này là dữ kiện **đã có sẵn trong repo**, tôi không bổ sung gì. Chỗ nào tôi nêu điều ngoài repo (luật, chính sách YouTube, tục lệ thời Tống) đều ghi "chưa kiểm chứng".

---

## 1. Trả lời năm câu hỏi của issue

### Câu 1. Ranh giới vùng 2 đã đủ rõ chưa? Cần ví dụ "được / không được" nào?

**Chưa đủ.** Định nghĩa trong issue ("không khí, thời tiết, cảnh vật đúng với thời đó và nơi đó; cảm giác hợp lẽ thường") dựa vào hai phán đoán mà agent không tự kiểm được:

- "đúng với thời đó, nơi đó": agent trả lời bằng trí nhớ của chính nó, tức là bằng thứ dễ bịa nhất;
- "không trái nguồn và không tạo sự kiện mới": ranh giới giữa *không khí* và *sự kiện* rất mờ. "Đêm ấy trời mưa" là không khí hay là sự kiện? Nếu vụ án xảy ra ban ngày thì sao?

Tôi đề xuất thay phán đoán bằng **bốn phép thử cơ học** (đã đưa vào guide nháp, mục 3):

1. **Phép thử xoá.** Xoá câu vùng 2 đi. Nếu một dữ kiện kiểm chứng được biến mất, câu đó là vùng 1 trá hình. Nếu chỉ mất giọng điệu, nó là vùng 2/3.
2. **Phép thử "danh từ mới".** Vùng 2 và 3 không được chứa số, ngày, tên riêng, hay danh từ chỉ người/vật mới mà bộ dữ kiện (vùng 1) chưa có. Người "lính gác lăng" nằm ngoài bộ dữ kiện thì không được xuất hiện như một nhân vật. Đây là phép thử mạnh nhất vì **máy kiểm được** (mục 4).
3. **Phép thử "chủ ngữ".** Vùng 2 có chủ ngữ là *loại* ("một gia đình thời ấy", "người thợ", "bạn", "người cầm quyền"), không phải *tên riêng + hành động mới*. "Một gia đình thời Tống coi mộ tổ là..." được. "Bao Chửng thở dài rồi đặt bút" không được (tên riêng + hành động).
4. **Phép thử "một lần, một nơi".** Không khí chỉ ở dạng *khái quát* (mùa, nơi, nếp sống), không bao giờ ở dạng *một lần cụ thể* ("hôm ấy", "đêm đó", "sáng hôm sau") khi nguồn không nói. "Đêm ấy" biến cảnh vật thành sự kiện.

Thêm hai điểm mà issue chưa nói:

- **Ngôn ngữ phỏng đoán không phải bùa hộ mệnh.** "Chắc hẳn đêm đó ông đã khóc" vẫn là bịa một sự kiện (khóc), chỉ mặc áo hedge. Phỏng đoán chỉ được áp lên **trạng thái cảm giác chung chung** ("có lẽ ông thấy nặng lòng"), không áp lên **hành vi, lời nói, sự kiện** (khóc, hét, đập bàn, thì thầm, nghiến răng).
- **Vùng 2 cần hai tầng.** Tôi tách 2a (bối cảnh chung của thời đó, có thể kiểm bằng nguồn thứ hai) và 2b (cảm giác phỏng đoán của nhân vật). Hai loại có rủi ro rất khác nhau (câu 2).

**Cặp ví dụ "được / không được"**: xem mục 2 (13 cặp lấy từ Short CL thật).

**Ví dụ mẫu của chính issue** dính lỗi, xem mục 3 (lỗ hổng L1, L2, L5).

### Câu 2. Nội tâm nhân vật thật: ngôn ngữ phỏng đoán có đủ không? Rủi ro pháp lý, đạo đức với người còn thân nhân?

**Không đủ nếu để một mình.** Ngôn ngữ phỏng đoán giải quyết vấn đề *trung thực với người nghe* (người nghe biết đây là suy đoán). Nó **không** giải quyết vấn đề *phẩm giá của người được nhắc đến* và *tác động lên người còn sống*. Tôi đề xuất phân ba tầng theo "khoảng cách tới người còn sống":

| Tầng | Ai | Nội tâm / cảm xúc |
|---|---|---|
| A | Nhân vật công đã mất từ rất lâu (Bao Chửng, Gia Khánh, Hòa Thân, Càn Long) | Được, dạng 2b, phải hedge rõ, chỉ ở mức cảm giác chung, không gán hành vi |
| B | Người thật đã mất nhưng còn thân nhân hoặc ký ức trực tiếp (khoảng thế kỷ 20 trở lại): nạn nhân vụ án, nhân chứng, người bị buộc tội | **Không viết nội tâm.** Chỉ vùng 1 và vùng 3 hướng vào người nghe ("bạn nghĩ gì") và vào sự việc, không vào người đó |
| C | Người còn sống, thân nhân còn sống, nghi phạm chưa bị kết án | Không nội tâm, không gán động cơ, không gán tính cách, không đoán |

Ngưỡng "rất lâu" là quyết định của PO; tôi đề xuất mốc thực dụng là *không còn ai có thể là thân nhân trực hệ còn sống*, khoảng một thế kỷ. Chưa kiểm chứng đây có phải mốc phù hợp, nên để PO chốt.

Dẫn chứng từ repo, các Short CL có người thật thuộc tầng B/C:

- `cl-black-dahlia-56-phut`: Elizabeth Short là nạn nhân; không có dòng nào trong lời đọc viết cảm giác của cô. Lời đọc hiện tại chỉ nói "dấu tay của cô đã có trong kho vì từng xin việc". Đó là mẫu đúng. Guide v3 không được làm điều này tệ đi bằng "cô gái trẻ mơ làm minh tinh, sợ hãi bước vào đêm ấy".
- `cl-diane-jackson-van-tay`: lời đọc có "anh trai cô đề nghị cảnh sát xem lại chứng cứ" (nguồn FBI). Đây là người thật có thể còn sống. Viết "người anh nghẹn ngào, suốt bao năm không ngủ" là bịa cảm xúc cho một người có thật, có tên trong hồ sơ.
- `cl-james-ricks-ban-tu`: có "bạn cùng phòng giam" thú nhận. Động cơ của người này (hối hận? muốn giảm án?) không có trong nguồn. Không được gán.
- `cl-alger-hiss-khai-man`: Hiss bị kết tội khai man, **không** bị kết tội gián điệp (theo đúng lời đọc hiện tại). Mọi câu "chắc chắn hắn là gián điệp" hoặc "hắn vô tội" đều vượt nguồn, và là đúng loại gán tội mà lằn ranh đỏ số 2 cấm.

**Rủi ro pháp lý.** Tôi không phải luật sư và *không kiểm chứng điều luật trong phiên này*. Ghi nhận ở mức cảnh báo:

- Kênh phát bằng tiếng Việt cho người xem Việt Nam. Bộ luật Dân sự 2015 có quy định bảo vệ danh dự, nhân phẩm, uy tín; Bộ luật Hình sự có tội vu khống và làm nhục. Số điều cụ thể: *chưa kiểm chứng*. Nhưng nguyên lý đủ rõ: gán sự thật xấu về người thật khi không có căn cứ thì bên bị nhắc có thể kiện, và "chỉ là phỏng đoán" thường không phải lý do miễn.
- Với đối tượng ở nước ngoài (nhiều Short CL là vụ án Mỹ), pháp luật nước họ có thể áp dụng khác. *Chưa kiểm chứng.* Rủi ro cụ thể nhất là thân nhân còn sống của nạn nhân.
- Nền tảng: YouTube có chính sách riêng về quấy rối và nội dung về nạn nhân sự kiện bạo lực. Nội dung chi tiết: *chưa kiểm chứng*. Khuyến nghị an toàn là không tái hiện chi tiết đau đớn của nạn nhân.

**Rủi ro đạo đức khác mà issue chưa nêu:**

- Kỹ thuật "cái giá với một con người: ai mất gì" rất dễ trượt sang **khai thác nỗi đau nạn nhân để câu cảm xúc**. Với tầng B, "ai mất gì" chỉ được nói bằng *dữ kiện của nguồn* ("một người anh đề nghị xem lại chứng cứ"), không bằng cảnh khóc do mình dựng.
- Lằn ranh đỏ số 2 của issue chỉ cấm "gán **tội hay tính cách xấu**". Nội tâm *tốt* hay *trung tính* gán bừa cũng là bịa. Bản đầu tôi đề xuất mở rộng lằn ranh đỏ; theo chỉ đạo PO 10/11 **đã rút lại**: lằn ranh đỏ 2 giữ nguyên chữ của issue, còn việc tránh gán nội tâm cho nạn nhân/thân nhân chỉ là khuyến nghị (guide nháp mục 4).

### Câu 3. Kỹ thuật đồng cảm nào hợp TTS tiếng Việt, kỹ thuật nào dễ sến hoặc giả?

Điều kiện nền: giọng VieNeu đọc gần như **phẳng về cảm xúc**; nhịp và quãng nghỉ gần như chỉ đến từ dấu câu và độ dài câu. Hai hệ quả: (a) cảm xúc phải nằm trong **cấu trúc và chọn chữ**, không trông chờ vào giọng; (b) từ gọi tên cảm xúc ("xót xa", "đau đớn", "nghẹn ngào") đọc bằng giọng phẳng nghe giả. (Giọng đọc có chiều lên ở câu hỏi hay không, tôi *chưa kiểm chứng*; cần nghe thử trước khi dựa vào.) Repo đã có tiền lệ cho điều này ở kênh BUD: `motion/stier/script_lint.py` có danh sách `CLICHE` (sáo ngữ cấm) và `LECTURE` (giọng giảng), và luật "nhịp: câu ngắn, mệnh đề ≤ 14 từ". Guide CL nên mượn đúng tinh thần đó.

| # | Kỹ thuật | Hợp TTS? | Cách làm | Dễ hỏng ở đâu |
|---|---|---|---|---|
| 3 | **Cái giá với một con người** | Hợp nhất | Danh từ cụ thể, không tính từ cảm xúc: "thợ đá làm thêm hàng chục chiếc", "dòng họ nằm lại bên nhau" | Trượt thành khai thác nạn nhân (tầng B/C); chỉ dùng dữ kiện của nguồn |
| 5 | **Nhịp và khoảng lặng** | Hợp, nhưng chỉ qua dấu câu | Câu dài rồi câu ngắn. "Bị gạch tên khỏi dòng họ. Cả khi đã chết." | Không dùng "...", ngoặc, gạch ngang (`script_lint` R7, `AGENTS.md` cấm ký hiệu lạ). Đừng cắt vụn mọi câu: nhịp đều cũng thành robot |
| 4 | **Đối lập nhỏ/lớn** | Hợp | "Một chiếc nghiên. Một cánh cửa quà cáp." Dùng sự việc đã có ở vùng 1 | Phóng đại ("làm rung chuyển cả triều đình") là bịa hệ quả |
| 6 | **Kết bằng ý nghĩa / câu hỏi** | Hợp | Một câu hỏi cụ thể gắn với hook ("điều gì đủ nặng để giữ một người khỏi tham ô?") | Câu hỏi chung chung ("bạn nghĩ sao?") vô hồn; đạo lý khép bài ("tham lam rốt cuộc chỉ hại mình") thành giảng đạo |
| 2 | **Đặt người nghe vào cảnh** | Hợp vừa | "Thử hình dung bạn là người thợ đá" | Tối đa **một lần mỗi Short**; lặp thành tic. Đừng giả định người nghe có mặt trong sự kiện có người thật gặp nạn. Đừng giả định nhân vật không có trong nguồn (xem L3) |
| 1 | **Kéo về đời thường** | Dễ sến nhất | Chỉ khi phép so hiển nhiên, một câu | "Giống như bạn nhận lương rồi bị sếp..." nghe gượng; lệch thời đại; làm nhẹ vụ án nặng |

Hai lỗi chung đáng cấm vì máy kiểm được:

- **Tic lặp giữa các Short.** Nếu 9 Short đều có "Thử nghĩ xem" và "Nếu bạn là...", cả lô nghe như một khuôn, đúng thứ CLAUDE.md gọi là "nội dung sản xuất hàng loạt theo khuôn" mà YouTube coi là spam. Cần luật xoay vòng cụm mở (mục 4).
- **Từ gọi tên cảm xúc.** Cấm danh sách tính từ cảm xúc dựng sẵn; ngoài đó, để chi tiết gây cảm xúc.

### Câu 4. Mức cảm xúc khác nhau cho CL / MIM / CK

Nguyên tắc: **cùng ba vùng và ba lằn ranh đỏ cho cả ba kênh; chỉ khác "loại cảm xúc" và "nhiệt độ".** (BUD, FS, Văn Sử Địa không thuộc phạm vi issue này; BUD giữ luật chặt, xem mục 3 lỗ hổng L9.)

| Kênh | Loại cảm xúc nên nhắm | Nhiệt độ | Kỹ thuật chính | Cấm riêng |
|---|---|---|---|---|
| **CL** (hồ sơ vụ án, nhân vật lịch sử) | Lạnh, nặng, day dứt; "cái giá" và "chi tiết nhỏ dẫn tới kết cục lớn" | Trầm. Ít, đắt. Tối đa 1–2 câu 2b mỗi Short | 3, 4, 5, 6 | Nội tâm nạn nhân (tầng B/C); chi tiết bạo lực; kết đạo lý; gán tính cách xấu cho người chưa có bản án |
| **MIM** (AI, công nghệ) | Tò mò, ngạc nhiên, "chuyện này chạm vào đời bạn" | Sáng hơn, nhịp nhanh, tự nhiên có chút dí dỏm | 1, 2, 4 | Phóng đại tác động công nghệ như sự thật ("AI sẽ thay thế bạn"); tính cách bịa cho nhà khoa học (dùng `voice2` cho trích dẫn thật) |
| **CK** (tài chính cá nhân) | Đồng cảm với nỗi lo hoặc niềm mong của người nghe; "ai mất gì" trong tình huống giả định | Ấm, thực tế, không dọa | 1, 3, 6 | **Hứa lợi nhuận; bán nỗi sợ/FOMO; "nên mua/bán"** (`AGENTS.md`). Nhân vật và số giả định phải có nhãn VÍ DỤ GIẢ ĐỊNH đọc được ở 360 px |

Lưu ý CK: nhân vật giả định có tự do cảm xúc hơn (đã được gắn nhãn là giả), nhưng **chính vì vậy** mới dễ trượt thành "lời chứng thực giả" ("chị Lan đã tiết kiệm được 500 triệu nhờ cách này"). Quy tắc: nhân vật giả định không bao giờ có kết quả đẹp như bằng chứng cho một khuyến nghị; nhãn VÍ DỤ GIẢ ĐỊNH đứng trước, trên hình, không chỉ trong lời đọc.

### Câu 5. Cách đo 72 giờ có tách được hiệu ứng văn phong không?

**Không.** Có ít nhất sáu biến lẫn vào và một lỗi trong tiêu chí.

**Biến gây nhiễu.**

1. **Khung đầu / thumbnail và chủ đề.** Lô mới là series Bao Chửng và vụ án châu Á, lô cũ là vụ án FBI và nhiều thứ khác. Khác chủ đề đã đủ làm lệch views.
2. **Series và tên kênh.** Một series mới có thể được thuật toán đối xử khác (hoặc cùng người xem bấm sang bài kế).
3. **Giờ đăng và thứ trong tuần.** Lịch "25–30/11, 2 bài/ngày" so với lô cũ ở tuần khác. `docs/pm/2026-11-06-cl-analytics.md` cho thấy giờ và thứ ảnh hưởng.
4. **Mốc so sánh lịch sử.** "So với lô cũ" dùng đối chứng *không đồng thời*. Xu hướng kênh, mùa, thay đổi thuật toán đều lẫn vào.
5. **Cỡ mẫu.** 9 Short, mỗi Short views phân bố lệch rất nặng (Short CL từ vài chục tới vài chục nghìn). Trung vị 9 điểm không đủ sức phân biệt +20%.
6. **72 giờ quá sớm** với Short: phần lớn phân phối của Short có thể còn tiếp tục, nên view 72 giờ không phải trạng thái cuối. *Chưa kiểm chứng* cho riêng kênh CL; đề xuất lấy mốc 7 ngày làm quyết định, 72 giờ chỉ đọc sớm.

**Lỗi trong tiêu chí đạt.** Tiêu chí hiện là "trung vị views > 1.000 **hoặc** ≥ 1 sub/1.000 views". Theo `2026-11-06-cl-analytics.md`, 28 ngày gần nhất của kênh: Short có 84.342 views và +93 sub, tức **khoảng 1,1 sub / 1.000 views**; kênh nói chung 92.731 views, +111 sub (≈1,2). *Nền hiện tại đã đạt vế "hoặc" thứ hai.* Nghĩa là gần như mọi kết quả đều "đạt", và tiêu chí không phân biệt được v3 với không-v3. Bỏ vế đó.

Thêm một điều đáng ghi: cùng báo cáo ghi 531 Short công khai và 310.843 views Short trong 365 ngày, tức khoảng 585 views mỗi Short tính trung bình. Tôi không có chẩn đoán gốc để hiểu "trung vị khoảng 1.000" tính trên tập nào; PO/Lead nên chốt rõ **trung vị của tập nào, đo ở mốc nào** trước khi đo.

**Thiết kế đo tốt hơn (đề xuất).**

*Nguyên tắc:* một biến mỗi lần, đối chứng đồng thời, metric giữ chân thay vì views.

1. **Đối chứng đồng thời, ghép cặp.** Trong cùng khung giờ và cùng tuần, đăng xen kẽ bài v2 (giữ lời cũ đã duyệt) và v3. Với 9 bài series, đề xuất 6 bài v3 + 3 bài giữ lời v2 cùng series; hoặc, nếu muốn đo mạnh hơn, mở rộng lô tới ≥ 12 bài mỗi nhánh. Gán nhánh bằng bốc thăm, không do Lead chọn.
2. **Cố định mọi thứ ngoài lời đọc.** Cùng kiểu thumbnail/khung đầu (cùng mẫu bố cục, ảnh tương đương), cùng giọng, cùng nhạc/`variety`, cùng độ dài ±3 giây, cùng khuôn tiêu đề, cùng khung giờ (xen kẽ trong ngày), cùng loại chủ đề trong mỗi cặp (Bao với Bao, châu Á với châu Á).
3. **Đừng nhân đôi cùng một vụ án thành hai video v2/v3** (trùng nội dung có thể bị coi là lặp, và người xem thấy lặp). Ghép cặp theo *loại*, không theo *cùng vụ*.
4. **Metric chính là giữ chân, không phải views:** tỷ lệ xem tiếp so với vuốt qua và AVP từ Studio (có quy trình `webauto studio collect`, xem bộ nhớ dự án về CSV Studio), kèm số lần hiển thị. Views chỉ là phụ. Sub/1.000 views là phụ, chỉ đọc khi đủ mẫu.
5. **Đăng ký trước** (ghi vào issue trước khi đăng): metric chính, mốc đo (72 giờ đọc sớm, 7 ngày quyết định), ngưỡng hiệu ứng tối thiểu có ý nghĩa, và việc *cái gì sẽ làm ta dừng*. Nêu rõ với cỡ mẫu này chỉ phát hiện được chênh lệch lớn (khoảng +25% giữ chân trở lên, *ước lượng, chưa kiểm chứng*); chênh nhỏ thì kết luận là "không phân biệt được", không phải "v3 thắng".
6. **Ghi biến gây nhiễu từng video**: thứ, giờ, tầng sự kiện thời sự, số ngày kể từ bài kế trước, trạng thái thumbnail. So theo hiệu từng cặp, không so hai trung vị rời.
7. **Tách đo "văn phong" khỏi đo "bao bì".** Nếu muốn đo bao bì (thumbnail, tiêu đề), dùng cơ chế Test & Compare của YouTube nếu kênh có (*chưa kiểm chứng* kênh CL được bật hay chưa) và làm ở lô khác. Đừng đổi cả bao bì và lời cùng lúc.

---

## 2. Bảng "ĐƯỢC / KHÔNG ĐƯỢC" cho vùng 2 (13 cặp từ Short CL thật)

Cột "Gốc" là dòng hiện có trong repo. Mọi câu "ĐƯỢC" tôi viết lại đều không thêm số, ngày, tên mới.

| # | Short (gốc) | ĐƯỢC (vùng 2/3, qua 4 phép thử) | KHÔNG ĐƯỢC (và vì sao) |
|---|---|---|---|
| 1 | `cl-bao-s2-loi-cam` (Tống sử q.316) | "Với một gia đình thời xưa, mộ tổ không chỉ là một nấm đất. Đó là nơi cả dòng họ nằm lại bên nhau." (2a, khái quát, chủ ngữ là loại) | "Ông viết lời dặn ấy trên giường bệnh, nước mắt rơi xuống trang giấy." (cảnh + hành vi bịa; nguồn chỉ có lời dặn) |
| 2 | `cl-bao-nghien-muc` | "Thử hình dung bạn là người thợ đá ở đó. Bạn đẽo thêm hàng chục chiếc để làm quà." (suy trực tiếp từ dòng "thu gấp hàng chục lần", vùng 2a, gọi là "bạn") | "Người thợ già nhìn Bao Chửng, mắt rưng rưng biết ơn." (nhân vật mới + cảm xúc + hành vi) |
| 3 | `cl-bao-cong-phu` | "Một cánh cổng nghe nhỏ, nhưng nó đổi cách lời dân tới tai người xét việc." (3, nhắc lại dữ kiện, ẩn dụ) | "Hôm khai cổng, cả Khai Phong đổ về, tiếng reo vang khắp phố." (sự kiện + quy mô bịa) |
| 4 | `cl-bao-luoi-bo` | "Một vụ nhỏ, không tên, không năm: chính vì thế nghe như chuyện ai cũng có thể gặp." (3, dựa trên dữ kiện "sử không ghi tên nạn nhân hay năm") | "Người chủ bò ôm con bò câm khóc suốt đêm." (sự kiện + cảm xúc + chi tiết bịa) |
| 5 | `cl-hoa-than-hai-muoi-toi` | "Có lẽ trong mắt người cầm quyền, đứng quá gần ngôi báu đáng sợ hơn giữ nhiều bạc." (2b hedge, chủ ngữ loại, không hành vi) | "Gia Khánh nghiến răng ký tên, mắt đỏ ngầu căm hận Hòa Thân từ lâu." (hành vi + nội tâm khẳng định + động cơ bịa) |
| 6 | `cl-hoa-than-doi-ten-phu` | "Bạn đi qua cái tên Cung Vương Phủ, có nghĩ tới người ở trước không?" (3) | "Khánh Thân vương sống năm mươi mốt năm trong nỗi ám ảnh bóng ma Hòa Thân." (dữ kiện mới + nội tâm + gán số năm cho một người, mà dòng gốc chỉ nói khoảng cách thời gian) |
| 7 | `cl-hoa-than-thi-ve` | "Dân gian kể rằng Càn Long để ý chàng thị vệ vì ông giống một người đã mất. Sử không chép." (dị bản **có khung**, quyết định PO 06/11; nội dung truyền thuyết *chưa kiểm chứng*, ở đây chỉ để minh hoạ cấu trúc khung) | "Càn Long để ý chàng trai vì khuôn mặt giống người cũ." (cùng nội dung nhưng khẳng định như sự thật, không khung) |
| 8 | `cl-frank-grigware-van-tay` | "Gần một phần tư thế kỷ trốn chạy; người ta có thể đoán ông quen ngoái nhìn sau lưng mỗi sáng." (2b hedge, trạng thái chung, người đã mất lâu; vẫn nên cân nhắc tầng B vì thế kỷ 20) | "Grigware run bần bật khi nhân viên ấn ngón tay vào bảng mực." (cảnh + hành vi cơ thể bịa) |
| 9 | `cl-black-dahlia-56-phut` | "Chưa đầy một giờ để biết nạn nhân là ai, và đến nay chưa ai biết kẻ giết người là ai." (1 + 3, đối lập; "chưa tìm thấy" là dữ kiện FBI) | "Cô gái trẻ mơ làm minh tinh, sợ hãi bước vào đêm cuối." (nội tâm nạn nhân tầng B; tuổi, ước mơ, đêm cuối đều ngoài nguồn) |
| 10 | `cl-ross-tien-chuoc` | "Có lẽ hắn tin tiền chuộc là thứ không ai lần theo được. Số seri nói khác." (2b hedge về điều hắn tin, kèm dữ kiện FBI) | "Seadlund là kẻ máu lạnh từ nhỏ, sinh ra đã tàn nhẫn." (gán tính cách; nguồn FBI không nói) |
| 11 | `cl-diane-jackson-van-tay` | "Anh trai cô đề nghị xem lại chứng cứ. Một lời đề nghị đơn giản, mà mở lại cả vụ án." (1 + 3) | "Người anh nghẹn ngào, bao năm không ngủ yên." (nội tâm người thật có tên trong hồ sơ, có thể còn sống) |
| 12 | `cl-alger-hiss-khai-man` | "Có những bản án chỉ nói điều người ta chứng minh được, không nói điều người ta ngờ." (3, khái quát về bản án) | "Hiss chắc chắn là điệp viên, tòa chỉ thiếu bằng chứng." (khẳng định ngoài nguồn FBI; gán tội) |
| 13 | `cl-james-ricks-ban-tu` | "Một cuộc trò chuyện trong buồng giam, tưởng chỉ là lời kể, mà đưa vụ án trở lại." (3) | "Người bạn tù ấy cắn rứt lương tâm nên mới thú nhận." (gán động cơ cho người thật; nguồn không nói) |

**Quy tắc rút ra từ 13 cặp:**

- Cột KHÔNG luôn có ít nhất một trong: *hành vi cơ thể/lời nói cụ thể*, *người mới*, *động cơ khẳng định*, *"hôm ấy/đêm ấy" + chi tiết*, *tính cách người thật*.
- Cột ĐƯỢC luôn có một trong: *chủ ngữ là loại hoặc là "bạn"*, *hedge trên trạng thái chung*, *ẩn dụ/so sánh trên dữ kiện đã nêu*, *câu hỏi gắn với hook*.
- Cặp 7 là chỗ quyết định PO 06/11 ("dị bản/phái sinh được nếu đóng khung") chạm guide: **khung phải đi kèm ngay trong câu** ("dân gian kể rằng", "sử không chép"), không đặt đâu đó ở mô tả.

---

## 3. Đánh giá rủi ro và lỗ hổng của đề xuất v3

Xếp theo mức nguy hiểm (C = cao, T = trung bình, X = thấp).

| # | Mức | Lỗ hổng | Agent có thể lợi dụng ra sao | Cách vá (đã đưa vào guide nháp) |
|---|---|---|---|---|
| L1 | C | **Vùng 3 chứa dữ kiện ngầm.** Vùng 3 "tự do" nên không bị kiểm; câu có thể giấu sự thật trong "nhận xét". Ví dụ của chính issue: "Ông không răn con bằng roi, cũng không bằng ngục tù." Đây là **phủ định sự việc**, không phải nhận xét. Tống sử không nói điều đó, và luật Tống có hình phạt cho tham ô. | Gói khẳng định thành ẩn dụ, so sánh, phủ định, so sánh hơn ("nặng hơn mọi hình phạt"), "người ta vẫn gọi...". | Vùng 3 cấm: phủ định sự việc, so sánh hơn về sự việc, số liệu, tuyên bố hiệu ứng. Vùng 3 chỉ nói về *người nghe* hoặc *ý nghĩa*, không về *điều đã xảy ra*. |
| L2 | C | **"Thử nghĩ xem" + khẳng định.** "Thử nghĩ xem, với một gia đình thời Tống, bị đuổi khỏi mộ tổ nghĩa là gì? Là bị gạch tên khỏi dòng họ, mãi mãi." Câu hỏi tu từ dẫn vào một *khẳng định* về tục lệ thời Tống (và "mãi mãi"). Đó là dữ kiện văn hoá chưa có nguồn trong repo. | Câu hỏi tu từ biến luận điểm thành vẻ "chung cuộc đã rõ". | Khẳng định văn hoá phải qua 2a và hedge ("có thể hiểu là") hoặc có nguồn thứ hai. Mẫu 3 dưới đã làm vậy. |
| L3 | C | **"Nếu bạn là người lính gác lăng đêm ấy..."** (ví dụ kỹ thuật 2 trong issue). "Đêm ấy" ngầm khẳng định có một đêm, có một lính gác. Trong repo, báo cáo nghiên cứu Đông Lăng (`GH-228-donglang-research-report.md`) không nhắc lính gác (chưa kiểm chứng ở nguồn gốc). | Tạo nhân vật qua giả thiết rồi cho "nhân vật" làm việc ở các câu sau. | Kỹ thuật 2 chỉ dùng nhân vật **đã có trong bộ dữ kiện** hoặc nhân vật *loại* nói chung ("người thợ", "người dân"); không "đêm ấy/hôm ấy"; một lần mỗi Short. |
| L4 | C | **Hedge laundering.** "Chắc hẳn", "có lẽ" xin phép cả *hành vi*. | "Chắc hẳn ông đã đập bàn và gọi lính vào." Câu qua phép thử hedge nhưng vẫn bịa sự kiện. | Hedge chỉ đi với trạng thái cảm giác chung, không đi với động từ hành vi/lời nói. Có danh sách động từ hành vi bị chặn khi đứng sau tên riêng (mục 4). |
| L5 | C | **Ví dụ mẫu của issue vi phạm cổng hiện có.** Dòng đầu "Có một người cha dặn con cháu: ai tham ô, đừng mong được nằm cạnh tổ tiên." dài 18 từ, vượt `HOOK_MAX_WORDS = 9` trong `build.py`, nên `--preflight` sẽ báo lỗi. Ngoài ra bản đề xuất bỏ câu dẫn nguồn "Tống sử, quyển ba trăm mười sáu", nên vùng 1 hết kiểm chứng được ngay trong video (trái tinh thần quyết định 06/11: đóng khung "có nguồn nói"). | Agent bắt chước ví dụ mẫu và bị chặn, hoặc bỏ nguồn. | Ví dụ mẫu trong guide v3 phải qua preflight và giữ câu nguồn. Mẫu 1 ở mục 5 làm vậy. |
| L6 | T | **Tự gán vùng.** Agent viết tự quyết câu nào vùng nào; câu bịa dễ được gắn "vùng 3". | Gắn nhãn dễ cho câu rủi ro. | Gán vùng bằng *quy tắc cơ học* (có số/tên/ngày/lời trích/ai-làm-gì thì luôn vùng 1), không bằng ý định. Kiểm tự động và nhãn cùng lúc (mục 4). |
| L7 | T | **Lằn ranh đỏ 1 mơ hồ**: "bịa rồi trình bày *như sự thật*". Agent bảo "tôi không trình bày như sự thật" vì có hedge nhẹ. | Hedge một lần ở câu đầu rồi viết cảnh dài như thật. | Đổi từ ý định sang cấu trúc: vùng 2/3 không chứa danh từ/sự kiện mới (phép thử 2). |
| L8 | T | **Lằn ranh đỏ 2 chỉ cấm "xấu".** Nội tâm tốt hoặc trung tính gán bừa ("ông luôn thương dân như con") vẫn bịa, và nạn nhân/thân nhân không được nhắc. | Gán nội tâm nhẹ nhàng cho người thật, nhất là nạn nhân. | Hướng dẫn tầng A/B/C ở dạng khuyến nghị (câu 2). |
| L9 | T | **Rò sang BUD.** Issue nói "luật nguồn không cứng, thay hàng rào". Nếu guide chung bị agent BUD đọc, "vùng 2" có thể sinh chi tiết gán cho Đức Phật, trái quyết định PO (BUD giữ chặt). | Agent BUD áp vùng 2 vào chuyện Phật. | Ghi rõ đầu guide: phạm vi CL/MIM/CK; BUD giữ luật riêng. Đã làm trong guide nháp. |
| L10 | T | **Câu hỏi có tiền giả định** ("Vì sao Gia Khánh căm ghét Hòa Thân đến thế?") dựng sẵn một sự thật trong câu hỏi. | Câu hỏi tu từ chở khẳng định. | Câu hỏi không chứa mệnh đề khẳng định về người thật. Lint bắt "vì sao [tên] + động từ tâm lý" (mục 4). |
| L11 | T | **Tiêu chí "≥ 1 khoảnh khắc đồng cảm mỗi Short"** có thể thành chỉ tiêu máy, khiến agent chèn một câu sến cho đủ. | Chèn "Thử nghĩ xem..." vào mọi bài. | Đổi thành "tối đa", và luật xoay vòng cụm mở. Đo bằng nghe thử, không bằng đếm. |
| L12 | T | **Đo 72 giờ không phân biệt được văn phong** và vế "≥ 1 sub/1.000 views" đã đạt từ trước (câu 5). | Kết luận thành công giả hoặc thất bại giả, rồi sửa guide theo tín hiệu nhiễu. | Thiết kế đo ở câu 5. |
| L13 | X | **Đồng cảm tăng độ dài, đẩy Short ra ngoài khung 25–40 giây** của preflight. Ba mẫu dưới đã phải cắt để vừa. | Chèn câu cảm xúc, vượt ngưỡng, rồi "sửa" bằng cách bỏ dữ kiện. | Khuyến nghị trong guide: dữ kiện vùng 1 đi trước và không được cắt để nhường chỗ cho vùng 2/3. |
| L14 | X | **Nhận định về nguồn khi không đọc được nguồn.** Quy tắc `AGENTS.md`: không mở được nguồn thì bỏ hoặc nói rõ "theo...". v3 làm mờ điều này nếu agent coi mọi thứ là vùng 2. | Chuyển một khẳng định không kiểm được từ vùng 1 xuống vùng 2 cho "an toàn". | Quy tắc hạ cấp: không kiểm được thì *bỏ* hoặc nêu "theo X", không hạ xuống vùng 2. |

---

## 4. Cơ chế kiểm tự động hoặc bán tự động (chỉ ý tưởng, chưa code)

**Theo chỉ đạo PO 10/11: tất cả chỉ là cảnh báo, không chặn.** Ý 1–12 dưới đây đọc theo nghĩa đó. Chỗ nối cụ thể ở mục 4b.

Cơ sở trong repo: `motion/stier/build.py --preflight` đã có sẵn cổng tĩnh (số từ, thời lượng ước lượng, hook, ký hiệu viết tắt). `motion/stier/script_lint.py` có mẫu luật (CLICHE, LECTURE, REHOOK, nhịp); hiện chỉ gọi cho BUD. `motion/long/factcheck_lint.py` đối chiếu số/ngày/TRÍCH DỊCH với `factcheck.md` cho Long, chưa có cho Short CL.

1. **Thẻ vùng cho từng câu.** Spec Short thêm trường song song `zones` (ví dụ `["1","1","1","2a","2a","3",...]`) cạnh `lines`. Preflight báo lỗi nếu thiếu hoặc lệch số câu. Lời đọc không đổi, nên TTS không bị ảnh hưởng.
2. **Quy tắc gán vùng cơ học (bắt nhãn nói dối).** Câu chứa chữ số, số đọc thành chữ, tên riêng, từ "theo ... chép", dấu trích dẫn, hoặc động từ hành động đứng sau tên người: bắt buộc `zones = 1`. Nếu agent gán 2 hoặc 3 mà câu có các dấu hiệu đó, báo lỗi. Bắt tên riêng và số bằng cách dùng danh sách tên có trong gói dữ kiện của bài.
3. **Đối chiếu "danh từ mới" (cơ chế rẻ mà mạnh nhất).** Mỗi Short có một *gói dữ kiện* (các số, ngày, tên riêng, danh từ chủ chốt từ vùng 1/nguồn). Với câu vùng 2/3, trích mọi số, tên riêng và các từ chỉ người/chức danh ("lính", "thợ", "vua", "thầy thuốc"). Cái nào không có trong gói dữ kiện và không thuộc danh sách "loại chung cho phép" (`bạn`, `người thời ấy`, `người cầm quyền`, `một gia đình`...) thì cảnh báo mạnh. Đây chính là phép thử 2 ở câu 1.
4. **Factcheck chỉ áp lên vùng 1, nhưng bắt buộc đầy đủ.** Chạy `factcheck_lint`-kiểu cho Short: mọi số/ngày/tên ở vùng 1 phải có dòng nguồn (URL) trong file `GH-…-lines` hoặc spec `sources`. Vùng 2, 3 không được xuất hiện số/ngày (xem mục 3 ở trên). Tách như vậy giữ nguyên "factcheck không đổi" của tiêu chí đạt trong issue.
5. **Lint cụm phỏng đoán.** Danh sách từ hedge (`có lẽ`, `chắc hẳn`, `thử hình dung`, `có thể hiểu là`, `dân gian kể rằng`). Quy tắc: câu vùng 2b *phải* chứa ít nhất một hedge; câu vùng 1 *không* được chứa hedge (tránh "hedge cho an toàn" làm sự thật cứng thành mềm); câu vùng 2b không được chứa động từ hành vi bị chặn đứng cạnh tên riêng: `khóc, nghiến, run, quỳ, hét, thì thầm, đập bàn, rưng rưng, nghẹn ngào, thở dài, siết chặt`... Danh sách do PO duyệt.
6. **Lint nội tâm nhân vật theo tầng.** Spec khai `person_tier: {tên: A|B|C}`; câu 2b gắn tên tầng B hoặc C bị chặn cứng. Tên và tầng để Lead/PO điền khi duyệt gói dữ kiện, không để agent viết tự khai.
7. **Lint cảm xúc dán nhãn và sáo.** Mượn `CLICHE`/`LECTURE` của `script_lint.py`, thêm danh sách tính từ cảm xúc dán nhãn (`xót xa, đau đớn, nghẹn ngào, kinh hoàng, rùng mình, bi thảm`). Cảnh báo, không chặn.
8. **Lint tic lặp giữa các Short CL.** Hiện `script_lint.recent()` chỉ nhìn `bud-*.json`. Mở rộng ý tưởng cho `cl-*.json`: cụm mở "Thử nghĩ xem", "Nếu bạn là", "Còn bạn" không được lặp quá 1 lần trong 3 Short gần nhất; câu cuối không được cùng khuôn với 3 Short gần nhất.
9. **Lint câu hỏi.** Câu hỏi tu từ chứa tên người thật cùng động từ tâm lý ("vì sao Gia Khánh căm ghét...") bị bắt (tiền giả định). Câu hỏi cuối bài phải gắn một từ của hook (tương tự luật R4 của BUD).
10. **Báo cáo đối chiếu cũ/mới (bán tự động, mắt người).** Công cụ sinh bảng hai cột: câu cũ và câu mới, tô màu theo vùng, liệt kê cặp "dữ kiện giữ/mất/thêm" (bắt thêm số/tên mới). PO duyệt 2–3 bài mẫu đọc bảng này và nghe TTS thử, không cần đọc JSON.
11. **Giám khảo LLM (tuỳ chọn, chỉ hỗ trợ).** Nếu sau này cần "soát bịa" bằng model khác, theo kết luận của #110–#125 trong bộ nhớ dự án (LLM tự duyệt không đạt; chỉ hỗ trợ), kết quả phải qua người trước khi dùng. Không phải điều kiện cần của v3.
12. **Đo trước khi tin.** Trước khi bật lint làm cổng cứng, chạy ở chế độ cảnh báo trên các lời đọc CL hiện có (12 bài trong GH-228 và các spec `cl-*`) để biết tỷ lệ báo nhầm. Một cổng báo nhầm nhiều sẽ bị agent tìm cách lách.

---

## 4b. Guide v3 nối vào đâu để agent viết bài sau tự động theo v3

Vấn đề thực tế: agent sản xuất chỉ đọc `AGENTS.md`, `docs/codex/long-rules.md`, `docs/codex/long-cheatsheet.md` và brief; **không đọc `docs/pm/`**. Guide để ở `docs/pm/` thì không agent nào theo. Chi tiết đầy đủ ở guide nháp mục 12. Tóm tắt:

1. `creator_v2/AGENTS.md`, "Luật nội dung": thêm đoạn trỏ tới guide, ghi lằn ranh đỏ chỉ ba điều (chữ).
2. `creator_v2/docs/codex/long-rules.md`: thêm mục "Giọng kể" một trang (ba vùng, sáu kỹ thuật) (chữ).
3. Mẫu brief `docs/pm/tickets/GH-<số>-<agent>.md`: hai dòng chuẩn "viết theo v3, ghi bảng vùng vào báo cáo" (chữ).
4. `creator_v2/motion/stier/build.py`, cạnh `hypo_preflight_warnings`: hàm cảnh báo (chỉ in, không đổi mã thoát) cho câu hỏi có tiền giả định, động từ hành vi sau tên riêng, từ gọi tên cảm xúc dựng sẵn, lặp khuôn so với Short `cl-*` gần nhất; `--preflight` chạy sẵn trước mọi render.
5. Trường `zones` tuỳ chọn trong spec Short; không có thì bỏ qua.
6. `motion/long/factcheck_lint.py` / `script_lines.py` (Long): factcheck vẫn như cũ nhưng nhận thẻ vùng tuỳ chọn để không đòi nguồn cho câu nhận định (vùng 2b/3).
7. `.claude/skills/long-script/SKILL.md` (BUD/FS): tham chiếu kỹ thuật giọng kể cho FS; **BUD thêm đúng một câu** (không gán cho Đức Phật lời hay việc ngoài kinh), luật nguồn BUD giữ nguyên.
8. Công cụ nhỏ sinh bảng đối chiếu cũ/mới cho PO duyệt mẫu.

Thứ tự: 1–3 (chỉ là chữ) ngay sau duyệt; 4–5 (cảnh báo) kế tiếp; 6 và 8 sau. Không điểm nào làm spec cũ hỏng.

---

## 5. Ba Short mẫu viết lại theo v3

Quy ước vùng: **[1]** sự thật cứng; **[2a]** tái dựng, bối cảnh chung; **[2b]** tái dựng, cảm giác phỏng đoán của nhân vật (có hedge); **[3]** giọng người kể.

Tất cả số viết như các Short hiện tại: chữ, không chữ số ("một nghìn bảy trăm chín mươi chín"). Không ký hiệu lạ, không ngoặc, không gạch ngang; câu một hơi. Khoảng lặng bằng câu ngắn.

### Mẫu 1. `cl-bao-s2-loi-cam` (Bao Chửng, lời dặn về mộ tổ)

*Dữ kiện chỉ dựa trên đoạn "Hiện tại" trong issue. Không có spec thật để đối chiếu nên không thêm dữ kiện nào.*

**Bản cũ (nguyên văn trong issue)**

> Bao Chửng cấm con cháu tham ô về nhà. Ông nói kẻ nhận hối lộ thì không được chôn vào mộ tổ. Câu ấy đứng trong Tống sử, quyển ba trăm mười sáu.

Ghi chú: chỉ khoảng 33 từ, thấp hơn ngưỡng preflight (55 từ, 25 giây); bản cũ trong issue có thể đã bị rút gọn khi trích.

**Bản mới (v3)**

| # | Câu | Vùng | Ghi chú |
|---|---|---|---|
| 1 | Con cháu tham ô, Bao Chửng cấm về nhà. | [1] | Hook 9 từ; giữ dữ kiện cũ, đảo trật tự để gây tò mò |
| 2 | Ông nói kẻ nhận hối lộ thì không được chôn vào mộ tổ. | [1] | nguyên dòng cũ |
| 3 | Câu ấy đứng trong Tống sử, quyển ba trăm mười sáu. | [1] | giữ nguồn trong lời (khác bản đề xuất của issue) |
| 4 | Với một gia đình thời xưa, mộ tổ không chỉ là một nấm đất. | [2a] | khái quát, chủ ngữ là loại; cần nguồn thứ hai về tục lệ thời Tống (chưa có trong repo, chưa kiểm chứng) |
| 5 | Đó là nơi cả dòng họ nằm lại bên nhau. | [2a] | như trên |
| 6 | Bị đuổi khỏi đó, có thể hiểu là bị gạch tên khỏi dòng họ. | [2a] | hedge "có thể hiểu là"; bỏ "mãi mãi" của bản issue |
| 7 | Cả khi đã chết. | [2a] | câu ngắn, khoảng lặng |
| 8 | Đặt mình vào chỗ con cháu ông, lời dặn ấy nặng đến mức nào? | [3] | kéo người nghe vào; không có nhân vật mới |
| 9 | Một lời dặn ngắn, nhưng chạm vào điều người thời ấy rất coi trọng. | [3] | nhận xét, không hứa hiệu ứng cụ thể |
| 10 | Với bạn, điều gì đủ nặng để giữ một người khỏi tham ô? | [3] | câu hỏi cuối gắn với hook ("tham ô") |

**Đọc thử liền mạch (TTS):**

> Con cháu tham ô, Bao Chửng cấm về nhà. Ông nói kẻ nhận hối lộ thì không được chôn vào mộ tổ. Câu ấy đứng trong Tống sử, quyển ba trăm mười sáu. Với một gia đình thời xưa, mộ tổ không chỉ là một nấm đất. Đó là nơi cả dòng họ nằm lại bên nhau. Bị đuổi khỏi đó, có thể hiểu là bị gạch tên khỏi dòng họ. Cả khi đã chết. Đặt mình vào chỗ con cháu ông, lời dặn ấy nặng đến mức nào? Một lời dặn ngắn, nhưng chạm vào điều người thời ấy rất coi trọng. Với bạn, điều gì đủ nặng để giữ một người khỏi tham ô?

**Đối chiếu dữ kiện:** giữ nguyên Bao Chửng, tham ô, cấm về nhà, kẻ nhận hối lộ không được chôn vào mộ tổ, Tống sử quyển ba trăm mười sáu. Thêm số/tên/ngày mới: **không**. Thay đổi so với đề xuất trong issue: bỏ "Ông không răn con bằng roi, cũng không bằng ngục tù" (phủ định không nguồn, lỗ hổng L1); bỏ "mãi mãi"; giữ câu nguồn; hook ≤ 9 từ.

**Đo thủ công theo preflight:** 116 từ, khoảng 35 giây (3,3 từ/giây), hook 9 từ; trong khung 55–135 từ và 25–40 giây. Hook có "Bao Chửng" (giả định nằm trong tiêu đề). Chưa chạy `build.py --preflight` thật.

### Mẫu 2. `cl-bao-nghien-muc` (Bao Chửng rời Đoan Châu không mang một nghiên mực)

*Nguồn trong spec: Tống sử q.316 (Wikisource) và bài Wikipedia về Bao Chửng.*

**Bản cũ (từ spec, 99 từ)**

> Một chiếc nghiên mực phơi ra đường quà cáp. Đoan Châu nổi tiếng vì nghiên đá được đem cống triều đình. Tống sử chép các quan trước thu gấp hàng chục lần số phải nộp. Phần thừa được đưa làm quà cho người quyền thế. Bao Chửng ra lệnh thợ chỉ làm đủ số cống. Hết nhiệm kỳ, ông không mang theo một chiếc nghiên nào. Theo bài viết về Bao Chửng, ông rời Đoan Châu năm một nghìn không trăm bốn mươi ba. Vật dùng để viết cũng có thể trở thành món quà đổi lấy quyền lực.

**Bản mới (v3)**

| # | Câu | Vùng | Ghi chú |
|---|---|---|---|
| 1 | Một chiếc nghiên mực phơi ra đường quà cáp. | [3] | giữ nguyên hook cũ (9 từ), ẩn dụ |
| 2 | Đoan Châu nổi tiếng vì nghiên đá được đem cống triều đình. | [1] | nguyên dòng |
| 3 | Tống sử chép các quan trước thu gấp hàng chục lần số phải nộp. | [1] | nguyên dòng |
| 4 | Phần thừa được đưa làm quà cho người quyền thế. | [1] | nguyên dòng |
| 5 | Thử hình dung bạn là người thợ đá ở đó. | [2a] | đặt người nghe vào cảnh; chủ ngữ loại ("người thợ", "bạn") |
| 6 | Bạn phải đẽo thêm hàng chục chiếc để làm quà. | [2a] | suy trực tiếp từ dòng 3; nếu nguồn nói khác thì bỏ |
| 7 | Bao Chửng ra lệnh thợ chỉ làm đủ số cống. | [1] | nguyên dòng |
| 8 | Một mệnh lệnh nghe nhỏ, nhưng chặn đúng cửa quà cáp. | [3] | đối lập nhỏ/lớn; suy trực tiếp từ dòng 4 và 7 |
| 9 | Hết nhiệm kỳ, ông không mang theo một chiếc nghiên nào. | [1] | nguyên dòng |
| 10 | Theo bài viết về Bao Chửng, ông rời Đoan Châu năm một nghìn không trăm bốn mươi ba. | [1] | nguyên dòng, giữ năm và "theo" |
| 11 | Một chiếc nghiên cũng đổi được quyền lực. Bạn có dám bỏ lại nó? | [3] | thay dòng kết cũ bằng ý nghĩa và câu hỏi; vẫn gọi lại hook (nghiên) |

**Đọc thử liền mạch (TTS):**

> Một chiếc nghiên mực phơi ra đường quà cáp. Đoan Châu nổi tiếng vì nghiên đá được đem cống triều đình. Tống sử chép các quan trước thu gấp hàng chục lần số phải nộp. Phần thừa được đưa làm quà cho người quyền thế. Thử hình dung bạn là người thợ đá ở đó. Bạn phải đẽo thêm hàng chục chiếc để làm quà. Bao Chửng ra lệnh thợ chỉ làm đủ số cống. Một mệnh lệnh nghe nhỏ, nhưng chặn đúng cửa quà cáp. Hết nhiệm kỳ, ông không mang theo một chiếc nghiên nào. Theo bài viết về Bao Chửng, ông rời Đoan Châu năm một nghìn không trăm bốn mươi ba. Một chiếc nghiên cũng đổi được quyền lực. Bạn có dám bỏ lại nó?

**Đối chiếu dữ kiện:** giữ đủ Đoan Châu, nghiên đá cống, Tống sử, "các quan trước thu gấp hàng chục lần", phần thừa làm quà cho người quyền thế, Bao Chửng ra lệnh thợ làm đủ số cống, hết nhiệm kỳ không mang nghiên, năm một nghìn không trăm bốn mươi ba. Số/tên/ngày mới: **không**. Câu cũ "Vật dùng để viết cũng có thể trở thành món quà đổi lấy quyền lực" được chuyển thành câu vùng 3 ngắn hơn ở dòng 11.

**Đo thủ công:** 129 từ, khoảng 39 giây, hook 9 từ (sát trần 40 giây) (có số "một" và "nghiên"/"mực" từ khoá tiêu đề). Trong khung.

### Mẫu 3. `cl-hoa-than-hai-muoi-toi` (Hai mươi tội của Hòa Thân bắt đầu bằng gì?)

*Nguồn trong spec: Thanh sử cảo q.319 (Wikisource).*

**Bản cũ (từ spec, 97 từ)**

> Hai mươi tội, nhưng dòng đầu không nói bạc. Năm một nghìn bảy trăm chín mươi chín, Gia Khánh công bố tội của Hòa Thân. Thanh sử cảo chép rằng trước khi ngôi thái tử được công bố, Hòa Thân đã dâng ngọc như ý. Bản cáo tội đặt hành động ấy ở vị trí đầu tiên. Những tội tiếp theo kể chuyện cưỡi ngựa vào vườn và đi kiệu vào cung. Các khoản tài sản xuất hiện ở phần sau của danh sách. Bản án mở đầu bằng chuyện ở quá gần người sắp lên ngôi.

**Bản mới (v3)**

| # | Câu | Vùng | Ghi chú |
|---|---|---|---|
| 1 | Hai mươi tội, nhưng dòng đầu không nói bạc. | [1] | nguyên hook cũ |
| 2 | Năm một nghìn bảy trăm chín mươi chín, Gia Khánh công bố tội của Hòa Thân. | [1] | nguyên dòng |
| 3 | Thanh sử cảo chép rằng trước khi ngôi thái tử được công bố, Hòa Thân đã dâng ngọc như ý. | [1] | nguyên dòng |
| 4 | Bản cáo tội đặt hành động ấy ở vị trí đầu tiên. | [1] | nguyên dòng |
| 5 | Thử nghĩ xem, vì sao một món quà lại đứng đầu? | [3] | câu hỏi mở vòng; không chứa khẳng định về động cơ |
| 6 | Những tội tiếp theo kể chuyện cưỡi ngựa vào vườn và đi kiệu vào cung. | [1] | nguyên dòng |
| 7 | Các khoản tài sản xuất hiện ở phần sau của danh sách. | [1] | nguyên dòng |
| 8 | Có lẽ trong mắt người cầm quyền, đứng quá gần ngôi báu đáng sợ hơn giữ nhiều bạc. | [2b] | hedge "có lẽ"; chủ ngữ loại ("người cầm quyền"); chỉ là cách hiểu, thay cho câu cũ khẳng định "bản án mở đầu bằng chuyện ở quá gần người sắp lên ngôi" |
| 9 | Nếu bạn là hoàng đế, bạn sẽ ghi tội nào lên đầu? | [3] | câu hỏi cuối, gọi lại hook ("tội", "đầu") |

**Đọc thử liền mạch (TTS):**

> Hai mươi tội, nhưng dòng đầu không nói bạc. Năm một nghìn bảy trăm chín mươi chín, Gia Khánh công bố tội của Hòa Thân. Thanh sử cảo chép rằng trước khi ngôi thái tử được công bố, Hòa Thân đã dâng ngọc như ý. Bản cáo tội đặt hành động ấy ở vị trí đầu tiên. Thử nghĩ xem, vì sao một món quà lại đứng đầu? Những tội tiếp theo kể chuyện cưỡi ngựa vào vườn và đi kiệu vào cung. Các khoản tài sản xuất hiện ở phần sau của danh sách. Có lẽ trong mắt người cầm quyền, đứng quá gần ngôi báu đáng sợ hơn giữ nhiều bạc. Nếu bạn là hoàng đế, bạn sẽ ghi tội nào lên đầu?

**Đối chiếu dữ kiện:** giữ đủ hai mươi tội, năm một nghìn bảy trăm chín mươi chín, Gia Khánh, Hòa Thân, Thanh sử cảo, ngọc như ý, trước khi công bố ngôi thái tử, vị trí đầu tiên, cưỡi ngựa vào vườn, đi kiệu vào cung, tài sản ở phần sau. Số/tên/ngày mới: **không**. Một thay đổi có chủ đích: dòng cũ "Bản án mở đầu bằng chuyện ở quá gần người sắp lên ngôi" là một **diễn giải được nói như sự thật**; v3 chuyển nó thành vùng 2b có hedge. Nó trung thực hơn, và nghe có người hơn.

**Đo thủ công:** 125 từ, khoảng 38 giây, hook 9 từ (có số "hai"). Trong khung.

### Nhận xét chung về ba mẫu

- Cả ba giữ nguyên ≥ 80% dòng cũ vùng 1. Phần "cảm xúc" được cộng thêm 3–4 câu, không thay thế dữ kiện.
- Cả ba **phải cắt** để vừa khung (mẫu 2 còn sát trần 40 giây) 25–40 giây: dòng đồng cảm không miễn phí về thời lượng (lỗ hổng L13).
- Mẫu 3 cho thấy v3 không chỉ "thêm cảm xúc", mà còn **phát hiện chỗ v2 nói như sự thật một điều chỉ là diễn giải**.
- Câu hỏi và "bạn" xuất hiện ở cả ba; nếu dùng cho 9 bài cần xoay cụm mở (mục 4, ý 8).

---

## 6. Phần còn thiếu / cần làm tiếp cho riêng đề xuất (để Lead và PO tham khảo)

- Chưa có "gói dữ kiện" chuẩn cho Short; muốn cơ chế đối chiếu "danh từ mới" chạy được thì mỗi Short cần một gói (số, ngày, tên, danh từ chủ chốt, URL). Kho GH-228 `*-lines.md` đã gần như là gói này.
- Phải có một nguồn thứ hai cho mọi khẳng định văn hoá ở vùng 2a (tục lệ thời Tống, ý nghĩa mộ tổ...). Hiện repo không có nguồn nào. *Chưa kiểm chứng.*
- Phải nghe thử TTS: (a) câu hỏi có lên giọng không; (b) câu 3–4 từ ("Cả khi đã chết.") có tạo khoảng lặng hay chỉ cụt.
- Phải mở lại 9 Short thật và chạy lại phần mẫu khi Lead tìm lại được các file bị thiếu (mục 0b).

---

## 7. Kết luận gửi PO

**DUYỆT CÓ SỬA.** Đồng ý đổi hướng sang ba vùng. Chưa nên viết lại 9 Short và chưa nên đăng đo cho đến khi các điều chỉnh dưới đây được chấp nhận.

### Điều chỉnh (xếp theo mức quan trọng, đã theo chỉ đạo "linh hoạt, không thêm luật cứng")

1. **Giữ đúng 3 lằn ranh đỏ của issue** (BUD thêm một câu về Đức Phật). Không mở rộng thêm.
2. **Vùng 2 thêm ba câu tự hỏi** (có thêm sự kiện mới? chủ ngữ là loại hay tên riêng làm việc mới? nghe như một lần cụ thể?), như gợi ý. Tách 2a/2b để người viết biết chỗ nào cần điểm tựa. Hedge đi với cảm giác, không với hành vi.
3. **Nêu cái bẫy của vùng 3** (phủ định sự việc, so sánh hơn, tuyên bố hiệu ứng) như lưu ý, và **sửa ví dụ mẫu của issue**: hook 18 từ vượt `HOOK_MAX_WORDS = 9` nên bị preflight chặn, câu "không răn bằng roi, cũng không bằng ngục tù" là khẳng định ngầm, bản đề xuất bỏ câu nguồn. Dùng Mẫu 1 mục 5.
4. **Người thật còn thân nhân: khuyến nghị**, không luật (nên không viết nội tâm nạn nhân/thân nhân; thoải mái với nhân vật công đã mất lâu).
5. **Nối guide vào đúng chỗ agent đọc và chạy** (mục 4b): `AGENTS.md`, `long-rules.md`, brief, cảnh báo trong `build.py --preflight`. Chỉ cảnh báo, spec cũ không hỏng.
6. **Sửa tiêu chí đo.** Bỏ vế "≥ 1 sub/1.000 views" (nền hiện tại ≈ 1,1 đã đạt). Đo giữ chân, đối chứng đồng thời xen kẽ, đăng ký trước, mốc quyết định 7 ngày, ghép cặp theo loại. Chốt "trung vị của tập nào".
7. **Giữ câu dẫn nguồn trong lời đọc** và đóng khung dị bản ngay trong câu, đúng quyết định 06/11.
8. **Xoay cụm mở giữa các Short** để cả lô không thành một khuôn.

### Cần PO quyết

1. Có muốn cố định mốc "nhân vật đã mất lâu" (tham khảo: khoảng một thế kỷ) hay để người viết tự cân.
2. Có muốn chốt danh sách nhân vật "đã mất lâu" (ví dụ Bao Chửng, Gia Khánh, Hòa Thân, Càn Long) hay để người viết tự cân khi viết.
3. Chấp nhận thiết kế đo ghép cặp (cần giữ 3 bài lời v2 làm đối chứng, hoặc tăng cỡ lô).
4. Có cần nguồn thứ hai cho các khẳng định văn hoá vùng 2a, hay cho phép "có thể hiểu là" mà không nguồn.
5. Ai tìm lại 4 file đầu vào bị thiếu (mục 0b) để chạy lại phần đối chiếu.
