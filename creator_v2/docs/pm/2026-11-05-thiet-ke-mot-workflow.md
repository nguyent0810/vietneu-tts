# #159: thiết kế một workflow dựng cho 6 kênh (nhận biết kênh, chọn theo hồ sơ)

**Trạng thái:** bản nháp 2, ngày 05/11/2026 (Lead MIM/CK). Đã sửa theo review của phiên vietneu (Lead BUD/FS): A1–A5, B1–B4, C1–C6, chép nguyên văn trong PR #164. **Chủ kênh duyệt ngày 05/11/2026: "Duyệt theo đề xuất"**, gồm cả 6 điểm ở mục 6 theo phương án đề xuất.

**Đầu vào:**
- kiểm kê B1: `docs/pm/tickets/GH-159-b1-report.md`;
- ràng buộc schema và builder Mac: `docs/pm/tickets/GH-159-mac-builders.md`;
- issue #159.

**Yêu cầu chủ kênh (05/11):** một workflow duy nhất. Phần riêng của từng kênh là dữ liệu. Pipeline nhận biết kênh, rồi chọn theme, cảnh, cổng kiểm, giọng, nhạc, luật theo kênh. Không còn hai luồng riêng.

## 1. Nguyên tắc
1. **Kênh là dữ liệu.** Mỗi kênh có một hồ sơ `library/channels/<id>.yaml`. Code không có `if kenh == "CK"`. Thêm kênh mới chỉ cần thêm một yaml, cộng file theme nếu kênh có giao diện mới.
2. **Code là danh mục có tên.** Engine, cổng kiểm, kho ảnh, uploader được đăng ký theo tên trong code. Hồ sơ chỉ chọn tên và tham số.
3. **Không có kênh mặc định.** Hiện `build_long.py:178` có `spec.get("channel", "CL")`, tức spec quên ghi kênh thì bị dựng thành CL. `resolve()` phải báo lỗi khi không biết kênh.
4. **Thêm vào, không thay.** Mỗi bước chuyển giữ nguyên đầu ra:
   - test so giá trị đọc từ hồ sơ với giá trị đang hard-code, phải giống hệt;
   - mỗi bước dựng thử rồi so tờ khung **và âm thanh** (cache TTS không đổi, LUFS) với bản chuẩn.
5. **Giữ hợp đồng BUD/FS/VSD** (`GH-159-mac-builders.md`):
   - file `.yaml` chứa JSON;
   - giữ nguyên tên và kiểu các khoá đang có code đọc: `kenh`, `ngach`, `khuon`, `bao_ve`, `assets`, `canh`, `typography`, `motion`, `sound`, `tts`, `kho_loc`;
   - không xoá dữ liệu PO viết tay (`luat_cam`, `packaging`, `giong`, …).
6. **Id kênh = stem = `kenh`.** Hồ sơ kênh phải có `kenh` trùng tên file.
   - Hiện có hai chỗ lệch: `_thu_lich_su.yaml` (`kenh = "lich_su"`) và `vsd.yaml` (`kenh = "Văn Sử Địa"`). PR 1 sửa cả hai (mục 5).
   - Sau đó, file có tên bắt đầu bằng `_` chỉ còn là mẫu hoặc dữ liệu phụ (`_mau.yaml`), không phải kênh.
7. **`make_video` không upload.** Upload luôn là bước riêng của Lead, có lệnh chủ kênh.

## 2. Nhận biết kênh
Hàm duy nhất `library/tools/channel_profile.py: resolve(item) -> id`, tra theo thứ tự:
1. Trường `channel` (luồng creator_v2) hoặc `kenh` (plan BUD/FS) trong spec hoặc plan row. So với stem, hoặc với `ten_hien_thi` và `alias` của hồ sơ. Có `alias` thì plan cũ ghi `kenh = "Văn Sử Địa"` vẫn nhận được.
2. Cờ `--channel` trên dòng lệnh.
3. Tiền tố slug (`slug_prefix` trong hồ sơ), chỉ khi **duy nhất** một kênh khớp. Ví dụ `long-` đang thuộc cả MIM lẫn CK, nên không dùng để suy ra kênh.
4. Không khớp, hoặc khớp nhiều hơn một kênh: báo lỗi.

Có id rồi thì `load(id)` trả hồ sơ đã kiểm schema.

## 3. Hồ sơ kênh: khối mới
Khoá hiện có giữ nguyên. Thêm các khối dưới đây. Mỗi thông tin chỉ có **một nguồn sự thật** (A3).

