# Structured Fact Store v0 (#123)

Nhánh nghiên cứu, không production. PO quyết 03/11: LLM chuyển thông tin phức tạp thành dữ liệu tái sử dụng; Python/n8n làm phần lặp lại; LLM giữ cho việc sáng tạo thật sự cần.

## Thành phần
- `fact_store.schema.json`: một store mỗi chủ đề = sources (có snapshot + sha256) + entities + facts.
- `predicates.json`: từ vựng quan hệ nhỏ, có slot cho NO_LLM và cụm động từ cho Fact Gate.

## Một fact không chỉ là triple
`kind` phân biệt: `assertion` (nguồn khẳng định), `attributed` (X đã nói Y — đúng là X nói, không có nghĩa Y đúng), `variant` (dị bản cùng `variant_group`, vd năm 627 vs 629), `conditional` (đúng khi điều kiện), `tradition` (luật/quan niệm truyền thống: tam tai, ngày kiêng), `legend` (truyền thuyết). `qualifiers` giữ phủ định, modality, người phát biểu, bản nguồn (`according_to_edition`), điều kiện, phạm vi.

Ví dụ:
- Fansipan: hai fact `measured_as` (3.143 m, 1909; 3.147,3 m, 2019) cùng `variant_group=fansipan_height`; **không** có fact `changed` vì nguồn không nói núi cao thêm → câu "núi cao thêm 4 m" không thể PASS.
- Bybit: `compromised(Safe{Wallet} infra, attacker=TraderTraitor)`, `lost_asset(Bybit, ETH ~1,5 tỷ USD)`, `attributed_to_actor(event, North Korea/TraderTraitor, attributed_to=FBI)` → "Bybit bị hack" không khớp `compromised` (subject sai) → REJECT; "Bybit mất 1,5 tỷ USD" khớp `lost_asset` → PASS nếu verified.
- Temiya: `performed(Temiya, giả câm và liệt, duration=16 năm)`, kind=legend/tradition theo kinh, `according_to_edition=Cowell Ja 538` → Sunanda không thể vào slot subject.

## v0.2 (sửa theo review Codex 03/11, FAIL)
- **Tách 2 file**: `facts` (trích xuất, `fact_store.schema.json`) không có trường kiểm chứng; `verification.json` (`verification.schema.json`) chỉ `validator.py` ghi, kèm `store_sha256` của file trích xuất — sửa store là kết quả cũ mất hiệu lực. LLM không có chỗ để tự ghi verified.
- **`certainty`** (yêu cầu PO) ở verification: `established` / `contested` / `uncertain` / `unknown`, tính từ status + `variant_group`/`conflicts_with` + `source_hedge` (mức rào đón CỦA NGUỒN do người trích ghi).
- **Kiểm độc lập máy kiểm được**: `span_match` ghi `snapshot_sha256` + offset; `independent_llm` ghi `model` và `extraction_model` (validator từ chối nếu trùng) + hash prompt; `cross_source` ghi `source_id` + `publisher` (phải khác publisher của evidence gốc).
- **`comparable_group`** cho các lần đo cùng đại lượng khác thời điểm (Fansipan 1909/2019) — không phải tranh chấp, không suy ra thay đổi. `variant_group` chỉ cho các phương án nguồn bất đồng (627/629).
- **Điều kiện có cấu trúc**: `qualifiers.condition` = {text, applies_when[{field, op, value}], outcome} cho luật truyền thống / có điều kiện.
- `legend` bắt buộc `modality=legendary` + `according_to_edition`; `tradition` bắt buộc `modality=traditional`. Validator kiểm `according_to_edition` ∈ source_id của evidence.
- Ràng buộc ngữ nghĩa (source_id tồn tại, predicate trong từ vựng, kiểu subject/object theo predicate) do validator kiểm.
- `gate_verbs` chỉ là gợi ý; từ đa nghĩa (là, thuộc, năm, ở, làm, đi, đến, do, ghi) đã bỏ.

### Hợp đồng Fact Gate (v0.2)
Claim được phân tích thành (subject, predicate, object, quantity, time, polarity, modality, attribution, condition, scope). Parser có thể là luật hoặc LLM; **parser không chắc (thiếu trường, nhiều cách hiểu) → REVIEW**. PASS chỉ khi tồn tại fact `verified` khớp TẤT CẢ: subject (qua aliases), predicate, object/quantity (đơn vị quy đổi, sai số làm tròn), time (nếu claim có), polarity, modality claim **không mạnh hơn** fact (fact traditional/legendary/reported/estimated → claim phải giữ khung tương ứng), attribution (claim nói "X cho rằng" thì attributed_to = X), condition (claim không được bỏ điều kiện), scope. Trái với fact verified (cùng subject + predicate + measure, khác giá trị/vai) → REJECT. Fact `contested` không đứng trong title/thumbnail khi claim khẳng định một phương án.

### Hợp đồng NO_LLM (v0.2)
Template khai báo `predicate` + slot. Chỉ điền từ **một** fact `verified`, `certainty` ∈ {established, uncertain}, đúng predicate, đủ slot; giữ nguyên modality (thêm khung "theo truyền thống", "tương truyền", "theo X"), attribution và condition. Không đủ → abstain. Đầu ra kèm fact_id cho từng slot để Fact Gate kiểm lại.

## Ai được đặt "verified"
- LLM trích xuất **không** ghi trạng thái. Validator tính:
  - `verified` = `span_match` supports (trích dẫn có mặt trong snapshot nguồn, kiểm tất định) **và** ≥ 1 trong: `independent_llm` (model khác model trích xuất) supports, `human` supports, `cross_source` (nguồn độc lập thứ hai) supports; **không** check nào contradicts.
  - `disputed` = có `variant_group`/`conflicts_with` khác giá trị, hoặc checks trái nhau.
  - `rejected` = span không tìm thấy hoặc có contradicts (ưu tiên cao nhất; certainty vẫn có thể là contested nếu fact thuộc variant_group).
  - còn lại `unverified`.

## Dùng ở hạ nguồn
- **Fact Gate**: claim của title/hook được phân tích thành (subject, predicate, object, quantity, time, polarity, modality) — phần phân tích có thể là LLM (semantic review có chọn lọc) hoặc luật; gate so tất định với facts `verified`: cùng subject (qua aliases), cùng predicate (qua `gate_verbs`), cùng object/quantity (đơn vị quy đổi), thời gian khớp, modality không mạnh hơn fact (vd fact `traditional` không được nói thành khẳng định). Chứng minh được → PASS; trái với fact verified → REJECT; còn lại → REVIEW.
- **NO_LLM**: template khai báo predicate + slot; chỉ điền từ đúng một fact verified có predicate đó; không đủ → abstain.

## Pilot (5 chủ đề)
tt05_temiya (kinh, dị bản, bản nguồn khoá) · vsd_fansipan (đo đạc, dị bản số) · ck_bybit_2025 (vai thực thể, quy trách nhiệm) · f19_hue_phong_thuy (diễn giải truyền thống, attributed) · fs_short_ngay_tot_cuoi (luật truyền thống có điều kiện).
Đo: tỉ lệ fact cấu trúc đúng (so kiểm tay một mẫu), claim PASS sai, số REVIEW, số phương án NO_LLM sinh được, chất lượng ngôn ngữ (chấm mù), chi phí LLM thực tế (token/thời gian theo CLI).
