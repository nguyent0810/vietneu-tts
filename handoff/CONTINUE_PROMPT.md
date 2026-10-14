# Prompt bàn giao — tiếp tục Phase 4.1

Sao chép nguyên khối dưới đây làm tin nhắn đầu tiên cho agent mới.

---

Tiếp tục Phase 4.1 của Content Hub trong repo này. Commit checkpoint là `33cf1f5`
trên nhánh `feat/content-hub-backend`. Đọc `handoff/PHASE4_1_HANDOFF.md` và
`creator_specs/PHASE4_1_DESIGN_V2.md` trước khi sửa bất cứ gì.

## Bối cảnh ngắn

Tầng này cho Cursor CLI suy luận trên gói bằng chứng tất định của Phase 3. Nguyên
tắc: **thuật toán tính sự kiện, LLM suy luận trên sự kiện**. Mô hình không được
tính lại chỉ số, bịa bằng chứng, hay kết luận nhân quả / CTR khi impressions và
CTR có độ phủ 0% trên cả ba kênh thật.

Schema 2.1 vừa thay `metricClaims[].text` (bản sao) bằng `sourceRef` (tham chiếu
tới ô gốc). Lý do và thiết kế đầy đủ nằm trong hai tài liệu trên.

## Trạng thái hiện tại

* 0 lỗi TypeScript
* 289/299 test đơn vị xanh; **10 lỗi còn lại**
* Migration 0016–0022 đã áp và kiểm trực tiếp trên cả hai database
* Quét bí mật: CLEAN
* **Chưa** viết prompt 3.0.0
* **Chưa** đóng băng, **chưa** chạy lô chính thức

## Việc cần làm, theo thứ tự phụ thuộc

1. **Sửa 10 test còn lại.** Chạy `npx vitest run tests/unit` để xem. Phần lớn cần
   quyết định ngữ nghĩa, không phải sửa cơ học. Ví dụ: câu
   `"Khi có impressions/CTR: so sánh CTR và impressions..."` nay có hai mệnh đề
   nhạy cảm trong một ô nên quy tắc U1 chặn — **đó là hành vi đúng của thiết kế
   mới**, và ca thật đó phải được viết lại thành hai ô. Đừng nới quy tắc để test
   xanh.

2. **Viết prompt 3.0.0** (`src/lib/cursor/prompt.ts`, hiện vẫn là 2.0.0):
   - đặc tả `sourceRef {section, itemId, field, ordinal}` với ví dụ cụ thể
   - danh sách `section`/`field` hợp lệ, **sinh từ schema** như `schemaConstraintLines()`
     đang làm, không viết tay
   - quy tắc "một ô một phát biểu nhạy cảm" kèm ví dụ tách ô
   - giữ nguyên cơ chế sinh ràng buộc từ Zod (đã có, có test bảo vệ)

3. **Thêm ma trận đối kháng 37 ca** — mục 6 của `PHASE4_1_DESIGN_V2.md`. Bổ sung
   bốn ca mà bản thiết kế yêu cầu thêm: văn bản trùng hệt ở hai item khác nhau;
   trùng hệt ở hai section khác nhau; đổi quyền sở hữu (finding → recommendation)
   với nội dung y hệt; trùng nội dung trong cùng field (`AMBIGUOUS_DUPLICATE_TEXT`).

4. **Chứng minh trực tiếp trên CẢ HAI database** (không tin log migration):
   round-trip JSONB cho payload 2.1; CHECK `cursor_result_schema_matches_payload`
   chấp nhận 2.1 và vẫn từ chối payload thiếu `schemaVersion`.

5. **Chạy đủ**: `npx tsc --noEmit`, `npx vitest run`,
   `node verify_schema.mjs`, `python3 scripts/secret_scan.py`.

6. **Rà soát Codex** phạm vi hẹp — mục 7 của `PHASE4_1_DESIGN_V2.md`.
   Lệnh: `codex exec --sandbox read-only "$(cat prompt.md)" < /dev/null > out.log 2>&1`
   **Bắt buộc `< /dev/null`** — thiếu nó Codex treo vô hạn chờ stdin, và vì output
   bị đệm nên trông hệt như đang phân tích. Đã mất nhiều giờ vì lỗi này.

7. **Một** lần thăm dò `hinh_su`. Điều kiện đóng băng: **0 lỗi phân giải (R) và
   0 lỗi đầy đủ (U)**. Lỗi ngữ nghĩa (S) mức thấp thì chấp nhận — lô chính thức
   mới là phép đo.

8. **Đóng băng mới** rồi chạy lô chính thức: 3 kênh × 3 mẫu đạt × trần 6 lần thử,
   một bộ hash duy nhất, không nới trần, không chạy lại để lấy kết quả đẹp.

## Quy tắc bắt buộc

* **Không dùng thay chuỗi diện rộng.** Một lệnh splice hai mốc đã xoá nhầm bảy
  schema mục. Mọi lệnh sửa tệp bằng script phải `assert` mốc tồn tại trước. Sửa
  nhỏ, chạy typecheck sau mỗi nhóm.
* **Tệp chưa commit KHÔNG có mạng an toàn.** `git show HEAD:...` sẽ thất bại và
  nếu nối bằng `&&` thì bước sau im lặng không chạy. Commit sớm.
* **Không nới quy tắc để test xanh.** Nếu một quy tắc chặn oan, sửa cho nó CHÍNH
  XÁC hơn, đừng làm nó dễ dãi hơn. Ghi ca thật vào test.
* **Không gộp "phân giải" với "ủng hộ ngữ nghĩa"** khi báo cáo. Phân giải tham
  chiếu là tất định; đếm mệnh đề nhạy cảm là heuristic ngôn ngữ.
* **Không tin log.** "Migration xong" từng in ra ba lần khi migration chưa chạy.
  Kiểm `information_schema` và `pg_proc.prosrc` trực tiếp.
* **Không commit** cho tới khi qua cổng đầy đủ.

## Mốc so sánh — giữ nguyên, không trộn mẫu

| Lô | hinh_su | phat_giao | phong_thuy |
|---|---|---|---|
| Batch 5 (lexical) | 3/4 | **2/6** | 3/3 |
| Cấu trúc 2.0 | 0/6 | 0/6 | 0/2 (bị ngắt) |

`phat_giao` = 2/6 theo chính sách mốc ngữ nghĩa. **Không an toàn cho vận hành tự
động** trừ khi lô mới có bằng chứng ngược lại rõ ràng. Ba lô vô hiệu và ba lần
thăm dò phải bị loại khỏi mọi mẫu số.

## Giới hạn đã biết, đừng tuyên bố ngược lại

* Ngữ nghĩa bằng chứng: chỉ kiểm cấu trúc (id giải được, cùng lineage, không chu
  trình). **Không** chứng minh được bằng chứng ỦNG HỘ kết luận. Ca không kết luận
  được phát `evidence_support_unverified` mức HIGH và chặn.
* Nguồn gốc là bản ghi có kỷ luật, **không phải attestation**. Băm được tính lúc
  nạp module; không chứng minh runtime đã chạy đúng những byte đó.
* Chi tiết: `creator_specs/PHASE4_TRUST_BOUNDARIES.md`.

## Lệnh hay dùng

```bash
cd apps/hub
npx tsc --noEmit                      # phải 0 lỗi
npx vitest run                        # hiện 10 lỗi cần sửa
node verify_schema.mjs                # migration trên cả hai DB
node attempt_table.mjs <ISO-start>    # bảng lần thử của một lô
npm run cursor -- --channel hinh_su --sandbox /tmp/sb   # thăm dò
```
