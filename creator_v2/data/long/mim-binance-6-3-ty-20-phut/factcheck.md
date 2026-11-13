# Fact-check: script.md (bản 1) · mim-binance-6-3-ty-20-phut

Ngày kiểm: 13/11/2026. Người kiểm: agent viết kịch bản (Sonnet), đọc bằng WebSearch/WebFetch; chưa có người thứ hai đọc lại. Số `[Fn]` là nguồn ở mục 6.

**Kết luận về sự kiện lõi: ĐÃ XÁC MINH, có chỉnh.** Vụ Binance bị rút khoảng 6,3 tỷ USD ngày 29/10/2026 là có thật (Reuters, CoinDesk, TechCrunch, The Block, TRM Labs, Elliptic, FBI). Khác với `plan.md` ở bốn điểm: (a) "20 phút" là khung TRM Labs nêu cho **phần lớn** số tiền, cả đợt rút kéo dài gần bốn tiếng (20:05–23:56 UTC theo Elliptic); (b) số tiền bị đóng băng là 2,4–2,84 tỷ tùy bên đếm, không phải "3 tỷ"; (c) 36 giờ là giai đoạn dàn dựng (nạp ví từ Tornado Cash, chạy thử trên ba ví), không phải "gửi lệnh thử vào hệ thống phê duyệt"; (d) cảnh đám đông "xin tiền hacker" và "gửi 1 nhận 10" không kiểm được đủ nguồn nên bỏ.

Nhãn: OK = khớp ít nhất một nguồn đã đọc; 2N = khớp từ hai nguồn độc lập; SECONDARY = chỉ qua báo/bài phân tích lại; GỐC? = chưa mở được bản gốc (máy chặn hoặc 403), chỉ có qua kết quả tìm kiếm và bài khác dẫn lại.

## 1. Bảng kiểm

