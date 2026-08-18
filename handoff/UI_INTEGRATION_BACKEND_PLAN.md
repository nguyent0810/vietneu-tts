# Kế hoạch backend cho tích hợp UI — theo CỔNG

> Pha này là **BACKEND-ONLY**. UI do đội khác dựng ở pha sau, sau handoff.
> Bản 4 — sau BA vòng phản biện Codex CLI. Một email đăng nhập duy nhất, và
> thêm kênh quản lý bằng uỷ quyền YouTube ngay trong ứng dụng.
> Lập trên cây `a67f0c6`, ngày 2026-08-18.

## 0. Quyết định đã đóng

| Quyết định | Chọn | Lý do |
|---|---|---|
| Đăng nhập | **Một email duy nhất**, Google OIDC | Chỉ một người vận hành. Allowlist là MỘT địa chỉ. |
| Thư viện auth | **Auth.js v5 + Drizzle adapter** | Yêu cầu giữ refresh token của kênh để chạy NỀN là *offline access*. Nền tảng danh tính hosted (Clerk/Auth0) sinh ra để MÔI GIỚI access token cho phiên đang mở, không để giao refresh token cho ta cất dùng dài hạn. Auth.js để token nằm trong database của ta — nơi trigger cưỡng chế được. |
| Origin của UI | **Cùng site** | Xoá CORS. KHÔNG xoá chống CSRF — xem §2.6. |
| Kết nối kênh | **Luồng RIÊNG**, không gọi là SSO | Đăng nhập trả lời "anh là ai"; kết nối kênh trả lời "hub được đọc kênh nào". Khác scope, khác tần suất, khác thứ được lưu. |
| Nguồn sự thật của token kênh | **Hub**, di trú dần | Python đã giữ token 3 kênh trong `.youtube_channels/*.json`. Hai kho cho cùng một thứ thì chắc chắn lệch. |
| Database cho CI | **Service container phù du** | Xoá hẳn secret dùng chung, xoá `hub_ci`, xoá hàng đợi `concurrency`. |

**Quyết định cũ bị VƯỢT QUA MỘT PHẦN:** bản 2 ghi "không có action nghiệp vụ".
Nhưng *thêm kênh* là một mutation có hậu quả thật — nó tạo một credential thường
trú. Nên pha này CÓ đúng một action nghiệp vụ, và chống CSRF từ chỗ "chỉ logout"
trở thành chuyện nghiêm túc.

## 1. Hiện trạng đã kiểm chứng

Bề mặt HTTP: đúng 5 route, không route đọc nào — `health`, `sync/start`,
`sync/ingest`, `sync/finish`, `sync/report`. Không `page.tsx` nào.
Hub KHÔNG có thư viện auth nào.

Tầng người dùng là MÃ CHẾT: `authenticateUser()`, `requireScope()`,
`assertCanApprove()` không được gọi ở đâu ngoài `auth.ts`. `user_account` = 0
hàng, `user_api_token` = 0 hàng, `route.ts` chỉ có `withWorkerAuth`.
`user_account` nhận diện bằng `email` unique — chưa có `(issuer, subject)`.

`consumeRateLimit` chỉ nối vào `withWorkerAuth`, khoá theo `machineId:capability`
(`route.ts:60`) — vô dụng cho login vì lúc đó chưa có principal.
`audit_event` chỉ được ghi bởi `sync/finish`.

Bảng `channel`: `id`, `workspace_id`, `label`, `youtube_channel_id`, `title`,
`reporting_timezone`. **Không có cột credential nào.**

Phía Python: `youtube_auth.py` bootstrap OAuth **loại Desktop app** (loopback cổng
8734), lưu refresh token ở `.youtube_channels/{label}.json`.

Dữ liệu: 1 workspace, 3 kênh, 1.073 video, 11.119 metric ngày, 156.395 feature
value, 15 analysis_run (mới nhất 2026-07-30), 116 cursor_analysis_result
(69 ANALYSIS + 47 COMPOSITE). **47 hàng COMPOSITE thuộc hai thế hệ schema không
tương thích:** `1.0` → 32 hàng, `3.0` → 15 hàng.

Rỗng: `analysis_result`, `approval`, `content_item`, `content_revision`,
`critique`, `evaluation`, `score`.

## 2. Nguyên tắc bắt buộc

