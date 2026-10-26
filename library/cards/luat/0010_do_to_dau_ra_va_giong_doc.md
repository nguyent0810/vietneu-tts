---
{
  "id": "0010_do_to_dau_ra_va_giong_doc",
  "ten": "Độ to đầu ra đo hai lượt và qua limiter đỉnh thật; giọng đọc theo preset C; không tăng vang hay nhạc khi chưa hỏi",
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
    "docs/adr/0010-do-to-dau-ra-va-giong-doc.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (01/10 cho giọng, 24/10 cho độ to; PR #29). **Giọng.** Ngày 01/10 chủ kênh nghe ba mẫu. Mẫu A bị chê \"rẹt rẹt như robot\", đọc nhanh. Mẫu B vang và nhạc quá to. Preset C được chọn: - BUD: giọng Bình, tempo .91, câu đỉnh .85–.88, vang .045; lời trích kinh dùng giọng thứ hai (Quang Sơn); - FS: giọng Thái Sơn v3, tempo .96, không vang. **Độ to.** Ngày 23/10 đo đầu ra Short: FS −20,8 LUFS, BUD −17,9 LUFS, đỉnh có bài tới −0,4 dBTP. Nguyên nhân là `loudnorm` một lượt, đích −14. Giọng TTS có hệ số đỉnh khoảng 18 dB (tích hợp −24,6 LUFS nhưng đỉnh đã ở −6 dBTP). Kéo lên tới đích thì đỉnh vượt 0 dB, nên loudnorm tự rơi về chế độ động và dừng sớm. Quy trình mới trong `mux_audi",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---

## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0010-do-to-dau-ra-va-giong-doc.md:1`. Trạng thái: đã chấp nhận (01/10 cho giọng, 24/10 cho độ to; PR #29). **Giọng.** Ngày 01/10 chủ kênh nghe ba mẫu. Mẫu A bị chê "rẹt rẹt như robot", đọc nhanh. Mẫu B vang và nhạc quá to. Preset C được chọn: - BUD: giọng Bình, tempo .91, câu đỉnh .85–.88, vang .045; lời trích kinh dùng giọng thứ hai (Quang Sơn); - FS: giọng Thái Sơn v3, tempo .96, không vang. **Độ to.** Ngày 23/10 đo đầu ra Short: FS −20,8 LUFS, BUD −17,9 LUFS, đỉnh có bài tới −0,4 dBTP. Nguyên nhân là `loudnorm.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
