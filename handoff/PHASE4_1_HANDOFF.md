# Phase 4.1 — Điểm dừng pháp y (forensic checkpoint)

> # VÒNG KHẮC PHỤC 2026-08-07 (subagent) — ĐÃ ĐÓNG F1…F7, H-2, M-1…M-5
>
> Toàn bộ mục §0–§10 bên dưới là bản ghi của vòng TRƯỚC và giữ nguyên để đối
> chiếu. Những gì vòng này làm, và những gì nó PHÁT HIỆN THÊM, nằm ở đây.
>
> ## Đã đóng, có bằng chứng CHẠY
>
> | Mã | Cách chứng minh |
> |---|---|
> | F1 | 6 test: `repairErrors` khác rỗng ở CẢ BỐN `return` sớm |
> | F2 | `scanProseOutsideJson` tách riêng, chạy ĐỘC LẬP với mọi cổng schema |
> | F3 | đối chiếu database CHÍNH: 32 hiện vật một lượt từng bị vứt khỏi tử số |
> | F4 | nhãn `ctr_claim_without_coverage` không tồn tại → `samples` luôn rỗng |
> | F5 | bộ dò tên quy tắc nay đọc CẢ mảng nhiều tên/dòng LẪN phép so `i.rule ===` |
> | F6 | fixture bổ sung hàng MỘT LƯỢT + `exec_id` |
> | F7 | phân biệt NHẮC TÊN với KHẲNG ĐỊNH (xem cảnh báo bên dưới) |
> | H-2 | 12 test tích hợp chạy `verify_phase4.mjs` THẬT qua bộ ghi THẬT |
> | M-1…M-5 | migration 0035 + ma trận phủ + `mixedAcrossBatch` kiểm bằng CHẠY |
> | Ranh giới 0 nghĩa vụ | mục 5 của `PHASE4_TRUST_BOUNDARIES.md`, có test |
>
> ## Khiếm khuyết vòng này TỰ SINH RA rồi tự sửa — đọc kỹ
>
> Truyền thống ba vòng trước tiếp tục: vòng này cũng sinh khiếm khuyết mới.
>
> 1. **`verify_phase4.mjs` so thân bằng `JSON.stringify`** trong khi `payload`
>    đến từ `jsonb`, vốn KHÔNG giữ thứ tự khoá. Cổng sẽ ĐỎ ở MỌI lô lành mạnh.
>    Đã thay bằng so CHUẨN TẮC (`canon`).
> 2. **Backtick trong chú thích SQL** đóng sớm template literal của
>    `attempt_table.mjs` — tệp không chạy nổi, và **toàn bộ bộ test vẫn xanh** vì
>    không test nào THỰC THI tệp đó. Đã thêm test `node --check`. Xảy ra HAI LẦN
>    (lần hai ở `verify_phase4.mjs`).
> 3. **Ghim `CURSOR_AGENT_PATH` làm hỏng cách ly của `cursor-exec.test.ts`**:
>    `tests/setup.ts` nạp `.env.local`, và override có ưu tiên cao hơn PATH — sáu
>    test gọi Cursor CLI THẬT và đốt hạn mức thật. Bộ test trước đó chỉ đúng nhờ
>    MAY MẮN là chưa ai ghim biến này.
> 4. **Bản đầu của F7 sai CẢ HAI CHIỀU.** Danh sách "dấu hiệu khẳng định" bỏ lọt
>    `CTR đang thấp`; đảo thành danh sách loại trừ thì `CTR đang thấp và tôi
>    tránh kết luận thêm` lại được tha. Bản cuối đòi HAI điều kiện và dùng
>    `CTR_CLAIM_PATTERNS` — bộ dò hai chiều CÓ SẴN trong tệp mà **chưa từng được
>    gọi ở đâu**.
>
> ## Vòng rà soát đối kháng (4 subagent) — mọi BLOCKER/HIGH đã tự kiểm chứng lại
>
> | Mã | Nội dung | Xử lý |
> |---|---|---|
> | B1 | nhánh `!json` của vòng chạy KHÔNG gọi bộ kiểm định → văn xuôi bị vứt, lớp `INVALID_JSON` (thử lại được) | **ĐÃ SỬA** (`validateProseOnly`) |
> | B2 | `verify_phase4.mjs` PART ONE join `analysis_validation` KHÔNG lọc chặng → chấm điểm bằng phán quyết SAI CHẶNG | **ĐÃ SỬA** (LATERAL + `stage DESC`) |
> | B3 | PART TWO thoát 0 khi kênh KHÔNG có hiện vật nào được cấp phép | **ĐÃ SỬA** |
> | H1 | `PROSE_SELF_DISCLAIMER` bị phá bằng một mệnh đề chứa cả khẳng định lẫn lời từ chối | **ĐÃ SỬA** |
> | H2 | lượt KHAI BÁO vứt `proseText` — hợp đồng "chỉ một object JSON" không được cưỡng chế ở lượt 2 | **ĐÃ SỬA** |
> | H3 | ghép hiện vật ↔ danh tính theo VỊ TRÍ, `files` đến từ `readdirSync` (không sắp xếp) | **ĐÃ SỬA** (ghép theo `resultId`) |
> | H4 | sentinel `'unavailable'` được chép sang mọi bề mặt → mọi phép so vẫn xanh | **ĐÃ SỬA** |
> | H5 | chặng hợp nhất KHÔNG tái sinh tập nghĩa vụ → `allowedAssertionStatuses` là đầu vào TIN CẬY | **ĐÃ SỬA** |
> | H6 | `verify_schema.mjs` không phủ 5 cột của 0035 | **ĐÃ SỬA** (danh sách cột CHO PHÉP NULL riêng) |
> | H7 | test "KHÔNG trùng lặp" là `0 === 0`; chốt `drained` không thể chạm tới | **ĐÃ SỬA** (test chạy trên payload CÓ vi phạm) |
>
> ## CÒN MỞ — mức MEDIUM, phải xử trước lô chính thức
>
> * **B-M2** đường một lượt là đường cấp phép KHÔNG có trần: hai trigger duy nhất
>   tính đều `RETURN NEW` khi `analysis_execution_id IS NULL`. N execution vai
>   ANALYSIS ⇒ N hiện vật "chính thức" cho cùng một kênh. Đây là hình dạng của 32
>   hàng đang có trong database CHÍNH.
> * **C-M2** năm băm của 0035 chưa được so artifact↔DB; `mixedAcrossBatch` báo
>   "sạch" khi một cột NULL trên MỌI hàng.
> * **C-M5** `obligation_count` NULL làm tắt cảnh báo "bộ dò không thấy gì".
> * **C-M6** `attempt_table.mjs` đọc `idx.promptVersion` — `buildIndexJson` không
>   hề sinh trường đó.
> * **A-M2** năm khối trong `validate.ts` là mã CHẾT kèm ~130 dòng chú thích mô tả
>   cơ chế không còn chạy (`mentionsMissingness`, `INSTEAD_OF`, `isInterrogative`,
>   `isConditional`, `textFields`).
> * **Ma trận phủ tự thoả mãn**: `provenance-matrix.test.ts` dựng bề mặt bằng cách
>   lặp chính `spec.required`, nên THÊM trường vào ma trận không bao giờ làm đỏ
>   test của chính nó.
>
> ## Ghim runtime
>
> ```
> CURSOR_AGENT_PATH=/Users/nguyenthanhtung/.local/share/cursor-agent/versions/2026.08.04-aaa8809/cursor-agent
> ```
>
> Launcher 1074 byte có băm GIỐNG HỆT ở cả hai bản đã cài
> (`eed61c5224668c92…`) — đã kiểm lại trong vòng này. **Chỉ ĐƯỜNG DẪN phân biệt
> được chúng.** Số đo của bản `2026.07.23-e383d2b` KHÔNG được gộp.
>
> `OBLIGATION_GENERATOR_VERSION` **1.0 → 1.1** vì `sensitive.ts` nhận thêm
> "ảnh bìa"/"hình bìa". Số đo trước và sau ranh giới này KHÔNG được gộp.
>
> ## CỔNG PHASE 4.1 — LẦN CHẠY HỢP LỆ 2026-08-07
>
> Cây mã ĐỨNG YÊN suốt lần chạy; dấu vân tay TRƯỚC và SAU giống hệt nhau ở cả
> sáu trường, và nó phủ **cả tệp đã theo dõi lẫn 65 tệp chưa theo dõi** (nội dung
> + mtime) — nên sáu tệp quyết định ngữ nghĩa chưa-được-git-theo-dõi cũng nằm
> trong bằng chứng.
>
> ```
> HEAD=0ae2bb818387f0d01d207d02fa66a4c6200b226c
> TRACKED_DIFF=49106dc824d1b772a0b8fed266c4feb7c9cc323866ce0c8f0ec7264dd43b5d22
> UNTRACKED_COUNT=65
> UNTRACKED_CONTENT=e9bed62cd91e6373ca7368827b2f09c1fd1ee6a0df2c7ecc47ea938b6417658f
> UNTRACKED_MTIME=e97815a5cbe01c5e38afc20cfec6b1f9e9c952c4ec2e42da0354b0bbfe94a6cd
> TRACKED_MTIME=2fe2b3c87e14914c425a5d2fcca19cb76d15e5d4723653d7de437ad5aef6af4c
> ```
>
> | Bước | Kết quả |
> |---|---|
> | Độc quyền database TEST | 0 tiến trình vitest, 0 tiến trình cursor-agent |
> | `npx tsc --noEmit` | 0 lỗi |
> | `verify_schema.mjs` MAIN / TEST | ĐẠT / ĐẠT (hai database giống hệt) |
> | `verify_migrations_g8.mjs` MAIN / TEST | ĐẠT / ĐẠT |
> | `secret_scan.py` | CLEAN — 0 phát hiện / 483 tệp |
> | `npx vitest run` | **818/818 xanh, 32 tệp** |
> | Cú pháp 5 công cụ cổng | `node --check` ĐẠT cả năm |
> | Cây đứng yên trước/sau | **ĐẠT** |
>
> **Một lần chạy TRƯỚC đó đã bị VÔ HIỆU và không được dùng làm bằng chứng:** một
> phiên Claude Code KHÁC (dự án `Automation-nextgen-bindup`) chạy song song trên
> cùng máy, load average lên 10.35, và lần chạy ấy hỏng vì lỗi TRUYỀN TẢI
> (`Connection terminated unexpectedly`, `fetch failed`) chứ không phải vì mã —
> `schema.test.ts` mất 2,75 GIỜ so với ~30 giây bình thường. Hai tệp có vẻ hỏng
> "thật" trong lần ấy đều XANH khi chạy riêng (36/36). Bài học bổ sung cho mục
> 10: **độc quyền database TEST là CẦN nhưng CHƯA ĐỦ — máy cũng phải rảnh.**
>
> Phép kiểm độc quyền của chính script cổng cũng từng báo động giả: shell của máy
> này alias `grep` sang `ugrep`, và `ps aux | grep -c '[v]itest'` tự khớp chính
> dòng lệnh ugrep. Đã đổi sang `ps -Ao command | awk`.
>
> ## CHIẾN DỊCH RÀ SOÁT CODEX — 20 VÒNG, 2026-08-11..12
>
> Hạn mức Codex đã mở lại (mốc 2026-08-10 trong bản ghi cũ đã qua). Cổng bắt buộc
> đã chạy **20 vòng** `codex exec` ở chế độ sandbox CHỈ ĐỌC, mỗi vòng trên đúng
> cây đã qua cổng, mỗi phát hiện được TỰ KIỂM CHỨNG LẠI trước khi sửa, và mỗi bản
> sửa kèm test làm ĐỎ khi dòng mã nó bảo vệ bị xoá.
>
> **Tổng: 13 BLOCKER + 12 HIGH + 6 MEDIUM đã đóng.**
>
> ### Vòng cuối chạy được (R20): **0 BLOCKER**, 1 HIGH — đã sửa
>
> R20 HIGH: câu truy vấn hiện vật của PHẦN HAI chỉ ràng buộc `r.id`, còn phép
> chống-cũ chỉ nhìn mtime của TỆP — nên một `INDEX.json` trỏ tới hàng COMPOSITE
> hợp lệ nhưng CŨ của cùng kênh, kèm tệp vừa ghi lại, đi qua được cả hai nửa.
> Đã thêm `JOIN llm_execution e2 ON e2.id = r.llm_execution_id AND e2.created_at >= $2`
> và một test dời execution lùi 400 ngày để chứng minh cổng ĐỎ.
>
> ### ⛔ VÒNG 21 KHÔNG CHẠY ĐƯỢC — hạn mức Codex cạn, mở lại **2026-08-18**
>
> Nghĩa là: **bản sửa R20 CHƯA được Codex rà soát lại.** Nó có test riêng và đã
> qua cổng đầy đủ, nhưng nó là thay đổi DUY NHẤT chưa đi qua một vòng rà soát độc
> lập. Vòng đầu tiên sau 2026-08-18 phải bắt đầu từ đúng chỗ đó.
>
> ### Hai bất đồng đã giải quyết bằng lập luận, không bằng phục tùng
>
> * **R11 (BỊ TỪ CHỐI).** Codex đòi coi khẳng định nhạy cảm trong một Ô PHÂN TÍCH
>   hợp lệ của payload hỏng schema là thất bại vĩnh viễn. Từ chối, vì ở chặng
>   ANALYSIS U3 cho ô TRONG JSON bị lọc bỏ CÓ CHỦ ĐÍCH — ô nhạy cảm chưa khai là
>   ĐẦU VÀO của bộ sinh nghĩa vụ, không phải vi phạm. Codex **chấp nhận** lập luận
>   ở R12. Ranh giới ấy nay có test khoá cả hai chiều.
> * **R15 (CHẤP NHẬN, KHÔNG SỬA BẰNG MÃ).** Không thể cưỡng chế
>   `cursor_declaration_result.payload_hash` ở tầng database mà không viết lại
>   `stableStringify` bằng SQL — tức bản cài đặt THỨ HAI của một định nghĩa, đúng
>   khuôn mẫu đã sinh ra F4, khoảng trống "ảnh bìa" và lỗ bí danh `CTR_SUBJECT`.
>   Đã ghi thành mục 5/6 của `PHASE4_TRUST_BOUNDARIES.md`. Codex **không phản đối**.
>
> ### Nguyên tắc rút ra, đã cưỡng chế bằng mã
>
> **Mọi đường phân loại thất bại từ output của mô hình phải quét MỌI thứ mô hình
> đã phát ra.** Chín vòng liên tiếp tìm ra các thể hiện hẹp dần của đúng nguyên
> tắc này. Nay nó được nối vào: `validateCursorOutput` (return sớm + quét theo Ô),
> `validateAnalysisOutput` (nhánh vòng hỏng hình dạng), `validateDeclarationOutput`
> (parse hỏng, schema hỏng, và return cuối), và `validateProseOnly` (cả bốn lời gọi
> trong `run.ts`, gồm hai nhánh `execFailure`, có cờ phân biệt lượt).
>
> Hai bài học phụ, cả hai đều là lỗi do CHÍNH VÒNG NÀY tự tạo rồi tự sửa:
> * Danh sách từ vựng KHÔNG chặn được không gian vô hạn. Ba lần liên tiếp bị phá
>   (tính từ → số → số viết bằng chữ) trước khi đổi sang phép thử ĐÓNG.
> * Mọi danh sách viết tay song song với schema đều lệch. `CTR_SUBJECT`,
>   `ANALYSIS_SCHEMA_KEYS` đều lệch ngay lần đầu; cả hai nay sinh TỪ nguồn duy nhất.
>
> ### Bằng chứng cổng của cây hiện tại
>
> `tsc` 0 · `verify_schema` MAIN+TEST ĐẠT · `verify_migrations` MAIN+TEST ĐẠT ·
> `secret_scan` CLEAN · **862/862 test** · cây đứng yên trước/sau (phủ cả 65 tệp
> chưa theo dõi). Migration 0036 + 0037 đã áp và đã kiểm trên CẢ HAI database.
>
> ## Vẫn CHƯA làm
>
> * Rà soát **Codex** bắt buộc (hết hạn mức tới **2026-08-10**). Cổng subagent
>   YẾU HƠN và không thay thế được.
> * Một lần **thăm dò MỚI** cho R=0, U=0, 0 SYSTEM_OR_INTEGRITY.
> * Sáu tệp quyết định ngữ nghĩa vẫn **chưa được git theo dõi**, nên
>   `gitDirtyDiffHash` mù với chúng.


