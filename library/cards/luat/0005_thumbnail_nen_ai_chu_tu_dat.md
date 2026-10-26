---
{
  "id": "0005_thumbnail_nen_ai_chu_tu_dat",
  "ten": "Thumbnail Long: nền AI không có chữ, chữ do ta tự đặt, có tên mỏ neo, duyệt ở cỡ 168 px",
  "loai": "luat",
  "dinh_dang": [],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [],
  "bang_chung_dung": [],
  "vi_du": [],
  "nguon_su_that": [
    "docs/adr/0005-thumbnail-nen-ai-chu-tu-dat.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (23/10/2026). Ngày 21/10 ta chốt thumbnail V2, mỗi bản 0–3 chữ, làm ba bản A/B/C. Ngày 23/10, bản đầu của Long Trạng Trình (\"SẤM CỦA AI?\") không cho người xem biết video nói về ai. Khi xem 12 video Trạng Trình top (0,86–2 triệu view) thì 11 video có tên nhân vật trên ảnh. CTR Long hiện là FS 6,8%, BUD 3,5%. BUD là điểm nghẽn. Ta thử ba cách cho Long Cao Biền: tự dựng thuần, nhờ ChatGPT vẽ cả ảnh lẫn chữ, và nhờ Flow vẽ. Cách được chọn là **ghép**: 1. ChatGPT vẽ nền không có chữ: mặt cận, kịch tính, chừa một mảng tối cho chữ. 2. Đặt chữ bằng `thumb_cb.py <nền> <ra> full q=175 \"t=DÒNG1|DÒNG2|CÂU HỎI\" pal=BUD|FS`: tên riêng viết hoa trên hai dòng, cộng một câu hỏi ≤ 3 c",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0005-thumbnail-nen-ai-chu-tu-dat.md:1`. Trạng thái: đã chấp nhận (23/10/2026). Ngày 21/10 ta chốt thumbnail V2, mỗi bản 0–3 chữ, làm ba bản A/B/C. Ngày 23/10, bản đầu của Long Trạng Trình ("SẤM CỦA AI?") không cho người xem biết video nói về ai. Khi xem 12 video Trạng Trình top (0,86–2 triệu view) thì 11 video có tên nhân vật trên ảnh. CTR Long hiện là FS 6,8%, BUD 3,5%. BUD là điểm nghẽn. Ta thử ba cách cho Long Cao Biền: tự dựng thuần, nhờ ChatGPT vẽ cả ảnh lẫn chữ, và nhờ Flow vẽ. Cách được chọn là **ghép**: 1.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
