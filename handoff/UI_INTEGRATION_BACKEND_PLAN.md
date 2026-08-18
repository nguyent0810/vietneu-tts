# Kế hoạch backend cho tích hợp UI — theo CỔNG

> Pha này là **BACKEND-ONLY**. UI do đội khác dựng ở pha sau, sau handoff.
> Trạng thái: đã qua HAI vòng phản biện Codex CLI (2026-08-18).
> Lập trên cây `43722a4`, ngày 2026-08-18.

## 0. Ba quyết định đã đóng

| Quyết định | Chọn | Vì sao |
|---|---|---|
| Phạm vi SSO | **Google OIDC, chỉ `openid email profile`** | Hub KHÔNG gọi API Google nào — đã kiểm toàn bộ `apps/hub/src`. Dữ liệu YouTube vào hub qua worker (`api/v1/sync/ingest`), do `youtube_sync.py` lấy bằng refresh token riêng từng kênh. Xin scope YouTube ở hub sẽ tạo NGUỒN SỰ THẬT THỨ HAI cho dữ liệu đã có. |
| Origin của UI | **Cùng site** (Next.js phục vụ luôn UI) | Xoá CORS allowlist và kiểm `Origin` cross-site. KHÔNG xoá được chống CSRF — xem §2.6. |
| Action nghiệp vụ | **Không có trong pha này** | Chỉ `logout`/revoke. Read API trả `allowedActions: []`. |

Điều kiện XÉT LẠI quyết định 1: chỉ khi hub phải tự gọi YouTube API (upload, sửa
metadata từ UI). Đọc số liệu thì không cần — số liệu đã ở trong database.

## 1. Hiện trạng đã kiểm chứng

Bề mặt HTTP: đúng 5 route, không route đọc nào — `health`, `sync/start`,
`sync/ingest`, `sync/finish`, `sync/report`. Không `page.tsx` nào.

Tầng người dùng là MÃ CHẾT: `authenticateUser()`, `requireScope()`,
`assertCanApprove()` tồn tại nhưng KHÔNG được gọi ở đâu ngoài `auth.ts`.
`user_account` = 0 hàng, `user_api_token` = 0 hàng, không có script phát token
người dùng, `route.ts` chỉ có `withWorkerAuth`.

`user_account` nhận diện bằng `email` unique — CHƯA có `(issuer, subject)`.

Dữ liệu: 1 workspace, 3 kênh, 1.073 video, 11.119 metric ngày, 156.395 feature
value, 15 analysis_run (mới nhất 2026-07-30), 116 cursor_analysis_result
(69 ANALYSIS + 47 COMPOSITE).

**47 hàng COMPOSITE thuộc hai thế hệ schema không tương thích:**
`schema_version=1.0` → 32 hàng, `schema_version=3.0` → 15 hàng.

Rỗng hoàn toàn: `analysis_result`, `approval`, `content_item`,
`content_revision`, `critique`, `evaluation`, `score`.

## 2. Nguyên tắc bắt buộc

Kế thừa từ Phase 4.1, không được nới:

1. Chứng minh bằng CHẠY. Không grep, không khẳng định cấu trúc.
2. "Không kiểm được" khác "đã kiểm và đạt". Cấm skip im lặng ở mọi tầng —
   kể cả tầng API: giấu 32 hàng schema 1.0 cũng là một kiểu skip im lặng.
3. Cổng chạm database phải độc quyền. Bộ test TRUNCATE bảng giữa các ca.
4. Bất biến quan trọng phải có TRIGGER ở database, không chỉ kiểm ở route.
   Route là lớp tiện lợi; database là lớp cưỡng chế.