> # ⛔ TRẠNG THÁI 2026-08-07T03:16Z — CÂY MÃ **KHÔNG AN TOÀN ĐỂ ĐÓNG BĂNG**
>
> Đọc hết mục này trước khi chạm vào bất cứ thứ gì. Có **2 phát hiện mức HIGH
> đang MỞ**, một phát hiện **sửa dở**, và **không có kết quả cổng nào còn hiệu
> lực**. Không đóng băng, không chạy lô chính thức, không commit.

## 0. Vị trí hiện tại

| Mục | Giá trị |
|---|---|
| Nhánh | `feat/content-hub-backend` |
| HEAD | `0ae2bb818387f0d01d207d02fa66a4c6200b226c` |
| Băm diff `apps/hub` | `8a4d9d6cd714b68df57dc035c9b6f0f6d106fc5ab82cbf1437276caac0eb8c94` |
| Migration | 0000–**0034**, journal 35 mục, đã áp trên **cả hai** database |
| Commit gần nhất của Phase 4.1 | `da7853e` — **TRUNG GIAN, chưa qua cổng** (xem mục cũ bên dưới) |
| Đã commit gì trong vòng này? | **KHÔNG.** Toàn bộ nằm ở working tree |

HEAD `0ae2bb8` **không phải** công việc của Phase 4.1. Đó là bốn commit của một
phiên SONG SONG (pipeline TTS: BGM, karaoke, chunk cache) chồng lên `da7853e`.
`git diff da7853e..HEAD -- apps/hub` rỗng — chúng không chạm Content Hub.

### Worktree cách ly

```
/private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/\
1c744401-70c9-42e1-8f33-a85df8160330/freeze-wt   (detached 0ae2bb8)
```

Được lập vì phiên song song liên tục sửa cây chính (băm diff đổi **hai lần**
giữa một lần chạy cổng). `node_modules` là symlink về checkout chính — một lần
`npm install` song song vẫn đổi được dependency; `lockfileHash` phát hiện được,
không ngăn được.

## 1. Sự cố NGHIÊM TRỌNG về quy trình — đọc kỹ

**Tôi đã tự làm hỏng cổng của chính mình.** Tôi chạy cổng đầy đủ trong worktree
ở nền, rồi ĐỒNG THỜI chạy các bộ test tích hợp từ checkout chính — cả hai trỏ
vào **cùng một `TEST_DATABASE_URL`**, và cả hai đều gọi `truncateAll`. Chúng xoá
dữ liệu của nhau: **83 test hỏng trên 4 tệp**, toàn bộ là lỗi giả
(`channel_workspace_id_workspace_id_fk`, `algorithm_key_key` trùng khoá).

`vitest.config.ts` đã đặt `fileParallelism: false` và `sequence.concurrent:
false` — nó bảo vệ TRONG một lần chạy, không bảo vệ giữa HAI tiến trình.

