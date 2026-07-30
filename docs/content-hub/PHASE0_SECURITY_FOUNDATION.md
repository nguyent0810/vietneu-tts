# Phase 0 — Repository and Security Foundation

Trạng thái: **HOÀN THÀNH**, chờ Codex phase gate.
Nhánh thực thi: `feat/content-hub-backend` (tách từ `main` @ `126363b`).

Tài liệu này ghi lại **bằng chứng** cho các yêu cầu bảo mật của Phase 0.
Không chứa bất kỳ giá trị credential nào — chỉ tên biến, đường dẫn và trạng
thái có/không.

---

## 1. Git baseline

| Mục | Giá trị |
|---|---|
| Nhánh gốc | `main` |
| Commit gốc | `126363b` (*Add topic-based TTS automation pipeline*) |
| Nhánh thực thi | `feat/content-hub-backend` |
| Trạng thái trước Phase 0 | 8 file tracked đã sửa + 66 mục untracked = 74 dòng `git status --porcelain` |
| Remote `origin` | `pnnbao97/VieNeu-TTS` — **repo upstream của người khác, TUYỆT ĐỐI không push** |
| Remote `audio_tool` | `nguyent0810/vietneu-tts` — fork của người dùng, đích push hợp lệ |

⚠️ Ràng buộc vận hành: mọi lệnh push phải chỉ đích danh `audio_tool`.
`git push` trần sẽ nhắm vào `origin` (repo người khác).

---

## 2. Kiểm kê credential cho 3 kênh

Cả 3 kênh đã cấu hình đầy đủ và **đã nằm ngoài git từ trước Phase 0**.

| Kênh (label) | Tiêu đề kênh | Channel ID (công khai) | Credential |
|---|---|---|---|
| `phong_thuy` | Astro Việt Insights | `UCabOUyNfseJfu-Xy_KXz2rw` | đủ |
| `phat_giao` | Trần Kim Liên | `UCQRsHSC8dBcLvCvrj7CLvKA` | đủ |
| `hinh_su` | Into the Killer's Mind | `UCegnaVpCsJ8souFka7s1URw` | đủ |

*Channel ID là dữ liệu công khai (hiện trong URL YouTube), không phải secret.*

### 2.1 Nơi lưu credential

| Đường dẫn | Nội dung | Trạng thái git | Quyền file |
|---|---|---|---|
| `.youtube_channels/{label}.json` | `client_id`, `client_secret`, `refresh_token`, `scopes` | gitignored (dòng 44) | `0600` |
| `.youtube_oauth_clients.env` | `{KÊNH}_CLIENT_ID` / `_CLIENT_SECRET` | gitignored (dòng 15) | — |
| `.github_integration.env` | `GITHUB_TOKEN`, `CONTENT_TOOL_REPO` | gitignored (dòng 14) | — |
| `.env` | `HF_TOKEN` (tuỳ chọn) | gitignored (dòng 13) | — |

Scope OAuth mỗi kênh (3): `youtube.upload`, `youtube`, `yt-analytics.readonly`.
Scope thứ ba là thứ Phase 2 cần để gọi YouTube Analytics API — **không cần
bootstrap lại kênh nào**.

### 2.2 File mẫu (commit được, giá trị rỗng)

- `.env.example`
- `.github_integration.env.example`
- `.youtube_oauth_clients.env.example` ← **thêm mới ở Phase 0** (trước đó thiếu,
  là khoảng trống duy nhất trong bộ file mẫu)

---

## 3. "Gỡ phụ thuộc runtime vào key/token hardcode trong source"

**Kết quả kiểm chứng: không có phụ thuộc nào để gỡ.** Kiến trúc credential
hiện tại đã đúng từ trước; Phase 0 xác minh và bổ sung hàng rào tự động.

Bằng chứng:

| Kiểm tra | Kết quả |
|---|---|
| Quét 238 file committable theo 12 rule secret | 0 phát hiện |
| Gán credential bằng literal trong source | 0 |
| Đọc credential từ đường dẫn gitignored | `youtube_auth.py:157-187` (`load_credentials` / `get_valid_access_token`) |
| Token trong log/stdout | 0 — 3 dòng khớp `print(.*token)` đều là dương tính giả (quota LLM, tokenizer file) |
| Token trong `.git/config` | Chủ động tránh: `content_repo.py:52-56` truyền credential qua header `Authorization`, không nhúng vào URL remote |
| Placeholder trong tài liệu | `PIPELINE.md:65` dùng `CLIENT_ID_CỦA_BẠN` — placeholder, không phải giá trị thật |

