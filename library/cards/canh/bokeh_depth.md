---
{
  "id": "bokeh_depth",
  "ten": "Bokeh / độ sâu trường ảnh",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "anh_tu_lieu",
    "khong_khi"
  ],
  "cam_ngach": [],
  "so_muc": 32,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/joaoli13/status/2102805376466891137",
    "https://x.com/gmgmgm1545/status/2103793820815245507"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 1
  },
  "cong": "vua"
}
---

## Mô tả

Chủ thể giữ nét, nền tách thành đốm tròn mờ; lớp xa mờ hơn và ít tương phản hơn. Mẫu [1](https://x.com/joaoli13/status/2102805376466891137) minh họa làm mờ nền phía sau đồ vật chính; mẫu [2](https://x.com/gmgmgm1545/status/2103793820815245507) cho thấy tách chủ thể khỏi gian phòng trong ảnh.

## Khi nào dùng

FS: Short giới thiệu một chi tiết trong ảnh tư liệu. Dạng Ca_hai. Không nên dùng khi bokeh tổng hợp giống bụi.

## Cách dựng trong HyperFrames

Kỹ thuật bokeh_depth chưa có trong engine như một visual riêng. Bake nền và đốm bokeh thành asset cục bộ; animate opacity/scale của vài lớp, tránh blur toàn khung. Mọi trạng thái của bokeh_depth là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

bokeh tổng hợp giống bụi; blur lớn nặng GPU và làm nhòe chữ.