1. Chứng minh bằng CHẠY. Không grep, không khẳng định cấu trúc.
2. "Không kiểm được" khác "đã kiểm và đạt". Cấm skip im lặng ở MỌI tầng —
   kể cả tầng API: giấu 32 hàng schema 1.0 cũng là một kiểu skip im lặng.
3. Bất biến quan trọng phải ở tầng database. Ưu tiên **khoá ngoại tổ hợp
   `(resource_id, workspace_id)`** — repo đã dùng mẫu này, `cursor-analysis.ts:399`.
   Trigger chỉ dành cho chuyển trạng thái mà FK/CHECK không nói được.
4. Đổi hợp đồng thì nâng phiên bản. Không gộp dữ liệu hai bên phiên bản.
5. Hết hạn theo thời gian thì đừng giả vờ trigger lo được — xác thực phải kiểm
   `expires_at <= now()` ở MỖI request.
6. **`SameSite=Lax` KHÔNG phải cơ chế chống CSRF.** "Cùng site" bao gồm subdomain
   anh em; `Lax` chỉ chặn cross-SITE. CORS không ngăn form POST. Mutation do UI
   khởi tạo — `logout`, `bắt đầu kết nối kênh`, `ngắt kênh` — phải có: cookie
   host-only tiền tố `__Host-` không đặt `Domain`; kiểm `Origin` fail-closed;
   chỉ nhận `Content-Type: application/json`.

   **NGOẠI LỆ BẮT BUỘC — callback OAuth.** `GET /oauth/youtube/callback` là một
   chuyển hướng top-level TỪ GOOGLE. Nó không phải JSON POST từ UI và có thể
   KHÔNG mang `Origin`. Áp luật trên vào đây sẽ làm hỏng luồng. Callback được
   bảo vệ bằng thứ khác: `state` dùng một lần + PKCE + ràng buộc phiên (xem cổng 7).
7. **Bí mật dài hạn không được nằm plaintext trong database.** Refresh token của
   kênh là credential thường trú: đọc được DB là chiếm được kênh.
8. **Nguyên tắc 7 áp cho MỌI bảng, kể cả bảng của thư viện.** Adapter của Auth.js
   có sẵn các cột token trong bảng `account`. Nếu luồng đăng nhập xin offline
   access, adapter sẽ ghi refresh token xuống ở dạng THÔ — tức bí mật dài hạn vào
   database từ cổng 2, trước cả cổng mã hoá. Luồng đăng nhập phải KHÔNG xin
   offline access, và cổng 2 phải chứng minh điều đó bằng chạy.

## 3. Các cổng

### Cổng 0 — Đổi CI sang database phù du (LUỒNG SONG SONG)

**Không phải cổng đầu tiên theo trình tự — nó là luồng chạy SONG SONG, và là
cổng bắt buộc trước khi merge.** Đặt nối tiếp ở đầu sẽ biến một hạ tầng chưa
kiểm được (wsproxy) thành đường găng của toàn dự án.

Thay secret `TEST_DATABASE_URL` bằng service container `postgres` + sidecar
`neondatabase/wsproxy` (driver là `@neondatabase/serverless`, nói WebSocket).
Cấu hình `neonConfig` trong `tests/helpers/db.ts` đặt sau MỘT cờ môi trường.

**Chưa kiểm được ở máy lập trình viên — máy không có Docker.** CI là người kiểm chứng.

**KHÔNG xoá secret, `hub_ci`, hay `concurrency` trước khi CI phù du xanh.** Chạy
song song hai đường một thời gian; cut over sau khi có bằng chứng.

Bằng chứng CHẤP NHẬN: một lượt CI THẬT trên pull request, `test:gate` xanh,
`gate-preconditions` xanh, log cho thấy 11 tệp integration đều CHẠY.
TRƯỢT khi: có tệp integration bị skip, hoặc phải nới `gate-preconditions`.

### Cổng 1 — Cấu trúc và bất biến GHI ở tầng database

Phạm vi HẸP: chỉ những gì một câu INSERT/UPDATE chứng minh được. "Session đã
revoke thì không đăng nhập được" KHÔNG thuộc về đây — hàng revoked vẫn là hàng
hợp lệ; vô hiệu hoá là hành vi của đường xác thực, chứng minh ở cổng 2.