```jsonc
{
  "kenh": "ck",                          // = stem
  "ten_hien_thi": "Biểu Đồ Biết Nói",
  "alias": [],                           // vd vsd: ["Văn Sử Địa"]
  "slug_prefix": ["ck-"],

  "dung": {                              // MỚI: chọn engine dựng
    "long":  {"engine": "casewide", "plugin": ["lab", "chart"], "craft": false},
    "short": {"engine": "casefile", "plugin": []}
    // BUD/FS (B1): long.engine = "hf_batch" (lane long → longform.js), short.engine = "hf_batch" (lane short)
    // VSD:         short.engine = "studio" (studio.py + thiết bị)
  },

  "canh": {"allowed_types": null, "forbidden_types": []},   // khối đã có; thêm allowed_types

  "theme": {                             // MỚI: chỉ chọn TÊN theme/look, không lặp màu/font
    "long": "chart", "short": "ck", "look_pool": "mim", "brand": "BIỂU ĐỒ BIẾT NÓI"
    // Màu, font: nằm ở typography (bridge.load_channel_typography đã đọc). Kênh creator_v2 chuyển accent sang typography.mau_nhan.
  },

  "voice_profile": {                     // MỚI (A4). Không đổi nghĩa "giong" (chuỗi mô tả)
    "engine": "creator_v2",              // BUD/FS: "giong_d" + {donor, temperature, text_mode} (hf_voice, wire_plan_row)
    "tham_so": {"dan": "Ngọc Huyền", "trich": "Xuân Vĩnh", "hoi": "Phạm Tuyên", "fx": null, "takes": 3}
  },

  "sound": {"...": "khối đã có"},

  "anh": {                               // MỚI: chỉ luật ảnh AI + nguồn. License nằm ở kho_loc
    "ai": {"cho_phep": true, "nhan_tren_khung": false, "nhac_trong_mo_ta": false, "credit": false},
    "nguon": ["commons", "openverse", "pexels", "kho_tai_san"]
  },
  "kho_loc": {"license_cho_phep": ["PD", "CC0", "CC BY"], "tag_cam": ["..."]},   // nguồn duy nhất cho license; chuyển từ _external.yaml

  "luat_noi_dung": {                     // MỚI: khối MÁY ĐỌC cho cổng kiểm.
                                         // luat_cam (PO viết tay) giữ nguyên; nội dung chỉ chuyển sang khi PO duyệt
    "cam_tu": ["<regex tên ngân hàng/công ty CK/hãng xe>", "\\bnên (mua|bán)\\b"],
    "cam_ma_co_phieu": true,
    "nhan_bat_buoc": {"so_tu_dung": "VÍ DỤ GIẢ ĐỊNH"},
    "mo_ta_bat_buoc": ["Nội dung giáo dục, không phải tư vấn đầu tư."],
    "mo_ta_cam": ["<", ">", "CẦN", "agent", "factcheck", "data/long"],
    "title_max": 60
  },

  "khuon": [{"ten": "...", "id": "...", "trang_thai": "active", "quyet_dinh": null}],
                                         // A5: MIM/CK/CL cũng có khuon; lib.enforce_lane chặn retire/hold

  "cong": {                              // MỚI: cổng theo tên, khớp production_gates.py (#163)
    "long":  [{"ten": "floor", "ho_so": "mim_ck"}, {"ten": "variety"}, {"ten": "lint_html"},
              {"ten": "factcheck"}, {"ten": "approved"}],
    "short": [{"ten": "preflight"}, {"ten": "script_lint"}, {"ten": "mix", "max_chu_tron": 0.35}]
  },

  "upload": {"duong": "factory", "pacing": [1, 90],
             "slot_short": ["07:00", "12:00", "17:30", "19:00", "22:00"]}
             // BUD/FS: "bud_fs_uploader" (upload_bud/upload_fs/upload_long: occupied_slots, ROLLING_GUARD, enforce_lane, packaging)
}
```

