---
{
  "id": "gauge_meter",
  "ten": "Đồng hồ đo / gauge",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "du_lieu",
    "chi_so"
  ],
  "cam_ngach": [],
  "so_muc": 26,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/LinearUncle/status/2103128559174971663",
    "https://x.com/itnavi2022/status/2104468704490909880"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Kim chỉ trên cung chia vạch, giá trị trung tâm đi cùng đơn vị và vùng ngưỡng. Mẫu [1](https://x.com/LinearUncle/status/2103128559174971663) minh họa đặt kim lên tỉ lệ có nguồn; mẫu [2](https://x.com/itnavi2022/status/2104468704490909880) cho thấy nhấn vùng đo đang được đề cập.

## Khi nào dùng

FS: Short minh họa tỉ lệ diện tích sáng trong phòng. Dạng Short. Không nên dùng khi trông như phép đo khách quan dù chỉ là minh họa.

## Cách dựng trong HyperFrames

Kỹ thuật gauge_meter chưa có trong engine như một visual riêng. Tạo cung/vạch SVG từ scale có miền xác định; góc kim là lerp của giá trị tại t. Mọi trạng thái của gauge_meter là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

trông như phép đo khách quan dù chỉ là minh họa; thiếu đơn vị làm sai nghĩa.