**Refactor bắt buộc, không hoãn được:** `user_account` hiện mang `workspace_id`
TRỰC TIẾP, và `authenticateUser` lấy workspace từ chính cột đó (`auth.ts:101`).
Không thể vừa thêm membership vừa giữ cột này mà không có hai nguồn sự thật.
Phải bỏ nó, hoặc đánh dấu legacy và CẤM mọi mã mới đọc. Nếu quên, test cách ly
mới sẽ XANH trên đường mới trong khi route cũ vẫn dùng workspace legacy.

Mô hình:
- Auth.js `user` = danh tính chuẩn tắc, adapter sở hữu.
- Auth.js `account` = danh tính đăng nhập ngoài, unique `(provider, providerAccountId)`.
- `user_account` = hồ sơ nghiệp vụ 1:1 với Auth user, qua `auth_user_id UNIQUE NOT NULL`.
- `workspace_membership` = FK tổ hợp tới `user_account` + workspace, mang role/status.
- Mỗi request join `session → user → user_account → membership đang hiệu lực`.

**Liên kết bằng `(issuer, subject)`, KHÔNG bằng email.** Email dùng để đối chiếu
allowlist; tự động nối hai tài khoản chỉ vì trùng email là một lỗ chiếm tài khoản.

`channel_credential` — mô hình TRẠNG THÁI, không phải một cột `revoked_at`:
`ACTIVE` | `REAUTH_REQUIRED` (do `invalid_grant`) | `REVOKED_BY_USER` |
`SUPERSEDED` (do kết nối lại) | `BROKEN` (ciphertext/khoá hỏng).
Kèm `last_refresh_at`, `last_success_at`, `last_failure_at`, mã lỗi đã chuẩn hoá,
scope ĐÃ ĐƯỢC CẤP (không phải scope đã xin), và định danh khoá mã hoá.

`channel.credential_source`: `LEGACY_FILE` | `HUB`. Bất biến là **một kênh chỉ có
MỘT nơi có thẩm quyền tiêu thụ tại một thời điểm** — mạnh hơn "một credential
hiệu lực trong hub".

Bất biến cần trigger:
- Danh tính `(issuer, subject)` đã liên kết thì KHÔNG đổi sang user khác.
- Gỡ membership hoặc vô hiệu user thì session liên quan revoke CÙNG giao dịch.
- KHÔNG "unrevoke" được bằng SQL trực tiếp.
- Một `youtube_channel_id` chỉ có TỐI ĐA MỘT credential `ACTIVE` — partial unique index.
- Xoá user/account KHÔNG được cascade xoá mất bằng chứng audit.

Bằng chứng CHẤP NHẬN:
```
npm run typecheck && npm run test:migrations
npm run test:gate -- tests/integration/auth-schema.test.ts
```
Bằng INSERT/UPDATE ĐỐI KHÁNG: subject trùng bị chặn; membership cross-workspace
bị chặn; đổi chủ danh tính bị chặn; unrevoke bằng SQL bị chặn; credential `ACTIVE`
thứ hai cho cùng kênh bị chặn.

**Trigger về session phải kiểm QUA ADAPTER THẬT, không chỉ bằng SQL.** Adapter tự
insert/update/delete hàng `session`; một trigger tự chế có thể phá hợp đồng của
adapter hoặc bị nó đi vòng. "Một session kế nhiệm" KHÔNG phải khái niệm chuẩn của
Auth.js — nếu cần chuỗi xoay session thì phải đặc tả riêng và chỉ rõ điểm móc.

### Cổng 2 — Đăng nhập Auth.js, allowlist một email, route `/me` THẬT

Auth.js **mặc định cho bất kỳ ai có tài khoản Google đăng nhập**. Chặn ở callback
`signIn`, và mặc định membership = KHÔNG CÓ GÌ. Hai lớp: một là mã, hai là dữ liệu.

**Phải chứng minh luồng đăng nhập KHÔNG xin và KHÔNG lưu offline credential**
(nguyên tắc 8). Nếu vì lý do nào đó nó buộc phải xin, thì cổng 5 phải chuyển lên
TRƯỚC cổng này.

`/me` là route SẢN PHẨM — cổng 3 cần route thật, mà route đọc chỉ ra đời ở cổng 4.

Rate limit khoá theo IP và `(issuer, subject)` — khoá `machineId` của worker
(`route.ts:60`) không dùng được. Audit: login thành công/thất bại, logout, revoke.
Audit KHÔNG chứa token, mã, hay cookie.

