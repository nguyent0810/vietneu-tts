---
{
  "id": "split_screen_multi",
  "ten": "Nhiều khung đồng thời",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "so_sanh",
    "anh_tu_lieu"
  ],
  "cam_ngach": [],
  "so_muc": 25,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/daniel_mac8/status/2103824976713306214",
    "https://x.com/Xterbase/status/2108161031243759993"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
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

Hai hay nhiều khung cùng thời điểm căn theo một lưới để đối chiếu nguồn/hành động. Mẫu [1](https://x.com/daniel_mac8/status/2103824976713306214) minh họa đặt hai bố cục cửa cạnh nhau; mẫu [2](https://x.com/Xterbase/status/2108161031243759993) cho thấy so sánh hai ảnh cùng loại.

## Khi nào dùng

FS: Short so sánh hai cách đặt cửa. Dạng Short. Không nên dùng khi trên hai khung chữ/chi tiết quá nhỏ.

## Cách dựng trong HyperFrames

Kỹ thuật split_screen_multi chưa có trong engine như một visual riêng. Chuẩn hóa crop các khung vào grid CSS tĩnh; mọi panel dùng cùng timeline và điểm cắt đã khóa. Mọi trạng thái của split_screen_multi là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

trên hai khung chữ/chi tiết quá nhỏ; thời điểm khác nhau gây so sánh sai.