Điểm nhạy cảm duy nhất còn lại là **tham số dòng lệnh** của
`youtube_auth.py bootstrap --client-secret <...>`: giá trị hiện trong
`ps`/history của máy local. Chấp nhận được vì (a) chỉ chạy 1 lần/kênh,
(b) cả 3 kênh **đã bootstrap xong** nên đường này không còn dùng tới trong
các phase sau. Ghi vào backlog `SEC-1`, không phải blocker.

---

## 4. Hàng rào tự động thêm ở Phase 0

### 4.1 `scripts/secret_scan.py`

Quét đúng tập file mà git **sẽ** commit (`git ls-files -co --exclude-standard`),
12 rule chia hai nhóm:

- **Hình dạng token** (11): Google OAuth secret / API key / refresh token,
  GitHub PAT, OpenAI, Anthropic, Slack, AWS, private key block, HF token,
  Postgres URL có mật khẩu. Nhận diện theo tiền tố đặc thù nhà cung cấp nên
  gần như không phụ thuộc ngữ cảnh → chạy được **cả trên file nhị phân**.
- **Phụ thuộc ngữ cảnh** (1): gán credential bằng literal. Chỉ chạy trên text,
  vì trên nhị phân sẽ nhiễu.

Bốn thuộc tính an toàn — **mỗi cái đều từng là một lỗ thật**, ba trong số đó do
Codex Phase 0 review bắt được (xem §8):

1. **Không bao giờ in giá trị khớp** — chỉ `file:dòng` + tên rule. Nếu không,
   chính báo cáo quét lại làm rò secret vào log phase gate/CI.
2. **`--staged` đọc blob trong INDEX** (`git show :path`), không đọc working
   tree. Stage một file có secret rồi sửa working tree cho sạch thì thứ được
   commit vẫn dính secret — đọc working tree sẽ cho qua.
3. **Placeholder xét trên ĐOẠN KHỚP, không xét cả dòng.** Xét cả dòng thì một
   credential thật nằm cạnh chữ `example`/`sample`/`fake` sẽ bị nuốt.
4. **Nhị phân nhận diện bằng nội dung (byte NUL), không bằng đuôi file.** SVG
   là text và chứa được secret; loại theo đuôi file là bỏ sót cả một lớp.

**Fail closed**: một file committable không đọc được → exit `2`, không báo
`CLEAN`. Đó đúng là chỗ secret có thể nấp.

Chặn cứng theo đường dẫn: `.youtube_channels/`, `.youtube_oauth_clients.env`,
`.github_integration.env`, `.env`, `.env.local` — lọt vào tập git theo dõi là
fail ngay, không phụ thuộc nội dung.

Viết bằng Python chứ không phải bash: macOS chỉ có bash 3.2 (không có
`mapfile`), bản bash đầu tiên đã sai âm thầm khi chạy thật.

### 4.2 `tests/test_secret_scan.py` — 36 test

Một scanner hỏng luôn báo `CLEAN` thì **tệ hơn là không có scanner**, vì nó
tạo cảm giác an toàn giả ở mọi phase gate. Bộ test bơm secret **giả** (giá trị
bịa, cố ý nối chuỗi để chính file test không bị bắt) và bắt buộc scanner phải
phát hiện; đồng thời khẳng định 12 dòng an toàn có thật trong repo không bị
báo động giả.

Nhóm `TestRealGitRepo` dựng **repo git thật trong thư mục tạm** (qua biến môi
trường `SECRET_SCAN_ROOT`) để kiểm những tình huống chỉ lộ ra khi chạy thật:
index khác working tree, secret trong SVG, secret nhúng trong file nhị phân,
file không đọc được, và khẳng định báo cáo không in giá trị khớp.

Test đã bắt được **lỗi thật ngay trong lần chạy đầu**: allowlist ban đầu dùng
`x{3,}` trần, nên secret THẬT chứa `xxx` ở giữa bị nuốt im lặng. Đã sửa thành
`[=:_-]x{3,}\b` và khoá lại bằng
`test_placeholder_marker_does_not_hide_real_secret`.

### 4.3 Pre-commit hook — **tuỳ chọn, chưa cài**

`scripts/hooks/pre-commit` + `scripts/install_hooks.sh` có sẵn trong repo
nhưng **cố ý không tự cài**. Người dùng tự chạy `./scripts/install_hooks.sh`
nếu muốn. Lý do: hook chạy code ở mọi commit về sau, và Phase 0 không yêu cầu
điều đó. Hook cũng bỏ qua được bằng `--no-verify`, nên biện pháp kiểm soát
thật vẫn là lần quét toàn repo ở mỗi phase gate.

### 4.4 `.gitignore` mở rộng cho backend sắp tới

