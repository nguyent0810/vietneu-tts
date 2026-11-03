# creator_v2 — phần CODE của Youtube_Creator_V2

Nguồn: repo Youtube_Creator_V2, commit HEAD `0a49de88628b01a543114455118753e41e7758f4` (chỉ file git đang track).

## Cấu trúc
- `factory/` — pipeline sản xuất (publish, trend, ...)
- `webauto/` — tự động hóa web/Studio (analytics)
- `scripts/` — script vận hành (`tools/ticket` = tk đã ngừng, không chuyển)
- `motion/` — HyperFrames/stier: chỉ code, đã loại wav lớn
- `tests/` — pytest (kèm fixtures)
- `.githooks/`, `pyproject.toml`, `AGENTS.md` (tham khảo)

## Chạy test
`cd creator_v2 && python -m pytest -q tests`

## Chưa chuyển
`data/`, `bundles/`, `docs/`, `.tickets/`, `output/`, STATUS/README/CLAUDE gốc. Test phụ thuộc data/ sẽ lỗi/skip.

## Trùng chức năng cần hợp nhất sau
- YouTube upload/auth: `factory/publish.py` ↔ `youtube_upload.py` / `youtube_auth.py`
- Studio analytics: `webauto/studio` ↔ `youtube_analytics.py`
- Trend: `factory/trend` ↔ `hf_trends.py`
- HyperFrames: `motion/hf` ↔ `hyperframes_short/`

## Trạng thái test khi nhập (03/11/2026)
627 qua, 38 hỏng, 26 skip. Phần lớn test hỏng là do thiếu `data/` (chưa chuyển), gói `vnlunar` hoặc font. `tests/test_long_coverage.py` import `motion.long.ai_prompt`, nhưng file này chưa được track ở repo nguồn.

## Đồng bộ Trend Engine (03/11/2026)
`factory/trend` đã đồng bộ với V2 PR #36 (nhánh `fix/trend-fs-bud`, 4 commit gốc 69b8db0, b2209e7, d428bc9, cc088f0). Từ nay sửa trend làm ở repo này (`creator_v2/factory/trend`), không sửa ở Youtube_Creator_V2. Cần đặt biến môi trường `TREND_CONTACT` trước khi chạy.
