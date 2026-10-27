---
{
  "id": "hierarchy_chart",
  "ten": "Sơ đồ phân cấp",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "phan_loai",
    "so_do"
  ],
  "cam_ngach": [],
  "so_muc": 16,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://prompt-motion.com/ultimaxbt-bbebf5",
    "https://prompt-motion.com/kantamk-61f410"
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

Nút xếp thành tầng từ gốc xuống nhánh con để biểu diễn cấp bậc hoặc phân loại. Mẫu [1](https://prompt-motion.com/ultimaxbt-bbebf5) minh họa xếp khu vực nhà theo tầng chính/phụ; mẫu [2](https://prompt-motion.com/kantamk-61f410) cho thấy nối cấp tổng thể với mục con.

## Khi nào dùng

FS: Long phân cấp khu vực trong sơ đồ nhà. Dạng Ca_hai. Không nên dùng khi cây quá sâu làm nhãn nhỏ.

## Cách dựng trong HyperFrames

Kỹ thuật hierarchy_chart chưa có trong engine như một visual riêng. Tính tọa độ node theo tầng và thứ tự khai báo; render cạnh/node SVG rồi reveal từng tầng. Mọi trạng thái của hierarchy_chart là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

cây quá sâu làm nhãn nhỏ; dễ bị hiểu là quan hệ nhân quả.