Thêm trước khi có code để không bao giờ tồn tại cửa sổ commit nhầm:
`node_modules/`, `apps/hub/.next|.vercel|dist|coverage`, `*.tsbuildinfo`,
`.env.local`, `apps/hub/.env*`, `analysis_out/`.

`DATABASE_URL` của Neon **chứa mật khẩu** → xếp cùng mức nhạy cảm với
`.youtube_channels/`, và đã có rule `postgres_url_with_password` trong scanner.

---

## 5. Tương thích 3 kênh — không đổi

Phase 0 **không sửa một dòng code ứng dụng nào**. Không đụng `youtube_auth.py`,
`youtube_analytics.py`, `youtube_upload.py`, `run.sh` hay pipeline hiện có.
Toàn bộ thay đổi là file mới (scanner, test, hook, file mẫu, tài liệu) cộng
phần thêm vào `.gitignore`.

Hệ quả: đường chạy hiện tại của 3 kênh giữ nguyên, và Phase 2 dùng lại đúng
`.youtube_channels/{label}.json` + `get_valid_access_token()` sẵn có.

---

## 6. Kết quả quét secret cuối Phase 0

```
$ python3 scripts/secret_scan.py
---
SECRET SCAN: CLEAN — 0 phát hiện trên 258 file (245 text, 13 nhị phân).

$ python3 scripts/secret_scan.py --staged
---
SECRET SCAN: CLEAN — 0 phát hiện trên 24 file.

$ uv run pytest tests/test_secret_scan.py -q
36 passed
```

Không có secret nào được commit mới ở Phase 0.

---

## 8. Codex phase gate

### Vòng 1 — `CHANGES_REQUIRED` (3 HIGH, 2 MEDIUM)

Toàn bộ phát hiện đều nhắm vào `secret_scan.py`, và **đều đúng**. Đáng chú ý:
scanner ban đầu chạy sạch trên repo thật và có 27 test xanh — nhưng vẫn tồn
tại ba lớp bỏ sót mà bộ test không chạm tới. Đây chính là kiểu "an toàn giả"
mà §4.2 nói đến.

| # | Mức | Vấn đề | Xử lý |
|---|---|---|---|
| 1 | HIGH | `--staged` lấy **tên** file staged nhưng đọc **nội dung working tree** → stage secret rồi dọn working tree là lọt | Đọc blob index bằng `git show :path`. Khoá bằng `test_staged_mode_reads_index_not_working_tree`. |
| 2 | HIGH | Chỉ cần dòng chứa bất kỳ marker placeholder nào là **cả dòng** bị bỏ qua → credential thật cạnh chữ `example` sẽ lọt | Chuyển sang xét placeholder trên **đoạn khớp**. Khoá bằng `test_allowlist_word_on_same_line_does_not_hide_real_secret`. |
| 3 | HIGH | Loại file theo **đuôi** → SVG (text) và các định dạng khác bị bỏ qua hoàn toàn | Bỏ loại theo đuôi; nhận diện nhị phân bằng byte NUL. Nhị phân vẫn quét bằng rule hình dạng token. Khoá bằng `test_secret_in_svg_is_detected` + `test_secret_embedded_in_binary_is_detected`. |
| 4 | MEDIUM | File không đọc được bị bỏ qua im lặng, scan vẫn báo `CLEAN` | Fail closed: exit `2`. Khoá bằng `test_unreadable_file_fails_closed`. |
| 5 | MEDIUM | Test chỉ phủ regex + working tree, không phủ index/nhị phân/lỗi đọc | Thêm nhóm `TestRealGitRepo` dựng repo git thật (27 → 36 test). |

Hai MEDIUM được sửa luôn thay vì đẩy vào backlog: chúng nhỏ, và chúng làm chắc
đúng cái cổng mà **mọi phase sau đều dựa vào**.

Số file quét tăng 239 → 258 sau khi bỏ loại theo đuôi — tức 19 file trước đây
**chưa từng được kiểm tra**.

### Vòng 2 — `APPROVED`

0 BLOCKER, 0 HIGH.

---

## 7. Đóng băng tài liệu kế hoạch

14 tài liệu trong `docs/content-hub/` (~8.500 dòng) đã **đóng băng** sau
`ARCHITECTURE_APPROVED_FOR_IMPLEMENTATION`. Xem `PLANNING_FROZEN.md` để biết
danh sách file, dòng và quy tắc sửa đổi.

7 rủi ro triển khai còn lại đã chuyển thành tiêu chí nghiệm thu có thể kiểm
tra được — xem `IMPLEMENTATION_ACCEPTANCE_CRITERIA.md`.
