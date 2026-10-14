# Planning Package — FROZEN

Gói tài liệu kế hoạch được **đóng băng** tại thời điểm
`ARCHITECTURE_APPROVED_FOR_IMPLEMENTATION`, trước khi bắt đầu Phase 0.

Lý do đóng băng: vòng review toàn tài liệu đã chạy 29 vòng và đứng yên ở một
điểm bất động (~2 HIGH/vòng, không có xu hướng giảm) — 44% phát hiện là do
chính các bản sửa trước sinh ra. Vòng Architecture Review có phạm vi hẹp cuối
cùng tìm được **đúng 1 lỗi thật** (thứ tự promote artifact vi phạm partial
unique index), đã sửa. Từ đây trở đi, **code là nguồn sự thật**, không phải
tài liệu.

---

## 1. Manifest (SHA-256 rút gọn 16 ký tự, tại thời điểm đóng băng)

| File | SHA-256 (16) | Dòng |
|---|---|---|
| `API_CONTRACT_PLAN.md` | `6fa1d47896d95745` | 2059 |
| `CODEX_PLAN_REVIEW.md` | `166335ea3e564da7` | 1154 |
| `ALGORITHM_VERSIONING_PLAN.md` | `3b1051b8e26db83e` | 947 |
| `STORAGE_STRATEGY.md` | `41e21ec8f899fe1f` | 739 |
| `DATA_MODEL_PLAN.md` | `458f766bb582f646` | 666 |
| `REPOSITORY_ASSESSMENT.md` | `ff00a148cb6ca1ed` | 531 |
| `API_AND_WORKER_PROTOCOL.md` | `c569816c6d7dccaa` | 465 |
| `IMPLEMENTATION_ROADMAP.md` | `b7fae7c97bd170de` | 377 |
| `TARGET_ARCHITECTURE.md` | `4c5171d8b6324eea` | 370 |
| `LEGACY_IMPORT_AND_SYNC_PLAN.md` | `53b9881e1013b343` | 333 |
| `TEST_STRATEGY.md` | `8cd5e502d9ee610a` | 301 |
| `FINAL_RECOMMENDATION.md` | `48541abbea303e32` | 233 |
| `BACKEND_MVP_SPEC.md` | `7416a9827a7e2978` | 215 |
| `RISK_REGISTER.md` | `3f69e9b487d1b78e` | 109 |

**Tổng: 14 file, 8.499 dòng.**

Kiểm chứng lại bất cứ lúc nào:

```sh
cd docs/content-hub && shasum -a 256 API_CONTRACT_PLAN.md ... | cut -c1-16
```

---

## 2. File KHÔNG thuộc diện đóng băng

Đây là tài liệu **sống**, cập nhật theo tiến độ triển khai:

| File | Vai trò |
|---|---|
| `PLANNING_FROZEN.md` | chính file này |
| `PHASE0_SECURITY_FOUNDATION.md` | bằng chứng Phase 0 |
| `IMPLEMENTATION_ACCEPTANCE_CRITERIA.md` | 7 rủi ro → tiêu chí nghiệm thu |
| `PHASE*_REPORT.md` | báo cáo từng phase (sinh dần) |
| `CODEX_PHASE_REVIEW.md` | log review từng phase (sinh dần) |

---

## 3. Quy tắc sửa tài liệu đã đóng băng

Chỉ được sửa file trong manifest khi **cả hai** điều kiện sau đúng:

1. Việc triển khai phát hiện tài liệu **sai về mặt kỹ thuật** (không phải khác
   cách diễn đạt, không phải thiếu chi tiết, không phải đặt tên chưa nhất quán).
2. Sai sót đó dẫn tới **code sai** nếu cứ làm theo.

Khi sửa, bắt buộc:
- Ghi một dòng vào §4 bên dưới: file, lý do, phase phát hiện.
- Cập nhật hash trong manifest.

**Không sửa** vì: câu chữ, thuật ngữ chưa thống nhất giữa các file, refactor
tuỳ chọn, hay để "cho khớp với code". Nếu code khác tài liệu mà code đúng thì
**code thắng** — ghi chú vào báo cáo phase, không viết lại kế hoạch.

---

## 4. Nhật ký sửa đổi sau đóng băng

| Ngày | File | Phase | Lý do (phải là lỗi kỹ thuật) | Hash mới |
|---|---|---|---|---|
| — | — | — | *(chưa có)* | — |
