# GH-31 · Grok: rà điều khoản và lập danh sách nguồn cho Trend Engine P0

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/31. Thiết kế: `docs/pm/2026-11-02-trend-engine-v1.md` (mục P0). Audit: `docs/pm/2026-11-02-audit-trend.md`.

## Được ghi
- `docs/pm/tickets/GH-31-sources.json`: bản đề xuất; Codex sẽ chép sang `factory/trend/sources.json`
- báo cáo `docs/pm/tickets/GH-31-grok-report.md`

**Không:** sửa code, upload, đổi lịch, đọc credentials, commit.

## Việc
Với mỗi nguồn ứng viên bên dưới, mở trang điều khoản sử dụng hoặc trang RSS của chính nguồn đó, rồi ghi:
- URL feed/API thật, hiện còn chạy;
- `tos_status`:
  - `ok`: điều khoản cho phép đọc tự động tiêu đề và URL làm tín hiệu nội bộ cho một kênh YouTube có kiếm tiền, không đăng lại nội dung;
  - `pending`: điều khoản không rõ;
  - `blocked`: cấm dùng thương mại, cấm tự động hoặc cấm thu thập;
- `tos_note`: trích ≤ 25 từ điều khoản liên quan, kèm URL trang điều khoản;
- `owner_group`: tòa soạn hoặc tập đoàn sở hữu, dùng để lọc nguồn độc lập. Ví dụ: Dân Trí, VnExpress (FPT), Tuổi Trẻ, CafeF và GenK (VCCorp), VnEconomy;
- kênh phù hợp (MIM / CK / cả hai) và giới hạn tần suất gọi nếu điều khoản có nêu.

Nguồn ứng viên:
- RSS báo VN: VnExpress, Tuổi Trẻ, Dân Trí, CafeF, VnEconomy, GenK, Thanh Niên, VietnamNet;
- Google News RSS theo từ khóa (`news.google.com/rss/search?...&hl=vi&gl=VN`);
- Google Trends daily trending RSS VN;
- Hacker News Firebase API;
- Reddit `.json` công khai (r/technology, r/MachineLearning, r/vietnam);
- Wikipedia pageviews API;
- bảng giá SJC và tỷ giá Vietcombank công khai;
- RSS hoặc trang tin của cơ quan nhà nước làm **nguồn sơ cấp**: chinhphu.vn, vanban.chinhphu.vn, sbv.gov.vn, mof.gov.vn, baohiemxahoi.gov.vn;
- nguồn sơ cấp công nghệ: blog OpenAI, Google, Microsoft, Meta, NVIDIA, Apple Newsroom, SEC EDGAR RSS.

Không dùng Google autocomplete. Nếu tìm được nguồn miễn phí khác tốt hơn, thêm vào kèm điều khoản.

## Báo cáo
Bảng nguồn và kết luận. Danh sách `ok` để bật ngay trong P0; danh sách `pending` để chủ kênh quyết.