**YÊU CẦU BẮT BUỘC:** khi chạy bất kỳ cổng nào, phải **độc quyền** database TEST.
Không chạy vitest ở nơi khác, không để subagent chạy vitest song song. Reviewer B
độc lập cũng vấp đúng lỗi này và tự chẩn ra — nên đây là bẫy có thật, không phải
sơ suất một lần.

> Nếu một lần chạy cổng XANH trong khi có tiến trình khác chạm database TEST,
> kết quả ấy **vô hiệu**, không phải "may mà xanh".

## 2. Cổng ĐÃ HOÀN TẤT (còn hiệu lực về mặt cài đặt)

| Cổng | Nội dung | Trạng thái |
|---|---|---|
| G1 | schema hai lượt + vai execution | XONG |
| G2 | bộ sinh nghĩa vụ + băm bất biến | XONG |
| G3 | lưu trữ + migration 0023–0026 (quy trình 7.1 cho 0025) | XONG |
| G4 | hai prompt + vòng chạy hai lượt | XONG |
| G5 | chặng hợp nhất + cấp phép kết quả chính thức | XONG |
| G6 | phân loại thất bại + thử lại chỉ-khai-báo | XONG |
| G7 | ma trận phủ nguồn gốc, 12 bề mặt | XONG |
| G8 | rà soát đối kháng Codex (4 lượt) | XONG — 1 BLOCKER + 7 HIGH + 1 MEDIUM, đã sửa |
| G-R1..G-R5 | khắc phục sau rà soát subagent vòng 1 | XONG (nhưng xem mục 5) |

### Migration 0023–0034

| # | Nội dung |
|---|---|
| 0023 | vai execution + hợp đồng phiên bản |
| 0024 | bảng nghĩa vụ khai báo |
| 0025 | chặng kiểm định (rủi ro cao — quy trình 7.1) |
| 0026 | cổng vai kết quả + hợp nhất |
| 0027 | bản khai + phán quyết hợp nhất |
| 0028 | MỘT phán quyết ĐẠT / lượt phân tích (trượt vẫn lưu tự do) |
| 0029 | *(thừa — trùng trigger cũ)* |
| 0030 | gỡ trigger thừa của 0029 |
| 0031 | khoá chống đua + lineage + trần lần thử theo SỐ HÀNG |
| 0032 | sửa 0031 làm quá tay (chặn nhầm đường ghi cũ; trigger che chẩn đoán) |
| 0033 | thu hẹp phép kiểm bản khai về đúng vai DECLARATION |
| 0034 | **bản kê execution BẤT BIẾN** (UPDATE + DELETE) |

Bài học lặp ba lần (0029→0030, 0031→0032→0033): **một ràng buộc mới phải nêu rõ
nó áp cho ĐƯỜNG CHẠY NÀO trước khi viết dòng SQL đầu tiên** — cây mã mang cả
kiến trúc một lượt lẫn hai lượt, và `analysis_validation.stage` có DEFAULT
`'COMPOSITE'` nên đường cũ lặng lẽ rơi vào phạm vi quy tắc mới.

## 3. Lô đo và thăm dò — CHÍNH SÁCH LOẠI TRỪ

**Không lô nào dưới đây được vào bất kỳ mẫu số chính thức nào.**

| Lô / thăm dò | Vì sao loại |
|---|---|
| 3 lô rỗng (void) trước đó | hợp đồng cũ |
| 4 thăm dò `hinh_su` prompt 3.0.0 | trước kiến trúc hai lượt |
| Thăm dò 2026-08-06 (hai lượt) | **PROBE SEMANTIC FAIL** — xem dưới |
| Mọi số đo trước 0034 | ràng buộc cấp phép đã đổi |

### Thăm dò 2026-08-06 — kết luận cuối

`PROBE SEMANTIC FAIL — architecture works, model analysis failed`

* R = 0 (151/151 bằng chứng neo được, tỉ lệ 1.0000)
* U = 0 (không lỗi đầy đủ nào)
* Hỏng vì **1 BLOCKER `causal_claim` + 1 HIGH `selfcheck_contradicted`** — mô
  hình viết một câu nhân quả rồi tự khai là không có.
* SYSTEM_OR_INTEGRITY = 0. Kiến trúc chạy đúng; mô hình sai.
* Một lần thử duy nhất là **đúng thiết kế**: `UNSUPPORTED_CLAIM` không nằm trong
  `RETRYABLE` ở chặng phân tích.
* **KHÔNG được chỉnh schema/prompt/validator/heuristic vì lần hỏng này.**

**Cảnh báo runtime:** thăm dò chạy `cursor-agent 2026.07.23-e383d2b`; hiện máy
phân giải `2026.08.04-aaa8809`. Launcher 1074 byte có băm GIỐNG HỆT ở cả hai bản
(`eed61c5224668c92`) — chỉ ĐƯỜNG DẪN phân biệt được. Số đo của thăm dò **không
được gộp** với bất kỳ lô nào chạy bằng bản mới.

## 4. Rà soát subagent — kết quả và xử lý

Codex bị **hết hạn mức tới 2026-08-10**, nên dùng 4 subagent độc lập làm cổng
tạm. **Đây là cổng YẾU HƠN Codex** (cùng họ mô hình, cùng điểm mù) — không được
coi kết quả xanh của nó là tương đương.

### Vòng 1 — 1 BLOCKER + 8 HIGH, tất cả đã tự kiểm chứng lại

| Mã | Nội dung | Xử lý |
|---|---|---|
| A-1 | `accountAttempts` nhận khoá `null` → tử số phồng: 3 bài phân tích đạt + 2 hiện vật ⇒ báo `authorized=3` | **ĐÃ SỬA** (G-R1) |
| A-2 | nhãn dòng sửa lỗi trỏ quy tắc KHÔNG tồn tại → vi phạm thật không có hướng dẫn | **ĐÃ SỬA** (G-R2) |
| A-3 | lọc theo chặng xoá vi phạm ngoài JSON + đổi lớp sang RETRYABLE | **ĐÃ SỬA** (G-R2) |
| B-1 | 0 nghĩa vụ ⇒ `SUCCEEDED` không qua cấp phép | **ĐÃ SỬA** (G-R3) |
| C-1 | `sensitive.ts` không được băm | **ĐÃ SỬA** (G-R4) |
| C-2 | `_meta` mất `llmExecutionId` | **ĐÃ SỬA** (G-R4) |
| C-3 | thiếu `INDEX.json` không làm hỏng cổng | **ĐÃ SỬA** (G-R4) |
| C-4 | trộn băm mã nguồn không bị phát hiện ở mức lô | **ĐÃ SỬA** (G-R4) |
| D-1 | bản kê execution sửa/xoá được ⇒ vượt trần + xoá bằng chứng | **ĐÃ SỬA** (G-R5, migration 0034) |

### Vòng 2 — kiểm tra chính bản khắc phục

* **D: sạch.** Không BLOCKER/HIGH. Xác nhận 0034 đúng `tgtype=27`, `prosrc`
  giống hệt hai database, không mất trigger cũ, test là ghi thật.
* **B: sạch về kiến trúc.** Không phá được G-R3. Xác nhận mọi tính chất cũ còn
  nguyên. Một HIGH của B trùng H-1 của C (đã sửa).
* **C: 2 HIGH mới** (H-1 đã sửa, H-2 sửa dở) + 5 MEDIUM.
* **A: 2 HIGH mới** (F1 — hồi quy do chính G-R2; F2 — có sẵn) + 5 MEDIUM.

## 5. ĐANG MỞ — phải đóng trước khi nghĩ tới đóng băng

### F1 — HIGH — hồi quy do G-R2 gây ra
`src/lib/cursor/validate.ts`. `pushRepair` ghi vào `repairSources`, nhưng vòng
đổ sang `repairErrors` nằm ở **dòng 1944**, trong khi bốn `return` sớm ở **829,
866, 880, 900** trả `repairErrors` trước đó ⇒ luôn rỗng.
`INVALID_JSON` / `UNSUPPORTED_SCHEMA_VERSION` / `MISSING_REQUIRED_FIELD` đều
**nằm trong `RETRYABLE`**, nên lần thử 2–3 chạy với prompt sửa lỗi **không nêu
lỗi nào** — đốt ngân sách thử lại vào phỏng đoán mù.
*Hướng sửa:* đổ `repairSources` → `repairErrors` ngay trước MỌI `return`, hoặc
gom các `return` sớm qua một helper. **Phải kiểm bằng cách CHẠY, không đọc mã.**

### F2 — HIGH — có sẵn, fail-open
Khi thân JSON hỏng schema lượt 1, `validateAnalysisOutput` trả về từ nhánh riêng
của nó và **`validateCursorOutput` không bao giờ chạy** — mà đó là nơi DUY NHẤT
quét văn bản ngoài JSON. Một câu nhân quả + một khẳng định CTR nằm ngoài JSON
biến mất không dấu vết, lớp là `MISSING_REQUIRED_FIELD` (RETRYABLE).
*Cần quyết định thiết kế:* quét văn xuôi phải chạy TRƯỚC hay ĐỘC LẬP với cổng
schema lượt 1.

### H-2 — HIGH — SỬA DỞ
`verify_phase4.mjs` đã viết lại cho hợp đồng hai lượt (lái theo `INDEX.json`,
neo 18 trường danh tính, gỡ `_meta` ở CẢ HAI phía trước khi so thân, ép hợp đồng
tên tệp `.sN`, phát hiện hiện vật mồ côi, "không thấy gì" LUÔN là trượt).
**Chưa có test tích hợp nào chạy qua bộ ghi thật** ⇒ chưa được coi là hoạt động.
Yêu cầu còn thiếu: artifact lành mạnh ĐẠT; sai resultId TRƯỢT; sai id khai báo
TRƯỢT; băm payload cũ TRƯỢT; thiếu tệp `.sN` TRƯỢT; tên tệp cũ KHÔNG được vô
tình thoả.

