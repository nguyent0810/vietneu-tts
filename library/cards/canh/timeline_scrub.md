---
{
  "id": "timeline_scrub",
  "ten": "Scrub qua thời gian",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "thoi_gian",
    "moc"
  ],
  "cam_ngach": [],
  "so_muc": 19,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/maker_evan/status/2108520350908916007",
    "https://prompt-motion.com/ultimaxbt-bbebf5"
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

Thanh thời gian và marker tiến qua mốc; panel hoặc nhãn đổi tại các khoảng đã xác định. Mẫu [1](https://x.com/maker_evan/status/2108520350908916007) minh họa đánh dấu giờ nắng thay đổi trên phòng; mẫu [2](https://prompt-motion.com/ultimaxbt-bbebf5) cho thấy hiện lần lượt các mốc thời gian.

## Khi nào dùng

FS: Long trình bày các mốc đo sáng đã có nguồn. Dạng Ca_hai. Không nên dùng khi scrub giả như tương tác thật.

## Cách dựng trong HyperFrames

Kỹ thuật timeline_scrub chưa có trong engine như một visual riêng. Lưu ticks và trạng thái mốc; marker = clamp(t/duration), panel chọn khoảng qua lookup tĩnh. Mọi trạng thái của timeline_scrub là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

scrub giả như tương tác thật; mốc không xác nhận làm sai thứ tự.
