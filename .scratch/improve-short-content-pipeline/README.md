# improve-short-content-pipeline

Branch: `feat/improve-short-content-pipeline` (tách từ `origin/feat/content-hub-backend`, upstream đã gỡ).

## File

- `research.md` — sự thật về code/dữ liệu hiện có
- `interview.md` — nhật ký grill
- `decisions.md` — quyết định D1–D91 (source of truth cho quyết định)
- `spec.md` — spec 1: instrumentation Content Quality (không phụ thuộc anchor)
- `spec-2.md` — spec 2: instrumentation Script Quality (không phụ thuộc anchor), đã duyệt
- `tickets/` — Spec 1: 01, 02, 03, 04, 05a, 05b, 06, 07, 08, 09, 10; Spec 2: 11–20
- Glossary: `/CONTEXT.md`; agent setup: `/AGENTS.md`, `/docs/agents/`

## Trạng thái (2026-09-28)

- Grill Content Quality Model: xong khung; anchor/threshold chờ baseline + labels.
- Spec 1 + tickets: đã duyệt. Frontier: 01, 02, 07, 08, 09.
- Grill Script Quality Model: xong 3 vòng (D58–D81); anchor/threshold chờ baseline + labels.
- Phạm vi (D82): chỉ Content Creator + Audio Script Creator. Không mở Audio Quality/Pipeline Reliability.
- Spec 2 + tickets 11–20: đã duyệt (D83–D92).
- Implementation Spec 1 (01–10) + Spec 2 (11–20): xong, mỗi ticket có grok review OK, đã push lên `feat/improve-short-content-pipeline`.
- Tiếp theo: người vận hành đặt baseline raw (`baseline/raw/`, gitignore) + chạy fetch retention/traffic (OAuth) → Baseline snapshot + labels → anchor/threshold cho Content và Script. Không viết anchor trước baseline.
- Lỗi CI còn lại là lỗi môi trường có sẵn từ trước (file BGM, content repo clone, font thumbnail, asset cache, secret scan `hub-ci.yml`), không do các ticket này.
- Phát hiện khi làm: CL case pipeline còn token `[F...]` trong script trước TTS → S8 giờ chặn (cần strip ở generator); script staged kiểu cũ không có Quality record sẽ bị chặn trước TTS/upload.

## Dependency tickets

Spec 1: 02→03, 02→04, 02→05a→05b, 03+04+05b→06, 09→10. 01 là prerequisite vận hành của 04, 05a, 05b, 06.

Spec 2:

```
11 ─────────┐
12 ─────────┤
13 ─────────┼──→ 14 ──→ 17
02 ─────────┘      │
                   ├──→ 18   (18 cũng ← 13)
                   └──→ 19
13 ─→ 15
14 + 15 + 03 + 04 + 05b ─→ 16
10 + 11 + 12 ─→ 20
```

01 là prerequisite vận hành của 15, 16.

**Frontier:** tất cả ticket đã xong.
- Ticket 10 mở rộng với `script_provenance` (D78–D81).
- Người vận hành cần cung cấp: `output/shorts/` từ máy production + export video/metrics từ Hub vào `baseline/raw/` (gitignore).

## Điểm xuất phát vòng Script Quality (sau `/compact`)

- Content Quality hỏi: "Nội dung có đáng xem và đáng tin không?"
- Script Quality hỏi: "Cách viết để đọc có giúp nội dung đó được truyền đạt rõ, tự nhiên và giữ người xem không?"
- Bắt đầu từ objective/model. Chưa bàn emotion tag, từ điển phát âm, pause marker, TTS engine hay code seam (D57).
- Giữ nguyên Content Quality chưa calibration: không tự đặt anchor/threshold khi chưa có baseline + labels.
