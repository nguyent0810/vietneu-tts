# #159: thiết kế một workflow dựng cho 6 kênh (nhận biết kênh rồi chọn theo hồ sơ)

**Trạng thái:** bản nháp ngày 05/11/2026 (Lead MIM/CK). Chờ phiên vietneu (Lead BUD/FS) review, rồi chờ chủ kênh duyệt.

**Đầu vào:**
- kiểm kê B1: `docs/pm/tickets/GH-159-b1-report.md`;
- ràng buộc schema và builder trên Mac: `docs/pm/tickets/GH-159-mac-builders.md`;
- issue #159.

**Yêu cầu của chủ kênh (05/11):** một workflow duy nhất. Phần riêng của từng kênh là dữ liệu. Pipeline nhận biết kênh, rồi chọn theme, cảnh, cổng kiểm, giọng, nhạc và luật theo kênh. Không giữ hai luồng riêng.

## 1. Nguyên tắc
1. **Kênh là dữ liệu.** Mỗi kênh có một file `library/channels/<id>.yaml`. Code không có `if kenh == "CK"`. Thêm kênh mới chỉ cần thêm một file yaml, cộng file theme nếu kênh có giao diện mới.
2. **Code là danh mục có tên.** Engine, plugin cảnh, cổng kiểm, kho ảnh và uploader được đăng ký theo tên trong code (registry). Hồ sơ kênh chỉ chọn tên trong danh mục đó, kèm tham số.
3. **Không có kênh mặc định.** Hiện `build_long.py:178` dùng `spec.get("channel", "CL")`, nên spec quên ghi kênh sẽ bị dựng thành CL. Hàm nhận biết kênh mới phải **báo lỗi** khi không xác định được kênh.
4. **Thêm vào, không thay.** Mỗi bước chuyển giữ nguyên đầu ra. Có test so giá trị lấy từ hồ sơ với giá trị đang hard-code (giống hệt mới đạt). Mỗi bước dựng thử một chương hoặc một Short và so tờ khung với bản chuẩn.
5. **Giữ hợp đồng phía BUD/FS** (mục ràng buộc trong `GH-159-mac-builders.md`):
   - file `.yaml` chứa JSON;
   - id kênh là stem của tên file, file có tên bắt đầu bằng `_` không phải kênh;
   - giữ nguyên tên và kiểu các khoá đang có code đọc: `kenh`, `ngach`, `khuon`, `bao_ve`, `assets`, `canh`, `typography`, `motion`, `sound`, `tts`, `kho_loc`;
   - không xoá dữ liệu PO viết tay.

## 2. Nhận biết kênh
Một hàm duy nhất `library/tools/channel_profile.py: resolve(item) -> id`. Thứ tự tra:
1. Trường `channel` (luồng B) hoặc `kenh` (luồng A) trong spec hay plan row. Dùng nếu khớp một stem.
2. Cờ `--channel` trên dòng lệnh.
3. Tiền tố slug, khai trong hồ sơ ở trường `slug_prefix`. Tiền tố chỉ được dùng khi **duy nhất** một kênh khớp. Ví dụ `long-` đang thuộc cả MIM lẫn CK (`factory/channels.py`), nên `long-` không được tự suy ra kênh.
4. Không có kết quả, hoặc có nhiều kết quả: **báo lỗi**, không đoán.

Lấy được id rồi thì `load(id)` trả về hồ sơ đã kiểm schema. Từ đây mọi bước chỉ đọc hồ sơ.

## 3. Hồ sơ kênh: khoá mới thêm vào
Các khoá hiện có của BUD/FS/VSD giữ nguyên. Thêm các khối mới dưới đây. Kênh nào chưa dùng khối nào thì bỏ trống khối đó.

