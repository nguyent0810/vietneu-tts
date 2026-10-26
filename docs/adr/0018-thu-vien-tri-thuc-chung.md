# Thư viện tri thức chung hai tầng: bản ghi do thuật toán sinh, thẻ do người duyệt; chỉ áp vào thử nghiệm và dạng thua

Trạng thái: đã chấp nhận (26/10/2026). Epic nguyent0810/vietneu-tts#37.

Tri thức dựng video của kênh đang rải ở nhiều nơi: 6 skill, 18 ADR, `grok/rules.md`, 34 công cụ `hf_*.py`, 28 template, sổ lỗi, memory. Thêm vào đó là các kho tham khảo ngoài (prompt-motion, 3 repo video Opus 5.5). Kênh khác, như Hình Sự ở repo Youtube_Creator_V2, phải xin bài học bằng tay. Ta cần một thư viện chung: tra được theo nhãn, cập nhật bằng máy, sau này tách ra cho nhiều kênh.

## Số đo lúc quyết định

`library/tools/inventory.py` gom 6 nguồn, được 4.125 mục thô. Khử trùng chính xác (cùng post ID, URL chuẩn hoá hoặc hash văn bản) còn 2.872 mục; khử gần trùng (MinHash 5-gram, Jaccard ≥ 0,8) còn **2.766**. Các mục này gom về **137 kỹ thuật dựng**:

| Trạng thái | Số kỹ thuật |
|---|---|
| Kênh đang dùng thật | 57 |
| Có sẵn nhưng chưa dùng | 10 |
| Chưa có | 70 |

Chưa phân loại 14,2%. Chạy 2 lần cùng đầu vào ra cùng kết quả (md5 trùng). Không bước nào gọi LLM.

## Quyết định

1. **Hai tầng.**
   - *Tầng bản ghi:* sinh lại hoàn toàn bằng `inventory.py fetch|build|report`. Mỗi nguồn có một adapter; muốn thêm nguồn thì viết thêm adapter. Không sửa tay.
   - *Tầng thẻ:* mỗi kỹ thuật hoặc đơn vị tri thức là một file md có phần đầu YAML. Phần số liệu (số mục, nguồn, cờ đã dựng, bằng chứng, ví dụ) do máy điền. Phần diễn giải (mô tả, cách dùng, phạm vi, độ hợp ngách) do Codex soạn và Lead duyệt.
2. **Thẻ trỏ tới nguồn sự thật, không chép lại.** Code, skill, template vẫn nằm ở chỗ cũ. Thẻ chỉ mô tả và dẫn tới chúng.
3. **13 loại tri thức:** `canh`, `thiet_bi`, `template`, `khuon`, `kich_ban`, `luat`, `cong_qa`, `quy_trinh`, `cong_cu`, `du_lieu_nguon`, `do_luong`, `bai_hoc`, `tham_khao`.
4. **Chung hay riêng kênh đánh dấu bằng nhãn `pham_vi`** (`chung`, `fs`, `bud`, `cl`…), chưa tách bằng thư mục hay repo. Việc tách để sau cùng (P7).
5. **Cờ "đã dựng" có 3 mức, mỗi mức kèm bằng chứng:** `dung_that` (plan, bản render hoặc builder có gọi tới), `co_san`, `chua_co`. Phần engine được gắn kỹ thuật bằng bảng khai báo tay `engine_map.json`, không dò từ khoá tự do.
6. **Git chỉ giữ dữ liệu khai báo:** taxonomy, `label_map`, `engine_map`, `stopwords`, báo cáo, mẫu soát. `records.jsonl` và `clusters.jsonl` (khoảng 8 MB) sinh lại được nên đưa vào gitignore.
7. **Ràng buộc áp dụng (chủ kênh duyệt 26/10).**
   - Thư viện chỉ được đem áp vào **ô thử nghiệm** và **dạng đang thua hoặc ngang**, xác định theo hf_brief và luật dừng khuôn ở ADR 0017.
   - **Dạng đang thắng giữ nguyên.** Chỉ được đổi khi có đủ hai điều: analytics đi xuống (hạng hoặc view trung vị giảm ≥ 2 tuần sạch liên tiếp so với 4 tuần trước), và đã có phân tích nguyên nhân được chủ kênh duyệt.
   - Bộ chấm ưu tiên và bộ chọn của thư viện phải tự loại các dạng thắng.

## Không chọn

- **Một tầng, viết thẻ tay cho mọi mục:** hàng nghìn mục, không bảo trì nổi, và không chạy được bằng cron.
- **Để LLM gắn nhãn trực tiếp trong pipeline:** kết quả không tất định, tốn token mỗi lần chạy, khó kiểm lại.
- **Tách repo ngay:** ranh giới chung/riêng chưa được kiểm, dễ tách nhầm luật riêng của BUD thành luật chung.

## Hệ quả

- Lộ trình P1–P7 nằm trong epic #37.
- Thêm nguồn mới, kể cả kho 52 mẫu của Hình Sự, chỉ cần viết một adapter.
- Vòng tuần (hf_brief thứ Hai) có thêm hai việc: diff kỹ thuật/nguồn mới, và ghi `bang_chung` vào thẻ.