| Mục | Khẳng định trong lời đọc | Nguồn | Trích (tiếng gốc hoặc tóm lược) | Trạng thái |
|---|---|---|---|---|
| 00 | Binance bị rút khoảng 6,3 tỷ USD trên mười chuỗi khối, ngày 29/10/2026, bắt đầu 20:05 UTC (= 3 giờ sáng 30/10 ở Hà Nội) | [F1] VnExpress; [F2] Halborn; [F3] TRM qua tìm kiếm | VnExpress: "Most funds left in roughly 20 minutes, starting at 20:05 UTC on October 29 (3:00 a.m. on October 30 in Hanoi)" (tóm lược). Halborn: "Date and window: October 29, 2026, 20:05 to 23:56 UTC… ten blockchains" | 2N |
| 00 | Năm ví XRP gửi hơn 233 triệu XRP về một địa chỉ trong bốn phút đầu | [F1] VnExpress; [F2] Halborn | VnExpress: "Five wallets sent about 233.46 million XRP in the first four minutes". Halborn: "20:05 Five Binance wallets on the XRP Ledger send 233.46 million XRP to one address" | 2N |
| 00 | Phần lớn số tiền đi trong khoảng hai mươi phút | [F1] VnExpress; [F3] TRM qua tìm kiếm; ACAMS (tiêu đề) | "Most of it went out in about 20 minutes starting at 20:05 UTC" (TRM, qua tìm kiếm) | OK (khung của TRM, lời đọc nói "phần lớn") |
| 00 | Ít nhất 36 giờ dàn dựng trước vụ trộm (TRM Labs) | [F4] The Block; [F1] VnExpress | The Block: "The attacker began staging at least 36 hours before the theft" (TRM Labs). VnExpress: "Quá trình chuẩn bị bắt đầu ít nhất 36 tiếng trước khi vụ hack xảy ra" | 2N |
| 00 | Trong chưa đầy một tiếng các nhà phát hành stablecoin khóa phần rất lớn | [F2] Halborn | "Tether froze within 37 minutes and Circle within 41, and between the issuers roughly 2.8 billion dollars stopped moving." | OK |
| 01 | Vụ lớn nhất trước đó là Bybit, năm 2025, khoảng 1,5 tỷ USD; vụ này gấp hơn bốn lần | [F4] The Block; [F1] VnExpress | The Block: "the same group connected to the $1.5 billion Bybit hack". VnExpress: "roughly $1.5 billion Bybit lost last year". Phép tính 6,3 / 1,5 ≈ 4,2 là của người viết | OK (năm 2025 suy từ "last year" trong bài 2026, khớp hiểu biết về vụ Bybit tháng 2/2025) |
| 01 | TRM tính 6,36 tỷ; Elliptic 6,43 tỷ; Binance khoảng 6,3 tỷ và để riêng 6,34 tỷ tiền công ty để bù | [F2] Halborn; [F5] NBC/Reuters; [F1] VnExpress | Halborn: "TRM at $6.36 billion, Elliptic at $6.43 billion". NBC/Reuters: "Binance said it set aside about $6.34 billion of company funds to cover losses." VnExpress: "Binance confirmed the attack affected about $6.3 billion" | 2N |
| 01 | "Lớn nhất lịch sử" là cách TRM gọi | [F3] TRM | Tiêu đề bài TRM: "North Korea Steals USD 6.36 Billion From Binance in the Largest Hack in History" | GỐC? (tiêu đề thấy ở kết quả tìm kiếm) |
| 01 | Ví lạnh tắt mạng, ví nóng nối mạng để trả lệnh rút | Giải thích chung, không phải số liệu; Halborn/TRM gọi các ví bị rút là "hot wallets" | — | OK (định nghĩa phổ thông) |
| 02 | Dàn dựng: nạp ví điều hành bằng khoản nhỏ rút từ Tornado Cash; chạy thử mã trên ba ví | [F4] The Block; [F2] Halborn | The Block: "funding an operational wallet with small Tornado Cash withdrawals"; "deployed and tested malicious code on three wallets before executing the attack." Halborn: "Oct 28 to 29: The attacker funded an operator wallet from Tornado Cash and deployed and tested a delegate contract." | 2N |
| 02 | Tornado Cash là dịch vụ trộn tiền để che nguồn gốc | Giải thích chung | — | OK |
| 02 | Binance chưa công bố báo cáo cuối | [F6] TechCrunch | "Binance will publish a more detailed incident report once its investigation is complete." | OK |
| 03 | 20:10 chuyển khoản trên Solana, Optimism, Base, Arbitrum; 20:20 ví Bitcoin gửi 18.270 BTC; chia nhỏ để khó lần | [F2] Halborn; [F1] VnExpress | Halborn: "20:10 Transfers begin on Solana, Optimism, Base, and Arbitrum"; "20:20 A Binance Bitcoin hot wallet sends 18,270 BTC." VnExpress: BTC "split into smaller chunks to complicate tracing" | 2N |
| 03 | Nâng cấp Pectra tháng 5/2025 cho phép ví thường ủy quyền cho mã chạy thay | [F2] Halborn | "EIP-7702 shipped with the Pectra upgrade in May 2025." "every call to the account, even a plain transfer, runs the delegate's code in the account's own context." | OK |
| 03 | 50 chữ ký ủy quyền chuẩn bị sẵn để ít nhất một cái còn hiệu lực | [F4] The Block; [F2] Halborn | The Block: "prepared 50 pre-signed authorizations to ensure one would remain valid when executed." Halborn: "20:20:59 A transaction carrying 50 EIP-7702 authorizations…" | 2N |
| 03 | Đoạn mã hút tiền dài khoảng 130 dòng (Immunefi) | [F4] The Block | "The sweeper contract was only around 130 lines," according to Immunefi's Simone Imbrescia. | OK |
| 03 | 20:24 lần quét đầu lấy khoảng 1,6 tỷ USDT và 167.464 ETH | [F2] Halborn | "20:24:23 The first sweep drains Binance 14 to a hub address, including about 1.6 billion USDT and 167,464 ETH." (lời đọc nói "hơn một trăm sáu mươi bảy nghìn") | SECONDARY (chưa đọc bản Elliptic gốc) |
| 03 | Đợt hai trên Avalanche và Polygon lúc 23:00; cả vụ tới gần nửa đêm (23:56); Binance gỡ ủy quyền lúc 00:10 ngày 30/10, gần bốn tiếng sau khi cài | [F2] Halborn | "23:05 A second wave hits Avalanche and Polygon." "00:10:35 (Oct 30) Binance clears the delegation, about three hours and 50 minutes after it was installed." "October 29, 2026, 20:05 to 23:56 UTC." | OK |
| 04 | Binance: laptop kỹ sư DevOps bị chiếm, truy cập trái phép vào service container, chưa thấy lộ khóa riêng | [F4] The Block; [F2] Halborn | The Block: "compromised DevOps engineer's laptop", "unauthorized access to a service container", "has not identified a private-key leak." | 2N |
| 04 | Điều tra sau đó thấy thêm điểm xâm nhập khác | [F1] VnExpress; [F2] Halborn | VnExpress (trích Binance trên X): "Tuy nhiên, cuộc điều tra sau đó của chúng tôi đã phát hiện thêm các điểm xâm nhập khác". Halborn: laptop "was not the only point of breach" | 2N |
| 04 | Richard Teng gọi là "cuộc tấn công phức tạp"; Reuters: có phần mềm độc hại để xóa dấu vết | [F5] NBC/Reuters | "Binance CEO Richard Teng said Friday the breach was a 'complex attack' involving a compromised laptop and malicious software meant to delete evidence." (The Block gọi ông là co-CEO; lời đọc dùng "người đứng đầu Binance") | OK |
| 04 | TRM: dấu hiệu chỉ về việc hệ thống ký của ví nóng bị xâm phạm | [F3] TRM qua tìm kiếm; [F4] The Block | "TRM says this points to a compromise of Binance's hot wallet signing infrastructure." The Block: "coordinated transfers across nine other blockchains, suggesting a broader hot-wallet signing compromise." | OK (TRM gốc chưa mở được) |
| 04 | Halborn: chữ ký hợp lệ do chính hệ thống ký của sàn tạo; Bybit và Binance là cùng một thất bại | [F2] Halborn | "Bybit and Binance are the same failure in different clothes." "In both, the legitimate signing system produced a valid signature for the attacker's transaction" | OK (nhận định của Halborn, lời đọc ghi rõ) |
| 04 | TRM liên hệ với nhóm đứng sau vụ Bybit | [F4] The Block | TRM linked it to "the same group connected to the $1.5 billion Bybit hack." | OK |
| 05 | 21:01 Tether khóa khoảng 971 triệu USDT trên Ethereum; 21:04 Circle khóa 823 triệu USDC; Tether sau 37 phút, Circle sau 41 phút | [F2] Halborn | Bảng khóa: "21:01:35 Tether USDT (Ethereum) 971.1 million"; "21:04:59 Circle USDC 823 million". "Tether froze within 37 minutes and Circle within 41" | OK (Halborn là nguồn duy nhất cho giờ chi tiết) |
| 05 | Ripple (RLUSD) và World Liberty (USD1) cũng khóa; Tether đưa ví nóng Binance vào danh sách đen | [F2] Halborn | "22:00:59 Ripple RLUSD 40.5 million"; "22:10:35 World Liberty USD1 27.8 million"; "Tether blacklisted Binance's own hot wallet to stop the sweeper" | OK |
| 05 | Stablecoin có hàm cho nhà phát hành đưa địa chỉ vào danh sách đen; Bitcoin/Ether không có nhà phát hành | [F2] Halborn; giải thích chung | Halborn: "A blacklisted balance sits in the thief's address until the issuer burns and reissues it under a legal process" | OK |
| 05 | Tổng bị khóa: CoinDesk hơn 2,4 tỷ; TRM khoảng 2,7 tỷ; Elliptic khoảng 2,84 tỷ, tức khoảng 44% | [F7] CoinDesk; [F3] TRM qua tìm kiếm; Elliptic qua tìm kiếm và [F2] Halborn | CoinDesk: "Stablecoin issuers froze over $2.4 billion of the stolen funds." TRM: "About $2.7 billion has been frozen". Elliptic qua tìm kiếm: "about $2.84 billion frozen, roughly 44% of the theft". Halborn: "about 44 percent of the stolen value is frozen and none has been recovered" | 2N cho khoảng; từng số riêng SECONDARY |
| 05 | Đóng băng không phải là lấy lại | [F2] Halborn | "Freezing is not recovering." | OK |
| 06 | Kẻ tấn công đổi khoảng 325 triệu USD stablecoin lấy khoảng 285 triệu USD ETH trong gần 20 phút, chấp nhận lỗ tới 26%, có vẻ để tránh bị khóa | [F4] The Block (dẫn Elliptic) | "The attacker converted $325 million in stablecoins into $285 million in ETH over nearly 20 minutes, apparently to avoid freezes." "losses 'of as much as 26% against market prices.'" | OK (một nguồn, dẫn Elliptic) |
| 06 | Phần còn lại phần lớn là ETH và BTC; kẻ tấn công vẫn giữ khoảng 2,4 tới 3 tỷ | TRM và Elliptic qua tìm kiếm | TRM: "the attacker still holds roughly $2.4 billion"; Elliptic: "around $3.0 billion remains in addresses linked to the theft, mostly as ETH and BTC" | SECONDARY, GỐC? |
| 06 | 31/10/2026 FBI: Triều Tiên chịu trách nhiệm; gọi là TraderTraitor, đơn vị thuộc nhóm Lazarus; đang đổi sang Ether; còn rửa tiếp | [F7] CoinDesk; [F5] NBC/Reuters; FBI qua tìm kiếm | CoinDesk: "TraderTraitor is a subunit of the Lazarus Group." "The FBI said the hackers had mainly been converting the stolen funds into ether." NBC: FBI "expects 'further laundering'". FBI (qua tìm kiếm): "North Korea responsible for the theft of over $6 billion in virtual assets from Binance on or about October 29, 2026" | 2N |
| 06 | Danh sách hơn 600 địa chỉ Ethereum, gần 20 Bitcoin, 1 Solana; FBI đề nghị khu vực tư nhân chặn | [F7] CoinDesk | "The notice listed over 600 Ethereum addresses, just under 20 Bitcoin addresses, and one Solana address." | OK |
| 06 | Ba hãng (TRM, Elliptic, Chainalysis) đã gán trước đó; TRM tin ở mức cao, Elliptic "nhiều khả năng" | [F4] The Block; [F2] Halborn | The Block: "Chainalysis, Elliptic, and TRM attributed the attack to North Korean hacking groups." Halborn: "TRM reports high confidence… Elliptic says 'likely.'" | 2N |
| 06 | 02/11/2026 Kim Yo Jong bác bỏ, nói FBI muốn gán nhãn "quốc gia tội phạm mạng" | [F8] The Block (dẫn Yonhap) | Cô ấy nói FBI đang cố "brand the DPRK as a 'cyber criminal state'" | OK |
| 06 | Chainalysis (Jonathan Levin): hàng nghìn địa chỉ, dự đoán hàng chục nghìn trong những tuần tới | [F7] CoinDesk | Levin: "thousands of addresses… tens of thousands over the coming weeks." | OK |
| 07 | Binance tạm dừng rút khoảng 22:30 UTC đêm 29/10 | [F2] Halborn | "Withdrawals were paused around 22:30." | OK (giờ UTC; lời đọc nói "khoảng hai mươi hai giờ ba mươi" không ghi múi giờ, xem rủi ro) |
| 07 | Bù từ quỹ SAFU (~1 tỷ USD Bitcoin), một phần Futures Insurance Fund, kho bạc công ty; 31/10 đã bù 90% | [F5] NBC/Reuters | "Replacement funds came from the $1 billion Secure Asset Fund for Users (a bitcoin reserve), part of the Futures Insurance Fund, and the corporate treasury." "replaced 90% of the stolen assets" | OK |
| 07 | 01/11 bù 95%; mở rút theo giai đoạn | [F6] TechCrunch | "Binance says it has covered 95% of the stolen assets." "restore withdrawals in phases." | OK |
| 07 | Từ 06:00 đến 15:30 UTC ngày 01/11: rút 4,6 tỷ, nạp 1,0 tỷ, chênh ròng 3,6 tỷ = 2,1% tổng tài sản | [F6] TechCrunch | "Between 6 a.m. and 3:30 p.m. UTC, Binance processed $4.6 billion in withdrawals and $1.0 billion in deposits." "net outflow was $3.6 billion, or 2.1% of total assets under management." | OK |
| 07 | Bằng chứng dự trữ mới, tối thiểu 1:1 | [F5] NBC/Reuters | "can verify their assets are backed at a minimum 1-to-1 ratio once the full proof is available." (lời đọc nói "có thể kiểm chứng"; bản đầy đủ khi nào có chưa rõ) | OK |
| 08 | Tổng kết: không phá mật mã; hệ thống ký bị xâm phạm; gần một nửa bị khóa vì là stablecoin | Tổng hợp các dòng trên | — | Nhận định của người viết, dựa trên các dòng 04–05 |

