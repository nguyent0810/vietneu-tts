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

## Chạy MIM/CK trên máy mới
1. Clone repo, rồi `cd creator_v2`.
2. Cài gói (giống job CI `creator-v2-tests`; `vnlunar` ghim 1.0.4):
   `pip install "pytest>=8.0" "httpx>=0.27" "vnlunar==1.0.4" numpy scipy "pillow>=10" requests soundfile`
3. Đặt biến môi trường (media lớn không nằm trong git):
   - `YT_CREDS_DIR=<thư mục credential kênh>` (không bao giờ nằm trong repo)
   - `CREATOR_MEDIA_ROOT=<thư mục media, cùng bố cục creator_v2>`
4. `python scripts/setup_local.py` nối `motion/hf/assets/{clips,cases,long}`, `output/music`, `.ref` (junction trên Windows, symlink nơi khác) và chép `motion/stier/ambience/*.wav`. Không ghi đè hay xóa gì: đích đã có thì báo "đã có" và bỏ qua.
5. `python scripts/setup_local.py --check` chỉ báo cáo (mã thoát 0 nếu đủ, 1 nếu thiếu). Không in giá trị `YT_CREDS_DIR`.
6. Chạy thử: `python motion/stier/build.py <slug> --preflight`.

### Ngày chuyển hẳn từ V2
- [ ] Dừng mọi lượt chạy trên V2.
- [ ] Chép `bundles/` mới nhất (bị `.gitignore` bỏ qua, không commit) và mọi thay đổi `data/` vào repo này.
- [ ] Chuyển `output/` đang có (nếu có) sang thư mục sao lưu, rồi chạy `python scripts/setup_local.py --link-output` để nối cả `output/` của V2 (giữ nghiên cứu/render Long đang có). Nếu `output/` vẫn là thư mục thật, script chỉ cảnh báo và không nối.
- [ ] Dựng thử một Short, không upload.
- [ ] Từ đó chỉ dùng repo này.

## Chưa chuyển
`data/`, `bundles/`, `docs/`, `.tickets/`, `output/`, STATUS/README/CLAUDE gốc. Test phụ thuộc data/ sẽ lỗi/skip.

## Trùng chức năng cần hợp nhất sau
- YouTube upload/auth: `factory/publish.py` ↔ `youtube_upload.py` / `youtube_auth.py`
- Studio analytics: `webauto/studio` ↔ `youtube_analytics.py`
- Trend: `factory/trend` ↔ `hf_trends.py`
- HyperFrames: `motion/hf` ↔ `hyperframes_short/`

## Trạng thái test khi nhập (03/11/2026)
627 qua, 38 hỏng, 26 skip. Phần lớn test hỏng là do thiếu `data/` (chưa chuyển), gói `vnlunar` hoặc font. `tests/test_long_coverage.py` import `motion.long.ai_prompt`, nhưng file này chưa được track ở repo nguồn.

**Cập nhật (ticket 108):** job CI riêng `creator-v2-tests`. 31 test đỏ + 1 lỗi thu thập đã được phân loại: 30 test + 1 module skip có lý do (`tests/_needs.py`: thiếu `data/`, `bundles/FS`, `output/music`, font, `docs/`, `ai_prompt.py`), 1 test `xfail` (lỗi thật: 7 CLI chưa gọi `utf8_console()`). Kết quả: 633 passed, 58 skipped, 1 xfailed, 0 failed. CI cần `vnlunar==1.0.4` (1.0.5 làm 2 test `test_claims` đỏ).

**Cập nhật (#100 bước 2):** đã nhập `motion/long/ai_prompt.py` từ V2 và bỏ `importorskip` trong `tests/test_long_coverage.py`. Module này giờ chạy 4 test thay vì skip.

## Đồng bộ Trend Engine (03/11/2026)
`factory/trend` đã đồng bộ với V2 PR #36 (nhánh `fix/trend-fs-bud`, 4 commit gốc 69b8db0, b2209e7, d428bc9, cc088f0). Từ nay sửa trend làm ở repo này (`creator_v2/factory/trend`), không sửa ở Youtube_Creator_V2. Cần đặt biến môi trường `TREND_CONTACT` trước khi chạy.