```jsonc
{
  "kenh": "ck",                       // trùng stem
  "ten_hien_thi": "Biểu Đồ Biết Nói",
  "slug_prefix": ["ck-"],             // chỉ những tiền tố duy nhất của kênh này

  "dung": {                           // MỚI: chọn engine và plugin
    "long":  {"engine": "casewide", "plugin": ["lab", "chart"], "craft": false},
    "short": {"engine": "casefile", "plugin": [], "thiet_bi": []}
    // BUD: long.engine "longform", short.engine "studio" | "casefile", short.thiet_bi ["hfs"]
  },

  "canh": {                           // khối đã có (scene_picker); thêm allowed_types
    "allowed_types": null,            // null = mọi loại engine có
    "forbidden_types": []
  },

  "theme": {                          // MỚI: hiện nằm trong build_long.py:110-116, themes.py, variety.py
    "long": "chart", "short": "ck", "brand": "BIỂU ĐỒ BIẾT NÓI", "accent": "#fbbf24",
    "look_pool": "mim"
  },

  "voice_profile": {                  // MỚI. Không đổi nghĩa trường "giong" (chuỗi mô tả)
    "dan": "Ngọc Huyền", "trich": "Xuân Vĩnh", "hoi": "Phạm Tuyên", "fx": null,
    "takes": 3
  },

  "sound": { "...": "khối đã có (Sound Director C); thêm sfx_palette" },

  "anh": {                            // MỚI: gộp luật ảnh hiện rải trong code
    "license_cho_phep": ["PD", "CC0", "CC BY"], "cam_sa": true,
    "ai": {"cho_phep": true, "nhan_tren_khung": false, "nhac_trong_mo_ta": false, "credit": false},
    "nguon": ["commons", "openverse", "pexels", "kho_tai_san"]
  },
  "kho_loc": { "...": "chuyển từ _external.yaml vào đây" },

  "luat_noi_dung": {                  // MỚI. Cổng kiểm đọc khối này; BUD/FS dùng chung cơ chế với luat_cam
    "cam_tu": ["<regex tên ngân hàng/công ty CK/hãng xe>", "\\bnên (mua|bán)\\b"],
    "cam_ma_co_phieu": true,
    "nhan_bat_buoc": {"so_tu_dung": "VÍ DỤ GIẢ ĐỊNH"},
    "mo_ta_bat_buoc": ["Nội dung giáo dục, không phải tư vấn đầu tư."],
    "mo_ta_cam": ["<", ">", "CẦN", "agent", "factcheck", "data/long"],
    "title_max": 60
  },

  "cong": {                           // MỚI: cổng kiểm theo tên và tham số. Code giữ danh mục cổng
    "long":  [{"ten": "floor", "ho_so": "mim_ck"}, {"ten": "variety"}, {"ten": "lint_html"},
              {"ten": "factcheck"}, {"ten": "approved"}, {"ten": "hf_qa", "che_do": "canh_bao"}],
    "short": [{"ten": "preflight"}, {"ten": "script_lint"}, {"ten": "mix", "max_chu_tron": 0.35}]
  },

  "upload": {                         // MỚI: chỉ khai báo. Chưa chuyển code ở B2
    "duong": "factory", "pacing": [1, 90],
    "slot_short": ["07:00", "12:00", "17:30", "19:00", "22:00"]
  }
}
```

**Không đưa vào hồ sơ:**
- Tên file credentials và mọi đường dẫn bí mật. Repo PUBLIC; phần này giữ trong `factory/channels.py` hoặc biến môi trường như hiện nay.
- Quyết định PO về lịch (giờ, số video/ngày). Hồ sơ chỉ chứa lưới slot làm mặc định.