5. Đổi hợp đồng thì nâng phiên bản. Không gộp dữ liệu hai bên phiên bản.
6. **`SameSite=Lax` KHÔNG phải cơ chế chống CSRF.** Codex vòng 2 bắt đúng chỗ
   tôi sai: "cùng site" bao gồm cả subdomain anh em, và `Lax` chỉ chặn cross-SITE
   chứ không chặn same-site-khác-origin. CORS cũng không ngăn được form POST.
   Nên mọi mutation dùng cookie — hiện là `logout`/revoke — vẫn phải có:
   - Cookie **host-only**, tên tiền tố `__Host-`, KHÔNG đặt thuộc tính `Domain`.
   - Kiểm `Origin` khớp một origin cố định; header thiếu hoặc lạ thì fail-closed.
   - Chỉ nhận `Content-Type: application/json`, từ chối form/simple request.
   `state` và `nonce` của OIDC là chuyện khác và vẫn bắt buộc.

## 3. Các cổng

Thứ tự dưới đây đã sửa HAI phụ thuộc ngược mà Codex vòng 2 chỉ ra.

### Cổng 1 — Cấu trúc và bất biến GHI ở tầng database

Phạm vi HẸP LẠI so với bản đầu: cổng này chỉ chứng minh những gì một câu INSERT/
UPDATE chứng minh được. "Session đã revoke thì không đăng nhập được" KHÔNG thuộc
về đây — một hàng revoked vẫn là một hàng hợp lệ; vô hiệu hoá là hành vi của
đường xác thực, và nó được chứng minh ở cổng 2.

Bảng cần có: danh tính OAuth `(issuer, subject)` UNIQUE tách khỏi `user_account`;
membership theo workspace mang role; session (hash, expiry, revoke, metadata
xoay); allowlist/lời mời.

Ưu tiên **khoá ngoại tổ hợp `(resource_id, workspace_id)`** thay vì trigger ở đâu
diễn đạt được — repo đã dùng rộng rãi mẫu này, ví dụ `cursor-analysis.ts:399`.
Trigger chỉ dành cho chuyển trạng thái và kiểm liên bảng mà FK/CHECK không nói được:

- Lời mời chỉ tiêu thụ ĐƯỢC MỘT LẦN, nguyên tử; không quay ngược về chưa dùng.
- Vô hiệu user hoặc gỡ membership thì session liên quan bị revoke trong CÙNG giao dịch.
- Danh tính `(issuer, subject)` đã liên kết thì KHÔNG đổi sang user khác được.
- Một session có tối đa MỘT session kế nhiệm; session cũ bị revoke cùng giao dịch.
- KHÔNG "unrevoke" được bằng SQL trực tiếp.

Hết hạn theo thời gian thì đừng giả vờ trigger lo được: xác thực vẫn phải kiểm
`expires_at <= now()` ở MỖI request.

Bằng chứng CHẤP NHẬN:
```
npm run typecheck && npm run test:migrations
npm run test:gate -- tests/integration/auth-schema.test.ts
```
Phải bằng INSERT/UPDATE ĐỐI KHÁNG, không đọc `information_schema`: subject trùng
bị chặn; membership cross-workspace bị chặn; lời mời tiêu thụ lần hai bị chặn;
đổi chủ danh tính bị chặn; unrevoke bằng SQL bị chặn.

TRƯỢT khi: thiếu database, có ca bị skip, migration không chạy được từ zero,
hoặc một câu SQL trực tiếp vượt qua được bất biến.

### Cổng 2 — Đăng nhập Google, vòng đời session, và route `/me` THẬT

Endpoint: khởi tạo login, callback, **`/me` (route sản phẩm, không phải route test)**,
logout/revoke. **KHÔNG phát PAT.**

`/me` phải là route thật vì cổng 3 cần một route sản phẩm để chứng minh
`withUserAuth`, mà các route đọc chỉ ra đời ở cổng 4. Đây là cách gỡ phụ thuộc
ngược, thay vì gộp cổng 3 vào cổng 4.

`revoke` phải định nghĩa RÕ phạm vi: chỉ session hiện tại, hay mọi session của
user. Hai thứ khác nhau và handoff phải nói cái nào được hỗ trợ.

Chống lạm dụng: `consumeRateLimit` đã có nhưng chỉ nối vào `withWorkerAuth` và
khoá theo `machineId:capability` (`route.ts:60`) — vô dụng cho login vì lúc đó
chưa có principal. Cần khoá theo IP và theo `(issuer, subject)`.