TRÍCH DỊCH (mỗi dòng có nguyên văn và URL):

- TRÍCH DỊCH, câu FBI đề nghị chặn giao dịch (CH06). nguyên văn: "block transactions with or derived from addresses TraderTraitor actors are using to launder these stolen assets". URL: https://www.coindesk.com/policy/2026/10/31/fbi-confirms-north-korea-s-role-in-usd6-billion-binance-hack-asks-defi-community-to-block-btc-eth-sol-addresses (CoinDesk trích thông cáo FBI; lời đọc ghép "Hãy chặn… các nhân vật TraderTraitor" cho tai; ý nguyên văn không đổi). Dấu hiệu: CoinDesk trích một vế, bản FBI gốc 403.
- TRÍCH DỊCH, câu của Levin (CH06). nguyên văn: "They have too much money for their trusted laundering venues to handle." URL: https://www.coindesk.com/policy/2026/10/31/fbi-confirms-north-korea-s-role-in-usd6-billion-binance-hack-asks-defi-community-to-block-btc-eth-sol-addresses
- TRÍCH DỊCH, câu của Richard Teng trên X (CH07). nguyên văn: "Our users will not bear the financial impact of this incident." URL: https://www.nbcnews.com/business/business-news/fbi-says-north-korea-was-6-billion-binance-crypto-hack-rcna606758
- TRÍCH DỊCH, cụm của Kim Yo Jong (CH06, trong lời đọc, không gắn nhãn). nguyên văn: "brand the DPRK as a 'cyber criminal state'". URL: https://www.theblock.co/news/regulation/2026-11-02-kim-jong-un-sister-rejects-fbi-claims-linking-north-korea-binance-hack-432344

