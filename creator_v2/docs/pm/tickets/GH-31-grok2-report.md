# Báo cáo GH-31 (Grok vòng 2): Kiểm tra sâu 3 nguồn thử nghiệm nội bộ, Nguồn quốc tế & Benchmark sự kiện nóng 72h (31/10–02/11/2026)

- **Ticket:** [GH-31-grok2.md](<thư mục làm việc>/Youtube_Creator_V2/docs/pm/tickets/GH-31-grok2.md) (Issue `#31`)
- **Thiết kế tham chiếu:** [2026-11-02-trend-engine-v1.md](<thư mục làm việc>/Youtube_Creator_V2/docs/pm/2026-11-02-trend-engine-v1.md)
- **Thời điểm thực hiện:** 02/11/2026 (18:35–19:12 UTC+7)
- **File bàn giao:**
  1. [GH-31-sources-v2.json](<thư mục làm việc>/Youtube_Creator_V2/docs/pm/tickets/GH-31-sources-v2.json) — 20 mục cập nhật/thêm mới (3 nguồn `trial_ok`, 2 nguồn VietNamNet `pending`, 15 nguồn quốc tế), đã kiểm thực 100% qua `load_sources()` của [sources.py](<thư mục làm việc>/Youtube_Creator_V2/factory/trend/sources.py).
  2. [GH-31-benchmark.json](<thư mục làm việc>/Youtube_Creator_V2/docs/pm/tickets/GH-31-benchmark.json) — 38 sự kiện nóng thực tế trong 72h qua (**18 sự kiện MIM**, **20 sự kiện CK**), mỗi sự kiện có từ 2–8 URL sống thuộc ≥ 2 `owner_group` độc lập.
  3. [GH-31-grok2-report.md](<thư mục làm việc>/Youtube_Creator_V2/docs/pm/tickets/GH-31-grok2-report.md) — báo cáo tổng hợp này.

---

## 1. Kiểm tra kỹ thuật & điều khoản 3 nguồn thử nghiệm nội bộ (`Task 1`)

Chủ dự án đã chấp thuận rủi ro cho 3 feed (`thanhnien_cong_nghe`, `thanhnien_kinh_te`, `genk_tin_ict`) chạy thử nghiệm nội bộ ở P0 (chỉ đọc tiêu đề + link làm tín hiệu phát hiện đề tài, không xuất bản lại nội dung). Kết quả kiểm tra trực tiếp từng endpoint ngày 02/11/2026 như sau:

### 1.1. Bảng tổng hợp 3 nguồn thử nghiệm nội bộ

| ID nguồn | URL feed sống & Số item trả về | Kết quả kiểm tra `robots.txt` (nguyên văn dòng liên quan) | Kết quả đọc trang điều khoản / footer (trích nguyên văn ≤ 25 chữ + URL) | Giới hạn tần suất đề xuất | Kết luận đề xuất |
|---|---|---|---|---|---|
| `thanhnien_cong_nghe` | `https://thanhnien.vn/rss/cong-nghe.rss`<br>**HTTP 200 OK — 50 items** (bài mới nhất: `02/11/2026 16:42 +0700`) | **Không chặn RSS, không có `Crawl-delay`.**<br>URL: `https://thanhnien.vn/robots.txt`<br>`User-agent: *`<br>`Allow: /`<br>`Disallow: /news-*.htm` | **Không có câu cấm bot/automated/harvesting; không có chữ "phi lợi nhuận".**<br>Trích (21 chữ): *"Khi sử dụng lại các tin lấy từ Báo Thanh Niên, bạn phải ghi rõ nguồn tin là 'Theo Báo Thanh Niên'..."*<br>URL: `https://thanhnien.vn/rss.html` | `<= 1 request / feed / 3h` (tối đa 8 req/ngày); cách ≥ 5s giữa các feed `thanhnien.vn`; gửi `ETag`/`If-Modified-Since` + `User-Agent` định danh rõ | **`trial_ok`**<br>(`tos_status: "ok"`, `trial_status: "trial_ok"`) |
| `thanhnien_kinh_te` | `https://thanhnien.vn/rss/kinh-te.rss`<br>**HTTP 200 OK — 50 items** (bài mới nhất: `02/11/2026 18:52 +0700`) | **Không chặn RSS, không có `Crawl-delay`.**<br>URL: `https://thanhnien.vn/robots.txt`<br>`User-agent: *`<br>`Allow: /`<br>`Disallow: /news-*.htm` | **Không có câu cấm bot/automated/harvesting; không có chữ "phi lợi nhuận".**<br>Trích (21 chữ): *"Khi sử dụng lại các tin lấy từ Báo Thanh Niên, bạn phải ghi rõ nguồn tin là 'Theo Báo Thanh Niên'..."*<br>URL: `https://thanhnien.vn/rss.html` | `<= 1 request / feed / 3h` (tối đa 8 req/ngày); cách ≥ 5s giữa các feed `thanhnien.vn`; gửi `ETag`/`If-Modified-Since` + `User-Agent` định danh rõ | **`trial_ok`**<br>(`tos_status: "ok"`, `trial_status: "trial_ok"`) |
| `genk_tin_ict` | **Lưu ý sửa URL:** URL cũ `https://genk.vn/tin-ict.rss` trả **HTTP 404 (0 item)**.<br>URL sống trên danh mục RSS: **`https://genk.vn/rss/tin-ict.rss`**<br>**HTTP 200 OK — 61 items** (bài mới nhất: `02/11/2026 18:29 +0700`) | **Không có bất kỳ dòng `Disallow` hay `Crawl-delay` nào; mở `Allow: /` cho cả `*` lẫn AI crawlers.**<br>URL: `https://genk.vn/robots.txt`<br>`User-agent: *`<br>`Allow: /`<br>`User-agent: GPTBot`<br>`Allow: /` | **Không có câu cấm bot/automated/harvesting; không có chữ "phi lợi nhuận".**<br>Trích (20 chữ): *"Khi sử dụng lại các tin lấy từ Genk.vn, bạn phải ghi rõ nguồn tin là 'Theo Genk.vn' hoặc 'Genk.vn'."*<br>URL: `https://genk.vn/rss.chn` (`https://genk.vn/index.rss`) | `<= 1 request / feed / 3h` (tối đa 8 req/ngày); gửi `ETag`/`If-Modified-Since` + `User-Agent` định danh rõ | **`trial_ok`**<br>(sau khi cập nhật `url` thành `https://genk.vn/rss/tin-ict.rss`; `tos_status: "ok"`, `trial_status: "trial_ok"`) |

