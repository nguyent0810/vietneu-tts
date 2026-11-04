# Báo cáo GH-31 (Grok) · Rà điều khoản và lập danh sách nguồn cho Trend Engine P0

- **Ticket:** `docs/pm/tickets/GH-31-grok.md` (Issue #31)
- **Thiết kế tham chiếu:** `docs/pm/2026-11-02-trend-engine-v1.md` (mục P0), `docs/pm/2026-11-02-audit-trend.md`, `docs/audit/2026-10-05-demand-sources-research.md`
- **File cấu hình đề xuất:** `docs/pm/tickets/GH-31-sources.json` (đã chuẩn hóa đúng schema `factory/trend/sources.py`: `id`, `url`, `kind` ∈ `{"rss", "json_hn", "json_reddit", "wiki_pageviews"}`, `owner_group`, `channels`, `tos_status`, `tos_note`, kèm metadata `lang`, `is_primary`, `rate_limit`, `tos_url`).

---

## 1. Tóm tắt kết luận

1. **Tổng số nguồn đã rà trong `docs/pm/tickets/GH-31-sources.json`: 45 mục nguồn**, chia thành 3 trạng thái theo tiêu chí nghiêm ngặt của brief:
   - **`ok` (13 mục — thuộc 9 `owner_group` độc lập):** Điều khoản công khai thuộc phạm vi công cộng (Public Domain / CC0), giấy phép mở (MIT / CC BY 4.0), hoặc cho phép sử dụng miễn phí cho cả mục đích thương mại khi tuân thủ `robots.txt` và ghi nguồn. **Đủ điều kiện bật ngay trong P0 cho cả MIM và CK.**
   - **`pending` (17 mục — thuộc 12 `owner_group`):** Điều khoản không cấm rõ việc đọc tự động tiêu đề qua RSS làm tín hiệu nội bộ (ví dụ: trang RSS của Thanh Niên, CafeF, GenK, VietNamNet chỉ yêu cầu ghi nguồn khi "sử dụng lại/phát hành lại thông tin", không có cụm "phi lợi nhuận" như VnExpress/Tuổi Trẻ/Dân Trí), hoặc RSS công khai của cơ quan nhà nước VN và các hãng công nghệ (OpenAI, Microsoft, Apple, Hugging Face) nằm chung dưới điều khoản website tổng quát. **Trình chủ kênh quyết định có bật cho tác vụ đọc tiêu đề nội bộ hay không.**
   - **`blocked` (15 mục — thuộc 9 `owner_group`):** Điều khoản ghi rõ chỉ miễn phí cho *"cá nhân và tổ chức phi lợi nhuận"* (VnExpress, Tuổi Trẻ, Dân Trí, VnEconomy, NVIDIA Blog), cấm mục đích thương mại ở tầng miễn phí (Reddit Data API, Vietcombank), hoặc cấm thu thập tự động / chặn qua `robots.txt` (Google News `/rss/search`, Meta). **Không gọi trong `scan.py` khi chưa có văn bản cho phép.**
2. **Không dùng Google Autocomplete (`suggestqueries.google.com`):** Đã loại hoàn toàn theo đúng chỉ đạo.
3. **Bổ sung 6 nguồn miễn phí tốt hơn (5 nguồn `ok`, 1 nguồn `pending`):**
   - **GDELT DOC 2.0 API (`format=rss`, `sourcelang:vie`)** (`ok`): Cho phép dùng thương mại không hạn chế (`unlimited and unrestricted use for any commercial, non-commercial, or research purpose`), trả về RSS 2.0 các tin tiếng Việt mới nhất trong 24h — giải quyết bài toán phát hiện tin tiếng Việt hợp pháp trong P0 mà không vướng điều khoản "phi lợi nhuận" của RSS từng báo.
   - **arXiv `cs.AI` RSS** (`ok`): Metadata phát hành theo **CC0 1.0 Public Domain**, nguồn sơ cấp chuẩn xác cho MIM.
   - **U.S. NIST News & AI RSS** (`ok`): Public Domain chính phủ Mỹ, nguồn sơ cấp về chuẩn AI/an toàn thông tin cho MIM.
   - **U.S. Federal Reserve Monetary Policy RSS** (`ok`) & **U.S. Bureau of Labor Statistics (BLS) Latest RSS** (`ok`): Public Domain (`17 U.S.C. §105`), nguồn sơ cấp vĩ mô (lãi suất Fed, CPI, việc làm) cho CK.
   - **Hugging Face Blog RSS** (`pending`): Nguồn sơ cấp mô hình AI mở cho MIM.

---

## 2. Bảng toàn bộ nguồn đã rà điều khoản

### 2.1. Nhóm `ok` — Đề xuất bật ngay trong P0 (13 mục / 9 `owner_group` độc lập)

| ID | Nguồn | URL feed / API thật | `owner_group` | Kênh | Vai trò | Giới hạn tần suất (`rate_limit`) | Trích điều khoản (≤ 25 từ) & URL ToS |
|---|---|---|---|---|---|---|---|
| `google_trends_vn` | Google Trends Daily RSS VN | `https://trends.google.com/trending/rss?geo=VN` | `Google` | MIM, CK | Tín hiệu | Không công bố trần cứng; feed làm mới ~10 phút/lần, quét 3h/lần | *"Google Trends data can be used in any publication, for free, and without prior permission from Google."* — https://support.google.com/trends/answer/4365538 (`robots.txt` không chặn `/trending/rss`) |
| `hacker_news` | Hacker News Firebase API | `https://hacker-news.firebaseio.com/v0/topstories.json` | `Y Combinator` | MIM | Tín hiệu | *"There is currently no rate limit"* (lấy tuần tự ≤ 30 item/lần) | *"Permission is hereby granted, free of charge, to any person... without restriction... There is currently no rate limit."* (MIT) — https://github.com/HackerNews/API |
| `wikipedia_pageviews_vi` | Wikimedia Pageviews (`vi.wikipedia`) | `https://wikimedia.org/api/rest_v1/metrics/pageviews/top/vi.wikipedia/all-access/{YYYY}/{MM}/{DD}` | `Wikimedia Foundation` | MIM, CK | Tín hiệu | 200 req/phút (bắt buộc `User-Agent` có thông tin liên hệ) | *"All datasets and endpoints available through the Analytics API are available under the Creative Commons CC0 1.0 dedication."* — https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/access-policy.html |
| `wikipedia_pageviews` | Wikimedia Pageviews (`en.wikipedia`) | `https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{YYYY}/{MM}/{DD}` | `Wikimedia Foundation` | MIM, CK | Tín hiệu | 200 req/phút (bắt buộc `User-Agent` có thông tin liên hệ) | *"All datasets and endpoints available through the Analytics API are available under the Creative Commons CC0 1.0 dedication."* — https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/access-policy.html |
| `sec_press_releases` | U.S. SEC Press Releases RSS | `https://www.sec.gov/news/pressreleases.rss` | `US SEC` | MIM, CK | **Sơ cấp** | Tối đa 10 req/giây; bắt buộc `User-Agent` có tên đơn vị + email | *"Current maximum request rate: 10 requests/second... declare your user agent in request headers."* (Public Domain) — https://www.sec.gov/os/webmaster-faq#developers |
| `sec_edgar_current` | U.S. SEC EDGAR Current Filings Atom | `https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&output=atom` | `US SEC` | MIM, CK | **Sơ cấp** | Tối đa 10 req/giây; bắt buộc `User-Agent` có tên đơn vị + email | *"Current maximum request rate: 10 requests/second... declare your user agent in request headers."* (Public Domain) — https://www.sec.gov/os/webmaster-faq#developers |
| `google_blog_rss` | Google Official Blog (`blog.google`) | `https://blog.google/rss/` | `Google` | MIM | **Sơ cấp** | Tuân thủ `robots.txt` (Allow `/rss/`); quét 3h/lần | *"Don't abuse our services... using automated means to access content... in violation of the machine-readable instructions."* — https://policies.google.com/terms |
| `google_devs_blog_rss` | Google Developers Blog (CC BY 4.0) | `https://developers.googleblog.com/feeds/posts/default` | `Google` | MIM | **Sơ cấp** | Không giới hạn cứng; quét 3h/lần | *"Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License."* — https://developers.google.com/terms/site-policies |
| `arxiv_cs_ai` | arXiv `cs.AI` Daily RSS *(bổ sung)* | `https://rss.arxiv.org/rss/cs.AI` | `Cornell University (arXiv)` | MIM | **Sơ cấp** | Tối đa 1 req / 3 giây, đơn luồng | *"Descriptive metadata... may be used under the terms of the Creative Commons CC0 1.0 Universal Public Domain Dedication."* — https://info.arxiv.org/help/api/tou.html |
| `nist_news_rss` | U.S. NIST News & AI Standards RSS *(bổ sung)* | `https://www.nist.gov/news-events/news/rss.xml` | `US Department of Commerce (NIST)` | MIM | **Sơ cấp** | Không giới hạn cứng; quét 3h/lần | *"NIST web pages are provided as a public service... and therefore are considered to be in the public domain."* — https://www.nist.gov/oism/copyrights |
| `fed_press_monetary` | U.S. Federal Reserve Monetary Policy RSS *(bổ sung)* | `https://www.federalreserve.gov/feeds/press_monetary.xml` | `US Federal Reserve` | CK | **Sơ cấp** | Không giới hạn cứng; quét 3h/lần | *"Information on this site is in the public domain and may be reproduced without permission."* (17 U.S.C. §105) — https://www.federalreserve.gov/disclaimer.htm |
| `bls_latest_rss` | U.S. Bureau of Labor Statistics (CPI/Jobs) RSS *(bổ sung)* | `https://www.bls.gov/feed/bls_latest.rss` | `US Department of Labor (BLS)` | CK | **Sơ cấp** | Không giới hạn cứng; quét 3h/lần | *"Public domain information on the Bureau of Labor Statistics (BLS) webpages may be freely distributed and copied."* — https://www.bls.gov/bls/linksite.htm |
| `gdelt_vi_news` | GDELT DOC 2.0 Vietnamese News RSS *(bổ sung)* | `https://api.gdeltproject.org/api/v2/doc/doc?query=sourcelang:vie&timespan=24h&mode=artlist&maxrecords=50&format=rss` | `GDELT Project` | MIM, CK | Tín hiệu | Tối đa 1 req / 5 giây | *"All datasets released by the GDELT Project are available for unlimited and unrestricted use for any commercial, non-commercial, or research purpose."* — https://www.gdeltproject.org/about.html |

---

### 2.2. Nhóm `pending` — Điều khoản chưa nói rõ đọc tự động tiêu đề nội bộ, trình chủ kênh quyết (17 mục)

| ID | Nguồn | URL feed / API thật | `owner_group` | Kênh | Vai trò | Giới hạn tần suất | Trích điều khoản (≤ 25 từ) & URL ToS |
|---|---|---|---|---|---|---|---|
| `thanhnien_kinh_te` | Báo Thanh Niên - Kinh tế | `https://thanhnien.vn/rss/kinh-te.rss` | `Thanh Niên` | CK | Tín hiệu | Không nêu rõ | *"Khi sử dụng lại các thông tin từ nguồn tin của Thanh Niên Online phải ghi rõ nguồn tin là 'Theo Báo Thanh Niên'."* — https://thanhnien.vn/rss.html |
| `thanhnien_cong_nghe` | Báo Thanh Niên - Công nghệ | `https://thanhnien.vn/rss/cong-nghe.rss` | `Thanh Niên` | MIM | Tín hiệu | Không nêu rõ | *"Khi sử dụng lại các thông tin từ nguồn tin của Thanh Niên Online phải ghi rõ nguồn tin là 'Theo Báo Thanh Niên'."* — https://thanhnien.vn/rss.html |
| `cafef_tai_chinh` | CafeF - Tài chính Ngân hàng | `https://cafef.vn/tai-chinh-ngan-hang.rss` | `VCCorp` | CK | Tín hiệu | Không nêu rõ | *"Khi sử dụng lại các thông tin từ nguồn tin... phải ghi rõ nguồn tin... Cấm sao chép dưới mọi hình thức."* — https://cafef.vn/rss.chn |
| `cafef_vi_mo` | CafeF - Vĩ mô Đầu tư | `https://cafef.vn/vi-mo-dau-tu.rss` | `VCCorp` | CK | Tín hiệu | Không nêu rõ | *"Khi sử dụng lại các thông tin từ nguồn tin... phải ghi rõ nguồn tin... Cấm sao chép dưới mọi hình thức."* — https://cafef.vn/rss.chn |
| `genk_tin_ict` | GenK - Tin ICT & AI | `https://genk.vn/tin-ict.rss` | `VCCorp` | MIM | Tín hiệu | Không nêu rõ | *"Khi sử dụng lại các thông tin từ nguồn tin của Genk.vn phải ghi rõ nguồn tin là 'Theo Genk.vn' hoặc 'Genk.vn'."* — https://genk.vn/rss.chn |
| `vietnamnet_kinh_doanh` | VietNamNet - Kinh doanh | `https://vietnamnet.vn/rss/kinh-doanh.rss` | `VietNamNet` | CK | Tín hiệu | Không nêu rõ | *"Chỉ được phát hành lại thông tin từ website này khi có sự đồng ý bằng văn bản của báo VietNamNet."* — https://vietnamnet.vn/rss |
| `vietnamnet_cong_nghe` | VietNamNet - Công nghệ | `https://vietnamnet.vn/rss/cong-nghe.rss` | `VietNamNet` | MIM | Tín hiệu | Không nêu rõ | *"Chỉ được phát hành lại thông tin từ website này khi có sự đồng ý bằng văn bản của báo VietNamNet."* — https://vietnamnet.vn/rss |
| `sjc_gold_xml` | Bảng giá vàng SJC XML | `https://sjc.com.vn/xml/tygiavang.xml` | `SJC` | CK | **Sơ cấp** | Không nêu rõ | *"Thông tin tỷ giá vàng chỉ mang tính chất tham khảo... Bản quyền thuộc Công ty TNHH MTV Vàng bạc Đá quý Sài Gòn."* — https://sjc.com.vn/giavang/textContent.php |
| `chinhphu_kinh_te` | Báo Điện tử Chính phủ - Kinh tế | `https://baochinhphu.vn/rss/kinh-te.rss` | `Chính phủ Việt Nam` | MIM, CK | **Sơ cấp** | Không nêu rõ | *"Ghi rõ nguồn 'Cổng Thông tin điện tử Chính phủ' hoặc 'baochinhphu.vn' khi phát hành lại thông tin từ các nguồn này."* — https://baochinhphu.vn |
| `vanban_chinhphu_rss` | Công báo & Văn bản Chính phủ mới | `https://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss` | `Chính phủ Việt Nam` | MIM, CK | **Sơ cấp** | Không nêu rõ | *"Các nguồn kênh tin được cung cấp miễn phí cho các cá nhân và các tổ chức phi lợi nhuận."* (Văn bản luật: Điều 15 Luật SHTT) — https://congbao.chinhphu.vn/rss |
| `sbv_gov_vn` | Cổng TTĐT Ngân hàng Nhà nước | `https://www.sbv.gov.vn/webcenter/portal/vi/home/rm/rss` | `Ngân hàng Nhà nước Việt Nam` | CK | **Sơ cấp** | Không nêu rõ | *"Ghi rõ nguồn 'Cổng thông tin điện tử Ngân hàng Nhà nước Việt Nam' hoặc 'www.sbv.gov.vn' khi phát hành lại thông tin."* — https://www.sbv.gov.vn |
| `mof_gov_vn` | Cổng TTĐT Bộ Tài chính | `https://mof.gov.vn/webcenter/portal/btcvn/pages_r/l/tin-bo-tai-chinh` | `Bộ Tài chính Việt Nam` | CK | **Sơ cấp** | Không nêu rõ | *"Ghi rõ nguồn 'Cổng Thông tin điện tử Bộ Tài chính' hoặc 'www.mof.gov.vn' khi phát hành lại thông tin từ địa chỉ này."* — https://mof.gov.vn |
| `bhxh_gov_vn` | Cổng TTĐT Bảo hiểm xã hội VN | `https://baohiemxahoi.gov.vn/rss/tin-tuc-su-kien.rss` | `Bảo hiểm xã hội Việt Nam` | CK | **Sơ cấp** | Không nêu rõ | *"Ghi rõ nguồn 'Cổng Thông tin điện tử Bảo hiểm xã hội Việt Nam' khi trích dẫn, sử dụng lại thông tin."* — https://baohiemxahoi.gov.vn |
| `openai_news_rss` | OpenAI News RSS | `https://openai.com/news/rss.xml` | `OpenAI` | MIM | **Sơ cấp** | Không nêu rõ cho RSS | *"You may not... automatically or programmatically extract data or Output."* (Áp dụng cho Services; RSS công khai chưa tách điều khoản) — https://openai.com/policies/terms-of-use/ |
| `microsoft_blog_rss` | Official Microsoft Blog RSS | `https://blogs.microsoft.com/feed/` | `Microsoft` | MIM | **Sơ cấp** | Không nêu rõ cho RSS | *"Unless otherwise specified, the Services are for your personal and non-commercial use."* — https://www.microsoft.com/en-us/legal/terms-of-use |
| `apple_newsroom_rss` | Apple Newsroom RSS | `https://www.apple.com/newsroom/rss-feed.rss` | `Apple` | MIM, CK | **Sơ cấp** | Không nêu rõ cho RSS | *"No part of the Site and no Content may be copied, reproduced, republished... for any commercial enterprise."* — https://www.apple.com/legal/internet-services/terms/site.html |
| `huggingface_blog_rss` | Hugging Face Blog RSS *(bổ sung)* | `https://huggingface.co/blog/feed.xml` | `Hugging Face` | MIM | **Sơ cấp** | Không nêu rõ cho RSS | *"You may not access or search... the Services by any means (automated or otherwise) other than through our currently available, published interfaces."* — https://huggingface.co/terms-of-service |

---

### 2.3. Nhóm `blocked` — Cấm thương mại, cấm tự động hoặc cấm thu thập khi chưa xin phép (15 mục)

| ID | Nguồn | URL feed / API thật | `owner_group` | Kênh | Lý do `blocked` | Trích điều khoản (≤ 25 từ) & URL ToS |
|---|---|---|---|---|---|---|
| `vnexpress_kinh_doanh` | VnExpress - Kinh doanh | `https://vnexpress.net/rss/kinh-doanh.rss` | `VnExpress (FPT)` | CK | Giới hạn cá nhân & phi lợi nhuận; ToS chung cấm thương mại khi chưa xin phép | *"Các nguồn kênh tin được cung cấp miễn phí cho các cá nhân và các tổ chức phi lợi nhuận."* — https://vnexpress.net/rss |
| `vnexpress_so_hoa` | VnExpress - KHCN / Số hóa | `https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss` | `VnExpress (FPT)` | MIM | Như trên | *"Các nguồn kênh tin được cung cấp miễn phí cho các cá nhân và các tổ chức phi lợi nhuận."* — https://vnexpress.net/rss |
| `tuoitre_kinh_doanh` | Tuổi Trẻ - Kinh doanh | `https://tuoitre.vn/rss/kinh-doanh.rss` | `Tuổi Trẻ` | CK | Giới hạn cá nhân & tổ chức phi lợi nhuận | *"Các nguồn kênh tin được cung cấp miễn phí cho các cá nhân và các tổ chức phi lợi nhuận."* — https://tuoitre.vn/rss.htm |
| `tuoitre_cong_nghe` | Tuổi Trẻ - Nhịp sống số | `https://tuoitre.vn/rss/nhip-song-so.rss` | `Tuổi Trẻ` | MIM | Như trên | *"Các nguồn kênh tin được cung cấp miễn phí cho các cá nhân và các tổ chức phi lợi nhuận."* — https://tuoitre.vn/rss.htm |
| `dantri_kinh_doanh` | Dân Trí - Kinh doanh | `https://dantri.com.vn/rss/kinh-doanh.rss` | `Dân Trí` | CK | Giới hạn cá nhân & tổ chức phi lợi nhuận | *"Các nguồn kênh tin được cung cấp miễn phí cho các cá nhân và các tổ chức phi lợi nhuận."* — https://dantri.com.vn/rss.htm |
| `dantri_suc_manh_so` | Dân Trí - Sức mạnh số | `https://dantri.com.vn/rss/suc-manh-so.rss` | `Dân Trí` | MIM | Như trên | *"Các nguồn kênh tin được cung cấp miễn phí cho các cá nhân và các tổ chức phi lợi nhuận."* — https://dantri.com.vn/rss.htm |
| `vneconomy_tai_chinh` | VnEconomy - Tài chính | `https://vneconomy.vn/tai-chinh.rss` | `VnEconomy` | CK | Giới hạn cá nhân & tổ chức phi lợi nhuận | *"Các nguồn kênh tin được cung cấp miễn phí cho các cá nhân và các tổ chức phi lợi nhuận."* — https://vneconomy.vn/rss.htm |
| `vneconomy_kinh_te_so` | VnEconomy - Kinh tế số | `https://vneconomy.vn/kinh-te-so.rss` | `VnEconomy` | MIM | Như trên | *"Các nguồn kênh tin được cung cấp miễn phí cho các cá nhân và các tổ chức phi lợi nhuận."* — https://vneconomy.vn/rss.htm |
| `google_news_mim` | Google News Search RSS (MIM) | `https://news.google.com/rss/search?q=AI+OR+chip+OR+b%C3%A1n+d%E1%BA%ABn+OR+OpenAI&hl=vi&gl=VN&ceid=VN:vi` | `Google` | MIM | `news.google.com/robots.txt` chặn `Disallow: /search`; không có API thương mại chính thức | *"Don't abuse our services... using automated means to access content... in violation of the machine-readable instructions."* (`Disallow /search`) — https://policies.google.com/terms |
| `google_news_ck` | Google News Search RSS (CK) | `https://news.google.com/rss/search?q=l%C3%A3i+su%E1%BA%A5t+OR+t%E1%BB%B7+gi%C3%A1+OR+gi%C3%A1+v%C3%A0ng+OR+tr%C3%A1i+phi%E1%BA%BFu&hl=vi&gl=VN&ceid=VN:vi` | `Google` | CK | Như trên | *"Don't abuse our services... using automated means to access content... in violation of the machine-readable instructions."* (`Disallow /search`) — https://policies.google.com/terms |
| `reddit_technology` | Reddit `r/technology` JSON | `https://www.reddit.com/r/technology/hot.json?limit=25` | `Reddit` | MIM | Cấm mục đích thương mại nếu không ký hợp đồng trả phí (10 QPM unauth) | *"You may not use the Data API Services for any commercial purposes... without Reddit's prior written consent."* — https://redditinc.com/policies/data-api-terms |
| `reddit_machinelearning` | Reddit `r/MachineLearning` JSON | `https://www.reddit.com/r/MachineLearning/hot.json?limit=25` | `Reddit` | MIM | Như trên | *"You may not use the Data API Services for any commercial purposes... without Reddit's prior written consent."* — https://redditinc.com/policies/data-api-terms |
| `reddit_vietnam` | Reddit `r/vietnam` JSON | `https://www.reddit.com/r/vietnam/hot.json?limit=25` | `Reddit` | MIM, CK | Như trên | *"You may not use the Data API Services for any commercial purposes... without Reddit's prior written consent."* — https://redditinc.com/policies/data-api-terms |
| `vcb_exchange_xml` | Tỷ giá Vietcombank XML | `https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx` | `Vietcombank` | CK | Cấm sử dụng thương mại không có văn bản; además luật kênh CK cấm nêu tên ngân hàng thương mại | *"Nghiêm cấm việc sao chép, sửa đổi, phân phối, xuất bản... vì mục đích thương mại mà không có sự đồng ý bằng văn bản."* — https://www.vietcombank.com.vn/vi-VN/Dieu-khoan-su-dung |
| `meta_newsroom_rss` | Meta Newsroom RSS | `https://about.fb.com/news/feed/` | `Meta` | MIM | Cấm thu thập tự động từ Products khi chưa có phép trước | *"You may not access or collect data from our Products using automated means (without our prior permission)."* — https://www.facebook.com/terms.php |
| `nvidia_blog_rss` | NVIDIA Official Blog RSS | `https://blogs.nvidia.com/feed/` | `NVIDIA` | MIM | Điều khoản RSS ghi rõ chỉ dành cho mục đích phi thương mại | *"RSS service is provided free of charge for non-commercial purposes only... NVIDIA reserves the right to discontinue this service."* — https://www.nvidia.com/en-us/about-nvidia/terms-of-service/ |

---

## 3. Khuyến nghị cho Chủ kênh & Lưu ý kỹ thuật P0/P1

### 3.1. Danh sách `ok` để bật ngay trong P0
- **13 nguồn `ok`** đã sẵn sàng trong `docs/pm/tickets/GH-31-sources.json`:
  - **Cho MIM (10 nguồn thuộc 7 `owner_group`):** `google_trends_vn`, `hacker_news`, `wikipedia_pageviews_vi`, `wikipedia_pageviews`, `sec_press_releases`, `sec_edgar_current`, `google_blog_rss`, `google_devs_blog_rss`, `arxiv_cs_ai`, `nist_news_rss`, `gdelt_vi_news`.
  - **Cho CK (8 nguồn thuộc 6 `owner_group`):** `google_trends_vn`, `wikipedia_pageviews_vi`, `wikipedia_pageviews`, `sec_press_releases`, `sec_edgar_current`, `fed_press_monetary`, `bls_latest_rss`, `gdelt_vi_news`.

### 3.2. Danh sách `pending` cần Chủ kênh quyết
Chủ kênh có thể xem xét duyệt bật từng nhóm sau (vì P0 chỉ đọc tiêu đề + URL lưu nội bộ, tuyệt đối không đăng lại nội dung bài báo):
1. **Nhóm P-A — Báo VN không ghi giới hạn "phi lợi nhuận" trên trang RSS (`Thanh Niên`, `CafeF`/`GenK` thuộc `VCCorp`, `VietNamNet`):**
   - Khác với VnExpress/Tuổi Trẻ/Dân Trí/VnEconomy, trang điều khoản RSS của Thanh Niên, CafeF, GenK và VietNamNet chỉ yêu cầu ghi nguồn hoặc xin phép khi **"sử dụng lại / phát hành lại thông tin"**. Nếu chủ kênh đồng ý việc đọc tiêu đề làm tín hiệu nội bộ không phải là "phát hành lại", có thể chuyển 7 feed này sang `ok` (lưu ý `CafeF` và `GenK` đã gắn chung `owner_group: "VCCorp"` để không đếm trùng nguồn độc lập).
2. **Nhóm P-B — Cổng cơ quan nhà nước VN (`chinhphu.vn`, `vanban.chinhphu.vn`, `sbv.gov.vn`, `mof.gov.vn`, `baohiemxahoi.gov.vn`) & Giá vàng `SJC`:**
   - Theo **Điều 15 Luật Sở hữu trí tuệ Việt Nam**, văn bản quy phạm pháp luật và văn bản hành chính của cơ quan nhà nước không thuộc đối tượng bảo hộ quyền tác giả (thuộc phạm vi công cộng). Tuy nhiên, trang RSS Công báo có câu mẫu *"miễn phí cho cá nhân và tổ chức phi lợi nhuận"* và các cổng `sbv.gov.vn` / `mof.gov.vn` hay lỗi kết nối/SSL với bot tự động. Khuyến nghị: giữ `pending` ở bước quét tự động 3h/lần P0 (hoặc chỉ bật `chinhphu_kinh_te`), và ưu tiên dùng làm **nguồn kiểm chứng sơ cấp bắt buộc ở bước Factcheck P1**.
3. **Nhóm P-C — RSS thông cáo báo chí công nghệ (`openai_news_rss`, `microsoft_blog_rss`, `apple_newsroom_rss`, `huggingface_blog_rss`):**
   - Các hãng này mở RSS công khai cho trình đọc tin (`feed.xml` / `rss.xml` không bị chặn trong `robots.txt`), nhưng điều khoản website chung có câu mẫu hạn chế scraping/commercial use. Nếu chủ kênh chấp nhận dùng RSS chính thức đúng chuẩn feed reader để lấy tiêu đề thông cáo báo chí, có thể chuyển sang `ok`.

### 3.3. Bốn lưu ý kỹ thuật cho Lead và Codex khi ghép vào `factory/trend/`
1. **`User-Agent` cho SEC EDGAR và Wikimedia:**
   - SEC (`sec.gov`) bắt buộc header `User-Agent` có định dạng `SampleCompanyName AdminContact@<domain>.com` (có địa chỉ email liên hệ); nếu dùng chuỗi không có email, tường lửa Akamai của SEC có thể trả `403 Forbidden`. Wikimedia cũng yêu cầu thông tin liên hệ trong `User-Agent`.
2. **Giãn cách 5 giây cho GDELT DOC 2.0 API:**
   - Endpoint `api.gdeltproject.org` giới hạn 1 request / 5 giây. Hiện trong `GH-31-sources.json` chỉ cấu hình **1 mục GDELT duy nhất (`gdelt_vi_news`)** nên mỗi lần `scan.py` chạy chỉ gọi GDELT đúng 1 lần, không bao giờ chạm trần 5 giây.
3. **Luật kênh CK đối với Vietcombank (`vcb_exchange_xml`):**
   - Ngoài việc ToS của Vietcombank cấm mục đích thương mại (`blocked`), quy tắc kênh CK trong `AGENTS.md` **cấm tuyệt đối nêu tên ngân hàng thương mại**. Khi cần dữ liệu tỷ giá làm nguồn sơ cấp cho CK, luôn dùng tỷ giá trung tâm của Ngân hàng Nhà nước (`sbv.gov.vn`).
4. **Định dạng XML của `sjc_gold_xml`:**
   - File `https://sjc.com.vn/xml/tygiavang.xml` dùng thẻ `<ratelist><city><item buy="..." sell="..." type="..."/>`, không có thẻ `<title>` và `<link>` chuẩn RSS 2.0. Hiện mục này đang để `tos_status: "pending"`; nếu chủ kênh duyệt bật trong tương lai thì `parse_rss` trong `scan.py` cần thêm nhánh đọc thuộc tính `buy`/`sell` của thẻ `<item>`.
