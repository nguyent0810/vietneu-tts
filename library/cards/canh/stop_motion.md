---
{
  "id": "stop_motion",
  "ten": "Stop motion",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "minh_hoa",
    "thu_cong"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 50,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/MustaphaFenzar/status/2102773737129156730",
    "https://x.com/_nikolajankovic/status/2102867033100616097"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 0,
    "bud": 0
  },
  "cong": "cao"
}
---

## Mô tả

Vật thể đổi pose theo chuỗi frame rời, tạo chuyển động từng nấc như chụp từng ảnh. Mẫu [1](https://x.com/MustaphaFenzar/status/2102773737129156730) minh họa xếp vật thể theo các pose rời; mẫu [2](https://x.com/_nikolajankovic/status/2102867033100616097) cho thấy dùng chuỗi ảnh tiền vẽ.

## Khi nào dùng

Không hợp FS/BUD trừ minh họa thủ công có ghi rõ. Dạng Short. Không nên dùng khi nhấp frame gây khó chịu.

## Cách dựng trong HyperFrames

Kỹ thuật stop_motion chưa có trong engine như một visual riêng. Dùng dãy frame render trước; chọn frame theo floor(t*fps), không chụp hoặc sinh frame trực tiếp. Mọi trạng thái của stop_motion là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

nhấp frame gây khó chịu; footage giả bị hiểu là tư liệu thật.