Ghi audit: `audit_event` hiện CHỈ được ghi bởi `sync/finish`. Login thành công,
login thất bại, logout và revoke đều phải sinh audit — và audit KHÔNG được chứa
token, mã, hay cookie.

Bằng chứng CHẤP NHẬN:
```
npm run test:unit -- tests/unit/oidc.test.ts tests/unit/session.test.ts
npm run test:gate -- tests/integration/auth-flow.test.ts
```
Ca bắt buộc: sai `state`, sai `nonce`, sai `iss`, sai `aud`, `exp` quá hạn,
`email_verified=false`, subject chưa được mời, tài khoản `disabledAt`, session
hết hạn, session đã revoke, xoay session sau đăng nhập, cờ cookie `__Host-` +
`HttpOnly` + `Secure` + `SameSite=Lax`, `Origin` sai bị từ chối, logout có hiệu lực.

TRƯỢT khi: token xuất hiện trong URL/body/localStorage; callback tự cấp ADMIN;
hoặc test mock được trình bày như bằng chứng tích hợp thật.

### Cổng 3 — `withUserAuth` và cách ly workspace

Chứng minh qua route `/me` sản phẩm của cổng 2. `requireScope` hết là mã chết.

Membership đổi thì session phải phản ứng — chốt một trong hai và kiểm đúng cái
đã chốt: (a) xác thực đọc membership LIVE mỗi request, hoặc (b) đổi membership
thì revoke session ngay trong giao dịch. Không được để mơ hồ.

Bằng chứng CHẤP NHẬN:
```
npm run test:unit -- tests/unit/user-route-auth.test.ts
npm run test:gate -- tests/integration/workspace-isolation.test.ts
```
Ma trận: ẩn danh, session đã revoke, user bị vô hiệu, member READ, member
workspace A đọc ID thuộc workspace B, ADMIN, và membership bị gỡ GIỮA phiên.

TRƯỢT khi: chỉ test helper mà không đi qua route sản phẩm; workspace suy ra từ
request thay vì từ principal; hoặc tài nguyên workspace khác trả lỗi KHÁC NHAU
đủ để dò được sự tồn tại.

### Cổng 4 — Read API có ý thức phiên bản

Phạm vi: danh sách kênh, danh sách lần phân tích, chi tiết một COMPOSITE kèm bằng chứng.

Response danh sách phải KÊ KHAI phần không phục vụ được:
```json
{
  "contractVersion": "1",
  "servedSchemaVersions": ["3.0"],
  "excluded": { "unsupportedSchemaVersions": { "1.0": 32 } },
  "allowedActions": []
}
```
Chi tiết một hàng 1.0 trả lỗi CÓ KIỂU `UNSUPPORTED_RESULT_SCHEMA` kèm phiên bản.
KHÔNG trả 404 — 404 nói "không có", trong khi sự thật là "có nhưng hợp đồng này
không phục vụ". KHÔNG tự nâng cấp payload 1.0 thành hình dạng 3.0.

**HAI bằng chứng TÁCH RỜI** — Codex vòng 2 bắt đúng: integration test chạy trên
database test đã TRUNCATE với fixture riêng (`tests/helpers/db.ts`, `tests/setup.ts`),
nên nó KHÔNG BAO GIỜ chứng minh được con số 32 trong database thật.

1. Integration: `excluded` khớp fixture do chính test tạo ra.
2. Kiểm toán CHỈ ĐỌC trên dữ liệu thật: phân bố `schema_version` thật khớp
   response thật. Không có môi trường thì trạng thái là `NOT_RUN`, KHÔNG phải PASS.

**Neo hợp đồng độc lập:** lưu fixture JSON của `contractVersion: "1"` đã phát
hành, và một test tương thích đọc fixture ấy. Sửa DTO và sửa số phiên bản trong
CÙNG commit vẫn xanh nếu không có neo này — chính sách không phải bằng chứng.
Thay đổi phá vỡ phải thêm v2, KHÔNG được sửa fixture v1.

