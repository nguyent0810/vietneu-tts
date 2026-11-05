# GH-159 B1: builder BUD/FS/VSD chỉ có trên Mac

Số liệu này do phiên Learn AI (Lead vietneu-tts) đo trên Mac ngày 05/11/2026 rồi gửi qua tin nhắn. Máy Windows không kiểm lại được.

Builder nằm ở `output/cl_staging/*/build_*.py` và bị gitignore. #140a đang đưa chúng vào repo thành `shortbuild/` và `builders/short/`.

## Số lượng
Tổng 90 builder:

| Thư mục | Số builder | Nội dung |
|---|---:|---|
| `long/` | 56 | Long BUD/FS |
| `grok/` | 25 | Short BUD/FS |
| `long_lab/` | 6 | |
| khác | 3 | |

26 builder có sửa trong 14 ngày gần nhất.

## Cách builder gọi render
| Cách gọi | Số builder |
|---|---:|
| Chỉ ghi `plan_*.json`, rồi Lead chạy `hf_batch_render.py <dir> --only <id>` | 68 |
| Import `hf_batch_render` để dùng hàm (TTS, lint, ghi plan) | 17 |
| Import `hf_batch_render` và `hyperframes_bridge`, render trực tiếp | 4 |
| Gọi CLI | 1 |

Entry point render thật là `hf_batch_render.py`. Builder chủ yếu chỉ sinh plan.

## Hàm `hf_batch_render` được builder gọi
Đếm số lần xuất hiện:

| Hàm | Số lần |
|---|---:|
| `render_tts` | 15 |
| `bare_lines` | 11 |
| `pacing` | 8 |
| `zodiac_naming_errors` | 6 |
| `crowded_chi_lines` | 6 |
| `integrity_issues` | 4 |
| `short_tone_issues` | 4 |
| `save_plan_rows` | 4 |
| `voice_for` | 3 |
| `reveal_issues` | 2 |

## Module khác được builder import
| Module | Số builder | Dùng để |
|---|---:|---|
| `hf_music` | 17 | nhạc theo chương, sổ nhạc |
| `hf_novelty` | 7 | chống trùng |
| `hyperframes_bridge` | 2 | |
| `studio`, `hf_qa`, `hf_sound`, `hf_voice` | 1 mỗi module | |

## Loại cảnh `longform.js` mà plan thật dùng
Đếm theo `visuals[].type` trên 722 row plan ở `long/`, `bud/`, `fs/`:

| Loại cảnh | Số lần |
|---|---:|
| word | 993 |
| studio | 706 |
| quote | 519 |
| ledger | 400 |
| list | 329 |
| compare | 288 |
| ask | 281 |
| illus | 193 |
| stamp | 158 |
| stat | 109 |
| timeline | 106 |
| scroll | 90 |
| dialog | 82 |
| chiwheel | 56 |
| bagua | 53 |
| lookup | 49 |
| doc | 46 |
| wheel | 46 |
| relic | 45 |
| museum | 35 |
| elements | 33 |
| shadow | 33 |
| map | 26 |
| teaser | 25 |
| years | 25 |

## Bố cục ảnh
Đếm theo `media[].layout` hoặc `kind`:

| Bố cục | Số lần |
|---|---:|
| image | 2487 |
| commons | 832 |
| full | 141 |
| video | 128 |
| card3d | 122 |
| frame | 122 |
| local | 107 |
| polaroid | 96 |
| depth | 91 |
| pinned | 90 |
| openverse | 38 |
| museum | 31 |

## Style/lane của row
| Style/lane | Số row |
|---|---:|
| tuong | 133 |
| tuoi | 115 |
| phap | 84 |
| niem | 75 |
| long | 68 |
| doi | 66 |
| nhao | 27 |
| kinhdich | 26 |
| nguhanh | 25 |
| hoangdao_daily | 22 |
| lich | 19 |
| ngaytot | 15 |