### F3 — MEDIUM — cũng do G-R1 gây ra
Bộ lọc bỏ khoá `null` vứt luôn hiện vật chính thức **một lượt** hợp lệ (0026 ghi
nhận MAIN có 32 hàng như vậy, và cố ý giữ hợp lệ). Khoá đúng là
`analysis_execution_id ?? exec_id`.

### F4–F7 — MEDIUM
* **F4** dòng hướng dẫn CTR vẫn chọn excerpt bằng tên quy tắc không tồn tại ⇒
  không bao giờ trích câu vi phạm; và văn bản "độ phủ 0%" có thể SAI SỰ THẬT.
* **F5** test nhãn tĩnh chỉ đọc tên ĐẦU TIÊN mỗi dòng ⇒ 2/3 nhãn nhân quả không
  được kiểm; cũng không nhìn `i.rule === '...'`.
* **F6** fixture `realRows` mô hình một hàng SQL không trả về được, và **thiếu**
  hàng mà nó thật sự trả về (một lượt) — đây chính là lý do F3 vô hình.
* **F7** một lời nhắc **vô hại** về chỉ số nhạy cảm trong văn bản ngoài JSON nay
  thành thất bại nội dung KHÔNG thử lại được (chặn quá tay, do A-3).

### MEDIUM về nguồn gốc (reviewer C)
* **M-1** `compositeSchemaVersion` có trên 3 bề mặt nhưng ma trận không đòi và
  không so.
* **M-2** ma trận **vẫn không đòi** `llmExecutionId` trên `artifactMeta` — đúng
  trường mà C-2 nói tới; chỉ một assertion tay giữ nó.
* **M-3** ba băm mới **không có cột database** ⇒ `attempt_table.mjs` không so
  được ở mức lô. Sửa `sensitive.ts` giữa hai kênh vẫn **không bị phát hiện**,
  chỉ được *ghi lại*.
* **M-4** assertion C-4 cho `prompt_source_hash` **không thể sai** (đã chứng minh
  bằng mutation: xoá dòng kiểm thật, test vẫn xanh).
* **M-5** `INDEX.json` một kênh ghi đè chỉ mục ⇒ hiện vật kênh khác thành mồ côi
  không ai đối chiếu.

### Hệ quả cần ghi vào TRUST_BOUNDARIES (reviewer B, Finding 3)
`sensitive.ts` **thiếu "ảnh bìa"** — từ phổ biến nhất cho thumbnail.
TRƯỚC G-R3: đầu vào như vậy short-circuit, `resultId: null`, bị loại khỏi mọi
mẫu số. SAU G-R3: nó sinh ra **hiện vật chính thức đầy đủ giấy tờ** với
`obligationCount: 0`, đọc như "phân tích sạch" thay vì "bộ dò không thấy gì".
Bản sửa đúng khi bỏ đường cấp phép thứ hai; nó **không** thêm phép kiểm độc lập
nào cho ca mà nó vừa cấp phép.

## 6. Thứ tự khắc phục còn lại

1. **F1** — nhỏ, rõ. Sửa rồi CHẠY để chứng minh `repairErrors` khác rỗng ở cả
   bốn `return` sớm.
2. **F3** — đổi khoá sang `analysis_execution_id ?? exec_id`; thêm fixture hàng
   MỘT LƯỢT (`execution_role: ANALYSIS`, `result_role: COMPOSITE`,
   `analysis_execution_id: null`) — chính hàng F6 còn thiếu.
3. **F2** — cần quyết định thiết kế trước khi viết mã.
4. **H-2** — 6 test tích hợp qua bộ ghi thật.
5. **F4, F5, F6, F7** rồi **M-1…M-5**.
6. Ghi hệ quả "ảnh bìa" vào `creator_specs/PHASE4_TRUST_BOUNDARIES.md`.
7. Ghim `CURSOR_AGENT_PATH`.
8. Chạy lại **4 subagent** trên đúng diff cuối.
9. Khi Codex có hạn mức (**2026-08-10**): rà soát Codex bắt buộc. Không thay thế
   được bằng tự rà soát.

## 7. Điều kiện BẮT BUỘC trước khi đóng băng

* 0 BLOCKER, 0 HIGH đang mở (subagent **và** Codex).
* Một lần chạy cổng đầy đủ **hợp lệ**, độc quyền database TEST, cây đứng yên:
  `HEAD`, băm diff, băm nội dung untracked và mtime **giống hệt trước/sau**.
* `verify_phase4.mjs` và `attempt_table.mjs` chạy THẬT và ĐẠT.
* `CURSOR_AGENT_PATH` đã ghim; số đo không trộn hai bản runtime.
* Một lần thăm dò MỚI cho **R=0 và U=0** và **0 SYSTEM_OR_INTEGRITY**.
* Đồng thuận nguồn gốc đầy đủ trên 12 bề mặt.
* Chỉ khi ấy: commit đóng băng MỚI, rồi lô chính thức 3 kênh × 3 mẫu, trần 6.

## 8. Lệnh một agent MỚI nên chạy đầu tiên

> Bảo đảm **không tiến trình nào khác** chạm database TEST trước khi chạy.

```bash
cd "/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS"
git rev-parse HEAD                                    # kỳ vọng 0ae2bb8...
git diff HEAD -- apps/hub | shasum -a 256             # kỳ vọng 8a4d9d6c...
cd apps/hub
npx tsc --noEmit                                      # kỳ vọng 0
node verify_schema.mjs        && node verify_schema.mjs TEST
node verify_migrations_g8.mjs MAIN && node verify_migrations_g8.mjs TEST
python3 ../../scripts/secret_scan.py
```

Kiểm F1 còn mở (phải thấy `repairErrors` RỖNG — tức lỗi CHƯA sửa):

```bash
cd apps/hub && grep -n "for (const src of repairSources)" src/lib/cursor/validate.ts
grep -n "return { report: emptyReport(), output: null, failureClass: 'INVALID_JSON'" src/lib/cursor/validate.ts
```

**KHÔNG** chạy `npm run cursor` (đó là thăm dò). **KHÔNG** commit.

## 9. Tệp đang thay đổi

### Đã theo dõi, có sửa (19)
```
apps/hub/attempt_table.mjs                     apps/hub/src/lib/cursor/run.ts
apps/hub/drizzle/meta/_journal.json            apps/hub/src/lib/cursor/schema.ts
apps/hub/package.json                          apps/hub/src/lib/cursor/source-ref.ts
apps/hub/src/db/cursor-stability.ts            apps/hub/src/lib/cursor/validate.ts
apps/hub/src/db/run-cursor.ts                  apps/hub/tests/integration/cursor-persistence.test.ts
apps/hub/src/db/schema/cursor-analysis.ts      apps/hub/tests/unit/cursor-adversarial.test.ts
apps/hub/src/lib/cursor/prompt.ts              apps/hub/tests/unit/cursor-baseline.test.ts
apps/hub/verify_phase4.mjs                     apps/hub/tests/unit/cursor-validate.test.ts
apps/hub/verify_schema.mjs                     creator_specs/PHASE4_TRUST_BOUNDARIES.md
handoff/PHASE4_1_HANDOFF.md
```

### Chưa theo dõi — mã (24)
```
src/lib/cursor/: composite.ts declaration-prompt.ts identity.ts obligation.ts
                 provenance.ts sensitive.ts
drizzle/       : 0023 … 0034 (12 tệp .sql)
công cụ        : apply_migrations.mjs attempt_accounting.mjs preflight_0025.mjs
                 rollback_g3.mjs stage_journal.mjs verify_g3.mjs verify_g5.mjs
                 verify_migrations_g8.mjs
```

### Chưa theo dõi — test (11)
```
tests/integration/: composite-authorization.test.ts declaration-pass-persistence.test.ts
                    provenance-agreement.test.ts two-pass-loop.test.ts
tests/unit/       : attempt-accounting.test.ts cursor-clause-split.test.ts
                    cursor-obligation.test.ts cursor-stored-payload.test.ts
                    cursor-two-pass.test.ts g8-review-fixes.test.ts
                    gate-preconditions.test.ts provenance-matrix.test.ts
                    reporting-defects.test.ts
```

> **CẢNH BÁO:** sáu tệp quyết định ngữ nghĩa (`sensitive.ts`, `identity.ts`,
> `provenance.ts`, `obligation.ts`, `composite.ts`, `declaration-prompt.ts`)
> **chưa được git theo dõi**, nên `git diff HEAD` mù với chúng và
> `gitDirtyDiffHash` không thấy chúng đổi. Băm mã nguồn có ghi lại nội dung,
> nhưng `_meta.gitCommit` **không** dẫn tới cây chứa chúng.

## 10. Ghi nhớ nghiêm khắc cho phiên sau

Ba vòng khắc phục liên tiếp, mỗi vòng đều **tự sinh khiếm khuyết mới**:
vòng G7 sinh A-1/A-2/A-3/C-2; vòng G-R1..R5 sinh F1 và F3; và tôi từng khẳng
định H-2 đã được sửa **mà không kiểm**. Cộng thêm việc tự làm hỏng một lần chạy
cổng bằng cách chạy test song song trên database dùng chung.

Bốn quy tắc, không thương lượng:

