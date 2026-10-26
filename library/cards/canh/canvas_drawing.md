---
{
  "id": "canvas_drawing",
  "ten": "Vẽ bằng Canvas",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "so_do",
    "giai_thich"
  ],
  "cam_ngach": [],
  "so_muc": 269,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/alexalbert__/status/2102466523164274839",
    "https://x.com/majidmanzarpour/status/2102476258948927543"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 1
  },
  "cong": "vua"
}
---

## Mô tả

Nét đường được lộ tuần tự như đang vẽ; thứ tự stroke định hướng cách đọc sơ đồ. Mẫu [1](https://x.com/alexalbert__/status/2102466523164274839) minh họa vẽ đường phân cung trên sơ đồ; mẫu [2](https://x.com/majidmanzarpour/status/2102476258948927543) cho thấy lộ đường viền trước khi tô vùng.

## Khi nào dùng

FS: Short vẽ đường đi trên bản vẽ mặt bằng. Dạng Ca_hai. Không nên dùng khi nét phụ thuộc frame trước sẽ sai khi seek.

## Cách dựng trong HyperFrames

Kỹ thuật canvas_drawing chưa có trong engine như một visual riêng. Lưu path/điểm trước; tính dashoffset theo progress t hoặc vẽ lại canvas từ đầu ở từng frame. Mọi trạng thái của canvas_drawing là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

nét phụ thuộc frame trước sẽ sai khi seek; nét nguệch ngoạc gây cảm giác cẩu thả.