```
npm run test:gate -- tests/integration/read-api.test.ts
npm run test:unit -- tests/unit/contract-v1-compat.test.ts
```

TRƯỢT khi: 32 hàng biến mất không dấu vết; API tự diễn giải 1.0 như 3.0; fixture
v1 bị sửa thay vì thêm v2; hoặc số liệu fixture được trình bày như số liệu thật.

### Cổng 5 — Action nghiệp vụ: `OUT_OF_SCOPE_BY_PRODUCT_DECISION`

Đổi nhãn từ `BLOCKED` sang `OUT_OF_SCOPE`. Lý do: quyết định sản phẩm ĐÃ đóng là
"không làm action ở pha này", nên gọi nó là blocked sẽ báo sai rằng dự án đang
tắc vì thiếu quyết định.

NHƯNG handoff vẫn phải ghi rõ: yêu cầu ban đầu của chủ dự án có "các action kèm
theo", và nó được HOÃN CÓ CHỦ Ý vì chưa đặc tả được, chứ không phải đã đáp ứng.

Ghi lại để pha sau khỏi điều tra lại: `approval.entityType/entityId` là tham
chiếu ĐA HÌNH không có khoá ngoại (`audit.ts:54`), và database chỉ ràng buộc
`actorType=USER` (`audit.ts:70`) — nó KHÔNG chứng minh `decidedById` là một
`user_account` thật cùng workspace. Vá chỗ này TRƯỚC khi mở bất kỳ endpoint duyệt nào.

### Cổng 5b — Topology staging và Google thật

Cổng RIÊNG, vì không lệnh nào ở máy chứng minh được nó.

Phải chạy trên staging: đăng nhập bằng tài khoản Google thật; cookie sống sót
qua proxy/CDN thật; `__Host-` thực sự được trình duyệt chấp nhận; UI và API
thật sự cùng site; header bảo mật đúng như khai báo.

Thiếu credential hoặc môi trường thì `NOT_RUN`. Chưa chạy cổng này thì KHÔNG
được nói "SSO đã kiểm chứng".

### Cổng 6 — Handoff

```
npm ci && npm run typecheck && npm run build
npm run db:migrate && npm run test:gate
```
Chạy độc quyền trên `hub_ci`.

`next build` chỉ chứng minh biên dịch và đóng gói. Nó KHÔNG chứng minh cookie
thật qua proxy, callback Google, header bảo mật, hay topology cùng site — đó là
việc của cổng 5b.

Báo cáo handoff tách BỐN trạng thái, không gộp:
`PASS` / `FAIL` / `NOT_RUN` (thiếu credential hoặc môi trường) /
`OUT_OF_SCOPE` (đã quyết định không làm ở pha này).

Giao cho đội UI: `contractVersion` và fixture v1, yêu cầu cookie/origin, danh mục
mã lỗi, số lượng dữ liệu bị loại kèm lý do, và danh sách action được hỗ trợ
(hiện chỉ có `logout`/revoke).

## 4. Điều kiện "backend sẵn sàng"

Pha này XONG khi và chỉ khi:

1. Người đã được cấp membership đăng nhập được bằng Google và nhận session
   cookie; người ngoài bị từ chối; chưa có allowlist thì fail-closed.
2. Principal READ chỉ thấy dữ liệu workspace của mình — chứng minh bằng ca đối kháng.
3. API v1 phục vụ COMPOSITE schema 3.0 và CÔNG KHAI số lượng bị loại.
4. Logout/revoke có hiệu lực thật, và phạm vi của "revoke" được ghi rõ.
5. Cổng 5b đã chạy trên staging — hoặc trạng thái `NOT_RUN` được ghi rõ và
   KHÔNG được gọi là production-ready.
6. Handoff ghi rõ pha này không có action nghiệp vụ, và đó là hoãn có chủ ý
   chứ không phải đã đáp ứng yêu cầu ban đầu.