## 2. Tựa và tiêu đề

Tựa phương án (1) 20 phút, 6,3 tỷ đô; (2) 36 giờ, 6,3 tỷ đô; (3) 2,8 tỷ đô bị đóng băng: số 2,8 là cách làm tròn của Halborn (roughly 2.8 billion) và nằm trong khoảng 2,4–2,84. Nếu Lead lo con số, dùng phương án (1) hoặc (2).

## 3. Phần đã bỏ so với plan.md

- "Khoảng 3 tỷ đô thành tiền chết trong ví kẻ trộm": nguồn nói 2,4–2,84 tỷ bị khóa, và phần kẻ trộm còn giữ (2,4–3 tỷ) lại chủ yếu là ETH, BTC, loại không khóa được. Đảo chiều so với plan.
- Cảnh đám đông "xin tiền hacker" và "gửi 1 nhận 10": chỉ có tin nhỏ lẻ trên một số trang tiền mã hóa (micropayment kèm lời nhắn trên các ví Bitcoin), số liệu mỗi nơi một khác, không đọc được bài gốc. Bỏ cả chương CH07 của plan.
- Vụ DOJ nhắm 1,2 tỷ USD từ Binance hack: chỉ thấy ở một dòng tin phụ, tìm kiếm không ra nguồn. Bỏ.
- "Tám tòa soạn độc lập", "BBC", "The Verge", "The Register", "VietNamNet", "VnEconomy", URL VnExpress/VietNamNet trong plan: chưa kiểm hết; chỉ dùng nguồn đã đọc. URL VnExpress đọc được nhưng công cụ không xác nhận bài là thật 100%, nên mỗi dòng dùng VnExpress đều có nguồn thứ hai.
- "Chạy thử mã qua Tornado Cash để thăm dò hệ thống phê duyệt": sai nghĩa; Tornado Cash chỉ dùng để nạp tiền cho ví điều hành.
- "Quỹ FIF" và "đồng CEO CZ": không có trong nguồn đã đọc. Bỏ tên CZ.
- "Hàm quản trị blacklist/freeze nằm sâu trong hợp đồng thông minh": lời đọc chỉ nói "có sẵn một hàm cho phép nhà phát hành đưa địa chỉ vào danh sách đen" (khớp Halborn).