### 1.2. Ghi chú kỹ thuật quan trọng cho `genk_tin_ict` và schema `sources.py`
1. **Phát hiện lỗi URL của `genk_tin_ict`:** Trong bản vòng 1 (`GH-31-sources.json` và `factory/trend/sources.json`), URL `https://genk.vn/tin-ict.rss` trả về **HTTP 404 Not Found**. Khi mở trang danh mục RSS chính thức `https://genk.vn/rss.chn` (redirect về `https://genk.vn/index.rss`), đường dẫn thực tế đang hoạt động là **`https://genk.vn/rss/tin-ict.rss`** (HTTP 200 OK, 61 bài). Các chuyên mục khác của GenK như `https://genk.vn/rss/ai.rss` (61 bài) và `https://genk.vn/rss/home.rss` (61 bài) cũng dùng tiền tố `/rss/`. Đã cập nhật URL đúng vào [GH-31-sources-v2.json](<thư mục làm việc>/Youtube_Creator_V2/docs/pm/tickets/GH-31-sources-v2.json).
2. **Tương thích với `factory/trend/sources.py`:** Hàm `load_sources()` trong [sources.py](<thư mục làm việc>/Youtube_Creator_V2/factory/trend/sources.py#L22-L26) chỉ chấp nhận `tos_status in {"ok", "pending", "blocked"}` và `scan.py` chỉ quét các nguồn có `tos_status == "ok"`. Do đó trong [GH-31-sources-v2.json](<thư mục làm việc>/Youtube_Creator_V2/docs/pm/tickets/GH-31-sources-v2.json), cả 3 nguồn được gắn `"tos_status": "ok"` kèm trường `"trial_status": "trial_ok"` để hệ thống quét chạy trực tiếp không lỗi `ValueError`.

---

## 2. Kết luận kiểm tra VietNamNet (`Task 2`)

> *Lưu ý theo brief:* **CafeF** (`cafef_tai_chinh_ngan_hang`, `cafef_vi_mo_dau_tu`) có điều khoản *"không vì mục đích thương mại"* trên `https://cafef.vn/rss.chn` nên **giữ nguyên `pending`**, không kiểm lại.

Kết quả kiểm tra trực tiếp **VietNamNet** (`vietnamnet_kinh_doanh`, `vietnamnet_cong_nghe`) ngày 02/11/2026:

1. **Kiểm tra `robots.txt` (`https://vietnamnet.vn/robots.txt` — HTTP 200 OK):**
   ```text
   User-agent: * 
   Allow: /
   Disallow: /tim-kiem?
   Disallow: /tim-kiem-
   Disallow: /sportapi
   Sitemap: https://vietnamnet.vn/sitemap.xml
   ```
   - Không có `Disallow` nào chạm tới `/rss/` hoặc `*.rss`; không có `Crawl-delay`.
2. **Kiểm tra trang điều khoản RSS và Footer:**
   - Đường dẫn trang danh mục/điều khoản RSS cũ `https://vietnamnet.vn/rss` (và `https://vietnamnet.vn/rss.html`) hiện trả về **HTTP 404 Not Found** — VietNamNet đã gỡ trang quy định sử dụng RSS riêng.
   - Footer trên trang chủ `https://vietnamnet.vn/` chỉ có câu bản quyền chung (trích nguyên văn 21 chữ):
     > *"Chỉ được phát hành lại thông tin từ website này khi có sự đồng ý bằng văn bản của báo VietNamNet."* — URL: `https://vietnamnet.vn/`
   - Không có câu cấm bot/truy cập tự động và không có chữ "phi lợi nhuận".
3. **Kiểm tra trạng thái kỹ thuật của các feed RSS VietNamNet:**
   - **`vietnamnet_kinh_doanh` (`https://vietnamnet.vn/rss/kinh-doanh.rss` -> redirect 301 về `https://vietnamnet.vn/kinh-doanh.rss`):** HTTP 200 OK, đang cập nhật sống ngày 02/11/2026, nhưng mỗi lần gọi trả về tới **1.000 items (~650 KB XML)**.
   - **`vietnamnet_cong_nghe` (`https://vietnamnet.vn/rss/cong-nghe.rss` -> redirect 301 về `https://vietnamnet.vn/cong-nghe.rss`):** Tuy trả HTTP 200 OK (36 items) nhưng **đã ngừng cập nhật từ ngày 10/03/2025** (`Mon, 10 Mar 2025 17:19:01 +0700`) do VietNamNet tách mục Công nghệ. Qua kiểm tra các đường dẫn con trên VietNamNet, hai feed công nghệ đang sống thực tế năm 2026 là:
     - `https://vietnamnet.vn/rss/an-ninh-mang.rss` (HTTP 200 OK, **1.000 items**, bài mới nhất `02/11/2026 14:33 +0700`).
     - `https://vietnamnet.vn/rss/ha-tang-so.rss` (HTTP 200 OK, **1.000 items**, bài mới nhất `01/11/2026 11:01 +0700`).
     - (Trong khi đó `/rss/vien-thong.rss` và `/rss/ung-dung.rss` bị lỗi cú pháp XML `mismatched tag: line 18`).
4. **Kết luận đề xuất cho VietNamNet:** Giữ **`pending`** (`tos_status: "pending"`, `trial_status: "pending"`).
   - **Lý do:** Dù `robots.txt` mở (`Allow: /`) và không có câu cấm bot hay "phi lợi nhuận", việc VietNamNet đã gỡ trang điều khoản RSS riêng (`/rss` trả 404) cộng với đặc thù mỗi feed trả 1.000 items/request cần chủ dự án xác nhận trước khi bật. Trong [GH-31-sources-v2.json](<thư mục làm việc>/Youtube_Creator_V2/docs/pm/tickets/GH-31-sources-v2.json), đã cập nhật `url` của `vietnamnet_cong_nghe` sang `https://vietnamnet.vn/rss/an-ninh-mang.rss` (thay cho `/rss/cong-nghe.rss` bị đóng băng từ 03/2025) để sẵn sàng nếu chủ dự án quyết định mở `trial_ok`.

---

## 3. Kiểm tra nguồn quốc tế & Quy tắc lọc "Tác động Việt Nam" (`Task 3`)

### 3.1. Bảng kết quả kiểm tra 14 tổ chức / nguồn tin quốc tế (15 mục trong `GH-31-sources-v2.json`)

| ID nguồn (`GH-31-sources-v2.json`) | Tên nguồn & URL Feed / API | `owner_group` | Kênh | Kết quả kiểm tra `robots.txt` & Kỹ thuật (HTTP/WAF) | Trích nguyên văn ToS / License (≤ 25 chữ) & URL | Kết luận (`tos_status`) |
|---|---|---|---|---|---|---|
| `reuters_news` | **Reuters**<br>`https://www.reuters.com/arc/outboundfeeds/news-sitemap-index/?outputType=xml` | `Thomson Reuters` | MIM, CK | Đã ngưng public RSS từ 2020. `robots.txt` chặn mọi bot ngoài whitelist: `# Block all other bots` / `User-agent: *` / `Disallow: /` | *"Collection of content, data and/or information from reuters.com through automated means is prohibited unless you have prior written consent from Reuters."*<br>`https://www.reuters.com/robots.txt` | **`blocked`** |
| `ap_news` | **Associated Press (AP)**<br>`https://apnews.com/ap-sitemap.xml` | `Associated Press` | MIM, CK | Đã ngưng public RSS. `robots.txt` đặt `User-Agent: *` / `Disallow: /*.rss` / `Disallow: /api/v2/feed/` | *"You will not, and will not attempt to, use any robot, spider, scraper, artificial intelligence, or other automated means..."*<br>`https://apnews.com/termsofservice` | **`blocked`** |
| `bbc_technology_rss`<br>`bbc_business_rss` | **BBC News (Tech & Business)**<br>`https://feeds.bbci.co.uk/news/technology/rss.xml` (21 items)<br>`https://feeds.bbci.co.uk/news/business/rss.xml` (47 items) | `BBC` | MIM (`tech`),<br>CK (`biz`) | Feed sống 200 OK. Tuy nhiên header của `https://www.bbc.co.uk/robots.txt` ghi rõ cấm scraping và cấm dùng cho mục đích kinh doanh không xin phép | *"No scraping, crawling, or systematic extraction of content... No business use without permission."*<br>`https://www.bbc.co.uk/robots.txt` & `https://www.bbc.co.uk/usingthebbc/terms/` | **`blocked`** |
| `theverge_rss` | **The Verge**<br>`https://www.theverge.com/rss/index.xml` (10 items) | `Vox Media` | MIM | Feed sống 200 OK. `https://www.theverge.com/robots.txt` chặn `User-agent: python-requests` (`Disallow: /`) và chặn hàng loạt bot thu thập | *"The Services are for your personal and noncommercial use only... You may not use any robot, spider, scraper, or other automated means..."*<br>`https://www.voxmedia.com/terms-of-use/` | **`blocked`** |
| `arstechnica_rss` | **Ars Technica**<br>`https://feeds.arstechnica.com/arstechnica/index` (20 items) | `Condé Nast` | MIM | Feed trên `feeds.arstechnica.com` trả 200 OK (20 items), nhưng `https://arstechnica.com/robots.txt` bật AWS WAF CAPTCHA trả **HTTP 405** với script tự động | *"The Service is for your personal and non-commercial use only... You may not use any robot, spider, scripts, service, software or any manual or automatic device..."*<br>`https://www.condenast.com/user-agreement` | **`blocked`** |
| `techcrunch_rss` | **TechCrunch**<br>`https://techcrunch.com/feed/` (20 items) | `TechCrunch` | MIM | Feed sống 200 OK. `https://techcrunch.com/robots.txt` không chặn `/feed/` với `User-agent: *` (chỉ chặn AI bots) | *"The Services are provided solely for your personal noncommercial use. You may not use the Services... in a manner that... has not been authorized."*<br>`https://techcrunch.com/terms-of-service/` | **`blocked`** |
| `coindesk_rss` | **CoinDesk**<br>`https://www.coindesk.com/arc/outboundfeeds/rss/` (25 items) | `CoinDesk (Bullish)` | MIM, CK | Feed sống 200 OK. `https://www.coindesk.com/robots.txt` mở `User-agent: * / Allow:` (chặn AI bots trừ `/price/`). Trang `/terms` bật Vercel Security Checkpoint (HTTP 429) | Điều khoản sử dụng giới hạn nội dung cho mục đích cá nhân phi thương mại (*personal, non-commercial use*) và cấm khai thác tự động thương mại.<br>`https://www.coindesk.com/terms` | **`blocked`** |
| `worldbank_vn_news` | **World Bank**<br>`https://search.worldbank.org/api/v2/news?format=json&rows=20&qterm=Vietnam` | `World Bank Group` | CK | `https://www.worldbank.org/robots.txt` mở hoàn toàn (`User-agent: * / Allow: /`, không `Crawl-delay`). Không có RSS XML, chỉ có JSON Search API | Dữ liệu mở theo CC BY 4.0, nhưng ToS website (25/07/2025) ghi: *"The content available on this platform is provided for informational and non-commercial purposes only, unless otherwise stated."*<br>`https://www.worldbank.org/ext/en/legal/terms-conditions` | **`pending`** |
| `imf_news_rss` | **IMF**<br>`https://www.imf.org/en/News/RSS` | `IMF` | CK | Cả `https://www.imf.org/robots.txt` và `/en/News/RSS` đều bị **Akamai EdgeSuite WAF chặn HTTP 403 Access Denied** với `urllib`/`curl` | *"Content on this site is provided for personal, non-commercial use only... may not be used for any commercial purpose without prior written permission."*<br>`https://www.imf.org/external/terms.htm` | **`blocked`** |
| `adb_news_rss` | **Asian Development Bank (ADB)**<br>`https://www.adb.org/rss` | `Asian Development Bank (ADB)` | CK | Cả `https://www.adb.org/robots.txt` và `/rss` đều bật **Cloudflare Challenge trả HTTP 403 Forbidden** với `urllib`/`curl` | Giấy phép mở rất thuận lợi: *"Materials... are licensed under the Creative Commons Attribution 3.0 IGO license (CC BY 3.0 IGO)."* (cho phép thương mại khi ghi nguồn)<br>`https://www.adb.org/terms-use` | **`pending`**<br>*(Pháp lý `ok` theo CC BY 3.0 IGO, nhưng kỹ thuật bị Cloudflare 403)* |
| `theregister_security_atom` | **The Register**<br>`https://www.theregister.com/security/headlines.atom` (50 items) | `Situation Publishing` | MIM | Feed sống 200 OK (50 items), nhưng `https://www.theregister.com/robots.txt` áp dụng **Default-Deny**: `User-agent: *` / `Allow: /ads.txt` / `Disallow: /` | *"POLICY: Default-deny. Any crawler not explicitly allowed below is BLOCKED... Anything else, including unknown bots .. BLOCKED by default."*<br>`https://www.theregister.com/robots.txt` | **`blocked`** |
| `krebsonsecurity_rss` | **Krebs on Security**<br>`https://krebsonsecurity.com/feed/` (10 items) | `Krebs on Security` | MIM | Feed sống 200 OK (10 items; đăng thưa ~2–4 bài/tháng). `robots.txt` cho phép `/feed/`: `User-agent: *` / `Crawl-Delay: 35` / `Disallow: /wp-admin/` | Chỉ ghi bản quyền chuẩn *"© Krebs on Security"* ở footer; không cấm đọc RSS khi tuân thủ `Crawl-Delay: 35`, chưa có giấy phép thương mại tường minh.<br>`https://krebsonsecurity.com/robots.txt` | **`pending`**<br>*(Có thể mở `trial_ok` với `Crawl-Delay >= 35s`, `<= 1 req/6h`)* |
| `bleepingcomputer_rss` | **BleepingComputer**<br>`https://www.bleepingcomputer.com/feed/` | `BleepingComputer` | MIM | Cả `https://www.bleepingcomputer.com/robots.txt` và `/feed/` đều bật **Cloudflare Challenge trả HTTP 403 Forbidden** với `urllib`/`curl` | Cấm truy cập tự động (automated bots/scrapers) và giới hạn sử dụng cá nhân phi thương mại.<br>`https://www.bleepingcomputer.com/terms-of-use/` | **`blocked`** |
| `cisa_advisories_rss` | **U.S. CISA Advisories**<br>`https://www.cisa.gov/cybersecurity-advisories/all.xml` | `US DHS (CISA)` | MIM | Máy chủ `www.cisa.gov` đứng sau **Akamai EdgeSuite WAF trả HTTP 403 Access Denied** cho cả `/robots.txt` và `/cybersecurity-advisories/all.xml` khi gọi từ `urllib`/`curl` | Thuộc **Public Domain** chính phủ liên bang Mỹ (`17 U.S.C. § 105`): *"Information presented on this website is considered public information and may be distributed or copied."*<br>`https://www.cisa.gov/privacy-policy` | **`pending`** trên `cisa.gov` do Akamai 403<br>*(Gợi ý: mirror chính thức của CISA trên GitHub `cisagov/kev-data` hoàn toàn `ok` 200 OK)* |

> **Nhận xét tổng quan về nguồn quốc tế:**
> - Các hãng thông tấn và báo công nghệ thương mại Anh/Mỹ (`Reuters`, `AP`, `BBC`, `The Verge`, `Ars Technica`, `TechCrunch`, `CoinDesk`, `The Register`, `BleepingComputer`) hiện đều đã khóa chặt bằng một hoặc cả hai lớp: **(1)** `robots.txt` đặt `Disallow: /` hoặc chặn `python-requests`/crawlers, và **(2)** ToS ghi tường minh *"solely for your personal noncommercial use"* + *"prohibit any robot, spider, scraper, or other automated means"*. Vì vậy, để bắt tín hiệu từ các báo này một cách hợp lệ mà không cào trực tiếp trang của họ, hệ thống nên tiếp tục đi qua **GDELT Doc 2.0 API (`gdelt_doc_api`)** và **Hacker News Algolia API (`hackernews_algolia`)** vốn đã có `tos_status = "ok"` trong `sources.json`.
> - Với nhóm tổ chức quốc tế & cơ quan chính phủ (`World Bank`, `ADB`, `CISA`), điều khoản dữ liệu rất mở (`Public Domain` hoặc `CC BY`), nhưng `cisa.gov` và `adb.org` chặn bot ở tầng CDN (Akamai/Cloudflare HTTP 403). Riêng CISA có thể lấy trực tiếp qua repo GitHub chính thức của cơ quan này (`https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json` — Public Domain, HTTP 200 OK) nếu bổ sung parser JSON tương ứng.

### 3.2. Đề xuất quy tắc lọc "Tác động Việt Nam" (`vn_impact_filter`) cho nguồn quốc tế

Để tránh làm loãng bảng xếp hạng bằng tin nội bộ của Mỹ/Châu Âu (như bầu cử giữa kỳ bang Ohio hay đình công hãng bay Ryanair), mọi item tiếng Anh từ nguồn quốc tế (bao gồm cả GDELT, Hacker News, Reddit, CISA, Krebs, World Bank/ADB) chỉ được giữ lại đưa vào cụm sự kiện của **MIM** hoặc **CK** nếu thỏa mãn **ít nhất 1 trong 2 tầng lọc** sau:

#### Tầng A — Khớp trực tiếp thực thể / địa danh Việt Nam (áp dụng cho cả MIM & CK)
Tiêu đề hoặc tóm tắt khớp từ khóa (không phân biệt hoa thường, có ranh giới từ `\b`):
- **Địa danh & Quốc gia:** `Vietnam`, `Viet Nam`, `Vietnamese`, `Hanoi`, `Ha Noi`, `Ho Chi Minh`, `Saigon`, `Da Nang`, `Hai Phong`, `Mekong`, `ASEAN`, `Southeast Asia`.
- **Tổ chức / Doanh nghiệp / Chỉ số VN:** `SBV` (`State Bank of Vietnam`), `VN-Index`, `HoSE`, `VND`, `Viettel`, `FPT`, `VNG`, `VinFast`, `Vingroup`, `VNPT`, `CMC`, `VNeID`, `Sky Mavis`.

#### Tầng B — Sự kiện toàn cầu ảnh hưởng trực tiếp đến người dùng / nhà đầu tư Việt Nam
Nếu không nhắc tên Việt Nam trực tiếp, bài quốc tế phải khớp **cặp điều kiện (Thực thể toàn cầu phổ biến tại VN + Từ khóa sự kiện trọng yếu)**:

1. **Cho kênh MIM (Công nghệ / AI / An ninh mạng):**
   - **Nhóm B1 — Lỗ hổng zero-day & sự cố an ninh mạng diện rộng:**
     - *Thực thể:* `Windows`, `iOS`, `iPhone`, `Android`, `Chrome`, `Safari`, `Edge`, `macOS`, `Linux`, `PHP`, `WordPress`, `Cloudflare`, `Telegram`, `Zalo`, `Messenger`, `Facebook`, `YouTube`, `TikTok`, `Gmail`, `GitHub`, `Docker`, `OpenSSL`, `Binance`, `MetaMask`, `Trust Wallet`, `Trezor`, `Ledger`.
     - *Từ khóa sự kiện:* `CVE-2026-`, `zero-day`, `0-day`, `actively exploited`, `emergency patch`, `critical vulnerability`, `remote code execution`, `RCE`, `data breach`, `hacked`, `drained`, `outage`, `down worldwide`, `ransomware`, `backdoor`, `supply chain attack`, `phishing`.
   - **Nhóm B2 — Bước ngoặt mô hình AI & phần cứng tiêu dùng cốt lõi:**
     - *Thực thể:* `OpenAI`, `ChatGPT`, `GPT-5`, `GPT-6`, `Anthropic`, `Claude`, `Google`, `Gemini`, `DeepSeek`, `Meta`, `Llama`, `Microsoft`, `Copilot`, `Apple`, `Nvidia`, `TSMC`, `Intel`, `AMD`, `Samsung`.
     - *Từ khóa sự kiện:* `launch`, `release`, `open-source`, `open weights`, `pricing`, `free tier`, `ban`, `export control`, `chip shortage`, `RAM`, `GPU`, `AI agent`, `jailbreak`, `copyright lawsuit`, `training data`.

2. **Cho kênh CK (Tài chính cá nhân / Vĩ mô):**
   - **Nhóm B3 — Chính sách tiền tệ, giá hàng hóa & cú sốc thị trường toàn cầu:**
     - *Thực thể:* `Federal Reserve`, `Fed`, `FOMC`, `Powell`, `U.S. Treasury`, `DXY`, `US Dollar`, `Gold`, `XAU`, `Silver`, `Brent`, `WTI`, `Crude Oil`, `OPEC`, `World Bank`, `IMF`, `ADB`, `tariffs`, `supply chain`, `Bitcoin ETF`, `S&P 500`, `Nasdaq`.
     - *Từ khóa sự kiện:* `rate cut`, `rate hike`, `interest rate`, `inflation`, `CPI`, `recession`, `all-time high`, `record high`, `crash`, `sell-off`, `plunge`, `surge`, `tariff`, `trade war`, `anti-dumping`, `sanctions`, `outflows`, `bank run`, `liquidity crisis`.
   - **Quy tắc loại trừ (Negative Filter cho CK):** Loại bỏ các bài chỉ nói về chính trị/bầu cử địa phương Mỹ (`midterm`, `governor`, `senate race`, `ballot`), dịch vụ tiêu dùng nội địa Anh/Mỹ (`NHS`, `401k`, `Roth IRA`, `Medicare`, `Council Tax`, `Ryanair`), hoặc kết quả kinh doanh của doanh nghiệp bán lẻ nội địa nước ngoài.

---

## 4. Benchmark độc lập các sự kiện nóng 72 giờ qua (`31/10–02/11/2026`) (`Task 4`)

### 4.1. Phương pháp thực hiện & Cam kết độc lập
- **Cam kết độc lập:** Toàn bộ quá trình làm benchmark **tuyệt đối không đọc** `output/trend/`, `data/trend/` hay các báo cáo `GH-31-fix*-report.md`.
- **Khung thời gian:** 72 giờ tính từ `2026-10-31T00:00:00+07:00` đến `2026-11-02T19:00:00+07:00`.
- **Cách thu thập (thực hiện lúc 18:35–19:05 ngày 02/11/2026):**
  - Mở trực tiếp và đối chiếu 28 nguồn RSS/Atom/JSON của **13 `owner_group` độc lập**:
    1. **VnExpress (`VnExpress (FPT)`):** `/rss/so-hoa.rss` (35 bài trong 72h), `/rss/kinh-doanh.rss` (44 bài), `/rss/thoi-su.rss` (51 bài), `/rss/phap-luat.rss` (33 bài).
    2. **Thanh Niên (`Thanh Niên`):** `/rss/cong-nghe.rss` (23 bài trong 72h), `/rss/kinh-te.rss` (50 bài), `/rss/thoi-su.rss` (50 bài).
    3. **Tuổi Trẻ (`Tuổi Trẻ`):** `/rss/cong-nghe.rss` & `/rss/nhip-song-so.rss`, `/rss/kinh-doanh.rss` (15 bài), `/rss/phap-luat.rss` (50 bài).
    4. **Dân Trí (`Dân Trí`):** `/rss/cong-nghe.rss` (12 bài), `/rss/kinh-doanh.rss` (50 bài). *(Lưu ý: feed cũ `/rss/suc-manh-so.rss` đã ngừng cập nhật từ 02/2025, Dân Trí đã chuyển sang `/rss/cong-nghe.rss`).*
    5. **VietNamNet (`VietNamNet`):** `/rss/kinh-doanh.rss` (42 bài trong 72h), `/rss/thi-truong.rss`, `/rss/an-ninh-mang.rss`, `/rss/ha-tang-so.rss`, `/rss/thoi-su.rss` (170 bài).
    6. **VnEconomy (`VnEconomy`):** `/kinh-te-so.rss` (11 bài), `/tai-chinh.rss` (17 bài), `/chung-khoan.rss` (23 bài).
    7. **GenK & CafeF (`VCCorp`):** `genk.vn/rss/tin-ict.rss` (9 bài), `genk.vn/rss/ai.rss` (8 bài), `genk.vn/rss/home.rss` (50 bài), `cafef.vn/tai-chinh-ngan-hang.rss` (38 bài), `cafef.vn/vi-mo-dau-tu.rss` (50 bài), `cafef.vn/thi-truong-chung-khoan.rss` (50 bài).
    8. **Google Trends Việt Nam (`Google`):** `https://trends.google.com/trending/rss?geo=VN` (ghi nhận các từ khóa đang lên đỉnh ngày 02/11: `cổ phiếu fpt`, `tổng giám đốc sacombank`, `lỗ hổng`, `doanh thu`).
    9. **Nguồn quốc tế đối chiếu chéo (`BBC`, `Vox Media`, `TechCrunch`, `CoinDesk (Bullish)`, `Situation Publishing`):** `feeds.bbci.co.uk/news/technology/rss.xml`, `feeds.bbci.co.uk/news/business/rss.xml`, `theverge.com/rss/index.xml`, `techcrunch.com/feed/`, `coindesk.com/arc/outboundfeeds/rss/`, `theregister.com/headlines.atom`, `theregister.com/security/headlines.atom`.

### 4.2. Thống kê số lượng sự kiện & Phân bố độ nóng (`hotness`)

Chi tiết đầy đủ nằm trong [GH-31-benchmark.json](<thư mục làm việc>/Youtube_Creator_V2/docs/pm/tickets/GH-31-benchmark.json):

| Kênh | Tổng số sự kiện (yêu cầu ≥ 15) | Số sự kiện `high` | Số sự kiện `medium` | Số URL trung bình / sự kiện | Số `owner_group` độc lập trung bình / sự kiện |
|---|---|---|---|---|---|
| **MIM** (AI / Công nghệ / An ninh mạng) | **18 sự kiện** (`mim_01` → `mim_18`) | **9** (50,0%) | **9** (50,0%) | 3,61 URL | 3,11 `owner_group` |
| **CK** (Tài chính cá nhân / Vĩ mô) | **20 sự kiện** (`ck_01` → `ck_20`) | **13** (65,0%) | **7** (35,0%) | 3,65 URL | 3,45 `owner_group` |
| **Tổng cộng** | **38 sự kiện** | **22** (57,9%) | **16** (42,1%) | **3,63 URL** | **3,29 `owner_group`** |

- **5 cặp sự kiện giao thoa giữa MIM và CK** (được ghi ở cả hai kênh với `angle` riêng biệt đúng luật từng kênh):
  1. `mim_01` ↔ `ck_19`: Vụ hack kỷ lục 6,3 tỷ USD trên sàn Binance và làn sóng rút ròng 3,6–6 tỷ USD khi mở lại cổng rút tiền.
  2. `mim_09` ↔ `ck_20`: Đợt bán tháo cổ phiếu công nghệ Mỹ (Alphabet mất 500 tỷ USD) vì nỗi lo chi tiêu hạ tầng AI, kéo theo hiện tượng bán vàng bù lỗ ký quỹ và tác động tâm lý tới nhóm công nghệ Việt Nam.
  3. `mim_02` (chính sách cấm nhập khẩu điện thoại/máy tính cũ từ 01/01/2027) & `mim_16` (triệt phá đường dây buôn lậu hàng nghìn điện thoại cũ trị giá gần 20 tỷ đồng).
  4. `mim_08` ↔ `ck_09`/`ck_18`: Rủi ro an ninh mạng AI và gian lận/kiểm soát nội bộ trong hệ thống ngân hàng.
  5. `mim_18` ↔ `ck_15`: Rủi ro khóa tài khoản ngân hàng khi giao dịch P2P/OTC và đại án sàn ngoại hối trái phép Mr Pips (5.300 tỷ đồng).

### 4.3. Danh mục tóm tắt 18 sự kiện kênh MIM trong `GH-31-benchmark.json`

| ID | Độ nóng | Tóm tắt sự kiện (`label`) | Số `owner_group` | Danh sách `owner_group` xác nhận |
|---|---|---|---|---|
| `mim_01` | `high` | Sàn tiền mã hóa Binance bị tấn công mạng đánh cắp kỷ lục 6,3 tỷ USD trong 20 phút, FBI cáo buộc nhóm hacker Triều Tiên đứng sau | 8 | `VnExpress (FPT)`, `VietNamNet`, `VnEconomy`, `BBC`, `CoinDesk (Bullish)`, `TechCrunch`, `Vox Media`, `Situation Publishing` |
| `mim_02` | `high` | Chính thức từ ngày 01/01/2027, Việt Nam cấm nhập khẩu điện thoại, máy tính, máy ảnh và thiết bị công nghệ đã qua sử dụng | 3 | `Dân Trí`, `Tuổi Trẻ`, `VCCorp` |
| `mim_03` | `high` | CEO OpenAI Sam Altman gây bão khi cho rằng RAM trong máy tính cá nhân bị lãng phí, Elon Musk và Jensen Huang lên tiếng phản bác | 3 | `VCCorp`, `VnExpress (FPT)`, `Thanh Niên` |
| `mim_04` | `high` | iPhone Duo xuất hiện lỗi khe hở ở bản lề và thân máy ngay sau khi mở bán, dấy lên tranh cãi về độ bền điện thoại gập của Apple | 5 | `VnExpress (FPT)`, `Thanh Niên`, `Dân Trí`, `VCCorp`, `TechCrunch` |
| `mim_05` | `high` | Vệ tinh tích hợp AI của Google gửi phản hồi đầu tiên là một bài thơ haiku từ quỹ đạo vũ trụ về Trái Đất | 3 | `Situation Publishing`, `Thanh Niên`, `VnExpress (FPT)` |
| `mim_06` | `high` | Elon Musk cảnh báo tác nhân AI (AI Agents) sẽ tự hack hệ thống để kiếm tiền; thử nghiệm mới phát hiện AI tự vượt hạn mức chi tiêu crypto | 4 | `Tuổi Trẻ`, `VnExpress (FPT)`, `CoinDesk (Bullish)`, `VCCorp` |
| `mim_07` | `high` | Cảnh báo lỗ hổng bảo mật 'tin nhắn tử thần' đe dọa hàng triệu thiết bị Android gây lỗi hệ thống nghiêm trọng | 2 (+ Google Trends) | `Thanh Niên`, `Dân Trí` |
| `mim_08` | `medium` | Các ngân hàng và doanh nghiệp trước làn sóng tấn công mạng bằng AI tự động hóa khai thác lỗ hổng sau 'tháng 10 đen tối' | 3 | `VnExpress (FPT)`, `VCCorp`, `VnEconomy` |
| `mim_09` | `high` | Làn sóng bán tháo cổ phiếu công nghệ Mỹ thổi bay 500 tỷ USD của Alphabet và kéo Intel lao dốc vì nỗi sợ bong bóng hạ tầng AI | 4 | `VCCorp`, `BBC`, `Dân Trí`, `VnEconomy` |
| `mim_10` | `medium` | Apple tung bản cập nhật bảo mật khẩn cấp cho 3 mẫu iPhone cũ và cách thu hồi 15 GB bộ nhớ lưu trữ sau khi nâng cấp iOS 27 | 2 | `Thanh Niên`, `VCCorp` |
| `mim_11` | `medium` | Anthropic đổi tên gói Claude Max 20x thành Ultra (bỏ giới hạn 5 giờ) và ngừng kiểm tra viết code truyền thống khi tuyển dụng kỹ sư | 2 | `VCCorp`, `VnExpress (FPT)` |
| `mim_12` | `medium` | Phát động cuộc thi AI theo chuẩn quốc tế miễn phí cho học sinh THPT toàn quốc với giải nhất 100 triệu đồng | 3 | `Dân Trí`, `VnExpress (FPT)`, `VCCorp` |
| `mim_13` | `medium` | Tranh cãi việc Apple trang bị màn hình cảm ứng cho MacBook Pro OLED, đi ngược tuyên bố nổi tiếng của cố CEO Steve Jobs | 2 | `Dân Trí`, `VnExpress (FPT)` |
| `mim_14` | `high` | Cơ quan Công an phát thông báo quan trọng về định danh điện tử VNeID của cá nhân, doanh nghiệp và đăng ký VNeID cho trẻ dưới 14 tuổi | 2 | `Dân Trí`, `VCCorp` |
| `mim_15` | `medium` | Bão code AI buộc GitHub phải bổ sung 4 triệu nhân CPU, trong khi các trung tâm dữ liệu AI của OpenAI và xAI bị phản đối vì điện năng và ô nhiễm | 3 | `VnExpress (FPT)`, `TechCrunch`, `Vox Media` |
| `mim_16` | `medium` | Khởi tố đường dây nhập lậu hàng nghìn điện thoại cũ từ Trung Quốc trị giá gần 20 tỷ đồng tiêu thụ qua mạng xã hội | 3 | `Thanh Niên`, `VietNamNet`, `Tuổi Trẻ` |
| `mim_17` | `medium` | Startup AI Việt Nam thắng giải khởi nghiệp quốc tế tại Hàn Quốc và làn sóng ứng dụng AI/chuyển đổi số thực chất vào logistics địa phương | 2 | `VnExpress (FPT)`, `VnEconomy` |
| `mim_18` | `medium` | Cảnh báo rủi ro bị khóa tài khoản ngân hàng khi giao dịch tiền mã hóa P2P và chợ đen OTC do dính dòng tiền lừa đảo | 2 | `Thanh Niên`, `VnExpress (FPT)` |

### 4.4. Danh mục tóm tắt 20 sự kiện kênh CK trong `GH-31-benchmark.json`

*(Tất cả trường `angle` của CK trong JSON đã được kiểm tra tự động đảm bảo **không nêu tên ngân hàng thương mại, công ty chứng khoán, hãng xe hay mã cổ phiếu** và không khuyến nghị mua/bán).*

| ID | Độ nóng | Tóm tắt sự kiện (`label`) | Số `owner_group` | Danh sách `owner_group` xác nhận |
|---|---|---|---|---|
| `ck_01` | `high` | Chính thức giảm 2% giá bán lẻ điện bình quân (giảm hơn 44 đồng/kWh về mức 2.159 đồng/kWh) từ ngày 01/11/2026 | 4 | `VnExpress (FPT)`, `VietNamNet`, `Thanh Niên`, `Dân Trí` |
| `ck_02` | `high` | Chính phủ hạ thuế tiêu thụ đặc biệt với xăng về 0% từ 01/11/2026 đến hết 31/03/2027, kéo giá xăng bán lẻ giảm sâu tới 1.804 đồng/lít | 5 | `VnExpress (FPT)`, `VietNamNet`, `VnEconomy`, `Thanh Niên`, `Dân Trí` |
| `ck_03` | `high` | Giá vàng SJC biến động dữ dội: lao dốc khiến người mua lỗ 11–12 triệu/lượng sau 2 tuần, sáng 02/11 đảo chiều tăng lên 140 triệu/lượng (cao hơn thế giới 14,3 triệu) | 6 | `VnEconomy`, `Thanh Niên`, `VnExpress (FPT)`, `VietNamNet`, `VCCorp`, `Dân Trí` |
| `ck_04` | `high` | Chứng khoán Việt Nam (VN-Index) giảm hơn 30 điểm phiên đầu tuần 02/11 về quanh 1.710 điểm, thanh khoản tăng đột biến do áp lực bán tháo diện rộng | 5 | `Tuổi Trẻ`, `Dân Trí`, `Thanh Niên`, `VnExpress (FPT)`, `VnEconomy` |
| `ck_05` | `high` | Khối ngoại bán ròng 20 phiên liên tiếp, rút gần 1 tỷ USD khỏi thị trường chứng khoán Việt Nam trong tháng 10/2026 | 3 | `VnEconomy`, `VnExpress (FPT)`, `VCCorp` |
| `ck_06` | `high` | Cá nhân, hộ kinh doanh và doanh nghiệp có doanh thu không quá 10 tỷ đồng/năm được giảm 30% thuế thu nhập theo từng kỳ | 3 | `VietNamNet`, `VnEconomy`, `VCCorp` |
| `ck_07` | `medium` | Bộ Tài chính công bố hơn 2,5 triệu doanh nghiệp và người nộp thuế ngừng hoạt động nhưng chưa hoàn tất thủ tục đóng mã số thuế | 2 | `VnExpress (FPT)`, `Dân Trí` |
| `ck_08` | `high` | Lãi suất tiết kiệm đầu tháng 11/2026 giảm tới 0,5 điểm phần trăm ở nhiều kỳ hạn nhưng tiền gửi vẫn chảy mạnh vào hệ thống ngân hàng | 4 | `VnExpress (FPT)`, `VCCorp`, `Thanh Niên`, `VietNamNet` |
| `ck_09` | `high` | 27 ngân hàng Việt báo lãi trước thuế 9 tháng hơn 311.000 tỷ đồng nhưng nhóm cổ phiếu ngân hàng vẫn giảm sâu vì áp lực nợ xấu và dự phòng trái phiếu | 3 | `VCCorp`, `Dân Trí`, `Thanh Niên` |
| `ck_10` | `high` | Biến động nhân sự cấp cao tại một ngân hàng thương mại cổ phần lớn khi bổ nhiệm Quyền Tổng giám đốc mới sau chưa đầy 4 tháng | 5 (+ Google Trends) | `Thanh Niên`, `VCCorp`, `VietNamNet`, `VnExpress (FPT)`, `VnEconomy` |
| `ck_11` | `medium` | Các doanh nghiệp lọc hóa dầu và đầu mối xăng dầu lớn gửi ngân hàng hơn 58.000 tỷ đồng (~2 tỷ USD), báo lãi đột biến gần 25.000 tỷ đồng | 3 | `VnExpress (FPT)`, `Dân Trí`, `VietNamNet` |
| `ck_12` | `high` | Doanh nghiệp sản xuất 'Anh trai Say Hi' (DatVietVAC) chính thức lên sàn HoSE với vốn hóa hơn 6.100 tỷ đồng, chia cổ tức tiền mặt 25% | 5 | `VCCorp`, `Tuổi Trẻ`, `Dân Trí`, `Thanh Niên`, `VnExpress (FPT)` |
| `ck_13` | `medium` | Giá bạc trong nước biến động dữ dội, từng 'bốc hơi' gần 80 triệu đồng/kg từ đỉnh khiến nhiều người mua đuổi lỗ nặng | 2 | `VietNamNet`, `VCCorp` |
| `ck_14` | `medium` | Tỷ giá USD/VND tại ngân hàng lùi xuống dưới mốc 26.000 đồng/USD, đưa VND vào nhóm 3 đồng tiền châu Á tăng giá mạnh nhất so với USD | 2 | `Thanh Niên`, `VnEconomy` |
| `ck_15` | `high` | Xét xử đường dây lừa đảo đầu tư ngoại hối Mr Pips (Phó Đức Nam) thu giữ 5.300 tỷ đồng: bị cáo khai '99% nhà đầu tư trên sàn mất tiền vì thiếu kiến thức' | 4 | `VnExpress (FPT)`, `Tuổi Trẻ`, `Thanh Niên`, `VietNamNet` |
| `ck_16` | `high` | Xét xử đại án xăng dầu: chủ doanh nghiệp đầu mối hầu tòa vì tham ô 79 tỷ đồng Quỹ bình ổn giá, cựu kế toán biển thủ 94 tỷ đồng nướng vào cờ bạc online | 4 | `Tuổi Trẻ`, `VnExpress (FPT)`, `VietNamNet`, `Thanh Niên` |
| `ck_17` | `medium` | Người dân bất ngờ nhận thông báo nợ thuế đất phi nông nghiệp hàng chục triệu đồng hoặc bị kê khai khống thu nhập chịu thuế TNCN | 2 | `Thanh Niên`, `VCCorp` |
| `ck_18` | `medium` | Khởi tố vụ nữ nhân viên ngân hàng tự ý chuyển quyền sở hữu sổ tiết kiệm của 5 khách hàng, chiếm đoạt hơn 31,7 tỷ đồng | 2 | `Thanh Niên`, `VietNamNet` |
| `ck_19` | `high` | Nhà đầu tư ồ ạt rút 3,6–6 tỷ USD khỏi sàn Binance ngay khi mở lại cổng rút tiền sau vụ hack 6,3 tỷ USD, quỹ ETF Bitcoin bị rút ròng 643 triệu USD | 5 | `VnEconomy`, `VnExpress (FPT)`, `VietNamNet`, `CoinDesk (Bullish)`, `BBC` |
| `ck_20` | `high` | Cú sập của nhóm cổ phiếu công nghệ Mỹ buộc nhiều quỹ đầu tư bán vàng bù lỗ ký quỹ và tạo áp lực tâm lý lên thị trường mới nổi | 3 | `VnEconomy`, `Dân Trí`, `BBC` |