## 4. Cách pipeline chọn theo hồ sơ
```
make_video.py <long|short> <spec|plan> [--channel X]
  → resolve(item) → load(id)
  → dung[kind].engine → builder đã đăng ký:
       casewide → motion/long/build_long.py
       casefile → motion/stier/build.py
       longform → hf_batch_render.py
       studio   → studio.py
  → builder nhận hồ sơ (theme, voice_profile, plugin, anh, sound) thay cho bảng hard-code
  → chạy lần lượt các cổng trong cong[kind]; cổng nào đọc luật thì đọc từ luat_noi_dung, anh, kho_loc
  → upload: duong → factory | youtube_upload. Vẫn chỉ Lead chạy, có lệnh chủ kênh
```
Đến B3 mới gộp engine. Trước đó, `make_video.py` chỉ là cửa chung: nhận biết kênh rồi gọi builder đang chạy tốt. Nhờ vậy chủ kênh có ngay "một workflow" mà không đổi hình của video nào.

## 5. Lộ trình (sửa thứ tự B2 trong báo cáo B1)
Mỗi bước là một PR nhỏ. PR đụng `library/`, `hf_*`, `hyperframes_short/` thì phiên vietneu review. PR đụng `creator_v2/` thì phiên MimCk review.

| # | PR | Đổi gì | Kiểm |
|---|---|---|---|
| 1 | `channel_profile.py` (`resolve`, `load`, schema) + `mim.yaml`, `ck.yaml`, `cl.yaml` | Chỉ thêm file. Chuyển `kho_loc` vào từng file, `assets.py` đọc file mới, bỏ `_external.yaml` | `json.loads` mọi file; đúng kiểu các khoá đang có code đọc; slug mơ hồ thì báo lỗi |
| 2 | `build_long.py`, `themes.py`, `floor.py` đọc theme, giọng, ngưỡng từ hồ sơ | Bỏ default "CL". Giá trị **giống hệt** | Test so hồ sơ với bảng cũ; dựng lại một chương golden, khung trùng |
| 3 | `make_video.py` (cửa chung) | Gọi bốn builder hiện có theo `dung` | Mỗi kênh dựng một Short hoặc chương thử; so tờ khung |
| 4 | Cổng kiểm theo tên (`cong`) + `luat_noi_dung` | Gộp các luật đang nằm trong AGENTS.md hoặc code thành cổng đọc hồ sơ; BUD/FS bật dần | Test từng cổng; không hạ ngưỡng |
| 5 | Kho ảnh chung cho MIM/CK/CL (`assets.py`) | Bài mới tra kho trước | Một bài MIM thử |
| 6 | `webauto` một bản; `hf_align` một file; lớp Hoàng Sa vào `hf_geo` chung | Dọn trùng | Test có sẵn |
| B3 | Gộp engine theo nhóm cảnh | Từng nhóm, so với bản chuẩn | Tờ khung trước/sau |
| B4 | Tài liệu skill; đánh dấu deprecated các đường cũ | Không xoá khi chưa có chủ kênh duyệt | |

Sau PR 3, MIM/CK/CL có thể dựng lại qua cửa chung, nếu chủ kênh cho mở lại.

## 6. Điểm cần chủ kênh quyết
1. Duyệt schema (mục 3) và lộ trình (mục 5).
2. Duyệt luật `kho_loc` và `anh` của MIM/CK/CL:
   - MIM: ảnh bên thứ ba chỉ PD/CC0/CC BY; ảnh AI được dùng nhưng không in nhãn, không nhắc trong mô tả;
   - CK: cấm logo, tên ngân hàng, mã cổ phiếu;
   - CL: cấm ảnh AI. (Luật này do phiên vietneu ghi. Cần xác nhận, vì Long CL golden không dùng ảnh AI.)
3. Lớp Hoàng Sa/Trường Sa: áp cho mọi bản đồ có Biển Đông của mọi kênh (đề xuất), hay chỉ BUD/FS.
4. Mở lại dựng MIM/CK/CL ngay sau PR 3 (đề xuất), hay chờ tới hết B3.
5. Hai đường upload (`factory` và `youtube_upload`): giữ riêng qua trường `upload.duong` (đề xuất), không gộp trong #159.
