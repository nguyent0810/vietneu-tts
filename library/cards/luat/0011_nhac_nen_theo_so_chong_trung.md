---
{
  "id": "0011_nhac_nen_theo_so_chong_trung",
  "ten": "Nhạc nền chọn theo sổ chống trùng, cho cả Long lẫn Short",
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
    "docs/adr/0011-nhac-nen-theo-so-chong-trung.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (04/10/2026). Trước 04/10, nhạc nền gần như không đổi giữa các video: - mọi Long BUD dùng đúng 3 bản *Meditation Impromptu*; - 240 short BUD dùng chung một bài; - 113 short FS đều dùng *Asian Drums*. Chính sách Spam của YouTube nêu đích danh việc dùng \"cùng nhạc nền\" trên nhiều video. Với một kênh đăng 5 short mỗi ngày, đây là rủi ro bị xếp vào nội dung lặp. **Long.** `hf_music.pool_for` chọn một lần 4 bài, là những bài ít dùng nhất trong 3 video cùng kênh gần ngày đăng nhất (tính cả hai chiều thời gian). Kết quả ghi vào `bgm_ledger.json`. Nhạc chỉ đổi bài ở thẻ chương, chồng mờ 3 giây, san đều độ to. Bài thật sự đã phát được ghi vào `render.json` (`bgm_used`), để up",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---

## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0011-nhac-nen-theo-so-chong-trung.md:1`. Trạng thái: đã chấp nhận (04/10/2026). Trước 04/10, nhạc nền gần như không đổi giữa các video: - mọi Long BUD dùng đúng 3 bản *Meditation Impromptu*; - 240 short BUD dùng chung một bài; - 113 short FS đều dùng *Asian Drums*. Chính sách Spam của YouTube nêu đích danh việc dùng "cùng nhạc nền" trên nhiều video. Với một kênh đăng 5 short mỗi ngày, đây là rủi ro bị xếp vào nội dung lặp. **Long.** `hf_music.pool_for` chọn một lần 4 bài, là những bài ít dùng nhất trong 3 video cùng.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
