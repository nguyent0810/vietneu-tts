# Ticket #119 — Fact Gate tất định (research)

## Eval sau Fix round 1

Lệnh: `python3 -m research.narrative.fact_gate eval research/narrative/bench114 --out /tmp/fact_gate_eval.json`

| Chủ đề | safe | max_defensible | invalid |
|---|---:|---:|---:|
| b18_huyen_trang | REVIEW | REVIEW | REVIEW |
| b19_xa_loi | REVIEW | REVIEW | REVIEW |
| bud26_devadatta | REVIEW | REVIEW | REVIEW |
| bud_short_niem_phat | REVIEW | REVIEW | REJECT |
| ck_bybit_2025 | REVIEW | REJECT | REJECT |
| ck_finance_topic | REVIEW | REVIEW | REJECT |
| f18_ta_ao | REVIEW | REVIEW | REVIEW |
| f19_hue_phong_thuy | REVIEW | REVIEW | REVIEW |
| fs27_cao_bien | REVIEW | REVIEW | REVIEW |
| fs_short_ngay_tot_cuoi | REVIEW | REVIEW | REJECT |
| mim_ai_topic | REVIEW | REVIEW | REVIEW |
| mim_long_topic | REVIEW | REVIEW | REVIEW |
| tt05_temiya | REVIEW | REVIEW | REVIEW |
| tv05_dinh_mui_1967 | REVIEW | REVIEW | REJECT |
| vsd_binh_ngo | REVIEW | REVIEW | REVIEW |
| vsd_fansipan | REVIEW | REJECT | REVIEW |
| vsd_luy_thay | REVIEW | REVIEW | REVIEW |
| vsd_son_doong | REVIEW | REVIEW | REVIEW |
| **Tổng (PASS / REVIEW / REJECT)** | **0 / 18 / 0** | **0 / 16 / 2** | **0 / 13 / 5** |

CLI tổng hợp số PASS / REVIEW / REJECT theo hàng: `safe` 0/18/0, `max_defensible` 0/16/2, `invalid` 0/13/5. JSON chi tiết được ghi qua `--out`.

## Fix round 1

- Claim số/ngày giữ span riêng; số có unit chỉ khớp khi cùng chủ thể câu, unit đã chuẩn hóa và giá trị tương đương. Đổi đơn vị như km↔m được quy đổi; thiếu/không tương thích unit hoặc thiếu chủ thể thì REVIEW. Chỉ REJECT khi có fact verified cùng chủ thể và unit chứng minh giá trị khác.
- `claims[]` chỉ còn là dữ liệu gợi ý và không tham gia tạo PASS.
- Thêm so sánh predicate canonical với quan hệ trong `relations`; các quan hệ claim không được fact bao phủ ở lại REVIEW. `entity_roles` kiểm tra trường hợp gán nhầm hệ thống bị xâm nhập với tổ chức chịu thiệt hại (Bybit/Safe{Wallet}).
- Các động từ thay đổi như “cao thêm”, “tăng”, “giảm”, “mất”, “mọc” là claim về biến đổi; số chênh lệch đơn thuần không chứng minh quá trình biến đổi. Vì thế Fansipan “cao thêm 4,3 m” không PASS.
- Bộ phân tích số đọc các đơn vị tiếng Việt đến tỷ, gồm hàng trăm/nghìn, “linh/lẻ”, biến thể “mốt/tư/lăm” và phần thập phân “phẩy”. Test xác nhận 2019 và 3147,3.
- Eval không có PASS sau khi siết điều kiện; đây là kết quả conservative. Nhiều nội dung chưa có triple hoặc căn cứ chủ thể đủ rõ nên cần REVIEW.

## Kiểm tra

- `python3 -m pytest -q research/narrative/test_fact_gate.py` → **11 passed**.
- Eval CLI chạy thành công trên 18 topic; bảng phía trên là đầu ra sau sửa.
- Thêm test cho fact cùng số nhưng khác entity, declared hint đơn độc, Fansipan tăng độ cao, lệch unit, số đọc tiếng Việt và quan hệ Bybit.

Phạm vi chỉ `research/narrative/`; không sửa production. Không commit/push.