## Cặp so sánh cho B1
- **Long:** `creator_v2/motion/hf/assets/engine/casewide.js` so với `hyperframes_short/compositions/longform.js` (Long BUD/FS).
- **Short:** `casefile.js` so với `hyperframes_short/studio/` (Short BUD/FS).
- **Danh mục cảnh BUD/FS đầy đủ:** skill `.claude/skills/motion-library`.

---

# Phần 2/2: ma trận audit #140

Nguồn là file `_140_matrix_ref.md`, chỉ có trên Mac. Learn AI tóm tắt và gửi lại ngày 05/11.

Audit tĩnh trên `origin/main` `fa6b738`, ngày 04/11.
- "DÙNG" chỉ nghĩa là có lời gọi tĩnh trong code, chưa chứng minh đã chạy thật.
- Sau audit đã merge thêm #148–#158. Ticket 140a–d chưa merge.

## Năm luồng dựng
| Luồng | Đường đi |
|---|---|
| Short FS (runner cũ) | `short_batch_runner.py:1221–1260` → `discover_segments` → `process_one_segment` (:666) → `_short_tts_render.py` + `render_short.py` → SEO/upload |
| Short BUD | cùng `short_batch_runner.py`; `--topic` chọn nguồn và registry |
| Short VSD (Studio) | `studio.py:481–499` → `build()` (:362) → `hf_batch_render`, `hf_align` → HyperFrames/FFmpeg |
| Long FS/BUD | builder → `plan_*.json` → `hf_batch_render.py:943–970` → `render_one` (:527) → `hyperframes_bridge.py` (:586–620) → `longform.js` khi lane=long |
| Long CL/MIM/CK | `creator_v2/motion/long/build_long.py`. Short CL/MIM/CK đi qua `creator_v2/scripts/run_pipeline.py:90–116` → `run_batch.py`. `hf_batch_render` không điều khiển luồng này. |

Short BUD/FS sản xuất thật hiện nay đi qua builder `grok/build_*.py`, rồi tới `hf_batch_render`. Không qua `short_batch_runner`.

## Trạng thái các nâng cấp (tại `fa6b738`)
| Nâng cấp | Trạng thái |
|---|---|
| Studio/devices | DÙNG (Short VSD) |
| Cổng short-v2 | CÓ NHƯNG TẮT. Hiệu lực 14/11 (`:410`), V3 hiệu lực 18/11 (`:468`) |
| Voice D / sound C | DÙNG có điều kiện (VSD, Long FS/BUD) |
| Final mix lock | DÙNG |
| `scene_picker` #70, `motion_picker` #71 | CHƯA NỐI (140b đang làm) |
| `prompt_builder` #60 | CHƯA NỐI (140c đang làm) |
| Components registry | CHƯA NỐI |
| `opening_library` | CHƯA NỐI |
| Packaging trong `library/channels/*.yaml` | CHƯA NỐI, không có code nào đọc |
| Hook lint | CHƯA NỐI (140d đang làm) |
| Long QA / cold-open #107 | UNKNOWN (140d sẽ nối `long_script_lint --strict`) |
| Creator V2 factory | chỉ dùng trong luồng creator_v2 |
| Trend FS/BUD #101 | có CLI riêng, chưa nối vào render |
| Data/rules #134/#135 | DÙNG có điều kiện trong creator_v2 |

## Đề xuất của audit
1. Nối scene picker vào bước tạo plan.
2. Nối motion picker sau scene picker.
3. Nối prompt builder ở bước tạo yêu cầu ảnh.
4. Nối `opening_library`, hoặc bỏ nó khỏi runtime.
5. Đưa hook lint vào trước TTS.
6. Nối Long QA/cold-open vào builder.
7. Quyết định components registry có phải là API của Studio không.
8. Packaging YAML: parse thật, hoặc ghi rõ chỉ là metadata.
9. Xác minh cổng short-v2 (sau 14/11) và V3 (sau 18/11) bằng log chạy thật.
10. Ghi provenance cho trend/data.