**Tên cổng BUD/FS** (B4, theo `library/tools/production_gates.py` ở #163):

| Loại | Cổng |
|---|---|
| Short | `hook_lint` (chặn), `short_tone`, `zodiac_naming` (FS), `integrity`, `reveal`, `novelty`, `short_v2` (theo ngày: 14/11, 18/11), `lane` (chặn ở uploader) |
| Long | `long_script_lint` (strict: ERROR thì chặn), `retention` (chỉ cảnh báo), `hf_qa` (overflow, contrast, strict) |
| Mọi kênh | `secret_scan` (khi commit), `credit_onscreen` (cấm credit hoặc chữ AI trên hình; luật PO 04/11 cho BUD/FS, #147 cho MIM/CK) |

**Không đưa vào hồ sơ:**
- Tên file credentials và đường dẫn bí mật. Repo PUBLIC; phần này giữ ở `factory/channels.py` hoặc biến môi trường.
- Quyết định lịch của PO. Hồ sơ chỉ chứa lưới slot làm mặc định.

## 4. Cách pipeline chọn theo hồ sơ
Builder là **bước biên tập** (kịch bản, ảnh, plan hoặc spec) và chạy riêng. `make_video.py` bắt đầu từ spec hoặc plan đã có (B2).

```
make_video.py <long|short> <spec | plan --only id> [--channel X]
  → resolve(item) → load(id)
  → dung[kind].engine → renderer đã đăng ký:
       casewide → motion/long/build_long.py
       casefile → motion/stier/build.py
       hf_batch → hf_batch_render.py <thư mục plan> --only <id>   (lane long/short)
       studio   → studio.py
  → renderer nhận hồ sơ (theme, voice_profile, plugin, anh, sound, typography) thay cho bảng hard-code
  → chạy lần lượt cong[kind]; cổng đọc luật từ luat_noi_dung, anh, kho_loc
  → DỪNG. Upload là bước riêng của Lead: upload.duong → factory | bud_fs_uploader
```
Trước B3, `make_video.py` chỉ là cửa chung gọi các renderer đang chạy tốt. Chủ kênh có ngay "một workflow" mà hình của video nào cũng không đổi.

## 5. Lộ trình
Mỗi bước một PR nhỏ.
- PR đụng `library/`, `hf_*`, `hyperframes_short/`: phiên vietneu review.
- PR đụng `creator_v2/`: phiên MimCk review.
- PR 1 tách nhánh **sau khi #160–#163 merge** (C2), vì các PR đó cũng đụng `hf_batch_render.py` và `library/tools`.

| # | PR | Đổi gì | Kiểm |
|---|---|---|---|
| 1 | `channel_profile.py` (`resolve`, `load`, schema) và `mim.yaml`, `ck.yaml`, `cl.yaml` | (A1) đổi `_thu_lich_su.yaml` thành `lich_su.yaml` và sửa mọi chỗ đọc. (A2) `vsd.yaml`: `kenh = "vsd"`, thêm `ten_hien_thi` và `alias`. Chuyển `kho_loc` vào từng file; `assets.py` đọc từ đó; bỏ `_external.yaml`. (A5) `khuon` của MIM/CK/CL có đủ trường lib đọc | `json.loads` mọi file; đúng kiểu các khoá đang có code đọc; tên `khuon` không trùng; `tests/test_library_cards.py`; `test_sound_director` (hf_sound chỉ nhận dict); slug mơ hồ thì báo lỗi |
| 2 | `build_long.py`, `themes.py`, `floor.py` (creator_v2) đọc theme, giọng, ngưỡng từ hồ sơ | Bỏ default "CL". Giá trị **giống hệt** | So hồ sơ với bảng cũ; dựng lại một chương golden, khung và âm thanh trùng |
| 2b | Giọng BUD/FS vào `voice_profile` (A4) | PR riêng | Cache TTS khoá theo voice/style/temperature, không bị đọc lại (#153) |
| 3 | `make_video.py` (cửa chung) | Gọi bốn renderer theo `dung` | Mỗi kênh dựng thử một Short hoặc chương. BUD/FS dùng plan của một Short đã hẹn để so (không đăng lại). So khung, LUFS, cache TTS (C3) |
| 4 | Cổng theo tên (`cong`) và `luat_noi_dung` | Gom luật đang nằm trong AGENTS.md hoặc code thành cổng đọc hồ sơ | Test từng cổng; không hạ ngưỡng |
| 5 | Kho ảnh chung cho MIM/CK/CL (`assets.py`) | Bài mới tra kho trước | Một bài MIM thử |
| 6 | Dọn trùng: một `webauto`; một `hf_align`; creator_v2 dùng `hf_geo.py` ở gốc (lớp Hoàng Sa/Trường Sa đã có từ #149, C4) | | Test có sẵn |
| B3 | Gộp engine theo nhóm cảnh | Từng nhóm, so với bản chuẩn | Tờ khung trước/sau |
| B4 | Tài liệu skill; đánh dấu deprecated đường cũ | Không xoá khi chưa có chủ kênh duyệt | |

Sau PR 3, MIM/CK/CL có thể dựng lại qua cửa chung nếu chủ kênh mở lại.

## 6. Điểm cần chủ kênh quyết
1. Duyệt schema (mục 3) và lộ trình (mục 5).
2. Duyệt luật ảnh MIM/CK/CL (`kho_loc`, `anh`):
   - MIM: ảnh bên thứ ba chỉ PD/CC0/CC BY; ảnh AI được dùng nhưng không in nhãn, không nhắc trong mô tả;
   - CK: cấm logo, tên ngân hàng, mã cổ phiếu;
   - CL: cấm ảnh AI. Đã đối chiếu: 9 Long CL có 0 cảnh ảnh AI, khớp luật "Không ảnh AI" trong `creator_v2/CLAUDE.md` (C5).
3. Lớp Hoàng Sa/Trường Sa: cả hai phiên đề xuất **áp cho mọi bản đồ có Biển Đông của mọi kênh** (C6).
4. Mở lại dựng MIM/CK/CL sau PR 3 (đề xuất), hay chờ hết B3.
5. Đổi tên `_thu_lich_su.yaml` thành `lich_su.yaml` và `kenh` của VSD thành `"vsd"` (PR 1). Hồ sơ BUD/FS là dữ liệu PO, nên cần duyệt.
6. Giữ hai đường upload riêng qua `upload.duong` (đề xuất), không gộp trong #159.