Bằng chứng CHẤP NHẬN:
```
npm run test:unit -- tests/unit/auth-callbacks.test.ts tests/unit/session.test.ts
npm run test:gate -- tests/integration/auth-flow.test.ts
```
Ca bắt buộc: email ngoài allowlist bị từ chối; `email_verified=false` bị từ chối;
sai `state`/`nonce`; session hết hạn; session đã revoke; cờ cookie `__Host-`;
`Origin` sai bị từ chối; logout có hiệu lực; **bảng `account` sau khi đăng nhập
KHÔNG chứa refresh token**; tạo user mồ côi trước khi `signIn` từ chối thì được
dọn (đua callback).

### Cổng 3 — `withUserAuth` và cách ly workspace

Chứng minh qua `/me`. `requireScope` hết là mã chết.
Chốt: **đọc membership LIVE mỗi request** — phương án revoke-khi-đổi để hở khoảng
giữa lúc đổi và lúc token hết hạn.

```
npm run test:unit -- tests/unit/user-route-auth.test.ts
npm run test:gate -- tests/integration/workspace-isolation.test.ts
```
Ma trận: ẩn danh; session revoke; user bị vô hiệu; **đăng nhập hợp lệ nhưng KHÔNG
có membership → thấy RỖNG**; member workspace A đọc ID của B; membership bị gỡ
GIỮA phiên; **route CŨ dùng `userAccount.workspaceId` legacy không còn đường sống**.

### Cổng 4 — Read API có ý thức phiên bản

Response danh sách KÊ KHAI phần không phục vụ được:
```json
{
  "contractVersion": "1",
  "servedSchemaVersions": ["3.0"],
  "excluded": { "unsupportedSchemaVersions": { "1.0": 32 } }
}
```
Chi tiết hàng 1.0 trả lỗi CÓ KIỂU `UNSUPPORTED_RESULT_SCHEMA`. KHÔNG trả 404.

**HAI bằng chứng TÁCH RỜI** — integration test chạy trên DB đã TRUNCATE với
fixture riêng, nên KHÔNG chứng minh được con số 32 ở dữ liệu thật.
1. Integration: `excluded` khớp fixture do test tạo.
2. Kiểm toán CHỈ ĐỌC trên dữ liệu thật. Không có môi trường thì `NOT_RUN`.

**Neo hợp đồng độc lập:** fixture JSON của `contractVersion: "1"` đã phát hành +
test tương thích đọc fixture ấy. Sửa DTO và số phiên bản trong CÙNG commit vẫn
xanh nếu thiếu neo này. Thay đổi phá vỡ phải thêm v2, KHÔNG sửa v1.
```
npm run test:gate -- tests/integration/read-api.test.ts
npm run test:unit -- tests/unit/contract-v1-compat.test.ts
```

### Cổng 5 — Kho bí mật, TRƯỚC khi có bí mật nào để mất

Mã hoá phong bì, khoá gốc ở biến môi trường, database không bao giờ thấy bản rõ.
Định danh khoá trong mỗi hàng để xoay khoá được.

**Không ghi nguyên văn response của token endpoint vào log hay lỗi.** Python hiện
đưa body lỗi của Google thẳng vào exception (`youtube_auth.py:197`), còn
`route.ts:26` chỉ scrub chung — scrub chung KHÔNG phải bảo đảm rằng body OAuth
không chứa bí mật.

```
npm run test:unit -- tests/unit/secret-box.test.ts
npm run test:gate -- tests/integration/credential-storage.test.ts
```
Ca bắt buộc: đọc thẳng hàng bằng SQL KHÔNG ra bản rõ; sai khoá thì giải mã THẤT
BẠI chứ không trả rác; xoay khoá đọc được hàng cũ; bản ghi hỏng ném lỗi mà KHÔNG
in bản rõ; credential đã thu hồi không giải mã ra dùng được.

### Cổng 6 — Ai TIÊU THỤ credential trong hub (BLOCKER)

**Đây là lỗ hổng lớn nhất của bản 3 và phải đóng TRƯỚC cổng 7.**

Hôm nay không có đường nào để credential trong hub được dùng. Python chỉ biết đọc
TỆP: `youtube_sync.py:595` dựng `.youtube_channels/{label}.json`;
`twice_weekly_batch.py:112` hard-code đúng ba đường dẫn tệp. Nên một kênh có thể
"kết nối thành công" rồi KHÔNG BAO GIỜ được đồng bộ — cổng 7 sinh ra một tài sản
không có người dùng.