**Rủi ro:** đổi đầu vào có thể làm hình thay đổi dù script không đổi. Cần golden plan và so trước/sau.

---

# Ràng buộc schema `library/channels/<kênh>.yaml` (phía BUD/FS/VSD)

Phiên Learn AI đo trên main `ea4cda9`, ngày 05/11. Đây là các trường đang có code đọc. Schema mới phải giữ nguyên tên và kiểu của chúng; muốn đổi thì phải có migration và sửa code trong **cùng PR**.

## A. Định dạng và cách tra kênh
1. **Nội dung là JSON, dù đuôi file là `.yaml`.**
   - `hf_sound.py` chỉ đọc bằng `json.loads`.
   - `hyperframes_bridge` thử JSON trước, rồi mới thử YAML.
   - Muốn viết YAML thật thì phải sửa loader trong cùng PR.
2. **Tên file (stem) là id kênh.**
   - `lib.py:89` lấy stem và bỏ qua file có tên bắt đầu bằng `_`.
   - Bridge đọc `f"{ch}.yaml"`.
   - `hf_sound` thử stem trước, rồi dò trường `kenh`.
   - `vsd.yaml` có `kenh = "Văn Sử Địa"`, khác stem; `assets.py` nhận cả hai.
   - Đề xuất: `mim.yaml`, `ck.yaml`, `cl.yaml` có `kenh` trùng với stem.
3. **`_external.yaml` hiện là một list** (mim/ck/cl, kèm `kho_loc`). Khi tạo ba file kênh riêng thì chuyển `kho_loc` vào từng file, sửa `assets.py` trong cùng PR, rồi bỏ `_external.yaml`.

## B. Trường đang có code đọc
| Khoá | File đọc | Ghi chú |
|---|---|---|
| `kenh` | hf_sound, assets, lib, prompt_builder | |
| `ngach` | assets | |
| `khuon` (list dict) | `lib.lane_decision` / `enforce_lane` | Quyết định RETIRE/HOLD của PO; uploader chặn theo trường này. Giữ nguyên. |
| `bao_ve` (list) | lib | ADR 0018 mục 7 |
| `do_hop`, `do_hop_mac_dinh`, `thu_muc_thu_nghiem` | lib | chỉ có trong `_mau.yaml` |
| `assets {…}` | prompt_builder, assets | |
| `canh {forbidden_types, tags, window_k}` | scene_picker | BUD cấm cảnh tử vi ở đây |
| `typography {…}` | `bridge.load_channel_typography`, long_batch_runner | |
| `motion {hold_split_s, max_shots, min_shot_s, presets, window_k}` | bridge, motion_picker | |
| `sound {bgm_mac_dinh, cam, ducking_db, max_true_peak_dbtp, mood_mapping, music_gap_db, …, target_lufs}` | hf_sound (Sound Director C), bridge | |
| `tts {device, mode, voice}` | assets | chỉ có trong `vsd.yaml` |
| `kho_loc` | assets | hiện nằm trong `_external.yaml` |

## C. Có trong file nhưng chưa có code đọc
`giong` (chuỗi), `dinh_dang_dung`, `luat_cam`, `packaging`, `cta_hien_tai`, `nguon_brief`, `subtitle`.

Đây là dữ liệu PO viết tay: được đổi tên nhưng không được xoá.

## D. Gợi ý cho schema chung
- **Giọng:** giọng thật lấy từ `wire_plan_row` và `hf_voice`, không lấy từ yaml. Nếu cần giọng có cấu trúc thì thêm trường mới (ví dụ `voice_profile`). Không đổi nghĩa trường `giong`.
- **Luật nội dung:** đặt luật CK và luật MIM vào một khối luật chung, có phần cho cổng kiểm đọc, dùng chung cơ chế với `luat_cam`.
- **Test cần có:**
  - mọi file kênh parse được bằng `json.loads`;
  - các khoá ở mục B đúng kiểu;
  - tên trong `khuon` không trùng nhau.
