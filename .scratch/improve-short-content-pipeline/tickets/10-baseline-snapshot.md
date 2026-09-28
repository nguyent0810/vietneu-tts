# 10: Baseline snapshot builder + xuất tập gán nhãn

**Spec:** `../spec.md` — Baseline snapshot. Quyết định: D20, D35, D37, D41, D78–D81.

**What to build:** Một lệnh đọc dữ liệu người vận hành đặt trong baseline raw (thư mục output Short từ máy production, export video + metrics theo ngày từ Hub, retention/traffic từ ticket 09, publishing ledger, vi phạm đã biết từ PR-5/audit) và tạo Baseline snapshot có version. Mỗi Short đã đăng là một dòng (domain, category, generator, script nếu có, `hook_score` cũ, views, average view %, retention curve, traffic source, vi phạm CR-1/Safety đã biết); mỗi trường thiếu có lý do. Mỗi Short có `script_provenance` (`exact`/`revision`/`rendered`/`source_only`/`missing`) + trạng thái xác minh (`verified`/`unverified`); `source_only` không bao giờ được ghi vào trường script đã đăng. Kèm thống kê theo Domain (n, median, phân vị average view %, publish/pass rate nếu có) và xuất tập gán nhãn theo D37.

**Blocked by:** 09

**Status:** done (grok review OK)

- [x] Phần ghép là hàm thuần; phần lệnh chỉ đọc/ghi file
- [x] Không tự kết nối Hub DB; chỉ đọc file export
- [x] Mỗi trường thiếu có lý do thiếu (không nhầm với 0)
- [x] Thống kê theo Domain: n, median, phân vị average view %
- [x] `script_provenance` + trạng thái xác minh cho từng Short; `revision` chỉ `verified` khi khớp revision lúc đăng
- [x] Đoạn trích `source_only` lưu ở trường tham chiếu riêng, không bao giờ ở trường script đã đăng; không có text đã publish → script là `Source không đủ`
- [x] Báo cáo số Short theo `script_provenance` và theo Domain (n theo tiêu chí tính sau khi có evaluator, không ghi n chung)
- [x] Không reconstruct bằng ASR hay sinh lại Claim ledger bằng code hiện tại
- [x] Snapshot có version và thời điểm tạo, ghi vào thư mục gitignore
- [x] Xuất tập gán nhãn: FS 10 từ PR-5, BUD 10 gồm 2 video retention 31%/25%, CL đã đăng
- [x] Test với fixture nhỏ cho registry, ledger, metrics, retention, `.srt`/manifest, staged `*_Short.txt`