Phải chốt một kiến trúc, theo thứ tự ưu tiên:
1. **Hub giữ refresh token và tự đổi lấy access token**, worker chỉ nhận access
   token ngắn hạn — hoặc hub tự gọi YouTube. An toàn nhất.
2. Worker nhận access token ngắn hạn qua capability riêng, ràng buộc theo kênh,
   có TTL và audit.
3. Phát refresh token cho worker — **rủi ro nhất, tránh**.
4. Xuất ngược ra JSON plaintext "cho tương thích tạm" — **loại**: nó phá ngay
   tuyên bố hub là nguồn sự thật và tạo thêm một bản sao credential.

**Scope không tương đương.** Credential cũ xin `youtube.upload` + `youtube` +
`yt-analytics.readonly` (`youtube_auth.py:45`). Cổng 7 chỉ xin analytics/read-only.
Nên di trú KHÔNG chỉ là đổi nơi lưu: nếu đường upload cũng chuyển sang credential
của hub thì token mới KHÔNG đủ quyền. Phải khai báo *mục đích* cho credential,
hoặc chốt rõ hub chỉ sở hữu credential analytics còn upload là hệ khác.

### Cổng 7 — Kết nối kênh (luồng B)

Cần OAuth client **loại Web application** MỚI — cái Python dùng là Desktop app
loopback cổng 8734, không dùng lại được.

Ba endpoint, ba mô hình bảo mật KHÁC NHAU:
- `POST /channel-connections/start` — session + `Origin` fail-closed + JSON.
- `GET /oauth/youtube/callback` — **KHÔNG dựa vào `Origin`**; xác minh `state` +
  PKCE + ràng buộc phiên.
- `POST /channel-connections/:id/disconnect` — session + `Origin` + JSON.

`state` phải: mờ đục, ngẫu nhiên, **dùng một lần**, hết hạn ngắn, lưu server-side
hoặc ký, và ràng buộc đồng thời với phiên hiện tại, workspace đích, OAuth client,
ý định `CONNECT_CHANNEL`, và đích chuyển hướng cuối. Thêm PKCE. `code` chỉ dùng
một lần và chống dùng lại đồng thời.

**Sau khi đồng ý, hub CHƯA BIẾT kênh nào.** Hỏi lại YouTube API. Đừng chỉ lấy
`items[0]` như `youtube_auth.py:160`. Fail-closed khi: không có kênh; response sai
hình dạng; **scope THỰC CẤP thiếu scope bắt buộc**; hoặc token thuộc OAuth client khác.

**Kết nối lại là THAY THẾ, không phải từ chối.** Bản 3 ghi "kênh đã kết nối thì từ
chối" — điều đó làm cho việc khôi phục sau khi bị thu hồi trở nên BẤT KHẢ.
- credential `ACTIVE` → trả idempotent "đã kết nối", hoặc hỏi xác nhận xoay.
- `REAUTH_REQUIRED` / `REVOKED_BY_USER` → cho thay thế.
- Ghi credential mới và `SUPERSEDE` cái cũ trong CÙNG giao dịch, và chỉ sau khi
  token mới đã đổi được, scope đã kiểm đủ, channel ID đã xác minh.

**Khi người dùng thu hồi ở phía Google, hub KHÔNG được báo.** Chỉ biết khi refresh
thất bại. Nên: coi `invalid_grant` là lỗi TERMINAL → `REAUTH_REQUIRED`; không
retry vô hạn như lỗi mạng; dừng job phụ thuộc; cảnh báo yêu cầu kết nối lại; kiểm
sức khoẻ credential trước mỗi lịch chạy. Lưu ý 401 của access token KHÔNG đồng
nghĩa refresh token bị thu hồi — thử refresh có kiểm soát trước khi kết luận.
Ngắt kênh ở hub nên gọi endpoint thu hồi của Google theo kiểu best-effort, rồi
vẫn revoke ở local fail-closed.

**PHẢI XÁC MINH TRƯỚC KHI XÂY:** ghi chú `youtube_auth.py:7` nói refresh token
dùng được vô hạn — CHỈ đúng khi app Google đã Published hoặc Internal. Nếu đang ở
trạng thái *Testing*, Google cho refresh token hết hạn sau **7 ngày**. Chưa kiểm
trên Google Cloud Console thì cổng này `NOT_RUN`.