1. **Chứng minh bằng CHẠY, không bằng đọc mã.**
2. **Độc quyền database TEST** trong suốt mọi lần chạy cổng.
3. **Không khẳng định điều chưa kiểm** — kể cả khi "rõ ràng là đúng".
4. **Test grep là yếu.** Reviewer C đã chứng minh bằng mutation rằng một
   assertion grep vẫn xanh sau khi xoá dòng mã nó tưởng đang bảo vệ. Ưu tiên
   test CHẠY được hàm thật.

---

## 11. VÒNG RÀ SOÁT C — hai reviewer độc lập trên cây sẽ đóng băng (2026-08-12)

Codex hết hạn mức tới 2026-08-18, nên vòng này chạy bằng hai reviewer độc lập,
mỗi bên một ống kính, đều bị CẤM tuyệt đối chạm database. Cả hai đều tìm ra
khiếm khuyết THẬT trên cây đã qua 20 vòng Codex — mọi phát hiện đều được **kiểm
chứng lại bằng CHẠY trước khi sửa**, không sửa theo lời reviewer.

### Đã đóng

| # | Mức | Khiếm khuyết | Bằng chứng CHẠY |
|---|-----|--------------|-----------------|
| C-1 | BLOCKER | JSON hỏng CÚ PHÁP + nhắc chỉ số nhạy cảm lành tính -> `UNSUPPORTED_CLAIM` (vĩnh viễn). Lớp `INVALID_JSON` trên thực tế không còn tồn tại, vì bài phân tích thật nào cũng nhắc impressions/CTR/thumbnail. | Cùng payload, đổi `impressions` -> `dữ liệu`: `UNSUPPORTED_CLAIM` vs `INVALID_JSON` |

**C-1 va thẳng vào R18 — và cả HAI đều đúng.** Bản sửa đầu tiên (bỏ quét khẳng
định nhạy cảm ở nhánh hỏng cú pháp) làm ĐỎ test R18, vốn đòi khẳng định ở trường
THỪA không được tha chỉ vì payload hỏng. Cổng bắt được đúng chỗ này.

