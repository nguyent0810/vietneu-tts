# Pilot Structured Fact Store (#123) — 5 chủ đề, 03/11

Chủ đề: tt05_temiya (kinh, bản nguồn khoá) · vsd_fansipan (đo đạc) · ck_bybit_2025 (vai thực thể) · f19_hue_phong_thuy (diễn giải có quy kết) · fs_short_ngay_tot_cuoi (luật truyền thống có điều kiện).

## 1. Dữ kiện có cấu trúc — ĐẠT, đáng dùng
| Chỉ số | Kết quả |
|---|---|
| Nguồn chụp được | 16/16 URL; 3 bản rác do không giải nén gzip (lỗi công cụ tải, sửa được); sacred-texts chặn 403 |
| Fact trích (Sonnet) | 94 |
| Lỗi cấu trúc validator bắt | 3/94 (3,2%): chủ thể sai kiểu, gộp nhầm nhóm so sánh |
| Trích dẫn khớp nguyên văn bản chụp | 100/100 |
| Kiểm độc lập (Codex, khác model) | 79 supports (84%), 15 partial (16%), 0 contradicts |
| Trạng thái cuối | 72 verified · 15 unverified · 7 disputed (dị bản thật: số tiền Bybit 1,5 vs 1,4 tỷ USD; định nghĩa "nguyệt kỵ") |

15 "partial" là đúng loại lỗi cần bắt: LLM trích **nói quá nguồn** (gán quy kết cho Sygnia thay vì FBI/Mandiant; "Thanh Long" gán riêng cồn Hến; "lý do thứ nhất" khi nguồn không xếp thứ tự; Temiya "giả câm suốt 16 năm" khi khung nguồn ±500 ký tự chỉ nói rõ 16 năm không cử động tay chân).

## 2. Chi phí LLM thực tế (một lần ở khâu research, ngoài n8n)
| Bước | Model | Token | Thời gian |
|---|---|---|---|
| Trích fact 5 chủ đề | Claude Sonnet (subagent) | ~200k | ~7 phút |
| Kiểm độc lập 94 fact | Codex CLI | ~127k (11,9k–47k/chủ đề) | ~67 giây |
Trung bình ~65k token/chủ đề cho dữ kiện dùng lại được nhiều video. Validator, khớp trích dẫn, gate, NO_LLM: 0 token.

## 3. Fact Gate v2 trên packaging do Sonnet viết (#114) — CHƯA ĐẠT
| | PASS | REVIEW | REJECT |
|---|---|---|---|
| 15 gói (5 chủ đề × 3 mức) | 0 | 11 gói | 4 gói |
- Parser tất định **không hiểu** phần lớn câu packaging tự nhiên ("Bấm xác nhận…", "Chàng đã đi qua lửa, voi, rắn…") → REVIEW. Đúng hợp đồng (không đoán) nhưng nghĩa là gate tất định một mình không PASS được title thật.
- **Sai 1 (code):** "Temiya: Hoàng Tử Giả Câm Suốt 16 Năm" bị REJECT, lẽ ra REVIEW (fact chưa verified + thiếu khung "tương truyền" chỉ là chưa đủ chứng cứ, không phải trái fact).
- **Sai 2 (mô hình dữ liệu):** "Bybit bị hack" chỉ ra REVIEW, lẽ ra REJECT: fact phủ định nói về `bybit_infra`, claim nói về `bybit`; store chưa có quan hệ `part_of(bybit_infra, bybit)` để gate nối hai thực thể.
- **Quá chặt (cần PO định hướng):** "Bybit mất 1,5 tỷ USD" bị REJECT vì số tiền là dị bản (FBI 1,5 tỷ / CryptoSlate 1,4 tỷ). Cách đúng: claim kèm "theo FBI" hoặc dùng "hơn 400.000 ETH" thì PASS được; nhưng luật hiện tại chặn cả title hợp lý. Tương tự truyện kinh: yêu cầu mọi title có "tương truyền" là quá chặt — nên đặt khung truyền thuyết ở cấp series/kênh (BUD "Truyện Tiền Thân") thay vì từng title.

## 4. NO_LLM v2 — AN TOÀN nhưng NHẠT
| Chủ đề | Phương án | Ví dụ |
|---|---|---|
| Temiya | 1 | "Tương truyền Temiya tên là Temiyakumāra." |
| Fansipan | 1 | "Fansipan cao 3.147,3 m." |
| Bybit | 1 | "Bybit mất 400.000 ETH vào 2025-02-21." (ngày chưa định dạng tiếng Việt) |
| Huế | 1 | "Núi Ngự Bình cao 105 m." |
| Ngày cưới | 4 | "Theo quan niệm, ngày Tam Nương…" |
Không sai vai, không bịa — nhưng chỉ là câu dữ kiện, không có tension. NO_LLM hợp làm **mức safe dự phòng** và dòng mô tả, không thay được phần sáng tạo.

## 5. Kết luận cho quyết định tiếp
1. **Giữ Structured Fact Store** làm nền: LLM trích 1 lần, máy + model khác kiểm, dùng lại cho mọi video của chủ đề. Mở rộng từ vựng quan hệ (35/94 fact phải dùng "other").
2. **Fact Gate cần parser claim có chọn lọc bằng LLM** (đúng mục 6 của PO): LLM chỉ chuyển câu packaging thành claim có cấu trúc; so khớp vẫn tất định với fact verified. Ước tính vài nghìn token/gói.
3. **Hiệu chỉnh 3 điểm quá chặt/sai**: lỗi REJECT Temiya; thêm `part_of` cho thực thể; cho phép claim chọn một dị bản khi có quy kết ("theo FBI"); khung truyền thuyết ở cấp series.
4. **Phần sáng tạo vẫn là LLM** (angle, hook), nhưng mọi claim của nó đi qua gate tất định trên fact verified.
Chưa tích hợp production. Code gate/NO_LLM v2 chưa qua review Codex (sẽ review khi chốt hướng).