## 4. Rủi ro còn lại cho người duyệt

1. Nhiều giờ chi tiết (21:01, 21:04, 20:24, 00:10) chỉ có ở Halborn; Halborn lấy từ dòng thời gian của Elliptic/TRM nhưng chưa đối chiếu được bản gốc (máy không mở được trmlabs.com, elliptic.co, fbi.gov).
2. "Hai mươi hai giờ ba mươi" ở CH07 là giờ UTC, lời đọc không nói múi giờ.
3. "Nhóm Lazarus", "TraderTraitor" và việc Triều Tiên chịu trách nhiệm là kết luận của FBI và các hãng; lời đọc luôn gắn tên nguồn và có câu phủ nhận của phía Triều Tiên.
4. Sự kiện còn mới (13/11/2026); số liệu có thể đổi (số bị khóa, số đã bù). Nên kiểm lại tuần dựng.
5. Phép so sánh "kẻ trộm thử chìa khóa" là ẩn dụ của người viết, có câu nói rõ.

## 5. Ghi chú nhà

- Số trong tiêu đề/ghi chú script: 20, 36, 6,3, 6,36, 6,43, 6,34, 2,8, 2,4, 2,84, 1,2, ngày 31/10/2026, 30/10/2026, 02/11/2026, 01/11/2026, 12/10/2026, 13/11/2026; đều được dòng nguồn ở trên hoặc mục 3 đỡ.
- Chỉ số sản xuất nội bộ trong tiêu đề script (không phải dữ kiện): 9 chương, 9 phút, 45% và 75% (mốc giữ chân).
- Không hướng dẫn cách tấn công, không nêu địa chỉ ví, không khuyên đầu tư.

