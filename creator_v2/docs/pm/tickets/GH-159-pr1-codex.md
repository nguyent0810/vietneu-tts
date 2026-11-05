# GH-159 · PR 1 (Codex): hồ sơ kênh chung, `channel_profile.py`, `mim`/`ck`/`cl.yaml`

Issue: https://github.com/nguyent0810/vietneu-tts/issues/159.

Thiết kế đã được chủ kênh duyệt ngày 05/11: `creator_v2/docs/pm/2026-11-05-thiet-ke-mot-workflow.md` trên nhánh `mimck/159-b1-thiet-ke` (PR #164). Nội dung cần cho việc này đã chép vào brief.

Bạn làm việc ở **gốc repo**, tức worktree này. Nhánh `mimck/159-pr1-channel-profile` tách từ `origin/main` `9cf55d4`.

**Hạn:** 90 phút.

## Mục tiêu
Một chỗ duy nhất để nhận biết kênh và nạp hồ sơ kênh. Thêm hồ sơ MIM/CK/CL, sửa hai hồ sơ có tên lệch. **Không đổi hành vi dựng của kênh nào.**

## Việc

### 1. Module mới `library/tools/channel_profile.py`
- `load(id) -> dict`.
  - Đọc `library/channels/<id>.yaml`. Nội dung là **JSON** nên dùng `json.loads`, không đổi định dạng.
  - Kiểm schema tối thiểu: `kenh` phải trùng stem; các khoá đang có code đọc phải đúng kiểu khi có mặt: `kenh` str, `ngach` list, `khuon` list[dict], `bao_ve` list, `assets`/`canh`/`typography`/`motion`/`sound`/`tts`/`kho_loc` dict.
  - Sai thì ném `ValueError` nêu rõ khoá nào sai.
- `ids() -> list[str]`: stem của mọi file `*.yaml` không bắt đầu bằng `_`.
- `resolve(item: dict | None = None, *, channel: str | None = None, slug: str | None = None) -> str`. Thứ tự tra:
  1. `item["channel"]` hoặc `item["kenh"]`. So khớp với stem, hoặc với `ten_hien_thi` và `alias` của từng hồ sơ, không phân biệt hoa thường.
  2. Tham số `channel` (lấy từ cờ `--channel`).
  3. `slug`: so với `slug_prefix` của các hồ sơ. Chỉ nhận khi **đúng một** kênh khớp.
  4. Không khớp, hoặc khớp nhiều kênh: ném `ValueError`. **Không có kênh mặc định.**
- **Tương thích ngược:** `load("_thu_lich_su")` trả hồ sơ `lich_su`. Ghi bảng ánh xạ tên cũ vào một dict hằng nhỏ, có comment ghi ngày.

### 2. Đổi tên và migration (chủ kênh đã duyệt)
- `git mv library/channels/_thu_lich_su.yaml library/channels/lich_su.yaml`. Nội dung không đổi (`kenh` đã là `"lich_su"`).
- `library/channels/vsd.yaml`:
  - đổi `kenh` thành `"vsd"`;
  - thêm `"ten_hien_thi": "Văn Sử Địa"` và `"alias": ["Văn Sử Địa"]`;
  - giữ nguyên mọi khoá khác.
- Sửa mọi chỗ đọc và mọi test đang dùng tên cũ (Learn AI đã dò):
  - `hf_sound.py:85`: chỉ sửa comment.
  - `library/tools/assets.py:189–256`:
    - bỏ đọc `_external.yaml`;
    - `lich_su` giờ thành `pham_vi` hợp lệ: cập nhật docstring;
    - giữ alias "Văn Sử Địa" ↔ "vsd" để manifest cũ có `pham_vi` "Văn Sử Địa" vẫn khớp.
  - `library/tools/lib.py:88–94`: kiểm `channel_names()` / `load_profile()` chạy đúng khi có thêm `lich_su`, `mim`, `ck`, `cl`.
  - `library/CHO_KENH_KHAC.md:11`: tài liệu.
  - Test:
    - `tests/test_assets.py` (khoảng dòng 722–760, 879, 964, 1009);
    - `tests/test_motion_picker.py:96`;
    - `tests/test_prompt_builder.py:185, 208`;
    - `tests/test_kinetic_presets.py:63`;
    - `tests/test_sound_director.py:4, 36, 73`;
    - `tests/test_studio_v3turbo.py:22`: đang assert `kenh == "Văn Sử Địa"`, sửa theo migration.
- Xong thì `git grep -n "_thu_lich_su"` chỉ còn hai loại chỗ: bảng tương thích trong `channel_profile.py`, và tài liệu cũ dưới `creator_v2/docs/pm/tickets/`.

### 3. Hồ sơ mới `library/channels/mim.yaml`, `ck.yaml`, `cl.yaml` (định dạng JSON)
Lấy giá trị đang hard-code. **Chỉ chép, không chọn giá trị mới:**
- `creator_v2/motion/long/build_long.py:104–125` (`_channels()`);
- `creator_v2/motion/stier/themes.py:100–161`;
- `creator_v2/motion/variety.py:30–45`;
- `creator_v2/factory/channels.py:31–58`: chỉ lấy `prefixes` và `pacing`. **Không** chép `creds` hay bất kỳ tên file credentials nào.
- `data/shorts_slots.json` (creator_v2): lưới slot.
- `_external.yaml`: `kho_loc` của từng kênh.

Khoá trong mỗi file:
- `kenh` = stem, `ten_hien_thi`, `alias` (để trống), `ngach`.
- `slug_prefix`: chỉ tiền tố **riêng** của kênh. `long-` là chung của MIM và CK, nên **không** đưa vào.
- `dung`:
  - MIM: `long {engine: "casewide", plugin: ["lab"]}`, `short {engine: "casefile"}`;
  - CK: `long {engine: "casewide", plugin: ["lab", "chart"]}`, `short {engine: "casefile"}`;
  - CL: `long {engine: "casewide", plugin: ["lab"]}`, `short {engine: "casefile"}`.

  Kiểm lại plugin theo cách `build_long.py:907-909` nạp `lab`/`chart`.
- `theme`:
  - `long`: lab / chart / mặc định của CL, theo code;
  - `short`: khoá trong `themes.py`;
  - `brand`.

  Đặt `accent` vào `typography.mau_nhan`; không lặp màu ở `theme`.
- `voice_profile {engine: "creator_v2", tham_so: {dan, trich, hoi?, fx?}}`. `fx` của CL ghi `"VOICE_FX_CL"` (tên hằng), không chép chuỗi.
- `anh`:
  - `ai {cho_phep, nhan_tren_khung: false, nhac_trong_mo_ta: false, credit: false}`, với `cho_phep` là true cho MIM/CK và false cho CL;
  - `cam_sa`: true cho MIM/CK.
- `kho_loc`: chuyển từ `_external.yaml`. License chỉ đặt ở đây.
- `luat_noi_dung`, chỉ là dữ liệu, chưa có cổng đọc:
  - CK: `cam_ma_co_phieu: true`, `nhan_bat_buoc {so_tu_dung: "VÍ DỤ GIẢ ĐỊNH"}`, `mo_ta_bat_buoc ["Nội dung giáo dục, không phải tư vấn đầu tư."]`;
  - cả ba kênh: `mo_ta_cam ["<", ">", "CẦN", "agent", "factcheck", "data/long"]`, `title_max: 60`.
- `khuon`: một mục cho mỗi dạng đang làm, gồm Long và Short. Mỗi mục có đủ trường `lib.lane_decision`/`enforce_lane` đọc (`ten`, `id`, `trang_thai: "active"`, `quyet_dinh: null`, …). Xem `bud.yaml` làm mẫu. Tên không trùng.
- `cong`: danh sách tên cổng đang chạy trong creator_v2, chỉ là dữ liệu.
  - Long: `floor {ho_so: "mim_ck" | "cl"}`, `variety`, `lint_html`, `factcheck`, `approved`.
  - Short: `preflight`, `script_lint`, `mix {max_chu_tron: 0.35}`.
- `upload {duong: "factory", pacing: [...], slot_short: [...]}`.

### 4. Bỏ `_external.yaml`
Xoá file sau khi `kho_loc` đã chuyển sang các file kênh và `assets.py` đã đọc từ đó.
- Giữ `merge_external` và CLI `merge-external`: đó là manifest máy ngoài, không phải hồ sơ.
- Cập nhật `library/schema/asset.schema.json:75` (mô tả).
- Nếu sửa chữ ký `find_assets` hoặc cách nạp `kho_loc` thì phải giữ tương thích với `library/tools/image_request.py` của PR #162 (`kho_loc` truyền vào bằng tham số).

### 5. Test mới `tests/test_channel_profile.py`
- Mọi `library/channels/*.yaml` parse được bằng `json.loads`.
- `kenh == stem` với mọi hồ sơ kênh.
- Các khoá đang có code đọc đều đúng kiểu.
- Tên trong `khuon` không trùng.
- `resolve`:
  - `{"channel": "CK"}` → `ck`;
  - `{"kenh": "Văn Sử Địa"}` → `vsd`;
  - `slug="ck-abc"` → `ck`;
  - `slug="long-abc"` → `ValueError` (mơ hồ);
  - `{}` → `ValueError`.
- `load("_thu_lich_su")["kenh"] == "lich_su"`.
- Không file hồ sơ nào chứa chuỗi `creds` hoặc `.json"` của credentials.
- **So khớp với bảng hard-code**, để có bằng chứng "chỉ chép": giọng/brand/theme của MIM/CK/CL trong yaml phải bằng giá trị `build_long._channels()` trả về. Import được thì import; không import được thì đọc file rồi so chuỗi.

### 6. Chạy test
Chạy toàn bộ các file test đã sửa hoặc thêm, cùng: `tests/test_library_cards.py`, `tests/test_sound_director.py`, `tests/test_assets.py`, `tests/test_motion_picker.py`, `tests/test_prompt_builder.py`, `tests/test_kinetic_presets.py`, `tests/test_studio_v3turbo.py`, `tests/test_channel_profile.py`. Nếu có `tests/test_image_request.py` thì chạy luôn.
- Lệnh: `python -m pytest <files> -q -p no:cacheprovider`.
- Test nào cần Chrome/puppeteer mà máy không có thì ghi rõ, không tắt test.

## Được ghi
- `library/tools/channel_profile.py` (mới).
- `library/channels/*`: mới `mim.yaml`, `ck.yaml`, `cl.yaml`; đổi tên `lich_su.yaml`; sửa `vsd.yaml`; xoá `_external.yaml`.
- `library/tools/assets.py`, `library/tools/lib.py` (nếu cần), `hf_sound.py` (comment), `library/CHO_KENH_KHAC.md`, `library/schema/asset.schema.json`.
- Các test liệt kê ở trên, cộng `tests/test_channel_profile.py`.
- Báo cáo: `creator_v2/docs/pm/tickets/GH-159-pr1-codex-report.md`.

**Không:**
- sửa code dựng trong `creator_v2/` (`build_long.py`, `themes.py`, … là PR 2);
- sửa `hf_batch_render.py`, `hyperframes_bridge.py`, `studio.py`;
- render, upload, đổi lịch;
- commit, push;
- đọc credentials hoặc in biến môi trường.

## Báo cáo
- Danh sách file đã đổi, mỗi file một dòng nói đổi gì.
- Kết quả pytest: dán dòng tổng.
- Kết quả `git grep -n "_thu_lich_su"` sau khi sửa.
- Giá trị nào trong `mim`/`ck`/`cl.yaml` phải tự quyết vì code không có. Liệt kê để Lead duyệt.

Câu trả lời cuối: tối đa 3 dòng.