Mâu thuẫn chỉ tồn tại khi MẤT cấu trúc trường. Lời giải là `stripTrailingCommas`
+ `reparseAfterTrivialRepair`: sửa đúng MỘT lỗi — dấu phẩy thừa, lỗi áp đảo của
LLM và là phép sửa duy nhất không đổi nghĩa payload — rồi parse lại. Có cấu trúc
trở lại thì `unrecognized_keys` hoạt động, nên **trường THỪA vẫn bị bắt (R18) mà
ô THẬT vẫn được tha (C-1)**. Phép cắt dấu phẩy PHÂN BIỆT trong/ngoài chuỗi: một
regex trần `,(\s*[}\]])` sẽ sửa cả bên trong câu văn sắp đem đi quét, và một phép
sửa dùng để CHẨN ĐOÁN thì tuyệt đối không được đổi lời của mô hình (có test).
Khi sửa xong vẫn không parse được thì mới thừa nhận là mất cấu trúc và lùi về
quét nhân quả — không đoán.
| C-2 | BLOCKER | Bản KHAI BÁO hỏng cú pháp bị quét như MỘT chuỗi -> `"relatedMetric":"impression_ctr"` của một bản khai ĐÚNG thành vi phạm. Một dấu phẩy vứt bỏ bài phân tích đã kiểm định xong. | `recoverJsonStringLiterals` + đối chứng `{"extra":"CTR thấp.",}` vẫn bị bắt |
| C-3 | BLOCKER | Khối ```json bọc ngoài hạ cấp `EVIDENCE_UNRESOLVED` (vĩnh viễn) thành `PROSE_OUTSIDE_JSON` (RETRYABLE). Một lỗi ĐỊNH DẠNG vô can mở đường thử lại cho thất bại NỘI DUNG. | Cùng payload evidence sai: không bọc -> `EVIDENCE_UNRESOLVED`, có bọc -> `PROSE_OUTSIDE_JSON` |
| C-4 | HIGH | Giả thuyết nhân quả CÓ RÀO ĐÓN không có bản khai nào hợp lệ — **cả 10 tổ hợp** claimType × assertionStatus đều BLOCKER. Chặng hợp nhất từ chối vĩnh viễn một bài phân tích đúng hợp đồng. | Bảng 10 tổ hợp trước/sau; nay `CAUSAL + CONDITIONAL` sạch, R5 (`CAUSAL + ASSERTED`) còn nguyên |
| C-5 | HIGH | `verify_phase4.mjs` không có chiều DB→INDEX: xoá một cặp (danh tính + tệp) khỏi chỉ mục thì "chạy tới khi đẹp rồi chọn 3 mẫu" qua cổng không một vết đỏ. | Test tích hợp 8 + đối chứng trong ca lành mạnh |
| C-6 | HIGH | `attempt_table.mjs:210` in "lô này không hợp lệ" rồi `process.exit(0)` — dòng duy nhất trong vòng lặp KHÔNG kèm `gateOk = false`. Đây là thứ DUY NHẤT chặn việc chạy lại lượt phân tích tới khi số liệu đẹp lên. | `samplingCapOk` tách sang `attempt_accounting.mjs`, có test chạy |
| C-7 | MEDIUM | Năm băm mã nguồn mà 0035 thêm vào bản kê không được phép kiểm nào đọc — 0035 GHI nguồn gốc mà không ai ĐỐI CHIẾU. | Thêm 5 mục vào `bind` của cổng + fixture |
| C-8 | MEDIUM | Bảng đếm `successes` của INDEX không bao giờ được đối chiếu với số danh tính. | Test tích hợp 9 |
| C-9 | MEDIUM | Một câu nhân quả bị đếm HAI lần vào `analysis_validation.causal_violations`. | `causalViolations === 1` |
| C-10 | MEDIUM | `validateProseOnly` ghi "không tìm thấy object JSON nào" vào bản ghi pháp y **khi đã có object JSON** — gọi từ cả hai nhánh `if (execFailure)` nơi `emittedJson` thường khác rỗng. | Thông điệp nay phụ thuộc `emittedJson` |

Test khoá: `tests/unit/review-round-c.test.ts` (14 test) và ba ca mới trong
`tests/integration/verify-phase4-gate.test.ts`. **Mọi phát hiện đều có cặp ĐỐI
CHỨNG** — nới một chiều mà không chứng minh chiều kia còn chặn thì chỉ là xoá
mất một phép kiểm.

### CÒN MỞ — cố ý hoãn, không phải bỏ sót

| # | Mức | Việc | Lý do hoãn |
|---|-----|------|-----------|
| C-11 | MEDIUM | Mã CHẾT mà chú thích vẫn mô tả như cơ chế an toàn đang chạy: `mentionsMissingness`, `isInterrogative`, `isConditional`, `INSTEAD_OF`, `textFields` — không nơi nào gọi (đã kiểm bằng grep toàn `src`/`tests`), nhưng ~120 dòng chú thích quanh chúng vẫn tả chúng là bộ lọc phủ định/nghi vấn đang hoạt động. Rủi ro: người rà soát sau suy luận từ một miễn trừ đã chết. | Xoá 5 hàm + sửa chú thích là thay đổi THUẦN HÌNH THỨC, không đổi hành vi nào. Làm ngay trước đóng băng chỉ thêm nhiễu vào diff mà không đóng lỗ nào. |
| C-12 | LOW | `cursor_declaration_result.payload->>'obligationSetHash'` và cột `obligation_set_hash` là CÙNG một chuỗi (`run.ts` ghi cả hai từ một biến), nên so chúng trong SQL là phép so văn bản thuần — KHÔNG cần dựng lại `stableStringify`. Đây là bất biến nằm NGOÀI ranh giới đã chấp nhận ở §6 của `PHASE4_TRUST_BOUNDARIES.md`. Hiện chỉ `composite.ts` (đường ghi ứng dụng) cưỡng chế. | Cần migration 0038 + áp lên cả hai database ngay giờ đóng băng. Khuôn mẫu đã có sẵn (0036/0037 dùng trigger cho hàng MỚI, không đụng hàng cũ). |
| C-13 | — | Vòng Codex 21 để rà soát bản sửa R20 — bản sửa DUY NHẤT chưa qua rà soát độc lập. | Hết hạn mức tới 2026-08-18. |

### Ghi nhớ bổ sung

5. **Dấu huyền trong template literal `.mjs` là lỗi cú pháp.** Lần thứ TƯ trong
   chiến dịch: một chú thích SQL viết \`sensitiveLexiconHash\` trong dấu huyền
   làm hỏng `verify_phase4.mjs`, và **toàn bộ test đơn vị vẫn xanh** vì không
   test nào nạp tệp ấy. `node --check` là phép kiểm rẻ nhất — chạy nó trước.
6. **Reviewer độc lập vẫn tìm ra BLOCKER sau 20 vòng Codex.** Số vòng đã qua
   không phải bằng chứng về độ sạch.

---

## 12. TÁM LÔ THĂM DÒ THẬT — hợp đồng khai báo từ BẤT KHẢ thành khả thi (2026-08-13..14)

`6817c40` qua mọi cổng kỹ thuật nhưng KHÔNG qua được điều kiện §7: thăm dò thật.
Tám lô trên database CHÍNH, runtime ghim `2026.08.04-aaa8809`, mỗi lô độc quyền.

### Diễn biến

| Lô | Mốc hợp đồng | Mẫu đạt | Phát hiện |
|---|---|---|---|
| 1 | gen 1.1 | 0/18 | `impressionCtr` không khớp bí danh — bẫy biên từ `\b` lần thứ NĂM |
| 2 | gen 1.2 | 0/18 | `subject_metric_not_in_text` 69→9, nhưng lộ nghịch lý `data_coverage` |
| 3 | prompt 1.1.0 | VÔ HIỆU | Cursor CLI treo (3×timeout, stdout 0 byte) — hỏng môi trường |
| 4 | validator 1.1 | 0/18 | R0b miễn `data_coverage`; lộ nghịch lý `LIMITATION` |
| 5 | validator 1.2 | **1**/18 | **hiện vật chính thức ĐẦU TIÊN** sau 54 lần thử trắng |
| 6 | validator 1.3 | 0/18 | BLOCKER 41→23; lộ giới hạn 2 ô chỉ số |
| 7 | validator 1.4 | **7**/18 | `hinh_su` 3/3, `phat_giao` 3/3, `phong_thuy` 1/6 |
| 8 | validator 1.4 | **7**/18 | **tái lập chính xác lô 7** |

Tổng BLOCKER ở chặng hợp nhất: **145 → 6**.

### BỐN nghịch lý CẤU TRÚC — đều là lỗi mã, đều đo được

Mỗi cái đều có cùng hình dạng: **câu đúng hợp đồng nhất của miền này lại không có
bản khai hợp lệ nào**, và lượt 2 không sửa được văn xuôi nên mô hình không có
đường thoát.

1. **Bí danh không biết camelCase.** Mô hình viết `impressionCtr` vì đó là tên
   trường THẬT trong gói dữ liệu (từ YouTube API qua `sync/ingest`). Sửa bằng
   cách SINH dạng tên từ chính khoá, không vá tay — đóng luôn `viewsD7` và
   `averageViewPercentage`.
2. **`data_coverage` vs R0b.** Câu "không có impressions nên không tách được…"
   khai `impressions` thì trúng `methodology_subject_also_missing`, khai
   `data_coverage` thì trúng `subject_metric_not_in_text` (113 lần). Miễn trừ
   R0b cho chủ ngữ SIÊU HÌNH.
3. **`LIMITATION` không biết tiếng Việt.** Đo trên 383 câu thật: bảng chỉ biết
   `0%`, bỏ sót 105 câu "không…được", 104 câu "thiếu", 68 câu "không có". Nới
   kèm chốt bù R1b (cấm `data_coverage` mang phán xét).
4. **Hai ô chỉ số cho câu bốn chỉ số.** "Không kết luận hiệu quả thumbnail, tiêu
   đề, hay packaging vì impressions/CTR phủ 0%" nhắc 4 chỉ số nhạy cảm; claim chỉ
   có `subjectMetric` + `relatedMetric` (14/17 lần chặn của lô 6). Miễn cho claim
   KHÔNG mang phán xét — không khẳng định gì thì không giấu được gì.

### Prompt và validator từng mã hoá HAI hợp đồng khác nhau

56% lỗi BLOCKER của lô 2 đến từ hai quy tắc prompt **chưa từng nêu**: dấu hiệu
tình thái, và dạng khai cho câu thiếu dữ liệu. Nay `MODALITY_MARKERS` và
`CLAIM_CONTRADICTIONS` được prompt SINH RA từ chính bảng luật, với test 45h/45i
buộc hai bên không lệch được.

### CÒN LẠI — lỗi MÔ HÌNH, không phải lỗi mã

`phong_thuy` trượt **4/6 ngay ở lượt PHÂN TÍCH** ở cả lô 7 và 8: mô hình tự viết
kết luận CTR/impressions rồi `selfCheck` khai là không viết. Đây đúng
`PROBE SEMANTIC FAIL` của §3 — **không được sửa schema/prompt/validator vì nó**.

### Đường ANTHROPIC_API — dựng sẵn, chưa chạy

Lõi kiểm định không biết ai sinh văn bản, nên đổi analyst chỉ là bộ thực thi
khác trả cùng `CursorExecResult`. `exec-anthropic.ts` + migration 0038 +
`selectedProvider()`. **Thiếu `ANTHROPIC_API_KEY`** để chạy thật. Lô
`ANTHROPIC_API` là lô RIÊNG, không gộp với 8 lô Cursor.

### Ghi nhớ bổ sung

7. **Vá từ vựng lẻ là vòng lặp tốn 1 giờ/lần.** Mỗi lô lòi một khoảng trống.
   Cách thoát: trích kho câu THẬT từ database rồi chạy qua toàn bộ bảng nhận
   diện trong MỘT lượt — không tốn hạn mức LLM nào.
8. **Audit đối chiếu bảng luật MỚI với lỗi ghi từ lô CŨ là nhiễm bẩn.** Lần chạy
   đầu báo "362 mô hình chọn sai"; dấu hiệu lộ ra là dòng vô nghĩa "khai
   LIMITATION nhưng câu khớp LIMITATION". Chỉ audit trong CÙNG một mốc hợp đồng.
9. **Nới một luật thì phải có test đối chứng cho chiều CÒN CHẶN.** Bản đầu của
   chốt R1b soi `relatedMetric` và làm đỏ 10 test — trong đó có nhóm tên là "các
   câu THẬT từng bị chặn oan". Cổng bắt được đúng chỗ đó.

### CODEX VÒNG 21 (2026-08-17) — một BLOCKER, đã đóng

Rà soát riêng bốn nghịch lý. Codex phá được, và ca phá khai thác **hệ quả GHÉP
của ba miễn trừ**, không phải lỗi của riêng cái nào:

```
văn xuôi : "Thumbnail kém dù thiếu impressions/CTR."
bản khai : data_coverage / impression_ctr / UNKNOWN / LIMITATION
```

`"thiếu"` khớp LIMITATION (C-15) -> `data_coverage` miễn R0b (C-14) -> claim tự
khai `UNKNOWN` nên vừa được miễn `undeclared_metric_in_claim_text` (C-16) vừa
làm R1b im lặng. Không quy tắc nào nổ, trong khi câu khẳng định `thumbnail`
(phủ 0%) là "kém". Đã tái lập bằng chạy: `blockersOf` trả về mảng RỖNG.

**Gốc rễ là lỗi THIẾT KẾ, không phải cài đặt:** `judgemental` suy ra từ TRƯỜNG
KHAI BÁO chứ không từ văn xuôi, nên **một bản tự khai đang được dùng làm bằng
chứng về chính nó**. Đó là lý do cả ba miễn trừ riêng lẻ đều trông hợp lý.

Bản sửa R1c: `UNKNOWN` + `LIMITATION` mà có MỘT MỆNH ĐỀ chứa đồng thời chỉ số
phủ 0% và từ phán xét -> BLOCKER. `COMPOSITE_VALIDATOR_VERSION` 1.4 -> 1.5.

10. **Xét theo MỆNH ĐỀ, không theo cả câu.** Xét cả câu chặn oan "Độ phủ ngày
    rất thấp và impressions/CTR bằng không" — "thấp" ở đó nói về độ phủ ngày.
11. **Miễn trừ phải liệt kê trạng thái, không dùng phủ định.** Bản đầu của R1c
    viết `!== 'ASSERTED'` và làm đỏ 3 câu hợp lệ; đúng là `=== 'LIMITATION'`,
    vì CONDITIONAL/QUESTION/NEGATED_ACTION đã đánh dấu sẵn phán xét là giả định.
    Lần thứ HAI trong vòng này mắc đúng lỗi ấy — và cả hai lần bộ test đều bắt.

---
---

# (LƯU TRỮ) Nội dung handoff trước 2026-08-07

# Phase 4.1 — Điểm dừng pháp y (forensic checkpoint)

> ## ⚠ TRẠNG THÁI COMMIT `da7853e`
>
> **`da7853e` là CHECKPOINT TRUNG GIAN, CHƯA QUA CỔNG ĐÓNG BĂNG.**
>
> Nó được tạo **TRƯỚC** khi đạt điều kiện đóng băng của Phase 4.1
> (0 lỗi phân giải R **và** 0 lỗi đầy đủ U trên lần thăm dò). Tại thời điểm
> commit, lần thăm dò gần nhất còn **2 lỗi U**.
>
> Vì vậy, một cách dứt khoát:
>
> * **KHÔNG merge** `da7853e` vào `main` hay bất kỳ nhánh tích hợp nào.
> * **KHÔNG tag** nó (không `v4.1`, không `phase4.1-frozen`, không gì khác).
> * **KHÔNG** trình bày nó là commit CUỐI của Phase 4.1, và không dùng nó làm
>   mốc đóng băng cho lô chính thức.
> * Nó tồn tại vì đúng MỘT lý do: tệp chưa commit không có mạng an toàn, và sự
>   cố xoá nhầm bảy schema đã chứng minh cái giá của việc để công việc nằm ngoài
>   git. Đây là lưới an toàn, không phải cột mốc.
>
> Cổng KỸ THUẬT (typecheck / test / lược đồ / quét bí mật) đã đạt tại commit này.
> Cổng ĐÓNG BĂNG thì chưa. Hai chuyện khác nhau và không được gộp khi báo cáo.
>
> Commit đóng băng thật, khi có, phải là một commit MỚI, sau khi một lần thăm dò
> cho R=0 và U=0.

> **CẬP NHẬT 2026-08-05 (vòng 2) — cài đặt XONG, cổng kỹ thuật ĐẠT, nhưng
> CHƯA đủ điều kiện đóng băng.**
>
> | Cổng | Trạng thái |
> |---|---|
> | `npx tsc --noEmit` | 0 lỗi |
> | `npx vitest run` | 481/481 xanh (17 tệp) |
> | `node verify_schema.mjs` | ĐẠT trên **cả hai** database, kèm ca 33/34 của 2.1 |
> | `python3 scripts/secret_scan.py` | CLEAN |
> | Prompt | **3.0.0** đã viết (sourceRef, section/field sinh từ schema, một-ô-một-phát-biểu) |
> | Ma trận đối kháng | 37 ca + 4 ca bổ sung + 11 ca hồi quy = `tests/unit/cursor-adversarial.test.ts` |
> | Rà soát Codex | xong, 4 phát hiện, **đã sửa hết** (`creator_specs/_codex_review_4_1.log`) |
> | Thăm dò `hinh_su` | **3 lần**, xem bảng dưới |
>
> **Điều kiện đóng băng (0 lỗi R và 0 lỗi U) CHƯA đạt. KHÔNG đóng băng, KHÔNG
> chạy lô chính thức.**
>
> | Thăm dò | R | U | S | Ghi chú |
> |---|---|---|---|---|
> | #1 (prompt 3.0.0 bản đầu) | **0** | 9 | 38 | mô hình khai 26 claim, mọi `sourceRef` phân giải đúng |
> | #2 (sau sửa alias + gỡ gạch ngang) | **0** | 19 | 5 | mô hình né bằng cách KHÔNG khai — cùng nguyên nhân, chiều ngược |
> | #3 (sau tình thái theo cấu trúc) | **0** | **2** | 24 | U giảm 19 → 2 |
>
> **R = 0 ở cả ba lần.** Cơ chế `sourceRef` hoạt động: mô hình chưa trỏ sai một
> lần nào trên ~26 claim mỗi lần chạy. Đây là kết quả rõ rệt nhất của 2.1.
>
> ### Hai lỗi U còn lại của lần #3 — đã chẩn đoán, chưa sửa
>
> 1. `HYPOTHESIS(H-005).validationMethod` — *"Khi có impression_ctr, so sánh CTR
>    nhóm high-retention/low-views với nhóm median-retention."* Dấu phẩy sau mệnh
>    đề điều kiện đứng trước tách câu thành hai, cả hai đều nhắc CTR. **Lỗi của
>    MÔ HÌNH**: prompt 3.0.0 đã dạy đúng cách viết ("So sánh CTR … khi có dữ
>    liệu" — đưa điều kiện vào trong mệnh đề), mô hình chưa theo.
> 2. `NON_CONCLUSION().explicitNonConclusions[0]` — *"Không kết luận hiệu quả
>    thumbnail, tiêu đề hút click, hoặc packaging vì impressions và
>    impression_ctr độ phủ 0%."* **Lỗi của QUY TẮC**: dấu phẩy ở đây ngăn cách
>    các mục trong một LIỆT KÊ, không ngăn cách mệnh đề. U1 đếm một phát biểu
>    thành hai. Cùng họ với `và` và với gạch ngang (xem
>    `creator_specs/PHASE4_TRUST_BOUNDARIES.md` mục 3).
>
> Việc tiếp theo, theo thứ tự: sửa (2) cho `clausesOf` không tách trên dấu phẩy
> của liệt kê; thêm hướng dẫn prompt cho (1); thăm dò lại. **Không** nới U1.
>
> ### Ba thay đổi HỢP ĐỒNG đã làm ở vòng này — cần biết trước khi đọc mã
>
> 1. **Danh tính Ô gồm `ordinal`.** Bản bàn giao trước ghi `canonical =
>    section|itemId|field` (không ordinal). Sai: hai phần tử của cùng một mảng
>    mang chung danh tính, nên U2 chặn oan đúng cách sửa mà U1 yêu cầu, và U3
>    coi cả mảng là "đã khai" khi mới khai một phần tử.
> 2. **Trường hợp lệ của `sourceRef` sinh từ schema và dùng CHUNG** cho prompt,
>    bộ phân giải và bộ liệt kê ô (`sourceRefSections()` trong `schema.ts`).
>    `resolveSourceRef` nay từ chối field không phải văn xuôi (ca 7 của ma trận).
> 3. **Tình thái theo CẤU TRÚC** cho ba trường nhãn (`metricOrArtifact`,
>    `missingEvidence`, `reviewQuestions`). Đây là SIẾT chứ không nới: trước đó
>    `ASSERTED` là trạng thái DUY NHẤT đi qua được ở các ô đó; nay nó là trạng
>    thái duy nhất bị CẤM.
>
> Chi tiết bản cũ giữ nguyên bên dưới để đối chiếu lịch sử.

---

**Trạng thái (bản gốc, đã lỗi thời): cài đặt DỞ DANG, KHÔNG an toàn để đóng băng.**

> **CẬP NHẬT sau khi chốt checkpoint** — đã commit `33cf1f5` trên nhánh
> `feat/content-hub-backend`. Git giờ là mạng an toàn, nên `phase4_tracked.patch`
> và `phase4_untracked.tar.gz` không còn cần thiết (vẫn giữ trên đĩa, không đưa
> vào commit). Prompt cho agent tiếp theo: `handoff/CONTINUE_PROMPT.md`.
>
> Tiến độ từ lúc lập checkpoint: 68 lỗi TS → **0**; test hỏng 53 → **10**;
> `mc.text` trong validate.ts 19 → **0**; thêm 22 test đặc tả khoá bảy schema.
> Hai lỗi thật phát hiện thêm: **mất quét ngôn ngữ nhân quả trên văn xuôi**
> (đã khôi phục) và **U4 chặn oan** claim về chỉ số có dữ liệu (đã sửa).

Ngày: 2026-08-05 · Commit nền: `c4d5321` (commit của bạn, không liên quan Phase 4)
· 68 lỗi TypeScript · Không chạy test/lô nào sau điểm dừng này.

---

## 1. Kho hiện vật

| Tệp | Nội dung |
|---|---|
| `handoff/phase4_tracked.patch` | 252 KB — diff của các tệp ĐÃ theo dõi |
| `handoff/phase4_untracked.tar.gz` | 116 KB — toàn bộ tệp Phase 4 CHƯA theo dõi |
| `handoff/PHASE4_1_HANDOFF.md` | tài liệu này |

Phần lớn công việc Phase 4 nằm ở tệp **chưa theo dõi**, nên `git diff` một mình
KHÔNG đủ để khôi phục. Phải dùng cả hai hiện vật.

---

## 2. Phân loại từng thay đổi

### ✅ Đã kiểm chứng — giữ lại

| Tệp | Ghi chú |
|---|---|
| `drizzle/0016..0022*.sql` + snapshot + `_journal.json` | 23 migration, đã kiểm trực tiếp trên CẢ HAI database |
| `src/db/schema/cursor-analysis.ts` | lineage phức hợp, trigger, cột nguồn gốc |
| `src/lib/cursor/exec.ts` | sandbox, allowlist môi trường, dọn cây tiến trình, timeout — **không đụng tới ở 4.1** |
| `src/db/run-cursor.ts` | CLI, `--successes/--max-attempts`, INDEX.json, xoá artifact cũ |
| `verify_schema.mjs`, `verify_phase4.mjs`, `attempt_table.mjs` | công cụ kiểm chứng, chạy được |
| `tests/integration/cursor-persistence.test.ts` | 28 test, xanh trước 4.1 |
| `tests/unit/cursor-exec.test.ts` | 23 test, xanh |
| `creator_specs/PHASE4_*.md` | tài liệu thiết kế + ranh giới tin cậy |

### 🟡 Dở dang — cần hoàn thiện

| Tệp | Tình trạng |
|---|---|
| `src/lib/cursor/schema.ts` | schema 2.1 XONG (`sourceRef`, bỏ `text`, `LEGACY=['1.0','2.0']`) |
| `src/lib/cursor/source-ref.ts` | **MỚI, hoàn chỉnh, chưa có test** — resolver + `enumerateUnits` + `findDuplicateItemIds` |
| `src/lib/cursor/validate.ts` | R/U đã thay vào; **S-rules vẫn đọc `mc.text` (đã bị bỏ)** → 26 lỗi |
| `src/lib/cursor/run.ts` | drift đã theo danh tính chuẩn tắc + nội dung ô; chưa có bên gọi truyền `rootText`/`repairedText` |
| `tests/unit/cursor-validate.test.ts` | 42 lỗi — fixture còn dùng hình dạng claim 2.0 |
| `tests/unit/cursor-baseline.test.ts` | dùng `FULL` có `text`/`sourceSection`/`sourceId` — cần đổi sang `sourceRef` |

### 🔴 Tái dựng — **đã đối chiếu độc lập, KHÔNG còn "không nguồn tin cậy"**

Xem mục 4.

### ⛔ Không an toàn để giữ

Không có tệp nào cần xoá. `prompt.ts` vẫn ở bản 2.0.0 (chưa viết 3.0.0) — đây là
**thiếu**, không phải sai; nó vẫn nhất quán với schema 2.0 cũ nên đừng dùng lẫn
với schema 2.1.

---

## 3. Sự cố: xoá nhầm bảy schema

**Chuyện gì xảy ra.** Một lệnh thay chuỗi trong `schema.ts` dùng hai mốc:
`"MỘT phát biểu liên quan tới chỉ số…"` → `"export const cursorOutputSchema"`.
Bảy schema mục nằm GIỮA hai mốc đó và bị xoá cùng.

**Vì sao không phát hiện ngay.** Lệnh thay không có assert. Chỉ lộ ra khi
typecheck nhảy lên 244 lỗi.

**Vì sao khôi phục từ git thất bại.** Toàn bộ Phase 4 CHƯA commit, nên
`git show HEAD:apps/hub/src/lib/cursor/schema.ts` báo lỗi. Do dùng `&&`, bước
python phía sau **không chạy** và không in ra lỗi nào — một thất bại IM LẶNG,
đúng loại lỗi mà cả Phase 4 này chống lại.

**Bài học vận hành:** mọi lệnh sửa tệp bằng script phải `assert` mốc tồn tại; và
tệp chưa commit thì git KHÔNG phải mạng an toàn.

---

## 4. Bảy schema tái dựng — và bằng chứng đối chiếu

Tái dựng bằng tay: `keyFindingSchema`, `hypothesisSchema`, `recommendationSchema`,
`experimentSchema`, `manualReviewTargetSchema`, `dataRequestSchema`,
`selfCheckSchema` (95 dòng, hiện nằm trong `schema.ts`).

**Nguồn đối chiếu ĐỘC LẬP và có trước lúc xoá:** vòng rà soát Codex về tương ứng
prompt↔schema (log `codex_prompt.log`) đã liệt kê đầy đủ mọi ràng buộc chuỗi/mảng
của schema **trước** khi sự cố xảy ra.

**Kết quả đối chiếu tự động: 26/26 KHỚP, không sai lệch.**

| Trường | Codex ghi trước khi xoá | Bản tái dựng |
|---|---|---|
| `analysisSummary.overallAssessment` | 20–2000 | ✅ |
| `analysisSummary.confidenceRationale` | 10–1000 | ✅ |
| `analysisSummary.primaryConstraint` | 5–600 | ✅ |
| `keyFindings[].statement` | 10–600 | ✅ |
| `keyFindings[].supportingReasoning` | 10–1200 | ✅ |
| `keyFindings[].limitations[]` | ≤400 | ✅ |
| `hypotheses[].statement` | 10–600 | ✅ |
| `hypotheses[].missingEvidence[]` | ≤300 | ✅ |
| `hypotheses[].validationMethod` | 10–800 | ✅ |
| `recommendations[].action` | 10–600 | ✅ |
| `recommendations[].rationale` | 10–1200 | ✅ |
| `recommendations[].risks[]` | ≤400 | ✅ |
| `recommendations[].successMetric` | 3–400 | ✅ |
| `experiments[].change` | 10–600 | ✅ |
| `experiments[].baseline` | 3–400 | ✅ |
| `experiments[].successMetrics[]` | ≤300 | ✅ |
| `experiments[].sampleLimitations[]` | ≤400 | ✅ |
| `experiments[].stopConditions[]` | ≤300 | ✅ |
| `experiments[].interpretationRisks[]` | ≤400 | ✅ |
| `manualReviewTargets[].targetId` | 1–120 | ✅ |
| `manualReviewTargets[].reason` | 5–500 | ✅ |
| `manualReviewTargets[].reviewQuestions[]` | ≤300 | ✅ |
| `dataRequests[].metricOrArtifact` | 2–200 | ✅ |
| `dataRequests[].reason` | 5–500 | ✅ |
| `dataRequests[].decisionUnlocked` | 5–500 | ✅ |
| `explicitNonConclusions[]` | ≤500 | ✅ |

Ngoài ra khớp với các nguồn khác: `minimumWindowDays` 1–365, trần mảng
(`keyFindings` 1–10, `hypotheses` ≤8, `recommendations` ≤10, `experiments` ≤5,
`stopConditions` 1–5, `interpretationRisks` 1–6, `reviewQuestions` 1–6), và các
regex id `F-/H-/R-/E-` — tất cả đều xuất hiện trong log Codex và trong test.

**Vẫn CHƯA đối chiếu được:** `.default([])` trên các trường tuỳ chọn và
`z.literal('UNVERIFIED')` của `hypotheses[].status`. Cả hai đều có test bao phủ
(`mọi giả thuyết đều UNVERIFIED`), nhưng nên soát mắt một lượt khi tiếp tục.

**Kết luận phân loại:** ✅ *tái dựng có đối chiếu độc lập* — KHÔNG phải "không có
nguồn tin cậy". Vẫn nên review bằng mắt trước khi đóng băng.

---

## 5. 68 lỗi TypeScript — theo NGUYÊN NHÂN GỐC

| # | Nguyên nhân | Lỗi | Cách sửa |
|---|---|---|---|
| 1 | **S-rules vẫn đọc `mc.text`** (19 chỗ) | 26 ở `validate.ts` | đổi sang văn bản ĐÃ PHÂN GIẢI qua `resolvedByClaim` |
| 2 | **Thiếu import** từ `source-ref.ts` | 4 | thêm `resolveSourceRef`, `enumerateUnits`, `findDuplicateItemIds`, `ResolvedUnit` |
| 3 | **`clausesOf` bị xoá cùng khối cũ** | 1 | khôi phục (tách mệnh đề: `,` `;` `:` `và` `nhưng` `còn`) |
| 4 | **`scanTargets` không còn tồn tại** | 1 | phần quét chỉ số bịa phải chạy trên `enumerateUnits()` |
| 5 | **Fixture test dùng hình dạng 2.0** | 42 ở `cursor-validate.test.ts` | đổi `text`/`sourceSection`/`sourceId` → `sourceRef` |

Không có lỗi nào ở `exec.ts`, `run-cursor.ts`, `cursor-analysis.ts`, migration,
hay test tích hợp — các vùng đó không bị 4.1 đụng tới.

---

## 6. Thiết kế ĐÃ HOÀN THÀNH — giữ nguyên

### Schema 2.1
`sourceRef {section, itemId, field, ordinal}` thay cho `text`. Version `2.1`,
`LEGACY_SCHEMA_VERSIONS = ['1.0','2.0']`.

### `source-ref.ts` (mới, hoàn chỉnh)
`resolveSourceRef` · `enumerateUnits` · `findDuplicateItemIds` · `ResolvedUnit`
với `canonical = section|itemId|field` (KHÔNG gồm ordinal).
Fail-closed: `AMBIGUOUS_DUPLICATE_TEXT` khi một field mảng có hai phần tử trùng
nội dung — không phân giải bừa.

### Quy tắc R/U (đã viết trong `validate.ts`)
R1–R5 phân giải · U1 một-ô-một-phát-biểu (validator ĐẾM, không nhờ prompt) ·
U2 một ô một claim · U3 ô nhạy cảm phải được khai · U4 claim mồ côi.

### Drift theo danh tính chuẩn tắc (đã viết trong `run.ts`)
- `section|itemId|field` **không được đổi**, kể cả khi ô mới trùng nội dung —
  chặn việc đổi CHỦ SỞ HỮU kết luận.
- Chỉ `ordinal` (dữ liệu vị trí suy ra) được phép đổi sau khi đảo thứ tự.
- Nội dung ô được trỏ tới không được đổi; số trong ô không được đổi.

### Ranh giới tin cậy (đã ghi đúng)
- **Tất định:** phân giải tham chiếu, tính duy nhất `itemId`.
- **Heuristic ngôn ngữ:** đếm mệnh đề nhạy cảm, quy tắc "một ô một phát biểu".
- Không được gọi cả tầng R/U là tất định.

---

## 7. Việc còn lại — theo THỨ TỰ PHỤ THUỘC

1. Khôi phục `clausesOf`; thêm import từ `source-ref.ts` *(gỡ nguyên nhân 2,3)*
2. Viết lại S1–S8 trên văn bản đã phân giải; thay `scanTargets` bằng
   `enumerateUnits()` *(gỡ nguyên nhân 1,4)*
3. Nối `rootText`/`repairedText` vào `detectSemanticDrift` trong vòng lặp của `run.ts`
4. Viết `prompt.ts` 3.0.0: đặc tả `sourceRef`, `section`/`field` hợp lệ sinh từ
   schema, quy tắc một-ô-một-phát-biểu kèm ví dụ tách ô
5. Cập nhật fixture test sang `sourceRef` *(gỡ nguyên nhân 5)*
6. Thêm ma trận đối kháng 37 ca (mục 6 của `PHASE4_1_DESIGN_V2.md`), **bổ sung**:
   - văn bản TRÙNG HỆT ở hai item khác nhau → drift phải chặn khi đổi ref
   - văn bản trùng hệt ở hai section khác nhau
   - đổi quyền sở hữu (finding → recommendation) với nội dung y hệt
   - trùng nội dung trong cùng field → `AMBIGUOUS_DUPLICATE_TEXT`
7. Chứng minh round-trip JSONB 2.1 + CHECK 0022 trên **cả hai** database
8. Chạy full test + typecheck
9. Rà soát Codex phạm vi hẹp (mục 7 của `PHASE4_1_DESIGN_V2.md`)
10. **Một** lần thăm dò `hinh_su`; tiêu chí đóng băng: **0 lỗi R/U**
11. Đóng băng mới → lô chính thức 3 kênh × 3 mẫu × trần 6

---

## 8. Mốc so sánh — GIỮ NGUYÊN, không trộn mẫu

| Lô | hinh_su | phat_giao | phong_thuy |
|---|---|---|---|
| Batch 5 (lexical) | 3/4 | **2/6** | 3/3 |
| Cấu trúc 2.0 | 0/6 | 0/6 | 0/2 (bị ngắt) |

`phat_giao` = **2/6** theo chính sách mốc ngữ nghĩa (lần sửa sau JSON hỏng không
tính là mẫu hợp lệ). Giữ nguyên kết luận: **không an toàn cho vận hành tự động.**

Loại khỏi mọi mẫu số: 3 lô vô hiệu, 3 lần thăm dò.

---

## 9. Rủi ro còn tồn tại

1. Bảy schema tái dựng — đã đối chiếu 26/26 nhưng `.default()` và literal
   `UNVERIFIED` chưa có nguồn đối chiếu độc lập.
2. Ngữ nghĩa bằng chứng: chỉ kiểm cấu trúc, không kiểm nội dung có ủng hộ kết
   luận (`evidence_support_unverified`, HIGH, chặn).
3. Nguồn gốc là bản ghi có kỷ luật, **không phải attestation**.
4. Chưa đo được mô hình tuân thủ `sourceRef` tốt đến đâu — chưa có lần chạy thật nào.
5. Ràng buộc "một ô một phát biểu" là ràng buộc THẬT lên cách hành văn, chưa
   kiểm chứng thực tế.

---

`CHECKPOINT CREATED — implementation incomplete and unsafe to freeze`