## 6. Nguồn đã mở

- [F1] VnExpress: https://vnexpress.net/hacker-thu-nghiem-truoc-36-tieng-rut-6-3-ty-usd-tu-vi-binance-trong-20-phut-5139116.html
- [F2] Halborn: https://www.halborn.com/blog/post/binance-hack-explained-what-it-means-for-bank-custody
- [F3] TRM Labs (chỉ qua kết quả tìm kiếm, không mở được): https://www.trmlabs.com/resources/blog/north-korea-steals-usd-6-36-billion-from-binance-in-the-largest-hack-in-history
- [F4] The Block: https://www.theblock.co/news/business/2026-10-30-binance-hack-largest-crypto-hack-north-korea-432225
- [F5] NBC News (Reuters): https://www.nbcnews.com/business/business-news/fbi-says-north-korea-was-6-billion-binance-crypto-hack-rcna606758
- [F6] TechCrunch: https://techcrunch.com/2026/11/01/binance-resumes-withdrawals-following-6-3-billion-breach/
- [F7] CoinDesk: https://www.coindesk.com/policy/2026/10/31/fbi-confirms-north-korea-s-role-in-usd6-billion-binance-hack-asks-defi-community-to-block-btc-eth-sol-addresses
- [F8] The Block (Kim Yo Jong): https://www.theblock.co/news/regulation/2026-11-02-kim-jong-un-sister-rejects-fbi-claims-linking-north-korea-binance-hack-432344
- FBI (403, chỉ qua tìm kiếm): https://www.fbi.gov/investigate/cyber/alerts/2026/north-korea-responsible-for-6-billion-binance-attack
- Elliptic (không mở được): https://www.elliptic.co/insights/binance-largest-hack-in-history/