```
npm run test:gate -- tests/integration/channel-connect.test.ts
```
Ca bắt buộc: `state` sai/dùng lại/hết hạn bị từ chối; `state` của phiên khác bị từ
chối; PKCE sai bị từ chối; kênh thuộc workspace khác bị từ chối; scope thực cấp
thiếu bị từ chối; token lưu xuống ĐÃ MÃ HOÁ; kết nối lại thay thế đúng và cái cũ
thành `SUPERSEDED`; hai callback đồng thời chỉ một cái thắng; `invalid_grant` đẩy
sang `REAUTH_REQUIRED`; người không có membership không gọi được.

TRƯỢT khi: tin `channel_id` client gửi lên; lưu token trước khi cổng 5 xanh; hoặc
callback bị áp luật `Origin`/JSON làm hỏng luồng thật.

### Cổng 8 — Staging và Google thật

Không lệnh nào ở máy chứng minh được: đăng nhập Google thật; cookie `__Host-` sống
sót qua proxy/CDN thật; UI và API thật sự cùng site; kết nối một kênh thật và lấy
được số liệu bằng chính token đó; **thu hồi quyền thật ở Google rồi xem hub có
chuyển sang `REAUTH_REQUIRED` không**; **kết nối lại thật sau khi thu hồi**.

Chỉ kiểm đường hạnh phúc là chưa qua cổng này. Thiếu môi trường thì `NOT_RUN`.

### Cổng 9 — Handoff

```
npm ci && npm run typecheck && npm run build && npm run test:gate
```
`next build` chỉ chứng minh biên dịch — không chứng minh cookie qua proxy,
callback Google, hay topology cùng site. Đó là cổng 8.

Báo cáo tách BỐN trạng thái: `PASS` / `FAIL` / `NOT_RUN` / `OUT_OF_SCOPE`.

## 4. Runbook di trú từng kênh

Trạng thái "hub giữ kênh mới, Python giữ kênh cũ" **không được kéo dài vô hạn**.
Không có định tuyến nguồn và hạn cutover thì đó là HAI hệ thống production, không
phải một cuộc di trú. Rủi ro cụ thể khi để lâu: một kênh cũ vô tình kết nối lại
vào hub trong khi tệp cũ vẫn chạy → hai refresh token độc lập, hai lịch đồng bộ;
"ngắt kết nối" ở hub KHÔNG vô hiệu tệp Python, người vận hành tưởng đã ngắt mà
cron vẫn chạy; thu hồi ở Google làm hỏng một kho còn kho kia vẫn sống.

Mỗi kênh, theo đúng thứ tự:
1. Uỷ quyền lại vào hub.
2. Chứng minh consumer của hub lấy được dữ liệu ĐÚNG kênh đó.
3. Dừng scheduler/đường tệp cũ.
4. Kiểm không còn tiến trình nào dùng tệp — kể cả `twice_weekly_batch.py:112`.
5. Huỷ tệp cũ.
6. Chuyển `credential_source` sang `HUB`.

## 5. Ngoài phạm vi, ghi để pha sau khỏi điều tra lại

**Duyệt/từ chối kết quả phân tích.** `approval.entityType/entityId` là tham chiếu
ĐA HÌNH không có khoá ngoại (`audit.ts:54`); database chỉ ràng buộc
`actorType=USER` (`audit.ts:70`), không chứng minh `decidedById` là `user_account`
thật cùng workspace. Vá TRƯỚC khi mở endpoint duyệt.

**Đường upload.** Nếu chuyển sang credential của hub thì cần scope `youtube.upload`
— cổng 7 không xin scope đó.

## 6. Điều kiện "backend sẵn sàng"

1. Đúng một email đăng nhập được; đăng nhập hợp lệ mà không có membership thì
   thấy RỖNG; bảng `account` không chứa refresh token.
2. Principal READ chỉ thấy dữ liệu workspace của mình, và không route nào còn
   đọc `userAccount.workspaceId` legacy.
3. API v1 phục vụ COMPOSITE 3.0 và CÔNG KHAI số lượng bị loại.
4. Refresh token lưu mã hoá; SQL đọc thẳng không ra bản rõ.
5. **Kiến trúc tiêu thụ đã chốt và chứng minh** — kênh mới lấy được số liệu thật.
6. Thu hồi ở Google được phát hiện; kết nối lại khôi phục được.
7. Cổng 8 đã chạy — hoặc `NOT_RUN` được ghi rõ và KHÔNG gọi là production-ready.
8. Handoff ghi rõ trạng thái `credential_source` của từng kênh.
